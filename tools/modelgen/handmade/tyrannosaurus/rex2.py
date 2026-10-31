"""T. rex v2 (the shipped model): same cube budget idea, but every face drawn with form (scales, scutes, muscle rings,
rimmed stripes), teeth as alpha planes, dorsal scutes, stronger hue-shifted palette."""
import math
import zlib
import proto as P, geo, skin
from proto import hx, h32

PAL = {
    "s0": hx("181c1a"), "s1": hx("242b25"), "s2": hx("323c2e"), "s3": hx("465036"), "s4": hx("5d6840"), "s5": hx("7c8650"),
    "r0": hx("4a2418"), "r1": hx("7e3820"), "r2": hx("b0592b"), "r3": hx("d68a45"),
    "b0": hx("7f6c40"), "b1": hx("a99252"), "b2": hx("cbb472"), "b3": hx("e6d69c"),
    "claw": hx("221a17"), "clawl": hx("dcd1b0"),
    "tooth": hx("f1ebd4"), "tooth2": hx("c9bd98"), "gum": hx("7a2629"), "mouth": hx("3a1418"), "tongue": hx("b0463f"),
    "lea0": hx("2e1d14"), "lea1": hx("4a2f1f"), "lea2": hx("6b4429"), "stitch": hx("b89b6a"),
    "bl0": hx("3c2318"), "bl1": hx("7a3a24"), "bl2": hx("9c5a33"), "bl3": hx("c9b27a"),
    "iron0": hx("47474a"), "iron1": hx("6e6e6a"), "iron2": hx("a3a39b"),
    # the saddle, in the colours of its item icon (tools/spritegen/rex_extras.py SADDLE_PAL)
    "sd_o": hx("261911"), "sd_d": hx("4a2f1f"), "sd_l": hx("6b4429"), "sd_h": hx("8c5e3a"), "sd_s": hx("b89b6a"),
    "sd_r": hx("7a3a24"), "sd_R": hx("9c5a33"), "sd_b": hx("c9b27a"), "sd_k": hx("3c2318"), "sd_i": hx("6e6e6a"),
    "sd_I": hx("a3a39b"), "sd_t": hx("f1ebd4"), "sd_T": hx("c9bd98"),
    "eye": hx("e8a92f"), "eye_hi": hx("ffdf6e"), "eye2": hx("b8741f"), "pupil": hx("130d0c"), "glint": hx("fff3c6"), "lid": hx("141210"),
}
UP = {"s0": "s1", "s1": "s2", "s2": "s3", "s3": "s4", "s4": "s5", "s5": "s5", "b0": "b1", "b1": "b2", "b2": "b3", "b3": "b3", "r0": "r1", "r1": "r2", "r2": "r3", "r3": "r3"}
DN = {v: k for k, v in UP.items() if k != v}; DN.update({"s0": "s0", "b0": "b0", "r0": "r0"})

