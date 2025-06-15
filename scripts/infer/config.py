# config.py
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run multimodal inference for mode=3.")

    # Required arguments for mode=3
    parser.add_argument('--model_name', type=str, required=True,
                        help='Path to the model checkpoint')
    parser.add_argument('--model_type', type=str, required=True,
                        help='Type of the model to load (e.g., internvl, internvl2, etc.)')
    parser.add_argument('--dataset_names', type=str, required=True,
                        help='Comma-separated list of dataset names')
    parser.add_argument('--output_folder', type=str, required=True,
                        help='Folder to save the inference results')
    parser.add_argument('--infer_backend', type=str, choices=['lmdeploy', 'vllm', 'pt'], required=True,
                        help='Inference backend to use')

    # Optional arguments
    parser.add_argument('--suffix', type=str, default='', 
                        help='Suffix to append to the output filename')

    # Model-specific parameters
    parser.add_argument('--pt_max_batch_size', type=int, default=64,
                        help='Max batch size for PtEngine (default: 64)')
    parser.add_argument('--vllm_max_model_len', type=int, default=32768,
                        help='Max model length for VllmEngine (default: 32768)')
    parser.add_argument('--lmdeploy_tp', type=int, default=1,
                        help='Tensor parallelism for LmdeployEngine (default: 1)')

    # Inference configuration parameters
    parser.add_argument('--max_tokens', type=int, default=4096,
                        help='Maximum number of tokens for the inference request (default: 4096)')
    parser.add_argument('--temperature', type=float, default=0.2,
                        help='Temperature setting for the inference request (default: 0.2)')

    # Progress bar description
    parser.add_argument('--progress_desc', type=str, default="Inference Batches",
                        help='Description for the progress bar (default: "Inference Batches")')

    return parser.parse_args()
