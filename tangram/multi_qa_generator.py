import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
import os
from typing import Dict, List, Tuple, Any
import random
from dataclasses import dataclass, asdict
import colorsys
from matplotlib.colors import rgb2hex, hex2color
import copy
from main import (TengramGenerator, PuzzleConfig, QAPair, rotate_matrix, 
                flip_matrix, get_hole_shape, check_piece_fit_with_details, 
                analyze_rotation_possibilities, get_detailed_rotation_analysis)

def generate_multi_qa_dataset(num_puzzles: int, output_dir: str = 'tengram_multi_qa_dataset') -> None:
    """Generate multiple puzzles, each with multiple QA pairs, and save them to a dataset"""
    os.makedirs(f"{output_dir}/images", exist_ok=True)
    os.makedirs(f"{output_dir}/states", exist_ok=True)
    
    dataset = []
    
    for i in range(num_puzzles):
        # Randomly choose configuration
        config = PuzzleConfig(
            grid_size=random.randint(5, 10),
            num_seeds=random.randint(4, 8),
            num_pieces_to_remove=random.randint(1, 3)
        )
        
        # Generate base puzzle
        generator = TengramGenerator(config)
        generator.generate_seeds()
        generator.assign_cells_to_seeds()
        
        # Save original state before any piece removal
        original_grid = copy.deepcopy(generator.grid)
        original_pieces = copy.deepcopy(generator.pieces)
        original_seeds = copy.deepcopy(generator.seeds)
        
        # Remove random pieces to create the puzzle state that will be visualized
        generator.remove_random_pieces()
        
        # Save visualization of the puzzle with pieces removed
        generator.plot_puzzle(f"{output_dir}/images/tengram-mcq-{i:05d}.png")
        generator.save_state(f"{output_dir}/states/tengram-mcq-{i:05d}.json")
        
        # Generate all types of questions for this puzzle
        qa_pairs = generate_all_questions(generator, i, original_grid, original_pieces, original_seeds)
        dataset.extend(qa_pairs)
    
    # Save dataset
    with open(f"{output_dir}/data.json", 'w') as f:
        json.dump(dataset, f, indent=2)

