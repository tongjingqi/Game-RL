"""Independent verifier for the committed Lights Out example dataset.

The checker deliberately does not import ``lights_out.py``.  It reconstructs
press effects, solves each board with an independent first-row chasing method,
parses every question, and re-derives the answer from the saved state.
"""

import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from itertools import product

from PIL import Image


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "lights_out_dataset_example")
DATA_PATH = os.path.join(DATASET_DIR, "data.json")

EXPECTED_FIELDS = [
    "data_id", "image", "state", "plot_level", "qa_level", "qa_type",
    "question_id", "question_description", "question", "answer", "analysis",
    "options",
]
EXPECTED_STATE_FIELDS = [
    "size", "grid", "board_kind", "generation_presses", "on_count", "solver",
]
EXPECTED_META = {
    1: ("Target Perception", "Easy", "Identify states and counts of lights on the board"),
    2: ("State Prediction", "Medium", "Predict the board after a sequence of button presses"),
    3: ("State Prediction", "Hard", "Infer which button press(es) produced the shown board"),
    4: ("Strategy Optimization", "Hard", "Find the minimum presses needed to turn all lights off"),
}
EXPECTED_DIMS = {3: (478, 574), 4: (538, 634), 5: (544, 640)}
LEVEL_FOR_SIZE = {3: "Easy", 4: "Medium", 5: "Hard"}

errors = []
checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        errors.append(message)


def fail(message):
    errors.append(message)


def fmt_cell(cell):
    return f"({cell[0]}, {cell[1]})"


def parse_cells(text):
    return [(int(r), int(c)) for r, c in re.findall(r"\((\d+), (\d+)\)", text)]


def press_pattern(size, row, col):
    cells = [(row, col)]
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        rr, cc = row + dr, col + dc
        if 0 <= rr < size and 0 <= cc < size:
            cells.append((rr, cc))
    return cells


def apply_presses(grid, presses):
    size = len(grid)
    out = [row[:] for row in grid]
    for row, col in presses:
        for rr, cc in press_pattern(size, row, col):
            out[rr][cc] ^= 1
    return out


def count_on(grid):
    return sum(sum(row) for row in grid)


def chase_solutions(grid):
    """Enumerate all solutions independently by trying every first press row."""
    size = len(grid)
    solutions = []
    for first_mask in range(1 << size):
        sim = [row[:] for row in grid]
        presses = []

        def press(row, col):
            presses.append((row, col))
            for rr, cc in press_pattern(size, row, col):
                sim[rr][cc] ^= 1

        for col in range(size):
            if (first_mask >> col) & 1:
                press(0, col)
        for row in range(1, size):
            for col in range(size):
                if sim[row - 1][col]:
                    press(row, col)
        if not any(sim[-1]):
            check(not any(any(row) for row in sim), "internal chase solver left a light ON")
            solutions.append(sorted(presses))
    return solutions


