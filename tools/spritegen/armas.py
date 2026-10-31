"""Weapon art beyond the 16x16 item sprites (docs/ARMAS.md): the narcotic dart's flight texture (the vanilla
arrow layout: a 16x5 side view and a 5x5 back view in a 32x32 sheet) and the reed tube texture of the blowgun's
"at the lips" 3D model. Every pixel is placed by hand below."""
import os

from PIL import Image

from rex_extras import TEX
from sprites import save_png, hexc, REED, REED_L, REED_D, REED_N, DART_G, FEATHER, FEATHER_D, FLINT, FLINT_L, FLINT_D, \
    LEATHER, LEATHER_D, shade

PAL = {
    "f": FEATHER, "F": FEATHER_D,               # the fibre puff that seals the bore
    "r": REED_L, "R": REED, "n": REED_N, "d": REED_D,
    "g": DART_G, "G": shade(DART_G, 0.72),      # the narcotic paste smeared behind the point
    "s": FLINT, "l": FLINT_L, "k": FLINT_D,
    "L": LEATHER, "D": LEATHER_D,
}

# tail on the left, point on the right (the arrow renderer flies +u forward)
DART_SIDE = [
    ".ff.............",
    "fffF........ls..",
    "ffFFrRrnrRggslsk",
    "fFFF........sk..",
    ".FF.............",
]
DART_BACK = [
    ".fff.",
    "fffff",
    "ffrfF",
    "ffffF",
    ".FFF.",
]

# reed tube: rows 0-1 the lit sides, rows 2-3 the underside; nodes every five pixels
TUBE = {
    0: "rrrnrrrrnrrrrnrr",
    1: "RRRnRRRRnRRRRnRR",
    2: "RRdnddRdnddRdndd",
    3: "ddnnddddnnddddnd",
}
MUZZLE = ["nk", "kn"]                 # the open bore at (0, 4)
WRAP = ["LDL", "DLD", "LDL"]          # the leather mouthpiece binding at (0, 8)


def _paint(img, rows, x0, y0):
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                img.putpixel((x0 + x, y0 + y), PAL[ch])


def dart_texture():
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    _paint(img, DART_SIDE, 0, 0)
    _paint(img, DART_BACK, 0, 5)
    return img


def tube_texture():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    _paint(img, [TUBE[i] for i in range(4)], 0, 0)
    _paint(img, MUZZLE, 0, 4)
    _paint(img, WRAP, 0, 8)
    return img


def main():
    save_png(dart_texture(), os.path.join(TEX, "entity", "tranq_dart.png"))
    save_png(tube_texture(), os.path.join(TEX, "item", "blowgun_tube.png"))


if __name__ == "__main__":
    main()
