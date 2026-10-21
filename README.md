# Multi-entity privacy leakage in DP clinical text generation

Code for **"Beyond Single Identifiers: Multi-Entity Privacy Leakage in Differentially
Private Clinical Text Generation"** (BMC Medical Informatics and Decision Making).

We fine-tune Llama-3.2-1B (4-bit nf4 + LoRA) on English (i2b2 2014) and Spanish
(MEDDOCAN) clinical notes, without DP and with DP-SGD at ε ∈ {8, 4} under two privacy
units: the **record** (each note) and the **author** (all notes of one patient, or of the
canary profile; for canary sentences, the profile together with the patients whose notes
carry the paragraph). We then run two audits:

1. **Canary experiment** (publisher-side, needs model access). Fictitious patient profiles
   are inserted as 1, 10 or 100 distinct LLM-written clinical-style notes (*canary
   documents*), or as one fixed paragraph prepended to 10 or 100 notes (*canary
   sentences*). Memorisation of single identifiers and of identifier tuples is measured by
   the perplexity rank of the true value among 10,000 alternatives.
2. **Multi-entity leakage audit** (data-release setting, needs only the synthetic text).
   Training identifiers, and tuples of identifiers from one source note, that reappear in
   1,000 generated documents, calibrated against the non-fine-tuned model and checked for
   clinical context.

> **No patient data is included.** i2b2 2014 is distributed under a Data Use Agreement, and
> generated documents reproduce training identifiers. See [`DATA.md`](DATA.md). Only code,
> the synthetic canary inputs and aggregate result files are released.

## Layout

```
dpleak/                    the pipeline (one module per step)
  spec.py                    canary profiles, candidate templates, experimental grid, run ids
  data.py                    builds every training condition from the original corpus
  train.py                   QLoRA fine-tuning, non-DP or DP-SGD (record or author unit)
  score.py                   canary perplexity ranking
  generate.py                1,000 synthetic documents per model (and the base-model null)
  leakage.py                 single / tuple leakage, largest tuple per profile, type-pair rates
  context.py                 clinical context of matched pairs (similarity rank vs null)
  lexical.py                 lexical comparison of canaries and source corpora
canaries/                  synthetic inputs: 2 x 100 canary documents per dataset,
                           replacement map, candidate pools (no real data)
scripts/
  prepare_data.py            derive annotation tables from the licensed XML corpora
  corpus_stats.py            corpus statistics (word tokens, vocabulary, PII instances)
  verify_conditions.py       check the rebuilt conditions against pre-built folders
  run_queue.py               resumable multi-GPU queue for the whole study
  aggregate.py               per-run outputs -> results/*.json
  make_tables.py             results/*.json -> LaTeX tables of the manuscript
  make_figures.py            results/*.json -> figures of the manuscript (same summaries as the tables)
  compare_with_paper.py      re-run vs. previously published numbers (consistency report)
results/                   aggregate results reported in the paper (no PII):
  corpus_stats.json          counts of the two corpora (Table 1)
  runs_index.json            every training run: privacy accounting, utility
  accounting.json            per DP configuration: N_u, q, sigma, epsilon (see note below)
  canary_ranks.json          canary ranks per run; canary_summary.json: median/range over seeds
  name_field_ranks.json      MEDDOCAN document canaries: name ranked in header-field format
  sent_control_ranks.json    sentence-canary templates scored on the no-canary models (control)
  leakage_runs.json          leakage per synthetic corpus; leakage_summary.json: median/range, enrichment
  context_*.json             clinical-context analysis per setting; context_summary.json
  legacy_rescore.json        previously published adapters re-scored with the pinned canaries
  consistency_report.md      re-run vs. previously published numbers, cell by cell
  diagnostics/               checks referenced in legacy/AUDIT.md
vendor/dp_transformers/    Microsoft dp-transformers (MIT), with two documented patches
legacy/                    code and result files of the first submission, and the audit
                           of its canary evaluation (legacy/AUDIT.md)
```

