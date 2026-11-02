"""The Protoceratops' own egg art (2026-11-02, Rodrigo: "temos que ver os itens também (ovo e sela)").

Egg (block terrassic:protoceratops_egg, 3 hatch stages): four long SOFT eggs lying in a ring, half buried in a low
mound of the red Djadokhta sand. Protoceratops eggs were soft-shelled: a thin leathery membrane like a turtle's, with
little or no mineral (Norell et al. 2020, Nature, on embryos from Ukhaa Tolgod), so they were buried to keep them
from drying, and a nest with fifteen young was found in the same red sands (Fastovsky et al. 2011). The shell is
matte, pale grey with creases and grains of red sand stuck to it; it dents and tears instead of cracking: stage 1
shows the shell slumping in deeper folds, stage 2 a slit with the hatchling's grey beak. The sand of the mound keeps
the rake marks of the hind claws that buried it (the same shovel claws the adult digs with).
Different from the other two clutches in sand: the Velociraptor's are hard, blue-green and stand upright in pale sand;
the Pteranodon's are short and round in beach sand with kelp.

No saddle: an animal the size of a sheep carries nobody (docs: the review of 02/11).

usage: python3 -B tools/spritegen/proto_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (198, 199, 191), "light": (214, 215, 208), "fold": (170, 170, 160), "fold2": (150, 149, 140),
         "sand": (176, 104, 66), "sand2": (150, 84, 52), "slit": (70, 52, 44), "hole": (34, 26, 22),
         "beak": (102, 93, 82), "beak2": (134, 124, 110), "skin": (190, 156, 112), "frill": (214, 190, 150)}
SAND = {"s0": (168, 96, 60), "s1": (184, 110, 70), "s2": (198, 126, 82), "s3": (212, 146, 100),
        "rake": (132, 74, 46), "rake2": (226, 166, 120), "pebble": (110, 84, 70), "frond": (92, 106, 58), "frond2": (122, 132, 70)}


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(53)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            k = 1.04 - 0.12 * (y / 15.0)       # lit from above, darker toward the sand
            c = SHELL["light"] if (x * 5 + y * 3) % 11 == 0 else SHELL["base"]
            px[x, y] = tuple(min(255, int(v * k)) for v in c) + (255,)
    # soft creases: short wavy folds across the shell, more of them as it slumps before hatching
    folds = [(2, 3, 4), (9, 2, 3), (4, 8, 5), (11, 9, 3), (1, 12, 3), (7, 13, 4)]
    if stage >= 1:
        folds += [(5, 5, 4), (10, 6, 4), (2, 10, 4), (8, 11, 5)]
    for x0, y0, n in folds:
        for i in range(n):
            y = y0 + (1 if i % 3 == 1 else 0)
            px[(x0 + i) % 16, y] = (SHELL["fold2"] if stage >= 1 and i % 2 == 0 else SHELL["fold"]) + (255,)
    for _ in range(9):    # red sand stuck to the damp shell, most of it low
        x, y = rnd.randrange(16), 15 - int(rnd.random() ** 1.6 * 12)
        px[x, y] = (SHELL["sand"] if rnd.random() < 0.6 else SHELL["sand2"]) + (255,)
    if stage >= 2:        # a slit torn along the shell: dark inside, the hatchling's grey beak tip and its skin
        for x, y in ((5, 6), (6, 6), (7, 7), (8, 7), (9, 7), (10, 6)):
            px[x, y] = SHELL["slit"] + (255,)
        for x, y in ((6, 7), (10, 7), (7, 8), (9, 8)):
            px[x, y] = SHELL["hole"] + (255,)
        for x, y in ((7, 7), (8, 7), (7, 8)):
            px[x, y] = SHELL["skin"] + (255,)
        px[8, 8] = SHELL["beak2"] + (255,)
        for x in (5, 6, 7):
            px[x, 9] = SHELL["frill"] + (255,)
    return img


def nest():
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(31)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 7 + y * 5 + (x * y) % 5) % 10
            px[x, y] = (SAND["s0"] if h == 0 else SAND["s3"] if h in (4, 8) else SAND["s2"] if h == 6 else SAND["s1"]) + (255,)
    # the rake marks of the hind claws: three short grooves side by side, drawn once, slanting
    for k in range(3):
        for i in range(5):
            x, y = 2 + i + k, 9 + k * 2 - (i * 2) // 3
            px[x, y] = SAND["rake"] + (255,)
            if i < 4:
                px[x, y + 1] = SAND["s3"] + (255,)
    for x, y in ((12, 2), (4, 13), (8, 7)):
        px[x, y] = SAND["pebble"] + (255,)
    for x, y in ((13, 6), (14, 7), (12, 7)):    # a bitten fern frond, the parent's food
        px[x, y] = SAND["frond"] + (255,)
    px[13, 7] = SAND["frond2"] + (255,)
    return img


# a long egg lying down, rounded: (along from, along to, half width, height) slices, about 2.2 times as long as wide.
# Each slice is a rounded cross (a wide low bar and a narrow high bar), so the egg reads round from any side.
EGG_SLICES = [(0.0, 0.8, 0.9, 1.8), (0.8, 1.8, 1.5, 2.9), (1.8, 5.2, 1.9, 3.6), (5.2, 6.2, 1.5, 2.9), (6.2, 7.0, 0.9, 1.8)]
# four eggs in a ring (a pinwheel), their narrow ends toward the middle (centre x, z, axis of the length, y rotation, sink)
EGGS = [(6.6, 4.2, "z", 22.5, 1.0), (11.8, 6.6, "x", 22.5, 1.3), (9.4, 11.8, "z", 22.5, 1.1),
        (4.2, 9.4, "x", 22.5, 1.2)]
HATCH = 2   # the egg that hatches first (the one in front in the inventory)
TOP = 1.5   # the top of the mound's pad, where the eggs lie


def _egg(cx, cz, axis, angle, sink, squash=1.0):
    els = []
    for a0, a1, hw, h in EGG_SLICES:
        a0, a1 = a0 - 3.5, a1 - 3.5
        for w, hh in ((hw, h * 0.72 * squash), (hw * 0.72, h * squash)):
            y0, y1 = max(0.5, TOP - sink), TOP - sink + hh
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
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    # the mound: a wide low pad with a rounded edge, a raised rim of kicked-up sand and a heap in the middle
    for frm, to in (([2, 0, 1], [14, 1, 15]), ([1, 0, 2], [15, 1, 14]), ([3, 1, 3], [13, TOP, 13]),
                    ([0.5, 0, 5], [2, 2, 11]), ([14, 0, 4], [15.5, 1.8, 10]), ([5, 0, 14], [11, 2, 15.5]),
                    ([6, TOP, 6], [10, 3.2, 10]), ([5, TOP, 7], [11, 2.6, 9]), ([7, TOP, 5], [9, 2.6, 11])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1],
                                                            bottom=frm[1] == 0)})
    for i, (cx, cz, axis, angle, sink) in enumerate(EGGS):
        # before hatching the soft shells slump: the egg that hatches first sags lower
        els += _egg(cx, cz, axis, angle, sink, squash=0.85 if stage >= 1 and i == HATCH else 1.0)
    # sand thrown over the inner ends of the eggs (the clutch was buried)
    for frm, to in (([7, TOP, 6], [9, 3.6, 7.5]), ([9.5, TOP, 8], [10.8, 3.4, 10]), ([5.2, TOP, 8.5], [6.6, 3.2, 10])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1])})
    if stage >= 2:
        # the hatchling's beak tip poking out of the tear on top of the egg that slumped
        cx, cz, axis, angle, sink = EGGS[HATCH]
        top = TOP - sink + EGG_SLICES[2][3]
        f = {k: {"uv": [8, 8, 9, 9], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
        els.append({"from": [cx - 0.5, top - 0.4, cz - 0.5], "to": [cx + 0.5, top + 0.8, cz + 0.6], "faces": f,
                    "rotation": {"origin": [cx, 0.5, cz], "axis": "y", "angle": angle}})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1.5, 0], "scale": [0.95, 0.95, 0.95]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


CUSTOM_EGGS = {"protoceratops": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"protoceratops_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "protoceratops_nest.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
