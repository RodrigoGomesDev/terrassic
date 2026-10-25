"""Leaves of the mod's nine trees, in the style Rodrigo approved on 2026-10-25 (study in progressao/estudo/).

Each canopy is a scatter of small readable leaf clumps on the 16x16 torus, so clumps cross the block edge and no seam
shows. Every clump is lit from the top-left (light, middle, shadow by its diagonal), lower clumps overlap upper ones,
the deep shadow of the canopy fills the gaps, and a few compact 1-4 px holes sit where clumps leave the most room
(never thin lines). Four tones per species at a calm saturation (0.38 to 0.46), no direction in the pattern
(coherence under 0.05). Transparent pixels keep a dark leaf colour, which "fast" graphics shows instead of holes.

    python3 folhas.py        # writes previews of the nine to /tmp/folhas-*.png

blocos.leaves_img(tid) returns leaf(tid)."""
import colorsys

import numpy as np
from PIL import Image

N = 16

SHAPES = {
    "oval": [".##.", "####", "####", ".##."],
    "round": [".###.", "#####", "#####", "#####", ".###."],
    "small": [".#.", "###", ".##"],
    "drop": ["##.", "###", ".##"],
}

# tid: hue, saturation, four values (shadow, dark, middle, light), clump shapes, clumps, spacing, holes, seed.
# The seeds were picked by the study's metrics (low coherence and single-wave share, holes near 12%).
SPECIES = {
    "metasequoia": (96, .42, (74, 106, 136, 164), ("small", "drop", "oval"), 16, 3.4, .12, 76),
    "taxodium": (100, .40, (70, 100, 130, 158), ("small", "drop"), 18, 3.2, .12, 118),
    "ginkgo": (78, .46, (86, 120, 150, 178), ("round", "oval"), 11, 4.2, .12, 67),
    "platanus": (92, .42, (78, 108, 138, 164), ("round", "oval"), 10, 4.6, .10, 64),
    "magnolia": (128, .40, (52, 76, 102, 130), ("round", "oval"), 10, 4.4, .10, 129),
    "podocarpus": (120, .40, (54, 78, 104, 130), ("small", "drop"), 17, 3.3, .12, 131),
    "araucaria": (140, .38, (50, 74, 100, 126), ("small", "drop"), 17, 3.3, .14, 61),
    "sabal": (88, .38, (76, 104, 132, 158), ("oval", "drop"), 13, 3.8, .12, 140),
    "tree_fern": (98, .44, (72, 104, 136, 166), ("drop", "small", "oval"), 15, 3.5, .12, 30),
}

# magnolia flowers: cream petals with a pink blush, three pixels each
FLOWER = ((240, 236, 230), (226, 220, 212), (204, 170, 180))


def ramp(h, s, values):
    return [tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(h / 360, s, v / 255)) for v in values]


def parse(rows):
    return np.array([[c == '#' for c in r] for r in rows], bool)


def shade(mask):
    """Tone 3 on the top-left of the clump, 1 on the bottom-right, 2 between."""
    h, w = mask.shape
    t = np.zeros((h, w), int)
    c = (w - 1) / 2 + (h - 1) / 2
    r = max(1.0, c * 0.55)
    for y in range(h):
        for x in range(w):
            if mask[y, x]:
                d = x + y - c
                t[y, x] = 3 if d <= -r else (1 if d >= r else 2)
    return t


def canopy(seed, shapes, n, min_d, holes):
    """Tone map (0 = deep shadow .. 3 = lit) and opacity of one seamless 16x16 canopy."""
    rng = np.random.default_rng(seed)
    tone = np.zeros((N, N), int)
    pts, tries = [], 0
    while len(pts) < n and tries < 4000:
        tries += 1
        p = rng.integers(0, N, 2)
        if all(min(abs(p[0] - q[0]), N - abs(p[0] - q[0])) ** 2 + min(abs(p[1] - q[1]), N - abs(p[1] - q[1])) ** 2
               >= min_d ** 2 for q in pts):
            pts.append(p)
    pts.sort(key=lambda p: p[1])
    for px, py in pts:
        m = parse(SHAPES[shapes[rng.integers(len(shapes))]])
        if rng.random() < .5:
            m = m[:, ::-1]
        t = shade(m)
        h, w = m.shape
        for y in range(h):
            for x in range(w):
                if m[y, x]:
                    tone[(py + y - h // 2) % N, (px + x - w // 2) % N] = t[y, x]
    # holes grow from the shadow pixels farthest from any clump, kept apart and compact
    bg = tone == 0
    dist = np.zeros((N, N))
    ys, xs = np.nonzero(~bg)
    for y in range(N):
        for x in range(N):
            if bg[y, x]:
                dy = np.minimum(abs(ys - y), N - abs(ys - y))
                dx = np.minimum(abs(xs - x), N - abs(xs - x))
                dist[y, x] = np.min(dx + dy)
    op = np.ones((N, N), bool)
    target = int(holes * N * N)
    d2 = dist + rng.uniform(0, .4, (N, N))
    seeds = sorted(((d2[y, x], x, y) for y in range(N) for x in range(N) if bg[y, x]), reverse=True)
    used = 0
    for _, x, y in seeds:
        if used >= target:
            break
        if not op[y, x] or any(not op[(y + j) % N, (x + i) % N] for i in (-1, 0, 1) for j in (-1, 0, 1)):
            continue
        size = int(rng.choice([1, 2, 2, 3, 4]))
        cells = [(x, y)]
        while len(cells) < size:
            cand = [((cx + i) % N, (cy + j) % N) for cx, cy in cells for i, j in ((1, 0), (0, 1), (-1, 0), (0, -1))
                    if bg[(cy + j) % N, (cx + i) % N] and ((cx + i) % N, (cy + j) % N) not in cells]
            cand.sort(key=lambda c: -sum(((c[0] + i) % N, (c[1] + j) % N) in cells
                                         for i, j in ((1, 0), (0, 1), (-1, 0), (0, -1))))
            cand = cand[:2]
            if not cand:
                break
            cells.append(cand[int(rng.integers(len(cand)))])
        for cx, cy in cells:
            op[cy, cx] = False
        used += len(cells)
    return tone, op


def flowers(a, seed, k=2):
    rng = np.random.default_rng(seed)
    for _ in range(k):
        x, y = rng.integers(0, N, 2)
        for (dx, dy), c in zip(((0, 0), (1, 0), (0, 1)), FLOWER):
            a[(y + dy) % N, (x + dx) % N] = (*c, 255)


def leaf(tid):
    h, s, values, shapes, n, min_d, holes, seed = SPECIES[tid]
    pal = ramp(h, s, values)
    tone, op = canopy(seed, shapes, n, min_d, holes)
    a = np.zeros((N, N, 4), np.uint8)
    for t in range(4):
        a[tone == t, :3] = pal[t]
    a[..., 3] = np.where(op, 255, 0)
    a[~op, :3] = (np.array(pal[0]) * .6).round()
    if tid == "magnolia":
        flowers(a, 11)
    return Image.fromarray(a, "RGBA")


ALL = {f"{tid}_leaves": leaf(tid) for tid in SPECIES}

if __name__ == "__main__":
    for name, im in ALL.items():
        big = Image.new("RGBA", (48, 48), (169, 196, 221, 255))
        for x in range(3):
            for y in range(3):
                big.alpha_composite(im, (16 * x, 16 * y))
        big.resize((288, 288), Image.NEAREST).save(f"/tmp/folhas-{name}.png")
