# QA_generator.py
import random
import copy
from typing import Tuple, List, Optional
from level import Level
from chessboard import Chessboard

VALID_QA_TYPES = {"StateInfo", "ActionOutcome", "TransitionPath", "StrategyOptimization"}

common_elements = ['A', 'B', 'C', 'D', 'E']
special_elements = ['a', 'b', 'c', 'd', 'e', '+', '|']
directions = ["up", "down", "right", "left"]

question_prompt = """
# **Game Overview**
Jewel2 is a strategic puzzle game played on a grid. Your primary objective is to eliminate elements by forming horizontal or vertical lines of three or more identical items. Successfully eliminating elements increases your score and clears space on the board for new elements to appear.

# **Elements**
## **Basic Elements**
- **A, B, C, D, E**
  - **Description**: These are the standard elements in the game.
  - **Shape**: Diamond-shaped gems in various colors (Red, Green, Blue, Yellow, Purple).
    - A: Red
    - B: Green
    - C: Blue
    - D: Yellow
    - E: Purple
  - **Interactions**:
    - **Clearing**: When three or more identical basic elements align horizontally or vertically, they are eliminated from the board.
    - **Swapping**: Basic elements can be swapped with adjacent basic elements to form eliminations.

## **Special Elements**
- **a, b, c, d, e, +, |**
  - **Description**: These elements possess unique abilities that trigger specific elimination patterns when activated.
  - **Shape**:
    - **a, b, c, d, e**: Round gems in various colors (Red, Green, Blue, Yellow, Purple).
        - a: Red
        - b: Green
        - c: Blue
        - d: Yellow
        - e: Purple
    - **+**: A round black gem with low transparency.
    - **|**: A tall, rectangular cyan gem.
  - **Effects of Special Elements**:
    - **a, b, c, d, e**:
      - **Function**: Clearing one of these removes all corresponding uppercase basic elements from the board.
        - *Example*: Clearing element 'a' will eliminate all 'A's on the board.
    - **| (Vertical Clear)**:
      - **Function**: Activating this element clears all elements in its vertical column.
    - **+ (Surrounding Clear)**:
      - **Function**: Activating this element clears all elements within a distance of 1 from its position, including diagonals.
  
  - **Notes**:
    - Special elements do **not** trigger further eliminations if they remove other special elements.
    - Swapping involving special elements is **not allowed** and will be rejected by the game.

# **Commands**
## **Available Operations**
1. **Clear Operation**
   - **Syntax**: clear x y
   - **Description**: Attempts to clear the element located at coordinates (x, y).
   - **Conditions**:
     - The targeted element must form a valid elimination (i.e., be part of a horizontal or vertical line of three or more identical elements).
     - If the element is special, its unique ability is activated upon clearing.
   - **State Changes**:
     - **Basic Element**: If the clearance is valid, the element(s) are removed, the score (Total Cleared) increases accordingly, and new elements fall into place to fill the gaps.
     - **Special Element**: Activating a special element triggers its specific clearance effect as described above.

2. **Swap Operation**
   - **Syntax**: swap x y pos
   - **Parameters**:
     - (x, y): Coordinates of the element to be swapped.
     - pos: Direction to swap the element (up, down, left, right).
   - **Description**: Swaps the element at (x, y) with the adjacent element in the specified direction.
     - **pos** can be one of four directions:
       - **up**: Swap with the element directly above (in the same column but one row above).
       - **down**: Swap with the element directly below (in the same column but one row below).
       - **left**: Swap with the element directly to the left (in the same row but one column left).
       - **right**: Swap with the element directly to the right (in the same row but one column right).
   - **Conditions**:
     - Both elements involved in the swap must be basic elements. Swaps involving special elements are rejected.
     - The swap must result in a valid elimination; otherwise, the swap is undone.
   - **State Changes**:
     - **Successful Swap**: Elements are exchanged, any resulting eliminations are performed, and the score (Total Cleared) is updated accordingly.
     - **Unsuccessful Swap**: Elements revert to their original positions, and no changes are made to the score.

# **Coordinate System**
- The board uses **0-based coordinates**.
- **Top-left cell**: (0, 0)
- **Bottom-right cell**: ({size_minus_one}, {size_minus_one})

### **Coordinate Explanation**:
  - **x (Row)**: Represents the **row number** of the element. Rows are numbered from **top to bottom**, starting from 0.
    - *Example*: In a 5x5 grid, the first row (topmost) would have x = 0, the second row would have x = 1, and so on.
  - **y (Column)**: Represents the **column number** of the element. Columns are numbered from **left to right**, starting from 0.
    - *Example*: In a 5x5 grid, the first column (leftmost) would have y = 0, the second column would have y = 1, and so on.

### **Coordinate Example**:
  - To refer to the element located in the second row and third column, you would use coordinates (1, 2).
  - To refer to the element in the fifth row and the first column, you would use coordinates (4, 0).

# **Gameplay Mechanics**
## **Score Tracking**
- **Total Cleared**: Represents the cumulative number of elements that have been eliminated throughout the game.
  - **Incremented By**: The number of elements cleared in each successful operation (clear or swap).

# **Objective**
Maximize your **Total Cleared** count by strategically performing clear and swap operations to eliminate as many elements as possible. Effective use of special elements can significantly enhance your score by triggering large-scale eliminations.

# **How to Play**
## **Starting the Game**
1. **Initialization**:
   - Upon launching Jewel2, a grid is presented, populated with a mix of basic and special elements based on predefined probabilities.

2. **Understanding the Interface**:
   - **Grid Display**: Each cell in the grid represents an element. Basic elements are denoted by uppercase letters (A-E), while special elements use lowercase letters or symbols (a, b, c, d, e, +, |).
   - **Score Display**: The current **Total Cleared** count is visible, updating as you eliminate elements.
   - **Command Input**: A text input area is provided where you can enter commands (clear or swap) to interact with the game.

## **Performing Operations**
1. **Clear Operation**:
   - **Objective**: Remove specific elements to form or extend lines of three or more identical elements.
   - **How to Execute**:
     - Identify the coordinates (x, y) of the element you wish to clear.
     - Enter the command in the format: clear x y.
     - Example: To clear the element at row 2, column 3, input clear 2 3.
   - **Outcomes**:
     - **Successful Clear**: If the targeted element is part of a valid elimination, it and any adjacent identical elements are removed, the **Total Cleared** score increases by the number of elements cleared, and new elements fall into place.
     - **Special Element Activation**: If a special element is cleared, its unique ability is triggered, resulting in additional eliminations as defined in the **Special Elements** section.
     - **Unsuccessful Clear**: If the targeted element does not form a valid elimination, no changes occur, and the command is rejected.

2. **Swap Operation**:
   - **Objective**: Rearrange elements to create new elimination opportunities.
   - **How to Execute**:
     - Identify the coordinates (x, y) of the element you wish to swap.
     - Determine the direction pos (up, down, left, right) to which you want to swap the element.
     - Enter the command in the format: swap x y pos.
     - Example: To swap the element at row 1, column 1 with the element above it, input swap 1 1 up.
   - **Outcomes**:
     - **Successful Swap**: If the swap results in a valid elimination, the elements are exchanged, the resulting eliminations are performed, and the **Total Cleared** score is updated accordingly.
     - **Unsuccessful Swap**: If the swap does not create any valid elimination or involves special elements, the swap is undone, and no changes are made to the score.

# **Additional Notes**
- **Special Element Chain Reactions**: Activating a special element's ability will **not** trigger further eliminations, even if other special elements are removed as a result.
- **Element Replenishment**: After each elimination, new elements are generated randomly to maintain a fully populated board, ensuring continuous gameplay.
- **Row and Column Elimination**: When checking whether an ordinary element can be eliminated, we check whether its rows and columns have three or more identical elements. If both rows and columns meet the elimination rule, both rows and columns are eliminated.
- **Chain Elimination**: After the elimination operation is performed and new elements are generated, no chain elimination will occur.
"""

