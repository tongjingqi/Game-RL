import random
import json
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

# 确保文件夹存在
if not os.path.exists('tents_dataset'):
    os.makedirs('tents_dataset')
if not os.path.exists('tents_dataset/states'):
    os.makedirs('tents_dataset/states')
if not os.path.exists('tents_dataset/images'):
    os.makedirs('tents_dataset/images')


tents_description = f"This is a Tents puzzle. In this game, you will start with a grid that only marks the positions of the trees, the number of tents that should be in each row, and the number of tents that should be in each column. "\
                    f"Your goal is to place the tents step by step on the grid according to the following rules until there are no more missing tents in the grid:\n"\
                    f"1. **Valid Cell States**: Each cell in the grid can only be in one of the following three states, which are empty, containing a tree, and containing a tent.\n"\
                    f"2. **Equal Number of Tents and Trees**: The total number of tents you place must be equal to the number of trees present on the grid.\n"\
                    f"3. **Tent Placement Restrictions**: Tents can only be placed horizontally or vertically (diagonally does not count) adjacent to at least one tree.\n"\
                    f"4. **No Adjacent Tents**: No two tents can be adjacent, including diagonally.\n"\
                    f"5. **Row and Column Constraints**: The number of tents that should be placed in each row or column is given by the numbers on the left and top of the grid.\n\n"\
                    f"The positions of the trees and the tents are represented by their icons on the grid respectively. "\
                    f"The blue numbers on the left and top of the grid indicate the number of tents that should be placed in each row or column finally. "\
                    f"The black numbers on the left and top of the grid are the row numbers and column numbers, respectively. "\
                    f"In the coordinates (x, y), x corresponds to the row number, and y corresponds to the column number. "\
                    f"The row and column numbering both start from 0, meaning that the first row is actually row 0. The origin (0,0) is in the upper-left corner of the grid.\n\n"\
                    f"In the current state, only some of the correct positions of the tents are marked in the grid."


# 难度定义                 
def generate_plot_level(x, y):
    if x * y <= 50:
        return "Easy"
    elif x * y <= 100:
        return "Medium"
    else:
        return "Hard"

# 用于生成一个随机谜面
def generate_tents_puzzle(grid_size, num_trees):
    width, height = grid_size
    while True:
        grid = [['' for _ in range(width)] for _ in range(height)]
        tent_available = [[False for _ in range(width)] for _ in range(height)]
        
        # 随机放置树
        tree_positions = set()
        while len(tree_positions) < num_trees:
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
            if grid[x][y] == '' :
                potential_positions = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                for (tx, ty) in potential_positions:
                    if 0 <= ty < width and 0 <= tx < height and grid[tx][ty] == '':
                        tent_available[tx][ty] = True
                tree_positions.add((x, y))
                tent_available[x][y] = False
                grid[x][y] = 'T'  # T代表树
        
        # 随机放置帐篷
        tent_positions = set()
        trying_times = 0
        while len(tent_positions) < num_trees:
            x, y = random.choice(list(tree_positions))
            # 检查周围是否可以放帐篷
            potential_positions = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            random.shuffle(potential_positions)
            for (tx, ty) in potential_positions:
                if 0 <= ty < width and 0 <= tx < height and tent_available[tx][ty] == True:
                    grid[tx][ty] = 'X'  # X代表帐篷
                    tent_available[tx][ty] = False
                    tent_positions.add((tx, ty))
                    near_positions = [(tx+1, ty), (tx+1, ty+1), (tx+1, ty-1), (tx, ty+1), 
                                    (tx, ty-1), (tx-1, ty+1), (tx-1, ty), (tx-1, ty-1)]
                    for (nx, ny) in near_positions:
                        if 0 <= ny < width and 0 <= nx < height :
                            tent_available[nx][ny] = False  # 周围的位置也不能放帐篷
                    break
            trying_times += 1
            if trying_times > 10000:
                break
        if trying_times <= 10000:
            break

    # 计算每行和每列中的帐篷数量
    row_tent_counts = [0] * height
    col_tent_counts = [0] * width
    for tx, ty in tent_positions:
        row_tent_counts[tx] += 1
        col_tent_counts[ty] += 1        
    
    # 对坐标列表进行排序
    tree_positions = set(sorted(list(tree_positions)))
    tent_positions = set(sorted(list(tent_positions)))

    return grid, tree_positions, tent_positions, row_tent_counts, col_tent_counts

