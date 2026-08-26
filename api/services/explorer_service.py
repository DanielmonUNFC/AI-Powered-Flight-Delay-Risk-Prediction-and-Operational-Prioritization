from typing import Any
import time

from api.core.config import get_settings
from api.db.databricks import execute_queries


settings = get_settings()

DEFAULT_EXPLORER_LIMIT = 5000
MAX_EXPLORER_LIMIT = 10000
WARMUP_EXPLORER_LIMIT = 1000
EXPLORER_CACHE_TTL_SECONDS = 300

_explorer_caches: dict[tuple[Any, ...], dict[str, Any]] = {}


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


def _build_where(filters: dict[str, Any]) -> tuple[str, list[Any]]:
    clauses, parameters = [], []
    for key, column in {
        "month": "e.Month", "risk_tier": "e.RiskTier",
        "departure_window": "e.DepartureWindow", "origin": "e.Origin",
        "destination": "e.Destination", "carrier": "e.Carrier",
    }.items():
        value = filters.get(key)
        if value not in (None, "", "All"):
            clauses.append(f"{column} = ?")
            parameters.append(value)
    if filters.get("outcome") in {"Predicted Delayed", "Predicted On-Time"}:
        clauses.append("e.predicted_delay = ?")
        parameters.append(1 if filters["outcome"] == "Predicted Delayed" else 0)
    if filters.get("minimum_risk") is not None:
        clauses.append("e.DelayProb >= ?")
        parameters.append(float(filters["minimum_risk"]))
    return ("WHERE " + " AND ".join(clauses) if clauses else "", parameters)


def _build_enriched_cte(where_sql: str) -> str:
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
                CASE
                    WHEN e.predicted_delay = 1 THEN 'Predicted Delayed'
                    ELSE 'Predicted On-Time'
                END AS Status,
                e.Month,
                e.ShapMainDriver
            FROM {settings.explorer_table_full_name} AS e
            LEFT JOIN {settings.airlines_lookup_table_full_name} AS al
                ON e.Carrier = al.Code
            LEFT JOIN {settings.airports_lookup_table_full_name} AS ao
                ON e.Origin = ao.Code
            LEFT JOIN {settings.airports_lookup_table_full_name} AS ad
                ON e.Destination = ad.Code
            {where_sql}
        )
    """


def get_explorer_data(limit: int = DEFAULT_EXPLORER_LIMIT, **filters: Any) -> dict[str, Any]:
    """
    Load scored flights for the Explorer tab from flight_dashboard_explorer.

    Returns:
        JSON-ready dict with flights array and metadata.
    """
    safe_limit = _normalize_limit(limit)
    now = time.time()

    cache_key = (safe_limit, *sorted(filters.items()))
    cached_entry = _explorer_caches.get(cache_key)
    if cached_entry is not None and now < cached_entry["expires_at"]:
        return cached_entry["payload"]

    where_sql, parameters = _build_where(filters)
    cte = _build_enriched_cte(where_sql)
    if filters.get("sort_by") == "Departure Time":
        order_clause = "DepTime ASC, Flight ASC"
    elif filters.get("sort_by") == "Lowest Delay Risk":
        order_clause = "DelayProb ASC, Flight ASC"
    else:
        order_clause = "DelayProb DESC, Flight ASC"
    statements = [
        (cte + f" SELECT * FROM enriched ORDER BY {order_clause} LIMIT {safe_limit}", parameters),
        (cte + " SELECT Carrier, CarrierName, COUNT(*) AS Flights, AVG(DelayProb) AS MeanDelayProb FROM enriched GROUP BY Carrier, CarrierName ORDER BY MeanDelayProb DESC", parameters),
        (cte + " SELECT Origin, Destination, COUNT(*) AS Flights, MAX(DelayProb) AS PeakDelayProb FROM enriched GROUP BY Origin, Destination ORDER BY PeakDelayProb DESC LIMIT 5", parameters),
        (cte + " SELECT COUNT(*) AS TotalFlights FROM enriched", parameters),
    ]
    rows, airline_rows, route_rows, count_rows = execute_queries(statements)
    flights = [_map_flight_row(row) for row in rows]

    payload = {
        "flights": flights,
        "count": len(flights),
        "total_count": int(count_rows[0]["TotalFlights"]),
        "airline_summary": [
            {**row, "MeanDelayProb": float(row["MeanDelayProb"])}
            for row in airline_rows
        ],
        "route_summary": [
            {**row, "PeakDelayProb": float(row["PeakDelayProb"])}
            for row in route_rows
        ],
        "limit": safe_limit,
        "order_by": order_clause,
        "source_table": settings.explorer_table_full_name,
    }

    _explorer_caches[cache_key] = {
        "payload": payload,
        "expires_at": now + EXPLORER_CACHE_TTL_SECONDS,
    }

    return payload


def get_explorer_options() -> dict[str, Any]:
    """Return complete filter choices without deriving them from a sample."""
    queries = [
        f"SELECT DISTINCT Month FROM {settings.explorer_table_full_name} ORDER BY Month",
        f"SELECT DISTINCT RiskTier FROM {settings.explorer_table_full_name} ORDER BY RiskTier",
        f"SELECT DISTINCT DepartureWindow FROM {settings.explorer_table_full_name} ORDER BY DepartureWindow",
        f"SELECT DISTINCT e.Carrier AS Code, COALESCE(l.Description,e.Carrier) AS Name FROM {settings.explorer_table_full_name} e LEFT JOIN {settings.airlines_lookup_table_full_name} l ON e.Carrier=l.Code ORDER BY Name",
        f"SELECT DISTINCT e.Origin AS Code, COALESCE(l.Description,e.Origin) AS Name FROM {settings.explorer_table_full_name} e LEFT JOIN {settings.airports_lookup_table_full_name} l ON e.Origin=l.Code ORDER BY Name",
        f"SELECT DISTINCT e.Destination AS Code, COALESCE(l.Description,e.Destination) AS Name FROM {settings.explorer_table_full_name} e LEFT JOIN {settings.airports_lookup_table_full_name} l ON e.Destination=l.Code ORDER BY Name",
    ]
    rows = execute_queries([(query, None) for query in queries])
    return {"months": [row["Month"] for row in rows[0]],
            "risk_tiers": [row["RiskTier"] for row in rows[1]],
            "departure_windows": [row["DepartureWindow"] for row in rows[2]],
            "carriers": rows[3], "origins": rows[4], "destinations": rows[5]}


def warm_explorer_cache(limit: int = WARMUP_EXPLORER_LIMIT) -> None:
    """Preload Explorer data during API startup."""
    get_explorer_data(limit=limit)
