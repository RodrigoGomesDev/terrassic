"""Ground blocks of the mod in the style Rodrigo approved on 25/10 (16:31Z, the "calm" column of the scene):
nothing that reads from afar. Rocks are a FINE GRAIN (rank-quantised, high-passed noise of short horizontal grains,
6 tones, then pixels swapped until the far-away structure `macro` is down to vanilla's), with the real material only
in small accents; soils are CLODS (torroes.py: 2-3 px lumps lit from the top-left, like vanilla dirt); colours calm
(mean HSV saturation <= .50 on soils, .42 on laterite). Masonry variants reuse the rock's own grain as the fill of each
stone, with joints one step under the darkest tone (never near-black).
Targets measured on vanilla 1.20.1 (progressao/estudo/metricas.py): granular blocks macro <= 4, jointed <= 7.5,
glassy (honey, calcite) 8-10."""
import colorsys

import numpy as np
from PIL import Image

import torroes as TR

N = 16


# ------------------------------------------------------------------ grain
def blur(a, k=1):
    out = a.copy()
    for dy in range(-k, k + 1):
        for dx in range(-k, k + 1):
            if dx or dy:
                out = out + np.roll(np.roll(a, dy, 0), dx, 1)
    return out / (2 * k + 1) ** 2


def field(seed, clump=.45, hp=1.0):
    """Short horizontal grains of 2-3 px (like vanilla dirt) with the scale seen from afar taken out (blue-ish)."""
    r = np.random.default_rng(seed)
    g = r.normal(size=(N, N))
    hz = (np.roll(g, 1, 1) + g + np.roll(g, -1, 1)) / 3
    g = (1 - clump) * g + clump * hz * 1.4
    lo = sum(np.roll(np.roll(g, dy, 0), dx, 1) for dy in range(-2, 2) for dx in range(-2, 2)) / 16
    g = g - hp * lo
    return g / g.std()


def levels(f, weights):
    """Rank-quantise into len(weights) tones with those area shares (dark..light)."""
    order = np.argsort(f, axis=None)
    idx = np.zeros(N * N, int)
    cuts = np.cumsum(weights) / sum(weights) * N * N
    for k, o in enumerate(order):
        idx[o] = int(np.searchsorted(cuts, k, side="right"))
    return idx.reshape(N, N)


def ramp(rgb, n, ctr, hue_dark=.02, sat_dark=1.15, sat_light=.8):
    """n tones around rgb spanning about ctr of luma; lighter = warmer, darker = redder and a bit richer."""
    h, l, s = colorsys.rgb_to_hls(*(np.array(rgb) / 255))
    out = []
    for t in np.linspace(-.5, .5, n):
        L = min(.95, max(.03, l + t * ctr / 255 * 1.05))
        H = (h + t * 2 * hue_dark) % 1
        S = min(1, s * (sat_dark if t < 0 else 1) * (1 + (sat_light - 1) * max(0, t) * 2))
        out.append(tuple(int(round(c * 255)) for c in colorsys.hls_to_rgb(H, L, S)))
    return out


def paint(idx, pal):
    a = np.zeros((N, N, 4), np.uint8)
    for k, c in enumerate(pal):
        a[idx == k] = (*c, 255)
    return Image.fromarray(a, "RGBA")


def lum(pal):
    return np.array([.299 * c[0] + .587 * c[1] + .114 * c[2] for c in pal])


def macro_of(L):
    bl = sum(np.roll(np.roll(L, -j, 0), -i, 1) for i in range(-1, 3) for j in range(-1, 3)) / 16
    return bl.std()


def calm(idx, pal, target, seed=0, tries=6000, mask=None):
    """Swap pairs of pixels (the histogram stays) while the far-away structure (macro) is above target."""
    r = np.random.default_rng(seed)
    lu = lum(pal)
    idx = idx.copy()
    free = np.argwhere(np.ones((N, N), bool) if mask is None else ~mask)
    cur = macro_of(lu[idx])
    for _ in range(tries):
        if cur <= target:
            break
        a, b = (tuple(p) for p in free[r.integers(len(free), size=2)])
        if idx[a] == idx[b]:
            continue
        idx[a], idx[b] = idx[b], idx[a]
        m = macro_of(lu[idx])
        if m < cur:
            cur = m
        else:
            idx[a], idx[b] = idx[b], idx[a]
    return idx


