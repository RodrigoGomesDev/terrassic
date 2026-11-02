"""The Gallimimus' own egg and saddle art (2026-11-02, the 1.5 remake; its study page, "Gallimimus: estudo e modelo").

Egg (block terrassic:gallimimus_egg, 3 hatch stages): six long eggs lying in a loose ring, the narrow ends in, in a
shallow scrape on a river GRAVEL BAR. No Gallimimus egg is known: this is the study's hypothesis. The Nemegt was a
land of braided rivers with sand and gravel bars; an open-ground nester there hides its clutch by colour, the way
plovers and terns lay speckled stone-coloured eggs on shingle. Six in a ring is the shape of the clutches of the
oviraptorosaurs and troodontids (Varricchio et al. 1997; Norell et al. 1995): the nearest kin whose nests are known.
The shell is a matte stone grey-beige with fine dark speckles and a few larger blotches toward the blunt end; it
cracks (stage 1: hairline cracks on the egg that hatches first; stage 2: a hole with the chick's pale egg tooth and
a tuft of its dark down).
Kept apart from the other remade clutches: the T. rex's long pair in twigs, the Giganotosaurus' round pale eggs in
cracked mud, the Protoceratops' long pale eggs in red sand, the Carnotaurus' rust pairs on clay, the Triceratops'
olive ovals under leaves.

Saddle (item terrassic:gallimimus_saddle): the riding pad of the model: the madder-red wool blanket with its ochre
rim, the hide pad with the knee roll, the bone grip standing up in front.

usage: python3 -B tools/spritegen/galli_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import math
import os

from rex_extras import TEX, _faces

SHELL = {"base": (150, 142, 124), "light": (170, 162, 142), "shade": (128, 120, 104),
         "fleck": (74, 66, 58), "blot": (96, 84, 70), "crack": (58, 52, 46), "hole": (24, 20, 20),
         "tooth": (232, 226, 210), "down": (40, 42, 52), "down2": (64, 68, 80)}
GRAVEL = {"s0": (150, 136, 108), "s1": (172, 158, 128), "p0": (96, 92, 88), "p1": (124, 118, 110), "p2": (150, 144, 132),
          "o0": (128, 98, 66), "o1": (160, 126, 86), "w0": (196, 190, 178), "gap": (106, 94, 76)}


def _speck(x, y, salt):
    return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xffff


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            k = 1.05 - 0.14 * (y / 15.0)               # lit from above
            c = SHELL["base"]
            if y < 4 and (x + y) % 5 == 0: c = SHELL["light"]
            if y > 12: c = SHELL["shade"]
            px[x, y] = tuple(min(255, int(v * k)) for v in c) + (255,)
    # fine speckles all over (single dark flecks, spaced so no two touch), larger blotches toward the blunt end (x < 6)
    for y in range(16):
        for x in range(16):
            h = _speck(x, y, 7) % 100
            if h < 9 and (x + 2 * y) % 3:
                px[x, y] = SHELL["fleck"] + (255,)
    for bx, by in ((2, 3), (4, 9), (1, 12), (6, 5)):
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            px[bx + dx, by + dy] = SHELL["blot"] + (255,)
    if stage >= 1:                                  # hairline cracks
        for x, y in ((7, 4), (8, 5), (8, 6), (9, 7), (10, 7), (9, 8), (8, 9), (12, 5), (13, 6)):
            px[x, y] = SHELL["crack"] + (255,)
    if stage >= 2:                                  # the hole: the chick's egg tooth and dark down
        for x, y in ((7, 6), (8, 6), (9, 6), (6, 7), (10, 7), (6, 8), (10, 8), (7, 9), (8, 9), (9, 9)):
            px[x, y] = SHELL["hole"] + (255,)
        for x, y in ((7, 7), (8, 7), (7, 8), (9, 8)):
            px[x, y] = SHELL["down"] + (255,)
        px[9, 7] = SHELL["down2"] + (255,); px[8, 8] = SHELL["tooth"] + (255,)
    return img


def nest():
    """a gravel bar: rounded pebbles of grey and ochre lying in coarse sand, each lit on its top and shaded under"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = (GRAVEL["s1"] if _speck(x, y, 3) % 4 else GRAVEL["s0"]) + (255,)
    # pebbles: (x, y, w, h, tone) placed by hand so they never line up
    stones = [(0, 0, 3, 2, "p"), (4, 1, 2, 2, "o"), (8, 0, 3, 3, "p"), (12, 1, 3, 2, "p"), (1, 4, 2, 2, "o"),
              (5, 4, 3, 2, "p"), (10, 5, 2, 2, "w"), (13, 4, 3, 3, "o"), (0, 8, 3, 3, "p"), (4, 8, 2, 2, "p"),
              (7, 7, 3, 3, "o"), (11, 9, 3, 2, "p"), (2, 12, 2, 2, "w"), (5, 12, 3, 3, "p"), (9, 13, 2, 2, "o"),
              (12, 12, 3, 3, "p"), (14, 9, 2, 2, "p")]
    for sx, sy, w, h, tone in stones:
        for j in range(h):
            for i in range(w):
                x, y = sx + i, sy + j
                if x >= 16 or y >= 16 or ((i, j) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)) and w > 2 and h > 2):
                    continue
                if tone == "w": c = GRAVEL["w0"] if j == 0 else GRAVEL["p2"]
                elif tone == "o": c = GRAVEL["o1"] if j == 0 else GRAVEL["o0"]
                else: c = GRAVEL["p2"] if j == 0 else (GRAVEL["p0"] if j == h - 1 else GRAVEL["p1"])
                px[x, y] = c + (255,)
        if sy + h < 16:
            for i in range(1, w):
                if sx + i < 16: px[sx + i, sy + h] = GRAVEL["gap"] + (255,)
    return img


