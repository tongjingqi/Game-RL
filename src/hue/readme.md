# Hue Q&A Generator

This project is a Q&A generator for color-based puzzles. It generates questions about color gradients and patterns on a grid, providing a variety of question types and difficulty levels.

## Features

- **Color Matching Questions**: Identify the correct color for a specific cell.
- **Color Description Questions**: Determine the color of a specific cell.
- **Gradient Pattern Questions**: Describe the gradient pattern in a row or column.

## Installation

To install the required dependencies, run:

```bash
pip install numpy pillow opencv-python
```

## Usage

To generate a dataset of questions, run the following script:

```python
python main.py
```

This will create a dataset of 10 questions and save the images and states in the `hue_dataset` folder.

## Example

Here is an example of how to generate a dataset:

```python
outputFolder = "hue_dataset"
dataset = generate_dataset(10)
print("Dataset generated successfully!")
print(f"Number of questions generated: {len(dataset)}")
```

## Output

The generated dataset includes:

- **Images**: Visual representation of the board with color options.
- **States**: JSON files containing the board state and gradient information.
- **Questions**: JSON files with the question text, options, and correct answers.

## License

This project is licensed under the MIT License.

