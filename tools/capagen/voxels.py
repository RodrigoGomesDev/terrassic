"""
Block scenery for the cover and the title screen: original 16x16 block textures, a voxel world (terrain, water,
trees, plants) meshed into quads for gl.py, and the mod's dinosaur models placed in it at real scale
(1 block = 1 metre).
"""
import math

import numpy as np
from PIL import Image

import gl
from pixel import hexrgb, noise1d, noise2d

T = 16  # texture size of a block face


# ------------------------------------------------------------------ block textures (all drawn here, by code)
def _tile(rng, base, var=0.08, speck=None, speck_p=0.0):
    a = np.ones((T, T, 3)) * hexrgb(base)
    n = rng.normal(0, 1, (T, T))
    a *= (1 + n[..., None] * var)
    if speck:
        m = rng.random((T, T)) < speck_p
        a[m] = hexrgb(speck) * (1 + rng.normal(0, 0.05, (m.sum(), 1)))
    return a


def _rgba(a, alpha=None):
    al = np.full(a.shape[:2], 255.0) if alpha is None else alpha
    return np.dstack([np.clip(a, 0, 255), al]).astype(np.uint8)


def textures(seed=1):
    rng = np.random.default_rng(seed)
    t = {}
    # grass: Cretaceous ground cover was ferns and low plants, so a dense fern-green with darker fronds
    g = _tile(rng, "#5f8a3a", 0.10, "#3f6a2a", 0.22)
    blades = rng.random((T, T)) < 0.12
    g[blades] = hexrgb("#86ad4f")
    t["grass_top"] = _rgba(g)
    d = _tile(rng, "#7a5a3c", 0.10, "#5e4430", 0.25)
    pebble = rng.random((T, T)) < 0.05
    d[pebble] = hexrgb("#9b8a72")
    t["dirt"] = _rgba(d)
    side = d.copy()
    edge = 3 + (rng.random(T) * 3).astype(int)
    for x in range(T):
        side[:edge[x], x] = g[:edge[x], x]
        if rng.random() < 0.4:
            side[edge[x], x] = hexrgb("#4f7a33")
    t["grass_side"] = _rgba(side)
    s = _tile(rng, "#8a8580", 0.07, "#6f6a66", 0.20)
    for _ in range(3):  # strata cracks
        y = rng.integers(2, T - 2)
        x0 = rng.integers(0, T - 6)
        s[y, x0:x0 + rng.integers(3, 7)] *= 0.78
    t["stone"] = _rgba(s)
    t["sand"] = _rgba(_tile(rng, "#d8c48f", 0.05, "#c2ad78", 0.25))
    t["gravel"] = _rgba(_tile(rng, "#8e8378", 0.14, "#6c625a", 0.35))
    t["mud"] = _rgba(_tile(rng, "#5a4a3a", 0.08, "#4a3c2e", 0.3))
    # araucaria bark: vertical plates
    b = _tile(rng, "#6b4a33", 0.06)
    for x in range(T):
        if x % 4 == 0:
            b[:, x] *= 0.72
    for y in range(T):
        if y % 5 == 2:
            b[y, :] *= 0.85
    t["log"] = _rgba(b)
    lt = _tile(rng, "#a88459", 0.05)
    yy, xx = np.mgrid[0:T, 0:T]
    ring = (np.round(np.sqrt((xx - 7.5) ** 2 + (yy - 7.5) ** 2)) % 3 == 0)
    lt[ring] *= 0.85
    lt[(xx == 0) | (yy == 0) | (xx == T - 1) | (yy == T - 1)] = hexrgb("#6b4a33")
    t["log_top"] = _rgba(lt)
    # conifer leaves: dark needles with gaps
    lv = _tile(rng, "#2f5a34", 0.15, "#4c7a44", 0.2)
    holes = rng.random((T, T)) < 0.16
    t["leaves"] = _rgba(lv, np.where(holes, 0, 255.0))
    # fern (cross plant)
    f = np.zeros((T, T, 4))
    for k, ang in enumerate((-0.9, -0.45, 0.0, 0.45, 0.9)):
        for i in range(12):
            x = 7.5 + math.sin(ang) * i * 0.75
            y = 15 - i
            ix, iy = int(round(x)), int(y)
            if 0 <= ix < T and 0 <= iy < T:
                f[iy, ix] = list(hexrgb("#3f7a32")) + [255]
                for dx in (-1, 1):
                    if i % 2 == 0 and 0 <= ix + dx < T and i > 2:
                        f[iy, ix + dx] = list(hexrgb("#5d9a45")) + [255]
    t["fern"] = f.astype(np.uint8)
    # horsetail (cross plant)
    h = np.zeros((T, T, 4))
    for x in (3, 7, 11):
        top = rng.integers(2, 6)
        for y in range(top, T):
            h[y, x] = list(hexrgb("#6f8d3c" if y % 3 else "#3d4f22")) + [255]
    t["horsetail"] = h.astype(np.uint8)
    return t


