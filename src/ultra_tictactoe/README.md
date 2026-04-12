# Ultra TicTacToe

## Code Usage

### requirements

```python
pygame
```

### Adjust the amount of generated data

1. You can adjust the number of images generated for each difficulty in the main function.
2. By default, each image generates all 7 question types.

### Board complexity and corresponding step limits

```json
{
    "Easy": {"low": 10, "high": 34},
    "Medium": {"low": 35, "high": 59},
    "Hard": {"low": 60, "high": 81}
}
```



## Basic Game Information

### Game Type

1. Global information is not fully observable

2. The scene changes dynamically (there is an opponent)

### Board Setup

$3 \times 3 = 9$ Nine-grids

![final_board](old_data/final_board.png)

### Piece Placement Rules

0. First player: $\times$, second player: $\bigcirc$

1. At the start of the game, the first player places a piece in the middle Nine-grid
2. **<u>The position played in the current Nine-grid determines which Nine-grid the opponent must play in next</u>**



### Scoring Rules

Whenever either player makes one "three in a row" within a Nine-grid (three in a row cannot cross Nine-grids), that player gets 1 point.



### End Rule

The game ends when the center cell of every Nine-grid has been filled. Then the two players' scores are compared.



### Game Introduction

Now I give you an image showing a screenshot of Ultra TicTacToe. The introduction to Ultra TicTacToe is as follows:\n1. Board and coordinate representation: in this game, the board is divided into 9 3*3 Nine-grids. At the same time, we use $(i, j, row, col)$ to represent the coordinates of a cell: $(i, j)$ represents the coordinates of the Nine-grid; $(row, col)$ represents the coordinates within a Nine-grid; $i, j, row, col$ all range from 1 to 3. Two players take turns placing pieces on the board to mark cells, with the first player using "X" and the second player using "O" (just like traditional TicTacToe).\n2. Placement rules: after the game starts, the first player first places a piece in any cell of the middle Nine-grid (that is, Nine-grid (2, 2)). After that, the coordinates within the Nine-grid of each move determine the coordinates of the Nine-grid in which the opponent must move next. For example, if on move 1 the first player places a piece at (2, 2, 3, 1), then on move 2 the second player must choose a move in Nine-grid (3, 1).\n3. Scoring rules: for each player, in each Nine-grid, every "three in a row" (that is, three identical pieces connected in a line, such as in the same row, the same column, or one diagonal) counts as 1 point. More than 1 point can be scored within one Nine-grid.\n\nNow I will give you a question about this game. Please extract information from the image, think carefully, reason, and answer:\n

```
Now I'll give you a picture, which shows a screenshot of Ultra TicTacToe. The introduction of Ultra TicTacToe is as follows:\n1. Board and coordinate representation: In this game, the board is divided into 9 3*3 squares(called Nine-grids). At the same time, we use $(i, j, row, col)$ to represent the coordinates of a cell: $(i, j)$ represents the coordinates of the Nine-grid; $(row, col)$ represents the coordinate of the cell within the Nine-grid; $i, j, row, col$ all range from 1 to 3. Two players take turns placing pieces on the board to mark the cells on the board, with the first player using "X" and the second player using "O" (this is the same as traditional TicTacToe). \n2. Rules for placing chess pieces: After the game starts, the first player places a chess piece in any cell in the Nine-grid in the middle (i.e., the Nine-grid (2, 2)). After that, the coordinates of each chess piece placed in the Nine-grid are the same as the coordinates of the Nine-grid in which the opponent's last chess piece was placed; for example, if the first player places a chess piece at the coordinates (2, 2, 3, 1) in the first step, then the second player needs to choose a chess piece in the nine-square grid (3, 1) in the second step. \n3. Scoring rules: For each player, each "Straight" (i.e., three identical chess pieces connected in a line, such as in the same row, the same column, or a diagonal line) in each nine-square grid is counted as 1 point. More than 1 point can be counted in each nine-square grid. \n\nNow I will give you a question about the game. Please extract information from the picture I give you, think carefully, reason, and answer: \n
```



## Question Templates

### Specific Questions

1. Ask about the piece status of a certain cell

   ```json
   {
       "qa_level": "Easy",
       "qa_type": "Target Perception",
       "question_id": 1,
       "question_description": "Find which player marked the cell at a given coordinate.",
       "question": game_explanation + " Which player marked the cell at {coord} in the image? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "{process} So, the answer is {option_number}.",
       "options": ["First Player", "Second Player", "Not Marked"]
   }
   ```

   The format of `{process}` is as follows:

   If there is a piece:

   ```
   There is a {piece} piece at {coord} in the image, which means it has been marked by {answer}.
   ```

   If there is no piece:

   ```
   There is no piece at {coord} in the image, which means it has not been marked by any player.
   ```

2. Given the opponent's current move, ask for the number of possible coordinates for the next move

   ```json
   {
       "qa_level": "Easy",
       "qa_type": "Target Perception",
       "question_id": 2,
       "question_description": "Given the coordinate of last step, find the number of possible coordinates of next step.",
       "question": game_explanation + " Now your opponent place a piece at {last_piece_coord}. What is the number of possible coordinates of your next step? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "Since the opponent placed a piece at {last_piece_coord}, our next step should be in the Nine-grid ({next_i}, {next_j}). In this nine grid, we can see that {coord_list_marked_by_X} are marked by the First Player, while {coord_list_marked_by_O} are marked by the Second Player. So, the possible coordinates are the rest cells in the Nine-grid, being {coord_avail_list}. This means there are {coord_avail_num} available coordinate(s), so the answer is {option_number}.",
       "options": []
   }
   ```

