import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from itertools import combinations
import random
from matplotlib.gridspec import GridSpec

class ThreeDimensionalReconstruction:
    def __init__(self, target_voxels_count=7, initial_voxels_count=4):
        """
        Initialize the 3D Reconstruction game.
        
        Args:
            target_voxels_count (int): Number of voxels in the target structure (1-27)
            initial_voxels_count (int): Number of initial voxels (must be less than target_voxels_count)
        """
        if not (1 <= target_voxels_count <= 27):
            raise ValueError("Target voxels count must be between 1 and 27")
        if initial_voxels_count >= target_voxels_count:
            raise ValueError("Initial voxels count must be less than target voxels count")
            
        self.target_count = target_voxels_count
        self.target_voxels = self._generate_connected_structure_with_base(target_voxels_count)
        self.current_voxels = self._generate_initial_state(self.target_voxels, initial_voxels_count)
        self.target_yz_projection, self.target_xz_projection = self._calculate_projections(self.target_voxels)
        self.minimal_addition = self._find_minimal_solution()
        self.complete_solution = list(set(self.current_voxels) | set(self.minimal_addition))

    def _get_adjacent_neighbors(self, voxel):
        """Get face-adjacent neighbors of a voxel within the 3x3x3 grid."""
        x, y, z = voxel
        neighbors = []
        directions = [(-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,-1), (0,0,1)]
        for dx, dy, dz in directions:
            neighbor = (x + dx, y + dy, z + dz)
            if all(1 <= coord <= 3 for coord in neighbor):
                neighbors.append(neighbor)
        return neighbors

    def _generate_connected_structure_with_base(self, voxel_count):
        """Generate a connected set of voxels with at least one in the base layer."""
        all_positions = [(x, y, z) for x in range(1,4) for y in range(1,4) for z in range(1,4)]
        base_voxel = random.choice([(x, y, 1) for x, y in [(i, j) for i in range(1,4) for j in range(1,4)]])
        structure = {base_voxel}

        while len(structure) < voxel_count:
            all_neighbors = set()
            for voxel in structure:
                all_neighbors.update(self._get_adjacent_neighbors(voxel))
            available_neighbors = all_neighbors - structure
            if not available_neighbors:
                break
            structure.add(random.choice(list(available_neighbors)))

        return list(structure)

    def _generate_initial_state(self, target_structure, initial_count):
        """Generate initial game state from target structure."""
        base_layer = [v for v in target_structure if v[2] == 1]
        if not base_layer:
            raise ValueError("Target structure must have at least one voxel in base layer")

        initial_state = {random.choice(base_layer)}
        while len(initial_state) < initial_count:
            all_neighbors = set()
            for voxel in initial_state:
                all_neighbors.update(self._get_adjacent_neighbors(voxel))
            valid_neighbors = all_neighbors & set(target_structure) - initial_state
            if not valid_neighbors:
                break
            initial_state.add(random.choice(list(valid_neighbors)))

        return list(initial_state)

    def _calculate_projections(self, voxels):
        """Calculate front (Y-Z) and side (X-Z) plane projections."""
        yz_grid = np.zeros((3,3), dtype=int)
        xz_grid = np.zeros((3,3), dtype=int)
        for x, y, z in voxels:
            yz_grid[y-1, z-1] = 1  # Front view (Y-Z)
            xz_grid[x-1, z-1] = 1  # Side view (X-Z)
        return yz_grid, xz_grid

    def _is_connected(self, voxel_set):
        """Check if a set of voxels forms a connected structure."""
        if not voxel_set:
            return False
        visited = set()
        to_visit = {next(iter(voxel_set))}
        while to_visit:
            current = to_visit.pop()
            visited.add(current)
            neighbors = set(self._get_adjacent_neighbors(current)) & voxel_set
            to_visit.update(neighbors - visited)
        return visited == voxel_set

    def _find_minimal_solution(self):
        """Find minimal set of voxels to add to satisfy projections."""
        current_set = set(self.current_voxels)
        all_positions = [(x, y, z) for x in range(1, 4) for y in range(1, 4) for z in range(1, 4)]
        candidates = [pos for pos in all_positions if pos not in current_set]

        def validates_solution(additional_voxels):
            test_structure = current_set.union(set(additional_voxels))
            if not self._is_connected(test_structure):
                return False
            yz_proj, xz_proj = self._calculate_projections(list(test_structure))
            return (np.array_equal(yz_proj, self.target_yz_projection) and 
                   np.array_equal(xz_proj, self.target_xz_projection))

        def can_connect(voxel, structure):
            return bool(set(self._get_adjacent_neighbors(voxel)) & structure)
        
        if validates_solution([]):
            return []
        
        max_additional = len(self.target_voxels) - len(self.current_voxels)
        for size in range(1, max_additional + 1):
            for combination in combinations(candidates, size):
                combination = list(combination)
                test_structure = current_set.copy()

                valid = True
                for voxel in combination:
                    if not can_connect(voxel, test_structure):
                        valid = False
                        break
                    test_structure.add(voxel)

                if not valid:
                    continue

                if validates_solution(combination):
                    return combination

        return [v for v in self.target_voxels if v not in current_set]

    def generate_random_connected_voxels(self, count, respect_remaining=False):
        """
        Generate random connected voxels based on current state.
        
        Args:
            count (int): Number of voxels to generate
            respect_remaining (bool): If True, will not generate more than remaining available voxels
        
        Returns:
            tuple: (current_voxels, new_voxels) where:
                  - current_voxels is a list of existing voxel positions
                  - new_voxels is a list of newly generated voxel positions
        """
        if respect_remaining:
            remaining = len(self.target_voxels) - len(self.current_voxels)
            count = min(count, remaining)
            
        all_positions = [(x, y, z) for x in range(1,4) for y in range(1,4) for z in range(1,4)]
        current_structure = set(self.current_voxels)
        new_voxels = []
        
        while len(new_voxels) < count:
            # Get all possible neighbors of the current structure
            all_neighbors = set()
            for voxel in current_structure:
                neighbors = set(self._get_adjacent_neighbors(voxel))
                all_neighbors.update(neighbors - current_structure)
            
            # Filter out positions that are already occupied or in new_voxels
            available_positions = all_neighbors - current_structure - set(new_voxels)
            
            if not available_positions:
                break
            
            # Add a random neighbor
            new_voxel = random.choice(list(available_positions))
            new_voxels.append(new_voxel)
        
        return list(current_structure), new_voxels

    def visualize_structure(self, show_solution=False, name=None, structure=None):
        """
        Visualize the voxel structure with projections.
        
        Args:
            show_solution (bool): If True, shows complete solution. If False, shows current state.
                                    Only used when structure is None.
            name (str): Optional custom name for the output file. If None, uses default naming.
            structure (list): Optional specific structure to visualize. If None, uses show_solution
                             to determine whether to show current_voxels or complete_solution.
        """
        # Determine which structure to show
        if structure is not None:
            display_structure = structure
            title_prefix = 'Custom Structure'
            # 计算custom结构的remaining
            added_voxels = len(set(structure) - set(self.current_voxels))
            remaining = len(self.target_voxels) - len(self.current_voxels) - added_voxels
        else:
            display_structure = self.complete_solution if show_solution else self.current_voxels
            title_prefix = 'Complete Solution' if show_solution else 'Current Structure'
            remaining = len(self.target_voxels) - len(self.current_voxels) if not show_solution else None
        
        # Use custom name if provided, otherwise use default
        if name is None:
            if structure is not None:
                name = '3DReconstruction_custom'
            else:
                name = '3DReconstruction_solution' if show_solution else '3DReconstruction_current'
        
        # Create figure
        fig = plt.figure(figsize=(8, 6), dpi=95)
        gs = GridSpec(2, 2, width_ratios=[1.5, 1], height_ratios=[1, 1], 
                     figure=fig, wspace=0.25, hspace=0.2)

        # Main title
        fig.suptitle('3D Voxel Reconstruction Game', fontsize=16, y=0.95)

        # 3D Structure plot
        ax_3d = fig.add_subplot(gs[:, 0], projection='3d')
        self._setup_3d_plot(ax_3d, display_structure, remaining, title_prefix)

        # Side view plots
        ax_yz = fig.add_subplot(gs[0, 1])
        ax_xz = fig.add_subplot(gs[1, 1])
        self._setup_side_views(ax_yz, ax_xz)

        plt.savefig(name, dpi=95, bbox_inches='tight')
        plt.close()

    def _setup_3d_plot(self, ax, structure, remaining, title_prefix):
        """Setup the 3D plot with grid, axes, and voxels."""
        # Set axis limits
        ax.set_xlim(0, 3)
        ax.set_ylim(0, 3)
        ax.set_zlim(0, 3)

        # Draw coordinate axes and labels
        for axis, color in zip(['X', 'Y', 'Z'], ['r', 'g', 'b']):
            if axis == 'X':
                ax.plot([0,3.1], [0,0], [0,0], color=color, linewidth=2)
                ax.text(3.3, 0, 0, axis, color=color, fontsize=10, ha='center', va='center')
            elif axis == 'Y':
                ax.plot([0,0], [0,3.1], [0,0], color=color, linewidth=2)
                ax.text(0, 3.3, 0, axis, color=color, fontsize=10, ha='center', va='center')
            else:  # Z
                ax.plot([0,0], [0,0], [0,3.1], color=color, linewidth=2)
                ax.text(0, 0, 3.3, axis, color=color, fontsize=10, ha='center', va='center')

        # Draw grid lines
        self._draw_grid_lines(ax)

        # Plot voxels
        voxel_grid = np.zeros((3,3,3), dtype=bool)
        for x, y, z in structure:
            voxel_grid[x-1, y-1, z-1] = True
        ax.voxels(voxel_grid, facecolors='cyan', edgecolors='k', linewidth=0.5, alpha=0.7)

        # Add coordinate labels
        self._add_coordinate_labels(ax)

        # Set title
        ax.set_title(title_prefix, fontsize=12, pad=10)

        # Adjust view and remove default elements
        ax.view_init(elev=15, azim=55)
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

        # Add remaining voxels text if applicable
        if remaining is not None:
            ax.text2D(0.5, 0.00001, f"Remaining Available Voxels: {remaining}", 
                    transform=ax.transAxes, ha="center", va="bottom", fontsize=10,
                    bbox={"facecolor":"orange", "alpha":0.5, "pad":3})

    def _draw_grid_lines(self, ax):
        """Draw grid lines on the 3D plot."""
        grid_color = 'lightgrey'
        for i in range(4):
            # XY plane
            ax.plot([0,3], [i,i], [0,0], color=grid_color, linewidth=0.5)
            ax.plot([i,i], [0,3], [0,0], color=grid_color, linewidth=0.5)
            # XZ plane
            ax.plot([0,3], [0,0], [i,i], color=grid_color, linewidth=0.5)
            ax.plot([i,i], [0,0], [0,3], color=grid_color, linewidth=0.5)
            # YZ plane
            ax.plot([0,0], [0,3], [i,i], color=grid_color, linewidth=0.5)
            ax.plot([0,0], [i,i], [0,3], color=grid_color, linewidth=0.5)

    def _add_coordinate_labels(self, ax):
        """Add coordinate labels to the 3D plot."""
        label_props = dict(fontsize=8, ha='center', va='center')
        for axis, color in zip(['X', 'Y', 'Z'], ['r', 'g', 'b']):
            for i in range(1,4):
                if axis == 'X':
                    ax.text(i - 0.5, 3.2, -0.2, str(i), color=color, **label_props)
                elif axis == 'Y':
                    ax.text(3.2, i - 0.5, -0.2, str(i), color=color, **label_props)
                else:  # Z
                    ax.text(-0.2, 3.2, i - 0.5, str(i), color=color, **label_props)

    def _setup_side_views(self, ax_yz, ax_xz):
        """Setup the side view projections."""
        view_settings = {
            'extent': [0,3,0,3],
            'origin': 'lower',  # 确保Z轴从下到上
            'aspect': 'equal',
            'vmin': 0,  # 设置颜色映射的最小值
            'vmax': 1,  # 设置颜色映射的最大值
            'cmap': 'Blues'  # 使用Blues色图
        }

        # Plot projections
        # 转置矩阵使得Y/X轴在水平方向，Z轴在垂直方向
        ax_yz.imshow(self.target_yz_projection.T, **view_settings)
        ax_xz.imshow(self.target_xz_projection.T, **view_settings)

        # Adjust size
        for ax in [ax_yz, ax_xz]:
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.9, box.height * 0.9])

        # Add labels and formatting
        self._format_side_view(ax_yz, 'Front View (Y-Z Plane)', 'Y')
        self._format_side_view(ax_xz, 'Side View (X-Z Plane)', 'X')

    def _format_side_view(self, ax, title, xlabel):
        """Format a side view projection plot."""
        # Grid lines
        for i in range(4):
            ax.axhline(i, color='lightgrey', linewidth=0.5)
            ax.axvline(i, color='lightgrey', linewidth=0.5)
        
        # Coordinate labels
        for i in range(1,4):
            ax.text(i - 0.5, -0.13, str(i), ha='center', va='center', fontsize=8)  # 水平轴标签
            ax.text(-0.08, i - 0.5, str(i), ha='center', va='center', fontsize=8)  # 垂直轴标签
        
        # Labels and formatting
        ax.set_xlabel(xlabel, fontsize=10, labelpad=10)  # X轴或Y轴标签
        ax.set_ylabel('Z', fontsize=10, labelpad=5)      # Z轴标签
        ax.set_title(title, fontsize=12, pad=5)
        ax.set_xticks([])
        ax.set_yticks([])

    def get_game_state(self):
        """
        Get information about the current game state.
        
        Returns:
            dict: Contains counts and positions of current state, minimal addition, 
                 complete solution voxels, and target count
        """
        return {
            'current_state': {
                'count': len(self.current_voxels),
                'positions': self.current_voxels
            },
            'minimal_addition': {
                'count': len(self.minimal_addition),
                'positions': self.minimal_addition
            },
            'complete_solution': {
                'count': len(self.complete_solution),
                'positions': self.complete_solution
            },
            'target_count': self.target_count
        }

    def get_projections(self, structure):
        """
        Calculate Y-Z (front) and X-Z (side) projections for a given structure.
        
        Args:
            structure (list): List of (x,y,z) tuples representing voxel positions
        
        Returns:
            tuple: (yz_projection, xz_projection) where each projection is a 3x3 boolean numpy array
                   yz_projection shows the structure viewed from the X direction (front view, Y-Z plane)
                   xz_projection shows the structure viewed from the Y direction (side view, X-Z plane)
        """
        # 验证输入的结构是否合法
        for x, y, z in structure:
            if not (1 <= x <= 3 and 1 <= y <= 3 and 1 <= z <= 3):
                raise ValueError(f"Invalid voxel position: ({x}, {y}, {z}). All coordinates must be between 1 and 3.")
        
        return self._calculate_projections(structure)


