import streamlit as st


def render_app_header(model_status: str = "UNFC CAPSTONE • BTS 2025") -> None:
    """Render the top dashboard branding header."""
    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-header__brand">
                <span class="app-header__brand-accent">FLIGHT DELAY RISK PREDICTION</span>
                <span class="app-header__brand-title"> | Operational Prioritization Dashboard</span>
            </div>
            <div>
                <span class="app-header__status">🟢 {model_status}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
