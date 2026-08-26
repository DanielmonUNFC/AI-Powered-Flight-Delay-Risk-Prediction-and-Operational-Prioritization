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
    model_insights_path: str
    prediction_path: str
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
    def is_model_insights_configured(self) -> bool:
        return bool(self.base_url and self.model_insights_path)

    @property
    def is_prediction_configured(self) -> bool:
        return bool(self.base_url and self.prediction_path)

    @property
    def overview_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.overview_path}"

    @property
    def explorer_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.explorer_path}"

    @property
    def prioritization_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.prioritization_path}"

    @property
    def model_insights_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.model_insights_path}"

    @property
    def prediction_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.prediction_path}"

    @property
    def prediction_options_url(self) -> str:
        return f"{self.prediction_url}/options"


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
        model_insights_path=os.getenv("STREAMLIT_API_MODEL_INSIGHTS_PATH", ""),
        prediction_path=os.getenv("STREAMLIT_API_PREDICTION_PATH", ""),
        timeout_seconds=int(timeout_raw),
        explorer_limit=int(limit_raw),
        prioritization_display_limit=int(prioritization_limit_raw),
    )