def calm_pal(pal, sat_cap, hue_to=None, pull=.35):
    """Mean HSV saturation down to sat_cap; hue pulled a little toward hue_to (earthy orange)."""
    hs = [colorsys.rgb_to_hsv(*(np.array(c) / 255)) for c in pal]
    m = np.mean([s for _, s, _ in hs])
    k = min(1, sat_cap / m) if m > 0 else 1
    out = []
    for h, s, v in hs:
        if hue_to is not None and s > .15:
            h = (h + pull * ((((hue_to / 360) - h + .5) % 1) - .5)) % 1
        out.append(tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(h, s * k, v)))
    return out


def stamp_accents(idx, pal, mask, r, accents):
    """accents: (colour, count, cells) dropped at random, kept out of the swaps."""
    for col, count, shape in accents:
        k = len(pal)
        pal = pal + [col]
        for _ in range(count):
            y, x = r.integers(N, size=2)
            for dy, dx in shape:
                idx[(y + dy) % N, (x + dx) % N] = k
                mask[(y + dy) % N, (x + dx) % N] = True
    return idx, pal


# ------------------------------------------------------------------ rocks
# rgb, contrast, laminae (bedded rocks), grain clumping, macro target, accents; sat/hue_to = calm colour
ROCKS = {
    "shale": dict(rgb=(76, 78, 82), ctr=56, layer=.8, clump=.6, macro=4.0, seed=11, partings=(4, (112, 114, 118))),
    "limestone": dict(rgb=(190, 184, 172), ctr=40, layer=.6, clump=.6, macro=3.6, seed=9,
                      acc=[((150, 144, 132), 3, [(0, 0), (0, 1)]), ((214, 210, 200), 3, [(0, 0), (0, 1), (0, 2)])]),
    "laterite": dict(rgb=(158, 94, 70), ctr=46, layer=.15, clump=.9, macro=4.5, seed=6, hue=.015, w=(1, 2, 4, 4, 2, 1),
                     sat=.42, hue_to=19,
                     acc=[((96, 46, 34), 6, [(0, 0)]), ((128, 68, 50), 4, [(0, 0), (0, 1)]), ((196, 146, 96), 3, [(0, 0)])]),
    "chalk": dict(rgb=(222, 220, 210), ctr=30, layer=.2, clump=.7, macro=3.2,
                  acc=[((150, 150, 150), 3, [(0, 0)]), ((200, 198, 186), 4, [(0, 0), (0, 1)])]),
    "quartzite": dict(rgb=(206, 190, 182), ctr=40, layer=.3, clump=.4, macro=3.5, hue=.01,
                      acc=[((236, 230, 224), 6, [(0, 0)]), ((170, 150, 142), 3, [(0, 0)])]),
    "gneiss": dict(rgb=(128, 124, 120), ctr=48, layer=1.2, clump=.6, macro=4.2, wob=1.6,
                   acc=[((160, 154, 146), 4, [(0, 0), (0, 1), (0, 2)]), ((92, 90, 92), 3, [(0, 0), (0, 1)])]),
    "conglomerate": dict(rgb=(150, 132, 108), ctr=50, layer=.1, clump=.5, macro=4.5, clasts=True, sat=.30),
    "flint": dict(rgb=(66, 66, 72), ctr=36, layer=.1, clump=.8, macro=5.0, smooth=True,
                  acc=[((112, 112, 114), 3, [(0, 0), (0, 1)])]),
}
CLASTS = [(178, 170, 160), (120, 112, 104), (168, 120, 96), (196, 188, 170)]


