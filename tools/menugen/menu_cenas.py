"""
Fundos do menu principal Terrassic: cenas de blocos (gl.py/voxels.py/cenas.py da capa) compostas para o menu.
O espécime fica no terço direito (lente deslocada com shift, sem girar a perspectiva), olhando para dentro do quadro;
o terço esquerdo fica calmo e mais escuro, porque ali entram o letreiro e a coluna de opções.

"nevoa" was the first one approved (docs/MENU.md); one scene per remastered species.

usage (OpenGL preview): xvfb-run -a -s "-screen 0 1920x1080x24" python3 menu_cenas.py CAPAGEN_DIR OUT_DIR [cena ...] [--small] [--wip DIR]
usage (final image):    BACKEND=cycles SAMPLES=96 python3 menu_cenas.py CAPAGEN_DIR OUT_DIR nevoa --wip DIR
"""
import math
import os
import sys

import numpy as np

CAPAGEN = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
sys.path.insert(0, CAPAGEN)

import cenas as cn  # noqa: E402
import voxels as vx  # noqa: E402
from pixel import noise2d  # noqa: E402

GOLDEN = dict(top=(0.30, 0.42, 0.66), mid=(0.70, 0.66, 0.62), hor=(1.0, 0.82, 0.58), glow=(1.0, 0.72, 0.40),
              sun_col=(1.40, 1.08, 0.74), sky_amb=(0.46, 0.48, 0.60), gnd_amb=(0.30, 0.26, 0.20),
              fog_col=(0.90, 0.74, 0.56), fog_density=0.0045, fog_height=66, water_sky=(0.98, 0.80, 0.58),
              water_deep=(0.10, 0.16, 0.18), clouds=0.45, sun_size=0.0008)

LAKE_MIST = dict(cn.MIST, fog_density=0.011, fog_height=68, water_sky=(0.80, 0.82, 0.78),
                 water_deep=(0.08, 0.13, 0.13), glow=(1.0, 0.84, 0.60), sun_size=0.0006)


def frame(scene, cam, target, fov, sun, look, gl_box, focus_point, fog_box, shift, W, H, gl_post):
    """Renders with the subject at (1 + shift) / 2 of the width. OpenGL: lens shift. Cycles (no lens shift here):
    render wider with the same vertical field and keep the left part."""
    if cn.BACKEND == "cycles":
        scene.W = int(round(W * (1.0 + shift)))
        col = cn.shoot(scene, cam, target, fov, sun, look, None, math.dist(cam, focus_point), None, 4.0, fog_box)
        return col.crop((0, 0, W, H))
    col, depth = scene.render(cam, target, fov, sun, look, gl_box, shift=(shift, 0.0))
    return gl_post(col, depth)


def sabal(world, x, y, z, h, rng):
    """Sabal palm: slender trunk and a round crown of drooping fronds."""
    for k in range(h):
        world.set(x, y + k, z, "sabal_log")
    top = y + h
    world.set(x, top, z, "sabal_leaves")
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        for s in range(1, 4 if dx == 0 or dz == 0 else 3):
            world.set(x + dx * s, top - (1 if s >= 2 else 0) - (1 if s >= 3 else 0), z + dz * s, "sabal_leaves")


GOLDEN = dict(top=(0.34, 0.46, 0.68), mid=(0.74, 0.68, 0.60), hor=(1.0, 0.84, 0.60), glow=(1.0, 0.74, 0.42),
              sun_col=(1.40, 1.05, 0.70), sky_amb=(0.46, 0.48, 0.58), gnd_amb=(0.30, 0.26, 0.20),
              fog_col=(0.92, 0.78, 0.60), fog_density=0.006, fog_height=70, water_sky=(0.98, 0.82, 0.60),
              water_deep=(0.10, 0.16, 0.18), clouds=0.35, sun_size=0.0008, fog_scale=0.35, sun_strength=6.0,
              fog_aniso=0.65)

DELTA = dict(top=(0.42, 0.56, 0.70), mid=(0.72, 0.78, 0.78), hor=(0.95, 0.90, 0.78), glow=(1.0, 0.86, 0.62),
             sun_col=(1.25, 1.08, 0.85), sky_amb=(0.52, 0.58, 0.62), gnd_amb=(0.28, 0.28, 0.22),
             fog_col=(0.82, 0.84, 0.78), fog_density=0.010, fog_height=70, water_sky=(0.86, 0.86, 0.80),
             water_deep=(0.10, 0.20, 0.18), clouds=0.0, sun_size=0.0, fog_scale=0.3, sun_strength=6.5,
             fog_aniso=0.7)

