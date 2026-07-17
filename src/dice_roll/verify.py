"""Independent checker for the dice_roll example dataset.

Re-derives every entry's answer from states/*.json plus the entry's question
text, re-implementing the dice-roll mechanics and BFS from scratch (the
generator's solver functions are NOT imported or called).

Usage: python verify.py
Prints a per-task summary and ALL CHECKS PASSED; exits non-zero otherwise.
"""

import json
import os
import re
import sys
from collections import deque

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "dice_roll_dataset_example")

VALID_LEVELS = {"Easy", "Medium", "Hard"}
VALID_TYPES = {"Target Perception", "State Prediction", "Strategy Optimization"}

# (top, bottom, north, south, east, west) tuple, indices 0..5.
MOVES = {
    # Rolling east: west->top, east->bottom, top->east, bottom->west.
    "East": lambda t: (t[5], t[4], t[2], t[3], t[0], t[1]),
    # Rolling west: east->top, west->bottom, top->west, bottom->east.
    "West": lambda t: (t[4], t[5], t[2], t[3], t[1], t[0]),
    # Rolling north: south->top, north->bottom, top->north, bottom->south.
    "North": lambda t: (t[3], t[2], t[0], t[1], t[4], t[5]),
    # Rolling south: north->top, south->bottom, top->south, bottom->north.
    "South": lambda t: (t[2], t[3], t[1], t[0], t[4], t[5]),
}
DELTAS = {"North": (-1, 0), "South": (1, 0), "East": (0, 1), "West": (0, -1)}

FAILURES = []
TASK_COUNTS = {}


def fail(msg):
    FAILURES.append(msg)


def state_to_tuple(orientation):
    """(top, bottom, north, south, east, west) tuple from the state dict."""
    return (orientation["top"], orientation["bottom"], orientation["north"],
            orientation["south"], orientation["east"], orientation["west"])


def run_sequence(state, sequence):
    """Independently simulate a roll sequence. Returns (pos, ori_tuple)."""
    rows, cols = state["rows"], state["cols"]
    blocked = {tuple(b) for b in state["blocked"]}
    pos = tuple(state["die"])
    ori = state_to_tuple(state["orientation"])
    for d in sequence:
        dr, dc = DELTAS[d]
        nr, nc = pos[0] + dr, pos[1] + dc
        if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in blocked:
            pos = (nr, nc)
            ori = MOVES[d](ori)
    return pos, ori


def bfs(state, target_top=None):
    """Independent BFS over (cell, orientation). Returns distance or None."""
    rows, cols = state["rows"], state["cols"]
    blocked = {tuple(b) for b in state["blocked"]}
    goal = tuple(state["star"])
    start = tuple(state["die"])
    start_ori = state_to_tuple(state["orientation"])
    if start == goal and (target_top is None or start_ori[0] == target_top):
        return 0
    dq = deque([(start, start_ori, 0)])
    seen = {(start, (start_ori[0], start_ori[2], start_ori[4]))}
    while dq:
        pos, ori, dist = dq.popleft()
        for d, (dr, dc) in DELTAS.items():
            nr, nc = pos[0] + dr, pos[1] + dc
            if not (0 <= nr < rows and 0 <= nc < cols) or (nr, nc) in blocked:
                continue
            nori = MOVES[d](ori)
            key = ((nr, nc), (nori[0], nori[2], nori[4]))
            if key in seen:
                continue
            if (nr, nc) == goal and (target_top is None or nori[0] == target_top):
                return dist + 1
            seen.add(key)
            dq.append(((nr, nc), nori, dist + 1))
    return None


def parse_seq(text):
    """Parse 'East, North, ...' into a list of directions."""
    seq = [s.strip() for s in text.split(",")]
    if not seq or any(s not in DELTAS for s in seq):
        raise ValueError(f"cannot parse sequence: {text!r}")
    return seq


