"""Overview tab chart builders."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from charts.plotly_helpers import apply_transparent_layout
from styles.theme import COLORS, PLOTLY_PIE_COLORS


def create_monthly_trend_figure(df: pd.DataFrame) -> go.Figure:
    """Build the monthly delay rate trend line chart."""
    fig = px.line(
        df,
        x="Month",
        y="DelayRate",
        markers=True,
        line_shape="spline",
    )
    fig.update_traces(
        line_color=COLORS["chart_line"],
        line_width=3,
        marker_size=6,
    )
    fig.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(
            showgrid=False,
            color=COLORS["text_secondary"],
            automargin=True,
            tickfont=dict(size=12),
            tickmode="array",
            tickvals=list(df["Month"]),
            ticktext=list(df["Month"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["grid"],
            color=COLORS["text_secondary"],
            ticksuffix="%",
            automargin=True,
            tickfont=dict(size=12),
        ),
    )
    fig.add_annotation(
        x="Jun",
        y=df.loc[df["Month"] == "Jun", "DelayRate"].iloc[0],
        text="summer",
        showarrow=False,
        yshift=18,
        font=dict(size=11, color=COLORS["text_muted"]),
    )
    fig.add_annotation(
        x="Dec",
        y=df.loc[df["Month"] == "Dec", "DelayRate"].iloc[0],
        text="winter",
        showarrow=False,
        yshift=18,
        font=dict(size=11, color=COLORS["text_muted"]),
    )
    return apply_transparent_layout(
        fig,
        height=340,
        autosize=True,
        margin={"l": 56, "r": 40, "t": 28, "b": 56},
    )


def create_delay_causes_figure(df: pd.DataFrame) -> go.Figure:
    """Build the delay causes donut chart."""
    fig = px.pie(
        df,
        values="Percentage",
        names="Cause",
        hole=0.62,
        color_discrete_sequence=PLOTLY_PIE_COLORS,
    )
    fig.update_traces(
        textinfo="none",
        marker=dict(line=dict(color=COLORS["surface_elevated"], width=2)),
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(
            font=dict(color=COLORS["text_secondary"], size=11),
            orientation="v",
            yanchor="middle",
            y=0.5,
            x=1.02,
        ),
    )
    return apply_transparent_layout(fig)
