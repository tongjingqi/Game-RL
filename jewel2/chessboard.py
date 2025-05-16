# chessboard.py
from typing import List, Tuple

class Chessboard:
    def __init__(self, randomizer, size=5):
        self.size = size  # Dynamic chessboard size
        self.normal_elements = ['A', 'B', 'C', 'D', 'E']
        self.special_elements = ['a', 'b', 'c', 'd', 'e', '+', '|']
        self.randomizer = randomizer
        self.chessboard = self.generate_random_board()
        self.signboard = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score = 0  # Total number of eliminations

    def generate_random_board(self) -> List[List[str]]:
        return [[self.randomizer.next_chess() for _ in range(self.size)] for _ in range(self.size)]

    def print_board(self):
        for row in self.chessboard:
            print(' '.join(row))
        print()

    def reset_signboard(self):
        for i in range(self.size):
            for j in range(self.size):
                self.signboard[i][j] = 0

    def clear_chess(self, x: int, y: int) -> int:
        self.reset_signboard()
        if not self.check_chess(x, y):
            # print("Cannot clear at the specified position.")
            return 0
        else:
            cleared = self.delete_chess()
            self.fill_chess()
            return cleared

    def delete_chess(self) -> int:
        cleared = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.signboard[i][j] == 1:
                    # Count all eliminated elements, including normal and special elements
                    if (self.chessboard[i][j] in self.normal_elements or
                        self.chessboard[i][j] in self.special_elements):
                        cleared += 1
                    self.chessboard[i][j] = ' '
        self.score += cleared
        # print(f"Total cleared this operation: {cleared}")
        return cleared

    def check_special_character(self, target: str, x: int, y: int):
        # Handle special elements and mark elements for clearing
        if target in ['a', 'b', 'c', 'd', 'e']:
            # 'a'-'e': Clear all corresponding uppercase letters and itself
            uppercase_target = target.upper()
            for i in range(self.size):
                for j in range(self.size):
                    if self.chessboard[i][j] == uppercase_target:
                        self.signboard[i][j] = 1
            # Also mark itself
            self.signboard[x][y] = 1
        elif target == '|':
            # Clear the entire column, including itself
            for i in range(self.size):
                self.signboard[i][y] = 1
        elif target == '+':
            # Clear all elements within a distance <= 1, including itself
            for i in range(x-1, x+2):
                for j in range(y-1, y+2):
                    if 0 <= i < self.size and 0 <= j < self.size:
                        self.signboard[i][j] = 1

    def mark_elements_for_special(self, x: int, y: int):
        target = self.chessboard[x][y]
        self.check_special_character(target, x, y)

    def mark_elements_for_line(self, x: int, y: int) -> bool:
        # Check whether there are three or more identical elements in a horizontal or vertical line
        target = self.chessboard[x][y]
        marked = False

        # Check horizontal line
        horizontal = self.get_horizontal_line(x, y)
        if len(horizontal) >= 3:
            for (i, j) in horizontal:
                self.signboard[i][j] = 1
            marked = True

        # Check vertical line
        vertical = self.get_vertical_line(x, y)
        if len(vertical) >= 3:
            for (i, j) in vertical:
                self.signboard[i][j] = 1
            marked = True

        return marked

    def check_chess(self, x: int, y: int) -> bool:
        target = self.chessboard[x][y]
        if target == ' ':
            return False

        if target in self.special_elements:
            # Handle special elements
            self.mark_elements_for_special(x, y)
            # Return True if any element is marked
            return any(self.signboard[i][j] == 1 for i in range(self.size) for j in range(self.size))
        elif target in self.normal_elements:
            # Handle normal elements and check whether elimination conditions are met
            return self.mark_elements_for_line(x, y)
        else:
            # Unknown elements cannot be cleared
            return False

    def get_horizontal_line(self, x: int, y: int) -> List[Tuple[int, int]]:
        target = self.chessboard[x][y]
        line = [(x, y)]
        # Check to the left
        j = y - 1
        while j >= 0 and self.chessboard[x][j] == target:
            line.append((x, j))
            j -= 1
        # Check to the right
        j = y + 1
        while j < self.size and self.chessboard[x][j] == target:
            line.append((x, j))
            j += 1
        return line

    def get_vertical_line(self, x: int, y: int) -> List[Tuple[int, int]]:
        target = self.chessboard[x][y]
        line = [(x, y)]
        # Check upwards
        i = x - 1
        while i >= 0 and self.chessboard[i][y] == target:
            line.append((i, y))
            i -= 1
        # Check downwards
        i = x + 1
        while i < self.size and self.chessboard[i][y] == target:
            line.append((i, y))
            i += 1
        return line

    def fill_chess(self):
        for j in range(self.size):
            # Fill from the bottom up
            for i in range(self.size - 1, -1, -1):
                if self.chessboard[i][j] == ' ':
                    # Find the first non-empty cell
                    k = i - 1
                    while k >= 0 and self.chessboard[k][j] == ' ':
                        k -= 1
                    if k >= 0:
                        self.chessboard[i][j] = self.chessboard[k][j]
                        self.chessboard[k][j] = ' '
                    else:
                        # Generate a new element
                        self.chessboard[i][j] = self.randomizer.next_chess()

    def swap_chess(self, x: int, y: int, pos: str) -> bool:
        direction_map = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }

        if pos not in direction_map:
            # print("Invalid direction. Use one of: up, down, left, right.")
            return False

        dx, dy = direction_map[pos]
        nx, ny = x + dx, y + dy

        if not (0 <= nx < self.size and 0 <= ny < self.size):
            # print("Swap direction out of range.")
            return False

        # Check for special elements
        elem1 = self.chessboard[x][y]
        elem2 = self.chessboard[nx][ny]
        if elem1 in self.special_elements or elem2 in self.special_elements:
            # print("Cannot swap involving special elements.")
            return False

        # Swap elements
        self.chessboard[x][y], self.chessboard[nx][ny] = self.chessboard[nx][ny], self.chessboard[x][y]

        # Check if elimination conditions are formed
        self.reset_signboard()
        cleared_after_swap = 0

        """
        if self.check_chess(x, y):
            cleared_after_swap += self.delete_chess()
            self.fill_chess()

        self.reset_signboard()

        if self.check_chess(nx, ny):
            cleared_after_swap += self.delete_chess()
            self.fill_chess()
        """

        check1 = self.check_chess(x, y)
        check2 = self.check_chess(nx, ny)

        if check1 or check2:
            cleared_after_swap += self.delete_chess()
            self.fill_chess()

        self.reset_signboard()

        if cleared_after_swap > 0:
            return True
        else:
            # Swap back
            self.chessboard[x][y], self.chessboard[nx][ny] = self.chessboard[nx][ny], self.chessboard[x][y]
            # print("Swap did not result in any eliminations.")
            return False

    def get_value(self, i: int, j: int) -> str:
        return self.chessboard[i][j]

    def set_value(self, i: int, j: int, value: str):
        self.chessboard[i][j] = value
