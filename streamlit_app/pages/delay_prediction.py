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
from services.api_client import (
    ApiClientError,
    create_prediction,
    fetch_prediction_options,
)


_PREDICTION_STATE_KEY = "delay_prediction_result"
_PREDICTION_ERROR_KEY = "delay_prediction_error"

_FORM_DEFAULTS: dict[str, object] = {
    "delay_prediction_airline": "DL",
    "delay_prediction_flight_number": "",
    "delay_prediction_origin": "ATL",
    "delay_prediction_destination": "ORD",
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

    options = _load_prediction_options()

    with col_form:
        if options is None:
            st.error(
                "Unable to load the live prediction form. Verify the API and "
                "rerun Notebook 08 to publish the inference-ready model bundle."
            )
            submitted = False
        else:
            _synchronize_option_state(options)
            submitted = _render_prediction_form(options)

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


def _render_prediction_form(options: dict) -> bool:
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

    airline_labels = {
        item["code"]: item["name"]
        for item in options["airlines"]
    }
    airport_labels = {
        item["code"]: item["name"]
        for item in options["airports"]
    }
    airline_codes = list(airline_labels)
    airline_routes = options.get("airline_routes", {})

    with airline_column:
        st.selectbox(
            "Airline",
            airline_codes,
            format_func=lambda code: f"{code} · {airline_labels[code]}",
            key="delay_prediction_airline",
        )

    with flight_number_column:
        st.text_input(
            "Flight Number (optional, reference only)",
            placeholder="DL215",
            key="delay_prediction_flight_number",
        )

    st.date_input(
        "Flight Date",
        key="delay_prediction_flight_date",
    )

    _render_form_section("Route Information")

    selected_airline = st.session_state["delay_prediction_airline"]
    supported_route_keys = airline_routes.get(selected_airline) or [
        f"{route['origin']}|{route['destination']}" for route in options["routes"]
    ]
    route_pairs = [route.split("|", 1) for route in supported_route_keys]
    origin_codes = sorted({origin for origin, _ in route_pairs})
    if st.session_state["delay_prediction_origin"] not in origin_codes:
        st.session_state["delay_prediction_origin"] = origin_codes[0]
    selected_origin = st.session_state["delay_prediction_origin"]
    destination_codes = sorted(
        destination for origin, destination in route_pairs if origin == selected_origin
    )
    if st.session_state["delay_prediction_destination"] not in destination_codes:
        st.session_state["delay_prediction_destination"] = destination_codes[0]

    origin_column, destination_column = st.columns(2)

    with origin_column:
        st.selectbox(
            "Origin Airport",
            origin_codes,
            format_func=lambda code: _airport_label(
                code,
                airport_labels[code],
            ),
            key="delay_prediction_origin",
        )

    with destination_column:
        st.selectbox(
            "Destination Airport",
            destination_codes,
            format_func=lambda code: _airport_label(
                code,
                airport_labels[code],
            ),
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
    """Validate inputs and request a live prediction."""

    origin = str(st.session_state.get("delay_prediction_origin", ""))
    destination = str(st.session_state.get("delay_prediction_destination", ""))

    validation_error = _validate_prediction_inputs(
        origin=origin,
        destination=destination,
    )

    if validation_error:
        st.session_state[_PREDICTION_ERROR_KEY] = validation_error
        return

    payload = {
        "airline": st.session_state["delay_prediction_airline"],
        "flight_number": (
            st.session_state["delay_prediction_flight_number"] or None
        ),
        "origin": st.session_state["delay_prediction_origin"],
        "destination": st.session_state["delay_prediction_destination"],
        "flight_date": st.session_state[
            "delay_prediction_flight_date"
        ].isoformat(),
        "scheduled_departure": st.session_state[
            "delay_prediction_departure_time"
        ].strftime("%H:%M:%S"),
        "scheduled_arrival": st.session_state[
            "delay_prediction_arrival_time"
        ].strftime("%H:%M:%S"),
    }

    try:
        result = create_prediction(payload)
    except ApiClientError as error:
        st.session_state[_PREDICTION_STATE_KEY] = None
        st.session_state[_PREDICTION_ERROR_KEY] = str(error)
        return

    st.session_state[_PREDICTION_STATE_KEY] = result
    st.session_state[_PREDICTION_ERROR_KEY] = None

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


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_prediction_options_cached() -> dict:
    """Cache stable form options for one hour."""
    return fetch_prediction_options()


def _load_prediction_options() -> dict | None:
    try:
        options = _fetch_prediction_options_cached()
    except ApiClientError as error:
        st.session_state[_PREDICTION_ERROR_KEY] = str(error)
        return None

    if not options.get("airlines") or not options.get("airports"):
        st.session_state[_PREDICTION_ERROR_KEY] = (
            "The prediction API returned no supported airlines or airports."
        )
        return None
    return options


def _synchronize_option_state(options: dict) -> None:
    """Replace obsolete hardcoded selections with supported API values."""
    airline_codes = [item["code"] for item in options["airlines"]]
    airport_codes = [item["code"] for item in options["airports"]]

    if st.session_state["delay_prediction_airline"] not in airline_codes:
        st.session_state["delay_prediction_airline"] = airline_codes[0]
    if st.session_state["delay_prediction_origin"] not in airport_codes:
        st.session_state["delay_prediction_origin"] = airport_codes[0]
    if st.session_state["delay_prediction_destination"] not in airport_codes:
        st.session_state["delay_prediction_destination"] = (
            airport_codes[1] if len(airport_codes) > 1 else airport_codes[0]
        )


def _airport_label(code: str, description: str) -> str:
    """Return a compact code-and-name label without changing the form layout."""
    name = description.split(":", maxsplit=1)[-1].strip()
    return f"{code} · {name or description}"
