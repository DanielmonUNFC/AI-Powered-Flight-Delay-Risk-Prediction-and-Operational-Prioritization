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

**Source**

U.S. Bureau of Transportation Statistics (BTS)

https://www.transtats.bts.gov/

**Dataset**

Airline On-Time Performance Data

---

## Technology Stack

### Data Engineering

- Databricks
- Apache Spark (PySpark)
- Python

### Machine Learning

- Scikit-learn
- SHAP

### Optimization

- Google OR-Tools

### Visualization

- Streamlit
- Plotly

### Backend

- FastAPI (Optional)

### Version Control

- Git
- GitHub

---

## Repository Structure

```
config/
dashboard/
data/
    ├── raw/
    ├── processed/
    ├── external/
    └── samples/
docs/
notebooks/
src/
tests/
```

---

## Git Workflow

The project follows a simplified Git Flow strategy.

```
main
│
└── Stable releases

develop
│
└── Integration branch

feature/*
│
└── Individual development
```

---

## Team

- Daniel Montero
- Alexis Baquidan
- Christianel Viaje
- Navpreet

---

## Project Status

In Progress

Current phase:

- Repository initialization
- Environment configuration
- Dataset exploration