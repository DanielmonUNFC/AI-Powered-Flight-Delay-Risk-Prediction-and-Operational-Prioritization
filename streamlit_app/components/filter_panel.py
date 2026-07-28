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
    if st.session_state["f_carrier"] != "All":
        filtered_df = filtered_df[filtered_df["Carrier"] == st.session_state["f_carrier"]]
    if st.session_state["f_origin"] != "All":
        filtered_df = filtered_df[filtered_df["Origin"] == st.session_state["f_origin"]]
    if st.session_state["f_dest"] != "All":
        filtered_df = filtered_df[filtered_df["Destination"] == st.session_state["f_dest"]]
    if st.session_state["f_status"] != "All":
        status = st.session_state["f_status"]
        filtered_df = filtered_df[
            filtered_df["Status"].str.upper() == status.upper().replace("-", "_")
        ]
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
    carriers = ["All"] + sorted(df["Carrier"].unique().tolist())
    origins = ["All"] + sorted(df["Origin"].unique().tolist())
    destinations = ["All"] + sorted(df["Destination"].unique().tolist())

    row_one_left, row_one_right = st.columns(2)
    with row_one_left:
        st.selectbox("Month", months, key="f_month")
    with row_one_right:
        st.selectbox("Carrier", carriers, key="f_carrier")

    row_two_left, row_two_right = st.columns(2)
    with row_two_left:
        st.selectbox("Origin", origins, key="f_origin")
    with row_two_right:
        st.selectbox("Destination", destinations, key="f_dest")

    row_three_left, row_three_right = st.columns(2)
    with row_three_left:
        st.selectbox("Delay Status", ["All", "Delayed", "On-Time"], key="f_status")
    with row_three_right:
        st.selectbox("Risk Tier", ["All", "CRITICAL", "HIGH", "LOW"], key="f_risk_tier")

    row_four_left, row_four_right = st.columns(2)
    with row_four_left:
        st.selectbox(
            "Departure Window",
            ["All", "Morning", "Afternoon", "Evening"],
            key="f_dep_window",
        )
    with row_four_right:
        st.selectbox("Min Delay Probability", ["All", "≥ 50%", "≥ 80%"], key="f_min_delay")

    st.selectbox(
        "Sort Results By",
        ["Highest Delay Risk", "Lowest Delay Risk", "Departure Time"],
        key="f_sort_by",
    )

    st.button(
        "↺ Reset Filters",
        on_click=reset_filters_callback,
        use_container_width=True,
        key="explorer_reset_filters",
    )

    return _apply_filters(df)
