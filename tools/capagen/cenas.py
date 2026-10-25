"""
Cover scenes built from blocks and rendered with gl.py (run under xvfb-run).

usage:  xvfb-run -a python3 cenas.py [scene ...] [--wip DIR]   -> art/capa/cenas/<scene>.png
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gl  # noqa: E402
import render3d as r3  # noqa: E402
import voxels as vx  # noqa: E402
from pixel import noise2d  # noqa: E402

OUT = os.path.join(r3.ROOT, "art", "capa", "cenas")
BACKEND = os.environ.get("BACKEND", "gl")  # "gl" (OpenGL preview, seconds) or "cycles" (Blender path tracing, minutes)
SAMPLES = int(os.environ.get("SAMPLES", 96))
HIDE = ("female_display", "saddle")
WIP = None
REX = "tyrannosaurus"
PTERO = "pteranodon"
_models = {}


def model(name):
    if name not in _models:
        _models[name] = r3.load(name, extra_path=WIP)
    return _models[name]


def place(scene, name, anim, t, pos, yaw, length, tint=(1, 1, 1), rim=0.7, axis=2, roll=0.0):
    rig, tex, m = model(name)
    pose = r3.pose(m, anim, t) if anim else None
    mesh = vx.dino_mesh(rig, tex, pose, HIDE, pos, yaw, length, tint, axis, roll)
    mesh.rim = rim
    scene.add(mesh)


def dof(img, depth, focus, near_ok, far_blur=6.0, ramp=60.0):
    """Blur what lies beyond the focus distance, more the farther it is (cheap layered depth of field)."""
    out = np.asarray(img, float)
    levels = [(focus + near_ok, 1.2), (focus + near_ok + ramp * 0.5, far_blur * 0.5), (focus + near_ok + ramp, far_blur)]
    for dist, rad in levels:
        b = np.asarray(img.filter(ImageFilter.GaussianBlur(rad)), float)
        k = np.clip((depth - dist) / (ramp * 0.5), 0, 1)[..., None]
        out = out * (1 - k) + b * k
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def bloom(img, threshold=200, radius=18, strength=0.35):
    a = np.asarray(img, float)
    lum = a.mean(-1, keepdims=True)
    hi = np.clip(a * ((lum - threshold) / (255 - threshold)).clip(0, 1), 0, 255)
    b = np.asarray(Image.fromarray(hi.astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius)), float)
    return Image.fromarray(np.clip(a + b * strength, 0, 255).astype(np.uint8), "RGB")


def vignette(img, k=0.35):
    a = np.asarray(img, float)
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - k * np.clip((((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) - 0.25, 0, 1)
    return Image.fromarray(np.clip(a * v[..., None], 0, 255).astype(np.uint8), "RGB")


SUNSET = dict(top=(0.20, 0.24, 0.40), mid=(0.62, 0.42, 0.45), hor=(0.98, 0.70, 0.45), glow=(1.0, 0.62, 0.30),
              sun_col=(1.35, 0.95, 0.62), sky_amb=(0.42, 0.40, 0.55), gnd_amb=(0.30, 0.22, 0.18),
              fog_col=(0.85, 0.58, 0.45), fog_density=0.006, fog_height=62, water_sky=(0.95, 0.66, 0.48),
              water_deep=(0.12, 0.16, 0.20), clouds=0.6, sun_size=0.0009,
              sky_strength=float(os.environ.get("SKYS", 1.3)), sun_strength=float(os.environ.get("SUNS", 8.0)),
              fill=float(os.environ.get("FILL", 1.2)), glow_gain=float(os.environ.get("GLOWG", 2.5)),
              fog_scale=float(os.environ.get("FOGS", 0.35)), fog_aniso=0.75)


def build_world(rng, nx, nz, height, river=None, sea=60, forest_z=(5, 95), trees=70, plants=2200, keep=None):
    """A Cretaceous valley: fern litter and grass, a river, araucarias, dawn redwoods and tree ferns, ferns and
    horsetails underneath."""
    world = vx.World()
    litter = noise2d(nz, nx, 18, rng, 3)
    vx.terrain(world, 0, 0, nx, nz, height, sea=sea, under="soil",
               top_fn=lambda x, z: "litter" if litter[z % nz, x % nx] > 0.05 else "grass")
    for _ in range(trees):
        x, z = int(rng.uniform(5, nx - 5)), int(rng.uniform(*forest_z))
        if (river and river(x, z) < 16) or (keep and not keep(x, z)):
            continue
        y = int(round(height(x, z))) + 1
        if y <= sea + 2:
            continue
        k = rng.random()
        if k < 0.55:
            vx.araucaria(world, x, y, z, int(rng.uniform(14, 24)), rng)
        elif k < 0.85:
            vx.conifer(world, x, y, z, int(rng.uniform(12, 20)), rng)
        else:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 7)), rng)
    kinds = ["royal_fern"] * 4 + ["bracken"] * 3 + ["horsetail"] * 2 + ["tall_horsetail", "tall_bracken", "cycad",
                                                                        "clubmoss", "cretaceous_grass"]
    for _ in range(plants):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if h > sea + 1 and (x, h + 1, z) not in world.blocks:
            kind = kinds[int(rng.integers(len(kinds)))]
            tall = kind.startswith("tall_") or kind == "cycad"
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.6, 2.2) if tall else rng.uniform(0.8, 1.2)))
    return world


class Shot:
    """Mesh list for the Cycles backend (no OpenGL context needed)."""

    def __init__(self, W, H):
        self.W, self.H, self.meshes = W, H, []

    def add(self, mesh):
        self.meshes.append(mesh)


def shoot(scene, cam, target, fov, sun, look, shadow_box, focus, gl_post, fstop=4.0, fog_box=None, exposure=0.0):
    """Render with the chosen backend. gl_post(col, depth) adds the OpenGL preview's fake depth of field and glow;
    Cycles does depth of field, shadows and fog for real, so it only gets a light vignette."""
    if BACKEND == "cycles":
        import blend
        ss = float(os.environ.get("SS", 1.0))  # supersampling: render bigger, scale down (crisper pixel textures)
        W, H = int(scene.W * ss), int(scene.H * ss)
        col = blend.render(scene.meshes, cam, target, fov, sun, look, W, H, SAMPLES, focus, fstop,
                           fog_box, exposure=exposure)
        if ss != 1.0:
            col = col.resize((scene.W, scene.H), Image.LANCZOS)
        return vignette(col, 0.22)
    col, depth = scene.render(cam, target, fov, sun, look, shadow_box)
    return gl_post(col, depth)


def scene_from(world, W, H):
    img, uv = vx.atlas(vx.all_textures())
    scene = Shot(W, H) if BACKEND == "cycles" else gl.Scene(W, H)
    scene.add(gl.Mesh(world.mesh(uv), img))
    if world.water:
        scene.add(gl.Mesh(world.water_mesh(), img, water=True))
    return scene


def ground(height, x, z, r=2):
    """Highest block top around (x, z): the camera must sit above it."""
    return max(int(round(height(x + i, z + k))) for i in range(-r, r + 1) for k in range(-r, r + 1)) + 1


def clear_of(seg_a, seg_b, r):
    """Tree filter: keep (x, z) at least r blocks from the segment a-b (keeps the view to the subject open)."""
    ax, az = seg_a
    bx, bz = seg_b
    def ok(x, z):
        dx, dz = bx - ax, bz - az
        t = max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz)))
        return math.hypot(x - ax - t * dx, z - az - t * dz) >= r
    return ok


def ribeira(W=1920, H=1080):
    """T. rex walking on a river beach at sunset, the river leading into the glow, araucaria forest on both banks."""
    rng = np.random.default_rng(3)
    nx, nz = 240, 240
    hn = noise2d(nz, nx, 40, rng, 4)
    river = lambda x, z: abs((x - 90) - 22 * math.sin(z / 30.0))  # noqa: E731

    def height(x, z):
        base = 64 + hn[z % nz, x % nx] * 6
        d = river(x, z)
        if d < 9:
            base = 55 + d * 0.4
        elif d < 18:
            base = min(base, 59 + (d - 9) * 0.6)
        if z < 60:
            base += (60 - z) * 0.9
        return base

    rx, rz = 99, 186
    ry = int(round(height(rx, rz))) + 1
    cx, cz = rx + 3, rz + 17
    cam = (cx + 0.5, max(ground(height, cx, cz) + 1.6, ry + float(os.environ.get('CAMY', 3.5))), cz + 0.5)
    keep = clear_of((cx, cz), (rx - 8, rz - 30), 9)
    world = build_world(rng, nx, nz, height, river, forest_z=(5, 215), trees=160, keep=keep)
    scene = scene_from(world, W, H)
    place(scene, REX, os.environ.get("ANIM", "roar"), float(os.environ.get("T", 0.15)), (rx, ry, rz), float(os.environ.get("YAW", 140)), 12.5)
    target = (rx - 11, ry + 5.0, rz - 8)
    sun = tuple(float(v) for v in os.environ.get("SUNR", "-0.62,0.14,-0.78").split(","))
    return shoot(scene, cam, target, 42, sun, SUNSET, ((rx - 10, ry, rz - 40), 110), math.dist(cam, (rx, ry + 4, rz)),
                 lambda col, depth: vignette(bloom(dof(col, depth, 20, 10, 5.0, 80))), 5.6,
                 ((120, 80, 120), (240, 60, 240)))


MORNING = dict(top=(0.28, 0.48, 0.82), mid=(0.60, 0.74, 0.92), hor=(0.98, 0.90, 0.76), glow=(1.0, 0.82, 0.55),
               sun_col=(1.30, 1.15, 0.92), sky_amb=(0.50, 0.58, 0.74), gnd_amb=(0.30, 0.29, 0.25),
               fog_col=(0.80, 0.86, 0.93), fog_density=0.0035, fog_height=64, water_deep=(0.04, 0.17, 0.24),
               clouds=0.55, sun_size=0.0008, cloud_shift=3.0)


def falesia(W=1920, H=1080):
    """Pteranodon gliding past white chalk sea cliffs in the morning: a wave-cut arch, a sea stack and flint bands,
    more of the colony over the sea."""
    rng = np.random.default_rng(11)
    nx, nz, y0, ny = 260, 260, 40, 60
    hn = noise2d(nz, nx, 30, rng, 4)
    cn = noise2d(nz, 1, 14, rng, 3)
    ero = noise2d(nz, ny, 11, rng, 3)  # (z, y): how far the face is eaten back
    coast = lambda z: 110 + 16 * math.sin(z / 37.0) + cn[z % nz, 0] * 8  # noqa: E731

    def height(x, z):
        d = x - coast(z)
        if d >= 0:
            return 86 + hn[z % nz, x % nx] * 3 + min(d, 30) * 0.08
        if d > -4:
            return 61
        return max(44, 58 + d * 0.5)

    X, Z, Y = np.meshgrid(np.arange(nx), np.arange(nz), np.arange(y0, y0 + ny), indexing="ij")
    cst = np.array([coast(z) for z in range(nz)])[None, :, None]
    top = np.array([[height(x, z) for z in range(nz)] for x in range(nx)])[:, :, None]
    eat = ero[Z % nz, Y - y0] * 3.2 + ((Y - 60) // 6 % 2) * 0.8 + np.where((Y > 59) & (Y < 65), 2.5, 0) + np.where(Y > 82, 1.5 * (Y - 82) / 4, 0)
    land = (X - cst - eat >= 0) & (Y <= np.round(top))
    sea_floor = (X - cst < 0) & (Y <= np.round(top))
    solid = land | sea_floor
    # sea stack and an arch (a wall from the cliff out to sea with a hole worn through)
    sx, sz = coast(128) - 24, 128
    r = 4.5 + ero[Z % nz, Y - y0] * 2
    solid |= (np.hypot(X - sx, Z - sz) < r) & (Y <= 79 - np.abs(Z - sz) * 0.3)
    ax, az = coast(96), 96
    wall = (X > ax - 30) & (X < ax + 2) & (np.abs(Z - az) < 4 + ero[Z % nz, Y - y0] * 1.5) & (Y <= 84 - (ax - X).clip(0) * 0.25)
    hole = ((X - (ax - 15)) / 10.0) ** 2 + ((Y - 52) / 16.0) ** 2 < 1
    solid |= wall & ~hole
    world = vx.World()
    band = noise2d(nz, nx, 5, rng, 2)

    def block(x, y, z, depth):
        if x - coast(z) < -1 and y <= 62 and not (abs(z - az) < 6 or math.hypot(x - sx, z - sz) < 7):
            return "pebbles" if y >= 59 else "gravel" if depth == 0 else "stone"
        if depth == 0 and y > 80:
            return "grass" if hn[z % nz, x % nx] > -0.2 else "litter"
        if depth < 2 and y > 80:
            return "dirt"
        if (y - 64) % 7 == 0 and band[z % nz, x % nx] > 0.0:
            return "shale"
        return "chalk"

    vx.fill(world, solid, (0, 0, y0), block)
    for _ in range(1800):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        if x - coast(z) > 4:
            h = int(round(height(x, z)))
            if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks:
                k = ["cretaceous_grass"] * 4 + ["bracken", "clubmoss", "horsetail"]
                world.plants.append((x, h + 1, z, k[int(rng.integers(len(k)))], rng.uniform(0.8, 1.2)))
    for _ in range(26):
        z = int(rng.uniform(5, 250))
        x = int(coast(z) + rng.uniform(16, 60))
        if x < nx - 3 and (x, int(round(height(x, z))), z) in world.blocks:
            vx.araucaria(world, x, int(round(height(x, z))) + 1, z, int(rng.uniform(12, 20)), rng)
    world.water = [(-3000, -3000, 3000, 3000, 60.9)]
    scene = scene_from(world, W, H)
    cz = 236
    cx = int(coast(cz)) - 24
    cam = (cx + 0.5, 84.0, cz + 0.5)
    fx, fy, fz = cx + float(os.environ.get("PX", -3)), 80.5, cz - float(os.environ.get("PZ", 10))
    place(scene, PTERO, "glide", 0.2, (fx, fy, fz), float(os.environ.get("YAW", 150)), 7.0, axis=0,
          roll=float(os.environ.get("ROLL", -14)))
    for i, (dx, dy, dz, yw) in enumerate([(20, 10, -60, 200), (30, 2, -95, 120), (8, 16, -120, 160),
                                          (-12, 6, -75, 230), (24, 22, -150, 180), (40, 12, -45, 140)]):
        place(scene, PTERO, "glide" if i % 2 else "fly", 0.3 * i, (cx + dx, 84 + dy, cz + dz), yw, 7.0, axis=0,
              roll=rng.uniform(-20, 20))
    target = (cx + 12, 78, cz - 60)
    sun = (-0.75, 0.32, -0.55)
    return shoot(scene, cam, target, 50, sun, MORNING, ((cx + 20, 75, cz - 70), 110), math.dist(cam, (fx, fy, fz)),
                 lambda col, depth: vignette(bloom(dof(col, depth, 13, 8, 3.0, 160), 215, 16, 0.25), 0.25), 5.6,
                 ((130, 75, 130), (600, 60, 600)))


MIST = dict(top=(0.52, 0.60, 0.66), mid=(0.70, 0.74, 0.74), hor=(0.88, 0.87, 0.80), glow=(1.0, 0.86, 0.62),
            sun_col=(1.05, 0.95, 0.78), sky_amb=(0.52, 0.58, 0.60), gnd_amb=(0.26, 0.28, 0.24),
            fog_col=(0.74, 0.78, 0.72), fog_density=0.017, fog_height=72, water_deep=(0.08, 0.14, 0.13),
            clouds=0.0, sun_size=0.0, fog_scale=float(os.environ.get("FOGS", 0.3)), sun_strength=float(os.environ.get("SUNS", 8.0)),
            fog_aniso=0.7)


MIST_DARK = dict(top=(0.28, 0.34, 0.38), mid=(0.40, 0.46, 0.48), hor=(0.54, 0.60, 0.58), glow=(0.78, 0.84, 0.80),
                 sun_col=(0.85, 0.93, 1.0), sky_amb=(0.34, 0.40, 0.44), gnd_amb=(0.16, 0.18, 0.17),
                 fog_col=(0.50, 0.58, 0.58), fog_density=0.020, fog_height=72, water_deep=(0.06, 0.10, 0.10),
                 clouds=0.0, sun_size=0.0, fog_scale=float(os.environ.get("FOGS", 0.55)),
                 sun_strength=float(os.environ.get("SUNS", 6.0)), sky_strength=float(os.environ.get("SKYS", 1.3)),
                 fog_aniso=0.75, agx="AgX - Medium High Contrast", fill=float(os.environ.get("FILL", 0.7)))


def neblina(W=1920, H=1080, manada=False, espreita=False):
    """An Alamosaurus walking out of the morning fog between giant dawn redwoods, ferns all around.
    manada: the whole family (two more adults and a juvenile) and small herbivores in the ferns."""
    rng = np.random.default_rng(5)
    nx, nz = 200, 200
    hn = noise2d(nz, nx, 30, rng, 4)
    height = lambda x, z: 64 + hn[z % nz, x % nx] * 2.5  # noqa: E731
    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, under="soil",
               top_fn=lambda x, z: "needles" if hn[z % nz, x % nx] > 0.1 else "litter")
    ax, az = 96, 120
    cx, cz = 106, 160
    keep = clear_of((cx, cz), (ax, az), 7)
    for _ in range(170):
        x, z = int(rng.uniform(4, nx - 4)), int(rng.uniform(4, nz - 4))
        if not keep(x, z) or math.hypot(x - ax, z - az) < 14 or (manada and math.hypot(x - 100, z - 106) < 24) \
                or (espreita and math.hypot(x - 91, z - 144) < 9):
            continue
        y = int(round(height(x, z))) + 1
        big = rng.random() < 0.6 or math.hypot(x - cx, z - cz) < 40
        vx.conifer(world, x, y, z, int(rng.uniform(26, 38) if big else rng.uniform(14, 24)), rng, thick=big)
    kinds = ["royal_fern"] * 5 + ["bracken"] * 3 + ["tall_bracken"] * 2 + ["horsetail", "tall_horsetail", "clubmoss"]
    for _ in range(9000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks and math.hypot(x - cx, z - cz) > 3.5:
            kind = kinds[int(rng.integers(len(kinds)))]
            tall = kind.startswith("tall_")
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.7, 2.3) if tall else rng.uniform(0.9, 1.3)))
    spots = ((116, 98, 245, 24.0, 0.7), (106, 128, 252, 10.0, 0.45), (72, 110, 250, 25.0, 0.1), (60, 96, 245, 20.0, 0.85))
    scene = scene_from(world, W, H)
    ay = int(round(height(ax, az))) + 1
    place(scene, "alamosaurus", "walk", 0.25, (ax, ay, az), float(os.environ.get("YAW", 250)), 26.0, rim=0.5)
    if manada:
        gy = lambda x, z: int(round(height(int(x), int(z)))) + 1  # noqa: E731
        for (x, z, yaw, length, t) in spots:
            place(scene, "alamosaurus", "walk", t, (x, gy(x, z), z), yaw, length, rim=0.5)
        herd(scene, rng, "thescelosaurus", ["graze", "idle"], (93, 136), 2, (3, 2), 200, 4.0, gy, 3)
        herd(scene, rng, "protoceratops", ["graze", "idle", "graze"], (112, 138), 3, (3, 2), 150, 2.0, gy, 2)
        herd(scene, rng, "pachycephalosaurus", ["graze", "walk"], (90, 136), 2, (4, 2), 110, 4.5, gy, 4)
    if espreita:  # a T. rex stalking through the ferns, unseen by the giant
        gy = lambda x, z: int(round(height(int(x), int(z)))) + 1  # noqa: E731
        px, pz = (float(v) for v in os.environ.get("PPOS", "90,146").split(","))
        place(scene, REX, os.environ.get("PANIM", "walk"), float(os.environ.get("PT", 0.3)), (px, gy(px, pz), pz),
              float(os.environ.get("PYAW", 345)), 12.5, rim=0.3)
    cam = (cx + 0.5, ground(height, cx, cz, 1) + (4.0 if manada else 2.4), cz + 0.5)
    target = (ax + 2, ay + 8, az)
    fov = 58 if manada else 50
    sun = tuple(float(v) for v in os.environ.get("SUN", "-0.5,0.6,-0.8").split(","))
    if espreita:
        sun = tuple(float(v) for v in os.environ.get("SUN", "0.2,0.35,-1.0").split(","))
    return shoot(scene, cam, target, fov, sun, MIST_DARK if espreita else MIST, ((ax, ay + 10, az + 20), 90), math.dist(cam, (ax, ay + 6, az)),
                 lambda col, depth: vignette(bloom(dof(col, depth, 40, 14, 3.0, 90), 205, 24, 0.3), 0.3), 4.0,
                 ((100, 85, 100), (200, 50, 200)))


def herd(scene, rng, name, anims, centre, n, spread, yaw, length, ground_y, min_gap=None, yaw_jitter=35, size=(0.82, 1.0)):
    """n animals of one species around centre: varied pose, phase, heading and size, never overlapping."""
    gap = min_gap or length * 0.55
    done = []
    tries = 0
    while len(done) < n and tries < 400:
        tries += 1
        x = centre[0] + rng.uniform(-spread[0], spread[0])
        z = centre[1] + rng.uniform(-spread[1], spread[1])
        if any(math.hypot(x - a, z - b) < gap for a, b in done):
            continue
        done.append((x, z))
        anim = anims[int(rng.integers(len(anims)))]
        place(scene, name, anim, float(rng.uniform(0, 1)), (x, ground_y(x, z), z), yaw + rng.uniform(-yaw_jitter, yaw_jitter),
              length * rng.uniform(*size))
    return done


VALE = dict(top=(0.26, 0.44, 0.80), mid=(0.52, 0.66, 0.86), hor=(0.98, 0.89, 0.74), glow=(1.0, 0.80, 0.52),
            sun_col=(1.25, 1.08, 0.86), sky_amb=(0.50, 0.58, 0.72), gnd_amb=(0.30, 0.29, 0.25),
            fog_col=(0.88, 0.88, 0.84), fog_density=0.012, fog_height=64, water_deep=(0.10, 0.20, 0.22),
            clouds=0.35, sun_size=0.0008, cloud_shift=7.0, sky_strength=float(os.environ.get("SKYS", 1.6)),
            sun_strength=float(os.environ.get("SUNS", 9.0)), fill=0.8, fog_scale=float(os.environ.get("FOGS", 0.8)), fog_aniso=0.7, glow_gain=2.0)


def vale(W=1920, H=1080):
    """Morning in a misty river valley, full of life: Triceratops grazing in front, hadrosaurs drinking at the river,
    titans walking in the fog on the far bank, a Pteranodon flock overhead."""
    rng = np.random.default_rng(21)
    nx, nz = 300, 280
    hn = noise2d(nz, nx, 40, rng, 4)
    river = lambda x, z: abs(z - (188 + 7 * math.sin(x / 26.0)))  # noqa: E731

    def height(x, z):
        base = 63.5 + hn[z % nz, x % nx] * 2.5
        d = river(x, z)
        if d < 8:
            base = 57.5 + d * 0.35
        elif d < 60:
            base = min(base, 60.5 + (d - 8) * (0.4 if z < 188 else 0.11) + hn[z % nz, x % nx] * 0.8)
        if z < 145:
            base += (145 - z) * 0.15
        return base

    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, sea=60, under="soil",
               top_fn=lambda x, z: "litter" if hn[z % nz, x % nx] > 0.25 else "grass")
    cx, cz = 150, 250
    keep = clear_of((cx, cz), (140, 120), 30)
    for _ in range(420):
        x, z = int(rng.uniform(3, nx - 3)), int(rng.uniform(3, nz - 3))
        far = z < 148
        edge = x < 60 or x > 245
        if not (far or (edge and rng.random() < 0.5) or rng.random() < 0.04) or river(x, z) < 15 or not keep(x, z):
            continue
        y = int(round(height(x, z))) + 1
        k = rng.random()
        if k < 0.45:
            vx.conifer(world, x, y, z, int(rng.uniform(22, 34)), rng, thick=True)
        elif k < 0.85:
            vx.araucaria(world, x, y, z, int(rng.uniform(14, 22)), rng)
        else:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 7)), rng)
    kinds = ["cretaceous_grass"] * 6 + ["royal_fern"] * 2 + ["bracken", "horsetail", "tall_horsetail", "clubmoss"]
    for _ in range(16000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(140, nz))
        h = int(round(height(x, z)))
        if h > 61 and (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks and math.hypot(x - cx, z - cz) > 3:
            kind = kinds[int(rng.integers(len(kinds)))]
            tall = kind.startswith("tall_")
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.7, 2.3) if tall else rng.uniform(0.8, 1.3)))
    scene = scene_from(world, W, H)
    gy = lambda x, z: int(round(height(int(x), int(z)))) + 1  # noqa: E731
    # focal group: Triceratops grazing on the near meadow
    herd(scene, rng, "triceratops", ["graze", "graze", "walk", "idle"], (160, 225), 3, (9, 4), 120, 9.0, gy, 8)
    # small herbivores in the grass
    herd(scene, rng, "thescelosaurus", ["graze", "idle", "walk"], (130, 232), 3, (7, 4), 250, 4.0, gy, 3)
    herd(scene, rng, "protoceratops", ["graze", "idle"], (142, 238), 3, (5, 3), 200, 2.0, gy, 2)
    # hadrosaurs at the river
    herd(scene, rng, "parasaurolophus", ["graze", "idle", "call", "walk"], (118, 193), 6, (26, 6), 80, 9.5, gy, 6)
    herd(scene, rng, "edmontosaurus", ["graze", "walk", "idle"], (178, 186), 4, (18, 6), 100, 11.0, gy, 7)
    # titans in the far mist
    herd(scene, rng, "alamosaurus", ["walk"], (130, 158), 3, (45, 5), 95, 28.0, gy, 18, yaw_jitter=12, size=(0.55, 1.0))
    # Pteranodon flock overhead
    for i in range(9):
        x, z = rng.uniform(90, 230), rng.uniform(130, 215)
        place(scene, "pteranodon", "glide" if i % 3 else "fly", float(rng.uniform(0, 1)),
              (x, rng.uniform(78, 96), z), rng.uniform(0, 360), 7.0 * rng.uniform(0.85, 1.0), axis=0,
              roll=rng.uniform(-25, 25))
    cam = (cx + 0.5, ground(height, cx, cz, 1) + float(os.environ.get("CAMY", 4.5)), cz + 0.5)
    target = (cx - 8, 66, cz - 70)
    sun = tuple(float(v) for v in os.environ.get("SUNV", "0.9,0.3,-0.35").split(","))
    return shoot(scene, cam, target, 50, sun, VALE, ((cx, 70, cz - 70), 140), math.dist(cam, (164, 66, 226)),
                 lambda col, depth: vignette(bloom(dof(col, depth, 28, 12, 3.0, 120), 215, 18, 0.25), 0.25), 8.0,
                 ((150, 73, 140), (300, 26, 280)))


DUSK = dict(top=(0.16, 0.18, 0.34), mid=(0.58, 0.34, 0.38), hor=(1.0, 0.64, 0.38), glow=(1.0, 0.56, 0.26),
            sun_col=(1.35, 0.85, 0.52), sky_amb=(0.40, 0.36, 0.50), gnd_amb=(0.30, 0.20, 0.16),
            fog_col=(0.90, 0.60, 0.44), fog_density=0.010, fog_height=63, water_deep=(0.12, 0.14, 0.18),
            clouds=0.55, sun_size=0.0010, cloud_shift=11.0, sky_strength=float(os.environ.get("SKYS", 1.1)),
            sun_strength=float(os.environ.get("SUNS", 8.0)), fill=float(os.environ.get("FILL", 1.4)),
            fog_scale=float(os.environ.get("FOGS", 0.5)), fog_aniso=0.75, glow_gain=float(os.environ.get("GLOWG", 3.5)))


def cacada(W=1920, H=1080):
    """Dusk on a dry floodplain: a T. rex and a Triceratops face off, the rest of the herd running in the dust behind,
    Pteranodons heading home."""
    rng = np.random.default_rng(33)
    nx, nz = 260, 240
    hn = noise2d(nz, nx, 36, rng, 4)
    mud = noise2d(nz, nx, 14, rng, 3)

    def height(x, z):
        base = 64 + hn[z % nz, x % nx] * 1.6 * min(1.0, math.hypot(x - 104, z - 160) / 30)
        if z < 90:
            base += (90 - z) * 0.2 + hn[(z * 3) % nz, (x * 2) % nx] * 4 * (90 - z) / 90
        return base

    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, under="soil",
               top_fn=lambda x, z: "mud" if mud[z % nz, x % nx] > 0.32 and z < 120 else "grass")
    cx, cz = 103, 178
    keep = clear_of((cx, cz), (100, 60), 40)
    for _ in range(150):
        x, z = int(rng.uniform(3, nx - 3)), int(rng.uniform(3, 160))
        if not keep(x, z) and z > 70:
            continue
        y = int(round(height(x, z))) + 1
        k = rng.random()
        if k < 0.7:
            vx.araucaria(world, x, y, z, int(rng.uniform(13, 22)), rng)
        elif k < 0.85:
            vx.conifer(world, x, y, z, int(rng.uniform(16, 26)), rng, thick=rng.random() < 0.4)
        else:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 7)), rng)
    kinds = ["cretaceous_grass"] * 6 + ["bracken", "clubmoss", "horsetail", "cycad"]
    for _ in range(9000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(60, nz))
        h = int(round(height(x, z)))
        if mud[z % nz, x % nx] > 0.28 or (x, h + 1, z) not in world.blocks and (x, h, z) not in world.blocks:
            continue
        if (x, h + 1, z) in world.blocks or math.hypot(x - cx, z - cz) < 4:
            continue
        kind = kinds[int(rng.integers(len(kinds)))]
        world.plants.append((x, h + 1, z, kind, rng.uniform(1.6, 2.1) if kind == "cycad" else rng.uniform(0.7, 1.1)))
    scene = scene_from(world, W, H)
    gy = lambda x, z: int(round(height(int(x), int(z)))) + 1  # noqa: E731
    rx, rz = (float(v) for v in os.environ.get("RPOS", "108,159").split(","))
    place(scene, REX, "roar", float(os.environ.get("RT", 0.2)), (rx, gy(rx, rz), rz),
          float(os.environ.get("RYAW", 72)), 12.5)
    tx, tz = 95, 155
    place(scene, "triceratops", "attack", float(os.environ.get("TT", 0.3)), (tx, gy(tx, tz), tz),
          float(os.environ.get("TYAW", 252)), 9.0)
    herd(scene, rng, "triceratops", ["run"], (70, 105), 5, (26, 6), 95, 8.5, gy, 9, yaw_jitter=12)
    herd(scene, rng, "parasaurolophus", ["run"], (150, 98), 4, (20, 6), 85, 9.0, gy, 8, yaw_jitter=12)
    for i in range(7):
        place(scene, PTERO, "fly" if i % 2 else "glide", float(rng.uniform(0, 1)),
              (rng.uniform(60, 160), rng.uniform(85, 105), rng.uniform(70, 130)), rng.uniform(60, 120), 7.0,
              axis=0, roll=rng.uniform(-20, 20))
    cam = (cx + 0.5, ground(height, cx, cz, 1) + 1.6, cz + 0.5)
    target = (cx + 1.5, gy(rx, rz) + 5.0, 154)
    sun = tuple(float(v) for v in os.environ.get("SUNC", "-0.03,0.17,-1.0").split(","))
    return shoot(scene, cam, target, 45, sun, DUSK, ((cx, 70, 140), 100), math.dist(cam, (rx - 3, 69, rz)),
                 lambda col, depth: vignette(bloom(dof(col, depth, 30, 8, 4.0, 90)), 0.3), 5.6,
                 ((130, 72, 130), (260, 22, 240)))


GOLD = dict(top=(0.24, 0.42, 0.78), mid=(0.48, 0.64, 0.88), hor=(0.98, 0.80, 0.56), glow=(1.0, 0.76, 0.46),
            sun_col=(1.30, 1.05, 0.76), sky_amb=(0.50, 0.58, 0.74), gnd_amb=(0.32, 0.30, 0.26),
            fog_col=(0.88, 0.86, 0.82), fog_density=0.006, fog_height=64, water_deep=(0.05, 0.20, 0.26), water_density=1.2,
            clouds=0.45, sun_size=0.0008, cloud_shift=17.0, sky_strength=float(os.environ.get("SKYS", 1.3)),
            sun_strength=float(os.environ.get("SUNS", 8.0)), fill=float(os.environ.get("FILL", 1.0)),
            fog_scale=float(os.environ.get("FOGS", 0.3)), fog_aniso=0.7, glow_gain=float(os.environ.get("GLOWG", 2.5)))


def costa(W=1920, H=1080):
    """Golden afternoon on the shore of the Inland Sea: titans wading in the shallows, hadrosaurs on the beach,
    an Elasmosaurus surfacing offshore, Pteranodons skimming the waves."""
    rng = np.random.default_rng(44)
    nx, nz = 240, 260
    hn = noise2d(nz, nx, 28, rng, 4)
    cn = noise2d(nz, 1, 18, rng, 3)
    coast = lambda z: 120 + 10 * math.sin(z / 45.0) + cn[z % nz, 0] * 6  # noqa: E731

    def height(x, z):
        d = x - coast(z)
        if d >= 0:
            return 61 + min(d, 12) * 0.25 + hn[z % nz, x % nx] * 1.5 * min(1.0, d / 10)
        return max(48, 60.4 + d * 0.12 if d > -25 else 57.4 + (d + 25) * 0.4)

    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, sea=60, beach=1, under="soil",
               top_fn=lambda x, z: "grass" if hn[z % nz, x % nx] > -0.1 else "litter")
    world.water = [(-3000, -3000, 3000, 3000, 60.9)]
    for _ in range(90):
        z = int(rng.uniform(5, 250))
        x = int(coast(z) + rng.uniform(14, 100))
        if x >= nx - 3:
            continue
        y = int(round(height(x, z))) + 1
        k = rng.random()
        if k < 0.55:
            vx.araucaria(world, x, y, z, int(rng.uniform(12, 20)), rng)
        elif k < 0.8:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 8)), rng)
        else:
            vx.conifer(world, x, y, z, int(rng.uniform(16, 26)), rng, thick=rng.random() < 0.3)
    kinds = ["cretaceous_grass"] * 5 + ["bracken", "cycad", "royal_fern", "horsetail"]
    for _ in range(9000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if h > 62 and (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks:
            kind = kinds[int(rng.integers(len(kinds)))]
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.5, 2.0) if kind == "cycad" else rng.uniform(0.8, 1.2)))
    scene = scene_from(world, W, H)
    gy = lambda x, z: int(round(height(int(x), int(z)))) + 1  # noqa: E731
    cz = 236
    cx = int(coast(cz)) + 7
    for (dx, z, yaw, length, t) in ((-10, 182, 160, 28.0, 0.2), (-22, 160, 150, 26.0, 0.6), (-4, 168, 165, 13.0, 0.4)):
        x = coast(z) + dx
        place(scene, "alamosaurus", "walk", t, (x, gy(x, z), z), yaw, length)
    herd(scene, rng, "edmontosaurus", ["graze", "idle", "walk", "call"], (coast(206) + 5, 206), 5, (3, 9), 105, 11.0, gy, 7)
    herd(scene, rng, "parasaurolophus", ["idle", "call", "walk"], (coast(140) + 6, 140), 4, (4, 10), 115, 9.5, gy, 7)
    ex, ez = coast(200) - 30, 200
    place(scene, "elasmosaurus", os.environ.get("EANIM", "idle"), 0.3, (ex, 59.4, ez), 60, 12.0)
    for i in range(10):
        z = rng.uniform(120, 220)
        place(scene, PTERO, "glide" if i % 3 else "fly", float(rng.uniform(0, 1)),
              (coast(int(z)) - rng.uniform(8, 50), rng.uniform(64, 84), z), rng.uniform(150, 240), 7.0, axis=0,
              roll=rng.uniform(-25, 25))
    cam = (cx + 0.5, ground(height, cx, cz, 1) + float(os.environ.get('CAMY', 5.0)), cz + 0.5)
    target = (coast(165) - 16, 64, 165)
    sun = tuple(float(v) for v in os.environ.get("SUNK", "-0.8,0.32,-0.25").split(","))
    return shoot(scene, cam, target, 52, sun, GOLD, ((cx - 20, 64, 180), 110), math.dist(cam, (coast(182) - 10, 64, 182)),
                 lambda col, depth: vignette(bloom(dof(col, depth, 40, 15, 3.0, 120), 215, 16, 0.25), 0.25), 8.0,
                 ((cx - 30, 70, 160), (300, 22, 260)))


SCENES = {"ribeira": ribeira, "falesia": falesia, "neblina": neblina, "vale": vale, "cacada": cacada, "costa": costa,
          "manada": lambda W=1920, H=1080: neblina(W, H, True),
          "espreita": lambda W=1920, H=1080: neblina(W, H, espreita=True)}

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--wip" in args:
        i = args.index("--wip")
        WIP = os.path.abspath(args[i + 1])
        args = args[:i] + args[i + 2:]
        if os.path.exists(os.path.join(WIP, "tyrannosaurus_v3.py")):
            REX = "tyrannosaurus_v3"
        if os.path.exists(os.path.join(WIP, "pteranodon_v3.py")):
            PTERO = "pteranodon_v3"
    os.makedirs(OUT, exist_ok=True)
    small = "--small" in args
    args = [a for a in args if a != "--small"]
    for name in args or SCENES:
        img = SCENES[name](960, 540) if small else SCENES[name]()
        img.save(os.path.join(OUT, f"{name}.png"))
        print(name, "ok")
