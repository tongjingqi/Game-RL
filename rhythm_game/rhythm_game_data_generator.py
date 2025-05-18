import pygame
import random
import sys
import os
import json

# 初始化 pygame
pygame.init()

# 常量定义
MARGIN_X = 30
MARGIN_Y_BOTTOM = 30
BLOCK_SCALE = 0.8
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PINK = (255, 105, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)

# 颜色名称映射
COLOR_NAMES = {
    YELLOW: "yellow",
    GREEN: "green",
    BLUE: "blue",
    PINK: "pink",
    GREY: "grey"
}

# 块类型映射
BLOCK_TYPE_NAMES = {
    "yellow": "Click",
    "green": "Reverse",
    "blue": "Snake Body",
    "pink": "Snake Head",
    "grey": "Snake Tail",
    "white": "Non-type"
}

# 定义不同难度级别的表格大小
GRID_SIZES = {
    "Easy": {"row_num": 15, "col_num": 4},
    "Medium": {"row_num": 15, "col_num": 6},
    "Hard": {"row_num": 20, "col_num": 6}
}

# 游戏描述
game_explanation = """Now I'll give you a picture, which shows a screenshot of a rhythm game, in which there are operation blocks of various colors. In this game, the operation blocks will fall at a speed of 1 cell/second. At the same time, you can select a column to place your finger (you cannot move your finger after selecting it), and click the operation blocks in the column that fall to the first row to score points (of course, you can also choose not to click any column, which will not affect the falling of the operation blocks). 
For the operation blocks, we divide them into 3 categories, including Click blocks, Reverse blocks, and Snake blocks, as follows: 
1. Click blocks are yellow, occupy 1 cell, and you can get 10 points by clicking them. 
2. Reverse blocks are green, occupy 1 cell, and you can get 15 points by clicking them. It should be noted that after you click the Reverse block, the entire game situation will **reverse left and right**, but your finger position **will not** change accordingly. 
3. A Snake block occupies 2 or more consecutive cells in a column, and its first cell (called Snake Head block) is pink, its last cell (called Snake Tail block) is grey, and the middle cells (called Snake Body blocks, if any) are blue. Only when you click on **all cells** occupied by the snake block can you score points. The score is related to the length $l$ (including the head and tail) of the snake block. The specific score is $l \cdot (2l + 7)$. 
Now I will give you a question about the game. Please extract information from the picture I give you, think carefully, reason and answer: 
"""

# 删除开头的换行
game_explanation = game_explanation.strip()

