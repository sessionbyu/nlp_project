# backend/app/api/v1/predict.py
from typing import List, Optional

from app.core.config import settings
from app.db.session import get_async_session
from app.services.history import save_prediction
from app.services.inference import predict_text, predict_batch, sentiment_service
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


class BatchPredictItem(BaseModel):
    text: str
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


class BatchPredictRequest(BaseModel):
    texts: List[str]
    model_key: Optional[str] = None


class BatchPredictResponse(BaseModel):
    results: List[BatchPredictItem]
    total: int
    success: int
    failed: int


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

@router.post("/batch-predict", response_model=BatchPredictResponse)
async def batch_predict(
    data: BatchPredictRequest,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """批量预测多条文本"""
    if not data.texts:
        raise HTTPException(status_code=400, detail="Texts list cannot be empty")

    if len(data.texts) > 1000:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size too large. Maximum 1000 texts, got {len(data.texts)}"
        )

    # 确定使用的模型 key
    model_key = data.model_key or settings.DEFAULT_MODEL
    if model_key not in sentiment_service.available_models:
        available = sentiment_service.available_models
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_key}' not available. Available: {available}",
        )

    # 执行批量预测
    batch_results = await predict_batch(data.texts, model_key=model_key)

    # 格式化结果
    results = []
    success_count = 0
    failed_count = 0

    for i, result in enumerate(batch_results):
        if "error" in result:
            results.append(BatchPredictItem(
                text=data.texts[i],
                success=False,
                error=result.get("error", "Unknown error")
            ))
            failed_count += 1
        else:
            # 保存到数据库
            try:
                await save_prediction(
                    session=session,
                    input_text=data.texts[i],
                    label=result["label"],
                    score=result["score"],
                    source_ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
            except Exception as e:
                logger.warning(f"Failed to save prediction for text {i}: {e}")

            results.append(BatchPredictItem(
                text=data.texts[i],
                success=True,
                result={
                    "label": result["label"],
                    "score": result["score"],
                    "model_key": model_key,
                }
            ))
            success_count += 1

    return BatchPredictResponse(
        results=results,
        total=len(data.texts),
        success=success_count,
        failed=failed_count,
    )
