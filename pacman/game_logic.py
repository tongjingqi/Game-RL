# game_logic.py

import random
import os
import json
from collections import deque

class UnionFind:
    """Union-Find (Disjoint Set) data structure for cycle detection."""
    def __init__(self):
        self.parent = {}

    def find(self, item):
        """Find the root of the set in which element `item` belongs."""
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])  # Path compression
        return self.parent[item]

    def union(self, item1, item2):
        """Union the sets containing `item1` and `item2`."""
        root1 = self.find(item1)
        root2 = self.find(item2)
        if root1 == root2:
            return False  # Cycle detected
        self.parent[root2] = root1
        return True

class Ghost:
    """Class representing a ghost in the Pac-Man game."""
    def __init__(self, name, color, game):
        """
        Initialize a Ghost instance.

        :param name: Name of the ghost (e.g., 'Pinky', 'Blinky').
        :param color: Color tuple for the ghost.
        :param game: Reference to the PacManGame instance.
        """
        self.name = name
        self.color = color
        self.game = game
        self.position = self.get_random_initial_position()
        self.target = None
        self.path = []
        self.move_interval = 15  # Ghost moves every 15 frames
        self.move_counter = 0

    def get_random_initial_position(self):
        """
        Get a random starting position for the ghost that is not a wall,
        not overlapping with Pac-Man or other ghosts.

        :return: Tuple (row, col) representing the Ghost's starting position.
        """
        available_positions = [
            (row, col)
            for row in range(self.game.grid_size)
            for col in range(self.game.grid_size)
            if (row, col) not in self.game.walls
            and (row, col) != self.game.pacman_position
            and all(ghost.position != (row, col) for ghost in self.game.ghosts)
        ]
        if not available_positions:
            raise ValueError("No available positions to place the ghost without overlapping.")
        return random.choice(available_positions)

    def update_direction(self):
        """
        Update the ghost's path based on its target using BFS.
        """
        if self.name == 'Pinky':
            self.target = self.game.get_pinky_target()
        elif self.name == 'Blinky':
            self.target = self.game.pacman_position

        if self.target:
            self.path = self.game.bfs(self.position, self.target)

    def move(self):
        """
        Move the ghost along the path towards its target.
        """
        if not self.path or len(self.path) < 2:
            return  # No movement needed

        # Move to the next cell in the path
        self.position = self.path[1]
        self.path.pop(0)  # Remove the current position


    def update(self):
        self.move_counter += 1
        if self.move_counter >= self.move_interval:
            self.update_direction()
            if self.path and len(self.path) >= 2:
                self.move()
            self.move_counter = 0

