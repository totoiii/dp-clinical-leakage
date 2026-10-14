#!/usr/bin/env bash

#Script para generar texto usando generate_text.py

#Uso: bash run_generate.sh [output_dir] [num_seq] [length] [temperature] [k] [p] [device] [language_prompt]

OUTPUT_DIR=${1:-output/deepseek-achs_admission-100can-common-8eps}
NUM_SEQ=${2:-1}
LENGTH=${3:-512}
TEMPERATURE=${4:-0.1}
TOP_K=${5:-50}
TOP_P=${6:-0.9}
DEVICE=${7:-cuda:0}
LANGUAGE_PROMPT=${8:-es}

python generate_text.py --output_dir $OUTPUT_DIR \
    --language_prompt $LANGUAGE_PROMPT \
    --num_seq_to_generate $NUM_SEQ \
    --length $LENGTH \
    --temperature $TEMPERATURE \
    --k $TOP_K \
    --p $TOP_P \
    --device $DEVICE \
    > $OUTPUT_DIR/logs/generation.log 2>&1

