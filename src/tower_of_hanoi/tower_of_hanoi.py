"""
tower_of_hanoi.py - Tower of Hanoi game logic, PIL rendering and QA builders
for the GameQA multimodal dataset.

Boards show arbitrary legal mid-game configurations of the classic 3-peg
Tower of Hanoi. All QA answers are computed exactly (simulation / BFS).
"""

import os
from collections import deque

from PIL import Image, ImageDraw, ImageFont, ImageFilter

PEGS = ["A", "B", "C"]

GAME_RULES = (
    "This is a Tower of Hanoi puzzle. The image shows three pegs labeled A, B and C from left to "
    "right, standing on a wooden base, with disks stacked on them. Each disk is drawn as a colored "
    "rounded bar labeled with its size number: disk 1 is the smallest disk and larger numbers mean "
    "larger disks (a wider bar is always a larger disk). The disks on a peg are stacked from bottom "
    "to top, and the top disk of a peg is the uppermost disk of its stack.\n"
    "Rules:\n"
    "1. Only one disk may be moved at a time, and only the top disk of a peg may be moved.\n"
    "2. A disk may be placed on an empty peg or on top of a larger disk; a larger disk may never be "
    "placed on top of a smaller disk.\n"
    'A move is written as "X → Y", meaning: move the top disk of peg X onto peg Y.'
)

# qa_type, qa_level per question_id (task template)
TASK_META = {
    1: ("Target Perception", "Easy"),
    2: ("State Prediction", "Medium"),
    3: ("State Prediction", "Hard"),
    4: ("Strategy Optimization", "Hard"),
}

# fixed size -> color mapping (1 = smallest)
DISK_COLORS = {
    1: (231, 76, 60),    # red
    2: (243, 156, 18),   # orange
    3: (241, 196, 15),   # yellow
    4: (39, 174, 96),    # green
    5: (52, 152, 219),   # blue
}

ALL_MOVES = [(s, d) for s in PEGS for d in PEGS if s != d]


# ---------------------------------------------------------------------------
# Game logic
# ---------------------------------------------------------------------------

def is_legal(pegs, src, dst):
    """A move src -> dst is legal if src is non-empty and dst is empty or
    topped by a larger disk."""
    return bool(pegs[src]) and (not pegs[dst] or pegs[src][-1] < pegs[dst][-1])


def legal_moves(pegs):
    return [(s, d) for s, d in ALL_MOVES if is_legal(pegs, s, d)]


def moved(pegs, src, dst):
    """Return a new pegs dict with the (assumed legal) move applied."""
    new = {p: list(pegs[p]) for p in PEGS}
    new[dst].append(new[src].pop())
    return new


def generate_board(num_disks, rng):
    """Start from the full tower on a random peg, apply 4-12 random legal
    moves, and reject boring states (all disks back on one peg)."""
    while True:
        start_peg = rng.choice(PEGS)
        pegs = {p: [] for p in PEGS}
        pegs[start_peg] = list(range(num_disks, 0, -1))
        scramble = []
        for _ in range(rng.randint(4, 12)):
            s, d = rng.choice(legal_moves(pegs))
            pegs[d].append(pegs[s].pop())
            scramble.append([s, d])
        # reject boring: every disk on a single peg (necessarily an ordered tower)
        if any(len(pegs[p]) == num_disks for p in PEGS):
            continue
        return {
            "num_disks": num_disks,
            "pegs": pegs,
            "target_peg": None,  # filled in by the task-4 builder
            "initial_peg": start_peg,
            "scramble_moves": scramble,
        }


# ---------------------------------------------------------------------------
# Exact solver: BFS shortest path to gather all disks on a target peg
# ---------------------------------------------------------------------------

def _encode(pegs):
    return tuple(tuple(pegs[p]) for p in PEGS)


def _expand(enc):
    for si in range(3):
        if not enc[si]:
            continue
        disk = enc[si][-1]
        for di in range(3):
            if di == si:
                continue
            if enc[di] and enc[di][-1] < disk:
                continue
            nxt = [list(p) for p in enc]
            nxt[di].append(nxt[si].pop())
            yield (si, di), tuple(tuple(p) for p in nxt)