# 随机移除若干帐篷
def remove_random_tents(grid, tent_positions, num_to_remove):
    # 随机选择要删除的帐篷位置
    removed_tents = random.sample(list(tent_positions), min(num_to_remove, len(tent_positions)))
    
    # 从 grid 中删除帐篷，并从 tent_positions 集合中移除
    for tx, ty in removed_tents:
        grid[tx][ty] = ''  # 在网格中去掉帐篷
        tent_positions.remove((tx, ty))  # 从 tent_positions 集合中删除该位置
    
    return removed_tents

# 生成并保存图片
def save_visualization(grid, row_tent_counts, col_tent_counts, puzzle_number):
    # 调整图像的大小
    fig, ax = plt.subplots(figsize=(6, 6))  # 图像大小为 6x6 英寸（增加图像大小）
    ax.set_aspect('equal')

    width, height = len(grid[0]), len(grid)

    # 设置坐标轴的范围
    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(-0.5, height - 0.5)

    # 绘制网格
    for y in range(width + 1):
        ax.axvline(y - 0.5, color='black', lw=1)
    for x in range(height + 1):
        ax.axhline(x - 0.5, color='black', lw=1)

    # 加载树和帐篷图片
    tree_img = mpimg.imread('tree.png')
    tent_img = mpimg.imread('tent.png')

    # 反转图片（翻转180度）
    tree_img = np.flipud(np.fliplr(tree_img))  # 水平和垂直翻转树的图片
    tent_img = np.flipud(np.fliplr(tent_img))  # 水平和垂直翻转帐篷的图片

    # 绘制每个方格的内容（使用图片替代色块）
    for x in range(height):
        for y in range(width):
            if grid[x][y] == 'T':  # 树
                # 使用树图片
                ax.imshow(tree_img, extent=(y - 0.5, y + 0.5, x - 0.5, x + 0.5), aspect='auto')
            elif grid[x][y] == 'X':  # 帐篷
                # 使用帐篷图片
                ax.imshow(tent_img, extent=(y - 0.5, y + 0.5, x - 0.5, x + 0.5), aspect='auto')

    # 在左侧添加每行的帐篷数量，调整位置，使其远离网格
    for x in range(height):
        ax.text(-width/7-0.1, x, str(row_tent_counts[x]), color='#0033CC', ha='center', va='center', fontsize=18, fontweight='bold')

    # 在下方添加每列的帐篷数量，调整位置，使其远离网格
    for y in range(width):
        ax.text(y, -width/7-0.1, str(col_tent_counts[y]), color='#0033CC', ha='center', va='center', fontsize=18, fontweight='bold')

    # 设置坐标轴的刻度标签字体大小
    ax.tick_params(axis='both', which='major', labelsize=15)  # 设置坐标轴刻度标签字体大小
    # 确保每个坐标轴都有刻度
    ax.set_xticks(range(width))
    ax.set_yticks(range(height))

    # 反转纵轴，使得坐标原点位于左上角
    ax.invert_yaxis()
    # 调整横轴的位置，使其在上方
    ax.xaxis.set_ticks_position('top')

    # 保存为 PNG 格式，增加dpi值提高分辨率
    plt.savefig(f'tents_dataset/images/{puzzle_number:05d}.png', dpi=100, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)

# 生成并保存谜面
def save_puzzle_to_json(grid_size, tree_positions, tent_positions, removed_tents, puzzle_number):
    puzzle_data = {
        'size': grid_size,
        'tree_positions': list(tree_positions),
        'tent_positions': list(tent_positions),
        'removed_tents': list(removed_tents),
    }
    with open(f'tents_dataset/states/{puzzle_number:05d}.json', 'w') as json_file:
        json.dump(puzzle_data, json_file, indent=4)

