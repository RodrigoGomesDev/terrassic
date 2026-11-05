"""Styracosaurus albertensis, made by hand from its own study (page "Estiracossauro: estudo para a 1.8", approved by
Rodrigo on 05/11/2026: the shape, the "argila rosada" colour and the reed-and-mud nest). Real size 5.5 m, about
2.7 t (Ryan et al. 2007), Dinosaur Park Formation, Alberta, about 75 million years ago.

Drawn at 32 px = 1 m (game scale 0.5): the skull with its frill is about 1.8 m, so it gets 58 px for the narrow
beak, the tall nose horn, the brow bumps, the eye and the crown of spikes.

What makes it itself (each point from the study, none taken from another species of the mod):
- ONE long horn, standing up from the nose: up to 57 cm long and about 15 cm wide at the root (Lambe 1913), straight,
  leaning only a little forward; the brow horns are low bumps over the eye (the reverse of the Triceratops);
- the CROWN: four to six long spikes, up to about 55 cm, from the back edge of a short frill, fanned out so that from
  the front the crown is wider than the body (Ryan, Holmes & Russell 2007). Their number and angle vary between
  animals: here the male carries six long ones and the female six shorter ones (bones "male_display" and
  "female_display" under "adult_frill");
- the frill is bone with two big windows under the skin (never painted: the skin over them is whole), a display
  surface (Padian & Horner 2011);
- the GROWTH SERIES of the centrosaurines: the calf has a short nose horn and a frill with small points that later
  grow into the spikes (bones "young_horns" and "young_frill", shown on babies only; "adult_horns" and "adult_frill"
  on the grown animal, DinoGeoModel);
- the back RISES to the hips (about 1.9 m, the highest point of the body), a short tail, a big low head; the forelegs
  half bent with the elbows a little out, not sprawling (Thompson & Holmes 2007); four-toed hind feet and hands with
  blunt hoof-like nails;
- a narrow beak for low plants.

The colour ("argila rosada", docs/CORES.md): a big animal of the river plain, a calm pink-grey clay like a hippo's
hide, a darker back, a pale belly, no stripes. The frill is the display: wine-red on the male, a faded rose-brown on
the female; spikes and horn the colour of bone, darkening toward the tips.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 32
FRILL_TILT = 42          # degrees the frill plate leans back from the vertical of the skull

SCHEMES = {
    "argila": {
        "k0": "3c2629", "k1": "56393d", "k2": "705053", "k3": "8e686b", "k4": "a87d81", "k5": "bb9193",
        "b0": "bfa098", "b1": "cfb3a9", "b2": "dcc4b9", "b3": "e8d5ca",
        "fb0": "4a1d23", "fb1": "6a2f34", "fb2": "843f46", "fb3": "9b5258",          # the male's wine frill
        "rim": "dcc8b6", "rim2": "bea996",
        "female": {"k3": "8f6f6d", "k4": "a98683", "k5": "ba9894",
                   "fb0": "5a3a3a", "fb1": "7a5454", "fb2": "8d6763", "fb3": "9f7a75"},
    },
}
SCHEME = ["argila"]

PAL = {
    "beak0": hx("231c1d"), "beak1": hx("3a3132"), "beak2": hx("524647"), "beak3": hx("7a6c6a"),
    # bone-coloured horn and spikes: ivory at the root, darkening to the tip
    "horn0": hx("e2d6c0"), "horn1": hx("cbbda2"), "horn2": hx("a8987d"), "horn3": hx("7c6c58"), "horn4": hx("4e4236"),
    "eyeY": hx("c9973e"), "eyeE": hx("9c6a2a"), "eyee": hx("62401d"), "pupil": hx("120d0b"), "glint": hx("efe6c8"),
    "eyeD": hx("1c1418"),
    "nost": hx("2a1a1e"), "gum": hx("6e3a42"), "mouth": hx("33181e"), "tongue": hx("94505a"),
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

# the nose horn: stacked pieces along the horn's own +y (half width, length), the whole horn leaning forward a little
NOSE = [(2.5, 6), (2, 6), (1.5, 5), (1, 4), (0.5, 2)]
NOSE_LEAN = -12
YOUNG_NOSE = [(1.5, 3), (1, 2)]

# the crown: (x on the rim, y on the plate, fan angle from the plate's vertical (out to the side), lean back
# (deg about x), length of the male's spike, length of the female's). Uneven on purpose: the real spikes vary.
SPIKES = [(3, 25, 10, 14, 18, 13), (9, 23, 33, 10, 18, 14), (13, 18, 58, 6, 15, 11), (14, 11, 84, 2, 7, 5)]


def head(m, parent, hy, hz, sex="male", rest=(0, 0, 0)):
    """skull, nose horn, frill with the crown, and jaw. (hy, hz): the mouth line at the jaw joint; returns the skull"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    sk = m.bone("skull", parent, (0, hy + 6, hz), rest)
    # the skull: deep at the snout (the centrosaurine nasal), wide at the cheeks, narrowing to the beak
    m.cube(sk, *B(-8, -1, -13, 8, 16, 1), name="cranium")
    m.cube(sk, *B(-6, 0, -24, 6, 15, -12), name="face", faces=OUT("south"))
    m.cube(sk, *B(-4, 1, -33, 4, 16, -23), name="snout", faces=OUT("south"))
    m.cube(sk, *B(-2, 1, -37, 2, 10, -32), name="rostral", mat="beak", faces=OUT("south"))
    m.cube(sk, *B(-1.5, -3, -39, 1.5, 5, -36), name="hook", mat="beak", faces=OUT("south"))
    # the brow: low bumps over the eye, all that is left of the brow horns
    m.pair(sk, sk, *B(7, 14, -11, 9, 17, -7), name="brow", faces=OUT("west"))
    m.pair(sk, sk, *B(6, 17, -10, 8, 19, -8), name="brow_horn", mat="horn", hseg=1, hlen=3, faces=OUT("down"))
    # the cheeks: the jugal flaring out under the eye, a short blunt point
    m.pair(sk, sk, *B(7, -3, -14, 10, 7, -3), name="jugal", faces=OUT("west"))
    m.pair(sk, sk, *B(9, -4, -10, 11, -1, -8), name="epijugal", mat="horn", faces=OUT("up"),
           rot=(0, 0, 24), origin=(10, hy - 1, hz - 9), hseg=1, hlen=3)
    # the nose horn over the nostril: the adult's tall straight horn, the calf's nub
    for bone_name, parts in (("adult_horns", NOSE), ("young_horns", YOUNG_NOSE)):
        hb = m.bone(bone_name, sk, (0, hy + 15, hz - 28), (NOSE_LEAN, 0, 0))
        y = hy + 15
        total = sum(ln for _, ln in parts)
        for k, (hw, ln) in enumerate(parts):
            m.cube(hb, (-hw, y, hz - 28 - hw), (hw, y + ln + (1 if k == 0 else 0), hz - 28 + hw),
                   name=f"{bone_name}_{k}", mat="horn", faces=OUT("down") if k else None, hseg=k, hlen=total)
            y += ln + (1 if k == 0 else 0)
    # the frill: its own bone at the back of the skull roof, leaning back; a short plate in stepped widths
    fr = m.bone("frill", sk, (0, hy + 15, hz), (FRILL_TILT, 0, 0))
    F = lambda x0, y0, z0, x1, y1, z1: ((x0, hy + 15 + y0, hz + z0), (x1, hy + 15 + y1, hz + z1))
    base = m.cube(fr, *F(-7, -4, -1, 7, 4, 2), name="frill_base", mat="frill", faces=OUT("up"))
    for nm, hw, y0, y1 in FRILL_PLATE:
        m.cube(fr, *F(-hw, y0, -1, hw, y1, 1), name=nm, mat="frill")
    m.pair(fr, fr, *F(7, -7, -0.5, 11, 5, 1.5), name="squam_low", mat="frill")     # the sides run down behind the eye
    # the sides of the plate bend forward (the squamosals): seen from the side the frill is a surface, not a stick
    m.pair(fr, fr, *F(10, -3, -7, 12, 13, -1), name="squam_a", mat="frill", faces=OUT("west", "south"))
    m.pair(fr, fr, *F(12, 13, -5, 14, 19, -1), name="squam_b", mat="frill", faces=OUT("west", "south"))
    for c in m.cubes:
        if c["mat"] == "frill": c["fref"] = base
    # the crown on the adult (long on the male, shorter on the female); small points on the calf
    fy = hy + 15
    ad = m.bone("adult_frill", fr, (0, fy, hz))
    for disp, col in (("male_display", 4), ("female_display", 5)):
        d = m.bone(disp, ad, (0, fy, hz))
        for k, row in enumerate(SPIKES):
            x, y, fan, lean, *lens = row
            for side, sx in (("l", 1), ("r", -1)):
                spike_at(m, d, f"{disp[0]}spike{k}_{side}", x, fy + y, hz, fan, lean, lens[col - 4], sx)
    yf = m.bone("young_frill", fr, (0, fy, hz))
    for k, (x, y) in enumerate(((4, 25), (10, 22), (13, 17))):
        for side, sx in (("l", 1), ("r", -1)):
            m.cube(yf, (x * sx - 1, fy + y - 1, hz - 1.5), (x * sx + 1, fy + y + 2, hz + 1.5),
                   name=f"ypoint{k}_{side}", mat="horn", hseg=0, hlen=3)
    # the jaw: hinged at the back under the cheek, the dark predentary at the tip
    jaw = m.bone("jaw", sk, (0, hy + 1, hz - 2))
    m.cube(jaw, *B(-2, -4, -38, 2, 0, -32), name="predentary", mat="beak", faces=OUT("south", "up"))
    m.cube(jaw, *B(-4, -5, -33, 4, 0, -21), name="dentary", faces=OUT("south"))
    m.cube(jaw, *B(-6, -8, -22, 6, 0, -2), name="jaw_back")
    m.cube(jaw, *B(-5, -9, -17, 5, -7, -2), name="gular", mat="gular", faces=OUT("up"))
    m.cube(jaw, *B(-5, -1, -21, 5, 2, -4), name="cheek_in", mat="mouth")
    m.cube(jaw, *B(-1, -2, -31, 1, 1, -6), name="tongue", mat="tongue")
    m.cube(sk, *B(-1.5, -1, -35, 1.5, 3, -15), name="palate", mat="mouth")
    return sk


