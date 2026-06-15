import asyncio
import hashlib
import json
from typing import Any, Dict

import redis.asyncio as redis
from app.models.bert_model import bert_model

from ..core.config import settings
from ..utils.logger import logger

# 创建 Redis 连接池（异步）
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)


def get_cache_key(text: str) -> str:
    """生成文本的哈希键"""
    return f"nlp:cache:{hashlib.md5(text.encode()).hexdigest()}"


async def predict_text(text: str) -> Dict[str, Any]:
    # 1. 检查缓存
    if settings.USE_CACHE:
        cache_key = get_cache_key(text)
        cached = await redis_client.get(cache_key)
        if cached:
            logger.info(f"Cache hit for text: {text[:50]}...")
            return json.loads(cached)

    # 2. 执行模型推理（耗时的同步操作放入线程池）
    logger.info(f"Running inference for text: {text[:50]}...")
    result = await asyncio.to_thread(bert_model.predict, text)

    # 3. 存入缓存（过期时间 1 小时）
    if settings.USE_CACHE:
        await redis_client.setex(
            cache_key, 3600, json.dumps(result, ensure_ascii=False)
        )

    return result
