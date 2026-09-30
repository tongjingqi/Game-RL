# main.py

import json
import random
import os
from chessboard import Chessboard
from randomizer import SpecialRandom
from level import Level
from image_generator import generate_jewel2_image
from QA_generator import generate_jewel2_QA, has_unique_best_command

VALID_QA_TYPES = {"Target Perception", "State Prediction", "Strategy Optimization"}

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


def create_level(size):
    """A random board of the given size with a random starting score."""
    # Initialize random generator
    randomizer = SpecialRandom()

    # Initialize chessboard with dynamic size
    chessboard = Chessboard(randomizer, size=size)

    # Initialize level
    level = Level(chessboard)

    # Randomly initialize starting score
    level.total_cleared = random.randint(0, 100)
    return level


def save_level(level, stem, output_image_dir, output_state_dir):
    """Render the board and save its state; returns the image and state paths relative to the dataset."""
    image_filename = f"{stem}.png"
    generate_jewel2_image(
        level.chessboard.chessboard,
        level.total_cleared,
        font_path="font/Arial.ttf",
        output_path=os.path.join(output_image_dir, image_filename)
    )
    state_filename = f"{stem}.json"
    level.save_game_state(filename=state_filename, directory=output_state_dir)
    return f"images/{image_filename}", f"states/{state_filename}"  # dataset paths always use '/'


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
            level = create_level(size)

            # Generate chessboard image and save game state (sequential numbering)
            image_path, state_path = save_level(level, str(sample_index).zfill(5), output_image_dir, output_state_dir)

            for j in range(0,10):   # Ten questions per image
                question_level, question_image, question_state = level, image_path, state_path
                if j == 9 and not has_unique_best_command(level, size):
                    # q6 is a fill-in-the-blank with a single gold command; when several commands tie
                    # for the most eliminations, it is asked on a board of its own ("<index>_q6")
                    question_level = create_level(size)
                    while not has_unique_best_command(question_level, size):
                        question_level = create_level(size)
                    question_image, question_state = save_level(
                        question_level, f"{str(sample_index).zfill(5)}_q6", output_image_dir, output_state_dir)

                # Generate question and answer
                qa_type, qa_level, question, question_id, question_description, answer, analysis, options = generate_jewel2_QA(level=question_level, num=j, size=size)

                # Ensure qa_type is in VALID_QA_TYPES
                if qa_type not in VALID_QA_TYPES:
                    # Map or adjust qa_type to VALID_QA_TYPES
                    if qa_type == "Recognizing":
                        qa_type_mapped = "Target Perception"
                    elif qa_type in {"Reasoning", "ActionOutcome", "TransitionPath"}:
                        qa_type_mapped = "State Prediction"
                    elif qa_type == "Strategy":
                        qa_type_mapped = "Strategy Optimization"
                    else:
                        qa_type_mapped = "Target Perception"  # Default value
                    qa_type = qa_type_mapped

                # Generate unique data_id
                data_id = f"jewel2-train-{str(sample_index).zfill(5)}-{j}"

                # Generate VQA entry
                vqa_entry = generate_vqa_entry(
                    data_id,
                    qa_type,
                    question_id,
                    question_description,
                    question_image,
                    question_state,
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
