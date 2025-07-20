import json
import os
import re

def read_json(file_path):
    """Read and parse a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def cube_state_to_text(state_data):
    """Convert cube state data to a text description."""
    faces = state_data["faces"]
    colors = state_data["colors"]
    
    # Create a text representation of each face
    faces_text = {}
    for face_name, face_data in faces.items():
        face_text = []
        for row in face_data:
            # Convert color indices to actual color names
            color_row = [colors[idx] for idx in row]
            face_text.append(color_row)
        faces_text[face_name] = face_text
    
    # Create a human-readable representation
    text = "RUBIK'S CUBE STATE DESCRIPTION:\n\n"
    text += "The Rubik's cube has six faces: Upper (U), Down (D), Left (L), Right (R), Front (F), and Back (B).\n"
    text += "Each face is a 3x3 grid with coordinates (row, column) starting from (0,0) at the top-left.\n"
    text += "The colors are represented as follows: " + ", ".join([f"{colors[i]}" for i in range(len(colors))]) + ".\n\n"
    
    # Dictionary mapping face abbreviations to full names
    face_names = {
        'U': 'Upper face',
        'D': 'Down face',
        'L': 'Left face',
        'R': 'Right face',
        'F': 'Front face',
        'B': 'Back face'
    }
    
    # Display each face with its colors
    for face, matrix in faces_text.items():
        text += f"{face_names[face]} ('{face}'):\n"
        for i, row in enumerate(matrix):
            text += f"  Row {i}: " + ", ".join([f"{color}" for color in row]) + "\n"
        text += "\n"
    
    # Add explanation about move notation
    text += "MOVE NOTATION:\n"
    text += "An uppercase letter indicates which face to rotate ('F' for Front, 'B' for Back, 'L' for Left, 'R' for Right, 'U' for Upper, 'D' for Down).\n"
    text += "A prime symbol (') after the letter denotes counterclockwise rotation, while no prime symbol denotes clockwise rotation.\n\n"
    
    return text

def update_question_text(question_text, cube_text):
    """Update the question to reference the text representation instead of the image."""
    
    # Replace image references with text references
    question_text = re.sub(r"As shown in the figure", "As described in the text", question_text)
    question_text = re.sub(r"shown in the bottom left corner", "explained in the description", question_text)
    
    # If the question starts with "Rules: " remove that part since we've included the rules in our text description
    if question_text.startswith("Rules: "):
        question_text = question_text.split("Rules: ", 1)[1]
    
    return question_text

def process_dataset():
    """Process the entire dataset to create a text-based version."""
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
            
            # Convert cube state to text
            cube_text = cube_state_to_text(state_data)
            
            # Create a new entry with the modified question
            new_entry = entry.copy()
            new_entry["question"] = cube_text + update_question_text(entry["question"], cube_text)
            
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