"""Protoceratops andrewsi, made by hand from its own study (page "Protoceratops: estudo antes de modelar", approved
by Rodrigo on 01/11/2026 20:15Z with the "Penhasco" colours and 2.0 m).

Drawn at 48 px = 1 m (game scale 1/3), like the Velociraptor: a small animal needs more pixels per metre to carry
the same detail as the T. rex; at 40 px/m (the study's first figure) the eye would have been 2 px.

The head (each point from the study):
- huge for the body: 0.30 m from the beak to the jaw joint, and the frill rising 0.35 m behind it;
- a hooked parrot beak of dark keratin (rostral above, predentary below) with the two small peg teeth of the
  premaxilla just behind it;
- a low bump on the nose (taller on the male: the only trait that may differ between the sexes);
- the cheek bones flaring out and down into points, tipped with keratin;
- a big round eye facing forward-out, with a pale lid ring and a small brow (palpebral) over it;
- the frill: a broad plate tilted back, its sides (the squamosals) curving down like a low roof, so it reads as a
  wide fan from the front and as a rising band from the side. The two windows are only one tone darker, never two
  dark ovals: those read as eyes (the old model's mistake).
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 128
PX_M = 48
FRILL_TILT = 42          # degrees the frill plate leans back from vertical

SCHEMES = {
    "penhasco": {   # warm sand of the Flaming Cliffs; shadows lean to red-brown, lights to yellow
        "k0": "4e2f22", "k1": "603b2a", "k2": "7d5f42", "k3": "977552", "k4": "b08e64", "k5": "c6a676",
        "b0": "a99573", "b1": "bba783", "b2": "d0bd96", "b3": "e4d4ad",
        "r0": "5e3524", "r1": "74432c", "r2": "8a5233", "f0": "7a5a3f", "f1": "8d6a4b", "f2": "a98460", "f3": "c29d73", "rim": "e2cfa6", "flush": "b2553a",
        "female": {"flush": None},
    },
}
SCHEME = ["penhasco"]

PAL = {
    "beak0": hx("4a4239"), "beak1": hx("665d52"), "beak2": hx("867c6e"), "beak3": hx("b2a892"),
    "horn0": hx("3a2a20"), "horn1": hx("5a4332"), "horn2": hx("8a7058"),
    "iris": hx("6a4426"), "iris2": hx("8f6236"), "eyeY": hx("f2c14e"), "eyeE": hx("d99a2b"), "eyee": hx("9c6418"), "eyeD": hx("1e1712"), "pupil": hx("130d0a"), "glint": hx("efe6c8"), "lid": hx("d9c39b"),
    "lid2": hx("a58a64"), "nost": hx("3a261c"),
    "gum": hx("6b3a33"), "mouth": hx("3a1d1a"), "tongue": hx("a05a50"), "tooth": hx("efe7d0"),
}


def pal_for(sex, scheme=None):
    sc = SCHEMES[scheme or SCHEME[0]]
    p = dict(PAL)
    for k, v in sc.items():
        if k != "female": p[k] = hx(v)
    p["male"] = sex == "male"
    return p


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes}))
    m.shift(-lo)


def head(m, parent, hy, hz, sex="male", rest=(0, 0, 0)):
    """skull, jaw and frill. (hy, hz): the mouth line at the jaw joint; returns the skull bone"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    FR_Y[0] = hy + 8; HZ[0] = hz
    sk = m.bone("skull", parent, (0, hy + 5, hz), rest)
    # the skull: deep and short, the top line falling from the frill to the beak. Pieces overlap by 1 px instead
    # of touching (touching faces are coplanar and fight in GeckoLib); faces buried in a neighbour are left out.
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    m.cube(sk, *B(-5, -1, -6, 5, 9, 1), name="cranium")
    m.cube(sk, *B(-4, 0, -9, 4, 8, -5), name="face", faces=out("south"))
    m.cube(sk, *B(-3, 0, -12, 3, 7, -8), name="snout", faces=out("south", "down"))
    m.cube(sk, *B(-1.5, 1, -14, 1.5, 6, -11), name="rostral", mat="beak", faces=out("south"))
    m.cube(sk, *B(-1, -2, -15, 1, 2, -13), name="hook", mat="beak", faces=out("south"))       # the hooked tip
    # the nasal bump, taller on the male: one geo for both sexes, so each bump sits in its own bone and the renderer
    # hides the other sex's (DinoGeoModel: male_display / female_display)
    for disp, top in (("male_display", 9), ("female_display", 8)):
        bb = m.bone(disp, sk, (0, hy + 5, hz))
        m.cube(bb, *B(-1, 6, -11, 1, top, -7), name="nasal_bump" + ("" if top == 9 else "_f"), mat="bump", faces=out("down"))
    m.pair(sk, sk, *B(4.5, 7, -7, 6.5, 8, -2), name="palpebral", faces=out("west"))     # the small brow over the eye
    m.pair(sk, sk, *B(4, -2, -5, 6, 3, -1), name="jugal", faces=out("west"))        # the cheek flaring under the eye
    m.pair(sk, sk, *B(5, -4, -4, 7, -1, -2), name="epijugal", mat="horn", faces=out("up"))   # its keratin point
    m.cube(sk, *B(-4, 2, 0, 4, 10, 3), name="occiput", faces=out("north"))
    m.pair(sk, sk, *B(2.75, -1, -12, 2.75, 0, -9), name="pegs", mat="teeth")    # the two premaxillary peg teeth
    # the frill: its own bone at the top of the back of the skull, leaning back. A plate of stepped widths (a fan)
    fr = m.bone("frill", sk, (0, hy + 8, hz + 1), (FRILL_TILT, 0, 0))
    F = lambda x0, y0, z0, x1, y1, z1: ((x0, hy + 8 + y0, hz + 1 + z0), (x1, hy + 8 + y1, hz + 1 + z1))
    base = m.cube(fr, *F(-4, -3, 0, 4, 3, 2), name="frill_base", mat="frill", faces=out("up"))
    m.cube(fr, *F(-7, 3, 0, 7, 7, 2), name="frill_low", mat="frill", faces=out("up"))
    m.cube(fr, *F(-9, 7, 0, 9, 12, 2), name="frill_mid", mat="frill")
    m.cube(fr, *F(-7, 12, 0, 7, 15, 2), name="frill_top", mat="frill", faces=out("down"))
    m.cube(fr, *F(-4, 15, 0, 4, 16, 2), name="frill_crown", mat="frill", faces=out("down"))
    # the squamosals: the sides of the frill curving down toward the neck (a low roof seen from behind)
    m.pair(fr, fr, *F(3, -3, 1, 8, 8, 9), name="squam_low", mat="frill")
    m.pair(fr, fr, *F(6, 8, 1, 10, 13, 6), name="squam_mid", mat="frill")
    for c in m.cubes:        # the painter measures the plate from the bottom of its base (the model shifts later)
        if c["mat"] == "frill": c["fref"] = base
    # the jaw: hinged at the back, the dark predentary beak at the tip
    jaw = m.bone("jaw", sk, (0, hy + 1, hz - 1))
    m.cube(jaw, *B(-1.5, -4, -13, 1.5, 0, -9), name="predentary", mat="beak", faces=out("south", "up"))
    m.cube(jaw, *B(-2.5, -4.5, -10, 2.5, -0.5, -4), name="dentary", faces=out("south"))
    m.cube(jaw, *B(-3.5, -5, -5, 3.5, 0, 0), name="jaw_back")
    m.cube(jaw, *B(-3, -6, -4, 3, -5, 0), name="gular", mat="gular", faces=out("up"))
    return sk


