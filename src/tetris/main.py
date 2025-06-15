import argparse
import random
from typing import Tuple, List, Dict
from qa_generator import TetrisQAGenerator
from img_generator import TetrisStateGenerator

QA_TYPE_NUMS = 4

GRID_SIZES = [8,12,16]

def generate_datasets(
    num_grids: int = 10,
    output_dir = "tetris_dataset",
    moves_range: Tuple[int, int] = (10, 20)
) -> Tuple[List[Dict], List[Dict]]:
    """
    Generate Tetris puzzle datasets.
    
    Args:
        num_grids: Number of grid states to generate for each moves count
        grid_size: Size of the grid (rows = cols = grid_size)
        output_dir: Directory to save the generated files
        moves_range: Range of moves to simulate (min_moves, max_moves)
    
    Returns:
        Tuple of (mcq_dataset, fill_dataset)
    """
    # Create generators
    qa_generator = TetrisQAGenerator(output_dir=output_dir)
    state_generator = TetrisStateGenerator(output_dir=output_dir)
    
    # Generate states for different move counts
    all_states = []
    min_moves, max_moves = moves_range
    for sz in GRID_SIZES:
        for moves in range(min_moves, max_moves + 1):
            states = state_generator.generate_all_states(
                num_states=num_grids,
                rows=sz,
                cols=sz,
                num_moves=moves
            )
            all_states.extend(states)
    
    # Shuffle all states
    random.shuffle(all_states)
    
    # Split states into chunks for different QA types
    chunk_size = len(all_states) // QA_TYPE_NUMS
    state_chunks = [
        all_states[i:i + chunk_size] 
        for i in range(0, len(all_states), chunk_size)
    ]
    
    # Generate different types of QA pairs
    for i in range(QA_TYPE_NUMS):
        state_chunks[i] = qa_generator.generate_chunk_qa_pairs(state_chunks[i],i)
        state_generator.save_states(state_chunks[i])
    
    # Save complete dataset
    qa_generator.save_dataset()
    
    return qa_generator.mcq_dataset, qa_generator.fill_dataset

def main():
    """Command-line interface for dataset generation"""
    parser = argparse.ArgumentParser(
        description='Generate Tetris puzzle datasets with various question types'
    )
    
    parser.add_argument(
        '--num_grids',
        type=int,
        default=10,
        help='Number of grid states to generate for each moves count'
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        default='tetris_dataset',
        help='Directory to save the generated files'
    )
    
    parser.add_argument(
        '--min_moves',
        type=int,
        default=10,
        help='Minimum number of moves to simulate'
    )
    
    parser.add_argument(
        '--max_moves',
        type=int,
        default=20,
        help='Maximum number of moves to simulate'
    )
    
    args = parser.parse_args()
    
    # Generate datasets with command line arguments
    mcq_dataset, fill_dataset = generate_datasets(
        num_grids=args.num_grids,
        output_dir=args.output_dir,
        moves_range=(args.min_moves, args.max_moves)
    )
    
    print(f"Generated {len(mcq_dataset)} MCQ questions and {len(fill_dataset)} fill-in-the-blank questions")

if __name__ == "__main__":
    main()