# SNAKE
This is a tool to simulate the classic game Snake and generate QA dataset, which contains images, questions and step-by-step CoT solutions.

## Rule
10x10 grid map, where red represents food, yellow represents the snake's head, and blue represents the snake's body. The snake head cannot touch the map boundary or the snake's body, otherwise the game ends.

## Question
1. Snake head postion
2. Food postion
3. Snake length
4. What will happen until this process ends if following a specific sequence of moves (hitting its own body, hitting the wall, reaching the food, or nothing else happens)?
5. The shortest path to reach the food

## How to use
### requirements
python version: 3.8.18
numpy 1.24.4
pygame 2.6.1

You can run `pip install numpy==1.24.4 pygame==2.6.1`.

### How to run code
Just run `python gen_qa.py`.
