"""Recalculate Flight Explorer panel heights from the live viewport.

CSS sets the layout; this script updates CSS variables and resizes Plotly
charts when the tab becomes visible or the window changes size.
"""

import streamlit.components.v1 as components

_HEIGHT_SYNC_SCRIPT = """
<script>
(function () {
    const win = window.parent;
    const doc = win.document;
    const BOTTOM_PADDING = 10;
    let timer = null;

    function cssPx(name, fallback) {
        const value = win.getComputedStyle(doc.documentElement).getPropertyValue(name).trim();
        const parsed = parseInt(value, 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function resizePlotlyCharts() {
        doc.querySelectorAll('[data-testid="stPlotlyChart"] .js-plotly-plot').forEach(function (el) {
            if (win.Plotly) {
                win.Plotly.Plots.resize(el);
            }
        });

        doc.querySelectorAll('[data-testid="stHtml"] iframe').forEach(function (frame) {
            try {
                const frameWindow = frame.contentWindow;
                const frameDoc = frame.contentDocument;
                if (!frameWindow || !frameDoc || !frameWindow.Plotly) {
                    return;
                }
                frameDoc.querySelectorAll('.js-plotly-plot').forEach(function (el) {
                    frameWindow.Plotly.Plots.resize(el);
                });
            } catch (error) {
                return;
            }
        });
    }

    function syncHeights() {
        const marker = doc.querySelector(".explorer-layout-marker");
        if (!marker || marker.getBoundingClientRect().width <= 0) return;

        const row = doc.querySelector(
            '[data-testid="stHorizontalBlock"]:has(.explorer-filter-panel-marker)'
        );
        if (!row) return;

        const compactHeight = cssPx("--explorer-compact-height", 420);
        const sectionGap = cssPx("--explorer-section-gap", 10);
        const mainMarginTop = cssPx("--explorer-main-margin-top", 0);
        const logMinHeight = cssPx("--explorer-flight-log-min-height", 320);
        const shellHeight = Math.max(
            480,
            win.innerHeight - row.getBoundingClientRect().top - BOTTOM_PADDING
        );
        const logHeight = Math.max(
            logMinHeight,
            shellHeight - compactHeight - sectionGap - mainMarginTop
        );

        doc.documentElement.style.setProperty("--explorer-shell-height", shellHeight + "px");
        doc.documentElement.style.setProperty("--explorer-flight-log-height", logHeight + "px");
        resizePlotlyCharts();
    }

    function scheduleSync() {
        if (timer) win.clearTimeout(timer);
        timer = win.setTimeout(syncHeights, 60);
    }

    win.addEventListener("load", scheduleSync);
    win.addEventListener("resize", scheduleSync);
    doc.querySelectorAll('[data-baseweb="tab"]').forEach(function (tab) {
        tab.addEventListener("click", function () {
            win.setTimeout(scheduleSync, 120);
            win.setTimeout(scheduleSync, 400);
        });
    });

    const observer = new MutationObserver(function () {
        scheduleSync();
    });
    observer.observe(doc.body, { childList: true, subtree: true });

    scheduleSync();
    win.setTimeout(scheduleSync, 250);
    win.setTimeout(scheduleSync, 800);
})();
</script>
"""


def render_explorer_layout_sync() -> None:
    """Inject zero-height iframe that syncs explorer height CSS variables."""
    components.html(_HEIGHT_SYNC_SCRIPT, height=0, scrolling=False)
