"""Research questions panel for the Project Overview tab."""

from __future__ import annotations

import html

from components.info_panel import build_info_panel_html
from config.project_info import ResearchQuestionsSection


def build_research_questions_panel_html(section: ResearchQuestionsSection) -> str:
    """Build the research questions list panel."""
    items = []
    for question in section.questions:
        code = html.escape(question.code)
        text = html.escape(question.text)
        items.append(
            '<div class="project-rq__item">'
            f'<span class="project-rq__code">{code}</span>'
            f'<span class="project-rq__text">{text}</span>'
            "</div>"
        )

    body_html = f'<div class="project-rq">{"".join(items)}</div>'
    return build_info_panel_html(
        title=section.title,
        icon_id=section.icon_id,
        body_html=body_html,
        panel_class="project-info-panel--research",
    )
