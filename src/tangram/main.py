import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
import os
from typing import Dict, List, Tuple, Any
import random
from dataclasses import dataclass, asdict
import colorsys
from matplotlib.colors import rgb2hex, hex2color

@dataclass
class PuzzleConfig:
    grid_size: int
    num_seeds: int
    num_pieces_to_remove: int
    
@dataclass
class QAPair:
    data_id: str
    qa_type: str
    question_id: int
    question_description: str
    image: str
    state: str
    plot_level: str
    qa_level: str
    question: str
    answer: int
    analysis: str
    options: List[str]

@dataclass
class Piece:
    id: int
    width: int
    height: int
    cells: List[Tuple[int, int]]

class TengramGenerator:
    def __init__(self, config: PuzzleConfig):
        self.config = config
        self.grid = np.zeros((config.grid_size, config.grid_size), dtype=int)
        self.seeds = []
        self.pieces = []
        self.pieceMaxWidth = 0
        self.pieceMaxHeight = 0
        self.removed_pieces = []
        # Create a fixed color mapping that will be consistent across all plots
        self.color_mapping = self._create_fixed_color_mapping()
        
    def _create_fixed_color_mapping(self):
        """Create a fixed RGB color mapping that will be consistent across all plots"""
        # Define base colors (RGB values between 0-1)
        colors = [
            (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),  # blue
            (1.0, 0.4980392156862745, 0.054901960784313725),  # orange
            (0.17254901960784313, 0.6274509803921569, 0.17254901960784313),  # green
            (0.8392156862745098, 0.15294117647058825, 0.1568627450980392),  # red
            (0.5803921568627451, 0.403921568627451, 0.7411764705882353),  # purple
            (0.5490196078431373, 0.33725490196078434, 0.29411764705882354),  # brown
            (0.9901960784313725, 0.6666666666666667, 0.7607843137254902),  # pink
            (0.4980392156862745, 0.4980392156862745, 0.4980392156862745),  # gray
            (0.7372549019607844, 0.7411764705882353, 0.13333333333333333),  # yellow
            (0.09019607843137255, 0.7450980392156863, 0.8117647058823529),  # cyan
        ]
        # for r, g, b in colors:
        #     print(self.get_color_name((r*255, g*255, b*255)))
        # Duplicate colors with different intensities
        light_colors = [(r + (1-r)*0.6, g + (1-g)*0.6, b + (1-b)*0.6) for r, g, b in colors]
        colors.extend(light_colors)
        # Convert to 0-255 range for easier use
        colors = [(int(r*255), int(g*255), int(b*255)) for r, g, b in colors]
        dic={i: colors[i-1] for i in range(1, len(colors)+1)}
        dic[0]=(255,255,255)
        return dic
    
    def generate_seeds(self) -> None:
        """Generate random seed points for Voronoi regions"""
        points = []
        while len(points) < self.config.num_seeds:
            x = np.random.randint(0, self.config.grid_size)
            y = np.random.randint(0, self.config.grid_size)
            if (x, y) not in points:
                points.append((x, y))
        self.seeds = points

    def assign_cells_to_seeds(self) -> None:
        """Assign each cell to closest seed point"""
        for i in range(self.config.grid_size):
            for j in range(self.config.grid_size):
                min_dist = float('inf')
                closest_seed = 0
                for idx, (seed_x, seed_y) in enumerate(self.seeds):
                    dist = (i - seed_x)**2 + (j - seed_y)**2
                    if dist < min_dist:
                        min_dist = dist
                        closest_seed = idx + 1  # 1-based indexing
                self.grid[i, j] = closest_seed
        self.calc_pieces()
    
    def calc_pieces(self) -> None:
        """Assign value to self.pieces after calling assign_cells_to_seeds"""
        self.pieces = []
        self.pieceMaxHeight=0
        self.pieceMaxWidth=0
        minxes=[self.config.grid_size]*self.config.num_seeds
        minyes=[self.config.grid_size]*self.config.num_seeds
        maxxes=[0]*self.config.num_seeds
        maxyes=[0]*self.config.num_seeds
        for piece_id in range(1, self.config.num_seeds + 1):
            cells = np.argwhere(self.grid == piece_id)
            minx = min(cells[:, 0])
            miny = min(cells[:, 1])
            maxx = max(cells[:, 0])
            maxy = max(cells[:, 1])
            minxes[piece_id-1]=minx
            minyes[piece_id-1]=miny
            maxxes[piece_id-1]=maxx
            maxyes[piece_id-1]=maxy
            height = maxx - minx + 1
            width = maxy - miny + 1
            self.pieceMaxWidth=max(self.pieceMaxWidth,width)
            self.pieceMaxHeight=max(self.pieceMaxHeight,height)
            
            # crop grid to piece
            cellArray = np.zeros((height, width), dtype=int)
            for cell in cells:
                cellArray[cell[0]-minx, cell[1]-miny] = piece_id
            self.pieces.append(Piece(piece_id, width, height, cellArray))

    def remove_random_pieces(self) -> None:
        """Remove random pieces from the board"""
        available_pieces = list(range(1, self.config.num_seeds + 1))
        pieces_to_remove = random.sample(available_pieces, 
                                       self.config.num_pieces_to_remove)
        self.removed_pieces = pieces_to_remove
        for piece in pieces_to_remove:
            self.grid[self.grid == piece] = 0
            
    def _draw_shaded_cell(self, ax, i, j, color='black', line_num=6, linewidth=1):
        """Draw a shaded cell at position (i, j)"""
        # Draw lines from top-left to bottom-right
        for d in range(-line_num, line_num, 1):
            d = d / line_num
            start_point = (max(0, d), max(0, -d)) 
            end_point = (min(1, d + 1), min(1, -d + 1)) 
            ax.plot([j + start_point[0] - 0.5, j + end_point[0] - 0.5], 
                    [i + start_point[1] - 0.5, i + end_point[1] - 0.5], 
                    color=color, linewidth=linewidth)

    def plot_puzzle(self, output_path: str) -> None:
        """Plot the puzzle state with main board and removed pieces"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 6))
        # plt.rcParams.update({'font.size': 30})
        # Create RGB arrays for visualization
        board_rgb = np.zeros((self.config.grid_size, self.config.grid_size, 3), dtype=np.uint8)
        for i in range(self.config.grid_size):
            for j in range(self.config.grid_size):
                piece_id = self.grid[i, j]
                board_rgb[i, j] = self.color_mapping[piece_id]
        
        # Plot main board
        ax1.imshow(board_rgb)
        ax1.set_title('Main Board')
        
        # Add grid and numbers
        for i in range(self.config.grid_size):
            for j in range(self.config.grid_size):
                ax1.axhline(y=i-0.5, color='black', linewidth=0.5)
                ax1.axvline(x=j-0.5, color='black', linewidth=0.5)
                if self.grid[i, j] != 0:
                    ax1.text(j, i, str(self.grid[i, j]), 
                            ha='center', va='center')
                else:  # draw dense lines for empty cells
                    self._draw_shaded_cell(ax1, i, j, color='black', line_num=6, linewidth=1)
                        
        # Add ticks at center of edges
        ax1.set_xticks(np.arange(self.config.grid_size))
        ax1.set_yticks(np.arange(self.config.grid_size))
    
        # Plot removed pieces
        widthNeeded = -1
        heightNeeded = -1
        for piece in self.removed_pieces:
            widthNeeded += self.pieces[piece-1].width + 1
            heightNeeded = max(heightNeeded, self.pieces[piece-1].height)

        removed_grid = np.zeros((heightNeeded, widthNeeded), dtype=int)
        removed_rgb = np.zeros((heightNeeded, widthNeeded, 3), dtype=np.uint8)
        currentWidth = 0
        for piece in self.removed_pieces:
            pieceWidth = self.pieces[piece-1].width
            pieceHeight = self.pieces[piece-1].height
            piece_cells = self.pieces[piece-1].cells
            removed_grid[0:pieceHeight, currentWidth:currentWidth+pieceWidth] = piece_cells
            
            # Fill RGB values for the piece
            for i in range(pieceHeight):
                for j in range(pieceWidth):
                    removed_rgb[i, currentWidth+j] = self.color_mapping[piece_cells[i, j]]
                    if piece_cells[i, j] > 0:
                        ax2.text(currentWidth+j, i, str(piece), ha='center', va='center')
            currentWidth += pieceWidth + 1
        for i in range(heightNeeded):
            for j in range(widthNeeded):
                if removed_rgb[i, j][0] == 0 and removed_rgb[i, j][1] == 0 and removed_rgb[i, j][2] == 0:
                    removed_rgb[i, j] = (240,240,240)
        
        # Plot removed pieces
        ax2.imshow(removed_rgb)
        ax2.set_title('Removed Pieces')
        
        # Add grid lines and shading for removed pieces
        for i in range(heightNeeded):
            for j in range(widthNeeded):
                ax2.axhline(y=i-0.5, color='black', linewidth=0.5)
                ax2.axvline(x=j-0.5, color='black', linewidth=0.5)
                if removed_grid[i, j] == 0:
                    self._draw_shaded_cell(ax2, i, j, color='black', line_num=6, linewidth=1)
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
    def get_color_name(self, rgb):
        """Convert RGB color to human-readable name"""
        r, g, b = rgb
        while r>1 or g>1 or b>1:
            r, g, b = [x/255 for x in (r, g, b)]
        h, s, v = colorsys.rgb_to_hsv(r,g,b)
        h = h * 360
        
        if v < 0.2:
            return "black"
        if v > 0.9 and s < 0.1:
            return "white"
        if s < 0.15:
            return f"{'dark' if v < 0.5 else 'light'} gray"
        
        color_ranges = {
            (330, 20): "red",
            (20, 45): "orange",
            (45, 80): "yellow",
            (80, 150): "green",
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
        # if base_color=='red':
        #     print(r,g,b,h,s,v)
        if v < 0.3:
            modifiers.append("dark")
        elif v > 0.8:
            modifiers.append("bright")
            
        if modifiers==['pale','bright'] and base_color=='red':
            return "pink"
        if (10 <= h <= 35) and (0.3 <= s <= 0.50) and (0.20 <= v <= 0.55):
            return 'brown'
        return f"{' '.join(modifiers)} {base_color}" if modifiers else base_color

    def get_piece_colors(self):
        """Get color names for each piece using tab20 colormap"""
        colors = {}
        for i in range(1, self.config.num_seeds + 1):
            rgb = self.color_mapping[i][:3]  # Get RGB values
            rgb = tuple(int(x * 1) for x in rgb)  # Convert to 0-255 range
            colors[i] = self.get_color_name(rgb)
        return colors

    def get_plot_level(self):
        """Determine the plot level based on grid size"""
        if self.config.grid_size <= 5:
            return "Easy"
        if self.config.grid_size <= 8:
            return "Medium"
        return "Hard"

    def generate_count_question(self, index: int) -> QAPair:
        """Generate a question about counting pieces on the board with detailed analysis"""
        unique_pieces = len(np.unique(self.grid[self.grid != 0]))
        piece_colors = self.get_piece_colors()
        
        # Generate options (same as before)
        options = list(range(max(0, unique_pieces - 4), unique_pieces + 5))
        while len(options) < 8:
            options.append(options[-1] + 1)
        random.shuffle(options)
        
        correct_answer = options.index(unique_pieces) + 1
        
        # Create detailed piece analysis
        piece_details = []
        for piece_id in range(1, self.config.num_seeds + 1):
            if piece_id not in self.removed_pieces:
                seed_x, seed_y = self.seeds[piece_id-1]
                piece_details.append(
                    f"Piece {piece_id} ({piece_colors[piece_id]}) around "
                    f"position ({seed_x}, {seed_y})"
                )
        
        removed_details = [
            f"Piece {piece_id}"
            for piece_id in self.removed_pieces
        ]
        
        analysis = (
            f"Let's analyze the puzzle state:\n\n"
            f"Pieces currently on the board:\n"
            f"{'; '.join(piece_details)}\n\n"
            f"Removed pieces:\n"
            f"{'; '.join(removed_details)}\n\n"
            f"By counting the unique non-zero numbers on the main board, "
            f"we can see there are {unique_pieces} pieces remaining. "
            f"Therefore, the answer is Option {correct_answer}."
        )
        
        # Rest of the question generation remains the same
        question = (
            "Rules:\n"
            "1. Each numbered region represents a piece on the board.\n"
            "2. Pieces are considered adjacent if they share at least one edge.\n"
            "3. Pieces that only touch at corners are not considered adjacent.\n"
            "4. Some pieces have been removed and are shown below the main board.\n"
            "\n"
            "Question:\n"
            "How many pieces are currently on the main board?\n"
            "\n"
            "Options:\n" + 
            "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options))
        )
        
        return QAPair(
            data_id=f"tengram-mcq-{index:05d}-piece_count",
            qa_type="Target Perception",
            question_id=1,
            question_description="piece_count",
            image=f"images/tengram-mcq-{index:05d}.png",
            state=f"states/tengram-mcq-{index:05d}.json",
            plot_level=self.get_plot_level(),
            qa_level="Easy",
            question=question,
            answer=correct_answer,
            analysis=analysis,
            options=[str(x) for x in options]
        )

    def save_state(self, output_path: str) -> None:
        """Save the puzzle state to a JSON file"""
        state = {
            'grid': self.grid.tolist(),
            'seeds': self.seeds,
            'removed_pieces': self.removed_pieces,
            'config': asdict(self.config)
        }
        
        with open(output_path, 'w') as f:
            json.dump(state, f, indent=2)

    rotation_descriptions = [
            "rotate 0 degrees",
            "rotate 90 degrees clockwise",
            "rotate 180 degrees",
            "rotate 90 degrees counterclockwise",
            "can't put inside (flipped)",
            "both rotate 0 and 180 degrees",
            "rotate 90 degrees by both direction",
            "no matter what degrees rotated, it always can fit"
        ]
    def rotations2description(self, rotations: List[int]) -> str:
        """Convert a list of rotations to a human-readable description"""
        if not rotations:
            return TengramGenerator.rotation_descriptions[4]
        if set(rotations) == {0, 180}:
            return TengramGenerator.rotation_descriptions[5]
        if set(rotations) == {90, 270}:
            return TengramGenerator.rotation_descriptions[6]
        if rotations == [0]:
            return TengramGenerator.rotation_descriptions[0]
        if rotations == [90]:
            return TengramGenerator.rotation_descriptions[1]
        if rotations == [180]:
            return TengramGenerator.rotation_descriptions[2]
        if rotations == [270]:
            return TengramGenerator.rotation_descriptions[3]
        return TengramGenerator.rotation_descriptions[7]

    def generate_rotation_question(self, index: int) -> QAPair:
        """Generate a question about rotating and fitting a removed piece"""
        # Ensure only one piece is removed
        self.config.num_pieces_to_remove = 1
        self.remove_random_pieces()
        removed_piece_id = self.removed_pieces[0]
        
        # Get the original piece shape
        original_piece = self.pieces[removed_piece_id-1].cells
        
        # Randomly decide whether to flip (20% chance)
        should_flip = random.random() < 0.2
        flipped_piece = flip_matrix(original_piece) if should_flip else original_piece
        
        # Randomly rotate the piece
        rotation_degrees = random.choice([0, 90, 180, 270])
        rotated_piece = rotate_matrix(flipped_piece, rotation_degrees)
        
        # Get the hole shape from the main board
        hole_shape, hole_dims, hole_pos = get_hole_shape(self.grid, removed_piece_id)
        
        self.pieces[removed_piece_id-1].cells = rotated_piece
        self.pieces[removed_piece_id-1].width = rotated_piece.shape[1]
        self.pieces[removed_piece_id-1].height = rotated_piece.shape[0]
        
        # Initialize valid rotations list
        valid_rotations = []
        
        # Check all possible rotations
        for deg in [0, 90, 180, 270]:
            test_piece = rotate_matrix(rotated_piece, deg)
            # print(hole_shape,test_piece)
            if check_piece_fit_with_details(hole_shape, test_piece)[0]:
                valid_rotations.append(deg)
        
        # Determine the correct answer based on valid rotations
        options = TengramGenerator.rotation_descriptions[:]
        random.shuffle(options)
        
        # Determine correct answer
        correct_answer = options.index(self.rotations2description(valid_rotations)) + 1
        
        # Generate analysis text
        hole_width, hole_height = hole_dims
        piece_width, piece_height = rotated_piece.shape
        analysis = get_detailed_rotation_analysis(self, hole_shape, rotated_piece, valid_rotations, hole_dims, removed_piece_id, hole_pos)
        analysis += f"\n\nSo, the correct answer is:  {self.rotations2description(valid_rotations)} which is Option {correct_answer}."
        
        question = (
            "Rules:\n"
            "1. Each numbered region represents a piece on the board.\n"
            "2. Pieces are considered adjacent if they share at least one edge.\n"
            "3. Pieces that only touch at corners are not considered adjacent.\n"
            "4. One piece is removed from main board and shown below. It has been rotated and may have been flipped.\n"
            "\n"
            "Question:\n"
            "Can the removed piece fit back into the main board by only rotation? If yes, what rotation(s) would work?\n"
            "\n"
            "Options:\n" + 
            "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options))
        )
        
        return QAPair(
            data_id=f"tengram-mcq-{index:05d}-rotation",
            qa_type="State Prediction",
            question_id=2,
            question_description="piece_rotation",
            image=f"images/tengram-mcq-{index:05d}.png",
            state=f"states/tengram-mcq-{index:05d}.json",
            plot_level=self.get_plot_level(),
            qa_level="Medium",
            question=question,
            answer=correct_answer,
            analysis=analysis,
            options=options
        )

    def get_piece_area(self, piece_id: int) -> int:
        """Calculate the area (number of cells) of a specific piece.
        
        Args:
            piece_id (int): The ID of the piece to calculate area for
            
        Returns:
            int: The area of the piece in grid cells
        """
        return np.sum(self.grid == piece_id)

    def get_adjacent_pieces(self, piece_id: int) -> List[int]:
        """Find all pieces that share at least one edge with the given piece.
        
        Args:
            piece_id (int): The ID of the piece to find adjacencies for
            
        Returns:
            List[int]: List of piece IDs that are adjacent to the given piece
        """
        # Create a mask for the current piece
        piece_mask = self.grid == piece_id
        
        # Create shifted masks in all four directions
        shifts = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # right, left, down, up
        adjacent_pieces = set()
        
        for dx, dy in shifts:
            # Create shifted mask
            shifted = np.zeros_like(self.grid)
            if dx > 0:
                shifted[:-dx, :] = piece_mask[dx:, :]
            elif dx < 0:
                shifted[-dx:, :] = piece_mask[:dx, :]
            elif dy > 0:
                shifted[:, :-dy] = piece_mask[:, dy:]
            else:  # dy < 0
                shifted[:, -dy:] = piece_mask[:, :dy]
            
            # Find pieces that overlap with shifted mask
            neighbor_ids = np.unique(self.grid[shifted > 0])
            
            # Add to set of adjacent pieces, excluding 0 (empty) and the piece itself
            adjacent_pieces.update(
                id for id in neighbor_ids 
                if id != 0 and id != piece_id
            )
        
        return sorted(list(adjacent_pieces))

    def get_border_segments(self, piece_id: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get all border segments of a piece.
        Each segment is represented by two cells forming the border.
        Returns List of ((x1,y1), (x2,y2)) where (x,y) are cell coordinates."""
        piece_mask = (self.grid == piece_id)
        segments = []
        
        # Check horizontal segments
        for i in range(piece_mask.shape[0]):
            for j in range(piece_mask.shape[1]-1):
                if piece_mask[i,j] != piece_mask[i,j+1]:
                    segments.append(((i,j), (i,j+1)))
                    
        # Check vertical segments
        for i in range(piece_mask.shape[0]-1):
            for j in range(piece_mask.shape[1]):
                if piece_mask[i,j] != piece_mask[i+1,j]:
                    segments.append(((i,j), (i+1,j)))
                    
        return segments

    def analyze_border_segment(self, segment: Tuple[Tuple[int, int], Tuple[int, int]], piece_id: int) -> Tuple[int, str]:
        """Analyze a border segment to determine what's on the other side.
        Returns (adjacent_piece_id, direction) or (0, direction) if empty space."""
        (x1,y1), (x2,y2) = segment
        
        # Determine if segment is horizontal or vertical
        is_horizontal = y1 == y2
        
        # For horizontal segments, check cells above and below
        if is_horizontal:
            if self.grid[x1,y1] == piece_id:
                # Check cell below segment
                if x1 < self.grid.shape[0]-1:
                    return (self.grid[x1+1,y1], "below")
            else:
                # Check cell above segment
                return (self.grid[x1,y1], "above")
                    
        # For vertical segments, check cells left and right
        else:
            if self.grid[x1,y1] == piece_id:
                # Check cell to right of segment
                if y1 < self.grid.shape[1]-1:
                    return (self.grid[x1,y1+1], "right")
            else:
                # Check cell to left of segment
                return (self.grid[x1,y1], "left")
                    
        return (0, "edge of board")

    def analyze_cell_adjacencies(self, piece_id: int) -> List[Tuple[Tuple[int, int], List[Tuple[int, str, int]]]]:
        """Analyze adjacencies for each cell of a piece.
        Returns list of (cell_coords, list of (direction, adjacent_piece))"""
        piece_cells = list(zip(*np.where(self.grid == piece_id)))
        cell_analysis = []
        
        directions = [
            ('up', (-1, 0)),
            ('down', (1, 0)),
            ('left', (0, -1)),
            ('right', (0, 1))
        ]
        
        for cell in piece_cells:
            adjacencies = []
            for dir_name, (dx, dy) in directions:
                new_x, new_y = cell[0] + dx, cell[1] + dy
                if (0 <= new_x < self.grid.shape[0] and 
                    0 <= new_y < self.grid.shape[1]):
                    adj_value = self.grid[new_x, new_y]
                    if adj_value not in (0, piece_id):
                        adjacencies.append((dir_name, new_x, new_y, adj_value))
            cell_analysis.append((cell, adjacencies))
            
        return cell_analysis

    def generate_adjacency_question(self, index: int) -> QAPair:
        """Generate a question about piece adjacencies with cell-based analysis."""
        active_pieces = sorted(list(set(np.unique(self.grid)) - {0}))
        
        if len(active_pieces) < 2:
            return self.generate_count_question(index)
            
        target_piece = random.choice(active_pieces)
        piece_colors = self.get_piece_colors()

        # Get cell-by-cell adjacency analysis
        cell_analysis = self.analyze_cell_adjacencies(target_piece)
        
        # Track adjacent pieces and their contact points
        adjacent_info = {}
        
        # Generate detailed analysis text
        cell_details = []
        for (cell_x, cell_y), adjacencies in cell_analysis:
            if adjacencies:
                cell_text = [f"Cell ({cell_x},{cell_y}):"]
                for dir_name, adj_x, adj_y, adj_piece in adjacencies:
                    cell_text.append(
                        f"   - {dir_name}: Piece {adj_piece} "
                        f"({piece_colors[adj_piece]}) at ({adj_x},{adj_y})"
                    )
                    adjacent_info[adj_piece] = adjacent_info.get(adj_piece, 0) + 1
                cell_details.append("\n".join(cell_text))
            else:
                cell_details.append(
                    f"Cell ({cell_x},{cell_y}): No adjacent pieces"
                )

        adjacent_pieces = list(adjacent_info.keys())
        correct_count = len(adjacent_pieces)

        # Generate options
        options = list(range(max(0, correct_count - 4), min(len(active_pieces), correct_count + 3)))
        while len(options) < 8:
            next_val = options[-1] + 1
            options.append(next_val)
        random.shuffle(options)
        
        correct_answer = options.index(correct_count) + 1

        # Get piece boundaries
        piece_mask = self.grid == target_piece
        rows, cols = np.where(piece_mask)
        min_row, max_row = np.min(rows), np.max(rows)
        min_col, max_col = np.min(cols), np.max(cols)

        # Generate analysis
        analysis = (
            f"Let's analyze Piece {target_piece} "
            f"({piece_colors[target_piece]}):\n\n"
            f"Piece Boundaries:\n"
            f"- Spans rows {min_row} to {max_row} (height: {max_row - min_row + 1})\n"
            f"- Spans columns {min_col} to {max_col} (width: {max_col - min_col + 1})\n\n"
            "1. Cell-by-cell examination:\n" +
            "\n".join(cell_details) +
            "\n\n2. Adjacent Pieces Summary:\n" +
            "\n".join(
                f"- Piece {pid} ({piece_colors[pid]}): {count} contact sides"
                for pid, count in adjacent_info.items()
            ) +
            f"\n\nTotal number of unique adjacent pieces: {correct_count}\n"
            f"Therefore, the answer is Option {correct_answer}."
        )

        # ...rest of question generation remains the same...
        question = (
            "Rules:\n"
            "1. Each numbered region represents a piece on the board.\n"
            "2. Pieces are considered adjacent if they share at least one edge.\n"
            "3. Pieces that only touch at corners are not considered adjacent.\n"
            "\n"
            f"Question:\n"
            f"How many different pieces are adjacent to Piece {target_piece}?\n"
            "\n"
            "Options:\n" + 
            "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options))
        )
        
        return QAPair(
            data_id=f"tengram-mcq-{index:05d}-adjacency",
            qa_type="Target Perception",
            question_id=4,
            question_description="piece_adjacency",
            image=f"images/tengram-mcq-{index:05d}.png",
            state=f"states/tengram-mcq-{index:05d}.json",
            plot_level=self.get_plot_level(),
            qa_level="Medium",
            question=question,
            answer=correct_answer,
            analysis=analysis,
            options=[str(x) for x in options]
        )

    def generate_area_question(self, index: int) -> QAPair:
        """Generate a question about a specific piece's area.
        
        Args:
            index (int): Index for the question ID
            
        Returns:
            QAPair: Question and answer pair about piece area
        """
        # Get all pieces currently on the board
        active_pieces = sorted(list(set(np.unique(self.grid)) - {0}))
        if not active_pieces:
            return self.generate_count_question(index)
            
        # Randomly choose a piece to analyze
        target_piece = random.choice(active_pieces)
        piece_colors = self.get_piece_colors()
        
        # Analyze the piece's shape row by row
        piece_mask = self.grid == target_piece
        rows, cols = np.where(piece_mask)
        if len(rows) == 0:
            return self.generate_count_question(index)
            
        min_row, max_row = np.min(rows), np.max(rows)
        min_col, max_col = np.min(cols), np.max(cols)
        
        # Count cells in each row
        row_counts = []
        for row in range(min_row, max_row + 1):
            row_cols = cols[rows == row]
            if len(row_cols) > 0:
                row_counts.append((row, np.min(row_cols), np.max(row_cols), len(row_cols)))
        
        target_area = sum(count for _, _, _, count in row_counts)
        
        # Generate options
        possible_areas = list(range(max(1, target_area - 6), target_area + 6))
        options = random.sample(possible_areas, min(8, len(possible_areas)))
        if target_area not in options:
            options[0] = target_area
        options = sorted(options)
        
        correct_answer = options.index(target_area) + 1
        
        # Generate detailed analysis
        analysis = (
            f"Let's analyze Piece {target_piece} ({piece_colors[target_piece]}) row by row:\n\n"
            f"The piece spans from row {min_row} to {max_row} "
            f"(height of {max_row - min_row + 1}):\n\n"
        )
        
        running_sum = 0
        for row, start_col, end_col, count in row_counts:
            running_sum += count
            analysis += (
                f"Row {row }: {count} cells from column {start_col } to {end_col } "
                f"(Running sum: {running_sum})\n"
            )
        
        analysis += (
            f"\nAdding up all the cells: {' + '.join(str(count) for _, _, _, count in row_counts)} "
            f"= {target_area} cells\n"
            f"Therefore, the answer is Option {correct_answer}."
        )
        
        question = (
            "Rules:\n"
            "1. Each numbered region represents a piece on the board.\n"
            "2. Pieces are considered adjacent if they share at least one edge.\n"
            "3. Pieces that only touch at corners are not considered adjacent.\n"
            "4. A piece's area is the number of cells it contains.\n"
            "\n"
            f"Question:\n"
            f"What is the area (number of cells) of Piece {target_piece}?\n"
            "\n"
            "Options:\n" + 
            "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options))
        )
        return QAPair(
            data_id=f"tengram-mcq-{index:05d}-piece_area",
            qa_type="Target Perception",
            question_id=3,
            question_description="piece_area",
            image=f"images/tengram-mcq-{index:05d}.png",
            state=f"states/tengram-mcq-{index:05d}.json",
            plot_level=self.get_plot_level(),
            qa_level="Medium",
            question=question,
            answer=correct_answer,
            analysis=analysis,
            options=[str(x) for x in options])
        
    def generate_neighbor_pieces(self) -> Tuple[int, int]:
        """Find and remove two neighboring pieces."""
        active_pieces = sorted(list(set(np.unique(self.grid)) - {0}))
        for piece_id in active_pieces:
            neighbors = self.get_adjacent_pieces(piece_id)
            if neighbors:
                return int(piece_id), int(random.choice(neighbors))
        return None, None

    def generate_placement_question(self, index: int) -> QAPair:
        """Generate a question about placing one of two removed neighboring pieces."""
        piece1, piece2 = self.generate_neighbor_pieces()
        if not piece1 or not piece2:
            return self.generate_count_question(index)

        self.removed_pieces = [piece1, piece2]
        self.grid[self.grid == piece1] = 0
        self.grid[self.grid == piece2] = 0

        piece1_shape = self.pieces[piece1-1].cells
        piece2_shape = self.pieces[piece2-1].cells
        
        if np.array_equal(piece1_shape, piece2_shape):
            return self.generate_count_question(index)

        hole_shape, hole_dims, hole_pos = get_hole_shape(self.grid, piece1)
        hole_height, hole_width = hole_dims
        min_row, min_col = hole_pos

        piece1_height, piece1_width = piece1_shape.shape
        piece2_height, piece2_width = piece2_shape.shape

        def crop_hole(hole: np.ndarray) -> np.ndarray:
            """Crop hole by removing full 0 rows and columns from edges"""
            # Find non-zero rows and columns
            non_zero_rows = np.where(np.any(hole != 0, axis=1))[0]
            non_zero_cols = np.where(np.any(hole != 0, axis=0))[0]
            
            if len(non_zero_rows) == 0 or len(non_zero_cols) == 0:
                return np.zeros((0, 0), dtype=int)
                
            # Crop to minimum size
            return hole[non_zero_rows[0]:non_zero_rows[-1]+1,
                      non_zero_cols[0]:non_zero_cols[-1]+1]

        def check_piece_at_corner(hole_shape, piece_shape, corner, piece_offset=0):
            """Check if piece fits at a specific corner and return details about any mismatch"""
            hole_h, hole_w = hole_shape.shape
            piece_h, piece_w = piece_shape.shape
            
            if piece_h > hole_h or piece_w > hole_w:
                return False, f"Piece dimensions ({piece_h}x{piece_w}) exceed hole dimensions ({hole_h}x{hole_w})"
            
            if corner == 'upper-left':
                region = hole_shape[:piece_h, :piece_w]
                offset_row, offset_col = 0, 0
            elif corner == 'upper-right':
                region = hole_shape[:piece_h, -piece_w:]
                offset_row, offset_col = 0, hole_w - piece_w
            elif corner == 'bottom-left':
                region = hole_shape[-piece_h:, :piece_w]
                offset_row, offset_col = hole_h - piece_h, 0
            else:  # bottom-right
                region = hole_shape[-piece_h:, -piece_w:]
                offset_row, offset_col = hole_h - piece_h, hole_w - piece_w

            # Check each cell where piece has content
            for i in range(piece_h):
                for j in range(piece_w):
                    if piece_shape[i, j] > 0 and region[i, j] == 0:
                        board_row = i + offset_row + min_row
                        board_col = j + offset_col + min_col
                        return False, f"Cell ({i},{j+piece_offset}) on Removed Pieces plot maps to board position ({board_row},{board_col}) which isn't empty"
            
            return True, None

        def get_piece_area_coords(corner, hole_h, hole_w, piece_h, piece_w):
            """Get the coordinates of where a piece would be placed in a given corner"""
            if corner == 'upper-left':
                return (0 + min_row, 0 + min_col, piece_h-1 + min_row, piece_w-1 + min_col)
            elif corner == 'upper-right':
                return (0 + min_row, hole_w-piece_w + min_col, piece_h-1 + min_row, hole_w-1 + min_col)
            elif corner == 'bottom-left':
                return (hole_h-piece_h + min_row, 0 + min_col, hole_h-1 + min_row, piece_w-1 + min_col)
            else:  # bottom-right
                return (hole_h-piece_h + min_row, hole_w-piece_w + min_col, hole_h-1 + min_row, hole_w-1 + min_col)

        corners = ['upper-left', 'upper-right', 'bottom-left', 'bottom-right']
        valid_corners = []
        corner_analysis = []
        
        for corner in corners:
            if corner=='upper-right' and piece1_width==hole_width:
                corner_analysis.append(
                    f"- {corner}: Since Piece {piece1} has the same width as the hole, upper-right corner is same as upper-left corner. Skipped."
                )
                continue
            if corner=='bottom-right' and piece1_width==hole_width:
                corner_analysis.append(
                    f"- {corner}: Since Piece {piece1} has the same width as the hole, bottom-right corner is same as bottom-left corner. Skipped."
                )
                continue
            if corner=='bottom-left' and piece1_height==hole_height:
                corner_analysis.append(
                    f"- {corner}: Since Piece {piece1} has the same height as the hole, bottom-left corner is same as upper-left corner. Skipped."
                )
                continue
            if corner=='bottom-right' and piece1_height==hole_height:
                corner_analysis.append(
                    f"- {corner}: Since Piece {piece1} has the same height as the hole, bottom-right corner is same as upper-right corner. Skipped."
                )
                continue
            
            
            fits, message = check_piece_at_corner(hole_shape, piece1_shape, corner)
            area1 = get_piece_area_coords(corner, hole_height, hole_width, 
                                        piece1_height, piece1_width)
            piece1_area_str = f"({area1[0]},{area1[1]}) to ({area1[2]},{area1[3]})"
            
            if fits:
                # Create remaining hole by only zeroing out cells where piece1 has content
                remaining_hole = hole_shape.copy()
                if corner == 'upper-left':
                    mask = (piece1_shape > 0)
                    remaining_hole[:piece1_height, :piece1_width][mask] = 0
                elif corner == 'upper-right':
                    mask = (piece1_shape > 0)
                    remaining_hole[:piece1_height, -piece1_width:][mask] = 0
                elif corner == 'bottom-left':
                    mask = (piece1_shape > 0)
                    remaining_hole[-piece1_height:, :piece1_width][mask] = 0
                elif corner == 'bottom-right':
                    mask = (piece1_shape > 0)
                    remaining_hole[-piece1_height:, -piece1_width:][mask] = 0
                
                remaining_hole = crop_hole(remaining_hole)
                corner_analysis.append(
                    f"- {corner}: Attempting to place Piece {piece1} at {piece1_area_str}\n"
                    f"  Success! Remaining hole dimensions: {remaining_hole.shape[0]}x{remaining_hole.shape[1]}"
                )
                if remaining_hole.shape[0] == piece2_height and remaining_hole.shape[1] == piece2_width:
                    area2 = get_piece_area_coords(corner, *remaining_hole.shape, 
                                                piece2_height, piece2_width)
                    piece2_area_str = f"({area2[0]},{area2[1]}) to ({area2[2]},{area2[3]})"
                    # Try to fit piece2 in the remaining space
                    fits2, message2 = check_piece_at_corner(remaining_hole, piece2_shape, corner, piece1_width+1)
                    corner_analysis.append(
                        f"  Then placing Piece {piece2} at {piece2_area_str}"
                    )
                    if fits2:
                        valid_corners.append(corner)
                        corner_analysis.append(
                            f"  Both pieces fit perfectly!"
                        )
                    else:
                        corner_analysis.append(
                            f"  But Piece {piece2} fails: {message2}"
                        )
                else:
                    corner_analysis.append(
                        f"  But the remaining hole is not the right size for Piece {piece2}: {piece2_height}x{piece2_width}, so it fails"
                    )
            else:
                corner_analysis.append(
                    f"- {corner}: Attempting to place Piece {piece1} at {piece1_area_str}\n"
                    f"  Failed: {message}"
                )

        # Generate coordinate-based options
        valid_positions = set()
        position_details = {}
        
        # Get valid positions from successful placements
        for corner in valid_corners:
            area = get_piece_area_coords(corner, hole_height, hole_width, 
                                       piece1_height, piece1_width)
            pos_str = f"({area[0]},{area[1]}) to ({area[2]},{area[3]})"
            valid_positions.add(pos_str)
            position_details[pos_str] = corner

        # Generate wrong answers by slightly shifting coordinates
        def generate_wrong_position():
            # Randomly shift the starting position
            start_row = random.randint(max(0, min_row-2), min_row+hole_height-piece1_height)
            start_col = random.randint(max(0, min_col-2), min_col+hole_width-piece1_width)
            end_row = start_row + piece1_height - 1
            end_col = start_col + piece1_width - 1
            return f"({start_row},{start_col}) to ({end_row},{end_col})"

        # Create list of options
        options = list(valid_positions)
        if not options:
            return self.generate_count_question(index)
        cnt=0
        while len(options) < 8 and cnt<100:
            cnt+=1
            wrong_pos = generate_wrong_position()
            if wrong_pos not in options:
                options.append(wrong_pos)
        
        random.shuffle(options)
        
        # Update corner_analysis to reference positions instead of directions
        updated_corner_analysis = []
        for analysis in corner_analysis:
            # for pos, corner_name in position_details.items():
            #     if corner_name in analysis:
            #         analysis = analysis.replace(f"- {corner_name}:", f"- Position {pos}:")
            updated_corner_analysis.append(analysis)
        
        correct_answer = options.index(list(valid_positions)[0]) + 1

        analysis = (
            f"Let's analyze the placement of Piece {piece1} and Piece {piece2}:\n\n"
            f"1. Hole dimensions: {hole_height}x{hole_width}\n"
            f"2. Piece {piece1} dimensions: {piece1_height}x{piece1_width}\n"
            f"3. Piece {piece2} dimensions: {piece2_height}x{piece2_width}\n\n"
            "We know that if Piece 1 fits, then it must be placed at one of the four corners.\n"
            f"Testing each corner:\n"
            + "\n".join(updated_corner_analysis) +
            f"\n\nTherefore, Piece {piece1} should be placed at position {list(valid_positions)[0]} as shown in Option {correct_answer}."
            
        )

        question = (
            "Rules:\n"
            "1. Each numbered region represents a piece on the board.\n"
            "2. Pieces are considered adjacent if they share at least one edge.\n"
            "3. Pieces that only touch at corners are not considered adjacent.\n"
            "4. Two adjacent pieces have been removed from the board.\n"
            "5. A valid placement is one where both pieces fit into the hole without overlapping.\n"
            "\n"
            "Question:\n"
            f"At which position should Piece {piece1} be placed? Each option shows (top_row,left_col) to (bottom_row,right_col).\n"
            "\n"
            "Options:\n" + 
            "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options))
        )

        return QAPair(
            data_id=f"tengram-mcq-{index:05d}-placement",
            qa_type="State Prediction",
            question_id=5,
            question_description="piece_placement",
            image=f"images/tengram-mcq-{index:05d}.png",
            state=f"states/tengram-mcq-{index:05d}.json",
            plot_level=self.get_plot_level(),
            qa_level="Hard",
            question=question,
            answer=correct_answer,
            analysis=analysis,
            options=options
        )

