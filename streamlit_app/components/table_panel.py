"""Reusable surface card for tabular data panels."""

from typing import Optional

import pandas as pd

from components.surface_card import render_html_panel
from styles.theme import COLORS, COMPACT_PANEL_HEIGHT, EXPLORER_FLIGHT_LOG_FALLBACK_HEIGHT
from styles.typography import typography_css_variables

COMPACT_TABLE_HEIGHT = COMPACT_PANEL_HEIGHT


def _base_table_styles() -> str:
    return f"""
        {typography_css_variables()}
        .surface-table {{
            width: 100%;
            min-width: 920px;
            border-collapse: collapse;
            font-size: var(--font-size-body-sm);
        }}
        .surface-table thead th {{
            background-color: #162032;
            color: {COLORS["text_secondary"]};
            font-weight: 600;
            text-align: left;
            padding: 10px 12px;
            border-bottom: 1px solid {COLORS["border"]};
            white-space: nowrap;
        }}
        .surface-table tbody td {{
            color: {COLORS["text_primary"]};
            padding: 10px 12px;
            border-bottom: 1px solid {COLORS["border"]};
            vertical-align: middle;
        }}
        .surface-table tbody tr:last-child td {{
            border-bottom: none;
        }}
        .surface-table tbody tr:hover td {{
            background-color: rgba(37, 99, 235, 0.08);
        }}
        .flight-link {{
            color: {COLORS["accent_bright"]};
            font-weight: 600;
        }}
        .delay-value {{
            color: {COLORS["danger"]};
            font-weight: 600;
        }}
        .status-critical {{
            color: {COLORS["danger"]};
            font-weight: 700;
        }}
        .status-high {{
            color: #f59e0b;
            font-weight: 700;
        }}
        .status-low {{
            color: {COLORS["success"]};
            font-weight: 700;
        }}
        .row-critical td {{
            background-color: rgba(235, 87, 87, 0.12);
        }}
        .row-high td {{
            background-color: rgba(245, 158, 11, 0.08);
        }}
        @media (max-width: 700px) {{
            .surface-table {{
                min-width: 680px;
                font-size: 0.75rem;
            }}
            .surface-table thead th,
            .surface-table tbody td {{
                padding: 7px 8px;
            }}
            .table-footer {{
                font-size: 0.72rem;
                line-height: 1.35;
            }}
        }}
    """


def _scrollable_table_styles(*, fluid: bool = False) -> str:
    scroll_height_rule = "height: 100%;" if fluid else "max-height: 100%;"
    return f"""
        {_base_table_styles()}
        .table-scroll-wrap {{
            flex: 1;
            min-height: 0;
            {scroll_height_rule}
            overflow-y: auto;
            overflow-x: auto;
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            background-color: rgba(8, 13, 26, 0.35);
        }}
        .table-scroll-wrap thead th {{
            position: sticky;
            top: 0;
            z-index: 2;
        }}
        .table-footer {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px solid {COLORS["border"]};
            color: {COLORS["text_muted"]};
            font-size: var(--font-size-caption);
            flex-shrink: 0;
        }}
    """


def _build_table_html(df: pd.DataFrame, row_class_col: Optional[str] = None) -> str:
    """Build an HTML table, optionally applying row classes from a helper column."""
    display_columns = [column for column in df.columns if column != row_class_col]
    headers = "".join(f"<th>{column}</th>" for column in display_columns)

    rows = []
    for _, row in df.iterrows():
        row_class = row[row_class_col] if row_class_col and row_class_col in row else ""
        class_attr = f' class="{row_class}"' if row_class else ""
        cells = "".join(f"<td>{row[column]}</td>" for column in display_columns)
        rows.append(f"<tr{class_attr}>{cells}</tr>")

    return (
        f'<table class="surface-table"><thead><tr>{headers}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def _scroll_footer(row_count: int, footer_text: str = "") -> str:
    caption = footer_text or f"Showing {row_count} flights · scroll horizontally and vertically to browse"
    return f"""
        <div class="table-footer">
            <span>{caption}</span>
        </div>
    """


def render_table_panel(
    title: str,
    icon_id: str,
    df: pd.DataFrame,
    *,
    height: Optional[int] = None,
    scrollable: bool = False,
    row_class_col: Optional[str] = None,
    header_action: str = "",
    extra_css: str = "",
    footer_text: str = "",
) -> None:
    """Render a dataframe inside the standard surface panel card."""
    if df.empty:
        render_html_panel(
            title=title,
            icon_id=icon_id,
            body_html=f'<p style="color:{COLORS["text_muted"]}; margin:0;">No data available.</p>',
            height=180,
            extra_css=_base_table_styles() + extra_css,
        )
        return

    table_html = _build_table_html(df, row_class_col=row_class_col)
    panel_extra_css = _base_table_styles() + extra_css

    if scrollable:
        panel_height = height or EXPLORER_FLIGHT_LOG_FALLBACK_HEIGHT
        use_fluid_layout = height is None

        render_html_panel(
            title=title,
            icon_id=icon_id,
            body_html=table_html,
            height=panel_height,
            footer_html=_scroll_footer(len(df), footer_text),
            scrollable=True,
            fill_height=True,
            header_action=header_action,
            extra_css=_scrollable_table_styles(fluid=use_fluid_layout) + extra_css,
        )
        return

    render_html_panel(
        title=title,
        icon_id=icon_id,
        body_html=table_html,
        height=height or COMPACT_TABLE_HEIGHT,
        extra_css=panel_extra_css,
    )
