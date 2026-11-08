"""Albertosaurus sarcophagus, made by hand from its own study (docs/estudos/13_PREDADORES_1_10.md, approved by Rodrigo
on 07/11/2026). Real size 10 m (the top of the estimates: the Dry Island adult of Erickson et al. 2006, Rodrigo's
answer).

The second rig of the 1.10.1 standard (docs/estudos/14_POR_QUE_PARECE_IA.md, "Decisões do Rodrigo"), the way the
Daspletosaurus pilot set it (art/daspletosaurus/PILOTO.md):
- one texel = one Minecraft pixel: drawn at skin2.PX_PER_M (16.94 px per metre), shown at a model scale of ~1;
- the skin in BODY space (skin2): dark back, middle flank, pale belly as one shape from the snout to the tail tip, a
  calm base with soft blotches, scales only where they belong (the belly scutes, the feet, the rugose nasals) and the
  species' marks DRAWN as shapes;
- the detail stays, standardised.

What makes it read as an albertosaurine and not as the T. rex or the Daspletosaurus (study 13, "Diferente dos
parentes"): the silhouette of a greyhound, not a bull.
- a LONG, LOW skull (Currie 2003): 25 px from the occiput to the snout (1.5 m drawn against ~1.1 m real: the one
  signature shape, exaggerated by a third as in the pilot) but only 11 px tall at the back and 9 wide, tapering to a
  7 px snout: lighter than the tyrannosaurines' (the Daspletosaurus has 15 tall over 26);
- a short TRIANGULAR crest on the lacrimal in front of each eye, rust on the male (a courting crest, Dodson et al.
  1993: a hypothesis), dark on the female;
- LONG LEGS: the tibia and metatarsus longer than in the tyrannosaurines (Currie 2003; Currie et al. 2003), the hips
  at ~3.0 m against the Daspletosaurus' 2.6 m on a body only half a metre longer; long narrow feet; the hallux off
  the ground (Holtz 2004);
- a slim, shallow trunk, minimal arms with two fingers, a long thin tail.

Colour "verde-abeto" (study 13): a dark petrol-green back like the shade of a conifer wood, a cool moss-green flank
with one lighter LATERAL STRIPE from the shoulder to the tail (its first drawn mark), a row of dark paired spots down
the spine (the second) and a dark band from the eye back to the jaw joint (the third); the belly a pale lichen grey.
"""
import math

import head2
import proto as P
import skin
import skin2
from proto import hx, h32

TEX_W = 256
PX_M = skin2.PX_PER_M

# ------------------------------------------------------------------ palette
# k0..k5 the body ramp (hue-shifted: shadows to blue-black, lights to a greyer moss), b0..b3 the lichen belly, s0..s1
# the pale lateral stripe, hr the male's rust crest, hd the female's dark one
SCHEME = {
    "k0": "0f1d17", "k1": "15291f", "k2": "1d3a2c", "k3": "274c3a", "k4": "325d48", "k5": "427058",
    "b0": "587e68", "b1": "6d927c", "b2": "83a691", "b3": "99b9a5",
    "s0": "4f7a61", "s1": "5f8a70",
    "hr0": "6e3d24", "hr1": "9a5430", "hr2": "b8683a",
    "lip": "5e816b", "scar": "8fa892",
    "female": {"k1": "182d23", "k2": "213f31", "k3": "2c513f", "k4": "38634d", "k5": "48765e",
               "b0": "60846e", "b1": "759883", "b2": "8aab97", "s0": "56806a", "s1": "669077",
               "hr0": "1a2b22", "hr1": "25392f", "hr2": "33493d"},
}
PAL = {
    "ker0": hx("1c1a16"), "ker1": hx("34302a"), "ker2": hx("cbc2a2"), "ker3": hx("9a9072"),
    "iris": hx("d8b43a"), "pupil": hx("0e0c0b"), "lid": hx("0c1410"), "glint": hx("f0ead0"),
    "gum": hx("6e3535"), "mouth": hx("351b1d"), "tongue": hx("94504b"), "tooth": hx("ebe2c8"), "tooth2": hx("c0b28e"),
}


