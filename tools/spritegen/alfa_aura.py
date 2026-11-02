"""Sprites of the alphas' aura (client/AlphaMoteParticle, docs/ALFAS.md, v1.6). Rodrigo 02/11/2026: the vanilla dust and
flame "nao ficou tao bom, o bicho tem que ter aura". Four 16x16 frames, white (the particle tints them with the alpha's
own coat colours), alpha in a few hard steps so they stay pixel art at any distance:
  0 haze  - a wide soft blot, the heat coming off the hide
  1 mote  - a smaller round glow with a bright core
  2 glint - a four-pointed glint, crooked on purpose (one arm longer), the spark that twinkles
  3 flake - an irregular flake of ash or ember, five pixels lit around a hot one
Run: python3 tools/spritegen/alfa_aura.py
"""
import math
import os

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "particle")
# v1.6 fix: the vanilla particle shader discards anything under 10% opacity (texture x particle alpha), so the lit
# steps start at 110/255 and the glows fill most of the frame
STEPS = (0, 110, 170, 215, 240, 255)


def step(a):
    """Snap an alpha 0..1 to the nearest hard step."""
    v = max(0.0, min(1.0, a)) * 255
    return min(STEPS, key=lambda s: abs(s - v))


def glow(radius, core, wobble=0.0):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            ang = math.atan2(dy, dx)
            r = math.hypot(dx, dy) / (radius * (1.0 + wobble * math.sin(ang * 3 + 0.7)))
            a = (1.0 - r) ** 0.8 if r < 1.0 else 0.0
            if r < core:
                a = 1.0
            img.putpixel((x, y), (255, 255, 255, step(a)))
    return img


def glint():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    arms = {(0, -1): 6, (1, 0): 4, (0, 1): 4, (-1, 0): 5}   # the upper arm is the long one
    for (ax, ay), n in arms.items():
        for i in range(1, n + 1):
            img.putpixel((7 + ax * i, 8 + ay * i), (255, 255, 255, step(1.0 - i / (n + 1.5))))
    for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        img.putpixel((7 + dx, 8 + dy), (255, 255, 255, step(0.6)))
    for dx, dy in ((1, -1), (1, -2), (-1, 1), (1, 1)):   # a thicker heart, so it reads from afar
        img.putpixel((7 + dx, 8 + dy), (255, 255, 255, step(0.8)))
    img.putpixel((7, 8), (255, 255, 255, 255))
    return img


def flake():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    lit = {(7, 7): 1.0, (8, 7): 0.95, (7, 8): 0.9, (6, 7): 0.8, (8, 6): 0.75, (9, 8): 0.6, (6, 9): 0.55,
           (8, 8): 0.9, (7, 6): 0.7, (9, 7): 0.6, (5, 8): 0.5, (8, 9): 0.5, (10, 9): 0.45, (6, 6): 0.45}
    for (x, y), a in lit.items():
        img.putpixel((x, y), (255, 255, 255, step(a)))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    frames = [glow(7.6, 0.0, 0.05), glow(6.5, 0.4), glint(), flake()]
    for i, img in enumerate(frames):
        img.save(os.path.join(OUT, f"alpha_mote_{i}.png"))
    print(f"alfa_aura: {len(frames)} frames -> {OUT}")


if __name__ == "__main__":
    main()
