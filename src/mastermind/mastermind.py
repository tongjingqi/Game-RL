"""Mastermind GameQA dataset generator: game logic, rendering and QA builders.

Classic Mastermind: a hidden 4-peg secret code (6 colors, repeats allowed).
Each guess row on the board shows 4 colored pegs and its feedback pegs:
black = right color in the right position, white = right color, wrong position.
All deduction tasks are computed by brute force over the 6**4 = 1296 codes.
"""

import random
from itertools import product

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Game constants
# ---------------------------------------------------------------------------

COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
COLOR_RGB = {
    "red": (231, 76, 60),
    "orange": (243, 156, 18),
    "yellow": (241, 196, 15),
    "green": (39, 174, 96),
    "blue": (52, 152, 219),
    "purple": (155, 89, 182),
}
CODE_LENGTH = 4
NUM_COLORS = 6
ALL_CODES = list(product(range(NUM_COLORS), repeat=CODE_LENGTH))  # 1296

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_BOLD = f"{FONT_DIR}/DejaVuSans-Bold.ttf"
FONT_REG = f"{FONT_DIR}/DejaVuSans.ttf"

GAME_RULES = (
    "You are looking at a Mastermind board. Mastermind is a code-breaking game: "
    "a hidden secret code consists of 4 colored pegs in a row (positions 1 to 4, "
    "left to right), each chosen from 6 available colors (red, orange, yellow, "
    "green, blue, purple), and the same color may appear multiple times in the code. "
    "The secret code is covered at the top of the board and drawn as four dark "
    "wooden caps marked with '?'. Below it, each numbered row shows one past guess "
    "of 4 colored pegs (left to right = positions 1 to 4) together with its "
    "feedback: a 2x2 cluster of small pegs on the right side of the row. A black "
    "feedback peg means one peg of that guess is the correct color in the correct "
    "position; a white feedback peg means one peg is a correct color but in the "
    "wrong position. The positions of the feedback pegs inside the cluster carry "
    "no meaning (black pegs are drawn first, then white ones), and the number of "
    "black plus white pegs never exceeds 4. Guess rows are numbered 1 to N from "
    "top to bottom, printed on the left of each row. A legend and the palette of "
    "the 6 available colors are shown at the bottom of the board. Every feedback "
    "shown on the board is correct."
)

TASK_META = {
    1: ("Target Perception", "Easy",
        "Read a guess row: its peg colors, its feedback counts, or color occurrences"),
    2: ("State Prediction", "Medium",
        "Determine which colors are certainly in or certainly not in the secret code"),
    3: ("State Prediction", "Medium",
        "Find the candidate code that is consistent with every row of feedback"),
    4: ("State Prediction", "Hard",
        "Deduce the exact secret code from all the feedback"),
    5: ("Strategy Optimization", "Hard",
        "Pick the next guess that minimizes the worst-case number of remaining codes"),
}


# ---------------------------------------------------------------------------
# Core rule logic
# ---------------------------------------------------------------------------

def feedback(guess, secret):
    """Return (black, white) for a guess against a secret (int tuples)."""
    black = sum(1 for a, b in zip(guess, secret) if a == b)
    common = 0
    for c in range(NUM_COLORS):
        common += min(guess.count(c), secret.count(c))
    return black, common - black


def consistent_codes(guesses):
    """All codes consistent with every shown row.

    guesses: list of (pegs, black, white) with pegs an int tuple.
    A candidate secret x is consistent with row (g, b, w) iff feedback(g, x) == (b, w).
    """
    cons = []
    for x in ALL_CODES:
        if all(feedback(g, x) == (b, w) for g, b, w in guesses):
            cons.append(x)
    return cons


def consistent_prefix_sizes(guesses):
    """Number of consistent codes after applying row 1, rows 1-2, ... ."""
    sizes = []
    cons = list(ALL_CODES)
    for g, b, w in guesses:
        cons = [x for x in cons if feedback(g, x) == (b, w)]
        sizes.append(len(cons))
    return sizes


def certainly_in(cons):
    """Colors (indices) present in EVERY consistent code."""
    return {c for c in range(NUM_COLORS) if all(c in x for x in cons)}


def certainly_not_in(cons):
    """Colors (indices) present in NO consistent code."""
    return {c for c in range(NUM_COLORS) if all(c not in x for x in cons)}


