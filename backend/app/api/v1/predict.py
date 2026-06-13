from app.models.schema import PredictRequest, PredictResponse
from app.services.inference import predict_async
from fastapi import APIRouter

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict(data: PredictRequest):
    result = await predict_async(data.text)

    return result
