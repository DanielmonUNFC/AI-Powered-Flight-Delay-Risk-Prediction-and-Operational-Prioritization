"""Unified inline SVG icons for all dashboard tabs."""

from __future__ import annotations

PANEL_ICON_IDS = frozenset({
    "monthly_trend",
    "delay_causes",
    "insight",
    "explorer_filters",
    "airline_chart",
    "routes",
    "flight_log",
    "objective",
    "dataset",
    "prediction_target",
    "research_questions",
    "methodology",
    "team",
    "tech",
    "delay_prediction",
    "model_insights",
    "prioritization",
    "live_summary",
    "priority_ranking",
})

TECH_ICON_IDS = frozenset({
    "databricks",
    "pyspark",
    "python",
    "xgboost",
    "shap",
    "ortools",
    "fastapi",
    "streamlit",
})

_SVG = (
    ' xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
    ' stroke="currentColor" stroke-width="1.75" stroke-linecap="round"'
    ' stroke-linejoin="round" aria-hidden="true"'
)


def panel_icon_svg(icon_id: str) -> str:
    """Return a compact inline SVG for a panel section header."""
    icons = {
        "monthly_trend": (
            f"<svg{_SVG}><path d=\"M3 17l6-6 4 4 8-9\"/>"
            f"<path d=\"M14 6h7v7\"/></svg>"
        ),
        "delay_causes": (
            f"<svg{_SVG}><path d=\"M12 3a9 9 0 1 0 9 9\"/>"
            f"<path d=\"M12 3v9h9\"/></svg>"
        ),
        "insight": (
            f"<svg{_SVG}><path d=\"M9 18h6\"/>"
            f"<path d=\"M10 22h4\"/>"
            f"<path d=\"M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z\"/></svg>"
        ),
        "explorer_filters": (
            f"<svg{_SVG}><circle cx=\"11\" cy=\"11\" r=\"7\"/>"
            f"<path d=\"M20 20l-3.5-3.5\"/>"
            f"<path d=\"M8 11h6M11 8v6\"/></svg>"
        ),
        "airline_chart": (
            f"<svg{_SVG}><path d=\"M4 19V5\"/>"
            f"<path d=\"M4 13h4l3-5 3 8 3-4h3\"/></svg>"
        ),
        "routes": (
            f"<svg{_SVG}><path d=\"M3 6h18\"/>"
            f"<path d=\"M6 3v6M18 3v6\"/>"
            f"<rect x=\"3\" y=\"6\" width=\"18\" height=\"14\" rx=\"2\"/>"
            f"<path d=\"M8 14h8M8 17h5\"/></svg>"
        ),
        "flight_log": (
            f"<svg{_SVG}><path d=\"M2 12h5l2-4 4 8 2-4h7\"/></svg>"
        ),
        "objective": (
            f"<svg{_SVG}><circle cx=\"12\" cy=\"12\" r=\"8\"/>"
            f"<circle cx=\"12\" cy=\"12\" r=\"2.5\"/>"
            f"<path d=\"M12 2.5v2.5M12 19v2.5M4 12H2M22 12h-2\"/></svg>"
        ),
        "dataset": (
            f"<svg{_SVG}><ellipse cx=\"12\" cy=\"7\" rx=\"7.5\" ry=\"3\"/>"
            f"<path d=\"M4.5 7v5c0 1.66 3.36 3 7.5 3s7.5-1.34 7.5-3V7\"/>"
            f"<path d=\"M4.5 12v5c0 1.66 3.36 3 7.5 3s7.5-1.34 7.5-3v-5\"/></svg>"
        ),
        "prediction_target": (
            f"<svg{_SVG}><circle cx=\"12\" cy=\"12\" r=\"8\"/>"
            f"<circle cx=\"12\" cy=\"12\" r=\"4\"/>"
            f"<circle cx=\"12\" cy=\"12\" r=\"1.2\" fill=\"currentColor\" stroke=\"none\"/></svg>"
        ),
        "research_questions": (
            f"<svg{_SVG}><path d=\"M9 4h6a2 2 0 0 1 2 2v11H7V6a2 2 0 0 1 2-2z\"/>"
            f"<path d=\"M7 17h10M9 8h6M9 11h4\"/></svg>"
        ),
        "methodology": (
            f"<svg{_SVG}><rect x=\"3\" y=\"4\" width=\"6\" height=\"5\" rx=\"1.2\"/>"
            f"<rect x=\"15\" y=\"4\" width=\"6\" height=\"5\" rx=\"1.2\"/>"
            f"<rect x=\"9\" y=\"15\" width=\"6\" height=\"5\" rx=\"1.2\"/>"
            f"<path d=\"M6 9v2.5c0 1 1 1.5 3 1.5s3-.5 3-1.5V9M12 12.5V15\"/></svg>"
        ),
        "team": (
            f"<svg{_SVG}><path d=\"M16 19v-1.2a3.2 3.2 0 0 0-3.2-3.2H7.2A3.2 3.2 0 0 0 4 17.8V19\"/>"
            f"<circle cx=\"9.5\" cy=\"8.5\" r=\"2.8\"/>"
            f"<path d=\"M20 19v-1a3 3 0 0 0-2.2-2.9\"/>"
            f"<path d=\"M15.5 4.6a3 3 0 0 1 0 5.8\"/></svg>"
        ),
        "tech": (
            f"<svg{_SVG}><rect x=\"4\" y=\"4\" width=\"7\" height=\"7\" rx=\"1.5\"/>"
            f"<rect x=\"13\" y=\"4\" width=\"7\" height=\"7\" rx=\"1.5\"/>"
            f"<rect x=\"4\" y=\"13\" width=\"7\" height=\"7\" rx=\"1.5\"/>"
            f"<rect x=\"13\" y=\"13\" width=\"7\" height=\"7\" rx=\"1.5\"/></svg>"
        ),
        "delay_prediction": (
            f"<svg{_SVG}><path d=\"M13 2L4 14h7l-1 8 10-14H11l2-6z\"/></svg>"
        ),
        "model_insights": (
            f"<svg{_SVG}><path d=\"M9 3a6 6 0 0 0-3 11.2V17h6v-2.8A6 6 0 0 0 9 3z\"/>"
            f"<path d=\"M9 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z\"/></svg>"
        ),
        "prioritization": (
            f"<svg{_SVG}><path d=\"M12 3 2 20h20L12 3z\"/>"
            f"<path d=\"M12 9v5M12 17h.01\"/></svg>"
        ),
        "live_summary": (
            f"<svg{_SVG}><path d=\"M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z\"/>"
            f"<circle cx=\"12\" cy=\"12\" r=\"2.8\"/></svg>"
        ),
        "priority_ranking": (
            f"<svg{_SVG}><path d=\"M4 6h16M4 12h10M4 18h14\"/>"
            f"<path d=\"M19 11v2M19 17v2\"/></svg>"
        ),
    }
    return icons.get(icon_id, icons["objective"])


