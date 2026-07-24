"""Prescriptive flight prioritization mock engine (Notebook 08 + 10 alignment)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config.prioritization import (
    CAPACITY_K_OPTIONS,
    CRITICAL_RISK_COUNT,
    DEFAULT_CAPACITY_K,
    FLIGHTS_ANALYZED,
    HIGH_RISK_COUNT,
    MAX_FLIGHTS_PER_AIRLINE,
    MAX_FLIGHTS_PER_AIRPORT,
    RISK_RECOMMENDATIONS,
    SHAP_MAIN_DRIVERS,
)


@dataclass(frozen=True)
class PrioritizationSummary:
    """Operational summary metrics for the prioritization tab."""

    flights_analyzed: int
    critical_risk: int
    high_risk: int
    flights_selected: int
    capacity_k: int


_FLIGHT_POOL: tuple[dict[str, object], ...] = (
    {"Flight": "AA1204", "Airline": "AA", "Origin": "KDFW", "Destination": "KORD", "SchedDep": "19:15", "DelayProb": 0.884},
    {"Flight": "DL882", "Airline": "DL", "Origin": "KATL", "Destination": "KLGA", "SchedDep": "18:40", "DelayProb": 0.812},
    {"Flight": "UA441", "Airline": "UA", "Origin": "KORD", "Destination": "KLAX", "SchedDep": "20:05", "DelayProb": 0.776},
    {"Flight": "WN903", "Airline": "WN", "Origin": "KDEN", "Destination": "KATL", "SchedDep": "17:55", "DelayProb": 0.748},
    {"Flight": "AA318", "Airline": "AA", "Origin": "KJFK", "Destination": "KMIA", "SchedDep": "21:10", "DelayProb": 0.721},
    {"Flight": "DL1190", "Airline": "DL", "Origin": "KATL", "Destination": "KORD", "SchedDep": "16:30", "DelayProb": 0.698},
    {"Flight": "UA772", "Airline": "UA", "Origin": "KSFO", "Destination": "KSEA", "SchedDep": "18:15", "DelayProb": 0.672},
    {"Flight": "WN214", "Airline": "WN", "Origin": "KORD", "Destination": "KDEN", "SchedDep": "19:45", "DelayProb": 0.655},
    {"Flight": "AA905", "Airline": "AA", "Origin": "KDFW", "Destination": "KLAX", "SchedDep": "20:30", "DelayProb": 0.631},
    {"Flight": "DL556", "Airline": "DL", "Origin": "KATL", "Destination": "KBOS", "SchedDep": "17:20", "DelayProb": 0.608},
    {"Flight": "UA118", "Airline": "UA", "Origin": "KORD", "Destination": "KATL", "SchedDep": "15:50", "DelayProb": 0.594},
    {"Flight": "AA742", "Airline": "AA", "Origin": "KDFW", "Destination": "KMIA", "SchedDep": "14:35", "DelayProb": 0.581},
    {"Flight": "DL331", "Airline": "DL", "Origin": "KATL", "Destination": "KDFW", "SchedDep": "13:10", "DelayProb": 0.568},
    {"Flight": "WN512", "Airline": "WN", "Origin": "KDEN", "Destination": "KORD", "SchedDep": "12:45", "DelayProb": 0.552},
    {"Flight": "UA903", "Airline": "UA", "Origin": "KSFO", "Destination": "KORD", "SchedDep": "11:20", "DelayProb": 0.539},
    {"Flight": "AA611", "Airline": "AA", "Origin": "KJFK", "Destination": "KORD", "SchedDep": "10:55", "DelayProb": 0.526},
    {"Flight": "DL204", "Airline": "DL", "Origin": "KATL", "Destination": "KLAX", "SchedDep": "09:40", "DelayProb": 0.514},
    {"Flight": "UA655", "Airline": "UA", "Origin": "KORD", "Destination": "KDEN", "SchedDep": "08:25", "DelayProb": 0.501},
    {"Flight": "WN778", "Airline": "WN", "Origin": "KDEN", "Destination": "KLAX", "SchedDep": "22:10", "DelayProb": 0.488},
    {"Flight": "AA890", "Airline": "AA", "Origin": "KDFW", "Destination": "KATL", "SchedDep": "07:15", "DelayProb": 0.472},
    {"Flight": "DL445", "Airline": "DL", "Origin": "KATL", "Destination": "KMIA", "SchedDep": "06:50", "DelayProb": 0.458},
    {"Flight": "UA321", "Airline": "UA", "Origin": "KSFO", "Destination": "KLAX", "SchedDep": "23:05", "DelayProb": 0.441},
    {"Flight": "WN102", "Airline": "WN", "Origin": "KORD", "Destination": "KATL", "SchedDep": "05:30", "DelayProb": 0.428},
    {"Flight": "AA507", "Airline": "AA", "Origin": "KJFK", "Destination": "KDFW", "SchedDep": "04:45", "DelayProb": 0.415},
    {"Flight": "DL990", "Airline": "DL", "Origin": "KATL", "Destination": "KSEA", "SchedDep": "03:20", "DelayProb": 0.402},
    {"Flight": "B6118", "Airline": "B6", "Origin": "KJFK", "Destination": "KBOS", "SchedDep": "18:05", "DelayProb": 0.647},
    {"Flight": "B6440", "Airline": "B6", "Origin": "KBOS", "Destination": "KFLL", "SchedDep": "16:20", "DelayProb": 0.623},
    {"Flight": "AS812", "Airline": "AS", "Origin": "KSEA", "Destination": "KSFO", "SchedDep": "15:05", "DelayProb": 0.601},
    {"Flight": "AS219", "Airline": "AS", "Origin": "KSFO", "Destination": "KPDX", "SchedDep": "14:10", "DelayProb": 0.587},
    {"Flight": "NK451", "Airline": "NK", "Origin": "KFLL", "Destination": "KATL", "SchedDep": "13:25", "DelayProb": 0.571},
    {"Flight": "NK908", "Airline": "NK", "Origin": "KLAS", "Destination": "KORD", "SchedDep": "12:00", "DelayProb": 0.558},
    {"Flight": "F9721", "Airline": "F9", "Origin": "KDEN", "Destination": "KPHX", "SchedDep": "11:35", "DelayProb": 0.544},
    {"Flight": "F9332", "Airline": "F9", "Origin": "KPHX", "Destination": "KDFW", "SchedDep": "10:20", "DelayProb": 0.531},
    {"Flight": "AA144", "Airline": "AA", "Origin": "KCLT", "Destination": "KORD", "SchedDep": "09:05", "DelayProb": 0.517},
    {"Flight": "DL733", "Airline": "DL", "Origin": "KMSP", "Destination": "KATL", "SchedDep": "08:40", "DelayProb": 0.504},
    {"Flight": "UA889", "Airline": "UA", "Origin": "KIAD", "Destination": "KORD", "SchedDep": "07:55", "DelayProb": 0.491},
    {"Flight": "WN667", "Airline": "WN", "Origin": "KHOU", "Destination": "KDAL", "SchedDep": "06:35", "DelayProb": 0.476},
    {"Flight": "B6771", "Airline": "B6", "Origin": "KMCO", "Destination": "KJFK", "SchedDep": "22:40", "DelayProb": 0.463},
    {"Flight": "AS550", "Airline": "AS", "Origin": "KPDX", "Destination": "KSEA", "SchedDep": "21:25", "DelayProb": 0.449},
)


def normalize_capacity_k(capacity_k: int) -> int:
    """Return a supported operational capacity value."""
    if capacity_k in CAPACITY_K_OPTIONS:
        return capacity_k
    return DEFAULT_CAPACITY_K


def get_prioritization_pool() -> pd.DataFrame:
    """Return the ranked high-risk flight pool used for prescriptive selection."""
    rows = []
    for entry in _FLIGHT_POOL:
        delay_prob = float(entry["DelayProb"])
        risk_level = _classify_risk_level(delay_prob)
        flight_id = str(entry["Flight"])
        rows.append(
            {
                "Flight": flight_id,
                "Airline": str(entry["Airline"]),
                "Origin": str(entry["Origin"]),
                "Destination": str(entry["Destination"]),
                "SchedDep": str(entry["SchedDep"]),
                "DelayProb": delay_prob,
                "RiskLevel": risk_level,
                "PriorityScore": int(round(delay_prob * 100)),
                "Recommendation": RISK_RECOMMENDATIONS[risk_level],
                "ShapMainDriver": _assign_shap_driver(flight_id),
            }
        )

    pool = pd.DataFrame(rows)
    pool = pool[pool["DelayProb"] >= 0.50]
    return pool.sort_values(
        by=["PriorityScore", "DelayProb"],
        ascending=[False, False],
    ).reset_index(drop=True)


def build_prioritization_summary(
    *,
    capacity_k: int,
    selected_count: int,
) -> PrioritizationSummary:
    """Build summary KPI values for the prioritization tab."""
    return PrioritizationSummary(
        flights_analyzed=FLIGHTS_ANALYZED,
        critical_risk=CRITICAL_RISK_COUNT,
        high_risk=HIGH_RISK_COUNT,
        flights_selected=selected_count,
        capacity_k=normalize_capacity_k(capacity_k),
    )


def optimize_flight_selection(
    pool: pd.DataFrame,
    *,
    capacity_k: int,
    max_per_airport: int = MAX_FLIGHTS_PER_AIRPORT,
    max_per_airline: int = MAX_FLIGHTS_PER_AIRLINE,
) -> pd.Series:
    """
    Greedy OR-Tools-style selection under capacity and diversification constraints.

    Flights are considered in descending priority score order. A flight is selected
    when capacity remains and airport/airline limits are not exceeded.
    """
    target_k = normalize_capacity_k(capacity_k)
    selected_flags = pd.Series(False, index=pool.index, dtype=bool)
    airline_counts: dict[str, int] = {}
    airport_counts: dict[str, int] = {}
    selected_total = 0

    for index, row in pool.iterrows():
        if selected_total >= target_k:
            break

        airline = str(row["Airline"])
        origin = str(row["Origin"])
        if airline_counts.get(airline, 0) >= max_per_airline:
            continue
        if airport_counts.get(origin, 0) >= max_per_airport:
            continue

        selected_flags.loc[index] = True
        airline_counts[airline] = airline_counts.get(airline, 0) + 1
        airport_counts[origin] = airport_counts.get(origin, 0) + 1
        selected_total += 1

    return selected_flags


def build_prioritization_ranking(
    pool: pd.DataFrame | None = None,
    *,
    capacity_k: int = DEFAULT_CAPACITY_K,
) -> pd.DataFrame:
    """Return the ranked table with selection flags for the current capacity K."""
    if pool is None:
        pool = get_prioritization_pool()

    if pool.empty:
        return pd.DataFrame()

    ranking = pool.copy()
    selected_flags = optimize_flight_selection(ranking, capacity_k=capacity_k)
    ranking["Selected"] = selected_flags
    ranking["Priority"] = range(1, len(ranking) + 1)
    return ranking


def format_summary_values(summary: PrioritizationSummary) -> dict[str, str]:
    """Format summary metrics for UI rendering."""
    return {
        "flights_analyzed": f"{summary.flights_analyzed:,}",
        "critical_risk": str(summary.critical_risk),
        "high_risk": str(summary.high_risk),
        "flights_selected": str(summary.flights_selected),
        "capacity_k": str(summary.capacity_k),
    }


def _classify_risk_level(delay_prob: float) -> str:
    if delay_prob >= 0.80:
        return "CRITICAL"
    if delay_prob >= 0.50:
        return "HIGH"
    if delay_prob >= 0.30:
        return "MEDIUM"
    return "LOW"


def _assign_shap_driver(flight_id: str) -> str:
    seed = sum(ord(character) for character in flight_id)
    return SHAP_MAIN_DRIVERS[seed % len(SHAP_MAIN_DRIVERS)]