def pal_for(sex):
    p = dict(PAL)
    for k, v in SCHEME.items():
        if k != "female":
            p[k] = hx(v)
    if sex != "male":
        for k, v in SCHEME["female"].items():
            p[k] = hx(v)
    return p


# ------------------------------------------------------------------ geometry
def _ground(m):
    import geo
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes})
             if c["mat"] not in ("teeth", "teeth_lo"))
    m.shift(-lo)


SNOUT_ROT = (-3, 0, 0)      # the long snout slopes only a little from the eyes to the tip (low, not deep)


def head(m, parent, hy, hz, rest=(-6, 0, 0)):
    """the long low skull and the slender jaw. (hy, hz): the mouth line at the back of the skull; returns the skull"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    sk = m.bone("skull", parent, (0, hy + 5, hz), rest)
    so = (0, hy + 9, hz - 10)               # the snout hinges at the front of the cranium, at its top
    m.cube(sk, *B(-4.5, 0, -10, 4.5, 11, 0), name="cranium")
    m.cube(sk, *B(-3.5, 3, 0, 3.5, 10, 2), name="occiput")
    m.pair(sk, sk, *B(4.5, 2, -4.5, 5.5, 7, -0.5), name="temporal")      # the jaw muscle, slight (a lighter bite)
    m.cube(sk, *B(-3.5, 0, -23, 3.5, 9, -10), name="snout", rot=SNOUT_ROT, origin=so)
    m.cube(sk, *B(-2.5, 0, -25, 2.5, 7, -23), name="premax", rot=SNOUT_ROT, origin=so)
    m.cube(sk, *B(-1.5, 9, -22, 1.5, 10, -11), name="nasal", mat="plate", rot=SNOUT_ROT, origin=so)   # rugose nasals
    # the short TRIANGULAR lacrimal crest in front of each eye, two tiers narrowing to a point (padrão v2: it grows
    # out of the skull, its base the face's own skin, the display skin above it rust on the male with a keratin
    # point), and the low brow shelf over the eye socket under it
    m.pair(sk, sk, *B(1.5, 10.5, -11, 4.5, 12.5, -5), name="lacrimal", mat="crest_base")
    m.pair(sk, sk, *B(2, 12, -10, 4, 14, -7), name="crest", mat="horn", rot=(-12, 0, 0), origin=(3, hy + 12, hz - 8.5))
    m.pair(sk, sk, *B(3.5, 8, -10.5, 5.5, 10, -4.5), name="brow", mat="brow")
    jaw = m.bone("jaw", sk, (0, hy + 1, hz - 2))
    m.cube(jaw, *B(-4, -4, -10, 4, 0, 0), name="jaw_back")
    m.cube(jaw, *B(-3, -3, -24, 3, 0, -10), name="jaw_front", rot=(-2, 0, 0), origin=(0, hy, hz - 10))
    m.cube(jaw, *B(-3, -6, -12, 3, -4, -3), name="gular", mat="gular")
    m.cube(jaw, *B(-3.5, -1, -7, 3.5, 2, -1), name="cheek", mat="mouth")
    m.cube(jaw, *B(-1.5, -2, -21, 1.5, 1, -6), name="tongue", mat="tongue")
    m.cube(sk, *B(-1, -1, -22, 1, 2, -11), name="palate", mat="mouth")
    # teeth as alpha planes. Padrão v2: the upper row hangs just OUTSIDE the slender jaw (3.25 > 3) under the snout's
    # lip (3.5): with the mouth shut the many slender crowns show, the lips covering their base; the lower row
    # inside the snout
    m.pair(sk, sk, *B(3.25, -2, -23, 3.25, 0, -11), name="teeth_up", mat="teeth", rot=SNOUT_ROT, origin=so)
    m.pair(jaw, jaw, *B(2, -1, -23, 2, 2, -10), name="teeth_lo", mat="teeth_lo")
    return sk


REST = {   # bone rest angles (x: + = far end up for the neck and tail, knee forward for the thigh)
    "neck1": 26, "neck2": 4, "skull": -31, "thigh": 20, "shin": -50, "foot": 42, "toes": -12,
    "arm": 18, "forearm": -70, "tail1": -4, "tail2": 1.5, "tail3": 1, "tail4": 0.5, "tail5": 0,
}
HIP_Y = 52


def legs(m, body):
    """the runner's legs: a slim drumstick, a long shin and a LONG metatarsus (Currie 2003), a long narrow foot of
    three toes wider than the shin, the small first toe held off the ground (Holtz 2004)"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (7 * sx, HIP_Y, 0), (REST["thigh"], 0, 4 * sx))
        sh = m.bone(f"shin_{side}", th, (7 * sx, 33, 0), (REST["shin"], 0, -8 * sx))
        ft = m.bone(f"foot_{side}", sh, (7 * sx, 14, 0), (REST["foot"], 0, 4 * sx))
        m.bone(f"toes_{side}", ft, (7 * sx, -1, 0), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (3, 44, -7.5), (12, 60, 7.5), name="thigh")
    m.pair("thigh_l", "thigh_r", (3.5, 35, -6), (11.5, 45, 5), name="thigh_low")
    m.pair("thigh_l", "thigh_r", (4, 29, -4.5), (11, 36, 3.5), name="knee")
    m.pair("shin_l", "shin_r", (4.5, 20, -4), (10.5, 34, 3), name="calf")
    m.pair("shin_l", "shin_r", (5, 10, -2.5), (10, 21, 2.5), name="shin")
    m.pair("foot_l", "foot_r", (5.5, -2, -2), (9.5, 15, 2), name="meta")
    m.pair("toes_l", "toes_r", (6, -3, -13), (9, 0, 0), name="toe_mid")
    m.pair("toes_l", "toes_r", (9, -3, -10), (11, 0, -1), name="toe_out")
    m.pair("toes_l", "toes_r", (4, -3, -10), (6, 0, -1), name="toe_in")
    m.pair("toes_l", "toes_r", (7, -3, -15), (8, -1, -13), name="claw_mid", mat="claw")
    m.pair("toes_l", "toes_r", (9.5, -3, -12), (10.5, -1, -10), name="claw_out", mat="claw")
    m.pair("toes_l", "toes_r", (4.5, -3, -12), (5.5, -1, -10), name="claw_in", mat="claw")
    m.pair("foot_l", "foot_r", (4.5, 4, 1.5), (6.5, 6, 4.5), name="hallux")


