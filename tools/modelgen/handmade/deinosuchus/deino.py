"""Deinosuchus, made by hand from its own study (page "Deinossuco: estudo para a 1.8", approved by Rodrigo on
05/11/2026: the shape, the "carvão-ouro" colour, the nest dug in the beach sand, and not rideable). An alligatoroid,
not a crocodylid (Brochu 1999; Cossette & Brochu 2020), of the estuaries and coastal swamps on both shores of the
Western Interior Seaway, 82 to 73 million years ago. 12 m in game, the top of the published estimates (Schwimmer 2002).

Drawn at 20 px = 1 m (game scale 0.8): 240 px from the snout to the tail tip, the skull about 1.6 m (32 px).

What makes it itself (each point from the study, none taken from another species of the mod):
- the SNOUT: broad and rounded like an alligator's, the tip SWOLLEN out to the sides behind a narrower waist, and on
  top of the tip, in front of the nostril, the two big pits no other crocodylian has (Cossette & Brochu 2020);
- the eyes and the nostril high on the head, so it floats with only them above the water;
- the teeth: thick holding teeth in front, low blunt crushers at the back (turtle shells with its bites, Schwimmer
  2002); an alligator's overbite, the lower teeth hidden inside the upper jaw with the mouth shut;
- the OSTEODERMS: huge, thick, deeply pitted plates (the genus was named from them, Holland 1909), two rows down the
  back, smaller ones on the flanks, the two rows of the tail crest closing into one toward the tip;
- half the length is tail, tall and flat, the oar; legs short and sprawling to the sides, the hind ones longer; four
  webbed toes behind, five fingers in front.

The colour ("carvão-ouro", docs/CORES.md): charcoal above, the plates a shade darker with their pits marked, broken
gold crossbands on the flanks and the tail (the bands of a young alligator, kept faint in the adult), a gold belly;
the female the same with fainter bands (crocodylians have no colours of sex). A yellow-green eye with a slit pupil.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 20

SCHEMES = {
    "carvao": {
        "k0": "16140f", "k1": "211e18", "k2": "302c24", "k3": "433e33", "k4": "565043", "k5": "6a6352",
        "g0": "5c4e2c", "g1": "7d6a3a", "g2": "9a8148",
        "b0": "a38a4c", "b1": "bb9f5a", "b2": "d0b46a", "b3": "dcc488",
        "band": 1.0,
        "female": {"g0": "4c432c", "g1": "625637", "g2": "7a6a42", "band": 0.45},
    },
}
SCHEME = ["carvao"]

PAL = {
    "eyeY": hx("c6c24e"), "eyeG": hx("9a9a3a"), "pupil": hx("100e0b"), "glint": hx("efe8c8"), "lid": hx("29261f"),
    "nost": hx("0e0d0b"), "tooth": hx("e2d8bc"), "tooth2": hx("bdb193"),
    "gum": hx("c9a878"), "mouth": hx("b48f62"), "tongue": hx("a88258"), "throat": hx("6e5236"),
    "claw": hx("2a241c"), "claw2": hx("463d30"),
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


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes}))
    m.shift(-lo)


OUT = lambda *d: [f for f in P.geo.FACES if f not in d]


def head(m, parent, hy, hz):
    """skull and jaw. (hy, hz): the jaw line at the jaw joint (the back corner of the mouth); the snout runs to -z"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    sk = m.bone("skull", parent, (0, hy + 4, hz))
    # the skull table behind the eyes, wide and flat, then the snout tapering to the waist and the swollen tip
    m.cube(sk, *B(-10, -1, -8, 10, 8, 2), name="cranium")
    m.cube(sk, *B(-8, 0, -16, 8, 6, -7), name="face", faces=OUT("south"))
    m.cube(sk, *B(-7, 0.5, -24, 7, 5.5, -15), name="snout", faces=OUT("south"))
    m.cube(sk, *B(-5, 0, -28, 5, 4, -23), name="waist", faces=OUT("south"))
    m.cube(sk, *B(-9, 0.5, -34, 9, 5.5, -27), name="tip", faces=OUT("south"))      # the swollen tip
    m.cube(sk, *B(-2, 5.5, -33, 2, 6.5, -30), name="nostril_boss")                 # the nostril, high on the tip
    # the eyes: raised orbits on top of the skull table, the eye on their side (it floats with only these out)
    m.pair(sk, sk, *B(3, 8, -8, 8, 11, -3), name="orbit", faces=OUT("down"))
    m.cube(sk, *B(-3, 8, -4, 3, 9, 1), name="table_ridge", faces=OUT("down"))
    # the jaw: hinged at the back, the lower teeth inside the upper jaw (the alligator's overbite)
    jaw = m.bone("jaw", sk, (0, hy, hz + 1))
    m.cube(jaw, *B(-9, -4, -6, 9, 1, 3), name="jaw_back")
    m.cube(jaw, *B(-6.5, -2.5, -16, 6.5, 1.5, -5), name="jaw_mid", faces=OUT("south"))
    m.cube(jaw, *B(-4.5, -3, -26, 4.5, 1, -15), name="jaw_front", faces=OUT("south"))
    m.cube(jaw, *B(-8, -2.5, -33, 8, 1.5, -25), name="jaw_tip", faces=OUT("south"))
    m.cube(jaw, *B(-7, -6, -10, 7, -4, 2), name="throat", mat="belly", faces=OUT("up"))
    return sk