def validate_state(state_path, image_path, state_rel, image_rel):
    try:
        with open(state_path, encoding="utf-8") as handle:
            state = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{state_rel}: cannot read state: {exc}")
        return None, []

    check(list(state) == EXPECTED_STATE_FIELDS,
          f"{state_rel}: state fields/order differ: {list(state)}")
    size = state.get("size")
    check(size in (3, 4, 5), f"{state_rel}: unsupported size {size}")
    if size not in (3, 4, 5):
        return None, []

    grid = state.get("grid")
    valid_grid = (
        isinstance(grid, list) and len(grid) == size
        and all(isinstance(row, list) and len(row) == size for row in grid)
        and all(cell in (0, 1) for row in grid for cell in row)
    )
    check(valid_grid, f"{state_rel}: grid is not a {size}x{size} binary matrix")
    if not valid_grid:
        return None, []

    generation = state.get("generation_presses")
    valid_generation = (
        isinstance(generation, list)
        and all(isinstance(cell, list) and len(cell) == 2 for cell in generation)
        and all(isinstance(v, int) for cell in generation for v in cell)
        and all(0 <= r < size and 0 <= c < size for r, c in generation)
        and len({tuple(cell) for cell in generation}) == len(generation)
    )
    check(valid_generation, f"{state_rel}: invalid/duplicate generation presses")
    if valid_generation:
        rebuilt = apply_presses([[0] * size for _ in range(size)], generation)
        check(rebuilt == grid, f"{state_rel}: generation presses do not reconstruct grid")

    board_kind = state.get("board_kind")
    expected_kinds = {"single_press": 1, "two_press": 2}
    check(board_kind in {"single_press", "two_press", "general"},
          f"{state_rel}: bad board_kind {board_kind!r}")
    if board_kind in expected_kinds:
        check(len(generation) == expected_kinds[board_kind],
              f"{state_rel}: {board_kind} has {len(generation)} generation presses")
    elif board_kind == "general":
        check(len(generation) > 2, f"{state_rel}: general board uses <=2 presses")

    actual_on = count_on(grid)
    check(0 < actual_on < size * size, f"{state_rel}: board is all-OFF or all-ON")
    check(state.get("on_count") == actual_on,
          f"{state_rel}: on_count {state.get('on_count')} != {actual_on}")

    solutions = chase_solutions(grid)
    check(bool(solutions), f"{state_rel}: board is not solvable")
    if solutions:
        minimum = min(map(len, solutions))
        saved = state.get("solver", {})
        check(list(saved) == ["solvable", "nullity", "min_weight", "min_presses", "num_solutions"],
              f"{state_rel}: solver fields/order differ")
        check(saved.get("solvable") is True, f"{state_rel}: solver.solvable is not true")
        check(saved.get("num_solutions") == len(solutions),
              f"{state_rel}: saved num_solutions differs from independent solver")
        expected_nullity = int(math.log2(len(solutions)))
        check(1 << expected_nullity == len(solutions),
              f"{state_rel}: solution count is not a power of two")
        check(saved.get("nullity") == expected_nullity,
              f"{state_rel}: saved nullity differs from independent solver")
        check(saved.get("min_weight") == minimum,
              f"{state_rel}: saved min_weight differs from independent solver")
        saved_min = [tuple(cell) for cell in saved.get("min_presses", [])]
        check(saved_min in solutions and len(saved_min) == minimum,
              f"{state_rel}: saved min_presses is not an optimal solution")

    try:
        with Image.open(image_path) as image:
            image.load()
            check(image.format == "PNG", f"{image_rel}: format is {image.format}, not PNG")
            check(image.mode == "RGB", f"{image_rel}: mode is {image.mode}, not RGB")
            check(image.size == EXPECTED_DIMS[size],
                  f"{image_rel}: dimensions {image.size} != {EXPECTED_DIMS[size]}")
            check(max(image.size) <= 640, f"{image_rel}: long side exceeds 640 px")
            btn = {3: 118, 4: 100, 5: 80}[size]
            gap = 14 if size <= 4 else 12
            for row in range(size):
                for col in range(size):
                    x = round(62 + col * (btn + gap) + btn / 2)
                    y = round(106 + row * (btn + gap) + btn / 2)
                    red, green, blue = image.getpixel((x, y))
                    if grid[row][col]:
                        check(red > 190 and green > 145 and blue < 175,
                              f"{image_rel}: ON cell {(row, col)} center pixel looks OFF")
                    else:
                        check(max(red, green, blue) < 135,
                              f"{image_rel}: OFF cell {(row, col)} center pixel looks ON")
    except OSError as exc:
        fail(f"{image_rel}: cannot read image: {exc}")

    return state, solutions


def task1_truth(entry, state):
    question = entry["question"]
    grid, size = state["grid"], state["size"]
    match = re.search(r"What are the states of the lights at (.*?) \(in that order\)\?", question)
    if match:
        cells = parse_cells(match.group(1))
        check(len(cells) == 3, f"{entry['data_id']}: task1-a does not name three cells")
        truth = ", ".join("ON" if grid[r][c] else "OFF" for r, c in cells)
        expected = {", ".join(bits) for bits in product(("ON", "OFF"), repeat=3)}
        check(set(entry["options"]) == expected,
              f"{entry['data_id']}: task1-a options are not all eight state triples")
        return truth, "1a"

    if "How many lights are currently ON?" in question:
        return str(count_on(grid)), "1b"

    if "Which row has the most lights ON?" in question:
        row_counts = [sum(row) for row in grid]
        maximum = max(row_counts)
        winners = [i for i, value in enumerate(row_counts) if value == maximum]
        truth = f"Row {winners[0]}" if len(winners) == 1 else "Two or more rows are tied for the most"
        expected = {f"Row {i}" for i in range(size)} | {"Two or more rows are tied for the most"}
        check(set(entry["options"]) == expected,
              f"{entry['data_id']}: task1-c options do not enumerate all rows plus tie")
        return truth, "1c"

    match = re.search(r"How many lights are ON in column (\d+)\?", question)
    if match:
        col = int(match.group(1))
        check(0 <= col < size, f"{entry['data_id']}: task1-d column out of bounds")
        check(set(entry["options"]) == {str(i) for i in range(size + 1)},
              f"{entry['data_id']}: task1-d options do not cover 0..{size}")
        return str(sum(grid[row][col] for row in range(size))), "1d"

    fail(f"{entry['data_id']}: cannot identify task1 variant")
    return None, "1?"


