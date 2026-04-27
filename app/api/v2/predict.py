from fastapi import APIRouter

from app.schemas import PredictionResponse, TextIn
from app.service import language as language_service

router = APIRouter()


@router.post("/predict/language", response_model=PredictionResponse)
def get_language(payload: TextIn):
    return language_service.predict_pipeline(payload.text)