def worst_case_buckets(candidate, cons):
    """Worst-case number of remaining codes after guessing candidate.

    Partitions the consistent set by the feedback the candidate would receive;
    returns the size of the largest bucket.
    """
    buckets = {}
    for x in cons:
        f = feedback(candidate, x)
        buckets[f] = buckets.get(f, 0) + 1
    return max(buckets.values())


# ---------------------------------------------------------------------------
# Board generation
# ---------------------------------------------------------------------------

def _make_board(secret, rows, cons, mode):
    """Assemble a board dict, recomputing feedback for safety."""
    guesses = []
    for pegs, b, w in rows:
        rb, rw = feedback(pegs, secret)
        assert (rb, rw) == (b, w), "stored feedback mismatch"
        guesses.append((pegs, b, w))
    return {
        "secret": secret,
        "guesses": guesses,
        "consistent": list(cons),
        "consistent_set": set(cons),
        "mode": mode,
    }


def generate_board(rng, n_rows, mode, max_attempts=500):
    """Generate a board.

    mode "multi":  final consistent set size in [10, 150] (for tasks 2, 3, 5).
    mode "unique": final consistent set size exactly 1 (for task 4).
    Every guess strictly reduces the consistent set; no guess scores 4 black
    (the game would already be over and the secret visually given away).
    """
    final_target = 45.0 if mode == "multi" else 1.0
    for _ in range(max_attempts):
        secret = tuple(rng.randrange(NUM_COLORS) for _ in range(CODE_LENGTH))
        cons = list(ALL_CODES)
        rows = []
        ok = True
        for r in range(n_rows):
            last = r == n_rows - 1
            target = 1296.0 * (final_target / 1296.0) ** ((r + 1) / n_rows)
            pool = set()
            while len(pool) < 120:
                pool.add(tuple(rng.randrange(NUM_COLORS) for _ in range(CODE_LENGTH)))
            pool.update(rng.sample(cons, min(50, len(cons))))
            best = None
            for g in pool:
                f = feedback(g, secret)
                if f[0] == CODE_LENGTH:
                    continue  # never show a fully correct guess
                new = [x for x in cons if feedback(x, g) == f]
                ns = len(new)
                if ns == 0 or ns >= len(cons):
                    continue  # a guess must strictly reduce the set
                if mode == "multi":
                    if last:
                        if not (10 <= ns <= 150):
                            continue
                        score = abs(ns - final_target)
                    else:
                        if ns < 24:
                            continue
                        score = abs(ns - target)
                else:  # unique
                    if last:
                        if ns != 1:
                            continue
                        score = 0.0
                    else:
                        if ns < 2:
                            continue
                        score = abs(ns - target)
                if best is None or score < best[0]:
                    best = (score, g, f, new)
            if best is None:
                ok = False
                break
            _, g, f, cons = best
            rows.append((g, f[0], f[1]))
        if not ok:
            continue
        if mode == "multi" and 10 <= len(cons) <= 150:
            return _make_board(secret, rows, cons, mode)
        if mode == "unique" and len(cons) == 1 and cons[0] == secret:
            return _make_board(secret, rows, cons, mode)
    raise RuntimeError(f"could not generate a {mode} board with {n_rows} rows")


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_code(code):
    """'red, blue, green, red' for an int tuple."""
    return ", ".join(COLORS[i] for i in code)


def parse_code(text):
    """Inverse of fmt_code."""
    return tuple(COLORS.index(p.strip()) for p in text.split(","))


def fmt_set(color_idx_set):
    """Canonical string for a set of color indices, 'None' when empty."""
    if not color_idx_set:
        return "None"
    return ", ".join(c for i, c in enumerate(COLORS) if i in color_idx_set)


def make_mcq(rng, correct, distractors):
    """Build the option list: correct + unique distractors, shuffled.

    Returns (options, answer_index_1based).
    """
    opts = [correct]
    seen = {correct}
    for d in distractors:
        if d not in seen:
            opts.append(d)
            seen.add(d)
    assert len(opts) >= 4, "not enough distinct options"
    rng.shuffle(opts)
    return opts, opts.index(correct) + 1


# ---------------------------------------------------------------------------
# QA builders (each returns dict with question body, options, answer, analysis)
# ---------------------------------------------------------------------------

