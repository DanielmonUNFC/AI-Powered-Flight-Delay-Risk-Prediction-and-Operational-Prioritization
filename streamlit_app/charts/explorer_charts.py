"""Flight Explorer chart and table builders."""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from charts.plotly_helpers import apply_transparent_layout
from styles.theme import CHART_HEIGHT, COLORS


def create_airline_performance_figure(df: pd.DataFrame) -> Optional[go.Figure]:
    """Build the airline delay rate comparison bar chart."""
    if df.empty:
        return None

    carrier_perf = (
        df.groupby("Carrier")["DelayProb"]
        .mean()
        .reset_index()
        .sort_values(by="DelayProb", ascending=True)
    )
    carrier_perf["DelayRate%"] = carrier_perf["DelayProb"] * 100

    fig = px.bar(
        carrier_perf,
        x="DelayRate%",
        y="Carrier",
        orientation="h",
        text=carrier_perf["DelayRate%"].apply(lambda value: f"{value:.1f}%"),
        color="DelayRate%",
        color_continuous_scale=["#00D2FF", "#3B82F6"],
    )
    fig.update_traces(textposition="outside", marker_line_color="rgba(0,0,0,0)")
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Delay Rate",
        yaxis_title=None,
        xaxis=dict(showgrid=True, gridcolor=COLORS["grid"], color=COLORS["text_secondary"]),
        yaxis=dict(showgrid=False, color=COLORS["text_secondary"]),
        margin=dict(l=10, r=10, t=10, b=10),
        height=CHART_HEIGHT,
    )
    return apply_transparent_layout(fig, height=CHART_HEIGHT, hovermode=False)


def build_top_delayed_routes_table(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the top delayed routes summary table."""
    if df.empty:
        return pd.DataFrame(columns=["Route", "Delay %", "Avg Time"])

    routes = (
        df.groupby(["Origin", "Destination"])
        .agg(DelayProb=("DelayProb", "mean"))
        .reset_index()
        .sort_values(by="DelayProb", ascending=False)
        .head(5)
    )
    routes["Route"] = routes["Origin"] + " → " + routes["Destination"]
    routes["Delay %"] = routes["DelayProb"].apply(
        lambda value: f'<span class="delay-value">{value * 100:.1f}%</span>'
    )
    routes["Avg Time"] = "32m"
    return routes[["Route", "Delay %", "Avg Time"]]


def build_filtered_flight_log_table(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the detailed flight log table with row styling helpers."""
    if df.empty:
        return pd.DataFrame()

    display_df = df.copy()
    display_df["Flight"] = display_df["Flight"].apply(
        lambda flight: f'<span class="flight-link">{flight}</span>'
    )
    display_df["Trend"] = display_df["DelayProb"].apply(_format_trend_sparkline)
    display_df["DELAYProb%"] = display_df["DelayProb"].apply(
        lambda value: f'<span class="delay-value">{value * 100:.1f}%</span>'
    )
    display_df["STATUS"] = display_df["DelayProb"].apply(_format_status_cell)
    display_df["_row_class"] = display_df["DelayProb"].apply(_format_row_class)

    columns = [
        "Flight",
        "Carrier",
        "Origin",
        "Destination",
        "Trend",
        "SchedDep",
        "DELAYProb%",
        "STATUS",
        "_row_class",
    ]
    return display_df[columns]


def _format_status_cell(delay_prob: float) -> str:
    if delay_prob >= 0.8:
        return '<span class="status-critical">CRITICAL</span>'
    if delay_prob >= 0.5:
        return '<span class="status-high">HIGH</span>'
    return '<span class="status-low">LOW</span>'


def _format_row_class(delay_prob: float) -> str:
    if delay_prob >= 0.8:
        return "row-critical"
    if delay_prob >= 0.5:
        return "row-high"
    return ""


def _format_trend_sparkline(delay_prob: float) -> str:
    """Render a compact inline sparkline for the flight trend column."""
    seed = int(delay_prob * 100)
    heights = [8 + ((seed + index * 7) % 12) for index in range(5)]
    bars = "".join(
        f'<rect x="{index * 6 + 1}" y="{22 - height}" width="4" height="{height}" '
        f'rx="1" fill="#3b82f6" opacity="{0.45 + (height / 30):.2f}"/>'
        for index, height in enumerate(heights)
    )
    return (
        '<svg width="34" height="24" viewBox="0 0 34 24" '
        'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Trend">'
        f"{bars}</svg>"
    )
