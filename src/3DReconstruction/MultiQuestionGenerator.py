import os
import json
import random
import numpy as np
from collections import OrderedDict
import multiprocessing as mp
from tqdm import tqdm
from QAGenerator import ThreeDReconstructionQAGenerator
from ThreeDimensionalReconstruction import ThreeDimensionalReconstruction

class MultiQuestionGenerator:
    """
    生成器类，先生成游戏状态，然后对每个状态生成所有类型的问题
    """
    def __init__(self):
        """初始化生成器"""
        self.dataset = []
        self.state_count = 0
        self.qa_count = 0
        self.qa_generator = ThreeDReconstructionQAGenerator()
        
    def generate_game_state(self, plot_level=None):
        """
        生成一个游戏状态
        
        Args:
            plot_level (str): 可选的难度级别 'Easy'(2-5个), 'Medium'(6-10个), 'Hard'(11-15个)
            
        Returns:
            dict: 游戏状态信息
        """
        self.state_count += 1
        
        # 生成游戏实例
        game = self.qa_generator.generate_game_instance(plot_level)
        game_state = game.get_game_state()
        target_count = game_state['target_count']
        
        # 随机选择要显示的结构类型
        structure_type = random.choice(['current', 'solution', 'custom'])
        
        if structure_type == 'current':
            structure = game_state['current_state']['positions']
        elif structure_type == 'solution':
            structure = game_state['complete_solution']['positions']
        else:  # custom
            # 计算还可以添加的最大体素数量
            current_count = game_state['current_state']['count']
            remaining_count = target_count - current_count
            
            if remaining_count <= 0:
                # 如果没有剩余空间，就使用current状态
                structure = game_state['current_state']['positions']
            else:
                # 在剩余空间内随机生成
                current_structure, new_voxels = game.generate_random_connected_voxels(random.randint(1, remaining_count))
                structure = current_structure + new_voxels
        
        # 创建输出目录
        os.makedirs("reconstruction_dataset/images", exist_ok=True)
        os.makedirs("reconstruction_dataset/states", exist_ok=True)
        
        # 生成文件名
        base_name = f"reconstruction_state_{self.state_count:05d}"
        image_path = f"images/{base_name}.png"
        state_path = f"states/{base_name}.json"
        
        # 保存可视化
        if structure_type == 'current':
            game.visualize_structure(show_solution=False, name=f"reconstruction_dataset/{image_path}")
        elif structure_type == 'solution':
            game.visualize_structure(show_solution=True, name=f"reconstruction_dataset/{image_path}")
        else:
            game.visualize_structure(structure=structure, name=f"reconstruction_dataset/{image_path}")
            
        # 计算投影和剩余方块数
        target_yz_proj, target_xz_proj = game.get_projections(game_state['complete_solution']['positions'])
        remaining_voxels = len(game_state['complete_solution']['positions']) - len(structure)
            
        # 保存state信息
        state_info = {
            'voxel_positions': sorted(structure),
            'target_yz_projection': target_yz_proj.T.tolist(),  # 转置矩阵
            'target_xz_projection': target_xz_proj.T.tolist(),  # 转置矩阵
            'remaining_voxels': remaining_voxels
        }
        with open(f"reconstruction_dataset/{state_path}", 'w') as f:
            json.dump(state_info, f, indent=2)
        
        # 返回游戏状态信息
        return {
            'game': game,
            'game_state': game_state,
            'structure': structure,
            'structure_type': structure_type,
            'base_name': base_name,
            'image_path': image_path,
            'state_path': state_path,
            'plot_level': self.qa_generator.get_plot_level(target_count)
        }
    
    def generate_all_questions_for_state(self, state_info):
        """
        为一个游戏状态生成所有类型的问题
        
        Args:
            state_info (dict): 游戏状态信息
            
        Returns:
            list: 该游戏状态对应的所有问题
        """
        results = []
        
        # 获取游戏状态信息
        game = state_info['game']
        game_state = state_info['game_state']
        structure = state_info['structure']
        base_name = state_info['base_name']
        image_path = state_info['image_path']
        state_path = state_info['state_path']
        plot_level = state_info['plot_level']
        
        # 问题类型
        question_types = ['count', 'position', 'projection', 'action_outcome', 
                         'transition_path', 'strategy_optimization']
        
        # 对每种类型生成问题
        for question_type in question_types:
            self.qa_count += 1
            
            # 根据问题类型生成问题
            if question_type == 'count':
                question_result = self.qa_generator.generate_count_question(structure)
                question_id = 0
                qa_level = "Easy"
                qa_type = 'StateInfo'
            elif question_type == 'position':
                question_result = self.qa_generator.generate_position_question(structure)
                question_id = 1
                qa_level = "Easy"
                qa_type = 'StateInfo'
            elif question_type == 'projection':
                question_result = self.qa_generator.generate_projection_question(
                    structure, 
                    game_state['complete_solution']['positions'],
                    game
                )
                question_id = 2
                qa_level = "Medium"
                qa_type = 'StateInfo'
            elif question_type == 'action_outcome':
                # 对于action_outcome类型，必须使用当前状态而不是自定义状态
                question_result = self.qa_generator.generate_action_outcome_question(
                    game_state['current_state']['positions'],
                    game_state['complete_solution']['positions'],
                    game
                )
                question_id = 3
                qa_level = "Medium"
                qa_type = 'ActionOutcome'
            elif question_type == 'transition_path':
                question_result = self.qa_generator.generate_transition_path_question(game_state, game)
                question_id = 4
                qa_level = "Hard"
                qa_type = 'TransitionPath'
            else:  # 'strategy_optimization'
                question_result = self.qa_generator.generate_strategy_optimization_question(game_state, game)
                question_id = 5
                qa_level = "Hard"
                qa_type = 'StrategyOptimization'
            
            # 创建数据集条目
            entry = OrderedDict([
                ("data_id", f"{base_name}_qa_{question_type}_{self.qa_count:05d}"),
                ("qa_type", qa_type),
                ("question_id", question_id),
                ("question_description", (
                    "Count the total number of voxels in the given 3D structure." if question_type == 'count' else
                    "Choose the position that contains a voxel from the given options." if question_type == 'position' else
                    "Choose how the given 3D structure's projections match with the target projections." if question_type == 'projection' else
                    "Predict the projection matrix after adding specified voxels to the current structure." if question_type == 'action_outcome' else
                    "Choose the correct sequence of voxel additions that will make the structure match the target projection(s) while following game rules." if question_type == 'transition_path' else
                    "Find the minimum number of additional voxels needed to match both target projections."
                )),
                ("image", image_path),
                ("state", state_path),
                ("plot_level", plot_level),
                ("qa_level", qa_level),
                ("question", question_result[0] if isinstance(question_result, tuple) else question_result['question']),
                ("answer", question_result[1] if isinstance(question_result, tuple) else question_result['answer']),
                ("analysis", question_result[3] if isinstance(question_result, tuple) else question_result['analysis'])
            ])
            
            # 如果是position、projection或transition_path类型的问题，添加options字段
            if question_type in ['position', 'projection', 'transition_path']:
                entry["options"] = question_result[2] if isinstance(question_result, tuple) else question_result['options']
            
            results.append(entry)
        
        return results
    
    def generate_datasets(self, total_states, plot_level_ratios=None):
        """
        生成数据集
        
        Args:
            total_states (int): 要生成的游戏状态总数
            plot_level_ratios (list): 可选的难度比例，如 [0.2, 0.2, 0.6] 分别对应 Easy, Medium, Hard
            
        Returns:
            list: 生成的数据集
        """
        # 重置数据集
        self.dataset = []
        self.state_count = 0
        self.qa_count = 0
        
        # 创建输出目录
        os.makedirs("reconstruction_dataset/images", exist_ok=True)
        os.makedirs("reconstruction_dataset/states", exist_ok=True)
        
        # 确定每种难度级别的状态数量
        level_counts = self._calculate_level_distribution(total_states, plot_level_ratios)
        
        print(f"\n开始生成数据集，总游戏状态数：{total_states}")
        print(f"各难度级别状态数量：")
        for level, count in level_counts.items():
            print(f"- {level}: {count}")
        print(f"每个状态将生成6种类型的问题，总问答对数量：{total_states * 6}")
        print()
        
        # 生成状态和问题
        all_states = []
        print("生成游戏状态中...")
        for level, count in level_counts.items():
            for _ in tqdm(range(count), desc=f"生成{level}难度状态"):
                state_info = self.generate_game_state(level)
                all_states.append(state_info)
        
        # 为每个状态生成问题
        print("\n为每个状态生成问题中...")
        for state_info in tqdm(all_states, desc="问题生成进度"):
            questions = self.generate_all_questions_for_state(state_info)
            self.dataset.extend(questions)
        
        # 保存数据集
        print("\n保存数据集...")
        with open("reconstruction_dataset/data.json", "w") as f:
            json.dump(self.dataset, f, indent=2)
        
        print(f"\n数据集生成完成！共生成 {total_states} 个游戏状态，{len(self.dataset)} 个问答对")
        
        # 打印每种类型和难度的问题数量统计
        self._print_statistics()
        
        return self.dataset
    
    def _calculate_level_distribution(self, total_states, plot_level_ratios=None):
        """计算每种难度级别的状态数量"""
        if plot_level_ratios is None:
            # 默认平均分配
            base_count = total_states // 3
            extra = total_states % 3
            
            level_counts = {
                'Easy': base_count + (1 if 0 < extra else 0),
                'Medium': base_count + (1 if 1 < extra else 0),
                'Hard': base_count + (1 if 2 < extra else 0)
            }
        else:
            # 使用指定的比例
            level_counts = {
                'Easy': int(total_states * plot_level_ratios[0]),
                'Medium': int(total_states * plot_level_ratios[1])
            }
            # 最后一个难度级别保证总和等于total_states
            level_counts['Hard'] = total_states - level_counts['Easy'] - level_counts['Medium']
        
        return level_counts
    
    def _print_statistics(self):
        """打印数据集统计信息"""
        print("\n问题分布统计：")
        type_level_stats = {
            'count': {'Easy': 0, 'Medium': 0, 'Hard': 0},
            'position': {'Easy': 0, 'Medium': 0, 'Hard': 0},
            'projection': {'Easy': 0, 'Medium': 0, 'Hard': 0},
            'ActionOutcome': {'Easy': 0, 'Medium': 0, 'Hard': 0},
            'TransitionPath': {'Easy': 0, 'Medium': 0, 'Hard': 0},
            'StrategyOptimization': {'Easy': 0, 'Medium': 0, 'Hard': 0}
        }
        
        for entry in self.dataset:
            qa_type = entry['qa_type']
            plot_level = entry['plot_level']
            
            if qa_type == 'StateInfo':
                # 对StateInfo类型，根据question_id区分子类型
                if entry['question_id'] == 0:
                    type_level_stats['count'][plot_level] += 1
                elif entry['question_id'] == 1:
                    type_level_stats['position'][plot_level] += 1
                elif entry['question_id'] == 2:
                    type_level_stats['projection'][plot_level] += 1
            else:
                # 其他类型直接统计
                type_level_stats[qa_type][plot_level] += 1
            
        # 按照指定顺序打印统计信息
        print_order = ['count', 'position', 'projection', 'ActionOutcome', 
                      'TransitionPath', 'StrategyOptimization']
        
        # 计算最长的类型名称长度（考虑StateInfo前缀）
        display_names = {
            'count': 'StateInfo - count',
            'position': 'StateInfo - position',
            'projection': 'StateInfo - projection',
            'ActionOutcome': 'ActionOutcome',
            'TransitionPath': 'TransitionPath',
            'StrategyOptimization': 'StrategyOptimization'
        }
        max_type_len = max(len(display_names[qa_type]) for qa_type in print_order)
        
        # 打印对齐的统计信息
        for qa_type in print_order:
            stats = type_level_stats[qa_type]
            total = sum(stats.values())
            display_name = display_names[qa_type]
            print(f"- {display_name:<{max_type_len}}: {stats['Easy']:>3}, {stats['Medium']:>3}, {stats['Hard']:>3} (total: {total:>3})")
        
        print(f"\n文件保存在 reconstruction_dataset/ 目录下：")
        print("- data.json          （数据集）")
        print("- images/            （可视化图片）")
        print("- states/            （状态文件）")
