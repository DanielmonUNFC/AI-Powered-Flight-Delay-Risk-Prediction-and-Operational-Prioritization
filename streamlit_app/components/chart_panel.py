"""Reusable surface card for chart visualizations."""

from plotly.graph_objects import Figure

from components.surface_card import render_html_panel
from styles.theme import COMPACT_PANEL_HEIGHT, PLOTLY_CONFIG


def render_chart_panel(title: str, icon_id: str, figure: Figure) -> None:
    """Render a chart inside the standard surface panel card."""
    chart_html = figure.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config=PLOTLY_CONFIG,
    )
    extra_css = """
        .surface-panel-card__body,
        .surface-panel-card__body .plotly-graph-div {
            width: 100% !important;
        }
    """

    render_html_panel(
        title=title,
        icon_id=icon_id,
        body_html=chart_html,
        height=COMPACT_PANEL_HEIGHT,
        extra_css=extra_css,
    )
