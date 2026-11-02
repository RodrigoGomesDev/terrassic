"""
Hides of the remade species (1.5): the hide item and the hide rug of each species in Eras.REMADE, drawn from the
animal as it is now.

Why: the rugs and hide icons were made in October from the old skins (blocks.py phase6_textures, sprites.py
hide_sprite) and were never redrawn when the species were remade, so a brick-red Carnotaurus dropped an olive hide
and a plum Triceratops an olive-brown one.  Here each species takes its five tones from its current male texture
(blocks.species_ramp) and its accent colours from the same texture (snapped to the nearest colour that is really
painted on the animal), and its marking comes from its own study (docs/CORES.md):

  tyrannosaurus       pebbly fine scales, rust bands slanting across them
  carnotaurus         small scales with two rows of big conical osteoderms (Bonaparte 1990; Hendrickx & Bell 2021)
  giganotosaurus      broad slate scales, no markings
  protoceratops       sand scales with rust saddles across the back
  spinosaurus         vertical stripes, as before
  velociraptor        feathers with petrol-blue bars
  pteranodon          short pycnofibre fuzz
  triceratops         big polygonal scales with a raised tubercle in the middle of each (Hell Creek skin, "Lane")
  gallimimus          graphite feathers with chalk tips
  pachycephalosaurus  honey skin with slanted cream stripes
  parasaurolophus     impala: russet back, a dark line, then the cream belly
  ankylosaurus        dark horn osteoderms with pale keels on blue-grey skin

The hide item keeps the stretched-pelt outline every hide in the mod has (that is what tells a player "hide"), and
its inside is cut from the species' own rug, with the rolled edge and the outline on top.  The alpha T. rex rugs
(alfa_trofeus.py) are their own coats and are not touched.

usage: python3 tools/spritegen/couros_1_5.py [species ...]   (default: every species below)
"""
import math
import os
import random
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import blocks as bk  # noqa: E402
import pixelkit as pk  # noqa: E402
from pixelkit import at, put  # noqa: E402
from sprites import Canvas, hexc, shade  # noqa: E402

N = 16
ROOT = bk.ROOT
TEX_BLOCK = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "block")
TEX_ITEM = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "item")
TEX_ENTITY = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "entity")

# species: (base pattern of blocks.hide_grid, marking, accent hints snapped to the skin's own colours)
SPECIES = {
    "tyrannosaurus": ("fine_scales", "bands", ["#a9463d"]),
    "carnotaurus": ("fine_scales", "osteoderm_rows", ["#331a18", "#b79972"]),
    "giganotosaurus": ("big_scales", None, []),
    "protoceratops": ("scales", "saddles", ["#5b3526"]),
    "spinosaurus": ("stripes", None, []),
    "velociraptor": ("feathers", "bars", ["#2f5a60"]),
    "pteranodon": ("fuzz", None, []),
    "triceratops": ("big_scales", "tubercles", ["#baa7ab"]),
    "gallimimus": ("feathers", "tips", ["#dfdcd3"]),  # ramp below: its pink shins and mouth pulled it to brown
    "pachycephalosaurus": ("fine_scales", "slant_stripes", ["#dccaa3"]),
    "parasaurolophus": ("fine_scales", "impala", ["#452013", "#ac987a"]),
    "ankylosaurus": ("osteoderms", "horn", ["#26211d", "#7e877b"]),
    "mosasaurus": ("fine_scales", None, []),
}


# species whose five tones are picked by hand from the skin (snapped to it) instead of the luminance spread
RAMP = {"gallimimus": ["#1d202d", "#37323d", "#384258", "#656873", "#9c9a96"]}


def skin_colours(sid):
    """Every opaque colour painted on the male, with how often it appears."""
    im = Image.open(os.path.join(TEX_ENTITY, f"{sid}_male.png")).convert("RGBA")
    count = {}
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = im.getpixel((x, y))
            if a > 200:
                count[(r, g, b)] = count.get((r, g, b), 0) + 1
    return count


def snap(hint, colours, min_share=0.002):
    """The colour really on the animal nearest to the hint (ignoring the odd stray pixel)."""
    total = sum(colours.values())
    h = hexc(hint)[:3]
    best = min((c for c, n in colours.items() if n >= total * min_share),
               key=lambda c: sum((a - b) ** 2 for a, b in zip(c, h)))
    return "#%02x%02x%02x" % best


