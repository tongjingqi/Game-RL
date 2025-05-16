from typing import List, Optional, Iterator, Tuple
import json

class Square:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    @staticmethod
    def all() -> Iterator['Square']:
        for idx in range(64):
            yield Square(idx // 8, idx % 8)

    def is_valid(self) -> bool:
        return 0 <= self.row < 8 and 0 <= self.col < 8

    def row_char(self) -> str:
        return chr(ord('8') - self.row)

    def col_char(self) -> str:
        return chr(ord('a') + self.col)

    def idx(self) -> int:
        return 8 * self.row + self.col

    def offset(self, row_offset: int, col_offset: int) -> Optional['Square']:
        new_square = Square(self.row + row_offset, self.col + col_offset)
        return new_square if new_square.is_valid() else None

    def offset_iter(self, row_offset: int, col_offset: int) -> Iterator['Square']:
        current = self.offset(row_offset, col_offset)
        while current:
            yield current
            current = current.offset(row_offset, col_offset)

    def __str__(self):
        return f"{self.col_char()}{self.row_char()}"


class Piece:
    PAWN = "Pawn"
    ROOK = "Rook"
    BISHOP = "Bishop"
    KNIGHT = "Knight"
    QUEEN = "Queen"
    KING = "King"

    def __init__(self, name: str):
        self.name = name

    def offsets(self) -> List[Tuple[int, int]]:
        if self.name == Piece.PAWN:
            return [(-1, -1), (-1, 1)]
        if self.name == Piece.ROOK:
            return [(-1, 0), (0, -1), (0, 1), (1, 0)]
        if self.name == Piece.BISHOP:
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if self.name == Piece.KNIGHT:
            return [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        if self.name in (Piece.QUEEN, Piece.KING):
            return [(-1, 0), (0, -1), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def long_range(self) -> bool:
        return self.name in (Piece.ROOK, Piece.BISHOP, Piece.QUEEN)

    def __str__(self):
        return self.name


class Move:
    def __init__(self, src_piece: Piece, src_square: Square, dst_piece: Optional[Piece], dst_square: Square):
        self.src_piece = src_piece
        self.src_square = src_square
        self.dst_piece = dst_piece
        self.dst_square = dst_square

    def __str__(self):
        return f"{self.src_piece} from {self.src_square} to {self.dst_square}"

class Board:
    def __init__(self, puzzle: str):
        self.board = [None] * 64
        idx = 0
        piece_map = {'P': Piece.PAWN, 'R': Piece.ROOK, 'B': Piece.BISHOP,
                     'N': Piece.KNIGHT, 'Q': Piece.QUEEN, 'K': Piece.KING}
        for ch in puzzle:
            if ch.isdigit():
                idx += int(ch)
            elif ch in piece_map:
                self.board[idx] = Piece(piece_map[ch])
                idx += 1

    def piece_count(self) -> int:
        return sum(1 for square in self.board if square is not None)

    def __getitem__(self, square: Square) -> Optional[Piece]:
        return self.board[square.idx()]

    def __setitem__(self, square: Square, piece: Optional[Piece]):
        self.board[square.idx()] = piece

    def get_piece_positions(self):
        """
        获取棋盘上所有棋子的位置
        返回格式: [(piece_name, position_str), ...]
        """
        pieces = []
        for idx in range(64):
            piece = self.board[idx]
            if piece is not None:
                square = Square(idx // 8, idx % 8)
                pieces.append((piece.name, str(square)))
        return pieces

    def make_move(self, move: Move):
        self[move.src_square] = None
        self[move.dst_square] = move.src_piece

    def undo_move(self, move: Move):
        self[move.src_square] = move.src_piece
        self[move.dst_square] = move.dst_piece

    def moves(self) -> List[Move]:
        moves = []
        for square in Square.all():
            if self[square] is not None:
                self.collect_moves(square, moves)
        return moves

    def collect_moves(self, src_square: Square, moves: List[Move]):
        src_piece = self[src_square]
        for row_offset, col_offset in src_piece.offsets():
            if src_piece.long_range():
                for dst_square in src_square.offset_iter(row_offset, col_offset):
                    dst_piece = self[dst_square]
                    if dst_piece is not None:
                        moves.append(Move(src_piece, src_square, dst_piece, dst_square))
                        break
                    
            else:
                dst_square = src_square.offset(row_offset, col_offset)
                if dst_square and (dst_piece := self[dst_square]) is not None:
                    moves.append(Move(src_piece, src_square, dst_piece, dst_square))


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

class TraceSolver:
    def __init__(self, board: Board):
        self.board = board  # 当前棋盘状态
        self.trace = []  # 用于记录整个回溯过程

    def solve(self):
        """主方法，返回完整解答路径和回溯过程"""
        moves = []  # 存储成功路径
        piece_count = self.board.piece_count()
        self._solve(1,piece_count, moves)  # 开始递归求解
        return moves, self.trace

    def _solve(self, num_step: int, piece_count: int, moves: List[Move]) -> bool:
        """
        回溯求解。
        - piece_count: 当前棋盘上的剩余棋子数量
        - moves: 存储当前成功路径的列表
        """
        # 递归结束条件：棋盘上只剩一个棋子
        if piece_count == 1:
            self.trace.append(f"Success: Only one piece remains.")
            return True

        # 遍历所有可能的移动
        for move in self.board.moves():
            self.trace.append(f"Try step {num_step}: move {move.src_piece} in {move.src_square} to capture {move.dst_piece} in {move.dst_square}.")
            # 执行这一步移动
            self.board.make_move(move)
            moves.append(move)

            # 递归调用
            if self._solve(num_step + 1,piece_count - 1, moves):
                return True  # 找到解，返回

            # 回溯：撤销这一步移动
            moves.pop()
            self.board.undo_move(move)
            self.trace.append(f"Backtrack step {num_step}: move {move.src_piece} from {move.dst_square} to {move.src_square} and release {move.dst_piece} back to {move.dst_square}.")

        # 所有移动尝试均失败
        self.trace.append(f"Fail: No moves left with {piece_count} pieces.")
        return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python chess_ranger.py <puzzle>")
        sys.exit(1)

    puzzle = sys.argv[1]
    puzzle = Board(puzzle)

    positions = puzzle.get_piece_positions()
    for piece_name, position in positions:
        print(f"{piece_name} at {position}")

    all_moves = puzzle.moves()
    
    # 打印所有合法的棋步
    for move in all_moves:
        print(move)

    print("the solve steps are:")

    solver = Solver(puzzle)

    solver_type = solver.solve()

    step = ''
    for piece, src, dst in solver_type:
        step += f"move {piece} from {src} to {dst}." 

    print(step)
    '''
    trace_solver = TraceSolver(puzzle)  # 初始化TraceSolver

    # 调用solve方法
    solution, trace = trace_solver.solve()

    # 输出解答步骤和完整回溯过程
    print("Solution:")
    if solution:
        for step in solution:
            print(f"{step.src_piece} from {step.src_square} to {step.dst_square}")
    else:
        print("No solution found.")

    '''
    '''
    print("\nTrace:")
    entries = ""
    for entry in trace:
        print(entry)
        entries+=entry
    

    print("\nTrace:")
    entries = []
    for entry in trace:
        print(entry)
        entries.append(entry)
    '''