3. Ask how many center cells on the current board (that is, each Nine-grid's (2, 2)) are occupied

   ```json
   {
       "qa_level": "Easy",
       "qa_type": "Target Perception",
       "question_id": 3,
       "question_description": "Find the number of marked middle cells in the image.",
       "question": game_explanation + " How many middle cells in the image are marked? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "We check the middle cells in the Nine-grids one by one.\n{counting_process}\nSo there are {marked_middle_cell_num} middle cell(s) marked, the answer is {option_number}.",
       "options": []
   }
   ```

4. Ask how many total pieces are on the current board

   ```json
   {
       "qa_level": "Medium",
       "qa_type": "Target Perception",
       "question_id": 4,
       "question_description": "Find the number of pieces in the image.",
       "question": game_explanation + " How many pieces are there in the image? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "We count the number of chess pieces in the Nine-grids one by one. {counting_process} So there are {adding_process} = {piece_num} pieces, the answer is {option_number}.",
       "options": []
   }
   ```

5. Ask for the current score of a given player in a given Nine-grid

   ```json
   {
       "question_id": 5,
       "question_description": "Find the points the given player has got within the given Nine-grid.",
       "question": game_explanation + " How many points has the {player_name} got within the Nine-grid {nine_grid_coord}? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "The {player_name} uses {piece} pieces. We count the points in the order of rows, columns, and diagonals. We can see that in Nine-grid {nine_grid_coord}, there are {point_row} point(s) in rows, {point_col} point(s) in columns, and {point_diag} point(s) in diagonals, which is {point} point(s) in total. So, the answer is {option_number}.",
       "options": []
   }
   ```

6. Without marking the current move, only give the player name and ask in which Nine-grid the next move must be placed, inferred from the image

   ```json
   {
       "qa_level": "Hard",
       "qa_type": "Target Perception",
       "question_id": 6,
       "question_description": "Given the Player name, find in which Nine-grid to place the piece.",
       "question": game_explanation + " If you are {player_name}, from the image, we can see now it's your turn to place a piece. According to the rules of the game, in which Nine-grid should you place the next piece? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "Since we are the {player_name} now, we use the {your_piece} piece. First, we need to count the number of {your_piece} pieces in each Nine-grid.\n{counting_process_of_your_piece}\nThen, we need to count the number of {the_other_piece} pieces in each position of every Nine-grid.\n{counting_process_of_the_other_piece}\nSo the quantitative differences corresponding to these coordinates are {diff_list} respectively.\nFrom this difference, {supp_for_X}we can tell that our next step should be in {answer}, which means the answer is {option_number}.",
       "options": []
   }
   
   ```

   `supp_for_X`:

   ```
   plus the first chess piece is in the Nine-grid (2, 2) and there is no corresponding previous step O piece, 
   ```

7. Given the opponent's current move, ask which coordinate for the next move gives the highest score for our side. (fill-in-the-blank) The algorithm guarantees that the highest score is greater than 0 and the best coordinate is unique.

   ```json
   {
       "qa_level": "Hard",
       "qa_type": "Strategy Optimization",
       "question_id": 7,
       "question_description": "Given the coordinate of last step, find the coordinate to place the next piece to get the highest point.",
       "question": game_explanation + " Now your opponent place a piece at {last_piece_coord}. At which coordinate should you place your next piece to win the highest point?",
       "answer": "{max_coord}",
       "analysis": "Since the opponent placed a piece at {last_piece_coord}, our next step should be in the Nine-grid ({next_i}, {next_j}). In this Nine-grid, {avail_coord_num} coordinate(s) are available, and we count their points one by one. {counting_process} We can see that when choosing {max_coord}, the final point is the highest, being {max_point}. So, the answer is {max_coord}."
   }
   ```

8. Ask for the sum of the total scores of both players (abandoned)

9. Given the opponent's current move, ask for all coordinates that could give the opponent a chance to score next (abandoned)



## Data

### Coordinates

$(i, j, row, col)$

1. $(i, j)$ represents the position of the Nine-grid, ranging from 1 to 3
2. $(row, col)$ represents the coordinates within the Nine-grid, ranging from 1 to 3
3. When using $(i, j)$ alone, add `Nine-grid` or `grid` before it to distinguish it

### State Example

```json
{
    "rows": 3,
    "cols": 3,
    "middle_cell_count": 6,
    "last_step": [
        3,
        3,
        3,
        1
    ],
    "best_next_step": [
        3,
        1,
        1,
        1
    ],
    "total_steps": 60,
    "piece_info": [
        {
            "nine_grid": "(1, 1)",
            "position": "(3, 1)",
            "type": "X"
        },
        ...
        {
            "nine_grid": "(3, 3)",
            "position": "(3, 1)",
            "type": "O"
        }
    ]
}
```
