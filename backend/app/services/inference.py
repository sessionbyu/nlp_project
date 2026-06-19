import asyncio
import hashlib
import json
from typing import Any, Dict, Optional

import redis.asyncio as redis

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


class SentimentService:
    """情感分析服务单例，维护可用模型字典，支持热加载"""

    def __init__(self):
        self._models: Dict[str, Any] = {}
        self._load_all_models()

    def _load_all_models(self):
        """根据配置加载所有可用模型"""
        self._models = {}
        for model_key in settings.AVAILABLE_MODELS:
            model_key = model_key.strip()
            if not model_key:
                continue
            try:
                if model_key == "bert":
                    from app.models.bert_model import BertModel
                    self._models["bert"] = BertModel()
                    logger.info("BERT model loaded into registry")
                elif model_key == "vader":
                    from app.models.vader_model import VaderModel
                    self._models["vader"] = VaderModel()
                    logger.info("VADER model loaded into registry")
                else:
                    logger.warning(
                        f"Unknown model key '{model_key}', skipping"
                    )
            except Exception as e:
                logger.error(
                    f"Failed to load model '{model_key}': {e}"
                )
        logger.info(
            f"Model registry initialized with keys: {list(self._models.keys())}"
        )

    def reload_models(self):
        """热加载：重新初始化所有模型实例"""
        logger.info("Reloading all models...")
        # 清理旧模型引用
        old_keys = list(self._models.keys())
        self._models.clear()
        for key in old_keys:
            logger.info(f"Unloaded model: {key}")
        # 重新加载
        self._load_all_models()
        logger.info("Model reload complete")

    def get_model(self, model_key: str):
        """获取指定 key 的模型实例"""
        model = self._models.get(model_key)
        if model is None:
            available = list(self._models.keys())
            raise ValueError(
                f"Model '{model_key}' not found. "
                f"Available models: {available}"
            )
        return model

    @property
    def available_models(self) -> list:
        """返回当前可用的模型 key 列表"""
        return list(self._models.keys())


# 全局单例
sentiment_service = SentimentService()


def get_cache_key(text: str, model_key: str = "") -> str:
    """生成文本的哈希键（包含模型 key 以区分不同模型的缓存）"""
    raw = f"{model_key}:{text}"
    return f"nlp:cache:{hashlib.md5(raw.encode()).hexdigest()}"


async def predict_text(
    text: str, model_key: Optional[str] = None
) -> Dict[str, Any]:
    """预测单条文本的情感

    Args:
        text: 输入文本
        model_key: 模型 key（如 "vader", "bert"），默认使用配置中的 DEFAULT_MODEL
    """
    if model_key is None:
        model_key = settings.DEFAULT_MODEL

    # 验证模型可用性
    if model_key not in sentiment_service.available_models:
        available = sentiment_service.available_models
        raise ValueError(
            f"Model '{model_key}' not available. "
            f"Available models: {available}"
        )

    # 1. 检查缓存
    if settings.USE_CACHE:
        cache_key = get_cache_key(text, model_key)
        cached = await redis_client.get(cache_key)
        if cached:
            logger.info(
                f"Cache hit for text: {text[:50]}... (model={model_key})"
            )
            return json.loads(cached)

    # 2. 执行模型推理（耗时的同步操作放入线程池）
    logger.info(
        f"Running inference for text: {text[:50]}... (model={model_key})"
    )
    model = sentiment_service.get_model(model_key)
    result = await asyncio.to_thread(model.predict, text)

    # 3. 存入缓存（过期时间 1 小时）
    if settings.USE_CACHE:
        await redis_client.setex(
            cache_key,
            3600,
            json.dumps(result, ensure_ascii=False),
        )

    return result


async def predict_batch(
    texts: list, model_key: Optional[str] = None
) -> list:
    """批量预测多条文本"""
    results = []
    for text in texts:
        result = await predict_text(text, model_key=model_key)
        results.append(result)
    return results