def find_valid_clear_position(level, size):
    """
    Find a position where clear command can be executed successfully
    Returns: tuple (x, y) if found, None if not found
    """
    for x in range(size):
        for y in range(size):
            simulated_level = copy.deepcopy(level)
            if simulated_level.chessboard.clear_chess(x, y) > 0:
                return (x, y)
    return None

def find_valid_swap_position(level, size, directions):
   """
   Find a position and direction where swap command can be successfully executed
   Returns: tuple (x, y, pos) if found, None if not found
   """
   for x in range(size):
       for y in range(size):
           for pos in directions:
               simulated_level = copy.deepcopy(level)
               if simulated_level.chessboard.swap_chess(x, y, pos):
                   return (x, y, pos)
   return None

def generate_jewel2_QA(level: Level, num: int, size: int) -> Tuple[str, str, str, str, str, Optional[List[str]]]:
    """
    Generates a question and answer pair for Jewel2.

    Parameters:
    - level: Level object representing the current game state.
    - num: Integer used to select the question type.
    - size: The size of the chessboard.

    Returns:
    - qa_type: Type of the question.
    - qa_level: Difficulty level of the question.
    - question: The question text (including question_prompt).
    - answer: The correct answer.
    - analysis: Detailed explanation of the answer.
    - options: List of options if it's a multiple-choice question, else None.
    """
    
    # Define question types with VALID_QA_TYPES
    question_types = [
        # 0: StateInfo
        {"qa_type": "StateInfo", "template": "How many '{element}' elements are currently on the board?", "difficulty": "Easy", "is_mcq": False, "description": "Count specific element"},
        
        # 1: StateInfo - Multiple Choice
        {"qa_type": "StateInfo", "template": "Which of the following positions does element '{element}' reside in?", "difficulty": "Easy", "is_mcq": True, "description": "Identify element position"},
        
        # 2: ActionOutcome
        {"qa_type": "StateInfo", "template": "How many special elements (a, b, c, d, e, +, |) are there on the board?", "difficulty": "Easy", "is_mcq": False, "description": "Count special elements"},
        
        # 3: ActionOutcome - Reasoning
        {"qa_type": "ActionOutcome", "template": "What will happen if you execute clear {x} {y}?", "difficulty": "Medium", "is_mcq": True, "description": "Simulate clear operation"},
        
        # 4: TransitionPath - Reasoning
        {"qa_type": "ActionOutcome", "template": "What will happen if you execute swap {x} {y} {pos}?", "difficulty": "Medium", "is_mcq": True, "description": "Simulate swap operation"},
        
        # 5: StrategyOptimization - Fill in the blank
        {"qa_type": "ActionOutcome", "template": "How many elements will be eliminated at least after performing {command1} followed by {command2}?", "difficulty": "Hard", "is_mcq": False, "description": "Simulate command sequence"},
        
        # 6: StrategyOptimization - Fill in the blank
        {"qa_type": "StrategyOptimization", "template": "What command will result in the maximum number of elements being cleared in a single move?", "difficulty": "Hard", "is_mcq": False, "description": "Optimize command choice"},
    ]
    
    # Select question based on num
    num = num % 10  # Ensure num is within 0-9
    question_id = 0
    if num == 0:
        question_choice = question_types[0]  # Question 0
        question_id = 0
    elif num == 1:
        question_choice = question_types[1]  # Question 1
        question_id = 1
    elif num == 2:
        question_choice = question_types[2]  # Question 2
        question_id = 2
    elif num in [3, 4]:
        question_choice = question_types[3]  # Question 3
        question_id = 3
    elif num in [5, 6]:
        question_choice = question_types[4]  # Question 4
        question_id = 4
    elif num in [7, 8]:
        question_choice = question_types[5]  # Question 5
        question_id = 5
    elif num == 9:
        question_choice = question_types[6]  # Question 6
        question_id = 6
    
    qa_type = question_choice["qa_type"]
    question_template = question_choice["template"]
    qa_level = question_choice["difficulty"]  # 'Easy', 'Medium', 'Hard'
    is_mcq = question_choice["is_mcq"]
    question_description = question_choice["description"]
    
    # Initialize options as None
    options = None
    
    # Handle each question type accordingly
    if qa_type == "StateInfo" and "How many '{element}' elements are currently on the board?" in question_template:
        # Question Type 0
        element = random.choice(common_elements)
        # Find positions and count of the specified element
        positions = [(r, c) for r in range(size) for c in range(size) if level.chessboard.chessboard[r][c] == element]
        count = len(positions)
        question = question_prompt + f"\n\n**Question:** {question_template.format(element=element)}"
        answer = str(count)
        analysis = (
            f"By iterating through each row and column of the chessboard, we identified and counted all occurrences of the '{element}' element."
            f"The '{element}' elements are located at the following positions: "
            f"{', '.join([f'({r},{c})' for r, c in positions]) if positions else 'No positions found'}."
            f"So there are  **{count}** '{element}' in total.\n\n"
        )
    
    elif qa_type == "StateInfo" and "Which of the following positions does element '{element}' reside in?" in question_template:
        while True:
            # Randomly select an element from the common elements
            element = random.choice(common_elements)
            
            # Find the positions where the element resides
            size = len(level.chessboard.chessboard)
            positions = [(r, c) for r in range(size) for c in range(size) if level.chessboard.chessboard[r][c] == element]

            # positions is not empty
            if positions:
                break

        all_positions = [(r, c) for r in range(size) for c in range(size)]
        
        # Generate incorrect candidates: positions where the element does NOT reside
        incorrect_candidates = [pos for pos in all_positions if pos not in positions]
        
        # If there aren't enough incorrect candidates, randomly select incorrect positions
        if len(incorrect_candidates) < 7:
            # If there are not enough incorrect positions, we can randomly pick from all positions
            incorrect_candidates = random.sample(all_positions, 7)
        
        # Select one correct option from the positions where the element resides
        correct_position = random.choice(positions)
        
        # Combine the correct and incorrect options
        options_list = [f"Position {correct_position}"] + [f"Position {pos}" for pos in random.sample(incorrect_candidates, 7)]
        
        # Shuffle the options to randomize their order
        random.shuffle(options_list)
        
        # Format the options with A, B, C, D, ..., H
        options = [f"{chr(65 + idx)}. {opt}" for idx, opt in enumerate(options_list)]
        
        # Find the correct answer letter
        correct_answer_letter = next((opt[0] for opt in options if f"Position {correct_position}" in opt), 'A')
        answer = correct_answer_letter

        # Prepare the question
        question = question_prompt + f"\n\n**Question:**{question_template.format(element=element)}" + "\n\n**Options:**\n" + "\n".join(options)
        
        # Analysis: explain where the element is and where it isn't
        analysis = (
            f"The '{element}' element is located at the following positions: {', '.join([f'({r},{c})' for r, c in positions])}. "
            f"Option {correct_answer_letter} refers to position {correct_position}, where the '{element}' element resides."
        )
    
    elif qa_type == "StateInfo" and "How many special elements (a, b, c, d, e, +, |) are there on the board?" in question_template:
        # Question Type 2
        # Find positions and count of all special elements
        special_positions = {elem: [] for elem in special_elements}  # Dictionary to store positions for each special element
        for r in range(size):
            for c in range(size):
                if level.chessboard.chessboard[r][c] in special_elements:
                    special_positions[level.chessboard.chessboard[r][c]].append((r, c))

        count = sum(len(positions) for positions in special_positions.values())
        question = question_prompt + f"\n\n**Question:** {question_template}"
        answer = str(count)
        analysis = (
            f"By iterating through the chessboard, we counted all special elements (a, b, c, d, e, +, |).\n\n"
            "Positions of special elements:\n" + 
            "\n".join([f"- Element '{elem}': " + 
                    (', '.join([f'({r},{c})' for r, c in positions]) if positions else 'None found')
                    for elem, positions in special_positions.items()]) +
            f"So there are **{count}** special element in total."
        )
    
    elif qa_type == "ActionOutcome" and "What will happen if you execute clear {x} {y}?" in question_template:
        # Question Type 3
        # 75% chance to use valid position
        if random.random() < 0.75:
            valid_pos = find_valid_clear_position(level, size)
            if valid_pos:
                x, y = valid_pos
            else:
                x = random.randint(0, size - 1)
                y = random.randint(0, size - 1)
        else:
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)

        target = level.chessboard.chessboard[x][y]
        question = question_prompt + f"\n\n**Question:** {question_template.format(x=x, y=y)}"
        
        # Simulate clear
        simulated_level = copy.deepcopy(level)
        current_cleared = level.total_cleared
        cleared = simulated_level.chessboard.clear_chess(x, y)
        new_total_cleared = current_cleared + cleared
        
        if cleared == 0:
            options = [
                "A. Nothing will happen because the clear does not meet elimination conditions.",
                f"B. Trigger a special element, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"C. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"D. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}."
                f"E. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"F. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"G. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"H. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
            ]
            answer = 'A'
            analysis = (
                f"Attempting to clear the element at position ({x},{y}) did not meet the elimination conditions, so no elements were cleared."
            )
        else:
            if target in special_elements:
                if target in ['a', 'b', 'c', 'd', 'e']:
                    uppercase_target = target.upper()
                    additional_cleared = sum(row.count(uppercase_target) for row in level.chessboard.chessboard)
                    total_cleared = cleared + additional_cleared
                elif target == '|':
                    additional_cleared = size
                    total_cleared = cleared + additional_cleared
                elif target == '+':
                    # Calculate the number of elements cleared around
                    additional_cleared = 0
                    for r_adj in range(max(0, x-1), min(size, x+2)):
                        for c_adj in range(max(0, y-1), min(size, y+2)):
                            if level.chessboard.chessboard[r_adj][c_adj] != ' ':
                                additional_cleared += 1
                    total_cleared = cleared + additional_cleared
                options = [
                    "A. Nothing will happen because the clear does not meet elimination conditions.",
                    f"B. Trigger a special element, total cleared becomes {new_total_cleared}.",
                    f"C. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                    f"D. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}."
                    f"E. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                    f"F. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                    f"G. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                    f"H. Perform elimination, eliminate {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}."
                ]
                answer = 'B'
                analysis = (
                    f"Clearing the special element '{target}' at position ({x},{y}) triggered its ability, resulting in the elimination of additional elements. "
                    f"The total cleared count increased to {new_total_cleared}."
                )
            else:
                # Normal element handling: randomly select one of the options C-H as the correct answer
                correct_option = random.choice(["C", "D", "E", "F", "G", "H"])
                options = [
                    "A. Nothing will happen because the clear does not meet elimination conditions.",
                    f"B. Trigger a special element, total cleared becomes {new_total_cleared}.",
                ]
                # Generate random distractor options that are not equal to the correct value
                for option in ['C', 'D', 'E', 'F', 'G', 'H']:
                    while True:
                        random_value = random.randint(1, 9)
                        if random_value != cleared:  # Ensure the value is not equal to the correct one
                            break
                    options.append(f"{option}. Perform elimination, eliminate {random_value} elements, total cleared becomes {current_cleared + random_value}.")
                
                # Insert the correct answer in the correct location
                correct_option_index = ['C', 'D', 'E', 'F', 'G', 'H'].index(correct_option)
                options[correct_option_index + 2] = f"{correct_option}. Perform elimination, eliminate {cleared} elements, total cleared becomes {new_total_cleared}."
                
                answer = correct_option
                analysis = (
                    f"There are {cleared} '{target}' elements in a row/column."
                    f"When executing clear {x} {y} they will be eliminated."
                    f"Clearing the element '{target}' at position ({x},{y}) successfully eliminated {cleared} elements vertically/horizontally, increasing the total cleared count to {new_total_cleared}."
                )

        if not is_mcq:
            options = None  # Ensure options are None for fill-in-the-blank
        
        question += "\n\n**Options:**\n" + "\n".join(options)
    
    elif qa_type == "ActionOutcome" and "What will happen if you execute swap {x} {y} {pos}?" in question_template:
        # Question Type 4
        # 75% chance to use valid position
        if random.random() < 0.75:
            valid_move = find_valid_swap_position(level, size, directions)
            if valid_move:
                x, y, pos = valid_move
            else:
                x = random.randint(0, size - 1)
                y = random.randint(0, size - 1) 
                pos = random.choice(directions)
        else:
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            pos = random.choice(directions)

        target_swap = (x, y, pos)
        question = question_prompt + f"\n\n**Question:** {question_template.format(x=x, y=y, pos=pos)}"
        
        # Simulate swap
        simulated_level = copy.deepcopy(level)
        current_cleared = level.total_cleared
        success = simulated_level.chessboard.swap_chess(x, y, pos)
        cleared_after_swap = simulated_level.chessboard.score - level.chessboard.score
        
        nx = x + {'up': -1, 'down': 1, 'left': 0, 'right': 0}[pos]
        ny = y + {'up': 0, 'down': 0, 'left': -1, 'right': 1}[pos]
        
        elem1 = level.chessboard.chessboard[x][y]
        elem2 = level.chessboard.chessboard[nx][ny] if (0 <= nx < size and 0 <= ny < size) else None
        
        if not (0 <= nx < size and 0 <= ny < size):
            # Swap direction out of range
            options = [
                "A. Nothing will happen because the swap does not meet elimination conditions.",
                "B. Cannot perform swap because one of the elements is special.",
                f"C. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"D. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"E. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"F. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"G. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"H. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
            ]
            answer = 'A'
            analysis = (
                f"Attempting to swap the element at position ({x},{y}) in the '{pos}' direction goes out of the board's boundaries. "
                f"Therefore, the swap action cannot be performed, and no elements are cleared."
            )
        elif elem1 in special_elements or elem2 in special_elements:
            # Swap involving special elements is not allowed
            options = [
                "A. Nothing will happen because the swap does not meet elimination conditions.",
                "B. Cannot perform swap because one of the elements is special.",
                f"C. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"D. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"E. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"F. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"G. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                f"H. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
            ]
            answer = 'B'
            analysis = (
                f"Swapping involves special elements '{elem1}' or '{elem2}', which is not allowed. "
                f"The swap action is rejected, and no elements are cleared."
            )
        else:
            if success:
                # Swap resulted in elimination
                correct_option = random.choice(["C", "D", "E", "F", "G", "H"])
                options = [
                    "A. Nothing will happen because the swap does not meet elimination conditions.",
                    f"B. Cannot perform swap because one of the elements is special.",
                ]
                # Generate random distractor options that are not equal to the correct value
                for option in ['C', 'D', 'E', 'F', 'G', 'H']:
                    while True:
                        random_value = random.randint(1, 9)
                        if random_value != cleared_after_swap:  # Ensure the value is not equal to the correct one
                            break
                    options.append(f"{option}. After swap, elimination occurs, clearing {random_value} elements, total cleared becomes {current_cleared + random_value}.")

                # Insert the correct answer in the correct location
                correct_option_index = ['C', 'D', 'E', 'F', 'G', 'H'].index(correct_option)
                options[correct_option_index + 2] = f"{correct_option}. After swap, elimination occurs, clearing {cleared_after_swap} elements, total cleared becomes {level.total_cleared + cleared_after_swap}."

                answer = correct_option
                analysis = (
                    f"Successfully swapped the elements at position ({x},{y}) with ({nx},{ny}) in the '{pos}' direction, resulting in the vertical/horizontal elimination of {cleared_after_swap} elements because it meets the elimination rule. "
                    f"The total cleared count increased to {level.total_cleared + cleared_after_swap}."
                )
            else:
                # Swap did not result in elimination
                options = [
                    "A. Nothing will happen because the swap does not meet elimination conditions.",
                    f"B. Cannot perform swap because one of the elements is special.",
                    f"C. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                    f"D. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                    f"E. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                    f"F. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                    f"G. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                    f"H. After swap, elimination occurs, clearing {random.randint(1, 5)} elements, total cleared becomes {current_cleared + random.randint(1, 5)}.",
                ]
                answer = 'A'
                analysis = (
                    f"Swapping the elements at position ({x},{y}) with ({nx},{ny}) in the '{pos}' direction did not create any valid elimination conditions. "
                    f"No elements were cleared, and the total cleared count remains unchanged."
                )
        
        if not is_mcq:
            options = None  # Ensure options are None for fill-in-the-blank

        question += "\n\n**Options:**\n" + "\n".join(options)

    elif qa_type == "ActionOutcome" and "How many elements will be eliminated at least after performing" in question_template:
        # Question Type 5
        # Select two random commands and execute them to count total cleared elements
        possible_commands = []
        for r in range(size):
            for c in range(size):
                possible_commands.append(f"clear {r} {c}")
                for d in directions:
                    possible_commands.append(f"swap {r} {c} {d}")

        command1 = random.choice(possible_commands)
        command2 = random.choice(possible_commands)
        while command2 == command1:
            command2 = random.choice(possible_commands)

        simulated_level = copy.deepcopy(level)
        total_cleared = 0

        # Execute first command
        if command1.startswith("clear"):
            _, x1, y1 = command1.split()
            cleared1 = simulated_level.chessboard.clear_chess(int(x1), int(y1))
            simulated_level.total_cleared += cleared1
            total_cleared += cleared1
        elif command1.startswith("swap"):
            _, x1, y1, pos1 = command1.split()
            success1 = simulated_level.chessboard.swap_chess(int(x1), int(y1), pos1)
            if success1:
                cleared1 = simulated_level.chessboard.score - level.chessboard.score
                simulated_level.total_cleared += cleared1
                total_cleared += cleared1

        # Execute second command
        if command2.startswith("clear"):
            _, x2, y2 = command2.split()
            cleared2 = simulated_level.chessboard.clear_chess(int(x2), int(y2))
            simulated_level.total_cleared += cleared2
            total_cleared += cleared2
        elif command2.startswith("swap"):
            _, x2, y2, pos2 = command2.split()
            success2 = simulated_level.chessboard.swap_chess(int(x2), int(y2), pos2)
            if success2:
                cleared2 = simulated_level.chessboard.score - level.chessboard.score
                simulated_level.total_cleared += cleared2
                total_cleared += cleared2

        answer = str(total_cleared)
        analysis = (
            f"Executing `{command1}` resulted in vertically/horizontally clearing {cleared1 if 'cleared1' in locals() else 0} elements, "
            f"and executing `{command2}` resulted in vertically/horizontally clearing {cleared2 if 'cleared2' in locals() else 0} elements. "
            f"Overall, a total of {total_cleared} elements were cleared."
        )
        question = question_prompt + f"\n\n**Question:** {question_template.format(command1=command1, command2=command2)}"
        # No options for fill-in-the-blank
        options = None

    elif qa_type == "StrategyOptimization" and "What command will result in the maximum number of elements being cleared in a single move?" in question_template:
        # Question Type 6
        question = question_prompt + f"\n\n**Question:** {question_template}"

        max_cleared = 0
        best_command = "No command can clear any elements."
        valid_moves = []  # List to store all valid moves and their clear counts

        # Evaluate all possible swap commands
        for r in range(size):
            for c in range(size):
                for d in directions:
                    temp_level = copy.deepcopy(level)
                    success = temp_level.chessboard.swap_chess(r, c, d)
                    if success:
                        cleared = temp_level.chessboard.score - level.chessboard.score
                        valid_moves.append({"command": f"swap {r} {c} {d}", "cleared": cleared})
                        if cleared > max_cleared:
                            max_cleared = cleared
                            best_command = f"swap {r} {c} {d}"

        # Evaluate all possible clear commands
        for r in range(size):
            for c in range(size):
                temp_level = copy.deepcopy(level)
                cleared = temp_level.chessboard.clear_chess(r, c)
                if cleared > 0:  # Only add if it actually clears something
                    valid_moves.append({"command": f"clear {r} {c}", "cleared": cleared})
                    if cleared > max_cleared:
                        max_cleared = cleared
                        best_command = f"clear {r} {c}"

        # Sort valid moves by number of elements cleared (descending)
        valid_moves.sort(key=lambda x: x["cleared"], reverse=True)

        if max_cleared > 0:
            analysis = (
                f"Analysis of all possible clearing moves:\n\n"
                + "\n".join([f"- Command `{move['command']}` will vertically/horizontally clear {move['cleared']} elements"
                            for move in valid_moves])
                + "\n\nBest strategy analysis:\n"
                + f"The optimal move is `{best_command}`, which will vertically/horizontally clear the maximum number of {max_cleared} elements. "
                + f"This is superior to the other {len(valid_moves)-1} possible moves as it results in the highest number of cleared elements."
            )
        else:
            analysis = (
                f"In the current board state, no command can clear any elements. We evaluated:\n"
                f"- All possible swap commands for each position and direction\n"
                f"- All possible clear commands for each position\n"
                f"None of these commands resulted in any valid eliminations."
            )

        answer = best_command
        options = None  # No options for fill-in-the-blank

    return qa_type, qa_level, question, question_id, question_description, answer, analysis, options
