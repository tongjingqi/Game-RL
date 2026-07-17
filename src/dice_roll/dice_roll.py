"""Dice Roll puzzle: game logic, PIL rendering, and QA builders.

A standard six-sided die sits on a grid board with rock obstacles and a
golden star (goal) cell. The die can be rolled North/South/East/West; each
roll tips it onto the adjacent cell and changes its orientation. It is a
standard die: opposite faces sum to 7 (1-6, 2-5, 3-4).

Coordinates are (row, column), 0-based; row numbers are printed on the left
of the board, column numbers on top.
"""

import math
import random
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_CONDENSED = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"

DIRECTIONS = {
    "North": (-1, 0),
    "South": (1, 0),
    "East": (0, 1),
    "West": (0, -1),
}

CANONICAL_ORIENTATION = {
    "top": 1, "bottom": 6, "north": 2, "south": 5, "east": 3, "west": 4,
}

GAME_RULES = (
    "Dice Roll puzzle. A standard six-sided die sits on a grid board shown "
    "from above. Row numbers (0-based, increasing downward) are printed on "
    "the left of the board and column numbers (0-based, increasing "
    "rightward) on top; positions are written as (row, column). Gray-brown "
    "rocks are blocked cells that the die cannot enter. The golden star "
    "marks the goal cell. The die is drawn in isometric style so three of "
    "its faces are visible: the TOP face, the FRONT-LEFT face (the face "
    "pointing South, toward larger row numbers) and the FRONT-RIGHT face "
    "(the face pointing East, toward larger column numbers). It is a "
    "standard die: opposite faces always sum to 7 (1 opposite 6, 2 opposite "
    "5, 3 opposite 4), so the three hidden faces are fully determined by "
    "the three visible ones. The die can be rolled North (up, toward "
    "smaller row numbers), South (down), East (right) or West (left): it "
    "tips onto the adjacent cell and its orientation changes accordingly "
    "(the face opposite to the rolling direction comes to the top). If the "
    "target cell is blocked by a rock or lies outside the board, the die "
    "does not move and its orientation stays unchanged. "
)

TASK_DESCRIPTIONS = {
    1: "Identify a visible face value, the total visible pip count, or a piece position on the board",
    2: "Predict the die's orientation or final cell after a given sequence of rolls",
    3: "Find the roll sequence that produces a given final cell and orientation",
    4: "Compute the minimum number of rolls to reach the star (possibly with a required top face)",
}

TASK_TYPES = {
    1: ("Target Perception", "Easy"),
    2: ("State Prediction", "Medium"),
    3: ("State Prediction", "Hard"),
    4: ("Strategy Optimization", "Hard"),
}

# ---------------------------------------------------------------------------
# Core dice mechanics
# ---------------------------------------------------------------------------

def roll_orientation(ori, direction):
    """Return the new orientation after rolling the die one cell in `direction`."""
    o = dict(ori)
    if direction == "East":
        o["top"], o["bottom"] = ori["west"], ori["east"]
        o["east"], o["west"] = ori["top"], ori["bottom"]
    elif direction == "West":
        o["top"], o["bottom"] = ori["east"], ori["west"]
        o["west"], o["east"] = ori["top"], ori["bottom"]
    elif direction == "North":
        o["top"], o["bottom"] = ori["south"], ori["north"]
        o["north"], o["south"] = ori["top"], ori["bottom"]
    elif direction == "South":
        o["top"], o["bottom"] = ori["north"], ori["south"]
        o["south"], o["north"] = ori["top"], ori["bottom"]
    else:
        raise ValueError(f"unknown direction {direction!r}")
    return o


def random_orientation(rng):
    """Random valid die orientation: 1-3 random rolls from the canonical one."""
    ori = dict(CANONICAL_ORIENTATION)
    for _ in range(rng.randint(1, 3)):
        ori = roll_orientation(ori, rng.choice(list(DIRECTIONS)))
    return ori


