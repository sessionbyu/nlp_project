# backend/app/api/v1/predict.py
from app.services.inference import predict_text
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class PredictRequest(BaseModel):
    text: str


class PredictResponse(BaseModel):
    label: str
    score: float


@router.post("/predict", response_model=PredictResponse)
async def predict(data: PredictRequest):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    result = await predict_text(data.text)
    return result