MOD_TEXTURES = ["fern_litter", "fern_litter_side", "lateritic_soil", "cracked_mud", "limestone", "shale", "laterite",
                "peat", "needle_litter", "needle_litter_side", "mossy_limestone_stacked",
                "araucaria_log", "araucaria_log_top", "araucaria_leaves", "metasequoia_log", "metasequoia_log_top",
                "metasequoia_leaves", "sabal_log", "sabal_log_top", "sabal_leaves", "tree_fern_log", "tree_fern_log_top",
                "tree_fern_leaves", "podocarpus_leaves", "taxodium_log", "taxodium_log_top", "taxodium_leaves",
                "royal_fern", "horsetail", "bracken", "cretaceous_grass", "clubmoss", "cycad_top", "cycad_bottom",
                "tall_horsetail_top", "tall_horsetail_bottom", "tall_bracken_top", "tall_bracken_bottom", "chalk",
                "chalk_pebbles", "conglomerate"]


def mod_textures():
    """The mod's own block textures (assets/terrassic/textures/block), so the scenery matches the game."""
    import os
    from render3d import ROOT
    d = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "block")
    out = {}
    for n in MOD_TEXTURES:
        p = os.path.join(d, n + ".png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGBA")
            out[n] = np.asarray(im.crop((0, 0, T, T)))
    return out


def all_textures():
    t = textures()
    t.update(mod_textures())
    return t


def atlas(tex):
    names = list(tex)
    img = Image.new("RGBA", (T * len(names), T), (0, 0, 0, 0))
    uv = {}
    eps = 0.01
    for i, n in enumerate(names):
        img.paste(Image.fromarray(tex[n], "RGBA"), (i * T, 0))
        uv[n] = ((i * T + eps) / img.width, eps / T, ((i + 1) * T - eps) / img.width, (T - eps) / T)
    return img, uv


# ------------------------------------------------------------------ voxel world
# block -> (top, side, bottom) textures; mod textures where the mod has the block, procedural otherwise
BLOCKS = {
    "grass": ("grass_top", "grass_side", "dirt"), "dirt": ("dirt", "dirt", "dirt"), "stone": ("stone",) * 3,
    "sand": ("sand",) * 3, "gravel": ("gravel",) * 3, "mud": ("cracked_mud",) * 3, "log": ("log_top", "log", "log_top"),
    "litter": ("fern_litter", "fern_litter_side", "lateritic_soil"), "soil": ("lateritic_soil",) * 3,
    "needles": ("needle_litter", "needle_litter_side", "lateritic_soil"), "limestone": ("limestone",) * 3,
    "shale": ("shale",) * 3, "chalk": ("chalk",) * 3, "peat": ("peat",) * 3, "pebbles": ("chalk_pebbles",) * 3,
    "conglomerate": ("conglomerate",) * 3,
    "araucaria_log": ("araucaria_log_top", "araucaria_log", "araucaria_log_top"),
    "metasequoia_log": ("metasequoia_log_top", "metasequoia_log", "metasequoia_log_top"),
    "taxodium_log": ("taxodium_log_top", "taxodium_log", "taxodium_log_top"),
    "tree_fern_log": ("tree_fern_log_top", "tree_fern_log", "tree_fern_log_top"),
}
LEAVES = {"leaves", "araucaria_leaves", "metasequoia_leaves", "taxodium_leaves", "tree_fern_leaves",
          "podocarpus_leaves", "sabal_leaves"}
SOLID = set(BLOCKS)
FACES = {  # name: (normal, 4 corners as offsets, shade like Minecraft's face light)
    "up": ((0, 1, 0), [(0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)], 1.0),
    "down": ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)], 0.5),
    "north": ((0, 0, -1), [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)], 0.8),
    "south": ((0, 0, 1), [(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)], 0.8),
    "west": ((-1, 0, 0), [(0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)], 0.6),
    "east": ((1, 0, 0), [(1, 1, 1), (1, 1, 0), (1, 0, 0), (1, 0, 1)], 0.6),
}


