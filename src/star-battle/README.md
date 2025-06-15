# Star Battle Puzzle Generator
This project generates Star Battle puzzles, a logic puzzle where the goal is to place stars on a grid according to specific constraints. The puzzles are divided into regions, and each region, row, and column must contain exactly a specified number of stars, while no stars can be adjacent, including diagonally.

This repository provides a Python script that can generate puzzles of various grid sizes, save them in a specified format, and store the generated puzzles in directories. It also includes functionality to generate example puzzles and full datasets.

## Features
Puzzle Generation: Creates Star Battle puzzles with customizable grid sizes (5x5, 6x6, 8x8) and star counts.

Types of Puzzles:
Last Star: Identify the last star placed on the grid.
Cell of a specified region: select a cell belong to the specified region from options
Star of a specified region: select a cell which has been placed a star and belongs to the specified region from the options
valid_cells:select a cell which can be placed a star from the options

Data Storage: Saves puzzles in JSON and image formats, storing information about puzzle state, regions, stars, and more.
Customizable Number of Puzzles: You can specify how many puzzles to generate for each type and grid size.

## Requirements

- Python 3.x
- `pygame` library
- `json` library (for saving puzzle data)

To install the required dependencies, run:
pip install pygame


## Files and Directories
+---.idea
|   \---inspectionProfiles
+---star-battle_dataset
|   +---images
|   \---states
\---star-battle_dataset_example
    +---images
    \---states

Directory star-battle_dataset and star-battle_dataset_example also contain datasets of 4 types of questions.


## Puzzle Rules
The Star Battle puzzle consists of a grid, divided into regions. The objective is to place stars (*) on the grid while following these rules:
1、Row and Column Constraints: Each row and each column must contain exactly n stars.
2、Region Constraints: Each region must contain exactly n stars, where regions are defined by color.
3、Adjacency Rule: Stars cannot be adjacent to each other, including diagonally.

## Functions
1. generate_last_star_puzzle(num_puzzles, n, stars, grid_size, base_path): Generates puzzles of type "Last Star", where the user must identify the last placed star in the grid.

2. generate_state_analysis_puzzle(num_puzzles, n, stars, grid_size, base_path): Generates puzzles of type "State Analysis", where the user must analyze the grid state to identify valid placements or regions.

3. generate_examples(): Generates example puzzles for testing or previewing. Generates one puzzle for each grid size (5x5, 6x6, 8x8) and puzzle type ("Last Star" and "State Analysis").

4. generate_dataset(num_puzzles): Generates a full puzzle dataset with a specified number of puzzles (num_puzzles) for each type and grid size (5x5, 6x6, 8x8).

## How to use
1. Generate Example Puzzles
You can generate a small set of example puzzles by running the following:
generate_examples()

This will create puzzles in the star-battle_dataset_example directory, which includes images and puzzle states.

2. Generate a Full Puzzle Dataset
You can generate a larger set of puzzles by running:
generate_dataset(num_puzzles=400)

This will generate 400 puzzles for each puzzle type ("Last Star" and "State Analysis") for grid sizes 5x5, 6x6, and 8x8, and store them in the star-battle_dataset directory.

3. Customize the Parameters
You can modify the parameters in the generate_last_star_puzzle and generate_state_analysis_puzzle functions to change the number of puzzles, grid sizes, or star count.

## Example Output
After running the puzzle generation scripts, the dataset will be saved in the directories star-battle_dataset_example or star-battle_dataset. You will have:

Puzzle images stored in images/.
Puzzle state data in states/, where each JSON file contains the puzzle’s grid, regions, and star positions.
JSONL files containing puzzle questions, answers, and analysis.

## License
This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments
The Star Battle puzzle concept is used as the basis for the generation of these puzzles.
Pygame was used for rendering puzzle grids and saving images.
