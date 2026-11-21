"""Corythosaurus casuarius v4, "o pavão da mata" (16/11/2026), made by hand from the silhouette Rodrigo chose: variant B,
"leque alto", of the 1.11 silhouette study (tools/modelgen/handmade/_silhuetas/corythosaurus.py, `high_fan`).

Why v4: the v3 of 11/11 was refused ("os modelos tão muito padrão... parece sempre o mais do mesmo"): every remade
duck-bill came out with the same silhouette (a level body, a straight tail, thin legs) and only the head changed. The
silhouette came first this time, in black, and was measured against the other herbivores (sil.py: Dice of the side and
3/4 masks). This model follows that blocking bone for bone (the same pivots and rest angles, in metres x 16.94 px):

1. the POSTURE of a peacock of the forest: the trunk pitched 18 degrees nose-up on long forelegs (the withers far
   above the hips), the neck rising almost upright in three pieces, the small head held level at the top, the tail
   carried high and stiff;
2. the FAN: the helmet drawn as a fan of blades swept back like a cockatoo's crest, far bigger than the bone (study
   14, C: exaggerate what identifies it). Every blade is its own bone (fan0..fan4 under adult_crest), so the display
   opens the fan; the male's two longer blades (male_display: fan_m0, fan_m1) make his fan the bigger one;
3. the SAIL: the tall neural spines of the back drawn as a sail of blades leaning back, from the withers over the
   hips onto the tail;
4. the SKIN drawn, not generated (the thin stripes and the even scales of v3 were part of the "mais do mesmo"):
   azul-fumaça with the back and the sail slate-dark, a pale throat, and the BOLD white bars of the okapi across the
   rump, the thighs and the upper forelegs, drawn as a list of bars below (BARS); the male's fan terracotta with rays
   running out along each blade like cockatoo feathers and a dark keratin tip; the female's slate fan barred across
   in pale; the calf has no fan, only a high brow. A fine scale mosaic stays, one tone deep, under all of it.

Kept from v3: the head of the padrão v3 (the short narrow beak with its straight smooth edge, the big silver-eyed eye
in a ring of pale skin, the cheeks and the jaw), the palette of study 15, the forest saddle, and every bone the Java
looks for (head, skull, jaw, cheek_l/r, adult_crest, male_display, young_crest, saddle, neck*, tail1..4, thigh/shin/
foot/toes, arm/forearm/hand).
"""
import math

import numpy as np
import proto as P
import skin2
from proto import hx, h32

TEX_W = 256
PX_M = skin2.PX_PER_M
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# ------------------------------------------------------------------ palette ("azul-fumaça", study 15)
SCHEME = {
    "k0": "1c2433", "k1": "253247", "k2": "374d6b", "k3": "4e6a94", "k4": "6380aa", "k5": "7a96bb",
    "b0": "a0abbe", "b1": "b4bfd0", "b2": "c8d0de", "b3": "dfe5ee",
    "tc0": "6e2f22", "tc1": "9c432e", "tc2": "b8573a", "tc3": "d4825a", "tc4": "e8b48a",
    "kl0": "17191e", "kl1": "2c2f36", "kl2": "4e5258",
    "bk0": "22252b", "bk1": "3a3f48", "bk2": "565c66", "lip": "8b97a6",
    "female": {"tc0": "2f3a4b", "tc1": "45546b", "tc2": "5c6e88", "tc3": "a9b5c6", "tc4": "c9d1dc"},
}
PAL = {
    "iris": hx("cdd2d6"), "iris2": hx("98a1aa"), "pupil": hx("0b0c0f"), "glint": hx("f6f8fa"),
    "ring": hx("8e9cae"), "ring2": hx("a7b2c0"),
    "mouth": hx("3a2428"), "tongue": hx("7e5058"), "gum": hx("5c3640"),
    "edge": hx("d6d2c4"), "edge2": hx("aaa596"),
    "hoof0": hx("1c1f24"), "hoof1": hx("34383f"), "hoof2": hx("51565e"),
}
# the calf: a paler smoke, the bars as bold (it hides in the undergrowth), no fan colour
CALF = {"k0": "38424f", "k1": "475364", "k2": "5e6e84", "k3": "75879d", "k4": "899aae", "k5": "9dacbf"}


def pal_for(sex):
    p = dict(PAL)
    for k, v in SCHEME.items():
        if k != "female":
            p[k] = hx(v)
    if sex in ("female", "baby"):
        for k, v in SCHEME["female"].items():
            p[k] = hx(v)
    if sex == "baby":
        for k, v in CALF.items():
            p[k] = hx(v)
    return p


