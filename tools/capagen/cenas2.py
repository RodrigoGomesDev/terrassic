"""
Cover scenes for the remade creatures (T. rex v2 and Pteranodon v3), rendered with Blender Cycles (blend.py).
The world is built from the mod's own block textures (voxels.py); the creatures are the game's GeckoLib files
(geckomesh.py), posed with the game's animations.

usage:  python3 -B cenas2.py [scene ...] [--small] [--out DIR]     (needs `pip install bpy pillow numpy`)
        SAMPLES=128 SS=1.5 python3 -B cenas2.py falesia praia      -> art/capa/cenas/<scene>.png
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import blend  # noqa: E402
import cenas  # noqa: E402
import geckomesh as gk  # noqa: E402
import gl  # noqa: E402
import voxels as vx  # noqa: E402
from pixel import noise2d  # noqa: E402

OUT = os.path.join(cenas.r3.ROOT, "art", "capa", "cenas")
SAMPLES = int(os.environ.get("SAMPLES", 64))
def ENVC(k, d):
    v = os.environ.get(k)
    return tuple(float(c) for c in v.split(",")) if v else d


REX, PTERO = "tyrannosaurus", "pteranodon"
ENV = os.environ.get


def envf(name, default):
    return float(ENV(name, default))


def envv(name, default):
    return tuple(float(v) for v in ENV(name, default).split(","))


PLANTS = ("fern", "bracken", "horsetail", "clubmoss")


def foliage_mask(tex):
    """White where the atlas holds leaves and plants (they let the sun through), black elsewhere."""
    m = Image.new("RGB", (vx.T * len(tex), vx.T), (0, 0, 0))
    for i, n in enumerate(tex):
        if n in vx.LEAVES or (any(k in n for k in PLANTS) and "litter" not in n and "log" not in n):
            m.paste((255, 255, 255), (i * vx.T, 0, (i + 1) * vx.T, vx.T))
    return m


class Shot:
    def __init__(self, world):
        tex = vx.all_textures()
        img, uv = vx.atlas(tex)
        self.atlas, self.uv, self.mask = img, uv, foliage_mask(tex)
        self.meshes = [gl.Mesh(world.mesh(uv), img)]
        self.meshes[0].foliage = self.mask
        if world.water:
            self.meshes.append(gl.Mesh(world.water_mesh(), img, water=True))

    def debris(self, rng, centre, n, radius, height, textures, size=(0.12, 0.3)):
        """Little tumbling cubes in the air (leaves shaken loose, pebbles jumping): n of them in a cylinder."""
        out = []
        for _ in range(n):
            a, r = rng.uniform(0, 2 * math.pi), radius * math.sqrt(rng.uniform(0, 1))
            p = np.array((centre[0] + r * math.cos(a), centre[1] + rng.uniform(*height), centre[2] + r * math.sin(a)))
            s = rng.uniform(*size) / 2
            q = np.linalg.qr(rng.normal(size=(3, 3)))[0]  # a random rotation
            u0, v0, u1, v1 = self.uv[textures[int(rng.integers(len(textures)))]]
            uw, vh = (u1 - u0) / 4, (v1 - v0) / 4  # a 4x4 px patch of the texture, like a block-break particle
            pu, pv = u0 + uw * int(rng.integers(4)), v0 + vh * int(rng.integers(4))
            for face, (nrm, corners, _sh) in vx.FACES.items():
                cs = [tuple(p + q @ ((np.array(c) - 0.5) * 2 * s)) for c in corners]
                out += gl.quad_verts(cs, [(pu, pv), (pu + uw, pv), (pu + uw, pv + vh), (pu, pv + vh)], tuple(q @ nrm), 1.0)
        m = gl.Mesh(np.array(out, np.float32), self.atlas)
        m.foliage = self.mask
        self.meshes.append(m)
        return m

    def add(self, species, anim, t, pos, yaw, **kw):
        m = gk.mesh(species, anim, t, pos=pos, yaw=yaw, **kw)
        m.creature = True
        self.meshes.append(m)


def render(shot, W, H, cam, target, fov, sun, look, focus, fstop, fog_box=None, exposure=0.0, transparent=False):
    ss = envf("SS", 1.0)
    img = blend.render(shot.meshes, cam, target, fov, sun, look, int(W * ss), int(H * ss), SAMPLES, focus, fstop,
                       fog_box, exposure=exposure, transparent=transparent)
    if ss != 1.0:
        img = img.resize((W, H), Image.LANCZOS)
    return img if transparent else cenas.vignette(img, 0.22)


# ------------------------------------------------------------------ chalk cliffs on the Inland Sea
def chalk_coast(seed=11, nx=260, nz=300, extra_stacks=()):
    """White chalk cliffs over the sea with flint bands, a sea stack and a wave-cut arch (same recipe as
    cenas.falesia), returned as (world, coast(z), height(x, z), top_y(x, z))."""
    rng = np.random.default_rng(seed)
    y0, ny = 40, 60
    hn = noise2d(nz, nx, 30, rng, 4)
    cn = noise2d(nz, 1, 14, rng, 3)
    ero = noise2d(nz, ny, 11, rng, 3)
    coast = lambda z: 110 + 16 * math.sin(z / 37.0) + cn[int(z) % nz, 0] * 8  # noqa: E731

    def height(x, z):
        d = x - coast(z)
        if d >= 0:
            return 86 + hn[int(z) % nz, int(x) % nx] * 3 + min(d, 30) * 0.08
        if d > -4:
            return 61
        return max(44, 58 + d * 0.5)

    X, Z, Y = np.meshgrid(np.arange(nx), np.arange(nz), np.arange(y0, y0 + ny), indexing="ij")
    cst = np.array([coast(z) for z in range(nz)])[None, :, None]
    top = np.array([[height(x, z) for z in range(nz)] for x in range(nx)])[:, :, None]
    eat = (ero[Z % nz, Y - y0] * 3.2 + ((Y - 60) // 6 % 2) * 0.8 + np.where((Y > 59) & (Y < 65), 2.5, 0)
           + np.where(Y > 82, 1.5 * (Y - 82) / 4, 0))
    land = (X - cst - eat >= 0) & (Y <= np.round(top))
    sea_floor = (X - cst < 0) & (Y <= np.round(top))
    solid = land | sea_floor
    sx, sz = coast(envf("STZ", 150)) - envf("STX", 500), envf("STZ", 150)
    r = 4.5 + ero[Z % nz, Y - y0] * 2
    solid |= (np.hypot(X - sx, Z - sz) < r) & (Y <= 79 - np.abs(Z - sz) * 0.3)
    for (ez, edx, er, etop) in extra_stacks:  # more stacks farther out (z, distance from the coast, radius, top y)
        ex = coast(ez) - edx
        solid |= (np.hypot(X - ex, Z - ez) < er + ero[Z % nz, Y - y0] * 1.5) & (Y <= etop - np.abs(Z - ez) * 0.2)
    ax, az = coast(envf("ARZ", 60)), envf("ARZ", 60)
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
    topmap = {}
    for (x, y, z) in world.blocks:
        if y > topmap.get((x, z), -1):
            topmap[(x, z)] = y

    def top_y(x, z):
        return topmap.get((int(math.floor(x)), int(math.floor(z))), 60) + 1

    world.water = [(-3000, -3000, 3000, 3000, 60.9)]
    return world, coast, height, top_y, rng, topmap


def edge(topmap, coast, z, y=84):
    """First column of cliff-top ground at row z, walking inland from the sea."""
    x = int(coast(z)) - 6
    while topmap.get((x, int(z)), 0) < y:
        x += 1
    return x + 0.5


def plant(world, rng, topmap, n, ok, kinds, tall=("cycad",)):
    keys = list(topmap)
    for _ in range(n):
        x, z = keys[int(rng.integers(len(keys)))]
        y = topmap[(x, z)]
        if y < 80 or not ok(x, z) or (x, y + 1, z) in world.blocks:
            continue
        kind = kinds[int(rng.integers(len(kinds)))]
        world.plants.append((x, y + 1, z, kind, rng.uniform(1.5, 2.1) if kind in tall else rng.uniform(0.8, 1.2)))


GOLDEN = dict(top=(0.16, 0.30, 0.62), mid=(0.52, 0.60, 0.80), hor=(1.0, 0.74, 0.48), glow=(1.0, 0.66, 0.36),
              sun_col=(1.40, 0.98, 0.62), sky_amb=(0.50, 0.56, 0.72), gnd_amb=(0.30, 0.28, 0.24),
              fog_col=(0.95, 0.80, 0.66), fog_density=0.006, fog_height=66, water_deep=(0.04, 0.16, 0.22),
              water_density=1.0, clouds=0.5, sun_size=0.0008, cloud_shift=5.0,
              sky_strength=envf("SKYS", 1.0), sun_strength=envf("SUNS", 9.0), fill=envf("FILL", 1.2),
              fog_scale=envf("FOGS", 0.04), fog_aniso=0.8, glow_gain=envf("GLOWG", 1.6), sun_angle=1.2,
              ripple_scale=envf("RIPS", 0.5), ripple=envf("RIP", 0.6), ripple_dist=envf("RDIST", 1.2), water_color=(0.10, 0.30, 0.38),
              water_trans=envf("WTR", 0.3), water_rough=envf("WRO", 0.06), agx=ENV("AGX", "AgX - Medium High Contrast"))


def falesia(W=1920, H=1080):
    """Late afternoon on the chalk cliffs: a T. rex at the edge roars out over the Inland Sea while the Pteranodon
    colony wheels along the cliff face below and around it."""
    world, coast, height, top_y, rng, topmap = chalk_coast()
    rz = envf("RZ", 206)
    rx = edge(topmap, coast, rz) + envf("RXO", 2.5)
    cz = rz + envf("CZO", 22)
    cx = rx + envf("CXO", -7)
    keep = lambda x, z: math.hypot(x - rx, z - rz) > 9 and math.hypot(x - cx, z - cz) > 5  # noqa: E731
    for _ in range(40):
        z = int(rng.uniform(5, 295))
        x = int(coast(z) + rng.uniform(20, 90))
        if (x, z) in topmap and keep(x, z) and abs(z - cz) > 14:
            k = rng.random()
            y = topmap[(x, z)] + 1
            if k < 0.6:
                vx.araucaria(world, x, y, z, int(rng.uniform(12, 21)), rng)
            elif k < 0.8:
                vx.tree_fern(world, x, y, z, int(rng.uniform(4, 7)), rng)
            else:
                vx.conifer(world, x, y, z, int(rng.uniform(14, 22)), rng)
    plant(world, rng, topmap, 5000, keep, ["cretaceous_grass"] * 5 + ["bracken", "clubmoss", "horsetail", "royal_fern"])
    shot = Shot(world)
    shot.add(REX, ENV("RANIM", "roar"), envf("RT", 0.38), (rx, top_y(rx, rz), rz), envf("RYAW", 125))
    # the colony over the sea: one close glider, the rest along the cliff face and out over the water
    ry = top_y(rx, rz)
    px, py, pz = rx + envf("PXO", -16), ry + envf("PYO", -3), rz + envf("PZO", 6)
    shot.add(PTERO, "glide", 0.25, (px, py, pz), envf("PYAW", 235), roll=envf("PROLL", -20), ground=False)
    for i, (dz, dx, dy, yw) in enumerate([(-20, -40, 9, 150), (-46, -30, -6, 200), (-70, -60, 14, 120),
                                          (-30, -75, 3, 230), (-95, -45, 22, 170), (-60, -95, -9, 140),
                                          (-120, -70, 6, 190), (-8, -58, 20, 215), (-150, -100, 12, 160)]):
        z = rz + dz
        shot.add(PTERO, "fly" if i % 3 == 0 else "glide", (0.37 * i) % 1, (rx + dx, ry + dy, z), yw,
                 roll=float(rng.uniform(-22, 22)), ground=False, sex="female" if i % 2 else "male")
    cam = (cx, ry + envf("CAMY", 0.5), cz)
    target = (rx + envf("TXO", -7), ry + envf("TYO", 3.5), rz + envf("TZO", -2))
    sun = envv("SUN", "-0.9,0.16,-0.4")
    focus = math.dist(cam, (rx, ry + 3, rz))
    look = {"golden": GOLDEN, "storm": STORM, "fire": FIRE}[ENV("LOOK", "golden")]
    return render(shot, W, H, cam, target, envf("FOV", 46), sun, look, focus, envf("FSTOP", 4.0),
                  ((130, 75, 150), (600, 60, 600)))


def beach_world(rz, rx_off, keep=None):
    """The beach of the Inland Sea: sand between the water and an araucaria forest, a clearing at (coast(rz)+rx_off, rz)."""
    rng = np.random.default_rng(int(envf("SEED", 7)))
    nx, nz = 220, 280
    hn = noise2d(nz, nx, 24, rng, 4)
    cn = noise2d(nz, 1, 20, rng, 3)
    coast = lambda z: 96 + 9 * math.sin(z / 50.0) + cn[int(z) % nz, 0] * 5  # noqa: E731

    def height(x, z):
        d = x - coast(z)
        if d >= 0:
            return 61 + max(0.0, d - 12) * 0.22 + hn[int(z) % nz, int(x) % nx] * 1.4 * min(1.0, max(0.0, d - 10) / 8)
        return max(50, 60.6 + d * 0.18)

    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, sea=60, beach=1, under="soil",
               top_fn=lambda x, z: "grass" if hn[z % nz, x % nx] > -0.15 else "litter")
    world.water = [(-3000, -3000, 3000, 3000, 60.9)]
    # boulders on the beach, where the colony rests
    for (bz, bdx, r) in ((150, 2, 2.6), (128, 5, 3.0)):
        bx = coast(bz) + bdx
        for x in range(int(bx - r - 1), int(bx + r + 2)):
            for z in range(int(bz - r - 1), int(bz + r + 2)):
                for y in range(59, 66):
                    if ((x - bx) / r) ** 2 + ((z - bz) / r) ** 2 + ((y - 61) / (r * 0.9)) ** 2 < 1:
                        world.set(x, y, z, "conglomerate" if rng.random() < 0.6 else "limestone")
    rx = coast(rz) + rx_off
    for _ in range(170):
        z = int(rng.uniform(3, nz - 3))
        x = int(coast(z) + rng.uniform(16, 110))
        if x >= nx - 3 or math.hypot(x - rx, z - rz) < 9 or (z > 150 and x < coast(z) + 22) or (keep and not keep(x, z)):
            continue
        y = int(round(height(x, z))) + 1
        k = rng.random()
        if k < 0.55:
            vx.araucaria(world, x, y, z, int(rng.uniform(13, 23)), rng)
        elif k < 0.75:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 7)), rng)
        else:
            vx.conifer(world, x, y, z, int(rng.uniform(14, 24)), rng, thick=rng.random() < 0.3)
    kinds = ["cretaceous_grass"] * 5 + ["bracken", "cycad", "royal_fern", "horsetail", "clubmoss"]
    for _ in range(9000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if h > 61 and (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks:
            kind = kinds[int(rng.integers(len(kinds)))]
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.5, 2.0) if kind == "cycad" else rng.uniform(0.8, 1.2)))
    if ENV("WET", "1") == "1":  # the sand the waves reach stays dark and wet
        for (x, y, z), b in list(world.blocks.items()):
            if b == "sand" and y >= 60 and -3 <= x - coast(z) <= 1.5 and (x, y + 1, z) not in world.blocks:
                world.set(x, y, z, "wet_sand")
    return world, coast, height, rng


def praia(W=1920, H=1080):
    """Sunset on the beach of the Inland Sea: a T. rex bursts out of the araucaria forest and the Pteranodon colony
    resting on the sand takes off all at once."""
    rz = envf("RZ", 192)
    world, coast, height, rng = beach_world(rz, envf("RXO", 13))
    rx = coast(rz) + envf("RXO", 13)
    shot = Shot(world)
    gy = lambda x, z: max(61.0, int(round(height(x, z))) + 1.0)  # noqa: E731
    shot.add(REX, ENV("RANIM", "run"), envf("RT", 0.15), (rx, gy(rx, rz), rz), envf("RYAW", 118))
    colony = [  # (z, dx from the coast, anim, t, yaw, lift): the ones nearest the rex already in the air
        (205, 1, "idle", 0.3, 100, 0.0), (210, -2, "call", 0.45, 140, 0.0), (199, 4, "takeoff", 0.45, 150, 0.0),
        (194, 6, "takeoff", 0.7, 135, 0.0), (214, 3, "takeoff", 0.3, 160, 0.0), (190, 2, "fly", 0.2, 145, 4.0),
        (200, -6, "fly", 0.6, 165, 6.5), (186, -4, "fly", 0.85, 130, 9.0), (195, -14, "glide", 0.3, 175, 12.0),
        (176, -10, "fly", 0.1, 150, 15.0), (168, -24, "glide", 0.7, 200, 19.0), (182, -30, "glide", 0.4, 160, 24.0)]
    for i, (z, dx, anim, t, yaw, lift) in enumerate(colony):
        z = z + envf("COLZ", 0)
        x = coast(z) + dx
        air = lift > 0
        top = max((y for (bx, y, bz) in world.blocks if bx == int(x) and bz == int(z)), default=60) + 1
        shot.add(PTERO, anim, t, (x, top + lift, z), yaw, roll=float(rng.uniform(-18, 18)) if air else 0.0,
                 ground=not air, sex="female" if i % 3 == 1 else "male")
    cz = envf("CZ", 240)
    cx = coast(cz) + envf("CXO", 1)
    cam = (cx, envf("CAMY", 62.4), cz)
    target = (coast(195) + envf("TXO", 3), envf("TY", 66.5), envf("TZ", 195))
    sun = envv("SUN", "-0.85,0.13,-0.5")
    focus = math.dist(cam, (coast(199) + 4, 62, 199))
    return render(shot, W, H, cam, target, envf("FOV", 34), sun, GOLDEN, focus, envf("FSTOP", 5.6),
                  ((110, 72, 140), (500, 26, 500)))


def voo(W=1920, H=1080):
    """A Pteranodon glides past the camera along the shore at sunset; below, on the beach, a T. rex stops to look up."""
    rz = envf("RZ", 188)
    world, coast, height, rng = beach_world(rz, envf("RXO", 6))
    rx = coast(rz) + envf("RXO", 6)
    shot = Shot(world)
    gy = lambda x, z: max(61.0, int(round(height(x, z))) + 1.0)  # noqa: E731
    shot.add(REX, ENV("RANIM", "roar"), envf("RT", 0.3), (rx, gy(rx, rz), rz), envf("RYAW", 95))
    cz = envf("CZ", 216)
    cam = (coast(cz) + envf("CXO", -13), envf("CAMY", 69), cz)
    target = (rx + envf("TXO", -7), envf("TY", 64.5), rz + envf("TZO", 0))
    # the hero flyer is placed in the camera's frame: PD ahead, PX to the right, PY up (blocks)
    f = np.subtract(target, cam)
    f = f / np.linalg.norm(f)
    r = np.cross(f, (0, 1, 0))
    r = r / np.linalg.norm(r)
    u = np.cross(r, f)
    px, py, pz = np.array(cam) + f * envf("PD", 15) + r * envf("PX", -4.5) + u * envf("PY", 1.2)
    shot.add(PTERO, ENV("PANIM", "glide"), envf("PT", 0.3), (px, py, pz), envf("PYAW", 115), roll=envf("PROLL", -8),
             pitch=envf("PPITCH", 0), ground=False)
    for i, (z, dx, y, yw) in enumerate([(150, -30, 74, 170), (120, -20, 80, 200), (110, -50, 72, 140),
                                         (95, -36, 84, 190)]):
        shot.add(PTERO, "fly" if i % 2 else "glide", (0.31 * i) % 1, (coast(z) + dx, y, z), yw,
                 roll=float(rng.uniform(-20, 20)), ground=False, sex="female" if i % 2 else "male")
    sun = envv("SUN", "-0.8,0.16,0.45")
    return render(shot, W, H, cam, target, envf("FOV", 44), sun, GOLDEN, math.dist(cam, (px, py, pz)), envf("FSTOP", 4.0),
                  ((110, 72, 140), (500, 26, 500)))


SCENES = {"falesia": falesia, "praia": praia, "voo": voo}

# ------------------------------------------------------------------ concepts for the second round (Rodrigo 30/10: more light, more animals, more intense)
FIRE = dict(top=(0.10, 0.12, 0.30), mid=(0.62, 0.32, 0.34), hor=(1.0, 0.56, 0.26), glow=(1.0, 0.52, 0.20),
            sun_col=(1.50, 0.78, 0.40), sky_amb=(0.40, 0.30, 0.40), gnd_amb=(0.30, 0.20, 0.16),
            fog_col=(1.0, 0.66, 0.44), fog_density=0.012, fog_height=64, water_deep=(0.06, 0.08, 0.14),
            water_density=1.0, clouds=0.65, sun_size=0.0008, cloud_shift=9.0,
            sky_strength=envf("SKYS", 1.0), sun_strength=envf("SUNS", 9.0), fill=envf("FILL", 0.7),
            fog_scale=envf("FOGS", 0.45), fog_aniso=0.85, glow_gain=envf("GLOWG", 2.6), sun_angle=1.0,
            ripple_scale=0.5, ripple=0.6, ripple_dist=envf("RDIST", 1.2), water_color=(0.20, 0.14, 0.16), water_trans=0.3, water_rough=0.05,
            square_sun=envf("SQS", 0.035), sun_disc_gain=envf("SDG", 30.0), agx=ENV("AGX", "AgX - Punchy"))

STORM = dict(top=(0.10, 0.12, 0.16), mid=(0.26, 0.28, 0.32), hor=(0.80, 0.62, 0.42), glow=(1.0, 0.72, 0.40),
             sun_col=(1.50, 1.10, 0.70), sky_amb=(0.26, 0.28, 0.34), gnd_amb=(0.14, 0.14, 0.14),
             fog_col=(0.62, 0.62, 0.64), fog_density=0.014, fog_height=66, water_deep=(0.04, 0.07, 0.09),
             water_density=1.2, clouds=1.0, sun_size=0.0006, cloud_shift=21.0,
             sky_strength=envf("SKYS", 0.8), sun_strength=envf("SUNS", 11.0), fill=envf("FILL", 0.4),
             fog_scale=envf("FOGS", 0.5), fog_aniso=0.8, glow_gain=envf("GLOWG", 1.4), sun_angle=0.8,
             ripple_scale=0.6, ripple=0.9, ripple_dist=envf("RDIST", 1.2), water_color=(0.08, 0.12, 0.14), water_trans=0.25, water_rough=0.08,
             agx=ENV("AGX", "AgX - Medium High Contrast"))


def frame(cam, target):
    f = np.subtract(target, cam).astype(float)
    f /= np.linalg.norm(f)
    r = np.cross(f, (0, 1, 0))
    r /= np.linalg.norm(r)
    return f, r, np.cross(r, f)


def sun_from(cam, target, yaw_deg, elev_deg):
    """Sun direction relative to the view: yaw 0 = straight ahead, + to the right; elevation above the horizon."""
    f, _r, _u = frame(cam, target)
    a = math.atan2(f[0], -f[2]) + math.radians(yaw_deg)
    e = math.radians(elev_deg)
    return (math.sin(a) * math.cos(e), math.sin(e), -math.cos(a) * math.cos(e))


def in_view(cam, target, d, x, y):
    """World point d blocks ahead of the camera, x to the right and y up (blocks)."""
    f, r, u = frame(cam, target)
    return tuple(np.array(cam) + f * d + r * x + u * y)


def swarm(shot, rng, cam, target, n, dist, spread, height, sexes=True, anims=("glide", "glide", "fly"), avoid=None):
    """n Pteranodons scattered in front of the camera: dist (near, far), spread = half-width at the far end,
    height (low, high) relative to the camera."""
    f, r, u = frame(cam, target)
    for i in range(n):
        d = float(rng.uniform(*dist))
        x = float(rng.uniform(-1, 1)) * spread * d / dist[1]
        y = float(rng.uniform(*height))
        p = np.array(cam) + f * d + r * x + np.array([0, y, 0])
        v = p - np.array(cam)
        if avoid and avoid(v @ r / (v @ f), v @ u / (v @ f)):
            continue
        shot.add(PTERO, anims[i % len(anims)], float(rng.uniform(0, 1)), tuple(p), float(rng.uniform(0, 360)),
                 roll=float(rng.uniform(-28, 28)), ground=False, sex="female" if sexes and i % 2 else "male")


def c_familia(W=1920, H=1080):
    """Concept 1: sunset straight ahead over the Inland Sea, a T. rex family on the cliff edge against the sun, the
    whole colony wheeling over the water, light shafts through the sea haze."""
    world, coast, height, top_y, rng, topmap = chalk_coast()
    rz = envf("RZ", 206)
    rx = edge(topmap, coast, rz) + 2.5
    ry = top_y(rx, rz)
    cam = (rx + envf("CX", 24), ry + envf("CY", 3), rz + envf("CZ", 18))
    target = (rx - 40, ry + envf("TY", 3), rz - envf("TZ", 14))
    open_view = cenas.clear_of((cam[0], cam[2]), (rx - 10, rz - 4), 9)
    plant(world, rng, topmap, 4000, lambda x, z: math.hypot(x - rx, z - rz) > 7,
          ["cretaceous_grass"] * 5 + ["bracken", "clubmoss", "horsetail", "royal_fern"])
    for _ in range(30):
        z = int(rng.uniform(150, 290))
        x = int(coast(z) + rng.uniform(14, 60))
        if (x, z) in topmap and math.hypot(x - rx, z - rz) > 14 and open_view(x, z):
            vx.araucaria(world, x, topmap[(x, z)] + 1, z, int(rng.uniform(12, 21)), rng)
    shot = Shot(world)
    shot.add(REX, "roar", envf("RT", 0.42), (rx, ry, rz), envf("RYAW", 150))
    for dz, dx, anim, t, yaw, size in ((-7, 1.5, "call", 0.3, 95, 0.42), (5, 2.5, "idle", 0.6, 60, 0.33)):
        jz = rz + dz
        jx = edge(topmap, coast, jz) + dx
        shot.add(REX, anim, t, (jx, top_y(jx, jz), jz), yaw, size=size, sex="female" if dz > 0 else "male")
    swarm(shot, rng, cam, target, int(envf("NP", 34)), (30, 170), 90, (-12, 30))
    sun = sun_from(cam, target, envf("SUNYAW", -6), envf("SUNEL", 4))
    return render(shot, W, H, cam, target, envf("FOV", 42), sun, FIRE, math.dist(cam, (rx, ry + 3, rz)),
                  envf("FSTOP", 5.6), ((rx - 80, 70, rz), (400, 40, 400)))


SCENES.update({"familia": c_familia})


def c_ataque(W=1920, H=1080):
    """Concept 2: the T. rex charges into the colony resting on the beach; the Pteranodons burst into the air all
    around the camera, low sun behind the rex."""
    rz = envf("RZ", 200)
    world, coast, height, rng = beach_world(rz, envf("RXO", 3))
    rx = coast(rz) + envf("RXO", 3)
    gy = lambda x, z: max(61.0, int(round(height(x, z))) + 1.0)  # noqa: E731
    shot = Shot(world)
    cam = (rx + envf("CX", -11), envf("CY", 62.4), rz + envf("CZ", 17))
    target = (rx + envf("TX", -6), envf("TY", 66.5), rz + envf("TZ", -2))
    shot.add(REX, ENV("RANIM", "attack"), envf("RT", 0.38), (rx, gy(rx, rz), rz), envf("RYAW", 100))
    # the colony flees from the rex toward the sea (camera left): the nearest still on the sand opening the wings,
    # the rest already up, all seen side-on
    for i in range(int(envf("NG", 4))):
        x, z = rx - float(rng.uniform(4, 11)), rz + float(rng.uniform(-4, 6))
        shot.add(PTERO, "takeoff", float(rng.uniform(0.25, 0.5)), (x, gy(x, z), z), float(rng.uniform(75, 110)),
                 sex="female" if i % 2 else "male")
    for i in range(int(envf("NA", 22))):
        x = rx - float(rng.uniform(5, 40))
        z = rz + float(rng.uniform(-14, 9))
        y = 62 + float(rng.uniform(2, 16)) * (1 + (rx - x) / 40)
        shot.add(PTERO, ("fly", "fly", "glide")[i % 3], float(rng.uniform(0, 1)), (x, y, z),
                 float(rng.uniform(70, 140)), roll=float(rng.uniform(-25, 25)), ground=False,
                 sex="female" if i % 2 else "male")
    sun = sun_from(cam, target, envf("SUNYAW", -65), envf("SUNEL", 10))
    return render(shot, W, H, cam, target, envf("FOV", 50), sun, FIRE, math.dist(cam, (rx, 63, rz)),
                  envf("FSTOP", 4.0), ((rx - 20, 70, rz - 20), (300, 22, 300)))


def c_duelo(W=1920, H=1080):
    """Concept 3: two adult T. rex face off on the beach at sunset, roaring; seen from the edge of the forest, the
    sun sets over the sea right between them and the colony circles above the water."""
    rz = envf("RZ", 196)
    back = envf("CX", 29)
    keep = lambda x, z: abs(z - rz) > envf("CORR", 11)  # noqa: E731  (a corridor through the trees for the camera)
    world, coast, height, rng = beach_world(rz, envf("RXO", 6), keep)
    gy = lambda x, z: max(61.0, int(round(height(x, z))) + 1.0)  # noqa: E731
    shot = Shot(world)
    mx, mz = coast(rz) + envf("RXO", 6), rz
    gap = envf("GAP", 7.2)
    cx = mx + back
    cam = (cx, gy(cx, mz) + envf("CY", 1.7), mz)
    target = (mx - 30, envf("TY", 66.0), mz)
    for side, anim, t, sex, dyaw in ((1, ENV("AANIM", "roar_loud"), envf("AT", 0.35), "male", envf("AYAW", -16)),
                                     (-1, ENV("BANIM", "threat"), envf("BT", 0.45), "female", envf("BYAW", 16))):
        z = mz + side * gap
        x = coast(z) + envf("RXO", 6)
        # side +1 stands at +z and faces -z (yaw 0), side -1 faces +z (yaw 180); dyaw turns both toward the camera
        shot.add(REX, anim, t, (x, gy(x, z), z), (0 if side > 0 else 180) + side * dyaw, sex=sex)
    # keep the sky above the sun clear for the title (screen tangents: x across, y up)
    swarm(shot, rng, cam, target, int(envf("NP", 60)), (45, 170), 80, (4, 34),
          avoid=lambda sx, sy: abs(sx) < 0.36 and sy > 0.1)
    sun = sun_from(cam, target, envf("SUNYAW", 0), envf("SUNEL", 1.2))
    look = dict(FIRE, fog_scale=envf("FOGS", 0.03), fog_aniso=envf("FANI", 0.7), sky_strength=envf("SKYS", 0.75),
                top=(0.07, 0.07, 0.20), mid=(0.50, 0.20, 0.24), hor=(1.0, 0.48, 0.16), glow=(1.0, 0.46, 0.12),
                ripple=envf("RIP", 1.0), ripple_scale=envf("RIPS", 0.5), water_rough=envf("WRO", 0.03), glow_gain=envf("GLOWG", 1.0), clouds=envf("CLOUDS", 0.9),
                agx=ENV("AGX", "AgX - Medium High Contrast"), sun_disc_gain=envf("SDG", 80.0))
    return render(shot, W, H, cam, target, envf("FOV", 35), sun, look, math.dist(cam, (mx, 64, mz)),
                  envf("FSTOP", 5.6), ((mx - 60, 70, mz), (400, 22, 400)))


SCENES.update({"ataque": c_ataque, "duelo": c_duelo})


def c_tempestade(W=1920, H=1080):
    """Concept 4: a storm over the Inland Sea, one break in the clouds lights the T. rex roaring on the cliff edge
    while the colony is blown past it."""
    os.environ.setdefault("LOOK", "storm")
    os.environ.setdefault("SUN", "-0.55,0.42,0.35")
    return falesia(W, H)


SCENES["tempestade"] = c_tempestade


# ------------------------------------------------------------------ round 3 (Rodrigo 18:23Z: fewer animals, minimalist, mood: "neblina no meio da
# floresta e um trex de fundo")
# what a shader pack adds to the materials: pixel relief, leaves that glow against the sun, a sheen on the skin
SHADERS = dict(tex_bump=envf("TBUMP", 0.35), tex_bump_dist=0.02, leaf_trans=envf("LEAFT", 0.4),
               creature_bump=envf("CBUMP", 0.6), creature_rough=envf("CROUGH", 0.5), creature_spec=envf("CSPEC", 0.5))

FOREST = dict(top=(0.28, 0.34, 0.38), mid=(0.40, 0.46, 0.48), hor=(0.54, 0.60, 0.58), glow=(0.95, 0.85, 0.65),
              sun_col=(1.30, 1.06, 0.76), sky_amb=(0.34, 0.40, 0.44), gnd_amb=(0.16, 0.18, 0.17),
              fog_col=(0.52, 0.60, 0.62), fog_density=0.020, fog_height=72, water_deep=(0.06, 0.10, 0.10),
              clouds=0.0, sun_size=0.0, sky_strength=envf("SKYS", 1.0), sun_strength=envf("SUNS", 16.0),
              fill=envf("FILL", 0.5), fog_scale=envf("FOGS", 1.3), fog_aniso=envf("FANI", 0.8),
              glow_gain=envf("GLOWG", 0.8), sun_angle=1.0, agx=ENV("AGX", "AgX - Medium High Contrast"),
              **SHADERS)


def post(img, bloom=0.3):
    """The glow a shader pack gives bright light (sun shafts, lit fog)."""
    return cenas.bloom(img, envf("BLOOMT", 190), int(24 * img.size[0] / 1920) or 1, envf("BLOOM", bloom))


def fog_forest(seed, cam_xz, subj_xz, lane, gap, trees=330, ferns=9000, nx=200, nz=220):
    """The misty dawn redwood forest: rolling litter and grass, giant conifers kept out of the lane from the camera
    to the subject and out of a clearing around it, ferns and horsetails underneath."""
    rng = np.random.default_rng(seed)
    hn = noise2d(nz, nx, 30, rng, 4)
    height = lambda x, z: 64 + hn[int(z) % nz, int(x) % nx] * 2.0  # noqa: E731
    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, under="soil",
               top_fn=lambda x, z: "litter" if hn[z % nz, x % nx] > envf("LITTER", 0.35) else "grass")
    (cx, cz), (rx, rz) = cam_xz, subj_xz
    gy = lambda x, z: int(round(height(x, z))) + 1  # noqa: E731
    keep = cenas.clear_of((cx, cz), (rx, rz), lane)
    for _ in range(trees):
        x, z = int(rng.uniform(4, nx - 4)), int(rng.uniform(4, nz - 4))
        if not keep(x, z) or math.hypot(x - rx, z - rz) < gap or math.hypot(x - cx, z - cz) < 3:
            continue
        big = rng.random() < 0.7
        vx.conifer(world, x, gy(x, z), z, int(rng.uniform(28, 40) if big else rng.uniform(16, 24)), rng, thick=big)
    kinds = ["royal_fern"] * 5 + ["bracken"] * 3 + ["tall_bracken"] * 2 + ["horsetail", "tall_horsetail", "clubmoss"]
    for _ in range(ferns):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks and math.hypot(x - rx, z - rz) > 3 \
                and math.hypot(x - cx, z - cz) > envf("CLEARC", 2.5):
            kind = kinds[int(rng.integers(len(kinds)))]
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.7, 2.3) if kind.startswith("tall_") else rng.uniform(0.9, 1.3)))
    return world, gy


def c_floresta(W=1920, H=1080):
    """Morning fog in a dawn redwood forest: shafts of sun fall between the trunks and, far back in the mist, the
    T. rex walks out of the gloom toward the camera. Ferns in front, nothing else."""
    cx, cz = 100.5, 190.5
    rx, rz = 100 + envf("RX", -2), 190 - envf("RD", 24)
    world, gy = fog_forest(int(envf("SEED", 5)), (cx, cz), (rx, rz), envf("LANE", 5.5), envf("GAPR", 12),
                           int(envf("TREES", 330)))
    shot = Shot(world)
    shot.add(REX, ENV("RANIM", "walk"), envf("RT", 0.3), (rx, gy(rx, rz), rz), envf("RYAW", 222))
    cam = (cx, gy(cx, cz) + envf("CY", 2.2), cz)
    target = (rx + envf("TX", 0), gy(rx, rz) + envf("TY", 4), rz)
    # sun high and from behind the forest, slightly to one side: shafts come down through the canopy toward us
    sun = sun_from(cam, target, envf("SUNYAW", 25), envf("SUNEL", 22))
    img = render(shot, W, H, cam, target, envf("FOV", 44), sun, FOREST, math.dist(cam, (rx, 66, rz)) * envf("FOCK", 0.35),
                 envf("FSTOP", 2.8), ((rx, 80, rz), (220, 44, 220)), exposure=envf("EXPO", 0.3))
    return post(img)


def c_espreita(W=1920, H=1080):
    """Close on the T. rex stalking through the ferns of the misty forest, head low, one shaft of sun on its face;
    behind it only fog and trunks."""
    cx, cz = 100.5, 190.5
    rx, rz = 100 + envf("RX", 4), 190 - envf("RD", 15)
    world, gy = fog_forest(int(envf("SEED", 5)), (cx, cz), (rx, rz), envf("LANE", 4.0), envf("GAPR", 14),
                           int(envf("TREES", 330)), int(envf("FERNS", 14000)))
    ryaw = envf("RYAW", 125)
    shot = Shot(world)
    ranim, rt = ENV("RANIM", "stalk"), envf("RT", 0.15)
    shot.add(REX, ranim, rt, (rx, gy(rx, rz), rz), ryaw)
    # the head = the front 1.5 blocks of the posed model along its facing
    v, _ = gk.quads(REX, ranim, rt, pos=(rx, gy(rx, rz), rz), yaw=ryaw)
    ahead = v[:, 0] * -math.sin(math.radians(ryaw)) + v[:, 2] * -math.cos(math.radians(ryaw))
    head = tuple(v[ahead > ahead.max() - 1.5, :3].mean(0) + (0, envf("TY", 0), 0))
    cam = (cx + envf("CX", 0), gy(cx, cz) + envf("CY", 2.3), cz)
    target = (head[0] + envf("TX", -1.0), head[1] - envf("TDY", 0.5), head[2])
    sun = sun_from(cam, target, envf("SUNYAW", -20), envf("SUNEL", 40))
    look = dict(FOREST, fill=envf("FILL", 0.9))
    if envf("SHAFT", 1):
        # a shaft of sun on the face, from high on the camera's left, through a gap in the canopy
        src = (head[0] + envf("SHX", -7), head[1] + envf("SHY", 16), head[2] + envf("SHZ", 5))
        look["spots"] = [(src, head, envf("SHE", 90000), envf("SHA", 9), (1.0, 0.86, 0.62))]
    img = render(shot, W, H, cam, target, envf("FOV", 38), sun, look, math.dist(cam, head), envf("FSTOP", 2.0),
                 ((rx, 80, rz), (220, 44, 220)), exposure=envf("EXPO", 0.3))
    return post(img)


SCENES["espreita"] = c_espreita


RAPTOR = "velociraptor"
NIGHT = dict(FOREST, top=(0.04, 0.06, 0.12), mid=(0.10, 0.14, 0.24), hor=(0.20, 0.26, 0.38), glow=(0.55, 0.62, 0.80),
             sun_col=(0.70, 0.80, 1.05), sky_amb=(0.10, 0.13, 0.22), gnd_amb=(0.05, 0.06, 0.08),
             fog_col=(0.30, 0.36, 0.48), sun_strength=envf("SUNS", 2.2), fill=envf("FILL", 0.5),
             glow_gain=envf("GLOWG", 0.6), square_sun=envf("SQS", 0.03), sun_disc_gain=envf("SDG", 12.0),
             sun_disc_col=(0.85, 0.90, 1.0), sun_halo=envf("HALO", 1.5))


def face_to(src, dst):
    """Yaw that turns a model at src to face dst (yaw 0 faces -Z)."""
    return math.degrees(math.atan2(-(dst[0] - src[0]), -(dst[2] - src[2])))


def c_carcaca(W=1920, H=1080):
    """A pack of Velociraptors on a fallen T. rex in the misty forest: two tear at the carcass, one stands on it and
    screeches, one comes in low past the camera. NIGHT=1 = under a square moon."""
    os.environ.setdefault("CLEARC", "7")  # no ferns right in front of the lens
    cx, cz = 100.5, 190.5
    kx, kz = 100 + envf("KX", 2), 190 - envf("KD", 12)
    world, gy = fog_forest(int(envf("SEED", 5)), (cx, cz), (kx, kz), envf("LANE", 5.0), envf("GAPR", 15),
                           int(envf("TREES", 330)), int(envf("FERNS", 5000)))
    shot = Shot(world)
    g = gy(kx, kz)
    kyaw = envf("KYAW", 110)  # the carcass lies across the view
    kanim, kt = ENV("KANIM", "death"), envf("KT", 0.99)
    shot.add(REX, kanim, kt, (kx, g, kz), kyaw)
    v, _ = gk.quads(REX, kanim, kt, pos=(kx, g, kz), yaw=kyaw)
    centre = v[:, :3].mean(0)

    def top_at(x, z, r=0.8):
        near = v[(np.abs(v[:, 0] - x) < r) & (np.abs(v[:, 2] - z) < r)]
        return float(near[:, 1].max()) if len(near) else g

    # feeders on the near side of the belly, the screecher on the flank, the last one in front of the camera
    f = np.subtract((cx, 0, cz), centre)
    f[1] = 0
    f /= np.linalg.norm(f)
    side = np.array([-f[2], 0, f[0]])
    rel = v[:, :3] - centre

    def edge(b):
        """How far toward the camera the carcass reaches at offset b along its length."""
        near = rel[np.abs(rel @ side - b) < 0.6]
        return float((near @ f).max()) if len(near) else 0.0

    for k, (a, b, anim, t) in enumerate([(0.9, -1.2, "eat", 0.3), (0.9, 1.6, "eat", 0.7), (2.0, 3.4, "sniff", 0.4)]):
        p = centre + f * (edge(b) + a) + side * b
        p = (float(p[0]), gy(p[0], p[2]), float(p[2]))
        shot.add(RAPTOR, ENV(f"A{k}", anim), t, p, face_to(p, centre) + envf(f"Y{k}", 0), sex="female" if k % 2 else "male")
    top = centre + side * envf("TOPS", -0.6)
    tp = (float(top[0]), top_at(top[0], top[2]), float(top[2]))
    shot.add(RAPTOR, ENV("ATOP", "screech"), envf("TT", 0.45), tp, face_to(tp, (cx, 0, cz)) + envf("YTOP", 25))
    cam = (cx + envf("CX", 0), gy(cx, cz) + envf("CY", 2.4), cz)
    if envf("NEAR", 1):
        q = in_view(cam, (centre[0], g + 1.5, centre[2]), envf("ND", 5.5), envf("NX", -3.2), 0)
        q = (q[0], gy(q[0], q[2]), q[2])
        shot.add(RAPTOR, "stalk", 0.3, q, face_to(q, centre) + 10)
    target = (centre[0] + envf("TX", -1), g + envf("TY", 1.6), centre[2])
    look = dict(NIGHT if envf("NIGHT", 0) else FOREST, fill=envf("FILL", 0.7))
    sun = sun_from(cam, target, envf("SUNYAW", -25), envf("SUNEL", 30 if not envf("NIGHT", 0) else 14))
    if envf("SHAFT", 1) and not envf("NIGHT", 0):
        src = (tp[0] + envf("SHX", -6), tp[1] + envf("SHY", 18), tp[2] + envf("SHZ", 4))
        look["spots"] = [(src, (centre[0], g + 2, centre[2]), envf("SHE", 120000), envf("SHA", 14), (1.0, 0.86, 0.62))]
    img = render(shot, W, H, cam, target, envf("FOV", 42), sun, look, math.dist(cam, centre), envf("FSTOP", 2.8),
                 ((kx, 80, kz), (220, 44, 220)), exposure=envf("EXPO", 0.3 if not envf("NIGHT", 0) else 0.8))
    return post(img)


SCENES["carcaca"] = c_carcaca


# the game has no "lying dead" pose (death ends propped on legs and wingtips, then the game tips the body on its side),
# so the carcass is the glide pose laid on the sand: wings dropped flat, one folded at the wrist, neck fallen sideways
CARCASS = {k: tuple(v) for k, v in __import__("json").loads(ENV("CARC", __import__("json").dumps({
    "neck1": (15, 45, 0), "neck2": (-5, 15, 0), "head": (0, 0, 60), "jaw": (20, 0, 0), "arm_l": (0, 0, -14),
    "arm_r": (0, 0, 14), "forearm_r": (0, -25, 0), "thigh_l": (20, 0, 20), "thigh_r": (20, 0, -10),
    "shin_l": (-40, 0, 0), "shin_r": (-40, 0, 0)}))).items()}
CARCASS_REST = ("body",)  # the belly on the sand; wingtips and toes sink in a little


def c_praia_carcaca(W=1920, H=1080):
    """Afternoon on the beach of the Inland Sea: a Pteranodon lies dead on the sand, wings spread, a dark stain
    under it, and a pack of Velociraptors is at it: two tear at the neck and the wing, one screeches from on top,
    one comes in. Daylight from behind the camera, so sand, sea and the animals all read."""
    rz = envf("RZ", 196)
    world, coast, height, rng = beach_world(rz, envf("KXO", 5))
    gy = lambda x, z: max(61.0, int(round(height(x, z))) + 1.0)  # noqa: E731
    kx = coast(rz) + envf("KXO", 5)
    shot = Shot(world)
    kyaw = envf("KYAW", 240)
    k = (kx, gy(kx, rz), rz)
    kk = dict(pos=k, yaw=kyaw, sex="female", tweak=CARCASS, rest=CARCASS_REST)
    shot.add(PTERO, "glide", 0.3, k, kyaw, sex="female", tweak=CARCASS, rest=CARCASS_REST)
    body = gk.quads(PTERO, "glide", 0.3, only=("body",), **kk)[0][:, :3]
    centre = body.mean(0)
    # blood soaked into the sand under the body and by the torn neck
    neck = gk.quads(PTERO, "glide", 0.3, only=("neck1", "neck2"), **kk)[0][:, :3].mean(0)
    decal(shot, (centre[0], k[1], centre[2]), (envf("STW", 5.0), envf("STD", 3.4)), stain_texture(1), kyaw + 10)
    decal(shot, (neck[0], k[1], neck[2]), (2.4, 1.8), stain_texture(2), kyaw + 70, 0.035)
    # the waterline: first dry column from the sea at each row
    tops = {}
    for (x, y, z) in world.blocks:
        if y > tops.get((x, z), -99):
            tops[(x, z)] = y

    def wline(z):
        x = int(coast(z)) - 14
        while tops.get((x, int(z)), 0) < 60:
            x += 1
        return float(x)
    foam_line(shot, wline, rz - 60, rz + 60)
    cam = (kx + envf("CX", 7), gy(kx + envf("CX", 7), rz + envf("CZ", 4)) + envf("CY", 2.6), rz + envf("CZ", 4))

    def feed(part, side, anim, t, sex, reach=1.3):
        """A raptor with its snout on a part of the carcass, coming at it from `side` (a horizontal vector)."""
        pts = gk.quads(PTERO, "glide", 0.3, only=part, **kk)[0][:, :3]
        tgt = pts.mean(0)
        d = np.array((side[0], 0.0, side[1]))
        d /= np.linalg.norm(d)
        p = tgt + d * reach
        p = (float(p[0]), gy(p[0], p[2]), float(p[2]))
        shot.add(RAPTOR, anim, t, p, face_to(p, tgt), sex=sex)
        return p

    tocam = np.subtract(cam, centre)
    tocam[1] = 0
    tocam /= np.linalg.norm(tocam)
    side = np.array((-tocam[2], tocam[0]))
    tc = np.array((tocam[0], tocam[2]))
    feed(("neck1", "neck2"), tc * envf("N0A", 0.8) + side * envf("N0B", 0.6), "eat", envf("E0", 0.35), "male")
    feed(("mem_arm_l", "mem_forearm_l"), tc * envf("N1A", 1.0) + side * envf("N1B", -0.5), "eat", envf("E1", 0.75),
         "female")
    p = centre + np.array((tocam[0], 0, tocam[2])) * envf("P2A", 2.0) + np.array((side[0], 0, side[1])) * envf("P2B", 3.5)
    p = (float(p[0]), gy(p[0], p[2]), float(p[2]))
    shot.add(RAPTOR, "stalk", 0.4, p, face_to(p, centre), sex="female")
    feed(("mem_hand_r", "mem_forearm_r"), tc * envf("N3A", -0.6) + side * envf("N3B", -0.8), "eat", 0.55, "male")
    # the screecher stands on the body and calls toward the camera
    sp = centre + np.array((tocam[0], 0, tocam[2])) * envf("SA", 0.0)
    near = body[(np.abs(body[:, 0] - sp[0]) < 0.5) & (np.abs(body[:, 2] - sp[2]) < 0.5)]
    sy = float(near[:, 1].max()) if len(near) else float(body[:, 1].max())
    sp = (float(sp[0]), sy, float(sp[2]))
    shot.add(RAPTOR, ENV("STOP", "screech"), envf("ST", 0.45), sp, face_to(sp, cam) + envf("SYAW", 30))
    target = (centre[0] + envf("TX", 0), centre[1] + envf("TY", 0.7), centre[2] + envf("TZ", 0))
    look = dict(GOLDEN, fog_scale=envf("FOGS", 0.03), **SHADERS)
    sun = sun_from(cam, target, envf("SUNYAW", 200), envf("SUNEL", 38))
    img = render(shot, W, H, cam, target, envf("FOV", 42), sun, look, math.dist(cam, centre), envf("FSTOP", 5.6),
                 ((kx, 70, rz), (300, 24, 300)), exposure=envf("EXPO", 0.0))
    return post(img, 0.25)


SCENES["praia_carcaca"] = c_praia_carcaca


def decal(shot, centre, size, image, yaw=0.0, lift=0.03):
    """A flat picture lying on the ground (a stain, a foam line): one quad, cut out by the image's alpha."""
    c, s_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    hx, hz = size[0] / 2, size[1] / 2
    pts = [(-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz)]
    cs = [(centre[0] + x * c - z * s_, centre[1] + lift, centre[2] + x * s_ + z * c) for x, z in pts]
    verts = gl.quad_verts(cs, [(0, 0), (1, 0), (1, 1), (0, 1)], (0, 1, 0), 1.0)
    shot.meshes.append(gl.Mesh(np.array(verts, np.float32), image))


