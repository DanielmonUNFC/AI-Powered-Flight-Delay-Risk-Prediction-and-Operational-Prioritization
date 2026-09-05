"""Plotly charts for the Model Insights page."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from styles.theme import COLORS
from styles.typography import (
    PLOTLY_FONT_SIZE,
    PLOTLY_FONT_SIZE_ANNOTATION,
    PLOTLY_FONT_SIZE_TICK,
    PLOTLY_FONT_SIZE_TITLE,
)


_POSITIVE_COLOR = "#d47a6b"
_NEGATIVE_COLOR = "#69b27f"
_GLOBAL_BAR_START = "#355d93"
_GLOBAL_BAR_END = "#74b9ff"

_CHART_HEIGHT = 485
_GLOBAL_LEFT_MARGIN = 220
_LOCAL_LEFT_MARGIN = 190


def build_global_feature_importance_chart(
    feature_importance: pd.DataFrame,
) -> go.Figure:
    """Build the global mean absolute SHAP importance chart."""

    _validate_columns(
        feature_importance,
        {"Feature", "Importance"},
        dataset_name="global feature importance",
    )

    chart_data = (
        feature_importance
        .copy()
        .sort_values("Importance", ascending=True)
        .reset_index(drop=True)
    )

    maximum_importance = float(
        chart_data["Importance"].max()
    )

    figure = go.Figure(
        go.Bar(
            x=chart_data["Importance"],
            y=chart_data["Feature"],
            orientation="h",
            marker={
                "color": chart_data["Importance"],
                "colorscale": [
                    [0.0, _GLOBAL_BAR_START],
                    [1.0, _GLOBAL_BAR_END],
                ],
                "showscale": False,
                "line": {
                    "color": "rgba(255, 255, 255, 0.08)",
                    "width": 1,
                },
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Mean absolute SHAP value: %{x:.2f}"
                "<extra></extra>"
            ),
        )
    )

    # Keep global SHAP values visible when Plotly resizes inside the
    # Streamlit component iframe. Unlike local contributions, these mean
    # absolute values are always non-negative and therefore have no sign.
    for feature, importance in zip(
        chart_data["Feature"],
        chart_data["Importance"],
    ):
        value = float(importance)
        figure.add_annotation(
            x=value,
            y=feature,
            text=f"{value:.3f}",
            showarrow=False,
            xanchor="left",
            xshift=7,
            font={
                "color": COLORS["text_secondary"],
                "size": PLOTLY_FONT_SIZE_TICK,
            },
        )

    figure.update_layout(
        height=_CHART_HEIGHT,
        meta={"chart_kind": "global_shap"},
        margin={
            "l": _GLOBAL_LEFT_MARGIN,
            "r": 65,
            "t": 12,
            "b": 62,
            "pad": 4,
        },
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font={
            "color": COLORS["text_secondary"],
            "size": PLOTLY_FONT_SIZE,
        },
        bargap=0.24,
        showlegend=False,
        hoverlabel={
            "bgcolor": COLORS["surface_elevated"],
            "bordercolor": COLORS["border_subtle"],
            "font": {
                "color": COLORS["text_primary"],
            },
        },
        xaxis={
            "title": {
                "text": "Mean Absolute SHAP Value",
                "font": {
                    "color": COLORS["text_muted"],
                    "size": PLOTLY_FONT_SIZE_TITLE,
                },
                "standoff": 14,
            },
            "range": [
                0,
                maximum_importance * 1.15,
            ],
            "showgrid": True,
            "gridcolor": "rgba(90, 110, 145, 0.20)",
            "gridwidth": 1,
            "zeroline": False,
            "fixedrange": True,
            "tickfont": {
                "color": COLORS["text_muted"],
                "size": PLOTLY_FONT_SIZE_TICK,
            },
        },
        yaxis={
            "title": "",
            "showgrid": False,
            "automargin": False,
            "fixedrange": True,
            "tickfont": {
                "color": COLORS["text_secondary"],
                "size": PLOTLY_FONT_SIZE_TICK,
            },
        },
    )

    return figure


def build_local_prediction_explanation_chart(
    contributions: pd.DataFrame,
    *,
    base_probability: float,
    predicted_probability: float,
    decision_threshold: float,
) -> go.Figure:
    """
    Build a horizontal local prediction explanation chart.

    Positive contributions increase delay risk and use coral.
    Negative contributions reduce delay risk and use green.
    """

    _validate_columns(
        contributions,
        {"Feature", "Contribution"},
        dataset_name="local prediction explanation",
    )
    _validate_probability(
        base_probability,
        "base_probability",
    )
    _validate_probability(
        predicted_probability,
        "predicted_probability",
    )
    _validate_probability(
        decision_threshold,
        "decision_threshold",
    )

    chart_data = (
        contributions
        .copy()
        .sort_values(
            "Contribution",
            key=lambda values: values.abs(),
            ascending=True,
        )
        .reset_index(drop=True)
    )

    positive_values = chart_data["Contribution"].clip(
        lower=0
    )
    negative_values = chart_data["Contribution"].clip(
        upper=0
    )

    maximum_impact = max(
        float(chart_data["Contribution"].abs().max()),
        0.20,
    )

    axis_limit = maximum_impact * 1.45

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=positive_values,
            y=chart_data["Feature"],
            orientation="h",
            name="Increases risk",
            marker={
                "color": _POSITIVE_COLOR,
                "line": {
                    "color": "rgba(255, 255, 255, 0.08)",
                    "width": 1,
                },
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "SHAP contribution: %{x:+.3f} log-odds"
                "<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Bar(
            x=negative_values,
            y=chart_data["Feature"],
            orientation="h",
            name="Reduces risk",
            marker={
                "color": _NEGATIVE_COLOR,
                "line": {
                    "color": "rgba(255, 255, 255, 0.08)",
                    "width": 1,
                },
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "SHAP contribution: %{x:+.3f} log-odds"
                "<extra></extra>"
            ),
        )
    )

    # Plotly may suppress outside bar text when this figure is resized inside
    # a Streamlit component iframe. Explicit annotations keep one signed value
    # visible at the end of every bar at all supported viewport widths.
    for feature, contribution in zip(
        chart_data["Feature"],
        chart_data["Contribution"],
    ):
        value = float(contribution)
        figure.add_annotation(
            x=value,
            y=feature,
            text=f"{value:+.3f}",
            showarrow=False,
            xanchor="left" if value >= 0 else "right",
            xshift=7 if value >= 0 else -7,
            font={
                "color": COLORS["text_secondary"],
                "size": PLOTLY_FONT_SIZE_TICK,
            },
        )

    figure.add_vline(
        x=0,
        line={
            "color": COLORS["text_muted"],
            "width": 1.4,
        },
    )

    prediction_label = _get_prediction_label(
        predicted_probability,
        decision_threshold,
    )
    prediction_color = _get_prediction_color(
        prediction_label
    )

    figure.add_annotation(
        x=axis_limit * 0.95,
        y=1.14,
        xref="x",
        yref="paper",
        text=(
            f"<b>Net Risk: "
            f"{predicted_probability:.1%}</b><br>"
            f"<span style='color:{prediction_color}'>"
            f"{prediction_label}</span><br>"
            f"<span>Threshold: {decision_threshold:.1%} · "
            f"Baseline: {base_probability:.1%}</span>"
        ),
        showarrow=False,
        align="right",
        xanchor="right",
        yanchor="top",
        font={
            "size": PLOTLY_FONT_SIZE_ANNOTATION,
            "color": COLORS["text_primary"],
        },
    )

    figure.update_layout(
        height=_CHART_HEIGHT,
        meta={"chart_kind": "local_shap"},
        barmode="overlay",
        margin={
            "l": _LOCAL_LEFT_MARGIN,
            "r": 95,
            "t": 62,
            "b": 70,
            "pad": 4,
        },
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font={
            "color": COLORS["text_secondary"],
            "size": PLOTLY_FONT_SIZE,
        },
        showlegend=False,
        bargap=0.28,
        hoverlabel={
            "bgcolor": COLORS["surface_elevated"],
            "bordercolor": COLORS["border_subtle"],
            "font": {
                "color": COLORS["text_primary"],
            },
        },
        xaxis={
            "title": {
                "text": "SHAP Contribution to Raw Model Score (log-odds)",
                "font": {
                    "color": COLORS["text_muted"],
                    "size": PLOTLY_FONT_SIZE_TITLE,
                },
                "standoff": 14,
            },
            "range": [
                -axis_limit,
                axis_limit,
            ],
            "tickformat": "+.2f",
            "showgrid": True,
            "gridcolor": "rgba(90, 110, 145, 0.20)",
            "gridwidth": 1,
            "zeroline": False,
            "fixedrange": True,
            "tickfont": {
                "color": COLORS["text_muted"],
                "size": PLOTLY_FONT_SIZE_TICK,
            },
        },
        yaxis={
            "title": "",
            "showgrid": False,
            "automargin": False,
            "fixedrange": True,
            "tickfont": {
                "color": COLORS["text_secondary"],
                "size": PLOTLY_FONT_SIZE_TICK,
            },
        },
    )

    return figure


def _get_prediction_label(
    probability: float,
    decision_threshold: float,
) -> str:
    """Return the frozen binary model decision."""
    if probability >= decision_threshold:
        return "DELAY ALERT"
    return "ON-TIME PREDICTION"


def _get_prediction_color(
    prediction_label: str,
) -> str:
    """Return the binary prediction display color."""
    if prediction_label == "DELAY ALERT":
        return _POSITIVE_COLOR
    return _NEGATIVE_COLOR


def _validate_columns(
    data: pd.DataFrame,
    required_columns: set[str],
    *,
    dataset_name: str,
) -> None:
    """Validate required DataFrame columns."""

    missing_columns = required_columns.difference(
        data.columns
    )

    if missing_columns:
        missing = ", ".join(
            sorted(missing_columns)
        )
        raise ValueError(
            f"The {dataset_name} data is missing required "
            f"columns: {missing}."
        )

    if data.empty:
        raise ValueError(
            f"The {dataset_name} data cannot be empty."
        )


def _validate_probability(
    value: float,
    field_name: str,
) -> None:
    """Validate a probability value."""

    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{field_name} must be numeric."
        ) from exc

    if not 0.0 <= numeric_value <= 1.0:
        raise ValueError(
            f"{field_name} must be between 0 and 1."
        )
