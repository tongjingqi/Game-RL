import json
import random
import os
from PIL import Image, ImageDraw, ImageFont
from game import TicTacToe

# 常量定义
DATASET_PATH = "tictactoe_dataset"
DATASET_NAME = "data.json"
COLOR_OPTIONS = ["A.red", "B.blue", "C.white"]
# CHESS_OPTIONS = ["A.None", "B.(0, 0)", "C.(0, 1)", "D.(0, 2)", 
#                "E.(1, 0)", "F.(1, 1)", "G.(1, 2)", 
#                "H.(2, 0)", "I.(2, 1)", "J.(2, 2)"]
CHESS_OPTIONS = ["A.None", "B.(0, 0)", "C.(0, 1)", "D.(0, 2)", 
               "E.(1, 0)", "F.(1, 1)", "G.(1, 2)", 
               "H.(2, 0) or (2, 1) or (2, 2)"]
PRINCIPLES = "Tic-Tac-Toe is a classic two-player game played on a 3x3 grid, (row, col) from (0, 0) to (2, 2). Players take turns marking a space in the grid, one using **O** (the red block) and the other using **X** (the blue block). In each game, player **O** starts first. The objective is to be the first to get three of your marks in a row (horizontally, vertically, or diagonally). If all nine squares are filled without either player achieving this, the game ends in a draw. Notice: the current player to make a move should be inferred from the number of pieces for each players on the board. When inferring the optimal move, if optimal move can be inferred by some rules, choose the optimal move. Otherwise, choose the first move. (The order of choices is (0, 0), (0, 1), (0, 2), (1, 0), ..., (2, 2), choose the first move that is not occupied)"


def create_directories():
   """Create directories for states and images"""
   os.makedirs(os.path.join(DATASET_PATH, "images"), exist_ok=True)
   os.makedirs(os.path.join(DATASET_PATH, "states"), exist_ok=True)

def count_pieces(board):
   """Count the number of 'O's and 'X's on the board"""
   o_count = sum(row.count("O") for row in board)
   x_count = sum(row.count("X") for row in board)
   return o_count, x_count

# def check_winner(board, player):
#    """Check if player has won"""
#    # Check rows
#    for row in board:
#        if all(cell == player for cell in row):
#            return True
#    # Check columns
#    for col in range(3):
#        if all(board[row][col] == player for row in range(3)):
#            return True
#    # Check diagonals
#    if all(board[i][i] == player for i in range(3)):
#        return True
#    if all(board[i][2 - i] == player for i in range(3)):
#        return True
#    return False

def check_winner(board, player):
    """Check if player has won and return the winning coordinates"""
    # Check rows
    for row in range(3):
        if all(board[row][col] == player for col in range(3)):
            return [(row, col) for col in range(3)]
    
    # Check columns
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return [(row, col) for row in range(3)]
    
    # Check first diagonal
    if all(board[i][i] == player for i in range(3)):
        return [(i, i) for i in range(3)]
    
    # Check second diagonal
    if all(board[i][2 - i] == player for i in range(3)):
        return [(i, 2 - i) for i in range(3)]
    
    return None

def is_board_full(board):
   """Check if board is full"""
   return all(cell != " " for row in board for cell in row)

def is_valid_move(board, row, col):
   """Check if the move is valid (position is empty)"""
   return 0 <= row < 3 and 0 <= col < 3 and board[row][col] == " "

def is_valid_board_state(board):
   """Check if the board state is valid according to game rules"""
   o_count, x_count = count_pieces(board)
   
   if o_count < x_count or o_count > x_count + 1:
       return False
       
   o_won = check_winner(board, "O")
   x_won = check_winner(board, "X")
   if o_won and x_won:
       return False
       
   if o_won and o_count != x_count + 1:
       return False
       
   if x_won and o_count != x_count:
       return False
       
   return True