# 辅助函数：检查该位置是否符合放置新帐篷的条件
def is_valid_new_tent_position(x, y, grid, tree_positions, tent_positions, row_tent_counts, col_tent_counts):
    # 1. 该位置已经放了树
    if (x, y) in tree_positions:
        return False, "The position is already occupied by a tree."
    # 2. 该位置已经放了帐篷
    if (x, y) in tent_positions:
        return False, "The position is already occupied by a tent."
    # 3. 该位置上下左右都没有树
    adjacent_tree_found = False
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(grid[0]) and 0 <= nx < len(grid):
            if (nx, ny) in tree_positions:
                adjacent_tree_found = True
                adjacent_tree = (nx, ny)
                break
    if not adjacent_tree_found:
        return False, "There is no adjacent tree."
    # 4. 该位置的周围八格存在帐篷
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            nx, ny = x + dx, y + dy
            if (nx, ny) in tent_positions and (dx != 0 or dy != 0):
                return False, f"There is an adjacent tent at ({nx}, {ny})."
    # 5. 该行的帐篷总数已达标
    if row_tent_counts[x] <= sum(1 for tx, ty in tent_positions if tx == x):
        return False, f"The current row, row {x}, already has the maximum number of tents, which is {row_tent_counts[x]} tents."
    # 6. 该列的帐篷总数已达标
    if col_tent_counts[y] <= sum(1 for tx, ty in tent_positions if ty == y):
        return False, f"The current column, column {y}, already has the maximum number of tents, which is {col_tent_counts[y]} tents."
    # 该位置符合所有条件       
    # 获取该位置所在行和列分别缺少多少个帐篷
    row_missing_tents = row_tent_counts[x] - sum(1 for (tx, ty) in tent_positions if tx == x)  # 该行缺少的帐篷数量
    col_missing_tents = col_tent_counts[y] - sum(1 for (tx, ty) in tent_positions if ty == y)  # 该列缺少的帐篷数量

    # 为该有效位置添加详细信息
    reason = f"  - The adjacent tree is at ({adjacent_tree[0]}, {adjacent_tree[1]}).\n"
    reason += f"  - The current row, row {x}, still needs {row_missing_tents} more tents.\n"
    reason += f"  - The current column, column {y}, still needs {col_missing_tents} more tents.\n"
    return True, reason