def spike_at(m, parent, name, x, y, z, fan, lean, length, side):
    """a spike rooted on the rim at (x * side, y, z), fanned out (about z) and leaning back (about x)"""
    b = m.bone(name, parent, (x * side, y, z), (lean, 0, -fan * side))
    yy = y - 1
    for k, (hw, frac) in enumerate(((1.5, 0.42), (1.0, 0.34), (0.5, 0.24))):
        ln = max(1, round(length * frac))
        m.cube(b, (x * side - hw, yy, z - hw), (x * side + hw, yy + ln + (1 if k == 0 else 0), z + hw),
               name=f"{name}_{k}", mat="horn", faces=OUT("down") if k else None, hseg=k, hlen=length)
        yy += ln + (1 if k == 0 else 0)


# the plate, measured up from the skull roof (half width, y0, y1): short and broad, the spikes carry the height
FRILL_PLATE = [("frill_low", 10, 4, 8), ("frill_mid", 12, 8, 13), ("frill_wide", 14, 13, 18),
               ("frill_top", 13, 18, 22), ("frill_top2", 11, 22, 25), ("frill_crown", 7, 25, 27)]


# ------------------------------------------------------------------ paint
EYE = ["sdddds", "dYgYEd", "dYpEed", "dEpeed", ".dddd."]


