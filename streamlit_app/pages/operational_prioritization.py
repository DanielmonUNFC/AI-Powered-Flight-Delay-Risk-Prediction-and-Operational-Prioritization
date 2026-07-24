"""Operational Prioritization page."""

from __future__ import annotations

import streamlit as st

from charts.prioritization_charts import (
    build_priority_ranking_table,
    build_table_footer,
    prioritization_table_styles,
)
from components.prioritization_controls import render_prioritization_controls
from components.prioritization_layout_sync import render_prioritization_layout_sync
from components.prioritization_summary_panel import render_prioritization_summary_panel
from components.table_panel import render_table_panel
from config.panel_icons import ICON_PRIORITY_RANKING
from services.prioritization_engine import (
    build_prioritization_ranking,
    build_prioritization_summary,
    format_summary_values,
    get_prioritization_pool,
)


def render_operational_prioritization_page() -> None:
    """Render the Operational Prioritization dashboard tab."""
    st.markdown(
        """
        <div class="page-subtitle page-subtitle--prioritization">
            Prescriptive ranking of high-risk flights for operational review under capacity K
        </div>
        <span class="prioritization-layout-marker"></span>
        """,
        unsafe_allow_html=True,
    )

    capacity_k = render_prioritization_controls()
    pool = get_prioritization_pool()
    ranking = build_prioritization_ranking(pool, capacity_k=capacity_k)
    selected_count = int(ranking["Selected"].sum()) if not ranking.empty else 0

    summary = build_prioritization_summary(
        capacity_k=capacity_k,
        selected_count=selected_count,
    )
    render_prioritization_summary_panel(format_summary_values(summary))

    st.markdown(
        '<span class="prioritization-table-marker"></span>',
        unsafe_allow_html=True,
    )
    render_table_panel(
        "Priority Ranking Table",
        ICON_PRIORITY_RANKING,
        build_priority_ranking_table(ranking),
        scrollable=True,
        row_class_col="_row_class",
        header_action="ⓘ",
        extra_css=prioritization_table_styles(),
        footer_text=build_table_footer(
            total_rows=len(ranking),
            selected_rows=selected_count,
            capacity_k=capacity_k,
        ),
    )

    render_prioritization_layout_sync()
