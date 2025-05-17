# Tents Puzzle VQA Dataset Generator

## Overview

**Tents Puzzle VQA Dataset Generator** is a tool designed to create a Visual Question Answering (VQA) dataset based on the Tents puzzle game. It generates random Tents puzzle instances and produces various types of questions related to the puzzles. The dataset includes game images, questions, answers, and detailed analyses, making it ideal for training multimodal models.

## Features

- **Random Puzzle Generation**: Automatically creates Tents puzzle instances with configurable grid sizes and numbers of trees.
- **Question Generation**: Produces different types of questions related to the current state of the puzzle, including fill-in-the-blank and multiple-choice formats.
- **Data Storage**: Saves generated puzzles and questions in a structured format (JSON files) for easy access and use.

## Game Rules

In the Tents puzzle, trees and tents are placed on a grid. The objective is to position tents around the trees according to the following rules:

1. Each cell in the grid can only be in one of the following three states, which are empty, containing a tree, and containing a tent.
2. The number of tents equals the number of trees.
3. Tents can only be placed horizontally or vertically adjacent to the corresponding trees; diagonal placements are not allowed.
4. No two tents can be adjacent, including diagonally.
5. The numbers on the left and top indicate how many tents should be placed in the corresponding row or column.

## Project Structure

- `tents_generator.py`: Main script for generating puzzles and questions.
- `tents_dataset/`: Directory containing all generated datasets, including:
  - `states/`: JSON files representing the puzzle states.
  - `images/`: Visual representations of the puzzles.
  - `fill_dataset.json`: Contains fill-in-the-blank questions.
  - `mcq_dataset.json`: Contains multiple-choice questions.
  - `data.json`: Contains all generated questions.

## Output Contents/Dataset

The dataset consists of:
- **Images**: Visual representations of each puzzle instance.
- **States**: JSON files that describe the grid, tree positions, tent positions, and other relevant data.
- **Questions**: A structured format for both fill-in-the-blank and multiple-choice questions.

## Supported Question Types

1. **StateInfo**: Questions about the current state of the puzzle.
   - How many tents are there in a randomly selected row?
   - Which of the following positions contains a tree?

2. **ActionOutcome**: Questions regarding the outcome of potential actions.
   - How many tents are still missing in a randomly selected column?
   - How many tents are still missing in the entire puzzle?
   - Given the tree positions and considering only the second rule, how many positions in the entire grid are available to place tents (including both positions that are currently occupied by tents and positions that are currently empty)?
   - How many positions in the grid are available to place a new tent without breaking the game rules immediately (it does not have to be a part of a whole solution to the puzzle)?
   - Which of the following positions is allowed to place a new tent without breaking the game rules immediately (it does not have to be a part of a whole solution to the puzzle)?   

3. **TransitionPath**: Not implemented in this version but can be considered for future expansions.

4. **StrategyOptimization**: Not implemented in this version but can be considered for future expansions.


## How to Use

1. **Install Dependencies**:
   - Install required packages using `pip install -r requirements.txt`.

2. **Run the Program**:
   - Execute the main script: `python tents_generator.py`.
   - The program will generate puzzles and associated questions, saving them in the `tents_dataset` directory.

3. **Customize Parameters**:
   - Adjust the following parameters in the script to modify the puzzle generation settings:

   - **`grid_size_list`**:
     - **Description**: Defines the dimensions of the grid for the puzzles. Each tuple in the list represents a different grid size as `(width, height)`.
     - **Example Values**: `[(7, 7), (10, 10), (13, 13)]` creates puzzles with grid sizes of 7x7, 10x10, and 13x13.
     - **Impact**: Larger grids can increase complexity due to more potential placements.

   - **`num_trees_list`**:
     - **Description**: Specifies the number of trees for each puzzle, corresponding to the grid sizes in `grid_size_list`.
     - **Example Values**: `[5, 10, 17]` indicates 5 trees for the 7x7 grid, 10 for the 10x10 grid, and 17 for the 13x13 grid.
     - **Impact**: More trees lead to more tents, affecting the puzzle's difficulty.

   - **`num_puzzles`**:
     - **Description**: Defines how many puzzle instances to generate for each grid size and tree configuration.
     - **Example Value**: `10` generates 10 puzzles for each specified grid size and corresponding number of trees.
     - **Impact**: Increasing this number expands the dataset for testing or training purposes.

   - **`max_removed_tents_list`**:
     - **Description**: Specifies the maximum number of tents to randomly remove from complete puzzles initially generated.
     - **Example Values**: `[2, 4, 7]` allows removal of up to 2, 4, or 7 tents for the respective grid sizes.
     - **Impact**: Removing tents increases challenge and uncertainty, affecting puzzle-solving strategies.
     
   - **`num_options`**:
     - **Description**: Specifies the number of options to include in multiple-choice questions.
     - **Example Value**: `8` generates 8 options for each multiple-choice question.
     - **Impact**: Increasing this number increases the complexity of the questions and the dataset size.

4. **Utilizing the Dataset**:
   - The generated datasets can be used for training and evaluating VQA models or for further analysis in related projects.
