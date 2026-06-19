# backend/app/main.py
import os

from app.api.v1.history import router as history_router
from app.api.v1.predict import router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.services.inference import sentiment_service
from app.utils.logger import logger
from app.utils.model_watcher import start_model_watcher
from fastapi import FastAPI, HTTPException

app = FastAPI(title="NLP API")

app.include_router(router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")


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
    """服务关闭时停止文件监控"""
    watcher = getattr(app.state, "model_watcher", None)
    if watcher is not None:
        watcher.stop()
        watcher.join()
        logger.info("Model file watcher stopped")
