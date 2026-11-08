"""Carcharodontosaurus saharicus, made by hand from its own study (docs/estudos/13_PREDADORES_1_10.md, approved by
Rodrigo on 07/11/2026). Real size 12.5 m (the neotype SGM-Din 1, Seebacher 2001; Henderson & Nicholls 2015; Paul 2016;
Rodrigo's answer: the same length as the Giganotosaurus, told apart by build).

The third rig of the 1.10.1 standard (docs/estudos/14_POR_QUE_PARECE_IA.md, "Decisões do Rodrigo"), the way the
Daspletosaurus pilot set it (art/daspletosaurus/PILOTO.md) and the Albertosaurus followed it:
- one texel = one Minecraft pixel: drawn at skin2.PX_PER_M (16.94 px per metre), shown at a model scale of ~1;
- the skin in BODY space (skin2): dark back, middle flank, pale belly as one shape from the snout to the tail tip, a
  calm base with soft blotches, scales only where they belong and the species' marks DRAWN as shapes;
- the detail stays, standardised.

Of C. saharicus the skull is well known and the body is not (Stromer's skeleton is now Tameryraptor, Kellermann et al.
2025): the body's proportions here come from its relatives (Giganotosaurus, Mapusaurus, Acrocanthosaurus) and are a
hypothesis. What makes it read as itself and NOT as the remade Giganotosaurus (study 13, the five separations):
1. the HEAD: a tall triangular skull in profile (~15% taller than the Giganotosaurus' for its length, the snout ~10%
   shorter), a deep maxilla sculpted in grooves (the genus' own trait, Sereno et al. 1996; Ibrahim et al. 2020), a
   SHELF of bone over the orbit (the "scowl" seen side-on; Chure 1998) and a marked NUCHAL CREST at the back; the
   Giganotosaurus has a low knife head with almost parallel jaws (Coria & Salgado 1995);
2. a thicker, shorter NECK carried lower and a DEEPER, heavier trunk (5 to 7 t against the lean Giganotosaurus);
3. a smooth tail deep at the base: no tall ridge of caudal spines;
4. it waits in ambush and bursts out (the animations; the Java in Carcharodontosaurine);
5. its own colour, a North-African sandstone: a warm sand and ochre-tan body (08/11/2026: the study's "arenito-malva"
   read as the Daspletosaurus' mauve-wine family from afar), the back darker in short broken vertical umber bars
   (mangrove shadows: the first drawn mark), a pale sand-grey belly, the brow, lacrimal and nuchal crest dark horn (the
   second) and the dark MASK behind the eye, black on the male, lead grey on the female (the third).
"""
import math

import proto as P
import skin
import skin2
from proto import hx, h32

TEX_W = 256
PX_M = skin2.PX_PER_M

