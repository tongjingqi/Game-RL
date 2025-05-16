import pygame
import random
import sys
import os
import json

# 初始化 pygame
pygame.init()

# 常量定义
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

# 游戏描述
game_explanation = """Now I'll give you a picture, which shows a screenshot of Ultra TicTacToe. The introduction of Ultra TicTacToe is as follows:
1. Board and coordinate representation: In this game, the board is divided into 9 3*3 squares(called Nine-grids). At the same time, we use $(i, j, row, col)$ to represent the coordinates of a cell: $(i, j)$ represents the coordinates of the Nine-grid; $(row, col)$ represents the coordinate of the cell within the Nine-grid; $i, j, row, col$ all range from 1 to 3. Two players take turns placing pieces on the board to mark the cells on the board, with the first player using "X" and the second player using "O" (this is the same as traditional TicTacToe). 
2. Rules for placing chess pieces: After the game starts, the first player places a chess piece in any cell in the Nine-grid in the middle (i.e., the Nine-grid (2, 2)). After that, the coordinates of each chess piece placed in the Nine-grid are the same as the coordinates of the Nine-grid in which the opponent's last chess piece was placed; for example, if the first player places a chess piece at the coordinates (2, 2, 3, 1) in the first step, then the second player needs to choose a chess piece in the Nine-grid (3, 1) in the second step. 
3. Scoring rules: For each player, each "Straight" (i.e., three identical chess pieces connected in a line, such as in the same row, the same column, or a diagonal line) in each Nine-grid is counted as 1 point. More than 1 point can be counted in each Nine-grid. 

Now I will give you a question about the game. Please extract information from the picture I give you, think carefully, reason, and answer: 
"""
game_explanation = game_explanation.strip()

