"""Independent verifier for the domino example dataset.

Re-derives every entry's answer from states/*.json + the question text,
re-implementing the domino rules from scratch (no generator imports).
Run: python verify.py  ->  prints ALL CHECKS PASSED on success.
"""

import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "domino_dataset_example")

EXPECTED_KEYS = ["data_id", "image", "state", "plot_level", "qa_level",
                 "qa_type", "question_id", "question_description", "question",
                 "answer", "analysis", "options"]
QID_META = {
    1: ("Target Perception", "Easy"),
    2: ("State Prediction", "Medium"),
    3: ("State Prediction", "Medium"),
    4: ("Strategy Optimization", "Hard"),
}
RULES_PREFIX = "This is a Domino Chain puzzle."


# --------------------------------------------------------------------------- #
# Fresh re-implementations of the rule logic (shared with nobody)
# --------------------------------------------------------------------------- #

def fmt_labels(labels):
    labels = sorted(labels)
    if not labels:
        return "None"
    if len(labels) == 1:
        return f"{labels[0]} only"
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return ", ".join(labels[:-1]) + f" and {labels[-1]}"


def brute_max(tiles, left, right):
    """Plain exponential recursion (n <= 6) — independent of the generator."""
    best = 0
    for i, (a, b) in enumerate(tiles):
        rest = tiles[:i] + tiles[i + 1:]
        if a == left or b == left:
            nl = b if a == left else a
            best = max(best, 1 + brute_max(rest, nl, right))
        if a == right or b == right:
            nr = b if a == right else a
            best = max(best, 1 + brute_max(rest, left, nr))
    return best


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def fail(errors, data_id, msg):
    errors.append(f"[{data_id}] {msg}")


def parse_options_block(question):
    """Extract the 'Options:' block lines -> list of option strings."""
    if "\n\nOptions:\n" not in question:
        return None
    block = question.split("\n\nOptions:\n", 1)[1]
    out = []
    for line in block.split("\n"):
        m = re.fullmatch(r"\[(\d+)\] (.*)", line)
        if not m:
            return None
        if int(m.group(1)) != len(out) + 1:
            return None
        out.append(m.group(2))
    return out


def ground_truth(entry, state, errors):
    """Recompute the correct option string from the state + question text."""
    qid = entry["question_id"]
    q = entry["question"]
    chain = state["chain"]
    hand = {h["label"]: h["tile"] for h in state["hand"]}
    left, right = chain[0][0], chain[-1][1]

    if qid == 1:
        m = re.search(r"tile at the (LEFT|RIGHT) end of the chain\. "
                      r"How many pips are on its (left|right) half\?", q)
        if m:
            end, half_side = m.group(1), m.group(2)
            tile = chain[0] if end == "LEFT" else chain[-1]
            if tile[0] == tile[1]:
                fail(errors, entry["data_id"],
                     "task 1a asked about a double end tile (visually ambiguous)")
            return str(tile[0] if half_side == "left" else tile[1])
        m = re.search(r"What are the two values of hand tile ([A-Z])\?", q)
        if m:
            t = hand[m.group(1)]
            return f"({t[0]}|{t[1]})"
        if "How many doubles" in q:
            return str(sum(1 for t in chain if t[0] == t[1]))
        if "Which hand tile is a double" in q:
            dbl = [lb for lb, t in hand.items() if t[0] == t[1]]
            if len(dbl) != 1:
                fail(errors, entry["data_id"],
                     f"task 1d but hand has {len(dbl)} doubles")
                return None
            return dbl[0]
        fail(errors, entry["data_id"], "could not detect task-1 subtype")
        return None

    if qid == 2:
        playable = [lb for lb, t in hand.items()
                    if t[0] in (left, right) or t[1] in (left, right)]
        if not playable or len(playable) == len(hand):
            fail(errors, entry["data_id"],
                 "playable set is empty or covers the whole hand (bad board)")
        return fmt_labels(playable)

    if qid == 3:
        m = re.search(r"Hand tile ([A-Z]) \((\d)\|(\d)\) is played on the "
                      r"(LEFT|RIGHT) end", q)
        if not m:
            fail(errors, entry["data_id"], "could not parse task-3 question")
            return None
        lb, a, b, end = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
        if hand[lb] != [a, b]:
            fail(errors, entry["data_id"],
                 f"task-3 tile values in question {(a, b)} != state {hand[lb]}")
        if end == "LEFT":
            if a != left and b != left:
                fail(errors, entry["data_id"],
                     "task-3 tile does not match the LEFT open end")
                return None
            other = b if a == left else a
            return f"({other}, {right})"
        if a != right and b != right:
            fail(errors, entry["data_id"],
                 "task-3 tile does not match the RIGHT open end")
            return None
        other = b if a == right else a
        return f"({left}, {other})"

    if qid == 4:
        tiles = [(t[0], t[1]) for t in hand.values()]
        return str(brute_max(tiles, left, right))

    fail(errors, entry["data_id"], f"unknown question_id {qid}")
    return None


