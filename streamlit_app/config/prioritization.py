"""Operational prioritization configuration aligned with the capstone proposal."""

from typing import Final

CAPACITY_K_OPTIONS: Final[tuple[int, ...]] = (10, 25, 50, 100)
DEFAULT_CAPACITY_K: Final[int] = 25

MAX_FLIGHTS_PER_AIRPORT: Final[int] = 5
MAX_FLIGHTS_PER_AIRLINE: Final[int] = 4

FLIGHTS_ANALYZED: Final[int] = 1240
CRITICAL_RISK_COUNT: Final[int] = 42
HIGH_RISK_COUNT: Final[int] = 118

RISK_RECOMMENDATIONS: Final[dict[str, str]] = {
    "LOW": "Routine Monitoring",
    "MEDIUM": "Increased Operational Monitoring",
    "HIGH": "Priority Operational Review",
    "CRITICAL": "Immediate Operational Assessment",
}

SHAP_MAIN_DRIVERS: Final[tuple[str, ...]] = (
    "Historical Airport Delay",
    "Late Departure Hour",
    "Historical Route Delay",
    "Airline Delay History",
    "Origin Congestion Index",
    "Seasonal Delay Pattern",
    "Weekend Schedule Effect",
)

SESSION_CAPACITY_KEY: Final[str] = "prioritization_capacity_k"
