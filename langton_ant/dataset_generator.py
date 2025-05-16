import pygame
import json
import os
import random
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Any
import copy

# 文件路径设置
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(CURRENT_DIR, "images")
STATES_DIR = os.path.join(CURRENT_DIR, "states")
DATASET_FILE = os.path.join(CURRENT_DIR, "data.json")

# 常量定义
GRID_SIZES = {
    "Easy": 5,
    "Medium": 9,
    "Hard": 13
}

# 动态计算CELL_SIZE，确保总大小不超过560*560
def calculate_cell_size(grid_size: int) -> Tuple[int, int]:
    """根据网格大小动态计算单元格大小和边距"""
    max_size = 550
    min_margin = 30  # 确保至少有30像素的边距用于坐标标签
    
    # 计算可用空间
    available_space = max_size - (2 * min_margin)
    # 计算单元格大小
    cell_size = min(available_space // grid_size, 50)  # 限制最大单元格大小为50
    # 调整边距以使图像居中
    margin = (max_size - (cell_size * grid_size)) // 2
    
    return cell_size, margin


def init_grid(grid_size: int) -> List[List[int]]:
    """初始化网格，随机填充一些黑色方块"""
    grid = [[0] * grid_size for _ in range(grid_size)]
    # 根据难度设置不同的初始黑色方块数量
    if grid_size == 5:  # Easy
        black_cells = random.randint(2, 12)
    elif grid_size == 9:  # Medium
        black_cells = random.randint(8, 40)
    else:  # Hard
        black_cells = random.randint(16, 80)
    
    # 随机放置黑色方块
    for _ in range(black_cells):
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        grid[x][y] = 1
    
    return grid

DATASET_SIZE = 3  # 每个难度级别的样本数量

# Game rule description
GAME_RULES = """In Langton's Ant, we have a grid where each cell is either white or black. A red arrow represents an ant, showing its current position and direction. The ant follows these simple rules:
1. If the ant is on a white cell, it turns right 90 degrees, changes the cell to black, and moves forward one step
2. If the ant is on a black cell, it turns left 90 degrees, changes the cell to white, and moves forward one step
3. If the ant would move off the grid, it wraps around to the opposite side (using modulo with grid size)
The coordinates system: The top-left cell is (0,0), with x increasing downward and y increasing rightward."""

# 问题类型和难度映射
MCQ_QUESTION_TYPES = {
    1: {
        "type": "StateInfo",
        "description": "Identify the current position and direction of the ant",
        "qa_level": "Easy"
    },
    2: {
        "type": "ActionOutcome",
        "description": "Predict the ant's position and direction after several steps",
        "qa_level": "Medium"
    }
}

FILL_QUESTION_TYPES = {
    3: {
        "type": "ActionOutcome",
        "description": "Predict the color state of a specific cell after several steps",
        "qa_level": "Hard"
    }
}

# 创建必要的目录结构，直接在当前工作目录创建
def create_directories() -> None:
    """创建必要的目录结构"""
    os.makedirs(IMAGES_DIR, exist_ok=True)  # 当前工作目录下创建 images 文件夹
    os.makedirs(STATES_DIR, exist_ok=True)  # 当前工作目录下创建 states 文件夹
    
    # 如果目录已存在，清空其中的内容
    for dir_path in [IMAGES_DIR, STATES_DIR]:
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error: {e}")

def init_ant(grid_size: int) -> Dict[str, Any]:
    """初始化蚂蚁位置和方向"""
    return {
        "x": random.randint(0, grid_size - 1),
        "y": random.randint(0, grid_size - 1),
        "direction": random.choice(["up", "right", "down", "left"])
    }

def save_board_state(grid: List[List[int]], ant: Dict[str, Any], state_path: str) -> None:
    """保存棋盘状态到JSON文件"""
    state = {
        "grid": grid,
        "ant": ant
    }
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)

def save_board_image(screen: pygame.Surface, image_path: str) -> None:
    """保存棋盘图片"""
    pygame.image.save(screen, image_path)

def update_ant_state(grid: List[List[int]], ant: Dict[str, Any], grid_size: int) -> None:
    """更新蚂蚁状态"""
    x, y = ant["x"], ant["y"]
    direction = ant["direction"]
    directions = ["up", "right", "down", "left"]
    
    # 翻转颜色并改变方向
    current_color = grid[x][y]
    grid[x][y] = 1 - current_color
    
    if current_color == 0:  # 白色右转
        direction = directions[(directions.index(direction) + 1) % 4]
    else:  # 黑色左转
        direction = directions[(directions.index(direction) - 1) % 4]
    
    # 移动蚂蚁
    if direction == "up":
        x = (x - 1) % grid_size
    elif direction == "right":
        y = (y + 1) % grid_size
    elif direction == "down":
        x = (x + 1) % grid_size
    elif direction == "left":
        y = (y - 1) % grid_size
    
    ant["x"], ant["y"], ant["direction"] = x, y, direction