def generate_random_board():
   """Generate a random valid board state following the rule that O moves first"""
   while True:
       board = [[" " for _ in range(3)] for _ in range(3)]
       empty_positions = [(row, col) for row in range(3) for col in range(3)]
       random.shuffle(empty_positions)

       current_player = "O"  # O always moves first
       num_moves = random.randint(0, 9)  # Random number of moves

       for _ in range(num_moves):
           if not empty_positions:
               break

           row, col = empty_positions.pop()
           board[row][col] = current_player

           if check_winner(board, current_player):
               break

           current_player = "X" if current_player == "O" else "O"

       if is_valid_board_state(board):
           return board

def generate_board_image(board, image_path):
    """Generate image representation of the board"""
    image_size = (300, 300)
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)

    line_color = "black"
    cell_size = 100

    # Fill cells with O/X colors
    for row in range(3):
        for col in range(3):
            cell_value = board[row][col]
            if cell_value != " ":
                # Determine cell color
                color = "red" if cell_value == "O" else "blue"
                # Calculate cell coordinates
                left = col * cell_size
                top = row * cell_size
                right = (col + 1) * cell_size
                bottom = (row + 1) * cell_size
                # Fill the cell
                draw.rectangle([left, top, right, bottom], fill=color)

    # Draw grid lines
    for i in range(1, 3):
        draw.line((i * cell_size, 0, i * cell_size, image_size[1]), fill=line_color, width=3)
        draw.line((0, i * cell_size, image_size[0], i * cell_size), fill=line_color, width=3)

    # Load fonts
    try:
        coords_font = ImageFont.truetype("font/arial.ttf", 25)
    except IOError:
        try:
            coords_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
        except IOError:
            try:
                coords_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 25)
            except IOError:
                coords_font = ImageFont.load_default()

    # Draw coordinates with black outline and white fill
    for i in range(3):
        # Column coordinates (top)
        x_col = i * cell_size + cell_size // 2 - 7
        y_col = 5
        text = str(i)
        # Draw black outline
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x_col + dx, y_col + dy), text, fill="black", font=coords_font)
        # Draw white center
        draw.text((x_col, y_col), text, fill="white", font=coords_font)

        # Row coordinates (left)
        x_row = 5
        y_row = i * cell_size + cell_size // 2 - 10
        # Draw black outline
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x_row + dx, y_row + dy), text, fill="black", font=coords_font)
        # Draw white center
        draw.text((x_row, y_row), text, fill="white", font=coords_font)

    image.save(image_path)

def save_state(board, output_path):
   """Save board state to JSON file"""
   with open(output_path, "w") as f:
       json.dump({"board": board}, f, indent=4)

