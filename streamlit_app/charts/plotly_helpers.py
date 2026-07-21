"""Shared Plotly layout helpers for consistent chart styling."""

from typing import Any

import plotly.graph_objects as go

from styles.theme import CHART_HEIGHT, COLORS


def transparent_layout(**overrides: Any) -> dict[str, Any]:
    """Return a base Plotly layout configured for dark Streamlit surfaces."""
    layout = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": COLORS["text_secondary"], "size": 12},
        "margin": {"l": 0, "r": 0, "t": 10, "b": 0},
        "height": CHART_HEIGHT,
        "hovermode": "x unified",
    }
    layout.update(overrides)
    return layout


def apply_transparent_layout(fig: go.Figure, **overrides: Any) -> go.Figure:
    """Apply the shared transparent layout to a Plotly figure."""
    fig.update_layout(**transparent_layout(**overrides))
    return fig