def rotate_matrix(matrix: np.ndarray, degrees: int) -> np.ndarray:
    """Rotate a matrix by specified degrees (0, 90, 180, 270)"""
    k = (degrees % 360) // 90  # Number of 90-degree rotations
    return np.rot90(matrix, k=(-k))  # Negative k for clockwise rotation

def flip_matrix(matrix: np.ndarray, horizontal: bool = True) -> np.ndarray:
    """Flip a matrix horizontally or vertically"""
    if horizontal:
        return np.fliplr(matrix)
    return np.flipud(matrix)

def get_hole_shape(grid: np.ndarray, piece_id: int) -> Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]]:
    """Get the hole shape and its bounding box from the grid"""
    hole_mask = (grid == 0)
    if not np.any(hole_mask):
        return None, (0, 0), (0, 0)
    
    # Find bounding box of the hole
    rows, cols = np.where(hole_mask)
    if len(rows) == 0:
        return None, (0, 0), (0, 0)
    
    min_row, max_row = np.min(rows), np.max(rows)
    min_col, max_col = np.min(cols), np.max(cols)
    
    # Extract the hole region
    hole_shape = hole_mask[min_row:max_row+1, min_col:max_col+1]
    return hole_shape, (max_row - min_row + 1, max_col - min_col + 1), (min_row, min_col)

