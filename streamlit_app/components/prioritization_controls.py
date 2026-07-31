"""Operational Prioritization controls for capacity K and constraints."""

from __future__ import annotations

import streamlit as st

from components.panel_header import panel_header_html
from config.panel_icons import ICON_PRIORITIZATION
from config.prioritization import (
    CAPACITY_K_OPTIONS,
    DEFAULT_CAPACITY_K,
    MAX_FLIGHTS_PER_AIRLINE,
    MAX_FLIGHTS_PER_AIRPORT,
    SESSION_CAPACITY_KEY,
)


def initialize_prioritization_state() -> None:
    """Ensure session state defaults exist for prioritization controls."""
    if SESSION_CAPACITY_KEY not in st.session_state:
        st.session_state[SESSION_CAPACITY_KEY] = DEFAULT_CAPACITY_K


def render_prioritization_controls() -> int:
    """Render capacity K selector and optimization constraint summary."""
    initialize_prioritization_state()

    st.markdown(
        '<span class="prioritization-controls-marker"></span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        panel_header_html("Optimization Controls", ICON_PRIORITIZATION),
        unsafe_allow_html=True,
    )

    capacity_column, constraints_column = st.columns([1.15, 1], gap="medium")

    with capacity_column:
        capacity_k = st.select_slider(
            "Operational Capacity (K)",
            options=list(CAPACITY_K_OPTIONS),
            value=int(st.session_state[SESSION_CAPACITY_KEY]),
            help=(
                "Maximum number of high-risk flights selected for operational review "
                "under the current optimization constraints."
            ),
            key="prioritization_capacity_slider",
        )
        st.session_state[SESSION_CAPACITY_KEY] = int(capacity_k)
        st.caption(
            f"Selecting up to {capacity_k} flights from the high-risk queue for "
            "prescriptive operational review."
        )

    with constraints_column:
        st.markdown(
            f"""
            <div class="prioritization-constraints">
                <div class="prioritization-constraints__title">Optimization Constraints</div>
                <div class="prioritization-constraints__grid">
                    <div class="prioritization-constraints__item">
                        <span class="prioritization-constraints__label">Maximum per Airport</span>
                        <span class="prioritization-constraints__value">{MAX_FLIGHTS_PER_AIRPORT}</span>
                    </div>
                    <div class="prioritization-constraints__item">
                        <span class="prioritization-constraints__label">Maximum per Airline</span>
                        <span class="prioritization-constraints__value">{MAX_FLIGHTS_PER_AIRLINE}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return int(capacity_k)
