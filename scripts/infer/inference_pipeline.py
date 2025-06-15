import os
from data_processing import load_datasets, prepare_requests
from model_management import load_model
from inference import infer_requests
from output_management import save_results_mode3
from swift.llm import RequestConfig
from swift.plugin import InferStats

class InferencePipeline:
    dataset_path_map = {
        'MMMU-Pro': "./dataset/MMMU_Pro_10c",
        'CharXiv': "./dataset/charxiv",
        'MathVista': "./dataset/MathVista_mini",
    }

    def __init__(self, args):
        self.args = args
        os.makedirs(self.args.output_folder, exist_ok=True)

    def build_dataset_paths(self, dataset_names):
        """根据数据集名称列表构建数据集路径列表"""
        dataset_paths = []
        for name in dataset_names:
            name = name.strip()
            if name not in self.dataset_path_map:
                raise ValueError(f"Dataset name '{name}' is not in the allowed choices.")
            dataset_path = self.dataset_path_map[name]
            data_file = os.path.join(dataset_path, 'data.json')
            dataset_paths.append(data_file)
        return dataset_paths
    
    def pipeline(self):
        """执行推理流水线"""
        if not self.args.model_name or not self.args.dataset_names:
            raise ValueError("model_name and dataset_names must be specified.")

        # 准备数据集
        dataset_names = [name.strip() for name in self.args.dataset_names.split(',')]
        dataset_paths = self.build_dataset_paths(dataset_names)
        datasets = load_datasets(dataset_paths)
        
        print(f"Total loaded dataset entries: {sum(len(ds) for ds in datasets)}")

        # 准备推理请求
        requests_per_dataset = prepare_requests(datasets, 3)
        print(f"Total prepared request batches: {len(requests_per_dataset)}")

        # 加载模型
        try:
            engine = load_model(
                self.args.model_name,
                self.args.model_type,
                self.args.infer_backend,                
                pt_max_batch_size=self.args.pt_max_batch_size,
                vllm_max_model_len=self.args.vllm_max_model_len,
                lmdeploy_tp=self.args.lmdeploy_tp
            )
            print(f"Model loaded successfully using backend '{self.args.infer_backend}'.")
        except Exception as e:
            print(f"Error loading model: {e}")
            return

        # 执行推理
        all_responses = []
        for dataset_name, dataset_requests in zip(dataset_names, requests_per_dataset):
            print(f"\nProcessing dataset: {dataset_name}")
            print(f"Processing {len(dataset_requests)} entries in dataset '{dataset_name}'.")

            request_config = RequestConfig(max_tokens=self.args.max_tokens, temperature=self.args.temperature)
            metric = InferStats()
            
            responses = []
            for batch_responses in infer_requests(engine, dataset_requests, request_config, metric, len(dataset_requests), self.args.progress_desc):
                responses.extend(batch_responses)
            
            all_responses.append(responses)

        # 保存结果
        save_results_mode3(all_responses, datasets, dataset_names, self.args.output_folder, self.args.suffix)
        print("\nInference complete.")