# ------------------------------------------------------------------ palette
# k0..k5 the body ramp (the warm sand and ochre-tan of the Kem Kem sandstone, shadows to umber), b0..b3 the pale belly,
# hn the dark horn of the brow and crest, mk the mask behind the eye
SCHEME = {
    "k0": "30281a", "k1": "4f3b22", "k2": "69582a", "k3": "806b33", "k4": "927c46", "k5": "a48e5e",
    "b0": "938b7a", "b1": "a39a89", "b2": "b3aa99", "b3": "c1b8a6",
    "hn0": "211c16", "hn1": "342c24", "hn2": "4d4337",
    "mk": "1f1a15", "lip": "9a907c", "scar": "d8cfbd", "rd0": "7e3324", "rd1": "a3452c", "rd2": "bd5a36",
    "female": {"k1": "57422a", "k2": "715f31", "k3": "88723a", "k4": "9a844e", "k5": "ac9665",
               "b0": "9b9282", "b1": "aba291", "b2": "bcb2a1", "mk": "4a443b",
               "rd0": "6a4a32", "rd1": "7d5a3c", "rd2": "8e6a48"},
}
PAL = {
    "ker0": hx("1e1a18"), "ker1": hx("362e2a"), "ker2": hx("cfc4a8"), "ker3": hx("a09276"),
    "iris": hx("c9cdb4"), "iris2": hx("8f9886"), "pupil": hx("0f0b0c"), "lid": hx("130f0c"), "glint": hx("f6efd8"),
    "gum": hx("7a3a3e"), "mouth": hx("3a1b20"), "tongue": hx("9c5250"), "tooth": hx("f2ecd8"), "tooth2": hx("cdbf9c"), "tooth3": hx("8a7656"),
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


TOP_ROT = (-12, 0, 0)       # the top of the snout falls steeply from the brow to the tip: the triangular profile


def head(m, parent, hy, hz, rest=(-4, 0, 0)):
    """the tall triangular skull and the deep jaw. (hy, hz): the mouth line at the back of the skull; returns the
    skull. The profile is two pieces: a deep level MAXILLA (the bottom line straight, the sculpted side) and the top
    of the snout tilted down over it, so from the side the head is a triangle and not a box"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    sk = m.bone("skull", parent, (0, hy + 6, hz), rest)
    so = (0, hy + 12, hz - 11)              # the top of the snout hinges at the front of the cranium
    m.cube(sk, *B(-5, 0, -11, 5, 13, 0), name="cranium")
    m.cube(sk, *B(-4.5, 4, 0, 4.5, 12, 2), name="occiput")
    # the nuchal crest: a raised ridge across the back of the skull roof, set back over the occiput
    m.cube(sk, *B(-3.5, 12, -2, 3.5, 15, 3), name="nuchal", mat="crest")
    m.pair(sk, sk, *B(5, 1, -5.5, 6, 8, -0.5), name="temporal")          # the jaw muscle behind the eye
    # the brow SHELF over the orbits: a bar across the roof that juts 2 px forward of the cranium, and its sides that
    # stand out over each eye (the scowl)
    # (padrão v2: they grow out of the skull, the face's skin on their sides, the male's red display skin over the
    # eye, dark horn only along the shelf's rim and the crest's top)
    m.cube(sk, *B(-4, 13, -13, 4, 14, -6), name="brow", mat="crest")
    m.pair(sk, sk, *B(4, 11, -13, 6, 14, -6), name="brow_side", mat="brow")
    m.cube(sk, *B(-4, 0, -25, 4, 8, -11), name="maxilla")
    m.cube(sk, *B(-3, 5, -23, 3, 12, -11), name="snout", rot=TOP_ROT, origin=so)
    m.cube(sk, *B(-3, 0, -28, 3, 7, -25), name="premax")
    m.cube(sk, *B(-1.5, 12, -21, 1.5, 13, -12), name="nasal", mat="plate", rot=TOP_ROT, origin=so)   # rugose nasals
    jaw = m.bone("jaw", sk, (0, hy + 1, hz - 2))
    m.cube(jaw, *B(-4.5, -6, -11, 4.5, 0, 0), name="jaw_back")
    m.cube(jaw, *B(-3.5, -5, -27, 3.5, 0, -11), name="jaw_front", rot=(-2, 0, 0), origin=(0, hy, hz - 11))
    m.cube(jaw, *B(-3.5, -7.5, -13, 3.5, -5.5, -3), name="gular", mat="gular")
    m.cube(jaw, *B(-4, -1, -8, 4, 2, -1), name="cheek", mat="mouth")
    m.cube(jaw, *B(-1.5, -2, -24, 1.5, 1, -7), name="tongue", mat="tongue")
    m.cube(sk, *B(-1, -1, -26, 1, 2, -12), name="palate", mat="mouth")
    # the blade teeth (14 a side, Sereno et al. 1996: "shark-toothed") as alpha planes. Padrão v2: the upper row
    # hangs just OUTSIDE the jaw (3.75 > 3.5) under the maxilla's lip (4), four rows deep (padrão v3: the biggest
    # teeth of the four): with the mouth shut the long blades show
    # over the jaw, the lips covering only their base; the lower one inside the maxilla
    m.pair(sk, sk, *B(3.75, -4, -25, 3.75, 0, -11), name="teeth_up", mat="teeth")
    m.pair(jaw, jaw, *B(2.5, -1, -26, 2.5, 2, -11), name="teeth_lo", mat="teeth_lo")
    return sk


REST = {   # bone rest angles (x: + = far end up for the neck and tail, knee forward for the thigh)
    "neck1": 18, "neck2": 4, "skull": -20, "thigh": 20, "shin": -48, "foot": 40, "toes": -12,
    "arm": 20, "forearm": -68, "tail1": -5, "tail2": 2, "tail3": 1.5, "tail4": 0.5, "tail5": 0,
}
HIP_Y = 56


def legs(m, body):
    """heavy legs of a 6 t animal: a thick drumstick into the hip, a deep calf, a shorter metatarsus than the
    tyrannosaurids', a broad foot of three toes wider than the shin, the small first toe off the ground"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (9 * sx, HIP_Y, 0), (REST["thigh"], 0, 4 * sx))
        sh = m.bone(f"shin_{side}", th, (9 * sx, 32, 0), (REST["shin"], 0, -8 * sx))
        ft = m.bone(f"foot_{side}", sh, (9 * sx, 13, 0), (REST["foot"], 0, 4 * sx))
        m.bone(f"toes_{side}", ft, (9 * sx, -1, 0), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (3, 42, -12), (16, 68, 11), name="thigh")
    m.pair("thigh_l", "thigh_r", (4, 33, -9), (15, 45, 8), name="thigh_low")
    m.pair("thigh_l", "thigh_r", (5, 28, -6), (13, 36, 5), name="knee")
    m.pair("shin_l", "shin_r", (5, 19, -6), (13, 34, 4), name="calf")
    m.pair("shin_l", "shin_r", (5.5, 10, -4), (12.5, 20, 3), name="shin")
    m.pair("foot_l", "foot_r", (6.5, -2, -3), (11.5, 14, 3), name="meta")
    m.pair("toes_l", "toes_r", (7.5, -3, -15), (10.5, 0, 0), name="toe_mid")
    m.pair("toes_l", "toes_r", (10.5, -3, -12), (13.5, 0, -1), name="toe_out")
    m.pair("toes_l", "toes_r", (4.5, -3, -12), (7.5, 0, -1), name="toe_in")
    m.pair("toes_l", "toes_r", (8.5, -3, -17), (9.5, -1, -15), name="claw_mid", mat="claw")
    m.pair("toes_l", "toes_r", (11.5, -3, -14), (12.5, -1, -12), name="claw_out", mat="claw")
    m.pair("toes_l", "toes_r", (5, -3, -14), (6, -1, -12), name="claw_in", mat="claw")
    m.pair("foot_l", "foot_r", (5, 4, 2), (7, 6, 5), name="hallux")


def arms(m, body):
    """small arms of three fingers (the carcharodontosaurids kept three), an upper arm of 8 px, a forearm of 5"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (10 * sx, 42, -46), (REST["arm"], 0, -6 * sx))
        m.bone(f"forearm_{side}", a, (10 * sx, 35, -46), (REST["forearm"], 0, 0))
    m.pair("arm_l", "arm_r", (8.5, 34, -47.5), (11.5, 42, -44.5), name="arm")
    m.pair("forearm_l", "forearm_r", (8.5, 30, -47), (11.5, 35, -45), name="forearm")
    m.pair("forearm_l", "forearm_r", (8.5, 28, -47), (11.5, 30, -45), name="hand")
    m.pair("forearm_l", "forearm_r", (10.5, 26, -47), (11.5, 28, -46), name="claw_f1", mat="claw")
    m.pair("forearm_l", "forearm_r", (9.5, 26.5, -46), (10.5, 28.5, -45), name="claw_f2", mat="claw")
    m.pair("forearm_l", "forearm_r", (8.5, 26, -47), (9.5, 28, -46), name="claw_f3", mat="claw")


TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5")


def tail(m, body):
    """long, smooth and DEEP at the base (the caudofemoral muscle and the chevrons), no ridge of tall spines on top
    (the Giganotosaurus' mark); each segment starts 2 px inside the one before, none repeats another's size"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 8, 38, 8, 42, 66), ("tail2", 36, 62, 6, 46, 62), ("tail3", 60, 82, 4.5, 49, 59),
        ("tail4", 80, 98, 3, 51, 57), ("tail5", 96, 112, 1.5, 52.5, 55.5)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-5.5, 37, 6), (5.5, 43, 30), name="tail_muscle")     # the deep base under the tail


