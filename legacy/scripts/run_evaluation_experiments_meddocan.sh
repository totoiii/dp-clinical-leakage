
#Uso: bash run_evaluation.sh [output_dir] [dataset_name] [canaries] [type_of_canaries] [language_prompt] [sequence_len]
# Lista de directorios de modelos a evaluar


output_dirs_10can_common=("output/llama-1B-meddocan-10can-common-nodp" "output/llama-1B-meddocan-10can-common-8eps" "output/llama-1B-meddocan-10can-common-4eps" "output_after_review/llama-1B-meddocan-10can-rare-2eps" "output_after_review/llama-1B-meddocan-10can-rare-16eps")



#for output_dir in "${output_dirs_100can_rare[@]}"; do
#  # Llama a run_evaluation.sh con los 6 argumentos esperados:
#  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
#  bash scripts/evaluation.sh \
#    "$output_dir" \
#    "meddocan" \
#    "100" \
#    "rare" \
#    "es" \
#    "512"
#
#    
#done
##
#for output_dir in "${output_dirs_10can_rare[@]}"; do
#  # Llama a run_evaluation.sh con los 6 argumentos esperados:
#  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
#  bash scripts/evaluation.sh \
#    "$output_dir" \
#    "meddocan" \
#    "10" \
#    "rare" \
#     "es" \
#    "512"
#done
#
#for output_dir in "${output_dirs_0can_common[@]}"; do
#  # Llama a run_evaluation.sh con los 6 argumentos esperados:
#  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
#  bash scripts/evaluation.sh \
#    "$output_dir" \
#    "meddocan" \
#    "0" \
#    "common" \
#    "es" \
#    "512"
#done
#for output_dir in "${output_dirs_100can_common[@]}"; do
#  # Llama a run_evaluation.sh con los 6 argumentos esperados:
#  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
#  bash scripts/evaluation.sh \
#    "$output_dir" \
#    "meddocan" \
#    "100" \
#    "common" \
#    "es" \
#    "512"
#done
for output_dir in "${output_dirs_10can_common[@]}"; do
  # Llama a run_evaluation.sh con los 6 argumentos esperados:
  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
  bash scripts/evaluation.sh \
    "$output_dir" \
    "meddocan" \
    "10" \
    "common" \
    "es" \
    "512"
done
#for output_dir in "${output_dirs_1can_common[@]}"; do
#  # Llama a run_evaluation.sh con los 6 argumentos esperados:
#  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
#  bash scripts/evaluation.sh \
#    "$output_dir" \
#    "meddocan" \
#    "1" \
#    "common" \
#    "es" \
#    "512"
#  done
#for output_dir in "${output_dirs_1can_rare[@]}"; do
#  # Llama a run_evaluation.sh con los 6 argumentos esperados:
#  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
#  bash scripts/evaluation.sh \
#    "$output_dir" \
#    "meddocan" \
#    "1" \
#    "rare" \
#    "es" \
#    "512"
#done