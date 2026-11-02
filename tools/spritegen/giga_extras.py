"""The Giganotosaurus' own egg and saddle art (2026-11-02, Rodrigo: every species its own items, "ovo e sela").

Egg (block terrassic:giganotosaurus_egg, 3 hatch stages): a clutch of seven round, smooth eggs heaped in a wide pit
dug into the dried mud of a river plain, the mud round it cracked into plates, and a shed blade tooth by the rim.
Giganotosaurus was a carcharodontosaurid, an allosauroid; the only allosauroid clutch known (Lourinhanosaurus,
Portugal, with embryos) has many smooth eggs that are rounder than other theropod eggs, and the Candeleros Formation
it lived in was a land of rivers and dunes. Carcharodontosaurid eggs themselves are unknown; this is the closest
real reference. The shell is pale grey with a faint blue, like the animal's off-white belly. Different from the other
clutches: long eggs everywhere else (the T. rex pair, the Velociraptor's ring, the Carnotaurus' pairs on salt
clay, the Protoceratops' soft eggs in red sand); only these are round and heaped.

Saddle (item terrassic:giganotosaurus_saddle): 16x16, drawn like the T. rex saddle (rex_extras) so the saddles read
as one family, but the Giganotosaurus' own, the recado of its model (giga.py saddle()): the woven wool jerga with its
stepped wine and black band, the two dark leather rolls (bastos), the tan capybara-hide seat over them and a carved
wooden bell stirrup.

usage: python3 -B tools/spritegen/giga_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

from rex_extras import TEX, _faces

SHELL = {"base": (196, 206, 212), "light": (218, 226, 230), "shade": (166, 178, 186), "fleck": (146, 158, 168),
         "crack": (52, 58, 64), "hole": (22, 24, 28), "chick": (102, 116, 126), "chick2": (78, 90, 100),
         "tooth": (240, 236, 220)}
MUD = {"m0": (150, 120, 88), "m1": (166, 134, 98), "m2": (182, 150, 112), "gap": (92, 70, 50), "gap2": (118, 92, 66),
       "pit": (120, 94, 68), "pit2": (106, 82, 58), "tooth": (232, 226, 206), "tooth2": (190, 180, 154)}


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(83)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            k = 1.04 - 0.14 * (y / 15.0)       # smooth, lit from above
            c = SHELL["light"] if y < 4 and (x + y) % 3 == 0 else SHELL["base"]
            px[x, y] = tuple(min(255, int(v * k)) for v in c) + (255,)
    for _ in range(7):    # a few faint flecks: a smooth shell, almost bare
        x, y = rnd.randrange(16), rnd.randrange(16)
        px[x, y] = SHELL["fleck"] + (255,)
    if stage >= 1:
        for x, y in ((6, 4), (7, 5), (8, 5), (9, 4), (8, 6), (10, 5)):
            px[x, y] = SHELL["crack"] + (255,)
    if stage >= 2:        # a hole with the chick's grey snout and the white egg tooth
        for x, y in ((6, 5), (7, 4), (9, 6), (10, 6), (7, 6), (6, 6)):
            px[x, y] = SHELL["hole"] + (255,)
        for x, y in ((7, 5), (8, 5), (8, 6)):
            px[x, y] = SHELL["chick"] + (255,)
        px[9, 5] = SHELL["chick2"] + (255,)
        px[8, 4] = SHELL["tooth"] + (255,)
    return img


def nest():
    """the dried river mud cracked into plates (the pit's inner walls use the same texture)"""
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(29)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = (MUD["m1"] if (x * 5 + y * 3) % 7 else MUD["m2"]) + (255,)
    # the cracks between the plates: a few crooked lines that meet, a lit lip on the plate below each
    cracks = [[(0, 4), (1, 4), (2, 5), (3, 5), (4, 5), (5, 6), (6, 6)], [(6, 6), (7, 7), (7, 8), (8, 9), (8, 10), (9, 11), (9, 12), (10, 13), (10, 14), (10, 15)],
              [(6, 6), (7, 5), (8, 4), (9, 4), (10, 3), (11, 3), (12, 2), (13, 2), (14, 1), (15, 1)],
              [(8, 9), (9, 9), (10, 8), (11, 8), (12, 9), (13, 9), (14, 10), (15, 10)], [(4, 5), (4, 6), (3, 7), (3, 8), (2, 9), (2, 10), (1, 11), (1, 12), (0, 13)],
              [(3, 8), (4, 9), (5, 10), (5, 11), (6, 12), (6, 13), (7, 14), (7, 15)], [(11, 3), (11, 2), (11, 1), (11, 0)]]
    for crack in cracks:
        for x, y in crack:
            px[x, y] = MUD["gap"] + (255,)
            if y + 1 < 16 and px[x, y + 1][:3] != MUD["gap"]:
                px[x, y + 1] = MUD["m2"] + (255,)
    for _ in range(5):
        x, y = rnd.randrange(16), rnd.randrange(16)
        if px[x, y][:3] != MUD["gap"]:
            px[x, y] = MUD["m0"] + (255,)
    return img


def tooth_tex():
    """the shed blade tooth (the carcharodontosaur's 'shark tooth'), on its own small element"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = (MUD["tooth"] if x < 8 else MUD["tooth2"]) + (255,)
    return img


# a round egg: (y from, y to, half width) slices, about 1.2 times as tall as wide
EGG_SLICES = [(0.0, 0.6, 1.2), (0.6, 2.8, 1.8), (2.8, 3.6, 1.4), (3.6, 4.1, 0.9)]
# seven eggs heaped in the pit: a ring of six on the floor and one on top of them (x, z, y base)
EGGS = [(4.6, 5.2, 0.6), (8.4, 3.8, 0.6), (11.8, 6.0, 0.6), (11.4, 10.6, 0.6), (7.6, 12.2, 0.6), (4.2, 9.6, 0.6),
        (8.0, 8.0, 1.6)]


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    els = []
    # the pit: a floor sunk below a raised rim of dried mud plates, broken at the front
    els.append({"from": [2, 0, 2], "to": [14, 0.6, 14], "faces": _faces("#nest", 2, 14, 2, 14, 0, 0.6, bottom=True)})
    for frm, to in (([0, 0, 1], [2, 2.2, 15]), ([14, 0, 1], [16, 2.0, 15]), ([2, 0, 0], [14, 2.4, 2]),
                    ([2, 0, 14], [6, 1.8, 16]), ([9, 0, 14], [14, 2.0, 16]), ([6, 0, 14.5], [9, 1.0, 16]),
                    ([1, 2.0, 3], [2.5, 2.8, 7]), ([13.5, 1.8, 9], [15, 2.6, 13])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1],
                                                            bottom=frm[1] == 0)})
    for x0, z0, b in EGGS:
        for y0, y1, r in EGG_SLICES:
            for rx, rz in ((r, r * 0.7), (r * 0.7, r)):
                frm, to = [x0 - rx, b + y0, z0 - rz], [x0 + rx, b + y1, z0 + rz]
                els.append({"from": frm, "to": to, "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], frm[1], to[1], top=True)})
    # the shed tooth lying on the rim: a flat curved blade, two little steps
    for frm, to in (([12.0, 2.0, 2.4], [14.4, 2.4, 3.4]), ([14.4, 2.0, 2.6], [15.4, 2.3, 3.2])):
        els.append({"from": frm, "to": to, "faces": _faces("#tooth", frm[0], to[0], frm[2], to[2], frm[1], to[1])})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": f"terrassic:block/{sid}_nest",
                                                  "tooth": f"terrassic:block/{sid}_tooth", "particle": tex},
            "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {
    "o": (30, 22, 18),     # outline
    "C": (180, 139, 90),   # capybara seat light
    "c": (156, 116, 73),   # capybara seat
    "k": (122, 86, 54),    # seat shade
    "L": (99, 65, 42),     # basto leather light
    "l": (74, 48, 32),     # basto leather
    "W": (205, 189, 153),  # wool light
    "w": (169, 148, 111),  # wool natural
    "r": (107, 43, 40),    # wool wine
    "n": (46, 36, 32),     # wool black-brown
    "D": (155, 114, 70),   # carved wood light
    "d": (94, 65, 41),     # carved wood
    "s": (62, 42, 27),     # stirrup leather
}
SADDLE_ART = [
    "................",
    "................",
    "................",
    "..oo........oo..",
    ".oLlo......oLlo.",
    ".olloooooooollo.",
    ".olCCCCCCCCCClo.",
    ".ookcccccccckoo.",
    "oWWwWWwWWwWWwWWo",
    "onrnnrnnrnnrnnro",
    "orrnrrnrrnrrnrro",
    "owWwwWwwWwwWwwWo",
    ".oowwWwooowWwoo.",
    "...ooooosoooo...",
    ".......oDDo.....",
    "......odddDo....",
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


CUSTOM_EGGS = {"giganotosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"giganotosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "giganotosaurus_nest.png"))
    save_png(tooth_tex(), os.path.join(TEX, "block", "giganotosaurus_tooth.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "giganotosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
