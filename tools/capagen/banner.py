"""
Terrassic cover art, drawn by code from the mod's own models (painted from tools/modelgen, so always current).

usage:  python3 banner.py [entardecer|retrato|neblina ...] [--wip DIR]
        -> art/capa/terrassic_banner_<direção>_1920x1080.png

Clean compositions: one focal point, few elements, lots of empty space, flat Minecraft-like colours.
--wip DIR renders a proposed species file from DIR (e.g. a T. rex still waiting for approval).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import logo  # noqa: E402
import titulo  # noqa: E402
import render3d as r3  # noqa: E402
from pixel import banded, hexrgb, mix, noise1d, ramp  # noqa: E402

OUT = os.path.join(r3.ROOT, "art", "capa")
HIDE = ("female_display", "saddle")
WIP = None
REX = "tyrannosaurus"  # "tyrannosaurus_v3" while the v3 proposal waits in --wip


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB" if arr.shape[-1] == 3 else "RGBA")


_cache = {}


def dino(name, cam, anim=None, t=0.0, size=(1600, 1100), **light):
    if name not in _cache:
        _cache[name] = r3.load(name, extra_path=WIP)
    rig, tex, m = _cache[name]
    p = r3.pose(m, anim, t) if anim else None
    im = r3.render(rig, tex, cam, size, p, HIDE, **light)
    return im.crop(im.getbbox())


def backlight(cam, side=0.0, up=0.35):
    """Rim-light direction for a light behind the subject (as seen from cam), pushed left (-) or right (+)."""
    pos, tgt = np.array(cam["position"], float), np.array(cam["target"], float)
    fwd = (tgt - pos) / np.linalg.norm(tgt - pos)
    right = np.cross(fwd, [0.0, 1.0, 0.0])
    right /= np.linalg.norm(right)
    v = fwd + right * side + np.array([0, up, 0])
    return tuple(v)


def fit(im, height=None, width=None):
    if height:
        width = round(im.width * height / im.height)
    else:
        height = round(im.height * width / im.width)
    return im.resize((width, height), Image.LANCZOS)


def grade(im, tint=(1, 1, 1), fog=0.0, fog_col=(215, 122, 76), ground_fog=0.0):
    """Tint, uniform haze, and ground mist that thickens towards the feet."""
    a = np.asarray(im, dtype=float)
    rgb = a[..., :3] * np.array(tint)
    f = fog + ground_fog * np.linspace(0, 1, a.shape[0])[:, None, None] ** 2
    rgb = rgb * (1 - f) + np.array(fog_col) * f
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 3]]).astype(np.uint8), "RGBA")


def pixelate(im, k):
    """Snap a render to a k-px grid so it sits with the pixel-art background."""
    small = im.resize((max(1, im.width // k), max(1, im.height // k)), Image.BOX)
    a = np.asarray(small).copy()
    a[..., 3] = np.where(a[..., 3] > 110, 255, 0)
    return Image.fromarray(a, "RGBA").resize((small.width * k, small.height * k), Image.NEAREST)


def sky(PW, PH, stops, levels=None):
    """Smooth vertical gradient (levels=None) or clean bands."""
    t = np.mgrid[0:PH, 0:PW][0] / PH
    return ramp(stops, t if levels is None else banded_flat(t, levels))


def banded_flat(t, levels):
    """Clean colour bands, no dithering."""
    return np.round(np.clip(t, 0, 1) * (levels - 1)) / (levels - 1)


def hills(img, base, amp, scale, col, seed, octaves=3):
    PH, PW = img.shape[:2]
    rng = np.random.default_rng(seed)
    top = base + noise1d(PW, scale, rng, octaves) * amp
    yy = np.mgrid[0:PH, 0:PW][0]
    m = yy >= np.round(top)[None, :]
    img[m] = col
    return top


def disc(img, cx, cy, r, col, soft=None):
    PH, PW = img.shape[:2]
    yy, xx = np.mgrid[0:PH, 0:PW]
    d = np.sqrt((xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2)
    if soft:
        for k, (rr, c, a) in enumerate(soft):
            img[d < rr] = mix(img[d < rr], c, a)
    img[d < r] = col


def wordmark(bg, x, y, cell, sub=None, sub_cell=None, color="#f3ead6", shadow=(20, 14, 18, 150), anchor="left"):
    word = logo.clean_wordmark("TERRASSIC", cell, color, shadow, bold=True)
    if anchor == "center":
        x = (bg.width - word.width) // 2
    bg.alpha_composite(word, (x, y))
    if sub:
        s = logo.clean_wordmark(sub, sub_cell, color, shadow, gap=1, spacing=1)
        sx = x if anchor == "left" else (bg.width - s.width) // 2
        bg.alpha_composite(s, (sx, y + word.height + cell * 2))


def title_block(bg, x, y, finish="pedra", lang="pt_br", texel=2, slogan_finish="osso"):
    """TERRASSIC title + a thin amber rule + the slogan, left-aligned at (x, y). Returns the box it covers."""
    t = titulo.title(finish=finish, texel=texel)
    bg.alpha_composite(t, (x, y))
    s = titulo.slogan(titulo.SLOGANS[lang], cell=texel * 2, finish=slogan_finish)
    pad = 3 * texel * 5                      # the title image keeps 3 blocks of air around the letters
    ry = y + t.height - pad + texel * 10
    rule = Image.new("RGBA", (texel * 40, texel * 2), (232, 150, 60, 255))
    bg.alpha_composite(rule, (x + pad, ry))
    spad = 3 * max(2, round(texel * 2 * 0.75))
    bg.alpha_composite(s, (x + pad - spad, ry + texel * 7 - spad))
    return (x, y, x + max(t.width, s.width), ry + texel * 7 - spad + s.height)


# ------------------------------------------------------------------ direction A: sunset, backlit T. rex
def entardecer(W=1920, H=1080, K=4):
    PW, PH = W // K, H // K
    horizon = int(PH * 0.80)
    img = sky(PW, PH, [(0.0, "#1f2a48"), (0.40, "#5b4467"), (0.66, "#c9714f"), (0.80, "#f0b066"), (1.0, "#f7d48c")])
    sx, sy = PW * 0.66, horizon - 6
    disc(img, sx, sy, 13, hexrgb("#fff3cf"),
         soft=[(70, hexrgb("#f6c06a"), 0.18), (40, hexrgb("#f9d38a"), 0.30), (22, hexrgb("#fde6ae"), 0.5)])
    hills(img, horizon - 8, 5, 70, mix(hexrgb("#8d5260"), hexrgb("#e9a067"), 0.30), 3)
    hills(img, horizon - 2, 3, 40, hexrgb("#5c3747"), 5)
    hills(img, horizon + 4, 2, 30, hexrgb("#211821"), 8, 2)
    bg = to_img(img).resize((W, H), Image.NEAREST).convert("RGBA")

    ptero = dino("pteranodon", {"position": [40, 90, -30], "target": [0, 10, 0], "fov": 35}, "glide", 0.3, (700, 500))
    for (x, y, w) in [(0.36, 0.40, 58), (0.40, 0.36, 40)]:
        p = pixelate(grade(fit(ptero, width=w), (0.22, 0.16, 0.22)), 2)
        bg.alpha_composite(p, (int(W * x), int(H * y)))

    cam = {"position": [-300, 40, -380], "target": [0, 45, 0], "fov": 28}
    rex = dino(REX, cam, "walk", 0.3, (1800, 1200), key=(-0.3, 0.7, -1.0), key_col=(0.42, 0.34, 0.40),
               ambient=(0.30, 0.25, 0.32), rim=backlight(cam, 0.6), rim_col=(1.0, 0.70, 0.36), rim_power=1.3)
    rex = pixelate(fit(rex, height=int(H * 0.50)), 2)
    floor = int((horizon + 5) * K)
    bg.alpha_composite(rex, (int(W * 0.92) - rex.width, floor - rex.height))
    wordmark(bg, int(W * 0.07), int(H * 0.12), 18, "MINECRAFT 1.20.1 · FABRIC + FORGE", 4)
    return bg.convert("RGB")


# ------------------------------------------------------------------ direction B: portrait of a roaring T. rex
def retrato(W=1920, H=1080, K=4, finish="pedra", lang="pt_br"):
    PW, PH = W // K, H // K
    yy, xx = np.mgrid[0:PH, 0:PW]
    d = np.sqrt(((xx - PW * 0.70) / PW) ** 2 + ((yy - PH * 0.42) / PH * 0.8) ** 2)
    img = ramp([(0.0, "#3b3a33"), (0.35, "#262725"), (0.8, "#141516"), (1.0, "#0d0e0f")], np.clip(d / 0.85, 0, 1))
    bg = to_img(img).resize((W, H), Image.NEAREST).convert("RGBA")

    if REX not in _cache:
        _cache[REX] = r3.load(REX, extra_path=WIP)
    rig, tex, m = _cache[REX]
    p = r3.pose(m, "roar", 0.15)
    pts = np.array([w for c, _f, co, _uv in rig.cube_faces(p, HIDE) if c.get("bone") in ("skull", "jaw")
                    for _l, w in co.values()])
    hc = (pts.min(0) + pts.max(0)) / 2
    L = float(max(pts.max(0) - pts.min(0)))
    cam = {"position": [hc[0] - L * 1.6, hc[1] + L * 0.3, hc[2] - L * 1.9],
           "target": [hc[0], hc[1] - L * 0.1, hc[2] + L * 0.3], "fov": 40}
    im = r3.render(rig, tex, cam, (1080, 1080), p, HIDE, key=(-0.8, 0.8, -0.6), key_col=(1.0, 0.9, 0.76),
                   ambient=(0.40, 0.38, 0.42), rim=backlight(cam, 0.7), rim_col=(1.0, 0.66, 0.32), rim_power=0.6)
    im = pixelate(im, 2)
    bg.alpha_composite(im, (W - im.width, H - im.height))
    title_block(bg, int(W * 0.04), int(H * 0.35), finish, lang)
    return bg.convert("RGB")


# ------------------------------------------------------------------ direction C: titans in the morning mist
def neblina(W=1920, H=1080, K=4):
    PW, PH = W // K, H // K
    horizon = int(PH * 0.80)
    img = sky(PW, PH, [(0.0, "#86aacb"), (0.55, "#b9cfd6"), (0.80, "#dfe6db"), (1.0, "#e9ebdc")])
    disc(img, PW * 0.24, PH * 0.42, 9, hexrgb("#fbf6e4"), soft=[(36, hexrgb("#eef0e0"), 0.35), (20, hexrgb("#f6f4e2"), 0.5)])
    hills(img, horizon - 30, 9, 100, hexrgb("#aec3c1"), 2)
    hills(img, horizon - 14, 6, 60, hexrgb("#97b0a5"), 4)
    bg = to_img(img).resize((W, H), Image.NEAREST).convert("RGBA")

    mist = (214, 224, 216)
    cam = {"position": [520, 60, -560], "target": [0, 110, 0], "fov": 26}
    big = dino("alamosaurus", cam, "walk", 0.2, (1800, 1300), key=(0.5, 0.8, -0.4), key_col=(0.85, 0.85, 0.8),
               ambient=(0.55, 0.58, 0.62), rim_power=0.0)
    floor = int(horizon * K)
    b = pixelate(grade(fit(big, height=int(H * 0.24)), fog=0.45, fog_col=mist, ground_fog=0.35), 2)
    bg.alpha_composite(b, (int(W * 0.74), floor - b.height - 18))
    a = pixelate(grade(fit(big, height=int(H * 0.50)), fog=0.18, fog_col=mist, ground_fog=0.55), 2)
    bg.alpha_composite(a, (int(W * 0.36), floor - a.height + 10))

    near = np.zeros((PH, PW, 3))
    near[:] = hexrgb("#6d8a6a")
    top = hills(near, horizon - 1, 2, 30, hexrgb("#5d7a5b"), 9, 2)
    yy = np.mgrid[0:PH, 0:PW][0]
    m = yy >= np.round(top)[None, :]
    near[yy > horizon + 14] = hexrgb("#55704f")
    layer = np.dstack([near, m * 255.0])
    bg.alpha_composite(to_img(layer).resize((W, H), Image.NEAREST))
    wordmark(bg, 0, int(H * 0.11), 18, "MINECRAFT 1.20.1 · FABRIC + FORGE", 4, color="#27352f",
             shadow=(255, 255, 255, 80), anchor="center")
    return bg.convert("RGB")


DIRECTIONS = {"entardecer": entardecer, "retrato": retrato, "neblina": neblina}

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--wip" in args:
        i = args.index("--wip")
        WIP = os.path.abspath(args[i + 1])
        if os.path.exists(os.path.join(WIP, "tyrannosaurus_v3.py")):
            REX = "tyrannosaurus_v3"
        args = args[:i] + args[i + 2:]
    os.makedirs(OUT, exist_ok=True)
    for name in args or DIRECTIONS:
        DIRECTIONS[name]().save(os.path.join(OUT, f"terrassic_banner_{name}_1920x1080.png"))
        print(name, "ok")
