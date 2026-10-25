"""
Terrassic brand kit (docs/IDENTIDADE.md §5), drawn by code with the mod's own typefaces (tools/fontgen) and palette
(client/ui/TerrassicPalette):

  art/identidade/marca/letreiro.png      the wordmark: TERRASSIC in "Degraus", the title face (letreiro.py), in stone
  art/identidade/marca/monograma.png     the monogram: an amber Degraus T carved in a basalt slab (avatar, favicon)
  art/identidade/marca/selo.png          the Altar seal: the ring of stones and bones around the amber (no dinosaur)
  art/identidade/marca/icone_proposta.png  a 512 px mod icon proposal (seal + monogram), to replace the current one
                                           only after Rodrigo approves it (ROADMAP rule 12)
  art/identidade/marca/prancha.png       the brand board: all of the above, the palette and the three typefaces

usage:  python3 brand.py
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fontgen"))
import build as fontbuild  # noqa: E402
import degraus  # noqa: E402

sys.path.insert(0, HERE)
import letreiro  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "art", "identidade", "marca")

P = dict(BASALT_950=(14, 11, 14), BASALT_900=(20, 16, 20), BASALT_800=(28, 24, 30), BASALT_700=(42, 35, 41),
         BASALT_600=(58, 48, 54), BASALT_500=(82, 69, 80), STONE_400=(138, 124, 106), STONE_300=(179, 164, 140),
         STONE_200=(216, 204, 178), BONE_100=(239, 230, 210), AMBER_700=(185, 119, 28), AMBER_600=(217, 149, 44),
         AMBER_500=(242, 181, 68), AMBER_300=(255, 210, 122), RIFT_500=(240, 122, 26), DUSK_700=(58, 34, 64),
         DUSK_500=(94, 56, 102), FERN_400=(127, 175, 85), PAPER=(233, 220, 188), INK=(59, 42, 26))


def rgba(c, a=255):
    return c + (a,)


def text_mask(font, text):
    """1x mask of a text line in a pixel font (True = ink)."""
    w = font.text_width(text) + 2
    h = font.cell_h + font.extra + 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    font.draw(img, text, 0, font.extra, (255, 255, 255, 255))
    px = img.load()
    return [[px[x, y][3] > 0 for x in range(w)] for y in range(h)], w, h


def carve(mask, w, h, s, seed="terrassic", vein=True):
    """Each font pixel becomes an s x s block of carved stone: noisy limestone, lit top/left, shaded bottom/right,
    a dark outline around the letters and an amber vein running through them."""
    rnd = random.Random(seed)
    pad = 3
    W, H = (w + pad * 2) * s, (h + pad * 2) * s
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()

    def m(x, y):
        return 0 <= x < w and 0 <= y < h and mask[y][x]
    ramp = [P["STONE_400"], P["STONE_300"], P["STONE_200"], P["BONE_100"]]
    # the vein: a jagged line across the word, a little under the middle
    vein_y = {}
    y = h * 0.55
    for x in range(w):
        y += rnd.choice((-1, 0, 0, 1)) * 0.6
        y = max(h * 0.35, min(h * 0.75, y))
        vein_y[x] = int(round(y))
    for y in range(h):
        for x in range(w):
            if not m(x, y):
                continue
            for sy in range(s):
                for sx in range(s):
                    t = rnd.random()
                    c = ramp[1] if t < 0.45 else ramp[2] if t < 0.85 else ramp[0]
                    if sy == 0 and not m(x, y - 1):
                        c = ramp[3]
                    elif sx == 0 and not m(x - 1, y):
                        c = ramp[2] if c != ramp[3] else c
                    if sy == s - 1 and not m(x, y + 1):
                        c = P["STONE_400"]
                    if sx == s - 1 and not m(x + 1, y):
                        c = P["STONE_400"]
                    px[(x + pad) * s + sx, (y + pad) * s + sy] = rgba(c)
            if vein and abs(y - vein_y[x]) == 0:
                for sx in range(s):
                    core = s // 2
                    px[(x + pad) * s + sx, (y + pad) * s + core] = rgba(P["AMBER_300"])
                    if core + 1 < s:
                        px[(x + pad) * s + sx, (y + pad) * s + core + 1] = rgba(P["AMBER_600"])
                    if core - 1 >= 0:
                        px[(x + pad) * s + sx, (y + pad) * s + core - 1] = rgba(P["AMBER_500"])
    # outline: 1 sub-pixel of deep basalt around the letters, and a 2 sub-pixel drop shadow
    alpha = img.split()[3]
    ring = alpha.filter(ImageFilter.MaxFilter(3))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", (W, H), rgba(P["BASALT_950"], 200)), (s // 2, s // 2), ring)
    outline = Image.new("RGBA", (W, H), rgba(P["BASALT_950"]))
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base.alpha_composite(shadow)
    base.paste(outline, (0, 0), ring)
    base.alpha_composite(img)
    return base


def wordmark(scale=6, finish="pedra"):
    """TERRASSIC in Degraus, the approved title face (2026-10-25)."""
    return letreiro.image("TERRASSIC", finish, s=scale)


def slab(size, inset=0):
    """A basalt slab with bevel, as in TerrassicUi.slab, at pixel size `size`."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, size - 1, size - 1], fill=rgba(P["BASALT_950"]))
    d.rectangle([1, 1, size - 2, size - 2], fill=rgba(P["BASALT_800"]))
    d.line([1, 1, size - 2, 1], fill=rgba(P["BASALT_500"]))
    d.line([1, 1, 1, size - 2], fill=rgba(P["BASALT_600"]))
    d.line([1, size - 2, size - 2, size - 2], fill=rgba(P["BASALT_900"]))
    d.line([size - 2, 1, size - 2, size - 2], fill=rgba(P["BASALT_900"]))
    for (x, y) in ((3, 3), (size - 6, 3), (3, size - 6), (size - 6, size - 6)):
        d.rectangle([x, y, x + 2, y + 2], fill=rgba(P["AMBER_700"]))
        d.rectangle([x, y, x + 1, y + 1], fill=rgba(P["AMBER_500"]))
        d.point((x, y), fill=rgba(P["AMBER_300"]))
    return img


