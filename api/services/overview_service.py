from typing import Any
import time

from api.core.config import get_settings
from api.db.databricks import execute_query


settings = get_settings()

OVERVIEW_CACHE_TTL_SECONDS = 300
_overview_cache: dict[str, Any] = {"payload": None, "expires_at": 0.0}

OVERVIEW_SECTIONS = (
    "overview_kpi",
    "monthly_trend",
    "delay_cause",
)

OVERVIEW_KPI_METRICS = (
    "total_flights",
    "avg_delay_rate",
    "avg_arr_delay",
    "cancel_rate",
)

INSIGHT_CAUSES = (
    "Late Aircraft",
    "Carrier",
)


def _load_overview_rows() -> list[dict[str, Any]]:
    """Load all Overview sections from flight_dashboard in one query."""
    placeholders = ", ".join("?" * len(OVERVIEW_SECTIONS))
    query = f"""
        SELECT
            section,
            metric_name,
            metric_value,
            metric_text,
            dimension_1,
            sort_order
        FROM {settings.overview_table_full_name}
        WHERE section IN ({placeholders})
        ORDER BY section, sort_order
    """
    return execute_query(query, parameters=list(OVERVIEW_SECTIONS))


def _build_kpis(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build KPI array from overview_kpi rows."""
    kpi_rows = [row for row in rows if row["section"] == "overview_kpi"]
    kpis = [
        {
            "metric_name": row["metric_name"],
            "value": float(row["metric_value"]),
            "display": row["metric_text"],
            "sort_order": int(row["sort_order"]),
        }
        for row in kpi_rows
    ]

    existing_names = {item["metric_name"] for item in kpis}
    next_order = len(kpis) + 1

    for metric_name in OVERVIEW_KPI_METRICS:
        if metric_name not in existing_names:
            kpis.append(
                {
                    "metric_name": metric_name,
                    "value": 0.0,
                    "display": "0",
                    "sort_order": next_order,
                }
            )
            next_order += 1

    return sorted(kpis, key=lambda item: item["sort_order"])


def _build_monthly_trend(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build monthly trend array from monthly_trend rows."""
    trend_rows = [row for row in rows if row["section"] == "monthly_trend"]
    return [
        {
            "month": row["dimension_1"],
            "delay_rate": float(row["metric_value"]),
            "display": row["metric_text"],
            "sort_order": int(row["sort_order"]),
        }
        for row in trend_rows
    ]


def _build_delay_causes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build delay cause array from delay_cause rows."""
    cause_rows = [row for row in rows if row["section"] == "delay_cause"]
    return [
        {
            "cause": row["dimension_1"],
            "percentage": float(row["metric_value"]),
            "display": row["metric_text"],
            "sort_order": int(row["sort_order"]),
        }
        for row in cause_rows
    ]


def _build_operational_insight(
    delay_causes: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate the Key Operational Insight from delay cause shares."""
    lookup = {item["cause"]: item["percentage"] for item in delay_causes}

    combined_share = round(
        sum(lookup.get(cause, 0.0) for cause in INSIGHT_CAUSES),
        1,
    )

    text = (
        "Late aircraft propagation and carrier-related operational bottlenecks "
        f"account for {combined_share}% of total accumulated delay minutes "
        "across major US airport hubs in 2025."
    )

    return {
        "combined_late_aircraft_carrier_pct": combined_share,
        "text": text,
    }


def get_overview_data() -> dict[str, Any]:
    """
    Load the full Overview tab payload from flight_dashboard.

    Returns:
        JSON-ready dict with kpis, monthly_trend, delay_causes,
        and operational_insight arrays/objects.
    """
    now = time.time()
    cached_payload = _overview_cache["payload"]
    if cached_payload is not None and now < _overview_cache["expires_at"]:
        return cached_payload

    rows = _load_overview_rows()
    delay_causes = _build_delay_causes(rows)

    payload = {
        "kpis": _build_kpis(rows),
        "monthly_trend": _build_monthly_trend(rows),
        "delay_causes": delay_causes,
        "operational_insight": _build_operational_insight(delay_causes),
    }

    _overview_cache["payload"] = payload
    _overview_cache["expires_at"] = now + OVERVIEW_CACHE_TTL_SECONDS

    return payload


def warm_overview_cache() -> None:
    """Preload Overview data during API startup."""
    get_overview_data()