def check_piece_fit_with_details(hole_shape: np.ndarray, piece_shape: np.ndarray) -> Tuple[bool, Tuple[int, int]]:
    """
    Check if a piece fits in the hole and return the first mismatching cell if any
    
    Returns:
        Tuple[bool, Optional[Tuple[int, int]]]: (fits, first_mismatch_position)
    """
    if hole_shape.shape != piece_shape.shape:
        return False, None
        
    for i in range(hole_shape.shape[0]):
        for j in range(hole_shape.shape[1]):
            if (piece_shape[i,j] > 0) != (hole_shape[i,j] > 0):
                return False, (i, j)
                
    return True, None

def analyze_rotation_possibilities(hole_dims: Tuple[int, int], piece_dims: Tuple[int, int]) -> List[int]:
    """
    Analyze which rotations are possible based on dimensions alone
    
    Returns:
        List[int]: List of possible rotation angles (0, 90, 180, 270)
    """
    hole_height, hole_width = hole_dims
    piece_height, piece_width = piece_dims
    
    possible_rotations = []
    
    # Check 0° and 180° rotations
    if hole_height == piece_height and hole_width == piece_width:
        possible_rotations.extend([0, 180])
        
    # Check 90° and 270° rotations
    if hole_height == piece_width and hole_width == piece_height:
        possible_rotations.extend([90, 270])
        
    return sorted(possible_rotations)

