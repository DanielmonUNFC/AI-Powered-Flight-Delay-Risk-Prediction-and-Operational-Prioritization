"""Shared HTML surface card rendering for dashboard panels."""

import streamlit.components.v1 as components

from components.panel_header import panel_header_html
from styles.theme import COLORS
from styles.typography import typography_css_variables


def surface_panel_styles(extra_css: str = "") -> str:
    """Return inline CSS for a standard surface panel card."""
    return f"""
        .surface-panel-card {{
            background-color: {COLORS["surface_elevated"]};
            border: 1px solid {COLORS["border_subtle"]};
            border-radius: 8px;
            padding: 16px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            box-sizing: border-box;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        .surface-panel-card__header {{
            font-size: var(--font-size-overline);
            font-weight: 600;
            color: {COLORS["text_label"]};
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            flex-shrink: 0;
        }}
        .surface-panel-card__header-title {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .panel-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 16px;
            height: 16px;
            color: {COLORS["accent_bright"]};
            flex-shrink: 0;
        }}
        .panel-icon svg {{
            width: 16px;
            height: 16px;
            display: block;
        }}
        .surface-panel-card__header-action {{
            color: {COLORS["text_muted"]};
            font-size: var(--font-size-body-sm);
            cursor: default;
        }}
        .surface-panel-card__body {{
            width: 100%;
            flex: 1;
            min-height: 0;
            display: flex;
            flex-direction: column;
        }}
        @media (max-width: 700px) {{
            .surface-panel-card {{
                padding: 10px 12px;
            }}
            .surface-panel-card__header {{
                margin-bottom: 8px;
                font-size: 0.82rem;
                line-height: 1.25;
                letter-spacing: 0.025em;
            }}
            .surface-panel-card__header-title {{
                gap: 6px;
            }}
            .panel-icon,
            .panel-icon svg {{
                width: 14px;
                height: 14px;
            }}
        }}
        {extra_css}
    """


def render_html_panel(
    title: str,
    icon_id: str,
    body_html: str,
    height: int,
    *,
    footer_html: str = "",
    scrollable: bool = False,
    fill_height: bool = False,
    header_action: str = "",
    extra_css: str = "",
    inline_script: str = "",
) -> None:
    """Render a titled panel with optional scrollable body and footer."""
    header_html = panel_header_html(title, icon_id, header_action=header_action)

    page_styles = f"""
        {typography_css_variables()}
        html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
            overflow: hidden;
            height: 100%;
            font-size: var(--font-size-body-sm);
            line-height: var(--line-height-body);
        }}
    """

    if scrollable:
        body_block = f"""
            <div class="surface-panel-card__body">
                <div class="table-scroll-wrap">{body_html}</div>
                {footer_html}
            </div>
        """
    else:
        body_block = f"""
            <div class="surface-panel-card__body">{body_html}</div>
            {footer_html}
        """

    fill_height_script = ""
    if fill_height:
        fill_height_script = """
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

    inline_script_block = f"\n{inline_script}" if inline_script else ""

    components.html(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <style>
        {page_styles}
        {surface_panel_styles(extra_css)}
    </style>
</head>
<body>
    <div class="surface-panel-card">
        {header_html}
        {body_block}
    </div>
    {fill_height_script}{inline_script_block}
</body>
</html>""",
        height=height,
        scrolling=False,
    )
