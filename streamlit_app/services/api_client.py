"""HTTP client for the capstone FastAPI backend."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.api_settings import get_api_settings


class ApiClientError(RuntimeError):
    """Raised when the FastAPI request fails."""


def fetch_overview_data() -> dict[str, Any]:
    """Fetch the Overview tab payload from FastAPI."""
    settings = get_api_settings()

    if not settings.is_configured:
        raise ApiClientError(
            "Overview API is not configured. Set STREAMLIT_API_BASE_URL and "
            "STREAMLIT_API_OVERVIEW_PATH."
        )

    request = Request(
        settings.overview_url,
        headers={"Accept": "application/json"},
        method="GET",
    )

    try:
        with urlopen(request, timeout=settings.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)

    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise ApiClientError(
            f"Overview API returned HTTP {error.code}: {body}"
        ) from error

    except URLError as error:
        raise ApiClientError(
            f"Unable to reach Overview API at {settings.overview_url}: {error}"
        ) from error


def fetch_explorer_data(limit: int = 5000) -> dict[str, Any]:
    """Fetch the Flight Explorer tab payload from FastAPI."""
    settings = get_api_settings()

    if not settings.is_explorer_configured:
        raise ApiClientError(
            "Explorer API is not configured. Set STREAMLIT_API_BASE_URL and "
            "STREAMLIT_API_EXPLORER_PATH."
        )

    url = f"{settings.explorer_url}?limit={limit}"
    request = Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )

    try:
        with urlopen(request, timeout=settings.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)

    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise ApiClientError(
            f"Explorer API returned HTTP {error.code}: {body}"
        ) from error

    except URLError as error:
        raise ApiClientError(
            f"Unable to reach Explorer API at {url}: {error}"
        ) from error


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

    url = (
        f"{settings.prioritization_url}"
        f"?capacity_k={int(capacity_k)}&display_limit={int(display_limit)}"
    )
    request = Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )

    try:
        with urlopen(request, timeout=settings.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)

    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise ApiClientError(
            f"Prioritization API returned HTTP {error.code}: {body}"
        ) from error

    except URLError as error:
        raise ApiClientError(
            f"Unable to reach Prioritization API at {url}: {error}"
        ) from error