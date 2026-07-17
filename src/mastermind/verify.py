"""Independent checker for the mastermind example dataset.

Re-derives every entry's answer from states/*.json + the entry's question text.
The rule logic below is re-implemented from scratch (it does NOT call the
generator's functions): brute-force consistency over all 6**4 = 1296 codes,
certainly-in/out sets, minimax worst-case analysis. Run AFTER main.py.

Prints a per-task summary and ALL CHECKS PASSED; exits non-zero on any failure.
"""

import json
import os
import re
import sys
from collections import Counter
from itertools import product

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "mastermind_dataset_example")
COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
ALL = list(product(range(6), repeat=4))
VALID_QA_TYPES = {"Target Perception", "State Prediction", "Strategy Optimization"}
VALID_LEVELS = {"Easy", "Medium", "Hard"}
EXPECTED_FIELDS = ["data_id", "image", "state", "plot_level", "qa_level",
                   "qa_type", "question_id", "question_description", "question",
                   "answer", "analysis", "options"]

errors = []
checks = 0


def fail(msg):
    errors.append(msg)


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        fail(msg)


# --- independent rule implementation ---------------------------------------

def score(guess, secret):
    """(black, white): black = exact position matches; white = right color,
    wrong position (color-histogram overlap minus black)."""
    black = sum(1 for a, b in zip(guess, secret) if a == b)
    cg, cs = Counter(guess), Counter(secret)
    overlap = sum(min(cg[c], cs[c]) for c in cg)
    return black, overlap - black


def parse_code(text):
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 4 or any(p not in COLORS for p in parts):
        return None
    return tuple(COLORS.index(p) for p in parts)


def parse_set(text):
    if text == "None":
        return frozenset()
    parts = frozenset(p.strip() for p in text.split(","))
    if not parts or any(p not in COLORS for p in parts):
        return None
    return frozenset(COLORS.index(p) for p in parts)


def fmt_code(code):
    return ", ".join(COLORS[i] for i in code)


def fmt_set(s):
    if not s:
        return "None"
    return ", ".join(c for i, c in enumerate(COLORS) if i in s)


def load_state(path):
    st = json.load(open(path))
    secret = tuple(COLORS.index(c) for c in st["secret"])
    rows = []
    for g in sorted(st["guesses"], key=lambda r: r["row"]):
        pegs = tuple(COLORS.index(c) for c in g["pegs"])
        # recompute the shown feedback from the secret: it must match the state
        b, w = score(pegs, secret)
        check((b, w) == (g["black"], g["white"]),
              f"{path} row {g['row']}: stated feedback ({g['black']},{g['white']}) "
              f"!= recomputed ({b},{w})")
        rows.append((pegs, g["black"], g["white"]))
    cons = [x for x in ALL if all(score(g, x) == (b, w) for g, b, w in rows)]
    if "consistent_count" in st:
        check(st["consistent_count"] == len(cons),
              f"{path}: stated consistent_count {st['consistent_count']} "
              f"!= recomputed {len(cons)}")
    return secret, rows, cons


# --- per-task answer re-derivation ------------------------------------------

def check_task1(entry, rows):
    q = entry["question"]
    m = re.search(r"four colors of the guess in row (\d+)", q)
    if m:
        k = int(m.group(1))
        check(1 <= k <= len(rows), f"{entry['data_id']}: bad row {k}")
        return fmt_code(rows[k - 1][0]), "a"
    m = re.search(r"black and how many white feedback pegs did the guess in row (\d+)", q)
    if m:
        k = int(m.group(1))
        b, w = rows[k - 1][1], rows[k - 1][2]
        return f"{b} black, {w} white", "b"
    m = re.search(r"How many (\w+) pegs appear in the guess in row (\d+)", q)
    if m:
        color, k = m.group(1), int(m.group(2))
        check(color in COLORS, f"{entry['data_id']}: unknown color {color}")
        n = rows[k - 1][0].count(COLORS.index(color))
        return str(n), "c"
    fail(f"{entry['data_id']}: could not parse task-1 variant")
    return None, "?"


def check_task2(entry, cons):
    s_in = frozenset(c for c in range(6) if all(c in x for x in cons))
    s_out = frozenset(c for c in range(6) if all(c not in x for x in cons))
    if "CERTAINLY NOT" in entry["question"]:
        return fmt_set(s_out)
    return fmt_set(s_in)


def worst_case(cand, cons):
    buckets = Counter(score(cand, x) for x in cons)
    return max(buckets.values())