def arms(m, body):
    """minimal arms (Holtz 2004): an upper arm of 6 px, a forearm of 4, two fingers"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (6 * sx, 41, -40), (REST["arm"], 0, -6 * sx))
        m.bone(f"forearm_{side}", a, (6 * sx, 36, -40), (REST["forearm"], 0, 0))
    m.pair("arm_l", "arm_r", (4.5, 35, -41.5), (7.5, 41, -38.5), name="arm")
    m.pair("forearm_l", "forearm_r", (4.5, 32, -41), (7.5, 36, -39), name="forearm")
    m.pair("forearm_l", "forearm_r", (5, 30, -41), (7, 32, -39), name="hand")
    m.pair("forearm_l", "forearm_r", (6, 28, -41), (7, 30, -40), name="claw_f1", mat="claw")
    m.pair("forearm_l", "forearm_r", (5, 28.5, -40), (6, 30.5, -39), name="claw_f2", mat="claw")


TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5")


def tail(m, body):
    """long and thin: a modest root, tapering steadily to a whip of a tip; each segment starts 2 px inside the one
    before and none repeats the size of another (study 14, C)"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 6, 30, 6, 42, 58), ("tail2", 28, 50, 4.5, 45, 56), ("tail3", 48, 66, 3, 47, 54),
        ("tail4", 64, 78, 2, 48, 53), ("tail5", 76, 88, 1, 49, 52)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-4, 39, 4), (4, 43, 22), name="tail_muscle")


SADDLE_PAL = {   # light tan leather and bone: the racing saddle (its own: small and light, for the fastest tyrant)
    "L0": hx("2c2116"), "L1": hx("4a3826"), "L2": hx("6a5236"), "L3": hx("866a46"), "L4": hx("a08456"),
    "F0": hx("4d5a4c"), "F1": hx("66745f"), "F2": hx("7f8c74"),
    "I0": hx("4a4a48"), "I1": hx("787874"), "I2": hx("a4a49c"), "B0": hx("b9aa88"), "B1": hx("ddd0b0"),
}


