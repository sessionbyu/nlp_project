"""
认证 API 路由

功能：
1. 用户注册
2. 用户登录
3. 获取当前用户信息
4. 刷新 Token
5. 修改密码
"""
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...db.session import get_async_session
from ...db.models import User, APIKey
from ...services.auth import (
    get_current_user,
    get_current_user_required,
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from ...services.blacklist import token_blacklist

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ========== Pydantic Schemas ==========

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")

    @validator("username")
    def validate_username(cls, v: str) -> str:
        if not v.isalnum() and "_" not in v:
            raise ValueError("Username must be alphanumeric or contain underscore")
        return v


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住我")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: dict


class UserInfoResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str]
    avatar: Optional[str]
    role: str
    is_active: bool


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None


class APIKeyResponse(BaseModel):
    """API Key 响应"""
    id: int
    name: str
    key_prefix: str
    permissions: str
    is_active: bool
    expires_at: Optional[str] = None
    last_used_at: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class APIKeyCreateRequest(BaseModel):
    """创建 API Key 请求"""
    name: str = Field(..., min_length=1, max_length=100, description="密钥名称")
    permissions: str = Field("predict,history", description="权限列表（逗号分隔）")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="有效期（天），null表示永不过期")


class APIKeyCreateResponse(BaseModel):
    """创建 API Key 响应（包含完整密钥）"""
    id: int
    name: str
    api_key: str  # 完整密钥，仅显示一次
    key_prefix: str
    permissions: str
    is_active: bool
    expires_at: Optional[str] = None
    created_at: str
    message: str


# ========== API Endpoints ==========

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """用户注册"""
    # 检查用户名是否已存在
    result = await session.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    # 检查邮箱是否已存在
    result = await session.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 创建用户
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        nickname=data.nickname or data.username,
        role="user",
        is_active=True,
        is_verified=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {"msg": "User registered successfully", "user_id": user.id}


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """用户登录"""
    # 查找用户（支持用户名或邮箱登录）
    result = await session.execute(
        select(User).where(
            (User.username == data.username) | (User.email == data.username),
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # 更新最后登录时间
    from datetime import datetime
    user.last_login = datetime.utcnow()
    await session.commit()

    # 生成 Token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    refresh_token = None
    if data.remember_me:
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "role": user.role,
        },
    )


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_required),
):
    """获取当前用户信息"""
    return UserInfoResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        nickname=current_user.nickname,
        avatar=current_user.avatar,
        role=current_user.role,
        is_active=current_user.is_active,
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str = Body(..., description="Refresh token"),
    session: AsyncSession = Depends(get_async_session),
):
    """刷新访问令牌"""
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else "your-secret-key-change-in-production", algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        result = await session.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if not user or user.is_deleted or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

        return {"access_token": access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_async_session),
):
    """修改密码"""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    current_user.hashed_password = get_password_hash(data.new_password)
    await session.commit()

    return {"msg": "Password changed successfully"}


@router.put("/profile", response_model=UserInfoResponse)
async def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_async_session),
):
    """更新用户信息"""
    if data.nickname is not None:
        current_user.nickname = data.nickname
    if data.email is not None:
        # 检查邮箱是否被其他用户使用
        result = await session.execute(
            select(User).where(User.email == data.email, User.id != current_user.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = data.email
    if data.avatar is not None:
        current_user.avatar = data.avatar

    await session.commit()
    await session.refresh(current_user)

    return UserInfoResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        nickname=current_user.nickname,
        avatar=current_user.avatar,
        role=current_user.role,
        is_active=current_user.is_active,
    )


@router.post("/logout")
async def logout(request: Request):
    """用户登出（将 Token 加入黑名单）"""
    # 从请求头中获取 Token
    authorization: str = request.headers.get("Authorization", "")
    token = None

    if authorization.startswith("Bearer "):
        token = authorization[7:]

    # 将 Token 加入黑名单（异步，不阻塞响应）
    if token:
        try:
            await token_blacklist.add_to_blacklist(token)
        except Exception as e:
            print(f"Failed to add token to blacklist during logout: {e}")

    return {"msg": "Logged out successfully"}


# ========== API Keys 管理 ==========

import secrets
from datetime import datetime, timezone

@router.get("/api-keys", response_model=list[APIKeyResponse])
async def get_api_keys(
    current_user: User = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_async_session),
):
    """获取用户的所有 API Keys"""
    result = await session.execute(
        select(APIKey)
        .where(APIKey.user_id == current_user.id)
        .order_by(APIKey.created_at.desc())
    )
    api_keys = result.scalars().all()

    return [
        APIKeyResponse(
            id=key.id,
            name=key.name,
            key_prefix=key.key_prefix,
            permissions=key.permissions,
            is_active=key.is_active,
            expires_at=key.expires_at.isoformat() if key.expires_at else None,
            last_used_at=key.last_used.isoformat() if key.last_used else None,
            created_at=key.created_at.isoformat(),
        )
        for key in api_keys
    ]


@router.post("/api-keys", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    data: APIKeyCreateRequest,
    current_user: User = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_async_session),
):
    """创建新的 API Key"""
    # 生成完整的 API Key
    full_key = f"nlp_{secrets.token_urlsafe(32)}"
    key_prefix = full_key[:8]  # 前8位作为前缀

    # 对密钥进行哈希存储（不存储明文）
    import bcrypt
    key_hash = bcrypt.hashpw(full_key.encode(), bcrypt.gensalt()).decode()

    # 计算过期时间
    expires_at = None
    if data.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=data.expires_in_days)

    # 创建 API Key 记录
    api_key = APIKey(
        user_id=current_user.id,
        name=data.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        permissions=data.permissions,
        expires_at=expires_at,
        is_active=True,
    )

    session.add(api_key)
    await session.commit()
    await session.refresh(api_key)

    return APIKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        api_key=full_key,  # 仅返回一次完整密钥
        key_prefix=api_key.key_prefix,
        permissions=api_key.permissions,
        is_active=api_key.is_active,
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
        created_at=api_key.created_at.isoformat(),
        message="API Key 创建成功，请妥善保存完整密钥"
    )


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_async_session),
):
    """撤销 API Key"""
    result = await session.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")

    # 软删除：禁用密钥
    api_key.is_active = False
    await session.commit()

    return {"msg": "API Key revoked successfully", "key_id": key_id}
