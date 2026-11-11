"""The Maiasaura's own egg art, nest and saddle sprite (1.11.0, its study docs/estudos/15_HERBIVOROS_1_11.md, approved
by Rodrigo on 10/11/2026).

Egg (block terrassic:maiasaura_egg, 3 hatch stages, and COVERED or not): the nest of the Two Medicine is a MOUND of
mud about two metres across with a crater in the middle (Horner & Makela 1979); inside, the eggs lie in RINGS (no
spiral: the spiral is the Edmontosaurus'), oval and a little pointed at one end, the size of an ostrich egg, olive-grey
with fine ridges on the shell (the fossils are black, but the black is the fossil's). The mother covers them with a
layer of dark leaves and rotting twigs, a little damp (a HYPOTHESIS: the clutch warmed by rotting plants, Horner's
reading), and the model has a covered version of each stage (DinoEggBlock.COVERED): the crater filled with the litter,
the tips of two eggs showing. Uncovered: the crater open, the ring of eggs in it; at stage 2 one egg is broken and the
calf's short bill pokes out.

Saddle (item terrassic:maiasaura_saddle): the "Sela de Ninhal": a broad mat of woven reeds with a green weft, a low
hide seat on a wooden frame and a deep saddlebag of plaited bark fibre at the side.

usage: python3 -B tools/spritegen/maia_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import math
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (128, 128, 104), "light": (150, 150, 124), "ridge": (104, 104, 84), "mud": (96, 80, 58),
         "crack": (64, 60, 48), "bill": (46, 42, 32), "bill2": (34, 30, 24)}
MUD = {"m0": (88, 72, 52), "m1": (106, 88, 64), "m2": (124, 104, 76), "dry": (140, 122, 92)}
LITTER = {"l0": (40, 44, 26), "l1": (58, 62, 34), "l2": (78, 78, 44), "rot": (84, 66, 40), "rot2": (66, 52, 32),
          "twig": (102, 82, 52), "wet": (34, 36, 26)}


def shell(stage):
    """an olive-grey shell with fine ridges running along the egg (the ridged eggshell of the fossils), mud on its
    lower part"""
    from PIL import Image
    rnd = random.Random(71)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            ridge = (x + (y // 4) % 2) % 3 == 0
            h = (x * 5 + y * 3) % 11
            col = SHELL["ridge"] if ridge and h % 2 else SHELL["light"] if h == 0 else SHELL["base"]
            px[x, y] = col + (255,)
    for _ in range(14):
        x, y = rnd.randrange(16), 15 - int(rnd.random() ** 1.4 * 6)
        px[x, y] = SHELL["mud"] + (255,)
    if stage >= 2:
        for x, y in ((3, 6), (4, 5), (5, 6), (6, 5), (7, 6), (8, 5), (9, 6), (10, 5), (11, 6), (12, 5)):
            px[x, y] = SHELL["crack"] + (255,)
        for x in range(6, 10):
            px[x, 7] = SHELL["bill"] + (255,)
        px[6, 8] = SHELL["bill2"] + (255,); px[9, 8] = SHELL["bill2"] + (255,)
    return img


def nest():
    """the mud of the mound: clods of damp earth, a few dry pale crusts where the sun dried the rim"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 7 + y * 5 + (x * y) % 3) % 10
            c = MUD["m0"] if h in (0, 5) else MUD["m2"] if h in (2, 7) else MUD["dry"] if h == 9 and y < 6 else MUD["m1"]
            px[x, y] = c + (255,)
    return img


def litter():
    """the cover: dark leaves, some still green, most brown and rotting, twigs across them, damp in the hollows"""
    from PIL import Image
    rnd = random.Random(29)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 3 + y * 7 + (x * y) % 5) % 9
            c = LITTER["rot2"] if h in (0, 4) else LITTER["rot"] if h in (2, 7) else LITTER["wet"] if h == 8 else LITTER["l0"]
            px[x, y] = c + (255,)
    for _ in range(9):                      # leaves: a small blade of two or three pixels
        x, y = rnd.randrange(15), rnd.randrange(15)
        col = LITTER["l2"] if rnd.random() < 0.4 else LITTER["l1"]
        px[x, y] = col + (255,); px[x + 1, y] = col + (255,)
        if rnd.random() < 0.5:
            px[x + 1, y + 1] = col + (255,)
    for x0, y0, dx, dy, n in ((1, 3, 1, 0, 7), (9, 11, 1, -1, 5), (4, 13, 1, 0, 6)):   # twigs
        for i in range(n):
            xx, yy = x0 + dx * i, y0 + dy * i
            if 0 <= xx < 16 and 0 <= yy < 16:
                px[xx, yy] = LITTER["twig"] + (255,)
    return img