def face_tex(block, face, uv=None):
    if block in BLOCKS:
        top, side, bottom = BLOCKS[block]
        name = top if face == "up" else bottom if face == "down" else side
    else:
        name = block
    if uv is not None and name not in uv:  # mod texture missing: fall back to a procedural one
        name = {"fern_litter": "grass_top", "fern_litter_side": "grass_side", "lateritic_soil": "dirt"}.get(name, "stone")
    return name


class World:
    def __init__(self):
        self.blocks = {}
        self.plants = []  # (x, y, z, texture, height)
        self.water = []  # (x0, z0, x1, z1, y)

    def set(self, x, y, z, b):
        self.blocks[(x, y, z)] = b

    def mesh(self, uv):
        out = []
        B = self.blocks
        for (x, y, z), b in B.items():
            for face, (n, corners, shade) in FACES.items():
                nb = B.get((x + n[0], y + n[1], z + n[2]))
                if nb is not None and (nb in SOLID or (nb == b and b in LEAVES)):
                    continue
                u0, v0, u1, v1 = uv[face_tex(b, face, uv)]
                cs = [(x + c[0], y + c[1], z + c[2]) for c in corners]
                out += gl.quad_verts(cs, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], n, shade)
        for (x, y, z, tex, hgt) in self.plants:
            parts = [(tex, y, hgt)]
            if tex + "_top" in uv and tex + "_bottom" in uv:  # two blocks tall
                parts = [(tex + "_bottom", y, hgt / 2), (tex + "_top", y + hgt / 2, hgt / 2)]
            for name, py, ph in parts:
                if name not in uv:
                    continue
                u0, v0, u1, v1 = uv[name]
                for (ax, az, bx, bz) in ((0.1, 0.1, 0.9, 0.9), (0.1, 0.9, 0.9, 0.1)):
                    cs = [(x + ax, py + ph, z + az), (x + bx, py + ph, z + bz), (x + bx, py, z + bz), (x + ax, py, z + az)]
                    out += gl.quad_verts(cs, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], (0, 1, 0), 0.9)
        return np.array(out, np.float32)

    def water_mesh(self):
        out = []
        for (x0, z0, x1, z1, y) in self.water:
            cs = [(x0, y, z1), (x1, y, z1), (x1, y, z0), (x0, y, z0)]
            out += gl.quad_verts(cs, [(0, 0), (1, 0), (1, 1), (0, 1)], (0, 1, 0))
        return np.array(out, np.float32)


def terrain(world, x0, z0, nx, nz, height_fn, sea=None, beach=1, top="grass", under="dirt", rock="stone",
            top_fn=None):
    """Fill columns from a height function; exposes cliffs down to the lowest neighbour."""
    H = np.array([[int(round(height_fn(x0 + i, z0 + k))) for k in range(nz)] for i in range(nx)])
    for i in range(nx):
        for k in range(nz):
            h = H[i, k]
            lo = min(H[max(i - 1, 0), k], H[min(i + 1, nx - 1), k], H[i, max(k - 1, 0)], H[i, min(k + 1, nz - 1)], h) - 1
            for y in range(lo, h + 1):
                if sea is not None and h <= sea + beach:
                    b = "sand" if y >= h - 2 else "stone"
                    if h < sea - 2:
                        b = "gravel" if y == h else "stone"
                else:
                    t = top_fn(x0 + i, z0 + k) if top_fn else top
                    b = t if y == h else (under if y >= h - 3 else rock)
                world.set(x0 + i, y, z0 + k, b)
    if sea is not None:
        world.water.append((x0, z0, x0 + nx, z0 + nz, sea + 0.9))
    return H


def fill(world, solid, origin, block_fn):
    """Put a boolean voxel volume (x, z, y) into the world, only its shell (the inside is never seen).
    block_fn(x, y, z, depth_below_air) -> block name."""
    s = solid
    air = ~s
    shell = np.zeros_like(s)
    for ax in range(3):
        for d in (1, -1):
            n = np.roll(air, d, axis=ax)
            edge = [slice(None)] * 3
            edge[ax] = 0 if d == 1 else -1
            n[tuple(edge)] = True
            shell |= n
    shell &= s
    # depth below the first air block above, for soil layers
    above = np.zeros(s.shape, int)
    run = np.zeros(s.shape[:2], int)
    for y in range(s.shape[2] - 1, -1, -1):
        run = np.where(s[:, :, y], run + 1, 0)
        above[:, :, y] = run
    x0, z0, y0 = origin
    for i, k, j in zip(*np.nonzero(shell)):
        world.set(x0 + int(i), y0 + int(j), z0 + int(k), block_fn(x0 + int(i), y0 + int(j), z0 + int(k), int(above[i, k, j]) - 1))


