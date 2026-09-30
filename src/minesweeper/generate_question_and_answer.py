# generate_question_and_answer.py

import random

# Initialize global variables
last_random_coordinates = None  # Used to store the randomly generated coordinates for the 3rd and 8th calls

# Define the base explanation (common part)
base_prompt = (
    "The numbers on the board indicate how many mines are adjacent to that cell, including diagonals. "
    "Cells marked with \"F\" (flagged) are identified as potential locations of mines based on logical deduction or prior knowledge. "
    "These flagged cells play a critical role in guiding your reasoning for answering the questions. "
    "Revealed cells with no numbers and no flags are safe and contain no adjacent mines.\n\n"
    "The board uses a coordinate system where the top-left cell corresponds to (0,0), and the rows and columns are numbered starting from 0.\n\n"
    "Please use the provided board configuration and logical reasoning to deduce the correct answers to the following questions:\n\n"
)

# Define variable parts for different plot levels
plot_level_prompts = {
    "Easy": "This is a Minesweeper game. The size of the chessboard is 4x4, and there are a total of 3 mines hidden on the board.\n\n",
    "Medium": "This is a Minesweeper game. The size of the chessboard is 5x5, and there are a total of 5 mines hidden on the board.\n\n",
    "Hard": "This is a Minesweeper game. The size of the chessboard is 6x6, and there are a total of 8 mines hidden on the board.\n\n"
}

# Coordinates asked by the three q4 calls of the current board (reset at its first q4 call)
q4_used_cells = []


def get_neighbors(game, r, c):
    """The (up to eight) cells adjacent to (r, c), including diagonals."""
    return [(r + dr, c + dc) for dr in range(-1, 2) for dc in range(-1, 2)
            if (dr or dc) and 0 <= r + dr < game.rows and 0 <= c + dc < game.cols]


def enumerate_mine_layouts(game):
    """All mine placements consistent with the visible board.

    Flagged cells count as mines, every revealed number must be matched exactly, and the total
    number of mines stated in the question is respected. Hidden cells next to a revealed number
    (the frontier) are enumerated one by one; the remaining hidden cells (the interior) are only
    constrained by the mine total, so a layout records how many mines they hold.

    Returns (interior cells, [(frozenset of frontier mines, number of interior mines), ...]).
    """
    hidden = [(r, c) for r in range(game.rows) for c in range(game.cols)
              if not game.revealed[r][c] and not game.flagged[r][c]]
    hidden_set = set(hidden)
    constraints = []
    for r in range(game.rows):
        for c in range(game.cols):
            if game.revealed[r][c]:
                neighbors = get_neighbors(game, r, c)
                flags = sum(game.flagged[nr][nc] for nr, nc in neighbors)
                constraints.append(([p for p in neighbors if p in hidden_set], game.mine_board[r][c] - flags))
    frontier = sorted({p for cells, _ in constraints for p in cells})
    order = {p: i for i, p in enumerate(frontier)}
    interior = [p for p in hidden if p not in order]
    unflagged_mines = game.mines - sum(sum(row) for row in game.flagged)
    layouts = []

    def search(i, mines):
        for cells, need in constraints:
            placed = sum(p in mines for p in cells)
            open_cells = sum(order[p] >= i for p in cells)
            if placed > need or placed + open_cells < need:
                return
        if i == len(frontier):
            rest = unflagged_mines - len(mines)
            if 0 <= rest <= len(interior):
                layouts.append((frozenset(mines), rest))
            return
        search(i + 1, mines)
        search(i + 1, mines | {frontier[i]})

    search(0, frozenset())
    return interior, layouts


