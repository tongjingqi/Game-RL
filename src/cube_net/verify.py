"""Independent checker for the cube_net example dataset.

Re-derives every answer from cube_net_dataset_example/states/*.json and the
question text, re-implementing the rule logic from scratch (hexomino
enumeration, net folding, cube rotations) without importing the generator.

Usage: python verify.py
Prints a per-task summary and ALL CHECKS PASSED; exits non-zero otherwise.
"""

import itertools
import json
import os
import re
import sys
from collections import deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "cube_net_dataset_example")

FACE_COLORS = {
    "red": (231, 76, 60),
    "orange": (243, 156, 18),
    "yellow": (241, 196, 15),
    "green": (39, 174, 96),
    "blue": (52, 152, 219),
    "purple": (155, 89, 182),
}
FACE_SYMBOLS = {"star", "heart", "triangle", "circle", "diamond", "cross"}
LEVELS = {"Easy", "Medium", "Hard"}
QA_TYPES = {"Target Perception", "State Prediction", "Strategy Optimization"}
TASK_META = {
    1: ("Target Perception", "Easy", 8),
    2: ("State Prediction", "Medium", 6),
    3: ("State Prediction", "Medium", 5),
    4: ("State Prediction", "Hard", 8),
    5: ("State Prediction", "Hard", 8),
}
EXPECTED_KEYS = ["data_id", "image", "state", "plot_level", "qa_level",
                 "qa_type", "question_id", "question_description", "question",
                 "answer", "analysis", "options"]

errors = []


def fail(msg):
    errors.append(msg)


# ---------------------------------------------------------------------------
# Independent re-implementation of the net/folding mathematics
# ---------------------------------------------------------------------------

def canon(cells):
    best = None
    pts = list(cells)
    for swap in (False, True):
        for sr in (1, -1):
            for sc in (1, -1):
                t = [(sr * (c if swap else r), sc * (r if swap else c))
                     for r, c in pts]
                mr = min(r for r, _ in t)
                mc = min(c for _, c in t)
                key = tuple(sorted((r - mr, c - mc) for r, c in t))
                if best is None or key < best:
                    best = key
    return best


def free_hexominoes():
    polys = {((0, 0),)}
    for _ in range(5):
        nxt = set()
        for p in polys:
            s = set(p)
            for r, c in p:
                for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    if (r + dr, c + dc) not in s:
                        q = s | {(r + dr, c + dc)}
                        mr = min(x for x, _ in q)
                        mc = min(y for _, y in q)
                        nxt.add(tuple(sorted((x - mr, y - mc) for x, y in q)))
        polys = nxt
    return sorted({canon(p) for p in polys})


def fold(cells):
    """Independent folder: returns {cell: (n, u, r)} or None."""
    cells = {tuple(c) for c in cells}
    start = min(cells)
    frames = {start: ((0, 0, 1), (0, 1, 0), (1, 0, 0))}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        n, u, r = frames[cur]
        cr, cc = cur
        moves = {
            (0, 1): (r, u, (-n[0], -n[1], -n[2])),
            (0, -1): ((-r[0], -r[1], -r[2]), u, n),
            (1, 0): ((-u[0], -u[1], -u[2]), n, r),
            (-1, 0): (u, (-n[0], -n[1], -n[2]), r),
        }
        for (dr, dc), f in moves.items():
            nb = (cr + dr, cc + dc)
            if nb not in cells:
                continue
            if nb in frames:
                if frames[nb] != f:
                    return None
            else:
                frames[nb] = f
                queue.append(nb)
    if len({f[0] for f in frames.values()}) != 6:
        return None
    return frames


def rotations24():
    out = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            m = [[0] * 3 for _ in range(3)]
            for i in range(3):
                m[i][perm[i]] = signs[i]
            inv = sum(1 for i in range(3) for j in range(i + 1, 3)
                      if perm[i] > perm[j])
            det = (-1) ** inv * signs[0] * signs[1] * signs[2]
            if det == 1:
                out.append(m)
    return out


def mv(m, v):
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


# ---------------------------------------------------------------------------
# Ground-truth derivation from a state dict
# ---------------------------------------------------------------------------

