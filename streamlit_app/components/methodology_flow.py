"""Methodology flow visualization for Project Information."""

from __future__ import annotations

import html

from components.info_panel import build_info_panel_html
from config.project_info import InfoSection


def build_methodology_flow_html(
    section: InfoSection,
    steps: tuple[str, ...],
) -> str:
    """Build a compact dual-column methodology pipeline diagram."""
    split_index = (len(steps) + 1) // 2
    left_steps = list(enumerate(steps[:split_index], start=1))
    right_steps = list(enumerate(steps[split_index:], start=split_index + 1))

    body_html = (
        '<div class="methodology-pipeline methodology-pipeline--dual">'
        f"{_build_pipeline_column(left_steps, len(steps))}"
        f"{_build_pipeline_column(right_steps, len(steps))}"
        "</div>"
    )
    return build_info_panel_html(
        title=section.title,
        icon_id=section.icon_id,
        body_html=body_html,
        panel_class="project-info-panel--methodology",
    )


def _build_pipeline_column(
    indexed_steps: list[tuple[int, str]],
    total_steps: int,
) -> str:
    """Render one vertical pipeline column."""
    if not indexed_steps:
        return ""

    column_items: list[str] = []
    last_index = indexed_steps[-1][0]

    for index, step in indexed_steps:
        safe_step = html.escape(step)
        step_class = _step_class(index, total_steps)
        column_items.append(
            f"""
            <div class="methodology-pipeline__step {step_class}">
                <div class="methodology-pipeline__card">
                    <span class="methodology-pipeline__index">{index:02d}</span>
                    <span class="methodology-pipeline__label">{safe_step}</span>
                </div>
            </div>
            """
        )
        if index != last_index:
            column_items.append(
                '<div class="methodology-pipeline__connector" aria-hidden="true">'
                '<span class="methodology-pipeline__connector-arrow">↓</span>'
                "</div>"
            )

    return (
        '<div class="methodology-pipeline__column">'
        '<div class="methodology-pipeline__spine" aria-hidden="true"></div>'
        f'{"".join(column_items)}'
        "</div>"
    )


def _step_class(index: int, total_steps: int) -> str:
    """Return accent classes for the first, middle, and final pipeline nodes."""
    if index == 1:
        return "methodology-pipeline__step--start"
    if index == total_steps:
        return "methodology-pipeline__step--finish"
    if index >= total_steps - 2:
        return "methodology-pipeline__step--insight"
    if index >= total_steps - 5:
        return "methodology-pipeline__step--model"
    return "methodology-pipeline__step--core"


def render_methodology_flow(section: InfoSection, steps: tuple[str, ...]) -> None:
    """Render the methodology panel with a vertical step flow."""
    import streamlit as st

    st.markdown(
        build_methodology_flow_html(section, steps),
        unsafe_allow_html=True,
    )
