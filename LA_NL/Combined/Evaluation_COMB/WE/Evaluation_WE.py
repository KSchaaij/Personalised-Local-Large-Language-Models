import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import ttest_rel

""" In this script we run the statistical analysis per model, task, metric, and POS between conditions
on the results in the combined simulation """

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
fileQG = "QG_output_analysis_results_p.csv"
fileRG = "RG_output_analysis_results_p.csv"
df_QG = pd.read_csv(fileQG)
df_QG = df_QG[df_QG['Matchtype'] == 'Exact'].copy()
df_QG["Source"] = "QG"
df_RG = pd.read_csv(fileRG)
df_RG = df_RG[df_RG['Matchtype'] == 'Exact'].copy()
df_RG["Source"] = "RG"

df = pd.concat([df_QG, df_RG], ignore_index=True)

""" We loop over the two different tasks specified: Reflection and Question Generation """
for source in ['QG', 'RG']:
    source_df = df[df['Source'] == source]
    """ We loop over the different models for which we have ran the simulation"""
    for model in source_df['Model'].unique():
        model_df = source_df[source_df['Model'] == model]
        """ We loop over the different metrics calculated"""
        for metric in model_df['Metric'].unique():
            """ We loop over the different POS categories """
            for pos in model_df['POS'].unique():
                subset = model_df[(model_df['Metric'] == metric) & (model_df['POS'] == pos)]
                print(model)
                print(source)
                print(len(subset)/2)
                """ Aggregate over Transcript_nr the mean Value per Condition (baseline/alignment) """
                baseline_agg = (
                    subset[subset['Condition'] == 'baseline']
                    .groupby(['Transcript_nr', 'Model', 'Metric', 'POS', 'Matchtype'], dropna=False)['Value']
                    .mean()
                    .reset_index()
                )
                alignment_agg = (
                    subset[subset['Condition'] == 'alignment']
                    .groupby(['Transcript_nr', 'Model', 'Metric', 'POS', 'Matchtype'], dropna=False)['Value']
                    .mean()
                    .reset_index()
                )

                """ Merge on keys to get matched pairs correctly """
                merged = pd.merge(
                    baseline_agg,
                    alignment_agg,
                    on=['Transcript_nr', 'Model', 'Metric', 'POS', 'Matchtype'],
                    suffixes=('_baseline', '_alignment')
                )

                baseline_values = merged['Value_baseline'].reset_index(drop=True)
                alignment_values = merged['Value_alignment'].reset_index(drop=True)
                n = len(merged)
                if n > 2:
                    """ The difference, a positive difference means that the alignment has a higher value
                     A negative value means that alignment has a lower value """
                    diff = alignment_values - baseline_values
                    mean_diff = diff.mean()
                    n = len(diff)

                    """ Normality testing using Central Limit Theorem """
                    if n > 30:
                        is_normal = True
                        p_norm = np.nan
                    else:
                        print("Oh no! This still needs to be implemented..")

                    """ Make use of the correct statistical test """
                    if is_normal:
                        """ This tests for a significant mean difference between baseline and alignment values. 
                        In case of a positive sign, alignment has higher values
                        In case of a negative sign, alignment has a lower value """
                        t_stat, p_val = ttest_rel(alignment_values, baseline_values)  
                        Cohen_d, size = cohen_d_paired(alignment_values, baseline_values)


                    # Store individual differences
                    for i, row in merged.iterrows():
                        individual_differences.append({
                            'Source': source,
                            'Model': model,
                            'Metric': metric,
                            'POS': pos,
                            'Transcript_nr': row['Transcript_nr'],
                            'Baseline': row['Value_baseline'],
                            'Alignment': row['Value_alignment'],
                            'Difference': row['Value_alignment'] - row['Value_baseline']
                        })

                    stat_test_results.append({
                        'Source': source,
                        'Model': model,
                        'Metric': metric,
                        'POS': pos,
                        'Stat': t_stat,
                        'p-value': p_val,
                        "Cohen's D": Cohen_d,
                        "Effect size": size,
                        "Mean baseline": baseline_values.mean(),
                        "Mean alignment": alignment_values.mean(),
                        "Mean difference": mean_diff
                    })

""" Store the results """
stat_df = pd.DataFrame(stat_test_results)
individual_df = pd.DataFrame(individual_differences)

""" Use the Benjamini Hochberg correction for multiple comparisons """
stat_df['Significant (BH)'], stat_df["p-value (BH)"], _, _ = sm.stats.multipletests(stat_df['p-value'],0.05,'fdr_bh')

name = ""
if fileQG == "QG_output_analysis_results_d.csv":
    name = "Dialogue"   # This never happens
else:
    name = "Profile"
individual_df.to_csv(name + '_stattest_ind.csv', index=False)
stat_df.to_csv(name + '_stattest.csv', index=False)

