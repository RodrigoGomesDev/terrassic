"""The Carcharodontosaurus' own saddle art (1.10.1, 08/11/2026).

Saddle (item terrassic:carcharodontosaurus_saddle): 16x16, drawn like the other species saddles (rex_extras,
dasple_extras, alberto_extras) so they read as one family, but its own, the parts of the saddle bone of its model: the
river-plain saddle, a deep hide seat with a HIGH POMMEL to brace on when it bursts out of the ambush, a woven blanket of
undyed wool with a dark border, a rope girth and a bone stirrup. The egg keeps its generated design for now.

usage: python3 -B tools/spritegen/carcharo_extras.py   (sprites.py also calls main())
"""
import os

from rex_extras import TEX

SADDLE_PAL = {
    "o": (30, 22, 17),     # outline
    "d": (70, 48, 31),     # dark leather
    "l": (125, 92, 58),    # leather
    "h": (151, 116, 75),   # leather highlight
    "p": (149, 134, 112),  # the woven wool blanket
    "P": (179, 165, 140),  # blanket light
    "q": (90, 60, 52),     # the blanket's dark woven border
    "r": (141, 122, 86),   # rope
    "b": (185, 170, 136),  # bone stirrup
    "B": (221, 208, 176),  # bone light
}
SADDLE_ART = [
    "................",
    "................",
    "...oo...........",
    "..ohho..........",
    "..ohlo.......oo.",
    "..olldoooooo.olo",
    "..ollhhhhhhhhldo",
    "...oddlllllllddo",
    "..oooddddddddoo.",
    ".oqqqqqqqqqqqqqo",
    ".oqPpPpPpPpPpPqo",
    ".oqpPpPpPpPpPpqo",
    "..oqqqqo.orooqqo",
    "........oro.....",
    ".......oBbBo....",
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


# the bleeding effect's icon (18x18, textures/mob_effect/bleeding.png): a drop of blood falling from a serrated cut
BLEED_PAL = {
    "o": (46, 10, 12),     # outline
    "r": (138, 24, 26),    # blood
    "R": (184, 44, 40),    # blood light
    "w": (232, 190, 176),  # glint
    "c": (92, 16, 18),     # the cut
}
BLEED_ART = [
    "..................",
    "..oo.oo.oo.oo.oo..",
    ".ocrocrocrocrocro.",
    "..oo.oo.oo.oo.oo..",
    "........o.........",
    ".......oro........",
    ".......oro........",
    "......orrro.......",
    ".....orRrrro......",
    "....orRRrrrro.....",
    "....orwRrrrro.....",
    "...orRwRrrrrro....",
    "...orRRrrrrrro....",
    "...orrrrrrrrco....",
    "....orrrrrrco.....",
    ".....orrrrco......",
    "......ooooo.......",
    "..................",
]


def bleeding_icon():
    from PIL import Image
    img = Image.new("RGBA", (18, 18))
    px = img.load()
    for y, row in enumerate(BLEED_ART):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = BLEED_PAL[ch] + (255,)
    return img


def main():
    from sprites import save_png
    save_png(saddle_sprite(), os.path.join(TEX, "item", "carcharodontosaurus_saddle.png"))
    os.makedirs(os.path.join(TEX, "mob_effect"), exist_ok=True)
    save_png(bleeding_icon(), os.path.join(TEX, "mob_effect", "bleeding.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
