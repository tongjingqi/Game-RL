"""Independent verifier for the Tower of Hanoi example dataset.

The checker does not import the generator module. It parses every question,
re-simulates moves, and uses an independently encoded BFS state graph.

Usage: python verify.py
"""

import json
import os
import re
import sys
from collections import deque

from PIL import Image


BASE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "tower_of_hanoi_dataset_example"
)
PEGS = ("A", "B", "C")
EXPECTED_FIELDS = [
    "data_id",
    "image",
    "state",
    "plot_level",
    "qa_level",
    "qa_type",
    "question_id",
    "question_description",
    "question",
    "answer",
    "analysis",
    "options",
]
LEVEL_DISKS = {"Easy": 3, "Medium": 4, "Hard": 5}
TASK_META = {
    1: ("Target Perception", "Easy"),
    2: ("State Prediction", "Medium"),
    3: ("State Prediction", "Hard"),
    4: ("Strategy Optimization", "Hard"),
}
RULES_PREFIX = "This is a Tower of Hanoi puzzle."
MOVE_RE = re.compile(r"([ABC]) → ([ABC])")


def _legal(pegs, source, destination):
    return bool(pegs[source]) and (
        not pegs[destination] or pegs[source][-1] < pegs[destination][-1]
    )


def _after_move(pegs, source, destination):
    result = {peg: list(pegs[peg]) for peg in PEGS}
    result[destination].append(result[source].pop())
    return result


def _assignment(pegs, num_disks):
    """Encode a board as disk-indexed peg positions, unlike the generator."""
    result = [None] * num_disks
    for peg_index, peg in enumerate(PEGS):
        for disk in pegs[peg]:
            if 1 <= disk <= num_disks:
                result[disk - 1] = peg_index
    return tuple(result)


def _assignment_successors(board):
    top = [None, None, None]
    for disk, peg_index in enumerate(board, 1):
        if top[peg_index] is None:
            top[peg_index] = disk
    for source, disk in enumerate(top):
        if disk is None:
            continue
        for destination, destination_top in enumerate(top):
            if source == destination:
                continue
            if destination_top is not None and destination_top < disk:
                continue
            nxt = list(board)
            nxt[disk - 1] = destination
            yield (source, destination), tuple(nxt)


def _bfs_distance(pegs, target_peg, num_disks):
    start = _assignment(pegs, num_disks)
    target_index = PEGS.index(target_peg)
    goal = (target_index,) * num_disks
    if start == goal:
        return 0
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        board, distance = queue.popleft()
        for _, nxt in _assignment_successors(board):
            if nxt in seen:
                continue
            if nxt == goal:
                return distance + 1
            seen.add(nxt)
            queue.append((nxt, distance + 1))
    return None


def _parse_move(text):
    match = MOVE_RE.fullmatch(text.strip())
    if not match or match.group(1) == match.group(2):
        return None
    return match.group(1), match.group(2)


def _ground_truth_q1(question, state):
    pegs = state["pegs"]
    match = re.search(r"How many disks are on peg ([ABC])\?", question)
    if match:
        return str(len(pegs[match.group(1)]))
    match = re.search(r"What is the size of the top disk on peg ([ABC])\?", question)
    if match:
        stack = pegs[match.group(1)]
        return str(stack[-1]) if stack else "The peg is empty"
    match = re.search(r"Which peg holds the largest disk \(disk (\d+)\)\?", question)
    if match:
        disk = int(match.group(1))
        return f"Peg {next(peg for peg in PEGS if disk in pegs[peg])}"
    match = re.search(r"List the disks on peg ([ABC]) from bottom to top\.", question)
    if match:
        return ", ".join(str(disk) for disk in pegs[match.group(1)])
    raise ValueError("unrecognized task-1 variant")


def _ground_truth_q2(question, state):
    match = re.search(
        r"The following moves are made in order: (.*?)\. If a move is illegal,",
        question,
    )
    if not match:
        raise ValueError("cannot parse task-2 move sequence")
    moves = [_parse_move(text) for text in match.group(1).split(", ")]
    if not moves or any(move is None for move in moves):
        raise ValueError("task-2 sequence contains an invalid move token")

    pegs = {peg: list(state["pegs"][peg]) for peg in PEGS}
    for source, destination in moves:
        if _legal(pegs, source, destination):
            pegs = _after_move(pegs, source, destination)

    count_match = re.search(
        r"After the full sequence, how many disks will be on peg ([ABC])\?", question
    )
    if count_match:
        return str(len(pegs[count_match.group(1)])), moves
    top_match = re.search(
        r"After the full sequence, what will be the size of the top disk on peg ([ABC])\?",
        question,
    )
    if top_match:
        stack = pegs[top_match.group(1)]
        return (str(stack[-1]) if stack else "The peg is empty"), moves
    raise ValueError("unrecognized task-2 outcome variant")


