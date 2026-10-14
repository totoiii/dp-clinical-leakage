#!/usr/bin/env bash

# Script maestro para lanzar múltiples experimentos de generación de texto
# Usando run_generate.sh para distintos directorios de modelos entrenados



# Lista de directorios de modelos a evaluar
#model_dirs=(

model_dirs=("output/llama-1B-i2b2-0can-common-nodp" "output/llama-1B-i2b2-0can-common-8eps" "output/llama-1B-i2b2-0can-common-4eps"
"output/llama-1B-i2b2-0can-rare-nodp" "output/llama-1B-i2b2-0can-rare-8eps" "output/llama-1B-i2b2-0can-rare-4eps"
) 




# Parámetros comunes
num_seq=20
length=512
temperature=1.0
top_k=50
top_p=0.95
device="cuda:1"
language_prompt="en"

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

