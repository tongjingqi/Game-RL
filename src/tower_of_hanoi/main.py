"""Generate the Tower of Hanoi GameQA example dataset deterministically.

Usage: python main.py
Outputs 15 boards and 60 QA entries under tower_of_hanoi_dataset_example/.
"""

import json
import os
import random
import shutil

from tower_of_hanoi import (
    GAME_RULES,
    TASK_META,
    build_q1,
    build_q2,
    build_q3,
    build_q4,
    generate_board,
    render_board,
)


SEED = 20260723
NUM_IMAGES = 15
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "tower_of_hanoi_dataset_example"
)
Q1_VARIANTS = ("count", "top", "largest", "list")
Q2_VARIANTS = ("count", "top")


def _question_text(body, options):
    option_lines = "\n".join(f"[{i}] {option}" for i, option in enumerate(options, 1))
    return f"{GAME_RULES}\n\n{body}\n\nOptions:\n{option_lines}"


def _build_board_qas(rng, state, board_index):
    """Build exactly one QA for each of the four task templates."""
    q1_variant = Q1_VARIANTS[board_index % len(Q1_VARIANTS)]
    q2_variant = Q2_VARIANTS[board_index % len(Q2_VARIANTS)]
    q4_variant = "first" if board_index % 5 in (0, 2) else "minimum"

    q1 = build_q1(state, rng, q1_variant)
    q2 = build_q2(state, rng, q2_variant)
    q3 = build_q3(state, rng)
    q4, target_peg = build_q4(state, rng, q4_variant)
    if any(qa is None for qa in (q1, q2, q3, q4)):
        return None, None
    return [q1, q2, q3, q4], target_peg


def main(output_dir=OUTPUT_DIR):
    rng = random.Random(SEED)
    os.makedirs(output_dir, exist_ok=True)
    for subdir in ("images", "states"):
        path = os.path.join(output_dir, subdir)
        if os.path.isdir(path):
            shutil.rmtree(path)
        os.makedirs(path)

    entries = []
    for board_index in range(NUM_IMAGES):
        plot_level = ("Easy", "Medium", "Hard")[board_index // 5]
        num_disks = 3 + board_index // 5

        while True:
            state = generate_board(num_disks, rng)
            qas, target_peg = _build_board_qas(rng, state, board_index)
            if qas is not None:
                break
        state["target_peg"] = target_peg

        board_id = board_index + 1
        image_rel = f"images/board_{board_id:05d}.png"
        state_rel = f"states/board_{board_id:05d}.json"
        render_board(state, os.path.join(output_dir, image_rel))
        with open(os.path.join(output_dir, state_rel), "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)

        for question_id, qa in enumerate(qas, 1):
            body, analysis, options, answer, description = qa
            qa_type, qa_level = TASK_META[question_id]
            entries.append(
                {
                    "data_id": f"tower_of_hanoi-mcq-{len(entries) + 1:05d}",
                    "image": image_rel,
                    "state": state_rel,
                    "plot_level": plot_level,
                    "qa_level": qa_level,
                    "qa_type": qa_type,
                    "question_id": question_id,
                    "question_description": description,
                    "question": _question_text(body, options),
                    "answer": answer,
                    "analysis": analysis,
                    "options": options,
                }
            )

    with open(os.path.join(output_dir, "data.json"), "w", encoding="utf-8") as handle:
        json.dump(entries, handle, ensure_ascii=False, indent=2)

    print(f"Generated {len(entries)} QA entries over {NUM_IMAGES} images.")
    for question_id in sorted(TASK_META):
        count = sum(entry["question_id"] == question_id for entry in entries)
        print(f"  task {question_id} ({TASK_META[question_id][0]}): {count} entries")


if __name__ == "__main__":
    main()
