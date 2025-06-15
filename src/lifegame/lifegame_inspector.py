import pygame
import json
import sys
from typing import List, Dict, Tuple, Set
import argparse

# Constants
CELL_SIZE = 20
MARGIN = 40
FPS = 10
INFO_PANEL_WIDTH = 300  # 新增：信息面板宽度
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0) 

def load_state(file_path: str) -> List[List[int]]:
    """Load grid state from JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
        return data.get('grid', [])

class CellChange:
    """Class to track cell changes and their types."""
    def __init__(self, position: Tuple[int, int], old_state: int, new_state: int):
        self.position = position
        self.old_state = old_state
        self.new_state = new_state
    
    @property
    def is_birth(self) -> bool:
        """Check if this change represents a cell birth (0 -> 1)."""
        return self.old_state == 0 and self.new_state == 1
    
    @property
    def color(self) -> Tuple[int, int, int]:
        """Get the appropriate color for this change."""
        return GREEN if self.is_birth else RED

def draw_grid(screen, grid: List[List[int]], cell_size: int, margin: int, offset: int, 
              highlighted_changes: List[CellChange] = None):
    """
    Draw the grid with cells and grid lines.
    Uses color coding to show cell state changes:
    - Green: Cell became alive (0 -> 1)
    - Red: Cell died (1 -> 0)
    """
    # Create a lookup dictionary for changed cells
    changes_dict = {}
    if highlighted_changes:
        changes_dict = {change.position: change for change in highlighted_changes}
    
    # Draw cells
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if (x, y) in changes_dict:
                # Draw changed cell with appropriate color
                color = changes_dict[(x, y)].color
            else:
                # Draw normal cell
                color = BLACK if grid[x][y] == 1 else WHITE
            
            pygame.draw.rect(screen, color, 
                           (offset + y * cell_size, 
                            offset + x * cell_size, 
                            cell_size, cell_size))

    # Draw grid lines
    for x in range(len(grid) + 1):
        pygame.draw.line(screen, GRAY, 
                        (offset, offset + x * cell_size),
                        (offset + len(grid[0]) * cell_size, offset + x * cell_size))
    for y in range(len(grid[0]) + 1):
        pygame.draw.line(screen, GRAY,
                        (offset + y * cell_size, offset),
                        (offset + y * cell_size, offset + len(grid) * cell_size))

def update_grid(grid: List[List[int]]) -> Tuple[List[List[int]], List[CellChange]]:
    """
    Update the grid and track all cell changes.
    Returns the new grid and a list of cell changes.
    """
    size = len(grid)
    new_grid = [[0] * size for _ in range(size)]
    changes = []
    
    for x in range(size):
        for y in range(size):
            neighbors = count_neighbors(grid, x, y)
            old_state = grid[x][y]
            
            # Apply Conway's Game of Life rules
            if old_state == 1:
                new_grid[x][y] = 1 if neighbors in [2, 3] else 0
            else:
                new_grid[x][y] = 1 if neighbors == 3 else 0
            
            # Record changes
            if new_grid[x][y] != old_state:
                changes.append(CellChange((x, y), old_state, new_grid[x][y]))
    
    return new_grid, changes

def draw_coordinates(screen, grid_size: int, cell_size: int, margin: int, offset: int):
    """Draw coordinate numbers around the grid."""
    font = pygame.font.Font(None, 20)
    for x in range(grid_size):
        text = font.render(str(x), True, BLACK)
        text_rect = text.get_rect(right=offset-5, centery=offset + x * cell_size + cell_size//2)
        screen.blit(text, text_rect)

    for y in range(grid_size):
        text = font.render(str(y), True, BLACK)
        text_rect = text.get_rect(centerx=offset + y * cell_size + cell_size//2, bottom=offset-5)
        screen.blit(text, text_rect)

def draw_help(screen, font,info_panel_x):
    """Draw help text on screen."""
    help_text = [
        "Controls:",
        "Left Click: Toggle cell",
        "Space: Play/Pause simulation",
        "N: Step forward one generation",
        "H: Show/Hide this help",
        "R: Reset to initial state",
        "S: Save current state",
        "D: shows neighbor counts",
        "Q: Quit"
    ]
    for i, text in enumerate(help_text):
        surface = font.render(text, True, BLACK)
        screen.blit(surface, (info_panel_x+10, 10 + i * 20))

def draw_debug_info(screen, grid: List[List[int]], cell_size: int, margin: int, offset: int):
    """Draw neighbor counts for each cell."""
    font = pygame.font.Font(None, 20)
    for x in range(len(grid)):
        for y in range(len(grid)):
            neighbors = count_neighbors(grid, x, y)
            text = font.render(str(neighbors), True, RED)
            pos = (offset + y * cell_size + cell_size//4,
                  offset + x * cell_size + cell_size//4)
            screen.blit(text, pos)

def handle_mouse_input(pos, grid, cell_size, margin, offset) -> Tuple[List[CellChange], bool]:
    """
    Handle mouse clicks to toggle cells.
    Returns a list of changes and whether the input was valid.
    """
    x = (pos[1] - offset) // cell_size
    y = (pos[0] - offset) // cell_size
    
    if 0 <= x < len(grid) and 0 <= y < len(grid):
        old_state = grid[x][y]
        grid[x][y] = 1 - grid[x][y]
        print(f"Cell at ({x}, {y}) toggled from {old_state} to {grid[x][y]}")
        return [CellChange((x, y), old_state, grid[x][y])], True
    
    return [], False

def count_neighbors(grid, x, y):
    """Count live neighbors for a cell."""
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

def draw_statistics(screen, stats: Dict[str, int], font, info_panel_x):
    """Draw cell statistics on the screen."""
    # Define colors for the stats
    stats_colors = {
        'living': BLACK,
        'births': GREEN,
        'deaths': RED
    }
    
    # Define labels
    labels = {
        'living': 'Living Cells(Black):',
        'births': 'New Births(Green):',
        'deaths': 'Recent Deaths(Red):'
    }
    
    # Position for stats (right side of screen)
    
    # Draw each statistic
    for i, (key, label) in enumerate(labels.items()):
        # Draw label
        label_surface = font.render(label, True, stats_colors[key])
        screen.blit(label_surface, (info_panel_x + 10, 200 + i * 20))
        
        # Draw count
        count_surface = font.render(str(stats[key]), True, stats_colors[key])
        screen.blit(count_surface, (info_panel_x + 180, 200 + i * 20))

def count_cell_states(grid: List[List[int]], highlighted_changes: List[CellChange] = None) -> Dict[str, int]:
    """
    Count cells in different states.
    Returns a dictionary with counts of:
    - Living cells (black)
    - Birth cells (green)
    - Death cells (red)
    """
    # Initialize counters
    stats = {
        'living': 0,    # Black cells
        'births': 0,    # Green cells
        'deaths': 0     # Red cells
    }
    
    # Create lookup for changed cells
    changes_dict = {}
    if highlighted_changes:
        changes_dict = {change.position: change for change in highlighted_changes}
    
    # Count cells in different states
    size = len(grid)
    for x in range(size):
        for y in range(size):
            if (x, y) in changes_dict:
                # Count changed cells
                change = changes_dict[(x, y)]
                if change.is_birth:
                    stats['births'] += 1
                else:
                    stats['deaths'] += 1
            elif grid[x][y] == 1:
                # Count living cells (excluding newly born cells)
                stats['living'] += 1
    
    return stats

def main():
    parser = argparse.ArgumentParser(description='Game of Life State Inspector')
    parser.add_argument('state_file', help='Path to the state JSON file')
    args = parser.parse_args()

    pygame.init()
    initial_grid = load_state(args.state_file)
    grid = [row[:] for row in initial_grid]
    grid_size = len(grid)
    
    cell_size = min(CELL_SIZE, 600 // grid_size)
    grid_width = grid_size * cell_size + MARGIN * 2
    screen_width = grid_width + INFO_PANEL_WIDTH
    screen_height = max(grid_size * cell_size + MARGIN * 2, 600)  # 确保最小高度
    screen_size = (screen_width, screen_height)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption(f"Life Game Inspector - {args.state_file}")
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    running = False
    drawing = False
    show_help = True
    debug_mode = False
    highlighted_changes = []
    generation = 0

    while True:
        screen.fill(WHITE)
        offset = (grid_width - grid_size * cell_size) // 2
        info_panel_x = grid_width  # 信息面板起始x坐标
        
        # Calculate current statistics
        stats = count_cell_states(grid, highlighted_changes)
        
        pygame.draw.line(screen, GRAY, (grid_width, 0), (grid_width, screen_height))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = not running
                    print(f"Simulation {'started' if running else 'paused'} at generation {generation}")
                
                elif event.key == pygame.K_n and not running:
                    grid, highlighted_changes = update_grid(grid)
                    generation += 1
                    changes_str = "\n".join(
                        f"Cell at {change.position}: {'Birth' if change.is_birth else 'Death'}"
                        for change in highlighted_changes
                    )
                    print(f"Generation {generation} changes:\n{changes_str}")
                
                elif event.key == pygame.K_h:
                    show_help = not show_help
                
                elif event.key == pygame.K_r:
                    grid = [row[:] for row in initial_grid]
                    generation = 0
                    highlighted_changes = []
                    print("Reset to initial state")
                
                elif event.key == pygame.K_s:
                    with open(args.state_file, 'w') as f:
                        json.dump({"grid": grid}, f)
                    print(f"State saved to {args.state_file}")
                
                elif event.key == pygame.K_d:
                    debug_mode = not debug_mode
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drawing = True
                    changes, valid = handle_mouse_input(event.pos, grid, cell_size, MARGIN, offset)
                    if valid:
                        highlighted_changes = changes
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False
            
            elif event.type == pygame.MOUSEMOTION:
                if drawing:
                    changes, valid = handle_mouse_input(event.pos, grid, cell_size, MARGIN, offset)
                    if valid:
                        highlighted_changes = changes
        
        if running:
            grid, highlighted_changes = update_grid(grid)
            generation += 1
        
        # Draw everything
        draw_grid(screen, grid, cell_size, MARGIN, offset, highlighted_changes)
        draw_coordinates(screen, grid_size, cell_size, MARGIN, offset)
        
        # Draw statistics
        draw_statistics(screen, stats, font, info_panel_x)
        
        if show_help:
            # Draw help text
            draw_help(screen, font, info_panel_x)
        
        if debug_mode:
            draw_debug_info(screen, grid, cell_size, MARGIN, offset)
        
        # 在右侧信息面板底部绘制世代计数器
        gen_text = font.render(f"Generation: {generation}", True, BLACK)
        screen.blit(gen_text, (info_panel_x + 10, screen_height - 30))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()