"""Placeholder tab layout for upcoming dashboard modules."""

import html

import streamlit as st

from components.panel_header import panel_header_html


def render_placeholder_tab(title: str, icon_id: str, message: str) -> None:
    """Render a consistent placeholder view for tabs under development."""
    safe_message = html.escape(message)
    st.markdown(panel_header_html(title, icon_id), unsafe_allow_html=True)
    st.info(safe_message)
