"""TX2 (scratch): the eight vanilla woods redrawn for the Late Cretaceous pack.

Each wood has a bark of its own (not a recolour): oak with braided furrows and lichen, spruce with the scaly
plates of an araucaria and a drop of amber resin, birch with horizontal lenticels and peeling strips, jungle with
long buttress ridges and moss, acacia with fibres twisted round the trunk, dark oak in thick blocks, mangrove
smooth with growth rings, cherry dark with lenticels. Tops have off-centre rings (trees grow eccentric) and a
drying crack; planks are hand-split boards, each a shade of its own, held by wooden pegs."""
import math
import sys

import numpy as np
from PIL import Image

import tex as T  # noqa: E402
from fit import fit, colour_at  # noqa: E402
from stamps import poisson, stamp  # noqa: E402
from tex import N  # noqa: E402

from vanilla import VANILLA as TX2  # noqa: E402


def tgt(name, dl=-3.0, dc=0.0):
    r = TX2[name]
    return r[0] + dl, r[1] + dc


def paint(t, pal, alpha=None):
    return T.colorize(t, pal, alpha)


def wave(seed, x0, amp, amp2=0.0):
    """x(y) for y in 0..15, periodic on the torus (whole sine periods)."""
    r = T.rng(seed)
    p1, p2 = r.random() * 6.283, r.random() * 6.283
    ys = np.arange(N)
    return np.round(x0 + amp * np.sin(6.283 * ys / N + p1) + amp2 * np.sin(6.283 * 2 * ys / N + p2)).astype(int)


def draw_line(t, xs, tone, side=None, present=None):
    """Vertical wandering line through x = xs[y]; joins steps so it never breaks. side = (left_tone, right_tone)."""
    for y in range(N):
        if present is not None and not present[y]:
            continue
        x = xs[y]
        xn = xs[(y + 1) % N]
        span = range(min(x, xn), max(x, xn) + 1) if abs(xn - x) > 1 else [x]
        for xx in span:
            t[y, xx % N] = tone
        if side:
            lo, hi = side
            if lo is not None and t[y, (min(span) - 1) % N] != tone:
                t[y, (min(span) - 1) % N] = lo
            if hi is not None and t[y, (max(span) + 1) % N] != tone:
                t[y, (max(span) + 1) % N] = hi


# ------------------------------------------------------------------ bark
def streak_base(seed, main=3, lo=2, hi=4, lo_share=.3, hi_share=.15, layers=((8, 2, .6), (16, 4, .4))):
    f = T.fbm(seed, list(layers))
    t = np.full((N, N), main)
    t[f < np.quantile(f, lo_share)] = lo
    t[f > np.quantile(f, 1 - hi_share)] = hi
    return t


def bark_oak(seed=1):
    t = streak_base(seed)
    r = T.rng(seed + 1)
    for i, x0 in enumerate([1, 5, 9, 13]):
        xs = wave(seed + 10 + i, x0 + r.integers(-1, 2), 0.9, 0.5)
        g = T.value_noise(seed + 20 + i, 1, 4)[:, 0]
        draw_line(t, xs, 0, side=(1, 5), present=g > .22)
    # bridges: a furrow leans into its neighbour, braiding the bark into long diamonds
    for (x, y) in poisson(seed + 3, 4, 5):
        stamp(t, x, y, ['0.', '.0'] if r.random() < .5 else ['.0', '0.'], {'0': 0})
    # one soft patch of lichen
    ys, xs = np.mgrid[0:N, 0:N]
    d = np.sqrt(T.wrapdist(ys, 4) ** 2 + T.wrapdist(xs, 11) ** 2 * 1.4) + 1.6 * T.value_noise(seed + 7, 8)
    lichen = (d < 2.6) & (t >= 2)
    return T.cleanup(t, 2), lichen


