"""Late Cretaceous pack (the Overworld era): vanilla terrain redrawn as weathered, warm, primitive ground.

How every texture is drawn (engine v2, after Rodrigo found v1 "bem ruim"):
  1. a calm base of one main tone with a few large patches of the tones next to it;
  2. hand-designed details (ledges, specks, pebbles, blades, needles, roots) stamped where a blue-noise
     (Poisson-disc) pattern says, so they look placed by hand: evenly spread, never clumped, never in a grid;
  3. the palette is fitted (fit.py) so the luma mean and contrast match the vanilla block it replaces
     (targets.py), with our own hue: a faint warm cast on stone, red-brown laterite earth, golden sand.
"""
import numpy as np
from PIL import Image

import tex as T
from fit import fit
from stamps import base, poisson, stamp
from targets import TARGETS
from tex import N


def tgt(name, dl=0.0, dc=0.0):
    """(luma mean, contrast) of the vanilla block `name`, nudged by dl/dc for the era's look."""
    lum, ctr, _, _ = TARGETS[name]
    return lum + dl, ctr + dc

def paint(t, pal):
    return T.colorize(t, pal)

# ---------------------------------------------------------------- stone family
def stone_tones(seed):
    t = base(seed, 2, 1, 3, .18, .14, layers=((2, 4, .5), (4, 8, .3), (8, 16, .2)))
    r = T.rng(seed + 1)
    for (x, y) in poisson(seed + 2, 8, 4.4):
        L = int(r.integers(2, 6))
        bot = ('.' + 'D' * (L - 1)) if r.random() < .5 else 'D' * (L - 1)
        stamp(t, x, y, ['L' * L, bot], {'L': 3, 'D': 0 if r.random() < .5 else 1})
    for (x, y) in poisson(seed + 3, 5, 3.0):
        stamp(t, x, y, ['L.', '.D'], {'L': 3, 'D': 1})
    return t

def stone_palette(t):
    m, c = tgt('stone', -4, 2)
    return fit(t, 4, m, c, hue=0.08, sat=0.045, hue_shift=0.02, sat_shift=0.01)

def stone(seed=4):
    t = stone_tones(seed); return paint(t, stone_palette(t))

def stone_fossil(seed=4, at=(5, 9)):
    t = stone_tones(seed)
    pal = stone_palette(t)
    m = ["..###.", ".#...#", "#.##.#", "#.#..#", "#..##.", ".##..."]
    y0, x0 = at
    for y in range(6):
        for x in range(6):
            yy, xx = y0 + y, x0 + x
            if m[y][x] == '#':
                t[yy, xx] = 3
                if y + 1 < 6 and x + 1 < 6 and m[y + 1][x + 1] != '#':
                    t[yy + 1, xx + 1] = 0
            elif 1 <= y <= 4 and 1 <= x <= 4 and t[yy, xx] != 0:
                t[yy, xx] = 1
    return paint(t, pal)

# ---------------------------------------------------------------- earth family
DARK = [['D'], ['DD'], ['D.', '.D'], ['DD', 'D.'], ['.D', 'DD'], ['D', 'D'], ['DD']]
LIGHT = [['L'], ['LL'], ['L.', '.L'], ['L', 'L']]
PEBBLE = [(122, 116, 108), (142, 135, 126)]

def dirt_tones(seed, dark=22, light=15):
    t = base(seed, 2, 1, 3, .16, .14, layers=((4, 4, .6), (8, 8, .4)))
    r = T.rng(seed + 1)
    for (x, y) in poisson(seed + 2, dark, 2.6):
        stamp(t, x, y, DARK[int(r.integers(len(DARK)))], {'D': 0 if r.random() < .5 else 1})
    for (x, y) in poisson(seed + 3, light, 2.8):
        stamp(t, x, y, LIGHT[int(r.integers(len(LIGHT)))], {'L': 4 if r.random() < .55 else 3})
    return t