class RhythmGameGrid:
    def __init__(self, width, height, rows, cols):
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.screen = pygame.Surface((width + MARGIN_X, height + MARGIN_Y_BOTTOM))
        self.font = pygame.font.SysFont(None, 24)
        self.occupied_spaces = []
        self.screen.fill(WHITE)
        self.cell_width = width // cols
        self.cell_height = height // rows
        self.block_width = self.cell_width * BLOCK_SCALE
        self.block_height = self.cell_height * BLOCK_SCALE

    def draw_grid(self):
        for i in range(self.rows):
            text = self.font.render(str(self.rows - i), True, BLACK)
            self.screen.blit(text, (5, i * self.cell_height + self.cell_height // 2 - text.get_height() // 2))
            pygame.draw.line(self.screen, BLACK, (MARGIN_X, i * self.cell_height), (self.width + MARGIN_X, i * self.cell_height))
        for i in range(self.cols):
            text = self.font.render(str(i + 1), True, BLACK)  # col 从1开始计数
            self.screen.blit(text, ((i + 0.5) * self.cell_width + MARGIN_X - text.get_width() // 2, self.height + 5))
        for i in range(1, self.cols):
            pygame.draw.line(self.screen, BLACK, (i * self.cell_width + MARGIN_X, 0), (i * self.cell_width + MARGIN_X, self.height))

    def add_block(self, color, col, start_row, length, block_type, head_color=None, tail_color=None):
        for idx, row in enumerate(range(start_row, min(self.rows + 1, start_row + length))):
            if idx == 0 and head_color:
                block_label = f"{block_type} Head"
                display_color = head_color
            elif idx == length - 1 and tail_color:
                block_label = f"{block_type} Tail"
                display_color = tail_color
            else:
                if block_type == "蛇块 (Snake)":
                    block_label = f"{block_type} Body"
                else:
                    block_label = block_type
                display_color = color
            self.occupied_spaces.append((row, col, block_label))
            rect_x = (col - 1) * self.cell_width + MARGIN_X + (self.cell_width - self.block_width) / 2
            rect_y = (self.rows - row) * self.cell_height + (self.cell_height - self.block_height) / 2
            pygame.draw.rect(self.screen, display_color, (rect_x, rect_y, self.block_width, self.block_height))

    def add_random_blocks(self, color, count, block_type, min_length=1, max_length=1, head_color=None, tail_color=None):
        for _ in range(count):
            while True:
                col = random.randint(1, self.cols)
                start_row = random.randint(1, self.rows - max_length + 1)
                length = random.randint(min_length, max_length)
                end_row = start_row + length - 1
                is_space_available = True
                for row in range(start_row, end_row + 1):
                    if (row, col) in [(r, c) for r, c, _ in self.occupied_spaces]:
                        is_space_available = False
                        break
                if is_space_available:
                    self.add_block(color, col, start_row, length, block_type, head_color, tail_color)
                    break

    def save_image(self, filename):
        # pygame.image.save(self.screen, filename)
        new_filename = os.path.join(file_path, filename)
        pygame.image.save(self.screen, new_filename)

    def get_game_state(self):
        game_state = {
            "rows": self.rows,
            "cols": self.cols,
            "blocked_cell_num": len(self.occupied_spaces),
            "block_info": []
        }
        for row, col, block_type in self.occupied_spaces:
            color = None
            if "Head" in block_type:
                color = COLOR_NAMES[PINK]
            elif "Tail" in block_type:
                color = COLOR_NAMES[GREY]
            elif "Body" in block_type:
                color = COLOR_NAMES[BLUE]
            elif block_type == "单点块 (Click)":
                color = COLOR_NAMES[YELLOW]
            elif block_type == "反转块 (Flip)":
                color = COLOR_NAMES[GREEN]
            game_state["block_info"].append({
                "row": row,
                "col": col,
                "color": color
            })
        return game_state

def generate_rhythm_game(width=400, height=500, plot_level="Easy"):
    grid_size = GRID_SIZES[plot_level]
    rows = grid_size["row_num"]
    cols = grid_size["col_num"]

    grid = RhythmGameGrid(width, height, rows, cols)
    grid.draw_grid()
    total_blocks = (rows * cols) // 2
    proportions = {
        "单点块 (Click)": 7,
        "反转块 (Flip)": 4,
        "蛇块 (Snake)": 3
    }
    total_proportion = sum(proportions.values())
    single_click_count = total_blocks * proportions["单点块 (Click)"] // total_proportion
    reverse_count = total_blocks * proportions["反转块 (Flip)"] // total_proportion
    snake_count = total_blocks - single_click_count - reverse_count
    print(f"单点块 (Click): {single_click_count}, 反转块 (Flip): {reverse_count}, 蛇块 (Snake): {snake_count}")
    
    # 调整顺序：先添加蛇块，再添加点击块，最后添加反转块
    grid.add_random_blocks(BLUE, snake_count, "蛇块 (Snake)", min_length=2, max_length=5, head_color=PINK, tail_color=GREY)
    print("Snake blocks added")
    grid.add_random_blocks(YELLOW, single_click_count, "单点块 (Click)", min_length=1, max_length=1)
    print("Click blocks added")
    grid.add_random_blocks(GREEN, reverse_count, "反转块 (Flip)", min_length=1, max_length=1)
    print("Reverse blocks added")
    
    return grid

def find_snake_length(game_state, head_position):
    """
    找到以head_position为首（即最下端）的蛇块长度
    :param game_state: 游戏状态
    :param head_position: 蛇头位置 (row, col)
    :return: 蛇块长度
    """
    row, col = head_position
    length = 2  # 头、尾
    current_row = row + 1
    # 向上查找蛇块长度
    while current_row <= game_state["rows"]:
        block_info = next((info for info in game_state["block_info"] if info["row"] == current_row and info["col"] == col), None)
        if block_info and block_info["color"] == COLOR_NAMES[BLUE]:
            length += 1
            current_row += 1
        else:
            break
    return length

def calculate_points_for_column(game_state, select_col, reverse_time=0):
    """
    计算选择某一列点击时的得分
    :param game_state: 游戏状态
    :param select_col: 选择的列
    :param reverse_time: 反转次数，默认为0
    :return: 坐标列表、块类型列表、分数列表
    """
    row = 1
    col = select_col
    coordinates = []
    block_types = []
    points_list = []
    final_point = 0
    col_num = game_state["cols"]

    while row <= game_state["rows"]:
        block_info = next((info for info in game_state["block_info"] if info["row"] == row and info["col"] == col), None)
        if block_info:
            block_color = block_info["color"]
            block_type = BLOCK_TYPE_NAMES[block_color]
            points = 0

            coordinates.append((row, col))
            block_types.append(block_type)

            if block_type == "Click":
                points = 10
                row += 1
            elif block_type == "Reverse":
                points = 15
                col = col_num - col + 1  # 反转列位置            
                row += (reverse_time + 1)  # 额外跳过reverse_skip个块
            elif block_type == "Snake Head":
                length = find_snake_length(game_state, (row, col))
                points = length * (2 * length + 7)
                row += length
            elif block_type == "Snake Body":
                length = find_snake_length(game_state, (row, col))  # 直接跳过整个蛇块
                row += length
            elif block_type == "Snake Tail":
                row += 1

            points_list.append(points)
            final_point += points
        else:
            row += 1

    return coordinates, block_types, points_list, final_point

def generate_question_1(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Easy",
        "qa_type": "Target Perception",
        "question_id": 1,
        "question_description": "Find the type of the block in a given coordinate.",
        "question": game_explanation + " Which type of block does row {row} and column {col} in the image belong to? Options: {option_list}",
        "answer": "{option_number}",
        "analysis": "The cell at row {row} and column {col} in the image is {block_color}, which means it is a {block_type} block. So, the answer is {option_number}",
        "options": ["Non-type", "Click", "Reverse", "Snake Head", "Snake Body", "Snake Tail"]
    }
    # 随机选择一个格子
    row = random.randint(1, game_state["rows"])
    col = random.randint(1, game_state["cols"])
    # 获取该格子的块类型和颜色
    block_info = next((info for info in game_state["block_info"] if info["row"] == row and info["col"] == col), None)
    if block_info:
        block_color = block_info["color"]
        block_type = BLOCK_TYPE_NAMES[block_color]
    else:
        block_color = "white"
        block_type = "Non-type"
    # 确定正确答案的序号
    options = question_template["options"]
    option_number = options.index(block_type) + 1
    # 处理选项列表，添加序号
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options)])
    # 填充模板
    question_template["question"] = question_template["question"].format(row=row, col=col, option_list=option_list)
    question_template["answer"] = question_template["answer"].format(option_number=option_number)
    question_template["analysis"] = question_template["analysis"].format(
        row=row,
        col=col,
        block_color=block_color,
        block_type=block_type,
        option_number=option_number
    )
    return question_template

def generate_question_2(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Easy",
        "qa_type": "Target Perception",
        "question_id": 2,
        "question_description": "Find the percentage of cells with blocks, retaining 3 significant figures.",
        "question": game_explanation + " What percentage of the grid in the current image is occupied by the operation blocks? The answer is expressed as a decimal, retaining 3 significant figures.",
        "answer": "{current_answer}",
        "analysis": "There are {row_num} rows and {col_num} columns in the grid, which means there are {row_num} * {col_num} = {cell_num} cells in total. {counting_row_cells}\nIn total, there are {adding_blocks} = {blocked_cell_num} cells occupied by blocks in the image. So, the answer is {blocked_cell_num} / {cell_num} = {current_answer}"
    }

    row_num = game_state["rows"]
    col_num = game_state["cols"]
    blocked_cell_num = game_state["blocked_cell_num"]
    cell_num = row_num * col_num
    # current_answer = round(blocked_cell_num / cell_num, 3)
    current_answer = blocked_cell_num / cell_num
    current_answer = f"{current_answer:.3f}"

    # 生成每一行的操作块数量描述
    counting_row_cells = []
    blocked_cell_num_list = []
    for row in range(1, row_num + 1):
        blocks_in_row = len([info for info in game_state["block_info"] if info["row"] == row])
        blocked_cell_num_list.append(blocks_in_row)
        counting_row_cells.append(f"In row {row}, there are {blocks_in_row} blocks.")
    
    adding_blocks = " + ".join(map(str, blocked_cell_num_list))
    counting_row_cells_str = "\n".join(counting_row_cells)

    # 填充模板
    question_template["answer"] = question_template["answer"].format(current_answer=current_answer)
    question_template["analysis"] = question_template["analysis"].format(
        row_num=row_num,
        col_num=col_num,
        cell_num=cell_num,
        counting_row_cells=counting_row_cells_str,
        adding_blocks=adding_blocks,
        blocked_cell_num=blocked_cell_num,
        current_answer=current_answer
    )

    return question_template

def generate_question_3(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Medium",
        "qa_type": "State Prediction",
        "question_id": 3,
        "question_description": "Find the length of Snake block headed by a given coordinate after given sconds.",
        "question": game_explanation + " Without selecting any column to click, what is the length of the snake block headed (which means being the lower end) by {head_position_after} after {time} second(s)? Options: {option_list}",
        "answer": "{option_number}",
        "analysis": "Because the blocks fall at the speed of 1 cell/second, before {time} second(s), the head cell of that Snake block should be at {head_position_before}. From the image we can see that the Snake block starts from {head_position_before} occupies {length} cells. So, the answer is {option_number}",
        "options": ["2", "3", "4", "5"]
    }

    # 找到所有蛇头块
    snake_heads = [(info["row"], info["col"]) for info in game_state["block_info"] if info["color"] == COLOR_NAMES[PINK]]

    if not snake_heads:
        # 如果没有蛇头块，返回None
        return None

    # 随机选择一个蛇头块，确保 row_before > 1
    while True:
        head_position_before = random.choice(snake_heads)
        row_before, col_before = head_position_before
        if row_before > 1:
            break

    # 随机选择一个时间k，确保y_1 = y_0 - k > 0
    k = random.randint(1, row_before - 1)
    row_after = row_before - k

    # 计算蛇块长度
    length = find_snake_length(game_state, head_position_before)

    # 填充模板
    question_template["question"] = question_template["question"].format(
        head_position_after=f"({row_after}, {col_before})",
        time=k,
        option_list=" ".join([f"{i+1}. {option}" for i, option in enumerate(question_template["options"])])
    )
    question_template["answer"] = question_template["answer"].format(option_number=question_template["options"].index(str(length)) + 1)
    question_template["analysis"] = question_template["analysis"].format(
        time=k,
        head_position_before=f"({row_before}, {col_before})",
        length=length,
        option_number=question_template["options"].index(str(length)) + 1
    )

    return question_template

def generate_question_4(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Medium",
        "qa_type": "State Prediction",
        "question_id": 4,
        "question_description": "Find the final point of choosing a given column to click.",
        "question": game_explanation + " While selecting column {select_col} to click, how many points will you get? Options: {option_list}",
        "answer": "{option_number}",
        "analysis": "We count from bottom to top.\n{counting_procedure}So, the final point is {adding_points} = {final_point}, the answer is {option_number}",
        "options": []
    }
    # 随机选择一个列
    select_col = random.randint(1, game_state["cols"])
    # 计算选择该列点击时的得分
    coordinates, block_types, points_list, final_point = calculate_points_for_column(game_state, select_col)

    counting_procedure = []
    for (row, col), block_type, points in zip(coordinates, block_types, points_list):
        sentence = f"At ({row}, {col}), there is a {block_type} block"
        if block_type == "Snake Head":
            length = find_snake_length(game_state, (row, col))
            sentence += f", the Snake block's length is {length}"
        if block_type not in ["Non-type", "Snake Body", "Snake Tail"]:
            sentence += f", so we get {points} points."
        else:
            sentence += ", so we skip it."
        if block_type == "Reverse":
            sentence += " Also, the grid will reverse after clicking it."

        counting_procedure.append(sentence)

    # 生成选项列表
    options_made = [str(final_point)]
    random_range = 15
    option_count = 8
    for _ in range(option_count - 1):
        offset = random.randint(-random_range, random_range)  # 随机上下浮动
        while str(final_point + offset) in options_made:
            offset = random.randint(-random_range, random_range)
        options_made.append(str(final_point + offset))
    random.shuffle(options_made)
    option_number = options_made.index(str(final_point)) + 1

    # 处理选项列表，添加序号
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options_made)])

    # 填充模板
    question_template["question"] = question_template["question"].format(select_col=select_col, option_list=option_list)
    question_template["answer"] = question_template["answer"].format(option_number=option_number)
    question_template["analysis"] = question_template["analysis"].format(
        counting_procedure="\n".join(counting_procedure) + "\n",
        adding_points=" + ".join(map(str, points_list)),
        final_point=final_point,
        option_number=option_number
    )
    question_template["options"] = options_made
    return question_template

