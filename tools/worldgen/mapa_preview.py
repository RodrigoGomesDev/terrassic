"""Prévia do mapa da ilha: um levantamento falso (formato de ilha_preview.py) desenhado com o mesmo algoritmo de
client/ClientIslandMap.draw(). Uso: python3 mapa_preview.py saida.png [semente] [raio]"""
import math, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ilha_preview as ip

PAPER = np.array([233, 220, 188.]); PAPER_DARK = np.array([216, 199, 158.]); INK = np.array([59, 42, 26.])
INK_SOFT = np.array([122, 100, 72.]); BLOOD = np.array([196, 71, 58.])
DEEP, SEA, BEACH, RIVER, SWAMP, PLAINS, FOREST, HIGH, DRY = range(9)
N, PX, SEA_LEVEL = 128, 256, 63

def survey(seed, R):
    span = 2 * R
    xs = np.linspace(-span, span, N)
    X, Z = np.meshgrid(xs, xs, indexing="xy")
    v = ip.fake_vanilla(N, 2 * span, seed)
    ang = (seed * 2.399963) % (2 * math.pi)
    n1 = ip.own_noise(X, Z, R, seed, 0.8); n2 = ip.own_noise(X, Z, R, seed + 1, 0.22)
    c = ip.shape(X, Z, v, R, ang, n1, n2)
    rng = np.random.default_rng(seed)
    t = ip.value_noise(N, 6, rng); w = ip.value_noise(N, 5, rng)
    h = np.where(c > -0.11, 64 + (c + 0.11) * 70 + t * 6, 63 + c * 40)
    k = np.full((N, N), PLAINS)
    k[c < -0.11] = SEA; k[c < -0.455] = DEEP
    land = c >= -0.11
    k[land & (c < -0.06)] = BEACH
    k[land & (c >= -0.06) & (t > 0.15)] = FOREST
    k[land & (c >= -0.06) & (w > 0.3)] = DRY
    k[land & (c >= -0.06) & (w < -0.35)] = SWAMP
    k[land & (c > 0.35)] = HIGH
    return h, k

def draw(h, k):
    sc = PX // N
    def H(u, v):
        u = np.clip(u, 0, N - 1.001); v = np.clip(v, 0, N - 1.001)
        i = u.astype(int); j = v.astype(int); a = u - i; b = v - j
        g = lambda ii, jj: h[np.clip(jj, 0, N - 1), np.clip(ii, 0, N - 1)]
        return (g(i, j) * (1 - a) + g(i + 1, j) * a) * (1 - b) + (g(i, j + 1) * (1 - a) + g(i + 1, j + 1) * a) * b
    py, px = np.mgrid[0:PX, 0:PX]
    u = (px + 0.5) / sc - 0.5; v = (py + 0.5) / sc - 0.5
    kk = k[np.clip(np.round(v).astype(int), 0, N - 1), np.clip(np.round(u).astype(int), 0, N - 1)]
    wet = (H(u, v) < SEA_LEVEL - 0.5) & ((kk == DEEP) | (kk == SEA))
    far = PX * 2
    edge = np.zeros_like(wet)
    edge[:, 1:] |= wet[:, 1:] != wet[:, :-1]; edge[:, :-1] |= wet[:, :-1] != wet[:, 1:]
    edge[1:] |= wet[1:] != wet[:-1]; edge[:-1] |= wet[:-1] != wet[1:]
    d = np.where(edge, 3, far * 4).astype(int)
    for y in range(PX):
        for x in range(PX):
            for dx_, dy_, c_ in ((-1, 0, 3), (0, -1, 3), (-1, -1, 4), (1, -1, 4)):
                nx, ny = x + dx_, y + dy_
                if 0 <= nx < PX and 0 <= ny < PX and wet[ny, nx] == wet[y, x]: d[y, x] = min(d[y, x], d[ny, nx] + c_)
    for y in range(PX - 1, -1, -1):
        for x in range(PX - 1, -1, -1):
            for dx_, dy_, c_ in ((1, 0, 3), (0, 1, 3), (1, 1, 4), (-1, 1, 4)):
                nx, ny = x + dx_, y + dy_
                if 0 <= nx < PX and 0 <= ny < PX and wet[ny, nx] == wet[y, x]: d[y, x] = min(d[y, x], d[ny, nx] + c_)
    d = (d + 1) // 3
    mix = lambda a, b, t: a * (1 - t) + b * t
    out = np.zeros((PX, PX, 3))
    sea = mix(PAPER, PAPER_DARK, np.where(kk == DEEP, 0.9, 0.6)[..., None])
    rip = np.select([d == 3, d == 7, d == 12], [0.55, 0.35, 0.2], 0.0)[..., None]
    sea = mix(sea, INK_SOFT, rip)
    dx = H(u + 0.5, v) - H(u - 0.5, v); dz = H(u, v + 0.5) - H(u, v - 0.5)
    shade = np.clip(0.5 + (dx + dz) * 0.06, 0, 1)[..., None]
    land = mix(PAPER, INK_SOFT, shade * 0.7)
    cx = (px + (py // 6 % 2) * 3) % 6; cy = py % 6
    tree = ((cx == 2) & (cy <= 2)) | ((cy == 1) & (cx >= 1) & (cx <= 3))
    m = np.zeros((PX, PX)); col = np.tile(INK, (PX, PX, 1)).astype(float)
    land = np.where(((kk == FOREST) & tree)[..., None], mix(land, INK, 0.6), land)
    land = np.where(((kk == SWAMP) & (cy == 3) & (cx <= 2))[..., None], mix(land, INK_SOFT, 0.7), land)
    land = np.where(((kk == DRY) & (cx == 1) & (cy == 1) & ((px * 7 + py * 13) % 3 == 0))[..., None], mix(land, INK_SOFT, 0.7), land)
    land = np.where((kk == RIVER)[..., None], mix(land, INK_SOFT, 0.5), land)
    land = np.where((kk == BEACH)[..., None], mix(land, PAPER, 0.5), land)
    land = np.where(((kk == HIGH) & (cy == 2) & (cx == 3))[..., None], mix(land, INK, 0.5), land)
    out = np.where(wet[..., None], sea, np.where((d == 1)[..., None], INK, land))
    return Image.fromarray(out.astype(np.uint8))

if __name__ == "__main__":
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    R = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
    img = draw(*survey(seed, R))
    img.save(sys.argv[1]); print("ok")
