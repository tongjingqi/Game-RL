# main.py

from minesweeper import Minesweeper  # Import Minesweeper logic
from generate_board import generate_board_image  # Import board generation logic
from generate_question_and_answer import generate_question_and_answer
import random
import json
import os

def generate_vqa_entry(data_id, question_id, qa_level, image_path, state_path, plot_level, qa_type, question, question_description, answer, analysis, options=None):
    """
    Generate a VQA dataset entry
    """

    vqa_entry = {
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
        "analysis": analysis
    }

    # Add the 'options' field only if it exists
    if options:
        vqa_entry["options"] = options

    return vqa_entry

# Define a mapping between qa_type and difficulty level
qa_type_difficulty_map = {
    "StateInfo": "Easy",
    "ActionOutcome": "Easy",
    "TransitionPath": "Easy",
    "StrategyOptimization": "Hard"
}

def main():
    # Create output directories
    output_dir = "minesweeper_dataset_example"
    output_image_dir = os.path.join(output_dir, "images")
    output_state_dir = os.path.join(output_dir, "states")
    data_json_path = os.path.join(output_dir, "data.json")

    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(output_state_dir, exist_ok=True)

    vqa_data = []  # Used to store generated VQA data

    # Set the number of samples to generate
    num_samples = 10  # Set the number of batches to generate

    # Define different plot_level configurations for board sizes and number of mines
    plot_levels = {
        "Easy": {"rows": 4, "cols": 4, "mines": 3},
        "Medium": {"rows": 5, "cols": 5, "mines": 5},
        "Hard": {"rows": 6, "cols": 6, "mines": 8}
    }
    plot_level_order = ["Easy", "Medium", "Hard"]  # Define the generation order

    image_counter = 1  # Initialize the counter for images and state files

    for i in range(1, num_samples + 1):
        for plot_level in plot_level_order:
            config = plot_levels[plot_level]
            rows, cols, mines = config["rows"], config["cols"], config["mines"]

            # Create a Minesweeper game object
            game = Minesweeper(rows, cols, mines)

            # Simulate a first click
            first_click_row, first_click_col = random.randint(0, rows - 1), random.randint(0, cols - 1)
            game.reveal(first_click_row, first_click_col)

            # Automatically flag mines, 2 to 4 flags
            max_flag_number = random.randint(2, 4)
            game.auto_flagger(max_flag_number)

            # Generate the board image
            image_filename = f"board_{str(image_counter).zfill(5)}.png"  # Sequential numbering
            image_path = os.path.join(output_image_dir, image_filename)
            board_image = generate_board_image(game)
            board_image.save(image_path)  # Save the generated image

            # Save the game state
            state_filename = f"board_{str(image_counter).zfill(5)}.json"  # Sequential numbering
            state_path = os.path.join(output_state_dir, state_filename)
            game.save_state(filename=state_filename, directory=output_state_dir)

            for j in range(0, 10):   # Each image generates 10 questions
                # Generate question and answer
                qa_type, qa_level, question, question_id, question_description, answer, analysis, options = generate_question_and_answer(game, j, plot_level)

                # Generate VQA entry
                data_id = f"minesweeper-train-{str(image_counter).zfill(5)}-{j}"

                vqa_entry = generate_vqa_entry(
                    data_id, question_id, qa_level, os.path.join("images", image_filename), os.path.join("states", state_filename), plot_level, qa_type, question, question_description, answer, analysis, options
                )
                vqa_data.append(vqa_entry)

            image_counter += 1  # Increment the counter

    # Save VQA data to JSON file
    with open(data_json_path, "w", encoding="utf-8") as json_file:
        json.dump(vqa_data, json_file, ensure_ascii=False, indent=4)

    print(f"VQA data generation completed. A total of {num_samples * 3} samples (3 difficulty levels per batch), each containing 10 questions, were generated, for a total of {num_samples * 3 * 10} records. Saved to {data_json_path}.")

if __name__ == "__main__":
    main()