# 定义类 UTTTGameGrid
class UTTTGameGrid:
    def __init__(self, plot_level="Easy"):
        self.plot_level = plot_level
        # self.margin = 50
        # self.cell_size = 60
        self.margin = 30
        self.cell_size = 40
        self.gap = self.cell_size  # 九宫格之间的间隔等于小格的边长
        self.screen_size = 3 * self.cell_size * 3 + 2 * self.gap
        self.total_size = self.screen_size + 2 * self.margin
        self.screen = pygame.Surface((self.total_size, self.total_size))
        self.font = pygame.font.SysFont(None, 24)
        self.piece_coord = {f"({s}, {t})": {"X": [], "O": []} for s in range(1, 4) for t in range(1, 4)}
        self.point_record = {"X": {f"({s}, {t})": 0 for s in range(1, 4) for t in range(1, 4)}, 
                             "O": {f"({s}, {t})": 0 for s in range(1, 4) for t in range(1, 4)}}
        self.all_points = {"X": 0, "O": 0}
        self.break_step_dict = {
            "Easy": {"low": 10, "high": 34},
            "Medium": {"low": 35, "high": 59},
            "Hard": {"low": 60, "high": 81}
        }
        self.middle_cell_count = 0  # 新增中间单元格计数器
        self.last_step = None
        self.best_next_step = None
        self.screen.fill(white)
        self.draw_main_grid()
        self.draw_small_grid()
        self.draw_labels()

    def draw_main_grid(self):
        for x in range(3):
            for y in range(3):
                top_left_x = self.margin + x * (3 * self.cell_size + self.gap)
                top_left_y = self.margin + y * (3 * self.cell_size + self.gap)
                pygame.draw.rect(self.screen, black, (top_left_x, top_left_y, 3 * self.cell_size, 3 * self.cell_size), 2)

    def draw_small_grid(self):
        for x in range(3):
            for y in range(3):
                top_left_x = self.margin + x * (3 * self.cell_size + self.gap)
                top_left_y = self.margin + y * (3 * self.cell_size + self.gap)
                for k in range(1, 3):
                    pygame.draw.line(self.screen, black, (top_left_x + k * self.cell_size, top_left_y), 
                                     (top_left_x + k * self.cell_size, top_left_y + 3 * self.cell_size), 1)
                    pygame.draw.line(self.screen, black, (top_left_x, top_left_y + k * self.cell_size), 
                                     (top_left_x + 3 * self.cell_size, top_left_y + k * self.cell_size), 1)

    def draw_labels(self):
        for s in range(3):
            label = self.font.render(str(s + 1), True, black)
            for t in range(3):
                # 行号
                self.screen.blit(label, (self.margin // 2, self.margin + t * (3 * self.cell_size + self.gap) + s * self.cell_size + self.cell_size // 2 - 8))
                # 列号
                self.screen.blit(label, (self.margin + t * (3 * self.cell_size + self.gap) + s * self.cell_size + self.cell_size // 2 - 8, self.margin // 2))

    def coord_to_str(self, row, col):
        return f"({row}, {col})"

    def check_coord_avail(self, i, j, row, col):
        if i < 1 or i > 3 or j < 1 or j > 3:
            return False
        if col < 1 or col > 3 or row < 1 or row > 3:
            return False
        if self.coord_to_str(row, col) in self.piece_coord[self.coord_to_str(i, j)]["X"] or \
           self.coord_to_str(row, col) in self.piece_coord[self.coord_to_str(i, j)]["O"]:
            return False
        return True

    def draw_piece(self, i, j, row, col, piece):
        if not self.check_coord_avail(i, j, row, col):
            return

        x = (j - 1) * 3 + col - 1
        y = (i - 1) * 3 + row - 1
        center_x = self.margin + x * self.cell_size + self.cell_size // 2 + (j - 1) * self.gap
        center_y = self.margin + y * self.cell_size + self.cell_size // 2 + (i - 1) * self.gap
        if piece == "X":
            pygame.draw.line(self.screen, red, 
                            (center_x - 20, center_y - 20), (center_x + 20, center_y + 20), 2)
            pygame.draw.line(self.screen, red, 
                            (center_x + 20, center_y - 20), (center_x - 20, center_y + 20), 2)
        elif piece == "O":
            pygame.draw.circle(self.screen, blue, (center_x, center_y), 20, 2)
        self.piece_coord[self.coord_to_str(i, j)][piece].append(self.coord_to_str(row, col))

        # 更新中间单元格计数器
        if row == 2 and col == 2:
            self.middle_cell_count += 1

    def random_piece_in_nine_grid(self, i, j, piece):
        coord_avail_list = [(x, y) for x in range(1, 4) for y in range(1, 4) if self.check_coord_avail(i, j, x, y)]
        if not coord_avail_list:
            return 0, 0
        row, col = random.choice(coord_avail_list)
        self.draw_piece(i, j, row, col, piece)
        return row, col

    def find_best_piece_in_nine_grid(self, i, j, piece):
        coord_avail_list = [(x, y) for x in range(1, 4) for y in range(1, 4) if self.check_coord_avail(i, j, x, y)]
        if not coord_avail_list:
            return 0, 0

        add_point_record = {k: [] for k in range(5)}  # 记录每个得分的可能新棋子
        max_point_diff = 0  # 最大新增得分
        old_point = self.point_record[piece][self.coord_to_str(i, j)]
        for row, col in coord_avail_list:
            new_point, _, _, _ = self.check_point_in_nine_grid(i, j, row, col, piece)
            point_diff = new_point - old_point
            if point_diff > max_point_diff:
                max_point_diff = point_diff
            add_point_record[point_diff].append((row, col))
        return max_point_diff, add_point_record[max_point_diff]

    def check_point_in_nine_grid(self, i=1, j=1, row=0, col=0, piece="X"):
        all_pieces = self.piece_coord[self.coord_to_str(i, j)][piece]
        if row > 0 and col > 0:
            all_pieces.append(self.coord_to_str(row, col))

        point = 0
        point_row = 0
        point_col = 0
        point_diag = 0
        if len(all_pieces) >= 3:
            for s in range(1, 4):
                if all(self.coord_to_str(s, t) in all_pieces for t in range(1, 4)):
                    point += 1
                    point_row += 1
            for t in range(1, 4):
                if all(self.coord_to_str(s, t) in all_pieces for s in range(1, 4)):
                    point += 1
                    point_col += 1
            if all(self.coord_to_str(s, s) in all_pieces for s in range(1, 4)):
                point += 1
                point_diag += 1
            if all(self.coord_to_str(s, 4 - s) in all_pieces for s in range(1, 4)):
                point += 1
                point_diag += 1

        if row > 0 and col > 0:
            all_pieces.remove(self.coord_to_str(row, col))
        return point, point_row, point_col, point_diag

    def current_piece(self, step):
        return "X" if step % 2 == 1 else "O"

    def generate_uttt_game(self, plot_level="Easy"):
        step = 1
        step_limit = 81
        break_step = self.break_step_dict[plot_level]["low"]
        last_i, last_j = 2, 2  # 从中间的九宫格开始
        middle_cell_count = 0

        while step <= step_limit:
            piece = self.current_piece(step)
            coord_avail_list = [(x, y) for x in range(1, 4) for y in range(1, 4) if self.check_coord_avail(last_i, last_j, x, y)]
            max_point_diff, best_pieces = self.find_best_piece_in_nine_grid(last_i, last_j, piece)  # 找到最优位置
            if len(best_pieces) == 1 and max_point_diff > 0 and step >= break_step:
                row, col = best_pieces[0]
                self.best_next_step = [last_i, last_j, row, col]
                print("Found available game state.")
                print(f"Step {step}: {piece} should be in ({last_i}, {last_j}, {row}, {col})")
                break
            else:
                row, col = random.choice(best_pieces)
                self.draw_piece(last_i, last_j, row, col, piece)
                self.last_step = [last_i, last_j, row, col]
                # print(f"Step {step}: {piece} in ({last_i}, {last_j}, {row}, {col})")
                if row == 2 and col == 2:
                    middle_cell_count += 1
                if middle_cell_count >= 9:
                    print(f"Game over with 9 pieces in the middle cells.")
                    # print(f"Current points: {self.all_points}")
                    # break
                    return None
                if row == 0 or col == 0:
                    print(f"Step {step}: {piece} in ({last_i}, {last_j}) failed")
                    # break
                    return None
                
                if max_point_diff > 0:
                    self.point_record[piece][self.coord_to_str(last_i, last_j)] += max_point_diff
                    self.all_points[piece] += max_point_diff
                    # print(f"{piece} wins {max_point_diff} point(s) in ({last_i}, {last_j}, {row}, {col})")
                    # print(f"Current points: {self.all_points}")
                step += 1
                last_i, last_j = row, col

        return self.get_game_state()

    def get_game_state(self):
        game_state = {
            "rows": 3,
            "cols": 3,
            "middle_cell_count": self.middle_cell_count,  # 新增中间单元格计数信息
            "last_step": self.last_step,
            "best_next_step": self.best_next_step,
            "total_steps": sum(len(self.piece_coord[coord]["X"]) + len(self.piece_coord[coord]["O"]) for coord in self.piece_coord),
            "piece_info": []
        }
        for coord, pieces in self.piece_coord.items():
            for piece_type, coords in pieces.items():
                for coord_str in coords:
                    game_state["piece_info"].append({
                        "nine_grid": coord,
                        "position": coord_str,
                        "type": piece_type
                    })
        return game_state
        
    def save_image(self, filename):
        try:
            pygame.image.save(self.screen, filename)
        except:
            try:
                new_filename = os.path.join(file_path, filename)
                pygame.image.save(self.screen, new_filename)
            except:
                print(f"Failed to save image {filename}.")
                return False


def check_point_in_nine_grid(nine_grid, all_pieces):
    """
    检查在给定九宫格中某一方的得分
    :param nine_grid: 九宫格坐标
    :param all_pieces: 该九宫格中标记的所有棋子位置
    :return: 得分信息（总得分、行得分、列得分、对角线得分）
    """
    i, j = map(int, nine_grid[1:-1].split(", "))
    point = 0
    point_row = 0
    point_col = 0
    point_diag = 0

    if len(all_pieces) >= 3:
        for s in range(1, 4):
            if all(f"({s}, {t})" in all_pieces for t in range(1, 4)):
                point += 1
                point_row += 1
        for t in range(1, 4):
            if all(f"({s}, {t})" in all_pieces for s in range(1, 4)):
                point += 1
                point_col += 1
        if all(f"({s}, {s})" in all_pieces for s in range(1, 4)):
            point += 1
            point_diag += 1
        if all(f"({s}, {4 - s})" in all_pieces for s in range(1, 4)):
            point += 1
            point_diag += 1

    return point, point_row, point_col, point_diag

def generate_uttt_game(plot_level="Easy"):
    grid = UTTTGameGrid(plot_level=plot_level)
    flag = grid.generate_uttt_game(plot_level=plot_level)
    total_steps = grid.get_game_state()["total_steps"]
    print(f"Total steps: {total_steps}")
    while (not flag) or (total_steps > grid.break_step_dict[plot_level]["high"]): # 保证生成的游戏局面有效且步数在合理范围内
        print("Regenerate game for invalid game state or too many steps...")
        grid = UTTTGameGrid(plot_level=plot_level)
        flag = grid.generate_uttt_game(plot_level=plot_level)
        total_steps = grid.get_game_state()["total_steps"]
        print(f"Total steps: {total_steps}")
    return grid

def trans_coord_to_str(nine_grid, position):
    i, j = map(int, nine_grid[1:-1].split(", "))
    row, col = map(int, position[1:-1].split(", "))
    return f"({i}, {j}, {row}, {col})"

def generate_question_1(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "plot_id": plot_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Easy",
        "qa_type": "StateInfo",
        "question_id": 1,
        "question_description": "Find which player marked the cell at a given coordinate.",
        "question": game_explanation + " Which player marked the cell at {coord} in the image? Options: {option_list}",
        "answer": "{option_number}",
        "analysis": "{process} So, the option number is {option_number}.",
        "options": ["First Player", "Second Player", "Not Marked"]
    }

    # 随机选择一个九宫格和位置
    nine_grids = list(set(info["nine_grid"] for info in game_state["piece_info"]))
    if nine_grids:
        nine_grid = random.choice(nine_grids)
        positions = list(set(info["position"] for info in game_state["piece_info"] if info["nine_grid"] == nine_grid))
        if positions:
            position = random.choice(positions)
        else:
            # 如果九宫格内没有棋子，则随机选择一个位置
            position = random.choice([f"({row}, {col})" for row in range(1, 4) for col in range(1, 4)])
    else:
        # 如果没有任何棋子，则随机选择一个九宫格和位置
        nine_grid = random.choice([f"({i}, {j})" for i in range(1, 4) for j in range(1, 4)])
        position = random.choice([f"({row}, {col})" for row in range(1, 4) for col in range(1, 4)])

    # 获取该格子的棋子类型
    block_info = next((info for info in game_state["piece_info"] if info["nine_grid"] == nine_grid and info["position"] == position), None)
    if block_info:
        block_type = block_info["type"]
        if block_type == "X":
            option_number = 1  # First Player
            process = f"There is an X piece at {trans_coord_to_str(nine_grid, position)} in the image, which means it has been marked by First Player."
        elif block_type == "O":
            option_number = 2  # Second Player
            process = f"There is an O piece at {trans_coord_to_str(nine_grid, position)} in the image, which means it has been marked by Second Player."
    else:
        option_number = 3  # Not Marked
        process = f"There is no piece at {trans_coord_to_str(nine_grid, position)} in the image, which means it has not been marked by any player."

    coord_str = trans_coord_to_str(nine_grid, position)
    options = question_template["options"]
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options)])

    # 填充模板
    question_template["question"] = question_template["question"].format(
        coord=coord_str,
        option_list=option_list
    )
    question_template["answer"] = question_template["answer"].format(option_number=option_number)
    question_template["analysis"] = question_template["analysis"].format(
        process=process,
        option_number=option_number
    )

    return question_template


def generate_question_2(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "plot_id": plot_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Easy",
        "qa_type": "StateInfo",
        "question_id": 2,
        "question_description": "Given the coordinate of last step, find the number of possible coordinates of next step.",
        "question": game_explanation + " Now your opponent place a piece at {last_piece_coord}. What is the number of possible coordinates of your next step? Options: {option_list}",
        "answer": "{option_number}",
        "analysis": "Since the opponent placed a piece at {last_piece_coord}, our next step should be in the Nine-grid ({next_i}, {next_j}). In this nine grid, we can see that {coord_list_marked_by_X} are marked by the First Player, while {coord_list_marked_by_O} are marked by the Second Player. So, the possible coordinates are the rest cells in the Nine-grid, being {coord_avail_list}. This means there are {coord_avail_num} available coordinate(s), so the option number is {option_number}.",
        "options": []
    }

    last_step = game_state["last_step"]
    last_i, last_j, last_row, last_col = last_step
    last_piece_coord = f"({last_i}, {last_j}, {last_row}, {last_col})"
    
    best_next_step = game_state["best_next_step"]
    next_i, next_j, _, _ = best_next_step
    
    
    # 获取下一个九宫格中标记的坐标列表
    coords_marked_by_X = [info["position"] for info in game_state["piece_info"] if info["nine_grid"] == f"({next_i}, {next_j})" and info["type"] == "X"]
    str_coords_marked_by_X = ", ".join(coords_marked_by_X) if coords_marked_by_X else "no cell"
    coords_marked_by_O = [info["position"] for info in game_state["piece_info"] if info["nine_grid"] == f"({next_i}, {next_j})" and info["type"] == "O"]
    str_coords_marked_by_O = ", ".join(coords_marked_by_O) if coords_marked_by_O else "no cell"

    # 检查下一个九宫格中可用的坐标
    # coord_avail_list = [(x, y) for x in range(1, 4) for y in range(1, 4) if UTTTGameGrid().check_coord_avail(next_i, next_j, x, y)]
    coord_marked_list = [info["position"] for info in game_state["piece_info"] if info["nine_grid"] == f"({next_i}, {next_j})"]
    coord_avail_list = [(x, y) for x in range(1, 4) for y in range(1, 4) if f"({x}, {y})" not in coord_marked_list]
    coord_avail_num = len(coord_avail_list)
    
    # 将可用坐标转换为字符串格式
    coord_avail_list_str = ", ".join([f"({x}, {y})" for x, y in coord_avail_list])
    
    # 生成选项列表
    # options_made = [str(coord_avail_num)]
    # for _ in range(3):
    #     offset = random.randint(-3, 3)  # 随机上下浮动
    #     while str(coord_avail_num + offset) in options_made or (coord_avail_num + offset) <= 0 or (coord_avail_num + offset) > 9:
    #         offset = random.randint(-3, 3)
    #     options_made.append(str(coord_avail_num + offset))
    # random.shuffle(options_made)
    options_made = [str(num) for num in range(0, 10)]
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options_made)])
    option_number = options_made.index(str(coord_avail_num)) + 1
    
    # 填充模板
    question_template["question"] = question_template["question"].format(
        last_piece_coord=last_piece_coord,
        option_list=option_list
    )
    question_template["answer"] = question_template["answer"].format(option_number=option_number)
    question_template["analysis"] = question_template["analysis"].format(
        last_piece_coord=last_piece_coord,
        next_i=next_i,
        next_j=next_j,
        coord_list_marked_by_X=str_coords_marked_by_X,
        coord_list_marked_by_O=str_coords_marked_by_O,
        coord_avail_list=coord_avail_list_str,
        coord_avail_num=coord_avail_num,
        option_number=option_number
    )
    question_template["options"] = options_made

    return question_template


