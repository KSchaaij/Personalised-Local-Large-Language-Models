import pandas as pd


""" In this script the difference for Recall and Coverage (separately) between conditions is calculated following prior work as discussed in the paper
This is purely exploratory, no statistical testing is involved - Individual simulation results 
"""


stat_test_results = []
individual_differences = []   

""" Here we load the analysis results """
fileQG = "dev_QG_output_analysis_results_p.csv"
fileRG = "dev_RG_output_analysis_results_p.csv"
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
                        "Mean baseline": baseline_values.mean(),
                        "Mean alignment": alignment_values.mean(),
                        "Mean difference": mean_diff
                    })

""" Store the results """
stat_df = pd.DataFrame(stat_test_results)
individual_df = pd.DataFrame(individual_differences)
name = ""
if fileQG == "QG_output_analysis_results_d.csv":
    name = "Dialogue"   # This never happens
else:
    name = "Profile"
stat_df.to_csv(name + '_evaluation.csv', index=False)
individual_df.to_csv(name + '_evaluation_ind.csv', index=False)
