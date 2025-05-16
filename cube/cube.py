import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Set
from copy import deepcopy
import random
from collections import defaultdict, deque
import os
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib
matplotlib.use('Agg')

class RubiksCube:
    def __init__(self):
        # Initialize faces: U(up), D(down), L(left), R(right), F(front), B(back)
        self.faces = {
            'U': np.zeros((3, 3), dtype=int),   # Yellow - 0
            'D': np.ones((3, 3), dtype=int),    # White - 1
            'L': np.full((3, 3), 2),           # Orange - 2
            'R': np.full((3, 3), 3),           # Red - 3
            'F': np.full((3, 3), 4),           # Blue - 4
            'B': np.full((3, 3), 5)            # Green - 5
        }
        self.colors = ['yellow', 'white', 'orange', 'red', 'blue', 'green']
        self.move_history = []

    def _generate_color_count(self) -> Tuple[str, str, List[str], int,str]:
        """Generate a question about counting colors on a specific face."""
        face = random.choice(list(self.faces.keys()))
        # 先统计每个颜色的实际数量
        color_counts = defaultdict(int)
        for i in range(3):
            for j in range(3):
                color_idx = self.faces[face][i, j]
                color_counts[self.colors[color_idx]] += 1
        
        # 从存在的颜色中选择一个
        color = random.choice([c for c in color_counts.keys()])
        count = color_counts[color]
        
        FACES = {
            'F': 'Front face',
            'B': 'Back face',
            'L': 'Left face',
            'R': 'Right face',
            'U': 'Upper face',
            'D': 'Down face'
        }
        face1 = FACES[face]
        
        
        analysis = f"Initial state analysis of {face1}:\n"
        for i in range(3):
            for j in range(3):
                curr_color = self.colors[self.faces[face][i, j]]
                if curr_color == color:
                    analysis += f"- Position ({i},{j}) is {color}\n"
                    
        
        
        # Generate reasonable options around the actual count
        possible_counts = list(range(max(0, count-4), min(9, count+5)))
        if count in possible_counts:
            possible_counts.remove(count)
        
        # Ensure we have exactly 3 wrong options
        while len(possible_counts) > 7:
            possible_counts.pop()
            
        while len(possible_counts) < 7:
            new_count = random.randint(0, 9)
            if new_count != count and new_count not in possible_counts:
                possible_counts.append(new_count)
                
        options = [str(count)] + [str(c) for c in possible_counts]
        random.shuffle(options)
        correct_idx = options.index(str(count))
        options_display = ", ".join(f"[{i+1}] {opt}" for i, opt in enumerate(options))
        question = (f"Rules: As shown in the figure, the Rubik's cube consists of both 3D views and an unfolded view. The 3D views show the cube from two angles: left-tilted 30 degrees looking down, and right-tilted ,30 degrees looking up. The cube has six faces: Upper (U), Down (D), Left (L), Right (R), Front (F), and Back (B). Each face can be rotated clockwise or counterclockwise.And for each face, the coordinates are determined based on the unfolded view: column number increases from left to right (0,1,2) and row number increases from bottom to top (0,1,2). Legend shown in the bottom left corner.Handedness issues in the 3D views can be ignored.An uppercase letter indicates which face to rotate ('F' for Front, 'B' for Back, 'L' for Left, 'R' for Right, 'U' for Upper, 'D' for Down), with a prime symbol (') denoting counterclockwise rotation and no prime symbol denoting clockwise rotation. "
                   f"How many {color} squares are there on the {face1}?\n"
                   f"Options: {options_display}")
        analysis += f"\nTotal count: {count} {color} squares on the {face1},So the answer is {options[correct_idx]}. The option number is {correct_idx+1}."
        return question, analysis, options, correct_idx,face

    def _solve_single_face(self, face: str, max_depth: int = 12) -> Tuple[List[str], List[Dict]]:
        """Find optimal sequence of moves to solve a single face."""
        if self._is_face_solved(face):
            return [], []

        original_state = deepcopy(self.faces)
        seen_states = set()
        queue = deque([([], self.faces, [])])  # [moves, state, search_states]
        min_solution = None
        min_search_process = None
        
        def get_state_hash(faces):
            return str(faces[face].tobytes())
            
        def try_move(move_sequence, current_faces, search_process):
            self.faces = deepcopy(current_faces)
            self.make_move(move)
            new_state = deepcopy(self.faces)
            state_hash = get_state_hash(new_state)
            
            if state_hash not in seen_states:
                seen_states.add(state_hash)
                current_search_state = {
                    'moves': move_sequence + [move],
                    'face_state': str(new_state[face])
                }
                queue.append((
                    move_sequence + [move], 
                    new_state,
                    search_process + [current_search_state]
                ))
        
        while queue:
            move_sequence, current_state, search_process = queue.popleft()
            
            if len(move_sequence) >= max_depth:
                continue
                
            self.faces = deepcopy(current_state)
            if self._is_face_solved(face):
                if min_solution is None or len(move_sequence) < len(min_solution):
                    min_solution = move_sequence
                    min_search_process = search_process
                    continue
                
            for move in ['F', 'B', 'L', 'R', 'U', 'D', 
                        "F'", "B'", "L'", "R'", "U'", "D'"]:
                try_move(move_sequence, current_state, search_process)
        
        self.faces = original_state
        return min_solution or [], min_search_process or []

    def _solve_cube(self, max_depth: int = 20) -> Tuple[List[str], List[Dict]]:
        """Find optimal sequence of moves to solve the entire cube."""
        if self._is_solved():
            return [], []

        original_state = deepcopy(self.faces)
        seen_states = set()
        queue = deque([([], self.faces, [])])  # [moves, state, search_states]
        min_solution = None
        min_search_process = None
        
        def get_state_hash(faces):
            return str({face: faces[face].tobytes() for face in faces})
            
        def try_move(move_sequence, current_faces, search_process):
            self.faces = deepcopy(current_faces)
            self.make_move(move)
            new_state = deepcopy(self.faces)
            state_hash = get_state_hash(new_state)
            
            if state_hash not in seen_states:
                seen_states.add(state_hash)
                current_search_state = {
                    'moves': move_sequence + [move],
                    'cube_state': {f: str(new_state[f]) for f in new_state}
                }
                queue.append((
                    move_sequence + [move], 
                    new_state,
                    search_process + [current_search_state]
                ))
        
        while queue:
            move_sequence, current_state, search_process = queue.popleft()
            
            if len(move_sequence) >= max_depth:
                continue
                
            self.faces = deepcopy(current_state)
            if self._is_solved():
                if min_solution is None or len(move_sequence) < len(min_solution):
                    min_solution = move_sequence
                    min_search_process = search_process
                    continue
                
            for move in ['F', 'B', 'L', 'R', 'U', 'D',
                        "F'", "B'", "L'", "R'", "U'", "D'"]:
                try_move(move_sequence, current_state, search_process)
        
        self.faces = original_state
        return min_solution or [], min_search_process or []

    def _generate_single_face_solve(self) -> Tuple[str, str, List[str], int]:
        """Generate a question about solving a single face."""
        face = random.choice(list(self.faces.keys()))
        if self._is_face_solved(face):
            return self._generate_single_face_solve()
            
        solution, search_process = self._solve_single_face(face)
        if not solution:
            return self._generate_single_face_solve()
        
        actual_moves = len(solution)
        options = [actual_moves]

