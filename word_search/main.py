import random
import json
import os
import string
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple, Set
from enum import Enum
from dataclasses import dataclass

class QuestionType(Enum):
    CELL_LETTER = "cell_letter"
    LETTER_COUNT = "letter_count"
    WORD_DIRECTION = "word_direction"
    FIND_WORD_LOCATION = "find_word_location"

@dataclass
class GridPosition:
    row: int
    col: int

class WordSearchGrid:
    def __init__(self, size: int):
        self.size = size
        self.grid = [[random.choice(string.ascii_uppercase) for _ in range(size)] for _ in range(size)]
        
    def get_cell(self, pos: GridPosition) -> str:
        return self.grid[pos.row][pos.col]
    
    def set_cell(self, pos: GridPosition, letter: str):
        self.grid[pos.row][pos.col] = letter
    
    def count_letter(self, letter: str) -> List[GridPosition]:
        positions = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == letter:
                    positions.append(GridPosition(i, j))
        return positions

    def insert_word(self, word: str, start_pos: GridPosition, direction: Tuple[int, int]) -> bool:
        temp_grid = [row[:] for row in self.grid]
        curr_pos = start_pos
        
        for letter in word:
            if (0 <= curr_pos.row < self.size and 
                0 <= curr_pos.col < self.size):
                temp_grid[curr_pos.row][curr_pos.col] = letter
                curr_pos = GridPosition(
                    curr_pos.row + direction[0],
                    curr_pos.col + direction[1]
                )
            else:
                return False
                
        self.grid = temp_grid
        return True

