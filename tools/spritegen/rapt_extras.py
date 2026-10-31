"""The Velociraptor's own egg and harness art (2026-10-30, with the v3 model).

Egg (block terrassic:velociraptor_egg, 3 hatch stages): a clutch of six long eggs standing half buried in a shallow
scrape of desert sand with a raised rim, in pairs round the middle and leaning outward. Troodontid and oviraptorid
clutches were laid two at a time and stood upright in a ring, and maniraptoran eggs were coloured: the pigments
biliverdin and protoporphyrin made them blue-green (Wiemann et al. 2018, Nature). The shell here is pale blue-green
with brown speckles; stage 1 shows a crack, stage 2 a hole with the chick's snout and egg tooth. Velociraptor eggs
themselves are unknown; this is the closest real reference. The block model comes from egg_model()
(tools/javagen/gen_resources.py uses it for the species in CUSTOM_EGGS).

Harness (item terrassic:velociraptor_harness): not a saddle, a 20 kg animal carries nobody. A leather hunting vest that
wraps both flanks, a bone plate on the withers and an iron ring for a lead, the same parts as the "saddle" bone of
the model. It gives the raptor armour; it cannot be ridden.

usage: python3 -B tools/spritegen/rapt_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (150, 186, 172), "light": (176, 206, 192), "shade": (122, 156, 144), "speck": (107, 80, 56),
         "speck2": (127, 143, 120), "crack": (62, 74, 68), "hole": (29, 23, 20), "chick": (179, 143, 92),
         "chick2": (143, 108, 69), "tooth": (239, 230, 207)}
SAND = {"sand": (205, 178, 122), "sand2": (185, 154, 99), "sand3": (220, 195, 142), "rim": (168, 136, 90),
        "pebble": (120, 104, 84), "feather": (58, 50, 44), "feather2": (67, 101, 119)}


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(67)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            # smooth hard shell, lit from above, a little darker toward the sand
            k = 1.05 - 0.14 * (y / 15.0)
            c = SHELL["light"] if (x * 3 + y * 7) % 13 == 0 else SHELL["base"]
            px[x, y] = tuple(min(255, int(v * k)) for v in c) + (255,)
    for _ in range(14):   # speckles, denser at the blunt (top) end
        x, y = rnd.randrange(16), int(rnd.random() ** 1.8 * 16)
        px[x, y] = (SHELL["speck"] if rnd.random() < 0.7 else SHELL["speck2"]) + (255,)
    if stage >= 1:   # a crack across the top
        for x, y in ((5, 4), (6, 5), (7, 5), (8, 4), (9, 5), (10, 6), (7, 6)):
            px[x, y] = SHELL["crack"] + (255,)
    if stage >= 2:   # a hole: the chick's snout and its egg tooth
        for x, y in ((6, 4), (7, 4), (8, 5), (9, 4), (6, 6), (8, 6), (9, 6)):
            px[x, y] = SHELL["hole"] + (255,)
        for x, y in ((7, 5), (8, 5), (7, 6)):
            px[x, y] = SHELL["chick"] + (255,)
        px[8, 6] = SHELL["chick2"] + (255,)
        px[7, 4] = SHELL["tooth"] + (255,)
    return img


def nest():
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(23)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 5 + y * 11 + (x * y) % 7) % 9
            px[x, y] = (SAND["sand2"] if h == 0 else SAND["sand3"] if h == 5 else SAND["sand"]) + (255,)
    for _ in range(6):    # heaped sand of the rim, kicked up when the scrape was dug
        x, y = rnd.randrange(16), rnd.randrange(16)
        for dx, dy in ((0, 0), (1, 0)):
            px[(x + dx) % 16, y] = SAND["rim"] + (255,)
    for x, y in ((3, 11), (4, 12), (5, 12)):   # a shed feather, dark with the blue sheen at the tip
        px[x, y] = SAND["feather"] + (255,)
    px[6, 13] = SAND["feather2"] + (255,)
    for x, y in ((12, 3), (2, 2), (13, 13)):
        px[x, y] = SAND["pebble"] + (255,)
    return img


# a long egg standing up: (y from, y to, radius) slices; about 2.4 times as tall as it is wide, the blunt end up
EGG_SLICES = [(0.0, 1.0, 0.9), (1.0, 4.5, 1.25), (4.5, 5.5, 1.0), (5.5, 6.0, 0.6)]
# six eggs in three pairs round the middle (x, z, lean axis, lean angle: outward, block models allow 22.5 steps)
EGGS = [(5.0, 4.5, "x", -22.5), (8.0, 3.5, "x", -22.5), (11.5, 6.0, "z", -22.5),
        (11.0, 10.0, "x", 22.5), (7.5, 12.0, "x", 22.5), (4.0, 9.5, "z", 22.5)]


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    # the scrape: a low pad of sand with a raised rim all round, the eggs standing in it
    els.append({"from": [1, 0, 1], "to": [15, 1, 15], "faces": _faces("#nest", 1, 15, 1, 15, 0, 1, bottom=True)})
    for frm, to in (([0, 0, 3], [2, 2.5, 13]), ([14, 0, 3], [16, 2, 13]), ([3, 0, 0], [13, 2, 2]), ([3, 0, 14], [13, 2.5, 16]),
                    ([1, 0, 1], [3, 1.5, 3]), ([13, 0, 13], [15, 1.5, 15])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1])})
    for x0, z0, axis, angle in EGGS:
        for y0, y1, r in EGG_SLICES:
            # each slice is a rounded cross: two bars, the corners cut, sunk 0.5 into the sand
            for rx, rz in ((r, r * 0.7), (r * 0.7, r)) if r > 1 else ((r, r),):
                frm, to = [x0 - rx, 0.5 + y0, z0 - rz], [x0 + rx, 0.5 + y1, z0 + rz]
                els.append({"from": frm, "to": to, "rotation": {"origin": [x0, 0.5, z0], "axis": axis, "angle": angle},
                            "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], frm[1], to[1], top=True)})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1, 0], "scale": [0.85, 0.85, 0.85]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


HARNESS_PAL = {
    "o": (30, 24, 20),     # outline
    "d": (66, 46, 32),     # dark leather
    "l": (98, 70, 46),     # leather
    "h": (132, 98, 66),    # leather highlight
    "s": (52, 40, 30),     # strap
    "b": (214, 204, 178),  # bone plate
    "B": (238, 230, 208),  # bone light
    "n": (168, 156, 128),  # bone shade
    "i": (104, 104, 100),  # iron ring
    "I": (176, 176, 168),  # iron light
    "q": (34, 30, 30),     # quill
    "Q": (67, 101, 119),   # quill sheen, the steel blue of the model
}
HARNESS_ART = [
    "................",
    "......oooo......",
    ".....oi..io.....",
    ".....oIooIo...qo",
    "..oooooBBoooooQo",
    ".ohhllobBBollloo",
    ".ohlllobbbollldo",
    ".olllllonolllldo",
    ".olllllllllllldo",
    ".odllllllllllddo",
    "..osdddddddddso.",
    "..os.oooooo.so..",
    "..os........so..",
    "..oiIo....oiIo..",
    "..oIio....oIio..",
    "...oo......oo...",
]


def harness_sprite():
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y, row in enumerate(HARNESS_ART):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = HARNESS_PAL[ch] + (255,)
    return img


CUSTOM_EGGS = {"velociraptor": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"velociraptor_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "velociraptor_nest.png"))
    save_png(harness_sprite(), os.path.join(TEX, "item", "velociraptor_harness.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