def build_head_only(sex="male"):
    m = P.Model("protoceratops")
    root = m.bone("root", None, (0, 0, 0))
    n = m.bone("neck", root, (0, 14, 6))
    m.cube(n, (-4.5, 4, 2), (4.5, 16, 12), name="neck_stub")
    hd = m.bone("head", n, (0, 12, 0))
    head(m, hd, 10, 0, sex)
    _ground(m)
    return m


# ------------------------------------------------------------------ paint
def _ramp(p, k):
    return p[f"k{max(0, min(5, k))}"]


EYE_STYLE = ["ambar"]
# the eyes on trial (Rodrigo 21:03Z did not like the first one: a pale ring round a brown iris read as a target)
#   ambar: an amber iris round a black pupil, a glint, sunk in a dark socket under the brow (the house eye)
#   ave:   a big dark bird eye, one glint, only a thin pale lower lid
#   lid:   amber, wider than tall, a dark upper lid line and a pale lower lid
EYES = {
    # the house eye (T. rex, Velociraptor): an almond, not a ring; the pupil toward the front with more iris behind
    # it, the glint over it, shade low and at the back (the round 3 px eye read as a target, 02/11)
    "ambar": ["sdddds", "dYgYEd", "dYpEed", "dEpeed", ".dddd."],
    "ambar_v1": ["sssss", "sgYEs", "sEpEs", "seEes", ".sss."],
    "ave":   [".sss.", "sgDDs", "sDDDs", "sDDDs", ".LLL."],
    "lid":   ["ddddd", "dgYEd", "sEpEs", "seees", ".LLL."],
}


