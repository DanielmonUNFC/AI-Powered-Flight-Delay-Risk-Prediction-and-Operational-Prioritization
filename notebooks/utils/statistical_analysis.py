"""Statistical hypothesis-testing helpers for the capstone notebooks."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from scipy import stats


def chi_square_independence(
    contingency_table: pd.DataFrame,
    min_expected_frequency: float = 5.0,
) -> dict[str, float | bool | str]:
    """Run a chi-square test of independence and compute Cramér's V."""
    observed = contingency_table.to_numpy(dtype=float)
    chi2_statistic, p_value, degrees_of_freedom, expected = stats.chi2_contingency(
        observed
    )

    minimum_expected = float(np.min(expected))
    assumptions_met = minimum_expected >= min_expected_frequency

    row_count, column_count = observed.shape
    sample_size = observed.sum()
    cramers_v = np.sqrt(
        chi2_statistic
        / (sample_size * (min(row_count, column_count) - 1))
    ) if sample_size > 0 and min(row_count, column_count) > 1 else 0.0

    return {
        "test_name": "Chi-Square Test of Independence",
        "statistic": float(chi2_statistic),
        "p_value": float(p_value),
        "degrees_of_freedom": float(degrees_of_freedom),
        "effect_size": float(cramers_v),
        "effect_size_label": "Cramer's V",
        "minimum_expected_frequency": minimum_expected,
        "assumptions_met": assumptions_met,
    }


def pearson_correlation(
    x_values: pd.Series,
    y_values: pd.Series,
) -> dict[str, float | str]:
    """Calculate Pearson correlation and its p-value."""
    clean_frame = pd.DataFrame({"x": x_values, "y": y_values}).dropna()
    if len(clean_frame) < 3:
        raise ValueError("At least three complete observations are required.")

    correlation, p_value = stats.pearsonr(
        clean_frame["x"].astype(float),
        clean_frame["y"].astype(float),
    )

    return {
        "test_name": "Pearson Correlation",
        "statistic": float(correlation),
        "p_value": float(p_value),
        "degrees_of_freedom": float(len(clean_frame) - 2),
        "effect_size": float(abs(correlation)),
        "effect_size_label": "|Pearson r|",
        "minimum_expected_frequency": np.nan,
        "assumptions_met": True,
    }


def independent_t_test(
    group_zero: pd.Series,
    group_one: pd.Series,
) -> dict[str, float | bool | str]:
    """Compare two independent groups using Welch's t-test."""
    clean_zero = group_zero.dropna().astype(float)
    clean_one = group_one.dropna().astype(float)

    if len(clean_zero) < 2 or len(clean_one) < 2:
        raise ValueError("Each group requires at least two observations.")

    t_statistic, p_value = stats.ttest_ind(
        clean_zero,
        clean_one,
        equal_var=False,
    )

    pooled_std = np.sqrt(
        (
            ((len(clean_zero) - 1) * clean_zero.std(ddof=1) ** 2)
            + ((len(clean_one) - 1) * clean_one.std(ddof=1) ** 2)
        )
        / (len(clean_zero) + len(clean_one) - 2)
    )
    cohens_d = (
        (clean_one.mean() - clean_zero.mean()) / pooled_std
        if pooled_std > 0
        else 0.0
    )

    _, levene_p_value = stats.levene(clean_zero, clean_one)

    return {
        "test_name": "Welch's Independent t-Test",
        "statistic": float(t_statistic),
        "p_value": float(p_value),
        "degrees_of_freedom": np.nan,
        "effect_size": float(abs(cohens_d)),
        "effect_size_label": "|Cohen's d|",
        "minimum_expected_frequency": np.nan,
        "assumptions_met": bool(levene_p_value >= 0.05),
    }


def one_way_anova(
    groups: Iterable[pd.Series],
) -> dict[str, float | bool | str]:
    """Run a one-way ANOVA across multiple independent groups."""
    clean_groups = [group.dropna().astype(float) for group in groups]
    clean_groups = [group for group in clean_groups if len(group) >= 2]

    if len(clean_groups) < 2:
        raise ValueError("At least two groups with two observations are required.")

    f_statistic, p_value = stats.f_oneway(*clean_groups)

    all_values = np.concatenate([group.to_numpy() for group in clean_groups])
    grand_mean = all_values.mean()
    ss_between = sum(
        len(group) * (group.mean() - grand_mean) ** 2 for group in clean_groups
    )
    ss_total = sum((value - grand_mean) ** 2 for value in all_values)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0.0

    levene_groups = [group.to_numpy() for group in clean_groups]
    _, levene_p_value = stats.levene(*levene_groups)

    return {
        "test_name": "One-Way ANOVA",
        "statistic": float(f_statistic),
        "p_value": float(p_value),
        "degrees_of_freedom": float(len(clean_groups) - 1),
        "effect_size": float(eta_squared),
        "effect_size_label": "Eta-squared",
        "minimum_expected_frequency": np.nan,
        "assumptions_met": bool(levene_p_value >= 0.05),
    }


