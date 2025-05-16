import os
import json
import random
import pygame
from pygame import Surface
from typing import List, Dict, Tuple, Any , Optional
import itertools
from tqdm import tqdm
import time
from functools import wraps
import threading

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR=os.path.join(CURRENT_DIR,"lifegame_dataset")
IMAGES_DIR = os.path.join(DATASET_DIR, "images")
STATES_DIR = os.path.join(DATASET_DIR, "states")
DATASET_FILE = os.path.join(DATASET_DIR, "data.json")

# Grid sizes for different plot complexity levels
GRID_SETTINGS = {
    "Easy": 3,    # 3x3 grid
    "Medium": 4,  # 4x4 grid
    "Hard": 5     # 5x5 grid
}

# Question type settings with fixed difficulty levels
QUESTION_SETTINGS = {
    "StateInfo": {
        "qa_level": "Easy",
        "question_id": 1,
        "question_description": "Questions about counting the current number of live cells in the grid"
    },
    "ActionOutcome": {
        "qa_level": "Medium",
        "question_id": 2,
        "question_description": "Questions about predicting the number of live cells after 1 iteration"
    },
    "CellChangeCount": {
        "qa_level": "Medium",
        "question_id": 3,
        "question_description": "Questions about counting state changes of specific cells over iterations"
    },
    "StabilitySteps": {
        "qa_level": "Hard",
        "question_id": 4,
        "question_description": "Questions about predicting steps needed to reach stability"
    }
}

# Coordinate system explanation
COORDINATE_SYSTEM = """In this grid, we use (row, col) coordinates where:
- row increases from top to bottom (0 at top)
- col increases from left to right (0 at left)
For example, the top-left cell is at (0, 0), and the cell below it is at (1, 0)."""

# Game rules (including coordinate system explanation)
GAME_RULES = f"""Conway's Game of Life is a cellular automaton where each cell in the grid can be either alive (black) or dead (white). 

Each cell interacts with its eight neighbors, which are the cells that are horizontally, vertically, or diagonally adjacent. For a cell at position (r,c), its neighbors are:
- (r-1,c-1)  (r-1,c)  (r-1,c+1)   [above row]
- (r,c-1)     (r,c)    (r,c+1)     [same row]
- (r+1,c-1)  (r+1,c)  (r+1,c+1)   [below row]

Region boundaries wrap around to the opposite side:
- A cell at the top edge connects to cells at the bottom edge
- A cell at the left edge connects to cells at the right edge
- Corner cells connect to the diagonally opposite corner
For example, in a 3x3 region:
- Cell (0,0)'s top neighbor is (2,0)
- Cell (0,0)'s left neighbor is (0,2)
- Cell (0,0)'s top-left neighbor is (2,2)

The game evolves in discrete steps according to these rules:
1. Any live cell with fewer than two live neighbors dies (underpopulation)
2. Any live cell with two or three live neighbors lives on to the next generation
3. Any live cell with more than three live neighbors dies (overpopulation)
4. Any dead cell with exactly three live neighbors becomes alive (reproduction)

In the image, black squares represent live cells, white squares represent dead cells, and the grid lines help visualize the cell boundaries. 

{COORDINATE_SYSTEM}"""

def get_live_cells(grid: List[List[int]]) -> List[Tuple[int, int]]:
    """
    Get coordinates of all live cells in the grid.
    
    Args:
        grid: The game grid
    Returns:
        List of (x,y) coordinates of live cells
    """
    size = len(grid)
    return [(x, y) for x in range(size) for y in range(size) if grid[x][y] == 1]

def debug_print_grid_section(grid: List[List[int]], coords: List[Tuple[int, int]]):
    """
    Debug helper to print the grid section around given coordinates.
    
    Args:
        grid: The game grid
        coords: List of coordinates to check
    """
    if not coords:
        return
        
    # Find the bounds of the area to print
    min_row = max(0, min(row for row, _ in coords) - 1)
    max_row = min(len(grid), max(row for row, _ in coords) + 2)
    min_col = max(0, min(col for _, col in coords) - 1)
    max_col = min(len(grid), max(col for _, col in coords) + 2)
    
    print(f"Grid section from ({min_row},{min_col}) to ({max_row-1},{max_col-1}):")
    coord_set = set(coords)
    for row in range(min_row, max_row):
        line = ""
        for col in range(min_col, max_col):
            if (row, col) in coord_set:
                line += "X" if grid[row][col] == 1 else "?"  # ? indicates mismatch
            else:
                line += str(grid[row][col])
        print(line)

