"""Lights Out puzzle: game logic, PIL rendering, and QA builders for GameQA.

Lights Out is played on an N x N grid of buttons. Pressing a button toggles
its own light and the lights of its orthogonal neighbors. This module provides
board generation, an exact GF(2) solver, rich PIL rendering, and the builders
for every supported question template.
"""

import itertools
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Fixed game-rules preamble prepended to every question
# ---------------------------------------------------------------------------

GAME_RULES = (
    "Lights Out is a puzzle played on a square grid of buttons, one light per button. "
    "In the picture, a light is either ON (a glowing yellow button) or OFF (a dark slate button). "
    "Positions are written as (row, column) and are 0-based: the top-left button is at row 0, "
    "column 0, rows increase downward and columns increase to the right; row numbers are printed "
    "along the left edge of the board and column numbers along the top edge. "
    "Pressing a button toggles its own light and the lights of its orthogonal neighbors (the "
    "buttons directly above, below, to the left and to the right, as many as exist): every toggled "
    "light that was ON turns OFF and every toggled light that was OFF turns ON. Pressing the same "
    "button twice has no net effect, and the order of presses does not matter. "
    "The classic goal of the puzzle is to turn ALL the lights OFF."
)

# ---------------------------------------------------------------------------
# Core game logic
# ---------------------------------------------------------------------------


def press_pattern(size, r, c):
    """Return the list of cells toggled by pressing the button at (r, c)."""
    cells = [(r, c)]
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < size and 0 <= cc < size:
            cells.append((rr, cc))
    return cells


def apply_presses(grid, presses):
    """Return a new grid after applying the given presses (order irrelevant)."""
    size = len(grid)
    out = [row[:] for row in grid]
    for (r, c) in presses:
        for (rr, cc) in press_pattern(size, r, c):
            out[rr][cc] ^= 1
    return out


def count_on(grid):
    return sum(sum(row) for row in grid)


def on_cells(grid):
    size = len(grid)
    return [(r, c) for r in range(size) for c in range(size) if grid[r][c]]


def generate_board(size, k, rng):
    """Generate a board by applying k distinct random presses to an all-OFF grid.

    The result is guaranteed to be neither all-OFF nor all-ON, and solvable by
    construction. Returns (grid, presses_made).
    """
    cells = [(r, c) for r in range(size) for c in range(size)]
    while True:
        presses = rng.sample(cells, k)
        grid = apply_presses([[0] * size for _ in range(size)], presses)
        total = count_on(grid)
        if 0 < total < size * size:
            return grid, presses


# ---------------------------------------------------------------------------
# Exact GF(2) solver (bitmask Gaussian elimination)
# ---------------------------------------------------------------------------


