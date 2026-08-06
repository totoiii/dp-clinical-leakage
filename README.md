# Multi-Entity Privacy Leakage in DP Clinical Text Generation

Code for the paper **"Beyond Single Identifiers: Multi-Entity Privacy Leakage in
Differentially Private Clinical Text Generation."**

We DP-SGD fine-tune Llama-3.2-1B (with LoRA) on English (i2b2 2014) and Spanish
(MEDDOCAN) clinical corpora under privacy budgets ε ∈ {4, 8, ∞}, then audit the
generated synthetic text with two complementary tools:

1. **Canary-document experiment** — full, realistic clinical narratives embedding
   controlled PII across multiple notes per patient, scored by perplexity ranking
   over 10,000 candidates.
2. **Multi-entity (tuple) leakage audit** — exact, type-distinct co-occurrences of
   real training PII in the generated corpus, calibrated against a **generative
   null model** (the same pipeline run on the *non-fine-tuned* base model).

>  **No patient data is included in this repository.** The i2b2 2014 corpus is
> governed by a Data Use Agreement that prohibits redistribution, and generated
> outputs reproduce real training PII. See [`DATA.md`](DATA.md) to obtain the
> datasets. Only source code and aggregate result files (no PII) are shipped here.

## Repository layout

```
src/                     Training & evaluation pipeline
  dp_finetuning.py         DP-SGD + LoRA fine-tuning entry point
  generate_text.py         Synthetic-text generation from a fine-tuned model
  evaluation.py            Canary perplexity ranking + PII matching
  load_dataset.py          Dataset loading / preprocessing
  utils.py                 Prompts, PII matching, tuple co-occurrence counting
  dp_transformers/         Vendored Microsoft dp-transformers (MIT, see NOTICE)
scripts/                 Shell wrappers for fine-tuning, generation, evaluation
reanalysis.py            Comparable-unit recount + largest-tuple-per-profile
canary_ranks.py          rep=1/10/100 canary ranks + bootstrap 95% CIs
null_generative.py       Generative null: generate with the base model, match PII
generative_null.py       Apples-to-apples fine-tuned-vs-base enrichment
compare_base_ft.py       Quick per-pair base-vs-fine-tuned comparison
*_results.json           Aggregate results reported in the paper (no PII)
```

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .          # installs the vendored dp_transformers package
```

Python ≥ 3.9. A CUDA GPU is recommended for fine-tuning/generation; the
generative-null generation also runs on Apple Silicon (MPS).

## Pipeline

1. **Obtain the data** — see [`DATA.md`](DATA.md); place it under `data/`.
2. **Fine-tune** (DP-SGD + LoRA):
   ```bash
   bash scripts/finetuning.sh output/llama-1B-meddocan-nodp \
        meta-llama/Llama-3.2-1B meddocan 100 common es 8 true
   ```
3. **Generate** synthetic documents:
   ```bash
   bash scripts/generate_text.sh
   ```
4. **Evaluate** (canary ranking + PII/tuple matching):
   ```bash
   bash scripts/run_evaluation_experiments_i2b2.sh
   ```
5. **Re-analysis reported in the paper** (runs on already-generated outputs):
   ```bash
   python reanalysis.py            # comparable units + largest-tuple-per-profile
   python canary_ranks.py          # canary ranks + bootstrap CIs
   ```
6. **Generative null model** (base-model baseline requested by reviewers):
   ```bash
   bash run_null.sh                # generate 1,000 docs/dataset with the base model
   python generative_null.py       # fine-tuned-vs-base enrichment -> JSON
   ```

## Results

The `*_results.json` files contain the exact aggregate numbers reported in the
paper (single/tuple leakage in comparable units, largest-tuple-per-profile,
canary ranks with bootstrap CIs, and generative-null enrichment). They contain
**no** patient PII.

## Attribution & license

The `src/dp_transformers/` subpackage is Microsoft's
[dp-transformers](https://github.com/microsoft/dp-transformers) (MIT License),
included unmodified except where noted; its upstream README is preserved as
`README_dp_transformers_upstream.md` and its copyright in [`NOTICE`](NOTICE).
All other code in this repository is released under the MIT License
([`LICENSE`](LICENSE)).

## Citation

```bibtex
@article{multientity_leakage,
  title   = {Beyond Single Identifiers: Multi-Entity Privacy Leakage in
             Differentially Private Clinical Text Generation},
  journal = {BMC Medical Informatics and Decision Making},
  year    = {2026},
  note    = {Under review}
}
```