def monogram():
    """32 x 32: an amber T in "Degraus" (scaled x2) carved in a basalt slab."""
    img = slab(32)
    rows = degraus.GLYPHS["T"]
    px = img.load()
    ox, oy = (32 - len(rows[0]) * 2) // 2, (32 - len(rows) * 2) // 2
    for gy, row in enumerate(rows):
        for gx, c in enumerate(row):
            if c != "#":
                continue
            for sy in range(2):
                for sx in range(2):
                    X, Y = ox + gx * 2 + sx, oy + gy * 2 + sy
                    top = gy == 0 or rows[gy - 1][gx] != "#"
                    col = P["AMBER_300"] if (top and sy == 0) else P["AMBER_500"] if sx == 0 else P["AMBER_600"]
                    px[X, Y] = rgba(col)
                    # carved shadow under and right of each stroke
                    for (dx, dy) in ((1, 1),):
                        if 0 <= X + dx < 32 and 0 <= Y + dy < 32 and px[X + dx, Y + dy][:3] == P["BASALT_800"]:
                            px[X + dx, Y + dy] = rgba(P["BASALT_950"])
    return img


def seal(size=64):
    """The Altar seal: a dusk disc, a ring of 4 standing stones and 4 bones, the amber core in the middle."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2 - 0.5
    d.ellipse([0, 0, size - 1, size - 1], fill=rgba(P["BASALT_950"]))
    d.ellipse([2, 2, size - 3, size - 3], fill=rgba(P["STONE_400"]))
    d.ellipse([4, 4, size - 5, size - 5], fill=rgba(P["DUSK_700"]))
    d.ellipse([10, 10, size - 11, size - 11], fill=rgba(P["DUSK_500"]))
    d.ellipse([12, 12, size - 13, size - 13], fill=rgba(P["DUSK_700"]))
    r = size * 0.33
    for i in range(8):
        a = -math.pi / 2 + i * math.pi / 4
        x, y = c + math.cos(a) * r, c + math.sin(a) * r
        if i % 2 == 0:   # standing stone
            d.rectangle([x - 2, y - 4, x + 2, y + 4], fill=rgba(P["BASALT_950"]))
            d.rectangle([x - 1, y - 3, x + 1, y + 3], fill=rgba(P["STONE_300"]))
            d.line([x - 1, y - 3, x - 1, y + 3], fill=rgba(P["STONE_200"]))
        else:            # bone
            d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=rgba(P["BASALT_950"]))
            d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=rgba(P["BONE_100"]))
    # the amber core: a cut gem with a glow
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([c - 11, c - 11, c + 11, c + 11], fill=rgba(P["AMBER_500"], 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(img)
    gem = [(c, c - 8), (c + 6, c - 2), (c + 4, c + 7), (c - 4, c + 7), (c - 6, c - 2)]
    d.polygon(gem, fill=rgba(P["AMBER_600"]), outline=rgba(P["BASALT_950"]))
    d.polygon([(c, c - 7), (c + 5, c - 2), (c, c + 1), (c - 5, c - 2)], fill=rgba(P["AMBER_500"]))
    d.polygon([(c - 1, c - 6), (c - 4, c - 2), (c - 1, c - 1)], fill=rgba(P["AMBER_300"]))
    return img


def icon_proposal():
    """512 px: the seal at 8x with the monogram glyph in the gem's place."""
    s = seal(64)
    big = s.resize((512, 512), Image.NEAREST)
    return big


