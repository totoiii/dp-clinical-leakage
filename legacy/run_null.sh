#!/usr/bin/env bash
# Generate the generative-null baseline (base model, no fine-tuning) for both
# datasets, then compute fine-tuned-vs-base enrichment.
cd "$(dirname "$0")" || exit 1
echo "===== START $(date) ====="
echo "----- i2b2 (1000) -----"
python3 null_generative.py --stage all --dataset i2b2 --num 1000 --batch 50
echo "----- meddocan (1000) -----"
python3 null_generative.py --stage all --dataset meddocan --num 1000 --batch 50
echo "----- enrichment (fine-tuned vs base) -----"
python3 generative_null.py
echo "===== DONE $(date) ====="
