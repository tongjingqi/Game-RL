# Tengram Puzzle Generator

## Overview

This Python script generates Tengram-like puzzles and accompanying question-answer pairs for different reasoning tasks.  It utilizes Voronoi diagrams to create puzzle pieces on a grid and then poses questions related to the puzzle state.

The script can generate puzzles with questions of the following types:

*   **Counting Pieces:** Asks the user to count the number of pieces remaining on the main board after some pieces have been removed.
*   **Piece Rotation:** Presents a removed piece and asks the user to determine if it can fit back into its original space after rotation, and if so, what rotation(s) would work.
*   **Piece Area:** Asks for the area (number of cells) of a specific piece on the board.
*   **Piece Adjacency:** Asks the user to count how many pieces are adjacent to a given piece on the board.
*   **Piece Placement:**  Removes two neighboring pieces and asks the user to identify the correct position to place a specific piece back into the board from a set of coordinate options.

For each puzzle, the script outputs:

*   **Puzzle Image:** A PNG image visualizing the puzzle, including the main board and removed pieces.
*   **Puzzle State:** A JSON file containing the grid state, seed points, removed pieces, and puzzle configuration.
*   **Dataset Entry:** A JSON entry in `data.json` describing the question, answer, analysis, options, and links to the image and state file.

This tool is designed for generating datasets of Tengram puzzles for research in visual reasoning, question answering, or puzzle generation.

## Dependencies

Before running the script, ensure you have the following Python libraries installed:

*   **numpy:** For numerical operations and array manipulation.
*   **json:** For handling JSON data.
*   **matplotlib:** For plotting and image generation.
*   **scipy:** For Voronoi diagram calculations.
*   **typing:** For type hinting (optional but recommended).
*   **dataclasses:** For creating data classes (Python 3.7+).
*   **colorsys:** For color space conversions.

You can install these dependencies using pip:

```bash
pip install numpy matplotlib scipy
```

## Usage

To generate a dataset of Tengram puzzles, run the script directly:

```bash
python main.py
```

This will execute the `generate_dataset` function at the end of the script, which by default generates 15 puzzles and saves them in a directory named `tengram_dataset`.

You can customize the dataset generation by modifying the `generate_dataset` function or calling it with different parameters.

**`generate_dataset(num_puzzles: int, output_dir: str = 'tengram_dataset')`**

*   **`num_puzzles` (int):** The number of puzzles to generate.
*   **`output_dir` (str, optional):** The directory where the dataset will be saved. Defaults to `tengram_dataset`.

**Example:** To generate 50 puzzles in a directory named `my_puzzles`:

```python
if __name__ == "__main__":
    generate_dataset(num_puzzles=50, output_dir='my_puzzles')
```

Modify the `if __name__ == "__main__":` block in your script to adjust these parameters.

## Dataset Format

The generated dataset is stored in `data.json` within the specified output directory. It is a JSON list where each element is a dictionary representing a question-answer pair (`QAPair` dataclass).

Each dictionary in the dataset has the following keys:

*   **`data_id` (str):** Unique identifier for the data point.
*   **`qa_type` (str):** Type of question (e.g., "StateInfo", "ActionOutcome", "TransitionPath").
*   **`question_id` (int):**  ID of the question type (1 for count, 2 for rotation, 3 for area, 4 for adjacency, 5 for placement).
*   **`question_description` (str):**  Textual description of the question type (e.g., "piece_count", "piece_rotation", "piece_area", "piece_adjacency", "piece_placement").
*   **`image` (str):** Path to the generated puzzle image (PNG file).
*   **`state` (str):** Path to the JSON file containing the puzzle state.
*   **`plot_level` (str):** Difficulty level of the plot visualization ("Easy", "Medium", "Hard") based on grid size.
*   **`qa_level` (str):** Difficulty level of the question ("Easy", "Medium", "Hard").
*   **`question` (str):** The question text presented to the user.
*   **`answer` (int):** The correct answer option number (1-indexed).
*   **`analysis` (str):** Detailed step-by-step analysis explaining the reasoning behind the answer.
*   **`options` (List[str]):** List of answer options presented to the user as strings.

## File Structure

After running the script, the output directory (e.g., `tengram_dataset`) will contain the following structure:

```
tengram_dataset/
├── images/
│   ├── tengram-mcq-00000.png
│   ├── tengram-mcq-00001.png
│   └── ... (puzzle images)
├── states/
│   ├── tengram-mcq-00000.json
│   ├── tengram-mcq-00001.json
│   └── ... (puzzle state JSONs)
└── data.json      (dataset JSON file)
```

*   **`images/`:**  Directory containing PNG images of the generated puzzles.
*   **`states/`:** Directory containing JSON files representing the state of each puzzle.
*   **`data.json`:**  JSON file containing the dataset of question-answer pairs.

