"""TX2: the workshop blocks of the Late Cretaceous pack, built from what a castaway in the Cretaceous has at hand.

crafting table: a split-log worktop on lashed posts, the grid cut into the wood with a flint, a stone hammer
hanging on one side and a flint knife with a bone awl on the front; furnace: a kiln of fieldstones bedded in clay
with an arched mouth (embers inside when lit); torch: a stick with a head of fibre soaked in resin."""
import numpy as np
from PIL import Image

import tex as T
from fit import colour_at
from materials import MATERIALS
from stamps import poisson
from tex import N
from vanilla import target
import woods
from woods import planks_tones, plates


def ramp(mat, lums):
    m = MATERIALS[mat]
    return [colour_at(l, m.hue + m.hue_shift * (k / max(len(lums) - 1, 1) - .5) * 2, m.sat) for k, l in enumerate(lums)]


def overlay(img, rows, colours, x0=0, y0=0):
    a = np.asarray(img).copy()
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.' or ch == ' ':
                continue
            y, x = y0 + j, x0 + i
            if 0 <= y < N and 0 <= x < N:
                a[y, x, :3] = colours[ch]
                a[y, x, 3] = 255
    return Image.fromarray(a, "RGBA")


def lum_of(img):
    a = np.asarray(img)[..., :3].reshape(-1, 3) @ np.array([.299, .587, .114])
    return a.mean(), np.percentile(a, 95) - np.percentile(a, 5)


# ------------------------------------------------------------------ colours
PLANK = ramp("oak_planks", [70, 112, 128, 142, 158])        # 0 = gap
BARK = ramp("oak_bark", [46, 64, 82, 100])
STONE = ramp("stone", [58, 96, 132, 170])
FLINT = [(40, 38, 44), (70, 66, 72), (128, 124, 128)]
BONE = [(178, 170, 140), (220, 212, 186), (240, 236, 214)]
CORD = [(92, 72, 34), (142, 116, 60), (176, 150, 86)]
HANDLE = [(84, 60, 32), (132, 98, 54)]
CLAY = [(92, 62, 44), (122, 84, 58), (146, 104, 72)]

COL = {
    'B': BARK[0], 'b': BARK[2], 'v': BARK[3],
    'S': STONE[3], 's': STONE[2], 't': STONE[1], 'u': STONE[0],
    'F': FLINT[0], 'f': FLINT[1], 'g': FLINT[2],
    'O': BONE[2], 'o': BONE[1], 'q': BONE[0],
    'C': CORD[0], 'c': CORD[1], 'k': CORD[2],
    'W': HANDLE[0], 'w': HANDLE[1],
    'K': (24, 18, 14),
    'D': tuple(np.array(PLANK[1]) * .62),                 # shadow a hanging tool casts on the wood
    'L': tuple(np.array(PLANK[0]) * .72),                  # a cut in the worktop
}


def planks(seed=31):
    return T.colorize(planks_tones(seed), PLANK)


# ------------------------------------------------------------------ crafting table
TABLE_TOP = [  # the grid cut with a flint, a little uneven; a few knife scores
    "BBBBBBBBBBBBBBBB",
    "Bb.............B",
    "B..............B",
    "B...L....L..L..B",
    "B...L....L...L.B",
    "BLLLLLLLLLLLLL.B",
    "B...L....L.....B",
    "B.L.L....L.....B",
    "B..LL....L.....B",
    "B...L....L.....B",
    "B.LLLLLLLLLLLLLB",
    "B...L....L.....B",
    "B...L....L.L...B",
    "B...L.....L....B",
    "B.............bB",
    "BBBBBBBBBBBBBBBB",
]

TABLE_SIDE = [  # tabletop edge, lashed posts, a stone hammer hanging from a cord
    "bvbbvbbbvbbvbbvb",
    "BBBBBBBBBBBBBBBB",
    "bkC..........Ckb",
    "bCk....c.....kCb",
    "Bk.....c.....Ckb",
    "b......c......vb",
    "b....sSSSs....bB",
    "b...sSSsSSt...bB",
    "b...tSskcst...bB",
    "b....tcCctDD..bB",
    "b......wWD....vB",
    "b......wWD....bB",
    "b......wWD....bB",
    "b......wWD....bB",
    "b.......DD....bB",
    "vk...........kvB",
    "bB...........BbB",
]

TABLE_FRONT = [  # flint knife and bone awl on pegs
    "bvbbvbbbvbbvbbvb",
    "BBBBBBBBBBBBBBBB",
    "bkC..........Ckb",
    "bCk..W....W..kCb",
    "Bk...w....w..Ckb",
    "b...gf....O...vb",
    "b...gfFD.oOD..bB",
    "b...gfFD.oOD..bB",
    "b...gfFD.oqD..bB",
    "b....fFD.oqD..bB",
    "b....gFD..oD..vB",
    "b....ccD..qD..bB",
    "b....CcD...D..bB",
    "b....wWD......bB",
    "vk...wWD.....kvB",
    "bB...........BbB",
]


