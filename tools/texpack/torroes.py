"""Clods, flakes and grains: the ground recipe Rodrigo approved on 2026-10-25 (study in progressao/estudo/).

Vanilla dirt reads calm from afar because its detail is small clods of 2-3 px, each lit from the top-left, packed
over a darker gap tone, with a few pebbles. A 1 px grain reads as static instead and makes a floor flicker. This module
scatters such shapes on the 16x16 torus (seamless) with the same machinery as the leaves (folhas.canopy, no holes):

    torroes(seed, pal, formas, n, min_d, pedrinhas)   -> opaque 16x16 RGBA image
    escolher(lambda s: torroes(s, ...), range(150))   -> the seed with the calmest image

pal is four colours, darkest first: 0 is the gap between shapes, 3 the lit edge. formas names shapes from FORMAS:
clods ("torrao_*") for soils, flat flakes ("lasca_*") for bedded rock, grains ("grao_*") for ash and sand.
pedrinhas: (dark, light) colours of 2 px pebbles, or None.

escolher scores macro + 4 coherence + 4 single-wave share (the study's metrics): low macro means nothing big shows
from a few blocks away, low coherence and wave share mean no stripes or regular stamps."""
import math

import numpy as np
from PIL import Image

import folhas

N = 16

FORMAS = {
    "torrao_22": ["##", "##"],
    "torrao_32": ["###", "###"],
    "torrao_23": ["##", "##", "##"],
    "torrao_31": [".##", "###", "##."],
    "torrao_21": ["##.", "###"],
    "lasca_4": ["####"],
    "lasca_5": [".####", "####."],
    "lasca_6": ["..####", "######"],
    "grao_1": ["#"],
    "grao_2": ["##"],
    "grao_3": [".#", "##"],
}
folhas.SHAPES.update(FORMAS)
TORROES = ("torrao_22", "torrao_32", "torrao_23", "torrao_31", "torrao_21")


def torroes(seed, pal, formas=TORROES, n=36, min_d=2.25, pedrinhas=None, k_peb=5):
    tone, _ = folhas.canopy(seed, list(formas), n, min_d, 0.0)
    a = np.zeros((N, N, 4), np.uint8)
    for t in range(4):
        a[tone == t, :3] = pal[t]
    a[..., 3] = 255
    if pedrinhas:
        rng = np.random.default_rng(seed + 99)
        for _ in range(k_peb):
            x, y = rng.integers(0, N, 2)
            a[y, x, :3] = pedrinhas[0]
            a[y, (x + 1) % N, :3] = pedrinhas[1]
    return Image.fromarray(a, "RGBA")


def _luma(img):
    a = np.asarray(img.convert("RGB"), float)
    return a @ np.array([0.299, 0.587, 0.114])


def macro(img):
    """Luma std after a 4x4 box blur on the torus: the structure still visible a few blocks away."""
    L = _luma(img)
    b = sum(np.roll(np.roll(L, -j, 0), -i, 1) for i in range(-1, 3) for j in range(-1, 3)) / 16
    return float(b.std())


def ondas(img):
    """(single strongest wave's share of the variance, structure-tensor coherence) on the torus."""
    L = _luma(img)
    F = np.abs(np.fft.fft2(L - L.mean())) ** 2
    F[0, 0] = 0
    tot = F.sum()
    pico = float(2 * F.max() / tot) if tot else 0.0
    gx = (np.roll(L, -1, 1) - np.roll(L, 1, 1)) / 2
    gy = (np.roll(L, -1, 0) - np.roll(L, 1, 0)) / 2
    jxx, jyy, jxy = (gx * gx).sum(), (gy * gy).sum(), (gx * gy).sum()
    coh = math.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy) if jxx + jyy else 0.0
    return pico, coh


def escolher(fazer, sementes=range(150)):
    """The image (and its seed) with the lowest macro + 4 coherence + 4 wave share."""
    best = None
    for s in sementes:
        im = fazer(s)
        pico, coh = ondas(im)
        score = macro(im) + 4 * coh + 4 * pico
        if best is None or score < best[0]:
            best = (score, s, im)
    return best[2], best[1]
