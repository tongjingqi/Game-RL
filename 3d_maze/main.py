import json
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict, Set, Optional
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

@dataclass(frozen=True)  # Make the class immutable
class Position:
    x: int
    y: int
    z: int
    
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def __hash__(self):
        return hash((self.x, self.y, self.z))
    
    def to_tuple(self):
        return (self.x, self.y, self.z)

@dataclass
class PathSegment:
    start: Position
    end: Position
    type: str  # 'walk' or 'ladder'

@dataclass
class Ladder:
    base_pos: Position
    direction: str
    height: int

@dataclass
class Branch:
    pos: Position
    branch_id: int
    paths: Dict[str, List[PathSegment]] # 'A' for main path, 'B' for alternative

@dataclass
class BasePuzzleState:
    grid_size: Tuple[int, int, int]
    cubes: Set[Position]
    start_pos: Position
    goal_pos: Position
    ladders: List[Ladder]
    path: List[PathSegment]

@dataclass
class PathFindingState(BasePuzzleState):
    branches: List[Branch]
    all_paths: List[PathSegment]

@dataclass
class SequencePoint:
    pos: Position
    label: int
    
@dataclass
class SequenceState(BasePuzzleState):
    sequence_points: List[SequencePoint]
    
def create_cube_verts(pos: Position, cubes: Set[Position]):
    """Create vertices for a cube at given position, omitting hidden faces"""
    x, y, z = pos.x, pos.y, pos.z
    verts = []
    
    # # Only add bottom face if there's no cube below
    # if Position(x, y, z-1) not in cubes:
    #     verts.append([(x, y, z), (x+1, y, z), (x+1, y+1, z), (x, y+1, z)])
    
    # Only add top face if there's no cube above
    if Position(x, y, z+1) not in cubes:
        verts.append([(x, y, z+1), (x+1, y, z+1), (x+1, y+1, z+1), (x, y+1, z+1)])
    
    # # Only add left face if there's no cube to the left
    # if Position(x-1, y, z) not in cubes:
    #     verts.append([(x, y, z), (x, y+1, z), (x, y+1, z+1), (x, y, z+1)])
    
    # Only add right face if there's no cube to the right
    if Position(x+1, y, z) not in cubes:
        verts.append([(x+1, y, z), (x+1, y+1, z), (x+1, y+1, z+1), (x+1, y, z+1)])
    
    # # Only add front face if there's no cube in front
    # if Position(x, y-1, z) not in cubes:
    #     verts.append([(x, y, z), (x+1, y, z), (x+1, y, z+1), (x, y, z+1)])
    
    # Only add back face if there's no cube behind
    if Position(x, y+1, z) not in cubes:
        verts.append([(x, y+1, z), (x+1, y+1, z), (x+1, y+1, z+1), (x, y+1, z+1)])
    
    return verts

def draw_ladder(ax, ladder: Ladder, zorder=3):
    base = ladder.base_pos
    height = ladder.height
    
    if ladder.direction == '+x':
        x, y, z = base.x + 0.5, base.y, base.z + 0.5
        ax.plot([x, x], [y, y], [z, z + height], 'k-', linewidth=3, zorder=zorder)
        ax.plot([x, x], [y + 0.2, y + 0.2], [z, z + height], 'k-', linewidth=3, zorder=zorder)
        for h in np.linspace(z, z + height, 6):
            ax.plot([x, x], [y, y + 0.2], [h, h], 'k-', linewidth=2, zorder=zorder)