def _ramp(p, k):
    return p[f"k{max(0, min(5, k))}"]


STEP_DN = {"k5": "k4", "k4": "k3", "k3": "k2", "k2": "k1", "k1": "k0", "k0": "k0", "b3": "b2", "b2": "b1", "b1": "b0", "b0": "b0"}
STEP_UP = {"k0": "k1", "k1": "k2", "k2": "k3", "k3": "k4", "k4": "k5", "k5": "k5"}


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        c = t.cube; f = t.face; mat = c["mat"]; n = c["name"]
        i, j, w, h = t.i, t.j, t.w, t.h
        if mat == "beak":
            if f == "up": return p["beak2"]
            if f == "down": return p["beak0"]
            if n == "hook" and f in ("east", "west", "north"):
                return p["beak3"] if j >= h - 1 else p["beak1"]
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
    """bone over keratin: ivory at the root, darkening toward the point; long grooves on the root half (never rings,
    never stripes: the old model's banded horn is gone); lit on the upper and front faces"""
    c = t.cube; f = t.face; k = c.get("hseg", 0); n = c["name"]
    if c["name"].startswith(("brow_horn", "epijugal")):
        return p["horn2"] if f in ("up", "north") else p["horn3"]
    if n.startswith("ypoint"): return p["horn1"] if f in ("up", "north") else p["horn2"]
    nseg = 5 if n.startswith(("adult_horns", "young_horns")) else 3
    along = min(1.0, (k + t.rel[1]) / nseg)
    tone = 0 if along < 0.3 else (1 if along < 0.55 else (2 if along < 0.78 else (3 if along < 0.92 else 4)))
    if f in ("south", "down", "west") and tone < 4: tone += 1
    if along < 0.5 and f in ("east", "west", "north", "south") and t.w >= 3 and t.i == t.w // 2 and tone < 4:
        tone += 1
    return p[f"horn{tone}"]


