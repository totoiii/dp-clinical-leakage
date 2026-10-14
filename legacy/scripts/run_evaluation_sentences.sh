output_dirs_100can_common=("output/llama-1B-i2b2_sentences-100can-common-nodp" "output/llama-1B-i2b2_sentences-100can-common-8eps")
output_dirs_10can_common=("output/llama-1B-i2b2_sentences-10can-common-nodp" "output/llama-1B-i2b2_sentences-10can-common-8eps")


for output_dir in "${output_dirs_100can_common[@]}"; do
  # Llama a run_evaluation.sh con los 6 argumentos esperados:
  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
  bash scripts/evaluation.sh \
    "$output_dir" \
    "i2b2_sentences" \
    "100" \
    "common" \
    "en" \
    "512"
done
for output_dir in "${output_dirs_10can_common[@]}"; do
  # Llama a run_evaluation.sh con los 6 argumentos esperados:
  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
  bash scripts/evaluation.sh \
    "$output_dir" \
    "i2b2_sentences" \
    "10" \
    "common" \
    "en" \
    "512"
done

output_dirs_100can_common=("output/llama-1B-meddocan_sentences-100can-common-nodp" "output/llama-1B-meddocan_sentences-100can-common-8eps")
output_dirs_10can_common=("output/llama-1B-meddocan_sentences-10can-common-nodp" "output/llama-1B-meddocan_sentences-10can-common-8eps")


for output_dir in "${output_dirs_100can_common[@]}"; do
  # Llama a run_evaluation.sh con los 6 argumentos esperados:
  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
  bash scripts/evaluation.sh \
    "$output_dir" \
    "meddocan_sentences" \
    "100" \
    "common" \
    "es" \
    "512"
done
for output_dir in "${output_dirs_10can_common[@]}"; do
  # Llama a run_evaluation.sh con los 6 argumentos esperados:
  # 1) output_dir, 2) dataset_name, 3) canaries_dataset, 4) type_of_canaries, 5) language_prompt, 6) sequence_len
  bash scripts/evaluation.sh \
    "$output_dir" \
    "meddocan_sentences" \
    "10" \
    "common" \
    "es" \
    "512"
done