```markdown
# Sudoku Puzzle Generator

## Game Rules
This Sudoku variant uses **colors** instead of numbers. The game is played on a grid of size 4x4 or 9x9, where:
- Each row, column, and subgrid (2x2 for 4x4, 3x3 for 9x9) must contain **unique colors**.
- Players can only fill empty cells ("0" in the state) following the uniqueness constraints.
- The goal is to fill the entire board without violating any rules.

## Problem Types
1. **Color Position**  
   *Ask for the color at a specific position.*  
   **Example**:  
   ```json
   {
    "data_id": "sudoku-00001",
    "question_id": 1,
    "qa_type": "StateInfo",
    "question_description": "Check color state at position",
    "image": "images/board_00001.png",
    "state": "states/board_00001.json",
    "plot_level": "easy",
    "qa_level": "easy",
    "question": "What color is at position (1,1)?",
    "answer": "#FF0000",
    "analysis": "The color at Position (1,1) is #FF0000"
  }
   ```

2. **Color Count**  
   *Count occurrences of a specific color.*  
   **Example**:  
   ```json
   {
    "data_id": "sudoku-00004",
    "question_id": 2,
    "qa_type": "StateInfo",
    "question_description": "Count occurrences of specific color",
    "image": "images/board_00004.png",
    "state": "states/board_00004.json",
    "plot_level": "hard",
    "qa_level": "easy",
    "question": "How many times does #FFFF00 appear on the board?",
    "answer": "7",
    "analysis": "Color #FFFF00 appears at: (1,2), (2,4), (3,9), (4,8), (7,1), (8,6), (9,7), total 7 times.So the answer is 7"
  }
   ```

3. **Possible Colors**  
   *Determine valid colors for an empty cell.*  
   **Example**:  
   ```json
   {
    "data_id": "sudoku-00006",
    "question_id": 3,
    "qa_type": "StrategyOptimization",
    "question_description": "Analyze possible colors to fill",
    "image": "images/board_00006.png",
    "state": "states/board_00006.json",
    "plot_level": "hard",
    "qa_level": "medium",
    "question": "This is a sudoku game in which the board is filled with a total number of colours equal to the length of the board's sides, and no rows, columns or squares are allowed to have duplicate colours.How many colors can be filled in position (9,3)?",
    "answer": "1",
    "analysis": "Constraint analysis for position (9,3):\n1. Existing colors in row: #0000FF, #00FF00, #FF00FF\n2. Existing colors in column: #FF0000, #FF00FF, #696969, #228B22, #00FFFF, #00FF00, #0000FF\n3. Existing colors in box: #FFFF00, #FF00FF, #00FF00, #696969, #0000FF\n4. Therefore, possible colors are: #A020F05. So, the answer is 1"
  }
   ```

4. **Empty Count**  
   *Count rows/columns with empty cells exceeding a threshold.*  
   **Example**:  
   ```json
   {
    "data_id": "sudoku-00007",
    "question_id": 4,
    "qa_type": "StateInfo",
    "question_description": "Count regions with empty cells exceeding threshold",
    "image": "images/board_00007.png",
    "state": "states/board_00007.json",
    "plot_level": "easy",
    "qa_level": "medium",
    "question": "How many rows have more than 2 empty cells?",
    "answer": "1",
    "analysis": "Row analysis: row 4 have 3 empty cells in positions 1, 3, 4. Total 1 row(s) have more than 2 empty cells.So the answer is 1"
  }
   ```

5. **Deductive Reasoning**  
   *Multi-step reasoning to determine a cell's color.*  
   **Example**:  
   ```json
   {
    "data_id": "sudoku-00010",
    "question_id": 5,
    "qa_type": "ActionOutcome",
    "question_description": "Multi-step deductive reasoning with constraints analysis",
    "image": "images/board_00010.png",
    "state": "states/board_00010.json",
    "plot_level": "hard",
    "qa_level": "hard",
    "question": "This is a sudoku game in which the board is filled with a total number of colours equal to the length of the board's sides, and no rows, columns or squares are allowed to have duplicate colours.After determining colors at positions (1,2), (1,8), what color should be at position (2,5)?",
    "answer": "#FF00FF",
    "analysis": "Deductive reasoning process:\nStep 1: Position (1,2) must be #696969 because:\n1. Existing colors in row: #00FF00, #FFFF00, #0000FF, #FF0000, #00FFFF, #FF00FF, #A020F0\n2. Existing colors in column: #228B22, #A020F0, #00FF00, #0000FF, #00FFFF, #FF00FF\n3. Existing colors in 3x3 box: #00FF00, #FFFF00, #00FFFF, #228B22, #FF0000, #0000FF, #A020F0, #FF00FF\n4. Therefore, the only possible color for this position is #696969.\nStep 2: Position (1,8) must be #228B22 because:\n1. Existing colors in row: #00FF00, #696969, #FFFF00, #0000FF, #FF0000, #00FFFF, #FF00FF, #A020F0\n2. Existing colors in column: #FFFF00, #00FFFF, #FF00FF, #FF0000, #696969, #0000FF\n3. Existing colors in 3x3 box: #FF00FF, #A020F0, #FFFF00, #696969, #FF0000, #00FFFF\n4. Therefore, the only possible color for this position is #228B22.\n\nFinal analysis for position (2,5):\n1. Existing colors in row: #00FFFF, #228B22, #FF0000, #00FF00, #A020F0, #FFFF00, #696969\n2. Existing colors in column: #FF0000, #FFFF00, #00FF00, #A020F0, #0000FF, #00FFFF\n3. Existing colors in 3x3 box: #0000FF, #FF0000, #00FFFF, #00FF00, #A020F0, #696969, #FFFF00\n4. After previous deductions, possible colors reduced to: #FF00FF"
  }
   ```

## Code Structure
The generator uses the following core classes:
- `SudokuDataGenerator`: Generates puzzles and questions.
- `SudokuGenerator`: Creates valid Sudoku boards.
- `SudokuSolver`: Validates and solves boards.
- `SudokuVisualizer`: Renders boards as images.

## Usage
### Dependencies
Install requirements:  
```bash
pip install -r requirements.txt
```

### Generate Dataset
Run the generator with:  
```bash
python data_generator.py <num_samples> --output_dir <directory>
```
- **`num_samples`**: Total puzzles to generate (e.g., `10`).
- **`--output_dir`**: Output directory (default: `sudoku_dataset`).

### Output Structure
```
output_dir/
├── images/          # Board images (PNG)
├── states/          # Board states (JSON)
└── dataset.json     # Full dataset with questions/answers
```

## Customization
- **Difficulty Control**:  
  - 4x4 boards use `easy_4` or `hard_4` difficulty.  
  - 9x9 boards use `easy`, `medium`, or `hard`.  
- **Problem Distribution**: Modify `question_types` in `generate_dataset()` to prioritize specific questions.

## Notes
- The generator may lag for large `num_samples` due to backtracking in puzzle generation.
- If a puzzle cannot be solved, the generator falls back to simpler questions.
- Images and states are saved incrementally (e.g., `board_00001.png`, `board_00001.json`).

---

**Example Command**:  
```bash
python data_generator.py 5000 --output_dir my_dataset
```  
Generates 5000 puzzles with all question types into `my_dataset`.