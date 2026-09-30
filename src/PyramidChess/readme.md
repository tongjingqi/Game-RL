# Pyramid Chess
## Overview
The PyramidChess Dataset is a specialized dataset derived from the 3D strategy game PyramidChess, designed to support research in computer vision, natural language processing, and game-state understanding. Each data entry represents a specific game scenario, captured as a 3D game-state image, accompanied by structured question-answer pairs. There are six specific questions spanning three distinct types (e.g., Target Perception, State Prediction, and Strategy Optimization), each designed to probe strategic reasoning and spatial understanding.

In addition to the questions, the dataset provides detailed analyses and accurate answers, offering insights into the reasoning process behind each solution. By combining rich game-state imagery with comprehensive QA pairs and explanations, the PyramidChess Dataset serves as a tool for advancing AI research in spatial reasoning, strategy modeling, and explainable decision-making.

## Game Rule

```
Pyramid Chess Rules:
0.Game Board:
The game board is square and comes in various sizes: 3x3, 4x4, or 5x5. On an nxn board, there are n levels (0 to n-1). At each level k, the x and y coordinates range from 0 to n-1-k, resulting in (n-k)**2 slots per level. The slots in the lower levels act as the base for the slots in the upper levels. Slots at level 0 have no base, while slots at level j (j!=0) with coordinates (a,b) are supported by four base slots (a,b),(a+1,b),(a,b+1),(a+1,b+1) from level j-1.
1.Players and Initial Setup:
The game is played between two players, designated as PLAYER_0 and PLAYER_1, each using balls of a distinct color from their color pool. Players take turns placing their balls on a square game board. The number of balls available to each player depends on the size of the board: on a 3x3 board, each player has 7 balls; on a 4x4 board, each has 15 balls; and on a 5x5 board, PLAYER_0 (the first player to place a ball) has 28 balls, while PLAYER_1 has 27 balls.
2.Placing Balls and Creating New Slots:
At the start of the game, the lowest level of the board (Level 0) is completely open and balls can be placed in any available slot on this level. After a ball is placed in a slot, that slot is no longer available for placing another ball. A ball can only be placed on the upper level if it is supported by a fully completed 2x2 block of balls on the level directly beneath. All four slots in the 2x2 block must be filled for the upper ball to be placed.
3.Take-back mechanism:
If a player places a ball that completes a 2x2 block of the same color (all four balls belonging to that player), they may return up to two balls from the block to their color pool. A ball can only be removed if it does not have another ball directly above it, as removing a "base" ball would collapse the pyramid. Returning a ball reopens the slot it occupied, allowing it to be used for future placements, but the rule requiring a full 2x2 block as a base for placing balls on upper levels still applies. 
4.Winning the Game:
The game ends when one player successfully places the last ball on top of the pyramid. The player who places the ball on the top of the pyramid wins.
```

## Project Structure

The project is structured to efficiently generate the PyramidChess dataset through a modular workflow. The main entry point is main.py, which serves as the user interface, handling input and orchestrating the dataset generation process. It imports pyramidchess_data_generate, the core module responsible for creating dataset entries. This module relies on two additional components: pyramidchess_board_generate, which constructs valid game states adhering to PyramidChess rules, and pyramidchess_image_generate, which transforms these game states into 3D board images. Together, these modules produce comprehensive dataset entries that include 3D images, questions, analyses, and answers.

main.py (User Interface)
    |
    v
pyramidchess_data_generate (Dataset Generation)
    |
    +--> pyramidchess_image_generate (Image Generation)
    |                |
    |                v
    +--> pyramidchess_board_generate (Game State Creation)

## Output Contents/Dataset

### state

```json
{
    "0": [
        ["--","P0","--"],
        ["P0","--","P1"],
        ["--","P1","--"]
    ],
    "1": [
        ["--","--"],
        ["--","--"]
    ],
    "2": [
        ["--"]
    ]
}
```



### image

![board_00000](pyramidchess_dataset_example/images/board_00000.png)

### [data.json](pyramidchess_dataset_example/data.json)

## Supported Question Types 

