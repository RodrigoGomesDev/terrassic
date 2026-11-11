"""The Albertosaurus' own saddle art (1.10.1, 08/11/2026).

Saddle (item terrassic:albertosaurus_saddle): 16x16, drawn like the other species saddles (rex_extras,
dasple_extras) so they read as one family, but its own, the parts of the saddle bone of its model: the light racing
saddle of the runner, a low seat with a small pommel and a low cantle on a thin felt pad of its fir-green skin, short
flaps, and a bone stirrup.

Egg (block terrassic:albertosaurus_egg, 3 hatch stages, 1.11): the study's nest (docs/estudos/13, "Ninho", speculative):
at the edge of the conifer wood, under a litter of needles. Here the needles are raked into a CRESCENT bank, high at the
back and open in front, with fallen cones and a broken green sprig; five long eggs lie in a FAN in the hollow, the
blunt ends together at the back, a pale grey-green shell with dark brown speckles and blotches thick at the blunt end
(theropod eggs could be pigmented, Wiemann et al. 2018; a wood-edge nester hides its eggs by colour in the litter).
Stage 0: the eggs are under the needles, only their backs show; stage 1: the needles pushed off; stage 2: one egg
cracked, the chick's slim grey-green snout with its dark eye stripe out. Kept apart from the other clutches: the
Pachycephalosaurus' soft white eggs lie among roots, the Gallimimus' stone-grey ring on gravel, the Dakotaraptor's
blue-green ring under a log; only this one is a fan in a crescent of needles.

usage: python3 -B tools/spritegen/alberto_extras.py   (sprites.py also calls main())
"""
import math
import os
import random

from rex_extras import TEX
from nestkit import lying_egg, mapped, model, paint, shade, yrot, zoned

SADDLE_PAL = {
    "o": (28, 22, 16),     # outline
    "d": (44, 33, 22),     # dark leather
    "l": (106, 82, 54),    # tan leather
    "h": (134, 106, 70),   # leather highlight
    "p": (77, 90, 76),     # the felt pad (its own fir green)
    "P": (102, 116, 95),   # pad light
    "q": (52, 64, 54),     # pad shade
    "b": (185, 170, 136),  # bone stirrup
    "B": (221, 208, 176),  # bone light
}
SADDLE_ART = [
    "................",
    "................",
    "................",
    "...oo...........",
    "..ohho......oo..",
    "..olldoooooohlo.",
    "..ollhhhhhhhldo.",
    "...oddlllllddo..",
    "..oooddddddooo..",
    ".oPPPPPPPPPPPPo.",
    ".opPpqpPpqpPpqo.",
    "..oqpqo.oqpqo...",
    "...oo..odo.oo...",
    ".......odo......",
    "......oBbBo.....",
    "......oo.oo.....",
]


def saddle_sprite():
    from PIL import Image  # lazy, like the other extras
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y, row in enumerate(SADDLE_ART):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = SADDLE_PAL[ch] + (255,)
    return img


# ------------------------------------------------------------------ egg and nest (1.11)
SHELL = {"base": (176, 184, 160), "light": (194, 200, 178), "shade": (156, 164, 142), "speck": (82, 60, 42),
         "blot": (112, 82, 56), "crack": (52, 46, 38), "hole": (26, 24, 20)}
LITTER = {"hum": (78, 56, 38), "n0": (96, 64, 40), "n1": (114, 76, 46), "n2": (130, 90, 56), "g": (84, 98, 62)}
PROP = {"c0": (88, 58, 36), "c1": (118, 82, 48), "c2": (150, 112, 66), "s0": (46, 74, 46), "s1": (66, 98, 60),
        "s2": (88, 120, 74), "tw": (96, 70, 46), "k0": (70, 88, 76), "k1": (92, 112, 98), "k2": (120, 138, 122),
        "eye": (20, 22, 18), "stripe": (44, 56, 48), "tooth": (228, 220, 198), "b0": (72, 54, 40), "b1": (96, 72, 52)}


def shell(stage):
    """pale grey-green, speckled dark brown, the blotches thick at the blunt end (the top rows)"""
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(1201)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 5 + y * 3 + (x * y) % 4) % 9
            c = SHELL["light"] if h == 0 else SHELL["shade"] if h in (4, 7) else SHELL["base"]
            paint(px, x, y, shade(c, 1.05 - 0.12 * y / 15.0))
    for _ in range(26):
        x, y = rnd.randrange(16), int(rnd.random() ** 1.8 * 16)
        paint(px, x, y, SHELL["speck"])
    for _ in range(5):
        x, y = rnd.randrange(15), int(rnd.random() ** 2 * 8)
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            paint(px, x + dx, y + dy, SHELL["blot"])
    if stage >= 1:
        for x, y in ((5, 8), (6, 7), (7, 8), (8, 7), (9, 8), (10, 7)):
            paint(px, x, y, SHELL["crack"])
    if stage >= 2:
        for x, y in ((7, 7), (8, 8)):
            paint(px, x, y, SHELL["hole"])
    return img


