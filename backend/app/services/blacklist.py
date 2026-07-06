"""
Token 黑名单服务

使用 Redis 存储已注销的 Token，确保 Token 在过期前无法使用
"""

from datetime import datetime, timezone
from typing import Optional
from jose import jwt
from ..core.config import settings
from ..services.cache import cache_service

# JWT 配置
ALGORITHM = "HS256"


class TokenBlacklist:
    """Token 黑名单管理"""

    def __init__(self):
        self.prefix = "blacklist:token:"

    async def add_to_blacklist(
        self,
        token: str,
        expires_in: Optional[int] = None
    ) -> bool:
        """
        将 Token 加入黑名单

        Args:
            token: JWT Token
            expires_in: 过期时间（秒），如果为 None 则从 Token 中提取

        Returns:
            是否成功
        """
        try:
            # 解码 Token 获取过期时间
            payload = jwt.decode(
                token,
                settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else "your-secret-key-change-in-production",
                algorithms=[ALGORITHM],
                options={"verify_signature": False}
            )

            # 计算 Token 的剩余有效期
            if expires_in is None:
                exp = payload.get("exp")
                if exp:
                    exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
                    now = datetime.now(timezone.utc)
                    expires_in = int((exp_datetime - now).total_seconds())
                else:
                    # 默认 15 分钟
                    expires_in = 900

            # 确保过期时间至少 1 秒，最多 24 小时
            expires_in = max(1, min(expires_in, 86400))

            # 使用 Token 的 JTI (JWT ID) 或整个 Token 作为键
            jti = payload.get("jti", token)

            # 存储到 Redis，设置过期时间
            key = f"{self.prefix}{jti}"
            await cache_service.set(key, "blacklisted", expire=expires_in)

            return True

        except Exception as e:
            print(f"Failed to add token to blacklist: {e}")
            return False

    async def is_blacklisted(self, token: str) -> bool:
        """
        检查 Token 是否在黑名单中

        Args:
            token: JWT Token

        Returns:
            是否在黑名单中
        """
        try:
            # 解码 Token 获取 JTI
            payload = jwt.decode(
                token,
                settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else "your-secret-key-change-in-production",
                algorithms=[ALGORITHM],
                options={"verify_signature": False}
            )

            jti = payload.get("jti", token)
            key = f"{self.prefix}{jti}"

            # 检查 Redis 中是否存在
            value = await cache_service.get(key)
            return value is not None

        except Exception as e:
            print(f"Failed to check token blacklist: {e}")
            return False

    async def remove_from_blacklist(self, token: str) -> bool:
        """
        从黑名单中移除 Token

        Args:
            token: JWT Token

        Returns:
            是否成功
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else "your-secret-key-change-in-production",
                algorithms=[ALGORITHM],
                options={"verify_signature": False}
            )

            jti = payload.get("jti", token)
            key = f"{self.prefix}{jti}"

            await cache_service.delete(key)
            return True

        except Exception as e:
            print(f"Failed to remove token from blacklist: {e}")
            return False

    async def clear_expired(self) -> int:
        """
        清理过期的黑名单条目（Redis 会自动处理，此方法主要用于统计）

        Returns:
            当前黑名单中的 Token 数量
        """
        try:
            # 获取所有黑名单键
            pattern = f"{self.prefix}*"
            keys = await cache_service.keys(pattern)
            return len(keys)
        except Exception as e:
            print(f"Failed to clear expired blacklist entries: {e}")
            return 0


# 全局黑名单实例
token_blacklist = TokenBlacklist()