# 保存数据
def save_data(question_data, path):
    # 尝试读取现有的json文件内容，如果文件不存在则创建一个空列表
    try:
        with open(path, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = []  # 文件不存在时，创建一个空列表
    
    # 将新的问题数据添加到现有的列表中
    data.append(question_data)
    
    # 将更新后的列表写回到文件中
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# 某一行有多少个帐篷
def gen_num_tents_in_row_fill(grid, tent_positions, puzzle_number):
    row_tent_counts = [0] * len(grid)
    row_tent_positions = [[] for _ in range(len(grid))]
    for tx, ty in tent_positions:
        row_tent_counts[tx] += 1
        row_tent_positions[tx].append((tx, ty))

    # 随机选择一行提问
    row_to_ask = random.randint(0, len(grid) - 1)
    question = tents_description + \
            f"Given the current state, how many tents are there in row {row_to_ask} currently?\n"
    
    correct_answer = row_tent_counts[row_to_ask]

    # 分析部分：列出每个帐篷的坐标
    tents_in_row = row_tent_positions[row_to_ask]
    tents_coordinates = ', '.join([f"({tx}, {ty})" for tx, ty in tents_in_row])
    if correct_answer > 1:
        analysis = f"**Step-by-step reasoning:**\n"\
                   f"1. Count the number of tents in row {row_to_ask}. There are {correct_answer} tents placed at the following coordinates: {tents_coordinates}.\n"\
                   f"2. The correct answer is {correct_answer}."
    elif correct_answer == 1:
        analysis = f"**Step-by-step reasoning:**\n"\
                   f"1. Count the number of tents in row {row_to_ask}. There is 1 tent placed at the following coordinate: {tents_coordinates}.\n"\
                   f"2. The correct answer is 1."
    else:
        analysis = f"**Step-by-step reasoning:**\n"\
                   f"1. Count the number of tents in row {row_to_ask}. There are no tents placed in this row yet.\n"\
                   f"2. The correct answer is 0."

    # 填空题的JSON数据格式
    question_data = {
        "data_id": f"tents-fill-{puzzle_number:05d}-tents-in-row",
        "qa_type": "StateInfo",  # 问题类型
        "question_id": 0,
        "question_description": "how many tents are there in a randomly selected row currently?",
        "image": f"images/{puzzle_number:05d}.png",
        "state": f"states/{puzzle_number:05d}.json",
        "plot_level": generate_plot_level(len(grid[0]), len(grid)),  # 根据网格大小可定义难度
        "qa_level": "Easy",  # 难度可以扩展
        "question": question,
        "answer": str(correct_answer),
        "analysis": analysis
    }

    # 保存填空题到文件
    path = 'tents_dataset/fill_dataset.json'
    save_data(question_data, path)


# 某一列缺少多少帐篷
def gen_num_missing_tents_in_column_fill(grid, tent_positions, col_tent_counts, puzzle_number):
    col_tent_positions = [[] for _ in range(len(grid[0]))]  # 存储每列中帐篷的位置
    
    # 统计每列已经放置的帐篷数量及位置
    for tx, ty in tent_positions:
        col_tent_positions[ty].append((tx, ty))
    
    # 随机选择一列提问
    col_to_ask = random.randint(0, len(grid[0]) - 1)
    
    # 计算缺少的帐篷数量
    missing_tents = col_tent_counts[col_to_ask] - len(col_tent_positions[col_to_ask])
    
    # 生成问题文本
    question = tents_description + \
               f"Given the current state, how many tents are still missing in column {col_to_ask}?\n"
    
    # 分析部分：列出已放置的帐篷位置
    tents_in_col = col_tent_positions[col_to_ask]
    tents_coordinates = ', '.join([f"({tx}, {ty})" for tx, ty in tents_in_col])

    if len(col_tent_positions[col_to_ask]) > 1:
        analysis =  f"**Step-by-step reasoning:**\n"\
                    f"1. According to the blue number above column {col_to_ask}, the total number of tents in column {col_to_ask} should be {col_tent_counts[col_to_ask]}.\n"\
                    f"2. Count the number of tents already placed in column {col_to_ask}, there are {len(col_tent_positions[col_to_ask])} tents placed at the following coordinates: {tents_coordinates}.\n"\
                    f"3. The correct answer is {col_tent_counts[col_to_ask]} - {len(col_tent_positions[col_to_ask])} = {missing_tents}."    
    elif len(col_tent_positions[col_to_ask]) == 1:
        analysis =  f"**Step-by-step reasoning:**\n"\
                    f"1. According to the blue number above column {col_to_ask}, the total number of tents in column {col_to_ask} should be {col_tent_counts[col_to_ask]}.\n"\
                    f"2. Count the number of tents already placed in column {col_to_ask}, there is 1 tent placed at the following coordinate: {tents_coordinates}.\n"\
                    f"3. The correct answer is {col_tent_counts[col_to_ask]} - 1 = {missing_tents}."    
    else:
        analysis =  f"**Step-by-step reasoning:**\n"\
                    f"1. According to the blue number above column {col_to_ask}, the total number of tents in column {col_to_ask} should be {col_tent_counts[col_to_ask]}.\n"\
                    f"2. Count the number of tents already placed in column {col_to_ask}, there are no tents placed in column {col_to_ask}.\n"\
                    f"3. The correct answer is {col_tent_counts[col_to_ask]} - 0 = {missing_tents}."    

    # 填空题的JSON数据格式
    question_data = {
        "data_id": f"tents-fill-{puzzle_number:05d}-missing-tents-in-column",
        "qa_type": "ActionOutcome",  # 问题类型
        "question_id": 3,
        "question_description": "how many tents are still missing in a randomly selected column?",
        "image": f"images/{puzzle_number:05d}.png",
        "state": f"states/{puzzle_number:05d}.json",
        "plot_level": generate_plot_level(len(grid[0]), len(grid)),  # 可以根据网格大小定义难度
        "qa_level": "Easy",  # 难度可以扩展
        "question": question,
        "answer": str(missing_tents),
        "analysis": analysis
        }

    # 保存填空题到文件
    path = 'tents_dataset/fill_dataset.json'
    save_data(question_data, path)

# 整个网格缺少多少帐篷
def gen_num_missing_tents_in_grid_fill(grid, tent_positions, col_tent_counts, puzzle_number):
    total_tents_needed = sum(col_tent_counts)  # 网格中应放置的总帐篷数量
    string_col_tent_counts = ' + '.join([str(count) for count in col_tent_counts])
    
    # 统计当前网格中已放置的帐篷数量
    total_tents_placed = len(tent_positions)
    
    # 计算缺少的帐篷数量
    missing_tents = total_tents_needed - total_tents_placed
    
    # 生成问题文本
    question = tents_description + \
               f"Given the current state, how many tents are still missing in the entire grid?\n"
    
    # 分析部分：列出已放置的帐篷位置
    tents_coordinates = ', '.join([f"({tx}, {ty})" for tx, ty in tent_positions])
    
    # 填空题的JSON数据格式
    question_data = {
        "data_id": f"tents-fill-{puzzle_number:05d}-missing-tents-in-grid",
        "qa_type": "ActionOutcome",  # 问题类型
        "question_id": 4,
        "question_description": "how many tents are still missing in the entire grid?",
        "image": f"images/{puzzle_number:05d}.png",
        "state": f"states/{puzzle_number:05d}.json",
        "plot_level": generate_plot_level(len(grid[0]), len(grid)),  # 可以根据网格大小定义难度
        "qa_level": "Medium",  # 难度可以扩展
        "question": question,
        "answer": str(missing_tents),
        "analysis": f"**Step-by-step reasoning:**\n"
                    f"1. Calculate the total number of tents needed in the grid by summing the values in the blue numbers above each column. The sum is: {string_col_tent_counts} = {total_tents_needed}.\n"
                    f"2. Count the number of tents already placed in the grid. There are {total_tents_placed} tents placed in the grid at the following coordinates: {tents_coordinates}.\n"
                    f"3. Subtract the number of tents already placed from the total number of tents that should be in the grid. The correct answer is {total_tents_needed} - {total_tents_placed} = {missing_tents}."
    }

    # 保存填空题到文件
    path = 'tents_dataset/fill_dataset.json'
    save_data(question_data, path)

# 所有可能的帐篷位置
def gen_possible_tent_positions_fill(grid, tree_positions, puzzle_number):
    # 用set存储所有可能放置帐篷的位置，避免重复
    possible_tent_positions = set()

    analysis= f"**Step-by-step reasoning:**\n"\
              f"1. Find all the trees in the grid: {', '.join([f'({x}, {y})' for (x, y) in tree_positions])}.\n"\
              f"2. For each tree, check its adjacent horizontal and vertical positions (up, down, left, right). "\
              f"List the positions that are within the grid bounds and are not already occupied by trees:\n"\
                

    # 网格的行数和列数
    rows = len(grid)
    cols = len(grid[0])
    
    # 遍历树的位置
    for (x, y) in tree_positions:
        places = ""
        # 检查上、下、左、右四个方格
        if y + 1 < cols and (x, y + 1) not in tree_positions:
            possible_tent_positions.add((x, y + 1))
            places += f"({x}, {y+1}), "
        if y - 1 >= 0 and (x, y - 1) not in tree_positions:
            possible_tent_positions.add((x, y - 1))
            places += f"({x}, {y-1}), "
        if x - 1 >= 0 and (x - 1, y) not in tree_positions:
            possible_tent_positions.add((x - 1, y))
            places += f"({x-1}, {y}), "
        if x + 1 < rows and (x + 1, y) not in tree_positions:
            possible_tent_positions.add((x + 1, y))
            places += f"({x+1}, {y}), "
        if places:
            places = places[:-2]  # 去掉最后的逗号和空格
            analysis += f"Tree at ({x}, {y}) has the following one or more valid positions around it: {places}.\n"
        else:
            analysis += f"Tree at ({x}, {y}) has no valid positions around it.\n"
    
    # 计算填空题的答案
    answer = len(possible_tent_positions)
    
    # 生成问题文本
    question = tents_description + \
            f"Given the tree positions and considering only the first and the third rule, how many positions in the entire grid are available to place tents (including both positions that are currently occupied by tents and positions that are currently empty)?"

    # 分析部分：列出所有可能放置帐篷的位置
    possible_positions_str = ', '.join([f"({x}, {y})" for (x, y) in sorted(possible_tent_positions)])

    analysis += f"\n3. Aggregate the valid positions where tents can be placed and remove duplicates. The valid positions are: {possible_positions_str}.\n"\
                f"4. The correct answer is the total number of valid positions, which is {answer}."

    # 填空题的JSON数据格式
    question_data = {
        "data_id": f"tents-fill-{puzzle_number:05d}-possible-tent-positions",
        "qa_type": "ActionOutcome",  # 问题类型
        "question_id": 5,
        "question_description": "Given the tree positions and considering only the second rule, how many positions in the entire grid are available to place tents (including those already occupied by tents)?",
        "image": f"images/{puzzle_number:05d}.png",
        "state": f"states/{puzzle_number:05d}.json",
        "plot_level": generate_plot_level(len(grid[0]), len(grid)),  # 可以根据网格大小定义难度
        "qa_level": "Medium",  # 难度可以扩展
        "question": question,
        "answer": str(answer),
        "analysis": analysis
    }
    
    # 保存填空题到文件
    path = 'tents_dataset/fill_dataset.json'
    save_data(question_data, path)

# 生成“新帐篷位置”的填空题
def gen_new_tent_count_fill(grid, tent_positions, tree_positions, col_tent_counts, row_tent_counts, puzzle_number):
    # 分析部分：列出有效位置的类型
    analysis = "**Step-by-step reasoning:**\n"
    analysis += f"We need to check every position in the grid to see if it can hold a new tent without violating the game rules. "\
                f"By evaluating the conditions, we can find out how many positions are suitable for placing a new tent.\n"
    valid_positions = []
    # 遍历整个网格，检查每个位置是否可以放置新帐篷
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            is_valid, reason = is_valid_new_tent_position(x, y, grid, tree_positions, tent_positions, row_tent_counts, col_tent_counts)
            if is_valid:
                valid_positions.append((x, y))
                analysis += f"Position ({x}, {y}) is valid for placing a new tent.\n{reason}"

    analysis += f"Therefore, the answer is {len(valid_positions)} positions.\n"

    # 构建问题
    question = tents_description + \
               f"Given the current state, how many positions in the grid are available to place a new tent without breaking the game rules immediately"\
               f" (it does not have to be a part of a whole solution to the puzzle)?\n"

    # 填空题的答案是有效的位置计数
    answer = len(valid_positions)

    # 填空题的JSON数据格式
    question_data = {
        "data_id": f"tents-fill-{puzzle_number:05d}-new-tent-positions",
        "qa_type": "ActionOutcome",  # 问题类型
        "question_id": 6,
        "question_description": "how many positions in the grid are available to place a new tent without breaking the game rules immediately (it does not have to be a part of a whole solution to the puzzle)?",
        "image": f"images/{puzzle_number:05d}.png",
        "state": f"states/{puzzle_number:05d}.json",
        "plot_level": generate_plot_level(len(grid[0]), len(grid)),  # 可以根据网格大小定义难度
        "qa_level": "Hard",  # 难度可以扩展
        "question": question,
        "answer": str(answer),
        "analysis": analysis
    }

    # 保存填空题到文件
    path = 'tents_dataset/fill_dataset.json'
    save_data(question_data, path)


# 生成“以下x个位置中哪个位置上有树”的单选题
def gen_tree_position_mcq(grid, tent_positions, tree_positions, puzzle_number, num_options = 4):
    # 随机选择x个不同的位置
    options = []
    correct_option = random.choice(list(tree_positions))  # 随机选择一个正确的树的位置
    
    # 确保选项中不重复并且包含正确答案
    options.append(correct_option)
    
    while len(options) < num_options:
        random_position = (random.randint(0, len(grid[0]) - 1), random.randint(0, len(grid) - 1))
        if random_position not in options and random_position not in tree_positions:
            options.append(random_position)
    
    # 随机打乱选项
    random.shuffle(options)

    # 构建问题
    question = tents_description + \
               f"Given the current state, which of the following positions contains a tree?\nOptions:\n"

    # 构建选项字符串
    options_str = "\n".join([f"{i + 1}: ({x}, {y})" for i, (x, y) in enumerate(options)])
    
    # 答案是正确选项的索引（从1开始）
    correct_answer = options.index(correct_option) + 1

    # 分析部分：列出每个选项的类型
    analysis = "**Step-by-step reasoning:**\n"
    for idx, (x, y) in enumerate(options):
        if (x, y) in tree_positions:
            analysis += f"Option {idx+1}: The position {(x, y)} contains a tree.\n"
        elif (x, y) in tent_positions:
            analysis += f"Option {idx+1}: The position {(x, y)} contains a tent.\n"
        else:
            analysis += f"Option {idx+1}: The position {(x, y)} is empty.\n"
    
    # 点明正确答案
    analysis += f"\nSo, the correct answer is option {correct_answer}, which corresponds to the position {correct_option}."

    # 单选题的JSON数据格式
    question_data = {
        "data_id": f"tents-mcq-{puzzle_number:05d}-which-position-has-tree",
        "qa_type": "StateInfo",  # 问题类型
        "question_id": 8,
        "question_description": "which of the following positions contains a tree?",
        "image": f"images/{puzzle_number:05d}.png",
        "state": f"states/{puzzle_number:05d}.json",
        "plot_level": generate_plot_level(len(grid[0]), len(grid)),  # 可以根据网格大小定义难度
        "qa_level": "Easy",  # 难度也可以扩展
        "question": f"{question}{options_str}",
        "answer": correct_answer,
        "options": [[x, y] for x, y in options],  # 转换为坐标的列表形式
        "analysis": analysis
    }
    
    # 保存单选题到文件
    path = 'tents_dataset/mcq_dataset.json'
    save_data(question_data, path)

# 生成“以下x个位置中哪个位置上可以放置新帐篷”的单选题
def gen_new_tent_position_mcq(grid, tent_positions, tree_positions, col_tent_counts, row_tent_counts, removed_tents, puzzle_number, num_options = 4):
    # 随机选择从removed_tents中一个位置作为正确答案
    correct_option = random.choice(removed_tents)  # 随机选择一个可以放新帐篷的位置
    
    # 初始化选项，确保包含正确答案
    _, correct_reason = is_valid_new_tent_position(correct_option[0], correct_option[1], grid, tree_positions, tent_positions, row_tent_counts, col_tent_counts)
    options = [(correct_option, correct_reason),]
    
    # 随机生成错误选项，确保选项中的位置符合上述条件
    while len(options) < num_options:
        random_position = (random.randint(0, len(grid[0]) - 1), random.randint(0, len(grid) - 1))
        is_valid, random_reason = is_valid_new_tent_position(random_position[0], random_position[1], grid, tree_positions, tent_positions, row_tent_counts, col_tent_counts)
        if ((random_position, random_reason) not in options) and not is_valid:
            options.append((random_position, random_reason))
    
    # 随机打乱选项
    random.shuffle(options)

    # 构建问题
    question = tents_description + \
               f"Given the current state, which of the following positions is allowed to place a new tent without breaking the game rules immediately (it does not have to be a part of a whole solution to the puzzle)?\nOptions:\n"

    # 构建选项字符串
    options_str = "\n".join([f"{i + 1}: ({x}, {y})" for i, ((x, y), r) in enumerate(options)])

    # 答案是正确选项的索引（从1开始）
    correct_answer = options.index((correct_option,correct_reason)) + 1

    # 分析部分：列出每个选项的类型
    analysis = "**Step-by-step reasoning:**\n"
    for idx, ((x, y), r) in enumerate(options):
        if (x, y) == correct_option:
            analysis += f"Option {idx+1}: The position {(x, y)} is available to place a new tent.\n{r}"
        else:
            analysis += f"Option {idx+1}: The position {(x, y)} does not meet the conditions for placing a new tent.{r}\n"
    
    # 点明正确答案
    analysis += f"\nSo, the correct answer is option {correct_answer}, which corresponds to the position {correct_option}."

    # 单选题的JSON数据格式
    question_data = {
        "data_id": f"tents-new-tent-mcq-{puzzle_number:05d}-which-position-is-valid",
        "qa_type": "ActionOutcome",  # 问题类型
        "question_id": 9,
        "question_description": "which of the following positions is available to place a new tent?",
        "image": f"images/{puzzle_number:05d}.png",
        "state": f"states/{puzzle_number:05d}.json",
        "plot_level": generate_plot_level(len(grid[0]), len(grid)),  # 可以根据网格大小定义难度
        "qa_level": "Medium",  # 难度可以扩展
        "question": f"{question}{options_str}",
        "answer": correct_answer,
        "options": [[x, y] for (x, y), r in options],  # 转换为坐标的列表形式
        "analysis": analysis
    }

    # 保存单选题到文件
    path = 'tents_dataset/mcq_dataset.json' 
    save_data(question_data, path)

# 配置谜面大小、树的数量和生成谜面的数量
grid_size_list = [(7, 7), (10, 10), (13, 13)]  # 网格大小
num_trees_list = [5, 10, 17]      # 树和帐篷的数量
num_puzzles = 24   # 生成谜面的数量
max_removed_tents_list = [2, 4, 7]  # 每次去掉的帐篷数量

# 自动分配谜面编号并生成谜面
def generate_and_save_puzzle(grid_size, num_trees, max_removed_tents):
    puzzle_number = len(os.listdir('tents_dataset/states')) + 1
    grid, tree_positions, tent_positions, row_tent_counts, col_tent_counts = generate_tents_puzzle(grid_size, num_trees)

    # 移除一些帐篷
    removed_tents = remove_random_tents(grid, tent_positions, max_removed_tents)
    
    save_puzzle_to_json(grid_size, tree_positions, tent_positions, removed_tents, puzzle_number)
    save_visualization(grid, row_tent_counts, col_tent_counts, puzzle_number)
    # 填空题 
    gen_num_tents_in_row_fill(grid, tent_positions, puzzle_number)
    gen_num_missing_tents_in_column_fill(grid, tent_positions, col_tent_counts, puzzle_number)
    gen_num_missing_tents_in_grid_fill(grid, tent_positions, col_tent_counts, puzzle_number)
    gen_possible_tent_positions_fill(grid, tree_positions, puzzle_number)
    gen_new_tent_count_fill(grid, tent_positions, tree_positions, col_tent_counts, row_tent_counts, puzzle_number)

    # 单选题 
    num_options = 8 # 选项数量
    gen_tree_position_mcq(grid, tent_positions, tree_positions, puzzle_number, num_options)
    gen_new_tent_position_mcq(grid, tent_positions, tree_positions, col_tent_counts, row_tent_counts, removed_tents, puzzle_number, num_options)

    print(f'Generated puzzle #{puzzle_number:05d}')


# 生成并保存谜面
for i in range(3):
    for j in range(num_puzzles):
        generate_and_save_puzzle(grid_size_list[i], num_trees_list[i], max_removed_tents_list[i])

# 合并数据
with open('tents_dataset/fill_dataset.json', 'r') as json_file:
    fill_data = json.load(json_file)
with open('tents_dataset/mcq_dataset.json', 'r') as json_file:
    mcq_data = json.load(json_file)

data = fill_data + mcq_data
with open('tents_dataset/data.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)
