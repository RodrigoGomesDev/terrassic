"""Sprites of the alphas' aura (client/AlphaMoteParticle, docs/ALFAS.md, v1.6). Rodrigo 02/11/2026: the vanilla dust and
flame "nao ficou tao bom, o bicho tem que ter aura". Four 16x16 frames, white (the particle tints them with the alpha's
own coat colours), alpha in a few hard steps so they stay pixel art at any distance:
  0 block - a 4x4 beveled square speck (round 3: no circles, Minecraft-like)
  1 chip  - a 2x2 square speck
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


def block(n):
    """v1.6, round 3 (Rodrigo 02/11: "mais sucinto e mais minecraft, sem círculos"): a square speck of n x n pixels,
    beveled like a Minecraft block (light top and left edge, dark bottom and right), inside a dark outline."""
    o = 8 - n // 2
    pts = {}
    for y in range(n):
        for x in range(n):
            g = 215
            if x == 0 or y == 0:
                g = 255
            if x == n - 1 or y == n - 1:
                g = 140
            pts[(o + x, o + y)] = g
    return outlined(pts)


def outlined(points):
    """Lit pixels {(x, y): grey} with a dark outline around them, so a thin shape holds against the sky."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for (x, y) in points:
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                p = (x + ox, y + oy)
                if p not in points and 0 <= p[0] < 16 and 0 <= p[1] < 16:
                    img.putpixel(p, (60, 60, 60, 190))
    for (x, y), g in points.items():
        img.putpixel((x, y), (g, g, g, 255))
    return img


def glint():
    """A small plus, the twinkling spark (one arm a pixel longer)."""
    pts = {(7, 8): 255, (7, 7): 235, (7, 6): 200, (7, 5): 160, (8, 8): 230, (9, 8): 170, (6, 8): 230, (5, 8): 170,
           (7, 9): 230, (7, 10): 170}
    return outlined(pts)


def flake():
    lit = {(7, 7): 255, (8, 7): 240, (7, 8): 200, (6, 7): 225, (8, 6): 250, (9, 8): 150, (6, 9): 140,
           (8, 8): 170, (7, 6): 255, (9, 7): 190, (5, 8): 160, (8, 9): 130, (10, 9): 120, (6, 6): 235}
    return outlined(lit)


def main():
    os.makedirs(OUT, exist_ok=True)
    frames = [block(4), block(2), glint(), flake()]
    for i, img in enumerate(frames):
        img.save(os.path.join(OUT, f"alpha_mote_{i}.png"))
    print(f"alfa_aura: {len(frames)} frames -> {OUT}")


if __name__ == "__main__":
    main()
