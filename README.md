# Flight Delay Risk Prediction and Operational Prioritization

## Overview

This repository contains the Capstone Project developed for the Master of Data Analytics program at the University of Niagara Falls.

The objective of this project is to develop a machine-learning-based flight delay risk prediction and operational prioritization system for airline operations managers. The solution combines descriptive, diagnostic, predictive, and prescriptive analytics using historical flight information provided by the U.S. Bureau of Transportation Statistics (BTS).

---

## Project Objectives

- Analyze historical airline operational performance.
- Identify factors associated with flight delays.
- Predict flight delay risk using Machine Learning.
- Explain model predictions using SHAP-based model explainability.
- Prioritize operational decisions using optimization techniques.
- Provide business insights through an interactive dashboard.

---

## Dataset

**Source:** U.S. Bureau of Transportation Statistics (BTS)  
**URL:** https://www.transtats.bts.gov/  
**Dataset:** Airline On-Time Performance Data  
**Study period:** 2025  
**Prediction target:** `ArrDel15` (arrival delay ≥ 15 minutes)

### Data Acquisition

| Item | Detail |
|---|---|
| Download tool | BTS TranStats "Reporting Carrier On-Time Performance" download form (https://www.transtats.bts.gov/DL_SelectFields.aspx) |
| Monthly flight files | 12 files, `T_ONTIME_REPORTING_<MONTH>_2025.csv` (January-December 2025) |
| Reference (lookup) files | 7 files: `L_AIRPORT_Origin_Dest.csv`, `L_CANCELLATION_CancellationCode.csv`, `L_MONTHS_Month.csv`, `L_QUARTERS_Quarter.csv`, `L_UNIQUE_CARRIERS_Reporting_Airline.csv`, `L_WEEKDAYS_DayOfWeek.csv`, `L_YESNO_RESP_ArrDel15_DepDel15_Cancelled_Diverted.csv` |
| Columns requested | 32 fields covering calendar, schedule, airline/route, delay, and cancellation/diversion attributes — see [`EXPECTED_RAW_COLUMNS`](notebooks/config/project_config.py) for the exact list |
| Selection rationale | Only fields needed for schedule-time prediction, descriptive/diagnostic analytics, and the leakage audit were requested — no passenger-level or unrelated BTS fields were downloaded |
| Download period | January 2025 - December 2025 |

Raw files are landed unmodified into the Databricks Volume (`/raw`, `/reference`) and their presence/count is validated in [`00_environment_setup`](notebooks/00_environment_setup.ipynb) before ingestion.

---

## Technology Stack

| Layer | Tools |
|---|---|
| Data engineering | Databricks, Apache Spark (PySpark), Delta Lake, Python |
| Machine learning | Scikit-learn, XGBoost, SHAP |
| Optimization | SciPy mixed-integer linear programming (MILP) |
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
03_data_cleaning
04_descriptive_analytics
05_statistical_analysis
06_feature_engineering
07_model_training
08_model_evaluation
09_explainability
10_operational_prioritization
11_dashboard_data_preparation
```

After model changes in notebooks 07–09, re-run **07 → 11** to refresh model artifacts, predictions, and dashboard tables. Statistical-only changes in Notebook 05 require rerunning **05**, then **11** to refresh research records.

### Notebook Outputs

| Notebook | Primary outputs |
|---|---|
| 00 | Environment and source-file validation only |
| 01 | `flights_raw` and seven reference lookup tables |
| 02 | Data-quality profiling only; no persisted output |
| 03 | `flights_clean` |
| 04 | Descriptive analytics only; no persisted output |
| 05 | `statistical_analysis_results` |
| 06 | `flights_features` |
| 07–08 | Selected Python XGBoost bundle, preprocessing pipeline, and evaluation metrics |
| 09 | SHAP global/directional/sample tables, local explanation table, and local JSON artifact |
| 10 | `flight_predictions`, `flight_prioritization_results`, `flight_prioritization_evaluation` |
| 11 | `flight_dashboard`, `flight_dashboard_explorer`, `flight_dashboard_insights` |

### Research Questions

| RQ | Question | Validated in |
|---|---|---|
| RQ1 | How accurately can schedule-time flight information predict arrival delay of at least 15 minutes? | 05 (preliminary), 07, 08 |
| RQ2 | Which scheduling, airline, airport, route, and temporal factors are most strongly associated with delay risk? | 05, 09 |
| RQ3 | How do delay rates differ across airlines, airports, routes, departure periods, and seasons? | 04, 05 |
| RQ4 | How can SHAP explain overall and individual flight-delay predictions? | 09 |
| RQ5 | Can optimization identify more actual delays than random or simple rule-based prioritization under limited capacity? | 10 |

---

## FastAPI (`api/`)

FastAPI service connected to Databricks SQL Warehouse. Configuration is loaded from `api/.env` (see `api/.env.example`).

### Structure

```
api/
├── main.py                 # Application entry point and health checks
├── core/config.py          # Settings and table name resolution
├── db/databricks.py        # Databricks SQL connection helper
├── routers/                # HTTP endpoints by dashboard domain
├── services/               # Cached Databricks-backed payload builders
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
| GET | `/api/v1/overview` | Overview tab payload |
| GET | `/api/v1/explorer` | Scored Flight Explorer payload |
| GET | `/api/v1/explorer/options` | Complete Explorer filter choices |
| GET | `/api/v1/prioritization` | Capacity-constrained prioritization payload |
| GET | `/api/v1/model-insights` | Global and local SHAP explanations |
| GET | `/api/v1/predictions/options` | Supported airline, airport, and airline-route options |
| POST | `/api/v1/predictions` | Live single-flight delay-risk prediction |

### Run locally

```bash
cd api
cp .env.example .env   # fill in Databricks credentials
pip install -r requirements.txt
uvicorn api.main:app --reload --app-dir ..
```

---

## Streamlit Dashboard (`streamlit_app/`)

The Streamlit app preserves the complete dashboard structure: Overview, Flight Explorer, Delay Prediction, Model Insights, Operational Prioritization, and Project Overview.

- Overview, Flight Explorer, Delay Prediction, Model Insights, and Operational Prioritization use FastAPI services backed by notebook-generated tables or the frozen model bundle.
- Tabs whose live service is not connected display an explicit error.
- Never substitutes simulated dashboard or prediction results.
- Flight Explorer applies filters in Databricks: charts and counts use the full
  filtered population, while only the detailed flight log is limited for display.
- Live prediction rejects unsupported airline-route combinations and implausible
  schedules, reports the historical-reference date, and exposes future-date
  extrapolation explicitly.

### Model-serving verification

Notebook 08 publishes a small deterministic serving contract inside the frozen
model bundle. API startup verifies that the saved preprocessor and XGBoost model
reproduce the expected probabilities before accepting live prediction requests.
After changing Notebook 08, rerun **08 → 11**, restart FastAPI, and run:

```bash
python -m pytest -q
```

The current model is intended for operational risk ranking and planning. Its
main limitation is the absence of pre-departure weather, inbound-aircraft status,
real-time congestion, crew, maintenance, and air-traffic-control information.
RQ5 is supported at lower operational capacities in the evaluated scenarios, but
the optimization method does not outperform the simple baseline at every capacity.

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
- Operational prioritization with RQ5 baseline comparison
- Dashboard data preparation for Streamlit and API
- FastAPI services for Overview, Explorer, Delay Prediction, Model Insights, Prioritization, and health checks
- Streamlit dashboard without simulated fallback data

Next steps:

- Run the full pipeline on Databricks (`00 → 11`)
- Rerun Notebook 08 to publish the inference-ready model bundle
- Validate Streamlit against live Delta tables
- Finalize capstone report and presentation materials