def stain_texture(seed=0, n=32):
    """Blood soaked into the sand, in pixels: a dark red blotch with a few drops around it."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    r = np.hypot((xx - n / 2) / (n * 0.42), (yy - n / 2) / (n * 0.30))
    edge = noise2d(n, n, 6, rng, 2)
    blot = r + edge * 0.35 < 0.75
    drops = (rng.random((n, n)) < 0.03) & (r < 1.0)
    a = np.zeros((n, n, 4), np.uint8)
    col = np.array((96, 22, 18)) * (1 + rng.normal(0, 0.08, (n, n, 1)))
    a[..., :3] = np.clip(col, 0, 255)
    a[..., 3] = np.where(blot | drops, 235, 0)
    a[blot & (r + edge * 0.35 < 0.4), :3] = (70, 14, 12)
    return Image.fromarray(a, "RGBA")


def foam_line(shot, wline, z0, z1, wl=60.93, width=1.6, seed=0):
    """White foam where the waves run up the sand: broken pixel strips along the waterline wline(z)."""
    rng = np.random.default_rng(seed)
    for z in range(int(z0), int(z1)):
        a = np.zeros((8, 16, 4), np.uint8)
        on = rng.random((8, 16)) < np.linspace(0.05, 0.9, 16)[None, :] ** 1.5
        a[on] = (238, 242, 238, 235)
        decal(shot, (wline(z) - width / 2 + 0.3, wl, z + 0.5), (width, 1.0), Image.fromarray(a, "RGBA"), 0.0, 0.0)


def ring_texture(seed=0, n=32):
    """A pixel sound ring: a broken circle 1-2 px thick, brighter on the inside edge."""
    rng = np.random.default_rng(seed)
    a = np.zeros((n, n, 4), np.uint8)
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    r = np.hypot(xx - n / 2, yy - n / 2)
    ang = np.arctan2(yy - n / 2, xx - n / 2)
    gaps = np.sin(ang * rng.integers(3, 6) + rng.uniform(0, 6)) > -0.75
    ring = (np.abs(r - (n / 2 - 2.5)) < 1.0 + (rng.random((n, n)) < 0.25)) & gaps
    inner = ring & (r < n / 2 - 2.5)
    a[ring] = (255, 236, 200, 200)
    a[inner] = (255, 250, 236, 255)
    return Image.fromarray(a, "RGBA")


def sound_rings(shot, mouth, direction, n=4, start=1.2, step=1.6, r0=0.9, grow=0.75, emit=6.0):
    """The roar made visible, Minecraft-style: flat pixel rings flying out of the mouth, bigger and fainter."""
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    u = np.cross(d, (0, 1, 0))
    u = u / np.linalg.norm(u) if np.linalg.norm(u) > 1e-6 else np.array((1.0, 0, 0))
    w = np.cross(u, d)
    for i in range(n):
        c = np.asarray(mouth) + d * (start + step * i)
        r = r0 + grow * i
        cs = [tuple(c + (-u + w) * r), tuple(c + (u + w) * r), tuple(c + (u - w) * r), tuple(c + (-u - w) * r)]
        img = ring_texture(i)
        fade = 1.0 - i / (n + 1)
        a = np.asarray(img).copy()
        a[..., 3] = (a[..., 3] * fade).astype(np.uint8)
        verts = gl.quad_verts(cs, [(0, 0), (1, 0), (1, 1), (0, 1)], tuple(d), 1.0)
        m = gl.Mesh(np.array(verts, np.float32), Image.fromarray(a, "RGBA"))
        m.emit = emit * fade
        shot.meshes.append(m)


def radial_blur(img, centre, strength=0.04, steps=8):
    """Zoom blur out of a point (the roar's punch), strongest at the frame's edges."""
    W, H = img.size
    acc = np.zeros((H, W, 3), float)
    for i in range(steps):
        k = 1 + strength * i / steps
        im = img.resize((int(W * k), int(H * k)), Image.BILINEAR)
        ox, oy = int(centre[0] * (k - 1)), int(centre[1] * (k - 1))
        acc += np.asarray(im.crop((ox, oy, ox + W, oy + H)), float)
    blur = acc / steps
    yy, xx = np.mgrid[0:H, 0:W]
    m = (np.hypot(xx - centre[0], yy - centre[1]) / math.hypot(W, H) * 2.2).clip(0, 1)[..., None]
    out = np.asarray(img, float) * (1 - m) + blur * m
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def c_grito(W=1920, H=1080):
    """A storm over the Inland Sea: the T. rex stands on the edge of the chalk cliff and roars out to sea. The roar
    is made visible: pixel sound rings, dust blown off the cliff top, chalk crumbling off the edge, the frame shaking.
    Camera up on the cliff top in front of it, looking a little down so the feet on the edge show."""
    world, coast, height, top_y, rng, topmap = chalk_coast()
    rz = envf("RZ", 150)
    rx = edge(topmap, coast, rz) + envf("RXO", 4)
    g = top_y(rx, rz)
    ryaw = envf("RYAW", 120)  # facing the sea (-X), turned a little toward the camera
    ranim, rt = ENV("RANIM", "roar"), envf("RT", 0.5)
    shot = Shot(world)
    shot.add(REX, ranim, rt, (rx, g, rz), ryaw)
    v, _ = gk.quads(REX, ranim, rt, pos=(rx, g, rz), yaw=ryaw)
    fx, fz = -math.sin(math.radians(ryaw)), -math.cos(math.radians(ryaw))
    ahead = v[:, 0] * fx + v[:, 2] * fz
    snout = v[ahead > ahead.max() - 0.6, :3].mean(0)
    back = v[(ahead > ahead.max() - 3.0) & (ahead < ahead.max() - 1.8), :3].mean(0)
    rd = snout - back
    rd[1] += envf("RUP", 0.15)
    sound_rings(shot, snout, rd, int(envf("RINGS", 4)), emit=envf("REMIT", 3.0))
    ccx, ccz = rx + envf("CX", 2), rz + envf("CZ", 22)
    # SEA=1: the camera hangs out over the sea at the height of the cliff top, looking back at the rex on the edge
    cam = (ccx, (g if ENV("SEA", "") else top_y(ccx, ccz)) + envf("CY", 4.5), ccz)
    shot.debris(rng, (rx - 2, g - 6, rz), int(envf("CHALK", 60)), 4, (-14, 3), ["chalk", "chalk_pebbles"], (0.1, 0.3))
    shot.debris(rng, (rx, g, rz), int(envf("PEBBLES", 80)), 4, (0.1, 1.2), ["dirt", "gravel", "grass_top"], (0.08, 0.16))
    target = (snout[0] + envf("TX", -1), snout[1] + envf("TY", -3), snout[2])
    look = dict(STORM, fill=envf("FILL", 0.7), fog_scale=envf("FOGS", 0.03), glow_gain=envf("GLOWG", 0.8),
                sky_strength=envf("SKYS", 0.7), **SHADERS)
    look["dust"] = ((rx, g + 1.2, rz), (12, 2.5, 12), envf("DUSTD", 0.08), (0.75, 0.72, 0.66))
    sun = sun_from(cam, target, envf("SUNYAW", -100), envf("SUNEL", 20))
    img = render(shot, W, H, cam, target, envf("FOV", 48), sun, look, math.dist(cam, snout), envf("FSTOP", 4.0),
                 ((rx, 70, rz), (300, 30, 300)), exposure=envf("EXPO", 0.0))
    img = post(img, 0.35)
    # where the mouth lands on screen, for the zoom blur
    f, r, u = frame(cam, target)
    d = snout - np.asarray(cam)
    th = math.tan(math.radians(envf("FOV", 48)) / 2)
    sx = W / 2 + (d @ r) / (d @ f) / th * H / 2
    sy = H / 2 - (d @ u) / (d @ f) / th * H / 2
    img = radial_blur(img, (sx, sy), envf("ZOOM", 0.02))
    return shake(img, envf("SHAKE", 2))


SCENES["grito"] = c_grito


# dusk over the lava field: a cold blue sky and a cold moon-like key from behind, against the warm lava, so the two
# colours separate instead of everything going brown
VOLCANO = dict(FIRE, top=(0.03, 0.05, 0.12), mid=(0.09, 0.11, 0.24), hor=(0.42, 0.24, 0.26), glow=(1.0, 0.45, 0.18),
               sun_col=envv("SUNC", "0.55,0.68,1.0"), sky_amb=(0.16, 0.20, 0.34), gnd_amb=(0.12, 0.06, 0.04),
               fog_col=(0.30, 0.22, 0.26), clouds=0.8, sky_strength=envf("SKYS", 0.8), sun_strength=envf("SUNS", 5.0),
               fill=envf("FILL", 0.7), glow_gain=envf("GLOWG", 1.2), square_sun=0.0, agx=ENV("AGX", "AgX - Punchy"))


def lava_field(seed=3, nx=200, nz=230, clear=(), outcrop=None, fissure=None):
    """A Cretaceous volcanic plain: basalt and ash split by glowing fissures, a smoking cone in the distance.
    Returns (world, height(x, z), lava cells [(x, y, z)], crater (x, y, z))."""
    rng = np.random.default_rng(seed)
    hn = noise2d(nz, nx, 18, rng, 4)
    an = noise2d(nz, nx, 9, rng, 3)
    fn = noise2d(nz, nx, envf("CRACKS", 16), rng, 2)
    vx_, vz_ = envf("VOLX", 135), envf("VOLZ", 20)
    peak = 64 + envf("VOLH", 62)

    def cone(x, z):
        d = math.hypot(x - vx_, z - vz_)
        h = peak - d * 0.95 + hn[int(z) % nz, int(x) % nx] * 3
        if d < 9:  # the crater
            h = peak - 9 * 0.95 - (9 - d) * 0.8
        return h

    def crack(x, z):
        if fissure and abs(z - fissure(x)) < 0.75 and not rock(x, z):  # one long fissure across the foreground
            return True
        return (abs(fn[int(z) % nz, int(x) % nx]) < envf("CRACKW", 0.05) and math.hypot(x - vx_, z - vz_) > 45
                and not rock(x, z))

    cols = rng.integers(0, 2, (nz, nx))

    def rock(x, z):
        """A knob of basalt columns (outcrop = x, z, radius, height): stepped tops, one column a little off the next."""
        if not outcrop:
            return 0.0
        ox, oz, r, h = outcrop
        d = math.hypot(x - ox, z - oz)
        return 0.0 if d > r else 64 + h - int(d * h / r * 0.7) + cols[int(z) % nz, int(x) % nx] - (d > r - 1.5)

    def ground(x, z):
        return max(64 + hn[int(z) % nz, int(x) % nx] * 2.2, cone(x, z), rock(x, z))

    def height(x, z):
        return round(ground(x, z)) - 1 if crack(x, z) else ground(x, z)

    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, top="basalt", under="basalt", rock="basalt",
               top_fn=lambda x, z: "ash" if an[z % nz, x % nx] > 0.15 or math.hypot(x - vx_, z - vz_) < 40 else "basalt")
    lava = [(x, int(round(height(x, z))) + 1, z) for z in range(nz) for x in range(nx) if crack(x, z)]
    for x in range(int(vx_ - 9), int(vx_ + 10)):
        for z in range(int(vz_ - 9), int(vz_ + 10)):
            if math.hypot(x - vx_, z - vz_) < 7.5:
                lava.append((x, int(round(cone(x, z))) + 1, z))
    flows = set()  # lava running down the flanks from the crater rim
    for a0 in [float(v) for v in ENV("FLOWS", "200,235,290").split(",")]:
        a = math.radians(a0)
        for step in range(9, int(envf("FLOWL", 60))):
            a += rng.normal(0, 0.03)
            x, z = int(vx_ + math.sin(a) * step), int(vz_ + math.cos(a) * step)
            for dx in (-1, 0, 1):
                flows.add((x + dx, z))
    for (x, z) in flows:
        if 0 <= x < nx and 0 <= z < nz:
            lava.append((x, int(round(height(x, z))) + 0.18, z))  # a skin of lava just over the slope
    # charred trunks, no leaves left
    for _ in range(int(envf("TRUNKS", 26))):
        x, z = int(rng.uniform(20, nx - 20)), int(rng.uniform(70, nz - 10))
        if crack(x, z) or any(math.hypot(x - cx, z - cz) < r for cx, cz, r in clear):
            continue
        y = int(round(height(x, z))) + 1
        for k in range(int(rng.uniform(4, 11))):
            world.set(x, y + k, z, "metasequoia_log")
        if rng.random() < 0.5:
            dx, dz = ((1, 0), (-1, 0), (0, 1), (0, -1))[int(rng.integers(4))]
            world.set(x + dx, y + k - 1, z + dz, "metasequoia_log")
    return world, height, crack, lava, (vx_, peak - 9 * 0.95, vz_)


def lava_mesh(shot, cells, emit):
    """Lava as a glowing surface a little under the rim of its channel (like a Minecraft fluid)."""
    u0, v0, u1, v1 = shot.uv["lava"]
    out = []
    for (x, y, z) in cells:
        cs = [(x, y + 0.85, z + 1), (x + 1, y + 0.85, z + 1), (x + 1, y + 0.85, z), (x, y + 0.85, z)]
        out += gl.quad_verts(cs, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], (0, 1, 0), 1.0)
    m = gl.Mesh(np.array(out, np.float32), shot.atlas)
    m.emit = emit
    shot.meshes.append(m)


def c_vulcao(W=1920, H=1080):
    """Dusk on a volcanic plain: the T. rex on a basalt rise roars straight up at the ash sky, sound rings climbing
    out of its jaws; a lava river lights it from below and the volcano smokes behind. Low camera, looking up."""
    rz = envf("RZ", 150)
    rx = envf("RX", 86)
    ccx, ccz = rx + envf("CX", 5), rz + envf("CZ", 18)
    world, height, crack, lava, crater = lava_field(clear=((rx, rz, 12), (ccx, ccz, 8), ((rx + ccx) / 2, (rz + ccz) / 2, 8)),
                                                    outcrop=(rx, rz, envf("ROCKR", 7), envf("ROCKH", 3)),
                                                    fissure=lambda x: rz + envf("FISZ", 9) + 2.5 * math.sin(x / 6.0) + 1.2 * math.sin(x / 2.3))
    gy = lambda x, z: int(round(height(x, z))) + 1.0  # noqa: E731
    ryaw = envf("RYAW", 104)
    ranim, rt = ENV("RANIM", "roar_loud"), envf("RT", 0.4)
    shot = Shot(world)
    lava_mesh(shot, lava, envf("LAVAE", 2.5))
    g = max(gy(rx + dx, rz + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1))  # feet on the highest column
    shot.add(REX, ranim, rt, (rx, g, rz), ryaw)
    v, _ = gk.quads(REX, ranim, rt, pos=(rx, g, rz), yaw=ryaw)
    top = v[:, 1].max()
    snout = v[v[:, 1] > top - 0.6, :3].mean(0)
    jaw = gk.quads(REX, ranim, rt, pos=(rx, g, rz), yaw=ryaw, only=("neck", "neck1", "neck2"))[0]
    base = jaw[:, :3].mean(0) if len(jaw) else snout - np.array((0, 2.0, 0))
    rd = snout - base
    rd[1] += envf("RUP", 0.5)
    sound_rings(shot, snout, rd, int(envf("RINGS", 4)), start=envf("RSTART", 1.4), emit=envf("REMIT", 3.0))
    rng = np.random.default_rng(5)
    embers = shot.debris(rng, (rx - 6, g, rz - 8), int(envf("EMBERS", 140)), 22, (0.5, 16), ["lava"], (0.05, 0.12))
    embers.emit = envf("EMBERE", 8.0)
    shot.debris(rng, (rx, g, rz), int(envf("PEBBLES", 50)), 3.5, (0.1, 1.0), ["basalt", "volcanic_ash"], (0.08, 0.16))
    cam = (ccx, gy(ccx, ccz) + envf("CY", 1.8), ccz)
    target = (rx + envf("TX", 1.5), g + envf("TY", 3.0), rz)
    look = dict(VOLCANO, fog_scale=envf("FOGS", 0.25), **SHADERS)
    look["dust"] = (np.array(crater) + np.array((0, 68, 0)), (70, 140, 70), envf("PLUMED", 0.3), (0.20, 0.17, 0.17))
    # the fissures' glow from below, on the belly and the throat (a warm light low on the camera's side)
    src = (rx + envf("GLX", 3), g + envf("GLY", 0.3), rz + envf("GLZ", 8))
    look["spots"] = [(src, (rx, g + 4.0, rz), envf("GLOWE", 5000), envf("GLOWA", 80), (1.0, 0.42, 0.12)),
                     # the crater lights its own ash column from below
                     ((crater[0], crater[1] + 2, crater[2]), (crater[0], crater[1] + 80, crater[2]),
                      envf("CRATE", 2000000), envf("CRATA", 50), (1.0, 0.40, 0.12))]
    sun = sun_from(cam, target, envf("SUNYAW", 150), envf("SUNEL", 30))
    img = render(shot, W, H, cam, target, envf("FOV", 58), sun, look, math.dist(cam, (rx, g + 3, rz)), envf("FSTOP", 5.0),
                 ((100, 90, 115), (240, 100, 260)), exposure=envf("EXPO", 0.2))
    return post(img, envf("BLOOM", 0.45))


SCENES["vulcao"] = c_vulcao


def cave_world(seed=21, nx=170, nz=200):
    """A sunny valley of ferns and araucarias, and a limestone hill whose cave looks out over it (mouth facing -Z).
    Returns (world, ground height(x, z), cave dict)."""
    rng = np.random.default_rng(seed)
    hn = noise2d(nz, nx, 26, rng, 4)
    cn = noise2d(nz, nx, 5, rng, 2)
    hx, hz = envf("HILLX", 80), envf("HILLZ", 150)

    def ground(x, z):
        return 64 + hn[int(z) % nz, int(x) % nx] * 1.6 + max(0.0, (hz - 60 - z) * 0.12)  # far side rises gently

    def hill(x, z):
        front = max(0.0, hz - envf("MOUTH", 6) - z)  # a steep face over the mouth
        d = math.hypot((x - hx) / 1.3, max(0.0, z - hz - 30))
        return 64 + 15 - d * 0.55 - front * 3.0 + cn[int(z) % nz, int(x) % nx] * 1.5

    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, ground, top_fn=lambda x, z: "grass" if hn[z % nz, x % nx] > -0.2 else "litter")
    for x in range(int(hx - 30), int(hx + 31)):
        for z in range(int(hz - 30), nz):
            top = int(round(hill(x, z)))
            g = int(round(ground(x, z)))
            for y in range(g - 1, top + 1):
                world.set(x, y, z, ("grass" if cn[z % nz, x % nx] > 0 else "litter") if y == top else
                          "stone" if cn[(y * 7 + z) % nz, (x * 3) % nx] > 0.45 else "limestone")
    # the cave: a tunnel along -Z with a lumpy oval section, floor at y 64 (walk on 65)
    rw, rh, cy = envf("CAVEW", 4.6), envf("CAVEH", 3.4), 65.2
    z_back = int(hz + 12)
    mz = hz - envf("MOUTH", 6)
    for z in range(int(mz - 4), z_back):
        flare = 1 + envf("FLARE", 0.7) * min(1.0, max(0.0, (mz + 5 - z) / 6))  # the mouth opens up like a bell
        for x in range(int(hx - 9), int(hx + 10)):
            for y in range(64, 76):
                taper = 1.0 if z < z_back - 4 else (z_back - z) / 4
                q = ((x + 0.5 - hx) / (rw * taper * flare)) ** 2 + ((y + 0.5 - cy) / (rh * flare)) ** 2 + cn[(z * 3 + y) % nz, x % nx] * 0.15
                if q < 1 and y >= 65:
                    world.blocks.pop((x, y, z), None)
    # trees and plants in the valley, kept off the line of sight to the rex
    for _ in range(int(envf("TREES", 120))):
        x, z = int(rng.uniform(5, nx - 5)), int(rng.uniform(5, hz - 30))
        if abs(x - hx) < 14 and z > hz - 50:
            continue
        y = int(round(ground(x, z))) + 1
        if rng.random() < 0.6:
            vx.araucaria(world, x, y, z, int(rng.uniform(14, 24)), rng)
        else:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 7)), rng)
    kinds = ["cretaceous_grass"] * 5 + ["bracken", "cycad", "royal_fern", "horsetail", "clubmoss"]
    for _ in range(9000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, hz - 8))
        h = int(round(ground(x, z)))
        if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks:
            kind = kinds[int(rng.integers(len(kinds)))]
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.5, 2.0) if kind == "cycad" else rng.uniform(0.8, 1.2)))
    return world, ground, dict(x=hx, z=hz, floor=65.0, rw=rw)


def wall_block(world, x0, y, z, step):
    """First solid block walking sideways (step = -1 left, +1 right) from x0 at (y, z): the cave wall."""
    x = int(x0)
    while (x, y, z) not in world.blocks:
        x += step
    return x


def c_caverna(W=1920, H=1080):
    """From inside a cave: the T. rex cave painting on the wall, lit by a bone torch, and through the mouth, in full
    daylight, the real T. rex roaring into the cave. The roar shows in the cave itself: the torch flame laid flat,
    dust and grit falling from the roof at the mouth."""
    world, ground, cave = cave_world()
    hx, hz, fl = cave["x"], cave["z"], cave["floor"]
    pz = int(hz + envf("PAINTZ", 0))  # the painted wall starts beside the camera and runs toward the mouth
    wx = wall_block(world, hx, 65, pz, -1)
    frieze = [(0, 0, "painting_rex"), (1, -1, "painting_sun"), (0, -2, "painting_feet"), (1, -3, "painting_hand"),
              (0, -4, "painting_feet"), (0, -6, "painting_hand"), (1, 1, "painting_hand")]
    for (dy, dz, b) in frieze:
        world.set(wall_block(world, hx, 65 + dy, pz + dz, -1), 65 + dy, pz + dz, b)
    # the cave floor: worn limestone with gravel and dirt blown in from the mouth
    fr = np.random.default_rng(5)
    fn = noise2d(40, 40, 4, fr, 2)
    cn_floor = lambda x, z: fn[int(z) % 40, int(x) % 40] * 0.6
    for (x, y, z) in [k for k in world.blocks if k[1] == 64 and abs(k[0] - hx) < 8 and hz - 12 < k[2] < hz + 12]:
        if (x, 65, z) not in world.blocks:
            r = fr.random() * 0.5 + cn_floor(x, z) + (hz - z) * 0.03
            world.set(x, y, z, "gravel" if r > 0.75 else "stone" if r < -0.2 else "limestone")
    tx, tz = wx + 1, pz + int(envf("TORCHZ", 1))  # the bone torch stands on the floor next to the painting
    world.plants.append((tx, int(fl), tz, "bone_torch", 1.0))
    shot = Shot(world)
    lean = envf("FLAMEL", 0.18)  # the roar's wind lays the flame over, into the cave: a tongue of three cubes
    flame = (tx + 0.5, fl + 0.72, tz + 0.5)
    fm = []
    for k, (sz, up) in enumerate(((0.13, 0.0), (0.09, 0.07), (0.05, 0.12))):
        c = np.array(flame) + (0, up, lean * k)
        for face, (nrm, corners, _sh) in vx.FACES.items():
            cs = [tuple(c + (np.array(q) - 0.5) * (sz, sz * 1.3, sz * 1.4)) for q in corners]
            fm += gl.quad_verts(cs, [(0, 0), (1, 0), (1, 1), (0, 1)], nrm, 1.0)
    m = gl.Mesh(np.array(fm, np.float32), Image.new("RGBA", (2, 2), (255, 140, 50, 255)))
    m.emit = envf("FLAMEE", 12.0)
    shot.meshes.append(m)
    # the rex outside, roaring at the cave
    cam = (hx + envf("CX", 0.6), fl + envf("CY", 1.2), hz + envf("CZ", 3))
    rx, rz = hx + envf("RX", 3), hz + envf("RZ", -26)
    ry = ground(rx, rz)
    g = int(round(ry)) + 1.0
    shot.add(REX, ENV("RANIM", "roar"), envf("RT", 0.5), (rx, g, rz), face_to((rx, g, rz), cam) + envf("RYAW", 30))
    rng = np.random.default_rng(9)
    mz = hz - envf("GRITZ", 8)  # grit shaken off the roof at the mouth, and a little inside over the paintings
    shot.debris(rng, (hx, fl + 0.2, mz), int(envf("GRIT", 160)), 3.5, (0.2, 4.2), ["limestone", "stone", "gravel"], (0.05, 0.12))
    shot.debris(rng, (wx + 2.0, fl + 0.3, pz - 1), int(envf("GRIT2", 40)), 1.6, (0.3, 3.0), ["limestone", "gravel"], (0.03, 0.07))
    target = (hx + envf("TX", -0.6), fl + envf("TY", 1.5), hz + envf("TZ", -20))
    look = dict(GOLDEN, fog_scale=envf("FOGS", 0.03), **SHADERS)
    look["dust"] = ((hx, fl + 1.8, mz), (9, 4.0, 8), envf("DUSTD", 0.15), (0.85, 0.80, 0.70))
    look["points"] = [(flame, envf("TORCHE", 40.0), (1.0, 0.62, 0.30), 0.1)]
    sun = sun_from(cam, target, envf("SUNYAW", 150), envf("SUNEL", 40))
    img = render(shot, W, H, cam, target, envf("FOV", 60), sun, look, math.dist(cam, (rx, g + 3, rz)), envf("FSTOP", 8.0),
                 ((hx, 72, hz - 40), (220, 24, 220)), exposure=envf("EXPO", 0.0))
    return post(img, 0.3)


SCENES["caverna"] = c_caverna


def dolina_world(seed=8, n=120, R_bot=None, R_top=None):
    """A jungle sinkhole: a round limestone shaft whose walls lean in toward the top (the rim overhangs), a pool on
    the floor, leaves hanging off the lip, araucarias and tree ferns crowding the rim. Returns (world, top(x, z), info)."""
    rng = np.random.default_rng(seed)
    hn = noise2d(n, n, 20, rng, 3)
    an = rng.normal(0, 1, 64)
    sx = sz = n / 2
    rb, rt = R_bot or envf("RBOT", 12.0), R_top or envf("RTOP", 7.5)
    floor, top0 = 60, int(envf("RIM", 86))

    def top(x, z):
        return top0 + hn[int(z) % n, int(x) % n] * 1.5

    def radius(x, z, y):
        a = math.atan2(z - sz, x - sx)
        wob = sum(an[k] * math.sin((k + 2) * a + an[32 + k] * 3) for k in range(5)) * 0.18
        t = min(1.0, max(0.0, (y - floor) / (top0 - floor)))
        return (rb + (rt - rb) * t ** 1.4) * (1 + wob * 0.12)

    world = vx.World()
    vx.terrain(world, 0, 0, n, n, top, top_fn=lambda x, z: "grass" if hn[z % n, x % n] > -0.3 else "litter")
    wet = noise2d(n, n, 4, rng, 2)
    for x in range(int(sx - rb - 6), int(sx + rb + 7)):
        for z in range(int(sz - rb - 6), int(sz + rb + 7)):
            h = int(round(top(x, z)))
            d = math.hypot(x + 0.5 - sx, z + 0.5 - sz)
            for y in range(floor - 2, h + 1):
                r = radius(x + 0.5, z + 0.5, y)
                if y > floor - (1 if d < rb * 0.55 and x < sx else 0) and d < r:
                    world.blocks.pop((x, y, z), None)
                    continue
                if y == h and d >= r:
                    continue  # keep the grass top
                moss = wet[(z + y * 7) % n, (x + y * 3) % n] + (top0 - y) * 0.03 - 0.3
                world.set(x, y, z, "moss_rock" if moss > 0.35 else "stone" if wet[(y * 5) % n, (x + z) % n] > 0.5 else "limestone")
    # the pool fills the deeper half of the floor
    world.water.append((sx - rb - 1, sz - rb - 1, sx + rb + 1, sz + rb + 1, floor + 0.55))
    # leaves hanging off the lip, in curtains of uneven length
    for k in range(int(envf("HANG", 70))):
        a = rng.uniform(0, 2 * math.pi)
        y0 = int(round(top0)) - 1
        r = radius(sx, sz, y0) - 0.6
        x, z = int(sx + r * math.cos(a)), int(sz + r * math.sin(a))
        for dy in range(int(rng.uniform(2, 11))):  # crossed sprites, lighter than leaf blocks
            if (x, y0 - dy, z) not in world.blocks:
                world.plants.append((x, y0 - dy, z, "tree_fern_leaves" if k % 3 else "podocarpus_leaves", 1.0))
    # the jungle crowding the rim
    for _ in range(int(envf("TREES", 90))):
        x, z = int(rng.uniform(4, n - 4)), int(rng.uniform(4, n - 4))
        d = math.hypot(x - sx, z - sz)
        if d < rt + 3 or d > 45:
            continue
        y = int(round(top(x, z))) + 1
        if rng.random() < 0.5:
            vx.araucaria(world, x, y, z, int(rng.uniform(16, 26)), rng)
        else:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 8)), rng)
    kinds = ["cretaceous_grass"] * 4 + ["bracken", "royal_fern", "horsetail", "clubmoss", "cycad"]
    for _ in range(5000):
        x, z = int(rng.uniform(0, n)), int(rng.uniform(0, n))
        h = int(round(top(x, z)))
        if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks:
            kind = kinds[int(rng.integers(len(kinds)))]
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.5, 2.0) if kind == "cycad" else rng.uniform(0.8, 1.2)))
    # ferns on the dry floor and on ledges low down
    for _ in range(400):
        x, z = int(rng.uniform(sx - rb, sx + rb)), int(rng.uniform(sz - rb, sz + rb))
        if (x, floor, z) in world.blocks and (x, floor + 1, z) not in world.blocks:
            world.plants.append((x, floor + 1, z, ["royal_fern", "clubmoss", "horsetail"][int(rng.integers(3))], rng.uniform(0.8, 1.2)))
    return world, top, dict(x=sx, z=sz, floor=floor, rim=top0, rt=rt, rb=rb, radius=radius)


def falls_texture(seed=0, w=12, h=64):
    """A waterfall in pixels: broken white and pale-blue streaks running down, see-through between them."""
    rng = np.random.default_rng(seed)
    a = np.zeros((h, w, 4), np.uint8)
    for x in range(w):
        if rng.random() < 0.25:
            continue  # gaps between the strands
        y = int(rng.integers(h))
        while y < h * 2:
            ln = int(rng.integers(3, 14))
            c = (236, 244, 246) if rng.random() < 0.5 else (176, 206, 220)
            for k in range(ln):
                a[(y + k) % h, x] = (*c, 235)
            y += ln + int(rng.integers(2, 10))
    return Image.fromarray(a, "RGBA")


def sheet(shot, p0, p1, width, image, face_pos, emit=0.0):
    """A vertical picture hung between two points (top p0, bottom p1), turned to face face_pos: a waterfall."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = np.array(face_pos, float) - (p0 + p1) / 2
    side = np.cross((p1 - p0) / np.linalg.norm(p1 - p0), d)
    side = side / np.linalg.norm(side) * width / 2
    cs = [tuple(p0 - side), tuple(p0 + side), tuple(p1 + side), tuple(p1 - side)]
    reps = max(1.0, float(np.linalg.norm(p1 - p0)) / (width * 8))
    nrm = tuple(d / np.linalg.norm(d))
    verts = gl.quad_verts(cs, [(0, 0), (1, 0), (1, reps), (0, reps)], nrm, 1.0)
    m = gl.Mesh(np.array(verts, np.float32), image)
    if emit:
        m.emit = emit
    shot.meshes.append(m)
    return m


def c_dolina(W=1920, H=1080):
    """From the bottom of a jungle sinkhole, looking straight up: the T. rex on the overhanging rim, roaring down into
    the hole, against a disc of sky. The jungle answers: Pteranodons burst off the rim, a waterfall pours in."""
    world, top, info = dolina_world()
    sx, sz, fl, rim, rt = info["x"], info["z"], info["floor"], info["rim"], info["rt"]
    shot = Shot(world)
    cam = (sx + envf("CX", 3.0), fl + envf("CY", 1.6), sz + envf("CZ", 5.0))
    # the rex stands on the far lip, head out over the hole
    a = math.radians(envf("RANG", -100))
    rr = rt + envf("RBACK", 2.5)
    rx, rz = sx + rr * math.cos(a), sz + rr * math.sin(a)
    g = int(round(top(rx, rz))) + 1.0
    ryaw = face_to((rx, g, rz), (sx, g, sz)) + envf("RYAW", 0)
    shot.add(REX, ENV("RANIM", "roar"), envf("RT", 0.5), (rx, g, rz), ryaw, pitch=envf("RPITCH", 0))
    # a waterfall over the lip on the left, into the pool
    wa = math.radians(envf("WANG", 200))
    wr = info["radius"](sx, sz, rim - 1) + 0.2
    wx, wz = sx + wr * math.cos(wa), sz + wr * math.sin(wa)
    sheet(shot, (wx, rim + 0.6, wz), (wx + (sx - wx) * 0.12, fl + 0.6, wz + (sz - wz) * 0.12), envf("WW", 1.6),
          falls_texture(), cam)
    # Pteranodons bursting off the rim, across the sky
    rng = np.random.default_rng(int(envf("PSEED", 4)))
    for i in range(int(envf("PTEROS", 5))):
        b = rng.uniform(0, 2 * math.pi)
        p = (sx + math.cos(b) * rng.uniform(2, 12), rim + rng.uniform(6, 22), sz + math.sin(b) * rng.uniform(2, 12))
        shot.add(PTERO, "fly" if i % 2 else "glide", float(rng.uniform(0, 1)), p, float(rng.uniform(0, 360)),
                 roll=float(rng.uniform(-30, 30)), ground=False, sex="female" if i % 2 else "male")
    target = (sx + envf("TX", -1.0), rim + envf("TY", 2.0), sz + envf("TZ", -4.0))
    look = dict(GOLDEN if ENV("LOOK", "golden") == "golden" else FOREST, fog_scale=envf("FOGS", 0.3), **SHADERS)
    look["dust"] = ((wx, fl + 1.5, wz), (4, 3, 4), envf("MIST", 0.25), (0.9, 0.92, 0.94))  # spray at the foot of the falls
    sun = sun_from(cam, target, envf("SUNYAW", 160), envf("SUNEL", 62))
    img = render(shot, W, H, cam, target, envf("FOV", 70), sun, look, math.dist(cam, (rx, g + 4, rz)), envf("FSTOP", 11.0),
                 ((sx, (fl + rim) / 2, sz), (rt * 2 + 10, rim - fl + 4, rt * 2 + 10)), exposure=envf("EXPO", 0.0))
    return post(img, 0.3)


SCENES["dolina"] = c_dolina

def shake(img, amount):
    """Camera shake as a still: the frame laid over itself twice, nudged a few pixels, like a long exposure."""
    a = np.asarray(img, float)
    k = max(1, int(round(amount * img.size[0] / 1920)))
    b = np.roll(a, (-k // 2, k), (0, 1))
    c = np.roll(a, (k, -k), (0, 1))
    return Image.fromarray((a * 0.55 + b * 0.25 + c * 0.20).clip(0, 255).astype(np.uint8))


def c_rugido(W=1920, H=1080):
    """The T. rex roars in a forest clearing and the ground shakes: dust jumps off the floor round its feet, leaves and
    pebbles shake loose, the whole frame trembles. Low camera, light from behind it through the fog."""
    cx, cz = 100.5, 190.5
    rx, rz = 100 + envf("RX", 1), 190 - envf("RD", 15)
    world, gy = fog_forest(int(envf("SEED", 5)), (cx, cz), (rx, rz), envf("LANE", 5.0), envf("GAPR", 15),
                           int(envf("TREES", 330)), int(envf("FERNS", 9000)))
    rng = np.random.default_rng(int(envf("PSEED", 3)))
    g = gy(rx, rz)
    ryaw = envf("RYAW", 118)
    shot = Shot(world)
    ranim, rt = ENV("RANIM", "roar"), envf("RT", 0.5)
    shot.add(REX, ranim, rt, (rx, g, rz), ryaw)
    v, _ = gk.quads(REX, ranim, rt, pos=(rx, g, rz), yaw=ryaw)
    ahead = v[:, 0] * -math.sin(math.radians(ryaw)) + v[:, 2] * -math.cos(math.radians(ryaw))
    head = v[ahead > ahead.max() - 1.5, :3].mean(0)
    cam = (cx + envf("CX", -1.5), gy(cx, cz) + envf("CY", 1.6), cz)
    # leaves shaken out of the canopy, pebbles jumping between the camera and the feet
    shot.debris(rng, (rx, g, rz + 3), int(envf("LEAVES", 120)), 14, (1.5, 14), ["metasequoia_leaves"], (0.18, 0.3))
    shot.debris(rng, ((rx + cx) / 2, gy(cx, cz), (rz + cz) / 2), int(envf("PEBBLES", 90)), 5, (0.1, 0.9),
                ["gravel", "dirt", "stone"], (0.08, 0.16))
    target = (head[0] + envf("TX", 1.5), head[1] - envf("TDY", 1.5), head[2])
    look = dict(FOREST, fill=envf("FILL", 0.8))
    look["dust"] = ((rx, g + 1.5, rz + 2), (16, 3, 12), envf("DUSTD", 0.2), (0.62, 0.55, 0.44))
    if envf("SHAFT", 1):
        src = (head[0] + envf("SHX", -7), head[1] + envf("SHY", 16), head[2] + envf("SHZ", 5))
        look["spots"] = [(src, tuple(head), envf("SHE", 90000), envf("SHA", 9), (1.0, 0.86, 0.62))]
    sun = sun_from(cam, target, envf("SUNYAW", -20), envf("SUNEL", 40))
    img = render(shot, W, H, cam, target, envf("FOV", 46), sun, look, math.dist(cam, head), envf("FSTOP", 4.0),
                 ((rx, 80, rz), (220, 44, 220)), exposure=envf("EXPO", 0.3))
    return shake(post(img), envf("SHAKE", 4))


SCENES["rugido"] = c_rugido
SCENES["floresta"] = c_floresta


SEAFOG = dict(top=(0.36, 0.48, 0.62), mid=(0.62, 0.68, 0.74), hor=(0.94, 0.86, 0.74), glow=(1.0, 0.80, 0.56),
              sun_col=(1.30, 1.04, 0.74), sky_amb=(0.50, 0.56, 0.64), gnd_amb=(0.26, 0.26, 0.26),
              fog_col=(0.86, 0.86, 0.86), fog_density=0.03, fog_height=envf("FOGH", 63), water_deep=(0.05, 0.12, 0.16),
              water_density=1.0, clouds=0.25, sun_size=0.0006, cloud_shift=3.0,
              sky_strength=envf("SKYS", 1.0), sun_strength=envf("SUNS", 8.0), fill=envf("FILL", 0.4),
              fog_scale=envf("FOGS", 1.0), fog_aniso=envf("FANI", 0.75), glow_gain=envf("GLOWG", 1.6), sun_angle=1.0,
              fog_base=envf("FOGB", 0.03), fog_falloff=envf("FOGF", 0.3),
              ripple_scale=0.5, ripple=0.6, ripple_dist=1.2, water_color=(0.10, 0.22, 0.28), water_trans=0.3,
              water_rough=0.04, square_sun=envf("SQS", 0.03), sun_disc_gain=envf("SDG", 40.0),
              agx=ENV("AGX", "AgX - Medium High Contrast"))


def c_rochedo(W=1920, H=1080):
    """Dawn over the Inland Sea, a bank of sea fog: a single Pteranodon perched on top of a chalk sea stack that
    rises out of the mist, the low sun behind it."""
    os.environ.setdefault("STX", "28")
    os.environ.setdefault("STZ", "150")
    world, coast, height, top_y, rng, topmap = chalk_coast(extra_stacks=((112, 58, 4.0, 74), (88, 40, 3.2, 70),
                                                                         (128, 80, 5.0, 77)))
    sz = envf("STZ", 150)
    sx = coast(sz) - envf("STX", 28)
    # highest block of the stack
    best = max(((y, x, z) for (x, z), y in topmap.items() if math.hypot(x - sx, z - sz) < 6), default=(79, int(sx), int(sz)))
    py, px, pz = best[0] + 1, best[1] + 0.5, best[2] + 0.5
    shot = Shot(world)
    shot.add(PTERO, ENV("PANIM", "idle"), envf("PT", 0.2), (px, py, pz), envf("PYAW", 250))
    if envf("SECOND", 1):
        shot.add(PTERO, "glide", 0.4, (px - envf("P2X", 20), py + envf("P2Y", 9), pz - envf("P2Z", 26)), envf("P2YAW", 230),
                 roll=-12, ground=False, sex="female")
    cam = (px + envf("CX", 16), py + envf("CY", 2.5), pz + envf("CZ", 18))
    target = (px + envf("TX", -3), py + envf("TY", 0.5), pz)
    sun = sun_from(cam, target, envf("SUNYAW", -14), envf("SUNEL", 5))
    img = render(shot, W, H, cam, target, envf("FOV", 34), sun, SEAFOG, math.dist(cam, (px, py, pz)), envf("FSTOP", 4.0),
                 ((px, 70, pz), (500, 40, 500)), exposure=envf("EXPO", 0.0))
    return post(img, 0.25)


SCENES["rochedo"] = c_rochedo


if __name__ == "__main__":
    args = sys.argv[1:]
    out = OUT
    if "--out" in args:
        i = args.index("--out")
        out = os.path.abspath(args[i + 1])
        args = args[:i] + args[i + 2:]
    small = "--small" in args
    args = [a for a in args if a != "--small"]
    os.makedirs(out, exist_ok=True)
    for name in args or SCENES:
        size = tuple(int(v) for v in ENV("SIZE", "960,540" if small else "1920,1080").split(","))
        img = SCENES[name](*size)
        img.save(os.path.join(out, f"{name}.png"))
        print(name, "ok", flush=True)