def check_state(entry, state, errors):
    did = entry["data_id"]
    chain, hand = state["chain"], state["hand"]
    if not (5 <= len(chain) <= 9):
        fail(errors, did, f"chain length {len(chain)} out of range")
    if not (4 <= len(hand) <= 6):
        fail(errors, did, f"hand size {len(hand)} out of range")
    for t in chain:
        if not (isinstance(t, list) and len(t) == 2
                and all(isinstance(v, int) and 0 <= v <= 6 for v in t)):
            fail(errors, did, f"bad chain tile {t}")
    for i in range(len(chain) - 1):
        if chain[i][1] != chain[i + 1][0]:
            fail(errors, did, f"chain broken at index {i}: {chain[i]} -> {chain[i + 1]}")
    if state["open_left"] != chain[0][0] or state["open_right"] != chain[-1][1]:
        fail(errors, did, "stored open ends do not match the chain")
    labels = [h["label"] for h in hand]
    if len(set(labels)) != len(labels):
        fail(errors, did, "hand labels not unique")
    if labels != [chr(ord("A") + i) for i in range(len(labels))]:
        fail(errors, did, f"hand labels are not consecutive from A: {labels}")
    seen = set()
    for t in chain + [h["tile"] for h in hand]:
        key = frozenset(t) if t[0] != t[1] else ("D", t[0])
        if key in seen:
            fail(errors, did, f"tile {t} used more than once (not a 28-set draw)")
        seen.add(key)
    sizes = {"Easy": (5, 4), "Medium": ((6, 7), 5), "Hard": ((8, 9), 6)}
    want_n, want_h = sizes[entry["plot_level"]]
    ok_n = len(chain) in want_n if isinstance(want_n, tuple) else len(chain) == want_n
    if not ok_n or len(hand) != want_h:
        fail(errors, did, f"plot_level {entry['plot_level']} inconsistent with "
                          f"chain={len(chain)} hand={len(hand)}")


def main():
    errors = []
    with open(os.path.join(DATA_DIR, "data.json")) as f:
        data = json.load(f)

    task_counts = Counter()
    for idx, e in enumerate(data, 1):
        did = e.get("data_id", f"entry#{idx}")
        if list(e.keys()) != EXPECTED_KEYS:
            fail(errors, did, f"field order/names wrong: {list(e.keys())}")
        if did != f"domino-mcq-{idx:05d}":
            fail(errors, did, f"data_id should be domino-mcq-{idx:05d}")
        if e["plot_level"] not in ("Easy", "Medium", "Hard"):
            fail(errors, did, f"bad plot_level {e['plot_level']}")
        qid = e["question_id"]
        if qid not in QID_META:
            fail(errors, did, f"bad question_id {qid}")
            continue
        want_type, want_level = QID_META[qid]
        if e["qa_type"] != want_type or e["qa_level"] != want_level:
            fail(errors, did, f"qa_type/qa_level mismatch for task {qid}")
        if not e["question"].startswith(RULES_PREFIX):
            fail(errors, did, "question missing GAME_RULES preamble")

        opts = parse_options_block(e["question"])
        if opts is None:
            fail(errors, did, "Options block malformed")
        elif opts != e["options"]:
            fail(errors, did, "options list does not match the question text")
        if len(set(e["options"])) != len(e["options"]):
            fail(errors, did, "options not unique")
        if not isinstance(e["answer"], int) or not (1 <= e["answer"] <= len(e["options"])):
            fail(errors, did, f"answer index {e['answer']} out of range")

        for rel, kind in ((e["image"], "image"), (e["state"], "state")):
            if not os.path.isfile(os.path.join(DATA_DIR, rel)):
                fail(errors, did, f"missing {kind} file {rel}")
        m = re.fullmatch(r"images/board_(\d{5})\.png", e["image"])
        if not m or e["state"] != f"states/board_{m.group(1)}.json":
            fail(errors, did, "image/state paths not paired board_xxxxx files")

        with open(os.path.join(DATA_DIR, e["state"])) as f:
            state = json.load(f)
        check_state(e, state, errors)

        truth = ground_truth(e, state, errors)
        if truth is None:
            continue
        correct_str = e["options"][e["answer"] - 1]
        if correct_str != truth:
            fail(errors, did, f"option at answer index is '{correct_str}' "
                              f"but ground truth is '{truth}'")
        n_correct = sum(1 for o in e["options"] if o == truth)
        if n_correct != 1:
            fail(errors, did, f"ground truth appears {n_correct} times in options")
        tail = f"So the answer is {truth}. The option number is {e['answer']}."
        if tail not in e["analysis"]:
            fail(errors, did, f"analysis does not end with '{tail}'")
        task_counts[qid] += 1

    # Per-task summary.
    print("Per-task summary:")
    for qid in sorted(QID_META):
        print(f"  task {qid} ({QID_META[qid][0]} / {QID_META[qid][1]}): "
              f"{task_counts[qid]} entries checked")
    print(f"  total entries: {len(data)}")

    if errors:
        print(f"\n{len(errors)} CHECK(S) FAILED:")
        for msg in errors:
            print("  " + msg)
        sys.exit(1)
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
