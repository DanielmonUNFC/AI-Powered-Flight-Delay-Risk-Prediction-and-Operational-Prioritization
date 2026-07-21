"""Static content for the Project Information dashboard tab.

Edit this file to update copy, team members, methodology steps, or tech stack
without touching layout components.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from config.panel_icons import (
    ICON_METHODOLOGY,
    ICON_OBJECTIVE,
    ICON_TEAM,
    ICON_TECH_STACK,
    TECH_ICON_DATABRICKS,
    TECH_ICON_FASTAPI,
    TECH_ICON_ORTOOLS,
    TECH_ICON_PYSPARK,
    TECH_ICON_PYTHON,
    TECH_ICON_SHAP,
    TECH_ICON_STREAMLIT,
    TECH_ICON_XGBOOST,
)
from utils.media import asset_path


@dataclass(frozen=True)
class InfoSection:
    """Text block shown inside a project information panel."""

    title: str
    icon_id: str
    paragraphs: tuple[str, ...]


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
class ProjectInformationContent:
    """All predefined content for the Project Information tab."""

    business_objective: InfoSection
    methodology: InfoSection
    methodology_steps: tuple[str, ...]
    team: TeamSection
    tech_stack: TechStackSection


BUSINESS_OBJECTIVE: Final[InfoSection] = InfoSection(
    title="Business & Technical Objective",
    icon_id=ICON_OBJECTIVE,
    paragraphs=(
        (
            "Develop an AI-powered decision support system that estimates the probability "
            "that a scheduled flight will arrive at least 15 minutes late (ArrDel15) before "
            "departure, using the 2025 BTS Airline On-Time Performance dataset. The system "
            "helps airline operations managers prioritize high-risk flights when operational "
            "review capacity is limited—moving from reactive reporting to proactive, "
            "evidence-based planning."
        ),
        (
            "Technically, the project implements the full analytics lifecycle: data "
            "acquisition and cleaning on Databricks/PySpark, schedule-time feature "
            "engineering with a target-leakage audit, descriptive and diagnostic analytics, "
            "predictive modeling (Logistic Regression, Random Forest, XGBoost), SHAP "
            "explainability, and prescriptive optimization (OR-Tools), integrated through "
            "a FastAPI backend and this executive Streamlit dashboard."
        ),
    ),
)

METHODOLOGY: Final[InfoSection] = InfoSection(
    title="Methodology",
    icon_id=ICON_METHODOLOGY,
    paragraphs=(),
)

METHODOLOGY_STEPS: Final[tuple[str, ...]] = (
    "BTS Data Ingestion",
    "Data Cleaning",
    "Feature Engineering",
    "Leakage Audit",
    "Descriptive Analytics",
    "Predictive Modeling",
    "SHAP Explainability",
    "Prescriptive Optimization",
)

TEAM_SECTION: Final[TeamSection] = TeamSection(
    title="Capstone Team Members",
    icon_id=ICON_TEAM,
    members=(
        TeamMember("Daniel Montero", "team/daniel_montero.jpg"),
        TeamMember("Christianel Viaje", "team/christianel_viaje.jpg"),
        TeamMember("Alexis Baquidan", "team/alexis_baquidan.jpg"),
        TeamMember("Navpreet", "team/navpreet.jpg"),
    ),
)

TECH_STACK_SECTION: Final[TechStackSection] = TechStackSection(
    title="Tech Stack",
    icon_id=ICON_TECH_STACK,
    items=(
        TechStackItem("Databricks", TECH_ICON_DATABRICKS),
        TechStackItem("PySpark", TECH_ICON_PYSPARK),
        TechStackItem("Python", TECH_ICON_PYTHON),
        TechStackItem("XGBoost", TECH_ICON_XGBOOST),
        TechStackItem("SHAP", TECH_ICON_SHAP),
        TechStackItem("OR-Tools", TECH_ICON_ORTOOLS),
        TechStackItem("FastAPI", TECH_ICON_FASTAPI),
        TechStackItem("Streamlit", TECH_ICON_STREAMLIT),
    ),
)

PROJECT_INFORMATION: Final[ProjectInformationContent] = ProjectInformationContent(
    business_objective=BUSINESS_OBJECTIVE,
    methodology=METHODOLOGY,
    methodology_steps=METHODOLOGY_STEPS,
    team=TEAM_SECTION,
    tech_stack=TECH_STACK_SECTION,
)


def team_photo_path(member: TeamMember):
    """Return the on-disk path for a team member photo."""
    return asset_path(member.photo_file)


def tech_icon_path(icon_key: str):
    """Return the on-disk path for a tech stack SVG logo."""
    return asset_path("tech", f"{icon_key}.svg")
