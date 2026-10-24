"""
Title-screen panorama of the Late Cretaceous (v0.8, "Mundo Terrassic", phase M2).

usage:  python3 panorama.py   -> common/src/main/resources/assets/terrassic/textures/gui/title/background/panorama_0..5.png
                                 + art/capa/panorama_preview.png (the 6 faces unfolded, for review)

The same dusk as the cover (banner.py): the Rift torn open in the sky, a smoking volcano, araucaria forests, a lake
that mirrors the amber glow, and the mod's own models standing around the viewer: a Parasaurolophus herd at the
water, a T. rex roaring on a rise, Triceratops, a titanosaur far away and pterosaurs gliding.

How it is drawn: every pixel of the six cube faces is a direction. The sky, the clouds and the Rift are functions of
that direction; the distant land is a 360-degree painted strip; the near ground is the plane under the viewer. The
dinosaurs are rasterised straight onto the cube faces with the same software renderer as the cover, so they line
up across the seams. Faces follow the layout of the vanilla CubeMap (net.minecraft.client.renderer.CubeMap).
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import render3d as r3  # noqa: E402
from pixel import BAYER4, hexrgb, mix  # noqa: E402

N = 512          # face size the scene is painted at (pixel art grid)
OUT_SIZE = 1024  # face size written for the game (nearest-neighbour x2)
OUT = os.path.join(r3.ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "gui", "title",
                   "background")
PREVIEW = os.path.join(r3.ROOT, "art", "capa", "panorama_preview.png")
EYE = 12.0       # blocks above the valley floor (the viewer stands on a rise)
RIFT_LON = 0.0   # the Rift and the lake are straight ahead of the first face

SKY = [(0.0, "#f7cf7a"), (0.06, "#ec9a4a"), (0.16, "#c35a3c"), (0.32, "#6a3254"), (0.55, "#2c1d45"),
       (1.0, "#120d22")]
AMBER_CORE = hexrgb("#fff4cf")
AMBER = hexrgb("#ffb63c")
AMBER_DEEP = hexrgb("#e0661c")
HAZE = hexrgb("#d77a4c")

# cube faces: normal, u axis, v axis, in CubeMap space (y points down, the first face looks along +z)
FACES = [((0, 0, 1), (1, 0, 0), (0, 1, 0)),
         ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
         ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
         ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
         ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
         ((0, 1, 0), (1, 0, 0), (0, 0, -1))]
FACES = [tuple(np.array(v, dtype=float) for v in f) for f in FACES]


def to_cube(w):
    """World (x, y up, z) -> CubeMap space. A rotation of 180 degrees around z, so handedness is kept."""
    return np.stack([-w[..., 0], -w[..., 1], w[..., 2]], axis=-1)


def face_dirs(k):
    """World-space unit direction of every pixel centre of face k, shape (N, N, 3)."""
    n, a, b = FACES[k]
    s = (np.arange(N) + 0.5) / N * 2 - 1
    vv, uu = np.meshgrid(s, s, indexing="ij")
    c = n[None, None, :] + uu[..., None] * a[None, None, :] + vv[..., None] * b[None, None, :]
    w = to_cube(c)  # the mapping is its own inverse
    return w / np.linalg.norm(w, axis=-1, keepdims=True)


def lonlat(d):
    lon = np.degrees(np.arctan2(d[..., 0], d[..., 2]))  # 0 = straight ahead (+z), grows towards +x
    lat = np.degrees(np.arcsin(np.clip(d[..., 1], -1, 1)))
    return lon, lat


# ---- periodic noise (so the 360 degrees close without a seam) -------------------------------------------------

def pnoise1(lon, cells, seed, octaves=4):
    rng = np.random.default_rng(seed)
    out, amp, tot = np.zeros_like(lon, dtype=float), 1.0, 0.0
    for o in range(octaves):
        c = cells * 2 ** o
        v = rng.uniform(-1, 1, c)
        x = (lon % 360.0) / 360.0 * c
        i = np.floor(x).astype(int) % c
        f = x - np.floor(x)
        f = f * f * (3 - 2 * f)
        out += amp * (v[i] * (1 - f) + v[(i + 1) % c] * f)
        tot += amp
        amp *= 0.5
    return out / tot


def pnoise2(lon, lat, cells, rows, seed, octaves=3):
    rng = np.random.default_rng(seed)
    out, amp, tot = np.zeros_like(lon, dtype=float), 1.0, 0.0
    for o in range(octaves):
        c, r = cells * 2 ** o, rows * 2 ** o
        g = rng.uniform(-1, 1, (r + 2, c))
        x = (lon % 360.0) / 360.0 * c
        y = (np.clip(lat, -90, 90) + 90) / 180.0 * r
        xi, yi = np.floor(x).astype(int) % c, np.floor(y).astype(int)
        fx, fy = x - np.floor(x), y - np.floor(y)
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a = g[yi, xi] * (1 - fx) + g[yi, (xi + 1) % c] * fx
        b = g[yi + 1, xi] * (1 - fx) + g[yi + 1, (xi + 1) % c] * fx
        out += amp * (a * (1 - fy) + b * fy)
        tot += amp
        amp *= 0.5
    return out / tot


def dither(t, levels, shape):
    """Bands with ordered dithering, on the face's pixel grid."""
    h, w = shape
    bay = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
    x = np.clip(t, 0, 1) * (levels - 1)
    k = np.floor(x)
    return (k + (x - k > bay)) / (levels - 1)


def ramp(stops, t):
    t = np.clip(t, 0, 1)
    pos = np.array([p for p, _ in stops])
    cols = np.array([hexrgb(c) for _, c in stops])
    return np.stack([np.interp(t, pos, cols[:, ch]) for ch in range(3)], axis=-1)


def angdiff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


# ---- sky -----------------------------------------------------------------------------------------------------

RIFT_TOP, RIFT_BOTTOM = 64.0, 3.0


