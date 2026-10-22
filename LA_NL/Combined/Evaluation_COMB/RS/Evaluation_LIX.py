import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import ttest_rel

"""
This script was used for statistical testing for RS Flesch score between conditions
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

""" Here we load the analysis reasults """
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
df['Model'] = df['Model'].replace(short_names)


# Select only the LIX score
df["LIX_user"] = df["[LIX, Flesch]user"].apply(lambda x: eval(x)[0] if isinstance(x, str) else x)   # Target
df["LIX_model"] = df["[LIX, Flesch]model"].apply(lambda x: eval(x)[0] if isinstance(x, str) else x)

""" We loop over the two different tasks specified: Reflection and Question Generation """
for source in ['QG', 'RG']:
    source_df = df[df['Source'] == source]
    # print(source)
    """ We loop over the different models for which we have ran the simulation"""
    for model in source_df['Model'].unique():
        model_df = source_df[source_df['Model'] == model]
        print(model)
        print(source)
        print(len(model_df)/2)

        """ Aggregate over Transcript_nr the mean Value per Condition (baseline/alignment) """
        baseline_agg = (
            model_df[model_df['Condition'] == 'baseline']
            .groupby(['Transcript_nr', 'Model', 'LIX_user'], dropna=False)['LIX_model']
            .mean()
            .reset_index()
        )
        alignment_agg = (
            model_df[model_df['Condition'] == 'alignment']
            .groupby(['Transcript_nr', 'Model', 'LIX_user'], dropna=False)['LIX_model']
            .mean()
            .reset_index()
        )

        """ Merge on keys to get matched pairs correctly """
        merged = pd.merge(
            baseline_agg,
            alignment_agg,
            on=['Transcript_nr', 'Model', 'LIX_user'],
            suffixes=('_baseline', '_alignment')
        )

        mean_target = model_df['LIX_user'].mean()

        baseline_values = merged['LIX_model_baseline'].reset_index(drop=True)
        alignment_values = merged['LIX_model_alignment'].reset_index(drop=True)

        n = len(merged)
        if n > 2:
            # Positive mean_diff means that alignment was more difficult than the baseline
            diff = alignment_values - baseline_values
            mean_diff = diff.mean() 
            n = len(diff)


            """ Normality testing using Central Limit Theorem """
            if n > 30:
                is_normal = True
                p_norm = np.nan
            else:
                print("Oh no! This still needs to be implemented")

            """ Make use of the correct statistical test """
            if is_normal:
                t_stat_abs, p_val_abs = ttest_rel(alignment_values, baseline_values)
                Cohen_d, size = cohen_d_paired(alignment_values, baseline_values)

        # Store individual differences
        for i, row in merged.iterrows():
            individual_differences.append({
                'Source': source,
                'Model': model,
                'Transcript_nr': row['Transcript_nr'],
                'Baseline': row['LIX_model_baseline'],
                'Alignment': row['LIX_model_alignment'],
                "Target mean": mean_target,
                'Difference': row['LIX_model_alignment'] - row['LIX_model_baseline']
            })


        stat_test_results.append({
            "Source": source,
            "Model": model,
            "Target mean": mean_target,
            "Baseline mean±std": f"{baseline_values.mean():.2f} ± {baseline_values.std(ddof=1):.2f}",
            "Alignment mean±std": f"{alignment_values.mean():.2f} ± {alignment_values.std(ddof=1):.2f}",
            "Mean difference LIX": mean_diff,
            "n": n,
            "Stat": t_stat_abs,
            "p-value": p_val_abs,
            "Cohen's D": Cohen_d,
            "Effect size": size
        })

""" Store the results properly """
stat_df = pd.DataFrame(stat_test_results)
individual_df = pd.DataFrame(individual_differences)

""" Use the Holm correction for multiple comparisons """
stat_df['Significant (Holm)'], stat_df["p-value (Holm)"], _, _ = sm.stats.multipletests(stat_df['p-value'],0.05,'holm')