def build(saddle=True):
    m = P.Model("tyrannosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 52, 4))
    m.cube(body, (-14, 34, -38), (14, 68, 6), name="torso")
    m.cube(body, (-12, 28, -36), (12, 35, -14), name="chest", mat="belly")
    m.cube(body, (-12, 41, 2), (12, 70, 22), name="rump")
    for k, z in enumerate((-30, -20, -10, 0)):
        m.pair(body, body, (2, 67, z), (4, 69, z + 4), name=f"scute_t{k}", mat="scute")
    for k, z in enumerate((9, 16)):
        m.pair(body, body, (2, 69, z), (4, 71, z + 4), name=f"scute_r{k}", mat="scute")
    neck = m.bone("neck", body, (0, 58, -34), (28, 0, 0))
    m.cube(neck, (-11, 46, -52), (11, 70, -32), name="neck")
    m.cube(neck, (-9, 42, -50), (9, 47, -36), name="throat", mat="belly")
    m.pair(neck, neck, (2, 69, -48), (4, 71, -44), name="scute_n0", mat="scute")
    m.pair(neck, neck, (2, 69, -41), (4, 71, -37), name="scute_n1", mat="scute")
    head = m.bone("head", neck, (0, 62, -50))
    skull = m.bone("skull", head, (0, 62, -50), (-28, 0, 0))
    m.cube(skull, (-13, 53, -74), (13, 78, -50), name="cranium")
    m.cube(skull, (-10, 54, -98), (10, 73, -72), name="snout", rot=(-9, 0, 0), origin=(0, 74, -72))
    m.cube(skull, (-4, 72, -96), (4, 75, -70), name="nasal", mat="ridge_g", rot=(-9, 0, 0), origin=(0, 74, -72))
    m.pair(skull, skull, (12, 54, -72), (15, 64, -55), name="cheek")
    m.pair(skull, skull, (7, 77, -77), (11, 80, -71), name="brow", mat="horn", rot=(-6, 0, 0), origin=(9, 77, -74))
    m.pair(skull, skull, (9, 76, -64), (12, 79, -56), name="boss", mat="horn")
    m.pair(skull, skull, (10, 74, -76), (14, 77, -63), name="brow_ridge", mat="ridge")
    # upper teeth: alpha plane between snout side (x=10) and jaw side (x=9)
    m.pair(skull, skull, (9.5, 51, -97), (9.5, 55, -73), name="teeth_up", mat="teeth", rot=(-9, 0, 0), origin=(0, 74, -72))
    m.pair(skull, skull, (13.5, 50, -72), (13.5, 54, -60), name="teeth_up2", mat="teeth")
    jaw = m.bone("jaw", skull, (0, 55, -55))
    m.cube(jaw, (-12, 45, -73), (12, 55, -52), name="jaw_back")
    m.cube(jaw, (-9, 46, -96), (9, 55, -72), name="jaw_front", rot=(-4, 0, 0), origin=(0, 55, -72))
    m.pair(jaw, jaw, (8.5, 55, -95), (8.5, 58, -73), name="teeth_lo", mat="teeth_lo", rot=(-4, 0, 0), origin=(0, 55, -72))
    for side, sx in (("l", 1), ("r", -1)):
        arm = m.bone(f"arm_{side}", body, (13 * sx, 42, -30), (35, 0, 0))
        m.bone(f"forearm_{side}", arm, (14.5 * sx, 35, -30), (-70, 0, 0))
    m.pair("arm_l", "arm_r", (13, 34, -32), (17, 43, -28), name="arm")
    m.pair("forearm_l", "forearm_r", (13.5, 28, -32), (16.5, 36, -29), name="forearm")
    m.pair("forearm_l", "forearm_r", (13.5, 25, -32), (16.5, 28, -29), name="hand", mat="claw")
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (15 * sx, 56, 2), (20, 0, 0))
        sh = m.bone(f"shin_{side}", th, (15 * sx, 28, 2), (-56, 0, 0))
        mt = m.bone(f"foot_{side}", sh, (15 * sx, 6, 3), (44, 0, 0))
        m.bone(f"toes_{side}", mt, (15 * sx, -6, 3), (-8, 0, 0))
    m.pair("thigh_l", "thigh_r", (8, 24, -13), (22, 62, 15), name="thigh")
    m.pair("shin_l", "shin_r", (10, 4, -3), (20, 32, 8), name="shin")
    m.pair("foot_l", "foot_r", (11, -8, -1), (19, 8, 7), name="meta")
    m.pair("toes_l", "toes_r", (9, -10, -15), (21, -5, 7), name="foot")
    m.pair("toes_l", "toes_r", (10, -10, -18), (12, -7, -15), name="claw1", mat="claw")
    m.pair("toes_l", "toes_r", (14, -10, -19), (16, -7, -15), name="claw2", mat="claw")
    m.pair("toes_l", "toes_r", (18, -10, -18), (20, -7, -15), name="claw3", mat="claw")
    t1 = m.bone("tail1", body, (0, 56, 20), (-3, 0, 0))
    m.cube(t1, (-11, 42, 18), (11, 66, 46), name="tail1")
    m.pair(t1, t1, (2, 65, 24), (4, 67, 28), name="scute_a0", mat="scute")
    m.pair(t1, t1, (2, 65, 34), (4, 67, 38), name="scute_a1", mat="scute")
    t2 = m.bone("tail2", t1, (0, 55, 44), (1, 0, 0))
    m.cube(t2, (-8, 46, 44), (8, 62, 70), name="tail2")
    t3 = m.bone("tail3", t2, (0, 55, 68), (1, 0, 0))
    m.cube(t3, (-5, 49, 68), (5, 59, 92), name="tail3")
    t4 = m.bone("tail4", t3, (0, 55, 90), (1, 0, 0))
    m.cube(t4, (-3, 51, 90), (3, 57, 108), name="tail4")
    # saddle: hidden in game unless saddled; left out of the rig the animations are baked on (rexanim), so it never
    # counts for the ground fit
    if saddle:
        add_saddle(m, body)
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes}) if c["mat"] not in ("teeth", "teeth_lo"))
    m.shift(-lo)
    return m