# ------------------------------------------------------------------ geometry
# Model px at PX_M (16.94 px per metre: the blocking's metres x 16.94), the hip joint at z = 0, the ground at y = 0
# (after _ground), the beak toward -z. Pivots are the blocking's (high_fan in _silhuetas/corythosaurus.py).
# Signs (geo.rot_matrix): +x lifts what lies in front (-z), lowers what lies behind (+z) and sweeps what stands up
# backward; a hanging limb with +x swings its far end forward.
BODY_TILT = 18
REST = {"body": BODY_TILT, "neck1": 62, "neck2": 8, "neck3": -20, "skull": -61,
        "thigh": -6, "shin": -28, "foot": 30, "toes": -14,
        "arm": -20, "forearm": 4, "hand": 16,
        "tail1": -32, "tail2": -4, "tail3": 0, "tail4": 4}
HIP_Y = 56
HIND_EXT = 0.85
SADDLE_MATS = ("hide", "leather", "bark", "fringe", "cord", "bone")


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes})
             if c["mat"] not in SADDLE_MATS + ("teeth",))
    m.shift(-lo)


# THE FAN, in skull space: blades standing up from a hub over the back of the braincase, each its own bone swept back
# by its rest angle (skull space; the skull is carried 13 degrees nose-up, so the world sweep is 13 more).
# (name, sweep deg, start, length, depth, half width): the front blade short and steep, the middle ones the longest.
FAN = (("fan0", -4, 2, 22, 12, 2.0), ("fan1", 12, 3, 30, 12, 1.5), ("fan2", 27, 3, 34, 12, 2.5),
       ("fan3", 43, 3, 31, 11, 1.5), ("fan4", 60, 2, 23, 10, 2.0))
FAN_MALE = (("fan_m0", 20, 10, 31, 5, 1.0), ("fan_m1", 51, 9, 29, 5, 1.0))
HUB = (0.0, 4.0, -6.0)            # skull space (x, up, along -z from the occiput)


def head(m, parent, y, z):
    """the short narrow skull under the fan, the shallow beak, the cheeks and the jaw. (y, z): the occipital joint"""
    sk = m.bone("skull", parent, (0, y, z), (REST["skull"], 0, 0))

    def B(x0, y0, z0, x1, y1, z1):
        return (x0, y + y0, z + z0), (x1, y + y1, z + z1)
    # the braincase with the big eye at its front, a short face, a NARROW shallow snout
    m.cube(sk, *B(-5, -6, -10, 5, 4, 1), name="cranium")
    m.cube(sk, *B(-4, -5, -15, 4, 2, -9), name="face", faces=OUT("south"))
    m.cube(sk, *B(-2.5, -4.5, -20, 2.5, 0.5, -14), name="snout", faces=OUT("south"))
    # the shallow beak, narrow, its edge straight and smooth (no denticles: a choosy browser)
    m.cube(sk, *B(-3, -5.5, -24, 3, -2.5, -19), name="beak", mat="beak", faces=OUT("south"))
    # the forehead ridge the fan grows from: it rises steep from the snout (the nasals running up into the crest)
    m.cube(sk, *B(-1.5, -1, -18, 1.5, 3, -8), name="brow_keel", mat="helmet", hk=0)
    # THE FAN (adult_crest: the calf has none, only a high brow, young_crest)
    hx_, hy, hz = HUB
    hc = m.bone("adult_crest", sk, (0, y + hy, z + hz))
    m.cube(hc, *B(-2.5, 1, -12, 2.5, 7, 0), name="fan_base", mat="helmet", hk=0)
    for k, (n, sweep, r0, L, d, w) in enumerate(FAN):
        b = m.bone(n, hc, (0, y + hy, z + hz), (sweep, 0, 0))
        m.cube(b, *B(-w, hy + r0, hz - d / 2 - 1, w, hy + r0 + L, hz + d / 2 - 1), name=n, mat="helmet", hk=k + 1,
               blade=(sweep, r0, L))
    md = m.bone("male_display", hc, (0, y + hy, z + hz))
    for k, (n, sweep, r0, L, d, w) in enumerate(FAN_MALE):
        b = m.bone(n, md, (0, y + hy, z + hz), (sweep, 0, 0))
        m.cube(b, *B(-w, hy + r0, hz - d / 2 - 1, w, hy + r0 + L, hz + d / 2 - 1), name=n, mat="helmet", hk=6 + k,
               blade=(sweep, r0, L))
    yc = m.bone("young_crest", sk, (0, y + 2, z - 7))
    m.cube(yc, *B(-3, 1, -13, 3, 6, -1), name="young_brow", mat="helmet", hk=0)
    # the cheeks over the dental batteries (they flex out as it chews)
    for side, sx in (("l", 1), ("r", -1)):
        m.bone(f"cheek_{side}", sk, (3 * sx, y - 1, z - 8))
    m.pair("cheek_l", "cheek_r", *B(4, -5, -14, 5, -2, -10), name="cheek", faces=OUT("west"))
    # the lower jaw: a slim dentary and the predentary under the beak
    jaw = m.bone("jaw", sk, (0, y - 4, z - 3))
    m.cube(jaw, *B(-3, -8, -14, 3, -5, -2), name="dentary")
    m.cube(jaw, *B(-3, -8, -24, 3, -5, -14), name="predentary", mat="beak", faces=OUT("south"))
    m.cube(jaw, *B(-2.5, -5.9, -21, 2.5, -4.9, -3), name="mouth", mat="mouth", faces=["up"])
    m.pair(sk, sk, *B(3.25, -6.5, -24, 3.25, -5.5, -17), name="beak_edge", mat="teeth")
    return sk


