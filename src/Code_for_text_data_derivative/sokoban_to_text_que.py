import json
import os

def read_json(file_path):
    """Read and parse a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def grid_to_text(grid):
    """Convert grid data to a text representation."""
    symbols = {
        0: '.',   # Empty
        1: '#',   # Wall
        2: 'B',   # Box
        3: 'T',   # Target
        4: '*',   # Box on target
        5: 'P',   # Player
        6: '+'    # Player on target
    }
    
    text = []
    for row in grid:
        row_text = ''.join([symbols[cell] for cell in row])
        text.append(row_text)
    return '\n'.join(text)

def state_to_text(state_data):
    """Convert state data to a comprehensive text description."""
    text = "SOKOBAN BOARD DESCRIPTION:\n\n"
    
    # Grid representation
    text += "GRID REPRESENTATION:\n"
    text += "# = Wall, . = Empty space, P = Player, B = Box, T = Target, * = Box on target, + = Player on target\n\n"
    text += grid_to_text(state_data["grid"]) + "\n\n"
    
    # Player position
    player = state_data["player"]
    text += f"PLAYER POSITION: (x={player['y']}, y={player['x']})\n\n"
    
    # Box positions
    text += "BOX POSITIONS:\n"
    for i, box in enumerate(state_data["boxes"], 1):
        text += f"Box {i}: (x={box['y']}, y={box['x']})\n"
    text += "\n"
    
    # Target positions
    text += "TARGET POSITIONS:\n"
    for i, target in enumerate(state_data["targets"], 1):
        text += f"Target {i}: (x={target['y']}, y={target['x']})\n"
    text += "\n"
    
   
    # Movement explanation
    text += "MOVEMENT RULES:\n"
    text += "- The player can move Up, Right, Down, or Left if there is no wall in the way.\n"
    text += "- The player can push boxes (one at a time) if there is an empty space behind the box.\n"
    text += "- The goal is to push all boxes onto target positions.\n"
    
    return text

def update_question_text(question_text):
    """Update question text to refer to the text description instead of an image."""
    # Replace any image references with text references
    question_text = question_text.replace("As shown in the figure", "As described in the text")
    question_text = question_text.replace("in the figure", "in the text representation")
    question_text = question_text.replace("from the figure", "from the text description")
    
    return question_text

def process_dataset():
    """Process the dataset to create text-based versions of the questions."""
    # Check if we're in the right directory
    if not os.path.exists("data.json"):
        print("Error: data.json not found in the current directory.")
        print("Please make sure you're running this script from the dataset directory.")
        return
    
    # Load the dataset
    data = read_json("data.json")
    processed_data = []
    
    # Process each entry
    for entry in data:
        try:
            # Get state path and load state data
            state_path = entry.get("state")
            if not state_path:
                print(f"Warning: No state path found for entry {entry.get('data_id')}")
                continue
                
            state_data = read_json(state_path)
            
            # Convert state to text
            state_text = state_to_text(state_data)
            
            # Create a new entry with the modified question
            new_entry = entry.copy()
            new_entry["question"] = state_text + "\n" + update_question_text(entry["question"])
            
            # Remove the image and state references
            if "image" in new_entry:
                del new_entry["image"]
            if "state" in new_entry:
                del new_entry["state"]
                
            processed_data.append(new_entry)
            
        except Exception as e:
            print(f"Error processing entry {entry.get('data_id')}: {str(e)}")
    
    # Save the processed data
    with open("data_text.json", "w") as f:
        json.dump(processed_data, f, indent=4)
    
    print(f"Successfully processed {len(processed_data)} entries. Saved to data_text.json")

if __name__ == "__main__":
    process_dataset()