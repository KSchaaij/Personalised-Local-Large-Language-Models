from scipy.stats import ttest_rel
import statsmodels.api as sm
import pandas as pd
import numpy as np
import ast


"""
Statistical testing for RS LIX scores between baseline and alignment.
The analysis uses matched transcript-level observations.
"""

def cohen_d_paired(x, y):
    """Calculate paired Cohen's dz using the standard deviation of differences."""

    differences = np.asarray(x) - np.asarray(y)

    mean_difference = np.mean(differences)
    std_difference = np.std(differences, ddof=1)

    if np.isnan(std_difference) or std_difference == 0:
        return np.nan, "Undefined - zero variance"

    cohens_d = mean_difference / std_difference
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


"""Load and prepare the data """
fileQG = "QG_output_analysis_results_RS.csv"
fileRG = "RG_output_analysis_results_RS.csv"

df_QG = pd.read_csv(fileQG)
df_QG["Source"] = "QG"

df_RG = pd.read_csv(fileRG)
df_RG["Source"] = "RG"

df = pd.concat([df_QG, df_RG], ignore_index=True)


# Short model names
short_names = {
    'gpt-4.1-2025-04-14': 'GPT-4.1',
    'mistral-large-2411': 'Mistral-large',
    'robinsmits/Qwen1.5-7B-Dutch-Chat': 'Qwen-1.5',
    'mistralai/Mistral-Small-3.2-24B-Instruct-2506': 'Mistral-small'
}

df["Model"] = df["Model"].replace(short_names)


# Select only the LIX score
df["LIX_user"] = df["[LIX, Flesch]user"].apply(lambda x: eval(x)[0] if isinstance(x, str) else x)   # Target
df["LIX_model"] = df["[LIX, Flesch]model"].apply(lambda x: eval(x)[0] if isinstance(x, str) else x)

stat_test_results = []
individual_differences = []

for source in ["QG", "RG"]:

    source_df = df[df["Source"] == source]

    for model in source_df["Model"].unique():

        model_df = source_df[source_df["Model"] == model]

        # Aggregate model LIX scores per transcript and condition
        baseline_agg = (
            model_df[model_df["Condition"] == "baseline"]
            .groupby(
                ["Transcript_nr", "Model", "LIX_user"],
                dropna=False
            )["LIX_model"]
            .mean()
            .reset_index()
        )

        alignment_agg = (
            model_df[model_df["Condition"] == "alignment"]
            .groupby(
                ["Transcript_nr", "Model", "LIX_user"],
                dropna=False
            )["LIX_model"]
            .mean()
            .reset_index()
        )

        # Match baseline and alignment observations
        merged = pd.merge(
            baseline_agg,
            alignment_agg,
            on=["Transcript_nr", "Model", "LIX_user"],
            suffixes=("_baseline", "_alignment")
        )

        baseline_values = merged["LIX_model_baseline"].reset_index(drop=True)
        alignment_values = merged["LIX_model_alignment"].reset_index(drop=True)

        # Target mean across matched transcripts
        mean_target = merged["LIX_user"].mean()

        n = len(merged)

        if n > 2:
            # Difference: alignment - baseline
            # Positive values indicate a higher LIX score under alignment
            differences = alignment_values - baseline_values
            mean_diff = differences.mean() if n > 0 else np.nan
            n = len(differences)

            """ Normality testing using Central Limit Theorem """
            if n > 30:
                is_normal = True
                p_norm = np.nan
            else:
                print("Oh no! This still needs to be implemented")

            # Paired statistical testing
            if is_normal:
                t_stat, p_value = ttest_rel(alignment_values,baseline_values)
                cohens_d, effect_size = cohen_d_paired(alignment_values,baseline_values)

        """Individual results"""
        for _, row in merged.iterrows():
            individual_differences.append({
                "Source": source,
                "Model": model,
                "Transcript_nr": row["Transcript_nr"],
                "Baseline": row["LIX_model_baseline"],
                "Alignment": row["LIX_model_alignment"],
                "Target mean": row["LIX_user"],
                "Difference": (
                    row["LIX_model_alignment"]
                    - row["LIX_model_baseline"]
                )
            })

        """Summary results """
        stat_test_results.append({
            "Source": source,
            "Model": model,
            "Target mean": mean_target,
            "Baseline mean±std": (
                f"{baseline_values.mean():.2f} ± {baseline_values.std(ddof=1):.2f}"),
            "Alignment mean±std": (f"{alignment_values.mean():.2f} ± {alignment_values.std(ddof=1):.2f}"),
            "Mean difference LIX": mean_diff,
            "n": n,
            "Stat": t_stat,
            "p-value": p_value,
            "Cohen's D": cohens_d,
            "Effect size": effect_size
        })

""" Properly store the results """
stat_df = pd.DataFrame(stat_test_results)
individual_df = pd.DataFrame(individual_differences)

""" Use Hold correction """
stat_df['Significant (Holm)'], stat_df["p-value (Holm)"], _, _ = sm.stats.multipletests(stat_df['p-value'],0.05,'holm')

""" Store the results properly"""
stat_df.to_csv("stattest_LIX.csv", index=False)
individual_df.to_csv("stattest_LIX_ind.csv", index=False)
