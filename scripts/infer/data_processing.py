# data_processing.py
import os
import json

def load_datasets(dataset_paths):
    """
    Load datasets and adjust image paths.

    Args:
        dataset_paths (List[str]): List of dataset JSON file paths.

    Returns:
        List[List[dict]]: List of datasets, each dataset is a list of entries (dicts).
    """
    all_datasets = []

    for path in dataset_paths:
        if not os.path.isfile(path):
            raise ValueError(f"Dataset path '{path}' does not exist or is not a file.")

        with open(path, 'r', encoding='utf-8') as file:
            dataset = json.load(file)

        # Adjust image paths
        for item in dataset:
            images = item.get('image', None)
            if images is None:
                print(f"Warning: 'image' key is missing in item: {item}")
                item['image'] = []  
                continue  

            if isinstance(images, list):
                item['image'] = [os.path.join(os.path.dirname(path), img) for img in images]
            else:
                item['image'] = [os.path.join(os.path.dirname(path), images)]

        all_datasets.append(dataset)  

    return all_datasets

def prepare_requests(datasets, mode):
    """
    Prepare inference requests.

    Args:
        datasets (List[List[dict]]): List of datasets, each dataset is a list of entries.
        mode (int): Current mode (should be 3).

    Returns:
        List[List[dict]]: List of prepared inference requests per dataset.
    """
    all_requests = []

    for dataset in datasets:
        requests = []
        for entry in dataset:
            query = entry['question']
            content = entry['query']
            content = f"""{query} Let's think step by step.Please analyze the question carefully and follow these requirements:
            Provide detailed step-by-step reasoning,
            Show all your work and calculations,
            End your response with one of these formats:
            1.For choice questions: 'The answer is [option]'
            2.For other questions: 'The answer is [final answer]'
            The final answer line must be on its own line at the very end of your response"""
            request = {
                'messages': [{'role': 'user', 'content': content}],
                'images': entry['image']
            }
            requests.append(request)
        all_requests.append(requests)

    return all_requests