def get_detailed_rotation_analysis(generator: TengramGenerator, hole_shape: np.ndarray, 
    rotated_piece: np.ndarray, valid_rotations: List[int], 
    hole_dims: Tuple[int, int], removed_piece_id: int, hole_pos: Tuple[int, int]) -> str:
    """Generate detailed analysis of rotation attempts"""
    piece_colors = generator.get_piece_colors()
    piece_color = piece_colors[removed_piece_id]
    
    analysis_parts = [
        f"Let's analyze how piece {removed_piece_id} can be rotated to fit the hole:\n"
    ]
    
    # Dimension analysis
    hole_height, hole_width = hole_dims
    piece_height, piece_width = rotated_piece.shape
    
    analysis_parts.append(
        f"\n1. Dimension Analysis:\n"
        f"   - Hole dimensions: {hole_height}x{hole_width}\n"
        f"   - Piece dimensions: {piece_height}x{piece_width}\n"
    )
    
    # Get theoretically possible rotations based on dimensions
    possible_rotations = analyze_rotation_possibilities((hole_height, hole_width), 
                                                      (piece_height, piece_width))
    
    if not possible_rotations:
        analysis_parts.append(
            "   - Based on dimensions alone, no rotation can make this piece fit!\n"
        )
    else:
        analysis_parts.append(
            f"   - Based on dimensions, these rotations (clockwise) might work: {possible_rotations}\n"
        )
    
    # Detailed rotation analysis
    analysis_parts.append("\n2. Testing Each Rotation:")
    
    for deg in [0, 90, 180, 270]:
        test_piece = rotate_matrix(rotated_piece, deg)
        fits, mismatch_pos = check_piece_fit_with_details(hole_shape, test_piece)
        
        if deg not in possible_rotations:
            ...
            # analysis_parts.append(
            #     f"\n   {deg}° rotation:"
            #     f"\n   - Skipped: Dimensions after rotation ({test_piece.shape}) "
            #     f"wouldn't match hole ({hole_shape.shape})"
            # )
        elif fits:
            analysis_parts.append(
                f"\n   {deg}° rotation:"
                f"\n   - Success! Piece fits perfectly"
            )
        else:
            original_pos=mismatch_pos
            if deg==270:
                original_pos=(mismatch_pos[1],piece_width-1-mismatch_pos[0])
            elif deg==180:
                original_pos=(piece_height-1-mismatch_pos[0],piece_width-1-mismatch_pos[1])
            elif deg==90:
                original_pos=(piece_height-1-mismatch_pos[1],mismatch_pos[0])
                
            analysis_parts.append(
                f"\n   {deg}° rotation:"
                f"\n   - Failed: First mismatch at row {mismatch_pos[0]}, column {mismatch_pos[1]} (mapped to ({original_pos[0]},{original_pos[1]}) of removed piece and ({hole_pos[0]+mismatch_pos[0]},{hole_pos[1]+mismatch_pos[1]}) of board)"
                f"\n   - At this position, the hole "
                f"{'was empty' if hole_shape[mismatch_pos] else 'was filled'} "
                f"but the piece {'was present' if test_piece[mismatch_pos] else 'was absent'}"
            )
    
    # Summary
    analysis_parts.append(
        f"\n3. Summary:\n"
        f"   - Valid rotations found: {valid_rotations}\n"
        f"   - {'Some' if valid_rotations else 'No'} rotations work"
    )
    
    return "\n".join(analysis_parts)

