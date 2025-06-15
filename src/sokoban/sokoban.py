import random
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Set
from copy import deepcopy
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple
from collections import deque
import os

@dataclass
class Move:
    def __init__(self, is_push: bool, start_pos: tuple, end_pos: tuple, box_start=None, box_end=None):
        self.is_push = is_push
        self.start_pos = tuple(start_pos) if isinstance(start_pos, (list, tuple)) else start_pos
        self.end_pos = tuple(end_pos) if isinstance(end_pos, (list, tuple)) else end_pos
        self.box_start = tuple(box_start) if isinstance(box_start, (list, tuple)) and box_start is not None else box_start
        self.box_end = tuple(box_end) if isinstance(box_end, (list, tuple)) and box_end is not None else box_end

class Solution:
    def __init__(self):
        self.steps = []
        self.min_moves = float('inf')
        
    def can_reach(self, grid: List[List[str]], start: Tuple[int, int], 
                  target: Tuple[int, int], box_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Check if player can reach the target position and return the path."""
        if start == target:
            return [start]
            
        rows, cols = len(grid), len(grid[0])
        queue = deque([(start, [start])])
        visited = {start}
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        while queue:
            curr_pos, path = queue.popleft()
            
            for dx, dy in directions:
                next_x, next_y = curr_pos[0] + dx, curr_pos[1] + dy
                next_pos = (next_x, next_y)
                
                if (0 <= next_x < rows and 0 <= next_y < cols and
                    grid[next_x][next_y] != '#' and
                    next_pos not in visited and
                    next_pos != box_pos):
                    
                    if next_pos == target:
                        return path + [next_pos]
                        
                    queue.append((next_pos, path + [next_pos]))
                    visited.add(next_pos)
                    
        return []

    def minPushBox(self, grid: List[List[str]]) -> Tuple[int, int]:
        rows, cols = len(grid), len(grid[0])
        
        # Find initial positions
        box_pos = player_pos = target = None
        for i in range(rows):
            for j in range(cols):
                if grid[i][j] == 'B':
                    box_pos = (i, j)
                elif grid[i][j] == 'S':
                    player_pos = (i, j)
                elif grid[i][j] == 'T':
                    target = (i, j)
                    
        if not all((box_pos, player_pos, target)):
            return -1, -1

        # Define directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        # Queue format: (box_pos, player_pos, pushes, total_moves, moves_list)
        queue = deque([(box_pos, player_pos, 0, 0, [])])
        # Track visited states: (box_pos, player_pos)
        visited = {(box_pos, player_pos)}
        
        while queue:
            box_pos, player_pos, pushes, total_moves, moves = queue.popleft()
            
            if box_pos == target:
                self.steps = moves
                return total_moves, pushes
                
            for i, (dx, dy) in enumerate(directions):
                new_box_x, new_box_y = box_pos[0] + dx, box_pos[1] + dy
                new_box_pos = (new_box_x, new_box_y)
                
                # Check if new box position is valid
                if not (0 <= new_box_x < rows and 0 <= new_box_y < cols) or grid[new_box_x][new_box_y] == '#':
                    continue
                    
                # Calculate required player position to push the box
                push_pos = (box_pos[0] - dx, box_pos[1] - dy)
                
                # Check if push position is valid
                if not (0 <= push_pos[0] < rows and 0 <= push_pos[1] < cols) or grid[push_pos[0]][push_pos[1]] == '#':
                    continue
                    
                # Check if player can reach the position to push the box
                player_path = self.can_reach(grid, player_pos, push_pos, box_pos)
                
                if player_path:
                    next_state = (new_box_pos, box_pos)
                    if next_state not in visited:
                        visited.add(next_state)
                        
                        # Create moves for player walking
                        new_moves = []
                        curr_pos = player_pos
                        for next_pos in player_path[1:]:  # Skip start position
                            new_moves.append(Move(False, curr_pos, next_pos))
                            curr_pos = next_pos
                            
                        # Add the push move
                        new_moves.append(Move(True, push_pos, box_pos, 
                                           box_start=box_pos, 
                                           box_end=new_box_pos))
                        
                        queue.append((new_box_pos, box_pos, 
                                    pushes + 1,
                                    total_moves + len(new_moves),
                                    moves + new_moves))
                        
        return -1, -1

    def get_solution_path(self) -> List[Move]:
        """Returns the list of moves that solve the puzzle"""
        return self.steps if self.steps else []
class SokobanBoard:
    def __init__(self, grid, player_x, player_y):
        self.grid = grid
        self.player_x = player_x
        self.player_y = player_y
        self.directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Up, Right, Down, Left
        self.colors = ['white', 'gray', 'green', 'red', 'red', 'blue', 'cyan']
        self.question_types = ['next_position', 'box_position', 'steps_to_target', 
                             'state_info_player', 'state_info_object', 'state_info_distance',
                             'state_info_trapped', 'transition_path']
    
    
    
    
    def _generate_player_position_question(self, num_options: int) -> Tuple[str, str, List[str], int]:
        """Generate question about player's current position."""
        player_pos = (self.player_y, self.player_x)  # Convert to (row, col) format
        
        # Generate other positions as options
        options = [player_pos]
        while len(options) < num_options:
            pos = (random.randint(0, self.grid.shape[0]-1), 
                  random.randint(0, self.grid.shape[1]-1))
            if pos not in options and self.grid[pos[0], pos[1]] != 1:  # Not a wall
                options.append(pos)
                
        random.shuffle(options)
        correct_idx = options.index(player_pos)
        
        question = "What is the current position of the player (row, column)?"
        analysis = f"The player is currently at position ({player_pos[0]}, {player_pos[1]})."
        player_pos = (self.player_y, self.player_x)
        
        # Generate initial state description
        initial_state = (
            "- Player position: ({}, {})\n".format(player_pos[0], player_pos[1]) +
            "- Boxes positions: {}\n".format(
                ", ".join(f"({y}, {x})" for x, y in self.get_box_positions())) +
            "- Target positions: {}\n".format(
                ", ".join(f"({y}, {x})" for x, y in self.get_target_positions()))
        )
        formatted_question, formatted_analysis = format_question_and_analysis2(
        question, options, analysis, correct_idx,initial_state)
        return formatted_question, formatted_analysis, [f"({pos[0]}, {pos[1]})" for pos in options], correct_idx
    def _generate_manhattan_distance_question(self, num_options: int) -> Tuple[str, str, List[str], int]:
        """Generate question about Manhattan distance between box and target."""
        # Find box and target positions
        box_pos = None
        target_pos = None
        
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                if self.grid[y, x] in [2, 4]:  # Box
                    box_pos = (y, x)
                if self.grid[y, x] in [3, 4, 6]:  # Target
                    target_pos = (y, x)
                    
        if not box_pos or not target_pos:
            return "Invalid state", "No box or target found", ["Invalid"], 0
            
        # Calculate Manhattan distance
        distance = abs(box_pos[0] - target_pos[0]) + abs(box_pos[1] - target_pos[1])
        
        # Generate options
        options = [distance]
        while len(options) < num_options:
            new_dist = random.randint(1, self.grid.shape[0] + self.grid.shape[1])
            if new_dist not in options:
                options.append(new_dist)
                
        random.shuffle(options)
        correct_idx = options.index(distance)
        
        question = "What is the Manhattan distance between the box and the target?"
        analysis = (f"Box position: ({box_pos[0]}, {box_pos[1]})\n"
                   f"Target position: ({target_pos[0]}, {target_pos[1]})\n"
                   f"Manhattan distance = |{box_pos[0]} - {target_pos[0]}| + |{box_pos[1]} - {target_pos[1]}| = {distance}")
        player_pos = (self.player_y, self.player_x)
        
        # Generate initial state description
        initial_state = (
            "- Player position: ({}, {})\n".format(player_pos[0], player_pos[1]) +
            "- Boxes positions: {}\n".format(
                ", ".join(f"({y}, {x})" for x, y in self.get_box_positions())) +
            "- Target positions: {}\n".format(
                ", ".join(f"({y}, {x})" for x, y in self.get_target_positions()))
        )
        formatted_question, formatted_analysis = format_question_and_analysis(
        question, options, analysis, correct_idx,initial_state)
        return formatted_question, formatted_analysis, [str(d) for d in options], correct_idx


    def _generate_transition_path_question(self, num_options: int) -> Tuple[str, str, List[str], int]:
        """Generate question about moving from point A to point B."""
        # Get all valid floor positions
        floor_positions = []
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                if self.grid[y, x] in [0, 3]:  # Empty space or target
                    floor_positions.append((x, y))
                    
        if not floor_positions:
            return "Invalid state", "No valid positions found", ["Invalid"], 0
            
        # Current position is start (A)
        start_pos = (self.player_x, self.player_y)
        
        # Try to find a valid end position (B)
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            # Randomly select end position from floor positions
            end_pos = random.choice(floor_positions)
            if end_pos != start_pos:
                # Check if path exists
                path = self._find_path(start_pos, end_pos)
                if path:
                    # Convert path to moves
                    moves = self._path_to_moves(path)
                    if moves:
                        # Generate alternative paths
                        options = self._generate_alternative_paths(moves, num_options)
                        if options:
                            correct_sequence = moves
                            random.shuffle(options)
                            correct_idx = options.index(correct_sequence)
                            
                            question = f"Treat the boxes as walls,What is the shortest sequence of moves for human to move himself from position ({start_pos[1]}, {start_pos[0]}) to position ({end_pos[1]}, {end_pos[0]})?\n"
                                    
                            
                            analysis = (f"Start position: ({start_pos[1]}, {start_pos[0]})\n"
                                    f"End position: ({end_pos[1]}, {end_pos[0]})\n"
                                    f"Optimal move sequence: {correct_sequence}")
                            player_pos = (self.player_y, self.player_x)
        
                            # Generate initial state description
                            initial_state = (
                                "- Player position: ({}, {})\n".format(player_pos[0], player_pos[1]) +
                                "- Boxes positions: {}\n".format(
                                    ", ".join(f"({y}, {x})" for x, y in self.get_box_positions())) +
                                "- Target positions: {}\n".format(
                                    ", ".join(f"({y}, {x})" for x, y in self.get_target_positions()))
                            )
                            formatted_question, formatted_analysis = format_question_and_analysis(
                            question, options, analysis, correct_idx,initial_state)
                            return formatted_question, formatted_analysis, options, correct_idx
                            
            attempts += 1
            
        return "No valid path", "Could not find valid path after maximum attempts", ["No solution"], 0

    def _find_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find path between two points using BFS."""
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current, path = queue.popleft()
            if current == end:
                return path
                
            for dx, dy in self.directions:
                next_x, next_y = current[0] + dx, current[1] + dy
                next_pos = (next_x, next_y)
                
                if (0 <= next_x < self.grid.shape[1] and 
                    0 <= next_y < self.grid.shape[0] and 
                    self.grid[next_y, next_x] not in [1, 2, 4] and 
                    next_pos not in visited):
                    queue.append((next_pos, path + [next_pos]))
                    visited.add(next_pos)
                    
        return None

    def _path_to_moves(self, path: List[Tuple[int, int]]) -> str:
        """Convert path to move sequence."""
        if len(path) < 2:
            return ""
            
        moves = []
        direction_map = {
            (0, -1): "Up",
            (1, 0): "Right",
            (0, 1): "Down",
            (-1, 0): "Left"
        }
        
        for i in range(len(path) - 1):
            dx = path[i+1][0] - path[i][0]
            dy = path[i+1][1] - path[i][1]
            moves.append(direction_map.get((dx, dy), ""))
            
        return " → ".join(moves)

    def _generate_alternative_paths(self, correct_moves: str, num_options: int) -> List[str]:
        """Generate alternative paths by modifying the correct sequence."""
        moves_list = correct_moves.split(" → ")
        
        # Define direction_deltas at the beginning of the function
        direction_deltas = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }
        
        # Function to check if path reaches the same end point
        def get_end_position(moves, start_pos):
            current_pos = list(start_pos)
            for move in moves:
                dx, dy = direction_deltas[move]
                current_pos[0] += dx
                current_pos[1] += dy
            return tuple(current_pos)
        
        # Function to validate a path
        def is_valid_path(path, start_pos):
            current_pos = list(start_pos)
            for move in path:
                if move not in direction_deltas:  # 使用direction_deltas来检查有效移动
                    return False
                dx, dy = direction_deltas[move]
                new_x = current_pos[0] + dx
                new_y = current_pos[1] + dy
                # Check if new position is valid (not wall and within bounds)
                if (new_x < 0 or new_y < 0 or 
                    new_x >= self.grid.shape[1] or 
                    new_y >= self.grid.shape[0] or
                    self.grid[new_y, new_x] == 1):  # Wall check
                    return False
                current_pos = [new_x, new_y]
            return True

        # Get the correct end position
        start_pos = (self.player_x, self.player_y)
        correct_end_pos = get_end_position(moves_list, start_pos)
        
        # Store all valid paths and their end positions
        valid_paths = {correct_moves}
        attempts = 0
        max_attempts = 100
        
        while len(valid_paths) < num_options and attempts < max_attempts:
            # Create a variation of the path that is guaranteed to be different
            variation = []
            current_length = len(moves_list)
            
            # Randomly choose one of these modification strategies
            modification = random.choice([
                'different_length',  # Make path longer or shorter
                'different_order',   # Change order of moves
                'different_direction' # Use different directions
            ])
            
            if modification == 'different_length':
                # Add or remove 1-2 moves
                target_length = current_length + random.choice([-1, 1, 2])
                if target_length > 0:
                    variation = [random.choice(list(direction_deltas.keys())) 
                            for _ in range(target_length)]
                    
            elif modification == 'different_order':
                # Take original moves but shuffle some of them
                variation = moves_list.copy()
                if len(variation) >= 2:
                    idx1, idx2 = random.sample(range(len(variation)), 2)
                    variation[idx1], variation[idx2] = variation[idx2], variation[idx1]
                    
            else:  # different_direction
                # Replace some moves with different directions
                variation = moves_list.copy()
                for i in range(len(variation)):
                    if random.random() < 0.3:  # 30% chance to change each move
                        other_directions = [d for d in direction_deltas.keys() 
                                        if d != variation[i]]
                        variation[i] = random.choice(other_directions)
            
            # Validate the new path
            if variation:
                new_path = " → ".join(variation)
                if (new_path not in valid_paths and
                    is_valid_path(variation, start_pos) and
                    get_end_position(variation, start_pos) != correct_end_pos):
                    valid_paths.add(new_path)
            
            attempts += 1
        
        # If we couldn't generate enough valid paths, add some clearly wrong ones
        while len(valid_paths) < num_options:
            wrong_path = [random.choice(list(direction_deltas.keys())) 
                        for _ in range(random.randint(1, len(moves_list) + 2))]
            new_path = " → ".join(wrong_path)
            if new_path not in valid_paths:
                valid_paths.add(new_path)
        
        return list(valid_paths)
    def is_solvable(self) -> bool:
        """Check if the current board configuration is solvable."""
        grid_chars = []
        for y in range(self.grid.shape[0]):
            row = []
            for x in range(self.grid.shape[1]):
                cell = self.grid[y, x]
                if cell == 1:
                    row.append('#')
                elif cell in [5, 6]:
                    row.append('S')
                elif cell in [2, 4]:
                    row.append('B')
                elif cell == 3:
                    row.append('T')
                else:
                    row.append('.')
            grid_chars.append(row)
        
        solution = Solution()
        total_moves, _ = solution.minPushBox(grid_chars)
        return total_moves != -1

    def _generate_steps_question(self, num_moves: int, num_options: int) -> Tuple[str, str, List[str], int]:
        """Generate question about minimum moves needed."""
        try:
            player_pos, boxes, targets = self.get_board_elements()
            if not boxes or not targets:
                return "Invalid board state", "No boxes or targets found", ["Invalid"], 0
            # Ensure positions are tuples
            player_pos = tuple(player_pos) if isinstance(player_pos, list) else player_pos
            if boxes and isinstance(boxes[0], list):
                boxes = [tuple(pos) for pos in boxes]
            if targets and isinstance(targets[0], list):
                targets = [tuple(pos) for pos in targets]
        except Exception as e:
            print(f"Error getting board elements: {e}")
            return "Invalid board state", "Error processing board elements", ["Invalid"], 0
        
        # Convert grid to format expected by minPushBox
        grid_chars = []
        for y in range(self.grid.shape[0]):
            row = []
            for x in range(self.grid.shape[1]):
                cell = self.grid[y, x]
                if cell == 1:
                    row.append('#')
                elif cell in [5, 6]:
                    row.append('S')
                elif cell in [2, 4]:
                    row.append('B')
                elif cell in [3, 4, 6]:
                    row.append('T')
                else:
                    row.append('.')
            grid_chars.append(row)
        
        solution = Solution()
        total_moves, _ = solution.minPushBox(grid_chars)
        
        if total_moves == -1:
            return "How many moves are needed?", "Puzzle is unsolvable", ["Unsolvable"], 0
        
        solution_path = solution.get_solution_path()
        
        # Generate detailed analysis
        
        analysis = f"Solution analysis:"
        analysis += f"Step by step solution:\n"
        current_pos = [player_pos[1], player_pos[0]]  
        player_moves = 0
    #加注释  
        for move in solution_path:
            player_moves += 1
            if move.is_push and isinstance(move.end_pos, (list, tuple)) and isinstance(current_pos, (list, tuple)):
                if isinstance(move.box_start, (list, tuple)) and isinstance(move.box_end, (list, tuple)):
                    analysis += (f"Player moves from ({current_pos[0]}, {current_pos[1]}) to "
                              f"( {move.end_pos[0]},{move.end_pos[1]}) "
                              f"(box moves from ({move.box_start[0]}, {move.box_start[1]}) "
                              f"to ({move.box_end[0]}, {move.box_end[1]}))\n")
                else:
                    # Handle case where box positions are not properly set
                    analysis += (f"Player moves from ({current_pos[0]}, {current_pos[1]}) to "
                              f"({move.end_pos[0]}, {move.end_pos[1]})\n")
            else:
                if isinstance(move.end_pos, (list, tuple)) and isinstance(current_pos, (list, tuple)):
                    analysis += (f"Player moves from ({current_pos[0]}, {current_pos[1]}) to "
                              f"({move.end_pos[0]}, {move.end_pos[1]})\n")
                else:
                    print(f"Warning: Invalid position format - current_pos: {current_pos}, end_pos: {move.end_pos}")
            current_pos = move.end_pos
        
        analysis += f"\nTotal player moves: {player_moves}"
        
        # Generate options with safety limit
        options = [player_moves]
        attempts = 0
        max_attempts = 100
        
        while len(options) < num_options and attempts < max_attempts:
            new_move = max(1, player_moves + random.randint(-3, 3))
            if new_move > 0 and new_move not in options:
                options.append(new_move)
            attempts += 1
        
        while len(options) < num_options:
            new_move = max(1, player_moves + len(options))
            if new_move not in options:
                options.append(new_move)
        
        random.shuffle(options)
        options_str = [str(moves) for moves in options]
        options_display = ", ".join(f"[{i+1}] {opt}" for i, opt in enumerate(options_str))
        
        question = (f"What is the minimum number of moves needed to solve this puzzle?\n"
                   )
        correct_idx = options.index(player_moves)
        player_pos = (self.player_y, self.player_x)
        
        # Generate initial state description
        initial_state = (
            "- Player position: ({}, {})\n".format(player_pos[0], player_pos[1]) +
            "- Boxes positions: {}\n".format(
                ", ".join(f"({y}, {x})" for x, y in self.get_box_positions())) +
            "- Target positions: {}\n".format(
                ", ".join(f"({y}, {x})" for x, y in self.get_target_positions()))
        )
        formatted_question, formatted_analysis = format_question_and_analysis(
        question, options, analysis, correct_idx,initial_state)
        return formatted_question, formatted_analysis, [str(moves) for moves in options], correct_idx

    
    def _generate_position_question(self, num_moves: int, num_options: int) -> Tuple[str, str, List[str], int]:
        """Generate question about player's final position after moves."""
        moves = [random.randint(0, 3) for _ in range(num_moves)]
        saved_state = self.save_state()
        positions = [(self.player_x, self.player_y)]
        move_names = ['Up', 'Right', 'Down', 'Left']
        moves_str = []
        move_results = []
        
        # Record initial position
        current_pos = (self.player_x, self.player_y)
        move_results.append(f"Initial position: ({current_pos[1]}, {current_pos[0]})")
        
        for i, move in enumerate(moves, 1):
            success, msg = self.make_move(move)
            if success:
                new_pos = (self.player_x, self.player_y)
                positions.append(new_pos)
                moves_str.append(move_names[move])
                move_results.append(
                    f"Move {i} - {move_names[move]}: Player moves from ({current_pos[1]}, {current_pos[0]}) "
                    f"to ({new_pos[1]}, {new_pos[0]})"
                )
                current_pos = new_pos
            else:
                move_results.append(
                    f"Move {i} - {move_names[move]}: Failed - {msg} "
                    f"(Player stays at ({current_pos[1]}, {current_pos[0]}))"
                )
                moves_str.append(move_names[move])
        
        if not positions[1:]:  # If no valid moves were made
            self.load_state(saved_state)
            return self._generate_position_question(num_moves - 1, num_options)
            
        final_pos = positions[-1]
        moves_description = ' → '.join(moves_str)
        
        # Generate detailed analysis
        analysis = "Move sequence analysis:\n"
        analysis += "\n".join(move_results)
        analysis += f"\n\nFinal position: ({final_pos[1]}, {final_pos[0]})"
        
        # Generate options including the correct position
        options = [final_pos]
        while len(options) < num_options:
            pos = (random.randint(0, self.grid.shape[1]-1), 
                random.randint(0, self.grid.shape[0]-1))
            if pos not in options and self.grid[pos[1], pos[0]] != 1:  # Not a wall
                options.append(pos)
                
        self.load_state(saved_state)
        random.shuffle(options)
        correct_idx = options.index(final_pos)
        
        question = f"If the player makes these moves: {moves_description}, where will player end up?\n"
        
        player_pos = (self.player_y, self.player_x)
        
        # Generate initial state description
        initial_state = (
            "- Player position: ({}, {})\n".format(player_pos[0], player_pos[1]) +
            "- Boxes positions: {}\n".format(
                ", ".join(f"({y}, {x})" for x, y in self.get_box_positions())) +
            "- Target positions: {}\n".format(
                ", ".join(f"({y}, {x})" for x, y in self.get_target_positions()))
        )
        
        formatted_question, formatted_analysis = format_question_and_analysis(
            question, options, analysis, correct_idx, initial_state)
        
        return formatted_question, formatted_analysis, [f"({p[1]}, {p[0]})" for p in options], correct_idx
    def _generate_box_question(self, num_moves: int, num_options: int) -> Tuple[str, str, List[str], int]:
        box_positions = [(x, y) for y in range(self.grid.shape[0]) 
                    for x in range(self.grid.shape[1]) 
                    if self.grid[y, x] in [2, 4]]
        if not box_positions:
            return self._generate_position_question(num_moves, num_options)
        initial_box = box_positions[0]
        moves = [random.randint(0, 3) for _ in range(num_moves)]
        saved_state = self.save_state()
        move_names = ['up', 'right', 'down', 'left']
        moves_str = []
        move_results = []
        current_box = initial_box
        for move in moves:
            dx, dy = self.directions[move]
            next_x, next_y = current_box[0] + dx, current_box[1] + dy
            if (0 <= next_x < self.grid.shape[1] and 
                0 <= next_y < self.grid.shape[0] and 
                self.grid[next_y, next_x] != 1):
                moves_str.append(move_names[move])
                move_results.append(f"Move {move_names[move]}: Box moved from ({current_box[1]}, {current_box[0]}) to ({next_y}, {next_x})")
                current_box = (next_x, next_y)
            else:
                move_results.append(f"Move {move_names[move]}: Cannot move - blocked")
                moves_str.append(move_names[move])
        final_box = current_box
        analysis = "Move sequence:\n" + "\n".join(move_results) + \
              f"\nBox moves from ({initial_box[1]}, {initial_box[0]}) to ({final_box[1]}, {final_box[0]})"

        options = [(final_box[0], final_box[1])]
        valid_positions = [(x, y) for x in range(1, self.grid.shape[1]-1) 
                      for y in range(1, self.grid.shape[0]-1) 
                      if self.grid[y, x] != 1 and (x,y) != final_box]
    
        options.extend(random.sample(valid_positions, min(num_options-1, len(valid_positions))))
        while len(options) < num_options:
            options.append((1, 1))

        random.shuffle(options)
        correct_idx = options.index((final_box[0], final_box[1]))
        options_str = [f"({p[1]}, {p[0]})" for p in options]
        options_display = ", ".join(f"[{i+1}] {opt}" for i, opt in enumerate(options_str))

        question = (
                   f"Treat boxes as objects that can move by themselves, and treat people as floor (movable areas),After the moves {', '.join(moves_str)}, where will the box that started at "
                   f"position ({initial_box[1]}, {initial_box[0]}) end up?\n"
                   )
        player_pos = (self.player_y, self.player_x)
        
        # Generate initial state description
        initial_state = (
            "- Player position: ({}, {})\n".format(player_pos[0], player_pos[1]) +
            "- Boxes positions: {}\n".format(
                ", ".join(f"({y}, {x})" for x, y in self.get_box_positions())) +
            "- Target positions: {}\n".format(
                ", ".join(f"({y}, {x})" for x, y in self.get_target_positions()))
        )
        formatted_question, formatted_analysis = format_question_and_analysis(
        question, options, analysis, correct_idx,initial_state)
        return formatted_question, formatted_analysis, [f"({p[1]}, {p[0]})" for p in options], correct_idx

    def get_board_elements(self):
        """Get coordinates of board elements."""
        boxes = []
        targets = []
        player = None
        
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                cell = self.grid[y, x]
                if cell in [2, 4]:  # Box or box on target
                    boxes.append((x, y))
                if cell in [3, 4, 6]:  # Target or box/player on target
                    targets.append((x, y))
                if cell in [5, 6]:  # Player or player on target
                    player = (x, y)
        
        return player, boxes, targets

    def is_valid_move(self, dx: int, dy: int) -> Tuple[bool, str]:
        """Check if a move is valid."""
        new_x = self.player_x + dx
        new_y = self.player_y + dy

        if new_x < 0 or new_y < 0 or new_y >= self.grid.shape[0] or new_x >= self.grid.shape[1]:
            return False, "Out of bounds"
            
        if self.grid[new_y, new_x] == 1:
            return False, "Wall in the way"
            
        if self.grid[new_y, new_x] in [2, 4]:
            box_x = new_x + dx
            box_y = new_y + dy
            if (box_x < 0 or box_y < 0 or 
                box_y >= self.grid.shape[0] or 
                box_x >= self.grid.shape[1] or
                self.grid[box_y, box_x] in [1, 2, 4]):
                return False, "Cannot push box"
                
        return True, "Move valid"

    def make_move(self, direction: int) -> Tuple[bool, str]:
        """Make a move in the given direction if valid."""
        dx, dy = self.directions[direction]
        is_valid, msg = self.is_valid_move(dx, dy)
        
        if not is_valid:
            return False, msg
            
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        # Handle box pushing
        if self.grid[new_y, new_x] in [2, 4]:
            box_x = new_x + dx
            box_y = new_y + dy
            
            # Move box
            if self.grid[box_y, box_x] == 3:  # Box moves onto target
                self.grid[box_y, box_x] = 4
            else:  # Box moves to empty space
                self.grid[box_y, box_x] = 2
                
            # Update old box position
            if self.grid[new_y, new_x] == 4:  # Box was on target
                self.grid[new_y, new_x] = 3
            else:
                self.grid[new_y, new_x] = 0
        
        # Move player
        if self.grid[self.player_y, self.player_x] == 6:  # Player was on target
            self.grid[self.player_y, self.player_x] = 3
        else:
            self.grid[self.player_y, self.player_x] = 0
            
        if self.grid[new_y, new_x] == 3:  # Player moves to target
            self.grid[new_y, new_x] = 6
        else:
            self.grid[new_y, new_x] = 5
            
        self.player_x = new_x
        self.player_y = new_y
        return True, "Move successful"

    def save_state(self) -> Dict:
        """Save the current state of the board."""
        return {
            'grid': self.grid.copy(),
            'player_x': self.player_x,
            'player_y': self.player_y
        }

    def load_state(self, state: Dict):
        """Load a saved state of the board."""
        self.grid = state['grid'].copy()
        self.player_x = state['player_x']
        self.player_y = state['player_y']

    def save_board(self, path: str):
        """Generate a picture of the board and save it."""
        # Calculate figure size to achieve 640x480 resolution
        dpi = 80  # Standard screen DPI
        width_inches = 640 / dpi
        height_inches = 480 / dpi
        
        # Create figure with specified size
        fig, ax = plt.subplots(figsize=(width_inches, height_inches))

        # Create background
        ax.add_patch(plt.Rectangle((0, 0), self.grid.shape[1], self.grid.shape[0], 
                            facecolor='#DEB887'))  # 木纹色背景

        # Draw each cell
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                cell = self.grid[y, x]
            
                if cell == 1:  # Wall - 砖墙纹理
                    # 绘制砖墙图案
                    brick_color = '#CD853F'  # 砖红色
                    ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor=brick_color))
                
                    # 添加砖块纹理
                    for bx in range(2):
                        for by in range(2):
                            ax.add_patch(plt.Rectangle(
                            (x + bx*0.5, y + by*0.5), 0.48, 0.48,
                            facecolor=brick_color, edgecolor='white', linewidth=1
                        ))
                        
                elif cell == 2 or cell == 4:  # Box - 木箱
                    # 绘制木箱底色
                    box_color = '#8B4513'
                    ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor=box_color))
                
                    # 添加木箱边框
                    ax.add_patch(plt.Rectangle((x+0.1, y+0.1), 0.8, 0.8, 
                                        facecolor='none', edgecolor='#8B4513', linewidth=2))
                
                    # 添加斜线纹理
                    ax.plot([x+0.1, x+0.9], [y+0.1, y+0.9], 'k-', linewidth=1)
                    ax.plot([x+0.1, x+0.9], [y+0.9, y+0.1], 'k-', linewidth=1)
                
                    # 添加中间的X
                    ax.plot([x+0.35, x+0.65], [y+0.5, y+0.5], 'k-', linewidth=2)
                    ax.plot([x+0.5, x+0.5], [y+0.35, y+0.65], 'k-', linewidth=2)
                
                elif cell == 3 or cell == 6:  # Target - 绿色X
                    if cell != 6:  # 如果不是玩家占据的目标点
                        # 绘制绿色X标记
                        ax.plot([x+0.2, x+0.8], [y+0.2, y+0.8], 'g-', linewidth=3)
                        ax.plot([x+0.2, x+0.8], [y+0.8, y+0.2], 'g-', linewidth=3)
                
                if cell in [5, 6]:  # Player - 简化的人物图标
                    # 绘制圆形头部
                    circle = plt.Circle((x+0.5, y+0.3), 0.15, color='black')
                    ax.add_artist(circle)
                    # 绘制身体
                    ax.plot([x+0.5, x+0.5], [y+0.45, y+0.7], 'k-', linewidth=3)
                    # 绘制手臂
                    ax.plot([x+0.3, x+0.7], [y+0.5, y+0.5], 'k-', linewidth=3)
                    # 绘制腿
                    ax.plot([x+0.5, x+0.3], [y+0.7, y+0.8], 'k-', linewidth=3)
                    ax.plot([x+0.5, x+0.7], [y+0.7, y+0.8], 'k-', linewidth=3)

        # Set display properties 
        ax.grid(True, linestyle='-', color='black', linewidth=0.5)
        ax.set_xlim(0, self.grid.shape[1])
        ax.set_ylim(0, self.grid.shape[0])

        # Set tick positions
        ax.set_xticks([x + 0.5 for x in range(self.grid.shape[1])])
        ax.set_yticks([y + 0.5 for y in range(self.grid.shape[0])])

        # Adjust tick labels with larger font size
        ax.set_xticklabels(range(self.grid.shape[1]), fontsize=16)
        ax.set_yticklabels(range(self.grid.shape[0]), fontsize=16)
        
        # Move x-axis ticks to the top
        ax.xaxis.tick_top()

        # Set aspect ratio and invert y-axis
        ax.set_aspect('equal')
        plt.gca().invert_yaxis()

        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Add padding
        plt.tight_layout(pad=1.0)

        # Save with specific resolution
        plt.savefig(path, dpi=dpi, bbox_inches='tight')
        plt.close()

    def get_full_state(self) -> dict:
        """Return full information about board state."""
        box_positions = [(x, y) for y in range(self.grid.shape[0]) 
                        for x in range(self.grid.shape[1]) 
                        if self.grid[y, x] in [2, 4]]
        
        target_positions = [(x, y) for y in range(self.grid.shape[0]) 
                           for x in range(self.grid.shape[1]) 
                           if self.grid[y, x] in [3, 4, 6]]

        return {
            "grid": self.grid.tolist(),
            "grid_size": {
                "width": self.grid.shape[1],
                "height": self.grid.shape[0]
            },
            "player": {
                "x": self.player_x,
                "y": self.player_y
            },
            "boxes": [{"x": x, "y": y} for x, y in box_positions],
            "targets": [{"x": x, "y": y} for x, y in target_positions],
            "symbols": {
                "empty": 0,
                "wall": 1,
                "box": 2,
                "target": 3,
                "box_on_target": 4,
                "player": 5,
                "player_on_target": 6
            }
        }
    def generate_question(self, num_moves: int, num_options: int) -> Tuple[str, str, List[str], int]:
        """Generate a Sokoban puzzle question."""
        question_type = self.question_types[0]  # Use first type
        
        if question_type.startswith('state_info_'):
            if question_type == 'state_info_player':
                return self._generate_player_position_question(num_options)
            elif question_type == 'state_info_object':
                return self._generate_object_position_question(num_options)
            elif question_type == 'state_info_distance':
                return self._generate_manhattan_distance_question(num_options)
            elif question_type == 'state_info_trapped':
                return self._generate_box_trapped_question(num_options)
        elif question_type == 'transition_path':
            return self._generate_transition_path_question(num_options)
        elif question_type == 'next_position':
            return self._generate_position_question(num_moves, num_options)
        elif question_type == 'box_position':
            return self._generate_box_question(num_moves, num_options)
        else:
            return self._generate_steps_question(num_moves, num_options)

    def get_box_positions(self) -> List[Tuple[int, int]]:
        """Get all box positions on the board."""
        positions = []
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                if self.grid[y, x] in [2, 4]:  # Box or box on target
                    positions.append((x, y))
        return positions

    def get_target_positions(self) -> List[Tuple[int, int]]:
        """Get all target positions on the board."""
        positions = []
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                if self.grid[y, x] in [3, 4, 6]:  # Target, box on target, or player on target
                    positions.append((x, y))
        return positions
