"""The TERRASSIC wordmark: stone blocks from the 5x7 font, extruded, with the Rift's amber crack running through."""
import math

import numpy as np
from PIL import Image, ImageFilter

from font import layout
from pixel import hexrgb, mix, noise2d

STONE_TOP = hexrgb("#e8dcc0")
STONE_MID = hexrgb("#b9a27e")
STONE_BOT = hexrgb("#7d6448")
SIDE = hexrgb("#3b2a22")
SIDE_DARK = hexrgb("#24181a")
OUTLINE = hexrgb("#120b10")
AMBER_CORE = hexrgb("#fff4cf")
AMBER = hexrgb("#ffb63c")
AMBER_DEEP = hexrgb("#e0661c")


def wordmark(text="TERRASSIC", block=10, depth=4, seed=5, crack=True):
    """RGBA image at texture resolution (one block = `block` px). Scale up with nearest neighbour."""
    rng = np.random.default_rng(seed)
    cells, (cw, ch) = layout(text)
    pad = depth + 3
    W, H = cw * block + pad * 2, ch * block + pad * 2
    face = np.zeros((H, W), bool)
    for (x, y) in cells:
        face[pad + y * block:pad + (y + 1) * block, pad + x * block:pad + (x + 1) * block] = True
    img = np.zeros((H, W, 3))
    alpha = np.zeros((H, W), bool)
    # extrusion (down and slightly right)
    for d in range(depth, 0, -1):
        sh = np.zeros_like(face)
        sh[d:, d // 2:] = face[:H - d, :W - d // 2]
        side = sh & ~alpha
        img[side] = mix(SIDE, SIDE_DARK, d / depth)
        alpha |= sh
    # front faces: vertical light ramp + stone grain + per-block bevel
    yy, xx = np.mgrid[0:H, 0:W]
    t = np.clip((yy - pad) / (ch * block), 0, 1)
    grain = noise2d(H, W, 2.5, rng, 2)
    base = np.where(t[..., None] < 0.5, mix(STONE_TOP, STONE_MID, t * 2),
                    mix(STONE_MID, STONE_BOT, (t - 0.5) * 2))
    base = base * (1 + grain[..., None] * 0.10)
    by, bx = (yy - pad) % block, (xx - pad) % block
    bev_hi = (by == 0) | (bx == 0)
    bev_lo = (by == block - 1) | (bx == block - 1)
    base[bev_hi] *= 1.10
    base[bev_lo] *= 0.82
    speck = rng.random((H, W)) > 0.93
    base[speck] *= 0.86
    img[face] = base[face]
    alpha |= face
    # the crack of the Rift, running through the whole word
    if crack:
        x, y = pad - 2, pad + ch * block * 0.30
        pts = []
        while x < W - pad + 2:
            pts.append((x, y))
            x += rng.uniform(2, 5)
            y += rng.uniform(-2.2, 2.2) + (pad + ch * block * 0.55 - y) * 0.05
        line = np.zeros((H, W), bool)
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
            for k in range(n + 1):
                line[int(round(y0 + (y1 - y0) * k / n)), int(round(x0 + (x1 - x0) * k / n))] = True
        line |= np.roll(line, 1, 0)
        halo = np.zeros_like(line)
        for dy in (-2, -1, 0, 1, 2):
            for dx in (-1, 0, 1):
                halo |= np.roll(np.roll(line, dy, 0), dx, 1)
        img[halo & face & ~line] = mix(img, AMBER_DEEP, 0.55)[halo & face & ~line]
        img[line & face] = AMBER_CORE
        img[line & alpha & ~face] = AMBER
    # outline
    out = np.zeros_like(alpha)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            out |= np.roll(np.roll(alpha, dy, 0), dx, 1)
    ring = out & ~alpha
    img[ring] = OUTLINE
    alpha |= ring
    rgba = np.dstack([img, alpha * 255.0])
    return Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA")


def glow(img, radius, color=(255, 170, 60), strength=0.8):
    """Soft amber glow from an RGBA image's alpha, same size."""
    a = img.split()[3].filter(ImageFilter.GaussianBlur(radius))
    a = a.point(lambda v: int(min(255, v * strength)))
    g = Image.new("RGBA", img.size, color + (0,))
    g.putalpha(a)
    return g


def caption(text, color="#f3e6c8", shadow="#1a1018"):
    """Small caption in the block font, RGBA at 1 px per cell (scale up with nearest)."""
    cells, (cw, ch) = layout(text)
    im = Image.new("RGBA", (cw + 1, ch + 1), (0, 0, 0, 0))
    px = im.load()
    sc = tuple(int(v) for v in hexrgb(shadow)) + (255,)
    fc = tuple(int(v) for v in hexrgb(color)) + (255,)
    for (x, y) in cells:
        px[x + 1, y + 1] = sc
    for (x, y) in cells:
        px[x, y] = fc
    return im


def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def clean_wordmark(text, cell, color="#f3ead6", shadow=(20, 14, 18, 150), gap=1, spacing=1, bold=False):
    """Plain blocky letters from the 5x7 font: solid colour and a soft drop shadow, nothing else.
    bold doubles every vertical stroke (chunkier letters for the title)."""
    cells, (cw, ch) = layout(text, gap * spacing + (1 if bold else 0))
    if bold:
        cells = sorted(set(cells) | {(x + 1, y) for (x, y) in cells})
        cw += 1
    sh = max(1, cell // 4)
    im = Image.new("RGBA", (cw * cell + sh, ch * cell + sh), (0, 0, 0, 0))
    px = np.zeros((im.height, im.width, 4), np.uint8)
    fc = tuple(int(v) for v in hexrgb(color)) + (255,)
    for (x, y) in cells:
        px[y * cell + sh:(y + 1) * cell + sh, x * cell + sh:(x + 1) * cell + sh] = shadow
    for (x, y) in cells:
        px[y * cell:(y + 1) * cell, x * cell:(x + 1) * cell] = fc
    return Image.fromarray(px, "RGBA")
