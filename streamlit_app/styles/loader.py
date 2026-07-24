"""Load and inject modular CSS bundles into the Streamlit app shell."""

from pathlib import Path

import streamlit as st

STYLE_FILES = (
    "base.css",
    "components.css",
    "explorer.css",
    "project_info.css",
)


def load_styles() -> None:
    """Read stylesheet modules in order and inject a single style block."""
    styles_dir = Path(__file__).parent
    css_chunks = []

    for filename in STYLE_FILES:
        stylesheet = styles_dir / filename
        if stylesheet.exists():
            css_chunks.append(stylesheet.read_text(encoding="utf-8"))

    if css_chunks:
        st.markdown(f"<style>{''.join(css_chunks)}</style>", unsafe_allow_html=True)