def generate_question_3(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "plot_id": plot_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Easy",
        "qa_type": "StateInfo",
        "question_id": 3,
        "question_description": "Find the number of marked middle cells in the image.",
        "question": game_explanation + " How many middle cells in the image are marked? Options: {option_list}",
        "answer": "{option_number}",
        "analysis": "We check the middle cells in the Nine-grids one by one.\n{counting_process}\nSo there are {marked_middle_cell_num} middle cell(s) marked, the option number is {option_number}.",
        "options": []
    }

    # 中间单元格坐标
    middle_cells = [(f"({i}, {j})", "(2, 2)") for i in range(1, 4) for j in range(1, 4)]

    # 计算标记的中间单元格数量
    marked_middle_cell_num = 0
    counting_process = []
    for nine_grid, position in middle_cells:
        if any(info["nine_grid"] == nine_grid and info["position"] == position for info in game_state["piece_info"]):
            marked_middle_cell_num += 1
            piece_type = next(info["type"] for info in game_state["piece_info"] if info["nine_grid"] == nine_grid and info["position"] == position)
            counting_process.append(f"The middle cell at ({nine_grid[1:-1]}, {position[1:-1]}) is marked by {piece_type}.")
        else:
            counting_process.append(f"The middle cell at ({nine_grid[1:-1]}, {position[1:-1]}) is not marked.")

    # 生成选项列表
    options_made = [str(marked_middle_cell_num)]
    # for _ in range(3):
    #     offset = random.randint(-3, 3)  # 随机上下浮动
    #     while str(marked_middle_cell_num + offset) in options_made or (marked_middle_cell_num + offset) < 0 or (marked_middle_cell_num + offset) > 9:
    #         offset = random.randint(-3, 3)
    #     options_made.append(str(marked_middle_cell_num + offset))
    # random.shuffle(options_made)
    options_made = [str(num) for num in range(0, 10)]
    option_number = options_made.index(str(marked_middle_cell_num)) + 1
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options_made)])

    # 填充模板
    question_template["question"] = question_template["question"].format(
        option_list=option_list
    )
    question_template["answer"] = question_template["answer"].format(option_number=option_number)
    question_template["analysis"] = question_template["analysis"].format(
        counting_process="\n".join(counting_process),
        marked_middle_cell_num=marked_middle_cell_num,
        option_number=option_number
    )
    question_template["options"] = options_made

    return question_template


