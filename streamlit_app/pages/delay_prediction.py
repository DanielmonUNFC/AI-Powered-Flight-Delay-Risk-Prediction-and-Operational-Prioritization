"""Delay Prediction page."""

from __future__ import annotations

import streamlit as st

from components.prediction_result_panel import (
    render_prediction_placeholder,
    render_prediction_result,
    render_recommendation_placeholder,
    render_recommendation_result,
)
from services.prototype_data import get_mock_prediction


_PREDICTION_STATE_KEY = "delay_prediction_result"


def render_delay_prediction_page() -> None:
    """Render the Delay Prediction page."""

    _initialize_prediction_state()

    st.markdown("##### DELAY PREDICTION")

    left, right = st.columns([0.95, 1.05], gap="large")

    with left:
        st.markdown("### Flight Parameters Entry")

        airline = st.selectbox(
            "Airline",
            [
                "Delta Air Lines (DL)",
                "American Airlines (AA)",
                "United Airlines (UA)",
                "Southwest Airlines (WN)",
            ],
            key="delay_prediction_airline",
        )

        origin = st.selectbox(
            "Origin",
            [
                "KATL - Atlanta",
                "KORD - Chicago",
                "KLAX - Los Angeles",
            ],
            key="delay_prediction_origin",
        )

        destination = st.selectbox(
            "Destination",
            [
                "KORD - Chicago",
                "KATL - Atlanta",
                "KLAX - Los Angeles",
            ],
            key="delay_prediction_destination",
        )

        st.date_input(
            "Flight Date",
            key="delay_prediction_flight_date",
        )

        departure_column, arrival_column = st.columns(2)

        with departure_column:
            departure_time = st.time_input(
                "Departure Time",
                key="delay_prediction_departure_time",
            )

        with arrival_column:
            st.time_input(
                "Arrival Time",
                key="delay_prediction_arrival_time",
            )

        predict_clicked = st.button(
            "Predict Delay Risk",
            use_container_width=True,
            type="primary",
            key="delay_prediction_submit",
        )

        if predict_clicked:
            validation_error = _validate_prediction_inputs(
                origin=origin,
                destination=destination,
            )

            if validation_error:
                st.error(validation_error)
            else:
                st.session_state[_PREDICTION_STATE_KEY] = (
                    get_mock_prediction(
                        airline=airline,
                        origin=origin,
                        destination=destination,
                        departure_time=departure_time.strftime("%H:%M"),
                    )
                )

    with right:
        result = st.session_state[_PREDICTION_STATE_KEY]

        if result is None:
            render_prediction_placeholder()
            st.write("")
            render_recommendation_placeholder()
        else:
            render_prediction_result(result)
            st.write("")
            render_recommendation_result(result)


def _initialize_prediction_state() -> None:
    """Create the prediction state entry once per Streamlit session."""

    if _PREDICTION_STATE_KEY not in st.session_state:
        st.session_state[_PREDICTION_STATE_KEY] = None


def _validate_prediction_inputs(
    origin: str,
    destination: str,
) -> str | None:
    """Validate required inputs before generating a prediction."""

    if origin == destination:
        return "Origin and destination must be different airports."

    return None