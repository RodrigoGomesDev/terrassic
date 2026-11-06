"""The Edmontosaurus' own egg art and saddle sprite (06/11/2026, its study in the page "1.9: estudos do
Quetzalcoatlus, do Edmontossauro e do Dakotaraptor", approved by Rodrigo).

Egg (block terrassic:edmontosaurus_egg, 3 hatch stages): hadrosaurs nested in colonies and kept the clutch warm under
plants that rotted on it. Here: a shallow bowl scraped in the earth, the round eggs laid in a SPIRAL in it, the whole
covered by a heap of fern fronds. At stage 0 only the heap of fronds shows; at stage 1 the fronds are pulled aside and
the spiral of eggs shows in the bowl; at stage 2 one egg is broken and the hatchling's flat little bill pokes out.
Kept apart from the Parasaurolophus' mud crater under reeds: no raised rim of mud, a plant heap on top, a spiral.

Saddle (item terrassic:edmontosaurus_saddle): the traveller's saddle: a deep dark-leather seat on an indigo felt with
an ochre stripe, a rolled hide bedroll behind it, a water bladder hanging at the side.

usage: python3 -B tools/spritegen/edmo_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import math
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (206, 196, 172), "light": (224, 216, 196), "pit": (176, 166, 142), "earth": (120, 96, 66),
         "crack": (96, 84, 66), "bill": (58, 50, 42), "bill2": (40, 34, 28)}
NEST = {"e0": (92, 72, 48), "e1": (112, 88, 60), "e2": (130, 104, 72), "f0": (52, 76, 36), "f1": (72, 98, 46),
        "f2": (96, 120, 58), "rot": (110, 90, 52), "rot2": (88, 72, 42)}


def shell(stage):
    """round eggs with a pebbled shell, earth on their lower half"""
    from PIL import Image
    rnd = random.Random(53)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 3 + y * 5 + (x * y) % 4) % 7
            px[x, y] = (SHELL["light"] if h == 0 else SHELL["pit"] if h == 4 else SHELL["base"]) + (255,)
    for _ in range(12):
        x, y = rnd.randrange(16), 15 - int(rnd.random() ** 1.3 * 7)
        px[x, y] = SHELL["earth"] + (255,)
    if stage >= 2:
        for x, y in ((3, 5), (4, 6), (5, 5), (6, 6), (7, 5), (8, 6), (9, 5), (10, 6), (11, 5), (12, 6)):
            px[x, y] = SHELL["crack"] + (255,)
        for x in range(5, 11):
            px[x, 7] = SHELL["bill"] + (255,)
        px[5, 8] = SHELL["bill2"] + (255,); px[10, 8] = SHELL["bill2"] + (255,)
    return img


def nest():
    """the scraped earth of the bowl, and the fern fronds of the heap: a midrib with paired leaflets, some fresh, some
    already brown and rotting (the warmth of the nest)"""
    from PIL import Image
    rnd = random.Random(19)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 7 + y * 3 + (x * y) % 5) % 9
            px[x, y] = (NEST["e0"] if h == 0 else NEST["e2"] if h in (3, 6) else NEST["e1"]) + (255,)
    for k, (x0, y0, dx, dy, n) in enumerate(((1, 2, 1, 1, 9), (14, 1, -1, 1, 10), (2, 13, 1, -1, 8), (8, 15, 0, -1, 7))):
        fresh = k % 2 == 0
        x, y = x0, y0
        for i in range(n):
            if 0 <= x < 16 and 0 <= y < 16:
                px[x, y] = (NEST["f0"] if fresh else NEST["rot2"]) + (255,)
                for sx, sy in ((dy, -dx), (-dy, dx)):           # the leaflets either side of the midrib
                    xx, yy = x + sx, y + sy
                    if 0 <= xx < 16 and 0 <= yy < 16 and i % 2 == 0:
                        px[xx, yy] = (NEST["f2" if i < n // 2 else "f1"] if fresh else NEST["rot"]) + (255,)
            x += dx; y += dy
    return img


BALL = [(0.0, 0.8, 1.4), (0.8, 2.2, 2.1), (2.2, 3.4, 1.9), (3.4, 4.0, 1.1)]
SPIRAL = [(8.0, 8.0)] + [(8.0 + r * math.cos(a), 8.0 + r * math.sin(a)) for r, a in ((3.6, 0.0), (3.8, 1.6), (4.6, 3.1), (5.2, 4.5))]
HATCH = 2
BASE = 0.6


def _ball(cx, cz, sink):
    els = []
    for y0, y1, hw in BALL:
        a, b = BASE + y0 - sink, BASE + y1 - sink
        if b <= BASE:
            continue
        a = max(a, BASE)
        frm, to = [cx - hw, a, cz - hw], [cx + hw, b, cz + hw]
        els.append({"from": frm, "to": to, "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], a, b, top=True)})
    return els


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []

    def box(frm, to, bottom=False, rot=None):
        el = {"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1], bottom=bottom)}
        if rot:
            el["rotation"] = rot
        els.append(el)
    box([0.5, 0, 0.5], [15.5, BASE, 15.5], bottom=True)
    if stage == 0:
        # the heap of fronds over the clutch, low and untidy
        for frm, to, ang in (([2, BASE, 3], [14, 2.2, 13], 0), ([3, 2.2, 2], [12, 3.4, 12], 22.5), ([5, 3.4, 5], [11, 4.4, 11], -22.5)):
            box(frm, to, rot={"origin": [8, 1, 8], "axis": "y", "angle": ang} if ang else None)
    else:
        # the fronds pulled aside onto the rim, the spiral of eggs in the bowl
        box([0.5, BASE, 0.5], [15.5, 1.8, 3]); box([12.5, BASE, 3], [15.5, 1.6, 15.5])
        for k, (cx, cz) in enumerate(SPIRAL):
            els.extend(_ball(cx, cz, 0.8 if k != HATCH else 0.5))
        if stage >= 2:
            cx, cz = SPIRAL[HATCH]
            top = BASE + BALL[-1][1] - 0.5
            f = {k: {"uv": [5, 7, 11, 8], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
            els.append({"from": [cx - 1.0, top - 0.3, cz - 2.2], "to": [cx + 1.0, top + 0.5, cz - 0.4], "faces": f})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": nest_tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 2.0, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (26, 18, 12), "l": (67, 44, 30), "L": (94, 62, 40), "b": (106, 90, 68), "B": (138, 118, 88),
              "f": (58, 68, 88), "F": (42, 48, 64), "y": (184, 154, 90), "w": (142, 108, 64), "W": (110, 82, 48)}
SADDLE_ART = [
    "................",
    "................",
    "........oooooo..",
    ".......obBbBbBo.",
    "..oo...oBbBbBbo.",
    ".oLLo..oooooooo.",
    "oLlLLooooo......",
    "oLLLLLLLLLLLLo..",
    "olLLLLlLLLLLLLo.",
    "oyyyyyyyyyyyyyo.",
    "offFffFffFffFfo.",
    "oFfffFffoowwo.o.",
    ".oooooooowWWo...",
    "........owwwo...",
    ".........ooo....",
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


CUSTOM_EGGS = {"edmontosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"edmontosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "edmontosaurus_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "edmontosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
