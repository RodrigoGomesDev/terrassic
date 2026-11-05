"""The Pocket Guide (v1.1.2, docs/AJUDA.md): the open book behind client/PocketGuideScreen and the 16x16 item.
Own pixel art: a stitched leather cover, two parchment pages shaded toward the sewn spine, the page-turn arrows.
Design approved by Rodrigo on 31/10/2026 (https://claude.ai/artifact/7jPEtKqxLkDr6jf9qdUgmF)."""
import os
import random

from PIL import Image

from rex_extras import TEX
from sprites import save_png, hexc

W, H = 276, 182          # the book on screen, at GUI scale 1 (the screen blits it from a 512x256 sheet)
ARROW_Y = 184            # the four arrows below the book: right, right lit, left, left lit (8x7 each)

LEATHER = [hexc("#5b3a1f"), hexc("#6b4526"), hexc("#4a2f18")]
RIM = hexc("#2e1d0e")
STITCH = hexc("#c8b48a")
PAPER = [hexc("#eadfbf"), hexc("#e4d7b4"), hexc("#efe6c9")]
PAGE_EDGE = [hexc("#cbbd98"), hexc("#b9a984")]
FOLD = [hexc("#8a6a42"), hexc("#5b3a1f")]
ARROW = ["..#.....", "..##....", "######..", "#######.", "######..", "..##....", "..#....."]


def _book(img):
    rnd = random.Random(7)
    px = img.load()
    for y in range(H):
        for x in range(W):
            if (x < 2 or x >= W - 2) and (y < 2 or y >= H - 2):
                continue  # rounded corners
            if x < 2 or y < 2 or x >= W - 2 or y >= H - 2:
                px[x, y] = RIM
            else:
                px[x, y] = LEATHER[rnd.randrange(3)] if rnd.random() < 0.35 else LEATHER[1]
    for x in range(8, W - 8, 4):
        px[x, 4] = STITCH
        px[x, H - 5] = STITCH
    for y in range(8, H - 8, 4):
        px[4, y] = STITCH
        px[W - 5, y] = STITCH
    for x0, x1 in ((9, W // 2 - 1), (W // 2 + 1, W - 9)):
        for y in range(8, H - 9):
            for x in range(x0, x1):
                c = PAPER[0] if rnd.random() < 0.8 else PAPER[rnd.randrange(1, 3)]
                d = min(abs(x - W // 2), 12)
                if d < 12:   # the paper darkens into the fold
                    k = 0.86 + 0.14 * d / 12
                    c = tuple(int(v * k) for v in c[:3]) + (255,)
                px[x, y] = c
        for x in range(x0, x1):
            px[x, H - 9] = PAGE_EDGE[0]
            px[x, H - 8] = PAGE_EDGE[1]
    for y in range(7, H - 7):
        px[W // 2 - 1, y] = FOLD[0]
        px[W // 2, y] = FOLD[1]
        px[W // 2 + 1, y] = FOLD[0]


def _arrows(img):
    for i, (colour, mirror) in enumerate(((hexc("#7a4e22"), False), (hexc("#c0782c"), False),
                                          (hexc("#7a4e22"), True), (hexc("#c0782c"), True))):
        for r, row in enumerate(ARROW):
            for c, ch in enumerate(row):
                if ch == "#":
                    img.putpixel((i * 8 + (7 - c if mirror else c), ARROW_Y + r), colour)


# the item (05/11/2026, Rodrigo: a book in the shape of Minecraft's own books, like Tinkers' "Materials and You"):
# the leather book lying at an angle, the cover on top with bone corners and the amber drop of the Guide, the parchment
# page edges running down one side to the corner and up the other over the dark back cover
ITEM = [
    "................",
    "........DDD.....",
    "......DDlBbD....",
    "....DDlllLLbD...",
    "..DDllLLsLLLLD..",
    "DDBlLLLLaaLLLLD.",
    "DbLLsLLahaALLLLD",
    "DDLLLLLaAALLsDDD",
    "DPDLLLLLALLDDPPD",
    "DpPDsLLLLDDPPpDD",
    ".DpPDssLDPPPpD..",
    "..DpPDDDPPpDD...",
    "...DpPPPpDD.....",
    "....DbBDDD......",
    ".....DDD........",
    "................",
]
ITEM_PAL = {"D": hexc("#2a1a0c"), "L": hexc("#6b4526"), "l": hexc("#845631"), "s": hexc("#4e311a"),
            "B": hexc("#e6dcc2"), "b": hexc("#b5a684"), "P": hexc("#eadfbf"), "p": hexc("#cdbf98"),
            "a": hexc("#e8a33a"), "A": hexc("#a8661a"), "h": hexc("#ffd88a")}


def main():
    sheet = Image.new("RGBA", (512, 256), (0, 0, 0, 0))
    _book(sheet)
    _arrows(sheet)
    save_png(sheet, os.path.join(TEX, "gui", "pocket_guide.png"))
    item = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(ITEM):
        for x, ch in enumerate(row):
            if ch != ".":
                item.putpixel((x, y), ITEM_PAL[ch])
    save_png(item, os.path.join(TEX, "item", "pocket_guide.png"))


if __name__ == "__main__":
    main()