def build_task1(rng, board):
    """Target Perception / Easy: read a row (colors / feedback / color count)."""
    guesses = board["guesses"]
    variant = rng.choice(["a", "b", "c"])
    k = rng.randrange(len(guesses))
    pegs, b, w = guesses[k]
    row = k + 1
    row_str = fmt_code(pegs)
    if variant == "a":
        correct = row_str
        muts = set()
        while len(muts) < 7:
            m = list(pegs)
            r = rng.random()
            if r < 0.45:
                i, j = rng.sample(range(CODE_LENGTH), 2)
                m[i], m[j] = m[j], m[i]
            elif r < 0.85:
                i = rng.randrange(CODE_LENGTH)
                m[i] = (m[i] + 1 + rng.randrange(NUM_COLORS - 1)) % NUM_COLORS
            else:
                m = m[::-1]
            t = tuple(m)
            if t != pegs:
                muts.add(t)
        distractors = [fmt_code(t) for t in muts]
        body = (f"What are the four colors of the guess in row {row}, "
                f"from left to right?")
        explanation = (f"Reading row {row} on the board from left to right, the "
                       f"four pegs are: {row_str}.")
    elif variant == "b":
        correct = f"{b} black, {w} white"
        pairs = [(bb, ww) for bb in range(5) for ww in range(5)
                 if bb + ww <= 4 and not (bb == 3 and ww == 1) and (bb, ww) != (b, w)]
        rng.shuffle(pairs)
        distractors = [f"{bb} black, {ww} white" for bb, ww in pairs[:7]]
        body = (f"How many black and how many white feedback pegs did the guess "
                f"in row {row} receive?")
        explanation = (f"The 2x2 feedback cluster next to row {row} shows {b} black "
                       f"peg(s) and {w} white peg(s).")
    else:
        color = rng.randrange(NUM_COLORS)
        count = pegs.count(color)
        correct = str(count)
        distractors = [str(v) for v in range(5) if v != count]
        body = (f"How many {COLORS[color]} pegs appear in the guess in row {row}?")
        explanation = (f"Row {row} is {row_str}. The color {COLORS[color]} appears "
                       f"{count} time(s) in it.")
    opts, ans = make_mcq(rng, correct, distractors)
    analysis = (f"{explanation}\n\nSo the answer is {correct}. "
                f"The option number is {ans}.")
    return {"body": body, "options": opts, "answer": ans, "analysis": analysis}


def build_task2(rng, board, variant):
    """State Prediction / Medium: colors certainly in / certainly not in.

    Returns None when the requested variant has an unusable correct answer
    ((a) requires a non-empty certainly-in set).
    """
    cons = board["consistent"]
    s_in = certainly_in(cons)
    s_out = certainly_not_in(cons)
    if variant == "a":
        if not s_in:
            return None
        correct_set = s_in
        body = ("Based on all the feedback shown on the board, which colors are "
                "CERTAINLY in the secret code? (List every color that must appear "
                "in the code at least once.)")
    else:
        correct_set = s_out
        body = ("Based on all the feedback shown on the board, which colors are "
                "CERTAINLY NOT in the secret code? (List every color that "
                "definitely does not appear in the code.)")
    correct = fmt_set(correct_set)
    # near-miss distractor sets
    cand_sets = [frozenset()]  # "None" as a distractor when not correct
    for c in range(NUM_COLORS):
        if c not in correct_set:
            cand_sets.append(frozenset(set(correct_set) | {c}))
    for c in correct_set:
        cand_sets.append(frozenset(set(correct_set) - {c}))
    for c in correct_set:
        for d in range(NUM_COLORS):
            if d not in correct_set:
                cand_sets.append(frozenset((set(correct_set) - {c}) | {d}))
    rng.shuffle(cand_sets)
    distractors = []
    seen = {correct}
    for s in cand_sets:
        f = fmt_set(s)
        if f not in seen:
            distractors.append(f)
            seen.add(f)
        if len(distractors) == 7:
            break
    while len(distractors) < 7:
        s = frozenset(rng.sample(range(NUM_COLORS), rng.randrange(1, 5)))
        f = fmt_set(s)
        if f not in seen:
            distractors.append(f)
            seen.add(f)
    opts, ans = make_mcq(rng, correct, distractors)
    in_str = fmt_set(certainly_in(cons))
    out_str = fmt_set(certainly_not_in(cons))
    in_part = (f"Every one of these remaining codes contains: {in_str}."
               if s_in else "No single color appears in every one of them.")
    out_part = (f"The colors that appear in none of them are: {out_str}."
                if s_out else "Every available color appears in at least one of them.")
    analysis = (
        f"Checking all 1296 possible codes against every row of feedback leaves "
        f"{len(cons)} code(s) that could still be the secret. {in_part} {out_part} "
        f"Therefore the colors that are CERTAINLY "
        f"{'in' if variant == 'a' else 'NOT in'} the secret code are: {correct}."
        f"\n\nSo the answer is {correct}. The option number is {ans}.")
    return {"body": body, "options": opts, "answer": ans, "analysis": analysis,
            "none_correct": correct == "None"}