def _ground_truth_q3(question, state):
    match = re.search(
        r"After this move, peg ([ABC]) has (\d+) disk\(s\) with disk (\d+) on top\.",
        question,
    )
    if not match:
        raise ValueError("cannot parse task-3 target outcome")
    target_peg = match.group(1)
    target_count = int(match.group(2))
    target_top = int(match.group(3))
    matches = []
    for source in PEGS:
        for destination in PEGS:
            if source == destination or not _legal(state["pegs"], source, destination):
                continue
            after = _after_move(state["pegs"], source, destination)
            stack = after[target_peg]
            if len(stack) == target_count and stack and stack[-1] == target_top:
                matches.append(f"{source} → {destination}")
    if len(matches) != 1:
        raise ValueError(f"task-3 outcome has {len(matches)} matching legal moves")
    return matches[0]


def _ground_truth_q4(question, state):
    first_variant = "Which FIRST move belongs to a shortest solution?" in question
    if first_variant:
        match = re.search(r"gather all (\d+) disks onto peg ([ABC])", question)
    else:
        match = re.search(
            r"minimum number of moves needed to get all (\d+) disks onto peg ([ABC])",
            question,
        )
    if not match:
        raise ValueError("cannot parse task-4 target peg")
    num_disks = int(match.group(1))
    target_peg = match.group(2)
    if num_disks != state["num_disks"]:
        raise ValueError("task-4 disk count disagrees with state")
    if target_peg != state.get("target_peg"):
        raise ValueError("task-4 target peg disagrees with state")

    distance = _bfs_distance(state["pegs"], target_peg, num_disks)
    if distance is None:
        raise ValueError("task-4 target is unreachable")
    if not first_variant:
        return str(distance)

    optimal = []
    for source in PEGS:
        for destination in PEGS:
            if source == destination or not _legal(state["pegs"], source, destination):
                continue
            after = _after_move(state["pegs"], source, destination)
            remainder = _bfs_distance(after, target_peg, num_disks)
            if remainder == distance - 1:
                optimal.append(f"{source} → {destination}")
    if len(optimal) != 1:
        raise ValueError(f"task-4 first-move variant has {len(optimal)} optima")
    return optimal[0]


def _check_entry(entry, index, base_dir, failures, counts):
    entry_id = entry.get("data_id", f"<entry {index + 1}>") if isinstance(entry, dict) else f"<entry {index + 1}>"

    def fail(message):
        failures.append(f"{entry_id}: {message}")

    if not isinstance(entry, dict):
        fail("entry is not an object")
        return
    if list(entry) != EXPECTED_FIELDS:
        fail(f"fields/order differ from required schema: {list(entry)}")
        return
    expected_id = f"tower_of_hanoi-mcq-{index + 1:05d}"
    if entry["data_id"] != expected_id:
        fail(f"expected sequential data_id {expected_id}")

    question_id = entry["question_id"]
    if question_id not in TASK_META:
        fail(f"unknown question_id {question_id!r}")
        return
    counts[question_id] = counts.get(question_id, 0) + 1
    expected_type, expected_level = TASK_META[question_id]
    if entry["qa_type"] != expected_type or entry["qa_level"] != expected_level:
        fail(
            f"metadata should be ({expected_type}, {expected_level}), got "
            f"({entry['qa_type']}, {entry['qa_level']})"
        )
    if entry["plot_level"] not in LEVEL_DISKS:
        fail(f"invalid plot_level {entry['plot_level']!r}")
        return
    if not isinstance(entry["question_description"], str) or not entry["question_description"].strip():
        fail("question_description is empty")

    image_path = os.path.join(base_dir, entry["image"])
    state_path = os.path.join(base_dir, entry["state"])
    if not os.path.isfile(image_path):
        fail(f"missing image {entry['image']}")
    else:
        try:
            with Image.open(image_path) as image:
                if image.format != "PNG" or image.mode != "RGB" or image.size != (600, 580):
                    fail(
                        f"image must be RGB PNG 600x580, got "
                        f"{image.format} {image.mode} {image.size}"
                    )
                image.verify()
        except Exception as exc:
            fail(f"cannot read image: {exc}")
    if not os.path.isfile(state_path):
        fail(f"missing state {entry['state']}")
        return
    try:
        with open(state_path, encoding="utf-8") as handle:
            state = json.load(handle)
    except Exception as exc:
        fail(f"cannot read state: {exc}")
        return

    num_disks = state.get("num_disks")
    if num_disks != LEVEL_DISKS[entry["plot_level"]]:
        fail(f"state has {num_disks} disks for {entry['plot_level']} plot_level")
    pegs = state.get("pegs")
    if not isinstance(pegs, dict) or list(pegs) != list(PEGS):
        fail("state pegs must contain A, B, C in order")
        return
    disks = []
    for peg in PEGS:
        stack = pegs[peg]
        if not isinstance(stack, list) or any(
            stack[i] <= stack[i + 1] for i in range(len(stack) - 1)
        ):
            fail(f"peg {peg} is not a legal bottom-to-top stack: {stack!r}")
            return
        disks.extend(stack)
    if sorted(disks) != list(range(1, num_disks + 1)):
        fail(f"disks are not exactly 1..{num_disks}: {disks!r}")
        return
    if state.get("target_peg") not in PEGS:
        fail(f"invalid target_peg {state.get('target_peg')!r}")

    options = entry["options"]
    answer = entry["answer"]
    if not isinstance(options, list) or not 4 <= len(options) <= 8:
        fail(f"expected 4-8 options, got {options!r}")
        return
    if len(options) != len(set(options)):
        fail("options are not unique")
    if not isinstance(answer, int) or not 1 <= answer <= len(options):
        fail(f"answer {answer!r} is not a 1-based option index")
        return

    question = entry["question"]
    if not isinstance(question, str) or not question.startswith(RULES_PREFIX):
        fail("question does not begin with the fixed game-rules preamble")
        return
    option_block = "Options:\n" + "\n".join(
        f"[{number}] {option}" for number, option in enumerate(options, 1)
    )
    if not question.endswith(option_block):
        fail("numbered options in question do not match options field")

    try:
        if question_id == 1:
            correct = _ground_truth_q1(question, state)
        elif question_id == 2:
            correct, moves = _ground_truth_q2(question, state)
            for move_number, (source, destination) in enumerate(moves, 1):
                marker = f"Move {move_number} - {source} → {destination}:"
                if marker not in entry["analysis"]:
                    fail(f"analysis is missing trace marker {marker!r}")
        elif question_id == 3:
            correct = _ground_truth_q3(question, state)
            if any(_parse_move(option) is None for option in options):
                fail("task-3 options must all be valid directed move labels")
        else:
            correct = _ground_truth_q4(question, state)
    except (KeyError, StopIteration, TypeError, ValueError) as exc:
        fail(f"cannot independently derive answer: {exc}")
        return

    matching_options = [i for i, option in enumerate(options, 1) if option == correct]
    if matching_options != [answer]:
        fail(
            f"ground truth {correct!r} occurs at {matching_options}, "
            f"but answer is {answer}"
        )
    tail = f"So the answer is {correct}. The option number is {answer}."
    if not entry["analysis"].endswith(tail):
        fail(f"analysis does not end with {tail!r}")


