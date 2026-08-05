from typing import Optional

import streamlit as st


def render_kpi_card(
    title: str,
    value: str,
    subtext: Optional[str] = None,
    is_positive: bool = True,
) -> None:
    """Render a KPI metric card with an optional trend delta."""
    display_value = value if value.startswith("(") else f"({value})"

    delta_html = ""
    if subtext:
        delta_class = (
            "kpi-card__delta--positive" if is_positive else "kpi-card__delta--negative"
        )
        delta_html = f'<div class="kpi-card__delta {delta_class}">{subtext}</div>'

    st.markdown(
        f"""
        <div class="surface-card kpi-card">
            <div class="kpi-card__title">{title}</div>
            <div class="kpi-card__value">{display_value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
