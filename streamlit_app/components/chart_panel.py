"""Reusable surface card for chart visualizations."""

from typing import Optional

from plotly.graph_objects import Figure

from components.surface_card import render_html_panel
from styles.theme import COMPACT_PANEL_HEIGHT, PLOTLY_CONFIG

_CHART_RESIZE_SCRIPT = """
<script>
(function () {
    function plotBodyHeight() {
        var frame = window.frameElement;
        if (!frame) return 0;
        var frameHeight = frame.clientHeight || frame.offsetHeight;
        var header = document.querySelector(".surface-panel-card__header");
        var headerHeight = header ? header.offsetHeight : 0;
        return Math.max(220, frameHeight - headerHeight - 24);
    }

    function plotBodyWidth() {
        var body = document.querySelector(".surface-panel-card__body");
        return body ? body.clientWidth : 0;
    }

    function resizePlotly() {
        var plot = document.querySelector(".js-plotly-plot");
        if (!plot || !window.Plotly) return;
        var height = plotBodyHeight();
        var width = plotBodyWidth();
        var relayout = { height: height };
        if (width > 0) {
            relayout.width = width;
        }
        Plotly.relayout(plot, relayout);
        Plotly.Plots.resize(plot);
    }

    function syncChartFrame() {
        try {
            var frame = window.frameElement;
            if (frame) {
                var frameHeight = frame.clientHeight || frame.offsetHeight;
                if (frameHeight > 0) {
                    document.documentElement.style.height = frameHeight + "px";
                    document.body.style.height = frameHeight + "px";
                }
            }
            resizePlotly();
        } catch (error) {
            return;
        }
    }

    function waitForPlotly(attempt) {
        if (window.Plotly) {
            syncChartFrame();
            return;
        }
        if (attempt >= 25) return;
        window.setTimeout(function () {
            waitForPlotly(attempt + 1);
        }, 100);
    }

    window.addEventListener("load", function () {
        waitForPlotly(0);
    });
    window.addEventListener("resize", syncChartFrame);

    if (window.ResizeObserver && window.frameElement) {
        new ResizeObserver(syncChartFrame).observe(window.frameElement);
    }

    window.setTimeout(function () { waitForPlotly(0); }, 120);
    window.setTimeout(function () { waitForPlotly(0); }, 500);
})();
</script>
"""


def render_chart_panel(
    title: str,
    icon_id: str,
    figure: Figure,
    *,
    height: Optional[int] = None,
    fill_height: bool = True,
) -> None:
    """Render a chart inside the standard surface panel card."""
    chart_html = figure.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config=PLOTLY_CONFIG,
    )
    extra_css = """
        .surface-panel-card {
            padding: 12px 16px 10px 16px;
        }
        .surface-panel-card__header {
            margin-bottom: 6px;
        }
        .surface-panel-card__body,
        .surface-panel-card__body .plotly-graph-div {
            width: 100% !important;
            flex: 1 1 auto;
            min-height: 0;
            height: 100%;
            overflow: visible;
        }
        .surface-panel-card__body .plotly-graph-div .main-svg {
            overflow: visible;
        }
    """

    render_html_panel(
        title=title,
        icon_id=icon_id,
        body_html=chart_html,
        height=height or COMPACT_PANEL_HEIGHT,
        fill_height=False,
        extra_css=extra_css,
        inline_script=_CHART_RESIZE_SCRIPT if fill_height else "",
    )
