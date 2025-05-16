# minesweeper.py

import random
import json
import os

class Minesweeper:
    def __init__(self, rows=10, cols=10, mines=15):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.mine_board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flagged = [[False for _ in range(cols)] for _ in range(rows)]  # Flagging the state of mines
        self.first_click = True

    def _place_mines(self, exclude_row, exclude_col):
        # Randomly place mines, avoiding the first click position and its surrounding area
        placed_mines = 0
        while placed_mines < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            # Avoid the initial click position and its surrounding tiles
            if (row >= exclude_row - 1 and row <= exclude_row + 1 and
                col >= exclude_col - 1 and col <= exclude_col + 1):
                continue
            if self.mine_board[row][col] == 'M':
                continue
            self.mine_board[row][col] = 'M'
            placed_mines += 1

    def _calculate_adjacent_mines(self):
        # Calculate the number of mines around each position
        for r in range(self.rows):
            for c in range(self.cols):
                if self.mine_board[r][c] == 'M':
                    continue
                mine_count = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        nr, nc = r + i, c + j
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and self.mine_board[nr][nc] == 'M':
                            mine_count += 1
                self.mine_board[r][c] = mine_count

    def display_board(self, reveal_all=False):
        # Calculate the number of flagged mines
        flagged_count = sum(sum(row) for row in self.flagged)
        remaining_mines = self.mines - flagged_count

        # Display mine statistics
        print(f"Remaining mines: {remaining_mines} | Flagged: {flagged_count}")

        # Display the current revealed board; if reveal_all is True, show all mines
        print("  ", end="")  # Top offset
        for col_num in range(self.cols):
            print(f"{col_num:2}", end=" ")
        print()

        for r in range(self.rows):
            print(f"{r:2} ", end="")  # Row number
            for c in range(self.cols):
                if reveal_all and self.mine_board[r][c] == 'M':
                    print('M ', end=' ')
                elif self.flagged[r][c]:
                    print('F ', end=' ')  # Marked as a mine
                elif self.revealed[r][c]:
                    print(f"{self.mine_board[r][c]} ", end=' ')
                else:
                    print('- ', end=' ')
            print()

    def reveal(self, row, col):
        # Place mines on the first click, calculate adjacent mine numbers, and auto-reveal safe areas
        if self.first_click:
            self._place_mines(row, col)
            self._calculate_adjacent_mines()
            self.first_click = False

        # If the revealed area is not a mine, continue recursively revealing surrounding safe areas
        if self.mine_board[row][col] == 'M':
            print("Boom! You hit a mine!")
            return False

        # If the tile is flagged, remove the flag
        if self.flagged[row][col]:
            self.flagged[row][col] = False

        # Continue recursive revealing
        self._reveal_recursive(row, col)
        return True

    def _reveal_recursive(self, row, col):
        # Recursively reveal surrounding safe tiles
        if self.revealed[row][col] or self.mine_board[row][col] == 'M':
            return
        self.revealed[row][col] = True
        if self.mine_board[row][col] == 0:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    nr, nc = row + i, col + j
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self._reveal_recursive(nr, nc)

    def toggle_flag(self, row, col):
        # Toggle the flagging state
        if not self.revealed[row][col]:  # Only un-revealed tiles can be flagged
            self.flagged[row][col] = not self.flagged[row][col]

    def is_won(self):
        # Determine if the game has been won
        for r in range(self.rows):
            for c in range(self.cols):
                if self.mine_board[r][c] != 'M' and not self.revealed[r][c]:
                    return False
        return True
    
    def state_around(self):
        """
        Identify the boundary between revealed and unrevealed tiles and return the coordinates of unrevealed tiles on the boundary, along with whether they are mines.
    
        :return: A list of dictionaries, each containing the coordinates of an unrevealed boundary tile and whether it is a mine.
        """
        boundary_cells = []

        for r in range(self.rows):
            for c in range(self.cols):
                # If the current tile is not revealed
                if not self.revealed[r][c]:
                    # Check if there are revealed neighbors
                    has_revealed_neighbor = False
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            nr, nc = r + i, c + j
                            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.revealed[nr][nc]:
                                has_revealed_neighbor = True
                                break
                        if has_revealed_neighbor:
                            break

                    # If there are revealed neighbors, the current tile is a boundary tile
                    if has_revealed_neighbor:
                        boundary_cells.append({
                            "row": r,
                            "col": c,
                            "is_mine": self.mine_board[r][c] == 'M'
                        })

        return boundary_cells

    def save_state(self, filename="game_state.json", directory="states"):
        """
        Save the current game state to a file
        :param filename: The name of the save file
        :param directory: The save directory
        """
        # Ensure the save directory exists
        os.makedirs(directory, exist_ok=True)

        # Assemble state data
        state_data = {
            "rows": self.rows,
            "cols": self.cols,
            "mines": self.mines,
            "mine_board": self.mine_board,
            "revealed": self.revealed,
            "flagged": self.flagged,
            "first_click": self.first_click,
        }

        # Save as a JSON file
        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as file:
            json.dump(state_data, file, indent=4)

        print(f"Game state saved to {filepath}.")

    def auto_flagger(self, num=1):
        """
        Automatically flag up to a certain number of mines
        :param num: Maximum number of mines to flag
        """
        count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                # Stop flagging if the required number is reached
                if count >= num:
                    return
            
                # If the current tile is not revealed
                if not self.revealed[r][c]:
                    # Check if there are revealed neighbors
                    has_revealed_neighbor = False
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            nr, nc = r + i, c + j
                            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.revealed[nr][nc]:
                                has_revealed_neighbor = True
                                break
                        if has_revealed_neighbor:
                            break
                
                    # If the tile is a boundary tile and is a mine, flag it
                    if has_revealed_neighbor:
                        if self.mine_board[r][c] == 'M':
                            self.flagged[r][c] = True
                            count += 1
                            # Exit if the required number is reached
                            if count >= num:
                                return

def play_game():
    # Provide a choice between default and custom configurations
    print("Welcome to Minesweeper!")
    choice = input("Enter 'd' for default configuration or 'c' for custom configuration: ").strip().lower()

    if choice == 'c':
        rows = int(input("Enter number of rows: "))
        cols = int(input("Enter number of columns: "))
        mines = int(input("Enter number of mines: "))
        if mines >= rows * cols:
            print("Too many mines! Setting mines to a maximum of rows * columns - 1.")
            mines = rows * cols - 1
    else:
        rows, cols, mines = 10, 10, 15  # Default configuration

    game = Minesweeper(rows, cols, mines)

    while True:
        game.display_board()
        row = int(input(f"Enter row (0-{rows - 1}): "))
        col = int(input(f"Enter col (0-{cols - 1}): "))
        
        if not (0 <= row < rows and 0 <= col < cols):
            print("Invalid input. Try again.")
            continue
        
        action = input("Enter 'r' to reveal or 'f' to flag/unflag: ").strip().lower()
        if action == 'r':
            if not game.reveal(row, col):
                # Game over, reveal all mines
                game.display_board(reveal_all=True)
                print("Game over!")
                break
        elif action == 'f':
            game.toggle_flag(row, col)
        else:
            print("Invalid action. Try again.")
            continue

        if game.is_won():
            game.display_board()
            print("Congratulations! You won!")
            break


if __name__ == "__main__":
    play_game()
