"""Model Insights tab data access via FastAPI."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

from config.api_settings import get_api_settings
from services.api_client import ApiClientError, fetch_model_insights_data


DEFAULT_MODEL_INSIGHTS_LIMIT = 10


def _transform_global_importance(items: list[dict]) -> pd.DataFrame:
    """Map API global SHAP rows to the chart's DataFrame contract."""
    return pd.DataFrame(
        {
            "Feature": [item["feature"] for item in items],
            "Importance": [float(item["importance"]) for item in items],
        }
    )


def _transform_local_explanation(item: dict[str, Any]) -> dict[str, Any]:
    """Map the API local SHAP payload to the panel contract."""
    contributions = pd.DataFrame(
        {
            "Feature": [
                row["feature"] for row in item["contributions"]
            ],
            "Contribution": [
                float(row["contribution"])
                for row in item["contributions"]
            ],
        }
    )
    return {
        "flight_id": item["flight_id"],
        "base_probability": float(item["base_probability"]),
        "predicted_probability": float(item["predicted_probability"]),
        "contributions": contributions,
        "flight_date": item["flight_date"],
        "origin": item["origin"],
        "destination": item["destination"],
        "decision_threshold": float(item["decision_threshold"]),
        "output_scale": item["output_scale"],
    }


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_model_insights_payload(api_url: str, limit: int) -> dict:
    """Cache the Model Insights API response for five minutes."""
    return fetch_model_insights_data(limit=limit)


def get_model_insights_page_data(
    limit: int = DEFAULT_MODEL_INSIGHTS_LIMIT,
) -> Optional[dict[str, Any]]:
    """Return real global and local SHAP data, or None on API failure."""
    settings = get_api_settings()
    if not settings.is_model_insights_configured:
        st.error(
            "Model Insights API is not configured. Set "
            "STREAMLIT_API_BASE_URL and STREAMLIT_API_MODEL_INSIGHTS_PATH."
        )
        return None

    try:
        payload = _fetch_model_insights_payload(
            settings.model_insights_url,
            limit,
        )
    except ApiClientError as error:
        st.error(f"Unable to load Model Insights data from API: {error}")
        return None

    return {
        "global_importance": _transform_global_importance(
            payload["global_importance"]
        ),
        "local_explanation": _transform_local_explanation(
            payload["local_explanation"]
        ),
        "source_tables": payload["source_tables"],
    }
