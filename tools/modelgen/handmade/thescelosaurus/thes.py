"""Thescelosaurus neglectus v4, "o bicho do mato" (16/11/2026), made by hand from the silhouette Rodrigo chose: variant
A, "tipo ave", of the 1.11 silhouette study (tools/modelgen/handmade/_silhuetas/thescelosaurus.py, `bird`).

Its own study: docs/estudos/15_HERBIVOROS_1_11.md (section Tescelossauro, approved 10/11/2026). It is the first small
ornithopod remade, and it must read apart from the other small bipeds of the game (the Gallimimus, the
Pachycephalosaurus, the Dakotaraptor, the Velociraptor). The silhouette came first, in black, and this model follows
that blocking bone for bone (the same pivots and rest angles, the blocking's metres x BLOCK_PX px):

1. the POSTURE of a ground bird: a SHORT trunk pitched 22 degrees nose-up like a bird's, the neck rising from the
   chest in an S (up, then forward, then the head held level), small arms tucked under the chest;
2. the LEGS: thick drumstick thighs (the femur longer than the tibia, Boyd et al. 2014) over long thin shins and a
   long metatarsus, in a half-stride, three toes with dark nails;
3. the TAIL: straight and stiff (ossified tendons), as long as the rest of the animal, carried as one rod;
4. the HEAD of the padrao v3, drawn from its own anatomy: long and low, a big eye under a bar of bone (the palpebral)
   that gives it a wary look, the cheek plates bulging at the corner of the mouth, a short toothless beak tip and,
   at the tip of the snout, REAL TEETH: three small worn pegs of the premaxilla set in under the lip (the only one of
   the 1.11 four that shows teeth), a predentary under them; big nostrils at the tip (a keen nose, Button & Zanno
   2023). The male's accent is the palpebral bar painted yellow, flush over the eye and along the brow;
5. the SKIN drawn, not generated (proto stamps and drawn body-space marks): "samambaia" (study 15), a dark back broken
   by short dark saddles with rows of small pale spots between them following the ribs (the light of the forest
   floor, as on a fawn or a tapir calf), the flank fern green, a cream-green belly; a pale line from the eye along the
   neck to the shoulder over a dark band from the eye to the corner of the mouth; the tail ringed dark toward the tip
   with a pale FLAG under it (the white tail of the bolt). The calf has the spots bolder on a paler ground. No saddle:
   it is not rideable (study 15, answer of Rodrigo).

Bones the Java looks for: root, body, neck1..3, head, skull, jaw, male_display, female_display, arm/forearm/hand,
thigh/shin/foot/toes, tail1..5 (the parts of DinoPart: head, neck, tail).
"""
import math

import numpy as np
import proto as P
import skin2
from proto import hx, h32

TEX_W = 128
# blocking metres -> model px: the blocking A is 5.04 m long; the animal is 4.0 m (Galton 1974) shown at about 17
# texels per block (skin2.PX_PER_M x a little), so the whole blocking is drawn BLOCK_PX px per blocking metre
REAL_M = 4.0
BLOCK_PX = 14.7
PX_M = BLOCK_PX * 5.04 / REAL_M          # model px per real metre (the density gate reads it)
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# ------------------------------------------------------------------ palette ("samambaia", study 15)
SCHEME = {
    "k0": "1b2414", "k1": "26341f", "k2": "3b4f2e", "k3": "5e7a48", "k4": "708c58", "k5": "86a069",
    "b0": "a3ad84", "b1": "b9c198", "b2": "ccd2aa", "b3": "e0e3c6",
    "y0": "a07a26", "y1": "e0b040",
    "hn0": "1e1c16", "hn1": "3a3528", "hn2": "5a5240",
}
PAL = {
    "iris": hx("e6d672"), "iris2": hx("c4b44a"), "pupil": hx("0b0d08"), "glint": hx("f7f8ea"),
    "tooth": hx("cdc29e"), "tooth2": hx("9e967a"), "gum": hx("5a2e2c"), "mouth": hx("3e2224"),
    "claw0": hx("1e1c16"), "claw1": hx("38342a"),
}
# the female: no yellow brow, the green a touch duller; the calf: a paler ground, the spots bolder
FEMALE = {"y0": "3b4f2e", "y1": "5e7a48"}
CALF = {"k0": "26301c", "k1": "33432a", "k2": "4b613b", "k3": "6b8754", "k4": "7d9962", "k5": "93ac76",
        "y0": "4b613b", "y1": "6b8754"}