def solve_lights_out(grid):
    """Solve the Lights Out system Ax = grid over GF(2).

    Returns a dict with:
      - solvable: bool
      - nullity: dimension of the solution (affine) space
      - min_weight: minimum number of presses among all solutions
      - min_presses: one minimum-weight solution, sorted list of (r, c)
      - num_solutions: total number of solutions
    """
    size = len(grid)
    m = size * size
    b = [grid[r][c] for r in range(size) for c in range(size)]

    # Row i of the toggle matrix as a bitmask over press variables j.
    rows = []
    for i in range(m):
        r, c = divmod(i, size)
        mask = 0
        for (pr, pc) in press_pattern(size, r, c):
            mask |= 1 << (pr * size + pc)
        rows.append([mask, b[i]])

    # Gauss-Jordan elimination over GF(2).
    pivot_row_of_col = {}
    n_rows = 0
    for col in range(m):
        sel = -1
        for i in range(n_rows, m):
            if (rows[i][0] >> col) & 1:
                sel = i
                break
        if sel == -1:
            continue
        rows[n_rows], rows[sel] = rows[sel], rows[n_rows]
        for i in range(m):
            if i != n_rows and ((rows[i][0] >> col) & 1):
                rows[i][0] ^= rows[n_rows][0]
                rows[i][1] ^= rows[n_rows][1]
        pivot_row_of_col[col] = n_rows
        n_rows += 1

    for i in range(m):
        if rows[i][0] == 0 and rows[i][1] == 1:
            return {"solvable": False}

    free_cols = [c for c in range(m) if c not in pivot_row_of_col]
    nullity = len(free_cols)

    def solution_for(free_vals):
        x = [0] * m
        for c, v in zip(free_cols, free_vals):
            x[c] = v
        for col, ri in pivot_row_of_col.items():
            val = rows[ri][1]
            mask = rows[ri][0]
            for c in free_cols:
                if (mask >> c) & 1:
                    val ^= x[c]
            x[col] = val
        return x

    best_weight = None
    best_x = None
    for free_vals in itertools.product((0, 1), repeat=nullity):
        x = solution_for(free_vals)
        w = sum(x)
        if best_weight is None or w < best_weight:
            best_weight = w
            best_x = x

    min_presses = sorted(
        (divmod(j, size) for j in range(m) if best_x[j]), key=lambda t: (t[0], t[1])
    )
    return {
        "solvable": True,
        "nullity": nullity,
        "min_weight": best_weight,
        "min_presses": min_presses,
        "num_solutions": 1 << nullity,
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SUPERSAMPLE = 2


def _layout(n):
    """Pixel layout (final scale) for an n x n board; long side stays <= 640."""
    btn = {3: 118, 4: 100, 5: 80}[n]
    gap = 14 if n <= 4 else 12
    grid_px = n * btn + (n - 1) * gap
    left_pad = 62
    right_pad = 34
    top_pad = 106   # title strip + column labels
    bottom_pad = 86  # footer legend + rule line; keeps the 5x5 board at 640 px
    width = left_pad + grid_px + right_pad
    height = top_pad + grid_px + bottom_pad
    return btn, gap, left_pad, top_pad, width, height


def _fit_font(text, max_width_px, start_size, bold=True):
    """Largest DejaVu font size (final px) whose text fits max_width_px (supersampled)."""
    path = FONT_BOLD if bold else FONT_REG
    for size in range(start_size, 10, -1):
        font = ImageFont.truetype(path, size * SUPERSAMPLE)
        probe = ImageDraw.Draw(Image.new("RGB", (4, 4)))
        if probe.textlength(text, font=font) <= max_width_px * SUPERSAMPLE:
            return font, size
    return ImageFont.truetype(path, 11 * SUPERSAMPLE), 11


def _vertical_gradient(w, h, top_color, bottom_color):
    grad = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        grad.putpixel(
            (0, y),
            tuple(int(top_color[i] + (bottom_color[i] - top_color[i]) * t) for i in range(3)),
        )
    return grad.resize((w, h))


def _rounded_tile(w, h, radius, top_color, bottom_color):
    """Vertical gradient clipped to a rounded rectangle (RGBA)."""
    grad = _vertical_gradient(w, h, top_color, bottom_color)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    tile = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tile.paste(grad, (0, 0), mask)
    return tile


def _background(width, height):
    """Deep blue-gray gradient with vignette and subtle noise (RGBA, supersampled)."""
    w, h = width * SUPERSAMPLE, height * SUPERSAMPLE
    top = np.array([40, 51, 66], dtype=float)
    bot = np.array([17, 23, 32], dtype=float)
    t = np.linspace(0.0, 1.0, h)[:, None, None]
    img = np.broadcast_to(top * (1 - t) + bot * t, (h, w, 3)).copy()

    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    vignette = 1.0 - 0.30 * np.clip(dist - 0.55, 0.0, None)
    img *= vignette[..., None]

    rng = np.random.RandomState(7)
    img += rng.normal(0.0, 2.0, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype("uint8")).convert("RGBA")


def render_board(grid, path):
    """Render the board to a PNG file (final long side <= 640 px)."""
    n = len(grid)
    S = SUPERSAMPLE
    btn, gap, left_pad, top_pad, width, height = _layout(n)
    grid_px = n * btn + (n - 1) * gap

    img = _background(width, height)
    draw = ImageDraw.Draw(img)

    # Control panel behind grid + labels.
    panel = [14 * S, (top_pad - 42) * S, (width - 14) * S, (top_pad + grid_px + 18) * S]
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [panel[0], panel[1] + 6 * S, panel[2], panel[3] + 6 * S], radius=22 * S, fill=(0, 0, 0, 110)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(8 * S))
    img = Image.alpha_composite(img, shadow)
    panel_tile = _rounded_tile(
        panel[2] - panel[0], panel[3] - panel[1], 22 * S, (33, 43, 56), (24, 32, 43)
    )
    img.paste(panel_tile, (panel[0], panel[1]), panel_tile)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(panel, radius=22 * S, outline=(70, 86, 106, 255), width=2 * S)
    draw.rounded_rectangle(
        [panel[0] + 2 * S, panel[1] + 2 * S, panel[2] - 2 * S, panel[3] - 2 * S],
        radius=20 * S,
        outline=(52, 66, 83, 160),
        width=1 * S,
    )

    # Title.
    title_font = ImageFont.truetype(FONT_BOLD, 30 * S)
    title = "Lights Out"
    tw = draw.textlength(title, font=title_font)
    tx = (width * S - tw) / 2
    ty = 20 * S
    draw.text((tx + 2 * S, ty + 3 * S), title, font=title_font, fill=(0, 0, 0, 140))
    draw.text((tx, ty), title, font=title_font, fill=(232, 238, 246, 255))

    # Coordinate labels (0-based): columns on top, rows on the left.
    label_font = ImageFont.truetype(FONT_BOLD, 20 * S)
    label_color = (196, 206, 220, 255)
    for c in range(n):
        x = left_pad + c * (btn + gap)
        cx = (x + btn / 2) * S
        cy = (top_pad - 20) * S
        text = str(c)
        bb = draw.textbbox((0, 0), text, font=label_font)
        draw.text(
            (cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]),
            text, font=label_font, fill=label_color,
        )
    for r in range(n):
        y = top_pad + r * (btn + gap)
        cy = (y + btn / 2) * S
        cx = 34 * S
        text = str(r)
        bb = draw.textbbox((0, 0), text, font=label_font)
        draw.text(
            (cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]),
            text, font=label_font, fill=label_color,
        )

    # Soft outer glow behind ON buttons.
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for (r, c) in on_cells(grid):
        x = (left_pad + c * (btn + gap)) * S
        y = (top_pad + r * (btn + gap)) * S
        s = btn * S
        for expand, alpha in ((7, 74), (16, 44), (28, 22)):
            e = expand * S
            gd.rounded_rectangle(
                [x - e, y - e, x + s + e, y + s + e],
                radius=(16 + expand) * S,
                fill=(255, 217, 77, alpha),
            )
    glow = glow.filter(ImageFilter.GaussianBlur(9 * S))
    img = Image.alpha_composite(img, glow)

    # Buttons.
    for r in range(n):
        for c in range(n):
            x = (left_pad + c * (btn + gap)) * S
            y = (top_pad + r * (btn + gap)) * S
            s = btn * S
            radius = 16 * S
            if grid[r][c]:
                tile = _rounded_tile(s, s, radius, (255, 233, 145), (255, 190, 52))
                img.paste(tile, (x, y), tile)
                d = ImageDraw.Draw(img)
                d.rounded_rectangle([x, y, x + s - 1, y + s - 1], radius=radius,
                                    outline=(226, 158, 24, 255), width=2 * S)
                # Bright specular dot (upper-left) + soft center bloom.
                sheen = Image.new("RGBA", (s, s), (0, 0, 0, 0))
                sd = ImageDraw.Draw(sheen)
                sd.ellipse([int(0.16 * s), int(0.10 * s), int(0.52 * s), int(0.34 * s)],
                           fill=(255, 255, 255, 105))
                sheen = sheen.filter(ImageFilter.GaussianBlur(3 * S))
                img.paste(sheen, (x, y), sheen)
                d = ImageDraw.Draw(img)
                d.ellipse([x + int(0.20 * s), y + int(0.13 * s),
                           x + int(0.34 * s), y + int(0.24 * s)],
                          fill=(255, 255, 255, 215))
            else:
                tile = _rounded_tile(s, s, radius, (66, 82, 101), (38, 50, 65))
                img.paste(tile, (x, y), tile)
                d = ImageDraw.Draw(img)
                d.rounded_rectangle([x, y, x + s - 1, y + s - 1], radius=radius,
                                    outline=(20, 27, 36, 255), width=2 * S)
                # Top bevel highlight.
                bevel = Image.new("RGBA", (s, s), (0, 0, 0, 0))
                ImageDraw.Draw(bevel).rounded_rectangle(
                    [2 * S, 2 * S, s - 3 * S, int(0.30 * s)], radius=radius - 3 * S,
                    fill=(140, 160, 185, 42),
                )
                img.paste(bevel, (x, y), bevel)

    # Footer: ON/OFF legend + rule reminder.
    draw = ImageDraw.Draw(img)
    footer_font, _ = _fit_font("ON", 60, 16, bold=True)
    legend_y = (height - 66) * S
    icon = 22 * S
    lx = left_pad * S
    # ON icon with glow.
    on_tile = _rounded_tile(icon, icon, 6 * S, (255, 233, 145), (255, 190, 52))
    img.paste(on_tile, (lx, legend_y), on_tile)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([lx, legend_y, lx + icon - 1, legend_y + icon - 1],
                           radius=6 * S, outline=(226, 158, 24, 255), width=1 * S)
    lx += icon + 8 * S
    draw.text((lx, legend_y + 2 * S), "ON", font=footer_font, fill=(222, 230, 240, 255))
    lx = int(round(lx + draw.textlength("ON", font=footer_font) + 26 * S))
    off_tile = _rounded_tile(icon, icon, 6 * S, (66, 82, 101), (38, 50, 65))
    img.paste(off_tile, (lx, legend_y), off_tile)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([lx, legend_y, lx + icon - 1, legend_y + icon - 1],
                           radius=6 * S, outline=(20, 27, 36, 255), width=1 * S)
    lx += icon + 8 * S
    draw.text((lx, legend_y + 2 * S), "OFF", font=footer_font, fill=(222, 230, 240, 255))

    rule_text = "Pressing a button toggles it and its orthogonal neighbors."
    rule_font, rule_size = _fit_font(rule_text, width - 2 * left_pad, 16, bold=False)
    rw = draw.textlength(rule_text, font=rule_font)
    draw.text(((width * S - rw) / 2, (height - 36) * S), rule_text,
              font=rule_font, fill=(158, 170, 186, 255))

    img = img.convert("RGB").resize((width, height), Image.LANCZOS)
    img.save(path)