def draw_puzzle(puzzle, filename: str):
    """
    Universal drawing function that handles both regular puzzles and sequence puzzles.
    Works with both PuzzleState and VisitSequenceState.
    """
    # Create figure with tight layout and no extra padding
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Common view and styling settings
    ax.view_init(elev=25, azim=30)
    ax.grid(False)
    ax.set_facecolor('white')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_axis_off()
    
    margin = 0.5
    ax.set_xlim(-margin, puzzle.grid_size[0] + margin)
    ax.set_ylim(-margin, puzzle.grid_size[1] + margin)
    ax.set_zlim(-margin, puzzle.grid_size[2] + margin)
    
    # Draw base grid with lowest z-order
    x = np.arange(-margin, puzzle.grid_size[0] + margin, 1)
    y = np.arange(-margin, puzzle.grid_size[1] + margin, 1)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    ax.plot_surface(X, Y, Z, alpha=0.1, color='gray', zorder=1)
    
    # Sort cubes by distance from camera view for proper transparency
    camera_pos = np.array([puzzle.grid_size[0] + 2, puzzle.grid_size[1] + 2, puzzle.grid_size[2] + 2])
    sorted_cubes = sorted(
        puzzle.cubes,
        key=lambda pos: -np.linalg.norm(
            np.array([pos.x, pos.y, pos.z]) - camera_pos
        )
    )
    
    # First pass: Draw opaque faces
    for cube_pos in sorted_cubes:
        verts = create_cube_verts(cube_pos, puzzle.cubes)
        
        alpha = 0.8
        
        # Determine cube color based on type
        if cube_pos == puzzle.start_pos:
            color = '#4444FF'
        elif cube_pos == puzzle.goal_pos:
            color = '#FF4444'
        elif hasattr(puzzle, 'sequence_points') and any(sp.pos == cube_pos for sp in puzzle.sequence_points):
            color = '#44FF44'
        elif hasattr(puzzle, 'branches') and any(b.pos == cube_pos for b in puzzle.branches):
            color = '#44FF44'
        else:
            color = '#888888'
        
        pc = Poly3DCollection(verts, alpha=alpha, zorder=2)
        pc.set_facecolor(color)
        pc.set_edgecolor('black')
        pc.set_linewidth(1.0)
        ax.add_collection3d(pc)
    
    # Draw ladders with higher z-order
    for ladder in puzzle.ladders:
        draw_ladder(ax, ladder, zorder=300)
    
    # Draw sequence point numbers or branch numbers with highest z-order
    if hasattr(puzzle, 'sequence_points'):
        for sp in puzzle.sequence_points:
            draw_number(ax, sp.pos, sp.label, zorder=400)
    
    if hasattr(puzzle, 'branches'):
        for branch in puzzle.branches:
            draw_number(ax, branch.pos, branch.branch_id, zorder=400)
    
    # Set axis limits
    ax.set_xlim(0, puzzle.grid_size[0])
    ax.set_ylim(0, puzzle.grid_size[1])
    ax.set_zlim(0, puzzle.grid_size[2])
    
    # Remove extra white space
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    
    # Save with tight bbox and transparent background
    plt.savefig(filename, bbox_inches='tight', pad_inches=-0.3, facecolor='white')
    plt.close()
    
def draw_number(ax, pos: Position, number: int, zorder=4):
    """Helper function to draw numbers with white outline for better visibility"""
    # Draw white outline/background
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
        ax.text(pos.x + 0.5 + dx*0.01, 
                pos.y + 0.5 + dy*0.01, 
                pos.z + 1.1,
                str(number), 
                size=24, 
                ha='center', 
                va='center',
                weight='bold', 
                color='white', zorder=zorder)
    
    # Draw main text in black
    ax.text(pos.x + 0.5, 
            pos.y + 0.5, 
            pos.z + 1.1,
            str(number), 
            size=24, 
            ha='center', 
            va='center',
            weight='bold', 
            color='black', zorder=zorder)  


def get_adjacent_positions(pos: Position) -> Set[Position]:
    """Get all positions adjacent to the given position"""
    adjacent = set()
    for dx, dy, dz in [(x, y, z) for x in [-1,0,1] for y in [-1,0,1] for z in [-1,0,1]]:
        if dx == dy == dz == 0:
            continue
        adjacent.add(Position(pos.x + dx, pos.y + dy, pos.z + dz))
    return adjacent

def is_path_valid(start_pos: Position, delta: Position, existing_cubes: Set[Position], 
                 grid_size: Tuple[int, int, int], check_adjacency: bool = False) -> bool:
    """Check if a proposed path segment would collide with existing cubes or their adjacent spaces"""
    new_pos = start_pos + delta
    
    # Check grid boundaries
    if not all(0 <= coord < size for coord, size in zip((new_pos.x, new_pos.y, new_pos.z), grid_size)):
        return False
    
    # Handle walking paths and intermediate positions
    if delta.z == 0:  # Walking path
        intermediate_pos = Position(
            start_pos.x + delta.x // 2,
            start_pos.y + delta.y // 2,
            start_pos.z
        )
        if intermediate_pos in existing_cubes:
            return False
        # if check_adjacency: # this part is not needed because the begin position is always adjacent to the intermediate position. Enable this will forbid all walking paths
        #     if any(adj in existing_cubes for adj in get_adjacent_positions(intermediate_pos)):
        #         return False
    
    # Check end position
    if new_pos in existing_cubes:
        return False
        
    if check_adjacency:
        if any(adj in existing_cubes for adj in get_adjacent_positions(new_pos)):
            return False
    
    return True

