# Jewel2 VQA Dataset Generator

## Overview
**Jewel2 VQA Dataset Generator** is a tool designed to simulate the classic game **Jewel2** and generate a comprehensive Visual Question Answering (VQA) dataset. It creates game images featuring various elements on the game board and the current total number of cleared elements. Based on these images, it generates different types of test questions. The generated VQA dataset includes game images, questions, answers, and detailed analyses, making it suitable for training multimodal models.

## Project Structure
```
jewel2/
├── chessboard.py
├── level.py
├── randomizer.py
├── image_generator.py
├── QA_generator.py
├── main.py
├── requirements.txt
├── README.md
├── font/
│   ├── Arial.tff
├── jewel2_dataset_example/
│   ├── images/
│   │   └── 00001.png
│   ├── states/
│   │   └── 00001.json
│   └── data.json
```
- **chessboard.py**: Implements the game board and elimination logic.
- **level.py**: Manages level information and various commands.
- **randomizer.py**: Randomly generates elements.
- **image_generator.py**: Generates images based on the current game state.
- **QA_generator.py**: Generates questions, answers, and analyses based on the current game state and question templates.
- **main.py**: Main dataset generation script.
- **requirements.txt**: Lists required Python packages.
- **README.md**: Project documentation.
- **font/**: Include the necessary fonts.
  - **Arial.tff**: Arial font.
- **jewel2_dataset_example/**: Automatically created upon running `main.py`.
  - **images/**: Directory for generated game images named sequentially (e.g., `00001.png`, `00002.png`, ...).
  - **states/**: Directory for saved game state JSON files named sequentially (e.g., `00001.json`, `00002.json`, ...).
  - **data.json**: Generated comprehensive Jewel2 VQA dataset.

## Game Rules

### Elements

#### Basic Elements
- **A, B, C, D, E**
  - **Description**: Standard elements in the game.
  - **Shape**: Diamond-shaped gems in various colors (Red, Green, Blue, Yellow, Purple).
  - **Interactions**:
    - **Clearing**: Align three or more identical basic elements horizontally or vertically to eliminate them.
    - **Swapping**: Swap with adjacent basic elements to form eliminations.

#### Special Elements
- **a, b, c, d, e, +, |**
  - **Description**: Elements with unique abilities that trigger specific elimination patterns.
  - **Shape**:
    - **a, b, c, d, e**: Round gems in various colors (Red, Green, Blue, Yellow, Purple).
    - **+**: A round black gem with low transparency.
    - **|**: A tall, rectangular cyan gem.
  - **Effects**:
    - **a, b, c, d, e**:
      - **Function**: Clearing one removes all corresponding uppercase elements from the board.
        - *Example*: Clearing 'a' eliminates all 'A's.
    - **| (Vertical Clear)**:
      - **Function**: Clears all elements in its vertical column.
    - **+ (Surrounding Clear)**:
      - **Function**: Clears all elements within a distance of 1, including diagonals.
  - **Notes**:
    - Special elements do **not** trigger further eliminations if they remove other special elements.
    - Swapping involving special elements is **not allowed** and will be rejected by the game.

### Commands

#### Available Operations

1. **Clear Operation**
   - **Syntax**: `clear x y`
   - **Description**: Attempts to clear the element at coordinates (x, y).
   - **Conditions**:
     - Must form a valid elimination (part of a horizontal or vertical line of three or more identical elements).
     - If special, its ability is activated upon clearing.
   - **State Changes**:
     - **Basic Element**: Eliminates the element(s), increases **Total Cleared**, and fills gaps with new elements.
     - **Special Element**: Activates its specific clearance effect.

2. **Swap Operation**
   - **Syntax**: `swap x y pos`
   - **Parameters**:
     - (x, y): Coordinates of the element to swap.
     - pos: Direction to swap (up, down, left, right).
   - **Description**: Swaps the element at (x, y) with the adjacent element in the specified direction.
   - **Conditions**:
     - Both elements must be basic.
     - Swap must result in a valid elimination; otherwise, it is undone.
   - **State Changes**:
     - **Successful Swap**: Exchanges elements, performs eliminations, updates **Total Cleared**.
     - **Unsuccessful Swap**: Reverts elements; no score changes.

### Coordinate System
- **0-based coordinates**.
- **Top-left cell**: (0, 0)
- **Bottom-right cell**: Varies based on the chessboard size (e.g., for a 5x5 board, (4, 4)).

### Gameplay Mechanics

#### Score Tracking
- **Total Cleared**: Cumulative number of elements eliminated.
  - **Incremented By**: Number of elements cleared in each successful operation (clear or swap).

#### Objective
Maximize your **Total Cleared** count by strategically performing clear and swap operations to eliminate as many elements as possible. Effective use of special elements can significantly enhance your score by triggering large-scale eliminations.

#### How to Play

##### Starting the Game
1. **Initialization**:
   - Launching Jewel2 presents a grid (size varies based on difficulty level) populated with a mix of basic and special elements based on predefined probabilities.

2. **Understanding the Interface**:
   - **Grid Display**: Each cell shows an element (A-E for basic, a, b, c, d, e, +, | for special).
   - **Score Display**: Shows the current **Total Cleared** count.
   - **Command Input**: Text area to enter `clear` or `swap` commands.

##### Performing Operations
1. **Clear Operation**
   - **Objective**: Remove specific elements to form or extend lines of three or more identical elements.
   - **How to Execute**:
     - Identify coordinates (x, y) of the element to clear.
     - Enter `clear x y`.
     - *Example*: `clear 2 3` clears the element at row 2, column 3.
   - **Outcomes**:
     - **Successful Clear**: Element(s) are removed, **Total Cleared** increases, new elements fill the gaps.
     - **Special Element Activation**: Triggers additional eliminations as per **Special Elements**.
     - **Unsuccessful Clear**: No changes; command is rejected.

2. **Swap Operation**
   - **Objective**: Rearrange elements to create new elimination opportunities.
   - **How to Execute**:
     - Identify coordinates (x, y) of the element to swap.
     - Determine direction `pos` (up, down, left, right).
     - Enter `swap x y pos`.
     - *Example*: `swap 1 1 up` swaps the element at row 1, column 1 with the one above it.
   - **Outcomes**:
     - **Successful Swap**: Elements are exchanged, eliminations performed, **Total Cleared** updated.
     - **Unsuccessful Swap**: Elements revert; no score changes.

#### Additional Notes
- **Special Element Chain Reactions**: Activating a special element's ability will **not** trigger further eliminations, even if other special elements are removed as a result.
- **Element Replenishment**: After each elimination, new elements are generated randomly to maintain a fully populated board, ensuring continuous gameplay.
- **Row and Column Elimination**: Both row and column are evaluated for eliminations. If both meet the criteria, both are cleared.
- **Chain Elimination**: No further chain eliminations occur after new elements are generated post-elimination.

## Supported Question Types

### Questions About the Current Game State

1. **Element Counting**
   - *Example*: **How many 'A' elements are currently on the board?**
   - **Type**: Fill in the blank

2. **Element Positioning**
   - *Example*: **Which of the following positions does element 'C' reside in?**
   - **Type**: Multiple choice
   - **Options**:
     - Eight different options, one of which is the incorrect location

3. **Special Elements Counting**
   - *Example*: **How many special elements (a, b, c, d, e, +, |) are there on the board?**
   - **Type**: Fill in the blank

### Questions After Executing Actions

1. **Single-Step Strategy Questions**
   - **Clear Operation Outcome**
     - *Example*: **What will happen if you execute `clear 0 0`?**
     - **Type**: Multiple choice
     - **Options**:
       - A. Nothing will happen because it does not meet elimination conditions.
       - B. Trigger a special element, total cleared becomes {num}.
       - C. Perform elimination, eliminate {num1} elements, total cleared becomes {num3}.
       - D. Perform elimination, eliminate {num2} elements, total cleared becomes {num4}.
       - E. Perform elimination, eliminate {num5} elements, total cleared becomes {num6}.
       - F. Perform elimination, eliminate {num7} elements, total cleared becomes {num8}.
       - G. Perform elimination, eliminate {num9} elements, total cleared becomes {num10}.
       - H. Perform elimination, eliminate {num11} elements, total cleared becomes {num12}.
   
   - **Swap Operation Outcome**
     - *Example*: **What will happen if you execute `swap 0 0 down`?**
     - **Type**: Multiple choice
     - **Options**:
       - A. Nothing will happen because the swap does not meet elimination conditions.
       - B. Cannot perform swap because one of the elements is special.
       - C. After swap, elimination occurs, clearing {num1} elements, total cleared becomes {num2}.
       - D. After swap, elimination occurs, clearing {num3} elements, total cleared becomes {num4}.
       - E. After swap, elimination occurs, clearing {num5} elements, total cleared becomes {num6}.
       - F. After swap, elimination occurs, clearing {num7} elements, total cleared becomes {num8}.
       - G. After swap, elimination occurs, clearing {num9} elements, total cleared becomes {num10}.
       - H. After swap, elimination occurs, clearing {num11} elements, total cleared becomes {num12}.

2. **Multi-Step Strategy Questions**
   - *Example*: **How many elements will be eliminated after performing `clear 1 1` followed by `swap 2 2 right`?**
   - **Type**: Fill in the blank

### Strategy Questions

- *Example*: **What command will result in the maximum number of elements being cleared in a single move?**
- **Type**: Fill in the blank

## Output Contents

### 1. Image Files
- **Location**: `jewel2_dataset_example/images/`
- **Content**: Generated images representing the current game state, including elements and the total number of cleared elements.
- **Naming Convention**: Sequentially named as `00001.png`, `00002.png`, etc.

### 2. State Files
- **Location**: `jewel2_dataset_example/states/`
- **Content**: JSON files saving the current game state, including the elements on the board and the total number of cleared elements.
- **Naming Convention**: Sequentially named as `00001.json`, `00002.json`, etc.

### 3. VQA Dataset
- **File**: `jewel2_dataset_example/data.json`
- **Content**: JSON array with entries containing:
  - `data_id`
  - `qa_type`
  - `question_id`
  - `question_description`
  - `image`
  - `state`
  - `plot_level`
  - `qa_level`
  - `question`
  - `answer`
  - `analysis`
  - `options` (only for multiple-choice questions)

## How to Use

### 1. Install Dependencies
Before generating the VQA dataset, ensure that all required Python packages are installed. It's recommended to use a virtual environment to manage dependencies.

1. **Set Up a Virtual Environment** *(Optional but recommended)*:
   ```bash
   python -m venv venv
   ```
   - **Activate the Virtual Environment**:
     - **Windows**:
       ```bash
       venv\Scripts\activate
       ```
     - **macOS/Linux**:
       ```bash
       source venv/bin/activate
       ```

2. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

   **Required Packages:**
   - Python 3.x
   - Pillow
   - Any other packages listed in `requirements.txt`

### 2. Generate the VQA Dataset
```bash
python main.py
```
- **Actions**:
  - Generates game states and corresponding images in the `jewel2_dataset_example/images/` directory.
  - Saves game states as JSON files in the `jewel2_dataset_example/states/` directory.
  - Creates VQA entries and compiles them into `jewel2_dataset_example/data.json`.

### 3. Customize Generation Parameters
You can adjust the dataset generation parameters by modifying the `main.py` script:

- **Number of Samples per Difficulty Level**:
  - Locate the following line in `main.py`:
    ```python
    num_samples_per_level = 2  # Adjust as needed
    ```
  - Change the value `2` to your desired number of samples per difficulty level (`Easy`, `Medium`, `Hard`).

- **Difficulty Levels and Chessboard Sizes**:
  - The script supports three difficulty levels, each with a corresponding chessboard size:
    ```python
    plot_levels = [
        {"plot_level": "Easy", "size": 4},
        {"plot_level": "Medium", "size": 5},
        {"plot_level": "Hard", "size": 6}
    ]
    ```
  - You can modify the `size` values or add/remove difficulty levels as needed.

## License
This project is licensed under the [MIT License](LICENSE).
