"""TX3: the vanilla rocks and ores of the Late Cretaceous pack.

Rocks are drawn from what they are made of: granite and diorite as interlocking crystals (feldspar, quartz,
dark mica or hornblende), andesite fine-grained with a few pale phenocrysts, tuff as volcanic ash with lapilli,
deepslate foliated in thin layers, calcite with rhombic cleavage. Ores sit on exactly the pack's own stone (or
deepslate), so an ore block never looks pasted in; the mineral comes as a natural vein with blebs along it, in
the colours of the real mineral: coal seams, rusty limonite, malachite with native copper, gold in a quartz vein,
cinnabar, lazurite with pyrite, diamond in a dark kimberlite pocket, emerald in a calcite vein."""
import math

import numpy as np
from PIL import Image

import api
import cretaceo as C
import tex as T
from targets import measure
from vanilla import target
from stamps import base, poisson, stamp
from tex import N


def crystals(seed, nx, ny, shares, jitter=.9):
    """Interlocking crystals: small Voronoi cells, each given a mineral by `shares` (tone ranges with weights)."""
    pts = T.jittered_points(seed, nx, ny, jitter)
    idx, d1, d2 = T.voronoi(pts, warp=T.fbm(seed + 1, [(4, 4, .5), (8, 8, .5)]), warp_amp=1.0)
    r = T.rng(seed + 2)
    kinds = r.choice(len(shares), len(pts), p=np.array([s[1] for s in shares]) / sum(s[1] for s in shares))
    t = np.zeros((N, N), int)
    for k, (tones, _) in enumerate(shares):
        lo, hi = tones
        cell_tone = r.integers(lo, hi + 1, len(pts))
        m = kinds[idx] == k
        t[m] = cell_tone[idx][m]
    # a crystal catches light on its upper-left edge
    edge = T.cell_edges(idx)
    lit = T.roll(edge, -1, -1) & ~edge
    hi_tone = max(s[0][1] for s in shares)
    t = np.where(lit & (t < hi_tone), t + 1, t)
    return T.cleanup(t, 1)


def granite():
    t = crystals(11, 6, 6, [((0, 0), .14), ((1, 3), .62), ((4, 5), .24)])
    return api.paint(t, api.Material("granite", .03, .28, hue_shift=.02, sat_shift=.18, dl=-3, n=6))


def diorite():
    t = crystals(13, 5, 5, [((0, 1), .32), ((3, 5), .68)])
    return api.paint(t, api.Material("diorite", .1, .03, dl=-4, n=6))


def andesite():
    t = base(15, 2, 1, 3, .2, .18, layers=((4, 4, .5), (8, 8, .3), (16, 16, .2)))
    r = T.rng(16)
    for (x, y) in poisson(17, 7, 3.6):                 # pale phenocrysts, little laths
        stamp(t, x, y, ['44'] if r.random() < .6 else ['4', '4'], {'4': 4})
    for (x, y) in poisson(18, 6, 3.2):
        stamp(t, x, y, ['0'], {'0': 0})
    return api.paint(t, api.Material("andesite", .58, .03, dl=-3, n=5))


def tuff():
    t = base(19, 2, 1, 3, .22, .2, layers=((4, 4, .5), (8, 8, .5)))
    r = T.rng(20)
    for (x, y) in poisson(21, 9, 3.4):                 # lapilli: pale pumice and dark scoria, rounded
        if r.random() < .5:
            stamp(t, x, y, ['.4', '43', '3.'][:2] if r.random() < .5 else ['44', '43'], {'4': 4, '3': 3})
        else:
            stamp(t, x, y, ['00', '01'] if r.random() < .5 else ['0'], {'0': 0, '1': 1})
    return api.paint(t, api.Material("tuff", .16, .09, dl=-3, n=5))


def deepslate_tones(seed=23):
    f = T.fbm(seed, [(2, 8, .5), (4, 16, .3), (8, 16, .2)])
    t = T.quantize(f, [.12, .25, .3, .23, .1])
    r = T.rng(seed + 1)
    for (x, y) in poisson(seed + 2, 4, 5):             # cleavage: short splits along the layers
        L = int(r.integers(3, 6))
        stamp(t, x, y, ['0' * L, '.' + '4' * (L - 1)], {'0': 0, '4': 4})
    return T.cleanup(t, 1)


DEEPSLATE = api.Material("deepslate", .62, .06, dl=-3, n=5)


def deepslate():
    return api.paint(deepslate_tones(), DEEPSLATE)


def deepslate_top():
    t = base(25, 2, 1, 3, .22, .2, layers=((4, 4, .5), (8, 8, .5)))
    for (x, y) in poisson(26, 5, 4.5):
        stamp(t, x, y, ['0.', '.4'], {'0': 0, '4': 4})
    return api.paint(t, api.Material("deepslate_top", .62, .06, dl=-3, n=5))


def cobbled_deepslate():
    t, _ = C.cobble_tones(27)
    return api.paint(t, api.Material("cobbled_deepslate", .62, .06, dl=-3, n=6))


def calcite():
    t = base(29, 3, 2, 4, .2, .2, layers=((4, 4, .5), (8, 8, .5)))
    ys, xs = np.mgrid[0:N, 0:N]
    t = np.where((xs + 2 * ys) % 11 == 0, np.minimum(t, 1), t)   # rhombic cleavage: two families of faint lines
    t = np.where((xs - ys) % 9 == 0, np.minimum(t, 2), t)
    return api.paint(T.cleanup(t, 1), api.Material("calcite", .12, .03, dl=-3, n=5))


