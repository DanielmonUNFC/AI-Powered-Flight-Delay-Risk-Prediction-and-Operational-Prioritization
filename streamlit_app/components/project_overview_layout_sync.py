"""Sync Project Overview iframe height to the live viewport."""

import streamlit.components.v1 as components

_HEIGHT_SYNC_SCRIPT = """
<script>
(function () {
    const win = window.parent;
    const doc = win.document;
    const BOTTOM_PADDING = 12;
    let timer = null;

    function cssPx(name, fallback) {
        const value = win.getComputedStyle(doc.documentElement).getPropertyValue(name).trim();
        const parsed = parseInt(value, 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function syncHeight() {
        const marker = doc.querySelector(".project-overview-layout-marker");
        if (!marker || marker.getBoundingClientRect().width <= 0) return;

        const iframeContainer = doc.querySelector(
            '[data-testid="element-container"]:has(.project-overview-iframe-marker) + [data-testid="element-container"]'
        );
        const iframe = iframeContainer ? iframeContainer.querySelector("iframe") : null;
        if (!iframe) return;

        const chromeHeight = cssPx("--project-overview-chrome-height", 230);
        const panelHeight = Math.max(
            680,
            win.innerHeight - chromeHeight - BOTTOM_PADDING
        );

        iframe.style.height = panelHeight + "px";
        iframe.style.minHeight = panelHeight + "px";
    }

    function scheduleSync() {
        if (timer) win.clearTimeout(timer);
        timer = win.setTimeout(syncHeight, 60);
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


def render_project_overview_layout_sync() -> None:
    """Inject zero-height iframe that syncs project overview panel height."""
    components.html(_HEIGHT_SYNC_SCRIPT, height=0, scrolling=False)
