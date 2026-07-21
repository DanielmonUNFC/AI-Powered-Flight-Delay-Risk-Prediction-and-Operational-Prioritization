import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Flight Delay Risk Prediction | Capstone Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inject CSS stylesheets
from styles.loader import load_styles

load_styles()

# 3. Global App Branding Header
from components.app_header import render_app_header
render_app_header()

# 4. Main Navigation Tabs
from components.placeholder_tab import render_placeholder_tab
from config.panel_icons import (
    ICON_DELAY_PREDICTION,
    ICON_MODEL_INSIGHTS,
    ICON_PRIORITIZATION,
)

tab_overview, tab_explorer, tab_prediction, tab_insights, tab_prioritization, tab_info = st.tabs([
    "Overview",
    "Flight Explorer",
    "Delay Prediction",
    "Model Insights",
    "Operational Prioritization",
    "Project Information"
])

# 5. Tab Views Router
with tab_overview:
    from pages.overview import render_overview_page
    render_overview_page()

with tab_explorer:
    from pages.flight_explorer import render_flight_explorer_page
    render_flight_explorer_page()

with tab_prediction:
    render_placeholder_tab(
        "Delay Prediction",
        ICON_DELAY_PREDICTION,
        "Tab ready for ML Model Inference integration.",
    )

with tab_insights:
    render_placeholder_tab(
        "Model Insights",
        ICON_MODEL_INSIGHTS,
        "Tab ready for SHAP Explainability plots integration.",
    )

with tab_prioritization:
    render_placeholder_tab(
        "Operational Prioritization",
        ICON_PRIORITIZATION,
        "Tab ready for Prescriptive Ranking Matrix integration.",
    )

with tab_info:
    from pages.project_information import render_project_information_page
    render_project_information_page()