def rift_lon(lat):
    """Longitude of the Rift's crack at each latitude: a jagged line falling from high in the sky."""
    return RIFT_LON + pnoise1(lat * 9.0, 20, 31, 3) * 3.2 + pnoise1(lat * 40.0, 30, 32, 2) * 0.9


def rift_width(lat):
    t = np.clip((RIFT_TOP - lat) / (RIFT_TOP - RIFT_BOTTOM), 0, 1)
    return 0.15 + 2.1 * np.sin(np.pi * np.clip(t * 1.02, 0, 1)) ** 0.7


def sky(lon, lat, shape):
    """Sky colour for directions (lon, lat), lat >= -something (also used mirrored for reflections)."""
    t = np.clip(lat / 90.0, 0, 1) ** 0.75
    # the horizon is brighter towards the Rift
    toward = np.cos(np.radians(angdiff(lon, RIFT_LON))) * 0.5 + 0.5
    t = t + (1 - toward) * 0.10 * (1 - t)
    img = ramp(SKY, dither(t, 20, shape))

    # stars, away from the glow
    rng = np.random.default_rng(3)
    key = (np.floor((lon + 180) * 3.1).astype(int) * 7919 + np.floor((lat + 90) * 3.1).astype(int) * 104729) % 100003
    star = (rng.random(100003)[key] > 0.993) & (lat > 32)
    img[star] = mix(img[star], hexrgb("#e9ddff"), 0.9)

    # the Rift: glow, crack and branches
    rl, rw = rift_lon(lat), rift_width(lat)
    inside = (lat < RIFT_TOP) & (lat > RIFT_BOTTOM)
    dx = np.abs(angdiff(lon, rl)) * np.cos(np.radians(np.clip(lat, -80, 80)))
    d = np.where(inside, np.maximum(dx - rw, 0), 1e3)
    d_top = np.hypot(dx, np.maximum(lat - RIFT_TOP, 0) + np.maximum(RIFT_BOTTOM - lat, 0))
    d = np.minimum(d, d_top + 2.0)
    glow = np.exp(-d / 13.0) * 0.85 + np.exp(-d / 3.5) * 0.5
    g = dither(np.clip(glow, 0, 1), 9, shape)
    img[:] = mix(img, AMBER_DEEP, np.clip(g * 1.2, 0, 0.75))
    img[:] = mix(img, AMBER, np.clip((g - 0.45) * 1.6, 0, 1))
    img[inside & (dx <= rw + 0.35) & (dx > rw)] = AMBER
    img[inside & (dx <= rw)] = AMBER_CORE

    # clouds: long bands lit from the Rift side
    cn = pnoise2(lon * 0.6, lat * 2.2, 18, 40, 41, 4)
    band = np.exp(-((lat - 16.0) / 9.0) ** 2) + 0.6 * np.exp(-((lat - 34.0) / 6.0) ** 2)
    cloud = (cn * 0.9 + band * 0.75) > 0.78
    cloud &= (lat > 4) & (lat < 46)
    lit = np.clip(1.0 - np.abs(angdiff(lon, RIFT_LON)) / 110.0, 0, 1)
    ccol = mix(hexrgb("#33213f"), hexrgb("#8c4058"), dither(lit * 0.8 + (1 - lat / 46) * 0.35, 5, shape))
    img[cloud] = ccol[cloud]
    under = cloud & ~(pnoise2(lon * 0.6, (lat - 0.6) * 2.2, 18, 40, 41, 4) * 0.9
                      + (np.exp(-((lat - 0.6 - 16.0) / 9.0) ** 2) + 0.6 * np.exp(-((lat - 0.6 - 34.0) / 6.0) ** 2)) * 0.75 > 0.78)
    img[under] = mix(img[under], AMBER, 0.35 + 0.5 * lit[under])

    # shooting stars: the meteors that come more and more often at the end of the Cretaceous
    for (lon0, lat0, ln, ang) in ((-120, 52, 9, -28), (150, 60, 7, -35), (95, 44, 5, -22), (-40, 66, 6, -40)):
        a = math.radians(ang)
        along = angdiff(lon, lon0) * math.cos(a) + (lat - lat0) * math.sin(a)
        across = -angdiff(lon, lon0) * math.sin(a) + (lat - lat0) * math.cos(a)
        m = (np.abs(across) < 0.22) & (along > 0) & (along < ln)
        img[m] = mix(img[m], AMBER_CORE, (1 - along[m] / ln) * 0.95)
    return img


# ---- distant land: a 360-degree painted strip ------------------------------------------------------------------

STRIP_W, STRIP_LAT0, STRIP_LAT1 = 2048, -8.0, 20.0
STRIP_H = int(round((STRIP_LAT1 - STRIP_LAT0) / 360.0 * STRIP_W))
VOLCANO_LON = -55.0


def strip_lat(y):
    return STRIP_LAT1 - (y + 0.5) / STRIP_H * (STRIP_LAT1 - STRIP_LAT0)