# ---------------------------------------------------------------------------
# QA builders
# ---------------------------------------------------------------------------

QUESTION_DESCRIPTIONS = {
    1: "Identify states and counts of lights on the board",
    2: "Predict the board after a sequence of button presses",
    3: "Infer which button press(es) produced the shown board",
    4: "Find the minimum presses needed to turn all lights off",
}

QA_TYPES = {
    1: ("Target Perception", "Easy"),
    2: ("State Prediction", "Medium"),
    3: ("State Prediction", "Hard"),
    4: ("Strategy Optimization", "Hard"),
}


def _fmt_cell(cell):
    return f"({cell[0]}, {cell[1]})"


def _fmt_presses(presses):
    return ", ".join(_fmt_cell(p) for p in presses)


def _number_options(true_val, lo, hi, rng, count=8):
    """true_val plus distinct distractors in [lo, hi], true +/- 1..4 first."""
    values = {true_val}
    d = 1
    while len(values) < count and d <= max(hi - lo, count) + 4:
        for cand in (true_val - d, true_val + d):
            if lo <= cand <= hi and len(values) < count:
                values.add(cand)
        d += 1
    opts = sorted(values)
    rng.shuffle(opts)
    return [str(v) for v in opts]


def _cell_distractors(size, exclude, rng, count=7):
    cells = [(r, c) for r in range(size) for c in range(size)
             if (r, c) not in exclude]
    return rng.sample(cells, min(count, len(cells)))


