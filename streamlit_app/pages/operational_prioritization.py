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
from components.insight_card import render_insight_card
from components.table_panel import render_table_panel
from config.panel_icons import ICON_PRIORITY_RANKING
from services.prioritization_data import (
    format_summary_values,
    get_prioritization_page_data,
)


def render_operational_prioritization_page() -> None:
    """Render the Operational Prioritization dashboard tab."""
    st.markdown(
        """
        <div class="page-subtitle page-subtitle--prioritization">
            Prescriptive selection of high-risk flights for operational review under capacity K
        </div>
        <span class="prioritization-layout-marker"></span>
        """,
        unsafe_allow_html=True,
    )

    capacity_k = render_prioritization_controls()
    page_data = get_prioritization_page_data(capacity_k=capacity_k)
    if page_data is None:
        st.warning(
            "Prioritization data is unavailable. Verify that the API is running, "
            "reachable, and that notebook 10 has populated "
            "flight_prioritization_results."
        )
        return

    ranking, summary, table_meta, rq5_evaluation = page_data

    st.markdown(
        '<span class="prioritization-summary-marker"></span>',
        unsafe_allow_html=True,
    )
    render_prioritization_summary_panel(format_summary_values(summary))
    p_value_text = (
        f"p={rq5_evaluation.random_p_value:.4f}"
        if rq5_evaluation.random_p_value is not None
        else "p-value unavailable"
    )
    effective_capacity_note = (
        ""
        if rq5_evaluation.effective_capacity_k == rq5_evaluation.capacity_k
        else (
            " The diversification constraints permitted only "
            f"{rq5_evaluation.effective_capacity_k} selections."
        )
    )
    render_insight_card(
        f"RQ5 comparison at K={rq5_evaluation.capacity_k}: "
        f"{rq5_evaluation.verdict}",
        (
            f"Optimization captured {rq5_evaluation.optimized_delays:.0f} "
            "actually delayed flights, compared with "
            f"{rq5_evaluation.simple_rule_delays:.0f} using the simple "
            f"Top-K rule and {rq5_evaluation.random_mean_delays:.1f} on "
            f"average under random selection ({p_value_text})."
            f"{effective_capacity_note}"
        ),
    )

    st.markdown(
        '<span class="prioritization-table-marker"></span>',
        unsafe_allow_html=True,
    )
    render_table_panel(
        "Selected Flights for Review",
        ICON_PRIORITY_RANKING,
        build_priority_ranking_table(ranking),
        scrollable=True,
        row_class_col="_row_class",
        header_action="ⓘ",
        extra_css=prioritization_table_styles(),
        footer_text=build_table_footer(
            displayed_count=table_meta.displayed_count,
            selected_count=table_meta.selected_count,
            queue_size=table_meta.queue_size,
            capacity_k=capacity_k,
        ),
    )

    render_prioritization_layout_sync()
