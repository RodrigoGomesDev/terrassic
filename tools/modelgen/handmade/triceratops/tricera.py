"""Triceratops horridus, made by hand from its own study (page "Triceratops: estudo antes de modelar", approved by
Rodrigo on 02/11/2026 02:40Z with the "ameixa" colours and 9 m; his note: legs and eye must not look odd).

Drawn at 24 px = 1 m (game scale 0.667), like the Carnotaurus and the Giganotosaurus: the skull with its frill is
2.4 m, so it gets about 58 px to carry the beak, the three horns, the cheek points, the eye and the frill rim.

The head (each point from the study):
- a narrow parrot beak of dark keratin (rostral above, predentary below), no teeth in sight (the dental batteries sit
  deep inside the cheeks);
- a short, thick nose horn over the nostril, leaning forward (T. horridus);
- two brow horns of about 1 m, ivory keratin darker at the root, rising from over the eye and sweeping FORWARD and a
  little out, the tips curving down a touch (the adult shape; the baby's curve back);
- the eye small for the skull, on the side, deep under the root of the brow horn (the house almond, dark honey iris);
- the cheek bones flaring out and down into keratin points (epijugals);
- the frill SOLID (no windows), a broad plate continuing the skull roof up and back, its sides curving down, the rim
  with low, flat, uneven bumps (the adult epoccipitals, almost fused): never a row of equal pins (teeth).
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 24
FRILL_TILT = 55          # degrees the frill plate leans back from the vertical of the skull

SCHEMES = {
    "ameixa": {   # plum-grey of a big animal (hippo, elephant in mud); shadows lean violet, lights to a warm rose-grey
        "k0": "2e2234", "k1": "3d2d42", "k2": "503e55", "k3": "66546a", "k4": "7d6a7c", "k5": "94808f",
        "b0": "a38f98", "b1": "b5a1a8", "b2": "c7b4b8", "b3": "d8c8c8",
        "fb0": "6a3a34", "fb1": "86493c", "fb2": "a45c46",              # the male's terracotta frill band
        "rim": "ddcfb6", "rim2": "bfae96",
        "female": {"k2": "56445b", "k3": "6d5b70", "k4": "846f82", "k5": "9b8795", "fb0": "5a3f48", "fb1": "6e4a52", "fb2": "84595e"},
    },
}
SCHEME = ["ameixa"]

PAL = {
    "beak0": hx("262022"), "beak1": hx("3f3534"), "beak2": hx("574b48"), "beak3": hx("7e7069"),
    "horn0": hx("4e4136"), "horn1": hx("7c6d5a"), "horn2": hx("a99a7f"), "horn3": hx("cfc3a8"), "horn4": hx("e6dcc6"),
    "eyeY": hx("d09a42"), "eyeE": hx("a8702c"), "eyee": hx("6e4620"), "pupil": hx("120d0b"), "glint": hx("efe6c8"),
    "eyeD": hx("1c1418"), "lid": hx("d9c39b"),
    "nost": hx("241a26"), "gum": hx("6b3a40"), "mouth": hx("33181e"), "tongue": hx("94505a"),
}


def pal_for(sex, scheme=None):
    sc = SCHEMES[scheme or SCHEME[0]]
    p = dict(PAL)
    for k, v in sc.items():
        if k != "female": p[k] = hx(v)
    if sex != "male":
        for k, v in sc["female"].items(): p[k] = hx(v)
    p["male"] = sex == "male"
    return p


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes}))
    m.shift(-lo)


OUT = lambda *d: [f for f in P.geo.FACES if f not in d]
# the brow horn: segments along its own +y, each a child bone bent a little forward (the adult curve)
HORN = [  # half width, length, bend of this segment (deg, about x; negative = further forward, the tip curving down)
    (2.5, 8, 0), (2, 7, -5), (1.5, 6, -6), (1, 4, -7)]
HORN_ROOT = (-42, 0, -12)      # the root's lean: forward, and out to the side


# the calf's brow horns (Horner & Goodwin 2006, the growth series): short stubs that curve BACK; they straighten and
# then turn forward only as the animal grows. Shown on babies only (bone "young_horns"; the adult's are "adult_horns")
YOUNG_HORN = [(2, 5, 0), (1.5, 4, 32), (1, 3, 36)]
YOUNG_ROOT = (-4, 0, -14)


def young_horns(m, sk, hy, hz):
    yh = m.bone("young_horns", sk, (0, hy + 16, hz - 11))
    for side, sx in (("l", 1), ("r", -1)):
        parent = m.bone(f"young_horn_{side}", yh, (5 * sx, hy + 16, hz - 11), (YOUNG_ROOT[0], 0, YOUNG_ROOT[2] * sx))
        y = hy + 16
        for k, (hw, ln, bend) in enumerate(YOUNG_HORN):
            b = parent if k == 0 else m.bone(f"young_horn_{side}{k}", parent, (5 * sx, y, hz - 11), (bend, 0, 0))
            m.cube(b, (5 * sx - hw, y - (1 if k else 2), hz - 11 - hw), (5 * sx + hw, y + ln, hz - 11 + hw),
                   name=f"yhorn{k}_{side}", mat="horn", faces=OUT("down") if k else None, hseg=k + 1)
            parent = b; y += ln


def brow_horns(m, sk, hy, hz):
    ah = m.bone("adult_horns", sk, (0, hy + 16, hz - 11))
    for side, sx in (("l", 1), ("r", -1)):
        parent = m.bone(f"brow_horn_{side}", ah, (5 * sx, hy + 16, hz - 11),
                        (HORN_ROOT[0], 0, HORN_ROOT[2] * sx))
        y = hy + 16
        for k, (hw, ln, bend) in enumerate(HORN):
            b = parent if k == 0 else m.bone(f"brow_horn_{side}{k}", parent, (5 * sx, y, hz - 11), (bend, 0, 0))
            m.cube(b, (5 * sx - hw, y - (1 if k else 2), hz - 11 - hw), (5 * sx + hw, y + ln, hz - 11 + hw),
                   name=f"horn{k}_{side}", mat="horn", faces=OUT("down") if k else None, hseg=k)
            parent = b; y += ln


def head(m, parent, hy, hz, sex="male", rest=(0, 0, 0)):
    """skull, horns, frill and jaw. (hy, hz): the mouth line at the jaw joint; returns the skull bone"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    HZ[0] = hz
    sk = m.bone("skull", parent, (0, hy + 6, hz), rest)
    # the skull, wide at the cheeks, narrowing to the beak; the top line falls from the horn roots to the nose.
    # Pieces overlap by 1 px instead of touching; faces buried in a neighbour are left out.
    m.cube(sk, *B(-8, -1, -15, 8, 17, 1), name="cranium")
    m.cube(sk, *B(-6, 0, -25, 6, 15, -14), name="face", faces=OUT("south"))
    m.cube(sk, *B(-4, 0, -33, 4, 12, -24), name="snout", faces=OUT("south"))
    m.cube(sk, *B(-2, 1, -37, 2, 8, -32), name="rostral", mat="beak", faces=OUT("south"))
    m.cube(sk, *B(-1.5, -3, -39, 1.5, 4, -35), name="hook", mat="beak", faces=OUT("south"))
    # the nose horn: short and thick, leaning forward over the nostril
    m.cube(sk, *B(-2, 11, -31, 2, 15, -26), name="nose_horn", mat="horn", faces=OUT("down"),
           rot=(-18, 0, 0), origin=(0, hy + 12, hz - 28.5), hseg=0)
    m.cube(sk, *B(-1, 15, -31, 1, 17, -28), name="nose_tip", mat="horn", faces=OUT("down"),
           rot=(-18, 0, 0), origin=(0, hy + 12, hz - 28.5), hseg=3)
    # the cheeks: the jugal flaring out under the eye, and its keratin point aimed out and down
    m.pair(sk, sk, *B(7, -3, -13, 11, 7, -3), name="jugal", faces=OUT("west"))
    m.pair(sk, sk, *B(10, -6, -8, 12, 0, -6), name="epijugal", mat="horn", faces=OUT("up"),
           rot=(0, 0, 38), origin=(11, hy, hz - 7), hseg=2)
    # the brow over the eye: the swollen root of the horn, a heavy upper lid
    m.pair(sk, sk, *B(7, 12, -13, 9, 15, -7), name="brow", faces=OUT("west"))
    brow_horns(m, sk, hy, hz)
    young_horns(m, sk, hy, hz)
    # the frill: its own bone at the back of the skull roof, leaning back. A solid plate in stepped widths, the
    # lower sides (the squamosals) curving down toward the neck, and a rim of low flat bumps
    fr = m.bone("frill", sk, (0, hy + 15, hz), (FRILL_TILT, 0, 0))
    F = lambda x0, y0, z0, x1, y1, z1: ((x0, hy + 15 + y0, hz + z0), (x1, hy + 15 + y1, hz + z1))
    base = m.cube(fr, *F(-8, -4, -1, 8, 4, 2), name="frill_base", mat="frill", faces=OUT("up"))
    for nm, hw, y0, y1 in FRILL_PLATE:
        m.cube(fr, *F(-hw, y0, -1, hw, y1, 1), name=nm, mat="frill")
    m.pair(fr, fr, *F(8, -8, -0.5, 13, 5, 1.5), name="squam_low", mat="frill")     # the sides run down behind the eye
    # the sides of the fan bend forward (a saddle-shaped plate): seen from the side the frill is a surface, not a stick
    m.pair(fr, fr, *F(12, -6, -10, 14, 15, -1), name="squam_a", mat="frill", faces=OUT("west", "south"))
    m.pair(fr, fr, *F(15, 15, -6, 17, 23, -1), name="squam_b", mat="frill", faces=OUT("west", "south"))
    # (the adult's low rim bumps are drawn in the rim's outline, not built: proud blocks read as battlements)
    for c in m.cubes:
        if c["mat"] == "frill": c["fref"] = base
    # the jaw: hinged at the back under the cheek, the dark predentary at the tip
    jaw = m.bone("jaw", sk, (0, hy + 1, hz - 2))
    m.cube(jaw, *B(-2.5, -5, -38, 2.5, 0, -31), name="predentary", mat="beak", faces=OUT("south", "up"))
    m.cube(jaw, *B(-4, -6, -32, 4, 0, -20), name="dentary", faces=OUT("south"))
    m.cube(jaw, *B(-6, -8, -21, 6, 0, -2), name="jaw_back")
    m.cube(jaw, *B(-5, -9, -16, 5, -7, -2), name="gular", mat="gular", faces=OUT("up"))
    m.cube(jaw, *B(-5, -1, -20, 5, 2, -4), name="cheek_in", mat="mouth")     # the mouth wall: no slit half-open
    m.cube(jaw, *B(-1, -2, -30, 1, 1, -6), name="tongue", mat="tongue")
    m.cube(sk, *B(-1.5, -1, -34, 1.5, 3, -15), name="palate", mat="mouth")
    return sk


