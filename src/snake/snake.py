import random
from collections import deque
import numpy as np
import pygame

class SnakeGame:
    def __init__(self, width=10, height=10, snake_length=4):
        self.width = width
        self.height = height
        self.snake_length = min(snake_length, width * height - 1)
        self.margin=30
        self.reset()

        # Pygame初始化
        pygame.init()
        self.cell_size=420//width
        #self.screen = pygame.display.set_mode((width * self.cell_size, height * self.cell_size))
        self.screen=pygame.Surface((self.width*self.cell_size+2*self.margin,self.height*self.cell_size+2*self.margin))
        pygame.display.set_caption('Snake Pathfinding')
        self.font = pygame.font.Font(None, 36)
        
        # 颜色定义
        self.colors = {
            'background': (255, 255, 255),
            'grid': (200, 200, 200),
            'coords': (0, 0, 0),
            'snake_head': (255, 255, 0),  # 黄色蛇头
            'snake_body': (0, 0, 255),    # 蓝色蛇身
            'food': (255, 0, 0),          # 红色食物
            'text': (0, 0, 0)             # 黑色文字
        }
    
    def reset(self):
        self.board = np.zeros((self.height, self.width))
        self.generate_snake()
        self.generate_food()
    
    def generate_snake(self):
        head_row = random.randint(0, self.height-1)
        head_col = random.randint(0, self.width-1)
        directions = [(-1,0), (0,1), (1,0), (0,-1)]
        
        max_attempts = 100
        for _ in range(max_attempts):
            self.snake = [(head_row, head_col)]
            self.board = np.zeros((self.height, self.width))
            self.board[head_row, head_col] = 3
            
            success = True
            for _ in range(self.snake_length - 1):
                curr_row, curr_col = self.snake[-1]
                valid_directions = directions.copy()
                random.shuffle(valid_directions)
                
                found_valid_pos = False
                for dr, dc in valid_directions:
                    new_row, new_col = curr_row + dr, curr_col + dc
                    
                    if (0 <= new_row < self.height and 
                        0 <= new_col < self.width and 
                        self.board[new_row, new_col] == 0):
                        
                        self.snake.append((new_row, new_col))
                        self.board[new_row, new_col] = 2
                        found_valid_pos = True
                        break
                
                if not found_valid_pos:
                    success = False
                    break
            
            if success:
                return
        
        # 如果生成失败，退化为短蛇
        self.snake_length = 2
        self.snake = [(head_row, head_col)]
        self.board[head_row, head_col] = 3
        
        for dr, dc in directions:
            new_row, new_col = head_row + dr, head_col + dc
            if (0 <= new_row < self.height and 
                0 <= new_col < self.width):
                self.snake.append((new_row, new_col))
                self.board[new_row, new_col] = 2
                break

    
    def generate_food(self):
        empty_positions = [(r, c) for r in range(self.height) 
                          for c in range(self.width) 
                          if self.board[r, c] == 0]
        
        if empty_positions:
            self.food = random.choice(empty_positions)
            self.board[self.food] = 1
        else:
            self.food = None

    def is_valid_move(self, head_pos, snake_body):
        """检查移动是否有效"""
        row, col = head_pos
        return (0 <= row < self.height and 
                0 <= col < self.width and 
                head_pos not in snake_body[:-1])  # 允许移动到即将离开的尾部位置

    def get_snake_after_move(self, snake_body, new_head):
        """返回移动后的蛇身"""
        return [new_head] + snake_body[:-1]

    def find_path(self):
        if self.food is None:
            return None
            
        # 使用BFS寻找最短路径，状态包含蛇的整个身体
        queue = deque([(self.snake[0], self.snake.copy(), [])])  # (头部位置, 蛇身列表, 路径)
        # visited存储蛇头位置和蛇身状态的组合
        visited = {(self.snake[0], tuple(self.snake))}
        
        directions = [(-1,0), (0,1), (1,0), (0,-1)]
        dir_symbols = ['up', 'right', 'down', 'left']
        
        while queue:
            head_pos, current_snake, path = queue.popleft()
            
            for (dr, dc), symbol in zip(directions, dir_symbols):
                new_head = (head_pos[0] + dr, head_pos[1] + dc)
                
                # 如果是食物位置，不需要移动蛇尾
                if new_head == self.food:
                    return path + [symbol]
                
                # 计算移动后的新蛇身
                new_snake = self.get_snake_after_move(current_snake, new_head)
                
                # 检查移动是否有效且状态未访问过
                new_state = (new_head, tuple(new_snake))
                if (self.is_valid_move(new_head, current_snake) and 
                    new_state not in visited):
                    
                    visited.add(new_state)
                    queue.append((new_head, new_snake, path + [symbol]))
        
        return None
    
    def print_board(self):
        symbols = {0: '0', 1: '1', 2: '2',3:'3'}
        print("\n当前地图状态：")
        for row in self.board:
            print(' '.join(symbols[int(cell)] for cell in row))
        print(f"\n蛇身位置：{self.snake}")
        print(f"蛇的长度：{len(self.snake)}")
        if self.food:
            print(f"食物位置：{self.food}")
        print()

    def simulate_path(self, path):
        """模拟路径并显示每一步"""
        if not path:
            return 3
        
        print('moves: ',path)

        ret=3
        analysis=''

        
        
        print("simulate path: ")
        current_snake = self.snake.copy()
        
        analysis+=f'At first the snake head(yellow block) is at {current_snake[0]}. '
        analysis+=f'The snake body(blue blocks) is at {current_snake[1:]}.\nThen it moves like this: '

        directions = {
            'up': (-1, 0),
            'right': (0, 1),
            'down': (1, 0),
            'left': (0, -1)
        }
        
        for step, symbol in enumerate(path, 1):
            dr, dc = directions[symbol]
            head_row, head_col = current_snake[0]
            new_head = (head_row + dr, head_col + dc)
            
            analysis+=f'step {step}: '
            analysis+=f'move {symbol}\n'

            # 更新蛇身

            analysis+=f'Before moving, the snake is at {current_snake}. '

            current_snake = self.get_snake_after_move(current_snake, new_head)
            
            #0: 碰壁 1: 吃到自己 2: 吃到食物 3: 其他
            head=current_snake[0]

            analysis+=f'After moving {symbol}, the snake head will move {symbol} directly, which will be at {head}. '
            analysis+=f'Each block of the snake body will move to the position of the block in front of it, so the snake body will be at {current_snake[1:]}.\n'

            x,y=head
            if x<0 or x>=self.height or y<0 or y>=self.width:
                analysis+='Now the snake hits the bound the grid.'
                return 0,analysis
            elif head in current_snake[1:]:
                analysis+='Now the snake hits its body.'
                return 1,analysis
            elif head==self.food:
                analysis+='Now the snake reaches the food.'
                return 2,analysis
            
        analysis+='Now the process ends and nothing else happens.'
        return 3,analysis

    def draw(self,image_path):
        # 填充背景色
        self.screen.fill(self.colors['grid'])
        
        # 绘制坐标标记
        coords_font = pygame.font.Font(None, self.cell_size // 2)
        # 绘制行号（左侧）
        for row in range(self.height):
            text = coords_font.render(str(row), True, self.colors['coords'])
            text_rect = text.get_rect(
                center=(self.margin // 2, 
                       self.margin + row * self.cell_size + self.cell_size // 2)
            )
            self.screen.blit(text, text_rect)
        
        # 绘制列号（上方）
        for col in range(self.width):
            text = coords_font.render(str(col), True, self.colors['coords'])
            text_rect = text.get_rect(
                center=(self.margin + col * self.cell_size + self.cell_size // 2,
                       self.margin // 2)
            )
            self.screen.blit(text, text_rect)
        
        # 绘制空白方格
        for row in range(self.height):
            for col in range(self.width):
                rect = pygame.Rect(
                    self.margin + col * self.cell_size + 1,
                    self.margin + row * self.cell_size + 1,
                    self.cell_size - 2,
                    self.cell_size - 2
                )
                pygame.draw.rect(self.screen, self.colors['background'], rect)

        # 绘制食物
        if self.food:
            food_rect = pygame.Rect(
                self.margin + self.food[1] * self.cell_size + 1,
                self.margin + self.food[0] * self.cell_size + 1,
                self.cell_size - 2,
                self.cell_size - 2
            )
            pygame.draw.rect(self.screen, self.colors['food'], food_rect)

        # 绘制蛇身方块
        for i, (row, col) in enumerate(self.snake):
            snake_rect = pygame.Rect(
                self.margin + col * self.cell_size + 1,
                self.margin + row * self.cell_size + 1,
                self.cell_size - 2,
                self.cell_size - 2
            )
            color = self.colors['snake_head'] if i == 0 else self.colors['snake_body']
            pygame.draw.rect(self.screen, color, snake_rect)
            


        # 绘制连接蛇身的黑线
        if len(self.snake) > 1:
            points = []
            for row, col in self.snake:
                # 获取每个蛇身方块的中心点
                center_x = self.margin + col * self.cell_size + self.cell_size // 2
                center_y = self.margin + row * self.cell_size + self.cell_size // 2
                points.append((center_x, center_y))
            
            # 绘制黑色连线
            pygame.draw.lines(self.screen, (0, 0, 0), False, points, width=4)

        #self.screen=pygame.transform.scale(self.screen,(480,480))
        #pygame.image.
        pygame.image.save(self.screen,image_path)
        #pygame.display.flip()
        '''
        # 填充背景色
        self.screen.fill(self.colors['grid'])

        # 绘制坐标标记
        coords_font = pygame.font.Font(None, self.cell_size // 2)
        # 绘制行号（左侧）
        for row in range(self.height):
            text = coords_font.render(str(row), True, self.colors['coords'])
            text_rect = text.get_rect(
                center=(self.margin // 2, 
                       self.margin + row * self.cell_size + self.cell_size // 2)
            )
            self.screen.blit(text, text_rect)
        
        # 绘制列号（上方）
        for col in range(self.width):
            text = coords_font.render(str(col), True, self.colors['coords'])
            text_rect = text.get_rect(
                center=(self.margin + col * self.cell_size + self.cell_size // 2,
                       self.margin // 2)
            )
            self.screen.blit(text, text_rect)
        
        # 绘制空白方格
        for row in range(self.height):
            for col in range(self.width):
                rect = pygame.Rect(col * self.cell_size + 1, 
                                 row * self.cell_size + 1,
                                 self.cell_size - 2, 
                                 self.cell_size - 2)
                pygame.draw.rect(self.screen, self.colors['background'], rect)

        # 绘制食物
        if self.food:
            food_rect = pygame.Rect(self.food[1] * self.cell_size + 1,
                                  self.food[0] * self.cell_size + 1,
                                  self.cell_size - 2,
                                  self.cell_size - 2)
            pygame.draw.rect(self.screen, self.colors['food'], food_rect)

        # 绘制蛇身方块
        for i, (row, col) in enumerate(self.snake):
            snake_rect = pygame.Rect(col * self.cell_size + 1,
                                   row * self.cell_size + 1,
                                   self.cell_size - 2,
                                   self.cell_size - 2)
            color = self.colors['snake_head'] if i == 0 else self.colors['snake_body']
            pygame.draw.rect(self.screen, color, snake_rect)
            

        # 绘制连接蛇身的黑线
        if len(self.snake) > 1:
            points = []
            for row, col in self.snake:
                # 获取每个蛇身方块的中心点
                center_x = col * self.cell_size + self.cell_size // 2
                center_y = row * self.cell_size + self.cell_size // 2
                points.append((center_x, center_y))
            
            # 绘制黑色连线
            pygame.draw.lines(self.screen, (0, 0, 0), False, points, width=16)

        print('image_path: ',image_path)
        pygame.image.save(self.screen,image_path)
        #pygame.display.flip()
        '''


# 测试代码
if __name__=='__main__':
    game = SnakeGame(width=10, height=10, snake_length=20)
    game.print_board()
    game.visualize()  # 显示初始状态
    game.draw()

    path = game.find_path()
    if path:
        print(f"找到最短路径：{''.join(path)}")
        print(f"路径长度：{len(path)}步")
        
        # 模拟显示路径
        game.simulate_path(path)
    else:
        print("没有找到有效路径！")