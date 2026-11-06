"""The Quetzalcoatlus' own egg art and saddle sprite (06/11/2026, its study in the page "1.9: estudos do
Quetzalcoatlus, do Edmontossauro e do Dakotaraptor", approved by Rodrigo).

Egg (block terrassic:quetzalcoatlus_egg, 3 hatch stages): pterosaur eggs were soft, with a thin shell like parchment,
and were buried (the Hamipterus eggs of China, Wang et al. 2017, many of them squashed out of shape). So: a low pale
patch of sand on the margin, two long soft eggs half buried in it and dented by the sand, the marks of a long beak
that dug them in, and a feather of grey fibres. At stage 1 the sand is pushed off them; at stage 2 one is split and
the hatchling's long beak pokes out: young pterosaurs flew almost from the egg (Unwin & Deeming 2019).
Kept apart from the other nests: no rim, no crater, no plant heap; two eggs only.

Saddle (item terrassic:quetzalcoatlus_saddle): a madder-red felt pad with an ochre rim, a small leather seat, a tall
grab bar and two straps for the base of the neck.

usage: python3 -B tools/spritegen/quetz_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (226, 220, 204), "light": (238, 234, 222), "fold": (198, 190, 172), "fold2": (182, 174, 156),
         "sand": (204, 186, 146), "crack": (120, 110, 96), "beak": (150, 146, 136), "beak2": (110, 106, 98)}
SAND = {"s0": (186, 166, 124), "s1": (202, 184, 142), "s2": (216, 200, 160), "s3": (228, 214, 178),
        "mark": (168, 148, 108), "fib": (120, 124, 126), "fib2": (152, 156, 156)}


def shell(stage):
    """a soft shell: wrinkled in long folds where the sand pressed it"""
    from PIL import Image
    rnd = random.Random(61)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            fold = (x * 2 + y + (y // 4) * 3) % 9
            px[x, y] = (SHELL["fold"] if fold == 0 else SHELL["fold2"] if fold == 5 and y > 8 else
                        SHELL["light"] if (x + y * 3) % 11 == 0 else SHELL["base"]) + (255,)
    for _ in range(10):
        x, y = rnd.randrange(16), 15 - int(rnd.random() ** 1.4 * 7)
        px[x, y] = SHELL["sand"] + (255,)
    if stage >= 2:
        for x, y in ((3, 6), (4, 7), (5, 6), (6, 7), (7, 6), (8, 7), (9, 6), (10, 7), (11, 6), (12, 7)):
            px[x, y] = SHELL["crack"] + (255,)
        for x in range(4, 13):
            px[x, 8] = SHELL["beak"] + (255,)
        px[12, 8] = SHELL["beak2"] + (255,); px[13, 8] = SHELL["beak2"] + (255,)
    return img


def nest():
    """pale margin sand, the long grooves a beak dug, a grey fibre feather"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 5 + y * 7 + (x * y) % 3) % 10
            px[x, y] = (SAND["s0"] if h == 0 else SAND["s2"] if h in (3, 7) else SAND["s3"] if h == 5 else SAND["s1"]) + (255,)
    for x0, y0, n in ((1, 3, 7), (6, 12, 8), (10, 5, 5)):      # beak grooves, straight and long
        for i in range(n):
            px[(x0 + i) % 16, y0] = SAND["mark"] + (255,)
    for i in range(5):                                         # the fibre feather
        px[11 + i % 4, 10 + i // 2] = (SAND["fib"] if i % 2 else SAND["fib2"]) + (255,)
    return img


# a long soft egg, a little flattened: (along from, to, half width, height) slices
EGG_SLICES = [(0.0, 1.0, 1.2, 1.8), (1.0, 2.2, 1.8, 2.6), (2.2, 4.4, 2.0, 2.8), (4.4, 5.6, 1.7, 2.4), (5.6, 6.6, 1.0, 1.6)]
EGGS = [(5.6, 6.4, "z", 22.5, 0.9), (10.4, 9.6, "z", -22.5, 0.9)]
HATCH = 1
BASE = 0.5


def _egg(cx, cz, axis, angle, sink):
    els = []
    for a0, a1, hw, h in EGG_SLICES:
        a0, a1 = a0 - 3.3, a1 - 3.3
        y0, y1 = BASE, BASE + h - sink
        frm, to = ([cx - hw, y0, cz + a0], [cx + hw, y1, cz + a1]) if axis == "z" else ([cx + a0, y0, cz - hw], [cx + a1, y1, cz + hw])
        el = {"from": frm, "to": to, "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], y0, y1, top=True)}
        if angle:
            el["rotation"] = {"origin": [cx, 0.5, cz], "axis": "y", "angle": angle}
        els.append(el)
    return els


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []

    def box(frm, to, bottom=False):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1], bottom=bottom)})
    box([1, 0, 1], [15, BASE, 15], bottom=True)
    if stage == 0:
        # half buried: the sand heaped over the eggs in two low humps
        box([3, BASE, 3], [8.5, 1.6, 10]); box([7.5, BASE, 6], [13, 1.6, 13]); box([4, 1.6, 4.5], [7.5, 2.1, 8.5])
        box([8.5, 1.6, 7.5], [12, 2.1, 11.5])
    else:
        for cx, cz, axis, angle, sink in EGGS:
            els.extend(_egg(cx, cz, axis, angle, sink))
        box([2, BASE, 12], [6, 1.2, 14.5]); box([11, BASE, 2], [14.5, 1.0, 5])     # the sand pushed off them
        if stage >= 2:
            cx, cz, axis, angle, sink = EGGS[HATCH]
            top = BASE + EGG_SLICES[2][3] - sink
            f = {k: {"uv": [4, 8, 14, 9], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
            els.append({"from": [cx - 0.4, top - 0.4, cz - 3.5], "to": [cx + 0.4, top + 0.4, cz - 0.5], "faces": f,
                        "rotation": {"origin": [cx, top, cz], "axis": "x", "angle": 22.5}})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": nest_tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 2.0, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (28, 20, 14), "f": (122, 58, 42), "F": (94, 44, 32), "y": (176, 138, 74),
              "l": (74, 47, 31), "L": (110, 72, 46), "w": (164, 130, 79), "W": (122, 94, 62)}
SADDLE_ART = [
    "................",
    ".......ow.......",
    ".......ow.......",
    "....owwwwwo.....",
    ".......ow.......",
    "..oooooowoooo...",
    ".oLLLLLLLLLLo...",
    ".olLLLLLLLLLLo..",
    "oyyyyyyyyyyyyyo.",
    "offFffFffFffFfo.",
    "oFffFffFffFffFo.",
    "oyyyyyyyyyyyyyo.",
    ".ooooooooooooo..",
    "..ol.......lo...",
    "..ol.......lo...",
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


CUSTOM_EGGS = {"quetzalcoatlus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"quetzalcoatlus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "quetzalcoatlus_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "quetzalcoatlus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
