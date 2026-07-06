"""
管理员 API 路由

功能：
1. 用户管理
2. API Key 管理
3. 系统统计
4. 数据管理
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import User, PredictionHistory, APIKey
from ...db.session import get_async_session
from ...services.auth import require_admin, get_current_user_required
from ...utils.logger import logger

router = APIRouter(prefix="/admin", tags=["Admin"])


# ========== Pydantic Schemas ==========

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    role: Optional[str] = Field(None, description="用户角色 (admin/user)")
    is_active: Optional[bool] = Field(None, description="是否激活")


class APIKeyCreateRequest(BaseModel):
    name: str = Field(..., description="API Key 名称")
    permissions: str = Field("predict,history", description="权限列表（逗号分隔）")
    rate_limit: int = Field(100, description="每小时请求限制")
    expires_in_days: Optional[int] = Field(None, description="过期天数")


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    permissions: str
    rate_limit: int
    is_active: bool
    usage_count: int
    last_used: Optional[datetime]
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class SystemStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_predictions: int
    recent_predictions_24h: int
    total_api_keys: int
    active_api_keys: int
    label_distribution: dict
    avg_score: float


# ========== 用户管理 ==========

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin),
):
    """获取用户列表（管理员）"""
    query = select(User)

    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await session.execute(query)
    users = result.scalars().all()

    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin),
):
    """获取指定用户信息（管理员）"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdateRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin),
):
    """更新用户信息（管理员）"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 禁止修改自己的角色
    if user.id == current_user.id and data.role is not None:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    # 更新字段
    if data.role is not None:
        if data.role not in ["admin", "user"]:
            raise HTTPException(status_code=400, detail="Invalid role")
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active

    await session.commit()
    await session.refresh(user)

    logger.info(f"User updated by admin: {current_user.username} -> user_id={user_id}")
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin),
):
    """软删除用户（管理员）"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 禁止删除自己
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    # 软删除
    from datetime import datetime
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    user.is_active = False

    await session.commit()

    logger.info(f"User deleted by admin: {current_user.username} -> user_id={user_id}")
    return {"msg": "User deleted successfully"}


# ========== API Key 管理 ==========

@router.post("/users/{user_id}/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    user_id: int,
    data: APIKeyCreateRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin),
):
    """为用户创建 API Key（管理员）"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 生成 API Key
    import secrets
    raw_key = secrets.token_urlsafe(32)
    key_hash = secrets.token_hex(32)  # 实际存储哈希
    key_prefix = raw_key[:8]

    # 计算过期时间
    from datetime import timedelta
    expires_at = None
    if data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=data.expires_in_days)

    api_key = APIKey(
        user_id=user_id,
        name=data.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        permissions=data.permissions,
        rate_limit=data.rate_limit,
        expires_at=expires_at,
    )

    session.add(api_key)
    await session.commit()
    await session.refresh(api_key)

    logger.info(f"API Key created by admin: {current_user.username} -> user={user.username}")

    # 返回时包含明文 key（只显示一次）
    response = APIKeyResponse.model_validate(api_key).model_dump()
    response["key"] = raw_key
    response["warning"] = "Save this key securely, it won't be shown again"

    return response


@router.get("/users/{user_id}/api-keys", response_model=List[APIKeyResponse])
async def list_user_api_keys(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin),
):
    """获取用户的 API Keys（管理员）"""
    result = await session.execute(
        select(APIKey).where(APIKey.user_id == user_id).order_by(APIKey.created_at.desc())
    )
    keys = result.scalars().all()
    return keys


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin),
):
    """撤销 API Key（管理员）"""
    result = await session.execute(select(APIKey).where(APIKey.id == key_id))
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")

    api_key.is_active = False
    await session.commit()

    logger.info(f"API Key revoked by admin: {current_user.username} -> key_id={key_id}")
    return {"msg": "API Key revoked successfully"}


# ========== 系统统计 ==========

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin),
):
    """获取系统统计信息（管理员）"""
    # 用户统计
    total_users_result = await session.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    active_users_result = await session.execute(
        select(func.count(User.id)).where(User.is_active == True, User.is_deleted == False)
    )
    active_users = active_users_result.scalar() or 0

    # 预测统计
    total_predictions_result = await session.execute(select(func.count(PredictionHistory.id)))
    total_predictions = total_predictions_result.scalar() or 0

    # 最近24小时预测数
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_predictions_result = await session.execute(
        select(func.count(PredictionHistory.id)).where(PredictionHistory.created_at >= yesterday)
    )
    recent_predictions_24h = recent_predictions_result.scalar() or 0

    # API Key 统计
    total_keys_result = await session.execute(select(func.count(APIKey.id)))
    total_api_keys = total_keys_result.scalar() or 0

    active_keys_result = await session.execute(
        select(func.count(APIKey.id)).where(APIKey.is_active == True)
    )
    active_api_keys = active_keys_result.scalar() or 0

    # 情感分布
    label_query = (
        select(PredictionHistory.label, func.count(PredictionHistory.id))
        .group_by(PredictionHistory.label)
    )
    label_result = await session.execute(label_query)
    label_distribution = {row[0]: row[1] for row in label_result.fetchall()}

    # 平均分数
    avg_score_result = await session.execute(select(func.avg(PredictionHistory.score)))
    avg_score = avg_score_result.scalar() or 0.0

    return SystemStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_predictions=total_predictions,
        recent_predictions_24h=recent_predictions_24h,
        total_api_keys=total_api_keys,
        active_api_keys=active_api_keys,
        label_distribution=label_distribution,
        avg_score=round(float(avg_score), 4),
    )


# ========== 数据管理 ==========

@router.get("/predictions/all")
async def get_all_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin),
):
    """获取所有用户的预测记录（管理员）"""
    query = (
        select(PredictionHistory)
        .order_by(PredictionHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(query)
    records = result.scalars().all()

    return {
        "total": len(records),
        "records": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "input_text": r.input_text[:100],
                "label": r.label,
                "score": r.score,
                "created_at": r.created_at.isoformat(),
            }
            for r in records
        ],
    }


@router.delete("/predictions/{prediction_id}")
async def delete_prediction(
    prediction_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin),
):
    """软删除预测记录（管理员）"""
    result = await session.execute(
        select(PredictionHistory).where(PredictionHistory.id == prediction_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")

    record.is_deleted = True
    record.deleted_at = datetime.utcnow()

    await session.commit()

    logger.info(f"Prediction deleted by admin: {current_user.username} -> prediction_id={prediction_id}")
    return {"msg": "Prediction deleted successfully"}
