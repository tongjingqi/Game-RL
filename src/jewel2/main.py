# main.py

import json
import random
import os
from chessboard import Chessboard
from randomizer import SpecialRandom
from level import Level
from image_generator import generate_jewel2_image
from QA_generator import generate_jewel2_QA

VALID_QA_TYPES = {"StateInfo", "ActionOutcome", "TransitionPath", "StrategyOptimization"}

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


def main():
    # Define plot_levels and corresponding chessboard sizes
    plot_levels = [
        {"plot_level": "Easy", "size": 4},
        {"plot_level": "Medium", "size": 5},
        {"plot_level": "Hard", "size": 6}
    ]

    # Number of samples to generate per plot_level
    num_samples_per_level = 2  # Adjust as needed

    # Create dataset directory
    dataset_dir = "jewel2_dataset_example"  # Adjust as needed
    os.makedirs(dataset_dir, exist_ok=True)

    # Create subdirectories
    output_image_dir = os.path.join(dataset_dir, "images")
    output_state_dir = os.path.join(dataset_dir, "states")
    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(output_state_dir, exist_ok=True)

    vqa_data = []  # To store generated VQA data

    # Initialize question_id counters per plot_level
    question_id_counters = { "Easy": 1, "Medium":1, "Hard":1 }
    
    sample_index = 1  # Initialize sample index

    for plot in plot_levels:
        plot_level = plot["plot_level"]
        size = plot["size"]

        for i in range(1, num_samples_per_level + 1):
            # Initialize random generator
            randomizer = SpecialRandom()

            # Initialize chessboard with dynamic size
            chessboard = Chessboard(randomizer, size=size)

            # Initialize level
            level = Level(chessboard)

            # Randomly initialize starting score
            level.total_cleared = random.randint(0, 100)

            # Generate chessboard image
            image_filename = f"{str(sample_index).zfill(5)}.png"  # Sequential numbering
            image_path = os.path.join("images", image_filename)  # Relative path
            generate_jewel2_image(
                chessboard.chessboard,
                level.total_cleared,
                font_path="font/Arial.ttf",
                output_path=os.path.join(output_image_dir, image_filename)
            )

            # Save game state
            state_filename = f"{str(sample_index).zfill(5)}.json"  # Sequential numbering
            state_path = os.path.join("states", state_filename)  # Relative path
            level.save_game_state(filename=state_filename, directory=output_state_dir)

            for j in range(0,10):   # Ten questions per image
                # Generate question and answer
                qa_type, qa_level, question, question_id, question_description, answer, analysis, options = generate_jewel2_QA(level=level, num=j, size=size)

                # Ensure qa_type is in VALID_QA_TYPES
                if qa_type not in VALID_QA_TYPES:
                    # Map or adjust qa_type to VALID_QA_TYPES
                    if qa_type == "Recognizing":
                        qa_type_mapped = "StateInfo"
                    elif qa_type == "Reasoning":
                        qa_type_mapped = "ActionOutcome"
                    elif qa_type == "Strategy":
                        qa_type_mapped = "StrategyOptimization"
                    else:
                        qa_type_mapped = "StateInfo"  # Default value
                    qa_type = qa_type_mapped

                # Generate unique data_id
                data_id = f"jewel2-train-{str(sample_index).zfill(5)}-{j}"

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
