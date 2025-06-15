# Klondike Solitaire Dataset Generator

This tool generates question-answer datasets based on Klondike Solitaire game states. It automatically creates screenshots, game states, and corresponding QA pairs for both multiple-choice and fill-in-the-blank questions.

## Quick Start

```bash
# Install requirements
pip install -r requirements.txt

# Run with default settings (100 datasets)
python src/main.py

# To generate a different number of datasets, modify TOTAL_DATASETS in src/main.py
```

## Requirements

- Python 3.8+
- pygame
- tqdm

## Usage

### Basic Run
```bash
python src/main.py
```

### Customize Dataset Size
To change the number of datasets generated:

1. Open `src/main.py`
2. Find this line near the bottom:
```python
TOTAL_DATASETS = 100  # Adjust this number as needed
```
3. Change `100` to your desired number of datasets
4. Save and run the script

### Output Structure

Each run creates a new numbered dataset directory:
```
klondike_dataset_001/
├── images/           # Game board screenshots
├── states/          # Game state JSON files
├── data.json 		# Questions & Answers
```

### Progress Tracking
The tool shows two progress bars:
- Upper bar: Overall dataset generation progress
- Lower bar: Current dataset's question generation progress

## Generated Data Types

Each dataset contains 5 questions (1 of each type):
1. Tableau State Analysis
2. Move Validity
3. Foundation Move Possibilities
4. Deadlock Detection
5. Move Effectiveness

## Technical Notes

- Images are saved as PNG files
- State files are in JSON format
- The program supports keyboard interruption (Ctrl+C)
- Each run creates a new numbered dataset directory automatically

## Performance

- Generates approximately 4-5 datasets per minute
- Each dataset contains 5 questions with corresponding images
- Total generation time depends on the number of datasets requested

## Troubleshooting

If you encounter "pygame module not found":
```bash
pip install pygame
```

If the progress bar doesn't display correctly:
```bash
pip install tqdm
```
