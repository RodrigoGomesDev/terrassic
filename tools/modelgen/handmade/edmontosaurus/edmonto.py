"""Edmontosaurus annectens, made by hand from its own study (page "1.9: estudos do Quetzalcoatlus, do Edmontossauro e do
Dakotaraptor", approved by Rodrigo on 06/11/2026). Up to 12 m and 4 to 6 t, the biggest duckbill of the end of the
Cretaceous (Hell Creek and Lance, 68 to 66 Ma).

Drawn at 20 px = 1 m (game scale 0.8). The hadrosaur plumbing (a facultative quadruped: walks on four, runs on two)
is shared with the Parasaurolophus; the animal is not, and every proportion here is its own:
- the HEAD: long and low, the longest of the duckbills (about 1.2 m), with NO bony crest; the bill very broad, flat
  and spatulate, much wider than the snout behind it; the face long between the eye and the bill, with the wide
  circumnarial depression round the nostril (an inflatable nasal sac in life, Hopson 1975: the sac_l / sac_r bones,
  hidden inside the snout, swell out in the bellow);
- the COMB: a fleshy cock's comb on top of the head (E. regalis, Bell et al. 2014), here on the grown males only
  (bone adult_comb under male_display: hidden on females and on the young);
- the back LOWER than a lambeosaur's (shorter neural spines): the hips the highest point but the line gentle; the
  body long and heavy, the neck thick, the tail deep and stiff;
- the skin of the "mummies" (AMNH 5060, Dakota): small even pebbly scales and a low SEGMENTED FRILL of skin along the
  middle of the back and the top of the tail (the frill cubes, a row of separate plates);
- the hands of the mummies: the fingers bound in a hoof-like mitten.

The colour ("areia quente", docs/CORES.md): a warm sand coat crossed by soft dark-brown saddles over the back that
fade down the flank, the belly pale; the frill a shade darker; the male's comb a muted rust. The female a little
greyer, her saddles fainter.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 20
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# ------------------------------------------------------------------ palette
PAL_M = {
    "r0": "5a4a34", "r1": "7a6448", "r2": "9a8462", "r3": "b49e7a", "r4": "c8b48e", "r5": "dccaa6",   # warm sand
    "c0": "bcae90", "c1": "d2c6aa", "c2": "e4dabf", "c3": "f2ebd6",                                  # pale belly
    "k0": "5a4632", "k1": "6e5840", "k2": "84704e",                                                  # the saddles
    "b0": "1e1a16", "b1": "302a24", "b2": "4a423a", "b3": "6a6056",                                  # the bill
    "h0": "2c2620", "h1": "4a4038", "h2": "6e6254",                                                  # hoof nails
    "cr0": "4a2418", "cr1": "6a3424", "cr2": "8a4a34", "cr3": "a8603e",                              # the comb
    "s0": "6e4a3a", "s1": "8e6450",                                                                  # the nasal sac
}
PAL_F = dict(PAL_M)
PAL_F.update({     # the female: a greyer sand, the saddles fainter
    "r0": "564a3a", "r1": "746652", "r2": "92846c", "r3": "ac9e84", "r4": "c2b49a", "r5": "d6caae",
    "k0": "625444", "k1": "746452", "k2": "887862",
    "s0": "6a5a4a", "s1": "84725e",
})
EYE = {"eD": "120d0e", "eY": "a8823e", "eE": "74502a", "ee": "4a321a", "pupil": "0c0a0a", "glint": "f0e6cc",
       "lid": "d6caa8", "nost": "1a1612"}


def pal_for(sex):
    src = PAL_M if sex == "male" else PAL_F
    p = {k: hx(v) for k, v in src.items()}
    p.update({k: hx(v) for k, v in EYE.items()})
    return p


# ------------------------------------------------------------------ geometry
# Model px at 24 px/m, the hip joint at z = 0, the ground at y = 0 (after _ground), the bill toward -z.
# Signs (geo.rot_matrix): +x lifts what lies in front (-z) and lowers what lies behind (+z); a hanging limb with +x
# swings its far end forward.
REST = {"neck1": 30, "neck2": -20, "skull": -24,
        "thigh": 10, "shin": -26, "foot": 30, "toes": -14,
        "arm": -16, "forearm": 22, "hand": -6,
        "tail1": 5, "tail2": 1, "tail3": 1, "tail4": 0, "tail5": 0, "tail6": 0}


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes}) if c["mat"] not in SADDLE_MATS)
    m.shift(-lo)


def head(m, parent, y, z):
    """skull, the broad bill, cheeks, jaw, the nasal sacs and the male's comb. (y, z): the occipital joint"""
    sk = m.bone("skull", parent, (0, y, z), (REST["skull"], 0, 0))
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, y + y0, z + z0), (x1, y + y1, z + z1)
    # a low braincase, a long face with the eye at its back, a long snout, the bill flaring wide and flat in front
    m.cube(sk, *B(-4, -5, -9, 4, 4, 1), name="cranium")
    m.cube(sk, *B(-3.5, -5, -16, 3.5, 2, -8), name="face", faces=OUT("south"))
    m.cube(sk, *B(-3, -5, -23, 3, 0, -16), name="snout", faces=OUT("south"))
    m.cube(sk, *B(-4.5, -5.2, -29, 4.5, -2.2, -22), name="bill", mat="beak", faces=OUT("south"))
    m.cube(sk, *B(-3.5, -4, -30, 3.5, -2, -28), name="bill_tip", mat="beak", faces=OUT("south"))
    # the cheeks over the dental batteries, their own bones (they flex out as it chews)
    for side, sx in (("l", 1), ("r", -1)):
        m.bone(f"cheek_{side}", sk, (3.5 * sx, y - 1, z - 11))
        # the pivot on the INNER edge of the sac, so the swelling grows out of the snout (on the outer edge it grew
        # inward and never showed)
        m.bone(f"sac_{side}", sk, (1.4 * sx, y - 2.5, z - 19))
    m.pair("cheek_l", "cheek_r", *B(3.5, -5, -15, 4.5, -1, -6), name="cheek", faces=OUT("west"))
    # the nasal sacs: folded inside the snout over the nostril, they swell out in the bellow (scale on sac_l/r)
    m.pair("sac_l", "sac_r", *B(1.4, -4, -22, 2.4, -1, -16), name="sac", mat="sac")
    # the lower jaw: a long dentary and the dark keratin under the bill
    jaw = m.bone("jaw", sk, (0, y - 4, z - 4))
    m.cube(jaw, *B(-2.5, -8, -16, 2.5, -4, -3), name="dentary")
    m.cube(jaw, *B(-4, -8.1, -28, 4, -5.1, -15), name="predentary", mat="beak", faces=OUT("south"))
    m.cube(jaw, *B(-2.5, -4.9, -15, 2.5, -3.9, -4), name="mouth", mat="mouth", faces=["up"])
    # the comb: a fleshy cock's comb over the eyes, the grown male's only
    md = m.bone("male_display", sk, (0, y + 4, z - 6))
    cb = m.bone("adult_comb", md, (0, y + 4, z - 6))
    # a smooth rounded lobe, not a crown of points: a long low base and a shorter rounded top
    m.cube(cb, *B(-1, 3.9, -12, 1, 6.9, -1), name="comb_base", mat="comb")
    m.cube(cb, *B(-0.5, 6.8, -10, 0.5, 8.8, -3), name="comb_top", mat="comb")
    return sk


