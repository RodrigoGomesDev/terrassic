"""Woods of the mod in the calm style (approved 25/10, see chao.py): bark of fine vertical fibres with each tree's own mark kept small,
planks of fine streaky grain in 4 boards like vanilla, rings on the ends, stripped wood smooth."""
import colorsys
import numpy as np
import chao as C
N = 16
def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def wood_rgb(h, v=.70, sat=1.25):
    """Cut wood a little darker and richer than the table's pale colour (vanilla planks sit near v .64, s .52)."""
    hh, ss, vv = colorsys.rgb_to_hsv(*(np.array(hexrgb(h)) / 255))
    return tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(hh, min(1, ss * sat), min(vv, v)))
# bark colour, wood colour, bark style
WOODS = {
    "araucaria": ("#5a4a3b", "#cdb07e", "scales"),
    "ginkgo": ("#615a50", "#d6c29a", "furrows"),
    "metasequoia": ("#723a25", "#bf8266", "fibres"),
    "taxodium": ("#5b5045", "#c49f75", "fibres"),
    "tree_fern": ("#43321f", "#83623e", "fern_bases"),
    "sabal": ("#6e6150", "#ccb48c", "palm_bases"),
    "magnolia": ("#6e6a62", "#d8c49e", "smooth"),
    "podocarpus": ("#6c442d", "#cc985c", "fibres"),
    "platanus": ("#8c866a", "#d2b490", "patches"),
}
SEED = {t: 500 + 13 * i for i, t in enumerate(WOODS)}
def streaks(seed, vertical=True, length=4, clump=.75):
    """Fine grain stretched along the fibre: each pixel averaged with `length` neighbours along one axis."""
    r = np.random.default_rng(seed)
    g = r.normal(size=(N, N))
    ax = 0 if vertical else 1
    s = sum(np.roll(g, k, ax) for k in range(-(length // 2), length - length // 2)) / length
    g = (1 - clump) * g + clump * s * np.sqrt(length)
    lo = sum(np.roll(np.roll(g, dy, 0), dx, 1) for dy in range(-2, 2) for dx in range(-2, 2)) / 16
    g = g - lo
    return g / g.std()
def tones(f, w=(1, 2, 3, 3, 2, 1)): return C.levels(f, list(w))
def calmish(pal, sat): return C.calm_pal(pal, sat, hue_to=28, pull=.3)   # woods lean to honey-brown, never pink
# ------------------------------------------------------------------ bark
def bark(tid):
    bark_c, _, style = WOODS[tid]; seed = SEED[tid]; r = np.random.default_rng(seed)
    rgb = hexrgb(bark_c)
    f = streaks(seed, True, 5, .8)
    x = np.arange(N)
    if style in ("fibres", "furrows"):   # long furrows: a darker column every 3-5 px, broken, wandering by 1
        cols = np.cumsum(r.integers(3, 6, size=6)) % N
        for c0 in cols:
            wob = np.round(np.sin(np.arange(N) / N * 2 * np.pi + r.uniform(0, 6)) * (1 if style == "fibres" else .6)).astype(int)
            for y in range(N):
                if r.random() < (.8 if style == "fibres" else .65): f[y, (c0 + wob[y]) % N] -= 1.4
    idx = tones(f)
    pal = C.ramp(rgb, 6, 46 if style != "fern_bases" else 40, hue_dark=.015)
    mask = np.zeros((N, N), bool)
    if style == "scales":    # araucaria: small overlapping plates, lit top-left edge
        for y0 in range(0, N, 4):
            for x0 in range((y0 // 4 % 2) * 3 + int(r.integers(0, 2)), N, 6):
                idx[y0 % N, x0 % N] = 4; idx[y0 % N, (x0 + 1) % N] = 4
                idx[(y0 + 2) % N, (x0 + 1) % N] = 1; idx[(y0 + 2) % N, (x0 + 2) % N] = 1
    if style == "fern_bases":  # tree fern: rhombic leaf-base scars in a lattice, dark centre
        for y0 in range(0, N, 5):
            for x0 in range((y0 // 5 % 2) * 3, N, 6):
                for dy, dx, v in ((0, 1, 4), (1, 0, 4), (1, 1, 0), (1, 2, 2), (2, 1, 1)):
                    idx[(y0 + dy) % N, (x0 + dx) % N] = v
    if style == "palm_bases":  # sabal: criss-cross boots of old leaf bases
        for y0 in range(0, N, 4):
            for x0 in range((y0 // 4 % 2) * 4, N, 8):
                for i in range(3):
                    idx[(y0 + i) % N, (x0 + i) % N] = 4 if i == 0 else 3
                    idx[(y0 + i + 1) % N, (x0 + i) % N] = 1
    if style == "smooth":      # magnolia: smooth grey bark with a few lenticels
        idx = tones(streaks(seed, True, 3, .4), (1, 3, 4, 4, 3, 1))
        for _ in range(7):
            y, xx = r.integers(N, size=2); idx[y, xx] = 4; idx[y, (xx + 1) % N] = 4; mask[y, xx] = mask[y, (xx + 1) % N] = True
    if style == "patches":     # plane tree: soft camouflage of flaking patches
        c = r.normal(size=(N, N))
        for _ in range(2): c = C.blur(c, 1)
        idx = tones(.45 * c / c.std() + .8 * streaks(seed, True, 3, .5), (1, 2, 3, 3, 2, 1))
        pal = C.ramp(rgb, 6, 40)
    idx = C.calm(idx, pal, 5.0, mask=mask, seed=seed) if style in ("fibres", "furrows", "smooth") else idx
    return C.paint(idx, calmish(pal, .40))
# ------------------------------------------------------------------ planks
def planks(tid):
    _, wood_c, _ = WOODS[tid]; seed = SEED[tid] + 7; r = np.random.default_rng(seed)
    f = streaks(seed, False, 12, .95)
    idx = tones(f, (1, 2, 4, 4, 2, 1))
    pal = C.ramp(wood_rgb(wood_c), 6, 46, hue_dark=.02)
    J = len(pal); pal = pal + [tuple(int(v * .86) for v in pal[0])]
    out = idx.copy()
    for b in range(4):  # four boards of 4 px with a seam under each; one end joint on every other board
        y0 = b * 4
        out[y0:y0 + 3] = C.shade(pal[:J], out[y0:y0 + 3], int(r.choice([-1, 0, 1])))   # each board its own shade
        out[y0 + 3, :] = J
        if b % 2 == 0:
            xj = int(r.integers(2, 14))
            out[y0:y0 + 3, xj] = J
    return C.paint(out, calmish(pal, .48))
# ------------------------------------------------------------------ stripped and ends
def stripped(tid):
    _, wood_c, _ = WOODS[tid]; seed = SEED[tid] + 5
    idx = tones(streaks(seed, True, 7, .9), (1, 3, 4, 4, 3, 1))
    pal = C.ramp(wood_rgb(wood_c, .76), 6, 34, hue_dark=.02)
    return C.paint(C.calm(idx, pal, 3.5, seed=seed), calmish(pal, .46))
def log_top(tid, strip=False):
    bark_c, wood_c, _ = WOODS[tid]; seed = SEED[tid] + 3; r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:N, 0:N] + .5
    cx, cy = 8 + r.uniform(-.5, .5), 8 + r.uniform(-.5, .5)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) + .25 * np.sin(np.arctan2(yy - cy, xx - cx) * 3 + r.uniform(0, 6))
    ring = np.floor(d / 2.0).astype(int) % 2               # growth rings 2 px apart
    grain = r.random((N, N))
    idx = np.where(ring == 0, 3, 2)
    idx = np.where(grain < .12, idx - 1, np.where(grain > .9, idx + 1, idx)).clip(0, 4)
    idx[d < 1.0] = 1                                        # pith
    pal = list(C.ramp(wood_rgb(wood_c, .74), 5, 40, hue_dark=.02))
    out = idx.copy()
    edge = np.minimum(np.minimum(xx, N - xx), np.minimum(yy, N - yy))
    if not strip:   # one pixel of bark round the edge, a darker sapwood line inside it
        bp = C.ramp(hexrgb(bark_c), 3, 26)
        k = len(pal); pal = pal + bp
        out[edge < 1] = k + 1 + (r.random((N, N)) < .3)[edge < 1]
        out[(edge >= 1) & (edge < 2)] = 1
    else:
        out[edge < 1] = 1
    return C.paint(out, calmish(pal, .40))
def textures(tid):
    return {f"{tid}_log": bark(tid), f"{tid}_log_top": log_top(tid), f"stripped_{tid}_log": stripped(tid),
            f"stripped_{tid}_log_top": log_top(tid, True), f"{tid}_hewn_planks": planks(tid)}