def eye_rows(style):
    return EYES[style]


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        c = t.cube; f = t.face; mat = c["mat"]; n = c["name"]
        i, j, w, h = t.i, t.j, t.w, t.h
        if mat == "beak":
            if f == "up": return p["beak2"]
            if f == "down": return p["beak0"]
            if n == "hook" and f in ("east", "west", "north"):
                return p["beak3"] if j >= h - 1 else p["beak1"]           # paler worn tip
            if n == "predentary" and f in ("east", "west", "north"):
                return p["beak2"] if j == 0 else p["beak1"]
            return p["beak2"] if j == 0 else p["beak1"]
        if mat == "horn":       # the epijugal point: skin at the root, keratin to a dark tip
            return p["k3"] if t.rel[1] > 0.67 else (p["horn2"] if t.rel[1] > 0.34 else p["horn1"])
        if mat == "bump":       # rugose keratin; the male's flushed rust-red
            if p["male"]:
                return p["flush"] if f == "up" and (i + j) % 3 else (p["k1"] if f != "up" else p["k2"])
            return p["k4"] if f == "up" else p["k3"]
        if mat == "teeth":
            if f not in ("east", "west"): return None
            col = int(math.floor(t.L[2]))
            return p["tooth"] if col in (-12 + HZ[0], -10 + HZ[0]) else None
        if mat == "mouth": return p["gum"] if f in ("up", "down") else p["mouth"]
        if mat == "tongue": return p["tongue"] if f == "up" else p["mouth"]
        if mat == "gular": return p["b2"] if f == "down" else p["b1"]
        if mat == "frill": return frill_px(t, p)
        if mat == "claw":
            if f == "up": return p["beak2"]
            return p["beak3"] if t.j == t.h - 1 or f == "north" else p["beak1"]
        if n in BODY_PARTS or mat in ("sail", "belly"): return body_px(t, p)
        return head_px(t, p)
    return sh


HZ = [0]      # the jaw-joint z of the current build (the peg teeth columns are measured from it)


FRILL_RECTS = [(4, -3, 3), (7, 3, 7), (9, 7, 12), (7, 12, 15), (4, 15, 16)]   # (half width, y0, y1) of the plate


def _in_frill(x, y):
    if y < 7: return abs(x) < 9.5              # below the widest part the plate runs into the flanges: no rim there
    return any(abs(x) < hw and y0 <= y < y1 for hw, y0, y1 in FRILL_RECTS)


def _frill_edge(x, y):
    """distance band to the outline of the whole plate: 1 = the outermost texel ring, 2 = the next, 9 = inside"""
    for r in (1, 2):
        if any(not _in_frill(x + dx * r, y + dy * r) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): return r
    return 9


