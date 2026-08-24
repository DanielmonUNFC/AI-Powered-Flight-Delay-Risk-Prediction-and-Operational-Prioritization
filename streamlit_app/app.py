import config.env_loader  # noqa: F401  — loads streamlit_app/.env before other imports

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
from components.tab_layout import render_tab_top_spacer

tab_overview, tab_explorer, tab_prediction, tab_insights, tab_prioritization, tab_info = st.tabs([
    "Overview",
    "Flight Explorer",
    "Delay Prediction",
    "Model Insights",
    "Operational Prioritization",
    "Project Overview"
])

# 5. Tab Views Router
with tab_overview:
    render_tab_top_spacer()
    from pages.overview import render_overview_page
    render_overview_page()

with tab_explorer:
    render_tab_top_spacer()
    from pages.flight_explorer import render_flight_explorer_page
    render_flight_explorer_page()

with tab_prediction:
    render_tab_top_spacer()
    from pages.delay_prediction import render_delay_prediction_page
    render_delay_prediction_page()

with tab_insights:
    render_tab_top_spacer()
    from pages.model_insights import render_model_insights_page
    render_model_insights_page()

with tab_prioritization:
    render_tab_top_spacer()
    from pages.operational_prioritization import render_operational_prioritization_page
    render_operational_prioritization_page()

with tab_info:
    render_tab_top_spacer()
    from pages.project_information import render_project_information_page
    render_project_information_page()
