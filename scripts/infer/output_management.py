# output_management.py
import os
import json

def save_results_mode3(responses, datasets, dataset_names, output_folder, suffix):
    """
    Save results for mode=3 by dataset.

    Args:
        responses (List[List[dict]]): List of response lists from inference, each sublist corresponds to a dataset.
        datasets (List[List[dict]]): List of datasets, each dataset is a list of entries.
        dataset_names (List[str]): List of dataset names.
        output_folder (str): Folder to save the results.
        suffix (str): Suffix to append to the output filename.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    for dataset_name, dataset, dataset_responses in zip(dataset_names, datasets, responses):
        dataset_results = []
        for entry, response in zip(dataset, dataset_responses):
            dataset_results.append({
                "question": entry.get('question', entry.get('query', '')),
                "answer": entry.get('answer', entry.get('response', '')),
                "prediction": response.get('conclusion', '')
            })
        
        if suffix:
            output_file = os.path.join(output_folder, f"{suffix}-{dataset_name}.json")
        else:
            output_file = os.path.join(output_folder, f"{dataset_name}.json")
        
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(dataset_results, file, indent=4, ensure_ascii=False)
        
        print(f"Results saved to {output_file}")
