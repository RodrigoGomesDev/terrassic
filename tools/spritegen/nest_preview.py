"""Preview of an egg-and-nest block model, drawn outside the game (a small software renderer of the block model
JSON: cuboids, the vanilla face UV rules, one-axis element rotation, flat Minecraft-like face shading).

Writes art/<species>/previews/ovo_ninho.png: the three hatch stages seen from the front three-quarter, the same three
from above, and the shell texture of each stage blown up.
usage: python3 -B tools/spritegen/nest_preview.py daspletosaurus [albertosaurus ...]
"""
import importlib
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rex_extras import TEX, ROOT  # noqa: E402

EXTRAS = {"daspletosaurus": "dasple_extras", "albertosaurus": "alberto_extras",
          "carcharodontosaurus": "carcharo_extras", "majungasaurus": "majunga_extras"}
SHADE = {"up": 1.0, "down": 0.5, "north": 0.8, "south": 0.8, "east": 0.62, "west": 0.62}


def _tex(ref):
    ns, path = ref.split(":", 1)
    with Image.open(os.path.join(TEX, path + ".png")) as im:
        return np.asarray(im.convert("RGBA"), dtype=np.float32)


def _face_corners(name, x0, y0, z0, x1, y1, z1):
    """The four corners of a face in the order (uv0,v0) (u1,v0) (u1,v1) (u0,v1)."""
    return {
        "up": [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
        "down": [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)],
        "north": [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
        "south": [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
        "east": [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
        "west": [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
    }[name]


def _rotate(p, rot):
    if not rot:
        return p
    ox, oy, oz = rot["origin"]
    a = math.radians(rot["angle"])
    x, y, z = p[0] - ox, p[1] - oy, p[2] - oz
    c, s = math.cos(a), math.sin(a)
    if rot["axis"] == "y":
        x, z = x * c + z * s, -x * s + z * c
    elif rot["axis"] == "x":
        y, z = y * c - z * s, y * s + z * c
    else:
        x, y = x * c - y * s, x * s + y * c
    return (x + ox, y + oy, z + oz)


def render(model, yaw=35.0, pitch=32.0, ppu=22, size=470):
    texs = {}
    for key, ref in model["textures"].items():
        if ":" in ref:
            texs["#" + key] = _tex(ref)
    img = np.zeros((size, size, 3), np.float32)
    img[:] = (232, 228, 220)
    depth = np.full((size, size), np.inf, np.float32)
    cy_, sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def view(p):
        # seen from the south (+z, the front of the nest) and above: turn half a circle, then yaw and pitch
        x, y, z = 8 - p[0], p[1] - 3, 8 - p[2]
        x, z = x * cy_ - z * sy_, x * sy_ + z * cy_
        y, z = y * cp + z * sp, z * cp - y * sp   # depth: smaller is nearer the viewer
        return (size / 2 + x * ppu, size * 0.58 - y * ppu, z)

    for el in model["elements"]:
        (x0, y0, z0), (x1, y1, z1) = el["from"], el["to"]
        for name, face in el["faces"].items():
            tex = texs.get(face["texture"])
            if tex is None:
                continue
            u0, v0, u1, v1 = face.get("uv", [0, 0, 16, 16])
            cs = [view(_rotate(c, el.get("rotation"))) for c in _face_corners(name, x0, y0, z0, x1, y1, z1)]
            a, b, d = np.array(cs[0]), np.array(cs[1]), np.array(cs[3])
            e1, e2 = b[:2] - a[:2], d[:2] - a[:2]
            det = e1[0] * e2[1] - e1[1] * e2[0]
            if abs(det) < 1e-6:
                continue
            xs = [c[0] for c in cs]
            ys = [c[1] for c in cs]
            bx0, bx1 = max(0, int(min(xs))), min(size - 1, int(max(xs)) + 1)
            by0, by1 = max(0, int(min(ys))), min(size - 1, int(max(ys)) + 1)
            if bx1 < bx0 or by1 < by0:
                continue
            gx, gy = np.meshgrid(np.arange(bx0, bx1 + 1) + 0.5, np.arange(by0, by1 + 1) + 0.5)
            px, py = gx - a[0], gy - a[1]
            s = (px * e2[1] - py * e2[0]) / det
            t = (e1[0] * py - e1[1] * px) / det
            inside = (s >= 0) & (s <= 1) & (t >= 0) & (t <= 1)
            if not inside.any():
                continue
            zz = a[2] + s * (b[2] - a[2]) + t * (d[2] - a[2])
            uu = u0 + s * (u1 - u0)
            vv = v0 + t * (v1 - v0)
            th, tw = tex.shape[:2]
            ti = np.clip((vv / 16.0 * th).astype(int), 0, th - 1)
            tj = np.clip((uu / 16.0 * tw).astype(int), 0, tw - 1)
            col = tex[ti, tj]
            sub_d = depth[by0:by1 + 1, bx0:bx1 + 1]
            ok = inside & (zz < sub_d) & (col[..., 3] > 8)
            sub_d[ok] = zz[ok]
            img[by0:by1 + 1, bx0:bx1 + 1][ok] = col[..., :3][ok] * SHADE[name]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def sheet(sid):
    mod = importlib.import_module(EXTRAS[sid])
    egg = mod.CUSTOM_EGGS[sid]
    w = 470
    out = Image.new("RGB", (w * 3, w * 2 + 450), (232, 228, 220))
    dr = ImageDraw.Draw(out)
    names = ("0: postos", "1: a mae abre o ninho", "2: o filhote sai")
    for st in range(3):
        m = egg(sid, st)
        out.paste(render(m), (st * w, 0))
        out.paste(render(m, yaw=10.0, pitch=70.0), (st * w, w))
        dr.text((st * w + 10, 8), f"{sid} - estagio {names[st]}", fill=(30, 30, 30))
        shell = _tex(f"terrassic:block/{sid}_egg_{st}").astype(np.uint8)
        big = Image.fromarray(shell).resize((192, 192), Image.NEAREST)
        out.paste(big, (20 + st * 212, w * 2 + 20), big)
    extra = [r for k, r in egg(sid, 0)["textures"].items() if k not in ("egg", "particle")]
    for i, ref in enumerate(extra):
        big = Image.fromarray(_tex(ref).astype(np.uint8)).resize((192, 192), Image.NEAREST)
        out.paste(big, (20 + i * 212, w * 2 + 240), big)
    path = os.path.join(ROOT, "art", sid, "previews", "ovo_ninho.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path)
    return path


if __name__ == "__main__":
    for s in sys.argv[1:] or list(EXTRAS):
        print(sheet(s))
