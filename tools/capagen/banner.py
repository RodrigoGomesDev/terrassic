"""
Terrassic cover art, all drawn by code from the mod's own models.

usage:  python3 banner.py            -> art/capa/terrassic_banner_1920x1080.png (+ smaller versions)

The background is pixel art painted at 1/4 resolution; the dinosaurs are the mod's own GeckoLib models
(tools/modelgen) rendered with the mod's own textures and posed with their own animations.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import logo  # noqa: E402
import render3d as r3  # noqa: E402
import scene  # noqa: E402
from pixel import hexrgb, mix  # noqa: E402

OUT = os.path.join(r3.ROOT, "art", "capa")
HIDE = ("female_display", "saddle")


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB" if arr.shape[-1] == 3 else "RGBA")


def dino(name, cam, anim=None, t=0.0, size=(1400, 1000), **light):
    rig, tex, m = r3.load(name)
    p = r3.pose(m, anim, t) if anim else None
    im = r3.render(rig, tex, cam, size, p, HIDE, **light)
    return im.crop(im.getbbox())


def fit(im, height=None, width=None):
    if height:
        width = round(im.width * height / im.height)
    else:
        height = round(im.height * width / im.width)
    return im.resize((width, height), Image.LANCZOS)


def grade(im, tint, fog=0.0, fog_col=(215, 122, 76), dark=1.0):
    """Colour-grade a rendered dinosaur into the dusk: multiply tint, then mix towards the haze."""
    a = np.asarray(im, dtype=float)
    rgb = a[..., :3] * np.array(tint) * dark
    rgb = rgb * (1 - fog) + np.array(fog_col) * fog
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 3]]).astype(np.uint8), "RGBA")


def pixelate(im, k):
    """Snap a render to a k-px grid so it sits with the pixel-art background."""
    small = im.resize((max(1, im.width // k), max(1, im.height // k)), Image.BOX)
    a = np.asarray(small).copy()
    a[..., 3] = np.where(a[..., 3] > 110, 255, 0)
    return Image.fromarray(a, "RGBA").resize((small.width * k, small.height * k), Image.NEAREST)


def shadow(size, rx, ry, alpha=150):
    sh = Image.new("RGBA", size, (0, 0, 0, 0))
    a = np.zeros((size[1], size[0]))
    yy, xx = np.mgrid[0:size[1], 0:size[0]]
    a[((xx - size[0] / 2) / rx) ** 2 + ((yy - size[1] / 2) / ry) ** 2 < 1] = alpha
    sh.putalpha(Image.fromarray(a.astype(np.uint8)))
    return sh.filter(ImageFilter.GaussianBlur(6))


def build(W=1920, H=1080, K=4, seed=7):
    PW, PH = W // K, H // K
    horizon = int(PH * 0.66)
    rift_x = PW * 0.5
    rift_end = int(PH * 0.50)

    # ---- painted background (pixel resolution)
    sky, rxs, rdist = scene.sky_layer(PW, PH, horizon, rift_x, rift_end, seed)
    r2 = scene.land_layer(sky, PW, PH, horizon, rift_x, seed + 4)
    rng = np.random.default_rng(seed + 9)
    mid = np.array(sky)
    far_tree = hexrgb("#2b1a33")
    rim = hexrgb("#c06a45")
    for x in list(range(4, int(PW * 0.20), 11)) + list(range(int(PW * 0.84), PW, 10)):
        hgt = int(rng.integers(26, 46))
        scene.tree(mid, x + int(rng.integers(-3, 3)), int(r2[min(x, PW - 1)]) + 14, hgt, far_tree, rim, rng,
                   "araucaria" if rng.random() < 0.7 else "cycad")
    bg = to_img(mid).resize((W, H), Image.NEAREST).convert("RGBA")

    # ---- distant life: pteranodons in the sky, a brachiosaurus and a parasaurolophus herd by the lake
    ptero_cam = {"position": [60, 70, -40], "target": [0, 10, 0], "fov": 35}
    ptero = dino("pteranodon", ptero_cam, "glide", 0.3, (700, 500))
    for (x, y, wd, flip) in [(0.10, 0.36, 150, False), (0.17, 0.27, 96, False), (0.88, 0.40, 120, True),
                             (0.84, 0.31, 70, True)]:
        p = fit(ptero, width=wd)
        p = grade(p, (0.50, 0.38, 0.50), fog=0.30, fog_col=(80, 45, 75))
        if flip:
            p = p.transpose(Image.FLIP_LEFT_RIGHT)
        p = pixelate(p, 2)
        bg.alpha_composite(p, (int(W * x - p.width / 2), int(H * y - p.height / 2)))

    shore = int(H * horizon / PH) + 10
    brachio_cam = {"position": [200, 30, -120], "target": [0, 60, 0], "fov": 30}
    brachio = dino("brachiosaurus", brachio_cam, "graze", 0.0, (1000, 900), rim=(-1.0, 0.4, 0.3))
    b = grade(fit(brachio, height=int(H * 0.25)), (0.60, 0.45, 0.58), fog=0.55, fog_col=(150, 78, 82))
    b = pixelate(b, 2)
    bg.alpha_composite(b, (int(W * 0.37) - b.width // 2, shore - b.height))

    para_cam = {"position": [-170, 30, -150], "target": [0, 30, 0], "fov": 30}
    para = dino("parasaurolophus", para_cam, "graze", 0.4, (900, 700))
    para_idle = dino("parasaurolophus", para_cam, "idle", 0.0, (900, 700))
    for (x, hgt, im) in [(0.555, 64, para_idle), (0.615, 52, para), (0.475, 46, para)]:
        p = grade(fit(im, height=hgt), (0.62, 0.48, 0.60), fog=0.45, fog_col=(150, 78, 82))
        p = pixelate(p, 2)
        bg.alpha_composite(p, (int(W * x - p.width / 2), shore + 6 - p.height))

    # ---- foreground ground
    ground, gedge = scene.ground_layer(PW, PH, int(PH * 0.84), rift_x, seed + 2)
    bg.alpha_composite(to_img(ground).resize((W, H), Image.NEAREST))

    # ---- the stars: a roaring T. rex facing a Triceratops
    light = dict(ambient=(0.40, 0.36, 0.46), rim_power=0.55, key_col=(0.85, 0.74, 0.62))
    rex_cam = {"position": [-150, 6, -175], "target": [0, 30, 0], "fov": 30}
    rex = dino("tyrannosaurus", rex_cam, "roar", 0.75, (1600, 1000), rim=(1.4, 0.6, 0.1), key=(0.07, 0.8, -1.4),
               **light)
    rex = grade(fit(rex, height=int(H * 0.64)), (1.0, 0.88, 0.82))
    trike_cam = {"position": [160, 8, -160], "target": [0, 22, 0], "fov": 30}
    trike = dino("triceratops", trike_cam, "attack", 0.75, (1400, 900), rim=(-1.4, 0.6, 0.0), key=(0.0, 0.8, -1.4),
                 **light)
    trike = grade(fit(trike, height=int(H * 0.36)), (1.0, 0.88, 0.82))
    floor = int(H * 0.955)
    for im, x in ((trike, int(W * 0.03)), (rex, int(W * 0.985) - rex.width)):
        sh = shadow((int(im.width * 0.9), 60), im.width * 0.42, 20)
        bg.alpha_composite(sh, (x + int(im.width * 0.05), floor - 32))
        bg.alpha_composite(pixelate(im, 2), (x, floor - im.height))

    # ---- foreground plants (pixel)
    front = np.zeros((PH, PW, 4))
    frng = np.random.default_rng(seed + 31)
    for (cx, d, s) in [(8, 1, 60), (30, 1, 44), (PW - 6, -1, 62), (PW - 40, -1, 40), (PW * 0.36, 1, 28),
                       (PW * 0.62, -1, 30)]:
        scene.fern(front, cx, PH + 2, s, d, hexrgb("#1d1a1f"), hexrgb("#7a4632"), frng)
    bg.alpha_composite(to_img(front).resize((W, H), Image.NEAREST))

    # ---- wordmark over the Rift
    word = logo.up(logo.wordmark(), 2)
    wx, wy = (W - word.width) // 2, int(H * 0.10)
    halo = Image.new("RGBA", (word.width + 120, word.height + 120), (0, 0, 0, 0))
    halo.alpha_composite(word, (60, 60))
    bg.alpha_composite(logo.glow(halo, 22, strength=0.9), (wx - 60, wy - 60))
    bg.alpha_composite(word, (wx, wy))
    cap = logo.up(logo.caption("MINECRAFT 1.20.1 · FABRIC + FORGE"), 3)
    cx, cy = (W - cap.width) // 2, wy + word.height + 18
    plate = Image.new("RGBA", (cap.width + 48, cap.height + 24), (20, 10, 24, 170))
    bg.alpha_composite(plate, (cx - 24, cy - 12))
    bg.alpha_composite(cap, (cx, cy))

    # ---- vignette
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.75)) ** 2
    vig = np.clip((v - 0.55) * 0.9, 0, 0.55)
    va = Image.fromarray((vig * 255).astype(np.uint8))
    shade = Image.new("RGBA", (W, H), (12, 6, 16, 0))
    shade.putalpha(va)
    bg.alpha_composite(shade)
    return bg.convert("RGB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    img = build()
    img.save(os.path.join(OUT, "terrassic_banner_1920x1080.png"))
    print("ok")