def crafting_table():
    # the worktop is one split slab of log, grain running across
    slab = np.rot90(woods.stripped_tones(33))
    top = T.colorize(slab, ramp("oak_stripped", [82, 98, 112, 126]))
    top = overlay(top, TABLE_TOP, COL)
    a = np.asarray(top).copy()
    # the cut lines catch light on their lower-right lip
    for y in (5, 10):
        a[y + 1, 1:15, :3] = np.minimum(a[y + 1, 1:15, :3].astype(int) + 22, 255)
    for x in (4, 9):
        a[1:15, x + 1, :3] = np.minimum(a[1:15, x + 1, :3].astype(int) + 22, 255)
    top = Image.fromarray(a, "RGBA")
    side = overlay(planks(37), TABLE_SIDE, COL)
    front = overlay(planks(41), TABLE_FRONT, COL)
    return top, side, front


# ------------------------------------------------------------------ furnace (kiln)
def kiln_stones(seed, nx=3, ny=4, pal=None):
    t, gap = plates(seed, nx, ny, .9, 1.1, jitter=.6, warp_amp=1.4, bodies=(1, 2, 2))
    pal = pal or STONE
    img = np.asarray(T.colorize(np.clip(t, 0, 4), pal + [pal[3]])).copy()
    # mortar of clay in the joints instead of dark gaps
    img[gap, :3] = np.array(CLAY)[(T.white(seed + 4)[gap] > .5).astype(int)]
    return Image.fromarray(img, "RGBA"), gap


MOUTH = [
    "....sSSSSs......",
    "...sSttttSs.....",
    "..sStKKKKtSs....",
    "..StKKKKKKtS....",
    "..StKKKKKKtS....",
    "..StKKKKKKtS....",
    "..StKKKKKKtS....",
    ".sSSSSSSSSSSs...",
]

EMBERS = {'1': (110, 30, 12), '2': (196, 70, 18), '3': (246, 150, 40), '4': (255, 222, 120), '5': (70, 22, 14)}
FIRE = [
    "......",
    "...4..",
    ".4.3.4",
    ".3343.",
    "323232",
    "212121",
]


def furnace():
    side, _ = kiln_stones(51)
    top, _ = kiln_stones(53, 2, 2)
    front, _ = kiln_stones(57, pal=ramp("stone", [50, 84, 116, 150]))
    front = overlay(front, MOUTH, COL, 1, 7)
    a = np.asarray(front).copy()
    # soot: years of smoke have blackened the stones above the mouth
    ys, xs = np.mgrid[0:N, 0:N]
    d = np.sqrt(((xs - 6.5) / 4.5) ** 2 + ((ys - 8.0) / 7.0) ** 2)
    soot = np.clip(1.0 - d, 0, 1) * (ys < 9)
    k = np.where(soot > .45, .62, np.where(soot > .1, .8, 1.0))        # two steps of soot, no smeared colours
    a[..., :3] = (a[..., :3] * k[..., None]).round().astype(np.uint8)
    on = a.copy()
    # lit: embers in the mouth, the arch stones warmed by the glow
    for j, row in enumerate(FIRE):
        for i, ch in enumerate(row):
            if ch != '.':
                on[9 + j, 5 + i, :3] = EMBERS[ch]
    glow = np.array([255, 150, 60], float)
    for y in range(7, 15):
        for x in range(2, 14):
            if MOUTH[y - 7][x - 1] in 'tS' if 0 <= x - 1 < 16 else False:
                on[y, x, :3] = (on[y, x, :3] * .7 + glow * .3).round()
    return top, side, Image.fromarray(a, "RGBA"), Image.fromarray(on, "RGBA")


# ------------------------------------------------------------------ torch
def torch():
    """Only columns 7-8, rows 6-15 are on the model (flame on top, stick below)."""
    a = np.zeros((N, N, 4), np.uint8)
    col = {
        (6, 7): (255, 236, 160), (6, 8): (255, 210, 110),
        (7, 7): (255, 196, 84), (7, 8): (236, 140, 44),
        (8, 7): (150, 86, 26), (8, 8): (112, 62, 20),     # resin-soaked fibre head
        (9, 7): CORD[1], (9, 8): CORD[0],
    }
    for y in range(10, 16):
        col[(y, 7)] = HANDLE[1]
        col[(y, 8)] = HANDLE[0]
    col[(12, 7)] = (84, 60, 32)                             # a knot in the stick
    for (y, x), c in col.items():
        a[y, x, :3] = c
        a[y, x, 3] = 255
    return Image.fromarray(a, "RGBA")


ALL = {}
ALL["crafting_table_top"], ALL["crafting_table_side"], ALL["crafting_table_front"] = crafting_table()
ALL["furnace_top"], ALL["furnace_side"], ALL["furnace_front"], ALL["furnace_front_on"] = furnace()
ALL["torch"] = torch()
