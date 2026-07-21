import streamlit as st


def render_overview():

    st.title("✈ AEROINTEL")
    st.caption("Flight Delay Intelligence Platform")

    st.divider()

    st.header("Operational Overview")

    st.write(
        """
        Executive dashboard showing the operational performance of the
        2025 BTS On-Time Performance dataset.
        """
    )

    st.divider()

    ###################################################
    # KPI Cards
    ###################################################

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Flights", "—")
    col2.metric("Delay Rate", "—")
    col3.metric("Avg Departure Delay", "—")
    col4.metric("Cancellation Rate", "—")

    st.divider()

    ###################################################
    # Charts
    ###################################################

    left, right = st.columns([3, 2])

    with left:

        st.subheader("Monthly Delay Rate Trend")

        st.info("Monthly trend chart goes here.")

    with right:

        st.subheader("Delay Minutes by Cause")

        st.info("Donut chart goes here.")

    st.divider()

    st.subheader("Key Operational Insight")

    st.info(
        "Operational insight generated from dashboard metrics."
    )