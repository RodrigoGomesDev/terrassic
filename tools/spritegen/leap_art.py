"""
Art of v0.9 "The End" (docs/SALTO.md), drawn by code:

  textures/entity/rift_overlay.png  128x128  amber cracks for the creatures of the Rift (client/RiftLayer). Drawn
                                             additive at full brightness over any model, so black = nothing; the
                                             cracks follow each model's own UV layout (one texture for every species).
  textures/entity/meteor.png         16x16   the burning rock of the ritual (client/MeteorRenderer), a cutout sprite.

The Leap Altar block uses the existing textures of the mod (stacked limestone, ossuary wall, tanned hide, amber),
so it needs no new block art.

usage:  python3 leap_art.py [--preview out.png]
"""
import math
import os
import random
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ENTITY = os.path.join(HERE, "..", "..", "common", "src", "main", "resources", "assets", "terrassic", "textures", "entity")


def rift_overlay(size=128, seed="rift-v09"):
    """Branching cracks: a bright amber core line with a dim halo, on black (transparent). Tileable."""
    rnd = random.Random(seed)
    core = [[0.0] * size for _ in range(size)]

    def crack(x, y, angle, steps, depth):
        for _ in range(steps):
            core[int(y) % size][int(x) % size] = 1.0
            angle += rnd.uniform(-0.3, 0.3)
            x += math.cos(angle)
            y += math.sin(angle)
            if depth < 1 and rnd.random() < 0.035:
                crack(x, y, angle + rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.2), steps // 2, depth + 1)

    cell = size / 4
    for gy in range(4):  # one crack per cell of a 4x4 grid, so they spread evenly over the whole texture
        for gx in range(4):
            crack((gx + rnd.random()) * cell, (gy + rnd.random()) * cell, rnd.uniform(0, math.tau), rnd.randint(18, 40), 0)
    # small sparks: single glowing grains, like amber dust under the skin
    for _ in range(50):
        y, x = rnd.randrange(size), rnd.randrange(size)
        core[y][x] = max(core[y][x], 0.6)

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    for y in range(size):
        for x in range(size):
            c = core[y][x]
            halo = 0.0
            if c < 1.0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if core[(y + dy) % size][(x + dx) % size] >= 1.0:
                        halo = 0.38
                        break
            v = max(c, halo)
            if v <= 0.0:
                continue
            if v >= 1.0:
                rgb = (255, 206, 96)
            elif v >= 0.5:
                rgb = (232, 150, 50)
            else:
                rgb = (120, 58, 16)
            px[x, y] = rgb + (255,)
    return img


METEOR = [
    "......yyyy......",
    "....yyooooyy....",
    "...yoorrrrooy...",
    "..yorrdddddroy..",
    ".yordddkkdddroy.",
    ".yordkkkkkkdroy.",
    "yordkkLkkkkkdroy",
    "yordkkkLLkkkdroy",
    "yordkkkkkLkkdroy",
    "yordkLkkkkkkdroy",
    ".yordkLLkkkdroy.",
    ".yorddkkkkddroy.",
    "..yorrddddrroy..",
    "...yoorrrrooy...",
    "....yyooooyy....",
    "......yyyy......",
]
METEOR_PAL = {
    ".": (0, 0, 0, 0),
    "y": (255, 230, 120, 255),   # the burning rim
    "o": (255, 160, 40, 255),
    "r": (214, 82, 24, 255),
    "d": (92, 40, 26, 255),      # the rock
    "k": (46, 26, 22, 255),
    "L": (255, 120, 30, 255),    # lava in the cracks
}


def meteor():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(METEOR):
        for x, ch in enumerate(row):
            img.putpixel((x, y), METEOR_PAL[ch])
    return img


def main():
    os.makedirs(ENTITY, exist_ok=True)
    overlay = rift_overlay()
    overlay.save(os.path.join(ENTITY, "rift_overlay.png"))
    rock = meteor()
    rock.save(os.path.join(ENTITY, "meteor.png"))
    print("leap art:", os.path.normpath(ENTITY))
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        sheet = Image.new("RGBA", (128 * 2 + 16 * 8 + 24, 256), (20, 16, 20, 255))
        sheet.paste(overlay.resize((256, 256), Image.NEAREST), (0, 0), overlay.resize((256, 256), Image.NEAREST))
        big = rock.resize((128, 128), Image.NEAREST)
        sheet.paste(big, (256 + 12, 64), big)
        sheet.save(out)


if __name__ == "__main__":
    main()
