"""Technology stack grid for Project Information."""

from __future__ import annotations

import html

from components.info_panel import build_info_panel_html
from config.project_info import TechStackSection, tech_icon_path
from utils.media import file_to_data_uri


def _render_tech_item(item) -> str:
    safe_name = html.escape(item.name)
    icon_uri = file_to_data_uri(tech_icon_path(item.icon_key))

    if icon_uri:
        icon_html = (
            f'<img class="project-tech__icon" src="{icon_uri}" '
            f'alt="{safe_name}" loading="lazy" />'
        )
    else:
        initials = html.escape(item.name[:2].upper())
        icon_html = (
            f'<div class="project-tech__icon project-tech__icon--fallback" '
            f'aria-hidden="true">{initials}</div>'
        )

    return (
        f'<div class="project-tech__item">'
        f'<span class="project-tech__icon-wrap">{icon_html}</span>'
        f'<div class="project-tech__label">{safe_name}</div></div>'
    )


def build_tech_stack_panel_html(section: TechStackSection) -> str:
    """Build the technology stack panel HTML."""
    cards = "".join(_render_tech_item(item) for item in section.items)
    body_html = f'<div class="project-tech">{cards}</div>'

    return build_info_panel_html(
        title=section.title,
        icon_id=section.icon_id,
        body_html=body_html,
        panel_class="project-info-panel--tech",
    )


def render_tech_stack_panel(section: TechStackSection) -> None:
    """Render the technology stack panel."""
    st.markdown(build_tech_stack_panel_html(section), unsafe_allow_html=True)
