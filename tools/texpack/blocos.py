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


# texture name -> the vanilla block whose contrast it is held to (see drift())
ROLE = {}  # texture name -> vanilla role (filled by each family)


# ------------------------------------------------------------------ rocks
# drawn in chao.py (fine grain, approved 25/10): base, stacked, flagstone, pebbles, mossy stacked per rock
ROCKS = ("limestone", "shale", "chalk", "flint", "laterite", "quartzite", "gneiss", "conglomerate")




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

# drawn in madeira.py (bark, ends, stripped, planks) and folhas.py (leaves), calm style approved 25/10
WOODS = ("araucaria", "ginkgo", "metasequoia", "taxodium", "tree_fern", "sabal", "magnolia", "podocarpus", "platanus")


def leaves_img(tid):
    """Leaves in simple clumps with one light (folhas.py, the engine thread's, approved 25/10)."""
    import folhas
    return folhas.leaf(tid)


def wood_textures(tid):
    """Bark, ends, stripped and planks from madeira.py (calm style, 25/10); leaves from folhas.py."""
    import madeira
    out = madeira.textures(tid)
    out[f"{tid}_leaves"] = leaves_img(tid)
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
STRAW, REED = "#a08848", "#8a7e45"


def thatch_family():
    """Thatch roofs from paredes.py (calm style, 25/10); the woven mats are drawn here and only calmed there."""
    import paredes
    side_role, top_role = "hay_block_side", "hay_block_top"
    out = {}
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
    out = {k: paredes.recolour(im, .40) for k, im in out.items()}
    out.update(paredes.thatch())
    ROLE.update({k: (side_role if k.endswith(("thatch",)) or k == "reed_mat" or k == "wicker_block" else top_role)
                 for k in out})
    return out


# ------------------------------------------------------------------ daub, plaster, earth




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




def earth_family():
    """Plasters, daub, timber frames, whitewash and rammed earth from paredes.py (calm style, 25/10)."""
    import paredes
    out = paredes.earth()
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
