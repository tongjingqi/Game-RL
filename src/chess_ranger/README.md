# Chess Ranger

## Game Rules
In Chess Ranger, the game is played on an 8x8 chessboard, where the rows are numbered 1 to 8 from bottom to top, and columns are labeled a to h from left to right. The pieces move according to standard chess rules, and players can only capture pieces. The king can be captured as well. The goal is to end up with only one piece remaining on the board.

## Problem Types
- **Piece Count Question**: Asking how many pieces of a specific type are on the board.

- **Piece Position Question**: Asking for a piece located at a specific square.

- **Find Pieces Question**: Asking for the location of all pieces of a specific type.

- **Steps to Solve Puzzle Question**: Asking for the number of moves to solve the puzzle.

- **Predict Next Move Question**: Asking for the next move that can lead to solving the puzzle.

- **dataset examples**
```json
{
        "data_id": "chess-ranger-001-answer_question",
        "qa_type": "TransitionPath",
        "question_id": 1,
        "question_description": "Asking for the number of moves to solve the puzzle",
        "image": "images/board_001.png",
        "state": "states/board_001.json",
        "plot_level": "Easy",
        "qa_level": "Hard",
        "question": "This game is called Chess Ranger. The rules are as follows:Pieces move like in standard chess.You can only perform capture moves.The king is allowed to be captured.The goal is to end up with a single piece remaining on the board.How many steps are needed to solve the puzzle?Choose from the following options:A.7,B.6,C.4,D.8,E.3,F.2,G.5",
        "answer": "C",
        "analysis": "The solved steps are as follows: Try: Bishop from f5 to h7.Try: Bishop from h7 to c2.Fail: No moves left with 3 pieces.Backtrack: Bishop from c2 to h7.Try: Queen from h1 to h7.Try: Queen from h7 to c2.Fail: No moves left with 2 pieces.Backtrack: Queen from c2 to h7.Fail: No moves left with 3 pieces.Backtrack: Queen from h7 to h1.Fail: No moves left with 4 pieces.Backtrack: Bishop from h7 to f5.Try: Bishop from f5 to c2.Try: Bishop from c2 to h7.Try: Queen from h1 to h7.Fail: No moves left with 2 pieces.Backtrack: Queen from h7 to h1.Fail: No moves left with 3 pieces.Backtrack: Bishop from h7 to c2.Try: Queen from h1 to h7.Try: Queen from h7 to c2.Fail: No moves left with 2 pieces.Backtrack: Queen from c2 to h7.Try: Bishop from c2 to h7.Fail: No moves left with 2 pieces.Backtrack: Bishop from h7 to c2.Fail: No moves left with 3 pieces.Backtrack: Queen from h7 to h1.Fail: No moves left with 4 pieces.Backtrack: Bishop from c2 to f5.Try: Queen from h1 to h7.Try: Queen from h7 to f5.Try: Queen from f5 to f8.Fail: No moves left with 2 pieces.Backtrack: Queen from f8 to f5.Try: Queen from f5 to c2.Fail: No moves left with 2 pieces.Backtrack: Queen from c2 to f5.Fail: No moves left with 3 pieces.Backtrack: Queen from f5 to h7.Try: Queen from h7 to c2.Try: Bishop from f5 to c2.Fail: No moves left with 2 pieces.Backtrack: Bishop from c2 to f5.Try: Queen from c2 to f5.Try: Queen from f5 to f8.Success: Only one piece remains.So the total number of steps is 4.Then,the right option is C.",
        "options": [
            "A.7",
            "B.6",
            "C.4",
            "D.8",
            "E.3",
            "F.2",
            "G.5"
        ]
    },
    {
        "data_id": "chess-ranger-002-count_piece_question",
        "qa_type": "StateInfo",
        "question_id": 2,
        "question_description": "Asking how many pieces of a specific type are on the board",
        "image": "images/board_002.png",
        "state": "states/board_002.json",
        "plot_level": "Easy",
        "qa_level": "Medium",
        "question": "How many Rooks are on the board?",
        "answer": "1",
        "analysis": "The Rook is in the following positions on the board: g7.So the number of Rook is 1."
    },
    {
        "data_id": "chess-ranger-003-find_pieces",
        "qa_type": "StateInfo",
        "question_id": 3,
        "question_description": "Asking for the location of all pieces of a specific type",
        "image": "images/board_003.png",
        "state": "states/board_003.json",
        "plot_level": "Easy",
        "qa_level": "Easy",
        "question": "Where are the Knights on the board?",
        "answer": "d7",
        "analysis": "The Knights are located at the following positions: d7."
    },
    {
        "data_id": "chess-ranger-004-pos_question",
        "qa_type": "StateInfo",
        "question_id": 4,
        "question_description": "Asking for a piece located at a specific square",
        "image": "images/board_004.png",
        "state": "states/board_004.json",
        "plot_level": "Easy",
        "qa_level": "Easy",
        "question": "What piece is at c1?Choose from the following options:A.Pawn,B.Rook,C.Knight,D.Bishop,E.Queen,F.King,G.No Piece",
        "answer": "D",
        "analysis": "The piece at c1 is Bishop.So the option is D.",
        "options": [
            "A.Pawn",
            "B.Rook",
            "C.Knight",
            "D.Bishop",
            "E.Queen",
            "F.King",
            "G.No Piece"
        ]
    },
    {
        "data_id": "chess-ranger-005-predict_state",
        "qa_type": "ActionOutcome",
        "question_id": 5,
        "question_description": "Asking for the next move that can lead to solving the puzzle",
        "image": "images/board_005.png",
        "state": "states/board_005.json",
        "plot_level": "Easy",
        "qa_level": "Hard",
        "question": "This game is called Chess Ranger. The rules are as follows:Pieces move like in standard chess.You can only perform capture moves.The king is allowed to be captured.The goal is to end up with a single piece remaining on the board.Which step can lead to solve the puzzle?Choose from the following options:A.Bishop from h5 to f3,B.King from h4 to h5,C.Rook from h8 to h4,D.Rook from h8 to h5,E.None",
        "answer": "CD",
        "analysis": "The solved steps of option C are as follows:Try: Rook from a5 to h5.Try: Rook from h5 to h4.Try: Knight from f3 to h4.Success: Only one piece remains.The solved steps of option D are as follows:Try: Rook from a5 to h5.Try: Rook from h5 to h4.Try: Knight from f3 to h4.Success: Only one piece remains.So the answer is CD",
        "options": [
            "A.Bishop from h5 to f3",
            "B.King from h4 to h5",
            "C.Rook from h8 to h4",
            "D.Rook from h8 to h5",
            "E.None"
        ]
    }
```

