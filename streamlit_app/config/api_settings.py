"""Runtime settings for Streamlit → FastAPI communication."""

from __future__ import annotations

import os
from dataclasses import dataclass

import config.env_loader  # noqa: F401  — loads streamlit_app/.env


DEFAULT_PRIORITIZATION_DISPLAY_LIMIT = 500


@dataclass(frozen=True)
class ApiSettings:
    """FastAPI connection settings loaded from environment variables."""

    base_url: str
    overview_path: str
    explorer_path: str
    prioritization_path: str
    timeout_seconds: int
    explorer_limit: int
    prioritization_display_limit: int

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.overview_path)

    @property
    def is_explorer_configured(self) -> bool:
        return bool(self.base_url and self.explorer_path)

    @property
    def is_prioritization_configured(self) -> bool:
        return bool(self.base_url and self.prioritization_path)

    @property
    def overview_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.overview_path}"

    @property
    def explorer_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.explorer_path}"

    @property
    def prioritization_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.prioritization_path}"


def get_api_settings() -> ApiSettings:
    timeout_raw = os.getenv("STREAMLIT_API_TIMEOUT_SECONDS", "30")
    limit_raw = os.getenv("STREAMLIT_API_EXPLORER_LIMIT", "1000")
    prioritization_limit_raw = os.getenv(
        "STREAMLIT_API_PRIORITIZATION_LIMIT",
        str(DEFAULT_PRIORITIZATION_DISPLAY_LIMIT),
    )
    return ApiSettings(
        base_url=os.getenv("STREAMLIT_API_BASE_URL", ""),
        overview_path=os.getenv("STREAMLIT_API_OVERVIEW_PATH", ""),
        explorer_path=os.getenv("STREAMLIT_API_EXPLORER_PATH", ""),
        prioritization_path=os.getenv("STREAMLIT_API_PRIORITIZATION_PATH", ""),
        timeout_seconds=int(timeout_raw),
        explorer_limit=int(limit_raw),
        prioritization_display_limit=int(prioritization_limit_raw),
    )
