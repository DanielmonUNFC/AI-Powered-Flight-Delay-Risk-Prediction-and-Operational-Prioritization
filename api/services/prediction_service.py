"""Live inference for one scheduled flight using the frozen model bundle."""

from __future__ import annotations

import io
from datetime import date, time
from functools import lru_cache
from typing import Any, Mapping

import joblib
import pandas as pd
from databricks.sdk import WorkspaceClient

from api.core.config import get_settings
from api.db.databricks import execute_queries


settings = get_settings()

REQUIRED_BUNDLE_KEYS = {
    "model",
    "preprocessor",
    "model_name",
    "decision_threshold",
    "risk_thresholds",
    "categorical_features",
    "numerical_features",
    "inference_reference",
}

RECOMMENDATIONS = {
    "LOW": "Routine Monitoring",
    "MEDIUM": "Increased Operational Monitoring",
    "HIGH": "Priority Operational Review",
    "CRITICAL": "Immediate Operational Assessment",
}

# Scheduled arrival is expressed in the destination's local time. This broad
# tolerance allows domestic time-zone differences while rejecting implausible
# schedules such as a 14-hour clock gap for a two-hour route.
MAX_SCHEDULE_DEVIATION_MINUTES = 420

SEASONS = {
    1: "Winter",
    2: "Winter",
    3: "Spring",
    4: "Spring",
    5: "Spring",
    6: "Summer",
    7: "Summer",
    8: "Summer",
    9: "Fall",
    10: "Fall",
    11: "Fall",
    12: "Winter",
}


def _workspace_host() -> str:
    hostname = settings.databricks_server_hostname.strip().rstrip("/")
    if hostname.startswith(("http://", "https://")):
        return hostname
    return f"https://{hostname}"


@lru_cache(maxsize=1)
def load_model_bundle() -> dict[str, Any]:
    """Download and cache the final model bundle from the Databricks Volume."""
    client = WorkspaceClient(
        host=_workspace_host(),
        token=settings.databricks_access_token,
        auth_type="pat",
    )
    response = client.files.download(settings.databricks_model_bundle_path)
    if response.contents is None:
        raise RuntimeError("The model bundle download returned no content.")

    bundle = joblib.load(io.BytesIO(response.contents.read()))
    if not isinstance(bundle, dict):
        raise RuntimeError("The saved model bundle has an invalid format.")

    missing = sorted(REQUIRED_BUNDLE_KEYS - set(bundle))
    if missing:
        raise RuntimeError(
            "The model bundle is not ready for live inference. "
            f"Missing entries: {missing}. Run Notebook 08 again."
        )
    return bundle


def _row_value(row: dict[str, Any], key: str) -> Any:
    for column, value in row.items():
        if column.lower() == key.lower():
            return value
    raise KeyError(key)


@lru_cache(maxsize=1)
def get_prediction_options() -> dict[str, Any]:
    """Return real airline and airport options supported by the model bundle."""
    bundle = load_model_bundle()
    reference = bundle["inference_reference"]
    supported_airlines = set(reference["airline_delay_rates"])
    supported_airports = {
        airport
        for route in reference["route_schedule"]
        for airport in route.split("|", maxsplit=1)
    }

    airline_rows, airport_rows = execute_queries(
        [
            (
                f"SELECT Code, Description FROM "
                f"{settings.airlines_lookup_table_full_name}",
                None,
            ),
            (
                f"SELECT Code, Description FROM "
                f"{settings.airports_lookup_table_full_name}",
                None,
            ),
        ]
    )

    airlines = sorted(
        (
            {
                "code": str(_row_value(row, "Code")),
                "name": str(_row_value(row, "Description")),
            }
            for row in airline_rows
            if str(_row_value(row, "Code")) in supported_airlines
        ),
        key=lambda item: item["name"],
    )
    airports = sorted(
        (
            {
                "code": str(_row_value(row, "Code")),
                "name": str(_row_value(row, "Description")),
            }
            for row in airport_rows
            if str(_row_value(row, "Code")) in supported_airports
        ),
        key=lambda item: item["name"],
    )

    supported_routes = sorted(reference["route_schedule"])
    return {
        "airlines": airlines,
        "airports": airports,
        "routes": [
            {"origin": route.split("|", 1)[0], "destination": route.split("|", 1)[1]}
            for route in supported_routes
        ],
        "airline_routes": reference.get("airline_routes", {}),
        "model_name": bundle["model_name"],
        "reference_as_of": reference["as_of_date"],
    }


def _time_of_day(hour: int) -> str:
    if hour <= 5:
        return "Overnight"
    if hour <= 11:
        return "Morning"
    if hour <= 16:
        return "Afternoon"
    if hour <= 20:
        return "Evening"
    return "Night"


def _distance_category(distance: float) -> str:
    if distance < 500:
        return "Short"
    if distance <= 1500:
        return "Medium"
    return "Long"


def _risk_level(probability: float, thresholds: Mapping[str, Any]) -> str:
    if probability >= float(thresholds["critical"]):
        return "CRITICAL"
    if probability >= float(thresholds["high"]):
        return "HIGH"
    if probability >= float(thresholds["medium"]):
        return "MEDIUM"
    return "LOW"


