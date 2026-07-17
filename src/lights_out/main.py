"""Generate the deterministic Lights Out example GameQA dataset.

The output contains 15 boards (five each at 3x3, 4x4, and 5x5) and exactly
four questions per board.  Every board receives task 1, task 2, and task 4;
six one/two-press boards also receive inverse task 3, while the nine general
boards receive a second, different task-1 or task-2 variant.
"""

import json
import os
import random
import shutil
from collections import Counter

from lights_out import (
    GAME_RULES,
    QA_TYPES,
    QUESTION_DESCRIPTIONS,
    build_task1,
    build_task2,
    build_task3,
    build_task4,
    count_on,
    generate_board,
    render_board,
    solve_lights_out,
)


SEED = 20260721
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "lights_out_dataset_example")

# size, plot level, board kind, generation k, base task-1 variant,
# base task-2 variant, task-4 variant, fourth question (qid, variant)
BOARD_PLAN = [
    (3, "Easy",   "single_press", 1,  "a", "A", "numeric", (3, "a")),
    (3, "Easy",   "two_press",    2,  "b", "B", "set",     (3, "b")),
    (3, "Easy",   "general",      4,  "c", "A", "numeric", (1, "a")),
    (3, "Easy",   "general",      5,  "d", "B", "set",     (1, "b")),
    (3, "Easy",   "general",      6,  "a", "A", "numeric", (1, "c")),
    (4, "Medium", "single_press", 1,  "b", "B", "set",     (3, "a")),
    (4, "Medium", "two_press",    2,  "c", "A", "numeric", (3, "b")),
    (4, "Medium", "general",      6,  "d", "B", "set",     (2, "A")),
    (4, "Medium", "general",      7,  "a", "A", "numeric", (1, "d")),
    (4, "Medium", "general",      8,  "b", "B", "set",     (2, "A")),
    (5, "Hard",   "single_press", 1,  "c", "A", "numeric", (3, "a")),
    (5, "Hard",   "two_press",    2,  "d", "B", "set",     (3, "b")),
    (5, "Hard",   "general",      8,  "a", "A", "numeric", (2, "B")),
    (5, "Hard",   "general",      10, "b", "B", "set",     (1, "d")),
    (5, "Hard",   "general",      12, "c", "A", "numeric", (2, "B")),
]

MIN_GENERAL_WEIGHT = {3: 3, 4: 3, 5: 4}


def has_unique_max_row(grid):
    counts = [sum(row) for row in grid]
    return counts.count(max(counts)) == 1


def board_key(grid):
    return tuple(tuple(row) for row in grid)


def build_qas(grid, generation_presses, base_t1, base_t2, task4_variant,
              extra_spec, rng):
    """Build the four planned QA tuples as (question_id, variant, payload)."""
    qas = [
        (1, base_t1, build_task1(grid, base_t1, rng)),
        (2, base_t2, build_task2(grid, base_t2, rng)),
        (4, task4_variant, build_task4(grid, task4_variant, rng)),
    ]
    extra_qid, extra_variant = extra_spec
    if extra_qid == 1:
        payload = build_task1(grid, extra_variant, rng)
    elif extra_qid == 2:
        payload = build_task2(grid, extra_variant, rng)
    elif extra_qid == 3:
        payload = build_task3(grid, generation_presses, extra_variant, rng)
    else:
        raise ValueError(f"unsupported extra question_id {extra_qid}")
    qas.append((extra_qid, extra_variant, payload))
    return qas


def finalize_payload(payload, rng):
    """Shuffle options and convert a builder's answer text to a 1-based index."""
    body, options, correct, analysis_core = payload
    options = list(options)
    if len(options) != len(set(options)):
        raise ValueError("builder returned duplicate options")
    if options.count(correct) != 1:
        raise ValueError("builder answer is not unique among options")
    rng.shuffle(options)
    answer = options.index(correct) + 1
    options_block = "\n".join(f"[{index}] {option}"
                              for index, option in enumerate(options, 1))
    question = f"{GAME_RULES}\n\n{body}\n\nOptions:\n{options_block}"
    analysis = (
        f"{analysis_core}\n\n"
        f"So the answer is {correct}. The option number is {answer}."
    )
    return question, answer, analysis, options


