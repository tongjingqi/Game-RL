# Ultra TicTacToe

## 代码使用

### requirements

```python
pygame
```

### 调整数据生成数量

1. 可在主函数中调整各个难度所生成的图片数量
2. 默认每张图片生成全部7种题目

### 局面复杂度与对应步数限制

```json
{
    "Easy": {"low": 10, "high": 34},
    "Medium": {"low": 35, "high": 59},
    "Hard": {"low": 60, "high": 81}
}
```



## 游戏基本信息

### 游戏类型

1. 全局信息不完全可知

2. 场景动态变化（有对手）

### 棋盘设置

$3 \times 3 = 9$个九宫格

![final_board](old_data/final_board.png)

### 落子规则

0. 先手：$\times$，后手：$\bigcirc$

1. 游戏开始时，先手在中间的九宫格中落子
2. **<u>双方每次落子在当前九宫格中的位置，决定对手下一次在哪个九宫格中落子</u>**



### 计分规则

任意一方在一个九宫格中达成1个“三连”（不能跨九宫格形成“三连”），得1分。



### 游戏结束规则

当每个九宫格的中心格都被填满时结束游戏，比较双方分值。



### 游戏介绍

现在我给你一张图片，它展示了一份Ultra TicTacToe的游戏截图。关于Ultra TicTacToe这个游戏的介绍如下：\n1. 棋盘与坐标表示：在本游戏中，棋盘分为9个3*3的九宫格。同时，我们用$(i, j, row, col)$表示一个格子的坐标：其中$(i, j)$表示九宫格的坐标；$(row, col)$表示九宫格内的坐标；$i, j, row, col$的范围均为1~3。两名玩家轮流在棋盘中放置棋子来标记棋盘中的格子，其中先手使用"X"，后手使用"O"（这点与传统的TicTacToe一样）。\n2. 落子规则：在游戏开始后，先手先在中间的九宫格（即九宫格(2, 2)）中任意一格放置一枚棋子，之后每次落子的九宫格坐标都与对手上次落子的九宫格内坐标相同；比如第1步先手在坐标(2, 2, 3, 1)处落子，那么第2步后手需要在九宫格(3, 1)中选择一个落子。\n3. 计分规则：对于每位玩家，在每个九宫格内，每有一个“三连”（即三个同样的棋子连成一条线，比如在同一行、同一列或者一条对角线上）计1分。每个九宫格内可以计不止1分。\n\n现在我会给你一道有关该游戏的题目，请你从我给你的图片中提取信息，仔细思考、推理并进行作答：\n

```
Now I'll give you a picture, which shows a screenshot of Ultra TicTacToe. The introduction of Ultra TicTacToe is as follows:\n1. Board and coordinate representation: In this game, the board is divided into 9 3*3 squares(called Nine-grids). At the same time, we use $(i, j, row, col)$ to represent the coordinates of a cell: $(i, j)$ represents the coordinates of the Nine-grid; $(row, col)$ represents the coordinate of the cell within the Nine-grid; $i, j, row, col$ all range from 1 to 3. Two players take turns placing pieces on the board to mark the cells on the board, with the first player using "X" and the second player using "O" (this is the same as traditional TicTacToe). \n2. Rules for placing chess pieces: After the game starts, the first player places a chess piece in any cell in the Nine-grid in the middle (i.e., the Nine-grid (2, 2)). After that, the coordinates of each chess piece placed in the Nine-grid are the same as the coordinates of the Nine-grid in which the opponent's last chess piece was placed; for example, if the first player places a chess piece at the coordinates (2, 2, 3, 1) in the first step, then the second player needs to choose a chess piece in the nine-square grid (3, 1) in the second step. \n3. Scoring rules: For each player, each "Straight" (i.e., three identical chess pieces connected in a line, such as in the same row, the same column, or a diagonal line) in each nine-square grid is counted as 1 point. More than 1 point can be counted in each nine-square grid. \n\nNow I will give you a question about the game. Please extract information from the picture I give you, think carefully, reason, and answer: \n
```



## 题目模版

### 具体题目

1. 询问某一格子的落子情况

   ```json
   {
       "qa_level": "Easy",
       "qa_type": "StateInfo",
       "question_id": 1,
       "question_description": "Find which player marked the cell at a given coordinate.",
       "question": game_explanation + " Which player marked the cell at {coord} in the image? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "{process} So, the answer is {option_number}.",
       "options": ["First Player", "Second Player", "Not Marked"]
   }
   ```

   其中{process}的格式如下：

   有棋子时

   ```
   There is a {piece} piece at {coord} in the image, which means it has been marked by {answer}.
   ```

   没棋子时

   ```
   There is no piece at {coord} in the image, which means it has not been marked by any player.
   ```