# the plate, measured up from the skull roof (half width, y0, y1): a broad rounded fan, widest two thirds up
FRILL_PLATE = [("frill_low", 14, 4, 7), ("frill_mid", 16, 7, 11), ("frill_mid2", 17, 11, 15), ("frill_wide", 18, 15, 19),
               ("frill_top", 17, 19, 22), ("frill_top2", 15, 22, 24), ("frill_top3", 12, 24, 26), ("frill_crown", 8, 26, 27)]
# (the bent sides squam_a, squam_b follow the plate's outline: x 12-14 low, 15-17 high)
# low flat rim bumps along the top and upper sides: (name, x0, x1, y0, y1); widths 3-5, gaps 1-3, never even
RIM_BUMPS = []


def build_head_only(sex="male"):
    m = P.Model("triceratops")
    root = m.bone("root", None, (0, 0, 0))
    n = m.bone("neck", root, (0, 30, 10))
    m.cube(n, (-10, 14, 2), (10, 38, 22), name="neck_stub")
    hd = m.bone("head", n, (0, 28, 0))
    head(m, hd, 24, 4, sex, rest=(12, 0, 0))
    _ground(m)
    return m


# ------------------------------------------------------------------ paint
HZ = [0]


def _ramp(p, k):
    return p[f"k{max(0, min(5, k))}"]


