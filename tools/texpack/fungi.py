"""TX3d: fungi and undergrowth of the Late Cretaceous pack. Huge mushrooms as bracket fungi with growth zones
and warty caps; small mushrooms; a berry shrub through its four stages (flowering plants were spreading
fast); hanging roots; a pale cave lichen. Sprites are hand-drawn grids: digits are tones of the material
(1 darkest), letters are fixed colours (berries, spots, stems), '.' is empty."""
import numpy as np

import api
import tex as T
from stamps import base, poisson, stamp
from tex import N

M = api.Material


def sprite(rows, mat, colours=None):
    """Grid -> RGBA. Digits 1..n are the material's ramp; letters are looked up in colours."""
    colours = colours or {}
    letters = sorted({c for r in rows for c in r if c.isalpha()})
    n = max(int(c) for r in rows for c in r if c.isdigit())
    idx = {c: n + k for k, c in enumerate(letters)}
    t = np.array([[0 if c == '.' else idx[c] if c.isalpha() else int(c) - 1 for c in r] for r in rows])
    op = np.array([[c != '.' for c in r] for r in rows])
    return api.paint(t, mat.like(n=n), alpha=op, extra=[colours[c] for c in letters])


# ---------------------------------------------------------------- small mushrooms
BROWN_MUSHROOM = [  # two ink-cap-like mushrooms, the taller one with ribbed gills
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "......444.......",
    ".....43332......",
    "....4333332.....",
    "....1212121.....",
    "......43...444..",
    "......43..43332.",
    "......43..12121.",
    ".....4332..43...",
]

RED_MUSHROOM = [  # a domed red cap with a few pale warts and a button cap at its foot
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    ".......443......",
    "......4w3332....",
    ".....433333w2...",
    ".....3w333322...",
    ".....2222222....",
    "........st......",
    "........st..43..",
    "........st.3w32.",
    ".......ssst.st..",
]
STEM = {"s": (188, 174, 150), "t": (150, 136, 114), "w": (200, 184, 162)}


# ---------------------------------------------------------------- huge mushroom blocks
def brown_mushroom_block():
    """A bracket fungus seen from above: broad concentric growth zones, a few pores."""
    ys, xs = np.mgrid[0:N, 0:N] + .5
    r = np.hypot(xs - 3.0, ys - 20.0) + 1.2 * T.fbm(401, [(4, 4, 1)])
    zone = (r / 3.0) % 1.0
    t = np.where(zone < .25, 1, np.where(zone < .8, 2, 3))
    for (x, y) in poisson(402, 4, 4.5):
        stamp(t, x, y, ['D'], {'D': 0})
    return api.paint(t, M("brown_mushroom_block", .07, .45, dl=-3, n=4))


def red_mushroom_block():
    t = base(411, 2, 1, 3, .2, .2, layers=((4, 4, .5), (8, 8, .5)))
    for (x, y) in poisson(412, 4, 6.0):                      # pale warts, lit on top, shaded below
        stamp(t, x, y, ['WW', 'SS'], {'W': 5, 'S': 0})
    return api.paint(t, M("red_mushroom_block", .995, .78, dl=-3, n=4), extra=[(226, 212, 196), (236, 226, 212)])


def mushroom_stem():
    """Pale fibrous flesh in long vertical strands."""
    f = T.fbm(421, [(16, 2, .6), (16, 4, .4)])
    t = T.quantize(f, [.15, .55, .3])
    return api.paint(t, M("mushroom_stem", .1, .1, dl=-3, n=3))


def mushroom_block_inside():
    """The underside: pores in loose rows."""
    t = base(431, 2, 1, 3, .15, .2, layers=((4, 4, .5), (8, 8, .5)))
    for (x, y) in poisson(432, 18, 2.6):
        stamp(t, x, y, ['D'], {'D': 0})
    return api.paint(t, M("mushroom_block_inside", .08, .35, dl=-3, n=4))


# ---------------------------------------------------------------- berry shrub
BERRY_SPROUT = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    ".......4........",
    "......434..4....",
    "..4...32..343...",
    ".343..2..3.2....",
    "..32..2.32.2.4..",
    "...2.2.2...2343.",
    "....2.121.2..2..",
    ".....2.1.2......",
    "......111.......",
]

BERRY_BUSH = [  # 'a' marks where berries grow: leaf on stage 1, green on stage 2, ripe on stage 3
    "................",
    ".....3.....4....",
    "...434.3..343...",
    "..43a3434.3a2.4.",
    ".4332.32a3423434",
    "..3a24323.32a32.",
    ".4323.2a43.2323.",
    "43a2343232432a3.",
    ".323a2.4323a232.",
    "..2323a3.a32323.",
    ".43a2.3213.2a2..",
    "..232.2.1..232..",
    "...2...1.1..2...",
    "......1..1......",
    ".......1.1......",
    ".......11.......",
]


def berry_stage(stage):
    if stage == 0:
        return sprite(BERRY_SPROUT, M("sweet_berry_bush_stage0", .27, .5, dl=-2))
    rows = BERRY_BUSH
    if stage == 1:
        rows = ["................"] * 3 + [r.replace('a', '3') for r in rows[3:]]
        return sprite(rows, M("sweet_berry_bush_stage1", .27, .5, dl=-2))
    if stage == 2:
        return sprite(rows, M("sweet_berry_bush_stage2", .27, .5, dl=-2), {"a": (104, 124, 54)})
    return sprite(rows, M("sweet_berry_bush_stage3", .27, .5, dl=-2), {"a": (150, 26, 52)})


# ---------------------------------------------------------------- cave growth
HANGING_ROOTS = [
    "21..32..2..213.1",
    ".2..3...21..3..2",
    ".3..2...3...2..3",
    "..2.3..2.4.3...2",
    "..3..2.3....3..3",
    "..2..3..2..2..2.",
    ".3...2..3..3..3.",
    ".2..2...2..4..2.",
    ".4..3..2...3..3.",
    "..2.2..3..2...4.",
    "..3..4.2..3.....",
    "..2....3..4.....",
    "..4....2........",
    ".......4........",
    "................",
    "................",
]


def glow_lichen():
    """Rosettes of a pale cave lichen spreading in patches (it glows in game)."""
    t = np.full((N, N), -1)
    patch = T.fbm(441, [(4, 4, .6), (8, 8, .4)]) > .58
    t[patch] = 1
    for (x, y) in poisson(442, 10, 3.6):
        stamp(t, x, y, ['.2.', '232', '.2.'], {'2': 2, '3': 3})
    for (x, y) in poisson(443, 6, 4.0):
        stamp(t, x, y, ['0'], {'0': 0})
    op = t >= 0
    return api.paint(np.maximum(t, 0), M("glow_lichen", .42, .16, dl=-2, n=4), alpha=op)


def textures():
    out = {
        "brown_mushroom": sprite(BROWN_MUSHROOM, M("brown_mushroom", .07, .45, dl=-2)),
        "red_mushroom": sprite(RED_MUSHROOM, M("red_mushroom", .995, .8, dl=-2), STEM),
        "brown_mushroom_block": brown_mushroom_block(), "red_mushroom_block": red_mushroom_block(),
        "mushroom_stem": mushroom_stem(), "mushroom_block_inside": mushroom_block_inside(),
        "hanging_roots": sprite(HANGING_ROOTS, M("hanging_roots", .07, .4, dl=-2)),
        "glow_lichen": glow_lichen(),
    }
    for s in range(4):
        out[f"sweet_berry_bush_stage{s}"] = berry_stage(s)
    return out


ALL = textures()
