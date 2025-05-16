# Langton's Ant VQA Dataset Generator

## Overview

**Langton's Ant VQA Dataset Generator** is a tool designed to simulate the classic cellular automaton **Langton's Ant** and generate a comprehensive Visual Question Answering (VQA) dataset. It creates game board images featuring the ant's position, direction, and the current state of cells (black or white). Based on these images, it generates different types of questions about the current state and future states of the system. The generated VQA dataset includes game board images, questions, multiple-choice answers, and detailed step-by-step analyses, making it suitable for training multimodal models.

## Features

- **Dynamic Grid Sizes**: Supports multiple grid sizes (5x5, 9x9, 13x13) corresponding to different difficulty levels
- **Coordinate System**: Clear coordinate labeling system for precise position reference
- **Visual Elements**: 
  - White/black cells representing the board state
  - Red arrow indicating ant's position and direction
  - Coordinate labels for easy reference
- **Multiple Question Types**: Generates various types of questions about current state and future states
- **Detailed Analysis**: Provides step-by-step explanations for each question

## Game Rules

In Langton's Ant, we have a grid where each cell is either white or black. A red arrow represents an ant, showing its current position and direction. The ant follows these simple rules:
1. If the ant is on a white cell, it turns right 90 degrees, changes the cell to black, and moves forward one step
2. If the ant is on a black cell, it turns left 90 degrees, changes the cell to white, and moves forward one step
The coordinates system: The top-left cell is (0,0), with x increasing downward and y increasing rightward.

## Project Structure

- `generate_dataset.py`: Main script containing the LangtonVQAGenerator class
- `/images`: Directory containing generated game board images
- `/states`: Directory containing JSON files with board states
- `data.json`: Output JSON file containing the complete dataset

## Output Contents

The generator creates three types of output:

1. **Images (PNG)**:
   - Game board visualizations with ant, cells, and coordinates
   - Stored in `/images` directory

2. **States (JSON)**:
   - Complete board state information
   - Includes grid configuration and ant state
   - 0 indicates white, 1 indicates black
   - Stored in `/states` directory

3. **Dataset (JSON)**:
   - Questions, answers, and analyses
   - References to corresponding images and states
   - Stored as `data.json`

## Supported Question Types

### By Type Category
1. **StateInfo**:
   - Current position and direction of the ant
   - Difficulty: Easy

2. **ActionOutcome**:
   - Predict ant's position and direction after several steps
   - Predict cell color changes after several steps
   - Difficulty: Medium to Hard

### By Difficulty Level
1. **Easy**:
   - plot_size: 5x5 grid
   - qa_type: Current state identification questions

2. **Medium**:
   - plot_size: 9x9 grid
   - qa_type: Movement prediction questions

3. **Hard**:
   - plot_size: 13x13 grid
   - qa_type: Cell state prediction questions

## Usage

### Prerequisites
```bash
pip install pygame
```

### Basic Usage
```bash
python dataset_generator.py
```
And it will automatically generate a file branch like:

foo/                 # Your current working directory

├── images/          # images of the game board

├── states/          # JSON files containing the board states

└── data.json        # VQA dataset

### Adjustable Parameters

1. **Dataset Size**:
   - `dataset_size`: Number of samples to generate per difficulty level, can be adjusted at:
   ```python
   data += generate_mcq_dataset(dataset_size=1, options_num=8)
   data += generate_fill_dataset(dataset_size=1)
   ```

2. **Grid Sizes**:
   - `GRID_SIZES`: Dictionary containing the grid sizes for each difficulty level, can be adjusted at:
   ```python
   GRID_SIZES = {
       "Easy": 5,    # Can be modified
       "Medium": 9,  # Can be modified
       "Hard": 13    # Can be modified
   }
   ```

3. **Steps**:
   - `steps`: Number of steps for question 2 and 3, can be adjusted at:
   ```python
   steps = random.randint(5, 12)
   ```

4. **options_num**
   - `options_num`: Number of options for multiple-choice questions, can be adjusted at:
   ```python
   data += generate_mcq_dataset(dataset_size=1, options_num=8)
   ```

## Additional Notes

- The generator ensures periodic boundary conditions (the ant wraps around the grid edges)
- Questions are generated with varying complexity based on the number of steps
- Each sample includes multiple questions of different types
- Images are generated with clear visual indicators and coordinate systems

## License

This project is licensed under the MIT License - see the LICENSE file for details.