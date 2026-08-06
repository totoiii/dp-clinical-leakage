#!/usr/bin/env bash

# Script para ejecutar dp_finetuning.py con parámetros de ejemplo
# Uso: bash run_finetuning.sh [output_dir] [model_name] [dataset_name] [canaries] [type_of_canaries] [language_prompt] [target_epsilon] [disable_dp]

OUTPUT_DIR=${1:-output/test_llama-1B-nodp}
MODEL_NAME=${2:-meta-llama/Llama-3.2-1B}
DATASET=${3:-meddocan}
CANARIES=${4:-100}
TYPE_CANARIES=${5:-common}
LANG_PROMPT=${6:-es}
EPSILON=${7:-8}
DISABLE_DP_FLAG=${8:-true}

# Parámetros fijos
SEQ_LEN=1024
BATCH_SIZE=2
GRAD_ACC=1
EVAL_STRATEGY="steps"
EVAL_STEPS=10000000
SAVE_STRATEGY="no"
LOG_LEVEL="info"
EVAL_BATCH=8
EVAL_ACC_STEPS=1
SEED=42
REMOVE_UNUSED_COLUMNS=false
WEIGHT_DECAY=0.01
EPOCHS=30
LOGGING_STEPS=5
MAX_GRAD_NORM=1.0
LR_SCHED="constant"
LR=3e-4
DISABLE_TQDM=true
NUM_WORKERS=2
LORA_DIM=4
LORA_ALPHA=32
LORA_DROPOUT=0.0
ENABLE_LORA="--enable_lora"
TARGET_MODULES="['q_proj', 'k_proj', 'v_proj', 'o_proj']"

# Construir flags DP
if [[ "$DISABLE_DP_FLAG" == "true" ]]; then
  DP_FLAG="--disable_dp"
else
  DP_FLAG="--target_epsilon $EPSILON --per_sample_max_grad_norm 1.0"
fi

mkdir -p $OUTPUT_DIR/logs

python -m torch.distributed.run \
  --nproc_per_node 3 src/dp_finetuning.py \
  --output_dir $OUTPUT_DIR \
  --model_name $MODEL_NAME \
  --dataset_name $DATASET \
  --sequence_len $SEQ_LEN \
  --per_device_train_batch_size $BATCH_SIZE \
  --gradient_accumulation_steps $GRAD_ACC \
  --eval_steps $EVAL_STEPS \
  --save_strategy $SAVE_STRATEGY \
  --log_level $LOG_LEVEL \
  --per_device_eval_batch_size $EVAL_BATCH \
  --eval_accumulation_steps $EVAL_ACC_STEPS \
  --seed $SEED \
  --weight_decay $WEIGHT_DECAY \
  --remove_unused_columns $REMOVE_UNUSED_COLUMNS \
  --num_train_epochs $EPOCHS \
  --logging_steps $LOGGING_STEPS \
  --max_grad_norm $MAX_GRAD_NORM \
  --lr_scheduler_type $LR_SCHED \
  --learning_rate $LR \
  --disable_tqdm $DISABLE_TQDM \
  --dataloader_num_workers $NUM_WORKERS \
  --lora_dim $LORA_DIM \
  --lora_alpha $LORA_ALPHA \
  --lora_dropout $LORA_DROPOUT \
  $ENABLE_LORA \
  --target_modules "$TARGET_MODULES" \
  --canaries_dataset $CANARIES \
  --type_of_canaries $TYPE_CANARIES \
  --language_prompt $LANG_PROMPT \
  $DP_FLAG \
  > $OUTPUT_DIR/logs/train.log 2>&1

# #  --evaluation_strategy $EVAL_STRATEGY \