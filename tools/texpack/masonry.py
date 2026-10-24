"""TX3b: building and ground blocks of the Late Cretaceous pack: hand-dressed stone courses (with moss, cracks
and an ammonite carved in the chiseled block), hand-shaped fired bricks in lime mortar, moss cushions, tilled
furrows, a packed path with a theropod track pressed in it, thatch bundles for hay, snow, and on the water giant
horsetail canes for sugar cane and a notched water lily pad (water lilies grew in Cretaceous ponds)."""
import math

import numpy as np
from PIL import Image

import api
import cretaceo as C
import tex as T
from plants import grid
from stamps import base, poisson, stamp
from tex import N


def courses(seed, heights=(4, 4, 4, 4), lengths=(5, 9), bodies=(2, 3, 3, 4), gap_tone=0, bevel=True):
    """Rows of dressed blocks: a mortar line under each course and between blocks, joints staggered course to
    course, every block a tone of its own, lit top-left rim and shaded bottom-right rim."""
    r = T.rng(seed)
    t = np.zeros((N, N), int)
    owner = np.zeros((N, N), int)
    gap = np.zeros((N, N), bool)
    y0, k, prev = 0, 0, []
    for h in heights:
        x = int(r.integers(0, N))
        while any(abs(x - p) < 2 or abs(x - p) > N - 2 for p in prev):
            x = int(r.integers(0, N))
        start, joints = x, []
        while True:
            L = int(r.integers(lengths[0], lengths[1] + 1))
            if (x - start) + L > N - lengths[0]:
                L = N - (x - start)
            body = int(r.choice(bodies))
            for xx in range(x, x + L):
                t[y0:y0 + h, xx % N] = body
                owner[y0:y0 + h, xx % N] = k
            joints.append(x % N)
            gap[y0:y0 + h, x % N] = True
            k += 1
            x += L
            if x - start >= N:
                break
        gap[y0 + h - 1, :] = True
        prev = joints
        y0 += h
    if bevel:
        lit = (T.roll(gap, 0, -1) | T.roll(gap, -1, 0)) & ~gap
        shade = (T.roll(gap, 0, 1) | T.roll(gap, 1, 0)) & ~gap & ~lit
        t = np.where(lit, np.minimum(t + 1, 5), t)
        t = np.where(shade, np.maximum(t - 1, 1), t)
    t[gap] = gap_tone
    return t, gap, owner


def stone_bricks(seed=3):
    t, gap, _ = courses(seed, heights=(4, 4, 4, 4), lengths=(6, 9))
    for (x, y) in poisson(seed + 5, 6, 3.5):                # tool marks on the faces
        if not gap[y, x] and not gap[y, (x + 1) % N]:
            stamp(t, x, y, ['1'], {'1': lambda v: max(1, v - 1)})
    return t, gap


def stone_bricks_img():
    t, _ = stone_bricks()
    return api.paint(t, api.Material("stone_bricks", .08, .04, dl=-4, n=6))


def mossy_stone_bricks():
    t, gap = stone_bricks()
    img = np.asarray(api.paint(t, api.Material("mossy_stone_bricks", .08, .04, dl=-4, n=6))).copy()
    moss = [(64, 84, 40), (84, 108, 50), (106, 132, 62)]
    f = T.fbm(41, [(4, 4, .5), (8, 8, .5)])
    near = T.distance_to(gap) <= 1
    m = (f > .55) & near | (f > .78)
    lvl = T.quantize(T.fbm(42, [(16, 16, 1)]), [.3, .45, .25])
    img[m, :3] = np.array(moss)[lvl][m]
    return Image.fromarray(img, "RGBA")


def cracked_stone_bricks():
    t, gap = stone_bricks()
    r = T.rng(43)
    for _ in range(3):                                     # cracks wander from a corner across a block
        x, y = int(r.integers(0, N)), int(r.integers(0, N))
        for _ in range(int(r.integers(4, 7))):
            if not gap[y % N, x % N]:
                t[y % N, x % N] = 0
            x += int(r.choice([0, 1, 1]))
            y += int(r.choice([1, 1, 0, -1]))
    return api.paint(t, api.Material("cracked_stone_bricks", .08, .04, dl=-4, n=6))