OVAL = [(0.0, 0.8, 1.0), (0.8, 2.8, 1.6), (2.8, 4.0, 1.2), (4.0, 4.8, 0.6)]    # a little pointed at the top
RING = [(8.0 + 4.3 * math.cos(a), 8.0 + 4.3 * math.sin(a)) for a in (0.3, 1.35, 2.4, 3.45, 4.5, 5.55)]
HATCH = 1
FLOOR = 1.0


def _oval(cx, cz, sink, tex="#egg"):
    els = []
    for y0, y1, hw in OVAL:
        a, b = FLOOR + y0 - sink, FLOOR + y1 - sink
        if b <= FLOOR:
            continue
        a = max(a, FLOOR)
        frm, to = [cx - hw, a, cz - hw], [cx + hw, b, cz + hw]
        els.append({"from": frm, "to": to, "faces": _faces(tex, frm[0], to[0], frm[2], to[2], a, b, top=True)})
    return els


def _mound(els):
    """the crater floor and the raised mud rim round it"""
    def box(frm, to, bottom=False):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1], bottom=bottom)})
    box([0.5, 0, 0.5], [15.5, FLOOR, 15.5], bottom=True)
    for frm, to in (([0.5, FLOOR, 0.5], [15.5, 3.0, 2.0]), ([0.5, FLOOR, 14.0], [15.5, 3.0, 15.5]),
                    ([0.5, FLOOR, 2.0], [2.0, 3.5, 14.0]), ([14.0, FLOOR, 2.0], [15.5, 2.5, 14.0])):
        box(frm, to)


def egg_model(sid, stage, covered=False):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    _mound(els)
    if covered:
        # the litter heaped in the crater over the ring, two egg tips showing through it
        for frm, to in (([2.0, FLOOR, 2.0], [14.0, 3.6, 14.0]), ([3.5, 3.6, 3.5], [12.5, 4.6, 12.5])):
            els.append({"from": frm, "to": to, "faces": _faces("#litter", frm[0], to[0], frm[2], to[2], frm[1], to[1])})
        for k in (0, 3):
            cx, cz = RING[k]
            els.append({"from": [cx - 0.6, 3.6, cz - 0.6], "to": [cx + 0.6, 4.4, cz + 0.6],
                        "faces": _faces("#egg", cx - 0.6, cx + 0.6, cz - 0.6, cz + 0.6, 3.6, 4.4)})
    else:
        for k, (cx, cz) in enumerate(RING):
            els.extend(_oval(cx, cz, 0.6 if k != HATCH else 0.3))
        if stage >= 2:
            cx, cz = RING[HATCH]
            top = FLOOR + OVAL[-1][1] - 0.3
            f = {k: {"uv": [6, 7, 10, 8], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
            els.append({"from": [cx - 0.9, top - 0.4, cz - 2.0], "to": [cx + 0.9, top + 0.4, cz - 0.4], "faces": f})
    textures = {"egg": tex, "nest": nest_tex, "particle": nest_tex}
    if covered:
        textures["litter"] = f"terrassic:block/{sid}_nest_litter"
    return {"parent": "block/block", "textures": textures, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 2.0, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


def covered_model(sid, stage):
    return egg_model(sid, stage, covered=True)


SADDLE_PAL = {"o": (28, 20, 14), "w": (138, 120, 72), "W": (168, 148, 92), "g": (76, 90, 48), "h": (90, 66, 48),
              "H": (122, 90, 64), "d": (68, 52, 34), "D": (108, 84, 54), "b": (124, 100, 64), "B": (152, 128, 78)}
SADDLE_ART = [
    "................",
    "................",
    "................",
    "....oo....oo....",
    "....odo..odo....",
    "....oDoooodo....",
    "...oHHHHHHHHo...",
    "..ohhhhhhhhhho..",
    ".owWwWwWwWwWwWo.",
    ".ogggggggggggggo",
    ".oWwWwWwWwWwWwo.",
    "..oooooooooooo..",
    "..obBbBo........",
    "..oBbBbo........",
    "..obBbBo........",
    "...oooo.........",
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


CUSTOM_EGGS = {"maiasaura": egg_model}
COVERED_EGGS = {"maiasaura": covered_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"maiasaura_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "maiasaura_nest.png"))
    save_png(litter(), os.path.join(TEX, "block", "maiasaura_nest_litter.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "maiasaura_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
