# Pacman VQA Dataset Generator

## Overview
**Pacman VQA Dataset Generator** is a tool designed to simulate the classic game **Pacman** and generate a comprehensive Visual Question Answering (VQA) dataset. The generated VQA dataset includes game images, questions, answers, and detailed analyses, making it ideal for training and evaluating multimodal models in understanding and reasoning about complex game environments.

## Game Rules
### Game Overview
Pac-Man is a maze arcade game where the player controls Pac-Man to eat as many beans as possible while avoiding ghosts. If a ghost catches Pac-Man, the game ends.

### Basic Elements
- **Pac-Man**: The yellow circular character that the player controls
- **Beans**: Yellow dots that Pac-Man can eat to score points
- **Walls**: Blue barriers that restrict movement
- **Ghosts**: Two ghosts (Pinky and Blinky) that chase Pac-Man

### Game Rules
- Pac-Man must eat beans while avoiding ghosts
- Each bean eaten adds 1 point to the score
- The game ends if a ghost catches Pac-Man
- Movement is restricted by walls

### Movement and Direction
- Pac-Man's mouth opening indicates its current direction
- The direction can be UP, DOWN, LEFT, or RIGHT
- Neither Pac-Man nor ghosts can move through walls

### Ghost Behavior
- **Pinky** (Pink Ghost): Targets 4 spaces ahead of Pac-Man's current position and direction (stops at walls)
- **Blinky** (Red Ghost): Directly targets Pac-Man's current position

### Board Layout
- The board is surrounded by walls on all four sides
- Position (0,0) is located at the top-left corner wall
- Movement grid uses (row, column) coordinates

### Scoring
The score equals the total number of beans eaten by Pac-Man

## Output Contents

### 1. Image Files
- **Location**: `pacman_dataset_example/images/`
- **Content**: Generated images representing the current game state.
- **Naming Convention**: Sequentially named as `board_00001.png`, `board_00002.png`, etc.

### 2. State Files
- **Location**: `pacman_dataset_example/states/`
- **Content**: JSON files saving the current game state.
- **Naming Convention**: Sequentially named as `board_00001.json`, `board_00002.json`, etc.

### 3. VQA Dataset
- **File**: `pacman_dataset_example/data.json`
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

## Dataset Details

### Difficulty Levels
The Pacman VQA dataset supports three levels of difficulty, each with different board sizes:
- **Easy**: 16*16 board.
- **Medium**: 18*18 board.
- **Hard**: 20*20 board.

### Supported Question Types
#### Questions about StateInfo Description
1. **What is Pac-Man's position and direction?**
   - **Type**: Multiple choice
   - **Options**
     - A. (pos1, pos2) dir1
     - B. (pos3, pos4) dir2
     - C. (pos5, pos6) dir3
     - D. (pos7, pos8) dir4
     - E. (pos9, pos10) dir5
     - F. (pos11, pos12) dir6
     - G. (pos13, pos14) dir7
     - H. (pos15, pos15) dir8

2. **Now how many beans are visible there in the 5 by 5 grid around the Pac-man center?**
   - **Type**: Fill in the blank

3. **Which ghost is closer to Pac-Man, Pinky or Blinky?**
   - **Type**: Multiple choice
   - **Options**
     - A. Pinky is closer to Pac-Man
     - B. Blinky is closer to Pac-Man
     - C. Both ghosts are equidistant from Pac-Man

#### Questions about ActionOutcome Description
1. **Assuming the ghosts don't move, how many beans can Pac-Man eat if it moves in its current direction until hitting a wall?**
   - **Type**: Fill in the blank

2. **Assuming Pac-Man and both ghosts move one step at a time, what would happen if Pac-Man moves {direction1} {num1} times, then {direction2} {num2} times?**
   - **Type**: Multiple choice
   - **Options**
     - A. It will eat {bean1} beans, and the score will become {score1}
     - B. It will eat {bean2} beans, and the score will become {score2}
     - C. It will eat {bean3} beans, and the score will become {score3}
     - D. It will eat {bean4} beans, and the score will become {score4}
     - E. It will eat {bean5} beans, and the score will become {score5}
     - F. It will eat {bean6} beans, and the score will become {score6}
     - G. It will be caught by Pinky (the pink ghost)
     - H. It will be caught by Blinky (the red ghost)

3. **Assuming Pinky doesn't move, if Pac-Man moves {direction0} {num1} times, will Pinky's next movement direction change?**
   - **Type**: Multiple choice
   - **Options**
     - A. No. Pinky's direction remains unchanged, still {direction1}
     - B. Yes. Pinky's direction changes to {direction2}
     - C. Yes. Pinky's direction changes to {direction3}
     - D. Yes. Pinky's direction changes to {direction4}

4. **Assuming Blinky doesn't move, if Pac-Man moves {direction0} {num1} times, will Blinky's next movement direction change?**
   - **Type**: Multiple choice
   - **Options**
     - A. No. Blinky's direction remains unchanged, still {direction1}
     - B. Yes. Blinky's direction changes to {direction2}
     - C. Yes. Blinky's direction changes to {direction3}
     - D. Yes. Blinky's direction changes to {direction4}

#### Question about TransitionPath Description
1. **If Pac-Man stays still, where will Pinky move in the next turn?**
   - **Type**: Multiple choice
   - **Options**
     - A. Pinky will move one step {direction1}
     - B. Pinky will move one step {direction2}
     - C. Pinky will move one step {direction3}
     - D. Pinky will move one step {direction4}

2. **If Pac-Man stays still, where will Blinky move in the next turn?**
   - **Type**: Multiple choice
   - **Options**
     - A. Blinky will move one step {direction1}
     - B. Blinky will move one step {direction2}
     - C. Blinky will move one step {direction3}
     - D. Blinky will move one step {direction4}

#### Question About StrategyOptimization Description
1. **If Pac-Man and both ghosts move one step at a time, in which direction should Pac-Man move continuously until hitting a wall to eat the most beans without being caught by a ghost?**
   - **Type**: Multiple choice
   - **Options**
     - A. Pac-Man should move UP
     - B. Pac-Man should move DOWN
     - C. Pac-Man should move RIGHT
     - D. Pac-Man should move LEFT
     - E. Pac-Man will be caught by a ghost regardless of direction

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

### 2. Generate the VQA Dataset
```bash
python main.py
```
- **Actions**:
  - Generates game states and corresponding images in the `pacman_dataset_example/images/` directory.
  - Saves game states as JSON files in the `pacman_dataset_example/states/` directory.
  - Creates VQA entries and compiles them into `pacman_dataset_example/data.json`.

### 3. Customize Generation Parameters
You can adjust the dataset generation parameters by modifying the `main.py` script:

- **Number of Samples per Difficulty Level**:
  - Locate the following line in `main.py`:
    ```python
    # Number of samples to generate per plot_level
    num_samples_per_level = 2  # Adjust as needed
    ```

- **Difficulty Levels and Board Sizes**:
  - The script supports three difficulty levels, each with a corresponding grid size:
    ```python
    # Define plot_levels and corresponding waste pile counts
    plot_levels = [
        {"plot_level": "Easy", "grid_size": 16},
        {"plot_level": "Medium", "grid_size": 18},
        {"plot_level": "Hard", "grid_size": 20}
    ]
    ```

## License
This project is licensed under the [MIT License](LICENSE).