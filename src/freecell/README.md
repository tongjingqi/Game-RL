# FreeCell Puzzle Dataset Generator

This project generates FreeCell game state puzzles in JSON format. The dataset is used to create problem scenarios where players must analyze the game state and answer questions related to valid moves, future states, and game logic.

## 📌 Features
- **Generates FreeCell puzzles** with different problem types.
- **Creates datasets** in a structured JSON format.
- **Supports configurable dataset size** for flexibility.
- **Includes progress tracking** for long-running dataset generation.

---

## 🛠️ Installation
Ensure you have **Python 3.8+** installed. Clone the repository and install dependencies:

```sh
pip install python3.11.11
```

## 🚀 Usage

### Basic Usage
Run the script to generate datasets on a bash:
python main.py

This will:

Generate 1 puzzle (for every kind of puzzle with three types of plot level) in freecell_dataset_example/
Generate 600 puzzles (for every kind of puzzle with three types of plot level) in freecell_dataset/

### Custom Dataset Generation
if you want to change the number of puzzles generated,you can change the parameter "num_puzzles" in main.py

## 📂 Output Format
Each puzzle is stored in JSON format with the following structure:
{
    "data_id": "free_cell-card_after_move-1-00001",
    "plot_level": 1,
    "qa_type": "ActionOutcome",
    "question_id": 4,
    "question_description": "Given a particular game state...",
    "image": "path/to/image.png",
    "state": "path/to/state.json",
    "question": "Find the top card from cascade pile...",
    "answer": 3,
    "analysis": "Detailed explanation of the move...",
    "options": [
        "(Spades, 7)",
        "(Hearts, 9)",
        "(Clubs, 4)",
        "(Diamonds, 2)"
    ]
}

### Key Fields
data_id: Unique identifier for each puzzle.
question: The main FreeCell problem statement.
options: Multiple-choice answers.
answer: The correct answer index (1-based).
analysis: Explanation of the move and its effects.

## 🔧 Code Structure
freecell/
│── generator.py       # Core logic for dataset generation
│── main.py            # Script to run dataset generation
│── freecell.py        # FreeCell game logic and rules
│── requirements.txt   # Dependencies
│── README.md          # Documentation

## 📜 License
This project is licensed under the MIT License. Feel free to use and modify.