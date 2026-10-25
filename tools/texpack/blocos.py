"""Terrassic primitive building blocks drawn with the texpack engine (tex, stamps, fit), the same way the era packs
redraw vanilla terrain, so mod blocks and pack blocks read as one hand.

Every texture follows the pack recipe:
  1. a tone map: a calm base (one main tone, a few large patches) plus hand-designed details stamped where a
     blue-noise pattern says (ledges lit on top with a shadow under, pits, chips, grain);
  2. a palette fitted (fit.py) so the image hits a target: the BRIGHTNESS of the real material (our own colour, a
     chalk is light, a shale is dark) and the CONTRAST of the vanilla block that plays the same role (natural rock ->
     stone/andesite/tuff, dry-laid wall -> stone_bricks/cobblestone, planks -> oak_planks, thatch -> hay_block, ...);
  3. hue and saturation come from the material's own colour, shadows cooler, lights warmer.

ROLE says which vanilla block each texture is held to; drift() lists the ones far from it.
Since 25/10 the GROUND (rocks, soils, raw amber) comes from chao.py and the leaves from folhas.py: the style Rodrigo
approved, made to not repeat from afar (fine grain, clods, calm colours).
Called from tools/spritegen/blocks.py, which writes the PNGs.
"""
import colorsys

import numpy as np
from PIL import Image

import api
import tex as T
from fit import fit
from materials import material
from stamps import base, poisson, stamp
from tex import N
from vanilla import target

W = np.array([0.299, 0.587, 0.114])


# ------------------------------------------------------------------ colour helpers
def hsv_of(hexcol):
    r, g, b = T.hexrgb(hexcol)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h, s, (np.array([r, g, b]) @ W)


def pal(t, mat, role=None, n=5, dl=0.0, mask=None):
    """Ramp of n tones fitted to material `mat` (materials.py): its own brightness and hue; with `role`, the
    contrast of that vanilla block instead (a wall of chalk has the contrast of stone_bricks, not of calcite)."""
    m = material(mat)
    if role:
        m = m.like(dc=m.dc + target(role)[1] - target(m.ref)[1])
    if dl:
        m = m.like(dl=m.dl + dl)
    return api.palette(np.clip(np.asarray(t), 0, n - 1), m, mask, n=n)


def img(t, pal, alpha=None):
    return T.colorize(np.asarray(t), pal, alpha)


# texture name -> the vanilla block whose contrast it is held to (see drift())
ROLE = {}  # texture name -> vanilla role (filled by each family)


# ------------------------------------------------------------------ rocks
# drawn in chao.py (fine grain, approved 25/10): base, stacked, flagstone, pebbles, mossy stacked per rock
ROCKS = ("limestone", "shale", "chalk", "flint", "laterite", "quartzite", "gneiss", "conglomerate")


CLAST_COLOURS = ["#cfc8b8", "#3e3a38", "#b08c5a", "#9a8a84"]  # quartz, chert, sandstone, granite


# ---- dry-laid stones: courses of squared stones, each with its own body tone, lit top/left rim, shadowed
# bottom/right rim and a dark joint; the rock's own grain shows inside each stone
def bevel(idx, round_corners=True):
    gap = T.cell_edges(idx)
    if round_corners:  # knock the corner pixel of each stone into the joint, so stones look worn, not cut
        g2 = gap.copy()
        for y in range(N):
            for x in range(N):
                if not gap[y, x] and gap[(y + 1) % N, x] and gap[y, (x + 1) % N]:
                    g2[y, x] = True
        gap = g2
    hi = (T.roll(gap, -1, 0) | T.roll(gap, 0, -1)) & ~gap
    lo = (T.roll(gap, 1, 0) | T.roll(gap, 0, 1)) & ~gap & ~hi
    return gap, hi, lo


MOSS = ["#3d4f2a", "#506a32", "#66843c", "#7d9a48"]


SOIL = "#6a5640"


def rock_textures(rid):
    """Fine grain since 25/10 (chao.py, the style Rodrigo approved): nothing that repeats from afar."""
    import chao
    out = chao.rock_textures(rid)
    ROLE.update({rid: material("chalk" if rid == "flint" else rid).ref, f"{rid}_stacked": "stone_bricks", f"{rid}_flagstone": "stone_bricks",
                 f"mossy_{rid}_stacked": "mossy_stone_bricks", f"{rid}_pebbles": "gravel"})
    return out


# ------------------------------------------------------------------ woods
import leaves as LV  # noqa: E402
import woods as WD  # noqa: E402

