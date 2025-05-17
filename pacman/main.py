# main.py

import json
import random
import os
from game_logic import PacManGame
from image_generator import PacManImageGenerator, generate_game_image
from QA_generator import generate_pacman_QA

VALID_QA_TYPES = {"StateInfo", "ActionOutcome", "TransitionPath", "StrategyOptimization"}

# Generate a valid path using BFS
def generate_valid_path(game, start, max_length):
    from collections import deque
    
    # Get all possible positions (no walls)
    valid_positions = [
        (row, col)
        for row in range(game.grid_size)
        for col in range(game.grid_size)
        if (row, col) not in game.walls
    ]
    
    if not valid_positions:
        return []
        
    # Random path length between 1 and max_length
    desired_length = random.randint(0, max_length) if max_length > 1 else 1
    
    # Initialize with start position and movement direction
    # Direction: (0,0) for start position
    queue = deque([(start, [start], (0,0))])
    visited = {start}
    
    while queue:
        current, path, last_direction = queue.popleft()
        
        # If path is desired length, return it
        if len(path) == desired_length:
            return path
            
        # Get valid neighbors
        row, col = current
        # Define all possible directions: UP, RIGHT, DOWN, LEFT
        directions = [(-1,0), (0,1), (1,0), (0,-1)]
        
        # Filter valid moves and split into forward and backward moves
        forward_moves = []
        side_moves = []
        for direction in directions:
            next_pos = (row + direction[0], col + direction[1])
            
            # Check if move is valid
            if (next_pos not in game.walls and 
                next_pos not in visited and 
                0 <= next_pos[0] < game.grid_size and 
                0 <= next_pos[1] < game.grid_size):
                
                # If this is the first move or continuing in similar direction
                if last_direction == (0,0) or (
                    (direction[0] != -last_direction[0] or direction[1] != -last_direction[1]) and  # not reverse
                    (direction[0] * last_direction[0] + direction[1] * last_direction[1] >= 0)  # same or perpendicular direction
                ):
                    forward_moves.append((next_pos, direction))
                else:
                    side_moves.append((next_pos, direction))
        
        # Prioritize forward moves, then side moves
        valid_moves = forward_moves if forward_moves else side_moves
        random.shuffle(valid_moves)  # Randomize moves within each priority level
        
        # Add valid moves to queue
        for next_pos, direction in valid_moves:
            visited.add(next_pos)
            queue.append((next_pos, path + [next_pos], direction))
            
    # If we couldn't reach desired length, return the longest path found
    return path

def generate_vqa_entry(data_id, qa_type, question_id, question_description, image_path, state_path, plot_level, qa_level, question, answer, analysis, options=None):
    """
    Generate VQA data entries with fields in the specified order.
    """
    entry = {
        "data_id": data_id,
        "qa_type": qa_type,
        "question_id": question_id,
        "question_description": question_description,
        "image": image_path,
        "state": state_path,
        "plot_level": plot_level,
        "qa_level": qa_level,
        "question": question,
        "answer": answer,
        "analysis": analysis,
    }
    if options:
        entry["options"] = options
    return entry

def main():
    # Define plot_levels and corresponding chessboard sizes
    plot_levels = [
        {"plot_level": "Easy", "grid_size": 16},
        {"plot_level": "Medium", "grid_size": 18},
        {"plot_level": "Hard", "grid_size": 20}
    ]

    # Number of samples to generate per plot_level
    num_samples_per_level = 2  # Adjust as needed

    # Create dataset directory
    dataset_dir = "pacman_dataset_example"  # Adjust as needed
    os.makedirs(dataset_dir, exist_ok=True)

    # Create subdirectories
    output_image_dir = os.path.join(dataset_dir, "images")
    output_state_dir = os.path.join(dataset_dir, "states")
    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(output_state_dir, exist_ok=True)

    vqa_data = []  # To store generated VQA data
    
    sample_index = 1  # Initialize sample index

    for plot in plot_levels:
        plot_level = plot["plot_level"]
        grid_size = plot["grid_size"]

        for i in range(1, num_samples_per_level + 1):
            # Initialize Game
            game = PacManGame(grid_size=grid_size)

            # Calculate maximum path length
            max_path_length = int(grid_size * grid_size * (1 - game.wall_ratio) * 0.7)

            # Get current Pac-Man position as start
            start = game.pacman_position

            # Generate and apply the path
            path = generate_valid_path(game, start, max_path_length)

            if path:
                # Remove beans along the path and update score
                for position in path:
                    if position in game.beans:
                        game.beans.remove(position)
                        game.score += 1
                
                # Set Pac-Man's final position and direction
                final_pos = path[-1]
                prev_pos = path[-2] if len(path) > 1 else path[0]
                
                # Calculate direction based on final movement
                row_diff = final_pos[0] - prev_pos[0]
                col_diff = final_pos[1] - prev_pos[1]
                
                if row_diff == -1:
                    game.direction = 'UP'
                elif row_diff == 1:
                    game.direction = 'DOWN'
                elif col_diff == -1:
                    game.direction = 'LEFT'
                elif col_diff == 1:
                    game.direction = 'RIGHT'
            
            # Generate chessboard image
            image_filename = f"image_{str(sample_index).zfill(5)}.png"  # Sequential numbering
            image_path = os.path.join("images", image_filename)  # Relative path
            generate_game_image(game, output_image_dir, image_filename)

            # Save game state
            state_filename = f"board_{str(sample_index).zfill(5)}.json"  # Sequential numbering
            state_path = os.path.join("states", state_filename)  # Relative path
            game.save_to_json(output_state_dir, state_filename)

            for j in range(0,10):   # Ten questions per image
                # Generate question and answer
                qa_type, qa_level, question, question_id, question_description, answer, analysis, options = generate_pacman_QA(game=game, num=j, size=grid_size)

                # Generate unique data_id
                data_id = f"pacman-train-{str(sample_index).zfill(5)}-{j}"

                # Generate VQA entry
                vqa_entry = generate_vqa_entry(
                    data_id,
                    qa_type,
                    question_id,
                    question_description,
                    image_path,
                    state_path,
                    plot_level,
                    qa_level,
                    question,
                    answer,
                    analysis,
                    options
                )
                vqa_data.append(vqa_entry)

            sample_index += 1  # Increment sample index

    # Save VQA data to 'data.json'
    output_json_path = os.path.join(dataset_dir, "data.json")
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(vqa_data, json_file, indent=4, ensure_ascii=False)

    print(f"VQA data generation is complete. A total of {len(vqa_data)} records have been generated and saved to {output_json_path}.")


if __name__ == "__main__":
    main()
