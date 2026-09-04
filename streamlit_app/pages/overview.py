import streamlit as st

from charts.overview_charts import create_delay_causes_figure, create_monthly_trend_figure
from components.chart_panel import render_chart_panel
from components.insight_card import render_insight_card
from components.kpi_card import render_kpi_card
from config.panel_icons import ICON_DELAY_CAUSES, ICON_INSIGHT, ICON_MONTHLY_TREND
from services.overview_data import get_overview_page_data


def render_overview_page() -> None:
    """Render the executive overview dashboard tab."""
    st.markdown(
        """
        <div class="page-subtitle">
            Flight delay risk prediction and operational prioritization • Dataset: BTS 2025 Full Year
        </div>
        """,
        unsafe_allow_html=True,
    )

    overview_data = get_overview_page_data()
    if overview_data is None:
        st.warning("Overview data is unavailable. Verify that the API is running and reachable.")
        return

    kpis = overview_data["kpis"]
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        render_kpi_card("Total Flights", kpis["total_flights"])
    with col2:
        render_kpi_card(
            "Delayed Arrival Rate (15+ min)",
            kpis["avg_delay_rate"],
        )
    with col3:
        render_kpi_card(
            "Average Arrival Delay (minutes)",
            kpis["avg_arr_delay"],
        )
    with col4:
        render_kpi_card("Cancellation Rate", kpis["cancellation_rate"])

    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1.8, 1.2], gap="medium")

    with col_left:
        render_chart_panel(
            "Monthly Delay Rate Trend (2025)",
            ICON_MONTHLY_TREND,
            create_monthly_trend_figure(overview_data["monthly_trend"]),
        )

    with col_right:
        render_chart_panel(
            "Total Delay Minutes by Cause",
            ICON_DELAY_CAUSES,
            create_delay_causes_figure(overview_data["delay_causes"]),
        )

    render_insight_card(
        "Key Operational Insight",
        overview_data["insight_html"],
    )