def build_task1(grid, variant, rng):
    """Target Perception. Returns (body, options, correct, analysis_core)."""
    size = len(grid)

    if variant == "a":  # states of three cells
        cells = rng.sample([(r, c) for r in range(size) for c in range(size)], 3)
        states = ["ON" if grid[r][c] else "OFF" for (r, c) in cells]
        correct = ", ".join(states)
        combos = [", ".join(bits) for bits in itertools.product(("ON", "OFF"), repeat=3)]
        body = (
            f"What are the states of the lights at {_fmt_cell(cells[0])}, "
            f"{_fmt_cell(cells[1])} and {_fmt_cell(cells[2])} (in that order)?"
        )
        lines = [
            f"Looking at the picture, the light at {_fmt_cell(cells[0])} is {states[0]}, "
            f"the light at {_fmt_cell(cells[1])} is {states[1]}, and the light at "
            f"{_fmt_cell(cells[2])} is {states[2]}.",
            f"So the states in the requested order are {correct}.",
        ]
        return body, combos, correct, "\n".join(lines)

    if variant == "b":  # total ON count
        per_row = [sum(row) for row in grid]
        total = sum(per_row)
        correct = str(total)
        options = _number_options(total, 0, size * size, rng)
        body = "How many lights are currently ON?"
        rows_txt = ", ".join(f"row {i} has {v}" for i, v in enumerate(per_row))
        lines = [
            f"Counting the glowing (yellow) buttons row by row: {rows_txt}.",
            f"Total lights ON = {' + '.join(str(v) for v in per_row)} = {total}.",
        ]
        return body, options, correct, "\n".join(lines)

    if variant == "c":  # row with the most lights ON (requires a unique maximum)
        per_row = [sum(row) for row in grid]
        best = max(per_row)
        assert per_row.count(best) == 1, "variant c requires a unique maximum row"
        row_idx = per_row.index(best)
        correct = f"Row {row_idx}"
        options = [f"Row {i}" for i in range(size)] + ["Two or more rows are tied for the most"]
        body = "Which row has the most lights ON?"
        rows_txt = ", ".join(f"row {i}: {v} light(s) ON" for i, v in enumerate(per_row))
        lines = [
            f"Count the ON lights in each row: {rows_txt}.",
            f"Row {row_idx} has {best} light(s) ON, strictly more than any other row, "
            f"so there is no tie.",
        ]
        return body, options, correct, "\n".join(lines)

    if variant == "d":  # lights ON in one column
        col = rng.randrange(size)
        cells = [(r, col) for r in range(size)]
        states = ["ON" if grid[r][col] else "OFF" for (r, col) in cells]
        total = sum(grid[r][col] for r in range(size))
        correct = str(total)
        options = [str(v) for v in range(size + 1)]
        body = f"How many lights are ON in column {col}?"
        cells_txt = ", ".join(
            f"{_fmt_cell(cell)} is {st}" for cell, st in zip(cells, states)
        )
        lines = [
            f"Look at column {col} from top to bottom: {cells_txt}.",
            f"That is {total} light(s) ON in column {col}.",
        ]
        return body, options, correct, "\n".join(lines)

    raise ValueError(f"unknown task1 variant {variant}")


