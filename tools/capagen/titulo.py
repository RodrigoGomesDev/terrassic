"""
The TERRASSIC title in "Degraus", the approved title face (2026-10-25): stepped capitals of worn stone, each letter on
its own step (glyphs in tools/fontgen/degraus.py, drawing in letreiro.py). Four finishes: "pedra", "osso", "ambar" and
"basalto" ("fossil", the old bone finish, maps to "osso"). The slogan uses the same face, lightly worn.
"""
import numpy as np
from PIL import Image

import letreiro
from pixel import hexrgb

FINISHES = tuple(letreiro.FILLS)
ALIASES = {"fossil": "osso"}


def title(text="TERRASSIC", finish="pedra", texel=2, age=1.0):
    """RGBA title in Degraus; texel = 2 gives the cover size (about 970 px wide for TERRASSIC)."""
    return letreiro.image(text, ALIASES.get(finish, finish), s=texel * 5, age=age)


def title_in(W, H, finish="pedra", text="TERRASSIC", align="left", top=None, age=1.0):
    """The title at the largest whole block size that fits a W x H texture (one block of air around it), on a
    transparent W x H canvas: left-aligned or centred; centred vertically, or `top` px from the top. For game textures
    of a fixed size."""
    f = ALIASES.get(finish, finish)
    w1, h1 = letreiro.image(text, f, s=1, age=0, pad=1).size
    s = max(1, min(W // w1, H // h1))
    t = letreiro.image(text, f, s=s, age=age, pad=1)
    out = Image.new("RGBA", (W, H))
    out.alpha_composite(t, ((W - t.width) // 2 if align == "center" else 0, (H - t.height) // 2 if top is None else top))
    return out


SLOGANS = {
    "pt_br": "O PASSADO ACORDOU.",
    "en_us": "THE PAST HAS AWOKEN.",
    "es_es": "EL PASADO DESPERTÓ.",
}


def slogan(text, cell=4, finish="osso", age=0.45):
    """Slogan in Degraus at a small size and lightly worn, so it still reads (cell = screen px per stone block / 1.33)."""
    return letreiro.image(text, ALIASES.get(finish, finish), s=max(2, round(cell * 0.75)), age=age, seed=5)


def slogan_blocos(text, cell=4, color="#d8ccb2", shadow=(10, 8, 6, 200), spacing=2):
    """The old slogan in the 5x7 block font (with accents), widely spaced, with a soft shadow."""
    from font import layout_text
    cells, (cw, ch) = layout_text(text, spacing)
    sh = max(1, cell // 2)
    px = np.zeros((ch * cell + sh, cw * cell + sh, 4), np.uint8)
    fc = tuple(int(v) for v in hexrgb(color)) + (255,)
    for (x, y) in cells:
        px[y * cell + sh:(y + 1) * cell + sh, x * cell + sh:(x + 1) * cell + sh] = shadow
    for (x, y) in cells:
        px[y * cell:(y + 1) * cell, x * cell:(x + 1) * cell] = fc
    return Image.fromarray(px, "RGBA")
