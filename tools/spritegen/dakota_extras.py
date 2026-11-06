"""The Dakotaraptor's own egg art and saddle sprite (06/11/2026, its study in the page "1.9: estudos do
Quetzalcoatlus, do Edmontossauro e do Dakotaraptor", approved by Rodrigo).

Egg (block terrassic:dakotaraptor_egg, 3 hatch stages): the eggs of the big dromaeosaurs are ELONGATED, laid in pairs
in a ring with the blunt ends inward and half buried, as in Deinonychus and the troodontids; their shells were tinted
blue-green (Wiemann et al. 2018 found the pigments in maniraptoran eggs). Here the ring sits in the leaf litter against
a fallen log, the brooding parent's shelter: at stage 0 the eggs barely show under the log's shadow, at stage 1 they
are fully clear of the litter, at stage 2 one is split open along its length and the sickle claw of the chick shows.
Kept apart from the Velociraptor's nest of the mod (a bare scrape) and the round eggs of the others.

Saddle (item terrassic:dakotaraptor_saddle): the light hunting saddle: a short grey pad, a low dark seat with knee
rolls, a pale bone grip in front.

usage: python3 -B tools/spritegen/dakota_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import math
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (150, 186, 172), "light": (176, 206, 192), "pit": (122, 158, 146), "spot": (96, 112, 98),
         "earth": (92, 74, 54), "crack": (54, 62, 56), "claw": (34, 28, 24), "skin": (110, 70, 56)}
NEST = {"l0": (74, 58, 38), "l1": (96, 74, 46), "l2": (120, 92, 56), "l3": (140, 112, 66), "g0": (70, 82, 44),
        "b0": (64, 50, 38), "b1": (84, 66, 48), "b2": (104, 84, 60), "r0": (150, 128, 96), "r1": (124, 102, 74)}


def shell(stage):
    """blue-green, faintly speckled, the ridges along the egg; earth on the half that was buried"""
    from PIL import Image
    rnd = random.Random(71)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 2 + y * 7 + (x * y) % 3) % 8
            px[x, y] = (SHELL["light"] if h == 0 else SHELL["pit"] if h in (3, 6) else SHELL["base"]) + (255,)
    for _ in range(9):
        px[rnd.randrange(16), rnd.randrange(16)] = SHELL["spot"] + (255,)
    for _ in range(14):
        x, y = rnd.randrange(16), 15 - int(rnd.random() ** 1.4 * 6)
        px[x, y] = SHELL["earth"] + (255,)
    if stage >= 2:
        for x in range(2, 14):
            px[x, 6 + (x % 2)] = SHELL["crack"] + (255,)
        for x, y in ((7, 8), (8, 8), (8, 9), (9, 9)):
            px[x, y] = SHELL["claw"] + (255,)
        for x in range(4, 7):
            px[x, 8] = SHELL["skin"] + (255,)
    return img


def nest():
    """the leaf litter (brown leaves and a few green ones) on the bottom, and the bark of the fallen log"""
    from PIL import Image
    rnd = random.Random(23)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(8):
            h = (x * 5 + y * 3 + (x * y) % 4) % 7
            px[x, y] = (NEST["l0"] if h == 0 else NEST["l2"] if h in (2, 5) else NEST["l1"]) + (255,)
    for _ in range(10):
        x, y = rnd.randrange(8), rnd.randrange(16)
        px[x, y] = (NEST["g0"] if rnd.random() < 0.3 else NEST["l3"]) + (255,)
    # the bark (right half): long fissures, and the cut end rings in the corner
    for y in range(16):
        for x in range(8, 16):
            f = (x * 3 + (y // 4) * 5) % 5
            px[x, y] = (NEST["b0"] if f == 0 else NEST["b2"] if f == 3 else NEST["b1"]) + (255,)
    for y in range(12, 16):
        for x in range(12, 16):
            r = math.hypot(x - 13.5, y - 13.5)
            px[x, y] = (NEST["r1"] if int(r * 1.5) % 2 else NEST["r0"]) + (255,)
    return img


BASE = 0.6
# the ring: (centre x, centre z, angle of the long axis, rad) pointing out from the middle, in pairs
RING = [(8.0 + 3.6 * math.cos(a), 9.0 + 3.6 * math.sin(a), a) for a in [k * math.pi / 3.0 + 0.3 for k in range(6)]]
HATCH = 1


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []

    def litter(frm, to):
        f = {k: {"uv": [0, 0, 8, 16], "texture": "#nest"} for k in ("north", "south", "east", "west", "up", "down")}
        els.append({"from": frm, "to": to, "faces": f})
    litter([0.5, 0, 0.5], [15.5, BASE, 15.5])
    # the fallen log along the back, its bark half
    bark = {k: {"uv": [8, 0, 16, 16], "texture": "#nest"} for k in ("north", "south", "up", "down")}
    bark.update({k: {"uv": [12, 12, 16, 16], "texture": "#nest"} for k in ("east", "west")})
    els.append({"from": [0, BASE, 1], "to": [16, BASE + 4.2, 5], "faces": bark,
                "rotation": {"origin": [8, 2, 3], "axis": "y", "angle": 22.5}})
    sink = {0: 1.4, 1: 0.5, 2: 0.5}[stage]
    for k, (cx, cz, a) in enumerate(RING):
        L, W, H = 5.0, 2.4, 2.4
        y0 = BASE + 0.0 - sink + (0.3 if k == HATCH and stage >= 2 else 0.0)
        frm, to = [cx - W / 2, max(BASE, y0), cz - L / 2], [cx + W / 2, y0 + H, cz + L / 2]
        el = {"from": frm, "to": to, "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], frm[1], to[1], top=True)}
        ang = math.degrees(-a) + 90.0
        ang = max(-45.0, min(45.0, round(((ang + 90) % 180 - 90) / 22.5) * 22.5))
        if ang:
            el["rotation"] = {"origin": [cx, BASE, cz], "axis": "y", "angle": ang}
        els.append(el)
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": nest_tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 2.0, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (24, 18, 14), "p": (106, 96, 80), "P": (84, 73, 60), "l": (74, 47, 31), "L": (94, 62, 40),
              "b": (226, 216, 189), "B": (184, 172, 144), "s": (42, 28, 18)}
SADDLE_ART = [
    "................",
    "................",
    "................",
    "..oo............",
    ".obBo...........",
    ".oBBo.....ooo...",
    "..oo.ooooooLLo..",
    "....oLLlLLLLLo..",
    "...oLLLLlLLlLo..",
    "..oppppppppppppo",
    "..oPpPpPpPpPpPpo",
    "...ooooosooooo..",
    ".......os.......",
    ".......os.......",
    "........o.......",
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


CUSTOM_EGGS = {"dakotaraptor": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"dakotaraptor_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "dakotaraptor_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "dakotaraptor_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