# Example usage:
if __name__ == "__main__":
    print("=== 3D Reconstruction Game Test Cases ===\n")
    
    # 1. 创建游戏实例
    print("1. 创建游戏实例 (目标7个方块，初始4个方块)")
    game = ThreeDimensionalReconstruction(target_voxels_count=10, initial_voxels_count=6)
    
    # 2. 获取并打印当前游戏状态
    print("\n2. 获取当前游戏状态")
    state_info = game.get_game_state()
    print(f"初始结构: {state_info['current_state']['count']} 个方块")
    print(f"位置: {state_info['current_state']['positions']}")
    print(f"\n最小需要添加: {state_info['minimal_addition']['count']} 个方块")
    print(f"位置: {state_info['minimal_addition']['positions']}")
    print(f"\n完整解决方案: {state_info['complete_solution']['count']} 个方块")
    print(f"位置: {state_info['complete_solution']['positions']}")
    
    # 3. 生成随机连续方块
    print("\n3. 测试随机生成连续方块")
    random_voxels = game.generate_random_connected_voxels(3)
    print(f"随机生成了 {len(random_voxels)} 个新方块")
    print(f"新方块位置: {random_voxels}")
    
    # 4. 测试不同的可视化方式
    print("\n4. 测试不同的可视化方式")
    
    # 4.1 可视化当前状态
    print("4.1 生成当前状态可视化...")
    game.visualize_structure(show_solution=False, name="test_current_state")
    
    # 4.2 可视化完整解决方案
    print("4.2 生成完整解决方案可视化...")
    game.visualize_structure(show_solution=True, name="test_complete_solution")
    
    # 4.3 可视化包含随机方块的结构
    print("4.3 生成包含随机方块的结构可视化...")
    combined_structure = game.current_voxels + random_voxels
    game.visualize_structure(structure=combined_structure, name="test_with_random_voxels")
    
    print("\n=== 测试完成 ===")
    print("生成的图片文件:")
    print("- test_current_state.png")
    print("- test_complete_solution.png")
    print("- test_with_random_voxels.png")