def rock_base(rid, seed=None):
    """(tone index map, palette) of the raw rock: the first 6 palette entries are its tone ramp, dark first."""
    p = ROCKS[rid]
    seed = p.get("seed", 11) if seed is None else seed
    r = np.random.default_rng(seed)
    off = np.zeros(N, int)
    if p.get("smooth"):  # glassy: soft clouds, little grain
        c = r.normal(size=(N, N))
        for _ in range(2):
            c = blur(c, 1)
        f = c / c.std() + .6 * field(seed, .7)
    else:
        f = field(seed, p["clump"])
        if p.get("layer"):  # thin laminae, gently waving, never a thick band
            rows = r.normal(size=N)
            rows = rows - .25 * (np.roll(rows, 1) + np.roll(rows, -1))
            off = np.round(p.get("wob", 1.0) * np.sin(2 * np.pi * (np.arange(N) / N + r.uniform()))).astype(int)
            lam = np.array([[rows[(y + off[x]) % N] for x in range(N)] for y in range(N)])
            f = f + p["layer"] * lam / lam.std()
    w = list(p.get("w", (1, 2, 3, 3, 2, 1)))
    idx = levels(f, w)
    pal = ramp(p["rgb"], len(w), p["ctr"], hue_dark=p.get("hue", .01))
    mask = np.zeros((N, N), bool)
    if p.get("clasts"):  # conglomerate: small rounded pebbles of other rocks
        for i in range(9):
            y, x = r.integers(N, size=2)
            col = CLASTS[i % len(CLASTS)]
            k = len(pal)
            pal = pal + [col, tuple(int(c * .82) for c in col)]
            for dy in range(2):
                for dx in range(3 if i % 2 else 2):
                    idx[(y + dy) % N, (x + dx) % N] = k + (1 if dy == 1 and dx > 0 else 0)
                    mask[(y + dy) % N, (x + dx) % N] = True
    idx, pal = stamp_accents(idx, pal, mask, r, p.get("acc", []))
    if p.get("partings"):  # short pale partings along the bedding
        n, col = p["partings"]
        k = len(pal)
        pal = pal + [col]
        for _ in range(n):
            y, x = r.integers(N, size=2)
            for i in range(int(r.integers(2, 5))):
                yy, xx = (y + off[(x + i) % N]) % N, (x + i) % N
                idx[yy, xx] = k
                mask[yy, xx] = True
    idx = calm(idx, pal, p["macro"], mask=mask, seed=seed)
    if "sat" in p:
        pal = calm_pal(pal, p["sat"], p.get("hue_to"))
    return idx, pal


def shade(pal, idx, k):
    """Move every pixel k steps along the luma order of the palette (a stone a little lighter or darker)."""
    order = np.argsort(lum(pal))
    rank = np.empty(len(pal), int)
    rank[order] = np.arange(len(pal))
    return order[np.clip(rank[idx] + k, 0, len(pal) - 1)]


def joint(pal):
    """A little under the darkest ramp tone (accents ignored), never near-black."""
    return tuple(int(v) for v in np.array(pal[0], float) * .94)


COURSES = [(4, 4, 3, 5), (5, 3, 4, 4), (3, 5, 4, 4)]


def stacked(rid, seed=21):
    """Dry-laid courses of uneven height, long stones, lit top edges; returns (idx, pal, bed rows)."""
    idx, pal = rock_base(rid, seed)
    r = np.random.default_rng(seed)
    J = len(pal)
    pal = pal + [joint(pal)]
    out = idx.copy()
    beds = []
    y0 = 0
    for h in COURSES[seed % len(COURSES)]:
        x = int(r.integers(0, N))
        start = x
        while x < start + N:
            L = int(r.integers(5, 11))
            k = int(r.integers(-1, 2))
            for xx in range(x, min(x + L, start + N)):
                for yy in range(y0, y0 + h - 1):
                    out[yy % N, xx % N] = shade(pal[:J], idx[yy % N, xx % N], k)
                if r.random() < .5:
                    out[y0 % N, xx % N] = shade(pal[:J], out[y0 % N, xx % N], 1)
            if x + L < start + N:
                for yy in range(y0, y0 + h - 1):
                    out[yy % N, (x + L - 1) % N] = J
            x += L
        beds.append((y0 + h - 1) % N)
        out[(y0 + h - 1) % N, :] = J
        y0 += h
    return out, pal, beds


def voronoi(r, n):
    """Cell labels on the torus and the distance to the nearest other cell (edge < 1 = joint)."""
    pts = r.uniform(0, N, size=(n, 2))
    yy, xx = np.mgrid[0:N, 0:N] + .5
    d = np.full((N, N), 1e9)
    d2 = np.full((N, N), 1e9)
    lab = np.zeros((N, N), int)
    for i, (py, px) in enumerate(pts):
        for oy in (-N, 0, N):
            for ox in (-N, 0, N):
                dd = (yy - py - oy) ** 2 + (xx - px - ox) ** 2
                upd = dd < d
                d2 = np.where(upd, d, np.minimum(d2, dd))
                lab = np.where(upd, i, lab)
                d = np.where(upd, dd, d)
    return lab, np.sqrt(d2) - np.sqrt(d)


