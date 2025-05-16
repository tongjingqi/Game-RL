import json
import os
import random
import numpy as np
from collections import OrderedDict
from ThreeDimensionalReconstruction import ThreeDimensionalReconstruction
import multiprocessing as mp
from tqdm import tqdm
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
matplotlib.pyplot.rcParams['figure.dpi'] = 100

def generate_single_fill_question(args):
    """单个填空题生成函数（用于多进程）"""
    qa_type, qa_count, plot_level = args
    generator = ThreeDReconstructionQAGenerator()
    return generator.generate_fill_pair(qa_types=[qa_type], qa_count=qa_count, plot_level=plot_level)

def generate_single_mcq_question(args):
    """单个选择题生成函数（用于多进程）"""
    qa_count, plot_level = args
    generator = ThreeDReconstructionQAGenerator()
    return generator.generate_mcq_pair(qa_count=qa_count, plot_level=plot_level)

class ThreeDReconstructionQAGenerator:
    def __init__(self):
        self.dataset = []
        self.qa_count = 0
        
    def get_plot_level(self, voxel_count):
        """根据体素数量确定难度级别"""
        if voxel_count <= 5:
            return "Easy"
        elif voxel_count <= 10:
            return "Medium"
        else:  # 11-15
            return "Hard"
        
    def generate_game_instance(self, plot_level=None):
        """
        生成一个游戏实例
        
        Args:
            plot_level (str): 可选的难度级别 'Easy'(2-5个), 'Medium'(6-10个), 'Hard'(11-15个)
        """
        if plot_level == 'Easy':
            target_count = random.randint(3, 5)  # 确保至少3个方块
            initial_count = max(1, target_count - 3)  # 确保至少有1个初始方块
        elif plot_level == 'Medium':
            target_count = random.randint(6, 10)
            initial_count = max(2, target_count - 4)  # 确保至少有2个初始方块
        elif plot_level == 'Hard':
            target_count = random.randint(11, 15)
            initial_count = max(3, target_count - 5)  # 确保至少有3个初始方块
        else:
            target_count = random.randint(3, 15)  # 确保至少3个方块
            if target_count <= 5:
                initial_count = max(1, target_count - 3)
            elif target_count <= 10:
                initial_count = max(2, target_count - 4)
            else:
                initial_count = max(3, target_count - 5)
            
        # 确保 initial_count 小于 target_count
        initial_count = min(initial_count, target_count - 1)
            
        game = ThreeDimensionalReconstruction(target_count, initial_count)
        return game
        
    def generate_count_question(self, structure):
        """生成计数问题"""
        voxel_count = len(structure)
        voxel_positions = sorted(structure)  # 排序以保持一致的顺序
        
        question = (
            "This is a state in a 3D reconstruction game.\n\n"
            "Given:\n"
            "- A 3x3x3 grid structure containing voxels\n"
            "- A image containing the voxel structure and its target projections (possibly not the projections of the given structure)\n"
            "  (Note: The projections shown in the image are not relevant for this question)\n\n"
            "Game Rules:\n"
            "1. Grid Space: The game is played on a 3x3x3 cube grid.\n"
            "2. Coordinates: Position (x,y,z) ranges from 1 to 3, with (1,1,1) at front-left-bottom.\n"
            "3. Position Rule: Each position can contain at most one voxel.\n"
            "4. Connectivity: All voxels must be connected face-to-face.\n\n"
            "Question:\n"
            "How many voxels are there in the given structure?\n\n"
            "Please answer with a number."
        )
        
        answer = str(voxel_count)  # 转换为字符串以保持一致性
        options = None  # 填空题不需要选项
        
        # 详细的分析，列出所有体素位置
        position_list = ", ".join([f"({x},{y},{z})" for x,y,z in voxel_positions])
        analysis = f"The structure contains voxels at the following positions: {position_list}. By counting these positions, we can see there are {voxel_count} voxels in total. Therefore the answer is {answer}."
        
        return question, answer, options, analysis
        
    def generate_position_question(self, structure):
        """生成位置检查问题"""
        # 从已有的体素中随机选择一个作为正确答案
        if not structure:
            raise ValueError("Structure is empty, cannot generate position question")
        correct_pos = random.choice(list(structure))
        
        # 生成5个错误选项（不在structure中的坐标）
        all_positions = [(x,y,z) for x in range(1,4) for y in range(1,4) for z in range(1,4)]
        wrong_positions = [pos for pos in all_positions if pos not in structure]
        wrong_options = random.sample(wrong_positions, 5)
        
        # 合并所有选项并打乱顺序
        all_options = [f"({x},{y},{z})" for x,y,z in [correct_pos] + wrong_options]
        random.shuffle(all_options)
        
        # 找到正确答案的索引（从1开始）
        correct_index = all_options.index(f"({correct_pos[0]},{correct_pos[1]},{correct_pos[2]})") + 1
        
        question = (
            "This is a state in a 3D reconstruction game.\n\n"
            "Given:\n"
            "- A 3x3x3 grid structure containing voxels\n"
            "- A image containing the voxel structure and its target projections (possibly not the projections of the given structure)\n"
            "  (Note: The projections shown in the image are not relevant for this question)\n\n"
            "Game Rules:\n"
            "1. Grid Space: The game is played on a 3x3x3 cube grid.\n"
            "2. Coordinates: Position (x,y,z) ranges from 1 to 3, with (1,1,1) at front-left-bottom.\n"
            "3. Position Rule: Each position can contain at most one voxel.\n"
            "4. Connectivity: All voxels must be connected face-to-face.\n\n"
            f"Question:\n"
            f"Which of the following positions contains a voxel?\n\n"
            "Choose the correct position from the options below.\n"
            "Options:\n"
        )
        
        # 添加选项到问题字符串
        for i, option in enumerate(all_options, 1):
            question += f"{i}: {option}\n"
        
        answer = str(correct_index)
        
        # 生成分析
        analysis = f"Let's analyze each option:\n\n"
        for i, option in enumerate(all_options, 1):
            # 去掉括号并分割坐标
            x, y, z = map(int, option.strip('()').split(','))
            pos = (x,y,z)
            
            analysis += f"Option {i} - Position {option}:\n"
            if pos in structure:
                analysis += "- This position contains a voxel.\n"
                analysis += "- This is the correct answer.\n"
            else:
                analysis += "- This position is empty.\n"
            analysis += "\n"
            
        analysis += f"Therefore, the correct answer is option {correct_index}."
        
        return question, answer, all_options, analysis
        
    def generate_projection_question(self, current_structure, solution_structure, game):
        """生成投影检查问题"""
        # 获取solution的投影作为目标
        target_yz_proj, target_xz_proj = game.get_projections(solution_structure)
        # 获取当前结构的投影
        current_yz_proj, current_xz_proj = game.get_projections(current_structure)
        
        # 检查两个投影是否匹配
        yz_match = np.array_equal(current_yz_proj, target_yz_proj)
        xz_match = np.array_equal(current_xz_proj, target_xz_proj)
        
        # 根据匹配情况确定正确答案
        if not yz_match and not xz_match:
            correct_index = 1
        elif yz_match and not xz_match:
            correct_index = 2
        elif not yz_match and xz_match:
            correct_index = 3
        else:  # yz_match and xz_match
            correct_index = 4
            
        # 固定的4个选项
        all_options = [
            "Neither Y-Z projection nor X-Z projection matches the target",
            "Only Y-Z projection matches the target",
            "Only X-Z projection matches the target",
            "Both Y-Z and X-Z projections match the target"
        ]
        
        question = (
            "This is a state in a 3D reconstruction game.\n\n"
            "Given:\n"
            "- A 3x3x3 grid structure containing voxels\n"
            "- A image containing the voxel structure and its target projections (possibly not the projections of the given structure)\n\n"
            "Game Rules:\n"
            "1. Grid Space: The game is played on a 3x3x3 cube grid.\n"
            "2. Coordinates: Position (x,y,z) ranges from 1 to 3, with (1,1,1) at front-left-bottom.\n"
            "3. Position Rule: Each position can contain at most one voxel.\n"
            "4. Connectivity: All voxels must be connected face-to-face.\n"
            "5. Front View (Y-Z): Shows structure when viewed along the negative X-axis direction (front to back), with Y as horizontal axis and Z as vertical axis. Projection coordinates are in (y,z) format.\n"
            "6. Side View (X-Z): Shows structure when viewed along the positive Y-axis direction (left to right), with X as horizontal axis and Z as vertical axis. Projection coordinates are in (x,z) format.\n"
            "7. Projection Rule: A cell shows '1' if any voxel exists along that line of sight, and '0' if no voxel exists along that line.\n\n"
            "Question:\n"
            "How does the voxel structure's projections match with the target projections?\n\n"
            "Choose the correct description from the options below.\n"
            "Options:\n"
        )
        
        # 添加选项到问题字符串
        for i, option in enumerate(all_options, 1):
            question += f"{i}: {option}\n"
        
        answer = str(correct_index)
        
        # 找出每个投影方向上最靠近视角的方块
        # 对于Y-Z投影（从X轴负方向看），对于每个(y,z)位置，选择最大的x坐标
        visible_voxels_zy = {}  # (y,z) -> (x,y,z)
        for x, y, z in current_structure:
            if (y,z) not in visible_voxels_zy or x > visible_voxels_zy[(y,z)][0]:
                visible_voxels_zy[(y,z)] = (x,y,z)
                
        # 对于X-Z投影（从Y轴正方向看），对于每个(x,z)位置，选择最小的y坐标
        visible_voxels_xz = {}  # (x,z) -> (x,y,z)
        for x, y, z in current_structure:
            if (x,z) not in visible_voxels_xz or y < visible_voxels_xz[(x,z)][1]:
                visible_voxels_xz[(x,z)] = (x,y,z)
        
        # 生成投影的坐标形式，用于分析
        target_yz_positions = [(y+1,z+1) for y in range(3) for z in range(3) if target_yz_proj[y,z]]  # 注意：y在前，z在后
        target_xz_positions = [(x+1,z+1) for x in range(3) for z in range(3) if target_xz_proj[x,z]]  # 注意：x在前，z在后
        current_yz_positions = [(y+1,z+1) for y in range(3) for z in range(3) if current_yz_proj[y,z]]  # 注意：y在前，z在后
        current_xz_positions = [(x+1,z+1) for x in range(3) for z in range(3) if current_xz_proj[x,z]]  # 注意：x在前，z在后
        
        # 找出不匹配的位置
        yz_extra = [pos for pos in current_yz_positions if pos not in target_yz_positions]
        yz_missing = [pos for pos in target_yz_positions if pos not in current_yz_positions]
        xz_extra = [pos for pos in current_xz_positions if pos not in target_xz_positions]
        xz_missing = [pos for pos in target_xz_positions if pos not in current_xz_positions]
        
        # 生成分析
        analysis = "Let's analyze the projections:\n\n"
        
        # 分析Y-Z投影（从X轴负方向看）
        analysis += "1. Looking along the negative X-axis direction (Front View, using (y,z) coordinates):\n"
        if visible_voxels_zy:
            visible_voxels_list = sorted(visible_voxels_zy.values())
            analysis += f"   - We can see voxels at positions {visible_voxels_list}, forming a Y-Z projection of {sorted(current_yz_positions)}\n"
        else:
            analysis += "   - No voxels are visible in this view\n"
            
        if yz_match:
            analysis += "   - This matches the target Y-Z projection exactly\n"
        else:
            if yz_extra:
                analysis += f"   - Compared to the target, extra voxels appear at positions {sorted(yz_extra)}\n"
            if yz_missing:
                analysis += f"   - Compared to the target, voxels are missing at positions {sorted(yz_missing)}\n"
            analysis += "   - Therefore, the Y-Z projection does not match the target\n"
        analysis += "\n"
        
        # 分析X-Z投影（从Y轴正方向看）
        analysis += "2. Looking along the positive Y-axis direction (Side View, using (x,z) coordinates):\n"
        if visible_voxels_xz:
            visible_voxels_list = sorted(visible_voxels_xz.values())
            analysis += f"   - We can see voxels at positions {visible_voxels_list}, forming a X-Z projection of {sorted(current_xz_positions)}\n"
        else:
            analysis += "   - No voxels are visible in this view\n"
            
        if xz_match:
            analysis += "   - This matches the target X-Z projection exactly\n"
        else:
            if xz_extra:
                analysis += f"   - Compared to the target, extra voxels appear at positions {sorted(xz_extra)}\n"
            if xz_missing:
                analysis += f"   - Compared to the target, voxels are missing at positions {sorted(xz_missing)}\n"
            analysis += "   - Therefore, the X-Z projection does not match the target\n"
        analysis += "\n"
        
        # 总结
        analysis += f"Based on the above analysis, {'neither projection matches' if not yz_match and not xz_match else 'only Y-Z projection matches' if yz_match and not xz_match else 'only X-Z projection matches' if not yz_match and xz_match else 'both projections match'} the target.\n"
        analysis += f"Therefore, the correct answer is option {correct_index}."
        
        return question, answer, all_options, analysis

    def generate_state_info_question(self, structure, game_state, game, force_type=None):
        """生成StateInfo类型的问题（count/position/projection）"""
        # 使用指定的问题类型或随机选择
        question_type = force_type if force_type else random.choice(['count', 'position', 'projection'])
        
        if question_type == 'count':
            question, answer, options, analysis = self.generate_count_question(structure)
            question_id = 0
            qa_level = "Easy"
        elif question_type == 'position':
            question, answer, options, analysis = self.generate_position_question(structure)
            question_id = 1
            qa_level = "Easy"
        else:  # projection
            question, answer, options, analysis = self.generate_projection_question(
                structure, 
                game_state['complete_solution']['positions'],
                game
            )
            question_id = 2
            qa_level = "Medium"
            
        return {
            'question_type': question_type,
            'question_id': question_id,
            'qa_level': qa_level,
            'question': question,
            'answer': answer,
            'options': options if question_type in ['position', 'projection'] else None,  # position和projection类型需要options
            'analysis': analysis
        }

    def generate_action_outcome_question(self, current_structure, solution_structure, game):
        """生成ActionOutcome类型的问题"""
        # 计算可以添加的方块数量
        remaining = len(solution_structure) - len(current_structure)
        if remaining <= 0:
            raise ValueError("No remaining voxels available for addition")
            
        # 随机生成1到min(3,remaining)个新方块
        add_count = random.randint(1, min(3, remaining))
        _, new_voxels = game.generate_random_connected_voxels(add_count, respect_remaining=True)
        
        # 计算添加新方块后的结构
        combined_structure = current_structure + new_voxels
        
        # 获取添加新方块后的投影
        new_yz_proj, new_xz_proj = game.get_projections(combined_structure)
        
        # 随机选择检查哪个投影
        check_yz = random.choice([True, False])
        proj_name = "Y-Z" if check_yz else "X-Z"
        
        question = (
            "You are in the middle of a 3D reconstruction puzzle.\n"
            "The current structure has some initial voxels, and your goal is to complete it.\n\n"
            "Game Rules:\n"
            "1. Goal: Reconstruct a 3D structure by adding voxels to match given projections.\n"
            "2. Grid Space: The game is played on a 3x3x3 cube grid.\n"
            "3. Coordinates: Position (x,y,z) ranges from 1 to 3, with (1,1,1) at front-left-bottom.\n"
            "4. Position Rule: Each position can contain at most one voxel.\n"
            "5. Connectivity: All voxels must be connected face-to-face.\n"
            "6. Voxel Limit: You have a maximum of n additional voxels available.\n"
            "7. Placement Rule: New voxels can only be placed adjacent to existing ones.\n"
            "8. Front View (Y-Z): Shows structure when viewed along the negative X-axis direction (front to back), with Y as horizontal axis and Z as vertical axis. Projection coordinates are in (y,z) format.\n"
            "9. Side View (X-Z): Shows structure when viewed along the positive Y-axis direction (left to right), with X as horizontal axis and Z as vertical axis. Projection coordinates are in (x,z) format.\n"
            "10. Projection Rule: A cell shows '1' if any voxel exists along that line of sight, and '0' if no voxel exists along that line.\n\n"
            f"Action:\n"
            f"Add {len(new_voxels)} voxels at positions: {sorted(new_voxels)}\n\n"
            f"Question:\n"
            f"After adding these voxels, what will be the {proj_name} projection of the new structure?\n\n"
            "Answer Format:\n"
            "1. Write the answer as a list of three lists: [[row1], [row2], [row3]]\n"
            "2. Each row should contain three numbers (0 or 1)\n"
            "3. Rows are ordered from top to bottom of the projection\n"
            "4. Numbers in each row are ordered from left to right\n"
            "5. Use 1 to indicate presence of a voxel in the projection, 0 for empty space\n"
            "6. Example format: [[0, 1, 0], [1, 1, 0], [0, 1, 1]]\n\n"
        )
        
        # 准备答案
        if check_yz:
            # 找出每个投影方向上最靠近视角的方块（从X轴负方向看）
            visible_voxels_zy = {}  # (y,z) -> (x,y,z)
            for x, y, z in combined_structure:
                if (y,z) not in visible_voxels_zy or x > visible_voxels_zy[(y,z)][0]:
                    visible_voxels_zy[(y,z)] = (x,y,z)
                    
            # 生成答案（3x3矩阵形式，从下到上，从左到右）
            answer = str([
                [int(new_yz_proj.T[2,0]), int(new_yz_proj.T[2,1]), int(new_yz_proj.T[2,2])],  # z=3，y从1到3
                [int(new_yz_proj.T[1,0]), int(new_yz_proj.T[1,1]), int(new_yz_proj.T[1,2])],  # z=2，y从1到3
                [int(new_yz_proj.T[0,0]), int(new_yz_proj.T[0,1]), int(new_yz_proj.T[0,2])]   # z=1，y从1到3
            ])
            
            # 生成分析
            analysis = "Let's analyze the projection:\n\n"
            analysis += "Looking along the negative X-axis direction (Front View, using (y,z) coordinates):\n"
            if visible_voxels_zy:
                visible_voxels_list = sorted(visible_voxels_zy.values())
                # 生成投影坐标
                proj_positions = [(y,z) for x,y,z in visible_voxels_list]
                analysis += f"- We can see voxels at positions {visible_voxels_list}, which in Y-Z projection appear at positions {sorted(proj_positions)}\n"
                analysis += f"- This forms a Y-Z projection matrix (from top to bottom):\n"
                for z in range(3):
                    row = [int(new_yz_proj.T[2-z,y]) for y in range(3)]  # 从下到上，从左到右
                    analysis += f"  {row}\n"
            else:
                analysis += "- No voxels are visible in this view\n"
                analysis += "- This forms an empty projection matrix:\n"
                analysis += "  [0, 0, 0]\n  [0, 0, 0]\n  [0, 0, 0]\n"
                
            analysis += "\nTherefore, the answer is:\n"
            analysis += str([
                [int(new_yz_proj.T[2,0]), int(new_yz_proj.T[2,1]), int(new_yz_proj.T[2,2])],  # z=3，y从1到3
                [int(new_yz_proj.T[1,0]), int(new_yz_proj.T[1,1]), int(new_yz_proj.T[1,2])],  # z=2，y从1到3
                [int(new_yz_proj.T[0,0]), int(new_yz_proj.T[0,1]), int(new_yz_proj.T[0,2])]   # z=1，y从1到3
            ])
                
        else:  # check_xz
            # 找出每个投影方向上最靠近视角的方块（从Y轴正方向看）
            visible_voxels_xz = {}  # (x,z) -> (x,y,z)
            for x, y, z in combined_structure:
                if (x,z) not in visible_voxels_xz or y < visible_voxels_xz[(x,z)][1]:
                    visible_voxels_xz[(x,z)] = (x,y,z)
                    
            # 生成答案（3x3矩阵形式，从下到上，从左到右）
            answer = str([
                [int(new_xz_proj.T[2,0]), int(new_xz_proj.T[2,1]), int(new_xz_proj.T[2,2])],  # z=3，x从1到3
                [int(new_xz_proj.T[1,0]), int(new_xz_proj.T[1,1]), int(new_xz_proj.T[1,2])],  # z=2，x从1到3
                [int(new_xz_proj.T[0,0]), int(new_xz_proj.T[0,1]), int(new_xz_proj.T[0,2])]   # z=1，x从1到3
            ])
            
            # 生成分析
            analysis = "Let's analyze the projection:\n\n"
            analysis += "Looking along the positive Y-axis direction (Side View, using (x,z) coordinates):\n"
            if visible_voxels_xz:
                visible_voxels_list = sorted(visible_voxels_xz.values())
                # 生成投影坐标
                proj_positions = [(x,z) for x,y,z in visible_voxels_list]
                analysis += f"- We can see voxels at positions {visible_voxels_list}, which in X-Z projection appear at positions {sorted(proj_positions)}\n"
                analysis += f"- This forms a X-Z projection matrix (from top to bottom):\n"
                for z in range(3):
                    row = [int(new_xz_proj.T[2-z,x]) for x in range(3)]  # 从下到上，从左到右
                    analysis += f"  {row}\n"
            else:
                analysis += "- No voxels are visible in this view\n"
                analysis += "- This forms an empty projection matrix:\n"
                analysis += "  [0, 0, 0]\n  [0, 0, 0]\n  [0, 0, 0]\n"
                
            analysis += "\nTherefore, the answer is:\n"
            analysis += str([
                [int(new_xz_proj.T[2,0]), int(new_xz_proj.T[2,1]), int(new_xz_proj.T[2,2])],  # z=3，x从1到3
                [int(new_xz_proj.T[1,0]), int(new_xz_proj.T[1,1]), int(new_xz_proj.T[1,2])],  # z=2，x从1到3
                [int(new_xz_proj.T[0,0]), int(new_xz_proj.T[0,1]), int(new_xz_proj.T[0,2])]   # z=1，x从1到3
            ])
        
        return {
            'question_type': 'action_outcome',
            'question_id': 3,
            'qa_level': 'Medium',
            'question': question,
            'answer': answer,
            'options': None,
            'analysis': analysis
        }
        
    def generate_transition_path_question(self, game_state, game):
        """生成TransitionPath类型的选择题"""
        def is_valid_solution(test_voxels, current_voxels, target_voxels, remaining, check_both, check_zy):
            """验证一个选项是否是正确答案
            
            Args:
                test_voxels: 要添加的方块列表
                current_voxels: 当前结构的方块列表
                target_voxels: 目标结构的方块列表
                remaining: 剩余可用方块数量
                check_both: 是否检查两个投影
                check_zy: 如果不检查两个投影，是否检查Y-Z投影（False则检查X-Z投影）
                
            Returns:
                bool: 是否是正确答案
            """
            # 1. 检查方块数量是否超过限制
            if len(test_voxels) > remaining:
                return False
            
            # 2. 组合当前结构和新增体素
            test_structure = current_voxels + test_voxels
            
            # 3. 检查是否连通
            test_structure_set = set(tuple(pos) if isinstance(pos, list) else pos for pos in test_structure)
            if not game._is_connected(test_structure_set):
                return False
            
            # 4. 检查投影是否匹配
            test_yz_proj, test_xz_proj = game.get_projections(test_structure)
            target_yz_proj, target_xz_proj = game.get_projections(target_voxels)
            
            if check_both:
                return (np.array_equal(test_yz_proj, target_yz_proj) and 
                       np.array_equal(test_xz_proj, target_xz_proj))
            elif check_zy:
                return np.array_equal(test_yz_proj, target_yz_proj)
            else:  # check_xz
                return np.array_equal(test_xz_proj, target_xz_proj)
        
        # 随机选择检查一个投影或两个投影
        check_both = random.choice([True, False])
        proj_type = "both target projections" if check_both else random.choice(["Y-Z", "X-Z"]) + " target projection"
        
        # 如果不是检查两个投影，确定是检查哪一个
        check_zy = not check_both and "Y-Z" in proj_type
        
        question = (
            "You are in the middle of a 3D reconstruction puzzle.\n"
            "The current structure has some initial voxels, and your goal is to complete it as the game rules.\n\n"
            "Game Rules:\n"
            "1. Goal: Reconstruct a 3D structure by adding voxels to match given projections.\n"
            "2. Grid Space: The game is played on a 3x3x3 cube grid.\n"
            "3. Coordinates: Position (x,y,z) ranges from 1 to 3, with (1,1,1) at front-left-bottom.\n"
            "4. Position Rule: Each position can contain at most one voxel.\n"
            "5. Connectivity: All voxels must be connected face-to-face.\n"
            "6. Voxel Limit: You have a maximum of n additional voxels available.\n"
            "7. Placement Rule: New voxels can only be placed adjacent to existing ones.\n"
            "8. Front View (Y-Z): Shows structure when viewed along the negative X-axis direction (front to back), with Y as horizontal axis and Z as vertical axis. Projection coordinates are in (y,z) format.\n"
            "9. Side View (X-Z): Shows structure when viewed along the positive Y-axis direction (left to right), with X as horizontal axis and Z as vertical axis. Projection coordinates are in (x,z) format.\n"
            "10. Projection Rule: A cell shows '1' if any voxel exists along that line of sight, and '0' if no voxel exists along that line.\n"
            f"Question:\n"
            f"Which sequence of voxel additions will make the structure match the {proj_type}?\n"
            "Choose the correct sequence from the options below.\n\n"
            "Options:\n"
        )
        
        # 生成选项
        current_voxels = game_state['current_state']['positions']
        minimal_addition = game_state['minimal_addition']['positions']
        target_voxels = game_state['complete_solution']['positions']
        remaining = len(target_voxels) - len(current_voxels)
        
        # 正确选项
        correct_option = f"Add voxels at positions: {sorted(minimal_addition)}"
        
        # 生成错误选项
        wrong_options = []
        used_options = {correct_option}  # 使用set来跟踪已使用的选项
        
        # 定义最大尝试次数
        MAX_ATTEMPTS = 50  # 每个选项的最大尝试次数
        MAX_TOTAL_ATTEMPTS = 200  # 总的最大尝试次数
        total_attempts = 0
        
        # 1. 先生成2个过多的方块（超出remaining的限制）
        extra_count = 0
        attempts = 0
        
        while extra_count < 2 and attempts < MAX_ATTEMPTS and total_attempts < MAX_TOTAL_ATTEMPTS:
            # 随机选择一个超出限制的数量，但不超过27（3x3x3空间）
            extra_count_range = min(27 - len(current_voxels), remaining + 10)
            target_count = remaining + random.randint(1, extra_count_range)
            _, extra_voxels = game.generate_random_connected_voxels(target_count)
            option = f"Add voxels at positions: {sorted(extra_voxels)}"
            
            if option not in used_options and not is_valid_solution(extra_voxels, current_voxels, target_voxels, remaining, check_both, check_zy):
                wrong_options.append(option)
                used_options.add(option)
                extra_count += 1
            attempts += 1
            total_attempts += 1
            
        # 2. 生成3个不连通的路径
        disconnected_count = 0
        attempts = 0
        
        while disconnected_count < 3 and attempts < MAX_ATTEMPTS and total_attempts < MAX_TOTAL_ATTEMPTS:
            disconnected_voxels = []
            all_positions = [(x,y,z) for x in range(1,4) for y in range(1,4) for z in range(1,4)]
            available = [pos for pos in all_positions if pos not in current_voxels]
            target_count = random.randint(1, remaining)
            
            inner_attempts = 0
            MAX_INNER_ATTEMPTS = 20
            while len(disconnected_voxels) < target_count and inner_attempts < MAX_INNER_ATTEMPTS:
                if not available:
                    break
                pos = random.choice(available)
                disconnected_voxels.append(pos)
                available.remove(pos)
                inner_attempts += 1
                
            option = f"Add voxels at positions: {sorted(disconnected_voxels)}"
            
            if option not in used_options and not is_valid_solution(disconnected_voxels, current_voxels, target_voxels, remaining, check_both, check_zy):
                wrong_options.append(option)
                used_options.add(option)
                disconnected_count += 1
            attempts += 1
            total_attempts += 1
            
        # 3. 生成2个不满足投影的路径
        invalid_count = 0
        attempts = 0
        
        while invalid_count < 2 and attempts < MAX_ATTEMPTS and total_attempts < MAX_TOTAL_ATTEMPTS:
            target_count = random.randint(1, remaining)
            _, test_voxels = game.generate_random_connected_voxels(target_count)
            option = f"Add voxels at positions: {sorted(test_voxels)}"
            
            if option not in used_options and not is_valid_solution(test_voxels, current_voxels, target_voxels, remaining, check_both, check_zy):
                wrong_options.append(option)
                used_options.add(option)
                invalid_count += 1
            attempts += 1
            total_attempts += 1
            
        # 如果无法生成足够的不重复错误选项，生成一些随机的错误选项
        attempts = 0
        
        while len(wrong_options) < 7:  # 需要7个错误选项
            # 如果尝试次数过多，直接生成超出限制的选项
            extra_count_range = min(27 - len(current_voxels), remaining + 10)
            target_count = remaining + random.randint(1, extra_count_range)
                
            # 生成随机连通结构
            _, random_voxels = game.generate_random_connected_voxels(target_count)
            option = f"Add voxels at positions: {sorted(random_voxels)}"
            
            if option not in used_options and not is_valid_solution(random_voxels, current_voxels, target_voxels, remaining, check_both, check_zy):
                wrong_options.append(option)
                used_options.add(option)
            
            attempts += 1
            
            # 如果尝试次数过多，直接使用不连通的路径补充
            if attempts >= MAX_ATTEMPTS * 2:
                while len(wrong_options) < 7:
                    disconnected_voxels = []
                    all_positions = [(x,y,z) for x in range(1,4) for y in range(1,4) for z in range(1,4)]
                    available = [pos for pos in all_positions if pos not in current_voxels]
                    target_count = random.randint(1, remaining)
                    
                    for _ in range(target_count):
                        if not available:
                            break
                        pos = random.choice(available)
                        disconnected_voxels.append(pos)
                        available.remove(pos)
                    
                    option = f"Add voxels at positions: {sorted(disconnected_voxels)}"
                    if option not in used_options:
                        wrong_options.append(option)
                        used_options.add(option)
                break
        
        # 如果无法生成足够的错误选项，抛出异常
        if len(wrong_options) < 7:
            raise ValueError(f"Unable to generate enough wrong options: only generated {len(wrong_options)}")
            
        # 合并所有选项并打乱顺序
        all_options = [correct_option] + wrong_options
        random.shuffle(all_options)
        
        # 添加选项到问题字符串
        for i, option in enumerate(all_options, 1):
            question += f"{i}: {option}\n"
            
        # 找到正确答案的索引（从1开始）
        correct_index = all_options.index(correct_option) + 1
        
        # 生成分析
        analysis = (
            f"Let's analyze each option:\n\n"
            f"Current structure: {sorted(current_voxels)}\n\n"
            # f"Target structure: {sorted(target_voxels)}\n\n"
        )
        
        for i, option in enumerate(all_options, 1):
            voxels_str = option.split(": ")[1]
            voxels = eval(voxels_str)  # 将字符串转换回列表
            
            # 检查是否连通
            test_structure = current_voxels + voxels
            is_connected = game._is_connected(set(test_structure))
            
            # 检查投影是否匹配
            yz_proj, xz_proj = game.get_projections(test_structure)
            target_yz, target_xz = game.get_projections(target_voxels)
            yz_match = np.array_equal(yz_proj, target_yz)
            xz_match = np.array_equal(xz_proj, target_xz)
            
            analysis += f"Option {i}:\n"
            if not is_connected:
                analysis += "- The added voxels are not all connected to the existing structure\n"
            else:
                analysis += "- The added voxels maintain connectivity\n"
                
            if check_both:
                if not (yz_match and xz_match):
                    analysis += "- Does not match both target projections\n"
                else:
                    analysis += "- Matches both target projections\n"
            else:
                if "Y-Z" in proj_type:
                    if not yz_match:
                        analysis += "- Does not match the Y-Z target projection\n"
                    else:
                        analysis += "- Matches the Y-Z target projection\n"
                else:
                    if not xz_match:
                        analysis += "- Does not match the X-Z target projection\n"
                    else:
                        analysis += "- Matches the X-Z target projection\n"
                        
            if len(voxels) > remaining:
                analysis += f"- Uses {len(voxels)} voxels, which exceeds the remaining limit of {remaining}\n"
            else:
                analysis += f"- Uses {len(voxels)} voxels, which is within the limit of {remaining}\n"
                
            analysis += "\n"
            
        analysis += f"Therefore, the correct answer is option {correct_index}."
        
        return {
            'question_type': 'transition_path',
            'question_id': 4,
            'question': question,
            'options': all_options,
            'answer': str(correct_index),
            'analysis': analysis
        }
        
    def generate_strategy_optimization_question(self, game_state, game):
        """生成StrategyOptimization类型的填空题"""
        current_voxels = game_state['current_state']['positions']
        target_voxels = game_state['complete_solution']['positions']
        minimal_addition = game_state['minimal_addition']['positions']
        
        question = (
            "You are in the middle of a 3D reconstruction puzzle.\n"
            "The current structure has some initial voxels, and your goal is to complete it as the game rules.\n\n"
            "Game Rules:\n"
            "1. Goal: Reconstruct a 3D structure by adding voxels to match given projections.\n"
            "2. Grid Space: The game is played on a 3x3x3 cube grid.\n"
            "3. Coordinates: Position (x,y,z) ranges from 1 to 3, with (1,1,1) at front-left-bottom.\n"
            "4. Position Rule: Each position can contain at most one voxel.\n"
            "5. Connectivity: All voxels must be connected face-to-face.\n"
            "6. Voxel Limit: You have a maximum of n additional voxels available.\n"
            "7. Placement Rule: New voxels can only be placed adjacent to existing ones.\n"
            "8. Front View (Y-Z): Shows structure when viewed along the negative X-axis direction (front to back), with Y as horizontal axis and Z as vertical axis. Projection coordinates are in (y,z) format.\n"
            "9. Side View (X-Z): Shows structure when viewed along the positive Y-axis direction (left to right), with X as horizontal axis and Z as vertical axis. Projection coordinates are in (x,z) format.\n"
            "10. Projection Rule: A cell shows '1' if any voxel exists along that line of sight, and '0' if no voxel exists along that line.\n"
            "11. Victory: Match both projections using available voxels.\n\n"
            "Question:\n"
            "What is the minimum number of voxels needed to add to the current structure\n"
            "to make it match both target projections?\n\n"
            "Please answer with a number."
        )
        
        answer = str(len(minimal_addition))
        
        # 生成分析过程
        analysis = (
            f"Let's solve this optimization problem through systematic reasoning:\n\n"
            
            f"1. Basic Information:\n"
            f"   - Current structure: {len(current_voxels)} voxels at positions {sorted(current_voxels)}\n"
            f"   - Remaining available voxels: {len(target_voxels) - len(current_voxels)}\n\n"
            
            f"2. Analysis of Y-Z Projection (Front View):\n"
            f"   a) Current Y-Z projection:\n"
            f"      {game.get_projections(current_voxels)[0].T.tolist()[2]} (top)\n"
            f"      {game.get_projections(current_voxels)[0].T.tolist()[1]} (middle)\n"
            f"      {game.get_projections(current_voxels)[0].T.tolist()[0]} (bottom)\n"
            f"   b) Target Y-Z projection:\n"
            f"      {game.get_projections(target_voxels)[0].T.tolist()[2]} (top)\n"
            f"      {game.get_projections(target_voxels)[0].T.tolist()[1]} (middle)\n"
            f"      {game.get_projections(target_voxels)[0].T.tolist()[0]} (bottom)\n"
            f"   c) Candidate positions from Y-Z view:\n"
            f"      {', '.join([f'(?, {y+1}, {z+1})' for y in range(3) for z in range(3) if game.get_projections(target_voxels)[0][y,z] == 1 and game.get_projections(current_voxels)[0][y,z] == 0])}\n"
            f"      where ? can be any value from 1 to 3 for x-coordinate\n"
            f"   d) Note: At positions where projection already shows 1, we can add more voxels without affecting the projection.\n"
            f"      For example, if (2, y0, z0) exists (where y0 and z0 are specific fixed values), we can add (1, y0, z0) or (3, y0, z0) at the same projection position.\n\n"
            
            f"3. Analysis of X-Z Projection (Side View):\n"
            f"   a) Current X-Z projection:\n"
            f"      {game.get_projections(current_voxels)[1].T.tolist()[2]} (top)\n"
            f"      {game.get_projections(current_voxels)[1].T.tolist()[1]} (middle)\n"
            f"      {game.get_projections(current_voxels)[1].T.tolist()[0]} (bottom)\n"
            f"   b) Target X-Z projection:\n"
            f"      {game.get_projections(target_voxels)[1].T.tolist()[2]} (top)\n"
            f"      {game.get_projections(target_voxels)[1].T.tolist()[1]} (middle)\n"
            f"      {game.get_projections(target_voxels)[1].T.tolist()[0]} (bottom)\n"
            f"   c) Candidate positions from X-Z view:\n"
            f"      {', '.join([f'({x+1}, ?, {z+1})' for x in range(3) for z in range(3) if game.get_projections(target_voxels)[1][x,z] == 1 and game.get_projections(current_voxels)[1][x,z] == 0])}\n"
            f"      where ? can be any value from 1 to 3 for y-coordinate\n"
            f"   d) Note: At positions where projection already shows 1, we can add more voxels without affecting the projection.\n"
            f"      For example, if (x0, 2, z0) exists (where x0 and z0 are specific fixed values), we can add (x0, 1, z0) or (x0, 3, z0) at the same projection position.\n\n"
            
            f"4. Finding Required Positions:\n"
            f"   By matching candidates from both projections:\n"
            f"   - When (?, y, z) from Y-Z view matches (x, ?, z) from X-Z view, position (x, y, z) can be filled.\n"
            f"   - Example: if we have (?, 2, 3) and (1, ?, 3), then (1, 2, 3) is required\n"
            f"   - To ensure connectivity, we can add voxels at positions where projections already show 1\n"
            f"     * This strategy is optimal because it doesn't create new projections\n"
            f"     * Use these positions as 'bridges' to connect required positions\n"
            f"   Required positions from projection matching: {sorted(set(minimal_addition) - set(current_voxels))}\n\n"
            
            f"5. Connectivity Analysis and Completion:\n"
            f"   a) Checking connectivity of required positions:\n"
            f"      - Required positions must connect to existing structure\n"
            f"      - Required positions must connect to each other\n"
            f"   b) Adding connecting voxels if needed:\n"
            f"      - Additional voxels must not violate projection constraints\n"
            f"      - Prioritize positions that satisfy multiple connectivity needs\n"
            f"   c) Final set of positions to add: {sorted(minimal_addition)}\n\n"
            
            f"6. Verifying Optimality:\n"
            f"   After adding {len(minimal_addition)} voxels:\n"
            f"   - Projection verification:\n"
            f"     * Y-Z projection matches:\n"
            f"       {game.get_projections(target_voxels)[0].T.tolist()[2]} (top)\n"
            f"       {game.get_projections(target_voxels)[0].T.tolist()[1]} (middle)\n" 
            f"       {game.get_projections(target_voxels)[0].T.tolist()[0]} (bottom)\n"
            f"     * X-Z projection matches:\n"
            f"       {game.get_projections(target_voxels)[1].T.tolist()[2]} (top)\n"
            f"       {game.get_projections(target_voxels)[1].T.tolist()[1]} (middle)\n"
            f"       {game.get_projections(target_voxels)[1].T.tolist()[0]} (bottom)\n"
            f"   - Connectivity verification: All voxels are face-connected\n"
            f"   - Minimality verification:\n"
            f"     * All required positions are included\n"
            f"     * Minimum number of connecting voxels added\n"
            f"     * Cannot satisfy all constraints with fewer voxels\n\n"
            
            f"Therefore, the minimum number of voxels needed to complete the reconstruction is {len(minimal_addition)}."
        )
        
        return {
            'question_type': 'strategy_optimization',
            'question_id': 5,
            'question': question,
            'answer': answer,
            'analysis': analysis
        }
        
    def generate_question(self, qa_types=None, qa_count=None, plot_level=None, force_state_info_type=None):
        """
        生成一个问题

        Args:
            qa_types (list): 问题类型列表
            qa_count (int): 问题编号
            plot_level (str): 难度级别 'Easy', 'Medium', 'Hard'
            force_state_info_type (str): 强制生成特定类型的StateInfo问题
        """
        if qa_count is not None:
            self.qa_count = qa_count
        else:
            self.qa_count += 1
            
        # 设置默认的问题类型
        if qa_types is None:
            qa_types = ['count', 'position', 'projection', 'action_outcome', 
                       'transition_path', 'strategy_optimization']
            
        # 随机选择问题类型
        question_type = random.choice(qa_types)
        
        # 生成游戏实例
        game = self.generate_game_instance(plot_level)
        game_state = game.get_game_state()
        target_count = game_state['target_count']
        
        # 对于action_outcome和strategy_optimization类型，只使用current状态
        if question_type in ['action_outcome', 'strategy_optimization', 'transition_path']:
            structure = game_state['current_state']['positions']
        else:
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
        base_name = f"reconstruction_{self.qa_count:05d}"
        image_path = f"images/{base_name}.png"
        state_path = f"states/{base_name}.json"
        
        # 保存可视化
        if question_type in ['action_outcome', 'strategy_optimization', 'transition_path'] or structure_type == 'current':
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
            
        # 生成问题
        if question_type == 'action_outcome':
            question_result = self.generate_action_outcome_question(
                game_state['current_state']['positions'],
                game_state['complete_solution']['positions'],
                game
            )
            question_id = 3
            qa_type = 'ActionOutcome'
        elif question_type == 'transition_path':
            question_result = self.generate_transition_path_question(game_state, game)
            question_id = 4
            qa_type = 'TransitionPath'
        elif question_type == 'strategy_optimization':
            question_result = self.generate_strategy_optimization_question(game_state, game)
            question_id = 5
            qa_type = 'StrategyOptimization'
        else:  # StateInfo类型
            question_result = self.generate_state_info_question(structure, game_state, game, force_type=question_type)
            question_id = question_result['question_id']
            qa_type = 'StateInfo'
            
        # 设置问题难度
        if question_type in ['strategy_optimization', 'transition_path']:
            qa_level = "Hard"
        elif question_type == 'action_outcome':
            qa_level = "Medium"
        else:
            qa_level = question_result['qa_level']
        
        # 创建数据集条目
        entry = OrderedDict([
            ("data_id", base_name),
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
            ("plot_level", self.get_plot_level(target_count)),
            ("qa_level", qa_level),
            ("question", question_result['question']),
            ("answer", question_result['answer']),
            ("analysis", question_result['analysis'])
        ])
        
        # 如果是position、projection或transition_path类型的问题，添加options字段
        if question_type in ['position', 'projection', 'transition_path']:
            entry["options"] = question_result['options']
        
        self.dataset.append(entry)
        return entry

    def _generate_single_question(self, task):
        """单个问题生成函数（用于多进程）"""
        _, qa_type, qa_count, plot_level = task
        # 如果是StateInfo类型的子类型，直接使用该类型
        if qa_type in ['count', 'position', 'projection']:
            return self.generate_question(qa_types=[qa_type], qa_count=qa_count, plot_level=plot_level)
        else:
            return self.generate_question(qa_types=[qa_type], qa_count=qa_count, plot_level=plot_level)

    def generate_all_datasets(self, total_samples=100, type_ratios=None, plot_level_ratios=None):
        """
        生成所有类型的问题数据集

        Args:
            total_samples (int): 要生成的总样本数量
            type_ratios (dict): 可选的问题类型比例，如 {'count': 0.2, 'position': 0.2}
            plot_level_ratios (list): 可选的难度比例，如 [0.2, 0.2, 0.6] 分别对应 Easy, Medium, Hard
        """
        # 重置数据集
        self.dataset = []
        
        # 所有问题类型（将StateInfo拆分为三个子类型，并调整顺序）
        question_types = ['count', 'position', 'projection', 'action_outcome', 
                         'transition_path', 'strategy_optimization']  # 调整顺序
        
        # 计算每种类型的样本数量
        type_samples = {}
        if type_ratios is None:
            # 如果没有指定比例，平均分配
            base_count = total_samples // len(question_types)
            extra = total_samples % len(question_types)
            
            for i, qt in enumerate(question_types):
                type_samples[qt] = base_count + (1 if i < extra else 0)
        else:
            # 使用指定的比例精确计算
            remaining = total_samples
            for qt in question_types[:-1]:  # 除了最后一个类型
                if qt in type_ratios:
                    count = int(total_samples * type_ratios[qt])
                    type_samples[qt] = count
                    remaining -= count
                else:
                    type_samples[qt] = 0
            
            # 最后一个类型分配剩余的数量
            last_type = question_types[-1]
            type_samples[last_type] = remaining if last_type in type_ratios else 0
        
        print(f"\n开始生成数据集，总样本数：{total_samples}")
        print("各类型问题数量：")
        for qt, count in type_samples.items():
            print(f"- {qt}: {count}")
        print()
        
        # 创建输出目录
        os.makedirs("reconstruction_dataset/images", exist_ok=True)
        os.makedirs("reconstruction_dataset/states", exist_ok=True)
        
        # 创建所有任务
        all_tasks = []
        current_count = 1
        
        # 为每个问题类型创建任务，根据难度比例分配
        for qt in question_types:
            if qt in type_samples and type_samples[qt] > 0:
                count = type_samples[qt]
                
                # 确定这个类型的难度分布
                if plot_level_ratios is not None:
                    # 使用指定的难度比例
                    ratios = plot_level_ratios
                else:
                    # 默认平均分配
                    ratios = [1/3, 1/3, 1/3]  # Easy, Medium, Hard
                
                # 计算每个难度级别的问题数量
                level_counts = {}
                remaining_count = count
                
                # 按比例分配
                for i, level in enumerate(['Easy', 'Medium']):  # 先分配Easy和Medium
                    level_count = int(count * ratios[i])
                    level_counts[level] = level_count
                    remaining_count -= level_count
                level_counts['Hard'] = remaining_count  # 剩余的分配给Hard
                
                # 为每个难度级别创建对应数量的任务
                for level, level_count in level_counts.items():
                    for _ in range(level_count):
                        all_tasks.append(('task', qt, current_count, level))
                        current_count += 1
        
        # 使用单个进度条处理所有任务
        print("生成数据集中...")
        with mp.Pool() as pool:
            results = list(tqdm(
                pool.imap(self._generate_single_question, all_tasks),
                total=len(all_tasks),
                desc="生成进度"
            ))
            self.dataset.extend([r for r in results if r is not None])
        
        # 保存数据集
        print("\n保存数据集...")
        with open("reconstruction_dataset/data.json", "w") as f:
            json.dump(self.dataset, f, indent=2)
        
        print(f"\n数据集生成完成！共生成 {len(self.dataset)} 个问题")
        
        # 打印每种类型和难度的问题数量统计
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
            print(f"- {display_name:<{max_type_len}}: {stats['Easy']:>1}, {stats['Medium']:>1}, {stats['Hard']:>1} (total: {total:>1})")
        
        print(f"\n文件保存在 reconstruction_dataset/ 目录下：")
        print("- data.json          （数据集）")
        print("- images/            （可视化图片）")
        print("- states/            （状态文件）")

if __name__ == "__main__":
    generator = ThreeDReconstructionQAGenerator()
    
    # 使用默认设置生成所有类型的问题
    generator.generate_all_datasets(6)  # 增加样本数以便看到所有类型的问题
    
    # 示例：使用自定义比例生成问题
    # custom_ratios = {
    #     'count': 0.2,
    #     'position': 0.2,
    #     'projection': 0.2,
    #     'action_outcome': 0.2,
    #     'strategy_optimization': 0.1,
    #     'transition_path': 0.1
    # }
    # generator.generate_all_datasets(200, custom_ratios)