def plates(seed, nx, ny, sx, sy, jitter=.7, warp_amp=1.2, bodies=(2, 3, 3)):
    """Bark plates: stretched Voronoi cells with a dark gap, lit top-left rim and shaded bottom-right rim."""
    pts = T.jittered_points(seed, nx, ny, jitter)
    idx, _, _ = T.voronoi(pts, sx=sx, sy=sy, warp=T.fbm(seed + 1, [(4, 4, .6), (8, 8, .4)]), warp_amp=warp_amp)
    gap = T.cell_edges(idx)
    hi = (T.roll(gap, -1, 0) | T.roll(gap, 0, -1)) & ~gap
    lo = (T.roll(gap, 1, 0) | T.roll(gap, 0, 1)) & ~gap & ~hi
    body = T.rng(seed + 2).choice(list(bodies), len(pts))[idx]
    t = body.copy()
    t[hi] = np.minimum(body[hi] + 2, 5)
    t[lo] = np.maximum(body[lo] - 1, 1)
    t[gap] = 0
    return t, gap


def bark_spruce(seed=1, resin=False):
    """Araucaria-like bark: wide, short scales overlapping like shingles. The variant with resin carries one drop
    of amber, the stuff of the Âmbar Temporal."""
    t, gap = plates(seed, 3, 5, .55, 1.25, bodies=(2, 2, 3))
    drop = None
    if resin:
        for (x, y) in poisson(seed + 5, 6, 1):
            if not gap[y, x] and not gap[(y + 1) % N, x]:
                drop = [(y, x), ((y + 1) % N, x)]
                break
    return T.cleanup(t, 1, keep=(t == 0)), drop


def bark_birch(seed=1):
    t = np.full((N, N), 4)
    f = T.fbm(seed, [(4, 8, .6), (8, 16, .4)])
    t[f > np.quantile(f, .75)] = 5
    t[f < np.quantile(f, .15)] = 3
    r = T.rng(seed + 1)
    for (x, y) in poisson(seed + 2, 5, 4.6):          # lenticels: thin dark horizontal dashes
        L = int(r.integers(3, 6))
        stamp(t, x, y, ['1' * L], {'1': 1})
    x, y = poisson(seed + 3, 1, 8)[0]                  # one knot: a dark eye with a brow
    stamp(t, x, y, ['.000.', '00.00', '.222.'], {'0': 0, '2': 2})
    x, y = poisson(seed + 4, 1, 8)[0]                  # one peeling strip: light curl over its shadow
    stamp(t, (x + 6) % N, (y + 7) % N, ['.555', '2222'], {'5': 5, '2': 2})
    return T.cleanup(t, 1, keep=(t <= 2))


def bark_jungle(seed=1):
    t = streak_base(seed, 2, 1, 3, .25, .2, layers=((8, 1, .7), (16, 2, .3)))
    r = T.rng(seed + 1)
    for i, x0 in enumerate([2, 7, 12]):
        xs = wave(seed + 10 + i, x0 + r.integers(-1, 2), 0.6)
        draw_line(t, xs, 0, side=(None, 4))
    # one patch of moss on the damp side, ragged at the edge
    ys, xs = np.mgrid[0:N, 0:N]
    cy, cx = 10, 3
    d = np.sqrt(T.wrapdist(ys, cy) ** 2 * .45 + T.wrapdist(xs, cx) ** 2) + 2.2 * T.value_noise(seed + 7, 8)
    moss = d < 3.6
    return T.cleanup(t, 2), moss


