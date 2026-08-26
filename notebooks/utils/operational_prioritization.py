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

STRATEGY_CONSTRAINED_OPTIMIZED = "Constrained Optimized Selection"
STRATEGY_TOP_K_PROBABILITY = "Top-K Probability Baseline"
STRATEGY_RANDOM_BASELINE = "Random Baseline"


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
    if not (
        0.0 <= medium_threshold <= high_threshold
        < critical_threshold <= 1.0
    ):
        raise ValueError(
            "Risk thresholds must satisfy 0 <= medium <= high "
            "< critical <= 1."
        )
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
    score_column: str = "delay_probability",
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
    score_column: str = "delay_probability",
    max_per_airline: int = 4,
    max_per_airport: int = 5,
) -> pd.Series:
    """Solve the constrained binary selection problem with SciPy MILP."""
    try:
        from scipy.optimize import Bounds, LinearConstraint, milp
        from scipy.sparse import csr_matrix
    except ImportError as exc:
        raise RuntimeError(
            "SciPy MILP is required for the RQ5 optimization comparison."
        ) from exc

    if pool.empty:
        return pd.Series(dtype=bool)

    flight_indexes = list(pool.index)
    position_by_index = {
        index: position for position, index in enumerate(flight_indexes)
    }
    row_indexes: list[int] = []
    column_indexes: list[int] = []
    values: list[float] = []
    upper_bounds: list[float] = []

    def add_constraint(indexes: Iterable[int], upper_bound: int) -> None:
        row = len(upper_bounds)
        for index in indexes:
            row_indexes.append(row)
            column_indexes.append(position_by_index[index])
            values.append(1.0)
        upper_bounds.append(float(upper_bound))

    add_constraint(flight_indexes, capacity_k)
    for _, airline_frame in pool.groupby(airline_column):
        add_constraint(airline_frame.index, max_per_airline)
    for _, origin_frame in pool.groupby(origin_column):
        add_constraint(origin_frame.index, max_per_airport)

    constraint_matrix = csr_matrix(
        (values, (row_indexes, column_indexes)),
        shape=(len(upper_bounds), len(flight_indexes)),
    )
    scores = pool[score_column].astype(float).clip(lower=0).to_numpy()
    result = milp(
        c=-scores,
        integrality=np.ones(len(flight_indexes), dtype=int),
        bounds=Bounds(0.0, 1.0),
        constraints=LinearConstraint(
            constraint_matrix,
            lb=-np.inf,
            ub=np.asarray(upper_bounds),
        ),
        options={"time_limit": 30.0, "presolve": True},
    )

    if not result.success or result.x is None:
        raise RuntimeError(
            "The SciPy MILP solver did not produce a valid prioritization "
            f"solution: {result.message}"
        )

    selected_flags = pd.Series(False, index=pool.index, dtype=bool)
    selected_flags.loc[flight_indexes] = result.x >= 0.5
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


def build_top_k_probability_selection(
    frame: pd.DataFrame,
    *,
    capacity_k: int,
    probability_column: str = "delay_probability",
) -> pd.Series:
    """Select the highest-probability flights without diversification constraints."""
    if frame.empty:
        return pd.Series(dtype=bool)

    top_indexes = (
        frame.sort_values(probability_column, ascending=False)
        .head(capacity_k)
        .index
    )
    selected_flags = pd.Series(False, index=frame.index, dtype=bool)
    selected_flags.loc[top_indexes] = True
    return selected_flags


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


def assign_shap_main_drivers(
    frame: pd.DataFrame,
    global_importance: pd.DataFrame,
    *,
    feature_column: str = "Feature",
    importance_column: str = "MeanAbsSHAP",
    airline_column: str = "airline_code",
    origin_column: str = "origin_airport",
    destination_column: str = "destination_airport",
    departure_window_column: str = "departure_window",
    season_column: str = "season",
    top_n: int = 15,
    fallback_feature: str | None = None,
) -> pd.Series:
    """Map each flight to the best-matching global SHAP driver for its attributes."""
    if global_importance.empty:
        return pd.Series("Unknown", index=frame.index, dtype="object")

    ranked_features = (
        global_importance.sort_values(importance_column, ascending=False)
        .head(top_n)[feature_column]
        .tolist()
    )
    default_feature = fallback_feature or ranked_features[0]

    def _resolve_driver(row: pd.Series) -> str:
        candidate_tokens = [
            str(row.get(airline_column, "")),
            str(row.get(origin_column, "")),
            str(row.get(destination_column, "")),
            str(row.get(departure_window_column, "")),
            str(row.get(season_column, "")),
        ]
        candidate_tokens = [
            token.strip()
            for token in candidate_tokens
            if token and token.lower() != "nan"
        ]

        for feature_name in ranked_features:
            feature_upper = feature_name.upper()
            for token in candidate_tokens:
                if token.upper() in feature_upper:
                    return feature_name
        return default_feature

    return frame.apply(_resolve_driver, axis=1)