## Code
The puzzle generator uses the number of pieces and their positions to generate random puzzles, ensuring the generated puzzles are solvable using the Solver class. The code below also generates the necessary chessboard image and state file.
```python
class Solver:
    def __init__(self, board: Board):
        self.board = board

    def solve(self) -> List[Tuple[Piece, Square, Square]]:
        moves = []
        if self._solve(self.board.piece_count(), moves):
            return [(move.src_piece, move.src_square, move.dst_square) for move in moves]
        else :
            return None

    def _solve(self, piece_count: int, moves: List[Move]) -> bool:
        if piece_count == 1:
            return True
        for move in self.board.moves():
            self.board.make_move(move)
            moves.append(move)
            if self._solve(piece_count - 1, moves):
                return True
            moves.pop()
            self.board.undo_move(move)
        return False
```
### Usage
Environment configuration reference directory `requirement.txt`
```bash
pip install -r requirement.txt
```
The basic code is already encapsulated, you just need to run the python file with the data_generate prefix in the code directory, the data is stored in the dataset folder with the same suffix, run the command as follow:
```bash
python data_generate.py --data_num 500 --num_pieces 6 --max_length 5000
```
The `data_num` parameter specifies the number of generated data, `num_pieces` specifies the maximum number of pieces to generate the data(range:4-6),and `max_length` parameter is the max length of analysis in each data.
The generated dataset is stored in the `{problem type}_dataset` directory shown at the end of the code, you need to construct the subdirectories image and state in advance.The images and states are saved at `image_path` and `state_path`,you can also change it as you need.
The ability to customise the difficulty scale is provided in the `data_generate.py`.Each of the three parameters `level_percentage_i` corresponds to the proportion of questions of three levels of difficulty.In this case, `num_pieces` is not actually called during the generation process
Note: Due to the principle of generating questions is to generate and then verify, there may be many times to generate the results of the situation are not solved, the generation process will be slightly lagging,please wait for its completion.

