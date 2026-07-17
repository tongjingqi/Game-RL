"""Entry point: generate the dice_roll example dataset deterministically.

Usage: python main.py
Outputs to dice_roll_dataset_example/ (data.json, images/, states/).
"""

import json
import os
import random

from dice_roll import (
    TASK_DESCRIPTIONS,
    TASK_TYPES,
    build_task1,
    build_task2,
    build_task3,
    build_task4,
    generate_board,
    render_board,
)

SEED = 20260718
NUM_IMAGES = 15  # 5 Easy, 5 Medium, 5 Hard
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "dice_roll_dataset_example")

# task-1 sub-variants cycled over the 15 primary (+5 extra) entries
TASK1_VARIANTS = ["top", "front_left", "front_right", "pip_total", "die_cell", "star_cell"]
# task-2 sub-variants cycled over the 15 primary (+5 extra) entries
TASK2_VARIANTS = ["top", "front_left", "top", "final_cell", "top"]


def build_image_qas(rng, board, index, t4_unconstrained):
    """Build the 4 QA entries for one board. Returns (qas, state_extra)."""
    qas = []
    state_extra = {}

    need3 = index % 3 != 2   # task 3 on ~10 of 15 images
    need4 = index % 3 != 0   # task 4 on ~10 of 15 images

    # task 1 (always) + a second task-1 variant when task 3 is absent
    v1 = TASK1_VARIANTS[index % len(TASK1_VARIANTS)]
    qas.append(build_task1(rng, board, v1))
    if not need3:
        v1b = TASK1_VARIANTS[(index + 3) % len(TASK1_VARIANTS)]
        qas.append(build_task1(rng, board, v1b))

    # task 2 (always) + a second task-2 variant when task 4 is absent
    v2 = TASK2_VARIANTS[index % len(TASK2_VARIANTS)]
    qa2 = build_task2(rng, board, v2)
    state_extra["move_sequence"] = qa2.pop("_sequence")
    qas.append(qa2)
    if not need4:
        v2b = TASK2_VARIANTS[(index + 2) % len(TASK2_VARIANTS)]
        qa2b = build_task2(rng, board, v2b)
        state_extra["extra_move_sequence"] = qa2b.pop("_sequence")
        qas.append(qa2b)

    if need3:
        qa3 = None
        while qa3 is None:
            qa3 = build_task3(rng, board)
        qas.append(qa3)
    if need4:
        qas.append(build_task4(rng, board, t4_unconstrained))

    # order entries by question_id for readability
    qas.sort(key=lambda q: q["question_id"])
    return qas, state_extra


def main():
    rng = random.Random(SEED)
    images_dir = os.path.join(OUTPUT_DIR, "images")
    states_dir = os.path.join(OUTPUT_DIR, "states")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(states_dir, exist_ok=True)

    entries = []
    t4_count = 0
    for i in range(NUM_IMAGES):
        plot_level = ["Easy", "Medium", "Hard"][i // 5]
        need4 = i % 3 != 0
        # ~30% of task-4 entries drop the top-face constraint
        t4_unconstrained = need4 and (t4_count % 10) < 3
        # regenerate the board until task 4 (if needed on this image) is feasible
        while True:
            board = generate_board(rng, plot_level)
            if not need4:
                break
            probe_rng = random.Random(12345 + i)
            if build_task4(probe_rng, board, t4_unconstrained) is not None:
                break
        if need4:
            t4_count += 1

        board_id = i + 1
        image_rel = f"images/board_{board_id:05d}.png"
        state_rel = f"states/board_{board_id:05d}.json"
        render_board(board, os.path.join(OUTPUT_DIR, image_rel), rng)

        qas, state_extra = build_image_qas(rng, board, i, t4_unconstrained)
        board.update(state_extra)
        with open(os.path.join(OUTPUT_DIR, state_rel), "w") as f:
            json.dump(board, f, indent=2)

        for qa in qas:
            qid = qa["question_id"]
            qa_type, qa_level = TASK_TYPES[qid]
            entries.append({
                "data_id": f"dice_roll-mcq-{len(entries) + 1:05d}",
                "image": image_rel,
                "state": state_rel,
                "plot_level": plot_level,
                "qa_level": qa_level,
                "qa_type": qa_type,
                "question_id": qid,
                "question_description": TASK_DESCRIPTIONS[qid],
                "question": qa["question"],
                "answer": qa["answer"],
                "analysis": qa["analysis"],
                "options": qa["options"],
            })

    with open(os.path.join(OUTPUT_DIR, "data.json"), "w") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    counts = {}
    for e in entries:
        counts[e["question_id"]] = counts.get(e["question_id"], 0) + 1
    print(f"Generated {len(entries)} QA entries over {NUM_IMAGES} images.")
    for qid in sorted(counts):
        print(f"  task {qid} ({TASK_TYPES[qid][0]}): {counts[qid]} entries")


if __name__ == "__main__":
    main()
