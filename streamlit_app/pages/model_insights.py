"""Model Insights page."""

from __future__ import annotations

import streamlit as st

from components.model_insights_panel import (
    render_global_feature_importance_panel,
    render_local_prediction_explanation_panel,
    render_model_insights_error,
)
from services.prototype_data import (
    get_global_feature_importance,
    get_local_prediction_explanation,
)


def render_model_insights_page() -> None:
    """Render the Model Insights page using prototype SHAP data."""

    st.markdown(
        """
        <div class="page-subtitle page-subtitle--model-insights">
            Global and local SHAP explainability for delay-risk predictions
        </div>
        """,
        unsafe_allow_html=True,
    )

    global_column, local_column = st.columns(
        [1, 1],
        gap="large",
    )

    try:
        feature_importance = get_global_feature_importance()
        local_explanation = get_local_prediction_explanation()
    except Exception:
        render_model_insights_error(
            "The prototype explainability data could not be loaded."
        )
        return

    with global_column:
        try:
            render_global_feature_importance_panel(
                feature_importance
            )
        except (TypeError, ValueError) as exc:
            render_model_insights_error(str(exc))
        except Exception:
            render_model_insights_error(
                "The global feature-importance chart could not be rendered."
            )

    with local_column:
        try:
            render_local_prediction_explanation_panel(
                local_explanation
            )
        except (TypeError, ValueError) as exc:
            render_model_insights_error(str(exc))
        except Exception:
            render_model_insights_error(
                "The local prediction explanation could not be rendered."
            )