"""Plotly charts for the Model Insights page."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from styles.theme import COLORS


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
            text=chart_data["Importance"].map(
                lambda value: f"{value:.1f}"
            ),
            textposition="outside",
            cliponaxis=False,
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

    figure.update_layout(
        height=_CHART_HEIGHT,
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
            "size": 12,
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
                    "size": 12,
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
                "size": 11,
            },
        },
        yaxis={
            "title": "",
            "showgrid": False,
            "automargin": False,
            "fixedrange": True,
            "tickfont": {
                "color": COLORS["text_secondary"],
                "size": 11,
            },
        },
    )

    return figure


def build_local_prediction_explanation_chart(
    contributions: pd.DataFrame,
    *,
    base_probability: float,
    predicted_probability: float,
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
            text=[
                f"+{value:.1%}" if value > 0 else ""
                for value in positive_values
            ],
            textposition="outside",
            textfont={
                "color": COLORS["text_secondary"],
                "size": 11,
            },
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Risk contribution: %{x:+.1%}"
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
            text=[
                f"{value:.1%}" if value < 0 else ""
                for value in negative_values
            ],
            textposition="outside",
            textfont={
                "color": COLORS["text_secondary"],
                "size": 11,
            },
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Risk contribution: %{x:+.1%}"
                "<extra></extra>"
            ),
        )
    )

    figure.add_vline(
        x=0,
        line={
            "color": COLORS["text_muted"],
            "width": 1.4,
        },
    )

    net_risk_level = _get_net_risk_level(
        predicted_probability
    )
    net_risk_color = _get_net_risk_color(
        predicted_probability
    )

    figure.add_annotation(
        x=axis_limit * 0.95,
        y=1.14,
        xref="x",
        yref="paper",
        text=(
            f"<b>Net Risk: "
            f"{predicted_probability:.1%}</b><br>"
            f"<span style='color:{net_risk_color}'>"
            f"{net_risk_level}"
            "</span>"
        ),
        showarrow=False,
        align="right",
        xanchor="right",
        yanchor="top",
        font={
            "size": 14,
            "color": COLORS["text_primary"],
        },
    )

    figure.add_annotation(
        x=-axis_limit * 0.95,
        y=-0.17,
        xref="x",
        yref="paper",
        text=f"Base rate: {base_probability:.1%}",
        showarrow=False,
        align="left",
        xanchor="left",
        font={
            "size": 11,
            "color": COLORS["text_muted"],
        },
    )

    figure.update_layout(
        height=_CHART_HEIGHT,
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
            "size": 12,
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
                "text": "Feature Contribution to Delay Risk",
                "font": {
                    "color": COLORS["text_muted"],
                    "size": 12,
                },
                "standoff": 14,
            },
            "range": [
                -axis_limit,
                axis_limit,
            ],
            "tickformat": "+.0%",
            "showgrid": True,
            "gridcolor": "rgba(90, 110, 145, 0.20)",
            "gridwidth": 1,
            "zeroline": False,
            "fixedrange": True,
            "tickfont": {
                "color": COLORS["text_muted"],
                "size": 11,
            },
        },
        yaxis={
            "title": "",
            "showgrid": False,
            "automargin": False,
            "fixedrange": True,
            "tickfont": {
                "color": COLORS["text_secondary"],
                "size": 11,
            },
        },
    )

    return figure


def _get_net_risk_level(
    probability: float,
) -> str:
    """Return the operational risk category."""

    if probability < 0.30:
        return "LOW"

    if probability < 0.60:
        return "MEDIUM"

    if probability < 0.80:
        return "HIGH"

    return "CRITICAL"


def _get_net_risk_color(
    probability: float,
) -> str:
    """Return the risk display color."""

    risk_colors = {
        "LOW": "#69b27f",
        "MEDIUM": "#d0ad63",
        "HIGH": "#d47a6b",
        "CRITICAL": "#a95656",
    }

    return risk_colors[
        _get_net_risk_level(probability)
    ]


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