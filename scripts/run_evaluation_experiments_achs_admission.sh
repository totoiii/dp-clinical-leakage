
#Uso: bash run_evaluation.sh [output_dir] [dataset_name] [canaries] [type_of_canaries] [language_prompt] [sequence_len]
# Lista de directorios de modelos a evaluar para achs_admission


output_dirs_0can_rare=("output_after_review/llama-1B-achs_admission-0can-rare-nodp" "output_after_review/llama-1B-achs_admission-0can-rare-2eps" "output_after_review/llama-1B-achs_admission-0can-rare-4eps" "output_after_review/llama-1B-achs_admission-0can-rare-8eps" "output_after_review/llama-1B-achs_admission-0can-rare-16eps")
output_dirs_100can_rare=("output_after_review/llama-1B-achs_admission-100can-rare-nodp" "output_after_review/llama-1B-achs_admission-100can-rare-2eps" "output_after_review/llama-1B-achs_admission-100can-rare-4eps" "output_after_review/llama-1B-achs_admission-100can-rare-8eps" "output_after_review/llama-1B-achs_admission-100can-rare-16eps")
output_dirs_100can_common=("output_after_review/llama-1B-achs_admission-100can-common-nodp" "output_after_review/llama-1B-achs_admission-100can-common-4eps")
output_dirs_10can_rare=("output_after_review/llama-1B-achs_admission-10can-rare-nodp" "output_after_review/llama-1B-achs_admission-10can-rare-2eps" "output_after_review/llama-1B-achs_admission-10can-rare-4eps" "output_after_review/llama-1B-achs_admission-10can-rare-8eps" "output_after_review/llama-1B-achs_admission-10can-rare-16eps")
output_dirs_1can_rare=("output_after_review/llama-1B-achs_admission-1can-rare-nodp" "output_after_review/llama-1B-achs_admission-1can-rare-2eps" "output_after_review/llama-1B-achs_admission-1can-rare-4eps" "output_after_review/llama-1B-achs_admission-1can-rare-8eps" "output_after_review/llama-1B-achs_admission-1can-rare-16eps")






for output_dir in "${output_dirs_0can_rare[@]}"; do
  # Llama a run_evaluation.sh con los 6 argumentos esperados:
  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
  bash scripts/evaluation.sh \
    "$output_dir" \
    "achs_admission" \
    "0" \
    "rare" \
    "en" \
    "512"
done

#for output_dir in "${output_dirs_100can_rare[@]}"; do
#  # Llama a run_evaluation.sh con los 6 argumentos esperados:
#  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
#  bash scripts/evaluation.sh \
#    "$output_dir" \
#    "achs_admission" \
#    "100" \
#    "rare" \
#    "en" \
#    "512"
#done
#
#for output_dir in "${output_dirs_100can_common[@]}"; do
#  # Llama a run_evaluation.sh con los 6 argumentos esperados:
#  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
#  bash scripts/evaluation.sh \
#    "$output_dir" \
#    "achs_admission" \
#    "100" \
#    "common" \
#    "en" \
#    "512"
#done
#
#for output_dir in "${output_dirs_10can_rare[@]}"; do
#  # Llama a run_evaluation.sh con los 6 argumentos esperados:
#  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
#  bash scripts/evaluation.sh \
#    "$output_dir" \
#    "achs_admission" \
#    "10" \
#    "rare" \
#    "en" \
#    "512"
#done
#
#for output_dir in "${output_dirs_1can_rare[@]}"; do
#  # Llama a run_evaluation.sh con los 6 argumentos esperados:
#  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
#  bash scripts/evaluation.sh \
#    "$output_dir" \
#    "achs_admission" \
#    "1" \
#    "rare" \
#    "en" \
#    "512"
#done