def dirt_palette(t, name='dirt', dl=-3, dc=0):
    m, c = tgt(name, dl, dc)
    return fit(np.minimum(t, 4), 5, m, c, hue=0.075, sat=0.47, hue_shift=0.015, sat_shift=0.05)

def add_pebbles(t, seed, n, first):
    r = T.rng(seed)
    for (x, y) in poisson(seed + 1, n, 6):
        w = int(r.integers(1, 3))
        stamp(t, x, y, ['Q' + 'P' * (w - 1), 'd' * w], {'Q': first + 1, 'P': first, 'd': 0})
    return t

def dirt(seed=1, pebbles=2):
    t = dirt_tones(seed)
    pal = dirt_palette(t)
    t = add_pebbles(t, seed + 9, pebbles, 5)
    return paint(t, pal + PEBBLE)

def rooted_dirt(seed=5):
    t = dirt_tones(seed, dark=16, light=10)
    pal = dirt_palette(t, 'rooted_dirt', -3)
    root = [(150, 112, 84), (176, 136, 104)]
    r = T.rng(seed + 1)
    for _ in range(3):
        x, y = float(r.integers(N)), float(r.integers(N)); ang = r.uniform(.8, 2.3)
        for k in range(int(r.integers(6, 11))):
            yi, xi = int(round(y)) % N, int(round(x)) % N
            t[yi, xi] = 6 if k % 3 == 0 else 5
            if t[(yi + 1) % N, xi] < 5: t[(yi + 1) % N, xi] = 0
            ang = min(max(ang + r.normal(0, .5), .3), 2.8); x += np.cos(ang); y += np.sin(ang) * .8
    return paint(t, pal + root)

def coarse_dirt(seed=7):
    t = dirt_tones(seed)
    pal = dirt_palette(t, 'coarse_dirt', 0, -6)
    grav = [(84, 78, 72), (112, 105, 97), (138, 130, 120)]
    r = T.rng(seed + 2)
    for (x, y) in poisson(seed + 3, 9, 3.6):
        shp = [['GH', 'gG'], ['HG', 'Gg'], ['H', 'g'], ['GH', 'g.']][int(r.integers(4))]
        stamp(t, x, y, shp, {'G': 6, 'H': 7, 'g': 5})
    return paint(t, pal + grav)

# ---------------------------------------------------------------- cobble
def bevel_cells(seed, nx, ny, sx=1.0, jitter=.8, warp_amp=1.3, rmin=None):
    pts = T.jittered_points(seed, nx, ny, jitter) if rmin is None else [
        (x + .5, y + .5) for (x, y) in poisson(seed + 11, nx * ny, rmin)]
    idx, _, _ = T.voronoi(pts, sx=sx, sy=1.0, warp=T.fbm(seed + 1, [(4, 4, .6), (8, 8, .4)]), warp_amp=warp_amp)
    gap = T.cell_edges(idx)
    hi = (T.roll(gap, -1, 0) | T.roll(gap, 0, -1)) & ~gap
    lo = (T.roll(gap, 1, 0) | T.roll(gap, 0, 1)) & ~gap & ~hi
    return pts, idx, gap, hi, lo

def cobble_tones(seed):
    pts, idx, gap, hi, lo = bevel_cells(seed, 4, 3, sx=.9, rmin=4.6, warp_amp=1.8)
    r = T.rng(seed + 2)
    body = r.choice([2, 2, 3, 3, 3, 4], len(pts))[idx]
    t = body.copy(); t[hi] = np.minimum(body[hi] + 2, 5); t[lo] = np.maximum(body[lo] - 1, 1); t[gap] = 0
    inner = ~gap & ~hi & ~lo
    for (x, y) in poisson(seed + 3, 8, 3.2):
        if inner[y, x]:
            t[y, x] = max(1, t[y, x] - 1)
    return t, gap

def cobblestone(seed=1):
    t, _ = cobble_tones(seed)
    m, c = tgt('cobblestone', -4)
    return paint(t, fit(t, 6, m, c, hue=0.08, sat=0.035, hue_shift=0.02))

