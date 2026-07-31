"""Live operational summary panel for the prioritization tab."""

from __future__ import annotations

import html

import streamlit as st

from components.panel_header import panel_header_html
from config.panel_icons import ICON_LIVE_SUMMARY


def _kpi_card_html(
    label: str,
    value: str,
    *,
    variant: str,
    prefix: str = "",
) -> str:
    prefix_html = (
        f'<span class="prioritization-kpi__prefix">{html.escape(prefix)}</span> '
        if prefix
        else ""
    )
    return f"""
        <div class="surface-card prioritization-kpi prioritization-kpi--{variant}">
            <div class="prioritization-kpi__label">
                {prefix_html}{html.escape(label)}:
            </div>
            <div class="prioritization-kpi__value">{html.escape(value)}</div>
        </div>
    """


def render_prioritization_summary_panel(summary: dict[str, str]) -> None:
    """Render the bordered summary strip with four glowing KPI cards."""
    cards_html = "".join(
        [
            _kpi_card_html(
                "Flights Analyzed",
                summary["flights_analyzed"],
                variant="monitored",
            ),
            _kpi_card_html(
                "Critical Risk",
                summary["critical_risk"],
                variant="critical",
                prefix="●",
            ),
            _kpi_card_html(
                "High Risk",
                summary["high_risk"],
                variant="high",
                prefix="▲",
            ),
            _kpi_card_html(
                "Flights Selected",
                summary["flights_selected"],
                variant="selected",
                prefix="◉",
            ),
        ]
    )

    st.markdown(
        f"""
        <div class="prioritization-summary-panel">
            {panel_header_html(
                "Operational Prioritization Summary",
                ICON_LIVE_SUMMARY,
                header_action="ⓘ",
            )}
            <div class="prioritization-summary-grid">
                {cards_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
