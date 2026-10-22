import os
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

""" In this script the difference in RS ARI differences between conditions is calculated 
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

# Select only the ARI score
df["ARI_user"] = df["[ARI, Flesch]user"].apply(lambda x: eval(x)[0] if isinstance(x, str) else x)   # Target
df["ARI_model"] = df["[ARI, Flesch]model"].apply(lambda x: eval(x)[0] if isinstance(x, str) else x)

""" We loop over the two different tasks specified: Reflection and Question Generation """
for source in ['QG', 'RG']:
    source_df = df[df['Source'] == source]
    """ We loop over the different models for which we have ran the simulation"""
    for model in source_df['Model'].unique():
        model_df = source_df[source_df['Model'] == model]


        """ Aggregate over Transcript_nr the mean Value per Condition (baseline/alignment) """
        baseline_agg = (
            model_df[model_df['Condition'] == 'baseline']
            .groupby(['Transcript_nr', 'Model', 'ARI_user'], dropna=False)['ARI_model']
            .mean()
            .reset_index()
        )
        alignment_agg = (
            model_df[model_df['Condition'] == 'alignment']
            .groupby(['Transcript_nr', 'Model', 'ARI_user'], dropna=False)['ARI_model']
            .mean()
            .reset_index()
        )

        """ Merge on keys to get matched pairs correctly """
        merged = pd.merge(
            baseline_agg,
            alignment_agg,
            on=['Transcript_nr', 'Model', 'ARI_user'],
            suffixes=('_baseline', '_alignment')
        )

        mean_target = model_df['ARI_user'].mean()

        baseline_values = merged['ARI_model_baseline'].reset_index(drop=True)
        alignment_values = merged['ARI_model_alignment'].reset_index(drop=True)

        n = len(merged)
        if n > 2:
            # Positive mean_diff means that alignment was more difficult than the baseline
            diff = alignment_values - baseline_values
            mean_diff = diff.mean() 
            n = len(diff)

        # Store individual differences
        for i, row in merged.iterrows():
            individual_differences.append({
                'Source': source,
                'Model': model,
                'Transcript_nr': row['Transcript_nr'],
                'Baseline': row['ARI_model_baseline'],
                'Alignment': row['ARI_model_alignment'],
                "Target mean": mean_target,
                'Difference': row['ARI_model_alignment'] - row['ARI_model_baseline']
            })


        stat_test_results.append({
            "Source": source,
            "Model": model,
            "Target mean": mean_target,
            "Baseline mean±std": f"{baseline_values.mean():.2f} ± {baseline_values.std(ddof=1):.2f}",
            "Alignment mean±std": f"{alignment_values.mean():.2f} ± {alignment_values.std(ddof=1):.2f}",
            "Mean difference ARI": mean_diff,
            "n": n
        })

""" Store the results """
stat_df = pd.DataFrame(stat_test_results)
individual_df = pd.DataFrame(individual_differences)
stat_df.to_csv('testing_ARI.csv', index=False)
individual_df.to_csv('testing_ARI_ind.csv', index=False)
