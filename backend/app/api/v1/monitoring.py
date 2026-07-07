"""
监控 API 路由

功能：
1. 健康检查
2. 系统状态
3. Prometheus 指标
"""
import time
try:
    import psutil
except ImportError:
    psutil = None
from typing import Dict, Any

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_async_session
from ...core.config import settings
from ...utils.logger import logger

router = APIRouter(tags=["Monitoring"])


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "NLP API",
    }


@router.get("/health/ready")
async def readiness_check(
    session: AsyncSession = Depends(get_async_session),
):
    """就绪检查（检查数据库连接）"""
    try:
        # 检查数据库连接
        result = await session.execute(text("SELECT 1"))
        result.scalar()

        return {
            "status": "ready",
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not ready",
            "database": "disconnected",
            "error": str(e),
        }


@router.get("/health/live")
async def liveness_check():
    """存活检查"""
    return {
        "status": "alive",
        "timestamp": time.time(),
    }


@router.get("/status")
async def system_status(
    session: AsyncSession = Depends(get_async_session),
):
    """系统状态信息"""
    # 系统资源（如果 psutil 不可用，使用默认值）
    if psutil is None:
        logger.warning("psutil not installed, returning mock system status")
        cpu_percent = 0.0
        memory = type('obj', (object,), {
            'total': 0,
            'available': 0,
            'percent': 0.0
        })()
        disk = type('obj', (object,), {
            'total': 0,
            'free': 0,
            'percent': 0.0
        })()
    else:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

    # 数据库状态
    db_status = "unknown"
    try:
        result = await session.execute(text("SELECT COUNT(*) FROM prediction_history"))
        prediction_count = result.scalar()
        db_status = "connected"
    except Exception as e:
        prediction_count = 0
        db_status = f"error: {str(e)}"

    return {
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "percent": disk.percent,
            },
        },
        "database": {
            "status": db_status,
            "prediction_count": prediction_count,
        },
        "config": {
            "default_model": settings.DEFAULT_MODEL,
            "redis_host": settings.REDIS_HOST,
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
        },
    }


# Prometheus metrics（如果安装了 prometheus-client）
try:
    from prometheus_client import generate_latest, REGISTRY
    from prometheus_client.core import CollectorRegistry

    @router.get("/metrics")
    async def get_metrics():
        """Prometheus 指标端点"""
        return Response(
            content=generate_latest(REGISTRY),
            media_type="text/plain",
        )
except ImportError:
    logger.warning("prometheus-client not installed, /metrics endpoint unavailable")

    @router.get("/metrics")
    async def get_metrics_unavailable():
        """Prometheus 指标不可用"""
        return {
            "error": "prometheus-client not installed",
            "install": "pip install prometheus-client",
        }