def araucaria(world, x, y, z, h, rng, log="araucaria_log", leaves="araucaria_leaves"):
    """Monkey-puzzle pine: tall bare trunk, a flat umbrella crown of tiered branch whorls."""
    for k in range(h):
        world.set(x, y + k, z, log)
    top = y + h
    for tier in range(3):
        r = 3 - tier + (1 if h > 14 else 0)
        ty = top - 2 + tier * 1
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r + 1 and rng.random() > 0.08:
                    world.set(x + dx, ty, z + dz, leaves)
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for s in range(1, r + 1):
                world.set(x + dx * s, ty - 1 + (1 if s == r else 0), z + dz * s, leaves)
    world.set(x, top + 1, z, leaves)


def conifer(world, x, y, z, h, rng, log="metasequoia_log", leaves="metasequoia_leaves", thick=False):
    """Metasequoia / dawn redwood: a narrow cone (thick: 2x2 trunk with a buttressed foot, for old giants)."""
    for k in range(h):
        world.set(x, y + k, z, log)
        if thick and k < h * 0.6:
            for dx, dz in ((1, 0), (0, 1), (1, 1)):
                world.set(x + dx, y + k, z + dz, log)
    if thick:
        for dx, dz in ((-1, 0), (2, 1), (0, -1), (1, 2)):
            for k in range(int(rng.integers(1, 4))):
                world.set(x + dx, y + k, z + dz, log)
    start = int(h * 0.45) if thick else 3
    for k in range(start, h + 2):
        r = max(0, int((h + 2 - k) * 0.35))
        if thick:
            r = min(r, 4 + int(rng.integers(0, 2)))
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if abs(dx) + abs(dz) <= r + (k % 2) and (dx, dz) != (0, 0) or k >= h:
                    if rng.random() > 0.05:
                        world.set(x + dx, y + k, z + dz, leaves)


# ------------------------------------------------------------------ dinosaurs into the scene
def dino_mesh(rig, tex, pose, hidden, pos, yaw_deg, length_blocks, tint=(1, 1, 1), axis=2, roll_deg=0.0):
    """Mesh of a posed model, scaled so its extent along axis (2 = body length, 0 = wingspan) is length_blocks,
    standing on pos, turned by yaw (and banked by roll, for flyers)."""
    faces = rig.cube_faces(pose, hidden)
    pts = np.array([w for _c, _f, co, _uv in faces for _l, w in co.values()])
    lo, hi = pts.min(0), pts.max(0)
    s = length_blocks / (hi[axis] - lo[axis])
    yaw, roll = math.radians(yaw_deg), math.radians(roll_deg)
    R = np.array([[math.cos(yaw), 0, math.sin(yaw)], [0, 1, 0], [-math.sin(yaw), 0, math.cos(yaw)]])
    R = R @ np.array([[math.cos(roll), -math.sin(roll), 0], [math.sin(roll), math.cos(roll), 0], [0, 0, 1]])
    off = np.array([-(lo[0] + hi[0]) / 2, -lo[1], -(lo[2] + hi[2]) / 2])
    tw, th = tex.size
    out = []
    for _c, _f, co, (u0, v0, u1, v1) in faces:
        if u1 <= u0 or v1 <= v0:
            continue
        keys = [(0, 0), (1, 0), (1, 1), (0, 1)]
        w = [R @ ((np.array(co[k][1]) + off) * s) + np.array(pos) for k in keys]
        n = np.cross(w[1] - w[0], w[3] - w[0])
        nn = np.linalg.norm(n)
        if nn < 1e-9:
            continue
        n /= nn
        uvs = [((u0 + k[0] * (u1 - u0)) / tw, (v0 + k[1] * (v1 - v0)) / th) for k in keys]
        out += gl.quad_verts([tuple(p) for p in w], uvs, tuple(n), 1.0)
    return gl.Mesh(np.array(out, np.float32), tex, tint)


def tree_fern(world, x, y, z, h, rng, log="tree_fern_log", leaves="tree_fern_leaves"):
    """Tree fern: short shaggy trunk and a flat rosette of fronds."""
    for k in range(h):
        world.set(x, y + k, z, log)
    top = y + h
    world.set(x, top, z, leaves)
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        world.set(x + dx, top, z + dz, leaves)
        if dx == 0 or dz == 0:
            world.set(x + 2 * dx, top - 1, z + 2 * dz, leaves)