# id: bark colour, wood colour, leaf colour (mid tones of the real tree), bark style, ring spacing,
# leaf shapes (leaves.CH letters: H lit, B leaf, D shade, V vein), see-through share, leaf spacing
WOODS = {
    "araucaria": ("#5a4a3b", "#cdb07e", "#2f5632", "scales", 2.3, "spiky", .30, 1.8),
    "ginkgo": ("#615a50", "#d6c29a", "#5e8a2c", "furrows", 2.5, "fans", .34, 2.4),
    "metasequoia": ("#723a25", "#bf8266", "#517c36", "fibres", 2.2, "feathery", .36, 1.7),
    "taxodium": ("#5b5045", "#c49f75", "#4c6b31", "fibres", 2.4, "feathery", .36, 1.7),
    "tree_fern": ("#43321f", "#83623e", "#46732c", "fern_bases", 2.0, "fronds", .38, 2.0),
    "sabal": ("#6e6150", "#ccb48c", "#507230", "palm_bases", 2.6, "palm", .40, 2.6),
    "magnolia": ("#6e6a62", "#d8c49e", "#305a34", "smooth", 2.3, "broad", .26, 2.4),
    "podocarpus": ("#6c442d", "#cc985c", "#365e2a", "fibres", 2.2, "narrow", .32, 1.9),
    "platanus": ("#8c866a", "#d2b490", "#527c30", "patches", 2.4, "lobed", .28, 2.6),
}
WSEED = {tid: 500 + 13 * i for i, tid in enumerate(WOODS)}
BARK_CTR = {"scales": 56, "furrows": 60, "fibres": 50, "fern_bases": 62, "palm_bases": 58, "smooth": 38, "patches": 64}

LEAF_SHAPES = {
    "spiky": [["H..", ".B.", "..D"], ["..H", ".B.", "D.."], ["HB.", ".BD", "..D"], [".H.", "HBB", ".D."]],
    "fans": [["HHHB", "BBBD", ".VD.", ".V.."], [".HHB", "HBBD", ".VD.", "..V."], ["HHB", "BBD", ".V."]],
    "feathery": [["H.H.H.", "VVVVVV", ".D.D.D"], ["H.H.H", "VVVVV", "D.D.D"], [".H.H", "VVVV", "D.D."]],
    "fronds": [["H.H.H.H", "BVBVBVB", "D.D.D.D"], ["H.H.H", "BVBVB", "D.D.D"]],
    "palm": [["H...", ".H..", "..B.", "...D"], ["...H", "..H.", ".B..", "D..."], ["HHHH", "BBBB", "DDDD"],
             ["H.....", ".HB...", "...BD.", ".....D"]],
    "broad": [[".HH.", "HBBB", "BVBD", ".DD."], [".HB", "HBD", "BDD", "D.."], ["HHB.", "BBVD", ".DD."]],
    "narrow": [["HB", "BD", "BD", "D."], [".H", "HB", "BD", "D."], ["H.", "B.", "BD", ".D"]],
    "lobed": [[".H.H.", "HBBBB", ".BVBD", "..DD."], ["H.H", "BBB", "BVD", ".D."]],
}