def bfs_solve(pegs, target_idx):
    """Return (distance, move_path) of a shortest sequence that gathers all
    disks on peg target_idx. move_path is a list of (src_idx, dst_idx)."""
    num_disks = sum(len(pegs[p]) for p in PEGS)
    start = _encode(pegs)
    if len(start[target_idx]) == num_disks:
        return 0, []
    prev = {start: None}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for mv, nxt in _expand(cur):
            if nxt in prev:
                continue
            prev[nxt] = (cur, mv)
            if len(nxt[target_idx]) == num_disks:
                path = []
                node = nxt
                while prev[node] is not None:
                    node_prev, node_mv = prev[node]
                    path.append(node_mv)
                    node = node_prev
                path.reverse()
                return len(path), path
            queue.append(nxt)
    return None, None  # unreachable in a 3-peg Hanoi graph


# ---------------------------------------------------------------------------
# Rendering (PIL only, supersampled 2x then downscaled for crisp edges)
# ---------------------------------------------------------------------------

def _lerp(c0, c1, t):
    return tuple(int(round(c0[i] + (c1[i] - c0[i]) * t)) for i in range(3))


def _scale_color(c, f):
    return tuple(max(0, min(255, int(round(v * f)))) for v in c)


def _vgrad(w, h, c0, c1):
    g = Image.new("RGB", (w, h))
    gd = ImageDraw.Draw(g)
    for y in range(h):
        gd.line([(0, y), (w, y)], fill=_lerp(c0, c1, y / max(1, h - 1)))
    return g


class _Canvas:
    """ImageDraw wrapper that scales all coordinates by a supersample factor."""

    def __init__(self, img, ss):
        self.d = ImageDraw.Draw(img)
        self.ss = ss

    def _box(self, box):
        s = self.ss
        return [box[0] * s, box[1] * s, box[2] * s, box[3] * s]

    def rr(self, box, radius, **kw):
        if "width" in kw:
            kw["width"] = kw["width"] * self.ss
        self.d.rounded_rectangle(self._box(box), radius=radius * self.ss, **kw)

    def ellipse(self, box, **kw):
        if "width" in kw:
            kw["width"] = kw["width"] * self.ss
        self.d.ellipse(self._box(box), **kw)

    def line(self, pts, **kw):
        if "width" in kw:
            kw["width"] = kw["width"] * self.ss
        s = self.ss
        self.d.line([(x * s, y * s) for x, y in pts], **kw)

    def text(self, xy, txt, font, **kw):
        if "stroke_width" in kw:
            kw["stroke_width"] = kw["stroke_width"] * self.ss
        self.d.text((xy[0] * self.ss, xy[1] * self.ss), txt, font=font, **kw)


def _load_fonts(ss):
    font_dir = "/usr/share/fonts/truetype/dejavu"

    def f(name, size):
        try:
            return ImageFont.truetype(os.path.join(font_dir, name), size * ss)
        except Exception:
            return ImageFont.load_default()

    return {
        "title": f("DejaVuSans-Bold.ttf", 34),
        "subtitle": f("DejaVuSans.ttf", 16),
        "label": f("DejaVuSans-Bold.ttf", 24),
        "legend": f("DejaVuSans.ttf", 15),
        "disk": f("DejaVuSans-Bold.ttf", 19),
    }


def _disk_width(size, num_disks):
    w_min, w_max = 72.0, 182.0
    if num_disks <= 1:
        return (w_min + w_max) / 2
    return w_min + (size - 1) * (w_max - w_min) / (num_disks - 1)


def _draw_disk(cv, cx, y_top, w, h, size, font):
    color = DISK_COLORS[size]
    dark = _scale_color(color, 0.50)
    shade = _scale_color(color, 0.70)
    light = _scale_color(color, 1.25)
    x0, x1 = cx - w / 2, cx + w / 2
    r = min(15.0, h / 2 - 1)
    cv.rr([x0, y_top, x1, y_top + h], r, fill=shade)            # darker depth body
    cv.rr([x0, y_top, x1, y_top + h - 8], r, fill=color)        # main face
    cv.rr([x0 + 7, y_top + 3, x1 - 7, y_top + 6], 2, fill=light)  # top highlight
    cv.rr([x0, y_top, x1, y_top + h], r, outline=dark, width=2)  # outline
    lum = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
    text_col = (255, 255, 255) if lum < 150 else (70, 42, 14)
    stroke_col = _scale_color(color, 0.45) if lum < 150 else _scale_color(color, 1.4)
    cv.text((cx, y_top + (h - 8) / 2 + 1), str(size), font, fill=text_col,
            anchor="mm", stroke_width=1, stroke_fill=stroke_col)


