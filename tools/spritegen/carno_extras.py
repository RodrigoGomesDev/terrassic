"""The Carnotaurus' own egg and saddle art (2026-11-02, Rodrigo: every species its own items, "ovo e sela").

Egg (block terrassic:carnotaurus_egg, 3 hatch stages): six long eggs lying in pairs along a crescent, pressed into
the grey clay of a coastal mudflat crusted white with salt, and beside them the deep three-toed print of the mother.
Carnotaurus lived on the coastal plains and estuaries of the La Colonia Formation (Patagonia). Theropods laid two
eggs at a time (two oviducts), so the eggs lie in pairs, long and narrow; theropod eggs could be coloured by
protoporphyrin, so these are a dark rust with darker freckles, the colour of the animal. Abelisaurid eggs are
unknown; this is the closest real reference. Different from the other clutches: the T. rex's pair stands in a twig
nest, the Velociraptor's blue-green eggs stand in pale sand, the Protoceratops' soft eggs lie in a red sand mound.

Saddle (item terrassic:carnotaurus_saddle): 16x16, drawn like the T. rex saddle (rex_extras) so the saddles read as
one family, but the Carnotaurus' own, the parts of the saddle bone of its model: the pale sand blanket under a low
racing seat (it is the fastest of the big predators), a tall pommel to hold on through the charge, the crimson
band of its horn bases along the blanket, and an iron stirrup.

usage: python3 -B tools/spritegen/carno_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (122, 66, 44), "light": (146, 84, 56), "shade": (100, 52, 36), "freckle": (70, 36, 28),
         "freckle2": (160, 104, 70), "crack": (44, 26, 22), "hole": (26, 16, 14), "inner": (222, 206, 170),
         "chick": (150, 80, 52), "horn": (52, 40, 32)}
MUD = {"clay": (128, 128, 118), "clay2": (112, 112, 104), "clay3": (146, 144, 132), "salt": (224, 222, 210),
       "salt2": (196, 194, 182), "print": (84, 84, 78), "print2": (98, 98, 90), "shell": (214, 200, 178)}


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(71)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            k = 1.06 - 0.16 * (y / 15.0)        # lit from above, darker toward the clay
            c = SHELL["light"] if (x * 7 + y * 3) % 9 == 0 else SHELL["base"]
            px[x, y] = tuple(min(255, int(v * k)) for v in c) + (255,)
    for _ in range(18):   # dark freckles, a few pale ones, most at the blunt end
        x, y = rnd.randrange(16), int(rnd.random() ** 1.5 * 16)
        px[x, y] = (SHELL["freckle"] if rnd.random() < 0.75 else SHELL["freckle2"]) + (255,)
    if stage >= 1:   # a crack across the top
        for x, y in ((5, 5), (6, 6), (7, 6), (8, 5), (9, 6), (10, 7), (8, 4)):
            px[x, y] = SHELL["crack"] + (255,)
    if stage >= 2:   # a hole: the chick's snout with the two little horn knobs already showing, and the egg tooth
        for x, y in ((6, 5), (7, 5), (9, 5), (6, 7), (7, 7), (8, 7), (9, 7)):
            px[x, y] = SHELL["hole"] + (255,)
        for x, y in ((7, 6), (8, 6), (8, 5)):
            px[x, y] = SHELL["chick"] + (255,)
        px[7, 5] = SHELL["horn"] + (255,)
        px[9, 6] = SHELL["inner"] + (255,)
    return img


def nest():
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(17)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 3 + y * 7 + (x * y) % 4) % 8
            px[x, y] = (MUD["clay2"] if h == 0 else MUD["clay3"] if h == 5 else MUD["clay"]) + (255,)
    # the salt crust: white patches cracked into plates
    for cx, cy, r in ((3, 3, 2), (12, 4, 2), (11, 13, 2), (2, 12, 1)):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if 0 <= x < 16 and 0 <= y < 16 and (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 1:
                    px[x, y] = (MUD["salt"] if (x + y) % 3 else MUD["salt2"]) + (255,)
    for x, y in ((5, 8), (13, 9), (8, 14)):    # bits of clam shell washed up
        px[x, y] = MUD["shell"] + (255,)
    return img


def print_tex():
    """the mother's three-toed footprint pressed into the clay (its own small texture on the print element)"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = MUD["clay"] + (255,)
    toes = [[(7, 1), (7, 2), (7, 3), (7, 4), (8, 2), (8, 3), (8, 4), (8, 5)],
            [(3, 3), (4, 4), (4, 5), (5, 5), (5, 6), (6, 7)], [(12, 3), (11, 4), (11, 5), (10, 5), (10, 6), (9, 7)]]
    for toe in toes:
        for x, y in toe:
            px[x, y] = MUD["print"] + (255,)
    for x in range(5, 11):
        for y in range(7, 11):
            if (x - 7.5) ** 2 / 9 + (y - 8.5) ** 2 / 3 <= 1.2:
                px[x, y] = MUD["print"] + (255,)
    for x, y in ((6, 11), (9, 11), (7, 0), (2, 3), (13, 3)):
        px[x, y] = MUD["print2"] + (255,)
    return img


