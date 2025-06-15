# Tic-Tac-Toe VQA Dataset Generator

## Overview

The **Tic-Tac-Toe VQA Dataset Generator** is a tool designed to simulate the classic game of **Tic-Tac-Toe** and generate a comprehensive Visual Question Answering (VQA) dataset. This tool creates game images featuring various states of the Tic-Tac-Toe board and generates different types of questions based on these images. The generated VQA dataset includes game images, questions, answers, and detailed analyses, making it suitable for training multimodal models.

### Dataset Contents:

- **Images**: Visual representations of the Tic-Tac-Toe board at different states.
- **States**: JSON files containing the board state, including player moves and game progress.
- **Questions & Answers**: A variety of questions related to the game state, optimal moves, and potential outcomes.

## Game Rules

Tic-Tac-Toe is a classic two-player game played on a 3x3 grid, (row, col) from (0, 0) to (2, 2). Players take turns marking a space in the grid, one using **O** and the other using **X**. In each game, player **O** starts first. The objective is to be the first to get three of your marks in a row (horizontally, vertically, or diagonally). If all nine squares are filled without either player achieving this, the game ends in a draw.

## Project Structure

```
tictactoe_dataset/
├── images/                  # Directory containing generated board images
│   ├── board_1.png
│   ├── board_2.png
│   └── ...
├── states/                  # Directory containing JSON files of board states
│   ├── board_1.json
│   ├── board_2.json
│   └── ...
└── mcq_dataset.json         # Generated VQA dataset in JSON format
```

### File Descriptions:

- **images/**: Contains PNG images of the Tic-Tac-Toe board at various states.
- **states/**: Contains JSON files representing the board state, including player moves and game progress.
- **mcq_dataset.json**: The main dataset file containing questions, answers, and metadata.

## Supported Question Types

The dataset includes questions categorized into the following types:

1. **StateInfo**: Questions about the current state of the board.
   - Example: *"What is the color of the block at row 0, column 1?"*
2. **ActionOutcome**: Questions about the outcome of a specific move.
   - Example: *"What is the optimal move for the current player?"*
3. **TransitionPath**: Questions about the path to transition from one state to another.
   - Example: *"If the current player moves to row 1, column 0, what is the opponent's optimal move?"*

## How to Use

### 1. Install Dependencies

Ensure you have the following dependencies installed:

- Python 3.x
- `tkinter` (usually included with Python)
- `Pillow==10.2.0` (for generating board images)

Install the required packages using:

```
pip install -r requirements.txt
```

### 2. Run the Script

To generate the dataset, run the following command:

```
python main.py --num 100
```

- `--num`: Specifies the number of board states to generate (default is `10`).

### 3. Output Files

- **Board Images**: Saved in the `tictactoe_dataset/images/` directory.
- **Board States**: Saved in the `tictactoe_dataset/states/` directory.
- **VQA Dataset**: Saved as `tictactoe_dataset/mcq_dataset.json`.

### 4. Dataset Format

The `mcq_dataset.json` file contains the following fields for each question:

- `data_id`: Unique identifier for the question.
- `qa_type`: Type of question (`StateInfo`, `ActionOutcome`, `TransitionPath`).
- `question_id`: Number for qa_type.
- `question_description`: Description of the question type.
- `image`: Path to the corresponding board image.
- `state`: Path to the corresponding board state JSON file.
- `plot_level`: Difficulty level of the board state (`Easy`, `Medium`, `Hard`).
- `qa_level`: Difficulty level of the question (`Easy`, `Medium`, `Hard`).
- `question`: The question text.
- `answer`: The correct answer to the question.
- `analysis`: Detailed analysis of the question.
- `options`: List of possible answers.

### Example Dataset Entry

```json
    {
        "data_id": "tictactoe-mcq-6-TransitionPath",
        "qa_type": "TransitionPath",
        "question_id": 3,
        "question_description": "Questions about the path to transition from one state to another.",
        "image": "images/board_6.png",
        "state": "states/board_6.json",
        "plot_level": "Medium",
        "qa_level": "Hard",
        "question": "If the current player moves to (0, 2), what is the opponent's optimal move?",
        "answer": "B",
        "analysis": "Since the current player moves to (0, 2), after that, Current player is X, opponent is O. Must block opponent O's potential double threat on Row 0 and Column 0.",
        "options": [
            "A.None",
            "B.(0, 0)",
            "C.(0, 1)",
            "D.(0, 2)",
            "E.(1, 0)",
            "F.(1, 1)",
            "G.(1, 2)",
            "H.(2, 0)",
            "I.(2, 1)",
            "J.(2, 2)"
        ]
    },
```

## Additional Notes

The recommendations for the Tic-Tac-Toe analysis provided in the data are based on the following rules:
(Executed sequentially; if the preceding condition is not met, the subsequent one is executed.)

1. If the current player can win immediately, choose the corresponding position.
2. If the opponent can win immediately, choose the corresponding position to block. (If the opponent has multiple immediate winning options, then the opponent is guaranteed to win, and an empty suggestion is returned.)
3. If the current player can create a "double threat" (after placing a piece, there are two rows/columns/diagonals each with two of the current player's pieces and no opponent's pieces, meaning the current player is guaranteed to win), choose the corresponding position.
4. If the opponent can create a "double threat", block the corresponding position.
5. Choose the first empty position from `(0, 0)` to `(2, 2)`.

## License

This project is licensed under the **MIT License**. See the [LICENSE](https://chat.deepseek.com/a/chat/s/LICENSE) file for more details.

