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
        self.meshes = [gl.Mesh(world.mesh(uv), img)]
        self.meshes[0].foliage = foliage_mask(tex)
        if world.water:
            self.meshes.append(gl.Mesh(world.water_mesh(), img, water=True))

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
