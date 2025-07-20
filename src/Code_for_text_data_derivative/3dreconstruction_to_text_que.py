import json
import os

def format_3d_array(array):
    """Format 3D array with annotations"""
    result = []
    # Iterate through x (fixed x-planes)
    for x in range(3):
        layer = []
        # For each x, create a y-z plane
        for y in range(3):
            # For each y, get values along z
            row = [array[x][y][z] for z in range(3)]
            layer.append(row)
        # Format each x-plane as a string with annotations
        layer_str = f"[\n      {layer[0]},  # y=1, z increases right (1->3)\n      {layer[1]},  # y=2, z increases right (1->3)\n      {layer[2]}   # y=3, z increases right (1->3)\n    ]  # x={x+1}"
        result.append(layer_str)
    return "[\n    " + ",\n    ".join(result) + "\n  ]"

def format_projection(matrix, is_front_view=True):
    """Format projection matrix with annotations"""
    result = []
    for i, row in enumerate(matrix):
        z = 3 - i  # z coordinate (top to bottom)
        if is_front_view:
            result.append(f"    {row}  # z={z}, x increases right (1->3)")
        else:
            result.append(f"    {row}  # z={z}, y increases right (1->3)")
    return "[\n" + ",\n".join(result) + "\n  ]"

def format_state_json(state_json):
    """Format the entire state JSON with custom formatting"""
    current_structure = format_3d_array(state_json["current_structure"])
    target_front = format_projection(state_json["target_front_view"], True)
    target_side = format_projection(state_json["target_side_view"], False)
    
    return f"""{{
  "current_structure": {current_structure},
  
  "target_front_view": {target_front},
  
  "target_side_view": {target_side},
  
  "remaining_voxels": {state_json["remaining_voxels"]}
}}"""

def convert_to_3d_array(voxel_positions):
    # Initialize 3x3x3 array with zeros (x,y,z order)
    array_3d = [[[0 for _ in range(3)] for _ in range(3)] for _ in range(3)]
    
    # Fill in voxels
    for x, y, z in voxel_positions:
        # Convert 1-based to 0-based indexing
        array_3d[x-1][y-1][z-1] = 1  # Note the x,y,z order
        
    return array_3d

def transform_state_to_text(data_json_path):
    # Read the original data.json file
    with open(data_json_path, 'r') as f:
        data_items = json.load(f)
    
    results = []
    
    # Process each item in the data.json file
    for item in data_items:
        # Get the state file path
        state_path = item["state"]
        
        # Check if the state file exists
        if not os.path.exists(state_path):
            print(f"Warning: State file not found at {state_path}")
            continue
        
        # Read the state file
        with open(state_path, 'r') as f:
            state_data = json.load(f)
        
        # Extract state information
        voxel_positions = state_data["voxel_positions"]
        target_yz = list(reversed(state_data["target_yz_projection"]))  # Reverse order (bottom to top)
        target_xz = list(reversed(state_data["target_xz_projection"]))  # Reverse order (bottom to top)
        remaining_voxels = state_data["remaining_voxels"]
        
        # Convert voxel positions to 3D array
        voxel_array = convert_to_3d_array(voxel_positions)
        
        # Create state description
        state_json = {
            "current_structure": voxel_array,  # 3D array representation (x,y,z order)
            "target_front_view": target_yz,    # Y-Z projection (front view), top to bottom
            "target_side_view": target_xz,     # X-Z projection (side view), top to bottom
            "remaining_voxels": remaining_voxels
        }
        
        # Create state description text
        state_description = """
Instead of image, the current state of the 3D reconstruction game is described in JSON format as follows:
{
  "current_structure": 3D array (3x3x3) representing the voxel structure, where:
    - First index (x): front to back (0-2)
    - Second index (y): left to right (0-2)
    - Third index (z): bottom to top (0-2)
    - Value 1 indicates presence of a voxel, 0 indicates empty space
    - Position [0,0,0] is at the front-left-bottom corner
    - Each x-plane shows a y-z slice: rows are y, columns are z
  
  "target_front_view": Target front view (Y-Z projection) matrix, 3 rows from top to bottom, each row has 3 numbers from left to right:
    - Each row represents a fixed z-coordinate (z=3,2,1 from top to bottom)
    - Each column represents a y-coordinate (y=1,2,3 from front to back)
    - 0 indicates no voxel along that line of sight (looking from negative x direction)
    - 1 indicates presence of voxel(s) along that line of sight
  
  "target_side_view": Target side view (X-Z projection) matrix, 3 rows from top to bottom, each row has 3 numbers from left to right:
    - Each row represents a fixed z-coordinate (z=3,2,1 from top to bottom)
    - Each column represents an x-coordinate (x=1,2,3 from left to right)
    - 0 indicates no voxel along that line of sight (looking from positive y direction)
    - 1 indicates presence of voxel(s) along that line of sight
  
  "remaining_voxels": Number of voxels available for placement
}

The specific state data:
""" + format_state_json(state_json) + "\n"

        # Split question into rules and actual question
        if "Game Rules:" in item["question"]:
            parts = item["question"].split("Question:", 1)
            if len(parts) == 2:
                rules = parts[0].strip()
                question = "Question:" + parts[1].strip()
                # Insert state description between rules and question
                item["question"] = rules + "\n" + state_description + "\n" + question
            else:
                # If can't split properly, append at the end
                item["question"] = item["question"] + "\n" + state_description
        else:
            # If no Game Rules found, append at the beginning
            item["question"] = state_description + "\n" + item["question"]
            
        results.append(item)

    return results

def save_results(results, output_path):
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    data_json_path = "data.json"
    output_path = "data_text.json"
    results = transform_state_to_text(data_json_path)
    save_results(results, output_path)
    
    print(f"Transformed {len(results)} state(s) to text format and saved to {output_path}") 