def add_saddle(m, body):
    """the item icon on the back (Rodrigo 31/10: simpler, like the icon): a plain leather seat with a high cantle and a
    small pommel on a narrow rust-and-bone band that drops a little down the flanks, one strap with an iron stirrup
    each side, an iron ring with a rex tooth on the left. No saddlebags drawn (the cargo still comes with the saddle).
    The faces lying on the body are left out: GeckoLib draws without back-face culling, so they would flicker. As in
    velociraptor/raptor.py, the inner face of a +x piece is "east" here (GeckoLib mirrors x once more)."""
    out = lambda *drop: [f for f in geo.FACES if f not in drop]
    sd = m.bone("saddle", body, (0, 72, -15))
    m.cube(sd, (-12, 68, -24), (12, 69.5, -8), name="band", mat="blanket", faces=out("down"))
    m.pair(sd, sd, (14, 61, -24), (15, 69.5, -14), name="band_side", mat="blanket", faces=out("east"))
    m.cube(sd, (-7, 69.5, -21), (7, 73, -9), name="seat", mat="leather", faces=out("down"))
    m.cube(sd, (-6, 73, -11), (6, 77, -8.5), name="cantle", mat="leather", rot=(-12, 0, 0), origin=(0, 73, -8.5))
    m.cube(sd, (-1.5, 73, -21), (1.5, 75.5, -18.5), name="pommel", mat="leather")
    m.pair(sd, sd, (15, 50, -19.5), (15.6, 61, -18), name="strap", mat="leather")
    m.pair(sd, sd, (14.5, 48, -21.5), (16.5, 50, -16), name="stirrup", mat="iron")
    m.cube(sd, (15, 57.5, -23.5), (16, 59.5, -22), name="ring", mat="iron")
    m.cube(sd, (15.2, 54, -23.3), (15.8, 57.5, -22.2), name="tooth", mat="tooth")

BODY = ("torso", "rump", "neck", "tail1", "tail2", "tail3", "tail4")

def stripe(t, base):
    """tapered 'flame' stripes from the spine, dark core with a warm rim on the front edge"""
    n = t.cube["name"]; v = t.rel[1]
    if n not in BODY + ("thigh",) or (t.face not in ("east", "west", "up")): return None
    depth = 1.0 if t.face == "up" else (v - 0.40) / 0.60
    if depth <= 0: return None
    z = t.P[2] + 0.55 * (t.P[1] - 60)
    per = 15; k = math.floor(z / per); z0 = k * per + 4 + h32(k, 4) % 6
    half = (1.8 + (h32(k, 7) % 3) * 0.8) * depth
    if h32(k, 11) % 6 == 0: return None
    dz = z - z0
    if abs(dz) <= half:
        if dz < -half + 1: return "r2"           # warm rim on the front edge
        return "r1" if depth < 0.85 else "r0"
    if abs(dz) <= half + 1 and depth > 0.15: return "s1"   # dark outline around the flame
    return None