def check_dataset(base_dir=BASE_DIR):
    failures = []
    counts = {}
    data_path = os.path.join(base_dir, "data.json")
    if not os.path.isfile(data_path):
        return [f"data.json not found at {data_path}"], counts
    try:
        with open(data_path, encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:
        return [f"cannot read data.json: {exc}"], counts
    if not isinstance(data, list):
        return ["data.json root must be a list"], counts

    if len(data) != 60:
        failures.append(f"expected 60 entries, found {len(data)}")
    for index, entry in enumerate(data):
        _check_entry(entry, index, base_dir, failures, counts)

    images = {entry.get("image") for entry in data if isinstance(entry, dict)}
    states = {entry.get("state") for entry in data if isinstance(entry, dict)}
    if len(images) != 15:
        failures.append(f"expected 15 referenced images, found {len(images)}")
    if len(states) != 15:
        failures.append(f"expected 15 referenced states, found {len(states)}")

    by_image = {}
    by_level = {level: set() for level in LEVEL_DISKS}
    for entry in data:
        if not isinstance(entry, dict) or not all(
            key in entry for key in ("image", "question_id", "plot_level")
        ):
            continue
        by_image.setdefault(entry["image"], []).append(entry["question_id"])
        if entry["plot_level"] in by_level:
            by_level[entry["plot_level"]].add(entry["image"])
    for image, question_ids in by_image.items():
        if sorted(question_ids) != [1, 2, 3, 4]:
            failures.append(f"{image}: expected question_ids 1..4, got {question_ids}")
    for level, level_images in by_level.items():
        if len(level_images) != 5:
            failures.append(f"expected 5 {level} images, found {len(level_images)}")
    for question_id in TASK_META:
        if counts.get(question_id, 0) != 15:
            failures.append(
                f"expected 15 entries for task {question_id}, found {counts.get(question_id, 0)}"
            )
    return failures, dict(sorted(counts.items()))


def main():
    failures, counts = check_dataset()
    entry_count = sum(counts.values())
    print(f"Checked {entry_count} entries over 15 expected images.")
    print("Per-task summary:")
    for question_id in sorted(counts):
        print(f"  question_id {question_id}: {counts[question_id]} entries")
    if failures:
        print(f"\n{len(failures)} CHECK(S) FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        sys.exit(1)
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
