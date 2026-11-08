"""The 1.10.1 skin standard (docs/estudos/14_POR_QUE_PARECE_IA.md, decisions of 07/11/2026).

What it fixes in skin.py, without taking away the drawn details that give each animal its character:
- every pattern is laid in BODY space (tx.P, the rest-pose position of the texel), not in each face's own frame, so
  scales, blotches and marks run on from one cube to the next instead of starting over at every edge;
- the tones come from the whole silhouette (dorsal, flank, belly measured on the body's profile at that point along
  its length), so countershading is one continuous shape and never a band per cube;
- the base is calm: big soft blotches of one tone step and a few flecks; scales only where the anatomy has them
  (osteoderms, feet, the face), never the same Voronoi stamped from snout to tail;
- one pixel = one Minecraft pixel in game: models are drawn at PX_PER_M and placed at scale ~1 (density()).

Style reference (Rodrigo): Alex's Mobs and Raxiores' mods; not the extreme Voronoi of other dinosaur mods.
"""
import math
import numpy as np
import geo
from proto import h32

METRE = 1.059                     # blocks per metre (gen_species.METRE: the player is a 1.70 m person)
PX_PER_M = 16.0 * METRE          # draw at this many model pixels per metre: 16 texels per block in game


def density(model_px_length, metres, model_scale=None):
    """texels per block in game for a rig model_px_length pixels long shown at the real size in metres"""
    scale = model_scale if model_scale is not None else metres * METRE * 16.0 / model_px_length
    return 16.0 / scale


# ------------------------------------------------------------------ body space
def surface_uv(t):
    """continuous 2D coordinates of a texel on the body surface, in model pixels: the same point on two touching
    cubes gets the same coordinates, so a pattern does not restart at the seam"""
    P = t.P
    if t.face in ("east", "west"):
        return P[2], P[1]
    if t.face in ("north", "south"):
        return P[0], P[1]
    return P[0], P[2]


class Profile:
    """top and bottom of the body along its length (z), measured on the rest pose of the named parts"""

    def __init__(self, m, parts, smooth=3):
        tops, bots = {}, {}
        for c, pts in geo.cube_points(m.spec()):
            if c["name"] not in parts and c["bone"] not in parts:
                continue
            z0, z1 = int(math.floor(pts[:, 2].min())), int(math.ceil(pts[:, 2].max()))
            for z in range(z0, z1 + 1):
                tops[z] = max(tops.get(z, -1e9), pts[:, 1].max())
                bots[z] = min(bots.get(z, 1e9), pts[:, 1].min())
        self.z0, self.z1 = min(tops), max(tops)
        zs = np.arange(self.z0, self.z1 + 1)
        top = np.array([tops.get(z, np.nan) for z in zs], float)
        bot = np.array([bots.get(z, np.nan) for z in zs], float)
        for a in (top, bot):           # fill gaps, then a running mean so the line follows the body, not the cubes
            idx = np.arange(len(a)); ok = ~np.isnan(a)
            a[:] = np.interp(idx, idx[ok], a[ok])
        k = np.ones(2 * smooth + 1) / (2 * smooth + 1)
        self.top = np.convolve(np.pad(top, smooth, mode="edge"), k, "valid")
        self.bot = np.convolve(np.pad(bot, smooth, mode="edge"), k, "valid")

    def at(self, z):
        i = int(min(max(round(z) - self.z0, 0), len(self.top) - 1))
        return self.bot[i], self.top[i]

    def height(self, t):
        """0 at the belly line, 1 along the spine, at this point of the body's length"""
        lo, hi = self.at(t.P[2])
        return float(min(1.0, max(0.0, (t.P[1] - lo) / max(1.0, hi - lo))))


# ------------------------------------------------------------------ smooth fields (no per-texel noise)
def soft(x, y, cell, seed=0):
    """smooth value noise in 0..1 with features about `cell` pixels wide"""
    gx, gy = x / cell, y / cell
    ix, iy = math.floor(gx), math.floor(gy)
    fx, fy = gx - ix, gy - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    v = lambda a, b: (h32(a, b, seed, 41) % 1000) / 999.0
    top = v(ix, iy) * (1 - fx) + v(ix + 1, iy) * fx
    bot = v(ix, iy + 1) * (1 - fx) + v(ix + 1, iy + 1) * fx
    return top * (1 - fy) + bot * fy


