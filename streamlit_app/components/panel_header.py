"""Shared panel header markup with SVG icons."""

from __future__ import annotations

import html

from utils.dashboard_icons import panel_icon_svg


def panel_header_html(
    title: str,
    icon_id: str,
    *,
    header_action: str = "",
) -> str:
    """Build a surface-panel header row with a line-icon and optional action."""
    safe_title = html.escape(title.upper())
    icon_html = panel_icon_svg(icon_id)
    action_html = (
        f'<span class="surface-panel-card__header-action">{html.escape(header_action)}</span>'
        if header_action
        else ""
    )
    return (
        f'<div class="surface-panel-card__header">'
        f'<span class="surface-panel-card__header-title">'
        f'<span class="panel-icon">{icon_html}</span>'
        f"<span>{safe_title}</span></span>"
        f"{action_html}</div>"
    )