def generate_valid_path(start: Position, grid_size: Tuple[int, int, int], 
                       existing_cubes: Set[Position] = None,
                       segRange: Tuple[int, int]=(5,7),
                       check_adjacency: bool = False) -> Tuple[List[PathSegment], Set[Position]]:
    """Generate a valid path from start position"""
    if existing_cubes is None:
        existing_cubes = set()
    
    current_pos = start
    path_segments = []
    path_cubes = {start}
    all_cubes = existing_cubes | path_cubes
    
    num_segments = random.randint(*segRange)
    
    for _ in range(num_segments):
        moves = []
        # Check possible moves
        possible_moves = []
        if current_pos.y - 2 > 0:
            possible_moves.append(('walk', Position(0, -2, 0)))
        if current_pos.x - 2 > 0:
            possible_moves.append(('walk', Position(-2, 0, 0)))
        if current_pos.z + 3 < grid_size[2]:
            possible_moves.append(('ladder', Position(0, 0, 3)))
            
        for move_type, delta in possible_moves:
            if delta and is_path_valid(current_pos, delta, all_cubes, grid_size, check_adjacency):
                moves.append((move_type, delta))
        
        if not moves:
            break
            
        move_type, delta = random.choice(moves)
        new_pos = current_pos + delta
        
        segment = PathSegment(current_pos, new_pos, move_type)
        path_segments.append(segment)
        
        if move_type == 'walk':
            intermediate_pos = Position(
                current_pos.x + delta.x // 2,
                current_pos.y + delta.y // 2,
                current_pos.z
            )
            path_cubes.add(intermediate_pos)
            all_cubes.add(intermediate_pos)
        
        path_cubes.add(new_pos)
        all_cubes.add(new_pos)
        current_pos = new_pos
    
    return path_segments, path_cubes

def get_ordered_path_cubes(path: List[PathSegment]) -> List[Position]:
    """Convert path segments into an ordered list of cubes, including intermediate positions"""
    ordered_cubes = []
    
    if path:
        ordered_cubes.append(path[0].start)
    
    for segment in path:
        if segment.type == 'walk':
            delta = Position(
                segment.end.x - segment.start.x,
                segment.end.y - segment.start.y,
                segment.end.z - segment.start.z
            )
            intermediate_pos = Position(
                segment.start.x + delta.x // 2,
                segment.start.y + delta.y // 2,
                segment.start.z
            )
            ordered_cubes.append(intermediate_pos)
        ordered_cubes.append(segment.end)
    
    return ordered_cubes

def is_positions_too_close(pos1: Position, pos2: Position) -> bool:
    """Check if two positions are too close (less than 2 blocks apart)"""
    return all(abs(getattr(pos1, attr) - getattr(pos2, attr)) < 2 
              for attr in ['x', 'y', 'z'])

def get_segment_direction(segment: PathSegment) -> str:
    """Determine the direction of a path segment"""
    if segment.type == 'ladder':
        return 'up'
    
    delta_x = segment.end.x - segment.start.x
    delta_y = segment.end.y - segment.start.y
    
    if delta_x == 0:
        return 'left-forward'
    elif delta_y == 0:
        return 'right-forward'
    return '??'

def get_plot_level(cubes: Set[Position]) -> str:
    """Determine plot level based on number of blocks"""
    num_blocks = len(cubes)
    if num_blocks < 15:
        return "Easy"
    elif num_blocks < 25:
        return "Medium"
    return "Hard"

def get_path_direction(segment: PathSegment) -> str:
    """Determine the direction of a path segment"""
    if segment.type == 'ladder':
        return 'up'
    
    # For walking paths, determine direction based on coordinate changes
    delta_x = segment.end.x - segment.start.x
    delta_y = segment.end.y - segment.start.y
    
    if delta_x == 0:
        return 'left-forward'
    elif delta_y == 0:
        return 'right-forward'  # or could be called 'straight'
    else:
        return '??'
    
def get_branch_order(main_path: List[PathSegment], branches: List[Branch]) -> List[Branch]:
    """Get branches in the order they appear along the main path"""
    ordered_positions = get_ordered_path_cubes(main_path)
    ordered_branches = []
    
    for pos in ordered_positions:
        for branch in branches:
            if pos == branch.pos and branch not in ordered_branches:
                ordered_branches.append(branch)
    
    return ordered_branches

def find_path_between_points(start: Position, end: Position, cubes: Set[Position], path: List[PathSegment]) -> List[PathSegment]:
    """Find the path segments between two points on the main path"""
    ordered_cubes = get_ordered_path_cubes(path)
    start_idx = ordered_cubes.index(start) if start in ordered_cubes else -1
    end_idx = ordered_cubes.index(end) if end in ordered_cubes else -1
    reverse=start_idx>end_idx
    
    if start_idx == -1 or end_idx == -1:
        return []
    
    # Get the relevant segment of the path
    relevant_cubes = ordered_cubes[min(start_idx, end_idx):max(start_idx, end_idx) + 1]
    relevant_segments = []
    
    for i in range(len(path)):
        segment = path[i]
        segment_cubes = [segment.start]
        if segment.type == 'walk':
            delta = Position(
                segment.end.x - segment.start.x,
                segment.end.y - segment.start.y,
                segment.end.z - segment.start.z
            )
            intermediate_pos = Position(
                segment.start.x + delta.x // 2,
                segment.start.y + delta.y // 2,
                segment.start.z
            )
            segment_cubes.append(intermediate_pos)
        segment_cubes.append(segment.end)
        
        if sum(cube in relevant_cubes for cube in segment_cubes)>1:
            relevant_segments.append(segment)
    
    return relevant_segments,reverse

