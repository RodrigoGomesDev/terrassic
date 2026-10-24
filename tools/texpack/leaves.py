"""TX2 (scratch): leaves for the Late Cretaceous pack. Each canopy is built from leaf shapes of its own species,
stamped in two layers by blue noise: a back layer a step darker, a front layer lit from the top-left, with real
holes between them. Tinted leaves are grey (the biome colours them); cherry and azalea carry their own colour.
Transparent pixels keep a dark leaf colour, which is what "fast" graphics shows instead of the holes."""
import sys

import numpy as np
from PIL import Image

import tex as T  # noqa: E402
from fit import fit  # noqa: E402
from stamps import poisson  # noqa: E402
from tex import N  # noqa: E402

from vanilla import VANILLA as TX2  # noqa: E402

CLUSTER = {"birch": (4.6, 4, 2), "acacia": (5.0, 5, 2)}

CH = {'D': 1, 'B': 2, 'H': 3, 'S': 4, 'V': 1, 'P': 7, 'Q': 6, 'C': 5, 'G': 8}

SHAPES = {
    "oak": [[".HB.", "HBBD", "BBDD", ".DD."],
            [".HH..", "HBBB.", "BBVBD", ".BDD."],
            ["HB.", "BBD", ".DD"]],
    "dark_oak": [[".HHB.", "HBBBD", "BBVBD", "BBBDD", ".DD.."],
                 [".HB.", "HBBD", "BBDD", ".DD."]],
    "birch": [[".H.", "HBD", ".D."], ["HB", "BD"], [".HB", "HBD", "BD."]],
    # fir twigs: a stem with needles both sides, pointing up or leaning
    "spruce": [["..H..", ".HVH.", "H.V.B", ".DVD.", "D.V.D"],
               ["H.H..", ".HVB.", "H.VB.", ".DV.D", "..VD."],
               ["..H.H", ".BVH.", ".BV.H", "D.VD.", ".DV.."]],
    "jungle": [["..HH..", ".HBBB.", "HBBVBD", ".BVBDD", "..DDD."],
               ["..HH..", ".BBBH.", "DBVBBH", "DDBVB.", ".DDD.."],
               [".HH.", "HBVB", "BVBD", ".DD."]],
    "acacia": [["HB", "BD"], [".H.", "HBD"], ["HB."]],
    "mangrove": [[".HHB.", "HBBBD", ".BDD."], [".HB", "HBD", "BDD", "DD."]],
    "azalea": [[".HB.", "HBBD", ".BD."], ["HB", "BD"]],
}

# species: (target name, transparent share, rmin, colour (hue, sat) or None for grey)
SPECIES = {
    "oak": ("oak_leaves", .33, 2.2, None),
    "dark_oak": ("dark_oak_leaves", .28, 2.6, None),
    "birch": ("birch_leaves", .42, 1.8, None),
    "spruce": ("spruce_leaves", .38, 1.6, None),
    "jungle": ("jungle_leaves", .30, 3.0, None),
    "acacia": ("acacia_leaves", .42, 2.2, None),
    "mangrove": ("mangrove_leaves", .18, 2.2, None),
    "azalea": ("azalea_leaves", .23, 2.0, (.24, .52)),
}


