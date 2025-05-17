import os
import json
from PIL import Image, ImageDraw, ImageFont
from grid import TetrisGrid

class TetrisStateGenerator:
    def __init__(self, output_dir="tetris_dataset"):
        self.output_dir = output_dir
        self.setup_directories()
        self.current_id = 1
        
    def setup_directories(self):
        dirs = [
            os.path.join(self.output_dir, "images"),
            os.path.join(self.output_dir, "states")
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            
    def generate_image(self, grid, filename):
        cell_size = 30
        padding = 35  # 增加padding以容纳坐标标签
        width = grid.cols * cell_size + 2 * padding
        height = grid.rows * cell_size + 2 * padding
        filename = os.path.join(self.output_dir, filename)
        
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 添加字体
        try:
            font = ImageFont.truetype("font/Arial.ttf", 20)  # 使用Arial字体
        except:
            font = ImageFont.load_default()  # 如果找不到Arial字体，使用默认字体
        
        # Draw grid lines and cells
        for row in range(grid.rows):
            for col in range(grid.cols):
                x1 = col * cell_size + padding
                y1 = row * cell_size + padding
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Fill cell
                if grid.grid[row][col] == 1:
                    draw.rectangle([x1, y1, x2, y2], fill='gray')
                if grid.grid[row][col] == 2:
                    draw.rectangle([x1, y1, x2, y2], fill='red')
                
                # Draw cell border
                draw.rectangle([x1, y1, x2, y2], outline='black')
        
        # 添加行号(纵坐标)
        for row in range(grid.rows):
            y = row * cell_size + padding + cell_size//2
            draw.text((padding-20, y-8), str(row), fill='black', font=font)
            
        # 添加列号(横坐标)
        for col in range(grid.cols):
            # consider x is 2-digit number
            x = col * cell_size + padding + cell_size//2 if col < 10 else col * cell_size + padding + cell_size//2 - 7
            draw.text((x-4, padding-20), str(col), fill='black', font=font)
        
        if not filename.lower().endswith('.png'):
            filename += '.png'
            
        img.save(filename, format='PNG')
        
    def generate_state_json(self, grid, filename):
        state = {
            'grid': grid.grid.tolist(),
            'rows': grid.rows,
            'cols': grid.cols
        }

        filename = os.path.join(self.output_dir, filename)
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=1)

    def generate_state(self, rows=10, cols=10, num_moves=5):
        """Generate a single game state and return relevant paths"""
        # Generate puzzle ID
        puzzle_id = f"tetris-{str(self.current_id).zfill(5)}"
        self.current_id += 1
        
        # Create grid and simulate game
        grid = TetrisGrid(rows, cols)
        grid.simulate_realistic_game(num_moves)
        
        # Generate file paths
        image_path = f"images/{puzzle_id}.png"
        state_path = f"states/{puzzle_id}.json"
        
        # # Generate files
        # self.generate_image(grid, image_path)
        # self.generate_state_json(grid, state_path)

        return {
            "puzzle_id": puzzle_id,
            "grid": grid,
            "image_path": image_path,
            "state_path": state_path,
            "num_moves": num_moves,
            "rows": rows,
        }


    def generate_all_states(self, num_states, rows=10, cols=10, num_moves=5):
        
        states = []
        for _ in range(num_states):
            state = self.generate_state(rows, cols, num_moves)
            states.append(state)
        return states
    
    def save_states(self,states):
        for state in states:
            self.generate_image(state['grid'], state['image_path'])
            self.generate_state_json(state['grid'], state['state_path'])