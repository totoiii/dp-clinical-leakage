#!/usr/bin/env bash

# Script maestro para lanzar múltiples experimentos de generación de texto
# Usando run_generate.sh para distintos directorios de modelos entrenados



# Lista de directorios de modelos a evaluar (excluyendo i2b2)
model_dirs=(
"output_after_review/llama-1B-achs_admission-0can-rare-16eps"
"output_after_review/llama-1B-achs_admission-0can-rare-2eps"
"output_after_review/llama-1B-achs_admission-0can-rare-4eps"
"output_after_review/llama-1B-achs_admission-0can-rare-8eps"
"output_after_review/llama-1B-achs_admission-0can-rare-nodp"
"output_after_review/llama-1B-achs_admission-100can-common-4eps"
"output_after_review/llama-1B-achs_admission-100can-common-nodp"
"output_after_review/llama-1B-achs_admission-100can-rare-16eps"
"output_after_review/llama-1B-achs_admission-100can-rare-2eps"
"output_after_review/llama-1B-achs_admission-100can-rare-4eps"
"output_after_review/llama-1B-achs_admission-100can-rare-8eps"
"output_after_review/llama-1B-achs_admission-100can-rare-nodp"
"output_after_review/llama-1B-achs_admission-10can-rare-16eps"
"output_after_review/llama-1B-achs_admission-10can-rare-2eps"
"output_after_review/llama-1B-achs_admission-10can-rare-4eps"
"output_after_review/llama-1B-achs_admission-10can-rare-8eps"
"output_after_review/llama-1B-achs_admission-10can-rare-nodp"
"output_after_review/llama-1B-achs_admission-1can-rare-16eps"
"output_after_review/llama-1B-achs_admission-1can-rare-2eps"
"output_after_review/llama-1B-achs_admission-1can-rare-4eps"
"output_after_review/llama-1B-achs_admission-1can-rare-8eps"
"output_after_review/llama-1B-achs_admission-1can-rare-nodp"
"output_after_review/llama-1B-meddocan-0can-rare-16eps"
"output_after_review/llama-1B-meddocan-0can-rare-2eps"
"output_after_review/llama-1B-meddocan-0can-rare-nodp"
"output_after_review/llama-1B-meddocan-100can-rare-16eps"
"output_after_review/llama-1B-meddocan-100can-rare-2eps"
"output_after_review/llama-1B-meddocan-100can-rare-nodp"
"output_after_review/llama-1B-meddocan-10can-rare-16eps"
"output_after_review/llama-1B-meddocan-10can-rare-2eps"
"output_after_review/llama-1B-meddocan-10can-rare-nodp"
"output_after_review/llama-1B-meddocan-1can-rare-16eps"
"output_after_review/llama-1B-meddocan-1can-rare-2eps"
"output_after_review/llama-1B-meddocan-1can-rare-nodp"
) 


# Parámetros comunes
num_seq=20
length=512
temperature=1.0
top_k=50
top_p=0.95
device="cuda:0"
language_prompt="es"

for model_dir in "${model_dirs[@]}"; do
  bash scripts/generate_text.sh \
    "$model_dir" \
    "$num_seq" \
    "$length" \
    "$temperature" \
    "$top_k" \
    "$top_p" \
    "$device" \
    "$language_prompt" \
  
  done

# para correr este bash colocar
# chmod +x run_generation_experiments_es.sh
# y luego ejecutar ./run_generation_experiments_es.sh
# --- IGNORE ---