SADDLE_PAL = {   # undyed woven wool, oiled hide and bone: the saddle of the river plains (its own)
    "L0": hx("2b1d16"), "L1": hx("46301f"), "L2": hx("62452c"), "L3": hx("7d5c3a"), "L4": hx("97744b"),
    "F0": hx("6e6250"), "F1": hx("958670"), "F2": hx("b3a58c"), "F3": hx("5a3c34"),
    "I0": hx("4a4a48"), "I1": hx("787874"), "I2": hx("a4a49c"), "B0": hx("b9aa88"), "B1": hx("ddd0b0"),
    "R0": hx("6b5a3e"), "R1": hx("8d7a56"),
}


def saddle(m, body):
    """The river-plain saddle: a woven blanket of undyed wool with a darker border laid over the withers, a deep hide
    seat with a high pommel to brace on when it bursts out of the ambush, rope girths, a rope breast collar tied with
    a bone toggle, and stirrups of bone. Faces lying on the body are left out (no back-face culling in GeckoLib)."""
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    sd = m.bone("saddle", body, (0, 71, -24))
    m.cube(sd, (-9.5, 69, -38), (9.5, 71, -12), name="pad", mat="fur", faces=out("down"))
    m.pair(sd, sd, (10, 58, -36), (11, 69, -22), name="flap_f", mat="fur", faces=out("east", "up"))
    m.cube(sd, (-6.5, 71, -34), (6.5, 73, -16), name="seat", mat="hide", faces=out("down"))
    m.cube(sd, (-4, 73, -34), (4, 77, -31), name="pommel", mat="hide")
    m.cube(sd, (-6, 73, -19), (6, 76, -16), name="cantle", mat="hide")
    m.pair(sd, sd, (11, 51, -30), (12, 68, -29), name="leather", mat="strap", faces=out("east", "up"))
    m.pair(sd, sd, (11, 48, -31), (14, 51, -30), name="stir_f", mat="bone")
    m.pair(sd, sd, (11, 48, -29), (14, 51, -28), name="stir_b", mat="bone")
    m.pair(sd, sd, (11, 47, -31), (14, 48, -28), name="stir_t", mat="bone")
    # the rope girth, down the flank under the blanket and across the belly
    m.pair(sd, sd, (10.5, 36, -26), (11.5, 58, -24), name="girth", mat="rope", faces=out("east", "up"))
    m.cube(sd, (-8.5, 29, -26), (8.5, 30, -24), name="girth_under", mat="rope", faces=out("up"))
    m.pair(sd, sd, (8.5, 29, -26), (10.5, 36, -24), name="girth_low", mat="rope", faces=out("east"))
    # the rope breast collar round the base of the neck, the bone toggle on the left
    m.pair(sd, sd, (9, 44, -52), (10, 63, -50), name="breast", mat="rope", faces=out("east"))
    m.cube(sd, (10, 52, -53), (11, 55, -49), name="toggle", mat="bone")


