"""Load Streamlit environment variables from streamlit_app/.env."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

STREAMLIT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(STREAMLIT_ENV_PATH)