def task2_truth(entry, state):
    question = entry["question"]
    match = re.search(r"the buttons (.*?) are pressed in that order", question)
    if not match:
        fail(f"{entry['data_id']}: cannot parse task2 press sequence")
        return None, "2?"
    presses = parse_cells(match.group(1))
    expected_k = {3: 2, 5: 3}.get(state["size"])
    if expected_k is not None:
        check(len(presses) == expected_k,
              f"{entry['data_id']}: task2 uses {len(presses)} presses, expected {expected_k}")
    else:
        check(len(presses) in (2, 3),
              f"{entry['data_id']}: 4x4 task2 should use two or three presses")
    check(len(set(presses)) == len(presses), f"{entry['data_id']}: task2 repeats a press")
    final_grid = apply_presses(state["grid"], presses)

    if "How many lights will be ON afterwards?" in question:
        return str(count_on(final_grid)), "2A"

    match = re.search(r"states of the lights at (.*?) \(in that order\)\?", question)
    if match:
        targets = parse_cells(match.group(1))
        check(len(targets) == 3, f"{entry['data_id']}: task2-B does not name three targets")
        truth = ", ".join("ON" if final_grid[r][c] else "OFF" for r, c in targets)
        expected = {", ".join(bits) for bits in product(("ON", "OFF"), repeat=3)}
        check(set(entry["options"]) == expected,
              f"{entry['data_id']}: task2-B options are not all eight state triples")
        return truth, "2B"

    fail(f"{entry['data_id']}: cannot identify task2 variant")
    return None, "2?"


def task3_truth(entry, state):
    question = entry["question"]
    size = state["size"]
    zero = [[0] * size for _ in range(size)]
    candidates = [(row, col) for row in range(size) for col in range(size)]

    for option in entry["options"]:
        parsed = parse_cells(option)
        check(len(parsed) == 1 and option == fmt_cell(parsed[0]),
              f"{entry['data_id']}: malformed task3 option {option!r}")

    if "Exactly one button was pressed" in question:
        valid = [cell for cell in candidates if apply_presses(zero, [cell]) == state["grid"]]
        check(state["board_kind"] == "single_press",
              f"{entry['data_id']}: task3-a is not attached to single_press state")
        check(len(valid) == 1, f"{entry['data_id']}: task3-a has {len(valid)} valid cells")
        return fmt_cell(valid[0]) if valid else None, "3a"

    match = re.search(r"One of them was \((\d+), (\d+)\)\. Which was the other one\?", question)
    if match:
        given = (int(match.group(1)), int(match.group(2)))
        valid = [
            cell for cell in candidates
            if cell != given and apply_presses(zero, [given, cell]) == state["grid"]
        ]
        check(state["board_kind"] == "two_press",
              f"{entry['data_id']}: task3-b is not attached to two_press state")
        check(len(valid) == 1, f"{entry['data_id']}: task3-b has {len(valid)} valid cells")
        return fmt_cell(valid[0]) if valid else None, "3b"

    fail(f"{entry['data_id']}: cannot identify task3 variant")
    return None, "3?"


def parse_press_set(option, size):
    if not (option.startswith("{") and option.endswith("}")):
        return None
    cells = parse_cells(option)
    if not cells or len(cells) != len(set(cells)):
        return None
    if any(not (0 <= row < size and 0 <= col < size) for row, col in cells):
        return None
    if option != "{" + ", ".join(fmt_cell(cell) for cell in cells) + "}":
        return None
    return cells