def kruskal_wallis_test(
    groups: Iterable[pd.Series],
) -> dict[str, float | bool | str]:
    """Compare continuous distributions and compute epsilon-squared."""
    clean_groups = [
        group.dropna().astype(float)
        for group in groups
        if len(group.dropna()) >= 2
    ]

    if len(clean_groups) < 2:
        raise ValueError(
            "At least two groups with two observations are required."
        )

    h_statistic, p_value = stats.kruskal(*clean_groups)
    group_count = len(clean_groups)
    sample_size = sum(len(group) for group in clean_groups)
    epsilon_squared = (
        max(0.0, (h_statistic - group_count + 1) / (sample_size - group_count))
        if sample_size > group_count
        else 0.0
    )

    return {
        "test_name": "Kruskal-Wallis H-Test",
        "statistic": float(h_statistic),
        "p_value": float(p_value),
        "degrees_of_freedom": float(group_count - 1),
        "effect_size": float(epsilon_squared),
        "effect_size_label": "Epsilon-squared",
        "minimum_expected_frequency": np.nan,
        "assumptions_met": True,
    }


def spearman_correlation(
    x_values: pd.Series,
    y_values: pd.Series,
) -> dict[str, float | str]:
    """Calculate Spearman rank correlation and its p-value."""
    clean_frame = pd.DataFrame({"x": x_values, "y": y_values}).dropna()
    if len(clean_frame) < 3:
        raise ValueError("At least three complete observations are required.")

    correlation, p_value = stats.spearmanr(
        clean_frame["x"].astype(float),
        clean_frame["y"].astype(float),
    )

    return {
        "test_name": "Spearman Rank Correlation",
        "statistic": float(correlation),
        "p_value": float(p_value),
        "degrees_of_freedom": float(len(clean_frame) - 2),
        "effect_size": float(abs(correlation)),
        "effect_size_label": "|Spearman rho|",
        "minimum_expected_frequency": np.nan,
        "assumptions_met": True,
    }


def interpret_cramers_v(value: float) -> str:
    """Return a practical interpretation label for Cramér's V."""
    if value < 0.10:
        return "Negligible"
    if value < 0.30:
        return "Small"
    if value < 0.50:
        return "Moderate"
    return "Strong"


def interpret_effect_size(effect_size_label: str, value: float) -> str:
    """Return a practical-significance label appropriate to the effect-size metric.

    Reporting statistical significance alone can be misleading on very large
    samples, where even negligible effects become "significant". Each metric
    uses its own conventional (Cohen, 1988) small/medium/large thresholds.
    """
    magnitude = abs(value)

    if effect_size_label == "Cramer's V":
        return interpret_cramers_v(magnitude)

    if effect_size_label in ("|Pearson r|", "|Spearman rho|"):
        if magnitude < 0.10:
            return "Negligible"
        if magnitude < 0.30:
            return "Small"
        if magnitude < 0.50:
            return "Moderate"
        return "Strong"

    if effect_size_label == "|Cohen's d|":
        if magnitude < 0.20:
            return "Negligible"
        if magnitude < 0.50:
            return "Small"
        if magnitude < 0.80:
            return "Moderate"
        return "Strong"

    if effect_size_label in ("Eta-squared", "Epsilon-squared"):
        if magnitude < 0.01:
            return "Negligible"
        if magnitude < 0.06:
            return "Small"
        if magnitude < 0.14:
            return "Moderate"
        return "Strong"

    return "Not standardized"


def classify_hypothesis_result(
    p_value: float,
    alpha: float,
) -> str:
    """Return reject-or-fail-to-reject language for reporting."""
    if p_value < alpha:
        return "Reject H0"
    return "Fail to reject H0"


def build_test_result_row(
    *,
    research_question: str,
    hypothesis_id: str,
    null_hypothesis: str,
    alternative_hypothesis: str,
    factor: str,
    test_output: dict[str, float | bool | str],
    alpha: float,
) -> dict[str, object]:
    """Convert a test output dictionary into a report row."""
    p_value = float(test_output["p_value"])
    effect_size = float(test_output["effect_size"])
    effect_size_label = test_output["effect_size_label"]
    return {
        "research_question": research_question,
        "hypothesis_id": hypothesis_id,
        "null_hypothesis": null_hypothesis,
        "alternative_hypothesis": alternative_hypothesis,
        "factor": factor,
        "test_name": test_output["test_name"],
        "statistic": round(float(test_output["statistic"]), 6),
        "p_value": round(p_value, 6),
        "effect_size": round(effect_size, 6),
        "effect_size_label": effect_size_label,
        "effect_size_interpretation": interpret_effect_size(
            effect_size_label, effect_size
        ),
        "alpha": alpha,
        "decision": classify_hypothesis_result(p_value, alpha),
        "assumptions_met": bool(test_output["assumptions_met"]),
    }
