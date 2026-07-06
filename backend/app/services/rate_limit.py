"""
API 限流服务

功能：
1. 基于 Redis 的限流
2. 支持不同限流策略
3. 自定义限流规则
"""
import time
from typing import Optional

import redis.asyncio as redis

from ..core.config import settings


class RateLimiter:
    """Redis 限流器（基于滑动窗口）"""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def init(self):
        """初始化 Redis 连接"""
        self.redis = await redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self):
        """关闭连接"""
        if self.redis:
            await self.redis.close()

    async def is_rate_limited(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 3600,
    ) -> tuple[bool, dict]:
        """
        检查是否超过限流阈值

        Args:
            key: 限流键（如 user_id、ip_address）
            max_requests: 窗口期内最大请求数
            window_seconds: 时间窗口（秒）

        Returns:
            (是否限流, 信息字典)
        """
        if not self.redis:
            return False, {"error": "Redis not initialized"}

        now = int(time.time())
        window_key = f"rate_limit:{key}:{now // window_seconds}"

        # 使用 Redis Pipeline
        pipe = self.redis.pipeline()

        # 增加请求计数
        pipe.incr(window_key)
        pipe.expire(window_key, window_seconds)

        results = await pipe.execute()
        current_count = results[0]

        # 计算剩余配额
        remaining = max(0, max_requests - current_count)
        reset_time = (now // window_seconds + 1) * window_seconds
        reset_in = reset_time - now

        is_limited = current_count > max_requests

        info = {
            "limit": max_requests,
            "remaining": remaining,
            "reset": reset_time,
            "reset_in": reset_in,
            "window_seconds": window_seconds,
        }

        return is_limited, info

    async def get_rate_limit_info(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 3600,
    ) -> dict:
        """获取限流信息（不增加计数）"""
        if not self.redis:
            return {"error": "Redis not initialized"}

        now = int(time.time())
        window_key = f"rate_limit:{key}:{now // window_seconds}"

        current_count = await self.redis.get(window_key)
        current_count = int(current_count) if current_count else 0

        remaining = max(0, max_requests - current_count)
        reset_time = (now // window_seconds + 1) * window_seconds
        reset_in = reset_time - now

        return {
            "limit": max_requests,
            "remaining": remaining,
            "reset": reset_time,
            "reset_in": reset_in,
            "window_seconds": window_seconds,
            "used": current_count,
        }


# 全局限流器实例
rate_limiter = RateLimiter()


# ========== 限流规则 ==========

class RateLimitRule:
    """限流规则"""

    def __init__(
        self,
        name: str,
        max_requests: int,
        window_seconds: int,
        description: str = "",
    ):
        self.name = name
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.description = description

    def __repr__(self):
        return f"RateLimitRule({self.name}, {self.max_requests}/{self.window_seconds}s)"


# 预设限流规则
RATE_LIMIT_RULES = {
    # 预测接口 - 宽松限制
    "predict": RateLimitRule(
        name="predict",
        max_requests=100,
        window_seconds=3600,
        description="预测接口：每小时100次",
    ),
    # 批量预测 - 较严格限制
    "batch_predict": RateLimitRule(
        name="batch_predict",
        max_requests=20,
        window_seconds=3600,
        description="批量预测：每小时20次",
    ),
    # 认证接口 - 严格限制（防暴力破解）
    "auth": RateLimitRule(
        name="auth",
        max_requests=10,
        window_seconds=300,  # 5分钟
        description="认证接口：每5分钟10次",
    ),
    # 默认规则
    "default": RateLimitRule(
        name="default",
        max_requests=1000,
        window_seconds=3600,
        description="默认：每小时1000次",
    ),
}


def get_rate_limit_rule(endpoint: str) -> RateLimitRule:
    """根据端点获取限流规则"""
    return RATE_LIMIT_RULES.get(endpoint, RATE_LIMIT_RULES["default"])
