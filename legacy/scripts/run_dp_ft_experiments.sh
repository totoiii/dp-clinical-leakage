#!/usr/bin/env bash

# Script maestro para lanzar múltiples experimentos de dp_finetuning
# Llama a run_finetuning.sh con los 8 argumentos esperados:
# 1) output_dir, 2) model_name, 3) dataset_name, 4) canaries_dataset,
# 5) type_of_canaries, 6) language_prompt, 7) target_epsilon, 8) disable_dp_flag

# Arrays de valores a iterar
# Usamos el dataset TAB
datasets=("tab" "ai4privacy/pii-masking-300k")

model_names=("meta-llama/Llama-3.1-8B-Instruct" "meta-llama/Llama-3.2-1B-Instruct")
model_suffix="llama-8B"

# Puedes ajustar estos hiperparámetros si lo deseas
epsilons=(2 4 8 16 32)
canaries=(0)          # para TAB no usamos canaries, pero el argumento sigue siendo obligatorio
types=(common)        # se ignora para TAB
disable_dp_flags=(false true)

# Carpeta base para resultados
BASE_OUTPUT="results/output_after_review"
# TAB está en inglés
lang="en"

for dataset in "${datasets[@]}"; do
  for model in "${model_names[@]}"; do
    for can in "${canaries[@]}"; do
      for type_can in "${types[@]}"; do
        for disable_dp in "${disable_dp_flags[@]}"; do
          if [[ "$disable_dp" == "true" ]]; then
            # Sin DP: pasar epsilon=0 y disable_dp_flag=true
            epsilon=0
            flag_dp=true
            out_dir="$BASE_OUTPUT/${model}-${dataset}-${can}can-${type_can}-nodp"
            bash scripts/finetuning.sh \
              "$out_dir" \
              "$model" \
              "$dataset" \
              "$can" \
              "$type_can" \
              "$lang" \
              "$epsilon" \
              "$flag_dp"
          else
            # Con DP: iterar sobre epsilons y disable_dp_flag=false
            flag_dp=false
            for epsilon in "${epsilons[@]}"; do
              out_dir="$BASE_OUTPUT/${model_suffix}-${dataset}-${can}can-${type_can}-${epsilon}eps"
              bash scripts/finetuning.sh \
                "$out_dir" \
                "$model" \
                "$dataset" \
                "$can" \
                "$type_can" \
                "$lang" \
                "$epsilon" \
                "$flag_dp"
            done
          fi
        done
      done
    done
  done

done

