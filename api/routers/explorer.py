from typing import Any

from fastapi import APIRouter, HTTPException, Query

from api.services.explorer_service import (
    DEFAULT_EXPLORER_LIMIT,
    MAX_EXPLORER_LIMIT,
    get_explorer_data,
)


router = APIRouter(
    prefix="/explorer",
    tags=["Explorer"],
)


@router.get("")
def explorer_page_data(
    limit: int = Query(
        default=DEFAULT_EXPLORER_LIMIT,
        ge=1,
        le=MAX_EXPLORER_LIMIT,
        description="Maximum number of scored flights to return.",
    ),
) -> dict[str, Any]:
    """
    Return the Flight Explorer tab payload from flight_dashboard_explorer.

    Results are ordered by month and predicted delay risk. For limits below the
    full validation set (~1.16M rows), the service balances rows across months
    instead of returning an arbitrary slice.
    """
    try:
        return get_explorer_data(limit=limit)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve explorer data: {error}",
        ) from error
