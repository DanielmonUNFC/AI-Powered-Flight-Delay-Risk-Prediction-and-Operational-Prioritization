"""Reusable panels for delay prediction results."""

from __future__ import annotations

import html
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Any

from components.prediction_gauge import (
    build_prediction_gauge_html,
)
from components.surface_card import render_html_panel
from styles.theme import COLORS
from styles.typography import typography_css_variables


_PREDICTION_CSS_PATH = (
    Path(__file__).resolve().parents[1]
    / "styles"
    / "delay_prediction.css"
)

_RISK_COLORS = {
    "LOW": "#69b27f",
    "MEDIUM": "#d0ad63",
    "HIGH": "#d47a6b",
    "CRITICAL": "#a95656",
}


def render_prediction_placeholder() -> None:
    """Render the empty state before a prediction is submitted."""

    body_html = """
        <div class="prediction-placeholder">
            Enter the flight parameters and select Predict Delay Risk
            to request a live prediction.
        </div>
    """

    render_html_panel(
        title="Risk Assessment Diagnostic",
        icon_id="delay_prediction",
        body_html=body_html,
        height=410,
        fill_height=True,
        extra_css=_prediction_component_css(),
    )


def render_recommendation_placeholder() -> None:
    """Render the empty operational recommendation state."""

    body_html = """
        <div
            class="
                prediction-placeholder
                prediction-placeholder--recommendation
            "
        >
            Operational recommendations will appear after a prediction
            is generated.
        </div>
    """

    render_html_panel(
        title="Recommended Operational Action",
        icon_id="insight",
        body_html=body_html,
        height=190,
        fill_height=True,
        extra_css=_prediction_component_css(),
    )


def render_prediction_result(
    result: Mapping[str, Any],
) -> None:
    """Render a completed delay-risk prediction."""

    probability = _get_probability(result)
    probability_label = _get_probability_percentage(
        result,
        probability,
    )
    risk_level = _get_risk_level(result)
    risk_color = _get_risk_color(risk_level)

    body_html = build_prediction_gauge_html(
        probability=probability,
        probability_label=probability_label,
        risk_level=risk_level,
        risk_color=risk_color,
    )

    render_html_panel(
        title="Risk Assessment Diagnostic",
        icon_id="delay_prediction",
        body_html=body_html,
        height=410,
        fill_height=True,
        extra_css=_prediction_component_css(),
    )


def render_recommendation_result(
    result: Mapping[str, Any],
) -> None:
    """Render the recommendation associated with a prediction."""

    recommendation = html.escape(
        str(
            result.get(
                "recommended_action",
                "No operational recommendation is currently available.",
            )
        )
    )

    provenance = html.escape(str(result.get("provenance_note", "")))
    extrapolation = ""
    if result.get("is_temporal_extrapolation"):
        extrapolation = (
            '<span class="prediction-recommendation__text">'
            'Future-date estimate: operational conditions after the reference '
            'date are not observed.</span>'
        )
    body_html = f"""
        <div class="prediction-recommendation">
            <span class="prediction-recommendation__label">
                Recommended action
            </span>

            <span class="prediction-recommendation__text">
                {recommendation}
            </span>
            <span class="prediction-recommendation__text">{provenance}</span>
            {extrapolation}
        </div>
    """

    render_html_panel(
        title="Recommended Operational Action",
        icon_id="insight",
        body_html=body_html,
        height=190,
        fill_height=True,
        extra_css=_prediction_component_css(),
    )


def _get_probability(
    result: Mapping[str, Any],
) -> float:
    """Read and validate the numeric prediction probability."""

    try:
        probability = float(result["probability"])
    except KeyError as exc:
        raise ValueError(
            "Prediction response is missing the probability field."
        ) from exc
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Prediction probability must be numeric."
        ) from exc

    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "Prediction probability must be between 0 and 1."
        )

    return probability


def _get_probability_percentage(
    result: Mapping[str, Any],
    probability: float,
) -> str:
    """Return the display-ready probability percentage."""

    supplied_value = result.get("probability_pct")

    if supplied_value not in (None, ""):
        return str(supplied_value)

    return f"{probability * 100:.1f}%"


def _get_risk_level(
    result: Mapping[str, Any],
) -> str:
    """Read and normalize the operational risk level."""

    risk_level = str(
        result.get("risk_level", "UNKNOWN")
    ).strip().upper()

    if risk_level not in _RISK_COLORS:
        return "UNKNOWN"

    return risk_level


def _get_risk_color(
    risk_level: str,
) -> str:
    """Return the display color for an operational risk level."""

    return _RISK_COLORS.get(
        risk_level,
        COLORS["text_muted"],
    )


@lru_cache(maxsize=1)
def _load_prediction_stylesheet() -> str:
    """Read the prediction stylesheet once per process."""

    try:
        return _PREDICTION_CSS_PATH.read_text(
            encoding="utf-8"
        )
    except OSError as exc:
        raise RuntimeError(
            "Unable to load the Delay Prediction stylesheet from "
            f"{_PREDICTION_CSS_PATH}."
        ) from exc


@lru_cache(maxsize=1)
def _prediction_component_css() -> str:
    """Return iframe-ready prediction styles."""

    theme_variables = f"""
        {typography_css_variables()}
        :root {{
            --prediction-text-primary:
                {COLORS["text_primary"]};
            --prediction-text-secondary:
                {COLORS["text_secondary"]};
            --prediction-text-muted:
                {COLORS["text_muted"]};
            --prediction-accent:
                {COLORS["accent_bright"]};
            --prediction-border-subtle:
                {COLORS["border_subtle"]};
        }}
    """

    return (
        theme_variables
        + "\n"
        + _load_prediction_stylesheet()
    )
