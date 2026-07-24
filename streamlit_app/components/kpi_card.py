import streamlit as st


def render_kpi_card(
    title: str,
    value: str,
    subtext: str,
    is_positive: bool = True,
) -> None:
    """Render a KPI metric card with trend delta."""
    delta_class = "kpi-card__delta--positive" if is_positive else "kpi-card__delta--negative"
    display_value = value if value.startswith("(") else f"({value})"

    st.markdown(
        f"""
        <div class="surface-card kpi-card">
            <div class="kpi-card__title">{title}</div>
            <div class="kpi-card__value">{display_value}</div>
            <div class="kpi-card__delta {delta_class}">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
