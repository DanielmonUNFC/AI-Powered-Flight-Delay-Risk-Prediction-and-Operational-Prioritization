"""Layout helpers for the Project Information tab."""

from __future__ import annotations

from typing import Optional

import streamlit.components.v1 as components

from styles.theme import PROJECT_INFO_ROW_GAP_PX


def render_project_info_row_gap(height_px: Optional[int] = None) -> None:
    """Insert a reliable vertical gap between Project Information grid rows."""
    gap = PROJECT_INFO_ROW_GAP_PX if height_px is None else height_px
    components.html(
        f'<div style="height:{gap}px;width:100%;margin:0;padding:0;"></div>',
        height=gap,
        scrolling=False,
    )