def tree(img, alpha, cx, base, height, col, rim, rng, kind):
    """Silhouette tree into the strip (cx, base in strip pixels; x wraps around)."""
    h, w = alpha.shape

    def put(x, y, c):
        x, y = int(x) % w, int(y)
        if 0 <= y < h:
            img[y, x] = c
            alpha[y, x] = True
    trunk = max(1, height // 16)
    for y in range(base - height, base + 2):
        for dx in range(-(trunk // 2), trunk - trunk // 2):
            put(cx + dx, y, col)
    if kind == "araucaria":
        tiers = max(3, height // 6)
        for i in range(tiers):
            ty = base - height + 1 + i * (height * 0.5 / tiers)
            span = int(2 + height * 0.11 + i * 0.7 + rng.integers(0, 3))
            for dx in range(-span, span + 1):
                droop = int(abs(dx) ** 1.3 * 0.13)
                for k in range(2):
                    put(cx + dx, ty + droop + k, col)
                put(cx + dx, ty + droop - 1, rim if dx < 0 else col)
    elif kind == "palm":
        for f in range(7):
            a = math.pi * (0.05 + 0.9 * f / 6)
            L = height * 0.42
            for s in range(int(L)):
                t = s / L
                x = cx + math.cos(a) * s
                y = base - height + 1 - math.sin(a) * s * 0.55 + t * t * L * 0.55
                put(x, y, col)
                if s % 2 == 0:
                    put(x, y + 1, col)
                    put(x, y - 1, rim if math.cos(a) < 0 else col)
    else:  # broadleaf (magnolia, plane tree): a lumpy round crown
        r = max(3, int(height * 0.32))
        cy = base - height + r
        for dy in range(-r, r + 1):
            for dx in range(-r - 2, r + 3):
                if (dx / (r + 2)) ** 2 + (dy / r) ** 2 <= 1.0 + rng.uniform(-0.15, 0.1):
                    put(cx + dx, cy + dy, rim if dy < -r * 0.5 and dx < 0 else col)


def paint_strip():
    """RGBA strip (STRIP_H, STRIP_W): far range, volcano and smoke, hills, forests."""
    w, h = STRIP_W, STRIP_H
    img = np.zeros((h, w, 3))
    alpha = np.zeros((h, w), bool)
    x = np.arange(w)
    lon = (x + 0.5) / w * 360.0 - 180.0
    yy = np.arange(h)[:, None]
    lat = strip_lat(yy) * np.ones((1, w))
    px_per_deg = w / 360.0
    toward = np.cos(np.radians(angdiff(lon, RIFT_LON))) * 0.5 + 0.5
    shape = (h, w)

    def layer(top_lat, col_far, col_near, haze_amt):
        top = (STRIP_LAT1 - top_lat) / (STRIP_LAT1 - STRIP_LAT0) * h
        m = yy > top[None, :]
        depth = np.clip((yy - top[None, :]) / 30.0, 0, 1)
        col = mix(col_far, col_near, dither(depth, 4, shape))
        col = mix(col, HAZE, (haze_amt * (0.6 + 0.4 * toward))[None, :] * np.ones((h, 1)))
        img[m] = col[m]
        alpha[m] = True
        return top

    # far mountain range (the Highlands), highest behind the viewer
    far = 3.5 + 4.5 * (pnoise1(lon, 9, 5, 4) * 0.5 + 0.5) + 2.5 * (1 - toward)
    layer(far, mix(hexrgb("#7a3f5c"), HAZE, 0.35), hexrgb("#4d2a4f"), 0.18)

    # the volcano, with lava rills and smoke drifting away from the Rift
    rng = np.random.default_rng(17)
    dv = np.abs(angdiff(lon, VOLCANO_LON))
    vprof = np.where(dv < 1.2, 12.6, 13.4 - dv ** 1.15 * 0.55) + pnoise1(lon, 90, 6, 2) * 0.3
    vtop = (STRIP_LAT1 - vprof) / (STRIP_LAT1 - STRIP_LAT0) * h
    mv = (yy > vtop[None, :]) & (dv < 30)[None, :]
    vc = mix(hexrgb("#3d2340"), hexrgb("#6b3550"), dither(np.clip((angdiff(lon, VOLCANO_LON) + 8) / 30, 0, 1)[None, :]
                                                          * np.ones((h, 1)), 4, shape))
    img[mv] = vc[mv]
    alpha[mv] = True
    vx = (VOLCANO_LON + 180) / 360 * w
    vt = (STRIP_LAT1 - 13.0) / (STRIP_LAT1 - STRIP_LAT0) * h
    for k in range(3):
        lx = vx + rng.uniform(-3, 3)
        for y in range(int(vt), int(vt + 22 + k * 5)):
            lx += rng.choice([-1, 0, 0, 1])
            img[y, int(lx) % w] = mix(AMBER_DEEP, AMBER, 1 - (y - vt) / 30)
    img[int(vt):int(vt) + 2, int(vx - 4):int(vx + 5)] = AMBER

    # mid hills
    mid = 0.6 + 2.2 * (pnoise1(lon, 24, 7, 3) * 0.5 + 0.5)
    layer(mid, hexrgb("#4a2a46"), hexrgb("#3c2340"), 0.12)

    # forests on the hills: araucarias, palms and broadleaf trees, sparser towards the lake
    rng = np.random.default_rng(23)
    for i in range(520):
        l = rng.uniform(-180, 180)
        if abs(angdiff(l, RIFT_LON)) < 22 and rng.random() < 0.8:  # keep the lake view open
            continue
        if abs(angdiff(l, VOLCANO_LON)) < 6:
            continue
        cx = (l + 180) / 360 * w
        ground = (STRIP_LAT1 - (0.6 + 2.2 * (pnoise1(np.array([l]), 24, 7, 3)[0] * 0.5 + 0.5))) / (STRIP_LAT1 - STRIP_LAT0) * h
        base = int(ground + rng.uniform(2, 14))
        near = (base - ground) / 14.0
        height = int(10 + near * 26 + rng.uniform(-3, 5))
        kind = rng.choice(["araucaria", "araucaria", "palm", "broad"], p=[0.45, 0.15, 0.15, 0.25])
        col = mix(hexrgb("#2b1a30"), hexrgb("#1a1020"), near)
        rim = mix(col, AMBER_DEEP, 0.55 * max(0.0, math.cos(math.radians(angdiff(l, RIFT_LON)))) + 0.1)
        tree(img, alpha, cx, base, height, col, rim, rng, kind)
    return img, alpha


def smoke(lon, lat, shape):
    """Volcano smoke column (mask, colour), drawn in direction space so it can rise above the strip."""
    m = np.zeros(lon.shape, bool)
    col = np.zeros(lon.shape + (3,))
    rng = np.random.default_rng(29)
    for k in range(16):
        t = k / 15
        cl = VOLCANO_LON - t ** 1.6 * 24 + rng.uniform(-0.6, 0.6)  # drifts away from the Rift
        ca = 13.6 + t * 26
        rad = 0.8 + t * 4.2
        d = np.hypot(angdiff(lon, cl) * np.cos(np.radians(lat)), (lat - ca) * 1.25)
        d = d + pnoise2(lon * 4, lat * 4, 40, 60, 30 + k, 2) * rad * 0.35
        puff = d < rad
        shade = np.clip((ca - lat) / rad * 0.5 + 0.5, 0, 1)
        c = mix(hexrgb("#5a3448"), hexrgb("#2e1d34"), np.round(np.clip(t * 0.8 + (1 - shade) * 0.4, 0, 1) * 3) / 3)
        col[puff] = c[puff]
        m |= puff
    return m, col


# ---- ground: the plane under the viewer ------------------------------------------------------------------------

LAKE = (2.0, 47.0, 31.0, 17.0)  # centre x, z and half axes, in blocks


def vnoise(x, y, seed):
    """Smooth value noise on an infinite grid, in [-1, 1]."""
    xi, yi = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x - xi, y - yi
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)

    def h(i, j):
        v = (i * 374761393 + j * 668265263 + seed * 1442695041) & 0xFFFFFFFF
        v = ((v ^ (v >> 13)) * 1274126177) & 0xFFFFFFFF
        return (v ^ (v >> 16)) / 2147483648.0 - 1.0
    a = h(xi, yi) * (1 - fx) + h(xi + 1, yi) * fx
    b = h(xi, yi + 1) * (1 - fx) + h(xi + 1, yi + 1) * fx
    return a * (1 - fy) + b * fy


def fbm(x, y, seed, octaves=3):
    out, amp, tot = 0.0, 1.0, 0.0
    for o in range(octaves):
        out = out + amp * vnoise(x * 2 ** o, y * 2 ** o, seed + o)
        tot += amp
        amp *= 0.5
    return out / tot


def hill_edge(lon):
    """Distance (blocks) where the rise the viewer stands on drops to the valley, per direction."""
    return 15.0 + 5.0 * pnoise1(lon, 10, 71, 3)


def tiled(tex, gx, gz):
    """Texel of a 16x16 block texture laid on the ground plane, one block per metre."""
    u = ((gx - np.floor(gx)) * 16).astype(int).clip(0, 15)
    v = ((gz - np.floor(gz)) * 16).astype(int).clip(0, 15)
    return tex[v, u, :3]


HILL_BASE = mix(hexrgb("#3c2340"), HAZE, 0.25)


def ground(d, lon, lat, shape):
    """Ground seen along directions d (lat < 0): the dark rise under the viewer, then the valley floor (the mod's
    fern litter, greener where grass grows) with the lake that mirrors the sky and the Rift."""
    tdown = np.maximum(-d[..., 1], 1e-4)
    dist = EYE / tdown
    gx, gz = d[..., 0] * dist, d[..., 2] * dist
    toward = np.clip(np.cos(np.radians(angdiff(lon, RIFT_LON))), 0, 1)

    litter = block_tex("fern_litter")
    tex = tiled(litter, gx, gz)
    mean = litter[..., :3].reshape(-1, 3).mean(axis=0)
    tex = mix(tex, mean, np.clip((dist - 22) / 45.0, 0, 1))  # far texels blur into their average
    grassy = fbm(gx / 11.0, gz / 11.0, 61, 3) > -0.15
    col = np.where(grassy[..., None], tex * np.array([0.78, 1.0, 0.62]), tex)
    blockvar = (vnoise(np.floor(gx) + 0.5, np.floor(gz) + 0.5, 63) * 0.06 + 1.0)[..., None]
    col = col * blockvar
    # dusk light: purple ambient, amber towards the Rift and on the far ground
    lit = toward * (0.35 + 0.65 * np.clip(dist / 70.0, 0, 1))
    light = mix(np.array([0.48, 0.38, 0.50]), np.array([1.05, 0.66, 0.42]), lit * 0.8)
    img = col * light
    img = mix(img, mix(HILL_BASE, HAZE, toward ** 2 * 0.8), np.clip((dist - 60) / 260.0, 0, 0.85))

    # the lake: the sky mirrored, darker, with a broken amber path under the Rift
    cx, cz, ax, az = LAKE
    wob = pnoise1(np.degrees(np.arctan2(gx - cx, gz - cz)), 14, 51, 3) * 0.14
    r = ((gx - cx) / ax) ** 2 + ((gz - cz) / az) ** 2
    lake = r < 1.0 + wob
    refl = mix(sky(lon, -lat, shape), hexrgb("#2a1f3d"), 0.32)
    img[lake] = refl[lake]
    rows = np.floor(dist * 1.6).astype(int)
    jitter = np.random.default_rng(5).random(4096)[rows % 4096] - 0.5
    wpath = 0.5 + 2.2 * np.clip(1 - (dist - 25) / 50.0, 0, 1)
    path = lake & (np.abs(angdiff(lon, RIFT_LON + jitter * 1.6)) < wpath) & (rows % 2 == 0)
    img[path] = mix(img[path], mix(AMBER, AMBER_CORE, 0.6), 0.85)
    ripple = lake & (vnoise(gx / 0.8, gz / 3.0, 66) > 0.55)
    img[ripple] = mix(img[ripple], AMBER, 0.25 * (0.3 + toward[ripple]))
    shore = (~lake) & (r < (1.0 + wob) * 1.12)
    img[shore] = mix(img[shore], hexrgb("#8a6a52") * 0.75, 0.6)

    return img


# ---- dinosaurs, rasterised onto the cube faces ------------------------------------------------------------------

def species_scale(name):
    """In-game model scale of a species (the MODEL_SCALE constant gen_species.py writes into its class)."""
    import re
    path = os.path.join(r3.ROOT, "common", "src", "main", "java", "com", "terrassic", "entity",
                        name.capitalize() + ".java")
    with open(path, encoding="utf-8") as f:
        return float(re.search(r"MODEL_SCALE = ([0-9.]+)F", f.read()).group(1))


def raster_quad(faces, zbufs, W, texa, uv, light, fog, ss=2):
    """Rasterise one textured quad, given by its world corners W[(s, t)] for s, t in {0, 1}, onto the six faces."""
    u0, v0, u1, v1 = uv
    th, tw = texa.shape[:2]
    S = N * ss
    C = {st: to_cube(w) for st, w in W.items()}
    for k, (n, a, b) in enumerate(FACES):
        proj = {}
        for st, cc in C.items():
            depth = float(np.dot(cc, n))
            if depth <= 0.05:
                break
            proj[st] = ((np.dot(cc, a) / depth + 1) / 2 * S, (np.dot(cc, b) / depth + 1) / 2 * S, depth)
        if len(proj) < 4:
            continue
        xs = [q[0] for q in proj.values()]
        ys = [q[1] for q in proj.values()]
        if max(xs) < 0 or min(xs) > S or max(ys) < 0 or min(ys) > S:
            continue
        img, zb = faces[k], zbufs[k]
        for tri in (((0, 0), (1, 0), (1, 1)), ((0, 0), (1, 1), (0, 1))):
            A, B, Cc = (proj[q] for q in tri)
            x0, x1 = max(0, int(min(A[0], B[0], Cc[0]))), min(S - 1, int(max(A[0], B[0], Cc[0])) + 1)
            y0, y1 = max(0, int(min(A[1], B[1], Cc[1]))), min(S - 1, int(max(A[1], B[1], Cc[1])) + 1)
            if x0 > x1 or y0 > y1:
                continue
            den = (B[1] - Cc[1]) * (A[0] - Cc[0]) + (Cc[0] - B[0]) * (A[1] - Cc[1])
            if abs(den) < 1e-9:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            l1 = ((B[1] - Cc[1]) * (gx - Cc[0]) + (Cc[0] - B[0]) * (gy - Cc[1])) / den
            l2 = ((Cc[1] - A[1]) * (gx - Cc[0]) + (A[0] - Cc[0]) * (gy - Cc[1])) / den
            l3 = 1 - l1 - l2
            inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if not inside.any():
                continue
            with np.errstate(divide="ignore", invalid="ignore"):
                z = 1.0 / (l1 / A[2] + l2 / B[2] + l3 / Cc[2])
            s_ = (l1 * tri[0][0] / A[2] + l2 * tri[1][0] / B[2] + l3 * tri[2][0] / Cc[2]) * z
            t_ = (l1 * tri[0][1] / A[2] + l2 * tri[1][1] / B[2] + l3 * tri[2][1] / Cc[2]) * z
            s_, t_ = np.nan_to_num(s_), np.nan_to_num(t_)
            tu = np.clip((u0 + s_ * (u1 - u0)).astype(int), 0, tw - 1)
            tv = np.clip((v0 + t_ * (v1 - v0)).astype(int), 0, th - 1)
            col = texa[tv, tu]
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            okm = inside & np.isfinite(z) & (z < sub) & (col[..., 3] > 10)
            sub[okm] = z[okm]
            px = img[y0:y1 + 1, x0:x1 + 1]
            rgb = col[..., :3] * light
            rgb = rgb * (1 - fog) + HAZE * fog
            px[..., :3][okm] = rgb[okm]
            px[..., 3][okm] = 255


KEY_COL, RIM_COL, AMBIENT = np.array((1.0, 0.86, 0.72)), np.array((1.0, 0.62, 0.22)), np.array((0.40, 0.33, 0.45))
RIM_DIR = r3.norm((0.0, 0.25, 1.0))   # the Rift is ahead (+z) and low in the sky
KEY_DIR = r3.norm((0.3, 0.8, -0.4))


def shade(nrm, center, tint, rim_power=0.85):
    view = -r3.norm(center)
    light = AMBIENT + KEY_COL * max(0.0, float(np.dot(nrm, KEY_DIR))) * 0.7
    rr = max(0.0, float(np.dot(nrm, RIM_DIR))) * (1.0 - max(0.0, float(np.dot(nrm, view)))) ** 0.6
    return (light + RIM_COL * rr * rim_power) * np.array(tint)


def place_dino(faces, zbufs, name, pos, yaw, anim=None, t=0.0, sex="male", tint=(1.0, 1.0, 1.0), fog=0.0):
    """Rasterise a posed model at world position `pos` (blocks, feet), turned by `yaw` degrees (0 = facing -z,
    i.e. towards a viewer looking at it from the origin along +z; 90 = facing -x, the viewer's right)."""
    rig, tex, model = r3.load(name, sex)
    p = None
    if anim:
        try:
            p = r3.pose(model, anim, t)
        except StopIteration:
            p = None
    scale = species_scale(name) / 16.0
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    R = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    P = np.array(pos, dtype=float)
    texa = np.asarray(tex, dtype=float)
    for c, face, corners, uv in rig.cube_faces(p, ("female_display", "saddle")):
        if uv[2] <= uv[0] or uv[3] <= uv[1]:
            continue
        W = {st: P + R @ (np.array(wp, dtype=float) * scale) for st, (_l, wp) in corners.items()}
        nrm = np.cross(W[(1, 0)] - W[(0, 0)], W[(0, 1)] - W[(0, 0)])
        nn = np.linalg.norm(nrm)
        if nn < 1e-9:
            continue
        raster_quad(faces, zbufs, W, texa, uv, shade(nrm / nn, W[(0, 0)], tint), fog)


# ---- trees, built from the mod's own blocks ------------------------------------------------------------------

BLOCK_TEX = os.path.join(r3.ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "block")
_TEX = {}


def block_tex(name):
    if name not in _TEX:
        a = np.asarray(Image.open(os.path.join(BLOCK_TEX, name + ".png")).convert("RGBA"), dtype=float).copy()
        if name.endswith("_leaves"):  # opaque leaves ("fast" graphics): holes become the leaves' shadow
            holes = a[..., 3] < 128
            dark = a[~holes][:, :3].mean(axis=0) * 0.45 if (~holes).any() else np.array([30.0, 40.0, 20.0])
            a[holes, :3] = dark
            a[..., 3] = 255
        _TEX[name] = a
    return _TEX[name]


def tree_voxels(kind, rng):
    """{(x, y, z): block} of one tree, trunk base at (0, 0, 0)."""
    v = {}
    if kind == "araucaria":  # tall bare trunk, flat crown of tiered branches
        h = int(rng.integers(15, 21))
        for y in range(h):
            v[(0, y, 0)] = "araucaria_log"
        for i, y in enumerate(range(h - 6, h + 1, 2)):
            r = 4 - (i // 2) + (1 if i == 0 else 0)
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if abs(dx) + abs(dz) <= r and (dx == 0 or dz == 0 or abs(dx) + abs(dz) <= r - 1 or rng.random() < 0.3):
                        v.setdefault((dx, y, dz), "araucaria_leaves")
                        if abs(dx) + abs(dz) >= r - 1 and rng.random() < 0.5:
                            v.setdefault((dx, y - 1, dz), "araucaria_leaves")
        v[(0, h + 1, 0)] = "araucaria_leaves"
    elif kind == "magnolia":  # short trunk, round crown
        h = int(rng.integers(5, 8))
        for y in range(h):
            v[(0, y, 0)] = "magnolia_log"
        r = 3
        for dx in range(-r, r + 1):
            for dy in range(-2, 3):
                for dz in range(-r, r + 1):
                    if dx * dx + (dy * 1.4) ** 2 + dz * dz <= r * r + rng.uniform(-2, 1.5):
                        v.setdefault((dx, h - 1 + dy, dz), "magnolia_leaves")
    elif kind == "sabal":  # palm: slender trunk, fronds drooping from the top
        h = int(rng.integers(6, 10))
        for y in range(h):
            v[(0, y, 0)] = "sabal_log"
        v[(0, h, 0)] = "sabal_leaves"
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            for s in range(1, 4):
                v[(dx * s, h - (1 if s == 3 else 0), dz * s)] = "sabal_leaves"
    else:  # metasequoia: tall cone
        h = int(rng.integers(16, 23))
        for y in range(h):
            v[(0, y, 0)] = "metasequoia_log"
        for y in range(4, h + 2):
            r = int(round((h + 2 - y) / (h - 2) * 3.4))
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if dx * dx + dz * dz <= r * r + 0.5 and (y % 3 or dx * dx + dz * dz < r * r):
                        v.setdefault((dx, y, dz), "metasequoia_leaves")
    return v


QUAD = {  # face -> (normal, corner offsets for (s, t) in {0, 1}, texture suffix for logs)
    "up": ((0, 1, 0), lambda s, t: (s, 1, t), "_top"),
    "down": ((0, -1, 0), lambda s, t: (s, 0, 1 - t), "_top"),
    "north": ((0, 0, -1), lambda s, t: (1 - s, 1 - t, 0), ""),
    "south": ((0, 0, 1), lambda s, t: (s, 1 - t, 1), ""),
    "west": ((-1, 0, 0), lambda s, t: (0, 1 - t, s), ""),
    "east": ((1, 0, 0), lambda s, t: (1, 1 - t, 1 - s), ""),
}
FACE_SHADE = {"up": 1.0, "down": 0.5, "north": 0.8, "south": 0.8, "west": 0.6, "east": 0.6}


def place_tree(faces, zbufs, kind, pos, seed, fog=0.0):
    rng = np.random.default_rng(seed)
    vox = tree_voxels(kind, rng)
    base = np.array(pos, dtype=float) - np.array([0.5, 0.0, 0.5])
    for (x, y, z), blk in vox.items():
        for face, (nrm, corner, suffix) in QUAD.items():
            if (x + nrm[0], y + nrm[1], z + nrm[2]) in vox:
                continue
            tex = block_tex(blk + (suffix if blk.endswith("_log") else ""))
            W = {(s, t): base + np.array((x, y, z), dtype=float) + np.array(corner(s, t), dtype=float)
                 for s in (0, 1) for t in (0, 1)}
            light = shade(np.array(nrm, dtype=float), W[(0, 0)], (0.9, 0.82, 0.86)) * FACE_SHADE[face]
            raster_quad(faces, zbufs, W, tex, (0, 0, 16, 16), light, fog)


G = -EYE  # the valley floor
SCENE = [
    # name, position (x, y, z in blocks), yaw, animation, t, sex, tint, fog
    ("parasaurolophus", (-8.0, G, 24.0), 95, "graze", 0.4, "male", (0.95, 0.86, 0.86), 0.06),
    ("parasaurolophus", (-15.0, G, 28.0), 70, "idle", 0.0, "female", (0.95, 0.86, 0.86), 0.09),
    ("parasaurolophus", (10.0, G, 25.0), -100, "graze", 0.8, "female", (0.95, 0.86, 0.86), 0.07),
    ("tyrannosaurus", (21.0, G, 8.0), 125, "roar", 0.75, "male", (1.0, 0.93, 0.92), 0.0),
    ("triceratops", (-23.0, G, -2.0), 35, "idle", 0.0, "male", (0.95, 0.88, 0.88), 0.03),
    ("triceratops", (-29.0, G, -9.0), 55, "graze", 0.5, "female", (0.95, 0.88, 0.88), 0.06),
    ("alamosaurus", (14.0, G, -62.0), 70, "graze", 0.2, "male", (0.88, 0.76, 0.82), 0.26),
    ("alamosaurus", (-6.0, G, -74.0), 100, "idle", 0.0, "female", (0.88, 0.76, 0.82), 0.3),
    ("struthiomimus", (-20.0, G, -38.0), -80, "run", 0.2, "male", (0.92, 0.82, 0.86), 0.14),
    ("struthiomimus", (-25.0, G, -42.0), -80, "run", 0.6, "female", (0.92, 0.82, 0.86), 0.15),
    ("struthiomimus", (-17.0, G, -45.0), -80, "run", 0.9, "female", (0.92, 0.82, 0.86), 0.16),
    ("pteranodon", (-22.0, 9.0, 33.0), 120, "glide", 0.3, "male", (0.78, 0.65, 0.74), 0.10),
    ("pteranodon", (-31.0, 13.0, 25.0), 100, "glide", 0.6, "female", (0.78, 0.65, 0.74), 0.14),
    ("quetzalcoatlus", (38.0, 22.0, -36.0), -60, "glide", 0.1, "male", (0.78, 0.65, 0.74), 0.2),
]

# groves on both sides of the lake and a forest behind the viewer: (lon range, distance range, count, kinds)
GROVES = [((24, 75), (30, 70), 9, ("araucaria", "araucaria", "magnolia", "sabal")),
          ((-75, -24), (30, 70), 9, ("magnolia", "araucaria", "sabal", "metasequoia")),
          ((95, 265), (45, 120), 22, ("araucaria", "metasequoia", "magnolia", "araucaria"))]


def tree_positions():
    rng = np.random.default_rng(77)
    out = []
    cx, cz, ax, az = LAKE
    for (l0, l1), (d0, d1), count, kinds in GROVES:
        tries = 0
        placed = 0
        while placed < count and tries < 500:
            tries += 1
            lon = math.radians(rng.uniform(l0, l1))
            dist = rng.uniform(d0, d1)
            x, z = math.sin(lon) * dist, math.cos(lon) * dist
            if ((x - cx) / ax) ** 2 + ((z - cz) / az) ** 2 < 1.4:
                continue
            if any(math.hypot(x - p[0], z - p[2]) < 7 for _n, p, *_r in SCENE if p[1] <= G + 1):
                continue
            if any(math.hypot(x - t[1][0], z - t[1][2]) < 6 for t in out):
                continue
            out.append((kinds[placed % len(kinds)], (x, G, z), int(rng.integers(1 << 30)), min(0.45, dist / 300.0)))
            placed += 1
    return out


# ---- the rise under the viewer, in blocks ----------------------------------------------------------------------

HILL_R = 10  # radius (blocks) where the rise under the viewer meets the valley


def hill_height(i, k):
    """Height in blocks above the valley floor of the column whose centre is (i + 0.5, k + 0.5)."""
    r = math.hypot(i + 0.5, k + 0.5)
    lon = math.degrees(math.atan2(i + 0.5, k + 0.5))
    R = HILL_R + 3.0 * float(pnoise1(np.array([lon]), 8, 71, 3)[0])
    if r >= R:
        return 0
    top = EYE - 5.0  # the viewer floats a few blocks above the top, so the nearest blocks are not huge
    h = top * (1 - (r / R) ** 1.4) + float(vnoise(np.array([i / 3.0]), np.array([k / 3.0]), 72)[0]) * 1.0
    return max(0, int(round(h)))


def place_hill(faces, zbufs):
    cols = {}
    for i in range(-HILL_R - 6, HILL_R + 6):
        for k in range(-HILL_R - 6, HILL_R + 6):
            h = hill_height(i, k)
            if h > 0:
                cols[(i, k)] = h
    top_tex = block_tex("fern_litter") * np.array([0.78, 1.0, 0.62, 1.0])
    side_top = block_tex("fern_litter_side")
    soil = block_tex("peat")
    rng = np.random.default_rng(81)
    plants = []
    for (i, k), h in cols.items():
        y_top = G + h
        W = {(s, t): np.array((i + s, y_top, k + t), dtype=float) for s in (0, 1) for t in (0, 1)}
        raster_quad(faces, zbufs, W, top_tex, (0, 0, 16, 16), shade(np.array((0.0, 1.0, 0.0)), W[(0, 0)], (0.8, 0.7, 0.8)), 0.0)
        for (di, dk), face in (((1, 0), "east"), ((-1, 0), "west"), ((0, 1), "south"), ((0, -1), "north")):
            nh = cols.get((i + di, k + dk), 0)
            nrm, corner, _suf = QUAD[face]
            for y in range(nh, h):
                base = np.array((i, G + y, k), dtype=float)
                Wq = {(s, t): base + np.array(corner(s, t), dtype=float) for s in (0, 1) for t in (0, 1)}
                tex = side_top if y == h - 1 else soil
                light = shade(np.array(nrm, dtype=float), Wq[(0, 0)], (0.8, 0.7, 0.8)) * FACE_SHADE[face]
                raster_quad(faces, zbufs, Wq, tex, (0, 0, 16, 16), light, 0.0)
        r = math.hypot(i + 0.5, k + 0.5)
        if rng.random() < 0.22:
            plants.append((i, y_top, k, rng.choice(["bracken", "bracken", "cretaceous_grass", "horsetail", "royal_fern",
                                                   "young_cycad", "williamsonia"])))
    for i, y, k, name in plants:  # crossed sprites, like the plant blocks in the game
        tex = block_tex(name)
        for (x0, z0, x1, z1) in ((0.15, 0.15, 0.85, 0.85), (0.15, 0.85, 0.85, 0.15)):
            W = {(s, t): np.array((i + (x0 if s == 0 else x1), y + (1 - t), k + (z0 if s == 0 else z1)), dtype=float)
                 for s in (0, 1) for t in (0, 1)}
            raster_quad(faces, zbufs, W, tex, (0, 0, 16, 16), shade(np.array((0.0, 1.0, 0.0)), W[(0, 0)], (0.75, 0.68, 0.75)) * 0.85, 0.0)


def place_sprite(faces, zbufs, name, x, y, z, size=1.0, fog=0.0):
    """A plant as two crossed quads, like the plant blocks of the game."""
    tex = block_tex(name)
    h0, h1 = 0.5 - 0.35 * size, 0.5 + 0.35 * size
    for (x0, z0, x1, z1) in ((h0, h0, h1, h1), (h0, h1, h1, h0)):
        W = {(s, t): np.array((x - 0.5 + (x0 if s == 0 else x1), y + (1 - t) * size, z - 0.5 + (z0 if s == 0 else z1)),
                              dtype=float) for s in (0, 1) for t in (0, 1)}
        raster_quad(faces, zbufs, W, tex, (0, 0, 16, 16),
                    shade(np.array((0.0, 1.0, 0.0)), W[(0, 0)], (0.75, 0.68, 0.75)) * 0.85, fog)


def place_block(faces, zbufs, name, x, y, z, fog=0.0):
    tex = block_tex(name)
    base = np.array((math.floor(x), y, math.floor(z)), dtype=float)
    for face, (nrm, corner, _suf) in QUAD.items():
        if face == "down":
            continue
        W = {(s, t): base + np.array(corner(s, t), dtype=float) for s in (0, 1) for t in (0, 1)}
        raster_quad(faces, zbufs, W, tex, (0, 0, 16, 16),
                    shade(np.array(nrm, dtype=float), W[(0, 0)], (0.6, 0.52, 0.6)) * FACE_SHADE[face], fog)


def place_valley_details(faces, zbufs):
    """Plants and a few boulders on the valley floor, denser close to the viewer."""
    rng = np.random.default_rng(91)
    cx, cz, ax, az = LAKE
    for _ in range(900):
        dist = 9.0 + rng.random() ** 1.8 * 55.0
        lon = math.radians(rng.uniform(-180, 180))
        x, z = math.sin(lon) * dist, math.cos(lon) * dist
        r = ((x - cx) / ax) ** 2 + ((z - cz) / az) ** 2
        if r < 1.15:
            continue
        near_water = r < 1.6
        if near_water:
            name = rng.choice(["horsetail", "rush", "archaefructus", "royal_fern"])
        else:
            name = rng.choice(["bracken", "bracken", "cretaceous_grass", "cretaceous_grass", "young_cycad",
                               "williamsonia", "clubmoss", "royal_fern"])
        if name == "rush" and not os.path.exists(os.path.join(BLOCK_TEX, "rush.png")):
            name = "horsetail"
        place_sprite(faces, zbufs, name, math.floor(x) + 0.5, G, math.floor(z) + 0.5, 1.0, min(0.3, dist / 300.0))
    for _ in range(14):
        dist = rng.uniform(14, 50)
        lon = math.radians(rng.uniform(-180, 180))
        x, z = math.sin(lon) * dist, math.cos(lon) * dist
        if ((x - cx) / ax) ** 2 + ((z - cz) / az) ** 2 < 1.3:
            continue
        rock = rng.choice(["limestone", "laterite", "gneiss"])
        for dx, dy, dz in ((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0))[:int(rng.integers(1, 5))]:
            place_block(faces, zbufs, rock, x + dx, G + dy, z + dz, min(0.3, dist / 300.0))


def render_faces():
    strip, salpha = paint_strip()
    faces, zbufs = [], []
    for k in range(6):
        d = face_dirs(k)
        lon, lat = lonlat(d)
        img = sky(lon, lat, (N, N))
        sm, scol = smoke(lon, lat, (N, N))
        img[sm] = scol[sm]
        below = lat < 0
        if below.any():
            g = ground(d, lon, lat, (N, N))
            img[below] = g[below]
        # the land strip over both
        sx = (((lon + 180.0) / 360.0) * STRIP_W).astype(int) % STRIP_W
        sy = ((STRIP_LAT1 - lat) / (STRIP_LAT1 - STRIP_LAT0) * STRIP_H).astype(int)
        inside = (sy >= 0) & (sy < STRIP_H)
        syc = np.clip(sy, 0, STRIP_H - 1)
        land = inside & salpha[syc, sx] & (lat > -0.8)
        img[land] = strip[syc, sx][land]
        # 2x supersampled RGBA canvas for the models
        big = np.repeat(np.repeat(img, 2, axis=0), 2, axis=1)
        canvas = np.dstack([big, np.full(big.shape[:2], 255.0)])
        faces.append(canvas)
        zbufs.append(np.full(big.shape[:2], np.inf))
    place_hill(faces, zbufs)
    place_valley_details(faces, zbufs)
    print("  hill and plants placed")
    for kind, pos, seed, fog in tree_positions():
        place_tree(faces, zbufs, kind, pos, seed, fog)
    print("  trees placed")
    for name, pos, yaw, anim, t, sex, tint, fog in SCENE:
        place_dino(faces, zbufs, name, pos, yaw, anim, t, sex, tint, fog)
        print("  placed", name)
    out = []
    for canvas in faces:
        im = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "RGBA").convert("RGB")
        im = im.resize((N, N), Image.BOX)  # back to the pixel grid: the models sit with the painting
        out.append(im.resize((OUT_SIZE, OUT_SIZE), Image.NEAREST))
    return out


def preview(faces):
    """Faces unfolded as a cross (top above the front row, bottom below) at 1/4 size."""
    s = OUT_SIZE // 4
    sheet = Image.new("RGB", (s * 4, s * 3), (20, 14, 26))
    small = [f.resize((s, s), Image.BOX) for f in faces]
    for i, k in enumerate((3, 0, 1, 2)):  # left, front, right, back
        sheet.paste(small[k], (i * s, s))
    sheet.paste(small[4], (s, 0))
    sheet.paste(small[5], (s, 2 * s))
    return sheet


def main():
    os.makedirs(OUT, exist_ok=True)
    faces = render_faces()
    for k, im in enumerate(faces):
        im.save(os.path.join(OUT, f"panorama_{k}.png"), optimize=True)
    preview(faces).save(PREVIEW, optimize=True)
    print("panorama written:", OUT)


if __name__ == "__main__":
    main()