def generate_dataset(num_puzzles: int, output_dir: str = 'tengram_dataset') -> None:
    """Generate multiple puzzles and save them to a dataset"""
    os.makedirs(f"{output_dir}/images", exist_ok=True)
    os.makedirs(f"{output_dir}/states", exist_ok=True)
    
    dataset = []
    
    for i in range(num_puzzles):
        # Randomly choose configuration
        config = PuzzleConfig(
            grid_size=random.randint(5, 10),
            num_seeds=random.randint(4, 8),
            num_pieces_to_remove=random.randint(1, 3)
        )
        
        # Generate puzzle
        generator = TengramGenerator(config)
        generator.generate_seeds()
        generator.assign_cells_to_seeds()
        
        # Randomly choose question type
        question_type = random.choice([
            'counting',
            'rotation',
            'area',
            'adjacency',
            'placement'  # Add new question type
        ])
        
        if question_type == 'counting':
            generator.remove_random_pieces()
            qa_pair = generator.generate_count_question(i)
        elif question_type == 'rotation':
            qa_pair = generator.generate_rotation_question(i)
        elif question_type == 'area':
            generator.remove_random_pieces()
            qa_pair = generator.generate_area_question(i)
        elif question_type == 'adjacency':
            generator.remove_random_pieces()
            qa_pair = generator.generate_adjacency_question(i)
        else:  # placement
            qa_pair = generator.generate_placement_question(i)
        
        # Save visualization and state
        generator.plot_puzzle(f"{output_dir}/images/tengram-mcq-{i:05d}.png")
        generator.save_state(f"{output_dir}/states/tengram-mcq-{i:05d}.json")
        
        dataset.append(asdict(qa_pair))
    
    # Save dataset
    with open(f"{output_dir}/data.json", 'w') as f:
        json.dump(dataset, f, indent=2)
    
if __name__ == "__main__":
    generate_dataset(num_puzzles=500)
