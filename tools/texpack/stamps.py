"""Hand-placed details for the texture engine: blue-noise positions on the 16x16 torus, small stamped shapes and a
calm base of one main tone with a few large patches."""
import numpy as np

import tex as T
from tex import N


def poisson(seed, n, rmin, tries=4000):
    """Up to n points on the torus, none closer than rmin to another (blue noise: even, never clumped)."""
    r = T.rng(seed)
    pts = []
    for _ in range(tries):
        if len(pts) >= n:
            break
        p = r.random(2) * N
        if all(min(abs(p[0] - q[0]), N - abs(p[0] - q[0])) ** 2 + min(abs(p[1] - q[1]), N - abs(p[1] - q[1])) ** 2
               >= rmin * rmin for q in pts):
            pts.append(p)
    return [(int(x) % N, int(y) % N) for x, y in pts]


def stamp(t, x, y, rows, tones):
    """Paint a small shape: rows are strings, each character is looked up in tones ('.' = leave as is)."""
    for j, row in enumerate(rows):
        for i, c in enumerate(row):
            if c == ".":
                continue
            v = tones[c]
            yy, xx = (y + j) % N, (x + i) % N
            t[yy, xx] = v(t[yy, xx]) if callable(v) else v


def base(seed, main, alt_lo, alt_hi, lo_share=0.18, hi_share=0.18, layers=((2, 4, .6), (4, 8, .4))):
    """Tone map of one main tone with large soft patches of alt_lo / alt_hi, cleaned of lonely pixels."""
    f = T.fbm(seed, list(layers))
    t = np.full((N, N), main)
    t[f < np.quantile(f, lo_share)] = alt_lo
    t[f > np.quantile(f, 1 - hi_share)] = alt_hi
    return T.cleanup(t, 3)