def generate_planned_board(plan, rng, used_grids):
    size, _, board_kind, generation_k, base_t1, base_t2, task4_variant, extra = plan
    needs_unique_max = "c" in (base_t1, extra[1] if extra[0] == 1 else None)
    for _ in range(10000):
        grid, generation_presses = generate_board(size, generation_k, rng)
        key = board_key(grid)
        if key in used_grids:
            continue
        if needs_unique_max and not has_unique_max_row(grid):
            continue
        solution = solve_lights_out(grid)
        if board_kind == "general" and solution["min_weight"] < MIN_GENERAL_WEIGHT[size]:
            continue
        try:
            qas = build_qas(
                grid, generation_presses, base_t1, base_t2,
                task4_variant, extra, rng,
            )
        except AssertionError:
            # A candidate can fail a builder precondition (notably a task-4
            # distractor endpoint); deterministically reject and regenerate.
            continue
        used_grids.add(key)
        return grid, generation_presses, solution, qas
    raise RuntimeError(f"could not generate board satisfying plan {plan}")


def state_payload(size, grid, board_kind, generation_presses, solution):
    return {
        "size": size,
        "grid": grid,
        "board_kind": board_kind,
        "generation_presses": [list(cell) for cell in generation_presses],
        "on_count": count_on(grid),
        "solver": {
            "solvable": solution["solvable"],
            "nullity": solution["nullity"],
            "min_weight": solution["min_weight"],
            "min_presses": [list(cell) for cell in solution["min_presses"]],
            "num_solutions": solution["num_solutions"],
        },
    }


def main():
    rng = random.Random(SEED)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    images_dir = os.path.join(OUTPUT_DIR, "images")
    states_dir = os.path.join(OUTPUT_DIR, "states")
    os.makedirs(images_dir)
    os.makedirs(states_dir)

    all_data = []
    used_grids = set()
    qid_counts = Counter()
    variant_counts = Counter()

    for board_id, plan in enumerate(BOARD_PLAN, 1):
        size, plot_level, board_kind, generation_k, _, _, _, _ = plan
        grid, generation_presses, solution, qas = generate_planned_board(
            plan, rng, used_grids,
        )
        image_rel = f"images/board_{board_id:05d}.png"
        state_rel = f"states/board_{board_id:05d}.json"
        render_board(grid, os.path.join(OUTPUT_DIR, image_rel))
        with open(os.path.join(OUTPUT_DIR, state_rel), "w", encoding="utf-8") as handle:
            json.dump(
                state_payload(size, grid, board_kind, generation_presses, solution),
                handle, ensure_ascii=False, indent=2,
            )
            handle.write("\n")

        for question_id, variant, payload in qas:
            question, answer, analysis, options = finalize_payload(payload, rng)
            qa_type, qa_level = QA_TYPES[question_id]
            all_data.append({
                "data_id": f"lights_out-mcq-{len(all_data) + 1:05d}",
                "image": image_rel,
                "state": state_rel,
                "plot_level": plot_level,
                "qa_level": qa_level,
                "qa_type": qa_type,
                "question_id": question_id,
                "question_description": QUESTION_DESCRIPTIONS[question_id],
                "question": question,
                "answer": answer,
                "analysis": analysis,
                "options": options,
            })
            qid_counts[question_id] += 1
            variant_counts[f"{question_id}{variant}"] += 1

        print(
            f"board {board_id:02d} [{plot_level:6s} {size}x{size} {board_kind:12s}] "
            f"generated with {generation_k:2d}, ON={count_on(grid):2d}, "
            f"minimum={solution['min_weight']:2d}, solutions={solution['num_solutions']:2d}"
        )

    if len(all_data) != 60:
        raise RuntimeError(f"expected 60 entries, built {len(all_data)}")
    with open(os.path.join(OUTPUT_DIR, "data.json"), "w", encoding="utf-8") as handle:
        json.dump(all_data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"\nWrote {len(all_data)} entries for {len(BOARD_PLAN)} boards to {OUTPUT_DIR}")
    print("question_id counts:", dict(sorted(qid_counts.items())))
    print("builder variant counts:", dict(sorted(variant_counts.items())))


if __name__ == "__main__":
    main()
