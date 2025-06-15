# image_generator.py

from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

from game_logic import PacManGame

class PacManImageGenerator:
    def __init__(self, game):
        """
        Initialize the PacMan image generator.
        
        :param game: Instance of PacManGame containing game state
        """
        self.game = game
        self.image_width = 540
        self.score_height = 20
        
        # Add margin for row/column annotations
        self.left_margin = 30  # Space for row numbers
        self.top_margin = 30   # Space for column numbers
        
        # Calculate available space for grid
        self.grid_width = self.image_width - self.left_margin
        self.grid_height = 540 - self.score_height - self.top_margin
        self.total_height = self.score_height + self.top_margin + self.grid_height
        
        # Calculate cell size based on available space and grid dimensions
        self.cell_size = min(self.grid_width // self.game.grid_size,
                           self.grid_height // self.game.grid_size)
        
        # Recalculate actual grid dimensions
        self.actual_grid_width = self.cell_size * self.game.grid_size
        self.actual_grid_height = self.cell_size * self.game.grid_size
        
        # Define colors (RGB)
        self.BLACK = (0, 0, 0)
        self.DEEP_BLUE = (0, 0, 139)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.PINK = (255, 182, 193)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        
        # Load character images
        self.pacman_image = self.load_and_scale_image("images/pacman.png")
        self.ghost_images = {
            'Pinky': self.load_and_scale_image("images/Pinky.png"),
            'Blinky': self.load_and_scale_image("images/Blinky.png")
        }
        
        # Try to load font
        try:
            self.font = ImageFont.truetype(os.path.join("font","Arial.tff"), 12)
            self.large_font = ImageFont.truetype(os.path.join("font","Arial.tff"), 36)
        except IOError:
            self.font = ImageFont.load_default()
            self.large_font = ImageFont.load_default()

    def draw_grid_annotations(self, draw):
        """
        Draw row and column numbers around the grid with tick marks.
        
        :param draw: ImageDraw object to draw on
        """
        tick_length = 5  # Length of tick marks
        
        # Draw column numbers and ticks (top)
        for col in range(self.game.grid_size):
            # Calculate positions
            x = self.left_margin + col * self.cell_size + self.cell_size // 2
            y_text = self.score_height + 2  # Text position
            y_tick_start = self.score_height + self.top_margin - tick_length
            y_tick_end = self.score_height + self.top_margin
            
            # Draw tick mark
            draw.line([(x, y_tick_start), (x, y_tick_end)], 
                     fill=self.WHITE, width=1)
            
            # Draw number
            text = str(col)
            text_width = draw.textlength(text, font=self.font)
            draw.text((x - text_width//2, y_text), 
                     text, fill=self.WHITE, font=self.font)
        
        # Draw row numbers and ticks (left)
        for row in range(self.game.grid_size):
            # Calculate positions
            y = self.score_height + self.top_margin + row * self.cell_size + self.cell_size // 2
            x_text = 2  # Text position
            x_tick_start = self.left_margin - tick_length
            x_tick_end = self.left_margin
            
            # Draw tick mark
            draw.line([(x_tick_start, y), (x_tick_end, y)], 
                     fill=self.WHITE, width=1)
            
            # Draw number
            text = str(row)
            text_width = draw.textlength(text, font=self.font)
            draw.text((x_text, y - 7), 
                     text, fill=self.WHITE, font=self.font)

    def draw_score(self, draw):
        """
        Draw the score at the top of the image.
        
        :param draw: ImageDraw object to draw on
        """
        score_text = f"Score: {self.game.score}"
        draw.text((10, 2), score_text, fill=self.YELLOW, font=self.font)

    def draw_walls(self, draw):
        """
        Draw the maze walls on the image.
        
        :param draw: ImageDraw object to draw on
        """
        for wall in self.game.walls:
            row, col = wall
            x = self.left_margin + col * self.cell_size
            y = self.score_height + self.top_margin + row * self.cell_size
            draw.rectangle(
                [x, y, x + self.cell_size, y + self.cell_size],
                fill=self.DEEP_BLUE
            )

    def draw_beans(self, draw):
        """
        Draw the beans (dots) on the image.
        
        :param draw: ImageDraw object to draw on
        """
        for bean in self.game.beans:
            row, col = bean
            center_x = self.left_margin + col * self.cell_size + self.cell_size // 2
            center_y = self.score_height + self.top_margin + row * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 6
            draw.ellipse(
                [center_x - radius, center_y - radius,
                 center_x + radius, center_y + radius],
                fill=self.YELLOW
            )

    def load_and_scale_image(self, image_path):
        """
        Load and scale an image to fit the cell size.
        
        :param image_path: Path to the image file
        :return: PIL Image object scaled to cell size
        """
        try:
            image = Image.open(image_path)
            return image.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # Create a placeholder colored square
            placeholder = Image.new('RGB', (self.cell_size, self.cell_size), self.YELLOW)
            return placeholder
            
    def rotate_image(self, image, direction):
        """
        Rotate an image based on the direction.
        
        :param image: PIL Image object to rotate
        :param direction: Direction string ('UP', 'DOWN', 'LEFT', 'RIGHT')
        :return: Rotated PIL Image object
        """
        if direction == 'LEFT':
            return image.rotate(180)
        elif direction == 'UP':
            return image.rotate(90)
        elif direction == 'DOWN':
            return image.rotate(-90)
        return image  # 'RIGHT' or default case
            
    def draw_pacman(self, draw):
        """
        Draw Pac-Man on the image.
        
        :param draw: ImageDraw object to draw on
        """
        row, col = self.game.pacman_position
        x = self.left_margin + col * self.cell_size
        y = self.score_height + self.top_margin + row * self.cell_size
        
        # Rotate Pac-Man image based on direction
        rotated_pacman = self.rotate_image(self.pacman_image, self.game.direction)
        
        # Paste the rotated image onto the game board
        self.image.paste(rotated_pacman, (x, y))

    def draw_ghosts(self, draw):
        """
        Draw the ghosts on the image.
        
        :param draw: ImageDraw object to draw on
        """
        for ghost in self.game.ghosts:
            row, col = ghost.position
            x = self.left_margin + col * self.cell_size
            y = self.score_height + self.top_margin + row * self.cell_size
            
            # Get the corresponding ghost image
            ghost_image = self.ghost_images.get(ghost.name)
            if ghost_image:
                # Paste the ghost image onto the game board
                self.image.paste(ghost_image, (x, y))

    def draw_game_over(self, draw):
        """
        Draw the game over screen if the game is finished.
        
        :param draw: ImageDraw object to draw on
        """
        if self.game.game_over:
            # Semi-transparent overlay
            overlay = Image.new('RGBA', (self.image_width, self.total_height), (0, 0, 0, 128))
            Image.alpha_composite(self.image.convert('RGBA'), overlay)
            
            # Game Over text
            text = "GAME OVER"
            text_width = draw.textlength(text, font=self.large_font)
            x = (self.image_width - text_width) // 2
            y = (self.total_height - 36) // 2
            draw.text((x, y), text, fill=self.RED, font=self.large_font)
            
            # Final score
            score_text = f"Final Score: {self.game.score}"
            score_width = draw.textlength(score_text, font=self.font)
            x = (self.image_width - score_width) // 2
            draw.text((x, y + 40), score_text, fill=self.RED, font=self.font)

    def generate_image(self, output_folder="game_images", filename="game_state.png"):
        """
        Generate and save a PNG image of the current game state.
        
        :param output_folder: Folder where the image will be saved
        :param filename: Name of the output image file
        :return: Path to the generated image
        """
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Create a new image with a black background
        self.image = Image.new('RGB', (self.image_width, self.total_height), self.BLACK)
        draw = ImageDraw.Draw(self.image)
        
        # Draw all game elements
        self.draw_grid_annotations(draw)  # Draw annotations first
        self.draw_walls(draw)
        self.draw_beans(draw)
        self.draw_pacman(draw)
        self.draw_ghosts(draw)
        self.draw_score(draw)
        
        if self.game.game_over:
            self.draw_game_over(draw)
        
        # Save the image
        output_path = os.path.join(output_folder, filename)
        self.image.save(output_path)
        
        return output_path

def generate_game_image(game, output_folder="game_images", filename="game_state.png"):
    """
    Convenience function to generate a game state image without creating a class instance.
    
    :param game: Instance of PacManGame containing game state
    :param output_folder: Folder where the image will be saved
    :param filename: Name of the output image file
    :return: Path to the generated image
    """
    generator = PacManImageGenerator(game)
    return generator.generate_image(output_folder, filename)

if __name__ == "__main__":
    game = PacManGame(grid_size=20, cell_size=30, wall_ratio=0.1)
    game.set_direction("UP")
    generate_game_image(game, "output_folder", "game3.png")