def frill_px(t, p):
    """the display face (north, facing up-forward) and the flanges: tawny, a bone-white rim round the WHOLE outline
    (not round each step), a few faint radial grooves, the windows one tone darker; the male's rim band flushes
    rust-red. Back and underside: the plain body skin."""
    c = t.cube; f = t.face; n = c["name"]
    L = t.L
    yb = L[1] - (c["fref"]["from"][1] + 3)
    x = L[0]
    if f in ("south", "down"):
        s = skin.scales(*skin.face_uv_coords(t), cell=5.0, seed=7)
        return p["k2"] if s == "edge" else p["k3"]
    if n.startswith("squam"):
        if f in ("east", "west"):     # the outer face of the side flange: the frill surface curving down
            if t.rel[2] > 0.84 or (n == "squam_mid" and t.rel[1] > 0.8): return p["rim"]
            u, v = skin.face_uv_coords(t)
            sc = skin.scales(u, v, cell=5.5, seed=17)
            base = "f2" if t.rel[1] > 0.3 else "f1"
            return p["f1" if base == "f2" else "f0"] if sc == "edge" else p[base]
        return p["f1"]
    if f in ("east", "west", "up"):   # the thickness of the plate at its edge
        return p["rim"] if n in ("frill_mid", "frill_top", "frill_crown") and f == "up" else p["f1"]
    # north: the display face
    e = _frill_edge(math.floor(x) + 0.5, math.floor(yb) + 0.5)
    if e == 1: return p["rim"]
    if e == 2 and p["male"]: return p["flush"]
    a = math.atan2(x, yb + 4.0)
    g = (a * 3.2 + 0.08 * math.sin(yb * 0.5)) % 1.0
    # the windows are NOT drawn as dark ovals (two closed dark shapes read as eyes): the bone bars between and
    # round them are one tone lighter instead: the midline bar of the parietal and the band along the rim
    if abs(x) < 1.0 and yb > 2: return p["f3"]
    sc = skin.scales(*skin.face_uv_coords(t), cell=7.0, seed=13)
    return p["f1"] if sc == "edge" else p["f2"]


FR_Y = [0]


def head_px(t, p):
    """head skin: drawn scales, darker on top and lighter down the sides, a cream lower jaw; one light from above"""
    c = t.cube; f = t.face; n = c["name"]
    u, v = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    s = skin.scales(u, v, cell=4.6, seed=seed)
    if n in ("dentary", "jaw_back"):
        if f == "up": return p["gum"]
        if f in ("east", "west", "north"):
            base = "b1" if t.rel[1] < 0.45 else "k4"            # the lip line is drawn once, on the upper jaw
            return p["b0"] if s == "edge" and base == "b1" else (p["k3"] if s == "edge" else p[base])
        return p["b1"]
    if f == "down": return p["b1"]
    if f == "up":
        return p["k2"] if s == "edge" else p["k3"]
    if f in ("east", "west", "north", "south"):
        k = 4 if t.rel[1] < 0.55 else 3
        if n in ("palpebral", "occiput"): k = 3
        if n == "jugal": k = 4 if t.rel[1] > 0.3 else 3
        if t.j == t.h - 1 and n in ("cranium", "face", "snout") and f != "south": return p["k1"]   # the lip line
        return _ramp(p, k - 1) if s == "edge" else _ramp(p, k)
    return p["k3"]


def _col(u, w, i):
    """texture column of face-local column i; a face packed as a mirror of its twin (negative width) runs backwards,
    so a decal drawn on it lands on the twin's pixels (drawing at u + i spilled onto the next cube: the eye showed on
    the thighs)"""
    return u + i if w > 0 else u - 1 - i


def decals_for(sex):
    p = pal_for(sex)

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        cr = C["cranium"]
        for f in ("east", "west"):
            u, v, w, h = cr["uv"][f]
            # the eye: centred 3 px behind the face, 3 px under the top (col 0 = back on east, front on west)
            rows = eye_rows(EYE_STYLE[0])
            cmap = {"s": p["k1"], "Y": p["eyeY"], "E": p["eyeE"], "e": p["eyee"], "p": p["pupil"], "g": p["glint"],
                    "D": p["eyeD"], "L": p["lid"], "d": p["k0"]}
            for j, row in enumerate(rows):
                for k, ch in enumerate(row):
                    if ch == ".": continue
                    col = cmap[ch]
                    i = (abs(w) - 2 - k) if f == "east" else (1 + k)     # art column 0 = the front; 1 px behind the edge
                    img[v + 1 + j, _col(u, w, i)] = (*col, 255)
        sn = C["snout"]
        for f in ("east", "west"):     # the nostril: high on the snout, under the bump
            u, v, w, h = sn["uv"][f]
            i0 = 1 if f == "east" else abs(w) - 2
            img[v + 2, _col(u, w, i0)] = (*p["k1"], 255)                # a slit, not a dark dot (a dot reads as an eye)
            img[v + 2, _col(u, w, i0 + (1 if f == "east" else -1))] = (*p["k1"], 255)
    return dec


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))