def main():
    data = json.load(open(os.path.join(BASE, "data.json")))
    check(len(data) == 60, f"expected 60 entries, got {len(data)}")
    per_task = Counter()
    state_cache = {}

    for i, e in enumerate(data):
        did = e["data_id"]
        # structural checks
        check(list(e.keys()) == EXPECTED_FIELDS, f"{did}: field order/names differ")
        check(did == f"mastermind-mcq-{i + 1:05d}", f"{did}: not sequential")
        check(e["qa_type"] in VALID_QA_TYPES, f"{did}: bad qa_type")
        check(e["qa_level"] in VALID_LEVELS and e["plot_level"] in VALID_LEVELS,
              f"{did}: bad level")
        check(isinstance(e["question_id"], int) and 1 <= e["question_id"] <= 5,
              f"{did}: bad question_id")
        check(isinstance(e["answer"], int) and 1 <= e["answer"] <= len(e["options"]),
              f"{did}: bad answer index")
        check(len(e["options"]) == len(set(e["options"])), f"{did}: duplicate options")
        img_p = os.path.join(BASE, e["image"])
        st_p = os.path.join(BASE, e["state"])
        check(os.path.exists(img_p), f"{did}: missing image {e['image']}")
        check(os.path.exists(st_p), f"{did}: missing state {e['state']}")
        check("Mastermind" in e["question"][:400], f"{did}: question lacks rules preamble")
        check("\n\nOptions:\n[1] " in e["question"], f"{did}: malformed options block")
        for j, o in enumerate(e["options"]):
            check(f"[{j + 1}] {o}" in e["question"], f"{did}: option {j + 1} not in question")

        if not os.path.exists(st_p):
            continue
        if st_p not in state_cache:
            state_cache[st_p] = load_state(st_p)
        secret, rows, cons = state_cache[st_p]
        correct_str = e["options"][e["answer"] - 1]

        qid = e["question_id"]
        per_task[qid] += 1

        if qid == 1:
            truth, _ = check_task1(e, rows)
            if truth is None:
                continue
            check(correct_str == truth,
                  f"{did}: answer '{correct_str}' != ground truth '{truth}'")
            # every other option must be a genuinely different value
            for o in e["options"]:
                if o != correct_str:
                    check(o != truth, f"{did}: distractor '{o}' equals truth")

        elif qid == 2:
            truth = check_task2(e, cons)
            check(correct_str == truth,
                  f"{did}: answer '{correct_str}' != computed '{truth}'")
            truth_set = parse_set(truth)
            for o in e["options"]:
                if o != correct_str:
                    os_ = parse_set(o)
                    check(os_ is not None and os_ != truth_set,
                          f"{did}: distractor '{o}' not genuinely wrong")

        elif qid == 3:
            codes = [parse_code(o) for o in e["options"]]
            check(all(c is not None for c in codes), f"{did}: unparsable option code")
            consistent_idx = [j for j, c in enumerate(codes)
                              if c is not None and all(score(g, c) == (b, w)
                                                       for g, b, w in rows)]
            check(len(consistent_idx) == 1,
                  f"{did}: {len(consistent_idx)} consistent options, expected 1")
            check(consistent_idx == [e["answer"] - 1],
                  f"{did}: consistent option is not the answer")
            check(codes[e["answer"] - 1] in cons,
                  f"{did}: answer code not in consistent set")

        elif qid == 4:
            check(len(cons) == 1, f"{did}: board not uniquely determined ({len(cons)})")
            truth = fmt_code(cons[0])
            check(correct_str == truth,
                  f"{did}: answer '{correct_str}' != deduced '{truth}'")
            for o in e["options"]:
                if o != correct_str:
                    c = parse_code(o)
                    check(c is not None and not all(score(g, c) == (b, w)
                                                    for g, b, w in rows),
                          f"{did}: distractor '{o}' is consistent!")

        elif qid == 5:
            codes = [parse_code(o) for o in e["options"]]
            check(all(c is not None for c in codes), f"{did}: unparsable candidate")
            check(all(c in set(cons) for c in codes),
                  f"{did}: candidate outside the consistent set")
            worsts = [worst_case(c, cons) for c in codes]
            m = min(worsts)
            check(worsts.count(m) == 1, f"{did}: no strict unique argmin {worsts}")
            check(worsts.index(m) == e["answer"] - 1,
                  f"{did}: minimax argmin is option {worsts.index(m) + 1}, "
                  f"answer says {e['answer']}")

        # analysis must mention the final answer and option number
        check(correct_str in e["analysis"],
              f"{did}: analysis does not mention '{correct_str}'")
        check(re.search(rf"So the answer is .+\. The option number is {e['answer']}\.",
                        e["analysis"]) is not None,
              f"{did}: analysis missing final 'So the answer is ... option number' line")

    # dataset-level checks
    plot_counts = Counter(e["plot_level"] for e in data)
    check(plot_counts == {"Easy": 20, "Medium": 20, "Hard": 20},
          f"plot_level distribution off: {dict(plot_counts)}")
    for qid in range(1, 6):
        check(per_task[qid] >= 4, f"task {qid} appears only {per_task[qid]} times")
    none_correct = sum(1 for e in data
                       if e["question_id"] == 2 and e["options"][e["answer"] - 1] == "None")
    check(none_correct <= 3, f"'None' correct task-2 answers: {none_correct} > 3")
    images = {e["image"] for e in data}
    check(len(images) == 15, f"expected 15 distinct images, got {len(images)}")

    print(f"Checked {len(data)} entries, {checks} individual checks.")
    print("Entries per task:", dict(sorted(per_task.items())))
    print("Entries per plot_level:", dict(plot_counts),
          "| 'None'-correct task2:", none_correct)
    if errors:
        print(f"\n{len(errors)} FAILURE(S):")
        for msg in errors[:40]:
            print(" -", msg)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
