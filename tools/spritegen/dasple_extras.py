"""The Daspletosaurus' own saddle art (1.10.1 pilot, 07/11/2026).

Saddle (item terrassic:daspletosaurus_saddle): 16x16, drawn like the other species saddles (rex_extras, carno_extras)
so they read as one family, but its own, the parts of the saddle bone of its model: a deep seat with a high cantle
(the slowest and toughest mount of the mid tyrannosaurs, a saddle you sit IN), on a hide pad of its own mahogany
skin, a bone toggle on the breast strap and an iron stirrup.

Egg (block terrassic:daspletosaurus_egg, 3 hatch stages, 1.11): the study's nest (docs/estudos/13, "Ninho", speculative):
a shallow pit dug into the bank of a forest river, the cut bank behind it showing its layers (dark humus, grey silt,
a band of river pebbles), the dug earth thrown up in a lip in front. Four LONG eggs, dark chocolate-plum, lying in two
pairs (theropods laid two at a time, two oviducts) set in a V, the shell raised in lengthwise lines of little nodes
(the "linearituberculate" shell of the big theropod eggs, Macroelongatoolithus). Stage 0: the mother has pulled broad
plane-tree and magnolia leaves over the clutch, the eggs barely show; stage 1: the leaves pushed onto the bank step
and the lip, the pairs in the open; stage 2: one egg split along its top, the chick's mahogany snout and pale egg
tooth out. Kept apart from the other clutches: the T. rex's pair stands in twigs, the Carnotaurus' rust pairs lie on
salt clay, the Triceratops' ovals sit under rotting leaves; only this one has a cut bank of strata.

usage: python3 -B tools/spritegen/dasple_extras.py   (sprites.py also calls main())
"""
import os
import random

from rex_extras import TEX
from nestkit import ball_egg, lying_egg, mapped, model, paint, shade, yrot, zoned  # noqa: F401

