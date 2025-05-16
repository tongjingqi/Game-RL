import json
import argparse
import random
import itertools
from cr_generate import generate_random_puzzle
from cr_solver import Solver,Board,TraceSolver
from plot_board import ChessBoardImage
from state_generate import fen_to_custom_json_file

qtype = "predict_state"

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

def generate_moves_more_than_4(piece_types,num_pieces):
    # 生成随机题目
    fen = generate_random_puzzle(piece_types, num_pieces)  
    # 解答过程
    board_fen = Board(fen)
    all_moves = board_fen.moves()
    if len(all_moves) < 4:
        return generate_moves_more_than_4(piece_types,num_pieces) 
    return fen

def generate_combinations(input_str, num):
    # 定义可选的字符
    chars = "1234"
    
    # 生成所有2-3个字符的组合
    all_combinations = []
    for r in range(1, 4):  # 生成长度为2或3的组合
        combs = itertools.combinations(chars, r)
        for comb in combs:
            all_combinations.append(''.join(comb))
    
    # 排除掉输入的字符串
    all_combinations = [comb for comb in all_combinations if comb != input_str]
    
    # 随机选择三个组合并返回
    return random.sample(all_combinations, num)

def generate_data_predict(num, num_pieces, data_path, image_path, state_path, max_analysis_len, max_retries=100):

    piece_types = ['P', 'R', 'B', 'N', 'Q', 'K']
    # 获取难度级别
    plot_level = get_plot_level(num_pieces)
    # 生成随机题目
    fen = generate_moves_more_than_4(piece_types,num_pieces)

    # 解答过程
    board_fen = Board(fen)
    pieces_positions = board_fen.get_piece_positions()

    analysis = "The current board situation is:"
    for piece_name, position in pieces_positions:
        analysis += f"{piece_name} at {position}."
    
    all_moves = board_fen.moves()
    solver = Solver(board_fen)
    steps = ""
    for piece, src, dst in solver.solve():
        steps += f"Move {piece} from {src} to {dst}. "

    #print(steps)

    # 生成棋盘图像
    board_image = ChessBoardImage(fen)
    image_save_path = data_path + "/" + image_path
    board_image.save_image(image_save_path)

    # 生成json格式state
    state_save_path = data_path + "/" + state_path
    fen_to_custom_json_file(fen, state_save_path)


    atype = "option"

    # 找出有解的步骤
    all_steps = []

    for move in all_moves:
        board_next = Board(fen)
        board_next.make_move(move)

        board_trace_next = Board(fen)
        board_trace_next.make_move(move)

        #all_bn_moves = board_next.moves()
        #for move in all_bn_moves:print(move)

        next_solver = Solver(board_next)
        # 注意不要重复调用solve
        next_solver_type = next_solver.solve()

        if next_solver_type is None:

            trace_solver = TraceSolver(board_trace_next)
            solution, trace = trace_solver.solve()

            entries = ""
            for entry in trace:
                #print(entry)
                entries += entry

            step_type = {
                "move":f"move {move.src_piece} in {move.src_square} to capture {move.dst_piece} in {move.dst_square}",
                "type":"F",
                "solve":entries
            }
            all_steps.append(step_type)
            
        else:
            
            trace_solver = TraceSolver(board_trace_next)
            solution, trace = trace_solver.solve()

            entries = ""
            for entry in trace:
                #print(entry)
                entries += entry

            step_type = {
                "move":f"move {move.src_piece} in {move.src_square} to capture {move.dst_piece} in {move.dst_square}",
                "type":"T",
                #"solve":solve_steps
                "solve":entries
            }
            all_steps.append(step_type)
           
     
    #print(len(all_steps)) 
    random.shuffle(all_steps)
    option_steps = random.sample(all_steps,4)
    #print(option_steps[0])
    
    # 不定项选择题
    options = []
    answer_indexes = []
    answer_index = 0
    for option_step in option_steps:
        options.append(option_step["move"])
        if option_step["type"] == "T":
            answer_indexes.append(answer_index)
        answer_index += 1

    answer = ""
    letters = ["1","2","3","4","E"]

    analysis += "In the process of solving the puzzle, we have 2 operations and 2 flags to analysis:operation Try indicates the execution of a step, operation Backtrack indicates that the capture operation performed by the last Try step is withdrawn; flag Fail indicates all tries have failed in the current case, flag Success indicates that the puzzle is solved."

    if len(answer_indexes) == 0:
        i_op = 1
        for option_step in option_steps:
            analysis += f"The tried steps after tring option {i_op} are as follows:" 
            analysis += option_step["solve"]
            analysis += f"So the option {i_op} is wrong."
            i_op += 1

        answer = "H"
        analysis += f"All of the options can not lead to solve.So the answer is {answer}"
        option_answer = "H" 
        final_options = generate_combinations(answer, 7)
    else:
        for a_i in answer_indexes:
            answer += letters[a_i]

        i_op = 1
        for option_step in option_steps:
            analysis += f"The tried steps after tring option {i_op} are as follows:" 
            analysis += option_step["solve"]

            if option_step["type"] == "F":
                analysis += f"So the option {i_op} is wrong."
            else: 
                analysis += f"So the option {i_op} is right."

            i_op += 1

        analysis += f"So the answer is {answer}."

        final_options = generate_combinations(answer, 6)
        op_letters = ["A","B","C","D","E","F","G"]
        final_options.append(answer)
        random.shuffle(final_options)
        an_index = final_options.index(answer)
        option_answer = op_letters[an_index]

    analysis += f"So the answer letter is {option_answer}."

    # 检查analysis长度

    if len(analysis) > max_analysis_len and max_retries > 0:
        # 如果analysis太长并且还有重试次数，则重新调用函数
        return generate_data_predict(num, num_pieces, data_path, image_path, state_path, max_analysis_len, max_retries-1)

            # 创建问题和解答结构
    data = {
        "data_id": f"chess-ranger-{num:03}-{qtype}",  # 使用递增编号
        "qa_type": "ActionOutcome",
        "question_id": 5,
        "question_description": "Asking for the next move that can lead to solving the puzzle",
        "image": image_path,
        "state": state_path,
        "plot_level": plot_level,  # 根据num_pieces设置的难度
        "qa_level":"Hard",
        "question": f"This game is called Chess Ranger. The rules are as follows:Pieces move like in standard chess.You can only perform capture moves.The king is allowed to be captured.The goal is to end up with a single piece remaining on the board.The possible first step to be tried is the following 4 steps: 1.{options[0]},2.{options[1]},3.{options[2]},4.{options[3]}.What is the first step to be tried now in order to finally solve the puzzle?Choose the number combination from the following options:A.{final_options[0]},B.{final_options[1]},C.{final_options[2]},D.{final_options[3]},E.{final_options[4]},F.{final_options[5]},G.{final_options[6]},H.None",
        "answer": option_answer,
        "analysis": analysis,
        "options":[
            f"A.{final_options[0]}",
            f"B.{final_options[1]}",
            f"C.{final_options[2]}",
            f"D.{final_options[3]}",
            f"E.{final_options[4]}",
            f"F.{final_options[5]}",
            f"G.{final_options[6]}",
            f"H.None"
        ]
    }

    return data