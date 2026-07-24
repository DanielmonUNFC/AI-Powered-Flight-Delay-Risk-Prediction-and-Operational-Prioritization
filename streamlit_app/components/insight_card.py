import html

import streamlit as st

from config.panel_icons import ICON_INSIGHT
from utils.dashboard_icons import panel_icon_svg


def render_insight_card(
    title: str,
    text: str,
    *,
    icon_id: str = ICON_INSIGHT,
) -> None:
    """Render the executive insight banner."""
    safe_title = html.escape(title.upper())
    icon_html = panel_icon_svg(icon_id)
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-card__content">
                <div class="insight-card__title">
                    <span class="panel-icon">{icon_html}</span>
                    <span>{safe_title}</span>
                </div>
                <div class="insight-card__body">{text}</div>
            </div>
            <div class="insight-card__sparkle">✦</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
