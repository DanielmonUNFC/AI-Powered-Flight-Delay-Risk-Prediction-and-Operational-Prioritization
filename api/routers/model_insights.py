"""HTTP endpoint for global and local SHAP explanations."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from api.services.model_insights_service import (
    DEFAULT_INSIGHTS_LIMIT,
    MAX_INSIGHTS_LIMIT,
    get_model_insights_data,
)


router = APIRouter(
    prefix="/model-insights",
    tags=["Model Insights"],
)


@router.get("")
def model_insights_page_data(
    limit: int = Query(
        default=DEFAULT_INSIGHTS_LIMIT,
        ge=1,
        le=MAX_INSIGHTS_LIMIT,
        description="Maximum global and local SHAP features to return.",
    ),
) -> dict[str, Any]:
    """Return the complete Model Insights payload without simulated fallback."""
    try:
        return get_model_insights_data(limit=limit)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve Model Insights data: {error}",
        ) from error