def _near_miss_codes(rng, board, n):
    """Inconsistent codes that fail the feedback on as few rows as possible.

    Strong distractors fail exactly one row by exactly one peg; medium ones fail
    exactly one row by more. Returns a list of (code, fails) where fails is a
    list of (row_index, (black, white)_the_code_would_score).
    """
    guesses = board["guesses"]
    cons_set = board["consistent_set"]
    strong, medium = [], []
    tried = set()
    for _ in range(40000):
        x = tuple(rng.randrange(NUM_COLORS) for _ in range(CODE_LENGTH))
        if x in tried:
            continue
        tried.add(x)
        if len(tried) >= len(ALL_CODES):
            break
        if x in cons_set:
            continue
        fails = []
        for idx, (g, b, w) in enumerate(guesses):
            fx = feedback(x, g)
            if fx != (b, w):
                fails.append((idx, fx))
        if len(fails) == 1:
            idx, fx = fails[0]
            _, b, w = guesses[idx]
            diff = abs(fx[0] - b) + abs(fx[1] - w)
            (strong if diff == 1 else medium).append((x, fails))
        if len(strong) >= n:
            break
    pool = strong[:n]
    if len(pool) < n:
        pool = (strong + medium)[:n]
    return pool if len(pool) >= n else None


def build_task3(rng, board):
    """State Prediction / Medium: which candidate code is consistent with all rows."""
    cons = board["consistent"]
    guesses = board["guesses"]
    near = _near_miss_codes(rng, board, 7)
    if near is None:
        return None
    correct_code = rng.choice(cons)
    correct = fmt_code(correct_code)
    distractors = [fmt_code(x) for x, _ in near]
    opts, ans = make_mcq(rng, correct, distractors)
    lines = [f"Test the candidate '{correct}' against every row of the board:"]
    for idx, (g, b, w) in enumerate(guesses):
        fx = feedback(correct_code, g)
        lines.append(
            f"- Row {idx + 1} (guess {fmt_code(g)}): the board shows {b} black, "
            f"{w} white; the candidate scores {fx[0]} black, {fx[1]} white - match.")
    lines.append("It matches every row, so it is consistent. The other options "
                 "each fail at least one row, for example:")
    for x, fails in near[:2]:
        idx, fx = fails[0]
        g, b, w = guesses[idx]
        lines.append(
            f"- '{fmt_code(x)}' fails row {idx + 1}: it would score {fx[0]} black, "
            f"{fx[1]} white, but the board shows {b} black, {w} white.")
    analysis = ("\n".join(lines) +
                f"\n\nSo the answer is {correct}. The option number is {ans}.")
    return {"body": "Which ONE of the following candidate codes is consistent with "
                    "every row of feedback shown on the board?",
            "options": opts, "answer": ans, "analysis": analysis}


def build_task4(rng, board):
    """State Prediction / Hard: deduce the exact secret code (unique board)."""
    cons = board["consistent"]
    if len(cons) != 1:
        return None
    secret = cons[0]
    near = _near_miss_codes(rng, board, 7)
    if near is None:
        return None
    correct = fmt_code(secret)
    distractors = [fmt_code(x) for x, _ in near]
    opts, ans = make_mcq(rng, correct, distractors)
    sizes = consistent_prefix_sizes(board["guesses"])
    lines = ["Start from all 1296 possible codes and keep only those consistent "
             "with each row's feedback:"]
    for i, s in enumerate(sizes):
        lines.append(f"- After row {i + 1}: {s} code(s) remain consistent.")
    lines.append(f"After the last row only one code remains: {correct}. It is the "
                 f"only code consistent with all the feedback, so it must be the "
                 f"secret code.")
    analysis = ("\n".join(lines) +
                f"\n\nSo the answer is {correct}. The option number is {ans}.")
    return {"body": "Using all the feedback shown on the board, deduce the exact "
                    "secret code (positions 1 to 4, left to right).",
            "options": opts, "answer": ans, "analysis": analysis}