def generate_question_4(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "plot_id": plot_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Medium",
        "qa_type": "StateInfo",
        "question_id": 4,
        "question_description": "Find the number of pieces in the image.",
        "question": game_explanation + " How many pieces are there in the image? Options: {option_list}",
        "answer": "{option_number}",
        "analysis": "We count the number of chess pieces in the Nine-grids one by one. {counting_process} So there are {adding_process} = {piece_num} pieces, the option number is {option_number}.",
        "options": []
    }

    # 计算每个九宫格中的棋子数量
    counting_process = []
    piece_counts = {"X": [], "O": []}
    total_piece_count = 0
    
    for i in range(1, 4):
        for j in range(1, 4):
            nine_grid = f"({i}, {j})"
            x_count = len([info for info in game_state["piece_info"] if info["nine_grid"] == nine_grid and info["type"] == "X"])
            o_count = len([info for info in game_state["piece_info"] if info["nine_grid"] == nine_grid and info["type"] == "O"])
            piece_counts["X"].append(x_count)
            piece_counts["O"].append(o_count)
            total_pieces_in_nine_grid = x_count + o_count
            total_piece_count += total_pieces_in_nine_grid
            if total_pieces_in_nine_grid > 0:
                counting_process.append(f"In Nine-grid ({i}, {j}), there are {x_count} X piece(s) and {o_count} O piece(s), totaling {total_pieces_in_nine_grid} piece(s).")
            else:
                counting_process.append(f"In nine grid ({i}, {j}), there are no pieces.")

    # 生成 `{adding_process}` 字符串
    adding_process = " + ".join([str(x_count + o_count) for x_count, o_count in zip(piece_counts["X"], piece_counts["O"])])
    if not adding_process.strip().replace(" + ", ""):  # 如果没有任何棋子，则添加默认值
        adding_process = "0"

    # 生成选项列表
    options_made = [str(total_piece_count)]
    random_range = 15
    option_count = 8
    for _ in range(option_count - 1):
        offset = random.randint(-random_range, random_range)  # 随机上下浮动
        while str(total_piece_count + offset) in options_made or (total_piece_count + offset) < 0:
            offset = random.randint(-random_range, random_range)
        options_made.append(str(total_piece_count + offset))
    random.shuffle(options_made)
    option_number = options_made.index(str(total_piece_count)) + 1
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options_made)])

    # 填充模板
    question_template["question"] = question_template["question"].format(
        option_list=option_list
    )
    question_template["answer"] = question_template["answer"].format(option_number=option_number)
    question_template["analysis"] = question_template["analysis"].format(
        counting_process="\n".join(counting_process),
        adding_process=adding_process,
        piece_num=total_piece_count,
        option_number=option_number
    )
    question_template["options"] = options_made

    return question_template