class Truth:
    def __init__(self, state):
        self.state = state
        self.faces = state["faces"]
        self.by_color = {f["color"]: f for f in self.faces}
        self.by_symbol = {f["symbol"]: f for f in self.faces}
        self.normal = {f["color"]: tuple(f["normal"]) for f in self.faces}
        self.color_at = {tuple(f["normal"]): f["color"] for f in self.faces}

    def opposite(self, color):
        n = self.normal[color]
        return self.color_at[(-n[0], -n[1], -n[2])]

    def adjacents(self, color):
        n = self.normal[color]
        return sorted(c for c, nn in self.normal.items()
                      if c != color and nn != (-n[0], -n[1], -n[2]))

    def vertex_triples(self):
        triples = set()
        for sx in (1, -1):
            for sy in (1, -1):
                for sz in (1, -1):
                    triples.add(tuple(sorted((
                        self.color_at[(sx, 0, 0)],
                        self.color_at[(0, sy, 0)],
                        self.color_at[(0, 0, sz)]))))
        return triples

    def placed_face(self, bottom_color, front_color, side):
        n1, n2 = self.normal[bottom_color], self.normal[front_color]
        rot = next(m for m in ROTS
                   if mv(m, n1) == (0, 0, -1) and mv(m, n2) == (0, -1, 0))
        want = {"RIGHT": (1, 0, 0), "LEFT": (-1, 0, 0),
                "BACK": (0, 0, 1)}[side]
        return next(c for c, n in self.normal.items() if mv(rot, n) == want)


ROTS = rotations24()
assert len(ROTS) == 24
NETS = [p for p in free_hexominoes() if fold(p) is not None]
assert len(NETS) == 11, len(NETS)


# ---------------------------------------------------------------------------
# State validation
# ---------------------------------------------------------------------------

def check_state(state, label):
    cells = {tuple(c) for c in state["cells"]}
    if len(cells) != 6:
        fail(f"{label}: state does not have 6 cells")
        return
    if canon(cells) not in NETS:
        fail(f"{label}: cells do not form one of the 11 cube nets")
        return
    frames = fold(cells)
    if frames is None:
        fail(f"{label}: net does not fold to 6 distinct normals")
        return
    faces = state["faces"]
    if len(faces) != 6:
        fail(f"{label}: state does not have 6 faces")
        return
    if {f["color"] for f in faces} != set(FACE_COLORS):
        fail(f"{label}: face colors are not exactly the 6 expected colors")
    if {f["symbol"] for f in faces} != FACE_SYMBOLS:
        fail(f"{label}: face symbols are not exactly the 6 expected symbols")
    for f in faces:
        cell = tuple(f["cell"])
        if cell not in cells:
            fail(f"{label}: face {f['color']} cell {cell} not in cells")
            continue
        if list(FACE_COLORS[f["color"]]) != f["rgb"]:
            fail(f"{label}: rgb mismatch for color {f['color']}")
        n, u, r = frames[cell]
        if tuple(f["normal"]) != n or tuple(f["up"]) != u or tuple(f["right"]) != r:
            fail(f"{label}: independently folded frame of cell {cell} "
                 f"disagrees with the stored state")
    if state["grid_rows"] != max(r for r, _ in cells) + 1:
        fail(f"{label}: grid_rows wrong")
    if state["grid_cols"] != max(c for _, c in cells) + 1:
        fail(f"{label}: grid_cols wrong")


# ---------------------------------------------------------------------------
# Entry checking
# ---------------------------------------------------------------------------

def parse_color_set(option):
    return tuple(sorted(s.strip() for s in option.split(",")))


