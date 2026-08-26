"""Routes for live single-flight delay prediction."""

from datetime import date, time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.services.prediction_service import (
    get_prediction_options,
    predict_delay,
)


router = APIRouter(prefix="/predictions", tags=["Predictions"])


class PredictionRequest(BaseModel):
    airline: str = Field(min_length=2, max_length=3)
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    flight_date: date
    scheduled_departure: time
    scheduled_arrival: time
    flight_number: str | None = Field(default=None, max_length=10)


@router.get("/options")
def prediction_options() -> dict[str, Any]:
    """Return airline and airport choices supported by the model."""
    try:
        return get_prediction_options()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load prediction options: {error}",
        ) from error


@router.post("")
def create_prediction(request: PredictionRequest) -> dict[str, Any]:
    """Generate a live delay-risk prediction for one scheduled flight."""
    try:
        return predict_delay(request.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate prediction: {error}",
        ) from error
