"""Model Insights page backed only by real SHAP artifacts."""

from __future__ import annotations

import streamlit as st

from components.model_insights_panel import (
    render_global_feature_importance_panel,
    render_local_prediction_explanation_panel,
    render_model_insights_error,
)
from services.model_insights_data import get_model_insights_page_data


def render_model_insights_page() -> None:
    """Render Model Insights without substituting simulated results."""

    st.markdown(
        """
        <div class="page-subtitle page-subtitle--model-insights">
            Global and local SHAP explainability for delay-risk predictions
        </div>
        """,
        unsafe_allow_html=True,
    )

    global_column, local_column = st.columns(
        [1, 1],
        gap="large",
    )

    insights_data = get_model_insights_page_data()
    if insights_data is None:
        with global_column:
            render_model_insights_error(
                "Global SHAP results are unavailable from the API."
            )
        with local_column:
            render_model_insights_error(
                "Local SHAP results are unavailable from the API."
            )
        return

    with global_column:
        try:
            feature_importance = insights_data["global_importance"]
            if feature_importance.empty:
                raise ValueError("The SHAP importance table is empty.")
            render_global_feature_importance_panel(feature_importance)
        except Exception as error:
            render_model_insights_error(
                f"Unable to load the real global SHAP results: {error}"
            )

    with local_column:
        try:
            render_local_prediction_explanation_panel(
                insights_data["local_explanation"]
            )
        except Exception as error:
            render_model_insights_error(
                f"Unable to render the real local SHAP explanation: {error}"
            )