# a long egg lying down, rounded (along from, along to, half width, height): about 2.6 times as long as wide
EGG_SLICES = [(0.0, 0.7, 0.7, 1.4), (0.7, 1.5, 1.1, 2.2), (1.5, 4.5, 1.4, 2.8), (4.5, 5.3, 1.1, 2.2), (5.3, 6.0, 0.7, 1.4)]
# three pairs along a crescent (centre x, z, length axis, y rotation, sink)
EGGS = [(2.8, 8.4, "z", 22.5, 1.0), (5.6, 8.0, "z", 22.5, 1.2),          # the left pair
        (8.0, 3.0, "x", 0.0, 1.1), (8.2, 5.8, "x", 0.0, 1.0),               # the pair at the back
        (10.6, 8.0, "z", -22.5, 1.0), (13.4, 8.4, "z", -22.5, 1.2)]         # the right pair
TOP = 1.0


def _egg(cx, cz, axis, angle, sink):
    els = []
    for a0, a1, hw, h in EGG_SLICES:
        a0, a1 = a0 - 3.0, a1 - 3.0
        for w, hh in ((hw, h * 0.72), (hw * 0.72, h)):
            y0, y1 = max(0.5, TOP - sink + 0.6), TOP - sink + 0.6 + hh
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
    els = []
    # the mudflat: a slab of clay (the footprint's patch in front is its own piece, so the print does not
    # sit on top of the clay and flicker), a low lip of pushed-up mud along the back
    for frm, to in (([0, 0, 1], [16, TOP, 11]), ([1, 0, 0], [15, TOP, 1]), ([0, 0, 11], [5, TOP, 15]),
                    ([11, 0, 11], [16, TOP, 15]), ([1, 0, 15], [15, TOP, 16]), ([1, TOP, 0.5], [15, 1.6, 2]),
                    ([0.5, TOP, 2], [2, 1.4, 6]), ([14, TOP, 2], [15.5, 1.4, 6])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1],
                                                            bottom=frm[1] == 0)})
    els.append({"from": [5, 0, 11], "to": [11, TOP, 15],
                "faces": {"up": {"uv": [3, 1, 13, 11], "texture": "#print"}, "down": {"uv": [5, 1, 11, 5], "texture": "#nest"},
                          "south": {"uv": [5, 15, 11, 16], "texture": "#nest"}}})
    for e in EGGS:
        els += _egg(*e)
    return {"parent": "block/block", "textures": {"egg": tex, "nest": f"terrassic:block/{sid}_nest",
                                                  "print": f"terrassic:block/{sid}_print", "particle": tex},
            "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1.5, 0], "scale": [0.95, 0.95, 0.95]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {
    "o": (34, 22, 18),     # outline
    "d": (70, 40, 28),     # dark leather
    "l": (104, 62, 40),    # leather
    "h": (138, 90, 58),    # leather highlight
    "s": (196, 170, 120),  # stitching
    "p": (206, 186, 146),  # sand blanket
    "P": (230, 214, 178),  # blanket light
    "q": (168, 146, 108),  # blanket shade
    "r": (147, 48, 45),    # crimson band (the horn bases)
    "R": (110, 31, 34),    # crimson dark
    "i": (110, 110, 106),  # iron
    "I": (163, 163, 155),  # iron light
}
SADDLE_ART = [
    "................",
    "..oo............",
    ".ohho...........",
    ".ohlo......ooo..",
    ".olldo....ohhdo.",
    ".ollldooooolldo.",
    "..oddlhhhhhlddo.",
    ".ooddlllllllddoo",
    "oPPPPPPPPPPPPPPo",
    "orRrRrRrRrRrRrRo",
    "oqpPpqpPpqpPpqpo",
    ".oqpqpoooopqpqo.",
    "..oqpo.odo.oqo..",
    "...oo..odo..o...",
    "......oIiIo.....",
    "......oo.oo.....",
]


def saddle_sprite():
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y, row in enumerate(SADDLE_ART):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = SADDLE_PAL[ch] + (255,)
    return img


CUSTOM_EGGS = {"carnotaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"carnotaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "carnotaurus_nest.png"))
    save_png(print_tex(), os.path.join(TEX, "block", "carnotaurus_print.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "carnotaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
