"""Operational prioritization configuration aligned with the capstone proposal."""

from typing import Final

CAPACITY_K_OPTIONS: Final[tuple[int, ...]] = (10, 25, 50, 100)
DEFAULT_CAPACITY_K: Final[int] = 25

MAX_FLIGHTS_PER_AIRPORT: Final[int] = 5
MAX_FLIGHTS_PER_AIRLINE: Final[int] = 4

SESSION_CAPACITY_KEY: Final[str] = "prioritization_capacity_k"
