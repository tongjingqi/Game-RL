import json
import os

def read_json(file_path):
    """Read and parse a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)
    
def pacman_state_to_text(state_data):
    """Convert pacman state data to a text description."""
    grid_size = state_data["grid_size"]
    board = [['' for _ in range(grid_size)] for _ in range(grid_size)]
    walls = state_data["walls"]
    beans = state_data["beans"]
    pacman_position = state_data["pacman_position"]
    pacman_direction = state_data["direction"]
    ghosts = state_data["ghosts"]
    for ghost in ghosts:
        if ghost["name"] == "Blinky":
            blinky = ghost
        elif ghost["name"] == "Pinky":
            pinky = ghost

    board[pacman_position[0]][pacman_position[1]] = 'Pacman'
    board[blinky["position"][0]][blinky["position"][1]] = 'Blinky'
    board[pinky["position"][0]][pinky["position"][1]] = 'Pinky'

    for wall in walls:
        x, y = wall
        board[x][y] = 'wall'
    
    for bean in beans:
        x, y = bean
        board[x][y] = 'bean'

    # Create a text representation of the grid
    grid_text = "BOARD: " + '\n'.join([''.join(str(row)) for row in board])
    grid_text += "PACMAN DIRECTION: " + pacman_direction + "\n"
    grid_text += "PACMAN POSITION: " + str(pacman_position) + "\n"
    grid_text += "BLINKY POSITION: " + str(blinky["position"]) + "\n"
    grid_text += "PINKY POSITION: " + str(pinky["position"]) + "\n"
    
    # Create a human-readable representation
    text = "PACMAN BOARD DESCRIPTION:\n\n"
    text += "The pacman grid has dimensions (rows, columns): " + f"({grid_size}, {grid_size}).\n"
    text += "Each cell in the grid can be one of the following:\n"
    text += "  - 'Pacman' representing Pacman's position.\n"
    text += "  - 'Blinky' representing Blinky's position.\n"
    text += "  - 'Pinky' representing Pinky's position.\n"
    text += "  - 'wall' representing a wall.\n"
    text += "  - 'bean' representing a bean.\n\n"
    text += "The grid and positions are represented as follows:\n"
    text += " [ " + grid_text + " ] " + "\n\n"
    
    return text

def process_dataset():
    """Process the pacman dataset to convert image references to text descriptions."""
    # Check if we're in the right directory
    if not os.path.exists("data.json"):
        print("Error: data.json not found in the current directory.")
        print("Please make sure you're running this script from the dataset directory.")
        return
    
    # Load the dataset
    data = read_json('data.json')
    processed_data = []

        # Process each entry
    for entry in data:
        try:
            # Get state path and load state data
            state_path = entry["state"]
            if not state_path:
                print(f"Warning: No state path found for entry {entry['data_id']}")
                continue
                
            state_data = read_json(state_path)
            
            # Convert pacman state to text
            text = pacman_state_to_text(state_data)
            
            # Create a new entry with the modified question
            new_entry = entry.copy()
            new_entry["question"] = text + entry["question"]

            # Remove the image and state references
            if "image" in new_entry:
                del new_entry["image"]
            """ if "state" in new_entry:
                del new_entry["state"] """
                
            processed_data.append(new_entry)
        
        except Exception as e:
            print(f"Error processing entry {entry.get('data_id')}: {str(e)}")
    
    with open('data_text.json', 'w') as f:
        json.dump(processed_data, f, indent=4)

    print(f"Successfully processed {len(processed_data)} entries. Saved to data_text.json")

if __name__ == "__main__":
    process_dataset()