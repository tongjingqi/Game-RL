# Rhythm Game

## 代码使用

可以在主函数中调整各个难度需要的图片数量

代码保存路径：`data.json`

需要下载`pygame`模块



## 游戏类型

1. 全局信息可知

2. 场景动态变化
   1. 下落式音游，方块会随时间下落
   2. 与传统音游的差异：添加玩家与场景的交互



### 游戏描述

现在我给你一张图片，它展示了一份音乐游戏的截图，其中有各种颜色的操作块。在本游戏中，操作块会以1格/s的速度进行下落。同时，你可以选定某一列放置你的手指（在选定后不能移动手指），点击该列中下落到第1行的操作块以得分（当然你也可以选择不点击任何一列，这不会影响操作块的下落）。\n对于操作块，我们将其分为3类，包括单点块、反转块、和蛇块，具体如下：\n1. 单点块是黄色的，占据1格，点击可以获得10分。\n2. 反转块是绿色的，占据1格，点击可以获得15分。需要注意的是，在你点击反转块后，整个游戏的局面会**左右反转**，但是你的手指位置**不会**随之改变。\n3. 蛇块占据一列中连续的2格或更多格，它的第一格（称为蛇头块）是粉色的，最后一格（称为蛇尾块）是灰色的，中间的格子(称为蛇身块，如果有的话)是蓝色的。只有当你点击蛇块占据的**所有格子**后，你才能得分，得分值与蛇块的长度$l$(包括首尾)有关，具体得分为$l \cdot (2l + 7)$。\n现在我会给你一道有关该游戏的题目，请你从我给你的图片中提取信息，仔细思考、推理并进行作答：\n



## 改变

与传统音游的差异：**<u>需要加入决策点</u>**

1. 调整玩家与游戏的交互：
   1. 玩家的点击 -> **<u>选出一列点击</u>**
   2. **<u>反转块的点击会左右翻转整个场景</u>**，可以在某些题目中添加难度
      1. ps：点击反转块后，选择的列不反转，但是格子会反转



## 方块设置

|        |             描述              |           颜色           |        分值        |
| :----: | :---------------------------: | :----------------------: | :----------------: |
| 单点块 |             占1格             |           黄色           |         10         |
| 反转块 | 占1格，点击会左右翻转整个场景 |           绿色           |         15         |
|  蛇快  |   同一列上最长5格，最短2格    | 头粉色，尾灰色，中间蓝色 | $l \cdot (2l + 7)$ |



## 问题模板

1. 当前图中某格属于哪种块

   ```json
   {
       "qa_level": "Easy",
       "qa_type": "StateInfo",
       "question_id": 1,
       "question_description": "Find the type of the block in a given coordinate.",
       "question": game_explanation + " Which type of block does row {row} and column {col} in the image belong to? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "The cell at row {row} and column {col} in the image is {block_color}, which means it is a {block_type} block. So, the answer is {option_number}",
       "options": ["Non-type", "Click", "Reverse", "Snake Head", "Snake Body", "Snake Tail"]
   }
   ```

2. 当前图中被操作块占据的格子占比多少，答案保留3位小数（填空题）

   ```json
   {
       "qa_level": "Easy",
       "qa_type": "StateInfo",
       "question_id": 2,
       "question_description": "Find the percentage of cells with blocks, retaining 3 significant figures.",
       "question": game_explanation + " What percentage of the grid in the current image is occupied by the operation blocks? The answer is expressed as a decimal, retaining 3 significant figures.",
       "answer": "{current_answer}",
       "analysis": "There are {row_num} rows and {col_num} columns in the grid, which means there are {row_num} * {col_num} = {cell_num} cells in total. {counting_row_cells}\nIn total, there are {adding_blocks} = {blocked_cell_num} cells occupied by blocks in the image. So, the answer is {blocked_cell_num} / {cell_num} = {current_answer}"
   }
   ```

3. 在不选择任何一列点击的情况下，$k$秒后，以$(x_0, y_0)$为首（即最下端）的蛇块长度是多少（蛇块长度为2~5）

   ```json
   {
       "qa_level": "Medium",
       "qa_type": "ActionOutcome",
       "question_id": 3,
       "question_description": "Find the length of Snake block headed by a given coordinate after given sconds.",
       "question": game_explanation + " Without selecting any column to click, what is the length of the snake block headed (which means being the lower end) by {head_position_after} after {time} second(s)? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "Because the blocks fall at the speed of 1 cell/second, before {time} second(s), the head cell of that Snake block should be at {head_position_before}. From the image we can see that the Snake block starts from {head_position_before} occupies {length} cells. So, the answer is {option_number}",
       "options": ["2", "3", "4", "5"]
   }
   ```

