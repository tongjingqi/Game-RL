import random
from cr_solver import Piece,Board,Solver,Square
from typing import List

def generate_random_puzzle(piece_types: List[str], num_pieces: int) -> Board:
        """
        生成一个随机题目
        :param piece_types: 可用的棋子类型列表
        :param num_pieces: 棋盘上棋子的总数
        :return: 一个有效的棋盘布局
        """
        
        # 创建一个空的 FEN 格式棋盘
        chesses = []

        def format_list_to_string(input_list):
        # 以8个元素为一组分组，并将每个元素转换成字符串后连接起来
            formatted_string = '/'.join(
                ''.join(str(item) for item in input_list[i:i+8])
                for i in range(0, len(input_list), 8)
            )
            return formatted_string

        def compress_zeros(board_string):
            result = []
            zero_count = 0
            
            for char in board_string:
                if char == '0':
                    zero_count += 1
                else:
                    if zero_count > 0:
                        result.append(str(zero_count))
                        zero_count = 0
                    result.append(char)
                
                # 如果当前字符是斜杠并且有连续的0，那么添加计数并重置
                if char == '/':
                    if zero_count > 0:
                        result[-1] = str(zero_count)  # 替换最后一个添加的非零字符（如果有）
                        zero_count = 0

            # 处理最后一段可能存在的连续0
            if zero_count > 0:
                result.append(str(zero_count))

            return ''.join(result)

        # 随机选择num_pieces个格子来放置棋子
        positions = random.sample(range(64), num_pieces)
                
        # 随机为每个位置分配棋子并生成FEN字符串
        for pos in positions:
            piece_type = random.choice(piece_types)  # 从指定的棋子种类中随机选择
            chesses.append(piece_type)

        arr = []
        index = 0
        for i in range(64):
            if i in positions:
                arr.append(chesses[index])
                index += 1
            else:  arr.append(0)  

        arr = format_list_to_string(arr)
        arr = compress_zeros(arr)

        # 创建棋盘对象并返回
        puzzle = Board(arr)
        solver_puzzle = Solver(puzzle)

        # 用回溯法检查这个布局是否可解
        if solver_puzzle.solve() is not None:
            print(arr)
            return arr
        else:
            return generate_random_puzzle(piece_types, num_pieces)  # 如果不可解，重新生成
