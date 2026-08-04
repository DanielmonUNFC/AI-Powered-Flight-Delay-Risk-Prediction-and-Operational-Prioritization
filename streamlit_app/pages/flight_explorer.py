import streamlit as st
import pandas as pd
from typing import Optional

from charts.explorer_charts import (
    build_filtered_flight_log_table,
    build_top_delayed_routes_table,
    create_airline_performance_figure,
)
from components.chart_panel import render_chart_panel
from components.explorer_layout_sync import render_explorer_layout_sync
from components.filter_panel import render_explorer_filters
from components.table_panel import render_table_panel
from config.panel_icons import ICON_AIRLINE_CHART, ICON_FLIGHT_LOG, ICON_ROUTES
from config.api_settings import get_api_settings
from services.explorer_data import get_explorer_page_data
from styles.theme import EXPLORER_COMPACT_PANEL_HEIGHT


def render_flight_explorer_page(df: Optional[pd.DataFrame] = None) -> None:
    """Render the Flight Explorer analytics tab."""
    if df is None:
        df = get_explorer_page_data()
        if df is None:
            st.warning(
                "Explorer data is unavailable. Verify that the API is running "
                "and reachable."
            )
            return

    st.markdown(
        """
        <div class="page-subtitle page-subtitle--explorer">
            Historical Flight Performance & Route Drill-down Analytics
        </div>
        <span class="explorer-layout-marker"></span>
        """,
        unsafe_allow_html=True,
    )
    render_explorer_layout_sync()

    col_filters, col_main = st.columns([1.05, 3.95], gap="medium")

    with col_filters:
        st.markdown('<span class="explorer-filter-panel-marker"></span>', unsafe_allow_html=True)
        filtered_df = render_explorer_filters(df)

    with col_main:
        st.markdown('<span class="explorer-main-panel-marker"></span>', unsafe_allow_html=True)

        col_chart, col_routes = st.columns([1.8, 1.2], gap="medium")

        with col_chart:
            st.markdown(
                '<span class="explorer-top-panel explorer-chart-panel-marker"></span>',
                unsafe_allow_html=True,
            )
            chart_body_height = EXPLORER_COMPACT_PANEL_HEIGHT - 52
            airline_figure = create_airline_performance_figure(
                filtered_df,
                chart_height=chart_body_height,
            )
            if airline_figure is not None:
                render_chart_panel(
                    "Airline Predicted Delay Risk (Filtered)",
                    ICON_AIRLINE_CHART,
                    airline_figure,
                    height=EXPLORER_COMPACT_PANEL_HEIGHT,
                )
            else:
                render_table_panel(
                    "Airline Predicted Delay Risk (Filtered)",
                    ICON_AIRLINE_CHART,
                    pd.DataFrame(),
                    height=EXPLORER_COMPACT_PANEL_HEIGHT,
                )

        with col_routes:
            st.markdown(
                '<span class="explorer-top-panel explorer-routes-panel-marker"></span>',
                unsafe_allow_html=True,
            )
            render_table_panel(
                "Top Routes by Predicted Delay Risk (Filtered)",
                ICON_ROUTES,
                build_top_delayed_routes_table(filtered_df),
                height=EXPLORER_COMPACT_PANEL_HEIGHT,
                scrollable=True,
                footer_text="Top routes by peak predicted delay risk · scroll to browse",
                extra_css="""
                    .surface-table {
                        min-width: 0;
                        width: 100%;
                        table-layout: fixed;
                    }
                    .surface-table tbody td:first-child {
                        white-space: normal;
                        line-height: 1.35;
                        font-size: var(--font-size-caption);
                    }
                    .surface-table thead th:nth-child(2),
                    .surface-table tbody td:nth-child(2) {
                        text-align: center;
                        white-space: nowrap;
                        width: 72px;
                    }
                    .surface-table thead th:nth-child(3),
                    .surface-table tbody td:nth-child(3) {
                        text-align: right;
                        white-space: nowrap;
                        width: 110px;
                    }
                """,
            )

        st.markdown(
            '<span class="explorer-flight-log-marker"></span>',
            unsafe_allow_html=True,
        )
        flight_log = build_filtered_flight_log_table(filtered_df)
        api_limit = get_api_settings().explorer_limit
        render_table_panel(
            "Filtered Flight Log (Detailed)",
            ICON_FLIGHT_LOG,
            flight_log,
            scrollable=True,
            row_class_col="_row_class",
            header_action="ⓘ",
            footer_text=(
                f"Showing {len(flight_log)} filtered flights "
                f"(loaded up to {api_limit} from API) · scroll to browse"
            ),
            extra_css="""
                .surface-table thead th {
                    white-space: normal;
                    line-height: 1.2;
                    vertical-align: bottom;
                    font-size: var(--font-size-caption);
                    padding: 8px 10px;
                    max-width: 92px;
                }
                .surface-table tbody td:nth-child(1) {
                    white-space: nowrap;
                    font-size: var(--font-size-caption);
                }
                .surface-table tbody td:nth-child(2),
                .surface-table tbody td:nth-child(3),
                .surface-table tbody td:nth-child(4) {
                    white-space: normal;
                    line-height: 1.35;
                    font-size: var(--font-size-caption);
                    min-width: 120px;
                    max-width: 200px;
                }
                .surface-table thead th:nth-child(7),
                .surface-table tbody td:nth-child(7),
                .surface-table thead th:nth-child(8),
                .surface-table tbody td:nth-child(8) {
                    white-space: nowrap;
                    text-align: center;
                }
            """,
        )
