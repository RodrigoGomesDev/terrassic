"""The Styracosaurus' own egg and saddle art (05/11/2026, the 1.8 remake; its study page, "Estiracossauro: estudo para a
1.8", approved by Rodrigo with the reed-and-mud nest).

Egg (block terrassic:styracosaurus_egg, 3 hatch stages): four long eggs in a hollow on top of a HEAP of cut reed stalks
on a mud base by the river, a few stalks laid across them. No Styracosaurus egg is known: this is the study's
hypothesis. The early horned dinosaurs laid soft, leathery eggs (Protoceratops, Norell et al. 2020), and soft eggs are
kept warm by plants rotting around them, as in a crocodile's or a megapode's mound; Dinosaur Park was a plain of rivers
and marshes, so the heap is of reeds. The shell is matte, a pale grey-buff with smears of mud low down; soft, it dents
and tears (stage 1: two stalks pulled off, the egg that hatches first slumps; stage 2: a tear with the calf's
pink-grey snout and the nub of its nose horn).
Kept apart from the other remade clutches: the T. rex's long pair in twigs, the Giganotosaurus' round eggs sunk in a
cracked mud pit, the Protoceratops' long pale eggs in red sand, the Carnotaurus' rust pairs on clay, the Triceratops'
olive ovals under leaves, the Gallimimus' speckled ring on gravel, the Pachycephalosaurus' soft eggs among roots, the
Parasaurolophus' white nodular eggs in a raised mud CRATER with reeds across, the Ankylosaurus' eggs in forest loam.
This one is a tall HEAP of stalks, the highest nest of all, the eggs on its top.

Saddle (item terrassic:styracosaurus_saddle): the running pad of the model: the thick hide pad with its fringe, the
grip bar on two short posts, a rope foot loop with its bone toggle. No frame, no baskets, no metal.

usage: python3 -B tools/spritegen/styr_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (196, 186, 166), "light": (214, 206, 188), "mottle": (176, 164, 144), "crease": (160, 148, 128),
         "mud": (104, 84, 64), "mud2": (84, 68, 52), "tear": (70, 56, 44), "hole": (30, 22, 18),
         "membrane": (226, 214, 196), "snout": (168, 125, 129), "snout2": (142, 104, 107), "horn": (226, 214, 192)}
REED = {"r0": (78, 70, 38), "r1": (112, 102, 54), "r2": (142, 130, 70), "r3": (170, 156, 88), "node": (92, 80, 42),
        "mud": (72, 58, 44), "mud2": (58, 46, 36), "rot": (98, 76, 46)}


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(83)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            k = 1.04 - 0.1 * (y / 15.0)
            c = SHELL["light"] if (x * 5 + y * 3) % 11 == 0 else SHELL["base"]
            px[x, y] = tuple(min(255, int(v * k)) for v in c) + (255,)
    for _ in range(10):                          # a faint mottling, the shell is pale and plain
        x, y = rnd.randrange(16), rnd.randrange(16)
        px[x, y] = SHELL["mottle"] + (255,)
    for _ in range(9):                           # smears of mud, most of them low
        x, y = rnd.randrange(16), 15 - int(rnd.random() ** 1.6 * 9)
        px[x, y] = (SHELL["mud"] if rnd.random() < 0.6 else SHELL["mud2"]) + (255,)
        if rnd.random() < 0.5 and x + 1 < 16:
            px[x + 1, y] = SHELL["mud"] + (255,)
    folds = [(3, 5, 3), (11, 4, 2), (6, 11, 3)]
    if stage >= 1:                               # the soft shell slumps before hatching: long creases
        folds += [(1, 8, 5), (9, 7, 5), (4, 13, 4), (11, 10, 4)]
    for x0, y0, n in folds:
        for i in range(n):
            px[(x0 + i) % 16, y0 + (i % 3 == 1)] = SHELL["crease"] + (255,)
    if stage >= 2:                               # a tear: the calf's snout and the nub of its nose horn
        for x, y in ((4, 6), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 6), (11, 6)):
            px[x, y] = SHELL["tear"] + (255,)
        for x, y in ((5, 6), (10, 7), (6, 8), (9, 8)):
            px[x, y] = SHELL["hole"] + (255,)
        for x, y in ((6, 6), (7, 6), (9, 6), (6, 7), (9, 7)):
            px[x, y] = SHELL["snout"] + (255,)
        px[8, 6] = SHELL["horn"] + (255,); px[7, 7] = SHELL["snout2"] + (255,); px[8, 7] = SHELL["snout2"] + (255,)
        for x in (4, 11):
            px[x, 7] = SHELL["membrane"] + (255,)
    return img


def nest():
    """cut reed stalks heaped criss-cross: long straight stems with darker nodes, rotting ones browner, mud between"""
    from PIL import Image
    rnd = random.Random(29)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = (REED["mud"] if (x * 3 + y * 5) % 7 else REED["mud2"]) + (255,)
    # stalks heaped every way: straight stems of uneven length, some lying flat, some on a slant, a node now and then,
    # a lit upper edge; never a woven grid
    stalks = [((0, 2), (9, 1), "r2"), ((5, 4), (15, 5), "r1"), ((0, 8), (6, 9), "rot"), ((7, 7), (15, 9), "r2"),
              ((1, 12), (12, 13), "r1"), ((10, 14), (15, 15), "rot"), ((3, 0), (1, 7), "r3"), ((12, 0), (13, 6), "r3"),
              ((8, 9), (6, 15), "r2"), ((14, 10), (13, 15), "r3")]
    for (x0, y0), (x1, y1), tone in stalks:
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
            px[x, y] = REED["node"] + (255,) if (i + x0) % 6 == 3 else REED[tone] + (255,)
            if abs(x1 - x0) >= abs(y1 - y0) and y + 1 < 16 and i % 2 == 0:
                px[x, y + 1] = REED["r0"] + (255,)          # the stalk's shadow on what lies under it
    for _ in range(5):
        px[rnd.randrange(16), rnd.randrange(16)] = REED["mud2"] + (255,)
    return img


# a long soft egg lying down: (along from, along to, half width, height) slices, about twice as long as wide
EGG_SLICES = [(0.0, 0.8, 0.9, 2.0), (0.8, 1.8, 1.5, 3.0), (1.8, 4.6, 1.8, 3.5), (4.6, 5.6, 1.5, 3.0), (5.6, 6.4, 0.9, 2.0)]
# four eggs in a ring on the top of the heap, the narrow ends in (centre x, z, axis, y rotation, sink)
EGGS = [(5.0, 5.8, "z", 22.5, 1.4), (11.0, 5.4, "z", -22.5, 1.5), (5.2, 10.8, "z", -22.5, 1.3), (11.0, 10.8, "z", 22.5, 1.4)]
HATCH = 2
TOP = 4.2   # the top of the heap, where the eggs lie (the highest of the nests)
# stalks laid across the clutch (from, to, y rotation): the first two are pulled off before hatching
STALKS = [([2, 0, 7.4], [14, 0.6, 8.2], 22.5), ([7.6, 0, 2], [8.4, 0.6, 14], -22.5),
          ([2, 0, 11.6], [12, 0.6, 12.4], 0), ([3.6, 0, 3], [4.4, 0.6, 12], 0)]


def _egg(cx, cz, axis, angle, sink, squash=1.0):
    els = []
    for a0, a1, hw, h in EGG_SLICES:
        a0, a1 = a0 - 3.2, a1 - 3.2
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


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    # the heap: a broad base of stalks and mud, stepping up to a flat top, a few stalk ends sticking out at the edge
    for frm, to in (([0.5, 0, 1.5], [15.5, 1.6, 14.5]), ([1.5, 0, 0.5], [14.5, 1.6, 15.5]), ([1.5, 1.6, 1.5], [14.5, 3.0, 14.5]),
                    ([2.5, 3.0, 2.5], [13.5, TOP, 13.5]), ([0, 0.2, 6], [0.5, 1.0, 9.5]), ([15.5, 0.4, 4], [16, 1.2, 7]),
                    ([5, 0.3, 15.5], [9, 1.0, 16]), ([9, 1.6, 0.6], [12.5, 2.4, 1.5])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1],
                                                            bottom=frm[1] == 0)})
    for i, (cx, cz, axis, angle, sink) in enumerate(EGGS):
        els += _egg(cx, cz, axis, angle, sink, squash=0.86 if stage >= 1 and i == HATCH else 1.0)
    for k, (frm, to, angle) in enumerate(STALKS):
        if stage >= 1 and k < 2:
            continue
        y = TOP + 1.6 + 0.6 * (k % 2)
        f2, t2 = [frm[0], y, frm[2]], [to[0], y + 0.6, to[2]]
        el = {"from": f2, "to": t2, "faces": _faces("#nest", f2[0], t2[0], f2[2], t2[2], f2[1], t2[1], bottom=True)}
        if angle:
            el["rotation"] = {"origin": [(frm[0] + to[0]) / 2, y, (frm[2] + to[2]) / 2], "axis": "y", "angle": angle}
        els.append(el)
    if stage >= 1:   # the stalks pulled off, dropped at the foot of the heap
        for frm, to in (([1, 1.6, 10], [6, 2.2, 11]), ([11, 1.6, 2], [15, 2.2, 3])):
            els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1])})
    if stage >= 2:
        # the calf's nose horn nub and snout poking out of the tear on top of the egg that slumped
        cx, cz, axis, angle, sink = EGGS[HATCH]
        top = TOP - sink + EGG_SLICES[2][3] * 0.86
        f = {k: {"uv": [8, 6, 9, 7], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
        els.append({"from": [cx - 0.5, top - 0.4, cz - 0.5], "to": [cx + 0.5, top + 1.1, cz + 0.5], "faces": f})
        g = {k: {"uv": [7, 7, 8, 8], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
        els.append({"from": [cx - 0.7, top - 0.4, cz - 1.8], "to": [cx + 0.7, top + 0.5, cz - 0.6], "faces": g})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 0.5, 0], "scale": [0.85, 0.85, 0.85]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (34, 24, 16), "w": (94, 67, 42), "W": (125, 92, 58),                          # outline, grip wood
              "h": (106, 74, 54), "H": (133, 97, 74), "j": (160, 123, 94),                        # thick hide pad
              "F": (166, 150, 111), "f": (138, 122, 92),                                          # the fringe
              "R": (133, 115, 80), "r": (94, 80, 54), "B": (207, 194, 168)}                       # rope, bone toggle
SADDLE_ART = [
    "................",
    "..oooooooooo....",
    "..oWWWWWWWWo....",
    "...owo..owo.....",
    ".oooooooooooooo.",
    "ohHHHjHHHHjHHHho",
    "ohHjHHHHjHHHjHho",
    "ohHHHHjHHHHHHHho",
    "oohhhhhhhhhhhhoo",
    ".oFfFfFfFfFfFRo.",
    "..F.F.F.F.F.FR..",
    "..f.f.f.f.f.fR..",
    "............orRo",
    "...........oBBBo",
    "............ooo.",
    "................",
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


CUSTOM_EGGS = {"styracosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"styracosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "styracosaurus_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "styracosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