# the house eye (T. rex, Protoceratops): an almond, the pupil toward the front, the glint over it, the shade low and
# behind; here under a heavy brow (the root of the horn) and with a dark honey iris
EYE = ["sdddds", "dYgYEd", "dYpEed", "dEpeed", ".dddd."]


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        c = t.cube; f = t.face; mat = c["mat"]; n = c["name"]
        i, j, w, h = t.i, t.j, t.w, t.h
        if mat == "beak":
            if f == "up": return p["beak2"]
            if f == "down": return p["beak0"]
            if n == "hook" and f in ("east", "west", "north"):
                return p["beak3"] if j >= h - 1 else p["beak1"]        # the worn pale cutting edge
            return p["beak2"] if j == 0 else p["beak1"]
        if mat == "horn": return horn_px(t, p)
        if mat == "mouth": return p["gum"] if f in ("up", "down") else p["mouth"]
        if mat == "tongue": return p["tongue"] if f == "up" else p["mouth"]
        if mat == "gular": return p["b2"] if f == "down" else p["b1"]
        if mat in SADDLE_MATS: return saddle_px(t)
        if mat == "frill": return frill_px(t, p)
        if n in BODY_PARTS or mat in ("hoof", "belly"): return body_px(t, p)
        return head_px(t, p)
    return sh


