import random
from itertools import permutations
import pygame
import os
from collections import deque
import datetime
import json


class StarBattle:
    def __init__(self, n, stars, grid_size):
        """
        Initialize a Star Battle puzzle.

        :param n: Number of regions.
        :param stars: Number of stars per row/column/region.
        :param grid_size: Size of the grid (grid_size x grid_size).
        """
        self.n = n
        self.stars = stars
        self.grid_size = grid_size
        self.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        self.regions=[]
    
    # 为网格分区
    def generate_regions(self):
        """
        Generate exactly n connected regions for the grid with better randomization.
        Returns a list of n regions, where each region is a list of (row, col) coordinates.
        """
        while True:  # Keep trying until we get exactly n regions
            # Reset for each attempt
            cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
            random.shuffle(cells)  # Shuffle cells for randomization
            regions = []
            unassigned_cells = set(cells)
            
            def get_neighbors(cell):    # 获取cell的neighbor
                r, c = cell
                neighbors = []
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                        neighbors.append((nr, nc))
                return neighbors

            # Try to create exactly n regions
            while len(regions) < self.n and unassigned_cells:
                # Start a new region
                start_cell = random.choice(list(unassigned_cells))  # 从未分配的cell中任选一个作为当前region的第一个cell
                current_region = []
                queue = deque([start_cell]) # 队列
                unassigned_cells.remove(start_cell)
                current_region.append(start_cell)

                # Grow the region
                target_size = max(len(cells) // self.n, 1)  # Minimum target size for each region 尽可能的均分
                while queue and len(current_region) < target_size:
                    cell = queue.popleft()  # 从队列中退出一个元素
                    neighbors = get_neighbors(cell) # 找出该元素的邻居
                    random.shuffle(neighbors)  # 打乱邻居的顺序,使得邻居的选择是随机的
                    
                    for neighbor in neighbors:
                        if neighbor in unassigned_cells:
                            unassigned_cells.remove(neighbor)
                            current_region.append(neighbor)
                            queue.append(neighbor)
                if current_region:  # 只有current_region不为空时才会加入regions中
                    regions.append(current_region)

            # If we have exactly n regions, distribute any remaining cells
            if len(regions) == self.n:
                # Distribute any remaining cells to adjacent regions
                while unassigned_cells:
                    cell = unassigned_cells.pop()
                    neighbors = get_neighbors(cell)
                    # Find regions adjacent to this cell
                    adjacent_regions = []
                    for i, region in enumerate(regions):
                        for neighbor in neighbors:
                            if neighbor in region:
                                adjacent_regions.append(i)
                                break
                    
                    if adjacent_regions:
                        # Add to a random adjacent region
                        region_idx = random.choice(adjacent_regions)
                        regions[region_idx].append(cell)
                    else:
                        # If no adjacent regions, add to the smallest region
                        unassigned_cells.add(cell)
                        # print("No adjacent_region for cell",cell)
                        # print(self.grid)
                        # print(regions)
                        # smallest_region = min(range(len(regions)), key=lambda i: len(regions[i]))
                        # regions[smallest_region].append(cell)
                
                return regions
            else:
                # If we didn't get exactly n regions, try again
                continue
    
    # 打印网格以及region
    def display(self):
        """Display the grid and regions."""
        print("Grid:")
        for row in self.grid:
            print(" ".join(str(x) for x in row))

        print("\nRegions:")
        for i, region in enumerate(self.regions):
            print(f"Region {i + 1}: {region}")
    
    # 判断当前cell放置一个star是否是合规的
    def is_valid(self, row, col):
        """
        Check if placing a star at (row, col) is valid.

        :param row: Row index.
        :param col: Column index.
        :return: True if valid, False otherwise.
        """
        # Check row and column constraints 每行、每列只有一个
        if sum(self.grid[row]) >= self.stars or sum(self.grid[r][col] for r in range(self.grid_size)) >= self.stars:
            return False

        # Check adjacent cells 不能有cell相邻
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size and self.grid[nr][nc] == 1:
                    return False

        # Check region constraints  一个区域内只能有一个
        for region in self.regions:
            if (row, col) in region:
                stars_in_region = sum(self.grid[r][c] for r, c in region)
                if stars_in_region >= self.stars:
                    return False

        return True

    def solve(self, cell=0):
        """
        Solve the Star Battle puzzle using backtracking.

        :param cell: Current cell index to consider.
        :return: True if solved, False otherwise.
        """
        if cell == self.grid_size * self.grid_size:
            for region in self.regions:
                stars_in_region = sum(self.grid[r][c] for r, c in region)
                if stars_in_region != self.stars:
                    return False
            return True

        row, col = divmod(cell, self.grid_size) # cell -> (row,col)
        if self.grid[row][col] == 0:
            if self.is_valid(row, col):
                self.grid[row][col] = 1
                if self.solve(cell + 1):
                    return True
                self.grid[row][col] = 0

        return self.solve(cell + 1)

    # 用pygame把网格画出来
    def draw(self, screen, cell_size):
        """Draw the Star Battle grid and regions using Pygame."""
        # colors for drawing
        REGION_COLORS = [
            (255, 182, 193),  # Light pink
            (176, 224, 230),  # Powder blue
            (144, 238, 144),  # Light green
            (255, 218, 185),  # Peach
            (255, 0, 0),      # Red
            (255, 255, 0),    # Yellow
            (0, 255, 255),    # Cyan
            (255, 165, 0),    # Orange
            (128, 0, 128),    # Purple
        ]

        # Draw grid lines  画出网格线
        for i in range(self.grid_size + 1):
            pygame.draw.line(screen, (0, 0, 0), (0, i * cell_size), (self.grid_size * cell_size, i * cell_size), 2)
            pygame.draw.line(screen, (0, 0, 0), (i * cell_size, 0), (i * cell_size, self.grid_size * cell_size), 2)

        # Highlight regions
        # colors = [(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)) for _ in range(self.n)]
        for region_idx, region in enumerate(self.regions):
            color = REGION_COLORS[region_idx%self.n]
            for (row, col) in region:
                rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, color, rect, 0)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        # Draw stars
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] == 1:
                    center = (col * cell_size + cell_size // 2, row * cell_size + cell_size // 2)
                    pygame.draw.circle(screen, (0, 0, 0), center, cell_size // 4)

    # 保存图片
    def save_image(self, screen, filename):
        """Save the current Pygame screen as an image file."""
        pygame.image.save(screen, filename)

plot_difficulty_map = {
    5: "Easy",
    6: "Medium",
    8: "Hard"
}

qa_difficulty_map = {
    "last_star":"Hard",
    "State of the current grid":"Easy",
    "cells_of_region":"Easy",
    "star_of_region":"Easy",
    "valid_cells":"Medium",
}

def generate_last_star_puzzle(num_puzzles,n,stars,grid_size,base_path):
    """
    num_puzzles: 要生成的问题的个数
    n:区域数量
    stars:每行、每列、每区的star数限制
    grid_size:grid的大小
    base_path:保存路径
    """
    # Initialize Pygame
    pygame.init()
    cell_size = 50
    screen_size = grid_size * cell_size
    screen = pygame.display.set_mode((screen_size, screen_size))
    pygame.display.set_caption("Star Battle Puzzle")

    puzzles_generated = 0
    attempt = 0
    max_attempts = num_puzzles * 10  # Maximum attempts to avoid infinite loops

    data=[]
    # 开始产生answer puzzle 类型的问题
    while puzzles_generated < num_puzzles and attempt < max_attempts:
        attempt+=1
        puzzle = StarBattle(n, stars, grid_size)
        puzzle.regions=puzzle.generate_regions()    # 产生一个puzzle
        # puzzle.display()    # 打印出网格结构
        
        # 如果没有合法解,就跳过
        if not puzzle.solve():
            continue  # Skip if puzzle has no solution

        # 保存最终的solution
        solution=[]
        for i in range(puzzle.grid_size):
            for j in range(puzzle.grid_size):
                if puzzle.grid[i][j]==1:
                    solution.append((i,j))
        
        if len(solution)>puzzle.n:
            print("solve的逻辑出错了")
        
        # 构造谜面:从最终解中删去一个star,构成current_state
        number=puzzle.n-1
        answer=None
        preplaced_stars=[]
        selected_regions = random.sample(range(puzzle.n), number)  # 随机选取 puzzle.n-1 个区域
        # 把未选中的区域中的那个star删去
        for i in range(puzzle.grid_size):
            for j in range(puzzle.grid_size):
                if puzzle.grid[i][j]==1:    # 对每个star
                    region_of_cell=-1
                    for k in range(puzzle.n):
                        if (i,j) in puzzle.regions[k]:  # 找到所属区域
                            region_of_cell=k
                            break
                    if region_of_cell is not None and  region_of_cell not in selected_regions:  # 不被选中,且region存在
                        puzzle.grid[i][j]=0
                        answer=(i,j)
                    else:
                        preplaced_stars.append((i,j))
                        
        color_description=f''''''
        for i in range(puzzle.grid_size):
            color_description+=f"Region with index {i} has the color of {region_color_map[i]}\n"
        # 有合法解就求解
        puzzle_data={
            "data_id": f"star-battle-last_star-{plot_difficulty_map[puzzle.grid_size]}-{puzzles_generated+1:05d}",
            "qa_type":"TransitionPath",
            "question_id":1,
            "question_description":f"We have a {puzzle.grid_size}x{puzzle.grid_size} grid. The grid is divided into {puzzle.n} regions.\nThe current grid already has {len(preplaced_stars)} stars placed.\nYour task is to find the location of the final star to complete the puzzle.",
            "image": f"images/board_last_star_{plot_difficulty_map[n]}_{puzzles_generated+1:05d}.png",
            "state": f"states/board_last_star_{plot_difficulty_map[n]}_{puzzles_generated+1:05d}.json",
            "plot_level": plot_difficulty_map[n],  # You can adjust difficulty based on your criteria
            "qa_level":qa_difficulty_map["last_star"],
            "question": f"""
We have a {puzzle.grid_size}x{puzzle.grid_size} grid. The grid is divided into {puzzle.n} regions.
Cells with the same color belong to the same region.
{color_description}
The cells in the grid are labeled with row and column numbers starting from 0. The top-left corner of the grid is (0, 0).
(x,y) means a cell at row x and column y. 
The current grid already has {len(preplaced_stars)} stars placed.
The preplaced stars are as follows:
{preplaced_stars}
Your task is to find the location of the final star to complete the puzzle.
Remember the rules:
- Each row must contain exactly {stars} star(s).
- Each column must contain exactly {stars} star(s).
- Each region must contain exactly {stars} star(s).
- Stars cannot be adjacent to each other, including diagonally.
- The cells in the grid are labeled with row and column numbers starting from 0. The top-left corner of the grid is (0, 0).
Now the puzzle has only one star left to be placed.The left star should be placed in which cell?
""",
            "answer": str(answer),
            "analysis": f""""""
        }
        analysis=f'''**Step-by-step reasoning to solve the puzzle:**
1. **Preplaced stars and their positions:**
   - The following stars are already placed:
     {', '.join([f"Row {x}, Column {y}" for x, y in preplaced_stars])}.
   - These positions fulfill the requirement of placing one star per row, column, and region.

2. **Identify rows and columns with and without stars:**
   - **Rows with stars:** {', '.join([f"Row {i}" for i in range(puzzle.n) if any(puzzle.grid[i][j] == 1 for j in range(puzzle.n))])}.
   - **Rows without stars:** {', '.join([f"Row {i}" for i in range(puzzle.n) if not any(puzzle.grid[i][j] == 1 for j in range(puzzle.n))])}.
   
   - **Columns with stars:** {', '.join([f"Column {j}" for j in range(puzzle.n) if any(puzzle.grid[i][j] == 1 for i in range(puzzle.n))])}.
   - **Columns without stars:** {', '.join([f"Column {j}" for j in range(puzzle.n) if not any(puzzle.grid[i][j] == 1 for i in range(puzzle.n))])}.

3. **Determine remaining valid cell:**
   - The final star must be placed in a row and column that are both missing stars.
   - Based on the information above, the row without a star is {', '.join([f"Row {i}" for i in range(puzzle.n) if not any(puzzle.grid[i][j] == 1 for j in range(puzzle.n))])} and the column without a star is {', '.join([f"Column {j}" for j in range(puzzle.n) if not any(puzzle.grid[i][j] == 1 for i in range(puzzle.n))])}.
   - The only available intersection is cell {answer}, which satisfies the row and column constraints.

4. **Region check:**
   - The preplaced stars occupy the following regions:{', '.join(map(str, set(region_idx for region_idx, region in enumerate(puzzle.regions) if any((x, y) in region for x, y in preplaced_stars))))}.
   The remaining region that requires a star is: {', '.join([f"Region {region_idx}" for region_idx, region in enumerate(puzzle.regions) if sum(1 for (x, y) in region if puzzle.grid[x][y] == 1) == 0])}.
5. **Final validation:**
   - The cell {answer} belongs to the remaining region without a star.
   - Placing the star here satisfies all row, column, region, and adjacency constraints.

Thus, the final star must be placed at **Row {answer[0]}, Column {answer[1]}**
'''
        puzzle_data["analysis"]=analysis
        # Save puzzle image
        screen.fill((255, 255, 255))
        puzzle.draw(screen, cell_size)
        image_path = os.path.join(base_path, f"images/board_last_star_{plot_difficulty_map[n]}_{puzzles_generated+1:05d}.png")
        pygame.image.save(screen, image_path)

        # Save puzzle state
        state_data = {
            "regions": puzzle.regions,
            "stars":[(i,j) for i in range(puzzle.grid_size) for j in range(puzzle.grid_size) if puzzle.grid[i][j]==1],
            "solution": solution
        }
        state_path = os.path.join(base_path, puzzle_data["state"])
        with open(state_path, 'w') as f:
            json.dump(state_data, f, indent=2)

        # Save puzzle data
        data.append(puzzle_data)
        # data_path = os.path.join(base_path, "last_star_dataset.jsonl")
        # with open(data_path, 'a', encoding='utf-8') as f:
        #     json.dump(puzzle_data, f, indent=2, ensure_ascii=False)
        #     f.write("\n")
        
        # save_answers   
        puzzles_generated += 1
        print(f"Generated puzzle {puzzles_generated}/{num_puzzles}")

    # data_path = os.path.join(base_path, "last_star_dataset.json")
    # with open(data_path, 'a', encoding='utf-8') as f:
    #     json.dump(data, f, indent=2, ensure_ascii=False)
    #     f.write("\n")
    pygame.quit()

    if puzzles_generated < num_puzzles:
        print(f"Warning: Only generated {puzzles_generated} valid puzzles out of {num_puzzles} requested")
    return data
    

region_color_map = {
    0: "light pink",
    1: "powder blue",
    2: "light green",
    3: "peach",
    4: "red",
    5: "yellow",
    6: "cyan",
    7: "orange",
    8: "purple"
}

def generate_state_analysis_puzzle(num_puzzles,n,stars,grid_size,base_path):
    """
    num_puzzles: 要生成的问题的个数
    n:区域数量
    stars:每行、每列、每区的star数限制
    grid_size:grid的大小
    base_path:保存路径
    """
    pygame.init()
    cell_size = 50
    screen_size = grid_size * cell_size
    screen = pygame.display.set_mode((screen_size, screen_size))
    pygame.display.set_caption("Star Battle Puzzle")

    puzzles_generated = 0
    attempt = 0
    max_attempts = num_puzzles * 10  # Maximum attempts to avoid infinite loops
    
    cells_of_region_data=[]
    cells_of_region_data_path=os.path.join(base_path, "cells_of_region_dataset.json")

    star_of_region_data=[]
    star_of_region_data_path=os.path.join(base_path, "star_of_region_dataset.json")

    valid_cell_data=[]
    valid_cell_data_path=os.path.join(base_path, "valid_cells_dataset.json")
    # 开始产生问题
    while puzzles_generated < num_puzzles and attempt < max_attempts:
        attempt+=1
        puzzle = StarBattle(n, stars, grid_size)
        puzzle.regions=puzzle.generate_regions()    # 产生一个puzzle

        # 如果没有合法解,就跳过
        if not puzzle.solve():
            continue  # Skip if puzzle has no solution
        
        # 保存一下解,留待后续使用
        solution = puzzle.grid

        color_description=f''''''
        for i in range(puzzle.grid_size):
            color_description+=f"Region with index {i} has the color of {region_color_map[i]}.\n"

        # 随机删去若干个star
        number = random.randint(2, puzzle.n)  # 随机选择放置的星星数量
        selected_regions = random.sample(range(puzzle.n), number)  # 随机选取 `number` 个区域
        # 把未选中的区域中的star删去
        for i in range(puzzle.grid_size):
            for j in range(puzzle.grid_size):
                if puzzle.grid[i][j]==1:
                    region_of_cell=-1
                    for k in range(puzzle.n):
                        if (i,j) in puzzle.regions[k]:
                            region_of_cell=k
                            break
                    if region_of_cell is not None and  region_of_cell not in selected_regions:
                        puzzle.grid[i][j]=0

        data_id=f"star-battle-cells_of_region-{plot_difficulty_map[n]}-{puzzles_generated+1:05d}"
        image=f"images/board_state_analysis_{plot_difficulty_map[n]}_{puzzles_generated+1:03d}.png"
        state=f"states/board_state_analysis_{plot_difficulty_map[n]}_{puzzles_generated+1:03d}.json"
        plot_level=plot_difficulty_map[n]
        question_base=f'''
We have a {puzzle.n}*{puzzle.n} grid.The grid is divided into {n} regions.
Cells with the same color belong to the same region.
{color_description}
In the image,a star is represented by a black dot. If a cell has been placed a star,a black dot will be shown on this cell. 
We should place the star in this Star Battle Puzzle according to the following rules:
Each row must contain exactly {stars} star(s).
Each column must contain {stars} star(s).
Each region must contain exactly {stars} star(s).
Stars cannot be adjacent to each other, including diagonally.
The cells in the grid are labeled with row and column numbers starting from 0. The top-left corner of the grid is (0, 0).
(x,y) means a cell at row x and column y. 
Now we have placed some stars in the grid.
'''
        
        """
        首先是第一类问题:cells of region   随机选取一个region,问:选项中哪一个cell属于该region  ==> 这类问题,可以保证,选项一定有四个
        """
        region_index = random.randint(0, puzzle.n - 1)  # Randomly select a region index
        correct_cells = puzzle.regions[region_index]
        correct_cell = random.choice(correct_cells)  # 随机选取该区域中的一个cell作为正确答案
        options=[]
        while len(options)<7:
            distractor_region = random.randint(0, puzzle.n - 1)  # 随机选一个不同的区域,返回其index
            if distractor_region != region_index:   # 如果该区域不是被选取区域
                distractor_cell = random.choice(puzzle.regions[distractor_region])  # 随机选择该区域的一个cell作为干扰项
                if f"({distractor_cell[0]},{distractor_cell[1]})" not in options:
                    options.append(f"({distractor_cell[0]},{distractor_cell[1]})")
        options.append(f"({correct_cell[0]},{correct_cell[1]})")  # 加入正确答案
        random.shuffle(options)     # 打乱顺序
        ## 正确选项对应的数值
        correct_answer_label=None
        temp=1
        for option in options:
            if option==f"({correct_cell[0]},{correct_cell[1]})":
                correct_answer_label=temp
                break
            temp+=1
        ## 生成选项文本
        option_text=f''''''
        for idx,option in enumerate(options):
            option_text+=(f"{idx+1}."+option+"\n")
        puzzle_data={
            "data_id": data_id,
            "qa_type":"StateInfo",
            "question_id":2,
            "question_description":f"Given current state and an index of a region.You should idectify which cell provided in the options belongs the region.",
            "image": image,
            "state": state,
            "plot_level": plot_level,  # You can adjust difficulty based on your criteria
            "qa_level":qa_difficulty_map["cells_of_region"],
            "question": question_base+f'''\nThe region with index {region_index} is represented by the color {region_color_map[region_index]} in the grid.Given the current state, which cell in the following options belong to region {region_index}?\n'''+f'''Options:\n{option_text}''',
            "answer": correct_answer_label,
            "analysis": f'''The region with index {region_index} is represented by the color {region_color_map[region_index]} in the grid.
In this puzzle, we need to identify which cell in the following options belongs to this region.
The region {region_index} contain the following cells:{puzzle.regions[region_index]}
By inspecting the grid, we can see that the following cell is part of region {region_index}:
Cell ({correct_cell[0]}, {correct_cell[1]})

This is because this cell is located within the colored area corresponding to region {region_index}, which is marked as {region_color_map[region_index]}.

Thus, the correct answer is: {correct_cell}.''',
            "options":options
        }

        # Save puzzle image
        screen.fill((255, 255, 255))
        puzzle.draw(screen, cell_size)
        image_path = os.path.join(base_path, f"images/board_state_analysis_{plot_difficulty_map[n]}_{puzzles_generated+1:03d}.png")
        pygame.image.save(screen, image_path)

        # Save puzzle state
        state_data = {
            "regions": puzzle.regions,  # 保存分区信息
            "stars": [[i, j] for i in range(grid_size) for j in range(grid_size) if puzzle.grid[i][j] == 1],  # 保存星星位置
        }
        state_path=os.path.join(base_path, state)
        with open(state_path, 'w',encoding='utf-8') as f:
            json.dump(state_data,f,indent=2,ensure_ascii=False)
            f.write("\n")
        # Save puzzle data
        # data_path = os.path.join(base_path, "cells_of_region_dataset.jsonl")
        # with open(data_path, 'a', encoding='utf-8') as f:
        #     json.dump(puzzle_data, f, indent=2, ensure_ascii=False)
        #     f.write("\n")
        cells_of_region_data.append(puzzle_data)

        """
        下面是第二类问题:star of region 随机选取一个region,找出该region中star所在的cell.  现在的构造下,选项全部来自于该region,但是该region只有一个cell时,仅有一个选项
        """
        puzzle_data_2={
            "data_id": f"star-battle-star_of_region-{plot_difficulty_map[n]}-{puzzles_generated+1:05d}",
            "qa_type":"StateInfo",
            "question_id":2,
            "question_description":f"Given current state and an index of a region.You should idectify which cell provided in the options belongs the region.",
            "image": image,
            "state": state,
            "plot_level": plot_level,  # You can adjust difficulty based on your criteria
            "qa_level":qa_difficulty_map["cells_of_region"],
            "question": question_base+f'''\nThe region with index {region_index} is represented by the color {region_color_map[region_index]} in the grid.Given the current state, which cell in the following options belong to region {region_index}?\n'''+f'''Options:\n{option_text}''',
            "answer": correct_answer_label,
            "analysis": f'''''',
            "options":options
        }

        region_index_2=random.randint(0, n - 1)   # 随机选取一个region
        # 首先找出正确答案
        correct_cell=None
        for cell in puzzle.regions[region_index_2]:
            row,col=cell
            if puzzle.grid[row][col]==1:
                correct_cell=cell
                break
        
        # 然后生成选项
        region_cells=puzzle.regions[region_index_2]   # 该region的全部元素
        if correct_cell is not None:
            correct_answer=f"({correct_cell[0]},{correct_cell[1]})"
        else:
            correct_answer=f"null"
        options_2=[correct_answer]
        while len(options_2)<min(8,len(region_cells)):
            random_cell = random.choice(region_cells)
            if f"({random_cell[0]},{random_cell[1]})" not in options_2:
                options_2.append(f"({random_cell[0]},{random_cell[1]})")
        # 如果该region的cell不足4个，选择其他region的cell作为选项
        if len(region_cells) < 8:
            remaining_cells = []
            for i, region in enumerate(puzzle.regions):
                if i != region_index:  # 排除已选择的region
                    remaining_cells.extend(region)
    
            # 添加其他region的cell直到选项数量达到8个
            while len(options_2) < 8:
                random_cell = random.choice(remaining_cells)
                if f"({random_cell[0]},{random_cell[1]})" not in options_2:
                    options_2.append(f"({random_cell[0]},{random_cell[1]})")

        random.shuffle(options_2) # 打乱顺序
        # 正确答案的选项值
        temp=1
        for option in options_2:
            if option== correct_answer:
                correct_answer_label=temp
                break
            temp+=1
        # 选项文本
        option_text_2=f''''''
        for idx,option in enumerate(options_2):
            option_text_2+=(f"{idx+1}."+option+"\n")
        
        # 构造puzzle_data
        puzzle_data_2["qa_level"]=f"{qa_difficulty_map['star_of_region']}"
        puzzle_data_2["qa_type"]=f"StateInfo"
        puzzle_data_2["question_id"]=3
        puzzle_data_2["question_description"]=f"Given current state and a region,Your task is to indentify which cell provided by options belongs to this region and has been placed a star. "
        puzzle_data_2["question"]=question_base+f'''\nIn the current puzzle state, region {region_index_2} is associated with color {region_color_map[region_index_2]}. 
Please identify which of the following cells in this region that contains a star?\nNote that:If no stars have been placed in the target region,please choose the option "null"\n'''+f'''Options:\n{option_text_2}'''
        puzzle_data_2["answer"]=correct_answer_label
        
        ## 构造 analysis
        detailed_analysis = f"In this task, we need to find all the stars in the region with index {region_index_2}.\n"
        detailed_analysis += f"The region with index {region_index_2} corresponds to the color {region_color_map[region_index]}.\n"
        detailed_analysis += f"This region contains the following cells: {region_cells}.\n"
        detailed_analysis += f'''Note that a star is represented by a black,now scan the cells of the region {region_index_2} on the image.The cell with a black dot is: {correct_answer}. '''
        detailed_analysis += "\nAnalysis of each option:\n"

        for option in options_2:
            # 解析每个选项的坐标
            if option == "null":    # 如果是null则跳过
                continue
            row, col = map(int, option.strip('()').split(','))
            
            # 查找该单元格所在的region
            cell_region_index = None
            for idx, region in enumerate(puzzle.regions):
                if (row, col) in region:
                    cell_region_index = idx
                    break
            
            # 判断该单元格是否包含星星
            contains_star = "contain a star" if puzzle.grid[row][col] == 1 else "does not contain a star"
            
            # 分析该选项
            detailed_analysis += f"Cell {option} belongs to region {cell_region_index} and {contains_star}.\n"

        detailed_analysis += f"\nTherefore,The stars found in region {region_index_2} are located at the following positions: {correct_cell if correct_cell is not None else 'No stars found'}.We should choose option {correct_answer_label}"
                
        puzzle_data_2["analysis"]=detailed_analysis
        puzzle_data_2["options"]=options_2

        # 保存生成的data
        # data_path = os.path.join(base_path, "star_of_region_dataset.jsonl")
        # with open(data_path, 'a', encoding='utf-8') as f:
        #     json.dump(puzzle_data, f, indent=2, ensure_ascii=False)
        #     f.write("\n")
        star_of_region_data.append(puzzle_data_2)
        
        """
        下面是第三类问题:根据当前的state,找出一个可以放置star的位置 ==> 当下的构造,从valid_cells中选一个,invalid_cells中选3个
        """

        puzzle_data_3={
            "data_id": f"star-battle-valid_cell-{plot_difficulty_map[n]}-{puzzles_generated+1:05d}",
            "qa_type":"StateInfo",
            "question_id":2,
            "question_description":f"Given current state and an index of a region.You should idectify which cell provided in the options belongs the region.",
            "image": image,
            "state": state,
            "plot_level": plot_level,  # You can adjust difficulty based on your criteria
            "qa_level":qa_difficulty_map["cells_of_region"],
            "question": "",
            "answer": correct_answer_label,
            "analysis": f'''''',
            "options":options
        }

        ## 先分类 valid_cells & invalid_cells
        valid_cells=[]
        invalid_cells=[]
        for i in range(puzzle.grid_size):
            for j in range(puzzle.grid_size):
                if puzzle.grid[i][j]==0 and  puzzle.is_valid(i,j):  # 空，且有效
                    valid_cells.append((i,j))
                elif puzzle.grid[i][j]==0 and not puzzle.is_valid(i,j):   # 空且无效
                    invalid_cells.append((i,j))
        ## 选出一个正确选项与若干干扰选项     
        if valid_cells: # 有valid_cell则随机选一个
            correct_cell = random.choice(valid_cells)
            correct_answer=f"({correct_cell[0]},{correct_cell[1]})"
        else:   # 无valid_cell则标记null
            correct_answer="null"
        options_3=[correct_answer]
        ## 生成干扰选项
        distractors_size = min(7, len(invalid_cells))  # 如果 invalid_cells 数量小于 3，选择所有元素
        distractors = random.sample(invalid_cells, distractors_size)  # 随机选取干扰
        for distractor in distractors:
            options_3.append(f"({distractor[0]},{distractor[1]})")
        random.shuffle(options_3)
        choices=distractors+[correct_cell]
        # 找出正确选项的label
        temp=1
        for option in options_3:
            if option == correct_answer:
                correct_answer_label=temp
                break
            temp+=1
        
        # Analyze each empty cell
        analysis_details = []
        for i, j in choices:
            # Check if the current cell is empty and valid
            if (i,j) in valid_cells:
                cell_analysis = f"Cell ({i}, {j}) can hold a star because:\n"
            else:
                cell_analysis = f"Cell ({i}, {j}) can not hold a star because:\n"
            
            # Check adjacency condition
            adjacent_to_star = False
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < puzzle.grid_size and 0 <= nj < puzzle.grid_size:
                        if puzzle.grid[ni][nj] == 1:  # Adjacent to a star
                            adjacent_to_star = True
                            break
                if adjacent_to_star:
                    break
            
            if adjacent_to_star:
                cell_analysis += " It is adjacent to a star, so it cannot hold a star."
            else:
                cell_analysis += " It is not adjacent to any star."
            
            # Check if the region contains any stars
            region_index = None
            for k, region in enumerate(puzzle.regions):
                if (i, j) in region:
                    region_index = k
                    break
            is_region_placed=False
            stars_in_region = [puzzle.grid[ri][rj] == 1 for ri, rj in puzzle.regions[region_index]]
            if any(stars_in_region):  # If there's any star in the region
                is_region_placed=True
                if not adjacent_to_star:    # 没有相邻,那么是因为region里已经防止star
                    cell_analysis += f" However, this cell is in region {region_index}, which already contains one star, so it cannot hold a star."
                else:
                    cell_analysis += f" Besides, this cell is in region {region_index}, which already contains one star, so it cannot hold a star."
            else:
                if not adjacent_to_star:    # 不相邻，且无star
                    cell_analysis += f" This cell is in region {region_index}, which contains no stars."

            # 下面判断行、列
            is_i_placed=False
            is_j_placed=False
            for k in range(grid_size):
                if puzzle.grid[i][k] == 1:
                    is_i_placed=True
                    break
            for k in range(grid_size):
                if puzzle.grid[k][j] == 1:
                    is_j_placed=True
                    break
            if is_i_placed is False and is_j_placed is False:# 行列规则满足了
                if adjacent_to_star is False and is_region_placed is False: # 正确答案
                    cell_analysis +=f"Both row {i} and column {j} now has no stars."
            elif is_i_placed is True:   # 行列规则不满足
                if not adjacent_to_star and not is_region_placed:   # 分区、相邻规则满足时，行列规则是错误的主要原因
                    cell_analysis +=f"However,Row {i} has already been placed a star.Therefore,it cannot hold a star."
            elif is_j_placed is True:
                if not adjacent_to_star and not is_region_placed:   # 分区、相邻规则满足时，行列规则是错误的主要原因
                    cell_analysis +=f"However,Column {j} has already been placed a star.Therefore,it cannot hold a star."
            analysis_details.append(cell_analysis)

        # 生成选项文本
        option_text_3=f''''''
        for idx,option in enumerate(options_3):
            option_text_3+=(f"{idx+1}."+option+"\n")
        # 构造data
        puzzle_data_3["qa_level"]=qa_difficulty_map["valid_cells"]
        puzzle_data_3["qa_type"]="StateInfo"
        puzzle_data_3["question_id"]=4
        puzzle_data_3["question_description"]=f"Based on the current puzzle state, your task is to identify which of the following cells provided by the options can a star be placed in?"
        puzzle_data_3["answer"]=correct_answer_label
        puzzle_data_3["question"]=question_base + "\nBased on the current puzzle state, which of the following cells can a star be placed in?\n"+f"Options:\n{option_text_3}\n"
        puzzle_data_3["analysis"]="\n".join(analysis_details)
        puzzle_data_3["options"] = options_3

        # 保存生成的data
        # data_path = os.path.join(base_path, "valid_cells_dataset.jsonl")
        # with open(data_path, 'a', encoding='utf-8') as f:
        #     json.dump(puzzle_data, f, indent=2, ensure_ascii=False)
        #     f.write("\n")
        valid_cell_data.append(puzzle_data_3)

        puzzles_generated += 1
        print(f"Generated state_analysis puzzle {plot_difficulty_map[puzzle.grid_size]} {puzzles_generated}/{num_puzzles}")

    pygame.quit()
    
    # with open(cells_of_region_data_path,"w",encoding="utf-8") as f:
    #     json.dump(cells_of_region_data,f,indent=2, ensure_ascii=False)
    
    # with open(star_of_region_data_path,"w",encoding="utf-8") as f:
    #     json.dump(star_of_region_data,f,indent=2, ensure_ascii=False)
    
    # with open(valid_cell_data_path,"w",encoding="utf-8") as f:
    #     json.dump(valid_cell_data,f,indent=2, ensure_ascii=False)
    
    if puzzles_generated < num_puzzles:
        print(f"Warning: Only generated {puzzles_generated} valid puzzles out of {num_puzzles} requested")
    return cells_of_region_data,star_of_region_data,valid_cell_data

def generate_examples():
    # 创建目录
    os.makedirs("star-battle_dataset_example",exist_ok=True)
    os.makedirs(os.path.join("star-battle_dataset_example", "images"), exist_ok=True)
    os.makedirs(os.path.join("star-battle_dataset_example", "states"), exist_ok=True)

    data1=generate_last_star_puzzle(num_puzzles=1,n=5,stars=1,grid_size=5,base_path="./star-battle_dataset_example")
    data2=generate_last_star_puzzle(num_puzzles=1,n=6,stars=1,grid_size=6,base_path="./star-battle_dataset_example")
    data3=generate_last_star_puzzle(num_puzzles=1,n=8,stars=1,grid_size=8,base_path="./star-battle_dataset_example")
    last_star_data=data1+data2+data3
    last_star_data_path="./star-battle_dataset_example/last_star_dataset.json"
    with open(last_star_data_path,"w",encoding="utf-8") as f:
        json.dump(last_star_data, f, indent=2, ensure_ascii=False)

    data1_easy,data2_easy,data3_easy=generate_state_analysis_puzzle(num_puzzles=1,n=5,stars=1,base_path="./star-battle_dataset_example",grid_size=5)
    data1_medium,data2_medium,data3_medium=generate_state_analysis_puzzle(num_puzzles=1,n=6,stars=1,base_path="./star-battle_dataset_example",grid_size=6)
    data1_hard,data2_hard,data3_hard=generate_state_analysis_puzzle(num_puzzles=1,n=8,stars=1,base_path="./star-battle_dataset_example",grid_size=8)

    base_path="./star-battle_dataset_example"
    cells_of_region_data=data1_easy+data1_hard+data1_medium
    cells_of_region_data_path=os.path.join(base_path, "cells_of_region_dataset.json")

    star_of_region_data=data2_easy+data2_medium+data2_hard
    star_of_region_data_path=os.path.join(base_path, "star_of_region_dataset.json")

    valid_cell_data=data3_easy+data3_medium+data3_hard
    valid_cell_data_path=os.path.join(base_path, "valid_cells_dataset.json")

    with open(cells_of_region_data_path,"w",encoding="utf-8") as f:
        json.dump(cells_of_region_data,f,indent=2, ensure_ascii=False)
    
    with open(star_of_region_data_path,"w",encoding="utf-8") as f:
        json.dump(star_of_region_data,f,indent=2, ensure_ascii=False)
    
    with open(valid_cell_data_path,"w",encoding="utf-8") as f:
        json.dump(valid_cell_data,f,indent=2, ensure_ascii=False)
    
    data_sum=last_star_data+cells_of_region_data+star_of_region_data+valid_cell_data
    with open("./star-battle_dataset_example/data.json","w",encoding="utf-8") as f:
        json.dump(data_sum,f,indent=2,ensure_ascii=False)

def generate_dataset(num_puzzles):
    
    # 创建目录
    os.makedirs("star-battle_dataset",exist_ok=True)
    os.makedirs(os.path.join("star-battle_dataset", "images"), exist_ok=True)
    os.makedirs(os.path.join("star-battle_dataset", "states"), exist_ok=True)

    data1=generate_last_star_puzzle(num_puzzles=num_puzzles,n=5,stars=1,base_path="./star-battle_dataset",grid_size=5)
    data2=generate_last_star_puzzle(num_puzzles=num_puzzles,n=6,stars=1,base_path="./star-battle_dataset",grid_size=6)
    data3=generate_last_star_puzzle(num_puzzles=num_puzzles,n=8,stars=1,base_path="./star-battle_dataset",grid_size=8)
    last_star_data=data1+data2+data3
    last_star_data_path="./star-battle_dataset/last_star_dataset.json"
    with open(last_star_data_path,"w",encoding="utf-8") as f:
        json.dump(last_star_data, f, indent=2, ensure_ascii=False)

    data1_easy,data2_easy,data3_easy=generate_state_analysis_puzzle(num_puzzles=num_puzzles,n=5,stars=1,base_path="./star-battle_dataset",grid_size=5)
    data1_medium,data2_medium,data3_medium=generate_state_analysis_puzzle(num_puzzles=num_puzzles,n=6,stars=1,base_path="./star-battle_dataset",grid_size=6)
    data1_hard,data2_hard,data3_hard=generate_state_analysis_puzzle(num_puzzles=num_puzzles,n=8,stars=1,base_path="./star-battle_dataset",grid_size=8)

    base_path="./star-battle_dataset"
    cells_of_region_data=data1_easy+data1_hard+data1_medium
    cells_of_region_data_path=os.path.join(base_path, "cells_of_region_dataset.json")

    star_of_region_data=data2_easy+data2_medium+data2_hard
    star_of_region_data_path=os.path.join(base_path, "star_of_region_dataset.json")

    valid_cell_data=data3_easy+data3_medium+data3_hard
    valid_cell_data_path=os.path.join(base_path, "valid_cells_dataset.json")

    with open(cells_of_region_data_path,"w",encoding="utf-8") as f:
        json.dump(cells_of_region_data,f,indent=2, ensure_ascii=False)
    
    with open(star_of_region_data_path,"w",encoding="utf-8") as f:
        json.dump(star_of_region_data,f,indent=2, ensure_ascii=False)
    
    with open(valid_cell_data_path,"w",encoding="utf-8") as f:
        json.dump(valid_cell_data,f,indent=2, ensure_ascii=False)

    data_sum=cells_of_region_data+star_of_region_data+valid_cell_data+last_star_data
    with open("./star-battle_dataset/data.json","w",encoding="utf-8") as f:
        json.dump(data_sum,f,indent=2,ensure_ascii=False)
    
if __name__ == "__main__":
    # 三种场景复杂度,4类不同问题,一共是12类,每一类都是num_puzzles个
    num_puzzles= 1    
    
    # generate_examples()
    generate_dataset(num_puzzles=num_puzzles)

    pygame.quit()