def normalize_height_relation(heights):
    """Convert raw heights into a valid relation string that matches possible_relations format"""
    # Sort points by height, then by label for equal heights
    sorted_points = sorted(heights, key=lambda x: (x[1], x[0]))
    
    # Build relation string ensuring valid format
    relations = []
    current_height = None
    current_group = []
    
    # Group points by height
    for label, height in sorted_points:
        if height != current_height:
            if current_group:
                relations.append(current_group)
            current_group = [label]
            current_height = height
        else:
            current_group.append(label)
    relations.append(current_group)
    
    # Convert groups into relation string
    result = []
    for i, group in enumerate(relations):
        # Sort labels within group
        group.sort()
        result.append(" = ".join(str(x) for x in group))
    
    return " < ".join(result)


class PuzzleGenerator:
    def __init__(self, grid_size=None):
        grid_size = grid_size or (8,8,7)
        self.grid_size = grid_size
        self.start_pos = Position(grid_size[0]-1, grid_size[1]-1, 0)
    
    def _extract_ladders(self, path: List[PathSegment]) -> List[Ladder]:
        return [Ladder(segment.start, '+x', segment.end.z - segment.start.z)
                for segment in path if segment.type == 'ladder']
    
    def generate_path_finding_puzzle(self, main_path_length: Tuple[int, int] = (5, 7), side_path_num: Tuple[int,int] = (3, 4), side_path_length: Tuple[int, int] = (1, 2)) -> PathFindingState:
        """Generate a puzzle with branching paths"""
        main_path, main_cubes = generate_valid_path(self.start_pos, self.grid_size, segRange=main_path_length)
        goal_pos = main_path[-1].end
        
        all_cubes = main_cubes.copy()
        branches = []
        
        # Select branch positions
        ordered_cubes = get_ordered_path_cubes(main_path)
        valid_branch_positions = ordered_cubes[0:-3]
        random.shuffle(valid_branch_positions)
        
        selected_positions = []
        for pos in valid_branch_positions:
            if not any(is_positions_too_close(pos, selected_pos) 
                      for selected_pos in selected_positions) and pos.x%2==1 and pos.y%2==1:
                selected_positions.append(pos)
        
        side_path_num = min(len(selected_positions), random.randint(*side_path_num))
        selected_positions, alters = selected_positions[:side_path_num], selected_positions[side_path_num:]
        
        # Generate branches
        for i, branch_pos in enumerate(selected_positions, 1):
            for _ in range(10):
                alt_path, alt_cubes = generate_valid_path(
                    branch_pos, self.grid_size,
                    existing_cubes=all_cubes,
                    segRange=side_path_length,
                    check_adjacency=True
                )
                if alt_path:
                    break
                if alters:
                    branch_pos = random.choice(alters)
            if not alt_path:
                raise Exception("Cannot generate valid path")
            
            branches.append(Branch(branch_pos, i, {'A': main_path, 'B': alt_path}))
            all_cubes.update(alt_cubes)
        
        return PathFindingState(
            self.grid_size, all_cubes, self.start_pos, goal_pos,
            self._extract_ladders(main_path + sum((b.paths['B'] for b in branches), [])),
            main_path, branches, main_path
        )
    
    def choose_labeled_cubes(self, valid_positions: List[Position], num_labels: int) -> List[SequencePoint]:
        """Choose labeled cubes from the valid positions, ensuring they are not too close"""
        num_labels = min(num_labels, len(valid_positions))
        sequence_points = []
        label_positions = []
        
        while len(sequence_points) < num_labels and valid_positions:
            pos = random.choice(valid_positions)
            if not any(is_positions_too_close(pos, prev_pos) for prev_pos in label_positions):
                label_positions.append(pos)
                sequence_points.append(SequencePoint(pos, len(sequence_points) + 1))
            valid_positions.remove(pos)
        return sequence_points
    
    def generate_sequence_puzzle(self, label_num_range: Tuple[int, int] = (3, 4)) -> SequenceState:
        """Generate a puzzle with labeled sequence points"""
        main_path, main_cubes = generate_valid_path(self.start_pos, self.grid_size)
        goal_pos = main_path[-1].end
        
        
        ordered_cubes = get_ordered_path_cubes(main_path)
        valid_positions = ordered_cubes[1:-1]
        
        num_labels = random.randint(*label_num_range)
        sequence_points = self.choose_labeled_cubes(valid_positions, num_labels)
        
        return SequenceState(
            self.grid_size, main_cubes, self.start_pos, goal_pos,
            self._extract_ladders(main_path), main_path, sequence_points
        )