def mossy_cobblestone(seed=1):
    t, gap = cobble_tones(seed)
    m, c = tgt('cobblestone', -4)
    pal = fit(t, 6, m, c, hue=0.08, sat=0.035, hue_shift=0.02)
    moss = [(70, 88, 50), (86, 108, 58), (102, 126, 66), (121, 146, 77)]
    n = T.fbm(seed + 7, [(4, 4, .5), (8, 8, .5)])
    near = T.distance_to(gap)
    mm = n > .64
    mv = T.quantize(T.fbm(seed + 8, [(16, 16, 1)]), [.2, .35, .3, .15])
    mv = np.where(gap, 0, mv)
    hi = T.roll(~mm, 1, 0) & mm  # top edge of moss clumps catches light
    mv = np.where(hi & ~gap, np.minimum(mv + 1, 3), mv)
    t = np.where(mm, 6 + mv, t)
    return paint(t, pal + moss)

# ---------------------------------------------------------------- sand, gravel
def sand_tones(seed):
    """Fine grain: almost every pixel differs a little from its neighbours (vanilla sand: nb 11, contrast 21)."""
    v = 0.75 * T.fbm(seed, [(16, 16, 1.0)]) + 0.25 * T.fbm(seed + 1, [(4, 8, 1.0)])
    t = T.quantize(v, [.08, .22, .36, .24, .10])
    return t


def sand(seed=1):
    t = sand_tones(seed); m, c = tgt('sand', -4)
    return paint(t, fit(t, 5, m, c, hue=0.115, sat=0.27, hue_shift=0.012, sat_shift=0.04))

def gravel(seed=1):
    pts, idx, gap, hi, lo = bevel_cells(seed, 5, 5, sx=.9, warp_amp=1.2, rmin=2.9)
    r = T.rng(seed + 2)
    fam = r.choice(2, len(pts), p=[.6, .4])
    body = r.choice([1, 2, 2, 3], len(pts))[idx]
    t = np.where(hi, np.minimum(body + 1, 4), np.where(lo, np.maximum(body - 1, 1), body))
    m, c = tgt('gravel', -3)
    pa = fit(np.where(gap, 0, t), 5, m + 4, c, hue=0.07, sat=0.035, hue_shift=0.01)
    pb = fit(np.where(gap, 0, t), 5, m - 6, c, hue=0.03, sat=0.10, hue_shift=0.01)
    t = np.where(gap, 0, t + fam[idx] * 5)
    return paint(t, pa + pb)


# ---------------------------------------------------------------- grass
def grass_tones(seed):
    t = base(seed, 2, 1, 3, .22, .22, layers=((4, 4, .4), (8, 8, .6)))
    for (x, y) in poisson(seed + 2, 46, 1.8):
        stamp(t, x, y, ['L', 'D'], {'L': 4 if (x * 7 + y) % 3 else 3, 'D': 0 if (x + y) % 2 else 1})
    return t

def grass_top(seed=1):
    t = grass_tones(seed); m, c = tgt('grass_block_top')
    return paint(t, fit(t, 5, m, c, hue=0, sat=0))

def fringe(seed):
    r = T.rng(seed); depth = np.zeros(N, int); d = 3
    for x in range(N):
        d = int(np.clip(d + r.choice([-1, 0, 0, 1]), 2, 4)); depth[x] = d
    for x in r.choice(N, 3, replace=False):
        depth[x] = min(depth[x] + 2, 6)
    mask = np.zeros((N, N), bool)
    for x in range(N): mask[:depth[x], x] = True
    return mask, depth

