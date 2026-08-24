"""Operational Prioritization tab data access via FastAPI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import streamlit as st

from config.api_settings import get_api_settings
from config.prioritization import CAPACITY_K_OPTIONS, DEFAULT_CAPACITY_K
from services.api_client import ApiClientError, fetch_prioritization_data


PRIORITIZATION_DF_COLUMNS = [
    "Priority",
    "FlightDate",
    "Flight",
    "Airline",
    "Origin",
    "Destination",
    "SchedDep",
    "DelayProb",
    "PriorityScore",
    "RiskLevel",
    "Recommendation",
    "ShapMainDriver",
    "Selected",
]


@dataclass(frozen=True)
class PrioritizationSummary:
    """Operational summary metrics for the prioritization tab."""

    flights_in_queue: int
    critical_risk: int
    high_risk: int
    flights_selected: int
    capacity_k: int


@dataclass(frozen=True)
class PrioritizationTableMeta:
    """Metadata describing how many selected flights are shown in the table."""

    displayed_count: int
    selected_count: int
    queue_size: int
    display_limit: int


def normalize_capacity_k(capacity_k: int) -> int:
    """Return a supported operational capacity value."""
    if capacity_k in CAPACITY_K_OPTIONS:
        return capacity_k
    return DEFAULT_CAPACITY_K


def _transform_ranking(flights: list[dict]) -> pd.DataFrame:
    """Map API snake_case fields to the DataFrame shape used by the UI."""
    if not flights:
        return pd.DataFrame(columns=PRIORITIZATION_DF_COLUMNS)

    return pd.DataFrame(
        {
            "Priority": [int(row["priority"]) for row in flights],
            "FlightDate": [row.get("flight_date", "") for row in flights],
            "Flight": [row["flight"] for row in flights],
            "Airline": [row["airline"] for row in flights],
            "Origin": [row["origin"] for row in flights],
            "Destination": [row["destination"] for row in flights],
            "SchedDep": [row["sched_dep"] for row in flights],
            "DelayProb": [float(row["delay_prob"]) for row in flights],
            "PriorityScore": [int(row["priority_score"]) for row in flights],
            "RiskLevel": [row["risk_level"] for row in flights],
            "Recommendation": [row["recommendation"] for row in flights],
            "ShapMainDriver": [row["shap_main_driver"] for row in flights],
            "Selected": [bool(row["selected"]) for row in flights],
        }
    )


def _transform_summary(summary: dict, capacity_k: int) -> PrioritizationSummary:
    return PrioritizationSummary(
        flights_in_queue=int(summary["flights_in_queue"]),
        critical_risk=int(summary["critical_risk"]),
        high_risk=int(summary["high_risk"]),
        flights_selected=int(summary["flights_selected"]),
        capacity_k=normalize_capacity_k(capacity_k),
    )


def _transform_table_meta(payload: dict) -> PrioritizationTableMeta:
    displayed_count = int(payload.get("count") or len(payload.get("flights", [])))
    selected_count = int(
        payload.get("total_count") or payload["summary"]["flights_selected"]
    )
    queue_size = int(
        payload.get("queue_size") or payload["summary"]["flights_in_queue"]
    )
    display_limit = int(payload.get("display_limit") or displayed_count)
    return PrioritizationTableMeta(
        displayed_count=displayed_count,
        selected_count=selected_count,
        queue_size=queue_size,
        display_limit=display_limit,
    )


def format_summary_values(summary: PrioritizationSummary) -> dict[str, str]:
    """Format summary metrics for UI rendering."""
    return {
        "flights_in_queue": f"{summary.flights_in_queue:,}",
        "critical_risk": f"{summary.critical_risk:,}",
        "high_risk": f"{summary.high_risk:,}",
        "flights_selected": f"{summary.flights_selected:,}",
        "capacity_k": str(summary.capacity_k),
    }


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_prioritization_payload(
    api_url: str,
    capacity_k: int,
    display_limit: int,
) -> dict:
    """Cache Prioritization API response for 5 minutes."""
    return fetch_prioritization_data(
        capacity_k=capacity_k,
        display_limit=display_limit,
    )


def get_prioritization_page_data(
    capacity_k: int = DEFAULT_CAPACITY_K,
) -> Optional[tuple[pd.DataFrame, PrioritizationSummary, PrioritizationTableMeta]]:
    """Return prioritization ranking, summary, and table metadata from FastAPI."""
    settings = get_api_settings()
    safe_capacity_k = normalize_capacity_k(capacity_k)

    if not settings.is_prioritization_configured:
        st.error(
            "Prioritization API is not configured. Set STREAMLIT_API_BASE_URL and "
            "STREAMLIT_API_PRIORITIZATION_PATH."
        )
        return None

    try:
        payload = _fetch_prioritization_payload(
            settings.prioritization_url,
            safe_capacity_k,
            settings.prioritization_display_limit,
        )
    except ApiClientError as error:
        st.error(f"Unable to load Prioritization data from API: {error}")
        return None

    ranking = _transform_ranking(payload["flights"])
    summary = _transform_summary(payload["summary"], safe_capacity_k)
    table_meta = _transform_table_meta(payload)
    return ranking, summary, table_meta
