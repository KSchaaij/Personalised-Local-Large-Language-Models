import numpy as np
import pandas as pd

""" In this script the difference in SL overlength between conditions is calculated 
Exploratory - Individual simulation results """
stat_test_results = []
individual_differences = []   


""" Here we load the analysis results """
fileQG = "QG_output_analysis_results.csv"
fileRG = "RG_output_analysis_results.csv"
df_QG = pd.read_csv(fileQG)
df_QG["Source"] = "QG"
df_RG = pd.read_csv(fileRG)
df_RG["Source"] = "RG"

df = pd.concat([df_QG, df_RG], ignore_index=True)

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
            baseline_over = np.maximum(0, baseline_values - target_values)
            alignment_over = np.maximum(0, alignment_values - target_values)

            # Negative mean_diff means that alignment has a smaller value for sentences exceeding the target (closer to the target)
            diff = alignment_over - baseline_over
            mean_diff = diff.mean() 
            
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
            "n": n
        })

""" Store the results """
stat_df = pd.DataFrame(stat_test_results)
individual_df = pd.DataFrame(individual_differences)
name = "SL"
stat_df.to_csv(name + '_testing_overlength.csv', index=False)
individual_df.to_csv(name + '_testing_overlength_ind.csv', index=False)
