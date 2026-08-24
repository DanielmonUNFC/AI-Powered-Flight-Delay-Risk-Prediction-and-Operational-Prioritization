from typing import Any

from fastapi import APIRouter, HTTPException, Query

from api.services.prioritization_service import (
    CAPACITY_K_OPTIONS,
    DEFAULT_CAPACITY_K,
    DEFAULT_DISPLAY_LIMIT,
    MAX_DISPLAY_LIMIT,
    get_prioritization_data,
)


router = APIRouter(
    prefix="/prioritization",
    tags=["Prioritization"],
)


@router.get("")
def prioritization_page_data(
    capacity_k: int = Query(
        default=DEFAULT_CAPACITY_K,
        description="Operational review capacity (K). Must match a precomputed value.",
    ),
    display_limit: int = Query(
        default=DEFAULT_DISPLAY_LIMIT,
        ge=1,
        le=MAX_DISPLAY_LIMIT,
        description="Maximum selected flights returned for the dashboard table.",
    ),
) -> dict[str, Any]:
    """
    Return the Operational Prioritization tab payload from
    flight_prioritization_results for the requested capacity K.
    """
    if capacity_k not in CAPACITY_K_OPTIONS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Unsupported capacity_k={capacity_k}. "
                f"Allowed values: {list(CAPACITY_K_OPTIONS)}"
            ),
        )

    try:
        return get_prioritization_data(
            capacity_k=capacity_k,
            display_limit=display_limit,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve prioritization data: {error}",
        ) from error
