import os
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

""" In this script the difference in RS Flesch differences between conditions is calculated 
Exploratory - Individual simulation results """

stat_test_results = []
individual_differences = []   

""" Here we load the analysis reasults """
fileQG = "QG_output_analysis_results.csv"
fileRG = "RG_output_analysis_results.csv"
df_QG = pd.read_csv(fileQG)
df_QG["Source"] = "QG"
df_RG = pd.read_csv(fileRG)
df_RG["Source"] = "RG"

df = pd.concat([df_QG, df_RG], ignore_index=True)

# Select only the Flesch scores
df["Flesch_user"] = df["[LIX, Flesch]user"].apply(lambda x: eval(x)[1] if isinstance(x, str) else x)
df["Flesch_model"] = df["[LIX, Flesch]model"].apply(lambda x: eval(x)[1] if isinstance(x, str) else x)

""" We loop over the two different tasks specified: Reflection and Question Generation """
for source in ['QG', 'RG']:
    source_df = df[df['Source'] == source]
    """ We loop over the different models for which we have ran the simulation"""
    for model in source_df['Model'].unique():
        model_df = source_df[source_df['Model'] == model]
        """ Aggregate over Transcript_nr the mean Value per Condition (baseline/alignment) """
        baseline_agg = (
            model_df[model_df['Condition'] == 'baseline']
            .groupby(['Transcript_nr', 'Model', 'Flesch_user'], dropna=False)['Flesch_model']
            .mean()
            .reset_index()
        )
        alignment_agg = (
            model_df[model_df['Condition'] == 'alignment']
            .groupby(['Transcript_nr', 'Model', 'Flesch_user'], dropna=False)['Flesch_model']
            .mean()
            .reset_index()
        )

        """ Merge on keys to get matched pairs correctly """
        merged = pd.merge(
            baseline_agg,
            alignment_agg,
            on=['Transcript_nr', 'Model', 'Flesch_user'],
            suffixes=('_baseline', '_alignment')
        )

        mean_target = model_df['Flesch_user'].mean()

        baseline_values = merged['Flesch_model_baseline'].reset_index(drop=True)
        alignment_values = merged['Flesch_model_alignment'].reset_index(drop=True)

        n = len(merged)

        if n > 2:
            # Positive mean_diff means alignment led to easier texts than baseline
            diff = alignment_values - baseline_values
            mean_diff = diff.mean() 
            n = len(diff)

        # Store individual differences
        for i, row in merged.iterrows():
            individual_differences.append({
                'Source': source,
                'Model': model,
                'Transcript_nr': row['Transcript_nr'],
                'Baseline': row['Flesch_model_baseline'],
                'Alignment': row['Flesch_model_alignment'],
                "Target mean": mean_target,
                'Difference': row['Flesch_model_alignment'] - row['Flesch_model_baseline']
            })

        stat_test_results.append({
            "Source": source,
            "Model": model,
            "Target mean": mean_target,
            "Baseline mean±std": f"{baseline_values.mean():.2f} ± {baseline_values.std(ddof=1):.2f}",
            "Alignment mean±std": f"{alignment_values.mean():.2f} ± {alignment_values.std(ddof=1):.2f}",
            "Mean difference Flesch": mean_diff,
            "n": n,
        })

""" Store the results """
stat_df = pd.DataFrame(stat_test_results)
individual_df = pd.DataFrame(individual_differences)
stat_df.to_csv('testing_Flesch.csv', index=False)
individual_df.to_csv('testing_Flesch_ind.csv', index=False)