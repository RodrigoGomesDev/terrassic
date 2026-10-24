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
import pixelkit as pk  # noqa: E402
from pixelkit import CLEAR, at, put  # noqa: E402,F401

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


# ------------------------------------------------------------------ rocks (engine v2: tone grids, see pixelkit.py)
# id: ramp of 5 tones (dark -> light), joint colour, noise stretch (x, y) and surface detail
ROCKS = {
    "limestone": {"ramp": ["#8f8670", "#a99f86", "#bdb49a", "#cfc7ae", "#e0d9c2"], "gap": "#5a5040",
                  "stretch": (0.5, 2.0), "detail": "fossils"},
    "shale": {"ramp": ["#2a2c30", "#383b40", "#464a50", "#555a60", "#686d72"], "gap": "#18191b",
              "stretch": (0.25, 2.0), "detail": "laminae"},
    "chalk": {"ramp": ["#b4b1a6", "#c9c6bc", "#d9d7ce", "#e7e5de", "#f3f2ec"], "gap": "#6e6858",
              "stretch": (1.0, 1.5), "detail": "cracks"},
    "flint": {"ramp": ["#bcb8aa", "#cdc9bc", "#dcd8cc", "#e8e5db", "#f3f1e9"], "gap": "#5e594d",
              "stretch": (1.0, 1.0), "detail": "nodules"},
    "laterite": {"ramp": ["#4a2012", "#66301b", "#824024", "#9c522e", "#b5683c"], "gap": "#2a140b",
                 "stretch": (1.0, 1.0), "detail": "pores"},
    "quartzite": {"ramp": ["#8f7a75", "#a68f89", "#baa39c", "#ccb7af", "#e2d2c9"], "gap": "#56463f",
                  "stretch": (0.7, 1.5), "detail": "sparkle"},
    "gneiss": {"ramp": ["#3a3a3e", "#55565b", "#717277", "#8f9095", "#b3b4b6"], "gap": "#1f1f22",
               "stretch": (1.0, 1.0), "detail": "bands"},
    "conglomerate": {"ramp": ["#5c4c38", "#726048", "#88755a", "#9c886b", "#b09c7e"], "gap": "#34291d",
                     "stretch": (1.0, 1.0), "detail": "clasts"},
}
HI = 4
GAP = -1
GAPCH = "g"
# extra colours (keys >= 10 so they never collide with ramp tones)
FLINT = {10: "#1d222a", 11: "#2c323c", 12: "#3e4550", 13: "#58606c", 14: "#eae5d8"}
OCHRE = {15: "#c4923e", 16: "#a87430"}
CLASTS = [  # quartz, dark chert, sandstone, granite, shale: dark, mid, light (own keys from 40 up)
    {40: "#8e877a", 41: "#c4bdb0", 42: "#ece8df"},
    {43: "#1f242b", 44: "#353c46", 45: "#56606c"},
    {46: "#8a6a44", 47: "#ad8a5c", 48: "#cfae7c"},
    {49: "#6a4a40", 50: "#93705e", 51: "#bb9682"},
    {52: "#3a3c40", 53: "#55585e", 54: "#73777d"},
]
MOSS = {30: "#2c4318", 31: "#3d5a1f", 32: "#527428", 33: "#6a8e33"}
SOIL = ["#4a3c2c", "#5c4b38", "#6e5c46", "#806d55"]


def extra_for(rid):
    r = ROCKS[rid]
    ex = {GAP: r["gap"]}
    ex.update(FLINT); ex.update(OCHRE); ex.update(MOSS)
    for c in CLASTS:
        ex.update(c)
    return ex


def chisel(g, seed, count, hi=HI, min_dist=3.2, horizontal=True):
    """The drawn detail of the modern stone textures: short lit ledges with a shadow line just under them
    (or beside them), spread evenly by blue noise instead of random speckle."""
    rnd = random.Random(seed)
    for x, y in pk.scatter(seed, count, min_dist):
        ln = rnd.choice((2, 3, 3, 4))
        for i in range(ln):
            px, py = (x + i, y) if horizontal else (x, y + i)
            if 0 <= at(g, px, py) <= hi:
                put(g, px, py, min(hi, at(g, px, py) + 1))
            qx, qy = (px, py + 1) if horizontal else (px + 1, py)
            if 0 <= at(g, qx, qy) <= hi and i < ln - 1:
                put(g, qx, qy, max(0, at(g, qx, qy) - 1))
    return g


def rock_face(rid, seed=""):
    """Calm natural rock: one dominant tone with big soft patches, then evenly spread chiselled ledges."""
    r = ROCKS[rid]
    g = pk.calm(rid + seed + "calm", base=2, share=0.62, periods=(2, 4, 8), weights=(0.45, 0.35, 0.2),
                stretch=r["stretch"])
    return chisel(g, rid + seed + "chisel", 9, horizontal=r["stretch"][1] >= r["stretch"][0])


def base_grid(rid):
    """The natural rock face as tone indices."""
    r = ROCKS[rid]
    d = r["detail"]
    rnd = random.Random(rid + "v2")
    if d == "laminae":
        g = rock_face(rid)
        for y in (1, 5, 8, 12):  # bedding planes: a dark parting with a lit lip under it, broken here and there
            x0 = rnd.randrange(N)
            for i in range(N):
                if (i + x0) % 11 < 9:
                    put(g, x0 + i, y, 0)
                    if at(g, x0 + i, y + 1) < 3:
                        put(g, x0 + i, y + 1, at(g, x0 + i, y + 1) + 1)
        for _ in range(2):  # rusty pyrite specks
            put(g, rnd.randrange(N), rnd.randrange(N), 16)
        return g
    if d == "bands":  # gneiss: wavy foliation, dark mica bands and light feldspar bands
        wav = pk.Noise(rid + "w", periods=(2, 4), weights=(0.7, 0.3))
        f = pk.field(lambda x, y: math.sin((y + x * 0.25) * (2 * math.pi / 8) + wav(x, y) * 3.0))
        g = pk.levels(f, [0.12, 0.2, 0.33, 0.2, 0.15])
        return chisel(pk.despeckle(pk.despeckle(g)), rid + "ch", 5)
    g = rock_face(rid)
    if d == "fossils":  # a small shell and a crinoid disc, lit on top
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, [".44.", "4224", "1..1"], {"4": 4, "2": 2, "1": 1})
        x, y = (x + 8) % N, (y + 7) % N
        pk.fleck(g, x, y, ["4.", "21"], {"4": 4, "2": 2, "1": 1})
        pk.dashes(g, rid + "bed", 3, 1, (3, 5))
    elif d == "cracks":  # chalk: one hairline crack and a few grey flint grains
        x, y = rnd.randrange(N), rnd.randrange(N)
        for _ in range(10):
            put(g, x, y, 1)
            x += rnd.choice((1, 1, 0)); y += rnd.choice((1, 0, 0, -1))
        for _ in range(3):
            x, y = rnd.randrange(N), rnd.randrange(N)
            pk.fleck(g, x, y, ["00"], {"0": 0})
    elif d == "pores":  # laterite: rounded holes (dark pit, lit lower rim) and ochre nodules
        for _ in range(9):
            x, y = rnd.randrange(N), rnd.randrange(N)
            pk.fleck(g, x, y, [GAPCH * 2, "44"] if rnd.random() < 0.4 else [GAPCH, "4"], {GAPCH: GAP, "4": 4})
        for _ in range(4):
            x, y = rnd.randrange(N), rnd.randrange(N)
            pk.fleck(g, x, y, ["ab"] if rnd.random() < 0.5 else ["a", "b"], {"a": 15, "b": 16})
    elif d == "sparkle":  # quartzite: sugary grains catching the light, and a few dark grains
        for x, y in pk.scatter(rid + "sp", 7, 3.5):
            put(g, x, y, 4)
        for x, y in pk.scatter(rid + "dk", 3, 5):
            put(g, x, y, 1)
    elif d == "nodules":  # flint nodules in the chalk: glassy dark core, white cortex rim, a glint
        wob = pk.Noise(rid + "wob", periods=(4, 8), weights=(0.6, 0.4))
        core = pk.Noise(rid + "core", periods=(4, 8), weights=(0.6, 0.4))
        for (cx, cy, rx, ry) in ((5.0, 5.0, 4.4, 3.0), (12.0, 11.5, 3.4, 3.6)):
            for y in range(N):
                for x in range(N):
                    dx = min(abs(x + 0.5 - cx), N - abs(x + 0.5 - cx)) / rx
                    dy = min(abs(y + 0.5 - cy), N - abs(y + 0.5 - cy)) / ry
                    dd = math.hypot(dx, dy) + (wob(x, y) - 0.5) * 0.6
                    if dd < 0.8:
                        lit = (x + 0.5 < cx and y + 0.5 < cy)
                        v = 10 + (2 if core(x, y) > 0.55 else 1) + (1 if lit and dd > 0.45 else 0)
                        g[y][x] = min(13, v) if not (dd > 0.55 and x + 0.5 > cx and y + 0.5 > cy) else 10
                    elif dd < 1.05:
                        g[y][x] = 14
            put(g, int(cx - rx / 3), int(cy - ry / 3), 13)
    elif d == "clasts":  # conglomerate: rounded pebbles of other rocks set in the sandy matrix
        for i in range(6):
            cl = CLASTS[rnd.randrange(len(CLASTS))]
            k0 = min(cl)
            cx, cy = rnd.uniform(0, N), rnd.uniform(0, N)
            rx, ry = rnd.uniform(1.6, 2.8), rnd.uniform(1.3, 2.1)
            for y in range(N):
                for x in range(N):
                    dx = (x + 0.5 - cx + N / 2) % N - N / 2
                    dy = (y + 0.5 - cy + N / 2) % N - N / 2
                    e = (dx / rx) ** 2 + (dy / ry) ** 2
                    if e <= 1:
                        k = 1 + (1 if (dx + dy < -0.6 * (rx + ry) / 2 and e > 0.25) else 0) \
                            - (1 if (dx + dy > 0.5 * (rx + ry) / 2 and e > 0.3) else 0)
                        g[y][x] = k0 + k
                    elif e <= 1.8 and dy > -0.3 and 0 <= at(g, x, y) < 10:
                        g[y][x] = 0  # the matrix shaded under the pebble
    return g



def rock_base(rid):
    """Natural rock surface (also the matrix of the cave paintings and skull fossils)."""
    return pk.colour(base_grid(rid), ROCKS[rid]["ramp"], extra_for(rid))


def stacked_grid(rid):
    """Dry-laid stones: courses, own tone per stone, lit top edge, shaded bottom/right, dark joints."""
    rnd = random.Random(rid + "h")
    owner, count = pk.courses(rid + "courses", heights=rnd.choice(([5, 5, 6], [6, 5, 5], [5, 6, 5])),
                              lengths=(5, 10), round_corners=0.5, min_last=5)
    # calm face per stone (modern stone bricks): one tone with a soft patch, a two-level chamfer, dark joints
    g = pk.calm(rid + "st", base=2, share=0.7, periods=(2, 4), weights=(0.6, 0.4))
    g = pk.per_region(g, owner, count, rid + "tone", spread=(-1, 0, 0, 1), hi=HI - 1)
    g = pk.bevel(g, owner, HI, joint=GAP)
    for x, y in pk.scatter(rid + "chip", 4, 5):  # a chipped spot here and there
        if owner[y][x] >= 0 and at(owner, x, y - 1) == owner[y][x] and at(owner, x + 1, y) == owner[y][x]:
            put(g, x, y, max(0, at(g, x, y) - 1)); put(g, x + 1, y, min(HI, at(g, x + 1, y) + 1))
    return g, owner


def stacked(rid):
    g, _ = stacked_grid(rid)
    return pk.colour(g, ROCKS[rid]["ramp"], extra_for(rid))


def flagstone(rid):
    """Flat slabs: big irregular stones with a fine joint, each lit along its top-left edge."""
    owner = pk.regions_from_cells(rid + "flag", 5, gap=0.8)
    count = max(max(r) for r in owner) + 1
    g = pk.calm(rid + "fl", base=2, share=0.68, periods=(2, 4), weights=(0.6, 0.4))
    g = pk.per_region(g, owner, count, rid + "ft", spread=(0, 0, 1, -1), hi=HI - 1)
    g = pk.bevel(g, owner, HI, joint=GAP)
    return pk.colour(g, ROCKS[rid]["ramp"], extra_for(rid))