def _in_plate(x, y):
    if y < 4: return abs(x) < 10 if y > -7 else False
    for nm, hw, y0, y1 in FRILL_PLATE:
        if y0 <= y < y1 and abs(x) < hw: return True
    return False


def _edge(x, y):
    for r in range(1, 7):
        if any(not _in_plate(x + dx * r, y + dy * r) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            return r
    return 9


def frill_px(t, p):
    """the display face (north): a bone rim round the outline; inside it the wine of the male (the faded rose-brown
    of the female), chosen per whole scale, darker toward the rim, with the vessel grooves fanning out from the base;
    near the skull the body skin. Back and underside: plain darker body skin. The windows are under the skin and are
    not painted."""
    c = t.cube; f = t.face; n = c["name"]
    y = t.L[1] - (c["fref"]["from"][1] + 4)
    x = t.L[0]
    u, v = skin.face_uv_coords(t)
    if f in ("south", "down"):
        s = skin.scales(u, v, cell=4.0, seed=7)
        return p["k1"] if s == "edge" else p["k2"]
    if n.startswith("squam"):
        s = skin.scales(u, v, cell=4.0, seed=17)
        if f == "up": return p["rim"]
        if f in ("east", "west") and n != "squam_low":
            if t.j == 0: return p["rim2"]                      # the bone edge of the frill seen from the side
            return p["fb0"] if s == "edge" else (p["fb1"] if t.rel[1] > 0.5 else p["k3"])
        return p["k2"] if s == "edge" else p["k3"]
    if f in ("east", "west", "up"):
        return p["rim"] if f == "up" and n == "frill_crown" else p["rim2"]
    xc, yc = math.floor(x) + 0.5, math.floor(y) + 0.5
    e = _edge(xc, yc)
    if e == 1: return p["rim"]
    d1, d2, cc = skin.voronoi(xc, yc, 4.0, 13)
    sc = skin.scales(xc, yc, cell=4.0, seed=13)
    if yc < 6:      # the root of the frill: body skin
        return p["k2"] if sc == "edge" else p["k3"]
    ce = _edge(math.floor(cc[2]) + 0.5, math.floor(cc[3]) + 0.5)
    tone = "fb1" if ce <= 3 else ("fb2" if ce <= 6 or yc > 14 else "fb3")
    a = math.atan2(xc, yc + 5.0)
    g = (a * 2.4 + 0.1 * math.sin(yc * 0.5) + 0.05 * (h32(int(a * 9), 3) % 3)) % 1.0
    if g < 0.08 and 6 < yc < 22: return p["fb0"]
    return p["fb0"] if sc == "edge" else p[tone]


def head_px(t, p):
    c = t.cube; f = t.face; n = c["name"]
    u, v = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    s = skin.scales(u, v, cell=4.0, seed=seed)
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
    if n == "snout" and t.rel[1] > 0.6: k = 3
    if t.j == t.h - 1 and n in ("cranium", "face", "snout") and f != "south": return p["k1"]      # the lip line
    return _ramp(p, k - 1) if s == "edge" else _ramp(p, k)


# ------------------------------------------------------------------ the body
# Model px at 32 px/m, the hip joint at z = 0, the ground at y = 0, the beak toward -z. From the study: the back
# rising to the hips (1.9 m), a short tail clear of the ground, a big low head on a short neck, the forelegs half
# bent with the elbows a little out, four-toed hind feet and three-toed hands with blunt nails.
REST = {"neck": -10, "skull": -10, "tail1": 9, "tail2": 6, "tail3": 4, "tail4": 3,
        "thigh": 4, "shin": -8, "foot": 4, "arm": 6, "forearm": -9}


def hind_legs(m, body):
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (12 * sx, 50, 0), (REST["thigh"], 0, 2 * sx))
        sh = m.bone(f"shin_{side}", th, (13 * sx, 28, -1), (REST["shin"], 0, -2 * sx))
        ft = m.bone(f"foot_{side}", sh, (13 * sx, 11, 0), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (13 * sx, 3, -3))
    m.pair("thigh_l", "thigh_r", (7, 25, -9), (18, 56, 8), name="thigh")
    m.pair("thigh_l", "thigh_r", (8, 21, -7), (17, 27, 5), name="knee")
    m.pair("shin_l", "shin_r", (8, 9, -6), (17, 23, 3), name="shin")
    m.pair("foot_l", "foot_r", (9, 1, -5), (17, 12, 1), name="meta")
    m.pair("toes_l", "toes_r", (8, 0, -9), (18, 3, -2), name="pes")
    for nm, x0, z0 in (("hoof_a", 8, -10), ("hoof_b", 11, -11), ("hoof_c", 14, -11), ("hoof_d", 16, -10)):
        m.pair("toes_l", "toes_r", (x0, 0, z0), (x0 + 2, 2, z0 + 2), name=nm, mat="hoof", faces=OUT("south"))