class QuestionGenerator:
    with open('words.txt') as f:
        words = f.read().splitlines()
        words = [word.upper() for word in words]
    def __init__(self):
        self.directions = {
            "right": (0, 1),
            "down": (1, 0),
            "diagonal-right-down": (1, 1),
            "diagonal-right-up": (-1, 1),
            "diagonal-left-down": (1, -1),
            "diagonal-left-up": (-1, -1),
            "up": (-1, 0),
            "left": (0, -1)
        }
        self.words = QuestionGenerator.words
    
    def generate_cell_letter_question(self, grid: WordSearchGrid) -> Dict:
        row = random.randint(0, grid.size - 1)
        col = random.randint(0, grid.size - 1)
        correct_letter = grid.get_cell(GridPosition(row, col))
        
        # Generate options including the correct letter
        options = [correct_letter]
        while len(options) < 8:
            letter = random.choice(string.ascii_uppercase)
            if letter not in options:
                options.append(letter)
        
        random.shuffle(options)
        correct_index = options.index(correct_letter) + 1
        
        return {
            "qa_type": "cell_letter",
            "question": f"Rules:\n1. The grid contains uppercase letters.\n2. Row and column indexes begin from 1 at the top-left corner.\n\nQuestion:\nWhat letter is at row {row + 1}, column {col + 1}?\n\nOptions:\n" + "\n".join([f"{i+1}: {opt}" for i, opt in enumerate(options)]),
            "answer": correct_index,
            "options": options,
            "analysis": f"The letter at position ({row + 1}, {col + 1}) is {correct_letter}. So the answer is Option {correct_index}."
        }

    def generate_letter_count_question(self, grid: WordSearchGrid) -> Dict:
        letter = random.choice(string.ascii_uppercase)
        positions = grid.count_letter(letter)
        count = len(positions)
        
        # Generate options including the correct count
        options = [count]
        upper=2
        while len(options) < 8:
            fake_count = random.randint(0, upper)
            upper=upper+1
            if fake_count not in options:
                options.append(fake_count)
        
        random.shuffle(options)
        correct_index = options.index(count) + 1
        
        # Create analysis with positions
        analysis = f"Let's find all occurrences of letter '{letter}' by scanning the grid row by row:\n"
        for pos in positions:
            analysis += f"- Found at row {pos.row + 1}, column {pos.col + 1}\n"
        analysis += f"\nAfter scanning the entire grid, letter '{letter}' appears {count} times in total. Therefore, the answer is Option {correct_index}."
        
        return {
            "qa_type": "letter_count",
            "question": f"Rules:\n1. The grid contains uppercase letters.\n2. Count all occurrences of the specified letter.\n\nQuestion:\nHow many times does the letter '{letter}' appear in the grid?\n\nOptions:\n" + "\n".join([f"{i+1}: {opt}" for i, opt in enumerate(options)]),
            "answer": correct_index,
            "options": options,
            "analysis": analysis
        }

    def generate_word_direction_question(self, grid: WordSearchGrid) -> Dict:
        # Place a word in the grid first
        word = random.choice(self.words)
        direction_name = random.choice(list(self.directions.keys()))
        direction = self.directions[direction_name]
        
        # Find valid starting position
        valid_starts = []
        for i in range(grid.size):
            for j in range(grid.size):
                start_pos = GridPosition(i, j)
                if self._can_place_word(grid, word, start_pos, direction):
                    valid_starts.append(start_pos)
        
        if not valid_starts:
            return self.generate_cell_letter_question(grid)  # Fallback
            
        start_pos = random.choice(valid_starts)
        grid.insert_word(word, start_pos, direction)
        
        # Generate options
        options = list(self.directions.keys())
        random.shuffle(options)
        correct_index = options.index(direction_name) + 1
        
        return {
            "qa_type": "word_direction",
            "question": f"Rules:\n1. This is a word search game. Words can be placed in different directions: right, down, diagonal, up, or left.\n2. Starting from position (row {start_pos.row + 1}, column {start_pos.col + 1}), in which direction can you find the word '{word}'?\n\nOptions:\n" + "\n".join([f"{i+1}: {opt}" for i, opt in enumerate(options)]),
            "answer": correct_index,
            "options": options,
            "analysis": self._generate_direction_analysis(grid, word, start_pos, direction_name, options)
        }

    def _generate_direction_analysis(self, grid: WordSearchGrid, word: str, start_pos: GridPosition, direction_name: str, options: List[str]) -> str:
        """Generate detailed analysis for word direction questions with comprehensive checking."""
        analysis = f"Let's analyze the word '{word}' starting from position (row {start_pos.row + 1}, column {start_pos.col + 1}):\n\n"
        
        # Step 1: Initial position analysis
        analysis += f"1. Starting position contains '{word[0]}'. Let's examine all possible directions:\n"
        
        # Step 2: Systematic direction checking
        found_matches = []
        for dir_name, (dy, dx) in self.directions.items():
            analysis += f"\nChecking {dir_name} direction:\n"
            
            # Check each letter in the word
            curr_pos = start_pos
            valid_sequence = True
            sequence_analysis = f"   Sequence found: {word[0]}"
            
            for i, letter in enumerate(word[1:], 1):  # Start from second letter
                new_row = curr_pos.row + dy
                new_col = curr_pos.col + dx
                
                if 0 <= new_row < grid.size and 0 <= new_col < grid.size:
                    curr_pos = GridPosition(new_row, new_col)
                    found_letter = grid.get_cell(curr_pos)
                    sequence_analysis += f" → {found_letter}"
                    
                    if found_letter != letter:
                        analysis += f"   - Position ({curr_pos.row + 1}, {curr_pos.col + 1}): Expected '{letter}', found '{found_letter}'\n"
                        valid_sequence = False
                        break
                else:
                    analysis += f"   - Position ({new_row + 1}, {new_col + 1}): Out of grid boundaries\n"
                    valid_sequence = False
                    break
                    
                if i == 1:  # After checking second letter
                    analysis += f"   - Second letter '{letter}' found at ({curr_pos.row + 1}, {curr_pos.col + 1})\n"
            
            if valid_sequence:
                found_matches.append(dir_name)
                analysis += f"   - Complete sequence: {sequence_analysis}\n"
                analysis += f"   ✓ Valid word '{word}' found in {dir_name} direction!\n"
            else:
                analysis += "   × This direction does not contain the complete word\n"
        
        # Step 3: Conclusion
        if len(found_matches) > 1:
            analysis += f"\n3. Multiple valid directions found: {', '.join(found_matches)}\n"
            if direction_name in found_matches:
                analysis += f"   However, the question asks about the specific placement at ({start_pos.row + 1}, {start_pos.col + 1}) going {direction_name}.\n"
        elif len(found_matches) == 1:
            analysis += f"\n3. Only one valid direction found: {found_matches[0]}\n"
        else:
            analysis += "\n3. No valid directions found (this shouldn't happen in a properly generated puzzle)\n"
        
        # Final answer
        correct_index = options.index(direction_name) + 1
        analysis += f"\nTherefore, the answer is Option {correct_index}: {direction_name}"
        
        return analysis

    def generate_find_word_location_question(self, grid: WordSearchGrid) -> Dict:
        """Generate a question asking to find a word's location and direction without giving starting position."""
        word = random.choice(self.words)
        first_letter = word[0]
        
        # Place the word in the grid
        valid_placements = []
        for i in range(grid.size):
            for j in range(grid.size):
                start_pos = GridPosition(i, j)
                for dir_name, direction in self.directions.items():
                    if self._can_place_word(grid, word, start_pos, direction):
                        valid_placements.append((start_pos, dir_name, direction))
        
        if not valid_placements:
            return self.generate_cell_letter_question(grid)  # Fallback
            
        # Choose a random valid placement
        start_pos, direction_name, direction = random.choice(valid_placements)
        grid.insert_word(word, start_pos, direction)
        
        # Create combined position-direction options
        all_positions = []
        for i in range(grid.size):
            for j in range(grid.size):
                if grid.get_cell(GridPosition(i, j)) == first_letter:
                    for dir_name in self.directions.keys():
                        all_positions.append((i, j, dir_name))
                        
        # Select random positions for incorrect options
        options = []
        correct_option = f"Row {start_pos.row + 1}, Column {start_pos.col + 1}, Direction: {direction_name}"
        options.append(correct_option)
        
        other_positions = [pos for pos in all_positions 
                          if not (pos[0] == start_pos.row and 
                                pos[1] == start_pos.col and 
                                pos[2] == direction_name)]
        
        # Add 3 random incorrect options
        for _ in range(7):
            if other_positions:
                row, col, dir_name = random.choice(other_positions)
                other_positions.remove((row, col, dir_name))
                options.append(f"Row {row + 1}, Column {col + 1}, Direction: {dir_name}")
            else:
                # Generate completely random option if needed
                random_row = random.randint(0, grid.size - 1)
                random_col = random.randint(0, grid.size - 1)
                random_dir = random.choice(list(self.directions.keys()))
                options.append(f"Row {random_row + 1}, Column {random_col + 1}, Direction: {random_dir}")
        
        random.shuffle(options)
        correct_index = options.index(correct_option) + 1
        
        return {
            "qa_type": "find_word_location",
            "question": f"Rules:\n1. This is a word search game. Words can be placed in different directions: right, down, diagonal-right-down, diagonal-right-up, diagonal-left-down, diagonal-left-up, up, or left.\n2. Words read from start to end in the specified direction.\n\nQuestion:\nFind the word '{word}' in the grid. Where does it start and in which direction does it go?\n\nOptions:\n" + "\n".join([f"{i+1}: {opt}" for i, opt in enumerate(options)]),
            "answer": correct_index,
            "options": options,
            "analysis": self._generate_find_word_analysis(grid, word, start_pos, direction_name, options)
        }

    def _generate_find_word_analysis(self, grid: WordSearchGrid, word: str, correct_pos: GridPosition, correct_direction: str, options: List[str]) -> str:
        """Generate detailed analysis for find word location questions."""
        first_letter = word[0]
        second_letter = word[1]
        
        analysis = f"Let's find the word '{word}' systematically:\n\n"
        analysis += f"1. First, let's locate all occurrences of the first letter '{first_letter}':\n"
        
        # Find all occurrences of first letter
        first_letter_positions = []
        for i in range(grid.size):
            for j in range(grid.size):
                if grid.get_cell(GridPosition(i, j)) == first_letter:
                    first_letter_positions.append(GridPosition(i, j))
                    analysis += f"   - Found '{first_letter}' at row {i + 1}, column {j + 1}\n"
        
        analysis += f"\n2. For each '{first_letter}', let's check surrounding cells for the second letter '{second_letter}':\n"
        
        # Check each position
        for pos in first_letter_positions:
            analysis += f"\nChecking around ({pos.row + 1}, {pos.col + 1}):\n"
            flag=True
            for dir_name, (dy, dx) in self.directions.items():
                new_row = pos.row + dy
                new_col = pos.col + dx
                if 0 <= new_row < grid.size and 0 <= new_col < grid.size:
                    letter = grid.get_cell(GridPosition(new_row, new_col))
                    if letter == second_letter:
                        flag=False
                        analysis += f"   - Found '{second_letter}' {dir_name} at ({new_row + 1}, {new_col + 1})\n"
                        
                        # Check if this is the correct word
                        analysis += f"      → Checking full word in this direction...\n"
                        curr_pos = GridPosition(pos.row, pos.col)
                        found_word = ""
                        matches = True
                        
                        for idx, target_letter in enumerate(word):
                            if 0 <= curr_pos.row < grid.size and 0 <= curr_pos.col < grid.size:
                                found_letter = grid.get_cell(curr_pos)
                                found_word += found_letter
                                
                                if found_letter == target_letter:
                                    analysis += f"         Position {idx + 1}: Expected '{target_letter}', found '{found_letter}' at ({curr_pos.row + 1}, {curr_pos.col + 1}) ✓\n"
                                else:
                                    analysis += f"         Position {idx + 1}: Expected '{target_letter}', found '{found_letter}' at ({curr_pos.row + 1}, {curr_pos.col + 1}) ✗\n"
                                    matches = False
                                    break
                                
                                curr_pos = GridPosition(
                                    curr_pos.row + self.directions[dir_name][0],
                                    curr_pos.col + self.directions[dir_name][1]
                                )
                            else:
                                analysis += f"         Position {idx + 1}: Out of grid bounds at ({curr_pos.row + 1}, {curr_pos.col + 1}) ✗\n"
                                matches = False
                                break
                        
                        if matches and pos.row == correct_pos.row and pos.col == correct_pos.col and dir_name == correct_direction:
                            analysis += f"         Found complete word '{found_word}' - This is the correct position and direction! ✓\n"
                        elif matches:
                            analysis += f"         Found word '{found_word}' - But this is not the position/direction we're looking for\n"
                        else:
                            analysis += f"         Incomplete match '{found_word}' - Word comparison failed\n"
            if flag:
                analysis += f"   - '{second_letter}' not found around ({pos.row + 1}, {pos.col + 1})\n"
        
        analysis += f"\n3. The complete word '{word}' was found starting at row {correct_pos.row + 1}, column {correct_pos.col + 1}, going {correct_direction}.\n"
        analysis += f"\nTherefore, the answer is Option {options.index(f'Row {correct_pos.row + 1}, Column {correct_pos.col + 1}, Direction: {correct_direction}') + 1}."
        
        return analysis

    def _can_place_word(self, grid: WordSearchGrid, word: str, start_pos: GridPosition, direction: Tuple[int, int]) -> bool:
        curr_pos = start_pos
        for _ in word:
            if not (0 <= curr_pos.row < grid.size and 0 <= curr_pos.col < grid.size):
                return False
            curr_pos = GridPosition(
                curr_pos.row + direction[0],
                curr_pos.col + direction[1]
            )
        return True

