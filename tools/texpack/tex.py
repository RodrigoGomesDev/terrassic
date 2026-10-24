"""Terrassic texture engine: 16x16 tileable pixel art drawn the way vanilla blocks are drawn.

Everything lives on the 16x16 torus (every neighbour lookup wraps), so textures tile without seams by construction.
The pipeline for a material is always the same:
  1. a height/value field   (tileable value noise, tileable Voronoi cells, strokes)
  2. light from the top-left (emboss of the height field)
  3. quantise to a short colour ramp (5-8 tones) by quantiles, so the contrast is controlled, not left to the noise
  4. clean-up: isolated pixels are merged into their neighbours, the way a pixel artist would clean a sprite
  5. colourise with a hue-shifted ramp (cool, saturated shadows; warm, light highlights)

No pixel comes from third-party art: vanilla is only the yardstick for brightness and contrast (see palettes.py).
"""
import colorsys
import math

import numpy as np
from PIL import Image

N = 16


# ------------------------------------------------------------------ random + torus helpers
def rng(seed):
    return np.random.default_rng(seed)


def roll(a, dy, dx):
    """a shifted so that out[y, x] = a[y + dy, x + dx] (wrapping)."""
    return np.roll(np.roll(a, -dy, axis=0), -dx, axis=1)


def wrapdist(a, b):
    d = abs(a - b) % N
    return np.minimum(d, N - d)


def normalize(a):
    lo, hi = float(a.min()), float(a.max())
    return (a - lo) / (hi - lo) if hi > lo else np.zeros_like(a)


# ------------------------------------------------------------------ fields
def value_noise(seed, px, py=None):
    """Tileable value noise: a random px x py lattice on the torus, smoothstep-interpolated, values in [0, 1]."""
    py = px if py is None else py
    g = rng(seed).random((py, px))
    ys = (np.arange(N) + 0.5) * py / N - 0.5
    xs = (np.arange(N) + 0.5) * px / N - 0.5
    y0 = np.floor(ys).astype(int)
    x0 = np.floor(xs).astype(int)
    fy = ys - y0
    fx = xs - x0
    fy = fy * fy * (3 - 2 * fy)
    fx = fx * fx * (3 - 2 * fx)
    Y0, X0 = np.meshgrid(y0 % py, x0 % px, indexing="ij")
    Y1, X1 = np.meshgrid((y0 + 1) % py, (x0 + 1) % px, indexing="ij")
    FY, FX = np.meshgrid(fy, fx, indexing="ij")
    top = g[Y0, X0] * (1 - FX) + g[Y0, X1] * FX
    bot = g[Y1, X0] * (1 - FX) + g[Y1, X1] * FX
    return top * (1 - FY) + bot * FY


def fbm(seed, layers):
    """layers = [(px, py, weight), ...] -> normalised sum."""
    out = np.zeros((N, N))
    for i, (px, py, w) in enumerate(layers):
        out += w * value_noise(seed * 31 + i * 7919, px, py)
    return normalize(out)


def white(seed):
    return rng(seed).random((N, N))


def jittered_points(seed, nx, ny, jitter=0.8, offset_rows=True):
    """One point per cell of an nx x ny grid, moved randomly inside its cell; odd rows shifted half a cell
    (running bond) so stones don't line up in columns."""
    r = rng(seed)
    pts = []
    cw, ch = N / nx, N / ny
    for j in range(ny):
        for i in range(nx):
            ox = (0.5 * cw if (offset_rows and j % 2) else 0.0)
            x = (i + 0.5) * cw + ox + (r.random() - 0.5) * jitter * cw
            y = (j + 0.5) * ch + (r.random() - 0.5) * jitter * ch
            pts.append((x % N, y % N))
    return pts


def voronoi(points, sx=1.0, sy=1.0, warp=None, warp_amp=0.0):
    """Nearest-point cells on the torus. sx/sy stretch the metric (sx < 1 -> wider cells).
    warp: optional (N, N) field in [0,1] that wobbles the borders. Returns (idx, d1, d2)."""
    ys, xs = np.mgrid[0:N, 0:N]
    cx = xs + 0.5
    cy = ys + 0.5
    ds = []
    for (px, py) in points:
        dx = wrapdist(cx, px) * sx
        dy = wrapdist(cy, py) * sy
        ds.append(np.sqrt(dx * dx + dy * dy))
    ds = np.stack(ds)
    if warp is not None:
        # each cell gets its own phase of the warp field, so borders wobble differently per pair
        for k in range(len(points)):
            ds[k] += warp_amp * (roll(warp, k * 5, k * 3) - 0.5)
    order = np.argsort(ds, axis=0)
    idx = order[0]
    d1 = np.take_along_axis(ds, order[:1], 0)[0]
    d2 = np.take_along_axis(ds, order[1:2], 0)[0]
    return idx, d1, d2


def cell_edges(idx, right_down_only=True):
    """Mask of 1-px borders between cells. With right_down_only a pixel is border when its right or lower neighbour
    belongs to another cell, which gives lines exactly 1 px thick."""
    e = (roll(idx, 0, 1) != idx) | (roll(idx, 1, 0) != idx)
    if not right_down_only:
        e |= (roll(idx, 0, -1) != idx) | (roll(idx, -1, 0) != idx)
    return e


