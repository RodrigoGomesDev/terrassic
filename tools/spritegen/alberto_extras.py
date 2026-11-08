"""The Albertosaurus' own saddle art (1.10.1, 08/11/2026).

Saddle (item terrassic:albertosaurus_saddle): 16x16, drawn like the other species saddles (rex_extras,
dasple_extras) so they read as one family, but its own, the parts of the saddle bone of its model: the light racing
saddle of the runner, a low seat with a small pommel and a low cantle on a thin felt pad of its fir-green skin, short
flaps, and a bone stirrup. The egg keeps its generated design for now.

usage: python3 -B tools/spritegen/alberto_extras.py   (sprites.py also calls main())
"""
import os

from rex_extras import TEX

SADDLE_PAL = {
    "o": (28, 22, 16),     # outline
    "d": (44, 33, 22),     # dark leather
    "l": (106, 82, 54),    # tan leather
    "h": (134, 106, 70),   # leather highlight
    "p": (77, 90, 76),     # the felt pad (its own fir green)
    "P": (102, 116, 95),   # pad light
    "q": (52, 64, 54),     # pad shade
    "b": (185, 170, 136),  # bone stirrup
    "B": (221, 208, 176),  # bone light
}
SADDLE_ART = [
    "................",
    "................",
    "................",
    "...oo...........",
    "..ohho......oo..",
    "..olldoooooohlo.",
    "..ollhhhhhhhldo.",
    "...oddlllllddo..",
    "..oooddddddooo..",
    ".oPPPPPPPPPPPPo.",
    ".opPpqpPpqpPpqo.",
    "..oqpqo.oqpqo...",
    "...oo..odo.oo...",
    ".......odo......",
    "......oBbBo.....",
    "......oo.oo.....",
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
    save_png(saddle_sprite(), os.path.join(TEX, "item", "albertosaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
