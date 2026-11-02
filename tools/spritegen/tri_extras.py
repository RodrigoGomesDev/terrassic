"""The Triceratops' own egg and saddle art (2026-11-02, the 1.5 remake; its study page, "Triceratops: estudo e modelo").

Egg (block terrassic:triceratops_egg, 3 hatch stages): three big OVAL eggs lying half under the leaves of a mound of
rotting leaves and fern on the forest floor by a river. No Triceratops egg is known: this is the study's hypothesis.
The early horned dinosaurs laid soft, leathery eggs (Protoceratops, Norell et al. 2020) and soft eggs were buried in
plant matter that warms as it rots, like a crocodile's or a megapode's mound; Hell Creek was a wet forest with
rivers, so the clutch goes under leaves, not in sand. The shell is matte olive-brown, mottled, with bits of leaf
stuck to it; it dents and tears (stage 1: the leaves pulled aside, the egg that hatches first slumps; stage 2: a
tear with the calf's pale beak and the nub of its nose horn).
Kept apart from the other remade clutches: the T. rex's long pair standing in twigs, the Giganotosaurus' round
pale eggs in a cracked mud pit, the Protoceratops' long pale eggs in red sand, the Carnotaurus' rust pairs on clay.

Saddle (item terrassic:triceratops_saddle): the drover's pack saddle of the model (cangalha): the two wooden heads of
the frame, the hide seat with its rolled blanket, a woven palm-fibre basket (balaio) hanging on the side tied with
rope, and the rope stirrup with its wooden step. No metal, no wool.

usage: python3 -B tools/spritegen/tri_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (114, 100, 64), "light": (132, 118, 78), "mottle": (94, 80, 52), "mottle2": (80, 68, 44),
         "crease": (92, 84, 56), "leaf": (88, 60, 34), "leaf2": (120, 84, 44),
         "tear": (58, 44, 30), "hole": (30, 22, 18), "membrane": (196, 186, 150),
         "beak": (64, 54, 52), "horn": (214, 204, 178), "skin": (128, 112, 124)}
LITTER = {"l0": (58, 40, 26), "l1": (78, 54, 32), "l2": (104, 72, 40), "l3": (134, 96, 52), "rib": (156, 120, 70),
          "fern": (70, 88, 44), "fern2": (96, 114, 56), "soil": (44, 32, 24)}


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(71)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            k = 1.05 - 0.12 * (y / 15.0)       # lit from above, darker toward the leaves
            c = SHELL["light"] if (x * 3 + y * 7) % 13 == 0 else SHELL["base"]
            px[x, y] = tuple(min(255, int(v * k)) for v in c) + (255,)
    for _ in range(14):                          # the mottling: soft blotches of a darker olive
        x, y = rnd.randrange(16), rnd.randrange(16)
        px[x, y] = SHELL["mottle"] + (255,)
        if rnd.random() < 0.5:
            px[(x + 1) % 16, y] = SHELL["mottle2"] + (255,)
    folds = [(2, 4, 3), (10, 3, 3), (5, 10, 4), (12, 11, 3)]
    if stage >= 1:                               # the leathery shell slumps before hatching: more and longer creases
        folds += [(1, 7, 5), (8, 6, 5), (3, 13, 4), (10, 8, 4)]
    for x0, y0, n in folds:
        for i in range(n):
            px[(x0 + i) % 16, y0 + (i % 3 == 1)] = SHELL["crease"] + (255,)
    for _ in range(6):                           # bits of rotten leaf stuck to the damp shell, most of them low
        x, y = rnd.randrange(16), 15 - int(rnd.random() ** 1.5 * 10)
        px[x, y] = (SHELL["leaf"] if rnd.random() < 0.6 else SHELL["leaf2"]) + (255,)
    if stage >= 2:                               # a tear: the calf's beak and the nub of its nose horn
        for x, y in ((4, 6), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 6), (11, 6)):
            px[x, y] = SHELL["tear"] + (255,)
        for x, y in ((5, 6), (10, 7), (6, 8), (9, 8)):
            px[x, y] = SHELL["hole"] + (255,)
        for x, y in ((6, 6), (7, 6), (9, 6), (6, 7), (9, 7)):
            px[x, y] = SHELL["skin"] + (255,)
        px[8, 6] = SHELL["horn"] + (255,); px[7, 7] = SHELL["beak"] + (255,); px[8, 7] = SHELL["beak"] + (255,)
        for x in (4, 11):
            px[x, 7] = SHELL["membrane"] + (255,)
    return img


def nest():
    """rotting leaves: broad brown leaves with pale midribs, darker soil between, a fern frond"""
    from PIL import Image
    rnd = random.Random(19)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 5 + y * 3 + (x * y) % 7) % 9
            px[x, y] = (LITTER["l0"] if h == 0 else LITTER["l2"] if h in (3, 7) else LITTER["l1"]) + (255,)
    # whole leaves lying at angles: an oval of one tone with its midrib
    for cx, cy, dx, dy, tone in ((4, 3, 1, 1, "l3"), (11, 5, 1, -1, "l2"), (6, 11, -1, 1, "l3"), (13, 13, 1, 0, "l2")):
        for i in range(-2, 3):
            for j in (-1, 0, 1):
                x, y = cx + i * dx + (j if dy == 0 else 0), cy + i * dy + (j if dy != 0 and dx == 0 else 0)
                if dx and dy:
                    x, y = cx + i * dx + (j if j > 0 else 0), cy + i * dy + (-j if j < 0 else 0)
                if 0 <= x < 16 and 0 <= y < 16 and (abs(i) < 2 or j == 0):
                    px[x, y] = LITTER[tone] + (255,)
        for i in range(-2, 3):
            x, y = cx + i * dx, cy + i * dy
            if 0 <= x < 16 and 0 <= y < 16:
                px[x, y] = LITTER["rib"] + (255,)
    for i in range(6):                             # a fern frond across one corner
        x, y = 1 + i, 14 - i
        px[x, y] = LITTER["fern"] + (255,)
        if i % 2 == 0 and x + 1 < 16:
            px[x + 1, y] = LITTER["fern2"] + (255,)
    for _ in range(5):
        px[rnd.randrange(16), rnd.randrange(16)] = LITTER["soil"] + (255,)
    return img


# a big oval egg lying down: (along from, along to, half width, height) slices, about 1.7 times as long as wide.
# Each slice is a rounded cross (a wide low bar and a narrow high bar), so the egg reads round from any side.
EGG_SLICES = [(0.0, 0.9, 1.1, 2.4), (0.9, 2.1, 1.9, 3.6), (2.1, 5.5, 2.3, 4.3), (5.5, 6.7, 1.9, 3.6), (6.7, 7.6, 1.1, 2.4)]
# three eggs in a loose triangle, the narrow ends in toward the middle (centre x, z, axis, y rotation, sink)
EGGS = [(5.0, 5.6, "z", 22.5, 1.6), (11.2, 6.0, "z", -22.5, 1.8), (8.2, 11.4, "x", 0, 1.5)]
HATCH = 2   # the egg that hatches first (the one in front in the inventory)
TOP = 2.5   # the top of the mound where the eggs lie
# leaves laid over the clutch (from, to, y rotation): the first two are pulled aside before hatching
LEAVES = [([6.5, 0, 7], [10, 0.5, 10.5], 22.5), ([3, 0, 3], [6.5, 0.5, 5.5], -22.5),
          ([10.5, 0, 9.5], [14, 0.5, 12.5], 22.5), ([4, 0, 11], [6.5, 0.5, 14], 0)]


def _egg(cx, cz, axis, angle, sink, squash=1.0):
    els = []
    for a0, a1, hw, h in EGG_SLICES:
        a0, a1 = a0 - 3.8, a1 - 3.8
        for w, hh in ((hw, h * 0.72 * squash), (hw * 0.72, h * squash)):
            y0, y1 = max(0.5, TOP - sink), TOP - sink + hh
            if axis == "x":
                frm, to = [cx + a0, y0, cz - w], [cx + a1, y1, cz + w]
            else:
                frm, to = [cx - w, y0, cz + a0], [cx + w, y1, cz + a1]
            el = {"from": frm, "to": to, "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], y0, y1, top=True)}
            if angle:
                el["rotation"] = {"origin": [cx, 0.5, cz], "axis": "y", "angle": angle}
            els.append(el)
    return els


def _top_of(i):
    cx, cz, axis, angle, sink = EGGS[i]
    return TOP - sink + EGG_SLICES[2][3]


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    # the mound: a wide low heap of leaves, rounded at the edge, higher toward the middle
    for frm, to in (([1.5, 0, 1], [14.5, 1.2, 15]), ([1, 0, 1.5], [15, 1.2, 14.5]), ([2.5, 1.2, 2.5], [13.5, 2.0, 13.5]),
                    ([3.5, 2.0, 3.5], [12.5, TOP, 12.5]), ([0.3, 0, 5], [1.5, 1.6, 10]), ([14.5, 0, 6], [15.7, 1.4, 11]),
                    ([6, 0, 14.5], [11, 1.5, 15.7]), ([5, 0, 0.3], [9, 1.3, 1.5])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1],
                                                            bottom=frm[1] == 0)})
    for i, (cx, cz, axis, angle, sink) in enumerate(EGGS):
        els += _egg(cx, cz, axis, angle, sink, squash=0.86 if stage >= 1 and i == HATCH else 1.0)
    # the leaves over the clutch, lying on the eggs' backs; before hatching the parent pulls two of them aside
    for k, (frm, to, angle) in enumerate(LEAVES):
        if stage >= 1 and k < 2:
            continue
        y = TOP + 2.0 + 0.4 * (k % 2)
        f2, t2 = [frm[0], y, frm[2]], [to[0], y + 0.5, to[2]]
        el = {"from": f2, "to": t2, "faces": _faces("#nest", f2[0], t2[0], f2[2], t2[2], f2[1], t2[1], bottom=True)}
        if angle:
            el["rotation"] = {"origin": [(frm[0] + to[0]) / 2, y, (frm[2] + to[2]) / 2], "axis": "y", "angle": angle}
        els.append(el)
    if stage >= 1:   # the pulled-aside leaves, heaped at the edge of the mound
        for frm, to in (([1.5, 1.2, 9], [4, 2.6, 13]), ([12, 1.2, 2], [14.5, 2.4, 5.5])):
            els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1])})
    if stage >= 2:
        # the calf's nose horn nub and beak poking out of the tear on top of the egg that slumped
        cx, cz, axis, angle, sink = EGGS[HATCH]
        top = TOP - sink + EGG_SLICES[2][3] * 0.86
        f = {k: {"uv": [8, 6, 9, 7], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
        els.append({"from": [cx - 0.5, top - 0.4, cz - 0.5], "to": [cx + 0.5, top + 0.9, cz + 0.5], "faces": f})
        g = {k: {"uv": [7, 7, 8, 8], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
        els.append({"from": [cx - 1.6, top - 0.4, cz - 0.6], "to": [cx - 0.6, top + 0.4, cz + 0.6], "faces": g})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1.5, 0], "scale": [0.92, 0.92, 0.92]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (34, 24, 16), "w": (92, 65, 41), "x": (125, 90, 55), "W": (154, 116, 70),      # outline, wood
              "h": (87, 64, 47), "H": (112, 85, 61), "j": (140, 109, 76),                        # hide
              "q": (86, 74, 46), "f": (116, 102, 63), "F": (143, 127, 80), "g": (166, 151, 101),  # palm fibre
              "R": (94, 80, 54)}                                                                  # rope
SADDLE_ART = [
    "..oo......oo....",
    ".oWxo....oWxo...",
    ".oxWo....oxWo...",
    ".owxoooooowxoo..",
    ".oojjjjjjjjjjHo.",
    "oHHHHHHHHHHHHjho",
    "owwxwwwwwxwwwwoo",
    ".ofgFRFgFgRgfo..",
    ".oFqFRFqFqRqFoR.",
    ".ogFgFgFgFgFgoR.",
    ".oFqFqFqFqFqFoR.",
    ".ogFgFgFgFgFgoR.",
    ".oFqFqFqFqFqFoR.",
    "..offfffffffo.R.",
    "...ooooooooo.oWo",
    ".............oo.",
]


def saddle_sprite():
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y, row in enumerate(SADDLE_ART):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = SADDLE_PAL[ch] + (255,)
    return img


CUSTOM_EGGS = {"triceratops": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"triceratops_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "triceratops_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "triceratops_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
