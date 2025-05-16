import numpy as np
from PIL import Image
import json
import random
import os
import cv2
from typing import List, Tuple, Dict
import colorsys

def create_color_swatch(color, width=60, height=40):
    """Create a color swatch for the options area"""
    swatch = np.full((height, width, 3), color, dtype=np.uint8)
    cv2.rectangle(swatch, (0, 0), (width-1, height-1), (0, 0, 0), 1)
    return swatch

def create_cell_image(color, cell_size=60, empty=False, cell_label=None):
    """Create a single cell image with proper formatting"""
    cell = np.full((cell_size, cell_size, 3), 255, dtype=np.uint8)
    
    if empty:
        if not cell_label:
            # Create more visible line pattern for unused cells
            cell.fill(245)
            line_spacing = 12
            line_color = (200, 200, 200)
            line_thickness = 2
            
            # Draw lines from top-left to bottom-right
            for i in range(-cell_size, cell_size * 2, line_spacing):
                start_point = (max(0, i), max(0, -i))
                end_point = (min(cell_size, i + cell_size), min(cell_size, -i + cell_size))
                cv2.line(cell, start_point, end_point, line_color, line_thickness)
            
            # Draw lines from top-right to bottom-left
            for i in range(-cell_size, cell_size * 2, line_spacing):
                start_point = (min(cell_size, i), max(0, i - cell_size))
                end_point = (max(0, i - cell_size), min(cell_size, i))
                cv2.line(cell, start_point, end_point, line_color, line_thickness)
                
        if cell_label:
            cell.fill(255)
            cv2.putText(cell, cell_label, (cell_size//3, 2*cell_size//3),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    else:
        margin = 2
        cv2.rectangle(cell, (margin, margin), 
                     (cell_size-margin, cell_size-margin),
                     color.tolist(), -1)
    
    cv2.rectangle(cell, (0, 0), (cell_size-1, cell_size-1), (0, 0, 0), 1)
    return cell

def generate_distant_color(existing_colors, num_colors=1):
    """Generate colors that are maximally distant from existing colors"""
    def color_distance(c1, c2):
        hsv1 = colorsys.rgb_to_hsv(c1[0]/255, c1[1]/255, c1[2]/255)
        hsv2 = colorsys.rgb_to_hsv(c2[0]/255, c2[1]/255, c2[2]/255)
        h_diff = min(abs(hsv1[0] - hsv2[0]), 1 - abs(hsv1[0] - hsv2[0]))
        s_diff = abs(hsv1[1] - hsv2[1])
        v_diff = abs(hsv1[2] - hsv2[2])
        return h_diff + s_diff + v_diff

    new_colors = []
    for _ in range(num_colors):
        max_min_distance = 0
        best_color = None
        
        for _ in range(100):
            color = np.array([random.randint(0, 255) for _ in range(3)])
            min_distance = float('inf')
            
            for existing_color in existing_colors + new_colors:
                dist = color_distance(color, existing_color)
                min_distance = min(min_distance, dist)
            
            if min_distance > max_min_distance:
                max_min_distance = min_distance
                best_color = color
        
        new_colors.append(best_color)
    
    return new_colors if num_colors > 1 else new_colors[0]

def get_color_name(rgb):
    """Convert RGB color to human-readable name"""
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h = h * 360
    
    if v < 0.2:
        return "black"
    if v > 0.9 and s < 0.1:
        return "white"
    if s < 0.15:
        return f"{'dark' if v < 0.5 else 'light'} gray"
    
    color_ranges = {
        (330, 30): "red",
        (30, 60): "orange",
        (60, 90): "yellow",
        (90, 150): "green",
        (150, 200): "cyan",
        (200, 240): "blue",
        (240, 270): "indigo",
        (270, 330): "purple"
    }
    
    base_color = None
    for (start, end), name in color_ranges.items():
        if start <= h <= end or (start > end and (h >= start or h <= end)):
            base_color = name
            break
    
    if not base_color:
        return "gray"
    
    modifiers = []
    if s < 0.4:
        modifiers.append("pale")
    elif s > 0.8:
        modifiers.append("vivid")
        
    if v < 0.4:
        modifiers.append("dark")
    elif v > 0.8:
        modifiers.append("bright")
        
    return f"{' '.join(modifiers)} {base_color}" if modifiers else base_color

def describe_gradient(start_color, end_color=None, direction=None):
    """Create a human-readable description of a color gradient"""
    if end_color is None and direction is not None:
        base_color = get_color_name(start_color)
        return f"gradually getting {'lighter' if direction == 1 else 'darker'} from {base_color}"
    
    elif start_color is not None and end_color is not None:
        start_name = get_color_name(start_color)
        end_name = get_color_name(end_color)
        
        if start_name == end_name:
            start_hsv = colorsys.rgb_to_hsv(start_color[0]/255, start_color[1]/255, start_color[2]/255)
            end_hsv = colorsys.rgb_to_hsv(end_color[0]/255, end_color[1]/255, end_color[2]/255)
            
            return f"transitioning from {'darker' if end_hsv[2] > start_hsv[2] else 'lighter'} to {'lighter' if end_hsv[2] > start_hsv[2] else 'darker'} {start_name}"
        else:
            return f"transitioning from {start_name} to {end_name}"
    
    return "gradient pattern"

def find_relevant_gradients(board, target_pos):
    """Find all gradients that could influence the target position"""
    relevant_gradients = []
    for gradient in board.gradient_info:
        if gradient["type"] == "row" and gradient["index"] == target_pos[0]:
            relevant_gradients.append(("row", gradient))
        if gradient["type"] == "column" and gradient["index"] == target_pos[1]:
            relevant_gradients.append(("column", gradient))
        if gradient["type"] == "row" and abs(gradient["index"] - target_pos[0]) == 1:
            relevant_gradients.append(("nearby row", gradient))
        if gradient["type"] == "column" and abs(gradient["index"] - target_pos[1]) == 1:
            relevant_gradients.append(("nearby column", gradient))
    
    return relevant_gradients

class ColorBoard:
    def __init__(self, size: int = 6):
        self.size = size
        self.board = np.zeros((size, size, 3), dtype=np.uint8)
        self.colored_cells = set()
        self.cells_to_fill = {}
        self.cell_size = 60
        self.gradient_info = []
        self.removed_colors = []
        self.extra_options = []
        self.removed_positions = []

    def get_rules_description(self) -> str:
        """Return a fixed description of the color gradient rules"""
        return ("Rules:\n"
                "1. Colors change gradually along rows or columns.\n"
                "2. A gradient transitions between two colors.\n"
                "3. Each row or column can have its own independent gradient pattern.\n"
                "4. Row and column indexes begin from 1 at the top-left corner.\n")

    def generate_color_question(self) -> dict:
        """Generate a question about a specific cell's color"""
        valid_cells = [(i, j) for i in range(self.size) for j in range(self.size) 
                      if (i, j) in self.colored_cells and (i, j) not in self.cells_to_fill]
        if not valid_cells:
            return None
            
        target_pos = random.choice(valid_cells)
        target_color = self.board[target_pos]
        correct_description = get_color_name(target_color)
        
        wrong_descriptions = set()
        while len(wrong_descriptions) < 7:
            wrong_color = generate_distant_color([])
            wrong_desc = get_color_name(wrong_color)
            if wrong_desc != correct_description:
                wrong_descriptions.add(wrong_desc)
        
        options = list(wrong_descriptions) + [correct_description]
        random.shuffle(options)
        
        question_text = (
            f"{self.get_rules_description()}\n\n"
            f"Question:\nWhat color is the cell at row {target_pos[0] + 1}, column {target_pos[1] + 1}?\n\n"
            f"Options:\n" + "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options))
        )
        
        return {
            "question": question_text,
            "answer": options.index(correct_description) + 1,
            "options": options,
            "qa_type": "color_description",
            "analysis": f"The cell at position ({target_pos[0] + 1}, {target_pos[1] + 1}) is {correct_description}. So the answer is Option {options.index(correct_description) + 1}."
        }

    def generate_gradient_question(self) -> dict:
        """Generate a question about a gradient pattern"""
        if not self.gradient_info:
            return None
            
        gradient = random.choice(self.gradient_info)
        gradient_type = gradient["type"]
        index = gradient["index"]
        
        if gradient["start_color"] is not None and gradient["end_color"] is not None:
            correct_desc = describe_gradient(gradient["start_color"], gradient["end_color"])
        else:
            correct_desc = describe_gradient(gradient["start_color"], direction=gradient["direction"])
        
        wrong_descriptions = set()
        while len(wrong_descriptions) < 7:
            color1 = generate_distant_color([])
            color2 = generate_distant_color([color1])
            wrong_desc = describe_gradient(color1, color2)
            if wrong_desc != correct_desc:
                wrong_descriptions.add(wrong_desc)
        
        options = list(wrong_descriptions) + [correct_desc]
        random.shuffle(options)
    
        line_type = "row" if gradient_type == "row" else "column"
        
        question_text = (
            f"{self.get_rules_description()}\n\n"
            f"Question:\nWhat is the gradient pattern in {line_type} {index + 1}?\n\n"
            f"Options:\n" + "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options))
        )
        
        return {
            "question": question_text,
            "answer": options.index(correct_desc) + 1,
            "options": options,
            "qa_type": "gradient_pattern",
            "analysis": f"The {line_type} {index + 1} shows a pattern that is {correct_desc}. So the answer is Option {options.index(correct_desc) + 1}."
        }

    def mix_colors(self, color1: np.ndarray, color2: np.ndarray, ratio: float) -> np.ndarray:
        """Linear interpolation between two colors"""
        mix = np.clip((1 - ratio) * color1 + ratio * color2, 0, 255)
        return mix.astype(np.uint8)
    def add_line(self) -> bool:
        """Add either a row or column with color gradient"""
        # Try several times to find a valid line that doesn't violate adjacency rules
        for _ in range(10):
            is_row = random.choice([True, False])
            idx = random.randint(0, self.size - 1)
            
            # Check if this line would be adjacent to a parallel gradient
            has_adjacent_parallel = False
            for gradient in self.gradient_info:
                if gradient["type"] == ("row" if is_row else "column"):
                    if abs(gradient["index"] - idx) == 1:
                        has_adjacent_parallel = True
                        break
            
            if has_adjacent_parallel:
                continue
                
            line_colored = []
            for i in range(self.size):
                coord = (idx, i) if is_row else (i, idx)
                if coord in self.colored_cells:
                    line_colored.append(coord)
            
            gradient_info = {
                "type": "row" if is_row else "column",
                "index": idx,
                "start_color": None,
                "end_color": None,
                "direction": None
            }
            
            if not line_colored:
                # For empty lines, create a partial gradient
                start_idx = random.randint(0, 1) 
                end_idx = random.randint(self.size - 2, self.size - 1)
                
                color1 = np.array([random.randint(0, 255) for _ in range(3)])
                color2 = np.array([random.randint(0, 255) for _ in range(3)])
                gradient_info["start_color"] = color1
                gradient_info["end_color"] = color2
                
                for i in range(start_idx, end_idx + 1):
                    pos = (idx, i) if is_row else (i, idx)
                    ratio = (i - start_idx) / (end_idx - start_idx)
                    self.board[pos[0], pos[1]] = self.mix_colors(color1, color2, ratio)
                    self.colored_cells.add(pos)
                    
            elif len(line_colored) == 1:
                # Create bidirectional gradient from the single colored cell
                base_color = self.board[line_colored[0]]
                base_pos = line_colored[0][1] if is_row else line_colored[0][0]
                
                # Generate darker and lighter versions for both directions
                darker_color = self.mix_colors(base_color,np.zeros(3),0.5)  # Black
                lighter_color = self.mix_colors(base_color,np.full(3, 255),0.5)  # White
                
                gradient_info["start_color"] = darker_color.copy()
                gradient_info["end_color"] = lighter_color.copy()
                
                # Fill cells before the colored cell (going darker)
                for i in range(base_pos - 1, -1, -1):
                    ratio = (base_pos - i) / base_pos if base_pos > 0 else 0
                    pos = (idx, i) if is_row else (i, idx)
                    self.board[pos[0], pos[1]] = self.mix_colors(base_color, darker_color, ratio)
                    self.colored_cells.add(pos)
                
                # Fill cells after the colored cell (going lighter)
                remaining_cells = self.size - base_pos - 1
                for i in range(base_pos + 1, self.size):
                    ratio = (i - base_pos) / (self.size - base_pos - 1) if remaining_cells > 0 else 0
                    pos = (idx, i) if is_row else (i, idx)
                    self.board[pos[0], pos[1]] = self.mix_colors(base_color, lighter_color, ratio)
                    self.colored_cells.add(pos)
                
            else:
                # Find two colored cells with no colored cells between them
                valid_pairs = []
                line_colored.sort(key=lambda x: x[1] if is_row else x[0])
                
                for i in range(len(line_colored) - 1):
                    start_cell = line_colored[i]
                    end_cell = line_colored[i + 1]
                    start_idx = start_cell[1] if is_row else start_cell[0]
                    end_idx = end_cell[1] if is_row else end_cell[0]
                    
                    # Check if there are no colored cells between these two
                    has_colored_between = False
                    for j in range(start_idx + 1, end_idx):
                        pos = (idx, j) if is_row else (j, idx)
                        if pos in self.colored_cells:
                            has_colored_between = True
                            break
                    
                    if not has_colored_between and end_idx - start_idx >= 2:
                        valid_pairs.append((start_cell, end_cell))
                
                if not valid_pairs:
                    continue
                
                start_cell, end_cell = random.choice(valid_pairs)
                start_color = self.board[start_cell]
                end_color = self.board[end_cell]
                gradient_info["start_color"] = start_color.copy()
                gradient_info["end_color"] = end_color.copy()
                
                start_pos = start_cell[1] if is_row else start_cell[0]
                end_pos = end_cell[1] if is_row else end_cell[0]
                
                # Fill the gap between the two cells
                for i in range(start_pos + 1, end_pos):
                    pos = (idx, i) if is_row else (i, idx)
                    if pos not in self.colored_cells:
                        ratio = (i - start_pos) / (end_pos - start_pos)
                        self.board[pos[0], pos[1]] = self.mix_colors(start_color, end_color, ratio)
                        self.colored_cells.add(pos)
            
            self.gradient_info.append(gradient_info)
            return True
        
        return False  # Could not find a valid line after multiple attempts

    def set_color_options(self, removed_positions, removed_colors, extra_options):
        """Store color options for analysis and shuffle the color order"""
        self.removed_positions = removed_positions
        
        # Create a shuffled mapping of colors
        all_colors = removed_colors + extra_options
        shuffled_indices = list(range(len(all_colors)))
        random.shuffle(shuffled_indices)
        
        # Map the original colors to their new positions
        self.color_mapping = {i: shuffled_indices[i] for i in range(len(all_colors))}
        self.inverse_color_mapping = {v: k for k, v in self.color_mapping.items()}
        
        # Store the shuffled colors
        self.removed_colors = removed_colors  # Keep original order for position mapping
        self.shuffled_colors = [all_colors[self.inverse_color_mapping[i]] for i in range(len(all_colors))]
        self.extra_options = []  # Now handled in shuffled_colors

    def create_image_with_options(self, removed_colors, extra_options):
        """Create the full board image with options below and indices on top/left"""
        board_size = self.size * self.cell_size
        options_height = 70
        padding = 20
        index_margin = 30  # Space for row/column indices
        
        # Create larger image to accommodate indices
        img = np.full((board_size + padding + options_height + index_margin, 
                    board_size + index_margin, 3), 255, dtype=np.uint8)
        
        # Add row indices (1-based)
        for i in range(self.size):
            cv2.putText(img, str(i + 1), 
                    (10, index_margin + i * self.cell_size + self.cell_size//2 + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Add column indices (1-based)
        for j in range(self.size):
            cv2.putText(img, str(j + 1), 
                    (index_margin + j * self.cell_size + self.cell_size//3, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Draw the board
        for i in range(self.size):
            for j in range(self.size):
                pos = (i, j)
                cell_color = self.board[i, j]
                
                cell_label = self.cells_to_fill.get(pos)
                
                if pos in self.cells_to_fill:
                    cell = create_cell_image(cell_color, self.cell_size, empty=True, cell_label=cell_label)
                elif pos in self.colored_cells:
                    cell = create_cell_image(cell_color, self.cell_size)
                else:
                    cell = create_cell_image(np.array([255, 255, 255]), self.cell_size, empty=True)
                
                y_start = index_margin + i * self.cell_size
                x_start = index_margin + j * self.cell_size
                img[y_start:y_start+self.cell_size, 
                    x_start:x_start+self.cell_size] = cell
        
        # Draw the color options using shuffled colors
        if hasattr(self, 'shuffled_colors') and self.shuffled_colors:
            option_width = (board_size + index_margin) // len(self.shuffled_colors)
            for idx, color in enumerate(self.shuffled_colors):
                swatch = create_color_swatch(color, width=option_width-10)
                
                x_start = idx * option_width + 5
                y_start = board_size + padding + index_margin + 20
                
                cv2.putText(img, f"{idx + 1}", 
                        (x_start, y_start - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                
                swatch_height = swatch.shape[0]
                img[y_start:y_start+swatch_height,
                    x_start:x_start+swatch.shape[1]] = swatch
                
        return img

    def generate_color_matching_question(self, target_label: str) -> dict:
        """Generate a color matching question for a specific cell"""
        target_pos = None
        for pos, label in self.cells_to_fill.items():
            if label == target_label:
                target_pos = pos
                break
        
        if target_pos is None:
            return None
        
        # Find the original color index and map it to the shuffled position
        original_color_idx = self.removed_positions.index(target_pos)
        shuffled_answer = self.color_mapping[original_color_idx] + 1  # Add 1 for 1-based indexing
        
        question_text = (
            f"{self.get_rules_description()}\n\n"
            f"Question:\nWhich color should be put in cell {target_label}?\n\n"
            "Options:\nColors are numbered from 1 to 6 in the palette below"
        )
        
        return {
            "question": question_text,
            "answer": shuffled_answer,
            "options": list(range(1, len(self.shuffled_colors) + 1)),
            "qa_type": "color_matching",
            "analysis": self.generate_analysis(target_label)
        }

    def generate_analysis(self, target_label):
        """Generate structured analysis of the solution"""
        analysis = []
        
        target_pos = None
        for pos, label in self.cells_to_fill.items():
            if label == target_label:
                target_pos = pos
                break
        
        analysis.append(f"We need to find the correct color for cell {target_label} "
                    f"at position ({target_pos[0] + 1}, {target_pos[1] + 1})")
        
        relevant_gradients = find_relevant_gradients(self, target_pos)
        
        if relevant_gradients:
            analysis.append("\nLet's analyze the color patterns around this cell:")
            
            for gradient_type, gradient in relevant_gradients:
                if gradient_type.startswith("nearby"):
                    continue
                    
                direction_text = "horizontally" if gradient_type == "row" else "vertically"
                
                if all(key in gradient and gradient[key] is not None 
                    for key in ['start_color', 'end_color']):
                    gradient_desc = describe_gradient(gradient['start_color'], gradient['end_color'])
                    analysis.append(f"- Looking {direction_text}, we see a pattern {gradient_desc}")
                elif gradient.get('start_color') is not None:
                    gradient_desc = describe_gradient(gradient['start_color'], 
                                                    direction=gradient.get('direction', 0))
                    analysis.append(f"- Looking {direction_text}, we see a pattern {gradient_desc}")
        else:
            analysis.append("\nLet's look at the colors in nearby cells:")
            
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x, new_y = target_pos[0] + dx, target_pos[1] + dy
                if (0 <= new_x < self.size and 0 <= new_y < self.size and 
                    (new_x, new_y) not in self.cells_to_fill):
                    color = self.board[new_x, new_y]
                    direction = "above" if dx < 0 else "below" if dx > 0 else "to the left" if dy < 0 else "to the right"
                    if not all(c == 255 for c in color):
                        neighbors.append((direction, get_color_name(color)))
            
            if neighbors:
                for direction, color in neighbors:
                    analysis.append(f"- The cell {direction} is {color}")
        
        analysis.append("\nLet's look at our color options:")
        for i, color in enumerate(self.shuffled_colors, 1):
            color_name = get_color_name(color)
            analysis.append(f"Option {i} is {color_name}")
        
        original_color_idx = self.removed_positions.index(target_pos)
        shuffled_answer = self.color_mapping[original_color_idx] + 1
        correct_color = self.shuffled_colors[shuffled_answer - 1]
        color_name = get_color_name(correct_color)
        analysis.append(f"\nBased on the pattern, we should use {color_name} (Option {shuffled_answer})")
        
        return "\n".join(analysis)
    
    
def get_plot_level(board_size):
    """Determine plot level based on grid size"""
    if board_size <= 5:
        return "Easy"
    elif board_size <= 7:
        return "Medium"
    else:
        return "Hard"

def get_qa_level(question_type):
    """Determine question level based on type"""
    qa_level_mapping = {
        "color_description": "Easy",  # Simply identifying a color
        "gradient_pattern": "Medium", # Understanding color patterns
        "color_matching": "Hard"      # Requires analyzing multiple patterns and relationships
    }
    return qa_level_mapping[question_type]

def generate_dataset(num_questions: int):
    os.makedirs(outputFolder+"/images", exist_ok=True)
    os.makedirs(outputFolder+"/states", exist_ok=True)
    
    dataset = []
    generator = QuestionGenerator()
    
    for _ in range(num_questions):
        board_size = random.randint(5, 8)
        num_lines = random.randint(3, 4)
        num_removed = random.randint(3, 6)
        num_extra_options = 6 - num_removed  # Ensure total options is always 6
        
        board = ColorBoard(board_size)
        for _ in range(num_lines):
            board.add_line()
            
        question_types=["color_matching", "color_description", "gradient_pattern"]
        question_descriptions=["Ask which option's color fits a specific empty cell","Ask what color a specific cell is","Ask what the gradient pattern is in a specific row or column"]
        qa_types=['ActionOutcome','StateInfo','StateInfo']
        question_type = random.choice(question_types)
        question_type_index=question_types.index(question_type)
        
        if question_type == "color_matching":
            removed_positions = random.sample(list(board.colored_cells), num_removed)
            removed_colors = []
            labels = list('ABCDEFGH')[:num_removed]
            
            for pos, label in zip(removed_positions, labels):
                color = tuple(map(int, board.board[pos[0], pos[1]]))
                removed_colors.append(color)
                board.board[pos[0], pos[1]] = (255, 255, 255)
                board.cells_to_fill[pos] = label

            extra_options = []
            existing_colors = removed_colors.copy()
            for _ in range(num_extra_options):
                new_color = generate_distant_color(existing_colors)
                extra_options.append(new_color)
                existing_colors.append(new_color)
            
            board.set_color_options(removed_positions, removed_colors, extra_options)
            
            target_pos = random.choice(removed_positions)
            target_label = board.cells_to_fill[target_pos]
            
            qa_pair = board.generate_color_matching_question(target_label)
            
        else:
            if question_type == "color_description":
                qa_pair = board.generate_color_question()
            else:
                qa_pair = board.generate_gradient_question()
                
            if qa_pair is None:
                continue
        
        # Add plot_level and qa_level to the output
        plot_level = get_plot_level(board_size)
        qa_level = get_qa_level(question_type)
        
        qa_pair.update({
            "data_id": f"color-mcq-{generator.question_count+1:05d}-{qa_pair['qa_type']}",
            'qa_type':qa_types[question_type_index],
            "question_id":question_type_index,
            "question_description":question_type,
            "plot_id": f"color-plot-{generator.question_count+1:05d}",
            "image": f"images/color-mcq-{generator.question_count+1:05d}.png",
            "state": f"states/color-mcq-{generator.question_count+1:05d}.json",
            "plot_level": plot_level,  # Based on grid size
            "qa_level": qa_level      # Based on question type
        })
        
        img = board.create_image_with_options(
            removed_colors if question_type == "color_matching" else [], 
            extra_options if question_type == "color_matching" else []
        )
        cv2.imwrite(f"{outputFolder}/{qa_pair['image']}", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        
        state = {
            "board": board.board.tolist(),
            "removed_positions": [tuple(pos) for pos in getattr(board, 'removed_positions', [])],
            "removed_colors": [tuple(map(int, color)) for color in getattr(board, 'removed_colors', [])],
            "extra_options": [tuple(map(int, color)) for color in getattr(board, 'extra_options', [])],
            "cell_labels": {str(pos): label for pos, label in board.cells_to_fill.items()},
            "gradient_info": [
                {
                    "type": info["type"],
                    "index": int(info["index"]),
                    "direction": int(info["direction"]) if info.get("direction") is not None else None,
                    "start_color": tuple(map(int, info["start_color"])) if info.get("start_color") is not None else None,
                    "end_color": tuple(map(int, info["end_color"])) if info.get("end_color") is not None else None
                }
                for info in board.gradient_info
            ]
        }
        with open(f"{outputFolder}/{qa_pair['state']}", 'w') as f:
            json.dump(state, f)
            
        dataset.append(qa_pair)
        generator.question_count += 1
    
    with open(outputFolder+"/data.json", 'w') as f:
        json.dump(dataset, f, indent=2)
    
    return dataset

class QuestionGenerator:
    def __init__(self):
        self.question_count = 0
        
if __name__ == "__main__":
    outputFolder="hue_dataset"
    dataset = generate_dataset(5000)
    print("Dataset generated successfully!")
    print(f"Number of questions generated: {len(dataset)}")
