"""
Terrassic 16x16 tileable textures for the primitive building blocks.  Everything is drawn with code (no external
art): tileable value noise for the material, a colour ramp taken from the real material, tileable Voronoi cells for
stacked stones and flagstones, light from the top-left.

Rocks: ROCKS has one entry per rock; every rock gets <rock>.png (natural), <rock>_stacked.png (dry-laid stones),
<rock>_flagstone.png (flat paving), mossy_<rock>_stacked.png and <rock>_pebbles.png (loose pebbles on soil).
Woods: WOODS has one entry per prehistoric tree (bark, log ends, stripped, hewn planks, leaves, sapling, lashed door
and trapdoor, branch fence).  The other textures are in OTHER.

usage: python3 blocks.py [preview.png]   -> writes into common/src/main/resources/assets/terrassic/textures/block
"""
import math
import os
import random
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from sprites import Canvas, hexc, shade, mixc  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEX = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "block")
N = 16


# ------------------------------------------------------------------ tileable helpers
class Noise:
    """Tileable value noise on the 16x16 torus: smooth-interpolated random lattices summed over octaves.
    stretch > 1 on an axis gives more cells (finer detail) along it."""

    def __init__(self, seed, periods=(2, 4, 8), weights=(0.5, 0.3, 0.2), stretch=(1.0, 1.0)):
        rnd = random.Random(seed)
        self.layers = []
        for p, w in zip(periods, weights):
            px = max(1, round(p * stretch[0]))
            py = max(1, round(p * stretch[1]))
            grid = [[rnd.random() for _ in range(px)] for _ in range(py)]
            self.layers.append((px, py, grid, w))

    def __call__(self, x, y):
        total = 0.0
        for px, py, grid, w in self.layers:
            fx, fy = x / N * px, y / N * py
            x0, y0 = int(math.floor(fx)), int(math.floor(fy))
            tx, ty = fx - x0, fy - y0
            tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
            a = grid[y0 % py][x0 % px]; b = grid[y0 % py][(x0 + 1) % px]
            c = grid[(y0 + 1) % py][x0 % px]; d = grid[(y0 + 1) % py][(x0 + 1) % px]
            total += w * ((a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty)
        return total


def ramp(colors, t):
    """Colour at t in [0,1] along a list of hex colours (dark -> light)."""
    t = max(0.0, min(0.999, t))
    pos = t * (len(colors) - 1)
    i = int(pos)
    return mixc(hexc(colors[i]), hexc(colors[i + 1]), pos - i)


def contrast(v, k):
    return 0.5 + (v - 0.5) * k


class Cells:
    """Tileable Voronoi: each pixel gets its nearest seed (owner) and its distance to the border (d2 - d1).
    sx < 1 stretches the cells horizontally (wide stones)."""

    def __init__(self, seed, count, sx=1.0, sy=1.0):
        rnd = random.Random(seed)
        self.seeds = [(rnd.uniform(0, N), rnd.uniform(0, N)) for _ in range(count)]
        self.sx, self.sy = sx, sy
        self.owner = [[0] * N for _ in range(N)]
        self.edge = [[0.0] * N for _ in range(N)]
        for y in range(N):
            for x in range(N):
                ds = sorted((self._dist(x + 0.5, y + 0.5, s), i) for i, s in enumerate(self.seeds))
                self.owner[y][x] = ds[0][1]
                self.edge[y][x] = ds[1][0] - ds[0][0]

    def _dist(self, x, y, s):
        dx = abs(x - s[0]); dy = abs(y - s[1])
        return math.hypot(min(dx, N - dx) * self.sx, min(dy, N - dy) * self.sy)

    def at(self, x, y):
        return self.owner[y % N][x % N]

    def border(self, x, y, width):
        return self.edge[y % N][x % N] < width


def paint(fn):
    cv = Canvas()
    for y in range(N):
        for x in range(N):
            cv.set(x, y, fn(x, y))
    return cv


def copy(cv):
    out = Canvas()
    out.p = [row[:] for row in cv.p]
    return out


# ------------------------------------------------------------------ rocks
# id: colour ramp (dark -> light), noise stretch (x, y), contrast, gap colour, surface detail
ROCKS = {
    "limestone": {"ramp": ["#8f8670", "#b2a98f", "#c9c1a6", "#ddd6bd", "#e9e3cc"], "stretch": (1.0, 2.0),
                  "contrast": 1.1, "gap": "#4a4232", "detail": "fossils"},
    "shale": {"ramp": ["#2b2d31", "#3d4045", "#4f5359", "#61666b", "#757a7d"], "stretch": (0.5, 3.0),
              "contrast": 1.2, "gap": "#141516", "detail": "laminae"},
    "chalk": {"ramp": ["#b9b7ad", "#cfcdc3", "#dfddd5", "#ebeae3", "#f7f6f1"], "stretch": (1.0, 1.0),
              "contrast": 0.9, "gap": "#77725f", "detail": "cracks"},
    "flint": {"ramp": ["#bdb9aa", "#d2cebf", "#e1ddd0", "#ebe8de", "#f4f1e8"], "stretch": (1.0, 1.0),
              "contrast": 0.8, "gap": "#4f4b42", "detail": "nodules"},
    "laterite": {"ramp": ["#4f2213", "#6e311b", "#8c4224", "#a8552f", "#bf6c40"], "stretch": (1.0, 1.0),
                 "contrast": 1.3, "gap": "#2a140b", "detail": "pores"},
    "quartzite": {"ramp": ["#8a7470", "#a68d87", "#bea79f", "#d4c1b8", "#e8dad1"], "stretch": (1.5, 1.0),
                  "contrast": 0.9, "gap": "#4e403c", "detail": "sparkle"},
    "gneiss": {"ramp": ["#353538", "#55555a", "#7a7a7f", "#a2a2a5", "#cfcfd0"], "stretch": (1.0, 1.0),
               "contrast": 1.0, "gap": "#1d1d1f", "detail": "bands"},
    "conglomerate": {"ramp": ["#5e4e39", "#77654b", "#8f7c5f", "#a69273", "#b9a688"], "stretch": (1.0, 1.0),
                     "contrast": 0.9, "gap": "#33291d", "detail": "clasts"},
}
# pebbles of each rock sit on this sandy soil
PEBBLE_SOIL = ["#5a4a36", "#6e5c45", "#806d53", "#917e62"]
# loose clasts cemented in the conglomerate: quartz, flint, sandstone, granite, shale
CLAST_RAMPS = [["#b8b0a2", "#d8d2c6", "#efebe2"], ["#2b313b", "#4f5764", "#6e7684"], ["#a8865a", "#c4a271", "#dcc08f"],
               ["#7d5a4e", "#a37a68", "#c49d8a"], ["#45484d", "#62666b", "#7e8287"]]
FLINT_RAMP = ["#1c2129", "#2b313b", "#3b424d", "#4f5764", "#6a7280"]
MOSS_RAMP = ["#2f4519", "#40591f", "#557229", "#6b8a34", "#83a043"]
SOIL = hexc("#3e3022")


def rock_base(rid):
    """Natural rock surface: the plain block, and the material the stacked stones are cut from."""
    r = ROCKS[rid]
    n = Noise(rid, stretch=r["stretch"])
    fine = Noise(rid + "fine", periods=(16,), weights=(1.0,))
    rnd = random.Random(rid + "spots")
    cv = paint(lambda x, y: ramp(r["ramp"], contrast(n(x, y) * 0.75 + fine(x, y) * 0.25, r["contrast"])))
    detail = r["detail"]
    if detail == "laminae":  # thin bedding planes, broken in places, and rusty iron specks
        for y in (2, 6, 9, 13):
            for x in range(N):
                if rnd.random() < 0.8:
                    cv.set(x, y, shade(cv.get(x, y), 0.7))
                    cv.set(x, (y + 1) % N, shade(cv.get(x, (y + 1) % N), 1.12))
        for _ in range(3):
            cv.set(rnd.randrange(N), rnd.randrange(N), hexc("#7a5a3a"))
    elif detail == "fossils":  # small shell fragments and pores
        for _ in range(1):
            x, y = rnd.randrange(N), rnd.randrange(N)
            for dx, dy in ((0, 0), (1, -1), (2, -1), (3, 0)):
                cv.set((x + dx) % N, (y + dy) % N, hexc("#f2ecd8"))
            cv.set((x + 1) % N, y % N, hexc("#8a7f66")); cv.set((x + 2) % N, y % N, hexc("#8a7f66"))
        for _ in range(5):
            cv.set(rnd.randrange(N), rnd.randrange(N), shade(hexc(r["ramp"][1]), 0.92))
    elif detail == "cracks":  # hairline cracks and grey specks
        x, y = rnd.randrange(N), rnd.randrange(N)
        for _ in range(9):
            cv.set(x % N, y % N, shade(cv.get(x % N, y % N), 0.82))
            x += rnd.choice((1, 1, 0)); y += rnd.choice((1, 0, -1))
        for _ in range(5):
            cv.set(rnd.randrange(N), rnd.randrange(N), hexc("#9e9b90"))
    elif detail == "pores":  # laterite: iron-rich clay rock full of small dark holes and yellow ochre streaks
        for _ in range(16):
            x, y = rnd.randrange(N), rnd.randrange(N)
            cv.set(x, y, hexc("#2a140b")); cv.set(x, (y + 1) % N, shade(cv.get(x, (y + 1) % N), 1.15))
        for _ in range(4):
            cv.set(rnd.randrange(N), rnd.randrange(N), hexc("#c99a4a"))
    elif detail == "sparkle":  # quartzite: sugary grains that catch the light
        for _ in range(14):
            cv.set(rnd.randrange(N), rnd.randrange(N), hexc("#f6eee8"))
        for _ in range(5):
            cv.set(rnd.randrange(N), rnd.randrange(N), hexc("#7c6662"))
    elif detail == "bands":  # gneiss: wavy dark and light mineral bands
        wav = Noise(rid + "wave", periods=(2, 4), weights=(0.7, 0.3))
        for y in range(N):
            for x in range(N):
                b = math.sin((y + x * 0.25) * (2 * math.pi / 8) + wav(x, y) * 3.0)
                c = cv.get(x, y)
                cv.set(x, y, shade(c, 0.62) if b > 0.55 else (shade(c, 1.22) if b < -0.7 else c))
    elif detail == "clasts":  # conglomerate: rounded pebbles of other rocks cemented in sandy matrix
        for i in range(9):
            cr = CLAST_RAMPS[rnd.randrange(len(CLAST_RAMPS))]
            cx, cy = rnd.uniform(0, N), rnd.uniform(0, N)
            rx, ry = rnd.uniform(1.2, 2.6), rnd.uniform(1.0, 2.0)
            for y in range(N):
                for x in range(N):
                    dx = min(abs(x + 0.5 - cx), N - abs(x + 0.5 - cx)) / rx
                    dy = min(abs(y + 0.5 - cy), N - abs(y + 0.5 - cy)) / ry
                    if dx * dx + dy * dy <= 1:
                        lit = (x + 0.5 < cx) + (y + 0.5 < cy)
                        cv.set(x, y, hexc(cr[min(2, lit)]))
    elif detail == "nodules":  # dark flint nodules with a white cortex rim and a glossy point
        fl = Noise(rid + "nod", periods=(4, 8), weights=(0.7, 0.3))
        wobble = Noise(rid + "wob", periods=(4, 8), weights=(0.6, 0.4))
        for (cx, cy, rx, ry) in ((5.0, 5.0, 4.4, 3.0), (12.0, 11.5, 3.6, 3.8)):
            for y in range(N):
                for x in range(N):
                    dx = min(abs(x - cx), N - abs(x - cx)) / rx
                    dy = min(abs(y - cy), N - abs(y - cy)) / ry
                    d = math.hypot(dx, dy) + (wobble(x, y) - 0.5) * 0.7
                    if d < 0.78:
                        cv.set(x, y, ramp(FLINT_RAMP, fl(x, y) * 0.9 + (0.2 if (x < cx and y < cy) else 0)))
                    elif d < 1.05:
                        cv.set(x, y, hexc("#ece7da"))
            cv.set(int(cx - rx / 3) % N, int(cy - ry / 3) % N, hexc("#9aa3b2"))
    return cv


def stones(base, cells, gap, tone_seed, width, light, dark):
    """Stones cut from the rock texture: each Voronoi cell is one stone and the borders are gaps. Top/left edges
    catch the light and bottom/right edges are in shadow, so every stone reads as a lump."""
    rnd = random.Random(tone_seed)
    tones = [0.86 + 0.24 * rnd.random() for _ in cells.seeds]
    cv = Canvas()
    for y in range(N):
        for x in range(N):
            if cells.border(x, y, width):
                cv.set(x, y, shade(gap, 0.85 + 0.3 * rnd.random()))
                continue
            o = cells.owner[y][x]
            c = shade(base.get(x, y), tones[o])
            if cells.at(x, y - 1) != o or cells.border(x, y - 1, width) or cells.at(x - 1, y) != o or cells.border(x - 1, y, width):
                c = shade(c, light)
            if cells.at(x, y + 1) != o or cells.border(x, y + 1, width) or cells.at(x + 1, y) != o or cells.border(x + 1, y, width):
                c = shade(c, dark)
            cv.set(x, y, c)
    return cv


def courses(seed):
    """Dry-laid wall layout: horizontal courses 3-5 px high, each split into stones 4-9 px long with an offset, so
    the joints never line up. Returns owner[y][x] = stone index or -1 for a joint (wraps on both axes)."""
    rnd = random.Random(seed)
    heights = rnd.choice(([4, 3, 5, 4], [5, 3, 4, 4], [3, 4, 4, 5], [4, 4, 3, 5]))
    owner = [[-1] * N for _ in range(N)]
    stone = 0
    y0 = 0
    for h in heights:
        cuts, x = [], rnd.randrange(N)
        total = 0
        while total < N:
            w = rnd.randint(4, 9)
            if N - total - w < 4:
                w = N - total
            cuts.append((x + total, w))
            total += w
        for (sx, w) in cuts:
            for yy in range(y0, y0 + h - 1):  # last row of the course is the joint
                for xx in range(sx, sx + w - 1):  # last column of the stone is the joint
                    owner[yy % N][xx % N] = stone
            # knock off the corners so the stones look rounded
            for (cx, cy) in ((sx, y0), (sx + w - 2, y0), (sx, y0 + h - 2), (sx + w - 2, y0 + h - 2)):
                if rnd.random() < 0.75:
                    owner[cy % N][cx % N] = -1
            stone += 1
        y0 += h
    return owner, stone


def laid(base, owner, count, gap, seed):
    """Stones from the rock texture laid in courses: lit top edge, shadowed bottom edge, own tone per stone."""
    rnd = random.Random(seed)
    tones = [0.84 + 0.26 * rnd.random() for _ in range(count)]
    cv = Canvas()
    own = lambda x, y: owner[y % N][x % N]  # noqa: E731
    for y in range(N):
        for x in range(N):
            o = own(x, y)
            if o < 0:
                cv.set(x, y, shade(gap, 0.8 + 0.35 * rnd.random()))
                continue
            c = shade(base.get(x, y), tones[o])
            if own(x, y - 1) != o:
                c = shade(c, 1.16)
            elif own(x - 1, y) != o:
                c = shade(c, 1.06)
            if own(x, y + 1) != o:
                c = shade(c, 0.7)
            elif own(x + 1, y) != o:
                c = shade(c, 0.86)
            cv.set(x, y, c)
    return cv


def rock_textures(rid):
    r = ROCKS[rid]
    base = rock_base(rid)
    owner, count = courses(rid + "courses")
    stacked = laid(base, owner, count, hexc(r["gap"]), rid + "t1")
    flag = stones(base, Cells(rid + "flag", 5), mixc(hexc(r["gap"]), SOIL, 0.6), rid + "t2", 0.45, 1.07, 0.88)
    # moss grows in the joints and on the top edge of the stones
    moss = copy(stacked)
    mn = Noise(rid + "moss", periods=(2, 4, 8), weights=(0.45, 0.35, 0.2))
    rnd = random.Random(rid + "moss")
    for y in range(N):
        for x in range(N):
            joint = owner[y][x] < 0
            top = not joint and owner[(y - 1) % N][x] != owner[y][x]
            v = mn(x, y) + (0.18 if joint else 0.0) + (0.1 if top else 0.0)
            if v > 0.72:
                moss.set(x, y, ramp(MOSS_RAMP, (v - 0.72) / 0.28 + 0.2 * rnd.random()))
    return {rid: base, f"{rid}_stacked": stacked, f"{rid}_flagstone": flag, f"mossy_{rid}_stacked": moss}


def pebbles(rid):
    """Loose rounded pebbles of the rock lying on sandy soil (the top of the thin pebble layer)."""
    r = ROCKS[rid]
    rnd = random.Random(rid + "pebbles")
    soil = Noise(rid + "soil", periods=(4, 8, 16), weights=(0.4, 0.3, 0.3))
    cv = paint(lambda x, y: ramp(PEBBLE_SOIL, soil(x, y)))
    for _ in range(11):
        cx, cy = rnd.uniform(0, N), rnd.uniform(0, N)
        rx, ry = rnd.uniform(1.0, 2.4), rnd.uniform(0.9, 1.8)
        tone = 0.3 + 0.5 * rnd.random()
        pr = FLINT_RAMP if rid == "flint" else r["ramp"]
        for y in range(N):
            for x in range(N):
                dx = (x + 0.5 - cx); dx = (dx + N / 2) % N - N / 2
                dy = (y + 0.5 - cy); dy = (dy + N / 2) % N - N / 2
                d = (dx / rx) ** 2 + (dy / ry) ** 2
                if d <= 1:
                    v = tone + (0.3 if dx < 0 and dy < 0 else 0) - (0.25 if dx > 0 and dy > 0 else 0)
                    cv.set(x, y, ramp(pr, v))
                elif d <= 1.6 and dy > 0:
                    cv.set(x, y, shade(cv.get(x, y), 0.75))  # shadow on the soil
    return cv


# ------------------------------------------------------------------ thatch (palha)
THATCH_RAMP = ["#4f3f20", "#75602f", "#957c40", "#b39752", "#cdb269"]


def thatch():
    """Courses of straw bundles: thin vertical strands; each course overhangs the one below (shadow under the
    lip, sun-bleached tips at the bottom of every course)."""
    strands = Noise("thatch", periods=(16, 8), weights=(0.7, 0.3), stretch=(1.0, 0.25))
    rnd = random.Random("thatch")

    def px(x, y):
        course, row = y // 4, y % 4
        v = strands((x + course * 5) % N, y) * 0.8 + 0.2 * rnd.random()
        if row == 0:
            v = v * 0.55  # shadow under the course above
        elif row == 3:
            v = v * 0.6 + 0.4  # bleached tips
        return ramp(THATCH_RAMP, v)
    return paint(px)


def thatch_top():
    strands = Noise("thatch_top", periods=(16, 8), weights=(0.6, 0.4), stretch=(0.25, 1.0))
    rnd = random.Random("thatch_top")
    return paint(lambda x, y: ramp(THATCH_RAMP, strands(x, y) * 0.8 + 0.2 * rnd.random()))


def straw_mat():
    """Hand-woven straw mat: over-under strips 4 px wide, each strip with its own strands."""
    n = Noise("mat", periods=(16,), weights=(1.0,))
    rnd = random.Random("mat")

    def px(x, y):
        horizontal = ((x // 4) + (y // 4)) % 2 == 0
        k = (y % 4) if horizontal else (x % 4)
        v = 0.3 + 0.35 * n(x, y) + (0.18 if k in (1, 2) else -0.12) + 0.08 * rnd.random()
        return ramp(THATCH_RAMP, v)
    return paint(px)


# ------------------------------------------------------------------ wattle and daub (pau a pique)
DAUB_RAMP = ["#5e4a34", "#7c644a", "#957b5c", "#ab9170", "#bea583"]
STICK_RAMP = ["#3a2814", "#54391d", "#6e4d2a", "#87623a"]


def wattle_daub():
    """Clay plaster smeared by hand over woven sticks: lumpy, with a drying crack and straw fibres."""
    n = Noise("daub", periods=(2, 4, 8), weights=(0.4, 0.35, 0.25))
    rnd = random.Random("daub")
    cv = paint(lambda x, y: ramp(DAUB_RAMP, contrast(n(x, y), 1.4)))
    for _ in range(9):  # straw fibres in the clay
        x, y = rnd.randrange(N), rnd.randrange(N)
        for i in range(rnd.choice((2, 3))):
            cv.set((x + i) % N, y, hexc("#c8b27a"))
    x, y = rnd.randrange(N), rnd.randrange(N)
    for _ in range(12):  # drying crack
        cv.set(x % N, y % N, hexc("#4a3826"))
        x += rnd.choice((1, 1, 0)); y += rnd.choice((1, 0, 0, -1))
    return cv


# ------------------------------------------------------------------ bone fence (cerca de osso)
BONE_RAMP = ["#9c9178", "#bdb296", "#d6ccb0", "#e6dec6", "#f3eedf"]


def bone_fence():
    """Long bones: porous, yellowed surface, a rounded highlight down each bone, sinew lashings."""
    n = Noise("bone", periods=(4, 16), weights=(0.6, 0.4), stretch=(0.5, 1.5))
    rnd = random.Random("bone")
    cv = paint(lambda x, y: ramp(BONE_RAMP, 0.2 + 0.5 * (1 - abs((x % 8) - 3.5) / 4.5) + 0.3 * n(x, y)))
    for _ in range(10):  # pores
        cv.set(rnd.randrange(N), rnd.randrange(N), hexc("#8a7f66"))
    for y in (3, 4, 11, 12):
        for x in range(N):
            cv.set(x, y, mixc(hexc("#5e3a20"), hexc("#8a5a34"), ((x + y) % 3) / 3))
    return cv


# ------------------------------------------------------------------ hide screen (painel de couro)
HIDE_RAMP = ["#5a3a1e", "#76502b", "#8f653a", "#a87b4b", "#bf915e"]


def hide_screen():
    """Scraped, stretched hide: uneven thickness (light and dark patches), a vein, stitched to the frame posts."""
    n = Noise("hide", periods=(2, 4, 8), weights=(0.5, 0.3, 0.2))
    rnd = random.Random("hide")
    cv = paint(lambda x, y: ramp(HIDE_RAMP, contrast(n(x, y), 1.3)))
    x, y = 4, 2
    for _ in range(10):
        cv.set(x % N, y % N, shade(cv.get(x % N, y % N), 0.84))
        x += rnd.choice((0, 1)); y += 1
    for i in range(N):
        cv.set(0, i, ramp(STICK_RAMP, 0.7)); cv.set(15, i, ramp(STICK_RAMP, 0.3))
    for i in range(1, N, 3):
        cv.set(1, i, hexc("#d8c9a4")); cv.set(14, i, hexc("#d8c9a4"))
    return cv


def hide_screen_edge():
    return paint(lambda x, y: ramp(STICK_RAMP, 0.3 + 0.4 * ((x % 4) in (1, 2))))


# ------------------------------------------------------------------ prehistoric woods
# tree id: bark ramp, bark style, wood ramp (stripped / planks), leaf ramp, leaf style
WOODS = {
    # Araucaria (monkey puzzle / Parana pine): grey-brown bark in scaly horizontal rings; pale yellow wood;
    # dark glossy green, stiff spiky scale leaves
    "araucaria": {"bark": ["#2e241b", "#43352a", "#5a4a3b", "#706050", "#857563"], "bark_style": "rings",
                  "wood": ["#9c8058", "#b8996a", "#cdb07e", "#dcc294", "#e8d3a8"],
                  "leaf": ["#14281a", "#1f3a22", "#2c4f2c", "#3d6638", "#527d46"], "leaf_style": "spiky"},
    # Ginkgo: grey, deeply furrowed bark; pale cream wood; bright fan-shaped leaves
    "ginkgo": {"bark": ["#2f2c27", "#48433b", "#615a50", "#7a7267", "#938a7e"], "bark_style": "furrows",
               "wood": ["#a89470", "#c2ad86", "#d6c29a", "#e3d1ab", "#eedfbd"],
               "leaf": ["#3b5a1c", "#557a26", "#6f9631", "#8cb03f", "#a8c858"], "leaf_style": "fans"},
    # Metasequoia (dawn redwood): red-brown fibrous bark peeling in long strips; pinkish heartwood;
    # soft feathery light-green needles
    "metasequoia": {"bark": ["#3a1c10", "#55291a", "#723a25", "#8f4c32", "#a86142"], "bark_style": "fibres",
                    "wood": ["#8e5a42", "#a86d52", "#bf8266", "#cf977b", "#dcab91"],
                    "leaf": ["#2b4a22", "#3d632c", "#517c36", "#679444", "#7fab55"], "leaf_style": "feathery"},
}
LASHING = ["#4a3a22", "#6e5a3a", "#8f7a55", "#b39d74"]


def bark(tid):
    w = WOODS[tid]
    style = w["bark_style"]
    rnd = random.Random(tid + "bark")
    if style == "rings":  # scaly plates in horizontal bands with dark leaf scars
        n = Noise(tid + "b", periods=(4, 16), weights=(0.5, 0.5), stretch=(1.0, 1.0))
        cv = paint(lambda x, y: ramp(w["bark"], contrast(n(x, y), 1.3) * (0.6 if y % 4 == 3 else 1.0) + (0.12 if y % 4 == 0 else 0)))
        for _ in range(6):
            x, y = rnd.randrange(N), rnd.randrange(N)
            cv.set(x, y, hexc(w["bark"][0]))
        return cv
    if style == "furrows":  # deep vertical furrows, ridges catching light
        n = Noise(tid + "b", periods=(8, 16), weights=(0.6, 0.4), stretch=(1.0, 0.25))
        fine = Noise(tid + "f", periods=(16,), weights=(1.0,))
        return paint(lambda x, y: ramp(w["bark"], contrast(n(x, y) * 0.8 + fine(x, y) * 0.2, 1.7)))
    # fibres: long stringy strips, some peeling (lighter edge)
    n = Noise(tid + "b", periods=(16, 8), weights=(0.6, 0.4), stretch=(1.0, 0.125))
    cv = paint(lambda x, y: ramp(w["bark"], contrast(n(x, y), 1.5)))
    for _ in range(4):
        x, y = rnd.randrange(N), rnd.randrange(N)
        for i in range(rnd.randint(3, 6)):
            cv.set(x, (y + i) % N, hexc(w["bark"][4]))
            cv.set((x + 1) % N, (y + i) % N, hexc(w["bark"][0]))
    return cv


def log_top(tid, stripped=False):
    """Cut end: growth rings around an off-centre pith, radial drying cracks; bark ring unless stripped."""
    w = WOODS[tid]
    rnd = random.Random(tid + "top")
    wob = Noise(tid + "rw", periods=(2, 4), weights=(0.7, 0.3))

    def px(x, y):
        d = math.hypot(x - 7.2, y - 7.8) + (wob(x, y) - 0.5) * 1.2
        edge = max(abs(x - 7.5), abs(y - 7.5))
        if not stripped and edge > 6.6:
            return ramp(w["bark"], 0.35 + 0.3 * rnd.random())
        ring = 0.5 + 0.5 * math.cos(d * 2.4)
        return ramp(w["wood"], 0.15 + 0.6 * ring + 0.12 * rnd.random() - (0.15 if d < 1.2 else 0))
    cv = paint(px)
    x, y = 7.2, 7.8
    ang = rnd.uniform(0, math.tau)
    for r in range(1, 7):  # one radial drying crack
        cv.set(int(x + math.cos(ang) * r), int(y + math.sin(ang) * r), hexc(w["wood"][0]))
    return cv


def stripped_side(tid):
    """Debarked trunk: long fibres with the draw-knife marks."""
    w = WOODS[tid]
    n = Noise(tid + "s", periods=(16, 8), weights=(0.6, 0.4), stretch=(1.0, 0.125))
    cv = paint(lambda x, y: ramp(w["wood"], 0.2 + 0.65 * n(x, y)))
    rnd = random.Random(tid + "knife")
    for _ in range(3):
        x, y = rnd.randrange(N), rnd.randrange(N)
        for i in range(4):
            cv.set((x + i) % N, (y + (i // 2)) % N, shade(cv.get((x + i) % N, (y + (i // 2)) % N), 0.85))
    return cv


def hewn_planks(tid):
    """Planks split and dressed with an adze: four boards of uneven height, scalloped tool marks, no nails."""
    w = WOODS[tid]
    rnd = random.Random(tid + "hewn")
    n = Noise(tid + "h", periods=(16, 8), weights=(0.5, 0.5), stretch=(0.25, 1.0))
    seams = [3, 7, 12, 15]
    tones = [0.85 + 0.25 * rnd.random() for _ in seams]

    def px(x, y):
        board = next(i for i, s in enumerate(seams) if y <= s)
        if y == seams[board] and not (board == 1 and 6 <= x <= 8):
            return ramp(w["wood"], 0.02)
        scallop = 0.22 * math.cos((x + board * 3) * (2 * math.pi / 5))  # adze strokes, scalloped hollows
        v = (0.3 + 0.45 * n(x, y) + scallop) * tones[board]
        if y == (seams[board - 1] + 1 if board else 0):
            v += 0.1
        return ramp(w["wood"], v)
    cv = paint(px)
    for i, s in enumerate(seams):  # a drying crack along the grain of each board
        x0 = rnd.randrange(N)
        y = s - 2 if s - 2 >= 0 else 0
        for k in range(rnd.randint(3, 6)):
            cv.set((x0 + k) % N, y, ramp(w["wood"], 0.05))
    return cv


def leaves(tid):
    """Foliage with gaps (transparent), clustered the way the real leaves grow."""
    w = WOODS[tid]
    style = w["leaf_style"]
    rnd = random.Random(tid + "leaf")
    n = Noise(tid + "l", periods=(4, 8, 16), weights=(0.4, 0.35, 0.25))
    cv = Canvas()
    for y in range(N):
        for x in range(N):
            v = n(x, y)
            if v < 0.36:
                continue  # gap
            cv.set(x, y, ramp(w["leaf"], contrast(v, 1.6) + 0.1 * rnd.random()))
    if style == "spiky":  # stiff overlapping scale leaves: diagonal bright points
        for _ in range(14):
            x, y = rnd.randrange(N), rnd.randrange(N)
            cv.set(x, y, hexc(w["leaf"][4])); cv.set((x + 1) % N, (y + 1) % N, hexc(w["leaf"][1]))
    elif style == "fans":  # fan-shaped leaves: little bright wedges
        for _ in range(7):
            x, y = rnd.randrange(N), rnd.randrange(N)
            for dx in (-1, 0, 1):
                cv.set((x + dx) % N, y, hexc(w["leaf"][4]))
            cv.set(x, (y + 1) % N, hexc(w["leaf"][3]))
    else:  # feathery: rows of tiny needles along twigs
        for _ in range(5):
            x, y = rnd.randrange(N), rnd.randrange(N)
            for i in range(5):
                cv.set((x + i) % N, y, hexc(w["leaf"][1]))
                cv.set((x + i) % N, (y - 1) % N if i % 2 else (y + 1) % N, hexc(w["leaf"][4]))
    return cv


def sapling(tid):
    """Young tree, drawn on transparent background: thin stem and the crown shape of its species."""
    w = WOODS[tid]
    cv = Canvas()
    stem = hexc(w["bark"][3])
    for y in range(8, 16):
        cv.set(7, y, stem)
    leaf = lambda k: hexc(w["leaf"][k])  # noqa: E731
    style = w["leaf_style"]
    if style == "spiky":  # araucaria seedling: whorls of stiff spiky branches, tiered
        for y, half in ((3, 2), (6, 4), (9, 5)):
            for dx in range(-half, half + 1):
                cv.set(7 + dx, y, leaf(2 if abs(dx) < half else 1))
                if abs(dx) == half:
                    cv.set(7 + dx, y - 1, leaf(4))
        for y in range(1, 10):
            cv.set(7, y, stem if y > 3 else leaf(3))
    elif style == "fans":  # ginkgo: a few fan leaves on a twig
        for (cx, cy) in ((4, 6), (10, 5), (7, 2), (5, 10), (10, 9)):
            for dx in (-2, -1, 0, 1, 2):
                cv.set(cx + dx, cy, leaf(3 if dx < 0 else 2))
            for dx in (-1, 0, 1):
                cv.set(cx + dx, cy + 1, leaf(2))
            cv.set(cx, cy + 2, leaf(1))
        for y in range(4, 16):
            cv.set(7, y, stem)
    else:  # metasequoia: soft cone of feathery needles
        for y in range(1, 12):
            half = max(0, (y - 1) // 2)
            for dx in range(-half, half + 1):
                if (dx + y) % 2 == 0 or abs(dx) < half:
                    cv.set(7 + dx, y, leaf(3 if dx < 0 else 1))
    cv.outline(0.5)
    return cv


def door(tid, part):
    """Door of split logs lashed to two cross-bars with rawhide; a gap between logs shows light (transparent)."""
    w = WOODS[tid]
    rnd = random.Random(tid + part)
    n = Noise(tid + "d" + part, periods=(16, 8), weights=(0.6, 0.4), stretch=(1.0, 0.125))
    cv = Canvas()
    for y in range(N):
        for x in range(N):
            if x in (4, 11) and rnd.random() < 0.5:
                continue  # crack between logs
            col = x // 4
            v = 0.2 + 0.55 * n(x, y) + (0.15 if x % 4 == 1 else 0) - (0.15 if x % 4 == 3 else 0)
            cv.set(x, y, ramp(w["wood"], v - 0.05 * col))
    bar = 3 if part == "top" else 11
    for x in range(N):  # cross-bar and lashing
        cv.set(x, bar, ramp(w["bark"], 0.6)); cv.set(x, bar + 1, ramp(w["bark"], 0.3))
        if x % 4 == 1:
            cv.set(x, bar - 1, hexc(LASHING[2])); cv.set(x, bar + 2, hexc(LASHING[1]))
    if part == "top":
        for x in range(N):  # sharpened tops of the logs
            if x % 4 in (0, 3):
                cv.p[0][x] = None
    return cv


def trapdoor(tid):
    """Hatch of lashed round poles, two cross-bars."""
    w = WOODS[tid]
    n = Noise(tid + "t", periods=(16, 8), weights=(0.6, 0.4), stretch=(0.125, 1.0))
    cv = Canvas()
    for y in range(N):
        for x in range(N):
            if y % 4 == 3 and x not in (3, 4, 11, 12):
                continue  # gaps between poles
            v = 0.2 + 0.6 * n(x, y) + (0.15 if y % 4 == 0 else 0)
            cv.set(x, y, ramp(w["wood"], v))
    for y in range(N):
        for x in (3, 4, 11, 12):
            cv.set(x, y, ramp(w["bark"], 0.5 if x in (3, 11) else 0.3))
    return cv


def door_item(tid):
    """Inventory sprite: the whole door squeezed to 8x16."""
    top, bottom = door(tid, "top"), door(tid, "bottom")
    cv = Canvas()
    for y in range(N):
        src = top if y < 8 else bottom
        sy = (y % 8) * 2
        for x in range(4, 12):
            cv.set(x, y, src.get((x - 4) * 2, sy))
    return cv


def branch_fence(tid):
    """Fence of whole branches: bark with knots and a lighter cut surface."""
    cv = bark(tid)
    rnd = random.Random(tid + "branch")
    for _ in range(3):
        x, y = rnd.randrange(N), rnd.randrange(N)
        cv.set(x, y, ramp(WOODS[tid]["wood"], 0.6)); cv.set((x + 1) % N, y, ramp(WOODS[tid]["bark"], 0.0))
    return cv


def wood_textures(tid):
    out = {f"{tid}_log": bark(tid), f"{tid}_log_top": log_top(tid), f"stripped_{tid}_log": stripped_side(tid),
           f"stripped_{tid}_log_top": log_top(tid, True), f"{tid}_hewn_planks": hewn_planks(tid),
           f"{tid}_leaves": leaves(tid), f"{tid}_sapling": sapling(tid), f"{tid}_lashed_door_top": door(tid, "top"),
           f"{tid}_lashed_door_bottom": door(tid, "bottom"), f"{tid}_lashed_trapdoor": trapdoor(tid),
           f"{tid}_branch_fence": branch_fence(tid)}
    return out


def wood_items(tid):
    """Inventory sprites (textures/item) of the wood blocks that are not drawn as blocks."""
    return {f"{tid}_lashed_door": door_item(tid)}


OTHER = {
    "thatch": thatch, "thatch_top": thatch_top, "straw_mat": straw_mat, "wattle_and_daub": wattle_daub,
    "bone_fence": bone_fence,
    "hide_screen": hide_screen, "hide_screen_edge": hide_screen_edge,
}


def build():
    out = {}
    for rid in ROCKS:
        out.update(rock_textures(rid))
        out[f"{rid}_pebbles"] = pebbles(rid)
    for name, fn in OTHER.items():
        out[name] = fn()
    for tid in WOODS:
        out.update(wood_textures(tid))
    for name, cv in out.items():
        cv.save(os.path.join(TEX, f"{name}.png"))
    for tid in WOODS:
        for name, cv in wood_items(tid).items():
            cv.save(os.path.join(os.path.dirname(TEX), "item", f"{name}.png"))
    return out


def preview(path, names):
    """Each texture upscaled 4x and tiled 2x2 (so seams show), with its name under it."""
    from PIL import ImageDraw
    tile = 16 * 4
    cell_w, cell_h = tile * 2 + 16, tile * 2 + 26
    cols = 6
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w, rows * cell_h), (44, 44, 50, 255))
    draw = ImageDraw.Draw(sheet)
    for i, name in enumerate(names):
        im = Image.open(os.path.join(TEX, f"{name}.png")).resize((tile, tile), Image.NEAREST)
        ox, oy = (i % cols) * cell_w + 8, (i // cols) * cell_h + 6
        for tx in range(2):
            for ty in range(2):
                sheet.alpha_composite(im, (ox + tx * tile, oy + ty * tile))
        draw.text((ox, oy + tile * 2 + 4), name, fill=(230, 230, 230, 255))
    sheet.save(path)


if __name__ == "__main__":
    textures = build()
    if len(sys.argv) > 1:
        preview(sys.argv[1], list(textures))
    print(len(textures), "block textures written to", TEX)
