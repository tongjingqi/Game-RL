import json
import os
import random
import numpy as np
from grid import TetrisGrid

class TetrisQAGenerator:
    def __init__(self, output_dir="tetris_dataset"):
        self.output_dir = output_dir
        self.fill_dataset = []
        self.mcq_dataset = []
        
    def generate_empty_cell_qa_pair(self, state_info):
        """Generate a QA pair for a given state"""
        grid = state_info["grid"]
        puzzle_id = state_info["puzzle_id"]
        image_path = state_info["image_path"]
        state_path = state_info["state_path"]
        
        # Generate a random row to ask about
        target_row = random.randint(0, grid.rows-1)
        empty_cells = grid.empty_cells_in_row(target_row)
        empty_cells_cnt = len(empty_cells)

        # Create Q&A entry
        qa_entry = {
            "data_id": f"{puzzle_id}-empty-cells",
            "qa_type": "StateInfo",
            "question_id": 0,
            "question_description": "empty cells in row",
            "image": image_path,
            "state": state_path,
            "plot_level": "Easy" if grid.rows <= 10 else "Medium" if grid.rows <= 15 else "Hard",
            "qa_level": "Easy",
            "question": (
                "Rules:\n"
                f"1. The image shows a standard Tetris grid with {grid.rows} rows and {grid.cols} columns.\n"
                "2. The top row of the grid is labeled as Row 0 according to the coordinates.\n"
                f"3. Row coordinates increment from top to bottom in the grid from 0 to {grid.rows-1}.\n"
                "4. In the image, empty cells are painted white and a cell is "
                "painted grey if in previous moves a tetromino was placed here. Besides, a cell is "
                "painted red if a falling active tetromino is here\n\n"
                f"\nQuestion:\nHow many empty cells are there in Row {target_row} of the grid?\n"
            ),
            "answer": int(empty_cells_cnt),
            "analysis": (
                f"In Row {target_row}, cells at {empty_cells} are white.\n"
                f"So the answer is {empty_cells_cnt}."
            )
        }
        
        return qa_entry
    
    def identify_tetromino_shape(self, normalized_cells):
        """Identify the tetromino shape from normalized coordinates"""
        if not normalized_cells:
            return "no falling Tetrimino", "No red cells in the image, therefore there is no falling Tetrimino currently."
            
        # Convert to binary matrix representation
        max_row = max(row for row, _ in normalized_cells)
        max_col = max(col for _, col in normalized_cells)
        shape_matrix = np.zeros((max_row + 1, max_col + 1), dtype=int)
        for row, col in normalized_cells:
            shape_matrix[row, col] = 1

        prefix = "From the image we can see a falling red Tetrimino."
            
        # Check each possible rotation of the shape against known patterns
        for rotation in range(4):
            rotated = np.rot90(shape_matrix, k=rotation)
            rotation_degrees = (rotation * 90) % 360
            
            # I shape
            if rotated.shape == (1, 4):
                return "I", f"{prefix} This red Tetromino lies horizontally with four blocks in a row, so it is an I-shape tetromino rotated 90° clockwise."
            elif rotated.shape == (4, 1):
                return "I", f"{prefix} This red Tetromino stands vertically with four blocks in a column, so it is an I-shape tetromino rotated 0°."
            
            # O shape
            if rotated.shape == (2, 2) and np.all(rotated == 1):
                return "O", f"{prefix} The red cells form a 2x2 square, which is the O-shape tetromino. Due to its symmetrical nature, rotation doesn't change its appearance."
            
            # T shape
            if rotated.shape == (2, 3) and np.array_equal(rotated, [[1,1,1],[0,1,0]]):
                orientations = {
                    0: "pointing down",
                    1: "pointing left",
                    2: "pointing up",
                    3: "pointing right"
                }
                return "T", f"{prefix} The red tetromino has three blocks in a row with one block extending {orientations[rotation].split()[1]}. So this is a T-shape tetromino rotated {rotation_degrees}° clockwise."
            
            # L shape
            if rotated.shape == (3, 2) and np.array_equal(rotated, [[1,0],[1,0],[1,1]]):
                orientations = {
                    0: "vertical line with one block extending right at the bottom",
                    1: "horizontal line with one block extending down on the left",
                    2: "vertical line with one block extending left at the top",
                    3: "horizontal line with one block extending up on the right"
                }
                return "L", f"{prefix} The red tetromino has three blocks in a {orientations[rotation]}. So this is an L-shape tetromino rotated {rotation_degrees}° clockwise."
            
            # J shape
            if rotated.shape == (3, 2) and np.array_equal(rotated, [[0,1],[0,1],[1,1]]):
                orientations = {
                    0: "vertical line with one block extending left at the bottom",
                    1: "horizontal line with one block extending up on the left",
                    2: "vertical line with one block extending right at the top",
                    3: "horizontal line with one block extending down on the right"
                }
                return "J", f"{prefix} The red tetromino has three blocks in a {orientations[rotation]}. So this is a J-shape tetromino rotated {rotation_degrees}° clockwise."

            # S shape
            if rotated.shape == (2, 3) and np.array_equal(rotated, [[0,1,1],[1,1,0]]):
                orientation = ["horizontal","right","left"] if rotation % 2 == 0 else ["vertical","left","right"]
                return "S", f"{prefix} The red tetromino has two {orientation[0]} blocks on the top {orientation[1]} connected to two {orientation[0]} blocks on the bottom {orientation[2]}. So this is an S-shape tetromino rotated {rotation_degrees}° clockwise, oriented {orientation[0]}."
            
            # Z shape
            if rotated.shape == (2, 3) and np.array_equal(rotated, [[1,1,0],[0,1,1]]):
                orientation = ["horizontal","left","right"] if rotation % 2 == 0 else ["vertical","right","left"]
                return "Z", f"{prefix} The red tetromino has two {orientation[0]} blocks on the top {orientation[1]} connected to two {orientation[0]} blocks on the bottom {orientation[2]}. So this is an Z-shape tetromino rotated {rotation_degrees}° clockwise, oriented {orientation[0]}."
            
        return "unknown", "Unable to identify the tetromino shape from the red cells pattern."

    def generate_falling_tetromino_qa_pair(self, state_info):
        """Generate a QA pair about the active tetromino shape"""
        grid = state_info["grid"]
        puzzle_id = state_info["puzzle_id"]
        image_path = state_info["image_path"]
        state_path = state_info["state_path"]
        
        # Find all cells with value 2 (active tetromino)
        active_cells = []
        for i in range(grid.rows):
            for j in range(grid.cols):
                if grid.grid[i][j] == 2:
                    active_cells.append((i, j))
        
        # Normalize the coordinates to top-left corner if active cells exist
        if active_cells:
            min_row = min(row for row, _ in active_cells)
            min_col = min(col for _, col in active_cells)
            normalized_cells = [(row - min_row, col - min_col) for row, col in active_cells]
        else:
            normalized_cells = []
        
        # Identify the shape
        shape, analysis = self.identify_tetromino_shape(normalized_cells)
        
        # Map shape to answer number
        shape_to_answer = {
            "I": 1,
            "O": 2,
            "T": 3,
            "L": 4,
            "J": 5,
            "S": 6,
            "Z": 7,
            "no falling Tetrimino": 8
        }
        
        answer = shape_to_answer.get(shape, 8)
        answer_analysis = f"So the shape of the active Tetrimino is identified as {shape}, and the option number is {answer}.\n"
            
        # Create Q&A entry
        qa_entry = {
            "data_id": f"{puzzle_id}-shape-recognizing",
            "qa_type": "StateInfo",
            "question_id": 1,
            "question_description": "shape_recognizing",
            "image": image_path,
            "state": state_path,
            "plot_level": "Easy" if grid.rows <= 10 else "Medium" if grid.rows <= 15 else "Hard",
            "qa_level": "Easy",
            "question": (
                "Rules:\n"
                f"1. The image shows a standard Tetris grid with {grid.rows} rows and {grid.cols} columns.\n"
                "2. In Tetris, a Tetrimino is a geometric shape composed of four square blocks. There are seven types of Tetriminos represented by the letters I, O, T, L, J, S, and Z.\n"
                "   - I: A straight line of 4 blocks.\n"
                "   - O: A square shape composed of 4 blocks arranged in a 2x2 square.\n"
                "   - T: A T-shape made up of 4 blocks, with one block in the center and the other three forming a horizontal row above it.\n"
                "   - L: An L-shape made of 4 blocks, with 3 blocks forming a vertical line and 1 block extending right at the bottom, forming an 'L'.\n"
                "   - J: A J-shape made of 4 blocks, similar to the L-shape but mirrored.\n"
                "   - S: An S-shape made of 4 blocks arranged in two stacked rows, each row having two blocks arranged diagonally.\n"
                "   - Z: A Z-shape made of 4 blocks arranged similarly to the S-shape, but mirrored.\n"
                "3. The falling tetromino is painted red in the image.\n"
                "4. The image may not contain active tetromino if the game is already over.\n\n"
                "\nQuestion:\n"
                "What is the shape of the active Tetrimino at the top of the screen?\n\n"
                "Options:\n"
                "1: I\n"
                "2: O\n"
                "3: T\n"
                "4: L\n"
                "5: J\n"
                "6: S\n"
                "7: Z\n"
                "8: no falling Tetrimino"
            ),
            "answer": answer,
            "analysis": analysis + answer_analysis,
            "Options":["I","O","T","L","J","S","Z","no falling Tetrimino"]
        }
        
        return qa_entry
    
    def count_steps_until_collision(self, grid, active_cells, action):
        """Count how many timesteps until the tetromino collides after the given action"""
        rows, cols = grid.shape
        
        # Apply the initial action
        new_cells = []
        if action == "left":
            new_cells = [(row, col - 1) for row, col in active_cells]
        elif action == "right":
            new_cells = [(row, col + 1) for row, col in active_cells]
        # elif action == "rotate":
        #     # Find center of rotation (using bounding box center)
        #     center_row = sum(row for row, _ in active_cells) / len(active_cells)
        #     center_col = sum(col for _, col in active_cells) / len(active_cells)
            
        #     # Rotate around center
        #     new_cells = []
        #     for row, col in active_cells:
        #         # Translate to origin, rotate 90° clockwise, translate back
        #         new_row = int(center_row + (col - center_col))
        #         new_col = int(center_col - (row - center_row))
        #         new_cells.append((new_row, new_col))
                
        # Check if initial action is valid
        for row, col in new_cells:
            if col < 0 or col >= cols or row >= rows:
                return 0  # Immediate collision with boundary
            if row >= 0 and grid[row, col] == 1:
                return 0  # Immediate collision with block
        
        # Count steps until collision
        steps = 0
        while True:
            # Move one step down
            falling_cells = [(row + steps, col) for row, col in new_cells]
            
            # Check for collisions
            for row, col in falling_cells:
                if row >= rows - 1:  # Hit bottom
                    return steps
                if grid[row + 1, col] == 1:  # Hit another block
                    return steps
            
            steps += 1
        
        return steps

    def generate_onestep_outcome_qa_pair(self, state_info):
        """Generate a QA pair about timesteps until collision after one action"""
        grid = state_info["grid"]
        puzzle_id = state_info["puzzle_id"]
        image_path = state_info["image_path"]
        state_path = state_info["state_path"]
        
        # Find active tetromino cells (value 2)
        active_cells = []
        for i in range(grid.rows):
            for j in range(grid.cols):
                if grid.grid[i][j] == 2:
                    active_cells.append((i, j))

        # Normalize the coordinates to top-left corner if active cells exist
        if active_cells:
            min_row = min(row for row, _ in active_cells)
            min_col = min(col for _, col in active_cells)
            normalized_cells = [(row - min_row, col - min_col) for row, col in active_cells]
        else:
            normalized_cells = []
        
        # Identify the shape
        shape, shape_analysis = self.identify_tetromino_shape(normalized_cells)

        cell_analysis = f"The red cells in the image are at {active_cells}.\n"
        
        # Randomly select an action
        actions = ["left", "right"]
        action = random.choice(actions)

        # Prepare action text
        action_text = f"After moving {action} for one column"
    
        # Count steps until collision
        if not active_cells:
            answer = -1
            analysis = "No red cells in the image, therefore there is no falling Tetrimino currently."
        else:
            steps = self.count_steps_until_collision(grid.grid, active_cells, action)
            answer = steps
            
            if steps == 0:
                analysis = (
                    f"{action_text}, the action itself would cause an immediate collision with "
                    f"{'the boundary' if any(col < 0 or col >= grid.cols for _, col in active_cells) else 'other blocks'}. "
                    "Therefore, it will take 0 timesteps to collide."
                )
            else:
                analysis = (
                    f"{action_text}, the tetromino can fall freely for {steps} timesteps before "
                    "colliding with "
                    f"{'the bottom boundary' if any(row + steps >= grid.rows for row, _ in active_cells) else 'another block'}. "
                    f"Therefore, it will take {steps} timesteps to collide."
                )
        
        # Create Q&A entry
        qa_entry = {
            "data_id": f"{puzzle_id}-onestep-outcome",
            "qa_type": "ActionOutcome",
            "question_id": 2,
            "question_description": "timesteps_until_collision",
            "image": image_path,
            "state": state_path,
            "plot_level": "Easy" if grid.rows <= 10 else "Medium" if grid.rows <= 15 else "Hard",
            "qa_level": "Medium",
            "question": (
                "Rules:\n"
                f"1. The image shows a standard Tetris grid with {grid.rows} rows and {grid.cols} columns. \n"
                "2. The first number in a cell coordinate represents the row, and the second number represents the column."
                "3. The action done to the falling tetromino is randomly selected between moved to left / right.\n"
                "4. The active tetromino falls one row every timestep.\n"
                "5. Collision means there is at least one cell around the falling tetromino taken by another tetromino or the boundary, "
                "which causes the falling tetromino can't continue falling or moving left/right.\n"
                "6. There may not be active tetromino(colored in red) falling in the image. If so, the answer should be -1. \n\n"
                "\nQuestion:\n"
                "If the current active Tetrimino is only moved one step "
                f"({action_text}), how many timesteps will it take to collide with another block "
                "or the grid boundary?\n\n"
            ),
            "answer": answer,
            "analysis": cell_analysis + shape_analysis + "\n" + analysis
        }
        
        return qa_entry
    
    def find_all_valid_positions(self, grid,normalized_cells):
        """Find all valid positions for the tetromino"""
        rows, cols = grid.shape
        valid_positions = []

        # Convert to binary matrix representation
        max_row = max(row for row, _ in normalized_cells)
        max_col = max(col for _, col in normalized_cells)
        shape_matrix = np.zeros((max_row + 1, max_col + 1), dtype=int)

        for row, col in normalized_cells:
            shape_matrix[row, col] = 1
        
        # Try all possible rotations
        for rotation in range(4):
            # Rotate the normalized cells
            if rotation > 0:
                shape_matrix = np.rot90(shape_matrix, k=rotation)
                normalized_cells = []
                for row in range(shape_matrix.shape[0]):
                    for col in range(shape_matrix.shape[1]):
                        if shape_matrix[row, col] == 1:
                            normalized_cells.append((row, col))
            
            # Try all possible columns
            for col_offset in range(-2, cols):  # Allow slight overhang
                for row_offset in range(rows):
                    # Check if position is valid
                    position_valid = True
                    position_cells = []
                    
                    for cell_row, cell_col in normalized_cells:
                        new_row = row_offset + cell_row
                        new_col = col_offset + cell_col
                        
                        # Check boundaries
                        if new_col < 0 or new_col >= cols or new_row >= rows:
                            position_valid = False
                            break
                            
                        # Check collision with existing blocks
                        if new_row >= 0 and grid[new_row, new_col] == 1:
                            position_valid = False
                            break
                            
                        position_cells.append((new_row, new_col))
                    
                    if position_valid:
                        # Check if this is the lowest valid position for this column/rotation
                        test_row = row_offset + 1
                        for cell_row, cell_col in normalized_cells:
                            new_row = test_row + cell_row
                            new_col = col_offset + cell_col
                            
                            if (new_row >= rows or 
                                (new_row >= 0 and grid[new_row, new_col] == 1)):
                                valid_positions.append(position_cells)
                                break
                        
        return valid_positions

    def count_cleared_rows(self, grid, added_cells):
        """Count how many rows would be cleared after adding the cells"""
        rows, cols = grid.shape
        grid_copy = grid.copy()
        cleared_row = []
        
        # Add the new cells
        for row, col in added_cells:
            if 0 <= row < rows and 0 <= col < cols:
                grid_copy[row, col] = 1
        
        # Count full rows
        cleared_count = 0
        for row in range(rows):
            if np.all(grid_copy[row] == 1):
                cleared_count += 1
                cleared_row.append(row)
                
        return cleared_count, cleared_row

    def generate_max_row_cleared_qa_pair(self, state_info):
        """Generate a QA pair about maximum possible rows cleared"""
        grid = state_info["grid"]
        puzzle_id = state_info["puzzle_id"]
        image_path = state_info["image_path"]
        state_path = state_info["state_path"]
        
        # Find active tetromino cells (value 2)
        active_cells = []
        for i in range(grid.rows):
            for j in range(grid.cols):
                if grid.grid[i][j] == 2:
                    active_cells.append((i, j))
        
        # If no active tetromino, return None
        if not active_cells:
            max_cleared = 0
            analysis = "No red cells in the image, therefore there is no falling Tetrimino currently. So none of these rows can be cleared."
        else:
            # Get tetromino dimensions
            min_row = min(row for row, _ in active_cells)
            min_col = min(col for _, col in active_cells)
            normalized_cells = [(row - min_row, col - min_col) for row, col in active_cells]

            # Find all valid positions
            valid_positions = self.find_all_valid_positions(grid.grid, normalized_cells)
            shape, shape_analysis = self.identify_tetromino_shape(normalized_cells)

            # Find maximum rows that can be cleared
            max_cleared = 0
            max_cleared_rows = []
            best_position = None
            
            for position in valid_positions:
                cleared, cleared_rows = self.count_cleared_rows(grid.grid, position)
                if cleared > max_cleared:
                    max_cleared = cleared
                    max_cleared_rows = cleared_rows
                    best_position = position
            
            # Prepare analysis text
            if max_cleared == 0:
                analysis = (
                    "After checking all possible positions and rotations of the active tetromino, "
                    "no position results in any complete rows. Therefore, the maximum number "
                    "of rows that can be cleared is 0."
                )
            else:
                # position_desc = f"row {best_position[0][0]}, column {best_position[0][1]}"
                analysis = (
                    f"By placing the 4 blocks of tetromino at {best_position}, "
                    f"{max_cleared} row{'s' if max_cleared > 1 else ''} can be cleared at rows {max_cleared_rows}. "
                    "This is the maximum possible number of rows that can be cleared "
                    "with any valid placement of the current tetromino."
                )
            
            analysis = shape_analysis + "\n\n" + analysis
        
        # Create Q&A entry
        qa_entry = {
            "data_id": f"{puzzle_id}-max-rows",
            "qa_type": "StrategyOptimization",
            "question_id": 3,
            "question_description": "maximum rows to be cleared",
            "image": image_path,
            "state": state_path,
            "plot_level": "Easy" if grid.rows <= 10 else "Medium" if grid.rows <= 15 else "Hard",
            "qa_level": "Hard",
            "question": (
                "Rules:\n"
                f"1. The image shows a standard Tetris grid with {grid.rows} rows and {grid.cols} columns.\n"
                "2. The number and categories of actions done to the falling tetromino "
                "are not restricted, which means you can perform unlimited rotations and translations (moving left, right, or down) to position the tetromino as needed. \n"
                "3. Only consider rows cleared in this turn.\n"
                "4. There may not be active tetromino(colored in red) falling in the image.\n\n"
                "\nQuestion:\n"
                "What's the maximum number of rows can be cleared after positioning "
                "the active Tetrimino in this turn?"
            ),
            "answer": max_cleared,
            "analysis": analysis
        }
        
        return qa_entry
    
    # generate given type of qa pairs from states 
    def generate_chunk_qa_pairs(self,states,qa_type):
        if qa_type == 0:
            for state in states:
                qa_entry = self.generate_empty_cell_qa_pair(state)
                self.fill_dataset.append(qa_entry)
        elif qa_type == 1:
            for state in states:
                qa_entry = self.generate_falling_tetromino_qa_pair(state)
                self.mcq_dataset.append(qa_entry)
        elif qa_type == 2:
            for state in states:
                qa_entry = self.generate_onestep_outcome_qa_pair(state)
                self.fill_dataset.append(qa_entry)
        elif qa_type == 3:
            qa_cnt = len(states)
            valid_cnt = 0
            for i in range(qa_cnt):
                grid_size = states[i]["rows"]
                num_moves = states[i]["num_moves"]
                qa_entry = self.generate_max_row_cleared_qa_pair(states[i])
                while qa_entry["answer"] == 0 and valid_cnt < qa_cnt * 0.7:
                    new_grid = TetrisGrid(grid_size, grid_size)
                    new_grid.simulate_realistic_game(num_moves)
                    states[i]["grid"] = new_grid
                    qa_entry = self.generate_max_row_cleared_qa_pair(states[i])
                if qa_entry["answer"] != 0:
                    valid_cnt += 1
                self.fill_dataset.append(qa_entry)
        return states
                    

    
    def save_dataset(self):
        combined_dataset = self.mcq_dataset + self.fill_dataset
        
        dataset_path = os.path.join(self.output_dir, "data.json")
        with open(dataset_path, 'w', encoding='utf-8') as f:
            json.dump(combined_dataset, f, indent=2, ensure_ascii=False)
        