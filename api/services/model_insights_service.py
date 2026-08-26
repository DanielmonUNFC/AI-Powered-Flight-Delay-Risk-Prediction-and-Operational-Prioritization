"""Databricks-backed payload builder for the Model Insights tab."""

from __future__ import annotations

import time
from typing import Any

from api.core.config import get_settings
from api.db.databricks import execute_queries


settings = get_settings()

DEFAULT_INSIGHTS_LIMIT = 10
MAX_INSIGHTS_LIMIT = 50
MODEL_INSIGHTS_CACHE_TTL_SECONDS = 300

_model_insights_cache: dict[int, dict[str, Any]] = {}


def _normalize_limit(limit: int) -> int:
    """Clamp the number of displayed features to a safe range."""
    if limit < 1:
        return DEFAULT_INSIGHTS_LIMIT
    return min(limit, MAX_INSIGHTS_LIMIT)


def _row_value(row: dict[str, Any], key: str) -> Any:
    """Read a Databricks result column regardless of driver casing."""
    if key in row:
        return row[key]

    normalized_key = key.casefold()
    for column_name, value in row.items():
        if column_name.casefold() == normalized_key:
            return value
    raise KeyError(key)


def _build_global_query(limit: int) -> str:
    return f"""
        SELECT
            feature,
            importance
        FROM {settings.insights_table_full_name}
        WHERE feature IS NOT NULL
          AND importance IS NOT NULL
        ORDER BY importance DESC, feature ASC
        LIMIT {limit}
    """


def _build_local_query(limit: int) -> str:
    return f"""
        SELECT
            model_name,
            row_index,
            flight_date,
            airline,
            flight_number,
            origin,
            destination,
            decision_threshold,
            delay_probability,
            predicted_class,
            actual_class,
            shap_output_scale,
            base_value,
            base_probability,
            `rank`,
            feature,
            feature_column,
            shap_value,
            absolute_shap,
            effect_direction
        FROM {settings.local_insights_table_full_name}
        ORDER BY `rank` ASC
        LIMIT {limit}
    """


def _map_global_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": rank,
            "feature": str(_row_value(row, "feature")),
            "importance": float(_row_value(row, "importance")),
        }
        for rank, row in enumerate(rows, start=1)
    ]


def _map_local_explanation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise RuntimeError(
            "The local SHAP explanation table is empty. Run Notebook 09."
        )

    first = rows[0]
    airline = str(_row_value(first, "airline"))
    flight_number = int(_row_value(first, "flight_number"))
    contributions = [
        {
            "rank": int(_row_value(row, "rank")),
            "feature": str(_row_value(row, "feature")),
            "feature_column": str(_row_value(row, "feature_column")),
            "contribution": float(_row_value(row, "shap_value")),
            "absolute_contribution": float(
                _row_value(row, "absolute_shap")
            ),
            "effect_direction": str(_row_value(row, "effect_direction")),
        }
        for row in rows
    ]

    return {
        "model_name": str(_row_value(first, "model_name")),
        "flight_id": f"{airline} {flight_number}",
        "flight_date": str(_row_value(first, "flight_date"))[:10],
        "airline": airline,
        "flight_number": flight_number,
        "origin": str(_row_value(first, "origin")),
        "destination": str(_row_value(first, "destination")),
        "decision_threshold": float(
            _row_value(first, "decision_threshold")
        ),
        "predicted_probability": float(
            _row_value(first, "delay_probability")
        ),
        "predicted_class": int(_row_value(first, "predicted_class")),
        "actual_class": int(_row_value(first, "actual_class")),
        "base_value": float(_row_value(first, "base_value")),
        "base_probability": float(_row_value(first, "base_probability")),
        "output_scale": str(_row_value(first, "shap_output_scale")),
        "contributions": contributions,
    }


def get_model_insights_data(
    limit: int = DEFAULT_INSIGHTS_LIMIT,
) -> dict[str, Any]:
    """Load the complete Model Insights payload through one SQL connection."""
    safe_limit = _normalize_limit(limit)
    now = time.time()
    cached_entry = _model_insights_cache.get(safe_limit)
    if cached_entry is not None and now < cached_entry["expires_at"]:
        return cached_entry["payload"]

    global_rows, local_rows = execute_queries(
        [
            (_build_global_query(safe_limit), None),
            (_build_local_query(safe_limit), None),
        ]
    )
    if not global_rows:
        raise RuntimeError(
            "The global SHAP insights table is empty. Run Notebooks 09 and 11."
        )

    payload = {
        "global_importance": _map_global_rows(global_rows),
        "local_explanation": _map_local_explanation(local_rows),
        "source_tables": {
            "global": settings.insights_table_full_name,
            "local": settings.local_insights_table_full_name,
        },
    }
    _model_insights_cache[safe_limit] = {
        "payload": payload,
        "expires_at": now + MODEL_INSIGHTS_CACHE_TTL_SECONDS,
    }
    return payload


def warm_model_insights_cache(
    limit: int = DEFAULT_INSIGHTS_LIMIT,
) -> None:
    """Preload Model Insights data during API startup."""
    get_model_insights_data(limit=limit)
