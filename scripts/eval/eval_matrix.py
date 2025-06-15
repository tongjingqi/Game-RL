import json
import argparse
import logging
from openai import OpenAI
from tqdm import tqdm
import os
import re
import concurrent.futures
from threading import Lock
from typing import List, Dict, Any

def setup_logging(log_level: str, log_file: str) -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def create_openai_client(api_key: str, base_url: str) -> OpenAI:
    """Create OpenAI client"""
    return OpenAI(api_key=api_key, base_url=base_url)

def simplify_text(text: str, markers: List[str] = None) -> str:
    """Simplify text and extract key parts"""
    if not markers:
        markers = ["###", "therefore", "conclusion"]
    
    for marker in markers:
        if marker in text.lower():
            index = text.lower().rfind(marker)
            return text[index:].strip()
    
    # For questions, extract the last sentence
    if "?" in text:
        question_index = text.rfind("?")
        period_index = text[:question_index].rfind(".")
        if period_index != -1:
            return text[period_index + 1:].strip()
    
    return text

def create_evaluation_messages(entry: Dict[str, Any]) -> List[Dict[str, str]]:
    """Create evaluation messages"""
    system_prompt =  """Compare the ground truth with the prediction from AI model and determine if the prediction is correct. 
    The question is about an image, which we have not given here. You need to determine whether the model's prediction 
    is consistent with the ground truth. No points will be awarded for wrong answers, over answers or under answers. 
    The reasoning process in the prediction does not need to be considered too much, you only need to determine if the 
    final answer is consistent. There are times when the answer may have a different form of expression and some variation 
    is acceptable.
    """
    
    question = simplify_text(entry["question"])
    prediction = simplify_text(entry["prediction"])
    
    # Handle multiple choice questions
    if "options" in entry and entry["options"]:
        answer = entry["answer"]
        if isinstance(answer, int) or (isinstance(answer, str) and answer.isdigit()):
            correct_option = entry["options"][int(answer) - 1]
            ground_truth = f"The correct option is {answer}: {correct_option}"
        else:
            ground_truth = f"The correct option is {answer}"
    else:
        ground_truth = f"The correct answer is {entry['answer']}"
    
    user_content = f"""## Question: {question}
    ## Ground Truth: {ground_truth}
    ## Prediction: {prediction}

    You need to determine whether the model's prediction is consistent with the ground truth. Output only:
    Correctness: (Yes or No)"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

def extract_correctness(response: str) -> str:
    """Extract correctness judgment from response"""
    match = re.search(r"Correctness:\s*(.*)", response, re.IGNORECASE)
    if match:
        answer = match.group(1).strip().lower()
        return "yes" if "yes" in answer else "no" if "no" in answer else "unknown"
    return "unknown"

def evaluate_entry(client: OpenAI, model_name: str, entry: Dict[str, Any]) -> str:
    """Evaluate single entry"""
    try:
        messages = create_evaluation_messages(entry)
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=512,
            temperature=0.0,
        )
        return extract_correctness(response.choices[0].message.content.strip())
    except Exception as e:
        logging.error(f"Evaluation failed: {e}")
        return "unknown"

class StatsTracker:
    """Statistics tracker"""
    def __init__(self):
        self.stats_matrix = {}
        self.incorrect_data_ids = {}
        self.lock = Lock()
        self.correct = 0
        self.total = 0
    
    def update(self, entry: Dict[str, Any], is_correct: bool):
        """Update statistics"""
        with self.lock:
            self.total += 1
            if is_correct:
                self.correct += 1
            
            qid = entry.get("question_id", 0)
            level = entry.get("plot_level", "Unknown")
            data_id = entry.get("data_id", "unknown")
            
            # Initialize statistics matrix
            if qid not in self.stats_matrix:
                self.stats_matrix[qid] = {}
            if level not in self.stats_matrix[qid]:
                self.stats_matrix[qid][level] = {"correct": 0, "total": 0}
            
            # Update statistics
            self.stats_matrix[qid][level]["total"] += 1
            if is_correct:
                self.stats_matrix[qid][level]["correct"] += 1
            else:
                # Record incorrect data IDs
                if qid not in self.incorrect_data_ids:
                    self.incorrect_data_ids[qid] = {}
                if level not in self.incorrect_data_ids[qid]:
                    self.incorrect_data_ids[qid][level] = []
                self.incorrect_data_ids[qid][level].append(data_id)
    
    def get_accuracy(self) -> float:
        """Get accuracy rate"""
        return (self.correct / self.total * 100) if self.total > 0 else 0

def process_dataset(client: OpenAI, model_name: str, input_paths: List[str], 
                   output_path: str, num_threads: int) -> None:
    """Process datasets"""
    results = []
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Load existing results
    processed_datasets = set()
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
            processed_datasets = {r["dataset_path"] for r in results}

    for input_path in input_paths:
        if input_path in processed_datasets:
            logging.info(f"Skipping already processed dataset: {input_path}")
            continue

        # Load dataset
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load dataset {input_path}: {e}")
            continue

        tracker = StatsTracker()
        short_path = os.path.join(*input_path.split(os.sep)[-3:])
        
        def process_entry(entry):
            evaluation = evaluate_entry(client, model_name, entry)
            is_correct = evaluation.lower() == "yes"
            tracker.update(entry, is_correct)
            return evaluation

        # Parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            list(tqdm(
                executor.map(process_entry, dataset),
                total=len(dataset),
                desc=f"Processing {short_path}"
            ))

        # Save results
        accuracy = tracker.get_accuracy()
        result = {
            "dataset_path": input_path,
            "model": model_name,
            "accuracy": f"{accuracy:.2f}% ({tracker.correct}/{tracker.total})",
            "stats_matrix": tracker.stats_matrix,
            "incorrect_data_ids": tracker.incorrect_data_ids
        }
        results.append(result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        logging.info(f"Dataset {input_path} accuracy: {accuracy:.2f}%")

def get_input_paths(args) -> List[str]:
    """Get input path list"""
    if args.input_directory:
        paths = []
        checkpoint_range = None
        
        if args.checkpoint_range:
            start, end = map(int, args.checkpoint_range.split('--'))
            checkpoint_range = (start, end)
        
        for root, dirs, _ in os.walk(args.input_directory):
            if root != args.input_directory:
                continue
            
            for dir_name in dirs:
                if not dir_name.startswith('checkpoint-'):
                    continue
                
                try:
                    checkpoint_num = int(dir_name.split('-')[1])
                    if checkpoint_range and not (checkpoint_range[0] <= checkpoint_num <= checkpoint_range[1]):
                        continue
                    
                    checkpoint_dir = os.path.join(root, dir_name)
                    for subroot, _, files in os.walk(checkpoint_dir):
                        for filename in files:
                            if filename.endswith('.json'):
                                paths.append(os.path.join(subroot, filename))
                except ValueError:
                    continue
        
        return paths
    
    return args.input_json_paths or []

def main():
    parser = argparse.ArgumentParser(description="Evaluate AI model performance")
    parser.add_argument('--api_key', required=True, help='OpenAI API key')
    parser.add_argument('--base_url', required=True, help='API base URL')
    parser.add_argument('--model_name', required=True, help='Model name')
    parser.add_argument('--input_json_paths', nargs='*', help='Input JSON path list')
    parser.add_argument('--input_directory', help='Directory containing JSON files')
    parser.add_argument('--checkpoint_range', help='Checkpoint range (e.g.: "0--1610")')
    parser.add_argument('--output_json_path', required=True, help='Output JSON path')
    parser.add_argument('--num_threads', type=int, default=4, help='Number of parallel threads')
    parser.add_argument('--log_level', default='INFO', help='Log level')
    parser.add_argument('--log_file', default='evaluation.log', help='Log file path')
    
    args = parser.parse_args()
    
    setup_logging(args.log_level, args.log_file)
    
    input_paths = get_input_paths(args)
    if not input_paths:
        logging.error("No input files found!")
        return
    
    client = create_openai_client(args.api_key, args.base_url)
    process_dataset(client, args.model_name, input_paths, args.output_json_path, args.num_threads)

if __name__ == '__main__':
    main()
