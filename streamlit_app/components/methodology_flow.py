"""Methodology flow visualization for Project Information."""

from __future__ import annotations

import html

from components.info_panel import render_info_panel
from config.project_info import InfoSection


def render_methodology_flow(section: InfoSection, steps: tuple[str, ...]) -> None:
    """Render the methodology panel with a horizontal step flow."""
    step_items = []
    for index, step in enumerate(steps):
        safe_step = html.escape(step)
        step_items.append(
            f'<div class="methodology-flow__step">'
            f'<span class="methodology-flow__label">{safe_step}</span></div>'
        )
        if index < len(steps) - 1:
            step_items.append('<span class="methodology-flow__arrow" aria-hidden="true">→</span>')

    body_html = f'<div class="methodology-flow">{"".join(step_items)}</div>'
    render_info_panel(
        title=section.title,
        icon_id=section.icon_id,
        body_html=body_html,
        panel_class="project-info-panel--methodology",
    )