4. 选择某列点击时最终得分多少

   ```json
   {
       "qa_level": "Medium",
       "qa_type": "ActionOutcome",
       "question_id": 4,
       "question_description": "Find the final point of choosing a given column to click.",
       "question": game_explanation + " While selecting column {select_col} to click, how many points will you get? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "We count from bottom to top.\n{counting_procedure}So, the final point is {adding_points} = {final_point}, the answer is {option_number}",
       "options": []
   }
   ```

5. 在反转块耗时2格时，选择某列点击最终得分多少

   ```json
   {
       "qa_level": "Medium",
       "qa_type": "ActionOutcome",
       "question_id": 5,
       "question_description": "Find the final point of choosing a given column to click when it takes 1 second to reverse the grid.",
       "question": game_explanation + " Now it takes 1 second to reverse the grid, during which the blocks will still be falling, but you can't click them. While selecting column {select_col} to click, how many points will you get? Options: {option_list}",
       "answer": "{option_number}",
       "analysis": "We count from bottom to top.\n{counting_procedure}So, the final point is {adding_points} = {final_point}, the answer is {option_number}",
       "options": []
   }
   ```

6. 选择哪列最终得分最高

   ```json
   {
       "qa_level": "Hard",
       "qa_type": "StrategyOptimization",
       "question_id": 6,
       "question_description": "Find choosing which column to click can get the highest score.",
       "question": game_explanation + " Which column(s) should I choose to click to get the highest final score? Options: {option_list}",
       "answer": "{option_numbers}",
       "analysis": "{counting_procedure}We can see that when choosing column(s) {max_col}, the final point is the highest, being {max_point}. So, the answer is {option_numbers}",
       "options": []
   }
   ```

7. 在反转块耗时2格时，选择哪列最终得分最高

   ```json
   {
       "qa_level": "Hard",
       "qa_type": "StrategyOptimization",
       "question_id": 7,
       "question_description": "Find choosing which column to click can get the highest score when it takes 1 second to reverse the grid.",
       "question": game_explanation + " Now it takes 1 second to reverse the grid, during which the blocks will still be falling, but you can't cilck them. Which column(s) should I choose to click to get the highest final score? Options: {option_list}",
       "answer": "{option_numbers}",
       "analysis": "{counting_procedure}We can see that when choosing column(s) {max_col}, the point is the highest, being {max_point}. So, the answer is {option_numbers}",
       "options": []
   }
   ```

ps: 第6/7题可能会有多解



## 代码解释

1. 目前设置是3种块的总块数（并不是占用格数）是表格总格数的1/2，使得最终占用格数略多于总格数的1/2
2. 3种操作块的比例可以自定义（目前单:反:蛇 = 7:4:3），但是蛇块的比例不宜过高，会使得占用格数过高
3. ```json
   {
       "Easy": {
           "row_num": 15,
   		"col_num": 4
       },
       "Medium": {
           "row_num": 15,
   		"col_num": 6
       },
       "Hard": {
           "row_num": 20,
   		"col_num": 6
       }
   }
   ```

   



## 数据部分展示

### 游戏描述

```
Now I'll give you a picture, which shows a screenshot of a rhythm game, in which there are operation blocks of various colors. In this game, the operation blocks will fall at a speed of 1 cell/second. At the same time, you can select a column to place your finger (you cannot move your finger after selecting it), and click the operation blocks in the column that fall to the first row to score points (of course, you can also choose not to click any column, which will not affect the falling of the operation blocks). \nFor the operation blocks, we divide them into 3 categories, including Click blocks, Reverse blocks, and Snake blocks, as follows: \n1. Click blocks are yellow, occupy 1 cell, and you can get 10 points by clicking them. \n2. Reverse blocks are green, occupy 1 cell, and you can get 15 points by clicking them. It should be noted that after you click the Reverse block, the entire game situation will **reverse left and right**, but your finger position **will not** change accordingly. \n3. A Snake block occupies 2 or more consecutive cells in a column, and its first cell (called Snake Head block) is pink, its last cell (called Snake Tail block) is grey, and the middle cells (called Snake Body blocks, if any) are blue. Only when you click on **all cells** occupied by the snake block can you score points. The score is related to the length $l$ (including the head and tail) of the snake block. The specific score is $l \cdot (2l + 7)$. \nNow I will give you a question about the game. Please extract information from the picture I give you, think carefully, reason and answer: \n
```



### state

```json
{
    "rows": 15,
    "cols": 4,
    "blocked_cell_num": 48,
    "block_info": [
        {
            "row": 4,
            "col": 2,
            "color": "pink"
        },
        ...
    ]
}
```



### image

![board_00001](old_data/images/board_00001.png)