def compare_prioritization_strategies(
    pool: pd.DataFrame,
    *,
    capacity_k: int,
    random_seed: int,
    label_column: str = "actual_delay",
    airline_column: str = "airline_code",
    origin_column: str = "origin_airport",
    random_repeats: int = 500,
) -> pd.DataFrame:
    """Compare RQ5 strategies at the same effective review capacity.

    The constrained optimizer can select fewer than the requested capacity
    when diversification limits bind. The simple and random baselines are
    therefore evaluated using the optimizer's actual selection count. Random
    selection is repeated to avoid drawing a conclusion from one lucky draw.
    """
    if random_repeats < 1:
        raise ValueError("random_repeats must be at least 1.")

    prioritized_flags = optimize_flight_selection(
        pool,
        capacity_k=capacity_k,
        airline_column=airline_column,
        origin_column=origin_column,
    )
    effective_capacity = int(prioritized_flags.sum())
    top_k_flags = build_top_k_probability_selection(
        pool,
        capacity_k=effective_capacity,
    )

    rows = []
    for strategy_name, flags in [
        (STRATEGY_CONSTRAINED_OPTIMIZED, prioritized_flags),
        (STRATEGY_TOP_K_PROBABILITY, top_k_flags),
    ]:
        metrics = evaluate_prioritization_scenario(
            pool,
            flags,
            label_column=label_column,
        )
        rows.append(
            {
                "capacity_k": capacity_k,
                "effective_capacity_k": effective_capacity,
                "strategy": strategy_name,
                "random_repeats": random_repeats,
                "captured_delays_ci_low": np.nan,
                "captured_delays_ci_high": np.nan,
                "random_p_at_least_optimized": np.nan,
                **metrics,
            }
        )

    labels = pool[label_column].astype(int).to_numpy()
    population_size = len(labels)
    total_delayed = int(labels.sum())
    random_expected = (
        total_delayed / population_size * effective_capacity
        if population_size > 0
        else 0.0
    )
    random_generator = np.random.default_rng(random_seed)
    random_metrics = []
    for _ in range(random_repeats):
        selected_positions = random_generator.choice(
            population_size,
            size=effective_capacity,
            replace=False,
        )
        captured_delays = int(labels[selected_positions].sum())
        random_metrics.append(
            {
                "population_size": float(population_size),
                "selected_count": float(effective_capacity),
                "total_delayed_flights": float(total_delayed),
                "captured_delayed_flights": float(captured_delays),
                "delay_recall": (
                    captured_delays / total_delayed
                    if total_delayed > 0
                    else 0.0
                ),
                "delay_precision": (
                    captured_delays / effective_capacity
                    if effective_capacity > 0
                    else 0.0
                ),
                "lift_vs_random": (
                    captured_delays / random_expected
                    if random_expected > 0
                    else 0.0
                ),
            }
        )

    random_frame = pd.DataFrame(random_metrics)
    optimized_captured = rows[0]["captured_delayed_flights"]
    random_captured = random_frame["captured_delayed_flights"]
    random_mean = random_frame.mean(numeric_only=True).to_dict()
    rows.append(
        {
            "capacity_k": capacity_k,
            "effective_capacity_k": effective_capacity,
            "strategy": STRATEGY_RANDOM_BASELINE,
            "random_repeats": random_repeats,
            "captured_delays_ci_low": float(random_captured.quantile(0.025)),
            "captured_delays_ci_high": float(random_captured.quantile(0.975)),
            "random_p_at_least_optimized": float(
                (1 + (random_captured >= optimized_captured).sum())
                / (random_repeats + 1)
            ),
            **random_mean,
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