def build_task2(grid, variant, rng):
    """State Prediction: press sequence. Returns (body, options, correct, analysis_core)."""
    size = len(grid)
    k = {3: 2, 4: rng.choice((2, 3)), 5: 3}[size]
    presses = rng.sample([(r, c) for r in range(size) for c in range(size)], k)
    press_txt = _fmt_presses(presses)

    # Simulate press by press, tracking the ON count.
    sim = [row[:] for row in grid]
    trace_lines = [f"The board initially has {count_on(sim)} light(s) ON."]
    for i, (r, c) in enumerate(presses, 1):
        toggled = press_pattern(size, r, c)
        before = count_on(sim)
        for (rr, cc) in toggled:
            sim[rr][cc] ^= 1
        after = count_on(sim)
        trace_lines.append(
            f"Press {i} at {_fmt_cell((r, c))} toggles {_fmt_presses(toggled)}: "
            f"the ON count goes from {before} to {after}."
        )

    if variant == "A":  # final ON count
        total = count_on(sim)
        correct = str(total)
        options = _number_options(total, 0, size * size, rng)
        body = (
            f"Starting from the shown board, the buttons {press_txt} are pressed in that "
            f"order. How many lights will be ON afterwards?"
        )
        trace_lines.append(f"After all presses, {total} light(s) are ON.")
        return body, options, correct, "\n".join(trace_lines)

    if variant == "B":  # final states of three cells
        targets = rng.sample([(r, c) for r in range(size) for c in range(size)], 3)
        states = ["ON" if sim[r][c] else "OFF" for (r, c) in targets]
        correct = ", ".join(states)
        combos = [", ".join(bits) for bits in itertools.product(("ON", "OFF"), repeat=3)]
        body = (
            f"Starting from the shown board, the buttons {press_txt} are pressed in that "
            f"order. After these presses, what are the states of the lights at "
            f"{_fmt_cell(targets[0])}, {_fmt_cell(targets[1])} and {_fmt_cell(targets[2])} "
            f"(in that order)?"
        )
        tgt_txt = ", ".join(
            f"the light at {_fmt_cell(cell)} ends {st}" for cell, st in zip(targets, states)
        )
        trace_lines.append(f"After all presses, {tgt_txt}.")
        return body, combos, correct, "\n".join(trace_lines)

    raise ValueError(f"unknown task2 variant {variant}")


