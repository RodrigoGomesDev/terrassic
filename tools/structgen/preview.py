"""Isometric preview of the structure templates, for review (flat-shaded blocks in the average colour of their
texture; stairs, slabs and mats drawn as the shapes they roughly are).

usage:  python3 preview.py  -> art/estruturas/<structure>_<variant>.png and art/estruturas/estruturas.png
"""
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import nbt  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
STRUCT = os.path.join(ROOT, "common", "src", "main", "resources", "data", "terrassic", "structures")
TEX = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "block")
OUT = os.path.join(ROOT, "art", "estruturas")
VANILLA = {"minecraft:gravel": (130, 124, 122), "minecraft:coarse_dirt": (119, 85, 59), "minecraft:bone_block": (226, 222, 200),
           "minecraft:grass_block": (95, 135, 60), "minecraft:dirt": (134, 96, 67), "minecraft:sand": (219, 207, 163),
           "minecraft:water": (60, 90, 200)}
_COL = {}


def colour(name):
    if name in _COL:
        return _COL[name]
    if name in VANILLA:
        c = VANILLA[name]
    else:
        short = name.split(":", 1)[1]
        cands = [short, short.replace("_stairs", ""), short.replace("_slab", ""), short.replace("_stacked", ""),
                 short + "_top", short.replace("stripped_", "stripped_") + "", short.replace("_skull_fossil", "_skull")]
        c = (200, 0, 200)
        for cand in cands + [short.split("_")[0]]:
            p = os.path.join(TEX, cand + ".png")
            if os.path.exists(p):
                a = np.asarray(Image.open(p).convert("RGBA"), dtype=float)
                m = a[..., 3] > 10
                c = tuple(int(v) for v in a[m][:, :3].mean(axis=0)) if m.any() else (128, 128, 128)
                break
    _COL[name] = c
    return c


def shape(name, props):
    if name.endswith("_slab") or name.endswith("_mat") or "rug" in name or name.endswith("bone_pile"):
        return 0.5 if name.endswith("_slab") else 0.12
    if name.endswith("_stairs"):
        return 0.75
    if name.endswith("_bed"):
        return 0.55
    if "fence" in name or "torch" in name:
        return -1  # post
    return 1.0


def render(path, scale=14):
    r = nbt.read(path)
    sx, sy, sz = r["size"]
    pal = r["palette"]
    blocks = [(b["pos"], pal[b["state"]]) for b in r["blocks"] if pal[b["state"]]["Name"] != "minecraft:air"]
    W = (sx + sz) * scale + 40
    H = (sx + sz) * scale // 2 + sy * scale + 60
    im = Image.new("RGB", (W, H), (34, 26, 40))
    d = ImageDraw.Draw(im)
    ox, oy = sz * scale + 20, sy * scale + 30

    def P(x, y, z):
        return (ox + (x - z) * scale, oy + (x + z) * scale // 2 - y * scale)
    for (x, y, z), st in sorted(blocks, key=lambda b: (b[0][0] + b[0][2], b[0][1])):
        c = np.array(colour(st["Name"]), dtype=float)
        h = shape(st["Name"], st.get("Properties", {}))
        if h < 0:
            x0, x1, z0, z1, h = x + 0.4, x + 0.6, z + 0.4, z + 0.6, 1.0
        else:
            x0, x1, z0, z1 = x, x + 1, z, z + 1
        top = [P(x0, y + h, z0), P(x1, y + h, z0), P(x1, y + h, z1), P(x0, y + h, z1)]
        left = [P(x0, y, z1), P(x1, y, z1), P(x1, y + h, z1), P(x0, y + h, z1)]
        right = [P(x1, y, z0), P(x1, y, z1), P(x1, y + h, z1), P(x1, y + h, z0)]
        d.polygon(right, fill=tuple((c * 0.62).astype(int)), outline=tuple((c * 0.45).astype(int)))
        d.polygon(left, fill=tuple((c * 0.8).astype(int)), outline=tuple((c * 0.55).astype(int)))
        d.polygon(top, fill=tuple(c.astype(int)), outline=tuple((c * 0.7).astype(int)))
    for e in r.get("entities", []):
        x, y, z = e["pos"]
        px, py = P(x, y + 0.6, z)
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=(230, 190, 60), outline=(60, 40, 10))
    d.text((8, 6), os.path.relpath(path, STRUCT), fill=(240, 230, 210))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = []
    for p in sorted(glob.glob(os.path.join(STRUCT, "**", "*.nbt"), recursive=True)):
        im = render(p)
        im.save(os.path.join(OUT, os.path.relpath(p, STRUCT).replace(os.sep, "_")[:-4] + ".png"))
        ims.append(im)
    w = max(i.width for i in ims)
    sheet = Image.new("RGB", (w * 2, sum(i.height for i in ims[::2]) + 10), (20, 16, 26))
    y = 0
    for k in range(0, len(ims), 2):
        for j, im in enumerate(ims[k:k + 2]):
            sheet.paste(im, (j * w, y))
        y += max(i.height for i in ims[k:k + 2])
    sheet.save(os.path.join(OUT, "estruturas.png"))
    print("previews:", OUT)


if __name__ == "__main__":
    main()
