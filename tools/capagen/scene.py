"""
Painted pixel-art layers of the cover: Late Cretaceous dusk, the Rift (a.k.a. a Fenda) torn open in the sky,
a smoking volcano, a lake, araucarias and ferns. Everything is drawn by code at low resolution and
scaled up with nearest neighbour, so it stays crisp pixel art.
"""
import math

import numpy as np

from pixel import banded, bayer, hexrgb, mix, noise1d, noise2d, paint, ramp

SKY = [(0.0, "#140f26"), (0.30, "#2c1d45"), (0.55, "#6a3254"), (0.75, "#c35a3c"), (0.90, "#ec9a4a"),
       (1.0, "#f7cf7a")]
AMBER_CORE = hexrgb("#fff4cf")
AMBER = hexrgb("#ffb63c")
AMBER_DEEP = hexrgb("#e0661c")


def rift_path(h_end, x0, rng, h):
    """x of the Rift's crack for every row (NaN below its end), plus its half-width."""
    xs = np.full(h, np.nan)
    ws = np.zeros(h)
    x = float(x0)
    for y in range(h_end):
        if y % 3 == 0:
            x += rng.choice([-1.6, -1.0, 0.0, 1.0, 1.6])
            x += (x0 - x) * 0.08
        xs[y] = x
        t = y / h_end
        ws[y] = 0.6 + 5.5 * math.sin(math.pi * min(1.0, t * 1.02)) ** 0.7
    return xs, ws


def rift_branches(xs, ws, rng, n=7):
    """Short forked cracks leaving the Rift: list of pixel paths."""
    ys = [y for y in range(len(xs)) if not np.isnan(xs[y])]
    out = []
    for _ in range(n):
        y = int(rng.uniform(ys[0] + 6, ys[-1] - 6))
        side = rng.choice([-1, 1])
        x, path = xs[y] + side * ws[y], []
        for s in range(int(rng.uniform(8, 22))):
            x += side * rng.uniform(0.6, 1.6)
            y += rng.choice([-1, 0, 1])
            path.append((int(x), int(y)))
        out.append(path)
    return out


def rift_distance(xs, ws, h, w):
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.full((h, w), 1e9)
    for y in range(h):
        if np.isnan(xs[y]):
            continue
        dy = (yy - y) * 1.0
        dd = np.sqrt((xx - xs[y]) ** 2 + dy ** 2) - ws[y]
        np.minimum(d, dd, out=d)
    return np.maximum(d, 0)