SADDLE_PAL = {
    "o": (30, 18, 14),     # outline
    "d": (46, 28, 18),     # dark oiled leather
    "l": (100, 67, 41),    # leather
    "h": (127, 88, 53),    # leather highlight
    "p": (93, 59, 63),     # the hide pad (its own mahogany skin)
    "P": (118, 82, 79),    # pad light
    "q": (71, 42, 48),     # pad shade
    "b": (185, 170, 136),  # bone toggle
    "B": (221, 208, 176),  # bone light
    "i": (120, 120, 116),  # iron
    "I": (164, 164, 156),  # iron light
}
SADDLE_ART = [
    "................",
    "............oo..",
    "...........ohho.",
    "..oo.......ohlo.",
    ".ohho.....ohldo.",
    ".olldoooooolldo.",
    ".olllhhhhhhlldo.",
    "..oddlllllllddo.",
    ".ooddddddddddooo",
    "oPPPPPPPPPPPPPPo",
    "opPpqpPpqpPpqpPo",
    "oqpqpqoBbooqpqo.",
    ".oqqo..obo.oqo..",
    "..oo...odo..o...",
    ".......oIiIo....",
    ".......oo.oo....",
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
SHELL = {"base": (76, 48, 44), "groove": (62, 38, 36), "ridge": (100, 68, 60), "node": (128, 94, 80),
         "crack": (30, 18, 16), "hole": (18, 10, 10), "chick": (118, 70, 66), "tooth": (226, 214, 190)}
LOAM = {"l0": (50, 38, 28), "l1": (64, 49, 34), "l2": (80, 62, 43), "peb": (122, 116, 104), "peb2": (98, 92, 82),
        "leaf": (70, 54, 32)}
BANK = {"hum": (48, 36, 27), "hum2": (60, 45, 32), "silt": (120, 108, 90), "silt2": (104, 93, 78),
        "silt3": (136, 124, 104), "peb": (148, 142, 128), "peb2": (112, 104, 90), "ochre": (150, 116, 70),
        "clay": (70, 64, 58), "root": (150, 128, 96)}
PROP = {"g0": (60, 86, 42), "g1": (78, 106, 52), "g2": (96, 124, 62), "vein": (140, 150, 86),
        "y0": (120, 86, 44), "y1": (150, 116, 58), "y2": (172, 138, 72), "yv": (196, 168, 104),
        "c0": (92, 52, 50), "c1": (118, 70, 66), "c2": (140, 92, 84), "eye": (24, 16, 14), "tooth": (226, 214, 190),
        "t0": (78, 60, 42), "t1": (100, 78, 54), "t2": (124, 98, 68)}


def shell(stage):
    """dark chocolate-plum, lengthwise lines of little nodes; darker low down"""
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            col = x % 3
            c = SHELL["ridge"] if col == 1 else SHELL["groove"] if col == 0 else SHELL["base"]
            if col == 1 and (y + x // 3) % 3 == 0:
                c = SHELL["node"]
            paint(px, x, y, shade(c, 1.06 - 0.16 * y / 15.0))
    if stage >= 1:
        for x, y in ((4, 6), (5, 7), (6, 7), (7, 6), (8, 7), (9, 7), (10, 6), (11, 7)):
            paint(px, x, y, SHELL["crack"])
    if stage >= 2:
        for x, y in ((5, 6), (6, 6), (8, 6), (9, 6), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8)):
            paint(px, x, y, SHELL["hole"])
        for x, y in ((7, 7), (8, 7)):
            paint(px, x, y, SHELL["chick"])
        paint(px, 9, 7, SHELL["tooth"])
    return img


def nest():
    """the forest loam of the bank top and the pit: dark clods, a few river pebbles, bits of old leaf"""
    from PIL import Image
    rnd = random.Random(1101)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = ((x // 2) * 7 + (y // 2) * 5 + (x * y) % 3) % 6
            paint(px, x, y, LOAM["l2"] if h == 0 else LOAM["l0"] if h in (3, 4) else LOAM["l1"])
    for _ in range(5):
        x, y = rnd.randrange(15), rnd.randrange(15)
        paint(px, x, y, LOAM["peb"]); paint(px, x + 1, y, LOAM["peb2"])
    for _ in range(7):
        paint(px, rnd.randrange(16), rnd.randrange(16), LOAM["leaf"])
    return img


def bank():
    """the cut bank seen from the side (row 16 - y): humus on top, laminated grey silt, a band of pebbles, wet clay"""
    from PIL import Image
    rnd = random.Random(1102)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            if y < 12:
                c = BANK["hum2"] if (x * 3 + y * 5) % 7 == 0 else BANK["hum"]
            elif y < 14:
                c = (BANK["silt3"] if y == 12 else BANK["silt2"]) if (x + y) % 5 == 0 else BANK["silt"]
            elif y == 14:
                c = BANK["peb2"]
            else:
                c = BANK["clay"]
            paint(px, x, y, c)
    for x in range(0, 16, 2):   # the pebble band: rounded stones, a few ochre
        paint(px, x + rnd.randrange(2), 14, BANK["ochre"] if rnd.random() < 0.25 else BANK["peb"])
    for x in (2, 9, 13):         # pale root hairs hanging out of the humus
        for y in range(10, 12 + rnd.randrange(2)):
            paint(px, x, y, BANK["root"])
    return img


def prop():
    """zones: a green broad leaf (0,0,8,8), a yellowed one (8,0,16,8), the chick's snout (0,8,8,16), drift twig
    bark (8,8,16,16)"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for ox, pal in ((0, ("g0", "g1", "g2", "vein")), (8, ("y0", "y1", "y2", "yv"))):
        for y in range(8):
            for x in range(8):
                c = PROP[pal[2]] if (x * 5 + y * 3) % 7 == 0 else PROP[pal[1]]
                if x in (0, 7):
                    c = PROP[pal[0]]                      # the rolled leaf edge
                if x in (3, 4) or (abs(x - 3.5) + 0.5 == (y % 4) + 0.5 and y % 4 != 0):
                    c = PROP[pal[3]] if x in (3, 4) else PROP[pal[0]]   # midrib and the side veins
                paint(px, ox + x, y, c)
    for y in range(8, 16):
        for x in range(8):
            paint(px, x, y, PROP["c2"] if (x * 3 + y) % 5 == 0 else PROP["c1"] if y < 13 else PROP["c0"])
    paint(px, 2, 10, PROP["eye"]); paint(px, 5, 10, PROP["eye"]); paint(px, 3, 8, PROP["tooth"])
    for y in range(8, 16):
        for x in range(8, 16):
            paint(px, x, y, PROP["t2"] if (y + x // 2) % 4 == 0 else PROP["t0"] if x % 3 == 0 else PROP["t1"])
    return img


BASE = 0.8
L_, W_ = 5.4, 2.3
# two pairs in a V, (centre x, centre z, angle)
EGGS = [(4.5, 9.6, 22.5), (6.8, 9.2, 22.5), (9.3, 9.2, -22.5), (11.6, 9.6, -22.5)]
HATCH = 2
LEAF, DEAD, CHICK, TWIG = (0, 0, 8, 8), (8, 0, 16, 8), (0, 8, 8, 16), (8, 8, 16, 16)


def _bank(frm, to):
    el = mapped(frm, to, "#bank")
    el["faces"]["up"]["texture"] = "#nest"
    return el


def egg_model(sid, stage):
    els = [mapped([0.5, 0, 0.5], [15.5, BASE, 15.5], bottom=True)]
    # the cut bank behind, a step down, the shoulders either side and the lip of thrown-out earth in front
    els += [_bank([0.5, BASE, 0.5], [15.5, 4.6, 3.4]), _bank([1.5, BASE, 3.4], [14.5, 2.6, 5.0]),
            _bank([0.5, BASE, 5.0], [2.6, 1.9, 12.0]), _bank([13.4, BASE, 5.0], [15.5, 1.6, 11.0]),
            mapped([3.0, BASE, 13.4], [13.0, 1.7, 15.3])]
    els.append(zoned([1.0, BASE, 12.6], [6.4, BASE + 0.6, 13.2], TWIG, rot=yrot(3.7, BASE, 12.9, -22.5)))
    sink = 1.35 if stage == 0 else 0.45
    for k, (cx, cz, a) in enumerate(EGGS):
        s = sink - (0.25 if k == HATCH and stage >= 2 else 0.0)
        els += lying_egg(cx, cz, L_, W_, BASE, s, a)
    if stage == 0:
        # broad leaves pulled over the clutch
        for frm, to, zone, ang in (([3.4, 0, 5.8], [8.6, 0, 13.2], LEAF, 22.5), ([8.4, 0, 6.0], [13.2, 0, 13.0], DEAD, -22.5),
                                   ([5.6, 0, 8.6], [10.4, 0, 14.8], LEAF, 0.0)):
            y = BASE + 1.05 + (0.18 if zone == DEAD else 0.0) + (0.36 if ang == 0 else 0.0)
            els.append(zoned([frm[0], y, frm[2]], [to[0], y + 0.2, to[2]], zone,
                             rot=yrot((frm[0] + to[0]) / 2, y, (frm[2] + to[2]) / 2, ang)))
    else:
        # the leaves pushed onto the bank step and the lip
        els.append(zoned([2.2, 2.6, 3.5], [7.6, 2.8, 5.0], LEAF))
        els.append(zoned([8.8, 1.7, 13.5], [13.6, 1.9, 15.2], DEAD, rot=yrot(11.2, 1.7, 14.3, 22.5)))
        els.append(zoned([10.0, 2.6, 3.6], [14.0, 2.8, 4.9], DEAD))
    if stage >= 2:
        cx, cz, a = EGGS[HATCH]
        top = BASE - (sink - 0.25) + W_
        els.append(zoned([cx - 0.8, top - 0.5, cz - 2.9], [cx + 0.8, top + 0.6, cz - 1.0], CHICK,
                         rot=yrot(cx, BASE, cz, a)))
    return model({"egg": f"terrassic:block/{sid}_egg_{stage}", "nest": f"terrassic:block/{sid}_nest",
                  "bank": f"terrassic:block/{sid}_nest_bank", "prop": f"terrassic:block/{sid}_nest_prop"}, els)


CUSTOM_EGGS = {"daspletosaurus": egg_model}


def main():
    from sprites import save_png
    save_png(saddle_sprite(), os.path.join(TEX, "item", "daspletosaurus_saddle.png"))
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"daspletosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "daspletosaurus_nest.png"))
    save_png(bank(), os.path.join(TEX, "block", "daspletosaurus_nest_bank.png"))
    save_png(prop(), os.path.join(TEX, "block", "daspletosaurus_nest_prop.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
