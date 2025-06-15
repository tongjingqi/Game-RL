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

# 用于存储所有数据的列表
all_data = []

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

# 将行列转换为国际象棋坐标（例如，行3列2 => b6）
def convert_to_chess_notation(row_idx, col_idx):
    # 列（a-h），行（1-8）
    col = chr(ord('a') + col_idx)  # 列从a开始
    row = 8 - row_idx  # 行从8开始
    return f"{col}{row}"

def generate_data_count(num, num_pieces, data_path, image_path, state_path):

    # 生成随机题目
    piece_types = ['P', 'R', 'B', 'N', 'Q', 'K']
    fen = generate_random_puzzle(piece_types, num_pieces)

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

    # 随机选择一种棋子类型进行提问
    random_piece_type = random.choice(piece_types)
    piece_count_for_question = piece_count[random_piece_type]
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

    # 创建问题和解答结构
    qtype = "count_piece_question"  # 新类型的题目
    atype = "answer"
    
    # 处理分析部分，根据棋子数量生成不同的回答
    if piece_count_for_question == 0:
        # 如果棋子数量是 0
        analysis += f"There's no {piece_full_name} on the board. So the number of {piece_full_name} is {piece_count_for_question}"
    else:
        # 如果棋子数量不为 0
        positions_str = ', '.join([convert_to_chess_notation(r, c) for r, c in piece_positions_for_question])  # 格式化坐标
        analysis += f"The {piece_full_name} is in the following positions on the board: {positions_str}.So the number of {piece_full_name} is {piece_count_for_question}."


    data = {
        "data_id": f"chess-ranger-{num:03}-{qtype}",  # 使用递增编号
        "qa_type": "Target Perception",
        "question_id": 2,
        "question_description": "Asking how many pieces of a specific type are on the board",
        "image": image_path,
        "state": state_path,
        "plot_level": plot_level,  # 根据num_pieces设置的难度
        "qa_level":"Medium",
        "question": f"How many {piece_full_name}s are on the board?",
        "answer": f"{piece_count_for_question}",
        "analysis": analysis,
    }

    return data