def saddle_px(t):
    mat = t.cube["mat"]; n = t.cube["name"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "fur":            # the woven blanket: plain weave, a dark border woven in two rows from the edge
        if f == "up":
            edge = min(i, w - 1 - i, j, h - 1 - j)
            if edge == 1:
                return p["F3"]
            return p["F2"] if (i + j) % 2 == 0 and h32(i, j, 33) % 100 < 30 else p["F1"]
        if j == h - 2:
            return p["F3"]
        if j == h - 1:
            return p["F0"]
        return p["F2"] if (i + j) % 2 == 0 and h32(i, j, 34) % 100 < 25 else p["F1"]
    if mat == "rope":           # twisted fibre: a diagonal lay
        return p["R1"] if (i + j) % 3 == 0 else p["R0"]
    if mat == "iron":
        return p["I2"] if f == "up" else (p["I0"] if j == h - 1 and h > 1 else p["I1"])
    if mat == "bone":
        return p["B1"] if f == "up" or j == 0 else p["B0"]
    if mat == "strap":
        if f in ("up", "down"):
            return p["L1"] if f == "down" else p["L2"]
        return p["L1"] if j == h - 1 else p["L2"]
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
    m = P.Model("carcharodontosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, HIP_Y, 0))
    # the trunk: deep and heavy (5 to 7 t), the deep chest well below the hips, the belly line rising to the hips
    m.cube(body, (-9, 32, -54), (9, 62, -38), name="chest")
    m.cube(body, (-6, 28, -52), (6, 33, -38), name="keel")
    m.cube(body, (-10.5, 34, -40), (10.5, 67, -8), name="torso")
    m.cube(body, (-8.5, 30, -39), (8.5, 35, -12), name="belly", mat="belly")
    m.cube(body, (-9.5, 44, -10), (9.5, 68, 12), name="hips")
    m.cube(body, (-6, 66, -44), (6, 69, -6), name="back")
    # the neck: thick and short, carried low (the rest angles); every segment starts inside the one behind
    n1 = m.bone("neck1", body, (0, 54, -52), (REST["neck1"], 0, 0))
    m.cube(n1, (-8, 40, -60), (8, 64, -48), name="shoulders")
    m.cube(n1, (-7, 43, -70), (7, 63, -58), name="neck1")
    n2 = m.bone("neck2", n1, (0, 54, -68), (REST["neck2"], 0, 0))
    m.cube(n2, (-6.5, 45, -78), (6.5, 62, -66), name="neck2")
    m.cube(n2, (-5, 41, -78), (5, 46, -67), name="throat")
    hd = m.bone("head", n2, (0, 53, -76))
    head(m, hd, 46, -76, rest=(REST["skull"], 0, 0))
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
HEAD = {"cranium", "occiput", "temporal", "maxilla", "snout", "premax", "jaw_back", "jaw_front"}

# THE MARKS (drawn, not drawn by lot):
# 1. short BROKEN VERTICAL BARS down the back and the upper flank, from the shoulders to the tail (the shade of the
#    mangrove): z centre, half width; each bar reaches down to a height of its own and is torn at its lower end;
# 2. the dark horn of the brow shelf, the lacrimal and the nuchal crest (materials);
# 3. the dark MASK from the eye back over the temporal to the jaw joint, black on the male, lead grey on the female.
BARS = [(-60, 1.6, 0.66), (-50, 2.0, 0.60), (-40, 2.2, 0.62), (-30, 2.0, 0.56), (-20, 2.2, 0.60), (-9, 2.0, 0.58),
        (2, 2.2, 0.62), (13, 2.0, 0.60), (25, 2.0, 0.62), (37, 1.8, 0.64), (49, 1.8, 0.66), (61, 1.6, 0.70),
        (73, 1.4, 0.72), (85, 1.2, 0.74), (96, 1.0, 0.78)]


def body_tone(t, prof, sex):
    """the palette key of a body texel: the countershading by the silhouette, the bars, the blotches"""
    n = t.cube["name"]; f = t.face
    z, y = t.P[2], t.P[1]
    if f == "down" or n in ("belly", "keel", "tail_muscle"):
        h = 0.0 if f == "down" else min(0.17, prof.height(t))
    elif f == "up":
        h = 1.0
    else:
        h = prof.height(t)
    b = skin2.bands(h, z, (0.20, 0.28, 0.50, 0.78), amp=0.04, seed=2)
    if b == 0:
        u, v = skin2.surface_uv(t)
        k = skin.scutes(u, v, row=3, width=6)
        return {"seam": "b0", "hi": "b2", "base": "b1"}[k]
    base = ["b1", "b0", "k4", "k3", "k2"][b]
    # the broken vertical bars, from the spine down to their own depth; the lower end torn by a soft field
    for k, (zc, half, low) in enumerate(BARS):
        edge = half + 0.5 * math.sin(y * 0.5 + k * 1.9)
        if abs(z - zc) < edge and h > low:
            torn = h < low + 0.12 and skin2.soft(*skin2.surface_uv(t), 2.5, seed=40 + k) < 0.45
            gap = skin2.soft(*skin2.surface_uv(t), 3.0, seed=60 + k) < 0.18     # a break in the bar
            if not torn and not gap:
                return "k1" if b >= 3 else "k2"
    if b >= 2:
        base = skin2.step(base, skin2.mottle(t, cell=11, strength=0.2, seed=3))
        # padrão v3: the body's own motif, long low FOLDS of skin along the flank (the face's grooves, calmer)
        base = skin2.step(base, folds(t, seed=4))
    return base


def limb_tone(t):
    """legs and arms: calm, lit on the front, a step darker behind and below; scutes across the front of the
    metatarsus and the toes"""
    n = t.cube["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    v = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    if n in ("thigh", "thigh_low", "knee"):
        base = "k3"
        if f in ("east", "west") and t.rel[2] > 0.55 and v < 0.45:
            base = "k2"
        if f in ("east", "west", "north") and t.rel[2] < 0.3 and 0.35 < v < 0.8:
            base = "k4"
        if f in ("east", "west") and v > 0.86:
            base = "k2"
        if f == "south" or f == "down":
            base = "k2"
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


# ------------------------------------------------------------------ padrão v3: the Carcharodontosaurus' own head
# (docs/estudos/14, "Padrão v3": the engine only measures, every part below is drawn for this animal alone)
#
# THE MOTIF: GROOVES. The maxilla of the genus is sculpted in long grooves (Sereno et al. 1996; Ibrahim et al. 2020):
# long wavy horizontal grooves along the snout and the jaw, each a dark line with the ridge over it lit, broken now
# and then; on the body the skin lies in long low FOLDS along the flank and the neck, wider apart and one step deep.
def grooves(t, spacing=3.0, seed=0, broken=0.22):
    """-1 in a groove, +1 on the ridge just above it, 0 between. The grooves run along the head (z) in short wavy
    runs, as sculpted bone does: each run steps up or down a texel every few texels and breaks off now and then"""
    u, v = skin2.surface_uv(t)
    if t.face in ("up", "down"):
        u, v = t.P[2], t.P[0]
    iu = math.floor(u)
    w = v + 0.9 * math.sin(u * 0.62 + seed) + 0.4 * math.sin(u * 1.37 + 2 * seed)
    k = math.floor(w) % int(spacing) if spacing >= 2 else 0
    if (iu + h32(math.floor(w) // int(spacing), seed, 7)) % 6 == 0:
        return 0                                        # the end of a run
    if skin2.soft(u, v, 4.0, seed + 90) < broken:
        return 0
    if k == 0:
        return -1
    if k == 1:
        return 1
    return 0


def folds(t, seed=0):
    """-1 on the long low skin folds of the flank and neck: creases slanting down and back (as skin hangs from the
    spine of a heavy animal), every fourth texel, waving and broken; else 0"""
    u, v = skin2.surface_uv(t)
    w = v + 0.45 * u + 1.1 * math.sin(u * 0.17 + seed)
    if math.floor(w) % 4:
        return 0
    return -1 if skin2.soft(u, v, 6.0, seed) > 0.3 else 0


def _display(t, sex):
    """the male's display skin: a thin brick-red EDGE along the top of the dark mask, from behind the eye back to the
    jaw joint (a line, not a patch), the female has none"""
    if sex != "male":
        return None
    zc = t.P[2] - EYE_Z[0]
    yb = EYE_Z[1] - 0.30 * zc
    top = yb + 1.4 + 0.12 * zc
    if zc > 3.0 and top <= t.P[1] < top + 1.0:
        return "rd1" if math.floor(t.P[2]) % 4 else "rd2"
    return None


def head_tone(t, sex):
    """the face: pale cheek, darker crown by height; the GROOVES along the deep maxilla and the jaw, finer on the jaw;
    the dark MASK behind the eye with the male's red edge; no light lip: the grooves run into a dark mouth line"""
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "b1"
    if n in ("jaw_back", "jaw_front"):
        if f == "up":
            return "k4"
        h = t.rel[1]
        if t.j == 0:
            return "k1"
        # the jaw's upper half dark tan behind the blades (the pale throat starts lower), so the teeth stand out
        base = "b1" if h < 0.25 else ("b2" if h < 0.4 else ("k3" if h < 0.7 else "k2"))
        return skin2.step(base, grooves(t, 3.0, 33, broken=0.3))
    if f == "up":
        return skin2.step("k3", grooves(t, 3.0, 21, broken=0.35))
    if n in ("maxilla", "premax") and t.j == t.h - 1:
        return "k0"                           # the mouth line
    hv = (t.P[1] - HEAD_Y[0]) / max(1.0, HEAD_Y[1] - HEAD_Y[0])
    base = ["k5", "k4", "k3"][skin2.bands(hv, t.P[2] * 2.0, (0.36, 0.70), amp=0.07, seed=31)]
    if n in ("cranium", "temporal", "occiput") and f in ("east", "west"):
        zc = t.P[2] - EYE_Z[0]
        yb = EYE_Z[1] - 0.30 * zc                          # it slopes down toward the jaw joint
        if zc > 1.0 and abs(t.P[1] - yb) < 1.4 + 0.12 * zc and t.rel[1] > 0.15:
            return "mk" if grooves(t, 2.0, 35, broken=0.5) >= 0 else "k1"
        d = _display(t, sex)
        if d:
            return d
    if n in ("maxilla", "premax", "snout"):
        return skin2.step(base, grooves(t, 3.0, 9, broken=0.18))
    return skin2.step(base, grooves(t, 4.0, 32, broken=0.4))


def teeth_up(t, p):
    """THE SHARK TEETH: wide, flat, serrated blades, clearly bigger than any tyrannosaur's (6.5 cm crowns, Sereno et
    al. 1996): three texels wide at the root, narrowing to a point raked BACK, the front edge lit, the flat blade
    between, the back edge notched by the serrations (a darker texel every other row); four rows deep. Columns from
    the FRONT: three big blades and a smaller one at the back"""
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2] - t.cube["from"][2])); row = t.j
    for c0, rows in ((0, 4), (4, 4), (8, 4), (12, 3)):
        k = col - c0
        if not 0 <= k < 3 or row >= rows:
            continue
        lo = 0 if row < rows - 2 else (1 if row == rows - 2 else 2)        # the blade narrows toward the back
        if k < lo:
            return None
        if row == 0:
            return p["tooth2"]                                          # the root, under the lip
        if k == lo:
            return p["tooth"]                                           # the lit front edge
        if k == 2:
            return p["tooth3"] if row % 2 else p["tooth2"]              # the serrated back edge
        return p["tooth"] if row == 1 else p["tooth2"]
    return None


def teeth_lo(t, p):
    """the lower blades inside the jaw, smaller"""
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2] - t.cube["from"][2])); row = t.j
    if row == t.h - 1:
        return p["k1"]          # the jaw's inner lip: it shows at the front of the shut mouth, so skin, not gum
    k = col % 4
    if row >= 1 and k < 2:
        return p["tooth"] if k == 0 else p["tooth3"]
    return None