# ------------------------------------------------------------------ the body
# Model px at 20 px/m, the hip joint at z = 0, the ground at y = 0, the snout toward -z. Low: the belly 0.45 m up in
# the high walk, the back about 1.1 m; 1.6 m wide at the trunk.
REST = {"neck": -2, "skull": 2, "tail1": 4, "tail2": 3, "tail3": 2, "tail4": 2, "tail5": 1, "tail6": 1,
        "thigh": 10, "shin": -20, "foot": 10, "arm": 6, "forearm": -14}


def hind_legs(m, body):
    """short and sprawling: the thigh out to the side and down, the shin down to a long four-toed webbed foot"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (13 * sx, 15, -2), (REST["thigh"], 0, 38 * sx))
        sh = m.bone(f"shin_{side}", th, (22 * sx, 12, -2), (REST["shin"], 0, -40 * sx))
        ft = m.bone(f"foot_{side}", sh, (23 * sx, 3, -1), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (23 * sx, 1, -6))
    m.pair("thigh_l", "thigh_r", (10, 11, -6), (24, 19, 3), name="thigh")
    m.pair("shin_l", "shin_r", (19, 2, -5), (26, 13, 1), name="shin")
    m.pair("foot_l", "foot_r", (19, 0, -8), (27, 3, 1), name="foot")
    m.pair("toes_l", "toes_r", (18, 0.5, -13), (28, 1.5, -7), name="web", mat="web")
    for nm, x0 in (("claw_a", 18), ("claw_b", 21), ("claw_c", 24), ("claw_d", 27)):
        m.pair("toes_l", "toes_r", (x0, 0, -15), (x0 + 1, 1, -13), name=nm, mat="claw", faces=OUT("south"))


def fore_legs(m, body):
    """shorter than the hind legs: the upper arm out to the side, the forearm down, a five-fingered hand"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (12 * sx, 15, -58), (REST["arm"], 0, 40 * sx))
        fa = m.bone(f"forearm_{side}", a, (20 * sx, 11, -58), (REST["forearm"], 0, -42 * sx))
        m.bone(f"hand_{side}", fa, (21 * sx, 2, -58))
    m.pair("arm_l", "arm_r", (10, 10, -61), (21, 17, -54), name="arm")
    m.pair("forearm_l", "forearm_r", (18, 2, -61), (24, 12, -55), name="forearm")
    m.pair("hand_l", "hand_r", (17, 0, -65), (25, 2, -56), name="hand")
    for nm, x0 in (("finger_a", 17), ("finger_b", 19), ("finger_c", 21), ("finger_d", 23)):
        m.pair("hand_l", "hand_r", (x0, 0, -67), (x0 + 1, 1, -65), name=nm, mat="claw", faces=OUT("south"))


