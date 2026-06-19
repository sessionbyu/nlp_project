import os
from typing import Dict, Optional


class Settings:
    # ==============================
    # Redis 配置
    # ==============================
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

    # ==============================
    # PostgreSQL 数据库配置
    # ==============================
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_USER: str = os.getenv("DB_USER", "nlp_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "nlp_pass")
    DB_NAME: str = os.getenv("DB_NAME", "nlp_db")

    @property
    def DATABASE_URL(self) -> str:
        """构建异步数据库连接 URL"""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """构建同步数据库连接 URL（用于 Alembic 迁移）"""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ==============================
    # 模型路径 (挂载在 /data/models 下)
    # ==============================
    MODEL_PATH: str = os.getenv("MODEL_PATH", "/data/models/bert-base-chinese")
    # 如果使用 HuggingFace 缓存，也可以留空让它自动下载
    USE_CACHE: bool = os.getenv("USE_CACHE", "true").lower() == "true"

    # ==============================
    # 可用模型列表
    # ==============================
    # 默认启用的模型 key 列表，可通过环境变量 AVAILABLE_MODELS 覆盖（逗号分隔）
    AVAILABLE_MODELS: list = os.getenv(
        "AVAILABLE_MODELS", "vader,bert"
    ).split(",")
    # 默认模型（当请求未指定 model_key 时使用）
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "bert")

    # ==============================
    # 日志级别
    # ==============================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: Optional[str] = os.getenv("LOG_DIR", None)  # 例如 "/app/logs/backend"


settings = Settings()