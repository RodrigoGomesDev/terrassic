"""The Majungasaurus' own saddle art (1.10.1, 08/11/2026).

Saddle (item terrassic:majungasaurus_saddle): 16x16, drawn like the other species saddles (rex_extras, dasple_extras,
alberto_extras, carcharo_extras) so they read as one family, but its own, the parts of the saddle bone of its model:
the brawler's saddle, a LOW hide seat with a rope grab loop at the front (for when it holds and shakes), a mat of
woven raffia palm fibre with two dyed red-brown stripes, a broad raffia girth and a short bone stirrup. The egg keeps
its generated design for now.

usage: python3 -B tools/spritegen/majunga_extras.py   (sprites.py also calls main())
"""
import os

from rex_extras import TEX

SADDLE_PAL = {
    "o": (30, 22, 17),     # outline
    "d": (70, 48, 31),     # dark leather
    "l": (125, 92, 58),    # leather
    "h": (151, 116, 75),   # leather highlight
    "p": (179, 154, 98),   # the raffia mat
    "P": (204, 180, 124),  # raffia light
    "q": (122, 58, 36),    # the dyed red-brown stripe
    "r": (168, 142, 88),   # raffia rope
    "b": (185, 170, 136),  # bone stirrup
    "B": (221, 208, 176),  # bone light
}
SADDLE_ART = [
    "................",
    "................",
    "................",
    "...ooo..........",
    "..oro.o.........",
    "..oo.ro.........",
    "...ollooooooooo.",
    "...ohhhhhhhhhhlo",
    "..oddllllllllddo",
    ".oooooooooooooo.",
    ".oPpPpPpPpPpPpPo",
    ".oqqqqqqqqqqqqqo",
    ".opPpPpPpPpPpPpo",
    "..ooooooorroooo.",
    ".........oBbo...",
    ".........ooo....",
]


def saddle_sprite():
    from PIL import Image  # lazy, like the other extras
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    for y, row in enumerate(SADDLE_ART):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = SADDLE_PAL[ch] + (255,)
    return img


def main():
    from sprites import save_png
    save_png(saddle_sprite(), os.path.join(TEX, "item", "majungasaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
