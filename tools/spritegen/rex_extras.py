"""The T. rex's own egg and saddle art (2026-10-29, Rodrigo: "um ovo mais único" and "uma sela para cada dinossauro,
como no ARK", starting with the T. rex).

Egg (block terrassic:tyrannosaurus_egg, 3 hatch stages): a PAIR of long eggs standing in a shallow nest of twigs and
fern. Big theropods laid their eggs two at a time (two oviducts), long (about three times as long as wide) with the
shell raised in lines of little nodes ("lineartuberculate", e.g. Macroelongatoolithus, once credited to the
tyrannosaurs). T. rex eggs themselves are unknown; this is the closest real reference. The block model comes from
egg_model() (tools/javagen/gen_resources.py uses it for the species in CUSTOM_EGGS).

Saddle (item terrassic:tyrannosaurus_saddle): 16x16, read like the vanilla saddle (the seat seen from the side) but
the rex's own: high cantle, the woven rust-and-bone blanket of the model, a saddlebag, an iron ring and a rex tooth.

usage: python3 -B tools/spritegen/rex_extras.py   (sprites.py also calls main() and skips the CUSTOM_EGGS eggs)
"""
import os
import random

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEX = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures")
SHELL = {"base": (176, 162, 132), "light": (204, 192, 160), "groove": (158, 145, 116), "node": (222, 212, 184),
         "rust": (150, 92, 58), "crack": (58, 46, 36), "hole": (30, 24, 20), "inner": (226, 214, 176)}
NEST = {"soil": (74, 58, 40), "soil2": (92, 72, 48), "twig": (128, 98, 62), "twig2": (160, 128, 84), "fern": (86, 104, 52), "fern2": (110, 128, 64)}