# Bloque antiguo comentado para referencia
# #!/usr/bin/env bash
# 
# # Script maestro para lanzar múltiples experimentos de dp_finetuning
# # Llama a run_finetuning.sh con los 8 argumentos esperados:
# # 1) output_dir, 2) model_name, 3) dataset_name, 4) canaries_dataset,
# # 5) type_of_canaries, 6) language_prompt, 7) target_epsilon, 8) disable_dp_flag
# 
# # Arrays de valores a iterar
# datasets=(achs_admission_sentences)
# 
# model_names=("meta-llama/Llama-3.1-8B-Instruct")
# model_suffix="llama-8B"
# 
# epsilons=(16)
# canaries=(100 10 0)
# types=(common)
# disable_dp_flags=(false true)
# 
# # Carpeta base para resultados
# BASE_OUTPUT="results/output_after_review"
# lang="es"
# 
# for dataset in "${datasets[@]}"; do
#   for model in "${model_names[@]}"; do
# 
#     for can in "${canaries[@]}"; do
#       for type_can in "${types[@]}"; do
#         for disable_dp in "${disable_dp_flags[@]}"; do
#           if [[ "$disable_dp" == "true" ]]; then
#             # Sin DP: pasar epsilon=0 y disable_dp_flag=true
#             epsilon=0
#             flag_dp=true
#             # Creamos un sufijo para colocarlo en el directorio de salida, 
#             
#             # Crear directorio de salida:
#         
#             out_dir="$BASE_OUTPUT/${model_suffix}-${dataset}-${can}can-${type_can}-nodp"
#             bash scripts/finetuning.sh \
#               "$out_dir" \
#               "$model" \
#               "$dataset" \
#               "$can" \
#               "$type_can" \
#               "$lang" \
#               "$epsilon" \
#               "$flag_dp"
#           else
#             # Con DP: iterar sobre epsilons y disable_dp_flag=false
#             flag_dp=false
#             for epsilon in "${epsilons[@]}"; do
#               out_dir="$BASE_OUTPUT/${model_suffix}-${dataset}-${can}can-${type_can}-${epsilon}eps"
#               bash scripts/finetuning.sh \
#                 "$out_dir" \
#                 "$model" \
#                 "$dataset" \
#                 "$can" \
#                 "$type_can" \
#                 "$lang" \
#                 "$epsilon" \
#                 "$flag_dp"
#             done
#           fi
#         done 
#       done
#     done
#   done
# 
# done
# 
# 
# #!/usr/bin/env bash
# 
# # Script maestro para lanzar múltiples experimentos de dp_finetuning
# # Llama a run_finetuning.sh con los 8 argumentos esperados:
# # 1) output_dir, 2) model_name, 3) dataset_name, 4) canaries_dataset,
# # 5) type_of_canaries, 6) language_prompt, 7) target_epsilon, 8) disable_dp_flag
# 
# # Arrays de valores a iterar
# ##datasets=(achs_admission)
# ##model_names=("meta-llama/Llama-3.2-1B")
# ##epsilons=(2 4 8 16)
# ##canaries=(100)
# ##types=(rare)
# ##disable_dp_flags=(false)
# ##
# ### Carpeta base para resultados
# ##BASE_OUTPUT="output_after_review"
# ##
# ##for dataset in "${datasets[@]}"; do
# ##  for model in "${model_names[@]}"; do
# ##
# ##    # crear sufijo para el modelo
# ##    if [[ "$model" == *"meta-llama/Llama-3.2-1B"* ]]; then
# ##      model_suffix="llama-1B"
# ##    else
# ##      model_suffix="other"
# ##    fi
# ##
# ##    if [[ "$dataset" == "achs_admission" ]]; then
# ##      lang="es"
# ##    elif [[ "$dataset" == "achs_admission_sentences" ]]; then
# ##      lang="es"
# ##    elif [[ "$dataset" == "meddocan" ]]; then
# ##      lang="es"
# ##    elif [[ "$dataset" == "meddocan_sentences" ]]; then
# ##      lang="es"
# ##    elif [[ "$dataset" == "i2b2_sentences" ]]; then
# ##      lang="en"
# ##    elif [[ "$dataset" == "i2b2" ]]; then
# ##      lang="en"
# ##    else
# ##      lang="error"
# ##    fi
# ##
# ##    for can in "${canaries[@]}"; do
# ##      for type_can in "${types[@]}"; do
# ##        for disable_dp in "${disable_dp_flags[@]}"; do
# ##          if [[ "$disable_dp" == "true" ]]; then
# ##            # Sin DP: pasar epsilon=0 y disable_dp_flag=true
# ##            epsilon=0
# ##            flag_dp=true
# ##            # Creamos un sufijo para colocarlo en el directorio de salida, 
# ##            
# ##            # Crear directorio de salida:
# ##        
# ##            out_dir="$BASE_OUTPUT/${model_suffix}-${dataset}-${can}can-${type_can}-nodp"
# ##            bash scripts/finetuning.sh \
# ##              "$out_dir" \
# ##              "$model" \
# ##              "$dataset" \
# ##              "$can" \
# ##              "$type_can" \
# ##              "$lang" \
# ##              "$epsilon" \
# ##              "$flag_dp"
# ##          else
# ##            # Con DP: iterar sobre epsilons y disable_dp_flag=false
# ##            flag_dp=false
# ##            for epsilon in "${epsilons[@]}"; do
# ##              out_dir="$BASE_OUTPUT/${model_suffix}-${dataset}-${can}can-${type_can}-${epsilon}eps"
# ##              bash scripts/finetuning.sh \
# ##                "$out_dir" \
# ##                "$model" \
# ##                "$dataset" \
# ##                "$can" \
# ##                "$type_can" \
# ##                "$lang" \
# ##                "$epsilon" \
# ##                "$flag_dp"
# ##            done
# ##          fi
# ##        done 
# ##      done
# ##    done
# ##  done
# ##
# ##done
# ##
# ##