# ------------------------------------------------------------------ the body (step 2)
# Model px at 48 px/m, the hip joint at z = 0, the ground at y = 0, the beak toward -z.
# From the study: the back rises to the hips (0.67 m) and the tail sail (0.72 m); the head is carried low (mouth
# line 0.31 m); short front legs with the elbows a little out; long hind legs with the shin longer than the thigh;
# a deep, flat-sided tail with a sail of tall spines over its first half.
REST = {"neck": -12, "skull": 6, "tail1": 2, "tail2": 5, "tail3": 6, "tail4": 5,
        "thigh": 14, "shin": -23, "foot": 9, "arm": -6, "forearm": 10}


SHIN_EXT = 2


def hind_legs(m, body):
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    E = SHIN_EXT          # the bent knee lifted the foot 2.3 px off the ground at rest: a longer shin and a straighter knee
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (8 * sx, 27, 0), (REST["thigh"], 0, 0))
        sh = m.bone(f"shin_{side}", th, (8.5 * sx, 15, -3), (REST["shin"], 0, 0))
        ft = m.bone(f"foot_{side}", sh, (8.5 * sx, 4 - E, 1), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (8.5 * sx, 1 - E, -2))
    m.pair("thigh_l", "thigh_r", (5, 13, -6), (11, 30, 4), name="thigh")           # the drumstick, into the hip
    m.pair("shin_l", "shin_r", (6.5, 3 - E, -5), (10.5, 16, 0), name="shin")
    m.pair("foot_l", "foot_r", (7, -E, -2), (11, 5 - E, 2), name="meta")
    m.pair("toes_l", "toes_r", (6, -E, -6), (11, 2 - E, -1), name="pes")
    # the four flat shovel claws: broad, short, grey horn (the digger's foot)
    m.pair("toes_l", "toes_r", (6, -E, -8), (8, 1 - E, -6), name="claw_in", mat="claw", faces=out("south"))
    m.pair("toes_l", "toes_r", (9, -E, -8), (11, 1 - E, -6), name="claw_out", mat="claw", faces=out("south"))


def fore_legs(m, body):
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (7 * sx, 21, -24), (REST["arm"], 0, -6 * sx))
        fa = m.bone(f"forearm_{side}", a, (8.5 * sx, 12, -24), (REST["forearm"], 0, 6 * sx))
        m.bone(f"hand_{side}", fa, (8.5 * sx, 2, -24))
    m.pair("arm_l", "arm_r", (5, 11, -28), (10, 24, -20), name="arm")
    m.pair("forearm_l", "forearm_r", (6.5, 2, -27), (10.5, 13, -22), name="forearm")
    m.pair("hand_l", "hand_r", (6, 0, -27), (11, 2, -22), name="hand")
    m.pair("hand_l", "hand_r", (6, 0, -28), (8, 1, -27), name="fclaw_in", mat="claw", faces=out("south"))
    m.pair("hand_l", "hand_r", (9, 0, -28), (11, 1, -27), name="fclaw_out", mat="claw", faces=out("south"))


def tail(m, body):
    """deep and flat-sided: a core that tapers, and over its first half the sail of tall neural spines (thin)"""
    segs = [  # name, z0, z1, half width, y0, y1 (the core)
        ("tail1", 6, 17, 5, 18, 31), ("tail2", 15, 26, 3, 19, 29), ("tail3", 24, 35, 2, 19, 26), ("tail4", 33, 45, 1, 18, 22)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 1 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-1, 31, 6), (1, 36, 16), name="sail1", mat="sail")
    m.cube("tail2", (-1, 29, 16), (1, 34, 25), name="sail2", mat="sail")
    m.cube("tail3", (-1, 26, 25), (1, 29, 33), name="sail3", mat="sail")