### Code example
`data_generate.py`
```python
import json
import argparse
import random
import os

from data_generate_aq import generate_data_aq
from data_generate_count import generate_data_count
from data_generate_find import generate_data_find
from data_generate_pos import generate_data_pos
from data_generate_predict import generate_data_predict

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate Chess Ranger puzzles and save as JSON files.")
    parser.add_argument('--data_num', type=int, default=100, help='Number of puzzles to generate')
    parser.add_argument('--num_pieces', type=int, default=6, help='Maximum number of pieces in the puzzle')
    parser.add_argument('--max_length', type=int, default=5000, help='Maximum length of analysis')  # 定义 max_length
    args = parser.parse_args()
    return args

# 自定义参数
args = parse_arguments()
data_num = args.data_num  # 从命令行获取生成的数据个数
max_pieces = args.num_pieces  # 从命令行获取最大棋子
max_analysis_len = args.max_length

all_data = []

'''
level_percentage_1 = 0.3
level_percentage_2 = 0.3
level_percentage_3 = 1 - level_percentage_1 - level_percentage_2
'''

# 创建多级文件夹（如果父文件夹不存在则会创建）
os.makedirs('chess_ranger_dataset/images', exist_ok=True)
os.makedirs('chess_ranger_dataset/states', exist_ok=True)

for num in range(1, data_num + 1):  # 循环生成data_num个数据

    '''
    if num/datanum <= level_percentage_1 : num_pieces = random.randint(4, 6)
    elif level_percentage_1 < num/datanum <= level_percentage_1 + level_percentage_2 : num_pieces = random.randint(7, 9)
    elif level_percentage_1 + level_percentage_2 < num/datanum <= 1 : num_pieces = random.randint(10, 11)
    '''

    # 随机选择棋子数量（范围为4到max_pieces之间）
    num_pieces = random.randint(4, max_pieces)

    '''
    if(num <= 5): num_pieces = random.randint(4,5)
    elif(5 < num <= 10): num_pieces = 6
    elif(10 < num <= 15): num_pieces = random.randint(7,8)
    '''

    data_path = "chess_ranger_dataset"
    image_path = f"images/board_{num:03}.png"
    state_path = f"states/board_{num:03}.json"

    opt = num % 5
    if opt == 1:
        data = generate_data_aq(num, num_pieces, data_path, image_path, state_path, max_analysis_len, 10)
    elif opt == 2:
        data = generate_data_count(num, num_pieces, data_path, image_path, state_path)
    elif opt == 3:
        data = generate_data_find(num, num_pieces, data_path, image_path, state_path)
    elif opt == 4:
        data = generate_data_pos(num, num_pieces, data_path, image_path, state_path)
    elif opt == 0:
        data = generate_data_predict(num, num_pieces, data_path, image_path, state_path, max_analysis_len, 10)

    all_data.append(data)

# 将数据写入 JSON 文件 
with open('chess_ranger_dataset/data.json', 'w') as f:
    json.dump(all_data, f, indent=4)

```