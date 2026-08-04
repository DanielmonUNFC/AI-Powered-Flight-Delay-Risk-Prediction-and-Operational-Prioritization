from typing import Any

from fastapi import APIRouter, HTTPException

from api.services.overview_service import get_overview_data

router = APIRouter(
    prefix="/overview",
    tags=["Overview"],
)

@router.get("")
def overview_page_data() -> dict[str, Any]:
    """
    Return the full Overview tab payload:
    KPIs, monthly trend, delay causes, and operational insight.
    """
    try:
        return get_overview_data()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve overview data: {error}",
        ) from error