def generate_random_board(size: int, num_boxes: int = None, check_solvable: bool = True, max_attempts: int = 10) -> SokobanBoard:
    """Generate a random Sokoban board with multiple boxes and targets."""
    if num_boxes is None:
        num_boxes = random.randint(1, 3)  # Default to 1-3 boxes if not specified
        
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        grid = np.zeros((size, size), dtype=int)
        
        # Add walls around border
        grid[0, :] = 1
        grid[-1, :] = 1
        grid[:, 0] = 1
        grid[:, -1] = 1
        
        # Add some internal walls (10% chance)
        for y in range(1, size-1):
            for x in range(1, size-1):
                if random.random() < 0.1:
                    grid[y, x] = 1
        
        # Get empty cells
        empty_cells = [(x, y) for x in range(1, size-1) 
                      for y in range(1, size-1) 
                      if grid[y, x] == 0]
        
        if len(empty_cells) < num_boxes * 2 + 1:  # Need space for boxes, targets, and player
            continue
            
        # Place boxes and targets
        box_positions = []
        target_positions = []
        for _ in range(num_boxes):
            if not empty_cells:
                break
                
            # Place box
            box_pos = random.choice(empty_cells)
            empty_cells.remove(box_pos)
            grid[box_pos[1], box_pos[0]] = 2
            box_positions.append(box_pos)
            
            # Place target
            target_pos = random.choice(empty_cells)
            empty_cells.remove(target_pos)
            grid[target_pos[1], target_pos[0]] = 3
            target_positions.append(target_pos)
            
        # Place player
        if empty_cells:
            player_pos = random.choice(empty_cells)
            grid[player_pos[1], player_pos[0]] = 5
            
            # Create board
            board = SokobanBoard(grid, player_pos[0], player_pos[1])
            
            # Check solvability only if required
            if not check_solvable or board.is_solvable():
                return board
                
    raise ValueError("Could not generate a valid board after maximum attempts")