def generate_question_5(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Medium",
        "qa_type": "State Prediction",
        "question_id": 5,
        "question_description": "Find the final point of choosing a given column to click when it takes 1 second to reverse the grid.",
        "question": game_explanation + " Now it takes 1 second to reverse the grid, during which the blocks will still be falling, but you can't click them. While selecting column {select_col} to click, how many points will you get? Options: {option_list}",
        "answer": "{option_number}",
        "analysis": "We count from bottom to top.\n{counting_procedure}So, the final point is {adding_points} = {final_point}, the answer is {option_number}",
        "options": []
    }
    reverse_time = 1 # 反转时间
    # 随机选择一个列
    select_col = random.randint(1, game_state["cols"])
    # 计算选择该列点击时的得分
    coordinates, block_types, points_list, final_point = calculate_points_for_column(game_state, select_col, reverse_time=reverse_time)

    counting_procedure = []
    for (row, col), block_type, points in zip(coordinates, block_types, points_list):
        sentence = f"At ({row}, {col}), there is a {block_type} block"
        if block_type == "Snake Head":
            length = find_snake_length(game_state, (row, col))
            sentence += f", the Snake block's length is {length}"
        if block_type not in ["Non-type", "Snake Body", "Snake Tail"]:
            sentence += f", so we get {points} points."
        else:
            sentence += ", so we skip it."
        if block_type == "Reverse":
            sentence += f" Also, the grid will reverse after clicking it, and we will skip {reverse_time} row."

        counting_procedure.append(sentence)

    # 生成选项列表
    options_made = [str(final_point)]
    random_range = 15
    option_count = 8
    for _ in range(option_count - 1):
        offset = random.randint(-random_range, random_range)  # 随机上下浮动
        while str(final_point + offset) in options_made:
            offset = random.randint(-random_range, random_range)
        options_made.append(str(final_point + offset))
    random.shuffle(options_made)
    option_number = options_made.index(str(final_point)) + 1

    # 处理选项列表，添加序号
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options_made)])

    # 填充模板
    question_template["question"] = question_template["question"].format(select_col=select_col, option_list=option_list)
    question_template["answer"] = question_template["answer"].format(option_number=option_number)
    question_template["analysis"] = question_template["analysis"].format(
        counting_procedure="\n".join(counting_procedure) + "\n",
        adding_points=" + ".join(map(str, points_list)),
        final_point=final_point,
        option_number=option_number
    )
    question_template["options"] = options_made
    return question_template