NECKS = ("neck1", "neck2", "neck3")


def neck(m, body):
    """three pieces rising almost upright (62 + 8 - 20 on the 18 of the body), each starting inside the one before; a
    low dark ridge runs up its back from the sail, the throat pale and smooth"""
    n1 = m.bone("neck1", body, (0, 61, -49), (REST["neck1"], 0, 0))
    m.cube(n1, (-7, 54, -66), (7, 68, -45), name="neck1")
    m.cube(n1, (-4.5, 51, -63), (4.5, 55, -47), name="throat", mat="belly", faces=OUT("up"))
    m.cube(n1, (-2, 67, -64), (2, 70, -47), name="ridge_neck", mat="sail")
    n2 = m.bone("neck2", n1, (0, 61, -64), (REST["neck2"], 0, 0))
    m.cube(n2, (-6, 55, -81), (6, 67, -62), name="neck2")
    m.cube(n2, (-4, 52.5, -79), (4, 56.5, -63), name="throat2", mat="belly", faces=OUT("up"))
    m.cube(n2, (-1.5, 66, -79), (1.5, 68, -63), name="ridge_neck2", mat="sail")
    n3 = m.bone("neck3", n2, (0, 61, -79), (REST["neck3"], 0, 0))
    m.cube(n3, (-4, 56, -88), (4, 66, -77), name="neck3")
    m.cube(n3, (-3, 54, -87), (3, 57, -79), name="throat3", mat="belly", faces=OUT("up"))
    hd = m.bone("head", n3, (0, 61, -88))
    head(m, hd, 61, -88)


def hind_legs(m, body):
    """long legs (the blocking's 3.25 m): a deep drumstick thigh, a long shin, a slanting metatarsus, three toes with
    hoof-like nails"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (9 * sx, 53, 0), (REST["thigh"], 0, 2 * sx))
        sh = m.bone(f"shin_{side}", th, (9.5 * sx, 29, 0), (REST["shin"], 0, -2 * sx))
        ft = m.bone(f"foot_{side}", sh, (9.5 * sx, 7, 0), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (9.5 * sx, -2, -0.5), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (4, 27, -8), (14, 60, 8), name="thigh")
    m.pair("thigh_l", "thigh_r", (5, 23, -5.5), (14, 30, 4.5), name="knee")
    m.pair("shin_l", "shin_r", (6, 6, -4), (13, 27, 4), name="shin")
    m.pair("foot_l", "foot_r", (6.5, -2, -3), (12.5, 8, 2), name="meta")
    m.pair("toes_l", "toes_r", (6, -3.5, -7), (13, -1.5, -1), name="pes")
    m.pair("toes_l", "toes_r", (8.5, -4, -9), (10.5, -2, -7), name="nail_mid", mat="hoof", faces=OUT("south"))
    m.pair("toes_l", "toes_r", (10.5, -4, -8), (12.5, -2, -6), name="nail_out", mat="hoof", faces=OUT("south"),
           rot=(0, -12, 0), origin=(11.5, -3, -6.5))
    m.pair("toes_l", "toes_r", (6.5, -4, -8), (8.5, -2, -6), name="nail_in", mat="hoof", faces=OUT("south"),
           rot=(0, 12, 0), origin=(7.5, -3, -6.5))
    # the shin and below a little lower, so the hind feet stand on the same ground as the long forelegs at rest
    lower = {f"{b}_{s}" for b in ("shin", "foot", "toes") for s in ("l", "r")}
    for b in m.bones:
        if b["name"] in lower:
            b["origin"][1] -= HIND_EXT
    for c in m.cubes:
        if c["bone"] in lower:
            c["from"][1] -= HIND_EXT; c["to"][1] -= HIND_EXT; c["origin"][1] -= HIND_EXT


def fore_legs(m, body):
    """the giraffe's forelegs of the blocking (3.7 m): a long upper arm under the high withers, a longer slim forearm,
    the bound metacarpals ending in a hoof-like mitten"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (8.5 * sx, 48, -46), (REST["arm"], 0, 4 * sx))
        fa = m.bone(f"forearm_{side}", a, (8.5 * sx, 21, -46), (REST["forearm"], 0, -6 * sx))
        m.bone(f"hand_{side}", fa, (8.5 * sx, -10, -46), (REST["hand"], 0, 2 * sx))
    m.pair("arm_l", "arm_r", (5, 19, -50), (12, 53, -42), name="arm")
    m.pair("forearm_l", "forearm_r", (6, -11, -49), (11, 22, -43), name="forearm")
    m.pair("hand_l", "hand_r", (6, -15, -48.5), (11, -9, -43.5), name="hand")
    m.pair("hand_l", "hand_r", (5.5, -17, -49), (11.5, -14, -43), name="mitten")
    m.pair("hand_l", "hand_r", (6, -17.5, -50.5), (11, -15.5, -48.5), name="hand_nail", mat="hoof", faces=OUT("south"))


