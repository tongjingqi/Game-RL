"""Entry point: generate the domino example dataset (15 boards, 60 QA entries).

Usage: python main.py
Deterministic: fixed seed 20260719.
"""

import json
import os
import random
import shutil

import numpy as np

from domino import (TASK1_SUBTYPES, build_task1, build_task2, build_task3,
                    build_task4, gen_board, render_board)

SEED = 20260719
LEVELS = ["Easy"] * 5 + ["Medium"] * 5 + ["Hard"] * 5
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "domino_dataset_example")


def main():
    random.seed(SEED)
    np_rng = np.random.default_rng(SEED)

    for sub in ("images", "states"):
        path = os.path.join(OUT_DIR, sub)
        if os.path.isdir(path):
            shutil.rmtree(path)
        os.makedirs(path)

    entries = []
    for board_id, level in enumerate(LEVELS, 1):
        state = gen_board(level, random)
        image_rel = f"images/board_{board_id:05d}.png"
        state_rel = f"states/board_{board_id:05d}.json"
        w, h = render_board(state, os.path.join(OUT_DIR, image_rel), np_rng)
        with open(os.path.join(OUT_DIR, state_rel), "w") as f:
            json.dump(state, f, indent=2)

        # Task 1 sub-types rotate across boards (a, b, c, d, a, ...).
        rot = (board_id - 1) % len(TASK1_SUBTYPES)
        order = TASK1_SUBTYPES[rot:] + TASK1_SUBTYPES[:rot]
        qas = [build_task1(state, random, order),
               build_task2(state, random),
               build_task3(state, random),
               build_task4(state, random)]

        for qa in qas:
            entries.append({
                "data_id": f"domino-mcq-{len(entries) + 1:05d}",
                "image": image_rel,
                "state": state_rel,
                "plot_level": level,
                "qa_level": qa["qa_level"],
                "qa_type": qa["qa_type"],
                "question_id": qa["question_id"],
                "question_description": qa["question_description"],
                "question": qa["question"],
                "answer": qa["answer"],
                "analysis": qa["analysis"],
                "options": qa["options"],
            })
        print(f"board {board_id:02d} ({level}): chain={len(state['chain'])} "
              f"hand={len(state['hand'])} image={w}x{h}")

    with open(os.path.join(OUT_DIR, "data.json"), "w") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {len(entries)} QA entries to "
          f"{os.path.join(OUT_DIR, 'data.json')}")


if __name__ == "__main__":
    main()
