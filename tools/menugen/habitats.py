"""
Dioramas de habitat do Guia de Campo: seis cenas de blocos sem animal (o modelo vivo do Guia fica na frente),
renderizadas pelo tools/capagen e passadas para "gravura" em tons de tinta sobre o papel do Caderno
(docs/IDENTIDADE.md: papel e tinta), com as bordas sumindo no papel.

  floresta   metassequoias e araucárias na neblina (tiranossaurídeos, raptores do norte, mamíferos, jurássicos)
  planicie   campo de samambaias com araucárias esparsas e colinas (ceratopsídeos, anquilossauros, hadrossauros)
  rio        margem de rio largo com palmeiras e cavalinhas (Spinosaurus, Deinosuchus, peixes de rio, tartarugas)
  seco       planalto seco de areia e laterita com cicadáceas (Gobi, Patagônia, Madagascar)
  litoral    falésias de giz sobre o mar (pterossauros e aves marinhas)
  mar        mar aberto com o horizonte e um rochedo ao longe (répteis marinhos e peixes do mar)

usage (OpenGL preview): xvfb-run -a -s "-screen 0 1920x1080x24" python3 habitats.py CAPAGEN_DIR OUT_DIR [nome ...] [--raw]
usage (final):          BACKEND=cycles SAMPLES=64 python3 habitats.py CAPAGEN_DIR OUT_DIR
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import menu_cenas as mc  # noqa: E402  (reads CAPAGEN_DIR and OUT_DIR from argv like this script)

cn, vx, noise2d = mc.cn, mc.vx, mc.noise2d
OUT = mc.OUT

W, H = 744, 288  # 4x the picture box of the Guide page (186 x 72 GUI pixels)
INK = np.array([59, 42, 26], float)         # TerrassicPalette.INK
INK_SOFT = np.array([122, 100, 72], float)  # TerrassicPalette.INK_SOFT
PAPER = np.array([233, 220, 188], float)    # TerrassicPalette.PAPER


def snap(scene, cam, target, fov, sun, look, focus, fog_box, shadow_box):
    look = dict(look, clouds=min(look.get("clouds", 0.0), 0.12))  # big cloud shapes turn into blotches as ink
    if cn.BACKEND == "cycles":
        return cn.shoot(scene, cam, target, fov, sun, look, None, math.dist(cam, focus), None, 8.0, fog_box)
    col, depth = scene.render(cam, target, fov, sun, look, shadow_box)
    return col


def plates_ground(height, x, z):
    return cn.ground(height, x, z, 1)


def floresta():
    rng = np.random.default_rng(105)
    nx, nz = 180, 180
    hn = noise2d(nz, nx, 30, rng, 4)
    height = lambda x, z: 64 + hn[z % nz, x % nx] * 2.0  # noqa: E731
    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, under="soil",
               top_fn=lambda x, z: "needles" if hn[z % nz, x % nx] > 0.0 else "litter")
    cx, cz = 90, 150
    for _ in range(190):
        x, z = int(rng.uniform(4, nx - 4)), int(rng.uniform(4, nz - 4))
        if math.hypot(x - cx, (z - (cz - 22)) * 1.4) < 16 or z > cz - 4:
            continue
        y = int(round(height(x, z))) + 1
        if rng.random() < 0.7:
            vx.conifer(world, x, y, z, int(rng.uniform(22, 36)), rng, thick=rng.random() < 0.5)
        else:
            vx.araucaria(world, x, y, z, int(rng.uniform(16, 26)), rng)
    kinds = ["royal_fern"] * 4 + ["bracken"] * 3 + ["tall_bracken"] * 2 + ["horsetail", "clubmoss"]
    for _ in range(6000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks and z < cz - 3:
            k = kinds[int(rng.integers(len(kinds)))]
            world.plants.append((x, h + 1, z, k, rng.uniform(1.6, 2.1) if k.startswith("tall_") else rng.uniform(0.8, 1.2)))
    scene = cn.scene_from(world, W, H)
    cam = (cx + 0.5, plates_ground(height, cx, cz) + 2.2, cz + 0.5)
    target = (cx + 0.5, cam[1] + 3.5, cz - 40)
    return snap(scene, cam, target, 50, (-0.4, 0.65, -0.65), cn.MIST, (cx, 66, cz - 24),
                ((90, 85, 90), (180, 50, 180)), ((cx, 66, cz - 40), 70))


def planicie():
    rng = np.random.default_rng(106)
    nx, nz = 240, 240
    hn = noise2d(nz, nx, 40, rng, 4)
    height = lambda x, z: 64 + hn[z % nz, x % nx] * 2.0 + max(0, 110 - z) * 0.18  # noqa: E731
    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, under="soil",
               top_fn=lambda x, z: "litter" if hn[z % nz, x % nx] > 0.2 else "grass")
    cx, cz = 120, 220
    for _ in range(70):
        x, z = int(rng.uniform(4, nx - 4)), int(rng.uniform(4, 170))
        y = int(round(height(x, z))) + 1
        if rng.random() < 0.75:
            vx.araucaria(world, x, y, z, int(rng.uniform(14, 24)), rng)
        else:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 7)), rng)
    kinds = ["cretaceous_grass"] * 5 + ["bracken"] * 3 + ["royal_fern"] * 2 + ["clubmoss", "horsetail"]
    for _ in range(9000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks and z < cz - 2:
            world.plants.append((x, h + 1, z, kinds[int(rng.integers(len(kinds)))], rng.uniform(0.8, 1.2)))
    scene = cn.scene_from(world, W, H)
    cam = (cx + 0.5, plates_ground(height, cx, cz) + 1.8, cz + 0.5)
    target = (cx + 0.5, cam[1] + 2.0, cz - 60)
    return snap(scene, cam, target, 50, (-0.55, 0.45, -0.7), mc.GOLDEN, (cx, 66, cz - 30),
                ((cx, 80, cz - 80), (240, 40, 240)), ((cx, 66, cz - 60), 100))


def rio():
    rng = np.random.default_rng(107)
    nx, nz = 200, 220
    hn = noise2d(nz, nx, 28, rng, 4)
    mid = lambda z: 100 + 10 * math.sin(z / 37.0)  # noqa: E731

    def height(x, z):
        bank = 62.4 + hn[z % nz, x % nx] * 1.6
        d = abs(x - mid(z))
        if d < 11:
            return 58.4 + d * 0.12
        if d < 22:
            return 59.9 + (d - 11) / 11.0 * (bank - 59.9)
        return bank

    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, sea=60, under="soil",
               top_fn=lambda x, z: "mud" if hn[z % nz, x % nx] < -0.2 else "grass")
    cz = 200
    cx = mid(cz) + 2
    for _ in range(200):
        x, z = int(rng.uniform(4, nx - 4)), int(rng.uniform(4, cz - 8))
        y = int(round(height(x, z))) + 1
        if y <= 62:
            continue
        k = rng.random()
        if k < 0.5:
            mc.sabal(world, x, y, z, int(rng.uniform(6, 11)), rng)
        elif k < 0.75:
            vx.tree_fern(world, x, y, z, int(rng.uniform(4, 7)), rng)
        else:
            vx.conifer(world, x, y, z, int(rng.uniform(14, 22)), rng, log="taxodium_log", leaves="taxodium_leaves")
    kinds = ["horsetail"] * 4 + ["tall_horsetail"] * 3 + ["royal_fern"] * 2 + ["cretaceous_grass"] * 3
    for _ in range(7000):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if h > 60 and (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks and z < cz - 2:
            k = kinds[int(rng.integers(len(kinds)))]
            world.plants.append((x, h + 1, z, k, rng.uniform(1.6, 2.1) if k.startswith("tall_") else rng.uniform(0.8, 1.2)))
    scene = cn.scene_from(world, W, H)
    cam = (cx + 0.5, 62.0, cz + 0.5)
    target = (mid(cz - 50), 63.0, cz - 50)
    return snap(scene, cam, target, 52, (-0.5, 0.4, -0.75), mc.DELTA, (mid(cz - 25), 62, cz - 25),
                ((100, 76, 120), (220, 34, 240)), ((100, 62, cz - 40), 90))


def seco():
    rng = np.random.default_rng(108)
    nx, nz = 240, 240
    hn = noise2d(nz, nx, 36, rng, 4)
    du = noise2d(nz, nx, 14, rng, 2)

    def height(x, z):
        h = 64 + hn[z % nz, x % nx] * 2.5 + du[z % nz, x % nx] * 1.5
        return h + max(0.0, 100 - z) * 0.22 * (1.0 + hn[z % nz, (x + 60) % nx])  # long dry slopes far away

    world = vx.World()
    vx.terrain(world, 0, 0, nx, nz, height, under="soil", rock="conglomerate",
               top_fn=lambda x, z: "sand" if du[z % nz, x % nx] > -0.1 else "soil")
    cx, cz = 120, 220
    for _ in range(1400):
        x, z = int(rng.uniform(0, nx)), int(rng.uniform(0, nz))
        h = int(round(height(x, z)))
        if (x, h + 1, z) not in world.blocks and (x, h, z) in world.blocks and z < cz - 3 and rng.random() < 0.5:
            k = ["cycad"] * 2 + ["clubmoss"] * 3 + ["cretaceous_grass"] * 2
            kind = k[int(rng.integers(len(k)))]
            world.plants.append((x, h + 1, z, kind, rng.uniform(1.5, 2.0) if kind == "cycad" else rng.uniform(0.7, 1.0)))
    for _ in range(12):
        x, z = int(rng.uniform(10, nx - 10)), int(rng.uniform(40, 180))
        vx.araucaria(world, x, int(round(height(x, z))) + 1, z, int(rng.uniform(9, 14)), rng)
    scene = cn.scene_from(world, W, H)
    cam = (cx + 0.5, plates_ground(height, cx, cz) + 1.7, cz + 0.5)
    target = (cx + 0.5, cam[1] + 2.5, cz - 70)
    return snap(scene, cam, target, 50, (-0.6, 0.55, -0.6), mc.GOLDEN, (cx, 66, cz - 30),
                ((cx, 80, cz - 80), (240, 40, 240)), ((cx, 66, cz - 60), 110))


def litoral():
    rng = np.random.default_rng(109)
    nx, nz, y0, ny = 200, 240, 40, 56
    hn = noise2d(nz, nx, 26, rng, 4)
    cnz = noise2d(nz, 1, 14, rng, 3)
    ero = noise2d(nz, ny, 9, rng, 3)
    coast = lambda z: 120 + 10 * math.sin(z / 29.0) + cnz[z % nz, 0] * 8  # noqa: E731

    def height(x, z):
        d = x - coast(z)
        if d >= 0:
            return 80 + hn[z % nz, x % nx] * 3
        if d > -4:
            return 61
        return max(44, 58 + d * 0.5)

    X, Z, Y = np.meshgrid(np.arange(nx), np.arange(nz), np.arange(y0, y0 + ny), indexing="ij")
    cst = np.array([coast(z) for z in range(nz)])[None, :, None]
    top = np.array([[height(x, z) for z in range(nz)] for x in range(nx)])[:, :, None]
    eat = ero[Z % nz, Y - y0] * 3.0 + ((Y - 60) // 5 % 2) * 0.7 + np.where((Y > 59) & (Y < 64), 2.2, 0)
    solid = ((X - cst - eat >= 0) | (X - cst < 0)) & (Y <= np.round(top))
    world = vx.World()

    def block(x, y, z, depth):
        if x - coast(z) < -1 and y <= 62:
            return "pebbles" if y >= 59 else "gravel"
        if depth == 0 and y > 77:
            return "grass"
        if depth < 2 and y > 77:
            return "dirt"
        return "chalk"

    vx.fill(world, solid, (0, 0, y0), block)
    for _ in range(25):
        z = int(rng.uniform(5, nz - 5))
        x = int(coast(z) + rng.uniform(8, 50))
        if x < nx - 3 and (x, int(round(height(x, z))), z) in world.blocks:
            vx.araucaria(world, x, int(round(height(x, z))) + 1, z, int(rng.uniform(12, 18)), rng)
    world.water = [(-3000, -3000, 3000, 3000, 60.9)]
    scene = cn.scene_from(world, W, H)
    cz = 225
    cx = int(coast(cz)) - 30
    cam = (cx + 0.5, 66.0, cz + 0.5)
    target = (cx + 14, 68.0, cz - 60)
    return snap(scene, cam, target, 52, (-0.7, 0.25, -0.65), mc.DAWN_SEA, (cx + 10, 68, cz - 40),
                ((cx, 72, cz - 60), (300, 30, 300)), ((cx, 62, cz - 50), 120))


def mar():
    rng = np.random.default_rng(110)
    nx, nz, y0, ny = 120, 200, 40, 40
    ero = noise2d(nz, ny, 9, rng, 3)
    X, Z, Y = np.meshgrid(np.arange(nx), np.arange(nz), np.arange(y0, y0 + ny), indexing="ij")
    sx, sz = 70, 40
    rr = np.hypot(X - sx, Z - sz)
    solid = (Y <= 44) | ((rr < (6 + ero[Z % nz, Y - y0] * 2) * np.clip((80 - Y) / 14.0, 0.35, 1.0)) & (Y <= 76 - rr * 0.6))
    world = vx.World()
    vx.fill(world, solid, (0, 0, y0), lambda x, y, z, d: "chalk" if y > 58 else "stone")
    world.water = [(-3000, -3000, 3000, 3000, 60.9)]
    scene = cn.scene_from(world, W, H)
    cam = (60.5, 62.4, 190.5)
    target = (64, 63.5, 100)
    return snap(scene, cam, target, 52, (-0.6, 0.3, -0.7), mc.DAWN_SEA, (sx, 64, sz),
                ((60, 70, 100), (300, 24, 300)), ((60, 62, 100), 120))


HABITATS = {"floresta": floresta, "planicie": planicie, "rio": rio, "seco": seco, "litoral": litoral, "mar": mar}


def engraving(img):
    """The render as a faint ink engraving on the notebook paper: continuous tone from between INK and INK_SOFT to PAPER with a fine grain, edges into the
    paper. Faint on purpose, so the live, coloured model in front reads first."""
    a = np.asarray(img.convert("RGB").resize((W, H), Image.LANCZOS), float) / 255.0
    lum = a @ np.array([0.30, 0.59, 0.11])
    lo, hi = np.percentile(lum, 1), np.percentile(lum, 99)
    t = np.clip((lum - lo) / max(hi - lo, 1e-3), 0, 1) ** 0.85
    t = np.clip(t + np.random.default_rng(7).normal(0, 0.012, t.shape), 0, 1)  # paper grain, no banding
    t = 0.30 + 0.70 * t  # darkest tone stays between ink and paper
    dark = INK * 0.6 + INK_SOFT * 0.4
    col = dark[None, None] * (1 - t[..., None]) + PAPER[None, None] * t[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    edge = np.minimum.reduce([xx / 60.0, (W - 1 - xx) / 60.0, yy / 40.0, (H - 1 - yy) / 40.0]).clip(0, 1) ** 1.3
    col = col * edge[..., None] + PAPER * (1 - edge[..., None])
    return Image.fromarray(col.astype(np.uint8), "RGB")


if __name__ == "__main__":
    args = [a for a in sys.argv[3:] if a != "--raw"]
    os.makedirs(OUT, exist_ok=True)
    for name in args or HABITATS:
        raw = HABITATS[name]()
        raw.save(os.path.join(OUT, f"raw_{name}.png"))
        engraving(raw).save(os.path.join(OUT, f"habitat_{name}.png"), optimize=True)
        print(name, "ok")