1. Choose a random coordinate and ask what status is the coordinate. （question_id:0）

   ```json
   {
       "qa_type": "Target Perception",
       "qa_level": "Easy",
       "question": "Question: What is the status of the ball on Level 1, which has coordinate [1, 1]?\nOptions:\n1. PLAYER_0\n2. PLAYER_1\n3. Empty\n4. Index out of bound",
       "answer": 2,
       "analysis": "From the image provided, we can recognize that the board is a 3x3 board. We can observe the layout of the pyramid across its levels. Based on level 1's grid (specifically at coordinate [1, 1]), the ball is red, which corresponds to PLAYER_1.",
       "options": [
           "PLAYER_0",
           "PLAYER_1",
           "Empty",
           "Index out of bound"
       ]
   }
   ```

2. Select a coordinate and determine whether a ball can be placed at this coordinate. If so, what would happen after the ball is placed.（question_id:1）

   ```json
   {
       "qa_type": "State Prediction",
       "qa_level": "Medium",
       "question": "Question: Can a ball be placed at coordinate [2, 2] on Level 0? If a red ball is placed there, what would be the outcome?\nOptions:\n1. Can place and no balls taken\n2. Can place and then balls can be taken\n3. Cannot place, position already occupied\n4. Cannot place, ball not ready below",
       "answer": 3,
       "analysis": "From the image provided, we can recognize that the board is a 3x3 board. The coordinate [2, 2] on level 0 is already occupied by a red ball, so it is not possible to place a ball there. Therefore, the status is: Cannot place, position already occupied.",
       "options": [
           "Can place and no balls taken",
           "Can place and then balls can be taken",
           "Cannot place, position already occupied",
           "Cannot place, ball not ready below"
       ]
   }
   ```

3. Calculate how many steps (turns) are required for a ball to be placed at certain coordinate.(Including the step putting the ball at the coordinate)（question_id:2）

   ```json
   {
       "qa_type": "State Prediction",
       "qa_level": "Hard",
       "question": "Question: How many steps (turns) are required for a ball to be placed at coordinate [0, 0] on Level 2? (including the turn placing the ball)",
       "answer": "2",
       "analysis": "From the image provided, we can recognize that the board is a 3x3 board. To place a ball at coordinate [0, 0] on Level 2, we need to ensure all the balls in its sub-pyramid, which are the balls supporting the position, are placed.\nThis is determined by checking each level below the target position, from the highest level below it to the base level, and counting how many balls that support the position are missing in each layer. The steps needed are the missing balls plus the turn placing the ball at the target position.\nLevel 1: 1 more ball(s) need to be placed at [[1, 0]].\nOnce all the required balls in the sub-pyramid are placed, the ball at the target position can be placed.\nTherefore, it needs 2 steps in total."
   }
   ```

4. Give out the best position to put the ball at a certain point of a game.（question_id:3）

   ```json
   {
       "qa_type": "Strategy Optimization",
       "qa_level": "Hard",
       "question": "It is PLAYER_0's turn (which uses the blue ball). What is the best coordinate to put a ball in order to maximize the opportunity of winning? Please answer in the form of \"[x, y] at level z\".",
       "answer": "[0, 1] at level 0",
       "analysis": "From the image provided, we can recognize that the board is a 3x3 board. To maximize the winning chance, one must try his best to form a 2x2 block of his color for the take-back mechanism, so that he avoids losing balls in his turn and therefore minimizes the chance of running out of balls first. Blocking the opponent's chance to form a 2x2 block of his color also increases the opportunity of winning. From the question, it is PLAYER_0's turn now, who uses the blue ball. Putting a blue ball at [0, 1] at Level 0 stops the other player PLAYER_1 from forming a 2x2 block of red at [[0, 0], [1, 0], [1, 1], [0, 1]]. So the answer is [0, 1] at level 0."
   }
   ```