def generate_question_6(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Hard",
        "qa_type": "Strategy Optimization",
        "question_id": 6,
        "question_description": "Find choosing which column to click can get the highest score.",
        "question": game_explanation + " Which column(s) should I choose to click to get the highest final score? Options: {option_list}",
        "answer": "{option_numbers}",
        "analysis": "{counting_procedure}We can see that when choosing column(s) {max_col}, the final point is the highest, being {max_point}. So, the answer is {option_numbers}",
        "options": []
    }

    cols = game_state["cols"]
    max_score = -1
    max_col = []
    all_col_options = []
    analysis_texts = []

    for col in range(1, cols + 1):
        coordinates, block_types, points_list, final_point = calculate_points_for_column(game_state, col)

        analysis_texts.append(f"If we choose column {col}, we will click {' -> '.join([f'{bt} at ({r}, {c})' for (r, c), bt in zip(coordinates, block_types)])}. The final point is {final_point}.")
        all_col_options.append(f"{col}")

        if final_point > max_score:
            max_score = final_point
            max_col = [col]
        elif final_point == max_score:
            max_col.append(col)

    # 生成选项列表
    options_made = all_col_options.copy()
    # random.shuffle(options_made)

    # 处理选项列表，添加序号
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options_made)])

    # 找到最高得分列的选项序号
    option_numbers = [str(options_made.index(str(c)) + 1) for c in max_col]
    option_numbers_str = ", ".join(option_numbers)

    # 填充模板
    question_template["question"] = question_template["question"].format(option_list=option_list)
    question_template["answer"] = question_template["answer"].format(option_numbers=option_numbers_str)
    question_template["analysis"] = question_template["analysis"].format(
        counting_procedure="\n".join(analysis_texts) + "\n",
        max_col=", ".join(map(str, max_col)),
        max_point=max_score,
        option_numbers=option_numbers_str
    )
    question_template["options"] = options_made

    return question_template