def generate_question_5(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "plot_id": plot_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Medium",
        "qa_type": "StateInfo",
        "question_id": 5,
        "question_description": "Find the points the given player has got within the given Nine-grid.",
        "question": game_explanation + " How many points has the {player_name} got within the Nine-grid {nine_grid_coord}? Options: {option_list}",
        "answer": "{option_number}",
        "analysis": "The {player_name} uses {piece} pieces. We count the points in the order of rows, columns, and diagonals. We can see that in Nine-grid {nine_grid_coord}, there are {point_row} point(s) in rows, {point_col} point(s) in columns, and {point_diag} point(s) in diagonals, which is {point} point(s) in total. So, the option number is {option_number}.",
        "options": []
    }

    # 随机选择一个九宫格和玩家
    nine_grids = list(set(info["nine_grid"] for info in game_state["piece_info"]))
    if not nine_grids:
        nine_grid = random.choice([f"({i}, {j})" for i in range(1, 4) for j in range(1, 4)])
    else:
        nine_grid = random.choice(nine_grids)

    player_name = random.choice(["First Player", "Second Player"])
    piece_type = "X" if player_name == "First Player" else "O"

    # 获取该九宫格中的棋子信息
    all_pieces = [info["position"] for info in game_state["piece_info"] if info["nine_grid"] == nine_grid and info["type"] == piece_type]

    # 计算该九宫格中的得分
    point, point_row, point_col, point_diag = check_point_in_nine_grid(nine_grid, all_pieces)

    # 生成选项列表
    options_made = [str(point)]
    random_range = 15
    option_count = 8
    for _ in range(option_count - 1):
        offset = random.randint(-random_range, random_range)  # 随机上下浮动
        while str(point + offset) in options_made or (point + offset) < 0:
            offset = random.randint(-random_range, random_range)
        options_made.append(str(point + offset))
    random.shuffle(options_made)
    option_number = options_made.index(str(point)) + 1
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options_made)])

    # 填充模板
    question_template["question"] = question_template["question"].format(
        player_name=player_name,
        nine_grid_coord=nine_grid,
        option_list=option_list
    )
    question_template["answer"] = question_template["answer"].format(option_number=option_number)
    question_template["analysis"] = question_template["analysis"].format(
        player_name=player_name,
        piece=piece_type,
        nine_grid_coord=nine_grid,
        point_row=point_row,
        point_col=point_col,
        point_diag=point_diag,
        point=point,
        option_number=option_number
    )
    question_template["options"] = options_made

    return question_template