def grass_side(seed=3, dirt_seed=1):
    mask, depth = fringe(seed)
    g = grass_tones(seed + 5)
    m, c = tgt('grass_block_side_overlay')
    gp = fit(g, 5, m, c, hue=0, sat=0)
    ov = np.asarray(paint(g, gp)).copy(); ov[..., 3] = np.where(mask, 255, 0)
    # lighter top row, darker hanging tips
    for x in range(N):
        ov[0, x, :3] = gp[min(4, g[0, x] + 1)]
        ov[depth[x] - 1, x, :3] = gp[max(0, g[depth[x] - 1, x] - 1)]
    t = dirt_tones(dirt_seed); pal = dirt_palette(t)
    t = add_pebbles(t, dirt_seed + 9, 2, 5)
    for x in range(N):
        if depth[x] < N: t[depth[x], x] = 0
    side = np.asarray(paint(t, pal + PEBBLE)).copy()
    olive = np.array([110, 142, 66], float)
    side[mask, :3] = (ov[mask, :3] / 255.0 * olive).round()
    return Image.fromarray(side, "RGBA"), Image.fromarray(ov, "RGBA")

def snow_side(seed=5, dirt_seed=1):
    """Snow lies thicker than turf: the fringe hangs 2 px lower."""
    mask, depth = fringe(seed)
    depth = np.minimum(depth + 2, 8)
    mask = np.arange(N)[:, None] < depth[None, :]
    t = dirt_tones(dirt_seed); pal = dirt_palette(t)
    t = add_pebbles(t, dirt_seed + 9, 2, 5)
    for x in range(N):
        if depth[x] < N: t[depth[x], x] = 0
    img = np.asarray(paint(t, pal + PEBBLE)).copy()
    snow = [(214, 230, 236), (232, 243, 246), (246, 252, 252), (255, 255, 255)]
    s = T.quantize(T.fbm(seed + 2, [(8, 8, .5), (16, 16, .5)]), [.15, .3, .35, .2])
    for x in range(N):
        s[depth[x] - 1, x] = 0
        s[0, x] = 3
    img[mask, :3] = np.array(snow)[s][mask]
    return Image.fromarray(img, "RGBA")

def podzol_tones(seed):
    """Needle and frond litter: short strokes in every direction over dark humus, each with a shadow."""
    t = base(seed, 1, 0, 2, .25, .2, layers=((8, 8, .5), (16, 16, .5)))
    r = T.rng(seed + 1)
    dirs = [(1, 1), (1, -1), (1, 0), (0, 1), (-1, 1), (2, 1)]
    for (x, y) in poisson(seed + 2, 14, 2.9):
        dx, dy = dirs[int(r.integers(len(dirs)))]
        tone = int(r.choice([3, 3, 4]))
        ln = int(r.integers(2, 4))
        for k in range(ln):
            xx, yy = (x + k * dx) % N, (y + k * (dy if abs(dx) < 2 else 1) // max(1, abs(dx) // 1)) % N
            t[yy, xx] = tone
            if t[(yy + 1) % N, xx] < 3: t[(yy + 1) % N, xx] = 0
    return t


def podzol_top(seed=1):
    t = podzol_tones(seed); m, c = tgt('podzol_top', 4)
    return paint(t, fit(t, 5, m, c, hue=0.08, sat=0.68, hue_shift=0.02))

def podzol_side(seed=3, dirt_seed=1):
    mask, depth = fringe(seed)
    t = dirt_tones(dirt_seed); pal = dirt_palette(t); t = add_pebbles(t, dirt_seed + 9, 2, 5)
    for x in range(N):
        if depth[x] < N: t[depth[x], x] = 0
    img = np.asarray(paint(t, pal + PEBBLE)).copy()
    top = np.asarray(podzol_top(seed + 2)).copy(); img[mask] = top[mask]
    return Image.fromarray(img, "RGBA")

# ---------------------------------------------------------------- sandstone
SS_HUE, SS_SAT = 0.115, 0.29

def ss_pal(t, name, n=5, dl=-4, dc=0):
    m, c = tgt(name, dl, dc); return fit(t, n, m, c, hue=SS_HUE, sat=SS_SAT, hue_shift=0.012, sat_shift=0.04)

def sandstone_top(seed=1):
    v = 0.6 * T.fbm(seed, [(16, 16, 1.0)]) + 0.4 * T.fbm(seed + 1, [(4, 4, 1.0)])
    t = T.quantize(v, [.1, .3, .4, .2])
    return paint(t, ss_pal(t, 'sandstone_top', 4))

def sandstone_side(seed=1):
    r = T.rng(seed); rows = []
    while len(rows) < N:
        h = int(r.integers(2, 5)); rows += [int(r.choice([2, 2, 3, 1]))] * h
    t = np.array(rows[:N])[:, None].repeat(N, 1)
    # bedding seams: broken dark lines where layers meet, and eroded pits
    for y in range(1, N):
        if rows[y] != rows[y - 1]:
            gate = T.fbm(seed + y, [(4, 1, 1)])[0] > .3
            t[y - 1, gate] = 0
    g = T.fbm(seed + 3, [(8, 16, .6), (16, 16, .4)])
    t = np.where((g > .72) & (t > 0) & (t < 4), t + 1, t)
    t = np.where((g < .2) & (t > 1), t - 1, t)
    t[0, :] = 4; t[1, :] = np.maximum(t[1, :], 3); t[N - 1, :] = np.minimum(t[N - 1, :], 1)
    return paint(t, ss_pal(t, 'sandstone'))

def sandstone_bottom(seed=2):
    t = base(seed, 2, 1, 3, .2, .2, layers=((4, 4, .5), (8, 8, .5)))
    for (x, y) in poisson(seed + 2, 7, 3.6): stamp(t, x, y, ['D.', '.D'], {'D': 0})
    g = T.fbm(seed + 3, [(16, 16, 1.)])
    t = np.where((g > .75) & (t < 4) & (t > 0), t + 1, t)
    return paint(t, ss_pal(t, 'sandstone_bottom'))

def cut_sandstone(seed=1):
    t = base(seed, 2, 1, 3, .15, .15, layers=((8, 8, 1),))
    for top in (0, 8):
        t[top, :] = 4; t[top + 7, :] = 0; t[top + 1:top + 7, 0] = 3; t[top + 1:top + 7, N - 1] = 1
    return paint(t, ss_pal(t, 'cut_sandstone'))

def footprint():
    m = np.zeros((10, 12), bool)
    m[0:6, 5:7] = True
    for (y, x) in [(1, 1), (2, 1), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4), (5, 4), (1, 2)]:
        m[y, x] = True; m[y, 11 - x] = True
    m[5:8, 4:8] = True; m[8, 5:7] = True
    return m