def render_board(state, path):
    """Render the board to a 600x580 PNG."""
    pegs = state["pegs"]
    n = state["num_disks"]
    W, H = 600, 580
    SS = 2
    img = Image.new("RGB", (W * SS, H * SS))
    bg = ImageDraw.Draw(img)
    c_top, c_bot = (251, 243, 224), (233, 214, 178)  # warm parchment gradient
    for y in range(H * SS):
        bg.line([(0, y), (W * SS, y)], fill=_lerp(c_top, c_bot, y / (H * SS - 1)))

    fonts = _load_fonts(SS)
    base = (44, 468, 556, 498)
    peg_xs = {"A": 108, "B": 300, "C": 492}
    disk_h = 34
    peg_top = base[1] - (n * disk_h + 52)

    # soft shadow under the base
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [(base[0] + 4) * SS, (base[1] + 7) * SS, (base[2] + 4) * SS, (base[3] + 9) * SS],
        radius=13 * SS, fill=(70, 45, 20, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(4 * SS))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    cv = _Canvas(img, SS)

    # wooden pegs (drawn before the base so the base covers their bottoms)
    for p in PEGS:
        x = peg_xs[p]
        cv.rr([x - 8, peg_top + 4, x + 8, base[1] + 14], 8, fill=(146, 100, 58))
        cv.rr([x - 8, peg_top + 4, x - 3, base[1] + 14], 3, fill=(186, 138, 88))  # highlight
        cv.rr([x + 4, peg_top + 4, x + 8, base[1] + 14], 3, fill=(118, 78, 42))   # shade
        cv.ellipse([x - 9, peg_top - 6, x + 9, peg_top + 12], fill=(160, 111, 66),
                   outline=(108, 70, 38), width=1)                                 # knob
        cv.ellipse([x - 5, peg_top - 3, x - 1, peg_top + 4], fill=(198, 150, 98))  # knob shine

    # wooden base bar (vertical gradient clipped to a rounded rect)
    grad = _vgrad((base[2] - base[0]) * SS, (base[3] - base[1]) * SS,
                  (163, 112, 66), (117, 79, 43))
    mask = Image.new("L", grad.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, grad.width - 1, grad.height - 1], radius=13 * SS, fill=255)
    img.paste(grad, (base[0] * SS, base[1] * SS), mask)
    cv = _Canvas(img, SS)
    cv.rr(base, 13, outline=(88, 56, 28), width=2)
    cv.line([(base[0] + 14, base[1] + 2), (base[2] - 14, base[1] + 2)],
            fill=(198, 152, 100), width=2)  # top edge highlight
    for gy, gc in [(474, (98, 64, 34)), (480, (136, 96, 56)),
                   (488, (98, 64, 34)), (493, (136, 96, 56))]:
        cv.line([(base[0] + 18, gy), (base[2] - 18, gy)], fill=gc, width=1)  # wood grain

    # disks (bottom to top), with a contact shadow on the base under each stack
    for p in PEGS:
        stack = pegs[p]
        if not stack:
            continue
        x = peg_xs[p]
        w_bottom = _disk_width(stack[0], n)
        cv.ellipse([x - w_bottom / 2 - 4, base[1] - 4, x + w_bottom / 2 + 4, base[1] + 5],
                   fill=(96, 62, 34))
        for level, size in enumerate(stack):
            y_top = base[1] - (level + 1) * disk_h
            _draw_disk(cv, x, y_top, _disk_width(size, n), disk_h, size, fonts["disk"])

    # text: title, subtitle, peg labels, legend
    cv.text((W / 2, 36), "Tower of Hanoi", fonts["title"], fill=(88, 54, 24), anchor="mm")
    cv.text((W / 2, 67), f"{n} disks", fonts["subtitle"], fill=(134, 102, 70), anchor="mm")
    for p in PEGS:
        cv.text((peg_xs[p], 524), p, fonts["label"], fill=(80, 50, 24), anchor="mm")
    cv.text((W / 2, 561),
            "Move one top disk at a time; never place a larger disk on a smaller one.",
            fonts["legend"], fill=(120, 92, 62), anchor="mm")

    img = img.resize((W, H), Image.LANCZOS)
    img.save(path)


# ---------------------------------------------------------------------------
# QA builders. Each returns (body, analysis, options, answer_index, description)
# or None when the instance constraints cannot be satisfied.
# ---------------------------------------------------------------------------

def _fmt_stack(stack):
    return "[" + ", ".join(map(str, stack)) + "]" if stack else "[] (empty)"


