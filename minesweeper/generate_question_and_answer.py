# generate_question_and_answer.py

import random

# Initialize global variables
last_random_coordinates = None  # Used to store the randomly generated coordinates for the 3rd and 8th calls

# Define the base explanation (common part)
base_prompt = (
    "The numbers on the board indicate how many mines are adjacent to that cell, including diagonals. "
    "Cells marked with \"F\" (flagged) are identified as potential locations of mines based on logical deduction or prior knowledge. "
    "These flagged cells play a critical role in guiding your reasoning for answering the questions. "
    "Cells with no numbers and no flags are safe and contain no adjacent mines.\n\n"
    "The board uses a coordinate system where the top-left cell corresponds to (0,0), and the rows and columns are numbered starting from 0.\n\n"
    "Please use the provided board configuration and logical reasoning to deduce the correct answers to the following questions:\n\n"
)

# Define variable parts for different plot levels
plot_level_prompts = {
    "Easy": "This is a Minesweeper game. The size of the chessboard is 4x4, and there are a total of 3 mines hidden on the board.\n\n",
    "Medium": "This is a Minesweeper game. The size of the chessboard is 5x5, and there are a total of 5 mines hidden on the board.\n\n",
    "Hard": "This is a Minesweeper game. The size of the chessboard is 6x6, and there are a total of 8 mines hidden on the board.\n\n"
}

