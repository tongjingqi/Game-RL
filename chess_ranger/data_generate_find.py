import json
import argparse
import random
from cr_solver import Board
from cr_generate import generate_random_puzzle
from plot_board import ChessBoardImage
from state_generate import fen_to_custom_json_file

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

# 定义棋子符号到全名的映射
piece_name_mapping = {
    'P': 'Pawn',
    'R': 'Rook',
    'N': 'Knight',
    'B': 'Bishop',
    'Q': 'Queen',
    'K': 'King'
}

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

# 将行列转换为国际象棋坐标
def convert_to_chess_notation(row_idx, col_idx):
    col = chr(ord('a') + col_idx)  # 列从a开始
    row = 8 - row_idx  # 行从8开始
    return f"{col}{row}"

# 验证是否有且仅有一种棋子数量为1
def verify_single_piece(piece_count):
    single_pieces = [piece for piece, count in piece_count.items() if count == 1]
    return len(single_pieces) > 0, single_pieces

# 生成确保有单个棋子的随机棋盘
def generate_board_with_single_piece(piece_types, num_pieces, max_attempts=100):
    for _ in range(max_attempts):
        fen = generate_random_puzzle(piece_types, num_pieces)
        piece_count, piece_positions = count_pieces_in_fen(fen)
        has_single, single_pieces = verify_single_piece(piece_count)
        if has_single:
            return fen, single_pieces
    raise Exception("Could not generate a board with a single piece after maximum attempts")

def generate_data_find(num, num_pieces, data_path, image_path, state_path):
    # 生成随机题目，确保有单个棋子
    piece_types = ['P', 'R', 'B', 'N', 'Q', 'K']
    fen, single_pieces = generate_board_with_single_piece(piece_types, num_pieces)
    
    # 解答过程
    board_fen = Board(fen)
    pieces_positions = board_fen.get_piece_positions()

    analysis = "The current board situation is:"
    for piece_name, position in pieces_positions:
        analysis += f"{piece_name} at {position}."

    # 获取难度级别
    plot_level = get_plot_level(num_pieces)
    
    # 统计每种棋子的数量及其位置
    piece_count, piece_positions = count_pieces_in_fen(fen)
    
    # 从单个棋子中随机选择一个作为问题
    random_piece_type = random.choice(single_pieces)
    piece_positions_for_question = piece_positions[random_piece_type]
    
    # 获取棋子全名
    piece_full_name = piece_name_mapping[random_piece_type]
    
    # 生成棋盘图像
    board_image = ChessBoardImage(fen)
    image_save_path = data_path + "/" + image_path
    board_image.save_image(image_save_path)
    
    # 生成json格式state
    state_save_path = data_path + "/" + state_path
    fen_to_custom_json_file(fen, state_save_path)
    
    qtype = "find_pieces"
    
    # 生成位置字符串
    positions_str = ', '.join([convert_to_chess_notation(r, c) for r, c in piece_positions_for_question])
    analysis += f"There is exactly one {piece_full_name} on the board, located at position: {positions_str}."
    
    data = {
        "data_id": f"chess-ranger-{num:03}-{qtype}",
        "qa_type": "StateInfo",
        "question_id": 3,
        "question_description": "Asking for the location of a single piece of a specific type",
        "image": image_path,
        "state": state_path,
        "plot_level": plot_level,
        "qa_level": "Easy",
        "question": f"Where is the {piece_full_name} on the board?",
        "answer": positions_str,
        "analysis": analysis,
    }
    
    return data