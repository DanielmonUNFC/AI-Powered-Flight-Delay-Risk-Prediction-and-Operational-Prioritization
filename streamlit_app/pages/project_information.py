"""Project Overview tab — business context, scope, methodology, and team."""

import streamlit as st

from components.project_overview_layout_sync import render_project_overview_layout_sync
from components.project_overview_panel import render_project_overview_panel
from config.project_info import PROJECT_OVERVIEW


def render_project_information_page() -> None:
    """Render the Project Overview dashboard tab."""
    st.markdown(
        """
        <div class="page-subtitle page-subtitle--project-overview">
            Business context, research scope, methodology, technology, and team
        </div>
        <span class="project-overview-layout-marker"></span>
        <span class="project-overview-iframe-marker"></span>
        """,
        unsafe_allow_html=True,
    )

    render_project_overview_panel(PROJECT_OVERVIEW)
    render_project_overview_layout_sync()