def saddle(m, body):
    """The racing saddle: a thin felt pad on the withers, a low seat set forward with a small pommel and a low cantle
    (the rider leans with the run), short flaps, one girth, a breast strap, and bone stirrups hung on leathers.
    Faces lying on the body are left out (no back-face culling in GeckoLib)."""
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    sd = m.bone("saddle", body, (0, 61, -20))
    m.cube(sd, (-7.5, 59, -33), (7.5, 61, -13), name="pad", mat="fur", faces=out("down"))
    m.pair(sd, sd, (7, 50, -31), (8, 60, -20), name="flap_f", mat="hide", faces=out("east", "up"))
    m.cube(sd, (-5, 61, -30), (5, 63, -16), name="seat", mat="hide", faces=out("down"))
    m.cube(sd, (-3, 63, -30), (3, 65, -28), name="pommel", mat="hide")
    m.cube(sd, (-5, 63, -18), (5, 65, -15), name="cantle", mat="hide")
    m.pair(sd, sd, (8, 45, -26), (9, 59, -25), name="leather", mat="strap", faces=out("east", "up"))
    m.pair(sd, sd, (8, 42, -27), (11, 45, -26), name="stir_f", mat="bone")
    m.pair(sd, sd, (8, 42, -25), (11, 45, -24), name="stir_b", mat="bone")
    m.pair(sd, sd, (8, 41, -27), (11, 42, -24), name="stir_t", mat="bone")
    # the girth, down the flank under the flap and across the belly
    m.pair(sd, sd, (7, 38, -23), (8, 50, -21), name="girth", mat="strap", faces=out("east", "up"))
    m.cube(sd, (-6, 30, -23), (6, 31, -21), name="girth_under", mat="strap", faces=out("up"))
    m.pair(sd, sd, (6, 30, -23), (7, 38, -21), name="girth_low", mat="strap", faces=out("east"))
    # the breast strap round the base of the neck
    m.pair(sd, sd, (6.5, 40, -44), (7.5, 55, -42), name="breast", mat="strap", faces=out("east"))


SADDLE_ART = {   # column 0 at the FRONT, row 0 at the top; a = L1, b = L2, c = L3 (worn by the rider's calf), d = L0
    "flap_f": ["aaaaaaaaaaa", "bbbbbbbbbbb", "bbbbbbbcbbb", "bbbbbbcccbb", "bbbbbbbcbbb", "bbbbbbbbbbb",
               "bbbbbbbbbbb", "abbbbbbbbba", "aabbbbbbbaa", "adaaaaaaada"],
}


