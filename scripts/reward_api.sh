#!/bin/bash

# Deploy Qwen2.5-VL-72B-Instruct-AWQ model
swift deploy \
    --model ./models/Qwen2.5-VL-72B-Instruct-AWQ \
    --infer_backend vllm \
    --tensor_parallel_size 1 \
    --gpu_memory_utilization 0.9 \
    --max_model_len 8192 \
    --max_new_tokens 2048 \
    --log_interval 0 \
    --port 8075