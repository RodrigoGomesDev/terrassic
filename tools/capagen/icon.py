"""
Square Terrassic icon (512x512): the Altar do Salto, a ring of stone, bone and leather around the amber Rift,
with a roaring T. rex breaking out of it. The ring is pixel art; the T. rex is the mod's own model.

usage:  python3 icon.py   -> art/capa/terrassic_icon_512.png (opaque) and terrassic_icon_512_transparente.png
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import banner  # noqa: E402
import scene  # noqa: E402
from pixel import banded, hexrgb, mix, noise2d, ramp  # noqa: E402

STONE = [hexrgb("#c9b48f"), hexrgb("#97805f"), hexrgb("#66513c"), hexrgb("#33261f")]
BONE = hexrgb("#efe6d0")
LEATHER = hexrgb("#7a4a2a")
OUTLINE = hexrgb("#120b10")
# T. rex framing: render height and top-left corner, in icon sizes
FRAMES = {"corpo": (0.86, 0.03, 0.12), "cabeca": (0.85, 0.12, 0.16)}  # "corpo" is the approved icon


def ring_layer(P, cx, cy, r_out, r_in, rift_x, seed=3):
    """RGBA (P x P) pixel-art ring + the sky inside it."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:P, 0:P]
    dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
    d = np.sqrt(dx ** 2 + dy ** 2)
    ang = (np.degrees(np.arctan2(dy, dx)) + 360) % 360
    img = np.zeros((P, P, 3))
    a = np.zeros((P, P), bool)

    # sky inside: dusk gradient, the Rift down the middle
    inside = d < r_in
    t = (yy - (cy - r_in)) / (2 * r_in)
    sky = ramp(scene.SKY, banded(np.clip(t * 1.15, 0, 1), 12))
    xs, ws = scene.rift_path(int(cy + r_in * 0.25), rift_x, rng, P)
    rd = scene.rift_distance(xs, ws * 0.8, P, P)
    g = banded(np.clip(np.exp(-rd / 9) * 0.9 + np.exp(-rd / 3) * 0.4, 0, 1), 7)
    sky = mix(sky, scene.AMBER_DEEP, np.clip(g * 1.2, 0, 0.75))
    sky = mix(sky, scene.AMBER, np.clip((g - 0.45) * 1.6, 0, 1))
    sky[(rd > 0) & (rd <= 1)] = scene.AMBER
    sky[rd <= 0] = scene.AMBER_CORE
    # hills at the bottom of the disc
    hill = cy + r_in * 0.45 + np.sin(xx[0] * 0.21) * 2 + np.sin(xx[0] * 0.07 + 1) * 3
    sky[yy > hill[None, :]] = hexrgb("#3c2340")
    img[inside] = sky[inside]
    a |= inside

    # stone blocks of the ring, 12 per turn, each with its own shade, bevel and grain
    band = (d >= r_in) & (d < r_out)
    seg = (ang // 30).astype(int)
    grain = noise2d(P, P, 2, rng, 2)
    light = np.clip(0.5 - (dx * 0.5 + dy * 0.8) / r_out * 0.7, 0, 1)  # lit from the top-left
    k = np.clip(np.round((1 - light) * 2 + grain * 0.5), 0, 2).astype(int)
    stone = np.array(STONE)[k] * (1 + rng.uniform(-0.08, 0.08, 12)[seg % 12][..., None])
    stone[band & (d < r_in + 1.5)] = STONE[3]                     # inner shadow
    stone[band & (d > r_out - 1.5)] *= 0.8
    seam = (ang % 30) < 1.8
    stone[seam] = STONE[3]
    stone[(ang % 30 >= 1.8) & (ang % 30 < 3.2) & band] *= 1.18    # bevel on the lit edge of each block
    img[band] = stone[band]
    a |= band
    # leather lashings on the diagonals
    for q in (45, 135, 225, 315):
        qa = math.radians(q)
        da = np.degrees(np.arctan2(np.sin(np.radians(ang) - qa), np.cos(np.radians(ang) - qa)))
        lash = band & (np.abs(da) < 5)
        stripe = (np.round(d) % 2 == 0)
        img[lash] = np.where(stripe[lash][:, None], LEATHER, LEATHER * 0.7)
    # amber stones set into the ring at the top and bottom
    for q in (270, 90, 0, 180):
        qa = math.radians(q)
        gx, gy = cx + math.cos(qa) * (r_in + r_out) / 2, cy + math.sin(qa) * (r_in + r_out) / 2
        gem = (np.abs(xx + 0.5 - gx) + np.abs(yy + 0.5 - gy)) < 4.5
        img[gem] = scene.AMBER
        img[gem & ((xx + 0.5 - gx) + (yy + 0.5 - gy) < -1)] = scene.AMBER_CORE
        img[gem & ((xx + 0.5 - gx) + (yy + 0.5 - gy) > 2)] = scene.AMBER_DEEP
        a |= gem
    return img, a


def outline(img, a, col=OUTLINE):
    out = np.zeros_like(a)
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            out |= np.roll(np.roll(a, oy, 0), ox, 1)
    ring = out & ~a
    img[ring] = col
    return a | ring


def build(S=512, K=4, opaque=True, frame="corpo"):
    rex_h, rex_x, rex_y = FRAMES[frame]
    P = S // K
    cx, cy, r_out, r_in = P / 2, P / 2 + 4, P * 0.42, P * 0.33
    img, a = ring_layer(P, cx, cy, r_out, r_in, cx + r_in * 0.45)
    a = outline(img, a)
    base = Image.fromarray(np.dstack([np.clip(img, 0, 255), a * 255.0]).astype(np.uint8), "RGBA")
    base = base.resize((S, S), Image.NEAREST)

    # T. rex: body stays inside the disc, the head breaks out over the ring
    if frame == "cabeca":
        # close-up: camera aimed at the head, the body falls out of the frame
        cam = {"position": [-40, 46, -100], "target": [2, 38, -30], "fov": 30}
        anim_t = 0.15
    else:
        cam = {"position": [-70, 50, -170], "target": [0, 40, -20], "fov": 30}
        anim_t = 0.3
    rex = banner.dino("tyrannosaurus", cam, "attack", anim_t, (1600, 1300), rim=(1.4, 0.6, 0.3), key=(0.2, 0.8, -1.4),
                      ambient=(0.44, 0.40, 0.48), rim_power=0.6, key_col=(0.9, 0.8, 0.68))
    rex = banner.grade(banner.fit(rex, height=int(S * rex_h)), (1.0, 0.9, 0.84))
    rex = banner.pixelate(rex, 2 if frame == "corpo" else 4)
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.alpha_composite(rex, (int(S * rex_x), int(S * rex_y)))
    la = np.asarray(layer).copy()
    yy, xx = np.mgrid[0:S, 0:S]
    d = np.sqrt((xx - cx * K) ** 2 + (yy - cy * K) ** 2)
    # body inside the disc; only the head breaks out, over the top-left of the ring
    edge = 0.1 if frame == "cabeca" else -0.2
    keep = (d < r_in * K) | ((yy < cy * K - r_in * K * 0.05) & (xx < cx * K + r_in * K * edge))
    la[..., 3] = np.where(keep, la[..., 3], 0)
    # dark outline around the T. rex so it reads at small sizes
    m = la[..., 3] > 0
    ol = np.zeros_like(m)
    for oy in (-2, 0, 2):
        for ox in (-2, 0, 2):
            ol |= np.roll(np.roll(m, oy, 0), ox, 1)
    out = np.asarray(base).copy()
    out[ol & ~m] = (18, 11, 16, 255)
    out[m] = la[m]
    icon = Image.fromarray(out, "RGBA")
    if opaque:
        bg = np.zeros((S, S, 4))
        t = yy / S
        bg[..., :3] = ramp([(0, "#1a1226"), (1, "#2e1a2e")], banded(t, 6))
        glow = np.exp(-np.maximum(d - r_out * K, 0) / (S * 0.10)) * (d >= r_out * K)
        bg[..., :3] = mix(bg[..., :3], scene.AMBER_DEEP, banded(glow * 0.5, 5))
        bg[..., 3] = 255
        full = Image.fromarray(bg.astype(np.uint8), "RGBA")
        full.alpha_composite(icon)
        return full.convert("RGB")
    return icon


if __name__ == "__main__":
    os.makedirs(banner.OUT, exist_ok=True)
    build().save(os.path.join(banner.OUT, "terrassic_icon_512.png"))
    build(opaque=False).save(os.path.join(banner.OUT, "terrassic_icon_512_transparente.png"))
    print("ok")
