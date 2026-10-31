"""Spinosaurus aegyptiacus, hand-made rig in the T. rex standard (4th species of the new standard, first one built on
the shared engine + the big-theropod body plan).

Research (sizes only, nothing copied):
  - ~14 m, ~7 t (Ibrahim et al. 2014, 2020; Sereno et al. 2022).
  - Skull long, low and narrow; the tip widens into a rosette of big procumbent teeth with a notch behind it where
    the lower rosette fits; nostrils far back near the eyes; a small fluted crest on the nasals (dal Sasso et al. 2005).
    Conical, unserrated, interlocking teeth.
  - Sail of neural spines up to 1.65 m, tallest over the rear of the trunk, lower over the hips and onto the tail
    (Ibrahim et al. 2014). Tail tall and paddle-like: long neural spines above and long chevrons below (Ibrahim 2020).
  - Long S-shaped neck; robust arms with a big hooked thumb claw; short hind legs, broad flat claws, hallux long
    enough to touch the ground (Ibrahim 2014).

Drawn at 16 px per metre like the T. rex (one texel = one Minecraft pixel), the skull ~1.2x for readability.
The sail and the tail paddle are 1 px thick panels painted with a cut-out outline (GeckoLib renders cut-out), so the
curve is a pixel-art line, never a staircase of cubes (that was what made the old model read as voxel noise).

Three marks of the species: the sail (dark spine ribs, crimson to bone in the male, ochre in the female), the heron
stripe through the eye, and dark bars on the tail paddle.
"""
import math
import zlib
import proto as P, geo, skin, qa
from proto import hx, h32

PAL = {
    # body: cool slate olive (river mud and wet stone), not the T. rex green
    "s0": hx("181c1c"), "s1": hx("252c2c"), "s2": hx("35403d"), "s3": hx("4a5650"), "s4": hx("64715f"), "s5": hx("838c72"),
    # belly and throat: sand
    "b0": hx("6c624b"), "b1": hx("958866"), "b2": hx("b7a982"), "b3": hx("d6caa1"),
    # sail (male): crimson to bone
    "r0": hx("3e1716"), "r1": hx("6e2420"), "r2": hx("9c3a28"), "r3": hx("c86a3c"), "tip": hx("e2c48c"), "rib": hx("2a1c1a"),
    "claw": hx("1f1a17"), "clawl": hx("cfc4a4"),
    "tooth": hx("efe8d0"), "tooth2": hx("c4b892"), "gum": hx("7a2a2c"), "mouth": hx("3a1618"), "tongue": hx("a8473f"),
    "eye": hx("d9c24e"), "eye2": hx("9a7f26"), "eye_hi": hx("f6e78a"), "pupil": hx("120d0c"), "glint": hx("fff6cf"),
    "stripe": hx("121414"),
}
UP = {"s0": "s1", "s1": "s2", "s2": "s3", "s3": "s4", "s4": "s5", "s5": "s5", "b0": "b1", "b1": "b2", "b2": "b3", "b3": "b3",
      "r0": "r1", "r1": "r2", "r2": "r3", "r3": "tip"}
DN = {v: k for k, v in UP.items() if k != v}; DN.update({"s0": "s0", "b0": "s3", "r0": "rib"})

FEMALE = {
    "s0": hx("1c1b18"), "s1": hx("2b2924"), "s2": hx("3d3a31"), "s3": hx("524d40"), "s4": hx("6b6552"), "s5": hx("888168"),
    "r0": hx("33261a"), "r1": hx("574129"), "r2": hx("7c5f37"), "r3": hx("a3844e"), "tip": hx("cdb98a"), "rib": hx("241d17"),
}

SHIFT = [0.0]        # how far build() moved the model so the feet touch y = 0 (the outlines below are pre-shift)
SAIL_Z = (-44.0, 22.0)


def dorsal(z):
    """top of the sail / tail paddle outline at z (pre-shift y), one curve along the whole animal"""
    z0, z1 = SAIL_Z
    if z <= z1:
        x = min(1.0, max(0.0, (z - z0) / (z1 - z0)))
        pk = 0.6
        h = math.sin(0.5 * math.pi * x / pk) ** 1.5 if x < pk else math.cos(0.5 * math.pi * (x - pk) / (1 - pk)) ** 0.7
        return 57.0 + 3 * (1 - x) + 32 * h
    # over the hips and down the tail: drops to the tail top, then the paddle swells again mid-tail
    u = z - z1
    base = 59 - 0.3 * u                        # the low hip spines running into the tail top
    paddle = 15 * math.sin(math.pi * min(1, max(0, (z - 44) / 86)) ** 0.8) ** 1.1
    return max(base, 50 + paddle - 0.06 * u)