def expected_answer(qid, question, truth, options):
    """Return (expected_correct_option_string, extra_error_checks)."""
    if qid == 1:
        m = re.search(r"Which color is the face with the (\w+) symbol\?",
                      question)
        if m:
            sym = m.group(1)
            if sym not in truth.by_symbol:
                fail(f"task1: symbol '{sym}' in question not on any face")
                return None
            return truth.by_symbol[sym]["color"]
        m = re.search(r"Which symbol is drawn on the (\w+) face\?", question)
        if m:
            col = m.group(1)
            if col not in truth.by_color:
                fail(f"task1: color '{col}' in question not on any face")
                return None
            return truth.by_color[col]["symbol"]
        m = re.search(r"grid position \(row, column\) of the (\w+) face\?",
                      question)
        if m:
            col = m.group(1)
            if col not in truth.by_color:
                fail(f"task1: color '{col}' in question not on any face")
                return None
            cell = truth.by_color[col]["cell"]
            return f"({cell[0]}, {cell[1]})"
        fail("task1: question matches no known sub-type")
        return None
    if qid == 2:
        m = re.search(r"which face is opposite to the (\w+) face\?", question)
        if not m:
            fail("task2: cannot parse question")
            return None
        return truth.opposite(m.group(1))
    if qid == 3:
        m = re.search(r"which set of faces shares an edge with the (\w+) "
                      r"face\?", question)
        if not m:
            fail("task3: cannot parse question")
            return None
        color = m.group(1)
        adj = truth.adjacents(color)
        expected = ", ".join(adj)
        opp = truth.opposite(color)
        others5 = sorted(c for c in FACE_COLORS if c != color)
        # Structural checks: exactly the five 4-subsets of the other five
        # colors; the correct one is the only option without the opposite face.
        seen_sets = set()
        for o in options:
            parts = [s.strip() for s in o.split(",")]
            if len(parts) != 4 or any(p not in others5 for p in parts):
                fail(f"task3: option '{o}' is not a 4-subset of the colors "
                     f"other than {color}")
            if color in parts:
                fail(f"task3: option '{o}' contains the queried face {color}")
            seen_sets.add(tuple(sorted(parts)))
        want_sets = {tuple(sorted(s))
                     for s in itertools.combinations(others5, 4)}
        if seen_sets != want_sets:
            fail(f"task3: options are not exactly the 5 near-miss sets "
                 f"(missing: {want_sets - seen_sets})")
        without_opp = [o for o in options if opp not in o.split(", ")]
        if without_opp != [expected]:
            fail(f"task3: expected exactly one option without the opposite "
                 f"face {opp} (the correct one), found {without_opp}")
        return expected
    if qid == 4:
        m = re.search(r"the (\w+) face is on the BOTTOM and the (\w+) face "
                      r"faces you \(the FRONT\)\. Which color is on the "
                      r"(RIGHT|LEFT|BACK) face\?", question)
        if not m:
            if "TOP face?" in question:
                fail("task4: TOP variant is forbidden (redundant with task 2)")
            else:
                fail("task4: cannot parse question")
            return None
        c1, c2, side = m.group(1), m.group(2), m.group(3)
        n1, n2 = truth.normal.get(c1), truth.normal.get(c2)
        if n1 is None or n2 is None:
            fail(f"task4: unknown colors {c1}/{c2}")
            return None
        if n1 == n2 or n1 == (-n2[0], -n2[1], -n2[2]):
            fail(f"task4: {c1} and {c2} are not adjacent faces")
            return None
        return truth.placed_face(c1, c2, side)
    if qid == 5:
        triples = truth.vertex_triples()
        hits = [o for o in options
                if all(p in FACE_COLORS for p in o.split(", "))
                and parse_color_set(o) in triples]
        if len(hits) != 1:
            fail(f"task5: expected exactly one vertex-triple option, "
                 f"found {len(hits)}")
            return None
        return hits[0]
    fail(f"unknown question_id {qid}")
    return None


