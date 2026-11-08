"""Daspletosaurus torosus, made by hand from its own study (docs/estudos/13_PREDADORES_1_10.md, approved by Rodrigo on
07/11/2026). Real size 9.5 m (the top of the estimates without the 2025 specimen, Rodrigo's answer).

The PILOT of the 1.10.1 standard (docs/estudos/14_POR_QUE_PARECE_IA.md, "Decisões do Rodrigo"):
- one texel = one Minecraft pixel: drawn at skin2.PX_PER_M (16.94 px per metre), so in game it is shown at a model
  scale of ~1 and every texel is the size of a pixel of a block (skin2.density);
- the skin is laid in BODY space (skin2): the tones come from the whole silhouette (dark back, middle flank, pale
  belly as one shape from the snout to the tail tip), a calm base with big soft blotches, scales only where they
  belong (the flat plates of the face, the feet, the belly scutes) and the species' marks DRAWN as shapes;
- the detail stays (Rodrigo: the detail gives personality), but standardised.

The head, from the study (Russell 1970; Carr 1999; Currie 2003; Carr et al. 2017; Cullen et al. 2023):
- a deep, narrow, massive skull for the body: 26 px from the back of the skull to the snout (1.5 m drawn: the real
  1.1 m exaggerated by a third, the study-14 rule of one signature shape), 15 px tall at the back, only 10 wide
  (the T. rex's is 26 wide in its rig): the eyes look more to the side than the T. rex's;
- a tall lacrimal "horn" in front of each eye (the D. torosus one is the tallest of the genus), a second boss of the
  postorbital behind the eye;
- the maxilla rugose, flat scales over the snout (Carr et al. 2017), in burnt-bone colour on the plates;
- lips covering the upper teeth with the mouth shut (Cullen et al. 2023): the teeth only show when it opens;
- the arms the longest of the family for the body (Russell 1970): 7 + 5 px, two fingers;
- a heavy, compact body on strong legs: a shorter, deeper trunk than the T. rex's.

Colour "mogno-fumê" (study 13): a smoky mahogany back, a lighter flank with broken dark saddles, a greyed pinkish
beige belly; the face plates and lacrimal horns burnt bone; on the male the postorbital bosses rust-ochre and pale
scars on the snout (the face bites, Tanke & Currie 1998).
"""
import math

import proto as P
import skin
import skin2
from proto import hx, h32

TEX_W = 256
PX_M = skin2.PX_PER_M