**Privacy accounting.** For every DP configuration the noise multiplier σ is the smallest
value whose PRV upper bound on ε, at error tolerance 0.05, does not exceed the target
(`results/accounting.json`, field `epsilon_prv`). The `epsilon_prv` stored in each
`run.json` (and copied to `runs_index.json`) is the trainer's own accountant, which uses
tolerance 0.1 and therefore reports up to ~0.05 above the target for the same σ
(`accounting.json`, field `epsilon_prv_trainer`). δ = 1/N_u, with N_u the number of privacy
units.

## Run identifiers

`{dataset}_{docs|sent}{K}[_{A|B}]_{nodp|eps8|eps4}[_{record|author}]_s{seed}`, e.g.
`i2b2_docs100_A_eps8_author_s42`: i2b2, 100 canary documents of profile A, ε = 8 with the
patient/profile as privacy unit, training seed 42. The held-out split (0.1%) is fixed
across seeds.

## Reproducing everything

```bash
uv venv --python 3.10 .venv && source .venv/bin/activate
uv pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu128
huggingface-cli login                                   # Llama-3.2-1B is gated

python scripts/prepare_data.py --dataset i2b2 --xml-dir <i2b2 2014 XML, train+test>
python scripts/prepare_data.py --dataset meddocan --xml-dir <MEDDOCAN XML, all splits>
python scripts/corpus_stats.py                          # -> results/corpus_stats.json

python scripts/run_queue.py --gpus 0,1,2      # 228 training runs + scoring + generation (~260 GPU-h)
python -m dpleak.leakage --all            # leakage audit of every synthetic corpus
for s in nodp eps8_record eps4_record eps8_author eps4_author; do   # clinical context (CPU)
  python -m dpleak.context --dataset i2b2 --out results/context_i2b2_$s.json \
    --gens runs/i2b2_docs0_${s}_s42 runs/i2b2_docs0_${s}_s43 runs/i2b2_docs0_${s}_s44
done                                      # (and nodp, eps8_record, eps4_record for meddocan)
python scripts/aggregate.py               # -> results/*.json
python scripts/make_tables.py             # -> tables for the manuscript
python scripts/make_figures.py            # -> figures for the manuscript
python scripts/compare_with_paper.py      # -> results/consistency_report.md
```

The queue runs, in order: the re-scoring of the previously published adapters (if present),
the seed-42 grid, the base-model corpora, and seeds 43 and 44. It skips every stage whose
output exists, so it can be stopped and restarted at any time (`runs/PAUSE` pauses it;
`runs/MAX_PER_GPU`, e.g. `0:1,1:2`, sets concurrent jobs per GPU). On one 48 GB GPU a run
takes about an hour.

Synthetic text is generated, as in the first submission, from the full-precision base model
with the LoRA adapter (`--quantized` generates with the 4-bit base used in training; see
legacy/AUDIT.md, section 5).

Single steps, e.g. one run:

```bash
python -m dpleak.train --run meddocan_docs10_B_eps4_author_s43
python -m dpleak.score --run meddocan_docs10_B_eps4_author_s43
```

## Changes with respect to the first submission

See [`legacy/AUDIT.md`](legacy/AUDIT.md). In short: the canary values are pinned by value
(the legacy evaluation read them by list position and scored a profile that was never
inserted in 24 of 252 published cells); every condition is trained with three seeds and,
for DP, with both privacy units; generations are written once (the legacy evaluation
appended to its output); leakage is reported with substring and whole-word matching; the
accountant composes exactly the steps run. `results/consistency_report.md` compares every
re-run cell with the previously published value.

## License

MIT ([`LICENSE`](LICENSE)). `vendor/dp_transformers/` is Microsoft's
[dp-transformers](https://github.com/microsoft/dp-transformers) (MIT, see [`NOTICE`](NOTICE));
the two patches (accounting for exactly the steps run, and a robust noise-multiplier
search) are marked `dpleak patch` in the source.
