"""Model engine of the hand-made rigs (the 'new standard' of the 29/10 model study): few designed cubes, per-face UV (1 texel = 1 px), hand-pixel textures
built from a short palette, ASCII decals and deterministic designed stamps (no noise)."""
import json, math, hashlib
import numpy as np
from PIL import Image
import geo

def hx(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def h32(*a):
    return int(hashlib.md5(repr(a).encode()).hexdigest()[:8], 16)

class Model:
    def __init__(self, ident):
        self.id = ident; self.bones = []; self.cubes = []; self.decals = []
    def bone(self, name, parent, pivot, rot=(0, 0, 0)):
        self.bones.append({"name": name, "parent": parent, "origin": list(pivot), "rotation": list(rot)}); return name
    def cube(self, bone, frm, to, mat="skin", rot=(0, 0, 0), origin=None, name=None, mirror_of=None, faces=None, **kw):
        c = {"bone": bone, "from": list(frm), "to": list(to), "rotation": list(rot), "origin": list(origin or frm),
             "inflate": 0, "mat": mat, "name": name or f"{bone}#{len(self.cubes)}", "mirror_of": mirror_of,
             "faces": faces or geo.FACES, **kw}
        self.cubes.append(c); return c
    def pair(self, bone_l, bone_r, frm, to, **kw):
        """cube on the left (+x) and its mirror on the right, sharing texture."""
        a = self.cube(bone_l, frm, to, **kw)
        kw2 = dict(kw); 
        if 'origin' in kw2 and kw2['origin'] is not None: o = kw2['origin']; kw2['origin'] = [-o[0], o[1], o[2]]
        if 'rot' in kw2: r = kw2['rot']; kw2['rot'] = [r[0], -r[1], -r[2]]
        b = self.cube(bone_r, [-to[0], frm[1], frm[2]], [-frm[0], to[1], to[2]], mirror_of=a, **kw2)
        return a, b
    def shift(self, dy):
        for b in self.bones: b["origin"][1] += dy
        for c in self.cubes: c["from"][1] += dy; c["to"][1] += dy; c["origin"][1] += dy
    def spec(self):
        return {"bones": self.bones, "cubes": self.cubes, "tw": self.tw, "th": self.th}

# ---------------------------------------------------------------- UV packing (per face, mirrored pairs share)
def face_size(c, f):
    w, h, d = (int(round(c["to"][i] - c["from"][i])) for i in range(3))
    return {"north": (w, h), "south": (w, h), "east": (d, h), "west": (d, h), "up": (w, d), "down": (w, d)}[f]

def pack(m, width=256):
    rects = []
    for c in m.cubes:
        c["uv"] = {}
        if c["mirror_of"] is not None: continue
        sym = abs(c["from"][0] + c["to"][0]) < 1e-6   # centred cube: east and west share (mirrored)
        for f in c["faces"]:
            if sym and f == "west": continue
            w, h = face_size(c, f)
            if w > 0 and h > 0: rects.append((h, w, c, f))
    rects.sort(key=lambda r: (-r[0], -r[1]))
    x = y = rowh = 0
    for h, w, c, f in rects:
        if x + w > width: x = 0; y += rowh; rowh = 0
        c["uv"][f] = (x, y, w, h); x += w; rowh = max(rowh, h)
    H = y + rowh; th = 1
    while th < H: th *= 2
    m.tw, m.th = width, th
    for c in m.cubes:
        if c["mirror_of"] is None and abs(c["from"][0] + c["to"][0]) < 1e-6 and "east" in c["uv"] and "west" in c["faces"]:
            u, v, w, h = c["uv"]["east"]; c["uv"]["west"] = (u + w, v, -w, h)
    for c in m.cubes:
        if c["mirror_of"] is not None:
            src = c["mirror_of"]["uv"]; uv = {}
            for f, (u, v, w, h) in src.items():
                g = {"east": "west", "west": "east"}.get(f, f)
                uv[g] = (u + w, v, -w, h)
            c["uv"] = uv

# ---------------------------------------------------------------- painting
class Tx:
    """one texel of one face, at rest pose"""
    pass

def paint(m, shader, decals=()):
    img = np.zeros((m.th, m.tw, 4), np.uint8)
    F = {(id(c), f): cs for c, f, cs, r in geo.faces(m.spec())}
    for c in m.cubes:
        if c["mirror_of"] is not None: continue
        for f, (u, v, w, h) in c["uv"].items():
            if w < 0: continue
            cs = F[(id(c), f)]
            a, b, cc, d = (np.array(cs[k]) for k in ((0, 0), (1, 0), (0, 1), (1, 1)))
            lo = np.array(c["from"]); hi = np.array(c["to"])
            lc = geo.corners(f, lo, hi); la, lb, lcc, ld = (np.array(lc[k]) for k in ((0, 0), (1, 0), (0, 1), (1, 1)))
            for j in range(h):
                for i in range(w):
                    s = (i + .5) / w; t = (j + .5) / h
                    P = (a * (1 - s) + b * s) * (1 - t) + (cc * (1 - s) + d * s) * t
                    L = (la * (1 - s) + lb * s) * (1 - t) + (lcc * (1 - s) + ld * s) * t
                    tx = Tx(); tx.P = P; tx.L = L; tx.rel = (L - lo) / np.maximum(hi - lo, 1e-6)
                    tx.face = f; tx.cube = c; tx.i = i; tx.j = j; tx.w = w; tx.h = h
                    col = shader(tx)
                    if col is not None: img[v + j, u + i] = (*col, 255)
    for dc in decals:
        dc(img, m)
    return Image.fromarray(img, "RGBA")

def stamp(img, m, cube, face, ascii_rows, pal, at=(0, 0), anchor="front-top"):
    """Draw an ASCII decal on a face. anchor: where (0,0) of the art sits. For side faces 'front' = toward -z."""
    u, v, w, h = cube["uv"][face]
    rows = [r for r in ascii_rows]
    ah, aw = len(rows), max(len(r) for r in rows)
    fx, fy = at
    for r, row in enumerate(rows):
        for k, ch in enumerate(row):
            if ch in (' ', '.'): continue
            if face == "east":      # col 0 = back (+z), col w-1 = front (-z)
                col = (w - 1 - fx - k) if anchor.startswith("front") else fx + k
            elif face == "west":
                col = fx + k if anchor.startswith("front") else (w - 1 - fx - k)
            else:
                col = fx + k
            row_ = fy + r if anchor.endswith("top") else (h - 1 - fy - (ah - 1 - r))
            if 0 <= col < w and 0 <= row_ < h:
                c = pal[ch]
                img[v + row_, u + col] = (*c, 255) if len(c) == 3 else c

# ---------------------------------------------------------------- export
def geo_json(m):
    bones = []
    for b in m.bones:
        o = b["origin"]; r = b["rotation"]
        bj = {"name": b["name"], "pivot": [-o[0], o[1], o[2]]}
        if b["parent"]: bj["parent"] = b["parent"]
        if any(r): bj["rotation"] = [-r[0], -r[1], r[2]]
        cubes = []
        for c in m.cubes:
            if c["bone"] != b["name"]: continue
            s = [c["to"][i] - c["from"][i] for i in range(3)]
            cj = {"origin": [-c["to"][0], c["from"][1], c["from"][2]], "size": s, "uv": {}}
            if any(c["rotation"]):
                oo = c["origin"]; cj["pivot"] = [-oo[0], oo[1], oo[2]]; rr = c["rotation"]; cj["rotation"] = [-rr[0], -rr[1], rr[2]]
            for f, (u, v, w, h) in c["uv"].items():
                g = {"east": "west", "west": "east"}.get(f, f)   # bedrock mirrors x
                if g in ("east", "west"):
                    # GeckoLib runs u the other way on side faces (seen in game 29/10: the eye decal came out
                    # mirrored front-to-back on both sides), so flip u to keep "front" at the front
                    u, w = u + w, -w
                cj["uv"][g] = {"uv": [u, v], "uv_size": [w, h]}
            cubes.append(cj)
        if cubes: bj["cubes"] = cubes
        bones.append(bj)
    return {"format_version": "1.12.0", "minecraft:geometry": [{"description": {"identifier": f"geometry.{m.id}",
            "texture_width": m.tw, "texture_height": m.th}, "bones": bones}]}
