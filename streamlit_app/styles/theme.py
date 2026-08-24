"""Design tokens for Python-rendered panels and charts.

Layout spacing for Flight Explorer lives in styles/explorer.css as CSS variables.
"""

from typing import Final

COLORS: Final[dict[str, str]] = {
    "app_bg": "#080d1a",
    "surface": "#0d1527",
    "surface_elevated": "#111d2e",
    "surface_insight": "#11253e",
    "border": "#1e293b",
    "border_subtle": "#1e2d42",
    "border_insight": "#1e3a5f",
    "text_primary": "#f5f7fa",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "text_label": "#9aa7b8",
    "accent": "#2563eb",
    "accent_bright": "#38bdf8",
    "accent_cyan": "#20c5d8",
    "success": "#2ecc71",
    "danger": "#eb5757",
    "chart_line": "#3b82f6",
    "grid": "#1e293b",
}

CHART_HEIGHT: Final[int] = 320
COMPACT_PANEL_HEIGHT: Final[int] = 400
EXPLORER_COMPACT_PANEL_HEIGHT: Final[int] = 420
EXPLORER_FLIGHT_LOG_MIN_HEIGHT: Final[int] = 320
EXPLORER_FLIGHT_LOG_FALLBACK_HEIGHT: Final[int] = 380
PROJECT_INFO_ROW_GAP_PX: Final[int] = 25

PLOTLY_CONFIG: Final[dict] = {"displayModeBar": False}

PLOTLY_PIE_COLORS: Final[list[str]] = [
    "#2563eb",
    "#00d2ff",
    "#38bdf8",
    "#60a5fa",
]
