"""The Carcharodontosaurus' own saddle art (1.10.1, 08/11/2026).

Saddle (item terrassic:carcharodontosaurus_saddle): 16x16, drawn like the other species saddles (rex_extras,
dasple_extras, alberto_extras) so they read as one family, but its own, the parts of the saddle bone of its model: the
river-plain saddle, a deep hide seat with a HIGH POMMEL to brace on when it bursts out of the ambush, a woven blanket of
undyed wool with a dark border, a rope girth and a bone stirrup.

Egg (block terrassic:carcharodontosaurus_egg, 3 hatch stages, 1.11): the study's nest (docs/estudos/13, "Ninho",
speculative): a MOUND of wet grey sand and mangrove debris at the edge of the Kem Kem channels, the clutch buried in its
top like the eggs of the big theropods that were covered over. Mangrove things on and round it: the pencil air roots
(pneumatophores) standing out of the mud, long seedlings (propagules) lying on the sand or stuck upright in the mound,
and a few leathery leaves. Five eggs, nearly ROUND and smooth (the only allosauroid clutch known, Lourinhanosaurus, has
rounder smooth eggs than other theropods), a pale pinkish buff with fine mauve-brown speckles. Stage 0: the mound
closed, only the crowns of the eggs show through the sand; stage 1: the mother has dug a crater into the top and the
eggs lie in it; stage 2: one cracked, the chick's deep snout with the dark mask behind the eye out. Kept apart from
the other clutches: the Giganotosaurus' round eggs are pale blue-grey in cracked mud, the Deinosuchus' white eggs in a
beach mound with shells, the Spinosaurus' long eggs on a sandbar with water; only this one has the mangrove.

usage: python3 -B tools/spritegen/carcharo_extras.py   (sprites.py also calls main())
"""
import os
import random

from rex_extras import TEX
from nestkit import ball_egg, mapped, model, paint, shade, yrot, zoned

SADDLE_PAL = {
    "o": (30, 22, 17),     # outline
    "d": (70, 48, 31),     # dark leather
    "l": (125, 92, 58),    # leather
    "h": (151, 116, 75),   # leather highlight
    "p": (149, 134, 112),  # the woven wool blanket
    "P": (179, 165, 140),  # blanket light
    "q": (90, 60, 52),     # the blanket's dark woven border
    "r": (141, 122, 86),   # rope
    "b": (185, 170, 136),  # bone stirrup
    "B": (221, 208, 176),  # bone light
}
SADDLE_ART = [
    "................",
    "................",
    "...oo...........",
    "..ohho..........",
    "..ohlo.......oo.",
    "..olldoooooo.olo",
    "..ollhhhhhhhhldo",
    "...oddlllllllddo",
    "..oooddddddddoo.",
    ".oqqqqqqqqqqqqqo",
    ".oqPpPpPpPpPpPqo",
    ".oqpPpPpPpPpPpqo",
    "..oqqqqo.orooqqo",
    "........oro.....",
    ".......oBbBo....",
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


# the bleeding effect's icon (18x18, textures/mob_effect/bleeding.png): a drop of blood falling from a serrated cut
BLEED_PAL = {
    "o": (46, 10, 12),     # outline
    "r": (138, 24, 26),    # blood
    "R": (184, 44, 40),    # blood light
    "w": (232, 190, 176),  # glint
    "c": (92, 16, 18),     # the cut
}
BLEED_ART = [
    "..................",
    "..oo.oo.oo.oo.oo..",
    ".ocrocrocrocrocro.",
    "..oo.oo.oo.oo.oo..",
    "........o.........",
    ".......oro........",
    ".......oro........",
    "......orrro.......",
    ".....orRrrro......",
    "....orRRrrrro.....",
    "....orwRrrrro.....",
    "...orRwRrrrrro....",
    "...orRRrrrrrro....",
    "...orrrrrrrrco....",
    "....orrrrrrco.....",
    ".....orrrrco......",
    "......ooooo.......",
    "..................",
]


def bleeding_icon():
    from PIL import Image
    img = Image.new("RGBA", (18, 18))
    px = img.load()
    for y, row in enumerate(BLEED_ART):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = BLEED_PAL[ch] + (255,)
    return img


# ------------------------------------------------------------------ egg and nest (1.11)
SHELL = {"base": (220, 202, 192), "light": (234, 220, 210), "shade": (204, 184, 176), "speck": (138, 100, 104),
         "speck2": (170, 132, 128), "crack": (90, 70, 66), "hole": (34, 26, 24)}
SAND = {"s0": (112, 100, 84), "s1": (126, 114, 96), "s2": (140, 128, 108), "grain": (164, 152, 128),
        "fleck": (78, 66, 52)}
PROP = {"p0": (64, 84, 44), "p1": (84, 104, 54), "p2": (110, 92, 56), "p3": (88, 70, 44),
        "r0": (78, 70, 60), "r1": (98, 88, 74), "r2": (118, 108, 92),
        "l0": (44, 66, 40), "l1": (58, 84, 48), "l2": (80, 104, 62),
        "k0": (150, 116, 108), "k1": (170, 136, 124), "mask": (44, 34, 34), "eye": (18, 14, 14), "tooth": (230, 222, 204)}


def shell(stage):
    """pale pinkish buff, smooth, finely speckled mauve-brown"""
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(1301)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 3 + y * 7 + (x * y) % 5) % 11
            c = SHELL["light"] if h == 0 else SHELL["shade"] if h in (5, 8) else SHELL["base"]
            paint(px, x, y, shade(c, 1.04 - 0.12 * y / 15.0))
    for _ in range(20):
        paint(px, rnd.randrange(16), rnd.randrange(16), SHELL["speck"] if rnd.random() < 0.6 else SHELL["speck2"])
    if stage >= 1:
        for x, y in ((5, 6), (6, 5), (7, 6), (8, 6), (9, 5), (10, 6)):
            paint(px, x, y, SHELL["crack"])
    if stage >= 2:
        for x, y in ((7, 5), (8, 5)):
            paint(px, x, y, SHELL["hole"])
    return img