def _build_feature_row(
    payload: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> dict[str, Any]:
    airline = str(payload["airline"]).strip().upper()
    origin = str(payload["origin"]).strip().upper()
    destination = str(payload["destination"]).strip().upper()
    flight_date: date = payload["flight_date"]
    departure: time = payload["scheduled_departure"]
    arrival: time = payload["scheduled_arrival"]

    if origin == destination:
        raise ValueError("Origin and destination must be different airports.")

    reference = bundle["inference_reference"]
    route_key = f"{origin}|{destination}"
    route_schedule = reference["route_schedule"].get(route_key)
    if route_schedule is None:
        raise ValueError(
            f"Route {origin}-{destination} is not available in the model reference."
        )
    if airline not in reference["airline_delay_rates"]:
        raise ValueError(
            f"Airline {airline} is not available in the model reference."
        )

    airline_routes = reference.get("airline_routes")
    if airline_routes:
        supported = set(airline_routes.get(airline, []))
        if route_key not in supported:
            raise ValueError(
                f"Airline {airline} has no training reference for route "
                f"{origin}-{destination}. Select a supported combination."
            )

    departure_minutes = departure.hour * 60 + departure.minute
    arrival_minutes = arrival.hour * 60 + arrival.minute
    expected_elapsed = float(route_schedule["scheduled_elapsed_time"])
    clock_gap = arrival_minutes - departure_minutes
    plausible_gaps = (clock_gap - 1440, clock_gap, clock_gap + 1440)
    closest_gap = min(plausible_gaps, key=lambda value: abs(value - expected_elapsed))
    if abs(closest_gap - expected_elapsed) > MAX_SCHEDULE_DEVIATION_MINUTES:
        raise ValueError(
            "The scheduled departure and arrival times are not plausible for "
            f"route {origin}-{destination}. The historical scheduled duration "
            f"is approximately {expected_elapsed:.0f} minutes."
        )

    global_rate = float(reference["global_delay_rate"])
    distance = float(route_schedule["distance"])
    return {
        "OP_UNIQUE_CARRIER": airline,
        "ORIGIN": origin,
        "DEST": destination,
        "SEASON": SEASONS[flight_date.month],
        "TIME_OF_DAY": _time_of_day(departure.hour),
        "FLIGHT_DISTANCE_CATEGORY": _distance_category(distance),
        "MONTH": flight_date.month,
        "DAY_OF_WEEK": flight_date.isoweekday(),
        "DISTANCE": distance,
        "CRS_ELAPSED_TIME": float(route_schedule["scheduled_elapsed_time"]),
        "DEP_HOUR": departure.hour,
        "DEP_MINUTE": departure.minute,
        "ARR_HOUR": arrival.hour,
        "ARR_MINUTE": arrival.minute,
        "IS_WEEKEND": int(flight_date.isoweekday() in (6, 7)),
        "AIRLINE_HIST_DELAY_RATE": float(
            reference["airline_delay_rates"].get(airline, global_rate)
        ),
        "ORIGIN_HIST_DELAY_RATE": float(
            reference["origin_delay_rates"].get(origin, global_rate)
        ),
        "DEST_HIST_DELAY_RATE": float(
            reference["destination_delay_rates"].get(destination, global_rate)
        ),
        "ROUTE_HIST_DELAY_RATE": float(
            reference["route_delay_rates"].get(route_key, global_rate)
        ),
    }


def predict_delay(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Score one scheduled flight and return its operational risk category."""
    bundle = load_model_bundle()
    feature_row = _build_feature_row(payload, bundle)
    model_columns = (
        list(bundle["categorical_features"])
        + list(bundle["numerical_features"])
    )
    missing = sorted(set(model_columns) - set(feature_row))
    if missing:
        raise RuntimeError(f"Unable to construct model features: {missing}")

    model_input = pd.DataFrame([feature_row], columns=model_columns)
    encoded = bundle["preprocessor"].transform(model_input)
    probability = float(bundle["model"].predict_proba(encoded)[0, 1])
    decision_threshold = float(bundle["decision_threshold"])
    risk_level = _risk_level(probability, bundle["risk_thresholds"])

    reference_as_of = date.fromisoformat(
        str(bundle["inference_reference"]["as_of_date"])
    )
    is_temporal_extrapolation = payload["flight_date"] > reference_as_of
    return {
        "airline": str(payload["airline"]).strip().upper(),
        "flight_number": payload.get("flight_number"),
        "origin": str(payload["origin"]).strip().upper(),
        "destination": str(payload["destination"]).strip().upper(),
        "flight_date": payload["flight_date"].isoformat(),
        "probability": probability,
        "probability_pct": f"{probability:.1%}",
        "predicted_delayed": probability >= decision_threshold,
        "decision_threshold": decision_threshold,
        "risk_level": risk_level,
        "recommended_action": RECOMMENDATIONS[risk_level],
        "model_name": bundle["model_name"],
        "reference_as_of": reference_as_of.isoformat(),
        "is_temporal_extrapolation": is_temporal_extrapolation,
        "provenance_note": (
            "Prediction uses schedule-time inputs and historical reference rates "
            f"available through {reference_as_of.isoformat()}."
        ),
    }


def validate_serving_contract() -> None:
    """Verify that the serialized preprocessing and model pipeline is stable."""
    bundle = load_model_bundle()
    contract = bundle.get("serving_contract")
    if not contract:
        raise RuntimeError(
            "The model bundle has no training-serving parity contract. "
            "Run Notebook 08 again."
        )
    columns = list(bundle["categorical_features"]) + list(bundle["numerical_features"])
    for index, case in enumerate(contract, start=1):
        frame = pd.DataFrame([case["model_input"]], columns=columns)
        encoded = bundle["preprocessor"].transform(frame)
        actual = float(bundle["model"].predict_proba(encoded)[0, 1])
        expected = float(case["expected_probability"])
        if abs(actual - expected) > 1e-10:
            raise RuntimeError(
                f"Training-serving parity failed for contract case {index}: "
                f"expected {expected}, received {actual}."
            )


def warm_prediction_model() -> None:
    """Load the model bundle during API startup."""
    load_model_bundle()
    validate_serving_contract()