def shell(stage):
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(41)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            ridge = x % 3 == 1
            c = SHELL["light"] if ridge else (SHELL["groove"] if x % 3 == 0 else SHELL["base"])
            if ridge and (y + x // 3) % 3 == 0:
                c = SHELL["node"]
            # a little darker towards the bottom, as if lit from above
            k = 1.0 - 0.10 * (y / 15.0)
            px[x, y] = (int(c[0] * k), int(c[1] * k), int(c[2] * k), 255)
    for _ in range(3):   # a few faint rust flecks
        x, y = rnd.randrange(16), rnd.randrange(2, 14)
        if x % 3 != 1:
            px[x, y] = tuple((a + b) // 2 for a, b in zip(SHELL["rust"], SHELL["base"])) + (255,)
    if stage >= 1:
        for x, y in ((7, 5), (8, 6), (8, 7), (9, 8), (8, 9)):
            px[x, y] = SHELL["crack"] + (255,)
    if stage >= 2:
        for x, y in ((6, 4), (10, 7), (11, 6), (7, 10), (6, 11)):
            px[x, y] = SHELL["crack"] + (255,)
        for x, y in ((8, 7), (9, 7), (8, 8)):
            px[x, y] = SHELL["hole"] + (255,)
        px[9, 9] = SHELL["inner"] + (255,)
    return img


def nest():
    from PIL import Image  # lazy: gen_resources imports this module for egg_model and must run without Pillow
    rnd = random.Random(7)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = (NEST["soil"] if (x * 7 + y * 3) % 5 else NEST["soil2"]) + (255,)
    for _ in range(14):   # twigs: short diagonal strokes
        x, y = rnd.randrange(16), rnd.randrange(16)
        dx = rnd.choice((1, -1))
        col = NEST["twig2"] if rnd.random() < 0.4 else NEST["twig"]
        for i in range(rnd.randint(3, 5)):
            xx, yy = (x + i * dx) % 16, (y + (i if rnd.random() < 0.6 else 0)) % 16
            px[xx, yy] = col + (255,)
    for _ in range(6):    # fern fronds tucked in
        x, y = rnd.randrange(16), rnd.randrange(16)
        px[x, y] = NEST["fern2"] + (255,)
        px[(x + 1) % 16, y] = NEST["fern"] + (255,)
    return img


# the egg standing on its blunt end: (y from, y to, half width) rows of a rounded egg 7 wide and 9.5 tall
# (Rodrigo 29/10: the first one, 5 x 13, was too thin)
EGG_ROWS = [(0.0, 1.0, 2.5), (1.0, 6.5, 3.5), (6.5, 8.5, 2.75), (8.5, 9.5, 1.5)]


def _faces(tex, x0, x1, z0, z1, y0, y1, sides=True, top=True, bottom=False):
    f = {}
    if sides:
        for name, (a, b) in (("north", (16 - x1, 16 - x0)), ("south", (x0, x1)), ("east", (16 - z1, 16 - z0)), ("west", (z0, z1))):
            f[name] = {"uv": [a, 16 - y1, b, 16 - y0], "texture": tex}
    if top:
        f["up"] = {"uv": [x0, z0, x1, z1], "texture": tex}
    if bottom:
        f["down"] = {"uv": [x0, 16 - z1, x1, 16 - z0], "texture": tex}
    return f


def egg_model(sid, stage):
    tex = f"terrassic:block/{sid}_egg_{stage}"
    nest_tex = f"terrassic:block/{sid}_nest"
    els = []
    # the nest: a low pad of soil and a rim of twigs
    els.append({"from": [2, 0, 2], "to": [14, 1, 14], "faces": _faces("#nest", 2, 14, 2, 14, 0, 1, bottom=True)})
    for frm, to in (([1, 0, 3], [3, 2.5, 13]), ([13, 0, 3], [15, 2.5, 13]), ([3, 0, 1], [13, 2, 3]), ([3, 0, 13], [13, 2, 15])):
        els.append({"from": frm, "to": to, "faces": _faces("#nest", frm[0], to[0], frm[2], to[2], frm[1], to[1])})
    # the pair, side by side in the hollow
    for cx, cz, sink, k in ((4.5, 5.0, 0.0, 1.0), (11.5, 11.0, 1.0, 0.85)):
        for y0, y1, h in EGG_ROWS:
            y0, y1, h = 1.0 - sink + y0 * k + sink * 0, 1.0 - sink + y1 * k, h * (0.92 if k < 1 else 1.0)
            if y1 <= 0.5:
                continue
            y0 = max(y0, 0.5)
            frm = [cx - h, y0, cz - h]; to = [cx + h, y1, cz + h]
            els.append({"from": frm, "to": to,
                        "faces": _faces("#egg", frm[0], to[0], frm[2], to[2], y0, y1, top=True)})
    return {"parent": "block/block", "textures": {"egg": tex, "nest": nest_tex, "particle": tex}, "elements": els,
            "display": {"gui": {"rotation": [25, 225, 0], "translation": [0, 1, 0], "scale": [0.85, 0.85, 0.85]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}

SADDLE_PAL = {
    "o": (38, 25, 17),     # outline
    "d": (74, 47, 31),     # dark leather
    "l": (107, 68, 41),    # leather
    "h": (140, 94, 58),    # leather highlight
    "s": (184, 155, 106),  # stitching
    "r": (122, 58, 36),    # blanket rust
    "R": (156, 90, 51),    # blanket rust light
    "b": (201, 178, 122),  # blanket bone
    "k": (60, 35, 24),     # blanket dark
    "i": (110, 110, 106),  # iron
    "I": (163, 163, 155),  # iron light
    "t": (241, 235, 212),  # tooth
    "T": (201, 189, 152),  # tooth shade
}
SADDLE_ART = [
    "................",
    "..........ooo...",
    ".........ohho...",
    "...oo....ohlo...",
    "..ohho..ohlld...",
    "..ohlhoooolldo..",
    "..odllhhhllldo..",
    ".ooddsslllsddoo.",
    ".okrbrbRbrbrbko.",
    ".okRbrbrbRbrbko.",
    "..okkkoodkkkko..",
    "....oldo.olIo...",
    "....olho.oIoIo..",
    "....oddo.oIIo...",
    ".....oo.otTo....",
    "........oto.....",
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


# species whose egg is drawn here instead of by sprites.py (texture) and gen_resources.egg_model (block model)
CUSTOM_EGGS = {"tyrannosaurus": egg_model}


def main():
    from sprites import save_png
    for stage in range(3):
        save_png(shell(stage), os.path.join(TEX, "block", f"tyrannosaurus_egg_{stage}.png"))
    save_png(nest(), os.path.join(TEX, "block", "tyrannosaurus_nest.png"))
    save_png(saddle_sprite(), os.path.join(TEX, "item", "tyrannosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
