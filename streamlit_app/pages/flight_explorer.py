import streamlit as st
import pandas as pd
from typing import Optional

from charts.explorer_charts import (
    build_filtered_flight_log_table,
    build_top_delayed_routes_table,
    create_airline_performance_figure,
)
from components.explorer_layout_sync import render_explorer_layout_sync
from components.chart_panel import render_chart_panel
from components.filter_panel import render_explorer_filters
from components.table_panel import render_table_panel
from config.panel_icons import ICON_AIRLINE_CHART, ICON_FLIGHT_LOG, ICON_ROUTES
from services.prototype_data import get_explorer_data
from styles.theme import COMPACT_PANEL_HEIGHT


def render_flight_explorer_page(df: Optional[pd.DataFrame] = None) -> None:
    """Render the Flight Explorer analytics tab."""
    if df is None:
        df = get_explorer_data()

    st.markdown(
        """
        <div class="page-subtitle page-subtitle--explorer">
            Historical Flight Performance & Route Drill-down Analytics
        </div>
        <span class="explorer-layout-marker"></span>
        """,
        unsafe_allow_html=True,
    )

    # Mock layout:
    # | Filters (left, full height) | Chart + Routes (top right)     |
    # |                             | Filtered Flight Log (bottom right)|
    col_filters, col_main = st.columns([1, 3.2], gap="medium")

    with col_filters:
        st.markdown('<span class="explorer-filter-panel-marker"></span>', unsafe_allow_html=True)
        filtered_df = render_explorer_filters(df)

    with col_main:
        st.markdown('<span class="explorer-main-panel-marker"></span>', unsafe_allow_html=True)

        col_chart, col_routes = st.columns([1.8, 1.2], gap="medium")

        with col_chart:
            st.markdown('<span class="explorer-top-panel"></span>', unsafe_allow_html=True)
            airline_figure = create_airline_performance_figure(filtered_df)
            if airline_figure is not None:
                render_chart_panel(
                    "Airline Performance Comparison (Filtered)",
                    ICON_AIRLINE_CHART,
                    airline_figure,
                )
            else:
                render_table_panel(
                    "Airline Performance Comparison (Filtered)",
                    ICON_AIRLINE_CHART,
                    pd.DataFrame(),
                    height=COMPACT_PANEL_HEIGHT,
                )

        with col_routes:
            st.markdown('<span class="explorer-top-panel"></span>', unsafe_allow_html=True)
            render_table_panel(
                "Top Delayed Routes (Filtered)",
                ICON_ROUTES,
                build_top_delayed_routes_table(filtered_df),
                height=COMPACT_PANEL_HEIGHT,
            )

        st.markdown(
            '<span class="explorer-flight-log-marker"></span>',
            unsafe_allow_html=True,
        )
        render_table_panel(
            "Filtered Flight Log (Detailed)",
            ICON_FLIGHT_LOG,
            build_filtered_flight_log_table(filtered_df),
            scrollable=True,
            row_class_col="_row_class",
            header_action="ⓘ",
        )

    render_explorer_layout_sync()