def simulate(rows, cols, blocked, start, orientation, sequence):
    """Simulate a roll sequence.

    Returns (final_pos, final_orientation, trace) where trace is a list of
    (direction, pos_after, orientation_after, moved) tuples. A roll onto a
    blocked or off-board cell leaves position and orientation unchanged.
    """
    blocked = set(map(tuple, blocked))
    pos = tuple(start)
    ori = dict(orientation)
    trace = []
    for d in sequence:
        dr, dc = DIRECTIONS[d]
        nr, nc = pos[0] + dr, pos[1] + dc
        if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in blocked:
            pos = (nr, nc)
            ori = roll_orientation(ori, d)
            moved = True
        else:
            moved = False
        trace.append((d, pos, dict(ori), moved))
    return pos, ori, trace


def bfs_min_rolls(rows, cols, blocked, start, orientation, goal, target_top=None):
    """Minimum rolls from (start, orientation) to the goal cell.

    If target_top is given, the die must additionally arrive with that value
    on its top face. Returns (distance, path) or (None, None).
    """
    blocked = set(map(tuple, blocked))
    goal = tuple(goal)

    def okey(o):
        return (o["top"], o["north"], o["east"])  # determines all six faces

    if tuple(start) == goal and (target_top is None or orientation["top"] == target_top):
        return 0, []
    dq = deque([(tuple(start), dict(orientation), [])])
    seen = {(tuple(start), okey(orientation))}
    while dq:
        pos, ori, path = dq.popleft()
        for d, (dr, dc) in DIRECTIONS.items():
            nr, nc = pos[0] + dr, pos[1] + dc
            if not (0 <= nr < rows and 0 <= nc < cols) or (nr, nc) in blocked:
                continue
            nori = roll_orientation(ori, d)
            k = ((nr, nc), okey(nori))
            if k in seen:
                continue
            seen.add(k)
            npath = path + [d]
            if (nr, nc) == goal and (target_top is None or nori["top"] == target_top):
                return len(npath), npath
            dq.append(((nr, nc), nori, npath))
    return None, None


# ---------------------------------------------------------------------------
# Board generation
# ---------------------------------------------------------------------------

PLOT_LEVEL_SIZES = {"Easy": (5, 2, 3), "Medium": (6, 3, 5), "Hard": (7, 5, 8)}


def _reachable(n, blocked, start, goal):
    """Flood fill: is goal reachable from start avoiding blocked cells?"""
    seen = {tuple(start)}
    dq = deque([tuple(start)])
    while dq:
        r, c = dq.popleft()
        if (r, c) == tuple(goal):
            return True
        for dr, dc in DIRECTIONS.values():
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in blocked and (nr, nc) not in seen:
                seen.add((nr, nc))
                dq.append((nr, nc))
    return False


def generate_board(rng, plot_level):
    """Generate a random board dict for the given plot level."""
    n, lo, hi = PLOT_LEVEL_SIZES[plot_level]
    cells = [(r, c) for r in range(n) for c in range(n)]
    while True:
        die = rng.choice(cells)
        star = rng.choice([c for c in cells if c != die])
        n_block = rng.randint(lo, hi)
        blocked = set(rng.sample([c for c in cells if c != die and c != star], n_block))
        if _reachable(n, blocked, die, star):
            return {
                "rows": n,
                "cols": n,
                "blocked": sorted([list(c) for c in blocked]),
                "star": list(star),
                "die": list(die),
                "orientation": random_orientation(rng),
            }


def free_cells(state):
    blocked = set(map(tuple, state["blocked"]))
    return [(r, c) for r in range(state["rows"]) for c in range(state["cols"])
            if (r, c) not in blocked]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

CELL_SIZES = {5: 86, 6: 74, 7: 64}

