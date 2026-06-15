import os
from typing import Optional


class Settings:
    # Redis 配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

    # 模型路径 (挂载在 /data/models 下)
    MODEL_PATH: str = os.getenv("MODEL_PATH", "/data/models/bert-base-chinese")
    # 如果使用 HuggingFace 缓存，也可以留空让它自动下载
    USE_CACHE: bool = os.getenv("USE_CACHE", "true").lower() == "true"

    # 日志级别
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: Optional[str] = os.getenv("LOG_DIR", None)  # 例如 "/app/logs/backend"


settings = Settings()
