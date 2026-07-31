"""Operational prioritization helpers for notebooks and downstream apps."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


RISK_RECOMMENDATIONS = {
    "LOW": "Routine Monitoring",
    "MEDIUM": "Increased Operational Monitoring",
    "HIGH": "Priority Operational Review",
    "CRITICAL": "Immediate Operational Assessment",
}


def classify_risk_level(
    delay_probability: float,
    *,
    high_threshold: float = 0.50,
    critical_threshold: float = 0.80,
    medium_threshold: float = 0.30,
) -> str:
    """Map a delay probability to an operational risk band."""
    if delay_probability >= critical_threshold:
        return "CRITICAL"
    if delay_probability >= high_threshold:
        return "HIGH"
    if delay_probability >= medium_threshold:
        return "MEDIUM"
    return "LOW"


def add_operational_scores(
    frame: pd.DataFrame,
    *,
    probability_column: str = "delay_probability",
    high_threshold: float = 0.50,
    critical_threshold: float = 0.80,
    medium_threshold: float = 0.30,
) -> pd.DataFrame:
    """Add risk level, priority score, and recommendation columns."""
    scored = frame.copy()
    scored["risk_level"] = scored[probability_column].astype(float).apply(
        lambda value: classify_risk_level(
            value,
            high_threshold=high_threshold,
            critical_threshold=critical_threshold,
            medium_threshold=medium_threshold,
        )
    )
    scored["priority_score"] = (
        scored[probability_column].astype(float) * 100.0
    ).round().astype(int)
    scored["recommendation"] = scored["risk_level"].map(RISK_RECOMMENDATIONS)
    return scored


def optimize_flight_selection_greedy(
    pool: pd.DataFrame,
    *,
    capacity_k: int,
    airline_column: str = "airline_code",
    origin_column: str = "origin_airport",
    score_column: str = "priority_score",
    max_per_airline: int = 4,
    max_per_airport: int = 5,
) -> pd.Series:
    """Select flights greedily under capacity and diversification constraints."""
    if pool.empty:
        return pd.Series(dtype=bool)

    ordered_pool = pool.sort_values(
        by=[score_column, "delay_probability"],
        ascending=[False, False],
    )
    selected_flags = pd.Series(False, index=ordered_pool.index, dtype=bool)
    airline_counts: dict[str, int] = {}
    airport_counts: dict[str, int] = {}
    selected_total = 0

    for index, row in ordered_pool.iterrows():
        if selected_total >= capacity_k:
            break

        airline = str(row[airline_column])
        origin = str(row[origin_column])
        if airline_counts.get(airline, 0) >= max_per_airline:
            continue
        if airport_counts.get(origin, 0) >= max_per_airport:
            continue

        selected_flags.loc[index] = True
        airline_counts[airline] = airline_counts.get(airline, 0) + 1
        airport_counts[origin] = airport_counts.get(origin, 0) + 1
        selected_total += 1

    return selected_flags.reindex(pool.index, fill_value=False)


def optimize_flight_selection(
    pool: pd.DataFrame,
    *,
    capacity_k: int,
    airline_column: str = "airline_code",
    origin_column: str = "origin_airport",
    score_column: str = "priority_score",
    max_per_airline: int = 4,
    max_per_airport: int = 5,
) -> pd.Series:
    """Select flights using OR-Tools when available, otherwise greedy selection."""
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        return optimize_flight_selection_greedy(
            pool,
            capacity_k=capacity_k,
            airline_column=airline_column,
            origin_column=origin_column,
            score_column=score_column,
            max_per_airline=max_per_airline,
            max_per_airport=max_per_airport,
        )

    if pool.empty:
        return pd.Series(dtype=bool)

    model = cp_model.CpModel()
    flight_indexes = list(pool.index)
    decision_vars = {
        index: model.new_bool_var(f"flight_{position}")
        for position, index in enumerate(flight_indexes)
    }

    model.add(
        sum(decision_vars.values()) <= capacity_k
    )

    for airline, airline_frame in pool.groupby(airline_column):
        model.add(
            sum(decision_vars[index] for index in airline_frame.index)
            <= max_per_airline
        )

    for origin, origin_frame in pool.groupby(origin_column):
        model.add(
            sum(decision_vars[index] for index in origin_frame.index)
            <= max_per_airport
        )

    scaled_scores = (
        pool[score_column].astype(float).clip(lower=0).round().astype(int)
    )
    model.maximize(
        sum(
            int(scaled_scores.loc[index]) * decision_vars[index]
            for index in flight_indexes
        )
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return optimize_flight_selection_greedy(
            pool,
            capacity_k=capacity_k,
            airline_column=airline_column,
            origin_column=origin_column,
            score_column=score_column,
            max_per_airline=max_per_airline,
            max_per_airport=max_per_airport,
        )

    selected_flags = pd.Series(False, index=pool.index, dtype=bool)
    for index in flight_indexes:
        selected_flags.loc[index] = bool(solver.value(decision_vars[index]))
    return selected_flags


def evaluate_prioritization_scenario(
    frame: pd.DataFrame,
    selected_flags: pd.Series,
    *,
    label_column: str = "actual_delay",
) -> dict[str, float]:
    """Summarize how many delayed flights are captured by a selection strategy."""
    working = frame.copy()
    working["selected"] = selected_flags.reindex(working.index, fill_value=False)
    working["actual_delay"] = working[label_column].astype(int)

    total_delayed = int(working["actual_delay"].sum())
    captured_delayed = int(
        working.loc[working["selected"], "actual_delay"].sum()
    )
    selected_count = int(working["selected"].sum())
    population_size = len(working)

    recall = (
        captured_delayed / total_delayed if total_delayed > 0 else 0.0
    )
    precision = (
        captured_delayed / selected_count if selected_count > 0 else 0.0
    )
    random_expected = (
        (total_delayed / population_size) * selected_count
        if population_size > 0
        else 0.0
    )
    lift_vs_random = (
        captured_delayed / random_expected if random_expected > 0 else 0.0
    )

    return {
        "population_size": float(population_size),
        "selected_count": float(selected_count),
        "total_delayed_flights": float(total_delayed),
        "captured_delayed_flights": float(captured_delayed),
        "delay_recall": float(recall),
        "delay_precision": float(precision),
        "lift_vs_random": float(lift_vs_random),
    }


def build_random_selection(
    frame: pd.DataFrame,
    *,
    capacity_k: int,
    random_seed: int,
) -> pd.Series:
    """Create a random baseline selection of the same size as capacity K."""
    if frame.empty:
        return pd.Series(dtype=bool)

    sample_size = min(capacity_k, len(frame))
    selected_indexes = (
        frame.sample(n=sample_size, random_state=random_seed, replace=False)
        .index
    )
    selected_flags = pd.Series(False, index=frame.index, dtype=bool)
    selected_flags.loc[selected_indexes] = True
    return selected_flags


def compare_prioritization_strategies(
    pool: pd.DataFrame,
    *,
    capacity_k: int,
    random_seed: int,
    label_column: str = "actual_delay",
    airline_column: str = "airline_code",
    origin_column: str = "origin_airport",
) -> pd.DataFrame:
    """Compare optimized prioritization against a random baseline for RQ4."""
    prioritized_flags = optimize_flight_selection(
        pool,
        capacity_k=capacity_k,
        airline_column=airline_column,
        origin_column=origin_column,
    )
    random_flags = build_random_selection(
        pool,
        capacity_k=capacity_k,
        random_seed=random_seed,
    )

    rows = []
    for strategy_name, flags in (
        ("Prioritized Selection", prioritized_flags),
        ("Random Baseline", random_flags),
    ):
        metrics = evaluate_prioritization_scenario(
            pool,
            flags,
            label_column=label_column,
        )
        rows.append(
            {
                "capacity_k": capacity_k,
                "strategy": strategy_name,
                **metrics,
            }
        )
    return pd.DataFrame(rows)


def build_ranking_table(
    pool: pd.DataFrame,
    *,
    capacity_k: int,
    airline_column: str = "airline_code",
    origin_column: str = "origin_airport",
) -> pd.DataFrame:
    """Return a ranked prioritization table with selection flags."""
    if pool.empty:
        return pool.copy()

    ranking = pool.sort_values(
        by=["priority_score", "delay_probability"],
        ascending=[False, False],
    ).copy()
    ranking["selected"] = optimize_flight_selection(
        ranking,
        capacity_k=capacity_k,
        airline_column=airline_column,
        origin_column=origin_column,
    )
    ranking["priority_rank"] = range(1, len(ranking) + 1)
    return ranking.reset_index(drop=True)