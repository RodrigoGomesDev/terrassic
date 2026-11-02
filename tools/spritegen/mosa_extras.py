"""The Mosasaurus' own item art (2026-11-02, the 1.5 remake; its study page, "Mosassauro 1.5").

No egg block: the Mosasaurus bears live young at sea (the calf is born beside its mother's tail), so there is no nest
and no CUSTOM_EGGS here. Its spawn egg is the front view in egg_designs.mosasaurus().

Saddle (item terrassic:mosasaurus_saddle): the diving harness of the model, in the model's own colours
(tools/modelgen/handmade/mosasaurus/mosa.py SADDLE_PAL): the pad of dark oiled sea-hide with its stitched edge and the
low cantle at the back, the hand cord in front with its bone toggle, the girth of twisted dried kelp hanging in a loop
(it goes round the chest behind the front flippers), and the swim-bladder float tied at the side, the air the rider
breathes when it goes under. No wood, no basket, no felt, no rush, no metal.

usage: python3 -B tools/spritegen/mosa_extras.py   (sprites.py also calls main())
"""
import os

from rex_extras import TEX


def _hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


SADDLE_PAL = {
    "x": _hx("1a1512"),                                                   # outline
    "o": _hx("2b2420"), "O": _hx("3d332c"), "p": _hx("52463b"), "h": _hx("67594b"), "s": _hx("7d6c5a"),  # oiled hide
    "k": _hx("2e3320"), "K": _hx("454a2c"), "g": _hx("5d6039"),           # dried-kelp cord
    "b": _hx("6e5a3a"), "B": _hx("8c7650"), "f": _hx("a69067"), "F": _hx("bfa97f"), "w": _hx("e2d6b4"),  # the float
    "t": _hx("cbbf9f"), "T": _hx("9c917a"),                               # bone toggle
}

SADDLE_ART = [
    "................",
    "..kk.......xx...",
    ".tTKk.....xhsx..",
    ".Tk.K....xhpOx..",
    "..k.xxxxxhppOx..",
    "...xhshshpppOox.",
    "..xspppppppOOox.",
    "..xpOOOOOOOOoox.",
    "...xxoooooooxx..",
    "....xKx...xKx...",
    "....xKg..xwFx...",
    "....xgK.xwFFfx..",
    ".....xKgxFffBx..",
    ".....xkKKxfBbx..",
    "......xkkkxbx...",
    "...........x....",
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
    save_png(saddle_sprite(), os.path.join(TEX, "item", "mosasaurus_saddle.png"))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