TAILS = [  # name, z0, z1, half width, y0, y1 (tall and flat: the oar)
    ("tail1", 6, 30, 12, 9, 22), ("tail2", 28, 52, 9, 10, 22), ("tail3", 50, 74, 6, 11, 21),
    ("tail4", 72, 96, 4, 11, 19), ("tail5", 94, 116, 2.5, 12, 18), ("tail6", 114, 134, 1.5, 12.5, 16.5)]


def tail(m, body):
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(TAILS):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        # the crest: two rows of upright scutes, closing to one from the fourth segment
        n_sc = int((z1 - z0) // 4)
        for i in range(n_sc):
            zz = z0 + 1 + i * 4
            h = 2 if k < 3 else 1
            if k < 3:
                xx = max(1, round(hw - 4 - k))
                m.pair(b, b, (xx, y1, zz), (xx + 2, y1 + h, zz + 3), name=f"crest{k}_{i}", mat="osteo",
                       faces=OUT("down"))
            elif hw >= 2:
                m.cube(b, (-1, y1, zz), (1, y1 + h, zz + 3), name=f"crest{k}_{i}", mat="osteo",
                       faces=OUT("down"))
        parent = b


def osteoderms(m, body):
    """the plates: two big rows down the back (thick, pitted), the outer row smaller and staggered; their length,
    width and height vary from plate to plate as on a real back, one missing now and then (an old wound)"""
    z = -60
    i = 0
    while z < 4:
        r = h32("osteo", i)
        ln = 4 + r % 3                                   # 4-6 long
        w = 4 + (r >> 3) % 2 + (1 if -46 < z < -6 else 0)
        h = 2 if -50 < z < -4 and (r >> 5) % 4 else 1
        if (r >> 8) % 11 != 0:                           # a missing plate, rarely
            m.pair(body, body, (2, 23, z), (2 + w, 23 + h, z + ln), name=f"osteo0_{i}", mat="osteo", faces=OUT("down"))
        if -54 < z < 0 and (r >> 12) % 5 != 0:
            off = 2 + (r >> 14) % 2
            m.pair(body, body, (8, 23, z + off), (8 + w - 1, 24, z + off + ln - 1), name=f"osteo1_{i}", mat="osteo",
                   faces=OUT("down"))
        z += ln + 1
        i += 1


def build(sex="male"):
    m = P.Model("deinosuchus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 16, 0))
    # the trunk: a broad flat barrel from the shoulders to the hips, a little wider in the middle
    m.cube(body, (-14, 9, -8), (14, 23, 8), name="hips")
    m.cube(body, (-16, 8, -40), (16, 23, -7), name="trunk")
    m.cube(body, (-14, 9, -64), (14, 22, -39), name="chest")
    m.cube(body, (-13, 7, -60), (13, 9, -6), name="belly", mat="belly", faces=OUT("up"))
    osteoderms(m, body)
    n = m.bone("neck", body, (0, 16, -64), (REST["neck"], 0, 0))
    m.cube(n, (-12, 9, -75), (12, 21, -63), name="neck")
    m.cube(n, (-10, 8, -74), (10, 9, -64), name="neck_belly", mat="belly", faces=OUT("up"))
    for i, z in enumerate((-74, -69)):          # two pairs of neck plates (the nuchal shield)
        m.pair(n, n, (2, 21, z), (6, 23, z + 4), name=f"nuchal_{i}", mat="osteo", faces=OUT("down"))
    hd = m.bone("head", n, (0, 15, -75))
    head(m, hd, 12, -75)
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    _ground(m)
    return m


def preview_faces(m):
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m


# ------------------------------------------------------------------ paint
STEP_DN = {"k5": "k4", "k4": "k3", "k3": "k2", "k2": "k1", "k1": "k0", "k0": "k0", "b3": "b2", "b2": "b1", "b1": "b0", "b0": "b0"}
STEP_UP = {"k0": "k1", "k1": "k2", "k2": "k3", "k3": "k4", "k4": "k5", "k5": "k5"}
TRUNK = {"hips", "trunk", "chest", "neck", "tail1", "tail2", "tail3", "tail4", "tail5", "tail6", "thigh", "arm"}
LEG = {"shin", "foot", "forearm", "hand"}
BELLY_LINE = {"hips": 0.28, "trunk": 0.3, "chest": 0.3, "neck": 0.32, "tail1": 0.3, "tail2": 0.32, "tail3": 0.34,
              "tail4": 0.36, "tail5": 0.4, "tail6": 0.4}


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        c = t.cube; mat = c["mat"]
        if mat == "osteo": return osteo_px(t, p)
        if mat == "claw": return p["claw"] if t.face != "up" else p["claw2"]
        if mat == "web": return p["k2"] if t.face == "up" else p["k1"]
        if mat == "mouth": return mouth_px(t, p)
        if mat == "belly": return belly_px(t, p)
        if c["name"] in TRUNK or c["name"] in LEG: return body_px(t, p)
        return head_px(t, p)
    return sh


def osteo_px(t, p):
    """a thick plate: lit top with a deep pit in the middle (one dark texel, off-centre), dark sides"""
    f = t.face
    if f == "up":
        cx, cz = t.w // 2, t.h // 2
        if (t.i, t.j) == (cx, cz) or (t.w >= 4 and (t.i, t.j) == (cx - 1, cz)): return p["k0"]
        if t.j == 0: return p["k5"]                                   # the lit front edge of the plate
        return p["k4"] if (t.i + t.j) % 3 else p["k3"]
    if f == "down": return p["k0"]
    return p["k1"] if t.j < t.h - 1 else p["k0"]


def mouth_px(t, p):
    """the inside of the mouth, pale as a living alligator's; the teeth along its edge (only seen with it open)"""
    i, j, w, h = t.i, t.j, t.w, t.h
    edge = i in (0, w - 1)
    if edge and (j + (3 if i else 0)) % 3 != 0:
        return p["tooth"] if (j // 3) % 2 == 0 else p["tooth2"]
    if t.cube["name"].startswith("jaw") and abs(i - w / 2) < w * 0.25 and j > h * 0.3: return p["tongue"]
    return p["gum"] if edge or i in (1, w - 2) else p["mouth"]


def belly_px(t, p):
    """the gold belly in square scutes in rows (the crocodylian belly), the throat paler"""
    if t.face == "up": return p["k2"]
    u, v = skin.face_uv_coords(t)
    s = skin.scutes(u, v, row=3, width=4)
    if t.cube["name"] == "throat": return p["b3"] if s == "base" else p["b2"]
    return p[{"seam": "b0", "hi": "b3", "base": "b2"}[s]]


def _band(n, z, x, seed):
    """the broken crossbands of a young alligator, kept in the adult: one every 13-16 px, 3-4 px wide, the edges
    jagged by whole scales, a few broken through"""
    k = (z + 2.5 * math.sin(x * 0.7 + 1.3) + 1.5 * math.sin(x * 1.9)) / 14.5
    band = int(math.floor(k))
    if h32("band", band) % 7 == 0:
        return False                                     # a band missing altogether
    return (k % 1.0) < 0.32 and h32(band, int(z // 2), int(x // 2), seed) % 5 != 0


def body_px(t, p):
    c = t.cube; n = c["name"]; f = t.face
    u_, w_ = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    if n in LEG:
        base = "k2" if f in ("east", "west", "north", "up") else "k1"
        return p[STEP_DN[base]] if skin.scales(u_, w_, cell=2.6, seed=seed) == "edge" else p[base]
    if f == "up":
        # the back between the plates: small square scales, dark, the bands crossing it fainter
        if n.startswith("tail") and _band(n, t.L[2], 0, seed):
            return p["g0"]
        return p["k1"] if (math.floor(u_) + math.floor(w_)) % 3 == 0 else p["k2"]
    if f == "down":
        return belly_px(t, p) if n not in ("thigh", "arm") else p["b1"]
    rel = t.rel[1]
    line = BELLY_LINE.get(n, 0.0) + 0.04 * math.sin(t.L[2] * 0.3)
    if f in ("east", "west") and rel < line and n not in ("thigh", "arm"):
        return belly_px(t, p)
    # flanks and tail: rectangular scales in rows (the side of a crocodylian), lit toward the top
    v = math.floor(w_); row = v // 2
    col = (math.floor(u_) + (row % 2) * 2) // 4
    seam = (v % 2 == 0) or ((math.floor(u_) + (row % 2) * 2) % 4 == 0)
    base = "k3" if rel < 0.7 else "k2"
    if n in ("thigh", "arm"): base = "k3"
    gold = f in ("east", "west") and n not in ("neck",) and _band(n, t.L[2], row, seed) and h32(row, col, seed) % 5 != 0
    if gold and p["band"] < 1.0 and h32(row, col, seed, 3) % 100 > p["band"] * 100: gold = False
    if gold:
        tone = "g2" if rel > 0.55 else "g1"
        return p["g0"] if seam else p[tone]
    return p[STEP_DN[base]] if seam else p[base]


def head_px(t, p):
    """head skin: tight small scales; dark above, the lips and the sides of the jaw lighter toward the belly gold;
    the snout tip with its two pits (decals)"""
    c = t.cube; f = t.face; n = c["name"]
    u, v = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    s = skin.scales(u, v, cell=2.8, seed=seed)
    if n.startswith("jaw"):
        if f == "down": return p["b2"] if s != "edge" else p["b1"]
        if f == "up": return mouth_px(t, p)
        return p["b1"] if t.rel[1] < 0.45 else (p["k3"] if s != "edge" else p["k2"])
    if f == "down": return mouth_px(t, p) if n in ("cranium", "face", "snout", "waist", "tip") else p["k1"]
    if f == "up":
        if n == "cranium" and (math.floor(u) * 3 + math.floor(v) * 5) % 7 == 0: return p["k0"]      # the pitted skull table
        return p["k1"] if s == "edge" else p["k2"]
    k = 3 if t.rel[1] < 0.6 else 2
    if n in ("orbit", "table_ridge", "nostril_boss"): k = 2
    return p[f"k{k - 1}"] if s == "edge" else p[f"k{k}"]


def _col(u, w, i):
    return u + i if w > 0 else u - 1 - i


EYE = ["dddd", "dYpY", "dGpG", ".dd."]


def decals_for(sex):
    p = pal_for(sex)

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        orb = C["orbit"]
        cmap = {"d": p["lid"], "Y": p["eyeY"], "G": p["eyeG"], "p": p["pupil"]}
        for f in ("east",):            # the eye only on the outer side of the raised orbit, a slit pupil (05/11: the inner face showed a second eye)
            if f not in orb["uv"]: continue
            u, v, w, h = orb["uv"][f]
            for j, row in enumerate(EYE[:h]):
                for k, ch in enumerate(row):
                    if ch == "." or k >= abs(w): continue
                    i = (abs(w) - 1 - k) if f == "east" else k
                    img[v + j, _col(u, w, i)] = (*cmap[ch], 255)
        tip = C["tip"]
        u, v, w, h = tip["uv"]["up"]           # the two pits on top of the swollen tip, in front of the nostril
        for (i, j) in ((4, 1), (5, 1), (4, 2), (w - 5, 1), (w - 6, 1), (w - 5, 2)):
            img[v + j, u + i] = (*p["k0"], 255)
        nb = C["nostril_boss"]
        u, v, w, h = nb["uv"]["up"]
        img[v + 1, u + 1] = (*p["nost"], 255); img[v + 1, u + w - 2] = (*p["nost"], 255)
        # the upper teeth showing along the lip with the mouth shut (the overbite): uneven, the big fourth one
        for name, step, off in (("snout", 3, 1), ("face", 4, 2), ("waist", 3, 0), ("tip", 2, 1)):
            cb = C[name]
            for f in ("east", "west"):
                if f not in cb["uv"]: continue
                u, v, w, h = cb["uv"][f]
                i = off
                while i < abs(w):
                    r = h32(name, i, f)
                    if r % 5:
                        img[v + h - 1, _col(u, w, i)] = (*(p["tooth"] if r % 3 else p["tooth2"]), 255)
                        if name in ("tip", "snout") and r % 4 == 1 and h > 2:      # a long holding tooth now and then
                            img[v + h - 2, _col(u, w, i)] = (*p["tooth"], 255)
                    i += step + (r % 3 == 0)
    return dec


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
