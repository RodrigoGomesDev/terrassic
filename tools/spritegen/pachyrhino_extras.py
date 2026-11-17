"""The Pachyrhinosaurus' own egg art, nest and saddle sprite (1.11.0, its study docs/estudos/15_HERBIVOROS_1_11.md,
approved by Rodrigo on 10/11/2026). Not pachy_extras.py: that one is the Pachycephalosaurus'.

Egg (block terrassic:pachyrhinosaurus_egg, 3 hatch stages): no centrosaurine egg is known. The Protoceratops' eggs were
soft-shelled (Norell et al. 2020), the best guide for the ceratopsians, and soft eggs are kept warm in a mound. The
study's proposal (SPECULATIVE): a MOUND of sand and peat on top of a dry bank, ELONGATED soft eggs the colour of hide,
half buried, covered with MOSS. So: a stepped mound (the highest point in the middle, dark peat streaked into pale sand),
three long eggs lying in its top, sunk to the middle, two cushions of moss laid over their ends; nothing of the other
clutches (no reed heap, no roots, no mud ring, no needles). The shell is matte leather-buff with soft creases; at stage
1 it slumps, at stage 2 a tear shows the calf's smooth grey brow (no boss: the calf has none).

Saddle (item terrassic:pachyrhinosaurus_saddle): the "Sela de Carga": a thick felted blanket over the hump, a low hide
seat behind it, packs of hide hanging on both flanks, tied with cord.

usage: python3 -B tools/spritegen/pachyrhino_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (168, 140, 106), "light": (186, 160, 124), "mottle": (150, 122, 92), "crease": (128, 102, 76),
         "sand": (196, 178, 140), "tear": (74, 56, 40), "hole": (32, 24, 18), "brow": (122, 118, 112), "brow2": (98, 94, 90)}
MOUND = {"s0": (176, 158, 120), "s1": (196, 178, 140), "s2": (212, 196, 160), "p0": (52, 40, 30), "p1": (72, 56, 40),
         "p2": (92, 72, 50)}
MOSS = {"m0": (58, 76, 40), "m1": (78, 98, 52), "m2": (104, 124, 66), "m3": (130, 146, 84)}


def shell(stage):
    """a matte leather-buff long shell with soft creases, sand stuck low"""
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(71)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            k = 1.05 - 0.12 * (y / 15.0)
            c = SHELL["light"] if (x * 3 + y * 7) % 13 == 0 else SHELL["base"]
            px[x, y] = tuple(min(255, int(v * k)) for v in c) + (255,)
    for _ in range(12):
        x, y = rnd.randrange(16), rnd.randrange(16)
        px[x, y] = SHELL["mottle"] + (255,)
    for _ in range(10):                        # sand grains on the lower half
        x, y = rnd.randrange(16), 15 - int(rnd.random() ** 1.5 * 7)
        px[x, y] = SHELL["sand"] + (255,)
    folds = [(2, 4, 4), (9, 6, 4)]
    if stage >= 1:
        folds += [(4, 9, 6), (10, 11, 4), (1, 12, 3)]
    for x0, y0, n in folds:
        for i in range(n):
            px[(x0 + i) % 16, y0 + (i % 3 == 1)] = SHELL["crease"] + (255,)
    if stage >= 2:                             # a tear and the calf's smooth brow
        for x, y in ((4, 5), (5, 4), (6, 5), (7, 4), (8, 4), (9, 5), (10, 4), (11, 5)):
            px[x, y] = SHELL["tear"] + (255,)
        for x in range(6, 10):
            px[x, 6] = SHELL["brow"] + (255,)
        px[7, 7] = SHELL["brow2"] + (255,)
        px[8, 7] = SHELL["hole"] + (255,)
    return img


def nest():
    """the mound: pale sand streaked with dark peat in short layers"""
    from PIL import Image
    rnd = random.Random(29)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            band = (y + (x * 2) // 7) % 6
            if band in (0, 1):
                c = MOUND["p1"] if (x + y) % 5 else MOUND["p0"]
            elif band == 2:
                c = MOUND["p2"] if (x * 3 + y) % 4 else MOUND["s0"]
            else:
                h = (x * 5 + y * 3 + (x * y) % 5) % 9
                c = MOUND["s2"] if h == 0 else MOUND["s0"] if h in (3, 7) else MOUND["s1"]
            px[x, y] = c + (255,)
    for _ in range(8):
        x, y = rnd.randrange(16), rnd.randrange(16)
        px[x, y] = MOUND["p0"] + (255,)
    return img


def moss():
    """a cushion of moss: tufts in four greens"""
    from PIL import Image
    rnd = random.Random(41)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 7 + y * 5 + (x * y) % 3) % 8
            c = MOSS["m0"] if h == 0 else MOSS["m2"] if h in (2, 5) else MOSS["m1"]
            px[x, y] = c + (255,)
    for _ in range(14):
        x, y = rnd.randrange(16), rnd.randrange(16)
        px[x, y] = MOSS["m3"] + (255,)
    return img


# three long eggs lying in the top of the mound: (centre x, centre z, along x?)
EGGS = [(5.2, 6.0, True), (10.6, 7.4, False), (7.4, 10.8, True)]
HATCH = 0
TOP = 3.0                      # the top of the mound
LONG = [(0.0, 0.5, 0.9, 1.6), (0.5, 2.1, 1.3, 2.6), (2.1, 2.6, 0.9, 1.6)]   # y0, y1, half width, half length


def _egg(cx, cz, along_x, sink, tex="#egg"):
    els = []
    for y0, y1, hw, hl in LONG:
        a, b = TOP + y0 - sink, TOP + y1 - sink
        if b <= TOP:
            continue
        a = max(a, TOP)
        hx, hz = (hl, hw) if along_x else (hw, hl)
        frm, to = [cx - hx, a, cz - hz], [cx + hx, b, cz + hz]
        els.append({"from": frm, "to": to, "faces": _faces(tex, frm[0], to[0], frm[2], to[2], a, b, top=True)})
    return els


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    moss_tex = f"terrassic:block/{sid}_nest_moss"
    els = []

    def box(frm, to, t, bottom=False):
        els.append({"from": frm, "to": to, "faces": _faces(t, frm[0], to[0], frm[2], to[2], frm[1], to[1], bottom=bottom)})
    # the stepped mound: a wide base, a middle layer, the top
    box([0.5, 0, 0.5], [15.5, 1.0, 15.5], "#nest", bottom=True)
    box([1.5, 1.0, 1.5], [14.5, 2.0, 14.5], "#nest")
    box([2.5, 2.0, 2.5], [13.5, TOP, 13.5], "#nest")
    for k, (cx, cz, ax) in enumerate(EGGS):
        els.extend(_egg(cx, cz, ax, 1.2 if k != HATCH else 0.8))
    # moss laid over the ends of the eggs and a tuft on the slope
    for frm, to in (([2.8, TOP, 3.5], [6.0, TOP + 1.4, 8.0]), ([9.0, TOP, 9.0], [13.2, TOP + 1.2, 12.6]),
                    ([11.5, 1.0, 1.5], [14.5, 2.4, 4.5])):
        box(frm, to, "#moss")
    if stage >= 2:
        cx, cz, _ax = EGGS[HATCH]
        top = TOP + LONG[-1][1] - 0.8
        f = {k: {"uv": [6, 6, 10, 8], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
        els.append({"from": [cx - 1.6, top - 0.3, cz - 0.6], "to": [cx - 0.2, top + 0.5, cz + 0.6], "faces": f})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "moss": moss_tex, "particle": nest_tex},
            "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1.5, 0], "scale": [0.85, 0.85, 0.85]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (26, 20, 16), "w": (92, 70, 50), "W": (122, 96, 70), "x": (150, 124, 92), "h": (60, 46, 36),
              "H": (84, 66, 50), "c": (176, 160, 128), "p": (100, 80, 58), "P": (128, 104, 76)}
SADDLE_ART = [
    "................",
    "................",
    "................",
    "................",
    "......oooo......",
    ".....ohHHho.....",
    "...ooWWWWWWoo...",
    "..oWxWxWxWxWWo..",
    ".owwwwwwwwwwwwo.",
    ".oWWWWWWWWWWWWo.",
    "oppcwwwwwwwwcppo",
    "oPPo.c....c.oPPo",
    "oppo........oppo",
    ".oo..........oo.",
    "................",
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


CUSTOM_EGGS = {"pachyrhinosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"pachyrhinosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "pachyrhinosaurus_nest.png"))
    save_png(moss(), os.path.join(TEX, "block", "pachyrhinosaurus_nest_moss.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "pachyrhinosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
