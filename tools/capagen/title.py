"""
Title-screen art (v0.8, phase M2): the TERRASSIC logo the title screen draws instead of the Minecraft one, and a preview
of the whole screen (panorama as the game shows it + logo + subtitle) for review.

usage:  python3 panorama.py && python3 title.py
        -> common/src/main/resources/assets/terrassic/textures/gui/title/terrassic.png  (256x64, drawn 1:1)
        -> art/capa/tela_titulo_preview.png and art/capa/panorama_vistas.png (four directions of the panorama)
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import logo  # noqa: E402
import panorama as P  # noqa: E402

TITLE = os.path.join(P.r3.ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "gui", "title")
PREVIEW = os.path.join(P.r3.ROOT, "art", "capa", "tela_titulo_preview.png")
VIEWS = os.path.join(P.r3.ROOT, "art", "capa", "panorama_vistas.png")


def logo_texture():
    """256x64 RGBA: the stone wordmark with the Rift's crack and an amber glow, centred, top 4 px of margin."""
    mark = logo.wordmark("TERRASSIC", block=4, depth=2)
    canvas = Image.new("RGBA", (256, 64), (0, 0, 0, 0))
    x, y = (256 - mark.width) // 2, 6
    layer = Image.new("RGBA", (256, 64), (0, 0, 0, 0))
    layer.paste(mark, (x, y), mark)
    canvas = Image.alpha_composite(canvas, logo.glow(layer, 3, strength=0.55))
    return Image.alpha_composite(canvas, layer)


def view(spin, W=854, H=480):
    """What the vanilla CubeMap camera shows: 85 degrees vertical field of view, looking 10 degrees down."""
    faces = [np.asarray(Image.open(os.path.join(P.OUT, f"panorama_{k}.png")).convert("RGB")) for k in range(6)]
    F = faces[0].shape[0]
    fy = math.tan(math.radians(85 / 2))
    fx = fy * W / H
    gx, gy = np.meshgrid(((np.arange(W) + 0.5) / W * 2 - 1) * fx, -((np.arange(H) + 0.5) / H * 2 - 1) * fy)
    d = np.stack([-gx, gy, np.ones_like(gx)], -1)
    p = math.radians(-10)
    d = np.stack([d[..., 0], d[..., 1] * math.cos(p) + d[..., 2] * math.sin(p),
                  -d[..., 1] * math.sin(p) + d[..., 2] * math.cos(p)], -1)
    a = math.radians(spin)
    d = np.stack([d[..., 0] * math.cos(a) + d[..., 2] * math.sin(a), d[..., 1],
                  -d[..., 0] * math.sin(a) + d[..., 2] * math.cos(a)], -1)
    c = P.to_cube(d)
    out = np.zeros((H, W, 3), np.uint8)
    best = np.full((H, W), -1e9)
    for k, (n, ua, vb) in enumerate(P.FACES):
        depth = c @ n
        u = (c @ ua / np.maximum(depth, 1e-6) + 1) / 2
        v = (c @ vb / np.maximum(depth, 1e-6) + 1) / 2
        ok = (depth > 0) & (u >= 0) & (u < 1) & (v >= 0) & (v < 1) & (depth > best)
        iu = np.clip((u * F).astype(int), 0, F - 1)
        iv = np.clip((v * F).astype(int), 0, F - 1)
        out[ok] = faces[k][iv[ok], iu[ok]]
        best[ok] = depth[ok]
    return Image.fromarray(out)


def preview(tex):
    """Title screen at GUI scale 2 (854x480 GUI units -> 1708x960 px): panorama, vanilla overlay, logo, buttons."""
    scale, W, H = 2, 427, 240
    bg = view(20, W * scale, H * scale).convert("RGBA")
    # the vanilla panorama_overlay is a vertical gradient, transparent at the top and dark at the bottom
    grad = np.zeros((H * scale, W * scale, 4), np.uint8)
    grad[..., 3] = (np.linspace(0, 1, H * scale) ** 2 * 120).astype(np.uint8)[:, None]
    bg = Image.alpha_composite(bg, Image.fromarray(grad, "RGBA"))
    big = tex.resize((256 * scale, 64 * scale), Image.NEAREST)
    bg.alpha_composite(big, ((W * scale - big.width) // 2, 30 * scale - 6 * scale))
    d = ImageDraw.Draw(bg)
    cap = logo.up(logo.caption("CAPITULO 1 - ECOS DO FIM"), scale)
    bg.alpha_composite(cap, ((W * scale - cap.width) // 2, (30 + 46) * scale))
    for i in range(4):  # the vanilla buttons, as grey placeholders
        y = (H // 4 + 48 + i * 24) * scale
        d.rectangle([(W // 2 - 100) * scale, y, (W // 2 + 100) * scale, y + 20 * scale], fill=(110, 110, 110, 230),
                    outline=(20, 20, 20, 255), width=scale)
    return bg.convert("RGB")


def main():
    tex = logo_texture()
    os.makedirs(TITLE, exist_ok=True)
    tex.save(os.path.join(TITLE, "terrassic.png"), optimize=True)
    preview(tex).save(PREVIEW, optimize=True)
    sheet = Image.new("RGB", (1280, 720))
    for i, spin in enumerate((0, 90, 180, 270)):  # the panorama turning, as the title screen shows it
        sheet.paste(view(spin, 640, 360), ((i % 2) * 640, (i // 2) * 360))
    sheet.save(VIEWS, optimize=True)
    print("title art written:", TITLE)


if __name__ == "__main__":
    main()
