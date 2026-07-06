# backend/app/main.py
import os
import time
from typing import Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.history import router as history_router
from app.api.v1.predict import router
from app.api.v1.admin import router as admin_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.upload import router as upload_router
from app.api.v1.tasks import router as tasks_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.services.cache import cache_service
from app.services.inference import sentiment_service
from app.services.rate_limit import rate_limiter
from app.services.websocket import manager
from app.services.text_analysis import text_analysis_service
from app.utils.logger import logger
from app.utils.model_watcher import start_model_watcher

app = FastAPI(title="NLP API")

# CORS 配置
# 注意：当 allow_credentials=True 时，不能使用 ["*"]，必须指定具体域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 从配置读取允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 请求日志中间件 ==========

@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """记录所有请求"""
    start_time = time.time()

    # 获取客户端信息
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # 处理请求
    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # 记录请求日志
        logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"IP: {client_ip} | "
            f"Time: {process_time:.3f}s"
        )

        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} | "
            f"Error: {str(e)} | "
            f"IP: {client_ip} | "
            f"Time: {process_time:.3f}s"
        )
        raise

# ========== 限流中间件 ==========

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next: Callable):
    """API 限流检查（监控端点和登录端点不受限流）"""
    if not settings.RATE_LIMIT_ENABLED:
        return await call_next(request)

    # 监控端点和认证端点不受限流
    if request.url.path.startswith(("/health", "/status", "/metrics")) or \
       "/auth/" in request.url.path:
        return await call_next(request)

    # 获取限流键（优先使用 user_id，否则用 IP）
    client_ip = request.client.host if request.client else "unknown"
    limit_key = client_ip

    # 检查限流
    is_limited, info = await rate_limiter.is_rate_limited(
        key=limit_key,
        max_requests=settings.RATE_LIMIT_DEFAULT_MAX,
        window_seconds=settings.RATE_LIMIT_DEFAULT_WINDOW,
    )

    if is_limited:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests",
                "limit": info["limit"],
                "reset_in": info["reset_in"],
            },
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset"]),
                "Retry-After": str(info["reset_in"]),
            },
        )

    # 添加限流信息到响应头
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(info["reset"])

    return response

app.include_router(router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(monitoring_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")


@app.get("/")
def index():
    logger.info("Root endpoint called")
    return {
        "status": "running",
        "redis_host": settings.REDIS_HOST,
        "available_models": sentiment_service.available_models,
        "default_model": settings.DEFAULT_MODEL,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ==============================
# 管理接口：模型热加载
# ==============================
@app.post("/admin/reload-model")
def reload_model():
    """热加载所有模型：重新初始化模型实例，无需重启服务"""
    try:
        sentiment_service.reload_models()
        return {
            "status": "ok",
            "message": "All models reloaded successfully",
            "available_models": sentiment_service.available_models,
        }
    except Exception as e:
        logger.error(f"Model reload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Model reload failed: {str(e)}",
        )


@app.on_event("startup")
async def startup():
    logger.info("Starting up NLP API...")

    # 初始化 Redis 缓存
    try:
        await cache_service.init()
        logger.info("Redis cache initialized")
    except Exception as e:
        logger.warning(f"Redis cache initialization failed: {e}")

    # 初始化限流器
    try:
        await rate_limiter.init()
        logger.info("Rate limiter initialized")
    except Exception as e:
        logger.warning(f"Rate limiter initialization failed: {e}")

    # 自动创建数据库表（如果不存在）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified.")

    # 启动模型文件监控（watchdog 自动热加载）
    model_dir = os.path.dirname(settings.MODEL_PATH)
    if os.path.isdir(model_dir):
        app.state.model_watcher = start_model_watcher(
            watch_path=model_dir,
            reload_callback=sentiment_service.reload_models,
            debounce_seconds=5.0,
        )
    else:
        logger.warning(
            f"Model directory not found: {model_dir}, "
            f"file watcher not started. Use POST /admin/reload-model to reload."
        )


@app.on_event("shutdown")
def shutdown():
    """服务关闭时停止文件监控和清理"""
    watcher = getattr(app.state, "model_watcher", None)
    if watcher is not None:
        watcher.stop()
        watcher.join()
        logger.info("Model file watcher stopped")

    # 关闭缓存服务
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cache_service.close())
        loop.run_until_complete(rate_limiter.close())
        logger.info("Cache and rate limiter closed")
    except Exception as e:
        logger.warning(f"Error closing services: {e}")
