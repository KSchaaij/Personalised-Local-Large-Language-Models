from scipy.stats import ttest_rel
import statsmodels.api as sm
import pandas as pd
import numpy as np
import ast

"""
Statistical testing for RS Flesch scores between baseline and alignment.
Positive differences (Alignment - Baseline) indicate higher Flesch scores,
which generally correspond to easier-to-read texts.
"""


def extract_flesch(value):
    """Safely extract the Flesch score (index 1) from a stored list."""
    if pd.isna(value):
        return np.nan

    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return np.nan

    try:
        return float(value[1])
    except (TypeError, IndexError, KeyError, ValueError):
        return np.nan


def cohen_d_paired(x, y):
    """Calculate Cohen's dz for paired observations."""
    differences = np.asarray(x) - np.asarray(y)

    std_difference = np.std(differences, ddof=1)

    if std_difference == 0:
        return np.nan, "Undefined - zero variance"

    cohens_d = np.mean(differences) / std_difference
    abs_d = abs(cohens_d)

    if abs_d <= 0.20:
        effect = "negligible"
    elif abs_d <= 0.50:
        effect = "small-medium"
    elif abs_d <= 0.80:
        effect = "medium-large"
    else:
        effect = "large"

    return cohens_d, effect


""" Load and prepare data """

fileQG = "QG_output_analysis_results_RS.csv"
fileRG = "RG_output_analysis_results_RS.csv"

df_QG = pd.read_csv(fileQG)
df_QG["Source"] = "QG"

df_RG = pd.read_csv(fileRG)
df_RG["Source"] = "RG"

df = pd.concat([df_QG, df_RG], ignore_index=True)

short_names = {
    'gpt-4.1-2025-04-14': 'GPT-4.1',
    'mistral-large-2411': 'Mistral-large',
    'robinsmits/Qwen1.5-7B-Dutch-Chat': 'Qwen-1.5',
    'mistralai/Mistral-Small-3.2-24B-Instruct-2506': 'Mistral-small'
}

df["Model"] = df["Model"].replace(short_names)

# Extract Flesch scores
df["Flesch_user"] = df["[LIX, Flesch]user"].apply(extract_flesch)
df["Flesch_model"] = df["[LIX, Flesch]model"].apply(extract_flesch)

stat_test_results = []
individual_differences = []

"""Loop over different tasks """
for source in ["QG", "RG"]:

    source_df = df[df["Source"] == source]

    for model in source_df["Model"].dropna().unique():

        model_df = source_df[source_df["Model"] == model].copy()

        # Aggregate mean Flesch score per transcript and condition
        baseline_agg = (
            model_df[model_df["Condition"] == "baseline"]
            .groupby(
                ["Transcript_nr", "Model", "Flesch_user"],
                dropna=False
            )["Flesch_model"]
            .mean()
            .reset_index()
        )

        alignment_agg = (
            model_df[model_df["Condition"] == "alignment"]
            .groupby(
                ["Transcript_nr", "Model", "Flesch_user"],
                dropna=False
            )["Flesch_model"]
            .mean()
            .reset_index()
        )

        # Match baseline and alignment observations
        merged = pd.merge(
            baseline_agg,
            alignment_agg,
            on=["Transcript_nr", "Model", "Flesch_user"],
            suffixes=("_baseline", "_alignment")
        )

        baseline_values = merged["Flesch_model_baseline"].reset_index(drop=True)
        alignment_values = merged["Flesch_model_alignment"].reset_index(drop=True)

        # Target mean based on the matched transcripts
        mean_target = merged["Flesch_user"].mean()

        n = len(merged)

        # Paired t-test requires at least 2 pairs;
        if n > 2:
            # Paired differences: alignment - baseline
            differences = alignment_values - baseline_values
            mean_diff = differences.mean() if n > 0 else np.nan
            n = len(differences)

            """ Normality testing using Central Limit Theorem """
            if n > 30:
                is_normal = True
                p_norm = np.nan
            else:
                print("Oh no! This still needs to be implemented")

            if is_normal:
                t_stat, p_value = ttest_rel(
                    alignment_values,
                    baseline_values
                )
                cohens_d, effect = cohen_d_paired(
                    alignment_values,
                    baseline_values
                )
        """Store individual results"""
        for _, row in merged.iterrows():

            individual_differences.append({
                "Source": source,
                "Model": model,
                "Transcript_nr": row["Transcript_nr"],
                "Baseline": row["Flesch_model_baseline"],
                "Alignment": row["Flesch_model_alignment"],
                "Target mean": row["Flesch_user"],
                "Difference": (
                    row["Flesch_model_alignment"]
                    - row["Flesch_model_baseline"]
                )
            })

        """Store summary results"""
        stat_test_results.append({
            "Source": source,
            "Model": model,
            "Target mean": mean_target,
            "Baseline mean±std": (
                f"{baseline_values.mean():.2f} ± {baseline_values.std(ddof=1):.2f}"),
            "Alignment mean±std": (
                f"{alignment_values.mean():.2f} ± {alignment_values.std(ddof=1):.2f}"),
            "Mean difference Flesch": mean_diff,
            "n": n,
            "Stat": t_stat,
            "p-value": p_value,
            "Cohen's D": cohens_d,
            "Effect size": effect
        })


"""Properly store the results"""
stat_df = pd.DataFrame(stat_test_results)
individual_df = pd.DataFrame(individual_differences)


""" Use Hold correction """
stat_df['Significant (Holm)'], stat_df["p-value (Holm)"], _, _ = sm.stats.multipletests(stat_df['p-value'],0.05,'holm')

stat_df.to_csv("stattest_Flesch.csv", index=False)
individual_df.to_csv("stattest_Flesch_ind.csv", index=False)