def neck(m, body):
    """an S from the shoulders: up and forward at the base, forward and down under the head"""
    n1 = m.bone("neck1", body, (0, 42, -60), (REST["neck1"], 0, 0))
    m.cube(n1, (-8, 33, -78), (8, 51, -57), name="neck1")
    m.cube(n1, (-6, 30, -76), (6, 34, -60), name="throat", mat="belly", faces=OUT("up"))
    m.cube(n1, (-0.5, 51, -76), (0.5, 53, -59), name="frill_n1", mat="frill", faces=["east", "west", "up"])
    n2 = m.bone("neck2", n1, (0, 43, -76), (REST["neck2"], 0, 0))
    m.cube(n2, (-6.5, 36, -92), (6.5, 50, -74), name="neck2")
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
    m.pair("thigh_l", "thigh_r", (3, 28, -10), (15, 60, 10), name="thigh")           # the big drumstick into the hip
    m.pair("thigh_l", "thigh_r", (4, 24, -7), (14, 30, 6), name="knee")
    m.pair("shin_l", "shin_r", (4.5, 9, -5.5), (13.5, 28, 3.5), name="shin")
    m.pair("foot_l", "foot_r", (5.5, 0, -4), (13.5, 10, 3), name="meta")
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
    m.pair("arm_l", "arm_r", (4, 22, -64), (14, 41, -52), name="arm")
    m.pair("forearm_l", "forearm_r", (5.5, 10, -62), (12.5, 25, -55), name="forearm")
    m.pair("hand_l", "hand_r", (7.5, 3, -60.5), (11.5, 12, -56.5), name="hand")      # the long metacarpals
    m.pair("hand_l", "hand_r", (7, 1, -62), (12, 4, -56), name="mitten")
    m.pair("hand_l", "hand_r", (7.5, 0, -62.5), (11.5, 2, -59.5), name="hand_nail", mat="hoof", faces=OUT("south"))
    m.pair("hand_l", "hand_r", (11.5, 5, -56.5), (12.5, 8, -54.5), name="finger5", rot=(0, 0, -22), origin=(11.5, 8, -55.5))