def saddle_px(t):
    mat = t.cube["mat"]; n = t.cube["name"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    key = {"a": "L1", "b": "L2", "c": "L3", "d": "L0"}
    if mat == "fur":            # the felt pad: plain, a darker hem
        if f == "up":
            return p["F2"] if h32(i, j, 33) % 100 < 7 else p["F1"]
        return p["F0"] if j == h - 1 else p["F1"]
    if mat == "iron":
        return p["I2"] if f == "up" else (p["I0"] if j == h - 1 and h > 1 else p["I1"])
    if mat == "bone":
        return p["B1"] if f == "up" or j == 0 else p["B0"]
    if mat == "strap":
        if f in ("up", "down"):
            return p["L1"] if f == "down" else p["L2"]
        return p["L1"] if j == h - 1 else p["L2"]
    if n in SADDLE_ART and f in ("east", "west"):
        fc = (w - 1 - i) if f == "east" else i
        return p[key[SADDLE_ART[n][j][fc]]]
    if f == "up":
        return p["L4"] if n in ("pommel", "cantle") else p["L3"]
    if f == "down":
        return p["L0"]
    return p["L3"] if j == 0 else (p["L1"] if j == h - 1 else p["L2"])


def preview_faces(m):
    """previews only: swap east/west on cubes that drop one of them, so the preview shows the face the game shows"""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m


def build(saddle_on=True):
    m = P.Model("albertosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, HIP_Y, 0))
    # the trunk: slim and shallow, the belly line rising to the hips
    m.cube(body, (-6.5, 33, -44), (6.5, 56, -31), name="chest")
    m.cube(body, (-4, 30, -42), (4, 34, -31), name="keel")
    m.cube(body, (-7.5, 35, -33), (7.5, 59, -7), name="torso")
    m.cube(body, (-6, 32, -32), (6, 36, -12), name="belly", mat="belly")
    m.cube(body, (-7, 41, -9), (7, 60, 9), name="hips")
    m.cube(body, (-4.5, 58, -35), (4.5, 60, -5), name="back")
    # the neck: slimmer and a little longer than the tyrannosaurines', in the S by the rest angles
    n1 = m.bone("neck1", body, (0, 48, -42), (REST["neck1"], 0, 0))
    m.cube(n1, (-5.5, 38, -49), (5.5, 56, -37), name="shoulders")
    m.cube(n1, (-4.5, 40, -58), (4.5, 55, -47), name="neck1")
    n2 = m.bone("neck2", n1, (0, 48, -56), (REST["neck2"], 0, 0))
    m.cube(n2, (-4, 42, -66), (4, 54, -54), name="neck2")
    m.cube(n2, (-3.5, 39, -66), (3.5, 43, -55), name="throat")
    hd = m.bone("head", n2, (0, 48, -64))
    head(m, hd, 43, -64, rest=(REST["skull"], 0, 0))
    arms(m, body); legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the skin (skin2, the 1.10.1 standard)
TRUNK = {"chest", "keel", "torso", "hips", "back", "shoulders", "neck1", "neck2", "throat", "tail1", "tail2", "tail3",
         "tail4", "tail5", "tail_muscle"}
LEG = {"calf", "shin", "meta", "toe_mid", "toe_out", "toe_in", "hallux"}
LIMB = {"thigh", "thigh_low", "knee", "arm", "forearm", "hand"}
BODY_PARTS = TRUNK | LEG | LIMB | {"belly"}
HEAD = {"cranium", "occiput", "temporal", "snout", "premax", "jaw_back", "jaw_front"}

# THE MARKS (drawn, not drawn by lot):
# 1. the pale LATERAL STRIPE from the shoulder to the tail, a dark rim over it (body heights, wandering slowly);
# 2. a row of dark PAIRED SPOTS down the spine, from the withers to the tail (z centres), fading into rings on the tip;
# 3. the dark EYE BAND, from the eye back over the temporal muscle to the jaw joint (head_tone).
STRIPE = (0.44, 0.555, 0.60)                 # the stripe from 0.44 to 0.555 of the body's height, its rim to 0.60
STRIPE_Z = (-48.0, 70.0)                     # from the shoulder to two thirds of the tail
SPOTS = [-40, -31, -22, -13, -4, 5, 14, 24, 34, 44, 54, 64, 73, 81]
_prof = {}


def body_tone(t, prof, sex):
    """the palette key of a body texel: the countershading by the silhouette, the stripe, the spots, the blotches"""
    n = t.cube["name"]; f = t.face
    z, y, x = t.P[2], t.P[1], t.P[0]
    if f == "down" or n in ("belly", "keel", "tail_muscle"):
        h = 0.0 if f == "down" else min(0.17, prof.height(t))
    elif f == "up":
        h = 1.0
    else:
        h = prof.height(t)
    stripe_on = STRIPE_Z[0] < z < STRIPE_Z[1] and f in ("east", "west")
    lim = (0.18, 0.25) + (STRIPE if stripe_on else (0.50, 0.50, 0.50)) + (0.80,)
    b = skin2.bands(h, z, lim, amp=0.04, seed=2)
    if b == 0:
        u, v = skin2.surface_uv(t)
        k = skin.scutes(u, v, row=3, width=5)
        return {"seam": "b0", "hi": "b2", "base": "b1"}[k]
    base = ["b1", "b0", "k4", "s1", "k2", "k3", "k2"][b]
    if b == 3:                  # the stripe itself: calm, a soft darker wash now and then, pale toward the tail
        return "s0" if skin2.soft(*skin2.surface_uv(t), 7.0, seed=13) < 0.32 else "s1"
    if b == 4:
        return "k2"
    if b >= 5:
        # the paired dark spots either side of the spine (only on the top and the upper flank)
        s = skin2.stripe(z, y, SPOTS, 1.3, slant=0.0, wander=0.5, seed=5)
        if s is not None and (f == "up" and 0.8 < abs(x) < 3.6 or f != "up" and h > 0.88):
            torn = skin2.soft(*skin2.surface_uv(t), 2.5, seed=21 + s) < 0.25
            if not torn:
                return "k1"
    if b >= 2:
        base = skin2.step(base, skin2.mottle(t, cell=10, strength=0.2, seed=3))
        # padrão v2: the body's own scales at one tone step, in body space (calm, but not a plain flank)
        base = skin2.step(base, head2.body_scales(t, cell=BODY_SCALE, seed=4))
    return base


def limb_tone(t):
    """legs and arms: calm, lit on the front, a step darker behind and below; scutes across the front of the long
    metatarsus and the toes"""
    n = t.cube["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    v = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    if n in ("thigh", "thigh_low", "knee"):
        base = "k4"
        if f in ("east", "west") and t.rel[2] > 0.55 and v < 0.45:
            base = "k3"
        if f in ("east", "west", "north") and t.rel[2] < 0.3 and 0.35 < v < 0.8:
            base = "k5"
        if f in ("east", "west") and v > 0.86:
            base = "k3"
        if f == "south" or f == "down":
            base = "k3"
        return skin2.step(base, skin2.mottle(t, cell=8, strength=0.22, seed=6))
    if n in ("arm", "forearm", "hand"):
        return "k4" if f in ("north", "up", "east", "west") and v > 0.3 else "k3"
    base = "k4" if f in ("north", "up") else "k3"
    if n in ("meta", "toe_mid", "toe_out", "toe_in") and f in ("north", "up", "east", "west"):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 3
        if k == 0 and (t.i % 3) != 1:
            return skin2.step(base, -1)
        return base
    if f == "south":
        return "k3"
    return skin2.step(base, skin2.mottle(t, cell=6, strength=0.25, seed=7))


def head_tone(t, sex):
    """the face (padrão v2): three tones by height (dark crown, middle cheek, light jaw) as one shape over the head,
    small scales over all of it at one tone step (head2.face_scale, body space), the dark EYE BAND from the eye back
    to the jaw joint, the rugose nasal ridge and maxilla (head2.rugose), the lip a step lighter and the dark mouth
    line over the teeth"""
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "b1"
    if n in ("jaw_back", "jaw_front"):
        if f == "up":
            return "k4"
        h = t.rel[1]
        if t.j == 0:
            return "k1"                       # the lower lip's dark edge under the teeth
        base = "b1" if h < 0.3 else ("b2" if h < 0.55 else "k4")
        return skin2.step(base, min(0, head2.face_scale(t, cell=2.4, seed=33)))
    if f == "up":
        if n in ("snout", "premax"):
            return skin2.step("k2", head2.rugose(t, seed=21))
        return skin2.step("k2", head2.face_scale(t, cell=2.2, seed=24, lift=3))
    v = t.rel[1]
    if n in ("snout", "premax"):
        if t.j == t.h - 1:
            return "k0"                       # the dark mouth line
        if t.j == t.h - 2:
            return "k5"                       # the lip, a step lighter than the cheek
    hv = (t.P[1] - HEAD_Y[0]) / max(1.0, HEAD_Y[1] - HEAD_Y[0])
    base = ["k4", "k3", "k2"][skin2.bands(hv, t.P[2] * 2.0, (0.40, 0.72), amp=0.07, seed=31)]
    # the eye band: from just behind the eye back over the temporal and occiput, sloping to the jaw joint
    if n in ("cranium", "temporal", "occiput") and f in ("east", "west"):
        zc = t.P[2] - (EYE_Z[0])
        yb = EYE_Z[1] - 0.22 * zc
        if zc > 0.0 and abs(t.P[1] - yb) < 1.2 + 0.06 * zc and t.rel[1] > 0.15:
            return "k0" if head2.face_scale(t, cell=2.2, seed=34) < 0 else "k1"
    if n in ("snout", "premax") and 0.15 < v < 0.55:
        return skin2.step(base, head2.rugose(t, seed=9))
    return skin2.step(base, head2.face_scale(t, cell=2.2, seed=32, lift=3))


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]; f = t.face; n = t.cube["name"]
        if mat in ("hide", "fur", "strap", "iron", "bone"):
            return saddle_px(t)
        if mat == "claw":
            return p["ker0"] if f != "up" else p["ker1"]
        if mat == "crest_base":  # the crest's foot: the face's own skin, rugose
            if f == "up":
                return p[skin2.step("k3", head2.rugose(t, seed=74))]
            return p["k1"] if t.j >= t.h - 1 else p[skin2.step("k2", head2.face_scale(t, cell=2.0, seed=75))]
        if mat == "horn":       # the crest's display skin: rust on the male, the dark crown's on the female; the
            if (f == "up" and t.rel[2] < 0.4) or (f == "north" and t.j == 0):    # keratin point at its front top
                return p["ker1"] if f == "north" else p["ker3"]
            if sex == "male":
                if f == "up":
                    return p["hr2"]
                return p["hr0"] if t.j >= t.h - 1 else (p["hr2"] if t.j == 0 else p["hr1"])
            return p["k3"] if f == "up" else p[skin2.step("k2", head2.face_scale(t, cell=2.0, seed=76))]
        if mat == "brow":       # the low brow shelf: the crown's dark, lit along its top, black under it
            if f == "up":
                return p[skin2.step("k3", head2.rugose(t, seed=77))]
            if f == "down":
                return p["k0"]
            return p["k2"] if t.j == 0 else p["k1"]
        if mat == "plate":      # the rugose nasals: a ridge of small bumps
            if f in ("up", "north"):
                return p[skin2.step("k2", head2.rugose(t, seed=78, every=2))]
            return p["k2"]
        if mat == "teeth":
            return head2.teeth_up(t, p, every=2, long_every=2, seed=11)
        if mat == "teeth_lo":
            return head2.teeth_lo(t, p)
        if mat == "mouth":
            return p["gum"] if f in ("up", "down") else p["mouth"]
        if mat == "tongue":
            return p["tongue"] if f == "up" else p["mouth"]
        if mat == "gular":
            return p["b1"] if f != "up" else p["b0"]
        if n in TRUNK or n == "belly":
            return p[body_tone(t, PROF[0], sex)]
        if n in LEG or n in LIMB:
            return p[limb_tone(t)]
        if n in HEAD:
            return p[head_tone(t, sex)]
        return p["k3"]
    return sh


PROF = [None]
BODY_SCALE = 8.0          # the body's scale cell in texels (padrão v2: one tone step, body neighbours change 0.20-0.30)
HEAD_Y = [0.0, 1.0]       # the lowest and highest point of the face at rest (the head's countershading)
EYE_Z = [0.0, 0.0]        # rest-pose z and y of the eye (the eye band starts there)

# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP
NOSTRIL = [      # the nostril high on the narrow snout tip, a lit rim over it
    "hh",
    "nn",
]


def decals_for(sex):
    p = pal_for(sex)
    cm = head2.eye_cmap(p, soft="k0")
    cm.update({"n": p["k0"], "h": p["k5"], "s": p["scar"]})

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", head2.EYE_HOODED, cm, at=(0, 3))
        P.stamp(img, m, C["premax"], "east", NOSTRIL, cm, at=(0, 1))
        # the row of nerve foramina above the lip line
        u, v, w, h = C["snout"]["uv"]["east"]
        for k in range(2, w - 1, 3):
            img[v + h - 3, u + w - 1 - k] = (*p["k1"], 255)
        head2.mouth_interior(img, C, p, ("snout", "premax", "cranium"), ("jaw_front", "jaw_back"))
    return dec


def paint_sex(m, sex="male"):
    PROF[0] = skin2.Profile(m, TRUNK | {"belly"})
    import geo
    pts = {c["name"]: q for c, q in geo.cube_points(m.spec())}
    ys = [pts[n][:, 1] for n in ("cranium", "snout", "premax")]
    HEAD_Y[:] = [min(a.min() for a in ys), max(a.max() for a in ys)]
    cr = pts["cranium"]
    # the eye sits at the front top of the cranium (the stamp at column 1, rows 3-5 of 11)
    EYE_Z[:] = [float(cr[:, 2].min()) + 5.5, float(cr[:, 1].max()) - 5.0]
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
