import json
import os

def read_json(file_path):
    """Read and parse a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)
    
def spider_state_to_text(state_data):
    """Convert spider state data to a text description."""
    stock = state_data["stock"]
    waste = state_data["waste"]

    for cards in stock:
        if cards["faceUp"]  == False:
            cards["code"] = ""
            cards["suit"] = ""
            cards["rank"] = ""
    
    for piles in waste:
        for cards in piles:
            if cards["faceUp"]  == False:
                cards["code"] = ""
                cards["suit"] = ""
                cards["rank"] = ""
    
    # Create a text representation of the grid
    # grid_text = "STOCK PILES:" + '\n'.join([''.join(str(cards)) for cards in stock])

    grid_text = "WASTE PILES: "
    for i in range(len(waste)):
        grid_text += "waste pile " + str(i) + ": " +'\t'.join([''.join(str(cards)) for cards in waste[i]]) + "\n"
    
    # Create a human-readable representation
    text = "SPIDER BOARD DESCRIPTION:\n\n"
    text += "There are three types of piles in the game: stock piles, waste piles and foundation piles.\n\n"
    text += "Each of the piles has cards in it, and the cards are either face up or face down.\n\n"
    text += "When a card is face up, you can see the suit and rank of the card.\n\n"
    text += "When a card is face down, you cannot see any of the information about it.\n\n"
    text += "The cards in stock piles are all face down. So they are not shown in the following statement.\n\n"
    text += "The foundation piles are initially empty, so they are also not shown in the following statement.\n\n"
    text += "The states of cards in the stock piles are as follows:\n\n"
    text += grid_text + "\n\n"
    
    return text

def process_dataset():
    """Process the spider dataset to convert image references to text descriptions."""
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
                print(f"Warning: No state path found for entry {entry["data_id"]}")
                continue
                
            state_data = read_json(state_path)
            
            # Convert spider state to text
            text = spider_state_to_text(state_data)
            
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