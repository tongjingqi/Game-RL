import json
import os
import argparse
import random
from typing import List, Dict, Tuple
from sudoku_core import SudokuGenerator, SudokuVisualizer, SudokuSolver

class SudokuDataGenerator:
    def __init__(self, size: int):
        self.size = size
        self.generator = SudokuGenerator(size)
        self.visualizer = SudokuVisualizer(size)
        self.visualizer.colors_word = [
            "red", "green", "blue", "magenta", "yellow",
            "aqua", "gray", "purple", "forest green"
        ][:size]
        self.solver = SudokuSolver(size)
        if(size == 4):
            self.colors_str = "red, green, blue, magenta"
        else :
            self.colors_str = "red, green, blue, magenta, yellow, aqua, gray, purple, forest green"
        
    def generate_question(self, board: List[List[int]], solved_board: List[List[int]], qa_type: str) -> Dict:
        if qa_type == "color_position":
            return self._generate_color_position_question(board, solved_board)
        elif qa_type == "color_count":
            return self._generate_color_count_question(board, solved_board)
        elif qa_type == "possible_colors":
            return self._generate_possible_colors_question(board, solved_board)
        elif qa_type == "empty_count":
            return self._generate_empty_count_question(board, solved_board)
        elif qa_type == "deductive_reasoning":
            return self._generate_deductive_reasoning_question(board, solved_board)
        else:
            raise ValueError(f"Unknown question type: {qa_type}")
            
    def _generate_color_position_question(self, board: List[List[int]], solved_board: List[List[int]]) -> Dict:
        while True:
            row = random.randint(0, self.size-1)
            col = random.randint(0, self.size-1)
            if board[row][col] != 0:
                break
        
        if(self.size == 4):
            color_options = "A.red, B.green, C.blue, D.magenta"

        else:
            color_options = "A.red, B.green, C.blue, D.magenta, E.yellow, F.aqua, G.gray, H.purple, I.forest green"

        options = [
            "A.red", "B.green", "C.blue", "D.magenta", "E.yellow",
            "F.aqua", "G.gray", "H.purple", "I.forest green"
        ][:self.size]

        answer_letters = ["A","B","C","D","E","F","G","H","I"][:self.size]
        answer_index = answer_letters[board[row][col]-1]
        
        return {
            "question_id": 1,
            "qa_type": "StateInfo",
            "qa_level": "Easy",
            "question_description": "Check color state at position",
            "question": f"This is a sudoku game in which the board is filled with a total number of colours equal to the length of the board's sides, and no rows, columns or squares are allowed to have duplicate colours.You should fill the empty cells on the board with following {self.size} colors: {self.colors_str}.In this Sudoku board, the row coordinates are 1-{self.size} from top to bottom, and the column coordinates are 1-{self.size} from left to right.What color is at position ({row+1},{col+1})(note that on the board the position ({row+1},{col+1}) has already been filled with a certain color)?Choose from following options:{color_options}",
            "answer": answer_index,
            "analysis": f"From the image we can see the color at Position ({row+1},{col+1}) is {self.visualizer.colors_word[board[row][col]-1]}.So the answer is {answer_index}",
            "options": options
        }
        
    def _generate_color_count_question(self, board: List[List[int]], solved_board: List[List[int]]) -> Dict:
        color_idx = random.randint(0, self.size-1)
        positions = []
        
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == color_idx + 1:
                    positions.append(f"({i+1},{j+1})")
        
        count = len(positions)
        return {
            "question_id": 2,
            "qa_type": "StateInfo",
            "qa_level": "Easy",
            "question_description": "Count occurrences of specific color",
            "question": f"This is a sudoku game in which the board is filled with a total number of colours equal to the length of the board's sides, and no rows, columns or squares are allowed to have duplicate colours.You should fill the empty cells on the board with following {self.size} colors: {self.colors_str}.In this Sudoku board, the row coordinates are 1-{self.size} from top to bottom, and the column coordinates are 1-{self.size} from left to right.How many times does {self.visualizer.colors_word[color_idx]} appear on the board?",
            "answer": str(count),
            "analysis": f"Color {self.visualizer.colors_word[color_idx]} appears at: {', '.join(positions)}, total {count} times.So the answer is {count}"
        }
        
    def _generate_possible_colors_question(self, board: List[List[int]], solved_board: List[List[int]]) -> Dict:
        empty_positions = [(i, j) for i in range(self.size) 
                          for j in range(self.size) if board[i][j] == 0]
        if not empty_positions:
            return self._generate_color_position_question(board, solved_board)
            
        row, col = random.choice(empty_positions)
        valid_nums = self.solver.get_valid_numbers(board, row, col)
        valid_colors_word = [self.visualizer.colors_word[num-1] for num in valid_nums]
        
        box_row = (row // self.solver.box_size) * self.solver.box_size
        box_col = (col // self.solver.box_size) * self.solver.box_size
        box_colors_word = [self.visualizer.colors_word[board[i][j]-1] 
                     for i in range(box_row, box_row + self.solver.box_size)
                     for j in range(box_col, box_col + self.solver.box_size)
                     if board[i][j] != 0]
        
        return {
            "question_id": 3,
            "qa_type": "StrategyOptimization",
            "qa_level": "Medium",
            "question_description": "Analyze possible colors to fill",
            "question": f"This is a sudoku game in which the board is filled with a total number of colours equal to the length of the board's sides, and no rows, columns or squares are allowed to have duplicate colours.You should fill the empty cells on the board with following {self.size} colors:{self.colors_str}.In this Sudoku board, the row coordinates are 1-{self.size} from top to bottom, and the column coordinates are 1-{self.size} from left to right.How many colors can be filled in position ({row+1},{col+1})?Inference based on the current situation focusing only on the colour of the position.",
            "answer": str(len(valid_colors_word)),
            "analysis": f"Constraint analysis for position ({row+1},{col+1}):\n" + \
                    f"1. Existing colors in row: {', '.join(self.visualizer.colors_word[n-1] for n in board[row] if n != 0)}\n" + \
                    f"2. Existing colors in column: {', '.join(self.visualizer.colors_word[n-1] for n in [board[i][col] for i in range(self.size)] if n != 0)}\n" + \
                    f"3. Existing colors in box: {', '.join(box_colors_word)}\n" + \
                    f"4. Therefore, possible colors are: {', '.join(valid_colors_word)}\n" + \
                    f"5. So, the answer is {str(len(valid_colors_word))}"
        }
        
    def _generate_empty_count_question(self, board: List[List[int]], solved_board: List[List[int]]) -> Dict:
        target_type = random.choice(['row', 'col'])
        N = random.randint(1, 2)
        count = 0
        details = []
        
        if target_type == 'row':
            for i in range(self.size):
                empty_positions = [j+1 for j in range(self.size) if board[i][j] == 0]
                empty = len(empty_positions)
                if empty > N:
                    count += 1
                details.append(f"row {i+1} have {empty} empty cells in positions {', '.join(map(str, empty_positions))}")
        
        elif target_type == 'col':
            for j in range(self.size):
                empty_positions = [i+1 for i in range(self.size) if board[i][j] == 0]
                empty = len(empty_positions)
                if empty > N:
                    count += 1
                details.append(f"col {j+1} have {empty} empty cells in positions {', '.join(map(str, empty_positions))}")
        
        return {
            "question_id": 4,
            "qa_type": "StateInfo",
            "qa_level": "Medium",
            "question_description": "Count regions with empty cells exceeding threshold",
            "question": f"This is a sudoku game in which the board is filled with a total number of colours equal to the length of the board's sides, and no rows, columns or squares are allowed to have duplicate colours.You should fill the empty cells on the board with following {self.size} colors: {self.colors_str}.In this Sudoku board, the row coordinates are 1-{self.size} from top to bottom, and the column coordinates are 1-{self.size} from left to right.How many {target_type}s have more than {N} empty cells?",
            "answer": str(count),
            "analysis": f"{target_type.capitalize()} analysis: {'; '.join(details)}. Total {count} {target_type}(s) have more than {N} empty cells.So the answer is {count}"
        }
    
    def _generate_deductive_reasoning_question(self, board: List[List[int]], solved_board: List[List[int]]) -> Dict:
        temp_board = [row[:] for row in board]
        steps = []
        dependencies = []

        # 寻找两个唯一可填的初始位置
        for step_num in range(2):
            found = False
            for i in range(self.size):
                for j in range(self.size):
                    if temp_board[i][j] == 0:
                        valid_nums = self.solver.get_valid_numbers(temp_board, i, j)
                        if len(valid_nums) == 1:
                            num = valid_nums[0]
                            color = self.visualizer.colors_word[num-1]
                            
                            # 生成详细约束分析
                            row_colors_word = [self.visualizer.colors_word[n-1] for n in temp_board[i] if n != 0]
                            col_colors_word = [self.visualizer.colors_word[temp_board[x][j]-1] for x in range(self.size) if temp_board[x][j] != 0]
                            
                            box_row = (i // self.solver.box_size) * self.solver.box_size
                            box_col = (j // self.solver.box_size) * self.solver.box_size
                            box_colors_word = [
                                self.visualizer.colors_word[temp_board[x][y]-1]
                                for x in range(box_row, box_row + self.solver.box_size)
                                for y in range(box_col, box_col + self.solver.box_size)
                                if temp_board[x][y] != 0
                            ]
                            
                            analysis = [
                                f"Step {step_num+1}: Position ({i+1},{j+1}) must be {color} because:",
                                f"1. Existing colors in row: {', '.join(row_colors_word) if row_colors_word else 'none'}",
                                f"2. Existing colors in column: {', '.join(col_colors_word) if col_colors_word else 'none'}",
                                f"3. Existing colors in {self.solver.box_size}x{self.solver.box_size} box: {', '.join(box_colors_word) if box_colors_word else 'none'}",
                                f"4. Therefore, the only possible color for this position is {color}."
                            ]
                            
                            steps.append( (i+1, j+1, color, '\n'.join(analysis)) )
                            dependencies.append( (i+1, j+1) )
                            temp_board[i][j] = num
                            found = True
                            break
                if found: break
            if not found:
                return self._generate_possible_colors_question(board, solved_board)

        # 寻找最终问题位置
        final_i, final_j, final_color = None, None, None
        for i in range(self.size):
            for j in range(self.size):
                if temp_board[i][j] == 0:
                    valid_nums = self.solver.get_valid_numbers(temp_board, i, j)
                    if len(valid_nums) == 1:
                        final_i, final_j = i+1, j+1
                        final_color = self.visualizer.colors_word[valid_nums[0]-1]
                        break
            if final_i: break
        
        if not final_i:
            return self._generate_possible_colors_question(board, solved_board)

        # 生成最终分析
        analysis = ["Deductive reasoning process:"]
        for step in steps:
            analysis.append(step[3])  # 直接使用预先生成的分析文本
            
        # 添加目标位置分析
        analysis.append(f"Final analysis for position ({final_i},{final_j}):")
        valid_nums = self.solver.get_valid_numbers(temp_board, final_i-1, final_j-1)
        row_colors_word = [self.visualizer.colors_word[n-1] for n in temp_board[final_i-1] if n != 0]
        col_colors_word = [self.visualizer.colors_word[temp_board[x][final_j-1]-1] for x in range(self.size) if temp_board[x][final_j-1] != 0]
        
        box_row = ((final_i-1) // self.solver.box_size) * self.solver.box_size
        box_col = ((final_j-1) // self.solver.box_size) * self.solver.box_size
        box_colors_word = [
            self.visualizer.colors_word[temp_board[x][y]-1]
            for x in range(box_row, box_row + self.solver.box_size)
            for y in range(box_col, box_col + self.solver.box_size)
            if temp_board[x][y] != 0
        ]
        
        analysis.extend([
            f"1. Existing colors in row: {', '.join(row_colors_word) if row_colors_word else 'none'}",
            f"2. Existing colors in column: {', '.join(col_colors_word) if col_colors_word else 'none'}",
            f"3. Existing colors in {self.solver.box_size}x{self.solver.box_size} box: {', '.join(box_colors_word) if box_colors_word else 'none'}",
            f"4. After previous deductions, possible color reduced to: {final_color}"
        ])

        if(self.size == 4):
            color_options = "A.red, B.green, C.blue, D.magenta"

        else:
            color_options = "A.red, B.green, C.blue, D.magenta, E.yellow, F.aqua, G.gray, H.purple, I.forest green"

        options = [
            "A.red", "B.green", "C.blue", "D.magenta", "E.yellow",
            "F.aqua", "G.gray", "H.purple", "I.forest green"
        ][:self.size]

        answer_letters = ["A","B","C","D","E","F","G","H","I"][:self.size]
        answer_index = self.visualizer.colors_word.index(final_color)
        
        analysis.append(f"So the answer is {answer_letters[answer_index]}")

        return {
            "question_id": 5,
            "qa_type": "ActionOutcome",
            "qa_level": "Hard",
            "question_description": "Multi-step deductive reasoning with constraints analysis",
            "question": f"This is a sudoku game in which the board is filled with a total number of colours equal to the length of the board's sides, and no rows, columns or squares are allowed to have duplicate colours.You should fill the empty cells on the board with following {self.size} colors:{self.colors_str}.In this Sudoku board, the row coordinates are 1-{self.size} from top to bottom, and the column coordinates are 1-{self.size} from left to right.After determining colors at positions {', '.join([f'({x},{y})' for x,y in dependencies])}, what color should be at position ({final_i},{final_j})?Choose from following options:{color_options}",
            "answer": answer_letters[answer_index],
            "analysis": '\n'.join(analysis),
            "options": options
        }
    
    
    def generate_dataset(self, num_samples: int, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            os.makedirs(os.path.join(output_dir, "images"))
            os.makedirs(os.path.join(output_dir, "states"))
            
        dataset = []
        question_types = ["color_position", "color_count", "possible_colors", "empty_count", "deductive_reasoning"]
        
        for i in range(1, num_samples + 1):
            # 随机选择棋盘大小和对应难度
            if i % 2 == 0:  # 偶数序号生成4x4
                size = 4
                plot_level = "Easy"
                difficulty = random.choice(["easy_4", "hard_4"])
            else:  # 奇数序号生成9x9
                size = 9
                plot_level = "Hard"
                difficulty = random.choice(["easy", "medium", "hard"])
                plot_level = "Medium" if difficulty == "easy" else "Hard"
            
            # 如果大小变化，需要重新初始化生成器
            if size != self.size:
                self.__init__(size)
            
            board, solved_board = self.generator.generate_puzzle(difficulty)
            
            image_path = os.path.join("images", f"board_{i:05d}.png")
            state_path = os.path.join("states", f"board_{i:05d}.json")
            
            self.visualizer.draw_board(board, os.path.join(output_dir, image_path))
            with open(os.path.join(output_dir, state_path), 'w') as f:
                json.dump(self.visualizer.board_to_state(board), f)
            
            # 为每个数独随机选择一种问题类型
            qa_type = random.choice(question_types)
            qa_data = self.generate_question(board, solved_board, qa_type)


            if(qa_data["question_id"] == 1):
                data_entry = {
                    "data_id": f"sudoku-{i:05d}",
                    "qa_type": qa_data["qa_type"],
                    "question_id":qa_data["question_id"],
                    "question_description": qa_data["question_description"],
                    "image": f"images/board_{i:05d}.png",
                    "state": f"states/board_{i:05d}.json",
                    "plot_level": plot_level,
                    "qa_level": qa_data["qa_level"],
                    "question": qa_data["question"],
                    "answer": qa_data["answer"],
                    "analysis": qa_data["analysis"],
                    "options": qa_data["options"]
                }
            elif(qa_data["question_id"] == 5):
                data_entry = {
                    "data_id": f"sudoku-{i:05d}",
                    "qa_type": qa_data["qa_type"],
                    "question_id":qa_data["question_id"],
                    "question_description": qa_data["question_description"],
                    "image": f"images/board_{i:05d}.png",
                    "state": f"states/board_{i:05d}.json",
                    "plot_level": plot_level,
                    "qa_level": qa_data["qa_level"],
                    "question": qa_data["question"],
                    "answer": qa_data["answer"],
                    "analysis": qa_data["analysis"],
                    "options": qa_data["options"]
                }
            else:    
                data_entry = {
                    "data_id": f"sudoku-{i:05d}",
                    "qa_type": qa_data["qa_type"],
                    "question_id":qa_data["question_id"],
                    "question_description": qa_data["question_description"],
                    "image": f"images/board_{i:05d}.png",
                    "state": f"states/board_{i:05d}.json",
                    "plot_level": plot_level,
                    "qa_level": qa_data["qa_level"],
                    "question": qa_data["question"],
                    "answer": qa_data["answer"],
                    "analysis": qa_data["analysis"]
                }
            
            dataset.append(data_entry)
                
        with open(os.path.join(output_dir, "data.json"), 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
            
def main():
    parser = argparse.ArgumentParser(description='Generate Sudoku dataset')
    parser.add_argument('num_samples', type=int, help='Number of samples to generate')
    parser.add_argument('--output_dir', type=str, default="sudoku_dataset", 
                      help='Output directory for the dataset')
    
    args = parser.parse_args()
    
    # 初始化为9x9，在生成过程中会根据需要切换大小
    generator = SudokuDataGenerator(9)
    generator.generate_dataset(args.num_samples, args.output_dir)
    print(f"Successfully generated {args.num_samples} samples in {args.output_dir}")
    
if __name__ == "__main__":
    main()