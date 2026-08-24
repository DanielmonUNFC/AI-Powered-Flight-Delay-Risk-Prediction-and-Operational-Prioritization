"""Recalculate Operational Prioritization panel heights from the live viewport."""

import streamlit.components.v1 as components

_HEIGHT_SYNC_SCRIPT = """
<script>
(function () {
    const win = window.parent;
    const doc = win.document;
    const BOTTOM_PADDING = 12;
    const MIN_TABLE_HEIGHT = 480;
    let timer = null;

    function syncHeights() {
        const marker = doc.querySelector(".prioritization-layout-marker");
        if (!marker || marker.getBoundingClientRect().width <= 0) return;

        const tableMarker = doc.querySelector(".prioritization-table-marker");
        if (!tableMarker) return;

        const tableContainer = tableMarker.closest('[data-testid="element-container"]');
        if (!tableContainer) return;

        const tableTop = tableContainer.getBoundingClientRect().top;
        const tableHeight = Math.max(
            MIN_TABLE_HEIGHT,
            win.innerHeight - tableTop - BOTTOM_PADDING
        );

        doc.documentElement.style.setProperty(
            "--prioritization-table-height",
            tableHeight + "px"
        );

        const iframeContainer = tableContainer.nextElementSibling;
        if (!iframeContainer) return;

        iframeContainer.style.flex = "1 1 auto";
        iframeContainer.style.minHeight = tableHeight + "px";
        iframeContainer.style.height = tableHeight + "px";

        const iframe = iframeContainer.querySelector("iframe");
        if (iframe) {
            iframe.style.height = tableHeight + "px";
            iframe.style.minHeight = tableHeight + "px";
        }
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


def render_prioritization_layout_sync() -> None:
    """Inject zero-height iframe that syncs prioritization height CSS variables."""
    components.html(_HEIGHT_SYNC_SCRIPT, height=0, scrolling=False)