def reveal_outcomes(game, row, col):
    """What revealing (row, col) can show over all consistent layouts: "mine" and/or the numbers."""
    if game.flagged[row][col]:
        return {"mine"}
    interior, layouts = enumerate_mine_layouts(game)
    neighbors = get_neighbors(game, row, col)
    flags = sum(game.flagged[nr][nc] for nr, nc in neighbors)
    interior_neighbors = [p for p in neighbors if p in interior]
    target_is_interior = (row, col) in interior
    outcomes = set()
    for mines, rest in layouts:
        if target_is_interior:
            if rest >= 1:
                outcomes.add("mine")
            if rest > len(interior) - 1:
                continue
            others = len(interior) - 1 - len(interior_neighbors)
        else:
            if (row, col) in mines:
                outcomes.add("mine")
                continue
            others = len(interior) - len(interior_neighbors)
        base = flags + sum(p in mines for p in neighbors)
        # j of the interior mines are next to the target, the other rest - j elsewhere in the interior
        for j in range(len(interior_neighbors) + 1):
            if 0 <= rest - j <= others:
                outcomes.add(base + j)
    return outcomes


def describe_constraints(game, row, col):
    """The revealed numbers and flags around (row, col) and the mine total, as analysis text."""
    neighbors = get_neighbors(game, row, col)
    numbers = [f"({r},{c}) shows {game.mine_board[r][c]}" for r, c in neighbors if game.revealed[r][c]]
    flags = [f"({r},{c})" for r, c in neighbors if game.flagged[r][c]]
    flagged_total = sum(sum(r) for r in game.flagged)
    text = f"The cell at ({row},{col}) is hidden. "
    text += (f"Its revealed neighbors: {', '.join(numbers)}. " if numbers else "It has no revealed neighbors. ")
    text += (f"Its flagged neighbors: {', '.join(flags)}. " if flags else "It has no flagged neighbors. ")
    text += (f"Flags count as mines, so {game.mines - flagged_total} of the {game.mines} mines are not flagged yet. "
             f"Considering every placement of these mines that agrees with all the revealed numbers on the board, ")
    return text

