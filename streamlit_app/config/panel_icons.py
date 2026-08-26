"""Dashboard icon identifiers shared across all tabs.

Icons render as inline SVG via utils/dashboard_icons.py (not emojis).
"""

from typing import Final

# Overview
ICON_MONTHLY_TREND: Final[str] = "monthly_trend"
ICON_DELAY_CAUSES: Final[str] = "delay_causes"
ICON_INSIGHT: Final[str] = "insight"

# Flight Explorer
ICON_EXPLORER_FILTERS: Final[str] = "explorer_filters"
ICON_AIRLINE_CHART: Final[str] = "airline_chart"
ICON_ROUTES: Final[str] = "routes"
ICON_FLIGHT_LOG: Final[str] = "flight_log"

# Project Overview
ICON_OBJECTIVE: Final[str] = "objective"
ICON_DATASET: Final[str] = "dataset"
ICON_PREDICTION_TARGET: Final[str] = "prediction_target"
ICON_RESEARCH_QUESTIONS: Final[str] = "research_questions"
ICON_METHODOLOGY: Final[str] = "methodology"
ICON_TEAM: Final[str] = "team"
ICON_TECH_STACK: Final[str] = "tech"

# Predictive and operational tabs
ICON_DELAY_PREDICTION: Final[str] = "delay_prediction"
ICON_MODEL_INSIGHTS: Final[str] = "model_insights"
ICON_PRIORITIZATION: Final[str] = "prioritization"
ICON_LIVE_SUMMARY: Final[str] = "live_summary"
ICON_PRIORITY_RANKING: Final[str] = "priority_ranking"

# Tech stack keys (Project Information grid)
TECH_ICON_DATABRICKS: Final[str] = "databricks"
TECH_ICON_DELTA_LAKE: Final[str] = "delta_lake"
TECH_ICON_PYSPARK: Final[str] = "pyspark"
TECH_ICON_PYTHON: Final[str] = "python"
TECH_ICON_XGBOOST: Final[str] = "xgboost"
TECH_ICON_SHAP: Final[str] = "shap"
TECH_ICON_FASTAPI: Final[str] = "fastapi"
TECH_ICON_STREAMLIT: Final[str] = "streamlit"
TECH_ICON_GITHUB: Final[str] = "github"