class QAGenerator:
    def __init__(self):
        self.puzzle_generator = PuzzleGenerator()
    
    def generate_qa_pair(self, index: int, qa_type: str):
        """Generate a Q&A pair based on the specified type"""
        self.puzzle_generator = PuzzleGenerator()
        if qa_type == 'path_finding':
            return self._generate_path_finding_qa(index)
        elif qa_type == 'sequence_finding':
            return self._generate_sequence_qa(index)
        elif qa_type == 'height_comparison':
            return self._generate_height_comparison_qa(index)
        elif qa_type == 'main_path':
            return self._generate_main_path_qa(index)
        raise ValueError(f"Unknown qa_type: {qa_type}")
    
    def _generate_path_finding_qa(self, index: int):
        """Generate a path-finding question and answer pair"""
        puzzle = self.puzzle_generator.generate_path_finding_puzzle()
        
        # Get branches in order of appearance
        ordered_branches = get_branch_order(puzzle.all_paths, puzzle.branches)
        
        def get_main_path_direction_at_branch(branch_pos: Position, path: List[PathSegment]) -> str:
            """Get the direction of the main path at the branch position"""
            current_segment = None
            for segment in path:
                if segment.start == branch_pos:
                    current_segment = segment
                    break
                    
                # For walking paths, check if branch is at intermediate position
                if segment.type == 'walk':
                    delta = Position(
                        segment.end.x - segment.start.x,
                        segment.end.y - segment.start.y,
                        segment.end.z - segment.start.z
                    )
                    intermediate_pos = Position(
                        segment.start.x + delta.x // 2,
                        segment.start.y + delta.y // 2,
                        segment.start.z
                    )
                    if intermediate_pos == branch_pos:
                        # Find the next segment that continues from this position
                        for next_segment in path:
                            if next_segment.start == segment.end:
                                current_segment = next_segment
                                break
                        break
            
            if current_segment:
                return get_path_direction(current_segment)
            return "??"

        # Create the correct path sequence with directional descriptions
        correct_path = ""
        for b in puzzle.branches:
            main_direction = get_main_path_direction_at_branch(b.pos, b.paths['A'])
            alt_segment = b.paths['B'][0]  # Alternative path always starts at branch position
            alt_direction = get_path_direction(alt_segment)
            correct_path += f"{b.branch_id}-{main_direction}, "
        correct_path = correct_path[:-2]  # Remove trailing comma and space
        
        # Create the correct path sequence with directional descriptions for ordered branches
        correct_path_ordered = ""
        for b in ordered_branches:
            main_direction = get_main_path_direction_at_branch(b.pos, b.paths['A'])
            alt_segment = b.paths['B'][0]  # Alternative path always starts at branch position
            alt_direction = get_path_direction(alt_segment)
            correct_path_ordered += f"{b.branch_id}-{main_direction}, "
        correct_path_ordered = correct_path_ordered[:-2]  # Remove trailing comma and space
        
        # Generate all possible combinations
        options = []
        for i in range(8):
            path = ""
            for branch in puzzle.branches:
                main_direction = get_main_path_direction_at_branch(branch.pos, branch.paths['A'])
                alt_segment = branch.paths['B'][0]
                alt_direction = get_path_direction(alt_segment)
                chosen_direction = main_direction if (i & (1 << (branch.branch_id - 1))) else alt_direction
                path += f"{branch.branch_id}-{chosen_direction}, "
            options.append(path[:-2])
        
        # Ensure correct path is in options
        if correct_path not in options:
            options[0] = correct_path
            
        random.shuffle(options)
        
        correct_answer = options.index(correct_path) + 1
        
        question = """Rules:
1. Player can only walk on top of cubes
2. Player can climb ladders if they can reach the cube under the ladder
3. From a ladder, player can reach the top of the last cube with the ladder
4. Blue cube is start position, red cube is goal position
5. Numbered cubes are branch points where player must choose a path

Which combination of path choices leads to the goal?"""
        
        # Create enhanced analysis with path progression
        branch_order_desc = "From the start point, "
        if ordered_branches:
            branch_order_desc += f"you first meet branch {ordered_branches[0].branch_id}"
            for b in ordered_branches[1:]:
                branch_order_desc += f", then branch {b.branch_id}"
            branch_order_desc += ", before finally reaching the goal."
        else:
            branch_order_desc += "you proceed directly to the goal."
        
        analysis = f"{branch_order_desc}\n\nAnalyzing each branch point:\n"
        for b in ordered_branches:
            main_direction = get_main_path_direction_at_branch(b.pos, b.paths['A'])
            alt_direction = get_path_direction(b.paths['B'][0])
            next_branch = None
            for i, next_b in enumerate(ordered_branches):
                if next_b.branch_id == b.branch_id:
                    if i + 1 < len(ordered_branches):
                        next_branch = ordered_branches[i + 1]
                    break
            
            if next_branch:
                analysis += f"- At branch {b.branch_id}, going {main_direction} leads to branch {next_branch.branch_id}, "
            else:
                analysis += f"- At branch {b.branch_id}, going {main_direction} leads toward the goal, "
            analysis += f"while going {alt_direction} leads to a dead end\n"
        
        analysis += f"\nTherefore, the correct sequence is {correct_path_ordered}, that is {correct_path}, making the answer Option {correct_answer}."
        
        data = {
            "qa_type": "TransitionPath",
            "question_description":"path_finding",
            "question_id": 0,
            "data_id": f"path-mcq-{index:05d}-path_finding",
            "plot_id": f"path-plot-{index:05d}",
            "image": f"images/path-mcq-{index:05d}.png",
            "state": f"states/path-mcq-{index:05d}.json",
            "plot_level": get_plot_level(puzzle.cubes),
            "qa_level": "Hard",  # path_finding questions are more complex
            "question": f"{question}\n\nOptions:\n" + "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options)),
            "answer": correct_answer,
            "options": options,
            "analysis": analysis
        }
        
        return data, puzzle

    def _generate_sequence_qa(self, index: int):
        """Generate a sequence question Q&A pair"""
        puzzle = self.puzzle_generator.generate_sequence_puzzle()
        
        # Get the correct sequence order
        ordered_cubes = get_ordered_path_cubes(puzzle.path)
        sequence = ["Start"]
        
        # Create ordered sequence by checking each cube in path order
        for cube in ordered_cubes:
            for sp in sorted(puzzle.sequence_points, key=lambda x: x.label):
                if sp.pos == cube:
                    sequence.append(str(sp.label))
        sequence.append("Goal")
        
        correct_sequence = " -> ".join(sequence)
        
        # Generate wrong options by shuffling middle numbers
        middle_numbers = sequence[1:-1]
        options = [correct_sequence]
        
        while len(options) < 6:  # Generate 7 wrong options
            random.shuffle(middle_numbers)
            wrong_sequence = " -> ".join(["Start"] + middle_numbers + ["Goal"])
            if wrong_sequence not in options:
                options.append(wrong_sequence)
        
        random.shuffle(options)
        correct_answer = options.index(correct_sequence) + 1
        
        question = """Rules:
1. Player can only walk on top of cubes
2. Player can climb ladders if they can reach the cube under the ladder
3. From a ladder, player can reach the top of the last cube with the ladder
4. Blue cube is start position, red cube is goal position
5. Green cubes are numbered checkpoints

What is the correct sequence of numbered checkpoints when following the path from start to goal?"""
        
        # Create analysis explaining the path
        analysis = "Following the path from start to goal:\n"
        current_pos = puzzle.start_pos
        step = 1
        
        for segment in puzzle.path:
            direction = get_segment_direction(segment)
            
            # Check if there's a sequence point at the current position
            for sp in puzzle.sequence_points:
                if sp.pos == current_pos:
                    analysis += f"\nStep {step}: At checkpoint {sp.label}"
                    step += 1
            
            # For walking paths, check intermediate position for checkpoints
            if segment.type == 'walk':
                delta = Position(
                    segment.end.x - segment.start.x,
                    segment.end.y - segment.start.y,
                    segment.end.z - segment.start.z
                )
                intermediate_pos = Position(
                    segment.start.x + delta.x // 2,
                    segment.start.y + delta.y // 2,
                    segment.start.z
                )
                # Check for checkpoint at intermediate position
                for sp in puzzle.sequence_points:
                    if sp.pos == intermediate_pos:
                        analysis += f"\nStep {step}: At checkpoint {sp.label}"
                        step += 1
        
            analysis += f"\nStep {step}: Move {direction}"
            current_pos = segment.end
            step += 1
        
        # Add final checkpoint if it exists
        for sp in puzzle.sequence_points:
            if sp.pos == current_pos:
                analysis += f"\nStep {step}: At checkpoint {sp.label}"
        
        analysis += f"\n\nTherefore, the correct sequence is {correct_sequence}, making the answer Option {correct_answer}."
        
        data = {
            "qa_type": "TransitionPath",
            "question_description":"sequence_finding",
            "question_id": 1 ,
            "data_id": f"path-mcq-{index:05d}",
            "plot_id": f"path-plot-{index:05d}",
            "image": f"images/path-mcq-{index:05d}.png",
            "state": f"states/path-mcq-{index:05d}.json",
            "plot_level": get_plot_level(puzzle.cubes),
            "qa_level": "Medium",  # sequence_finding questions are medium complexity
            "question": f"{question}\n\nOptions:\n" + "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options)),
            "answer": correct_answer,
            "options": options,
            "analysis": analysis
        }
        
        return data, puzzle

    def _generate_height_comparison_qa(self, index: int):
        """Generate a height comparison question Q&A pair with corrected relation handling"""
        puzzle = self.puzzle_generator.generate_sequence_puzzle((3, 3))
        
        # Get heights of comparison points
        heights = [(p.label, p.pos.z) for p in puzzle.sequence_points]
        
        # Generate the correct height relation string using normalized format
        correct_relation = normalize_height_relation(heights)
        
        # List of all possible height relations
        possible_relations = [
            "1 < 2 < 3", "1 < 3 < 2", "2 < 1 < 3", "2 < 3 < 1", "3 < 1 < 2", "3 < 2 < 1",
            "1 < 2 = 3", "2 < 1 = 3", "3 < 1 = 2", "1 = 2 < 3", "1 = 3 < 2", "2 = 3 < 1",
            "1 = 2 = 3"
        ]
        
        # Generate options
        options = [correct_relation]
        while len(options) < 8:
            wrong_relation = random.choice(possible_relations)
            if wrong_relation not in options:
                options.append(wrong_relation)
        
        random.shuffle(options)
        correct_answer = options.index(correct_relation) + 1
        
        question = """Rules:
1. Player can only walk on top of cubes
2. Player can climb ladders if they can reach the cube under the ladder
3. From a ladder, player can reach the top of the last cube with the ladder
4. Blue cube is start position, red cube is goal position
5. Green cubes are numbered points (1, 2, and 3)

What is the correct height relationship between the three numbered points? Use '<' for 'lower than' and '=' for 'same height as'."""
        
        # Create analysis explaining the height relationships
        analysis = "Analyzing the heights of each point:\n"
        
        # Compare each pair of points
        for i, point1 in enumerate(puzzle.sequence_points):
            for j, point2 in enumerate(puzzle.sequence_points[i+1:], i+1):
                path_segments, reverse = find_path_between_points(point1.pos, point2.pos, puzzle.cubes, puzzle.path)
                current_pos = point1.pos
                
                height_diff = point2.pos.z - point1.pos.z
                relation = "same height as" if height_diff == 0 else ("higher than" if height_diff > 0 else "lower than")
                
                analysis += f"\nComparing points {point1.label} and {point2.label}:\n"
                analysis += f" Found a path from {(point2 if reverse else point1).label} to {(point1 if reverse else point2).label}:\n"
                for segment in path_segments:
                    direction = get_segment_direction(segment)
                    if segment.type == 'ladder':
                        analysis += f"  * Go up {segment.end.z - segment.start.z} blocks\n"
                    else:
                        analysis += f"  * Move {direction}\n"
                    current_pos = segment.end
                    
                analysis += f"- Point {point2.label} is {relation} point {point1.label}\n"
        
        analysis += f"\nTherefore, the correct height relationship is {correct_relation}, making the answer Option {correct_answer}."
        
        data = {
            "qa_type": "StateInfo",
            "question_description":"height_comparison",
            "question_id": 2,
            "data_id": f"path-mcq-{index:05d}",
            "plot_id": f"path-plot-{index:05d}",
            "image": f"images/path-mcq-{index:05d}.png",
            "state": f"states/path-mcq-{index:05d}.json",
            "plot_level": get_plot_level(puzzle.cubes),
            "qa_level": "Easy",  # height comparison questions are simpler
            "question": f"{question}\n\nOptions:\n" + "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options)),
            "answer": correct_answer,
            "options": options,
            "analysis": analysis
        }
        
        return data, puzzle

    def _generate_main_path_qa(self, index: int):
        """Generate a question about which numbered blocks are on the main path"""
        puzzle = self.puzzle_generator.generate_path_finding_puzzle()
        
        # Get main path cubes in order
        cubes = puzzle.cubes
        
        # Remove start and goal positions from cubes when choosing labeled cubes
        cubes_remove = cubes.copy()
        cubes_remove.remove(puzzle.start_pos)
        cubes_remove.remove(puzzle.goal_pos)
        
        main_path_cubes = get_ordered_path_cubes(puzzle.path)
        
        label_cubes = self.puzzle_generator.choose_labeled_cubes(list(cubes_remove), random.randint(3, 4))
        
        puzzle.branches = [Branch(cube.pos, cube.label, {'A': [], 'B': []}) for cube in label_cubes] # so that draw_puzzle can draw the labels
        
        # Create list of branch numbers that are on main path vs side paths
        main_path_branches = []
        side_path_branches = []
        
        for cube in label_cubes:
            if cube.pos in main_path_cubes:
                main_path_branches.append(str(cube.label))
            else:
                side_path_branches.append(str(cube.label))
        
        # Generate the correct answer
        correct_answer = ", ".join(sorted(main_path_branches, key=int))
        if correct_answer == "":
            correct_answer = "None"
        
        # Generate wrong options by mixing main path and side path branches
        all_branches = [str(b.label) for b in label_cubes]
        options = [correct_answer]
        
        # Generate wrong options by taking different combinations
        while len(options) < 8:
            num_choices = random.randint(0, len(all_branches))
            if num_choices == 0:
                wrong_answer = "None"
            else:
                wrong_branches = random.sample(all_branches, num_choices)
                wrong_answer = ", ".join(sorted(wrong_branches, key=int))
            if wrong_answer not in options:
                options.append(wrong_answer)
        
        random.shuffle(options)
        correct_option = options.index(correct_answer) + 1
        
        question = """Rules:
    1. Player can only walk on top of cubes
    2. Player can climb ladders if they can reach the cube under the ladder
    3. From a ladder, player can reach the top of the last cube with the ladder
    4. Blue cube is start position, red cube is goal position
    5. Numbered cubes are branch points

    Which numbered blocks are passed through when following the most direct path from start to goal?"""

        # Create detailed path analysis
        analysis = "Following the main path from start to goal:\n"
        current_pos = puzzle.start_pos
        step = 1
        
        for segment in puzzle.path:
            direction = get_segment_direction(segment)
            
            # Check if current position is a branch point
            branch_num = None
            for branch in puzzle.branches:
                if branch.pos == current_pos:
                    branch_num = branch.branch_id
                    break
            
            if branch_num is not None:
                analysis += f"\nStep {step}: At Block {branch_num}"
                step += 1
            
            # For walking paths, check intermediate position for branch points
            if segment.type == 'walk':
                delta = Position(
                    segment.end.x - segment.start.x,
                    segment.end.y - segment.start.y,
                    segment.end.z - segment.start.z
                )
                intermediate_pos = Position(
                    segment.start.x + delta.x // 2,
                    segment.start.y + delta.y // 2,
                    segment.start.z
                )
                # Check for branch at intermediate position
                for branch in puzzle.branches:
                    if branch.pos == intermediate_pos:
                        analysis += f"\nStep {step}: At Block {branch.branch_id}"
                        step += 1
            
            analysis += f"\nStep {step}: Move {direction}"
            current_pos = segment.end
            step += 1
        
        # Add information about side paths
        if side_path_branches:
            analysis += f"\n\nBlocks not on main path: {', '.join(sorted(side_path_branches, key=int))}"
        
        analysis += f"\n\nTherefore, the blocks passed through on the main path are: {correct_answer}, making the answer Option {correct_option}."
        
        data = {
            "qa_type": "TransitionPath",
            "question_description":"main_path",
            "question_id": 3,
            "data_id": f"path-mcq-{index:05d}",
            "plot_id": f"path-plot-{index:05d}",
            "image": f"images/path-mcq-{index:05d}.png",
            "state": f"states/path-mcq-{index:05d}.json",
            "plot_level": get_plot_level(puzzle.cubes),
            "qa_level": "Medium",
            "question": f"{question}\n\nOptions:\n" + "\n".join(f"{i+1}: {opt}" for i, opt in enumerate(options)),
            "answer": correct_option,
            "options": options,
            "analysis": analysis
        }
        
        return data, puzzle
        
