"""Palette fitting: given a tone map (0 = darkest), build a ramp whose luminance mean and p5-p95 contrast hit a
target (measured on the vanilla block of the same role), with our own hue, saturation and hue shift."""
import colorsys
import numpy as np

W = np.array([0.299, 0.587, 0.114])


def colour_at(lum, hue, sat):
    """RGB with the given hue/saturation (HSV) whose luma is lum (bisection on V)."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        v = (lo + hi) / 2
        rgb = np.array(colorsys.hsv_to_rgb(hue % 1.0, sat, v)) * 255
        if rgb @ W < lum:
            lo = v
        else:
            hi = v
    return tuple(np.clip(rgb, 0, 255))


def stats_of(t, lums):
    l = np.array(lums)[t]
    return l.mean(), np.percentile(l, 95) - np.percentile(l, 5)


def fit(t, n, mean, ctr, hue, sat, hue_shift=0.0, sat_shift=0.0, gamma=1.0):
    """Ramp of n colours. Tone k gets luma a + b * ((k / (n-1)) ** gamma - 0.5); a and b are solved so the
    image's mean luma and p5-p95 contrast match (mean, ctr). Shadows rotate hue by -hue_shift and gain
    sat_shift saturation; highlights the opposite."""
    best = None
    for b in np.linspace(5, 220, 216):
        base = [((k / (n - 1)) ** gamma - 0.5) * b for k in range(n)]
        m0, c0 = stats_of(t, base)
        a = mean - m0
        err = abs(c0 - ctr)
        if best is None or err < best[0]:
            best = (err, a, b)
    _, a, b = best
    out = []
    for k in range(n):
        s = k / (n - 1)
        lum = float(np.clip(a + ((s ** gamma) - 0.5) * b, 8, 252))
        h = hue + hue_shift * (s - 0.5) * 2
        sa = max(0.0, sat - sat_shift * (s - 0.5) * 2)
        out.append(colour_at(lum, h, sa))
    return out
