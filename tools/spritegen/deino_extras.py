"""The Deinosuchus' own egg art (05/11/2026, the 1.8 remake; its study page, "Deinossuco: estudo para a 1.8", approved
by Rodrigo with the nest dug in the beach sand).

Egg (block terrassic:deinosuchus_egg, 3 hatch stages): a hole dug in the sand of the beach, filled back in, a low mound
with crushed shell and dry seaweed on it. Crocodiles of today dig their nest this way (the Nile crocodile, the
saltwater crocodile on a beach), and the mother opens it when the young call from inside; Deinosuchus lived on the
shores of the inland sea. So at stage 0 the eggs are not seen, only the closed mound; at stage 1 the mother has dug the
sand away and the top of the clutch shows; at stage 2 one egg is cracked and the hatchling's snout pokes out.
The eggs are hard-shelled and white like every crocodylian's, a chalky band round the middle (the opaque band the
embryo makes as it grows).
Kept apart from the Spinosaurus' sandbar by a river, the only other nest on sand: that one has water running in it
and the eggs lie in the open; this one is a closed mound on the beach with shells and weed.

No saddle: the Deinosuchus is not ridden (the study).

usage: python3 -B tools/spritegen/deino_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (226, 222, 210), "light": (240, 237, 228), "band": (206, 200, 184), "band2": (196, 190, 172),
         "sand": (196, 176, 130), "crack": (120, 112, 98), "hole": (30, 26, 20), "snout": (56, 52, 42),
         "snout2": (40, 37, 30), "eye": (198, 194, 78), "tooth": (232, 226, 206)}
SAND = {"s0": (182, 160, 112), "s1": (198, 178, 128), "s2": (214, 196, 148), "s3": (226, 212, 170),
        "shell": (236, 230, 214), "shell2": (204, 196, 178), "weed": (72, 62, 34), "weed2": (98, 84, 44), "dug": (156, 134, 92)}


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(41)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            band = 6 <= y <= 9
            c = SHELL["band"] if band else (SHELL["light"] if (x * 3 + y * 5) % 9 == 0 else SHELL["base"])
            if band and (x + y) % 5 == 0: c = SHELL["band2"]
            px[x, y] = c + (255,)
    for _ in range(7):                                # grains of sand stuck to the shell, low down
        x, y = rnd.randrange(16), 15 - int(rnd.random() ** 1.5 * 6)
        px[x, y] = SHELL["sand"] + (255,)
    if stage >= 2:                                    # a crack with the hatchling's dark snout and a tooth
        for x, y in ((3, 4), (4, 5), (5, 4), (6, 5), (7, 4), (8, 5), (9, 4), (10, 5), (11, 4), (12, 5)):
            px[x, y] = SHELL["crack"] + (255,)
        for x, y in ((5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (6, 7), (9, 7)):
            px[x, y] = SHELL["snout"] + (255,)
        px[7, 7] = SHELL["snout2"] + (255,); px[8, 7] = SHELL["snout2"] + (255,)
        px[6, 8] = SHELL["tooth"] + (255,); px[10, 7] = SHELL["eye"] + (255,)
    return img


def nest():
    """beach sand, fine and pale, ripples of a darker grain, bits of crushed shell and strands of dry seaweed"""
    from PIL import Image
    rnd = random.Random(23)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 7 + y * 13 + (x * y) % 5) % 11
            px[x, y] = (SAND["s0"] if h == 0 else SAND["s2"] if h in (2, 6, 9) else SAND["s3"] if h == 4 else SAND["s1"]) + (255,)
    for y0 in (3, 9, 14):                              # wind ripples, wandering
        for x in range(16):
            y = y0 + (1 if (x + y0) % 7 < 2 else 0)
            if y < 16 and x % 5 != 4:
                px[x, y] = SAND["s0"] + (255,)
    for _ in range(6):                                 # crushed shell
        x, y = rnd.randrange(15), rnd.randrange(16)
        px[x, y] = SAND["shell"] + (255,); px[x + 1, y] = SAND["shell2"] + (255,)
    for x0, y0, n in ((1, 6, 5), (9, 11, 4), (11, 1, 4)):   # strands of dry weed lying on the sand
        for i in range(n):
            px[(x0 + i) % 16, (y0 + (i % 3 == 2)) % 16] = (SAND["weed"] if i % 2 else SAND["weed2"]) + (255,)
    return img


# a hard white egg, an elongated ellipse: (along from, along to, half width, height) slices, about 1.6 times as long
EGG_SLICES = [(0.0, 0.8, 1.0, 2.0), (0.8, 1.8, 1.6, 3.0), (1.8, 4.0, 1.9, 3.4), (4.0, 5.0, 1.6, 3.0), (5.0, 5.8, 1.0, 2.0)]
# the clutch packed in the hole: (centre x, z, axis, y rotation, sink)
EGGS = [(5.2, 5.6, "z", 22.5, 0.8), (10.6, 6.0, "z", -22.5, 0.8), (7.8, 10.8, "x", 0, 0.8), (11.5, 11.0, "z", 22.5, 0.9)]
HATCH = 2
BASE = 1.0      # the bottom of the hole


def _egg(cx, cz, axis, angle, sink):
    els = []
    for a0, a1, hw, h in EGG_SLICES:
        a0, a1 = a0 - 2.9, a1 - 2.9
        for w, hh in ((hw, h * 0.72), (hw * 0.72, h)):
            y0, y1 = BASE, BASE + hh - sink
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
    def box(frm, to, bottom=False):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1], bottom=bottom)})
    # the floor of sand
    box([0.5, 0, 0.5], [15.5, BASE, 15.5], bottom=True)
    if stage == 0:
        # the closed mound: low, rounded, the eggs buried under it
        for frm, to in (([1.5, BASE, 2], [14.5, 2.4, 14]), ([2, BASE, 1.5], [14, 2.4, 14.5]), ([3, 2.4, 3.5], [13, 3.4, 12.5]),
                        ([5, 3.4, 5.5], [11, 4.0, 10.5])):
            box(frm, to)
        # a strand of weed and a shell on top
        box([6, 4.0, 7], [10, 4.4, 7.8]); box([8.5, 4.0, 9], [9.8, 4.5, 10.2])
    else:
        # the mother has dug the sand away: a rim of thrown-out sand, the clutch showing in the hole
        for frm, to in (([0.5, BASE, 0.5], [15.5, 2.6, 2.5]), ([0.5, BASE, 13.5], [15.5, 2.4, 15.5]),
                        ([0.5, BASE, 2.5], [2.5, 2.8, 13.5]), ([13.5, BASE, 2.5], [15.5, 2.2, 13.5]),
                        ([2.5, 2.6, 0.2], [7, 3.4, 2.2]), ([10, 2.2, 13.8], [14, 3.0, 15.8])):
            box(frm, to)
        for cx, cz, axis, angle, sink in EGGS:
            els.extend(_egg(cx, cz, axis, angle, sink))
        if stage >= 2:
            # the hatchling's snout poking out of the cracked egg
            cx, cz, axis, angle, sink = EGGS[HATCH]
            top = BASE + EGG_SLICES[2][3] - sink
            f = {k: {"uv": [6, 6, 9, 7], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
            els.append({"from": [cx - 2.4, top - 0.4, cz - 0.6], "to": [cx - 0.2, top + 0.7, cz + 0.6], "faces": f})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": nest_tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 2.0, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


CUSTOM_EGGS = {"deinosuchus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"deinosuchus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "deinosuchus_nest.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