def generate_question_6(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "plot_id": plot_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Hard",
        "qa_type": "StateInfo",
        "question_id": 6,
        "question_description": "Given the Player name, find in which Nine-grid to place the piece.",
        "question": game_explanation + " If you are {player_name}, from the image, we can see now it's your turn to place a piece. According to the rules of the game, in which Nine-grid should you place the next piece? Options: {option_list}",
        "answer": "{option_number}",
        "analysis": "Since we are the {player_name} now, we use the {your_piece} piece. First, we need to count the number of {your_piece} pieces in each Nine-grid.\n{counting_process_of_your_piece}\nThen, we need to count the number of {the_other_piece} pieces in each position of every Nine-grid.\n{counting_process_of_the_other_piece}\nSo the quantitative differences corresponding to these coordinates are {diff_list} respectively.\nFrom this difference, {supp_for_X}we can tell that our next step should be in {answer}, which means the option number is {option_number}.",
        "options": []
    }

    # 找到下一个九宫格的位置
    best_next_step = game_state["best_next_step"]
    last_step = game_state["last_step"]
    next_nine_grid = f"({best_next_step[0]}, {best_next_step[1]})"

    # 确定当前玩家和对方玩家的棋子类型
    other_piece_type = next(info["type"] for info in game_state["piece_info"] if info["nine_grid"] == f"({last_step[0]}, {last_step[1]})" and info["position"] == f"({last_step[2]}, {last_step[3]})")
    piece_type = "X" if other_piece_type == "O" else "O"
    player_name = "First Player" if piece_type == "X" else "Second Player"
    supp_for_X = "plus the first chess piece is in the Nine-grid (2, 2) and there is no corresponding previous step O piece, " if player_name == "First Player" else ""
    # 统计每个九宫格中当前玩家和对方玩家的棋子数量
    your_piece_counts = {}
    other_piece_counts = {f"({row}, {col})": [0] * 9 for row in range(1, 4) for col in range(1, 4)}

    for nine_grid in [(f"({i}, {j})") for i in range(1, 4) for j in range(1, 4)]:
        your_pieces = [info["position"] for info in game_state["piece_info"] if info["nine_grid"] == nine_grid and info["type"] == piece_type]
        your_piece_counts[nine_grid] = len(your_pieces)
        
        for pos in [(f"({row}, {col})") for row in range(1, 4) for col in range(1, 4)]:
            other_pieces = [info["position"] for info in game_state["piece_info"] if info["nine_grid"] == nine_grid and info["type"] == other_piece_type and info["position"] == pos]
            other_piece_counts[pos][((int(nine_grid[1]) - 1) * 3 + int(nine_grid[4]) - 1)] = len(other_pieces)

    # 生成详细的过程描述
    counting_process_of_your_piece = []
    your_piece_num = []
    for nine_grid in [(f"({i}, {j})") for i in range(1, 4) for j in range(1, 4)]:
        your_count = your_piece_counts[nine_grid]
        counting_process_of_your_piece.append(f"In nine grid ({nine_grid[1:-1]}), there are {your_count} {piece_type} piece(s).")
        your_piece_num.append(your_count)

    counting_process_of_the_other_piece = []
    opposite_piece_num = []
    for pos in [(f"({row}, {col})") for row in range(1, 4) for col in range(1, 4)]:
        counts_in_positions = [other_piece_counts[pos][(int(nine_grid[1]) - 1) * 3 + int(nine_grid[4]) - 1] for nine_grid in [(f"({i}, {j})") for i in range(1, 4) for j in range(1, 4)]]
        total_count = sum(counts_in_positions)
        counting_process_of_the_other_piece.append(f"In position ({pos[1:-1]}), there are {total_count} {other_piece_type} piece(s) across all Nine-grids.")
        opposite_piece_num.append(total_count)

    diff_piece_num = [your - opposite for your, opposite in zip(your_piece_num, opposite_piece_num)]

    # 生成选项列表
    next_i = best_next_step[0]
    next_j = best_next_step[1]
    answer = f"Nine-grid ({next_i}, {next_j})"
    # options_made = [answer]  # 将九宫格坐标格式化为 (i, j)
    # for _ in range(3):
    #     offset_i = random.randint(-1, 1)
    #     offset_j = random.randint(-1, 1)
    #     while abs(offset_i) + abs(offset_j) == 0:  # 确保不是原坐标
    #         offset_i = random.randint(-1, 1)
    #         offset_j = random.randint(-1, 1)
    #     new_i = (int(next_nine_grid[1]) - 1 + offset_i) % 3 + 1
    #     new_j = (int(next_nine_grid[4]) - 1 + offset_j) % 3 + 1
    #     option = f"Nine-grid ({new_i}, {new_j})"
    #     while option in options_made:
    #         offset_i = random.randint(-1, 1)
    #         offset_j = random.randint(-1, 1)
    #         while abs(offset_i) + abs(offset_j) == 0:
    #             offset_i = random.randint(-1, 1)
    #             offset_j = random.randint(-1, 1)
    #         new_i = (int(next_nine_grid[1]) - 1 + offset_i) % 3 + 1
    #         new_j = (int(next_nine_grid[4]) - 1 + offset_j) % 3 + 1
    #         option = f"Nine-grid ({new_i}, {new_j})"
    #     options_made.append(option)
    # random.shuffle(options_made)
    options_made = [f"Nine-grid ({x}, {y})" for x in range(1, 4) for y in range(1, 4)]
    option_number = options_made.index(answer) + 1
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options_made)])

    # 填充模板
    question_template["question"] = question_template["question"].format(
        player_name=player_name,
        option_list=option_list
    )
    question_template["answer"] = question_template["answer"].format(option_number=option_number)
    question_template["analysis"] = question_template["analysis"].format(
        player_name=player_name,
        your_piece=piece_type,
        counting_process_of_your_piece="\n".join(counting_process_of_your_piece),
        the_other_piece=other_piece_type,
        counting_process_of_the_other_piece="\n".join(counting_process_of_the_other_piece),
        diff_list=", ".join([str(diff) for diff in diff_piece_num]),
        supp_for_X=supp_for_X,
        answer=answer,
        option_number=option_number
    )
    question_template["options"] = options_made

    return question_template


