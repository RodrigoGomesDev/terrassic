"""The Parasaurolophus' own egg and saddle art (2026-11-02, the 1.5 remake; its study page, "Parassaurolofo: estudo e
modelo").

Egg (block terrassic:parasaurolophus_egg, 3 hatch stages): five nearly ROUND eggs in a raised crater of packed mud on
the floodplain, a few reed stems laid over them. No Parasaurolophus egg is known: this is the study's hypothesis, from
its nearest kin. The lambeosaurine Hypacrosaurus laid near-spherical eggs about 20 cm across (Devil's Coulee, Horner &
Currie 1994) and the hadrosaurs nested in colonies in bowl-shaped mounds of earth with a raised rim (Maiasaura, Horner
& Makela 1979), the clutch covered with plants that warm it as they rot. Unlike the soft eggs of the early ornithischians
(Norell et al. 2020) the hadrosaurs' shells were hard, of calcite, with a nodular surface (spheroolithid eggshell), and
the ornithischian eggs studied for colour show no pigment (Wiemann et al. 2018): so a dull chalk-white shell with low
nodes, smeared with the mud of the nest. It cracks (stage 1: a crack across the egg that hatches first; stage 2: a hole
with the hatchling's low rufous dome and its small dark bill).
Kept apart from the other remade clutches: the T. rex's long pair in twigs, the Giganotosaurus' round pale blue-grey
eggs sunk in a cracked mud PIT, the Protoceratops' long pale eggs in red sand, the Carnotaurus' rust pairs on clay,
the Triceratops' olive ovals under leaves, the Gallimimus' speckled ring on gravel, the Pachycephalosaurus' soft eggs
among roots. This one is a raised crater, white nodular eggs, reeds across.

Saddle (item terrassic:parasaurolophus_saddle): the reed saddle of the model: the woven rush mat (a twill, green-gold),
the hide seat with its rolled cantle, a rolled bundle of matting strapped along the side with cord, the plaited neck
rope in front. No wood frame, no felt, no metal.

usage: python3 -B tools/spritegen/para_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os

from rex_extras import TEX, _faces

SHELL = {"base": (214, 206, 186), "light": (232, 226, 210), "shade": (186, 176, 156), "node": (240, 236, 222),
         "node_s": (170, 160, 140), "mud": (120, 98, 74), "mud2": (98, 80, 62), "crack": (88, 76, 64),
         "hole": (30, 22, 18), "dome": (160, 82, 31), "dome2": (192, 106, 44), "bill": (55, 48, 45)}
MUD = {"m0": (70, 54, 42), "m1": (88, 70, 54), "m2": (108, 88, 68), "m3": (128, 106, 82), "drag": (60, 46, 36),
       "r0": (74, 74, 42), "r1": (103, 101, 58), "r2": (133, 129, 75), "r3": (163, 157, 97), "node": (88, 86, 50)}


def _h(x, y, salt):
    return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xffff


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            c = SHELL["base"]
            if y < 4: c = SHELL["light"]
            if y > 11: c = SHELL["shade"]
            px[x, y] = c + (255,)
    # the low nodes of the shell: a lit pixel with its shadow under it, scattered by hand (never a grid)
    for x, y in ((2, 2), (6, 1), (11, 3), (14, 1), (4, 6), (9, 5), (13, 7), (1, 9), (7, 9), (11, 10), (3, 13), (9, 13), (14, 12)):
        px[x, y] = SHELL["node"] + (255,)
        if y + 1 < 16: px[x, y + 1] = SHELL["node_s"] + (255,)
    # mud smeared on the lower part (the egg sits in the crater)
    for y in range(11, 16):
        for x in range(16):
            if _h(x, y, 5) % 5 < (y - 10):
                px[x, y] = (SHELL["mud"] if (x + y) % 3 else SHELL["mud2"]) + (255,)
    if stage >= 1:                                   # a crack across the top
        for x, y in ((3, 5), (4, 5), (5, 6), (6, 6), (7, 5), (8, 6), (9, 7), (10, 7), (11, 6), (12, 6)):
            px[x, y] = SHELL["crack"] + (255,)
    if stage >= 2:                                   # the hole: the hatchling's low rufous dome and its dark bill
        for x, y in ((6, 4), (7, 4), (8, 4), (9, 4), (5, 5), (10, 5), (5, 6), (10, 6), (6, 7), (9, 7)):
            px[x, y] = SHELL["hole"] + (255,)
        for x, y in ((6, 5), (7, 5), (8, 5), (9, 5), (7, 6), (8, 6)):
            px[x, y] = SHELL["dome"] + (255,)
        px[7, 5] = SHELL["dome2"] + (255,)
        px[6, 6] = SHELL["bill"] + (255,); px[9, 6] = SHELL["bill"] + (255,)
    return img


def nest():
    """the nest atlas: packed floodplain mud with drag marks (rows 3-15), and a band of reed stems (rows 0-2) that the
    stems laid over the clutch take their faces from"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            if y < 3:       # the reed band: a lit top row, the stem, its shaded under side; a node every few px
                c = (MUD["r3"], MUD["r2"], MUD["r1"])[y]
                if x in (4, 11) and y > 0: c = MUD["node"]
                px[x, y] = c + (255,)
                continue
            k = _h(x, y, 9) % 7
            c = MUD["m2"] if k > 2 else (MUD["m1"] if k > 0 else MUD["m3"])
            px[x, y] = c + (255,)
    # drag marks of the parent's bill heaping the rim: short curved strokes, each a dark line with a lit edge above
    for pts in (((2, 5), (3, 5), (4, 6)), ((9, 4), (10, 4), (11, 5), (12, 5)), ((5, 9), (6, 10), (7, 10)),
                ((11, 11), (12, 11), (13, 12)), ((1, 13), (2, 13)), ((7, 14), (8, 14), (9, 13))):
        for x, y in pts:
            px[x, y] = MUD["drag"] + (255,)
            if y - 1 >= 3: px[x, y - 1] = MUD["m3"] + (255,)
    return img


