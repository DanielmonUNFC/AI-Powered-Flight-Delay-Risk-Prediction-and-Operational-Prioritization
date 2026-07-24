"""Shared model-training helpers for Databricks notebooks."""

from __future__ import annotations

from config import project_config as cfg
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator,
)
from pyspark.ml.feature import FeatureHasher
from pyspark.sql import DataFrame


def build_feature_manifest(
    *,
    selected_model_name: str,
    selected_model_parameters: dict[str, float],
) -> dict[str, object]:
    """Return the canonical feature manifest persisted by notebook 07."""
    return {
        "target_column": cfg.TARGET_COLUMN,
        "categorical_columns": list(cfg.MODEL_CATEGORICAL_COLUMNS),
        "numerical_columns": list(cfg.MODEL_NUMERICAL_COLUMNS),
        "model_input_columns": list(cfg.MODEL_INPUT_COLUMNS),
        "hash_vector_size": cfg.HASH_VECTOR_SIZE,
        "selected_model_name": selected_model_name,
        "selected_model_parameters": selected_model_parameters,
        "train_end_date": cfg.TRAIN_END_DATE,
        "validation_start_date": cfg.VALIDATION_START_DATE,
        "validation_end_date": cfg.VALIDATION_END_DATE,
        "test_start_date": cfg.TEST_START_DATE,
    }


def create_feature_hasher() -> FeatureHasher:
    """Create the canonical FeatureHasher used across modeling notebooks."""
    return FeatureHasher(
        inputCols=list(cfg.MODEL_INPUT_COLUMNS),
        outputCol="features",
        categoricalCols=list(cfg.MODEL_CATEGORICAL_COLUMNS),
        numFeatures=cfg.HASH_VECTOR_SIZE,
    )


def validate_hist_modeling_frame(
    hist_dataframe: DataFrame,
    dataframe_name: str,
) -> None:
    """Ensure a hist modeling table contains the expected schema."""
    missing_columns = sorted(
        cfg.MODELING_REQUIRED_HIST_COLUMNS - set(hist_dataframe.columns)
    )
    if missing_columns:
        raise ValueError(
            f"{dataframe_name} is missing required modeling columns: "
            f"{missing_columns}"
        )


def prepare_hist_modeling_frame(hist_dataframe: DataFrame) -> DataFrame:
    """Drop intermediate prior-count columns and persist a stable hist schema."""
    intermediate_columns = [
        column_name
        for column_name in cfg.MODEL_INTERMEDIATE_HIST_COLUMNS
        if column_name in hist_dataframe.columns
    ]
    if intermediate_columns:
        hist_dataframe = hist_dataframe.drop(*intermediate_columns)

    return hist_dataframe.select(*cfg.MODEL_HIST_TABLE_COLUMNS)


def hash_modeling_frame(
    hist_dataframe: DataFrame,
    feature_hasher: FeatureHasher,
) -> DataFrame:
    """Hash a hist modeling frame and keep only join keys, target, and features."""
    return (
        feature_hasher.transform(hist_dataframe)
        .select(*cfg.MODEL_HASHED_OUTPUT_COLUMNS)
    )


def evaluate_tuning_predictions(
    predictions: DataFrame,
    target_column: str,
) -> dict[str, float]:
    """Calculate overall and delayed-flight validation metrics."""
    accuracy = MulticlassClassificationEvaluator(
        labelCol=target_column,
        predictionCol="prediction",
        metricName="accuracy",
    ).evaluate(predictions)

    precision = MulticlassClassificationEvaluator(
        labelCol=target_column,
        predictionCol="prediction",
        metricName="weightedPrecision",
    ).evaluate(predictions)

    recall = MulticlassClassificationEvaluator(
        labelCol=target_column,
        predictionCol="prediction",
        metricName="weightedRecall",
    ).evaluate(predictions)

    f1_score = MulticlassClassificationEvaluator(
        labelCol=target_column,
        predictionCol="prediction",
        metricName="f1",
    ).evaluate(predictions)

    delay_precision = MulticlassClassificationEvaluator(
        labelCol=target_column,
        predictionCol="prediction",
        metricName="precisionByLabel",
        metricLabel=1.0,
    ).evaluate(predictions)

    delay_recall = MulticlassClassificationEvaluator(
        labelCol=target_column,
        predictionCol="prediction",
        metricName="recallByLabel",
        metricLabel=1.0,
    ).evaluate(predictions)

    delay_f1 = (
        2.0 * delay_precision * delay_recall
        / (delay_precision + delay_recall)
        if delay_precision + delay_recall > 0
        else 0.0
    )

    roc_auc = BinaryClassificationEvaluator(
        labelCol=target_column,
        rawPredictionCol="rawPrediction",
        metricName="areaUnderROC",
    ).evaluate(predictions)

    pr_auc = BinaryClassificationEvaluator(
        labelCol=target_column,
        rawPredictionCol="rawPrediction",
        metricName="areaUnderPR",
    ).evaluate(predictions)

    return {
        "ACCURACY": float(accuracy),
        "PRECISION": float(precision),
        "RECALL": float(recall),
        "F1_SCORE": float(f1_score),
        "ROC_AUC": float(roc_auc),
        "PR_AUC": float(pr_auc),
        "DELAY_PRECISION": float(delay_precision),
        "DELAY_RECALL": float(delay_recall),
        "DELAY_F1": float(delay_f1),
    }