def mossy(rid):
    """Moss grows in the joints and creeps over the top edges of the stones."""
    g, owner = stacked_grid(rid)
    mn = pk.Noise(rid + "moss", periods=(2, 4, 8), weights=(0.45, 0.35, 0.2))
    for y in range(N):
        for x in range(N):
            joint = owner[y][x] < 0
            top = not joint and at(owner, x, y - 1) < 0
            v = mn(x, y) + (0.2 if joint else 0) + (0.12 if top else 0)
            if v > 0.8:
                below_joint = at(owner, x, y + 1) < 0
                g[y][x] = 30 + min(3, int((v - 0.8) / 0.05)) - (1 if below_joint and not joint else 0)
                if joint:
                    g[y][x] = max(30, g[y][x] - 1)
    return pk.colour(pk.despeckle(g, protect=(GAP,)), ROCKS[rid]["ramp"], extra_for(rid))


def pebbles(rid):
    """Loose rounded pebbles of the rock lying on sandy soil."""
    r = ROCKS[rid]
    rnd = random.Random(rid + "pebbles")
    soil = pk.calm(rid + "soil", base=1, share=0.6, periods=(2, 4, 8), weights=(0.4, 0.4, 0.2))
    g = [[100 + v for v in row] for row in soil]
    placed = []
    for _ in range(40):
        if len(placed) >= 7:
            break
        cx, cy = rnd.uniform(0, N), rnd.uniform(0, N)
        rx, ry = rnd.uniform(1.7, 2.8), rnd.uniform(1.3, 2.0)
        if any(min(abs(cx - a), N - abs(cx - a)) < rx + b + 0.8 and min(abs(cy - c), N - abs(cy - c)) < ry + d + 0.6
               for a, c, b, d in placed):
            continue
        placed.append((cx, cy, rx, ry))
        tone = rnd.choice((2, 2, 3))
        for y in range(N):
            for x in range(N):
                dx = (x + 0.5 - cx + N / 2) % N - N / 2
                dy = (y + 0.5 - cy + N / 2) % N - N / 2
                e = (dx / rx) ** 2 + (dy / ry) ** 2
                if e <= 1:
                    k = tone + (1 if dy < -ry * 0.3 or (dx < -rx * 0.4 and dy < 0) else 0) \
                        - (1 if dy > ry * 0.35 else 0)
                    g[y][x] = max(0, min(HI, k))
                elif e <= 1.8 and dy > 0 and at(g, x, y) >= 100:
                    g[y][x] = 99  # contact shadow on the soil
                elif e <= 1.6 and at(g, x, y) >= 100:
                    g[y][x] = 100
    if rid == "flint":
        g = [[(10 + min(3, v)) if v < 100 and v >= 0 else v for v in row] for row in g]
    ex = extra_for(rid)
    ex.update({100 + i: c for i, c in enumerate(SOIL)})
    ex[99] = "#3a2e22"
    return pk.colour(g, r["ramp"], ex)


def rock_textures(rid):
    return {rid: rock_base(rid), f"{rid}_stacked": stacked(rid), f"{rid}_flagstone": flagstone(rid),
            f"mossy_{rid}_stacked": mossy(rid), f"{rid}_pebbles": pebbles(rid)}


# ------------------------------------------------------------------ thatch (palha)
THATCH_RAMP = ["#4f3f20", "#75602f", "#957c40", "#b39752", "#cdb269"]


def thatch():
    """Two courses of straw bundles (8 px each, like the bands of the vanilla hay bale): a deep shadow under the
    lip of the course above, upright straws one pixel wide in alternating tones, ragged sun-bleached tips."""
    rnd = random.Random("thatch2")
    g = pk.grid(2)
    for c in range(2):
        y0 = c * 8
        shift_ = rnd.randrange(N)
        tone = [rnd.choice((1, 2, 2, 3, 3, 4)) for _ in range(N)]
        tips = [rnd.choice((5, 6, 6, 7, 7, 8)) for _ in range(N)]
        for x in range(N):
            t = tone[(x + shift_) % N]
            for k in range(8):
                y = y0 + k
                if k == 0:
                    v = 0
                elif k == 1:
                    v = 1 if x % 3 else 0
                elif k >= tips[x]:
                    v = 4 if (x + k) % 2 else 3
                else:
                    v = t if (k + x) % 5 else t - 1
                g[y][x] = max(0, min(4, v))
        for _ in range(4):  # a few stray straws crossing
            x, y = rnd.randrange(N), y0 + rnd.randint(2, 5)
            put(g, x, y, 4); put(g, x + 1, y + 1, 4)
    return pk.colour(g, THATCH_RAMP)