def generate_question_7(data_id, plot_id, image_filename, state_filename, game_state, plot_level):
    # 定义题目模板
    question_template = {
        "data_id": data_id,
        "image": image_filename,
        "state": state_filename,
        "plot_level": plot_level,
        "qa_level": "Hard",
        "qa_type": "Strategy Optimization",
        "question_id": 7,
        "question_description": "Find choosing which column to click can get the highest score when it takes 1 second to reverse the grid.",
        "question": game_explanation + " Now it takes 1 second to reverse the grid, during which the blocks will still be falling, but you can't cilck them. Which column(s) should I choose to click to get the highest final score? Options: {option_list}",
        "answer": "{option_numbers}",
        "analysis": "{counting_procedure}We can see that when choosing column(s) {max_col}, the final point is the highest, being {max_point}. So, the answer is {option_numbers}",
        "options": []
    }

    cols = game_state["cols"]
    max_score = -1
    max_col = []
    all_col_options = []
    analysis_texts = []

    for col in range(1, cols + 1):
        coordinates, block_types, points_list, final_point = calculate_points_for_column(game_state, col, reverse_time=1)

        analysis_texts.append(f"If we choose column {col}, we will click {' -> '.join([f'{bt} at ({r}, {c})' for (r, c), bt in zip(coordinates, block_types)])}. The final point is {final_point}.")
        all_col_options.append(f"{col}")

        if final_point > max_score:
            max_score = final_point
            max_col = [col]
        elif final_point == max_score:
            max_col.append(col)

    # 生成选项列表
    options_made = all_col_options.copy()
    # random.shuffle(options_made)

    # 处理选项列表，添加序号
    option_list = " ".join([f"{i+1}. {option}" for i, option in enumerate(options_made)])

    # 找到最高得分列的选项序号
    option_numbers = [str(options_made.index(str(c)) + 1) for c in max_col]
    option_numbers_str = ", ".join(option_numbers)

    # 填充模板
    question_template["question"] = question_template["question"].format(option_list=option_list)
    question_template["answer"] = question_template["answer"].format(option_numbers=option_numbers_str)
    question_template["analysis"] = question_template["analysis"].format(
        counting_procedure="\n".join(analysis_texts) + "\n",
        max_col=", ".join(map(str, max_col)),
        max_point=max_score,
        option_numbers=option_numbers_str
    )
    question_template["options"] = options_made

    return question_template

