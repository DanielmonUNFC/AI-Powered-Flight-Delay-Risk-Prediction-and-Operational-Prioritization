import pandas as pd
import numpy as np

from datetime import date, time
from typing import Optional

from services.prediction_features import PredictionFeatures, build_prediction_features


def get_overview_kpis():
    """Returns top-level operational metrics for the Overview page."""
    return {
        "total_flights": "6,842,105",
        "total_flights_sub": "+1.2% YoY",
        "total_flights_positive": True,
        "avg_delay_rate": "21.4%",
        "avg_delay_sub": "+1.8%",
        "avg_delay_positive": False,
        "avg_arr_delay": "18.6 min",
        "avg_arr_sub": "+2.1 min",
        "avg_arr_positive": False,
        "cancel_rate": "1.82%",
        "cancel_rate_sub": "-0.3%",
        "cancel_rate_positive": True,
    }

def get_monthly_delay_trend():
    """Provides monthly delay rate performance for 2025."""
    return pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "DelayRate": [18.2, 16.5, 19.4, 17.8, 20.1, 28.5, 27.2, 23.4, 15.8, 16.2, 17.5, 29.1]
    })

def get_delay_causes_breakdown():
    """Provides accumulated delay minutes distribution by cause."""
    return pd.DataFrame({
        "Cause": ["Late Aircraft", "Carrier", "Weather", "NAS"],
        "Percentage": [38, 26, 18, 18],
    })