def chiseled_stone_bricks():
    """A framed panel with an ammonite carved in it, the era's emblem."""
    t = np.full((N, N), 3)
    t[0, :] = t[:, 0] = 4
    t[N - 1, :] = t[:, N - 1] = 0
    t[1, 1:15] = 4
    t[1:15, 1] = 4
    t[14, 1:15] = 1
    t[1:15, 14] = 1
    t[3:13, 3] = 1
    t[3, 3:13] = 1
    t[12, 3:13] = 4
    t[3:13, 12] = 4
    # the ammonite: one groove coiling out from the centre, ribs across the outer whorl
    ys, xs = np.mgrid[0:N, 0:N] + .5
    cx, cy = 7.6, 8.0
    r = np.hypot(xs - cx, ys - cy)
    th = np.arctan2(ys - cy, xs - cx) % (2 * math.pi)
    coil = ((r - 1.9 * th / (2 * math.pi)) / 1.9) % 1.0
    inside = r < 4.4
    groove = inside & (coil < .32)
    ribs = inside & (r > 2.9) & (((th * 10 / (2 * math.pi)) % 1.0) < .18)
    cut = groove | ribs
    cut[int(cy), int(cx)] = True
    t = np.where(cut, 1, t)
    lit = T.roll(cut, -1, -1) & ~cut & inside               # the lower-right lip of a cut catches the light
    t = np.where(lit, 4, t)
    return api.paint(t, api.Material("chiseled_stone_bricks", .08, .04, dl=-4, n=5))


def bricks():
    """Hand-shaped fired bricks, each a little different, in pale lime mortar."""
    t, gap, owner = courses(51, heights=(4, 4, 4, 4), lengths=(5, 7), bodies=(1, 2, 2, 3), gap_tone=5)
    for (x, y) in poisson(52, 5, 3.6):
        if not gap[y, x]:
            stamp(t, x, y, ['0'], {'0': 0})
    return api.paint(t, api.Material("bricks", .025, .5, dl=-3, n=6, sat_shift=.1))


def moss_block():
    t = base(61, 2, 1, 3, .22, .2, layers=((4, 4, .5), (8, 8, .5)))
    for (x, y) in poisson(62, 10, 3.0):                   # cushions: lit cap, shaded foot
        stamp(t, x, y, ['.4.', '434', '.1.'], {'4': 4, '3': 3, '1': 1})
    return api.paint(T.cleanup(t, 1), api.Material("moss_block", .23, .55, dl=-3, n=5))


def farmland(moist=False):
    """Furrows dug with a stick into the pack's own earth: each furrow a wavering dark hollow with a lit ridge
    above it, clods left along the edge."""
    t = C.dirt_tones(1)
    t = np.clip(t, 0, 4)
    r = T.rng(71)
    for row in range(4):
        y0 = row * 4 + 3
        xs = np.arange(N)
        wob = np.round(.6 * np.sin(2 * math.pi * xs / N * 2 + r.uniform(0, 6.283))).astype(int)
        for x in xs:
            y = (y0 + wob[x]) % N
            t[y, x] = 0
            t[(y - 1) % N, x] = min(4, t[(y - 1) % N, x] + 1)
            t[(y - 2) % N, x] = max(t[(y - 2) % N, x], 3)
    for (x, y) in poisson(72, 5, 3.5):                    # clods
        stamp(t, x, y, ['4', '1'], {'4': 4, '1': 1})
    ref = "farmland_moist" if moist else "farmland"
    m = api.Material(ref, .055, .55 if moist else .45, dl=-3, n=5)
    img = api.paint(t, m)
    if moist:
        a = np.asarray(img).copy()
        for (x, y) in poisson(73, 8, 2.6):                # sheen of water in the hollows
            if t[y, x] == 0:
                a[y, x, :3] = np.minimum(a[y, x, :3].astype(int) + 36, 255)
        img = Image.fromarray(a, "RGBA")
    return img


TRACK = [  # a three-toed theropod print pressed into the path
    "1...1",
    ".1.1.",
    ".111.",
    "..1..",
]


