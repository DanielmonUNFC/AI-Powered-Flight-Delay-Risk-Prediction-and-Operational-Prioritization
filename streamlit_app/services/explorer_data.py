"""Flight Explorer tab data access via FastAPI."""

from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from config.api_settings import get_api_settings
from services.api_client import ApiClientError, fetch_explorer_data


EXPLORER_DF_COLUMNS = [
    "Flight",
    "Carrier",
    "CarrierName",
    "CarrierLabel",
    "Origin",
    "OriginName",
    "OriginLabel",
    "Destination",
    "DestinationName",
    "DestinationLabel",
    "SchedDep",
    "DepTime",
    "DepartureWindow",
    "DelayProb",
    "RiskTier",
    "Status",
    "Month",
    "ShapMainDriver",
]


def _compact_airport_label(code: str, description: str | None) -> str:
    """Readable but compact airport label for dense tables."""
    if not description or description == code:
        return code

    airport_name = description.split(":", maxsplit=1)[-1].strip()
    if not airport_name:
        return code
    if len(airport_name) > 24:
        airport_name = f"{airport_name[:21]}..."
    return f"{code} · {airport_name}"


def _carrier_label(code: str, name: str | None) -> str:
    if not name or name == code:
        return code
    return f"{code} · {name}"


def _transform_flights(flights: list[dict]) -> pd.DataFrame:
    """Map API snake_case fields to the DataFrame shape used by the UI."""
    if not flights:
        return pd.DataFrame(columns=EXPLORER_DF_COLUMNS)

    carrier_names = [row.get("carrier_name") or row["carrier"] for row in flights]
    origin_names = [row.get("origin_name") or row["origin"] for row in flights]
    destination_names = [
        row.get("destination_name") or row["destination"] for row in flights
    ]

    return pd.DataFrame(
        {
            "Flight": [row["flight"] for row in flights],
            "Carrier": [row["carrier"] for row in flights],
            "CarrierName": carrier_names,
            "CarrierLabel": [
                _carrier_label(row["carrier"], row.get("carrier_name"))
                for row in flights
            ],
            "Origin": [row["origin"] for row in flights],
            "OriginName": origin_names,
            "OriginLabel": [
                _compact_airport_label(row["origin"], row.get("origin_name"))
                for row in flights
            ],
            "Destination": [row["destination"] for row in flights],
            "DestinationName": destination_names,
            "DestinationLabel": [
                _compact_airport_label(row["destination"], row.get("destination_name"))
                for row in flights
            ],
            "SchedDep": [row["sched_dep"] for row in flights],
            "DepTime": [row["dep_time"] for row in flights],
            "DepartureWindow": [row["departure_window"] for row in flights],
            "DelayProb": [float(row["delay_prob"]) for row in flights],
            "RiskTier": [row["risk_tier"] for row in flights],
            "Status": [row["status"] for row in flights],
            "Month": [row["month"] for row in flights],
            "ShapMainDriver": [row["shap_main_driver"] for row in flights],
        }
    )


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_explorer_payload(api_url: str, limit: int) -> dict:
    """Cache Explorer API response for 5 minutes."""
    return fetch_explorer_data(limit=limit)


def get_explorer_page_data() -> Optional[pd.DataFrame]:
    """Return Explorer tab data from FastAPI, or None when unavailable."""
    settings = get_api_settings()

    if not settings.is_explorer_configured:
        st.error(
            "Explorer API is not configured. Set STREAMLIT_API_BASE_URL and "
            "STREAMLIT_API_EXPLORER_PATH."
        )
        return None

    try:
        payload = _fetch_explorer_payload(
            settings.explorer_url,
            settings.explorer_limit,
        )
    except ApiClientError as error:
        st.error(f"Unable to load Explorer data from API: {error}")
        return None

    return _transform_flights(payload["flights"])