def build_task5(rng, board, n_cand=4, max_tries=3000):
    """Strategy Optimization / Hard: best next guess by worst-case minimization."""
    cons = board["consistent"]
    if not (4 <= len(cons)):
        return None
    for _ in range(max_tries):
        cands = rng.sample(cons, n_cand)
        worsts = [worst_case_buckets(c, cons) for c in cands]
        m = min(worsts)
        if worsts.count(m) == 1:
            best_idx = worsts.index(m)
            break
    else:
        return None
    correct_code = cands[best_idx]
    correct = fmt_code(correct_code)
    opts, ans = make_mcq(rng, correct, [fmt_code(c) for c in cands if c != correct_code])
    order = sorted(zip(cands, worsts), key=lambda t: t[1])
    lines = [f"There are {len(cons)} codes still consistent with the board. For "
             f"each candidate guess, split those codes into groups that would get "
             f"the same feedback; the worst case is the largest group:"]
    for c, wv in order:
        lines.append(f"- {fmt_code(c)} -> worst case {wv} code(s) remain")
    lines.append(f"The smallest worst case is {m}, achieved by {correct}.")
    analysis = ("\n".join(lines) +
                f"\n\nSo the answer is {correct}. The option number is {ans}.")
    return {"body": "You may ask for feedback on one more guess. Consider the four "
                    "candidate guesses listed in the options. Which one minimizes "
                    "the WORST-CASE number of remaining possible secret codes "
                    "after its feedback is revealed? (The worst case is the size "
                    "of the largest group of still-possible codes that would share "
                    "the same feedback.)",
            "options": opts, "answer": ans, "analysis": analysis}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

W = 560
ROWS_TOP = 172
ROW_H = 74
PEG_D = 54
SOCKET_D = 60
PEG_XS = [150, 224, 298, 372]
ROWNO_X = 42
WELL_X0, WELL_X1 = 434, 528

_CREAM = (240, 226, 200, 255)
_GOLD = (250, 210, 120, 255)
_PEG_CACHE = {}


def _font(path, size):
    return ImageFont.truetype(path, size)


def peg_sprite(rgb, d):
    """Glossy peg sprite (RGBA), supersampled 3x then downscaled."""
    key = (rgb, d)
    if key in _PEG_CACHE:
        return _PEG_CACHE[key]
    S = 3
    D = d * S
    yy, xx = np.mgrid[0:D, 0:D].astype(np.float64)
    c = (D - 1) / 2.0
    r = D / 2.0 - 1.0
    nx = (xx - c) / r
    ny = (yy - c) / r
    d2 = nx * nx + ny * ny
    inside = d2 <= 1.0
    shade = 1.0 - 0.34 * np.clip(d2, 0, 1) ** 0.75
    spec = np.exp(-(((nx + 0.34) ** 2) / 0.09 + ((ny + 0.38) ** 2) / 0.05))
    bounce = np.exp(-(((nx - 0.45) ** 2) / 0.25 + ((ny - 0.80) ** 2) / 0.06))
    base = np.array(rgb, dtype=np.float64)
    arr = np.zeros((D, D, 4), dtype=np.float64)
    for ch in range(3):
        v = base[ch] * shade + 200.0 * spec + 26.0 * bounce
        v = np.where(d2 > 0.90, v * 0.62, v)  # dark rim
        arr[..., ch] = np.clip(v, 0, 255)
    arr[..., 3] = np.where(inside, 255.0, 0.0)
    img = Image.fromarray(arr.astype(np.uint8), "RGBA").resize((d, d), Image.LANCZOS)
    _PEG_CACHE[key] = img
    return img