# ------------------------------------------------------------------ ores
def vein_path(seed):
    """A gently curving line across the face, closing on the torus (slope 1/2 wraps after 16 columns)."""
    r = T.rng(seed)
    y0, ph = r.integers(0, N), r.uniform(0, 6.283)
    return [(x, int(round(y0 + x * .5 + 1.2 * math.sin(6.283 * x / N + ph))) % N) for x in range(N)]


BLEBS = [  # a light, b body, c mineral shadow, d the rock shaded under the bleb, e the rock lit above it
    [".ee.", "eabe", "abbc", ".bcd", "..d."],
    ["ee.", "abe", "bbc", ".cd"],
    [".e.", "eae", "abc", ".cd"],
    ["eee", "abb", "bcd"],
    ["ee", "ab", "cd"],
]


def ore(base_img, seed, mineral, host=None, n_blebs=8, darken_seam=False, speck=None):
    """mineral: 3 colours (light, body, shadow). host: colour of the vein filling (quartz, calcite) or None.
    darken_seam: the vein is a dark seam in the rock (coal). speck: a second mineral sprinkled beside the
    blebs (pyrite in lapis)."""
    img = np.asarray(base_img).copy()
    path = vein_path(seed)
    r = T.rng(seed + 1)
    for x, y in path:
        if darken_seam:
            img[y, x, :3] = (img[y, x, :3] * .5).astype(np.uint8)
            img[(y + 1) % N, x, :3] = (img[(y + 1) % N, x, :3] * .72).astype(np.uint8)
        elif host is not None and r.random() < .85:
            img[y, x, :3] = host
            img[(y + 1) % N, x, :3] = (img[(y + 1) % N, x, :3] * .8).astype(np.uint8)
    order = r.permutation(N)
    taken = []
    for px in order:
        if len(taken) >= n_blebs:
            break
        x, y = path[px]
        y = (y + int(r.integers(-2, 3))) % N               # some blebs sit just off the vein
        if any(min(abs(x - a), N - abs(x - a)) < 4 and min(abs(y - b), N - abs(y - b)) < 4 for a, b in taken):
            continue
        taken.append((x, y))
        shape = BLEBS[int(r.integers(0, len(BLEBS)))]
        for j, row in enumerate(shape):
            for i, ch in enumerate(row):
                if ch == '.':
                    continue
                yy, xx = (y + j - 2) % N, (x + i - 1) % N
                if ch == 'd':
                    img[yy, xx, :3] = (img[yy, xx, :3] * .45).astype(np.uint8)
                elif ch == 'e':
                    img[yy, xx, :3] = np.minimum(img[yy, xx, :3].astype(int) * 1.28, 255).astype(np.uint8)
                else:
                    img[yy, xx, :3] = mineral["abc".index(ch)]
        if speck is not None and r.random() < .7:
            img[(y + 2) % N, (x - 2) % N, :3] = speck
    return Image.fromarray(img, "RGBA")


MINERALS = {
    #        light, body, shadow                      host vein          kwargs
    "coal": (((110, 110, 118), (44, 44, 50), (22, 22, 26)), None, dict(darken_seam=True)),
    "iron": (((230, 184, 140), (190, 122, 76), (130, 72, 46)), None, dict()),
    "copper": (((132, 214, 160), (70, 156, 110), (186, 104, 60)), None, dict()),
    "gold": (((255, 246, 176), (240, 198, 64), (172, 116, 28)), (228, 224, 210), dict(n_blebs=6)),
    "redstone": (((255, 112, 86), (206, 40, 32), (122, 16, 16)), None, dict()),
    "lapis": (((126, 160, 236), (46, 84, 190), (26, 40, 112)), None, dict(speck=(222, 192, 90))),
    "diamond": (((232, 255, 252), (112, 224, 228), (36, 124, 140)), None, dict(n_blebs=5)),
    "emerald": (((150, 230, 176), (38, 188, 98), (16, 112, 58)), (214, 212, 202), dict(n_blebs=5)),
}


def ores():
    stone = C.stone(4)
    slate = deepslate()
    out = {}
    for i, (name, (cols, host, kw)) in enumerate(MINERALS.items()):
        for key, rock, s0 in ((f"{name}_ore", stone, 100), (f"deepslate_{name}_ore", slate, 200)):
            k2 = dict(kw)
            if rock is slate and name in ("iron", "coal"):
                k2["n_blebs"] = 11                       # deep veins run richer
            out[key] = best_of(key, lambda sd: ore(rock, sd, cols, host, **k2), s0 + i * 7)
    return out


def best_of(name, make, seed, tries=16):
    """The vein falls differently with each seed: keep the layout closest to the vanilla ore's numbers."""
    lum, ctr = target(name)[:2]
    best = None
    for k in range(tries):
        img = make(seed + 1000 * k)
        if T.seam_score(img) > 2.0 and T.seam_excess(img) > 1.1:
            continue
        m = measure(img)
        err = abs(m["lum"] - lum) + .5 * abs(m["ctr"] - ctr)
        if best is None or err < best[0]:
            best = (err, img)
    return best[1]


ALL = {
    "granite": granite(), "diorite": diorite(), "andesite": andesite(), "tuff": tuff(),
    "deepslate": deepslate(), "deepslate_top": deepslate_top(), "cobbled_deepslate": cobbled_deepslate(),
    "calcite": calcite(),
}
ALL.update(ores())