def horn_px(t, p):
    """keratin over bone: darker and ridged at the root, ivory toward the tip, lit on the upper side, worn smooth at
    the point; long grooves run along the horn (never rings: rings read as a screw)"""
    c = t.cube; f = t.face; k = c.get("hseg", 0)
    along = (k + t.rel[1]) / 4.0 if c["name"].startswith(("horn", "yhorn")) else t.rel[1]
    if c["name"] == "epijugal": return p["horn0"] if t.rel[1] > 0.5 else p["horn1"]
    tone = 1 if along < 0.18 else (2 if along < 0.5 else (3 if along < 0.85 else 4))
    if f in ("up", "north"): tone = min(4, tone + 1) if c["name"].startswith("horn") else tone
    if f in ("south", "down"): tone = max(0, tone - 1)
    # grooves along the horn on the root half: one darker texel column, not every column
    if along < 0.5 and f in ("east", "west", "north", "south") and t.w >= 4 and t.i in (1, t.w - 2): tone = max(0, tone - 1)
    return p[f"horn{tone}"]


def _in_plate(x, y):
    """inside the display face of the plate (plate coords: x across, y up from the skull roof)"""
    if y < 4: return abs(x) < 13 if y > -8 else False
    for nm, hw, y0, y1 in FRILL_PLATE:
        if y0 <= y < y1 and abs(x) < hw: return True
    for nm, x0, x1, y0, y1 in RIM_BUMPS:
        if x0 <= x < x1 and y0 <= y < y1: return True
    return False