def rug(sid):
    base, mark, hints = SPECIES[sid]
    colours = skin_colours(sid)
    raw = [snap(h, colours) for h in RAMP[sid]] if sid in RAMP else bk.species_ramp(sid)
    ramp = bk.muted(raw, 0.25)   # tanned: a little duller than the living animal
    acc = [bk.muted([snap(h, colours)], 0.25)[0] for h in hints]
    g = bk.hide_grid(sid + "_15", base)
    extra = {20 + i: c for i, c in enumerate(acc)}
    extra.update({30 + i: shade(hexc(c), 0.7) for i, c in enumerate(acc)})
    rnd = random.Random(sid + "rug15")
    if mark == "bands":  # rust bands slanting down to the tail, two per tile, ragged on their edges
        for y in range(N):
            for x in range(N):
                k = (x + y) % 8
                if k in (0, 1):
                    g[y][x] = 20 if g[y][x] >= 2 else 30
    elif mark == "osteoderm_rows":  # two rows of big cones, each lit on top with a shadow under it
        for row in (3, 11):
            for x0 in range(1 if row == 3 else 5, N, 8):
                for dx, dy, t in ((0, -1, 21), (1, -1, 21), (-1, 0, 20), (0, 0, 21), (1, 0, 21), (2, 0, 20),
                                  (-1, 1, 20), (0, 1, 20), (1, 1, 20), (2, 1, 30), (0, 2, 30), (1, 2, 30)):
                    put(g, (x0 + dx) % N, (row + dy) % N, t)
    elif mark == "saddles":  # broad dark saddles across the back with soft speckled edges
        for y in range(N):
            for x in range(N):
                d = (y + round(1.2 * math.sin(x / N * 2 * math.pi))) % 8
                if d in (0, 1, 2):
                    g[y][x] = 20 if g[y][x] >= 1 else 30
                elif d == 3 and rnd.random() < 0.35:
                    g[y][x] = 20
    elif mark == "bars":  # petrol-blue bars across the feathers, every other feather row
        for y in range(N):
            for x in range(N):
                if y % 6 in (2, 3) and g[y][x] >= 2:
                    g[y][x] = 20 if g[y][x] >= 3 else 30
    elif mark == "tubercles":  # a pale raised knob in the middle of every big scale
        owner = pk.regions_from_cells(sid + "_15", 10, gap=0.7)  # same cells blocks.hide_grid used
        cells = {}
        for y in range(N):
            for x in range(N):
                if owner[y][x] >= 0:
                    cells.setdefault(owner[y][x], []).append((x, y))
        for pts in cells.values():
            if len(pts) < 6:
                continue
            cx = round(sum(p[0] for p in pts) / len(pts)); cy = round(sum(p[1] for p in pts) / len(pts))
            put(g, cx, cy, 20); put(g, cx, cy + 1, 30)
    elif mark == "tips":  # chalk tips at the lower end of each feather
        for y in range(N):
            for x in range(N):
                if g[y][x] == 0 and rnd.random() < 0.3:
                    put(g, x, y - 1, 20)
    elif mark == "slant_stripes":  # thin cream stripes leaning back, as on the flank of the living animal
        for y in range(N):
            for x in range(N):
                if (2 * x - y) % 16 in (0, 1):
                    g[y][x] = 20
                elif (2 * x - y) % 16 == 2:
                    g[y][x] = max(0, min(g[y][x], 1))
    elif mark == "impala":  # russet down to row 10, a dark seam, then the cream belly
        for y in range(11, N):
            for x in range(N):
                g[y][x] = 30 if y == 11 else (21 if (x + y) % 5 else 31)
        for x in range(N):
            if rnd.random() < 0.5:
                put(g, x, 10, 20)
    elif mark == "horn":  # osteoderms in dark horn, keels pale, skin between them stays blue-grey
        for y in range(N):
            for x in range(N):
                v = g[y][x]
                if v == 4:
                    g[y][x] = 21
                elif v in (2, 3):
                    g[y][x] = 20
    return pk.colour(g, ramp, extra)


# the stretched pelt every hide item in the mod has: four leg flaps, the neck at the top
PELT = ["................",
        "....##....##....",
        "...##########...",
        "..############..",
        ".##############.",
        ".##############.",
        ".##############.",
        ".##############.",
        ".##############.",
        ".##############.",
        ".##############.",
        "..############..",
        "...##########...",
        "....##....##....",
        "................",
        "................"]


def pelt(sid, tile):
    cv = Canvas()
    for y, row in enumerate(PELT):
        for x, ch in enumerate(row):
            if ch != "#":
                continue
            c = tile.get(x, y)
            if any(PELT[y + dy][x + dx] != "#" for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                c = shade(c, 0.8)           # the edge curls under
            cv.set(x, y, c)
    for y in range(4, 10):                  # light down the left curl
        for x in range(1, 4):
            if PELT[y][x] == "#" and PELT[y][x - 1] != "#":
                cv.set(x + 1, y, shade(cv.get(x + 1, y), 1.15))
    cv.outline(0.42)
    return cv


def main(names):
    for sid in names:
        if not os.path.exists(os.path.join(TEX_ENTITY, f"{sid}_male.png")):
            print("skip", sid, "(no male texture yet)")
            continue
        tile = rug(sid)
        tile.save(os.path.join(TEX_BLOCK, f"{sid}_hide_rug.png"))
        pelt(sid, tile).save(os.path.join(TEX_ITEM, f"{sid}_hide.png"))
        print("ok", sid)


if __name__ == "__main__":
    main(sys.argv[1:] or list(SPECIES))
