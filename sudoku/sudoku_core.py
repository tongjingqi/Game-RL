# sudoku_core.py
import random
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple, Optional
import copy

class SudokuSolver:
    def __init__(self, size: int):
        self.size = size
        self.box_size = int(size ** 0.5)
        self.steps = []
        self.step_id = 0
        
    def is_valid(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        # Check row
        if num in board[row]:
            return False
            
        # Check column
        if num in [board[i][col] for i in range(self.size)]:
            return False
            
        # Check box
        box_row, box_col = self.box_size * (row // self.box_size), self.box_size * (col // self.box_size)
        for i in range(box_row, box_row + self.box_size):
            for j in range(box_col, box_col + self.box_size):
                if board[i][j] == num:
                    return False
        return True
        
    def find_empty(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == 0:
                    return (i, j)
        return None
        
    def get_valid_numbers(self, board: List[List[int]], row: int, col: int) -> List[int]:
        valid_nums = []
        for num in range(1, self.size + 1):
            if self.is_valid(board, row, col, num):
                valid_nums.append(num)
        return valid_nums
    
    def solve_base(self, board: List[List[int]], record_steps: bool = True) -> Dict:
        if record_steps:
            self.steps = []
            self.step_id = 0
            
        result = {
            "solution": None,
            "unique": True,
            "steps": self.steps,
            "success": False
        }
        
        empty = self.find_empty(board)
        if not empty:
            result["solution"] = [row[:] for row in board]
            result["success"] = True
            return result
            
        row, col = empty
        valid_nums = self.get_valid_numbers(board, row, col)
        
        if record_steps:
            self.steps.append({
                "step_id": self.step_id,
                "position": [row, col],
                "action": "analyzing",
                "remaining_options": valid_nums,
                "reason": f"Analyzing position ({row+1}, {col+1})"
            })
            self.step_id += 1
            
        for num in valid_nums:
            if record_steps:
                self.steps.append({
                    "step_id": self.step_id,
                    "position": [row, col],
                    "action": "try",
                    "value": num,
                    "reason": f"Trying {num} at position ({row+1}, {col+1})"
                })
                self.step_id += 1
                
            board[row][col] = num
            solve_result = self.solve_base(board, record_steps)
            
            if solve_result["success"]:
                if result["solution"] is not None:
                    result["unique"] = False
                    if record_steps:
                        self.steps.append({
                            "step_id": self.step_id,
                            "action": "multiple_solutions",
                            "reason": "Found multiple solutions"
                        })
                    return result
                result = solve_result
                
            board[row][col] = 0
            if record_steps:
                self.steps.append({
                    "step_id": self.step_id,
                    "position": [row, col],
                    "action": "backtrack",
                    "value": num,
                    "reason": f"Backtracking from {num} at ({row+1}, {col+1})"
                })
                self.step_id += 1
                
        return result
    
    def solve(self, board: List[List[int]], record_steps: bool = True) -> Dict:
        if record_steps:
            self.steps = []
            self.step_id = 0
            
        result = {
            "solution": None,
            "unique": True,
            "steps": self.steps,
            "success": False
        }
        
        def solve_recursive(board: List[List[int]]) -> bool:
            empty = self.find_empty(board)
            if not empty:
                result["solution"] = [row[:] for row in board]
                result["success"] = True
                return True
                
            row, col = empty
            valid_nums = self.get_valid_numbers(board, row, col)
            
            if record_steps:
                self.steps.append({
                    "step_id": self.step_id,
                    "position": [row, col],
                    "action": "analyzing",
                    "remaining_options": valid_nums.copy(),
                    "reason": f"Analyzing position ({row+1}, {col+1})"
                })
                self.step_id += 1
            
            for num in valid_nums:
                if record_steps:
                    self.steps.append({
                        "step_id": self.step_id,
                        "position": [row, col],
                        "action": "try",
                        "value": num,
                        "reason": f"Trying {num} at position ({row+1}, {col+1})"
                    })
                    self.step_id += 1
                
                board[row][col] = num
                
                if solve_recursive(board):
                    # 检查是否已有解
                    if result["solution"] is not None:
                        # 比较当前解与已存解是否相同
                        current_solution = [row[:] for row in board]
                        if any(current_solution[i][j] != result["solution"][i][j] 
                            for i in range(len(board)) 
                            for j in range(len(board))):
                            result["unique"] = False
                            if record_steps:
                                self.steps.append({
                                    "step_id": self.step_id,
                                    "action": "multiple_solutions",
                                    "reason": "Found multiple solutions"
                                })
                                self.step_id += 1
                            return True
                    return True
                
                board[row][col] = 0
                if record_steps:
                    self.steps.append({
                        "step_id": self.step_id,
                        "position": [row, col],
                        "action": "backtrack",
                        "value": num,
                        "reason": f"Backtracking from {num} at ({row+1}, {col+1})"
                    })
                    self.step_id += 1
            
            return False
        
        # 直接使用输入的棋盘，而不是创建副本
        solve_recursive(board)
        return result

class SudokuGenerator:
    def __init__(self, size: int):
        self.size = size
        self.solver = SudokuSolver(size)
        
    def generate_solved_board(self) -> List[List[int]]:
        board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        nums = list(range(1, self.size + 1))
        
        # Fill diagonal boxes
        for i in range(0, self.size, self.solver.box_size):
            box_nums = nums.copy()
            random.shuffle(box_nums)
            for r in range(i, i + self.solver.box_size):
                for c in range(i, i + self.solver.box_size):
                    board[r][c] = box_nums.pop() 
                    
        # Solve the rest
        result = self.solver.solve_base(board, record_steps=False)
        # 检查是否成功找到解
        if not result or not result.get('solution'):
            # 如果没有找到解，重新生成
            print("Failed to generate a valid board, retrying...")
            return self.generate_solved_board()

        solve_board = result['solution']

        puzzle = [row[:] for row in solve_board]

        # 验证并显示结果
        final_empty = set((i, j) for i in range(self.size) 
                        for j in range(self.size) if puzzle[i][j] == 0)
        
        print(f"Actual empty cells: {len(final_empty)}")


        return solve_board
        
    def generate_puzzle(self, difficulty: str) -> Tuple[List[List[int]], List[List[int]]]:
        difficulties = {
            "easy": 0.1,
            "medium": 0.2,
            "hard": 0.3,
            "easy_4": 0.4,
            "hard_4": 0.5
        }
        
        difficulty = difficulty.lower()
        if difficulty not in difficulties:
            raise ValueError(f"Invalid difficulty: {difficulty}")
        
        # 生成完整解答
        solved_board = self.generate_solved_board()
        puzzle = [row[:] for row in solved_board]
        
        # 计算目标空格数
        total_cells = self.size * self.size
        target_empty = int(total_cells * difficulties[difficulty])
        
        # 用集合记录已经挖空的位置
        empty_cells = set()
        attempted_cells = set()
        
        while len(empty_cells) < target_empty and len(attempted_cells) < total_cells:
            # 找出还未尝试过的格子
            available_cells = [(i, j) for i in range(self.size) 
                            for j in range(self.size) 
                            if (i, j) not in attempted_cells 
                            and puzzle[i][j] != 0]  # 确保只选择非空格子
            
            if not available_cells:
                break
            
            # 随机选择一个格子
            row, col = random.choice(available_cells)
            attempted_cells.add((row, col))
            
            # 保存原始数字并尝试挖空
            temp = puzzle[row][col]
            puzzle[row][col] = 0
            
            # 检查是否保持唯一解
            board_copy = [row[:] for row in puzzle]
            result = self.solver.solve(board_copy, record_steps=False)
            
            if result.get("unique", False):
                empty_cells.add((row, col))
                print(f"Successfully emptied cell ({row+1}, {col+1}). Progress: {len(empty_cells)}/{target_empty}")
            else:
                puzzle[row][col] = temp  # 恢复数字
                print(f"Failed to empty cell ({row+1}, {col+1}) - would lose unique solution")
        
        
        print(len(empty_cells))
        # 验证并显示结果
        final_empty = set((i, j) for i in range(self.size) 
                        for j in range(self.size) if puzzle[i][j] == 0)
        
        print(f"\nDifficulty: {difficulty}")
        print(f"Target empty ratio: {difficulties[difficulty]:.2%}")
        print(f"Actual empty ratio: {len(final_empty)/total_cells:.2%}")
        print(f"Empty cells: {len(final_empty)} / {total_cells}")
        print(f"Attempts made: {len(attempted_cells)} / {total_cells}")
        
        # 验证空格计数是否一致
        if len(final_empty) != len(empty_cells):
            print(f"\nWARNING: Inconsistency detected!")
            print(f"Tracked empty cells: {len(empty_cells)}")
            print(f"Actual empty cells: {len(final_empty)}")
            extra_empty = final_empty - empty_cells
            if extra_empty:
                print(f"Extra empty cells found at: {extra_empty}")
        
        return puzzle, solved_board
        
class SudokuVisualizer:
    def __init__(self, size: int):
        self.size = size
        self.box_size = int(size ** 0.5)
        self.cell_size = min(480 // size, 480 // size)
        self.grid_size = self.cell_size * size
        self.colors = self._generate_colors()
        self.colors_word = [
            "red", "green", "blue", "magenta", "yellow",
            "aqua", "gray", "purple", "forest green"
        ][:size]
        
    # def _generate_colors(self) -> List[str]:
    #     if self.size == 4:
    #         # return ['#FF0000', '#00FF00', '#0000FF', '#FF00FF']
    #         return [
    #             '#C00000',  # 稍亮的暗红色
    #             '#008C00',  # 暗绿色
    #             '#0000B3',  # 暗蓝色
    #             '#C000C0'   # 稍亮的暗洋红色
    #         ]
    #     else:  # 9x9
    #         # return [
    #         # '#FF0000',  # 荧光红 (100%红)
    #         # '#00FF00',  # 荧光绿 (100%绿)
    #         # '#0000FF',  # 荧光蓝 (100%蓝)
    #         # '#FF00FF',  # 品红 (红+蓝极限混合)
    #         # '#FFFF00',  # 荧光黄 (100%红+绿)
    #         # '#00FFFF',  # 荧光青 (100%绿+蓝)
    #         # #'#FF4500',  # 炽橙 (比标准橙更刺眼)
    #         # '#696969',  # 灰
    #         # '#A020F0',  # 纯紫
    #         # '#228B22'   #暗夜森林
    #         # ]
    #         return [
    #             '#C00000',  # 稍亮的暗红色
    #             '#008C00',  # 暗绿色 (确保与森林绿 #228B22 有区别)
    #             '#0000B3',  # 暗蓝色
    #             '#C000C0',   # 稍亮的暗洋红色
    #             '#CCCC00',  # 暗黄色 (如果需要，也可以调整黄色)
    #             '#00CCCC',  # 暗青色 (如果需要，也可以调整青色)
    #             '#696969',  # 灰 (保持不变)
    #             '#800080',  # 暗紫色 (如果需要，也可以调整紫色)
    #             '#228B22'   # 森林绿 (保持不变)
    #         ]

    def _generate_colors(self) -> List[str]:
        if self.size == 4:
            return [
                '#E59090',  # 稍深的淡红色
                '#A9D8A9',  # 淡绿色 (更浅，低饱和度)
                '#A9C0E5',  # 淡蓝色 (类似MetaMath的浅蓝)
                '#E5A9E5'   # 淡洋红色 (更浅，低饱和度)
            ]
        else:  # 9x9
            return [
                '#E59090',  # 稍深的淡红色
                '#A9D8A9',  # 淡绿色 (与森林绿 #228B22 有明显区别)
                '#A9C0E5',  # 淡蓝色 (类似MetaMath的浅蓝)
                '#E5A9E5',  # 淡洋红色
                "#E8E885",  # 淡黄色 (更浅，低饱和度)
                "#6DEDE2",  # 淡青色 (更浅，低饱和度)
                '#696969',  # 灰色 (保持不变，或可调整为更浅的灰色如 #BEBEBE)
                "#B296E0",  # 淡紫色 (更浅，低饱和度)
                '#228B22'   # 森林绿 (保持不变，作为对比色)
            ]
    
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[float, float, float]:
        if s == 0.0:
            return (v, v, v)
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0:
            return (v, t, p)
        if i == 1:
            return (q, v, p)
        if i == 2:
            return (p, v, t)
        if i == 3:
            return (p, q, v)
        if i == 4:
            return (t, p, v)
        if i == 5:
            return (v, p, q)
            
    def draw_board(self, board: List[List[int]], filename: str):
        # Create image with padding for labels
        padding = 30  # 增加padding以适应更大的字体
        img = Image.new('RGB', (self.grid_size + 2*padding, self.grid_size + 2*padding), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw labels with larger font
        try:
            font = ImageFont.truetype("arial.ttf", 20)  # 增大字体大小到20
        except:
            font = ImageFont.load_default()
        
        for i in range(self.size):
            # Row labels - 调整位置以居中对齐
            text_width = draw.textlength(str(i + 1), font=font)  # 获取文本宽度
            text_height = font.size  # 获取字体高度
            
            # 计算文本中心位置
            row_x = padding//2 - text_width//2
            row_y = padding + i * self.cell_size + (self.cell_size - text_height)//2
            
            # Column labels - 调整位置以居中对齐
            col_x = padding + i * self.cell_size + (self.cell_size - text_width)//2
            col_y = padding//2 - text_height//2
            
            # 绘制标签
            draw.text((row_x, row_y), str(i + 1), fill='black', font=font)
            draw.text((col_x, col_y), str(i + 1), fill='black', font=font)
        
        # Fill cells
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] != 0:
                    x = padding + j * self.cell_size
                    y = padding + i * self.cell_size
                    draw.rectangle([x, y, x + self.cell_size, y + self.cell_size],
                                fill=self.colors[board[i][j]-1])
        
        # Draw grid
        for i in range(self.size + 1):
            line_width = 2 if i % self.box_size == 0 else 1
            # Vertical lines
            draw.line([(padding + i * self.cell_size, padding),
                    (padding + i * self.cell_size, padding + self.grid_size)],
                    fill='black', width=line_width)
            # Horizontal lines
            draw.line([(padding, padding + i * self.cell_size),
                    (padding + self.grid_size, padding + i * self.cell_size)],
                    fill='black', width=line_width)
        
        img.save(filename)
        
    def board_to_state(self, board: List[List[int]]) -> Dict:
        return {
            "size": self.size,
            "board": board,
            "colors": self.colors
        }
    
def main():
    import time
    import os

    # 创建测试输出目录
    if not os.path.exists('test_output'):
        os.makedirs('test_output')

    # ----------------------------
    # 测试1: 解算器功能验证
    # ----------------------------
    print("\n=== 测试1: 解算器功能验证 ===")
    
    # 测试用例1: 简单数独
    test_board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    solver = SudokuSolver(9)
    start_time = time.time()
    result = solver.solve(copy.deepcopy(test_board))
    elapsed = time.time() - start_time
    
    print(f"解题结果: {'成功' if result['success'] else '失败'}")
    print(f"解题时间: {elapsed:.4f}秒")
    print(f"是否唯一解: {result['unique']}")
    
    # 验证已知解
    expected_solution = [
        [5,3,4,6,7,8,9,1,2],
        [6,7,2,1,9,5,3,4,8],
        [1,9,8,3,4,2,5,6,7],
        [8,5,9,7,6,1,4,2,3],
        [4,2,6,8,5,3,7,9,1],
        [7,1,3,9,2,4,8,5,6],
        [9,6,1,5,3,7,2,8,4],
        [2,8,7,4,1,9,6,3,5],
        [3,4,5,2,8,6,1,7,9]
    ]
    
    assert result['solution'] == expected_solution, "解算器返回错误解答"

    steps = result['steps']
    for step in steps:
        print(step['reason'])

    print("测试1通过 ✓")

    # ----------------------------
    # 测试2: 生成器功能验证
    # ----------------------------
    print("\n=== 测试2: 生成器功能验证 ===")
    
    generator = SudokuGenerator(9)
    
    # 测试不同难度
    for difficulty in ['easy']:
        print(f"\n正在生成 {difficulty} 难度谜题...")
        start_time = time.time()
        puzzle, solution = generator.generate_puzzle(difficulty)
        elapsed = time.time() - start_time
        
        # 验证谜题
        empty_cells = sum(row.count(0) for row in puzzle)
        total_cells = 9*9
        empty_ratio = empty_cells / total_cells
        
        print(f"生成时间: {elapsed:.2f}秒")
        print(f"空格数量: {empty_cells} ({empty_ratio:.1%})")
        
        # 验证解的唯一性
        verify_result = solver.solve_base(copy.deepcopy(puzzle), record_steps=False)
        assert verify_result['success'], "生成的谜题无解"
        assert verify_result['unique'], "生成的谜题存在多解"
        
    print("测试2通过 ✓")

    print("\n所有测试通过！")

if __name__ == "__main__":
    main()