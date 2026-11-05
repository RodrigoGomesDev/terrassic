"""Elasmosaurus platyurus, made by hand from its own study (page "Elasmossauro: estudo para a 1.8", approved by Rodrigo on
05/11/2026: the shape, the "turquesa pintada" colour and its own neck saddle). A plesiosaur of the Western Interior
Seaway, 80.5 to 77 million years ago; 10.3 m (Sachs 2005), about 7 m of it neck with 72 vertebrae.

Drawn at 20 px = 1 m (game scale 0.8): 206 px long, the neck 140 px in seven bones of 20 px (neck1 at the shoulders to
neck7 behind the head), the skull 10 px.

What makes it itself (each point from the study):
- the NECK is not a swan's: held almost straight ahead and a little down; it bends a little, more to the sides and down
  than up (Zammit, Daniels & Kear 2008; Noè, Taylor & Gómez-Pérez 2017). Thick at the shoulders, thin behind the head;
- a small head with long needle teeth that cross like a trap, showing outside the closed mouth;
- a stiff broad trunk shaped like a drop, flat below (the basket of belly ribs);
- four long FLIPPERS, nearly alike, the hind pair a little longer, each a wing in three tapering pieces;
- a short tail with a small vertical fin at its tip, the rudder (Smith 2013).

The colour ("turquesa pintada", docs/CORES.md): dark teal above, counter-shaded to a pale belly (marine reptiles with
pigment in fossil skin, Lindgren et al. 2014); loose pale spots on the back and the neck like sunlight on a shallow
floor. The female a shade lighter with fewer spots. A golden eye.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 20

SCHEMES = {
    "turquesa": {
        "k0": "0f2a2c", "k1": "163a3c", "k2": "1f4c4f", "k3": "2d6266", "k4": "3d7a7e", "k5": "4f9094",
        "b0": "a9bfb8", "b1": "bfd2cc", "b2": "d4e2dc", "b3": "e4eee9",
        "sp": "a9c4bd", "sp2": "8fb2ac", "spots": 0.42,
        "female": {"k1": "1d4446", "k2": "285658", "k3": "3a7072", "k4": "4a888a", "k5": "5c9c9e", "spots": 0.24},
    },
}
SCHEME = ["turquesa"]

PAL = {
    "eyeY": hx("d8b04a"), "eyeE": hx("a8802a"), "pupil": hx("100e0b"), "glint": hx("f2ecd6"),
    "tooth": hx("ece4cc"), "tooth2": hx("c8bea4"), "mouth": hx("8a4a4e"), "gum": hx("a8686a"), "nost": hx("0a1414"),
}


def pal_for(sex, scheme=None):
    sc = SCHEMES[scheme or SCHEME[0]]
    p = dict(PAL)
    for k, v in sc.items():
        if k == "female": continue
        p[k] = hx(v) if isinstance(v, str) else v
    if sex != "male":
        for k, v in sc["female"].items(): p[k] = hx(v) if isinstance(v, str) else v
    p["male"] = sex == "male"
    return p


OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# neck segments from the shoulders to the head: (half width, y0, y1) at 20 px each; it tapers and drops a little
NECK = [(9, 9, 25), (8.5, 9.5, 24.5), (7.5, 10, 23), (6.5, 10.5, 21.5), (5.5, 11, 20), (5, 11, 19), (4, 11, 18)]
NECK_REST = (-3, -2, -2, -1, -1, -1, 0)      # a slight droop along the neck (degrees each)


def head(m, parent, z0):
    """the small skull with the needle teeth, the jaw hinged under the eye. z0: where the neck ends"""
    sk = m.bone("skull", parent, (0, 15, z0))
    m.cube(sk, (-4, 11, z0 - 6), (4, 19, z0 + 1), name="cranium")
    m.cube(sk, (-3, 12, z0 - 11), (3, 17, z0 - 5), name="snout", faces=OUT("south"))
    m.cube(sk, (-2, 12, z0 - 14), (2, 15, z0 - 10), name="tip", faces=OUT("south"))
    m.pair(sk, sk, (3, 17, z0 - 6), (5, 19, z0 - 2), name="brow", faces=OUT("west"))
    jaw = m.bone("jaw", sk, (0, 12, z0))
    m.cube(jaw, (-3.5, 9, z0 - 7), (3.5, 12, z0 + 1), name="jaw_back")
    m.cube(jaw, (-2.5, 10, z0 - 13), (2.5, 12, z0 - 6), name="jaw_front", faces=OUT("south"))
    # the needle teeth outside the closed mouth, crossing: upper ones down outside the jaw, lower ones up outside the
    # snout, uneven lengths (cubes thin in x so they read as needles from the side)
    for i, z in enumerate((z0 - 12, z0 - 9, z0 - 6)):
        x = 3 if z < z0 - 8 else 4
        m.pair(sk, sk, (x, 10, z), (x + 1, 12, z + 1), name=f"utooth{i}", mat="tooth", faces=OUT("up"))
    for i, z in enumerate((z0 - 11, z0 - 8)):
        x = 3 if z < z0 - 8 else 4
        m.pair(jaw, jaw, (x, 12, z), (x + 1, 14, z + 1), name=f"ltooth{i}", mat="tooth", faces=OUT("down"))
    return sk


def neck(m, body):
    parent = body
    z = -40
    for k, ((hw, y0, y1), r) in enumerate(zip(NECK, NECK_REST)):
        b = m.bone(f"neck{k + 1}", parent, (0, (y0 + y1) / 2, z), (r, 0, 0))
        m.cube(b, (-hw, y0, z - 21), (hw, y1, z + 1), name=f"neck{k + 1}")
        parent = b
        z -= 20
    hd = m.bone("head", parent, (0, 15, z))
    head(m, hd, z)


def flipper(m, body, side, sx, front):
    """a wing-shaped flipper in three tapering pieces, out to the side and a little back"""
    name = "fore" if front else "hind"
    z = -28 if front else 12
    ln = (16, 14, 10) if front else (17, 15, 11)
    wd = (14, 10, 6) if front else (15, 11, 6)
    th = ((8.5, 11.5), (9, 11), (9.5, 10.5))
    root = m.bone(f"{name}_{side}", body, (13 * sx, 10, z), (0, -18 * sx if front else -26 * sx, -6 * sx))
    x = 13
    parent = root
    for k, (L, Wd) in enumerate(zip(ln, wd)):
        b = parent if k == 0 else m.bone(f"{name}{k}_{side}", parent, (x * sx, 10, z), (0, -10 * sx, 0))
        x0, x1 = (x, x + L) if sx > 0 else (-x - L, -x)
        zc = z + (2 if k else 0)
        m.cube(b, (x0, th[k][0], zc - Wd / 2), (x1, th[k][1], zc + Wd / 2), name=f"{name}{k}_{side}",
               mat="flipper", fseg=k)
        if k < 2:     # the leading edge: a rounded bar one px proud above and below along the front third
            m.cube(b, (x0, th[k][0] - 1, zc - Wd / 2 - 0.5), (x1, th[k][1] + 1, zc - Wd / 2 + 3.5),
                   name=f"{name}{k}_lead_{side}", mat="flipper", fseg=k, lead=True)
        parent = b
        x += L - 1


def tail(m, body):
    segs = [("tail1", 20, 34, 8, 9, 21), ("tail2", 32, 46, 5, 10, 19), ("tail3", 44, 56, 3, 11, 17)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube(parent, (-1, 17, 47), (1, 22, 56), name="fin", mat="fin")          # the small rudder at the tip, upright


def saddle(m, body):
    """the neck saddle: a hide seat lashed just behind the base of the neck, a rope loop round the neck to hold, two
    floats of lashed driftwood on the sides (not the Mosasaurus' swim-bladder floats), a girth of twisted rope"""
    sd = m.bone("saddle", body, (0, 26, -30))
    m.cube(sd, (-9, 26, -38), (9, 28, -20), name="seat_pad", mat="hide", faces=OUT("down"))
    m.cube(sd, (-6, 28, -34), (6, 30, -22), name="seat", mat="hide", faces=OUT("down"))
    m.cube(sd, (-5, 28, -20), (5, 32, -18), name="cantle", mat="hide", faces=OUT("down"))
    m.cube(sd, (-10, 24, -44), (10, 26, -42), name="neck_loop", mat="rope")
    m.pair(sd, sd, (10, 16, -44), (11, 26, -42), name="neck_loop_side", mat="rope", faces=OUT("east"))
    m.pair(sd, sd, (16, 16, -36), (20, 20, -18), name="float", mat="drift")
    m.pair(sd, sd, (9, 19, -30), (15, 27, -28), name="float_tie", mat="rope", faces=OUT("east"))
    m.pair(sd, sd, (15, 5, -30), (16, 19, -28), name="girth_side", mat="rope", faces=OUT("east"))
    m.cube(sd, (-16, 4, -30), (16, 5, -28), name="girth_under", mat="rope", faces=OUT("up"))


def build(sex="male", saddle_on=False):
    m = P.Model("elasmosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 15, 0))
    # the trunk: a drop, broad and flat below, the widest just behind the fore flippers
    m.cube(body, (-14, 5, -36), (14, 25, 10), name="trunk")
    m.cube(body, (-16, 7, -26), (16, 22, 4), name="flank")
    m.cube(body, (-11, 7, -42), (11, 24, -35), name="shoulders")
    m.cube(body, (-11, 6, 9), (11, 23, 22), name="hips")
    m.cube(body, (-12, 4, -32), (12, 5, 6), name="belly", mat="belly", faces=OUT("up"))
    m.cube(body, (-10, 25, -30), (10, 26, 2), name="back", faces=OUT("down"))
    neck(m, body)
    for side, sx in (("l", 1), ("r", -1)):
        flipper(m, body, side, sx, True)
        flipper(m, body, side, sx, False)
    tail(m, body)
    if saddle_on: saddle(m, body)
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes}))
    m.shift(-lo)
    return m