def ventral(z):
    """bottom of the tail paddle (chevrons), pre-shift y"""
    s = math.sin(math.pi * min(1, max(0, (z - 48) / 82)) ** 0.85) ** 1.1
    return 43 - 10 * s + 0.03 * (z - 50)


def build():
    m = P.Model("spinosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 46, 2))
    m.cube(body, (-11, 30, -40), (11, 54, 4), name="torso")
    m.cube(body, (-9, 26, -37), (9, 31, -12), name="chest", mat="belly")
    m.cube(body, (-10, 35, 2), (10, 55, 21), name="rump")
    m.cube(body, (-2.5, 52, -41), (2.5, 57, 20), name="spine_ridge", mat="ridge")
    m.cube(body, (-0.5, 54, -44), (0.5, 88, 22), name="sail", mat="sail", faces=["east", "west"])

    # long S neck: rises from the shoulders, bends forward, the head held low and level
    neck = m.bone("neck", body, (0, 46, -36), (58, 0, 0))
    m.cube(neck, (-8, 36, -55), (8, 53, -34), name="neck")
    m.cube(neck, (-6.5, 33, -53), (6.5, 37, -37), name="throat", mat="belly")
    m.cube(neck, (-1.5, 52, -54), (1.5, 55, -36), name="neck_ridge", mat="ridge")
    neck2 = m.bone("neck2", neck, (0, 45, -53), (-34, 0, 0))
    m.cube(neck2, (-6.5, 37, -69), (6.5, 51, -51), name="neck2")
    m.cube(neck2, (-5.5, 35, -67), (5.5, 38, -53), name="throat2", mat="belly")
    m.cube(neck2, (-1, 50, -68), (1, 53, -52), name="neck2_ridge", mat="ridge")

    head = m.bone("head", neck2, (0, 45, -67))
    skull = m.bone("skull", head, (0, 45, -67), (-30, 0, 0))
    m.cube(skull, (-7, 38, -80), (7, 52, -65), name="cranium")
    m.cube(skull, (-4.5, 39, -108), (4.5, 46, -78), name="snout", rot=(-3, 0, 0), origin=(0, 46, -78))
    m.cube(skull, (-4, 43, -92), (4, 49, -77), name="nasal", rot=(-16, 0, 0), origin=(0, 50, -77))
    m.cube(skull, (-1, 48, -88), (1, 53, -79), name="crest", mat="crest", rot=(-14, 0, 0), origin=(0, 50, -79))
    m.cube(skull, (-5.5, 38, -117), (5.5, 46, -106), name="rosette", rot=(-6, 0, 0), origin=(0, 46, -106))
    m.pair(skull, skull, (5, 50, -77), (8, 52, -69), name="brow", mat="ridge")
    m.pair(skull, skull, (6, 38, -78), (8, 46, -68), name="cheek")
    # teeth: alpha planes hanging from the upper jaw, the rosette ones longer
    m.pair(skull, skull, (4.2, 36.5, -104), (4.2, 39.5, -79), name="teeth_up", mat="teeth", rot=(-3, 0, 0), origin=(0, 46, -78))
    m.pair(skull, skull, (5.2, 34, -116), (5.2, 38, -107), name="teeth_ros", mat="teeth", rot=(-6, 0, 0), origin=(0, 46, -106))
    jaw = m.bone("jaw", skull, (0, 41, -70))
    m.cube(jaw, (-6.5, 33.5, -80), (6.5, 39.5, -66), name="jaw_back")      # starts under the cranium: no stub at the mouth corner
    m.cube(jaw, (-4, 34.5, -106), (4, 39.5, -80), name="jaw_front", rot=(-3, 0, 0), origin=(0, 39.5, -80))
    m.cube(jaw, (-5, 33.5, -115), (5, 39.5, -106), name="jaw_ros", rot=(-4, 0, 0), origin=(0, 39, -104))
    m.pair(jaw, jaw, (3.7, 39.5, -103), (3.7, 42.5, -82), name="teeth_lo", mat="teeth_lo", rot=(-3, 0, 0), origin=(0, 39.5, -80))
    m.pair(jaw, jaw, (4.7, 39.5, -114), (4.7, 42.5, -106), name="teeth_lo_ros", mat="teeth_lo", rot=(-4, 0, 0), origin=(0, 39, -104))

    # robust arms with the big hooked thumb claw
    for side, sx in (("l", 1), ("r", -1)):
        arm = m.bone(f"arm_{side}", body, (10 * sx, 37, -31), (38, 0, 0))
        fore = m.bone(f"forearm_{side}", arm, (11.5 * sx, 26, -30), (-88, 0, 0))
        m.bone(f"hand_{side}", fore, (11.5 * sx, 16, -30), (20, 0, 0))
    m.pair("arm_l", "arm_r", (9, 25, -34), (14, 39, -27), name="arm")
    m.pair("forearm_l", "forearm_r", (9.5, 15, -33), (13.5, 27, -28), name="forearm")
    m.pair("hand_l", "hand_r", (10, 11, -32.5), (13, 16, -28.5), name="hand")
    m.pair("hand_l", "hand_r", (12.5, 5, -33.5), (14.5, 12, -30.5), name="thumb", mat="claw", rot=(-22, 0, 0), origin=(13.5, 12, -32))
    m.pair("hand_l", "hand_r", (10, 7.5, -32.5), (11, 11.5, -30.5), name="finger1", mat="claw", rot=(-30, 0, 0), origin=(10.5, 11.5, -31.5))
    m.pair("hand_l", "hand_r", (11.5, 7.5, -32.5), (12.5, 11.5, -30.5), name="finger2", mat="claw", rot=(-30, 0, 0), origin=(12.2, 11.5, -31.5))

    # short, strong hind legs; broad flat-clawed feet with the hallux on the ground
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (12.5 * sx, 48, 6), (20, 0, 0))
        sh = m.bone(f"shin_{side}", th, (12.5 * sx, 23, 6), (-54, 0, 0))
        mt = m.bone(f"foot_{side}", sh, (12.5 * sx, 3, 7), (42, 0, 0))
        m.bone(f"toes_{side}", mt, (12.5 * sx, -9, 7), (-8, 0, 0))
    m.pair("thigh_l", "thigh_r", (6, 19, -8), (19, 54, 17), name="thigh")
    m.pair("shin_l", "shin_r", (8, 0, 0), (17, 25, 12), name="shin")
    m.pair("foot_l", "foot_r", (9, -10, 3), (16, 5, 10), name="meta")
    m.pair("toes_l", "toes_r", (6.5, -13, -10), (18.5, -9, 9), name="foot")
    m.pair("toes_l", "toes_r", (7, -13, -13), (10, -10, -10), name="claw1", mat="claw")
    m.pair("toes_l", "toes_r", (11, -13, -14), (14, -10, -10), name="claw2", mat="claw")
    m.pair("toes_l", "toes_r", (15, -13, -13), (18, -10, -10), name="claw3", mat="claw")
    m.pair("toes_l", "toes_r", (5, -13, 5), (7, -11, 9), name="hallux", mat="claw")

    # tail: five segments carrying the paddle (neural spines above, chevrons below)
    segs = [("tail1", (0, 47, 20), 9, 19, 48), ("tail2", (0, 47, 46), 7.5, 15, 72), ("tail3", (0, 47, 70), 5.5, 12, 96),
            ("tail4", (0, 47, 94), 3.5, 8, 116), ("tail5", (0, 47, 114), 2, 5, 132)]
    parent = body
    for k, (name, piv, hw, hh, z1) in enumerate(segs):
        b = m.bone(name, parent, piv, (-3 if k == 0 else 1, 0, 0))
        z0 = piv[2]
        m.cube(b, (-hw, piv[1] - hh * 0.5, z0), (hw, piv[1] + hh * 0.5, z1), name=name)
        top = max(dorsal(z) for z in range(int(z0), int(z1) + 1))
        if top > piv[1] + hh * 0.5 + 1:
            m.cube(b, (-0.5, math.floor(piv[1] + hh * 0.5 - 2), z0 - (2 if k else 1)), (0.5, math.ceil(top) + 1, z1), name=f"{name}_fin",
                   mat="fin", faces=["east", "west"])
        bot = min(ventral(z) for z in range(int(z0), int(z1) + 1))
        if k >= 1 and bot < piv[1] - hh * 0.5 - 1:
            m.cube(b, (-0.5, math.floor(bot) - 1, z0 - 2), (0.5, math.ceil(piv[1] - hh * 0.5 + 2), z1), name=f"{name}_keel",
                   mat="fin", faces=["east", "west"])
        parent = b

    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes}) if c["mat"] not in ("teeth", "teeth_lo"))
    m.shift(-lo); SHIFT[0] = -lo
    return m


