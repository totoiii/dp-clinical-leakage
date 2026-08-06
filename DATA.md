# Obtaining the datasets

This repository does **not** include any patient data. You must obtain the
corpora yourself and place them under `data/`.

## i2b2 2014 (English)

- Governed by a **Data Use Agreement** that **prohibits redistribution**.
- Request access via the i2b2 / n2c2 NLP Research Data Sets portal:
  https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/

## MEDDOCAN (Spanish)

- Synthetic Spanish clinical case reports with PII annotations.
- Available at: https://github.com/PlanTL-GOB-ES/SPACCC_MEDDOCAN

## Expected layout

After downloading, the pipeline expects preprocessed files under `data/<dataset>/`,
for example:

```
data/
  i2b2/
    original_tags.csv      # source PII spans grouped by document
    all_labels.csv         # flat list of PII values used for matching
  meddocan/
    original_tags.csv
    all_labels.csv
```

The preprocessing that produces these files from the raw corpora is described in
the paper (Section: Datasets) and in `src/load_dataset.py`.

## Base model

The generative-null baseline uses the non-fine-tuned base model
`meta-llama/Llama-3.2-1B` (download from Hugging Face; access must be requested on
the model card). Point `BASE_MODEL` in `null_generative.py` to a local path or the
HF model id.

## Note on generated outputs

Fine-tuned model outputs (`results/`, `null_base/`) reproduce real training PII by
design (that is the leakage being measured) and are therefore **not** distributed.
