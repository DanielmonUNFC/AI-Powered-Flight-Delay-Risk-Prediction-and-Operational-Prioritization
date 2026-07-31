"""Recalculate Operational Prioritization panel heights from the live viewport."""

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
        const marker = doc.querySelector(".prioritization-layout-marker");
        if (!marker || marker.getBoundingClientRect().width <= 0) return;

        const tableMarker = doc.querySelector(".prioritization-table-marker");
        if (!tableMarker) return;

        const tableContainer = tableMarker.closest('[data-testid="element-container"]');
        if (!tableContainer) return;

        const summaryHeight = cssPx("--prioritization-summary-height", 168);
        const controlsHeight = cssPx("--prioritization-controls-height", 132);
        const sectionGap = cssPx("--prioritization-section-gap", 12);
        const chromeHeight = cssPx("--prioritization-chrome-height", 250);
        const shellHeight = Math.max(
            420,
            win.innerHeight - chromeHeight
        );
        const tableHeight = Math.max(
            280,
            shellHeight - summaryHeight - controlsHeight - (sectionGap * 2)
        );

        doc.documentElement.style.setProperty(
            "--prioritization-shell-height",
            shellHeight + "px"
        );
        doc.documentElement.style.setProperty(
            "--prioritization-table-height",
            tableHeight + "px"
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


def render_prioritization_layout_sync() -> None:
    """Inject zero-height iframe that syncs prioritization height CSS variables."""
    components.html(_HEIGHT_SYNC_SCRIPT, height=0, scrolling=False)
