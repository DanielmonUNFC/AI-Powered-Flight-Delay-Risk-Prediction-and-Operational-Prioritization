"""Runtime settings for Streamlit data access."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

import config.env_loader  # noqa: F401  — loads streamlit_app/.env


@dataclass(frozen=True)
class DataSettings:
    """Databricks SQL settings loaded from environment variables."""

    databricks_server_hostname: str
    databricks_http_path: str
    databricks_access_token: str
    databricks_catalog: str = "workspace"
    databricks_schema: str = "default"
    dashboard_table: str = "flight_dashboard"
    dashboard_explorer_table: str = "flight_dashboard_explorer"
    dashboard_insights_table: str = "flight_dashboard_insights"
    predictions_table: str = "flight_predictions"
    prioritization_results_table: str = "flight_prioritization_results"
    prioritization_evaluation_table: str = "flight_prioritization_evaluation"
    shap_direction_table: str = "flight_delay_shap_direction_effects"
    use_mock_data: bool = False

    @property
    def is_configured(self) -> bool:
        """Return True when Databricks credentials are available."""
        return bool(
            self.databricks_server_hostname
            and self.databricks_http_path
            and self.databricks_access_token
            and not self.use_mock_data
        )

    def table_name(self, table: str) -> str:
        """Return a fully qualified Unity Catalog table name."""
        return f"{self.databricks_catalog}.{self.databricks_schema}.{table}"


@lru_cache
def get_data_settings() -> DataSettings:
    """Load data-access settings once per Streamlit session process."""
    use_mock = os.getenv("STREAMLIT_USE_MOCK_DATA", "").lower() in {
        "1",
        "true",
        "yes",
    }
    return DataSettings(
        databricks_server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME", ""),
        databricks_http_path=os.getenv("DATABRICKS_HTTP_PATH", ""),
        databricks_access_token=os.getenv("DATABRICKS_ACCESS_TOKEN", ""),
        databricks_catalog=os.getenv("DATABRICKS_CATALOG", "workspace"),
        databricks_schema=os.getenv("DATABRICKS_SCHEMA", "default"),
        dashboard_table=os.getenv("DATABRICKS_DASHBOARD_TABLE", "flight_dashboard"),
        dashboard_explorer_table=os.getenv(
            "DATABRICKS_DASHBOARD_EXPLORER_TABLE",
            "flight_dashboard_explorer",
        ),
        dashboard_insights_table=os.getenv(
            "DATABRICKS_DASHBOARD_INSIGHTS_TABLE",
            "flight_dashboard_insights",
        ),
        predictions_table=os.getenv(
            "DATABRICKS_PREDICTIONS_TABLE",
            "flight_predictions",
        ),
        prioritization_results_table=os.getenv(
            "DATABRICKS_PRIORITIZATION_RESULTS_TABLE",
            "flight_prioritization_results",
        ),
        prioritization_evaluation_table=os.getenv(
            "DATABRICKS_PRIORITIZATION_EVALUATION_TABLE",
            "flight_prioritization_evaluation",
        ),
        shap_direction_table=os.getenv(
            "DATABRICKS_SHAP_DIRECTION_TABLE",
            "flight_delay_shap_direction_effects",
        ),
        use_mock_data=use_mock,
    )