def nest():
    """conifer needle litter: rust needles in short strokes over dark humus, a few fresh green ones"""
    from PIL import Image
    rnd = random.Random(1202)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            paint(px, x, y, LITTER["hum"])
    for _ in range(46):
        x, y = rnd.randrange(16), rnd.randrange(16)
        dx, dy = rnd.choice(((1, 0), (0, 1), (1, 1), (1, -1)))
        col = LITTER[rnd.choice(("n0", "n1", "n1", "n2"))] if rnd.random() > 0.08 else LITTER["g"]
        for i in range(3):
            paint(px, (x + dx * i) % 16, (y + dy * i) % 16, col)
    return img


def prop():
    """zones: a cone's scales (0,0,8,8), a green sprig (8,0,16,8), the chick's snout (0,8,8,16), bark (8,8,16,16)"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(8):
        for x in range(8):
            d = (x + y) % 4 == 0 or (x - y) % 4 == 0
            paint(px, x, y, PROP["c0"] if d else PROP["c2"] if (x + y) % 4 == 2 and y % 2 == 0 else PROP["c1"])
    for y in range(8):
        for x in range(8, 16):
            c = PROP["tw"] if y in (3, 4) else PROP["s2"] if (x + y) % 3 == 0 else PROP["s1"] if (x - y) % 2 else PROP["s0"]
            paint(px, x, y, c)
    for y in range(8, 16):
        for x in range(8):
            paint(px, x, y, PROP["k2"] if y > 13 else PROP["k1"] if (x * 3 + y) % 4 else PROP["k0"])
    for x in range(8):
        paint(px, x, 10, PROP["stripe"])
    paint(px, 2, 10, PROP["eye"]); paint(px, 5, 10, PROP["eye"]); paint(px, 3, 8, PROP["tooth"])
    for y in range(8, 16):
        for x in range(8, 16):
            paint(px, x, y, PROP["b1"] if (x + y // 3) % 3 else PROP["b0"])
    return img


BASE = 0.7
L_, W_ = 5.0, 2.2
PIVOT = (8.0, 2.8)
FAN = [-45.0, -22.5, 0.0, 22.5, 45.0]
EGGS = [(PIVOT[0] + 5.9 * math.sin(math.radians(a)), PIVOT[1] + 5.9 * math.cos(math.radians(a)), a) for a in FAN]
HATCH = 3
CONE, SPRIG, CHICK, BARK = (0, 0, 8, 8), (8, 0, 16, 8), (0, 8, 8, 16), (8, 8, 16, 16)


def _cone(x, y, z, angle):
    """a fallen cone lying on its side, its point towards +z before turning"""
    r = yrot(x, y, z, angle)
    return [zoned([x - 0.9, y, z - 1.4], [x + 0.9, y + 1.8, z + 0.8], CONE, rot=r),
            zoned([x - 0.6, y + 0.3, z + 0.8], [x + 0.6, y + 1.5, z + 1.8], CONE, rot=r),
            zoned([x - 0.2, y + 0.7, z - 2.0], [x + 0.2, y + 1.1, z - 1.4], BARK, rot=r)]


def egg_model(sid, stage):
    els = [mapped([0.5, 0, 0.5], [15.5, BASE, 15.5], bottom=True)]
    # the crescent bank of raked needles: high at the back, tapering along the sides, open in front
    for frm, to in (([0.8, BASE, 0.8], [15.2, 2.8, 3.4]), ([2.2, 2.8, 1.2], [13.8, 3.7, 2.9]),
                    ([0.8, BASE, 3.4], [3.0, 2.3, 8.8]), ([0.8, BASE, 8.8], [2.4, 1.5, 12.6]),
                    ([13.0, BASE, 3.4], [15.2, 2.3, 8.8]), ([13.6, BASE, 8.8], [15.2, 1.5, 12.6])):
        els.append(mapped(frm, to))
    els += _cone(1.9, 2.3, 6.0, 22.5)
    els += _cone(11.8, BASE, 13.6, -45.0)
    els.append(zoned([3.0, BASE, 12.6], [9.4, BASE + 0.8, 14.0], SPRIG, rot=yrot(6.2, BASE, 13.3, 22.5)))
    sink = 1.5 if stage == 0 else 0.4
    for k, (cx, cz, a) in enumerate(EGGS):
        els += lying_egg(cx, cz, L_, W_, BASE, sink - (0.2 if k == HATCH and stage >= 2 else 0.0), a)
    if stage == 0:
        # needles drawn over the fan: two low drifts across it
        els.append(mapped([3.4, BASE, 5.6], [12.6, BASE + 0.9, 9.0]))
        els.append(mapped([5.0, BASE, 9.0], [11.0, BASE + 0.6, 11.6]))
    if stage >= 2:
        cx, cz, a = EGGS[HATCH]
        top = BASE - (sink - 0.2) + W_
        els.append(zoned([cx - 0.6, top - 0.5, cz + 0.8], [cx + 0.6, top + 0.5, cz + 2.8], CHICK,
                         rot=yrot(cx, BASE, cz, a)))
    return model({"egg": f"terrassic:block/{sid}_egg_{stage}", "nest": f"terrassic:block/{sid}_nest",
                  "prop": f"terrassic:block/{sid}_nest_prop"}, els)


CUSTOM_EGGS = {"albertosaurus": egg_model}


def main():
    from sprites import save_png
    save_png(saddle_sprite(), os.path.join(TEX, "item", "albertosaurus_saddle.png"))
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"albertosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "albertosaurus_nest.png"))
    save_png(prop(), os.path.join(TEX, "block", "albertosaurus_nest_prop.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
