# Word Search Q&A Generator

This project is a Word Search Q&A Generator that creates word search puzzles and generates various types of questions based on the puzzles. The questions can be used for educational purposes, quizzes, or games.

## Features

- **Grid Generation**: Generates a word search grid filled with random uppercase letters.
- **Question Types**:
    - **Cell Letter**: Identify the letter at a specific grid cell.
    - **Letter Count**: Count the occurrences of a specific letter in the grid.
    - **Word Direction**: Identify the direction in which a word is placed in the grid.
    - **Find Word Location**: Find the starting position and direction of a word in the grid.
- **Image Generation**: Creates an image representation of the word search grid.
- **Dataset Generation**: Generates a dataset of word search problems with questions, answers, and analysis.

## Installation

1. Install the required dependencies:
        ```bash
        pip install pillow
        ```

## Usage

To generate a dataset of word search problems, run the following command:
```bash
python word_search_generator.py
```

This will create a directory named `word_search_dataset` containing the generated problems, images, and state files.

## Example

Here is an example of how to use the `WordSearchGenerator` class to generate a dataset:

```python
from word_search_generator import WordSearchGenerator

generator = WordSearchGenerator(output_dir="word_search_dataset")
dataset = generator.generate_dataset(num_problems=8)
print(f"Generated {len(dataset)} problems")
```

## Directory Structure

- `main.py`: Main script to generate word search problems.
- `word_search_dataset/`: Directory containing the generated dataset.
    - `images/`: Directory containing the generated grid images.
    - `states/`: Directory containing the grid state files.
    - `data.json`: JSON file containing the dataset information.
- `words.txt`: Words dictionary. Palindrome words are removed to prevent multiple solutions.

## Dependencies

- `Pillow`: For image generation.
- `dataclasses`: For data structure definitions.
- `enum`: For enumerations.
- `json`: For JSON operations.
- `os`: For file operations.
- `random`: For random operations.
- `string`: For string operations.
- `typing`: For type annotations.

## License

This project is licensed under the MIT License.

## Acknowledgements

- The project uses the `Pillow` library for image generation.
