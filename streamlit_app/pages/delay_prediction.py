"""Delay Prediction page."""

from __future__ import annotations

from datetime import date, time
from typing import Optional

import streamlit as st

from components.delay_prediction_layout_sync import render_delay_prediction_layout_sync
from components.panel_header import panel_header_html
from components.prediction_result_panel import (
    render_prediction_placeholder,
    render_prediction_result,
    render_recommendation_placeholder,
    render_recommendation_result,
)
from config.panel_icons import ICON_DELAY_PREDICTION
from services.prototype_data import get_mock_prediction


_PREDICTION_STATE_KEY = "delay_prediction_result"
_PREDICTION_ERROR_KEY = "delay_prediction_error"

_FORM_DEFAULTS: dict[str, object] = {
    "delay_prediction_airline": "Delta Air Lines (DL)",
    "delay_prediction_flight_number": "",
    "delay_prediction_origin": "KATL - Atlanta",
    "delay_prediction_destination": "KORD - Chicago",
    "delay_prediction_flight_date": date.today(),
    "delay_prediction_departure_time": time(hour=8, minute=0),
    "delay_prediction_arrival_time": time(hour=10, minute=30),
}


def render_delay_prediction_page() -> None:
    """Render the Delay Prediction page."""

    _initialize_prediction_state()

    st.markdown(
        """
        <div class="page-subtitle page-subtitle--delay-prediction">
            Operational Delay Risk Scoring & Prescriptive Recommendations
        </div>
        <span class="delay-prediction-layout-marker"></span>
        """,
        unsafe_allow_html=True,
    )

    col_form, col_results = st.columns([1, 2.4], gap="medium")

    with col_form:
        submitted = _render_prediction_form()

        if submitted:
            _handle_prediction_submit()

        prediction_error = st.session_state.get(_PREDICTION_ERROR_KEY)
        if prediction_error:
            st.error(prediction_error)

    with col_results:
        st.markdown(
            '<span class="delay-prediction-main-panel-marker"></span>',
            unsafe_allow_html=True,
        )

        result = st.session_state[_PREDICTION_STATE_KEY]

        if result is None:
            render_prediction_placeholder()
            render_recommendation_placeholder()
        else:
            render_prediction_result(result)
            render_recommendation_result(result)

    render_delay_prediction_layout_sync()


def _render_prediction_form() -> bool:
    """Render the bordered flight-parameter panel and return submit state."""

    st.markdown(
        '<span class="delay-prediction-filter-panel-marker"></span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        panel_header_html("Flight Parameters Entry", ICON_DELAY_PREDICTION),
        unsafe_allow_html=True,
    )

    _render_form_section("Flight Information")

    airline_column, flight_number_column = st.columns(2)

    with airline_column:
        st.selectbox(
            "Airline",
            [
                "Delta Air Lines (DL)",
                "American Airlines (AA)",
                "United Airlines (UA)",
                "Southwest Airlines (WN)",
            ],
            key="delay_prediction_airline",
        )

    with flight_number_column:
        st.text_input(
            "Flight Number (optional)",
            placeholder="DL215",
            key="delay_prediction_flight_number",
        )

    st.date_input(
        "Flight Date",
        key="delay_prediction_flight_date",
    )

    _render_form_section("Route Information")

    origin_column, destination_column = st.columns(2)

    with origin_column:
        st.selectbox(
            "Origin Airport",
            [
                "KATL - Atlanta",
                "KORD - Chicago",
                "KLAX - Los Angeles",
            ],
            key="delay_prediction_origin",
        )

    with destination_column:
        st.selectbox(
            "Destination Airport",
            [
                "KORD - Chicago",
                "KATL - Atlanta",
                "KLAX - Los Angeles",
            ],
            key="delay_prediction_destination",
        )

    _render_form_section("Schedule Information")

    departure_column, arrival_column = st.columns(2)

    with departure_column:
        st.time_input(
            "Scheduled Departure",
            key="delay_prediction_departure_time",
        )

    with arrival_column:
        st.time_input(
            "Scheduled Arrival",
            key="delay_prediction_arrival_time",
        )

    st.markdown(
        '<span class="delay-prediction-submit-marker"></span>',
        unsafe_allow_html=True,
    )

    return st.button(
        "⚡ Predict Delay Risk",
        use_container_width=True,
        type="primary",
        key="delay_prediction_submit",
    )


def _handle_prediction_submit() -> None:
    """Validate inputs and persist a mock prediction result."""

    origin = str(st.session_state.get("delay_prediction_origin", ""))
    destination = str(st.session_state.get("delay_prediction_destination", ""))

    validation_error = _validate_prediction_inputs(
        origin=origin,
        destination=destination,
    )

    if validation_error:
        st.session_state[_PREDICTION_ERROR_KEY] = validation_error
        return

    try:
        st.session_state[_PREDICTION_STATE_KEY] = get_mock_prediction(
            airline=str(st.session_state["delay_prediction_airline"]),
            flight_number=str(
                st.session_state.get("delay_prediction_flight_number", "")
            ),
            origin=origin,
            destination=destination,
            flight_date=st.session_state["delay_prediction_flight_date"],
            scheduled_departure=st.session_state["delay_prediction_departure_time"],
            scheduled_arrival=st.session_state["delay_prediction_arrival_time"],
        )
        st.session_state[_PREDICTION_ERROR_KEY] = None
    except (TypeError, ValueError):
        st.session_state[_PREDICTION_ERROR_KEY] = (
            "Unable to generate a prediction with the current inputs. "
            "Please verify the route and schedule, then try again."
        )


def _render_form_section(title: str) -> None:
    """Render a grouped section label inside the parameter form."""

    st.markdown(
        f'<p class="delay-prediction-form-section">{title}</p>',
        unsafe_allow_html=True,
    )


def _initialize_prediction_state() -> None:
    """Create prediction and form state entries once per Streamlit session."""

    if _PREDICTION_STATE_KEY not in st.session_state:
        st.session_state[_PREDICTION_STATE_KEY] = None

    if _PREDICTION_ERROR_KEY not in st.session_state:
        st.session_state[_PREDICTION_ERROR_KEY] = None

    for key, value in _FORM_DEFAULTS.items():
        st.session_state.setdefault(key, value)


def _validate_prediction_inputs(
    origin: str,
    destination: str,
) -> Optional[str]:
    """Validate required inputs before generating a prediction."""

    if origin == destination:
        return "Origin and destination must be different airports."

    return None
