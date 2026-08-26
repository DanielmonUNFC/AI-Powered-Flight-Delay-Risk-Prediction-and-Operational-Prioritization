"""Tests for the operational prioritization API service."""

from __future__ import annotations

import pytest

from api.services.prioritization_service import _build_rq5_evaluation


def _evaluation_rows() -> list[dict]:
    return [
        {
            "strategy": "Constrained Optimized Selection",
            "effective_capacity_k": 25,
            "captured_delayed_flights": 16.0,
            "random_p_at_least_optimized": None,
        },
        {
            "strategy": "Top-K Probability Baseline",
            "effective_capacity_k": 25,
            "captured_delayed_flights": 15.0,
            "random_p_at_least_optimized": None,
        },
        {
            "strategy": "Random Baseline",
            "effective_capacity_k": 25,
            "captured_delayed_flights": 11.412,
            "random_p_at_least_optimized": 0.0499,
        },
    ]


def test_rq5_evaluation_matches_notebook_rule() -> None:
    result = _build_rq5_evaluation(_evaluation_rows(), capacity_k=25)

    assert result["optimized_delays"] == 16.0
    assert result["simple_rule_delays"] == 15.0
    assert result["random_mean_delays"] == 11.412
    assert result["beats_random"] is True
    assert result["beats_simple_rule"] is True
    assert result["verdict"] == "Supported"


def test_rq5_evaluation_fails_when_strategy_is_missing() -> None:
    with pytest.raises(RuntimeError, match="Missing strategies"):
        _build_rq5_evaluation(_evaluation_rows()[:2], capacity_k=25)