def flagstone(rid, seed=31):
    idx, pal = rock_base(rid, seed)
    r = np.random.default_rng(seed)
    lab, edge = voronoi(r, 10)
    J = len(pal)
    pal = pal + [joint(pal)]
    out = idx.copy()
    for c in range(lab.max() + 1):
        m = lab == c
        out[m] = shade(pal[:J], idx[m], int(r.integers(-1, 2)))
    out[edge < 1.0] = J
    return out, pal


def pebbles(rid, seed=41):
    idx, pal = rock_base(rid, seed)
    r = np.random.default_rng(seed)
    lab, edge = voronoi(r, 30)
    J = len(pal)
    pal = pal + [joint(pal)]
    out = idx.copy()
    for c in range(lab.max() + 1):
        m = lab == c
        out[m] = shade(pal[:J], idx[m], int(r.choice([-1, 0, 0, 1])))
    out[(edge < .7) & (r.random((N, N)) < .4)] = J
    return out, pal


def moss_for(ramp_):
    """Moss a little darker than the stone it grows on (sage on chalk, deep green on shale): calm, never a stamp."""
    L = float(np.mean(lum(ramp_)))
    out = []
    for f in (.78, .88, .98):
        target = max(52, min(170, L * f))
        rgb = np.array(colorsys.hsv_to_rgb(.23, .26 if L > 150 else .40, 1)) * 255
        rgb = rgb * target / (.299 * rgb[0] + .587 * rgb[1] + .114 * rgb[2])
        out.append(tuple(int(min(255, c)) for c in rgb))
    return out


def mossy(rid, seed=21):
    out, pal, beds = stacked(rid, seed)
    r = np.random.default_rng(seed + 5)
    k0 = len(pal)
    pal = pal + moss_for(pal[:6])
    for _ in range(4):  # moss creeps along the bed joints, thin and uneven
        y = beds[int(r.integers(len(beds)))]
        x = int(r.integers(N))
        for i in range(int(r.integers(4, 9))):
            xx = (x + i) % N
            if r.random() < .85:
                out[y, xx] = k0 + int(r.integers(0, 2))
            if r.random() < .35:
                out[(y - 1) % N, xx] = k0 + int(r.integers(1, 3))
            if r.random() < .15:
                out[(y + 1) % N, xx] = k0
    return out, pal


def rock_textures(rid):
    out = {rid: paint(*rock_base(rid))}
    i, p, _ = stacked(rid)
    out[f"{rid}_stacked"] = paint(i, p)
    out[f"{rid}_flagstone"] = paint(*flagstone(rid))
    out[f"{rid}_pebbles"] = paint(*pebbles(rid))
    out[f"mossy_{rid}_stacked"] = paint(*mossy(rid))
    return out


# ------------------------------------------------------------------ soils
def hsv_ramp(h, s, vs):
    return [tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(h / 360, s, v / 255)) for v in vs]


PEB = ((112, 104, 100), (138, 128, 122))
NEEDLE = [[(0, 0), (1, 1)], [(0, 1), (1, 0)], [(0, 0), (0, 1)], [(0, 0), (1, 0)]]
FROND = [[(0, 0), (0, 1), (1, 1)], [(0, 0), (1, 0), (1, 1)], [(0, 1), (0, 0), (1, 0)]]


def specks(img, seed, groups):
    """groups: (colours, count, shapes) drawn over the clods (needles, frond bits, fibres)."""
    a = np.array(img)
    r = np.random.default_rng(seed + 77)
    for cols, count, shp in groups:
        for _ in range(count):
            x, y = r.integers(0, N, 2)
            s = shp[int(r.integers(len(shp)))]
            for j, (dy, dx) in enumerate(s):
                a[(y + dy) % N, (x + dx) % N, :3] = cols[min(j, len(cols) - 1)]
    return Image.fromarray(a)


def clods(pal, groups=(), pedrinhas=None, n=36, min_d=2.25):
    return TR.escolher(lambda s: specks(TR.torroes(s, pal, n=n, min_d=min_d, pedrinhas=pedrinhas), s, groups))[0]