def task4_truth(entry, state, solutions):
    question = entry["question"]
    minimum = min(map(len, solutions))
    if "minimum number of button presses" in question:
        for option in entry["options"]:
            check(re.fullmatch(r"\d+", option) is not None,
                  f"{entry['data_id']}: nonnumeric task4-numeric option {option!r}")
        return str(minimum), "4numeric"

    if "Which set of button presses turns ALL lights OFF" in question:
        parsed = [parse_press_set(option, state["size"]) for option in entry["options"]]
        check(all(cells is not None for cells in parsed),
              f"{entry['data_id']}: malformed task4-set option")
        if not all(cells is not None for cells in parsed):
            return None, "4set"
        check(all(len(cells) == minimum for cells in parsed),
              f"{entry['data_id']}: task4-set options are not all minimum-sized")
        solves = [apply_presses(state["grid"], cells) == [[0] * state["size"] for _ in range(state["size"])]
                  for cells in parsed]
        check(sum(solves) == 1, f"{entry['data_id']}: task4-set has {sum(solves)} solving options")
        index = solves.index(True) if any(solves) else -1
        return entry["options"][index] if index >= 0 else None, "4set"

    fail(f"{entry['data_id']}: cannot identify task4 variant")
    return None, "4?"


def main():
    if not os.path.isfile(DATA_PATH):
        print(f"FAIL: missing dataset {DATA_PATH}")
        return 1
    try:
        with open(DATA_PATH, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read {DATA_PATH}: {exc}")
        return 1

    check(isinstance(data, list), "data.json root is not a list")
    if not isinstance(data, list):
        data = []
    check(len(data) == 60, f"expected 60 entries, got {len(data)}")

    state_cache = {}
    qid_counts = Counter()
    variant_counts = Counter()
    plot_counts = Counter()
    entries_per_state = Counter()
    qids_per_state = defaultdict(list)
    grids_seen = set()

    for index, entry in enumerate(data, 1):
        if not isinstance(entry, dict):
            fail(f"entry {index}: not an object")
            continue
        data_id = entry.get("data_id", f"entry-{index}")
        check(list(entry) == EXPECTED_FIELDS,
              f"{data_id}: fields/order differ: {list(entry)}")
        check(data_id == f"lights_out-mcq-{index:05d}",
              f"{data_id}: data_id is not sequential")

        image_rel, state_rel = entry.get("image"), entry.get("state")
        check(isinstance(image_rel, str) and re.fullmatch(r"images/board_\d{5}\.png", image_rel or ""),
              f"{data_id}: invalid image path {image_rel!r}")
        check(isinstance(state_rel, str) and re.fullmatch(r"states/board_\d{5}\.json", state_rel or ""),
              f"{data_id}: invalid state path {state_rel!r}")
        if not isinstance(image_rel, str) or not isinstance(state_rel, str):
            continue
        check(os.path.basename(image_rel).replace(".png", "")
              == os.path.basename(state_rel).replace(".json", ""),
              f"{data_id}: image/state board ids differ")
        image_path = os.path.join(DATASET_DIR, image_rel)
        state_path = os.path.join(DATASET_DIR, state_rel)
        check(os.path.isfile(image_path), f"{data_id}: missing {image_rel}")
        check(os.path.isfile(state_path), f"{data_id}: missing {state_rel}")
        if not os.path.isfile(image_path) or not os.path.isfile(state_path):
            continue

        if state_rel not in state_cache:
            state, solutions = validate_state(state_path, image_path, state_rel, image_rel)
            state_cache[state_rel] = (state, solutions)
            if state is not None:
                grid_key = (state["size"], tuple(tuple(row) for row in state["grid"]))
                check(grid_key not in grids_seen, f"{state_rel}: duplicate visual board")
                grids_seen.add(grid_key)
        state, solutions = state_cache[state_rel]
        if state is None:
            continue

        entries_per_state[state_rel] += 1
        qid = entry.get("question_id")
        qids_per_state[state_rel].append(qid)
        check(qid in EXPECTED_META, f"{data_id}: invalid question_id {qid}")
        if qid not in EXPECTED_META:
            continue
        qid_counts[qid] += 1
        expected_type, expected_level, expected_description = EXPECTED_META[qid]
        check(entry.get("qa_type") == expected_type,
              f"{data_id}: qa_type {entry.get('qa_type')!r} != {expected_type!r}")
        check(entry.get("qa_level") == expected_level,
              f"{data_id}: qa_level {entry.get('qa_level')!r} != {expected_level!r}")
        check(entry.get("question_description") == expected_description,
              f"{data_id}: question_description differs")
        expected_plot = LEVEL_FOR_SIZE[state["size"]]
        check(entry.get("plot_level") == expected_plot,
              f"{data_id}: plot_level {entry.get('plot_level')!r} != {expected_plot!r}")
        plot_counts[entry.get("plot_level")] += 1

        options = entry.get("options")
        answer = entry.get("answer")
        check(isinstance(options, list) and 4 <= len(options) <= 8,
              f"{data_id}: options must be a list of 4..8 strings")
        if not isinstance(options, list):
            continue
        check(all(isinstance(option, str) and option for option in options),
              f"{data_id}: blank/non-string option")
        check(len(options) == len(set(options)), f"{data_id}: duplicate options")
        check(isinstance(answer, int) and 1 <= answer <= len(options),
              f"{data_id}: answer {answer!r} is not a valid 1-based index")
        if not isinstance(answer, int) or not 1 <= answer <= len(options):
            continue

        question = entry.get("question")
        check(isinstance(question, str), f"{data_id}: question is not text")
        if not isinstance(question, str):
            continue
        check(question.startswith("Lights Out is a puzzle played on a square grid of buttons"),
              f"{data_id}: missing rules preamble")
        check("Positions are written as (row, column) and are 0-based" in question,
              f"{data_id}: preamble lacks coordinate convention")
        options_block = "\n\nOptions:\n" + "\n".join(
            f"[{i}] {option}" for i, option in enumerate(options, 1)
        )
        check(question.endswith(options_block), f"{data_id}: malformed options block")

        if qid == 1:
            truth, variant = task1_truth(entry, state)
        elif qid == 2:
            truth, variant = task2_truth(entry, state)
        elif qid == 3:
            truth, variant = task3_truth(entry, state)
        else:
            truth, variant = task4_truth(entry, state, solutions)
        variant_counts[variant] += 1
        correct_text = options[answer - 1]
        check(truth is not None and correct_text == truth,
              f"{data_id}: answer option {correct_text!r} != independent truth {truth!r}")
        if truth is not None:
            check(options.count(truth) == 1,
                  f"{data_id}: truth appears {options.count(truth)} times in options")

        analysis = entry.get("analysis")
        check(isinstance(analysis, str) and len(analysis) >= 80,
              f"{data_id}: analysis is missing/too short")
        if isinstance(analysis, str):
            expected_final = f"So the answer is {correct_text}. The option number is {answer}."
            check(analysis.endswith("\n\n" + expected_final),
                  f"{data_id}: analysis final answer/index line differs")

    check(len(state_cache) == 15, f"expected 15 distinct states, got {len(state_cache)}")
    check(len({entry.get('image') for entry in data if isinstance(entry, dict)}) == 15,
          "expected 15 distinct images")
    check(all(count == 4 for count in entries_per_state.values()),
          f"not every state has four entries: {dict(entries_per_state)}")
    for state_rel, qids in qids_per_state.items():
        check(all(qid in qids for qid in (1, 2, 4)),
              f"{state_rel}: every board must contain q1, q2, and q4")
        state = state_cache[state_rel][0]
        if state is not None and state["board_kind"] in {"single_press", "two_press"}:
            check(sorted(qids) == [1, 2, 3, 4],
                  f"{state_rel}: special board qids are {qids}, expected 1/2/3/4")
        elif state is not None:
            check(qids.count(3) == 0 and (qids.count(1) == 2 or qids.count(2) == 2),
                  f"{state_rel}: general board lacks one extra q1/q2 variant")

    check(qid_counts == {1: 20, 2: 19, 3: 6, 4: 15},
          f"question_id counts differ: {dict(qid_counts)}")
    check(variant_counts == {
        "1a": 5, "1b": 5, "1c": 5, "1d": 5,
        "2A": 10, "2B": 9, "3a": 3, "3b": 3,
        "4numeric": 8, "4set": 7,
    }, f"builder variant counts differ: {dict(variant_counts)}")
    check(plot_counts == {"Easy": 20, "Medium": 20, "Hard": 20},
          f"plot_level counts differ: {dict(plot_counts)}")

    print(f"Checked {len(data)} entries, {len(state_cache)} states, {checks} assertions.")
    print("question_id counts:", dict(sorted(qid_counts.items())))
    print("builder variant counts:", dict(sorted(variant_counts.items())))
    print("plot_level counts:", dict(sorted(plot_counts.items())))
    if errors:
        print(f"\n{len(errors)} FAILURE(S):")
        for message in errors[:80]:
            print(" -", message)
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
