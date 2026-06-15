# backend/app/main.py
from app.api.v1.predict import router
from app.core.config import settings
from app.utils.logger import logger
from fastapi import FastAPI

app = FastAPI(title="NLP API")

app.include_router(router, prefix="/api/v1")


@app.get("/")
def index():
    logger.info("Root endpoint called")
    return {"status": "running", "redis_host": settings.REDIS_HOST}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
async def startup():
    logger.info("Starting up NLP API...")