def build(sex="male"):
    m = P.Model("protoceratops")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 26, 0))
    # the trunk: the chest low and narrow between the front legs, the back rising to the hips
    m.cube(body, (-6, 12, -30), (6, 27, -15), name="chest")
    m.cube(body, (-8, 13, -18), (8, 30, -2), name="torso", rot=(-7, 0, 0), origin=(0, 21, -10))   # the back rising to the hips
    m.cube(body, (-7, 16, -5), (7, 33, 8), name="hips")
    m.cube(body, (-5, 11, -24), (5, 13, -6), name="belly", mat="belly")
    n = m.bone("neck", body, (0, 22, -28), (REST["neck"], 0, 0))
    m.cube(n, (-5, 13, -38), (5, 26, -27), name="neck")
    hd = m.bone("head", n, (0, 22, -37))
    head(m, hd, 15, -37, sex, rest=(REST["skull"], 0, 0))
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the body skin
# House skin (drawn scales, the tone chosen per whole scale, a seam on the shaded side, belly scutes), with the
# Protoceratops marks from the study: rust saddle blotches across the back that wander with the body (disruptive
# in dry scrub), a wandering countershade border, a few big pale tubercles on the upper flank (ceratopsian skin),
# the sail plain with its spines drawn at uneven spacing.
TRUNK = {"chest", "torso", "hips", "neck", "tail1", "tail2", "tail3", "tail4", "thigh", "arm", "neck_stub"}
UNDERSIDE = {"belly"}
LEG = {"shin", "meta", "pes", "forearm", "hand"}
BODY_PARTS = TRUNK | UNDERSIDE | LEG | {"sail1", "sail2", "sail3"}
STEP_DN = {"r2": "r1", "r1": "r0", "r0": "k0", "k5": "k4", "k4": "k3", "k3": "k2", "k2": "k1", "k1": "k0", "k0": "k0", "b3": "b2", "b2": "b1", "b1": "b0", "b0": "b0"}
UNDER = {"chest": 0.42, "torso": 0.30, "hips": 0.22, "neck": 0.45, "tail1": 0.18, "tail2": 0.2, "tail3": 0.22, "tail4": 0.25}
BCELL = 4.4
SPINES = [0, 3, 5, 8, 12, 14, 17, 21, 24, 26, 30, 33]     # the sail's spines: uneven, as on the fossil


def _blot(z, y):
    """the rust saddles: a low-frequency field along the body, > 0 inside a blotch"""
    return (math.sin(z * 0.20 + 0.9) * 0.9 + math.sin(z * 0.47 + y * 0.35 + 1.7) * 0.45
            + math.sin(y * 0.42 - z * 0.13) * 0.3 - 0.45)


# skin "b" (02/11, the anti-AI pass): the first skin read as one even crackle of big cells over a single tan, a
# procedural look. Now it is built like the approved T. rex: a dark back fading to lighter flanks over the cream belly,
# finer scales that catch the light on their upper side, and the rust saddles drawn as deliberate bars across the
# back that taper down the flanks and lean back, not a noise field. No lone pale dots.
SKIN_STYLE = ["b"]
STEP_UP = {"k0": "k1", "k1": "k2", "k2": "k3", "k3": "k4", "k4": "k5", "k5": "k5", "r0": "r1", "r1": "r2", "r2": "r2"}
# the saddles: (centre z, half width) along the body, nape to mid-tail; the hip one is the widest
BARS = [(-31.0, 2.6), (-19.0, 3.2), (-7.5, 3.0), (5.0, 3.8), (17.5, 3.0), (28.0, 2.4), (37.0, 2.0)]
CELL_B = 3.2


def _bar(cz, vc):
    """1 inside a rust bar: full across the back, narrowing down the flank, leaning back as it goes down"""
    for zc, hw in BARS:
        zz = cz - zc - (1 - vc) * 2.5
        reach = hw * (0.35 + 0.65 * min(1.0, max(0.0, (vc - 0.42) / 0.45)))
        if abs(zz) <= reach and vc > 0.42:
            return 1
    return 0


