# model_management.py
from swift.llm import PtEngine, VllmEngine, LmdeployEngine

def load_model(model_path, model_type, infer_backend, pt_max_batch_size, vllm_max_model_len, lmdeploy_tp):
    """
    Load the model based on the inference backend.

    Args:
        model_path (str): Path to the model checkpoint.
        model_type (str): Type of the model.
        infer_backend (str): Type of inference backend ('pt', 'vllm', 'lmdeploy').
        pt_max_batch_size (int): Max batch size for PtEngine.
        vllm_max_model_len (int): Max model length for VllmEngine.
        lmdeploy_tp (int): Tensor parallelism for LmdeployEngine.

    Returns:
        InferEngine: The loaded inference engine.
    """
    if infer_backend == 'pt':
        engine = PtEngine(model_path, model_type=model_type, max_batch_size=pt_max_batch_size)
    elif infer_backend == 'vllm':
        engine = VllmEngine(model_path, model_type=model_type, max_model_len=vllm_max_model_len)
    elif infer_backend == 'lmdeploy':
        engine = LmdeployEngine(model_path, model_type=model_type, tp=lmdeploy_tp)
    else:
        raise ValueError(f"Unsupported infer_backend: {infer_backend}")
    return engine
