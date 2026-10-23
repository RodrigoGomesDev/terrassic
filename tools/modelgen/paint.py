"""
Procedural texture painter.

Blockbench gives us, for every cube face, the 4 corner vertices with their UV
and their position in the model.  For every texel of the texture we therefore
know *where on the animal* it lands, and we can paint with 3D functions
(countershading, stripes, scales, eyes...).  Patterns stay continuous across
cubes, which is what makes the result look like one animal and not a pile of
boxes.
"""
import math
import numpy as np
from PIL import Image


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def mix(a, b, t):
    t = min(1.0, max(0.0, t))
    return a * (1 - t) + b * t


def smooth(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def hash3(x, y, z, seed=0):
    n = (int(x) * 73856093) ^ (int(y) * 19349663) ^ (int(z) * 83492791) ^ (seed * 2654435761)
    n &= 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def vnoise(x, y, z, seed=0):
    """Smooth 3D value noise in [0,1]."""
    xi, yi, zi = math.floor(x), math.floor(y), math.floor(z)
    xf, yf, zf = x - xi, y - yi, z - zi
    u, v, w = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf), zf * zf * (3 - 2 * zf)
    def h(a, b, c):
        return hash3(xi + a, yi + b, zi + c, seed)
    x00 = h(0, 0, 0) * (1 - u) + h(1, 0, 0) * u
    x10 = h(0, 1, 0) * (1 - u) + h(1, 1, 0) * u
    x01 = h(0, 0, 1) * (1 - u) + h(1, 0, 1) * u
    x11 = h(0, 1, 1) * (1 - u) + h(1, 1, 1) * u
    y0 = x00 * (1 - v) + x10 * v
    y1 = x01 * (1 - v) + x11 * v
    return y0 * (1 - w) + y1 * w


class Texel:
    """Everything the shader gets to know about one texel."""
    __slots__ = ("P", "W", "N", "face", "cube", "ci", "s", "t", "i", "j", "edge", "cy", "row", "rows", "col", "cols")


def face_geometry(verts):
    uvs = np.array([v["uv"] for v in verts])
    u0, u1 = int(round(uvs[:, 0].min())), int(round(uvs[:, 0].max()))
    v0, v1 = int(round(uvs[:, 1].min())), int(round(uvs[:, 1].max()))
    corner = {}
    for v in verts:
        s = 0 if abs(v["uv"][0] - u0) < abs(v["uv"][0] - u1) else 1
        t = 0 if abs(v["uv"][1] - v0) < abs(v["uv"][1] - v1) else 1
        corner[(s, t)] = v
    return u0, u1, v0, v1, corner


def bilerp(corner, key, s, t, add=None):
    a = np.array(corner[(0, 0)][key]); b = np.array(corner[(1, 0)][key])
    c = np.array(corner[(0, 1)][key]); d = np.array(corner[(1, 1)][key])
    p = (a * (1 - s) + b * s) * (1 - t) + (c * (1 - s) + d * s) * t
    if add is not None:
        p = p + add
    return p


def paint_model(model, dump, shader):
    W, H = model.tex_w, model.tex_h
    img = np.zeros((H, W, 4), dtype=float)
    assert len(dump) == len(model.cubes), (len(dump), len(model.cubes))
    for ci, (cube, d) in enumerate(zip(model.cubes, dump)):
        verts = d["verts"]
        order = d["order"]
        origin = np.array(cube.origin, dtype=float)
        wall = np.array([v["w"] for v in verts])
        wcenter = wall.mean(axis=0)
        uall = np.array([v["l"] for v in verts]) + origin
        ucenter = uall.mean(axis=0)
        for fi, face in enumerate(order):
            fv = verts[4 * fi: 4 * fi + 4]
            u0, u1, v0, v1, corner = face_geometry(fv)
            if len(corner) < 4 or u1 == u0 or v1 == v0:
                continue
            # normals (unposed + world), oriented outwards
            pu = [np.array(v["l"]) + origin for v in fv]
            pw = [np.array(v["w"]) for v in fv]
            def normal(pts, center):
                n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
                if np.linalg.norm(n) < 1e-9:
                    n = np.cross(pts[3] - pts[0], pts[2] - pts[0])
                n = n / (np.linalg.norm(n) + 1e-9)
                fc = sum(pts) / 4
                if np.dot(n, fc - center) < 0:
                    n = -n
                return n
            Nu = normal(pu, ucenter)
            Nw = normal(pw, wcenter)
            cols, rows = u1 - u0, v1 - v0
            for j in range(v0, v1):
                for i in range(u0, u1):
                    if not (0 <= i < W and 0 <= j < H):
                        continue
                    s = (i + 0.5 - u0) / cols
                    t = (j + 0.5 - v0) / rows
                    tx = Texel()
                    tx.P = bilerp(corner, "l", s, t, origin)
                    tx.W = bilerp(corner, "w", s, t)
                    tx.N = Nu
                    tx.face = face
                    tx.cube = cube
                    tx.ci = ci
                    tx.s, tx.t, tx.i, tx.j = s, t, i, j
                    tx.col, tx.row = i - u0, j - v0
                    tx.cols, tx.rows = cols, rows
                    tx.edge = (i == u0 or i == u1 - 1 or j == v0 or j == v1 - 1)
                    # vertical position inside the cube (unposed), 0 bottom .. 1 top
                    y0, y1 = cube.frm[1], cube.to[1]
                    tx.cy = (tx.P[1] - y0) / max(1e-6, (y1 - y0))
                    rgb = shader(model, tx)
                    img[j, i, :3] = np.clip(rgb, 0, 255)
                    img[j, i, 3] = 255
    return Image.fromarray(img.astype(np.uint8), "RGBA")