def format_question_and_analysis(question: str, options: List[str], analysis: str, correct_idx: int,initial_state:str) -> Tuple[str, str]:
        """Format question and analysis with consistent structure."""
        def convert_coordinates_in_text(text) -> str:
            """Convert (row, col) coordinates to (x, y) format in text."""
            import re
            
            # Convert input to string if it's not already
            if not isinstance(text, str):
                text = str(text)
                
            def swap_coordinates(match):
                # Extract numbers from the match
                row, col = match.groups()
                # Return as (col, row) to represent (x, y)
                return f"({col}, {row})"
                
            # Pattern to match (number, number) coordinates
            pattern = r'\((\d+),\s*(\d+)\)'
            return re.sub(pattern, swap_coordinates, text)
        # Format options display
        def format_option(opt):
            """Format individual option based on its type."""
            if isinstance(opt, (tuple, list)) and len(opt) == 2:
                # This is a coordinate pair
                return f"({opt[1]}, {opt[0]})"
            elif isinstance(opt, str) and opt.startswith("(") and opt.endswith(")"):
                # This is already a formatted coordinate string
                return convert_coordinates_in_text(opt)
            else:
                # This is a non-coordinate option
                return str(opt)
        
        # Format options display
        formatted_options = "\nOptions:\n" + "\n".join(
            f"[{i}] {format_option(opt)}" 
            for i, opt in enumerate(options, 1)
        )
        # Format question
        if "Options:" not in question:
            formatted_question = "This is a Sokoban puzzle where cartoon person is player, green X is target, brown box with X is box to push, brown tiles are walls, and light brown areas are movable spaces.The coordinates (x, y) in this puzzle represent the matrix format."+question + formatted_options
        else:
            formatted_question = question
     
        formatted_analysis = (initial_state+analysis+f"\n\nSo the answer is {format_option(options[correct_idx])}. The option number is {correct_idx + 1}. ")
                            

        return formatted_question, formatted_analysis


def format_question_and_analysis2(question: str, options: List[str], analysis: str, correct_idx: int,initial_state:str) -> Tuple[str, str]:
        """Format question and analysis with consistent structure."""
        # Format options display
        formatted_options = "\nOptions:\n" + "\n".join(f"[{i}] {opt}" for i, opt in enumerate(options, 1))
        
        # Format question
        if "Options:" not in question:
            formatted_question = "This is a Sokoban puzzle where cartoon person is player, green X is target, brown box with X is box to push, brown tiles are walls, and light brown areas are movable spaces.The coordinates (x, y) in this puzzle represent the matrix format."+question + formatted_options
        else:
            formatted_question = question
     
        formatted_analysis = initial_state+analysis+f"\n\nSo the answer is {options[correct_idx]}. The option number is {correct_idx + 1}."
                            

        return formatted_question, formatted_analysis

