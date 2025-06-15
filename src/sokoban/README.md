# Sokoban Puzzle Analysis Project

A Python-based tool for generating, analyzing, and creating educational content around Sokoban puzzles. The project includes functionality to generate random Sokoban boards, create visualizations, and generate various types of analytical questions about the puzzle states.

## Features

- **Random Board Generation**: Create randomized Sokoban puzzles with configurable parameters
- **Multiple Question Types**:
  - Action Outcome Analysis (player and box movement predictions)
  - Strategy Optimization (minimum moves calculation)
  - State Information Analysis (position identification, distance calculations)
  - Transition Path Finding (optimal move sequences)
- **Board Visualization**: Generate clear visual representations of puzzle states
- **Solvability Checking**: Verify if generated puzzles are solvable
- **Dataset Generation**: Create comprehensive datasets for educational or analytical purposes

## Project Structure

```
.
├── sokoban.py     # Core Sokoban implementation and question generation
├── main.py        # Dataset generation and management
└── sokoban_dataset/
    ├── images/    # Generated board visualizations
    ├── states/    # Saved board states
    └── data.json  # Generated questions and metadata
```

## Requirements

- Python 3.7+
- NumPy
- Matplotlib
- Random
- JSON
- OS

## Installation

1. Clone the repository
2. Install required packages:
```bash
pip install numpy matplotlib
```

## Usage

### Basic Usage

```python
from sokoban import generate_random_board
from main import generate_dataset

# Generate a single random board
board = generate_random_board(size=8, num_boxes=1)

# Generate a dataset with multiple boards and questions
dataset = generate_dataset(num_boards=3)
```

### Board Generation Parameters

- `size`: Board dimensions (size x size)
- `num_boxes`: Number of boxes and targets (default: random 1-3)
- `check_solvable`: Whether to verify puzzle solvability (default: True)

### Question Types

1. **ActionOutcome** (Medium Difficulty)
   - Player position prediction after moves
   - Box position prediction after moves

2. **StrategyOptimization** (Hard Difficulty)
   - Minimum moves calculation
   - Solution path finding

3. **StateInfo** (Easy Difficulty)
   - Current player position identification
   - Manhattan distance calculations

4. **TransitionPath** (Hard Difficulty)
   - Optimal move sequence determination

## Board Representation

The board uses the following numerical representation:

- 0: Empty space
- 1: Wall
- 2: Box
- 3: Target
- 4: Box on target
- 5: Player
- 6: Player on target

## JSON Data Format

Generated datasets include the following information for each puzzle:

```json
{
    "data_id": "sokoban-data-00001-00001",
    "image": "images/board_00001.png",
    "state": "states/board_00001.json",
    "plot_level": "Easy/Medium/Hard",
    "qa_level": "Easy/Medium/Hard",
    "qa_type": "ActionOutcome/StrategyOptimization/StateInfo/TransitionPath",
    "question_id": 1,
    "question_description": "Description of the question type",
    "question": "Generated question text",
    "answer": "Correct answer index",
    "analysis": "Detailed solution analysis",
    "options": ["Option 1", "Option 2", ...]
}
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open source and available under the MIT License.