def shader(t):
    c = t.cube; n = c["name"]; f = t.face; v = t.rel[1]; p = PAL; mat = c["mat"]
    u_, w_ = skin.face_uv_coords(t)
    if mat == "teeth":    # alpha plane: triangles hanging from the top edge
        if f not in ("east", "west"): return None
        col = int(t.L[2]) ; row = t.h - 1 - t.j   # row 0 = bottom
        spacing = 3; k = (col + 300) % spacing
        size = 3 if (h32(col // spacing, 5) % 3) else 2
        if row >= t.h - 1: return p["gum"]
        if k == 0 and row >= t.h - 1 - size: return p["tooth"] if row > 0 else p["tooth2"]
        if k == 1 and row >= t.h - size: return p["tooth2"]
        return None
    if mat == "teeth_lo":
        if f not in ("east", "west"): return None
        col = int(t.L[2]); row = t.j  # row 0 = top
        k = (col + 301) % 3
        if row == t.h - 1: return p["gum"]
        if k == 0 and row >= 0 + (h32(col, 6) % 2): return p["tooth2"] if row == t.h - 2 else p["tooth"]
        return None
    if mat == "leather":
        # the icon's leather: dark rim, plain body, light top edge, one stitched line along the sides
        if f == "up": return p["sd_d"] if t.i in (0, t.w - 1) or t.j in (0, t.h - 1) else p["sd_h"]
        if f == "down": return p["sd_d"]
        if t.j == 0: return p["sd_h"]
        if t.j == t.h - 1 or t.i in (0, t.w - 1): return p["sd_d"]
        if t.h >= 3 and t.j == t.h - 2 and t.i % 2 == 0: return p["sd_s"]
        return p["sd_l"]
    if mat == "blanket":
        # the icon's band: rust and bone stripes across, a lighter rust now and then, dark hem
        if f == "down" or (f in ("east", "west", "north", "south") and t.j == t.h - 1): return p["sd_k"]
        z = int(math.floor(t.L[2]))
        return p["sd_b"] if z % 2 else (p["sd_R"] if z % 5 == 0 else p["sd_r"])
    if mat == "iron":
        return p["sd_I"] if (f == "up" or t.j == 0) else p["sd_i"]
    if mat == "tooth":
        return p["sd_t"] if t.j < t.h - 1 else p["sd_T"]
    if mat == "claw":
        return p["clawl"] if (f == "north" and t.j >= t.h - 1) else p["claw"]
    if mat == "horn":
        return p["s4"] if (f == "up" and (t.i + t.j) % 3 == 0) else (p["s2"] if f == "up" else p["s1"])
    if mat == "ridge":
        # heavy brow over the eye: dark underside casts the socket shadow, rugose top with a rust edge
        if f == "down": return p["s0"]
        if f == "up": return p["r1"] if (t.i // 2 + t.j) % 3 == 0 else p["s3"]
        if t.j == t.h - 1: return p["s1"]
        return p["r1"] if t.j == 0 and t.i % 3 != 1 else p["s3"]
    if mat == "scute":
        return p["s4"] if f == "up" else p["s2"]
    if mat == "belly" or f == "down":
        sc = skin.scutes(t.L[0] + (0 if f == "down" else t.L[2]), t.L[2] if f == "down" else t.L[1], row=4, width=7)
        return p[{"seam": "b0", "hi": "b2", "base": "b1"}[sc]]
    # ---- base tone by region
    limb = n in ("shin", "meta", "foot", "forearm", "arm")
    if limb:
        # bird-like scutes across the shin and foot: rows every 3 px
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 4
        base = "s3" if (f == "north" or f == "up") else "s2"
        if f in ("east", "west", "north", "south") and k == 0 and (t.i % 5) != 2: return p[DN[base]]
        return p[base]
    if n in ("jaw_back", "jaw_front"):
        base = "b1" if v < 0.5 else "s3"
        cell = 2.8
    elif n == "nasal":
        # rugose nasal crest: lumpy bosses along the top
        if f == "up": return p["s4"] if (t.i // 2 + t.j // 3) % 3 == 0 else (p["s1"] if (t.i + t.j) % 5 == 0 else p["s3"])
        base = "s3"; cell = 3.0
    elif n == "cheek":
        base = "s3" if v > 0.4 else "s4"; cell = 3.5
    elif n in ("cranium", "snout"):
        base = "s3" if v < 0.62 else "s2"; cell = 4.2
        if f == "up": base = "s2"
    elif n == "thigh":
        base = "s3" if v > 0.3 else "s4"; cell = 5.5
    else:
        jag = (0, 0, 1, 1, 1, 0)[int(t.P[2] // 3) % 6] / max(1, t.h)
        if f in ("east", "west", "north", "south") and v < 0.22 + jag:
            sc = skin.scutes(u_, w_, row=4, width=7)
            return p[{"seam": "b0", "hi": "b2", "base": "b1"}[sc]]
        if f in ("east", "west", "north", "south") and v < 0.22 + jag + 1.5 / max(1, t.h):
            return p["b0"]
        base = "s4" if (f != "up" and v < 0.48) else ("s3" if (f != "up" and v < 0.74) else "s2")
        cell = {"s4": 5.0, "s3": 6.0, "s2": 7.0}[base]
    st = stripe(t, base)
    if st: return p[st]
    # muscle contour on the thigh and the shoulder
    if n == "thigh" and f in ("east", "west"):
        r = skin.ring(u_, w_, (c["from"][2] + c["to"][2]) / 2 + 1, c["from"][1] + 0.62 * (c["to"][1] - c["from"][1]), 9.5, 12.5)
        if r == "line": return p["s2"]
        if r == "hi": return p["s4"]
    if n == "torso" and f in ("east", "west"):
        r = skin.ring(u_, w_, -27, 46, 8, 9)
        if r == "line": return p["s2"]
        if r == "hi": return p["s4"]
    sc = skin.scales(u_, w_, cell=cell, seed=zlib.crc32(n.encode()) % 97)
    if sc == "edge": return p[DN[base]]
    if sc == "hi": return p[UP[base]]
    if sc == "alt": return p[base]
    return p[base]

def decals(img, m):
    C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
    pal = {"E": PAL["eye"], "e": PAL["eye2"], "Y": PAL["eye_hi"], "p": PAL["pupil"], "g": PAL["glint"], "l": PAL["lid"], "d": PAL["s1"], "D": PAL["s0"],
           "h": PAL["s4"], "H": PAL["s5"], "n": PAL["s0"], "b": PAL["b2"], "B": PAL["b1"], "o": PAL["s2"], "k": PAL["s3"], "r": PAL["r1"], "R": PAL["r2"]}
    eye = [".DDDDDDD.",
           "DYgYYYYED",
           "DYYppYEED",
           "DYYppEEED",
           "DEEEEEEeD",
           ".DDDDDDD.",
           "..hhhhh.."]
    cr, sn = C["cranium"], C["snout"]
    # rust streak behind the eye (postorbital), kept apart so it does not swallow the eye
    mask = ["rrrr....",
            "rRRrrr..",
            ".rrrrrr.",
            "...rrrrr"]
    P.stamp(img, m, cr, "east", mask, pal, at=(11, 2))
    P.stamp(img, m, cr, "east", eye, pal, at=(1, 2))
    # temporal fenestra shadow + jugal ridge highlight
    P.stamp(img, m, cr, "east", ["..oooo", ".oooooo", "oooooooo", ".oooooo", "...ooo"], pal, at=(11, 9))
    P.stamp(img, m, cr, "east", ["hhhhhhhhhh", ".hhhhhhh"], pal, at=(2, 15))
    # lip scales above the mouth line, mouth line
    lip = "".join("bB"[(i // 2) % 2] for i in range(40))
    P.stamp(img, m, sn, "east", [lip, "D" * 40], pal, at=(0, 0), anchor="front-bottom")
    P.stamp(img, m, cr, "east", [lip, "D" * 40], pal, at=(0, 0), anchor="front-bottom")
    # nostril + rugose snout ridge
    P.stamp(img, m, sn, "east", [".nnn", "nnnd", ".dd."], pal, at=(1, 2))
    P.stamp(img, m, sn, "east", ["h.h..h.h..h.h..h", ".h..h...h..h..h."], pal, at=(5, 0))
    # lower jaw: lip line on top + chin scales
    P.stamp(img, m, C["jaw_front"], "east", ["D" * 30, lip], pal, at=(0, 0))
    P.stamp(img, m, C["jaw_back"], "east", ["D" * 30, lip], pal, at=(0, 0))
    # front of snout
    w = sn["uv"]["north"][2]
    P.stamp(img, m, sn, "north", [".nn" + "." * (w - 6) + "nn.", "." * w], pal, at=(0, 3))
    P.stamp(img, m, sn, "north", [lip[:w], "D" * w], pal, at=(0, 0), anchor="front-bottom")
    P.stamp(img, m, C["jaw_front"], "north", ["D" * 20, lip[:18]], pal, at=(0, 0))
    # mouth interior: palate and tongue
    for name in ("snout", "jaw_front", "jaw_back"):
        c = C[name]; f = "down" if name == "snout" else "up"
        u, v, ww, hh = c["uv"][f]
        for j in range(hh):
            for i in range(ww):
                rim = i in (0, ww - 1)
                col = PAL["gum"] if (rim or i in (1, ww - 2)) else (PAL["tongue"] if name != "snout" and 3 <= i < ww - 3 else PAL["mouth"])
                if name == "snout" and not rim and i % 4 == 0 and j % 2 == 0: col = PAL["gum"]
                img[v + j, u + i] = (*col, 255)
    # feet: toes on the front, top scutes
    ft = C["foot"]; u, v, ww, hh = ft["uv"]["north"]
    for j in range(hh):
        for i in range(ww):
            if i in (3, 4, 7, 8): img[v + j, u + i] = (*PAL["s0"], 255)

HEAD_BONES = ("head", "skull", "jaw")
ROAR = {"neck": ((-12, 0, 0), (0, 0, 0)), "skull": ((14, 0, 0), (0, 0, 0)), "jaw": ((-38, 0, 0), (0, 0, 0))}


# the female: a browner, quieter coat (ochre instead of rust, olive-brown back), same marks and eyes
FEMALE = {
    "s0": hx("1d1b17"), "s1": hx("2b2a22"), "s2": hx("3b3a2c"), "s3": hx("504c36"), "s4": hx("69634a"), "s5": hx("857c5c"),
    "r0": hx("3f2a1a"), "r1": hx("6a4526"), "r2": hx("94673a"), "r3": hx("b88c55"),
}

def paint_sex(m, sex):
    keep = dict(PAL)
    try:
        if sex == "female": PAL.update(FEMALE)
        return P.paint(m, shader, [decals])
    finally:
        PAL.clear(); PAL.update(keep)