def draw_board(screen: pygame.Surface, grid: List[List[int]], ant: Dict[str, Any], 
               grid_size: int, cell_size: int, margin: int) -> None:
    """绘制棋盘状态"""
    screen.fill((255, 255, 255))
    offset = margin
    
    # 根据网格大小动态调整字体大小和位置
    if grid_size <= 5:  # 5x5网格
        font_size = 36
        x_offset = margin//6  # 减小与网格的距离
        y_offset = margin//6
    elif grid_size <= 9:  # 9x9网格
        font_size = 30
        x_offset = margin//3
        y_offset = margin//3
    else:  # 13x13网格
        font_size = 25
        x_offset = margin//2
        y_offset = margin//2
    
    # 创建字体对象
    font = pygame.font.Font(None, font_size)
    
    # 绘制坐标标签
    for i in range(grid_size):
        # 绘制左侧的行号（x坐标）
        text = font.render(str(i), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.centerx = offset - x_offset
        text_rect.centery = offset + i * cell_size + cell_size//2
        screen.blit(text, text_rect)
        
        # 绘制顶部的列号（y坐标）
        text = font.render(str(i), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.centerx = offset + i * cell_size + cell_size//2
        text_rect.centery = offset - y_offset
        screen.blit(text, text_rect)
    
    # 绘制网格
    for x in range(grid_size):
        for y in range(grid_size):
            color = (255, 255, 255) if grid[x][y] == 0 else (0, 0, 0)
            pygame.draw.rect(screen, color, 
                           (offset + y * cell_size, offset + x * cell_size, 
                            cell_size, cell_size))
            pygame.draw.rect(screen, (0, 0, 0), 
                           (offset + y * cell_size, offset + x * cell_size, 
                            cell_size, cell_size), 1)
    
    # 绘制蚂蚁（用红色箭头表示）
    ant_x = offset + ant["y"] * cell_size + cell_size // 2
    ant_y = offset + ant["x"] * cell_size + cell_size // 2
    arrow_size = cell_size // 2
    
    if ant["direction"] == "up":
        points = [(ant_x, ant_y - arrow_size), 
                 (ant_x - arrow_size//2, ant_y + arrow_size//2),
                 (ant_x + arrow_size//2, ant_y + arrow_size//2)]
    elif ant["direction"] == "down":
        points = [(ant_x, ant_y + arrow_size),
                 (ant_x - arrow_size//2, ant_y - arrow_size//2),
                 (ant_x + arrow_size//2, ant_y - arrow_size//2)]
    elif ant["direction"] == "left":
        points = [(ant_x - arrow_size, ant_y),
                 (ant_x + arrow_size//2, ant_y - arrow_size//2),
                 (ant_x + arrow_size//2, ant_y + arrow_size//2)]
    else:  # right
        points = [(ant_x + arrow_size, ant_y),
                 (ant_x - arrow_size//2, ant_y - arrow_size//2),
                 (ant_x - arrow_size//2, ant_y + arrow_size//2)]
    
    pygame.draw.polygon(screen, (255, 0, 0), points)

def get_possible_cells(ant: Dict[str, Any], grid_size: int, steps: int) -> List[Tuple[int, int]]:
    """获取蚂蚁在给定步数内可能经过的格子，重点关注实际路径"""
    possible_cells = []
    current_ant = copy.deepcopy(ant)
    grid = [[0] * grid_size for _ in range(grid_size)]
    
    # 记录蚂蚁实际经过的路径
    for _ in range(steps):
        x, y = current_ant['x'], current_ant['y']
        possible_cells.append((x, y))  # 添加当前位置
        
        # 移动蚂蚁
        current_color = grid[x][y]
        grid[x][y] = 1 - current_color
        directions = ["up", "right", "down", "left"]
        
        if current_color == 0:  # 白色右转
            current_ant['direction'] = directions[(directions.index(current_ant['direction']) + 1) % 4]
        else:  # 黑色左转
            current_ant['direction'] = directions[(directions.index(current_ant['direction']) - 1) % 4]
            
        if current_ant['direction'] == "up":
            current_ant['x'] = (x - 1) % grid_size
        elif current_ant['direction'] == "right":
            current_ant['y'] = (y + 1) % grid_size
        elif current_ant['direction'] == "down":
            current_ant['x'] = (x + 1) % grid_size
        elif current_ant['direction'] == "left":
            current_ant['y'] = (y - 1) % grid_size
    
    # 如果路径上的格子太少，再添加一些相邻格子
    if len(possible_cells) < 3:
        center_x, center_y = ant['x'], ant['y']
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_x = (center_x + dx) % grid_size
                new_y = (center_y + dy) % grid_size
                if (new_x, new_y) not in possible_cells:
                    possible_cells.append((new_x, new_y))
    
    return possible_cells

def select_target_cell(ant: Dict[str, Any], grid_size: int, steps: int) -> Tuple[int, int]:
    """选择目标格子，倾向于选择蚂蚁可能经过的路径附近的格子"""
    possible_cells = get_possible_cells(ant, grid_size, steps)
    return random.choice(possible_cells)

def generate_options_q1(ant: Dict[str, Any], grid_size: int, options_num: int) -> List[str]:
    """Generate options for question type 1"""
    correct = f"Position ({ant['x']}, {ant['y']}), facing {ant['direction']}"
    options = [correct]
    
    # Generate incorrect options
    while len(options) < options_num:
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        direction = random.choice(["up", "right", "down", "left"])
        option = f"Position ({x}, {y}), facing {direction}"
        if option not in options:
            options.append(option)
    
    random.shuffle(options)
    correct_letter = chr(65 + options.index(correct))  # 获取正确选项的字母
    return options, correct_letter

def generate_options_q2(ant: Dict[str, Any], grid_size: int, options_num: int) -> List[str]:
    """Generate options for question type 2"""
    correct = f"Position ({ant['x']}, {ant['y']}), facing {ant['direction']}"
    options = [correct]
    
    # Generate incorrect options
    while len(options) < options_num:
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        direction = random.choice(["up", "right", "down", "left"])
        option = f"Position ({x}, {y}), facing {direction}"
        if option not in options:
            options.append(option)
    
    random.shuffle(options)
    correct_letter = chr(65 + options.index(correct))  # 获取正确选项的字母
    return options, correct_letter

def generate_mcq_question(question_id: int, steps: int, options: List[str], x: int = None, y: int = None) -> str:
    """Generate question text based on question ID"""
    base_text = GAME_RULES + "\n\n"
    
    if question_id == 1:
        question = base_text + "What is the current position and direction of the ant in the image?"
    elif question_id == 2:
        question = base_text + f"After {steps} steps, what will be the ant's position and direction?"
    
    # Add options to question text
    lettered_options = [f"{chr(65 + i)}: {option}" for i, option in enumerate(options)]  # 使用ASCII码，65是'A'
    options_text = "\n\nAnswer using one of the following options with its corresponding letter:\n" + "\n".join(lettered_options)
    return question + options_text

def generate_fill_question(steps: int, x: int, y: int) -> str:
    """Generate fill-in-blank question text"""
    base_text = GAME_RULES + "\n\n"
    question = base_text + f"After {steps} steps, how many times did the cell at position ({x}, {y}) change its color? Answer with a number."
    return question
    
def generate_analysis(question_id: int, steps: int, 
                     initial_state: Dict[str, Any], final_state: Dict[str, Any],
                     x: int = None, y: int = None, color_changes: int = None) -> str:
    """Generate step-by-step analysis"""
    if question_id == 1:
        return f"""Step-by-step analysis:
1. Look at the red arrow in the image which represents the ant
2. The arrow's position indicates the ant is at coordinates ({initial_state['ant']['x']}, {initial_state['ant']['y']})
3. The arrow's direction shows the ant is facing {initial_state['ant']['direction']}
Therefore, the ant's current position is ({initial_state['ant']['x']}, {initial_state['ant']['y']}) and it's facing {initial_state['ant']['direction']}."""
    
    elif question_id == 2:
        analysis = [
            f"Initial state: The ant is at ({initial_state['ant']['x']}, {initial_state['ant']['y']}) facing {initial_state['ant']['direction']}",
            "Let's follow the ant's movement step by step:"
        ]
        
        # Simulate each step
        current_ant = copy.deepcopy(initial_state['ant'])
        grid = copy.deepcopy(initial_state['grid'])
        
        for step in range(1, steps + 1):
            old_pos = (current_ant['x'], current_ant['y'])
            old_direction = current_ant['direction']
            old_color = "white" if grid[old_pos[0]][old_pos[1]] == 0 else "black"
            
            # Update state
            x, y = current_ant['x'], current_ant['y']
            current_color = grid[x][y]
            grid[x][y] = 1 - current_color
            directions = ["up", "right", "down", "left"]
            
            if current_color == 0:  # white
                current_ant['direction'] = directions[(directions.index(current_ant['direction']) + 1) % 4]
            else:  # black
                current_ant['direction'] = directions[(directions.index(current_ant['direction']) - 1) % 4]
            
            # Move
            if current_ant['direction'] == "up":
                current_ant['x'] = (x - 1) % len(grid)
            elif current_ant['direction'] == "right":
                current_ant['y'] = (y + 1) % len(grid)
            elif current_ant['direction'] == "down":
                current_ant['x'] = (x + 1) % len(grid)
            elif current_ant['direction'] == "left":
                current_ant['y'] = (y - 1) % len(grid)
            
            step_analysis = f"Step {step}: "
            step_analysis += f"Ant is on a {old_color} cell at {old_pos}, facing {old_direction}. "
            step_analysis += f"It {'turns right' if old_color == 'white' else 'turns left'}, "
            step_analysis += f"changes the cell to {'black' if old_color == 'white' else 'white'}, "
            step_analysis += f"moves forward to ({current_ant['x']}, {current_ant['y']}), now facing {current_ant['direction']}"
            
            analysis.append(step_analysis)
        
        analysis.append(f"\nFinal state: The ant is at ({final_state['ant']['x']}, {final_state['ant']['y']}) facing {final_state['ant']['direction']}")
        return "\n".join(analysis)
    
    else:  # question_id == 3
        analysis = [
            f"Initial state: The ant is at ({initial_state['ant']['x']}, {initial_state['ant']['y']}) facing {initial_state['ant']['direction']}",
            f"Target cell ({x}, {y}) starts as {'white' if initial_state['grid'][x][y] == 0 else 'black'}",
            "Let's follow the ant's movement step by step:"
        ]
        
        current_ant = copy.deepcopy(initial_state['ant'])
        grid = copy.deepcopy(initial_state['grid'])
        changes = 0
        
        for step in range(1, steps + 1):
            # Store current state before update
            old_x, old_y = current_ant['x'], current_ant['y']
            old_direction = current_ant['direction']
            old_color = "white" if grid[old_x][old_y] == 0 else "black"
            target_color = "white" if grid[x][y] == 0 else "black"
            
            # Update state
            grid[old_x][old_y] = 1 - grid[old_x][old_y]
            directions = ["up", "right", "down", "left"]
            
            if old_color == "white":  # white cell
                current_ant['direction'] = directions[(directions.index(current_ant['direction']) + 1) % 4]
            else:  # black cell
                current_ant['direction'] = directions[(directions.index(current_ant['direction']) - 1) % 4]
            
            # Move ant
            if current_ant['direction'] == "up":
                current_ant['x'] = (old_x - 1) % len(grid)
            elif current_ant['direction'] == "right":
                current_ant['y'] = (old_y + 1) % len(grid)
            elif current_ant['direction'] == "down":
                current_ant['x'] = (old_x + 1) % len(grid)
            elif current_ant['direction'] == "left":
                current_ant['y'] = (old_y - 1) % len(grid)
                
            # Generate step analysis in the same style as question type 2
            step_analysis = f"Step {step}: "
            step_analysis += f"Ant is on a {old_color} cell at ({old_x}, {old_y}), facing {old_direction}. "
            step_analysis += f"It {'turns right' if old_color == 'white' else 'turns left'}, "
            step_analysis += f"changes the cell to {'black' if old_color == 'white' else 'white'}, "
            step_analysis += f"moves forward to ({current_ant['x']}, {current_ant['y']}), now facing {current_ant['direction']}. "
            
            if (old_x, old_y) == (x, y):
                changes += 1
                step_analysis += f"Target cell ({x}, {y}) is visited and changes from {target_color} to {'black' if target_color == 'white' else 'white'} "
                step_analysis += f"(change #{changes})"
            else:
                step_analysis += f"Target cell ({x}, {y}) remains {target_color} (no change)"
            
            analysis.append(step_analysis)
        
        analysis.append(f"\nFinal state: The ant is at ({final_state['ant']['x']}, {final_state['ant']['y']}) facing {final_state['ant']['direction']}")
        analysis.append(f"Target cell ({x}, {y}) changed color {color_changes} time" + ("s" if color_changes > 1 else ""))
        return "\n".join(analysis)

def generate_dataset(dataset_size: int = DATASET_SIZE, options_num: int = 8) -> List[Dict[str, Any]]:
    """生成完整的数据集,包含MCQ和填空题"""
    try:
        pygame.init()
        create_directories()
        
        dataset = []
        sample_id = 1
        data_id_counter = 1

        for difficulty in ["Easy", "Medium", "Hard"]:
            grid_size = GRID_SIZES[difficulty]
            cell_size, margin = calculate_cell_size(grid_size)
            screen_size = (grid_size * cell_size + margin * 2, 
                         grid_size * cell_size + margin * 2)
            screen = pygame.display.set_mode(screen_size)
            
            for _ in range(dataset_size):
                # 初始化网格和蚂蚁
                grid = init_grid(grid_size)
                ant = init_ant(grid_size)
                
                # 保存初始状态
                base_filename = f"board_{sample_id:03d}"
                image_path = os.path.join(IMAGES_DIR, f"{base_filename}.png")
                state_path = os.path.join(STATES_DIR, f"{base_filename}.json")
                
                # 绘制并保存棋盘状态
                draw_board(screen, grid, ant, grid_size, cell_size, margin)
                save_board_image(screen, image_path)
                save_board_state(grid, ant, state_path)
                
                # 生成MCQ题目
                for question_id in MCQ_QUESTION_TYPES:
                    data_entry = {
                        "data_id": f"langton-mcq-{data_id_counter:05d}",
                        "qa_type": MCQ_QUESTION_TYPES[question_id]["type"],
                        "question_id": question_id,
                        "question_description": MCQ_QUESTION_TYPES[question_id]["description"],
                        "image": f"images/{base_filename}.png",
                        "state": f"states/{base_filename}.json",
                        "plot_level": difficulty,
                        "qa_level": MCQ_QUESTION_TYPES[question_id]["qa_level"]
                    }
                    
                    if question_id == 1:
                        options, correct = generate_options_q1(ant, grid_size, options_num)
                        steps = 0
                        grid_copy, ant_copy = grid, ant
                    else:
                        steps = random.randint(5, 10)
                        grid_copy = copy.deepcopy(grid)
                        ant_copy = copy.deepcopy(ant)
                        
                        for _ in range(steps):
                            update_ant_state(grid_copy, ant_copy, grid_size)
                        
                        options, correct = generate_options_q2(ant_copy, grid_size, options_num)
                    
                    initial_state = {"grid": grid, "ant": ant}
                    final_state = {"grid": grid_copy, "ant": ant_copy}
                    
                    question_text = generate_mcq_question(question_id, steps, options)
                    
                    data_entry.update({
                        "question": question_text,
                        "answer": correct,
                        "analysis": generate_analysis(question_id, steps, 
                                                   initial_state, final_state),
                        "options": options
                    })
                    
                    dataset.append(data_entry)
                    data_id_counter += 1

                # 生成填空题
                for question_id in FILL_QUESTION_TYPES:
                    steps = random.randint(5, 12)
                    grid_copy = copy.deepcopy(grid)
                    ant_copy = copy.deepcopy(ant)
                    
                    x, y = select_target_cell(ant, grid_size, steps)
                    color_changes = 0
                    
                    for _ in range(steps):
                        if (ant_copy['x'], ant_copy['y']) == (x, y):
                            color_changes += 1
                        update_ant_state(grid_copy, ant_copy, grid_size)
                    
                    initial_state = {"grid": grid, "ant": ant}
                    final_state = {"grid": grid_copy, "ant": ant_copy}
                    
                    data_entry = {
                        "data_id": f"langton-fill-{data_id_counter:05d}",
                        "qa_type": "ActionOutcome",
                        "question_id": 3,
                        "question_description": "Count how many times a specific cell changes its color",
                        "image": f"images/{base_filename}.png",
                        "state": f"states/{base_filename}.json",
                        "plot_level": difficulty,
                        "qa_level": "Hard",
                        "question": generate_fill_question(steps, x, y),
                        "answer": str(color_changes),
                        "analysis": generate_analysis(question_id, steps, initial_state, final_state, x, y, color_changes)
                    }
                    
                    dataset.append(data_entry)
                    data_id_counter += 1

                sample_id += 1
                
        print("Dataset generated successfully!")
        return dataset

    except Exception as e:
        print(f"Error generating dataset: {e}")
        return []

    finally:
        pygame.quit()

if __name__ == "__main__":
    data = generate_dataset(dataset_size=56, options_num=8)

    with open(DATASET_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)