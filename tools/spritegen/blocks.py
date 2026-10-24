"""
Terrassic 16x16 tileable textures for the primitive building blocks (thatch, wattle and daub, log palisade,
dry stone, bone fence, hide screen, fur rug, straw mat).  Everything is drawn with code (no external art).

usage: python3 blocks.py [preview.png]   -> writes into common/src/main/resources/assets/terrassic/textures/block
"""
import os
import random
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from sprites import Canvas, hexc, shade, mixc  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEX = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "block")


def noise(cv, rnd, base, lo=0.92, hi=1.06):
    for y in range(16):
        for x in range(16):
            cv.set(x, y, shade(base, lo + (hi - lo) * rnd.random()))


# ------------------------------------------------------------------ thatch (palha)
STRAW = hexc("#c9a54e"); STRAW_L = hexc("#e6c873"); STRAW_D = hexc("#8e6f2c"); STRAW_DD = hexc("#5f4a1e")


def thatch():
    """Overlapping bundles of straw: 4 rows, each bundle hangs over the one below (dark lip at its bottom)."""
    rnd = random.Random("thatch")
    cv = Canvas()
    for y in range(16):
        row = y % 4
        for x in range(16):
            # vertical strands, staggered per row so the seams do not line up
            strand = (x + (y // 4) * 2) % 3
            c = (STRAW_L, STRAW, shade(STRAW, 0.9))[strand]
            if row == 3:
                c = STRAW_D if rnd.random() < 0.7 else STRAW_DD
            elif row == 0 and rnd.random() < 0.25:
                c = STRAW_L
            cv.set(x, y, shade(c, 0.95 + 0.1 * rnd.random()))
    # a few loose straws crossing the lips
    for _ in range(6):
        x, y = rnd.randrange(16), rnd.choice((3, 7, 11, 15))
        cv.set(x, y, STRAW)
    return cv


def thatch_top():
    """Top of the thatch: straw lying flat, mostly horizontal strands."""
    rnd = random.Random("thatch_top")
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            c = (STRAW, STRAW_L, STRAW, shade(STRAW, 0.85))[(y + (x // 5)) % 4]
            cv.set(x, y, shade(c, 0.94 + 0.1 * rnd.random()))
    for _ in range(10):
        x, y = rnd.randrange(16), rnd.randrange(16)
        cv.set(x, y, STRAW_D)
    return cv


# ------------------------------------------------------------------ wattle and daub (pau-a-pique)
DAUB = hexc("#9c7a55"); DAUB_L = hexc("#b8956a"); DAUB_D = hexc("#6e5238")
STICK = hexc("#7a5530"); STICK_L = hexc("#9a6e40"); STICK_D = hexc("#4e341a")


def wattle_daub():
    """Mud plaster over woven sticks: timber frame on the border, woven sticks showing through cracks."""
    rnd = random.Random("wattle")
    cv = Canvas()
    noise(cv, rnd, DAUB, 0.9, 1.08)
    # plaster lumps
    for _ in range(14):
        x, y = rnd.randrange(1, 15), rnd.randrange(1, 15)
        cv.set(x, y, DAUB_L); cv.set(x + 1, y, DAUB_L); cv.set(x, y + 1, DAUB_D)
    # woven sticks peeking through (horizontal weave in the middle band)
    for y in (5, 10):
        for x in range(2, 14):
            if (x // 3 + y) % 2 == 0 and rnd.random() < 0.85:
                cv.set(x, y, STICK_L if x % 3 == 0 else STICK)
                cv.set(x, y + 1, STICK_D)
    # timber frame: posts left/right, beams top/bottom
    for i in range(16):
        cv.set(i, 0, STICK_L); cv.set(i, 15, STICK_D)
        cv.set(0, i, STICK); cv.set(15, i, STICK_D)
    return cv


# ------------------------------------------------------------------ log palisade (paliçada)
BARK = hexc("#5e4428"); BARK_L = hexc("#7c5c36"); BARK_D = hexc("#3c2a16")
WOOD_CUT = hexc("#c09a62"); WOOD_RING = hexc("#9c7744")


def palisade_side():
    """Bark of a rough, unbarked log: long vertical grooves."""
    rnd = random.Random("palisade")
    cv = Canvas()
    for x in range(16):
        groove = rnd.random() < 0.3
        for y in range(16):
            c = BARK_D if groove else (BARK_L if rnd.random() < 0.18 else BARK)
            cv.set(x, y, shade(c, 0.93 + 0.1 * rnd.random()))
    for _ in range(4):  # knots
        x, y = rnd.randrange(2, 14), rnd.randrange(2, 14)
        cv.set(x, y, BARK_D); cv.set(x, y + 1, shade(BARK_D, 0.8))
    return cv


def palisade_top():
    """Cut end of the log, sharpened: light wood with rings and an axe-hewn bevel."""
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            d = max(abs(x - 7.5), abs(y - 7.5))
            if d > 6.5:
                c = BARK
            elif int(d) % 3 == 0:
                c = WOOD_RING
            else:
                c = WOOD_CUT
            cv.set(x, y, c)
    for i in range(3, 13):  # hatchet marks
        cv.set(i, i, shade(WOOD_RING, 0.85))
    return cv


# ------------------------------------------------------------------ dry stone (pedra empilhada)
STONE = hexc("#8a8780"); STONE_L = hexc("#a8a59c"); STONE_D = hexc("#5e5c56"); GAP = hexc("#2e2c28")
# irregular stones as rectangles (x0, y0, x1, y1), tiling across the edges of the 16x16 block
STONES = [(0, 0, 6, 3), (8, 0, 15, 4), (0, 5, 4, 9), (6, 5, 11, 8), (13, 6, 15, 10),
          (6, 10, 11, 14), (0, 11, 4, 15), (13, 12, 15, 15)]


def dry_stone():
    """Stacked, unmortared stones: dark gaps, each stone with its own tone, lit from top-left."""
    rnd = random.Random("dry_stone")
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            cv.set(x, y, GAP)
    for (x0, y0, x1, y1) in STONES:
        tone = shade(mixc(STONE, hexc("#8f8270"), rnd.random() * 0.5), 0.9 + 0.2 * rnd.random())
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                c = shade(tone, 0.95 + 0.08 * rnd.random())
                if y == y0 or x == x0:
                    c = mixc(c, STONE_L, 0.5)
                if y == y1 or x == x1:
                    c = mixc(c, STONE_D, 0.6)
                cv.set(x, y, c)
        # round the corners a bit
        cv.set(x1, y1, GAP)
    # moss specks
    for _ in range(5):
        cv.set(rnd.randrange(16), rnd.randrange(16), hexc("#5f6e3a"))
    return cv


# ------------------------------------------------------------------ bone fence (cerca de osso)
BONE = hexc("#e8e0c8"); BONE_D = hexc("#b8ad90"); BONE_L = hexc("#fbf6e8"); SINEW = hexc("#8a5a34")


def bone_fence():
    """Bone surface with knobbly joints and sinew lashings (used by the fence post and rails)."""
    rnd = random.Random("bone_fence")
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            c = BONE_L if x % 4 == 1 else (BONE_D if x % 4 == 3 else BONE)
            cv.set(x, y, shade(c, 0.96 + 0.06 * rnd.random()))
    for y in (0, 15):  # joints
        for x in range(16):
            cv.set(x, y, BONE_D)
    for y in (3, 4, 10, 11):  # sinew lashing
        for x in range(16):
            cv.set(x, y, SINEW if (x + y) % 2 else shade(SINEW, 0.8))
    return cv


# ------------------------------------------------------------------ hide screen (painel de couro)
HIDE = hexc("#a0703e"); HIDE_L = hexc("#bf8a52"); HIDE_D = hexc("#74502a"); STITCH = hexc("#e0d2b0")


def hide_screen():
    """Stretched hide lashed to a stick frame: frame on the border, stitches near the edges."""
    rnd = random.Random("hide")
    cv = Canvas()
    noise(cv, rnd, HIDE, 0.9, 1.06)
    for _ in range(8):  # natural blotches of the hide
        x, y = rnd.randrange(2, 14), rnd.randrange(2, 14)
        cv.set(x, y, HIDE_L); cv.set(x + 1, y, HIDE_L); cv.set(x, y + 1, HIDE_D)
    for i in range(16):
        cv.set(0, i, STICK); cv.set(15, i, STICK_D)
    for i in range(2, 15, 3):  # lashing from the hide to the posts
        cv.set(1, i, STITCH); cv.set(14, i, STITCH)
    return cv


def hide_screen_edge():
    """Edge of the hide panel (pane 'top' texture): just the frame stick."""
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            cv.set(x, y, STICK if x % 4 else STICK_D)
    return cv


# ------------------------------------------------------------------ fur rug (tapete de pele)
FUR = hexc("#7a5a3a"); FUR_L = hexc("#a07a50"); FUR_D = hexc("#4e3820")


def fur_rug():
    """Shaggy fur: short diagonal tufts in three tones."""
    rnd = random.Random("fur")
    cv = Canvas()
    noise(cv, rnd, FUR, 0.88, 1.04)
    for _ in range(26):
        x, y = rnd.randrange(16), rnd.randrange(16)
        cv.set(x, y, FUR_L); cv.set(x + 1, y + 1, FUR_D)
    return cv


# ------------------------------------------------------------------ straw mat (esteira de palha)
def straw_mat():
    """Woven straw mat: 4x4 basket weave."""
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            horizontal = ((x // 4) + (y // 4)) % 2 == 0
            k = (y % 4) if horizontal else (x % 4)
            c = (STRAW_L, STRAW, STRAW, STRAW_D)[k]
            cv.set(x, y, c)
    return cv


TEXTURES = {
    "thatch": thatch, "thatch_top": thatch_top, "wattle_and_daub": wattle_daub,
    "log_palisade": palisade_side, "log_palisade_top": palisade_top, "dry_stone": dry_stone,
    "bone_fence": bone_fence, "hide_screen": hide_screen, "hide_screen_edge": hide_screen_edge,
    "fur_rug": fur_rug, "straw_mat": straw_mat,
}


def build():
    out = {}
    for name, fn in TEXTURES.items():
        cv = fn()
        cv.save(os.path.join(TEX, f"{name}.png"))
        out[name] = cv
    return out


def preview(path, out):
    """Each texture upscaled 6x, tiled 2x2 so seams are visible."""
    cell = 16 * 6 * 2 + 12
    cols = 4
    rows = (len(out) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (60, 60, 68, 255))
    for i, name in enumerate(out):
        im = Image.open(os.path.join(TEX, f"{name}.png")).resize((96, 96), Image.NEAREST)
        ox, oy = (i % cols) * cell + 6, (i // cols) * cell + 6
        for tx in range(2):
            for ty in range(2):
                sheet.alpha_composite(im, (ox + tx * 96, oy + ty * 96))
    sheet.save(path)


if __name__ == "__main__":
    textures = build()
    if len(sys.argv) > 1:
        preview(sys.argv[1], textures)
    print("block textures written to", TEX)
