from dataclasses import dataclass

@dataclass
class AIRecommendation:
    move_count: int
    level: str
    options: str
    reason: str

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
    
    def print_board(self):
        print('---------')
        for i in range(0, 9, 3):
            print(f'|{self.board[i]}|{self.board[i+1]}|{self.board[i+2]}|')
            print('---------')

    def get_empty_cells(self):
        return [i for i, cell in enumerate(self.board) if cell == ' ']
    
    def get_lines(self):
        """Returns all possible winning lines"""
        return [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]

    def get_line_description(self, line):
        """Convert winning line to readable description"""
        if line == [0, 1, 2]: return "Row 0"
        if line == [3, 4, 5]: return "Row 1"
        if line == [6, 7, 8]: return "Row 2"
        if line == [0, 3, 6]: return "Column 0"
        if line == [1, 4, 7]: return "Column 1"
        if line == [2, 5, 8]: return "Column 2"
        if line == [0, 4, 8]: return "Top-left to bottom-right diagonal"
        if line == [2, 4, 6]: return "Bottom-left to top-right diagonal"
        return str(line)
    
    def find_winning_line(self, position, player):
        """Find winning line after placing piece at position"""
        if self.board[position] != ' ':
            return None
            
        self.board[position] = player
        winning_line = None
        for line in self.get_lines():
            if self.board[line[0]] == self.board[line[1]] == self.board[line[2]] == player:
                winning_line = line
                break
        self.board[position] = ' '
        return winning_line
    
    def find_winning_move(self, player):
        """Check for immediate winning moves"""
        empty_cells = self.get_empty_cells()
        winning_moves = []
        for pos in empty_cells:
            if self.find_winning_line(pos, player):
                winning_moves.append(pos)
        return winning_moves

    def find_double_threat_lines(self, position, player):
        """Find two lines that form a double threat after placing piece"""
        if self.board[position] != ' ':
            return None
            
        opponent = 'O' if player == 'X' else 'X'
        threat_lines = []
        
        for line in self.get_lines():
            if position in line:
                pieces = [self.board[i] for i in line]
                if pieces.count(player) == 1 and pieces.count(opponent) == 0:
                    threat_lines.append(line)
        
        return threat_lines if len(threat_lines) >= 2 else None
    
    def find_double_threat_move(self, player):
        """Find position that creates double threat"""
        empty_cells = self.get_empty_cells()
        for pos in empty_cells:
            threat_lines = self.find_double_threat_lines(pos, player)
            if threat_lines and len(threat_lines) >= 2:
                return pos
        return None

    def find_best_move(self, player):
        """Find best move by strict priority order and provide detailed reason"""
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return None, "Board is full"
            
        opponent = 'O' if player == 'X' else 'X'
        
        # 1. Check for immediate win
        winning_moves = self.find_winning_move(player)
        if winning_moves:
            pos = winning_moves[0]
            position = (pos // 3, pos % 3)
            winning_line = self.find_winning_line(pos, player)
            return pos, f"Current player is {player}, opponent is {opponent}. Player {player} can win on {self.get_line_description(winning_line)}, so player {player} should choose position {position}"
            
        # 2. Check opponent's immediate win threat
        opponent_winning_moves = self.find_winning_move(opponent)
        if len(opponent_winning_moves) > 1:
            lines = [self.find_winning_line(pos, opponent) for pos in opponent_winning_moves]
            line_desc = [self.get_line_description(line) for line in lines]
            return None, f"Current player is {player}, opponent is {opponent}. Opponent {opponent} has multiple winning moves on {', '.join(line_desc)}, cannot block all"
        elif len(opponent_winning_moves) == 1:
            pos = opponent_winning_moves[0]
            position = (pos // 3, pos % 3)
            winning_line = self.find_winning_line(pos, opponent)
            return pos, f"Current player is {player}, opponent is {opponent}. Must block opponent {opponent}'s winning threat on {self.get_line_description(winning_line)}, so player {player} should choose position {position}"
            
        # 3. Check for double threat creation
        double_threat_move = self.find_double_threat_move(player)
        if double_threat_move is not None:
            position = (double_threat_move // 3, double_threat_move % 3)
            threat_lines = self.find_double_threat_lines(double_threat_move, player)
            if threat_lines:
                line_desc = [self.get_line_description(line) for line in threat_lines[:2]]
                return double_threat_move, f"Current player is {player}, opponent is {opponent}. Player {player} can create double threat on {line_desc[0]} and {line_desc[1]}, so player {player} should choose position {position}"
            
        # 4. Check if need to block opponent's double threat
        opponent_double_threat = self.find_double_threat_move(opponent)
        if opponent_double_threat is not None:
            threat_lines = self.find_double_threat_lines(opponent_double_threat, opponent)
            if threat_lines:
                line_desc = [self.get_line_description(line) for line in threat_lines[:2]]
                position = (opponent_double_threat // 3, opponent_double_threat % 3)
                return opponent_double_threat, f"Current player is {player}, opponent is {opponent}. Must block opponent {opponent}'s potential double threat on {line_desc[0]} and {line_desc[1]}, so player {player} should choose position {position}"
            
        # 5. Choose first available position
        position = (empty_cells[0] // 3, empty_cells[0] % 3)
        return empty_cells[0], f"Current player is {player}, opponent is {opponent}. No special cases, player {player} chooses first available position {position}"
    
    def convert_2d_to_1d(self, board_2d):
        """Convert 2D board to 1D board"""
        return [cell for row in board_2d for cell in row]
    
    def get_ai_suggestion(self, board_2d, player):
        """Interface method for the dataset generator"""
        self.board = self.convert_2d_to_1d(board_2d)
        pos, reason = self.find_best_move(player)
        
        if pos is None:
            return AIRecommendation(
                move_count=0,
                level="Hard",
                options="A",
                reason=reason
            )
        
        row = pos // 3
        col = pos % 3
        chess_dict = {
            'None': 'A', (0, 0): 'B', (0, 1): 'C', (0, 2): 'D', 
            (1, 0): 'E', (1, 1): 'F', (1, 2): 'G',
            (2, 0): 'H', (2, 1): 'I', (2, 2): 'J'
        }
        option = chess_dict[(row, col)]
        
        level = "Hard"
        if "win" in reason.lower():
            level = "Easy"
        elif "threat" in reason.lower():
            level = "Medium"
            
        return AIRecommendation(
            move_count=1,
            level=level,
            options=option,
            reason=reason+'.'
        )