class ImageGenerator:
    def __init__(self, cell_size: int = 50, font_size: int = 32):
        self.cell_size = cell_size
        self.font_size = font_size
        
    def create_grid_image(self, grid: WordSearchGrid, filename: str):
        width = height = (grid.size + 1) * self.cell_size
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        # Try to find a suitable font that works cross-platform
        try:
            # Try common Windows fonts first
            font = ImageFont.truetype("arial.ttf", self.font_size)
        except OSError:
            try:
                # Try common Linux fonts
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size)
            except OSError:
                try:
                    # Try macOS fonts
                    font = ImageFont.truetype("/Library/Fonts/Arial.ttf", self.font_size)
                except OSError:
                    # Fallback to default font
                    font = ImageFont.load_default()
        
        # Draw grid lines
        for i in range(grid.size + 1):
            # Vertical lines
            draw.line([(i * self.cell_size, 0), 
                      (i * self.cell_size, height)], fill='black')
            # Horizontal lines
            draw.line([(0, i * self.cell_size), 
                      (width, i * self.cell_size)], fill='black')
        
        # Draw row numbers
        for i in range(grid.size):
            draw.text(
                (5, (i + 1) * self.cell_size + 5),
                str(i + 1),
                fill='black',
                font=font
            )
            
        # Draw column numbers
        for j in range(grid.size):
            draw.text(
                ((j + 1) * self.cell_size + 15, 5),
                str(j + 1),
                fill='black',
                font=font
            )
            
        # Draw letters
        for i in range(grid.size):
            for j in range(grid.size):
                draw.text(
                    ((j + 1) * self.cell_size + 15, 
                     (i + 1) * self.cell_size + 5),
                    grid.grid[i][j],
                    fill='black',
                    font=font
                )
        
        # Save image
        image.save(filename)

