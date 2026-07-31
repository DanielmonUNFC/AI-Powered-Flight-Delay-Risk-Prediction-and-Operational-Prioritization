"""Reusable panel shell for Project Information sections."""

from __future__ import annotations

import html

import streamlit as st

from components.panel_header import panel_header_html


def build_info_panel_html(
    title: str,
    icon_id: str,
    body_html: str,
    *,
    panel_class: str = "",
) -> str:
    """Build a titled project information panel as HTML."""
    extra_class = f" {panel_class}" if panel_class else ""
    header_html = panel_header_html(title, icon_id)

    return (
        f'<div class="project-info-panel{extra_class}">'
        f"{header_html}"
        f'<div class="project-info-panel__body">{body_html}</div>'
        f"</div>"
    )


def render_info_panel(
    title: str,
    icon_id: str,
    body_html: str,
    *,
    panel_class: str = "",
) -> None:
    """Render a titled surface card with custom HTML body content."""
    st.markdown(
        build_info_panel_html(
            title,
            icon_id,
            body_html,
            panel_class=panel_class,
        ),
        unsafe_allow_html=True,
    )


def render_text_paragraphs(paragraphs: tuple[str, ...]) -> str:
    """Build HTML paragraph blocks from plain-text copy."""
    return "".join(
        f'<p class="project-info-text">{html.escape(paragraph)}</p>'
        for paragraph in paragraphs
    )
