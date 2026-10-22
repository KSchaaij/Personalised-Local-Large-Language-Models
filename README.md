# Personalised Local Large Language Models
Code corresponding to the paper _Personalising Local Large Language Model Responses To Speaker-Specific Linguistic Patterns_ submitted for the CONVERSATIONS 2026 symposium on chatbots and human-centred AI.

This repository contains resources for the paper:

**Personalising Local Large Language Model Responses To Speaker-Specific Linguistic Patterns**
by Keara Schaaij, Roel Boumans, Tibor Bosse, and Iris Hendrickx

## :file_folder: Repository Information

This repository contains the code scripts correspdonding to the **speaker profile construction** (Section 3.2), **prompt construction** (Section 3.3), and **Evaluation** (Section 4) as described in our paper. 

To keep the repository concise, plotting and statistical testing scripts are excluded. The corresponding results are reported and discussed our paper.

**Important note.** The scripts have been restructured and reorganised to improve logical organisation of our repository. As a result, directory paths and file references from the original project may no longer be valid. In addition, model naming conventions throughout the results may differ slightly from those reported in the paper.

### Directory structure 
The repository is organised into two main folders per language: 
- **LA_EN** - Simulations for English data \
  (**Note** Folders containing (adapted) data are licensed under CC BY-NC-SA 4.0 license, see Data below)

- **LA_NL** - Simulations for Dutch data


Within each language folder, simulations are grouped:
- **Individual_WE** - Common words and expressions (individual simulation)
- **Individual_RS** - Language level (individual simulation)
- **Individual_SL** - Sentence length (individual simulation)
- **Combined** - All three features simultaneously (combined simulation)

and some more general aspects are included:

- **Pre_Post** containing preprocessing and postprocessing scripts for both the Data and the model outputs
- General functions used across subfolders (e.g., related to feature extraction)
- An overview of the number of rejected outputs, number of sentences, and use of emoji's across models and simulations

Each simulation folder contains:
- **Evaluation** folder containing
  - Cleaned model outputs
  - Numerical results
  - Scripts for analysis and evaluation
  - Visuals of the results
- **Prompting** folder containing
  - Scripts for model running
  - Prompt templates and structures
  - Raw model outputs (including rejected outputs)

## :spiral_notepad: Data 
In our work, comparable interview corpora are used for English and Dutch. 

### English
For the English folder, spoken dialogue transcripts are subject to access and usage restrictions imposed by the data providers and folders containing (parts) of this data are therefore licensed under the CC BY-NC-SA 4.0 license. This holds for the folders containing cleaned model outputs, raw model outputs, the _Data_ folder, and the _Turns_prompt_W4_90_ folder.

**Data source** \
CORHOH: Text Corpus Of Holocaust Oral Histories
Jaff, Daban Q (2025), “CORHOH: Text Corpus Of Holocaust Oral Histories”, Mendeley Data, V3, doi: 10.17632/gz7v268252.3

### Dutch
For the Dutch folder, spoken dialogue transcripts are subject to access and usage restrictions imposed by the data providers and therefore cannot be shared publicly. To reproduce the experiments or reuse (part of) the code, transcripts must be obtained from the original sources directly and compliance with the relevant terms of use from the provider must be ensured.

**Data source** \
Nederlands Veteraneninstituut (NLVI): Interviewcollectie Nederlandse veteranen (ICNV) (2024). https://www.veteranenvertellen.nl/

The following interview ID's from the ICNV collection are used in our work:
[243, 349, 436, 451, 566, 596, 597, 602, 605, 606, 611, 616, 716, 750, 781, 789, 797, 798, 804, 815, 852, 966, 967, 968, 973, 1016, 1026, 1063, 1083, 1106, 1125, 1297, 1299, 1300, 1301, 1302, 1323, 1324, 1413, 1444, 1445, 1463, 1487, 1551, 1630, 1650, 1651, 1668, 1672, 1700]. 


## Acknowledgments
This work is part of the project Responsible AI for Voice Diagnostics (RAIVD) with file number NGF.1607.22.013 of the research program NGF AiNed Fellowship Grants, which is financed by the Dutch Research Council (NWO). Part of this research was funded by the Dutch Research Council (NWO) through the QoLEAD (Quality of Life by use of Enabling AI in Dementia) project (project: KICH1.GZ02.20.008).