def _state_str(pegs):
    return (f"peg A: {_fmt_stack(pegs['A'])}, peg B: {_fmt_stack(pegs['B'])}, "
            f"peg C: {_fmt_stack(pegs['C'])}")


def _tops_str(pegs):
    parts = []
    for p in PEGS:
        parts.append(f"{p} → {pegs[p][-1]}" if pegs[p] else f"{p} → (empty)")
    return ", ".join(parts)


def _finalize(body, analysis_core, correct, distractors, rng, desc):
    opts = list(dict.fromkeys(distractors))  # dedupe, keep order
    if correct in opts:
        return None
    opts.append(correct)
    rng.shuffle(opts)
    ans = opts.index(correct) + 1
    analysis = analysis_core + f"\n\nSo the answer is {correct}. The option number is {ans}."
    return body, analysis, opts, ans, desc


def build_q1(state, rng, variant):
    """Task 1 (Target Perception / Easy): count / top disk / largest disk / list."""
    pegs = state["pegs"]
    n = state["num_disks"]
    if variant == "count":
        x = rng.choice(PEGS)
        k = len(pegs[x])
        body = f"How many disks are on peg {x}?"
        correct = str(k)
        distractors = [str(i) for i in range(n + 1) if i != k]
        core = (f"Peg {x} holds (from bottom to top): {_fmt_stack(pegs[x])}. "
                f"That is {k} disk(s).")
        desc = "Count the disks on a given peg"
    elif variant == "top":
        x = rng.choice(PEGS)
        if pegs[x]:
            t = pegs[x][-1]
            correct = str(t)
            core = (f"Peg {x} holds (from bottom to top): {_fmt_stack(pegs[x])}. "
                    f"The uppermost disk is disk {t}, so the top disk has size {t}.")
        else:
            correct = "The peg is empty"
            core = f"Peg {x} holds no disks at all — it is empty."
        distractors = [str(s) for s in range(1, n + 1) if str(s) != correct]
        if correct != "The peg is empty":
            distractors.append("The peg is empty")
        body = f"What is the size of the top disk on peg {x}?"
        desc = "Identify the top disk on a given peg"
    elif variant == "largest":
        holder = next(p for p in PEGS if n in pegs[p])
        correct = f"Peg {holder}"
        distractors = [f"Peg {p}" for p in PEGS if p != holder] + ["None of the pegs"]
        core = (f"The largest disk is disk {n}. In the image it sits on peg {holder} "
                f"(peg {holder} holds {_fmt_stack(pegs[holder])}), while the other pegs hold "
                f"only smaller disks. Disk {n} is on exactly one peg.")
        body = f"Which peg holds the largest disk (disk {n})?"
        desc = "Find which peg holds the largest disk"
    else:  # "list"
        x = rng.choice([p for p in PEGS if pegs[p]])
        correct_list = list(pegs[x])
        correct = ", ".join(map(str, correct_list))
        all_disks = list(range(1, n + 1))
        pool, tries = [], 0
        while len(pool) < 7 and tries < 400:
            tries += 1
            r = rng.random()
            if len(correct_list) > 1 and r < 0.30:
                cand = correct_list[::-1]
            elif r < 0.60:
                k = rng.randint(1, min(n, len(correct_list) + 1))
                cand = rng.sample(all_disks, k)
            else:
                cand = list(correct_list)
                if len(cand) > 1 and rng.random() < 0.5:
                    i, j = rng.sample(range(len(cand)), 2)
                    cand[i], cand[j] = cand[j], cand[i]
                else:
                    repl = [dsk for dsk in all_disks if dsk not in cand]
                    if not repl:
                        continue
                    cand[rng.randrange(len(cand))] = rng.choice(repl)
            s = ", ".join(map(str, cand))
            if s != correct and s not in pool:
                pool.append(s)
        if len(pool) < 7:
            return None
        body = f"List the disks on peg {x} from bottom to top."
        core = (f"Reading peg {x} from the base upward, the disks are: {correct}. "
                f"(Bottom-to-top order, exactly as stacked on the peg.)")
        desc = "List the disks on a given peg from bottom to top"
    return _finalize(body, core, correct, distractors if variant != "list" else pool,
                     rng, desc)