# ------------------------------------------------------------------ palette
# k0..k5 the body ramp (hue-shifted: shadows to wine, lights to warm grey), b0..b3 the belly, hb the burnt bone of the
# face plates and horns, hr the male's rust bosses
SCHEME = {
    "k0": "201217", "k1": "321b23", "k2": "472a33", "k3": "5c3a42", "k4": "735055", "k5": "8a6a68",
    "b0": "7c6466", "b1": "9a8283", "b2": "b29c98", "b3": "c6b3aa",
    "hb0": "4f3a32", "hb1": "6a5246", "hb2": "86705c", "hb3": "a08a72",
    "hr0": "61382a", "hr1": "8e4f2c", "hr2": "b0683a",
    "lip": "8a6d66", "scar": "b8a092",
    "female": {"k1": "39222a", "k2": "51333c", "k3": "67454d", "k4": "7f5d5f", "k5": "967672",
               "b0": "85706f", "b1": "a38b8b", "b2": "baa6a0"},
}
PAL = {
    "ker0": hx("1e1714"), "ker1": hx("362a22"), "ker2": hx("cdbf9f"), "ker3": hx("9e8d6f"),
    "iris": hx("c65a2a"), "iris2": hx("8a3a1e"), "pupil": hx("120c0b"), "lid": hx("150c0e"), "glint": hx("f0e4c4"),
    "gum": hx("743336"), "mouth": hx("381a1d"), "tongue": hx("9a4f4b"), "tooth": hx("ebe1c6"), "tooth2": hx("c2b28c"),
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


SNOUT_ROT = (-5, 0, 0)      # the snout slopes down from the eyes to the tip (the deep tyrannosaurine profile)


def head(m, parent, hy, hz, rest=(-6, 0, 0)):
    """the skull and jaw. (hy, hz): the mouth line at the back of the skull; returns the skull bone"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    sk = m.bone("skull", parent, (0, hy + 6, hz), rest)
    so = (0, hy + 13, hz - 11)              # the snout hinges at the front of the cranium, at its top
    m.cube(sk, *B(-5, 0, -11, 5, 15, 0), name="cranium")
    m.cube(sk, *B(-4, 4, 0, 4, 13, 2), name="occiput")
    m.pair(sk, sk, *B(5, 2, -6, 7, 8, -1), name="temporal")             # the jaw muscle bulging behind the eye
    m.cube(sk, *B(-4, 0, -24, 4, 13, -11), name="snout", rot=SNOUT_ROT, origin=so)
    m.cube(sk, *B(-3, 0, -26, 3, 10, -24), name="premax", rot=SNOUT_ROT, origin=so)
    m.cube(sk, *B(-2, 13, -23, 2, 14, -12), name="nasal", mat="plate", rot=SNOUT_ROT, origin=so)   # the fused nasals
    # the tall lacrimal horn in front of each eye (tilted forward a little) and the postorbital boss behind it
    # (padrão v2: the horn grows out of the skull, a base of the face's own skin and only its tip burnt bone; the
    # boss the same; a brow shelf over the socket between them)
    lo = (3, hy + 14, hz - 12)
    m.pair(sk, sk, *B(1.5, 14, -14, 4.5, 16, -10), name="lacrimal", mat="horn_base", rot=(-8, 0, 0), origin=lo)
    m.pair(sk, sk, *B(2, 15.5, -13.5, 4, 17.5, -11.5), name="lacrimal_tip", mat="horn", rot=(-16, 0, 0), origin=lo)
    m.pair(sk, sk, *B(4, 11, -7, 6, 14, -3), name="boss", mat="boss")
    m.pair(sk, sk, *B(4, 10, -11.5, 6, 11, -7.5), name="brow", mat="brow")
    jaw = m.bone("jaw", sk, (0, hy + 1, hz - 2))
    m.cube(jaw, *B(-4.5, -5, -10, 4.5, 0, 0), name="jaw_back")
    m.cube(jaw, *B(-3.5, -4, -25, 3.5, 0, -10), name="jaw_front", rot=(-2, 0, 0), origin=(0, hy, hz - 10))
    m.cube(jaw, *B(-3.5, -7, -12, 3.5, -5, -3), name="gular", mat="gular")     # the throat skin under the jaw
    m.cube(jaw, *B(-4, -1, -7, 4, 2, -1), name="cheek", mat="mouth")          # the mouth's inner wall
    m.cube(jaw, *B(-1.5, -2, -22, 1.5, 1, -6), name="tongue", mat="tongue")
    m.cube(sk, *B(-1, -1, -23, 1, 2, -11), name="palate", mat="mouth")
    # teeth as alpha planes. Padrão v2: the upper row hangs just OUTSIDE the lower jaw (3.75 > 3.5) under the snout's
    # lip (4): with the mouth shut the long D-section crowns show over the jaw, the lips covering only their base
    # (Cullen et al. 2023 give lips; they do not hide teeth this long). The lower row sits inside the snout
    m.pair(sk, sk, *B(3.75, -3, -24, 3.75, 0, -11), name="teeth_up", mat="teeth", rot=SNOUT_ROT, origin=so)
    m.pair(jaw, jaw, *B(2.5, -1, -24, 2.5, 2, -10), name="teeth_lo", mat="teeth_lo")
    return sk


REST = {   # bone rest angles (x: + = far end up for the neck and tail, knee forward for the thigh)
    "neck1": 30, "neck2": 6, "skull": -30, "thigh": 22, "shin": -52, "foot": 44, "toes": -14,
    "arm": 18, "forearm": -72, "tail1": -5, "tail2": 2, "tail3": 1.5, "tail4": 0.5, "tail5": 0,
}


def legs(m, body):
    """heavy legs: a big drumstick into the hip, a deep calf, a long metatarsus, and a broad foot of three toes
    plus the small first toe (wider than the shin, the study-14 rule)"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (8 * sx, 44, 0), (REST["thigh"], 0, 5 * sx))
        sh = m.bone(f"shin_{side}", th, (8 * sx, 26, 0), (REST["shin"], 0, -10 * sx))
        ft = m.bone(f"foot_{side}", sh, (8 * sx, 10, 0), (REST["foot"], 0, 5 * sx))
        m.bone(f"toes_{side}", ft, (8 * sx, -3, 0), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (3, 37, -9), (14, 54, 9), name="thigh")
    m.pair("thigh_l", "thigh_r", (4, 29, -7.5), (13, 38, 6.5), name="thigh_low")
    m.pair("thigh_l", "thigh_r", (4.5, 23, -5.5), (12.5, 30, 4.5), name="knee")
    m.pair("shin_l", "shin_r", (4.5, 14, -5), (11.5, 27, 4), name="calf")
    m.pair("shin_l", "shin_r", (5, 6, -3), (11, 15, 3), name="shin")
    m.pair("foot_l", "foot_r", (5.5, -4, -2.5), (10.5, 11, 2.5), name="meta")
    m.pair("toes_l", "toes_r", (6.5, -5, -12), (9.5, -2, 0), name="toe_mid")
    m.pair("toes_l", "toes_r", (9.5, -5, -9), (12.5, -2, -1), name="toe_out")
    m.pair("toes_l", "toes_r", (3.5, -5, -9), (6.5, -2, -1), name="toe_in")
    m.pair("toes_l", "toes_r", (7.5, -5, -14), (8.5, -3, -12), name="claw_mid", mat="claw")
    m.pair("toes_l", "toes_r", (10.5, -5, -11), (11.5, -3, -9), name="claw_out", mat="claw")
    m.pair("toes_l", "toes_r", (4.5, -5, -11), (5.5, -3, -9), name="claw_in", mat="claw")
    m.pair("foot_l", "foot_r", (4.5, -2, 1.5), (6.5, 0, 4.5), name="hallux")


def arms(m, body):
    """the longest arms of the family for the body (Russell 1970), still small: an upper arm of 7 px (0.4 m), a
    forearm of 5, a hand of two fingers with hooked claws"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (7 * sx, 32, -36), (REST["arm"], 0, -6 * sx))
        m.bone(f"forearm_{side}", a, (7 * sx, 26, -36), (REST["forearm"], 0, 0))
    m.pair("arm_l", "arm_r", (5.5, 25, -37.5), (8.5, 33, -34.5), name="arm")
    m.pair("forearm_l", "forearm_r", (5.5, 21, -37), (8.5, 26, -35), name="forearm")
    m.pair("forearm_l", "forearm_r", (6, 19, -37), (8, 21, -35), name="hand")
    m.pair("forearm_l", "forearm_r", (7, 17, -37), (8, 19, -36), name="claw_f1", mat="claw")
    m.pair("forearm_l", "forearm_r", (6, 17.5, -36), (7, 19.5, -35), name="claw_f2", mat="claw")


TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5")


def tail(m, body):
    """deep and heavy at the root (the caudofemoral muscle), tapering steadily; each segment starts 2 px inside the
    one before (no gap in motion) and none repeats the size of another (study 14, C)"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 8, 31, 7, 33, 52), ("tail2", 29, 49, 5.5, 36, 50), ("tail3", 47, 64, 4, 38.5, 48.5),
        ("tail4", 62, 74, 2.5, 40.5, 46.5), ("tail5", 72, 82, 1.5, 41.5, 45.5)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-5, 30, 6), (5, 34, 24), name="tail_muscle")