DAWN_SEA = dict(top=(0.36, 0.44, 0.62), mid=(0.70, 0.70, 0.76), hor=(1.0, 0.86, 0.74), glow=(1.0, 0.78, 0.56),
                sun_col=(1.35, 1.05, 0.80), sky_amb=(0.50, 0.54, 0.64), gnd_amb=(0.30, 0.28, 0.26),
                fog_col=(0.86, 0.82, 0.80), fog_density=0.008, fog_height=68, water_sky=(0.92, 0.84, 0.78),
                water_deep=(0.06, 0.14, 0.20), clouds=0.4, sun_size=0.0008, cloud_shift=2.0, fog_scale=0.3,
                sun_strength=6.0, fog_aniso=0.7)


def triceratops(W=1920, H=1080):
    """Um Triceratops pastando numa clareira de samambaias no fim da tarde, araucárias em volta, sol baixo atrás."""
    rng = np.random.default_rng(21)
    nx, nz = 220, 220
    hn = noise2d(nz, nx, 36, rng, 4)
    tx, tz = 110, 118
    cx, cz = tx + 6, tz + 17
    height = lambda x, z: 64 + hn[z % nz, x % nx] * 2.5 + (max(0, 70 - z) * 0.5)  # noqa: E731
    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, under="soil",
               top_fn=lambda x, z: "litter" if hn[z % nz, x % nx] > 0.25 else "grass")
    clearing = lambda x, z: math.hypot(x - (tx + cx) / 2, (z - (tz + cz) / 2) * 0.9) > 24  # noqa: E731
    view = cn.clear_of((cx, cz), (tx - 10, tz - 70), 10)
    for _ in range(200):
        x, z = int(rng.uniform(4, nx - 4)), int(rng.uniform(4, nz - 4))
        if not clearing(x, z) or not view(x, z):
            continue
        y = int(round(height(x, z))) + 1
        k = rng.random()
        if k < 0.6:
            vx.araucaria(world, x, y, z, int(rng.uniform(16, 26)), rng)
        elif k < 0.85:
            vx.conifer(world, x, y, z, int(rng.uniform(14, 22)), rng)
        else:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 7)), rng)
    near = cn.clear_of((cx, cz), (tx, tz), 2.5)
    kinds = ["royal_fern"] * 4 + ["bracken"] * 4 + ["cretaceous_grass"] * 4 + ["horsetail", "clubmoss", "tall_bracken"]
    for _ in range(7000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks and near(x, z) and math.hypot(x - tx, z - tz) > 3:
            kind = kinds[int(rng.integers(len(kinds)))]
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.6, 2.1) if kind.startswith("tall_") else rng.uniform(0.8, 1.2)))
    scene = cn.scene_from(world, W, H)
    ty = int(round(height(tx, tz))) + 1
    cn.place(scene, "triceratops", os.environ.get("ANIM", "graze"), float(os.environ.get("T", 0.35)), (tx, ty, tz),
             float(os.environ.get("YAW", 120)), 9.0, rim=0.7)
    cam = (cx + 0.5, cn.ground(height, cx, cz, 1) + float(os.environ.get("CAMY", 1.9)), cz + 0.5)
    target = (tx - 1, ty + 2.3, tz)
    sun = tuple(float(v) for v in os.environ.get("SUN", "-0.55,0.22,-0.80").split(","))
    return frame(scene, cam, target, 44, sun, GOLDEN, ((tx, ty, tz - 20), 90), (tx, ty + 2, tz),
                 ((tx, 80, tz - 40), (240, 40, 240)), float(os.environ.get("SHIFT", 0.30)), W, H,
                 lambda col, depth: cn.vignette(cn.bloom(cn.dof(col, depth, 18, 8, 4.0, 90), 210, 18, 0.3), 0.3))


