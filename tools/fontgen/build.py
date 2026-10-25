"""
Builds the three Terrassic typefaces (docs/IDENTIDADE.md §4):

  sedimento  interface (8 px)        assets/terrassic/font/sedimento.json
  entalhe    titles (12 px, capitals) assets/terrassic/font/entalhe.json
  caderno    Katarina's handwriting   assets/terrassic/font/caderno.json

For each: the Minecraft bitmap sheets (textures/font/<name>.png and <name>_accented.png, accented letters on a taller
sheet like vanilla), the font definition (a space provider, the bitmap providers and a reference to minecraft:default
so anything we did not draw still shows), a TrueType file for the website and brand material
(art/identidade/fontes/<name>.ttf, pixels traced into outlines) and a specimen image.

usage:  python3 build.py            (writes everything)
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
ART = os.path.join(ROOT, "art", "identidade", "fontes")

import caderno  # noqa: E402
import entalhe  # noqa: E402
import sedimento  # noqa: E402
from pixfont import PixelFont  # noqa: E402

FONTS = {}


def make_fonts():
    g = {}
    g.update(sedimento.UPPER)
    g.update(sedimento.LOWER)
    g.update(sedimento.DIGITS)
    g.update(sedimento.PUNCT)
    FONTS["sedimento"] = PixelFont("sedimento", g, 8, 7, sedimento.SPACE, sedimento.ACCENTS, sedimento.COMPOSED,
                                   sedimento.CEDILLA, accent_gap=1)
    g = {}
    g.update(entalhe.UPPER)
    g.update(entalhe.DIGITS)
    g.update(entalhe.PUNCT)
    f = PixelFont("entalhe", g, 12, 10, entalhe.SPACE, entalhe.ACCENTS, entalhe.COMPOSED, entalhe.CEDILLA,
                  accent_gap=1, spacing=entalhe.SPACING)
    # an inscription has no lowercase: lowercase letters use the capitals
    for ch in list(f.base):
        if ch.isalpha() and ch.isupper():
            f.base[ch.lower()] = f.base[ch]
    for ch in list(f.accented):
        if ch.isupper():
            f.accented[ch.lower()] = f.accented[ch]
    FONTS["entalhe"] = f
    FONTS["caderno"] = PixelFont("caderno", caderno.glyphs(), 8, 7, caderno.SPACE, caderno.ACCENTS, caderno.COMPOSED,
                                 caderno.CEDILLA, accent_gap=1)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def minecraft(name, f):
    tex = os.path.join(ASSETS, "textures", "font")
    os.makedirs(tex, exist_ok=True)
    base_cells = max(g.width for g in f.base.values()) + max(1, f.spacing)
    cell_w = max(8, base_cells)
    img, lines = f.sheet(sorted(f.base.items()), cell_w, f.cell_h, spacer_alpha=True)
    img.save(os.path.join(tex, f"{name}.png"))
    acc_h = f.cell_h + f.extra
    acc_w = max(cell_w, max((g.width for g in f.accented.values()), default=0) + max(1, f.spacing))
    aimg, alines = f.sheet(sorted(f.accented.items()), acc_w, acc_h, spacer_alpha=True)
    aimg.save(os.path.join(tex, f"{name}_accented.png"))
    providers = [
        {"type": "space", "advances": {" ": f.space, "‌": 0}},
        {"type": "bitmap", "file": f"terrassic:font/{name}.png", "height": f.cell_h, "ascent": f.ascent, "chars": lines},
        {"type": "bitmap", "file": f"terrassic:font/{name}_accented.png", "height": acc_h, "ascent": f.ascent + f.extra,
         "chars": alines},
        {"type": "reference", "id": "minecraft:default"},
    ]
    write_json(os.path.join(ASSETS, "font", f"{name}.json"), {"providers": providers})
    return len(f.base), len(f.accented)


# ------------------------------------------------------------------ TrueType (outlines traced from the pixels)

def trace(cells):
    """cells: set of (x, y) filled pixels, y up. Returns closed polygons (clockwise outside, counter-clockwise holes)."""
    edges = {}
    for (x, y) in cells:
        # each pixel's boundary, clockwise with y up: (x,y)->(x,y+1)->(x+1,y+1)->(x+1,y)->(x,y)
        for a, b in (((x, y), (x, y + 1)), ((x, y + 1), (x + 1, y + 1)), ((x + 1, y + 1), (x + 1, y)), ((x + 1, y), (x, y))):
            if (b, a) in edges:
                del edges[(b, a)]
            else:
                edges[(a, b)] = True
    nxt = {}
    for a, b in edges:
        nxt.setdefault(a, []).append(b)
    polys = []
    while nxt:
        start = next(iter(nxt))
        poly = [start]
        cur = start
        prev_dir = None
        while True:
            outs = nxt[cur]
            if len(outs) == 1:
                b = outs.pop()
            else:
                # two pixels touching at a corner: turn right (keeps diagonal pixels as separate shapes)
                def turn(b):
                    d = (b[0] - cur[0], b[1] - cur[1])
                    if prev_dir is None:
                        return 0
                    cross = prev_dir[0] * d[1] - prev_dir[1] * d[0]
                    return cross
                outs.sort(key=turn)
                b = outs.pop(0)
            if not outs:
                del nxt[cur]
            prev_dir = (b[0] - cur[0], b[1] - cur[1])
            cur = b
            if cur == start:
                break
            poly.append(cur)
        # drop collinear points
        simple = []
        n = len(poly)
        for i in range(n):
            p0, p1, p2 = poly[i - 1], poly[i], poly[(i + 1) % n]
            if (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p1[1] - p0[1]) * (p2[0] - p1[0]) != 0:
                simple.append(p1)
        polys.append(simple)
    return polys


def truetype(name, f, family):
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    unit = 100                          # one pixel
    upm = unit * (f.cell_h + 0)         # the em is the base cell height
    descent = f.cell_h - f.ascent
    order = [".notdef", "space"]
    cmap = {32: "space"}
    glyphs = {}
    metrics = {}

    def build(rows, above):
        cells = set()
        for gy, row in enumerate(rows):
            for gx, c in enumerate(row):
                if c == "#":
                    cells.add((gx, above - 1 - gy))   # y up, baseline at 0
        pen = TTGlyphPen(None)
        for poly in trace(cells):
            pen.moveTo((poly[0][0] * unit, poly[0][1] * unit))
            for p in poly[1:]:
                pen.lineTo((p[0] * unit, p[1] * unit))
            pen.closePath()
        return pen.glyph()

    notdef = TTGlyphPen(None)
    notdef.moveTo((0, 0)); notdef.lineTo((0, 7 * unit)); notdef.lineTo((4 * unit, 7 * unit)); notdef.lineTo((4 * unit, 0)); notdef.closePath()
    glyphs[".notdef"] = notdef.glyph()
    metrics[".notdef"] = (5 * unit, 0)
    glyphs["space"] = TTGlyphPen(None).glyph()
    metrics["space"] = (f.space * unit, 0)
    for ch in f.chars():
        g = f.glyph(ch)
        gname = f"uni{ord(ch):04X}"
        if gname in glyphs:
            continue
        order.append(gname)
        cmap[ord(ch)] = gname
        glyphs[gname] = build(g.rows, g.above)
        metrics[gname] = (f.advance(ch) * unit, 0)
    fb = FontBuilder(upm, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    asc = (f.ascent + f.extra) * unit
    fb.setupHorizontalHeader(ascent=asc, descent=-descent * unit)
    fb.setupNameTable({"familyName": family, "styleName": "Regular",
                       "copyright": "Copyright (c) 2026 Rodrigo Gomes. All rights reserved. Terrassic asset.",
                       "manufacturer": "Rodrigo Gomes", "description": "Pixel typeface of the Terrassic Minecraft mod."})
    fb.setupOS2(sTypoAscender=asc, sTypoDescender=-descent * unit, usWinAscent=asc, usWinDescent=descent * unit,
                sxHeight=5 * unit, sCapHeight=(f.ascent) * unit)
    fb.setupPost()
    os.makedirs(ART, exist_ok=True)
    fb.save(os.path.join(ART, f"{name}.ttf"))


# ------------------------------------------------------------------ specimen

SAMPLES = {
    "sedimento": ["Sedimento: a letra da interface do Terrassic",
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz",
                  "0123456789 !?.,;:'\"()[]{}<>/\\@#$%&*+-=_~«»¡¿ºª°…",
                  "ÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜ àáâãäçèéêëìíîïñòóôõöùúûü",
                  "Regras do Terrassic · Nível de dificuldade: 0,5",
                  "Atravesse a Fenda. Cross the Rift. Cruza la Grieta.",
                  "Do tamanho que eles eram: 13 blocos, 13 metros."],
    "entalhe": ["TERRASSIC", "ECOS DO FIM", "ATRAVESSE A FENDA",
                "ABCDEFGHIJKLM", "NOPQRSTUVWXYZ", "0123456789 ÁÊÇÃÕÑ !?&"],
    "caderno": ["Caderno: a letra da Dra. Katarina Usha",
                "Dia 212. O rio subiu de novo; o Mate não quis atravessar.",
                "Day 212. The river rose again; Mate would not cross.",
                "Día 212. El río volvió a subir; Mate no quiso cruzar.",
                "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789",
                "Não traga nada. Nada atravessa além de nós."],
}


def specimen(name, f, scale):
    from_palette = {"bg": (28, 24, 30, 255), "ink": (216, 204, 178, 255), "accent": (242, 181, 68, 255),
                    "shadow": (14, 11, 14, 255), "paper": (233, 220, 188, 255), "pen": (59, 42, 26, 255)}
    lines = SAMPLES[name]
    lh = f.cell_h + f.extra + 4
    width = max(f.text_width(l) for l in lines) + 16
    height = lh * len(lines) + 12
    paper = name == "caderno"
    img = Image.new("RGBA", (width, height), from_palette["paper" if paper else "bg"])
    y = 6
    for i, l in enumerate(lines):
        col = from_palette["pen"] if paper else (from_palette["accent"] if i == 0 or name == "entalhe" else from_palette["ink"])
        f.draw(img, l, 8, y + f.extra, col, shadow=None if paper else from_palette["shadow"])
        y += lh
    img = img.resize((width * scale, height * scale), Image.NEAREST)
    os.makedirs(ART, exist_ok=True)
    img.save(os.path.join(ART, f"especime_{name}.png"))


def main():
    make_fonts()
    families = {"sedimento": "Terrassic Sedimento", "entalhe": "Terrassic Entalhe", "caderno": "Terrassic Caderno"}
    for name, f in FONTS.items():
        nb, na = minecraft(name, f)
        truetype(name, f, families[name])
        specimen(name, f, 3 if name != "entalhe" else 3)
        print(f"{name}: {nb} glyphs + {na} accented")


if __name__ == "__main__":
    main()