def build_q2(state, rng, variant):
    """Task 2 (State Prediction / Medium): apply a 3-5 move sequence; up to one
    illegal move (skipped) in ~30% of instances."""
    pegs = {p: list(state["pegs"][p]) for p in PEGS}
    n = state["num_disks"]
    num_moves = rng.randint(3, 5)
    illegal_at = rng.randrange(num_moves) if rng.random() < 0.30 else -1
    seq, lines = [], []
    for i in range(num_moves):
        if i == illegal_at:
            cands = [(s, d) for s, d in ALL_MOVES if not is_legal(pegs, s, d)]
            s, d = rng.choice(cands)
            if not pegs[s]:
                reason = f"peg {s} is empty, so it has no top disk to move"
            else:
                reason = f"disk {pegs[s][-1]} cannot be placed on top of disk {pegs[d][-1]}"
            lines.append(f"Move {i + 1} - {s} → {d}: Illegal — {reason}. The board is unchanged.")
        else:
            s, d = rng.choice(legal_moves(pegs))
            disk = pegs[s][-1]
            onto = pegs[d][-1] if pegs[d] else None
            pegs[d].append(pegs[s].pop())
            landing = (f"onto peg {d}, landing on top of disk {onto}" if onto
                       else f"onto the empty peg {d}")
            lines.append(f"Move {i + 1} - {s} → {d}: Legal. Disk {disk} moves from peg {s} "
                         f"{landing}. Peg tops now: {_tops_str(pegs)}.")
        seq.append((s, d))
    z = rng.choice(PEGS)
    moves_str = ", ".join(f"{s} → {d}" for s, d in seq)
    intro = (f"The following moves are made in order: {moves_str}. If a move is illegal, "
             f"it is skipped and the board remains unchanged for that step. ")
    core_head = f"Initial state (bottom to top): {_state_str(state['pegs'])}.\n" + "\n".join(lines)
    if variant == "count":
        k = len(pegs[z])
        correct = str(k)
        distractors = [str(i) for i in range(n + 1) if i != k]
        body = intro + f"After the full sequence, how many disks will be on peg {z}?"
        core = (core_head + f"\nAfter the full sequence, peg {z} holds {_fmt_stack(pegs[z])} "
                f"— {k} disk(s).")
        desc = "Apply a move sequence and count the disks on a peg"
    else:
        if pegs[z]:
            t = pegs[z][-1]
            correct = str(t)
            tail = (f"After the full sequence, peg {z} holds {_fmt_stack(pegs[z])}, "
                    f"so its top disk is disk {t}.")
        else:
            correct = "The peg is empty"
            tail = f"After the full sequence, peg {z} holds no disks — it is empty."
        distractors = [str(s) for s in range(1, n + 1) if str(s) != correct]
        if correct != "The peg is empty":
            distractors.append("The peg is empty")
        body = intro + f"After the full sequence, what will be the size of the top disk on peg {z}?"
        core = core_head + "\n" + tail
        desc = "Apply a move sequence and identify the top disk on a peg"
    return _finalize(body, core, correct, distractors, rng, desc)


def build_q3(state, rng):
    """Task 3 (State Prediction / Hard): inverse — which single legal move
    produced a described outcome. Kept only when exactly one move matches."""
    pegs = state["pegs"]
    cands = []
    for s, d in ALL_MOVES:
        if not is_legal(pegs, s, d):
            continue
        after = moved(pegs, s, d)
        for z in PEGS:
            if not after[z]:
                continue
            k, top = len(after[z]), after[z][-1]
            matches = 0
            for s2, d2 in ALL_MOVES:
                if not is_legal(pegs, s2, d2):
                    continue
                a2 = moved(pegs, s2, d2)
                if len(a2[z]) == k and a2[z] and a2[z][-1] == top:
                    matches += 1
            if matches == 1:
                cands.append((s, d, z, k, top))
    if not cands:
        return None
    s, d, z, k, top = rng.choice(cands)
    body = (f"Exactly ONE legal move was made starting from the state shown in the image. "
            f"After this move, peg {z} has {k} disk(s) with disk {top} on top. "
            f"Which move was made?")
    correct = f"{s} → {d}"
    distractors = [f"{a} → {b}" for a, b in ALL_MOVES if (a, b) != (s, d)]
    lines = [f"Target outcome: peg {z} must have {k} disk(s) with disk {top} on top.",
             f"Shown state (bottom to top): {_state_str(pegs)}.",
             "Checking every candidate move:"]
    for a, b in ALL_MOVES:
        if not is_legal(pegs, a, b):
            reason = (f"peg {a} is empty" if not pegs[a]
                      else f"disk {pegs[a][-1]} cannot be placed on top of disk {pegs[b][-1]}")
            lines.append(f"- {a} → {b}: illegal ({reason}), so it cannot be the move that was made.")
        else:
            a2 = moved(pegs, a, b)
            kk = len(a2[z])
            tt = a2[z][-1] if a2[z] else None
            if kk == k and tt == top:
                verdict = (f"peg {z} becomes {_fmt_stack(a2[z])} — {kk} disk(s) with disk {tt} "
                           f"on top. This matches the outcome.")
            else:
                top_part = f" with disk {tt} on top" if tt is not None else " (empty)"
                verdict = (f"peg {z} would have {kk} disk(s){top_part} — does not match.")
            lines.append(f"- {a} → {b}: legal; {verdict}")
    lines.append(f"Only {s} → {d} produces the described outcome.")
    return _finalize(body, "\n".join(lines), correct, distractors, rng,
                     "Infer which single legal move produced a described outcome")


