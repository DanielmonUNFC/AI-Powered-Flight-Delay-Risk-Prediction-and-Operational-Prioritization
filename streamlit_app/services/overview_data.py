"""Overview tab data access via FastAPI."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from config.api_settings import get_api_settings
from services.api_client import ApiClientError, fetch_overview_data


def _format_count(value: float) -> str:
    return f"{int(value):,}"


def _transform_kpis(kpi_items: list[dict]) -> dict:
    """Convert API KPI array into the shape expected by overview.py."""
    lookup = {item["metric_name"]: item for item in kpi_items}

    return {
        "total_flights": _format_count(lookup["total_flights"]["value"]),
        "avg_delay_rate": f"{lookup['avg_delay_rate']['value']:.1f}%",
        "avg_arr_delay": f"{lookup['avg_arr_delay']['value']:.1f} min",
        "cancellation_rate": f"{lookup['cancel_rate']['value']:.2f}%",
    }


def _transform_monthly_trend(items: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Month": [item["month"] for item in items],
            "DelayRate": [float(item["delay_rate"]) for item in items],
        }
    )


def _transform_delay_causes(items: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Cause": [item["cause"] for item in items],
            "Percentage": [float(item["percentage"]) for item in items],
        }
    )


def _transform_operational_insight(insight: dict) -> str:
    """Use insight text from API; only add HTML bold for the percentage."""
    text = insight["text"]
    pct = insight["combined_late_aircraft_carrier_pct"]

    return text.replace(f"{pct}%", f"<b>{pct}%</b>", 1)


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_overview_payload(api_url: str) -> dict:
    """Cache Overview API response for 5 minutes."""
    return fetch_overview_data()


def get_overview_page_data() -> dict[str, Any] | None:
    """Return Overview tab data from FastAPI, or None when unavailable."""
    settings = get_api_settings()

    if not settings.is_configured:
        st.error("Overview API is not configured. Set STREAMLIT_API_BASE_URL.")
        return None

    try:
        payload = _fetch_overview_payload(settings.overview_url)
    except ApiClientError as error:
        st.error(f"Unable to load Overview data from API: {error}")
        return None

    return {
        "kpis": _transform_kpis(payload["kpis"]),
        "monthly_trend": _transform_monthly_trend(payload["monthly_trend"]),
        "delay_causes": _transform_delay_causes(payload["delay_causes"]),
        "insight_html": _transform_operational_insight(payload["operational_insight"]),
    }