def preview_faces(m):
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m


# ------------------------------------------------------------------ paint
STEP_DN = {"k5": "k4", "k4": "k3", "k3": "k2", "k2": "k1", "k1": "k0", "k0": "k0", "b3": "b2", "b2": "b1", "b1": "b0", "b0": "b0"}
SADDLE_PAL = {"H0": hx("3a2a1e"), "H1": hx("553f2c"), "H2": hx("6e543c"), "H3": hx("8a6c4e"),
              "R0": hx("6a5a3e"), "R1": hx("8e7c56"),
              "D0": hx("6e665a"), "D1": hx("8e8678"), "D2": hx("aaa294"), "D3": hx("c2bbae")}     # bleached driftwood
SADDLE_MATS = ("hide", "rope", "drift")


def saddle_px(t):
    c = t.cube; mat = c["mat"]; f = t.face; p = SADDLE_PAL; i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "hide":
        if f == "up": return p["H2"] if (i * 3 + j * 5) % 9 else p["H3"]
        return p["H0"] if j == h - 1 else p["H1"]
    if mat == "rope": return p["R1"] if (i + j) % 3 else p["R0"]
    if mat == "drift":
        if f == "up": return p["D3"] if (i + 2 * (j // 3)) % 5 else p["D2"]
        if f in ("north", "south"): return p["D1"] if (i + j) % 2 else p["D2"]     # the end grain of the logs
        return p["D2"] if j % 3 else p["D0"]
    return p["H2"]


def _spot(L, f, p, kind):
    """the pale spots: sunlight on a shallow floor. Placed in WORLD (model) space so they run across the cube seams;
    they gather in loose clouds on the back and the shoulders, thin out down the flanks and up the neck, and come in
    three sizes (a single texel, a pair, a small cross); none on the belly"""
    x, y, z = math.floor(L[0]), math.floor(L[1]), math.floor(L[2])
    cloud = 0.5 + 0.5 * math.sin(z * 0.09 + 1.1) * math.cos(x * 0.21 + z * 0.03)      # where the spots gather
    if z < -60: cloud *= 0.45                                                            # fewer up the neck
    if f in ("east", "west"): cloud *= 0.6                                               # fewer down the flanks
    density = p["spots"] * (0.4 + 1.6 * cloud)
    for cx, cy, cz, size in _spot_seeds(x, y, z):
        if (h32(cx, cy, cz, 77) % 1000) / 1000.0 >= density: continue
        dx, dy, dz = x - cx, y - cy, z - cz
        hit = (dx, dy, dz) == (0, 0, 0)
        if size == 2:      # a pair along the body
            hit = dx == 0 and dy == 0 and dz in (0, 1)
        elif size == 3:    # a small blot, 2 x 2 on whatever face it shows
            hit = dx in (0, 1) and dy in (0, 1) and dz in (0, 1)
        if hit:
            return "sp2" if kind == "up" else "sp"
    return None


def _spot_seeds(x, y, z):
    """one candidate spot in each 4 x 4 x 4 cell of model space around the texel, at a hashed point, of a hashed size"""
    out = []
    gx, gy, gz = x // 4, y // 4, z // 4
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            for dy in (-1, 0, 1):
                cx, cy, cz = gx + dx, gy + dy, gz + dz
                r = h32(cx, cy, cz, 5)
                out.append((cx * 4 + r % 4, cy * 4 + (r >> 2) % 4, cz * 4 + (r >> 4) % 4, 1 + (r >> 6) % 3))
    return out


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        c = t.cube; mat = c["mat"]; f = t.face; n = c["name"] or ""
        if mat in SADDLE_MATS: return saddle_px(t)
        if mat == "tooth": return p["tooth"] if t.j % 2 == 0 else p["tooth2"]
        u, v = skin.face_uv_coords(t)
        seed = zlib.crc32(n.encode()) % 97
        sc = skin.scales(u, v, cell=3.0, seed=seed)
        if mat == "belly" or f == "down":
            return p["b1"] if sc == "edge" else p["b2"]
        if mat == "fin":
            return p["k2"] if f != "up" else p["k1"]
        if mat == "flipper":
            # dark above with a pale trailing edge, pale below
            if f == "up":
                if t.j == t.h - 1: return p["b0"]
                return p["k1"] if sc == "edge" else p["k2"]
            return p["k1"] if f != "down" else p["b1"]
        if n in ("jaw_back", "jaw_front"):
            if f == "up": return p["mouth"]
            return p["b1"] if t.rel[1] < 0.6 else p["k3"]
        if f == "up":
            sp_ = _spot(t.L, f, p, "up")
            if sp_: return p[sp_]
            return p["k1"] if sc == "edge" else p["k2"]
        rel = t.rel[1]
        line = 0.32 + 0.05 * math.sin(t.L[2] * 0.25)
        if f in ("east", "west") and rel < line and not n.startswith(("cranium", "snout", "tip", "brow")):
            return p["b2"] if sc != "edge" else p["b1"]
        base = "k3" if rel < 0.7 else "k2"
        if rel > 0.45:
            sp_ = _spot(t.L, f, p, "side")
            if sp_: return p[sp_]
        return p[STEP_DN[base]] if sc == "edge" else p[base]
    return sh


def _col(u, w, i):
    return u + i if w > 0 else u - 1 - i


def decals_for(sex):
    p = pal_for(sex)

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        cr = C["cranium"]
        cmap = {"Y": p["eyeY"], "E": p["eyeE"], "p": p["pupil"], "g": p["glint"], "d": p["k0"]}
        eye = ["dddd", "dYgY", "dEpE", ".dd."]
        for f in ("east", "west"):
            u, v, w, h = cr["uv"][f]
            for j, row in enumerate(eye):
                for k, ch in enumerate(row):
                    if ch == ".": continue
                    i = (abs(w) - 2 - k) if f == "east" else (1 + k)
                    img[v + 1 + j, _col(u, w, i)] = (*cmap[ch], 255)
        sn = C["snout"]
        u, v, w, h = sn["uv"]["up"]
        img[v + h - 2, u + 1] = (*p["nost"], 255); img[v + h - 2, u + w - 2] = (*p["nost"], 255)
    return dec


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