TAILS = ("tail1", "tail2", "tail3", "tail4")


def tail(m, body):
    """carried high (14 degrees up in the world, against the 18 of the body), deep and flat-sided, stiff with ossified
    tendons; four overlapping pieces, none the size of another; the sail runs on along the top of the first two"""
    segs = [  # name, pivot z, z0, z1, half width, y0, y1
        ("tail1", 10, 7, 34, 8, 49, 68), ("tail2", 32, 30, 54, 6, 51.5, 65.5), ("tail3", 52, 50, 73, 4, 54, 63),
        ("tail4", 71, 69, 89, 2.5, 55.5, 61.5)]
    parent = body
    for n, pz, z0, z1, hw, y0, y1 in segs:
        b = m.bone(n, parent, (0, 58.5, pz), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-5, 46, 8), (5, 50, 26), name="tail_muscle", mat="belly")     # the long chevrons under it


# THE SAIL: (bone, z centre, height, lean back deg, half width) blades standing on the back; it starts behind the
# withers (the saddle sits between it and the neck), the tallest over the hips, running down onto the tail
SAIL = (("body", -25, 9, 12, 1.5), ("body", -18, 13, 14, 2.0), ("body", -11, 16, 16, 1.5), ("body", -4, 19, 18, 2.0),
        ("body", 3, 20, 20, 1.5), ("tail1", 11, 19, 22, 2.0), ("tail1", 18, 16, 22, 1.5), ("tail1", 25, 13, 20, 2.0),
        ("tail2", 33, 10, 18, 1.5), ("tail2", 40, 7, 16, 2.0), ("tail2", 47, 5, 14, 1.5))
SAIL_BASE = {"body": 66, "tail1": 66, "tail2": 63.5}


def sail(m):
    for k, (bone, zc, hgt, lean, w) in enumerate(SAIL):
        y0 = SAIL_BASE[bone] - 2
        m.cube(bone, (-w, y0, zc - 3.5), (w, y0 + hgt + 2, zc + 3.5), name=f"sail{k}", mat="sail",
               rot=(-lean, 0, 0), origin=(0, y0, zc), sk=k)


