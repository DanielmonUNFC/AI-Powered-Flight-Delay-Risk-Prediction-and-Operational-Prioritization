"""Structured fact cards for the Project Overview tab."""

from __future__ import annotations

import html

from components.info_panel import build_info_panel_html
from config.project_info import FactCardSection


def build_fact_card_panel_html(
    section: FactCardSection,
    *,
    panel_class: str = "project-info-panel--fact",
) -> str:
    """Build a compact key-value fact card panel."""
    rows = []
    for fact in section.facts:
        label = html.escape(fact.label)
        value = html.escape(fact.value)
        rows.append(
            '<div class="project-fact__row">'
            f'<span class="project-fact__label">{label}</span>'
            f'<span class="project-fact__value">{value}</span>'
            "</div>"
        )

    body_html = f'<div class="project-fact">{"".join(rows)}</div>'
    return build_info_panel_html(
        title=section.title,
        icon_id=section.icon_id,
        body_html=body_html,
        panel_class=panel_class,
    )