def distance_to(mask):
    """Euclidean distance (on the torus) from every pixel to the nearest True pixel of mask."""
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        return np.full((N, N), 99.0)
    gy, gx = np.mgrid[0:N, 0:N]
    best = np.full((N, N), 99.0)
    for y, x in zip(ys, xs):
        d = np.sqrt(wrapdist(gy, y) ** 2 + wrapdist(gx, x) ** 2)
        best = np.minimum(best, d)
    return best


# ------------------------------------------------------------------ light
def emboss(h, strength=1.0):
    """Light from the top-left: positive where the surface faces the light."""
    return strength * (roll(h, 1, 1) - roll(h, -1, -1)) * 0.5 + strength * 0.5 * (roll(h, 1, 0) - roll(h, -1, 0)) * 0.5


# ------------------------------------------------------------------ quantise + clean
def quantize(v, fractions):
    """Tone index map with tone k covering fractions[k] of the pixels (darkest first)."""
    fr = np.array(fractions, float)
    fr = fr / fr.sum()
    cuts = np.quantile(v, np.cumsum(fr)[:-1])
    return np.searchsorted(cuts, v, side="right")


def thresholds(v, cuts):
    return np.searchsorted(np.array(cuts), v, side="right")


def neighbours(t, diag=True):
    offs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diag:
        offs += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return np.stack([roll(t, dy, dx) for dy, dx in offs])


def isolated(t):
    """Pixels whose tone appears in none of the 8 neighbours."""
    nb = neighbours(t, True)
    return ~(nb == t[None]).any(axis=0)


def cleanup(t, passes=2, keep=None, diag=True):
    """Merge isolated pixels into the neighbour tone closest to them (pixel-artist clean-up).
    keep: boolean mask of pixels that may stay isolated (sparkles, pebble highlights)."""
    t = t.copy()
    for _ in range(passes):
        iso = isolated(t) if diag else ~(neighbours(t, False) == t[None]).any(axis=0)
        if keep is not None:
            iso &= ~keep
        if not iso.any():
            break
        nb = neighbours(t, True)
        for y, x in zip(*np.nonzero(iso)):
            vals = nb[:, y, x]
            # nearest tone among the neighbours, ties -> the most common one
            uniq, counts = np.unique(vals, return_counts=True)
            dist = np.abs(uniq - t[y, x])
            best = uniq[np.lexsort((-counts, dist))[0]]
            t[y, x] = best
    return t


def isolated_ratio(t):
    return float(isolated(t).mean())


# ------------------------------------------------------------------ colour
def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgbhex(c):
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)


def ramp(n, hue, light=(0.25, 0.72), sat=(0.30, 0.18), hue_shift=(-0.03, 0.03), sat_peak=0.35):
    """Hue-shifted ramp, darkest first. hue in [0,1) (HLS); shadows rotate by hue_shift[0], highlights by
    hue_shift[1]; saturation goes from sat[0] (dark) to sat[1] (light) with a bump in the dark-middle."""
    out = []
    for i in range(n):
        t = i / (n - 1)
        h = (hue + hue_shift[0] * (1 - t) + hue_shift[1] * t) % 1.0
        l = light[0] + (light[1] - light[0]) * t
        s = sat[0] + (sat[1] - sat[0]) * t + sat_peak * 0.25 * math.sin(math.pi * t) * 0
        r, g, b = colorsys.hls_to_rgb(h, l, max(0.0, min(1.0, s)))
        out.append((r * 255, g * 255, b * 255))
    return out


def ramp_hex(hexes):
    return [hexrgb(h) for h in hexes]


def colorize(t, pal, alpha=None):
    pal = np.array(pal, float)
    rgb = pal[np.clip(t, 0, len(pal) - 1)]
    a = np.full((N, N, 1), 255.0) if alpha is None else alpha[..., None].astype(float)
    return Image.fromarray(np.concatenate([rgb, a], axis=2).round().astype(np.uint8), "RGBA")


def gray_ramp(n, lo, hi):
    return [(v, v, v) for v in np.linspace(lo, hi, n)]


# ------------------------------------------------------------------ checks
def seam_score(img):
    """Mean colour jump across the wrap edges divided by the mean jump inside: ~1 means seamless."""
    a = np.asarray(img.convert("RGB"), float)
    inner = (np.abs(np.diff(a, axis=0)).mean() + np.abs(np.diff(a, axis=1)).mean()) / 2
    edge = (np.abs(a[0] - a[-1]).mean() + np.abs(a[:, 0] - a[:, -1]).mean()) / 2
    return edge / max(inner, 1e-6)


def stats(img):
    a = np.asarray(img.convert("RGB"), float)
    lum = a @ np.array([0.299, 0.587, 0.114])
    colours = len({tuple(p) for p in a.reshape(-1, 3).astype(int)})
    return {"mean": round(float(lum.mean()), 1), "std": round(float(lum.std()), 1), "colours": colours,
            "seam": round(seam_score(img), 2)}
