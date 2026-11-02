"""Parasaurolophus walkeri, made by hand from its own study (page "Parassaurolofo: estudo e modelo", 02/11/2026, the
fourth of the six remakes of the 1.5 package). Real size 9.5 m, about 2.5-3 t (Parks 1922; Paul 2010).

Drawn at 24 px = 1 m (game scale 0.667), like the Triceratops: the skull without the crest is about 1 m long and gets
24 px for the duck bill, the eye and the cheeks; the crest adds another 1.6 m of tube.

What makes it itself (each point from the study, none taken from another species of the mod):
- the crest: a long hollow tube of the premaxilla and the nasal bones that leaves the top of the snout, passes over
  the eyes and runs back about a metre past the skull, gently curved, round in section and of nearly even thickness
  (P. walkeri, ROM 768). It is a bone, not a sail: no skin web to the neck (the notch in the back is not proof of one).
  Inside it the nasal passage loops up to the tip and back (Weishampel 1981): the call is made with the BILL SHUT;
- the young have only a low half-dome over the eyes (RAM 14000, Farke et al. 2013): the crest is its own bone
  (adult_crest, hidden on babies) and the dome another (young_crest, shown only on babies);
- the hadrosaur plan: a facultative quadruped. The forelimb is half the hind limb, slender, with long bound
  metacarpals ending in a hoof-like mitten of the three middle fingers and a small free fifth finger (no thumb); so on
  four legs the back slopes DOWN from the high hips (the tall neural spines) to the shoulders and the head is carried
  low. It walks on four and runs on two;
- the duck bill: broad, flat, toothless keratin at the front, wider than the snout behind it; the cheeks hold the
  dental batteries and flex out as the jaw closes (pleurokinesis, Norman & Weishampel 1985): the cheek pieces are their
  own bones (cheek_l / cheek_r);
- the tail deep and flat-sided (tall spines above, long chevrons below), held straight out: a lattice of ossified
  tendons stiffens the back, the hips and the tail root, so it bends at the root and swings as a beam;
- three broad hind toes with hoof-like nails, the hind foot a short broad pad.

The colour ("ruivo de impala", its own in docs/CORES.md): a chestnut back over fawn-rufous flanks, cream belly and
throat, and the alarm flag of a herd animal that lives by running (the impala's): a black stripe down the back of each
thigh and along each side of the tail over the cream underside, seen by the herd from behind when one bolts. The male's
crest darkens to near black toward the tip (his display); the female is a greyer fawn, her crest plain.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 24
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# ------------------------------------------------------------------ palette
PAL_M = {
    "r0": "2e1410", "r1": "50200f", "r2": "7a3214", "r3": "a84618", "r4": "c85c22", "r5": "e07a3c",
    "c0": "9f8a6e", "c1": "b6a284", "c2": "d3c4a4", "c3": "e9dfc6",
    "k0": "171113", "k1": "29201e",                                                   # the alarm flag
    "b0": "221e1e", "b1": "37302d", "b2": "524842", "b3": "75695e",                   # the bill (keratin)
    "h0": "302621", "h1": "4f433a", "h2": "786a5c",                                   # hoof nails
    "cr0": "1d1517", "cr1": "34221d", "cr2": "4e2d1f",                                # the male crest toward the tip
}
PAL_F = dict(PAL_M)
PAL_F.update({     # the female: a dusty rose-fawn (cryptic, the nest-sitter), the flag brown, the crest the colour of her head
    "r0": "2d181c", "r1": "4a272c", "r2": "6b3d3e", "r3": "8e5652", "r4": "ad6f63", "r5": "c78c7f",
    "k0": "33231f", "k1": "45322b",
    "cr0": "6b3d3e", "cr1": "7c4948", "cr2": "8e5652",
})
EYE = {"eD": "120d0e", "eY": "b07a3a", "eE": "7d4f24", "ee": "4d3018", "pupil": "0c0a0a", "glint": "f0e6cc",
       "lid": "d9cdb0", "nost": "1a1314"}


def pal_for(sex):
    src = PAL_M if sex == "male" else PAL_F
    p = {k: hx(v) for k, v in src.items()}
    p.update({k: hx(v) for k, v in EYE.items()})
    return p


# ------------------------------------------------------------------ geometry
# Model px at 24 px/m, the hip joint at z = 0, the ground at y = 0 (after _ground), the bill toward -z.
# Signs (geo.rot_matrix): +x lifts what lies in front (-z) and lowers what lies behind (+z); a hanging limb with +x
# swings its far end forward.
REST = {"neck1": 34, "neck2": -22, "skull": -30,
        "thigh": 10, "shin": -26, "foot": 30, "toes": -14,
        "arm": -16, "forearm": 22, "hand": -6,
        "tail1": 5, "tail2": 1, "tail3": 1, "tail4": 0, "tail5": 0, "tail6": 0}


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes}) if c["mat"] not in SADDLE_MATS)
    m.shift(-lo)


# the crest: segments along its own +z (backward), each a child bone bent a little down at the end
CREST = [  # half width, half height, length, bend of this segment (deg; + = the far end down)
    (2.0, 2.5, 9, 0), (2.0, 2.5, 11, 3), (2.0, 2.0, 11, 4), (1.5, 2.0, 10, 6)]
CREST_ROOT = (-8, 0, 0)        # its lean: up and back from the top of the snout


def crest(m, sk, y, z):
    parent = m.bone("adult_crest", sk, (0, y, z), CREST_ROOT)
    zz = z
    for k, (hw, hh, ln, bend) in enumerate(CREST):
        b = parent if k == 0 else m.bone(f"adult_crest{k}", parent, (0, y, zz), (bend, 0, 0))
        m.cube(b, (-hw, y - hh, zz - (1 if k else 0)), (hw, y + hh, zz + ln), name=f"crest{k}", mat="crest", cseg=k)
        zz += ln
    # the rounded tip (the tube closes in a blunt knob)
    m.cube(b, (-1, y - 1, zz), (1, y + 1, zz + 2), name="crest_tip", mat="crest", cseg=4)


def head(m, parent, y, z):
    """skull, bill, cheeks, jaw and crest. (y, z): the occipital joint where the neck meets the skull"""
    sk = m.bone("skull", parent, (0, y, z), (REST["skull"], 0, 0))
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, y + y0, z + z0), (x1, y + y1, z + z1)
    # the braincase and the deep cheek region (the orbit on its side), the face narrowing to the snout
    m.cube(sk, *B(-4, -6, -10, 4, 5, 1), name="cranium")
    m.cube(sk, *B(-3.5, -6, -17, 3.5, 3, -9), name="face", faces=OUT("south"))
    m.cube(sk, *B(-2.5, -6, -23, 2.5, 1, -16), name="snout", faces=OUT("south"))
    # the duck bill: the keratin sheath, broad and flat, flaring wider than the snout behind it
    m.cube(sk, *B(-3.5, -6, -28, 3.5, -2, -22), name="bill", mat="beak", faces=OUT("south"))
    # the cheeks over the dental batteries: their own bones, hinged at the top so they can flex out when it chews
    for side, sx in (("l", 1), ("r", -1)):
        m.bone(f"cheek_{side}", sk, (3.5 * sx, y - 1, z - 12))
    m.pair("cheek_l", "cheek_r", *B(3.5, -6, -16, 4.5, -1, -7), name="cheek", faces=OUT("west"))
    # the lower jaw: the dentary under the cheeks and the predentary (dark keratin) under the bill
    jaw = m.bone("jaw", sk, (0, y - 5, z - 4))
    m.cube(jaw, *B(-3, -9, -17, 3, -5, -3), name="dentary")
    m.cube(jaw, *B(-3, -9, -27, 3, -6, -17), name="predentary", mat="beak", faces=OUT("south"))
    m.cube(jaw, *B(-2.5, -6, -15, 2.5, -5, -4), name="mouth", mat="mouth", faces=["up"])
    # the crest leaves the top of the snout, in front of the eyes (the premaxilla and nasal tube)
    crest(m, sk, y + 2.5, z - 16)
    # the young's crest: a low half-dome over the eyes (Farke et al. 2013), only on babies
    yc = m.bone("young_crest", sk, (0, y + 5, z - 8))
    m.cube(yc, *B(-2.5, 5, -14, 2.5, 7, -4), name="young_dome", mat="crest", cseg=0)
    m.cube(yc, *B(-1.5, 7, -12, 1.5, 8, -6), name="young_top", mat="crest", cseg=0)
    return sk


def neck(m, body):
    """an S from the shoulders: up and forward at the base, forward and down under the head"""
    n1 = m.bone("neck1", body, (0, 42, -60), (REST["neck1"], 0, 0))
    m.cube(n1, (-7, 34, -78), (7, 50, -57), name="neck1")
    m.cube(n1, (-5, 31, -76), (5, 35, -60), name="throat", mat="belly", faces=OUT("up"))
    n2 = m.bone("neck2", n1, (0, 43, -76), (REST["neck2"], 0, 0))
    m.cube(n2, (-5.5, 37, -92), (5.5, 49, -74), name="neck2")
    hd = m.bone("head", n2, (0, 43, -91))
    head(m, hd, 43, -91)


def hind_legs(m, body):
    """the walker's leg of a big ornithopod: a long straight femur deep in the thigh muscle, the knee a little bent,
    a shin as long, a short metatarsus and three broad toes ending in hoof-like nails (no claws)"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (9 * sx, 52, 0), (REST["thigh"], 0, 2 * sx))
        sh = m.bone(f"shin_{side}", th, (9.5 * sx, 29, 0), (REST["shin"], 0, -2 * sx))
        ft = m.bone(f"foot_{side}", sh, (9.5 * sx, 9, 0), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (9.5 * sx, 1, -1), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (4, 30, -9), (14, 60, 9), name="thigh")           # the big drumstick into the hip
    m.pair("thigh_l", "thigh_r", (5, 26, -6), (13, 31, 5), name="knee")
    m.pair("shin_l", "shin_r", (5.5, 9, -5), (12.5, 28, 3), name="shin")
    m.pair("foot_l", "foot_r", (6.5, 0, -3.5), (12.5, 10, 2.5), name="meta")
    # the toes: a broad pad of three, the middle the longest, each with its hoof nail
    m.pair("toes_l", "toes_r", (6, 0, -8), (13, 2, -1), name="pes")
    m.pair("toes_l", "toes_r", (8.5, -1, -11), (10.5, 1, -7), name="nail_mid", mat="hoof", faces=OUT("south"))
    m.pair("toes_l", "toes_r", (11, -1, -9.5), (13, 1, -6.5), name="nail_out", mat="hoof", faces=OUT("south"),
           rot=(0, -12, 0), origin=(12, 0, -7))
    m.pair("toes_l", "toes_r", (6, -1, -9.5), (8, 1, -6.5), name="nail_in", mat="hoof", faces=OUT("south"),
           rot=(0, 12, 0), origin=(7, 0, -7))