def build_task3(grid, presses_made, variant, rng):
    """State Prediction (inverse): which press(es) produced the board."""
    size = len(grid)
    lit = set(on_cells(grid))

    if variant == "a":  # single press
        assert len(presses_made) == 1
        answer = tuple(presses_made[0])
        pattern = press_pattern(size, *answer)
        assert set(pattern) == lit, "single-press board must equal its press pattern"
        distractors = _cell_distractors(size, {answer}, rng)
        options = [_fmt_cell(answer)] + [_fmt_cell(d) for d in distractors]
        correct = _fmt_cell(answer)
        body = (
            "The board started with ALL lights OFF. Exactly one button was pressed to "
            "reach the shown state. Which button was pressed?"
        )
        lines = [
            f"A single press lights up a plus-shaped pattern: the button itself and its "
            f"orthogonal neighbors (fewer cells on an edge or in a corner).",
            f"The ON lights are {_fmt_presses(sorted(lit))}.",
            f"This is exactly the pattern of pressing {_fmt_cell(answer)}: it toggles "
            f"{_fmt_presses(pattern)}, which matches the board.",
        ]
        return body, options, correct, "\n".join(lines)

    if variant == "b":  # two presses, one given
        assert len(presses_made) == 2
        given, answer = presses_made[0], presses_made[1]
        if rng.random() < 0.5:
            given, answer = answer, given
        given, answer = tuple(given), tuple(answer)
        residual = lit ^ set(press_pattern(size, *given))
        assert set(press_pattern(size, *answer)) == residual
        # Uniqueness: no other cell's press pattern equals the residual.
        for r in range(size):
            for c in range(size):
                if (r, c) != answer:
                    assert set(press_pattern(size, r, c)) != residual
        distractors = _cell_distractors(size, {given, answer}, rng)
        options = [_fmt_cell(answer)] + [_fmt_cell(d) for d in distractors]
        correct = _fmt_cell(answer)
        body = (
            f"The board started with ALL lights OFF. Exactly two buttons were pressed to "
            f"reach the shown state. One of them was {_fmt_cell(given)}. Which was the "
            f"other one?"
        )
        given_pattern = press_pattern(size, *given)
        lines = [
            f"Pressing {_fmt_cell(given)} toggles {_fmt_presses(given_pattern)}.",
            f"The board shows these lights ON: {_fmt_presses(sorted(lit))}.",
            f"Removing (XOR) the effect of {_fmt_cell(given)} from the board leaves the "
            f"lights {_fmt_presses(sorted(residual))} that the second press must have "
            f"switched ON.",
            f"That remaining set is exactly the press pattern of {_fmt_cell(answer)}: "
            f"pressing it toggles {_fmt_presses(press_pattern(size, *answer))}. "
            f"Checking the other candidates, none of their press patterns matches the "
            f"remaining set.",
        ]
        return body, options, correct, "\n".join(lines)

    raise ValueError(f"unknown task3 variant {variant}")