def generate_questions_for_plot_level(plot_level="Easy", num_images=1, start_image_id=1, start_data_id=1):
    all_questions = []
    grid_sizes = GRID_SIZES[plot_level]
    rows = grid_sizes["row_num"]
    cols = grid_sizes["col_num"]

    image_id = start_image_id
    data_id = start_data_id

    for i in range(num_images):
        # image_filename = os.path.join('images', f'board_{image_id:05d}.png')
        image_filename = f'images/board_{image_id:05d}.png'
        # state_filename = os.path.join('states', f'board_{image_id:05d}.json')
        state_filename = f'states/board_{image_id:05d}.json'
        
        # 生成游戏局面
        grid = generate_rhythm_game(width=400, height=500, plot_level=plot_level)
        grid.save_image(image_filename)
        print(f"Image {image_id} generated")
        
        # 保存状态
        game_state = grid.get_game_state()
        # with open(state_filename, 'w') as f:
        #     json.dump(game_state, f, ensure_ascii=False, indent=4)
        new_state_filename = os.path.join(file_path, state_filename)
        with open(new_state_filename, 'w') as f:
            json.dump(game_state, f, ensure_ascii=False, indent=4)
        
        # 生成题目1
        data_id1 = f"rhythm_game-data-{image_id:05d}-{data_id:05d}"
        plot_id1 = f"rhythm_game-plot-{image_id:05d}-{data_id:05d}"
        question_data1 = generate_question_1(data_id1, plot_id1, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data1)
        print(f"Question 1 generated for plot {image_id}")
        data_id += 1
        
        # 生成题目2
        data_id2 = f"rhythm_game-data-{image_id:05d}-{data_id:05d}"
        plot_id2 = f"rhythm_game-plot-{image_id:05d}-{data_id:05d}"
        question_data2 = generate_question_2(data_id2, plot_id2, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data2)
        print(f"Question 2 generated for plot {image_id}")
        data_id += 1
        
        # 生成题目3
        data_id3 = f"rhythm_game-data-{image_id:05d}-{data_id:05d}"
        plot_id3 = f"rhythm_game-plot-{image_id:05d}-{data_id:05d}"
        question_data3 = generate_question_3(data_id3, plot_id3, image_filename, state_filename, game_state, plot_level)
        if question_data3: # 只有当没有蛇头块时才会没有题目
            all_questions.append(question_data3)
        print(f"Question 3 generated for plot {image_id}")
        data_id += 1
        
        # 生成题目4
        data_id4 = f"rhythm_game-data-{image_id:05d}-{data_id:05d}"
        plot_id4 = f"rhythm_game-plot-{image_id:05d}-{data_id:05d}"
        question_data4 = generate_question_4(data_id4, plot_id4, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data4)
        print(f"Question 4 generated for plot {image_id}")
        data_id += 1
        
        # 生成题目5
        data_id5 = f"rhythm_game-data-{image_id:05d}-{data_id:05d}"
        plot_id5 = f"rhythm_game-plot-{image_id:05d}-{data_id:05d}"
        question_data5 = generate_question_5(data_id5, plot_id5, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data5)
        print(f"Question 5 generated for plot {image_id}")
        data_id += 1
        
        # 生成题目6
        data_id6 = f"rhythm_game-data-{image_id:05d}-{data_id:05d}"
        plot_id6 = f"rhythm_game-plot-{image_id:05d}-{data_id:05d}"
        question_data6 = generate_question_6(data_id6, plot_id6, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data6)
        print(f"Question 6 generated for plot {image_id}")
        data_id += 1
        
        # 生成题目7
        data_id7 = f"rhythm_game-data-{image_id:05d}-{data_id:05d}"
        plot_id7 = f"rhythm_game-plot-{image_id:05d}-{data_id:05d}"
        question_data7 = generate_question_7(data_id7, plot_id7, image_filename, state_filename, game_state, plot_level)
        all_questions.append(question_data7)
        print(f"Question 7 generated for plot {image_id}")
        data_id += 1

        image_id += 1
    
    return all_questions, image_id, data_id