5. Calculate how many balls are there on the board.（question_id:4）

   ```json
   {
       "qa_type": "Target Perception",
       "qa_level": "Easy",
       "question": "Question: How many balls are there on the board in the image?",
       "answer": "12",
       "analysis": "From the image provided, we can recognize that the board is a 3x3 board. To count the total number of balls on the board, we start from the downmost level and proceed upward. For each level, we use the 2D representation of that level to count the balls row by row and column by column. Here is the detailed count:\nLevel 0 contains 9 ball(s):\nA red ball at (0, 0).\nA blue ball at (0, 1).\nA red ball at (0, 2).\nA red ball at (1, 0).\nA blue ball at (1, 1).\nA red ball at (1, 2).\nA blue ball at (2, 0).\nA red ball at (2, 1).\nA blue ball at (2, 2).\nLevel 1 contains 3 ball(s):\nA blue ball at (0, 1).\nA blue ball at (1, 0).\nA red ball at (1, 1).\nLevel 2 contains 0 ball(s):\n\nFrom the image provided, the total number of balls on the board is 12.\n"
   }
   ```

6. Provide the higher level status of a coordinate: Is the coordinate legal? Does it contain a ball? Can the ball be taken? Can a ball be placed?（question_id:5）

   ```json
   {
       "qa_type": "Target Perception",
       "qa_level": "Medium",
       "question": "Question: What is the status of the ball on Level 0, which has coordinate [2, 0]?\nIs the coordinate legal? Does it contain a ball? Can the ball be taken (has no ball directly above it)? Can a ball be placed?\nOptions:\n1. The coordinate is out of bound\n2. It contains a ball and the ball can't be taken\n3. It contains a ball and the ball can be taken\n4. It doesn't contain a ball and the player can put a ball here this turn\n5. It doesn't contain a ball and the player can't put a ball here this turn",
       "answer": 3,
       "analysis": "From the image provided, we can recognize that the board is a 3x3 board. From the image provided, there is a ball at the coordinate [2, 0] in level 0. And there is no ball sitting above the ball, which means the ball isn't supporting other balls, so when a take-back happens, the ball can be taken without collapsing the pyramid. Therefore, the status is: it contains a ball and the ball can be taken.",
       "options": [
           "The coordinate is out of bound",
           "It contains a ball and the ball can't be taken",
           "It contains a ball and the ball can be taken",
           "It doesn't contain a ball and the player can put a ball here this turn",
           "It doesn't contain a ball and the player can't put a ball here this turn"
       ]
   }
   ```

## How to use
Install Dependencies:
Run the following command to install the required dependencies:
`pip install -r requirements.txt`

Run the Project:
Navigate to the PyramidChess directory and execute:
`python main.py -n 5000`

The -n argument specifies the number of data entries to generate. To change the number of entries, modify the value after -n.

Customize Data Generation:
Use -q and -l to selectively generate specific question types and difficulty levels. For example:
`python main.py -n 10 -q 0,1,5 -l Medium,Hard`

This command generates 10 entries with question types 0, 1, and 5, and difficulty levels "Medium" and "Hard".

Add -p Random to shuffle the dataset:
`python main.py -n 100 -p Random`

Set Starting ID:
Use -i to change the starting ID of the dataset. For instance:
`python main.py -n 500 -i 1000`
This will generate a dataset starting with ID 1000.

Example:
If you generate dataset with equal size of each qa_type, and the total size is 5000
run:
`python main.py -n 1250 -q 0,4,5`
`python main.py -n 3750 -i 1250 -q 1,2,3`

## Text-Only QA Conversion

To convert this game's multimodal QA data into a text-only version, run the unified converter from the repository root:

```bash
python src/Code_for_text_data_derivative/convert_text_data.py --game PyramidChess --data src/PyramidChess/pyramidchess_dataset_example/data.json --output src/PyramidChess/pyramidchess_dataset_example/data_text.json
```

The converter reads each entry's `state` JSON, prepends a textual description of the visible game state to the original question, and writes `data_text.json` without the `image` or `state` fields by default.

Example text state fragment:

```text
PYRAMID CHESS STATE:
{
  "0": [
    [
      "--",
      "P1",
      "P0"
    ],
    [
      "--",
      "P0",
      "P1"
    ],
    [
      "P1",
      "P0",
...
```