def paste_peg(img, sprite, cx, cy, shadow=True):
    d = sprite.width
    if shadow:
        sh = Image.new("RGBA", (d + 14, d // 3 + 12), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([5, 5, d + 9, d // 3 + 7], fill=(0, 0, 0, 110))
        sh = sh.filter(ImageFilter.GaussianBlur(3))
        img.paste(sh, (int(cx - d / 2 - 7), int(cy + d * 0.30)), sh)
    img.paste(sprite, (int(cx - d / 2), int(cy - d / 2)), sprite)


def _text_center(draw, cx, cy, s, font, fill):
    l, t, r, b = draw.textbbox((0, 0), s, font=font)
    draw.text((cx - (r - l) / 2 - l, cy - (b - t) / 2 - t), s, font=font, fill=fill)


def wood_panel(w, h, seed):
    """Wooden board panel with grain streaks, vignette and rounded corners."""
    rng = random.Random(seed)
    img = Image.new("RGBA", (w, h), (118, 72, 40, 255))
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(120):
        y0 = rng.uniform(0, h)
        amp = rng.uniform(0.6, 2.6)
        lam = rng.uniform(60, 220)
        phi = rng.uniform(0, 6.28)
        dark = rng.random() < 0.6
        col = ((58, 34, 18, rng.randint(10, 26)) if dark
               else (190, 140, 90, rng.randint(8, 18)))
        wd = rng.choice([1, 1, 2])
        pts = [(x, y0 + amp * np.sin(x / lam + phi)) for x in range(0, w + 8, 8)]
        d.line(pts, fill=col, width=wd)
    img = Image.alpha_composite(img, ov)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    nx = (xx - w / 2) / (w / 2)
    ny = (yy - h / 2) / (h / 2)
    vig = 1 - 0.16 * np.clip(nx * nx + ny * ny, 0, 1) ** 1.2
    arr = np.asarray(img).astype(np.float64)
    arr[..., :3] *= vig[..., None]
    img = Image.fromarray(arr.astype(np.uint8), "RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=16, fill=255)
    bg = Image.new("RGBA", (w, h), (28, 18, 12, 255))
    bg.paste(img, (0, 0), mask)
    return bg


def _recessed(draw, box, radius=10, fill=(64, 39, 23, 255)):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=radius, fill=fill)
    draw.rounded_rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], radius=max(radius - 2, 1),
                           outline=(35, 20, 12, 150), width=2)
    draw.line([(x0 + radius, y1 - 2), (x1 - radius, y1 - 2)],
              fill=(150, 105, 60, 110), width=2)


def _groove(draw, y, w):
    draw.line([(24, y), (w - 24, y)], fill=(58, 34, 18, 220), width=2)
    draw.line([(24, y + 2), (w - 24, y + 2)], fill=(152, 106, 60, 130), width=1)


def covered_cap(d):
    """Dark wooden cap with a gold '?'."""
    cap = peg_sprite((84, 58, 36), d).copy()
    dr = ImageDraw.Draw(cap)
    f = _font(FONT_BOLD, int(d * 0.50))
    _text_center(dr, d / 2 + 1, d / 2 + 1, "?", f, (30, 18, 10, 220))
    _text_center(dr, d / 2, d / 2 - 1, "?", f, (250, 210, 120, 255))
    return cap