def chiseled_sandstone(seed=1):
    t = base(seed, 2, 1, 3, .15, .15, layers=((8, 8, 1),))
    t[0, :] = 4; t[:, 0] = 4; t[N - 1, :] = 0; t[:, N - 1] = 0
    t[1, 1:N - 1] = 3; t[1:N - 1, 1] = 3; t[N - 2, 1:N - 1] = 1; t[1:N - 1, N - 2] = 1
    cut = np.zeros((N, N), bool); cut[3:13, 2:14] = footprint()
    t = np.where(cut, 1, t)
    t = np.where(cut & ~T.roll(cut, -1, -1), 0, t)
    t = np.where(T.roll(cut, -1, -1) & ~cut, 4, t)
    return paint(t, ss_pal(t, 'chiseled_sandstone'))

# ---------------------------------------------------------------- clay, mud
def clay(seed=1):
    t = base(seed, 2, 1, 3, .22, .2, layers=((4, 4, .6), (8, 8, .4)))
    for (x, y) in poisson(seed + 2, 7, 3.4): stamp(t, x, y, ['L.', '.D'], {'L': 4, 'D': 0})
    m, c = tgt('clay', -2)
    return paint(t, fit(t, 5, m, c, hue=0.6, sat=0.09, hue_shift=-0.01))

def mud(seed=1):
    t = base(seed, 2, 1, 3, .25, .15, layers=((4, 4, .6), (8, 8, .4)))
    for (x, y) in poisson(seed + 2, 5, 4.0): stamp(t, x, y, ['LL'], {'L': 4})
    m, c = tgt('mud', 2)
    return paint(t, fit(t, 5, m, c, hue=0.06, sat=0.13, hue_shift=0.02))