def ensure_directories():
    """Create necessary directories for the dataset."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(STATES_DIR, exist_ok=True)

def draw_coordinates(surface: Surface, grid_size: int, cell_size: int, margin: int, offset: int):
    """Draw coordinate numbers around the grid."""
    font = pygame.font.Font(None, 20)
    
    # Draw x coordinates on the left
    for x in range(grid_size):
        text = font.render(str(x), True, (0, 0, 0))
        text_rect = text.get_rect(right=offset-5, centery=offset + x * cell_size + cell_size//2)
        surface.blit(text, text_rect)

    # Draw y coordinates on top
    for y in range(grid_size):
        text = font.render(str(y), True, (0, 0, 0))
        text_rect = text.get_rect(centerx=offset + y * cell_size + cell_size//2, bottom=offset-5)
        surface.blit(text, text_rect)

def draw_grid(surface: Surface, grid: List[List[int]], cell_size: int, margin: int, offset: int):
    """Draw the grid with cells and grid lines."""
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            color = (0, 0, 0) if grid[x][y] == 1 else (255, 255, 255)
            pygame.draw.rect(surface, color, 
                           (offset + y * cell_size, 
                            offset + x * cell_size, 
                            cell_size, cell_size))

    # Draw grid lines
    for x in range(len(grid) + 1):
        pygame.draw.line(surface, (128, 128, 128), 
                        (offset, offset + x * cell_size),
                        (offset + len(grid[0]) * cell_size, offset + x * cell_size))
    for y in range(len(grid[0]) + 1):
        pygame.draw.line(surface, (128, 128, 128),
                        (offset + y * cell_size, offset),
                        (offset + y * cell_size, offset + len(grid) * cell_size))

def save_state_and_image(grid: List[List[int]], idx: int, grid_size: int) -> Tuple[str, str]:
    """Save the current grid state as both JSON and PNG files."""
    state_path = os.path.join(STATES_DIR, f"board_{idx:03d}.json")
    with open(state_path, "w") as f:
        json.dump({"grid": grid}, f)
    
    pygame.init()
    cell_size = min(30, 600 // grid_size)
    margin = 40
    
    screen_size = (grid_size * cell_size + margin * 2, grid_size * cell_size + margin * 2)
    screen = Surface(screen_size)
    screen.fill((255, 255, 255))
    offset = (screen_size[0] - grid_size * cell_size) // 2
    
    draw_grid(screen, grid, cell_size, margin, offset)
    draw_coordinates(screen, grid_size, cell_size, margin, offset)
    
    image_path = os.path.join(IMAGES_DIR, f"board_{idx:03d}.png")
    pygame.image.save(screen, image_path)
    
    # Return relative paths from project root
    rel_state_path = os.path.relpath(state_path, DATASET_DIR)
    rel_image_path = os.path.relpath(image_path, DATASET_DIR)
    return rel_state_path, rel_image_path

def init_grid(size: int) -> List[List[int]]:
    """Initialize a grid with the specified size."""
    grid = [[0] * size for _ in range(size)]
    for x in range(size):
        for y in range(size):
            grid[x][y] = 1 if random.random() < 0.3 else 0
    return grid

def count_neighbors(grid: List[List[int]], x: int, y: int) -> int:
    """Count live neighbors for a cell, including wrapping around edges."""
    count = 0
    size = len(grid)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx = (x + dx) % size
            ny = (y + dy) % size
            count += grid[nx][ny]
    return count

def update_grid(grid: List[List[int]]) -> List[List[int]]:
    """Update the grid according to Game of Life rules."""
    size = len(grid)
    new_grid = [[0] * size for _ in range(size)]
    
    for x in range(size):
        for y in range(size):
            neighbors = count_neighbors(grid, x, y)
            if grid[x][y] == 1:
                new_grid[x][y] = 1 if neighbors in [2, 3] else 0
            else:
                new_grid[x][y] = 1 if neighbors == 3 else 0
    
    return new_grid

def simulate_n_steps(grid: List[List[int]], steps: int) -> List[Dict[str, Any]]:
    """
    Simulate n steps of Game of Life evolution and track detailed changes.
    
    Args:
        grid: Initial grid state
        steps: Number of steps to simulate
        
    Returns:
        List of dictionaries containing state information for each step
    """
    current_grid = [row[:] for row in grid]
    evolution_history = []
    
    for step in range(steps):
        next_grid = update_grid(current_grid)
        live_cells = [(x, y) for x in range(len(grid)) 
                     for y in range(len(grid)) if next_grid[x][y] == 1]
        changes = get_state_changes(current_grid, next_grid)
        
        # Calculate stability metrics
        stability_score = sum(1 for x, y in live_cells 
                            if count_neighbors(next_grid, x, y) in [2, 3])
        
        evolution_history.append({
            "step": step + 1,
            "grid": [row[:] for row in next_grid],
            "changes": changes,
            "live_count": len(live_cells),
            "stability_score": stability_score,
            "stable_pattern_found": stability_score == len(live_cells)
        })
        
        current_grid = next_grid
        
    return evolution_history

def get_state_changes(old_grid: List[List[int]], new_grid: List[List[int]]) -> List[str]:
    """Get a list of changes between two grid states."""
    changes = []
    size = len(old_grid)
    for x in range(size):
        for y in range(size):
            if old_grid[x][y] != new_grid[x][y]:
                state = "alive" if new_grid[x][y] == 1 else "dead"
                changes.append(f"Cell at ({x},{y}) became {state}")
    return changes

class TimeoutError(Exception):
    """超时异常"""
    pass

def timeout_decorator(seconds):
    """
    一个跨平台的超时装饰器实现。
    
    这个装饰器使用threading模块来实现超时控制，可以在Windows、Linux和MacOS上正常工作。
    它会在指定的秒数后中断函数的执行。
    
    Args:
        seconds: 最大允许执行时间（秒）
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [TimeoutError(f'函数执行超过{seconds}秒')]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    result[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True  # 设置为守护线程，这样主程序退出时它也会退出
            
            thread.start()
            thread.join(seconds)  # 等待指定的秒数
            
            if thread.is_alive():
                return None  # 如果线程还在运行，返回None表示超时
            
            if isinstance(result[0], Exception):
                raise result[0]
            
            return result[0]
        return wrapper
    return decorator

@timeout_decorator(10)
def track_cell_changes(grid: List[List[int]], iterations: int, target_cell: Tuple[int, int]) -> int:
    """
    追踪特定格子在若干代演化中的状态变化次数。
    优化后的版本添加了更多的边界检查和错误处理。
    
    Args:
        grid: 初始网格状态
        iterations: 演化代数
        target_cell: 目标格子的坐标 (row, col)
    
    Returns:
        状态变化的次数，如果出现错误返回-1
    """
    try:
        current_grid = [row[:] for row in grid]
        changes = 0
        row, col = target_cell
        
        # 检查坐标是否有效
        if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
            return -1
            
        prev_state = current_grid[row][col]
        
        for _ in range(iterations):
            current_grid = update_grid(current_grid)
            current_state = current_grid[row][col]
            if current_state != prev_state:
                changes += 1
            prev_state = current_state
            
        return changes
    except Exception as e:
        print(f"Error in track_cell_changes: {str(e)}")
        return -1
    
def generate_state_sequence_options(correct_sequence: List[int], iterations: int) -> List[List[int]]:
    """
    根据正确的状态序列生成错误选项
    每个选项都是一个状态序列，表示细胞在每一步的状态（0或1）
    
    Args:
        correct_sequence: 正确的状态序列
        iterations: 迭代次数
    
    Returns:
        包含8个选项的列表（包括正确选项）
    """
    all_options = set()
    # 将正确序列转换为元组以便作为集合元素
    correct_tuple = tuple(correct_sequence)
    all_options.add(correct_tuple)
    
    # 生成所有可能的序列（每个位置可以是0或1）
    all_possible_sequences = list(itertools.product([0, 1], repeat=iterations + 1))  # +1因为包含初始状态
    
    # 移除正确序列
    all_possible_sequences.remove(correct_tuple)
    
    # 随机选择7个不同的错误序列
    wrong_sequences = random.sample(all_possible_sequences, min(7, len(all_possible_sequences)))
    
    # 将所有选项（包括正确序列）转换回列表格式
    options = [list(seq) for seq in wrong_sequences]
    options.append(correct_sequence)
    
    # 随机打乱选项顺序
    random.shuffle(options)
    return options

def state_sequence_to_text(sequence: List[int]) -> str:
    """
    将状态序列转换为易读的文本格式
    
    Args:
        sequence: 状态序列（0和1的列表）
    
    Returns:
        描述状态变化的文本
    """
    states = []
    for i, state in enumerate(sequence):
        if i == 0:
            states.append(f"Initially: {'alive' if state == 1 else 'dead'}")
        else:
            states.append(f"Step {i}: {'alive' if state == 1 else 'dead'}")
    return " → ".join(states)

@timeout_decorator(10)
def check_stability(grid: List[List[int]], max_steps: int = 30) -> int:
    """
    检查网格达到稳定状态需要的步数。
    增加了超时保护和更高效的状态检测。
    
    Args:
        grid: 初始网格状态
        max_steps: 最大检查步数
    
    Returns:
        达到稳定状态所需的步数，如果在max_steps步内未达到稳定则返回-1
    """
    current_grid = [row[:] for row in grid]
    history = []
    
    for step in range(max_steps):
        # 将当前状态转换为可哈希的形式
        state_hash = tuple(tuple(row) for row in current_grid)
        
        # 检查是否出现过这个状态
        if state_hash in history:
            return history.index(state_hash)
        
        history.append(state_hash)
        next_grid = update_grid(current_grid)
        
        # 优化的静态检查
        if all(all(current_grid[i][j] == next_grid[i][j] 
                   for j in range(len(grid))) 
               for i in range(len(grid))):
            return step + 1
            
        current_grid = next_grid
    
    return -1

def init_grid_with_ratio(size: int, max_attempts: int = 20) -> Tuple[List[List[int]], bool]:
    """
    初始化满足活细胞比例要求的网格。
    添加了尝试次数限制。
    
    Args:
        size: 网格大小
        max_attempts: 最大尝试次数
    
    Returns:
        (grid, success_flag)
    """
    start_time = time.time()
    timeout_seconds = 5  # 设置5秒超时
    
    for attempt in range(max_attempts):
        # 检查是否超时
        if time.time() - start_time > timeout_seconds:
            print(f"Grid generation timed out after {timeout_seconds} seconds")
            return init_grid(size), False
            
        grid = [[0] * size for _ in range(size)]
        # 使用更保守的初始化概率
        initial_probability = 0.3
        
        for x in range(size):
            for y in range(size):
                grid[x][y] = 1 if random.random() < initial_probability else 0
        
        live_ratio = sum(sum(row) for row in grid) / (size * size)
        if 0.2 <= live_ratio <= 0.4:
            return grid, True
    
    return init_grid(size), False

def evaluate_cell_activity(grid: List[List[int]], cell: Tuple[int, int], look_ahead: int = 3) -> int:
    """
    评估一个格子的活跃度。
    
    通过模拟未来几步来评估一个格子的状态变化频率。
    
    Args:
        grid: 当前网格
        cell: 目标格子坐标
        look_ahead: 向前看几步
        
    Returns:
        活跃度分数，越高表示该格子状态变化越频繁
    """
    row, col = cell
    current_grid = [row[:] for row in grid]
    changes = 0
    prev_state = current_grid[row][col]
    
    for _ in range(look_ahead):
        current_grid = update_grid(current_grid)
        current_state = current_grid[row][col]
        if current_state != prev_state:
            changes += 1
        prev_state = current_state
    
    return changes

def select_target_cell(grid: List[List[int]]) -> Optional[Tuple[int, int]]:
    """
    选择一个适合进行状态变化分析的目标格子。
    
    选择策略：
    1. 首先找到所有活细胞及其相邻格子
    2. 评估每个候选格子的活跃度（状态变化频率）
    3. 从活跃度较高的格子中随机选择一个
    
    Args:
        grid: 当前网格状态
        
    Returns:
        Tuple[int, int]: 选中格子的(行,列)坐标，如果没有合适的格子则返回None
    """
    grid_size = len(grid)
    
    # 获取所有活细胞
    live_cells = get_live_cells(grid)
    if not live_cells:
        return None
        
    # 收集候选格子（包括活细胞和它们的邻居）
    candidate_cells = set()
    for row, col in live_cells:
        # 添加活细胞本身
        candidate_cells.add((row, col))
        # 添加其相邻格子
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row = (row + dr) % grid_size
                new_col = (col + dc) % grid_size
                candidate_cells.add((new_row, new_col))
    
    if not candidate_cells:
        return None
    
    # 评估每个候选格子的活跃度
    cell_scores = []
    for cell in candidate_cells:
        # 计算未来几步的状态变化
        activity_score = evaluate_cell_activity(grid, cell, look_ahead=3)
        if activity_score > 0:  # 只考虑会发生变化的格子
            cell_scores.append((cell, activity_score))
    
    if not cell_scores:
        # 如果没有找到活跃的格子，从所有候选格子中随机选择一个
        return random.choice(list(candidate_cells))
    
    # 选择活跃度最高的几个格子作为最终候选
    cell_scores.sort(key=lambda x: x[1], reverse=True)
    top_candidates = cell_scores[:min(5, len(cell_scores))]
    
    # 从顶级候选中随机选择一个
    chosen_cell, _ = random.choice(top_candidates)
    return chosen_cell

def check_local_stability(grid: List[List[int]], region_start: Tuple[int, int], 
                       size: int = 3, max_steps: int = 20) -> int:
    """
    检查3x3区域作为独立生命游戏的稳定性。
    
    Args:
        grid: 完整的网格
        region_start: 区域左上角的坐标 (row, col)
        size: 区域的大小（默认3x3）
        max_steps: 最大检查步数
        
    Returns:
        达到稳定的步数，如果未达到则返回-1
    """
    # 提取目标区域
    row_start, col_start = region_start
    grid_size = len(grid)
    region = []
    for i in range(size):
        row = []
        for j in range(size):
            actual_row = (row_start + i) % grid_size
            actual_col = (col_start + j) % grid_size
            row.append(grid[actual_row][actual_col])
        region.append(row)
    
    current_region = [row[:] for row in region]
    state_history = [tuple(tuple(row) for row in current_region)]
    
    # 模拟区域演化
    for step in range(max_steps):
        # 计算新状态
        next_region = [[0] * size for _ in range(size)]
        for i in range(size):
            for j in range(size):
                neighbors = 0
                # 统计邻居（考虑3x3边界）
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni = (i + di) % size
                        nj = (j + dj) % size
                        neighbors += current_region[ni][nj]
                
                # 应用生命游戏规则
                if current_region[i][j] == 1:
                    next_region[i][j] = 1 if neighbors in [2, 3] else 0
                else:
                    next_region[i][j] = 1 if neighbors == 3 else 0
        
        # 检查是否达到稳定
        next_state = tuple(tuple(row) for row in next_region)
        if next_state in state_history:
            return step + 1
            
        state_history.append(next_state)
        current_region = next_region
    
    return -1

def simulate_region_evolution(region: List[List[int]], steps: int) -> List[List[List[int]]]:
        """模拟区域演化并返回历史记录"""
        size = len(region)
        history = [region]
        current = [row[:] for row in region]
        
        for _ in range(steps):
            next_region = [[0] * size for _ in range(size)]
            for i in range(size):
                for j in range(size):
                    neighbors = 0
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni = (i + di) % size
                            nj = (j + dj) % size
                            neighbors += current[ni][nj]
                    
                    if current[i][j] == 1:
                        next_region[i][j] = 1 if neighbors in [2, 3] else 0
                    else:
                        next_region[i][j] = 1 if neighbors == 3 else 0
            
            history.append(next_region)
            current = next_region
        
        return history
    
def will_change(region: List[List[int]], row: int, col: int) -> Tuple[bool, str, int]:
    """
    检查给定位置的细胞在下一步是否会改变状态
    
    Returns:
        Tuple[bool, str, int]: (是否会改变, 原因, 活邻居数量)
    """
    size = len(region)
    current_state = region[row][col]
    neighbors = 0
    
    # 计算邻居数量
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr = (row + dr) % size
            nc = (col + dc) % size
            neighbors += region[nr][nc]
    
    if current_state == 1:  # 活细胞
        if neighbors < 2:
            return True, "underpopulation", neighbors
        elif neighbors > 3:
            return True, "overpopulation", neighbors
        else:
            return False, "survival", neighbors
    else:  # 死细胞
        if neighbors == 3:
            return True, "reproduction", neighbors
        else:
            return False, "remains dead", neighbors

def analyze_region_stability(region: List[List[int]]) -> List[str]:
    """详细分析区域的稳定性"""
    size = len(region)
    analysis = []
    
    # 先显示当前状态
    analysis.append("Current state of the region('1' stands for living cell and '0' stands for dead cell):")
    for row in region:
        analysis.append(" ".join("1" if cell == 1 else "0" for cell in row))
    
    # 分析所有细胞
    analysis.append("\nCell-by-cell analysis:")
    has_changes = False
    
    for i in range(size):
        for j in range(size):
            will_change_state, reason, neighbors = will_change(region, i, j)
            current = "alive" if region[i][j] == 1 else "dead"
            
            if will_change_state:
                has_changes = True
                next_state = "dead" if region[i][j] == 1 else "alive"
                analysis.append(f"• Cell ({i},{j}): currently {current}")
                analysis.append(f"  - Has {neighbors} live neighbors")
                analysis.append(f"  - Will become {next_state} due to {reason}")
    
    if not has_changes:
        analysis.append("No cells will change state - region is stable")
    else:
        analysis.append("Region is not stable - some cells will change in the next step")
    
    return analysis

def is_region_stable(region: List[List[int]]) -> bool:
    """检查区域是否达到稳定状态"""
    size = len(region)
    for i in range(size):
        for j in range(size):
            will_change_state, _, _ = will_change(region, i, j)
            if will_change_state:
                return False
    return True
class MCQOptionsGenerator:
    """Multiple Choice Question options generator utility class"""
    
    @staticmethod
    def generate_numeric_options(correct_answer: int, num_options: int = 8, 
                               min_val: int = None, max_val: int = None) -> Tuple[List[int], int]:
        """
        Generate numeric options including the correct answer.
        Returns both options and the index of correct answer.
        """
        if min_val is None:
            min_val = max(0, correct_answer - 5)
        if max_val is None:
            max_val = correct_answer + 5
            
        min_val = min(min_val, correct_answer)
        max_val = max(max_val, correct_answer)
        
        # 生成所有可能的错误选项
        candidates = list(range(min_val, max_val + 1))
        candidates.remove(correct_answer)
        
        # 如果候选池太小，扩大范围
        while len(candidates) < num_options - 1:
            min_val = max(0, min_val - 1)
            max_val = max_val + 1
            candidates = list(range(min_val, max_val + 1))
            if correct_answer in candidates:
                candidates.remove(correct_answer)
        
        # 随机选择错误选项
        wrong_options = random.sample(candidates, num_options - 1)
        
        # 随机选择位置插入正确答案
        correct_index = random.randint(0, num_options - 1)
        options = wrong_options.copy()
        options.insert(correct_index, correct_answer)
        
        # 验证
        assert len(options) == num_options, f"Generated {len(options)} options, expected {num_options}"
        assert len(set(options)) == num_options, "Duplicate options found"
        assert correct_answer in options, "Correct answer not in options"
        assert options[correct_index] == correct_answer, "Correct answer not at expected index"
        
        return options, correct_index

    @staticmethod
    def format_options(options: List[Any], correct_index: int) -> Tuple[List[str], str, str]:
        """
        Format options with letter prefixes and find correct answer letter.
        Now takes the correct index as an argument.
        """
        # 生成带字母的选项
        formatted_options = [f"{chr(65+i)}: {opt}" for i, opt in enumerate(options)]
        options_text = "\n".join(formatted_options)
        
        # 根据索引确定正确答案字母
        correct_letter = chr(65 + correct_index)
        
        # 验证
        correct_option = formatted_options[correct_index]
        assert correct_option.startswith(f"{correct_letter}:"), \
            f"Correct letter mismatch: {correct_letter} vs {correct_option}"
        
        return formatted_options, options_text, correct_letter

    @staticmethod
    def generate_sequence_options(correct_sequence: List[int],
                                possible_values: List[int],
                                num_options: int = 8) -> Tuple[List[List[int]], int]:
        """
        Generate sequence-based options.
        Returns both options and the index of correct sequence.
        """
        sequence_length = len(correct_sequence)
        unique_sequences = {tuple(correct_sequence)}
        
        # 定义序列变化策略
        def create_variant(base_sequence: List[int], min_changes: int = 1) -> List[int]:
            variant = base_sequence.copy()
            num_changes = random.randint(min_changes, max(min_changes + 1, sequence_length // 2))
            positions = random.sample(range(sequence_length), num_changes)
            for pos in positions:
                other_values = [v for v in possible_values if v != variant[pos]]
                if other_values:
                    variant[pos] = random.choice(other_values)
            return variant
        
        # 使用不同策略生成变体
        strategies = [
            lambda seq: [1 - seq[0]] + seq[1:],
            lambda seq: seq[:-1] + [1 - seq[-1]],
            lambda seq: [1 - x for x in seq],
            lambda seq: seq[1:] + seq[:1],
            lambda seq: create_variant(seq, 1),
            lambda seq: create_variant(seq, 2)
        ]
        
        attempts = 0
        while len(unique_sequences) < num_options and attempts < 100:
            for strategy in strategies:
                if len(unique_sequences) >= num_options:
                    break
                new_sequence = strategy(list(correct_sequence))
                unique_sequences.add(tuple(new_sequence))
            attempts += 1
        
        # 确保有足够的选项
        while len(unique_sequences) < num_options:
            random_sequence = [random.choice(possible_values) for _ in range(sequence_length)]
            if tuple(random_sequence) != tuple(correct_sequence):
                unique_sequences.add(tuple(random_sequence))
        
        # 转换回列表并随机插入正确序列
        sequences = [list(seq) for seq in unique_sequences if seq != tuple(correct_sequence)]
        sequences = sequences[:num_options-1]
        correct_index = random.randint(0, num_options - 1)
        sequences.insert(correct_index, correct_sequence)
        
        # 验证
        assert len(sequences) == num_options, f"Generated {len(sequences)} sequences, expected {num_options}"
        assert len(set(tuple(seq) for seq in sequences)) == num_options, "Duplicate sequences found"
        assert sequences[correct_index] == correct_sequence, "Correct sequence not at expected index"
        
        return sequences, correct_index

class GameAnalysisGenerator:
    """Life Game analysis generator utility class"""
    
    @staticmethod
    def visualize_grid(grid: List[List[int]], highlight_cells: List[Tuple[int, int]] = None) -> str:
        """将网格转换为可视化文本表示"""
        visual = []
        grid_size = len(grid)
        
        # 添加列号
        col_numbers = "   " + " ".join(str(i) for i in range(grid_size))
        visual.append(col_numbers)
        
        # 添加带行号的网格行
        for i in range(grid_size):
            row_cells = []
            for j in range(grid_size):
                cell = "1" if grid[i][j] == 1 else "0"
                if highlight_cells and (i, j) in highlight_cells:
                    cell = f"[{cell}]"  # 标记发生变化的细胞
                row_cells.append(cell)
            row_visual = f"{i}: " + " ".join(row_cells)
            visual.append(row_visual)
            
        return "\n".join(visual)
    
    @staticmethod
    def generate_state_info_analysis(grid: List[List[int]]) -> str:
        """生成当前状态分析，专注于计数活细胞"""
        grid_size = len(grid)
        analysis = ["Current State Analysis:\n"]
        
        # 显示当前棋盘状态
        analysis.append("Grid State('1' stands for living cell and '0' stands for dead cell):")
        analysis.append(GameAnalysisGenerator.visualize_grid(grid))
        analysis.append("")
        
        # 逐行计数活细胞
        analysis.append("Counting live cells row by row:")
        total_live_cells = 0
        for row in range(grid_size):
            live_in_row = sum(grid[row])
            total_live_cells += live_in_row
            
            # 获取该行活细胞的位置
            live_positions = [(row, col) for col in range(grid_size) if grid[row][col] == 1]
            positions_str = ', '.join(f"({row},{col})" for row, col in live_positions)
            
            analysis.append(f"\nRow {row}:")
            analysis.append(f"- Live cells in this row: {live_in_row}")
            if live_positions:
                analysis.append(f"- Positions: {positions_str}")
        
        # 总结
        analysis.extend([
            f"\nFinal Count:",
            f"- Total live cells: {total_live_cells}"
        ])
        
        return "\n".join(analysis)
    
    @staticmethod
    def analyze_cell(grid: List[List[int]], row: int, col: int) -> str:
        """生成单个细胞的详细分析"""
        grid_size = len(grid)
        current_state = grid[row][col]
        state_text = "alive" if current_state == 1 else "dead"
        
        # 收集所有邻居信息
        neighbors_info = []
        live_neighbors = 0
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                    
                nr = (row + dr) % grid_size
                nc = (col + dc) % grid_size
                
                is_wrapped = nr != row + dr or nc != col + dc
                neighbor_state = grid[nr][nc]
                live_neighbors += neighbor_state
                
                position_desc = ""
                if dr == -1:
                    position_desc = "above"
                    if dc == -1: position_desc += " left"
                    if dc == 1: position_desc += " right"
                elif dr == 1:
                    position_desc = "below"
                    if dc == -1: position_desc += " left"
                    if dc == 1: position_desc += " right"
                else:
                    if dc == -1: position_desc = "left"
                    if dc == 1: position_desc = "right"
                
                if is_wrapped:
                    position_desc += " (wrapped)"
                    
                neighbors_info.append(
                    f"- {position_desc}: ({nr},{nc}) is {'alive' if neighbor_state == 1 else 'dead'}"
                )
        
        # 生成分析文本
        analysis = [f"Cell ({row},{col}) - currently {state_text}"]
        analysis.append("\nNeighbors:")
        analysis.extend(sorted(neighbors_info))  # 排序以保持一致的顺序
        analysis.append(f"\nTotal live neighbors: {live_neighbors}")
        
        # 添加状态变化预测及原因
        analysis.append("\nPrediction:")
        if current_state == 1:  # 当前是活细胞
            if live_neighbors < 2:
                analysis.append("→ Will die due to underpopulation (fewer than 2 live neighbors)")
            elif live_neighbors > 3:
                analysis.append("→ Will die due to overpopulation (more than 3 live neighbors)")
            elif live_neighbors in [2, 3]:
                analysis.append("→ Will survive (has 2 or 3 live neighbors)")
        else:  # 当前是死细胞
            if live_neighbors == 3:
                analysis.append("→ Will become alive due to reproduction (exactly 3 live neighbors)")
            else:
                analysis.append("→ Will remain dead (does not have exactly 3 live neighbors)")
                
        return "\n".join(analysis)
    
    @staticmethod
    def generate_evolution_analysis(grid: List[List[int]], steps: int = 1) -> str:
        """生成演化分析，关注会发生变化的细胞"""
        current_grid = [row[:] for row in grid]
        analysis = ["Evolution Analysis:\n"]
        grid_size = len(grid)
        initial_live_count = sum(sum(row) for row in current_grid)
        
        # 初始状态分析
        analysis.append("Initial State('1' stands for living cell and '0' stands for dead cell):")
        analysis.append(GameAnalysisGenerator.visualize_grid(current_grid))
        
        # 初始状态下所有细胞的分析
        will_change_cells = []  # 记录将要变化的细胞
        birth_cells = []  # 记录将要出生的细胞
        death_cells = []  # 记录将要死亡的细胞
        analysis.append("\nInitial Cell Analysis:")
        analysis.append("\nIdentifying cells that will change in the next step:")
        
        # 首先识别所有将要变化的细胞
        for row in range(grid_size):
            for col in range(grid_size):
                neighbors = count_neighbors(current_grid, row, col)
                will_change = False
                if current_grid[row][col] == 1:  # 活细胞
                    if neighbors < 2 or neighbors > 3:
                        will_change = True
                        death_cells.append((row, col))
                else:  # 死细胞
                    if neighbors == 3:
                        will_change = True
                        birth_cells.append((row, col))
                        
                if will_change:
                    will_change_cells.append((row, col))
        
        # 对将要变化的细胞进行详细分析
        for row, col in will_change_cells:
            analysis.append(f"\nCell ({row},{col}):")
            analysis.append(GameAnalysisGenerator.analyze_cell(current_grid, row, col))
            
        analysis.append(f"\nOther cells will maintain their current state according to the rules.")
        
        # 添加变化总结
        if will_change_cells:
            analysis.append("\nSummary of Predicted Changes:")
            if birth_cells:
                birth_positions = [f"({r},{c})" for r, c in birth_cells]
                analysis.append(f"- {len(birth_cells)} cells will become alive: {', '.join(birth_positions)}")
            if death_cells:
                death_positions = [f"({r},{c})" for r, c in death_cells]
                analysis.append(f"- {len(death_cells)} cells will die: {', '.join(death_positions)}")
        else:
            analysis.append("\nNo cells will change in the next iteration.")
            
        analysis.append(f"\n{'='*20} After 1 iteration {'='*20}")
            
        next_grid = [[0] * grid_size for _ in range(grid_size)]
        for row in range(grid_size):
            for col in range(grid_size):
                neighbors = count_neighbors(current_grid, row, col)
                # 计算下一状态
                if current_grid[row][col] == 1:
                    next_grid[row][col] = 1 if neighbors in [2, 3] else 0
                else:
                    next_grid[row][col] = 1 if neighbors == 3 else 0
        
        # 显示演化后的状态
        analysis.append("\nGrid State('1' stands for living cell and '0' stands for dead cell,[ ] represents cells that have undergone changes):")
        analysis.append(GameAnalysisGenerator.visualize_grid(next_grid, will_change_cells))
        
        # 计算并展示最终活细胞数
        analysis.append("\nCounting final live cells row by row:")
        final_live_count = 0
        for row in range(grid_size):
            row_live_count = sum(next_grid[row])
            final_live_count += row_live_count
            
            # 获取该行活细胞的位置
            live_positions = [(row, col) for col in range(grid_size) if next_grid[row][col] == 1]
            positions_str = ', '.join(f"({row},{col})" for row, col in live_positions)
            
            analysis.append(f"\nRow {row}:")
            analysis.append(f"- Live cells: {row_live_count}")
            if live_positions:
                analysis.append(f"- Positions: {positions_str}")
        
        # 总结变化
        population_change = final_live_count - initial_live_count
        analysis.extend([
            f"\nFinal Count:",
            f"- Initial live cells: {initial_live_count}",
            f"- Final live cells: {final_live_count}",
            f"- Population change: {population_change:+d}"
        ])
        
        return "\n".join(analysis)
    
    @staticmethod
    def generate_stability_analysis(grid: List[List[int]], steps_to_stability: int,
                            region_start: Tuple[int, int], region_size: int = 3) -> str:
        """
        生成区域稳定性分析。
        修复分析内容缺失的问题。
        """
        row_start, col_start = region_start
        current_grid = [row[:] for row in grid]
        grid_size = len(grid)
        analysis = ["Local Region Stability Analysis:\n"]
        
        def extract_region(grid: List[List[int]], start: Tuple[int, int]) -> List[List[int]]:
            """从完整棋盘中提取目标区域"""
            r_start, c_start = start
            region = []
            for i in range(region_size):
                row = []
                for j in range(region_size):
                    actual_row = (r_start + i) % grid_size
                    actual_col = (c_start + j) % grid_size
                    row.append(grid[actual_row][actual_col])
                region.append(row)
            return region
        
        def get_region_cells(start: Tuple[int, int]) -> List[Tuple[int, int]]:
            """获取目标区域在全局棋盘中的坐标列表"""
            r_start, c_start = start
            cells = []
            for i in range(region_size):
                for j in range(region_size):
                    actual_row = (r_start + i) % grid_size
                    actual_col = (c_start + j) % grid_size
                    cells.append((actual_row, actual_col))
            return cells
        
        def analyze_local_region(region: List[List[int]]) -> List[Dict[str, Any]]:
            """分析3x3区域内的状态变化（作为独立的生命游戏系统），包含详细的邻居信息"""
            unstable_cells = []
            for i in range(len(region)):
                for j in range(len(region)):
                    neighbors = 0
                    neighbor_info = []  # 存储邻居的详细信息
                    
                    # 遍历8个邻居位置
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                                
                            ni = (i + di) % len(region)
                            nj = (j + dj) % len(region)
                            
                            # 检查是否是通过边界循环得到的邻居
                            is_wrapped = ni != i + di or nj != j + dj
                            
                            # 记录此邻居的状态
                            if region[ni][nj] == 1:
                                neighbors += 1
                                position = ""
                                # 确定相对位置描述
                                if di == -1:
                                    position = "above"
                                    if dj == -1: position = "upper left"
                                    elif dj == 1: position = "upper right"
                                elif di == 1:
                                    position = "below"
                                    if dj == -1: position = "lower left"
                                    elif dj == 1: position = "lower right"
                                else:
                                    if dj == -1: position = "left"
                                    elif dj == 1: position = "right"
                                    
                                # 如果是通过边界循环得到的，添加说明
                                if is_wrapped:
                                    wrap_desc = []
                                    if ni != i + di:
                                        wrap_desc.append("top/bottom")
                                    if nj != j + dj:
                                        wrap_desc.append("left/right")
                                    position += f" (wrapped via {' and '.join(wrap_desc)} boundary)"
                                    
                                neighbor_info.append({
                                    "position": position,
                                    "coords": (ni, nj),
                                    "wrapped": is_wrapped
                                })
                    
                    current_state = region[i][j]
                    will_change = False
                    change_reason = ""
                    
                    # 判断是否会改变状态
                    if current_state == 1:  # 活细胞
                        if neighbors < 2:
                            will_change = True
                            change_reason = "underpopulation"
                        elif neighbors > 3:
                            will_change = True
                            change_reason = "overpopulation"
                    else:  # 死细胞
                        if neighbors == 3:
                            will_change = True
                            change_reason = "reproduction"
                    
                    if will_change:
                        unstable_cells.append({
                            "position": (i, j),
                            "current_state": current_state,
                            "neighbors": neighbors,
                            "neighbor_info": neighbor_info,
                            "reason": change_reason
                        })
            return unstable_cells
        
        # 1. 显示初始状态
        region_cells = get_region_cells(region_start)
        analysis.append("Step 0 - Initial State('1' stands for living cell and '0' stands for dead cell):")
        analysis.append(GameAnalysisGenerator.visualize_grid(current_grid, region_cells))
        
        # 显示目标区域
        initial_region = extract_region(current_grid, region_start)
        analysis.append(f"\nTarget 3x3 Region (starting at ({row_start},{col_start}),'1' stands for living cell and '0' stands for dead cell):")
        for row in initial_region:
            analysis.append(" ".join("1" if cell == 1 else "0" for cell in row))
        
        # 如果区域在初始状态就稳定，也要生成分析说明原因(change to final stable)
        initial_unstable = analyze_local_region(initial_region)
        if len(initial_unstable) == 0 and steps_to_stability == 0:
            analysis.append("\nLocal Stability Analysis (treating the region as an independent Game of Life):")
            analysis.append("\nThe region is stable in its initial state!")
            analysis.append("When treated as an independent 3x3 Game of Life:")
            # 分析每个细胞的状态和邻居情况
            initial_stable_analysis = []
            current_region=initial_region
            for i in range(region_size):
                for j in range(region_size):
                    cell_info = {
                        "position": (i, j),
                        "current_state": current_region[i][j],
                        "neighbors": 0,
                        "neighbor_info": []
                    }
                    
                    # 收集邻居信息
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni = (i + di) % region_size
                            nj = (j + dj) % region_size
                            
                            if current_region[ni][nj] == 1:
                                is_wrapped = ni != i + di or nj != j + dj
                                position = ""
                                if di == -1:
                                    position = "above"
                                    if dj == -1: position = "upper left"
                                    elif dj == 1: position = "upper right"
                                elif di == 1:
                                    position = "below"
                                    if dj == -1: position = "lower left"
                                    elif dj == 1: position = "lower right"
                                else:
                                    if dj == -1: position = "left"
                                    elif dj == 1: position = "right"
                                    
                                if is_wrapped:
                                    wrap_desc = []
                                    if ni != i + di:
                                        wrap_desc.append("top/bottom")
                                    if nj != j + dj:
                                        wrap_desc.append("left/right")
                                    position += f" (wrapped via {' and '.join(wrap_desc)} boundary)"
                                    
                                cell_info["neighbor_info"].append({
                                    "position": position,
                                    "coords": (ni, nj),
                                    "wrapped": is_wrapped
                                })
                                cell_info["neighbors"] += 1
                    
                    # 生成稳定状态的描述
                    state = "alive" if cell_info["current_state"] == 1 else "dead"
                    neighbor_count = cell_info["neighbors"]
                    
                    analysis.append(f"\nCell at local position ({i},{j}):")
                    analysis.append(f"- Currently {state}")
                    analysis.append(f"- Has {neighbor_count} live neighbors:")
                    
                    for neighbor in sorted(cell_info["neighbor_info"], key=lambda x: x["position"]):
                        ni, nj = neighbor["coords"]
                        analysis.append(f"  • Live neighbor {neighbor['position']} at ({ni},{nj})")
                    
                    if cell_info["current_state"] == 1:
                        analysis.append("- Will survive (has 2 or 3 live neighbors)")
                    else:
                        analysis.append("- Will remain dead (does not have exactly 3 live neighbors)")
            
            analysis.extend(initial_stable_analysis)

            return "\n".join(analysis)
        
        # 2. 逐步分析演化过程
        current_step = 0
        while current_step < steps_to_stability:
            current_step += 1
            analysis.append(f"\n{'='*50}")
            analysis.append(f"\nStep {current_step}:")
            
            # 2.1 分析全局演化
            next_grid = update_grid(current_grid)
            
            # 收集整个棋盘的变化
            global_changes = []
            for row in range(grid_size):
                for col in range(grid_size):
                    if current_grid[row][col] != next_grid[row][col]:
                        neighbors = count_neighbors(current_grid, row, col)
                        current_state = current_grid[row][col]
                        
                        reason = ""
                        if current_state == 1:  # 活细胞
                            if neighbors < 2:
                                reason = "underpopulation (fewer than 2 live neighbors)"
                            elif neighbors > 3:
                                reason = "overpopulation (more than 3 live neighbors)"
                        else:  # 死细胞
                            if neighbors == 3:
                                reason = "reproduction (exactly 3 live neighbors)"
                                
                        global_changes.append({
                            "position": (row, col),
                            "from_state": current_state,
                            "to_state": next_grid[row][col],
                            "neighbors": neighbors,
                            "reason": reason
                        })
            
            # 报告全局演化变化
            if global_changes:
                analysis.append("\nGlobal Evolution Changes:")
                for change in global_changes:
                    row, col = change["position"]
                    from_state = "alive" if change["from_state"] == 1 else "dead"
                    to_state = "alive" if change["to_state"] == 1 else "dead"
                    analysis.append(f"\nCell at global position ({row},{col}):")
                    analysis.append(f"- Changed from {from_state} to {to_state}")
                    analysis.append(f"- Reason: {change['reason']}")
            else:
                analysis.append("\nNo cells changed in the global evolution.")
                
            # 显示全局演化后的状态
            analysis.append("\nAfter global evolution:")
            analysis.append(GameAnalysisGenerator.visualize_grid(next_grid, region_cells))
            
            # 2.2 分析目标区域的局部稳定性
            next_region = extract_region(next_grid, region_start)
            current_region = next_region 
            analysis.append("\nLocal Stability Analysis (treating the region as an independent Game of Life):")
            
            # 分析区域内的状态
            unstable_cells = analyze_local_region(next_region)
            
            def generate_cell_analysis(cell: Dict[str, Any]) -> List[str]:
                """生成单个细胞的分析文本"""
                i, j = cell["position"]
                state = "alive" if cell["current_state"] == 1 else "dead"
                
                analysis = [
                    f"\nCell at local position ({i},{j}):",
                    f"- Currently {state}",
                    f"- Has {cell['neighbors']} live neighbors:"
                ]
                
                # 添加每个活邻居的详细信息
                for neighbor in sorted(cell["neighbor_info"], key=lambda x: x["position"]):
                    ni, nj = neighbor["coords"]
                    analysis.append(f"  • Live neighbor {neighbor['position']} at ({ni},{nj})")
                
                # 添加状态变化信息
                analysis.append(f"- Would change due to {cell['reason']}")
                
                return analysis

            # 在分析局部稳定性时，替换原有的代码：
            if unstable_cells:
                analysis.append("\nThe region is not yet stable. Here's why:")
                for cell in unstable_cells:
                    analysis.extend(generate_cell_analysis(cell))
            else:
                analysis.append("\nThe region has reached stability!")
                analysis.append("When treated as an independent 3x3 Game of Life:")
                
                # 即使对于稳定的情况，也生成每个细胞的详细分析
                stable_analysis = []
                for i in range(region_size):
                    for j in range(region_size):
                        cell_info = {
                            "position": (i, j),
                            "current_state": current_region[i][j],
                            "neighbors": 0,
                            "neighbor_info": []
                        }
                        
                        # 收集邻居信息
                        for di in [-1, 0, 1]:
                            for dj in [-1, 0, 1]:
                                if di == 0 and dj == 0:
                                    continue
                                ni = (i + di) % region_size
                                nj = (j + dj) % region_size
                                
                                if current_region[ni][nj] == 1:
                                    is_wrapped = ni != i + di or nj != j + dj
                                    position = ""
                                    if di == -1:
                                        position = "above"
                                        if dj == -1: position = "upper left"
                                        elif dj == 1: position = "upper right"
                                    elif di == 1:
                                        position = "below"
                                        if dj == -1: position = "lower left"
                                        elif dj == 1: position = "lower right"
                                    else:
                                        if dj == -1: position = "left"
                                        elif dj == 1: position = "right"
                                        
                                    if is_wrapped:
                                        wrap_desc = []
                                        if ni != i + di:
                                            wrap_desc.append("top/bottom")
                                        if nj != j + dj:
                                            wrap_desc.append("left/right")
                                        position += f" (wrapped via {' and '.join(wrap_desc)} boundary)"
                                        
                                    cell_info["neighbor_info"].append({
                                        "position": position,
                                        "coords": (ni, nj),
                                        "wrapped": is_wrapped
                                    })
                                    cell_info["neighbors"] += 1
                        
                        # 生成稳定状态的描述
                        state = "alive" if cell_info["current_state"] == 1 else "dead"
                        neighbor_count = cell_info["neighbors"]
                        
                        analysis.append(f"\nCell at local position ({i},{j}):")
                        analysis.append(f"- Currently {state}")
                        analysis.append(f"- Has {neighbor_count} live neighbors:")
                        
                        for neighbor in sorted(cell_info["neighbor_info"], key=lambda x: x["position"]):
                            ni, nj = neighbor["coords"]
                            analysis.append(f"  • Live neighbor {neighbor['position']} at ({ni},{nj})")
                        
                        if cell_info["current_state"] == 1:
                            analysis.append("- Will survive (has 2 or 3 live neighbors)")
                        else:
                            analysis.append("- Will remain dead (does not have exactly 3 live neighbors)")
                
                analysis.extend(stable_analysis)

            return "\n".join(analysis)
    @staticmethod
    def generate_cell_change_analysis(grid: List[List[int]], target_cell: Tuple[int, int], 
                                    iterations: int) -> str:
        """生成目标细胞状态变化分析"""
        row, col = target_cell
        current_grid = [row[:] for row in grid]
        analysis = ["Target Cell State Change Analysis:\n"]
        state_sequence = []  # 记录状态序列
        grid_size = len(grid)
        
        # 记录初始状态
        state_sequence.append(current_grid[row][col])
        
        # 初始状态分析
        analysis.append("Initial State('1' stands for living cell and '0' stands for dead cell):")
        analysis.append(GameAnalysisGenerator.visualize_grid(current_grid, [target_cell]))
        
        # 对目标细胞进行初始分析
        analysis.append("\nTarget Cell Initial Status:")
        analysis.append(GameAnalysisGenerator.analyze_cell(current_grid, row, col))
        
        # 分析将要变化的细胞
        changing_cells = GameAnalysisGenerator._identify_changing_cells(current_grid)
        if changing_cells:
            analysis.append("\nCells that will change in the next step:")
            for r, c in changing_cells:
                neighbors = count_neighbors(current_grid, r, c)
                if current_grid[r][c] == 1:
                    reason = "underpopulation" if neighbors < 2 else "overpopulation"
                    analysis.append(f"• Cell ({r},{c}): alive → dead (due to {reason}, has {neighbors} neighbors)")
                else:
                    analysis.append(f"• Cell ({r},{c}): dead → alive (reproduction, has {neighbors} neighbors)")
        
        # 逐步演化分析
        for step in range(iterations):
            analysis.append(f"\n{'='*20} Step {step + 1} {'='*20}")
            next_grid = [[0] * grid_size for _ in range(grid_size)]
            
            # 计算新状态
            for r in range(grid_size):
                for c in range(grid_size):
                    neighbors = count_neighbors(current_grid, r, c)
                    if current_grid[r][c] == 1:
                        next_grid[r][c] = 1 if neighbors in [2, 3] else 0
                    else:
                        next_grid[r][c] = 1 if neighbors == 3 else 0
            
            # 记录目标细胞的新状态
            state_sequence.append(next_grid[row][col])
            
            # 显示新状态
            analysis.append("\nNew Grid State:")
            analysis.append(GameAnalysisGenerator.visualize_grid(next_grid, [target_cell]))
            
            # 对目标细胞进行详细分析
            analysis.append("\nTarget Cell Status:")
            analysis.append(GameAnalysisGenerator.analyze_cell(next_grid, row, col))
            
            # 分析下一步将变化的细胞
            changing_cells = GameAnalysisGenerator._identify_changing_cells(next_grid)
            if changing_cells:
                analysis.append("\nCells that will change in the next step:")
                for r, c in changing_cells:
                    neighbors = count_neighbors(next_grid, r, c)
                    if next_grid[r][c] == 1:
                        reason = "underpopulation" if neighbors < 2 else "overpopulation"
                        analysis.append(f"• Cell ({r},{c}): alive → dead (due to {reason}, has {neighbors} neighbors)")
                    else:
                        analysis.append(f"• Cell ({r},{c}): dead → alive (reproduction, has {neighbors} neighbors)")
            else:
                analysis.append("\nNo cells will change in the next step.")
            
            current_grid = next_grid
        
        # 生成状态变化序列
        analysis.append("\n" + "="*50)
        analysis.append("\nTarget Cell State Change Summary:")
        state_changes = []
        for i, state in enumerate(state_sequence):
            if i == 0:
                state_changes.append(f"Initially: {'alive' if state == 1 else 'dead'}")
            else:
                state_changes.append(f"Step {i}: {'alive' if state == 1 else 'dead'}")
        
        analysis.append(" → ".join(state_changes))
        
        return "\n".join(analysis)
        
    @staticmethod
    def _identify_changing_cells(grid: List[List[int]]) -> List[Tuple[int, int]]:
        """识别将要在下一步改变状态的细胞"""
        grid_size = len(grid)
        changing_cells = []
        
        for r in range(grid_size):
            for c in range(grid_size):
                neighbors = count_neighbors(grid, r, c)
                if grid[r][c] == 1:  # 活细胞
                    if neighbors < 2 or neighbors > 3:
                        changing_cells.append((r, c))
                else:  # 死细胞
                    if neighbors == 3:
                        changing_cells.append((r, c))
                        
        return changing_cells
    
def generate_state_info_question(grid: List[List[int]], data_id: int, plot_level: str) -> Dict[str, Any]:
    """Generate a question about counting live cells."""
    try:
        grid_size = len(grid)
        total_count = sum(sum(row) for row in grid)
        
        # 使用分析生成器先生成分析，确保计数正确
        analysis_generator = GameAnalysisGenerator()
        analysis = analysis_generator.generate_state_info_analysis(grid)
        
        # 验证分析中的计数与直接计算的结果一致
        analysis_count = int(analysis.split("Total live cells: ")[1].split()[0])
        assert total_count == analysis_count, f"Count mismatch: {total_count} vs {analysis_count}"
        
        # 生成选项 - 现在返回选项列表和正确答案的索引
        options_generator = MCQOptionsGenerator()
        options, correct_index = options_generator.generate_numeric_options(
            correct_answer=total_count,
            num_options=8,
            min_val=0,
            max_val=grid_size * grid_size
        )
        # 格式化选项 - 使用正确答案的索引
        formatted_options, options_text, correct_letter = options_generator.format_options(
            options, correct_index)
        
        analysis += f"\n\nThe option is {correct_letter}."
        
        question_text = f"{GAME_RULES}\n\nHow many live cells are currently in the grid?\n\nOptions:\n{options_text}"
        
        return {
            "data_id": f"lifegame-mcq-{data_id:05d}-state",
            "qa_type": "StateInfo",
            **QUESTION_SETTINGS["StateInfo"],
            "plot_level": plot_level,
            "question": question_text,
            "answer": correct_letter,
            "analysis": analysis,
            "options": formatted_options
        }
    except Exception as e:
        print(f"Error (StateInfo): {str(e)}")
        return None

def generate_action_outcome_question(grid: List[List[int]], data_id: int, plot_level: str) -> Dict[str, Any]:
    """Generate a question about future grid state."""
    try:
        iterations = 1
        current_grid = [row[:] for row in grid]
        grid_size = len(grid)
        
        # Simulate evolution to get final count
        next_grid = update_grid(current_grid)
        final_count = sum(sum(row) for row in next_grid)
        
        # Generate options - 使用新的接口返回选项和正确答案索引
        options_generator = MCQOptionsGenerator()
        options, correct_index = options_generator.generate_numeric_options(
            correct_answer=final_count,
            num_options=8,
            min_val=0,
            max_val=grid_size * grid_size
        )
        
        # Format options - 传入正确答案索引
        formatted_options, options_text, correct_letter = options_generator.format_options(
            options, correct_index)
        
        # Generate analysis
        analysis_generator = GameAnalysisGenerator()
        analysis = analysis_generator.generate_evolution_analysis(grid, steps=iterations)
        analysis += f"\n\nThe option is {correct_letter}."
        
        question_text = f"{GAME_RULES}\n\nAfter {iterations} iterations, how many live cells will remain in the grid?\n\nOptions:\n{options_text}"
        
        return {
            "data_id": f"lifegame-mcq-{data_id:05d}-action",
            "qa_type": "ActionOutcome",
            **QUESTION_SETTINGS["ActionOutcome"],
            "plot_level": plot_level,
            "question": question_text,
            "answer": correct_letter,
            "analysis": analysis,
            "options": formatted_options
        }
    except Exception as e:
        print(f"Error (ActionOutcome): {str(e)}")
        return None

def generate_cell_change_question(grid: List[List[int]], data_id: int, plot_level: str) -> Dict[str, Any]:
    """Generate a question about cell state changes."""
    try:
        grid_size = len(grid)
        iterations = {
            "Easy": 4,
            "Medium": 3,
            "Hard": 2
        }.get(plot_level, 4)
        
        # Select target cell
        target_cell = select_target_cell(grid)
        if target_cell is None:
            return None
            
        row, col = target_cell
        
        # Track state changes
        current_grid = [row[:] for row in grid]
        state_sequence = [current_grid[row][col]]
        
        for _ in range(iterations):
            current_grid = update_grid(current_grid)
            state_sequence.append(current_grid[row][col])
        
        # Generate options - 使用新的接口返回序列和正确答案索引
        options_generator = MCQOptionsGenerator()
        sequence_options, correct_index = options_generator.generate_sequence_options(
            correct_sequence=state_sequence,
            possible_values=[0, 1],
            num_options=8
        )
        
        # Convert sequences to text
        options_text = [state_sequence_to_text(seq) for seq in sequence_options]
        # Format options - 传入正确答案索引
        formatted_options, options_text_block, correct_letter = options_generator.format_options(
            options_text, correct_index)
        
        # Generate analysis
        analysis_generator = GameAnalysisGenerator()
        analysis = analysis_generator.generate_cell_change_analysis(grid, target_cell, iterations)
        analysis += f"\n\nThe option is {correct_letter}."
        
        question_text = (
            f"{GAME_RULES}\n\n"
            f"Consider the cell at position ({row}, {col}). "
            f"How will its state change over the next {iterations} iterations?\n\n"
            f"Options:\n{options_text_block}"
        )
        
        return {
            "data_id": f"lifegame-mcq-{data_id:05d}-cell-changes",
            "qa_type": "ActionOutcome",
            **QUESTION_SETTINGS["CellChangeCount"],
            "plot_level": plot_level,
            "question": question_text,
            "answer": correct_letter,
            "analysis": analysis,
            "options": formatted_options
        }
    except Exception as e:
        print(f"Error (CellChangeCount): {str(e)}")
        return None

def generate_stability_question(grid: List[List[int]], data_id: int, plot_level: str) -> Dict[str, Any]:
    """
    生成关于局部区域稳定性的问题。改进的版本：
    1. 更智能地选择目标区域
    2. 更准确地计算稳定性
    3. 为问题提供更清晰的上下文
    4. 生成更有教育意义的选项
    """
    try:
        grid_size = len(grid)
        region_size = 3  # 固定使用3x3区域
        
        # 1. 智能选择目标区域（改进的选择逻辑）
        candidate_regions = []
        
        for row in range(grid_size):
            for col in range(grid_size):
                # 提取区域信息
                live_cells = 0
                border_cells = 0
                center_cells = 0
                
                # 检查3x3区域
                for i in range(region_size):
                    for j in range(region_size):
                        actual_row = (row + i) % grid_size
                        actual_col = (col + j) % grid_size
                        if grid[actual_row][actual_col] == 1:
                            live_cells += 1
                            if i == 0 or i == 2 or j == 0 or j == 2:
                                border_cells += 1
                            else:
                                center_cells += 1
                
                # 评分标准：
                # 1. 保证区域有足够的活细胞以产生变化
                # 2. 不需要太多活细胞以避免过于复杂
                # 3. 考虑活细胞的分布
                if live_cells >= 2:  # 降低最小活细胞要求
                    region_score = (
                        live_cells * 2 +        # 基础分：活细胞数
                        (border_cells > 0) +    # 有边界活细胞加分
                        (center_cells > 0) +    # 有中心活细胞加分
                        (4 <= live_cells <= 6) * 2  # 适中的活细胞数加分
                    )
                    
                    # 收集所有可能的候选区域
                    candidate_regions.append((row, col, region_score))
        
        # 如果没有找到任何候选区域，返回None
        if not candidate_regions:
            print(f"No suitable regions found in grid")
            return None
            
        # 按分数排序并从top 3中随机选择一个
        candidate_regions.sort(key=lambda x: x[2], reverse=True)
        top_candidates = candidate_regions[:min(3, len(candidate_regions))]
        row_start, col_start, score = random.choice(top_candidates)
        best_region = (row_start, col_start)
        
            
        # 2. 计算该区域达到稳定的步数
        row_start, col_start = best_region
        current_grid = [row[:] for row in grid]
        
        def extract_region(grid: List[List[int]], start: Tuple[int, int]) -> List[List[int]]:
            """从完整棋盘中提取目标区域"""
            r_start, c_start = start
            region = []
            for i in range(region_size):
                row = []
                for j in range(region_size):
                    actual_row = (r_start + i) % grid_size
                    actual_col = (c_start + j) % grid_size
                    row.append(grid[actual_row][actual_col])
                region.append(row)
            return region
        
        def is_region_stable(region: List[List[int]]) -> bool:
            """检查区域是否达到稳定状态（作为独立的生命游戏）"""
            for i in range(region_size):
                for j in range(region_size):
                    neighbors = 0
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni = (i + di) % region_size
                            nj = (j + dj) % region_size
                            neighbors += region[ni][nj]
                    
                    # 检查是否会变化
                    if region[i][j] == 1:  # 活细胞
                        if neighbors < 2 or neighbors > 3:
                            return False
                    else:  # 死细胞
                        if neighbors == 3:
                            return False
            return True
        
        # 模拟进化直到区域稳定或达到最大步数
        max_steps = 20
        steps_to_stability = -1
        history = []  # 记录区域历史状态
        
        for step in range(max_steps):
            current_region = extract_region(current_grid, best_region)
            region_hash = tuple(map(tuple, current_region))
            
            # 检查是否达到稳定
            if is_region_stable(current_region):
                steps_to_stability = step
                break
                
            # 检查是否出现循环
            if region_hash in history:
                # cycle_start = history.index(region_hash)
                steps_to_stability = step
                break
                
            history.append(region_hash)
            current_grid = update_grid(current_grid)
        
        if steps_to_stability == -1:
            print("Failed to reach stability within maximum steps")
            return None
            
        # 3. 生成问题选项
        options_generator = MCQOptionsGenerator()
        options, correct_index = options_generator.generate_numeric_options(
            correct_answer=steps_to_stability,
            num_options=8,
            min_val=1,
            max_val=max(steps_to_stability + 3, 8)
        )
        
        # 格式化选项
        formatted_options, options_text, correct_letter = options_generator.format_options(
            options, correct_index)
        
        # 4. 生成分析
        analysis_generator = GameAnalysisGenerator()
        analysis = analysis_generator.generate_stability_analysis(
            grid, steps_to_stability, best_region, region_size=3)
        analysis += f"\n\nThe option is {correct_letter}."
        
        # 5. 构建问题文本
        question_text = (
            f"{GAME_RULES}\n\n"
            f"Consider the 3x3 region starting at cell ({best_region[0]},{best_region[1]}).\n\n"
            f"When analyzing this region's stability:\n"
            "• We treat it as an independent Game of Life system\n"
            "• The region is stable when either:\n"
            "  - All cells maintain their current states, or\n"
            "  - The cells form a repeating pattern\n"
            "How many iterations will it take for this region to reach a stable state?\n\n"
            f"Options:\n{options_text}"
        )
        
        return {
            "data_id": f"lifegame-mcq-{data_id:05d}-stability",
            "qa_type": "ActionOutcome",
            **QUESTION_SETTINGS["StabilitySteps"],
            "plot_level": plot_level,
            "question": question_text,
            "answer": correct_letter,
            "analysis": analysis,
            "options": formatted_options
        }
        
    except Exception as e:
        print(f"Error (StabilitySteps): {str(e)}")
        return None

class DatasetGenerator:
    """数据集生成器类，使用跨平台的超时保护机制"""
    
    def __init__(self, num_samples: int):
        self.num_samples = num_samples
        self.dataset = []
        self.board_idx = 0
        self.failed_attempts = 0
        self.max_failed_attempts = 1000
        self.generation_start_time = None
        self.generation_timeout = 300  # 5分钟的总体超时时间
        self.stats = {
            "total_attempts": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "type_counts": {},
            "errors": [],
            "timeouts": 0
        }

    def check_timeout(self) -> bool:
        """检查是否超过了总体超时时间"""
        if self.generation_start_time is None:
            return False
        return time.time() - self.generation_start_time > self.generation_timeout

    @timeout_decorator(20)  # 单个问题生成的超时时间为20秒
    def _generate_single_question(self, plot_level: str, question_type: str) -> bool:
        """生成单个问题，改进的版本避免无效文件生成"""
        try:
            grid_size = GRID_SETTINGS[plot_level]
            
            # 1. 首先生成并验证网格
            start_time = time.time()
            grid = None
            valid_grid = False
            
            for _ in range(50):
                if time.time() - start_time > 15:  # 网格生成15秒超时
                    break
                    
                temp_grid = init_grid(grid_size)
                live_ratio = sum(sum(row) for row in temp_grid) / (grid_size * grid_size)
                
                if 0.2 <= live_ratio <= 0.4:
                    grid = temp_grid
                    valid_grid = True
                    break
            
            if not valid_grid:
                self.failed_attempts += 1
                return False
            
            # 2. 生成问题
            start_time = time.time()
            question_generators = {
                "StateInfo": generate_state_info_question,
                "ActionOutcome": generate_action_outcome_question,
                "CellChangeCount": generate_cell_change_question,
                "StabilitySteps": generate_stability_question
            }
            
            question = question_generators[question_type](grid, self.board_idx, plot_level)
            if question is None or time.time() - start_time > 15:  # 问题生成15秒超时
                self.failed_attempts += 1
                return False
                
            # 3. 只有在问题成功生成后才保存文件
            state_path, image_path = save_state_and_image(grid, self.board_idx, grid_size)
            
            question.update({
                "image": image_path.replace("lifegame_dataset/", ""),
                "state": state_path.replace("lifegame_dataset/", "")
            })
            
            self.dataset.append(question)
            self.board_idx += 1
            self.stats["type_counts"][question_type] = self.stats["type_counts"].get(question_type, 0) + 1
            return True
                
        except Exception as e:
            self.failed_attempts += 1
            self.stats["errors"].append(f"Error ({question_type}): {str(e)}")
            return False

    def generate_dataset(self):
        """生成数据集的主函数"""
        print("\n开始生成数据集...")
        ensure_directories()
        self.generation_start_time = time.time()
        
        # 准备问题类型组合
        plot_levels = list(GRID_SETTINGS.keys())
        question_types = list(QUESTION_SETTINGS.keys())
        all_combinations = list(itertools.product(plot_levels, question_types))
        
        # 计算需要的重复次数
        repeats = (self.num_samples + len(all_combinations) - 1) // len(all_combinations)
        
        with tqdm(total=self.num_samples, desc="总体进度") as pbar:
            for _ in range(repeats):
                if self.check_timeout():
                    print(f"\n警告：数据集生成总时间超过 {self.generation_timeout} 秒")
                    break
                    
                if self.failed_attempts >= self.max_failed_attempts:
                    print(f"\n警告：达到最大失败尝试次数 ({self.max_failed_attempts})")
                    break
                    
                if len(self.dataset) >= self.num_samples:
                    break
                    
                random.shuffle(all_combinations)
                for plot_level, question_type in all_combinations:
                    if len(self.dataset) >= self.num_samples:
                        break
                        
                    self.stats["total_attempts"] += 1
                    result = self._generate_single_question(plot_level, question_type)
                    
                    if result is None:  # 超时
                        self.stats["timeouts"] += 1
                        self.failed_attempts += 1
                    elif result:  # 成功
                        self.stats["successful_generations"] += 1
                        pbar.update(1)
                    else:  # 其他失败
                        self.stats["failed_generations"] += 1
                    
                    # 更新进度条描述
                    pbar.set_description(
                        f"总体进度 [成功: {len(self.dataset)}, "
                        f"超时: {self.stats['timeouts']}, "
                        f"失败: {self.failed_attempts}]"
                    )
        
        self._save_dataset_and_report()

    def _save_dataset_and_report(self):
        """保存数据集并生成报告"""
        # 保存数据集
        with open(DATASET_FILE, "w", encoding="utf-8") as f:
            json.dump(self.dataset, f, ensure_ascii=False, indent=2)
        
        # 生成报告
        total_time = time.time() - self.generation_start_time
        
        print("\n=== 数据集生成报告 ===")
        print(f"总生成时间: {total_time:.1f} 秒")
        print(f"总生成问题数: {len(self.dataset)}")
        print(f"成功率: {(self.stats['successful_generations'] / self.stats['total_attempts'] * 100):.1f}%")
        
        print("\n问题类型分布:")
        for qtype, count in self.stats["type_counts"].items():
            percentage = count / len(self.dataset) * 100
            print(f"{qtype}: {count} 个问题 ({percentage:.1f}%)")
        
        if self.stats["timeouts"] > 0:
            print(f"\n超时次数: {self.stats['timeouts']}")
        
        if self.stats["errors"]:
            print("\n错误统计:")
            error_counts = {}
            for error in self.stats["errors"]:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"- {error}: {count} 次")

def generate_dataset(num_samples: int = 5000):
    """生成数据集的入口函数"""
    try:
        generator = DatasetGenerator(num_samples)
        generator.generate_dataset()
    except KeyboardInterrupt:
        print("\n用户中断了生成过程")
    except Exception as e:
        print(f"\n生成过程发生错误: {str(e)}")
        
if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    generate_dataset(500)
