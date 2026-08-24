"""Clear, reusable helpers for the standard-Python model-training notebook."""

from __future__ import annotations

import json
import time
import warnings
from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def _python_value(value: Any) -> Any:
    """Convert NumPy scalars to JSON-compatible Python values."""
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _python_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_python_value(item) for item in value]
    return value


def parameters_json(parameters: dict[str, Any]) -> str:
    """Return deterministic JSON for a model configuration."""
    return json.dumps(_python_value(parameters), sort_keys=True)


def deduplicate_configurations(
    configurations: Iterable[dict[str, Any]],
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Remove repeated configurations while preserving their order."""
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for configuration in configurations:
        key = parameters_json(configuration)
        if key in seen:
            continue
        seen.add(key)
        unique.append(_python_value(configuration))
        if limit is not None and len(unique) >= limit:
            break
    return unique


def build_preprocessor(
    categorical_columns: Sequence[str],
    numerical_columns: Sequence[str],
) -> ColumnTransformer:
    """Create one leakage-safe preprocessing object for a training period."""
    categorical_pipeline = Pipeline(
        steps=[
            (
                "one_hot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    min_frequency=20,
                    dtype=np.float32,
                ),
            )
        ]
    )
    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler(with_mean=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("categorical", categorical_pipeline, list(categorical_columns)),
            ("numerical", numerical_pipeline, list(numerical_columns)),
        ],
        sparse_threshold=1.0,
    )


def prepare_model_matrices(
    train_frame: pd.DataFrame,
    validation_frame: pd.DataFrame,
    categorical_columns: Sequence[str],
    numerical_columns: Sequence[str],
    target_column: str,
) -> dict[str, Any]:
    """Fit preprocessing on training only and transform both periods."""
    input_columns = list(categorical_columns) + list(numerical_columns)
    preprocessor = build_preprocessor(categorical_columns, numerical_columns)
    x_train = preprocessor.fit_transform(train_frame[input_columns])
    x_validation = preprocessor.transform(validation_frame[input_columns])
    return {
        "x_train": x_train,
        "y_train": train_frame[target_column].astype(int).to_numpy(),
        "x_validation": x_validation,
        "y_validation": validation_frame[target_column].astype(int).to_numpy(),
        "preprocessor": preprocessor,
    }


def build_estimator(
    model_name: str,
    parameters: dict[str, Any],
    y_train: np.ndarray,
    random_seed: int,
):
    """Build Logistic Regression, Random Forest, or XGBoost consistently."""
    strategy = parameters.get("imbalance_strategy", "natural")

    if model_name == "Logistic Regression":
        import sklearn

        version_parts = tuple(
            int(part) for part in sklearn.__version__.split(".")[:2]
        )
        penalty = str(parameters.get("penalty", "l2"))
        penalty_arguments = (
            {"l1_ratio": 1.0 if penalty == "l1" else 0.0}
            if version_parts >= (1, 8)
            else {"penalty": penalty}
        )
        return LogisticRegression(
            C=float(parameters.get("C", 1.0)),
            solver="liblinear",
            class_weight="balanced" if strategy == "weighted" else None,
            max_iter=1000,
            tol=1e-4,
            random_state=random_seed,
            **penalty_arguments,
        )

    if model_name == "Random Forest":
        return RandomForestClassifier(
            n_estimators=int(parameters.get("n_estimators", 250)),
            max_depth=parameters.get("max_depth"),
            min_samples_split=int(parameters.get("min_samples_split", 2)),
            min_samples_leaf=int(parameters.get("min_samples_leaf", 1)),
            max_features=parameters.get("max_features", "sqrt"),
            class_weight="balanced_subsample" if strategy == "weighted" else None,
            random_state=random_seed,
            n_jobs=-1,
        )

    if model_name == "XGBoost":
        from xgboost import XGBClassifier

        negative_count = max(int(np.sum(y_train == 0)), 1)
        positive_count = max(int(np.sum(y_train == 1)), 1)
        positive_weight = negative_count / positive_count
        return XGBClassifier(
            n_estimators=int(parameters.get("n_estimators", 350)),
            max_depth=int(parameters.get("max_depth", 5)),
            learning_rate=float(parameters.get("learning_rate", 0.05)),
            min_child_weight=float(parameters.get("min_child_weight", 1.0)),
            subsample=float(parameters.get("subsample", 0.85)),
            colsample_bytree=float(parameters.get("colsample_bytree", 0.85)),
            gamma=float(parameters.get("gamma", 0.0)),
            reg_alpha=float(parameters.get("reg_alpha", 0.0)),
            reg_lambda=float(parameters.get("reg_lambda", 1.0)),
            scale_pos_weight=positive_weight if strategy == "weighted" else 1.0,
            objective="binary:logistic",
            eval_metric="logloss",
            tree_method="hist",
            random_state=random_seed,
            n_jobs=-1,
        )

    raise ValueError(f"Unsupported model: {model_name}")


def classification_metrics(
    y_true: np.ndarray,
    y_probability: np.ndarray,
    threshold: float,
) -> dict[str, float | int]:
    """Calculate proposal-required and operational classification metrics."""
    labels = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(y_probability, dtype=float)
    predictions = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()

    top_count = max(int(np.ceil(len(labels) * 0.10)), 1)
    top_indices = np.argsort(-probabilities)[:top_count]
    total_delays = int(labels.sum())
    top_delays = int(labels[top_indices].sum())
    baseline_rate = float(labels.mean())
    top_delay_rate = float(labels[top_indices].mean())

    return {
        "ACCURACY": float(accuracy_score(labels, predictions)),
        "DELAY_PRECISION": float(
            precision_score(labels, predictions, zero_division=0)
        ),
        "DELAY_RECALL": float(recall_score(labels, predictions, zero_division=0)),
        "DELAY_F1": float(f1_score(labels, predictions, zero_division=0)),
        "ROC_AUC": float(roc_auc_score(labels, probabilities)),
        "PR_AUC": float(average_precision_score(labels, probabilities)),
        "BRIER_SCORE": float(brier_score_loss(labels, probabilities)),
        "TOP_10_RECALL": float(top_delays / total_delays if total_delays else 0.0),
        "TOP_10_LIFT": float(
            top_delay_rate / baseline_rate if baseline_rate else 0.0
        ),
        "ALERT_RATE": float(predictions.mean()),
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "TP": int(tp),
    }


def choose_operational_threshold(
    y_true: np.ndarray,
    y_probability: np.ndarray,
    minimum_recall: float,
    threshold_min: float,
    threshold_max: float,
    threshold_step: float,
) -> tuple[float, pd.DataFrame]:
    """Maximize delayed F1 among thresholds meeting the recall requirement."""
    thresholds = np.arange(
        threshold_min,
        threshold_max + threshold_step / 2,
        threshold_step,
    )
    rows: list[dict[str, float | int]] = []
    for threshold in thresholds:
        row = classification_metrics(y_true, y_probability, float(threshold))
        row["THRESHOLD"] = float(np.round(threshold, 4))
        rows.append(row)

    results = pd.DataFrame(rows)
    eligible = results[results["DELAY_RECALL"] >= minimum_recall]
    if eligible.empty:
        eligible = results.sort_values(
            ["DELAY_RECALL", "DELAY_F1", "DELAY_PRECISION", "THRESHOLD"],
            ascending=[False, False, False, False],
        ).head(1)
    else:
        eligible = eligible.sort_values(
            ["DELAY_F1", "DELAY_PRECISION", "THRESHOLD"],
            ascending=[False, False, False],
        ).head(1)

    return float(eligible.iloc[0]["THRESHOLD"]), results


def choose_f1_threshold(
    y_true: np.ndarray,
    y_probability: np.ndarray,
    threshold_min: float,
    threshold_max: float,
    threshold_step: float,
) -> tuple[float, pd.DataFrame]:
    """Select the validation threshold with the highest delayed-class F1."""
    thresholds = np.arange(
        threshold_min,
        threshold_max + threshold_step / 2,
        threshold_step,
    )
    rows: list[dict[str, float | int]] = []
    for threshold in thresholds:
        row = classification_metrics(y_true, y_probability, float(threshold))
        row["THRESHOLD"] = float(np.round(threshold, 4))
        rows.append(row)

    results = pd.DataFrame(rows)
    winner = results.sort_values(
        ["DELAY_F1", "DELAY_PRECISION", "DELAY_RECALL", "THRESHOLD"],
        ascending=[False, False, False, False],
    ).iloc[0]
    return float(winner["THRESHOLD"]), results


def fit_and_score(
    model_name: str,
    parameters: dict[str, Any],
    prepared_data: dict[str, Any],
    threshold: float,
    random_seed: int,
) -> tuple[Any, np.ndarray, dict[str, float | int], bool, float]:
    """Fit one estimator and score its validation probabilities."""
    estimator = build_estimator(
        model_name,
        parameters,
        prepared_data["y_train"],
        random_seed,
    )
    started = time.perf_counter()
    converged = True
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", ConvergenceWarning)
        estimator.fit(prepared_data["x_train"], prepared_data["y_train"])
        converged = not any(
            issubclass(item.category, ConvergenceWarning) for item in captured
        )
    training_seconds = time.perf_counter() - started
    probabilities = estimator.predict_proba(prepared_data["x_validation"])[:, 1]
    metrics = classification_metrics(
        prepared_data["y_validation"], probabilities, threshold
    )
    return estimator, probabilities, metrics, converged, training_seconds


def evaluate_cv_configuration(
    model_name: str,
    configuration_id: str,
    parameters: dict[str, Any],
    prepared_folds: Sequence[dict[str, Any]],
    minimum_recall: float | None,
    threshold_min: float,
    threshold_max: float,
    threshold_step: float,
    random_seed: int,
    threshold_strategy: str = "recall_constrained_f1",
) -> dict[str, Any]:
    """Evaluate one configuration on every chronological fold."""
    fold_outputs: list[tuple[np.ndarray, np.ndarray, bool, float]] = []
    fold_probability_metrics: list[dict[str, float | int]] = []

    try:
        for fold_number, prepared_fold in enumerate(prepared_folds, start=1):
            _, probabilities, metrics, converged, seconds = fit_and_score(
                model_name=model_name,
                parameters=parameters,
                prepared_data=prepared_fold,
                threshold=0.50,
                random_seed=random_seed + fold_number,
            )
            labels = prepared_fold["y_validation"]
            fold_outputs.append((labels, probabilities, converged, seconds))
            fold_probability_metrics.append(metrics)
            print(
                f"{model_name} {configuration_id} | Fold {fold_number}/"
                f"{len(prepared_folds)} | PR-AUC={metrics['PR_AUC']:.4f} | "
                f"ROC-AUC={metrics['ROC_AUC']:.4f}"
            )

        pooled_labels = np.concatenate([item[0] for item in fold_outputs])
        pooled_probabilities = np.concatenate([item[1] for item in fold_outputs])
        if threshold_strategy == "max_f1":
            threshold, _ = choose_f1_threshold(
                pooled_labels,
                pooled_probabilities,
                threshold_min,
                threshold_max,
                threshold_step,
            )
        elif threshold_strategy == "recall_constrained_f1":
            if minimum_recall is None:
                raise ValueError(
                    "minimum_recall is required for recall-constrained F1."
                )
            threshold, _ = choose_operational_threshold(
                pooled_labels,
                pooled_probabilities,
                minimum_recall,
                threshold_min,
                threshold_max,
                threshold_step,
            )
        else:
            raise ValueError(
                f"Unsupported threshold strategy: {threshold_strategy}"
            )
        threshold_metrics = [
            classification_metrics(labels, probabilities, threshold)
            for labels, probabilities, _, _ in fold_outputs
        ]

        def mean_metric(name: str) -> float:
            return float(np.mean([row[name] for row in threshold_metrics]))

        def probability_mean(name: str) -> float:
            return float(np.mean([row[name] for row in fold_probability_metrics]))

        return {
            "MODEL": model_name,
            "CONFIGURATION_ID": configuration_id,
            "PARAMETERS": parameters_json(parameters),
            "STATUS": "OK",
            "CONVERGED": bool(all(item[2] for item in fold_outputs)),
            "FOLDS": int(len(prepared_folds)),
            "DECISION_THRESHOLD": threshold,
            "PR_AUC_MEAN": probability_mean("PR_AUC"),
            "PR_AUC_STD": float(
                np.std([row["PR_AUC"] for row in fold_probability_metrics])
            ),
            "ROC_AUC_MEAN": probability_mean("ROC_AUC"),
            "BRIER_SCORE_MEAN": probability_mean("BRIER_SCORE"),
            "DELAY_PRECISION_MEAN": mean_metric("DELAY_PRECISION"),
            "DELAY_RECALL_MEAN": mean_metric("DELAY_RECALL"),
            "DELAY_F1_MEAN": mean_metric("DELAY_F1"),
            "TOP_10_RECALL_MEAN": probability_mean("TOP_10_RECALL"),
            "TOP_10_LIFT_MEAN": probability_mean("TOP_10_LIFT"),
            "TRAINING_SECONDS": float(sum(item[3] for item in fold_outputs)),
            "ERROR": "",
        }
    except Exception as error:  # keep the search running if one configuration fails
        print(f"{model_name} {configuration_id} failed: {error}")
        return {
            "MODEL": model_name,
            "CONFIGURATION_ID": configuration_id,
            "PARAMETERS": parameters_json(parameters),
            "STATUS": "ERROR",
            "CONVERGED": False,
            "FOLDS": int(len(prepared_folds)),
            "DECISION_THRESHOLD": np.nan,
            "PR_AUC_MEAN": np.nan,
            "PR_AUC_STD": np.nan,
            "ROC_AUC_MEAN": np.nan,
            "BRIER_SCORE_MEAN": np.nan,
            "DELAY_PRECISION_MEAN": np.nan,
            "DELAY_RECALL_MEAN": np.nan,
            "DELAY_F1_MEAN": np.nan,
            "TOP_10_RECALL_MEAN": np.nan,
            "TOP_10_LIFT_MEAN": np.nan,
            "TRAINING_SECONDS": np.nan,
            "ERROR": str(error),
        }


def run_cv_search(
    model_name: str,
    stage: str,
    configurations: Sequence[dict[str, Any]],
    prepared_folds: Sequence[dict[str, Any]],
    minimum_recall: float | None,
    threshold_min: float,
    threshold_max: float,
    threshold_step: float,
    random_seed: int,
    threshold_strategy: str = "recall_constrained_f1",
) -> pd.DataFrame:
    """Run every supplied configuration on all chronological folds."""
    rows: list[dict[str, Any]] = []
    for index, parameters in enumerate(configurations, start=1):
        configuration_id = f"{stage}-{index:02d}"
        print(
            f"\n{model_name}: {stage} configuration {index}/"
            f"{len(configurations)}"
        )
        row = evaluate_cv_configuration(
            model_name=model_name,
            configuration_id=configuration_id,
            parameters=parameters,
            prepared_folds=prepared_folds,
            minimum_recall=minimum_recall,
            threshold_min=threshold_min,
            threshold_max=threshold_max,
            threshold_step=threshold_step,
            random_seed=random_seed,
            threshold_strategy=threshold_strategy,
        )
        row["SEARCH_STAGE"] = stage
        rows.append(row)
    return pd.DataFrame(rows)


def best_cv_row(results: pd.DataFrame) -> pd.Series:
    """Return the best stable, converged row for focused refinement."""
    valid = results[(results["STATUS"] == "OK") & results["CONVERGED"]].copy()
    if valid.empty:
        valid = results[results["STATUS"] == "OK"].copy()
    if valid.empty:
        raise RuntimeError("No successful tuning configuration is available.")
    return valid.sort_values(
        ["PR_AUC_MEAN", "PR_AUC_STD", "DELAY_F1_MEAN"],
        ascending=[False, True, False],
    ).iloc[0]


def logistic_refinements(
    winner: dict[str, Any], limit: int
) -> list[dict[str, Any]]:
    """Create nearby, unique Logistic Regression configurations."""
    candidates = []
    for factor in (0.5, 0.75, 1.25, 2.0):
        candidate = dict(winner)
        candidate["C"] = float(np.clip(float(winner["C"]) * factor, 1e-4, 100))
        candidates.append(candidate)
    for key, alternatives in {
        "penalty": ("l1", "l2"),
        "imbalance_strategy": ("natural", "weighted"),
    }.items():
        for value in alternatives:
            candidate = dict(winner)
            candidate[key] = value
            candidates.append(candidate)
    winner_key = parameters_json(winner)
    unique = [
        item
        for item in deduplicate_configurations(candidates)
        if parameters_json(item) != winner_key
    ]
    return unique[:limit]


def random_forest_refinements(
    winner: dict[str, Any], limit: int
) -> list[dict[str, Any]]:
    """Create nearby, unique Random Forest configurations."""
    candidates = []
    for value in (
        max(100, int(winner["n_estimators"]) - 100),
        int(winner["n_estimators"]) + 100,
    ):
        candidate = dict(winner)
        candidate["n_estimators"] = value
        candidates.append(candidate)
    depth = winner.get("max_depth")
    for value in ([None, 12] if depth is None else [max(4, depth - 2), depth + 2]):
        candidate = dict(winner)
        candidate["max_depth"] = value
        candidates.append(candidate)
    for key, values in {
        "min_samples_split": (2, 10, 30),
        "min_samples_leaf": (1, 5, 20),
        "max_features": ("sqrt", 0.3, 0.5, 0.7),
        "imbalance_strategy": ("natural", "weighted"),
    }.items():
        for value in values:
            candidate = dict(winner)
            candidate[key] = value
            candidates.append(candidate)
    winner_key = parameters_json(winner)
    unique = [
        item
        for item in deduplicate_configurations(candidates)
        if parameters_json(item) != winner_key
    ]
    return unique[:limit]


def xgboost_refinements(
    winner: dict[str, Any], limit: int
) -> list[dict[str, Any]]:
    """Create nearby, unique XGBoost configurations."""
    candidates = []
    for factor in (0.75, 1.25):
        candidate = dict(winner)
        candidate["learning_rate"] = float(
            np.clip(float(winner["learning_rate"]) * factor, 0.01, 0.30)
        )
        candidates.append(candidate)
    for value in (
        max(2, int(winner["max_depth"]) - 1),
        int(winner["max_depth"]) + 1,
    ):
        candidate = dict(winner)
        candidate["max_depth"] = value
        candidates.append(candidate)
    for factor in (0.8, 1.2):
        candidate = dict(winner)
        candidate["n_estimators"] = max(
            100, int(round(int(winner["n_estimators"]) * factor))
        )
        candidates.append(candidate)
    for key, values in {
        "min_child_weight": (1, 5, 10),
        "imbalance_strategy": ("natural", "weighted"),
    }.items():
        for value in values:
            candidate = dict(winner)
            candidate[key] = value
            candidates.append(candidate)
    winner_key = parameters_json(winner)
    unique = [
        item
        for item in deduplicate_configurations(candidates)
        if parameters_json(item) != winner_key
    ]
    return unique[:limit]


def shortlist_cv_candidates(
    results: pd.DataFrame,
    maximum_pr_auc_std: float,
    top_per_model: int = 2,
) -> pd.DataFrame:
    """Retain stable competitive configurations from every algorithm."""
    valid = results[(results["STATUS"] == "OK") & results["CONVERGED"]].copy()
    stable = valid[valid["PR_AUC_STD"] <= maximum_pr_auc_std]
    if not stable.empty:
        valid = stable
    return (
        valid.sort_values(
            ["MODEL", "PR_AUC_MEAN", "DELAY_F1_MEAN", "BRIER_SCORE_MEAN"],
            ascending=[True, False, False, True],
        )
        .groupby("MODEL", as_index=False, group_keys=False)
        .head(top_per_model)
        .reset_index(drop=True)
    )


def select_final_candidate(
    confirmation_results: pd.DataFrame,
    minimum_recall: float,
    pr_auc_tolerance: float,
) -> tuple[pd.Series, str]:
    """Apply the transparent final model-selection rule."""
    available = confirmation_results.copy()
    if "CONVERGED" in available and available["CONVERGED"].any():
        available = available[available["CONVERGED"]]

    eligible = available[
        available["DELAY_RECALL"] >= minimum_recall
    ].copy()
    rule_note = (
        f"delay recall >= {minimum_recall:.2f}; PR-AUC within "
        f"{pr_auc_tolerance:.2f} of the eligible leader; then highest delayed F1"
    )
    if eligible.empty:
        eligible = available.copy()
        rule_note = "recall target unavailable; selected by highest recall, then F1"
        winner = eligible.sort_values(
            ["DELAY_RECALL", "DELAY_F1", "PR_AUC", "BRIER_SCORE"],
            ascending=[False, False, False, True],
        ).iloc[0]
        return winner, rule_note

    best_pr_auc = float(eligible["PR_AUC"].max())
    competitive = eligible[
        eligible["PR_AUC"] >= best_pr_auc - pr_auc_tolerance
    ].copy()
    winner = competitive.sort_values(
        [
            "DELAY_F1",
            "BRIER_SCORE",
            "PR_AUC",
            "TOP_10_LIFT",
            "INTERPRETABILITY_RANK",
            "TRAINING_SECONDS",
        ],
        ascending=[False, True, False, False, False, True],
    ).iloc[0]
    return winner, rule_note


def select_final_candidate_by_f1(
    confirmation_results: pd.DataFrame,
    pr_auc_tolerance: float,
) -> tuple[pd.Series, str]:
    """Select a competitive calibrated candidate without a recall constraint."""
    available = confirmation_results.copy()
    if "CONVERGED" in available and available["CONVERGED"].any():
        available = available[available["CONVERGED"]]
    if available.empty:
        raise RuntimeError("No eligible final candidate is available.")

    best_pr_auc = float(available["PR_AUC"].max())
    competitive = available[
        available["PR_AUC"] >= best_pr_auc - pr_auc_tolerance
    ].copy()
    winner = competitive.sort_values(
        [
            "DELAY_F1",
            "BRIER_SCORE",
            "PR_AUC",
            "DELAY_PRECISION",
            "TOP_10_LIFT",
            "INTERPRETABILITY_RANK",
            "TRAINING_SECONDS",
        ],
        ascending=[False, True, False, False, False, False, True],
    ).iloc[0]
    rule_note = (
        f"PR-AUC within {pr_auc_tolerance:.2f} of the eligible leader; "
        "then highest validation delayed-class F1, with no minimum-recall rule"
    )
    return winner, rule_note