def pal_for(sex):
    p = dict(PAL)
    for k, v in SCHEME.items():
        p[k] = hx(v)
    if sex in ("female", "baby"):
        for k, v in FEMALE.items():
            p[k] = hx(v)
    if sex == "baby":
        for k, v in CALF.items():
            p[k] = hx(v)
    return p


# ------------------------------------------------------------------ geometry
# Model px, the blocking's pivots x BLOCK_PX (rounded to half pixels), every chain drawn straight in the rest frame and
# bent by the bone rest angles, as in the blocking (sil.chain): the neck and the tail along the body axis, the legs and
# the arms hanging down. Signs (geo.rot_matrix): +x lifts what lies in front (-z), lowers what lies behind (+z); a
# hanging limb with +x swings its far end forward. The legs and the tail hang from the body here (the blocking hangs
# them from the root): their first angle has the body's 22 taken off. Two angles moved from the blocking (16/11, measured on
# the exported geo): the tail rises 22 degrees instead of 14 and the neck base 52 instead of 50, which takes the
# silhouette off the Pachycephalosaurus (0.625 -> 0.59) and the Corythosaurus v4 (0.623 -> 0.60), the blocking still 0.82.
BODY_TILT = 22
REST = {"body": BODY_TILT, "neck1": 52, "neck2": 0, "neck3": -60, "skull": -12,
        "arm": 14, "forearm": 70, "hand": -30,
        "tail1": -22 - BODY_TILT, "tail2": 0, "tail3": 0, "tail4": 0, "tail5": 0}
# the half-stride of the blocking (left forward, right back): thigh, shin, foot; the toes flat on the ground
LEG_REST = {"l": (32 - BODY_TILT, -70, 52), "r": (10 - BODY_TILT, -55, 58)}
HIP = (4.5, 17.5, 4.5)
KNEE_Y, ANKLE_Y, BALL_Y = 9.5, -0.5, -6.5


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes}) if c["mat"] != "teeth")
    m.shift(-lo)


def head(m, parent):
    """the long low head: braincase with the big eye under the palpebral bar, a long low snout, the toothless beak tip,
    the premaxillary teeth under the snout behind it, cheek plates at the corner of the mouth, the slim jaw with its
    predentary"""
    sk = m.bone("skull", parent, (0, 21.5, -23.5), (REST["skull"], 0, 0))
    m.cube(sk, (-2.5, 18.5, -28.5), (2.5, 24.5, -22.5), name="cranium")
    m.cube(sk, (-2, 19.5, -29.5), (2, 23.5, -27.5), name="face", faces=OUT("south"))
    m.cube(sk, (-1.5, 19.5, -33.5), (1.5, 22.5, -29.5), name="snout", faces=OUT("south"))
    m.cube(sk, (-1, 19.5, -34.5), (1, 21.5, -33.5), name="beak", mat="beak", faces=OUT("south"))
    # the premaxillary teeth: three small pegs in the first four pixels of the snout only, just behind the toothless beak, set in
    # under the lip (the snout's edge overhangs them) so they peep out below it; one cube across the mouth, cut out
    m.cube(sk, (-0.5, 17.5, -33.5), (0.5, 19.5, -29.5), name="teeth", mat="teeth")
    # the palpebral bar over the eye is drawn flush on the braincase (decals and head_tone): yellow in the male
    md = m.bone("male_display", sk, (0, 24.5, -26))
    fd = m.bone("female_display", sk, (0, 24.5, -26))
    # the cheek plates over the corner of the mouth (they flex out as it chews)
    for side, sx in (("l", 1), ("r", -1)):
        m.bone(f"cheek_{side}", sk, (2.0 * sx, 19.5, -28))
    m.pair("cheek_l", "cheek_r", (2, 18, -28.5), (3, 20, -25.5), name="cheek")
    jaw = m.bone("jaw", sk, (0, 19.5, -23.5))
    m.cube(jaw, (-1.5, 17.5, -29.5), (1.5, 19.5, -23.5), name="dentary")
    m.cube(jaw, (-1, 16.5, -33.5), (1, 17.5, -28.5), name="predentary", mat="beak", faces=OUT("south"))
    m.cube(jaw, (-1, 17.5, -28.5), (1, 18.5, -27.5), name="mouth", mat="mouth", faces=["north", "up"])
    return sk


