"""The Therizinosaurus' own egg art and saddle sprite (06/11/2026; its study page, "Terizinossauro: estudo e modelo",
approved by Rodrigo with the buried clutch under a crust of red clay).

Egg (block terrassic:therizinosaurus_egg, 3 hatch stages): a nesting colony of therizinosaurs in Mongolia (Tanaka et
al. 2019) had its clutches BURIED, without mound or crater, the eggs round, and a thin red bed over the nests. So at
stage 0 only the cracked red crust shows, with dry leaves on it; at stage 1 the crust has broken open over three round
eggs with a rough, branching shell (the dendroolithid eggshell found with therizinosaur embryos); at stage 2 one egg
is cracked and the hatchling's little beak and a tuft of down poke out. Kept apart from the other nests: the
Parasaurolophus' mud crater, the Styracosaurus' reed heap, the Deinosuchus' beach pit.

Saddle (item terrassic:therizinosaurus_saddle): a teal felt blanket with an ochre rim, a broad hide pad with a high
cantle behind (the back slopes), a bone grab bar in front.

usage: python3 -B tools/spritegen/theri_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (222, 214, 196), "light": (238, 232, 216), "ridge": (196, 186, 164), "pit": (170, 160, 138),
         "clay": (158, 74, 48), "crack": (96, 84, 66), "hole": (28, 22, 16), "beak": (52, 44, 34), "down": (196, 150, 70),
         "down2": (160, 116, 50)}
CLAY = {"c0": (120, 52, 34), "c1": (146, 66, 42), "c2": (168, 82, 52), "c3": (186, 102, 66), "crack": (74, 34, 22),
        "sand": (196, 168, 120), "leaf": (110, 84, 36), "leaf2": (140, 108, 46), "leaf3": (86, 66, 30)}


def shell(stage):
    """the dendroolithid shell: rough, with short branching ridges and pits; a smear of the red clay low down"""
    from PIL import Image
    rnd = random.Random(73)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 5 + y * 3 + (x * y) % 7) % 9
            px[x, y] = (SHELL["light"] if h == 0 else SHELL["ridge"] if h in (3, 7) else SHELL["base"]) + (255,)
    for _ in range(14):                                 # pits
        px[rnd.randrange(16), rnd.randrange(16)] = SHELL["pit"] + (255,)
    for _ in range(8):                                  # clay stuck low on the shell
        x, y = rnd.randrange(16), 15 - int(rnd.random() ** 1.6 * 5)
        px[x, y] = SHELL["clay"] + (255,)
    if stage >= 2:
        for x, y in ((4, 4), (5, 5), (6, 4), (7, 5), (8, 4), (9, 5), (10, 4), (11, 5)):
            px[x, y] = SHELL["crack"] + (255,)
        for x, y in ((6, 6), (7, 6), (8, 6), (9, 6), (7, 7), (8, 7)):
            px[x, y] = SHELL["down"] + (255,)
        px[6, 7] = SHELL["down2"] + (255,); px[9, 7] = SHELL["down2"] + (255,)
        px[8, 8] = SHELL["beak"] + (255,); px[7, 8] = SHELL["beak"] + (255,)
    return img


def nest():
    """the red clay crust over the buried clutch: dried, cracked into plates, fine sand in the cracks, dry leaves"""
    from PIL import Image
    rnd = random.Random(29)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 3 + y * 11 + (x * y) % 5) % 10
            px[x, y] = (CLAY["c0"] if h == 0 else CLAY["c2"] if h in (2, 5, 8) else CLAY["c3"] if h == 6 else CLAY["c1"]) + (255,)
    # the crack network: three wandering lines that branch, sand showing in their widest part
    for x0, y0, dx, dy, n in ((0, 5, 1, 0, 16), (7, 0, 0, 1, 16), (9, 9, 1, 1, 7), (2, 12, 1, -1, 6)):
        x, y = x0, y0
        for i in range(n):
            if 0 <= x < 16 and 0 <= y < 16:
                px[x, y] = (CLAY["sand"] if i % 5 == 2 else CLAY["crack"]) + (255,)
            x += dx; y += dy
            if rnd.random() < 0.3:
                if dx == 0: x += rnd.choice((-1, 1))
                else: y += rnd.choice((-1, 1))
    for x0, y0 in ((2, 2), (11, 3), (12, 12), (4, 9)):   # dry leaves, each a small lanceolate blade
        for i, c in enumerate(("leaf3", "leaf", "leaf2", "leaf")):
            px[(x0 + i) % 16, (y0 + (i % 2)) % 16] = CLAY[c] + (255,)
    return img


# a round egg: horizontal slices (y from, y to, half width) of a ball 5 px across, sunk into the ground
BALL = [(0.0, 1.0, 1.6), (1.0, 2.0, 2.4), (2.0, 3.6, 2.6), (3.6, 4.6, 2.2), (4.6, 5.2, 1.3)]
EGGS = [(5.0, 6.0), (10.6, 6.6), (7.8, 10.8)]
HATCH = 2
BASE = 1.0


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
    def box(frm, to, bottom=False):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1], bottom=bottom)})
    if stage == 0:
        # only the crust: a low cracked plate, a little domed in the middle where the clutch lies under it
        box([1, 0, 1], [15, BASE, 15], bottom=True)
        box([3, BASE, 3], [13, 1.8, 13]); box([5, 1.8, 5], [11, 2.3, 11])
    else:
        # the crust broken open: plates tilted back round a hole, the tops of the eggs showing in it
        box([1, 0, 1], [15, BASE, 15], bottom=True)
        for frm, to in (([1, BASE, 1], [15, 2.2, 3]), ([1, BASE, 13], [15, 2.0, 15]), ([1, BASE, 3], [3, 2.4, 13]),
                        ([13, BASE, 3], [15, 1.8, 13]), ([3.5, 2.2, 1.5], [8, 2.8, 3])):
            box(frm, to)
        for k, (cx, cz) in enumerate(EGGS):
            els.extend(_ball(cx, cz, 2.0 if k != HATCH else 1.4))
        if stage >= 2:
            cx, cz = EGGS[HATCH]
            top = BASE + BALL[-1][1] - 1.4
            f = {k: {"uv": [6, 6, 10, 8], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
            els.append({"from": [cx - 1.0, top - 0.3, cz - 1.0], "to": [cx + 1.0, top + 1.2, cz + 1.0], "faces": f})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": nest_tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 2.0, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (28, 20, 14), "h": (99, 58, 34), "H": (126, 76, 44), "j": (150, 98, 60),          # outline, hide pad
              "t": (38, 58, 64), "T": (47, 74, 80), "y": (201, 162, 74),                             # teal felt, ochre rim
              "B": (226, 216, 189), "b": (168, 153, 122)}                                            # bone bar
SADDLE_ART = [
    "................",
    "..........ooo...",
    ".........ohhho..",
    ".........ohHho..",
    "..obbbo..ohHho..",
    "..oBBBoooojHho..",
    ".oooooojHHHHHho.",
    "ohHHHjHHHHHjHhho",
    "ohjHHHHHjHHHHHho",
    "oohhhhhhhhhhhhoo",
    "oyyyyyyyyyyyyyyo",
    "otTtTtTtTtTtTtTo",
    "oTtTtTtTtTtTtTto",
    "oyyyyyyyyyyyyyyo",
    ".oooooooooooooo.",
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


CUSTOM_EGGS = {"therizinosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"therizinosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "therizinosaurus_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "therizinosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