SADDLE_PAL = {   # dark oiled leather and bone: the tyrant saddle (its own: heavy, with a hide pad and a bone toggle)
    "L0": hx("2e1c12"), "L1": hx("48301e"), "L2": hx("644329"), "L3": hx("7f5835"), "L4": hx("9a7046"),
    "F0": hx("6b5a44"), "F1": hx("8a7658"), "F2": hx("a69273"),
    "I0": hx("4a4a48"), "I1": hx("787874"), "I2": hx("a4a49c"), "B0": hx("b9aa88"), "B1": hx("ddd0b0"),
}


def saddle(m, body):
    """The tyrant saddle: a broad hide pad over the shoulders, a deep seat with a high cantle (it is the toughest and
    slowest of the mid tyrannosaurs, a mount you sit in), long flaps, a girth and a breast strap tied with a bone
    toggle. Faces lying on the body are left out (no back-face culling in GeckoLib)."""
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    sd = m.bone("saddle", body, (0, 55, -16))
    m.cube(sd, (-9.5, 53, -30), (9.5, 55, -6), name="pad", mat="fur", faces=out("down"))
    m.pair(sd, sd, (9, 42, -28), (10, 53, -16), name="flap_f", mat="hide", faces=out("east", "up"))
    m.pair(sd, sd, (9, 45, -16), (10, 53, -8), name="flap_b", mat="hide", faces=out("east", "up", "north"))
    m.cube(sd, (-6, 55, -25), (6, 57, -10), name="seat", mat="hide", faces=out("down"))
    m.cube(sd, (-4, 57, -25), (4, 59, -22), name="pommel", mat="hide")
    m.cube(sd, (-6, 57, -12), (6, 61, -9), name="cantle", mat="hide")
    m.cube(sd, (-5, 61, -11), (5, 62, -9), name="cantle_lip", mat="hide")
    m.pair(sd, sd, (10, 39, -23), (11, 53, -22), name="leather", mat="strap", faces=out("east", "up"))
    m.pair(sd, sd, (10, 36, -24), (13, 39, -23), name="iron_f", mat="iron")
    m.pair(sd, sd, (10, 36, -22), (13, 39, -21), name="iron_b", mat="iron")
    m.pair(sd, sd, (10, 35, -24), (13, 36, -21), name="iron_t", mat="iron")
    # the girth, down the flank under the flap and across the belly
    m.pair(sd, sd, (9, 28, -19), (10, 42, -17), name="girth", mat="strap", faces=out("east", "up"))
    m.cube(sd, (-8, 22, -19), (8, 23, -17), name="girth_under", mat="strap", faces=out("up"))
    m.pair(sd, sd, (8, 22, -19), (9, 28, -17), name="girth_low", mat="strap", faces=out("east"))
    # the breast strap round the base of the neck, the bone toggle on the left
    m.pair(sd, sd, (9, 35, -31), (10, 51, -29), name="breast", mat="strap", faces=out("east"))
    m.cube(sd, (10, 43, -32), (11, 46, -28), name="toggle", mat="bone")


