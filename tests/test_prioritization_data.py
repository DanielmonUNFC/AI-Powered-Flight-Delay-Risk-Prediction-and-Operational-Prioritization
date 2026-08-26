"""Tests for Streamlit prioritization payload transformations."""

from __future__ import annotations

import sys
from pathlib import Path


STREAMLIT_ROOT = Path(__file__).resolve().parents[1] / "streamlit_app"
sys.path.insert(0, str(STREAMLIT_ROOT))

from services.prioritization_data import _transform_table_meta  # noqa: E402


def test_prioritization_table_metadata_is_preserved() -> None:
    result = _transform_table_meta(
        {
            "count": 25,
            "total_count": 25,
            "queue_size": 10_000,
            "display_limit": 500,
            "flights": [],
            "summary": {
                "flights_selected": 25,
                "flights_in_queue": 10_000,
            },
        }
    )

    assert result.displayed_count == 25
    assert result.selected_count == 25
    assert result.queue_size == 10_000
    assert result.display_limit == 500
