import random
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from copy import deepcopy

class Board:
    def __init__(self, grid, head_x, head_y, current_state, num_states, rules):
        self.grid = grid
        self.head_x = head_x
        self.head_y = head_y
        self.current_state = current_state
        self.num_states = num_states
        self.rules = rules
        self.directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Directions: 0=up, 1=right, 2=down, 3=left
        self.state_brackets = ['()', '[]', '{}', '<>']
        # Define easy-to-differentiate colors
        self.colors = ['red', 'green', 'blue', 'magenta', 'cyan', 'yellow', 'orange', 'purple']
        self.questionTypes=['position', 'head_state','symbol_at_position','first_state_entry']
        self.questionTypesMapping={
            'position': 'State Prediction',
            'head_state': 'State Prediction',
            'symbol_at_position': 'State Prediction',
            'first_state_entry': 'State Prediction'
        }
        self.qaLevelMapping={'position':'Medium','head_state':'Medium','symbol_at_position':'Medium','first_state_entry':'Medium'} # core parts are the same (executing the machine) so have the same level

    def saveState(self) -> Dict:
        """Save the current state of the board."""
        return {
            'grid': self.grid.copy(),
            'head_x': self.head_x,
            'head_y': self.head_y,
            'current_state': self.current_state
        }

    def loadState(self, state: Dict):
        """Load a saved state of the board."""
        self.grid = state['grid']
        self.head_x = state['head_x']
        self.head_y = state['head_y']
        self.current_state = state['current_state']

    def step(self):
        """Perform one step of the Turing machine."""
        current_symbol = self.grid[self.head_y, self.head_x]
        rule_key = (self.current_state, current_symbol)
        
        # Apply rule
        new_symbol, direction, new_state = self.rules[rule_key]
        self.grid[self.head_y, self.head_x] = new_symbol
        self.current_state = new_state
        
        # Move head
        dx, dy = self.directions[direction]
        self.head_x = self.head_x + dx
        self.head_y = self.head_y + dy
        
        if self.head_x < 0 or self.head_y < 0 or self.head_y >= self.grid.shape[0] or self.head_x >= self.grid.shape[1]:
            raise IndexError("Out of bound")

    def simulate_steps(self, num_steps: int) -> List[Tuple[int, int, int, int]]:
        """Simulate multiple steps and return list of (x, y, symbol, state) tuples."""
        positions = [(self.head_x, self.head_y, 
                     self.grid[self.head_y, self.head_x], 
                     self.current_state)]
        for _ in range(num_steps):
            self.step()
            positions.append((self.head_x, self.head_y, 
                             self.grid[self.head_y, self.head_x], 
                             self.current_state))
        return positions

    def __str__(self):
        """Return the board status as a string."""
        board_str = "Current Board State:\n"
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                if x == self.head_x and y == self.head_y:
                    left, right = self.state_brackets[self.current_state]
                    board_str += f"{left}{self.grid[y, x]}{right} "
                else:
                    board_str += f"{self.grid[y, x]} "
            board_str += "\n"
        board_str += f"Current State: {self.current_state}, Head Position: ({self.head_y}, {self.head_x})\n"
        return board_str
    
    def fullDescriptionDict(self) -> dict:
        """Return full information of rules, current head status and grid information as dict (for json.dump)"""
        # Extract rules in the desired format
        rules_list = []
        for (state, symbol), (new_symbol, direction, new_state) in self.rules.items():
            rule_dict = {
                "state": state,
                "symbol": symbol,
                "new_state": new_state,
                "new_symbol": new_symbol,
                "direction": direction
            }
            rules_list.append(rule_dict)
        
        # Extract head information
        head_info = {
            "x": self.head_x,
            "y": self.head_y,
            "state": self.current_state
        }
        
        # Extract grid information
        grid_info = self.grid.tolist()
        
        # Construct the final dictionary
        full_description = {
            "rules": rules_list,
            "head": head_info,
            "grid": grid_info
        }
        
        return full_description
    
    def descriptionStr(self) -> str:
        """Return detailed description of rules and current head status (but without grid information cuz it's in the image)."""
        left, right = self.state_brackets[self.current_state]
        description = ""
        description += "Rules:\n"
        for (state, symbol), (new_symbol, direction, new_state) in self.rules.items():
            dir_symbols = ['up','right','down','left']
            description += (f"State {state}, Symbol {symbol} -> Write {new_symbol}, Move {dir_symbols[direction]}, "
                        f"New State {new_state}\n")
        
        # Add color information for symbols
        description += "\nColor Legend for Symbols:\n"
        for i, color in enumerate(self.colors[:self.grid.max() + 1]):
            description += f"Symbol {i}: Color = {color}\n"
            
        description += "\nBracket Legend for States:\n"
        for i, color in enumerate(self.state_brackets[:self.num_states + 1]):
            description += f"State {i}: Bracket = {color[0]} {color[1]}\n"
        description += (f"Current head position is ({self.head_y}, {self.head_x}) "
                    f"with State {self.current_state} on Symbol {self.grid[self.head_y, self.head_x]} that is {left}{self.grid[self.head_y, self.head_x]}{right}.\n"
                    )
        return description

    def SaveBoard(self, path: str):
        """Generate a picture of the board and save it to the given path."""
        fig, ax = plt.subplots()
        
        # Assign colors for each state
        color_map = [self.colors[i % len(self.colors)] for i in range(self.grid.max() + 1)]
        
        # Display the grid with the assigned colors
        color_grid = np.empty(self.grid.shape, dtype=object)
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                color_grid[y, x] = color_map[self.grid[y, x]]
        
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                ax.add_patch(plt.Rectangle((x, y), 1, 1, color=color_grid[y, x]))
        
        # Mark the head position
        ax.scatter(self.head_x + 0.5, self.head_y + 0.5, color='black', s=200, edgecolors='white', label='Head')
        
        # Set limits, labels, and move legend outside of the grid
        ax.set_xlim(0, self.grid.shape[1])
        ax.set_ylim(0, self.grid.shape[0])
        num_rows, num_cols = self.grid.shape
        ax.set_xticks([x + 0.5 for x in range(num_cols)])
        ax.set_yticks([y + 0.5 for y in range(num_rows)])
        ax.set_xticklabels(range(self.grid.shape[1]))
        ax.set_yticklabels(range(self.grid.shape[0]))
        ax.xaxis.tick_top()  # Move x-axis ticks to the top
        ax.set_aspect('equal')
        ax.set_title(f"Turing Machine Board (Head State: {self.current_state})")
        ax.legend(loc='upper center', bbox_to_anchor=(1.15, 1))
        plt.gca().invert_yaxis()  # Flip the y-axis
        plt.savefig(path)
        plt.close()

    def GenerateStepQA(self, steps: int, optionNumber: int, questionType: str = '') -> Tuple[str, str, str, List[str], int]:
        """Generate multiple types of questions about the board's state after a given number of steps."""
        question_type = questionType or random.choice(self.questionTypes)
        
        if question_type == 'position':
            return self._generate_position_question(steps, optionNumber)
        elif question_type == 'head_state':
            return self._generate_head_state_and_symbol_question(steps, optionNumber)
        elif question_type == 'symbol_at_position':
            return self._generate_symbol_at_position_question(steps, optionNumber)
        elif question_type == 'first_state_entry':
            return self._generate_first_state_entry_question(steps, optionNumber)

    def _generate_position_question(self, steps: int, optionNumber: int) -> Tuple[str, str, str, List[str], int]:
        """Generate a multiple choice question about future head position and its answer."""
        if optionNumber > self.grid.shape[0] * self.grid.shape[1]:
            raise ValueError("Option number exceeds possible unique positions on the board.")

        left, right = self.state_brackets[self.current_state]
        question = self.descriptionStr() + '\n'
        question += (f"Question: where will the head be after {steps} steps?\n")
        
        # Save current state
        saved_state = self.saveState()
        
        # Simulate steps
        positions = self.simulate_steps(steps)
        
        # Restore original state
        self.loadState(saved_state)
        
        # Correct answer
        final_position = (positions[-1][1], positions[-1][0])
        answer = "Detailed step-by-step analysis:\n\n"
        original_grid = saved_state['grid']
        
        for i, (x, y, symbol, state) in enumerate(positions[:-1]):
            rule_key = (state, symbol)
            new_symbol, direction, new_state = self.rules[rule_key]
            dir_symbols = ['up','right','down','left']
            next_x = x + self.directions[direction][0]
            next_y = y + self.directions[direction][1]
            left, right = self.state_brackets[state]
            
            answer += f"Step {i+1}:\n"
            answer += f"- **Position:** ({y}, {x})\n"
            answer += f"- **State:** {state}\n"
            
            
            # Symbol analysis
            if i == 0:
                color = self.colors[symbol]
                answer += f"- **Symbol:** Directly from image, it's {color} which means symbol {symbol}\n"
            else:
                while i>0:
                    i-=1
                    prev_pos = positions[i]
                    if (x, y) == (prev_pos[0], prev_pos[1]):
                        answer += f"- **Symbol:** According to step {i+1}, it has been changed to symbol {symbol}\n"
                        break
                else:
                    color = self.colors[symbol]
                    answer += f"- **Symbol:** Directly from image, it's {color} which means symbol {symbol}\n"
            
            answer += f"- **State and Symbol**: {left}{symbol}{right}\n"
            answer += f"- **Action:** Write {new_symbol}, Move {dir_symbols[direction]}, New State {new_state}\n"
            answer += f"- **Symbol Written on ({y}, {x}):** {new_symbol}\n"
            answer += f"- **New Position:** ({next_y}, {next_x})\n"
            answer += f"- **New State:** {new_state}\n"
            

        final_pos = positions[-1]
        answer += f"Therefore, the final position after {steps} steps will be ({final_pos[1]}, {final_pos[0]}).\n"
        
        # Generate multiple choice options
        options = [final_position]
        while len(options) < optionNumber:
            random_pos = (random.randint(0, self.grid.shape[0] - 1), random.randint(0, self.grid.shape[1] - 1))
            if random_pos not in options:
                options.append(random_pos)
        random.shuffle(options)
        correct_choice = options.index(final_position) + 1
        
        answer += (f"The answer is option {correct_choice}.")
        
        # Format options for question
        options_str = "\n".join([f"{i + 1}: ({opt[0]}, {opt[1]})" for i, opt in enumerate(options)])
        question += f"Options:\n{options_str}\n"
        
        board_status = str(self)
        
        return question, answer, board_status, options, correct_choice

    def _generate_head_state_and_symbol_question(self, steps: int, optionNumber: int) -> Tuple[str, str, str, List[int], int]:
        """Generate a multiple choice question about the head state and symbol under it after a given number of steps."""
        maximum=(self.grid.max() + 1)*self.num_states
        if optionNumber > maximum:
            print(f"Option number ({optionNumber}) exceeds possible unique head states ({maximum}).")
            optionNumber=maximum

        question = self.descriptionStr() + '\n'
        question += (f"Question: what will be the head state and symbol under it after {steps} steps?\n")
        
        # Save current state
        saved_state = self.saveState()
        
        # Simulate steps
        positions = self.simulate_steps(steps)
        
        # Restore original state
        self.loadState(saved_state)
        
        # Correct answer
        final_state = positions[-1][3]
        final_symbol = positions[-1][2]
        answer = "Detailed step-by-step analysis:\n\n"
        original_grid = saved_state['grid']
        
        for i, (x, y, symbol, state) in enumerate(positions):
            rule_key = (state, symbol)
            new_symbol, direction, new_state = self.rules[rule_key]
            dir_symbols = ['up','right','down','left']
            next_x = x + self.directions[direction][0]
            next_y = y + self.directions[direction][1]
            left, right = self.state_brackets[state]
            
            answer += f"Step {i+1}:\n" if i<len(positions)-1 else f"Final:\n"
            answer += f"- **Position:** ({y}, {x})\n"
            answer += f"- **State:** {state}\n"
            
            
            iref=i
            # Symbol analysis
            if i == 0:
                color = self.colors[symbol]
                answer += f"- **Symbol:** Directly from image, it's {color} which means symbol {symbol}\n"
            else:
                while i>0:
                    i-=1
                    prev_pos = positions[i]
                    if (x, y) == (prev_pos[0], prev_pos[1]):
                        answer += f"- **Symbol:** According to step {i+1}, it has been changed to symbol {symbol}\n"
                        break
                else:
                    color = self.colors[symbol]
                    answer += f"- **Symbol:** Directly from image, it's {color} which means symbol {symbol}\n"
            
            answer += f"- **State and Symbol**: {left}{symbol}{right}\n"
            if iref==len(positions)-1:
                break
            
            answer += f"- **Action:** Write {new_symbol}, Move {dir_symbols[direction]}, New State {new_state}\n"
            answer += f"- **Symbol Written on ({y}, {x}):** {new_symbol}\n"
            answer += f"- **New Position:** ({next_y}, {next_x})\n"
            answer += f"- **New State:** {new_state}\n"
            
        left, right = self.state_brackets[final_state]
        answer += f"After {steps} steps, the head state and symbol under it will be {left}{final_symbol}{right}.\n"
        
        # Generate multiple choice options
        options = [f'{left}{final_symbol}{right}']
        correct=options[0]
        while len(options) < optionNumber:
            random_state = random.randint(0, self.num_states - 1)
            left, right = self.state_brackets[random_state]
            random_symbol = random.randint(0, self.grid.max())
            random_str = f'{left}{random_symbol}{right}'
            if random_str not in options:
                options.append(random_str)
        random.shuffle(options)
        correct_choice = options.index(correct) + 1
        
        answer += (f"The answer is option {correct_choice}.")
        
        # Format options for question
        options_str = "\n".join([f"{i + 1}: {opt}" for i, opt in enumerate(options)])# State And Symbol 
        question += f"Options:\n{options_str}\n"
        
        board_status = str(self)
        
        return question, answer, board_status, options, correct_choice

    def _generate_symbol_at_position_question(self, steps: int, optionNumber: int) -> Tuple[str, str, str, List[str], int]:
        """Generate a multiple choice question about the symbol changes at a specific position over steps."""
        # Save current state
        saved_state = self.saveState()
        
        # Simulate steps
        positions = self.simulate_steps(steps)
        
        # Find a position that has been modified
        modified_positions = [(x, y) for (x, y, symbol, state) in positions if (x, y) != (self.head_x, self.head_y)]
        if not modified_positions:
            raise ValueError("No modified positions found.")
        chosen_position = random.choice(modified_positions)
        
        # Track symbol changes for the chosen position
        symbol_changes = []
        init_symbol = saved_state['grid'][chosen_position[1],chosen_position[0]]
        
        for i, (x, y, symbol, state) in enumerate(positions):
            if (x, y) == chosen_position:
                
                rule_key = (state, symbol)
                
                # Apply rule
                new_symbol, direction, new_state = self.rules[rule_key]
                symbol_changes.append((i, new_symbol))
        
        # Restore original state
        self.loadState(saved_state)
        
        # Generate question
        question = self.descriptionStr() + '\n'
        question += (f"Question: how does the symbol at position ({chosen_position[1]}, {chosen_position[0]}) change after {steps} steps? Writing the same symbol needs to be tracked.\n")
        
        # Correct answer
        answer = "Detailed step-by-step analysis:\n\n"
        original_grid = saved_state['grid']
        
        for i, (x, y, symbol, state) in enumerate(positions[:-1]):
            rule_key = (state, symbol)
            new_symbol, direction, new_state = self.rules[rule_key]
            dir_symbols = ['up','right','down','left']
            next_x = x + self.directions[direction][0]
            next_y = y + self.directions[direction][1]
            left, right = self.state_brackets[state]
            
            answer += f"Step {i+1}:\n"
            answer += f"- **Position:** ({y}, {x})\n"
            answer += f"- **State:** {state}\n"
            
            
            # Symbol analysis
            if i == 0:
                color = self.colors[symbol]
                answer += f"- **Symbol:** Directly from image, it's {color} which means symbol {symbol}\n"
            else:
                while i>0:
                    i-=1
                    prev_pos = positions[i]
                    if (x, y) == (prev_pos[0], prev_pos[1]):
                        answer += f"- **Symbol:** According to step {i+1}, it has been changed to symbol {symbol}\n"
                        break
                else:
                    color = self.colors[symbol]
                    answer += f"- **Symbol:** Directly from image, it's {color} which means symbol {symbol}\n"
            
            answer += f"- **State and Symbol**: {left}{symbol}{right}\n"
            answer += f"- **Action:** Write {new_symbol}, Move {dir_symbols[direction]}, New State {new_state}\n"
            answer += f"- **Symbol Written on ({y}, {x}):** {new_symbol}\n"
            answer += f"- **New Position:** ({next_y}, {next_x})\n"
            answer += f"- **New State:** {new_state}\n"
            

        
        # Create symbol change trajectory
        trajectory_str = f"{init_symbol}"
        for step, symbol in symbol_changes:
            trajectory_str += f"->{symbol}(at step {step+1})"
        
        answer += f"The symbol trajectory at position ({chosen_position[1]}, {chosen_position[0]}) is: {trajectory_str}\n"
        
        # Generate multiple choice options
        options = [trajectory_str]
        
        # Try to generate unique random trajectories
        max_attempts = 50  # Prevent infinite loop
        attempts = 0
        while len(options) < optionNumber and attempts < max_attempts:
            # Generate a random trajectory
            rand_changes = random.randint(1, steps//2+1)
            random_trajectory = f"{init_symbol}"
            random_steps=random.sample(list(range(1,steps)),rand_changes)
            random_steps.sort()
            for j in range(rand_changes):
                random_symbol = random.randint(0, self.grid.max())
                random_trajectory += f"->{random_symbol}(at step {random_steps[j]})"
            
            if random_trajectory not in options:
                options.append(random_trajectory)
            
            attempts += 1
        
        random.shuffle(options)
        correct_choice = options.index(trajectory_str) + 1
        
        answer += (f"The answer is option {correct_choice}.")
        
        # Format options for question
        options_str = "\n".join([f"{i + 1}: {opt}" for i, opt in enumerate(options)])
        question += f"Options:\n{options_str}\n"
        
        board_status = str(self)
        
        return question, answer, board_status, options, correct_choice

    def _generate_first_state_entry_question(self, max_steps: int, optionNumber: int) -> Tuple[str, str, str, List[int], int]:
        """Generate a multiple choice question about when the head first enters a specific state."""

        # Save current state
        saved_state = self.saveState()
        
        # Simulate steps to track state changes
        state_entry_times = {}
        positions = [(self.head_x, self.head_y, 
                      self.grid[self.head_y, self.head_x], 
                      self.current_state)]
        
        # Track first entry to each state
        for step in range(1, max_steps + 1):
            self.step()
            positions.append((self.head_x, self.head_y, 
                              self.grid[self.head_y, self.head_x], 
                              self.current_state))
            
            # Record first entry to state if not already recorded
            if self.current_state not in state_entry_times:
                state_entry_times[self.current_state] = step
        
        # Restore original state
        self.loadState(saved_state)
        
        
        # Choose a state to ask about (preferably one not the initial state)
        possible_states = list(state_entry_times.keys())
        possible_states.remove(self.current_state) if self.current_state in possible_states else None
        
        # If no other states found, fallback to the first state
        if not possible_states:
            possible_states = list(state_entry_times.keys())
        
        target_state = random.choice(possible_states)
        first_entry_step = state_entry_times[target_state]
        
        
        # Prepare the question
        question = self.descriptionStr() + '\n'
        question += (f"Question: after how many steps will the head first enter state {target_state}?\n")
        
        
        # Full answer with state transition details
        answer = "Detailed step-by-step analysis:\n\n"
        original_grid = saved_state['grid']
        
        for i, (x, y, symbol, state) in enumerate(positions[:first_entry_step]):
            rule_key = (state, symbol)
            new_symbol, direction, new_state = self.rules[rule_key]
            dir_symbols = ['up','right','down','left']
            next_x = x + self.directions[direction][0]
            next_y = y + self.directions[direction][1]
            left, right = self.state_brackets[state]
            
            answer += f"Step {i+1}:\n"
            answer += f"- **Position:** ({y}, {x})\n"
            answer += f"- **State:** {state}\n"
            
            # Symbol analysis
            if i == 0:
                color = self.colors[symbol]
                answer += f"- **Symbol:** Directly from image, it's {color} which means symbol {symbol}\n"
            else:
                while i>0:
                    i-=1
                    prev_pos = positions[i]
                    if (x, y) == (prev_pos[0], prev_pos[1]):
                        answer += f"- **Symbol:** According to step {i+1}, it has been changed to symbol {symbol}\n"
                        break
                else:
                    color = self.colors[symbol]
                    answer += f"- **Symbol:** Directly from image, it's {color} which means symbol {symbol}\n"
            
            answer += f"- **State and Symbol**: {left}{symbol}{right}\n"
            answer += f"- **Action:** Write {new_symbol}, Move {dir_symbols[direction]}, New State {new_state}\n"
            answer += f"- **Symbol Written on ({y}, {x}):** {new_symbol}\n"
            answer += f"- **New Position:** ({next_y}, {next_x})\n"
            answer += f"- **New State:** {new_state}\n"
            

        
        # Add specific state entry information
        answer += (f"\nThe head first enters state {target_state} "
                   f"that is brackets {self.state_brackets[target_state]} after step {first_entry_step}.\n")
        
        # Generate multiple choice options
        options = [first_entry_step]
        while len(options) < optionNumber:
            # Generate alternative steps
            alt_step = random.randint(1, max(max_steps,8))
            if alt_step not in options:
                options.append(alt_step)
        
        # Shuffle and find correct choice
        random.shuffle(options)
        correct_choice = options.index(first_entry_step) + 1
        
        answer += f"The answer is option {correct_choice}."
        
        # Format options for question
        options_str = "\n".join([f"{i + 1}: {opt}" for i, opt in enumerate(options)])
        question += f"Options:\n{options_str}\n"
        
        board_status = str(self)
        
        return question, answer, board_status, options, correct_choice
    
def GenerateBoard(xSize: int, ySize: int, cellStateNum: int, headStateNum: int) -> Board:
    """Generate a board with random states for each cell and a head at a random position."""
    grid = np.random.randint(0, cellStateNum, (ySize, xSize), dtype=int)
    head_x = random.randint(0, xSize - 1)
    head_y = random.randint(0, ySize - 1)
    current_state = random.randint(0, headStateNum - 1)
    
    # Generate random rules
    rules = {}
    for state in range(headStateNum):
        for symbol in range(cellStateNum):
            new_symbol = random.randint(0, cellStateNum - 1)
            direction = random.randint(0, 3)  # Random direction
            new_state = random.randint(0, headStateNum - 1)
            rules[(state, symbol)] = (new_symbol, direction, new_state)
    
    board = Board(grid, head_x, head_y, current_state, headStateNum, rules)
    boardRef = deepcopy(board)
    
    try:
        board.simulate_steps(10)
    except IndexError:
        return GenerateBoard(xSize, ySize, cellStateNum, headStateNum)
    return boardRef


import os
import json

def GenerateDataset(num_boards: int, output_dir: str = "2d_turing_machine_dataset"):
    """Generate a dataset with N boards, questions, and answers."""
    images_dir = os.path.join(output_dir, "images")
    states_dir = os.path.join(output_dir, "states")
    qa_json_path = os.path.join(output_dir, "data.json")

    # Create directories if they don't exist
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(states_dir, exist_ok=True)

    qa_list = []

    for i in range(1, num_boards + 1):
        # Generate the board
        xSize=random.randint(3,5)
        ySize=random.randint(3,5)
        if xSize>ySize:
            xSize,ySize=ySize,xSize
        board = GenerateBoard(xSize=xSize, ySize=ySize, cellStateNum=random.randint(3,5), headStateNum=random.randint(2,4))

        # Generate the board image and save it
        image_path = os.path.join(images_dir, f"{i:05}.png")
        board.SaveBoard(image_path)
        
        # Save the board state to a JSON file
        state_json_path = os.path.join(states_dir, f"{i:05}.json")
        with open(state_json_path, "w") as state_file:
            state_file.write(json.dumps(board.fullDescriptionDict(),indent=4,ensure_ascii=False))

        # Generate a question and answer for the board
        steps = random.randint(3, 8)
        question_type=board.questionTypes[int((i-1)/num_boards*len(board.questionTypes))]
        question, answer, board_status, options, correct = board.GenerateStepQA(steps,8,question_type)

        def getPlotLevel(board):
            num=board.grid.shape[0]*board.grid.shape[1]
            if num<=12:
                return "Easy"
            elif num<=16:
                return "Medium"
            else:
                return "Hard"

        # Append the QA info to the list
        qa_entry = {
            "data_id": f"turing-machine-train-{i:05}",
            "image": os.path.join("images", f"{i:05}.png"),
            "state": os.path.join("states", f"{i:05}.json"),
            "plot_level": getPlotLevel(board),
            "qa_type": board.questionTypesMapping[question_type],
            "qa_level": board.qaLevelMapping[question_type],
            "question_id":board.questionTypes.index(question_type),
            "question_description":question_type,
            "question": question,
            "answer": correct,
            "options": list(map(str,eval(str(options)))),
            "analysis": answer
        }
        qa_list.append(qa_entry)

    # Save the QA dataset to a JSON file
    with open(qa_json_path, "w") as qa_file:
        json.dump(qa_list, qa_file, indent=4,ensure_ascii=False)


def main():
    # Number of boards to generate
    num_boards = 500  # Example: You can modify this to generate more boards

    # Generate the dataset and save to the specified directory
    GenerateDataset(num_boards, output_dir="2d_turing_machine_dataset")


if __name__ == "__main__":
    main()


