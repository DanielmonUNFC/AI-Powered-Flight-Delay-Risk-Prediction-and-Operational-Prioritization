"""Full-page Project Overview iframe panel."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import streamlit.components.v1 as components

from components.fact_card import build_fact_card_panel_html
from components.info_panel import build_info_panel_html, render_text_paragraphs
from components.methodology_flow import build_methodology_flow_html
from components.research_questions_panel import build_research_questions_panel_html
from components.team_grid import build_team_panel_html
from components.tech_stack_grid import build_tech_stack_panel_html
from config.project_info import ProjectOverviewContent
from styles.typography import typography_css_variables

_OVERVIEW_PANEL_CSS_PATH = (
    Path(__file__).resolve().parent.parent / "styles" / "project_overview_panel.css"
)
_DEFAULT_PANEL_HEIGHT = 760


@lru_cache(maxsize=1)
def _overview_panel_css() -> str:
    try:
        return _OVERVIEW_PANEL_CSS_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(
            f"Unable to load project overview panel CSS from {_OVERVIEW_PANEL_CSS_PATH}."
        ) from exc


def build_project_overview_grid_html(content: ProjectOverviewContent) -> str:
    """Assemble all overview sections into one HTML grid."""
    objective = build_info_panel_html(
        title=content.business_objective.title,
        icon_id=content.business_objective.icon_id,
        body_html=render_text_paragraphs(content.business_objective.paragraphs),
        panel_class="project-info-panel--objective",
    )
    dataset = build_fact_card_panel_html(
        content.dataset,
        panel_class="project-info-panel--dataset",
    )
    target = build_fact_card_panel_html(
        content.prediction_target,
        panel_class="project-info-panel--target",
    )
    research = build_research_questions_panel_html(content.research_questions)
    methodology = build_methodology_flow_html(
        content.methodology,
        content.methodology_steps,
    )
    tech = build_tech_stack_panel_html(content.tech_stack)
    team = build_team_panel_html(content.team)

    return (
        '<div class="project-overview-shell">'
        '<div class="project-overview-grid">'
        f'<div class="project-overview-grid__objective">{objective}</div>'
        f'<div class="project-overview-grid__dataset">{dataset}</div>'
        f'<div class="project-overview-grid__target">{target}</div>'
        f'<div class="project-overview-grid__research">{research}</div>'
        f'<div class="project-overview-grid__methodology">{methodology}</div>'
        f'<div class="project-overview-grid__tech">{tech}</div>'
        f'<div class="project-overview-grid__team">{team}</div>'
        "</div></div>"
    )


def render_project_overview_panel(
    content: ProjectOverviewContent,
    *,
    height: int = _DEFAULT_PANEL_HEIGHT,
) -> None:
    """Render the complete Project Overview layout inside a single iframe."""
    grid_html = build_project_overview_grid_html(content)
    page_styles = f"""
        {typography_css_variables()}
        {_overview_panel_css()}
    """

    height_sync_script = """
    <script>
    (function () {
        function syncFrameHeight() {
            try {
                var frame = window.frameElement;
                if (!frame) return;
                var frameHeight = frame.clientHeight || frame.offsetHeight;
                if (frameHeight <= 0) return;
                document.documentElement.style.height = frameHeight + "px";
                document.body.style.height = frameHeight + "px";
            } catch (error) {
                return;
            }
        }
        window.addEventListener("load", syncFrameHeight);
        window.addEventListener("resize", syncFrameHeight);
        if (window.ResizeObserver && window.frameElement) {
            new ResizeObserver(syncFrameHeight).observe(window.frameElement);
        }
    })();
    </script>
    """

    components.html(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <style>{page_styles}</style>
</head>
<body>
    {grid_html}
    {height_sync_script}
</body>
</html>""",
        height=height,
        scrolling=False,
    )
