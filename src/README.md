## Code for Generating GameQA samples

### Introduction

In this directory, we provide the code (i.e., "data engine" in our Code2Logic approached) used to generate samples for each game in GameQA. There are 30 directories in total - one for each game.

**Apart form the code, each game directory contains:**

1. **A README file describing the game tasks and code execution instructions**
2. **A subdirectory with example samples.** E.g., [sudoku_dataset_example](./sudoku/sudoku_dataset_example), [tetris_dataset_example](./tetris/tetris_dataset_example).

> 😎 Feel free to use the code directly to generate more samples, or adapt it to produce more types of training data for your specific requirements.

|                   |           3D Spatial Perception and Understanding            |               Pattern Recognition and Matching               |                     Multi-step Reasoning                     |                      Strategic Planning                      |
| :---------------- | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
| **In Domain**     | [3D Maze](./3d_maze) <br> [Rubik's Cube](./rubiks_cube) <br> [3D Reconstruction](./3DReconstruction) | [Tangram](./tangram) <br> [Freecell](./freecell) <br> [Tetris](./tetris) <br> [Zuma](./zuma) <br/> [Spider Solitaire](./spider_solitaire) <br> [Color Hue](./hue) | [Langton's Ant](./langton_ant) <br> [2D Turing Machine](./2d_turing_machine) <br> [Word Search](./word_search) <br> [Tents](./tents) <br> [Rhythm Game](./rhythm_game) <br> [Star Battle](./star-battle) | [Sokoban](./sokoban) <br> [Maze](./maze) <br> [TicTacToe](./tictactoe) <br> [Ultra TicTacToe](./ultra_tictactoe) <br> [Space Invaders](./space_invaders) |
| **Out of Domain** | [Pyramid Chess](./PyramidChess) <br> [Minecraft](./minecraft) |    [Jewel2](./jewel2) <br> [Klondike](./klondike)    | [Sudoku](./sudoku) <br> [Lifegame](./lifegame) <br> [Minesweeper](./minesweeper) | [Snake](./snake) <br> [Chess Ranger](./chess_ranger) <br> [Pacman](./pacman) |

### Output Files

For each game:

* Executing the code will produce **`data.json`** containing the generated data samples, with the corresponding visual input images saved in the  **`images/`** directory.
* Typically, **game state information (grid size, element positions, etc.) of the samples will simultaneously be saved in JSON** to the **`states/`** directory.

For example, the structure of the [sudoku_dataset_example](./sudoku/sudoku_dataset_example) (under [the directory of Sudoku](./sudoku)) is as follows:

```bash
.
├── data.json
├── images
│   ├── board_00001.png
│   ├── board_00002.png
│   ├── board_00003.png
│   ├── board_00004.png
│   ├── board_00005.png
│   ├── board_00006.png
│   ├── board_00007.png
│   ├── board_00008.png
│   ├── board_00009.png
│   ├── board_00010.png
│   ├── board_00011.png
│   ├── board_00012.png
│   ├── board_00013.png
│   ├── board_00014.png
│   └── board_00015.png
└── states
    ├── board_00001.json
    ├── board_00002.json
    ├── board_00003.json
    ├── board_00004.json
    ├── board_00005.json
    ├── board_00006.json
    ├── board_00007.json
    ├── board_00008.json
    ├── board_00009.json
    ├── board_00010.json
    ├── board_00011.json
    ├── board_00012.json
    ├── board_00013.json
    ├── board_00014.json
    └── board_00015.json
```

* The first data sample (in [sudoku_dataset_example/data.json](./sudoku/sudoku_dataset_example/data.json)):

  ```json
  [
      {
          "data_id": "sudoku-00001",
          "qa_type": "Target Perception",
          "question_id": 1,
          "question_description": "Check color state at position",
          "image": "images/board_00001.png",
          "state": "states/board_00001.json",
          "plot_level": "Easy",
          "qa_level": "Easy",
          "question": "This is a sudoku game in which the board is filled with a total number of colours equal to the length of the board's sides, and no rows, columns or squares are allowed to have duplicate colours.You should fill the empty cells on the board with following 4 colors: red, green, blue, magenta.In this Sudoku board, the row coordinates are 1-4 from top to bottom, and the column coordinates are 1-4 from left to right.What color is at position (2,1)(note that on the board the position (2,1) has already been filled with a certain color)?Choose from following options:A.red, B.green, C.blue, D.magenta",
          "answer": "A",
          "analysis": "From the image we can see the color at Position (2,1) is red.So the answer is A",
          "options": [
              "A.red",
              "B.green",
              "C.blue",
              "D.magenta"
          ]
      },
      ...
  ]
  ```

* The corresponding visual input image ([sudoku_dataset_example/images/board_00001.png](./sudoku/sudoku_dataset_example/images/board_00001.png)):

  <div align=center><img src="./sudoku/sudoku_dataset_example/images/board_00001.png" alt="./sudoku/sudoku_dataset_example/images/board_00001.png" width="30%" /></div>

* The JSON describing the Sudoku board state ([sudoku_dataset_example/states/board_00001.json](./sudoku/sudoku_dataset_example/states/board_00001.json)):

  ```json
  {"size": 4, "board": [[4, 2, 0, 3], [1, 3, 4, 0], [0, 0, 0, 1], [3, 0, 2, 4]], "colors": ["#FF0000", "#00FF00", "#0000FF", "#FF00FF"]}
  ```

> Directly based on these game state records, we've now derived 🤗[a pure-text version of GameQA](https://huggingface.co/datasets/Code2Logic/GameQA-text) from the visual one, using code at [Code_for_text_data_derivative](./Code_for_text_data_derivative).

