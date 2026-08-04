"""Flight Explorer chart and table builders."""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from charts.plotly_helpers import apply_transparent_layout
from styles.theme import COLORS


def _chart_carrier_name(name: str, code: str) -> str:
    """Prefer readable airline names on the chart y-axis."""
    cleaned = str(name).strip()
    if cleaned and cleaned != code:
        return cleaned
    return code


def create_airline_performance_figure(
    df: pd.DataFrame,
    *,
    chart_height: int = 280,
) -> Optional[go.Figure]:
    """Build the airline delay rate comparison bar chart."""
    if df.empty:
        return None

    carrier_perf = (
        df.groupby(["Carrier", "CarrierName"], as_index=False)["DelayProb"]
        .mean()
        .sort_values(by="DelayProb", ascending=True)
    )
    carrier_perf["ChartLabel"] = carrier_perf.apply(
        lambda row: _chart_carrier_name(row["CarrierName"], row["Carrier"]),
        axis=1,
    )
    carrier_perf["DelayRate%"] = carrier_perf["DelayProb"] * 100
    max_label_chars = max(len(label) for label in carrier_perf["ChartLabel"]) if not carrier_perf.empty else 12
    left_margin = min(340, max(200, max_label_chars * 9 + 56))
    label_font_size = 15 if max_label_chars <= 18 else 14
    x_max = max(carrier_perf["DelayRate%"].max() * 1.28, 14)

    fig = px.bar(
        carrier_perf,
        x="DelayRate%",
        y="ChartLabel",
        orientation="h",
        text=carrier_perf["DelayRate%"].apply(lambda value: f"{value:.1f}%"),
        color="DelayRate%",
        color_continuous_scale=["#00D2FF", "#3B82F6"],
        custom_data=["Carrier"],
    )
    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker_line_color="rgba(0,0,0,0)",
        width=0.88,
        textfont=dict(size=14, color=COLORS["text_primary"]),
        hovertemplate="%{y}<br>Predicted delay risk: %{x:.1f}%<extra></extra>",
    )
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        bargap=0.03,
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(
            showgrid=True,
            gridcolor=COLORS["grid"],
            color=COLORS["text_secondary"],
            ticksuffix="%",
            tickfont=dict(size=13),
            ticklabelstandoff=12,
            range=[0, x_max],
            automargin=True,
        ),
        yaxis=dict(
            showgrid=False,
            color=COLORS["text_primary"],
            automargin=False,
            ticklabelstandoff=32,
            tickfont=dict(size=label_font_size),
            categoryorder="total ascending",
        ),
    )
    return apply_transparent_layout(
        fig,
        height=chart_height,
        autosize=True,
        hovermode="closest",
        margin={"l": left_margin, "r": 104, "t": 16, "b": 56},
    )


def build_top_delayed_routes_table(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the top routes table ranked by peak predicted delay risk."""
    if df.empty:
        return pd.DataFrame(columns=["Route", "Flights", "Peak Delay Risk"])

    route_source = df.copy()
    route_source["Route"] = route_source.apply(
        lambda row: f"{row['Origin']} → {row['Destination']}",
        axis=1,
    )

    routes = (
        route_source.groupby(["Origin", "Destination", "Route"], as_index=False)
        .agg(
            PeakDelayProb=("DelayProb", "max"),
            Flights=("Flight", "count"),
        )
        .sort_values(by="PeakDelayProb", ascending=False)
        .head(5)
    )
    routes["Flights"] = routes["Flights"].astype(int).astype(str)
    routes["Peak Delay Risk"] = routes["PeakDelayProb"].apply(
        lambda value: f'<span class="delay-value">{value * 100:.1f}%</span>'
    )
    return routes[["Route", "Flights", "Peak Delay Risk"]]


def build_filtered_flight_log_table(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the detailed flight log table with row styling helpers."""
    if df.empty:
        return pd.DataFrame()

    display_df = df.copy()
    display_df["Flight ID"] = display_df["Flight"].apply(
        lambda flight: f'<span class="flight-link">{flight}</span>'
    )
    display_df["Predicted Delay Risk"] = display_df["DelayProb"].apply(
        lambda value: f'<span class="delay-value">{value * 100:.1f}%</span>'
    )
    display_df["Risk Level"] = display_df["RiskTier"].apply(_format_risk_tier_cell)
    display_df["Primary Risk Factor"] = display_df["ShapMainDriver"].apply(
        _format_primary_factor
    )
    display_df["_row_class"] = display_df["RiskTier"].apply(_format_row_class)

    return display_df[
        [
            "Flight ID",
            "CarrierLabel",
            "OriginLabel",
            "DestinationLabel",
            "DepartureWindow",
            "SchedDep",
            "Predicted Delay Risk",
            "Risk Level",
            "Primary Risk Factor",
            "_row_class",
        ]
    ].rename(
        columns={
            "CarrierLabel": "Airline",
            "OriginLabel": "Origin<br>Airport",
            "DestinationLabel": "Destination<br>Airport",
            "DepartureWindow": "Departure<br>Window",
            "SchedDep": "Scheduled<br>Departure",
            "Flight ID": "Flight<br>ID",
            "Predicted Delay Risk": "Predicted<br>Delay Risk",
            "Risk Level": "Risk<br>Level",
            "Primary Risk Factor": "Primary<br>Risk Factor",
        }
    )


def _format_risk_tier_cell(risk_tier: str) -> str:
    tier = str(risk_tier).upper()
    if tier == "CRITICAL":
        return '<span class="status-critical">CRITICAL</span>'
    if tier == "HIGH":
        return '<span class="status-high">HIGH</span>'
    if tier == "MEDIUM":
        return '<span class="status-high">MEDIUM</span>'
    return '<span class="status-low">LOW</span>'


def _format_row_class(risk_tier: str) -> str:
    tier = str(risk_tier).upper()
    if tier == "CRITICAL":
        return "row-critical"
    if tier in {"HIGH", "MEDIUM"}:
        return "row-high"
    return ""


def _format_primary_factor(value: str) -> str:
    """Present the simplified SHAP driver label in readable form."""
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return "—"
    text = text.replace("SEASON ", "Season · ").replace("_", " ")
    if len(text) > 28:
        return f"{text[:25]}..."
    return text