def fore_legs(m, body):
    """half as long as the hind leg and slender: the upper arm slants back from the shoulder, the long forearm comes
    forward, the long bound metacarpals end in a hoof-like mitten of the three middle fingers (the hands of the
    Edmontosaurus mummies); the small fifth finger stands free behind it; no thumb"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (9 * sx, 37, -58), (REST["arm"], 0, 6 * sx))
        fa = m.bone(f"forearm_{side}", a, (9.5 * sx, 24, -58), (REST["forearm"], 0, -8 * sx))
        m.bone(f"hand_{side}", fa, (9.5 * sx, 11, -58), (REST["hand"], 0, 2 * sx))
    m.pair("arm_l", "arm_r", (5, 22, -63), (13, 41, -53), name="arm")
    m.pair("forearm_l", "forearm_r", (6, 10, -61.5), (12, 25, -55.5), name="forearm")
    m.pair("hand_l", "hand_r", (7.5, 3, -60.5), (11.5, 12, -56.5), name="hand")      # the long metacarpals
    m.pair("hand_l", "hand_r", (7, 1, -62), (12, 4, -56), name="mitten")
    m.pair("hand_l", "hand_r", (7.5, 0, -62.5), (11.5, 2, -59.5), name="hand_nail", mat="hoof", faces=OUT("south"))
    m.pair("hand_l", "hand_r", (11.5, 5, -56.5), (12.5, 8, -54.5), name="finger5", rot=(0, 0, -22), origin=(11.5, 8, -55.5))


def tail(m, body):
    """deep and flat-sided (tall spines above, long chevrons below), straight, tapering slowly to a point"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 12, 36, 8, 36, 64), ("tail2", 34, 58, 6.5, 40, 62), ("tail3", 56, 78, 5, 43, 59),
        ("tail4", 76, 96, 3.5, 46, 56), ("tail5", 94, 112, 2.5, 48, 54), ("tail6", 110, 126, 1.5, 49.5, 52.5)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b