def get_explorer_data():
    """Generates a rich synthetic dataset ensuring data presence across common filter combinations."""
    carriers = ["Delta Air Lines", "American Airlines", "United Airlines", "Southwest Airlines", "JetBlue"]
    origins = ["KATL", "KORD", "KDFW", "KDEN", "KJFK"]
    dests = ["KLAX", "KMIA", "KSFO", "KBOS", "KSEA", "KORD", "KDFW"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    rows = []
    np.random.seed(42)
    
    # Generate 1,000 synthetic flight entries
    for i in range(1, 1001):
        carrier = np.random.choice(carriers, p=[0.3, 0.25, 0.2, 0.15, 0.1])
        origin = np.random.choice(origins, p=[0.35, 0.2, 0.2, 0.15, 0.1])
        valid_dests = [d for d in dests if d != origin]
        dest = np.random.choice(valid_dests)
        month = np.random.choice(months, p=[0.08, 0.07, 0.08, 0.08, 0.09, 0.11, 0.1, 0.09, 0.07, 0.08, 0.07, 0.08])
        
        hour = np.random.randint(6, 23)
        minute = int(np.random.choice([0, 15, 30, 45]))
        if hour < 12:
            dep_window = "Morning"
        elif hour < 18:
            dep_window = "Afternoon"
        else:
            dep_window = "Evening"

        prob = round(float(np.random.uniform(0.1, 0.95)), 3)
        status = "CRITICAL" if prob > 0.8 else ("HIGH" if prob > 0.5 else "LOW")

        rows.append({
            "Flight": f"FL-{1000 + i}",
            "Carrier": carrier,
            "Origin": origin,
            "Destination": dest,
            "SchedDep": f"{hour:02d}:{minute:02d}",
            "DepWindow": dep_window,
            "DelayProb": prob,
            "DelayProbPct": f"{prob * 100:.1f}%",
            "Status": status,
            "Month": month,
        })
    return pd.DataFrame(rows)


def get_prioritization_summary() -> dict[str, str]:
    """Backward-compatible summary accessor for prioritization prototypes."""
    from services.prioritization_engine import (
        build_prioritization_summary,
        format_summary_values,
        get_prioritization_pool,
        optimize_flight_selection,
    )
    from config.prioritization import DEFAULT_CAPACITY_K

    pool = get_prioritization_pool()
    selected_count = int(optimize_flight_selection(pool, capacity_k=DEFAULT_CAPACITY_K).sum())
    summary = build_prioritization_summary(
        capacity_k=DEFAULT_CAPACITY_K,
        selected_count=selected_count,
    )
    return format_summary_values(summary)


def get_prioritization_ranking() -> pd.DataFrame:
    """Backward-compatible ranking accessor for prioritization prototypes."""
    from services.prioritization_engine import build_prioritization_ranking
    from config.prioritization import DEFAULT_CAPACITY_K

    return build_prioritization_ranking(capacity_k=DEFAULT_CAPACITY_K)


def get_mock_prediction(
    *,
    airline: str,
    flight_number: Optional[str],
    origin: str,
    destination: str,
    flight_date: date,
    scheduled_departure: time,
    scheduled_arrival: time,
) -> dict[str, object]:
    """
    Return a deterministic mock delay-risk prediction.

    Derived calendar, schedule, route, and historical features are computed
    internally from the visible form inputs.
    """

    features = build_prediction_features(
        airline=airline,
        flight_number=flight_number,
        origin=origin,
        destination=destination,
        flight_date=flight_date,
        scheduled_departure=scheduled_departure,
        scheduled_arrival=scheduled_arrival,
    )

    seed_text = (
        f"{features.airline_code}|{features.origin_code}|{features.destination_code}|"
        f"{features.flight_date.isoformat()}|{features.scheduled_departure.strftime('%H:%M')}|"
        f"{features.scheduled_arrival.strftime('%H:%M')}|{features.flight_number or ''}|"
        f"{features.distance_miles}|{features.historical_delay_rate:.3f}"
    )
    seed_value = sum(ord(character) for character in seed_text)
    rng = np.random.default_rng(seed_value)

    historical_adjustment = (features.historical_delay_rate - 0.20) * 0.35
    season_adjustment = {
        "Winter": 0.04,
        "Spring": -0.01,
        "Summer": 0.06,
        "Fall": 0.01,
    }[features.season]
    weekend_adjustment = 0.03 if features.weekend_indicator == "Weekend" else -0.01
    hour_adjustment = {
        "Morning": -0.03,
        "Afternoon": 0.01,
        "Evening": 0.04,
        "Night": 0.02,
    }[features.departure_hour_category]

    probability = float(
        rng.uniform(0.18, 0.72)
        + historical_adjustment
        + season_adjustment
        + weekend_adjustment
        + hour_adjustment
    )
    probability = round(min(max(probability, 0.08), 0.95), 3)
    risk_level = _classify_risk(probability)

    return {
        "probability": probability,
        "probability_pct": f"{probability * 100:.1f}%",
        "risk_level": risk_level,
        "recommended_action": _recommended_action(risk_level),
        "derived_features": _features_to_dict(features),
    }


def _classify_risk(probability: float) -> str:
    """Convert a delay probability into an operational risk level."""

    if probability < 0.30:
        return "LOW"
    if probability < 0.60:
        return "MEDIUM"
    if probability < 0.80:
        return "HIGH"
    return "CRITICAL"


def _recommended_action(risk_level: str) -> str:
    """Return an operational recommendation for a risk level."""

    actions = {
        "LOW": (
            "Continue standard monitoring and routine departure preparation."
        ),
        "MEDIUM": (
            "Review gate readiness, turnaround progress, and known airport "
            "constraints."
        ),
        "HIGH": (
            "Review aircraft turnaround readiness and verify gate availability "
            "before boarding begins."
        ),
        "CRITICAL": (
            "Escalate the flight for immediate operational review and coordinate "
            "aircraft, crew, gate, and passenger recovery resources."
        ),
    }
    return actions.get(
        risk_level,
        "No operational recommendation is currently available.",
    )


def _features_to_dict(features: PredictionFeatures) -> dict[str, object]:
    """Serialize derived features for future model integration and debugging."""

    return {
        "distance_miles": features.distance_miles,
        "scheduled_elapsed_minutes": features.scheduled_elapsed_minutes,
        "day_of_week": features.day_of_week,
        "quarter": features.quarter,
        "season": features.season,
        "weekend_indicator": features.weekend_indicator,
        "departure_hour_category": features.departure_hour_category,
        "historical_delay_rate": features.historical_delay_rate,
        "historical_delay_rate_pct": f"{features.historical_delay_rate * 100:.1f}%",
    }


def get_global_feature_importance() -> pd.DataFrame:
    """Return mock global SHAP feature importance values."""

    return pd.DataFrame(
        {
            "Feature": [
                "Scheduled Departure Time",
                "Origin Airport Congestion",
                "Historical Route Delay",
                "Late Aircraft History",
                "Carrier Performance",
                "Carrier Route Delay",
                "Distance",
                "Day of Week",
                "Month",
                "Scheduled Arrival Time",
            ],
            "Importance": [
                23.8,
                18.2,
                14.1,
                12.9,
                11.7,
                9.4,
                8.5,
                7.6,
                6.1,
                5.2,
            ],
        }
    )


def get_local_prediction_explanation() -> dict[str, object]:
    """Return a mock local SHAP explanation for one flight."""

    return {
        "flight_id": "DL882",
        "base_probability": 0.31,
        "predicted_probability": 0.742,
        "risk_level": "HIGH",
        "contributions": pd.DataFrame(
            {
                "Feature": [
                    "Late Aircraft History",
                    "Origin Airport Congestion",
                    "Historical Route Delay",
                    "Carrier Performance",
                    "Scheduled Departure Time",
                    "Distance",
                ],
                "Contribution": [
                    0.182,
                    0.124,
                    0.066,
                    -0.043,
                    0.038,
                    -0.015,
                ],
            }
        ),
    }