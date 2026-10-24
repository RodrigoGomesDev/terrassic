"""Pixel-art helpers for the cover: dithered gradients, 1D noise ridges, palette ramps."""
import numpy as np

BAYER4 = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16.0


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def ramp(stops, t):
    """stops = [(pos, '#rrggbb'), ...] sorted; t array in [0,1] -> rgb array."""
    t = np.clip(t, 0, 1)
    pos = np.array([p for p, _ in stops])
    cols = np.array([hexrgb(c) for _, c in stops])
    out = np.zeros(t.shape + (3,))
    for ch in range(3):
        out[..., ch] = np.interp(t, pos, cols[:, ch])
    return out


def bayer(h, w):
    return np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]


def banded(t, levels):
    """Quantise t to `levels` bands with ordered dithering between neighbouring bands."""
    h, w = t.shape
    x = np.clip(t, 0, 1) * (levels - 1)
    k = np.floor(x)
    return (k + (x - k > bayer(h, w))) / (levels - 1)


def noise1d(n, scale, rng, octaves=4, persistence=0.5):
    """Smooth value noise of length n in [-1, 1]."""
    out = np.zeros(n)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        pts = int(n / scale * 2 ** o) + 3
        v = rng.uniform(-1, 1, pts)
        xs = np.linspace(0, pts - 3, n)
        i = np.floor(xs).astype(int)
        f = xs - i
        f = f * f * (3 - 2 * f)
        out += amp * (v[i] * (1 - f) + v[i + 1] * f)
        total += amp
        amp *= persistence
    return out / total


def noise2d(h, w, scale, rng, octaves=3):
    out = np.zeros((h, w))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        s = scale / 2 ** o
        gh, gw = int(h / s) + 3, int(w / s) + 3
        g = rng.uniform(-1, 1, (gh, gw))
        ys, xs = np.linspace(0, h / s, h), np.linspace(0, w / s, w)
        yi, xi = np.floor(ys).astype(int), np.floor(xs).astype(int)
        fy, fx = ys - yi, xs - xi
        fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
        a = g[yi][:, xi] * (1 - fx) + g[yi][:, xi + 1] * fx
        b = g[yi + 1][:, xi] * (1 - fx) + g[yi + 1][:, xi + 1] * fx
        out += amp * (a * (1 - fy)[:, None] + b * fy[:, None])
        total += amp
        amp *= 0.5
    return out / total


def mix(a, b, t):
    t = np.asarray(t, dtype=float)
    if t.ndim and t.shape[-1:] != (3,):
        t = t[..., None]
    return a * (1 - t) + b * t


def paint(img, mask, col, alpha=1.0):
    """img (h,w,3) float; mask bool or float (h,w); col rgb."""
    m = mask.astype(float) * alpha
    img[:] = img * (1 - m[..., None]) + np.asarray(col, dtype=float) * m[..., None]