def generate_mixed_dataset(num_problems: int):
    """Generate a dataset with mixed problem types"""
    ensure_output_dirs()
    dataset = []
    qa_generator = QAGenerator()
    
    qa_types = ['path_finding', 'sequence_finding', 'height_comparison', 'main_path']
    i = 0
    count=0
    while i < num_problems:
        try:
            # print(f"Generating problem {i+1}")
            qa_type = qa_types[i % len(qa_types)]
            data, puzzle = qa_generator.generate_qa_pair(i + 1, qa_type)
            draw_puzzle(puzzle, f"{outputPath}/images/path-mcq-{i+1:05d}.png")
            dataset.append(data)
            i += 1
            count=0
        except Exception as e:
            if str(e) != "Cannot generate valid path":
                raise e
            count+=1
            if count>10:
                print("Too many failures, aborting")
                raise e
    
    with open(f"{outputPath}/data.json", 'w') as f:
        json.dump(dataset, f, indent=2)

def ensure_output_dirs():
    """Create output directories if they don't exist"""
    os.makedirs(f"{outputPath}/images", exist_ok=True)
    os.makedirs(f"{outputPath}/states", exist_ok=True)

if __name__ == "__main__":
    outputPath = "3d_maze_dataset"
    generate_mixed_dataset(15)