def generate_all_questions(generator: TengramGenerator, index: int, 
                          original_grid: np.ndarray, 
                          original_pieces: List,
                          original_seeds: List) -> List[Dict]:
    """Generate all types of questions for a single puzzle state"""
    qa_pairs = []
    
    # Define the common properties for all questions
    image_path = f"images/tengram-mcq-{index:05d}.png"
    state_path = f"states/tengram-mcq-{index:05d}.json"
    
    # 1. Generate counting question
    # Using the current state of the generator with removed pieces
    counting_qa = generator.generate_count_question(index)
    counting_qa.data_id = f"tengram-mcq-{index:05d}-piece_count"
    counting_qa.image = image_path
    counting_qa.state = state_path
    qa_pairs.append(asdict(counting_qa))
    
    # 2. Generate area question
    # Use the same state as for counting question
    area_qa = generator.generate_area_question(index)
    area_qa.data_id = f"tengram-mcq-{index:05d}-piece_area"
    area_qa.image = image_path
    area_qa.state = state_path
    qa_pairs.append(asdict(area_qa))
    
    # 3. Generate adjacency question
    # Use the same state as for counting question
    adjacency_qa = generator.generate_adjacency_question(index)
    adjacency_qa.data_id = f"tengram-mcq-{index:05d}-adjacency"
    adjacency_qa.image = image_path
    adjacency_qa.state = state_path
    qa_pairs.append(asdict(adjacency_qa))
    
    # 4. Generate rotation question using the current state of the generator
    # We need to create a new generator that has just ONE piece removed for rotation questions
    rotation_generator = TengramGenerator(generator.config)
    rotation_generator.grid = copy.deepcopy(original_grid)
    rotation_generator.pieces = copy.deepcopy(original_pieces)
    rotation_generator.seeds = copy.deepcopy(original_seeds)
    rotation_generator.config.num_pieces_to_remove = 1
    
    # Make sure to remove one of the pieces that was already removed in the main generator
    # This ensures the rotation question is about a piece that's shown as removed in the image
    if generator.removed_pieces:
        piece_to_remove = generator.removed_pieces[0]
        rotation_generator.removed_pieces = [piece_to_remove]
        rotation_generator.grid[rotation_generator.grid == piece_to_remove] = 0
        
        rotation_qa = rotation_generator.generate_rotation_question(index)
        rotation_qa.data_id = f"tengram-mcq-{index:05d}-rotation"
        rotation_qa.image = image_path
        rotation_qa.state = state_path
        qa_pairs.append(asdict(rotation_qa))
    
    # 5. Generate placement question - Create question_id=5
    if len(generator.removed_pieces) >= 1:
        piece_id = generator.removed_pieces[0]
        
        # Find available positions adjacent to existing pieces
        available_positions = []
        for i in range(generator.grid.shape[0]):
            for j in range(generator.grid.shape[1]):
                if generator.grid[i, j] == 0:  # Empty cell
                    # Check if adjacent to any existing piece
                    for di, dj in [(0,1), (1,0), (0,-1), (-1,0)]:
                        ni, nj = i + di, j + dj
                        if (0 <= ni < generator.grid.shape[0] and 
                            0 <= nj < generator.grid.shape[1] and 
                            generator.grid[ni, nj] > 0):
                            available_positions.append((i, j))
                            break
        
        # If we have valid positions, create the placement question
        if available_positions:
            answer_pos = random.choice(available_positions)
            answer_str = f"({answer_pos[0]}, {answer_pos[1]})"
            
            # Generate options - distinct positions
            unique_positions = list(set(available_positions))
            if len(unique_positions) > 8:
                options_positions = random.sample(unique_positions, 8)
            else:
                options_positions = unique_positions
                
            # Ensure answer is included in options
            if answer_pos not in options_positions:
                options_positions[0] = answer_pos
            
            random.shuffle(options_positions)
            options = [f"({pos[0]}, {pos[1]})" for pos in options_positions]
            answer_index = options.index(answer_str) + 1
            
            # Create detailed analysis in the style of main.py
            piece_colors = generator.get_piece_colors()
            adjacent_pieces = []
            
            # Find which pieces are adjacent to the chosen position
            for di, dj in [(0,1), (1,0), (0,-1), (-1,0)]:
                ni, nj = answer_pos[0] + di, answer_pos[1] + dj
                if (0 <= ni < generator.grid.shape[0] and 
                    0 <= nj < generator.grid.shape[1] and 
                    generator.grid[ni, nj] > 0):
                    adjacent_piece = generator.grid[ni, nj]
                    if adjacent_piece not in adjacent_pieces:
                        adjacent_pieces.append(adjacent_piece)
            
            # Generate analysis text
            analysis = (
                f"Let's analyze the possible placement positions for Piece {piece_id}:\n\n"
                f"1. Board State Analysis:\n"
                f"   - The board has {len(np.unique(generator.grid[generator.grid > 0]))} active pieces\n"
                f"   - Piece {piece_id} is currently removed from the board\n\n"
                f"2. Valid Placement Requirements:\n"
                f"   - Empty cell\n"
                f"   - Adjacent to at least one existing piece\n\n"
                f"3. Position ({answer_pos[0]}, {answer_pos[1]}) Analysis:\n"
                f"   - This position is empty\n"
                f"   - Adjacent to "
            )
            
            if adjacent_pieces:
                pieces_text = [f"Piece {p} ({piece_colors[p]})" for p in adjacent_pieces]
                analysis += f"{', '.join(pieces_text)}\n"
            else:
                analysis += "no pieces (edge of board)\n"
                
            analysis += (
                f"\n4. Other Possible Positions:\n"
                f"   - Found {len(available_positions)} valid positions in total\n\n"
                f"The most appropriate position to place Piece {piece_id} is ({answer_pos[0]}, {answer_pos[1]}), "
                f"as shown in Option {answer_index}."
            )
            
            # Create the question
            question = (
                "Rules:\n"
                "1. Each numbered region represents a piece on the board.\n"
                "2. Pieces are considered adjacent if they share at least one edge.\n"
                "3. Pieces that only touch at corners are not considered adjacent.\n"
                "4. New pieces can only be placed adjacent to existing pieces.\n\n"
                "Question:\n"
                f"At which position (row, column) would be best to place Piece {piece_id} on the board?"
            )
            
            placement_qa = QAPair(
                data_id=f"tengram-mcq-{index:05d}-placement",
                qa_type="ActionOutcome",
                question_id=5,
                question_description="piece_placement",
                image=image_path,
                state=state_path,
                plot_level=generator.get_plot_level(),
                qa_level="Medium",
                question=question,
                answer=answer_index,
                analysis=analysis,
                options=options
            )
            qa_pairs.append(asdict(placement_qa))
    
    return qa_pairs

if __name__ == "__main__":
    generate_multi_qa_dataset(num_puzzles=100, output_dir='tengram_multi_qa_dataset_3')
