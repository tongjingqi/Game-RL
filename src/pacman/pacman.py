# pacman.py

import pygame
import sys
import os
from game_logic import PacManGame, Ghost

class GameDisplay:
    def __init__(self, game):
        """
        Initialize the GameDisplay with a PacManGame instance.

        :param game: Instance of PacManGame containing game logic.
        """
        self.game = game

        # Initialize Pygame
        pygame.init()

        # Set up display
        self.window_size = self.game.grid_size * self.game.cell_size
        self.screen = pygame.display.set_mode((self.window_size, self.window_size + 40))
        pygame.display.set_caption("Pac-Man")

        # Load images
        self.pacman_image_original = self.load_image('pacman.png')
        self.ghost_images = self.load_ghost_images()

        # Initialize fonts
        self.font = pygame.font.SysFont(None, 36)        # Default font, size 36
        self.large_font = pygame.font.SysFont(None, 72)  # Larger font for Game Over

    def load_image(self, image_name):
        """
        Load an image from the 'images' directory.

        :param image_name: Name of the image file.
        :return: Pygame Surface object with the loaded image.
        """
        image_path = os.path.join('images', image_name)
        try:
            image = pygame.image.load(image_path).convert_alpha()
            # Scale the image to fit within a cell
            image = pygame.transform.scale(image, (self.game.cell_size, self.game.cell_size))
            return image
        except pygame.error as e:
            print(f"Unable to load image at {image_path}: {e}")
            pygame.quit()
            sys.exit()

    def load_ghost_images(self):
        """
        Load ghost images based on the ghosts present in the game.

        :return: Dictionary mapping ghost names to their images.
        """
        ghost_images = {}
        for ghost in self.game.ghosts:
            image_name = f"{ghost.name}.png"
            ghost_images[ghost.name] = self.load_image(image_name)
        return ghost_images

    def get_rotated_image(self, image, direction):
        """
        Rotate an image based on the direction.

        :param image: Pygame Surface object to rotate.
        :param direction: Direction string ('UP', 'DOWN', 'LEFT', 'RIGHT').
        :return: Rotated Pygame Surface object.
        """
        if direction == 'UP':
            return pygame.transform.rotate(image, 90)
        elif direction == 'DOWN':
            return pygame.transform.rotate(image, -90)
        elif direction == 'LEFT':
            return pygame.transform.rotate(image, 180)
        elif direction == 'RIGHT':
            return image  # No rotation
        else:
            return image  # Default to original

    def draw_grid(self):
        """
        Draw the grid with walls, beans, Pac-Man, ghosts, and the score.
        """
        # Fill the entire screen with black (background)
        self.screen.fill(self.game.BLACK)

        # Draw the grid area background as black
        grid_area = pygame.Rect(0, 40, self.window_size, self.window_size)
        self.screen.fill(self.game.BLACK, grid_area)

        # Draw walls
        for wall in self.game.walls:
            row, col = wall
            rect = pygame.Rect(col * self.game.cell_size, 40 + row * self.game.cell_size,
                               self.game.cell_size, self.game.cell_size)
            pygame.draw.rect(self.screen, self.game.DEEP_BLUE, rect)

        # Draw beans
        for bean in self.game.beans:
            row, col = bean
            center_x = col * self.game.cell_size + self.game.cell_size // 2
            center_y = 40 + row * self.game.cell_size + self.game.cell_size // 2
            radius = self.game.cell_size // 6  # Adjust radius as needed
            pygame.draw.circle(self.screen, self.game.YELLOW, (center_x, center_y), radius)

        # Draw ghosts
        for ghost in self.game.ghosts:
            ghost_image = self.ghost_images.get(ghost.name, None)
            if ghost_image:
                ghost_x = ghost.position[1] * self.game.cell_size
                ghost_y = 40 + ghost.position[0] * self.game.cell_size
                self.screen.blit(ghost_image, (ghost_x, ghost_y))

        # Draw Pac-Man with rotation based on direction
        rotated_pacman = self.get_rotated_image(self.pacman_image_original, self.game.direction)
        pacman_x = self.game.pacman_position[1] * self.game.cell_size
        pacman_y = 40 + self.game.pacman_position[0] * self.game.cell_size
        self.screen.blit(rotated_pacman, (pacman_x, pacman_y))

        # Draw score
        score_text = self.font.render(f"Score: {self.game.score}", True, self.game.YELLOW)
        self.screen.blit(score_text, (10, 5))  # Position at top-left corner

        # If game over, display Game Over message
        if self.game.game_over:
            game_over_text = self.large_font.render("GAME OVER", True, self.game.RED)
            final_score_text = self.font.render(f"Final Score: {self.game.score}", True, self.game.RED)
            restart_text = self.font.render("Press R to Restart", True, self.game.RED)

            # Center the Game Over text
            text_rect = game_over_text.get_rect(center=(self.window_size // 2, self.window_size // 2))
            self.screen.blit(game_over_text, text_rect)

            # Position the final score below Game Over
            final_score_rect = final_score_text.get_rect(center=(self.window_size // 2, self.window_size // 2 + 50))
            self.screen.blit(final_score_text, final_score_rect)

            # Position the restart instruction below the final score
            restart_rect = restart_text.get_rect(center=(self.window_size // 2, self.window_size // 2 + 100))
            self.screen.blit(restart_text, restart_rect)

    def handle_events(self):
        """
        Handle user input events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game.game_over:
                    if event.key == pygame.K_r:
                        self.game.reset_game()
                        self.ghost_images = self.load_ghost_images()  # Reload ghost images in case of reset
                else:
                    if event.key == pygame.K_UP:
                        self.game.move_pacman('UP')
                    elif event.key == pygame.K_DOWN:
                        self.game.move_pacman('DOWN')
                    elif event.key == pygame.K_LEFT:
                        self.game.move_pacman('LEFT')
                    elif event.key == pygame.K_RIGHT:
                        self.game.move_pacman('RIGHT')
                    elif event.key == pygame.K_s:
                        # Save the game state
                        self.game.save_to_json("game_saves", "save_1.json")

    def update_display(self):
        """
        Update the game display by drawing all elements.
        """
        self.draw_grid()
        pygame.display.flip()

    def run(self):
        """
        Run the main game loop.
        """
        clock = pygame.time.Clock()

        while True:
            self.handle_events()

            # Update ghosts
            if not self.game.game_over:
                for ghost in self.game.ghosts:
                    ghost.update()

            # Check for collisions between ghosts and Pac-Man
            if not self.game.game_over:
                for ghost in self.game.ghosts:
                    if ghost.position == self.game.pacman_position:
                        self.game.trigger_game_over()
                        break  # No need to check further if game is over

            self.update_display()
            clock.tick(60)  # 60 FPS

def main():
    # Ensure the images directory exists and required images are present
    required_images = ['pacman.png', 'Pinky.png', 'Blinky.png']
    missing_images = [img for img in required_images if not os.path.exists(os.path.join('images', img))]
    if missing_images:
        print(f"Error: The following image(s) are missing in the 'images' folder: {', '.join(missing_images)}")
        print("Please ensure all required images are present before running the game.")
        sys.exit()

    # Initialize the game with cell_size parameter
    game = PacManGame(grid_size=20, cell_size=30, wall_ratio=0.1)
    game.save_to_json("game_saves", "save_1.json")
    display = GameDisplay(game)
    display.run()

if __name__ == "__main__":
    main()
