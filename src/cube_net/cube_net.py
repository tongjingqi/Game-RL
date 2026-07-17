"""Cube Net folding puzzle: game logic, PIL rendering and QA builders.

A cube net is a set of 6 unit squares (faces) arranged edge-to-edge in one of
the 11 valid cube-net hexomino shapes. Each face carries a distinct color and
a distinct symbol. The module can:

  * enumerate the 11 valid cube nets programmatically (hexomino BFS + fold
    check, with self-checking asserts),
  * fold a net into 3D orientation frames (normal/up/right per face),
  * render a rich graph-paper style PNG of the net with PIL,
  * build the 5 multiple-choice QA task templates.

All coordinates are (row, column), 0-based, matching the rendered axes.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Rich, distinct face colors (standard names, used verbatim in questions).
COLORS = {
    "red": (231, 76, 60),
    "orange": (243, 156, 18),
    "yellow": (241, 196, 15),
    "green": (39, 174, 96),
    "blue": (52, 152, 219),
    "purple": (155, 89, 182),
}
COLOR_NAMES = list(COLORS.keys())
# Color names never used on any face (distractor pool for some tasks).
EXTRA_COLOR_NAMES = ["black", "pink", "cyan", "brown", "gray"]

SYMBOLS = ["star", "heart", "triangle", "circle", "diamond", "cross"]
# Symbol names never drawn (distractor pool).
EXTRA_SYMBOL_NAMES = ["square", "hexagon", "crescent", "arrow"]

GAME_RULES = (
    "This is a cube net puzzle. The image shows a cube net: six square faces "
    "arranged edge-to-edge on a sheet of graph paper, which can be folded "
    "along their shared edges to form a cube. Each face has a distinct color "
    "(red, orange, yellow, green, blue or purple) and a distinct symbol drawn "
    "in its center (star, heart, triangle, circle, diamond or cross), printed "
    "in white or dark ink for contrast. Row numbers are printed along the left "
    "of the grid and column numbers along the top; a grid position is written "
    "as (row, column), with both indices starting from 0. When the net is "
    "folded into a cube, each pair of faces is either opposite (they never "
    "touch) or adjacent (they share exactly one cube edge), and exactly three "
    "faces meet at every vertex (corner) of the cube.\n\n"
)

# Direction words for 3D normals, used in analyses.
DIRECTION_WORDS = {
    (0, 0, 1): "front (toward the viewer)",
    (0, 0, -1): "back",
    (1, 0, 0): "right",
    (-1, 0, 0): "left",
    (0, 1, 0): "top (up)",
    (0, -1, 0): "bottom (down)",
}

# Cell pixel size per plot level.
CELL_SIZE = {"Easy": 110, "Medium": 95, "Hard": 80}


# ---------------------------------------------------------------------------
# Vector helpers (tuples of ints)
# ---------------------------------------------------------------------------

def vneg(v):
    return tuple(-x for x in v)


def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def mat_vec(m, v):
    """Apply a 3x3 matrix (tuple of 3 rows) to a vector."""
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


def cube_rotations():
    """All 24 proper rotations of the cube: signed permutation matrices, det +1."""
    import itertools
    rots = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            m = [[0, 0, 0] for _ in range(3)]
            for i in range(3):
                m[i][perm[i]] = signs[i]
            # determinant of a signed permutation matrix
            det = 1
            p = list(perm)
            for i in range(3):
                for j in range(i + 1, 3):
                    if p[i] > p[j]:
                        det = -det
            det *= signs[0] * signs[1] * signs[2]
            if det == 1:
                rots.append(tuple(tuple(row) for row in m))
    assert len(rots) == 24
    return rots


# ---------------------------------------------------------------------------
# Hexomino enumeration + net folding
# ---------------------------------------------------------------------------

def _normalize(cells):
    mr = min(r for r, _ in cells)
    mc = min(c for _, c in cells)
    return tuple(sorted((r - mr, c - mc) for r, c in cells))


def _d4_variants(cells):
    """The 8 dihedral symmetries of a cell set."""
    pts = list(cells)
    out = []
    for fr, fc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        out.append([(fr * r, fc * c) for r, c in pts])
        out.append([(fr * c, fc * r) for r, c in pts])
    return out


def _canonical(cells):
    return min(_normalize(t) for t in _d4_variants(cells))


def enumerate_free_hexominoes():
    """All 35 free hexominoes via BFS expansion + D4 dedupe (self-checked)."""
    polys = {((0, 0),)}
    for _ in range(5):
        nxt = set()
        for poly in polys:
            s = set(poly)
            for r, c in poly:
                for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    nb = (r + dr, c + dc)
                    if nb not in s:
                        nxt.add(_normalize(s | {nb}))
        polys = nxt
    assert len(polys) == 216, len(polys)  # fixed hexominoes
    free = sorted({_canonical(p) for p in polys})
    assert len(free) == 35, len(free)  # free hexominoes
    return free


def fold_net(cells, root=None):
    """Fold a net into 3D frames.

    Returns dict cell -> {"normal": n, "up": u, "right": r} or None if the
    hexomino does not fold into a cube (inconsistent or duplicated normals).

    Convention: root face gets n=(0,0,1) [front], u=(0,1,0) [up], r=(1,0,0)
    [right]. For a neighbor at net offset (dr, dc):
      east  (0,+1): n'=r,  r'=-n, u'=u
      west  (0,-1): n'=-r, r'=n,  u'=u
      south (+1,0): n'=-u, u'=n,  r'=r
      north (-1,0): n'=u,  u'=-n, r'=r
    """
    cells = set(cells)
    if root is None:
        root = sorted(cells)[0]
    frames = {root: ((0, 0, 1), (0, 1, 0), (1, 0, 0))}  # (n, u, r)
    stack = [root]
    while stack:
        cur = stack.pop()
        n, u, r = frames[cur]
        for (dr, dc), kind in (((0, 1), "E"), ((0, -1), "W"),
                               ((1, 0), "S"), ((-1, 0), "N")):
            nb = (cur[0] + dr, cur[1] + dc)
            if nb not in cells:
                continue
            if kind == "E":
                f = (r, u, vneg(n))
            elif kind == "W":
                f = (vneg(r), u, n)
            elif kind == "S":
                f = (vneg(u), n, r)
            else:
                f = (u, vneg(n), r)
            if nb in frames:
                if frames[nb] != f:
                    return None  # inconsistent folding around a cycle
            else:
                frames[nb] = f
                stack.append(nb)
    normals = [f[0] for f in frames.values()]
    if len(set(normals)) != 6:
        return None
    return {cell: {"normal": f[0], "up": f[1], "right": f[2]}
            for cell, f in frames.items()}


def enumerate_cube_nets():
    """The 11 valid cube nets (canonical cell tuples). Self-checking."""
    nets = [p for p in enumerate_free_hexominoes() if fold_net(p) is not None]
    assert len(nets) == 11, len(nets)
    # Sanity check on the classic cross net rooted at its center cell.
    cross = ((0, 1), (1, 0), (1, 1), (1, 2), (1, 3), (2, 1))
    fr = fold_net(cross, root=(1, 1))
    side_normals = {fr[c]["normal"] for c in ((1, 0), (1, 2), (0, 1), (2, 1))}
    assert side_normals == {(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)}
    assert fr[(1, 3)]["normal"] == (0, 0, -1)
    return nets


def _max_straight_run(cells):
    """Longest straight run of cells in any row or column."""
    cells = set(cells)
    best = 0
    for r, c in cells:
        for dr, dc in ((0, 1), (1, 0)):
            k = 0
            while (r + k * dr, c + k * dc) in cells:
                k += 1
            best = max(best, k)
    return best


def net_groups():
    """Split the 11 nets into Easy/Medium/Hard shape families.

    Easy   = cross family: contains a straight strip of 4 (classic cross-like)
    Medium = longest strip is 3
    Hard   = zigzag family: longest strip is 2
    """
    groups = {"Easy": [], "Medium": [], "Hard": []}
    for i, net in enumerate(enumerate_cube_nets()):
        run = _max_straight_run(net)
        if run >= 4:
            groups["Easy"].append(i)
        elif run == 3:
            groups["Medium"].append(i)
        else:
            groups["Hard"].append(i)
    assert all(groups.values())
    return groups


# ---------------------------------------------------------------------------
# Symbol drawing
# ---------------------------------------------------------------------------

def _symbol_points(name, cx, cy, R):
    """Return a list of PIL-drawable primitives for a symbol.

    Each primitive is ("polygon", points) or ("ellipse", bbox).
    """
    if name == "star":
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rad = R if k % 2 == 0 else R * 0.45
            pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        return [("polygon", pts)]
    if name == "heart":
        prims = []
        rad = R * 0.52
        for sx in (-1, 1):
            hx, hy = cx + sx * R * 0.40, cy - R * 0.28
            prims.append(("ellipse", [hx - rad, hy - rad, hx + rad, hy + rad]))
        prims.append(("polygon", [(cx - R * 0.88, cy - R * 0.10),
                                  (cx + R * 0.88, cy - R * 0.10),
                                  (cx, cy + R * 0.92)]))
        return prims
    if name == "triangle":
        return [("polygon", [(cx, cy - R * 0.90),
                             (cx - R * 0.85, cy + R * 0.65),
                             (cx + R * 0.85, cy + R * 0.65)])]
    if name == "circle":
        return [("ellipse", [cx - R * 0.85, cy - R * 0.85,
                             cx + R * 0.85, cy + R * 0.85])]
    if name == "diamond":
        return [("polygon", [(cx, cy - R), (cx + R * 0.72, cy),
                             (cx, cy + R), (cx - R * 0.72, cy)])]
    if name == "cross":
        w = R * 0.32
        return [("polygon", [(cx - w, cy - R), (cx + w, cy - R),
                             (cx + w, cy - w), (cx + R, cy - w),
                             (cx + R, cy + w), (cx + w, cy + w),
                             (cx + w, cy + R), (cx - w, cy + R),
                             (cx - w, cy + w), (cx - R, cy + w),
                             (cx - R, cy - w), (cx - w, cy - w)])]
    raise ValueError(name)


def draw_symbol(draw, name, cx, cy, R, fill):
    for kind, shape in _symbol_points(name, cx, cy, R):
        if kind == "polygon":
            draw.polygon(shape, fill=fill)
        else:
            draw.ellipse(shape, fill=fill)


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def _scale(rgb, f):
    return tuple(max(0, min(255, int(round(c * f)))) for c in rgb)


def _blend(rgb, other, t):
    return tuple(int(round(c + (o - c) * t)) for c, o in zip(rgb, other))


def _luminance(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def symbol_ink(rgb):
    """White or dark ink, whichever contrasts better with the face color."""
    return (250, 250, 250) if _luminance(rgb) < 150 else (44, 52, 64)


# ---------------------------------------------------------------------------
# CubeNet: one puzzle instance
# ---------------------------------------------------------------------------

class CubeNet:
    def __init__(self, net_id, cells, faces, plot_level):
        self.net_id = net_id
        self.cells = [tuple(c) for c in cells]
        self.faces = faces  # list of dicts: cell/color/rgb/symbol/normal/up/right
        self.plot_level = plot_level
        self.grid_rows = max(r for r, _ in self.cells) + 1
        self.grid_cols = max(c for _, c in self.cells) + 1

    # -- construction ------------------------------------------------------

    @classmethod
    def generate(cls, rng, plot_level, pick):
        nets = enumerate_cube_nets()
        group = net_groups()[plot_level]
        net_id = group[pick % len(group)]
        cells = list(nets[net_id])
        frames = fold_net(cells)
        colors = COLOR_NAMES[:]
        symbols = SYMBOLS[:]
        rng.shuffle(colors)
        rng.shuffle(symbols)
        faces = []
        for cell, color, symbol in zip(sorted(cells), colors, symbols):
            f = frames[cell]
            faces.append({
                "cell": [cell[0], cell[1]],
                "color": color,
                "rgb": list(COLORS[color]),
                "symbol": symbol,
                "normal": list(f["normal"]),
                "up": list(f["up"]),
                "right": list(f["right"]),
            })
        return cls(net_id, cells, faces, plot_level)

    # -- queries ------------------------------------------------------------

    def face_by_color(self, color):
        return next(f for f in self.faces if f["color"] == color)

    def face_by_symbol(self, symbol):
        return next(f for f in self.faces if f["symbol"] == symbol)

    def normal_of(self, color):
        return tuple(self.face_by_color(color)["normal"])

    def color_with_normal(self, n):
        return next(f["color"] for f in self.faces
                    if tuple(f["normal"]) == tuple(n))

    def opposite_color(self, color):
        return self.color_with_normal(vneg(self.normal_of(color)))

    def adjacent_colors(self, color):
        n = self.normal_of(color)
        return sorted(f["color"] for f in self.faces
                      if f["color"] != color
                      and tuple(f["normal"]) != vneg(n))

    def opposite_pairs(self):
        pairs = []
        seen = set()
        for f in self.faces:
            c = f["color"]
            if c in seen:
                continue
            o = self.opposite_color(c)
            pairs.append(tuple(sorted((c, o))))
            seen.add(c)
            seen.add(o)
        return sorted(pairs)

    def vertex_triples(self):
        """The 8 vertex triples: one face per opposite pair, as sorted tuples."""
        by_normal = {tuple(f["normal"]): f["color"] for f in self.faces}
        triples = []
        for sx in (1, -1):
            for sy in (1, -1):
                for sz in (1, -1):
                    triples.append(tuple(sorted((
                        by_normal[(sx, 0, 0)],
                        by_normal[(0, sy, 0)],
                        by_normal[(0, 0, sz)]))))
        return triples

    # -- state ---------------------------------------------------------------

    def to_state(self):
        return {
            "net_id": self.net_id,
            "plot_level": self.plot_level,
            "cells": [list(c) for c in sorted(self.cells)],
            "faces": self.faces,
            "grid_rows": self.grid_rows,
            "grid_cols": self.grid_cols,
        }

    # -- rendering -----------------------------------------------------------

    def render(self, path):
        cell = CELL_SIZE[self.plot_level]
        rows, cols = self.grid_rows, self.grid_cols
        left_m, right_m = 46, 26
        title_h, col_label_h, bottom_m = 54, 30, 26
        ox, oy = left_m, title_h + col_label_h
        W = ox + cols * cell + right_m
        H = oy + rows * cell + bottom_m

        paper = (250, 244, 229)
        img = Image.new("RGB", (W, H), paper)
        draw = ImageDraw.Draw(img)

        # Graph-paper backdrop: major lines on the cell lattice.
        major = (216, 206, 184)
        k = 0
        while ox + k * cell < W:
            x = ox + k * cell
            if x >= 0:
                draw.line([(x, 0), (x, H)], fill=major, width=1)
            k += 1
        k = -1
        while ox + k * cell >= 0:
            draw.line([(ox + k * cell, 0), (ox + k * cell, H)], fill=major, width=1)
            k -= 1
        k = 0
        while oy + k * cell < H:
            y = oy + k * cell
            if y >= 0:
                draw.line([(0, y), (W, y)], fill=major, width=1)
            k += 1
        k = -1
        while oy + k * cell >= 0:
            draw.line([(0, oy + k * cell), (W, oy + k * cell)], fill=major, width=1)
            k -= 1
        # Hard mode: busier backdrop with faint half-cell minor lines.
        if self.plot_level == "Hard":
            minor = (232, 224, 205)
            half = cell // 2
            x = (ox + half) % half
            for x in range(ox + half, W, cell):
                draw.line([(x, 0), (x, H)], fill=minor, width=1)
            for y in range(oy + half, H, cell):
                draw.line([(0, y), (W, y)], fill=minor, width=1)

        # Faint frame around the sheet.
        draw.rectangle([3, 3, W - 4, H - 4], outline=(198, 186, 160), width=2)

        # Title.
        font_title = ImageFont.truetype(FONT_BOLD, 32)
        title = "Cube Net"
        tw = draw.textlength(title, font=font_title)
        draw.text(((W - tw) / 2, 10), title, font=font_title, fill=(64, 58, 50))

        # Axis labels (0-based, rows left / columns top).
        font_axis = ImageFont.truetype(FONT_REG, 20)
        axis_ink = (96, 88, 74)
        for r in range(rows):
            y = oy + r * cell + cell / 2
            label = str(r)
            lw = draw.textlength(label, font=font_axis)
            draw.text((ox - 16 - lw, y - 12), label, font=font_axis, fill=axis_ink)
        for c in range(cols):
            x = ox + c * cell + cell / 2
            label = str(c)
            lw = draw.textlength(label, font=font_axis)
            draw.text((x - lw / 2, oy - 26), label, font=font_axis, fill=axis_ink)

        # Soft drop shadows under the tiles.
        m = max(4, cell // 24)
        radius = cell // 8
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        for r, c in self.cells:
            x0, y0 = ox + c * cell + m, oy + r * cell + m
            x1, y1 = ox + (c + 1) * cell - m, oy + (r + 1) * cell - m
            sd.rounded_rectangle([x0 + 4, y0 + 6, x1 + 4, y1 + 6],
                                 radius=radius, fill=(52, 42, 20, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(4))
        img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Tiles with bevel and symbol.
        for f in self.faces:
            r, c = f["cell"]
            rgb = tuple(f["rgb"])
            x0, y0 = ox + c * cell + m, oy + r * cell + m
            x1, y1 = ox + (c + 1) * cell - m, oy + (r + 1) * cell - m
            draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=rgb)
            # 3D bevel: light top/left inner edges, dark bottom/right.
            light = _blend(rgb, (255, 255, 255), 0.45)
            dark = _scale(rgb, 0.55)
            inset = 4
            draw.line([(x0 + radius, y0 + inset), (x1 - radius, y0 + inset)],
                      fill=light, width=3)
            draw.line([(x0 + inset, y0 + radius), (x0 + inset, y1 - radius)],
                      fill=light, width=3)
            draw.line([(x0 + radius, y1 - inset), (x1 - radius, y1 - inset)],
                      fill=dark, width=3)
            draw.line([(x1 - inset, y0 + radius), (x1 - inset, y1 - radius)],
                      fill=dark, width=3)
            # Border.
            draw.rounded_rectangle([x0, y0, x1, y1], radius=radius,
                                   outline=_scale(rgb, 0.62), width=3)
            # Symbol with a subtle offset shadow.
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            R = cell * 0.27
            draw_symbol(draw, f["symbol"], cx + 2, cy + 3, R, _scale(rgb, 0.48))
            draw_symbol(draw, f["symbol"], cx, cy, R, symbol_ink(rgb))

        img.save(path)
        return (W, H)


# ---------------------------------------------------------------------------
# QA builders
# ---------------------------------------------------------------------------

TASK_INFO = {
    1: ("Target Perception", "Easy",
        "Identify a face's color, symbol, or grid position in the net"),
    2: ("State Prediction", "Medium",
        "Determine which face is opposite a given face after folding"),
    3: ("State Prediction", "Medium",
        "Determine the set of faces adjacent to a given face after folding"),
    4: ("State Prediction", "Hard",
        "Determine which color ends up on a given side of the placed cube"),
    5: ("State Prediction", "Hard",
        "Identify which three faces meet at a single cube vertex"),
}


def _assemble(qid, body, correct, distractors, analysis_body, rng):
    """Shuffle options, number them, and compose question/analysis text."""
    assert correct not in distractors
    assert len(set(distractors)) == len(distractors)
    options = distractors + [correct]
    rng.shuffle(options)
    answer = options.index(correct) + 1
    options_block = "\n\nOptions:\n" + "\n".join(
        f"[{i + 1}] {o}" for i, o in enumerate(options))
    qa_type, qa_level, description = TASK_INFO[qid]
    analysis = (analysis_body +
                f"\n\nSo the answer is {correct}. The option number is {answer}.")
    return {
        "qa_type": qa_type,
        "qa_level": qa_level,
        "question_id": qid,
        "question_description": description,
        "question": GAME_RULES + body + options_block,
        "answer": answer,
        "analysis": analysis,
        "options": options,
    }


def _fold_trace(net):
    """Human-readable fold orientation list, used in several analyses."""
    lines = []
    for f in sorted(net.faces, key=lambda x: x["cell"]):
        d = DIRECTION_WORDS[tuple(f["normal"])]
        lines.append(f"- {f['color']} face ({f['symbol']}) at grid "
                     f"({f['cell'][0]}, {f['cell'][1]}): {d}")
    header = ("Folding the net (taking the face at grid position "
              f"({net.faces[0]['cell'][0]}, {net.faces[0]['cell'][1]}) as the "
              "reference front face) gives these final orientations:")
    return header + "\n" + "\n".join(lines)


def build_task1(net, rng, subtype):
    """Face identification: color-by-symbol / symbol-by-color / position."""
    if subtype == 0:  # symbol -> color
        face = rng.choice(net.faces)
        body = f"Which color is the face with the {face['symbol']} symbol?"
        correct = face["color"]
        others = [c for c in COLOR_NAMES if c != correct]
        distractors = others + rng.sample(EXTRA_COLOR_NAMES, 2)
        analysis = (f"Look at the net in the image and find the face carrying "
                    f"the {face['symbol']} symbol. It is located at grid "
                    f"position ({face['cell'][0]}, {face['cell'][1]}) and its "
                    f"color is {correct}.")
    elif subtype == 1:  # color -> symbol
        face = rng.choice(net.faces)
        body = f"Which symbol is drawn on the {face['color']} face?"
        correct = face["symbol"]
        others = [s for s in SYMBOLS if s != correct]
        distractors = others + rng.sample(EXTRA_SYMBOL_NAMES, 2)
        analysis = (f"Find the {face['color']} face in the net: it is at grid "
                    f"position ({face['cell'][0]}, {face['cell'][1]}). The "
                    f"symbol drawn in its center is the {correct}.")
    else:  # color -> position
        face = rng.choice(net.faces)
        body = (f"What is the grid position (row, column) of the "
                f"{face['color']} face?")
        correct = f"({face['cell'][0]}, {face['cell'][1]})"
        candidates = []
        occupied = {tuple(f["cell"]) for f in net.faces}
        # Other occupied cells first, then empty cells inside the bounding box.
        others_occ = sorted(occupied - {tuple(face["cell"])})
        rng.shuffle(others_occ)
        candidates.extend(others_occ)
        empties = [(r, c) for r in range(net.grid_rows)
                   for c in range(net.grid_cols) if (r, c) not in occupied]
        rng.shuffle(empties)
        candidates.extend(empties)
        distractors = [f"({r}, {c})" for r, c in candidates[:7]]
        analysis = (f"Scan the net for the {face['color']} face. Using the row "
                    f"numbers on the left and the column numbers on the top, "
                    f"it sits at row {face['cell'][0]}, column "
                    f"{face['cell'][1]}, i.e. grid position {correct}. Its "
                    f"symbol is the {face['symbol']}.")
    return _assemble(1, body, correct, distractors, analysis, rng)


def build_task2(net, rng):
    """Opposite face."""
    face = rng.choice(net.faces)
    color = face["color"]
    correct = net.opposite_color(color)
    body = (f"When this net is folded into a cube, which face is opposite to "
            f"the {color} face?")
    distractors = [c for c in COLOR_NAMES if c not in (color, correct)]
    distractors += [rng.choice(EXTRA_COLOR_NAMES)]
    trace = _fold_trace(net)
    n_dir = DIRECTION_WORDS[tuple(face["normal"])]
    o_dir = DIRECTION_WORDS[tuple(net.face_by_color(correct)["normal"])]
    analysis = (trace + f"\nThe {color} face ends up pointing to the {n_dir}. "
                f"The face pointing in the exact opposite direction "
                f"({o_dir}) is the {correct} face, so those two faces are "
                f"opposite each other on the cube.")
    return _assemble(2, body, correct, distractors, analysis, rng)


def build_task3(net, rng):
    """Adjacent face set (4 colors), exactly 5 near-miss options.

    Options are all five 4-subsets of "the other five colors" (every color
    except the queried one): the correct set is the only one that does not
    contain the opposite face; each of the four distractors contains the
    opposite face plus three of the four truly adjacent faces.
    """
    import itertools
    face = rng.choice(net.faces)
    color = face["color"]
    correct_set = tuple(net.adjacent_colors(color))
    correct = ", ".join(correct_set)
    body = (f"After the net is folded into a cube, which set of faces shares "
            f"an edge with the {color} face?")
    others5 = sorted(c for c in COLOR_NAMES if c != color)
    all_sets = [tuple(sorted(s)) for s in itertools.combinations(others5, 4)]
    assert len(all_sets) == 5 and correct_set in all_sets
    wrong_sets = [s for s in all_sets if s != correct_set]
    assert len(wrong_sets) == 4
    distractors = [", ".join(s) for s in wrong_sets]
    trace = _fold_trace(net)
    n_dir = DIRECTION_WORDS[tuple(face["normal"])]
    opp = net.opposite_color(color)
    adj_list = ", ".join(f"{c} ({DIRECTION_WORDS[net.normal_of(c)]})"
                         for c in correct_set)
    analysis = (trace + f"\nThe {color} face points to the {n_dir}. A cube "
                f"face shares an edge with every face except itself and its "
                f"opposite face. The key discriminator is the opposite face: "
                f"the face opposite to {color} is {opp}, which can never "
                f"share an edge with {color}. The correct set is therefore "
                f"the only option that does not contain {opp}; every other "
                f"option smuggles {opp} in alongside three genuinely "
                f"adjacent faces. The four faces that share an edge with "
                f"{color} are: {adj_list}.")
    return _assemble(3, body, correct, distractors, analysis, rng)


def build_task4(net, rng, ask):
    """Orientation reasoning: placed cube, ask a SIDE face.

    `ask` is one of "RIGHT", "LEFT", "BACK" (given BOTTOM + FRONT). The TOP
    face is deliberately never asked: it would always just be the opposite
    of the BOTTOM face, duplicating task 2.
    """
    assert ask in ("RIGHT", "LEFT", "BACK")
    # Pick an ordered pair of adjacent faces: c1 -> BOTTOM, c2 -> FRONT.
    colors = COLOR_NAMES[:]
    rng.shuffle(colors)
    pair = None
    for c1 in colors:
        for c2 in colors:
            if c1 != c2 and c2 in net.adjacent_colors(c1):
                pair = (c1, c2)
                break
        if pair:
            break
    c1, c2 = pair
    n1, n2 = net.normal_of(c1), net.normal_of(c2)
    rots = cube_rotations()
    target_bottom, target_front = (0, 0, -1), (0, -1, 0)
    rot = next(m for m in rots
               if mat_vec(m, n1) == target_bottom
               and mat_vec(m, n2) == target_front)
    wanted = {"RIGHT": (1, 0, 0), "LEFT": (-1, 0, 0), "BACK": (0, 0, 1)}[ask]
    target_normal = next(tuple(f["normal"]) for f in net.faces
                         if mat_vec(rot, tuple(f["normal"])) == wanted)
    correct = net.color_with_normal(target_normal)
    body = (f"The net is folded into a cube and the cube is placed so that "
            f"the {c1} face is on the BOTTOM and the {c2} face faces you "
            f"(the FRONT). Which color is on the {ask} face?")
    distractors = [c for c in COLOR_NAMES if c != correct]
    distractors += ["Cannot be determined", "None of the above"]
    trace = _fold_trace(net)
    if ask in ("RIGHT", "LEFT"):
        # A proper rotation preserves cross products, so the wanted side's
        # folded direction is a cross product of the given directions.
        cross = vcross(n2, n1) if ask == "RIGHT" else vcross(n1, n2)
        analysis = (
            trace +
            f"\nThe {c1} face has folded direction {n1} and goes to the "
            f"BOTTOM; the {c2} face has folded direction {n2} and goes to "
            f"the FRONT. For a proper rotation, the face that lands on the "
            f"{ask} is the one whose folded direction equals "
            + (f"(front direction) x (bottom direction) = {n2} x {n1} = "
               f"{cross}" if ask == "RIGHT" else
               f"(bottom direction) x (front direction) = {n1} x {n2} = "
               f"{cross}") +
            f". From the orientations above, the face with folded direction "
            f"{cross} is the {correct} face.")
    else:  # BACK
        back_normal = vneg(n2)
        analysis = (
            trace +
            f"\nThe {c1} face has folded direction {n1} and goes to the "
            f"BOTTOM; the {c2} face has folded direction {n2} and goes to "
            f"the FRONT. The BACK of the placed cube points opposite to the "
            f"FRONT, so the BACK face is the one whose folded direction is "
            f"the negation of the {c2} face's direction, i.e. -{n2} = "
            f"{back_normal}. From the orientations above, the face with "
            f"folded direction {back_normal} is the {correct} face (indeed "
            f"the face opposite to {c2}, with the {c1}-on-BOTTOM condition "
            f"fixing the cube's roll about the front-back axis).")
    return _assemble(4, body, correct, distractors, analysis, rng)


def build_task5(net, rng):
    """Vertex triple."""
    import itertools
    triples = net.vertex_triples()
    correct_t = triples[rng.randrange(len(triples))]
    correct = ", ".join(correct_t)
    body = ("After the net is folded into a cube, which set of three faces "
            "meets at a single vertex (corner) of the cube?")
    all_triples = [tuple(sorted(t))
                   for t in itertools.combinations(COLOR_NAMES, 3)]
    non_vertex = [t for t in all_triples if t not in triples]
    rng.shuffle(non_vertex)
    distractors = [", ".join(t) for t in non_vertex[:7]]
    pairs = net.opposite_pairs()
    pair_txt = "; ".join(f"{a} is opposite {b}" for a, b in pairs)
    dirs = ", ".join(f"{c} ({DIRECTION_WORDS[net.normal_of(c)]})"
                     for c in correct_t)
    analysis = (
        _fold_trace(net) +
        f"\nThe three opposite face pairs are: {pair_txt}. Every vertex of a "
        "cube is touched by exactly one face from each opposite pair, so a "
        "valid vertex triple must contain no opposite pair, and any such "
        f"choice of one face per pair does meet at one corner. The triple "
        f"{correct} contains no opposite pair; reading the fold orientations, "
        f"the three faces {dirs} indeed meet at one cube corner. Each of the "
        "other listed triples contains an opposite pair, so those faces "
        "cannot meet at a single vertex.")
    return _assemble(5, body, correct, distractors, analysis, rng)
