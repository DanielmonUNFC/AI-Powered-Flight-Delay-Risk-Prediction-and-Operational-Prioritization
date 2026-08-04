"""Explorer filter panel with native Streamlit controls."""

import pandas as pd
import streamlit as st

from components.panel_header import panel_header_html
from config.panel_icons import ICON_EXPLORER_FILTERS

FILTER_DEFAULTS = {
    "f_month": "All",
    "f_carrier": "All",
    "f_origin": "All",
    "f_dest": "All",
    "f_carrier_code": "All",
    "f_origin_code": "All",
    "f_dest_code": "All",
    "f_status": "All",
    "f_risk_tier": "All",
    "f_dep_window": "All",
    "f_min_delay": "All",
    "f_sort_by": "Highest Delay Risk",
}


def reset_filters_callback() -> None:
    """Reset all explorer filter widgets to their default values."""
    for key, value in FILTER_DEFAULTS.items():
        st.session_state[key] = value


def _init_filter_state() -> None:
    """Ensure filter widget keys exist in session state."""
    for key, value in FILTER_DEFAULTS.items():
        st.session_state.setdefault(key, value)


def _apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered_df = df.copy()

    if st.session_state["f_month"] != "All":
        filtered_df = filtered_df[filtered_df["Month"] == st.session_state["f_month"]]
    if st.session_state.get("f_carrier_code", "All") != "All":
        filtered_df = filtered_df[
            filtered_df["Carrier"] == st.session_state["f_carrier_code"]
        ]
    if st.session_state.get("f_origin_code", "All") != "All":
        filtered_df = filtered_df[
            filtered_df["Origin"] == st.session_state["f_origin_code"]
        ]
    if st.session_state.get("f_dest_code", "All") != "All":
        filtered_df = filtered_df[
            filtered_df["Destination"] == st.session_state["f_dest_code"]
        ]
    if st.session_state["f_status"] == "Predicted Delayed":
        filtered_df = filtered_df[filtered_df["DelayProb"] >= 0.5]
    elif st.session_state["f_status"] == "Predicted On-Time":
        filtered_df = filtered_df[filtered_df["DelayProb"] < 0.5]
    if st.session_state["f_risk_tier"] != "All":
        filtered_df = filtered_df[filtered_df["RiskTier"] == st.session_state["f_risk_tier"]]
    if st.session_state["f_dep_window"] != "All":
        filtered_df = filtered_df[
            filtered_df["DepartureWindow"] == st.session_state["f_dep_window"]
        ]
    if st.session_state["f_min_delay"] == "≥ 50%":
        filtered_df = filtered_df[filtered_df["DelayProb"] >= 0.5]
    elif st.session_state["f_min_delay"] == "≥ 80%":
        filtered_df = filtered_df[filtered_df["DelayProb"] >= 0.8]

    sort_by = st.session_state["f_sort_by"]
    if sort_by == "Highest Delay Risk":
        filtered_df = filtered_df.sort_values(by="DelayProb", ascending=False)
    elif sort_by == "Lowest Delay Risk":
        filtered_df = filtered_df.sort_values(by="DelayProb", ascending=True)
    elif sort_by == "Departure Time":
        filtered_df = filtered_df.sort_values(by="DepTime")

    return filtered_df


def render_explorer_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render the explorer filter panel and return the filtered dataframe."""
    _init_filter_state()

    st.markdown(
        panel_header_html("Explorer Filters", ICON_EXPLORER_FILTERS),
        unsafe_allow_html=True,
    )

    months = ["All"] + sorted(df["Month"].unique().tolist())
    carrier_options = (
        df[["Carrier", "CarrierLabel"]]
        .drop_duplicates()
        .sort_values("CarrierLabel")
    )
    carrier_labels = ["All"] + carrier_options["CarrierLabel"].tolist()
    carrier_lookup = dict(
        zip(carrier_options["CarrierLabel"], carrier_options["Carrier"])
    )
    origin_options = (
        df[["Origin", "OriginLabel"]]
        .drop_duplicates()
        .sort_values("OriginLabel")
    )
    origin_labels = ["All"] + origin_options["OriginLabel"].tolist()
    origin_lookup = dict(zip(origin_options["OriginLabel"], origin_options["Origin"]))
    destination_options = (
        df[["Destination", "DestinationLabel"]]
        .drop_duplicates()
        .sort_values("DestinationLabel")
    )
    destination_labels = ["All"] + destination_options["DestinationLabel"].tolist()
    destination_lookup = dict(
        zip(destination_options["DestinationLabel"], destination_options["Destination"])
    )

    if st.session_state["f_carrier"] not in carrier_labels:
        st.session_state["f_carrier"] = "All"
        st.session_state["f_carrier_code"] = "All"
    if st.session_state["f_origin"] not in origin_labels:
        st.session_state["f_origin"] = "All"
        st.session_state["f_origin_code"] = "All"
    if st.session_state["f_dest"] not in destination_labels:
        st.session_state["f_dest"] = "All"
        st.session_state["f_dest_code"] = "All"

    compact_left, compact_right = st.columns(2)
    with compact_left:
        st.selectbox("Month", months, key="f_month")
    with compact_right:
        st.selectbox(
            "Outcome",
            ["All", "Predicted Delayed", "Predicted On-Time"],
            key="f_status",
        )

    compact_left, compact_right = st.columns(2)
    with compact_left:
        st.selectbox(
            "Risk Tier",
            ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
            key="f_risk_tier",
        )
    with compact_right:
        st.selectbox(
            "Dep. Window",
            ["All", "Morning", "Afternoon", "Evening"],
            key="f_dep_window",
        )

    compact_left, compact_right = st.columns(2)
    with compact_left:
        st.selectbox("Min Delay", ["All", "≥ 50%", "≥ 80%"], key="f_min_delay")
    with compact_right:
        st.selectbox(
            "Sort By",
            ["Highest Delay Risk", "Lowest Delay Risk", "Departure Time"],
            key="f_sort_by",
        )

    route_left, route_right = st.columns(2)
    with route_left:
        selected_origin_label = st.selectbox("Origin", origin_labels, key="f_origin")
        st.session_state["f_origin_code"] = (
            "All"
            if selected_origin_label == "All"
            else origin_lookup[selected_origin_label]
        )
    with route_right:
        selected_destination_label = st.selectbox(
            "Destination",
            destination_labels,
            key="f_dest",
        )
        st.session_state["f_dest_code"] = (
            "All"
            if selected_destination_label == "All"
            else destination_lookup[selected_destination_label]
        )

    selected_carrier_label = st.selectbox("Carrier", carrier_labels, key="f_carrier")
    st.session_state["f_carrier_code"] = (
        "All"
        if selected_carrier_label == "All"
        else carrier_lookup[selected_carrier_label]
    )

    st.button(
        "↺ Reset",
        on_click=reset_filters_callback,
        use_container_width=True,
        key="explorer_reset_filters",
    )

    return _apply_filters(df)