# a long egg lying down: (along from, along to, half width, height) slices, about 1.8 times as long as wide; each slice
# is a rounded cross (a wide low bar and a narrow high bar) so the egg reads round from any side
EGG_SLICES = [(0.0, 1.0, 0.9, 2.0), (1.0, 4.0, 1.5, 3.0), (4.0, 5.2, 1.0, 2.2)]
# six eggs in a loose ring round the middle of the scrape, the narrow ends in: (direction in degrees, sink).
# Block models turn an element only in 22.5 degree steps, so the ring uses the 45 degree directions and leaves two gaps
EGGS = [(0, 0.3), (45, 0.5), (135, 0.4), (180, 0.3), (225, 0.6), (315, 0.4)]
HATCH = 0
FLOOR = 1.0
RING = 2.6


def _egg(theta, sink, squash=1.0):
    els = []
    t = math.radians(theta)
    dx, dz = math.cos(t), math.sin(t)
    axis_x = theta % 180 in (0, 45, 135)       # 0/180 lie along x; the diagonals are x-eggs turned 45 degrees
    angle = {0: 0, 180: 0, 45: -45, 225: -45, 135: 45, 315: 45}[theta]
    L = EGG_SLICES[-1][1]
    ccx, ccz = 8 + dx * (RING + L / 2), 8 + dz * (RING + L / 2)
    outward = 1 if theta in (0, 45, 315) else -1   # the blunt end (slices start) faces out
    for a0, a1, hw, h in EGG_SLICES:
        a0, a1 = (L / 2 - a1, L / 2 - a0) if outward > 0 else (a0 - L / 2, a1 - L / 2)
        for w, hh in ((hw, h * 0.72 * squash), (hw * 0.7, h * squash)):
            y0, y1 = max(0.5, FLOOR - sink), FLOOR - sink + hh
            frm, to = [ccx + a0, y0, ccz - w], [ccx + a1, y1, ccz + w]
            el = {"from": [round(v, 3) for v in frm], "to": [round(v, 3) for v in to],
                  "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], y0, y1, top=True)}
            if angle:
                el["rotation"] = {"origin": [round(ccx, 3), 0.5, round(ccz, 3)], "axis": "y", "angle": angle}
            els.append(el)
    return els


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    # the scrape: a floor of gravel and a low rim heaped round it, open on the two sides of the gaps
    els.append({"from": [1, 0, 1], "to": [15, 1, 15], "faces": _faces("#nest", 1, 15, 1, 15, 0, 1, bottom=True)})
    for frm, to in (([0, 0, 3], [1.5, 1.8, 13]), ([14.5, 0, 3], [16, 1.6, 13]), ([3, 0, 0], [7, 1.5, 1.5]),
                    ([9.5, 0, 14.5], [13, 1.7, 16]), ([1, 1, 1], [3, 1.6, 4]), ([12.5, 1, 11.5], [15, 1.5, 14.5])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1])})
    for i, (theta, sink) in enumerate(EGGS):
        els += _egg(theta, sink, squash=0.9 if stage >= 2 and i == HATCH else 1.0)
    if stage >= 2:   # the chick's egg tooth and down through the hole of the first egg
        theta, sink = EGGS[HATCH]
        cx = 8 + RING + EGG_SLICES[-1][1] / 2
        top = FLOOR - sink + EGG_SLICES[1][3] * 0.9
        f = {k: {"uv": [7, 7, 9, 9], "texture": "#egg"} for k in ("north", "south", "east", "west", "up")}
        els.append({"from": [cx - 0.6, top - 0.3, 7.4], "to": [cx + 0.6, top + 0.7, 8.6], "faces": f})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1.5, 0], "scale": [0.92, 0.92, 0.92]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (30, 20, 16),                                                   # outline
              "r": (94, 56, 40), "R": (138, 82, 54), "q": (112, 67, 46),          # madder-red felt
              "y": (199, 154, 90),                                                 # ochre rim
              "h": (87, 55, 34), "H": (116, 73, 43), "j": (143, 94, 56), "s": (201, 167, 116),   # hide, stitches
              "b": (168, 153, 122), "B": (226, 216, 189)}                          # bone grip
SADDLE_ART = [
    "................",
    "..oo............",
    ".oBbo...........",
    ".oBbo...........",
    ".oBbo...........",
    ".oBboooooooooo..",
    ".oojjjjjjjjjjHo.",
    "ojjHHsHHsHHsHHho",
    "ohhHHHHHHHHHHhho",
    "oyyyyyyyyyyyyyyo",
    "oRRqRRRqRRRRqRRo",
    "orRRRqRRRRqRRRro",
    "oqRRRRRqRRRRRqRo",
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


CUSTOM_EGGS = {"gallimimus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"gallimimus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "gallimimus_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "gallimimus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
