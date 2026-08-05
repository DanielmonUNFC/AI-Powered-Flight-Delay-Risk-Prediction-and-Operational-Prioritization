"""Live operational summary panel for the prioritization tab."""

from __future__ import annotations

import html

import streamlit.components.v1 as components

from components.panel_header import panel_header_html
from config.panel_icons import ICON_LIVE_SUMMARY
from styles.theme import COLORS
from styles.typography import typography_css_variables

_SUMMARY_PANEL_HEIGHT = 168


def _kpi_card_html(
    label: str,
    value: str,
    *,
    variant: str,
    prefix: str = "",
) -> str:
    prefix_html = (
        f'<span class="prioritization-kpi__prefix">{html.escape(prefix)}</span> '
        if prefix
        else ""
    )
    return (
        f'<div class="surface-card prioritization-kpi prioritization-kpi--{variant}">'
        f'<div class="prioritization-kpi__label">'
        f"{prefix_html}{html.escape(label)}:"
        f"</div>"
        f'<div class="prioritization-kpi__value">{html.escape(value)}</div>'
        f"</div>"
    )


def _summary_panel_css() -> str:
    app_font = (
        '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, '
        "Helvetica, Arial, sans-serif"
    )
    return f"""
        html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
            overflow: hidden;
            font-family: {app_font};
            font-size: var(--font-size-body-sm);
            line-height: var(--line-height-body);
        }}
        .prioritization-summary-panel {{
            background-color: {COLORS["surface_elevated"]};
            border: 1px solid {COLORS["border_subtle"]};
            border-radius: 8px;
            padding: 14px 18px 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            box-sizing: border-box;
            height: 100%;
            font-family: {app_font};
        }}
        .prioritization-summary-panel .surface-panel-card__header {{
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
        }}
        .prioritization-summary-panel .surface-panel-card__header-title {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .prioritization-summary-panel .panel-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            color: {COLORS["accent_bright"]};
            flex-shrink: 0;
        }}
        .prioritization-summary-panel .panel-icon svg {{
            width: 18px;
            height: 18px;
            display: block;
        }}
        .prioritization-summary-panel .surface-panel-card__header-action {{
            color: {COLORS["text_muted"]};
            font-size: var(--font-size-body-sm);
        }}
        .prioritization-summary-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
        }}
        .surface-card {{
            background-color: {COLORS["surface_elevated"]};
            border: 1px solid {COLORS["border_subtle"]};
            border-radius: 8px;
            padding: 16px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            box-sizing: border-box;
        }}
        .prioritization-kpi {{
            min-height: 96px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 8px;
            margin-bottom: 0;
        }}
        .prioritization-kpi__label {{
            font-size: var(--font-size-label);
            font-weight: 600;
            color: {COLORS["text_secondary"]};
            line-height: var(--line-height-tight);
        }}
        .prioritization-kpi__value {{
            font-family: "JetBrains Mono", "SF Mono", ui-monospace, monospace;
            font-size: var(--font-size-metric);
            font-weight: 700;
            color: {COLORS["text_primary"]};
            line-height: var(--line-height-tight);
        }}
        .prioritization-kpi--monitored {{
            border-color: rgba(37, 99, 235, 0.45);
            box-shadow:
                0 0 18px rgba(37, 99, 235, 0.16),
                inset 0 0 0 1px rgba(37, 99, 235, 0.12);
        }}
        .prioritization-kpi--critical {{
            border-color: rgba(235, 87, 87, 0.55);
            box-shadow:
                0 0 22px rgba(235, 87, 87, 0.22),
                inset 0 0 0 1px rgba(235, 87, 87, 0.14);
        }}
        .prioritization-kpi--critical .prioritization-kpi__prefix {{
            color: {COLORS["danger"]};
        }}
        .prioritization-kpi--high {{
            border-color: rgba(245, 158, 11, 0.5);
            box-shadow:
                0 0 20px rgba(245, 158, 11, 0.18),
                inset 0 0 0 1px rgba(245, 158, 11, 0.12);
        }}
        .prioritization-kpi--high .prioritization-kpi__prefix {{
            color: #f59e0b;
        }}
        .prioritization-kpi--selected {{
            border-color: rgba(46, 204, 113, 0.45);
            box-shadow:
                0 0 20px rgba(46, 204, 113, 0.16),
                inset 0 0 0 1px rgba(46, 204, 113, 0.12);
        }}
        .prioritization-kpi--selected .prioritization-kpi__prefix {{
            color: {COLORS["success"]};
        }}
    """


def render_prioritization_summary_panel(summary: dict[str, str]) -> None:
    """Render the bordered summary strip with four glowing KPI cards."""
    cards_html = "".join(
        [
            _kpi_card_html(
                "Flights in Queue",
                summary["flights_in_queue"],
                variant="monitored",
            ),
            _kpi_card_html(
                "Critical Risk",
                summary["critical_risk"],
                variant="critical",
                prefix="●",
            ),
            _kpi_card_html(
                "High Risk",
                summary["high_risk"],
                variant="high",
                prefix="▲",
            ),
            _kpi_card_html(
                "Flights Selected",
                summary["flights_selected"],
                variant="selected",
                prefix="◉",
            ),
        ]
    )

    panel_html = (
        '<div class="prioritization-summary-panel">'
        f'{panel_header_html("Operational Prioritization Summary", ICON_LIVE_SUMMARY, header_action="ⓘ")}'
        f'<div class="prioritization-summary-grid">{cards_html}</div>'
        "</div>"
    )

    components.html(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <style>
        {typography_css_variables()}
        {_summary_panel_css()}
    </style>
</head>
<body>
    {panel_html}
</body>
</html>""",
        height=_SUMMARY_PANEL_HEIGHT,
        scrolling=False,
    )