def body_px_b(t, p, n, f, side, vc, cz, u_, w_, seed):
    if f == "up":
        base = "k2"
    elif n in ("thigh", "arm"):
        base = "k4" if t.rel[1] < 0.55 else "k3"
    else:
        base = "k2" if vc > 0.86 else "k3" if vc > 0.66 else "k4"
    if n != "arm" and _bar(cz, 1.0 if f == "up" else vc):
        base = "r0" if base == "k2" else "r1"
    sc = skin.scales(u_, w_, cell=CELL_B, seed=seed)
    if sc == "edge": return p[STEP_DN[base]]
    if sc == "hi" and (f == "up" or vc > 0.3): return p[STEP_UP[base]]
    return p[base]


def body_px(t, p):
    c = t.cube; n = c["name"]; f = t.face
    u_, w_ = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    belly = lambda uu, ww, width=6: p[{"seam": "b0", "hi": "b3", "base": "b2"}[skin.scutes(uu, ww, row=3, width=width)]]
    if n.startswith("sail"):
        if f == "up": return p["k2"]
        if f in ("east", "west"):
            z = int(math.floor(t.L[2])); k = z - int(c["fref_z"]) if "fref_z" in c else z
            top = t.j <= 0
            if top: return p["k1"]
            spine = (z % 36) in SPINES
            return p["k2"] if spine else p["k3"]
        return p["k2"]
    if n in UNDERSIDE or (f == "down" and n not in LEG and n not in ("thigh", "arm")):
        if f == "up": return p["k3"]
        if f == "down": return belly(t.L[0], t.L[2], 7 if n.startswith("tail") else 5)
        return belly(u_, w_)
    if n in LEG:
        base = "k4" if f in ("north", "east", "west") else "k3"
        if n in ("shin", "meta", "forearm") and f == "north":       # scutes across the front of the shin
            if math.floor(t.L[1]) % 3 == 0: return p[STEP_DN[base]]
            return p[base]
        if n in ("pes", "hand") and f == "up":
            return p["k3"] if (t.i % 3) else p["k2"]                # the toes
        return p[STEP_DN[base]] if skin.scales(u_, w_, cell=3.4, seed=seed) == "edge" else p[base]
    # trunk, neck, tail, thigh, arm: tone per whole scale, from the height of its centre and the blotch field
    d1, d2, cc = skin.voronoi(math.floor(u_) + 0.5, math.floor(w_) + 0.5, BCELL, seed)
    side = f in ("east", "west")
    if side:
        vc = (cc[3] - c["from"][1]) / max(1, t.h)
        line = UNDER.get(n, 0.3) + 0.07 * math.sin(cc[2] * 0.13 + 0.7) + 0.04 * math.sin(cc[2] * 0.37 + 2.1)
        if n in UNDER and vc < line:
            return belly(u_, w_)
        cz, cy = cc[2], cc[3]
    elif f == "up":
        vc = 1.0; cz, cy = cc[3], c["to"][1]
    else:
        vc = t.rel[1]; cz, cy = c["from"][2], c["from"][1] + t.rel[1] * t.h
    if SKIN_STYLE[0] == "b":
        return body_px_b(t, p, n, f, side, vc, cz, u_, w_, seed)
    if f == "up":
        base = "k3"
    elif n in ("thigh", "arm"):
        base = "k4" if t.rel[1] > 0.35 else "k3"
    else:
        base = "k4" if vc < 0.82 else "k3"
    if n not in ("arm",) and _blot(cz, cy) > 0 and (f == "up" or vc > 0.45):
        base = "r1" if base == "k4" else "r0"         # the rust saddles: a hue, not just a darker sand
    elif side and 0.5 < vc < 0.85 and h32(cc[0], cc[1], seed, 5) % 11 == 0 and n in ("torso", "hips", "chest"):
        base = "k5"
    sc = skin.scales(u_, w_, cell=BCELL, seed=seed)
    return p[STEP_DN[base]] if sc == "edge" else p[base]