def generate_questions(board, data_id):
   """Generate questions for the current board state"""
   game = TicTacToe()
   questions = []
   
   # Check game state
   game_over = False
   game_over_reason = ""
   o_won = check_winner(board, "O")
   x_won = check_winner(board, "X")
   if o_won:
      game_over = True
      game_over_reason = f"the player O wins in {o_won}"
   elif x_won:
      game_over = True
      game_over_reason = f"the player X wins in {x_won}"
   elif is_board_full(board):
      game_over = True
      game_over_reason = "the board is full and no one wins"

   # Determine current player
   o_count, x_count = count_pieces(board)
   current_player = "X" if o_count > x_count else "O"
   
   # Get AI suggestion
   ai_suggestion = game.get_ai_suggestion(board, current_player)

   # Generate StateInfo question
   row = random.randint(0, 2)
   col = random.randint(0, 2)
   cell_value = board[row][col]
   option = "A" if cell_value == "O" else "B" if cell_value == "X" else "C"
   color = "red" if cell_value == "O" else "blue" if cell_value == "X" else "white"
   
   current_player_reason = f"Since the player \"O\" plays first in each game, if the count of \"O\" is the same as \"X\", the current player is \"O\". Otherwise, the current player is \"X\". The count of \"O\" is {o_count} and the count of \"X\" is {x_count}, so the player now is {current_player}."

   questions.append({
       "data_id": f"tictactoe-mcq-{data_id}-StateInfo",
       "qa_type": "Target Perception",
       "question_id": 1,
       "question_description": "Questions about the current state of a specific block of the board.",
       "image": f"images/board_{data_id}.png",
       "state": f"states/board_{data_id}.json",
       "plot_level": ai_suggestion.level,
       "qa_level": "Easy",
       "question": f"Principles: {PRINCIPLES}\n\nQuestion: What is the color of the block at ({row}, {col})? \n\nOptions: {COLOR_OPTIONS}",
       "answer": option,
       "analysis": f"The current board is {board}. The block at ({row}, {col}) is \"{board[row][col]}\", and the color matching \"{board[row][col]}\" is {color}, so the block at ({row}, {col}) is {color}.",
       "options": COLOR_OPTIONS
   })

   # Generate StrategyOptimization question
   StrategyOptimization_description = "Questions about the optimal strategy to take a move of the current player of the board."
   if game_over:
       questions.append({
           "data_id": f"tictactoe-mcq-{data_id}-StrategyOptimization",
           "qa_type": "Strategy Optimization",
           "question_id": 2,
           "question_description": StrategyOptimization_description,
           "image": f"images/board_{data_id}.png",
           "state": f"states/board_{data_id}.json",
           "plot_level": ai_suggestion.level,
           "qa_level": "Medium",
           "question": f"Principles: {PRINCIPLES}\n\nQuestion: What is the optimal move for the current player? If no move exists, choose the answer \"None\".\n\nOptions: {CHESS_OPTIONS}",
           "answer": "A",
           "analysis": f"The current board is {board}. {current_player_reason} The game is already over, since {game_over_reason} in {game_over}. No valid move can be made.",
           "options": CHESS_OPTIONS
       })
   else:
       if ai_suggestion.options == "I" or ai_suggestion.options == "J": # 8 options at most
           ai_suggestion.options = "H"
       questions.append({
           "data_id": f"tictactoe-mcq-{data_id}-StrategyOptimization",
           "qa_type": "Strategy Optimization",
           "question_id": 2,
           "question_description": StrategyOptimization_description,
           "image": f"images/board_{data_id}.png",
           "state": f"states/board_{data_id}.json",
           "plot_level": ai_suggestion.level,
           "qa_level": "Medium",
           "question": f"Principles: {PRINCIPLES}\n\nQuestion: What is the optimal move for the current player? If no move exists, choose the answer \"None\".\n\nOptions: {CHESS_OPTIONS}",
           "answer": ai_suggestion.options,
           "analysis": f"The current board is {board}. {current_player_reason} " + ai_suggestion.reason,
           "options": CHESS_OPTIONS
       })

   # Generate ActionOutcome question
   test_row = random.randint(0, 2)
   test_col = random.randint(0, 2)
   ActionOutcome_question = f"Principles: {PRINCIPLES}\n\nQuestion: If the current player moves to ({test_row}, {test_col}), will this move be successful? If not, choose the answer \"None\". If successful, will the current player win immediately? If yes, choose the answer \"None\". otherwise, what is the opponent's optimal move following this step?\n\nOptions: {CHESS_OPTIONS}"
   ActionOutcome_description = "Questions about the outcome to take a specific move of the current player of the board, and the optimal strategy to take a move of the opponent player after the specific move."

   if game_over:
       questions.append({
           "data_id": f"tictactoe-mcq-{data_id}-ActionOutcome",
           "qa_type": "Strategy Optimization",
           "question_id": 3,
           "question_description": ActionOutcome_description,
           "image": f"images/board_{data_id}.png",
           "state": f"states/board_{data_id}.json",
           "plot_level": ai_suggestion.level,
           "qa_level": "Hard",
           "question": ActionOutcome_question,
           "answer": "A",
           "analysis": f"No, this move won't be successful. The current board is {board}. {current_player_reason} The game is already over, since {game_over_reason}. No valid move can be made.",
           "options": CHESS_OPTIONS
       })
   elif is_valid_move(board, test_row, test_col):
       # Simulate move and get opponent's response
       board[test_row][test_col] = current_player
       game_over = check_winner(board, current_player)
       opponent = "O" if current_player == "X" else "X"
       opponent_suggestion = game.get_ai_suggestion(board, opponent)
       board[test_row][test_col] = " "  # Restore board state
       if game_over:
            questions.append({
                "data_id": f"tictactoe-mcq-{data_id}-ActionOutcome",
                "qa_type": "Strategy Optimization",
                "question_id": 3,
                "question_description": ActionOutcome_description,
                "image": f"images/board_{data_id}.png",
                "state": f"states/board_{data_id}.json",
                "plot_level": ai_suggestion.level,
                "qa_level": "Hard",
                "question": ActionOutcome_question,
                "answer": "A",
                "analysis": f"Yes, this move will be successful. The current board is {board}. {current_player_reason} Since the current player {current_player} moves to ({test_row}, {test_col}), the current player will win immediately in {game_over}.",
                "options": CHESS_OPTIONS
            })
       else:
            if opponent_suggestion.options == "I" or opponent_suggestion.options == "J": # 8 options at most
                opponent_suggestion.options = "H"
            questions.append({
                "data_id": f"tictactoe-mcq-{data_id}-ActionOutcome",
                "qa_type": "Strategy Optimization",
                "question_id": 3,
                "question_description": ActionOutcome_description,
                "image": f"images/board_{data_id}.png",
                "state": f"states/board_{data_id}.json",
                "plot_level": ai_suggestion.level,
                "qa_level": "Hard",
                "question": ActionOutcome_question,
                "answer": opponent_suggestion.options,
                "analysis": f"Yes, this move will be successful. The current board is {board}. {current_player_reason} Since the current player {current_player} moves to ({test_row}, {test_col}), the current player won't win immediately. after that, {opponent_suggestion.reason}",
                "options": CHESS_OPTIONS
            })
   else:
       questions.append({
           "data_id": f"tictactoe-mcq-{data_id}-ActionOutcome",
           "qa_type": "Strategy Optimization",
           "question_id": 3,
           "question_description": ActionOutcome_description,
           "image": f"images/board_{data_id}.png",
           "state": f"states/board_{data_id}.json",
           "plot_level": ai_suggestion.level,
           "qa_level": "Hard",
           "question": ActionOutcome_question,
           "answer": "A",
           "analysis": f"No, this move won't be successful. The current board is {board}. {current_player_reason} Since the position ({test_row}, {test_col}) is already occupied, no valid move can be made.",
           "options": CHESS_OPTIONS
       })

   return questions

def generate_dataset(num_states):
   """Generate the complete dataset"""
   dataset = []
   create_directories()

   for i in range(num_states):
       print(f"Generating data entry {i + 1}")
       
       # Generate random board
       board = generate_random_board()
       
       # Generate and save board image
       image_path = os.path.join(DATASET_PATH, f"images/board_{i + 1}.png")
       generate_board_image(board, image_path)
       
       # Save board state
       state_path = os.path.join(DATASET_PATH, f"states/board_{i + 1}.json")
       save_state(board, state_path)
       
       # Generate questions
       questions = generate_questions(board, i + 1)
       dataset.extend(questions)

   # Save complete dataset
   dataset_path = os.path.join(DATASET_PATH, DATASET_NAME)
   with open(dataset_path, "w") as f:
       json.dump(dataset, f, indent=4)

if __name__ == "__main__":
   import argparse
   
   parser = argparse.ArgumentParser(description="Generate TicTacToe dataset")
   parser.add_argument("--num", type=int, default=10, 
                     help="Number of board states to generate (default: 10)")
   args = parser.parse_args()
   
   generate_dataset(args.num)