from __future__ import annotations

import numpy as np
import pandas as pd


def get_overview_kpis() -> dict[str, object]:
    """Return top-level operational metrics for the Overview page."""

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


def get_monthly_delay_trend() -> pd.DataFrame:
    """Return monthly delay-rate performance for 2025."""

    return pd.DataFrame(
        {
            "Month": [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ],
            "DelayRate": [
                18.2,
                16.5,
                19.4,
                17.8,
                20.1,
                28.5,
                27.2,
                23.4,
                15.8,
                16.2,
                17.5,
                29.1,
            ],
        }
    )


def get_delay_causes_breakdown() -> pd.DataFrame:
    """Return accumulated delay-minute distribution by cause."""

    return pd.DataFrame(
        {
            "Cause": [
                "Late Aircraft",
                "Carrier",
                "Weather",
                "NAS",
            ],
            "Percentage": [38, 26, 18, 18],
        }
    )


def get_explorer_data() -> pd.DataFrame:
    """
    Generate a synthetic flight dataset for dashboard prototyping.

    The fixed random seed ensures that the same mock dataset is generated
    on every application run.
    """

    carriers = [
        "Delta Air Lines",
        "American Airlines",
        "United Airlines",
        "Southwest Airlines",
        "JetBlue",
    ]

    origins = [
        "KATL",
        "KORD",
        "KDFW",
        "KDEN",
        "KJFK",
    ]

    destinations = [
        "KLAX",
        "KMIA",
        "KSFO",
        "KBOS",
        "KSEA",
        "KORD",
        "KDFW",
    ]

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    month_probabilities = [
        0.08,
        0.07,
        0.08,
        0.08,
        0.09,
        0.11,
        0.10,
        0.09,
        0.07,
        0.08,
        0.07,
        0.08,
    ]

    rng = np.random.default_rng(42)
    rows: list[dict[str, object]] = []

    for index in range(1, 1001):
        carrier = rng.choice(
            carriers,
            p=[0.30, 0.25, 0.20, 0.15, 0.10],
        )

        origin = rng.choice(
            origins,
            p=[0.35, 0.20, 0.20, 0.15, 0.10],
        )

        valid_destinations = [
            destination
            for destination in destinations
            if destination != origin
        ]

        destination = rng.choice(valid_destinations)
        month = rng.choice(months, p=month_probabilities)

        hour = int(rng.integers(6, 23))
        minute = int(rng.choice([0, 15, 30, 45]))

        if hour < 12:
            departure_window = "Morning"
        elif hour < 18:
            departure_window = "Afternoon"
        else:
            departure_window = "Evening"

        probability = round(float(rng.uniform(0.10, 0.95)), 3)
        status = _classify_risk(probability)

        rows.append(
            {
                "Flight": f"FL-{1000 + index}",
                "Carrier": carrier,
                "Origin": origin,
                "Destination": destination,
                "SchedDep": f"{hour:02d}:{minute:02d}",
                "DepWindow": departure_window,
                "DelayProb": probability,
                "DelayProbPct": f"{probability * 100:.1f}%",
                "Status": status,
                "Month": month,
            }
        )

    return pd.DataFrame(rows)


def get_mock_prediction(
    airline: str,
    origin: str,
    destination: str,
    departure_time: str,
) -> dict[str, object]:
    """
    Return a deterministic mock delay-risk prediction.

    The same set of inputs always produces the same result, which makes the
    prototype predictable during testing and demonstrations.
    """

    seed_text = f"{airline}|{origin}|{destination}|{departure_time}"
    seed_value = sum(ord(character) for character in seed_text)

    rng = np.random.default_rng(seed_value)
    probability = round(float(rng.uniform(0.18, 0.92)), 3)
    risk_level = _classify_risk(probability)

    return {
        "probability": probability,
        "probability_pct": f"{probability * 100:.1f}%",
        "risk_level": risk_level,
        "recommended_action": _recommended_action(risk_level),
    }


def _classify_risk(probability: float) -> str:
    """Convert a delay probability into an operational risk level."""

    if not 0.0 <= probability <= 1.0:
        raise ValueError("Probability must be between 0 and 1.")

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

    try:
        return actions[risk_level]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported risk level: {risk_level}"
        ) from exc

        
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