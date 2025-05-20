# Code2Logic: Game-Code-Driven Data Synthesis for Enhancing VLMs General Reasoning

Code for the paper "Code2Logic: Game-Code-Driven Data Synthesis for Enhancing VLMs General Reasoning".

[[🤗 GameQA-140K Dataset](https://huggingface.co/datasets/Gabriel166/GameQA-140K)]

This is the first work, to the best of our knowledge, that leverages ***game code*** to synthesize multimodal reasoning data for ***training*** VLMs. Furthermore, when trained solely with a GRPO strategy on **GameQA** (synthesized via our proposed **Code2Logic** approach), multiple cutting-edge open-source models exhibit significantly enhanced out-of-domain generalization.

<div align=center><img src="./assets/categorized_30_games_images.png" alt="categorized_30_games_images" width="90%" /></div>

## Introduction

Visual Language Models (VLMs) have achieved impressive progress in tasks such as image description and general visual question answering, yet their performance remains limited in complex visual tasks requiring multi-step reasoning. However, the scarcity of high-quality multimodal reasoning datasets hinders the improvement of reasoning capabilities in VLMs.

Game code typically encodes sate transition logic and causal reasoning chains, and can be efficiently generated with LLMs. Inspired by this, we leverage game code to generate multimodal reasoning data at scale. We propose the Code2Logic approach that systematically maps code semantics to multimodal reasoning logic, and construct the GameQA-140K dataset spanning 30 different games for training and evaluating VLMs.

### Code2Logic Approach

<div align=center><img src="./assets/Code2Logic_approach.png" alt="Code2Logic_approach" width="75%" /></div>

For a selected game, the Code2Logic approach works as follows. We construct game code using LLMs at first. Then, design and refine some QA templates with the help of LLM. Finally, prompt the LLM to construct data engine based on the game code. During code execution, data engine fills out the QA templates to generate massive data samples containing detailed reasoning processes.

### GameQA Dataset

<div align=center><img src="./assets/4_game_example_samples.png" alt="4_game_example_samples" width="80%" /></div>

Our GameQA dataset transforms the game-playing tasks into Visual Question Answering format. It encompasses 30 different games classified into 4 categories based on the core capabilities required to solve game tasks, with 4 games from different categories and their example data samples illustrated in the image above. The data samples in GameQA are also reasonably graded (see [🤗 GameQA-140K](https://huggingface.co/datasets/Gabriel166/GameQA-140K)).

## All Code for Generating GameQA samples

In this repository, we provide the code used to generate samples for each game in GameQA. There are 30 directories in total - one for each game.

Apart form the code, each game directory contains:

1. A README file describing the game tasks and code execution instructions
2. A subdirectory with example samples

Feel free to use the code directly to generate more samples, or adapt it to produce more types of training data for your specific requirements.

|                     | 3D Spatial Perception and Understanding | Pattern Recognition and Matching | Multi-step Reasoning                                  | Strategic Planning                                      |
| :------------------ | :--------------------------------------: | :------------------------------: | :----------------------------------------------------: | :------------------------------------------------------: |
| **In Domain** | [3D Maze](./3d_maze) <br> [Rubik's Cube](./rubiks_cube) <br> [3D Reconstruction](./3DReconstruction) | [Tangram](./tangram) <br> [Freecell](./freecell) <br> [Tetris](./tetris) <br> [Zuma](./zuma) <br/> [Spider Solitaire](./spider_solitaire) <br> [Color Hue](./hue) | [Langton's Ant](./langton_ant) <br> [2D Turing Machine](./2d_turing_machine) <br> [Word Search](./word_search) <br> [Tents](./tents) <br> [Rhythm Game](./rhythm_game) <br> [Star Battle](./star-battle) | [Sokoban](./sokoban) <br> [Maze](./maze) <br> [TicTacToe](./tictactoe) <br> [Ultra TicTacToe](./ultra_tictactoe) <br> [Space Invaders](./space_invaders) |
| **Out of Domain** | [Pyramid Chess](./PyramidChess) <br> [Minecraft](./minecraft) | [Jewel2](./jewel2) <br> [Klondike](./klondike) | [Sudoku](./sudoku) <br> [Lifegame](./lifegame) <br> [Minesweeper](./minesweeper) | [Snake](./snake) <br> [Chess Ranger](./chess_ranger) <br> [Pacman](./pacman) |