"""Entry point: generate the mastermind example dataset (deterministic, seed 20260720).

Creates mastermind_dataset_example/{data.json, images/, states/}:
15 boards (5 Easy / 5 Medium / 5 Hard) and 60 QA entries covering all 5 task
templates (4 entries per board).
"""

import json
import os
import random
import shutil

from mastermind import (
    GAME_RULES, TASK_META, generate_board, board_to_state, render_board,
    build_task1, build_task2, build_task3, build_task4, build_task5,
    certainly_in, certainly_not_in,
)

SEED = 20260720
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "mastermind_dataset_example")

# (plot_level, n_rows, board_type) for boards 1..15
BOARD_PLAN = (
    [("Easy", 3, "multi")] * 5
    + [("Medium", 4, "multi")] * 2
    + [("Medium", 4, "unique")] * 3
    + [("Hard", 5, "multi")] * 1
    + [("Hard", 5, "unique")] * 4
)

NONE_CAP = 3  # 'None' may be the correct task-2 answer at most 3 times (<=20% of 15)


def build_entries_for_board(rng, board, none_count):
    """Build the 4 QA entries for a board. Returns (qas, none_count) or None
    when the board cannot support the planned tasks (caller regenerates)."""
    is_unique = board["mode"] == "unique"
    qas = []

    qa1 = build_task1(rng, board)
    qas.append((1, qa1))

    # task 2: pick variant (a)/(b); (a) needs non-empty certainly-in; a correct
    # 'None' answer for (b) is limited by NONE_CAP.
    variant = rng.choice(["a", "b"])
    s_in = certainly_in(board["consistent"])
    s_out = certainly_not_in(board["consistent"])
    if variant == "a" and not s_in:
        variant = "b"
    if variant == "b" and not s_out and none_count >= NONE_CAP:
        if s_in:
            variant = "a"
        else:
            return None  # cannot respect the cap: regenerate the board
    qa2 = build_task2(rng, board, variant)
    if qa2 is None:
        return None
    if qa2.pop("none_correct"):
        none_count += 1
    qas.append((2, qa2))

    qa3 = build_task3(rng, board)
    if qa3 is None:
        return None
    qas.append((3, qa3))

    if is_unique:
        qa4 = build_task4(rng, board)
        if qa4 is None:
            return None
        qas.append((4, qa4))
    else:
        qa5 = build_task5(rng, board)
        if qa5 is None:
            return None
        qas.append((5, qa5))
    return qas, none_count


def main():
    rng = random.Random(SEED)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(os.path.join(OUTPUT_DIR, "images"))
    os.makedirs(os.path.join(OUTPUT_DIR, "states"))

    all_data = []
    none_count = 0
    task_counts = {i: 0 for i in range(1, 6)}

    for board_id, (plot_level, n_rows, mode) in enumerate(BOARD_PLAN, start=1):
        while True:
            board = generate_board(rng, n_rows, mode)
            built = build_entries_for_board(rng, board, none_count)
            if built is not None:
                qas, none_count = built
                break

        image_rel = f"images/board_{board_id:05d}.png"
        state_rel = f"states/board_{board_id:05d}.json"
        wh = render_board(board, os.path.join(OUTPUT_DIR, image_rel))
        state = board_to_state(board)
        with open(os.path.join(OUTPUT_DIR, state_rel), "w") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        for question_id, qa in qas:
            qa_type, qa_level, description = TASK_META[question_id]
            options_block = "\n".join(f"[{i + 1}] {o}" for i, o in enumerate(qa["options"]))
            question = f"{GAME_RULES}\n\n{qa['body']}\n\nOptions:\n{options_block}"
            all_data.append({
                "data_id": f"mastermind-mcq-{len(all_data) + 1:05d}",
                "image": image_rel,
                "state": state_rel,
                "plot_level": plot_level,
                "qa_level": qa_level,
                "qa_type": qa_type,
                "question_id": question_id,
                "question_description": description,
                "question": question,
                "answer": qa["answer"],
                "analysis": qa["analysis"],
                "options": qa["options"],
            })
            task_counts[question_id] += 1
        print(f"board {board_id:02d} [{plot_level:6s} {mode:6s}] "
              f"{n_rows} rows, consistent={state['consistent_count']:4d}, "
              f"image {wh[0]}x{wh[1]}")

    with open(os.path.join(OUTPUT_DIR, "data.json"), "w") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {len(all_data)} entries to {OUTPUT_DIR}/data.json")
    print("Entries per task:", task_counts, "| 'None'-correct task2:", none_count)


if __name__ == "__main__":
    main()
