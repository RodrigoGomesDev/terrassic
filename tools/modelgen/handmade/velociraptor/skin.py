"""Structured hand-pixel skin helpers (no noise): voronoi scales with outline + highlight, belly scute rows,
muscle contour rings, tapered stripes with a warm rim. Everything is drawn on integer texel coordinates."""
import math
from proto import h32

def face_uv_coords(t):
    """2D integer coordinates of a texel in its cube's local frame, oriented per face (u right, v up)."""
    L = t.L; f = t.face
    if f in ("east", "west"): return L[2], L[1]
    if f in ("north", "south"): return L[0], L[1]
    return L[0], L[2]

def voronoi(u, v, cell=4.5, seed=0):
    """returns (d1, d2, cell_id): distances to the nearest and second nearest jittered seed"""
    gx, gy = math.floor(u / cell), math.floor(v / cell)
    best = [(1e9, None), (1e9, None)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            cx, cy = gx + dx, gy + dy
            px = (cx + 0.15 + 0.7 * (h32(cx, cy, seed, 1) % 1000) / 1000) * cell
            py = (cy + 0.15 + 0.7 * (h32(cx, cy, seed, 2) % 1000) / 1000) * cell
            d = math.hypot(u - px, (v - py) * 1.15)
            if d < best[0][0]: best = [(d, (cx, cy, px, py)), best[0]]
            elif d < best[1][0]: best[1] = (d, (cx, cy, px, py))
    return best[0][0], best[1][0], best[0][1]

def scales(u, v, cell=4.5, seed=0):
    """'edge' | 'hi' | 'lo' | 'base' | 'alt' for a pixel-art reptile scale field"""
    uc, vc = math.floor(u) + 0.5, math.floor(v) + 0.5
    d1, d2, c = voronoi(uc, vc, cell, seed)
    cx, cy, px, py = c
    if d2 - d1 < 0.9:
        # raised scales: only the lower-right side of a scale casts a dark seam
        return "edge" if (uc - px > -0.5 or vc - py < 0.5) else "base"
    # highlight: upper-left inside the scale; shade: lower-right
    if uc - px < -0.6 and vc - py > 0.4 and d1 < cell * 0.45: return "hi"
    if uc - px > 0.6 and vc - py < -0.6: return "lo"
    return "alt" if h32(cx, cy, seed, 9) % 4 == 0 else "base"

def scutes(u, v, row=3, width=7):
    """belly scute rows: highlight top row, dark seam bottom row, staggered vertical seams"""
    r = math.floor(v / row); k = math.floor(v) - r * row
    off = (r % 2) * (width // 2)
    c = (math.floor(u) + off) % width
    if k == 0: return "seam"
    if c == 0 and k == 1: return "seam"
    if k == row - 1 and c in (1, 2): return "hi"
    return "base"

def ring(u, v, cx, cy, rx, ry):
    """position relative to an elliptical contour: 'line' on the ring, 'hi' just inside upper-left, 'in', 'out'"""
    d = math.hypot((u - cx) / rx, (v - cy) / ry)
    if abs(d - 1) * min(rx, ry) < 0.55: return "line"
    if d < 1 and (u - cx) < 0 and (v - cy) > 0 and abs(d - 0.8) * min(rx, ry) < 0.5: return "hi"
    return "in" if d < 1 else "out"
