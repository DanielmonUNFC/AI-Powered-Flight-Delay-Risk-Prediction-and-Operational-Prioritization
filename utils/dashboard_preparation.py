"""Dashboard dataset builders for notebook 11."""

from __future__ import annotations

import json
from typing import Iterable

import pandas as pd


MONTH_LABELS = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def build_overview_kpi_records(
    *,
    total_flights: int,
    delay_rate: float,
    average_arrival_delay: float,
    cancellation_rate: float,
) -> pd.DataFrame:
    """Create overview KPI records for the dashboard table."""
    rows = [
        ("overview_kpi", "total_flights", float(total_flights), str(total_flights), None, None, 1),
        ("overview_kpi", "avg_delay_rate", delay_rate, f"{delay_rate:.1f}%", None, None, 2),
        ("overview_kpi", "avg_arr_delay", average_arrival_delay, f"{average_arrival_delay:.1f} min", None, None, 3),
        ("overview_kpi", "cancel_rate", cancellation_rate, f"{cancellation_rate:.2f}%", None, None, 4),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "section",
            "metric_name",
            "metric_value",
            "metric_text",
            "dimension_1",
            "dimension_2",
            "sort_order",
        ],
    )


def build_monthly_trend_records(monthly_frame: pd.DataFrame) -> pd.DataFrame:
    """Convert monthly delay-rate aggregates into dashboard records."""
    records = monthly_frame.copy()
    records["section"] = "monthly_trend"
    records["metric_name"] = "delay_rate"
    records["metric_value"] = records["delay_rate"]
    records["metric_text"] = records["month_label"]
    records["dimension_1"] = records["month_label"]
    records["dimension_2"] = None
    records["sort_order"] = records["month_number"]
    return records[
        [
            "section",
            "metric_name",
            "metric_value",
            "metric_text",
            "dimension_1",
            "dimension_2",
            "sort_order",
        ]
    ]


def build_delay_cause_records(cause_frame: pd.DataFrame) -> pd.DataFrame:
    """Convert delay-cause aggregates into dashboard records."""
    records = cause_frame.copy()
    records["section"] = "delay_cause"
    records["metric_name"] = "delay_minutes_share"
    records["metric_value"] = records["percentage"]
    records["metric_text"] = records["cause"]
    records["dimension_1"] = records["cause"]
    records["dimension_2"] = None
    records["sort_order"] = range(1, len(records) + 1)
    return records[
        [
            "section",
            "metric_name",
            "metric_value",
            "metric_text",
            "dimension_1",
            "dimension_2",
            "sort_order",
        ]
    ]


def build_research_validation_records(
    validation_frame: pd.DataFrame,
) -> pd.DataFrame:
    """Convert statistical or prioritization validation outputs into dashboard records."""
    records = validation_frame.copy()
    records["section"] = "research_validation"
    records["metric_name"] = records.get("metric_name", records.get("research_question", "validation"))
    records["metric_value"] = records.get("metric_value", records.get("delay_recall", 0.0))
    records["metric_text"] = records.get("metric_text", records.get("decision", ""))
    records["dimension_1"] = records.get("dimension_1", records.get("research_question", ""))
    records["dimension_2"] = records.get("dimension_2", records.get("strategy", ""))
    records["sort_order"] = range(1, len(records) + 1)
    return records[
        [
            "section",
            "metric_name",
            "metric_value",
            "metric_text",
            "dimension_1",
            "dimension_2",
            "sort_order",
        ]
    ]


def build_model_metric_records(model_metrics: dict[str, object]) -> pd.DataFrame:
    """Flatten model metric JSON into dashboard records."""
    rows = []
    sort_order = 1
    for metric_name, metric_value in model_metrics.items():
        if isinstance(metric_value, dict):
            continue
        rows.append(
            (
                "model_metric",
                metric_name,
                float(metric_value),
                str(metric_value),
                None,
                None,
                sort_order,
            )
        )
        sort_order += 1
    return pd.DataFrame(
        rows,
        columns=[
            "section",
            "metric_name",
            "metric_value",
            "metric_text",
            "dimension_1",
            "dimension_2",
            "sort_order",
        ],
    )


def combine_dashboard_records(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    """Combine multiple dashboard record frames."""
    valid_frames = [frame for frame in frames if not frame.empty]
    if not valid_frames:
        return pd.DataFrame(
            columns=[
                "section",
                "metric_name",
                "metric_value",
                "metric_text",
                "dimension_1",
                "dimension_2",
                "sort_order",
            ]
        )
    return pd.concat(valid_frames, ignore_index=True)


def serialize_dashboard_metadata(payload: dict[str, object]) -> str:
    """Serialize dashboard metadata for storage alongside Delta tables."""
    return json.dumps(payload, indent=4)
