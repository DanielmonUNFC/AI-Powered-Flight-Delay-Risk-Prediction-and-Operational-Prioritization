"""Reusable panels for Model Insights visualizations."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts.model_insights_charts import (
    build_global_feature_importance_chart,
    build_local_prediction_explanation_chart,
)
from components.surface_card import render_html_panel
from styles.theme import COLORS, PLOTLY_CONFIG


_MODEL_INSIGHTS_CSS_PATH = (
    Path(__file__).resolve().parents[1]
    / "styles"
    / "model_insights.css"
)

_MODEL_INSIGHTS_PANEL_HEIGHT = 560
_MODEL_INSIGHTS_CHART_HEIGHT = 485


def render_global_feature_importance_panel(
    feature_importance: pd.DataFrame,
) -> None:
    """Render the global SHAP feature-importance panel."""

    figure = build_global_feature_importance_chart(
        feature_importance
    )

    _render_model_insights_chart(
        title="Global Feature Importance (SHAP)",
        figure=figure,
    )


def render_local_prediction_explanation_panel(
    explanation: dict[str, Any],
) -> None:
    """Render the local SHAP prediction-explanation panel."""

    contributions = explanation.get("contributions")
    base_probability = explanation.get("base_probability")
    predicted_probability = explanation.get(
        "predicted_probability"
    )
    flight_id = str(
        explanation.get("flight_id", "Unknown Flight")
    )

    if not isinstance(contributions, pd.DataFrame):
        raise ValueError(
            "Local explanation contributions must be a DataFrame."
        )

    if base_probability is None:
        raise ValueError(
            "Local explanation is missing base_probability."
        )

    if predicted_probability is None:
        raise ValueError(
            "Local explanation is missing predicted_probability."
        )

    figure = build_local_prediction_explanation_chart(
        contributions,
        base_probability=float(base_probability),
        predicted_probability=float(predicted_probability),
    )

    _render_model_insights_chart(
        title=(
            "Local Prediction Explanation "
            f"(Flight {flight_id})"
        ),
        figure=figure,
    )


def render_model_insights_error(message: str) -> None:
    """Render a user-friendly Model Insights error message."""

    st.error(message)


def _render_model_insights_chart(
    *,
    title: str,
    figure: go.Figure,
) -> None:
    """Render a Plotly chart inside the standard surface panel."""

    chart_html = figure.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config=PLOTLY_CONFIG,
        default_width="100%",
        default_height=f"{_MODEL_INSIGHTS_CHART_HEIGHT}px",
    )

    body_html = f"""
        <div class="model-insights-chart">
            {chart_html}
        </div>
    """

    render_html_panel(
        title=title,
        icon_id="model_insights",
        body_html=body_html,
        height=_MODEL_INSIGHTS_PANEL_HEIGHT,
        extra_css=_model_insights_component_css(),
    )


@lru_cache(maxsize=1)
def _load_model_insights_stylesheet() -> str:
    """Load the Model Insights stylesheet once per process."""

    try:
        return _MODEL_INSIGHTS_CSS_PATH.read_text(
            encoding="utf-8"
        )
    except OSError as exc:
        raise RuntimeError(
            "Unable to load the Model Insights stylesheet from "
            f"{_MODEL_INSIGHTS_CSS_PATH}."
        ) from exc


@lru_cache(maxsize=1)
def _model_insights_component_css() -> str:
    """Return iframe-ready Model Insights styles."""

    theme_variables = f"""
        :root {{
            --model-insights-text-primary:
                {COLORS["text_primary"]};
            --model-insights-text-secondary:
                {COLORS["text_secondary"]};
            --model-insights-text-muted:
                {COLORS["text_muted"]};
            --model-insights-accent:
                {COLORS["accent_bright"]};
            --model-insights-border-subtle:
                {COLORS["border_subtle"]};
        }}
    """

    return (
        theme_variables
        + "\n"
        + _load_model_insights_stylesheet()
    )