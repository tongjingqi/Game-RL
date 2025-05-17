import random
import numpy as np

class TetrisGrid:
    # Define tetromino shapes (I, O, T, L, J, S, Z)
    TETROMINOES = {
        'I': np.array([[1, 1, 1, 1]]),
        'O': np.array([[1, 1],
                      [1, 1]]),
        'T': np.array([[0, 1, 0],
                      [1, 1, 1]]),
        'L': np.array([[1, 0],
                      [1, 0],
                      [1, 1]]),
        'J': np.array([[0, 1],
                      [0, 1],
                      [1, 1]]),
        'S': np.array([[0, 1, 1],
                      [1, 1, 0]]),
        'Z': np.array([[1, 1, 0],
                      [0, 1, 1]])
    }

    def __init__(self, rows=10, cols=10):
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=int)  # 0 for empty, 1 for filled
        
    def rotate_tetromino(self, tetromino, times=1):
        """Rotate tetromino clockwise n times"""
        times = (-times % 4)
        return np.rot90(tetromino, times)
    
    def is_valid_position(self, tetromino, pos_row, pos_col):
        """Check if tetromino can be placed at given position"""
        shape = tetromino.shape
        
        # Check bounds
        if (pos_row + shape[0] > self.rows or
            pos_col + shape[1] > self.cols or
            pos_col < 0):
            return False
            
        # Check collision with existing blocks
        for i in range(shape[0]):
            for j in range(shape[1]):
                if tetromino[i][j] == 1:
                    if (pos_row + i >= self.rows or
                        pos_col + j >= self.cols or
                        self.grid[pos_row + i][pos_col + j] == 1):
                        return False
        return True
    
    def place_tetromino(self, tetromino, pos_row, pos_col):
        """Place tetromino at given position"""
        shape = tetromino.shape
        for i in range(shape[0]):
            for j in range(shape[1]):
                if tetromino[i][j] == 1:
                    self.grid[pos_row + i][pos_col + j] = 1
    
    def find_landing_position(self, tetromino, col):
        """Find the lowest valid position for a tetromino in a given column"""
        row = 0
        while row <= self.rows - tetromino.shape[0]:
            if not self.is_valid_position(tetromino, row + 1, col):
                return row
            row += 1
        return row
    
    def clear_full_rows(self):
        """Clear full rows and drop blocks above them"""
        full_rows = []
        for i in range(self.rows):
            if np.all(self.grid[i] == 1):
                full_rows.append(i)
        
        if full_rows:
            # Remove full rows and add empty rows at top
            self.grid = np.delete(self.grid, full_rows, axis=0)
            self.grid = np.vstack([np.zeros((len(full_rows), self.cols)), self.grid])
    
    def evaluate_position(self, tetromino, pos_row, pos_col):
        """
        Evaluate how good a position is for placing the tetromino.
        Returns a score (higher is better).
        """
        # Make a copy of the grid for simulation
        temp_grid = self.grid.copy()
        
        # Place tetromino in temporary grid
        height = tetromino.shape[0]
        width = tetromino.shape[1]
        for i in range(height):
            for j in range(width):
                if tetromino[i][j] == 1:
                    temp_grid[pos_row + i][pos_col + j] = 1
        
        # Calculate score components
        
        # 1. Lines cleared (highest priority)
        lines_cleared = 0
        for row in range(self.rows):
            if np.all(temp_grid[row] == 1):
                lines_cleared += 1
        lines_score = lines_cleared * 100  # High weight for lines cleared
        
        # 2. Holes created (gaps with blocks above them)
        holes_before = self.count_holes(self.grid)
        holes_after = self.count_holes(temp_grid)
        holes_created = holes_after - holes_before
        holes_score = -50 * holes_created  # Negative score for creating holes
        
        # 3. Change in maximum height
        old_height = self.get_max_height(self.grid)
        new_height = self.get_max_height(temp_grid)
        height_increase = new_height - old_height
        height_score = -30 * max(0, height_increase)  # Negative score for increasing height
        
        # Calculate final score
        total_score = lines_score + holes_score + height_score
        
        return total_score
    
    def count_holes(self, grid):
        """Count number of holes (empty cells with filled cells above them)"""
        holes = 0
        for col in range(self.cols):
            block_found = False
            for row in range(self.rows):
                if grid[row][col] == 1:
                    block_found = True
                elif block_found and grid[row][col] == 0:
                    holes += 1
        return holes
    
    def get_max_height(self, grid):
        """Get the maximum height of blocks in the grid"""
        for row in range(self.rows):
            if np.any(grid[row] == 1):
                return self.rows - row
        return 0
    
    def simulate_realistic_game(self, num_moves=30):
        """Simulate a realistic Tetris game for a given number of strategic moves"""
        game_over = False
        for _ in range(num_moves):
            # Choose random tetromino and rotation
            tetromino_type = random.choice(list(self.TETROMINOES.keys()))
            tetromino = self.TETROMINOES[tetromino_type].copy()
            
            # Try all rotations and positions to find the best one
            best_score = float('-inf')
            best_position = None
            best_rotation = None
            
            for rotation in range(4):
                rotated_tetromino = self.rotate_tetromino(tetromino, rotation)
                
                # Try all possible columns
                for col in range(-2, self.cols):
                    if not self.is_valid_position(rotated_tetromino, 0, col):
                        continue
                    
                    # Find landing position
                    row = self.find_landing_position(rotated_tetromino, col)
                    
                    # Evaluate this position
                    score = self.evaluate_position(rotated_tetromino, row, col)
                    
                    if score > best_score:
                        best_score = score
                        best_position = (row, col)
                        best_rotation = rotation
            
            if best_position is None:  # If no valid moves found
                game_over = True
                break
            
            # Place tetromino in best position found
            best_tetromino = self.rotate_tetromino(tetromino, best_rotation)
            self.place_tetromino(best_tetromino, best_position[0], best_position[1])
            self.clear_full_rows()
        
        # If the game is not over, add a new falling tetromino to the grid
        if not game_over:
            # Choose a random tetromino and rotation
            falling_tetromino_type = random.choice(list(self.TETROMINOES.keys()))
            falling_tetromino = self.TETROMINOES[falling_tetromino_type].copy()
            falling_rotation = random.randint(0, 3)
            falling_tetromino = self.rotate_tetromino(falling_tetromino, falling_rotation)
            
            # Find a random valid column where the tetromino can be placed
            valid_cols_for_falling = []
            for col in range(self.cols):
                # Check if the tetromino can fit at least one empty row above the highest block
                highest_row = np.argmax(np.any(self.grid == 1, axis=1)) if np.any(self.grid == 1) else self.rows
                if highest_row >= falling_tetromino.shape[0] + 1:  # Ensure at least one empty row
                    if self.is_valid_position(falling_tetromino, highest_row - falling_tetromino.shape[0] - 1, col):
                        valid_cols_for_falling.append(col)
            
            if valid_cols_for_falling:
                falling_col = random.choice(valid_cols_for_falling)
                # Calculate the row where the tetromino will start falling
                falling_row = highest_row - falling_tetromino.shape[0] - 1
                
                # Add the falling tetromino to the grid
                for i in range(falling_tetromino.shape[0]):
                    for j in range(falling_tetromino.shape[1]):
                        if falling_tetromino[i][j] == 1:
                            self.grid[falling_row + i][falling_col + j] = 2  # Use 2 to indicate falling tetromino
    
    
    def empty_cells_in_row(self, row):
        """Return coordinates of empty cells in a given row"""
        if 0 <= row < self.rows:
            empty_cells = []
            for col in range(self.cols):
                if self.grid[row][col] == 0:
                    empty_cells.append((row,col))
            return empty_cells
        return []

    def get_grid_stats(self):
        """Get statistics about the current grid state"""
        stats = {
            'total_filled': np.sum(self.grid == 1),
            'total_empty': np.sum(self.grid == 0),
            'highest_block': self.rows - np.argmax(np.any(self.grid == 1, axis=1)),
            'holes': self._count_holes(),
            'complete_lines': self._count_complete_lines()
        }
        return stats

    def _count_holes(self):
        """Count enclosed empty cells (holes)"""
        holes = 0
        for col in range(self.cols):
            found_block = False
            for row in range(self.rows):
                if self.grid[row][col] == 1:
                    found_block = True
                elif found_block and self.grid[row][col] == 0:
                    holes += 1
        return holes

    def _count_complete_lines(self):
        """Count number of complete lines"""
        return sum(1 for row in range(self.rows) if np.all(self.grid[row] == 1))
    
    
    def count_empty_cells_in_row(self, row):
        if 0 <= row < self.rows:
            return np.sum(self.grid[row] == 0)
        return 0