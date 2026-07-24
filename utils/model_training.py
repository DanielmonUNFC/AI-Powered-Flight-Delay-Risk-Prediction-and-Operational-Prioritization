"""Shared model-training helpers for Databricks notebooks."""

from __future__ import annotations

from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator,
)
from pyspark.sql import DataFrame


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
