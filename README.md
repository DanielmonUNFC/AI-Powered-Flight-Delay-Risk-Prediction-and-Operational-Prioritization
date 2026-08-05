# AI-Powered Flight Delay Risk Prediction and Operational Prioritization

## Overview

This repository contains the Capstone Project developed for the Master of Data Analytics program at the University of Niagara Falls.

The objective of this project is to develop an AI-powered decision support system capable of assisting airline operations managers by predicting flight delay risks and recommending operational prioritization strategies. The proposed solution combines descriptive, diagnostic, predictive, and prescriptive analytics using historical flight information provided by the U.S. Bureau of Transportation Statistics (BTS).

---

## Project Objectives

- Analyze historical airline operational performance.
- Identify factors associated with flight delays.
- Predict flight delay risk using Machine Learning.
- Explain model predictions using Explainable AI (SHAP).
- Prioritize operational decisions using optimization techniques.
- Provide business insights through an interactive dashboard.

---

## Dataset

**Source:** U.S. Bureau of Transportation Statistics (BTS)  
**URL:** https://www.transtats.bts.gov/  
**Dataset:** Airline On-Time Performance Data  
**Study period:** 2025  
**Prediction target:** `ArrDel15` (arrival delay ≥ 15 minutes)

---

## Technology Stack

| Layer | Tools |
|---|---|
| Data engineering | Databricks, Apache Spark (PySpark), Delta Lake, Python |
| Machine learning | Scikit-learn, Spark ML, SHAP |
| Optimization | Google OR-Tools |
| Visualization | Streamlit, Plotly |
| Backend API | FastAPI, Databricks SQL Connector |
| Version control | Git, GitHub |

---

## Repository Structure

```
api/                    # FastAPI service (Databricks SQL backend)
notebooks/              # Databricks notebook pipeline (00–11)
  config/               # Pipeline table/column configuration
  utils/                # Reusable Python helpers for notebooks
streamlit_app/          # Interactive executive dashboard
requirements.txt        # Root Python dependencies
```

---

## Databricks Notebook Pipeline

Run the notebooks in order on Databricks:

```
00_environment_setup
01_data_ingestion
02_data_profiling
03_exploratory_data_analysis
04_data_cleaning
05_statistical_analysis
06_feature_engineering
07_model_training
08_model_evaluation
09_explainability
10_operational_prioritization
11_dashboard_data_preparation
```

After model changes in notebooks 07–09, re-run **07 → 11** to refresh checkpoints, predictions, and dashboard tables.

### Notebook Outputs

| Notebook | Primary outputs |
|---|---|
| 04 | `flights_clean` |
| 05 | `statistical_analysis_results` |
| 06 | `flights_features` |
| 07–08 | Selected Spark ML model, checkpoints, evaluation metrics |
| 09 | SHAP global/local artifacts |
| 10 | `flight_predictions`, `flight_prioritization_results`, `flight_prioritization_evaluation` |
| 11 | `flight_dashboard`, `flight_dashboard_explorer`, `flight_dashboard_insights` |

### Research Questions

| RQ | Question | Validated in |
|---|---|---|
| RQ1 | Can flight delays be accurately predicted before departure? | 05, 07, 08 |
| RQ2 | Which operational factors contribute most to delays? | 05, 09 |
| RQ3 | Do airlines and airports differ in delay rates? | 03, 05 |
| RQ4 | Can prescriptive prioritization improve operational decisions? | 10 |
| RQ5 | Can SHAP improve prediction interpretability? | 09 |

---

## FastAPI (`api/`)

Starter API scaffold connected to Databricks SQL Warehouse. Configuration is loaded from `api/.env` (see `api/.env.example`).

### Structure

```
api/
├── main.py                 # Application entry point and health checks
├── core/config.py          # Settings and table name resolution
├── db/databricks.py        # Databricks SQL connection helper
├── routers/overview.py     # Overview KPI endpoints
├── services/overview_service.py
├── requirements.txt
└── .env.example
```

### Endpoints (current)

| Method | Path | Description |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/docs` | Swagger UI |
| GET | `/api/v1/health` | Application health check |
| GET | `/api/v1/health/databricks` | Databricks connectivity check |
| GET | `/api/v1/overview/kpis` | Overview KPIs from `flights_clean` |

Additional endpoints for predictions, dashboard, and prioritization can be added incrementally as the pipeline notebooks 10–11 are completed.

### Run locally

```bash
cd api
cp .env.example .env   # fill in Databricks credentials
pip install -r requirements.txt
uvicorn api.main:app --reload --app-dir ..
```

---

## Streamlit Dashboard (`streamlit_app/`)

The Streamlit app provides the executive dashboard for overview KPIs, flight explorer, delay prediction, SHAP insights, and operational prioritization.

- Reads live Databricks tables when `DATABRICKS_*` environment variables are configured.
- Falls back to prototype data when credentials are missing.
- Force mock mode with `STREAMLIT_USE_MOCK_DATA=true`.

```bash
cd streamlit_app
streamlit run app.py
```

---

## Git Workflow

The project follows a simplified Git Flow strategy.

```
main        → Stable releases
develop     → Integration branch
feature/*   → Individual development
```

---

## Team

- Daniel Montero
- Alexis Baquidan
- Christianel Viaje
- Navpreet

---

## Project Status

**Current phase:** Pipeline complete — ready for Databricks execution and final report.

Completed:

- End-to-end Databricks notebook pipeline (00–11)
- Centralized configuration and reusable utilities
- Statistical analysis aligned with research questions
- Model training, evaluation, and SHAP explainability
- Operational prioritization with RQ4 baseline comparison
- Dashboard data preparation for Streamlit and API
- FastAPI starter service with overview KPIs and Databricks health check
- Streamlit dashboard with live-data and mock-data modes

Next steps:

- Run the full pipeline on Databricks (`00 → 11`)
- Extend the FastAPI layer step by step (predictions, dashboard, prioritization)
- Validate Streamlit against live Delta tables
- Finalize capstone report and presentation materials