# 修改：扩大范围并生成8个选项
        lower_bound = max(1, actual_moves - 3)
        upper_bound = actual_moves + 4

        while len(options) < 8:
            num = random.randint(lower_bound, upper_bound)
            if num not in options:
                options.append(num)
                
        random.shuffle(options)
        correct_idx = options.index(len(solution))
        
        FACES = {
            'F': 'Front face',
            'B': 'Back face',
            'L': 'Left face',
            'R': 'Right face',
            'U': 'Upper face',
            'D': 'Down face'
        }
        face1 = FACES[face]
        
        # 构建详细的分析过程
        analysis = f"Search process for solving {face1}:\n\n"
        analysis += "Initial state:\n"
        for i in range(3):
            for j in range(3):
                color = self.colors[self.faces[face][i, j]]
                analysis += f"Position ({i},{j}): {color}\n"
        
        # 添加搜索过程
        if search_process:
            analysis += "\nSearch steps:\n"
            for idx, state in enumerate(search_process, 1):
                analysis += f"\nStep {idx}:\n"
                analysis += f"Moves tried: {', '.join(state['moves'])}\n"
                analysis += f"Resulting face state: {state['face_state']}\n"
        
        analysis += f"\nFinal solution found: {', '.join(solution)}\n"
        analysis += f"Total moves needed: {len(solution)},So the answer is {options[correct_idx]}. The option number is {correct_idx+1}."
        options_display = ", ".join(f"[{i+1}] {opt}" for i, opt in enumerate(options))
        return (
            f"Rules: As shown in the figure, the Rubik's cube consists of both 3D views and an unfolded view. The 3D views show the cube from two angles: left-tilted 30 degrees looking down, and right-tilted ,30 degrees looking up. The cube has six faces: Upper (U), Down (D), Left (L), Right (R), Front (F), and Back (B). Each face can be rotated clockwise or counterclockwise.And for each face, the coordinates are determined based on the unfolded view: column number increases from left to right (0,1,2) and row number increases from bottom to top (0,1,2). Legend shown in the bottom left corner.Handedness issues in the 3D views can be ignored.An uppercase letter indicates which face to rotate ('F' for Front, 'B' for Back, 'L' for Left, 'R' for Right, 'U' for Upper, 'D' for Down), with a prime symbol (') denoting counterclockwise rotation and no prime symbol denoting clockwise rotation. "
            f"How many moves are needed to solve the {face1}?/n"
            f"Options: {options_display}",
            analysis,
            [str(opt) for opt in options],
            correct_idx
        )

    def _generate_full_solve(self) -> Tuple[str, str, List[str], int]:
        """Generate a question about solving the entire cube."""
        if self._is_solved():
            self.make_move("R")
            self.make_move("U")
            
        solution, search_process = self._solve_cube()
        if not solution:
            return ("Cannot be solved.", 
                   "This cube configuration cannot be solved.", 
                   ["Unsolvable"], 0)
                   
        actual_moves = len(solution)
        options = [actual_moves]