def tail(m, body):
    """deep and flat-sided (tall spines above, long chevrons below), straight, tapering slowly to a point"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 12, 36, 8.5, 35, 61), ("tail2", 34, 58, 7, 39, 59), ("tail3", 56, 78, 5.5, 42, 57),
        ("tail4", 76, 96, 4, 45, 55), ("tail5", 94, 112, 2.5, 47, 53), ("tail6", 110, 126, 1.5, 48.5, 51.5)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        if k < 4:      # the frill goes on along the top of the tail, the plates growing lower
            for q in range(2):
                zq = z0 + 3 + q * 11
                m.cube(b, (-0.5, y1, zq), (0.5, y1 + (3 if k < 2 else 2), zq + 6), name=f"frill_t{k}{q}", mat="frill",
                       faces=["east", "west", "up"])
        parent = b


def build(sex="male", saddle_on=True):
    m = P.Model("edmontosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 50, 0))
    # the trunk: the hips the highest point (the tall spines of a lambeosaurine), the back sloping down to the
    # shoulders, a deep narrow barrel, the chest between the short forelegs
    # the trunk: long and heavy, the hips the highest point but the back line gentle (shorter spines than a
    # lambeosaur's), a deep barrel, the chest between the short forelegs
    m.cube(body, (-10, 34, -14), (10, 61, 15), name="hips")
    m.cube(body, (-6, 60, -11), (6, 63, 12), name="sacrum")
    m.cube(body, (-12, 25, -44), (12, 60, -12), name="torso", rot=(-6, 0, 0), origin=(0, 46, -27))
    m.cube(body, (-10.5, 25, -68), (10.5, 54, -40), name="chest", rot=(-11, 0, 0), origin=(0, 40, -53))
    m.cube(body, (-9.5, 22, -48), (9.5, 26, -12), name="belly", mat="belly")
    # the segmented frill of skin along the middle of the back (the mummies): separate low plates
    for k, (z0, y0, h, rot) in enumerate(((-62, 54, 2, -11), (-54, 56, 2, -11), (-44, 59, 3, -6), (-35, 60, 3, -6),
                                          (-26, 61, 3, -6), (-17, 62, 3, -6), (-7, 63, 3, 0), (2, 63, 3, 0))):
        m.cube(body, (-0.5, y0, z0), (0.5, y0 + h, z0 + 6), name=f"frill_b{k}", mat="frill", faces=["east", "west", "up"],
               rot=(rot, 0, 0), origin=(0, y0, z0))
    neck(m, body)
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the saddle: the traveller's saddle
SADDLE_PAL = {   # its own: cured hide, dark leather, a felt blanket in faded indigo, a hide bedroll, two bladders of water
    "H0": hx("3b2a20"), "H1": hx("5a4130"), "H2": hx("765741"), "H3": hx("92704f"),     # cured hide
    "L0": hx("2a1c14"), "L1": hx("432c1e"), "L2": hx("5e3e28"),                          # dark leather
    "F0": hx("2a3040"), "F1": hx("3a4458"), "F2": hx("b89a5a"),                          # indigo felt, ochre stripe
    "B0": hx("6a5a44"), "B1": hx("8a7658"), "B2": hx("a8926e"),                          # the bedroll
    "W0": hx("6e5230"), "W1": hx("8e6c40"), "C0": hx("5b4a34"), "C1": hx("7f6a4b"),       # bladders, cord
}
SADDLE_MATS = ("hide", "leather", "felt", "roll", "bladder", "cord")


def saddle(m, body):
    """The traveller's saddle (the study): the herd animal that walks far. A felt blanket over the back behind the
    shoulders, a deep leather seat with a high cantle, a rolled hide bedroll strapped across behind the seat (its four
    rows of cargo), a water bladder hanging at each flank, a cord girth and a breast strap. Faces lying on the body are
    left out."""
    sd = m.bone("saddle", body, (0, 59, -27), (-6, 0, 0))
    m.cube(sd, (-13, 59, -42), (13, 60, -12), name="blanket", mat="felt", faces=OUT("down"))
    m.pair(sd, sd, (13, 48, -41), (14, 59, -13), name="blanket_side", mat="felt", faces=OUT("west"))
    m.cube(sd, (-7, 60, -36), (7, 62, -18), name="seat", mat="leather", faces=OUT("down"))
    m.cube(sd, (-7, 62, -20), (7, 66, -17), name="cantle", mat="leather")
    m.cube(sd, (-2, 62, -37), (2, 65, -34), name="pommel", mat="leather")
    m.cube(sd, (-11, 61, -16), (11, 66, -11), name="bedroll", mat="roll")
    m.pair(sd, sd, (6, 60.5, -16.5), (8, 66.5, -10.5), name="roll_strap", mat="cord")
    m.pair(sd, sd, (14, 40, -36), (17, 48, -30), name="bladder", mat="bladder")
    m.pair(sd, sd, (14.5, 48, -34), (15.5, 59, -32), name="bladder_cord", mat="cord", faces=OUT("west"))
    m.pair(sd, sd, (12.5, 24, -27), (13.5, 48, -24), name="girth_side", mat="cord", faces=OUT("west"))
    m.cube(sd, (-12.5, 22, -27), (12.5, 23, -24), name="girth_under", mat="cord", faces=OUT("up"))
    m.pair(sd, sd, (11, 50, -50), (12, 52, -40), name="breast_side", mat="cord", faces=OUT("west"))


def saddle_px(t):
    c = t.cube; mat = c["mat"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "felt":
        if f == "up" and (i in (1, w - 2) or j in (1, h - 2)): return p["F2"]
        return p["F1"] if (i + 2 * j) % 7 else p["F0"]
    if mat == "leather":
        if f == "up" and (i in (0, w - 1) or j in (0, h - 1)): return p["L0"]
        return p["L2"] if f == "up" and (i + j) % 5 else p["L1"]
    if mat == "roll":
        if f in ("east", "west"):
            r = max(abs(i - (w - 1) / 2), abs(j - (h - 1) / 2))
            return p["B0"] if int(r) % 2 else p["B2"]
        return p["B1"] if j < h - 1 else p["B0"]
    if mat == "bladder":
        return p["W1"] if j < h / 2 and f != "down" else p["W0"]
    if mat == "cord":
        return p["C1"] if (i + j) % 3 else p["C0"]
    if f == "up": return p["H3"] if (i * 3 + j) % 11 else p["H2"]
    return p["H0"] if j == h - 1 else p["H1"]


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
SADDLED = {"hips", "sacrum", "torso", "chest", "tail1", "tail2", "tail3", "tail4", "tail5", "neck1", "neck2", "thigh"}


def saddle_mark(n, t, zc, vc, seed):
    """a broad soft saddle every ~26 px along the body, 10 to 13 px wide, from the top of the back down a third of the
    flank, its ends shorter and its lower edge ragged and lighter (k2): soft patches, never stripes"""
    if n not in SADDLED or t.face not in ("east", "west", "up"): return None
    z = t.P[2]
    k = math.floor((z + 9.0) / 26.0)
    off = (z + 9.0) - k * 26.0
    wid = 10.0 + (h32(k, 3) % 4)
    if off > wid: return None
    if t.face == "up": return "k1"
    reach = 0.30 + 0.08 * ((h32(k, 5) % 100) / 100) + 0.05 * math.sin(math.floor(z / 2) * 1.3)
    if off < 1.5 or off > wid - 1.5: reach -= 0.12          # the ends of each saddle shorter: a rounded patch
    if n == "thigh": reach += 0.15
    if vc < 1.0 - reach - 0.12: return None
    return "k2" if vc < 1.0 - reach + 0.06 else "k1"
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
    # the saddles: soft dark-brown bands across the back, fading down the flank (whole scales, wandering edges)
    sad = saddle_mark(n, t, zc, vc, seed)
    if sad:
        sc = skin.scales(u_, w_, cell=CELL, seed=seed)
        return p["k0"] if sc == "edge" else p[sad]
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


def comb_px(t, p):
    """the fleshy comb: lit on top, darker at the base, a crease between the lobes"""
    f = t.face
    if f == "up": return p["cr3"]
    if f == "down": return p["cr0"]
    if t.j == t.h - 1: return p["cr1"]
    return p["cr2"] if (t.i + t.j) % 5 else p["cr1"]


def frill_px(t, p):
    """the plates of the frill: a shade darker than the back, the top edge lit"""
    if t.face == "up": return p["r3"]
    return p["r2"] if t.j == 0 else (p["r1"] if t.j > 1 else p["r2"])


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]
        if mat in SADDLE_MATS: return saddle_px(t)
        if mat == "comb": return comb_px(t, p)
        if mat == "frill": return frill_px(t, p)
        if mat == "sac": return p["s1"] if t.face in ("east", "west", "up") else p["s0"]
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


# the eye: 5 x 4 high at the back of the long face, the pale lower lid of a herd animal; front = toward the bill
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
                    i = (abs(w) - 1 - k) if f == "east" else k
                    img[v + 1 + j, _col(u, w, i)] = (*cmap[ch], 255)
        sn = C["snout"]
        for f in ("east", "west"):
            # the circumnarial depression: a long shallow hollow on the side of the snout (a darker oval), the nostril
            # a slit at its front end
            u, v, w, h = sn["uv"][f]
            for d in range(abs(w) - 1):
                for r in (1, 2, 3):
                    if (r == 1 or r == 3) and d in (0, abs(w) - 2): continue
                    i0 = (abs(w) - 1 - d) if f == "east" else d
                    img[v + r, _col(u, w, i0)] = (*p["r1" if r == 2 else "r2"], 255)
            for d in range(2):
                i0 = (abs(w) - 1 - d) if f == "east" else d
                img[v + 2, _col(u, w, i0)] = (*p["nost"], 255)
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
