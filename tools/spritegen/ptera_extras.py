"""The Pteranodon's own egg and saddle art (2026-10-29, Rodrigo: "ele tem que ser sela propria e um redesign no ovo
tambem").

Egg (block terrassic:pteranodon_egg, 3 hatch stages): a clutch of two soft, leathery eggs lying half buried in a
scrape of beach sand, with a strand of kelp and a broken shell. Pterosaur eggs were pliable, thin-shelled like a
lizard's, and were buried in sand or soil to incubate (Hamipterus, a colony with hundreds of eggs in Chinese lake
sands; Pterodaustro; Darwinopterus). They are shorter and rounder than a dinosaur egg and dent instead of cracking:
stage 1 shows a dent and creases, stage 2 a tear with the hatchling's beak tip poking out. Pteranodon eggs
themselves are unknown; this is the closest real reference. The block model comes from egg_model()
(tools/javagen/gen_resources.py uses it for the species in CUSTOM_EGGS).

Saddle (item terrassic:pteranodon_saddle): 16x16, drawn like the T. rex saddle (rex_extras: curved seat, blanket band,
things hanging on one side) so the saddles read as one family, but the flyer's own: a low seat on a fish-skin pad, the
wooden grab bar in front, a red crest feather behind the seat and an iron ring (2026-10-31, Rodrigo picked option B
over the first flat-pad version, which read as a table).

usage: python3 -B tools/spritegen/ptera_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (228, 220, 198), "light": (240, 234, 216), "fold": (190, 180, 158), "shade": (172, 162, 140),
         "dent": (150, 140, 120), "tear": (96, 84, 66), "hole": (40, 34, 30), "beak": (196, 178, 135), "beak2": (156, 138, 100)}
SAND = {"sand": (206, 190, 146), "sand2": (190, 172, 128), "sand3": (220, 206, 164), "damp": (166, 148, 108),
        "kelp": (78, 88, 48), "kelp2": (104, 112, 60), "shell": (232, 226, 214), "pebble": (128, 122, 112)}


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(53)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            # soft leather: smooth, lit from above, with faint lengthwise folds
            k = 1.04 - 0.12 * (y / 15.0)
            c = SHELL["base"]
            if (x * 5 + y * 2) % 11 == 0:
                c = SHELL["light"]
            px[x, y] = tuple(min(255, int(v * k)) for v in c) + (255,)
    for _ in range(4):   # a few wrinkles where the leathery shell has sagged
        x, y = rnd.randrange(1, 14), rnd.randrange(3, 14)
        for i in range(rnd.randint(2, 3)):
            px[x + i, y + (i % 2)] = SHELL["fold"] + (255,)
    if stage >= 1:   # a dent: the shell gives instead of cracking
        for x, y in ((6, 6), (7, 6), (8, 6), (9, 7), (5, 7), (6, 8), (7, 8), (8, 8)):
            px[x, y] = SHELL["shade"] + (255,)
        for x, y in ((6, 7), (7, 7), (8, 7)):
            px[x, y] = SHELL["dent"] + (255,)
        for x, y in ((4, 5), (10, 8), (11, 9)):
            px[x, y] = SHELL["fold"] + (255,)
    if stage >= 2:   # a tear, and the hatchling's beak tip poking through
        for x, y in ((5, 6), (10, 6), (5, 9), (10, 9), (4, 8), (11, 7)):
            px[x, y] = SHELL["tear"] + (255,)
        for x, y in ((6, 7), (7, 7), (8, 7), (9, 7), (6, 8), (9, 8)):
            px[x, y] = SHELL["hole"] + (255,)
        for x, y in ((7, 8), (8, 8), (8, 9)):
            px[x, y] = SHELL["beak"] + (255,)
        px[7, 9] = SHELL["beak2"] + (255,)
    return img


def nest():
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(19)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            h = (x * 7 + y * 13 + (x * y) % 5) % 9
            px[x, y] = (SAND["sand2"] if h == 0 else SAND["sand3"] if h == 4 else SAND["sand"]) + (255,)
    for _ in range(5):    # damp patches where the scrape was dug
        x, y = rnd.randrange(16), rnd.randrange(16)
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            px[(x + dx) % 16, (y + dy) % 16] = SAND["damp"] + (255,)
    for x, y in ((2, 3), (3, 3), (4, 4), (5, 4), (6, 5)):   # a strand of kelp
        px[x, y] = SAND["kelp"] + (255,)
    for x, y in ((3, 4), (7, 5)):
        px[x, y] = SAND["kelp2"] + (255,)
    for x, y in ((12, 11), (13, 11), (12, 12)):   # a broken shell
        px[x, y] = SAND["shell"] + (255,)
    for x, y in ((10, 2), (4, 13)):
        px[x, y] = SAND["pebble"] + (255,)
    return img


# an egg lying on its side along x: (x from, x to, radius) slices of a short, round egg 7 long and 5.5 thick
EGG_SLICES = [(0.0, 0.75, 1.5), (0.75, 1.75, 2.25), (1.75, 5.25, 2.75), (5.25, 6.25, 2.25), (6.25, 7.0, 1.5)]


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    # the scrape: a low pad of sand with a heaped rim, the eggs pressed into it
    els.append({"from": [1, 0, 1], "to": [15, 1, 15], "faces": _faces("#nest", 1, 15, 1, 15, 0, 1, bottom=True)})
    for frm, to in (([0, 0, 3], [2, 2, 13]), ([14, 0, 3], [16, 2, 13]), ([3, 0, 0], [13, 1.5, 2]), ([3, 0, 14], [13, 2.5, 16]),
                    ([2, 1, 6], [6, 2, 13]), ([10, 1, 3], [14, 2, 8])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1])})
    # two eggs, one lying along x and one along z, sunk into the sand to about a third of their thickness
    for x0, z0, cy, along_x in ((2.5, 5.0, 2.2, True), (11.0, 6.5, 2.0, False)):
        for a0, a1, r in EGG_SLICES:
            # each slice is a rounded cross: a full-height bar and a full-width bar, the corners cut by a quarter
            for ry, rw in ((r, r * 0.7), (r * 0.7, r)) if r > 2 else ((r, r),):
                y0, y1 = max(0.5, cy - ry), cy + ry
                if along_x:
                    frm, to = [x0 + a0, y0, z0 - rw], [x0 + a1, y1, z0 + rw]
                else:
                    frm, to = [x0 - rw, y0, z0 + a0], [x0 + rw, y1, z0 + a1]
                els.append({"from": frm, "to": to,
                            "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], y0, y1, top=True)})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 2, 0], "scale": [0.85, 0.85, 0.85]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {
    "o": (34, 26, 20),     # outline
    "d": (74, 50, 34),     # dark leather
    "l": (107, 74, 48),    # leather
    "h": (146, 104, 66),   # leather highlight
    "s": (196, 166, 112),  # stitching
    "f": (120, 128, 128),  # fish-skin pad, slate like the model
    "F": (168, 176, 172),  # pad light scale
    "g": (78, 86, 88),     # pad shade
    "w": (118, 88, 56),    # wooden grab bar
    "W": (170, 134, 88),   # bar light
    "i": (110, 110, 106),  # iron ring
    "I": (170, 170, 162),  # iron light
    "c": (182, 64, 30),    # crest feather
    "C": (124, 38, 24),    # crest feather dark
    "y": (236, 178, 84),   # feather tip
}
SADDLE_ART = [
    "................",
    "..oooo......oo..",
    ".oWWWwo....ocyo.",
    "..ooWoo...ocCo..",
    "...oWo....oCo...",
    "...oWo.....ooo..",
    "..ohWhoooohhho..",
    "..odlhhhhhhldo..",
    ".ooddsslllsddoo.",
    ".ogFfFfFfFfFfgo.",
    ".ogfgfgfgfgfggo.",
    "..oggooodgggoo..",
    "....oldo.olIo...",
    "....olho.oIoIo..",
    "....oddo.oIIo...",
    ".....oo...oo....",
]


def saddle_sprite():
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y, row in enumerate(SADDLE_ART):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = SADDLE_PAL[ch] + (255,)
    return img


CUSTOM_EGGS = {"pteranodon": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"pteranodon_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "pteranodon_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "pteranodon_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