def board():
    W, H = 1600, 1000
    img = Image.new("RGBA", (W, H), rgba(P["BASALT_800"]))
    d = ImageDraw.Draw(img)
    for y in range(H):   # dusk gradient band on top
        k = max(0.0, 1.0 - y / 420.0)
        if k > 0:
            col = tuple(int(P["BASALT_800"][i] + (P["DUSK_700"][i] - P["BASALT_800"][i]) * k) for i in range(3))
            d.line([0, y, W, y], fill=rgba(col))
    wm = wordmark(7)
    img.alpha_composite(wm, ((W - wm.width) // 2, 40))
    sedimento = fontbuild.FONTS["sedimento"]
    entalhe = fontbuild.FONTS["entalhe"]
    caderno = fontbuild.FONTS["caderno"]

    def line(font, text, x, y, col, scale, shadow=True):
        tmp = Image.new("RGBA", (font.text_width(text) + 4, font.cell_h + font.extra + 4), (0, 0, 0, 0))
        font.draw(tmp, text, 0, font.extra, rgba(col), shadow=rgba(P["BASALT_950"]) if shadow else None)
        tmp = tmp.resize((tmp.width * scale, tmp.height * scale), Image.NEAREST)
        img.alpha_composite(tmp, (x, y))
        return tmp.width

    tag = "ATRAVESSE A FENDA  ·  CROSS THE RIFT  ·  CRUZA LA GRIETA"
    tw = entalhe.text_width(tag) * 2
    line(entalhe, tag, (W - tw) // 2, 245, P["AMBER_500"], 2)
    # monogram, seal, icon
    mono = monogram().resize((192, 192), Image.NEAREST)
    img.alpha_composite(mono, (90, 340))
    sl = seal(64).resize((192, 192), Image.NEAREST)
    img.alpha_composite(sl, (320, 340))
    line(sedimento, "Monograma", 120, 545, P["STONE_200"], 3)
    line(sedimento, "Selo do Altar", 330, 545, P["STONE_200"], 3)
    # palette
    names = ["BASALT_800", "BASALT_700", "STONE_200", "BONE_100", "AMBER_700", "AMBER_500", "AMBER_300", "RIFT_500",
             "DUSK_700", "FERN_400", "PAPER", "INK"]
    x0, y0 = 600, 340
    for i, n in enumerate(names):
        x = x0 + (i % 6) * 160
        y = y0 + (i // 6) * 110
        d.rectangle([x, y, x + 140, y + 60], fill=rgba(P[n]), outline=rgba(P["BASALT_950"]))
        line(sedimento, n.replace("_", " ").title(), x, y + 66, P["STONE_200"], 2, shadow=False)
        line(sedimento, "#%02X%02X%02X" % P[n], x, y + 84, P["STONE_400"], 2, shadow=False)
    # typefaces
    y = 610
    line(entalhe, "ENTALHE", 90, y, P["AMBER_500"], 4)
    line(sedimento, "títulos · inscrição em pedra · 12 px", 520, y + 14, P["STONE_400"], 3)
    y += 80
    line(sedimento, "Sedimento: Regras do Terrassic. Nível de dificuldade 0,5.", 90, y, P["STONE_200"], 4)
    line(sedimento, "interface · 8 px", 1250, y + 4, P["STONE_400"], 3)
    y += 70
    paper = Image.new("RGBA", (1420, 150), rgba(P["PAPER"]))
    img.alpha_composite(paper, (90, y))
    d.rectangle([90, y, 1509, y + 149], outline=rgba((216, 199, 158)))

    def pline(text, yy):
        tmp = Image.new("RGBA", (caderno.text_width(text) + 4, 16), (0, 0, 0, 0))
        caderno.draw(tmp, text, 0, caderno.extra, rgba(P["INK"]))
        tmp = tmp.resize((tmp.width * 4, tmp.height * 4), Image.NEAREST)
        img.alpha_composite(tmp, (110, yy))
    pline("Caderno: Dia 212. O rio subiu de novo; o Mate não quis atravessar.", y + 14)
    pline("Não traga nada. Nada atravessa além de nós.  K. Usha", y + 78)
    return img


def main():
    fontbuild.make_fonts()
    os.makedirs(OUT, exist_ok=True)
    wordmark(6).save(os.path.join(OUT, "letreiro.png"))
    monogram().resize((256, 256), Image.NEAREST).save(os.path.join(OUT, "monograma.png"))
    seal(64).resize((256, 256), Image.NEAREST).save(os.path.join(OUT, "selo.png"))
    icon_proposal().save(os.path.join(OUT, "icone_proposta.png"))
    board().save(os.path.join(OUT, "prancha.png"))
    print("brand kit:", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
