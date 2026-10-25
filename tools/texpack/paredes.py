"""Walls and roofs of the mod in the calm style (approved 25/10, see chao.py): plasters and daub as a fine low-contrast grain like
packed mud, rammed earth in lifts, timber frames lit on one edge, thatch as fine straw with two ties per block."""
import numpy as np
import chao as C
import madeira as MD
N = 16
def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def grain(seed, rgb, ctr, w=(1, 3, 4, 4, 3, 1), clump=.6, sat=.45, macro=2.8, hue=.01):
    idx = C.levels(C.field(seed, clump), list(w))
    pal = C.ramp(rgb, len(w), ctr, hue_dark=hue)
    return C.calm(idx, pal, macro, seed=seed), pal
def strokes(idx, pal, r, count, length, k, horizontal=True):
    """Short trowel strokes (or straw flecks): k steps lighter (k>0) or darker along a few pixels."""
    for _ in range(count):
        y, x = r.integers(N, size=2)
        for i in range(int(r.integers(*length))):
            yy, xx = (y, (x + i) % N) if horizontal else ((y + i) % N, x)
            idx[yy, xx] = C.shade(pal, idx[yy, xx], k)
    return idx
PLASTERS = {"clay_plaster": "#a38868", "red_ochre_plaster": "#8e3f28", "yellow_ochre_plaster": "#b88b3a",
            "charcoal_plaster": "#33302d", "chalk_whitewash": "#dcd8ce"}
def plaster(pid, seed):
    rgb = hexrgb(PLASTERS[pid]); r = np.random.default_rng(seed)
    idx, pal = grain(seed, rgb, 22 if pid != "chalk_whitewash" else 16)
    idx = strokes(idx, pal, r, 5, (3, 6), 1)
    hue_to = {"red_ochre_plaster": 14, "clay_plaster": 26}.get(pid)
    return C.paint(idx, C.calm_pal(pal, {"red_ochre_plaster": .48, "yellow_ochre_plaster": .50}.get(pid, .42), hue_to, pull=.25))
DAUB = (149, 123, 92)
STRAW = (160, 140, 96)
def daub_idx(seed):
    r = np.random.default_rng(seed)
    idx, pal = grain(seed, DAUB, 30, macro=3.0)
    k = len(pal); pal = pal + [STRAW]
    for _ in range(9):   # chopped straw in the clay
        y, x = r.integers(N, size=2); d = [(0, 1), (1, 1), (1, 0), (1, -1)][int(r.integers(4))]
        for i in range(2): idx[(y + i * d[0]) % N, (x + i * d[1]) % N] = k
    return idx, C.calm_pal(pal, .38)
def wattle_and_daub():
    idx, pal = daub_idx(740)
    return C.paint(idx, pal)
def framed(kind):
    import blocos as BL
    b = BL.beams(kind)
    idx, pal = daub_idx(720 + len(kind))
    timber = C.calm_pal(C.ramp((94, 69, 44), 4, 40), .42)
    k = len(pal); pal = pal + timber
    f = MD.streaks(730 + len(kind), True, 4, .6)
    tb = np.clip(1 + np.round(f * .6).astype(int), 0, 2)
    lit = b & (~np.roll(b, 1, 0) | ~np.roll(b, 1, 1))
    dark = b & (~np.roll(b, -1, 0) | ~np.roll(b, -1, 1))
    tb = np.where(lit & ~dark, 3, np.where(dark & ~lit, 0, tb))
    shadow = ~b & (np.roll(b, 1, 0) | np.roll(b, 1, 1))
    idx = np.where(shadow, C.shade(pal[:k], idx, -2), idx)
    idx = np.where(b, k + tb, idx)
    return C.paint(idx, pal)
def whitewashed():
    r = np.random.default_rng(743)
    wi, wp = grain(742, hexrgb(PLASTERS["chalk_whitewash"]), 16)
    di, dp = daub_idx(744)
    dp = [tuple(int(.55 * v + .45 * w) for v, w in zip(p, (220, 216, 206))) for p in dp]   # daub still stained with lime
    c = r.normal(size=(N, N))
    for _ in range(2): c = C.blur(c, 1)
    worn = c > np.quantile(c, .93)   # 7% worn through to the daub
    k = len(wp)
    idx = np.where(worn, k + di, wi)
    edge = ~worn & (np.roll(worn, -1, 0))  # the whitewash lip just above a worn patch
    idx = np.where(edge, C.shade(wp, wi, -1), idx)
    return C.paint(idx, C.calm_pal(wp, .1) + dp)
