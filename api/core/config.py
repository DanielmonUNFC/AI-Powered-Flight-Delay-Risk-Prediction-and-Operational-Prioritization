from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration.

    Values are loaded from api/.env during development.
    """

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = "Flight Delay Risk API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # ------------------------------------------------------------------
    # Databricks Connection
    # ------------------------------------------------------------------

    databricks_server_hostname: str
    databricks_http_path: str
    databricks_access_token: str

    # ------------------------------------------------------------------
    # Catalog Configuration
    # ------------------------------------------------------------------

    databricks_catalog: str = "workspace"
    databricks_schema: str = "default"

    # ------------------------------------------------------------------
    # Tables used by API endpoints
    # ------------------------------------------------------------------

    databricks_overview_table: str = "flight_dashboard"
    databricks_explorer_table: str = "flight_dashboard_explorer"
    databricks_airlines_lookup_table: str = "airlines_lookup"
    databricks_airports_lookup_table: str = "airports_lookup"
    databricks_prioritization_results_table: str = "flight_prioritization_results"
    databricks_prioritization_evaluation_table: str = (
        "flight_prioritization_evaluation"
    )

    # ------------------------------------------------------------------
    # Tables reserved for upcoming endpoints
    # ------------------------------------------------------------------

    databricks_clean_table: str = "flights_clean"
    databricks_predictions_table: str = "flight_predictions"
    databricks_insights_table: str = "flight_dashboard_insights"

    model_config = SettingsConfigDict(
        env_file="api/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def _qualified_table(self, table_name: str) -> str:
        return (
            f"{self.databricks_catalog}."
            f"{self.databricks_schema}."
            f"{table_name}"
        )

    @property
    def overview_table_full_name(self) -> str:
        """Fully qualified table for GET /api/v1/overview."""
        return self._qualified_table(self.databricks_overview_table)

    @property
    def explorer_table_full_name(self) -> str:
        """Fully qualified table for GET /api/v1/explorer."""
        return self._qualified_table(self.databricks_explorer_table)

    @property
    def airlines_lookup_table_full_name(self) -> str:
        """Fully qualified airlines lookup table."""
        return self._qualified_table(self.databricks_airlines_lookup_table)

    @property
    def airports_lookup_table_full_name(self) -> str:
        """Fully qualified airports lookup table."""
        return self._qualified_table(self.databricks_airports_lookup_table)

    @property
    def clean_table_full_name(self) -> str:
        """Fully qualified flights_clean table (health check)."""
        return self._qualified_table(self.databricks_clean_table)

    @property
    def prioritization_results_table_full_name(self) -> str:
        """Fully qualified table for GET /api/v1/prioritization."""
        return self._qualified_table(self.databricks_prioritization_results_table)

    @property
    def prioritization_evaluation_table_full_name(self) -> str:
        """Fully qualified prioritization evaluation table."""
        return self._qualified_table(self.databricks_prioritization_evaluation_table)


@lru_cache
def get_settings() -> Settings:
    """Load application settings once and cache them."""
    return Settings()