2. 给出当前对手的落子，询问下次落子可能坐标数量

   ```json
   {
       "qa_level": "Easy",
       "qa_type": "StateInfo",
       "question_id": 2,
       "question_description": "Given the coordinate of last step, find the number of possible coordinates of next step.",
       "question": game_explanation + " Now your opponent place a piece at {last_piece_coord}. What is the number of possible coordinates of your next step? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "Since the opponent placed a piece at {last_piece_coord}, our next step should be in the Nine-grid ({next_i}, {next_j}). In this nine grid, we can see that {coord_list_marked_by_X} are marked by the First Player, while {coord_list_marked_by_O} are marked by the Second Player. So, the possible coordinates are the rest cells in the Nine-grid, being {coord_avail_list}. This means there are {coord_avail_num} available coordinate(s), so the answer is {option_number}.",
       "options": []
   }
   ```

3. 询问当前棋盘中总共有有多少个中心格（即每个九宫格的(2, 2)）被占据

   ```json
   {
       "qa_level": "Easy",
       "qa_type": "StateInfo",
       "question_id": 3,
       "question_description": "Find the number of marked middle cells in the image.",
       "question": game_explanation + " How many middle cells in the image are marked? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "We check the middle cells in the Nine-grids one by one.\n{counting_process}\nSo there are {marked_middle_cell_num} middle cell(s) marked, the answer is {option_number}.",
       "options": []
   }
   ```

4. 询问当前棋盘中总共有多少个棋子

   ```json
   {
       "qa_level": "Medium",
       "qa_type": "StateInfo",
       "question_id": 4,
       "question_description": "Find the number of pieces in the image.",
       "question": game_explanation + " How many pieces are there in the image? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "We count the number of chess pieces in the Nine-grids one by one. {counting_process} So there are {adding_process} = {piece_num} pieces, the answer is {option_number}.",
       "options": []
   }
   ```

5. 询问给定九宫格中某一方的当前得分

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

6. 不标记当前的落子，只给定落子方，询问下一次落子需要在哪个九宫格（通过图片信息推理）

   ```json
   {
       "qa_level": "Hard",
       "qa_type": "StateInfo",
       "question_id": 6,
       "question_description": "Given the Player name, find in which Nine-grid to place the piece.",
       "question": game_explanation + " If you are {player_name}, from the image, we can see now it's your turn to place a piece. According to the rules of the game, in which Nine-grid should you place the next piece? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "Since we are the {player_name} now, we use the {your_piece} piece. First, we need to count the number of {your_piece} pieces in each Nine-grid.\n{counting_process_of_your_piece}\nThen, we need to count the number of {the_other_piece} pieces in each position of every Nine-grid.\n{counting_process_of_the_other_piece}\nSo the quantitative differences corresponding to these coordinates are {diff_list} respectively.\nFrom this difference, {supp_for_X}we can tell that our next step should be in {answer}, which means the answer is {option_number}.",
       "options": []
   }
   
   ```

   supp_for_X：

   ```
   plus the first chess piece is in the Nine-grid (2, 2) and there is no corresponding previous step O piece, 
   ```

7. 给出当前对手的落子，询问下次落子能使己方得分最高的坐标。（填空）（会用算法保证最高得分大于0，且得分最高的坐标唯一）

   ```json
   {
       "qa_level": "Hard",
       "qa_type": "StrategyOptimization",
       "question_id": 7,
       "question_description": "Given the coordinate of last step, find the coordinate to place the next piece to get the highest point.",
       "question": game_explanation + " Now your opponent place a piece at {last_piece_coord}. At which coordinate should you place your next piece to win the highest point?",
       "answer": "{max_coord}",
       "analysis": "Since the opponent placed a piece at {last_piece_coord}, our next step should be in the Nine-grid ({next_i}, {next_j}). In this Nine-grid, {avail_coord_num} coordinate(s) are available, and we count their points one by one. {counting_process} We can see that when choosing {max_coord}, the final point is the highest, being {max_point}. So, the answer is {max_coord}."
   }
   ```

8. 询问当前双方的总分之和（废弃）

9. 给出当前对手的落子，询问下次落子可能使对方有机会得分的所有坐标（废弃）



## 数据

### 坐标

$(i, j, row, col)$

1.  $(i, j)$表示九宫格的位置，范围为1~3
2.  $(row, col)$表示九宫格内的坐标，范围为1~3
3.  单独使用$(i, j)$时，前面加Nine-grid或者grid以示区分

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