def build_task4(grid, variant, rng):
    """Strategy Optimization: minimum presses to all-OFF."""
    size = len(grid)
    sol = solve_lights_out(grid)
    assert sol["solvable"], "generated boards are always solvable"
    assert sol["min_weight"] >= 1, "board must not already be solved"
    min_presses = [tuple(p) for p in sol["min_presses"]]

    if variant == "numeric":
        correct = str(sol["min_weight"])
        options = _number_options(sol["min_weight"], 1, size * size, rng)
        body = (
            "What is the minimum number of button presses needed to turn ALL lights OFF "
            "from the shown state?"
        )
        press_detail = "; ".join(
            f"pressing {_fmt_cell(p)} toggles {_fmt_presses(press_pattern(size, *p))}"
            for p in min_presses
        )
        lines = [
            "Model the puzzle as a linear system over GF(2): each button press is a "
            "variable, and each light must be toggled an odd number of times to end OFF.",
            f"Solving the system and taking the solution with the fewest presses gives "
            f"the optimal press set {{{_fmt_presses(min_presses)}}}: {press_detail}.",
            f"Every ON light is toggled an odd number of times and every OFF light an "
            f"even number of times, so the board becomes completely dark after these "
            f"{sol['min_weight']} presses.",
            f"No solution with fewer presses exists - all {sol['num_solutions']} "
            f"solution(s) of the system were enumerated via linear algebra over GF(2), "
            f"so the minimum is {sol['min_weight']}.",
        ]
        return body, options, correct, "\n".join(lines)

    if variant == "set":
        correct = "{" + _fmt_presses(min_presses) + "}"
        k = len(min_presses)
        all_cells = [(r, c) for r in range(size) for c in range(size)]
        distractor_sets = []
        seen = {frozenset(min_presses)}
        attempts = 0
        while len(distractor_sets) < 7 and attempts < 400:
            attempts += 1
            if rng.random() < 0.5:
                # Swap one member of the optimal set for an outside cell.
                cand = set(min_presses)
                cand.remove(rng.choice(min_presses))
                outsiders = [cell for cell in all_cells if cell not in cand]
                cand.add(rng.choice(outsiders))
            else:
                cand = set(rng.sample(all_cells, k))
            key = frozenset(cand)
            if key in seen:
                continue
            # Must NOT actually solve the board.
            if count_on(apply_presses(grid, sorted(cand))) == 0:
                continue
            seen.add(key)
            distractor_sets.append(sorted(cand))
        assert len(distractor_sets) == 7, "could not build 7 failing distractor sets"
        options = [correct] + ["{" + _fmt_presses(s) + "}" for s in distractor_sets]
        body = (
            "Which set of button presses turns ALL lights OFF from the shown state?"
        )
        lines = [
            "Simulate each candidate set: a light ends OFF only if it is toggled an even "
            "number of times when it started ON... precisely, every ON light must be "
            "toggled an odd number of times and every OFF light an even number.",
            f"The set {{{_fmt_presses(min_presses)}}} toggles: "
            + "; ".join(
                f"{_fmt_cell(p)} -> {_fmt_presses(press_pattern(size, *p))}"
                for p in min_presses
            )
            + ".",
            f"Aggregating these toggles, every ON light is covered an odd number of "
            f"times and every OFF light an even number of times, so all lights turn OFF.",
            f"Each of the other listed sets leaves at least one light ON when simulated.",
        ]
        return body, options, correct, "\n".join(lines)

    raise ValueError(f"unknown task4 variant {variant}")
