"""Recalculate Flight Explorer panel heights from the live viewport.

CSS sets the layout; this script only updates --explorer-shell-height and
--explorer-flight-log-height when the window is resized or tabs change.
Column offset uses --explorer-main-margin-top from explorer.css (no JS margin).
"""

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
        const marker = doc.querySelector(".explorer-layout-marker");
        if (!marker || marker.getBoundingClientRect().width <= 0) return;

        const row = doc.querySelector(
            '[data-testid="stHorizontalBlock"]:has(.explorer-filter-panel-marker)'
        );
        if (!row) return;

        const compactHeight = cssPx("--explorer-compact-height", 360);
        const sectionGap = cssPx("--explorer-section-gap", 15);
        const mainMarginTop = cssPx("--explorer-main-margin-top", 22);
        const shellHeight = Math.max(
            420,
            win.innerHeight - row.getBoundingClientRect().top - BOTTOM_PADDING
        );
        const logHeight = Math.max(
            160,
            shellHeight - compactHeight - sectionGap - mainMarginTop
        );

        doc.documentElement.style.setProperty("--explorer-shell-height", shellHeight + "px");
        doc.documentElement.style.setProperty("--explorer-flight-log-height", logHeight + "px");
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


def render_explorer_layout_sync() -> None:
    """Inject zero-height iframe that syncs explorer height CSS variables."""
    components.html(_HEIGHT_SYNC_SCRIPT, height=0, scrolling=False)
