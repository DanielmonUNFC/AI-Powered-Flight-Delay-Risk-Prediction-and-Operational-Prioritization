import streamlit as st

from charts.overview_charts import create_delay_causes_figure, create_monthly_trend_figure
from components.chart_panel import render_chart_panel
from components.insight_card import render_insight_card
from components.kpi_card import render_kpi_card
from config.panel_icons import ICON_DELAY_CAUSES, ICON_INSIGHT, ICON_MONTHLY_TREND
from services.prototype_data import (
    get_delay_causes_breakdown,
    get_monthly_delay_trend,
    get_overview_kpis,
)


def render_overview_page() -> None:
    """Render the executive overview dashboard tab."""
    st.markdown(
        """
        <div class="page-subtitle">
            AI-powered risk prediction and operational decision support • Dataset: BTS 2025 Full Year
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpis = get_overview_kpis()
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        render_kpi_card(
            "Total Flights",
            kpis["total_flights"],
            kpis["total_flights_sub"],
            kpis["total_flights_positive"],
        )
    with col2:
        render_kpi_card(
            "Avg Delay Rate",
            kpis["avg_delay_rate"],
            kpis["avg_delay_sub"],
            kpis["avg_delay_positive"],
        )
    with col3:
        render_kpi_card(
            "Avg Arr Delay",
            kpis["avg_arr_delay"],
            kpis["avg_arr_sub"],
            kpis["avg_arr_positive"],
        )
    with col4:
        render_kpi_card(
            "Cancel Rate",
            kpis["cancel_rate"],
            kpis["cancel_rate_sub"],
            kpis["cancel_rate_positive"],
        )

    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

    trend_df = get_monthly_delay_trend()
    causes_df = get_delay_causes_breakdown()
    col_left, col_right = st.columns([1.8, 1.2], gap="medium")

    with col_left:
        render_chart_panel(
            "Monthly Delay Rate Trend (2025)",
            ICON_MONTHLY_TREND,
            create_monthly_trend_figure(trend_df),
        )

    with col_right:
        render_chart_panel(
            "Total Delay Minutes by Cause",
            ICON_DELAY_CAUSES,
            create_delay_causes_figure(causes_df),
        )

    render_insight_card(
        "Key Operational Insight",
        "Late aircraft propagation and carrier-related operational bottlenecks account for "
        "<b>64.2%</b> of total accumulated delay minutes across major US airport hubs in 2025.",
    )
