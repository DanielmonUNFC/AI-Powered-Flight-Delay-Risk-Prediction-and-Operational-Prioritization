"""HTTP client for the capstone FastAPI backend."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from config.api_settings import get_api_settings


class ApiClientError(RuntimeError):
    """Raised when the FastAPI request fails."""


def _request_json(
    url: str,
    service_name: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute one JSON request with consistent API error handling."""
    settings = get_api_settings()
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urlopen(request, timeout=settings.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise ApiClientError(
            f"{service_name} API returned HTTP {error.code}: {body}"
        ) from error
    except URLError as error:
        raise ApiClientError(
            f"Unable to reach {service_name} API at {url}: {error}"
        ) from error


def _fetch_json(url: str, service_name: str) -> dict[str, Any]:
    """Execute one JSON GET request."""
    return _request_json(url, service_name)


def fetch_overview_data() -> dict[str, Any]:
    """Fetch the Overview tab payload from FastAPI."""
    settings = get_api_settings()

    if not settings.is_configured:
        raise ApiClientError(
            "Overview API is not configured. Set STREAMLIT_API_BASE_URL and "
            "STREAMLIT_API_OVERVIEW_PATH."
        )

    return _fetch_json(settings.overview_url, "Overview")


def fetch_explorer_data(limit: int = 1000, **filters: Any) -> dict[str, Any]:
    """Fetch the Flight Explorer tab payload from FastAPI."""
    settings = get_api_settings()

    if not settings.is_explorer_configured:
        raise ApiClientError(
            "Explorer API is not configured. Set STREAMLIT_API_BASE_URL and "
            "STREAMLIT_API_EXPLORER_PATH."
        )

    query_values = {"limit": int(limit)}
    query_values.update(
        {key: value for key, value in filters.items() if value is not None}
    )
    url = f"{settings.explorer_url}?{urlencode(query_values)}"
    return _fetch_json(url, "Explorer")


def fetch_explorer_options() -> dict[str, Any]:
    """Fetch complete filter choices for Flight Explorer."""
    settings = get_api_settings()
    return _fetch_json(f"{settings.explorer_url}/options", "Explorer")


def fetch_prioritization_data(
    capacity_k: int = 25,
    *,
    display_limit: int = 500,
) -> dict[str, Any]:
    """Fetch the Operational Prioritization tab payload from FastAPI."""
    settings = get_api_settings()

    if not settings.is_prioritization_configured:
        raise ApiClientError(
            "Prioritization API is not configured. Set STREAMLIT_API_BASE_URL and "
            "STREAMLIT_API_PRIORITIZATION_PATH."
        )

    query = urlencode(
        {
            "capacity_k": int(capacity_k),
            "display_limit": int(display_limit),
        }
    )
    return _fetch_json(f"{settings.prioritization_url}?{query}", "Prioritization")


def fetch_model_insights_data(limit: int = 10) -> dict[str, Any]:
    """Fetch global and local SHAP explanations from FastAPI."""
    settings = get_api_settings()
    if not settings.is_model_insights_configured:
        raise ApiClientError(
            "Model Insights API is not configured. Set STREAMLIT_API_BASE_URL "
            "and STREAMLIT_API_MODEL_INSIGHTS_PATH."
        )

    url = f"{settings.model_insights_url}?{urlencode({'limit': int(limit)})}"
    return _fetch_json(url, "Model Insights")


def fetch_prediction_options() -> dict[str, Any]:
    """Fetch real airline and airport options for the prediction form."""
    settings = get_api_settings()
    if not settings.is_prediction_configured:
        raise ApiClientError(
            "Prediction API is not configured. Set STREAMLIT_API_BASE_URL "
            "and STREAMLIT_API_PREDICTION_PATH."
        )
    return _fetch_json(settings.prediction_options_url, "Prediction")


def create_prediction(payload: dict[str, Any]) -> dict[str, Any]:
    """Request one live delay-risk prediction from FastAPI."""
    settings = get_api_settings()
    if not settings.is_prediction_configured:
        raise ApiClientError(
            "Prediction API is not configured. Set STREAMLIT_API_BASE_URL "
            "and STREAMLIT_API_PREDICTION_PATH."
        )
    return _request_json(
        settings.prediction_url,
        "Prediction",
        method="POST",
        payload=payload,
    )
