"""The Pachycephalosaurus' own egg art (2026-11-02, the 1.5 remake; its study page, "Paquicefalossauro: estudo e
modelo"). It has no saddle: it is not rideable (the study says why), so there is no saddle item.

Egg (block terrassic:pachycephalosaurus_egg, 3 hatch stages): four short, round, SOFT eggs pressed in among the roots
at the foot of a tree, half buried in loose dark soil under a litter of conifer needles. No pachycephalosaur egg is
known: this is the study's hypothesis. Its nearest kin with known eggs, the Protoceratops (a marginocephalian like
it), laid soft leathery eggs that were buried and warmed by the ground (Norell et al. 2020); the Hell Creek country
was a wooded floodplain, and in the mod it lives in the conifer woods and on the hills, so the clutch goes under the
forest floor where roots hold the soil. The shell is a dull chalky white going grey, never glossy, with brown soil
stains low down; being soft it does not crack: stage 1 it slumps and wrinkles, stage 2 it tears and the chick's
flat, spiky little head shows (the young had spikes and no dome: Horner & Goodwin 2009).
Kept apart from the other remade clutches: the T. rex's long pair in twigs, the Giganotosaurus' round pale eggs in
cracked mud, the Protoceratops' long eggs in a ring in red sand, the Carnotaurus' rust pairs on clay, the
Triceratops' olive ovals under leaves, the Gallimimus' speckled ring on gravel.

usage: python3 -B tools/spritegen/pachy_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os

from rex_extras import TEX, _faces

SHELL = {"base": (206, 200, 186), "light": (222, 217, 204), "shade": (176, 170, 156), "fold": (150, 144, 130),
         "stain": (132, 108, 82), "stain2": (108, 86, 64), "tear": (70, 54, 44), "inside": (40, 30, 26),
         "skin": (160, 104, 38), "skin2": (125, 76, 20), "spike": (58, 44, 34)}
FLOOR = {"s0": (46, 34, 26), "s1": (62, 46, 34), "s2": (80, 60, 42),            # loose dark soil
         "n0": (110, 74, 40), "n1": (140, 98, 52), "n2": (92, 60, 34),          # fallen needles, rust and brown
         "g0": (66, 82, 44),                                                    # a few still green
         "b0": (58, 42, 30), "b1": (84, 62, 44), "b2": (108, 82, 58), "b3": (44, 32, 24)}   # root bark (last 4 rows)


def _h(x, y, salt):
    return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xffff


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            c = SHELL["light"] if y < 4 else (SHELL["base"] if y < 11 else SHELL["shade"])
            # the soft shell's faint wrinkles: short lines that wander, not a grid
            if (x + (y // 3) * 2) % 7 == 0 and _h(x, y, 2) % 3 == 0 and 3 < y < 13:
                c = SHELL["shade"]
            px[x, y] = c + (255,)
    # soil stains low down on the shell (it lay buried), uneven blots
    for (x, y) in ((1, 13), (2, 13), (2, 14), (5, 14), (6, 14), (6, 15), (10, 13), (11, 14), (12, 14), (14, 15),
                   (3, 15), (9, 15)):
        px[x, y] = (SHELL["stain"] if _h(x, y, 5) % 3 else SHELL["stain2"]) + (255,)
    if stage >= 1:   # a soft egg does not crack: it slumps, and folds show
        for (x, y) in ((4, 6), (5, 7), (6, 7), (7, 8), (11, 5), (11, 6), (12, 7), (9, 10), (10, 10)):
            px[x, y] = SHELL["fold"] + (255,)
    if stage >= 2:   # the tear, and the chick's flat head with its little spikes
        for (x, y) in ((6, 5), (7, 5), (8, 5), (9, 5), (5, 6), (10, 6), (5, 7), (10, 7), (6, 8), (9, 8)):
            px[x, y] = SHELL["tear"] + (255,)
        for (x, y) in ((6, 6), (9, 6), (6, 7), (9, 7), (7, 8), (8, 8)):
            px[x, y] = SHELL["inside"] + (255,)
        for (x, y) in ((7, 6), (8, 6), (7, 7), (8, 7)):
            px[x, y] = (SHELL["skin"] if y == 6 else SHELL["skin2"]) + (255,)
        px[7, 5] = SHELL["spike"] + (255,); px[9, 5] = SHELL["spike"] + (255,)
    return img


def nest():
    """the forest floor: loose dark soil scattered with fallen needles (single needles lie as 2-3 px strokes in
    different directions, rust and brown, a rare green one); the bottom four rows are the bark of the root"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(12):
        for x in range(16):
            k = _h(x, y, 3) % 5
            px[x, y] = (FLOOR["s1"] if k else FLOOR["s0"]) + (255,)
            if k == 4 and _h(x, y, 9) % 2: px[x, y] = FLOOR["s2"] + (255,)
    needles = [(1, 1, 1, 0, 3, "n1"), (6, 0, 1, 1, 3, "n0"), (11, 1, 0, 1, 3, "n2"), (3, 4, 1, -1, 3, "n0"),
               (8, 4, 1, 0, 2, "n1"), (13, 3, 1, 1, 2, "n1"), (0, 7, 0, 1, 3, "n2"), (5, 7, 1, 1, 3, "n1"),
               (10, 7, 1, 0, 3, "g0"), (14, 6, 0, 1, 3, "n0"), (2, 10, 1, 0, 3, "n0"), (8, 9, 1, -1, 3, "n2")]
    for x, y, dx, dy, n, c in needles:
        for i in range(n):
            xx, yy = x + dx * i, y + dy * i
            if 0 <= xx < 16 and 0 <= yy < 12:
                px[xx, yy] = FLOOR[c] + (255,)
    # bark: rough vertical fissures running along the root
    for y in range(12, 16):
        for x in range(16):
            c = FLOOR["b1"]
            if y == 12: c = FLOOR["b2"]
            if y == 15: c = FLOOR["b0"]
            if (x + _h(x // 4, 0, 7) % 3) % 5 == 0 and y in (13, 14): c = FLOOR["b3"]
            px[x, y] = c + (255,)
    return img


# a short round egg standing a little tilted in the soil: (y from, y to, half width) slices of a rounded cross
EGG_ROWS = [(0.0, 0.8, 1.2), (0.8, 3.6, 2.0), (3.6, 4.6, 1.4), (4.6, 5.0, 0.8)]
# four eggs among the roots: (centre x, centre z, sink, scale); the one that hatches first is the first
EGGS = [(6.0, 8.5, 1.5, 1.0), (10.8, 8.0, 1.7, 0.95), (8.2, 12.6, 1.6, 1.0), (12.8, 12.4, 1.9, 0.9)]
HATCH = 0
SOIL = 1.6


def _egg(cx, cz, sink, k, slump=1.0):
    els = []
    for y0, y1, hw in EGG_ROWS:
        a, b = SOIL - sink + y0 * k * slump, SOIL - sink + y1 * k * slump
        if b <= SOIL:
            continue
        a = max(a, SOIL - 0.5)
        for w, d in ((hw * k, hw * k * 0.7), (hw * k * 0.7, hw * k)):
            frm, to = [cx - w, a, cz - d], [cx + w, b, cz + d]
            els.append({"from": [round(v, 3) for v in frm], "to": [round(v, 3) for v in to],
                        "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], frm[1], to[1], top=True)})
    return els


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    # the soil and its needle litter, heaped a little toward the root
    els.append({"from": [0, 0, 0], "to": [16, 1, 16], "faces": _faces("#nest", 0, 16, 0, 16, 0, 1, bottom=True)})
    els.append({"from": [3, 1, 4.5], "to": [15, 1.6, 15], "faces": _faces("#nest", 3, 15, 4.5, 15, 1, 1.6)})
    # the root: a thick bar along the north side, with a smaller one branching across the west side
    bark = lambda frm, to: {k: {"uv": [0, 12, 16, 16], "texture": "#nest"} for k in ("north", "south", "east", "west", "up")}
    els.append({"from": [0, 0.5, 1.5], "to": [16, 3.5, 4.5], "faces": bark(None, None)})
    els.append({"from": [12, 3.5, 2], "to": [16, 4.5, 4], "faces": bark(None, None)})      # the swelling toward the trunk
    els.append({"from": [1, 0.5, 5], "to": [3, 2.5, 15], "faces": bark(None, None)})
    for i, (cx, cz, sink, k) in enumerate(EGGS):
        els += _egg(cx, cz, sink, k, slump=0.85 if stage >= 1 and i == HATCH else 1.0)
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1.5, 0], "scale": [0.92, 0.92, 0.92]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


CUSTOM_EGGS = {"pachycephalosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"pachycephalosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "pachycephalosaurus_nest.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
