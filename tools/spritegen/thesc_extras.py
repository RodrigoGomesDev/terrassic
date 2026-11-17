"""The Thescelosaurus' own egg art and nest (1.11.0, its study docs/estudos/15_HERBIVOROS_1_11.md, approved by Rodrigo on
10/11/2026).

Egg (block terrassic:thescelosaurus_egg, 3 hatch stages): no Thescelosaurus egg is known. The study's proposal
(SPECULATIVE): at the end of its burrow (itself a hypothesis, Button & Zanno 2023, after Oryctodromeus), or in a shallow
scrape between roots at the river bank, a ring of 4 to 6 ELONGATED eggs standing on end, half buried with the tip up,
creme-olive with dark freckles; the little heap of dug earth at the mouth gives the nest away. So: a floor of loose
dug earth, a heap of earth on one side (the spoil of the burrow), five tall eggs standing in a ring, each sunk to half
its height, creme-olive freckled in the parents' fern shades (no round eggs, no needles, no roots: those are the
Corythosaurus'). At stage 2 the egg nearest the heap is split at the top and the calf's snout pokes up.

usage: python3 -B tools/spritegen/thesc_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import math
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (206, 202, 160), "light": (222, 220, 182), "speck": (70, 84, 50), "speck2": (112, 124, 80),
         "earth": (96, 72, 48), "crack": (60, 56, 40), "snout": (70, 92, 56), "snout2": (40, 54, 32)}
EARTH = {"e0": (72, 52, 34), "e1": (94, 70, 46), "e2": (116, 88, 58), "e3": (138, 108, 72), "c0": (60, 66, 40)}


def shell(stage):
    """a creme-olive shell freckled in fern green, dug earth stuck on the lower part"""
    from PIL import Image
    rnd = random.Random(61)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 5 + y * 9 + (x * y) % 5) % 11
            px[x, y] = (SHELL["light"] if h == 0 else SHELL["base"]) + (255,)
    for _ in range(22):
        x, y = rnd.randrange(16), rnd.randrange(16)
        px[x, y] = (SHELL["speck"] if rnd.random() < 0.45 else SHELL["speck2"]) + (255,)
    for x in range(16):
        for y in range(13, 16):
            if (x * 3 + y) % 4:
                px[x, y] = SHELL["earth"] + (255,)
    if stage >= 2:
        for x, y in ((5, 2), (6, 3), (7, 2), (8, 3), (9, 2), (10, 3)):
            px[x, y] = SHELL["crack"] + (255,)
        for x in range(6, 10):
            px[x, 1] = SHELL["snout"] + (255,)
        px[7, 0] = SHELL["snout2"] + (255,)
    return img


def nest():
    """loose dug earth: lumps of two to three pixels in four browns, a little green litter"""
    from PIL import Image
    rnd = random.Random(29)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            lump = ((x // 2) * 7 + (y // 3) * 5 + ((x // 2) * (y // 3)) % 3) % 7
            c = EARTH["e0"] if lump == 0 else EARTH["e2"] if lump in (3, 5) else EARTH["e3"] if lump == 6 else EARTH["e1"]
            px[x, y] = c + (255,)
    for _ in range(6):
        x, y = rnd.randrange(15), rnd.randrange(16)
        px[x, y] = EARTH["c0"] + (255,)
    return img


RING = [(8.0 + 3.8 * math.cos(a), 8.0 + 3.8 * math.sin(a)) for a in (0.4, 1.65, 2.9, 4.15, 5.4)]
HATCH = 0
FLOOR = 0.5
TALL = [(0.0, 1.0, 0.9), (1.0, 4.4, 1.3), (4.4, 5.6, 0.9)]     # elongated, standing on end


def _egg(cx, cz, sink, tex="#egg"):
    els = []
    for y0, y1, hw in TALL:
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
    els = []

    def box(frm, to, t, bottom=False):
        els.append({"from": frm, "to": to, "faces": _faces(t, frm[0], to[0], frm[2], to[2], frm[1], to[1], bottom=bottom)})
    box([0.5, 0, 0.5], [15.5, FLOOR, 15.5], "#nest", bottom=True)
    # the spoil heap of the burrow on one side, in three steps
    box([10.5, FLOOR, 10.5], [15.5, 2.0, 15.5], "#nest")
    box([12.0, 2.0, 12.0], [15.5, 3.2, 15.5], "#nest")
    box([13.5, 3.2, 13.5], [15.5, 4.0, 15.5], "#nest")
    for k, (cx, cz) in enumerate(RING):
        els.extend(_egg(cx, cz, 2.6 if k != HATCH else 2.2))
    # loose earth heaped round the eggs' feet
    for frm, to in (([5.0, FLOOR, 5.0], [11.0, 1.4, 11.0]), ([2.0, FLOOR, 6.0], [4.5, 1.0, 10.5])):
        box(frm, to, "#nest")
    if stage >= 2:
        cx, cz = RING[HATCH]
        top = FLOOR + TALL[-1][1] - 2.2
        f = {k: {"uv": [6, 0, 10, 2], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
        els.append({"from": [cx - 0.6, top, cz - 0.6], "to": [cx + 0.6, top + 1.4, cz + 0.6], "faces": f})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": nest_tex},
            "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1.5, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


CUSTOM_EGGS = {"thescelosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"thescelosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "thescelosaurus_nest.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
