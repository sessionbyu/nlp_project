# backend/app/utils/logger.py
import logging
import sys
from pathlib import Path

from ..core.config import settings


def setup_logger(name: str = "nlp_backend") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 格式器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 1. 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 文件 handler（如果配置了日志目录）
    if settings.LOG_DIR:
        log_dir = Path(settings.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{name}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(settings.LOG_LEVEL)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# 全局默认 logger
logger = setup_logger()
