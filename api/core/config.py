from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration.

    Values are loaded from the local .env file during development.
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
    # Tables
    # ------------------------------------------------------------------

    databricks_raw_table: str = "flights_raw"
    databricks_clean_table: str = "flights_clean"
    databricks_features_table: str = "flights_features"

    model_config = SettingsConfigDict(
        env_file="api/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def clean_table_full_name(self) -> str:
        """
        Returns the fully qualified clean table name.
        """
        return (
            f"{self.databricks_catalog}."
            f"{self.databricks_schema}."
            f"{self.databricks_clean_table}"
        )


@lru_cache
def get_settings() -> Settings:
    """
    Loads the application settings once and caches them.
    """
    return Settings()