import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import ttest_rel

"""
This script was used for statistical testing for SL overlength between conditions
"""

""" Cohen's d effect size calculation """
def cohen_d_paired(x, y):
    mean_difference = np.mean(x-y)
    std_difference = np.std(x-y, ddof = 1)

    if std_difference == 0:
        cohens_d = np.nan
        effect = "There is a problem!"
    else:
        cohens_d = mean_difference/std_difference
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


normality_results = []
stat_test_results = []
individual_differences = []   


""" Here we load the analysis results """
fileQG = "QG_output_analysis_results_SL.csv"
fileRG = "RG_output_analysis_results_SL.csv"
df_QG = pd.read_csv(fileQG)
df_QG["Source"] = "QG"
df_RG = pd.read_csv(fileRG)
df_RG["Source"] = "RG"

df = pd.concat([df_QG, df_RG], ignore_index=True)

# Short names mapping
short_names = {
    'gpt-4.1-2025-04-14': 'GPT-4.1',
    'mistral-large-2411': 'Mistral-large',           
    'mistralai/Mistral-Small-3.2-24B-Instruct-2506': 'Mistral-small'
}
df['Model'] = df['Model'].replace(short_names)


""" We loop over the two different tasks specified: RG and QG"""
for source in ['QG', 'RG']:
    source_df = df[df['Source'] == source]
    """ We loop over the different models that were used"""
    for model in source_df['Model'].unique():
        model_df = source_df[source_df['Model'] == model]

        """ Aggregate over Transcript_nr the mean Value per Condition (baseline/alignment) """
        baseline_agg = (
            model_df[model_df['Condition'] == 'baseline']
            .groupby(['Transcript_nr', 'Model', 'SL_user'], dropna=False)['SL_model']
            .mean()
            .reset_index()
        )
        alignment_agg = (
            model_df[model_df['Condition'] == 'alignment']
            .groupby(['Transcript_nr', 'Model', 'SL_user'], dropna=False)['SL_model']
            .mean()
            .reset_index()
        )

        """ Merge on keys to get matched pairs correctly """
        merged = pd.merge(
            baseline_agg,
            alignment_agg,
            on=['Transcript_nr', 'Model', 'SL_user'],
            suffixes=('_baseline', '_alignment')
        )

        baseline_values = merged['SL_model_baseline'].reset_index(drop=True)
        alignment_values = merged['SL_model_alignment'].reset_index(drop=True)

        target_values = merged['SL_user'].reset_index(drop = True)

        n = len(merged)
        if n > 2:
            # values 8 - target 6 = 2 means that the value was higher than the target
            baseline_over = np.maximum(0, baseline_values - target_values)
            alignment_over = np.maximum(0, alignment_values - target_values)

            # Negative mean_diff means that alignment has a smaller value for sentences exceeding the target (closer to the target)
            diff = alignment_over - baseline_over
            mean_diff = diff.mean() 

            """ Normality testing using Central Limit Theorem """
            if n > 30:
                is_normal = True
                p_norm = np.nan
            else:
                print("Oh no! This still needs to be implemented")

            """ Make use of the correct statistical test """
            if is_normal:
                """ Statistical test on absolute deviation to see whether the alignment condition 
                produces outputs closer in length to the user on average """
                t_stat, p_val = ttest_rel(alignment_over, baseline_over)
                Cohen_d, size = cohen_d_paired(alignment_over, baseline_over)

            
            # Individual overlength
            for i, row in merged.iterrows():
                baseline_over_i = max(0, row['SL_model_baseline'] - row['SL_user'])
                alignment_over_i = max(0, row['SL_model_alignment'] - row['SL_user'])

                individual_differences.append({
                    'Source': source,
                    'Model': model,
                    'Transcript_nr': row['Transcript_nr'],
                    'SL_user': row['SL_user'],
                    'Baseline_over': baseline_over_i,
                    'Alignment_over': alignment_over_i,
                    'Difference_over': alignment_over_i - baseline_over_i
                })
           
        stat_test_results.append({
            "Source": source,
            "Model": model,
            "Target": target_values.mean(),
            "Baseline over mean±std": f"{baseline_over.mean():.2f} ± {baseline_over.std(ddof=1):.2f}",
            "Alignment over mean±std": f"{alignment_over.mean():.2f} ± {alignment_over.std(ddof=1):.2f}",
            "Mean over difference": mean_diff,
            "n": n,
            "Stat": t_stat,
            "p-value": p_val,
            "Cohen's D": Cohen_d,
            "Effect size": size

        })

""" Store the results properly """
stat_df = pd.DataFrame(stat_test_results)
individual_df = pd.DataFrame(individual_differences)

""" Use the Holm correction for multiple comparisons """
stat_df['Significant (Holm)'], stat_df["p-value (Holm)"], _, _ = sm.stats.multipletests(stat_df['p-value'],0.05,'holm')

""" Store the results """
name = "SL"
stat_df.to_csv(name + '_stattest_overlength.csv', index=False)
individual_df.to_csv(name + '_stattest_overlength_ind.csv', index=False)


