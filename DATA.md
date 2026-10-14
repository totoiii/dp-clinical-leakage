# Obtaining the datasets

This repository contains **no patient data**. Obtain the corpora yourself and run
`scripts/prepare_data.py`, which writes them to `data/` (git-ignored; set `DPLEAK_DATA`
to use another location).

## i2b2 2014 de-identification (English)

- 1,304 discharge-style notes from 296 patients (train + test of the shared task; we
  fine-tune on all of them). Distributed under a **Data Use Agreement** that prohibits
  redistribution: https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/
- File names are `<patient>-<note>.xml`; the patient id defines the author-level privacy unit.

## MEDDOCAN (Spanish)

- 1,000 synthetic clinical case reports (train + dev + test), one case per file:
  https://github.com/PlanTL-GOB-ES/SPACCC_MEDDOCAN (i2b2-style XML).

## Layout produced by `prepare_data.py`

```
data/{i2b2,meddocan}/
  original/*.xml        every note, XML with <TEXT> and <TAGS>
  original_tags.csv     one row per annotated span (Filename,Tag Name,ID,Start,End,Text,Type,Comment)
  all_labels.csv        unique annotated values (text,TYPE), used for matching
```

Canary conditions are not stored: `dpleak/data.py` builds them on the fly from
`original/`, `canaries/` and `canaries/replacement_map.json`
(`scripts/verify_conditions.py` checks them against pre-built folders).

## Base model

`meta-llama/Llama-3.2-1B` (gated on Hugging Face). Set `DPLEAK_BASE_MODEL` to a local path
if needed.

## Generated outputs

`runs/` (adapters, `generations.csv`, review samples) reproduces training identifiers by
design and must not be distributed. `results/` holds only aggregate numbers.
