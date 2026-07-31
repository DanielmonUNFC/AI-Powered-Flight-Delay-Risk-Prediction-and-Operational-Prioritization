"""Capstone team member grid for Project Information."""

from __future__ import annotations

import html

from components.info_panel import build_info_panel_html
from config.project_info import TeamSection, team_photo_path
from utils.media import file_to_data_uri, render_initials_avatar


def _render_member_card(member) -> str:
    photo_uri = file_to_data_uri(team_photo_path(member))
    safe_name = html.escape(member.name)

    if photo_uri:
        avatar_html = (
            f'<img class="project-team__avatar" src="{photo_uri}" '
            f'alt="{safe_name}" loading="lazy" />'
        )
    else:
        avatar_html = render_initials_avatar(member.name)

    return (
        f'<div class="project-team__member">{avatar_html}'
        f'<div class="project-team__name">{safe_name}</div></div>'
    )


def build_team_panel_html(section: TeamSection) -> str:
    """Build the team members panel HTML."""
    cards = "".join(_render_member_card(member) for member in section.members)
    body_html = f'<div class="project-team project-team--strip">{cards}</div>'

    return build_info_panel_html(
        title=section.title,
        icon_id=section.icon_id,
        body_html=body_html,
        panel_class="project-info-panel--team",
    )


def render_team_panel(section: TeamSection) -> None:
    """Render the team members panel."""
    st.markdown(build_team_panel_html(section), unsafe_allow_html=True)