def generate_question_and_answer(game, num, plot_level):
    """
    Randomly generate a question and answer related to the Minesweeper game state.
    """
    global last_random_coordinates, q4_used_cells  # Reference global variables

    question_types = [
        # StateInfo questions
        {"qa_type": "Target Perception", "template": "How many mines are currently flagged?", "difficulty": "Easy", "description": "Count flagged cells"},
        {"qa_type": "Target Perception", "template": "How many mines are left to be found?", "difficulty": "Easy", "description": "Calculate remaining mines"},
        {"qa_type": "Target Perception", "template": "How many cells have been revealed?", "difficulty": "Easy", "description": "Count revealed cells"},
        {"qa_type": "Target Perception", "template": "What is the state of the cell at ({row},{col})? (revealed number, hidden, flagged as mine)", "difficulty": "Easy", "description": "Check cell state"},

        # State prediction and strategy questions
        {"qa_type": "State Prediction", "template": "What will happen if the player reveals the cell at ({row},{col})?", "difficulty": "Hard", "description": "Predict cell reveal outcome"},
        {"qa_type": "Strategy Optimization", "template": "What is the best next move at ({row},{col})?", "difficulty": "Hard", "description": "Determine optimal move"},
    ]

    # Select the question based on num: each board asks q3 twice, q4 three times and q5 twice
    num = num % 10  # Ensure num is within the range of 0 to 9
    question_id = [0, 1, 2, 3, 3, 4, 4, 4, 5, 5][num]
    question_choice = question_types[question_id]

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
        # Only select cells at the boundary, a different one for each q4 call of the board
        if num == 5:
            q4_used_cells = []
        boundary_cells = [(cell["row"], cell["col"]) for cell in game.state_around()]
        unused_cells = [cell for cell in boundary_cells if cell not in q4_used_cells]
        if unused_cells:
            row, col = random.choice(unused_cells)
        elif boundary_cells:
            row, col = random.choice(boundary_cells)
        else:
            row, col = random.randint(0, game.rows - 1), random.randint(0, game.cols - 1)
        q4_used_cells.append((row, col))

        # Everything revealing the cell can show, over all mine layouts consistent with the board
        outcomes = reveal_outcomes(game, row, col)

        # Option C shows the number the cell hides; mines and empty cells get a random number from
        # 1 to 8 instead ("the number 0" would repeat option B, and no cell can show 9)
        actual_value = game.mine_board[row][col]
        value1 = actual_value if actual_value != 'M' and actual_value > 0 else random.randint(1, 8)

        # Construct question and options
        options = [
            f"A: The game will end because the cell contains a mine. ",
            f"B: The cell will reveal an empty area, and adjacent cells will also be revealed. ",
            f"C: The cell will reveal the number {value1}. ",
            f"D: Undecidable. The result cannot be determined from the current board."
        ]
        
        question = (
            question_prompt
            + f"**Question:** What will happen if the player reveals the cell at ({row},{col})? "
            + f"\n\n**Options:**\n" + "\n".join(options)
        )

        # Generate the answer based on the cell's state
        if game.flagged[row][col]:
            answer = "A"
            analysis = (
                f"The cell at ({row}, {col}) is flagged as a mine, which means it is known to contain a mine. "
                f"According to the rules of Minesweeper, revealing this cell(which contains a mine) will end the game. "
                f"Therefore, the correct answer is Option A."
            )
        elif outcomes == {"mine"}:
            answer = "A"
            analysis = describe_constraints(game, row, col) + (
                f"the cell at ({row},{col}) contains a mine in every placement, so revealing it will end the game. "
                f"Therefore, the correct answer is Option A."
            )
        elif outcomes == {0}:
            answer = "B"
            analysis = describe_constraints(game, row, col) + (
                f"the cell at ({row},{col}) is safe in every placement and none of its neighbors contains a mine, "
                f"so revealing it opens an empty area and the adjacent cells are revealed as well. "
                f"Therefore, the correct answer is Option B."
            )
        elif len(outcomes) == 1 and "mine" not in outcomes:
            number = next(iter(outcomes))
            answer = "C"
            analysis = describe_constraints(game, row, col) + (
                f"the cell at ({row},{col}) is safe in every placement and always has exactly {number} {'mine' if number == 1 else 'mines'} among its neighbors (flags included), "
                f"so revealing it will show the number {number}. "
                f"Therefore, the correct answer is Option C."
            )
        elif "mine" in outcomes:
            answer = "D"
            analysis = describe_constraints(game, row, col) + (
                f"the cell at ({row},{col}) contains a mine in some placements and is safe in others, "
                f"so the result of revealing it cannot be determined from the current board. "
                f"Therefore, the correct answer is Option D."
            )
        else:
            numbers = [str(n) for n in sorted(outcomes)]
            answer = "D"
            analysis = describe_constraints(game, row, col) + (
                f"the cell at ({row},{col}) is safe in every placement, but the number of mines around it can be "
                f"{', '.join(numbers[:-1])} or {numbers[-1]} depending on where the remaining mines are, "
                f"so the result of revealing it cannot be determined from the current board. "
                f"Therefore, the correct answer is Option D."
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

        # Generate the answer based only on visible state and logical inference
        if game.flagged[row][col]:
            # If the cell is flagged, select F
            answer = "F"
            analysis = (
                f"The cell at ({row},{col}) has already been flagged as a mine. "
                f"Therefore, no further action is needed for this cell (Option F), as it has already been marked as containing a mine, and the player should not attempt to reveal it."
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
        else:
            outcomes = reveal_outcomes(game, row, col)
            if outcomes == {"mine"}:
                answer = "A"
                analysis = describe_constraints(game, row, col) + (
                    f"the cell at ({row},{col}) contains a mine in every placement. "
                    f"The best move is to flag it as a mine (Option A)."
                )
            elif "mine" not in outcomes:
                answer = "B"
                analysis = describe_constraints(game, row, col) + (
                    f"the cell at ({row},{col}) is safe in every placement. "
                    f"The best move is to reveal this cell (Option B)."
                )
            else:
                answer = "D"
                analysis = describe_constraints(game, row, col) + (
                    f"the cell at ({row},{col}) contains a mine in some placements and is safe in others, so the visible board does not prove whether it is a mine or safe. "
                    f"In this case, it is better to skip this move and wait for more information (Option D)."
                )

    return qa_type, qa_level, question, question_id, question_description, answer, analysis, options
