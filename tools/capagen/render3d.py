"""
Renders the mod's own dinosaur models (tools/modelgen) for the cover art: transparent background,
key light + amber rim light from the Rift, posed with the model's own animations.
"""
import importlib
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MODELGEN = os.path.join(ROOT, "tools", "modelgen")
sys.path.insert(0, MODELGEN)
sys.path.insert(0, os.path.join(MODELGEN, "species"))

from pybench import Rig, pose_at  # noqa: E402

TEXTURES = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "entity")


def norm(v):
    v = np.array(v, dtype=float)
    return v / np.linalg.norm(v)


def load(name, sex="male", extra_path=None):
    """(rig, texture, model) of a species, painted from its modelgen code, so the cover always shows the current model.
    extra_path: a folder with a proposed species file (e.g. a model still waiting for approval) that wins over species/."""
    import asyncio
    from paint import make_shader, paint_model
    from pybench import PyBench
    if extra_path:
        sys.path.insert(0, extra_path)
    model = importlib.import_module(name).build()
    spec = model.spec()

    async def paint():
        async with PyBench() as bb:
            dump = await bb.build(spec)
            pal = dict(model.palette)
            pal.update((getattr(model, "sexes", None) or {}).get(sex, {}))
            return paint_model(model, dump, make_shader(pal, model.pattern, model.decals))
    tex = asyncio.run(paint()).convert("RGBA")
    return Rig(spec), tex, model


def pose(model, anim, t):
    """Pose of animation `anim` (short name, e.g. 'roar') at fraction t of its length."""
    a = next(a for a in model.animations if a["name"].endswith("." + anim))
    return pose_at(a, round(t * a["length"], 3))


def render(rig, texture, cam, size, pose=None, hidden=(), key=(0.5, 0.8, -0.3), key_col=(1.0, 0.93, 0.82),
           ambient=(0.42, 0.40, 0.48), rim=(-0.3, 0.35, 1.0), rim_col=(1.0, 0.62, 0.22), rim_power=0.75, ss=2):
    """Perspective software render -> RGBA image (alpha = coverage). ss = supersampling factor."""
    W, H = size[0] * ss, size[1] * ss
    tex = np.asarray(texture, dtype=float)
    th, tw = tex.shape[:2]
    pos = np.array(cam["position"], dtype=float)
    fwd = norm(np.array(cam["target"], dtype=float) - pos)
    right = norm(np.cross(fwd, [0.0, 1.0, 0.0]))
    up = np.cross(right, fwd)
    f = 1.0 / math.tan(math.radians(cam.get("fov", 40)) / 2)
    shift = cam.get("shift", (0.0, 0.0))  # lens shift in half-heights, to frame without tilting
    img = np.zeros((H, W, 4))
    zbuf = np.full((H, W), np.inf)
    key, rim = norm(key), norm(rim)
    key_col, rim_col, ambient = (np.array(c) for c in (key_col, rim_col, ambient))

    def project(p):
        d = p - pos
        z = np.dot(d, fwd)
        x = np.dot(d, right) / z * f + shift[0]
        y = np.dot(d, up) / z * f + shift[1]
        return np.array([W / 2 + x * H / 2, H / 2 - y * H / 2, z])

    for c, face, corners, (u0, v0, u1, v1) in rig.cube_faces(pose, hidden):
        if u1 <= u0 or v1 <= v0:
            continue
        P = {st: project(w) for st, (_l, w) in corners.items()}
        n = np.cross(corners[(1, 0)][1] - corners[(0, 0)][1], corners[(0, 1)][1] - corners[(0, 0)][1])
        nn = np.linalg.norm(n)
        if nn < 1e-9:
            continue
        n /= nn
        view = -fwd
        light = ambient + key_col * max(0.0, float(np.dot(n, key))) * 0.75
        # rim: faces turned away from the camera and towards the Rift catch its glow
        r = max(0.0, float(np.dot(n, rim))) * (1.0 - max(0.0, float(np.dot(n, view)))) ** 0.6
        light = light + rim_col * r * rim_power
        for tri in (((0, 0), (1, 0), (1, 1)), ((0, 0), (1, 1), (0, 1))):
            a, b, cc = (P[k] for k in tri)
            if min(a[2], b[2], cc[2]) <= 1e-3:
                continue
            xs, ys = (a[0], b[0], cc[0]), (a[1], b[1], cc[1])
            x0, x1 = max(0, int(min(xs))), min(W - 1, int(max(xs)) + 1)
            y0, y1 = max(0, int(min(ys))), min(H - 1, int(max(ys)) + 1)
            if x0 > x1 or y0 > y1:
                continue
            den = (b[1] - cc[1]) * (a[0] - cc[0]) + (cc[0] - b[0]) * (a[1] - cc[1])
            if abs(den) < 1e-9:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            l1 = ((b[1] - cc[1]) * (gx - cc[0]) + (cc[0] - b[0]) * (gy - cc[1])) / den
            l2 = ((cc[1] - a[1]) * (gx - cc[0]) + (a[0] - cc[0]) * (gy - cc[1])) / den
            l3 = 1 - l1 - l2
            inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if not inside.any():
                continue
            z = 1.0 / (l1 / a[2] + l2 / b[2] + l3 / cc[2])
            st = [np.array(k, dtype=float) for k in tri]
            s = (l1 * st[0][0] / a[2] + l2 * st[1][0] / b[2] + l3 * st[2][0] / cc[2]) * z
            t = (l1 * st[0][1] / a[2] + l2 * st[1][1] / b[2] + l3 * st[2][1] / cc[2]) * z
            tu = np.clip((u0 + s * (u1 - u0)).astype(int), 0, tw - 1)
            tv = np.clip((v0 + t * (v1 - v0)).astype(int), 0, th - 1)
            col = tex[tv, tu]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            ok = inside & (z < sub) & (col[..., 3] > 10)
            sub[ok] = z[ok]
            px = img[y0:y1 + 1, x0:x1 + 1]
            px[..., :3][ok] = col[..., :3][ok] * light
            px[..., 3][ok] = 255
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA")
    if ss > 1:
        out = out.resize(size, Image.LANCZOS)
    return out


def frame(rig, pose=None, hidden=()):
    """World bounds (lo, hi) of the posed model, in model pixels (16 = 1 block)."""
    pts = np.array([w for _c, _f, corners, _uv in rig.cube_faces(pose, hidden) for _l, w in corners.values()])
    return pts.min(axis=0), pts.max(axis=0)
