from typing import Any
import time

from api.core.config import get_settings
from api.db.databricks import execute_query


settings = get_settings()

DEFAULT_EXPLORER_LIMIT = 5000
MAX_EXPLORER_LIMIT = 10000
WARMUP_EXPLORER_LIMIT = 1000
EXPLORER_CACHE_TTL_SECONDS = 300

# Cap rows returned per Month label so Sep/Oct both appear in limited payloads.
EXPLORER_MAX_ROWS_PER_MONTH = 500

_explorer_caches: dict[int, dict[str, Any]] = {}


def _normalize_limit(limit: int) -> int:
    """Clamp explorer page size to a safe range."""
    if limit < 1:
        return DEFAULT_EXPLORER_LIMIT
    return min(limit, MAX_EXPLORER_LIMIT)


def _map_flight_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map a Databricks explorer row to API JSON field names."""
    return {
        "flight": row["Flight"],
        "carrier": row["Carrier"],
        "carrier_name": row["CarrierName"],
        "origin": row["Origin"],
        "origin_name": row["OriginName"],
        "destination": row["Destination"],
        "destination_name": row["DestinationName"],
        "sched_dep": row["SchedDep"],
        "dep_time": row["DepTime"],
        "departure_window": row["DepartureWindow"],
        "delay_prob": float(row["DelayProb"]),
        "risk_tier": row["RiskTier"],
        "status": row["Status"],
        "month": row["Month"],
        "shap_main_driver": row["ShapMainDriver"],
    }


def _rows_per_month(limit: int) -> int:
    """Balance limited explorer payloads across month labels when possible."""
    return max(1, min(EXPLORER_MAX_ROWS_PER_MONTH, (limit + 1) // 2))


def _build_explorer_query(safe_limit: int) -> str:
    """Build explorer query with lookup joins and deterministic ordering."""
    per_month = _rows_per_month(safe_limit)
    return f"""
        WITH enriched AS (
            SELECT
                e.Flight,
                e.Carrier,
                COALESCE(al.Description, e.Carrier) AS CarrierName,
                e.Origin,
                COALESCE(ao.Description, e.Origin) AS OriginName,
                e.Destination,
                COALESCE(ad.Description, e.Destination) AS DestinationName,
                e.SchedDep,
                e.DepTime,
                e.DepartureWindow,
                e.DelayProb,
                e.RiskTier,
                e.Status,
                e.Month,
                e.ShapMainDriver
            FROM {settings.explorer_table_full_name} AS e
            LEFT JOIN {settings.airlines_lookup_table_full_name} AS al
                ON e.Carrier = al.Code
            LEFT JOIN {settings.airports_lookup_table_full_name} AS ao
                ON e.Origin = ao.Code
            LEFT JOIN {settings.airports_lookup_table_full_name} AS ad
                ON e.Destination = ad.Code
        ),
        ranked AS (
            SELECT
                enriched.*,
                ROW_NUMBER() OVER (
                    PARTITION BY Month
                    ORDER BY DelayProb DESC, Flight ASC
                ) AS month_rank
            FROM enriched
        )
        SELECT
            Flight,
            Carrier,
            CarrierName,
            Origin,
            OriginName,
            Destination,
            DestinationName,
            SchedDep,
            DepTime,
            DepartureWindow,
            DelayProb,
            RiskTier,
            Status,
            Month,
            ShapMainDriver
        FROM ranked
        WHERE month_rank <= {per_month}
        ORDER BY Month ASC, DelayProb DESC, Flight ASC
        LIMIT {safe_limit}
    """


def get_explorer_data(limit: int = DEFAULT_EXPLORER_LIMIT) -> dict[str, Any]:
    """
    Load scored flights for the Explorer tab from flight_dashboard_explorer.

    Returns:
        JSON-ready dict with flights array and metadata.
    """
    safe_limit = _normalize_limit(limit)
    now = time.time()

    cached_entry = _explorer_caches.get(safe_limit)
    if cached_entry is not None and now < cached_entry["expires_at"]:
        return cached_entry["payload"]

    rows = execute_query(_build_explorer_query(safe_limit))
    flights = [_map_flight_row(row) for row in rows]

    payload = {
        "flights": flights,
        "count": len(flights),
        "limit": safe_limit,
        "order_by": "Month ASC, DelayProb DESC (balanced up to per-month cap)",
        "source_table": settings.explorer_table_full_name,
    }

    _explorer_caches[safe_limit] = {
        "payload": payload,
        "expires_at": now + EXPLORER_CACHE_TTL_SECONDS,
    }

    return payload


def warm_explorer_cache(limit: int = WARMUP_EXPLORER_LIMIT) -> None:
    """Preload Explorer data during API startup."""
    get_explorer_data(limit=limit)