def check_entry(entry, idx):
    label = entry.get("data_id", f"entry#{idx}")
    if list(entry.keys()) != EXPECTED_KEYS:
        fail(f"{label}: keys/order mismatch: {list(entry.keys())}")
    if entry["data_id"] != f"cube_net-mcq-{idx + 1:05d}":
        fail(f"{label}: data_id not sequential")
    if entry["plot_level"] not in LEVELS:
        fail(f"{label}: bad plot_level {entry['plot_level']}")
    if entry["qa_level"] not in LEVELS:
        fail(f"{label}: bad qa_level {entry['qa_level']}")
    if entry["qa_type"] not in QA_TYPES:
        fail(f"{label}: bad qa_type {entry['qa_type']}")
    qid = entry["question_id"]
    if qid not in TASK_META:
        fail(f"{label}: bad question_id {qid}")
        return
    qa_type, qa_level, n_opts = TASK_META[qid]
    if entry["qa_type"] != qa_type or entry["qa_level"] != qa_level:
        fail(f"{label}: qa_type/qa_level do not match task {qid}")
    if not entry["question_description"]:
        fail(f"{label}: empty question_description")
    if not entry["question"].startswith("This is a cube net puzzle."):
        fail(f"{label}: question missing the rules preamble")

    options = entry["options"]
    if len(options) != n_opts:
        fail(f"{label}: task {qid} should have {n_opts} options, "
             f"has {len(options)}")
    if len(set(options)) != len(options):
        fail(f"{label}: duplicate options")
    if not isinstance(entry["answer"], int) or not (1 <= entry["answer"] <= len(options)):
        fail(f"{label}: answer index {entry['answer']} out of range")
        return

    # The Options block in the question text must match the options list.
    block = "\n\nOptions:\n" + "\n".join(
        f"[{i + 1}] {o}" for i, o in enumerate(options))
    if not entry["question"].endswith(block):
        fail(f"{label}: options block in question text mismatches options list")

    # Files exist; image within size budget.
    img_path = os.path.join(DATA_DIR, entry["image"])
    state_path = os.path.join(DATA_DIR, entry["state"])
    if not os.path.isfile(img_path):
        fail(f"{label}: missing image {entry['image']}")
    if not os.path.isfile(state_path):
        fail(f"{label}: missing state {entry['state']}")
        return

    with open(state_path) as f:
        state = json.load(f)
    check_state(state, label + "/" + entry["state"])
    truth = Truth(state)

    expected = expected_answer(qid, entry["question"], truth, options)
    if expected is None:
        return
    if expected not in options:
        fail(f"{label}: correct option '{expected}' not among options")
        return
    if options[entry["answer"] - 1] != expected:
        fail(f"{label}: answer {entry['answer']} points to "
             f"'{options[entry['answer'] - 1]}', expected '{expected}'")
    # Exactly one correct option: every other option must be genuinely wrong.
    for i, o in enumerate(options):
        if i == entry["answer"] - 1:
            continue
        if qid in (3, 5):
            if parse_color_set(o) == parse_color_set(expected):
                fail(f"{label}: distractor '{o}' equals the correct set")
        elif o == expected:
            fail(f"{label}: distractor duplicates the correct option")
    if qid == 4:
        for bad in ("Cannot be determined", "None of the above"):
            if options[entry["answer"] - 1] == bad:
                fail(f"{label}: '{bad}' marked correct (never valid here)")
    # Analysis must state the final answer consistently.
    tail = f"So the answer is {expected}. The option number is {entry['answer']}."
    if tail not in entry["analysis"]:
        fail(f"{label}: analysis does not conclude with '{tail}'")


def main():
    data_file = os.path.join(DATA_DIR, "data.json")
    if not os.path.isfile(data_file):
        print("data.json not found")
        sys.exit(1)
    with open(data_file) as f:
        data = json.load(f)

    from PIL import Image
    for idx, entry in enumerate(data):
        check_entry(entry, idx)
        img_path = os.path.join(DATA_DIR, entry["image"])
        if os.path.isfile(img_path):
            with Image.open(img_path) as im:
                if max(im.size) > 640 or im.format != "PNG":
                    fail(f"{entry['data_id']}: image {im.size} {im.format} "
                         f"violates the <=640px PNG rule")

    # Per-task summary.
    counts = {}
    for e in data:
        counts[e["question_id"]] = counts.get(e["question_id"], 0) + 1
    print(f"Checked {len(data)} entries.")
    for qid in sorted(counts):
        print(f"  task {qid} ({TASK_META[qid][0]} / {TASK_META[qid][1]}): "
              f"{counts[qid]} entries")
    for qid, n in sorted(counts.items()):
        if n < 4:
            fail(f"task {qid} appears only {n} times (< 4)")

    if errors:
        print(f"\n{len(errors)} CHECK(S) FAILED:")
        for e in errors[:50]:
            print("  -", e)
        sys.exit(1)
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
