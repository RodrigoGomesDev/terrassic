"""The Majungasaurus' own saddle art (1.10.1, 08/11/2026).

Saddle (item terrassic:majungasaurus_saddle): 16x16, drawn like the other species saddles (rex_extras, dasple_extras,
alberto_extras, carcharo_extras) so they read as one family, but its own, the parts of the saddle bone of its model:
the brawler's saddle, a LOW hide seat with a rope grab loop at the front (for when it holds and shakes), a mat of
woven raffia palm fibre with two dyed red-brown stripes, a broad raffia girth and a short bone stirrup.

Egg (block terrassic:majungasaurus_egg, 3 hatch stages, 1.11): the study's nest (docs/estudos/13, "Ninho",
speculative): a shallow scrape in the DRY sand of a river margin in the Maevarano dry season, the red-ochre sand thrown
up in a low broken rim and the clutch covered with a thatch of DRY GRASS against the sun. Six eggs, medium long, laid
two at a time and lying side by side in two rows of three, a warm cream shell with dark brown scrawls (hairline
squiggles, not spots). Stage 0: only the heap of straw shows, a few straws standing out of the rim; stage 1: the mother
has dragged the thatch back onto the rim and the rows show; stage 2: one egg cracked, the chick's broad sage snout
with the first bump of its dome out. Kept apart from the other clutches: the Carnotaurus' rust pairs lie in a crescent
on salt clay, the Quetzalcoatlus' soft eggs in pale sand, the Therizinosaurus' under a red clay crust; only this one is
in rows under straw.

usage: python3 -B tools/spritegen/majunga_extras.py   (sprites.py also calls main())
"""
import os
import random

from rex_extras import TEX
from nestkit import lying_egg, mapped, model, paint, shade, yrot, zoned

SADDLE_PAL = {
    "o": (30, 22, 17),     # outline
    "d": (70, 48, 31),     # dark leather
    "l": (125, 92, 58),    # leather
    "h": (151, 116, 75),   # leather highlight
    "p": (179, 154, 98),   # the raffia mat
    "P": (204, 180, 124),  # raffia light
    "q": (122, 58, 36),    # the dyed red-brown stripe
    "r": (168, 142, 88),   # raffia rope
    "b": (185, 170, 136),  # bone stirrup
    "B": (221, 208, 176),  # bone light
}
SADDLE_ART = [
    "................",
    "................",
    "................",
    "...ooo..........",
    "..oro.o.........",
    "..oo.ro.........",
    "...ollooooooooo.",
    "...ohhhhhhhhhhlo",
    "..oddllllllllddo",
    ".oooooooooooooo.",
    ".oPpPpPpPpPpPpPo",
    ".oqqqqqqqqqqqqqo",
    ".opPpPpPpPpPpPpo",
    "..ooooooorroooo.",
    ".........oBbo...",
    ".........ooo....",
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
SHELL = {"base": (222, 206, 170), "light": (234, 222, 190), "shade": (204, 188, 152), "scrawl": (92, 60, 40),
         "scrawl2": (128, 92, 62), "crack": (74, 56, 40), "hole": (30, 22, 16)}
SAND = {"s0": (156, 114, 84), "s1": (170, 128, 96), "s2": (182, 142, 108), "grain": (198, 162, 128), "dark": (138, 98, 72)}
PROP = {"w0": (168, 146, 96), "w1": (190, 168, 112), "w2": (212, 192, 136), "w3": (146, 124, 80),
        "k0": (96, 116, 92), "k1": (116, 136, 108), "dome": (78, 66, 54), "eye": (20, 18, 14), "tooth": (232, 224, 204)}


def shell(stage):
    """warm cream with hairline scrawls of dark brown"""
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(1401)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 7 + y * 3 + (x * y) % 3) % 10
            c = SHELL["light"] if h == 0 else SHELL["shade"] if h in (4, 7) else SHELL["base"]
            paint(px, x, y, shade(c, 1.05 - 0.14 * y / 15.0))
    for _ in range(6):   # a scrawl: a short wandering hairline
        x, y = rnd.randrange(16), rnd.randrange(16)
        col = SHELL["scrawl"] if rnd.random() < 0.6 else SHELL["scrawl2"]
        for i in range(rnd.randint(3, 6)):
            paint(px, x % 16, y % 16, col)
            x += rnd.choice((1, 1, 0))
            y += rnd.choice((-1, 0, 1))
    if stage >= 1:
        for x, y in ((5, 8), (6, 7), (7, 7), (8, 8), (9, 8), (10, 7)):
            paint(px, x, y, SHELL["crack"])
    if stage >= 2:
        for x, y in ((7, 8), (8, 7)):
            paint(px, x, y, SHELL["hole"])
    return img