class PacManGame:
    def __init__(self, grid_size=20, cell_size=30, wall_ratio=0.1):
        """
        Initialize the Pac-Man game logic.

        :param grid_size: Number of rows and columns in the grid.
        :param cell_size: Size of each cell in pixels.
        :param wall_ratio: Ratio of internal walls to total grid cells.
        """
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.wall_ratio = wall_ratio

        # Colors (keep as tuples, rendering handled in game_display.py)
        self.BLACK = (0, 0, 0)            # Black for background
        self.DEEP_BLUE = (0, 0, 139)      # Deep blue for walls
        self.YELLOW = (255, 255, 0)       # Yellow for beans and score
        self.RED = (255, 0, 0)            # Red for Game Over

        # Initialize the grid
        self.walls = self.create_outer_walls()
        self.add_internal_walls()
        self.initialize_beans()

        # Initialize score
        self.total_beans = len(self.beans)
        self.score = 0

        # Initialize Pac-Man's position
        self.pacman_position = self.get_random_start_position()

        # Remove bean from Pac-Man's starting position
        if self.pacman_position in self.beans:
            self.beans.remove(self.pacman_position)
            self.score += 1  # Increment score as Pac-Man starts on a bean

        # Initialize direction
        self.direction = 'RIGHT'  # Default direction

        # Initialize ghosts list
        self.ghosts = []
        self.add_ghosts()

        # Game state
        self.game_over = False

    def create_outer_walls(self):
        """
        Create outer walls around the grid.

        :return: Set containing positions of outer walls.
        """
        walls = set()
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if row == 0 or row == self.grid_size - 1 or col == 0 or col == self.grid_size - 1:
                    walls.add((row, col))
        return walls

    def add_internal_walls(self):
        """
        Add internal walls randomly to the grid based on the wall ratio.
        Ensures walls do not form closed loops using Union-Find for cycle detection.
        """
        total_cells = self.grid_size * self.grid_size
        num_internal_walls = int(total_cells * self.wall_ratio)

        # Initialize Union-Find structure
        uf = UnionFind()

        # Initialize parent pointers for Union-Find
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if (row, col) not in self.walls:
                    uf.parent[(row, col)] = (row, col)

        available_positions = [
            (row, col)
            for row in range(1, self.grid_size - 1)
            for col in range(1, self.grid_size - 1)
            if (row, col) not in self.walls
        ]

        random.shuffle(available_positions)  # Shuffle to ensure randomness

        internal_walls = set()
        for position in available_positions:
            if len(internal_walls) >= num_internal_walls:
                break

            row, col = position

            # Find adjacent wall positions
            neighbors = [
                (row - 1, col),
                (row + 1, col),
                (row, col - 1),
                (row, col + 1)
            ]

            # Collect existing internal wall neighbors
            existing_wall_neighbors = [n for n in neighbors if n in internal_walls]

            # If there are less than two wall neighbors, safe to add without forming a loop
            if len(existing_wall_neighbors) < 2:
                internal_walls.add(position)
                for neighbor in existing_wall_neighbors:
                    uf.union(position, neighbor)

        self.walls.update(internal_walls)

    def initialize_beans(self):
        """
        Initialize beans in all non-wall cells.
        Beans are represented as a set of (row, col) tuples.
        """
        self.beans = set(
            (row, col)
            for row in range(self.grid_size)
            for col in range(self.grid_size)
            if (row, col) not in self.walls
        )

    def get_beans(self):
        """
        Get the current set of bean positions.

        :return: Set of (row, col) tuples representing bean positions.
        """
        return self.beans.copy()

    def set_beans(self, new_beans):
        """
        Set the bean positions to a new set.

        :param new_beans: Iterable of (row, col) tuples representing new bean positions.
        """
        # Ensure new beans are not placed on walls
        self.beans = set(
            (row, col) for row, col in new_beans if (row, col) not in self.walls
        )
        # Update score based on beans eaten
        self.score = self.total_beans - len(self.beans)

    def get_score(self):
        """
        Get the current score.

        :return: Integer representing the current score.
        """
        return self.score

    def get_random_start_position(self):
        """
        Get a random starting position for Pac-Man that is not a wall.

        :return: Tuple (row, col) representing Pac-Man's starting position.
        """
        available_positions = [
            (row, col)
            for row in range(self.grid_size)
            for col in range(self.grid_size)
            if (row, col) not in self.walls
        ]
        return random.choice(list(available_positions))

    def add_ghosts(self):
        """
        Initialize and add Pinky and Blinky ghosts to the game.
        """
        # Create Pinky and Blinky instances
        pinky = Ghost(name='Pinky', color=(255, 105, 180), game=self)
        blinky = Ghost(name='Blinky', color=(255, 0, 0), game=self)

        self.ghosts.append(pinky)
        self.ghosts.append(blinky)

    def eat_bean(self, position):
        """
        Remove a bean from the specified position and update the score.

        :param position: Tuple (row, col) indicating the position of the bean to eat.
        """
        if position in self.beans:
            self.beans.remove(position)
            self.score += 1

    def check_eat_bean(self):
        """
        Check if Pac-Man is on a bean. If so, eat the bean and update the score.
        """
        if self.pacman_position in self.beans:
            self.eat_bean(self.pacman_position)
            if not self.beans:
                self.trigger_game_over()

    def trigger_game_over(self):
        """
        Trigger the game over state.
        """
        self.game_over = True

    def reset_game(self):
        """
        Reset the game to the initial state.
        """
        self.walls = self.create_outer_walls()
        self.add_internal_walls()
        self.initialize_beans()
        self.total_beans = len(self.beans)
        self.score = 0
        self.pacman_position = self.get_random_start_position()

        # Remove bean from Pac-Man's starting position
        if self.pacman_position in self.beans:
            self.beans.remove(self.pacman_position)
            self.score += 1  # Increment score as Pac-Man starts on a bean

        self.direction = 'RIGHT'  # Reset direction to default

        # Reset ghosts
        self.ghosts = []
        self.add_ghosts()

        self.game_over = False

    def get_direction_between(self, current, next_cell):
        """
        Determine the direction between two adjacent cells.

        :param current: Tuple (row, col) of the current cell.
        :param next_cell: Tuple (row, col) of the next cell.
        :return: Direction string ('UP', 'DOWN', 'LEFT', 'RIGHT').
        """
        row_diff = next_cell[0] - current[0]
        col_diff = next_cell[1] - current[1]

        if row_diff == -1 and col_diff == 0:
            return 'UP'
        elif row_diff == 1 and col_diff == 0:
            return 'DOWN'
        elif row_diff == 0 and col_diff == -1:
            return 'LEFT'
        elif row_diff == 0 and col_diff == 1:
            return 'RIGHT'
        else:
            return 'RIGHT'  # Default direction

    def bfs(self, start, goal, max_depth=1000):
        """
        Perform BFS to find the shortest path from start to goal.

        :param start: Tuple (row, col) starting position.
        :param goal: Tuple (row, col) goal position.
        :return: List of tuples representing the path from start to goal.
        """
        queue = deque()
        queue.append([start])
        visited = set()
        visited.add(start)
        depth = 0

        while queue and depth < max_depth:
            path = queue.popleft()
            current = path[-1]
            depth += 1

            if current == goal:
                return path

            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor not in visited and neighbor not in self.walls:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        return []  # No path found or max depth reached

    def get_neighbors(self, position):
        """
        Get all valid neighboring positions (up, down, left, right).

        :param position: Tuple (row, col) of the current position.
        :return: List of tuples representing valid neighbors.
        """
        row, col = position
        neighbors = [
            (row - 1, col),  # UP
            (row + 1, col),  # DOWN
            (row, col - 1),  # LEFT
            (row, col + 1)   # RIGHT
        ]
        # Filter neighbors within the grid boundaries
        valid_neighbors = [
            (r, c) for r, c in neighbors
            if 0 <= r < self.grid_size and 0 <= c < self.grid_size
        ]
        return valid_neighbors

    def get_pinky_target(self):
        """
        Calculate Pinky's target position: four cells ahead of Pac-Man's current direction.

        :return: Tuple (row, col) representing Pinky's target position.
        """
        row, col = self.pacman_position
        direction = self.direction
        target = (row, col)

        for _ in range(4):
            if direction == 'UP':
                next_cell = (target[0] - 1, target[1])
            elif direction == 'DOWN':
                next_cell = (target[0] + 1, target[1])
            elif direction == 'LEFT':
                next_cell = (target[0], target[1] - 1)
            elif direction == 'RIGHT':
                next_cell = (target[0], target[1] + 1)
            else:
                next_cell = target  # Default to current position

            # Check if next_cell is a wall or out of bounds
            if (0 <= next_cell[0] < self.grid_size and
                0 <= next_cell[1] < self.grid_size and
                next_cell not in self.walls):
                target = next_cell
            else:
                break  # Stop if next cell is a wall or out of bounds

        return target

    def move_pacman(self, direction):
        """
        Move Pac-Man in the specified direction if possible and update direction.

        :param direction: String indicating the direction ('UP', 'DOWN', 'LEFT', 'RIGHT').
        """
        if self.game_over:
            return  # Prevent movement when game is over

        row, col = self.pacman_position
        if direction == 'UP':
            new_row, new_col = row - 1, col
        elif direction == 'DOWN':
            new_row, new_col = row + 1, col
        elif direction == 'LEFT':
            new_row, new_col = row, col - 1
        elif direction == 'RIGHT':
            new_row, new_col = row, col + 1
        else:
            return  # Invalid direction

        # Check for wall collision
        if (new_row, new_col) not in self.walls:
            self.pacman_position = (new_row, new_col)
            self.set_direction(direction)  # Update direction after successful move
            self.check_eat_bean()

    def set_direction(self, new_direction):
        """
        Set the direction of Pac-Man.

        :param new_direction: String indicating the new direction ('UP', 'DOWN', 'LEFT', 'RIGHT').
        """
        if new_direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            self.direction = new_direction
        else:
            print(f"Invalid direction: {new_direction}. Direction not changed.")

    def save_to_json(self, folder_name, file_name):
        """
        Save the current game state to a JSON file.

        :param folder_name: Name of the folder where the file will be stored.
        :param file_name: Name of the JSON file (e.g., 'save_1.json').
        """
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Prepare the game state dictionary
        game_state = {
            "grid_size": self.grid_size,
            "cell_size": self.cell_size,
            "wall_ratio": self.wall_ratio,
            "walls": list(self.walls),  # converting set to list for JSON serialization
            "pacman_position": self.pacman_position,
            "direction": self.direction,
            "beans": list(self.beans),   # converting set to list
            "ghosts": [
                {
                    "name": ghost.name,
                    "position": ghost.position,
                    "color": ghost.color
                }
                for ghost in self.ghosts
            ],
            "score": self.score,
            "game_over": self.game_over
        }

        # Construct the file path
        file_path = os.path.join(folder_name, file_name)

        # Write the game state to a JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(game_state, f, ensure_ascii=False, indent=4)

        # Print a confirmation message
        print(f"Game state has been saved to: {file_path}")
