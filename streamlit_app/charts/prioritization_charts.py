"""Operational Prioritization table builders and panel styles."""

from __future__ import annotations

import pandas as pd

from styles.theme import COLORS


def build_priority_ranking_table(ranking_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the selected-flights table with badge styling helpers."""
    if ranking_df.empty:
        return pd.DataFrame()

    display_df = ranking_df.copy()
    display_df["Risk Category"] = display_df["RiskLevel"].apply(_format_risk_cell)
    display_df["Delay Probability"] = display_df["DelayProb"].apply(_format_delay_prob_cell)
    display_df["Recommendation"] = display_df["Recommendation"].apply(_format_recommendation_cell)
    display_df["SHAP Main Driver"] = display_df["ShapMainDriver"].apply(_format_shap_cell)
    display_df["Selection Status"] = display_df["Selected"].apply(_format_selection_cell)
    display_df["_row_class"] = display_df.apply(_format_row_class, axis=1)
    display_df = display_df.rename(columns={"FlightDate": "Flight Date"})

    return display_df[
        [
            "Priority",
            "Flight Date",
            "Flight",
            "Airline",
            "Origin",
            "Destination",
            "SchedDep",
            "Delay Probability",
            "PriorityScore",
            "Risk Category",
            "Recommendation",
            "SHAP Main Driver",
            "Selection Status",
            "_row_class",
        ]
    ]


def prioritization_table_styles() -> str:
    """Return supplemental CSS for prioritization table badges and cells."""
    return f"""
        .surface-table tbody td {{
            padding: 12px 12px;
        }}
        .priority-badge {{
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: var(--font-size-caption);
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            white-space: nowrap;
        }}
        .priority-badge--critical {{
            color: #fecaca;
            background-color: rgba(235, 87, 87, 0.18);
            border: 1px solid rgba(235, 87, 87, 0.55);
        }}
        .priority-badge--high {{
            color: #fde68a;
            background-color: rgba(245, 158, 11, 0.16);
            border: 1px solid rgba(245, 158, 11, 0.45);
        }}
        .priority-badge--medium {{
            color: #dbeafe;
            background-color: rgba(59, 130, 246, 0.14);
            border: 1px solid rgba(96, 165, 250, 0.35);
        }}
        .delay-prob-cell {{
            font-weight: 700;
            white-space: nowrap;
        }}
        .delay-prob-cell--critical {{
            color: {COLORS["danger"]};
        }}
        .delay-prob-cell--high {{
            color: #f59e0b;
        }}
        .delay-prob-cell--medium {{
            color: {COLORS["accent_bright"]};
        }}
        .recommendation-cell {{
            color: {COLORS["text_primary"]};
            font-weight: 600;
            min-width: 240px;
            max-width: 320px;
            white-space: normal;
            line-height: 1.45;
            display: inline-block;
        }}
        .shap-driver-cell {{
            color: {COLORS["accent_bright"]};
            font-weight: 600;
            white-space: nowrap;
        }}
        .selection-badge {{
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: var(--font-size-caption);
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            white-space: nowrap;
        }}
        .selection-badge--selected {{
            color: #bbf7d0;
            background-color: rgba(46, 204, 113, 0.16);
            border: 1px solid rgba(46, 204, 113, 0.45);
        }}
        .selection-badge--not-selected {{
            color: {COLORS["text_muted"]};
            background-color: rgba(100, 116, 139, 0.12);
            border: 1px solid rgba(100, 116, 139, 0.28);
        }}
        .row-not-selected td {{
            opacity: 0.72;
        }}
        .row-selected td {{
            opacity: 1;
        }}
    """


def build_table_footer(
    displayed_count: int,
    selected_count: int,
    queue_size: int,
    capacity_k: int,
) -> str:
    """Build a contextual footer for the selected-flights table."""
    if displayed_count >= selected_count:
        visible_text = f"Showing all {selected_count:,} selected flights"
    else:
        visible_text = (
            f"Showing {displayed_count:,} of {selected_count:,} selected flights"
        )

    return (
        f"{visible_text} for K={capacity_k} · "
        f"ranked from {queue_size:,} high-risk flights in queue"
    )


def _format_risk_cell(risk_level: str) -> str:
    normalized = str(risk_level).upper()
    badge_class = {
        "CRITICAL": "priority-badge--critical",
        "HIGH": "priority-badge--high",
        "MEDIUM": "priority-badge--medium",
    }.get(normalized, "priority-badge--medium")
    return f'<span class="priority-badge {badge_class}">{normalized}</span>'


def _format_delay_prob_cell(delay_prob: float) -> str:
    delay_pct = float(delay_prob) * 100
    if delay_pct >= 80:
        cell_class = "delay-prob-cell--critical"
    elif delay_pct >= 50:
        cell_class = "delay-prob-cell--high"
    else:
        cell_class = "delay-prob-cell--medium"
    return f'<span class="delay-prob-cell {cell_class}">{delay_pct:.1f}%</span>'


def _format_recommendation_cell(recommendation: str) -> str:
    return f'<span class="recommendation-cell">{recommendation}</span>'


def _format_shap_cell(driver: str) -> str:
    return f'<span class="shap-driver-cell">{driver}</span>'


def _format_selection_cell(selected: object) -> str:
    is_selected = bool(selected)
    if is_selected:
        return '<span class="selection-badge selection-badge--selected">Selected</span>'
    return '<span class="selection-badge selection-badge--not-selected">Not Selected</span>'


def _format_row_class(row: pd.Series) -> str:
    classes: list[str] = []
    risk_level = str(row.get("RiskLevel", "")).upper()
    if risk_level == "CRITICAL":
        classes.append("row-critical")
    elif risk_level == "HIGH":
        classes.append("row-high")

    if bool(row.get("Selected")):
        classes.append("row-selected")
    else:
        classes.append("row-not-selected")
    return " ".join(classes)
