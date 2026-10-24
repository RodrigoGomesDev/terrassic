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
    # Taxodium (swamp / bald cypress): grey-brown stringy bark, light brown wood, soft flat sprays of needles
    "taxodium": {"bark": ["#2c2621", "#433a32", "#5b5045", "#736659", "#8a7c6d"], "bark_style": "fibres",
                 "wood": ["#9a7650", "#b08b62", "#c49f75", "#d4b289", "#e0c39e"],
                 "leaf": ["#2a3f1e", "#3a5428", "#4c6b31", "#5f823c", "#739848"], "leaf_style": "feathery"},
    # Tree fern: trunk wrapped in old frond bases and roots (no bark), fibrous dark wood, big arching fronds
    "tree_fern": {"bark": ["#1e150d", "#2f2215", "#43321f", "#58432b", "#6d5537"], "bark_style": "frond_bases",
                  "wood": ["#5a4128", "#6e5233", "#83623e", "#98744b", "#aa8659"],
                  "leaf": ["#24401a", "#335a22", "#46732c", "#5b8c38", "#73a447"], "leaf_style": "fronds"},
    # Sabal palm: trunk criss-crossed by the stubs of old leaf stalks; pale fibrous wood; stiff fan leaves
    "sabal": {"bark": ["#3a3024", "#54473a", "#6e6150", "#887a66", "#a0927c"], "bark_style": "frond_bases",
              "wood": ["#a08a64", "#b8a07a", "#ccb48c", "#dcc6a0", "#e8d6b4"],
              "leaf": ["#2a3e1a", "#3c5824", "#507230", "#668c3c", "#7ea64c"], "leaf_style": "palm"},
    # Magnolia, one of the first flowering trees: smooth grey bark, creamy wood, glossy dark leaves, white flowers
    "magnolia": {"bark": ["#3c3a36", "#55524c", "#6e6a62", "#878278", "#a09a8e"], "bark_style": "smooth",
                 "wood": ["#b09a74", "#c6b08a", "#d8c49e", "#e6d4b2", "#f0e2c4"],
                 "leaf": ["#16301c", "#224428", "#305a34", "#427242", "#588a52"], "leaf_style": "broad",
                 "flowers": ["#e8e0d8", "#f6f0ea", "#d8a8b8"]},
    # Podocarpus: red-brown stringy bark, orange-brown wood, long narrow dark leaves
    "podocarpus": {"bark": ["#3a2416", "#523321", "#6c442d", "#86573a", "#9c6a48"], "bark_style": "fibres",
                   "wood": ["#a0703e", "#b8844c", "#cc985c", "#dcac70", "#e8c088"],
                   "leaf": ["#1c3418", "#284820", "#365e2a", "#467436", "#5a8a44"], "leaf_style": "feathery"},
    # Platanus (plane tree, known from Cretaceous leaves): bark peeling in patches of olive, grey and cream
    "platanus": {"bark": ["#4a4636", "#6a654e", "#8c866a", "#aea886", "#cac4a2"], "bark_style": "plates",
                 "wood": ["#a88a68", "#c0a07c", "#d2b490", "#e0c6a4", "#eed6b8"],
                 "leaf": ["#2c4a1c", "#3e6226", "#527c30", "#68963c", "#80ae4c"], "leaf_style": "broad"},
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
    if style == "frond_bases":  # tree fern: diamond pattern of old frond stalks and hairy roots
        n = Noise(tid + "b", periods=(4, 16), weights=(0.5, 0.5))
        cv = paint(lambda x, y: ramp(w["bark"], contrast(n(x, y), 1.2) * 0.8))
        for y in range(N):
            for x in range(N):
                if (x + y) % 6 == 0 or (x - y) % 6 == 0:
                    cv.set(x, y, hexc(w["bark"][4]) if (x + 2 * y) % 4 else hexc(w["bark"][3]))
        return cv
    if style == "smooth":  # thin smooth bark: soft mottling and small horizontal lenticels
        n = Noise(tid + "b", periods=(2, 4), weights=(0.6, 0.4))
        cv = paint(lambda x, y: ramp(w["bark"], 0.35 + 0.4 * n(x, y)))
        for _ in range(7):
            x, y = rnd.randrange(N), rnd.randrange(N)
            cv.set(x, y, hexc(w["bark"][1])); cv.set((x + 1) % N, y, hexc(w["bark"][1]))
        return cv
    if style == "plates":  # bark flaking off in patches (camouflage), each patch its own tone
        cells = Cells(tid + "plates", 9)
        tones = [rnd.uniform(0.15, 0.95) for _ in cells.seeds]
        return paint(lambda x, y: ramp(w["bark"], tones[cells.at(x, y)] - (0.12 if cells.border(x, y, 0.8) else 0)))
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
    elif style == "broad":  # broad glossy leaves: bright highlight and dark midrib, a few flowers (magnolia)
        for _ in range(8):
            x, y = rnd.randrange(N), rnd.randrange(N)
            cv.set(x, y, hexc(w["leaf"][4])); cv.set((x + 1) % N, y, hexc(w["leaf"][3]))
            cv.set(x, (y + 1) % N, hexc(w["leaf"][1]))
        for _ in range(3 if "flowers" in w else 0):
            x, y = rnd.randrange(N), rnd.randrange(N)
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                cv.set((x + dx) % N, (y + dy) % N, hexc(w["flowers"][(dx + dy) % 2]))
            cv.set((x + 1) % N, (y + 1) % N, hexc(w["flowers"][2]))
    elif style == "palm":  # fan palm: stiff strap-like segments radiating from a point
        for x0, y0 in ((3, 6), (11, 14), (12, 4)):
            for a in range(6):
                ang = math.pi * (0.12 + a / 6.5)
                for r in range(1, 8):
                    x, y = int(x0 + math.cos(ang) * r) % N, int(y0 - math.sin(ang) * r) % N
                    cv.set(x, y, hexc(w["leaf"][4 if r < 4 else 3]))
                    cv.set(x, (y + 1) % N, hexc(w["leaf"][1]))
    elif style == "fronds":  # tree fern: long fronds with paired leaflets
        for _ in range(4):
            x, y = rnd.randrange(N), rnd.randrange(N)
            for i in range(7):
                cv.set((x + i) % N, (y + i // 2) % N, hexc(w["leaf"][1]))
                cv.set((x + i) % N, (y + i // 2 - 1) % N, hexc(w["leaf"][4]))
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
    elif style == "fronds":  # tree fern: a short shaggy stem with a crown of arching fronds
        for y in range(9, 16):
            cv.set(7, y, stem); cv.set(8, y, hexc(w["bark"][2]))
        for dx, dy, length in ((-1, 0, 6), (1, 0, 6), (-1, -1, 4), (1, -1, 4), (0, -1, 3)):
            x, y = 7.5, 8.5
            for i in range(length):
                x += dx * 1.0; y += dy * 0.8 + (0.35 * i if dx else -0.6)
                cv.set(int(x), int(y), leaf(3 if i % 2 else 2))
                cv.set(int(x), int(y) + 1, leaf(1))
    elif style == "broad":  # round leafy crown on a straight stem (a flower on the magnolia)
        for y in range(1, 10):
            half = 4 - abs(y - 5) // 1 if y < 9 else 2
            for dx in range(-half, half + 1):
                cv.set(7 + dx, y, leaf(3 if dx < 0 and y < 5 else 2 if (dx + y) % 3 else 1))
        if "flowers" in w:
            cv.set(5, 3, hexc(w["flowers"][1])); cv.set(9, 6, hexc(w["flowers"][0]))
    elif style == "palm":  # young palm: fan of leaves straight from the ground
        for k in range(7):
            ang = math.pi * (0.1 + k / 7.5)
            for r in range(2, 9):
                cv.set(int(7.5 + math.cos(ang) * r), int(13 - math.sin(ang) * r), leaf(3 if r % 2 else 2))
        for y in range(12, 16):
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


# ------------------------------------------------------------------ prehistoric plants (cross sprites, transparent)
GREEN = ["#1f3417", "#2e4a1f", "#40632a", "#557d35", "#6c9641", "#88b052"]
OLIVE = ["#2f3a1c", "#435127", "#5a6a33", "#728440", "#8c9c50"]


def stalk(cv, x, y0, y1, colors, joint=None):
    for y in range(y0, y1):
        cv.set(x, y, hexc(colors[3]) if (joint and (y - y0) % joint == 0) else hexc(colors[2]))


def horsetail(tall=False, giant=False, part="single"):
    """Equisetum: jointed upright stems with whorls of thin branches (Calamites: a thick ribbed trunk)."""
    cv = Canvas()
    rnd = random.Random("horsetail" + part + str(tall) + str(giant))
    stems = (3, 7, 11, 13) if not giant else (7,)
    for i, x in enumerate(stems):
        top = 0 if part != "single" and part == "lower" else (2 + (i * 3) % 6 if part != "upper" else 3 + i * 2)
        for y in range(top if part != "lower" else 0, 16):
            c = GREEN[3] if (y % 3) else "#3a2e1c"
            cv.set(x, y, hexc(c))
            if giant:
                cv.set(x + 1, y, hexc(GREEN[2] if y % 3 else "#2a2214")); cv.set(x - 1, y, hexc(GREEN[4] if y % 3 else "#3a2e1c"))
            if y % 3 == 1 and y > top + 1:  # whorl of branches
                span = 3 if giant else 2
                for d in range(1, span + 1):
                    cv.set(x - d - (1 if giant else 0), y - d // 2, hexc(GREEN[4])); cv.set(x + d + (1 if giant else 0), y - d // 2, hexc(GREEN[4]))
        if part in ("single", "upper"):
            cv.set(x, top - 1, hexc("#7a6a3a"))  # spore cone
            cv.set(x, top - 2, hexc("#9a8a4a"))
    return cv


def fern(kind="bracken", part="single"):
    """Fern fronds: arching midribs with paired leaflets; royal fern has upright fronds with rusty fertile tips."""
    cv = Canvas()
    fronds = ((-1, 5), (1, 5), (-1, 3), (1, 3), (0, 6)) if kind != "royal" else ((-1, 4), (1, 4), (0, 6), (-1, 6), (1, 6))
    base_y = 15
    for dx, length in fronds:
        x, y = 7.5, base_y
        for i in range(length * 2 if part != "single" else length + 3):
            x += dx * (0.55 if kind != "royal" else 0.3)
            y -= 1.0 - (0.08 * i * abs(dx) if kind != "royal" else 0)
            ix, iy = int(x), int(y)
            cv.set(ix, iy, hexc(GREEN[2]))
            if i > 1:
                cv.set(ix - 1, iy, hexc(GREEN[4])); cv.set(ix + 1, iy, hexc(GREEN[3]))
                if i % 2 == 0:
                    cv.set(ix - 2, iy + 1, hexc(GREEN[5])); cv.set(ix + 2, iy + 1, hexc(GREEN[4]))
        if kind == "royal":
            cv.set(int(x), int(y), hexc("#9a5a2a")); cv.set(int(x), int(y) + 1, hexc("#7a4a22"))
    return cv


def cycad(young=True, part="single"):
    """Cycad: a squat scaly trunk with a crown of stiff, glossy pinnate leaves."""
    cv = Canvas()
    trunk_top = 12 if young else (6 if part != "upper" else 99)
    if part != "upper":
        for y in range(trunk_top, 16):
            for x in range(6, 10):
                cv.set(x, y, hexc("#5a4630" if (x + y) % 2 else "#7a6040"))
    if part == "lower":
        return cv
    crown_y = trunk_top if young else 14
    for dx in (-1, -0.5, 0.5, 1, 0):
        x, y = 7.5, crown_y
        for i in range(7 if young else 9):
            x += dx * 1.0; y -= 1.0 - 0.12 * i * abs(dx)
            ix, iy = int(x), int(y)
            cv.set(ix, iy, hexc(OLIVE[1]))
            cv.set(ix, iy - 1, hexc(OLIVE[3])); cv.set(ix + (1 if dx >= 0 else -1), iy, hexc(OLIVE[4]))
    return cv


def flower(petal, center, kind="williamsonia"):
    """Early flowers: Williamsonia (cycad-like plant with a cone flower), Archaefructus (stems with tiny flowers)."""
    cv = Canvas()
    if kind == "williamsonia":
        for y in range(8, 16):
            cv.set(7, y, hexc(OLIVE[2]))
        for dx in (-3, -2, -1, 1, 2, 3):
            cv.set(7 + dx, 12 - abs(dx) // 2, hexc(OLIVE[3]))
        for (x, y) in ((6, 5), (8, 5), (5, 6), (9, 6), (6, 7), (8, 7), (7, 4)):
            cv.set(x, y, hexc(petal))
        cv.set(7, 6, hexc(center)); cv.set(7, 5, hexc(center))
    else:
        for x0 in (4, 8, 11):
            for y in range(6 + x0 % 3, 16):
                cv.set(x0 + (y % 4 == 0), y, hexc(GREEN[3]))
            cv.set(x0, 5 + x0 % 3, hexc(petal)); cv.set(x0 + 1, 5 + x0 % 3, hexc(center))
    return cv


def pad(kind):
    """Floating leaves seen from above: Cretaceous water lily, Archaefructus rosette, swamp algae mat."""
    cv = Canvas()
    rnd = random.Random("pad" + kind)
    if kind == "algae":
        n = Noise("algae", periods=(4, 8), weights=(0.6, 0.4))
        for y in range(N):
            for x in range(N):
                v = n(x, y)
                if v > 0.42:
                    cv.set(x, y, ramp(["#2c3a14", "#3f5219", "#566c22", "#6e862c"], (v - 0.42) * 2.2))
        return cv
    pads = ((5, 6, 4.2), (11, 11, 3.4)) if kind == "lily" else ((8, 8, 5.5),)
    for cx, cy, r in pads:
        for y in range(N):
            for x in range(N):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                ang = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
                if d <= r and not (kind == "lily" and -0.35 < ang < 0.05):
                    cv.set(x, y, ramp(GREEN[1:], 0.25 + 0.5 * (1 - d / r) + 0.1 * rnd.random()))
    if kind == "lily":
        for (x, y) in ((4, 5), (5, 4), (6, 5), (5, 6)):
            cv.set(x, y, hexc("#e8dcc0"))
        cv.set(5, 5, hexc("#d8b040"))
    else:
        for (x, y) in ((8, 8), (6, 7), (10, 9), (7, 10)):
            cv.set(x, y, hexc("#f0e6c8"))
    return cv


def grass(kind):
    """Low plants: Cretaceous grass tufts, clubmoss (upright scaly shoots), spikemoss (flat fronds)."""
    cv = Canvas()
    rnd = random.Random("grass" + kind)
    if kind == "grass":
        for i in range(9):
            x = rnd.randrange(2, 14); h = rnd.randint(6, 12); lean = rnd.choice((-1, 0, 1))
            for k in range(h):
                cv.set(x + (lean if k > h * 0.6 else 0), 15 - k, hexc(OLIVE[2 + (k > h // 2)]))
    elif kind == "clubmoss":
        for x in (3, 6, 9, 12):
            h = rnd.randint(7, 11)
            for k in range(h):
                cv.set(x, 15 - k, hexc(GREEN[3])); cv.set(x + (1 if k % 2 else -1), 15 - k, hexc(GREEN[4]))
            cv.set(x, 15 - h, hexc("#a8a050"))
    else:  # spikemoss
        for y in range(9, 16):
            for x in range(1, 15):
                if (x * 7 + y * 3) % 5 < 3 and abs(x - 7.5) < (y - 7):
                    cv.set(x, y, hexc(GREEN[2 + (x + y) % 3]))
    return cv


def rush(part):
    """Rushes: dense round green stems with brown flower tufts near the top."""
    cv = Canvas()
    for i, x in enumerate((2, 4, 5, 7, 9, 10, 12, 13)):
        top = 0 if part == "lower" else 2 + (i * 5) % 7
        for y in range(top, 16):
            cv.set(x, y, hexc(GREEN[2 + i % 3]))
        if part == "upper":
            cv.set(x + 1, top + 3, hexc("#6a4a26")); cv.set(x + 1, top + 4, hexc("#7a5a30"))
    return cv


def liverwort():
    """Liverwort: flat forking lobes forming a wet green crust on the ground."""
    n = Noise("liverwort", periods=(4, 8, 16), weights=(0.4, 0.35, 0.25))
    return paint(lambda x, y: ramp(["#1d3214", "#2a461b", "#3b5e24", "#4f772e", "#679340"], contrast(n(x, y), 1.4)))


def lichen():
    """Crusty lichen patches (sage, grey-green and orange) on a transparent background."""
    cv = Canvas()
    n = Noise("lichen", periods=(4, 8), weights=(0.6, 0.4))
    rnd = random.Random("lichen")
    for y in range(N):
        for x in range(N):
            v = n(x, y)
            if v > 0.52:
                cv.set(x, y, ramp(["#6f7a5a", "#8d9874", "#a9b38e"], (v - 0.52) * 3))
    for _ in range(6):
        cv.set(rnd.randrange(N), rnd.randrange(N), hexc("#c8812e"))
    return cv


def shelf_fungus():
    """Bracket fungus growing out of bark: tiers of fan-shaped brackets with pale growth rings."""
    cv = Canvas()
    for cx, cy, r in ((5, 5, 4), (10, 10, 5), (4, 12, 3)):
        for y in range(cy - r, cy + 1):
            for x in range(cx - r, cx + r + 1):
                d = math.hypot(x - cx, (y - cy) * 1.6)
                if d <= r:
                    band = int(d) % 2
                    cv.set(x, y, hexc(["#5a3a1e", "#7a5228", "#a87a40", "#d8b880"][min(3, int(d * 4 / r)) if not band else 1]))
    return cv


def plant_textures():
    out = {
        "horsetail": horsetail(), "tall_horsetail_bottom": horsetail(True, part="lower"),
        "tall_horsetail_top": horsetail(True, part="upper"), "calamites_bottom": horsetail(giant=True, part="lower"),
        "calamites_top": horsetail(giant=True, part="upper"), "bracken": fern(), "tall_bracken_bottom": fern(part="lower"),
        "tall_bracken_top": fern(part="upper"), "royal_fern": fern("royal"), "young_cycad": cycad(),
        "cycad_bottom": cycad(False, "lower"), "cycad_top": cycad(False, "upper"),
        "williamsonia": flower("#d9c27a", "#8a5a2a"), "archaefructus": pad("archaefructus"),
        "cretaceous_water_lily": pad("lily"), "cretaceous_grass": grass("grass"), "clubmoss": grass("clubmoss"),
        "spikemoss": grass("spikemoss"), "liverwort": liverwort(), "lichen": lichen(), "rush_bottom": rush("lower"),
        "rush_top": rush("upper"), "swamp_algae": pad("algae"), "shelf_fungus": shelf_fungus(),
    }
    return out


# ------------------------------------------------------------------ earth, plaster and cave paintings (phase 5)
EARTH_RAMP = ["#4a3524", "#5e4530", "#73573d", "#88694a", "#9c7b58"]
PLASTERS = {  # id: colour ramp of the plaster
    "clay_plaster": ["#7a6248", "#8f7558", "#a38868", "#b59a79", "#c4aa8a"],
    "red_ochre_plaster": ["#5e2618", "#76321f", "#8e3f28", "#a34d31", "#b45e3e"],
    "yellow_ochre_plaster": ["#8a6424", "#a2782e", "#b88b3a", "#c99d4a", "#d6ae5e"],
    "charcoal_plaster": ["#1c1b1a", "#272523", "#33302d", "#403c38", "#4d4843"],
    "chalk_whitewash": ["#b8b4a8", "#ccc8bd", "#dcd8ce", "#e8e5dc", "#f2f0e9"],
}


def plaster(pid):
    """Hand-smoothed plaster: soft trowel strokes, hairline cracks, a few grains of sand."""
    n = Noise(pid, periods=(2, 4, 8), weights=(0.45, 0.35, 0.2), stretch=(1.5, 1.0))
    rnd = random.Random(pid)
    cv = paint(lambda x, y: ramp(PLASTERS[pid], contrast(n(x, y), 0.9)))
    x, y = rnd.randrange(N), rnd.randrange(N)
    for _ in range(7):
        cv.set(x % N, y % N, shade(cv.get(x % N, y % N), 0.82))
        x += rnd.choice((1, 1, 0)); y += rnd.choice((1, 0, -1))
    for _ in range(6):
        c = cv.get(xx := rnd.randrange(N), yy := rnd.randrange(N))
        cv.set(xx, yy, shade(c, 1.12))
    return cv


def rammed_earth():
    """Rammed earth: horizontal layers of tamped soil of slightly different colour, small stones in it."""
    rnd = random.Random("rammed")
    n = Noise("rammed", periods=(4, 16), weights=(0.5, 0.5), stretch=(2.0, 0.5))
    layer_tone = [0.85 + 0.25 * rnd.random() for _ in range(4)]
    cv = paint(lambda x, y: shade(ramp(EARTH_RAMP, 0.25 + 0.5 * n(x, y)), layer_tone[y // 4] * (0.82 if y % 4 == 3 else 1.0)))
    for _ in range(7):
        x, y = rnd.randrange(N), rnd.randrange(N)
        cv.set(x, y, hexc("#8a857a")); cv.set((x + 1) % N, y, hexc("#6a665c"))
    return cv


def packed_earth():
    """Hut floor of beaten earth mixed with straw, worn smooth and darker where people walk."""
    n = Noise("packed", periods=(2, 4, 8), weights=(0.4, 0.35, 0.25))
    rnd = random.Random("packed")
    cv = paint(lambda x, y: ramp(EARTH_RAMP, 0.35 + 0.45 * n(x, y)))
    for _ in range(8):
        x, y = rnd.randrange(N), rnd.randrange(N)
        cv.set(x, y, hexc("#b39752")); cv.set((x + 1) % N, y, hexc("#957c40"))
    return cv


def wattle_variant(kind):
    """Wattle and daub with timber: cross braces, a log frame, or whitewashed with chalk."""
    if kind == "whitewashed":
        cv = plaster("chalk_whitewash")
        rnd = random.Random("ww")
        for _ in range(10):  # daub showing through worn whitewash
            x, y = rnd.randrange(N), rnd.randrange(N)
            cv.set(x, y, ramp(DAUB_RAMP, 0.5)); cv.set((x + 1) % N, y, ramp(DAUB_RAMP, 0.6))
        return cv
    cv = wattle_daub()
    beam = lambda x, y, k: cv.set(x % N, y % N, ramp(BARK_TIMBER, k))  # noqa: E731
    for i in range(N):
        beam(i, 0, 0.7); beam(i, 15, 0.3); beam(0, i, 0.6); beam(15, i, 0.35)
        if kind == "frame":
            beam(i, 1, 0.55); beam(1, i, 0.5); beam(14, i, 0.4); beam(i, 14, 0.45)
    if kind == "cross":
        for i in range(1, 15):
            beam(i, i, 0.65); beam(i + 1, i, 0.4); beam(15 - i, i, 0.6); beam(14 - i, i, 0.4)
    return cv


BARK_TIMBER = ["#2e2014", "#46321f", "#5e452c", "#76593a"]

# pictograms, drawn on limestone in red ochre (r), charcoal (k) and chalk (w); '.' = bare rock
PAINTINGS = {
    "handprint": ["................", "....r.r.r.......", "....r.r.r.r.....", "....r.r.r.r.....",
                  "....rrrrrrr.....", "..r.rrrrrrr.....", "...rrrrrrrr.....", "....rrrrrrr.....",
                  ".....rrrrr......", ".....rrrrr......", "................", "...........r....",
                  "..........rrr...", "...........r....", "................", "................"],
    "tyrannosaurus": ["................", "........kkkk....", ".......kkkkkkk..", ".......kkk......",
                      "......kkkk.k....", "..k..kkkkk......", ".kkkkkkkkkk.....", "kk..kkkkkkk.....",
                      "......kkkk......", "......k..k......", "......k..k......", ".....kk..kk.....",
                      "................", "..r..........r..", ".rrr........rrr.", "................"],
    "triceratops": ["................", "................", ".k..............", "..kk..kkkkkk....",
                    "kkkkkkkkkkkkkk..", ".kkkkkkkkkkkkkk.", "..kkkkkkkkkkkk.k", "..kkkkkkkkkkkk..",
                    "...k.k....k.k...", "...k.k....k.k...", "................", "..rrrr.rr.rrrr..",
                    "................", "................", "................", "................"],
    "brachiosaurus": ["..kk............", ".kkkk...........", "..kk............", "..kk............",
                      "..kk............", "..kk............", "..kkk...........", "...kkkkkkkk.....",
                      "...kkkkkkkkkk...", "....kkkkkkkkkkk.", "....k.k...k.k...", "....k.k...k.k...",
                      "....k.k...k.k...", "................", "...r.r.r.r.r.r..", "................"],
    "stegosaurus": ["................", "......r.r.r.....", ".....rkrkrkr....", "....kkkkkkkkk...",
                    "...kkkkkkkkkkk..", "kkkkkkkkkkkkkkk.", "k..kkkkkkkkkk.kk", "....k.k...k.k..k",
                    "....k.k...k.k...", "................", "................", "................",
                    "................", "................", "................", "................"],
    "raptor": ["................", "................", ".........kkk....", "........kkkkk...",
               "..k.....kk......", "...kkkkkkk......", "....kkkkk.......", ".....kkk........",
               "....k..k........", "...kk..kk.......", "................", "......rrr.......",
               ".....r...r......", "................", "................", "................"],
    "pteranodon": ["................", "................", "......k.........", ".....kkk...kk...",
                   "kk..kkkkkkkkkk..", ".kkkkkkkkkkk....", "...kkkkkkkk.....", "......kk........",
                   "................", "................", "....r.....r.....", "...r.r...r.r....",
                   "................", "................", "................", "................"],
    "mosasaurus": ["................", "................", "................", "...kk...........",
                   "..kkkkkkkkk.....", ".kkkkkkkkkkkk...", "kk.kkkkkkkkkkkk.", "....k...k....kkk",
                   "...............k", "................", "w.w.w.w.w.w.w.w.", ".w.w.w.w.w.w.w.w",
                   "................", "................", "................", "................"],
    "spear_hunt": ["................", ".....r..........", "....rrr.....kk..", ".....r....kkkkk.",
                   "....rrr..kkkkkkk", "...r.r.rkkkkkkk.", "....r.r..k...k..", "...r...r.k...k..",
                   "................", ".r.......r......", "rrr.....rrr.....", ".r.......r......",
                   "rrr.....rrr.....", "r.r.....r.r.....", "................", "................"],
    "herd": ["................", "................", ".kkk...kkk...kkk", "kkkkk.kkkkk.kkkk",
             "kkkkk.kkkkk.kkkk", ".k.k...k.k...k.k", "................", "...kkk...kkk....",
             "..kkkkk.kkkkk...", "..kkkkk.kkkkk...", "...k.k...k.k....", "................",
             "................", "................", "................", "................"],
    "footprints": ["..r.r...........", "...r............", "..rrr...........", "........r.r.....",
                   ".........r......", "........rrr.....", "..r.r...........", "...r............",
                   "..rrr...........", "........r.r.....", ".........r......", "........rrr.....",
                   "..r.r...........", "...r............", "..rrr...........", "................"],
    "fire": ["................", ".......r........", "......rr........", "......rrr...r...",
             "....r.rrrr..r...", "....rrrwrrrrr...", "...rrrwwwrrr....", "...rrwwwwwrr....",
             "...rrwwwwwrr....", "....rrwwwrr.....", ".....rrrrr......", "...kkkkkkkkk....",
             "....k.k.k.k.....", "................", "................", "................"],
    "sun": ["................", ".......r........", "..r....r....r...", "...r.......r....",
            "......rrr.......", ".....rrrrr......", "rr..rrrrrrr..rr.", ".....rrrrr......",
            "......rrr.......", "...r.......r....", "..r....r....r...", ".......r........",
            "................", "................", "................", "................"],
    "moon": ["................", ".....yyyy.......", "...yyy..........", "..yy............",
             "..yy............", ".yy.............", ".yy.............", ".yy.............",
             "..yy............", "..yy.......y....", "...yyy.........y", ".....yyyy.......",
             "..........y.....", "................", "................", "................"],
    "spiral": ["................", "...rrrrrrrr.....", "..r........r....", ".r..rrrrrr..r...",
               ".r.r......r.r...", ".r.r.rrrr.r.r...", ".r.r.r..r.r.r...", ".r.r.r.rr.r.r...",
               ".r.r.r....r.r...", ".r.r..rrrr..r...", ".r..r......r....", "..r..rrrrrr.....",
               "...r............", "....rrrrrrrr....", "................", "................"],
    "stars": ["................", "..y.......y.....", ".yyy.....yyy....", "..y.......y.....",
              "......y.........", ".....yyy........", "......y....y....", "..........yyy...",
              "...y.......y....", "..yyy...........", "...y....y.......", "........k.......",
              ".......kkk......", "......kkkkk.....", "................", "................"],
}
PIGMENT = {"y": ["#9a6a22", "#a87a2a", "#b5852f"], "r": ["#7a2a18", "#8e3420", "#a03e28"], "k": ["#1e1a17", "#2a2420", "#35302a"], "w": ["#e6e0d0", "#f0ebe0", "#d8d2c2"]}


def cave_painting(name):
    """Pigment on limestone, worn by time: the rock grain shows through the paint here and there."""
    cv = copy(rock_base("limestone"))
    rnd = random.Random("paint" + name)
    for y, row in enumerate(PAINTINGS[name]):
        for x, ch in enumerate(row):
            if ch in PIGMENT and rnd.random() > 0.12:
                cv.set(x, y, mixc(hexc(rnd.choice(PIGMENT[ch])), cv.get(x, y), 0.15 * rnd.random()))
    return cv


# ------------------------------------------------------------------ roofs and weaving (phase 5)
ROOFS = {  # roof covering: ramp, style
    "reed_thatch": (["#4a4426", "#6a6034", "#8a7e45", "#a89a58", "#c2b26c"], "bundles"),
    "cycad_thatch": (["#2a3418", "#3a4720", "#4e5c2a", "#647236", "#7c8844"], "fronds"),
    "fern_thatch": (["#3a2a18", "#55401f", "#715628", "#8c6b33", "#a47f40"], "fronds"),
}


def roof(rid, top=False):
    """Roof covering: bundles of reed in courses, or overlapping dried leaves/fronds with a midrib."""
    ramp_c, style = ROOFS[rid]
    strands = Noise(rid + str(top), periods=(16, 8), weights=(0.7, 0.3), stretch=((0.25, 1.0) if top else (1.0, 0.25)))
    rnd = random.Random(rid + str(top))

    def px(x, y):
        v = strands(x, y) * 0.8 + 0.2 * rnd.random()
        if not top:
            course, row = y // 4, y % 4
            if style == "fronds":
                mid = (x + course * 4) % 8 == 3
                v = v * (0.55 if row == 0 else 1.0) + (0.25 if mid else 0)
            else:
                v = v * (0.55 if row == 0 else 1.0) + (0.3 if row == 3 else 0)
        return ramp(ramp_c, v)
    return paint(px)


WICKER_RAMP = ["#5a4428", "#7a5e36", "#987646", "#b08d58", "#c4a26c"]


def wicker(alpha=False):
    """Basket weave of split cane: over-under strands 2 px wide; door/trapdoor version has holes."""
    cv = Canvas()
    for y in range(N):
        for x in range(N):
            over = ((x // 2) + (y // 2)) % 2 == 0
            k = (y % 2) if over else (x % 2)
            if alpha and over and (x % 4 == 1 and y % 4 == 1):
                continue
            cv.set(x, y, ramp(WICKER_RAMP, 0.35 + (0.35 if k == 0 else 0.0) + (0.15 if over else -0.1)))
    return cv


def wicker_door(part):
    cv = wicker(alpha=True)
    for i in range(N):  # frame poles
        cv.set(0, i, ramp(BARK_TIMBER, 0.6)); cv.set(15, i, ramp(BARK_TIMBER, 0.3))
        if (part == "top" and i == 0) or (part == "bottom" and i == 15):
            for x in range(N):
                cv.set(x, i, ramp(BARK_TIMBER, 0.5))
    return cv


def reed_mat():
    """Mat of whole reeds laid side by side and tied with fibre."""
    def px(x, y):
        if y in (3, 12):
            return hexc("#4a3a22")
        return ramp(ROOFS["reed_thatch"][0], 0.35 + 0.4 * (x % 3 != 2) + 0.15 * ((x * 7 + y) % 5 == 0))
    return paint(px)


def rope_coil(top):
    """Coiled plant-fibre rope: side shows the turns, top the spiral."""
    rope = ["#5e4a2e", "#7a6240", "#967c54", "#ad9468"]
    if top:
        return paint(lambda x, y: ramp(rope, 0.2 + 0.7 * (0.5 + 0.5 * math.cos(math.hypot(x - 7.5, y - 7.5) * 2.1))))
    return paint(lambda x, y: ramp(rope, 0.15 + 0.75 * (0.5 + 0.5 * math.cos((y + x * 0.5) * math.pi / 2))))


def fiber_net():
    """Knotted fibre net, transparent between the cords."""
    cv = Canvas()
    for y in range(N):
        for x in range(N):
            if (x + y) % 5 == 0 or (x - y) % 5 == 0:
                cv.set(x, y, hexc("#8a7452" if (x + y) % 2 else "#a68e66"))
    return cv


def reed_bundle(top):
    """Bundle of cut reeds tied with fibre: side shows the stems, top the cut ends."""
    if top:
        return paint(lambda x, y: hexc("#4a4426") if (x % 3 == 0 and y % 3 == 0) else ramp(ROOFS["reed_thatch"][0], 0.5 + 0.3 * ((x + y) % 2)))
    def px(x, y):
        if y in (4, 11):
            return hexc("#4a3a22")
        return ramp(ROOFS["reed_thatch"][0], 0.3 + 0.45 * (x % 2) + 0.1 * ((y * 3 + x) % 4 == 0))
    return paint(px)


def phase5_textures():
    out = {p_: plaster(p_) for p_ in PLASTERS}
    out.update({"rammed_earth": rammed_earth(), "packed_earth_floor": packed_earth(),
                "cross_braced_wattle": wattle_variant("cross"), "timber_framed_wattle": wattle_variant("frame"),
                "whitewashed_wattle": wattle_variant("whitewashed")})
    for name in PAINTINGS:
        out[f"cave_painting_{name}"] = cave_painting(name)
    for rid in ROOFS:
        out[rid] = roof(rid)
        out[f"{rid}_top"] = roof(rid, True)
    out.update({"wicker_block": wicker(), "wicker_door_top": wicker_door("top"), "wicker_door_bottom": wicker_door("bottom"),
                "wicker_trapdoor": wicker(alpha=True), "reed_mat": reed_mat(), "rope_coil": rope_coil(False),
                "rope_coil_top": rope_coil(True), "fiber_net": fiber_net(), "reed_bundle": reed_bundle(False),
                "reed_bundle_top": reed_bundle(True)})
    return out


def phase5_items():
    cv = Canvas()
    top, bottom = wicker_door("top"), wicker_door("bottom")
    for y in range(N):
        src = top if y < 8 else bottom
        for x in range(4, 12):
            cv.set(x, y, src.get((x - 4) * 2, (y % 8) * 2))
    return {"wicker_door": cv}


# ------------------------------------------------------------------ hide, bone, trophies and fossils (phase 6)
ENTITY_TEX = os.path.join(os.path.dirname(TEX), "entity")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "javagen"))
from gen_resources import SPECIES  # noqa: E402  (one rug, trophy and fossil per species)
# side view of each skull, snout to the left: o outline, b bone, l lit bone, e opening (socket, fenestra), t tooth
SKULLS = {
    "tyrannosaurus": ["......ooooooo...", "....oobbbblllo..", "..oobbbbbbbbbbo.", ".obbbbeebbbbeebo",
                      "obbbbbeeebbbeebo", "obbbbbbbbbbbbbbo", "ottttttbbbbbbboo", ".o.t.t.tobbbbo..",
                      ".obbbbbbbbbbbo..", "..oooooooooooo.."],
    "spinosaurus": ["..........oooo..", ".........obllbo.", "....ooooobbbeebo", "..oobbbbbbbbeebo",
                    "oobbbbbbbbbbbbbo", "otttttttttbbbbbo", ".t.t.t.t.tobbbo.", "oobbbbbbbbbbbo..",
                    "..ooooooooooo..."],
    "dilophosaurus": ["......o.o.......", ".....oloolo.....", "....olbolbbo....", "...obbbbbbbbooo.",
                      "..obbbbbbbbbeebo", ".obbbbbeebbbeebo", "obbbbbbbbbbbbbbo", "otttttttbbbbbbo.",
                      ".o.t.t.tobbbbo..", ".obbbbbbbbbbo...", "..oooooooooo...."],
    "velociraptor": ["........oooooo..", "....ooooblllbbo.", "..oobbbbbbbbeebo", ".obbbbbeebbbeebo",
                     "obbbbbbbbbbbbbbo", "otttttttbbbbbbo.", ".t.t.t.tobbbbo..", ".obbbbbbbbbbo...",
                     "..oooooooooo...."],
    "compsognathus": [".......oooo.....", ".....oobllbo....", "...oobbbbeebo...", "..obbbeebeebo...",
                      "..obbbbbbbbbo...", "..ottttbbbbo....", "...obbbbbbo.....", "....oooooo......"],
    "triceratops": ["..............oo", "............oobo", "...o.......obbbo", "...lo.....obbbbo",
                    "....lo...obbebbo", ".o...lo.obbbbbbo", ".lo...obbbbbbbbo", "..lo.obbbbbbbebo",
                    ".olbbbbeebbbbbbo", "olbbbbbeebbbbbbo", "obbbbbbbbbbbbbo.", "obbbbbbbbbboooo.",
                    ".obbbbbbbbbo....", "..ooooooooo....."],
    "stegosaurus": [".......ooooo....", "....oobbbllbo...", "..oobbbbbbeebo..", ".obbbbbbbbeebo..",
                    "obbbbbbbbbbbbo..", "ottttbbbbbbbo...", ".obbbbbbbbbo....", "..ooooooooo....."],
    "ankylosaurus": ["..o.o.o.o.o.o...", ".olololololollo.", ".obbbbbbbbbbbbbo", ".obbbbbbbbbeebbl",
                     "obbbbbbbbbbeebbo", "obbbbbbbbbbbbbbl", "oobbbbbbbbbbbbbo", ".otttbbbbbbbbbo.",
                     "..obbbbbbbbbbo..", "...oooooooooo..."],
    "brachiosaurus": ["......oooo......", ".....obllbo.....", ".....obeebo.....", "....obbeebbo....",
                      "...obbbbbbbbo...", "..obbbbbbbeebo..", ".obbbbbbbbeebo..", "obbbbbbbbbbbbo..",
                      "otttttbbbbbbo...", ".obbbbbbbbbo....", "..ooooooooo....."],
    "parasaurolophus": ["..........ooooo.", "........oollllo.", "......oollbboo..", ".....olbbboo....",
                        "....obbbbo......", "...obbbbeebo....", "..obbbbbeebo....", ".obbbbbbbbbbo...",
                        "obbbbbbbbbbbo...", "oobbbbbbbbbo....", ".obbbbbbbbo.....", "..oooooooo......"],
    "pachycephalosaurus": ["........oooooo..", "......ollllllloo", ".....olllbbbbllo", "....olbbbbbbbbbo",
                           "..oobbbbbbeebbbo", ".obbbbbbbbeebbo.", "obbbbbbbbbbbbblo", "otttbbbbbbbbbo.l",
                           ".obbbbbbbbbbo...", "..oooooooooo...."],
    "gallimimus": [".........oooo...", ".......oobllbo..", ".....oobbbeeebo.", "...oobbbbbeeebo.",
                   ".oobbbbbbbbbbbo.", "obbbbbbbbbbbbo..", ".oobbbbbbbbbo...", "...ooooooooo...."],
    # alvarezsaurid: a tiny narrow skull with big orbits
    "mononykus": ["........ooooo...", "......ooblllbo..", "....oobbbbbeebo.", "..oobbbbbbbeebo.",
                  "obbbbbbbbbbbbbo.", "oobbbbbbbbbbbo..", "..ooooooooooo..."],
    # the mammal: a short deep skull with a big jaw, no fenestrae
    "didelphodon": ["....ooooooo.....", "..oobbbbbbboo...", ".obbbbbeebbbbo..", "obbbbbbbbbbbbbo.",
                    "ottbbbbbbbbbbbo.", ".ottttbbbbbbbo..", "..obbbbbbbbbo...", "...ooooooooo...."],
    "maiasaura": ["..........o.....", ".........olo....", "........obbo....", "......oobbbboo..",
                  "....oobbbbbeebo.", "..oobbbbbbbeebo.", "oobbbbbbbbbbbbo.", "obbbbbbbbbbbbbo.",
                  "oobbbbbbbbbbbo..", ".obbbbbbbbbbo...", "..oooooooooo...."],
    "pteranodon": [".............oo.", "...........oolo.", "..........olbo..", "........oobbo...",
                   "......oobeebbo..", "..ooooobbeebbo..", "oobbbbbbbbbbo...", "..oooobbbbbo....",
                   "......ooooo....."],
    "quetzalcoatlus": ["............oo..", "..........oolo..", "........oobbbo..", "......oobeebbo..",
                       "..ooooobbeebbo..", "oobbbbbbbbbbbo..", "..oooooobbbbo...", "........oooo...."],
    "hatzegopteryx": ["...........ooo..", ".........oolllo.", ".......oobbbbbo.", ".....oobbbeebbo.",
                      "...oobbbbbeebbo.", ".oobbbbbbbbbbbo.", "obbbbbbbbbbbbo..", ".ooobbbbbbbbo...",
                      "....oooooooo...."],
    "mosasaurus": ["........ooooo...", ".....oooblllbo..", "..oobbbbbbbeebo.", ".obbbbbbbbbeebbo",
                   "obbbbbbbbbbbbbbo", "ottttttttttbbbbo", ".t.t.t.t.t.tbbbo", "obbbbbbbbbbbbbo.",
                   ".ooooooooooooo.."],
}
SKULLS.update({  # one skull per species added after the first fifteen
    "styracosaurus": ["..........o.o.o.", "..........lolol.", "....o.....obbbo.", "....lo...obbbbo.", "....lo..obbbebo.", ".....lo.obbbbbo.", "..oo.lobbbbbbbo.", ".olbbbbbbbbbebo.", "olbbbbbeebbbbbo.", "obbbbbbeebbbbo..", "obbbbbbbbbbbo...", ".obbbbbbbbbo....", "..ooooooooo....."],
    "pachyrhinosaurus": ["...........o.o..", "..........olol..", ".........obbbo..", "...oooo.obbbbo..", "..ollllobbbebo..", ".olbbbbbbbbbbo..", "olbbbbeebbbbbo..", "obbbbbeebbbbo...", "obbbbbbbbbbo....", ".obbbbbbbbo.....", "..oooooooo......"],
    "protoceratops": ["...........oo...", "..........obbo..", ".........obbbo..", "....oooooobebo..", "..oobbbbbbbbbo..", ".obbbbbeebbbbo..", "obbbbbbeebbbo...", "obbbbbbbbbbo....", ".obbbbbbbbo.....", "..oooooooo......"],
    "euoplocephalus": ["...o.o.o.o.o....", "..olololololo...", ".obbbbbbbbbbbo..", ".obbbbbbbbbeebl.", "obbbbbbbbbbeebo.", "obbbbbbbbbbbbbl.", ".obbbbbbbbbbbo..", "..otttbbbbbbo...", "...ooooooooo...."],
    "therizinosaurus": [".......oooo.....", ".....oobllbo....", "...oobbbbeebo...", ".oobbbbbbeebo...", "obbbbbbbbbbbo...", ".ootttbbbbbo....", "...oooooooo....."],
    "deinocheirus": ["..........oooo..", "........oobllbo.", "......oobbbeebo.", "..ooooobbbbeebo.", "oobbbbbbbbbbbbo.", "obbbbbbbbbbbbo..", "oobbbbbbbbbbbo..", ".oobbbbbbbbbo...", "...ooooooooo...."],
    "alamosaurus": ["......ooooo.....", "....oobllbbo....", "...obbbbbbeeo...", "..obbbbbbbeeo...", ".obbbbbbbbbbo...", "otttbbbbbbbo....", "o.t.tbbbbbo.....", ".obbbbbbbo......", "..ooooooo......."],
    "saltasaurus": [".......oooo.....", ".....oobllbo....", "....obbbbeebo...", "...obbbbbeebo...", "..obbbbbbbbbo...", "..otttbbbbbo....", "...obbbbbbo.....", "....oooooo......"],
    "argentinosaurus": [".........ooo....", "......oooblbo...", "....oobbbbbbo...", "..oobbbbbbeebo..", ".obbbbbbbbeebo..", "obbbbbbbbbbbbo..", "otttttbbbbbbo...", ".obbbbbbbbbo....", "..ooooooooo....."],
    "opisthocoelicaudia": ["........oooo....", "......oobllbo...", "....oobbbbeebo..", "...obbbbbbeebo..", "..obbbbbbbbbbo..", ".otttbbbbbbbo...", "..obbbbbbbbo....", "...oooooooo....."],
    "dreadnoughtus": [".......ooooo....", ".....oobllllo...", "...oobbbbbbbbo..", "..obbbbbbbeebo..", ".obbbbbbbbeebo..", ".obbbbbbbbbbbo..", ".otttttbbbbbo...", "..obbbbbbbbo....", "...oooooooo....."],
    "giganotosaurus": [".......ooooooo..", "....ooobblllbbo.", "..oobbbbbbbbbbbo", ".obbbeeebbbbeebo", "obbbbeeebbbbeebo", "obbbbbbbbbbbbbbo", "otttttttbbbbbbbo", ".t.t.t.t.obbbbo.", ".obbbbbbbbbbbo..", "..ooooooooooo..."],
    "carcharodontosaurus": ["......oooooo....", "....oobbblllo...", "..oobbbbbbbbbo..", ".obbbeeebbbbeeo.", "obbbbeeebbbbeebo", "obbbbbbbbbbbbbbo", "ottttttttbbbbbbo", ".t.t.t.t.tobbbo.", ".obbbbbbbbbbbo..", "..ooooooooooo..."],
    "carnotaurus": [".........o..o...", "........olo.lo..", "......oobbbbbo..", "....oobbbbbeebo.", "..oobbbeebbeebo.", ".obbbbbeebbbbbo.", "obbbbbbbbbbbbo..", "otttttbbbbbbo...", ".obbbbbbbbbo....", "..ooooooooo....."],
    "tarbosaurus": [".......oooooo...", ".....oobbbllo...", "...oobbbbbbbbo..", "..obbbeebbbeebo.", ".obbbbeebbbeebo.", "obbbbbbbbbbbbbo.", "otttttbbbbbbbo..", ".t.t.tobbbbbo...", ".obbbbbbbbbo....", "..ooooooooo....."],
    "daspletosaurus": ["..........o.....", "......oooolo....", "....oobbbbbbo...", "..oolbblbbbbbo..", ".obbbbeebbbeebo.", "obbbbbeebbbeebo.", "obbbbbbbbbbbbbo.", "otttttttbbbbbo..", ".t.t.t.tobbbo...", ".obbbbbbbbbo....", "..ooooooooo....."],
    "albertosaurus": ["........ooooo...", "......oobbllo...", "....oobbbbbbbo..", "..oobbbeebbbeeo.", ".obbbbbeebbbeebo", "obbbbbbbbbbbbbbo", "ottttttbbbbbbbo.", ".t.t.t.obbbbo...", "..obbbbbbbbo....", "...oooooooo....."],
    "majungasaurus": ["..........oo....", ".........olbo...", ".......oobbbbo..", ".....oobbbbeebo.", "...oobbeebbeebo.", "..obbbbeebbbbbo.", ".obbbbbbbbbbbo..", ".otttttbbbbbo...", "..obbbbbbbbo....", "...oooooooo....."],
    "dakotaraptor": [".......oooooo...", "....oooobllbbo..", "..oobbbbbbbbeebo", ".obbbbbeebbbeebo", "obbbbbbbbbbbbbbo", "ottttttttbbbbbo.", ".t.t.t.t.obbbo..", ".obbbbbbbbbbo...", "..oooooooooo...."],
    "troodon": ["........ooooo...", "......oobblbbo..", "....oobbbeeeebo.", "..oobbbbbeeeebo.", ".obbbbbbbeeeebo.", "obbbbbbbbbbbbo..", "otttttbbbbbbo...", ".obbbbbbbbbo....", "..ooooooooo....."],
    "oviraptor": [".......oooo.....", "......olllo.....", ".....olbbbo.....", "....obbbbbbo....", "...obbbbbeebo...", "..obbbbbbeebo...", ".obbbbbbbbbbo...", "obbbbbbbbbbo....", ".oobbbbbbbo.....", "...ooooooo......"],
    "thescelosaurus": ["........oooo....", "......oobllbo...", "....oobbbbeebo..", "..oobbbbbbeebo..", ".obbbbbbbbbbbo..", "obbbbbbbbbbbo...", ".ootttbbbbbo....", "...oooooooo....."],
    "struthiomimus": ["..........oooo..", "........oobllbo.", "......oobbbeebo.", "....oobbbbbeebo.", "..oobbbbbbbbbbo.", "oobbbbbbbbbbbo..", "..oooobbbbbo....", "......ooooo....."],
    "ichthyornis": [".........oooo...", ".......oobllbo..", ".....oobbbeebo..", "...oobbbbbeebo..", "oobbbbbbbbbbo...", "ottttttbbbbbo...", ".oooooobbbbo....", ".......oooo....."],
    "tylosaurus": [".........ooooo..", "......ooobllbo..", "...oobbbbbbbeebo", ".obbbbbbbbbbeebo", "obbbbbbbbbbbbbbo", "oobttttttttbbbbo", ".o.t.t.t.t.tbbbo", "..obbbbbbbbbbbo.", "...oooooooooooo."],
    "elasmosaurus": [".........oooo...", ".......oobllbo..", ".....oobbbeebo..", "..ooobbbbbeebo..", ".obbbbbbbbbbbo..", "tottttttbbbbo...", ".t.t.t.t.bbo....", "..oooooooo......"],
    "xiphactinus": [".........oooo...", "......oooblbo...", "....oobbbbbbbo..", "..oobbbbbbeebbo.", ".obbbbbbbbeebbo.", "obbbbbbbbbbbbbo.", "ttttbbbbbbbbbo..", "t.t.tbbbbbbbo...", "otttbbbbbbbo....", ".ooooooooooo...."],
    "archelon": [".......ooooo....", ".....oobllllo...", "...oobbbbbbbbo..", "..obbbbbbbeebo..", ".obbbbbbbbeebo..", "obbbbbbbbbbbbo..", "obbbbbbbbbbbo...", ".lbbbbbbbbbo....", "..ooooooooo....."],
    "hesperornis": ["...........ooo..", ".........oollbo.", ".......oobbeebo.", "...ooooobbeebo..", "oobbbbbbbbbbo...", "otttttttbbbbo...", "..ooooooobbo....", ".........oo....."],
    "deinosuchus": ["..........oooo..", ".........obeebo.", "oooooooooobbbbbo", "obbbbbbbbbbbbbbo", "otttttttttbbbbbo", ".t.t.t.t.t.tbbo.", "obbbbbbbbbbbbo..", ".oooooooooooo..."],
    "baurusuchus": ["........oooo....", "......oobbbeo...", "...ooobbbbbeeo..", ".oobbbbbbbbbbbo.", "obbbbbbbbbbbbbo.", "otttttttbbbbbo..", ".t.t.t.tobbbo...", "obbbbbbbbbbo....", ".oooooooooo....."],
    "edmontosaurus": ["..........oooo..", "........oobllbo.", "......oobbbeebo.", "....oobbbbbeebo.", "..oobbbbbbbbbbo.", "oobbbbbbbbbbbbo.", "obbbbbbbbbbbbo..", "oooooobbbbbbo...", "......ooooooo..."],
    "citipati": ["......ooo.......", ".....ollo.......", ".....olllo......", "....olllbo......", "....obbbbbo.....",
                 "...obbbbeebo....", "..obbbbbeebo....", ".obbbbbbbbbo....", "obbbbbbbbbo.....", ".oobbbbbbo......",
                 "...oooooo......."],
    "corythosaurus": ["........oooo....", ".......ollllo...", "......ollbbllo..", "......obbbbbbo..", ".....obbbbeebo..", "...oobbbbbeebo..", ".oobbbbbbbbbbo..", "obbbbbbbbbbbo...", "oobbbbbbbbbo....", "..ooooooooo....."],
})


SKULL_ERA_ROCK = {"brachiosaurus": "shale", "stegosaurus": "shale", "dilophosaurus": "shale",
                  "compsognathus": "shale"}  # Jurassic beds; the Cretaceous skulls come out of limestone
FOSSIL_BONE = ["#4a3a2a", "#6b5640", "#8a7256", "#a28a6a", "#b8a27f"]  # mineralised bone: brown-grey, not white


def skull_rows(sid):
    rows = SKULLS.get(sid, SKULLS["velociraptor"])
    rows = [r.ljust(N, ".")[:N] for r in rows]
    top = (N - len(rows)) // 2 + 1
    return ["." * N] * top + rows + ["." * N] * (N - top - len(rows))


def skull_sprite(sid, bone=BONE_RAMP, outline="#3a3226", hole="#2a241c", base=None):
    """The skull drawn over base (or on transparency): bone shaded with noise, lit at the top."""
    cv = copy(base) if base else Canvas()
    n = Noise("skull" + sid, periods=(4, 8), weights=(0.6, 0.4))
    for y, row in enumerate(skull_rows(sid)):
        for x, ch in enumerate(row):
            if ch == "o":
                cv.set(x, y, hexc(outline))
            elif ch == "e":
                cv.set(x, y, hexc(hole))
            elif ch == "t":
                cv.set(x, y, ramp(bone, 0.95))
            elif ch in "bl":
                cv.set(x, y, ramp(bone, (0.55 if ch == "b" else 0.85) - 0.03 * y / 2 + 0.25 * (n(x, y) - 0.5)))
    return cv


def skull_fossil(sid):
    """Skull still in the rock: mineralised brown bone, a dark groove where the matrix was dug out around it."""
    rock = rock_base(SKULL_ERA_ROCK.get(sid, "limestone"))
    rows = skull_rows(sid)
    cv = copy(rock)
    for y in range(N):
        for x in range(N):
            if rows[y][x] == "." and any(0 <= y + dy < N and 0 <= x + dx < N and rows[y + dy][x + dx] != "."
                                         for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                cv.set(x, y, shade(rock.get(x, y), 0.7))
    return skull_sprite(sid, FOSSIL_BONE, "#2e251b", "#241d16", base=cv)


def species_ramp(sid):
    """Five colours of the species' hide, from dark to light, read from its entity texture (male)."""
    path = os.path.join(ENTITY_TEX, f"{sid}_male.png")
    if not os.path.exists(path):  # species without its texture yet: a neutral brown hide
        return HIDE_RAMP
    im = Image.open(path).convert("RGBA")
    data = im.load()
    px = [data[x, y][:3] for y in range(im.size[1]) for x in range(im.size[0]) if data[x, y][3] > 200]
    px.sort(key=lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2])
    return ["#%02x%02x%02x" % px[int(len(px) * q)] for q in (0.08, 0.25, 0.45, 0.65, 0.85)]


HIDE_PATTERN = {  # rug pattern of each species (scales by default)
    "spinosaurus": "stripes", "dilophosaurus": "stripes", "parasaurolophus": "stripes",
    "velociraptor": "feathers", "compsognathus": "feathers", "gallimimus": "feathers",
    "stegosaurus": "spots", "pachycephalosaurus": "spots", "maiasaura": "spots",
    "ankylosaurus": "osteoderms", "triceratops": "big_scales", "mosasaurus": "fine_scales",
    "pteranodon": "fuzz", "quetzalcoatlus": "fuzz", "hatzegopteryx": "fuzz",
    "dakotaraptor": "feathers", "troodon": "feathers", "oviraptor": "feathers", "citipati": "feathers", "mononykus": "feathers", "didelphodon": "fuzz",
    "struthiomimus": "feathers", "deinocheirus": "feathers", "therizinosaurus": "feathers",
    "hesperornis": "feathers", "ichthyornis": "feathers",
}


def hide_pattern(seed, colors, pattern):
    """Tileable skin: scales (Voronoi), osteoderms (big raised cells), stripes, spots, feathers or fuzz."""
    n = Noise(seed, periods=(2, 4, 8), weights=(0.5, 0.3, 0.2))
    if pattern in ("scales", "big_scales", "fine_scales", "osteoderms"):
        count = {"scales": 22, "big_scales": 12, "fine_scales": 40, "osteoderms": 8}[pattern]
        cells = Cells(seed, count)
        rnd = random.Random(seed)
        tone = [rnd.uniform(-0.12, 0.12) for _ in cells.seeds]

        def px(x, y):
            e = cells.edge[y][x]
            if e < (0.9 if pattern != "osteoderms" else 1.2):
                return ramp(colors, 0.12)
            lit = 0.08 if pattern == "osteoderms" and e > 2.4 else 0.0
            return ramp(colors, 0.5 + tone[cells.at(x, y)] + 0.3 * (n(x, y) - 0.5) + lit)
        return paint(px)
    if pattern == "stripes":
        return paint(lambda x, y: ramp(colors, 0.62 + 0.25 * (n(x, y) - 0.5)
                                        - (0.38 if (x + round(2 * math.sin(y / N * 2 * math.pi))) % 8 < 2 else 0)))
    if pattern == "spots":
        cells = Cells(seed, 6)
        return paint(lambda x, y: ramp(colors, 0.62 + 0.25 * (n(x, y) - 0.5)
                                        - (0.4 if cells.edge[y][x] > 3.2 else 0)))
    if pattern == "feathers":  # overlapping contour feathers: long cells, shadow under each, light quill
        cells = Cells(seed, 14, sx=1.5, sy=0.75)
        rnd = random.Random(seed)
        tone = [rnd.uniform(-0.1, 0.1) for _ in cells.seeds]

        def px(x, y):
            o = cells.at(x, y)
            if cells.at(x, y + 1) != o:
                return ramp(colors, 0.1)
            if cells.at(x - 1, y) != o:
                return ramp(colors, 0.3 + tone[o])
            sx, sy = cells.seeds[o]
            quill = abs(((x + 0.5 - sx + N / 2) % N) - N / 2) < 0.5
            return ramp(colors, 0.55 + tone[o] + (0.2 if quill else 0) + 0.2 * (n(x, y) - 0.5))
        return paint(px)
    # fuzz (pterosaur pycnofibres): fine noise, soft
    m = Noise(seed + "f", periods=(8, 16), weights=(0.5, 0.5))
    return paint(lambda x, y: ramp(colors, 0.45 + 0.35 * (m(x, y) - 0.5) + 0.25 * (n(x, y) - 0.5)))


def framed(cv, sides=True, top=True):
    """Stretched on a stick frame and laced to it: posts at the sides (and the rails at top and bottom)."""
    out = copy(cv)
    for i in range(N):
        if sides:
            out.set(0, i, ramp(STICK_RAMP, 0.7)); out.set(15, i, ramp(STICK_RAMP, 0.3))
        if top:
            out.set(i, 0, ramp(STICK_RAMP, 0.8)); out.set(i, 15, ramp(STICK_RAMP, 0.25))
    for i in range(2, N - 1, 3):
        if sides:
            out.set(1, i, hexc("#d8c9a4")); out.set(14, i, hexc("#d8c9a4"))
        if top:
            out.set(i, 1, hexc("#d8c9a4")); out.set(i, 14, hexc("#d8c9a4"))
    return out


RAWHIDE_RAMP = ["#8a7356", "#a68c6a", "#bba07c", "#cbb28e", "#d8c3a0"]
TANNED_RAMP = ["#3a2414", "#4f321d", "#644128", "#775034", "#8a6142"]
GENERIC_HIDES = {  # hide id: (colour source: ramp or species, pattern)
    "rawhide": (RAWHIDE_RAMP, "plain"), "tanned_hide": (TANNED_RAMP, "plain"),
    "scaled_hide": ("ankylosaurus", "osteoderms"), "feathered_hide": ("velociraptor", "feathers"),
    "fuzzy_hide": ("pteranodon", "fuzz"),
}


def generic_hide(hid):
    src, pattern = GENERIC_HIDES[hid]
    colors = species_ramp(src) if isinstance(src, str) else src
    if pattern == "plain":
        n = Noise(hid, periods=(2, 4, 8), weights=(0.5, 0.3, 0.2))
        rnd = random.Random(hid)
        cv = paint(lambda x, y: ramp(colors, contrast(n(x, y), 1.2)))
        x, y = rnd.randrange(N), 1
        for _ in range(12):  # a vein of the animal
            cv.set(x % N, y % N, shade(cv.get(x % N, y % N), 0.85))
            x += rnd.choice((-1, 0, 1)); y += 1
        return cv
    return hide_pattern(hid, colors, pattern)


def ossuary():
    """Ossuary wall: skulls and long bones stacked in rows in dark niches, like a charnel wall."""
    cv = paint(lambda x, y: hexc("#2a241c"))
    n = Noise("ossuary", periods=(4, 8), weights=(0.6, 0.4))
    skull = ["..ooo..", ".obbbo.", "obebebo", "obbbbbo", ".obtbo.", "..ooo.."]
    for oy, ox in ((1, 0), (1, 8), (9, 4), (9, 12)):  # two skulls per row, offset like bricks
        for y, row in enumerate(skull):
            for x, ch in enumerate(row):
                c = {"o": hexc("#5a5040"), "e": hexc("#1a1612"), "t": ramp(BONE_RAMP, 0.9),
                     "b": ramp(BONE_RAMP, 0.45 + 0.4 * (n((ox + x) % N, oy + y) - 0.3))}.get(ch)
                cv.set((ox + x) % N, oy + y, c)
    for y0 in (7, 15):  # long bones lying between the rows
        for x in range(N):
            cv.set(x, y0, ramp(BONE_RAMP, 0.55 + 0.2 * (n(x, y0) - 0.5)))
            if x % 5 == 0:  # knuckle ends
                cv.set(x, y0, ramp(BONE_RAMP, 0.9))
    return cv


def rib_bone():
    """Rib bone (arch): smooth, curving grain along the bone, darker at the edges."""
    n = Noise("rib", periods=(2, 8), weights=(0.5, 0.5), stretch=(0.5, 2.0))
    return paint(lambda x, y: ramp(BONE_RAMP, 0.25 + 0.55 * (1 - abs(x % 8 - 3.5) / 4.5) + 0.2 * (n(x, y) - 0.5)))


def tooth_totem(top):
    """A post wrapped in rings of big teeth tied with sinew; the top is the post's cut end."""
    if top:
        return paint(lambda x, y: ramp(STICK_RAMP, 0.35 + 0.4 * (((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5 % 3 < 1)))
    cv = paint(lambda x, y: ramp(STICK_RAMP, 0.3 + 0.3 * ((x * 7 + y) % 5 == 0)))
    for y0 in (0, 8):
        for x0 in range(0, N, 4):  # a row of teeth pointing down
            for dy, w in enumerate((3, 3, 2, 1, 1)):
                for dx in range(w):
                    cv.set(x0 + dx + (3 - w) // 2, y0 + 1 + dy, ramp(BONE_RAMP, 0.9 - 0.1 * dy - 0.15 * (dx == w - 1)))
        for x in range(N):
            cv.set(x, y0, mixc(hexc("#5e3a20"), hexc("#8a5a34"), (x % 3) / 3))
    return cv


def bone_pile():
    """Loose bones on bare earth: long bones with knobbed ends, each with its shadow."""
    rnd = random.Random("bonepile")
    n = Noise("bonepile", periods=(4, 8), weights=(0.6, 0.4))
    cv = paint(lambda x, y: ramp(EARTH_RAMP, 0.3 + 0.4 * n(x, y)))
    for x, y, horizontal, length in ((1, 2, True, 9), (9, 6, False, 8), (2, 10, True, 6), (12, 1, False, 4),
                                     (5, 13, True, 8)):
        for i in range(length):
            px, py = (x + i, y) if horizontal else (x, y + i)
            cv.set(px % N, (py + 1) % N if horizontal else py % N, ramp(EARTH_RAMP, 0.05)) if horizontal else \
                cv.set((px + 1) % N, py % N, ramp(EARTH_RAMP, 0.05))
            cv.set(px % N, py % N, ramp(BONE_RAMP, 0.55 + 0.3 * (rnd.random() < 0.3)))
        for end in (0, length - 1):  # knobs
            px, py = (x + end, y) if horizontal else (x, y + end)
            for d in (-1, 1):
                q = (px % N, (py + d) % N) if horizontal else ((px + d) % N, py % N)
                cv.set(*q, ramp(BONE_RAMP, 0.8 if d < 0 else 0.45))
    return cv


FEATHER_RAMP = ["#2a2420", "#4a3a2c", "#6e5a42", "#9c8466", "#c8b496"]


def feather_bundle(top):
    """Long feathers bundled upright: a light quill in each, barbs slanting down from it, sinew bands."""
    if top:  # the cut quill ends inside the bundle
        n = Noise("feathertop", periods=(4, 8), weights=(0.5, 0.5))
        return paint(lambda x, y: ramp(FEATHER_RAMP, 0.2 + 0.4 * n(x, y) + (0.35 if (x % 4, y % 4) == (2, 1) else 0)))
    n = Noise("feathers", periods=(2, 8), weights=(0.4, 0.6))

    def px(x, y):
        if y in (4, 12):
            return mixc(hexc("#5e3a20"), hexc("#8a5a34"), (x % 3) / 3)
        cx = x % 4
        if cx == 2:
            return ramp(FEATHER_RAMP, 0.9)
        barb = (y + abs(cx - 2)) % 2 == 0
        return ramp(FEATHER_RAMP, 0.35 + (0.15 if barb else 0) - (0.2 if cx == 0 else 0) + 0.3 * (n(x, y) - 0.5))
    return paint(px)


def phase6_textures():
    out = {}
    for sid in SPECIES:
        out[f"{sid}_hide_rug"] = hide_pattern(sid, species_ramp(sid), HIDE_PATTERN.get(sid, "scales"))
        out[f"{sid}_skull_trophy"] = skull_sprite(sid)
        out[f"{sid}_skull_fossil"] = skull_fossil(sid)
    for hid in GENERIC_HIDES:
        out[f"{hid}_frame"] = framed(generic_hide(hid))
        if hid != "rawhide":  # the raw hide panel is the hide_screen of batch 1
            out[f"{hid}_panel"] = framed(generic_hide(hid), top=False)
    out["ossuary_wall"] = ossuary()
    out["rib_bone"] = rib_bone()
    out["tooth_totem"] = tooth_totem(False)
    out["tooth_totem_top"] = tooth_totem(True)
    out["bone_pile"] = bone_pile()
    out["feather_bundle"] = feather_bundle(False)
    out["feather_bundle_top"] = feather_bundle(True)
    return out


# ------------------------------------------------------------------ utilities (phase 7)
FLAME = ["#ffffff", "#fff3a0", "#ffd24a", "#f39a1e"]  # hot centre -> outer flame, like the vanilla torch


def torch_sprite(kind):
    """Like the vanilla torch sprite (stick in columns 7-8, rows 6-15, flame on rows 6-7), each in its material:
    a bone wrapped in fat-soaked hide, a stick with a lump of burning resin, or a bundle of reeds tied with sinew."""
    cv = Canvas()
    for y in range(8, 16):
        for x in (7, 8):
            if kind == "bone":
                c = ramp(BONE_RAMP, 0.75 if x == 7 else 0.4)
            elif kind == "resin":
                c = ramp(STICK_RAMP, 0.8 if x == 7 else 0.45)
            else:
                c = ramp(THATCH_RAMP, (0.85 if x == 7 else 0.5) - (0.35 if y in (11, 14) else 0))
            cv.set(x, y, c)
    if kind == "bone":  # fat-soaked wrapping below the flame, knob of the bone at the foot
        for x in (7, 8):
            cv.set(x, 8, hexc("#3a2a1a")); cv.set(x, 9, hexc("#5a3e24"))
            cv.set(x, 15, ramp(BONE_RAMP, 0.9))
    elif kind == "resin":  # amber resin lump
        cv.set(7, 8, hexc("#e0a030")); cv.set(8, 8, hexc("#b0701c")); cv.set(7, 9, hexc("#c4841f"))
        cv.set(8, 9, hexc("#8a5214"))
    cv.set(7, 6, hexc(FLAME[1])); cv.set(8, 6, hexc(FLAME[2]))
    cv.set(7, 7, hexc(FLAME[0])); cv.set(8, 7, hexc(FLAME[1]))
    return cv


def small_flame():
    """Flame of the fat lamp (a tiny box): bright core, orange edge."""
    return paint(lambda x, y: hexc(FLAME[min(3, int(abs(x - 7.5) / 3 + (15 - y) / 6))]))


def fat_top():
    """Rendered fat in a stone bowl: soft, waxy, a dark burnt ring around the wick."""
    n = Noise("fat", periods=(2, 4), weights=(0.6, 0.4))
    return paint(lambda x, y: ramp(["#8a7a50", "#a8966a", "#c4b384", "#d8c99c"], 0.4 + 0.5 * n(x, y))
                 if abs(x - 7.5) + abs(y - 7.5) > 2 else hexc("#3a2e1c"))


def ash():
    n = Noise("ash", periods=(4, 8), weights=(0.5, 0.5))
    rnd = random.Random("ash")
    cv = paint(lambda x, y: ramp(["#2a2622", "#3e3934", "#57514a", "#76706a"], n(x, y)))
    for _ in range(6):  # embers
        cv.set(rnd.randrange(N), rnd.randrange(N), hexc(rnd.choice(("#c4501a", "#e07a24", "#8a2e10"))))
    return cv


def dried_meat():
    """Strips of dried meat: dark red with fat streaks and a crust."""
    n = Noise("jerky", periods=(2, 8), weights=(0.5, 0.5), stretch=(0.5, 2.0))
    return paint(lambda x, y: ramp(["#3a1210", "#5a1c16", "#74281e", "#8e3a2a", "#c49a7a"],
                                   0.35 + 0.4 * n(x, y) + (0.4 if (x + y // 5) % 6 == 0 else 0)))


CLAY_RAW = ["#6e5a48", "#86705c", "#9c8670", "#b09a84", "#c2ad97"]
CLAY_FIRED = ["#5e2c18", "#7a3a20", "#96502e", "#ae663e", "#c27c50"]


def clay_pot(fired, top=False):
    """Hand-built pot: coil lines around it; the fired one is red-brown with soot clouds from the open fire."""
    colors = CLAY_FIRED if fired else CLAY_RAW
    n = Noise("pot" + str(fired), periods=(2, 4, 8), weights=(0.5, 0.3, 0.2))
    if top:  # rim around the dark inside (the rim box shows only the middle 8x8 of this texture)
        return paint(lambda x, y: ramp(colors, 0.6 + 0.1 * (y < 8)) if max(abs(x - 7.5), abs(y - 7.5)) > 2.5
                     else hexc("#1e1712"))
    soot = Noise("soot", periods=(2, 4), weights=(0.6, 0.4))

    def px(x, y):
        c = ramp(colors, 0.45 + 0.3 * (n(x, y) - 0.5) - (0.12 if y % 3 == 0 else 0))
        if fired and soot(x, y) > 0.68:
            c = mixc(c, hexc("#1e1712"), 0.35)
        return c
    return paint(px)


def basin_water():
    n = Noise("water", periods=(2, 4), weights=(0.6, 0.4), stretch=(1.5, 1.0))
    return paint(lambda x, y: ramp(["#1e3a5a", "#28507a", "#346694", "#4a80aa"], 0.4 + 0.5 * n(x, y)))


def hide_bedroll():
    """Furred hide bedroll: thick hair in short strokes, brown and tan."""
    n = Noise("bedroll", periods=(4, 16), weights=(0.5, 0.5), stretch=(1.0, 2.0))
    return paint(lambda x, y: ramp(["#3a2618", "#55392a", "#70503a", "#8a6a4e", "#a6866a"],
                                   0.3 + 0.6 * n(x, y) - (0.15 if (x * 3 + y) % 5 == 0 else 0)))


def hammock_cloth():
    """Bark-cloth hammock: beaten fibre, faint stripes of the weave, darker cords along the edges."""
    n = Noise("hammock", periods=(2, 8), weights=(0.5, 0.5), stretch=(2.0, 0.5))
    return paint(lambda x, y: ramp(["#6a5638", "#86704c", "#a08a62", "#b8a278"],
                                   (0.2 if x in (0, 15) else 0.55 + 0.3 * (n(x, y) - 0.5) - 0.1 * (x % 3 == 0))))


def stakes(bone):
    """Cross sprite: three sharpened stakes leaning out (wood, fire-hardened tips) or long bones."""
    cv = Canvas()
    for x0, lean, top in ((3, -1, 2), (8, 0, 0), (12, 1, 3)):
        for y in range(top, 16):
            x = x0 + (lean * (15 - y)) // 6
            if bone:
                c = ramp(BONE_RAMP, 0.85 - 0.3 * (y - top < 2))
            else:
                c = ramp(STICK_RAMP, 0.7) if y - top > 2 else hexc("#1e1610")
            cv.set(x, y, c)
            if y - top > 1:
                cv.set(x + 1, y, shade(c, 0.75))
    return cv


def pit_cover():
    """Brush laid over a pit: leaves and twigs on crossed sticks, the dark hole showing through gaps."""
    n = Noise("pit", periods=(4, 8), weights=(0.5, 0.5))
    rnd = random.Random("pit")
    cv = paint(lambda x, y: ramp(OLIVE, 0.2 + 0.7 * n(x, y)) if n(x, y) > 0.28 else hexc("#120e0a"))
    for _ in range(5):
        x, y = rnd.randrange(N), rnd.randrange(N)
        for i in range(rnd.randint(4, 8)):
            cv.set((x + i) % N, (y + i // 2) % N, ramp(STICK_RAMP, 0.6))
    return cv


def menhir(top):
    """Weathered standing stone: grey gneiss-like grain, patches of yellow lichen, smoothed by rain."""
    n = Noise("menhir" + str(top), periods=(2, 4, 8), weights=(0.5, 0.3, 0.2), stretch=(0.6, 1.4))
    lic = Noise("menhirlichen", periods=(4, 8), weights=(0.5, 0.5))
    return paint(lambda x, y: ramp(["#8a8a6a", "#a8a47a", "#c4bc84"], lic(x, y))
                 if lic(x, y) > 0.76 else ramp(["#4a4a4c", "#5e5e60", "#727274", "#88888a", "#9c9c9c"], n(x, y)))


TOTEM_FACES = {  # carved face on the front of a totem post: d deep cut, l lit edge, p red ochre paint
    "raptor": ["................", "..dd........dd..", "..dld......dld..", "...dlddddddld...", "....dppppppd....",
               "...dpdllllldpd..", "...dpl.dd.lpd...", "....ddd..ddd....", ".....dllllld....", "....dlpppppld...",
               "...dlddddddldd..", "...dl.d.d.d.ld..", "....dllllllld...", ".....ddddddd....", "................",
               "................"],
    "rex": ["................", ".ddddddddddddd..", ".dllllllllllld..", ".dlddlllllddld..", ".dldpdllldpdld..",
            ".dlddlllllddld..", ".dlllllllllll d.", ".ddddddddddddd..", ".dld.d.d.d.dld..", ".dlddddddddd.d..",
            ".dl.d.d.d.d.ld..", ".dlllllllllld...", ".dppppppppppd...", ".ddddddddddddd..", "................",
            "................"],
    "pterosaur": ["......dd........", ".....dlld.......", "....dlppld......", "...dlllllld.....", "..dlldllldld....",
                  ".dllldppdllld...", "dlllllddlllllddd", ".ddllllllllllll.", "...ddddddddddd..", "....dl....ld....",
                  "...dlld..dlld...", "..dlpld..dlpld..", "..ddddd..ddddd..", "................", "................",
                  "................"],
}


def totem(face):
    """A carved post: bark-free wood with vertical grain and, on the front, the carved and ochre-painted face."""
    n = Noise("totem", periods=(2, 8), weights=(0.4, 0.6), stretch=(2.0, 0.5))
    cv = paint(lambda x, y: ramp(["#4a3220", "#5e4029", "#765236", "#8c6444", "#a27852"], 0.3 + 0.5 * n(x, y)))
    if face:
        for y, row in enumerate(TOTEM_FACES[face]):
            for x, ch in enumerate(row):
                if ch == "d":
                    cv.set(x, y, hexc("#2a1c12"))
                elif ch == "l":
                    cv.set(x, y, shade(cv.get(x, y), 1.25))
                elif ch == "p":
                    cv.set(x, y, hexc("#8e3420"))
    return cv


def totem_top():
    return paint(lambda x, y: ramp(["#4a3220", "#765236", "#a27852"],
                                   0.3 + 0.5 * ((((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5) % 3 < 1.2)))


def drum(part):
    """Drum: a hollowed log laced with sinew from rim to rim; the head is stretched rawhide."""
    if part == "head":
        n = Noise("drumhead", periods=(2, 4), weights=(0.6, 0.4))
        return paint(lambda x, y: ramp(RAWHIDE_RAMP, 0.4 + 0.5 * n(x, y)) if max(abs(x - 7.5), abs(y - 7.5)) < 7
                     else ramp(STICK_RAMP, 0.4))
    n = Noise("drumside", periods=(2, 8), weights=(0.4, 0.6), stretch=(0.5, 2.0))

    def px(x, y):
        if y < 2:
            return ramp(RAWHIDE_RAMP, 0.5)
        lace = (x + y) % 6 == 0 or (x - y) % 6 == 0
        return hexc("#d8c9a4") if lace and y < 12 else ramp(STICK_RAMP, 0.3 + 0.5 * n(x, y))
    return paint(px)


def basket_lid():
    """Woven lid seen from above: a spiral of coiled reed."""
    return paint(lambda x, y: ramp(WICKER_RAMP, 0.3 + 0.6 * (((math.atan2(y - 7.5, x - 7.5) / math.pi + 1) * 2
                                                             + (((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5) / 2) % 1)))


def firewood(end):
    """Split firewood stacked crosswise: the ends of the pieces (rings and bark), or the long sides."""
    if end:
        cells = Cells("firewood", 9)
        return paint(lambda x, y: ramp(STICK_RAMP, 0.1) if cells.border(x, y, 0.9)
                     else ramp(["#8a6438", "#a47a48", "#bc9058"], 0.3 + 0.5 * ((cells.edge[y][x] % 2) > 1)))
    n = Noise("firewoodside", periods=(2, 8), weights=(0.4, 0.6), stretch=(2.0, 0.5))
    return paint(lambda x, y: ramp(STICK_RAMP, 0.05) if y % 4 == 3
                 else ramp(["#4a3220", "#6a4a2c", "#8a6438", "#a47a48"], 0.3 + 0.5 * n(x, y)))


def phase7_textures():
    out = {f"{k}_torch": torch_sprite(k) for k in ("bone", "resin", "reed")}
    out.update({
        "lamp_flame": small_flame(), "fat_lamp_top": fat_top(), "hearth_ash": ash(), "dried_meat": dried_meat(),
        "raw_clay_pot": clay_pot(False), "raw_clay_pot_top": clay_pot(False, True),
        "fired_clay_pot": clay_pot(True), "fired_clay_pot_top": clay_pot(True, True),
        "basin_water": basin_water(), "hide_bedroll": hide_bedroll(), "hammock_cloth": hammock_cloth(),
        "sharpened_stakes": stakes(False), "bone_spikes": stakes(True), "pit_trap_cover": pit_cover(),
        "menhir": menhir(False), "menhir_top": menhir(True), "totem_side": totem(None), "totem_top": totem_top(),
        "drum_head": drum("head"), "drum_side": drum("side"), "wicker_basket_top": basket_lid(),
        "firewood_pile": firewood(False), "firewood_pile_end": firewood(True),
    })
    for face in TOTEM_FACES:
        out[f"{face}_totem_front"] = totem(face)
    return out


# ------------------------------------------------------------------ amber and resin
AMBER_RAMP = ["#4a2006", "#7a3c0e", "#a85a16", "#cc7c22", "#e8a238", "#f6c860"]


def amber(kind):
    """Fossil tree resin: deep orange-gold with clouds and bubbles inside (block), a smooth surface with a long
    light streak (polished), or polished pieces set in dark resin (mosaic)."""
    rnd = random.Random("amber" + kind)
    n = Noise("amber" + kind, periods=(2, 4, 8), weights=(0.5, 0.3, 0.2))
    if kind == "mosaic":
        cells = Cells("ambermosaic", 10)
        tones = [rnd.uniform(0.3, 0.85) for _ in cells.seeds]
        return paint(lambda x, y: ramp(AMBER_RAMP, 0.05) if cells.border(x, y, 0.9)
                     else ramp(AMBER_RAMP, tones[cells.at(x, y)] + 0.15 * (n(x, y) - 0.5)))
    if kind == "polished":
        return paint(lambda x, y: ramp(AMBER_RAMP, 0.35 + 0.35 * n(x, y) + (0.25 if (x + y) % 16 in (3, 4) else 0)))
    cv = paint(lambda x, y: ramp(AMBER_RAMP, contrast(n(x, y), 1.4)))
    for _ in range(5):  # bubbles caught in the resin
        x, y = rnd.randrange(N), rnd.randrange(N)
        cv.set(x, y, hexc(AMBER_RAMP[5])); cv.set((x + 1) % N, (y + 1) % N, hexc(AMBER_RAMP[1]))
    return cv


INCLUSIONS = {  # what got caught in the resin: d dark body, l light part
    "insect": ["................", "................", "......d...d.....", ".......d.d......", "....l..ddd..l...",
               ".....l.ddd.l....", "......ddddd.....", "....dd.ddd.dd...", "...d...ddd...d..", "......ddddd.....",
               ".....d.ddd.d....", "....d...d...d...", "................", "................", "................",
               "................"],
    "feather": ["................", "...........ll...", "..........lldl..", ".........lldll..", "........lldll...",
                ".......lldll....", "......lldll.....", ".....lldll......", "....lldll.......", "...lldll........",
                "....dll.........", "...d............", "..d.............", "................", "................",
                "................"],
    "leaf": ["................", "................", "........dd......", ".......dlld.....", "......dlldld....",
             ".....dlldlld....", "....dlldlld.....", "....dldlld......", "...dlldld.......", "...dldld........",
             "..d.dd..........", ".d..............", "................", "................", "................",
             "................"],
}


def amber_inclusion(kind):
    cv = amber("polished")
    for y, row in enumerate(INCLUSIONS[kind]):
        for x, ch in enumerate(row):
            if ch == "d":
                cv.set(x, y, mixc(hexc("#1e120a"), cv.get(x, y), 0.25))
            elif ch == "l":
                cv.set(x, y, mixc(hexc("#5a3a1a" if kind != "leaf" else "#3a4a1a"), cv.get(x, y), 0.35))
    return cv


def resin_block():
    """Fresh resin set hard: paler, cloudy, with drips running down."""
    n = Noise("resin", periods=(2, 4), weights=(0.6, 0.4), stretch=(1.0, 0.5))
    return paint(lambda x, y: ramp(["#7a5a1e", "#a07a2c", "#c49c40", "#dcb85a", "#ecd07c"],
                                   0.3 + 0.5 * n(x, y) + (0.15 if (x * 5) % 7 == 0 and y > 4 else 0)))


def amber_lantern(top):
    """Lantern: polished amber panes held in a bone frame; the light shows through the amber."""
    if top:
        return paint(lambda x, y: ramp(BONE_RAMP, 0.45 + 0.2 * ((x + y) % 3 == 0)))
    def px(x, y):
        if x in (0, 15, 7, 8) or y in (0, 1, 14, 15):
            return ramp(BONE_RAMP, 0.6 if x != 15 and y > 1 else 0.35)
        return ramp(AMBER_RAMP, 0.95 - abs(x - 7.5) / 12 - abs(y - 7.5) / 14)
    return paint(px)


def amber_textures():
    out = {"amber_block": amber("raw"), "polished_amber": amber("polished"), "amber_mosaic": amber("mosaic"),
           "resin_block": resin_block(), "amber_lantern": amber_lantern(False), "amber_lantern_top": amber_lantern(True)}
    for kind in INCLUSIONS:
        out[f"amber_with_{kind}"] = amber_inclusion(kind)
    return out


# ------------------------------------------------------------------ Cretaceous soils
SOIL_RAMP = ["#3a2a1c", "#4e3a28", "#634a34", "#785c42", "#8c6e52"]


def litter(kind, side):
    """Forest floor: fallen fern fronds (brown and a few still green) or conifer needles over dark soil;
    the side shows the soil with the litter only along the top."""
    rnd = random.Random("litter" + kind + str(side))
    n = Noise("litter" + kind, periods=(4, 8), weights=(0.5, 0.5))
    soil = paint(lambda x, y: ramp(SOIL_RAMP, 0.25 + 0.5 * n(x, y)))
    colors = (["#5a3e1e", "#7a5428", "#94683a", "#4a6a2a", "#6a8a38"] if kind == "fern"
              else ["#6a3a1a", "#8a4e22", "#a8642c", "#c47c3a", "#7a4a20"])
    rows = range(0, 4) if side else range(N)
    for _ in range(40 if not side else 14):
        x, y = rnd.randrange(N), rnd.choice(list(rows))
        length = rnd.randint(2, 5)
        dx = rnd.choice((1, -1))
        for i in range(length):
            yy = y + (i // 2 if kind == "fern" else i % 2)
            if side and yy > 3:
                break
            soil.set((x + dx * i) % N, yy % N, hexc(rnd.choice(colors)))
    if side:
        for x in range(N):
            if rnd.random() < 0.6:
                soil.set(x, 0, hexc(colors[rnd.randrange(3)]))
    return soil


def cracked_mud():
    """Mud dried in the sun: pale polygons curling at the edges, deep dark cracks between them."""
    cells = Cells("mudcracks", 7)
    n = Noise("mudcracks", periods=(4, 8), weights=(0.5, 0.5))
    return paint(lambda x, y: ramp(SOIL_RAMP, 0.0) if cells.border(x, y, 0.4)
                 else ramp(["#6a5a46", "#7e6c56", "#928066", "#a69478", "#b8a68a"],
                           0.35 + 0.35 * n(x, y) + (0.2 if cells.border(x, y, 1.2) else 0)))


def volcanic_ash(layer=False):
    n = Noise("ash" + str(layer), periods=(4, 8, 16), weights=(0.4, 0.3, 0.3))
    return paint(lambda x, y: ramp(["#6e6a66", "#827e78", "#96928c", "#aaa6a0", "#bcb8b2"], 0.2 + 0.7 * n(x, y)))


def peat():
    """Peat: dark, wet, half-rotten plant fibres."""
    n = Noise("peat", periods=(2, 8, 16), weights=(0.3, 0.4, 0.3), stretch=(2.0, 0.5))
    return paint(lambda x, y: ramp(["#1a120c", "#2a1e14", "#3a2a1c", "#4a3826", "#5e4a32"], 0.15 + 0.75 * n(x, y)))


def lateritic_soil():
    """Red tropical soil rich in iron, with small hard nodules."""
    rnd = random.Random("latsoil")
    n = Noise("latsoil", periods=(4, 8), weights=(0.5, 0.5))
    cv = paint(lambda x, y: ramp(["#5a2414", "#74301c", "#8c3e24", "#a24e2e", "#b4603a"], 0.25 + 0.55 * n(x, y)))
    for _ in range(8):
        x, y = rnd.randrange(N), rnd.randrange(N)
        cv.set(x, y, hexc("#3a1a10")); cv.set((x + 1) % N, y, hexc("#c47850"))
    return cv


def salt_crust():
    """Salt left by an evaporated lagoon: white crystalline polygons with raised rims over grey sand."""
    cells = Cells("salt", 9)
    n = Noise("salt", periods=(4, 8), weights=(0.5, 0.5))
    return paint(lambda x, y: ramp(["#e8e4dc", "#f4f2ec", "#ffffff"], 0.6 + 0.4 * n(x, y))
                 if cells.border(x, y, 0.5)
                 else ramp(["#a8a294", "#bcb6a8", "#d0cabc", "#dedad0"], 0.3 + 0.6 * n(x, y)))


def soil_textures():
    return {"fern_litter": litter("fern", False), "fern_litter_side": litter("fern", True),
            "needle_litter": litter("needle", False), "needle_litter_side": litter("needle", True),
            "cracked_mud": cracked_mud(), "volcanic_ash": volcanic_ash(), "peat": peat(),
            "lateritic_soil": lateritic_soil(), "salt_crust": salt_crust()}


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
    out.update(plant_textures())
    out.update(phase5_textures())
    out.update(phase6_textures())
    out.update(phase7_textures())
    out.update(amber_textures())
    out.update(soil_textures())
    for name, cv in out.items():
        cv.save(os.path.join(TEX, f"{name}.png"))
    for tid in WOODS:
        for name, cv in wood_items(tid).items():
            cv.save(os.path.join(os.path.dirname(TEX), "item", f"{name}.png"))
    for name, cv in phase5_items().items():
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
