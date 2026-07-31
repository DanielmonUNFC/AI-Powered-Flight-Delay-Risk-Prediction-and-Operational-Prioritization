"""Recalculate Delay Prediction panel heights from the live viewport."""

import streamlit.components.v1 as components

_HEIGHT_SYNC_SCRIPT = """
<script>
(function () {
    const win = window.parent;
    const doc = win.document;
    const BOTTOM_PADDING = 20;
    let timer = null;

    function cssPx(name, fallback) {
        const value = win.getComputedStyle(doc.documentElement).getPropertyValue(name).trim();
        const parsed = parseInt(value, 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function syncHeights() {
        const marker = doc.querySelector(".delay-prediction-layout-marker");
        if (!marker || marker.getBoundingClientRect().width <= 0) return;

        const row = doc.querySelector(
            '[data-testid="stHorizontalBlock"]:has(.delay-prediction-filter-panel-marker)'
        );
        if (!row) return;

        const recommendationHeight = cssPx("--delay-prediction-recommendation-height", 190);
        const sectionGap = cssPx("--delay-prediction-section-gap", 14);
        const shellHeight = Math.max(
            520,
            win.innerHeight - row.getBoundingClientRect().top - BOTTOM_PADDING
        );
        const gaugeHeight = Math.max(
            280,
            shellHeight - recommendationHeight - sectionGap
        );

        doc.documentElement.style.setProperty(
            "--delay-prediction-shell-height",
            shellHeight + "px"
        );
        doc.documentElement.style.setProperty(
            "--delay-prediction-gauge-height",
            gaugeHeight + "px"
        );
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
        });
    });
    scheduleSync();
})();
</script>
"""


def render_delay_prediction_layout_sync() -> None:
    """Inject zero-height iframe that syncs delay prediction height CSS variables."""
    components.html(_HEIGHT_SYNC_SCRIPT, height=0, scrolling=False)
