"""
Square Terrassic icon in the style of the covers: the T. rex of the "cacada" cover roaring, close up, against the
dusk glow, path traced in Blender Cycles.

usage:  python3 icone.py [--small]   -> art/capa/terrassic_icon_512.png (opaque) and terrassic_icon_512_transparente.png
env:    SAMPLES (default 128), SS (supersampling, default 1.0), DIST/SIDE/LIFT/FOV (camera), ONLY=opaco|transparente
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["BACKEND"] = "cycles"
os.environ.setdefault("SAMPLES", "128")

import cenas  # noqa: E402

OUT = os.path.join(cenas.r3.ROOT, "art", "capa")
_rex = {}
_shot = {}


def _place(scene, name, anim, t, pos, yaw, length, *a, **k):
    _orig_place(scene, name, anim, t, pos, yaw, length, *a, **k)
    if name == cenas.REX:
        _rex.update(mesh=scene.meshes[-1], yaw=yaw)


def _shoot(scene, cam, target, fov, sun, look, shadow_box, focus, gl_post, fstop=4.0, fog_box=None, exposure=0.0):
    _shot.update(scene=scene, sun=sun, look=look, fog_box=fog_box)
    return None


_orig_place = cenas.place
cenas.place = _place
cenas.shoot = _shoot


def head():
    """Centre of the T. rex head and the direction it faces (scene coords, y up)."""
    v = _rex["mesh"].verts[:, :3]
    y = math.radians(_rex["yaw"])
    d = np.array([-math.sin(y), 0.0, -math.cos(y)])
    s = v @ d
    tip = v[s > s.max() - 2.2]
    return tip.mean(0), d


def camera():
    c, d = head()
    side = np.array([-d[2], 0.0, d[0]])  # to the right of the head
    dist = float(os.environ.get("DIST", 12.0))
    k = float(os.environ.get("SIDE", -0.7))  # 0 = straight in front, 1 or -1 = side view
    off = d * math.cos(k * math.pi / 2) + side * math.sin(k * math.pi / 2)
    cam = c + off * dist + np.array([0, float(os.environ.get("LIFT", -1.5)), 0])
    target = c - d * float(os.environ.get("TB", 0.5)) + np.array([0, float(os.environ.get("TY", -0.6)), 0])
    return tuple(cam), tuple(target), float(np.linalg.norm(c - cam))


def main():
    import blend
    small = "--small" in sys.argv
    P = 256 if small else 512
    ss = float(os.environ.get("SS", 1.0))
    R = int(P * 2 * ss)  # rendered at twice the icon size, then reduced: sharp at 512 and at 64
    cenas.cacada(R, R)
    cam, target, focus = camera()
    fov = float(os.environ.get("FOV", 38))
    only = os.environ.get("ONLY")
    os.makedirs(OUT, exist_ok=True)
    tag = "_small" if small else ""
    if only != "transparente":
        img = blend.render(_shot["scene"].meshes, cam, target, fov, _shot["sun"], _shot["look"], R, R,
                           cenas.SAMPLES, focus, 2.8, _shot["fog_box"])
        img = cenas.vignette(img.resize((P, P), Image.LANCZOS), 0.28)
        img.save(os.path.join(OUT, f"terrassic_icon_512{tag}.png"))
    if only != "opaco":
        rex = blend.render([_rex["mesh"]], cam, target, fov, _shot["sun"], _shot["look"], R, R,
                           cenas.SAMPLES, None, 2.8, None, transparent=True)
        rex.resize((P, P), Image.LANCZOS).save(os.path.join(OUT, f"terrassic_icon_512_transparente{tag}.png"))
    print("icon ok")


if __name__ == "__main__":
    main()
