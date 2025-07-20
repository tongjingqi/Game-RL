import json
import os

def read_json(file_path):
    """Read and parse a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)
    
def minesweeper_state_to_text(state_data):
    """Convert minesweeper state data to a text description."""
    mine_board = state_data["mine_board"]
    rows = state_data["rows"]
    cols = state_data["cols"]
    revealed = state_data["revealed"]
    flagged = state_data["flagged"]

    for i in range(rows):
        for j in range(cols):
            if not revealed[i][j]:
                mine_board[i][j] = str(mine_board[i][j])
            elif flagged[i][j]:
                mine_board[i][j] = 'F'
            else:
                mine_board[i][j] = '.'
    
    # Create a text representation of the grid
    grid_text = '\n'.join([''.join(str(row)) for row in mine_board])
    
    # Create a human-readable representation
    text = "MINESWEEPER BOARD DESCRIPTION:\n\n"
    text += "The Minesweeper grid has dimensions (rows, columns): " + f"({rows}, {cols}).\n"
    text += "Each cell in the grid can be one of the following:\n"
    text += "  - A digit from 0 to 8 representing the number of mines in adjacent cells.\n"
    text += "  - An 'F' indicating a flagged cell.\n"
    text += "  - A '.' indicating an unrevealed cell.\n\n"
    text += "The grid is represented as follows:\n"
    text += " [ " + grid_text + " ] " + "\n\n"
    
    return text

def process_dataset():
    """Process the Minesweeper dataset to convert image references to text descriptions."""
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
            
            # Convert minesweeper state to text
            text = minesweeper_state_to_text(state_data)
            
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