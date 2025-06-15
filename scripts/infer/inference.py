# inference.py
from tqdm import tqdm
from swift.llm import RequestConfig
from swift.plugin import InferStats

def infer_requests(engine, requests, request_config, metric, batch_size, desc):
    """
    Perform inference in batches and yield responses.

    Args:
        engine: The inference engine.
        requests (List[dict]): List of all inference requests.
        request_config (RequestConfig): Configuration for the inference request.
        metric (InferStats): Metrics collection instance.
        batch_size (int): Number of requests per batch.
        desc (str): Description for the progress bar.

    Yields:
        List[dict]: List of processed responses for each batch.
    """
    total_batches = (len(requests) + batch_size - 1) // batch_size
    for i in tqdm(range(total_batches), desc=desc):
        batch_requests = requests[i * batch_size : (i + 1) * batch_size]
        responses = engine.infer(batch_requests, request_config, metrics=[metric])
        processed_responses = [{'conclusion': resp.choices[0].message.content} for resp in responses]
        yield processed_responses