def wobble(z, amp=0.05, seed=0):
    """a slow wander along the body for tone borders (never parallel to a cube edge)"""
    return amp * (math.sin(z * 0.15 + seed) * 0.6 + math.sin(z * 0.37 + 2 * seed + 1.3) * 0.4)


# ------------------------------------------------------------------ the calm base
def bands(h, z, limits, amp=0.05, seed=0):
    """index of the tone band for body height h (0 belly .. 1 spine); limits ascending, e.g. (0.22, 0.30, 0.55, 0.8)
    -> 0 belly, 1 belly edge, 2 lower flank, 3 upper flank, 4 back"""
    hh = h + wobble(z, amp, seed)
    for i, lim in enumerate(limits):
        if hh < lim:
            return i
    return len(limits)


def mottle(t, cell=11.0, strength=0.16, seed=0):
    """-1, 0 or +1 tone step: big soft blotches in body space (one step only, never a pixel salt)"""
    u, v = surface_uv(t)
    n = soft(u, v, cell, seed) - 0.5
    return -1 if n < -strength else (1 if n > strength + 0.1 else 0)


def fleck(t, every=23, seed=0):
    """a lone darker pixel now and then, spaced like blue noise (never two touching)"""
    u, v = surface_uv(t)
    iu, iv = math.floor(u), math.floor(v)
    if (iu + 2 * iv) % 3:
        return False
    return h32(iu, iv, seed, 7) % every == 0


def scales(t, cell=4.0, seed=0, flat=0.9):
    """scales in body space, for the parts that have them (face, feet, osteoderms): 'edge' on the seam of the
    shaded side, otherwise 'base'. No lit corner (the game already lights the top faces)."""
    u, v = surface_uv(t)
    uc, vc = math.floor(u) + 0.5, math.floor(v) + 0.5
    gx, gy = math.floor(uc / cell), math.floor(vc / cell)
    best = [(1e9, None), (1e9, None)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            cx, cy = gx + dx, gy + dy
            px = (cx + 0.15 + 0.7 * (h32(cx, cy, seed, 1) % 1000) / 1000) * cell
            py = (cy + 0.15 + 0.7 * (h32(cx, cy, seed, 2) % 1000) / 1000) * cell
            d = math.hypot(uc - px, (vc - py) * 1.15)
            if d < best[0][0]:
                best = [(d, (px, py)), best[0]]
            elif d < best[1][0]:
                best[1] = (d, (px, py))
    (d1, (px, py)), (d2, _) = best
    if d2 - d1 < flat and (uc - px > -0.5 or vc - py < 0.5):
        return "edge"
    return "base"


def stripe(z, y, centres, half, slant=0.0, wander=1.2, seed=0):
    """inside a drawn band across the body (a stripe or a saddle)? centres: z of each band; half: half width;
    slant: z shift per pixel of height; the border wanders slowly so it reads drawn, not cut"""
    for k, zc in enumerate(centres):
        edge = half + wander * math.sin(y * 0.45 + k * 1.7 + seed)
        if abs(z - (zc + slant * y)) < edge:
            return k
    return None


STEP_DN = {"k5": "k4", "k4": "k3", "k3": "k2", "k2": "k1", "k1": "k0", "k0": "k0",
           "b3": "b2", "b2": "b1", "b1": "b0", "b0": "k4"}
STEP_UP = {v: k for k, v in STEP_DN.items() if k != v}
STEP_UP.update({"k5": "k5", "b3": "b3"})


def step(key, d):
    """move a palette key d tone steps (negative = darker) along the k0..k5 / b0..b3 ramps"""
    while d < 0:
        key = STEP_DN[key]; d += 1
    while d > 0:
        key = STEP_UP.get(key, key); d -= 1
    return key


def colour_count(img):
    a = np.asarray(img.convert("RGBA")).reshape(-1, 4)
    a = a[a[:, 3] > 0]
    return len({tuple(x) for x in a[:, :3]})