def generate_question_7(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "plot_id": plot_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Hard",
        "qa_type": "StrategyOptimization",
        "question_id": 7,
        "question_description": "Given the coordinate of last step, find the coordinate to place the next piece to get the highest point.",
        "question": game_explanation + " Now your opponent place a piece at {last_piece_coord}. At which coordinate should you place your next piece to win the highest point?",
        "answer": "{max_coord}",
        "analysis": "Since the opponent placed a piece at {last_piece_coord}, our next step should be in the Nine-grid ({next_i}, {next_j}). In this Nine-grid, {avail_coord_num} coordinate(s) are available, and we count their points one by one. {counting_process} We can see that when choosing {max_coord}, the final point is the highest, being {max_point}. So, the answer is {max_coord}."
    }

    # 获取最后一个棋子的位置（假设是对手的）
    last_step = game_state["last_step"]
    last_i, last_j, last_row, last_col = last_step
    last_piece_coord = f"({last_i}, {last_j}, {last_row}, {last_col})"
    
    # 确定下一步应该落在哪个九宫格
    next_i, next_j = last_row, last_col
    
    # 检查下一个九宫格中可用的坐标
    # coord_avail_list = [(x, y) for x in range(1, 4) for y in range(1, 4) if UTTTGameGrid().check_coord_avail(next_i, next_j, x, y)]
    coord_marked_list = [info["position"] for info in game_state["piece_info"] if info["nine_grid"] == f"({next_i}, {next_j})"]
    coord_avail_list = [(x, y) for x in range(1, 4) for y in range(1, 4) if f"({x}, {y})" not in coord_marked_list]
    avail_coord_num = len(coord_avail_list)

    # 确定当前玩家的棋子类型
    other_piece_type = next(info["type"] for info in game_state["piece_info"] if info["nine_grid"] == f"({last_i}, {last_j})" and info["position"] == f"({last_row}, {last_col})")
    piece_type = "X" if other_piece_type == "O" else "O"

    # 计算每个可用坐标的得分
    counting_process = []
    best_next_step = game_state["best_next_step"]
    best_i, best_j, best_row, best_col = best_next_step

    for row, col in coord_avail_list:
        new_pieces = game_state["piece_info"] + [{"nine_grid": f"({next_i}, {next_j})", "position": f"({row}, {col})", "type": piece_type}]
        point, point_row, point_col, point_diag = check_point_in_nine_grid(f"({next_i}, {next_j})", [info["position"] for info in new_pieces if info["nine_grid"] == f"({next_i}, {next_j})" and info["type"] == piece_type])

        counting_process.append(f"If placing at ({next_i}, {next_j}, {row}, {col}), you will get {point_row} point(s) in rows, {point_col} point(s) in columns, and {point_diag} point(s) in diagonals, totaling {point} point(s).")

        if row == best_row and col == best_col:
            max_coord = f"({next_i}, {next_j}, {row}, {col})"
            max_point = point

    # 填充模板
    question_template["question"] = question_template["question"].format(
        last_piece_coord=last_piece_coord
    )
    question_template["answer"] = question_template["answer"].format(max_coord=max_coord)
    question_template["analysis"] = question_template["analysis"].format(
        last_piece_coord=last_piece_coord,
        next_i=next_i,
        next_j=next_j,
        avail_coord_num=avail_coord_num,
        counting_process="\n".join(counting_process),
        max_coord=max_coord,
        max_point=max_point
    )

    return question_template