def bark_acacia(seed=1):
    """Fibres spiral round the trunk: lines with slope 1/4 wrap after 16 rows by exactly 4 columns."""
    t = np.full((N, N), 3)
    r = T.rng(seed)
    ys = np.arange(N)
    for x0 in [0, 4, 8, 12]:
        jitter = int(r.integers(0, 2))
        xs = (x0 + jitter + ys // 4) % N
        xs2 = xs + 1
        for y in ys:
            t[y, xs[y]] = 0 if (y + x0) % 7 else 1
            t[y, xs2[y] % N] = 4
            t[y, (xs[y] + 2) % N] = 2 if r.random() < .6 else 3
    for (x, y) in poisson(seed + 3, 3, 5):
        stamp(t, x, y, ['5'], {'5': 5})
    return T.cleanup(t, 1)


def bark_dark_oak(seed=1):
    """Thick blocks split by deep, uneven furrows."""
    t, gap = plates(seed, 4, 3, 1.35, .62, jitter=.8, warp_amp=1.6, bodies=(2, 3, 3))
    f = T.fbm(seed + 9, [(8, 2, 1)])
    t = np.where(~gap & (f < .3), np.maximum(t - 1, 1), t)
    return T.cleanup(t, 1, keep=(t == 0))


def bark_mangrove(seed=1):
    t = streak_base(seed, 3, 2, 4, .3, .15, layers=((8, 1, .6), (16, 2, .4)))
    r = T.rng(seed + 1)
    for (x, y) in poisson(seed + 2, 3, 5):             # growth rings: long, faint, horizontal
        L = int(r.integers(4, 8))
        stamp(t, x, y, ['1' * L, '.' + '4' * (L - 2)], {'1': 1, '4': 4})
    return T.cleanup(t, 2)


def bark_cherry(seed=1):
    t = streak_base(seed, 2, 1, 3, .25, .2, layers=((2, 8, .6), (4, 16, .4)))
    r = T.rng(seed + 1)
    for (x, y) in poisson(seed + 2, 9, 3.4):           # cherry lenticels: long horizontal slits
        L = int(r.integers(2, 5))
        stamp(t, x, y, ['4' * L, '0' * L], {'4': 4, '0': 0})
    return T.cleanup(t, 1, keep=(t >= 4))


# ------------------------------------------------------------------ rings (log tops)
def rings_tones(seed, spacing=2.2, bark=True, crack=True, square=2.4):
    """Growth rings around an off-centre pith (trees grow eccentric), heartwood a step darker, a pale band of
    sapwood under the bark and one radial drying check that starts at the rim and runs inwards."""
    r = T.rng(seed)
    cy, cx = 7.5 + r.uniform(-1.0, 1.0), 7.5 + r.uniform(-1.0, 1.0)
    ys, xs = np.mgrid[0:N, 0:N] + 0.5
    dy, dx = np.abs(ys - cy), np.abs(xs - cx)
    d = (dx ** square + dy ** square) ** (1 / square)
    d = d + 0.55 * (T.fbm(seed + 3, [(2, 2, .5), (4, 4, .5)]) - .5)
    ring = (d / spacing) % 1.0
    t = np.where(ring < .3, 1, 3)
    t = np.where(d < 3.0, np.where(t == 1, 1, 2), t)
    edge_d = np.minimum.reduce([ys, xs, N - ys, N - xs])
    t = np.where((edge_d < 2.6) & (t == 3), 4, t)
    t = T.cleanup(t, 2)
    t[int(cy), int(cx)] = 0
    if crack:
        side = int(r.integers(0, 4))
        pos = int(r.integers(4, 12))
        y, x = [(1, pos), (pos, N - 2), (N - 2, pos), (pos, 1)][side]
        vy, vx = [(1, 0), (0, -1), (-1, 0), (0, 1)][side]
        for k in range(int(r.integers(3, 5))):
            t[y, x] = 0
            y, x = y + vy, x + vx
            if r.random() < .4:
                x, y = x + (vy != 0) * int(r.choice([-1, 1])), y + (vx != 0) * int(r.choice([-1, 1]))
    if bark:
        edge = np.zeros((N, N), bool)
        edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = True
        return t, edge
    return t, None


RIM_MIX = .35


def top_image(wood, seed, ring_name, hue, sat, bark_img=None, spacing=2.2, dl=-3):
    """Rings fitted so the whole face (bark rim included) lands on the vanilla luma and contrast: the rim is
    fixed by the side texture, so the rings' own mean and contrast are searched for."""
    t, edge = rings_tones(seed, spacing, bark=bark_img is not None)
    m, c = tgt(ring_name, dl)
    inner = np.ravel(t if edge is None else t[~edge])

    def render(mi, ci):
        pal = fit(inner, 5, mi, max(ci, 12), hue, sat, hue_shift=.015, sat_shift=.06)
        img = np.asarray(paint(t, pal)).copy()
        if edge is not None:
            # bark seen end-on: the side texture, pulled a little towards the outer ring
            b = np.asarray(bark_img)[edge].astype(float)
            b[:, :3] = b[:, :3] * (1 - RIM_MIX) + np.array(pal[1]) * RIM_MIX
            img[edge] = b.round().astype(np.uint8)
        return img

    if edge is None:
        return Image.fromarray(render(m, c), "RGBA")
    best = None
    for mi in np.linspace(m - 30, m + 30, 13):
        for ci in np.linspace(12, c * 1.2, 12):
            img = render(mi, ci)
            l = img[..., :3].reshape(-1, 3) @ np.array([.299, .587, .114])
            err = abs(l.mean() - m) + .6 * abs(np.percentile(l, 95) - np.percentile(l, 5) - c)
            if best is None or err < best[0]:
                best = (err, img)
    return Image.fromarray(best[1], "RGBA")


# ------------------------------------------------------------------ stripped
def stripped_tones(seed, knots=1):
    f = T.fbm(seed, [(8, 1, .55), (16, 2, .3), (4, 1, .15)])
    t = T.quantize(f, [.12, .3, .38, .2])
    r = T.rng(seed + 1)
    # facets left by the stone axe: soft lighter bands every 5-6 rows
    y = int(r.integers(0, 4))
    while y < N:
        x0 = int(r.integers(0, N))
        for x in range(x0, x0 + int(r.integers(5, 9))):
            t[y % N, x % N] = min(3, t[y % N, x % N] + 1)
        y += int(r.integers(5, 7))
    for (x, yk) in poisson(seed + 2, knots, 8):
        stamp(t, x, yk, ['.1.', '101', '.1.'], {'1': 1, '0': 0})
    return T.cleanup(t, 2)


# ------------------------------------------------------------------ planks
def planks_tones(seed):
    """Four hand-split boards (4 rows each, so slabs and stairs still line up), every board a shade of its own,
    long grain streaks along the board. Only two boards are joined (staggered butt joints, a shade darker, not a
    gap), so the face reads as long boards and not as brickwork; two wooden pegs in the whole face."""
    r = T.rng(seed)
    t = np.zeros((N, N), int)
    shades = r.permutation([1, 2, 2, 3])
    joined = r.permutation([True, True, False, False])
    jbase = int(r.integers(0, N))
    for b in range(4):
        y0 = b * 4
        t[y0:y0 + 3] = shades[b]
        for _ in range(3):                                   # grain: long streaks, lighter or darker
            y = y0 + int(r.integers(0, 3))
            x = int(r.integers(0, N))
            L = int(r.integers(6, 13))
            dv = 1 if r.random() < .55 else -1
            for xx in range(x, x + L):
                t[y, xx % N] = np.clip(shades[b] + dv, 1, 4)
        t[y0 + 3, :] = 0                                     # gap under the board
        if joined[b]:
            jx = (jbase + b * 7) % N
            t[y0:y0 + 3, jx] = max(1, shades[b] - 1) if shades[b] > 1 else 0
            t[y0 + 1, (jx + 2) % N] = 0                      # peg
    return t


# ------------------------------------------------------------------ the eight woods
EXTRA = {
    "lichen": [(150, 158, 128), (176, 182, 150)],
    "moss": [(70, 92, 40), (92, 118, 52)],
    "amber": [(196, 110, 18), (240, 170, 48)],
}

WOODS = {
    # wood: (hue, sat, bark style, ring spacing, bark hue/sat override)
    "oak": (.090, .46, "oak", 2.3, None),
    "spruce": (.075, .55, "spruce", 2.2, None),
    "birch": (.115, .30, "birch", 2.4, (.11, .05)),
    "jungle": (.095, .55, "jungle", 2.6, None),
    "acacia": (.055, .62, "acacia", 2.3, (.09, .14)),
    "dark_oak": (.080, .58, "dark_oak", 2.2, None),
    "mangrove": (.010, .55, "mangrove", 2.3, (.085, .42)),
    "cherry": (.985, .30, "cherry", 2.3, (.92, .32)),
}


def bark(wood, resin=False, growth=False):
    hue, sat, style, _, ov = WOODS[wood]
    bh, bs = ov if ov else (hue, sat)
    m, c = tgt(f"{wood}_log")
    extra_pix = []
    if style == "oak":
        t, mask = bark_oak(1)
    elif style == "spruce":
        t, resin = bark_spruce(2, resin)
        mask = None
    elif style == "jungle":
        t, mask = bark_jungle(1)
    else:
        t = {"birch": bark_birch, "acacia": bark_acacia, "dark_oak": bark_dark_oak, "mangrove": bark_mangrove,
             "cherry": bark_cherry}[style](1)
        mask = None
    pal = fit(t, 6, m, c, bh, bs, hue_shift=.02, sat_shift=.06 if bs > .2 else .0)
    img = np.asarray(paint(t, pal)).copy()
    if style == "oak" and growth:
        lic = np.array(EXTRA["lichen"])[(t[mask] >= 3).astype(int)]
        img[mask, :3] = lic
    if style == "jungle" and growth:
        mv = np.array(EXTRA["moss"])[(t[mask] >= 2).astype(int)]
        img[mask, :3] = mv
    if style == "spruce" and resin:
        (y0, x0), (y1, x1) = resin
        img[y0, x0, :3] = EXTRA["amber"][1]
        img[y1, x1, :3] = EXTRA["amber"][0]
    return Image.fromarray(img, "RGBA")


def textures(wood):
    hue, sat, style, spacing, _ = WOODS[wood]
    side = bark(wood)
    out = {f"{wood}_log": side}
    out[f"{wood}_log_top"] = top_image(wood, SEEDS[wood] + 3, f"{wood}_log_top", hue, sat, side, spacing)
    m, c = tgt(f"stripped_{wood}_log")
    for k in range(8):   # smooth wood shows any seam: take the first seed whose wrap is no stronger than inside
        st = stripped_tones(SEEDS[wood] + 5 + 100 * k)
        img = paint(st, fit(st, 4, m, c, hue, sat, hue_shift=.012, sat_shift=.04))
        if T.seam_excess(img) <= 1.2:
            break
    out[f"stripped_{wood}_log"] = img
    out[f"stripped_{wood}_log_top"] = top_image(wood, SEEDS[wood] + 3, f"stripped_{wood}_log_top", hue, sat, None, spacing)
    pt = planks_tones(SEEDS[wood] + 7)
    m, c = tgt(f"{wood}_planks")
    out[f"{wood}_planks"] = paint(pt, fit(pt, 5, m, c, hue, sat, hue_shift=.02, sat_shift=.05, gamma=.55))
    if wood == "spruce":
        out["spruce_log_resin"] = bark(wood, resin=True)   # weighted variant: 1 trunk block in 6
    if wood == "oak":
        out["oak_log_lichen"] = bark(wood, growth=True)    # weighted variant: 1 in 4
    if wood == "jungle":
        out["jungle_log_moss"] = bark(wood, growth=True)   # weighted variant: 1 in 3
    return out


SEEDS = {w: i * 10 for i, w in enumerate(["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry"])}

ALL = {}
for w in WOODS:
    ALL.update(textures(w))
