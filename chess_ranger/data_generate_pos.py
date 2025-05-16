import json
import argparse
import random
from cr_solver import Board
from cr_generate import generate_random_puzzle
from plot_board import ChessBoardImage
from state_generate import fen_to_custom_json_file

# 定义棋子符号到全名的映射
piece_name_mapping = {
    'P': 'Pawn',
    'R': 'Rook',
    'N': 'Knight',
    'B': 'Bishop',
    'Q': 'Queen',
    'K': 'King'
}

# 定义根据num_pieces决定难度的函数
def get_plot_level(num_pieces):
    if num_pieces == 4:
        return "Easy"
    elif num_pieces == 5:
        return "Medium"
    elif num_pieces >= 6:
        return "Hard"
    else:
        return "Unknown"  # 如果棋子数不在这个范围内，返回"Unknown"

# 定义解析fen并统计棋子数量及其位置的函数
def count_pieces_in_fen(fen):
    # 初始化棋子计数和位置记录
    piece_count = {'P': 0, 'R': 0, 'N': 0, 'B': 0, 'Q': 0, 'K': 0}
    piece_positions = {'P': [], 'R': [], 'N': [], 'B': [], 'Q': [], 'K': []}

    # 遍历fen中的棋盘部分（即前8个斜杠分隔部分）
    rows = fen.split()[0].split('/')  # 分割成8行
    for row_idx, row in enumerate(rows):
        col_idx = 0
        for char in row:
            if char.isdigit():  # 该字符表示空格，数字表示空格数量
                col_idx += int(char)
            elif char.isalpha():  # 棋子字母
                piece_count[char.upper()] += 1
                piece_positions[char.upper()].append((row_idx, col_idx))  # 添加位置
                col_idx += 1  # 棋子占一个格子

    return piece_count, piece_positions

# 将行列转换为国际象棋坐标（例如，行3列2 => b6）
def convert_to_chess_notation(row_idx, col_idx):
    # 列（a-h），行（1-8）
    col = chr(ord('a') + col_idx)  # 列从a开始
    row = 8 - row_idx  # 行从8开始
    return f"{col}{row}"

# 随机选择一个格子并提问
def generate_pos_question(piece_positions, rows=8, cols=8, num=None):
    while True:
        # 随机选择一个位置
        random_row = random.randint(0, rows - 1)
        random_col = random.randint(0, cols - 1)

        # 检查该位置上是否有棋子
        piece_at_position = 'No Piece'
        for piece, positions in piece_positions.items():
            if (random_row, random_col) in positions:
                piece_at_position = piece_name_mapping[piece]
                break
        
        # 如果是2的倍数并且选中空格，重新选择
        if num % 2 == 0 and piece_at_position == 'No Piece':
            continue
        
        return (random_row, random_col), piece_at_position

def generate_data_pos(num, num_pieces, data_path, image_path, state_path):

    plot_level = get_plot_level(num_pieces)

    # 生成随机题目
    piece_types = ['P', 'R', 'B', 'N', 'Q', 'K']
    fen = generate_random_puzzle(piece_types, num_pieces)

    # 解答过程
    board_fen = Board(fen)
    pieces_positions = board_fen.get_piece_positions()

    analysis = "The current board situation is:"
    for piece_name, position in pieces_positions:
        analysis += f"{piece_name} at {position}."

    # 统计每种棋子的数量及其位置
    piece_count, piece_positions = count_pieces_in_fen(fen)

    # 随机生成一个位置和提问内容
    (rand_row, rand_col), piece_at_position = generate_pos_question(piece_positions,num=num)

    # 生成棋盘图像
    board_image = ChessBoardImage(fen)
    image_save_path = data_path + "/" + image_path
    board_image.save_image(image_save_path)

    # 生成json格式state
    state_save_path = data_path + "/" + state_path
    fen_to_custom_json_file(fen, state_save_path)


    # 生成问题和解答
    qtype = "pos_question"  # 更改为pos类型问题
    atype = "option"
    options = ['Pawn', 'Rook', 'Knight', 'Bishop', 'Queen', 'King', 'No Piece']
    answer_index = options.index(piece_at_position)
    letters = ["A","B","C","D","E","F","G"]
    answer_letter = letters[answer_index]

    # 提问：某个格子上的棋子是什么？
    question = f"What piece is at {convert_to_chess_notation(rand_row, rand_col)}?Choose from the following options:A.{options[0]},B.{options[1]},C.{options[2]},D.{options[3]},E.{options[4]},F.{options[5]},G.{options[6]}"

    # 答案：该位置上的棋子（或没有棋子）
    analysis += f"The piece at {convert_to_chess_notation(rand_row, rand_col)} is {piece_at_position}.So the option is {answer_letter}."


    data = {
        "data_id": f"chess-ranger-{num:03}-{qtype}",  # 使用递增编号
        "qa_type": "StateInfo",
        "question_id": 4,
        "question_description": "Asking for a piece located at a specific square",
        "image": image_path,
        "state": state_path,
        "plot_level":plot_level,
        "qa_level":"Easy",
        "question": question,
        "answer": answer_letter,
        "analysis":analysis,
        "options": [
            f"A.{options[0]}",
            f"B.{options[1]}",
            f"C.{options[2]}",
            f"D.{options[3]}",
            f"E.{options[4]}",
            f"F.{options[5]}",
            f"G.{options[6]}"
        ]
    }

    return data