# main.py

import json
import random
import os
from model import Model
from image_exporter import ImageExporter
from QA_generator import generate_spider_QA

def generate_vqa_entry(data_id, qa_type, question_id, question_description, image_path, state_path, plot_level, qa_level, question, answer, analysis, options=None):
    """
    Generate VQA data entries with fields in the specified order.
    """
    entry = {
        "data_id": data_id,
        "qa_type": qa_type,
        "question_id": question_id,
        "question_description": question_description,
        "image": image_path,
        "state": state_path,
        "plot_level": plot_level,
        "qa_level": qa_level,
        "question": question,
        "answer": answer,
        "analysis": analysis,
    }
    if options:
        entry["options"] = options
    return entry

def apply_random_deals(model_instance: Model, max_deals=3):
    """
    Randomly perform 0 to max_deals deal operations on the model.
    """
    num_deals = random.randint(0, max_deals)
    print(f"Applying {num_deals} random deal(s).")
    for _ in range(num_deals):
        if model_instance.canDeal():
            model_instance.dealUp()
        else:
            print("Cannot deal anymore.")
            break

def apply_random_moves(model_instance: Model, max_moves=3):
    """
    Randomly perform 0 to max_moves legal moves on the model.
    """
    num_moves = random.randint(0, max_moves)
    print(f"Applying {num_moves} random move(s).")
    for _ in range(num_moves):
        possible_moves = model_instance.get_all_possible_moves()
        if not possible_moves:
            print("No possible moves available.")
            break
        # Select a random move from the possible moves
        move = random.choice(possible_moves)
        src_pile_index, dest_pile_index, card_idx = move
        if dest_pile_index >= model_instance.num_waste:
            dest_type = "foundation"
            foundation_index = dest_pile_index - model_instance.num_waste
            print(f"Moving from waste pile {src_pile_index} (starting at card index {card_idx}) to foundation pile {foundation_index}.")
        else:
            dest_type = f"waste pile {dest_pile_index}"
            print(f"Moving from waste pile {src_pile_index} (starting at card index {card_idx}) to waste pile {dest_pile_index}.")
        # Perform the move
        model_instance.grab(src_pile_index, card_idx)
        if dest_pile_index >= model_instance.num_waste:
            # Moving to foundation
            foundation_index = dest_pile_index - model_instance.num_waste
            model_instance.selectionToFoundation(foundation_index)
        else:
            # Moving to another waste pile
            model_instance.selectionToWaste(dest_pile_index)
        # After moving, flip the top card if necessary (handled within Model methods)

def main():
    # Define plot_levels and corresponding waste pile counts
    plot_levels = [
        {"plot_level": "Easy", "num_waste": 8},
        {"plot_level": "Medium", "num_waste": 9},
        {"plot_level": "Hard", "num_waste": 10}
    ]

    # Number of samples to generate per plot_level
    num_samples_per_level = 1  # Adjust as needed

    # Create dataset directory
    dataset_dir = "spider_solitaire_dataset_example"  # Adjust as needed
    os.makedirs(dataset_dir, exist_ok=True)

    # Create subdirectories
    output_image_dir = os.path.join(dataset_dir, "images")
    output_state_dir = os.path.join(dataset_dir, "states")
    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(output_state_dir, exist_ok=True)

    vqa_data = []  # To store generated VQA data

    sample_index = 1  # Initialize sample index

    # Set the output image path and name
    card_dir = 'cards'  # Ensure this directory contains all card images

    for plot in plot_levels:
        plot_level = plot["plot_level"]
        num_waste = plot["num_waste"]

        for i in range(1, num_samples_per_level + 1):
            model_instance = Model(num_waste=num_waste)

            # Step 1: Apply random deals (0 to 3 times)
            apply_random_deals(model_instance, max_deals=3)

            # Step 2: Apply random moves (0 to 3 steps)
            apply_random_moves(model_instance, max_moves=3)

            # Generate chessboard image
            image_filename = f"board_{str(sample_index).zfill(5)}.png"  # Sequential numbering
            image_path = os.path.join("images", image_filename)  # Relative path
            output_path = os.path.join(output_image_dir, image_filename)

            exporter = ImageExporter(model_instance, card_dir=card_dir, output_path=output_path)
            exporter.generate_image()

            # Save game state
            state_filename = f"board_{str(sample_index).zfill(5)}.json"  # Sequential numbering
            state_path = os.path.join("states", state_filename)  # Relative path
            model_instance.save_to_json(file_path=output_state_dir, file_name=state_filename)
            
            for j in range(0, 10):   # Ten questions per image
                # Generate question and answer
                qa_type, qa_level, question, question_id, question_description, answer, analysis, options = generate_spider_QA(model_instance, num=j, num_waste=num_waste)

                # Generate unique data_id
                data_id = f"spider_solitaire-train-{str(sample_index).zfill(5)}-{j}"

                # Generate VQA entry
                vqa_entry = generate_vqa_entry(
                    data_id,
                    qa_type,
                    question_id,
                    question_description,
                    image_path,
                    state_path,
                    plot_level,
                    qa_level,
                    question,
                    answer,
                    analysis,
                    options
                )
                vqa_data.append(vqa_entry)
        
            sample_index += 1  # Increment sample index

    # Save VQA data to 'data.json'
    output_json_path = os.path.join(dataset_dir, "data.json")
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(vqa_data, json_file, indent=4, ensure_ascii=False)

    print(f"VQA data generation is complete. A total of {len(vqa_data)} records have been generated and saved to {output_json_path}.")

if __name__ == "__main__":
    main()