EARTH = (115, 87, 61)
def rammed_earth():
    r = np.random.default_rng(760)
    idx, pal = grain(760, EARTH, 40, macro=3.2)
    J = len(pal); pal = pal + [tuple(int(v * .86) for v in pal[0])]
    lifts = [0, 4, 7, 12, 16]
    for i in range(4):
        y0, y1 = lifts[i], lifts[i + 1]
        idx[y0:y1 - 1] = C.shade(pal[:J], idx[y0:y1 - 1], (0, 1, -1, 1)[i])
        idx[y1 - 1, :] = np.where(r.random(N) < .8, J, idx[y1 - 1, :])
    k = len(pal); pal = pal + [(112, 100, 86), (132, 120, 104)]
    for _ in range(2):
        y, x = r.integers(N, size=2); idx[y, x] = k + 1; idx[(y + 1) % N, x] = k
    return C.paint(idx, C.calm_pal(pal, .42))
THATCH = {"thatch": "#a08848", "reed_thatch": "#8a7e45", "fern_thatch": "#715628", "cycad_thatch": "#55632e"}
def thatch_side(name, seed):
    rgb = hexrgb(THATCH[name]); r = np.random.default_rng(seed)
    f = MD.streaks(seed, True, 6, .85)
    if name in ("fern_thatch", "cycad_thatch"):   # fronds hang as slanted leaflets, not straight straws
        f = .6 * f + .6 * np.array([[np.sin((x + y * (1 if (y // 4) % 2 else -1)) * 1.4) for x in range(N)] for y in range(N)])
    idx = C.levels(f, [1, 2, 4, 4, 3, 2])
    pal = C.ramp(rgb, 6, 50, hue_dark=.02)
    J = len(pal); pal = pal + [tuple(int(v * .8) for v in pal[0])]
    for ty in (6, 14):   # two ties: the cord, its shadow under, the straw bulging lit above
        idx[ty, :] = J
        idx[(ty + 1) % N, :] = C.shade(pal[:J], idx[(ty + 1) % N, :], -2)
        idx[ty - 1, :] = C.shade(pal[:J], idx[ty - 1, :], 1)
    return C.paint(idx, C.calm_pal(pal, .40, hue_to=40, pull=.2))
def thatch_top(name, seed):
    rgb = hexrgb(THATCH[name])
    f = MD.streaks(seed, True, 4, .7) + MD.streaks(seed + 1, False, 4, .7)
    idx = C.levels(f, [1, 2, 4, 4, 3, 2])
    pal = C.ramp(rgb, 6, 46, hue_dark=.02)
    return C.paint(C.calm(idx, pal, 3.5, seed=seed), C.calm_pal(pal, .40, hue_to=40, pull=.2))
def recolour(img, sat):
    """Calm an existing woven texture: same drawing, saturation down to sat."""
    a = np.array(img.convert("RGBA")); cols = sorted({tuple(c) for c in a[..., :3].reshape(-1, 3)})
    new = dict(zip(cols, C.calm_pal(cols, sat)))
    out = a.copy()
    for y in range(N):
        for x in range(N): out[y, x, :3] = new[tuple(a[y, x, :3])]
    from PIL import Image
    return Image.fromarray(out, "RGBA")
def thatch():
    out = {}
    for i, n in enumerate(THATCH):
        out[n] = thatch_side(n, 701 + 2 * i)
        out[f"{n}_top"] = thatch_top(n, 702 + 2 * i)
    return out


def earth():
    out = {pid: plaster(pid, 750 + i) for i, pid in enumerate(PLASTERS)}
    out["wattle_and_daub"] = wattle_and_daub()
    out["cross_braced_wattle"] = framed("cross")
    out["timber_framed_wattle"] = framed("frame")
    out["whitewashed_wattle"] = whitewashed()
    out["rammed_earth"] = rammed_earth()
    return out