class WordSearchGenerator:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.image_dir = os.path.join(output_dir, "images")
        self.state_dir = os.path.join(output_dir, "states")
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)
        
        self.question_generator = QuestionGenerator()
        self.image_generator = ImageGenerator()
        
        # Define mapping of question types to difficulty levels
        self.qa_level_mapping = {
            "cell_letter": "Easy",  # Simple cell lookup
            "letter_count": "Medium",  # Requires scanning entire grid
            "word_direction": "Medium",  # Requires understanding directions
            "find_word_location": "Hard"  # Most complex, requires finding both location and direction
        }
        
        self.qa_type_mapping={
            QuestionType.CELL_LETTER.value: "StateInfo",
            QuestionType.LETTER_COUNT.value: "StateInfo",
            QuestionType.WORD_DIRECTION.value: "TransitionPath",
            QuestionType.FIND_WORD_LOCATION.value: "TransitionPath",
        }
        
        self.qa_index_mapping={
            QuestionType.CELL_LETTER.value: 0,
            QuestionType.LETTER_COUNT.value: 1,
            QuestionType.WORD_DIRECTION.value: 2,
            QuestionType.FIND_WORD_LOCATION.value: 3,
        }
                
            
        
    def _get_plot_level(self, grid_size: int) -> str:
        """Determine plot level based on grid size"""
        if grid_size <= 5:
            return "Easy"
        elif grid_size <= 7:
            return "Medium"
        else:
            return "Hard"
            
    def _get_qa_level(self, question_type: str) -> str:
        """Get question difficulty level based on question type"""
        return self.qa_level_mapping.get(question_type, "Medium")
        
    def generate_dataset(self, num_problems: int) -> List[Dict]:
        dataset = []
        
        for i in range(num_problems):
            # Generate random grid size between 5 and 8
            grid_size = random.randint(5, 8)
            grid = WordSearchGrid(grid_size)
            
            # Generate unique IDs
            problem_id = f"word-mcq-{i+1:05d}"
            plot_id = f"word-plot-{i+1:05d}"
            
            # Generate question (randomly choose question type)
            question_func = random.choice([
                self.question_generator.generate_cell_letter_question,
                self.question_generator.generate_letter_count_question,
                self.question_generator.generate_word_direction_question,
                self.question_generator.generate_find_word_location_question
            ])
            qa_data = question_func(grid)
            
            # Generate image and state files
            image_path = os.path.join(self.image_dir, f"{problem_id}.png")
            state_path = os.path.join(self.state_dir, f"{problem_id}.json")
            
            self.image_generator.create_grid_image(grid, image_path)
            
            # Save state
            state_data = {
                "grid": grid.grid,
                "size": grid.size,
                "question_type": qa_data["qa_type"]
            }
            with open(state_path, "w") as f:
                json.dump(state_data, f)
            
            # Get plot and qa levels
            plot_level = self._get_plot_level(grid_size)
            qa_level = self._get_qa_level(qa_data["qa_type"])
            
            # Create dataset entry
            entry = {
                "data_id": problem_id,
                "qa_type": self.qa_type_mapping[qa_data["qa_type"]],
                'question_id': self.qa_index_mapping[qa_data["qa_type"]],
                'question_description': qa_data["qa_type"],
                "image": f"images/{problem_id}.png",
                "state": f"states/{problem_id}.json",
                "plot_id": plot_id,
                "plot_level": plot_level,  # Based on grid size
                "qa_level": qa_level,      # Based on question type
                "question": qa_data["question"],
                "answer": qa_data["answer"],
                "analysis": qa_data["analysis"],
                "options": qa_data["options"]
            }
            
            dataset.append(entry)
        
        # Save complete dataset
        with open(os.path.join(self.output_dir, "data.json"), "w") as f:
            json.dump(dataset, f, indent=2)
        
        return dataset

# Usage example
if __name__ == "__main__":
    generator = WordSearchGenerator(output_dir="word_search_dataset")
    dataset = generator.generate_dataset(num_problems=5000)
    print(f"Generated {len(dataset)} problems")