SADDLE_ART = {   # column 0 at the FRONT, row 0 at the top; a = L1, b = L2, c = L3 (worn by the rider's calf), d = L0
    "flap_f": ["aaaaaaaaaaaa", "bbbbbbbbbbbb", "bbbbbbbbbbbb", "bbbbbbbcbbbb", "bbbbbbcccbbb", "bbbbbbbcbbbb",
               "bbbbbbbbbbbb", "bbbbbbbbbbbb", "abbbbbbbbbba", "aabbbbbbbbaa", "adaaaaaaaada"],
    "flap_b": ["aaaaaaaa", "bbbbbbbb", "bbbbbbbb", "bbbbbbbb", "bbbbbbbb", "bbbbbbbb", "abbbbbba", "aaadaaaa"],
}


def saddle_px(t):
    mat = t.cube["mat"]; n = t.cube["name"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    key = {"a": "L1", "b": "L2", "c": "L3", "d": "L0"}
    if mat == "fur":            # the hide pad: short hair, a soft lit fringe
        if f == "up":
            return p["F2"] if h32(i, j, 33) % 100 < 9 else p["F1"]
        return p["F0"] if j == h - 1 else (p["F2"] if h32(i, 37) % 100 < 22 else p["F1"])
    if mat == "iron":
        return p["I2"] if f == "up" else (p["I0"] if j == h - 1 and h > 1 else p["I1"])
    if mat == "bone":
        return p["B1"] if f == "up" or j == 0 else p["B0"]
    if mat == "strap":
        if n == "girth" and f in ("east", "west") and 1 <= j <= 2:
            return p["I2"] if j == 1 else p["I1"]
        if f in ("up", "down"):
            return p["L1"] if f == "down" else p["L2"]
        return p["L1"] if j == h - 1 else p["L2"]
    if n in SADDLE_ART and f in ("east", "west"):
        fc = (w - 1 - i) if f == "east" else i
        return p[key[SADDLE_ART[n][j][fc]]]
    if f == "up":
        return p["L4"] if n in ("pommel", "cantle_lip") else p["L3"]
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
    m = P.Model("daspletosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 44, 0))
    # the trunk: short, deep and heavy (compact against the T. rex's), the belly line rising to the hips
    m.cube(body, (-7.5, 26, -41), (7.5, 49, -28), name="chest")
    m.cube(body, (-5, 22, -39), (5, 27, -28), name="keel")
    m.cube(body, (-9, 27, -30), (9, 52, -5), name="torso")
    m.cube(body, (-7, 23, -29), (7, 28, -9), name="belly", mat="belly")
    m.cube(body, (-8, 32, -7), (8, 53, 11), name="hips")
    m.cube(body, (-5.5, 51, -32), (5.5, 54, -3), name="back")
    # the neck: thick, short, bent up into the S by the rest angles; every segment starts inside the one behind
    n1 = m.bone("neck1", body, (0, 42, -40), (REST["neck1"], 0, 0))
    m.cube(n1, (-6.5, 30, -47), (6.5, 51, -35), name="shoulders")
    m.cube(n1, (-5.5, 33, -55), (5.5, 50, -45), name="neck1")
    n2 = m.bone("neck2", n1, (0, 43, -53), (REST["neck2"], 0, 0))
    m.cube(n2, (-5, 36, -62), (5, 50, -51), name="neck2")
    m.cube(n2, (-4, 33, -62), (4, 37, -52), name="throat")
    hd = m.bone("head", n2, (0, 43, -60))
    head(m, hd, 37, -60, rest=(REST["skull"], 0, 0))
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

# THE MARKS (drawn, not drawn by lot): broken dark saddles across the back from the shoulders to the tail, closing into
# rings on the thin tail. (z centre at the spine, half length); they lean back a little down the flank
SADDLES = [(-46, 3.0), (-31, 4.5), (-15, 4.5), (2, 4.0), (19, 4.0), (35, 3.5), (50, 3.0), (63, 2.5), (75, 2.0), (84, 1.5)]
_prof = {}


def profile(m):
    if "p" not in _prof:
        _prof["p"] = skin2.Profile(m, TRUNK | {"belly"})
    return _prof["p"]


def body_tone(t, prof, sex):
    """the palette key of a body texel: the countershading by the silhouette, the saddles, the soft blotches"""
    n = t.cube["name"]; f = t.face
    z, y = t.P[2], t.P[1]
    if f == "down" or n in ("belly", "keel", "tail_muscle"):
        h = 0.0 if f == "down" else min(0.18, prof.height(t))
    elif f == "up":
        h = 1.0
    else:
        h = prof.height(t)
    b = skin2.bands(h, z, (0.20, 0.26, 0.50, 0.78), amp=0.05, seed=2)
    if b == 0:
        u, v = skin2.surface_uv(t)
        k = skin.scutes(u, v, row=3, width=6)          # the belly's rows of wide scutes: the one scale that reads
        return {"seam": "b0", "hi": "b2", "base": "b1"}[k]
    base = ["b1", "b0", "k5", "k4", "k3"][b]
    if b >= 3:
        # the saddles: dark, broken by a soft field so each one reads as a torn patch, not a stripe
        s = skin2.stripe(z, y, [c for c, _ in SADDLES], 3.6, slant=-0.10, wander=1.0, seed=5)
        if s is not None:
            hl = SADDLES[s][1] / 3.6
            core = abs(z - (SADDLES[s][0] - 0.10 * y)) < 3.6 * hl + 0.6
            torn = skin2.soft(*skin2.surface_uv(t), 3.0, seed=11 + s) < 0.30
            if core and not torn:
                base = "k1" if (b == 4 and sex == "male") else "k2"
    if b >= 2:
        base = skin2.step(base, skin2.mottle(t, cell=9, strength=0.2, seed=3))
        # padrão v3: the body's own motif, the tyrannosaur BASEMENT SCALES in staggered rows (bricks), one tone step
        base = skin2.step(base, bricks(t, row=BRICK[0], width=BRICK[1], seed=4))
    return base


def limb_tone(t):
    """legs and arms: calm, lit on the front, a step darker behind and below; scutes across the front of the
    metatarsus and toes (the one place a leg shows its scales at this size)"""
    n = t.cube["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    v = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    if n in ("thigh", "thigh_low", "knee"):
        base = "k4"
        if f in ("east", "west") and t.rel[2] > 0.55 and v < 0.45:
            base = "k3"                                   # the shade where the drumstick meets the tail muscle
        if f in ("east", "west", "north") and t.rel[2] < 0.3 and 0.35 < v < 0.8:
            base = "k5"                                   # the lit front of the drumstick
        if f in ("east", "west") and v > 0.86:
            base = "k3"                                   # the top of the drumstick, under the flank's dark
        if f == "south" or f == "down":
            base = "k3"
        return skin2.step(base, skin2.mottle(t, cell=8, strength=0.22, seed=6))
    if n in ("arm", "forearm", "hand"):
        return "k4" if f in ("north", "up", "east", "west") and v > 0.3 else "k3"
    base = "k4" if f in ("north", "up") else "k3"
    if n in ("meta", "toe_mid", "toe_out", "toe_in") and f in ("north", "up", "east", "west"):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 3
        if k == 0 and (t.i % 4) != 1:
            return skin2.step(base, -1)
        return base
    if f == "south":
        return "k3"
    return skin2.step(base, skin2.mottle(t, cell=6, strength=0.25, seed=7))


# ------------------------------------------------------------------ padrão v3: the Daspletosaurus' own head
# (docs/estudos/14, "Padrão v3": the engine only measures, every part below is drawn for this animal alone)
#
# THE MOTIF: the big FLAT PLATES of a tyrannosaur's face (Carr et al. 2017: large flat scales over the snout with
# the sensory organs between them): polygons of one flat tone each, outlined by a dark seam all round, biggest on the
# snout, smaller on the cranium; a row of square LABIAL scales along each lip. The body carries the tyrannosaur
# basement scales as staggered rows ("bricks"), broken by a soft field.
def plates(t, cell=3.6, seed=0):
    """(kind, tone step, centre) of the plate under a texel: 'seam' on its outline (-1), 'rim' on its raised upper
    edge (+1), else 'plate' with a flat step (0, or +1 for one plate in four); centre = (u, v) of the plate's seed,
    so the caller can take ONE base tone for the whole plate"""
    u, v = skin2.surface_uv(t)
    uc, vc = math.floor(u) + 0.5, math.floor(v) + 0.5
    d1, d2, (cx, cy, px, py) = skin.voronoi(uc, vc, cell, seed)
    if d2 - d1 < 0.75:
        return "seam", -1, (px, py)
    if d2 - d1 < 1.6 and vc > py + 0.5:
        return "rim", 1, (px, py)
    return "plate", (0, 0, 1, 0)[h32(cx, cy, seed, 4) % 4], (px, py)


def bricks(t, row=3, width=6, seed=0):
    """-1 on the seams of the staggered rows of basement scales (the lower edge of each row and the joint between
    two scales), broken where a soft field says the scales are worn smooth; 0 elsewhere"""
    u, v = skin2.surface_uv(t)
    r = math.floor(v / row); k = math.floor(v) - r * row
    c = (math.floor(u) + (r % 2) * (width // 2)) % width
    if skin2.soft(u, v, 7.0, seed) < 0.5:
        return 0
    if k == 0 and c != width - 1:
        return -1
    if c == 0 and k == row - 1:
        return -1
    return 0


def _plate_key(t, base, cell, seed):
    """a plate texel: `base` may be a key or a function of the plate's centre (u, v) -> key"""
    kind, d, c = plates(t, cell, seed)
    return skin2.step(base(*c) if callable(base) else base, d)


def _rust(t, sex):
    """the male's display skin: the postorbital boss and, under it, the postorbital bar behind the eye flushed
    rust in a narrow VERTICAL streak that fades down the cheek (the female's stays the face's own)"""
    if sex != "male" or t.face not in ("east", "west"):
        return None
    dz = t.P[2] - EYE[0]; dy = t.P[1] - EYE[1]
    w = 1.3 - 0.12 * max(0.0, -dy)
    if 2.0 < dz < 2.0 + 2 * w and -5.0 < dy < 3.0:
        return "hr1" if (math.floor(t.P[1]) % 3) else "hr0"
    return None


def head_tone(t, sex):
    """the face: dark crown, middle cheek, pale jaw by height; big flat plates on the snout, smaller ones on the
    cranium and the jaw; a row of square labial scales on each lip; the mouth line dark and plain"""
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "b1"
    if n in ("jaw_back", "jaw_front"):
        if f == "up":
            return "k4"
        h = t.rel[1]
        if t.j == 0:
            return "k1"                       # the lower lip's edge under the teeth
        if t.j == 1:                          # the lower labial scales, square, a seam every third texel
            return "k2" if math.floor(t.P[2]) % 3 == 0 else "k5"
        base = "b1" if h < 0.3 else ("b2" if h < 0.55 else "k4")
        return _plate_key(t, base, 3.0, 33)
    if f == "up":
        if n in ("snout", "premax"):       # burnt-bone plates along the top of the snout, skin seams between
            kind, d, _c = plates(t, 3.2, 73)
            return "k1" if kind == "seam" else ("hb1", "hb2", "hb1", "hb0")[d + 1]
        return _plate_key(t, "k2", 2.8, 24)
    if n in ("snout", "premax"):
        if t.j == t.h - 1:
            return "k0"                       # the mouth line
        if t.j == t.h - 2:                    # the upper labial scales, square, staggered against the lower ones
            return "k3" if (math.floor(t.P[2]) + 1) % 3 == 0 else "k5"
        if t.rel[1] > 0.9:                    # the plates' burnt-bone edge down the top of the snout side
            kind, d, _c = plates(t, 3.2, 73)
            return "hb0" if kind == "seam" else "hb1"
    def base(pz, py):            # the plate's tone by the height of its centre: dark crown, middle cheek, light jaw
        hv = (py - HEAD_Y[0]) / max(1.0, HEAD_Y[1] - HEAD_Y[0])
        return ["k4", "k3", "k2"][skin2.bands(hv, pz * 2.0, (0.42, 0.74), amp=0.07, seed=31)]
    if n in ("cranium", "temporal") and f in ("east", "west"):
        r = _rust(t, sex)
        if r:
            return r
    if f in ("north", "south"):
        return _plate_key(t, base(t.P[2], t.P[1]), 3.4, 9)
    if n in ("snout", "premax"):
        return _plate_key(t, base, 4.4, 9)          # the big plates
    return _plate_key(t, base, 3.2, 32)              # smaller ones over the cranium


def teeth_up(t, p):
    """THICK, LONG teeth, D-shaped in section at the front (Russell 1970): two texels wide, the front one lit and the
    flat back one shaded, the lip's shadow over the root; uneven lengths, a gap where one was lost and the stub of
    the new one growing in it. Columns from the FRONT"""
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2] - t.cube["from"][2])); row = t.j
    for c0, wide, rows in ((0, 1, 2), (2, 2, 3), (5, 2, 3), (9, 1, 1), (11, 2, 2)):
        if c0 <= col < c0 + wide and row < rows:
            front = col == c0
            if row == 0:
                return p["tooth2"]                               # the root, in the lip's shadow
            if row == rows - 1 and rows > 2:
                return p["tooth"] if front else None             # the recurved tip: one texel
            return p["tooth"] if front else p["tooth2"]
    return None


def teeth_lo(t, p):
    """the lower row inside the snout: thick, every third column, two rows"""
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2] - t.cube["from"][2])); row = t.j
    if row == t.h - 1:
        return p["k1"]          # the jaw's inner lip: it shows at the front of the shut mouth, so skin, not gum
    if col % 3 in (0, 1) and row >= 1:
        return p["tooth"] if col % 3 == 0 else p["tooth2"]
    return None


