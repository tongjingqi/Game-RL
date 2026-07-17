"""Domino Chain Matching — game logic, PIL rendering and QA builders.

A chain of domino tiles (double-six set, 0-0 .. 6-6) is laid out left to right.
Adjacent tiles match: chain[i][1] == chain[i+1][0]. Doubles are drawn vertical.
Below the chain sits a hand of labeled spare tiles (A, B, C, ...).
"""

import os
import itertools

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

GAME_RULES = (
    "This is a Domino Chain puzzle. A domino tile is a rectangular piece divided into two "
    "halves; each half shows from 0 (blank) to 6 pips (dots), and the number of pips is the "
    "value of that half. A tile whose two halves are equal (for example 4-4) is called a "
    "double. On the green table a chain of domino tiles is laid out in a single horizontal "
    "row from left to right. Adjacent tiles in the chain always match: the value of the "
    "right half of every tile equals the value of the left half of the next tile. Double "
    "tiles in the chain are placed vertically (taller than they are wide); every other chain "
    "tile is horizontal (wider than it is tall), and the left/right halves of a horizontal "
    "tile are exactly what they look like. The chain has exactly two open ends: the LEFT "
    "open end is the value of the left half of the leftmost tile, and the RIGHT open end is "
    "the value of the right half of the rightmost tile (if an end tile is a vertical double, "
    "the open value is simply its value). Below the chain, on the darker rack, there is a "
    "hand of spare tiles labeled with the gold letters A, B, C, ... printed above them. "
    "Every hand tile is drawn vertically; a hand tile with U pips on its upper half and D "
    "pips on its lower half is written as (U|D). A hand tile can be legally played on an "
    "open end of the chain if either of its two halves matches the value of that open end. "
    "When a tile is played it is rotated as needed so that its matching half touches the "
    "chain, and its other half becomes the new value of that open end; the other open end "
    "does not change. "
)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

TASK1_SUBTYPES = ("a", "b", "c", "d")

# Standard pip layouts on a half-square, as (fx, fy) fractions of the half side.
PIP_POS = {
    0: [],
    1: [(0.5, 0.5)],
    2: [(0.28, 0.28), (0.72, 0.72)],
    3: [(0.28, 0.28), (0.5, 0.5), (0.72, 0.72)],
    4: [(0.28, 0.28), (0.72, 0.28), (0.28, 0.72), (0.72, 0.72)],
    5: [(0.28, 0.28), (0.72, 0.28), (0.5, 0.5), (0.28, 0.72), (0.72, 0.72)],
    6: [(0.28, 0.24), (0.72, 0.24), (0.28, 0.5), (0.72, 0.5), (0.28, 0.76), (0.72, 0.76)],
}

IVORY_TOP = (253, 249, 239)
IVORY_BOT = (222, 211, 189)
TILE_BORDER = (52, 46, 38)
PIP_COLOR = (28, 25, 22)
GOLD = (238, 200, 96)
TITLE_COLOR = (243, 238, 222)
LEGEND_COLOR = (198, 208, 196)


def _font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


# --------------------------------------------------------------------------- #
# Board generation
# --------------------------------------------------------------------------- #

def all_tiles():
    """The 28 tiles of a double-six set as unordered (a, b) with a <= b."""
    return [(a, b) for a in range(7) for b in range(a, 7)]