def build(saddle_on=True):
    m = P.Model("corythosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, HIP_Y, 0), (REST["body"], 0, 0))
    # the trunk: deep at the chest, the back pitched up toward the high withers by the body's own tilt
    m.cube(body, (-10, 44, -12), (10, 68, 12), name="hips")
    m.cube(body, (-11, 42, -33), (11, 67, -10), name="torso")
    m.cube(body, (-10, 40, -52), (10, 66, -31), name="chest")
    m.cube(body, (-7, 38, -46), (7, 43, -12), name="belly", mat="belly")
    m.cube(body, (-8, 63, -50), (8, 69, -32), name="withers")
    neck(m, body)
    fore_legs(m, body); hind_legs(m, body); tail(m, body); sail(m)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the saddle: the forest saddle ("sela de mata")
SADDLE_PAL = {   # its own: low and narrow for riding under branches; a pad of beaten bark cloth, dark hide, a bone grip
    "K0": hx("3a3424"), "K1": hx("54492e"), "K2": hx("6e6038"), "K3": hx("4a5434"),
    "H0": hx("2a2420"), "H1": hx("443830"), "H2": hx("5e4c40"), "H3": hx("766252"),
    "L0": hx("221a16"), "L1": hx("3a2c22"),
    "F0": hx("4c5a3a"), "F1": hx("66744c"),
    "C0": hx("5e5440"), "C1": hx("7c7056"), "B0": hx("bcb49c"), "B1": hx("dcd6c2"),
}


def saddle(m, body):
    """The forest saddle: a NARROW pad of beaten bark cloth on the withers, between the base of the neck and the first
    blade of the sail, wedged up at the front so the seat stays level on the sloping back, a low hide seat, a bone grip to duck behind, a fringe of dyed strips,
    a cord girth behind the forelegs. Faces lying on the body are left out."""
    sd = m.bone("saddle", body, (0, 69, -36), (-BODY_TILT, 0, 0))     # tilted back against the body: the seat level
    m.cube(sd, (-7, 69, -43), (7, 70, -29), name="pad", mat="bark", faces=OUT("down"))
    m.cube(sd, (-6, 66, -43), (6, 69, -38), name="wedge", mat="bark", faces=OUT("up", "down"))   # fills under the front
    m.pair(sd, sd, (7, 62, -42), (8, 69, -30), name="pad_side", mat="bark", faces=OUT("west"))
    m.pair(sd, sd, (7.5, 60, -41), (8.5, 62, -31), name="fringe", mat="fringe", faces=OUT("west"))
    m.cube(sd, (-5, 70, -41), (5, 71, -31), name="seat", mat="hide", faces=OUT("down"))
    m.cube(sd, (-4, 71, -32), (4, 73, -30), name="cantle", mat="leather")
    m.cube(sd, (-1, 71, -43), (1, 75, -41), name="grip", mat="bone")
    m.cube(sd, (-1.5, 74, -43.5), (1.5, 75, -40.5), name="grip_top", mat="bone")
    m.pair(sd, sd, (10.5, 40, -38), (11.5, 62, -35), name="girth_side", mat="cord", faces=OUT("west"))
    m.cube(sd, (-11, 39, -38), (11, 40, -35), name="girth_under", mat="cord", faces=OUT("up"))
    # the whole saddle sits up on the withers (their top is at y 69); the girth keeps its place round the chest
    for c in m.cubes:
        if c["bone"] == sd and not c["name"].startswith("girth"):
            c["from"][1] += 2.5; c["to"][1] += 2.5; c["origin"][1] += 2.5


def saddle_px(t):
    c = t.cube; mat = c["mat"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "bark":
        if f == "up" and (i == 1 or i == w - 2):
            return p["K3"]
        if j == h - 1 and f != "up":
            return p["K0"]
        return p["K2"] if h32(i // 3, j, 5) % 4 == 0 else p["K1"]
    if mat == "fringe":
        return p["F1"] if i % 2 == 0 else p["F0"]
    if mat == "cord":
        return p["C1"] if (i + j) % 3 else p["C0"]
    if mat == "bone":
        return p["B1"] if f == "up" or j == 0 else p["B0"]
    if mat == "leather":
        return p["L1"] if j < h - 1 else p["L0"]
    if f == "up":
        return p["H3"] if (i * 3 + j) % 11 else p["H2"]
    return p["H0"] if j == h - 1 else p["H1"]


def preview_faces(m):
    """previews only: swap east/west on cubes that drop one of them, so the preview shows the face the game shows"""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m


# ------------------------------------------------------------------ the skin: DRAWN
TRUNK = {"hips", "torso", "chest", "withers", "neck1", "neck2", "neck3", "tail1", "tail2", "tail3", "tail4"}
UNDER = {"belly", "throat", "throat2", "throat3", "tail_muscle"}
NECK = {"neck1", "neck2", "neck3"}
LEG = {"shin", "meta", "pes", "forearm", "hand", "mitten"}
LIMB = {"thigh", "knee", "arm"}
HEAD = {"cranium", "face", "snout", "cheek", "dentary"}

# THE BARS (the okapi's): bold pale bars drawn across the rump, the base of the tail, the thighs and the upper
# forelegs, in body space relative to the hip joint at rest (z back +, y up +). Each bar is a line y = y0 + slope*z
# from z0 to z1, `thick` texels thick in the middle, tapering to a point at both ends; the wander is a slow drawn
# wave (never per-texel noise). On the trunk they lie across the rump and fade forward before the middle of the back;
# on the legs they run round the limb (they are drawn in the leg's own height).
RUMP_BARS = (   # y0, slope, z0, z1, thick
    (10.0, -0.22, -4, 34, 4.2), (3.5, -0.16, -9, 28, 4.6), (-3.0, -0.10, -10, 20, 4.4), (-9.5, -0.04, -7, 12, 3.6))
THIGH_BARS = (6.0, 12.5, 19.0, 25.0)       # texels up the thigh from its lower end (the knee)
ARM_BARS = (17.0, 22.5, 28.0)               # texels up the upper arm from the elbow


def _bar(z, y, bars, wave=0.6):
    for k, (y0, sl, z0, z1, th) in enumerate(bars):
        if not z0 <= z <= z1:
            continue
        u = (z - z0) / (z1 - z0)
        half = th / 2 * min(1.0, 3.2 * min(u, 1 - u))            # tapering to a point at both ends
        yc = y0 + sl * z + wave * math.sin(z * 0.28 + k * 1.9)
        if abs(y - yc) < half:
            return k
    return None


def body_tone(t, prof, calf=False):
    """the palette key of a body texel: the countershading by the silhouette (the back and the sail slate-dark, the
    flank smoke, the belly misty grey), the okapi bars over the rump, a fine scale mosaic one tone deep"""
    n = t.cube["name"]; f = t.face
    z, y = t.P[2] - HIPW[2], t.P[1] - HIPW[1]
    if n in ("throat", "throat2", "throat3"):
        # the throat: the neck's own smoke a step lighter (no pale plate of its own between the jaw and the chest),
        # crossed by soft folds of skin every few texels (the gular folds that stretch in the call)
        along = t.L[2]
        if f == "down" and math.floor(along + 0.6 * math.sin(t.L[0] * 0.9)) % 4 == 0:
            return "k3"
        return "k5" if f != "down" else "k4"
    if n in NECK:
        if f == "up":
            return "k1"
        if f == "down":
            return "k4"
        # the side of the upright neck: dark along its back edge, smoke, lighter toward the throat (rest -y)
        v = float(t.rel[1])
        base = "k1" if v > 0.82 else "k2" if v > 0.6 else "k3" if v > 0.3 else "k4" if v > 0.14 else "k5"
        return skin2.step(base, -1) if skin2.scales(t, cell=3.2, seed=61, flat=0.45) == "edge" else base
    if f == "down" or n in UNDER:
        h = 0.0 if f == "down" else min(0.18, prof.height(t))
    elif f == "up":
        h = 1.0
    else:
        h = prof.height(t)
    b = skin2.bands(h, z, (0.16, 0.26, 0.50, 0.76), amp=0.04, seed=31)
    if b == 0:
        return "b2" if skin2.scales(t, cell=3.4, seed=33, flat=0.5) == "base" else "b1"
    base = ["b1", "b0", "k4", "k3", "k1"][b]
    if f in ("east", "west", "south") and n in ("hips", "torso", "tail1", "tail2") and b >= 2:
        if _bar(z, y, RUMP_BARS) is not None:
            return "b3" if calf or h < 0.7 else "b2"
    if calf:
        return base
    # the fine polygonal scales (Brown 1916) on the lower flank and the tail, one tone deep, under the drawing
    if (h < 0.62 or n in ("tail2", "tail3", "tail4")) and skin2.scales(t, cell=SCALE_CELL[0], seed=35, flat=SCALE_CELL[1]) == "edge":
        base = skin2.step(base, -1)
    return base


def sail_tone(t):
    """the sail: slate-dark blades, each spine's leading edge a step lighter, the very tip pale"""
    f = t.face
    if f == "up":
        return "b0"
    v = float(t.rel[1])
    if f in ("north",):
        return "k2"
    if v > 0.86 and f in ("east", "west"):
        return "k3"
    if f in ("east", "west") and t.rel[2] < 0.25:
        return "k2"
    return "k1" if (t.j + t.i // 2) % 5 else "k0"


def limb_tone(t, calf=False):
    """legs: darker than the body (the study: "as patas são mais escuras"), the okapi bars round the thigh and the
    upper arm, scutes over the front of the foot"""
    n = t.cube["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    v = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    if n in ("thigh", "knee", "arm"):
        base = "k2" if f in ("south", "down") else "k3"
        if side:
            bars = THIGH_BARS if n == "thigh" else ARM_BARS if n == "arm" else ()
            hpx = (t.L[1] - t.cube["from"][1]) if f != "up" else 99
            for k, b0 in enumerate(bars):
                lean = 1.6 * (t.rel[2] - 0.5) if f in ("east", "west") else 0.0     # the bars slant down to the back
                half = 1.6 if n == "thigh" else 1.2
                if f == "north":
                    half *= 0.6      # thinner at the front, the way an okapi's wrap round the leg
                if abs(hpx - b0 + lean - 0.5 * math.sin(t.P[2] * 0.7 + k)) < half:
                    return "b3" if calf else "b2"
        if not calf and skin2.scales(t, cell=4.0, seed=16, flat=0.3) == "edge":
            base = skin2.step(base, -1)
        return base
    if n in ("shin", "forearm"):
        # the bars run on down the leg, thinner and fading toward the ankle and the wrist
        base = "k2" if f in ("north", "east", "west") else "k1"
        if side and f != "south":
            hpx = t.L[1] - t.cube["from"][1]
            H = t.cube["to"][1] - t.cube["from"][1]
            for k, b0 in enumerate((H - 3.5, H - 8.0, H - 12.5)):
                half = (1.1, 0.8, 0.55)[k] * (0.7 if f == "north" else 1.0)
                lean = 1.2 * (t.rel[2] - 0.5) if f in ("east", "west") else 0.0
                if abs(hpx - b0 + lean) < half:
                    return "b3" if calf else "b1"
        return base
    # the hands and feet darker than the legs, scutes over the front
    base = "k1" if f in ("north", "up", "east", "west") else "k0"
    if f in ("north", "up"):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 2
        if k == 0 and (t.i % 3) != 1:
            return "k0"
    return base


# ------------------------------------------------------------------ padrão v3: the Corythosaurus' own head
HL = ["k1", "k2", "k3", "k4", "k5"]


def hstep(key, d):
    return HL[max(0, min(len(HL) - 1, HL.index(key) + d))] if key in HL else skin2.step(key, d)


def head_tone(t, sex):
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "k4"
    if n == "dentary":
        if f == "up":
            return "k3"
        if t.j == 0:
            return "lip"
        return "k4" if t.rel[1] < 0.5 else "k5"
    if n == "cheek":
        if t.j == t.h - 1:
            return "k0"
        if t.j == t.h - 2:
            return "lip"
        return hstep("k3", -1 if skin2.scales(t, cell=1.8, seed=44, flat=0.7) == "edge" else 0)
    if f == "up":
        return hstep("k2", -1 if skin2.scales(t, cell=2.0, seed=41, flat=0.7) == "edge" else 0)
    hv = (t.P[1] - HEAD_Y[0]) / max(1.0, HEAD_Y[1] - HEAD_Y[0])
    base = ["k3", "k3", "k2"][skin2.bands(hv, t.P[2] * 2.0, (0.30, 0.72), amp=0.06, seed=42)]
    if n in ("face", "snout") and f in ("east", "west", "north") and t.j == t.h - 1:
        return "k0"
    if n == "cranium" and f in ("east", "west"):
        dz = t.P[2] - EYE[0]; dy = t.P[1] - EYE[1]
        if dz * dz / 9.0 + dy * dy / 7.0 < 1.0 and not (abs(dz) < 2.0 and abs(dy) < 1.6):
            return "ring2" if dy < -1.0 else "ring"
    # a dark mask line from the eye back under the fan (it makes the eye read from afar)
    if n == "cranium" and f in ("east", "west") and abs(t.P[1] - EYE[1] + 0.5) < 1.0 and t.P[2] > EYE[0] + 2:
        return "k1"
    k = skin2.scales(t, cell=1.7, seed=43, flat=0.55)
    return hstep(base, -1 if k == "edge" else 0)


def fan_r(t):
    """how far out in the fan a texel lies, 0 at the hub to 1 at the longest tip, measured in the rest pose of the
    whole fan (so the colour runs across the blades as one shape, not blade by blade)"""
    d = math.dist((t.P[1], t.P[2]), (HUBW[1], HUBW[2]))
    return min(1.0, d / max(1.0, HUBW[3]))


FAN_RAMP_M = ((0.34, "tc0"), (0.52, "tc1"), (0.72, "tc2"), (0.88, "tc3"), (9.0, "tc4"))
FAN_RAMP_F = ((0.20, "k2"), (0.40, "tc0"), (0.66, "tc1"), (0.88, "tc2"), (9.0, "tc3"))
FAN_BARS_F = (0.47, 0.62, 0.77)      # the female's pale bars: arcs round the hub, running on across every blade
DARKER = {"k2": "k1", "tc0": "k1", "tc1": "tc0", "tc2": "tc1", "tc3": "tc2", "tc4": "tc3"}


def blade_px(t, p, sex):
    """one blade of the fan, coloured as part of ONE fan: the colour runs out from the hub (slate at the root, then
    terracotta deepening to a pale rim in the male; slate with pale arcs across all the blades in the female). Each
    blade's back edge is a step darker, so the blades read as layers fitted one over the next, never as sticks; a pale
    ray runs along the middle of the male's blades like the shaft of a feather."""
    f = t.face
    r = fan_r(t)
    across = float(t.rel[2])                # 0 front .. 1 back of the blade
    ramp = FAN_RAMP_M if sex == "male" else FAN_RAMP_F
    key = next(k for lim, k in ramp if r < lim)
    if f == "up":
        return p["tc4" if sex == "male" else "tc3"]
    if f == "down":
        return p["k1"]
    if f in ("north", "south"):
        return p[DARKER[key]]
    if sex != "male" and r > 0.3 and any(abs(r - b) < 0.035 for b in FAN_BARS_F):
        return p["tc4"]
    if across > 0.84:
        return p[DARKER[key]]                 # the edge where the next blade lies over it
    if sex == "male" and 0.36 < r < 0.86 and abs(across - 0.45) < 0.1:
        return p["tc3"] if r < 0.6 else p["tc4"]
    return p[key]


def helmet_px(t, p, sex):
    """the fan's base and the forehead ridge: slate plates under a dark keratin keel; in the male the terracotta
    starts here and rises into the blades"""
    n = t.cube["name"]; f = t.face
    if sex == "baby" or n == "young_brow":
        return p[hstep("k3", -1 if skin2.scales(t, cell=2.0, seed=46, flat=0.7) == "edge" else 0)]
    if t.cube.get("blade"):
        return blade_px(t, p, sex)
    if n == "fan_base" and f in ("east", "west"):
        # the root of the fan on the skull: in the male the terracotta starts here (the accent of the head), in the
        # female the slate of her fan
        if t.rel[1] < 0.35:
            return p["k2"]
        edge = skin2.scales(t, cell=2.2, seed=50, flat=0.7) == "edge"
        return p["tc0" if edge else "tc1"]
    if f == "up":
        return p["kl1"] if (t.i + t.j) % 4 else p["kl2"]
    edge = skin2.scales(t, cell=2.2, seed=50, flat=0.7) == "edge"
    return p[hstep("k2", -1 if edge else 0)]


def beak_px(t, p):
    n = t.cube["name"]; f = t.face
    if f == "up":
        return p["bk2"] if (t.i * 2 + t.j) % 5 else p["bk1"]
    if f == "down":
        return p["bk0"]
    if n == "predentary" and t.j == 0:
        return p["bk2"]
    return p["bk1"] if t.j > 0 else p["bk2"]


def beak_edge(t, p):
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2] - t.cube["from"][2]))
    return p["edge2"] if col >= 5 else p["edge"]


def shader_for(sex):
    p = pal_for(sex)
    calf = sex == "baby"

    def sh(t):
        mat = t.cube["mat"]; f = t.face; n = t.cube["name"]
        if mat in SADDLE_MATS:
            return saddle_px(t)
        if mat == "hoof":
            if f == "up":
                return p["hoof2"]
            return p["hoof1"] if t.j < t.h - 1 else p["hoof0"]
        if mat == "helmet":
            return helmet_px(t, p, sex)
        if mat == "beak":
            return beak_px(t, p)
        if mat == "teeth":
            return beak_edge(t, p)
        if mat == "mouth":
            return p["tongue"] if (t.i + t.j) % 4 else p["gum"]
        if mat == "sail":
            return p[sail_tone(t)]
        if n in TRUNK or n in UNDER:
            return p[body_tone(t, PROF[0], calf)]
        if n in LEG or n in LIMB:
            return p[limb_tone(t, calf)]
        if n in HEAD:
            return p[head_tone(t, sex)]
        return p["k3"]
    return sh


PROF = [None]
SCALE_CELL = [5.5, 0.45]
HEAD_Y = [0.0, 1.0]
EYE = [0.0, 0.0]
HIPW = [0.0, 0.0, 0.0]
HUBW = [0.0, 0.0, 0.0, 1.0]

# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP
EYE_ART = [
    ".kkkk.",
    "kiiigk",
    "kippik",
    "kIppIk",
    ".kIIk.",
]
NOSTRIL = [
    "hhh..",
    "nnnh.",
]


def decals_for(sex):
    p = pal_for(sex)
    cm = {"k": p["k0"], "g": p["glint"], "i": p["iris"], "I": p["iris2"], "p": p["pupil"], "n": p["k0"], "h": p["k1"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", EYE_ART, cm, at=(0, 2))
        P.stamp(img, m, C["snout"], "east", NOSTRIL, cm, at=(1, 1))
    return dec


def paint_sex(m, sex="male"):
    import geo
    PROF[0] = skin2.Profile(m, {"hips", "torso", "chest", "withers", "belly", "tail1", "tail2", "tail3", "tail4"})
    mats = geo.bone_mats(m.spec())
    HIPW[:] = [float(v) for v in (mats["body"] @ [*next(b for b in m.bones if b["name"] == "body")["origin"], 1.0])[:3]]
    pts = {c["name"]: q for c, q in geo.cube_points(m.spec())}
    ys = [pts[n][:, 1] for n in ("cranium", "face", "snout")]
    HEAD_Y[:] = [min(a.min() for a in ys), max(a.max() for a in ys)]
    hb = next(b for b in m.bones if b["name"] == "adult_crest")
    hw = mats["adult_crest"] @ [*hb["origin"], 1.0]
    blades = [pts[n] for n, *_ in FAN + FAN_MALE]
    rmax = max(float(np.hypot(q[:, 1] - hw[1], q[:, 2] - hw[2]).max()) for q in blades)
    HUBW[:] = [float(hw[0]), float(hw[1]), float(hw[2]), rmax]
    cr = pts["cranium"]
    # the eye at the front of the braincase (P is the rest pose: the head is pitched, so take the cube's own frame)
    c = next(c for c in m.cubes if c["name"] == "cranium")
    loc = [0.0, c["to"][1] - 4.0, c["from"][2] + 3.0]
    w = mats[c["bone"]] @ [loc[0], loc[1], loc[2], 1.0]
    EYE[:] = [float(w[2]), float(w[1])]
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