def check_entry(entry, idx):
    eid = entry.get("data_id", f"<entry {idx}>")

    def err(msg):
        fail(f"{eid}: {msg}")

    # --- generic field checks ---
    if entry.get("data_id") != f"dice_roll-mcq-{idx + 1:05d}":
        err(f"data_id not sequential: {entry.get('data_id')}")
    for field in ("image", "state", "plot_level", "qa_level", "qa_type",
                  "question_id", "question_description", "question",
                  "answer", "analysis", "options"):
        if field not in entry:
            err(f"missing field {field}")
            return
    if entry["plot_level"] not in VALID_LEVELS:
        err(f"bad plot_level {entry['plot_level']}")
    if entry["qa_level"] not in VALID_LEVELS:
        err(f"bad qa_level {entry['qa_level']}")
    if entry["qa_type"] not in VALID_TYPES:
        err(f"bad qa_type {entry['qa_type']}")

    image_path = os.path.join(BASE_DIR, entry["image"])
    state_path = os.path.join(BASE_DIR, entry["state"])
    if not os.path.isfile(image_path):
        err(f"missing image {entry['image']}")
    if not os.path.isfile(state_path):
        err(f"missing state {entry['state']}")
        return
    with open(state_path) as f:
        state = json.load(f)

    options = entry["options"]
    answer = entry["answer"]
    if not (4 <= len(options) <= 8):
        err(f"expected 4-8 options, got {len(options)}")
    if len(set(options)) != len(options):
        err("options are not unique")
    if not isinstance(answer, int) or not (1 <= answer <= len(options)):
        err(f"answer index {answer} out of range")
        return
    chosen = options[answer - 1]

    qid = entry["question_id"]
    TASK_COUNTS[qid] = TASK_COUNTS.get(qid, 0) + 1

    # --- state sanity ---
    ori = state["orientation"]
    if ori["top"] + ori["bottom"] != 7 or ori["north"] + ori["south"] != 7 \
            or ori["east"] + ori["west"] != 7:
        err("orientation violates opposite-faces-sum-to-7")
    if sorted(ori.values()) != [1, 2, 3, 4, 5, 6]:
        err("orientation is not a permutation of 1..6")
    blocked = {tuple(b) for b in state["blocked"]}
    if tuple(state["die"]) in blocked or tuple(state["star"]) in blocked:
        err("die or star on a blocked cell")

    # --- per-task answer re-derivation ---
    q = entry["question"]
    correct_str = None

    if qid == 1:
        m = re.search(r"What number is on the (TOP|FRONT-LEFT|FRONT-RIGHT) face", q)
        if m:
            key = {"TOP": "top", "FRONT-LEFT": "south", "FRONT-RIGHT": "east"}[m.group(1)]
            correct_str = str(ori[key])
        elif "How many pips are visible" in q:
            correct_str = str(ori["top"] + ori["south"] + ori["east"])
        else:
            m = re.search(r"Which cell \(row, column\) is the (die|star)(?: \(goal\))? on\?", q)
            if not m:
                err("task 1: unrecognized variant")
                return
            target = state["die"] if m.group(1) == "die" else state["star"]
            correct_str = f"({target[0]}, {target[1]})"
        if chosen != correct_str:
            err(f"task 1: chosen {chosen!r} != ground truth {correct_str!r}")
        for o in options:
            if o != chosen and o == correct_str:
                err("task 1: duplicate correct option")

    elif qid == 2:
        m = re.search(r"The die is rolled: ([A-Za-z, ]+?)\. ", q)
        if not m:
            err("task 2: cannot parse roll sequence")
            return
        seq = parse_seq(m.group(1))
        pos, f_ori = run_sequence(state, seq)
        if "Which cell (row, column) will the die be on" in q:
            correct_str = f"({pos[0]}, {pos[1]})"
        else:
            m2 = re.search(r"on the (TOP|FRONT-LEFT|FRONT-RIGHT) face", q)
            if not m2:
                err("task 2: unrecognized variant")
                return
            idx_map = {"TOP": 0, "FRONT-LEFT": 3, "FRONT-RIGHT": 4}
            correct_str = str(f_ori[idx_map[m2.group(1)]])
        if chosen != correct_str:
            err(f"task 2: chosen {chosen!r} != ground truth {correct_str!r}")
        for o in options:
            if o != chosen and o == correct_str:
                err("task 2: duplicate correct option")
        if "move_sequence" in state and "extra_move_sequence" not in state:
            pass  # primary sequence stored in state; question text is authoritative

    elif qid == 3:
        m = re.search(
            r"ended at cell \((\d+), (\d+)\) with (\d) on the top face and (\d) "
            r"on the front-left face", q)
        if not m:
            err("task 3: cannot parse target description")
            return
        target_pos = (int(m.group(1)), int(m.group(2)))
        target_top, target_fl = int(m.group(3)), int(m.group(4))
        matching = []
        for i, o in enumerate(options):
            try:
                seq = parse_seq(o)
            except ValueError:
                err(f"task 3: option {i + 1} not a parseable sequence: {o!r}")
                continue
            pos, f_ori = run_sequence(state, seq)
            if pos == target_pos and f_ori[0] == target_top and f_ori[3] == target_fl:
                matching.append(i + 1)
        if matching != [answer]:
            err(f"task 3: matching options {matching}, answer claims {answer}")
        correct_str = chosen

    elif qid == 4:
        m = re.search(r"star cell \((\d+), (\d+)\) AND have (\d) on the top face", q)
        if m:
            if (int(m.group(1)), int(m.group(2))) != tuple(state["star"]):
                err("task 4: question star cell != state star cell")
            dist = bfs(state, target_top=int(m.group(3)))
        elif "final orientation does not matter" in q:
            m2 = re.search(r"star cell \((\d+), (\d+)\)", q)
            if (int(m2.group(1)), int(m2.group(2))) != tuple(state["star"]):
                err("task 4: question star cell != state star cell")
            dist = bfs(state, target_top=None)
        else:
            err("task 4: unrecognized variant")
            return
        if dist is None:
            err("task 4: goal unreachable (generator bug)")
            return
        correct_str = str(dist)
        if chosen != correct_str:
            err(f"task 4: chosen {chosen!r} != BFS optimum {correct_str!r}")
        for o in options:
            if o != chosen:
                try:
                    if int(o) == dist:
                        err(f"task 4: distractor {o!r} equals the optimum")
                except ValueError:
                    err(f"task 4: non-numeric distractor {o!r}")
    else:
        err(f"unknown question_id {qid}")
        return

    # --- analysis consistency ---
    if correct_str is not None:
        tail = f"So the answer is {correct_str}. The option number is {answer}."
        if tail not in entry["analysis"]:
            err(f"analysis does not end with {tail!r}")


