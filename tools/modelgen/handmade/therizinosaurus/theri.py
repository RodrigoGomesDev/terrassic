"""Therizinosaurus cheloniformis, made by hand from its own study (page "Terizinossauro: estudo e modelo", approved by
Rodrigo on 06/11/2026). Real size 10 m along the spine, the head ~5.4 m up, 5 to 6.6 t (Zanno & Makovicky 2013).

Drawn at 24 px = 1 m (game scale 0.667, like the Giganotosaurus): the head of a 10 m Therizinosaurus is only ~0.55 m
long, 13 px here, and each hand claw (~52 cm) is 12 px.

What makes it itself (each point from the study):
- a pot-bellied biped with the trunk tilted up from the hips, a long neck (~2.4 m) and a SMALL head with a horny
  beak in front; a short tail;
- the arms: 2.4 m, thick, each hand with THREE straight blade claws, flat from the sides and curved only at the tip
  (the longest claws of any land animal); a fan of barred quills on the forearm of the adults (adult_l / adult_r,
  hidden on the young, who were downy);
- broad short feet with FOUR toes on the ground (the first toe weight-bearing, as in no other theropod of the mod);
- a wide pelvis it could sit on.

The colour (the first species after Rodrigo asked for bolder skins, 05/11/2026): golden ochre with broken black bars
over the back and the neck, a cream belly, black-and-white barred quills; the male's bare throat red. The female the
same ochre duller, brown bars, no red.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 24
TILT = 16          # the trunk rises from the hips

# the colour variants under study (06/11: Rodrigo did not like the ochre with black bars, "falta ser mais único").
# Each: body ramp o0..o5, the pattern marks b0..b2 and their kind, the belly w0..w3, the ruff and plumes m0..m2,
# the quills q0..q2 (barred), the throat r0..r2 (the female's in "rf"), claws, beak, bare feet.
COMMON = {
    "s0": "4a3c28", "s1": "675640", "s2": "84714f", "s3": "a08d66",
    "c0": "9c8f76", "c1": "cfc3a6", "c2": "e9e0c8", "k0": "1e1a14", "k1": "35302a", "k2": "5a5246",
}
VARIANTS = {
    # earth (the one in use, 06/11: "algo mais neutro"): an olive-khaki coat with soft darker mottles on the back,
    # a pale belly, the ruff and cape a shade darker than the coat, dark quills barred with cream; the male's bare throat a
    # muted brick red
    "terra": dict(pattern="mottle", male={
        "o0": "3f3f2f", "o1": "4d4d3a", "o2": "5c5c44", "o3": "6d6d52", "o4": "7f7f5f", "o5": "91916c",
        "b0": "3a3a28", "b1": "4a4a34", "b2": "565642",
        "w0": "a4977e", "w1": "bcae94", "w2": "d0c3a8", "w3": "e0d5bc",
        "m0": "33331f", "m1": "4a4a32", "m2": "5e5e42",
        "q0": "2a1e14", "q1": "e8dcc2", "q2": "c2b496", "r0": "6a2a22", "r1": "88382c", "r2": "a24838"},
        female={"m0": "3a3826", "m1": "504e38", "m2": "64624a", "r0": "625f4c", "r1": "74705a", "r2": "858067",
                "q0": "3e3122", "q1": "d0c3a8", "q2": "ae9f84"}),
    # ember: a dark wine-brown body with faint pale speckles, a blazing rust ruff and cape, black-and-white quills
    "brasa": dict(pattern="speckle", male={
        "o0": "221012", "o1": "33181b", "o2": "452024", "o3": "5a2930", "o4": "6e333b", "o5": "833d46",
        "b0": "8a7660", "b1": "a08b72", "b2": "b8a286",
        "w0": "8c7c66", "w1": "a8977e", "w2": "c2b196", "w3": "d6c6aa",
        "m0": "7a2a0e", "m1": "b04416", "m2": "d8661e",
        "q0": "141010", "q1": "f2ead6", "q2": "c9bfa8", "r0": "6e1218", "r1": "9a1e26", "r2": "c0303a"},
        female={"m0": "5e3a1c", "m1": "7e5226", "m2": "9a6a34", "r0": "452024", "r1": "5a2930", "r2": "6e333b",
                "q0": "2a211b", "q1": "c2b196", "q2": "a8977e"}),
    # slate: an indigo-slate body, a white ruff and cape, a black mask through the eye, black-and-white quills
    "ardosia": dict(pattern="mask", male={
        "o0": "2d3754", "o1": "364265", "o2": "3f4d76", "o3": "49598a", "o4": "54669d", "o5": "6476ac",
        "b0": "0e1216", "b1": "161c22", "b2": "222a32",
        "w0": "b8b4aa", "w1": "d2cec4", "w2": "e6e2d8", "w3": "f4f1ea",
        "m0": "c8c2b6", "m1": "e2ddd2", "m2": "f6f3ec",
        "q0": "10141a", "q1": "f2efe8", "q2": "c8c4ba", "r0": "6e1218", "r1": "9a1e26", "r2": "c0303a"},
        female={"m0": "8e98a4", "m1": "a8b2bc", "m2": "c2cad2", "r0": "3f4d76", "r1": "49598a", "r2": "54669d",
                "q0": "2c3846", "q1": "d2cec4", "q2": "a8a49a"}),
    # sand with rosettes: a pale sand body broken by big dark rosettes, a black ruff, cream-and-brown quills
    "rosetas": dict(pattern="rosette", male={
        "o0": "7a6440", "o1": "9a8052", "o2": "b49a66", "o3": "c8b07a", "o4": "d8c290", "o5": "e6d4a6",
        "b0": "2a1a0e", "b1": "3e2814", "b2": "5a3c1e",
        "w0": "c8bca0", "w1": "ddd2b8", "w2": "ece4ce", "w3": "f6f0e0",
        "m0": "100c08", "m1": "1e1610", "m2": "30241a",
        "q0": "3e2814", "q1": "f0e6cc", "q2": "c8b890", "r0": "6e1218", "r1": "9a1e26", "r2": "c0303a"},
        female={"m0": "3e2814", "m1": "5a3c1e", "m2": "7a5430", "r0": "b49a66", "r1": "c8b07a", "r2": "d8c290",
                "q0": "5a3c1e", "q1": "e6dcc2", "q2": "c2b28a"}),
}
VARIANT = "terra"
EYE = {"lid": "1a120a", "iris": "c47a1a", "iris2": "8a4e10", "pupil": "0a0806", "glint": "fbf3df", "ring": "3a2a14"}


def pal_for(sex, variant=None):
    v = VARIANTS[variant or VARIANT]
    src = dict(COMMON); src.update(v["male"])
    if sex != "male":
        src.update(v["female"])
    p = {k: hx(x) for k, x in src.items()}
    p.update({k: hx(x) for k, x in EYE.items()})
    return p


def pattern_of(variant=None):
    return VARIANTS[variant or VARIANT]["pattern"]


REST = {
    "neck1": 40, "neck2": -4, "neck3": -12, "skull": -24,
    "thigh": 18, "shin": -38, "foot": 22, "toes": -2,
    "arm": -6, "forearm": 58, "hand": 34,
    "tail1": -8, "tail2": 2, "tail3": 3, "tail4": 3,
}
HIP = (0, 66, 0)


def _ground(m):
    import geo
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes}) if c["mat"] not in ("plume",))
    m.shift(-lo)


def head(m, parent):
    """small but not a box: a rounded braincase with the eye high, a short snout, the horny beak in front; the lower
    jaw closes inside it; a tuft of plumes on the crown"""
    sk = m.bone("skull", parent, (0, 96, -112), (REST["skull"], 0, 0))
    m.cube(sk, (-4.5, 91, -121), (4.5, 100, -111), name="cranium")
    m.cube(sk, (-3.5, 100, -120), (3.5, 102, -112), name="crown")
    m.cube(sk, (-3.5, 92, -127), (3.5, 98, -121), name="snout")
    m.cube(sk, (-2.5, 92, -130), (2.5, 97, -127), name="beak", mat="beak")
    m.cube(sk, (0, 102, -120), (0, 108, -110), name="tuft", mat="plume")
    jaw = m.bone("jaw", sk, (0, 92, -114))
    m.cube(jaw, (-3.5, 89, -120), (3.5, 92, -112), name="jaw_back")
    m.cube(jaw, (-2.5, 89, -127), (2.5, 91, -120), name="jaw_front")
    m.cube(jaw, (-1.5, 89, -129), (1.5, 91, -127), name="beak_lo", mat="beak")
    return sk


def neck(m, body):
    """thick at the shoulders, thinning to the head; a sparse filament mane along the top and the ruff of long
    feathers hanging round its base"""
    n1 = m.bone("neck1", body, (0, 96, -56), (REST["neck1"], 0, 0))
    m.cube(n1, (-9, 86, -78), (9, 104, -54), name="neck1")
    m.cube(n1, (0, 104, -76), (0, 108, -56), name="mane1", mat="plume")
    m.pair(n1, n1, (9.5, 86, -78), (9.5, 100, -54), name="ruff", mat="plume")
    m.cube(n1, (-9, 84, -79), (9, 98, -79), name="ruff_front", mat="plume")
    n2 = m.bone("neck2", n1, (0, 96, -76), (REST["neck2"], 0, 0))
    m.cube(n2, (-7, 89, -97), (7, 103, -74), name="neck2")
    m.cube(n2, (0, 103, -95), (0, 106, -77), name="mane2", mat="plume")
    n3 = m.bone("neck3", n2, (0, 96, -95), (REST["neck3"], 0, 0))
    m.cube(n3, (-5.5, 90, -114), (5.5, 101, -93), name="neck3")
    hd = m.bone("head", n3, (0, 96, -112))
    head(m, hd)


def arms(m, body):
    """2.4 m: a thick upper arm, the forearm, a hand of three fingers each with its straight blade claw (flat from the
    sides, curved only at the tip), and the fan of barred quills trailing behind the forearm"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (17 * sx, 88, -50), (REST["arm"], 0, 0))
        fa = m.bone(f"forearm_{side}", a, (17 * sx, 68, -50), (REST["forearm"], 0, 0))
        m.bone(f"hand_{side}", fa, (17 * sx, 53, -50), (REST["hand"], 0, 0))
        m.bone(f"adult_{side}", fa, (17 * sx, 68, -50))
    m.pair("arm_l", "arm_r", (14, 66, -54), (20, 90, -46), name="arm")
    m.pair("forearm_l", "forearm_r", (15, 52, -53), (19, 69, -47), name="forearm")
    m.pair("hand_l", "hand_r", (14.5, 46, -53), (19.5, 53, -47), name="hand")
    for k, x in enumerate((14.5, 16.5, 18.5)):
        ln = (9, 10, 9)[k]
        m.pair("hand_l", "hand_r", (x, 46 - ln, -52), (x + 1, 46, -49), name=f"claw{k}", mat="claw")
        m.pair("hand_l", "hand_r", (x, 46 - ln - 4, -50.5), (x + 1, 46 - ln, -48.5), name=f"tip{k}", mat="claw")
    m.pair("adult_l", "adult_r", (17, 44, -47), (17, 72, -26), name="fan", mat="plume")