# a round egg: rounded-cross slices (a wide low bar and a narrow high bar per height band), about 4.4 px across (about 20 cm, like Hypacrosaurus)
ROUND = [(0.0, 1.0, 1.4), (1.0, 3.2, 2.2), (3.2, 4.2, 1.4)]      # (y from, y to, half width) from the egg's bottom
# five eggs in the crater: two in front, one in the middle (the first to hatch), two at the back, sunk a little in the mud
EGGS = [(4.8, 4.8, 0.5), (10.8, 5.0, 0.7), (7.8, 8.6, 0.4), (4.4, 11.6, 0.6), (11.0, 11.8, 0.7)]
HATCH = 2
FLOOR = 1.0
# reed stems laid across the clutch: (from x, from z, to x, to z, y, angle)
REEDS = [(2.0, 7.4, 14.0, 8.2, 4.7, 22.5), (1.5, 10.2, 13.5, 11.0, 4.5, -22.5), (3.0, 4.6, 13.0, 5.4, 4.3, 0)]


def _egg(cx, cz, sink, squash=1.0):
    """one round egg as a rounded cross per height band: a bar wide in x (a little lower and higher than the band's
    ends trimmed) and a bar wide in z (the band's full height), so the silhouette reads round from any side"""
    els = []
    for y0, y1, hw in ROUND:
        for wide_x in (True, False):
            trim = 0.15 if wide_x else 0.0
            a0 = max(0.5, FLOOR - sink + (y0 + trim) * squash)
            a1 = FLOOR - sink + (y1 - trim) * squash
            if a1 <= a0:
                continue
            wx, wz = (hw, hw * 0.62) if wide_x else (hw * 0.62, hw)
            frm, to = [cx - wx, a0, cz - wz], [cx + wx, a1, cz + wz]
            els.append({"from": [round(v, 3) for v in frm], "to": [round(v, 3) for v in to],
                        "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], a0, a1, top=True)})
    return els


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    # the crater: a floor of packed mud and a raised rim heaped all round, highest at the back
    els.append({"from": [1.5, 0, 1.5], "to": [14.5, 1, 14.5], "faces": _faces("#nest", 1.5, 14.5, 1.5, 14.5, 0, 1, bottom=True)})
    for frm, to in (([0, 0, 2], [1.5, 2.6, 14]), ([14.5, 0, 2.5], [16, 2.4, 13.5]), ([2, 0, 0], [14, 2.0, 1.5]),
                    ([2.5, 0, 14.5], [13.5, 3.0, 16]), ([0.6, 0, 0.6], [2.4, 2.2, 2.4]), ([13.6, 0, 13.6], [15.4, 2.8, 15.4]),
                    ([13.6, 0, 0.6], [15.4, 2.0, 2.4]), ([0.6, 0, 13.6], [2.4, 2.6, 15.4])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1])})
    for i, (cx, cz, sink) in enumerate(EGGS):
        els += _egg(cx, cz, sink, squash=0.88 if stage >= 2 and i == HATCH else 1.0)
    # the reed stems over the clutch (the hatchling's egg uncovered by stage 1: the parent pulled one stem away)
    for k, (x0, z0, x1, z1, y, angle) in enumerate(REEDS):
        if stage >= 1 and k == 0:
            continue
        cz = (z0 + z1) / 2
        f = {}
        for name in ("north", "south", "east", "west"):
            f[name] = {"uv": [0, 1, 12 if name in ("north", "south") else 1, 2], "texture": "#nest"}
        f["up"] = {"uv": [x0, 0, x1, 1], "texture": "#nest"}
        f["down"] = {"uv": [x0, 2, x1, 3], "texture": "#nest"}
        el = {"from": [x0, y, cz - 0.4], "to": [x1, y + 0.8, cz + 0.4], "faces": f}
        if angle:
            el["rotation"] = {"origin": [(x0 + x1) / 2, y, cz], "axis": "y", "angle": angle}
        els.append(el)
    if stage >= 1:   # the pulled stem, lying on the rim
        f = {n: {"uv": [0, 1, 10, 2], "texture": "#nest"} for n in ("north", "south", "east", "west")}
        f["up"] = {"uv": [2, 0, 12, 1], "texture": "#nest"}
        els.append({"from": [3.0, 2.6, 14.6], "to": [13.0, 3.4, 15.4], "faces": f})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1.5, 0], "scale": [0.92, 0.92, 0.92]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (30, 26, 18),                                                              # outline
              "r": (103, 101, 58), "R": (133, 129, 75), "y": (163, 157, 97), "q": (74, 74, 42),  # woven rush
              "h": (90, 65, 48), "H": (118, 87, 65), "j": (146, 112, 79), "s": (127, 106, 75),   # hide, lacing
              "m": (84, 80, 47), "M": (114, 108, 63), "N": (148, 139, 85),                       # rolled matting
              "c": (91, 74, 52), "C": (127, 106, 75)}                                            # plaited cord
SADDLE_ART = [   # side view: the rolled cantle at the back, the hide seat, the rush mat in twill (diagonals, never a
    "................",   # checker), the plaited neck rope hanging in front, the rolled bundle with its round end below
    "................",
    "............oo..",
    "...........oNMo.",
    "..ooooooooooMNo.",
    ".oHHjjHHjjHHHmo.",
    "oCoyRRyRRyRRyRo.",
    "oCoRyRRyRRyRRyo.",
    ".oCRRyRRyRRyRRo.",
    ".oCyRRyRRyRRyqo.",
    ".ooqqqqqqqqqqqo.",
    "oNMoMNMCMNMCMMo.",
    "oMmoNNMCNNMCNMo.",
    "oNMomMmcmMmcmmo.",
    ".ooooooooooooo..",
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


CUSTOM_EGGS = {"parasaurolophus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"parasaurolophus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "parasaurolophus_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "parasaurolophus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