def _tech_tile(inner_svg: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" aria-hidden="true">'
        '<rect x="1" y="1" width="46" height="46" rx="11" fill="#121c30" '
        'stroke="#243551" stroke-width="1"/>'
        f'<g transform="translate(24 24)">{inner_svg}</g>'
        "</svg>"
    )


def tech_icon_svg(icon_id: str) -> str:
    """Return a compact inline SVG for a tech stack item."""
    icons = {
        "databricks": _tech_tile(
            '<path fill="#FF3621" d="M-8-4 0-9l8 5v10l-8 5-8-5V1l8-5z"/>'
            '<path fill="#FFFFFF" d="M0-3 4-1v4L0 6-4 3V-2l4-1z"/>'
        ),
        "pyspark": _tech_tile(
            '<path fill="#E25A1C" d="M0-10 9-4.5v11L0 12-9 6.5v-11L0-10z"/>'
            '<circle cx="0" cy="1.5" r="2.2" fill="#FFFFFF"/>'
        ),
        "python": _tech_tile(
            '<path fill="#4B8BBE" d="M-6-7c-3 0-2.8 1.5-2.8 1.5v2.8H-1v.8h-7.2c-2 0-3.2 1.1-3.2 3s1.2 3 3.2 3h1.6v-2.8c0-2 1.8-2 1.8-2H-1v5.8c0 1.2 1 1.6 1.8 1.6.8 0 2.8-.4 2.8-2.8V4.2H2.2v-.8H7c2 0 3.2-1.1 3.2-3s-1.2-3-3.2-3H5.4v2.8c0 2-1.8 2-1.8 2H-1V-7z"/>'
            '<circle cx="-4.5" cy="-4.5" r="1" fill="#FFD43B"/>'
            '<circle cx="3.5" cy="5.5" r="1" fill="#FFD43B"/>'
        ),
        "xgboost": _tech_tile(
            '<circle cx="0" cy="0" r="9" fill="#1A472A"/>'
            '<path stroke="#74B816" stroke-width="1.8" d="M-4 3V-4M0 5V-6M4 2V-2"/>'
            '<path stroke="#74B816" stroke-width="1.8" d="M-4-4h8M-2 3h4"/>'
        ),
        "shap": _tech_tile(
            '<rect x="-9" y="-2" width="4" height="10" rx="1" fill="#1E88E5"/>'
            '<rect x="-2" y="-5" width="4" height="13" rx="1" fill="#42A5F5"/>'
            '<rect x="5" y="-8" width="4" height="16" rx="1" fill="#90CAF9"/>'
        ),
        "ortools": _tech_tile(
            '<rect x="-8" y="-8" width="16" height="16" rx="3" fill="none" '
            'stroke="#4285F4" stroke-width="1.6"/>'
            '<path stroke="#4285F4" stroke-width="1.6" stroke-linecap="round" '
            'd="M-4-4h8M-4 0h5M-4 4h8"/>'
            '<circle cx="5" cy="0" r="1.6" fill="#FBBC04"/>'
        ),
        "fastapi": _tech_tile(
            '<circle cx="0" cy="0" r="9" fill="#009688"/>'
            '<path fill="#FFFFFF" d="M4-6-5 4h3l-2.5 4.5L8-1H5l3-5z"/>'
        ),
        "streamlit": _tech_tile(
            '<path fill="#FF4B4B" d="M0-9c4.5 5.5 7.5 9.5 7.5 13a7.5 7.5 0 1 1-15 0C-7.5-0.5-4.5-3.5 0-9z"/>'
            '<circle cx="0" cy="4" r="2.2" fill="#FFFFFF"/>'
        ),
    }
    return icons.get(icon_id, icons["python"])