# 修改：扩大范围并生成8个选项
        lower_bound = max(1, actual_moves - 3)
        upper_bound = actual_moves + 4

        while len(options) < 8:
            num = random.randint(lower_bound, upper_bound)
            if num not in options:
                options.append(num)
                
        random.shuffle(options)
        correct_idx = options.index(len(solution))
        
        # 构建详细的分析过程
        analysis = "Initial cube state:\n"
        for face in self.faces:
            analysis += f"\n{face} face:\n"
            for i in range(3):
                for j in range(3):
                    color = self.colors[self.faces[face][i, j]]
                    analysis += f"Position ({i},{j}): {color}\n"
        
        # 添加搜索过程
        if search_process:
            analysis += "\nSearch steps:\n"
            for idx, state in enumerate(search_process, 1):
                analysis += f"\nStep {idx}:\n"
                analysis += f"Moves tried: {', '.join(state['moves'])}\n"
                analysis += "Resulting cube state:\n"
                for face, face_state in state['cube_state'].items():
                    analysis += f"{face} face: {face_state}\n"
        
        analysis += f"\nFinal solution found: {', '.join(solution)}\n"
        analysis += f"Total moves needed: {len(solution)},So the answer is {options[correct_idx]}. The option number is {correct_idx+1}."
        options_display = ", ".join(f"[{i+1}] {opt}" for i, opt in enumerate(options))
        return (
            "Rules: As shown in the figure, the Rubik's cube consists of both 3D views and an unfolded view. The 3D views show the cube from two angles: left-tilted 30 degrees looking down, and right-tilted ,30 degrees looking up. The cube has six faces: Upper (U), Down (D), Left (L), Right (R), Front (F), and Back (B). Each face can be rotated clockwise or counterclockwise.And for each face, the coordinates are determined based on the unfolded view: column number increases from left to right (0,1,2) and row number increases from bottom to top (0,1,2). Legend shown in the bottom left corner.Handedness issues in the 3D views can be ignored.An uppercase letter indicates which face to rotate ('F' for Front, 'B' for Back, 'L' for Left, 'R' for Right, 'U' for Upper, 'D' for Down), with a prime symbol (') denoting counterclockwise rotation and no prime symbol denoting clockwise rotation."
            "How many moves are needed to solve the entire cube?"
            f"Options: {options_display}",
            analysis,
            [str(opt) for opt in options],
            correct_idx
        )
    
    
   
    def make_move(self, move: str) -> None:
        """Execute a single move on the cube."""
        if not validate_move(move):
            raise ValueError(f"Invalid move: {move}")
        
        face = move[0]
        clockwise = len(move) == 1
    
    # Store original state of affected faces
        temp = deepcopy(self.faces)
    
    # Rotate face
        if clockwise:
            self.faces[face] = np.rot90(self.faces[face], k=-1)
        else:
            self.faces[face] = np.rot90(self.faces[face], k=1)
    
    # Define affected edges
        edges = {
        'F': {'up': ('U', (2, slice(None))), 'right': ('R', (slice(None), 0)), 
             'down': ('D', (0, slice(None))), 'left': ('L', (slice(None), 2))},
        'B': {'up': ('U', (0, slice(None))), 'left': ('L', (slice(None), 0)), 
             'down': ('D', (2, slice(None))), 'right': ('R', (slice(None), 2))},
        'R': {'up': ('U', (slice(None), 2)), 'back': ('B', (slice(None), 0)), 
             'down': ('D', (slice(None), 2)), 'front': ('F', (slice(None), 2))},
        'L': {'up': ('U', (slice(None), 0)), 'front': ('F', (slice(None), 0)), 
             'down': ('D', (slice(None), 0)), 'back': ('B', (slice(None), 2))},
        'U': {'front': ('F', (0, slice(None))), 'right': ('R', (0, slice(None))), 
             'back': ('B', (0, slice(None))), 'left': ('L', (0, slice(None)))},
        'D': {'front': ('F', (2, slice(None))), 'left': ('L', (2, slice(None))), 
             'back': ('B', (2, slice(None))), 'right': ('R', (2, slice(None)))}
    }
    
    # Get affected edges for this face
        edge_cycle = edges[face]
        cycle_orders= {
        'F': ['up', 'right', 'down', 'left'] if clockwise else ['up', 'left', 'down', 'right'],
        'B': ['up', 'left', 'down', 'right'] if clockwise else ['up', 'right', 'down', 'left'],
        'R': ['up', 'front', 'down', 'back'] if clockwise else ['up', 'back', 'down', 'front'],
        'L': ['up', 'back', 'down', 'front'] if clockwise else ['up', 'front', 'down', 'back'],
        'U': ['back', 'right', 'front', 'left'] if clockwise else ['back', 'left', 'front', 'right'],
        'D': ['front', 'right', 'back', 'left'] if clockwise else ['front', 'left', 'back', 'right']
    }
        cycle_order=cycle_orders[face]
    # Save first edge state
        first_pos = None
        first_data = None
        for pos in cycle_order:
            if pos in edge_cycle:
                curr_face, curr_idx = edge_cycle[pos]
                first_pos = (curr_face, curr_idx)
                first_data = temp[curr_face][curr_idx].copy()
                break
    
    # Rotate edges
        prev_data = first_data
        prev_pos = first_pos
    
        for i, pos in enumerate(cycle_order):
            if pos not in edge_cycle:
                continue
            
            curr_face, curr_idx = edge_cycle[pos]
        
            if i == 0:
                continue
            
        # Save current edge
            curr_data = temp[curr_face][curr_idx].copy()
        # Update current edge with previous data
            self.faces[curr_face][curr_idx] = prev_data
        # Save for next iteration
            prev_data = curr_data
            prev_pos = (curr_face, curr_idx)
    
    # Complete the cycle
        if first_pos:
            curr_face, curr_idx = first_pos
            self.faces[curr_face][curr_idx] = prev_data
    
        self.move_history.append(move)
    
    

    def _generate_face_recognition(self) -> Tuple[str, str, List[str], int,str]:
        """Generate a question about recognizing colors on a specific face."""
        face = random.choice(list(self.faces.keys()))
        pos_x = random.randint(0, 2)
        pos_y = random.randint(0, 2)
        
        color_idx = int(self.faces[face][pos_x, pos_y])
        correct_color = self.colors[color_idx]
        FACES = {
        'F': 'Front face',
        'B': 'Back face',
        'L': 'Left face',
        'R': 'Right face',
        'U': 'Upper face',
        'D': 'Down face'
         }
        face1=FACES[face]
        
        
        
        # Ensure we have valid options
        options = [correct_color]
        remaining_colors = self.colors.copy()
        remaining_colors.remove(correct_color)

# 新增：添加额外的颜色选项
        additional_colors = ['purple', 'pink', 'brown', 'gray', 'black', 'cyan', 'magenta']
        remaining_colors.extend(additional_colors)