def side(top, dirt, seed):
    """Dirt below, the litter running down 3-5 px, darker, with its shadow on the dirt (like podzol_side)."""
    a = np.array(dirt.convert("RGBA"))
    t = np.array(top.convert("RGBA"))
    r = np.random.default_rng(seed)
    depth = 3 + np.round(1.2 * np.sin(2 * np.pi * (np.arange(N) / N + r.uniform())) + r.integers(0, 2, N)).astype(int)
    for x in range(N):
        a[:depth[x], x] = t[:depth[x], x]
        a[:depth[x], x, :3] = (a[:depth[x], x, :3] * .8).astype(np.uint8)
        a[depth[x], x, :3] = (a[depth[x], x, :3] * .78).astype(np.uint8)
        if r.random() < .3:
            a[depth[x] + 1, x, :3] = (a[depth[x] + 1, x, :3] * .9).astype(np.uint8)
    return Image.fromarray(a)


def plates(seed, rgb, ctr, n, crack, sat):
    """Cracked crusts: plates of the grain, the top rim of each catching light, thin cracks between."""
    idx = levels(field(seed, .6), [1, 2, 3, 3, 2, 1])
    pal = calm_pal(ramp(rgb, 6, ctr), sat)
    r = np.random.default_rng(seed)
    lab, edge = voronoi(r, n)
    J = len(pal)
    pal = pal + [crack]
    out = idx.copy()
    for c in range(lab.max() + 1):
        m = lab == c
        out[m] = shade(pal[:J], idx[m], int(r.choice([-1, 0, 0, 1])))
    up = (np.roll(lab, 1, 0) != lab) & (edge >= .7)
    out[up] = shade(pal[:J], out[up], 1)
    out[edge < .7] = J
    return paint(out, pal)


def grain_soil(seed, rgb, ctr, accents, hue=.01, macro=3.4):
    idx = levels(field(seed, .5), [1, 2, 3, 3, 2, 1])
    pal = ramp(rgb, 6, ctr, hue_dark=hue)
    r = np.random.default_rng(seed + 1)
    mask = np.zeros((N, N), bool)
    idx, pal = stamp_accents(idx, pal, mask, r, accents)
    return paint(calm(idx, pal, macro, mask=mask), pal)


def soil_family():
    dirt = clods(hsv_ramp(26, .48, [86, 112, 132, 150]), pedrinhas=PEB)
    fern = clods(hsv_ramp(28, .42, [64, 86, 104, 120]),
                 [([(92, 100, 58), (78, 86, 50)], 7, FROND), ([(122, 96, 66)], 5, NEEDLE)])
    needle = clods(hsv_ramp(22, .46, [66, 88, 106, 122]), [([(150, 96, 56), (128, 82, 48)], 16, NEEDLE)], n=30)
    return {
        "lateritic_soil": clods(hsv_ramp(16, .50, [90, 120, 142, 162]), pedrinhas=PEB),
        "fern_litter": fern, "fern_litter_side": side(fern, dirt, 41),
        "needle_litter": needle, "needle_litter_side": side(needle, dirt, 43),
        "peat": clods(hsv_ramp(24, .36, [44, 58, 70, 80]), [([(86, 70, 52)], 6, [[(0, 0), (0, 1), (0, 2)]])], n=40, min_d=2.0),
        "packed_earth_floor": clods(hsv_ramp(26, .40, [112, 128, 140, 150]), n=44, min_d=2.0),
        "volcanic_ash": grain_soil(3, (128, 124, 118), 38, [((70, 68, 70), 5, [(0, 0)]), ((176, 172, 164), 3, [(0, 0), (0, 1)])]),
        "cracked_mud": plates(29, (132, 104, 78), 34, 7, (96, 74, 56), .40),
        "salt_crust": plates(31, (214, 210, 200), 22, 9, (190, 184, 172), .06),
    }


# ------------------------------------------------------------------ amber
def amber_block():
    """Raw amber: a warm mottle of resin with one dark bubble, glassy range (macro ~9.5, like honey), calm colour."""
    r = np.random.default_rng(41)
    c = r.normal(size=(N, N))
    for _ in range(2):
        c = blur(c, 1)
    idx = levels(c / c.std() + .6 * field(91, .7), [1, 3, 4, 4, 3, 1])
    pal = ramp((212, 126, 22), 6, 34, hue_dark=.03, sat_dark=1.0, sat_light=1.0) + [(160, 84, 18)]
    idx[13, 5] = 6
    idx = calm(idx, pal, 9.5, seed=41)
    return paint(idx, calm_pal(pal, .72))


def textures():
    out = {}
    for rid in ROCKS:
        out.update(rock_textures(rid))
    out.update(soil_family())
    out["amber_block"] = amber_block()
    return out