def nest():
    """dry red-ochre sand: calm, a few pale grains and darker crumbs"""
    from PIL import Image
    rnd = random.Random(1402)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = ((x // 2) * 3 + (y // 2) * 7 + y % 2) % 8
            paint(px, x, y, SAND["s2"] if h == 0 else SAND["s0"] if h in (3, 6) else SAND["s1"])
    for _ in range(12):
        paint(px, rnd.randrange(16), rnd.randrange(16), SAND["grain"])
    for _ in range(6):
        paint(px, rnd.randrange(16), rnd.randrange(16), SAND["dark"])
    return img


def prop():
    """zones: dry grass straws lengthwise (0,0,16,8), the chick's snout (0,8,8,16)"""
    from PIL import Image
    rnd = random.Random(1403)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for x in range(16):
        tone = rnd.choice(("w0", "w1", "w1", "w2", "w3"))
        for y in range(8):
            paint(px, x, y, PROP[tone] if (y * 3 + x * 7) % 11 else PROP["w3"])
    for y in range(8, 16):
        for x in range(8):
            paint(px, x, y, PROP["k1"] if (x + y) % 3 else PROP["k0"])
    paint(px, 3, 8, PROP["dome"]); paint(px, 4, 8, PROP["dome"])
    paint(px, 1, 10, PROP["eye"]); paint(px, 6, 10, PROP["eye"]); paint(px, 3, 13, PROP["tooth"])
    for y in range(8, 16):
        for x in range(8, 16):
            paint(px, x, y, PROP["w1"] if (x + y) % 2 else PROP["w0"])
    return img


BASE = 0.7
L_, W_ = 4.3, 2.3
# two rows of three, lying side by side (laid two at a time)
EGGS = [(x, z, 0.0) for z in (5.9, 10.3) for x in (5.0, 7.7, 10.4)]
HATCH = 4
STRAW, CHICK, BUNDLE = (0, 0, 16, 8), (0, 8, 8, 16), (8, 8, 16, 16)
# straws standing out of the rim: (x, z, height, lean axis, lean)
TUFTS = [(2.0, 2.4, 2.4, "x", 22.5), (2.6, 2.0, 1.8, "z", -22.5), (13.6, 13.4, 2.2, "x", -22.5),
         (14.0, 12.6, 1.6, "z", 22.5), (13.2, 2.0, 2.0, "z", 22.5), (2.4, 13.8, 1.8, "x", -22.5)]


def egg_model(sid, stage):
    els = [mapped([0.5, 0, 0.5], [15.5, BASE, 15.5], bottom=True)]
    # the low broken rim of thrown-out sand
    for frm, to in (([1.0, BASE, 1.0], [9.0, 1.7, 2.8]), ([10.2, BASE, 1.2], [15.0, 1.5, 2.8]),
                    ([1.0, BASE, 2.8], [2.8, 1.6, 9.6]), ([13.2, BASE, 2.8], [15.0, 1.8, 13.0]),
                    ([2.4, BASE, 13.0], [11.6, 1.5, 14.8]), ([1.2, BASE, 11.0], [2.6, 1.2, 13.0])):
        els.append(mapped(frm, to))
    for x, z, h, axis, ang in TUFTS:
        els.append(zoned([x - 0.2, 1.2, z - 0.2], [x + 0.2, 1.2 + h, z + 0.2], STRAW,
                         rot={"origin": [x, 1.2, z], "axis": axis, "angle": ang}))
    sink = 0.9 if stage == 0 else 0.45
    for k, (cx, cz, a) in enumerate(EGGS):
        els += lying_egg(cx, cz, L_, W_, BASE, sink - (0.2 if k == HATCH and stage >= 2 else 0.0), a)
    if stage == 0:
        # the thatch of dry grass over the scrape: layers laid crosswise, loose and untidy
        for frm, to, ang in (([2.8, 2.2, 3.4], [13.2, 2.5, 12.8], 0.0), ([3.6, 2.5, 3.0], [12.4, 2.8, 13.2], 22.5),
                             ([4.4, 2.8, 4.0], [11.6, 3.1, 12.0], -22.5), ([5.6, 3.1, 5.4], [10.4, 3.4, 10.6], 45.0)):
            els.append(zoned(frm, to, STRAW, rot=yrot((frm[0] + to[0]) / 2, frm[1], (frm[2] + to[2]) / 2, ang)))
    else:
        # the thatch dragged back onto the rim in a loose heap
        els.append(zoned([1.0, 1.7, 0.8], [10.0, 2.3, 3.0], STRAW))
        els.append(zoned([2.0, 2.3, 1.2], [8.0, 2.7, 2.6], STRAW, rot=yrot(5.0, 2.3, 1.9, 22.5)))
        els.append(zoned([0.9, 1.6, 3.0], [2.9, 2.1, 9.0], STRAW))
    if stage >= 2:
        cx, cz, a = EGGS[HATCH]
        top = BASE - (sink - 0.2) + W_
        els.append(zoned([cx - 0.8, top - 0.5, cz + 0.6], [cx + 0.8, top + 0.6, cz + 2.4], CHICK))
    return model({"egg": f"terrassic:block/{sid}_egg_{stage}", "nest": f"terrassic:block/{sid}_nest",
                  "prop": f"terrassic:block/{sid}_nest_prop"}, els)


CUSTOM_EGGS = {"majungasaurus": egg_model}


def main():
    from sprites import save_png
    save_png(saddle_sprite(), os.path.join(TEX, "item", "majungasaurus_saddle.png"))
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"majungasaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "majungasaurus_nest.png"))
    save_png(prop(), os.path.join(TEX, "block", "majungasaurus_nest_prop.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