def canopy(species, seed=1):
    """(tone map 0..4, opaque mask). Back layer first (one tone darker), then the front layer."""
    _, holes, rmin, _ = SPECIES[species]
    shapes = SHAPES[species]
    r = T.rng(seed)
    t = np.zeros((N, N), int)
    op = np.zeros((N, N), bool)
    target = 1 - holes
    for layer, shift in ((0, -1), (1, 0)):
        if species in CLUSTER:
            R, k, sp = CLUSTER[species]
            pts = [((cx + int(r.integers(-sp, sp + 1))) % N, (cy + int(r.integers(-sp, sp + 1))) % N)
                   for (cx, cy) in poisson(seed + 10 * layer + 3, 40, R) for _ in range(k)]
        else:
            pts = poisson(seed + 10 * layer + 3, 120, rmin)
        for (x, y) in pts:
            if layer == 0 and op.mean() > target * .55:
                break
            if layer == 1 and op.mean() > target:
                break
            sh = shapes[int(r.integers(0, len(shapes)))]
            for j, row in enumerate(sh):
                for i, c in enumerate(row):
                    if c == '.':
                        continue
                    yy, xx = (y + j) % N, (x + i) % N
                    t[yy, xx] = max(0, CH[c] + shift)
                    op[yy, xx] = True
    # a lone opaque pixel or a pinhole reads as noise: fill pinholes, drop lone leaves
    nb = T.neighbours(op.astype(int), False).sum(0)
    op = np.where(~op & (nb >= 4), True, op)
    t = np.where(op & (t == 0) & (nb >= 4), 1, t)
    nb = T.neighbours(op.astype(int), True).sum(0)
    op = np.where(op & (nb == 0), False, op)
    return t, op


def leaves(species, seed=1):
    name, _, _, col = SPECIES[species]
    t, op = canopy(species, seed)
    m, c = TX2[name][0] - 2, TX2[name][1]
    hue, sat = col if col else (0, 0)
    pal = fit(t[op], 5, m, c, hue, sat, hue_shift=.03 if col else 0, sat_shift=.08 if col else 0)
    img = np.asarray(T.colorize(t, pal)).copy()
    img[..., 3] = np.where(op, 255, 0)
    dark = (np.array(pal[0]) * .6).round()
    img[~op, :3] = dark
    return Image.fromarray(img, "RGBA")


def flowering_azalea(seed=1):
    img = np.asarray(leaves("azalea", seed)).copy()
    flowers = [(176, 100, 150), (198, 128, 176), (146, 78, 124)]
    for (x, y) in poisson(seed + 40, 6, 4.2):
        for (dy, dx), k in (((0, 1), 1), ((1, 0), 0), ((1, 1), 2), ((1, 2), 0), ((2, 1), 2)):
            yy, xx = (y + dy) % N, (x + dx) % N
            img[yy, xx, :3] = flowers[k]
            img[yy, xx, 3] = 255
    return Image.fromarray(img, "RGBA")


def cherry(seed=1):
    """A pink canopy of petal clumps (back), open five-petal blossoms with a deep-rose eye (front) and a few
    green leaves showing through; pink fitted to the vanilla cherry canopy's numbers."""
    SHAPES["cherry"] = SHAPES["oak"]
    SPECIES["cherry"] = ("cherry_leaves", .30, 2.4, None)
    t, op = canopy("cherry", seed)              # tones 0..4: pink petals in shade
    r = T.rng(seed + 9)
    for (x, y) in poisson(seed + 21, 5, 4.5):    # green leaves peeking out (tones 8..9)
        if op[y, x]:
            t[y, x] = 8
            t[y, (x + 1) % N] = 9
    flower = [".5.", "565", ".5."]
    for (x, y) in poisson(seed + 5, 9, 3.6):     # blossoms (5 = petal, 6 = eye)
        for j, row in enumerate(flower):
            for i, ch in enumerate(row):
                if ch != '.':
                    t[(y + j) % N, (x + i) % N] = int(ch)
                    op[(y + j) % N, (x + i) % N] = True
    m, c = TX2["cherry_leaves"][0] - 2, TX2["cherry_leaves"][1]
    pal = fit(t[op & (t < 5)], 5, m - 6, c * .7, .935, .30, hue_shift=.02, sat_shift=-.05)
    full = pal + [(252, 226, 238), (228, 128, 168), (0, 0, 0), (84, 116, 58), (110, 144, 70)]
    img = np.asarray(T.colorize(t, full)).copy()
    img[..., 3] = np.where(op, 255, 0)
    img[~op, :3] = (np.array(pal[0]) * .6).round()
    return Image.fromarray(img, "RGBA")


ALL = {f"{s}_leaves": leaves(s, i * 7 + 1) for i, s in enumerate(SPECIES)}
ALL["flowering_azalea_leaves"] = flowering_azalea(15)
ALL["cherry_leaves"] = cherry(3)