def thatch_top():
    """Ends of the straw seen from above: short stalks lying every way, lit on one side."""
    rnd = random.Random("thatchtop2")
    g = pk.despeckle(pk.clusters("tt2", [0.19, 0.62, 0.19], periods=(2, 4, 8)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for _ in range(26):
        x, y = rnd.randrange(N), rnd.randrange(N)
        dx, dy = rnd.choice(((1, 0), (0, 1), (1, 1), (1, -1)))
        ln = rnd.randint(2, 4)
        t = rnd.choice((3, 4, 4))
        for i in range(ln):
            put(g, x + dx * i, y + dy * i, t)
    return pk.colour(g, THATCH_RAMP)


def straw_mat():
    """Hand-woven straw mat: 4 px strips going over and under, each strip of three straws, the strip that dives
    under its neighbour in shadow."""
    g = pk.grid(2)
    rnd = random.Random("mat2")
    for y in range(N):
        for x in range(N):
            horiz = ((x // 4) + (y // 4)) % 2 == 0
            k = (y % 4) if horiz else (x % 4)
            along = (x % 4) if horiz else (y % 4)
            v = (4, 3, 2, 1)[k]
            if along == 3:
                v -= 1  # dives under the crossing strip
            g[y][x] = max(0, v)
    for _ in range(5):
        put(g, rnd.randrange(N), rnd.randrange(N), 0)
    return pk.colour(g, THATCH_RAMP)


# ------------------------------------------------------------------ wattle and daub (pau a pique)
DAUB_RAMP = ["#5e4a34", "#7c644a", "#957b5c", "#ab9170", "#bea583"]
STICK_RAMP = ["#3a2814", "#54391d", "#6e4d2a", "#87623a"]


def daub_grid(seed="daub2", sticks=True):
    """Clay daub as tone indices: lumpy hand-pressed clay, straw fibres, one drying crack and, where the clay
    has fallen away, the woven sticks underneath (tones 50+)."""
    rnd = random.Random(seed)
    g = pk.despeckle(pk.clusters(seed, [0.05, 0.15, 0.55, 0.18, 0.07], periods=(2, 4, 8), weights=(0.4, 0.4, 0.2)), passes=2)
    if sticks:  # a patch where the daub fell off: horizontal withies woven round an upright stake
        x0, y0 = rnd.randrange(N), rnd.randrange(N)
        for j in range(5):
            for i in range(6):
                if (i in (0, 5) and j in (0, 4)) or rnd.random() < 0.08:
                    continue
                x, y = x0 + i, y0 + j
                put(g, x, y, (52 if j % 2 == 0 else 50) if i != 2 else (53 if j % 2 else 51))
        for i in range(6):  # the broken clay edge throws a shadow
            if at(g, x0 + i, y0 - 1) < 50:
                put(g, x0 + i, y0 - 1, 4)
            if at(g, x0 + i, y0 + 5) < 50:
                put(g, x0 + i, y0 + 5, 0)
    for _ in range(7):  # straw in the clay
        x, y = rnd.randrange(N), rnd.randrange(N)
        if at(g, x, y) < 50:
            for i in range(rnd.choice((2, 3))):
                if at(g, x + i, y) < 50:
                    put(g, x + i, y, 60)
    x, y = rnd.randrange(N), rnd.randrange(N)
    for _ in range(9):  # drying crack, lit on its lower lip
        if at(g, x, y) < 50:
            put(g, x, y, 0)
            if at(g, x, y + 1) < 50:
                put(g, x, y + 1, 4)
        x += rnd.choice((1, 1, 0)); y += rnd.choice((1, 0, 0, -1))
    return g


DAUB_EXTRA = {50: "#3a2814", 51: "#54391d", 52: "#6e4d2a", 53: "#87623a", 60: "#c8b27a"}


def wattle_daub():
    return pk.colour(daub_grid(sticks=False), DAUB_RAMP, DAUB_EXTRA)


# ------------------------------------------------------------------ bone fence (cerca de osso)
BONE_RAMP = ["#9c9178", "#bdb296", "#d6ccb0", "#e6dec6", "#f3eedf"]


def bone_fence():
    """Long bones side by side: each 4 px wide, round (lit, body, body, shaded edge), porous, yellowed towards
    the ends, bound with two sinew lashings that cast a shadow."""
    rnd = random.Random("bone2")
    g = pk.grid(2)
    for y in range(N):
        for x in range(N):
            g[y][x] = (4, 3, 2, 1)[x % 4] if x % 8 < 4 else (3, 3, 2, 0)[x % 4]
    for _ in range(8):
        x, y = rnd.randrange(N), rnd.randrange(N)
        if x % 4 in (1, 2):
            put(g, x, y, 1)
    for y in (3, 11):
        for x in range(N):
            g[y][x] = 30 if x % 3 else 31
            g[y + 1][x] = 32
            g[y + 2][x] = max(0, g[y + 2][x] - 1)
    return pk.colour(g, BONE_RAMP, {30: "#8a5a34", 31: "#a87048", 32: "#5e3a20"})


# ------------------------------------------------------------------ hide screen (painel de couro)
HIDE_RAMP = ["#5a3a1e", "#76502b", "#8f653a", "#a87b4b", "#bf915e"]


def hide_screen():
    """Scraped, stretched hide laced to two stick posts."""
    rnd = random.Random("hide2")
    g = pk.despeckle(pk.clusters("hide2", [0.05, 0.15, 0.55, 0.18, 0.07], periods=(2, 4, 8)), passes=2)
    x, y = 5, 0
    for _ in range(16):
        if at(g, x, y) > 1:
            put(g, x, y, at(g, x, y) - 1)
        x += rnd.choice((-1, 0, 0, 1)); y += 1
    cv = pk.colour(g, HIDE_RAMP)
    return framed(cv, top=False)


def hide_screen_edge():
    g = pk.grid(0)
    for y in range(N):
        for x in range(N):
            g[y][x] = (1, 3, 2, 0)[x % 4]
    return pk.colour(g, STICK_RAMP)


# ------------------------------------------------------------------ prehistoric woods
# tree id: bark ramp, bark style, wood ramp (stripped / planks), leaf ramp, leaf style
WOODS = {
    # Araucaria (monkey puzzle / Parana pine): grey-brown bark in scaly horizontal rings; pale yellow wood;
    # dark glossy green, stiff spiky scale leaves
    "araucaria": {"bark": ["#2e241b", "#43352a", "#5a4a3b", "#706050", "#857563"], "bark_style": "rings",
                  "wood": ["#9c8058", "#b8996a", "#cdb07e", "#dcc294", "#e8d3a8"],
                  "leaf": ["#183020", "#25452a", "#355e36", "#4a7a44", "#62944f"], "leaf_style": "spiky"},
    # Ginkgo: grey, deeply furrowed bark; pale cream wood; bright fan-shaped leaves
    "ginkgo": {"bark": ["#2f2c27", "#48433b", "#615a50", "#7a7267", "#938a7e"], "bark_style": "furrows",
               "wood": ["#a89470", "#c2ad86", "#d6c29a", "#e3d1ab", "#eedfbd"],
               "leaf": ["#2e4a16", "#456a22", "#5e8a2c", "#7aa63a", "#98c04e"], "leaf_style": "fans"},
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


def bark_grid(tid):
    """Bark as tone indices (0 = deepest crevice, 4 = lit ridge).  Every style is built from vertical structure,
    like the vanilla logs, with the texture of the real tree on top."""
    w = WOODS[tid]
    style = w["bark_style"]
    rnd = random.Random(tid + "bark2")
    if style == "rings":  # araucaria: overlapping scaly plates in horizontal tiers, each tier lit on top
        g = pk.grid(2)
        for tier in range(4):
            y0 = tier * 4
            x = rnd.randrange(N)
            while x < N + 16:
                wdt = rnd.randint(3, 5)
                for i in range(wdt):
                    put(g, x + i, y0, 3 if i else 2)
                    put(g, x + i, y0 + 1, 4 if 0 < i < wdt - 1 else 3)
                    put(g, x + i, y0 + 2, 2 if i < wdt - 1 else 1)
                    put(g, x + i, y0 + 3, 1 if i < wdt - 1 else 0)
                put(g, x + wdt - 1, y0 + 1, 2)
                x += wdt
        for _ in range(5):  # dark leaf scars
            put(g, rnd.randrange(N), rnd.randrange(4) * 4 + 2, 0)
        return g
    if style == "frond_bases":  # tree fern / palm: diamond lattice of old leaf stubs in a fibrous mat
        g = pk.despeckle(pk.clusters(tid + "fib", [0.19, 0.62, 0.19], periods=(8, 16), stretch=(2.0, 0.5)), passes=2)
        for cy in range(0, N, 6 if tid == "sabal" else 4):
            for cx in range(0 if (cy // (6 if tid == "sabal" else 4)) % 2 == 0 else 4, N, 8):
                if tid == "sabal":  # palm: crossed boots of old leaf stalks, wide and flat
                    pk.fleck(g, cx - 2, cy, ["..44..", ".4333.", "433332", ".2221.", "..10.."],
                             {"4": 4, "3": 3, "2": 2, "1": 1, "0": 0})
                else:  # tree fern: round stalk scars with a dark core
                    pk.fleck(g, cx - 1, cy, [".43.", "4302", ".21."], {"4": 4, "3": 3, "2": 2, "1": 1, "0": 0})
        return g
    if style == "smooth":  # magnolia: thin smooth bark, soft mottling, rows of lenticels
        g = pk.despeckle(pk.clusters(tid + "sm", [0.1, 0.2, 0.55, 0.15], periods=(4, 8), stretch=(1.5, 0.75)), passes=2)
        g = [[v + 1 for v in row] for row in g]
        for _ in range(9):
            x, y = rnd.randrange(N), rnd.randrange(N)
            pk.fleck(g, x, y, ["00", "33"] if rnd.random() < 0.6 else ["0", "3"], {"0": 0, "3": 3})
        return g
    if style == "plates":  # platanus: bark flaking off in patches of olive, grey and cream
        owner = pk.regions_from_cells(tid + "pl", 8, gap=0.0)
        tones = [rnd.choice((1, 2, 3, 3, 4)) for _ in range(8)]
        g = [[tones[owner[y][x]] for x in range(N)] for y in range(N)]
        fine = pk.clusters(tid + "f", [0.2, 0.6, 0.2], periods=(8, 16))
        for y in range(N):
            for x in range(N):
                o = owner[y][x]
                if at(owner, x, y + 1) != o or at(owner, x + 1, y) != o:  # the edge of the flake casts a shadow
                    g[y][x] = max(0, g[y][x] - 2)
                else:
                    g[y][x] = max(0, min(4, g[y][x] + fine[y][x] - 1))
        return g
    # fibres (metasequoia, taxodium, podocarpus) and furrows (ginkgo): long vertical ridges and crevices
    furrow = style == "furrows"
    g = pk.clusters(tid + "v", [0.12, 0.23, 0.3, 0.23, 0.12], periods=(4, 8, 16), weights=(0.35, 0.4, 0.25),
                    stretch=(2.0, 0.25))
    g = pk.despeckle(g)
    for _ in range(7 if furrow else 5):  # crevices: a dark line with the lit ridge on its left
        x, y = rnd.randrange(N), rnd.randrange(N)
        for i in range(rnd.randint(5, 10) if furrow else rnd.randint(4, 8)):
            put(g, x, y + i, 0)
            if at(g, x - 1, y + i) < 3:
                put(g, x - 1, y + i, 3 if furrow else 2)
            if rnd.random() < (0.15 if furrow else 0.25):
                x += rnd.choice((-1, 1))
    if not furrow:  # loose strips peeling off: a bright strip with a shadow line on its right
        for _ in range(3):
            x, y = rnd.randrange(N), rnd.randrange(N)
            for i in range(rnd.randint(3, 5)):
                put(g, x, y + i, 4); put(g, x + 1, y + i, 1)
    return g


def bark(tid):
    return pk.colour(bark_grid(tid), WOODS[tid]["bark"])


def log_top(tid, stripped=False):
    """Cut end like the vanilla log tops: rounded-square growth rings, alternating light and dark wood, a pith,
    one radial drying crack and a 1 px rim of bark (or of darker sapwood once stripped)."""
    w = WOODS[tid]
    rnd = random.Random(tid + "top2")
    cx, cy = 7.5 + rnd.choice((-0.5, 0, 0.5)), 7.5 + rnd.choice((-0.5, 0, 0.5))
    g = pk.grid(2)
    for y in range(N):
        for x in range(N):
            dx, dy = abs(x - cx), abs(y - cy)
            d = 0.6 * max(dx, dy) + 0.4 * math.hypot(dx, dy)
            # thin dark latewood lines every ~2.5 px between broad light earlywood bands
            g[y][x] = 1 if (d + 0.6) % 2.5 < 0.9 else (3 if d > 1.2 else 2)
    put(g, int(cx), int(cy), 0)
    ang = rnd.choice((0.6, 2.3, 3.9, 5.4))
    for r in range(1, 7):  # drying crack
        put(g, int(round(cx + math.cos(ang) * r)), int(round(cy + math.sin(ang) * r)), 0)
    edge = [(x, y) for y in range(N) for x in range(N) if x in (0, 15) or y in (0, 15)]
    if stripped:
        for x, y in edge:
            g[y][x] = 1
        return pk.colour(g, w["wood"])
    bk = bark_grid(tid)
    out = {}
    for x, y in edge:
        out[(x, y)] = 50 + max(0, min(4, bk[y][x]))
        g[y][x] = out[(x, y)]
    for y in (1, 14):  # the inner sapwood ring just under the bark is darker
        for x in range(1, 15):
            g[y][x] = 1
    for x in (1, 14):
        for y in range(1, 15):
            g[y][x] = 1
    ex = {50 + i: c for i, c in enumerate(w["bark"])}
    return pk.colour(g, w["wood"], ex)


def stripped_side(tid):
    """Debarked trunk: long smooth fibres in few tones, with the facets of the draw-knife."""
    w = WOODS[tid]
    g = pk.clusters(tid + "s2", [0.15, 0.35, 0.35, 0.15], periods=(4, 8, 16), weights=(0.3, 0.4, 0.3),
                    stretch=(2.0, 0.25))
    g = [[v + 1 for v in row] for row in pk.despeckle(g)]
    rnd = random.Random(tid + "knife2")
    for _ in range(3):  # knife facets: a flat lit stroke ending in a small dark nick
        x, y = rnd.randrange(N), rnd.randrange(N)
        for i in range(rnd.randint(3, 5)):
            put(g, x, y + i, 4)
        put(g, x, y + i + 1, 1)
    return pk.colour(g, w["wood"])


def hewn_planks(tid):
    """Boards split from the trunk and dressed with an adze, laid like the modern vanilla planks: four calm 4 px
    boards (each its own tone, lit top row, shaded row over the dark seam), a few long grain lines, shallow adze
    hollows (a lit stroke with a shadow under it), staggered butt joints and wooden pegs instead of nails."""
    w = WOODS[tid]
    rnd = random.Random(tid + "hewn3")
    g = pk.grid(2)
    for b in range(4):
        y0 = b * 4
        t = 2 + rnd.choice((-1, 0, 0, 1)) * (1 if b % 2 else 0)
        for x in range(N):
            g[y0][x] = t
            g[y0 + 1][x] = t
            g[y0 + 2][x] = t
            g[y0 + 3][x] = 1  # seam: shaded, not black, like the vanilla planks
        for _ in range(2):  # grain line
            x, ln = rnd.randrange(N), rnd.randint(3, 6)
            yy = y0 + rnd.choice((1, 2))
            for i in range(ln):
                put(g, x + i, yy, t - 1)
        x = rnd.randrange(N)  # an adze hollow
        for i in range(3):
            put(g, x + i, y0 + 1, min(4, t + 1))
        joint = (rnd.randrange(N) if b % 2 == 0 else (rnd.randrange(N) + 8)) % N
        if b % 2 == 0:  # board ends only every other board, like long planks
            for k in range(3):
                put(g, joint, y0 + k, 1)
            peg = (joint + rnd.choice((3, 4, 5))) % N
            put(g, peg, y0 + 1, 0); put(g, peg, y0 + 2, min(4, t + 1))
    return pk.colour(g, w["wood"])


LEAF_SHAPES = {  # stamps for each leaf style: 4 lit tip, 3 leaf, 2 shaded leaf, 1 shadow under it, 0 dark gap
    "spiky": [["4..", ".3.", "..2"], ["..4", ".3.", "2.."], ["4.", "32", ".1"]],  # stiff scale leaves
    "fans": [["4443", "3332", ".22.", ".1.."], [".443", "4332", ".21."]],  # ginkgo fans on a short stalk
    "feathery": [["4.4.4.", "322222", ".3.3.3"], ["4.4.4", "22222", "3.3.3"]],  # needle sprays on a twig
    "broad": [[".44.", "4332", ".221"], ["443", "322", ".1."]],  # glossy oval leaves with a midrib shadow
    "palm": [["4...", ".4..", "..3.", "...2"], ["...4", "..4.", ".3..", "2..."], ["4444", "3333", "1111"]],
    "fronds": [["4.4.4", "33333", "2.2.2"], ["4.4", "333", "2.2"]],  # paired leaflets along a frond
}


def leaves(tid):
    """Foliage like the vanilla leaves: dense clusters with ~12% see-through gaps and plenty of shadow pixels, and
    on top the stamped leaf shape of the species (scales, fans, needles, broad leaves, palm straps, fronds)."""
    w = WOODS[tid]
    style = w["leaf_style"]
    rnd = random.Random(tid + "leaf2")
    g = pk.clusters(tid + "l2", [0.12, 0.2, 0.3, 0.26, 0.12], periods=(4, 8, 16), weights=(0.3, 0.35, 0.35))
    g = pk.despeckle(g)
    g = [[CLEAR if v == 0 else v - 1 for v in row] for row in g]  # rank 0 = gap, then tones 0..3
    shapes = LEAF_SHAPES[style]
    for _ in range({"palm": 7, "feathery": 9, "fronds": 9}.get(style, 12)):
        sh = rnd.choice(shapes)
        pk.fleck(g, rnd.randrange(N), rnd.randrange(N), sh, {"4": 4, "3": 3, "2": 2, "1": 1, "0": 0})
    if "flowers" in w:  # magnolia: a few big cream flowers with a pink blush at the base
        for _ in range(3):
            pk.fleck(g, rnd.randrange(N), rnd.randrange(N), [".ab.", "abba", ".cc."], {"a": 61, "b": 60, "c": 62})
    ex = {60 + i: c for i, c in enumerate(w.get("flowers", []))}
    return pk.colour(g, w["leaf"], ex)


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
    """Door of split logs lashed to two cross-bars with rawhide: every log rounded (lit left edge, shaded right
    edge), thin light gaps between some logs, sharpened tops, a bark bar with wrapped lashings."""
    w = WOODS[tid]
    rnd = random.Random(tid + part + "door2")
    grain = pk.clusters(tid + "dg" + part, [0.3, 0.45, 0.25], periods=(4, 8, 16), stretch=(2.0, 0.25))
    g = pk.grid(2)
    for x in range(N):
        k = x % 4
        for y in range(N):
            v = 1 + grain[y][x] + (1 if k == 0 else 0) - (1 if k == 3 else 0)
            g[y][x] = max(0, min(4, v))
    for x in (3, 11):  # a see-through crack between two logs, where they do not quite touch
        y0, ln = rnd.randrange(N), rnd.randint(2, 4)
        for i in range(ln):
            put(g, x, y0 + i, CLEAR)
    x, y = rnd.randrange(4) * 4 + rnd.choice((1, 2)), rnd.randrange(5, 10)  # one knot
    pk.fleck(g, x, y, ["0", "3"], {"0": 1, "3": 3})
    bar = 3 if part == "top" else 11
    for x in range(N):  # bark cross-bar: lit top, darker underside, shadow cast on the logs below
        g[bar][x] = 53 if x % 5 else 52
        g[bar + 1][x] = 51
        if g[bar + 2][x] is not CLEAR:
            g[bar + 2][x] = 1
    for x in (1, 5, 9, 13):  # rawhide lashings wrapped round bar and log
        for y, t in ((bar - 1, 62), (bar, 63), (bar + 1, 62), (bar + 2, 61)):
            g[y][x] = t
    if part == "top":
        for x in range(N):  # sharpened log tips
            if x % 4 in (0, 3):
                g[0][x] = CLEAR
            if x % 4 == 0:
                g[1][x] = 3
    ex = {50 + i: c for i, c in enumerate(w["bark"])}
    ex.update({60 + i: c for i, c in enumerate(LASHING)})
    return pk.colour(g, w["wood"], ex)


def trapdoor(tid):
    """Hatch of round poles laid side by side (each lit on top, shaded below, gaps between), two bark battens."""
    w = WOODS[tid]
    grain = pk.clusters(tid + "tg", [0.3, 0.45, 0.25], periods=(4, 8, 16), stretch=(0.25, 2.0))
    g = pk.grid(2)
    for y in range(N):
        k = y % 4
        for x in range(N):
            if k == 3 and x not in (2, 3, 12, 13):
                g[y][x] = CLEAR  # gap between poles
                continue
            g[y][x] = max(0, min(4, 1 + grain[y][x] + (1 if k == 0 else 0) - (1 if k == 2 else 0)))
    for y in range(N):
        for x, t in ((2, 53), (3, 51), (12, 53), (13, 51)):
            g[y][x] = t
        if y % 4 == 1:
            g[y][2], g[y][3], g[y][12], g[y][13] = 62, 61, 62, 61  # lashings
    ex = {50 + i: c for i, c in enumerate(w["bark"])}
    ex.update({60 + i: c for i, c in enumerate(LASHING)})
    return pk.colour(g, w["wood"], ex)


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
    """Fence of whole branches: the bark of the tree with a couple of cut-off twig knots."""
    w = WOODS[tid]
    g = bark_grid(tid)
    rnd = random.Random(tid + "branch2")
    for _ in range(2):
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, [".0.", "0a0", ".0."], {"0": 0, "a": 60})
    return pk.colour(g, w["bark"], {60: w["wood"][3]})


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
    """Hand-smoothed plaster: two close tones in broad soft trowel patches, a lit crescent where a stroke
    ended, one hairline crack (dark with a lit lip)."""
    rnd = random.Random(pid + "3")
    g = pk.calm(pid + "p3", base=2, share=0.72, periods=(2, 4), weights=(0.6, 0.4), stretch=(1.5, 1.0))
    x, y = rnd.randrange(N), rnd.randrange(N)
    for _ in range(6):
        put(g, x, y, 1); put(g, x, y + 1, 3)
        x += 1; y += rnd.choice((1, 0, 0, -1))
    return pk.colour(g, PLASTERS[pid])


def rammed_earth():
    """Rammed earth: horizontal lifts of tamped soil, each its own shade, a dark seam between lifts with the lit
    edge of the next lift under it, and small stones caught in the mix."""
    rnd = random.Random("rammed2")
    g = pk.despeckle(pk.clusters("rammed2", [0.19, 0.62, 0.19], periods=(2, 4, 8), stretch=(1.0, 2.0)), passes=2)
    lifts = [0, 4, 7, 12]
    for i, y0 in enumerate(lifts):
        y1 = lifts[i + 1] if i + 1 < len(lifts) else N
        off = (0, 1, 0, 1)[i] + rnd.choice((0, 0, 1))
        for y in range(y0, y1):
            for x in range(N):
                g[y][x] = max(0, min(4, g[y][x] + off))
        for x in range(N):
            g[(y1 - 1) % N][x] = 0 if x % 7 else 1
            g[y0][x] = min(4, g[y0][x] + 1)
    for _ in range(6):
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, ["ab", "c."] if rnd.random() < 0.5 else ["ab"], {"a": 61, "b": 60, "c": 0})
    return pk.colour(g, EARTH_RAMP, {60: "#6a665c", 61: "#8e897e"})


def packed_earth():
    """Hut floor of beaten earth with straw, worn smooth: soft clumps, straw bits and the odd pebble."""
    rnd = random.Random("packed2")
    g = pk.despeckle(pk.clusters("packed2", [0.1, 0.2, 0.55, 0.15], periods=(2, 4, 8), weights=(0.4, 0.4, 0.2)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for _ in range(7):
        x, y = rnd.randrange(N), rnd.randrange(N)
        horizontal = rnd.random() < 0.6
        pk.fleck(g, x, y, ["ab"] if horizontal else ["a", "b"], {"a": 60, "b": 61})
    for _ in range(3):
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, ["c", "0"], {"c": 62, "0": 0})
    return pk.colour(g, EARTH_RAMP, {60: "#b09a60", 61: "#8e7846", 62: "#8a857a"})


def wattle_variant(kind):
    """Wattle and daub with timber: cross braces, a log frame, or whitewashed with chalk.  The timbers are
    hewn beams in relief: lit on their top/left faces, shaded under/right, casting a shadow on the daub."""
    if kind == "whitewashed":
        g = daub_grid("ww2", sticks=False)
        wn = pk.Noise("wwn", periods=(4, 8), weights=(0.6, 0.4))
        out = pk.grid()
        for y in range(N):
            for x in range(N):
                v = g[y][x]
                worn = wn(x, y) < 0.22
                out[y][x] = v if v >= 50 else (70 + min(4, v + 2)) if worn else min(4, v + 1)
        ex = {70 + i: c for i, c in enumerate(DAUB_RAMP)}
        ex.update(DAUB_EXTRA)
        return pk.colour(out, PLASTERS["chalk_whitewash"], ex)
    g = daub_grid("daub2" + kind, sticks=False)
    beam = pk.grid(-1)  # beam id per pixel, -1 = daub
    for i in range(N):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            beam[y][x] = 0
        if kind == "frame":
            for (x, y) in ((i, 1), (1, i), (14, i), (i, 14)):
                beam[y][x] = 0
    if kind == "cross":
        for i in range(N):
            for (x, y) in ((i, i), ((i + 1) % N, i), (15 - i, i), ((14 - i) % N, i)):
                beam[y][x] = 0
    grain = pk.clusters("beam" + kind, [0.3, 0.4, 0.3], periods=(8, 16), stretch=(1.0, 1.0))
    for y in range(N):
        for x in range(N):
            if beam[y][x] < 0:
                if at(beam, x, y - 1) >= 0 or at(beam, x - 1, y) >= 0:  # shadow of the beam on the clay
                    if g[y][x] < 50:
                        g[y][x] = max(0, g[y][x] - 2)
                continue
            lit = at(beam, x, y - 1) < 0 or at(beam, x - 1, y) < 0
            dark = at(beam, x, y + 1) < 0 or at(beam, x + 1, y) < 0
            g[y][x] = 80 + max(0, min(3, 1 + grain[y][x] + (1 if lit and not dark else 0) - (1 if dark and not lit else 0)))
    ex = dict(DAUB_EXTRA)
    ex.update({80 + i: c for i, c in enumerate(BARK_TIMBER)})
    return pk.colour(g, DAUB_RAMP, ex)


BARK_TIMBER = ["#2e2014", "#46321f", "#5e452c", "#76593a"]


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
PIGMENT = {"y": ["#9a6a22", "#a87a2a", "#b5852f"], "r": ["#7a2a18", "#8e3420", "#a03e28"], "k": ["#1e1a17", "#2a2420", "#35302a"],
           "w": ["#d8d2c2", "#e6e0d0", "#f0ebe0"]}  # dark -> light


def cave_painting(name):
    """Pigment on limestone, worn by time: the paint takes the light and shade of the rock under it (three tones
    per pigment), and here and there it has flaked off and the bare rock shows through."""
    g = pk.to_grid(rock_base("limestone"), ROCKS["limestone"]["ramp"])
    rnd = random.Random("paint2" + name)
    keys = {"r": 60, "k": 63, "y": 66, "w": 69}
    for y, row in enumerate(PAINTINGS[name]):
        for x, ch in enumerate(row):
            if ch in keys and rnd.random() > 0.1:
                rock = g[y][x] if g[y][x] is not CLEAR and g[y][x] < 10 else 2
                g[y][x] = keys[ch] + (0 if rock <= 1 else 1 if rock <= 3 else 2)
    ex = extra_for("limestone")
    for ch, k in keys.items():
        ex.update({k + i: c for i, c in enumerate(PIGMENT[ch])})
    return pk.colour(g, ROCKS["limestone"]["ramp"], ex)


# ------------------------------------------------------------------ roofs and weaving (phase 5)
ROOFS = {  # roof covering: ramp, style
    "reed_thatch": (["#4a4426", "#6a6034", "#8a7e45", "#a89a58", "#c2b26c"], "bundles"),
    "cycad_thatch": (["#2a3418", "#3a4720", "#4e5c2a", "#647236", "#7c8844"], "fronds"),
    "fern_thatch": (["#3a2a18", "#55401f", "#715628", "#8c6b33", "#a47f40"], "fronds"),
}


def roof(rid, top=False):
    """Roof covering in two courses (8 px), each overhanging the next.  Reed: upright bundled stems with ragged
    tips.  Fronds (cycad, fern): overlapping dried fronds, a midrib with leaflets slanting down both sides."""
    ramp_c, style = ROOFS[rid]
    rnd = random.Random(rid + str(top) + "2")
    if top:  # seen from above: stems / leaflets lying along the slope
        g = pk.despeckle(pk.clusters(rid + "top2", [0.19, 0.62, 0.19], periods=(2, 4, 8), stretch=(0.5, 2.0)), passes=2)
        g = [[v + 1 for v in row] for row in g]
        for _ in range(18):
            x, y = rnd.randrange(N), rnd.randrange(N)
            for i in range(rnd.randint(2, 4)):
                put(g, x + i, y, 4 if i == 0 else 3)
            put(g, x, y + 1, 1)
        return pk.colour(g, ramp_c)
    if style == "bundles":
        g = pk.grid(2)
        for c in range(2):
            y0 = c * 8
            tone = [rnd.choice((1, 2, 2, 3, 3, 4)) for _ in range(N)]
            tips = [rnd.choice((6, 7, 7, 8)) for _ in range(N)]
            for x in range(N):
                for k in range(8):
                    if k == 0:
                        v = 0
                    elif k == 1:
                        v = 1
                    elif k >= tips[x]:
                        v = 4 if (x + k) % 2 else 3
                    elif k in (3, 4) and x % 4 == 1:
                        v = 1  # fibre tie round the bundle
                    else:
                        v = tone[x]
                    g[y0 + k][x] = v
        return pk.colour(g, ramp_c)
    g = pk.grid(1)
    for c in range(2):
        y0 = c * 8
        for f in range(2):  # two fronds per course, offset in every course
            mx = (f * 8 + c * 4 + 3) % N
            for k in range(8):
                y = y0 + k
                if k == 0:
                    for x in range(mx - 4, mx + 4):
                        put(g, x, y, 0)
                    continue
                put(g, mx, y, 4)  # midrib
                for side in (-1, 1):
                    for d in range(1, 4):
                        # leaflets slant down and out from the midrib; each leaflet lit on its upper edge
                        if (k + d) % 3 == 0:
                            put(g, mx + side * d, y, 3)
                        elif (k + d) % 3 == 1:
                            put(g, mx + side * d, y, 2)
                        else:
                            put(g, mx + side * d, y, 1)
            put(g, mx + 4, y0 + 1, 0)
    return pk.colour(g, ramp_c)


WICKER_RAMP = ["#5a4428", "#7a5e36", "#987646", "#b08d58", "#c4a26c"]


def wicker_grid(alpha=False):
    """Basket weave of split cane, 2 px strands: the strand on top is lit along its upper edge, the one passing
    under is in shadow where it dives; door/hatch version has little open windows."""
    g = pk.grid(2)
    for y in range(N):
        for x in range(N):
            over_h = ((x // 2) + (y // 2)) % 2 == 0
            if over_h:  # horizontal strand on top
                v = 4 if y % 2 == 0 else 2
                if x % 2 == 1 and y % 2 == 1:
                    v = 2
            else:  # vertical strand on top
                v = 3 if x % 2 == 0 else 1
            g[y][x] = v
            if alpha and (x % 4 == 1 and y % 4 == 1):
                g[y][x] = CLEAR
    return g


def wicker(alpha=False):
    return pk.colour(wicker_grid(alpha), WICKER_RAMP)


def wicker_door(part):
    g = wicker_grid(alpha=True)
    for i in range(N):  # frame poles in relief
        g[i][0], g[i][1], g[i][15] = 52, 51, 50
        if (part == "top" and i == 0) or (part == "bottom" and i == 15):
            for x in range(N):
                g[i][x] = 52 if part == "top" else 51
    ex = {50 + i: c for i, c in enumerate(BARK_TIMBER)}
    return pk.colour(g, WICKER_RAMP, ex)


def reed_mat():
    """Mat of whole reeds side by side (each 2 px: lit and shaded half, a node every few pixels), tied with
    twisted fibre."""
    g = pk.grid(2)
    rnd = random.Random("reedmat2")
    nodes = [rnd.randrange(5) for _ in range(8)]
    for y in range(N):
        for x in range(N):
            r = x // 2
            v = (3 if x % 2 == 0 else 1) + (1 if (y + nodes[r]) % 6 == 0 and x % 2 == 0 else 0)
            if (y + nodes[r]) % 6 == 1:
                v -= 1
            g[y][x] = max(0, v)
    for y in (3, 12):
        for x in range(N):
            g[y][x] = 60 if x % 2 else 61
            g[y + 1][x] = 0 if x % 2 else g[y + 1][x]
    return pk.colour(g, ROOFS["reed_thatch"][0], {60: "#4a3a22", 61: "#6e5a3a"})


ROPE = ["#4a3a24", "#5e4a2e", "#7a6240", "#967c54", "#b09870"]


def rope_coil(top):
    """Coiled fibre rope: side shows four turns of twisted rope (diagonal plies, shadow between turns); top
    shows the spiral of the coil."""
    g = pk.grid(2)
    if top:
        for y in range(N):
            for x in range(N):
                ang = math.atan2(y - 7.5, x - 7.5)
                r = math.hypot(x - 7.5, y - 7.5) + ang / math.tau * 2.5
                ph = r % 2.5
                g[y][x] = 0 if ph < 0.6 else (4 if ph < 1.2 else 3 if ph < 1.8 else 2)
        put(g, 7, 7, 0); put(g, 8, 8, 0)
        return pk.colour(g, ROPE)
    for y in range(N):
        for x in range(N):
            k = y % 4
            ply = (x + y) % 3
            if k == 3:
                v = 0
            else:
                v = (4 if ply == 0 else 3 if ply == 1 else 1) - (1 if k == 2 and ply != 2 else 0)
            g[y][x] = max(0, v)
    return pk.colour(g, ROPE)


def fiber_net():
    """Knotted fibre net, transparent between the cords: diagonal cords lit on one side, a knot at each crossing."""
    g = pk.grid(CLEAR)
    for y in range(N):
        for x in range(N):
            a, b = (x + y) % 6 == 0, (x - y) % 6 == 0
            if a and b:
                g[y][x] = 3
            elif a:
                g[y][x] = 2
            elif b:
                g[y][x] = 1
    for y in range(0, N, 6):  # knots: a small lump
        for x in range(N):
            if (x + y) % 6 == 0 and (x - y) % 6 == 0:
                put(g, x + 1, y, 2); put(g, x, y + 1, 0)
    return pk.colour(g, ROPE)


def reed_bundle(top):
    """Bundle of cut reeds tied with fibre: side shows the stems and their nodes, top the hollow cut ends."""
    rampr = ROOFS["reed_thatch"][0]
    if top:
        g = pk.grid(0)
        for cy in range(0, N, 3):
            for cx in range(0, N, 3):
                ox = 1 if (cy // 3) % 2 else 0
                pk.fleck(g, cx + ox, cy, ["43", "21"], {"4": 4, "3": 3, "2": 2, "1": 60})
        return pk.colour(g, rampr, {60: "#3a3420"})
    g = pk.grid(2)
    rnd = random.Random("reedb2")
    nodes = [rnd.randrange(7) for _ in range(8)]
    for y in range(N):
        for x in range(N):
            r = x // 2
            v = 3 if x % 2 == 0 else 1
            if (y + nodes[r]) % 7 == 0:
                v = 4 if x % 2 == 0 else 2
            g[y][x] = v
    for y in (4, 11):
        for x in range(N):
            g[y][x] = 60 if x % 3 else 61
            g[y + 1][x] = 0
    return pk.colour(g, rampr, {60: "#4a3a22", 61: "#6e5a3a"})


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
    # the little multituberculate: a round cranium, a big orbit and the long gnawing incisors
    "mesodma": ["......ooooooo...", "....oobbbbbbboo.", "...obbbbbeebbbo.", "..obbbbbbeebbbo.",
                "..obbbbbbbbbbbo.", "..ottbbbbbbbbo..", "...o.obbbbbbo...", ".....oooooooo..."],
    # the land turtle: a blunt deep skull, a big orbit, the hooked beak
    "basilemys": [".......oooooo...", ".....oobbbbbboo.", "...oobbbbbeebbo.", "..obbbbbbbeebbo.",
                  ".obbbbbbbbbbbbo.", "obbbbbbbbbbbbo..", "obbbbbbbbbbbo...", ".oooobbbbbbo....", "....oooooooo...."],
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
    # hornless, a short solid frill, a deep short face with the tall parrot beak
    "leptoceratops": ["..........oooo..", ".........obbbbo.", "......oooobbbbo.", "....oobbbbbeebo.",
                      "..oobbbbbbbeebo.", ".obbbbbbbbbbbo..", "obbbbbbbbbbbo...", "obbbbbbbbbo.....",
                      ".oooooooooo....."],
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
    # the duck: a round cranium and the long flat bill
    "vegavis": ["..........oooo..", "........oobbbbo.", "......oobbbeebo.", "oooooobbbbbeebo.",
                "obbbbbbbbbbbbbo.", "obbbbbbbbbbbbo..", ".oooooobbbbbo...", "........ooooo..."],
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


def skull_grid(sid, g=None, bone0=0, outline=10, hole=11):
    """The skull as tone indices over g (or transparency).  Bone is shaded like a lit object: the top row and the
    pixels under a hole edge catch the light, the lower jaw line and the pixels above holes are in shade, teeth
    are the brightest tone; a couple of suture lines break up the big flat areas."""
    rows = skull_rows(sid)
    out = [row[:] for row in g] if g else pk.grid(CLEAR)
    solid = lambda x, y: 0 <= x < N and 0 <= y < N and rows[y][x] in "blt"  # noqa: E731
    n = pk.clusters("skull2" + sid, [0.3, 0.5, 0.2], periods=(4, 8))
    for y in range(N):
        for x in range(N):
            ch = rows[y][x]
            if ch == "o":
                out[y][x] = outline
            elif ch == "e":
                out[y][x] = hole
            elif ch == "t":
                out[y][x] = bone0 + 4
            elif ch in "bl":
                v = 2 + (1 if ch == "l" else 0) + (n[y][x] - 1) * (1 if ch == "b" else 0)
                if y == 0 or (not solid(x, y - 1) and rows[y - 1][x] != "e"):
                    v = 4  # top edge in the light
                elif not solid(x, y + 1):
                    v = 1  # underside in shade
                if y > 0 and rows[y - 1][x] == "e":
                    v = 1  # shadow cast inside the lower lip of an opening
                if y < N - 1 and rows[y + 1][x] == "e":
                    v = min(4, v + 1)  # lit brow above an opening
                out[y][x] = bone0 + max(0, min(4, v))
    return out


def skull_sprite(sid, bone=BONE_RAMP, outline="#3a3226", hole="#2a241c", base=None):
    g = skull_grid(sid, bone0=20, outline=30, hole=31)
    ex = {20 + i: c for i, c in enumerate(bone)}
    ex.update({30: outline, 31: hole})
    return pk.colour(g, bone, ex)


def skull_fossil(sid):
    """Skull still in the rock: mineralised brown bone, a dark groove where the matrix was dug out around it,
    the rim of the groove lit along its lower edge."""
    rid = SKULL_ERA_ROCK.get(sid, "limestone")
    g = base_grid(rid)
    rows = skull_rows(sid)
    for y in range(N):
        for x in range(N):
            if rows[y][x] == "." and any(0 <= y + dy < N and 0 <= x + dx < N and rows[y + dy][x + dx] != "."
                                         for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                g[y][x] = GAP
    g = skull_grid(sid, g, bone0=20, outline=30, hole=31)
    ex = extra_for(rid)
    ex.update({20 + i: c for i, c in enumerate(FOSSIL_BONE)})
    ex.update({30: "#2e251b", 31: "#241d16"})
    return pk.colour(g, ROCKS[rid]["ramp"], ex)


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
    "stegosaurus": "spots", "pachycephalosaurus": "spots", "maiasaura": "spots", "leptoceratops": "spots",
    "ankylosaurus": "osteoderms", "triceratops": "big_scales", "mosasaurus": "fine_scales",
    "pteranodon": "fuzz", "quetzalcoatlus": "fuzz", "hatzegopteryx": "fuzz",
    "dakotaraptor": "feathers", "troodon": "feathers", "oviraptor": "feathers", "citipati": "feathers", "mononykus": "feathers", "didelphodon": "fuzz", "mesodma": "fuzz", "basilemys": "osteoderms",
    "struthiomimus": "feathers", "deinocheirus": "feathers", "therizinosaurus": "feathers",
    "hesperornis": "feathers", "ichthyornis": "feathers", "vegavis": "feathers",
}


def hide_grid(seed, pattern):
    """Tileable skin as tone indices (0..4 of the species ramp): scales and osteoderms are raised cells in relief
    (lit top/left, shaded bottom/right, dark creases), stripes and spots are darker markings over mottled skin,
    feathers overlap like shingles with a light quill, fuzz is short soft strands."""
    rnd = random.Random(seed + "hide2")
    if pattern in ("scales", "big_scales", "fine_scales", "osteoderms"):
        count = {"scales": 20, "big_scales": 10, "fine_scales": 26, "osteoderms": 7}[pattern]
        owner = pk.regions_from_cells(seed, count, gap=0.7 if pattern != "osteoderms" else 1.1)
        cnt = max(max(r) for r in owner) + 1
        g = pk.clusters(seed + "s", [0.5, 0.5], periods=(8, 16))
        g = [[v + 1 for v in row] for row in g]
        g = pk.per_region(g, owner, cnt, seed + "t", spread=(0, 0, 1), hi=3)
        # each scale: lit along its top only, shaded underneath, dark creases between scales
        for y in range(N):
            for x in range(N):
                o = owner[y][x]
                if o < 0:
                    continue
                if at(owner, x, y + 1) != o:
                    g[y][x] = max(1, g[y][x] - 1)
                elif at(owner, x, y - 1) != o:
                    g[y][x] = min(4, g[y][x] + 1)
                g[y][x] = g[y][x]
        g = [[0 if owner[y][x] < 0 else g[y][x] for x in range(N)] for y in range(N)]
        if pattern == "osteoderms":  # a bony keel in the middle of each plate
            for y in range(N):
                for x in range(N):
                    o = owner[y][x]
                    if o >= 0 and all(at(owner, x + dx, y + dy) == o for dx in (-2, 0, 2) for dy in (-2, 0, 2)):
                        g[y][x] = 4 if at(owner, x, y - 3) != o or at(owner, x - 3, y) != o else 3
        return g
    if pattern == "stripes":
        g = pk.despeckle(pk.clusters(seed + "m", [0.45, 0.55], periods=(4, 8, 16)))
        g = [[v + 1 for v in row] for row in g]
        for y in range(N):
            off = round(2 * math.sin(y / N * 2 * math.pi))
            for x in range(N):
                k = (x + off) % 8
                if k < 2:
                    g[y][x] = 0 if k == 0 else 1
                elif k == 2:
                    g[y][x] = min(4, g[y][x] + 1)  # the pale edge of the stripe
        return g
    if pattern == "spots":
        g = pk.despeckle(pk.clusters(seed + "m", [0.45, 0.55], periods=(4, 8, 16)))
        g = [[v + 1 for v in row] for row in g]
        cells = Cells(seed, 6)
        for y in range(N):
            for x in range(N):
                e = cells.edge[y][x]
                if e > 3.0:
                    g[y][x] = 0
                elif e > 2.4:
                    g[y][x] = min(g[y][x], 1)
        return g
    if pattern == "feathers":  # overlapping contour feathers: long narrow cells, a light quill down each,
        # the lower tip of every feather casting a shadow on the one below
        owner = pk.regions_from_cells(seed + "fe", 11, gap=0.0, sx=1.15, sy=0.85)
        cnt = max(max(r) for r in owner) + 1
        g = pk.clusters(seed + "fm", [0.3, 0.5, 0.2], periods=(8, 16))
        g = [[v + 1 for v in row] for row in g]
        g = pk.per_region(g, owner, cnt, seed + "ft", spread=(-1, 0, 0, 1), hi=4)
        cols = {}
        for y in range(N):
            for x in range(N):
                cols.setdefault(owner[y][x], []).append(x)
        for y in range(N):
            for x in range(N):
                o = owner[y][x]
                if at(owner, x, y + 1) != o:
                    g[y][x] = 0 if at(owner, x - 1, y) == o and at(owner, x + 1, y) == o else 1
                elif at(owner, x - 1, y) != o:
                    g[y][x] = max(0, g[y][x] - 1)
                elif at(owner, x, y - 1) != o:
                    g[y][x] = min(4, g[y][x] + 1)
                xs = sorted(cols[o])
                if x == xs[len(xs) // 2] and at(owner, x, y + 1) == o:
                    g[y][x] = 3  # quill
        return g
    # fuzz (pterosaur pycnofibres): short soft strands combed one way
    g = pk.despeckle(pk.clusters(seed + "fz", [0.19, 0.62, 0.19], periods=(2, 4, 8)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for _ in range(18):
        x, y = rnd.randrange(N), rnd.randrange(N)
        t = rnd.choice((1, 3, 3))
        put(g, x, y, t); put(g, x + 1, y + 1, max(0, t - 1) if t else 1)
    return g


def muted(colors, k=0.35):
    """The ramp pulled k of the way towards grey: tanned skin is duller than the living animal."""
    out = []
    for c in colors:
        r, g_, b, _ = hexc(c)
        lum = 0.3 * r + 0.59 * g_ + 0.11 * b
        out.append("#%02x%02x%02x" % tuple(int(v + (lum - v) * k) for v in (r, g_, b)))
    return out


def hide_pattern(seed, colors, pattern):
    return pk.colour(hide_grid(seed, pattern), muted(colors))


def framed(cv, sides=True, top=True):
    """Stretched on a stick frame and laced to it: round stick posts in relief (lit, mid, shaded), and pairs of
    rawhide laces wrapping the edge of the hide every three pixels."""
    out = copy(cv)
    st = [hexc(c) for c in STICK_RAMP]
    lace, lace_d = hexc("#d8c9a4"), hexc("#a8946c")
    for i in range(N):
        if sides:
            out.set(0, i, st[3]); out.set(15, i, st[1])
        if top:
            out.set(i, 0, st[3]); out.set(i, 15, st[0])
    for i in range(2, N - 1, 3):
        if sides:
            out.set(1, i, lace); out.set(1, i + 1, lace_d); out.set(14, i, lace); out.set(14, i + 1, lace_d)
        if top:
            out.set(i, 1, lace); out.set(i + 1, 1, lace_d); out.set(i, 14, lace); out.set(i + 1, 14, lace_d)
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
    if pattern == "plain":  # scraped hide: uneven thickness in soft patches, a vein, the odd scrape mark
        rnd = random.Random(hid + "2")
        g = pk.despeckle(pk.clusters(hid, [0.05, 0.15, 0.55, 0.18, 0.07], periods=(2, 4, 8)), passes=2)
        x, y = rnd.randrange(N), 0
        for _ in range(16):
            if at(g, x, y) > 1:
                put(g, x, y, at(g, x, y) - 1)
            x += rnd.choice((-1, 0, 0, 1)); y += 1
        for _ in range(3):
            x, y = rnd.randrange(N), rnd.randrange(N)
            pk.fleck(g, x, y, ["44.", ".44"], {"4": 4})
        return pk.colour(g, colors)
    return hide_pattern(hid, colors, pattern)


def bone_cyl(g, x0, y0, length, horizontal=True, b=20, profile=(4, 3, 1)):
    """A long bone lying along an axis (profile = tones across it: lit edge ... shaded edge); knobbed ends."""
    th = len(profile)
    for i in range(length):
        for j, t in enumerate(profile):
            x, y = (x0 + i, y0 + j) if horizontal else (x0 + j, y0 + i)
            put(g, x, y, b + t)
    for end in (0, length - 1):
        for j, t in ((-1, 4), (th, 1)):
            x, y = (x0 + end, y0 + j) if horizontal else (x0 + j, y0 + end)
            put(g, x, y, b + t)


def ossuary():
    """Ossuary wall: skulls and long bones stacked in dark niches, like a charnel wall.  Each skull is lit on
    the crown, has dark eye sockets and nasal hole, and teeth catching the light."""
    g = pk.grid(10)
    sk = [".1222.", "133332", "300300", "322223", ".2442."]
    for oy, ox in ((1, 0), (1, 8), (9, 4), (9, 12)):
        for y, row in enumerate(sk):
            for x, ch in enumerate(row):
                if ch == "0":
                    put(g, ox + 1 + x, oy + y, 11)
                elif ch != ".":
                    put(g, ox + 1 + x, oy + y, 20 + int(ch) + (1 if y == 0 else 0))
        for x in range(1, 7):
            put(g, ox + x, oy + 5, 11)  # shadow under the skull
    for y0 in (6, 14):
        for x in range(N):
            put(g, x, y0, 23 if x % 5 else 24)
            put(g, x, y0 + 1, 21 if x % 5 else 22)
    ex = {10: "#2a241c", 11: "#16120e"}
    ex.update({20 + i: c for i, c in enumerate(BONE_RAMP)})
    return pk.colour(g, BONE_RAMP, ex)


def rib_bone():
    """Rib bone (arch): two curved ribs side by side, each a lit edge, body and shaded edge, porous here and there."""
    g = pk.grid(0)
    rnd = random.Random("rib2")
    for y in range(N):
        for x in range(N):
            k = x % 8
            g[y][x] = (1, 3, 4, 4, 3, 3, 2, 1)[k]
    for _ in range(7):
        put(g, rnd.randrange(N), rnd.randrange(N), 1)
    return pk.colour(g, BONE_RAMP)


def tooth_totem(top):
    """A post wrapped in rings of big teeth tied with sinew; the top is the post's cut end."""
    if top:
        g = pk.grid(2)
        for y in range(N):
            for x in range(N):
                d = math.hypot(x - 7.5, y - 7.5)
                g[y][x] = 1 if (d + 0.5) % 2.5 < 0.9 else 2
                if max(abs(x - 7.5), abs(y - 7.5)) > 6.6:
                    g[y][x] = 0
        return pk.colour(g, STICK_RAMP)
    g = pk.despeckle(pk.clusters("totempost", [0.19, 0.62, 0.19], periods=(2, 4, 8), stretch=(2.0, 0.25)), passes=2)
    g = [[v for v in row] for row in g]
    for y0 in (0, 8):
        for x0 in range(0, N, 4):  # a ring of teeth hanging point-down: each tooth lit on its left flank
            for dy, (w, lit) in enumerate(((3, 1), (3, 1), (2, 1), (2, 0), (1, 0))):
                for dx in range(w):
                    t = 24 if dx < lit else (22 if dx == w - 1 and w > 1 else 23)
                    put(g, x0 + dx + (3 - w + 1) // 2, y0 + 1 + dy, t)
            put(g, x0 + 2, y0 + 6, 0)  # shadow under the tip
        for x in range(N):
            put(g, x, y0, 30 if x % 3 else 31)
    ex = {20 + i: c for i, c in enumerate(BONE_RAMP)}
    ex.update({30: "#5e3a20", 31: "#8a5a34"})
    return pk.colour(g, STICK_RAMP, ex)


def bone_pile():
    """Loose bones on bare earth: long bones with knobbed ends, each casting a shadow on the soil."""
    g = pk.despeckle(pk.clusters("bonepile2", [0.19, 0.62, 0.19], periods=(2, 4, 8)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for x, y, horizontal, length in ((1, 1, True, 8), (11, 5, False, 8), (2, 9, True, 6), (13, 0, False, 3),
                                     (5, 13, True, 7)):
        if (x, y) == (13, 0):
            continue
        for i in range(length + 1):  # shadow on the soil, under and right of the bone
            xx, yy = (x + i, y + 2) if horizontal else (x + 2, y + i)
            put(g, xx, yy, 0)
        bone_cyl(g, x, y, length, horizontal, profile=(4, 2))
    ex = {20 + i: c for i, c in enumerate(BONE_RAMP)}
    return pk.colour(g, EARTH_RAMP, ex)


FEATHER_RAMP = ["#2a2420", "#4a3a2c", "#6e5a42", "#9c8466", "#c8b496"]


def feather_bundle(top):
    """Long feathers bundled upright: each feather 4 px wide with a light quill, barbs slanting down from it
    (lit above the quill side, shaded on the outer edge), held by two sinew bands."""
    if top:  # the cut quill ends inside the bundle
        g = pk.despeckle(pk.clusters("feathertop2", [0.19, 0.62, 0.19], periods=(4, 8)), passes=2)
        g = [[v + 1 for v in row] for row in g]
        for y in range(1, N, 4):
            for x in range(2 if (y // 4) % 2 else 0, N, 4):
                pk.fleck(g, x, y, ["4", "0"], {"4": 4, "0": 0})
        return pk.colour(g, FEATHER_RAMP)
    rnd = random.Random("feather2")
    tone = [rnd.choice((-1, 0, 0, 1)) for _ in range(4)]
    g = pk.grid(2)
    for y in range(N):
        for x in range(N):
            f, cx = x // 4, x % 4
            if cx == 2:
                v = 4
            else:
                barb = (y + (2 - cx if cx < 2 else cx - 2)) % 3 == 0
                v = (1 if cx == 0 else 3 if cx == 1 else 2) + (1 if barb and cx else 0) - (1 if barb and not cx else 0)
                v += tone[f]
            g[y][x] = max(0, min(4, v))
    for y in (4, 12):
        for x in range(N):
            g[y][x] = 30 if x % 3 else 31
            g[y + 1][x] = max(0, g[y + 1][x] - 2)
    return pk.colour(g, FEATHER_RAMP, {30: "#5e3a20", 31: "#8a5a34"})


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
    """Rendered fat in a stone bowl: waxy, in three soft tones, a burnt ring and the black wick in the middle."""
    g = pk.despeckle(pk.clusters("fat2", [0.19, 0.62, 0.19], periods=(4, 8)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for y in range(N):
        for x in range(N):
            d = abs(x - 7.5) + abs(y - 7.5)
            if d < 1.5:
                g[y][x] = 10
            elif d < 3:
                g[y][x] = 0
    return pk.colour(g, ["#6e6040", "#8a7a50", "#a8966a", "#c4b384", "#d8c99c"], {10: "#1e1610"})


def ash():
    """Hearth ash: grey flakes in clumps, charcoal bits, a few glowing embers."""
    rnd = random.Random("ash2")
    g = pk.despeckle(pk.clusters("ash2", [0.1, 0.2, 0.55, 0.15], periods=(2, 4, 8)), passes=2)
    for _ in range(6):  # charcoal
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, ["01"], {"0": 10, "1": 0})
    for _ in range(5):  # embers: hot core with a dull rim
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, ["ab"] if rnd.random() < 0.5 else ["a"], {"a": 12, "b": 11})
    return pk.colour(g, ["#2a2622", "#3e3934", "#57514a", "#76706a"], {10: "#141210", 11: "#8a2e10", 12: "#e07a24"})


def dried_meat():
    """Strips of dried meat hung side by side: dark red flesh, a lit edge on each strip, white fat marbling."""
    rnd = random.Random("jerky2")
    g = pk.grid(2)
    grain = pk.clusters("jerkyg", [0.3, 0.45, 0.25], periods=(4, 8, 16), stretch=(2.0, 0.25))
    for y in range(N):
        for x in range(N):
            k = x % 4
            g[y][x] = max(0, min(3, grain[y][x] + (1 if k == 0 else 0) - (1 if k == 3 else 0) + 1))
            if k == 3 and (y + x) % 5 == 0:
                g[y][x] = 0
    for _ in range(9):  # fat streaks running along the strips
        x, y = rnd.randrange(N), rnd.randrange(N)
        if x % 4 in (1, 2):
            for i in range(rnd.randint(2, 4)):
                put(g, x, y + i, 4)
    return pk.colour(g, ["#3a1210", "#5a1c16", "#74281e", "#8e3a2a", "#c49a7a"])


CLAY_RAW = ["#6e5a48", "#86705c", "#9c8670", "#b09a84", "#c2ad97"]
CLAY_FIRED = ["#5e2c18", "#7a3a20", "#96502e", "#ae663e", "#c27c50"]


def clay_pot(fired, top=False):
    """Hand-built pot: coils of clay round the body (each coil lit on top, a shadow line under it); the fired one
    is red-brown with soot clouds from the open fire.  Top: thick rim round the dark inside."""
    colors = CLAY_FIRED if fired else CLAY_RAW
    if top:
        g = pk.grid(2)
        for y in range(N):
            for x in range(N):
                d = max(abs(x - 7.5), abs(y - 7.5))
                if d < 2.5:
                    g[y][x] = 10 if d < 1.5 else 11
                elif d < 3.5:
                    g[y][x] = 4 if (x < 8 and y < 8) else 1  # lit rim edge
                else:
                    g[y][x] = 3 if y < 8 else 2
        return pk.colour(g, colors, {10: "#140f0b", 11: "#2a1f17"})
    rnd = random.Random("pot2" + str(fired))
    g = pk.despeckle(pk.clusters("pot2" + str(fired), [0.19, 0.62, 0.19], periods=(2, 4, 8)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for y in range(N):
        for x in range(N):
            if y % 3 == 0:
                g[y][x] = min(4, g[y][x] + 1)  # top of the coil
            elif y % 3 == 2:
                g[y][x] = max(0, g[y][x] - 1)  # under the coil
    for _ in range(4):  # finger smoothing marks
        x, y = rnd.randrange(N), rnd.randrange(N)
        put(g, x, y, 0); put(g, x + 1, y, 0)
    if fired:
        soot = pk.Noise("soot2", periods=(2, 4), weights=(0.6, 0.4))
        for y in range(N):
            for x in range(N):
                if soot(x, y) > 0.66:
                    g[y][x] = 20 + min(2, g[y][x] // 2)
    return pk.colour(g, colors, {20: "#1e1712", 21: "#2e2018", 22: "#40281c"})


def basin_water():
    """Still water in a stone basin: deep blue in three tones with soft ripple lines and two glints."""
    g = pk.despeckle(pk.clusters("water2", [0.19, 0.62, 0.19], periods=(2, 4, 8), stretch=(1.5, 1.0)), passes=2)
    rnd = random.Random("water2")
    for _ in range(5):
        x, y = rnd.randrange(N), rnd.randrange(N)
        for i in range(rnd.randint(3, 5)):
            put(g, x + i, y, 3)
    for _ in range(2):
        put(g, rnd.randrange(N), rnd.randrange(N), 4)
    return pk.colour(g, ["#1e3a5a", "#28507a", "#346694", "#4a80aa", "#8ab4d0"])


def hide_bedroll():
    """Furred hide bedroll: thick hair lying in short tufts, each tuft lit at its root and dark at its tip."""
    rnd = random.Random("bedroll2")
    g = pk.despeckle(pk.clusters("bedroll2", [0.19, 0.62, 0.19], periods=(2, 4, 8), stretch=(1.0, 2.0)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for _ in range(28):
        x, y = rnd.randrange(N), rnd.randrange(N)
        put(g, x, y, 4); put(g, x, y + 1, 3); put(g, x + 1, y + 2, 0)
    return pk.colour(g, ["#3a2618", "#55392a", "#70503a", "#8a6a4e", "#a6866a"])


def hammock_cloth():
    """Bark-cloth hammock: beaten fibre in soft vertical bands, the faint weave of the beating, cords at the edges."""
    g = pk.despeckle(pk.clusters("hammock2", [0.19, 0.62, 0.19], periods=(2, 4, 8), stretch=(2.0, 0.5)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for y in range(N):
        for x in range(N):
            if x % 3 == 0 and y % 2 == 0:
                g[y][x] = max(1, g[y][x] - 1)
        g[y][0], g[y][1], g[y][15] = 0, 3, 0
    return pk.colour(g, ["#4e3e28", "#6a5638", "#86704c", "#a08a62", "#b8a278"])


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
    """Brush laid over a pit: leafy twigs on crossed sticks, the dark hole showing through the gaps."""
    rnd = random.Random("pit2")
    g = pk.despeckle(pk.clusters("pit2", [0.05, 0.15, 0.55, 0.18, 0.07], periods=(2, 4, 8)), passes=2)
    g = [[10 if v == 0 else v - 1 for v in row] for row in g]
    for _ in range(5):  # sticks: lit top, shaded under
        x, y = rnd.randrange(N), rnd.randrange(N)
        for i in range(rnd.randint(5, 9)):
            put(g, x + i, y + i // 2, 21); put(g, x + i, y + i // 2 + 1, 20)
    for _ in range(10):  # leaves catching the light
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, ["43", ".2"], {"4": 4, "3": 3, "2": 2})
    return pk.colour(g, OLIVE, {10: "#120e0a", 20: "#3a2814", 21: "#87623a"})


def menhir(top):
    """Weathered standing stone: grey grain running up the stone, rain-smoothed, patches of crusty yellow lichen
    (each patch with a lit rim) and a few dark pits."""
    rnd = random.Random("menhir2" + str(top))
    g = pk.despeckle(pk.clusters("menhir2" + str(top), [0.05, 0.15, 0.55, 0.18, 0.07], periods=(2, 4, 8),
                                 stretch=(2.0, 0.5) if not top else (1.0, 1.0)))
    lic = pk.Noise("menhirlichen", periods=(4, 8), weights=(0.5, 0.5))
    for y in range(N):
        for x in range(N):
            v = lic(x, y)
            if v > 0.74:
                g[y][x] = 20 + (2 if v > 0.82 else 1)
            elif v > 0.71:
                g[y][x] = 20
    for _ in range(4):
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, ["0", "4"], {"0": 0, "4": 4})
    return pk.colour(g, ["#4a4a4c", "#5e5e60", "#727274", "#88888a", "#9c9c9c"],
                     {20: "#6e6c50", 21: "#a8a47a", 22: "#c4bc84"})


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


TOTEM_WOOD = ["#4a3220", "#5e4029", "#765236", "#8c6444", "#a27852"]


def totem(face):
    """A carved post: bark-free wood with vertical grain and, on the front, the carved face: deep cuts dark,
    the carved ridges lit, ochre paint in two tones."""
    g = pk.despeckle(pk.clusters("totem2", [0.1, 0.2, 0.55, 0.15], periods=(2, 4, 8), stretch=(2.0, 0.25)), passes=2)
    g = [[v for v in row] for row in g]
    rnd = random.Random("totemcuts")
    for _ in range(4):  # adze facets on the post
        x, y = rnd.randrange(N), rnd.randrange(N)
        put(g, x, y, 4); put(g, x, y + 1, 3)
    if face:
        for y, row in enumerate(TOTEM_FACES[face]):
            for x, ch in enumerate(row):
                if ch == "d":
                    g[y][x] = 10
                elif ch == "l":
                    g[y][x] = 4 if y > 0 and TOTEM_FACES[face][y - 1][x] == "d" else 3
                elif ch == "p":
                    g[y][x] = 11 if y > 0 and TOTEM_FACES[face][y - 1][x] == "d" else 12
    return pk.colour(g, TOTEM_WOOD, {10: "#2a1c12", 11: "#6e2818", 12: "#8e3420"})


def totem_top():
    g = pk.grid(2)
    for y in range(N):
        for x in range(N):
            d = 0.6 * max(abs(x - 7.5), abs(y - 7.5)) + 0.4 * math.hypot(x - 7.5, y - 7.5)
            g[y][x] = 1 if (d + 0.6) % 2.5 < 0.9 else 3
            if max(abs(x - 7.5), abs(y - 7.5)) > 6.6:
                g[y][x] = 0
    put(g, 7, 7, 0)
    return pk.colour(g, TOTEM_WOOD)


def drum(part):
    """Drum: a hollowed log laced with sinew from rim to rim (the laces zig-zag, each lit on one side); the head
    is stretched rawhide, pale in the middle where it is beaten, pegged round the rim."""
    if part == "head":
        g = pk.despeckle(pk.clusters("drumhead2", [0.19, 0.62, 0.19], periods=(4, 8)), passes=2)
        g = [[v + 1 for v in row] for row in g]
        for y in range(N):
            for x in range(N):
                d = max(abs(x - 7.5), abs(y - 7.5))
                if d >= 7:
                    g[y][x] = 20 if (x + y) % 3 else 21
                elif d >= 6:
                    g[y][x] = 0 if (x + y) % 4 == 0 else 1
                elif d < 2.5:
                    g[y][x] = min(4, g[y][x] + 1)
        return pk.colour(g, RAWHIDE_RAMP, {20: "#54391d", 21: "#3a2814"})
    g = pk.despeckle(pk.clusters("drumside2", [0.19, 0.62, 0.19], periods=(2, 4, 8), stretch=(0.5, 2.0)), passes=2)
    g = [[20 + v for v in row] for row in g]
    for y in range(N):
        for x in range(N):
            if y < 2:
                g[y][x] = 3 if y == 0 else 1
            elif y < 12:
                a, b = (x + y) % 6, (x - y) % 6
                if a == 0 or b == 0:
                    g[y][x] = 4 if a == 0 else 2
                elif a == 1 or b == 5:
                    g[y][x] = 20
            elif y == 12:
                g[y][x] = 0
    return pk.colour(g, ["#3a2814", "#8a7356", "#a68c6a", "#bba07c", "#d8c9a4"],
                     {20: "#3a2814", 21: "#54391d", 22: "#6e4d2a"})


def basket_lid():
    """Woven lid seen from above: a spiral of coiled reed, each coil lit on its outer side, a knot in the middle."""
    g = pk.grid(2)
    for y in range(N):
        for x in range(N):
            ang = math.atan2(y - 7.5, x - 7.5)
            r = math.hypot(x - 7.5, y - 7.5) + ang / math.tau * 2.0
            ph = r % 2.0
            stitch = int((ang + math.pi) / math.tau * 16) % 4 == 0
            g[y][x] = 0 if ph < 0.45 else (4 if ph < 1.0 else 3 if ph < 1.5 else 2)
            if stitch and ph >= 0.45:
                g[y][x] = 1
    pk.fleck(g, 7, 7, ["43", "21"], {"4": 4, "3": 3, "2": 2, "1": 1})
    return pk.colour(g, WICKER_RAMP)


def firewood(end):
    """Split firewood stacked crosswise: the split ends (rings, bark rim, a lit top-left edge), or the long sides
    (bark-covered pieces in rows, dark gaps between)."""
    if end:
        owner = pk.regions_from_cells("firewood2", 9, gap=0.7)
        cnt = max(max(r) for r in owner) + 1
        cells = Cells("firewood2", 9)
        g = pk.grid(0)
        for y in range(N):
            for x in range(N):
                o = owner[y][x]
                if o < 0:
                    g[y][x] = 10
                    continue
                e = cells.edge[y][x]
                g[y][x] = 20 if e < 1.3 else (2 if int(e) % 2 else 3)
        g = pk.relief(g, owner, 4, joint=10, light=1, dark=-1, corner=False)
        return pk.colour(g, ["#6e4c2a", "#8a6438", "#a47a48", "#bc9058", "#d0a46a"],
                         {10: "#1e140c", 19: "#2e2014", 20: "#46321f", 21: "#5e452c"})
    g = pk.despeckle(pk.clusters("firewoodside2", [0.19, 0.62, 0.19], periods=(2, 4, 8), stretch=(0.25, 2.0)), passes=2)
    for y in range(N):
        for x in range(N):
            k = y % 4
            g[y][x] = 0 if k == 3 else max(0, min(4, g[y][x] + (2 if k == 0 else 1 if k == 1 else 0)))
    return pk.colour(g, ["#1e140c", "#4a3220", "#6a4a2c", "#8a6438", "#a47a48"])


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


def amber_grid(kind):
    """Amber as tone indices of AMBER_RAMP (0..5)."""
    rnd = random.Random("amber2" + kind)
    if kind == "mosaic":  # polished pieces set in dark resin, each with its own tone and a glint
        owner = pk.regions_from_cells("ambermosaic2", 10, gap=0.8)
        cnt = max(max(r) for r in owner) + 1
        g = pk.clusters("ambm", [0.4, 0.6], periods=(8, 16))
        g = [[v + 2 for v in row] for row in g]
        g = pk.per_region(g, owner, cnt, "ambmt", spread=(-1, 0, 1, 1), hi=5)
        g = pk.relief(g, owner, 5, joint=0, light=1, dark=-1, corner=False)
        return g
    if kind == "polished":  # smooth deep amber, a long diagonal light streak and a softer reflection
        g = pk.despeckle(pk.clusters("ambp", [0.19, 0.62, 0.19], periods=(4, 8)), passes=2)
        g = [[v + 2 for v in row] for row in g]
        for y in range(N):
            for x in range(N):
                k = (x + y) % 16
                if k in (3, 4):
                    g[y][x] = 5 if k == 3 else 4
                elif k == 5:
                    g[y][x] = max(1, g[y][x] - 1)
        return g
    g = pk.despeckle(pk.clusters("ambraw", [0.04, 0.1, 0.2, 0.45, 0.15, 0.06], periods=(2, 4, 8)), passes=2)
    for _ in range(6):  # bubbles caught in the resin: bright top-left, dark lower edge
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, ["5.", ".1"], {"5": 5, "1": 1})
    return g


def amber(kind):
    return pk.colour(amber_grid(kind), AMBER_RAMP)


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
    """Polished amber with something caught inside: the body seen through the resin is a darker amber, not black,
    and its light parts keep a hint of their own colour."""
    g = amber_grid("polished")
    for y, row in enumerate(INCLUSIONS[kind]):
        for x, ch in enumerate(row):
            if ch == "d":
                g[y][x] = 10
            elif ch == "l":
                g[y][x] = 11
    ex = {10: "#2e1a0a", 11: "#6a4a1a" if kind != "leaf" else "#4a5220"}
    return pk.colour(g, AMBER_RAMP, ex)


def resin_block():
    """Fresh resin set hard: paler and cloudy, drips running down, each drip lit on the left and fat at the end."""
    rnd = random.Random("resin2")
    g = pk.despeckle(pk.clusters("resin2", [0.19, 0.62, 0.19], periods=(2, 4, 8), stretch=(1.0, 0.5)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for _ in range(4):
        x, y = rnd.randrange(N), rnd.randrange(N)
        ln = rnd.randint(4, 8)
        for i in range(ln):
            put(g, x, y + i, 4); put(g, x + 1, y + i, 2)
        put(g, x, y + ln, 3); put(g, x + 1, y + ln, 1); put(g, x, y + ln + 1, 0)
    return pk.colour(g, ["#7a5a1e", "#a07a2c", "#c49c40", "#dcb85a", "#ecd07c"])


def amber_lantern(top):
    """Lantern: polished amber panes held in a bone frame; the light glows brightest in the middle of each pane."""
    if top:
        g = pk.grid(2)
        for y in range(N):
            for x in range(N):
                g[y][x] = 4 if (x in (0, 1) or y in (0, 1)) else 1 if (x in (14, 15) or y in (14, 15)) else \
                    (3 if (x + y) % 4 else 2)
        return pk.colour(g, BONE_RAMP)
    g = pk.grid(0)
    for y in range(N):
        for x in range(N):
            if x in (0, 7) or y in (0, 1):
                g[y][x] = 13
            elif x in (8, 15) or y in (14, 15):
                g[y][x] = 11 if x == 15 or y == 15 else 12
            else:
                px_ = x - 1 if x < 7 else x - 9  # 0..5 inside the pane
                d = max(abs(px_ - 2.5), abs(y - 7.5) / 2.2)
                g[y][x] = 5 if d < 1 else 4 if d < 2 else 3 if d < 2.8 else 2
    ex = {11: BONE_RAMP[0], 12: BONE_RAMP[2], 13: BONE_RAMP[3]}
    return pk.colour(g, AMBER_RAMP, ex)


def amber_textures():
    out = {"amber_block": amber("raw"), "polished_amber": amber("polished"), "amber_mosaic": amber("mosaic"),
           "resin_block": resin_block(), "amber_lantern": amber_lantern(False), "amber_lantern_top": amber_lantern(True)}
    for kind in INCLUSIONS:
        out[f"amber_with_{kind}"] = amber_inclusion(kind)
    return out


# ------------------------------------------------------------------ Cretaceous soils
SOIL_RAMP = ["#3a2a1c", "#4e3a28", "#634a34", "#785c42", "#8c6e52"]


def litter(kind, side):
    """Forest floor: fallen fern fronds (brown and a few still green) or conifer needles over dark soil; each bit
    lit along its top and casting a one-pixel shadow.  The side shows soil with the litter only along the top."""
    rnd = random.Random("litter2" + kind + str(side))
    g = pk.despeckle(pk.clusters("litter2" + kind, [0.19, 0.62, 0.19], periods=(2, 4, 8)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    cols = ([20, 21, 22, 23, 24] if kind == "fern" else [30, 31, 32, 33])
    rows = range(0, 3) if side else range(N)
    for _ in range(36 if not side else 12):
        x, y = rnd.randrange(N), rnd.choice(list(rows))
        length = rnd.randint(2, 4)
        dx = rnd.choice((1, -1))
        c = rnd.choice(cols)
        for i in range(length):
            yy = y + (i // 2 if kind == "fern" else i % 2)
            if side and yy > 3:
                break
            put(g, x + dx * i, yy, c)
            if not side and at(g, x + dx * i, yy + 1) < 10:
                put(g, x + dx * i, yy + 1, 0)
    if side:
        for x in range(N):
            if rnd.random() < 0.7:
                put(g, x, 0, rnd.choice(cols[:3]))
        for y in range(4, N):
            for x in range(N):
                if g[y][x] >= 10:
                    g[y][x] = 2
    ex = {20: "#5a3e1e", 21: "#7a5428", 22: "#94683a", 23: "#4a6a2a", 24: "#6a8a38",
          30: "#6a3a1a", 31: "#8a4e22", 32: "#a8642c", 33: "#c47c3a"}
    return pk.colour(g, SOIL_RAMP, ex)


def cracked_mud():
    """Mud dried in the sun: pale polygons curling up at the edges (lit rims), deep dark cracks between them."""
    owner = pk.regions_from_cells("mudcracks2", 7, gap=0.5)
    g = pk.despeckle(pk.clusters("mudc", [0.19, 0.62, 0.19], periods=(4, 8)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    g = pk.relief(g, owner, 4, joint=10, light=1, dark=-1, corner=False)
    return pk.colour(g, ["#5e4e3c", "#7e6c56", "#928066", "#a69478", "#b8a68a"], {10: "#2e2218"})


def volcanic_ash(layer=False):
    """Fine grey volcanic ash: soft drifts, a few dark cinders and glassy specks."""
    rnd = random.Random("vash2" + str(layer))
    g = pk.despeckle(pk.clusters("ash2" + str(layer), [0.1, 0.2, 0.55, 0.15], periods=(2, 4, 8)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for _ in range(6):
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, ["0"] if rnd.random() < 0.6 else ["4"], {"0": 0, "4": 4})
    return pk.colour(g, ["#5e5a56", "#6e6a66", "#827e78", "#96928c", "#aaa6a0"])


def peat():
    """Peat: dark, wet, half-rotten plant fibres lying flat, a few paler root threads."""
    rnd = random.Random("peat2")
    g = pk.despeckle(pk.clusters("peat2", [0.1, 0.2, 0.55, 0.15], periods=(2, 4, 8), stretch=(0.5, 2.0)), passes=2)
    for _ in range(6):
        x, y = rnd.randrange(N), rnd.randrange(N)
        for i in range(rnd.randint(3, 5)):
            put(g, x + i, y + (i // 3), 4)
    return pk.colour(g, ["#2a1e14", "#3a2a1c", "#4a3826", "#5a4630", "#7a6244"])


def lateritic_soil():
    """Red tropical soil rich in iron, in crumbs, with small hard nodules (dark, lit on top)."""
    rnd = random.Random("latsoil2")
    g = pk.despeckle(pk.clusters("latsoil2", [0.1, 0.2, 0.55, 0.15], periods=(2, 4, 8)), passes=2)
    g = [[v + 1 for v in row] for row in g]
    for _ in range(8):
        x, y = rnd.randrange(N), rnd.randrange(N)
        pk.fleck(g, x, y, ["a", "0"], {"a": 10, "0": 0})
    return pk.colour(g, ["#4a1e10", "#5a2414", "#74301c", "#8c3e24", "#a24e2e"], {10: "#c47850"})


def salt_crust():
    """Salt left by an evaporated lagoon: white crystalline polygons with raised rims over grey sand."""
    owner = pk.regions_from_cells("salt2", 9, gap=0.0)
    cells = Cells("salt2", 9)
    g = pk.despeckle(pk.clusters("salt2n", [0.19, 0.62, 0.19], periods=(4, 8)), passes=2)
    for y in range(N):
        for x in range(N):
            e = cells.edge[y][x]
            if e < 0.6:
                g[y][x] = 10 + (1 if at(owner, x, y - 1) == owner[y][x] else 2)  # raised rim, lit side
            elif e < 1.2:
                g[y][x] = 0  # shadow beside the rim
            else:
                g[y][x] = g[y][x] + 1
    return pk.colour(g, ["#9a9486", "#a8a294", "#bcb6a8", "#d0cabc"], {11: "#e8e4dc", 12: "#ffffff"})


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


# textures whose subject is a strong light/dark motif may keep more contrast (vanilla: cobblestone 84, oak leaves 86,
# hay 97); everything else is held to 68, near the vanilla median of 64 (see pixelkit.tame)
TAME_CAPS = (("ossuary_wall", 120), ("flint", 120), ("mossy_", 80), ("cave_painting_", 120), ("_skull_fossil", 100),
             ("amber_with_", 96), ("_totem_front", 96), ("_leaves", 84), ("thatch", 84), ("salt_crust", 84))


def tame_cap(name):
    return next((cap for key, cap in TAME_CAPS if key in name), 68.0)


def from_image(img):
    cv = Canvas()
    for y in range(N):
        for x in range(N):
            c = img.getpixel((x, y))
            if c[3] > 0:
                cv.set(x, y, tuple(c))
    return cv


def seed_of(name):
    return sum((i + 1) * ord(ch) for i, ch in enumerate(name)) % 9973


def fossil_on_rock(sid, rock_img, old):
    """The skull and its dug-out groove from the old drawing, laid into the new rock face of its era."""
    rows = skull_rows(sid)
    out = from_image(rock_img)
    for y in range(N):
        for x in range(N):
            near = any(0 <= y + dy < N and 0 <= x + dx < N and rows[y + dy][x + dx] != "."
                       for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if near:
                out.set(x, y, old.get(x, y))
    return out


def build():
    """Surfaces (rocks, woods, thatch, daub, plaster, earth, soils, amber, hides) come from the texpack engine
    (tools/texpack/blocos.py), fitted to the vanilla block of the same role; the drawn motifs (skulls, totems,
    paintings, doors, pots, plants...) are drawn here and tamed to vanilla contrast."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "texpack"))
    import blocos as BL  # noqa: E402
    out = {}
    for rid in ROCKS:
        out.update(rock_textures(rid))
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
    out = {name: pk.tame(cv, tame_cap(name)) for name, cv in out.items()}  # vanilla-like contrast
    engine = BL.textures(inclusions=INCLUSIONS)
    for sid in SPECIES:
        engine[f"{sid}_hide_rug"] = BL.hide(HIDE_PATTERN.get(sid, "scales"), species_ramp(sid)[2], seed_of(sid))
        rock = SKULL_ERA_ROCK.get(sid, "limestone")
        out[f"{sid}_skull_fossil"] = fossil_on_rock(sid, engine[rock], out[f"{sid}_skull_fossil"])
    for hid, (src, pattern) in GENERIC_HIDES.items():
        colour = species_ramp(src)[2] if isinstance(src, str) else src[2]
        skin = from_image(BL.hide(pattern, colour, seed_of(hid), muted=0 if pattern == "plain" else 0.35))
        out[f"{hid}_frame"] = framed(skin)
        if hid != "rawhide":
            out[f"{hid}_panel"] = framed(skin, top=False)
    for name, img in engine.items():
        if name not in out:
            raise SystemExit(f"texpack drew {name}, which no block uses")
        out[name] = from_image(img)
    for name, msg in BL.drift(engine).items():
        print("  off vanilla:", name, msg)
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
