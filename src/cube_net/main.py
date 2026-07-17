"""Entry point: generate the cube_net example dataset deterministically.

Usage: python main.py
Writes cube_net_dataset_example/{data.json, images/, states/}.
"""

import json
import os
import random

from cube_net import (CubeNet, build_task1, build_task2, build_task3,
                      build_task4, build_task5)

SEED = 20260717
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "cube_net_dataset_example")

IMAGES_PER_LEVEL = 5
PLOT_LEVELS = ["Easy", "Medium", "Hard"]


def build_board_qas(net, rng, board_index):
    """Build the QA entries for one board.

    Tasks 1-3 always; task 4 on 12 of 15 boards; task 5 on 12 of 15 boards
    (both on 9 boards), so tasks 4 and 5 each appear 12 times overall.
    Task 1 cycles through its three sub-types.
    """
    qas = []
    qas.append(build_task1(net, rng, subtype=board_index % 3))
    qas.append(build_task2(net, rng))
    qas.append(build_task3(net, rng))
    if board_index not in (4, 9, 14):
        ask = ("RIGHT", "LEFT")[board_index % 2]
        qas.append(build_task4(net, rng, ask))
    if board_index not in (1, 6, 11):
        qas.append(build_task5(net, rng))
    return qas


def main():
    rng = random.Random(SEED)
    images_dir = os.path.join(OUT_DIR, "images")
    states_dir = os.path.join(OUT_DIR, "states")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(states_dir, exist_ok=True)

    entries = []
    board_index = 0
    for plot_level in PLOT_LEVELS:
        for pick in range(IMAGES_PER_LEVEL):
            board_index += 1
            i0 = board_index - 1
            net = CubeNet.generate(rng, plot_level, pick)
            image_rel = f"images/board_{board_index:05d}.png"
            state_rel = f"states/board_{board_index:05d}.json"
            net.render(os.path.join(OUT_DIR, image_rel))
            with open(os.path.join(OUT_DIR, state_rel), "w") as f:
                json.dump(net.to_state(), f, indent=2)

            for qa in build_board_qas(net, rng, i0):
                entry = {
                    "data_id": f"cube_net-mcq-{len(entries) + 1:05d}",
                    "image": image_rel,
                    "state": state_rel,
                    "plot_level": plot_level,
                    "qa_level": qa["qa_level"],
                    "qa_type": qa["qa_type"],
                    "question_id": qa["question_id"],
                    "question_description": qa["question_description"],
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "analysis": qa["analysis"],
                    "options": qa["options"],
                }
                entries.append(entry)

    with open(os.path.join(OUT_DIR, "data.json"), "w") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    # Brief summary.
    from collections import Counter
    by_task = Counter(e["question_id"] for e in entries)
    print(f"Generated {board_index} boards and {len(entries)} QA entries "
          f"in {OUT_DIR}")
    print("Entries per task:", dict(sorted(by_task.items())))


if __name__ == "__main__":
    main()
