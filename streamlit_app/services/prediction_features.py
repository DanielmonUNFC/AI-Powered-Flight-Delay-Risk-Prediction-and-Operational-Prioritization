"""Derive model-ready features from Delay Prediction form inputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Optional
import re


_ROUTE_DISTANCE_MILES: dict[tuple[str, str], int] = {
    ("KATL", "KORD"): 606,
    ("KATL", "KLAX"): 1947,
    ("KORD", "KLAX"): 1744,
}

_HISTORICAL_DELAY_RATES: dict[tuple[str, str, str], float] = {
    ("DL", "KATL", "KORD"): 0.22,
    ("DL", "KATL", "KLAX"): 0.19,
    ("DL", "KORD", "KLAX"): 0.24,
    ("AA", "KATL", "KORD"): 0.21,
    ("AA", "KATL", "KLAX"): 0.18,
    ("AA", "KORD", "KLAX"): 0.23,
    ("UA", "KATL", "KORD"): 0.20,
    ("UA", "KATL", "KLAX"): 0.17,
    ("UA", "KORD", "KLAX"): 0.22,
    ("WN", "KATL", "KORD"): 0.18,
    ("WN", "KATL", "KLAX"): 0.16,
    ("WN", "KORD", "KLAX"): 0.20,
}

_AIRLINE_CODES: dict[str, str] = {
    "Delta Air Lines (DL)": "DL",
    "American Airlines (AA)": "AA",
    "United Airlines (UA)": "UA",
    "Southwest Airlines (WN)": "WN",
}


@dataclass(frozen=True)
class PredictionFeatures:
    """User-entered and derived values passed to the prediction service."""

    airline: str
    airline_code: str
    flight_number: Optional[str]
    origin: str
    origin_code: str
    destination: str
    destination_code: str
    flight_date: date
    scheduled_departure: time
    scheduled_arrival: time
    distance_miles: int
    scheduled_elapsed_minutes: int
    day_of_week: str
    quarter: str
    season: str
    weekend_indicator: str
    departure_hour_category: str
    historical_delay_rate: float


def parse_airport_code(airport_label: str) -> str:
    """Extract the IATA airport code from a display label."""

    match = re.match(r"^([A-Z0-9]{3,4})\s-", airport_label.strip())
    if not match:
        raise ValueError(f"Unable to parse airport code from '{airport_label}'.")
    return match.group(1)


def parse_airline_code(airline_label: str) -> str:
    """Extract the carrier code from a display label."""

    code = _AIRLINE_CODES.get(airline_label)
    if code:
        return code

    match = re.search(r"\(([A-Z0-9]{2})\)\s*$", airline_label.strip())
    if match:
        return match.group(1)
    raise ValueError(f"Unable to parse airline code from '{airline_label}'.")


def lookup_route_distance_miles(origin_code: str, destination_code: str) -> int:
    """Return great-circle distance in miles for a supported route."""

    route_key = tuple(sorted((origin_code, destination_code)))
    distance = _ROUTE_DISTANCE_MILES.get(route_key)
    if distance is None:
        raise ValueError(
            f"Distance is not configured for route {origin_code} → {destination_code}."
        )
    return distance


def compute_scheduled_elapsed_minutes(
    departure: time,
    arrival: time,
) -> int:
    """Compute scheduled block time, rolling arrival to the next day if needed."""

    departure_dt = datetime.combine(date.min, departure)
    arrival_dt = datetime.combine(date.min, arrival)
    if arrival_dt <= departure_dt:
        arrival_dt += timedelta(days=1)
    return int((arrival_dt - departure_dt).total_seconds() // 60)


def derive_day_of_week(flight_date: date) -> str:
    """Return the weekday name for a scheduled flight date."""

    return flight_date.strftime("%A")


def derive_quarter(flight_date: date) -> str:
    """Return the calendar quarter label for a scheduled flight date."""

    return f"Q{(flight_date.month - 1) // 3 + 1}"


def derive_season(flight_date: date) -> str:
    """Return a coarse season bucket for a scheduled flight date."""

    month = flight_date.month
    if month in {12, 1, 2}:
        return "Winter"
    if month in {3, 4, 5}:
        return "Spring"
    if month in {6, 7, 8}:
        return "Summer"
    return "Fall"


def derive_weekend_indicator(flight_date: date) -> str:
    """Return whether the flight date falls on a weekend."""

    return "Weekend" if flight_date.weekday() >= 5 else "Weekday"


def derive_departure_hour_category(departure: time) -> str:
    """Map scheduled departure time to an operational hour bucket."""

    hour = departure.hour
    if 5 <= hour <= 11:
        return "Morning"
    if 12 <= hour <= 17:
        return "Afternoon"
    if 18 <= hour <= 21:
        return "Evening"
    return "Night"


def lookup_historical_delay_rate(
    airline_code: str,
    origin_code: str,
    destination_code: str,
) -> float:
    """Return a prototype historical delay rate for the carrier and route."""

    rate = _HISTORICAL_DELAY_RATES.get((airline_code, origin_code, destination_code))
    if rate is not None:
        return rate

    route_key = tuple(sorted((origin_code, destination_code)))
    fallback_seed = sum(ord(char) for char in f"{airline_code}|{route_key[0]}|{route_key[1]}")
    return round(0.14 + (fallback_seed % 120) / 1000, 3)


def build_prediction_features(
    *,
    airline: str,
    flight_number: Optional[str],
    origin: str,
    destination: str,
    flight_date: date,
    scheduled_departure: time,
    scheduled_arrival: time,
) -> PredictionFeatures:
    """Build the full feature set from visible form inputs."""

    origin_code = parse_airport_code(origin)
    destination_code = parse_airport_code(destination)
    airline_code = parse_airline_code(airline)
    normalized_flight_number = (
        flight_number.strip().upper() if flight_number and flight_number.strip() else None
    )

    return PredictionFeatures(
        airline=airline,
        airline_code=airline_code,
        flight_number=normalized_flight_number,
        origin=origin,
        origin_code=origin_code,
        destination=destination,
        destination_code=destination_code,
        flight_date=flight_date,
        scheduled_departure=scheduled_departure,
        scheduled_arrival=scheduled_arrival,
        distance_miles=lookup_route_distance_miles(origin_code, destination_code),
        scheduled_elapsed_minutes=compute_scheduled_elapsed_minutes(
            scheduled_departure,
            scheduled_arrival,
        ),
        day_of_week=derive_day_of_week(flight_date),
        quarter=derive_quarter(flight_date),
        season=derive_season(flight_date),
        weekend_indicator=derive_weekend_indicator(flight_date),
        departure_hour_category=derive_departure_hour_category(scheduled_departure),
        historical_delay_rate=lookup_historical_delay_rate(
            airline_code,
            origin_code,
            destination_code,
        ),
    )
