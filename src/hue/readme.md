# Hue Q&A Generator

This project is a Q&A generator for color-based puzzles. It generates questions about color gradients and patterns on a grid, providing a variety of question types and difficulty levels.

An example game image:

![example game image](hue_dataset_example/images/color-mcq-00001.png)

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

## Text-Only QA Conversion

To convert this game's multimodal QA data into a text-only version, run the unified converter from the repository root:

```bash
python src/Code_for_text_data_derivative/convert_text_data.py --game hue --data src/hue/hue_dataset_example/data.json --output src/hue/hue_dataset_example/data_text.json
```

The converter reads each entry's `state` JSON, prepends a textual description of the visible game state to the original question, and writes `data_text.json` without the `image` or `state` fields by default.

Example text state fragment:

```text
HUE PUZZLE STATE:
Rows and columns follow the displayed 1-based labels from the top-left.
Visible color board as RGB triples; blank means a visible empty/checkered cell, not black:
Row 1: [[169, 234, 68], [115, 68, 222], [131, 108, 204], [148, 148, 187], [165, 188, 170], [182, 229, 153]]
Row 2: [[182, 182, 110], 'blank', [136, 121, 207], 'blank', 'blank', 'blank']
Row 3: [[195, 130, 152], 'blank', [142, 135, 211], 'blank', 'blank', 'blank']
Row 4: [[208, 78, 194], 'blank', [148, 149, 215], 'blank', 'blank', 'blank']
Row 5: [[222, 27, 236], 'blank', [154, 163, 219], 'blank', 'blank', 'blank']
Row 6: ['blank', [136, 208, 213], [160, 177, 223], [184, 146, 234], [209, 116, 245], 'blank']
Blank positions visible in the puzzle: [(2, 2), (2, 4), (2, 5), (2, 6), (3, 2), (3, 4), (3, 5), (3, 6), (4, 2), (4, 4), (4, 5), ...
Cell labels: {}
Gradient information visible from the board: [{'type': 'row', 'index': 5, 'direction': None, 'start_color': [136, 208, 213], 'en ...
Hidden removed color answers are intentionally omitted.
```

## License

This project is licensed under the MIT License.

