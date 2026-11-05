"""The Elasmosaurus' own item art (05/11/2026, the 1.8 remake; its study page, "Elasmossauro: estudo para a 1.8").

No egg block: it gives birth to live young at sea (the pregnant Polycotylus, O'Keefe & Chiappe 2011).

Saddle (item terrassic:elasmosaurus_saddle): the neck saddle of the model: the hide seat with its raised cantle, the
rope loop that goes round the neck, and a float of lashed driftwood on the side. Not the Mosasaurus' swim-bladder
floats: bleached grey wood.

usage: python3 -B tools/spritegen/elas_extras.py   (sprites.py also calls main())
"""
import os

from rex_extras import TEX

SADDLE_PAL = {"o": (30, 24, 18), "h": (85, 63, 44), "H": (110, 84, 60), "j": (138, 108, 78),
              "r": (106, 90, 62), "R": (142, 124, 86), "d": (110, 102, 90), "D": (142, 134, 120), "E": (194, 187, 174)}
SADDLE_ART = [
    "................",
    "..ooo...........",
    ".oRRRo..........",
    "oR...Ro.........",
    "oR....Ro..ooo...",
    "oR.....oooHHjo..",
    ".oR...ohhHHHjo..",
    "..oR.ohHHHHjHo..",
    "...ooohhhhhhho..",
    "....ooroooroo...",
    "...oDDDDDDDDDo..",
    "..oEDEDDEDDEDo..",
    "..oDDdDDDdDDDo..",
    "...ooooooooooo..",
    "................",
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


def main():
    from sprites import save_png
    save_png(saddle_sprite(), os.path.join(TEX, "item", "elasmosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
