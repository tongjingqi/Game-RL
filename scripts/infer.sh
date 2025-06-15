#!/bin/bash

set -e  

# Configuration
MODEL_NAME="/path/to/your/model"
MODEL_TYPE="qwen2.5vl"  # Example model type, adjust as needed
INFER_BACKEND="vllm"

# Timestamps for unique output folders
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_BASE="pipeline_results_$TIMESTAMP"


python ./scripts/infer/main.py \
    --model_name "$MODEL_NAME" \
    --model_type "$MODEL_TYPE" \
    --dataset_names "MMMU-Pro,CharXiv,MathVista" \
    --output_folder "$OUTPUT_BASE/inference" \
    --infer_backend "$INFER_BACKEND" \
    --max_tokens 4096 \
    --temperature 0.2 \
    --suffix "pipeline_$TIMESTAMP"