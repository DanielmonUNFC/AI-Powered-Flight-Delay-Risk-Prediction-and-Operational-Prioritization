from typing import Any
import time

from api.core.config import get_settings
from api.db.databricks import execute_query


settings = get_settings()

CAPACITY_K_OPTIONS = (10, 25, 50, 100)
DEFAULT_CAPACITY_K = 25
DEFAULT_DISPLAY_LIMIT = 500
MAX_DISPLAY_LIMIT = 2000
PRIORITIZATION_CACHE_TTL_SECONDS = 300

_prioritization_caches: dict[tuple[int, int], dict[str, Any]] = {}


def _normalize_capacity_k(capacity_k: int) -> int:
    """Return a supported operational capacity value."""
    if capacity_k in CAPACITY_K_OPTIONS:
        return capacity_k
    return DEFAULT_CAPACITY_K


def _coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def _row_value(row: dict[str, Any], key: str) -> Any:
    """Read a column regardless of Databricks driver casing."""
    if key in row:
        return row[key]
    lower_key = key.lower()
    for column_name, column_value in row.items():
        if column_name.lower() == lower_key:
            return column_value
    raise KeyError(key)


def _format_flight_date(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    return text[:10]


def _map_ranking_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map a Databricks prioritization row to API JSON field names."""
    return {
        "priority": int(_row_value(row, "priority_rank")),
        "flight": str(_row_value(row, "flight_label")),
        "flight_date": _format_flight_date(_row_value(row, "FL_DATE")),
        "airline": str(_row_value(row, "airline_code")),
        "origin": str(_row_value(row, "origin_airport")),
        "destination": str(_row_value(row, "destination_airport")),
        "sched_dep": str(_row_value(row, "scheduled_departure_text")),
        "delay_prob": float(_row_value(row, "delay_probability")),
        "priority_score": int(_row_value(row, "priority_score")),
        "risk_level": str(_row_value(row, "risk_level")),
        "recommendation": str(_row_value(row, "recommendation")),
        "shap_main_driver": str(_row_value(row, "shap_main_driver")),
        "selected": _coerce_bool(_row_value(row, "selected")),
    }


def _normalize_display_limit(display_limit: int) -> int:
    if display_limit < 1:
        return DEFAULT_DISPLAY_LIMIT
    return min(display_limit, MAX_DISPLAY_LIMIT)



def _build_summary_query() -> str:
    return f"""
        SELECT
            COUNT(*) AS flights_in_queue,
            SUM(
                CASE WHEN UPPER(risk_level) = 'CRITICAL' THEN 1 ELSE 0 END
            ) AS critical_risk,
            SUM(
                CASE WHEN UPPER(risk_level) = 'HIGH' THEN 1 ELSE 0 END
            ) AS high_risk,
            SUM(
                CASE WHEN selected THEN 1 ELSE 0 END
            ) AS flights_selected
        FROM {settings.prioritization_results_table_full_name}
        WHERE capacity_k = ?
    """


def _build_prioritization_query(display_limit: int) -> str:
    return f"""
        SELECT
            priority_rank,
            flight_label,
            FL_DATE,
            airline_code,
            origin_airport,
            destination_airport,
            scheduled_departure_text,
            delay_probability,
            priority_score,
            risk_level,
            recommendation,
            shap_main_driver,
            selected,
            capacity_k
        FROM {settings.prioritization_results_table_full_name}
        WHERE capacity_k = ?
          AND selected = true
        ORDER BY priority_rank ASC
        LIMIT {display_limit}
    """


def _build_evaluation_query() -> str:
    """Return the Notebook 10 comparison used to answer RQ5."""
    return f"""
        SELECT
            strategy,
            effective_capacity_k,
            captured_delayed_flights,
            random_p_at_least_optimized
        FROM {settings.prioritization_evaluation_table_full_name}
        WHERE capacity_k = ?
        ORDER BY strategy
    """


def _build_rq5_evaluation(
    rows: list[dict[str, Any]],
    capacity_k: int,
) -> dict[str, Any]:
    """Build a concise, explicit RQ5 comparison for the dashboard."""
    strategies = {
        str(_row_value(row, "strategy")): row
        for row in rows
    }
    required = {
        "Constrained Optimized Selection",
        "Top-K Probability Baseline",
        "Random Baseline",
    }
    missing = sorted(required - set(strategies))
    if missing:
        raise RuntimeError(
            "The RQ5 evaluation dataset is incomplete. Missing strategies: "
            f"{missing}. Run Notebook 10 again."
        )

    optimized = strategies["Constrained Optimized Selection"]
    simple = strategies["Top-K Probability Baseline"]
    random = strategies["Random Baseline"]
    optimized_delays = float(_row_value(optimized, "captured_delayed_flights"))
    simple_delays = float(_row_value(simple, "captured_delayed_flights"))
    random_mean = float(_row_value(random, "captured_delayed_flights"))
    random_p_value = _row_value(random, "random_p_at_least_optimized")
    random_p_value = (
        float(random_p_value) if random_p_value is not None else None
    )
    beats_random = (
        optimized_delays > random_mean
        and random_p_value is not None
        and random_p_value < 0.05
    )
    beats_simple = optimized_delays > simple_delays

    if beats_random and beats_simple:
        verdict = "Supported"
    elif beats_random:
        verdict = "Partially supported: beats random, not simple rule"
    else:
        verdict = "Not supported"

    return {
        "capacity_k": capacity_k,
        "effective_capacity_k": int(
            _row_value(optimized, "effective_capacity_k")
        ),
        "optimized_delays": optimized_delays,
        "simple_rule_delays": simple_delays,
        "random_mean_delays": random_mean,
        "random_p_value": random_p_value,
        "beats_random": beats_random,
        "beats_simple_rule": beats_simple,
        "verdict": verdict,
    }


def get_prioritization_data(
    capacity_k: int = DEFAULT_CAPACITY_K,
    *,
    display_limit: int = DEFAULT_DISPLAY_LIMIT,
) -> dict[str, Any]:
    """
    Load ranked prioritization results for the Operational Prioritization tab.

    Results are precomputed in notebook 10 for each supported capacity K.
    Summary KPIs are computed in SQL over the full queue; the flights array
    returns only selected flights for the requested K, ordered by priority rank.
    """
    safe_capacity_k = _normalize_capacity_k(capacity_k)
    safe_display_limit = _normalize_display_limit(display_limit)
    cache_key = (safe_capacity_k, safe_display_limit)
    now = time.time()

    cached_entry = _prioritization_caches.get(cache_key)
    if cached_entry is not None and now < cached_entry["expires_at"]:
        return cached_entry["payload"]

    summary_rows = execute_query(
        _build_summary_query(),
        parameters=[safe_capacity_k],
    )
    if not summary_rows:
        raise RuntimeError(
            "The prioritization dataset returned no summary. "
            "Run Notebook 10 again."
        )
    summary_row = summary_rows[0]
    flights_in_queue = int(_row_value(summary_row, "flights_in_queue"))
    if flights_in_queue < 1:
        raise RuntimeError(
            "The prioritization queue is empty. Run Notebook 10 again."
        )
    summary = {
        "flights_in_queue": flights_in_queue,
        "critical_risk": int(_row_value(summary_row, "critical_risk") or 0),
        "high_risk": int(_row_value(summary_row, "high_risk") or 0),
        "flights_selected": int(_row_value(summary_row, "flights_selected") or 0),
        "capacity_k": safe_capacity_k,
    }

    rows = execute_query(
        _build_prioritization_query(safe_display_limit),
        parameters=[safe_capacity_k],
    )
    flights = [_map_ranking_row(row) for row in rows]
    evaluation_rows = execute_query(
        _build_evaluation_query(),
        parameters=[safe_capacity_k],
    )
    rq5_evaluation = _build_rq5_evaluation(
        evaluation_rows,
        safe_capacity_k,
    )

    payload = {
        "capacity_k": safe_capacity_k,
        "flights": flights,
        "count": len(flights),
        "total_count": summary["flights_selected"],
        "queue_size": summary["flights_in_queue"],
        "display_limit": safe_display_limit,
        "summary": summary,
        "rq5_evaluation": rq5_evaluation,
        "source_table": settings.prioritization_results_table_full_name,
        "order_by": "priority_rank ASC",
        "selected_only": True,
    }

    _prioritization_caches[cache_key] = {
        "payload": payload,
        "expires_at": now + PRIORITIZATION_CACHE_TTL_SECONDS,
    }

    return payload


def warm_prioritization_cache(capacity_k: int = DEFAULT_CAPACITY_K) -> None:
    """Preload prioritization data during API startup."""
    get_prioritization_data(capacity_k=capacity_k)
