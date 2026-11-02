"""The Ankylosaurus' own egg and saddle art (2026-11-02, the 1.5 remake; its study page, "Anquilossauro 1.5").

Egg (block terrassic:ankylosaurus_egg, 3 hatch stages): eight small round eggs with a SOFT, leathery shell, half
buried in two layers in a low heap of dark forest loam and leaf litter, a few fern fronds stuck in over them. No
ankylosaur egg is known: this is the study's hypothesis. The early ornithischians laid soft-shelled eggs (Protoceratops,
Norell et al. 2020) and a soft egg has to be buried in damp soil or it dries out, so the clutch is covered, not laid in
the open; the shell is dull, creased and dented where it gave under the loam, and pale with no pigment (Wiemann et al.
2018). A soft egg does not crack: it tears (stage 1: a slit along the egg that hatches first; stage 2: the slit opened,
the hatchling's teal-grey snout and its small dark beak showing).
Kept apart from the other remade clutches: the T. rex's long pair in twigs, the Giganotosaurus' pale blue-grey eggs in
a cracked mud pit, the Protoceratops' long pale eggs in red sand, the Carnotaurus' rust pairs on clay, the Triceratops'
olive ovals under leaves, the Gallimimus' speckled ring on gravel, the Pachycephalosaurus' soft eggs among roots, the
Parasaurolophus' white nodular eggs in a raised mud crater. This one is a dark heap, eggs mostly buried, ferns on top.

Saddle (item terrassic:ankylosaurus_saddle): the pack deck of the model: two peeled poles along the back with slats
lashed across them, the bark-cloth cushion with its painted dark band at the front, a bale of smoked hide hanging on
the side, the tie-down cord running down to the flank plates (no girth: nothing goes under the belly). No A-frame, no
felt, no rush, no metal.

usage: python3 -B tools/spritegen/anky_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os

from rex_extras import TEX, _faces

SHELL = {"base": (206, 200, 184), "light": (224, 219, 205), "shade": (178, 170, 152), "crease": (160, 150, 132),
         "crease_l": (232, 228, 216), "loam": (58, 46, 36), "loam2": (78, 62, 46), "slit": (40, 30, 26),
         "lip": (150, 140, 120), "snout": (67, 89, 87), "snout2": (88, 113, 109), "beak": (50, 45, 38)}
LOAM = {"l0": (36, 28, 22), "l1": (50, 39, 30), "l2": (64, 51, 39), "l3": (80, 65, 49),
        "leaf": (98, 70, 40), "leaf2": (120, 88, 50),
        "f0": (38, 64, 32), "f1": (56, 90, 44), "f2": (82, 120, 58), "f3": (110, 146, 76)}


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
            if y > 10: c = SHELL["shade"]
            px[x, y] = c + (255,)
    # the creases of a soft shell: short bent strokes, a dark fold with a lit edge above it (dents where it gave)
    for pts in (((2, 3), (3, 4), (4, 4)), ((9, 2), (10, 3)), ((12, 6), (13, 6), (14, 7)), ((5, 8), (6, 9)),
                ((1, 11), (2, 11)), ((10, 10), (11, 11), (12, 11))):
        for x, y in pts:
            px[x, y] = SHELL["crease"] + (255,)
            if y - 1 >= 0: px[x, y - 1] = SHELL["crease_l"] + (255,)
    # loam stuck to the lower half (it is dug out of the heap)
    for y in range(12, 16):
        for x in range(16):
            if _h(x, y, 3) % 6 < (y - 11):
                px[x, y] = (SHELL["loam"] if (x * 3 + y) % 4 else SHELL["loam2"]) + (255,)
    if stage >= 1:                                   # a soft egg tears: a slit along the top, its lips pushed out
        for x in range(4, 12):
            px[x, 5] = SHELL["slit"] + (255,)
            px[x, 4] = SHELL["lip"] + (255,)
    if stage >= 2:                                   # the slit opened: the hatchling's teal-grey snout and dark beak
        for x, y in ((4, 6), (5, 6), (10, 6), (11, 6), (4, 7), (11, 7), (5, 8), (10, 8)):
            px[x, y] = SHELL["slit"] + (255,)
        for x, y in ((5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (6, 6), (7, 6), (8, 6), (9, 6), (6, 7), (9, 7)):
            px[x, y] = SHELL["snout"] + (255,)
        px[7, 5] = SHELL["snout2"] + (255,); px[8, 5] = SHELL["snout2"] + (255,)
        px[7, 7] = SHELL["beak"] + (255,); px[8, 7] = SHELL["beak"] + (255,)
    return img


def nest():
    """the nest atlas: dark forest loam with bits of leaf litter (rows 3-15), and a band of fern frond (rows 0-2) that
    the fronds stuck in over the clutch take their faces from"""
    from PIL import Image
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            if y < 3:       # the frond: the lit upper edge, the leaflets, the dark midrib under; leaflets every other px
                c = (LOAM["f3"] if x % 2 else LOAM["f2"], LOAM["f1"] if x % 2 else LOAM["f2"], LOAM["f0"])[y]
                px[x, y] = c + (255,)
                continue
            k = _h(x, y, 11) % 9
            c = LOAM["l1"] if k > 4 else (LOAM["l2"] if k > 1 else (LOAM["l0"] if k else LOAM["l3"]))
            px[x, y] = c + (255,)
    # leaf litter: a few curled brown leaves, each two or three px with a lit tip (scattered by hand, never a grid)
    for pts in (((2, 5), (3, 5)), ((10, 4), (11, 5)), ((6, 8), (7, 8), (7, 9)), ((13, 9), (14, 9)),
                ((3, 12), (4, 13)), ((9, 12), (10, 12)), ((12, 14), (13, 14), (13, 15))):
        for i, (x, y) in enumerate(pts):
            px[x, y] = (LOAM["leaf2"] if i == 0 else LOAM["leaf"]) + (255,)
    return img


# a small round egg (about 18 cm: smaller than the hadrosaurs' and soft): rounded-cross slices per height band
ROUND = [(0.0, 0.9, 1.3), (0.9, 2.9, 2.0), (2.9, 3.8, 1.3)]       # (y from, y to, half width) from the egg's bottom
# eight eggs in two layers: five below, sunk deep in the heap (only their tops show), three above in the middle,
# sunk to half; the one that hatches first is on top
EGGS = [(3.6, 4.0, 1.7), (12.2, 4.2, 1.8), (3.4, 11.6, 1.9), (12.4, 12.0, 1.7), (8.0, 13.6, 2.0),
        (5.8, 7.4, 0.5), (10.4, 7.8, 0.6), (8.0, 10.6, 0.4)]
HATCH = 6
FLOOR = 3.0
# fern fronds stuck in the heap over the clutch, leaning out: (from x, from z, to x, to z, y, angle about y)
FRONDS = [(2.0, 3.4, 9.0, 3.4, 4.4, 22.5), (7.5, 12.6, 14.0, 12.6, 4.2, -22.5), (9.5, 3.0, 14.5, 3.0, 4.0, 45)]


def _egg(cx, cz, sink, squash=1.0):
    """one round egg as a rounded cross per height band, sunk in the heap (the parts under the loam are left out)"""
    els = []
    for y0, y1, hw in ROUND:
        for wide_x in (True, False):
            trim = 0.15 if wide_x else 0.0
            a0 = max(FLOOR - 0.5, FLOOR - sink + (y0 + trim) * squash)
            a1 = FLOOR - sink + (y1 - trim) * squash
            if a1 <= a0:
                continue
            wx, wz = (hw, hw * 0.62) if wide_x else (hw * 0.62, hw)
            frm, to = [cx - wx, a0, cz - wz], [cx + wx, a1, cz + wz]
            els.append({"from": [round(v, 3) for v in frm], "to": [round(v, 3) for v in to],
                        "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], a0, a1, top=True)})
    return els


def _loam(x0, x1, z0, z1, y0, y1, bottom=False):
    """the heap's faces: like _faces, but the tops read only the loam rows (3-15) of the atlas, never the frond band"""
    f = _faces("#nest", x0, x1, z0, z1, y0, y1, bottom=bottom)
    f["up"]["uv"] = [x0, round(3 + z0 * 13 / 16, 3), x1, round(3 + z1 * 13 / 16, 3)]
    return f


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    # the heap: a wide low base of loam and a smaller, higher top, uneven at the edges (lumps at the corners)
    els.append({"from": [0.5, 0, 0.5], "to": [15.5, 1.6, 15.5], "faces": _loam(0.5, 15.5, 0.5, 15.5, 0, 1.6, bottom=True)})
    els.append({"from": [1.5, 1.6, 1.5], "to": [14.5, 2.5, 14.5], "faces": _loam(1.5, 14.5, 1.5, 14.5, 1.6, 2.5)})
    els.append({"from": [3, 2.5, 2.5], "to": [13, 3.0, 13.5], "faces": _loam(3, 13, 2.5, 13.5, 2.5, 3.0)})
    for frm, to in (([0.2, 0, 5], [1.5, 2.2, 9]), ([14.5, 0, 7], [15.8, 2.0, 11]), ([6, 0, 0.2], [10, 2.3, 1.5]),
                    ([4, 0, 14.5], [9, 2.1, 15.8])):
        els.append({"from": frm, "to": to, "faces": _loam(frm[0], to[0], frm[2], to[2], frm[1], to[1])})
    for i, (cx, cz, sink) in enumerate(EGGS):
        els += _egg(cx, cz, sink, squash=0.85 if stage >= 2 and i == HATCH else 1.0)
    # the fern fronds over the clutch (the hatchling's egg uncovered by stage 1: the parent pulled one frond off)
    for k, (x0, z0, x1, z1, y, angle) in enumerate(FRONDS):
        if stage >= 1 and k == 1:
            continue
        cz = (z0 + z1) / 2
        # a flat frond: the leaflets on top (the atlas' three frond rows across its width), the midrib dark under it
        f = {n: {"uv": [0, 2, 7, 2.2 if n in ("north", "south") else 2.4], "texture": "#nest"} for n in ("north", "south", "east", "west")}
        f["up"] = {"uv": [x0, 0, x1, 3], "texture": "#nest"}
        f["down"] = {"uv": [x0, 2, x1, 3], "texture": "#nest"}
        el = {"from": [x0, y, cz - 1.0], "to": [x1, y + 0.2, cz + 1.0], "faces": f}
        el["rotation"] = {"origin": [(x0 + x1) / 2, y, cz], "axis": "y", "angle": angle}
        els.append(el)
    if stage >= 1:   # the pulled frond, lying on the loam at the edge
        f = {n: {"uv": [0, 2, 7, 2.2], "texture": "#nest"} for n in ("north", "south", "east", "west")}
        f["up"] = {"uv": [3, 0, 11, 3], "texture": "#nest"}
        els.append({"from": [1.5, 1.6, 13.4], "to": [9.5, 1.8, 15.4], "faces": f})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": tex}, "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 1.5, 0], "scale": [0.92, 0.92, 0.92]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


