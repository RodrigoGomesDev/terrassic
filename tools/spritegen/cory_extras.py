"""The Corythosaurus' own egg art, nest and saddle sprite (1.11.0, its study docs/estudos/15_HERBIVOROS_1_11.md, approved
by Rodrigo on 10/11/2026).

Egg (block terrassic:corythosaurus_egg, 3 hatch stages): no Corythosaurus egg is known; its lambeosaurine kin
Hypacrosaurus laid nearly ROUND eggs of ~20 cm (Horner & Currie 1994). The study's proposal (SPECULATIVE): a shallow
scrape in the forest floor BETWEEN ROOTS, the round eggs in a ring, half covered with fallen CONIFER NEEDLES and twigs.
So: a patch of dark forest litter, two roots arching over it from the sides, a ring of five round eggs (no oval, no
spiral, no mud mound: those are the Maiasaura's and the Edmontosaurus'), pale blue-grey with soft slate speckles (a
shade of the parents' smoke), needles lying over their lower half. At stage 2 one egg is cracked and the calf's narrow
beak pokes out.

Saddle (item terrassic:corythosaurus_saddle): the "Sela de Mata": a narrow pad of beaten bark cloth with a moss-green
seam and a fringe of dyed strips, a low dark hide seat and a bone grip in front.

usage: python3 -B tools/spritegen/cory_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import math
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (186, 194, 200), "light": (206, 212, 218), "speck": (112, 124, 140), "speck2": (142, 152, 166),
         "needle": (92, 70, 42), "crack": (70, 72, 78), "bill": (40, 42, 48), "bill2": (28, 30, 34)}
FLOOR_PAL = {"f0": (44, 36, 26), "f1": (60, 48, 32), "f2": (78, 62, 40), "n0": (110, 78, 44), "n1": (134, 98, 56),
             "moss": (66, 80, 44)}
ROOT = {"r0": (62, 48, 34), "r1": (84, 66, 46), "r2": (104, 84, 60)}


def shell(stage):
    """a pale blue-grey round shell with soft slate speckles, a few brown needles stuck on its lower part"""
    from PIL import Image
    rnd = random.Random(53)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 7 + y * 11 + (x * y) % 7) % 13
            px[x, y] = (SHELL["light"] if h == 0 else SHELL["base"]) + (255,)
    for _ in range(16):
        x, y = rnd.randrange(16), rnd.randrange(16)
        px[x, y] = (SHELL["speck"] if rnd.random() < 0.4 else SHELL["speck2"]) + (255,)
    for _ in range(4):
        x, y = rnd.randrange(14), 11 + rnd.randrange(4)
        px[x, y] = SHELL["needle"] + (255,); px[x + 1, y] = SHELL["needle"] + (255,)
    if stage >= 2:
        for x, y in ((4, 6), (5, 5), (6, 6), (7, 5), (8, 6), (9, 5), (10, 6), (11, 5)):
            px[x, y] = SHELL["crack"] + (255,)
        for x in range(7, 9):
            px[x, 7] = SHELL["bill"] + (255,)
        px[7, 8] = SHELL["bill2"] + (255,)
    return img


def nest():
    """the forest floor of the scrape: dark humus, fallen conifer needles in short strokes, a little moss"""
    from PIL import Image
    rnd = random.Random(17)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 5 + y * 3 + (x * y) % 4) % 9
            c = FLOOR_PAL["f0"] if h in (0, 4) else FLOOR_PAL["f2"] if h == 7 else FLOOR_PAL["f1"]
            px[x, y] = c + (255,)
    for _ in range(14):                     # needles: strokes of 3 pixels, slanting either way
        x, y = rnd.randrange(13), rnd.randrange(13)
        d = rnd.choice((1, -1))
        col = FLOOR_PAL["n1"] if rnd.random() < 0.4 else FLOOR_PAL["n0"]
        for i in range(3):
            yy = y + i if d > 0 else y + 2 - i
            px[x + i, yy] = col + (255,)
    for x, y in ((2, 12), (3, 12), (12, 2), (13, 3), (13, 2)):
        px[x, y] = FLOOR_PAL["moss"] + (255,)
    return img


def root():
    """bark of the roots: long fibres along the root, dark grooves"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (y * 3 + (x // 4) * 5) % 7
            c = ROOT["r0"] if h == 0 else ROOT["r2"] if h == 4 else ROOT["r1"]
            px[x, y] = c + (255,)
    return img