# ----------------------------------------------------------------- default shader
def make_shader(pal, pattern=None, decals=None, noise=1.0):
    """
    pal: dict of hex colours. Required keys: dorsal, flank, belly, limb, claw.
    pattern(model, tx, rgb, region) -> rgb  (optional species specific layer)
    decals: list of dict(kind, bones, pos, r, side)
    """
    P = {k: hex2rgb(v) for k, v in pal.items()}
    decals = decals or []

    def countershade(tx, top, mid, bot):
        f = tx.face
        if f == "up":
            return top.copy(), "dorsal"
        if f == "down":
            return bot.copy(), "belly"
        y = tx.cy
        if y > 0.62:
            return mix(mid, top, smooth(0.62, 0.95, y)), "dorsal"
        if y < 0.42:
            return mix(bot, mid, smooth(0.08, 0.42, y)), "belly"
        return mid.copy(), "flank"

    def shader(model, tx):
        cube = tx.cube
        tag = cube.tag
        paint = cube.paint
        region = tag
        face_override = paint.get("faces", {}).get(tx.face)
        if face_override:
            tag = face_override
        if tag == "skin":
            rgb, region = countershade(tx, P["dorsal"], P["flank"], P["belly"])
        elif tag == "limb":
            top = P.get("limb_top", P["limb"])
            rgb = mix(P["limb"], top, smooth(0.2, 1.0, tx.cy))
            if tx.face == "down":
                rgb = P["limb"] * 0.8
            region = "limb"
        elif tag in ("horn", "spike", "claw", "tooth_cube"):
            base = P.get(tag + "_base", P.get("claw"))
            tip = P.get(tag + "_tip", base)
            axis = paint.get("axis", "-z")
            k = "xyz".index(axis[1])
            lo, hi = cube.frm[k], cube.to[k]
            g = (tx.P[k] - lo) / max(1e-6, hi - lo)
            if axis[0] == "-":
                g = 1 - g
            rgb = mix(base, tip, smooth(0.15, 0.95, g))
        elif tag in P:
            rgb = P[tag].copy()
            if tx.face == "down":
                rgb = rgb * 0.85
        else:
            rgb = P["flank"].copy()

        # species pattern
        if pattern is not None:
            rgb = pattern(model, tx, rgb, region)

        # teeth along an edge of the face
        teeth = paint.get("teeth")
        if teeth and tx.face in teeth.get("faces", ("east", "west", "north")):
            row = tx.rows - 1 - tx.row if teeth["edge"] == "bottom" else tx.row
            if row < teeth.get("rows", 1):
                coord = tx.P[2] if tx.face in ("east", "west") else tx.P[0]
                if int(math.floor(coord * teeth.get("freq", 1.0))) % 2 == 0:
                    rgb = P["tooth"].copy()
                else:
                    rgb = P.get("gum", P["mouth"]).copy()

        # decals (eyes, nostrils, markings)
        for d in decals:
            if cube.bone not in d["bones"]:
                continue
            side = d.get("side", 0)
            if side and tx.N[0] * side < 0.5:
                continue
            if d.get("face") and tx.face != d["face"]:
                continue
            c = d["pos"]
            dy = tx.P[1] - c[1]
            dz = tx.P[2] - c[2]
            dx = tx.P[0] - c[0]
            kind = d["kind"]
            r = d.get("r", 1.0)
            if kind == "eye":
                if abs(dy) <= r and abs(dz) <= r and abs(dx) <= 1.2:
                    rgb = P["eye"].copy()
                    if r >= 1.5:
                        if abs(dz) < 0.51:
                            rgb = P["pupil"].copy()
                        if dy > r - 1.0 and dz < -(r - 1.0):
                            rgb = mix(P["eye"], np.array([255, 255, 255.0]), 0.35)
                    else:
                        if dz < 0 and dy < 0:
                            rgb = P["pupil"].copy()
                        elif dz < 0 and dy > 0:
                            rgb = mix(P["eye"], np.array([255, 255, 255.0]), 0.6)
                elif d.get("ring", True) and abs(dx) <= 1.2 and abs(dz) <= r + 1.0 and r < dy <= r + 1.0:
                    rgb = rgb * 0.55   # brow shadow above the eye
                elif d.get("ring", True) and abs(dx) <= 1.2 and abs(dy) <= r and r < -dz <= r + 1.0:
                    rgb = rgb * 0.75   # tear duct / front corner
            elif kind == "spot":
                if abs(dy) <= r and abs(dz) <= r and abs(dx) <= d.get("rx", r):
                    rgb = P[d["color"]].copy() if d.get("color") else rgb * d.get("mul", 0.5)
            elif kind == "band_y":  # horizontal band (e.g. mouth line) between y bounds
                if c[1] - r <= tx.P[1] <= c[1] + r and (d.get("zmin", -1e9) <= tx.P[2] <= d.get("zmax", 1e9)):
                    rgb = P[d["color"]].copy() if d.get("color") else rgb * d.get("mul", 0.5)

        # subtle scale noise + edge occlusion
        if noise:
            n1 = hash3(tx.i, tx.j, tx.ci, 7) - 0.5
            n2 = vnoise(tx.P[0] / 2.2, tx.P[1] / 2.2, tx.P[2] / 2.2, 3) - 0.5
            rgb = rgb * (1 + noise * (0.07 * n1 + 0.10 * n2))
        if tx.edge and tag not in ("eye",):
            rgb = rgb * 0.93
        # gentle top lighting baked in (Cobblemon-ish soft volume)
        if tx.face == "down":
            rgb = rgb * 0.9
        return rgb

    return shader
