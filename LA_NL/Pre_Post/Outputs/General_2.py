import pandas as pd

""" This script is used to obtain some additional information about the generation behaviour of the models,
including emoji usage and number of sentences """


stat_test_results = []

""" Here we load the analysis results """
fileQG = "dev_QG_outputGeneral_analysis_results.csv"
fileRG = "dev_RG_outputGeneral_analysis_results.csv"
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
        print(model)

        """ Aggregate over Transcript_nr the mean Value per Condition (baseline/alignment) """
        # Nr of sentences
        baseline_agg = (
            model_df[model_df['Condition'] == 'baseline']
            .groupby(['Transcript_nr', 'Model'], dropna=False)['Nr_of_sentences']
            .mean()
            .reset_index()
        )
        alignment_agg = (
            model_df[model_df['Condition'] == 'alignment']
            .groupby(['Transcript_nr', 'Model'], dropna=False)['Nr_of_sentences']
            .mean()
            .reset_index()
        )
        """ Merge on keys to get matched pairs correctly """
        merged = pd.merge(
            baseline_agg,
            alignment_agg,
            on=['Transcript_nr', 'Model'],
            suffixes=('_baseline', '_alignment')
        )

        baseline_values = merged['Nr_of_sentences_baseline'].reset_index(drop=True)
        alignment_values = merged['Nr_of_sentences_alignment'].reset_index(drop=True)

        # Emoji usage
        baseline_emoji = (
            model_df[model_df['Condition'] == 'baseline']
            .groupby(['Transcript_nr', 'Model'], dropna=False)['Emoji_usage']
            .mean()  
            .reset_index()
        )
        baseline_emoji['Emoji_usage'] *= 100 

        alignment_emoji = (
            model_df[model_df['Condition'] == 'alignment']
            .groupby(['Transcript_nr', 'Model'], dropna=False)['Emoji_usage']
            .mean()
            .reset_index()
        )
        alignment_emoji['Emoji_usage'] *= 100

        emoji_merged = pd.merge(
            baseline_emoji,
            alignment_emoji,
            on='Transcript_nr',
            suffixes=('_baseline', '_alignment')
        )

        # Calculate mean ± std for summary
        baseline_emojis = emoji_merged['Emoji_usage_baseline']
        alignment_emojis = emoji_merged['Emoji_usage_alignment']

        stat_test_results.append({
            "Source": source,
            "Model": model,
            "Baseline #sentences mean±std": f"{baseline_values.mean():.2f} ± {baseline_values.std(ddof=1):.2f}",
            "Alignment #sentences mean±std": f"{alignment_values.mean():.2f} ± {alignment_values.std(ddof=1):.2f}",
            "Baseline smiley fraction ±std": f"{baseline_emojis.mean():.2f} ± {baseline_emojis.std(ddof=1):.2f}",
            "Alignment smiley fraction ±std": f"{alignment_emojis.mean():.2f} ± {alignment_emojis.std(ddof=1):.2f}",
        })

""" Store the results properly """
stat_df = pd.DataFrame(stat_test_results)
summary_cols = [
    "Source",
    "Model",
    "Baseline #sentences mean±std",
    "Alignment #sentences mean±std",
    "Baseline smiley fraction ±std",
    "Alignment smiley fraction ±std"
]
summary_df = stat_df[summary_cols].copy()


