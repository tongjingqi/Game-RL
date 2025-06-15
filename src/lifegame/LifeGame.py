import pygame
import random
import sys
import datetime

# Constants
GRID_SIZE = 30       # Size of the grid (30x30 cells)
CELL_SIZE = 20       # Pixel size of each cell
FPS = 10            # Frames per second
MARGIN = 20         # Canvas margin width

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

def init_grid(grid_size, random_init=False):
    """Initialize the grid with random live cells or empty grid"""
    grid = [[0] * grid_size for _ in range(grid_size)]
    if random_init:
        # Randomly populate about 30% of cells
        for x in range(grid_size):
            for y in range(grid_size):
                grid[x][y] = 1 if random.random() < 0.3 else 0
    return grid

def count_neighbors(grid, x, y, grid_size):
    """Count live neighbors for a cell, including wrapping around edges"""
    count = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:  # Skip the cell itself
                continue
            # Use modulo for wrapping around edges
            nx = (x + dx) % grid_size
            ny = (y + dy) % grid_size
            count += grid[nx][ny]
    return count

def update_grid(grid, grid_size):
    """Update the grid according to Conway's Game of Life rules"""
    new_grid = [[0] * grid_size for _ in range(grid_size)]
    
    for x in range(grid_size):
        for y in range(grid_size):
            neighbors = count_neighbors(grid, x, y, grid_size)
            # Apply Conway's Game of Life rules:
            # 1. Any live cell with 2 or 3 live neighbors survives
            # 2. Any dead cell with exactly 3 live neighbors becomes alive
            # 3. All other cells die or stay dead
            if grid[x][y] == 1:  # Live cell
                new_grid[x][y] = 1 if neighbors in [2, 3] else 0
            else:  # Dead cell
                new_grid[x][y] = 1 if neighbors == 3 else 0
                
    return new_grid

def draw_grid(screen, grid, cell_size, margin, offset):
    """Draw the grid with cells and grid lines"""
    # Draw cells
    for x in range(len(grid)):
        for y in range(len(grid[0])):
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

def draw_coordinates(screen, grid_size, cell_size, margin, offset):
    """Draw coordinate numbers around the grid"""
    font = pygame.font.Font(None, 15)
    for x in range(grid_size):
        # Draw x coordinates on the left
        text = font.render(str(x), True, BLACK)
        screen.blit(text, (offset - margin // 2, offset + x * cell_size + cell_size // 2))

    for y in range(grid_size):
        # Draw y coordinates on top
        text = font.render(str(y), True, BLACK)
        screen.blit(text, (offset + y * cell_size + cell_size // 2, offset - margin // 2))

def save_screen(screen):
    """Save the current screen as a PNG file with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gameoflife_{timestamp}.png"
    pygame.image.save(screen, filename)
    print(f"Screen saved as {filename}")

def handle_mouse_input(pos, grid, cell_size, margin, offset, grid_size):
    """Handle mouse clicks to toggle cells"""
    x = (pos[1] - offset) // cell_size
    y = (pos[0] - offset) // cell_size
    if 0 <= x < grid_size and 0 <= y < grid_size:
        grid[x][y] = 1 - grid[x][y]  # Toggle cell state

def main():
    pygame.init()
    grid_size = GRID_SIZE
    screen_size = (grid_size * CELL_SIZE + MARGIN * 2, 
                  grid_size * CELL_SIZE + MARGIN * 2)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()

    # Initialize grid
    grid = init_grid(grid_size, random_init=False)
    running = False  # Simulation state
    drawing = False  # Mouse drawing state
    global FPS

    while True:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Toggle simulation
                    running = not running
                elif event.key == pygame.K_r:    # Reset grid (random)
                    grid = init_grid(grid_size, random_init=True)
                    running = False
                elif event.key == pygame.K_c:    # Clear grid
                    grid = init_grid(grid_size, random_init=False)
                    running = False
                elif event.key == pygame.K_UP:   # Increase speed
                    FPS = min(60, FPS + 5)
                    print(f"FPS increased to {FPS}")
                elif event.key == pygame.K_DOWN: # Decrease speed
                    FPS = max(1, FPS - 5)
                    print(f"FPS decreased to {FPS}")
                elif event.key == pygame.K_s:    # Save screenshot
                    save_screen(screen)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    drawing = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    drawing = False
            elif event.type == pygame.MOUSEMOTION:
                if drawing:  # Draw cells while dragging
                    offset = (screen_size[0] - grid_size * CELL_SIZE) // 2
                    handle_mouse_input(event.pos, grid, CELL_SIZE, MARGIN, offset, grid_size)

        # Update grid if simulation is running
        if running:
            grid = update_grid(grid, grid_size)

        # Calculate offset to center the grid
        offset = (screen_size[0] - grid_size * CELL_SIZE) // 2

        # Draw everything
        draw_grid(screen, grid, CELL_SIZE, MARGIN, offset)
        draw_coordinates(screen, grid_size, CELL_SIZE, MARGIN, offset)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()