# ---------------------------------------------------------------- painting
BODY = ("torso", "rump", "neck", "neck2", "tail1", "tail2", "tail3", "tail4", "tail5")


def bands(t):
    """dark crossbars from the hips down the tail (crocodile-like), ragged edges; 'core' | 'rim' | None"""
    n = t.cube["name"]
    if n not in ("rump", "tail1", "tail2", "tail3", "tail4", "tail5", "thigh") or t.face not in ("east", "west", "up"): return None
    z = t.L[2] + 0.35 * (t.L[1] - SHIFT[0] - 47)
    per = 11 if n != "thigh" else 13
    k = math.floor((z - 4) / per); z0 = k * per + 4 + h32(k, 31) % 4
    half = 2.2 + (h32(k, 37) % 3) * 0.6
    depth = 1.0 if t.face == "up" else (t.rel[1] - 0.30) / 0.70
    if depth <= 0: return None
    dz = z - z0
    if abs(dz) <= half * (0.6 + 0.4 * depth): return "core"
    if abs(dz) <= half * (0.6 + 0.4 * depth) + 1: return "rim"
    return None


def blotch(t):
    """broken rows of dark blotches along the flanks and the neck"""
    if t.cube["name"] not in ("torso", "neck", "neck2") or t.face not in ("east", "west"): return False
    u, v = skin.face_uv_coords(t)
    d1, d2, c = skin.voronoi(u, v * 1.3, cell=6.5, seed=7)
    return h32(c[0], c[1], 3) % 3 == 0 and d1 < 1.9 and t.rel[1] > 0.4