def generate_question_and_answer(game, num, plot_level):
    """
    Randomly generate a question and answer related to the Minesweeper game state.
    """
    global last_random_coordinates  # Reference global variable

    question_types = [
        # StateInfo questions
        {"qa_type": "StateInfo", "template": "How many mines are currently flagged?", "difficulty": "Easy", "description": "Count flagged cells"},
        {"qa_type": "StateInfo", "template": "How many mines are left to be found?", "difficulty": "Easy", "description": "Calculate remaining mines"},
        {"qa_type": "StateInfo", "template": "How many cells have been revealed?", "difficulty": "Easy", "description": "Count revealed cells"},
        {"qa_type": "StateInfo", "template": "What is the state of the cell at ({row},{col})? (revealed number, hidden, flagged as mine)", "difficulty": "Easy", "description": "Check cell state"},

        # StrategyOptimization questions
        {"qa_type": "StrategyOptimization", "template": "What will happen if the player reveals the cell at ({row},{col})?", "difficulty": "Hard", "description": "Predict cell reveal outcome"},
        {"qa_type": "StrategyOptimization", "template": "What is the best next move at ({row},{col})?", "difficulty": "Hard", "description": "Determine optimal move"},
    ]

    # Select the question based on num
    num = num % 10  # Ensure num is within the range of 0 to 9
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
    elif num in [5, 6, 7]:
        question_choice = question_types[4]  # Question 4
        question_id = 4
    elif num in [8, 9]:
        question_choice = question_types[5]  # Question 5
        question_id = 5

    qa_type = question_choice["qa_type"]
    question_template = question_choice["template"]
    qa_level = question_choice["difficulty"]
    question_description = question_choice["description"]

    # Initialize options as None
    options = None

    # Combine the initial explanation
    question_prompt = plot_level_prompts.get(plot_level, plot_level_prompts["Medium"]) + base_prompt

    if "How many mines are currently flagged?" in question_template:
        question = question_prompt + "**Question:** How many mines are currently flagged?"
        answer = sum(sum(row) for row in game.flagged)
        analysis = f"In the current game board, the number of cells that are flagged as mines (marked as F) is {answer}. These F-marked cells represent the locations that the player has deduced or guessed to be mines, so the count of these flagged cells gives us the total number of flagged mines."

    elif "How many mines are left to be found?" in question_template:
        question = question_prompt + "**Question:** How many mines are left to be found?"
        flagged_count = sum(sum(row) for row in game.flagged)
        answer = game.mines - flagged_count
        analysis = f"On the game board, the remaining number of mines is the total mines minus the number of cells flagged as mines (F). By counting the number of F-marked cells (a total of {flagged_count}), we can determine the remaining mines: {answer}."

    elif "How many cells have been revealed?" in question_template:
        question = question_prompt + "**Question:** How many cells have been revealed?"
        answer = sum(sum(row) for row in game.revealed)
        analysis = f"On the current game board, the number of cells that have been revealed is the cells whose background color is white. And the total number is {answer}. Each revealed cell indicates that the player has confirmed it is safe and has explored the surrounding area. Thus, this count represents the total number of revealed cells."

    elif "What is the state of the cell at ({row},{col})?" in question_template:
        # Ensure the random coordinates for the 3rd and 4th calls are different
        if num == 3:
            row, col = random.randint(0, game.rows - 1), random.randint(0, game.cols - 1)
            last_random_coordinates = (row, col)  # Record the random coordinates for the 3rd call
        elif num == 4:
            while True:
                row, col = random.randint(0, game.rows - 1), random.randint(0, game.cols - 1)
                if (row, col) != last_random_coordinates:  # Ensure no duplication
                    break
        else:
            row, col = random.randint(0, game.rows - 1), random.randint(0, game.cols - 1)

        options = [
            "A. It is revealed and shows a number. ",
            "B. It is flagged as mine. ",
            "C. It is still hidden. ",
            "D. It is revealed and shows no more information."
        ]
        question = (
            question_prompt
            + f"**Question**: What is the state of the cell at ({row},{col})? "
            + "\n\n**Options:**\n" + "\n".join(options)
        )
        if game.revealed[row][col]:
            if game.mine_board[row][col] == 0:
                answer = "D"
                analysis = (
                    f"The cell at ({row},{col}) is revealed, and it does not display any useful information "
                    f"because it is an empty cell with no adjacent mines. This is why the state is categorized as 'D'."
                )
            else:
                answer = "A"
                analysis = (
                    f"The cell at ({row},{col}) is revealed, and it displays the number {game.mine_board[row][col]}, "
                    f"indicating the count of mines in the surrounding cells. This matches the description of option 'A'."
                )
        elif game.flagged[row][col]:
            answer = "B"
            analysis = (
                f"The cell at ({row},{col}) is flagged as a potential mine (marked with 'F'). "
                f"This is based on the player's deduction, aligning with the description of option 'B'."
            )
        else:
            answer = "C"
            analysis = (
                f"The cell at ({row},{col}) remains hidden and has not been revealed by the player. "
                f"Hidden cells have no visible numbers or flags, making the state correspond to option 'C'."
            )

    elif "What will happen if the player reveals the cell at ({row},{col})?" in question_template:
        # Only select cells at the boundary
        boundary_cells = game.state_around()
        if not boundary_cells:
            row, col = random.randint(0, game.rows - 1), random.randint(0, game.cols - 1)
        else:
            chosen_cell = random.choice(boundary_cells)
            row, col = chosen_cell["row"], chosen_cell["col"]

        # Initialize value and value2
        if game.mine_board[row][col] == 'M':
            # If the cell is a mine, randomly generate two different numbers
            value = random.randint(1, 9)
            while True:
                value2 = random.randint(1, 9)
                if value2 != value:
                    break
        else:
            # If the cell is not a mine, randomly decide which is the actual value
            actual_value = game.mine_board[row][col]
            if random.choice([True, False]):
                value = actual_value
                while True:
                    value2 = random.randint(0, 9)
                    if value2 != value:
                        break
            else:
                value2 = actual_value
                while True:
                    value = random.randint(0, 9)
                    if value != value2:
                        break

        # Construct question and options
        options = [
            f"A: The game will end because the cell contains a mine. ",
            f"B: The cell will reveal an empty area, and adjacent cells will also be revealed. ",
            f"C: The cell will reveal the number {value}. ",
            f"D: The cell will reveal the number {value2}."
        ]
        
        question = (
            question_prompt
            + f"**Question:** What will happen if the player reveals the cell at ({row},{col})? "
            + f"\n\n**Options:**\n" + "\n".join(options)
        )

        # Generate the answer based on the cell's state
        if game.mine_board[row][col] == 'M':
            # If the cell is a mine, the answer is A
            answer = "A"
            analysis = (
                f"The cell at ({row},{col}) is a mine ('M'). This can be inferred from surrounding cells that indicate the number of adjacent mines and the flags placed by the player. "
                f"If the player reveals this cell, the mine will explode and the game will end immediately, matching the scenario described by option 'A'."
            )
        else:
            # If the cell is not a mine, the answer depends on the actual_value
            if actual_value == 0:
                answer = "B"
                analysis = (
                    f"The cell at ({row},{col}) is not a mine and is empty (0). "
                    f"This conclusion can be drawn from the fact that all surrounding cells are revealed or flagged, and no adjacent cells suggest a mine nearby. "
                    f"When this cell is revealed, an empty area will be displayed, and adjacent cells will also be revealed, matching the scenario in option 'B'."
                )
            elif value == actual_value:
                answer = "C"
                analysis = (
                    f"The cell at ({row},{col}) is not a mine and will reveal the number {value}. "
                    f"This number indicates the count of mines in the surrounding cells. Based on the numbers displayed on adjacent cells and the flags placed, it is logical to conclude that the number {value} matches the condition of the cell, as described in option 'C'."
                )
            else:
                answer = "D"
                analysis = (
                    f"The cell at ({row},{col}) is not a mine and will reveal a number that does not match the expected value. "
                    f"This can occur if the surrounding cells' values or flags are misinterpreted or if the value presented in option 'C' was incorrectly chosen. "
                    f"Therefore, option 'D' is the correct answer, as it represents a situation where the number revealed the correct value {value2} based on the surrounding context and cell conditions."
                )
    
    elif "What is the best next move at ({row},{col})?" in question_template:
        # Randomly select a cell
        # Ensure the random coordinates for the 8th and 9th calls are different
        if num == 8:
            row, col = random.randint(0, game.rows - 1), random.randint(0, game.cols - 1)
            last_random_coordinates = (row, col)
        elif num == 9:
            while True:
                row, col = random.randint(0, game.rows - 1), random.randint(0, game.cols - 1)
                if (row, col) != last_random_coordinates:
                    break
        else:
            row, col = random.randint(0, game.rows - 1), random.randint(0, game.cols - 1)

        # Construct the question and options
        options = [
            "A. Flag this cell as a mine. ",
            "B. Reveal this cell. ",
            "C. Analyze adjacent cells for potential mines according to the number on it. ",
            "D. Skip this move and wait for more information. ",
            "E. This cell has already been revealed, and no further action is required. ",
            "F. This cell has already been flagged as a mine, and no further action is needed."
        ]

        question = (
            question_prompt
            + f"**Question:** What is the best next move at ({row},{col})? "
            + "\n\n**Options:** \n" + "\n".join(options)
        )

        # Check the state of the cell and whether it is on the boundary
        is_boundary_cell = False
        for i in range(-1, 2):
            for j in range(-1, 2):
                nr, nc = row + i, col + j
                if 0 <= nr < game.rows and 0 <= nc < game.cols:
                    if game.revealed[nr][nc]:
                        is_boundary_cell = True
                        break
            if is_boundary_cell:
                break

        # Generate the answer based on the board state
        if game.mine_board[row][col] == 'M' and not game.flagged[row][col]:
            # If the cell is a mine and not flagged, the best action is to flag it
            answer = "A"
            analysis = (
                f"The cell at ({row},{col}) is a mine ('M'). Based on the surrounding cells, it is likely that this cell has not been flagged yet, which means the best move is to flag it as a mine (Option A). "
                f"This prevents accidental revealing and helps the player avoid triggering the mine."
            )
        elif not game.revealed[row][col] and not game.flagged[row][col]:
            if is_boundary_cell:
                # If the cell is on the boundary and not revealed, the best action is to reveal it
                answer = "B"
                analysis = (
                    f"The cell at ({row},{col}) is not revealed yet and is on the boundary of the game area. "
                    f"Based on the adjacent cells' states and the flags in place, the best move is to reveal this cell (Option B), as revealing boundary cells can often provide new information about nearby mines."
                )
            else:
                # If the cell is not on the boundary and not revealed, skip this cell
                answer = "D"
                analysis = (
                    f"The cell at ({row},{col}) is not revealed and not flagged, but it is not near any boundary cells with useful information. "
                    f"In this case, it is better to skip this move and wait for further information (Option D), as revealing this cell may not provide significant new data."
                )
        elif game.revealed[row][col] and game.mine_board[row][col] != 0:
            # If the cell is revealed and the number is not 0, analyze the adjacent cells
            answer = "C"
            analysis = (
                f"The cell at ({row},{col}) has been revealed and shows the number {game.mine_board[row][col]}. This number indicates the count of mines in adjacent cells."
                f" Given the state of the surrounding cells, analyzing adjacent cells to find potential mines is the best next move (Option C). This can help identify safe cells and avoid triggering mines."
            )
        elif game.revealed[row][col]:
            # If the cell is revealed and shows no number (value is 0), no further action is required
            answer = "E"
            analysis = (
                f"The cell at ({row},{col}) has been revealed and shows a value of 0. This means that no mines are adjacent to it. "
                f"Since no further action is required for this cell, the correct answer is Option E."
            )
        elif game.flagged[row][col]:
            # If the cell is flagged, select F
            answer = "F"
            analysis = (
                f"The cell at ({row},{col}) has already been flagged as a mine. "
                f"Therefore, no further action is needed for this cell (Option F), as it has already been marked as containing a mine, and the player should not attempt to reveal it."
            )

    return qa_type, qa_level, question, question_id, question_description, answer, analysis, options
