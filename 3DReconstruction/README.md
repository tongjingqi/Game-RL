# 3D Reconstruction Game Q&A Dataset Generator

This is a tool for generating Q&A datasets related to 3D reconstruction games. The tool can generate various types of questions, including fill-in-the-blank and multiple choice questions, to test understanding of 3D reconstruction game rules and strategies.

## Installation:
```bash
pip install -r requirements.txt
```

Dependencies include:

- Python 3.6+
- NumPy >= 1.19.0
- Matplotlib >= 3.3.0
- tqdm >= 4.65.0

## Game Rules

1. Game Space: Takes place in a 3x3x3 cubic grid
2. Coordinate System: Positions (x,y,z) range from 1 to 3, with (1,1,1) at the front-left-bottom
3. Position Rule: Only one voxel can be placed at each position
4. Connection Rule: All voxels must be face-to-face connected
5. Voxel Limit: There is a maximum limit on the number of voxels that can be added
6. Placement Rule: New voxels can only be placed adjacent to existing voxels
7. Projection Rules:
   - Front View (Z-Y): Shows structure when viewed from negative X-axis (front to back), with Y-axis horizontal and Z-axis vertical
   - Side View (Z-X): Shows structure when viewed from positive Y-axis (left to right), with X-axis horizontal and Z-axis vertical
   - A cell in the projection shows 1 if there is a voxel along that line of sight
8. Win Condition: Match the target projections using no more than the limited number of voxels

## Difficulty Levels

The game has two different types of difficulty levels:

### 1. Question Difficulty (qa_level)
This is a fixed difficulty level based on question type:

- Easy:
  - Count: Calculate the number of voxels in the current structure
  - Position: Check if a specific position has a voxel

- Medium:
  - Projection: Check if the current structure's projections match the target views
  - ActionOutcome: Predict the projection matrix after adding specified voxels

- Hard:
  - StrategyOptimization: Calculate the minimum number of voxels needed to achieve the target
  - TransitionPath: Choose the correct sequence of voxel additions to satisfy target projections

### 2. Structure Difficulty (plot_level)
This is defined by the number of voxels:

- Easy: 3-5 voxels, need to fill 3
- Medium: 6-10 voxels, need to fill 4
- Hard: 11-15 voxels, need to fill 5

### Difficulty Distribution

You can set the structure difficulty (plot_level) distribution ratio using the --level-ratios parameter:

- Format: x:y:z (e.g., 0.2:0.2:0.6)
- The three numbers represent Easy:Medium:Hard ratios
- At most one value can be omitted, which will be auto-calculated (ensuring sum is 1)
- If not set, difficulties are evenly distributed (one third each)

## Question Distribution

The generator supports two ways of distributing questions:

1. Equal Distribution (default):
   - If no question type ratios are specified, questions are equally distributed among 6 types
   - Example: For 100 questions, about 16-17 questions per type
   - Remainders are distributed from first to last type

2. Ratio Distribution:
   - Specify ratios for each type using --type-ratios parameter
   - Sum of ratios must equal 1
   - Precisely calculates number of questions for each type
   - Example: With count=0.2, 20 out of 100 questions will be count type

Note:
- In ratio distribution, the last type gets remaining questions to ensure correct total
- Recommended to generate at least 1 question per type for dataset diversity

## Question Types

1. StateInfo Type
   - Count: Calculate number of voxels in current structure
   - Position: Check if specific position has a voxel
   - Projection: Check if current structure's projections match target views

2. ActionOutcome Type
   - Predict the projection matrix (front view or side view) after adding specified voxels to the current structure
   - Answer should be written as a 3x3 matrix showing the projection pattern

3. TransitionPath Type
   - Choose correct voxel addition sequence from options to satisfy target projections
   - Considers connectivity, projection matching, and voxel limit constraints

4. StrategyOptimization Type
   - Calculate minimum voxels needed to achieve target
   - Returns 0 if current structure already matches target projections
   - Otherwise returns minimum voxels needed to reach target

## Usage

### Command Line Arguments

```bash
python main.py [arguments]
```

Available arguments:

- `--total N`: Generate N questions (default: 100)
- `--qa-types TYPE1 TYPE2 ...`: Specify specific question types to generate (multiple allowed)
  - count: Counting questions
  - position: Position checking
  - projection: Projection matching
  - action_outcome: Action results
  - strategy_optimization: Strategy optimization
  - transition_path: Transition path
- `--type-ratios RATIOS`: Set question type ratios
  - Format: 0.2:0.2:0.2:0.2:0.1:0.1
  - Six numbers correspond to: count, position, projection, action_outcome, strategy_optimization, transition_path
  - Sum of ratios must equal 1