def build(sex="male", saddle_on=True):
    m = P.Model("parasaurolophus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 50, 0))
    # the trunk: the hips the highest point (the tall spines of a lambeosaurine), the back sloping down to the
    # shoulders, a deep narrow barrel, the chest between the short forelegs
    m.cube(body, (-9, 34, -14), (9, 64, 15), name="hips")
    m.cube(body, (-5, 63, -11), (5, 66, 12), name="sacrum")                          # the ridge over the hips
    m.cube(body, (-11, 26, -42), (11, 62, -12), name="torso", rot=(-9, 0, 0), origin=(0, 46, -27))
    m.cube(body, (-9.5, 25, -66), (9.5, 53, -40), name="chest", rot=(-15, 0, 0), origin=(0, 40, -53))
    m.cube(body, (-8.5, 23, -46), (8.5, 27, -12), name="belly", mat="belly")
    neck(m, body)
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the saddle: a reed saddle of the floodplain
SADDLE_PAL = {   # its own: woven rush, cured hide, plaited fibre cord and rolled bundles of rush matting (no wood
                 # frame like the Triceratops' cangalha, no felt like the Gallimimus' pad, no metal)
    "R0": hx("4a4a2a"), "R1": hx("67653a"), "R2": hx("85814b"), "R3": hx("a39d61"),     # rush, green-gold when dry
    "H0": hx("3b2a20"), "H1": hx("5a4130"), "H2": hx("765741"), "H3": hx("92704f"),     # cured hide
    "C0": hx("5b4a34"), "C1": hx("7f6a4b"),                                              # plaited cord
    "M0": hx("54502f"), "M1": hx("726c3f"), "M2": hx("948b55"),                          # the rolled mats
}
SADDLE_MATS = ("rush", "hide", "cord", "roll")


def saddle(m, body):
    """A reed saddle, the kind a floodplain people would make: a thick mat of woven rush over a hide pad on the back
    behind the withers (the rider sits where the back is lowest, in front of the high hips); a raised hide seat with a
    rolled rush cantle; two long bundles of rolled rush matting strapped along the flanks (its four rows of cargo,
    rolled up, not baskets); a plaited neck rope in front to hold, no bit; a plaited girth under the belly. Faces lying
    on the body are left out."""
    sd = m.bone("saddle", body, (0, 61, -27), (-9, 0, 0))
    m.cube(sd, (-13, 61, -41), (13, 62, -12), name="hide_pad", mat="hide", faces=OUT("down"))
    m.cube(sd, (-11, 62, -39), (11, 64, -14), name="mat", mat="rush", faces=OUT("down"))
    m.pair(sd, sd, (13, 50, -40), (14, 62, -13), name="mat_side", mat="rush", faces=OUT("east"))
    m.cube(sd, (-6, 64, -33), (6, 66, -19), name="seat", mat="hide", faces=OUT("down"))
    m.cube(sd, (-7, 64, -19), (7, 69, -15), name="cantle", mat="roll", faces=OUT("down"))
    # the rolled mats along the flanks (the cargo) and their straps
    m.pair(sd, sd, (14, 44, -38), (19, 50, -14), name="bundle", mat="roll")
    m.pair(sd, sd, (13.5, 43, -33), (19.5, 51, -31), name="band_f", mat="cord")
    m.pair(sd, sd, (13.5, 43, -22), (19.5, 51, -20), name="band_b", mat="cord")
    # the girth: down the flank behind the bundle, under the belly
    m.pair(sd, sd, (12.5, 24, -28), (13.5, 50, -25), name="girth_side", mat="cord", faces=OUT("east"))
    m.cube(sd, (-12.5, 22, -28), (12.5, 23, -25), name="girth_under", mat="cord", faces=OUT("up"))
    # the neck rope: from the front of the mat round the base of the neck
    m.pair(sd, sd, (11, 56, -48), (12, 58, -40), name="rope_side", mat="cord", faces=OUT("east"))


def saddle_px(t):
    """light from above, the lower edge of each piece one step darker; the rush mat woven in a twill (diagonal steps
    that break every few rows, never a checker), its edges bound with cord"""
    c = t.cube; mat = c["mat"]; n = c["name"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "rush":
        edge = (i == 0 or i == w - 1 or j == 0 or j == h - 1) if f == "up" else (j == h - 1)
        if edge: return p["C0"]
        if f == "down": return p["R0"]
        band = (j // 3) % 2
        k = (i + j + (2 if band else 0)) % 4
        if h32(j // 5, n, 3) % 4 == 0 and k == 1: k = 2                 # a strand now and then broken
        return p[("R3", "R2", "R2", "R1")[k]] if f == "up" else p[("R2", "R1", "R1", "R0")[k]]
    if mat == "hide":
        if f == "up":
            if i == 0 or j == 0 or i == w - 1 or j == h - 1: return p["H1"]
            if n == "seat" and i in (1, w - 2) and j % 2 == 0: return p["C1"]       # the lacing along the seat
            return p["H3"] if (i * 3 + j) % 11 else p["H2"]
        return p["H0"] if j == h - 1 else p["H1"]
    if mat == "roll":
        # a bundle of matting rolled up: the spiral shows on the ends, the wraps run round the length
        if f in ("north", "south"):
            r = max(abs(i - (w - 1) / 2), abs(j - (h - 1) / 2))
            return p["M0"] if int(r) % 2 else p["M2"]
        if f == "up": return p["M2"] if (t.L[2] // 2) % 3 else p["M1"]
        if f == "down": return p["M0"]
        return p["M1"] if j < h - 1 else p["M0"]
    if mat == "cord":
        return p["C1"] if (i + j) % 3 else p["C0"]
    return p["R1"]


# ------------------------------------------------------------------ painting
# The house skin (drawn scales, tone per whole scale, a seam on the shaded side, belly scutes) with its own marks:
# - the hadrosaur skin is a field of small even tubercles (Parks 1922 on ROM 768) with bigger feature scales; here
#   the big scales run as a low row along the mid-line of the back and the tail top, never as dots on the flank;
# - the colour by height: chestnut back, rufous flank, a lighter fawn low on the flank, cream underneath; the borders
#   wander between whole scales;
# - the alarm flag: a black stripe down the back of each thigh and along each side of the tail, right over the cream
#   underside, in whole scales.
TRUNK = {"hips", "sacrum", "torso", "chest", "neck1", "neck2", "tail1", "tail2", "tail3", "tail4", "tail5", "tail6",
         "thigh", "knee", "arm"}
UNDERSIDE = {"belly", "throat"}
LEG = {"shin", "meta", "pes", "forearm", "hand", "finger5", "mitten"}
HEADP = {"cranium", "face", "snout", "cheek", "dentary"}
UNDER = {"chest": 0.30, "torso": 0.20, "hips": 0.16, "neck1": 0.34, "neck2": 0.36, "tail1": 0.26, "tail2": 0.3,
         "tail3": 0.34, "tail4": 0.38, "tail5": 0.4, "tail6": 0.45, "cranium": 0.30, "face": 0.30, "cheek": 0.5,
         "dentary": 1.0}
FLAG = {"tail1": (0.26, 0.40), "tail2": (0.30, 0.44), "tail3": (0.34, 0.48), "tail4": (0.38, 0.52)}
CELL = 3.8
DN = {"r5": "r4", "r4": "r3", "r3": "r2", "r2": "r1", "r1": "r0", "r0": "r0", "c3": "c2", "c2": "c1", "c1": "c0",
      "c0": "c0", "k1": "k0", "k0": "k0"}
UP = {"r0": "r1", "r1": "r2", "r2": "r3", "r3": "r4", "r4": "r5", "r5": "r5", "c0": "c1", "c1": "c2", "c2": "c3", "c3": "c3"}


def _line(n, z):
    return UNDER.get(n, 0.3) + 0.05 * math.sin(z * 0.17 + 0.9) + 0.035 * math.sin(z * 0.41 + 2.3)


def _belly(p, u, w, width=6):
    """the underside: the same small tubercles in cream (hadrosaur bellies had no wide scutes)"""
    sc = skin.scales(u, w, cell=3.2, seed=31)
    return p["c0"] if sc == "edge" else (p["c2"] if sc == "hi" else p["c1"])


def body_px(t, p, sex):
    c = t.cube; n = c["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    u_, w_ = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    if c["mat"] == "hoof":
        if f == "up": return p["h2"]
        return p["h1"] if t.j < t.h - 1 else p["h0"]
    if (f == "down" and n not in LEG and n not in ("thigh", "knee", "arm")) or n in UNDERSIDE:
        if f == "up": return p["r3"]
        if f == "down": return _belly(p, t.L[0], t.L[2])
        return _belly(p, u_, w_)
    if n in LEG:
        # the lower legs: darker, small round scales, a crease across the joints
        low = n in ("meta", "pes", "hand", "finger5", "mitten")
        base = ("r2" if low else "r3") if f in ("east", "west", "north", "up") else ("r1" if low else "r2")
        if n == "shin" and f in ("east", "west") and t.rel[2] > 0.72: base = "r2"
        sc = skin.scales(u_, w_, cell=3.0, seed=seed)
        return p[DN[base]] if sc == "edge" else p[base]
    d1, d2, cc = skin.voronoi(math.floor(u_) + 0.5, math.floor(w_) + 0.5, CELL, seed)
    if f == "up":
        # the mid-line row of bigger, flatter scales along the back and the tail top
        if n in ("hips", "sacrum", "back", "torso", "tail1", "tail2", "tail3", "tail4") and abs(t.L[0]) < 2.6:
            k = math.floor((t.L[2] + 0.37 * h32(math.floor(t.L[2] / 5), seed) % 2) / 5.0)
            j = t.L[2] - k * 5.0
            if j < 0.9: return p["r1"]
            return p["r3"] if abs(t.L[0]) < 1.4 and j < 3.2 else p["r2"]
        sc = skin.scales(u_, w_, cell=CELL, seed=seed)
        base = "r2" if n in ("hips", "sacrum", "back", "torso", "chest", "tail1", "tail2", "neck1") else "r3"
        return p[DN[base]] if sc == "edge" else p[base]
    vc = (cc[3] - c["from"][1]) / max(1, c["to"][1] - c["from"][1]) if f in ("east", "west") else t.rel[1]
    zc = cc[2] if f in ("east", "west") else t.L[0]
    if side and n in UNDER and f != "south":
        if vc < _line(n, zc):
            return _belly(p, u_, w_)
    # the alarm flag along the tail, over the cream
    if f in ("east", "west") and n in FLAG:
        a, b = FLAG[n]
        rel = t.rel[1]
        zz = math.floor(t.L[2] / 3)
        wob = 0.03 * math.sin(zz * 0.9 + seed) + (0.025 if h32(zz, seed, 5) % 3 == 0 else 0.0)
        if a + wob < rel < b - wob * 0.5:
            sc = skin.scales(u_, w_, cell=CELL, seed=seed)
            return p["k0"] if sc == "edge" else p["k1"]
    # the flag down the back of the thigh: the rear third of the drumstick, below the hip line
    if n in ("thigh", "knee") and f in ("east", "west", "south"):
        back = (t.L[2] - c["from"][2]) / (c["to"][2] - c["from"][2])
        edge = 0.80 + 0.05 * math.sin(math.floor(t.L[1] / 3) * 1.1 + seed)
        if (back > edge if f != "south" else abs(t.L[0]) > 8.5 * (1 if t.L[0] > 0 else 1) - 99) and 0.12 < t.rel[1] < 0.8 - 0.08 * math.sin(seed):
            sc = skin.scales(u_, w_, cell=CELL, seed=seed)
            return p["k0"] if sc == "edge" else p["k1"]
    if n in ("thigh", "knee", "arm"):
        base = "r3" if t.rel[1] > 0.4 else "r4"
    elif n in HEADP:
        base = "r3" if vc > 0.62 else "r4"
    else:
        wob = 0.05 * math.sin(zc * 0.19 + seed) + 0.04 * math.sin(zc * 0.53)
        base = "r4" if vc < 0.42 + wob else ("r3" if vc < 0.70 + wob else "r2")
        if n in ("neck1", "neck2") and vc > 0.62 + wob: base = "r2"
    sc = skin.scales(u_, w_, cell=CELL if n not in HEADP else 3.0, seed=seed)
    if sc == "edge": return p[DN[base]]
    if sc == "hi" and base in ("r3", "r4") and f in ("east", "west", "north") and h32(cc[0], cc[1], seed) % 3 == 0:
        return p[UP[base]]
    return p[base]


def crest_px(t, p, sex):
    """the tube: lit along its top, shaded under; the male's darkens to near black toward the tip (segments 2-4),
    the female's stays the colour of her head. A thin seam runs along it where the premaxilla meets the nasal"""
    c = t.cube; f = t.face; k = c.get("cseg", 0)
    if sex == "male":
        tone = ("r3", "r2", "cr2", "cr1", "cr0")[k]
    else:
        tone = ("r3", "r3", "r3", "r3", "r2")[k]
    if c["name"].startswith("young"):
        tone = "r3"
    ramp = {"r3": ("r2", "r3", "r4"), "r2": ("r1", "r2", "r3"), "cr2": ("cr1", "cr2", "r2"), "cr1": ("cr0", "cr1", "cr2"),
            "cr0": ("cr0", "cr0", "cr1")}[tone]
    if f == "up": return p[ramp[2]]
    if f == "down": return p[ramp[0]]
    if f in ("east", "west"):
        if t.j == 0: return p[ramp[2]]
        if t.j == t.h - 1: return p[ramp[0]]
        if t.j == 1 and t.h >= 4 and (t.i + k) % 5 == 2: return p[ramp[0]]      # the suture, broken
    return p[ramp[1]]


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]
        if mat in SADDLE_MATS: return saddle_px(t)
        if mat == "crest": return crest_px(t, p, sex)
        if mat == "beak":
            if t.face == "up": return p["b2"] if t.i % 3 else p["b3"]
            if t.face == "down": return p["b0"]
            if t.cube["name"] == "bill" and t.j == t.h - 1: return p["b3"]     # the paler cutting edge
            return p["b1"] if t.j > 0 else p["b2"]
        if mat == "mouth": return hx("5a2e2e")
        return body_px(t, p, sex)
    return sh


def _col(u, w, i):
    """texture column of face-local column i (a face packed as a mirror of its twin runs backwards)"""
    return u + i if w > 0 else u - 1 - i


# the eye: 5 x 4 under the crest's base, high on the cranium's front corner, with the pale lower lid of a herd animal
# (a ring of light skin, as the impala's); front = toward the bill
EYE_ART = [".DDD.",
           "DYgED",
           "DEpeD",
           ".LLL."]


def decals_for(sex):
    p = pal_for(sex)
    cmap = {"D": p["eD"], "Y": p["eY"], "E": p["eE"], "e": p["ee"], "p": p["pupil"], "g": p["glint"], "L": p["lid"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        cr = C["cranium"]
        for f in ("east", "west"):
            u, v, w, h = cr["uv"][f]
            for j, row in enumerate(EYE_ART):
                for k, ch in enumerate(row):
                    if ch == ".": continue
                    i = (abs(w) - 1 - k) if f == "east" else k        # front corner
                    img[v + 2 + j, _col(u, w, i)] = (*cmap[ch], 255)
        sn = C["snout"]
        for f in ("east", "west"):     # the nostril: a long slit low on the snout, behind the bill
            u, v, w, h = sn["uv"][f]
            for d in range(3):
                i0 = (abs(w) - 1 - d) if f == "east" else d
                img[v + 4, _col(u, w, i0)] = (*p["nost"], 255)
    return dec


def _clean(img, m):
    import qa
    qa.clean_orphans(img, m, cutout=(), keep=())


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))


def preview_faces(m):
    """previews only, BEFORE packing: swap east/west on cubes that drop one, so the preview shows what the game shows"""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m