def sail_px(t, p, top):
    """the sail and the tail paddle: a smooth membrane edge, spine ribs every 6 px leaning back (their tips just
    break the edge), the membrane from body colour to crimson to bone"""
    y = t.L[1] - SHIFT[0]; z = t.L[2]
    lean = 0.16 * (y - 54)
    col = int(math.floor(z - lean)); k = col % 6
    rib = k == 0
    edge = top + (0.6 if rib and t.cube["mat"] == "sail" else 0.0)
    if y > edge: return None
    if t.cube["mat"] == "sail":
        g = max(0.0, min(1.0, (y - 57) / max(1.0, top - 57)))
        tone = "s2" if g < 0.08 else ("r0" if g < 0.22 else ("r1" if g < 0.5 else ("r2" if g < 0.78 else "r3")))
        if y > top - 1.5: tone = "tip"
        if rib: tone = "rib" if g < 0.78 else "r1"
        elif k == 1 and 0.08 <= g < 0.78: tone = DN[tone]                           # shadow beside each spine
        elif 0.3 < g < 0.75 and h32(col // 3, int(y) // 4, 5) % 7 == 0: tone = UP[tone]   # pale blotches
        return p[tone]
    # tail paddle: body colours, the tail bars run through it, pale rim, spines faint
    bar = ((z + 0.35 * (y - 47) - 4) % 11) < 4.5
    tone = "s3" if (y - 47) < 0.55 * (top - 47) else "s4"
    if bar: tone = "s1" if tone == "s3" else "s2"
    if y > top - 1.2: tone = "s5"
    elif rib: tone = DN[tone]
    return p[tone]


def keel_px(t, p, bot):
    y = t.L[1] - SHIFT[0]; z = t.L[2]
    col = int(math.floor(z + 0.15 * (y - 40))); k = col % 6
    if y < bot: return None
    bar = ((z - 0.35 * (y - 47) - 4) % 11) < 4.5
    tone = "s1" if bar else "s3"
    if y < bot + 1.2: tone = "b1"
    elif k == 0: tone = DN[tone]
    return p[tone]


def shader(t):
    c = t.cube; n = c["name"]; f = t.face; v = t.rel[1]; p = PAL; mat = c["mat"]
    u_, w_ = skin.face_uv_coords(t)
    if mat == "sail":
        return sail_px(t, p, dorsal(t.L[2]))
    if mat == "fin":
        if n.endswith("_keel"): return keel_px(t, p, ventral(t.L[2]))
        return sail_px(t, p, dorsal(t.L[2]))
    if mat == "teeth":                          # conical, spaced, interlocking: every other gap takes a lower tooth
        if f not in ("east", "west"): return None
        col = int(t.L[2]); row = t.h - 1 - t.j
        ros = n == "teeth_ros"; spacing = 3 if ros else 4; k = (col + 400) % spacing
        if ros and t.L[2] > -108.5: return None          # nothing hangs in the notch behind the rosette (seen in game)
        size = (4 if ros else 2) + (h32(col // spacing, 5) % 2)
        if row >= t.h - 1: return p["gum"]
        if k == 0 and row >= t.h - 1 - size: return p["tooth"] if row > t.h - 1 - size else p["tooth2"]
        return None
    if mat == "teeth_lo":
        if f not in ("east", "west"): return None
        col = int(t.L[2]); row = t.j
        ros = n == "teeth_lo_ros"; spacing = 3 if ros else 4; k = (col + 402) % spacing
        if ros and t.L[2] > -107.5: return None
        size = (3 if ros else 2) + (h32(col, 6) % 2)
        if row == t.h - 1: return p["gum"]
        if k == 0 and row >= t.h - 1 - size: return p["tooth2"] if row == t.h - 1 - size else p["tooth"]
        return None
    if mat == "claw":
        return p["clawl"] if (f in ("north", "down") and t.j >= t.h - 2) or (f == "up" and t.j == 0) else p["claw"]
    if mat == "crest":
        # fluted nasal crest: grooves along it, pale top
        if f == "up": return p["s4"]
        return p["s1"] if t.i % 3 == 0 else p["s3"]
    if mat == "ridge":
        if f == "up": return p["s1"] if (t.j % 4 == 0) else p["s2"]
        if f == "down": return p["s0"]
        return p["s1"] if t.j == t.h - 1 else (p["s3"] if (t.i % 4) else p["s2"])
    if mat == "belly" or f == "down":
        sc = skin.scutes(t.L[0] + (0 if f == "down" else t.L[2]), t.L[2] if f == "down" else t.L[1], row=3, width=6)
        return p[{"seam": "b0", "hi": "b2", "base": "b1"}[sc]]
    limb = n in ("shin", "meta", "foot", "forearm", "arm", "hand")
    if limb:
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 3
        base = "s3" if (f in ("north", "up")) else "s2"
        if n == "foot" and f == "up":                  # webbing between the toes
            return p["s1"] if t.i in (3, 4, 7, 8) else p["s3"]
        if f in ("east", "west", "north", "south") and k == 0 and (t.i % 4) != 1: return p[DN[base]]
        return p[base]
    if n in ("jaw_back", "jaw_front", "jaw_ros"):
        base = "b1" if v < 0.45 else "s3"; cell = 2.6
    elif n in ("snout", "rosette", "nasal"):
        base = "s3" if v < 0.55 else "s2"; cell = 2.8
        if f == "up": base = "s2"
    elif n in ("cranium", "cheek"):
        base = "s3" if v < 0.6 else "s2"; cell = 3.4
        if f == "up": base = "s2"
    elif n == "thigh":
        base = "s3" if v > 0.3 else "s4"; cell = 5.0
    else:
        jag = (0, 0, 1, 1, 1, 0)[int(t.L[2] // 3) % 6] / max(1, t.h)
        if f in ("east", "west", "north", "south") and v < 0.24 + jag:
            sc = skin.scutes(u_, w_, row=3, width=6)
            return p[{"seam": "b0", "hi": "b2", "base": "b1"}[sc]]
        if f in ("east", "west", "north", "south") and v < 0.24 + jag + 1.5 / max(1, t.h):
            return p["b0"]
        base = "s4" if (f != "up" and v < 0.5) else ("s3" if (f != "up" and v < 0.78) else "s2")
        cell = {"s4": 4.6, "s3": 5.4, "s2": 6.0}[base]
    b = bands(t)
    if b == "core": return p["s1"]
    if b == "rim": return p[DN[base]] if base != "s2" else p["s1"]
    if blotch(t): return p["s2"] if base != "s2" else p["s1"]
    if n == "thigh" and f in ("east", "west"):
        r = skin.ring(u_, w_, (c["from"][2] + c["to"][2]) / 2 + 1, c["from"][1] + 0.62 * (c["to"][1] - c["from"][1]), 8, 11)
        if r == "line": return p["s2"]
        if r == "hi": return p["s4"]
    sc = skin.scales(u_, w_, cell=cell, seed=zlib.crc32(n.encode()) % 97)
    if sc == "edge": return p[DN[base]]
    if sc == "hi": return p[UP[base]]
    return p[base]


def decals(img, m):
    C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
    pal = {"E": PAL["eye"], "e": PAL["eye2"], "Y": PAL["eye_hi"], "p": PAL["pupil"], "g": PAL["glint"], "D": PAL["stripe"],
           "d": PAL["s1"], "h": PAL["s4"], "H": PAL["s5"], "n": PAL["s0"], "b": PAL["b2"], "B": PAL["b1"], "o": PAL["s2"]}
    cr, sn, ns = C["cranium"], C["snout"], C["nasal"]
    # the heron stripe: from the nostril back through the eye to the back of the skull
    eye = [".DDDDDD.",
           "DYgYYYED",
           "DYYppEED",
           "DEEppEeD",
           ".DDDDDD."]
    P.stamp(img, m, cr, "east", ["nnnnnnnn.nnnnn", "dnnnnnnnnnnnd", "..dd.ddd..dd"], pal, at=(3, 3))
    P.stamp(img, m, cr, "east", eye, pal, at=(1, 1))
    P.stamp(img, m, cr, "east", ["hhhhhh", ".hhhh"], pal, at=(1, 6))           # pale lid line under the eye
    P.stamp(img, m, ns, "east", ["..nn", ".nnd", "..d."], pal, at=(3, 2))
    P.stamp(img, m, ns, "east", ["dddd.ddd.dd", ".d.dd.dd.d"], pal, at=(5, 1))
    # lip scales and mouth line on the snout, the rosette and the jaws
    lip = "".join("bB"[(i // 2) % 2] for i in range(40))
    for nm in ("snout", "rosette", "cranium"):
        P.stamp(img, m, C[nm], "east", [lip, "D" * 40], pal, at=(0, 0), anchor="front-bottom")
    for nm in ("jaw_front", "jaw_back", "jaw_ros"):
        P.stamp(img, m, C[nm], "east", ["D" * 30, lip], pal, at=(0, 0))
    P.stamp(img, m, sn, "east", ["h..h..h..h..h..h..h..h..h..h", ".h..h..h..h..h..h..h..h..h."], pal, at=(1, 0))
    # pits of the snout tip (pressure receptors, small dots on the rosette)
    P.stamp(img, m, C["rosette"], "east", [".d.d.d.d", "d.d.d.d.", ".d.d.d.d"], pal, at=(1, 2))
    w = C["rosette"]["uv"]["north"][2]
    P.stamp(img, m, C["rosette"], "north", [lip[:w], "D" * w], pal, at=(0, 0), anchor="front-bottom")
    # mouth interior
    for name in ("snout", "rosette", "jaw_front", "jaw_back", "jaw_ros"):
        c = C[name]; f = "down" if name in ("snout", "rosette") else "up"
        if f not in c["uv"]: continue
        u, v, ww, hh = c["uv"][f]
        for j in range(hh):
            for i in range(ww):
                rim = i in (0, ww - 1)
                col = PAL["gum"] if (rim or i in (1, ww - 2)) else (PAL["tongue"] if name in ("jaw_back", "jaw_front") and 2 <= i < ww - 2 else PAL["mouth"])
                img[v + j, u + i] = (*col, 255)
    # toes on the front of the foot
    ft = C["foot"]; u, v, ww, hh = ft["uv"]["north"]
    for j in range(hh):
        for i in range(ww):
            if i in (3, 7): img[v + j, u + i] = (*PAL["s0"], 255)


def paint_sex(m, sex):
    keep = dict(PAL)
    try:
        if sex == "female": PAL.update(FEMALE)
        return P.paint(m, shader, [decals, qa.clean_orphans])
    finally:
        PAL.clear(); PAL.update(keep)
