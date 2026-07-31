"""Databricks-backed data access for the Streamlit dashboard."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import pandas as pd

from config.data_settings import get_data_settings


@contextmanager
def _get_connection() -> Iterator[Any]:
    """Open a Databricks SQL connection."""
    settings = get_data_settings()
    from databricks import sql

    connection = sql.connect(
        server_hostname=settings.databricks_server_hostname,
        http_path=settings.databricks_http_path,
        access_token=settings.databricks_access_token,
    )
    try:
        yield connection
    finally:
        connection.close()


def databricks_configured() -> bool:
    """Return True when live Databricks data can be queried."""
    return get_data_settings().is_configured


def load_dashboard_section(section: str) -> pd.DataFrame:
    """Load dashboard records for a specific section."""
    allowed_sections = {
        "overview_kpi",
        "monthly_trend",
        "delay_cause",
        "research_validation",
        "model_metric",
    }
    if section not in allowed_sections:
        raise ValueError(f"Unsupported dashboard section: {section}")

    settings = get_data_settings()
    table_name = settings.table_name(settings.dashboard_table)
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE section = ?
        ORDER BY sort_order
    """
    return query_dataframe(query, parameters=[section])


def query_dataframe(query: str, parameters: list[Any] | None = None) -> pd.DataFrame:
    """Execute a SQL query and return a pandas DataFrame."""
    with _get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, parameters or [])
            if cursor.description is None:
                return pd.DataFrame()
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def load_explorer_data(limit: int = 5000) -> pd.DataFrame:
    """Load the explorer dataset prepared in notebook 11."""
    settings = get_data_settings()
    table_name = settings.table_name(settings.dashboard_explorer_table)
    query = f"""
        SELECT *
        FROM {table_name}
        LIMIT {int(limit)}
    """
    return query_dataframe(query)


def load_global_feature_importance() -> pd.DataFrame:
    """Load SHAP global importance for the Model Insights tab."""
    settings = get_data_settings()
    table_name = settings.table_name(settings.dashboard_insights_table)
    query = f"""
        SELECT feature AS Feature, importance AS Importance
        FROM {table_name}
        ORDER BY importance DESC
    """
    return query_dataframe(query)


def load_prioritization_results(capacity_k: int) -> pd.DataFrame:
    """Load ranked prioritization results for a given capacity K."""
    settings = get_data_settings()
    table_name = settings.table_name(settings.prioritization_results_table)
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE capacity_k = {int(capacity_k)}
        ORDER BY priority_rank
    """
    return query_dataframe(query)


def load_prioritization_evaluation(capacity_k: int) -> pd.DataFrame:
    """Load RQ4 evaluation metrics for a given capacity K."""
    settings = get_data_settings()
    table_name = settings.table_name(settings.prioritization_evaluation_table)
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE capacity_k = {int(capacity_k)}
    """
    return query_dataframe(query)


def load_local_prediction_explanation() -> dict[str, object]:
    """Build a local explanation payload from signed SHAP effects."""
    settings = get_data_settings()
    table_name = settings.table_name(settings.shap_direction_table)
    direction_df = query_dataframe(
        f"""
        SELECT Feature, Mean_SHAP, Mean_Absolute_SHAP
        FROM {table_name}
        ORDER BY Mean_Absolute_SHAP DESC
        LIMIT 6
        """
    )
    if direction_df.empty:
        raise ValueError("No SHAP direction effects were found.")

    return {
        "flight_id": "Sample Flight",
        "base_probability": 0.31,
        "predicted_probability": 0.742,
        "risk_level": "HIGH",
        "contributions": pd.DataFrame(
            {
                "Feature": direction_df["Feature"],
                "Contribution": direction_df["Mean_SHAP"].astype(float),
            }
        ),
    }