def build_q4(state, rng, variant):
    """Task 4 (Strategy Optimization / Hard): exact BFS minimum moves to gather
    all disks on a target peg, or the unique optimal first move.
    Returns (qa_tuple, target_peg) or (None, None)."""
    pegs = state["pegs"]
    n = state["num_disks"]
    order = PEGS[:]
    rng.shuffle(order)
    for t in order:
        ti = PEGS.index(t)
        dist, path = bfs_solve(pegs, ti)
        if dist is None or dist < 2:
            continue
        if variant == "first":
            info = []
            for a, b in ALL_MOVES:
                if not is_legal(pegs, a, b):
                    info.append(((a, b), None))
                else:
                    d2, _ = bfs_solve(moved(pegs, a, b), ti)
                    info.append(((a, b), d2))
            best = [m for m, dd in info if dd == dist - 1]
            if len(best) != 1:
                continue  # need a strictly unique optimal first move
            fm = best[0]
            correct = f"{fm[0]} → {fm[1]}"
            distractors = [f"{a} → {b}" for a, b in ALL_MOVES if (a, b) != fm]
            lines = [
                f"Gathering all {n} disks on peg {t} takes a minimum of {dist} moves "
                f"(found by breadth-first search over all reachable states).",
                "Checking every possible first move (the number is the minimum moves still "
                "needed afterwards):"]
            for (a, b), dd in info:
                if dd is None:
                    reason = (f"peg {a} is empty" if not pegs[a]
                              else f"disk {pegs[a][-1]} cannot be placed on top of disk "
                              f"{pegs[b][-1]}")
                    lines.append(f"- {a} → {b}: illegal move ({reason}) — cannot be played.")
                elif dd == dist - 1:
                    lines.append(f"- {a} → {b}: {dd} more move(s), {dd + 1} in total — optimal.")
                else:
                    lines.append(f"- {a} → {b}: {dd} more move(s), {dd + 1} in total — not optimal.")
            lines.append(f"Only {correct} keeps a shortest ({dist}-move) solution open.")
            body = (f"Starting from the state shown in the image, you want to gather all {n} "
                    f"disks onto peg {t} (a single legal tower) in as few moves as possible. "
                    f"Which FIRST move belongs to a shortest solution?")
            desc = "Choose the optimal first move to gather all disks on the target peg"
        else:
            correct = str(dist)
            pool, delta = [], 1
            while len(pool) < 7:
                for v in (dist - delta, dist + delta):
                    if v >= 1 and v != dist and str(v) not in pool:
                        pool.append(str(v))
                delta += 1
            distractors = pool[:7]
            path_lines = [f"{i + 1}. {PEGS[mv[0]]} → {PEGS[mv[1]]}" for i, mv in enumerate(path)]
            lines = [
                f"A breadth-first search over all reachable configurations of the {n} disks "
                f"finds a shortest solution of {dist} moves. One optimal solution is:",
                *path_lines,
                f"After these {dist} moves, all {n} disks form a single legal tower on peg {t}. "
                f"Because BFS explores states in increasing order of move count, no solution "
                f"with fewer than {dist} moves exists."]
            body = (f"What is the minimum number of moves needed to get all {n} disks onto "
                    f"peg {t} (a single legal tower), starting from the state shown in the image?")
            desc = "Find the minimum number of moves to gather all disks on the target peg"
        qa = _finalize(body, "\n".join(lines), correct, distractors, rng, desc)
        if qa is None:
            continue
        return qa, t
    return None, None