PIP_LAYOUTS = {
    1: [(1, 1)],
    2: [(0, 0), (2, 2)],
    3: [(0, 0), (1, 1), (2, 2)],
    4: [(0, 0), (2, 0), (0, 2), (2, 2)],
    5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)],
    6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)],
}


def _font(path, size):
    return ImageFont.truetype(path, size)


def _star_points(cx, cy, r_out, r_in, n=5):
    pts = []
    for i in range(2 * n):
        ang = math.radians(-90 + i * 180 / n)
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def _bilinear(A, B, C, D, u, v):
    """Bilinear interpolation in quad A,B,C,D (clockwise)."""
    x = (1 - u) * (1 - v) * A[0] + u * (1 - v) * B[0] + u * v * C[0] + (1 - u) * v * D[0]
    y = (1 - u) * (1 - v) * A[1] + u * (1 - v) * B[1] + u * v * C[1] + (1 - u) * v * D[1]
    return (x, y)


def _draw_face_pips(draw, quad, value, pip_r):
    A, B, C, D = quad
    for gx, gy in PIP_LAYOUTS[value]:
        u = 0.30 + 0.20 * gx
        v = 0.30 + 0.20 * gy
        px, py = _bilinear(A, B, C, D, u, v)
        draw.ellipse([px - pip_r, py - pip_r, px + pip_r, py + pip_r], fill=(28, 26, 24))


def _draw_rock(base, draw, x0, y0, cell, rng):
    cx, cy = x0 + cell / 2, y0 + cell / 2
    R = cell * 0.32
    # soft shadow
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([cx - R * 1.0, cy + R * 0.30, cx + R * 1.0, cy + R * 0.85], fill=(0, 0, 0, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))
    base.alpha_composite(shadow)
    # irregular blob
    pts = []
    for i in range(9):
        ang = 2 * math.pi * i / 9
        rr = R * rng.uniform(0.80, 1.06)
        pts.append((cx + rr * math.cos(ang), cy + 0.84 * rr * math.sin(ang)))
    draw.polygon(pts, fill=(117, 105, 91), outline=(66, 57, 48), width=2)
    # highlight blob (upper-left)
    hl = []
    for i in range(9):
        ang = 2 * math.pi * i / 9
        rr = R * 0.52 * rng.uniform(0.80, 1.05)
        hl.append((cx - R * 0.22 + rr * math.cos(ang), cy - R * 0.24 + 0.80 * rr * math.sin(ang)))
    draw.polygon(hl, fill=(152, 140, 124))
    # a couple of speckles
    for _ in range(4):
        sx = cx + rng.uniform(-R * 0.5, R * 0.5)
        sy = cy + rng.uniform(-R * 0.1, R * 0.5)
        r = cell * 0.02
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(88, 78, 66))