RING = [(8.0 + 3.6 * math.cos(a), 8.0 + 3.6 * math.sin(a)) for a in (0.2, 1.45, 2.7, 3.95, 5.2)]
HATCH = 2
FLOOR = 0.5
ROUND = [(0.0, 0.6, 1.0), (0.6, 2.6, 1.4), (2.6, 3.2, 1.0)]     # nearly round (Hypacrosaurus, ~20 cm)


def _egg(cx, cz, sink, tex="#egg"):
    els = []
    for y0, y1, hw in ROUND:
        a, b = FLOOR + y0 - sink, FLOOR + y1 - sink
        if b <= FLOOR:
            continue
        a = max(a, FLOOR)
        frm, to = [cx - hw, a, cz - hw], [cx + hw, b, cz + hw]
        els.append({"from": frm, "to": to, "faces": _faces(tex, frm[0], to[0], frm[2], to[2], a, b, top=True)})
    return els


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    root_tex = f"terrassic:block/{sid}_nest_root"
    els = []

    def box(frm, to, t, bottom=False):
        els.append({"from": frm, "to": to, "faces": _faces(t, frm[0], to[0], frm[2], to[2], frm[1], to[1], bottom=bottom)})
    box([0.5, 0, 0.5], [15.5, FLOOR, 15.5], "#nest", bottom=True)
    # two roots arching in from the sides, and a fallen twig
    box([0.0, FLOOR, 1.0], [5.0, 2.0, 2.5], "#root")
    box([5.0, FLOOR, 1.5], [9.0, 1.4, 2.7], "#root")
    box([13.5, FLOOR, 7.0], [15.0, 2.2, 15.5], "#root")
    box([12.8, FLOOR, 4.0], [14.2, 1.4, 7.0], "#root")
    box([2.0, FLOOR, 13.2], [8.0, 1.0, 13.8], "#root")
    for k, (cx, cz) in enumerate(RING):
        els.extend(_egg(cx, cz, 0.5 if k != HATCH else 0.2))
    # the needle cover heaped over the lower halves of the eggs: low drifts between them
    for frm, to in (([4.5, FLOOR, 4.5], [11.5, 1.6, 11.5]), ([2.5, FLOOR, 6.0], [5.0, 1.2, 10.0]),
                    ([10.5, FLOOR, 3.0], [12.5, 1.3, 6.5])):
        box(frm, to, "#nest")
    if stage >= 2:
        cx, cz = RING[HATCH]
        top = FLOOR + ROUND[-1][1] - 0.2
        f = {k: {"uv": [7, 7, 9, 8], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
        els.append({"from": [cx - 0.6, top - 0.4, cz - 1.8], "to": [cx + 0.6, top + 0.3, cz - 0.4], "faces": f})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "root": root_tex, "particle": nest_tex},
            "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 2.0, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (24, 20, 14), "k": (84, 72, 46), "K": (110, 96, 58), "g": (74, 84, 52), "h": (68, 56, 48),
              "H": (94, 76, 64), "f": (76, 90, 58), "F": (102, 116, 76), "b": (188, 180, 156), "B": (220, 214, 194)}
SADDLE_ART = [
    "................",
    "................",
    "................",
    "......oo........",
    ".....oBbo.......",
    ".....obo........",
    "...oohHHHHhoo...",
    "..okKkKkKkKkKo..",
    ".okgggggggggggko",
    ".oKkKkKkKkKkKko.",
    "..offfFfFfFfFo..",
    "..of.F.f.F.f.o..",
    "...o.f...F.o....",
    "................",
    "................",
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


CUSTOM_EGGS = {"corythosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"corythosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "corythosaurus_nest.png"))
    save_png(root(), os.path.join(TEX, "block", "corythosaurus_nest_root.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "corythosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
