"""The Daspletosaurus' own saddle art (1.10.1 pilot, 07/11/2026).

Saddle (item terrassic:daspletosaurus_saddle): 16x16, drawn like the other species saddles (rex_extras, carno_extras)
so they read as one family, but its own, the parts of the saddle bone of its model: a deep seat with a high cantle
(the slowest and toughest mount of the mid tyrannosaurs, a saddle you sit IN), on a hide pad of its own mahogany
skin, a bone toggle on the breast strap and an iron stirrup. The egg keeps its generated design for now.

usage: python3 -B tools/spritegen/dasple_extras.py   (sprites.py also calls main())
"""
import os

from rex_extras import TEX

SADDLE_PAL = {
    "o": (30, 18, 14),     # outline
    "d": (46, 28, 18),     # dark oiled leather
    "l": (100, 67, 41),    # leather
    "h": (127, 88, 53),    # leather highlight
    "p": (93, 59, 63),     # the hide pad (its own mahogany skin)
    "P": (118, 82, 79),    # pad light
    "q": (71, 42, 48),     # pad shade
    "b": (185, 170, 136),  # bone toggle
    "B": (221, 208, 176),  # bone light
    "i": (120, 120, 116),  # iron
    "I": (164, 164, 156),  # iron light
}
SADDLE_ART = [
    "................",
    "............oo..",
    "...........ohho.",
    "..oo.......ohlo.",
    ".ohho.....ohldo.",
    ".olldoooooolldo.",
    ".olllhhhhhhlldo.",
    "..oddlllllllddo.",
    ".ooddddddddddooo",
    "oPPPPPPPPPPPPPPo",
    "opPpqpPpqpPpqpPo",
    "oqpqpqoBbooqpqo.",
    ".oqqo..obo.oqo..",
    "..oo...odo..o...",
    ".......oIiIo....",
    ".......oo.oo....",
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
    save_png(saddle_sprite(), os.path.join(TEX, "item", "daspletosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
