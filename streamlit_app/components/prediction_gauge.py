"""SVG delay-risk gauge component."""

from __future__ import annotations

import html


_GAUGE_CENTER_X = 260
_GAUGE_CENTER_Y = 235


def build_prediction_gauge_html(
    *,
    probability: float,
    probability_label: str,
    risk_level: str,
    risk_color: str,
) -> str:
    """
    Build the SVG gauge markup for a delay-risk prediction.

    Parameters
    ----------
    probability:
        Numeric probability between 0 and 1.
    probability_label:
        Display-ready percentage, such as ``"74.2%"``.
    risk_level:
        Normalized risk category.
    risk_color:
        CSS-compatible color for the risk category.
    """

    _validate_probability(probability)

    safe_probability_label = html.escape(probability_label)
    safe_risk_level = html.escape(risk_level)
    safe_risk_color = html.escape(risk_color)

    marker_angle = _probability_to_marker_angle(probability)

    return f"""
        <div class="prediction-result">
            <svg
                class="prediction-gauge"
                viewBox="0 0 520 320"
                role="img"
                aria-label="
                    Delay probability {safe_probability_label},
                    {safe_risk_level} risk
                "
            >
                {_build_svg_definitions()}

                <path
                    d="M 90 235 A 170 170 0 0 1 430 235"
                    fill="none"
                    stroke="#354055"
                    stroke-width="44"
                    opacity="0.40"
                />

                <path
                    d="M 90 235 A 170 170 0 0 1 430 235"
                    fill="none"
                    stroke="url(#riskGradient)"
                    stroke-width="44"
                    filter="url(#gaugeGlow)"
                />

                <g
                    transform="
                        rotate(
                            {marker_angle:.2f}
                            {_GAUGE_CENTER_X}
                            {_GAUGE_CENTER_Y}
                        )
                    "
                >
                    <line
                        x1="405"
                        y1="235"
                        x2="452"
                        y2="235"
                        stroke="#f4f6fb"
                        stroke-width="5"
                        stroke-linecap="round"
                        filter="url(#markerGlow)"
                    />
                </g>

                <text
                    x="260"
                    y="165"
                    text-anchor="middle"
                    class="prediction-gauge__value"
                >
                    {safe_probability_label}
                </text>

                <text
                    x="260"
                    y="197"
                    text-anchor="middle"
                    class="prediction-gauge__caption"
                >
                    probability
                </text>

                <text
                    x="260"
                    y="270"
                    text-anchor="middle"
                    class="prediction-gauge__risk"
                    fill="{safe_risk_color}"
                >
                    {safe_risk_level} RISK
                </text>
            </svg>

            <div class="prediction-risk-scale">
                <span>LOW</span>
                <span>MEDIUM</span>
                <span>HIGH</span>
                <span>CRITICAL</span>
            </div>
        </div>
    """


def _probability_to_marker_angle(probability: float) -> float:
    """
    Convert probability to the SVG marker angle.

    The arc mapping is:

    - 0% = left side;
    - 50% = top centre;
    - 100% = right side.
    """

    return 180.0 + (probability * 180.0)


def _validate_probability(probability: float) -> None:
    """Validate the gauge probability."""

    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "Gauge probability must be between 0 and 1."
        )


def _build_svg_definitions() -> str:
    """Return shared gradient and glow definitions for the SVG."""

    return """
        <defs>
            <linearGradient
                id="riskGradient"
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
            >
                <stop
                    offset="0%"
                    stop-color="#69b27f"
                />
                <stop
                    offset="22%"
                    stop-color="#8fbd68"
                />
                <stop
                    offset="40%"
                    stop-color="#d0ad63"
                />
                <stop
                    offset="62%"
                    stop-color="#d98a62"
                />
                <stop
                    offset="80%"
                    stop-color="#d47a6b"
                />
                <stop
                    offset="100%"
                    stop-color="#a95656"
                />
            </linearGradient>

            <filter
                id="gaugeGlow"
                x="-30%"
                y="-30%"
                width="160%"
                height="160%"
            >
                <feGaussianBlur
                    stdDeviation="6"
                    result="blur"
                />
                <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                </feMerge>
            </filter>

            <filter
                id="markerGlow"
                x="-60%"
                y="-60%"
                width="220%"
                height="220%"
            >
                <feGaussianBlur
                    stdDeviation="2"
                    result="blur"
                />
                <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                </feMerge>
            </filter>
        </defs>
    """