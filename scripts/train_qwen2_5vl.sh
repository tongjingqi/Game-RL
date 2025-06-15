#!/bin/bash

# Environment variables
export OMP_NUM_THREADS=4
export MASTER_PORT=29501

# Path configuration
export PROJECT_ROOT="."
export MODEL_PATH="${PROJECT_ROOT}/models/Qwen2.5-VL-7B-Instruct"
export DATA_PATH="${PROJECT_ROOT}/data/GameQA_RL_5k.json"
export PLUGIN_PATH="${PROJECT_ROOT}/Code2Logic/ms-swift/examples/train/grpo/plugin/plugin.py"
export SYSTEM_PROMPT="${PROJECT_ROOT}/Code2Logic/ms-swift/examples/train/grpo/game_prompt.txt"
export OUTPUT_DIR="${PROJECT_ROOT}/Code2Logic/output/models/qwen2.5vl_grpo"
export LOG_FILE="${PROJECT_ROOT}/Code2Logic/logs/qwen2.5vl_grpo.log"


MAX_PIXELS=1003520 \
CUDA_VISIBLE_DEVICES=1,2,3,4,5 \
NPROC_PER_NODE=4 \
swift rlhf \
    --rlhf_type grpo \
    --model ${MODEL_PATH} \
    --model_type qwen2_5_vl \
    --use_vllm true \
    --vllm_device auto \
    --vllm_gpu_memory_utilization 0.5 \
    --vllm_max_model_len 8192 \
    --external_plugins ${PLUGIN_PATH} \
    --reward_funcs external_r1v_acc \
    --train_type full \
    --torch_dtype bfloat16 \
    --dataset ${DATA_PATH} \
    --max_completion_length 2048 \
    --num_train_epochs 1 \
    --freeze_vit true \
    --per_device_train_batch_size 3 \
    --per_device_eval_batch_size 3 \
    --learning_rate 5e-7 \
    --lr_scheduler_type constant_with_warmup \
    --eval_steps 400 \
    --save_steps 400 \
    --save_only_model true \
    --save_total_limit 3 \
    --logging_steps 5 \
    --max_length 2048 \
    --output_dir ${OUTPUT_DIR} \
    --warmup_ratio 0.05 \
    --dataloader_num_workers 4 \
    --dataset_num_proc 4 \
    --num_generations 12 \
    --async_generate true \
    --temperature 1.0 \
    --top_p 0.85 \
    --top_k 50 \
    --system ${SYSTEM_PROMPT} \
    --deepspeed zero3 \
    --log_completions true \
    --gradient_accumulation_steps 2 \
    --num_iterations 1 \
    --num_infer_workers 1 \
    > ${LOG_FILE} 2>&1
    # --report_to wandb \

echo "Training started. Check logs at: ${LOG_FILE}"