def nest():
    """the wet grey-brown sand of the channel edge, paler grains and dark bits of rotting mangrove"""
    from PIL import Image
    rnd = random.Random(1302)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = ((x // 2) * 5 + (y // 2) * 3 + x % 2) % 7
            paint(px, x, y, SAND["s2"] if h == 0 else SAND["s0"] if h in (3, 5) else SAND["s1"])
    for _ in range(12):
        paint(px, rnd.randrange(16), rnd.randrange(16), SAND["grain"])
    for _ in range(7):
        x, y = rnd.randrange(15), rnd.randrange(16)
        paint(px, x, y, SAND["fleck"]); paint(px, x + 1, y, SAND["fleck"])
    return img


def prop():
    """zones: a propagule, green above and brown below (0,0,4,16); root bark (4,0,8,16); a leathery mangrove leaf
    (8,0,16,8); the chick's snout with its dark mask (8,8,16,16)"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(4):
            c = (PROP["p1"] if x in (1, 2) else PROP["p0"]) if y < 10 else (PROP["p2"] if x in (1, 2) else PROP["p3"])
            paint(px, x, y, c)
        for x in range(4, 8):
            paint(px, x, y, PROP["r2"] if (y + x) % 5 == 0 else PROP["r1"] if x in (5, 6) else PROP["r0"])
    for y in range(8):
        for x in range(8, 16):
            c = PROP["l2"] if x in (11, 12) else PROP["l0"] if x in (8, 15) else PROP["l1"]
            paint(px, x, y, c)
    for y in range(8, 16):
        for x in range(8, 16):
            paint(px, x, y, PROP["k1"] if (x + y) % 3 else PROP["k0"])
    for x in range(8, 16):
        paint(px, x, 10, PROP["mask"])
    paint(px, 10, 10, PROP["eye"]); paint(px, 13, 10, PROP["eye"]); paint(px, 11, 8, PROP["tooth"])
    return img


PROPAGULE, ROOT, LEAF, CHICK = (0, 0, 4, 16), (4, 0, 8, 16), (8, 0, 16, 8), (8, 8, 16, 16)
FLOOR = 2.2   # the floor of the crater the eggs lie in
EGGS = [(6.0, 6.3), (9.9, 6.5), (5.9, 10.1), (9.8, 10.2), (7.9, 8.2)]
K = 0.66
HATCH = 3
# pencil air roots standing out of the mud round the mound: (x, z, height)
AIR_ROOTS = [(0.8, 3.0, 2.2), (1.0, 7.4, 1.6), (0.9, 12.6, 2.6), (3.6, 15.0, 1.8), (12.8, 15.1, 2.4),
             (15.0, 11.0, 1.7), (15.1, 5.4, 2.3), (13.4, 0.9, 1.5)]


def egg_model(sid, stage):
    els = [mapped([0.3, 0, 0.3], [15.7, 0.6, 15.7], bottom=True),
           mapped([1.4, 0.6, 1.4], [14.6, 1.4, 14.6]), mapped([2.6, 1.4, 2.6], [13.4, FLOOR, 13.4])]
    if stage == 0:
        # the closed mound: one more tier and a cap
        els += [mapped([3.6, FLOOR, 3.6], [12.4, 3.4, 12.4]), mapped([5.6, 3.4, 4.4], [9.0, 3.9, 6.0])]
        sink = 1.35
    else:
        # the crater dug into the top: a ring of the dug sand round the hollow
        els += [mapped([3.6, FLOOR, 3.6], [12.4, 3.3, 4.8]), mapped([3.6, FLOOR, 11.6], [12.4, 3.1, 12.4]),
                mapped([3.6, FLOOR, 4.8], [4.6, 3.2, 11.6]), mapped([11.4, FLOOR, 4.8], [12.4, 3.4, 11.6])]
        sink = 0.5
    for k, (cx, cz) in enumerate(EGGS):
        els += ball_egg(cx, cz, FLOOR, sink - (0.3 if k == HATCH and stage >= 2 else 0.0), K)
    for x, z, h in AIR_ROOTS:
        els.append(zoned([x - 0.3, 0.6, z - 0.3], [x + 0.3, 0.6 + h, z + 0.3], ROOT))
    # a propagule stuck upright in the mound, two lying on the sand, a drift root leaning on the side
    els.append(zoned([12.6, 1.4, 6.4], [13.2, 6.2, 7.0], PROPAGULE, rot={"origin": [12.9, 1.4, 6.7], "axis": "z", "angle": -22.5}))
    els.append(zoned([4.4, 0.6, 10.0], [5.0, 1.2, 15.4], PROPAGULE, rot=yrot(4.7, 0.6, 12.7, -22.5)))
    els.append(zoned([5.6, 0.6, 14.8], [11.2, 1.2, 15.4], PROPAGULE, rot=yrot(8.4, 0.6, 15.1, 22.5)))
    els.append(zoned([0.4, 0.6, 9.0], [1.4, 1.6, 14.2], ROOT, rot={"origin": [0.9, 0.6, 9.0], "axis": "x", "angle": 22.5}))
    for frm, to, ang in (([2.8, 1.45, 3.2], [6.0, 1.6, 5.0], 22.5), ([10.6, 0.65, 13.2], [13.8, 0.8, 15.0], -45.0)):
        els.append(zoned(frm, to, LEAF, rot=yrot((frm[0] + to[0]) / 2, frm[1], (frm[2] + to[2]) / 2, ang)))
    if stage >= 2:
        cx, cz = EGGS[HATCH]
        top = FLOOR - (sink - 0.3) + 4.1 * K
        els.append(zoned([cx - 0.7, top - 0.5, cz - 0.4], [cx + 0.7, top + 0.8, cz + 1.8], CHICK))
    return model({"egg": f"terrassic:block/{sid}_egg_{stage}", "nest": f"terrassic:block/{sid}_nest",
                  "prop": f"terrassic:block/{sid}_nest_prop"}, els, gui_y=1.5)


CUSTOM_EGGS = {"carcharodontosaurus": egg_model}


def main():
    from sprites import save_png
    save_png(saddle_sprite(), os.path.join(TEX, "item", "carcharodontosaurus_saddle.png"))
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"carcharodontosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "carcharodontosaurus_nest.png"))
    save_png(prop(), os.path.join(TEX, "block", "carcharodontosaurus_nest_prop.png"))
    os.makedirs(os.path.join(TEX, "mob_effect"), exist_ok=True)
    save_png(bleeding_icon(), os.path.join(TEX, "mob_effect", "bleeding.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