# 选择7个错误选项
        wrong_options = random.sample(remaining_colors, 7)
        options.extend(wrong_options)
        # Guarantee we always have  8options
        while len(options) < 8:
            options.append(f"Option {len(options)}")
        
        random.shuffle(options)
        correct_idx = options.index(correct_color)
        options_display = ", ".join(f"[{i+1}] {opt}" for i, opt in enumerate(options))
        question = f"Rules: As shown in the figure, the Rubik's cube consists of both 3D views and an unfolded view. The 3D views show the cube from two angles: left-tilted 30 degrees looking down, and right-tilted ,30 degrees looking up. The cube has six faces: Upper (U), Down (D), Left (L), Right (R), Front (F), and Back (B). Each face can be rotated clockwise or counterclockwise.And for each face, the coordinates are determined based on the unfolded view: column number increases from left to right (0,1,2) and row number increases from bottom to top (0,1,2). Legend shown in the bottom left corner.Handedness issues in the 3D views can be ignored.An uppercase letter indicates which face to rotate ('F' for Front, 'B' for Back, 'L' for Left, 'R' for Right, 'U' for Upper, 'D' for Down), with a prime symbol (') denoting counterclockwise rotation and no prime symbol denoting clockwise rotation.What color is at position ({pos_x}, {pos_y}) on the {face1} face?Options: {options_display}"
        analysis = f" Based on the cube's state and the given coordinates ({pos_x}, {pos_y}) on the {face1} face, we can observe that this position contains {correct_color}. So the answer is {options[correct_idx]}. The option number is {correct_idx+1}."
        return question, analysis, options, correct_idx,face

    def _generate_move_prediction(self) -> Tuple[str, str, List[str], int]:
        """Generate a detailed question about cube state changes after a sequence of moves"""
    # Save initial state
        initial_state = deepcopy(self.faces)
    
    # Generate move sequence
        num_moves = random.randint(1, 5)
        moves = [random.choice(['F', 'B', 'L', 'R', 'U', 'D', "F'", "B'", "L'", "R'", "U'", "D'"]) 
            for _ in range(num_moves)]
    
    # Select position to track
        target_face = random.choice(list(self.faces.keys()))
        pos_x = random.randint(0, 2)
        pos_y = random.randint(0, 2)
        FACES = {
        'F': 'Front face',
        'B': 'Back face',
        'L': 'Left face',
        'R': 'Right face',
        'U': 'Upper face',
        'D': 'Down face'
         }
        face1=FACES[target_face]
    # Create detailed analysis
        initial_color = self.colors[self.faces[target_face][pos_x, pos_y]]
        analysis_steps = [
        f"Initial state: Position ({pos_x}, {pos_y}) on face {face1} is {initial_color},\n"
    ]
    
    # Execute moves and record changes
        for i, move in enumerate(moves, 1):
        # Save color at target position before move
            current_color = self.colors[self.faces[target_face][pos_x, pos_y]]
        
        # Execute move
            self.make_move(move)
        
        # Get new color after move
            new_color = self.colors[self.faces[target_face][pos_x, pos_y]]
        
        # Record detailed analysis if color changed
            if current_color != new_color:
                analysis_steps.append(
                f"Step {i}: After move {move}.\n"
                f"- This move {self._explain_move_effect(move,face1)},\n"
                f"- Changed color at position ({pos_x}, {pos_y}) from {current_color} to {new_color};\n"
            )
            else:
                analysis_steps.append(
                f"Step {i}: After move {move},\n"
                f"- This move did not affect the color at position ({pos_x}, {pos_y}), remaining {current_color};\n"
            )
    
    # Get final color
        final_color = self.colors[self.faces[target_face][pos_x, pos_y]]
        
    
    
    # Restore initial state
        self.faces = initial_state
    
    # Generate options
        options = [final_color]
        remaining_colors = [c for c in self.colors if c != final_color]
        additional_colors = ['purple', 'pink', 'brown', 'gray', 'black', 'cyan', 'magenta']
        remaining_colors.extend(additional_colors)
        options.extend(random.sample(remaining_colors, 7))
        random.shuffle(options)
        options_display = ", ".join(f"[{i+1}] {opt}" for i, opt in enumerate(options))
    # Generate question
        question = f"Rules: As shown in the figure, the Rubik's cube consists of both 3D views and an unfolded view. The 3D views show the cube from two angles: left-tilted 30 degrees looking down, and right-tilted ,30 degrees looking up. The cube has six faces: Upper (U), Down (D), Left (L), Right (R), Front (F), and Back (B). Each face can be rotated clockwise or counterclockwise.And for each face, the coordinates are determined based on the unfolded view: column number increases from left to right (0,1,2) and row number increases from bottom to top (0,1,2). Legend shown in the bottom left corner.Handedness issues in the 3D views can be ignored.An uppercase letter indicates which face to rotate ('F' for Front, 'B' for Back, 'L' for Left, 'R' for Right, 'U' for Upper, 'D' for Down), with a prime symbol (') denoting counterclockwise rotation and no prime symbol denoting clockwise rotation.After the sequence {' '.join(moves)}, what color will be at position ({pos_x}, {pos_y}) on the {face1} face?Options: {options_display}"
        # Generate complete analysis
        analysis = "Detailed Analysis:\n" + "\n".join(analysis_steps) + \
              f"\nFinal Result: After {len(moves)} moves, the final color at position ({pos_x}, {pos_y}) is {final_color},So the answer is {final_color}. The option number is {options.index(final_color)+1}."
        return question, analysis, options, options.index(final_color)

    def _explain_move_effect(self, move: str, target_face: str) -> str:
        """Explain the effect of a specific move on the target face"""
        face = move[0]
        is_clockwise = len(move) == 1
        direction = "clockwise" if is_clockwise else "counterclockwise"
    
        if face == target_face:
            return f"directly rotated the target face {direction}"
    
    # Define adjacent face relationships
        adjacent_faces = {
        'F': {'U': 'upper face', 'R': 'right face', 'D': 'bottom face', 'L': 'left face'},
        'B': {'U': 'upper face', 'L': 'left face', 'D': 'bottom face', 'R': 'right face'},
        'L': {'U': 'upper face', 'F': 'front face', 'D': 'bottom face', 'B': 'back face'},
        'R': {'U': 'upper face', 'B': 'back face', 'D': 'bottom face', 'F': 'front face'},
        'U': {'F': 'front face', 'R': 'right face', 'B': 'back face', 'L': 'left face'},
        'D': {'F': 'front face', 'L': 'left face', 'B': 'back face', 'R': 'right face'}
    }
    
        if target_face in adjacent_faces.get(face, {}):
            return f"rotated face {face} {direction}, affecting the edges of face {target_face}"
    
        return "did not directly affect the target position"
    


    def _is_face_solved(self, face: str) -> bool:
        """Check if a face is solved (all stickers same color)."""
        return np.all(self.faces[face] == self.faces[face][0, 0])

    def _is_solved(self) -> bool:
        """Check if the entire cube is solved."""
        return all(self._is_face_solved(face) for face in self.faces)

    def _evaluate_face(self, face: str) -> int:
        """Count number of correct stickers on a face."""
        target_color = self.faces[face][1, 1]  # Center color
        return np.sum(self.faces[face] == target_color)

    def _evaluate_cube(self) -> int:
        """Count total number of correctly colored stickers."""
        return sum(self._evaluate_face(face) for face in self.faces)


  

    def save_visualization(self, path: str, game_title: str = "cube") -> None:
        """Save improved visualization of the Rubik's cube with better layout and readability."""
        # Create figure with improved size ratio
        fig = plt.figure(figsize=(12, 9))
        
        # Create grid with better proportions - left side split into 70% top, 30% bottom
        grid = plt.GridSpec(10, 2, width_ratios=[2, 1], hspace=0.3, wspace=0.15)
        
        # Draw main unfolded cube (top left, larger size)
        ax_main = fig.add_subplot(grid[0:7, 0])  # Takes up first 7 units vertically
        self._draw_unfolded_cube_improved(ax_main)
        
        # Draw coordinate reference (bottom left)
        ax_coord = fig.add_subplot(grid[7:, 0])  # Takes up remaining 3 units vertically
        self._draw_coordinate_reference(ax_coord)
        
        # Draw 3D views (right column)
        ax_front = fig.add_subplot(grid[0:5, 1], projection='3d')
        self._draw_3d_cube_improved(ax_front, angle_front=30, angle_side=45)
        ax_front.set_title("Front view (F, R, U faces)", pad=8, fontsize=16)
        
        ax_back = fig.add_subplot(grid[5:, 1], projection='3d')
        self._draw_3d_cube_improved(ax_back, angle_front=-30, angle_side=225)
        ax_back.set_title("Back view (L, D, B faces)", pad=8, fontsize=16)
        
        # Save with higher resolution
        plt.savefig(path, bbox_inches='tight', dpi=65)
        plt.close()

    def _draw_unfolded_cube_improved(self, ax):
        """Draw improved unfolded cube layout with thicker borders but no coordinates."""
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Standard layout positions
        layouts = {
            'U': (0, 3),   # Upper face at top
            'L': (3, 0),   # Left face on left
            'F': (3, 3),   # Front face in center
            'R': (3, 6),   # Right face on right
            'B': (3, 9),   # Back face on far right
            'D': (6, 3)    # Down face at bottom
        }
        
        # Draw faces with thicker borders
        for face, (row_offset, col_offset) in layouts.items():
            # Draw face outline with thicker border
            rect = plt.Rectangle((col_offset, row_offset), 3, 3, 
                            fill=False, edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            
            # Draw individual cells
            for i in range(3):
                for j in range(3):
                    color = self.colors[self.faces[face][i, j]]
                    cell = plt.Rectangle((col_offset + j, row_offset + i), 1, 1,
                                    facecolor=color, edgecolor='black', linewidth=1)
                    ax.add_patch(cell)
            
            # Add face labels with better positioning
            label_offset = 1.0  # Reduced offset for more compact layout
            if face in ['U', 'D', 'L', 'B', 'R']:
                ax.annotate(f'{face}', 
                        xy=(col_offset + 1.5, row_offset + 1.5),
                        xytext=(col_offset + 1.5, row_offset + (-label_offset if face == 'U' else 4)),
                        ha='center', va='center', fontsize=20,
                        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
                        arrowprops=dict(arrowstyle='->', linewidth=1.5))
            else:
                ax.annotate(f'{face}',
                        xy=(col_offset + 1.5, row_offset + 1.5),
                        xytext=(col_offset + 4.5, row_offset - label_offset),
                        va='center', fontsize=20,
                        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
                        arrowprops=dict(arrowstyle='->', linewidth=1.5))
        
        ax.set_xlim(-1, 13)
        ax.set_ylim(-1, 10)

    def _draw_coordinate_reference(self, ax):
        """Draw a reference grid showing the coordinate system with pink background."""
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Draw title first
        ax.text(1.5, 3.2, 'Coordinate Reference',
                ha='center', va='bottom', fontsize=12,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
        
        # Draw 3x3 grid with coordinates
        coords = [(2,0), (2,1), (2,2),
                (1,0), (1,1), (1,2),
                (0,0), (0,1), (0,2)]
        
        for idx, (i, j) in enumerate(coords):
            row = idx // 3
            col = idx % 3
            # Draw cell with pink background
            rect = plt.Rectangle((col, 2-row), 1, 1, 
                            facecolor='pink', 
                            edgecolor='black',
                            linewidth=1.5)
            ax.add_patch(rect)
            
            # Add coordinates with larger font
            ax.text(col + 0.5, 2-row + 0.5, f'({i},{j})',
                ha='center', va='center', fontsize=12,
                weight='bold')
        
        ax.set_xlim(-0.2, 3.2)
        ax.set_ylim(-0.2, 3.5)

    def _draw_3d_cube_improved(self, ax, angle_front: int, angle_side: int):
        """Draw improved 3D view with better visibility."""
        scale = 3
        cell_size = scale / 3

        def draw_cell(vertices, color):
            """Draw a single colored cell with thicker edges"""
            x = [v[0] for v in vertices]
            y = [v[1] for v in vertices]
            z = [v[2] for v in vertices]
            verts = [list(zip(x, y, z))]
            poly = Poly3DCollection(verts)
            poly.set_color(color)
            poly.set_alpha(1.0)
            poly.set_edgecolor('black')
            poly.set_linewidth(1.5)
            ax.add_collection3d(poly)

        def is_face_visible(face: str, elev: float, azim: float) -> bool:
            """Determine if a face should be visible from the current viewing angle."""
            elev_rad = np.radians(elev)
            azim_rad = np.radians(azim)
            
            view_vector = np.array([
                np.cos(elev_rad) * np.sin(azim_rad),
                np.cos(elev_rad) * np.cos(azim_rad),
                np.sin(elev_rad)
            ])
            
            normals = {
                'F': np.array([0, 0, 1]),
                'B': np.array([0, 0, -1]),
                'R': np.array([1, 0, 0]),
                'L': np.array([-1, 0, 0]),
                'U': np.array([0, 1, 0]),
                'D': np.array([0, -1, 0])
            }
            
            normal = normals[face]
            visibility = np.dot(view_vector, normal)
            
            return visibility > -0.2

        def map_coordinates(face, i, j):
            """Map coordinates from 2D to 3D space."""
            if face == 'F':  # Front face
                return [
                    (j * cell_size, (2-i) * cell_size, scale),
                    ((j+1) * cell_size, (2-i) * cell_size, scale),
                    ((j+1) * cell_size, (3-i) * cell_size, scale),
                    (j * cell_size, (3-i) * cell_size, scale)
                ]
            elif face == 'B':  # Back face
                return [
                    ((2-j) * cell_size, (2-i) * cell_size, 0),
                    ((3-j) * cell_size, (2-i) * cell_size, 0),
                    ((3-j) * cell_size, (3-i) * cell_size, 0),
                    ((2-j) * cell_size, (3-i) * cell_size, 0)
                ]
            elif face == 'R':  # Right face
                return [
                    (scale, (2-i) * cell_size, scale - j * cell_size),
                    (scale, (2-i) * cell_size, scale - (j+1) * cell_size),
                    (scale, (3-i) * cell_size, scale - (j+1) * cell_size),
                    (scale, (3-i) * cell_size, scale - j * cell_size)
                ]
            elif face == 'L':  # Left face
                return [
                    (0, (2-i) * cell_size, j * cell_size),
                    (0, (2-i) * cell_size, (j+1) * cell_size),
                    (0, (3-i) * cell_size, (j+1) * cell_size),
                    (0, (3-i) * cell_size, j * cell_size)
                ]
            elif face == 'U':  # Upper face
                return [
                    (j * cell_size, scale, scale - (2-i) * cell_size),
                    ((j+1) * cell_size, scale, scale - (2-i) * cell_size),
                    ((j+1) * cell_size, scale, scale - (3-i) * cell_size),
                    (j * cell_size, scale, scale - (3-i) * cell_size)
                ]
            elif face == 'D':  # Down face
                return [
                    (j * cell_size, 0, (2-i) * cell_size),
                    ((j+1) * cell_size, 0, (2-i) * cell_size),
                    ((j+1) * cell_size, 0, (3-i) * cell_size),
                    (j * cell_size, 0, (3-i) * cell_size)
                ]

        # Draw all faces
        faces = ['F', 'B', 'U', 'D', 'L', 'R']
        for face in faces:
            if is_face_visible(face, angle_front, angle_side):
                for i in range(3):
                    for j in range(3):
                        color_idx = self.faces[face][i, j]
                        color = self.colors[color_idx]
                        vertices = map_coordinates(face, i, j)
                        draw_cell(vertices, color)

        # Update label positions
        label_positions = {
            'F': (scale/2, scale/2, scale + 0.01),
            'B': (scale/2, scale/2, -0.01),
            'R': (scale + 0.01, scale/2, scale/2),
            'L': (-0.01, scale/2, scale/2),
            'U': (scale/2, scale + 0.01, scale/2),
            'D': (scale/2, -0.01, scale/2)
        }

        # Draw labels with improved visibility
        for face, pos in label_positions.items():
            if is_face_visible(face, angle_front, angle_side):
                x, y, z = pos
                ax.text(x, y, z, face,
                    fontsize=30,
                    color='black',
                    ha='center',
                    va='center',
                    weight='bold',
                    bbox=dict(facecolor='white', 
                            alpha=0.8,
                            edgecolor='black',
                            pad=3),
                    zorder=100)

        ax.view_init(elev=angle_front, azim=angle_side)
        ax.set_box_aspect([1, 1, 1])
        ax.axis('off')
        ax.set_xlim(0, scale)
        ax.set_ylim(0, scale)
        ax.set_zlim(0, scale)
    
   
    def _get_face_state(self, face: str) -> Dict:
        """Get detailed state information about a specific face."""
        color_counts = defaultdict(int)
        color_matrix = []
        
        # 创建颜色矩阵并计算颜色计数
        for i in range(3):
            row = []
            for j in range(3):
                color_idx = int(self.faces[face][i, j])  # 转换为Python int
                color = self.colors[color_idx]
                row.append(color)
                color_counts[color] += 1
            color_matrix.append(row)
                
        # 确保所有值都是Python原生类型
        dominant_color = max(color_counts.items(), key=lambda x: x[1])[0]
        is_solved = bool(np.all(self.faces[face] == self.faces[face][0, 0]))  # 显式转换为Python bool
        matching_stickers = int(max(color_counts.values()))  # 转换为Python int
        
        return {
            'colors': color_matrix,
            'dominant_color': dominant_color,
            'is_solved': is_solved,
            'matching_stickers': matching_stickers,
            'color_counts': dict(color_counts)  # 转换defaultdict为普通dict
        }

    def get_full_state(self) -> Dict:
        """Return full information about cube state."""
        # 辅助函数：转换numpy类型为Python原生类型
        def convert_numpy_types(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.int_, np.int32, np.int64)):
                return int(obj)
            if isinstance(obj, (np.float_, np.float32, np.float64)):
                return float(obj)
            if isinstance(obj, np.bool_):
                return bool(obj)
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [convert_numpy_types(x) for x in obj]
            return obj

        # 构建状态字典
        state = {
            "faces": {face: self.faces[face].tolist() for face in self.faces},
            "colors": self.colors,
            "move_history": self.move_history,
            "face_states": {
                face: self._get_face_state(face) for face in self.faces
            },
            "is_solved": bool(self._is_solved()),  # 显式转换为Python bool
            "symbols": {
                "yellow": 0,
                "white": 1,
                "orange": 2,
                "red": 3,
                "blue": 4,
                "green": 5
            }
        }
        
        # 转换所有numpy类型为Python原生类型
        return convert_numpy_types(state)
    
    



    def _generate_detailed_analysis(self, face: str) -> str:
        """Generate detailed color analysis for a face."""
        FACES = {
            'F': 'Front face',
            'B': 'Back face',
            'L': 'Left face',
            'R': 'Right face',
            'U': 'Upper face',
            'D': 'Down face'
        }
        face_name = FACES[face]
        
        analysis = f"Analysis of {face_name}:\n\n"
        analysis += "Current state of each position:\n"
        
        for i in range(3):
            for j in range(3):
                color = self.colors[self.faces[face][i, j]]
                analysis += f"Position ({i},{j}): {color}\n"
                
        return analysis

    def generate_question(self, qtype: str) -> Tuple[str, str, List[str], int]:
        """Generate a question based on the specified type."""
        if qtype == 'face_recognition':
           
            question, analysis, options, correct_idx,face = self._generate_face_recognition()
            analysis = self._generate_detailed_analysis(face) + "\n" + analysis
            return question, analysis, options, correct_idx
            
        elif qtype == 'move_prediction':
            
            question, analysis, options, correct_idx = self._generate_move_prediction()

            return question, analysis, options, correct_idx
            
        elif qtype == 'single_face_solve':
            
            question, analysis, options, correct_idx,face = self._generate_single_face_solve()
            analysis = self._generate_detailed_analysis(face) + "\n" + analysis
            return question, analysis, options, correct_idx
            
        elif qtype == 'full_solve':
            question, analysis, options, correct_idx = self._generate_full_solve()
            
            return question, analysis, options, correct_idx
            
        elif qtype == 'color_count':
         
            question, analysis, options, correct_idx,face = self._generate_color_count()
            analysis = self._generate_detailed_analysis(face) + "\n" + analysis
            return question, analysis, options, correct_idx
            
        else:
            raise ValueError(f"Invalid question type: {qtype}")
    def _solve_single_face(self, face: str) -> List[str]:
        """Find optimal sequence of moves to solve a single face."""
        if self._is_face_solved(face):
            return []
        
        original_state = deepcopy(self.faces)
        seen_states = set()
        queue = deque([([], self.faces)])
        max_depth = 12  # Limit maximum search depth
        search_process = []  # Track detailed search process
        states_explored = 0
        
        def get_state_hash(faces):
            return str(faces[face].tobytes())  # Only care about target face state
            
        def try_move(move_sequence, current_faces):
            nonlocal states_explored
            self.faces = deepcopy(current_faces)
            prev_matching = self._evaluate_face(face)  # Record state before move
            self.make_move(move)
            new_state = deepcopy(self.faces)
            new_matching = self._evaluate_face(face)  # Record state after move
            state_hash = get_state_hash(new_state)
            
            states_explored += 1
            if state_hash not in seen_states:
                seen_states.add(state_hash)
                # Record detailed analysis of this move attempt
                move_analysis = {
                    'depth': len(move_sequence) + 1,
                    'move': move,
                    'prev_state': current_faces[face].tolist(),
                    'new_state': new_state[face].tolist(),
                    'prev_matching': prev_matching,
                    'new_matching': new_matching,
                    'improved': new_matching > prev_matching,
                    'selected': False  # Will be set to True if this move is chosen
                }
                search_process.append(move_analysis)
                
                # Only continue with this path if it didn't make things worse
                if new_matching >= prev_matching:
                    queue.append((move_sequence + [move], new_state))
                    move_analysis['selected'] = True
                
        # Breadth-first search
        while queue:
            move_sequence, current_state = queue.popleft()
            
            if len(move_sequence) >= max_depth:
                continue
                
            self.faces = deepcopy(current_state)
            if self._is_face_solved(face):
                self.faces = original_state
                return move_sequence, search_process, states_explored
                
            # Try all possible moves
            for move in ['F', 'B', 'L', 'R', 'U', 'D',
                        "F'", "B'", "L'", "R'", "U'", "D'"]:
                try_move(move_sequence, current_state)
        
        self.faces = original_state
        return [], search_process, states_explored  # No solution found

    def _solve_cube(self) -> Optional[List[str]]:
        """Find optimal sequence of moves to solve the entire cube."""
        if self._is_solved():
            return []
            
        original_state = deepcopy(self.faces)
        seen_states = set()
        queue = deque([([], self.faces)])
        max_depth = 20  # Limit maximum search depth
        search_process = []  # Track detailed search process
        states_explored = 0
        
        def get_state_hash(faces):
            return str({face: faces[face].tobytes() for face in faces})
            
        def try_move(move_sequence, current_faces):
            nonlocal states_explored
            self.faces = deepcopy(current_faces)
            prev_matching = sum(self._evaluate_face(f) for f in self.faces)
            prev_face_matching = {f: self._evaluate_face(f) for f in self.faces}
            
            self.make_move(move)
            new_state = deepcopy(self.faces)
            new_matching = sum(self._evaluate_face(f) for f in self.faces)
            new_face_matching = {f: self._evaluate_face(f) for f in self.faces}
            
            state_hash = get_state_hash(new_state)
            states_explored += 1
            
            if state_hash not in seen_states:
                seen_states.add(state_hash)
                # Record detailed analysis of this move attempt
                improved_faces = []
                worsened_faces = []
                for f in self.faces:
                    if new_face_matching[f] > prev_face_matching[f]:
                        improved_faces.append(f)
                    elif new_face_matching[f] < prev_face_matching[f]:
                        worsened_faces.append(f)
                
                move_analysis = {
                    'depth': len(move_sequence) + 1,
                    'move': move,
                    'prev_matching': prev_matching,
                    'new_matching': new_matching,
                    'improved_faces': improved_faces,
                    'worsened_faces': worsened_faces,
                    'face_states': {
                        f: {'before': current_faces[f].tolist(), 
                            'after': new_state[f].tolist(),
                            'matching_before': prev_face_matching[f],
                            'matching_after': new_face_matching[f]}
                        for f in self.faces
                    },
                    'selected': False  # Will be set to True if this move is chosen
                }
                search_process.append(move_analysis)
                
                # Only continue with moves that don't make overall state worse
                if new_matching >= prev_matching:
                    queue.append((move_sequence + [move], new_state))
                    move_analysis['selected'] = True
        
        # Breadth-first search
        while queue:
            move_sequence, current_state = queue.popleft()
            
            if len(move_sequence) >= max_depth:
                continue
                
            self.faces = deepcopy(current_state)
            if self._is_solved():
                self.faces = original_state
                return move_sequence, search_process, states_explored
                
            # Try all possible moves
            for move in ['F', 'B', 'L', 'R', 'U', 'D',
                        "F'", "B'", "L'", "R'", "U'", "D'"]:
                try_move(move_sequence, current_state)
        
        self.faces = original_state
        return None, search_process, states_explored  # No solution found

    def _generate_single_face_solve(self) -> Tuple[str, str, List[str], int,str]:
        """Generate a question about solving a single face."""
        face = random.choice(list(self.faces.keys()))
        if self._is_face_solved(face):
            return self._generate_single_face_solve()
            
        solution, search_process, states_explored = self._solve_single_face(face)
        if not solution:
            return ("Can't be solved.", 
                   "This face configuration cannot be solved.", 
                   ["Unsolvable"], 0)
                   
        actual_moves = len(solution)
        options = [actual_moves]

# 修改：扩大范围并生成8个选项
        lower_bound = max(1, actual_moves - 3)
        upper_bound = actual_moves + 10

        while len(options) < 8:
            num = random.randint(lower_bound, upper_bound)
            if num not in options:
                options.append(num)
                
        random.shuffle(options)
        correct_idx = options.index(len(solution))
        FACES = {
            'F': 'Front face',
            'B': 'Back face',
            'L': 'Left face',
            'R': 'Right face',
            'U': 'Upper face',
            'D': 'Down face'
        }
        face1 = FACES[face]

        if len(solution) == 1:
            analysis = f"Based on observation, rotating {solution[0]} will solve the {face1}.So the answer is {options[correct_idx]}. The option number is {correct_idx+1}."
        else:
        # Step 1: Detailed search process
            analysis = f"Step 1: Search Process\n"
            current_depth = 0
            current_step = 0
        
            try:
                for step in search_process:
                    if step['depth'] != current_depth:
                        current_depth = step['depth']
                        current_step = 0
                        analysis += f"\nDepth {current_depth}:"
                
                    current_step += 1
                    if step['selected']:
                        analysis += (
                        f"\n  Step {current_step}: Tried {step['move']} - "
                        f"Looking at state {'(better state found)' if step['improved'] else '(keeping current path)'} "
                        f"(Selected for further exploration)"
                    )
                    else:
                        analysis += (
                        f"\n  Step {current_step}: Tried {step['move']} - "
                        f"{'State already seen' if not step.get('improved', False) else 'Not a better state'}, skipping"
                    )
            except Exception as e:
                analysis = "Step 1: Search process details unavailable\n"
        
        # Step 2: Simple observation-based conclusion
            analysis += f"\n\nStep 2: Based on analysis, the solution requires the following sequence: "
            analysis += ", ".join([f"rotate {move}" for move in solution])+f"So the answer is {options[correct_idx]}. The option number is {correct_idx+1}."
        options_display = ", ".join(f"[{i+1}] {opt}" for i, opt in enumerate(options))
        question = (f"Rules: As shown in the figure, the Rubik's cube consists of both 3D views and an unfolded view. The 3D views show the cube from two angles: left-tilted 30 degrees looking down, and right-tilted ,30 degrees looking up. The cube has six faces: Upper (U), Down (D), Left (L), Right (R), Front (F), and Back (B). Each face can be rotated clockwise or counterclockwise.And for each face, the coordinates are determined based on the unfolded view: column number increases from left to right (0,1,2) and row number increases from bottom to top (0,1,2). Legend shown in the bottom left corner.Handedness issues in the 3D views can be ignored.An uppercase letter indicates which face to rotate ('F' for Front, 'B' for Back, 'L' for Left, 'R' for Right, 'U' for Upper, 'D' for Down), with a prime symbol (') denoting counterclockwise rotation and no prime symbol denoting clockwise rotation.How many moves are needed to solve the {face1} face?Options: {options_display}")

        return question, analysis, [str(opt) for opt in options], correct_idx,face
    def _generate_full_solve(self) -> Tuple[str, str, List[str], int]:
        """Generate a question about solving the entire cube."""
        if self._is_solved():
            self.make_move("R")
            self.make_move("U")
            
        solution, search_process, states_explored = self._solve_cube()
        if not solution:
            return ("Can't be solved.", 
                   "This cube configuration cannot be solved.", 
                   ["Unsolvable"], 0)
                   
        actual_moves = len(solution)
        options = [actual_moves]

# 修改：扩大范围并生成8个选项
        lower_bound = max(1, actual_moves - 3)
        upper_bound = actual_moves + 10

        while len(options) < 8:
            num = random.randint(lower_bound, upper_bound)
            if num not in options:
                options.append(num)
                
        random.shuffle(options)
        correct_idx = options.index(len(solution))
        
        if len(solution) == 1:
            analysis = f"Based on observation, rotating {solution[0]} will solve the entire cube.So the answer is {options[correct_idx]}. The option number is {correct_idx+1}."
        else:
        # Step 1: Detailed search process
            analysis = "Step 1: Search Process\n"
            current_depth = 0
            moves_at_depth = []
        
            try:
                for step in search_process:
                # When reaching a new depth, summarize previous depth
                    if step['depth'] != current_depth:
                        if moves_at_depth:
                            summary = (
                            f"\nAt depth {current_depth}, tried {len(moves_at_depth)} moves. "
                            f"Best improvement was {max(m['improvement'] for m in moves_at_depth)} matching cells. "
                            f"Selected {sum(1 for m in moves_at_depth if m['selected'])} moves for further exploration."
                        )
                            analysis += summary
                        current_depth = step['depth']
                        moves_at_depth = []
                
                # Record move attempts and their outcomes
                    if step['selected']:
                        affected_faces = []
                        if step['improved_faces']:
                         affected_faces.append(f"improved {', '.join(step['improved_faces'])}")
                        if step['worsened_faces']:
                         affected_faces.append(f"worsened {', '.join(step['worsened_faces'])}")
                    
                        move_result = (
                        f"\nTried {step['move']}: "
                        f"Changed total matching cells from {step['prev_matching']} to {step['new_matching']}. "
                        f"This move {', '.join(affected_faces) if affected_faces else 'had no immediate effect'}. "
                        f"State looks promising, will explore further."
                    )
                        analysis += move_result
                    else:
                        if step.get('worsened_faces'):
                            move_result = (
                            f"\nTried {step['move']}: "
                            f"Move worsened {', '.join(step['worsened_faces'])}. "
                            f"Backtracking to try different move."
                        )
                            analysis += move_result
                        else:
                            move_result = (
                            f"\nTried {step['move']}: "
                            f"This state was already seen or didn't improve the situation. "
                            f"Skipping to next move."
                        )
                            analysis += move_result
                        
                    moves_at_depth.append({
                    'improvement': step.get('new_matching', 0) - step.get('prev_matching', 0),
                    'selected': step['selected']
                })
            
            # Add final depth summary if any moves remain
                if moves_at_depth:
                    summary = (
                    f"\nAt depth {current_depth}, tried {len(moves_at_depth)} moves. "
                    f"Best improvement was {max(m['improvement'] for m in moves_at_depth)} matching cells. "
                    f"Selected {sum(1 for m in moves_at_depth if m['selected'])} moves for further exploration."
                )
                    analysis += summary
                
            except Exception as e:
                analysis = "Step 1: Search process details unavailable\n"
        
        # Step 2: Simple observation-based conclusion
            analysis += f"\n\nStep 2: Based on analysis, the solution requires the following sequence: "
            analysis += ", ".join([f"rotate {move}" for move in solution])+f"So the answer is {options[correct_idx]}. The option number is {correct_idx+1}."

        options_display = ", ".join(f"[{i+1}] {opt}" for i, opt in enumerate(options))
        
        
        question = (f"Rules: As shown in the figure, the Rubik's cube consists of both 3D views and an unfolded view. The 3D views show the cube from two angles: left-tilted 30 degrees looking down, and right-tilted ,30 degrees looking up. The cube has six faces: Upper (U), Down (D), Left (L), Right (R), Front (F), and Back (B). Each face can be rotated clockwise or counterclockwise.And for each face, the coordinates are determined based on the unfolded view: column number increases from left to right (0,1,2) and row number increases from bottom to top (0,1,2). Legend shown in the bottom left corner.Handedness issues in the 3D views can be ignored.An uppercase letter indicates which face to rotate ('F' for Front, 'B' for Back, 'L' for Left, 'R' for Right, 'U' for Upper, 'D' for Down), with a prime symbol (') denoting counterclockwise rotation and no prime symbol denoting clockwise rotation.How many moves are needed to solve the entire cube?Options: {options_display}")

        return question, analysis, [str(opt) for opt in options], correct_idx
def validate_move(move: str) -> bool:
    """Validate if a move string is legal.
    
    Valid moves are:
    - Single face rotations: F, B, L, R, U, D
    - Counter-clockwise rotations: F', B', L', R', U', D'
    """
    if len(move) not in [1, 2]:
        return False
    if move[0] not in ['F', 'B', 'L', 'R', 'U', 'D']:
        return False
    if len(move) == 2 and move[1] != "'":
        return False
    return True


def parse_algorithm(alg: str) -> List[str]:
    """Parse a space-separated algorithm string into a list of moves."""
    moves = alg.strip().split()
    return [m for m in moves if validate_move(m)]


def generate_random_cube(num_moves: int = 20) -> RubiksCube:
    """Generate a random cube state by applying random moves.
    
    Args:
        num_moves: Number of random moves to apply
        
    Returns:
        A new RubiksCube instance in a random state
    """
    cube = RubiksCube()
    moves = ['F', 'B', 'L', 'R', 'U', 'D', "F'", "B'", "L'", "R'", "U'", "D'"]
    
    for _ in range(num_moves):
        move = random.choice(moves)
        
        cube.make_move(move)
        
    return cube