def espinossauro(W=1920, H=1080):
    """Um Spinosaurus pescando no raso de um delta quente de manhã, palmeiras e fetos-arborescentes, névoa úmida."""
    rng = np.random.default_rng(31)
    nx, nz = 220, 220
    hn = noise2d(nz, nx, 28, rng, 4)
    channel = lambda x, z: abs((x - 100) - 18 * math.sin(z / 26.0))  # noqa: E731
    sx, sz = 104, 120
    cx, cz = sx + 7, sz + 18

    def height(x, z):
        base = 62 + hn[z % nz, x % nx] * 2.2
        d = channel(x, z)
        if d < 14:
            base = 58.6 + d * 0.12
        elif d < 22:
            base = min(base, 60 + (d - 14) * 0.3)
        return base

    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, sea=60, under="soil",
               top_fn=lambda x, z: "mud" if hn[z % nz, x % nx] < -0.25 else "grass")
    view = cn.clear_of((cx, cz), (sx - 12, sz - 60), 9)
    for _ in range(170):
        x, z = int(rng.uniform(4, nx - 4)), int(rng.uniform(4, nz - 4))
        y = int(round(height(x, z))) + 1
        if y <= 62 or not view(x, z) or math.hypot(x - sx, z - sz) < 10:
            continue
        k = rng.random()
        if k < 0.55:
            sabal(world, x, y, z, int(rng.uniform(6, 11)), rng)
        elif k < 0.8:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 7)), rng)
        else:
            vx.conifer(world, x, y, z, int(rng.uniform(12, 18)), rng, log="taxodium_log", leaves="taxodium_leaves")
    kinds = ["horsetail"] * 4 + ["tall_horsetail"] * 2 + ["royal_fern"] * 2 + ["cretaceous_grass"] * 3 + ["clubmoss"]
    near = cn.clear_of((cx, cz), (sx, sz), 2.5)
    for _ in range(6000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if h > 60 and (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks and near(x, z):
            kind = kinds[int(rng.integers(len(kinds)))]
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.6, 2.1) if kind.startswith("tall_") else rng.uniform(0.8, 1.2)))
    scene = cn.scene_from(world, W, H)
    sy = 59.8  # wading: the feet in the shallows
    cn.place(scene, "spinosaurus", os.environ.get("ANIM", "idle"), float(os.environ.get("T", 0.3)), (sx, sy, sz),
             float(os.environ.get("YAW", 125)), 14.0, rim=0.6)
    cam = (cx + 0.5, 61.6 + float(os.environ.get("CAMY", 1.6)), cz + 0.5)
    target = (sx - 2, sy + 3.2, sz)
    sun = tuple(float(v) for v in os.environ.get("SUN", "-0.45,0.35,-0.85").split(","))
    return frame(scene, cam, target, 46, sun, DELTA, ((sx, 62, sz - 20), 100), (sx, sy + 3, sz),
                 ((sx, 78, sz - 40), (240, 36, 240)), float(os.environ.get("SHIFT", 0.30)), W, H,
                 lambda col, depth: cn.vignette(cn.bloom(cn.dof(col, depth, 20, 8, 3.5, 90), 205, 22, 0.3), 0.3))


def pteranodonte(W=1920, H=1080):
    """Um Pteranodon planando rente ao mar na alvorada, falésia de giz à direita, a colônia ao longe."""
    rng = np.random.default_rng(41)
    nx, nz = 220, 260
    hn = noise2d(nz, nx, 26, rng, 4)
    coast = lambda z: 150 + 14 * math.sin(z / 33.0)  # noqa: E731

    def height(x, z):
        d = x - coast(z)
        if d >= 0:
            return 80 + hn[z % nz, x % nx] * 3 + min(d, 20) * 0.1
        if d > -3:
            return 61
        return max(44, 57 + d * 0.4)

    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, sea=60, under="chalk", rock="chalk",
               top_fn=lambda x, z: "grass" if hn[z % nz, x % nx] > -0.3 else "litter")
    for _ in range(40):
        z = int(rng.uniform(5, nz - 5))
        x = int(coast(z) + rng.uniform(6, 50))
        if x < nx - 3:
            vx.araucaria(world, x, int(round(height(x, z))) + 1, z, int(rng.uniform(12, 20)), rng)
    for _ in range(1500):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        if x - coast(z) > 2:
            h = int(round(height(x, z)))
            if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks:
                k = ["cretaceous_grass"] * 4 + ["bracken", "clubmoss"]
                world.plants.append((x, h + 1, z, k[int(rng.integers(len(k)))], rng.uniform(0.8, 1.2)))
    scene = cn.scene_from(world, W, H)
    cz = 240
    cx = int(coast(cz)) - 30
    cam = (cx + 0.5, 66.0, cz + 0.5)
    px, py, pz = cx + 3.0, 67.0, cz - 13.0
    cn.place(scene, cn.PTERO, "glide", 0.2, (px, py, pz), float(os.environ.get("YAW", 205)), 7.0, axis=0,
             roll=float(os.environ.get("ROLL", -10)), rim=0.7)
    for i, (dx, dy, dz, yw) in enumerate([(25, 14, -70, 200), (40, 8, -110, 150), (10, 20, -130, 175),
                                          (-15, 10, -90, 220), (32, 24, -160, 185)]):
        cn.place(scene, cn.PTERO, "glide" if i % 2 else "fly", 0.3 * i, (cx + dx, 66 + dy, cz + dz), yw, 7.0, axis=0,
                 roll=float(rng.uniform(-18, 18)))
    target = (px - 1, py + 0.5, pz)
    sun = tuple(float(v) for v in os.environ.get("SUN", "-0.70,0.18,-0.70").split(","))
    return frame(scene, cam, target, 46, sun, DAWN_SEA, ((px, 62, pz - 40), 120), (px, py, pz),
                 ((px, 72, pz - 60), (300, 30, 300)), float(os.environ.get("SHIFT", 0.30)), W, H,
                 lambda col, depth: cn.vignette(cn.bloom(cn.dof(col, depth, 14, 6, 3.0, 160), 215, 16, 0.25), 0.25))


