#!/bin/bash

set -e  

API_KEY="your-api-key-here"
BASE_URL="http://0.0.0.0:8075/v1"
EVAL_MODEL="Qwen2.5-72B-Instruct-AWQ"
OUTPUT_BASE="pipeline_results_$TIMESTAMP"

python eval_matrix.py \
    --api_key "$API_KEY" \
    --base_url "$BASE_URL" \
    --model_name "$EVAL_MODEL" \
    --input_directory "$OUTPUT_BASE/inference" \
    --output_json_path "$OUTPUT_BASE/evaluation_results.json" \
    --num_threads 4 \
    --log_level "INFO" \
    --log_file "$OUTPUT_BASE/evaluation.log"