def dirt_path_top():
    t = base(81, 2, 1, 3, .2, .2, layers=((4, 4, .5), (8, 8, .5)))
    stamp(t, 5, 5, TRACK, {'1': 0})
    stamp(t, 6, 6, ["....", "....", "..4.", "...."], {'4': 3})
    return api.paint(T.cleanup(t, 1, keep=(t == 0)), api.Material("dirt_path_top", .07, .42, dl=-3, n=4))


def dirt_path_side():
    """The path block is 15/16 tall: the top row stays empty, two rows of packed path, then earth."""
    a = np.asarray(C.dirt(1)).copy()
    top = np.asarray(dirt_path_top())
    a[1:3] = top[1:3]
    a[3, :, :3] = (a[3, :, :3] * .8).astype(np.uint8)
    a[0, :, 3] = 0
    return Image.fromarray(a, "RGBA")


def hay_side():
    """A thatch bundle: straws standing, tied twice with cord."""
    f = T.fbm(91, [(16, 2, .6), (16, 4, .4)])
    t = T.quantize(f, [.15, .3, .35, .2])
    for y in (4, 11):
        t[y, :] = 0
        t[y + 1, :] = 1
    return api.paint(t, api.Material("hay_block_side", .12, .62, dl=-3, n=5))


def hay_top():
    """The cut end of the bundle: hollow straw ends, the cord round the rim."""
    t = base(93, 2, 1, 3, .2, .2, layers=((8, 8, .5), (16, 16, .5)))
    for (x, y) in poisson(94, 22, 2.2):
        stamp(t, x, y, ['4', '1'], {'4': 4, '1': 1})
    t[0, :] = t[-1, :] = t[:, 0] = t[:, -1] = 0
    return api.paint(t, api.Material("hay_block_top", .12, .66, dl=-3, n=5))


def snow():
    t = np.full((N, N), 1)
    for (x, y) in poisson(101, 7, 3.6):
        t[y, x] = 0
    return T.colorize(t, [(236, 244, 250), (252, 253, 255)])


CANE = [  # giant horsetail canes: jointed, tinted by the biome
    "..3....3...3....",
    "..3....3...3....",
    ".2.2...1...3....",
    "..1...232..1....",
    "..3....3..232...",
    "..3....3...3....",
    "..3....3...3....",
    ".232...1...3....",
    "..1....3...1....",
    "..3...232.232...",
    "..3....3...3....",
    "..3....3...3....",
    ".2.2...3...3....",
    "..1....1...1....",
    "..3...232..3....",
    "..3....3...3....",
]

LILY = [  # a water lily pad: round, notched, veins from the centre
    "................",
    "................",
    ".....33333......",
    "...334444433....",
    "..33444244433...",
    "..3444424444 3..",
    ".344444244443 ..",
    ".34442222....  .",
    ".3444442444 3...",
    ".34442444244 3..",
    "..344244442443..",
    "..33444244443...",
    "...3344444333...",
    ".....33333......",
    "................",
    "................",
]


def sugar_cane():
    t, op = grid(CANE)
    return api.paint(t, api.Material("sugar_cane", 0, 0, dl=-2, n=3), alpha=op)


def lily_pad():
    rows = [r.replace(' ', '.') for r in LILY]
    t, op = grid(rows)
    return api.paint(t, api.Material("lily_pad", 0, 0, dl=-2, n=4), alpha=op)


ALL = {
    "stone_bricks": stone_bricks_img(), "mossy_stone_bricks": mossy_stone_bricks(),
    "cracked_stone_bricks": cracked_stone_bricks(), "chiseled_stone_bricks": chiseled_stone_bricks(),
    "bricks": bricks(), "moss_block": moss_block(), "farmland": farmland(), "farmland_moist": farmland(True),
    "dirt_path_top": dirt_path_top(), "dirt_path_side": dirt_path_side(), "hay_block_side": hay_side(),
    "hay_block_top": hay_top(), "snow": snow(), "sugar_cane": sugar_cane(), "lily_pad": lily_pad(),
}