def _draw_star(base, draw, x0, y0, cell):
    cx, cy = x0 + cell / 2, y0 + cell / 2
    r_out, r_in = cell * 0.34, cell * 0.145
    # glow
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.polygon(_star_points(cx, cy, r_out * 1.35, r_in * 1.35), fill=(255, 214, 90, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(cell * 0.06))
    base.alpha_composite(glow)
    # main star
    draw.polygon(_star_points(cx, cy, r_out, r_in), fill=(255, 198, 41), outline=(178, 122, 18), width=2)
    # bright core highlight
    draw.polygon(_star_points(cx, cy - r_out * 0.08, r_out * 0.42, r_in * 0.42),
                 fill=(255, 228, 130))


def _draw_die(base, draw, x0, y0, cell, orientation):
    cx = x0 + cell / 2
    w = cell * 0.33
    hh = w * 0.62
    v = cell * 0.33
    total_h = 2 * hh + v
    cy_top = y0 + (cell - total_h) / 2
    T = (cx, cy_top)
    R = (cx + w, cy_top + hh)
    B = (cx, cy_top + 2 * hh)
    L = (cx - w, cy_top + hh)
    Bd = (B[0], B[1] + v)
    Rd = (R[0], R[1] + v)
    Ld = (L[0], L[1] + v)
    # soft shadow under the die
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([cx - w * 1.15, Bd[1] - cell * 0.10, cx + w * 1.15, Bd[1] + cell * 0.06],
               fill=(0, 0, 0, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(4))
    base.alpha_composite(shadow)
    # three visible faces (top lightest, front-left mid, front-right darkest)
    ew = max(2, cell // 30)
    draw.polygon([T, R, B, L], fill=(252, 250, 244), outline=(30, 28, 26), width=ew)
    draw.polygon([L, B, Bd, Ld], fill=(226, 219, 204), outline=(30, 28, 26), width=ew)
    draw.polygon([B, R, Rd, Bd], fill=(198, 190, 173), outline=(30, 28, 26), width=ew)
    # pips
    pip_r = max(2.0, cell * 0.030)
    _draw_face_pips(draw, (T, R, B, L), orientation["top"], pip_r)
    _draw_face_pips(draw, (L, B, Bd, Ld), orientation["south"], pip_r)
    _draw_face_pips(draw, (B, R, Rd, Bd), orientation["east"], pip_r)


def render_board(state, out_path, rng):
    """Render the board to a PNG file (isometric die, textured board)."""
    rows, cols = state["rows"], state["cols"]
    cell = CELL_SIZES[rows]
    left, top_m, right = 46, 46, 18
    legend_h = 78
    gw, gh = cols * cell, rows * cell
    W = left + gw + right
    H = top_m + gh + 10 + legend_h + 10

    np_rng = np.random.RandomState(rng.getrandbits(32))
    # parchment background with subtle noise
    base_arr = np.zeros((H, W, 3), dtype=np.float64)
    base_arr[:, :] = (233, 224, 201)
    base_arr += np_rng.normal(0, 4.0, (H, W, 1))
    img = Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    draw = ImageDraw.Draw(img)

    # wooden frame around the board
    draw.rounded_rectangle([left - 7, top_m - 7, left + gw + 7, top_m + gh + 7],
                           radius=8, fill=(104, 76, 48), outline=(70, 50, 30), width=2)

    # two-tone felt cells with speckle texture
    felt_a = np.array((94, 148, 96), dtype=np.float64)
    felt_b = np.array((80, 132, 84), dtype=np.float64)
    for r in range(rows):
        for c in range(cols):
            x0, y0 = left + c * cell, top_m + r * cell
            cell_arr = np.zeros((cell, cell, 3), dtype=np.float64)
            cell_arr[:, :] = felt_a if (r + c) % 2 == 0 else felt_b
            cell_arr += np_rng.normal(0, 3.0, (cell, cell, 1))
            tile = Image.fromarray(np.clip(cell_arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
            img.alpha_composite(tile, (x0, y0))
            # subtle inner highlight for a tiled look
            draw.rectangle([x0 + 1, y0 + 1, x0 + cell - 2, y0 + cell - 2],
                           outline=(255, 255, 255, 28), width=1)
    # grid lines
    for r in range(rows + 1):
        y = top_m + r * cell
        draw.line([left, y, left + gw, y], fill=(52, 92, 56, 255), width=1)
    for c in range(cols + 1):
        x = left + c * cell
        draw.line([x, top_m, x, top_m + gh], fill=(52, 92, 56, 255), width=1)

    blocked = set(map(tuple, state["blocked"]))
    star = tuple(state["star"])
    die = tuple(state["die"])

    # star cell tint
    sx0, sy0 = left + star[1] * cell, top_m + star[0] * cell
    tint = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(tint).rectangle([sx0 + 1, sy0 + 1, sx0 + cell - 2, sy0 + cell - 2],
                                   fill=(255, 235, 150, 46))
    img.alpha_composite(tint)

    for r in range(rows):
        for c in range(cols):
            x0, y0 = left + c * cell, top_m + r * cell
            if (r, c) in blocked:
                rock_rng = random.Random(9000 + r * 131 + c * 17 + rows)
                _draw_rock(img, draw, x0, y0, cell, rock_rng)
            if (r, c) == star:
                _draw_star(img, draw, x0, y0, cell)
            if (r, c) == die:
                _draw_die(img, draw, x0, y0, cell, state["orientation"])

    # vignette
    yy, xx = np.mgrid[0:H, 0:W]
    dist = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
    factor = 1.0 - 0.16 * np.clip(dist - 0.45, 0, None)
    arr = np.asarray(img.convert("RGB")).astype(np.float64) * factor[:, :, None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img)

    # coordinate labels (0-based): rows left, columns top
    coord_font = _font(FONT_BOLD, max(15, int(cell * 0.26)))
    coord_color = (58, 50, 40)
    for c in range(cols):
        draw.text((left + c * cell + cell / 2, top_m - 16), str(c),
                  font=coord_font, fill=coord_color, anchor="mm")
    for r in range(rows):
        draw.text((left - 17, top_m + r * cell + cell / 2), str(r),
                  font=coord_font, fill=coord_color, anchor="mm")

    # legend strip
    ly0 = top_m + gh + 10
    draw.rounded_rectangle([left - 7, ly0, left + gw + 7, ly0 + legend_h], radius=8,
                           fill=(56, 46, 36), outline=(38, 30, 22), width=2)
    leg_font = _font(FONT_CONDENSED, max(14, int(cell * 0.185)))
    leg_font_b = _font(FONT_BOLD, max(14, int(cell * 0.185)))
    draw.text((left + 6, ly0 + 12), "Die visible faces:", font=leg_font_b, fill=(255, 230, 170))
    draw.text((left + 6, ly0 + 34), "TOP / FRONT-LEFT (south) / FRONT-RIGHT (east)",
              font=leg_font, fill=(235, 228, 214))
    draw.text((left + 6, ly0 + 56),
              "Opposite faces sum to 7.  Star = goal,  rock = blocked.",
              font=leg_font, fill=(235, 228, 214))

    img.save(out_path)
    return W, H


# ---------------------------------------------------------------------------
# QA builders
# ---------------------------------------------------------------------------

def _fmt_cell(c):
    return f"({c[0]}, {c[1]})"


def _finalize(body, options, correct_str, analysis_core, rng):
    """Shuffle options, compute the answer index, close the analysis."""
    opts = list(options)
    rng.shuffle(opts)
    answer = opts.index(correct_str) + 1
    question = (GAME_RULES + body + "\n\nOptions:\n" +
                "\n".join(f"[{i + 1}] {o}" for i, o in enumerate(opts)))
    analysis = (analysis_core +
                f"\n\nSo the answer is {correct_str}. The option number is {answer}.")
    return {"question": question, "answer": answer, "analysis": analysis, "options": opts}


def _face_name(variant):
    return {"top": "TOP", "front_left": "FRONT-LEFT", "front_right": "FRONT-RIGHT"}[variant]


def _face_key(variant):
    return {"top": "top", "front_left": "south", "front_right": "east"}[variant]


def build_task1(rng, state, variant):
    """Target Perception: face value / pip count / positions."""
    ori = state["orientation"]
    die, star = tuple(state["die"]), tuple(state["star"])
    if variant in ("top", "front_left", "front_right"):
        value = ori[_face_key(variant)]
        body = f"What number is on the {_face_name(variant)} face of the die?"
        correct = str(value)
        options = [str(i) for i in range(1, 7)] + ["7", "8"]
        analysis_core = (
            f"Looking at the isometric die in the image, the {_face_name(variant)} face "
            f"shows {value} pip(s)."
        )
    elif variant == "pip_total":
        total = ori["top"] + ori["south"] + ori["east"]
        body = "How many pips are visible on the die in total (sum of the three visible faces)?"
        correct = str(total)
        pool = [i for i in range(4, 18) if i != total]
        options = [correct] + [str(i) for i in rng.sample(pool, 7)]
        analysis_core = (
            f"The TOP face shows {ori['top']} pip(s), the FRONT-LEFT face shows "
            f"{ori['south']} pip(s) and the FRONT-RIGHT face shows {ori['east']} pip(s).\n"
            f"Total visible pips: {ori['top']} + {ori['south']} + {ori['east']} = {total}."
        )
    else:  # die_cell / star_cell
        target = die if variant == "die_cell" else star
        name = "die" if variant == "die_cell" else "star (goal)"
        body = f"Which cell (row, column) is the {name} on?"
        correct = _fmt_cell(target)
        pool = [c for c in free_cells(state) if c != target]
        options = [correct] + [_fmt_cell(c) for c in rng.sample(pool, 7)]
        which = ("The isometric die sits in the row labeled "
                 f"{target[0]} on the left and the column labeled {target[1]} on top."
                 if variant == "die_cell" else
                 "The golden star is drawn in the row labeled "
                 f"{target[0]} on the left and the column labeled {target[1]} on top.")
        analysis_core = f"{which}\nSo the {name} is on cell {_fmt_cell(target)}."
    qa = _finalize(body, options, correct, analysis_core, rng)
    qa["question_id"] = 1
    return qa


def _random_sequence(rng, state, length, allow_one_blocked):
    """Random roll sequence; at most one blocked/off-board move if allowed."""
    blocked = set(map(tuple, state["blocked"]))
    pos = tuple(state["die"])
    seq = []
    used_blocked = 0
    while len(seq) < length:
        d = rng.choice(list(DIRECTIONS))
        dr, dc = DIRECTIONS[d]
        nr, nc = pos[0] + dr, pos[1] + dc
        ok = 0 <= nr < state["rows"] and 0 <= nc < state["cols"] and (nr, nc) not in blocked
        if ok:
            pos = (nr, nc)
            seq.append(d)
        elif allow_one_blocked and used_blocked < 1:
            used_blocked += 1
            seq.append(d)
        # otherwise resample
    return seq


def _trace_text(state, sequence):
    """Step-by-step orientation trace used by tasks 2 and 3."""
    _, _, trace = simulate(state["rows"], state["cols"], state["blocked"],
                           state["die"], state["orientation"], sequence)
    pos = tuple(state["die"])
    lines = []
    for i, (d, p, o, moved) in enumerate(trace, 1):
        if moved:
            lines.append(
                f"Roll {i} - {d}: the die moves from {_fmt_cell(pos)} to {_fmt_cell(p)}. "
                f"Visible faces become top={o['top']}, front-left={o['south']}, "
                f"front-right={o['east']}.")
            pos = p
        else:
            lines.append(
                f"Roll {i} - {d}: blocked (rock or board edge) - the die stays at "
                f"{_fmt_cell(pos)} and its orientation is unchanged "
                f"(top={o['top']}, front-left={o['south']}, front-right={o['east']}).")
    return "\n".join(lines), trace


def build_task2(rng, state, variant):
    """State Prediction: rolls then top/front-left face or final cell."""
    ori = state["orientation"]
    length = rng.randint(3, 6)
    allow_blocked = rng.random() < 0.35
    seq = _random_sequence(rng, state, length, allow_blocked)
    pos, final_ori, trace = simulate(state["rows"], state["cols"], state["blocked"],
                                     state["die"], ori, seq)
    seq_str = ", ".join(seq)
    trace_txt, _ = _trace_text(state, seq)
    start_line = (
        f"The die starts at {_fmt_cell(state['die'])} with top={ori['top']}, "
        f"front-left={ori['south']}, front-right={ori['east']} (so bottom={ori['bottom']}, "
        f"back-right/hidden-north={ori['north']}, back-left/hidden-west={ori['west']}).\n"
        + trace_txt
    )
    if variant == "final_cell":
        body = (f"The die is rolled: {seq_str}. "
                f"Which cell (row, column) will the die be on after these rolls?")
        correct = _fmt_cell(pos)
        pool = [c for c in free_cells(state) if c != pos]
        options = [correct] + [_fmt_cell(c) for c in rng.sample(pool, 7)]
        analysis_core = start_line + f"\nAfter all rolls the die rests on cell {_fmt_cell(pos)}."
    else:
        face = _face_name(variant)
        key = _face_key(variant)
        body = (f"The die is rolled: {seq_str}. "
                f"What number will be on the {face} face of the die after these rolls?")
        correct = str(final_ori[key])
        options = [str(i) for i in range(1, 7)] + [
            "The die falls off the board", "The roll sequence cannot be performed"]
        analysis_core = (start_line +
                         f"\nAfter all rolls the {face} face shows {final_ori[key]}.")
    qa = _finalize(body, options, correct, analysis_core, rng)
    qa["question_id"] = 2
    qa["_sequence"] = seq
    return qa


def _mutate_sequence(rng, seq):
    """One random mutation of a roll sequence (result length kept in 3..5)."""
    ops = ["change", "swap"]
    if len(seq) > 3:
        ops.append("delete")
    if len(seq) < 5:
        ops.append("insert")
    op = rng.choice(ops)
    s = list(seq)
    if op == "change":
        i = rng.randrange(len(s))
        s[i] = rng.choice([d for d in DIRECTIONS if d != s[i]])
    elif op == "swap":
        i, j = rng.sample(range(len(s)), 2)
        s[i], s[j] = s[j], s[i]
    elif op == "delete":
        s.pop(rng.randrange(len(s)))
    else:  # insert
        s.insert(rng.randrange(len(s) + 1), rng.choice(list(DIRECTIONS)))
    return s


def build_task3(rng, state):
    """State Prediction (inverse): which roll sequence gives this result?"""
    seq = _random_sequence(rng, state, rng.randint(3, 5), allow_one_blocked=False)
    pos, final_ori, _ = simulate(state["rows"], state["cols"], state["blocked"],
                                 state["die"], state["orientation"], seq)
    target = (pos, final_ori["top"], final_ori["south"])

    def outcome(s):
        p, o, _ = simulate(state["rows"], state["cols"], state["blocked"],
                           state["die"], state["orientation"], s)
        return (p, o["top"], o["south"])

    distractors = []
    seen = {tuple(seq)}
    attempts = 0
    while len(distractors) < 7 and attempts < 4000:
        attempts += 1
        cand = _mutate_sequence(rng, seq)
        if tuple(cand) in seen:
            continue
        seen.add(tuple(cand))
        if outcome(cand) == target:
            continue  # would be a second correct answer
        distractors.append(cand)
    if len(distractors) < 7:
        return None

    body = (f"Starting from the position and orientation shown in the image, the die "
            f"went through a sequence of rolls. It ended at cell {_fmt_cell(pos)} with "
            f"{final_ori['top']} on the top face and {final_ori['south']} on the "
            f"front-left face. Which of the following roll sequences produces exactly "
            f"this final position and orientation?")
    correct = ", ".join(seq)
    options = [correct] + [", ".join(s) for s in distractors]

    trace_txt, _ = _trace_text(state, seq)
    # pick two distractors to discuss concretely
    discuss = rng.sample(distractors, 2)
    discuss_lines = []
    for s in discuss:
        p, o, _ = simulate(state["rows"], state["cols"], state["blocked"],
                           state["die"], state["orientation"], s)
        reason = []
        if p != pos:
            reason.append(f"ends at {_fmt_cell(p)} instead of {_fmt_cell(pos)}")
        if o["top"] != final_ori["top"]:
            reason.append(f"has top={o['top']} instead of {final_ori['top']}")
        if o["south"] != final_ori["south"]:
            reason.append(f"has front-left={o['south']} instead of {final_ori['south']}")
        discuss_lines.append(f'The sequence "{", ".join(s)}" ' + " and ".join(reason) + ".")
    analysis_core = (
        f"Simulate the candidate sequences from the start at {_fmt_cell(state['die'])} "
        f"(top={state['orientation']['top']}, front-left={state['orientation']['south']}, "
        f"front-right={state['orientation']['east']}):\n"
        f'Correct sequence "{correct}" step by step:\n' + trace_txt +
        f"\nIt ends at {_fmt_cell(pos)} with top={final_ori['top']} and "
        f"front-left={final_ori['south']} - exactly the required result.\n"
        + "\n".join(discuss_lines) +
        "\nEvery other listed sequence also fails to match the final cell and/or orientation."
    )
    qa = _finalize(body, options, correct, analysis_core, rng)
    qa["question_id"] = 3
    return qa


def build_task4(rng, state, unconstrained):
    """Strategy Optimization: minimum rolls to the star (maybe with top constraint)."""
    rows, cols = state["rows"], state["cols"]
    blocked, start, star = state["blocked"], state["die"], state["star"]
    ori = state["orientation"]
    if unconstrained:
        dist, path = bfs_min_rolls(rows, cols, blocked, start, ori, star, None)
        if dist is None or dist < 2 or dist > 12:
            return None
        k = None
    else:
        best = []
        for cand_k in range(1, 7):
            d, _ = bfs_min_rolls(rows, cols, blocked, start, ori, star, cand_k)
            if d is not None and 2 <= d <= 12:
                best.append((d, cand_k))
        if not best:
            return None
        preferred = [(d, k_) for d, k_ in best if 3 <= d <= 10]
        pool = preferred if preferred else best
        dist, k = rng.choice(pool)
        _, path = bfs_min_rolls(rows, cols, blocked, start, ori, star, k)

    if k is None:
        body = (f"What is the minimum number of rolls needed to move the die onto the "
                f"star cell {_fmt_cell(star)}? (The final orientation does not matter.)")
    else:
        body = (f"What is the minimum number of rolls needed to move the die onto the "
                f"star cell {_fmt_cell(star)} AND have {k} on the top face when it arrives?")
    correct = str(dist)
    offsets = [-4, -3, -2, -1, 1, 2, 3, 4]
    rng.shuffle(offsets)
    distractors = []
    for off in offsets:
        v = dist + off
        if v >= 1 and v != dist and str(v) not in distractors:
            distractors.append(str(v))
        if len(distractors) == 7:
            break
    if len(distractors) < 7:
        extra = dist + 5
        while len(distractors) < 7:
            if extra != dist and str(extra) not in distractors:
                distractors.append(str(extra))
            extra += 1
    options = [correct] + distractors

    # per-step positions of one optimal path
    step_pos = [tuple(start)]
    pos = tuple(start)
    for d in path:
        dr, dc = DIRECTIONS[d]
        pos = (pos[0] + dr, pos[1] + dc)
        step_pos.append(pos)
    path_txt = ", ".join(path)
    pos_txt = " -> ".join(_fmt_cell(p) for p in step_pos)
    if k is None:
        constraint_txt = "reaching the star cell (any orientation)"
    else:
        constraint_txt = f"reaching the star cell with top={k}"
    analysis_core = (
        f"Run a breadth-first search over (die cell, orientation) states, starting at "
        f"{_fmt_cell(start)}. The BFS expands the frontier one roll at a time: no state "
        f"{constraint_txt} appears at depths 1 to {dist - 1}, and the first such state "
        f"appears at depth {dist}.\n"
        f"One optimal sequence of {dist} rolls: {path_txt}.\n"
        f"Positions along the way: {pos_txt}."
    )
    qa = _finalize(body, options, correct, analysis_core, rng)
    qa["question_id"] = 4
    return qa