def _edge(x, y):
    """1 = the outermost ring of the plate's outline, 2.. = rings further in, 9 = deep inside"""
    for r in range(1, 7):
        if any(not _in_plate(x + dx * r, y + dy * r) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            return r
    return 9


def frill_px(t, p):
    """the display face (north, toward the front and up): body skin near the skull with fine grooves of the blood
    vessels fanning out, a bone rim round the whole outline, and the male's terracotta band inside the rim, chosen
    per whole scale (no gradient). Back and underside: the plain darker body skin."""
    c = t.cube; f = t.face; n = c["name"]
    L = t.L
    y = L[1] - (c["fref"]["from"][1] + 4)
    x = L[0]
    u, v = skin.face_uv_coords(t)
    if f in ("south", "down"):
        s = skin.scales(u, v, cell=5.0, seed=7)
        return p["k1"] if s == "edge" else p["k2"]
    if n.startswith("squam_") and n != "squam_low":
        if f in ("east", "west"):
            s = skin.scales(u, v, cell=4.4, seed=19)
            return p["k2"] if s == "edge" else p["k3"]
        if f == "north":
            s = skin.scales(u, v, cell=4.4, seed=21)
            return p["k2"] if s == "edge" else p["k3"]
        return p["k2"]
    if n.startswith("squam"):
        if f in ("east", "west"): return p["rim2"]
        if f == "north":
            if t.i == (t.w - 1 if c["mirror_of"] is None else 0) and False: return p["rim"]
            s = skin.scales(u, v, cell=4.4, seed=17)
            return p["k2"] if s == "edge" else p["k3"]
        return p["k2"]
    if n.startswith("rim_"):
        return p["rim"] if f in ("north", "up") else p["rim2"]
    if f in ("east", "west", "up"):     # the thickness of the plate at its edge (the steps behind: body skin)
        if f == "up": return p["rim"] if n == "frill_crown" else p["k2"]
        return p["rim2"]
    # north: the display face
    xc, yc = math.floor(x) + 0.5, math.floor(y) + 0.5
    e = _edge(xc, yc)
    if e == 1: return p["rim"]
    # the adult's low rim bumps (epoccipitals, almost fused): the rim swells inward in short, uneven runs
    if e == 2 and yc > 12 and h32(int((xc + 40) // 3), 7) % 5 in (0, 2): return p["rim2"]
    d1, d2, cc = skin.voronoi(xc, yc, 4.4, 13)
    sc = skin.scales(xc, yc, cell=4.4, seed=13)
    ce = _edge(math.floor(cc[2]) + 0.5, math.floor(cc[3]) + 0.5)     # the band is chosen at the scale's centre
    band = None
    if yc < 11: ce = 9                 # the band runs round the top of the fan, not down to the neck
    if ce <= 3: band = "fb2" if ce == 2 else "fb1"
    elif ce <= 5: band = "fb1" if p["male"] else None
    if not p["male"]: band = None          # the female's frill: the body colour inside the bone rim
    if band:
        return p["fb0" if sc == "edge" else band]
    # vessel grooves fan out from the base of the plate: a few wandering darker lines, not evenly spaced
    a = math.atan2(xc, yc + 6.0)
    g = (a * 2.6 + 0.12 * math.sin(yc * 0.45) + 0.05 * h32(int(a * 9), 3) % 3) % 1.0
    if g < 0.07 and 3 < yc < 21: return p["k2"]
    base = "k4" if yc > 9 else "k3"
    return p[STEP_DN[base]] if sc == "edge" else p[base]


def head_px(t, p):
    """head skin: drawn scales, darker on top and down the back of the head, lighter low on the face; pale jaw;
    a solid dark lip line; one light from above"""
    c = t.cube; f = t.face; n = c["name"]
    u, v = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    s = skin.scales(u, v, cell=4.4, seed=seed)
    if n in ("dentary", "jaw_back"):
        if f == "up": return p["gum"]
        if f in ("east", "west", "north"):
            base = "b1" if t.rel[1] < 0.5 else "k4"
            return p["b0"] if s == "edge" and base == "b1" else (p["k3"] if s == "edge" else p[base])
        return p["b1"]
    if f == "down": return p["b0"]
    if f == "up":
        return p["k1"] if s == "edge" else p["k2"]
    k = 4 if t.rel[1] < 0.5 else 3
    if n == "brow": k = 3
    if n == "jugal": k = 4 if t.rel[1] > 0.3 else 3
    if n == "neck_stub": k = 3 if t.rel[1] > 0.4 else 4
    if t.j == t.h - 1 and n in ("cranium", "face", "snout") and f != "south": return p["k1"]      # the lip line
    return _ramp(p, k - 1) if s == "edge" else _ramp(p, k)


STEP_DN = {"k5": "k4", "k4": "k3", "k3": "k2", "k2": "k1", "k1": "k0", "k0": "k0", "b3": "b2", "b2": "b1", "b1": "b0", "b0": "b0"}

# ------------------------------------------------------------------ the body (step 2)
# Model px at 24 px/m, the hip joint at z = 0, the ground at y = 0, the beak toward -z. From the study: the head
# carried low (beak 1 m up), a wide barrel of a trunk whose back RISES to the hips (2.8 m, the highest point), short
# columnar front legs with the elbows a little out and the hands under the shoulders, long straight hind legs
# (a walker of 6-12 t, not a runner), broad four-toed hind feet and three-toed hands with blunt hoof-like nails,
# a short tail that clears the ground.
REST = {"neck": -12, "skull": -8, "tail1": 7, "tail2": 4, "tail3": 3, "tail4": 2, "tail5": 2,
        "thigh": 4, "shin": -7, "foot": 3, "arm": 4, "forearm": -6}


def hind_legs(m, body):
    """pillars, like an elephant's: a deep thigh set into the hip, a slightly bent knee, a short metatarsus and a
    broad foot of four toes, each with a blunt hoof. The thigh in the flank's tone (a lighter one reads as trousers)"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (14 * sx, 50, 0), (REST["thigh"], 0, 2 * sx))
        sh = m.bone(f"shin_{side}", th, (15 * sx, 26, -1), (REST["shin"], 0, -2 * sx))
        ft = m.bone(f"foot_{side}", sh, (15 * sx, 9, 0), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (15 * sx, 3, -4))
    m.pair("thigh_l", "thigh_r", (8, 24, -11), (21, 60, 10), name="thigh")
    m.pair("thigh_l", "thigh_r", (10, 20, -9), (20, 27, 6), name="knee")
    m.pair("shin_l", "shin_r", (10, 7, -8), (20, 22, 4), name="shin")
    m.pair("foot_l", "foot_r", (10.5, 1, -7), (19.5, 10, 2), name="meta")
    m.pair("toes_l", "toes_r", (9, 0, -11), (21, 4, -3), name="pes")
    for nm, x0, z0 in (("hoof_a", 9, -12), ("hoof_b", 12, -13), ("hoof_c", 15, -13), ("hoof_d", 18, -12)):
        m.pair("toes_l", "toes_r", (x0, 0, z0), (x0 + 2, 2, z0 + 3), name=nm, mat="hoof", faces=OUT("south"))


def fore_legs(m, body):
    """short and stout: the upper arm leaves the shoulder going a little OUT (the elbow beside the chest, not under
    it, as the new studies place it), the forearm comes back in so the hand lands under the shoulder; the hand
    stands on its three inner fingers, each with a blunt hoof, the palm turned in"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (13 * sx, 44, -60), (REST["arm"], 0, 10 * sx))
        fa = m.bone(f"forearm_{side}", a, (15 * sx, 24, -60), (REST["forearm"], 0, -14 * sx))
        m.bone(f"hand_{side}", fa, (15 * sx, 6, -60), (0, 0, 4 * sx))
    m.pair("arm_l", "arm_r", (8, 22, -67), (19, 48, -53), name="arm")
    m.pair("forearm_l", "forearm_r", (10, 5, -65), (19, 25, -55), name="forearm")
    m.pair("hand_l", "hand_r", (9.5, 0, -66), (19.5, 6, -55), name="hand")
    for nm, x0 in (("nail_a", 10), ("nail_b", 13), ("nail_c", 16)):
        m.pair("hand_l", "hand_r", (x0, 0, -67), (x0 + 2, 2, -65), name=nm, mat="hoof", faces=OUT("south"))


def tail(m, body):
    """short and thick at the root, tapering fast; carried clear of the ground, a little down"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 10, 34, 11, 40, 61), ("tail2", 32, 54, 8, 43, 60), ("tail3", 52, 72, 5, 46, 57),
        ("tail4", 70, 88, 3, 48, 55), ("tail5", 86, 100, 1.5, 49, 53)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b


def build(sex="male", saddle_on=False):
    m = P.Model("triceratops")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 50, 0))
    # the trunk: a wide barrel, the chest lower and narrower between the front legs, the back rising to the hips
    m.cube(body, (-16, 33, -16), (16, 64, 14), name="hips")
    m.cube(body, (-18, 25, -42), (18, 61, -12), name="torso", rot=(-5, 0, 0), origin=(0, 45, -27))
    m.cube(body, (-16, 28, -70), (16, 54, -38), name="chest", rot=(-7, 0, 0), origin=(0, 42, -54))
    m.cube(body, (-14, 22, -60), (14, 27, -14), name="belly", mat="belly")
    m.cube(body, (-12, 63, -14), (12, 67, 12), name="rump_top")
    m.cube(body, (-13, 59, -40), (13, 63, -13), name="back_top", rot=(-5, 0, 0), origin=(0, 45, -27))
    m.cube(body, (-11, 53, -66), (11, 57, -39), name="withers", rot=(-7, 0, 0), origin=(0, 42, -54))
    # the neck: short and thick, hidden under the frill; the head hangs low in front of the chest
    n = m.bone("neck", body, (0, 44, -66), (REST["neck"], 0, 0))
    m.cube(n, (-12, 24, -86), (12, 45, -62), name="neck")
    m.cube(n, (-9, 21, -84), (9, 27, -66), name="dewlap", mat="belly")
    hd = m.bone("head", n, (0, 36, -84))
    head(m, hd, 26, -86, sex, rest=(REST["skull"], 0, 0))
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    if saddle_on: saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the saddle: a drover's pack saddle (cangalha)
SADDLE_PAL = {   # its own: hewn wood, cured hide, palm-fibre baskets and twisted rope (no wool, no iron: the Giga has
                 # the gaucho recado, the Carno the jockey saddle)
    "D0": hx("3b2a1c"), "D1": hx("5c4129"), "D2": hx("7d5a37"), "D3": hx("9a7446"),     # hewn wood of the frame
    "H0": hx("3a2a22"), "H1": hx("57402f"), "H2": hx("70553d"), "H3": hx("8c6d4c"),     # cured hide: pad and seat
    "F0": hx("564a2e"), "F1": hx("74663f"), "F2": hx("8f7f50"), "F3": hx("a69765"),     # woven palm fibre: the balaios
    "R0": hx("5e5036"), "R1": hx("857350"),                                              # twisted rope
    "G0": hx("463626"), "G1": hx("6a5236"),                                              # the woven girth
}
SADDLE_MATS = ("wood", "hide", "fibre", "rope", "girth")


def saddle(m, body):
    """A cangalha, the Brazilian drover's pack saddle, sized for a 9 m animal: a hide pad on the back; a wooden frame
    of two A-shaped arches joined by side rails; a big woven basket (balaio) hanging on each side, the cargo of its
    four rows; a hide seat with a rolled blanket on top of the arches; rope stirrups with a wooden step outside the
    baskets; one woven girth under the belly. Faces lying on the body or on another layer are left out."""
    sd = m.bone("saddle", body, (0, 63, -28), (-5, 0, 0))
    m.cube(sd, (-14, 63, -42), (14, 65, -14), name="pad", mat="hide", faces=OUT("down"))
    m.pair(sd, sd, (14, 52, -42), (15, 65, -14), name="pad_side", mat="hide", faces=OUT("east"))
    for nm, z0 in (("arch_f", -40), ("arch_b", -19)):          # the A-frame: two legs leaning in, a cap on top
        m.pair(sd, sd, (6, 64, z0), (9, 72, z0 + 3), name=nm, mat="wood", rot=(0, 0, 24), origin=(7.5, 64, z0 + 1.5), faces=OUT("down"))
        m.cube(sd, (-5, 71, z0), (5, 74, z0 + 3), name=nm + "_cap", mat="wood")
    m.pair(sd, sd, (12, 63, -41), (15, 66, -15), name="rail", mat="wood", faces=OUT("east", "down"))
    m.cube(sd, (-7, 74, -36), (7, 76, -21), name="seat", mat="hide", faces=OUT("down"))
    m.cube(sd, (-8, 74, -20), (8, 78, -16), name="roll", mat="hide", faces=OUT("down"))
    # the balaios hang from the rails on two ropes each
    m.pair(sd, sd, (16, 36, -39), (23, 58, -18), name="balaio", mat="fibre")
    m.pair(sd, sd, (15, 57, -37), (16, 64, -35), name="strap_f", mat="rope", faces=OUT("east"))
    m.pair(sd, sd, (15, 57, -22), (16, 64, -20), name="strap_b", mat="rope", faces=OUT("east"))
    # rope stirrups: from the seat over the basket's top edge, a wooden step at the end
    m.pair(sd, sd, (23, 49, -29), (24, 59, -27), name="stirrup_rope", mat="rope", faces=OUT("east"))
    m.pair(sd, sd, (22, 47, -31), (26, 49, -25), name="stirrup_step", mat="wood")
    m.pair(sd, sd, (16, 58, -29), (24, 59, -27), name="stirrup_over", mat="rope", faces=OUT("down"))   # over the basket rim
    # the girth: down the side under the basket, across under the belly
    m.pair(sd, sd, (14, 24, -30), (15, 52, -27), name="girth_side", mat="girth", faces=OUT("east"))
    m.cube(sd, (-15, 21, -30), (15, 22, -27), name="girth_under", mat="girth", faces=OUT("up"))


def saddle_px(t):
    """light from above, the bottom edge of each piece one step darker; the basket weave drawn as offset rows (a
    brick weave, never a checker), its rim and bottom bound darker"""
    c = t.cube; mat = c["mat"]; n = c["name"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "wood":
        if f == "up": return p["D3"]
        if f == "down": return p["D0"]
        if j == h - 1 and h > 2: return p["D1"]
        return p["D2"] if (i + 3 * (j // 4)) % 7 else p["D1"]           # a grain line now and then
    if mat == "hide":
        if f == "up":
            edge = i == 0 or j == 0 or i == w - 1 or j == h - 1
            if n == "roll": return p["H3"] if j % 2 == 0 else p["H2"]
            return p["H1"] if edge else p["H2"]
        return p["H0"] if j == h - 1 else p["H1"]
    if mat == "fibre":
        if f == "up": return p["F1"] if (i == 0 or j == 0 or i == w - 1 or j == h - 1) else p["F0"]   # open top
        if f == "down": return p["F0"]
        if j <= 1: return p["F1"] if j == 0 else p["F0"]                 # the bound rim
        if j >= h - 2: return p["F0"]                                     # the bound bottom
        row = (j - 2) // 2; k = (i + (row % 2) * 2) % 4
        return p["F3"] if (k == 0 and (j - 2) % 2 == 0) else (p["F1"] if k == 3 else p["F2"])
    if mat == "rope":
        return p["R1"] if (j + i) % 3 else p["R0"]
    if mat == "girth":
        return p["G1"] if (w >= 3 and i == w // 2) else p["G0"]
    return p["D2"]


def preview_faces(m):
    """previews only, BEFORE packing: swap east/west on cubes that drop one, so the preview shows what the game shows
    (geo.load_geo puts a dropped model "east" face on the outer side, GeckoLib on the inner one)"""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m


# ------------------------------------------------------------------ the body skin
# House skin (drawn scales, tone per whole scale, a seam on the shaded side, belly scutes) with the Triceratops marks
# from the study: a dark plum back over lighter flanks and a rose-grey belly, the border wandering between whole
# scales; the "Lane" tubercles: big polygonal scales with a cone in the middle, lit on the upper face, scattered over
# the flank and the thigh (never in rows); elephant-like creased skin on the legs; blunt hooves.
TRUNK = {"hips", "torso", "chest", "rump_top", "back_top", "withers", "neck", "tail1", "tail2", "tail3", "tail4", "tail5", "thigh", "knee", "arm", "neck_stub"}
UNDERSIDE = {"belly", "dewlap"}
LEG = {"shin", "meta", "pes", "forearm", "hand"}
BODY_PARTS = TRUNK | UNDERSIDE | LEG
UNDER = {"chest": 0.20, "torso": 0.16, "hips": 0.10, "neck": 0.26, "tail1": 0.18, "tail2": 0.22, "tail3": 0.26,
         "tail4": 0.3, "tail5": 0.34, "neck_stub": 0.3}
CELL = 4.6


def _line(n, z):
    return UNDER.get(n, 0.3) + 0.05 * math.sin(z * 0.13 + 0.7) + 0.04 * math.sin(z * 0.31 + 2.1)


def body_px(t, p):
    c = t.cube; n = c["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    u_, w_ = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    belly = lambda uu, ww, width=7: p[{"seam": "b0", "hi": "b2", "base": "b1"}[skin.scutes(uu, ww, row=3, width=width)]]
    if c["mat"] == "hoof":
        if f == "up": return p["horn2"]
        return p["horn1"] if t.j < t.h - 1 else p["horn0"]
    # the underside: wide scutes
    if (f == "down" and n not in LEG and n not in ("thigh", "knee", "arm")) or n in UNDERSIDE:
        if f == "up": return p["k3"]
        if f == "down": return belly(t.L[0], t.L[2])
        return belly(u_, w_)
    # legs: thick creased skin, the creases across the limb (an elephant's), darker toward the foot
    if n in LEG:
        low = n in ("meta", "pes", "hand")
        base = ("k2" if low else "k3") if f in ("east", "west", "north", "up") else ("k1" if low else "k2")
        crease = (math.floor(t.L[1]) + h32(int(t.L[2] // 3), int(t.L[0] // 3), seed) % 2) % 4 == 0
        if crease and f != "up": return p[STEP_DN[base]]
        return p[STEP_DN[base]] if skin.scales(u_, w_, cell=3.6, seed=seed) == "edge" else p[base]
    if f == "up":
        sc = skin.scales(u_, w_, cell=CELL, seed=seed)
        return p["k1"] if sc == "edge" else p["k2"]
    # trunk, neck, tail, thigh, arm: tone per whole scale, by the height of its centre
    d1, d2, cc = skin.voronoi(math.floor(u_) + 0.5, math.floor(w_) + 0.5, CELL, seed)
    if side and n in UNDER:
        vc = (cc[3] - c["from"][1]) / max(1, t.h) if f in ("east", "west") else t.rel[1]
        if vc < _line(n, cc[2] if f in ("east", "west") else t.L[2]):
            return belly(u_, w_)
    else:
        vc = t.rel[1] if side else 1.0
    if n in ("thigh", "knee", "arm"):
        base = "k3" if t.rel[1] > 0.35 else "k2"
    else:
        base = "k4" if vc < 0.46 else ("k3" if vc < 0.74 else "k2")
    # the Lane tubercles: big polygonal scales with a cone, on the flank and the thigh only, scattered
    if f in ("east", "west") and n in ("hips", "torso", "chest", "thigh"):
        e1, e2, tt = skin.voronoi(u_, w_, 10.0, seed + 11)
        if h32(tt[0], tt[1], seed, 4) % 3 == 0 and e1 < 3.8 and 0.3 < vc < 0.9:
            dy = w_ - tt[3]
            if e1 > 3.0: return p[STEP_DN[base]]
            if dy > 1.0: return p[{"k2": "k3", "k3": "k4", "k4": "k5"}[base]]
            if dy < -0.9: return p[STEP_DN[base]]
            return p[base]
    sc = skin.scales(u_, w_, cell=CELL, seed=seed)
    return p[STEP_DN[base]] if sc == "edge" else p[base]


def _col(u, w, i):
    """texture column of face-local column i (a face packed as a mirror of its twin runs backwards)"""
    return u + i if w > 0 else u - 1 - i


def decals_for(sex):
    p = pal_for(sex)

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        cr = C["cranium"]
        cmap = {"s": p["k1"], "Y": p["eyeY"], "E": p["eyeE"], "e": p["eyee"], "p": p["pupil"], "g": p["glint"],
                "D": p["eyeD"], "L": p["lid"], "d": p["k0"]}
        for f in ("east", "west"):
            u, v, w, h = cr["uv"][f]
            # the eye: under the brow (the cranium top is y 17: the brow covers 12..15), its front 2 px behind the face
            for j, row in enumerate(EYE):
                for k, ch in enumerate(row):
                    if ch == ".": continue
                    i = (abs(w) - 3 - k) if f == "east" else (2 + k)
                    img[v + 5 + j, _col(u, w, i)] = (*cmap[ch], 255)
        sn = C["snout"]
        for f in ("east", "west"):     # the nostril: a long slit high on the snout, under the nose horn
            u, v, w, h = sn["uv"][f]
            for d in range(3):
                i0 = (1 + d) if f == "east" else abs(w) - 2 - d
                img[v + 3, _col(u, w, i0)] = (*p["nost"], 255)
            i1 = 2 if f == "east" else abs(w) - 3
            img[v + 4, _col(u, w, i1)] = (*p["k2"], 255)
    return dec


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