def nevoa(W=1920, H=1080):
    """O T. rex saindo da neblina da manhã entre metassequoias gigantes, no terço direito; à esquerda a névoa com os
    raios de sol fica calma para o letreiro e as opções (o cenário que o Rodrigo preferiu na capa)."""
    rng = np.random.default_rng(5)
    nx, nz = 200, 200
    hn = noise2d(nz, nx, 30, rng, 4)
    height = lambda x, z: 64 + hn[z % nz, x % nx] * 2.5  # noqa: E731
    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, under="soil",
               top_fn=lambda x, z: "needles" if hn[z % nz, x % nx] > 0.1 else "litter")
    cx, cz = 106, 160
    rx, rz = cx - 5, cz - 17
    keep = cn.clear_of((cx, cz), (rx, rz), 8)
    for _ in range(170):
        x, z = int(rng.uniform(4, nx - 4)), int(rng.uniform(4, nz - 4))
        if not keep(x, z) or math.hypot(x - rx, z - rz) < 11:
            continue
        y = int(round(height(x, z))) + 1
        big = rng.random() < 0.6 or math.hypot(x - cx, z - cz) < 40
        vx.conifer(world, x, y, z, int(rng.uniform(26, 38) if big else rng.uniform(14, 24)), rng, thick=big)
    keep_low = cn.clear_of((cx, cz), (rx, rz), 2.5)
    kinds = ["royal_fern"] * 5 + ["bracken"] * 3 + ["tall_bracken"] * 2 + ["horsetail", "tall_horsetail", "clubmoss"]
    for _ in range(9000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks and math.hypot(x - cx, z - cz) > 3.5 \
                and keep_low(x, z):
            kind = kinds[int(rng.integers(len(kinds)))]
            tall = kind.startswith("tall_")
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.7, 2.3) if tall else rng.uniform(0.9, 1.3)))
    scene = cn.scene_from(world, W, H)
    ry = int(round(height(rx, rz))) + 1
    cn.place(scene, cn.REX, os.environ.get("ANIM", "walk"), float(os.environ.get("T", 0.25)), (rx, ry, rz),
             float(os.environ.get("YAW", 150)), 12.5, rim=0.6)
    cam = (cx + 0.5, cn.ground(height, cx, cz, 1) + float(os.environ.get("CAMY", 2.8)), cz + 0.5)
    target = (rx - 1, ry + 4.5, rz)
    sun = tuple(float(v) for v in os.environ.get("SUN", "-0.5,0.6,-0.8").split(","))
    shift = float(os.environ.get("SHIFT", 0.30))
    if cn.BACKEND == "cycles":
        # Cycles has no lens shift here: render wider (same vertical field) and keep the left part, so the rex
        # lands at (1 + shift) / 2 of the width
        scene.W = int(round(W * (1.0 + shift)))
        col = cn.shoot(scene, cam, target, 48, sun, cn.MIST, None, math.dist(cam, (rx, ry + 4, rz)), None, 4.0,
                       ((100, 85, 100), (200, 50, 200)))
        return col.crop((0, 0, W, H))
    col, depth = scene.render(cam, target, 48, sun, cn.MIST, ((rx, ry + 10, rz + 20), 90), shift=(shift, 0.0))
    return cn.vignette(cn.bloom(cn.dof(col, depth, 24, 12, 3.0, 90), 205, 24, 0.3), 0.3)


SCENES = {"nevoa": nevoa, "triceratops": triceratops, "espinossauro": espinossauro, "pteranodonte": pteranodonte}

if __name__ == "__main__":
    args = sys.argv[3:]
    if "--wip" in args:
        i = args.index("--wip")
        cn.WIP = os.path.abspath(args[i + 1])
        args = args[:i] + args[i + 2:]
        if os.path.exists(os.path.join(cn.WIP, "tyrannosaurus_v3.py")):
            cn.REX = "tyrannosaurus_v3"
    small = "--small" in args
    args = [a for a in args if a != "--small"]
    os.makedirs(OUT, exist_ok=True)
    for name in args or SCENES:
        img = SCENES[name](960, 540) if small else SCENES[name]()
        img.save(os.path.join(OUT, f"{name}.png"))
        print(name, "ok")