def fore_legs(m, body):
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (11 * sx, 40, -44), (REST["arm"], 0, 10 * sx))
        fa = m.bone(f"forearm_{side}", a, (13 * sx, 21, -44), (REST["forearm"], 0, -14 * sx))
        m.bone(f"hand_{side}", fa, (13 * sx, 5, -44), (0, 0, 4 * sx))
    m.pair("arm_l", "arm_r", (7, 19, -49), (16, 44, -39), name="arm")
    m.pair("forearm_l", "forearm_r", (8, 4, -48), (16, 22, -40), name="forearm")
    m.pair("hand_l", "hand_r", (8, 0, -49), (17, 5, -40), name="hand")
    for nm, x0 in (("nail_a", 9), ("nail_b", 12), ("nail_c", 15)):
        m.pair("hand_l", "hand_r", (x0, 0, -50), (x0 + 2, 2, -48), name=nm, mat="hoof", faces=OUT("south"))


def tail(m, body):
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 10, 30, 10, 37, 57), ("tail2", 28, 46, 7, 40, 54), ("tail3", 44, 60, 4.5, 42, 51),
        ("tail4", 58, 71, 2.5, 44, 49)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b


def build(sex="male", saddle_on=False):
    m = P.Model("styracosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 48, 0))
    # the trunk: the back rising from the withers to the hips, the chest lower and narrower between the forelegs
    m.cube(body, (-14, 32, -14), (14, 60, 12), name="hips")
    m.cube(body, (-16, 26, -38), (16, 57, -12), name="torso", rot=(-6, 0, 0), origin=(0, 42, -25))
    m.cube(body, (-14, 28, -54), (14, 51, -36), name="chest", rot=(-8, 0, 0), origin=(0, 40, -45))
    m.cube(body, (-12, 24, -48), (12, 29, -12), name="belly", mat="belly")
    m.cube(body, (-10, 59, -12), (10, 63, 10), name="rump_top")
    m.cube(body, (-11, 55, -37), (11, 59, -11), name="back_top", rot=(-6, 0, 0), origin=(0, 42, -25))
    m.cube(body, (-9, 49, -52), (9, 53, -37), name="withers", rot=(-8, 0, 0), origin=(0, 40, -45))
    # the neck: short and thick, hidden under the frill; the head carried low in front of the chest
    n = m.bone("neck", body, (0, 40, -52), (REST["neck"], 0, 0))
    m.cube(n, (-11, 24, -68), (11, 43, -48), name="neck")
    m.cube(n, (-8, 21, -66), (8, 26, -51), name="dewlap", mat="belly")
    hd = m.bone("head", n, (0, 34, -66))
    head(m, hd, 22, -68, sex, rest=(REST["skull"], 0, 0))
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    if saddle_on: saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the saddle: a running pad
SADDLE_PAL = {   # its own: no wooden frame, no baskets (the Triceratops' cangalha), no wool or iron
    "H0": hx("4a3226"), "H1": hx("6a4a36"), "H2": hx("85614a"), "H3": hx("a07b5e"),     # thick cured hide pad
    "F0": hx("8a7a5c"), "F1": hx("a6966f"),                                              # the fringe of the pad
    "D0": hx("3e2b1c"), "D1": hx("5e432a"), "D2": hx("7d5c3a"), "D3": hx("9a7a52"),     # the grip bar's posts
    "R0": hx("5e5036"), "R1": hx("857350"),                                              # twisted rope
    "G0": hx("4b5a36"), "G1": hx("63744a"),                                              # woven rush girth
    "B0": hx("cfc2a8"), "B1": hx("a8987a"),                                              # bone toggles
}
SADDLE_MATS = ("hide", "fringe", "wood", "rope", "girth", "bone")


def saddle(m, body):
    """A running pad for a quick, middle-sized mount: a thick hide pad over the withers and the back, its fringe hanging
    on the flanks; in front a grip bar on two short posts (the rider sits behind the crown and holds on in the
    charge); knotted rope foot loops with bone toggles; a woven rush girth under the chest."""
    sd = m.bone("saddle", body, (0, 58, -26), (-6, 0, 0))
    m.cube(sd, (-12, 58, -40), (12, 61, -14), name="pad", mat="hide", faces=OUT("down"))
    m.pair(sd, sd, (12, 50, -39), (13, 61, -15), name="pad_side", mat="hide", faces=OUT("east"))
    m.pair(sd, sd, (13, 47, -38), (14, 51, -16), name="fringe", mat="fringe", faces=OUT("east"))
    m.cube(sd, (-7, 61, -33), (7, 63, -18), name="seat", mat="hide", faces=OUT("down"))
    m.pair(sd, sd, (4, 61, -40), (6, 67, -38), name="post", mat="wood", faces=OUT("down"))
    m.cube(sd, (-6, 67, -41), (6, 69, -37), name="grip", mat="wood")
    m.pair(sd, sd, (14, 40, -27), (15, 51, -25), name="loop_rope", mat="rope", faces=OUT("east"))
    m.pair(sd, sd, (14, 38, -29), (17, 40, -23), name="loop_foot", mat="rope")
    m.pair(sd, sd, (16, 40, -27), (18, 42, -25), name="toggle", mat="bone")
    m.pair(sd, sd, (12, 26, -30), (13, 50, -27), name="girth_side", mat="girth", faces=OUT("east"))
    m.cube(sd, (-13, 23, -30), (13, 24, -27), name="girth_under", mat="girth", faces=OUT("up"))


def saddle_px(t):
    c = t.cube; mat = c["mat"]; n = c["name"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "hide":
        if f == "up":
            edge = i == 0 or j == 0 or i == w - 1 or j == h - 1
            if n == "seat": return p["H3"] if (i + j) % 5 else p["H2"]
            return p["H1"] if edge else (p["H3"] if (i * 7 + j * 3) % 11 == 0 else p["H2"])
        return p["H0"] if j == h - 1 else p["H1"]
    if mat == "fringe":
        return p["F1"] if (i % 2 == 0 and j < h - 1) else (p["F0"] if j < h - 1 or i % 2 == 0 else p["F0"])
    if mat == "wood":
        if f == "up": return p["D3"]
        if f == "down": return p["D0"]
        return p["D2"] if (i + 2 * j) % 5 else p["D1"]
    if mat == "rope":
        return p["R1"] if (j + i) % 3 else p["R0"]
    if mat == "girth":
        return p["G1"] if (j + i) % 2 else p["G0"]
    if mat == "bone":
        return p["B0"] if f in ("up", "north") else p["B1"]
    return p["H2"]


def preview_faces(m):
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m


# ------------------------------------------------------------------ the body skin
# Drawn scales, tone per whole scale: a darker back over the clay flanks, a pale belly, the border wandering between
# whole scales; a few bigger round scales scattered on the flank and the thigh (never in rows); creased leg skin.
TRUNK = {"hips", "torso", "chest", "rump_top", "back_top", "withers", "neck", "tail1", "tail2", "tail3", "tail4",
         "thigh", "knee", "arm"}
UNDERSIDE = {"belly", "dewlap"}
LEG = {"shin", "meta", "pes", "forearm", "hand"}
BODY_PARTS = TRUNK | UNDERSIDE | LEG
UNDER = {"chest": 0.22, "torso": 0.18, "hips": 0.12, "neck": 0.28, "tail1": 0.2, "tail2": 0.24, "tail3": 0.28,
         "tail4": 0.32}
CELL = 4.2


def _line(n, z):
    return UNDER.get(n, 0.3) + 0.05 * math.sin(z * 0.15 + 0.4) + 0.04 * math.sin(z * 0.37 + 1.9)


def body_px(t, p):
    c = t.cube; n = c["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    u_, w_ = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    belly = lambda uu, ww, width=7: p[{"seam": "b0", "hi": "b2", "base": "b1"}[skin.scutes(uu, ww, row=3, width=width)]]
    if c["mat"] == "hoof":
        if f == "up": return p["horn2"]
        return p["horn3"] if t.j < t.h - 1 else p["horn4"]
    if (f == "down" and n not in LEG and n not in ("thigh", "knee", "arm")) or n in UNDERSIDE:
        if f == "up": return p["k3"]
        if f == "down": return belly(t.L[0], t.L[2])
        return belly(u_, w_)
    if n in LEG:
        low = n in ("meta", "pes", "hand")
        base = ("k2" if low else "k3") if f in ("east", "west", "north", "up") else ("k1" if low else "k2")
        crease = (math.floor(t.L[1]) + h32(int(t.L[2] // 3), int(t.L[0] // 3), seed) % 2) % 4 == 0
        if crease and f != "up": return p[STEP_DN[base]]
        return p[STEP_DN[base]] if skin.scales(u_, w_, cell=3.4, seed=seed) == "edge" else p[base]
    if f == "up":
        sc = skin.scales(u_, w_, cell=CELL, seed=seed)
        return p["k1"] if sc == "edge" else p["k2"]
    d1, d2, cc = skin.voronoi(math.floor(u_) + 0.5, math.floor(w_) + 0.5, CELL, seed)
    if side and n in UNDER:
        vc = (cc[3] - c["from"][1]) / max(1, t.h) if f in ("east", "west") else t.rel[1]
        if vc < _line(n, cc[2] if f in ("east", "west") else t.L[2]):
            return belly(u_, w_)
    else:
        vc = t.rel[1] if side else 1.0
    if n in ("thigh", "knee", "arm"):
        base = "k4" if t.rel[1] > 0.35 else "k3"
    else:
        base = "k4" if vc < 0.55 else ("k3" if vc < 0.8 else "k2")
    # a few big round scales on the flank and the thigh, scattered, lit on top
    if f in ("east", "west") and n in ("hips", "torso", "chest", "thigh"):
        e1, e2, tt = skin.voronoi(u_, w_, 9.0, seed + 11)
        if h32(tt[0], tt[1], seed, 4) % 4 == 0 and e1 < 2.6 and 0.3 < vc < 0.85:
            if e1 > 2.0: return p[STEP_DN[base]]
            if w_ - tt[3] > 0.6: return p[STEP_UP[base]]
            return p[base]
    sc = skin.scales(u_, w_, cell=CELL, seed=seed)
    if sc == "edge": return p[STEP_DN[base]]
    if sc == "hi" and base != "k5": return p[STEP_UP[base]] if h32(int(u_), int(w_), seed) % 3 == 0 else p[base]
    return p[base]


def _col(u, w, i):
    return u + i if w > 0 else u - 1 - i


def decals_for(sex):
    p = pal_for(sex)

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        cr = C["cranium"]
        cmap = {"s": p["k1"], "Y": p["eyeY"], "E": p["eyeE"], "e": p["eyee"], "p": p["pupil"], "g": p["glint"],
                "D": p["eyeD"], "d": p["k0"]}
        for f in ("east", "west"):
            u, v, w, h = cr["uv"][f]
            for j, row in enumerate(EYE):
                for k, ch in enumerate(row):
                    if ch == ".": continue
                    i = (abs(w) - 3 - k) if f == "east" else (2 + k)
                    img[v + 3 + j, _col(u, w, i)] = (*cmap[ch], 255)
        sn = C["snout"]
        for f in ("east", "west"):     # the nostril: big and round, high on the deep snout, just under the horn
            u, v, w, h = sn["uv"][f]
            for di, dj in ((1, 4), (2, 4), (1, 5), (2, 5), (3, 5)):
                i0 = di if f == "east" else abs(w) - 1 - di
                img[v + dj, _col(u, w, i0)] = (*p["nost"], 255)
    return dec


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