def render_board(board, path):
    """Render one board to PNG. Returns (width, height)."""
    guesses = board["guesses"]
    R = len(guesses)
    rows_bottom = ROWS_TOP + R * ROW_H
    H = rows_bottom + 88
    img = wood_panel(W, H, seed=4242 + R * 131 + board["secret"][0])
    d = ImageDraw.Draw(img)

    f_title = _font(FONT_BOLD, 34)
    f_cap = _font(FONT_BOLD, 11)
    f_small = _font(FONT_REG, 13)
    f_pal = _font(FONT_REG, 12)
    f_badge = _font(FONT_BOLD, 15)

    # inner frame
    d.rounded_rectangle([4, 4, W - 5, H - 5], radius=13,
                        outline=(168, 124, 72, 190), width=2)

    # title
    _text_center(d, W / 2 + 1, 36 + 1, "Mastermind", f_title, (40, 24, 14, 255))
    _text_center(d, W / 2, 36, "Mastermind", f_title, _CREAM)

    # secret strip
    _recessed(d, [30, 62, W - 30, 134], radius=12, fill=(66, 40, 24, 255))
    _text_center(d, 84, 88, "SECRET", f_cap, _GOLD)
    _text_center(d, 84, 106, "(hidden)", f_cap, (220, 195, 150, 255))
    for x in PEG_XS:
        paste_peg(img, covered_cap(48), x, 98, shadow=True)
    # small gold lock on the right of the strip
    d.arc([468, 78, 486, 98], start=180, end=360, fill=_GOLD, width=3)
    d.rounded_rectangle([464, 90, 490, 112], radius=4, fill=(212, 175, 55, 255),
                        outline=(120, 90, 20, 255), width=1)
    d.ellipse([474, 97, 480, 103], fill=(90, 60, 15, 255))

    _groove(d, 148, W)

    # guess rows
    badge_r = 13
    for i, (pegs, b, w) in enumerate(guesses):
        cy = ROWS_TOP + i * ROW_H + ROW_H // 2
        if i > 0:
            _groove(d, ROWS_TOP + i * ROW_H, W)
        # row number badge
        d.ellipse([ROWNO_X - badge_r, cy - badge_r, ROWNO_X + badge_r, cy + badge_r],
                  fill=(66, 40, 24, 255), outline=(190, 150, 90, 255), width=2)
        _text_center(d, ROWNO_X, cy, str(i + 1), f_badge, _CREAM)
        # sockets + pegs
        for j, x in enumerate(PEG_XS):
            d.ellipse([x - SOCKET_D / 2, cy - SOCKET_D / 2, x + SOCKET_D / 2, cy + SOCKET_D / 2],
                      fill=(52, 32, 18, 255), outline=(35, 20, 12, 255), width=2)
            paste_peg(img, peg_sprite(COLOR_RGB[COLORS[pegs[j]]], PEG_D), x, cy)
        # feedback well
        _recessed(d, [WELL_X0, cy - 27, WELL_X1, cy + 27], radius=9,
                  fill=(60, 36, 22, 255))
        slots = [(WELL_X0 + 32, cy - 12), (WELL_X0 + 62, cy - 12),
                 (WELL_X0 + 32, cy + 12), (WELL_X0 + 62, cy + 12)]
        pegs_to_draw = [(30, 30, 34)] * b + [(236, 236, 230)] * w
        for sx, sy in slots:
            d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=(40, 24, 14, 255))
        for (sx, sy), rgb in zip(slots, pegs_to_draw):
            paste_peg(img, peg_sprite(rgb, 17), sx, sy, shadow=False)

    # legend strip
    _groove(d, rows_bottom + 6, W)
    ly = rows_bottom + 24
    black = peg_sprite((30, 30, 34), 15)
    white = peg_sprite((236, 236, 230), 15)
    t1 = "= right color, right position"
    t2 = "= right color, wrong position"
    w1 = f_small.getlength(t1) + 24
    w2 = f_small.getlength(t2) + 24
    x = (W - (w1 + w2 + 30)) / 2
    img.paste(black, (int(x), int(ly - 7)), black)
    d.text((x + 22, ly - 8), t1, font=f_small, fill=_CREAM)
    x += w1 + 30
    img.paste(white, (int(x), int(ly - 7)), white)
    d.text((x + 22, ly - 8), t2, font=f_small, fill=_CREAM)

    # palette strip
    py = rows_bottom + 56
    items = []
    total = 0
    for cname in COLORS:
        tw = f_pal.getlength(cname)
        items.append((cname, tw))
        total += 20 + tw
    total += 14 * (len(items) - 1)
    x = (W - total) / 2
    for cname, tw in items:
        sp = peg_sprite(COLOR_RGB[cname], 16)
        img.paste(sp, (int(x), int(py - 8)), sp)
        d.text((x + 20, py - 7), cname, font=f_pal, fill=_CREAM)
        x += 20 + tw + 14

    img.convert("RGB").save(path)
    return W, H


# ---------------------------------------------------------------------------
# State (de)serialization
# ---------------------------------------------------------------------------

def board_to_state(board):
    return {
        "code_length": CODE_LENGTH,
        "num_colors": NUM_COLORS,
        "colors": list(COLORS),
        "board_type": board["mode"],
        "secret": [COLORS[i] for i in board["secret"]],
        "guesses": [
            {"row": i + 1,
             "pegs": [COLORS[c] for c in pegs],
             "black": b, "white": w}
            for i, (pegs, b, w) in enumerate(board["guesses"])
        ],
        "consistent_count": len(board["consistent"]),
    }


def state_to_board(state):
    """Parse a state file back into the internal board representation."""
    secret = parse_code(", ".join(state["secret"]))
    guesses = [(parse_code(", ".join(g["pegs"])), g["black"], g["white"])
               for g in state["guesses"]]
    cons = consistent_codes(guesses)
    return {
        "secret": secret,
        "guesses": guesses,
        "consistent": cons,
        "consistent_set": set(cons),
        "mode": state.get("board_type", "multi"),
    }
