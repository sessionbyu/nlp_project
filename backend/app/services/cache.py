"""
缓存服务（Redis）

功能：
1. 缓存预测结果
2. 缓存统计信息
3. 缓存用户会话
"""
import hashlib
import json
from typing import Optional

import redis.asyncio as redis
from fastapi import Depends

from ..core.config import settings


class CacheService:
    """Redis 缓存服务"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

    async def init(self):
        """初始化 Redis 连接"""
        self.redis_client = await redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self):
        """关闭 Redis 连接"""
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        if not self.redis_client:
            return None
        return await self.redis_client.get(key)

    async def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """设置缓存（默认1小时过期）"""
        if not self.redis_client:
            return False
        return await self.redis_client.setex(key, expire, value)

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.redis_client:
            return False
        return await self.redis_client.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.redis_client:
            return False
        return await self.redis_client.exists(key) > 0

    # ========== 预测结果缓存 ==========

    @staticmethod
    def _get_prediction_cache_key(text: str, model_key: str) -> str:
        """生成预测结果缓存键"""
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return f"prediction:{model_key}:{text_hash}"

    async def get_prediction(self, text: str, model_key: str) -> Optional[dict]:
        """获取缓存的预测结果"""
        key = self._get_prediction_cache_key(text, model_key)
        cached = await self.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_prediction(self, text: str, model_key: str, result: dict, expire: int = 86400) -> bool:
        """缓存预测结果（默认24小时）"""
        key = self._get_prediction_cache_key(text, model_key)
        return await self.set(key, json.dumps(result), expire=expire)

    async def invalidate_prediction(self, text: str, model_key: str) -> bool:
        """清除预测缓存"""
        key = self._get_prediction_cache_key(text, model_key)
        return await self.delete(key)

    # ========== 统计信息缓存 ==========

    @staticmethod
    def _get_stats_cache_key() -> str:
        """生成统计信息缓存键"""
        return "stats:prediction"

    async def get_stats(self) -> Optional[dict]:
        """获取缓存的统计信息"""
        key = self._get_stats_cache_key()
        cached = await self.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_stats(self, stats: dict, expire: int = 300) -> bool:
        """缓存统计信息（默认5分钟）"""
        key = self._get_stats_cache_key()
        return await self.set(key, json.dumps(stats), expire=expire)

    async def invalidate_stats(self) -> bool:
        """清除统计缓存"""
        key = self._get_stats_cache_key()
        return await self.delete(key)


# 全局缓存服务实例
cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """获取缓存服务（FastAPI 依赖注入）"""
    return cache_service
