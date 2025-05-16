import json
import argparse
import random
from cr_generate import generate_random_puzzle
from cr_solver import Solver,Board,TraceSolver
from plot_board import ChessBoardImage
from state_generate import fen_to_custom_json_file

qtype = "answer_question"

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


def generate_data_aq(num, num_pieces, data_path, image_path, state_path, max_analysis_len, max_retries=100):

        # 生成随机题目
    piece_types = ['P', 'R', 'B', 'N', 'Q', 'K']
    fen = generate_random_puzzle(piece_types, num_pieces)

    # 获取难度级别
    plot_level = get_plot_level(num_pieces)

    # 解答过程
    board_fen = Board(fen)
    pieces_positions = board_fen.get_piece_positions()

    analysis = "The current board situation is:"
    for piece_name, position in pieces_positions:
        analysis += f"{piece_name} at {position}."

    solver = Solver(board_fen)
    num_step = 0
    steps = ""
    for piece, src, dst in solver.solve():
        steps += f"Move {piece} from {src} to {dst}. "
        num_step += 1

    #print(steps)

    new_board_fen = Board(fen)
    trace_solver = TraceSolver(new_board_fen)
    solution, trace = trace_solver.solve()

    entries = ""
    for entry in trace:
        #print(entry)
        entries += entry

    # 生成棋盘图像
    board_image = ChessBoardImage(fen)
    image_save_path = data_path + "/" + image_path
    board_image.save_image(image_save_path)

    # 生成json格式state
    state_save_path = data_path + "/" + state_path
    fen_to_custom_json_file(fen, state_save_path)

    if(num % 2 == 0):
        atype = "answer"
        
        analysis += "In the process of solving the puzzle, we have 2 operations and 2 flags to analysis:operation Try indicates the execution of a step, operation Backtrack indicates that the capture operation performed by the last Try step is withdrawn; flag Fail indicates all tries have failed in the current case, flag Success indicates that the puzzle is solved."
        analysis += f"The solved steps are as follows: {entries}So the total number of steps is {num_step}."

        # 创建问题和解答结构
        data = {
            "data_id": f"chess-ranger-{num:03}-{qtype}",  # 使用递增编号
            "qa_type": "TransitionPath",
            "question_id": 1,
            "question_description": "Asking for the number of moves to solve the puzzle",
            "image": image_path,
            "state": state_path,
            "plot_level": plot_level,  # 根据num_pieces设置的难度
            "qa_level":"Hard",
            "question": "This game is called Chess Ranger. The rules are as follows:Pieces move like in standard chess.You can only perform capture moves.The king is allowed to be captured.The goal is to end up with a single piece remaining on the board.How many steps are needed to solve the puzzle?",
            "answer": f"{num_step}",
            "analysis": analysis,
        }
    else: 
        atype = "option"
        # 只要保证棋子数大于3就可以让options均大于0
        options = [num_step-2,num_step-1,num_step,num_step+1,num_step+2,num_step+3,num_step+4,num_step+5]
        # 打乱顺序
        random.shuffle(options)
        answer_index = options.index(num_step)
        letters = ["A","B","C","D","E","F","G","H"]
        answer_letter = letters[answer_index]

        analysis += "In the process of solving the puzzle, we have 2 operations and 2 flags to analysis:operation Try indicates the execution of a step, operation Backtrack indicates that the capture operation performed by the last Try step is withdrawn; flag Fail indicates all tries have failed in the current case, flag Success indicates that the puzzle is solved."
        analysis += f"The solved steps are as follows: {entries}So the total number of steps is {num_step}.Then,the right option is {answer_letter}."

        # 创建问题和解答结构
        data = {
            "data_id": f"chess-ranger-{num:03}-{qtype}",  # 使用递增编号
            "qa_type": "TransitionPath",
            "question_id": 1,
            "question_description": "Asking for the number of moves to solve the puzzle",
            "image": image_path,
            "state": state_path,
            "plot_level": plot_level,  # 根据num_pieces设置的难度
            "qa_level":"Hard",
            "question": f"This game is called Chess Ranger. The rules are as follows:Pieces move like in standard chess.You can only perform capture moves.The king is allowed to be captured.The goal is to end up with a single piece remaining on the board.How many steps are needed to solve the puzzle?Choose from the following options:A.{options[0]},B.{options[1]},C.{options[2]},D.{options[3]},E.{options[4]},F.{options[5]},G.{options[6]},H.{options[7]}",
            "answer": f"{answer_letter}",
            "analysis": analysis,
            "options":[
                f"A.{options[0]}",
                f"B.{options[1]}",
                f"C.{options[2]}",
                f"D.{options[3]}",
                f"E.{options[4]}",
                f"F.{options[5]}",
                f"G.{options[6]}",
                f"H.{options[7]}"
            ]
        }
    # 检查analysis长度
    if len(analysis) > max_analysis_len and max_retries > 0:
        # 如果analysis太长并且还有重试次数，则重新调用函数
        return generate_data_aq(num, num_pieces, data_path, image_path, state_path, max_analysis_len, max_retries-1)

    return data
