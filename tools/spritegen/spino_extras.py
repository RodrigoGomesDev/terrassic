"""The Spinosaurus' own egg art (2026-11-02, Rodrigo: every species its own items, "ovo e sela").

Egg (block terrassic:spinosaurus_egg, 3 hatch stages): four long eggs lying half buried in the wet sand of a river
sandbar, the water of the channel running along one side, a clump of horsetail reeds at the edge and the bones of
an eaten fish on the sand. Spinosaurus lived in the rivers of the Kem Kem beds (Morocco) and ate fish; the nest is on
the sand by the water, where a crocodile or a turtle would lay. Its eggs are unknown; theropod eggs are long and
could be coloured, so these are khaki with dark olive blotches, the colours of the river and of the animal.
Different from the other clutches: only this one has water in it.

No saddle yet (02/11): the sail runs over the whole back, from the shoulders to the hips, so there is no seat without
cutting the sail, and riding in the river (its home) does not exist yet. It waits for its own riding study.

usage: python3 -B tools/spritegen/spino_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (176, 166, 120), "light": (194, 184, 138), "blot": (92, 98, 66), "blot2": (120, 124, 84),
         "crack": (48, 44, 32), "hole": (22, 20, 16), "chick": (84, 98, 88), "chick2": (64, 76, 70), "tooth": (236, 230, 206)}
SAND = {"s0": (120, 104, 80), "s1": (136, 118, 90), "s2": (150, 132, 100), "wet": (96, 84, 66),
        "bone": (226, 220, 200), "bone2": (190, 182, 160)}
WATER = {"w0": (52, 92, 104), "w1": (66, 110, 120), "w2": (98, 140, 146)}
REED = {"r0": (70, 92, 50), "r1": (96, 120, 64), "joint": (48, 60, 36)}


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(97)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            k = 1.05 - 0.15 * (y / 15.0)
            c = SHELL["light"] if (x * 3 + y * 5) % 11 == 0 else SHELL["base"]
            px[x, y] = tuple(min(255, int(v * k)) for v in c) + (255,)
    for _ in range(6):    # dark olive blotches, each a few pixels, irregular
        x, y = rnd.randrange(15), rnd.randrange(15)
        for dx, dy in ((0, 0), (1, 0), (0, 1)) if rnd.random() < 0.6 else ((0, 0), (1, 0)):
            px[x + dx, y + dy] = SHELL["blot"] + (255,)
        px[(x + 2) % 16, y] = SHELL["blot2"] + (255,)
    if stage >= 1:
        for x, y in ((5, 5), (6, 5), (7, 6), (8, 6), (9, 5), (10, 6), (7, 7)):
            px[x, y] = SHELL["crack"] + (255,)
    if stage >= 2:        # a hole: the chick's long thin snout and the egg tooth
        for x, y in ((6, 6), (8, 5), (9, 6), (6, 7), (8, 7)):
            px[x, y] = SHELL["hole"] + (255,)
        for x, y in ((7, 6), (8, 6), (9, 7)):
            px[x, y] = SHELL["chick"] + (255,)
        px[10, 7] = SHELL["chick2"] + (255,)
        px[7, 5] = SHELL["tooth"] + (255,)
    return img


def nest():
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(13)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 5 + y * 9 + (x * y) % 3) % 7
            px[x, y] = (SAND["s0"] if h == 0 else SAND["s2"] if h == 4 else SAND["s1"]) + (255,)
    for x in range(16):          # the wet line along the water side (low u) and ripple marks
        px[x, 0] = SAND["wet"] + (255,)
        if x % 4 == 1:
            px[x, 1] = SAND["wet"] + (255,)
    for y in (6, 10):
        for x in range(2, 14):
            if (x + y) % 5 in (0, 1):
                px[x, y] = SAND["s2"] + (255,)
    # the bones of an eaten fish: a spine with ribs, the skull at one end
    for x in range(4, 12):
        px[x, 12] = SAND["bone"] + (255,)
        if x % 2 == 0 and x < 11:
            px[x, 11] = SAND["bone2"] + (255,); px[x, 13] = SAND["bone2"] + (255,)
    for x, y in ((12, 11), (12, 12), (12, 13), (13, 12)):
        px[x, y] = SAND["bone"] + (255,)
    return img


def water():
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = (WATER["w2"] if (x + y * 3) % 9 == 0 else WATER["w1"] if (x * 2 + y) % 5 == 0 else WATER["w0"]) + (255,)
    return img


def reed():
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = (REED["joint"] if y % 4 == 0 else REED["r1"] if x % 2 else REED["r0"]) + (255,)
    return img


# a long egg lying down, rounded (along from, along to, half width, height)
EGG_SLICES = [(0.0, 0.7, 0.7, 1.4), (0.7, 1.5, 1.1, 2.2), (1.5, 4.7, 1.4, 2.8), (4.7, 5.5, 1.1, 2.2), (5.5, 6.2, 0.7, 1.4)]
# four eggs half buried in the sandbar, away from the water (centre x, z, length axis, y rotation, sink)
EGGS = [(5.0, 9.0, "x", 22.5, 1.2), (10.2, 8.4, "x", -22.5, 1.0), (6.4, 12.6, "x", 0.0, 1.1), (11.0, 12.4, "z", 22.5, 1.3)]
SAND_TOP = 2.0


def _egg(cx, cz, axis, angle, sink):
    els = []
    for a0, a1, hw, h in EGG_SLICES:
        a0, a1 = a0 - 3.1, a1 - 3.1
        for w, hh in ((hw, h * 0.72), (hw * 0.72, h)):
            y0, y1 = SAND_TOP - sink, SAND_TOP - sink + hh
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
    # the channel along the back (north): water a little below the sand; the sandbar slopes up from it
    els.append({"from": [0, 0, 0], "to": [16, 1.0, 4], "faces": {**_faces("#water", 0, 16, 0, 4, 0, 1.0, bottom=True)}})
    for frm, to in (([0, 0, 4], [16, 1.4, 6]), ([0, 0, 6], [16, SAND_TOP, 16]), ([2, SAND_TOP, 9], [14, SAND_TOP + 0.6, 15])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1],
                                                            bottom=frm[1] == 0)})
    for e in EGGS:
        els += _egg(*e)
    # a clump of horsetail reeds at the water's edge (thin jointed stems of different heights)
    for x, z, h in ((1.5, 4.2, 9), (2.6, 5.0, 7), (1.2, 5.6, 6), (14.0, 4.6, 8), (13.0, 5.2, 5.5)):
        els.append({"from": [x, 1.0, z], "to": [x + 0.8, 1.0 + h, z + 0.8], "faces": _faces("#reed", x, x + 0.8, z, z + 0.8, 1.0, 1.0 + h)})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": f"terrassic:block/{sid}_nest",
                                                  "water": f"terrassic:block/{sid}_water", "reed": f"terrassic:block/{sid}_reed",
                                                  "particle": tex},
            "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 0.5, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


CUSTOM_EGGS = {"spinosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"spinosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "spinosaurus_nest.png"))
    save_png(water(), os.path.join(TEX, "block", "spinosaurus_water.png"))
    save_png(reed(), os.path.join(TEX, "block", "spinosaurus_reed.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