SADDLE_PAL = {"o": (28, 24, 18),                                                               # outline
              "w": (111, 100, 78), "W": (142, 130, 102), "V": (170, 158, 128), "v": (79, 70, 54),  # peeled poles, slats
              "t": (143, 118, 86), "T": (173, 147, 111), "b": (63, 44, 32),                       # bark cloth, its band
              "h": (77, 61, 46), "H": (102, 82, 61), "j": (124, 101, 73), "k": (51, 40, 31),      # smoked hide bale
              "c": (78, 66, 48), "C": (112, 97, 70)}                                              # twisted cord
SADDLE_ART = [   # side view: the cushion at the front (left) with its dark painted band, the deck of slats on the two
    "................",   # poles behind it (the slat ends stand up, uneven), the hide bale hanging on the side with its
    "................",   # one seam, the tie-down cord running down from the pole to the flank plate (no girth)
    "................",
    "..oooo..........",
    ".oTTTto.o.o.o...",
    ".otbbbtoVoVoVo..",
    ".oTttttoWoWoWoo.",
    "oVWWWWWWWWWWWWVo",
    "ovvvvvvvvvvvvvvo",
    ".oo.ohHHHHHjhoo.",
    "..C.ohjHHHHHho..",
    "..c.okhhhhhhko..",
    "..C.ohHHjHHHho..",
    "..c.okkkkkkkko..",
    "..C..oooooooo...",
    "..oo............",
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


CUSTOM_EGGS = {"ankylosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"ankylosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "ankylosaurus_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "ankylosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
