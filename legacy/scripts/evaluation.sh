#!/usr/bin/env bash

#Script para ejecutar evaluate_model.py con parámetros de ejemplo

#Uso: bash run_evaluate.sh [output_dir] [dataset_name] [canaries] [type_of_canaries] [language_prompt] [sequence_len]

OUTPUT_DIR=${1:-output/test_llama-1B-nodp}
DATASET=${2:-meddocan}
CANARIES=${3:-100}
TYPE_CANARIES=${4:-common}
LANG_PROMPT=${5:-es}
SEQ_LEN=${6:-512}

#Crear carpeta de logs

mkdir -p $OUTPUT_DIR/logs

python evaluation.py --output_dir $OUTPUT_DIR \
    --dataset_name $DATASET \
    --canaries_dataset $CANARIES \
    --type_of_canaries $TYPE_CANARIES \
    --language_prompt $LANG_PROMPT \
    --sequence_len $SEQ_LEN \
    > $OUTPUT_DIR/logs/evaluation.log 2>&1

