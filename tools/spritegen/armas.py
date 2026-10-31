"""Weapon art beyond the 16x16 item sprites (docs/ARMAS.md): the narcotic dart's flight texture (the vanilla
arrow layout: a 16x5 side view and a 5x5 back view in a 32x32 sheet) and the reed tube texture of the blowgun's
"at the lips" 3D model. Every pixel is placed by hand below."""
import os

from PIL import Image

from rex_extras import TEX
from sprites import save_png, hexc, WOOD, WOOD_D, WOOD_L, BONE, REED, REED_L, REED_D, REED_N, DART_G, FEATHER, FEATHER_D, FLINT, FLINT_L, FLINT_D, \
    LEATHER, LEATHER_D, shade

PAL = {
    "f": FEATHER, "F": FEATHER_D,               # the fibre puff that seals the bore
    "r": REED_L, "R": REED, "n": REED_N, "d": REED_D,
    "g": DART_G, "G": shade(DART_G, 0.72),      # the narcotic paste smeared behind the point
    "s": FLINT, "l": FLINT_L, "k": FLINT_D,
    "L": LEATHER, "D": LEATHER_D,
    "w": WOOD, "e": WOOD_D, "h": WOOD_L, "b": BONE, "t": FEATHER_D, "S": hexc("#e2dcc8"),  # bow wood, sinew
    "u": hexc("#c8c48a"), "U": hexc("#9c9a5a"),  # rush-fibre fletching
    "v": hexc("#b8a8ec"), "V": hexc("#8a7ac8"),  # the same, dyed with the sleep herb
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

# the hunting bow: a sinew-backed recurve (bone nocks, sinew bindings, leather grip at the apex), string from
# top-left to bottom-right like the vanilla bow so it inherits its held pose; then the three draw frames
BOW = [
    ".b...e..........",
    "..ewwheeee......",
    "...S..wSwLe.....",
    "....S.....De....",
    ".....S.....Le...",
    "......S.....D...",
    ".......S.....we.",
    "........S....we.",
    ".........S...Se.",
    "..........S...we",
    "...........S..he",
    "............S.w.",
    ".............Sw.",
    "..............e.",
    "...............b",
    "................",
]
BOW_PULL = [[
    ".b...e..........",
    "..ewwheeee...kl.",
    "...S..wSwLe..wk.",
    "...S......Deh...",
    "....S......he...",
    ".....S....w.D...",
    "......S..h...we.",
    "......S.h....we.",
    "......tw.....Se.",
    "......ttSS....we",
    "..........S...he",
    "...........S..w.",
    "............SSw.",
    "..............e.",
    "...............b",
    "................",
], [
    ".b...e.......kl.",
    "..ewwheeee...hk.",
    "...S..wSwLe.w...",
    "...S......Dh....",
    "....S.....hLe...",
    "....S....w..D...",
    ".....S..h....we.",
    ".....S.h.....we.",
    ".....tw......Se.",
    ".....ttSS.....we",
    ".........S....he",
    "..........SS..w.",
    "............SSw.",
    "..............e.",
    "...............b",
    "................",
], [
    ".b...e........kl",
    "..ewwheeee....hk",
    "...S..wSwLe..h..",
    "...S......Dew...",
    "....S......he...",
    "....S.....h.D...",
    ".....S...w...we.",
    ".....S..h....we.",
    "......Sh.....Se.",
    ".....tw.......we",
    ".....ttSS.....he",
    ".........SS...w.",
    "...........SS.w.",
    ".............Se.",
    "...............b",
    "................",
]]

# arrows: flint head lashed with sinew, rush-fibre fletching; the narcotic one has the herb paste behind the head
# and fletching dyed with the sleep herb's violet
ARROW_ITEM = [
    "................",
    "............kl..",
    "..........kklk..",
    "...........lk...",
    "..........w.k...",
    ".........S......",
    "........w.......",
    ".......h........",
    "......w.........",
    ".....h..........",
    "...uw...........",
    "..uwU...........",
    "..eU............",
    "................",
    "................",
    "................",
]
ARROW_SIDE = [
    ".uu.........k...",
    "uUUu........kl..",
    "ewwwwhwwwwSklllk",
    "uUUu........kl..",
    ".uu.........k...",
]
ARROW_BACK = [
    "u...u",
    ".u.u.",
    "..e..",
    ".u.u.",
    "u...u",
]


def _narcotic(rows, band):
    """The narcotic variant: violet fletching and the green paste on the given shaft pixels."""
    out = [row.replace("u", "v").replace("U", "V") for row in rows]
    for x, y in band:
        out[y] = out[y][:x] + "g" + out[y][x + 1:]
    return out


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


def sprite(rows):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    _paint(img, rows, 0, 0)
    return img


def arrow_texture(side, back):
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    _paint(img, side, 0, 0)
    _paint(img, back, 0, 5)
    return img


def main():
    save_png(dart_texture(), os.path.join(TEX, "entity", "tranq_dart.png"))
    save_png(sprite(BOW), os.path.join(TEX, "item", "hunting_bow.png"))
    for i, rows in enumerate(BOW_PULL):
        save_png(sprite(rows), os.path.join(TEX, "item", f"hunting_bow_pulling_{i}.png"))
    save_png(sprite(ARROW_ITEM), os.path.join(TEX, "item", "flint_arrow.png"))
    save_png(sprite(_narcotic(ARROW_ITEM, [(8, 6), (7, 7)])), os.path.join(TEX, "item", "narcotic_arrow.png"))
    save_png(arrow_texture(ARROW_SIDE, ARROW_BACK), os.path.join(TEX, "entity", "flint_arrow.png"))
    save_png(arrow_texture(_narcotic(ARROW_SIDE, [(7, 2), (8, 2), (9, 2)]), _narcotic(ARROW_BACK, [])),
             os.path.join(TEX, "entity", "narcotic_arrow.png"))
    save_png(tube_texture(), os.path.join(TEX, "item", "blowgun_tube.png"))


if __name__ == "__main__":
    main()
