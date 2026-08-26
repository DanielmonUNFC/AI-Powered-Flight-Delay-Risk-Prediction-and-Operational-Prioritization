"""Static content for the Project Overview dashboard tab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from config.panel_icons import (
    ICON_DATASET,
    ICON_METHODOLOGY,
    ICON_OBJECTIVE,
    ICON_PREDICTION_TARGET,
    ICON_RESEARCH_QUESTIONS,
    ICON_TEAM,
    ICON_TECH_STACK,
    TECH_ICON_DATABRICKS,
    TECH_ICON_DELTA_LAKE,
    TECH_ICON_FASTAPI,
    TECH_ICON_GITHUB,
    TECH_ICON_PYSPARK,
    TECH_ICON_PYTHON,
    TECH_ICON_SHAP,
    TECH_ICON_STREAMLIT,
    TECH_ICON_XGBOOST,
)
from utils.media import asset_path


@dataclass(frozen=True)
class InfoSection:
    """Text block shown inside a project overview panel."""

    title: str
    icon_id: str
    paragraphs: tuple[str, ...]


@dataclass(frozen=True)
class FactItem:
    """Single label/value pair for a compact fact card."""

    label: str
    value: str


@dataclass(frozen=True)
class FactCardSection:
    """Compact fact card panel content."""

    title: str
    icon_id: str
    facts: tuple[FactItem, ...]


@dataclass(frozen=True)
class ResearchQuestion:
    """Research question entry linked to dashboard capabilities."""

    code: str
    text: str


@dataclass(frozen=True)
class ResearchQuestionsSection:
    """Research questions panel content."""

    title: str
    icon_id: str
    questions: tuple[ResearchQuestion, ...]


@dataclass(frozen=True)
class TeamMember:
    """Capstone team member entry."""

    name: str
    photo_file: str


@dataclass(frozen=True)
class TeamSection:
    """Team panel header plus member list."""

    title: str
    icon_id: str
    members: tuple[TeamMember, ...]


@dataclass(frozen=True)
class TechStackItem:
    """Technology entry for the tech stack grid."""

    name: str
    icon_key: str


@dataclass(frozen=True)
class TechStackSection:
    """Tech stack panel header plus technology list."""

    title: str
    icon_id: str
    items: tuple[TechStackItem, ...]


@dataclass(frozen=True)
class ProjectOverviewContent:
    """All predefined content for the Project Overview tab."""

    business_objective: InfoSection
    dataset: FactCardSection
    prediction_target: FactCardSection
    research_questions: ResearchQuestionsSection
    methodology: InfoSection
    methodology_steps: tuple[str, ...]
    tech_stack: TechStackSection
    team: TeamSection


BUSINESS_OBJECTIVE: Final[InfoSection] = InfoSection(
    title="Business Objective",
    icon_id=ICON_OBJECTIVE,
    paragraphs=(
        (
            "Develop an AI-powered decision support system that estimates the probability "
            "that a scheduled flight will arrive at least 15 minutes late (ArrDel15) before "
            "departure. The system helps airline operations managers prioritize high-risk "
            "flights when operational review capacity is limited—moving from reactive "
            "reporting to proactive, evidence-based planning."
        ),
        (
            "The solution connects descriptive analytics, predictive modeling, SHAP "
            "explainability, and operational prioritization in a single executive dashboard "
            "backed by reproducible Delta Lake datasets and version-controlled pipelines."
        ),
    ),
)

DATASET_INFORMATION: Final[FactCardSection] = FactCardSection(
    title="Dataset Information",
    icon_id=ICON_DATASET,
    facts=(
        FactItem("Source", "Bureau of Transportation Statistics"),
        FactItem("Dataset", "Airline On-Time Performance"),
        FactItem("Study Period", "2025"),
        FactItem("Flights", "6.88 million"),
    ),
)

PREDICTION_TARGET: Final[FactCardSection] = FactCardSection(
    title="Prediction Target",
    icon_id=ICON_PREDICTION_TARGET,
    facts=(
        FactItem("Target", "ArrDel15"),
        FactItem("Prediction Type", "Binary Classification"),
        FactItem("Positive Class", "Arrival Delay ≥15 min"),
    ),
)

RESEARCH_QUESTIONS: Final[ResearchQuestionsSection] = ResearchQuestionsSection(
    title="Research Questions",
    icon_id=ICON_RESEARCH_QUESTIONS,
    questions=(
        ResearchQuestion("RQ1", "Predict Delay Risk"),
        ResearchQuestion("RQ2", "Delay Factors"),
        ResearchQuestion("RQ3", "Operational Differences"),
        ResearchQuestion("RQ4", "Model Explainability"),
        ResearchQuestion("RQ5", "Operational Prioritization"),
    ),
)

METHODOLOGY: Final[InfoSection] = InfoSection(
    title="Methodology",
    icon_id=ICON_METHODOLOGY,
    paragraphs=(),
)

METHODOLOGY_STEPS: Final[tuple[str, ...]] = (
    "Business Understanding",
    "Data Ingestion",
    "Data Profiling",
    "Data Cleaning",
    "Statistical Analysis",
    "Feature Engineering",
    "Predictive Modeling",
    "Model Evaluation",
    "SHAP Explainability",
    "Operational Prioritization",
    "Dashboard Data Preparation",
)

TECH_STACK_SECTION: Final[TechStackSection] = TechStackSection(
    title="Technology Stack",
    icon_id=ICON_TECH_STACK,
    items=(
        TechStackItem("Databricks", TECH_ICON_DATABRICKS),
        TechStackItem("Delta Lake", TECH_ICON_DELTA_LAKE),
        TechStackItem("PySpark", TECH_ICON_PYSPARK),
        TechStackItem("Python", TECH_ICON_PYTHON),
        TechStackItem("XGBoost", TECH_ICON_XGBOOST),
        TechStackItem("SHAP", TECH_ICON_SHAP),
        TechStackItem("SciPy MILP", TECH_ICON_PYTHON),
        TechStackItem("FastAPI", TECH_ICON_FASTAPI),
        TechStackItem("Streamlit", TECH_ICON_STREAMLIT),
        TechStackItem("GitHub", TECH_ICON_GITHUB),
    ),
)

TEAM_SECTION: Final[TeamSection] = TeamSection(
    title="Team Members",
    icon_id=ICON_TEAM,
    members=(
        TeamMember("Daniel Montero", "team/daniel_montero.jpg"),
        TeamMember("Christianel Viaje", "team/christianel_viaje.jpg"),
        TeamMember("Alexis Baquidan", "team/alexis_baquidan.jpg"),
        TeamMember("Navpreet", "team/navpreet.jpg"),
    ),
)

PROJECT_OVERVIEW: Final[ProjectOverviewContent] = ProjectOverviewContent(
    business_objective=BUSINESS_OBJECTIVE,
    dataset=DATASET_INFORMATION,
    prediction_target=PREDICTION_TARGET,
    research_questions=RESEARCH_QUESTIONS,
    methodology=METHODOLOGY,
    methodology_steps=METHODOLOGY_STEPS,
    tech_stack=TECH_STACK_SECTION,
    team=TEAM_SECTION,
)

def team_photo_path(member: TeamMember):
    """Return the on-disk path for a team member photo."""
    return asset_path(member.photo_file)


def tech_icon_path(icon_key: str):
    """Return the on-disk path for a tech stack SVG logo."""
    return asset_path("tech", f"{icon_key}.svg")
