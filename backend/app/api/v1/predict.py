# backend/app/api/v1/predict.py
from typing import Optional

from app.core.config import settings
from app.db.session import get_async_session
from app.services.history import save_prediction
from app.services.inference import predict_text, sentiment_service
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class PredictRequest(BaseModel):
    text: str
    model_key: Optional[str] = None  # 可选，默认使用 settings.DEFAULT_MODEL


class PredictResponse(BaseModel):
    label: str
    score: float
    model_key: str  # 返回实际使用的模型 key，便于前端确认


@router.post("/predict", response_model=PredictResponse)
async def predict(
    data: PredictRequest,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # 确定使用的模型 key
    model_key = data.model_key or settings.DEFAULT_MODEL
    if model_key not in sentiment_service.available_models:
        available = sentiment_service.available_models
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_key}' not available. Available: {available}",
        )

    result = await predict_text(data.text, model_key=model_key)

    # 异步保存预测记录到数据库
    await save_prediction(
        session=session,
        input_text=data.text,
        label=result["label"],
        score=result["score"],
        source_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # 在响应中添加 model_key
    result["model_key"] = model_key
    return result


@router.get("/models")
async def list_models():
    """列出当前可用的模型列表"""
    return {
        "available_models": sentiment_service.available_models,
        "default_model": settings.DEFAULT_MODEL,
    }