def gen_chain(n, rng):
    """Build a random valid chain of n oriented tiles from the 28-set.

    Returns (chain, remaining_tiles) where chain[i][1] == chain[i+1][0],
    or (None, None) if the chain got stuck.
    """
    tiles = all_tiles()
    rng.shuffle(tiles)
    a, b = tiles.pop()
    chain = [[a, b]] if rng.random() < 0.5 else [[b, a]]
    while len(chain) < n:
        left_val, right_val = chain[0][0], chain[-1][1]
        idxs = [i for i, t in enumerate(tiles)
                if t[0] in (left_val, right_val) or t[1] in (left_val, right_val)]
        if not idxs:
            return None, None
        i = rng.choice(idxs)
        t = tiles.pop(i)
        sides = []
        if t[0] == left_val or t[1] == left_val:
            sides.append("L")
        if t[0] == right_val or t[1] == right_val:
            sides.append("R")
        side = rng.choice(sides)
        if side == "L":
            # Prepend [other, left_val] so its right half touches the old left end.
            tile = [t[1], t[0]] if t[0] == left_val else [t[0], t[1]]
            chain.insert(0, tile)
        else:
            # Append [right_val, other] so its left half touches the old right end.
            tile = [t[0], t[1]] if t[0] == right_val else [t[1], t[0]]
            chain.append(tile)
    return chain, tiles


def gen_hand(remaining, hn, open_left, open_right, rng):
    """Draw hn hand tiles from the remaining ones.

    Guarantees at least one playable and at least one unplayable tile so that
    the 'playable set' task is never trivial. Display orientation is random.
    """
    for _ in range(300):
        sample = rng.sample(remaining, hn)
        playable = [t for t in sample
                    if t[0] in (open_left, open_right) or t[1] in (open_left, open_right)]
        if not (1 <= len(playable) < hn):
            continue
        hand = []
        for i, t in enumerate(sample):
            u, d = (t[0], t[1]) if rng.random() < 0.5 else (t[1], t[0])
            hand.append({"label": chr(ord("A") + i), "tile": [u, d]})
        return hand
    return None


def gen_board(plot_level, rng):
    """Generate a complete board state dict for the given difficulty."""
    if plot_level == "Easy":
        n_chain, n_hand = 5, 4
    elif plot_level == "Medium":
        n_chain, n_hand = rng.choice([6, 7]), 5
    else:
        n_chain, n_hand = rng.choice([8, 9]), 6
    for _ in range(300):
        chain, remaining = gen_chain(n_chain, rng)
        if chain is None:
            continue
        hand = gen_hand(remaining, n_hand, chain[0][0], chain[-1][1], rng)
        if hand is None:
            continue
        has_double = (any(t[0] == t[1] for t in chain)
                      or any(h["tile"][0] == h["tile"][1] for h in hand))
        if not has_double:
            continue
        return {
            "chain": chain,
            "chain_oriented": True,
            "open_left": chain[0][0],
            "open_right": chain[-1][1],
            "hand": hand,
            "table_note": "doubles vertical",
            "plot_level": plot_level,
        }
    raise RuntimeError(f"could not generate a {plot_level} board")


# --------------------------------------------------------------------------- #
# Rule helpers (generator side)
# --------------------------------------------------------------------------- #

def tile_matches(tile, value):
    return tile[0] == value or tile[1] == value


def playable_labels(state):
    left, right = state["open_left"], state["open_right"]
    return [h["label"] for h in state["hand"]
            if tile_matches(h["tile"], left) or tile_matches(h["tile"], right)]


def other_half(tile, matched_value):
    """Value of the half opposite to the one matching matched_value."""
    return tile[1] if tile[0] == matched_value else tile[0]


def format_set(labels):
    """Human-readable label set: 'None', 'A only', 'A and C', 'B, D and F'."""
    labels = list(labels)
    if not labels:
        return "None"
    if len(labels) == 1:
        return f"{labels[0]} only"
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return ", ".join(labels[:-1]) + f" and {labels[-1]}"


