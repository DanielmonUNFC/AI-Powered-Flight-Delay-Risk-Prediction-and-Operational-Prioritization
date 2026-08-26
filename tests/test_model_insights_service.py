"""Focused tests for the Model Insights API data contract."""

from __future__ import annotations

import os

import pytest


os.environ.setdefault("DATABRICKS_SERVER_HOSTNAME", "example.databricks.com")
os.environ.setdefault("DATABRICKS_HTTP_PATH", "/sql/test")
os.environ.setdefault("DATABRICKS_ACCESS_TOKEN", "test-token")

from api.services import model_insights_service as service  # noqa: E402


def _local_row(rank: int, contribution: float) -> dict:
    return {
        "model_name": "XGBoost",
        "row_index": 4,
        "flight_date": "2025-11-02",
        "airline": "AA",
        "flight_number": 3022,
        "origin": "LGA",
        "destination": "ORD",
        "decision_threshold": 0.20,
        "delay_probability": 0.797,
        "predicted_class": 1,
        "actual_class": 1,
        "shap_output_scale": "XGBoost raw score (log-odds)",
        "base_value": -1.0,
        "base_probability": 0.268941,
        "rank": rank,
        "feature": f"Feature {rank}",
        "feature_column": f"FEATURE_{rank}",
        "shap_value": contribution,
        "absolute_shap": abs(contribution),
        "effect_direction": (
            "Increases risk" if contribution >= 0 else "Decreases risk"
        ),
    }


def test_model_insights_payload_maps_real_shap_rows(monkeypatch: pytest.MonkeyPatch):
    global_rows = [
        {"feature": "Departure hour", "importance": 0.42},
        {"feature": "Origin", "importance": 0.31},
    ]
    local_rows = [_local_row(1, 0.35), _local_row(2, -0.12)]

    monkeypatch.setattr(
        service,
        "execute_queries",
        lambda statements: [global_rows, local_rows],
    )
    service._model_insights_cache.clear()

    payload = service.get_model_insights_data(limit=2)

    assert payload["global_importance"][0] == {
        "rank": 1,
        "feature": "Departure hour",
        "importance": 0.42,
    }
    local = payload["local_explanation"]
    assert local["flight_id"] == "AA 3022"
    assert local["predicted_probability"] == pytest.approx(0.797)
    assert [item["contribution"] for item in local["contributions"]] == [
        pytest.approx(0.35),
        pytest.approx(-0.12),
    ]


def test_model_insights_fails_when_local_table_is_empty(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        service,
        "execute_queries",
        lambda statements: [[{"feature": "Origin", "importance": 0.3}], []],
    )
    service._model_insights_cache.clear()

    with pytest.raises(RuntimeError, match="local SHAP explanation table is empty"):
        service.get_model_insights_data()