def generate_questions_for_plot_level(plot_level="Easy", num_images=1, start_image_id=1, start_data_id=1):
    all_questions = []
    image_id = start_image_id
    data_id = start_data_id
    rows = 3
    cols = 3

    for i in range(num_images):
        # image_filename = os.path.join(f'{file_path}\\images', f'board_{image_id:05d}.png')
        # state_filename = os.path.join(f'{file_path}\\states', f'board_{image_id:05d}.json')
        image_filename = f'images/board_{image_id:05d}.png'
        state_filename = f'states/board_{image_id:05d}.json'

        # 生成游戏局面
        print(f"Generating image {image_id}...")
        grid = generate_uttt_game(plot_level=plot_level)
        grid.save_image(image_filename)
        print(f"Image {image_id} generated")

        # 保存状态
        game_state = grid.get_game_state()
        try:
            with open(state_filename, 'w') as f:
                json.dump(game_state, f, ensure_ascii=False, indent=4)
        except:
            try:
                new_state_filename = os.path.join(file_path, state_filename)
                with open(new_state_filename, 'w') as f:
                    json.dump(game_state, f, ensure_ascii=False, indent=4)
            except:
                print(f"Failed to save state file for image {image_id}")

        # 生成题目1
        data_id1 = f"ultra_tictactoe-data-{image_id:05d}-{data_id:05d}"
        plot_id1 = f"ultra_tictactoe-plot-{image_id:05d}-{data_id:05d}"
        question_data1 = generate_question_1(data_id1, plot_id1, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data1)
        print(f"Question 1 generated for plot {image_id}")
        data_id += 1

        # 生成题目2
        data_id2 = f"ultra_tictactoe-data-{image_id:05d}-{data_id:05d}"
        plot_id2 = f"ultra_tictactoe-plot-{image_id:05d}-{data_id:05d}"
        question_data2 = generate_question_2(data_id2, plot_id2, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data2)
        print(f"Question 2 generated for plot {image_id}")
        data_id += 1

        # 生成题目3
        data_id3 = f"ultra_tictactoe-data-{image_id:05d}-{data_id:05d}"
        plot_id3 = f"ultra_tictactoe-plot-{image_id:05d}-{data_id:05d}"
        question_data3 = generate_question_3(data_id3, plot_id3, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data3)
        print(f"Question 3 generated for plot {image_id}")
        data_id += 1

        # 生成题目4
        data_id4 = f"ultra_tictactoe-data-{image_id:05d}-{data_id:05d}"
        plot_id4 = f"ultra_tictactoe-plot-{image_id:05d}-{data_id:05d}"
        question_data4 = generate_question_4(data_id4, plot_id4, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data4)
        print(f"Question 4 generated for plot {image_id}")
        data_id += 1

        # 生成题目5
        data_id5 = f"ultra_tictactoe-data-{image_id:05d}-{data_id:05d}"
        plot_id5 = f"ultra_tictactoe-plot-{image_id:05d}-{data_id:05d}"
        question_data5 = generate_question_5(data_id5, plot_id5, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data5)
        print(f"Question 5 generated for plot {image_id}")
        data_id += 1

        # 生成题目6
        data_id6 = f"ultra_tictactoe-data-{image_id:05d}-{data_id:05d}"
        plot_id6 = f"ultra_tictactoe-plot-{image_id:05d}-{data_id:05d}"
        question_data6 = generate_question_6(data_id6, plot_id6, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data6)
        print(f"Question 6 generated for plot {image_id}")
        data_id += 1

        # 生成题目7
        data_id7 = f"ultra_tictactoe-data-{image_id:05d}-{data_id:05d}"
        plot_id7 = f"ultra_tictactoe-plot-{image_id:05d}-{data_id:05d}"
        question_data7 = generate_question_7(data_id7, plot_id7, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data7)
        print(f"Question 7 generated for plot {image_id}")
        data_id += 1

        image_id += 1

    return all_questions, image_id, data_id

def generate_image_question(plot_level="Easy", num_images=1, start_image_id=1, start_data_id=1):
    os.makedirs(os.path.join(file_path, 'images'), exist_ok=True)
    os.makedirs(os.path.join(file_path, 'states'), exist_ok=True)
    
    # 生成题目数据
    all_questions, image_id, data_id = generate_questions_for_plot_level(plot_level, num_images, start_image_id, start_data_id)
    return all_questions, image_id, data_id

if __name__ == '__main__':
    file_path = 'ultra_tictactoe_dataset'
    os.makedirs(file_path, exist_ok=True)

    file_name = 'data.json'
    data_path = os.path.join(file_path, file_name)

    # 生成题目数据
    easy_image_num = 1
    medium_image_num = 1
    hard_image_num = 1


    all_questions = []

    print("Generating questions for Easy level...")
    question_data_easy, image_id, data_id = generate_image_question(plot_level="Easy", num_images=easy_image_num)
    all_questions.extend(question_data_easy)
    # 保存 uttt_data.json 文件；多次保存，防止程序中途退出导致数据丢失
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=4)
    print("Easy level questions generated.")
    print("----------------------------------------")

    print("Generating questions for Medium level...")
    question_data_medium, image_id, data_id = generate_image_question(plot_level="Medium", num_images=medium_image_num, start_image_id=image_id, start_data_id=data_id)
    all_questions.extend(question_data_medium)
    # 保存 uttt_data.json 文件；多次保存，防止程序中途退出导致数据丢失
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=4)
    print("Medium level questions generated.")
    print("----------------------------------------")

    print("Generating questions for Hard level...")
    question_data_hard, image_id, data_id = generate_image_question(plot_level="Hard", num_images=hard_image_num, start_image_id=image_id, start_data_id=data_id)
    all_questions.extend(question_data_hard)
    # 保存 uttt_data.json 文件；多次保存，防止程序中途退出导致数据丢失
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=4)
    print("Hard level questions generated.")
    
    # 关闭 pygame
    pygame.quit()
    sys.exit()