from datetime import date, time

import numpy as np
import pytest

from api.services import prediction_service


class PassthroughPreprocessor:
    def transform(self, frame):
        return frame


class FixedProbabilityModel:
    def predict_proba(self, _):
        return np.array([[0.55, 0.45]])


def _bundle():
    categorical = [
        "OP_UNIQUE_CARRIER",
        "ORIGIN",
        "DEST",
        "SEASON",
        "TIME_OF_DAY",
        "FLIGHT_DISTANCE_CATEGORY",
    ]
    numerical = [
        "MONTH",
        "DAY_OF_WEEK",
        "DISTANCE",
        "CRS_ELAPSED_TIME",
        "DEP_HOUR",
        "DEP_MINUTE",
        "ARR_HOUR",
        "ARR_MINUTE",
        "IS_WEEKEND",
        "AIRLINE_HIST_DELAY_RATE",
        "ORIGIN_HIST_DELAY_RATE",
        "DEST_HIST_DELAY_RATE",
        "ROUTE_HIST_DELAY_RATE",
    ]
    return {
        "model": FixedProbabilityModel(),
        "preprocessor": PassthroughPreprocessor(),
        "model_name": "XGBoost",
        "decision_threshold": 0.20,
        "risk_thresholds": {
            "medium": 0.20,
            "high": 0.4095,
            "critical": 0.4820,
        },
        "categorical_features": categorical,
        "numerical_features": numerical,
        "inference_reference": {
            "as_of_date": "2025-10-31",
            "global_delay_rate": 0.22,
            "airline_delay_rates": {"DL": 0.18},
            "origin_delay_rates": {"ATL": 0.19},
            "destination_delay_rates": {"ORD": 0.24},
            "route_delay_rates": {"ATL|ORD": 0.21},
            "route_schedule": {
                "ATL|ORD": {
                    "distance": 606.0,
                    "scheduled_elapsed_time": 135.0,
                }
            },
        },
    }


def test_predict_delay_uses_frozen_thresholds_and_references(monkeypatch):
    monkeypatch.setattr(prediction_service, "load_model_bundle", _bundle)

    result = prediction_service.predict_delay(
        {
            "airline": "dl",
            "flight_number": "215",
            "origin": "atl",
            "destination": "ord",
            "flight_date": date(2026, 8, 25),
            "scheduled_departure": time(8, 0),
            "scheduled_arrival": time(10, 30),
        }
    )

    assert result["probability"] == 0.45
    assert result["predicted_delayed"] is True
    assert result["risk_level"] == "HIGH"
    assert result["decision_threshold"] == 0.20
    assert result["reference_as_of"] == "2025-10-31"


def test_predict_delay_rejects_unknown_route(monkeypatch):
    monkeypatch.setattr(prediction_service, "load_model_bundle", _bundle)

    try:
        prediction_service.predict_delay(
            {
                "airline": "DL",
                "flight_number": None,
                "origin": "ATL",
                "destination": "LAX",
                "flight_date": date(2026, 8, 25),
                "scheduled_departure": time(8, 0),
                "scheduled_arrival": time(10, 30),
            }
        )
    except ValueError as error:
        assert "ATL-LAX" in str(error)
    else:
        raise AssertionError("Unknown routes must fail explicitly.")


def test_predict_delay_rejects_implausible_schedule(monkeypatch):
    monkeypatch.setattr(prediction_service, "load_model_bundle", _bundle)
    try:
        prediction_service.predict_delay(
            {"airline": "DL", "flight_number": None, "origin": "ATL",
             "destination": "ORD", "flight_date": date(2026, 8, 25),
             "scheduled_departure": time(8, 0),
             "scheduled_arrival": time(22, 30)}
        )
    except ValueError as error:
        assert "not plausible" in str(error)
    else:
        raise AssertionError("Implausible schedules must fail explicitly.")


def test_serving_contract_is_required(monkeypatch):
    monkeypatch.setattr(prediction_service, "load_model_bundle", _bundle)

    with pytest.raises(RuntimeError, match="no training-serving parity contract"):
        prediction_service.validate_serving_contract()


def test_serving_contract_mismatch_fails(monkeypatch):
    bundle = _bundle()
    columns = bundle["categorical_features"] + bundle["numerical_features"]
    bundle["serving_contract"] = [
        {
            "model_input": {column: 0 for column in columns},
            "expected_probability": 0.40,
        }
    ]
    monkeypatch.setattr(prediction_service, "load_model_bundle", lambda: bundle)

    with pytest.raises(RuntimeError, match="Training-serving parity failed"):
        prediction_service.validate_serving_contract()