def generate_image_question(plot_level="Easy", num_images=1, start_image_id=1, start_data_id=1):
    # 确保文件夹存在
    os.makedirs('images', exist_ok=True)
    os.makedirs('states', exist_ok=True)
    
    # 生成题目数据
    all_questions, image_id, data_id = generate_questions_for_plot_level(plot_level, num_images, start_image_id, start_data_id)

    return all_questions, image_id, data_id

    # # 保存 rg_data.json 文件
    # with open('rg_data.json', 'w', encoding='utf-8') as f:
    #     json.dump(all_questions, f, ensure_ascii=False, indent=4)
    
    # # 关闭 pygame
    # pygame.quit()
    # sys.exit()

if __name__ == '__main__':
    file_path = 'rhythm_game_dataset'
    os.makedirs(file_path, exist_ok=True)

    file_name = 'data.json'
    data_path = os.path.join(file_path, file_name)

    easy_image_num = 24
    medium_image_num = 24
    hard_image_num = 24

    all_questions = []

    print("Generating questions for Easy level...")
    question_data_easy, image_id, data_id = generate_image_question(plot_level="Easy", num_images=easy_image_num)
    all_questions.extend(question_data_easy)

    # 保存 rg_data.json 文件；多次保存，防止程序中途退出导致数据丢失
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=4)


    print("Generating questions for Medium level...")
    question_data_medium, image_id, data_id = generate_image_question(plot_level="Medium", num_images=medium_image_num, start_image_id=image_id, start_data_id=data_id)
    all_questions.extend(question_data_medium)

    # 保存 rg_data.json 文件；多次保存，防止程序中途退出导致数据丢失
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=4)



    print("Generating questions for Hard level...")
    question_data_hard, image_id, data_id = generate_image_question(plot_level="Hard", num_images=hard_image_num, start_image_id=image_id, start_data_id=data_id)
    all_questions.extend(question_data_hard)

    # 保存 rg_data.json 文件；多次保存，防止程序中途退出导致数据丢失
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=4)

    
    # 关闭 pygame
    pygame.quit()
    sys.exit()