def mouth_interior(img, C, p):
    """the deep mouth: the palate gum-red with the sockets of the blades along the rims (a tooth every fourth),
    the floor dark with a broad tongue"""
    for name in ("maxilla", "premax", "cranium"):
        u, v, ww, hh = C[name]["uv"]["down"]
        for j in range(hh):
            for i in range(ww):
                rim = i in (0, ww - 1) and name != "cranium"
                col = (p["tooth2"] if j % 4 == 0 else p["mouth"]) if rim else p["gum"]
                img[v + j, u + i] = (*col, 255)
    for name in ("jaw_front", "jaw_back"):
        u, v, ww, hh = C[name]["uv"]["up"]
        for j in range(hh):
            for i in range(ww):
                rim = i in (0, ww - 1) or (name == "jaw_front" and j >= hh - 2)    # shows when shut: skin
                img[v + j, u + i] = (*(p["k1"] if rim else p["tongue"]), 255)


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]; f = t.face; n = t.cube["name"]
        if mat in ("hide", "fur", "strap", "iron", "bone", "rope"):
            return saddle_px(t)
        if mat == "claw":
            return p["ker0"] if f != "up" else p["ker1"]
        if mat == "crest":      # the brow shelf's top and the nuchal crest: grooved skin sides, a rim of dark horn
            if f == "up":
                return p["hn2"] if h32(t.i, t.j, 5) % 3 else p["hn1"]
            if t.j == 0:
                return p["hn1"]
            if sex == "male" and n == "nuchal" and f in ("east", "west", "south"):
                # the male's display skin on the crest: red between VERTICAL ribs of horn
                return p["hn1"] if t.i % 3 == 0 else (p["rd2"] if t.j == 1 else p["rd1"])
            return p[skin2.step("k3", grooves(t, 2.0, 79, broken=0.3))]
        if mat == "brow":       # the shelf's sides over each eye: the scowl, grooved, black underneath
            if f == "up":
                return p["hn2"] if h32(t.i, t.j, 6) % 3 else p["hn1"]
            if f == "down":
                return p["k0"]
            if t.j == t.h - 1:
                return p["mk"]
            if t.j == 0:
                return p["hn2"]
            return p[skin2.step("k4", grooves(t, 2.0, 80, broken=0.2))]
        if mat == "plate":      # the rugose nasals: a ridge with a groove down each side
            if f in ("up", "north"):
                return p["k2"] if t.i in (0, t.w - 1) else p["k4"]
            return p["k2"]
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
HEAD_Y = [0.0, 1.0]       # the lowest and highest point of the face at rest (the head's countershading)
EYE_Z = [0.0, 0.0]        # rest-pose z and y of the eye (the mask starts there)

# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP
# THE EYE: SMALL, sunk under the brow shelf (the shelf's black underside is its lid), a pale cold iris, the pupil at
# the FRONT of it (it looks forward and down from under the scowl), the glint at the back; the dark mask runs straight
# on from it
EYE_ART = [
    "rrrmmmm",
    "rpigmmm",
    "rIIrmm.",
    ".rrm...",
]
NOSTRIL = [      # a narrow nostril on the snout tip, the grooves running into it
    "nn.",
    ".nn",
]


def decals_for(sex):
    p = pal_for(sex)
    cm = {"r": p["k0"], "m": p["mk"], "g": p["glint"], "i": p["iris"], "I": p["iris2"], "p": p["pupil"],
          "n": p["k0"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", EYE_ART, cm, at=(1, 3))
        P.stamp(img, m, C["premax"], "east", NOSTRIL, cm, at=(0, 1))
        mouth_interior(img, C, p)
    return dec


def paint_sex(m, sex="male"):
    PROF[0] = skin2.Profile(m, TRUNK | {"belly"})
    import geo
    pts = {c["name"]: q for c, q in geo.cube_points(m.spec())}
    ys = [pts[n][:, 1] for n in ("cranium", "maxilla", "premax")]
    HEAD_Y[:] = [min(a.min() for a in ys), max(a.max() for a in ys)]
    cr = pts["cranium"]
    # the eye: EYE_ART at column 1, rows 3-5 of the cranium's 13 (its centre 2.5 px from the front, 4 down)
    EYE_Z[:] = [float(cr[:, 2].min()) + 2.5, float(cr[:, 1].max()) - 4.0]
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