def main():
    data_path = os.path.join(BASE_DIR, "data.json")
    if not os.path.isfile(data_path):
        print(f"data.json not found at {data_path}")
        sys.exit(1)
    with open(data_path) as f:
        data = json.load(f)

    # one entry per image/state consistency: images referenced exist
    for idx, entry in enumerate(data):
        check_entry(entry, idx)

    # dataset-level checks
    images = {e["image"] for e in data}
    levels = {}
    for e in data:
        levels.setdefault(e["plot_level"], set()).add(e["image"])
    print(f"Checked {len(data)} entries over {len(images)} images.")
    for lvl in ("Easy", "Medium", "Hard"):
        n = len(levels.get(lvl, set()))
        print(f"  plot_level {lvl}: {n} images")
        if n != 5:
            fail(f"expected 5 {lvl} images, found {n}")
    print("Per-task summary:")
    for qid in sorted(TASK_COUNTS):
        print(f"  question_id {qid}: {TASK_COUNTS[qid]} entries")
        if TASK_COUNTS[qid] < 4:
            fail(f"task {qid} appears only {TASK_COUNTS[qid]} times (< 4)")

    if FAILURES:
        print(f"\n{len(FAILURES)} CHECK(S) FAILED:")
        for msg in FAILURES:
            print("  - " + msg)
        sys.exit(1)
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
