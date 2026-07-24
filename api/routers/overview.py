from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from api.services.overview_service import get_overview_kpis


router = APIRouter(
    prefix="/overview",
    tags=["Overview"],
)


@router.get("/kpis")
def overview_kpis() -> Dict[str, Any]:
    """
    Return the main KPIs displayed on the Overview page.
    """
    try:
        return get_overview_kpis()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve overview KPIs: {error}",
        ) from error