def bark_tones(tid):
    style = WOODS[tid][3]
    s = WSEED[tid]
    r = T.rng(s)
    if style == "scales":  # araucaria: wide shingled scales, the plates of the motor's spruce
        t, _ = WD.bark_spruce(s)
        return t
    if style == "furrows":  # ginkgo: deep braided furrows
        t, _ = WD.bark_oak(s)
        return np.minimum(t, 5)
    if style == "smooth":  # magnolia: thin smooth bark, soft mottling, short lenticels
        t = WD.streak_base(s, 3, 2, 4, .25, .2, layers=((4, 8, .6), (8, 16, .4)))
        for (x, y) in poisson(s + 2, 8, 3.6):
            L = int(r.integers(2, 4))
            stamp(t, x, y, ['1' * L, '4' * L], {'1': 1, '4': 4})
        return T.cleanup(t, 1, keep=(t <= 1))
    if style == "patches":  # platanus: bark flaking off in patches, each with its own tone and a shadowed edge
        t, gap = WD.plates(s, 3, 3, 1.0, 1.0, jitter=.9, warp_amp=2.0, bodies=(2, 3, 4, 4))
        t[gap] = 1
        return T.cleanup(t, 1)
    if style in ("fern_bases", "palm_bases"):  # trunk clad in old leaf stubs set in a diamond lattice
        t = WD.streak_base(s, 2, 1, 3, .25, .2, layers=((8, 2, .6), (16, 4, .4)))
        palm = style == "palm_bases"
        step_y, step_x = (6, 8) if palm else (4, 8)
        shp = ["..55..", ".5443.", "544332", ".3221.", "..10.."] if palm else [".54.", "5401", ".21."]
        for row, cy in enumerate(range(0, N, step_y)):
            for cx in range(0 if row % 2 == 0 else step_x // 2, N, step_x):
                stamp(t, cx - len(shp[0]) // 2, cy, shp, {c: int(c) for c in "012345"})
        return t
    # fibres: long vertical strips peeling off, each strip lit on its left edge, a dark crevice on its right
    t = WD.streak_base(s, 3, 2, 4, .3, .15, layers=((8, 1, .6), (16, 2, .4)))
    for i, x0 in enumerate(range(1, N, 3)):
        xs = WD.wave(s + 10 + i, x0 + int(r.integers(-1, 2)), 0.5, 0.3)
        g = T.value_noise(s + 20 + i, 1, 4)[:, 0]
        WD.draw_line(t, xs, 0 if i % 2 else 1, side=(None, 4), present=g > .3)
    for (x, y) in poisson(s + 3, 3, 5):  # a loose strip curling off
        stamp(t, x, y, ['5', '5', '5', '1'], {'5': 5, '1': 1})
    return T.cleanup(t, 1)


def wood_fit(t, colour, ctr, n, dl=0.0, gamma=1.0, hue_shift=.02, sat_shift=.05, mask=None):
    h, sat, lum = hsv_of(colour)
    sample = np.asarray(t)[mask] if mask is not None else np.ravel(t)
    return fit(np.minimum(sample, n - 1), n, lum + dl, ctr, h, sat, hue_shift=hue_shift, sat_shift=sat_shift,
               gamma=gamma)


def bark_img(tid):
    t = bark_tones(tid)
    return img(t, wood_fit(t, WOODS[tid][0], BARK_CTR[WOODS[tid][3]], 6, sat_shift=.06))


def log_top_img(tid, stripped=False):
    """Off-centre rings with a drying check (the motor's rings), heartwood darker; the rim is the bark seen end-on,
    or a darker sapwood band once stripped."""
    bark_c, wood_c, _, _, spacing, _, _, _ = WOODS[tid]
    t, edge = WD.rings_tones(WSEED[tid] + 3, spacing, bark=True)
    inner = ~edge
    p = wood_fit(t, wood_c, 52, 5, dl=-8, mask=inner)
    out = np.asarray(img(t, p)).copy()
    if stripped:
        out[edge, :3] = np.array(p[1])
    else:
        b = np.asarray(bark_img(tid))[edge].astype(float)
        b[:, :3] = b[:, :3] * (1 - WD.RIM_MIX) + np.array(p[1]) * WD.RIM_MIX
        out[edge] = b.round().astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def stripped_img(tid):
    t = WD.stripped_tones(WSEED[tid] + 5)
    return img(t, wood_fit(t, WOODS[tid][1], 37, 4, dl=-6, hue_shift=.012, sat_shift=.04))


def planks_img(tid):
    t = WD.planks_tones(WSEED[tid] + 7)
    return img(t, wood_fit(t, WOODS[tid][1], 62, 5, dl=-22, gamma=.55))


def leaves_img(tid):
    """Leaves in simple clumps with one light (folhas.py, the engine thread's, approved 25/10)."""
    import folhas
    return folhas.leaf(tid)


def wood_textures(tid):
    out = {f"{tid}_log": bark_img(tid), f"{tid}_log_top": log_top_img(tid),
           f"stripped_{tid}_log": stripped_img(tid), f"stripped_{tid}_log_top": log_top_img(tid, True),
           f"{tid}_hewn_planks": planks_img(tid), f"{tid}_leaves": leaves_img(tid)}
    ROLE.update({f"{tid}_log": "oak_log", f"{tid}_log_top": "oak_log_top", f"stripped_{tid}_log": "stripped_oak_log",
                 f"stripped_{tid}_log_top": "stripped_oak_log_top", f"{tid}_hewn_planks": "oak_planks",
                 f"{tid}_leaves": "oak_leaves"})
    return out


# ------------------------------------------------------------------ materials of our own colour
from materials import Material  # noqa: E402


def own(colour, role, dc=0.0, n=5, **kw):
    """Material with the brightness, hue and saturation of `colour` and the contrast of vanilla `role` (+dc)."""
    h, sat, lum = hsv_of(colour)
    return Material(role, h, sat, dl=lum - target(role)[0], dc=dc, n=n, **kw)


def paint(t, m, n=None, extra=(), alpha=None):
    """Tones 0..n-1 get the ramp fitted to material m (only those pixels count); tones n.. take `extra`."""
    t = np.asarray(t)
    m = material(m)
    n = n or m.n
    base_px = t < n if alpha is None else (t < n) & np.asarray(alpha, bool)
    p = api.palette(np.where(t < n, t, 0), m, base_px, n=n)
    out = np.asarray(T.colorize(t, list(p) + [tuple(c) if not isinstance(c, str) else T.hexrgb(c) for c in extra])).copy()
    if alpha is not None:
        a = np.asarray(alpha, bool)
        out[..., 3] = np.where(a, 255, 0)
        out[~a, :3] = (np.array(p[0]) * .6).round()
    return Image.fromarray(out, "RGBA")


def extras(colours):
    return [T.hexrgb(c) for c in colours]


def strokes(t, seed, count, rmin, dirs, length, tone, shadow=None, rows=None):
    """Short straight strokes (straws, needles, stalks) placed on blue noise, each with a shadow pixel under it."""
    r = T.rng(seed)
    for (x, y) in poisson(seed + 1, count, rmin):
        if rows is not None and y not in rows:
            continue
        dx, dy = dirs[int(r.integers(len(dirs)))]
        tn = tone(r) if callable(tone) else tone
        for k in range(int(r.integers(*length))):
            yy, xx = (y + k * dy) % N, (x + k * dx) % N
            t[yy, xx] = tn
            if shadow is not None and t[(yy + 1) % N, xx] != tn:
                t[(yy + 1) % N, xx] = shadow
    return t


# ------------------------------------------------------------------ thatch, roofs, mats, wicker
STRAW, REED, FERN_DRY, CYCAD_DRY = "#a08848", "#8a7e45", "#715628", "#55632e"


def bundles(seed, ties=False):
    """Two courses of bundles (8 px, like the bands of the hay bale): a deep shadow under the lip of the course
    above, upright stalks in their own tones, ragged sun-bleached tips, a stray stalk or two across."""
    r = T.rng(seed)
    t = np.zeros((N, N), int)
    for c in range(2):
        y0 = c * 8
        col = T.quantize(T.fbm(seed + c, [(16, 1, .7), (8, 1, .3)])[0], [.25, .45, .3]) + 1
        col = np.roll(col, int(r.integers(N)))
        for x in range(N):
            tip = int(r.choice([5, 6, 6, 7, 7]))
            for k in range(8):
                v = 0 if k == 0 else 1 if k == 1 else (4 if (x + k) % 2 else 3) if k >= tip else col[x]
                if ties and k in (3, 4) and x % 4 == 1:
                    v = 1
                t[y0 + k, x] = v
        for (x, y) in poisson(seed + 10 + c, 4, 3.5):  # dark gaps between stalks
            for k in range(2, 2 + int(r.integers(2, 4))):
                t[y0 + k, x] = max(0, t[y0 + k, x] - 1) if k < 6 else t[y0 + k, x]
        for (x, y) in poisson(seed + 20 + c, 2, 6):  # stray stalk lying across
            yy = y0 + 3 + y % 3
            stamp(t, x, yy, ['4..', '14.', '.14', '..1'][:2] if r.random() < .5 else ['44.', '.14'], {'4': 4, '1': 1})
    return t


def fronds(seed):
    """Two courses of dried fronds overlapping like shingles: a midrib, leaflets slanting down both sides, each
    leaflet lit on its upper edge, the lip of the course above throwing a shadow."""
    r = T.rng(seed)
    t = np.ones((N, N), int)
    for c in range(2):
        y0 = c * 8
        for f in range(2):
            mx = (f * 8 + c * 4 + 3 + int(r.integers(-1, 2))) % N
            for k in range(1, 8):
                y = y0 + k
                t[y, mx] = 4
                for side in (-1, 1):
                    for d in range(1, 4):
                        t[y, (mx + side * d) % N] = (3, 2, 1)[(k + d) % 3]
        t[y0, :] = 0
        for (x, y) in poisson(seed + 5 + c, 3, 4):  # a broken leaflet shows the darker course under it
            t[y0 + 1 + y % 6, x] = 0
    return t


def roof_top(seed, dirs):
    t = base(seed, 2, 1, 3, .2, .18, layers=((2, 8, .5), (4, 16, .5)))
    return strokes(t, seed + 3, 22, 2.4, dirs, (2, 5), lambda r: int(r.choice([3, 4, 4])), shadow=1)


def thatch_family():
    side_role, top_role = "hay_block_side", "hay_block_top"
    out = {
        "thatch": paint(bundles(701), own(STRAW, side_role, dc=-26)),
        "thatch_top": paint(roof_top(702, [(1, 0), (0, 1), (1, 1), (1, -1)]), own(STRAW, top_role)),
        "reed_thatch": paint(bundles(703, ties=True), own(REED, side_role, dc=-30)),
        "reed_thatch_top": paint(roof_top(704, [(1, 0), (1, 0), (1, 1)]), own(REED, top_role)),
        "fern_thatch": paint(fronds(705), own(FERN_DRY, side_role, dc=-30)),
        "fern_thatch_top": paint(roof_top(706, [(1, 0), (1, 1), (1, -1)]), own(FERN_DRY, top_role)),
        "cycad_thatch": paint(fronds(707), own(CYCAD_DRY, side_role, dc=-34)),
        "cycad_thatch_top": paint(roof_top(708, [(1, 0), (1, 1), (1, -1)]), own(CYCAD_DRY, top_role)),
    }
    # straw mat: 4 px strips over and under, three straws to a strip, the end that dives under in shade
    ys, xs = np.mgrid[0:N, 0:N]
    horiz = ((xs // 4) + (ys // 4)) % 2 == 0
    k = np.where(horiz, ys % 4, xs % 4)
    along = np.where(horiz, xs % 4, ys % 4)
    t = np.array([4, 3, 2, 1])[k] - (along == 3)
    vary = T.rng(709).choice([0, 0, -1], (4, 4))
    t = np.clip(t + vary[ys // 4, xs // 4], 0, 4)
    for (x, y) in poisson(710, 5, 4):
        t[y, x] = 0
    out["straw_mat"] = paint(t, own(STRAW, top_role, dc=6))
    # wicker: 2 px canes in a basket weave, each cane its own shade
    over_h = ((xs // 2) + (ys // 2)) % 2 == 0
    t = np.where(over_h, np.where(ys % 2 == 0, 4, 2), np.where(xs % 2 == 0, 3, 1))
    cane = T.rng(711).choice([0, 0, 0, -1], (8, 8))
    t = np.clip(t + np.where(over_h, cane[ys // 2, 0 * xs], cane[0 * ys, xs // 2]), 0, 4)
    out["wicker_block"] = paint(t, material("wicker").like(dc=-20))
    # reed mat: whole reeds side by side (lit and shaded half), a node every few pixels, two fibre ties
    r = T.rng(712)
    nodes = r.integers(0, 6, 8)
    shade = r.choice([0, 0, -1], 8)
    t = np.where(xs % 2 == 0, 3, 1) + shade[xs // 2]
    t = np.where(((ys + nodes[xs // 2]) % 6 == 0) & (xs % 2 == 0), 4, t)
    t = np.where((ys + nodes[xs // 2]) % 6 == 1, t - 1, t)
    t = np.clip(t, 0, 4)
    for y in (3, 12):
        t[y] = np.where(xs[0] % 2, 5, 6)
        t[y + 1] = np.where(xs[0] % 2, 0, t[y + 1])
    out["reed_mat"] = paint(t, own(REED, side_role, dc=-30), extra=extras(["#4a3a22", "#6e5a3a"]))
    ROLE.update({k: (side_role if k.endswith(("thatch",)) or k == "reed_mat" or k == "wicker_block" else top_role)
                 for k in out})
    return out


# ------------------------------------------------------------------ daub, plaster, earth
DAUB = "#957b5c"
STICKS = ["#3a2814", "#54391d", "#6e4d2a", "#87623a"]
TIMBER = ["#2e2014", "#46321f", "#5e452c", "#76593a"]
EARTH = "#73573d"


def daub_tones(seed, sticks=True):
    """Hand-pressed clay: lumps lit on top with a shadow under, straw in the clay (tone 5), a drying crack and,
    where the clay fell away, the woven sticks underneath (tones 6..9)."""
    t = base(seed, 2, 1, 3, .2, .2, layers=((4, 4, .6), (8, 8, .4)))
    for (x, y) in poisson(seed + 1, 12, 3.0):
        stamp(t, x, y, ['L', 'D'] if (x + y) % 3 else ['LL', 'DD'], {'L': 3, 'D': 1})
    strokes(t, seed + 2, 8, 3.5, [(1, 0), (1, 1), (1, -1)], (2, 4), 5)
    r = T.rng(seed + 3)
    x, y = int(r.integers(N)), int(r.integers(N))
    for _ in range(8):
        if t[y % N, x % N] < 5:
            t[y % N, x % N] = 0
            if t[(y + 1) % N, x % N] < 5:
                t[(y + 1) % N, x % N] = 4
        x += int(r.choice([1, 1, 0]))
        y += int(r.choice([1, 0, 0, -1]))
    if sticks:
        x0, y0 = int(r.integers(N)), int(r.integers(N))
        for j in range(5):
            for i in range(6):
                if i in (0, 5) and j in (0, 4):
                    continue
                t[(y0 + j) % N, (x0 + i) % N] = (8 if j % 2 == 0 else 6) if i != 2 else (9 if j % 2 else 7)
        for i in range(6):
            if t[(y0 - 1) % N, (x0 + i) % N] < 5:
                t[(y0 - 1) % N, (x0 + i) % N] = 4
            if t[(y0 + 5) % N, (x0 + i) % N] < 5:
                t[(y0 + 5) % N, (x0 + i) % N] = 0
    return t


DAUB_MAT = own(DAUB, "packed_mud", dc=22)
DAUB_EXTRA = ["#c8b27a"] + STICKS


def beams(kind):
    b = np.zeros((N, N), bool)
    b[0, :] = b[-1, :] = b[:, 0] = b[:, -1] = True
    if kind == "frame":
        b[1, :] = b[-2, :] = b[:, 1] = b[:, -2] = True
    if kind == "cross":
        for i in range(N):
            for (x, y) in ((i, i), ((i + 1) % N, i), (15 - i, i), ((14 - i) % N, i)):
                b[y, x] = True
    return b


def wattle(kind):
    t = daub_tones(720 + len(kind), sticks=False)
    b = beams(kind)
    grain = T.quantize(T.fbm(730 + len(kind), [(8, 2, .6), (16, 4, .4)]), [.3, .4, .3])
    lit = (~T.roll(b, -1, 0) | ~T.roll(b, 0, -1)) & b
    dark = (~T.roll(b, 1, 0) | ~T.roll(b, 0, 1)) & b
    tb = np.clip(1 + grain + (lit & ~dark) - (dark & ~lit), 0, 3)
    shadow = ~b & (T.roll(b, -1, 0) | T.roll(b, 0, -1)) & (t < 5)
    t = np.where(shadow, np.maximum(t - 2, 0), t)
    t = np.where(b, 10 + tb, t)
    return paint(t, DAUB_MAT, extra=DAUB_EXTRA + extras(TIMBER))


PLASTERS = {"clay_plaster": "#a38868", "red_ochre_plaster": "#8e3f28", "yellow_ochre_plaster": "#b88b3a",
            "charcoal_plaster": "#33302d", "chalk_whitewash": "#dcd8ce"}


def plaster_tones(seed):
    """Hand-smoothed plaster: one main tone in broad soft patches, trowel strokes (a lit ridge with a soft shade
    under it) where a stroke ended, one hairline crack with a lit lip."""
    t = base(seed, 2, 1, 3, .16, .16, layers=((2, 4, .6), (4, 8, .4)))
    r = T.rng(seed)
    for (x, y) in poisson(seed + 1, 4, 5.5):
        L = int(r.integers(3, 6))
        stamp(t, x, y, ['3' * L, '.' + '1' * (L - 2)], {'3': 3, '1': 1})
    x, y = int(r.integers(N)), int(r.integers(N))
    for _ in range(6):
        t[y % N, x % N] = 0
        t[(y + 1) % N, x % N] = 4
        x += 1
        y += int(r.choice([1, 0, 0, -1]))
    return t


def earth_family():
    out = {"wattle_and_daub": paint(daub_tones(740), DAUB_MAT, extra=DAUB_EXTRA)}
    for kind, name in (("cross", "cross_braced_wattle"), ("frame", "timber_framed_wattle")):
        out[name] = wattle(kind)
    # whitewash: chalk over daub, worn through in patches
    t = daub_tones(741, sticks=False)
    worn = T.fbm(742, [(4, 4, .6), (8, 8, .4)]) < .15
    t = np.where(worn & (t < 5), 10 + np.minimum(t, 4), np.where(t < 5, np.minimum(t + 1, 4), t))
    dp = api.palette(np.arange(5)[None], DAUB_MAT, n=5)
    out["whitewashed_wattle"] = paint(t, own(PLASTERS["chalk_whitewash"], "packed_mud", dc=10),
                                      extra=DAUB_EXTRA + list(dp))
    for i, (pid, c) in enumerate(PLASTERS.items()):
        if pid == "chalk_whitewash":
            continue
        out[pid] = paint(plaster_tones(750 + i), own(c, "packed_mud", dc=6))
    # rammed earth: horizontal lifts of tamped soil, each its own shade, a dark seam with the lit top of the next
    t = base(760, 2, 1, 3, .18, .18, layers=((4, 2, .6), (8, 4, .4)))
    lifts = [0, 4, 7, 12, 16]
    for i in range(4):
        y0, y1 = lifts[i], lifts[i + 1]
        t[y0:y1] = np.clip(t[y0:y1] + (0, 1, 0, 1)[i] - 1 + 1, 0, 4)
        t[y1 - 1, :] = np.where(np.arange(N) % 7, 0, 1)
        t[y0, :] = np.minimum(t[y0, :] + 1, 4)
    for (x, y) in poisson(761, 6, 4):
        stamp(t, x, y, ['ab', 'c.'], {'a': 6, 'b': 5, 'c': 0})
    out["rammed_earth"] = paint(t, own(EARTH, "packed_mud", dc=30), extra=extras(["#6a665c", "#8e897e"]))
    # beaten earth floor: soft clumps worn smooth, straw bits, the odd pebble
    t = base(762, 2, 1, 3, .18, .16, layers=((4, 4, .6), (8, 8, .4)))
    for (x, y) in poisson(763, 10, 3.2):
        stamp(t, x, y, ['L', 'D'], {'L': 3, 'D': 1})
    strokes(t, 764, 7, 4, [(1, 0), (0, 1)], (2, 3), lambda r: int(r.choice([5, 6])))
    for (x, y) in poisson(765, 3, 6):
        stamp(t, x, y, ['c', 'd'], {'c': 7, 'd': 0})
    out["packed_earth_floor"] = paint(t, own("#806048", "packed_mud", dc=18),
                                      extra=extras(["#b09a60", "#8e7846", "#8a857a"]))
    ROLE.update({k: "packed_mud" for k in out})
    return out


# ------------------------------------------------------------------ hides
def hide_tones(pattern, seed):
    """Tileable skin (tones 0..4). Scales and osteoderms are raised cells (lit top, shaded under, dark creases);
    stripes and spots are markings over mottled skin; feathers overlap like shingles with a light quill; fuzz is
    short soft strands; plain is scraped hide with a vein and scrape marks."""
    r = T.rng(seed)
    if pattern in ("scales", "big_scales", "fine_scales", "osteoderms"):
        rmin = {"scales": 3.4, "big_scales": 4.6, "fine_scales": 2.7, "osteoderms": 5.2}[pattern]
        pts = [(x + .5, y + .5) for (x, y) in poisson(seed + 1, 40, rmin)]
        idx, _, _ = T.voronoi(pts, sx=.95, warp=T.fbm(seed + 2, [(8, 8, 1)]), warp_amp=.8)
        gap, hi, lo = bevel(idx, round_corners=pattern != "fine_scales")
        body = r.choice([2, 2, 3], len(pts))[idx]
        t = np.where(hi, np.minimum(body + 1, 4), np.where(lo, body - 1, body))
        t[gap] = 0
        if pattern == "osteoderms":
            for k, (px, py) in enumerate(pts):
                x, y = int(px) % N, int(py) % N
                stamp(t, x - 1, y - 1, ['.4.', '434', '.2.'], {'4': 4, '3': 3, '2': 1})
        return t
    if pattern == "feathers":
        t = np.full((N, N), 2)
        FE = [".344.", "33443", "23332", "22322", ".222.", "..1.."]
        for row in range(4):
            for col in range(3):
                x = col * 6 + (3 if row % 2 else 0) + int(r.integers(-1, 2))
                y = row * 4 - 1
                stamp(t, x, y, FE, {'1': 0, '2': 1 + int(r.integers(0, 2)), '3': 2 + int(r.integers(0, 2)), '4': 3})
                t[(y + 1) % N:(y + 4) % N or N, (x + 2) % N] = 4  # quill
        return T.cleanup(t, 1, keep=(t == 4))
    t = base(seed, 2, 1, 3, .2, .2, layers=((4, 4, .6), (8, 8, .4)))
    if pattern == "stripes":
        ys, xs = np.mgrid[0:N, 0:N]
        k = (xs + np.round(2 * np.sin(ys / N * 2 * np.pi)).astype(int)) % 8
        t = np.where(k == 0, 0, np.where(k == 1, 1, np.where(k == 2, np.minimum(t + 1, 4), t)))
    elif pattern == "spots":
        for (x, y) in poisson(seed + 1, 7, 5.0):
            stamp(t, x, y, ['.00.', '0110', '.00.'] if r.random() < .5 else ['00', '00'], {'0': 0, '1': 1})
    elif pattern == "fuzz":
        strokes(t, seed + 1, 30, 2.0, [(1, 1)], (2, 3), lambda r: int(r.choice([3, 3, 4])), shadow=1)
    else:  # plain scraped hide
        x = int(r.integers(N))
        for y in range(N):
            t[y, x % N] = max(1, t[y, x % N] - 1)
            x += int(r.choice([-1, 0, 0, 1]))
        for (x, y) in poisson(seed + 2, 4, 6):
            stamp(t, x, y, ['33.', '.33'] if r.random() < .5 else ['3', '1'], {'3': 3, '1': 1})
        for (x, y) in poisson(seed + 3, 10, 3):
            t[y, x] = 1
    return t


def hide(pattern, colour, seed=1, muted=0.35):
    """A hide in the species colour pulled `muted` of the way to grey (tanned skin is duller than the animal)."""
    h, sat, lum = hsv_of(colour)
    role = "brown_wool"
    dc = {"plain": 10, "stripes": 30, "spots": 30, "fuzz": 14, "feathers": 26}.get(pattern, 30)
    m = Material(role, h, sat * (1 - muted), dl=lum - target(role)[0], dc=dc, n=5)
    return paint(hide_tones(pattern, seed), m)


GENERIC_HIDES = {"rawhide": ("#bba07c", "plain"), "tanned_hide": ("#644128", "plain")}


# ------------------------------------------------------------------ amber
AMBER = "#b0601a"
AMBER_MAT = own(AMBER, "honey_block_side", dc=8, n=6, hue_shift=.03, sat_shift=-.05)


def amber_tones(kind, seed=800):
    r = T.rng(seed)
    if kind == "mosaic":
        pts = [(x + .5, y + .5) for (x, y) in poisson(seed + 1, 12, 4.0)]
        idx, _, _ = T.voronoi(pts, warp=T.fbm(seed + 2, [(8, 8, 1)]), warp_amp=1.0)
        gap, hi, lo = bevel(idx, round_corners=False)
        body = r.choice([2, 3, 3, 4], len(pts))[idx]
        t = np.where(hi, np.minimum(body + 1, 5), np.where(lo, body - 1, body))
        t[gap] = 0
        for (px, py) in pts[::2]:  # a glint on every other piece
            t[int(py) % N, int(px) % N] = 5
        return t
    if kind == "polished":
        t = base(seed, 3, 2, 4, .2, .15, layers=((4, 4, .6), (8, 8, .4)))
        ys, xs = np.mgrid[0:N, 0:N]
        k = (xs + ys) % 16
        t = np.where(k == 3, 5, np.where(k == 4, 4, np.where(k == 5, np.maximum(t - 1, 1), t)))
        return t
    t = base(seed, 3, 2, 4, .22, .16, layers=((2, 4, .5), (4, 8, .5)))
    for (x, y) in poisson(seed + 3, 4, 5.0):  # cloudy darker swirls
        stamp(t, x, y, ['11.', '.11'], {'1': 1})
    for (x, y) in poisson(seed + 4, 6, 4.0):  # bubbles: bright top-left, dark lower edge
        stamp(t, x, y, ['5.', '.1'], {'5': 5, '1': 1})
    return t


def amber_family(inclusions):
    import chao
    out = {"amber_block": chao.amber_block(),
           "polished_amber": paint(amber_tones("polished"), AMBER_MAT),
           "amber_mosaic": paint(amber_tones("mosaic"), AMBER_MAT.like(dc=24))}
    t = base(810, 2, 1, 3, .2, .2, layers=((4, 2, .6), (8, 4, .4)))
    r = T.rng(811)
    for (x, y) in poisson(812, 4, 4.5):  # drips: lit left, shaded right, fat at the end
        L = int(r.integers(4, 8))
        stamp(t, x, y, ['42'] * L + ['31', '0.'], {'4': 4, '2': 2, '3': 3, '1': 1, '0': 0})
    out["resin_block"] = paint(t, own("#c49c40", "honeycomb_block", dc=-30))
    for kind, rows in inclusions.items():
        t = amber_tones("polished")
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch in "dl":
                    t[y, x] = 6 if ch == "d" else 7
        out[f"amber_with_{kind}"] = paint(t, AMBER_MAT, extra=extras(["#2e1a0a", "#6a4a1a" if kind != "leaf" else "#4a5220"]))
    ROLE.update({k: "honey_block_side" for k in out})
    return out


# ------------------------------------------------------------------ soils
def soil_family():
    """Clods and calm colours since 25/10 (chao.py, the style Rodrigo approved)."""
    import chao
    out = chao.soil_family()
    ROLE.update({k: "dirt" for k in out})
    ROLE.update({"cracked_mud": "mud_bricks", "volcanic_ash": "sand", "peat": "mud", "salt_crust": "calcite"})
    return out


FAMILIES = ("rocks", "woods", "thatch", "earth", "soils")


def textures(families=FAMILIES, inclusions=None):
    """Every surface texture drawn here, by name. Hides (species colours) and amber with inclusions (shapes kept in
    spritegen/blocks.py) are called from there with what they need."""
    out = {}
    if "rocks" in families:
        for rid in ROCKS:
            out.update(rock_textures(rid))
    if "woods" in families:
        for tid in WOODS:
            out.update(wood_textures(tid))
    if "thatch" in families:
        out.update(thatch_family())
    if "earth" in families:
        out.update(earth_family())
    if "soils" in families:
        out.update(soil_family())
    if inclusions is not None:
        out.update(amber_family(inclusions))
    return out


def drift(out):
    """Textures whose contrast is more than 40 away from the vanilla block of their role (see ROLE): the deliberate
    ones are motifs (beams on daub, moss on pale stone, flowers, inclusions); anything else is a slip."""
    from targets import measure
    bad = {}
    for name, im in out.items():
        role = ROLE.get(name)
        if not role:
            continue
        m = measure(im)
        lum, ctr = target(role)[:2]
        if abs(m["ctr"] - ctr) > 40:
            bad[name] = f"contrast {m['ctr']:.0f} vs {role} {ctr:.0f}"
    return bad
