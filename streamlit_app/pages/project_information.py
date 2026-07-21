"""Project Information tab — academic and architecture documentation."""

import streamlit as st

from components.info_panel import render_info_panel, render_text_paragraphs
from components.methodology_flow import render_methodology_flow
from components.project_info_layout import render_project_info_row_gap
from components.team_grid import render_team_panel
from components.tech_stack_grid import render_tech_stack_panel
from config.project_info import PROJECT_INFORMATION


def render_project_information_page() -> None:
    """Render the predefined Project Information dashboard tab."""
    content = PROJECT_INFORMATION

    st.markdown(
        '<span class="project-info-layout-marker"></span>',
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns(2, gap="medium")

    with top_left:
        render_info_panel(
            title=content.business_objective.title,
            icon_id=content.business_objective.icon_id,
            body_html=render_text_paragraphs(content.business_objective.paragraphs),
            panel_class="project-info-panel--objective",
        )

    with top_right:
        render_team_panel(content.team)

    render_project_info_row_gap()

    bottom_left, bottom_right = st.columns(2, gap="medium")

    with bottom_left:
        render_methodology_flow(content.methodology, content.methodology_steps)

    with bottom_right:
        render_tech_stack_panel(content.tech_stack)