def max_extend(state):
    """Maximum number of hand tiles that can be played (DFS with memo).

    Returns (best_count, moves) where moves is one achieving sequence of
    dicts {label, tile, end, new_left, new_right}.
    """
    tiles = [(h["label"], h["tile"][0], h["tile"][1]) for h in state["hand"]]
    n = len(tiles)
    memo = {}

    def dfs(mask, left, right):
        key = (mask, left, right)
        if key in memo:
            return memo[key]
        best = 0
        for i in range(n):
            if mask & (1 << i):
                continue
            _, a, b = tiles[i]
            if a == left or b == left:
                best = max(best, 1 + dfs(mask | (1 << i),
                                         b if a == left else a, right))
            if a == right or b == right:
                best = max(best, 1 + dfs(mask | (1 << i),
                                         left, b if a == right else a))
        memo[key] = best
        return best

    # Reconstruct one achieving sequence greedily using the memoized counts.
    moves = []
    mask, left, right = 0, state["open_left"], state["open_right"]
    while True:
        cur = dfs(mask, left, right)
        if cur == 0:
            break
        for i in range(n):
            if mask & (1 << i):
                continue
            label, a, b = tiles[i]
            if a == left or b == left:
                nl = b if a == left else a
                if dfs(mask | (1 << i), nl, right) == cur - 1:
                    moves.append({"label": label, "tile": [a, b], "end": "LEFT",
                                  "new_left": nl, "new_right": right})
                    mask |= (1 << i)
                    left = nl
                    break
            if a == right or b == right:
                nr = b if a == right else a
                if dfs(mask | (1 << i), left, nr) == cur - 1:
                    moves.append({"label": label, "tile": [a, b], "end": "RIGHT",
                                  "new_left": left, "new_right": nr})
                    mask |= (1 << i)
                    right = nr
                    break
    return dfs(0, state["open_left"], state["open_right"]), moves


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def make_felt(width, height, np_rng, ss):
    """Dark-green casino felt with radial vignette, grain noise and a wood frame."""
    w, h = width * ss, height * ss
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dist = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    vignette = 1.0 - 0.30 * np.clip(dist / 1.35, 0.0, 1.0) ** 2
    base = np.zeros((h, w, 3), dtype=np.float32)
    base[..., 0], base[..., 1], base[..., 2] = 25.0, 96.0, 57.0
    noise = np_rng.uniform(-5.0, 5.0, (h, w, 1)).astype(np.float32)
    arr = np.clip(base * vignette[..., None] + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB").convert("RGBA")
    dr = ImageDraw.Draw(img)
    fw = 9 * ss
    dr.rectangle([0, 0, w - 1, h - 1], outline=(122, 80, 44, 255), width=fw)
    dr.rectangle([fw, fw, w - 1 - fw, h - 1 - fw], outline=(64, 40, 22, 255),
                 width=max(1, ss))
    dr.rectangle([0, 0, w - 1, h - 1], outline=(168, 116, 70, 255), width=max(1, ss))
    return img


def draw_pips(dr, ox, oy, size, value, ss):
    """Draw the pips of one half-square of side `size` (already ss-scaled)."""
    r = max(2, int(round(size * 0.085)))
    for fx, fy in PIP_POS[value]:
        cx, cy = ox + fx * size, oy + fy * size
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PIP_COLOR + (255,))
        hr = max(1, r // 3)
        dr.ellipse([cx - r + hr, cy - r + hr, cx - r + 2 * hr, cy - r + 2 * hr],
                   fill=(110, 104, 94, 200))


def draw_tile(base, x, y, half, va, vb, orient, ss):
    """Draw one domino tile; x, y, half are in final pixels (scaled internally).

    orient 'H': width 2*half, height half, va = left half, vb = right half.
    orient 'V': width half, height 2*half, va = upper half, vb = lower half.
    """
    if orient == "H":
        w, ht = 2 * half, half
    else:
        w, ht = half, 2 * half
    radius = max(4, half // 7) * ss

    # Soft drop shadow.
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([x * ss + 2 * ss, y * ss + 3 * ss,
                          (x + w) * ss + 2 * ss, (y + ht) * ss + 3 * ss],
                         radius=radius, fill=(0, 0, 0, 115))
    shadow = shadow.filter(ImageFilter.GaussianBlur(2 * ss))
    base.alpha_composite(shadow)

    # Ivory body with a soft vertical gradient, clipped to a rounded rectangle.
    pw, ph = w * ss, ht * ss
    grad_arr = np.zeros((ph, pw, 4), dtype=np.uint8)
    t = np.linspace(0.0, 1.0, ph, dtype=np.float32)[:, None, None]
    top = np.array(IVORY_TOP, dtype=np.float32)
    bot = np.array(IVORY_BOT, dtype=np.float32)
    grad_arr[..., :3] = (top * (1 - t) + bot * t).astype(np.uint8)
    grad_arr[..., 3] = 255
    patch = Image.fromarray(grad_arr, "RGBA")
    mask = Image.new("L", (pw, ph), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=radius, fill=255)
    patch.putalpha(mask)

    pd = ImageDraw.Draw(patch)
    pd.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=radius,
                         outline=TILE_BORDER + (255,), width=max(1, ss))
    pd.rounded_rectangle([ss, ss, pw - 1 - ss, ph - 1 - ss],
                         radius=max(1, radius - ss),
                         outline=(255, 255, 250, 90), width=max(1, ss // 2))
    if orient == "H":
        pd.line([(pw // 2, 2 * ss), (pw // 2, ph - 2 * ss)],
                fill=TILE_BORDER + (255,), width=max(2, ss))
        halves = [(0, va), (half * ss, vb)]
        for hx, val in halves:
            draw_pips(pd, hx, 0, half * ss, val, ss)
    else:
        pd.line([(2 * ss, ph // 2), (pw - 2 * ss, ph // 2)],
                fill=TILE_BORDER + (255,), width=max(2, ss))
        halves = [(0, va), (half * ss, vb)]
        for hy, val in halves:
            draw_pips(pd, 0, hy, half * ss, val, ss)
    base.alpha_composite(patch, (x * ss, y * ss))


def _text(dr, xy, s, size, fill, bold=True, anchor="la", shadow=True):
    f = _font(size, bold)
    if shadow:
        dr.text((xy[0] + max(1, size // 12), xy[1] + max(1, size // 12)), s,
                font=f, fill=(0, 0, 0, 160), anchor=anchor)
    dr.text(xy, s, font=f, fill=fill, anchor=anchor)


def render_board(state, out_path, np_rng, ss=2):
    """Render one board to a PNG (final size 640 px wide, supersampled)."""
    chain, hand = state["chain"], state["hand"]
    width = 640
    margin = 18
    gap = 5
    avail = width - 2 * margin

    n = len(chain)
    n_dbl = sum(1 for t in chain if t[0] == t[1])
    half = min(56, (avail - (n - 1) * gap) // (2 * (n - n_dbl) + n_dbl))

    hn = len(hand)
    hgap = 22
    hhalf = min(50, (avail - (hn - 1) * hgap) // hn)

    chain_top = 62
    chain_band_h = 2 * half
    rack_top = chain_top + chain_band_h + 34
    label_h = 28
    rack_h = 12 + label_h + 2 * hhalf + 14
    height = rack_top + rack_h + 34

    img = make_felt(width, height, np_rng, ss)
    dr = ImageDraw.Draw(img, "RGBA")

    # Rack band behind the hand tiles.
    dr.rounded_rectangle([margin * ss, rack_top * ss,
                          (width - margin) * ss, (rack_top + rack_h) * ss],
                         radius=16 * ss, fill=(11, 52, 33, 255),
                         outline=(172, 144, 82, 255), width=max(1, ss))
    dr.line([((margin + 10) * ss, (rack_top + 2) * ss),
             ((width - margin - 10) * ss, (rack_top + 2) * ss)],
            fill=(220, 190, 120, 110), width=max(1, ss))

    # Chain tiles, centered as a group and vertically centered in the band.
    chain_w = sum(half if t[0] == t[1] else 2 * half for t in chain) + (n - 1) * gap
    x = (width - chain_w) // 2
    for t in chain:
        if t[0] == t[1]:
            draw_tile(img, x, chain_top, half, t[0], t[1], "V", ss)
            x += half + gap
        else:
            draw_tile(img, x, chain_top + half // 2, half, t[0], t[1], "H", ss)
            x += 2 * half + gap

    # Hand tiles on the rack, gold letter labels above them.
    hand_w = hn * hhalf + (hn - 1) * hgap
    x = (width - hand_w) // 2
    tile_y = rack_top + 12 + label_h
    label_y = rack_top + 12 + label_h // 2
    for h in hand:
        cx = (x + hhalf // 2) * ss
        _text(dr, (cx, label_y * ss), h["label"], 20 * ss, GOLD, anchor="mm")
        draw_tile(img, x, tile_y, hhalf, h["tile"][0], h["tile"][1], "V", ss)
        x += hhalf + hgap

    # Title and legend.
    _text(dr, ((margin + 2) * ss, 14 * ss), "Domino Chain", 24 * ss, TITLE_COLOR)
    _text(dr, ((width - margin - 2) * ss, (height - 7) * ss),
          "match open ends to play; doubles are vertical", 13 * ss,
          LEGEND_COLOR, bold=False, anchor="rd", shadow=False)

    img = img.convert("RGB").resize((width, height), Image.LANCZOS)
    img.save(out_path)
    return width, height


# --------------------------------------------------------------------------- #
# QA builders
# --------------------------------------------------------------------------- #

def _assemble(body, correct, distractors, analysis_body, rng):
    """Shuffle options, compute the answer index and finish the analysis."""
    assert len(distractors) == len(set(distractors)), "distractors not unique"
    assert correct not in distractors, "correct answer among distractors"
    options = list(distractors) + [correct]
    rng.shuffle(options)
    answer = options.index(correct) + 1
    question = (GAME_RULES + body + "\n\nOptions:\n"
                + "\n".join(f"[{i + 1}] {o}" for i, o in enumerate(options)))
    analysis = (analysis_body
                + f"\n\nSo the answer is {correct}. The option number is {answer}.")
    return {"question": question, "answer": answer,
            "analysis": analysis, "options": options}


def _pips_word(v):
    return f"{v} pip" + ("" if v == 1 else "s")


# --- Task 1: Target Perception / Easy -------------------------------------- #

def _q1a(state, rng):
    chain = state["chain"]
    cands = []
    if chain[0][0] != chain[0][1]:
        cands += [("LEFT", "left", chain[0][0]), ("LEFT", "right", chain[0][1])]
    if chain[-1][0] != chain[-1][1]:
        cands += [("RIGHT", "left", chain[-1][0]), ("RIGHT", "right", chain[-1][1])]
    if not cands:
        return None
    end, half_side, val = rng.choice(cands)
    body = (f"Look at the tile at the {end} end of the chain. "
            f"How many pips are on its {half_side} half?")
    which = "leftmost" if end == "LEFT" else "rightmost"
    blank = " (it is blank)" if val == 0 else ""
    analysis = (f"The tile at the {end} end of the chain is the {which} tile in the row. "
                f"It is drawn horizontally, and its {half_side} half shows "
                f"{_pips_word(val)}{blank}.")
    correct = str(val)
    distractors = [str(v) for v in range(7) if v != val]
    rng.shuffle(distractors)
    return ("Count the pips on one half of a tile at an end of the chain",
            body, correct, distractors, analysis)


def _q1b(state, rng):
    pick = rng.choice(state["hand"])
    a, b = pick["tile"]
    body = (f"What are the two values of hand tile {pick['label']}? "
            f"Give the value of the upper half first and the value of the lower half second.")
    analysis = (f"Hand tile {pick['label']} is the vertical tile under the gold letter "
                f"{pick['label']}. Its upper half shows {_pips_word(a)} and its lower "
                f"half shows {_pips_word(b)}, so its value is ({a}|{b}).")
    correct = f"({a}|{b})"
    cands = []
    if a != b:
        cands.append((b, a))
    for da, db in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1),
                   (2, 0), (0, 2), (-2, 0), (0, -2), (1, -1), (-1, 1)]:
        cands.append((a + da, b + db))
    seen, distractors = set(), []
    for p in cands:
        s = f"({p[0]}|{p[1]})"
        if 0 <= p[0] <= 6 and 0 <= p[1] <= 6 and p != (a, b) and s not in seen:
            seen.add(s)
            distractors.append(s)
    rng.shuffle(distractors)
    while len(distractors) < 7:  # extremely defensive; the pool above is enough
        p = (rng.randint(0, 6), rng.randint(0, 6))
        s = f"({p[0]}|{p[1]})"
        if p != (a, b) and s not in seen:
            seen.add(s)
            distractors.append(s)
    return ("Identify the two values of a labeled hand tile",
            body, correct, distractors[:7], analysis)


def _q1c(state, rng):
    chain = state["chain"]
    cnt = sum(1 for t in chain if t[0] == t[1])
    body = ("How many doubles (tiles whose two halves show the same number of pips) "
            "are there in the chain?")
    chain_str = ", ".join(f"{t[0]}-{t[1]}" for t in chain)
    dbl_str = ", ".join(f"{t[0]}-{t[1]}" for t in chain if t[0] == t[1]) or "none"
    analysis = (f"Reading the chain from left to right: {chain_str}. "
                f"The tiles with two equal halves are: {dbl_str}. "
                f"That is {cnt} double" + ("" if cnt == 1 else "s") + " in total.")
    correct = str(cnt)
    pool = [v for v in range(0, len(chain) + 3) if v != cnt]
    rng.shuffle(pool)
    distractors = [str(v) for v in pool[:7]]
    return ("Count the doubles in the chain", body, correct, distractors, analysis)


def _q1d(state, rng):
    hand = state["hand"]
    dbl = [h for h in hand if h["tile"][0] == h["tile"][1]]
    if len(dbl) != 1:
        return None
    correct = dbl[0]["label"]
    body = ("Which hand tile is a double (a tile whose two halves show the same "
            "number of pips)?")
    parts = []
    for h in hand:
        a, b = h["tile"]
        note = "equal halves -> double" if a == b else "halves differ"
        parts.append(f"{h['label']} ({a}|{b}): {note}")
    analysis = ("Checking each hand tile: " + "; ".join(parts)
                + f". Only tile {correct} has two equal halves.")
    distractors = [h["label"] for h in hand if h["label"] != correct] + ["None of them"]
    rng.shuffle(distractors)
    return ("Identify which hand tile is a double", body, correct, distractors, analysis)


_Q1_BUILDERS = {"a": _q1a, "b": _q1b, "c": _q1c, "d": _q1d}


def build_task1(state, rng, subtype_order):
    """Try the preferred perception sub-type first, then fall back in order."""
    for st in subtype_order:
        res = _Q1_BUILDERS[st](state, rng)
        if res is not None:
            desc, body, correct, distractors, analysis = res
            qa = _assemble(body, correct, distractors, analysis, rng)
            qa.update({"question_id": 1, "question_description": desc,
                       "qa_type": "Target Perception", "qa_level": "Easy"})
            return qa
    raise RuntimeError("no valid task-1 subtype for this board")


# --- Task 2: State Prediction / Medium — playable set ---------------------- #

def _match_reason(a, b, left, right):
    m_left = a == left or b == left
    m_right = a == right or b == right
    if not (m_left or m_right):
        if a == b:
            if left == right:
                return (f"both its halves are {a} and {a} does not match the open "
                        f"end value {left} -> not playable")
            return (f"both its halves are {a} and {a} matches neither {left} "
                    f"nor {right} -> not playable")
        if left == right:
            return f"neither {a} nor {b} matches the open end value {left} -> not playable"
        return f"neither {a} nor {b} matches {left} or {right} -> not playable"
    if left == right:
        m = a if a == left else b
        return (f"its {m}-half matches the open end value {left} "
                f"(both open ends are {left}) -> playable")
    if m_left and m_right:
        lm = a if a == left else b
        rm = a if a == right else b
        return (f"its {lm}-half matches the left open end {left} and its {rm}-half "
                f"matches the right open end {right} -> playable on either end")
    if m_left:
        lm = a if a == left else b
        return f"its {lm}-half matches the left open end {left} -> playable"
    rm = a if a == right else b
    return f"its {rm}-half matches the right open end {right} -> playable"


def build_task2(state, rng):
    left, right = state["open_left"], state["open_right"]
    hand = state["hand"]
    labels = [h["label"] for h in hand]
    playable = playable_labels(state)
    correct = format_set(playable)
    body = ("Which of the hand tiles can be legally played on EITHER open end of the "
            "chain right now? A tile counts as playable if it can be played on the left "
            "open end, on the right open end, or on both.")

    lines = [f"The left open end of the chain is {left} and the right open end is {right}.",
             "Checking every hand tile against these two values:"]
    for h in hand:
        a, b = h["tile"]
        lines.append(f"- {h['label']} ({a}|{b}): {_match_reason(a, b, left, right)}")
    lines.append(f"So the playable hand tiles are: {correct}.")
    analysis = "\n".join(lines)

    # Distractors: subsets differing from the correct set (plus None / all).
    cand = set()
    pset = frozenset(playable)
    for t in labels:
        cand.add(tuple(sorted(pset - {t})))
        cand.add(tuple(sorted(pset | {t})))
    cand.add(())
    cand.add(tuple(labels))
    all_subs = [c for r in range(len(labels) + 1)
                for c in itertools.combinations(labels, r)]
    rng.shuffle(all_subs)
    cand.update(all_subs)
    cand.discard(tuple(sorted(pset)))
    strs = []
    for c in sorted(cand):  # sorted: set iteration order must not leak into the RNG stream
        s = format_set(list(c))
        if s not in strs:
            strs.append(s)
    rng.shuffle(strs)
    distractors = strs[:7]
    assert len(distractors) == 7, "not enough unique subset distractors"

    qa = _assemble(body, correct, distractors, analysis, rng)
    qa.update({"question_id": 2,
               "question_description": "Determine which hand tiles can be legally "
                                       "played on either open end of the chain",
               "qa_type": "State Prediction", "qa_level": "Medium"})
    return qa


# --- Task 3: State Prediction / Medium — new open ends --------------------- #

def build_task3(state, rng):
    left, right = state["open_left"], state["open_right"]
    cands = []
    for h in state["hand"]:
        a, b = h["tile"]
        if a == left or b == left:
            cands.append((h, "LEFT"))
        if a == right or b == right:
            cands.append((h, "RIGHT"))
    h, end = rng.choice(cands)
    a, b = h["tile"]
    if end == "LEFT":
        m = left
        other = b if a == left else a
        new_left, new_right = other, right
    else:
        m = right
        other = b if a == right else a
        new_left, new_right = left, other

    body = (f"Hand tile {h['label']} ({a}|{b}) is played on the {end} end of the chain "
            f"(it is rotated as needed so that one of its halves matches the "
            f"{end.lower()} open end). After this move, what are the values of the two "
            f"open ends of the chain? Give the left open end first and the right open "
            f"end second.")
    keep = right if end == "LEFT" else left
    keep_name = "right" if end == "LEFT" else "left"
    analysis = (f"The current open ends are left = {left} and right = {right}. Hand tile "
                f"{h['label']} ({a}|{b}) is played on the {end} end. Its half with "
                f"{_pips_word(m)} matches the {end.lower()} open end {m}, so the tile is "
                f"rotated to touch the chain with that half, and its other half ({other}) "
                f"becomes the new {end.lower()} open end. The {keep_name} open end does "
                f"not change and stays {keep}. The new open ends are "
                f"({new_left}, {new_right}).")
    correct = f"({new_left}, {new_right})"

    pool = [(left, right), (right, left), (other, other), (m, other), (other, m),
            (a, b), (b, a), (new_left, new_left), (new_right, new_right)]
    seen, distractors = set(), []
    for p in pool:
        s = f"({p[0]}, {p[1]})"
        if p != (new_left, new_right) and s not in seen:
            seen.add(s)
            distractors.append(s)
    rng.shuffle(distractors)
    while len(distractors) < 7:
        p = (rng.randint(0, 6), rng.randint(0, 6))
        s = f"({p[0]}, {p[1]})"
        if p != (new_left, new_right) and s not in seen:
            seen.add(s)
            distractors.append(s)

    qa = _assemble(body, correct, distractors[:7], analysis, rng)
    qa.update({"question_id": 3,
               "question_description": "Predict the two open ends after a given hand "
                                       "tile is played on one end of the chain",
               "qa_type": "State Prediction", "qa_level": "Medium"})
    return qa


# --- Task 4: Strategy Optimization / Hard — maximum extension -------------- #

def build_task4(state, rng):
    left, right = state["open_left"], state["open_right"]
    best, moves = max_extend(state)
    assert best >= 1, "hand guarantees at least one playable tile"
    body = ("What is the maximum number of hand tiles that can be played onto the "
            "chain, in some order? Each hand tile can be used at most once, and every "
            "tile played must match one of the two open ends at the moment it is "
            "played. The open ends change as tiles are added.")

    lines = [f"The chain starts with open ends left = {left} and right = {right}.",
             f"One sequence that achieves the maximum ({best} tile"
             + ("" if best == 1 else "s") + "):"]
    cur_l, cur_r = left, right
    for i, mv in enumerate(moves, 1):
        a, b = mv["tile"]
        m = cur_l if mv["end"] == "LEFT" else cur_r
        cur_l, cur_r = mv["new_left"], mv["new_right"]
        lines.append(f"{i}. Play {mv['label']} ({a}|{b}) on the {mv['end']} end: its "
                     f"{m}-half matches the {mv['end'].lower()} open end {m}, so that "
                     f"end becomes {cur_l if mv['end'] == 'LEFT' else cur_r}. "
                     f"Open ends are now ({cur_l}, {cur_r}).")
    used = {mv["label"] for mv in moves}
    remaining = [h for h in state["hand"] if h["label"] not in used]
    ends_str = (f"the open end value {cur_l}" if cur_l == cur_r
                else f"{cur_l} or {cur_r}")
    if remaining:
        if len(remaining) == 1:
            h = remaining[0]
            a, b = h["tile"]
            no_match = (f"its value {a} does not match {ends_str}" if a == b
                        else f"neither {a} nor {b} matches {ends_str}")
            lines.append(f"The only unused hand tile is {h['label']} ({a}|{b}): "
                         f"{no_match}, so no further tile can be played.")
        else:
            tile_strs = [f"{h['label']} ({h['tile'][0]}|{h['tile'][1]})"
                         for h in remaining]
            rem_str = ", ".join(tile_strs[:-1]) + f" and {tile_strs[-1]}"
            lines.append(f"The unused hand tiles are {rem_str}: none of their "
                         f"halves matches {ends_str}, so no further tile can be played.")
    else:
        lines.append("All hand tiles have been used, so no further tile can be played.")
    lines.append(f"Hence the maximum number of hand tiles that can be played is {best}.")
    analysis = "\n".join(lines)

    correct = str(best)
    pool = []
    for d in (-1, 1, -2, 2, -3, 3):
        v = best + d
        if v >= 0 and v not in pool:
            pool.append(v)
    v = 0
    while len(pool) < 7:
        if v != best and v not in pool:
            pool.append(v)
        v += 1
    distractors = [str(x) for x in pool[:7]]

    qa = _assemble(body, correct, distractors, analysis, rng)
    qa.update({"question_id": 4,
               "question_description": "Find the maximum number of hand tiles that "
                                       "can be played onto the chain in some order",
               "qa_type": "Strategy Optimization", "qa_level": "Hard"})
    return qa
