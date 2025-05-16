# 2D Turing Machine Q&A Generator

This project generates a dataset of 2D Turing machine boards, along with questions and answers about the state of the machine after a given number of steps. The dataset includes images of the boards, JSON files describing the board states, and a JSON file containing the questions and answers.

## Features

- Generates random 2D Turing machine boards with customizable sizes and states.
- Simulates the Turing machine for a specified number of steps.
- Generates multiple types of questions about the board's state after the simulation, including the following types:

- Position: Determines the final position of the Turing machine's head after a specified number of steps.
- Head State: Identifies the state of the Turing machine's head after a specified number of steps.
- Symbol at Position: Determines how the symbol at a specific position on the board changes during a specified number of steps.
- First State Entry: Identifies the step at which the Turing machine's head first enters a specific state.
 
- Saves board images, state descriptions, and Q&A data to specified directories.

## Requirements

- Python 3.x
- NumPy
- Matplotlib

## Installation

1. Install the required packages:
    ```sh
    pip install numpy matplotlib
    ```

## Usage

1. Open the `main.py` file and set the desired number of boards to generate:
    ```python
    num_boards = 8  # Example: You can modify this to generate more boards
    ```

2. Run the script to generate the dataset:
    ```sh
    python main.py
    ```

3. The generated dataset will be saved in the `2d_turing_machine_dataset` directory, which includes:
    - `images/`: Directory containing images of the boards.
    - `state/`: Directory containing JSON files describing the board states.
    - `data.json`: JSON file containing the questions and answers.

## Example

Here is an example of the generated Q&A entry in the `data.json` file:

```json
{
    "data_id": "turing-machine-train-00001",
    "plot_id": "turing-machine-train-plot-00001",
    "image": "images\\00001.jpg",
    "state": "state\\00001.json",
    "plot_level": "Medium",
    "qa_type": "ActionOutcome",
    "qa_level": "Medium",
    "question_id": 0,
    "question_description": "position",
    "question": "Question: where will the head be after 5 steps?\nOptions:\n1: (2, 3)\n2: (1, 4)\n...",
    "answer": 1,
    "options": ["(2, 3)", "(1, 4)", "..."],
    "analysis": "The head will visit these positions in order:...\nThe answer is option 1."
}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

This project was inspired by the concept of Turing machines and their applications in theoretical computer science.