- `--level-ratios RATIOS`: Set difficulty level ratios
  - Format: 0.2:0.2:0.6
  - At most one value can be omitted

### Usage Examples

1. Generate 100 questions with default settings (equal distribution for both question types and difficulty levels):
```bash
python main.py --total 100
```

2. Generate specific types of questions:
```bash
python main.py --total 100 --qa-types count position projection
```

3. Use custom type ratios:
```bash
python main.py --total 100 --type-ratios 0.2:0.2:0.2:0.2:0.1:0.1
```

4. Set difficulty level ratios:
```bash
# Generate 100 questions with Easy:Medium:Hard = 0.2:0.2:0.6
python main.py --total 100 --level-ratios 0.2:0.2:0.6

# Omit first value, automatically calculated as 0.4:0.2:0.4
python main.py --total 100 --level-ratios :0.2:0.4
```

5. Combine multiple parameters:
```bash
python main.py --total 100 \
    --type-ratios 0.2:0.2:0.2:0.2:0.1:0.1 \
    --level-ratios 0.2:0.2:0.6
```

### Python API Usage

```python
from QAGenerator import ThreeDReconstructionQAGenerator

# Create generator instance
generator = ThreeDReconstructionQAGenerator()

# Generate dataset with default settings
generator.generate_all_datasets(total_samples=100)

# Optional: Use custom type ratios
custom_ratios = {
    'count': 0.2,
    'position': 0.2,
    'projection': 0.2,
    'action_outcome': 0.2,
    'strategy_optimization': 0.1,
    'transition_path': 0.1
}

# Optional: Use custom difficulty ratios
level_ratios = [0.2, 0.2, 0.6]  # Easy, Medium, Hard

# Generate custom dataset
generator.generate_all_datasets(
    total_samples=100,
    type_ratios=custom_ratios,
    plot_level_ratios=level_ratios
)
```

## Output Format

The generated dataset will be saved in the `reconstruction_dataset` directory:

```
reconstruction_dataset/
├── data.json           # Dataset file
├── images/             # Visualization images
│   └── reconstruction_*.png
└── states/            # State files
    └── reconstruction_*.json
```

### Dataset Format

Each question entry contains the following fields:
- data_id: Data identifier
- qa_type: Question type (StateInfo/ActionOutcome/StrategyOptimization/TransitionPath)
- question_id: Question number
- question_description: Question type description
- image: Image path
- state: State file path
- plot_level: Structure difficulty level (Easy/Medium/Hard)
- qa_level: Question difficulty level (Easy/Medium/Hard)
- question: Question description
- answer: Answer
- analysis: Analysis
- options: Options (multiple choice questions only)

### State File Format (states/*.json)
```json
{
   "voxel_positions": [[1,1,1], [1,2,1], [2,2,1]],  // List of voxel positions in current structure
   "target_yz_projection": [                        // Y-Z projection (front view) matrix
      [1, 1, 0],  // z = 1 layer (bottom) projection
      [0, 1, 0],  // z = 2 layer (middle) projection
      [1, 0, 0]   // z = 3 layer (top) projection
   ],
   "target_xz_projection": [                        // X-Z projection (side view) matrix
      [1, 1, 0],  // z = 1 layer (bottom) projection
      [1, 0, 0],  // z = 2 layer (middle) projection
      [0, 0, 1]   // z = 3 layer (top) projection
   ],
   "remaining_voxels": 2                            // Number of remaining available voxels
}
```
- voxel_positions: List where each element is an [x,y,z] coordinate representing a voxel position in the current structure
- target_yz_projection: 3x3 matrix representing the front view projection (viewed from negative X-axis)
   * Each row represents a z-coordinate layer (from top to bottom: z = 3, 2, 1)
   * Elements in each row represent y-coordinates (from left to right: y = 1, 2, 3)
   * 1 indicates visible in projection, 0 indicates not visible
- target_xz_projection: 3x3 matrix representing the side view projection (viewed from positive Y-axis)
   * Each row represents a z-coordinate layer (from top to bottom: z = 3, 2, 1)
   * Elements in each row represent x-coordinates (from left to right: x = 1, 2, 3)
   * 1 indicates visible in projection, 0 indicates not visible
- remaining_voxels: Integer indicating the number of voxels that can still be added

## Notes

1. Generated question count should be reasonable, recommended at least 1 question per type
2. Sum of question type ratios must equal 1
3. Sum of difficulty level ratios must equal 1
4. Images and state files are automatically saved in the `reconstruction_dataset` directory
5. Parameters can be adjusted to control ratios and difficulty of different question types
