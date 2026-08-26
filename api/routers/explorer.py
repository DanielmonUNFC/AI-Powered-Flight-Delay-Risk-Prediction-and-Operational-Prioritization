from typing import Any

from fastapi import APIRouter, HTTPException, Query

from api.services.explorer_service import (
    DEFAULT_EXPLORER_LIMIT,
    MAX_EXPLORER_LIMIT,
    get_explorer_data,
    get_explorer_options,
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
    ), month: int | None = None, outcome: str | None = None,
    risk_tier: str | None = None, departure_window: str | None = None,
    minimum_risk: float | None = Query(default=None, ge=0, le=1),
    origin: str | None = None, destination: str | None = None,
    carrier: str | None = None, sort_by: str | None = None,
) -> dict[str, Any]:
    """
    Return the Flight Explorer tab payload from flight_dashboard_explorer.

    Results are ordered by month and predicted delay risk. For limits below the
    full validation set (~1.16M rows), the service balances rows across months
    instead of returning an arbitrary slice.
    """
    try:
        return get_explorer_data(limit=limit, month=month, outcome=outcome,
            risk_tier=risk_tier, departure_window=departure_window,
            minimum_risk=minimum_risk, origin=origin, destination=destination,
            carrier=carrier, sort_by=sort_by)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve explorer data: {error}",
        ) from error


@router.get("/options")
def explorer_options() -> dict[str, Any]:
    """Return complete Explorer filter choices."""
    try:
        return get_explorer_options()
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve explorer options: {error}") from error