def sky_layer(w, h, horizon, rift_x, rift_end, seed=7):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    t = yy / horizon
    img = ramp(SKY, banded(t, 18))

    # stars, fading towards the glow
    stars = (rng.random((h, w)) > 0.9965) & (yy < horizon * 0.45)
    paint(img, stars, hexrgb("#e9ddff"), 0.9)

    # the Rift: glow, crack and the light it throws on the clouds
    xs, ws = rift_path(rift_end, rift_x, rng, h)
    d = rift_distance(xs, ws, h, w)
    glow = np.exp(-d / 26.0) * 0.85 + np.exp(-d / 7.0) * 0.5
    g = banded(np.clip(glow, 0, 1), 9)
    img[:] = mix(img, AMBER_DEEP, np.clip(g * 1.2, 0, 0.75))
    img[:] = mix(img, AMBER, np.clip((g - 0.45) * 1.6, 0, 1))
    crack = d <= 0.0
    edge = (d > 0) & (d <= 1.2)
    for path in rift_branches(xs, ws, rng):
        for i, (bx, by) in enumerate(path):
            if 0 <= bx < w and 0 <= by < h:
                img[by, bx] = AMBER if i < len(path) * 0.6 else mix(img[by, bx], AMBER, 0.6)
    paint(img, edge, AMBER)
    paint(img, crack, AMBER_CORE)

    # clouds: long bands, lit from the Rift side
    cn = np.repeat(noise2d(h, w // 5 + 1, 6, rng, 4), 5, axis=1)[:, :w]
    fine = noise2d(h, w, 6, rng, 2)
    band = np.exp(-((yy - horizon * 0.58) / (horizon * 0.13)) ** 2)
    cloud = (cn * 0.9 + fine * 0.25 + band * 0.7) > 0.66
    cloud &= yy < horizon * 0.82
    lit = np.clip(1.0 - np.abs(xx - rift_x) / (w * 0.55), 0, 1)
    under = np.roll(cloud, -2, axis=0) & ~cloud  # bottom edge catches light
    ccol = mix(hexrgb("#33213f"), hexrgb("#8c4058"), banded(lit * 0.8 + (yy / horizon) * 0.35, 5))
    img[cloud] = ccol[cloud]
    img[under] = mix(img, AMBER, (0.35 + 0.5 * lit) * (yy < horizon))[under]

    # amber shards drifting out of the Rift
    for _ in range(26):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(10, 70)
        sy = int(rng.uniform(4, rift_end + 10))
        sx = int(xs[min(sy, rift_end - 1)] + math.cos(a) * r * 1.4)
        sy = int(sy + math.sin(a) * r * 0.4)
        s = rng.integers(1, 3)
        if 0 <= sx < w and 0 <= sy < h:
            img[max(0, sy - s):sy + s + 1, sx] = AMBER_CORE if s > 1 else AMBER
            img[sy, max(0, sx - s + 1):sx + s] = AMBER
    return img, xs, d


def ridge(w, base, amp, scale, rng, octaves=4):
    return base + noise1d(w, scale, rng, octaves) * amp


def land_layer(img, w, h, horizon, rift_x, seed=11):
    """Far mountains, volcano and its smoke, mid hills and the lake. Paints into img."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    haze = hexrgb("#d77a4c")

    # far range
    r1 = ridge(w, horizon - 30, 16, 60, rng)
    m1 = yy > r1[None, :]
    c1 = mix(hexrgb("#7a3f5c"), haze, 0.35)
    shade1 = banded(np.clip((yy - r1[None, :]) / 40, 0, 1), 4)
    img[m1] = mix(c1, hexrgb("#4d2a4f"), shade1 * 0.6)[m1]

    # volcano
    vx, vtop = w * 0.20, horizon - 78
    prof = vtop + np.abs(xx[0] - vx) ** 1.25 * 0.42 + noise1d(w, 8, rng, 2) * 2.5
    crater = np.abs(xx[0] - vx) < 6
    prof = np.where(crater, vtop + 3, prof)
    mv = (yy > prof[None, :]) & (yy < horizon + 10)
    vc = mix(hexrgb("#3d2340"), hexrgb("#6b3550"), banded(np.clip((xx - vx + 40) / 120, 0, 1), 4))
    img[mv] = vc[mv]
    # lava rills
    for k in range(3):
        lx = vx + rng.uniform(-4, 4)
        for y in range(int(vtop + 3), int(vtop + 30 + k * 6)):
            lx += rng.choice([-1, 0, 0, 1])
            if 0 <= int(lx) < w:
                img[y, int(lx)] = mix(AMBER_DEEP, AMBER, 1 - (y - vtop) / 40)
    # smoke: a column of puffs drifting away from the Rift
    for k in range(14):
        t = k / 13
        cx = vx + t ** 1.7 * 60 + rng.uniform(-2, 2)
        cy = vtop - 4 - t * (vtop * 0.55)
        rad = 3 + t * 13
        d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.3) ** 2) + noise2d(h, w, 4, rng, 2) * rad * 0.35
        puff = d < rad
        shade = np.clip((yy - cy) / rad * 0.5 + 0.5, 0, 1)  # lit from below by the lava
        col = mix(hexrgb("#5a3448"), hexrgb("#2e1d34"), np.round(np.clip(t * 0.8 + (1 - shade) * 0.4, 0, 1) * 3) / 3)
        img[puff] = col[puff]
    img[int(vtop):int(vtop) + 2, int(vx - 5):int(vx + 6)] = AMBER

    # mid hills
    r2 = ridge(w, horizon - 8, 9, 40, rng)
    m2 = yy > r2[None, :]
    c2 = hexrgb("#3c2340")
    img[m2] = mix(c2, haze, 0.18 * (1 - np.clip((yy - r2[None, :]) / 20, 0, 1)))[m2]

    # lake, mirroring the sky and the Rift
    lake_top, lake_bot = horizon, int(h * 0.88)
    shore = (noise1d(w, 30, rng, 3) * 6).astype(int)
    for y in range(lake_top, lake_bot):
        my = max(0, 2 * lake_top - y - 6)
        row = mix(img[my].copy(), hexrgb("#2a1f3d"), 0.35)
        inside = (xx[0] > w * 0.18 + shore) & (xx[0] < w * 0.86 - shore)
        img[y][inside] = row[inside]
        if y % 3 == 0:
            sh = (rng.random(w) > 0.85) & inside
            img[y][sh] = mix(img[y][sh], AMBER, 0.5)
    # the Rift's reflection: broken dashes that widen towards the viewer
    rx = int(rift_x)
    for y in range(lake_top, lake_bot):
        depth = (y - lake_top) / max(1, lake_bot - lake_top)
        wdt = 1 + int(depth * 7)
        x0 = rx + int(rng.integers(-1 - wdt // 2, 2 + wdt // 2))
        seg = int(rng.integers(1, wdt + 2))
        img[y, x0 - seg:x0 + seg] = mix(AMBER, AMBER_CORE, 0.6 - depth * 0.4)
        if rng.random() < 0.5:
            img[y, x0 - seg - 2:x0 - seg] = mix(img[y, x0 - seg - 2:x0 - seg], AMBER, 0.5)
    return r2


def tree(img, cx, base, height, col, rim, rng, kind="araucaria"):
    """Silhouette tree drawn into img (h,w,3)."""
    h, w = img.shape[:2]

    def put(x, y, c):
        if 0 <= x < w and 0 <= y < h:
            img[y, x] = c
    trunk = max(1, height // 18)
    for y in range(base - height, base):
        for dx in range(-trunk // 2, trunk - trunk // 2):
            put(cx + dx, y, col)
    if kind == "araucaria":
        # flat-topped crown of tiered branches, like the monkey-puzzle pines of the Cretaceous
        tiers = max(3, height // 7)
        for i in range(tiers):
            ty = base - height + 2 + i * (height * 0.55 / tiers)
            span = int(3 + (height * 0.10) + i * 0.8 + rng.integers(0, 3))
            for dx in range(-span, span + 1):
                droop = int(abs(dx) ** 1.3 * 0.12)
                for k in range(2):
                    put(cx + dx, int(ty) + droop + k, col)
                put(cx + dx, int(ty) + droop - 1, rim if dx < 0 else col)
    else:  # cycad / tree fern
        fronds = 7
        for f in range(fronds):
            a = math.pi * (0.05 + 0.9 * f / (fronds - 1))
            L = height * 0.45
            for s in range(int(L)):
                t = s / L
                x = cx + math.cos(a) * s
                y = base - height + 1 - math.sin(a) * s * 0.6 + t * t * L * 0.5
                put(int(x), int(y), col)
                if s % 2 == 0:
                    put(int(x), int(y) + 1, col)
                    put(int(x), int(y) - 1, rim if math.cos(a) < 0 else col)


def ground_layer(w, h, top, rift_x, seed=23):
    """Foreground ground strip as RGBA."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    edge = top + noise1d(w, 25, rng, 4) * 5 + (np.abs(xx[0] - w / 2) / (w / 2)) ** 2 * -6
    m = yy > edge[None, :]
    n = noise2d(h, w, 3, rng, 2)
    t = np.clip((yy - edge[None, :]) / 30, 0, 1)
    col = mix(hexrgb("#4a2f2c"), hexrgb("#1c1220"), banded(t + n * 0.15, 5))
    lit = np.clip(1 - np.abs(xx - rift_x) / (w * 0.35), 0, 1) * (1 - t)
    col = mix(col, hexrgb("#b0603a"), banded(lit * 0.55, 4))
    rgba = np.zeros((h, w, 4))
    rgba[..., :3] = col
    rgba[..., 3] = m * 255
    # grass tufts on the edge
    for x in range(w):
        if rng.random() < 0.5:
            hgt = rng.integers(1, 4)
            y0 = int(edge[x])
            for k in range(hgt):
                if 0 <= y0 - k < h:
                    rgba[y0 - k, x, :3] = mix(hexrgb("#5a6a3a"), hexrgb("#c08048"), lit[y0, x] * 0.8)
                    rgba[y0 - k, x, 3] = 255
    return rgba, edge


def fern(rgba, cx, base, size, direction, col, hi, rng):
    """Big foreground fern frond (pixel), arching towards `direction` (+1 right, -1 left)."""
    h, w = rgba.shape[:2]

    def put(x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            rgba[y, x, :3] = c
            rgba[y, x, 3] = 255
    for f in range(5):
        a0 = math.radians(60 + f * 14 + rng.uniform(-5, 5))
        L = size * rng.uniform(0.7, 1.0)
        px, py = cx, base
        for s in range(int(L)):
            t = s / L
            ang = a0 - t * 1.4
            px += math.cos(ang) * direction
            py -= math.sin(ang)
            put(px, py, col)
            if s % 2 == 0 and t < 0.92:
                leaf = int((1 - t) * size * 0.16) + 1
                for k in range(1, leaf):
                    put(px + k * direction * 0.3 - k * math.sin(ang) * direction * 0.2, py + k * 0.7, col)
                    put(px - k * direction * 0.2, py - k * 0.8, hi if k == 1 else col)