def mouth_interior(img, C, p):
    """the deep narrow mouth: a dark palate with the sockets of the thick teeth along its rims, a narrow tongue"""
    for name in ("snout", "premax", "cranium"):
        u, v, ww, hh = C[name]["uv"]["down"]
        for j in range(hh):
            for i in range(ww):
                rim = i in (0, ww - 1)
                col = (p["tooth2"] if j % 3 == 0 else p["gum"]) if rim and name != "cranium" else p["mouth"]
                img[v + j, u + i] = (*col, 255)
    for name in ("jaw_front", "jaw_back"):
        u, v, ww, hh = C[name]["uv"]["up"]
        for j in range(hh):
            for i in range(ww):
                lip = i in (0, ww - 1) or (name == "jaw_front" and j >= hh - 2)   # shows when shut: skin
                img[v + j, u + i] = (*(p["k2"] if lip else (p["tongue"] if 1 < i < ww - 2 else p["mouth"])), 255)


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]; f = t.face; n = t.cube["name"]
        if mat in ("hide", "fur", "strap", "iron", "bone"):
            return saddle_px(t)
        if mat == "claw":
            return p["ker0"] if f != "up" else p["ker1"]
        if mat == "horn_base":  # the lacrimal horn's base: the face's plates running up into it
            if t.j >= t.h - 1 and f != "up":
                return p["k1"]
            return p[_plate_key(t, "k3" if f == "up" else "k2", 2.2, 70)]
        if mat == "horn":       # the tall lacrimal horn's tip: burnt bone, ridged up its front, the worn top pale
            if f == "up":
                return p["hb3"]
            if f == "north":
                return p["hb2"] if t.i % 2 else p["hb1"]
            return p["hb2"] if t.j == 0 else (p["hb0"] if t.i == 0 else p["hb1"])
        if mat == "boss":       # the postorbital boss: a ROUNDED knob of rugose bone (rust on the male), not a slab:
            hi, mid, lo = ("hr2", "hr1", "hr0") if sex == "male" else ("k4", "k3", "k2")
            if f == "up":       # lit only on its crown, the rim falling away into the skin, pitted
                if t.i in (0, t.w - 1) or t.j in (0, t.h - 1):
                    return p["k2"] if (t.i + t.j) % 2 else p[lo]
                return p[lo] if h32(t.i, t.j, 75) % 3 == 0 else p[hi]
            if t.j >= t.h - 1:
                return p["k1"]
            if t.i in (0, t.w - 1) and f in ("east", "west"):
                return p["k2"]                                   # its rounded front and back fall into shadow
            if h32(t.i, t.j, 74) % 3 == 0:
                return p[lo]                                     # a pit in the knob
            return p[mid]
        if mat == "brow":       # between horn and boss: the face's plates, a black underside over the eye
            if f == "down":
                return p["k0"]
            if f in ("east", "west") and t.j == t.h - 1:
                return p["k0"]
            return p[_plate_key(t, "k3", 2.4, 72)]
        if mat == "plate":      # the fused nasals: a ridge of burnt-bone plates
            kind, d, _c = plates(t, 2.4, 75)
            if f in ("up", "north"):
                return p["hb0"] if kind == "seam" else p["hb2" if d > 0 else "hb1"]
            return p["hb1"]
        if mat == "teeth":
            return teeth_up(t, p)
        if mat == "teeth_lo":
            return teeth_lo(t, p)
        if mat == "mouth":
            return p["gum"] if f in ("up", "down") else p["mouth"]
        if mat == "tongue":     # in shadow: its top shows in the seam of the shut mouth (the v2 "red thread"); the
            return p["mouth"] if f == "up" else p["k0"]     # pink floor of the open mouth is on the jaw's top
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
BRICK = (3, 8)           # the body's scale rows: height and length in texels (body change 0.20-0.30)
HEAD_Y = [0.0, 1.0]       # the lowest and highest point of the face at rest (the head's countershading)
EYE = [0.0, 0.0]          # rest-pose z and y of the eye's centre (the male's rust streak runs down behind it)

# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP
# THE EYE: an almond tilted forward-down in the top of a KEYHOLE orbit (the tyrannosaur orbit, narrowing into a slot
# below the eye), right behind the lacrimal horn; a blood-orange iris, a horizontal pupil, the glint at the back top
EYE_ART = [
    "Krrrr.",
    "rriigr",
    ".rIppr",
    "..rIr.",
    "..rr..",
    "..r...",
]
NOSTRIL = [      # an oval nostril at the front top of the snout, set in a burnt-bone plate
    "bbb",
    "nnb",
    "bnb",
]
SCARS = [        # the male's pale scars of old face bites, across the snout, lighter where the skin knitted
    "s.....",
    ".s...s",
    "..s.s.",
    "....s.",
]


def decals_for(sex):
    p = pal_for(sex)
    cm = {"r": p["k0"], "K": p["k1"], "g": p["glint"], "i": p["iris"], "I": p["iris2"], "p": p["pupil"],
          "n": p["k0"], "b": p["hb1"], "s": p["scar"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", EYE_ART, cm, at=(1, 5))
        P.stamp(img, m, C["premax"], "east", NOSTRIL, cm, at=(0, 1))
        if sex == "male":
            P.stamp(img, m, C["snout"], "east", SCARS, cm, at=(4, 3))
        mouth_interior(img, C, p)
    return dec


def paint_sex(m, sex="male"):
    PROF[0] = skin2.Profile(m, TRUNK | {"belly"})
    import geo
    pts = {c["name"]: q for c, q in geo.cube_points(m.spec())}
    ys = [pts[n][:, 1] for n in ("cranium", "snout", "premax")]
    HEAD_Y[:] = [min(a.min() for a in ys), max(a.max() for a in ys)]
    cr = pts["cranium"]
    # the eye: EYE_ART at column 1, rows 5-7 of the cranium's 15 (its centre about 3.5 px from the front, 6.5 down)
    EYE[:] = [float(cr[:, 2].min()) + 3.5, float(cr[:, 1].max()) - 6.5]
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