NECKS = ("neck1", "neck2", "neck3")


def neck(m, body):
    """the S: up from the chest (50), on (0), then bent level again (-60); each piece starts inside the one before"""
    n1 = m.bone("neck1", body, (0, 21.5, -11.5), (REST["neck1"], 0, 0))
    m.cube(n1, (-2, 19, -17), (2, 24, -10), name="neck1")
    n2 = m.bone("neck2", n1, (0, 21.5, -16.5), (REST["neck2"], 0, 0))
    m.cube(n2, (-1.5, 19.5, -21), (1.5, 23.5, -16), name="neck2")
    n3 = m.bone("neck3", n2, (0, 21.5, -20.5), (REST["neck3"], 0, 0))
    m.cube(n3, (-1.5, 19.5, -24), (1.5, 23.5, -20), name="neck3")
    hd = m.bone("head", n3, (0, 21.5, -23.5))
    head(m, hd)


def arms(m, body):
    """the small arms tucked under the chest: a short upper arm, the forearm, a five-fingered hand with dark nails"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (4 * sx, 16, -9.5), (REST["arm"], 0, 4 * sx))
        fa = m.bone(f"forearm_{side}", a, (4 * sx, 12.5, -9.5), (REST["forearm"], 0, -4 * sx))
        m.bone(f"hand_{side}", fa, (4 * sx, 9.5, -9.5), (REST["hand"], 0, 0))
    m.pair("arm_l", "arm_r", (3, 12, -10.5), (5, 17, -8.5), name="arm")
    m.pair("forearm_l", "forearm_r", (3.5, 9, -10), (4.5, 13, -9), name="forearm")
    m.pair("hand_l", "hand_r", (3.5, 7.5, -10), (4.5, 9.5, -9), name="hand")
    m.pair("hand_l", "hand_r", (3.5, 6.5, -10), (4.5, 7.5, -9), name="hand_nail", mat="claw")


def legs(m, body):
    """the drumstick thigh (deep, into the hips), a narrower knee, the long thin shin, the long metatarsus and the toes
    (drawn flat, -z, their bone turned back so they lie on the ground) with dark nails"""
    for side, sx in (("l", 1), ("r", -1)):
        a, b, c = LEG_REST[side]
        th = m.bone(f"thigh_{side}", body, (HIP[0] * sx, HIP[1], HIP[2]), (a, 0, 2 * sx))
        sh = m.bone(f"shin_{side}", th, (HIP[0] * sx, KNEE_Y, HIP[2]), (b, 0, -2 * sx))
        ft = m.bone(f"foot_{side}", sh, (HIP[0] * sx, ANKLE_Y, HIP[2]), (c, 0, 0))
        m.bone(f"toes_{side}", ft, (HIP[0] * sx, BALL_Y, HIP[2]), (-(BODY_TILT + a + b + c), 0, 0))
    # the drumstick: wide and deep at the hip, narrowing in two steps to the knee
    m.pair("thigh_l", "thigh_r", (1.5, 16.5, -0.5), (7.5, 20.5, 9.5), name="thigh")
    m.pair("thigh_l", "thigh_r", (2, 12.5, 0.5), (7, 17.5, 8.5), name="thigh_mid")
    m.pair("thigh_l", "thigh_r", (2.5, 9.5, 2), (6.5, 13.5, 7), name="knee")
    m.pair("shin_l", "shin_r", (3.5, -0.5, 3), (5.5, 10.5, 6), name="shin")
    m.pair("foot_l", "foot_r", (3.5, -6.5, 3.5), (5.5, 0.5, 5.5), name="meta")
    m.pair("toes_l", "toes_r", (3, -7.5, 1.5), (6, -6.5, 6.5), name="pes")
    m.pair("toes_l", "toes_r", (3, -7.5, 0.5), (6, -6.5, 1.5), name="nails", mat="claw", faces=OUT("south"))


TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5")
# name, pivot z, z0, z1, half width, y0, y1: the stiff rod, five pieces that taper and overlap, none the size of another
TAIL = (("tail1", 7.5, 6, 16, 3, 17, 24), ("tail2", 16.5, 15, 25, 2, 18, 23), ("tail3", 25.5, 24, 34, 1.5, 18.5, 22.5),
        ("tail4", 34.5, 33, 43, 1, 19, 22), ("tail5", 43.5, 42, 50, 1, 19.5, 21.5))


def tail(m, body):
    parent = body
    for n, pz, z0, z1, hw, y0, y1 in TAIL:
        b = m.bone(n, parent, (0, 20.5, pz), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b


def build(saddle_on=False):
    """saddle_on is kept for the shared tools: the Thescelosaurus has no saddle"""
    m = P.Model("thescelosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 18.5, 4.5), (REST["body"], 0, 0))
    # the short trunk: the deep chest of a bird, the belly, the hips over the thighs
    # (each part narrows toward the belly in an inner cube, so the trunk tapers from the deep breast to the belly)
    m.cube(body, (-4, 15, -13), (4, 23, -5), name="chest")
    m.cube(body, (-3, 12, -12), (3, 15, -6), name="keel")
    m.cube(body, (-4.5, 16, -6), (4.5, 24, 2), name="torso")
    m.cube(body, (-3.5, 13, -7), (3.5, 16, 1), name="belly")
    m.cube(body, (-4, 17, 1), (4, 24, 9), name="hips")
    m.cube(body, (-3, 15, 0), (3, 17, 6), name="loin")
    neck(m, body)
    arms(m, body); legs(m, body); tail(m, body)
    _ground(m)
    return m


def preview_faces(m):
    """previews only: swap east/west on cubes that drop one of them, so the preview shows the face the game shows"""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m


# ------------------------------------------------------------------ the skin: DRAWN
TRUNK = {"chest", "torso", "hips", "keel", "belly", "loin"}
NECK = set(NECKS)
TAILN = set(TAILS)
HEAD = {"cranium", "face", "snout", "cheek", "dentary"}

# the trunk and the tail are drawn in each part's own straight frame (t.L: the rest frame before the bones bend it), so
# the marks run on from chest to hips and along the rod of the tail
TRUNK_Y = (13.0, 24.0)
# the dark saddles across the back: z centres (body frame), half width; each is broken in two by a gap on the spine
SADDLES = (-10.5, -3.0, 4.5)
# the rows of pale spots between the saddles follow the ribs: a row is a line slanting down and back
SPOT_ROWS = (-13.5, -6.5, 0.5, 7.5)
TAIL_RINGS = (27.0, 31.5, 36.0, 40.0, 44.0, 47.5)


def _trunk_h(t):
    y0, y1 = TRUNK_Y
    return (t.L[1] - y0) / (y1 - y0)


def _spot(z, y, rows, slope=0.42, every=3.0, calf=False):
    """a small pale spot on a row of spots: the row runs down and back (z = z0 + slope * (top - y)); the spots sit every
    `every` px along it, each one texel (two in the calf), a few missing so the row reads drawn"""
    for k, z0 in enumerate(rows):
        zr = z0 + slope * (TRUNK_Y[1] - y)
        if abs(z - zr) > (0.9 if calf else 0.6):
            continue
        s = (TRUNK_Y[1] - y) / every
        i = math.floor(s)
        if s - i < (0.55 if calf else 0.38) and h32(k, i, 7) % 5 != 0:
            return True
    return False


def trunk_tone(t, calf=False):
    """countershading by the height on the body (the back dark, the flank fern, the belly cream), the broken saddles
    across the back, the rows of pale spots between them"""
    f = t.face; n = t.cube["name"]
    z, y = t.L[2], t.L[1]
    if f == "down":
        return "b2" if (math.floor(z) + math.floor(t.L[0])) % 5 else "b1"
    h = 1.0 if f == "up" else _trunk_h(t)
    if f == "north" and n in ("chest", "keel", "belly"):
        # the breast: cream at the bottom, the fern green rising to the throat
        return "b2" if h < 0.45 else "b0" if h < 0.58 else "k4" if h < 0.8 else "k3"
    hh = h + 0.05 * math.sin(z * 0.5 + 1.1)
    if hh < 0.22:
        return "b2"
    if hh < 0.3:
        return "b0"
    base = "k5" if hh < 0.4 else "k4" if hh < 0.6 else "k3" if hh < 0.78 else "k2"
    # the broken saddles over the back and down the upper flank, darker than the back, ragged at their foot
    if hh > 0.56:
        for k, zc in enumerate(SADDLES):
            half = 1.1 + 0.5 * math.sin(y * 0.9 + k * 2.1)
            foot = 0.6 + 0.08 * math.sin(z * 1.3 + k)
            if abs(z - zc - 0.35 * (TRUNK_Y[1] - y)) < half and hh > foot:
                if f == "up" and abs(t.L[0]) < 0.6 + (k % 2):
                    break                  # broken on the spine
                return "k1"
    # the rows of pale spots on the flank and the back
    if 0.34 < hh and _spot(z, y if f != "up" else TRUNK_Y[1] + 1.5 * abs(t.L[0]), SPOT_ROWS, calf=calf):
        return "b1" if hh < 0.7 else "b0"
    # the fine grain of small scales, one tone deep, on the flank only
    if 0.3 < hh < 0.8 and f in ("east", "west") and skin2.scales(t, cell=2.6, seed=73, flat=0.5) == "edge":
        return skin2.step(base, -1)
    return base


def neck_tone(t):
    """the neck: the back dark, the throat cream; along its side the pale line from the eye to the shoulder"""
    f = t.face
    if f == "up":
        return "k2"
    if f == "down":
        return "b2"
    v = float(t.rel[1])               # 0 the throat side .. 1 the nape
    if f == "north":
        return "b2" if v < 0.7 else "k3"
    if f == "south":
        return "k2"
    if 0.55 < v < 0.78:
        return "b1"                   # the pale line
    if 0.38 < v <= 0.55:
        return "k2"                   # the dark band under it
    return "k3" if v >= 0.78 else ("b2" if v < 0.18 else "k5")


def tail_tone(t, calf=False):
    """the rod: dark above, the fern flank with the spot rows running on, the pale flag underneath (seen in the bolt),
    dark rings toward the tip"""
    f = t.face; n = t.cube["name"]
    z = t.L[2]
    v = float(t.rel[1]) if f in ("east", "west", "north", "south") else (1.0 if f == "up" else 0.0)
    if f == "down":
        return "b3"
    for k, zc in enumerate(TAIL_RINGS):
        half = 0.9 + 0.3 * (k % 2)
        if abs(z - zc + 0.6 * (v - 0.5)) < half:
            return "k1" if v > 0.22 else "b1"
    if v < 0.28 and n in ("tail1", "tail2", "tail3"):
        return "b3" if v < 0.15 else "b2"        # the flag shows on the low flank of the root
    if f == "up":
        return "k2"
    base = "k3" if v > 0.74 else "k4" if v > 0.42 else "k5"
    if n in ("tail1", "tail2") and v > 0.4 and _spot(z - 6.0, 24.0 - (v * 7.0), (2.0, 9.0), slope=0.3, calf=calf):
        return "b0"
    return base


def limb_tone(t, calf=False):
    """legs: the thigh carries the flank's green with spots and a dark seam where it meets the body; the shin, the
    metatarsus and the toes darker, with scutes across the front"""
    n = t.cube["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    v = float(t.rel[1]) if side else (1.0 if f == "up" else 0.0)
    if n in ("thigh", "thigh_mid", "knee"):
        if f == "down":
            return "k2"
        if f == "up":
            return "k2"
        if n == "thigh" and v > 0.88:
            return "k2"
        base = "k4" if v > 0.3 or n != "thigh" else "k3"
        if f == "north":
            base = "k5" if n != "knee" else "k4"
        if f in ("east", "west") and v > 0.15:
            # the flank's rows of spots run on down the thigh, slanting back (every 3 px along a row, rows 4 px apart)
            zz, yy = math.floor(t.L[2]), math.floor(t.L[1])
            if zz % 2 == 0 and (yy + zz // 2) % 3 == 0 and h32(zz, yy, 11) % 4 != 0:
                return "b1"
            # a broken dark saddle over the top of the thigh, the back's pattern carried down
            if n == "thigh" and v > 0.7 and abs(t.L[2] - 4.5 + 0.6 * (t.L[1] - 17.0)) < 1.2 and h32(zz, 5) % 3:
                return "k2"
        return base
    if n in ("arm", "forearm"):
        return "k4" if f not in ("south", "down") else "k3"
    if n == "hand":
        return "k3"
    # shin, metatarsus, toes: darker, a scute seam every 2 px down the front
    if n == "pes":
        return "k2" if f != "up" else "k3"
    base = "k4" if f == "north" else "k3" if f in ("east", "west") else "k2"
    if f in ("north", "up") and math.floor(t.L[1] if f != "up" else t.L[2]) % 3 == 0:
        return "k3" if f == "north" else "k2"
    return base


# ------------------------------------------------------------------ padrão v3: the Thescelosaurus' own head
def head_tone(t, sex):
    """the face: a fine grain of small scales (the study: "escama miúda em grão"), dark above, the fern on the sides,
    cream under the jaw; the dark band from the eye to the corner of the mouth with the pale line over it is drawn
    in the decals"""
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "b1"
    if n == "cranium" and f == "up" and abs(t.L[0]) > 1.5 and -28.5 < t.L[2] < -24.5:
        return "y1" if sex == "male" else "k0"           # the palpebral bar, flush along the brow
    if n == "dentary":
        if f == "up":
            return "k3"
        return "k3" if t.rel[1] < 0.5 else "k4"            # the jaw in the face's green: only the pegs read pale
    if n == "cheek":
        if f == "down" or (f in ("east", "west") and t.j == t.h - 1):
            return "k1"
        return "k4" if (t.i + t.j) % 2 else "k3"
    if f == "up":
        return "k1" if (t.i + 2 * t.j) % 3 else "k2"
    base = "k3" if t.rel[1] < 0.55 else "k2"
    edge = skin2.scales(t, cell=1.6, seed=71, flat=0.7) == "edge"
    return skin2.step(base, -1) if edge else base


def beak_px(t, p):
    f = t.face
    if t.cube["name"] == "predentary":
        return p["hn2"] if f != "down" else p["hn1"]
    if f == "up":
        return p["hn2"]
    if f == "down":
        return p["hn0"]
    return p["hn1"] if t.j < t.h - 1 else p["hn0"]


def teeth_px(t, p):
    """three small pegs of the premaxilla at the tip, front to back 2, 0, 2, 2 texels down (the gaps cut out); the
    lower texel in shadow, so they read half hidden under the lip"""
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2] - t.cube["from"][2]))          # 0 at the front
    length = (2, 0, 2, 2)[min(col, 3)]
    row = int(math.floor(t.cube["to"][1] - t.L[1]))            # 0 at the top (the lip)
    if row >= length:
        return None
    return p["tooth"] if row == 0 else p["tooth2"]


def shader_for(sex):
    p = pal_for(sex)
    calf = sex == "baby"

    def sh(t):
        mat = t.cube["mat"]; n = t.cube["name"]; f = t.face
        if mat == "claw":
            return p["claw1"] if f == "up" else p["claw0"]
        if mat == "beak":
            return beak_px(t, p)
        if mat == "teeth":
            return teeth_px(t, p)
        if mat == "mouth":
            return p["gum"] if f == "up" else p["mouth"]
        if n in TRUNK:
            return p[trunk_tone(t, calf)]
        if n in NECK:
            return p[neck_tone(t)]
        if n in TAILN:
            return p[tail_tone(t, calf)]
        if n in HEAD:
            return p[head_tone(t, sex)]
        return p[limb_tone(t, calf)]
    return sh


# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP. The cranium's side is
# 6 x 6: the big eye at its front under the brow (the brow bar is its own cube above row 0), the dark band from the
# eye down and forward to the corner of the mouth, the pale line over it running back to the neck, the ear behind.
CRANIUM = [
    "BBBBk3",
    "kiik23",
    "ipgIkl",
    "kiIkll",
    "dkkd33",
    "dd3333",
]
# the face (2 x 4) ahead of the eye: the band goes on down to the mouth corner
FACE = [
    "22",
    "33",
    "dd",
    "dd",
]
# the snout (4 x 3): the big nostril at the tip, the lip line
SNOUT = [
    "nn33",
    "n333",
    "3333",
]


def decals_for(sex):
    p = pal_for(sex)
    cm = {"k": p["k0"], "g": p["glint"], "i": p["iris"], "I": p["iris2"], "p": p["pupil"], "n": p["k0"],
          "d": p["k1"], "2": p["k2"], "3": p["k3"], "l": p["b1"], "e": p["k1"],
          "B": p["y1"] if sex == "male" else p["k0"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", CRANIUM, cm, at=(0, 0))
        P.stamp(img, m, C["face"], "east", FACE, cm, at=(0, 0))
        P.stamp(img, m, C["snout"], "east", SNOUT, cm, at=(0, 0))
    return dec


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
