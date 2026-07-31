"""Shared layout helpers for tab content areas."""

import streamlit as st


def render_tab_top_spacer() -> None:
    """Insert a fixed-height gap below the tab navigation bar."""
    st.markdown(
        '<div class="tab-content-top-spacer" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
