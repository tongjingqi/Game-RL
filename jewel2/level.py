# level.py
import json
import os
from chessboard import Chessboard

class Level:
    def __init__(self, chessboard: Chessboard):
        self.chessboard = chessboard
        self.total_cleared = 0

    def clear_chess(self, x: int, y: int) -> bool:
        cleared = self.chessboard.clear_chess(x, y)
        if cleared > 0:
            self.total_cleared += cleared
            return True
        else:
            return False

    def swap_chess(self, x: int, y: int, pos: str) -> bool:
        cleared_before = self.total_cleared
        success = self.chessboard.swap_chess(x, y, pos)
        if success:
            # Count the number of eliminations after this swap
            cleared = self.chessboard.score - cleared_before
            self.total_cleared += cleared
            return True
        else:
            return False

    def restart(self):
        self.chessboard = Chessboard(self.chessboard.randomizer)
        self.total_cleared = 0

    def give_up(self):
        print("You give up!")
        print(f"Total elements cleared: {self.total_cleared}")

    def print_status(self):
        print(f"Total elements cleared: {self.total_cleared}")
        self.chessboard.print_board()

    def save_game_state(self, filename: str = "game_state.json", directory: str = "states"):
        """
        Save the current game state to a JSON file.

        Parameters:
        - filename: The name of the JSON file to save, e.g., "game_state.json". Defaults to "game_state.json".
        - directory: The directory to save the file, e.g., "states". Defaults to "states".
        """
        data = {
            "rows": self.chessboard.size,
            "cols": self.chessboard.size,
            "chessboard": self.chessboard.chessboard,
            "total_cleared": self.total_cleared
        }

        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)

        # Construct the full file path
        filepath = os.path.join(directory, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Game state has been saved to '{filepath}'.")
        except Exception as e:
            print(f"Error saving game state: {e}")
