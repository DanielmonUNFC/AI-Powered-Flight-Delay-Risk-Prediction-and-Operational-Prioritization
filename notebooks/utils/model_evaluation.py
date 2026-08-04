"""Reusable model-evaluation helpers for calibration, thresholds, and subgroups."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


def brier_score(y_true: pd.Series, y_prob: pd.Series) -> float:
    """Calculate the Brier score for binary probability forecasts."""
    labels = y_true.astype(float).to_numpy()
    probabilities = y_prob.astype(float).to_numpy()
    return float(np.mean((probabilities - labels) ** 2))


def calibration_summary(
    y_true: pd.Series,
    y_prob: pd.Series,
    n_bins: int = 10,
) -> pd.DataFrame:
    """Summarize predicted versus observed delay rates by probability bin."""
    frame = pd.DataFrame(
        {
            "label": y_true.astype(float),
            "probability": y_prob.astype(float),
        }
    )
    frame["bin"] = pd.cut(
        frame["probability"],
        bins=n_bins,
        labels=False,
        include_lowest=True,
    )

    summary = (
        frame.groupby("bin", dropna=False)
        .agg(
            predicted_probability=("probability", "mean"),
            observed_rate=("label", "mean"),
            flight_count=("label", "count"),
        )
        .reset_index()
    )
    summary["bin"] = summary["bin"].astype("Int64")
    return summary


def plot_calibration_curve(
    y_true: pd.Series,
    y_prob: pd.Series,
    n_bins: int = 10,
):
    """Plot a reliability diagram for binary probability forecasts."""
    import matplotlib.pyplot as plt

    summary = calibration_summary(y_true, y_prob, n_bins=n_bins)
    figure, axis = plt.subplots(figsize=(6, 5))
    axis.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        color="gray",
        label="Perfect calibration",
    )
    axis.plot(
        summary["predicted_probability"],
        summary["observed_rate"],
        marker="o",
        label="Model calibration",
    )
    axis.set_xlabel("Mean predicted delay probability")
    axis.set_ylabel("Observed delay rate")
    axis.set_title("Calibration plot")
    axis.legend()
    axis.grid(alpha=0.3)
    figure.tight_layout()
    return figure


def threshold_search(
    y_true: pd.Series,
    y_prob: pd.Series,
    threshold_min: float = 0.10,
    threshold_max: float = 0.90,
    threshold_step: float = 0.05,
) -> pd.DataFrame:
    """Search decision thresholds and return delay-focused metrics."""
    labels = y_true.astype(int).to_numpy()
    probabilities = y_prob.astype(float).to_numpy()
    thresholds = np.arange(
        threshold_min,
        threshold_max + threshold_step,
        threshold_step,
    )

    rows: list[dict[str, float]] = []
    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(int)
        true_positives = np.sum((predictions == 1) & (labels == 1))
        false_positives = np.sum((predictions == 1) & (labels == 0))
        false_negatives = np.sum((predictions == 0) & (labels == 1))

        precision = (
            true_positives / (true_positives + false_positives)
            if true_positives + false_positives > 0
            else 0.0
        )
        recall = (
            true_positives / (true_positives + false_negatives)
            if true_positives + false_negatives > 0
            else 0.0
        )
        f1_score = (
            2 * precision * recall / (precision + recall)
            if precision + recall > 0
            else 0.0
        )

        rows.append(
            {
                "threshold": float(threshold),
                "delay_precision": float(precision),
                "delay_recall": float(recall),
                "delay_f1": float(f1_score),
            }
        )

    return pd.DataFrame(rows)


def lift_at_top_percentiles(
    y_true: pd.Series,
    y_prob: pd.Series,
    percentiles: Iterable[float],
) -> pd.DataFrame:
    """Calculate recall and lift within the highest predicted-risk groups."""
    frame = pd.DataFrame(
        {
            "label": y_true.astype(int),
            "probability": y_prob.astype(float),
        }
    ).sort_values("probability", ascending=False)

    baseline_rate = frame["label"].mean()
    total_delays = frame["label"].sum()
    rows: list[dict[str, float]] = []

    for percentile in percentiles:
        top_count = max(int(len(frame) * percentile), 1)
        top_group = frame.head(top_count)
        captured_delays = top_group["label"].sum()
        recall = captured_delays / total_delays if total_delays > 0 else 0.0
        observed_rate = top_group["label"].mean()
        lift = observed_rate / baseline_rate if baseline_rate > 0 else 0.0

        rows.append(
            {
                "top_percent": float(percentile),
                "flight_count": float(top_count),
                "observed_delay_rate": float(observed_rate),
                "delay_recall": float(recall),
                "lift": float(lift),
            }
        )

    return pd.DataFrame(rows)


def subgroup_error_analysis(
    frame: pd.DataFrame,
    group_columns: Iterable[str],
    label_column: str,
    probability_column: str,
    threshold: float,
    min_group_size: int = 100,
) -> pd.DataFrame:
    """Summarize delay recall and calibration error by operational subgroup."""
    working = frame.copy()
    working["prediction"] = (
        working[probability_column].astype(float) >= threshold
    ).astype(int)
    working["label"] = working[label_column].astype(int)

    rows: list[dict[str, float | str]] = []
    for group_column in group_columns:
        grouped = working.groupby(group_column, dropna=False)
        for group_value, group_frame in grouped:
            if len(group_frame) < min_group_size:
                continue

            true_positives = (
                (group_frame["prediction"] == 1) & (group_frame["label"] == 1)
            ).sum()
            actual_positives = (group_frame["label"] == 1).sum()
            predicted_positives = (group_frame["prediction"] == 1).sum()

            recall = (
                true_positives / actual_positives
                if actual_positives > 0
                else 0.0
            )
            precision = (
                true_positives / predicted_positives
                if predicted_positives > 0
                else 0.0
            )

            rows.append(
                {
                    "subgroup_type": group_column,
                    "subgroup_value": str(group_value),
                    "flight_count": float(len(group_frame)),
                    "delay_rate": float(group_frame["label"].mean()),
                    "mean_predicted_probability": float(
                        group_frame[probability_column].mean()
                    ),
                    "delay_recall": float(recall),
                    "delay_precision": float(precision),
                }
            )

    return pd.DataFrame(rows).sort_values(
        ["subgroup_type", "delay_recall"],
        ascending=[True, True],
    )


def confusion_matrix_summary(
    y_true: pd.Series,
    y_pred: pd.Series,
) -> pd.DataFrame:
    """Build a labeled confusion matrix for binary classification."""
    labels = y_true.astype(int).to_numpy()
    predictions = y_pred.astype(int).to_numpy()

    true_negatives = int(np.sum((predictions == 0) & (labels == 0)))
    false_positives = int(np.sum((predictions == 1) & (labels == 0)))
    false_negatives = int(np.sum((predictions == 0) & (labels == 1)))
    true_positives = int(np.sum((predictions == 1) & (labels == 1)))

    return pd.DataFrame(
        [
            {
                "actual_on_time_predicted_on_time": true_negatives,
                "actual_on_time_predicted_delayed": false_positives,
                "actual_delayed_predicted_on_time": false_negatives,
                "actual_delayed_predicted_delayed": true_positives,
            }
        ]
    )


def plot_confusion_matrix(
    y_true: pd.Series,
    y_pred: pd.Series,
):
    """Plot a binary confusion matrix heatmap."""
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

    matrix = confusion_matrix(
        y_true.astype(int),
        y_pred.astype(int),
        labels=[0, 1],
    )
    figure, axis = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=["On-time", "Delayed"],
    ).plot(ax=axis, colorbar=False, cmap="Blues")
    axis.set_title("Holdout confusion matrix")
    figure.tight_layout()
    return figure


def plot_roc_pr_curves(
    y_true: pd.Series,
    y_prob: pd.Series,
):
    """Plot ROC and precision-recall curves for binary probabilities."""
    import matplotlib.pyplot as plt
    from sklearn.metrics import (
        PrecisionRecallDisplay,
        RocCurveDisplay,
        average_precision_score,
        roc_auc_score,
    )

    labels = y_true.astype(int).to_numpy()
    probabilities = y_prob.astype(float).to_numpy()

    figure, axes = plt.subplots(1, 2, figsize=(12, 5))

    RocCurveDisplay.from_predictions(
        labels,
        probabilities,
        ax=axes[0],
        name="Logistic Regression",
    )
    axes[0].set_title(
        f"ROC curve (AUC={roc_auc_score(labels, probabilities):.4f})"
    )

    PrecisionRecallDisplay.from_predictions(
        labels,
        probabilities,
        ax=axes[1],
        name="Logistic Regression",
    )
    axes[1].set_title(
        "Precision-recall curve "
        f"(AP={average_precision_score(labels, probabilities):.4f})"
    )

    figure.tight_layout()
    return figure