def legs(m, body):
    """the heavy leg: a big drumstick showing under the belly, a stout shin, a SHORT metatarsus and a broad foot with
    four toes on the ground"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (13 * sx, 66, 2), (REST["thigh"], 0, 0))
        sh = m.bone(f"shin_{side}", th, (13 * sx, 42, 2), (REST["shin"], 0, 0))
        ft = m.bone(f"foot_{side}", sh, (13 * sx, 18, 2), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (13 * sx, 7, 0), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (6, 38, -10), (20, 74, 12), name="thigh")
    # the feathered "trousers": long body feathers hanging from the drumstick over the knee, outside and in front
    m.pair("thigh_l", "thigh_r", (20.5, 30, -10), (20.5, 50, 12), name="breeches", mat="plume")
    m.pair("thigh_l", "thigh_r", (6, 30, -10.5), (20, 46, -10.5), name="breeches_front", mat="plume")
    m.pair("shin_l", "shin_r", (8.5, 16, -3), (17.5, 44, 7), name="shin")
    m.pair("foot_l", "foot_r", (9.5, 6, -2), (16.5, 19, 5), name="meta")
    m.pair("toes_l", "toes_r", (9, 5, -4), (17, 8, 3), name="pad")
    for k, (x0, ln) in enumerate(((8.5, 4), (11, 7), (13.5, 7), (16, 6))):
        m.pair("toes_l", "toes_r", (x0, 4, -4 - ln), (x0 + 2, 7, -3), name=f"toe{k}")
        m.pair("toes_l", "toes_r", (x0 + 0.5, 4, -6 - ln), (x0 + 1.5, 6, -4 - ln), name=f"tclaw{k}", mat="claw")


def tail(m, body):
    """short and thick at the root, carried a little down"""
    segs = [("tail1", 12, 36, 11, 58, 78), ("tail2", 34, 58, 8, 61, 75), ("tail3", 56, 80, 5, 64, 72), ("tail4", 78, 98, 3, 66, 70)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    # the fan of plumes at the end of the short tail
    m.cube(parent, (0, 63, 88), (0, 75, 104), name="tailfan", mat="plume")


SADDLE_MATS = ("felt", "hide", "strap", "bone")


def saddle(m, body):
    """Its own saddle on the sloping back, behind the shoulders: a broad hide pad on a felt blanket, a high cantle
    behind (the back slopes, the rider would slide down it), knee rolls and a bone grab bar in front, a girth behind
    the arms and a breast strap round the chest"""
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    sd = m.bone("saddle", body, HIP, (TILT, 0, 0))
    m.cube(sd, (-12, 79, -36), (12, 80, -8), name="blanket", mat="felt", faces=out("down"))
    m.cube(sd, (-9, 80, -33), (9, 82, -11), name="pad", mat="hide", faces=out("down"))
    m.cube(sd, (-8, 82, -12), (8, 87, -9), name="cantle", mat="hide")
    m.pair(sd, sd, (7, 82, -33), (10, 85, -27), name="knee_roll", mat="hide")
    m.pair(sd, sd, (3, 82, -35), (4, 87, -34), name="grip_post", mat="bone")
    m.cube(sd, (-4, 87, -35), (4, 88, -34), name="grip_bar", mat="bone")
    m.pair(sd, sd, (17.5, 40, -26), (18.5, 79, -23), name="girth", mat="strap", faces=out("west", "up"))
    m.cube(sd, (-17.5, 39, -26), (17.5, 40, -23), name="girth_under", mat="strap", faces=out("up"))


def build(saddle_on=True):
    m = P.Model("therizinosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, HIP)
    rot = (TILT, 0, 0)
    # the trunk in parts, as the other remakes: a deep pot belly slung low, a narrower back on top, the chest rising
    # in front at a steeper angle and narrowing into the neck, the hips behind
    m.cube(body, (-17, 44, -52), (17, 72, 0), name="belly", rot=rot, origin=HIP)
    m.cube(body, (-15, 40, -42), (15, 44, -10), name="sag", rot=rot, origin=HIP, mat="belly")
    m.cube(body, (-12, 72, -54), (12, 79, -6), name="back", rot=rot, origin=HIP)
    m.cube(body, (-13, 54, -66), (13, 78, -44), name="chest", rot=(24, 0, 0), origin=HIP)
    m.cube(body, (-12, 54, -8), (12, 78, 14), name="hips", rot=(6, 0, 0), origin=HIP)
    m.cube(body, (0, 79, -48), (0, 85, -10), name="crest", rot=rot, origin=HIP, mat="plume")
    m.pair(body, body, (17.5, 66, -60), (17.5, 78, -38), name="cape", rot=rot, origin=HIP, mat="plume")
    neck(m, body)
    arms(m, body); legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ painting
FILAMENT = {"back", "belly", "chest", "hips", "neck1", "neck2", "neck3", "tail1", "tail2", "tail3", "tail4", "thigh", "arm",
            "forearm", "cranium", "crown"}
BARE = {"shin", "meta", "pad", "toe0", "toe1", "toe2", "toe3", "hand", "snout", "jaw_front"}
UNDER = {"back": -1.0, "belly": 0.16, "chest": 0.24, "hips": 0.12, "neck1": 0.35, "neck2": 0.4, "neck3": 0.45, "tail1": 0.22,
         "tail2": 0.25, "tail3": 0.3, "tail4": 0.35, "thigh": 0.0}
DN = {"o5": "o4", "o4": "o3", "o3": "o2", "o2": "o1", "o1": "o0", "o0": "o0", "w3": "w2", "w2": "w1", "w1": "w0", "w0": "o2",
      "b2": "b1", "b1": "b0", "b0": "b0"}
UP = {"o0": "o1", "o1": "o2", "o2": "o3", "o3": "o4", "o4": "o5", "o5": "o5", "w0": "w1", "w1": "w2", "w2": "w3", "w3": "w3",
      "b0": "b1", "b1": "b2", "b2": "b2"}


def fil(u, v, base, p, seed=0):
    """the sparse filament coat: short 1 px strokes lying back and down, here and there, darker under, lit at the root"""
    c = math.floor(u); r = math.floor(v)
    k = h32(c // 2, r // 3, seed)
    if k % 7 == 0 and r % 3 == 0: return p[DN[base]]
    if k % 11 == 1 and r % 3 == 2: return p[UP[base]]
    return p[base]


def bar_at(n, f, t, seed):
    """the broken black bars across the back and the neck: each bar 2-3 px wide, leaning, of its own length, and now
    and then broken; None where there is no bar"""
    if n not in ("back", "belly", "chest", "hips", "neck1", "neck2", "neck3", "tail1", "tail2", "tail3", "tail4", "thigh"): return None
    if f in ("east", "west"): a = t.L[2]; down = 1 - t.rel[1]
    elif f == "up": a = t.L[2]; down = abs(t.rel[0] - 0.5) * 0.6
    elif f == "north": a = t.L[0] * 0.3 + 40; down = 1 - t.rel[1]
    else: return None
    step = 9 if n.startswith("neck") else 11
    col = math.floor((a + 3.0 * down) / step)
    off = (a + 3.0 * down) - col * step
    wid = 2 + h32(col, seed, 1) % 2
    reach = 0.42 + 0.28 * (h32(col, seed, 2) % 100) / 100
    if n == "thigh": reach *= 0.5
    if off < wid and down < reach:
        if h32(col, math.floor(down * 6), seed) % 9 == 0: return None      # a break in the bar
        return "b1" if off < 1 or down > reach - 0.08 else "b0"
    return None


def mark_at(n, f, t, seed, pattern):
    """the body marks of the variant: bars, pale speckles, a black mask on the head, or big rosettes"""
    if pattern == "bars":
        return bar_at(n, f, t, seed)
    if pattern == "mask":
        if n in ("cranium", "snout") and f in ("east", "west") and 0.3 < t.rel[1] < 0.75:
            return "b0"
        return None
    if f not in ("east", "west", "up", "north"): return None
    u = t.L[2] if f in ("east", "west", "up") else t.L[0] + 40
    v = t.L[1] if f != "up" else t.L[0] * 0.7
    if pattern == "mottle":
        # soft blotches on the upper half, as on a bird's back, and a few dark flecks
        if f in ("east", "west") and t.rel[1] < 0.5: return None
        cell = 6.0
        cx, cy = math.floor(u / cell), math.floor(v / cell)
        px_ = (cx + 0.5 + 0.4 * ((h32(cx, cy, seed) % 100) / 100 - 0.5)) * cell
        py_ = (cy + 0.5 + 0.4 * ((h32(cx, cy, seed, 2) % 100) / 100 - 0.5)) * cell
        if h32(cx, cy, seed, 5) % 4 == 0 and math.hypot(u - px_, (v - py_) * 1.3) < 1.6:
            return "b2"
        if h32(math.floor(u), math.floor(v), seed, 7) % 41 == 0: return "b0"
        return None
    if pattern == "speckle":
        k = h32(math.floor(u), math.floor(v), seed, 7)
        if k % 23 == 0: return "b1"
        if k % 37 == 1: return "b0"
        return None
    if pattern == "rosette":
        if n not in ("back", "belly", "chest", "hips", "neck1", "neck2", "neck3", "tail1", "tail2", "tail3", "thigh", "arm"): return None
        cell = 7.0
        cx, cy = math.floor(u / cell), math.floor(v / cell)
        px_ = (cx + 0.5 + 0.3 * ((h32(cx, cy, seed) % 100) / 100 - 0.5)) * cell
        py_ = (cy + 0.5 + 0.3 * ((h32(cx, cy, seed, 2) % 100) / 100 - 0.5)) * cell
        d = math.hypot(u - px_, (v - py_) * 1.2)
        if h32(cx, cy, seed, 5) % 5 == 0: return None
        if 1.6 < d < 2.8 and h32(math.floor(u), math.floor(v)) % 6: return "b0"      # the broken ring
        if d <= 1.6: return "b2"                                                      # the brownish heart
        return None
    return None


def _uv(t):
    if t.face in ("up", "down"): return t.L[2], t.L[0]
    return skin.face_uv_coords(t)


def body_px(t, p, sex):
    c = t.cube; n = c["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    u, v = _uv(t)
    seed = zlib.crc32(n.encode()) % 7
    rel = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    # the bare throat (red on the male): under the last two neck segments and up their sides a little
    throat = n in ("neck3", "neck2") and (f == "down" or (f in ("east", "west") and rel < (0.3 if n == "neck3" else 0.18)))
    if f == "down" and not throat or n == "sag":
        return fil(u, v, "w1", p, seed)
    if throat:
        return p["r1"] if (math.floor(u) + math.floor(v)) % 5 else p["r0"]
    if side and n in UNDER and f in ("east", "west", "north"):
        col = math.floor((t.L[2] if f != "north" else t.L[0] + 8) / 2)
        line = UNDER[n] + 0.05 * math.sin(col * 0.8 + seed) + (h32(col, seed) % 3) / max(1, t.h)
        if rel < line:
            return fil(u, v, "w2" if rel > line * 0.5 else "w1", p, seed)
    b = mark_at(n, f, t, seed, pattern_of())
    if b: return p[b]
    if f == "up":
        base = "o2"
    else:
        wob = 0.06 * math.sin(math.floor(t.L[2]) * 0.3 + seed)
        base = "o3" if rel < 0.55 + wob else ("o4" if rel < 0.85 + wob else "o3")
        if n in ("thigh",): base = "o3" if rel > 0.4 else "o2"
        if n in ("arm", "forearm"): base = "o3" if f != "north" else "o4"
        if n in ("cranium", "crown"): base = "o4"
    return fil(u, v, base, p, seed)


def bare_px(t, p, sex):
    """the bare feet and hands: big scutes across the top of the foot and toes, small round scales on the sides"""
    n = t.cube["name"]; f = t.face
    if n in ("snout", "jaw_front"):
        if f == "down": return p["w1"]
        return p["o4"] if f == "up" else p["o3"]
    if n == "shin" and f != "down" and t.rel[1] > 0.55:
        # the upper shin feathered in the body's colour, the feathers ending in a ragged line over the scales
        col = math.floor(t.L[2] if f in ("east", "west") else t.L[0])
        if t.rel[1] > 0.62 + 0.06 * (h32(col, 21) % 3):
            return fil(*_uv(t), "o3" if f != "north" else "o4", p)
        return p["m0"]
    base = "s2" if f in ("north", "up") else "s1"
    if f == "down": return p["s0"]
    if f in ("north", "up"):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 3
        if k == 0: return p[{"s2": "s1", "s1": "s0"}[base]]
        return p[base]
    sc = skin.scales(*skin.face_uv_coords(t), cell=2.4, seed=zlib.crc32(n.encode()) % 97)
    if sc == "edge": return p[{"s2": "s1", "s1": "s0"}[base]]
    if sc == "hi": return p["s3"]
    return p[base]


def plume_px(t, p, sex):
    n = t.cube["name"]
    if n == "fan":
        # the quill fan in the forearm's frame: y down the forearm, z back from it. Each quill 1 px, barred black and
        # white across (2 px bands), the longest at the middle of the forearm; the female's shorter and brown
        z = t.L[2] - t.cube["from"][2]; y = t.L[1] - t.cube["from"][1]
        H = t.cube["to"][1] - t.cube["from"][1]
        s = y / H
        reach = (9.5 + 3.5 * math.sin(math.pi * min(1, s * 1.1))) if sex == "male" else (7 + 2.5 * math.sin(math.pi * s))
        reach -= (0, 0.8, 0.3, 1.2, 0.5)[int(math.floor(y)) % 5]
        if z > reach: return None
        band = (math.floor(z) // 2) % 2
        return p["q0"] if band == 0 else (p["q1"] if int(math.floor(y)) % 2 == 0 else p["q2"])
    if n == "tailfan":
        # the tail fan: quills radiating back, barred like the arms'
        z = t.L[2] - t.cube["from"][2]; y = t.L[1] - t.cube["from"][1]
        H = t.cube["to"][1] - t.cube["from"][1]; D = t.cube["to"][2] - t.cube["from"][2]
        dy = abs(y - H / 2) / (H / 2)
        if z > D * (1 - 0.55 * dy * dy) - (0, 1, 0.5, 1.5)[int(math.floor(y)) % 4]: return None
        if z < 4: return None
        return p["m0"] if z > D * (1 - 0.55 * dy * dy) - 3 else (p["m1"] if int(math.floor(y)) % 3 else p["m2"])
    if n in ("ruff", "ruff_front", "cape", "breeches", "breeches_front"):
        # long feathers hanging: each 1 px strand its own length, lit at the root, darker at the tip
        col = int(math.floor(t.L[0] + 20 if n in ("ruff_front", "breeches_front") else t.L[2]))
        y = t.cube["to"][1] - t.L[1]                 # down from the top
        H = t.cube["to"][1] - t.cube["from"][1]
        ln = H * (0.7 + 0.3 * ((h32(col // 2, 11) % 100) / 100)) - (h32(col, 12) % 2)
        if y > ln: return None
        if y > ln - 2: return p["m0"]
        return p["m2"] if y < 2 and col % 3 == 0 else p["m1"]
    # the filament mane, the crest and the tuft: ragged strands standing up
    i = int(math.floor(t.L[2]))
    top = t.cube["to"][1] - t.cube["from"][1]
    y = t.L[1] - t.cube["from"][1]
    drop = (0.0, 1.0, 2.0, 0.5, 2.5, 1.5, 3.0, 1.0)[(i + h32(i // 2, 3) % 5) % 8]
    if n == "tuft": drop = (0.0, 1.5, 0.5, 3.0, 1.0, 2.0)[i % 6]
    if y > top - drop: return None
    return p["m1"] if (i + h32(i, 4) % 3) % 3 else p["m0"]


def saddle_px(t, p):
    mat = t.cube["mat"]; n = t.cube["name"]; f = t.face; i, j, w, h = t.i, t.j, t.w, t.h
    S = SADDLE_PAL
    if mat == "felt":
        if f == "up":
            edge = i in (0, w - 1) or j in (0, h - 1)
            return S["f2"] if edge else (S["f1"] if (i + 2 * j) % 5 else S["f0"])
        return S["f0"] if j == h - 1 else S["f3"]
    if mat == "bone":
        return S["b1"] if f == "up" else (S["b0"] if j == h - 1 and h > 1 else S["b2"])
    if mat == "strap":
        if n == "girth" and f in ("east", "west") and 4 <= j <= 5: return S["b1"] if j == 4 else S["b0"]
        return S["l1"] if f in ("down",) else S["l2"]
    if f == "up":
        if n == "pad" and (i in (0, w - 1) or j in (0, h - 1)): return S["l1"]
        if n == "pad" and (i in (1, w - 2)) and j % 2 == 0: return S["st"]
        return S["l3"]
    if f == "down": return S["l0"]
    return S["l2"] if j < h - 1 else S["l1"]


SADDLE_PAL = {
    "l0": hx("2c1a10"), "l1": hx("47291a"), "l2": hx("633a22"), "l3": hx("7e4c2c"), "st": hx("d8c08a"),
    "f0": hx("1d2a2e"), "f1": hx("2f4a50"), "f2": hx("c9a24a"), "f3": hx("263a40"),     # teal wool with an ochre rim
    "b0": hx("a8997a"), "b1": hx("e2d8bd"), "b2": hx("c6b998"),
}


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]
        if mat in SADDLE_MATS: return saddle_px(t, p)
        if mat == "plume": return plume_px(t, p, sex)
        if mat == "claw":
            # horn: ivory, darker toward the root, a dark line along the cutting edge underneath
            if t.face == "down": return p["c0"]
            rel = t.rel[1]
            return p["c2"] if rel < 0.4 else (p["c1"] if rel < 0.85 else p["c0"])
        if mat == "beak":
            if t.face == "up": return p["k1"]
            if t.face == "down": return p["k0"]
            return p["k2"] if t.j == t.h - 1 else p["k1"]
        if mat == "belly":
            return fil(*_uv(t), "w1" if t.face != "down" else "w0", p)
        n = t.cube["name"]
        if n in BARE: return bare_px(t, p, sex)
        if n == "jaw_back":
            if sex == "male" and t.face == "down": return p["r1"]
            return p["w1"] if t.face == "down" else p["o3"]
        return body_px(t, p, sex)
    return sh


FACE_ART = {
    ("cranium", "east"): [      # 10 wide x 9 tall (column 0 the front): the eye high and forward, a dark lid line over it,
        "4444444444",           # the amber iris round the pupil with a glint, a pale ring under it; the ear opening behind
        "44lllll444",
        "4lgpIIl444",
        "4lIppil444",
        "44lrrl4444",
        "4444444n44",
        "4444444444",
        "4444444444",
        "4444444444"],
    ("snout", "east"): [        # 6 x 6: the nostril up on the snout, the beak's edge running back along the bottom
        "444444",
        "4n4444",
        "444444",
        "444444",
        "444444",
        "kkkk44"],
}


def decals_for(sex):
    p = pal_for(sex)
    cmap = {"4": p["o4"], "3": p["o3"], "l": p["lid"], "i": p["iris"], "I": p["iris2"], "p": p["pupil"], "g": p["glint"],
            "r": p["w2"],
            "n": p["b0"], "k": p["k2"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        for (name, face), rows in FACE_ART.items():
            c = C.get(name)
            if not c or face not in c["uv"]: continue
            u, v, w, h = c["uv"][face]
            if w <= 0: continue
            assert (len(rows), len(rows[0])) == (h, w), (name, face, (w, h), (len(rows[0]), len(rows)))
            rows2 = [r.replace("4", ".") for r in rows]      # only the marks: the coat underneath stays
            P.stamp(img, m, c, face, rows2, cmap, at=(0, 0))
    return dec


def _clean(img, m):
    import qa
    qa.clean_orphans(img, m, cutout=("plume",), keep=())


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex), _clean))
