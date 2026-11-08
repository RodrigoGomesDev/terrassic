"""Majungasaurus crenatissimus, made by hand from its own study (docs/estudos/13_PREDADORES_1_10.md, approved by
Rodrigo on 07/11/2026). Real size 8 m (the top without the 2025 material: Sampson & Witmer 2007, the bigger
fragments; Rodrigo's answer: 8 m).

The fourth and last rig of the 1.10.1 standard (docs/estudos/14_POR_QUE_PARECE_IA.md, "Decisões do Rodrigo"), the way
the Daspletosaurus pilot set it (art/daspletosaurus/PILOTO.md) and the Albertosaurus and Carcharodontosaurus followed:
- one texel = one Minecraft pixel: drawn at skin2.PX_PER_M (16.94 px per metre), shown at a model scale of ~1;
- the skin in BODY space (skin2): dark back, middle flank, pale belly as one shape from the snout to the tail tip, a
  calm base with soft blotches, scales only where they belong and the species' marks DRAWN as shapes;
- the detail stays, standardised.

What makes it read as itself and NOT as the remade Carnotaurus, its cousin (study 13, "Diferente do Carnotauro"):
1. the HEAD: short, deep and BROAD (wider than any other abelisaurid's, Sampson & Witmer 2007), thick fused rugose
   nasals and ONE dome on the fused frontals over the eyes (hollow, sinus-filled, keratin-covered in life); no horns
   over the eyes. The dome is the shape it is known by, drawn ~25% bigger than the bone (study 14, C);
2. SHORT thick legs (a tibia stouter than the Carnotaurus', Carrano 2007) with a short metatarsus: the line of the back
   sits ~18% lower for its length than the Carnotaurus' (0.29 against 0.35), a bulldog of a theropod with a low
   centre of gravity;
3. a stocky, broad trunk and tiny stub arms (Burch & Carrano 2012: probably immobile, maybe clawless): two nubs;
4. it bites and HOLDS (the animations and the Java in Majungasaurine), it does not ram;
5. its own colour, "cinza-basalto": a dusky blue-grey of the dry Maevarano mud (the study's dry sage was green, and the
   T. rex and the Albertosaurus already hold the greens), the back crossed by BROAD ragged dark bands that ring the
   tail (the first drawn mark), on the male the bare skin of the rugose brow and behind the eye dull ochre-orange
   (the second; padrão v2, 08/11/2026: the dome stays the skull's own skin with a worn pale crown, since ochre round
   or under it read as a hat), and a pale stripe from the corner of the mouth down the side of the neck (the third).
   The belly is a pale warm grey.
"""
import math

import proto as P
import skin
import skin2
from proto import hx, h32

TEX_W = 256
PX_M = skin2.PX_PER_M

# ------------------------------------------------------------------ palette
# k0..k5 the body ramp (the dusky blue-grey of dry Maevarano mud, shadows to slate), b0..b3 the pale warm-grey belly,
# hn the dark horn of the dome and the nasals, oc the bare skin round the male's dome, st the pale neck stripe
SCHEME = {
    "k0": "0e1f2c", "k1": "142f41", "k2": "223e53", "k3": "334e63", "k4": "465f73", "k5": "5a7081",
    "b0": "727b82", "b1": "7f878f", "b2": "8c949c", "b3": "99a2a9",
    "hn0": "1f1b1a", "hn1": "34302c", "hn2": "4c463f",
    "oc0": "8a5a30", "oc1": "a8723c", "oc2": "c4843a", "st": "919aa1", "lip": "737d86",
    # padrão v3.1: the BONE greys of the rugose roof, nasals, brow and dome (the skull lit from above, lighter than
    # the face's sides; the same blue-grey family, a little warmer and paler toward the knobs)
    "bn0": "6c7d8b", "bn1": "8696a2", "bn2": "a6b1b8",
    "female": {"k1": "163143", "k2": "254055", "k3": "365066", "k4": "486175", "k5": "5d7283",
               "b0": "757d84", "b1": "828a91", "b2": "8e979f", "oc0": "4a4440", "oc1": "5c5650",
               "oc2": "6e665c"},
}
PAL = {
    "ker0": hx("1e1a18"), "ker1": hx("362e2a"), "ker2": hx("cfc4a8"), "ker3": hx("a09276"),
    "iris": hx("b4c65a"), "iris2": hx("74903c"), "iris3": hx("c09a44"), "pupil": hx("0f0b0c"), "lid": hx("120f14"), "glint": hx("f2ead2"),
    "gum": hx("7a3a3e"), "mouth": hx("3a1b20"), "tongue": hx("9c5250"), "tooth": hx("eee6cf"), "tooth2": hx("c6b796"),
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


DOME_ROT = (-10, 0, 0)      # the dome leans forward off the skull roof
TOP_ROT = (-8, 0, 0)        # the top of the snout falls gently to the blunt tip (a short deep box, not a wedge)


def head(m, parent, hy, hz, rest=(-4, 0, 0)):
    """the short, deep, BROAD skull and the deep jaw. (hy, hz): the mouth line at the back of the skull; returns the
    skull. 16 px from the occiput to the blunt snout (0.95 m drawn against ~0.7 m: the head is the signature), 11 px
    wide at the cranium.

    Padrão v2 (study 14, 08/11/2026): the single DOME grows out of the skull roof (two low swellings in the skin's
    own colour and only a small keratin cap, no plate under it: the v1 read as a hat on a brown plate), a rugose BROW
    over the eye socket, the thick rugose nasals as a broad knobbed ridge, and the upper teeth hung just outside the
    lower jaw so the row shows with the mouth shut, the lips covering only their base"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    sk = m.bone("skull", parent, (0, hy + 5, hz), rest)
    so = (0, hy + 10, hz - 7)               # the top of the snout hinges at the front of the cranium
    m.cube(sk, *B(-5.5, 0, -7, 5.5, 10, 0), name="cranium")
    m.cube(sk, *B(-4.5, 3, 0, 4.5, 9, 2), name="occiput")
    m.pair(sk, sk, *B(5.5, 1, -3, 6.5, 6, 0), name="temporal")           # the jaw muscle bulging behind the eye
    # the rugose brow over the eye: a ridge of the postorbital and lacrimal standing out of the cranium's side, its
    # front jutting past the cranium over the socket
    # padrão v3.1: a HEAVY overhang, a full px out past the cranium and a px forward of it, so its dark underside
    # roofs the eye like a hood (the eye sits in its shadow, deep-set)
    m.pair(sk, sk, *B(5, 7.5, -8, 7, 10.5, -2), name="brow", mat="brow")
    # THE DOME: one rounded knob on the fused frontals, over and just behind the eyes (no brow horns), rising out of
    # the roof in two swellings of skin and a small keratin cap; each starts inside the one under it
    # it leans forward a little (the knob's front slope runs on from the nasal ridge), so it is not a stack of level
    # boxes on a level roof
    # padrão v3.1: the knob is FOUR thin layers of 1 to 1.5 px, each starting half a px inside the one under it and
    # half a px to 1.5 px shorter at each end, so the silhouette from the side and in 3/4 is a low rounded hump (a
    # pixel-art arc: long runs at the foot, short at the crown) and not a stair of boxes; all of it the skull's own
    # rugose bone, the crown its palest knobs (no keratin lid)
    do = (0, hy + 10, hz - 4)
    for k, (w, y0, y1, z0, z1) in enumerate(((4.0, 9.0, 11.0, -11.0, 0.0), (3.5, 10.0, 12.0, -9.0, -1.0),
                                              (3.0, 11.0, 13.0, -8.0, -2.0), (2.0, 12.5, 13.5, -7.0, -3.0))):
        m.cube(sk, *B(-w, y0, z0, w, y1, z1), name=("dome_base", "dome", "dome_top", "dome_cap")[k], mat="dome",
               rot=DOME_ROT, origin=do)
    m.cube(sk, *B(-4.5, 0, -14, 4.5, 7, -7), name="maxilla")              # the broad, blunt snout
    m.cube(sk, *B(-3.5, 5, -14, 3.5, 10, -7), name="snout", rot=TOP_ROT, origin=so)
    m.cube(sk, *B(-3.5, 0, -16, 3.5, 6, -14), name="premax")
    # the thick fused nasals, rugose and sculpted (keratin in life): a broad knobbed ridge along the top of the snout
    m.cube(sk, *B(-2.5, 9, -13.5, 2.5, 11, -7.5), name="nasal", mat="plate", rot=TOP_ROT, origin=so)
    jaw = m.bone("jaw", sk, (0, hy + 1, hz - 1))
    m.cube(jaw, *B(-5, -5, -7, 5, 0, 0), name="jaw_back")
    m.cube(jaw, *B(-4, -4, -16, 4, 0, -7), name="jaw_front", rot=(-2, 0, 0), origin=(0, hy, hz - 7))
    m.cube(jaw, *B(-3.5, -6, -9, 3.5, -4, -2), name="gular", mat="gular")
    m.cube(jaw, *B(-4.5, -1, -6, 4.5, 2, -1), name="cheek", mat="mouth")
    m.cube(jaw, *B(-2, -2, -14, 2, 1, -5), name="tongue", mat="tongue")
    m.cube(sk, *B(-1.5, -1, -15, 1.5, 2, -7), name="palate", mat="mouth")
    # the short, recurved teeth (the "crenatissimus": finely serrated) as alpha planes. The upper row hangs just
    # OUTSIDE the lower jaw (4.25 > 4) under the maxilla's lip (4.5): with the mouth shut the crowns show over the
    # jaw's side and the lips cover only their base; the lower row stays inside the snout
    # (v3.1: the row runs on under the premaxilla, 9 px, so five short cones fit with uneven gaps)
    m.pair(sk, sk, *B(4.25, -2, -16, 4.25, 0, -7), name="teeth_up", mat="teeth")
    m.pair(jaw, jaw, *B(3, -1, -15, 3, 2, -7), name="teeth_lo", mat="teeth_lo")
    return sk


REST = {   # bone rest angles (x: + = far end up for the neck and tail, knee forward for the thigh)
    "neck1": 12, "neck2": 2, "skull": -14, "thigh": 20, "shin": -46, "foot": 38, "toes": -10,
    "arm": 15, "forearm": -40, "tail1": -4, "tail2": 2, "tail3": 1.5, "tail4": 0.5, "tail5": 0,
}
HIP_Y = 27


def legs(m, body):
    """SHORT thick legs: a heavy drumstick into the hip, a stout calf (a tibia more robust than the Carnotaurus'), a
    short metatarsus and a broad foot of three toes wider than the shin, the small first toe off the ground"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (7 * sx, HIP_Y, 0), (REST["thigh"], 0, 3 * sx))
        sh = m.bone(f"shin_{side}", th, (7 * sx, 15, 0), (REST["shin"], 0, -6 * sx))
        ft = m.bone(f"foot_{side}", sh, (7 * sx, 6, 0), (REST["foot"], 0, 3 * sx))
        m.bone(f"toes_{side}", ft, (7 * sx, -0.5, 0), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (2.5, 20, -7), (11.5, 34, 6), name="thigh")
    m.pair("thigh_l", "thigh_r", (3, 14, -5), (11, 21, 4), name="thigh_low")
    m.pair("shin_l", "shin_r", (3.5, 9, -4.5), (10.5, 16, 3.5), name="calf")
    m.pair("shin_l", "shin_r", (4, 5, -3), (10, 10, 2), name="shin")
    m.pair("foot_l", "foot_r", (5, -1, -2), (9, 7, 2), name="meta")
    m.pair("toes_l", "toes_r", (5.5, -2, -9), (8.5, 0, 0), name="toe_mid")
    m.pair("toes_l", "toes_r", (8.5, -2, -7), (10.5, 0, -1), name="toe_out")
    m.pair("toes_l", "toes_r", (3.5, -2, -7), (5.5, 0, -1), name="toe_in")
    m.pair("toes_l", "toes_r", (6.5, -2, -10), (7.5, -1, -9), name="claw_mid", mat="claw")
    m.pair("toes_l", "toes_r", (9, -2, -8), (10, -1, -7), name="claw_out", mat="claw")
    m.pair("toes_l", "toes_r", (4, -2, -8), (5, -1, -7), name="claw_in", mat="claw")
    m.pair("foot_l", "foot_r", (4, 3, 1.5), (5, 4, 3.5), name="hallux")


def arms(m, body):
    """the tiny stub arms (Burch & Carrano 2012): a short stout upper arm, a forearm of 3 px, two blunt nubs of
    fingers, no claws to speak of"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (8 * sx, 24, -29), (REST["arm"], 0, -8 * sx))
        m.bone(f"forearm_{side}", a, (8 * sx, 20, -29), (REST["forearm"], 0, 0))
    m.pair("arm_l", "arm_r", (6.5, 20, -30.5), (9.5, 25, -27.5), name="arm")
    m.pair("forearm_l", "forearm_r", (6.5, 17, -30.5), (9.5, 20, -27.5), name="forearm")
    m.pair("forearm_l", "forearm_r", (7, 16, -30), (8, 17, -29), name="nub_1", mat="claw")
    m.pair("forearm_l", "forearm_r", (8.5, 16, -30), (9.5, 17, -29), name="nub_2", mat="claw")


TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5")


def tail(m, body):
    """thick at the base and shorter than a tyrannosaur's for the body; each segment starts 2 px inside the one before,
    none repeats another's size"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 8, 26, 6.5, 23, 38), ("tail2", 24, 40, 5, 26, 36), ("tail3", 38, 52, 3.5, 28, 34),
        ("tail4", 50, 62, 2.5, 29.5, 33.5), ("tail5", 60, 70, 1.5, 30.5, 32.5)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-4.5, 20, 6), (4.5, 24, 20), name="tail_muscle")     # the deep base under the tail


SADDLE_PAL = {   # woven raffia palm fibre (Madagascar's own), oiled hide and bone: the low brawler's saddle
    "L0": hx("2b1d16"), "L1": hx("46301f"), "L2": hx("62452c"), "L3": hx("7d5c3a"), "L4": hx("97744b"),
    "F0": hx("8a7446"), "F1": hx("b39a62"), "F2": hx("ccb47c"), "F3": hx("7a3a24"),
    "I0": hx("4a4a48"), "I1": hx("787874"), "I2": hx("a4a49c"), "B0": hx("b9aa88"), "B1": hx("ddd0b0"),
    "R0": hx("8a7446"), "R1": hx("a88e58"),
}


def saddle(m, body):
    """The brawler's saddle: a mat of woven raffia with dyed red-brown stripes over the broad back, a LOW hide seat
    (it is the steady mount, nothing to brace against), a grab rope looped at the front for when it holds and shakes,
    a broad raffia girth, short bone stirrups. Faces lying on the body are left out (no back-face culling in
    GeckoLib)."""
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    sd = m.bone("saddle", body, (0, 39, -16))
    m.cube(sd, (-8, 38, -27), (8, 40, -7), name="pad", mat="fur", faces=out("down"))
    m.pair(sd, sd, (8.5, 29, -25), (9.5, 38, -10), name="flap_f", mat="fur", faces=out("east", "up"))
    m.cube(sd, (-5, 40, -24), (5, 41, -11), name="seat", mat="hide", faces=out("down"))
    m.cube(sd, (-3, 41, -24), (3, 43, -22), name="pommel", mat="hide")
    m.cube(sd, (-4, 41, -12), (4, 43, -10), name="cantle", mat="hide")
    m.cube(sd, (-2.5, 43, -24), (2.5, 45, -23), name="grab", mat="rope")
    m.pair(sd, sd, (9.5, 24, -19), (10.5, 37, -18), name="leather", mat="strap", faces=out("east", "up"))
    m.pair(sd, sd, (9.5, 22, -20), (12.5, 24, -19), name="stir_f", mat="bone")
    m.pair(sd, sd, (9.5, 22, -18), (12.5, 24, -17), name="stir_b", mat="bone")
    m.pair(sd, sd, (9.5, 21, -20), (12.5, 22, -17), name="stir_t", mat="bone")
    # the broad raffia girth, down the flank and across the belly
    m.pair(sd, sd, (9, 16, -15), (10, 30, -12), name="girth", mat="rope", faces=out("east", "up"))
    m.cube(sd, (-7, 13, -15), (7, 14, -12), name="girth_under", mat="rope", faces=out("up"))
    m.pair(sd, sd, (7, 13, -15), (9, 16, -12), name="girth_low", mat="rope", faces=out("east"))


def saddle_px(t):
    mat = t.cube["mat"]; n = t.cube["name"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "fur":            # the raffia mat: a twill of palm fibre, two dyed stripes across it
        if f == "up":
            if j in (3, h - 4):
                return p["F3"]
            return p["F2"] if (i + 2 * j) % 3 == 0 else p["F1"]
        if j == h - 1:
            return p["F0"]
        if j == 1:
            return p["F3"]
        return p["F2"] if (i + j) % 3 == 0 else p["F1"]
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
    m = P.Model("majungasaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, HIP_Y, 0))
    # the trunk: stocky and broad, low over the short legs, the chest deep in front
    m.cube(body, (-7, 15, -35), (7, 35, -25), name="chest")
    m.cube(body, (-4.5, 13, -34), (4.5, 16, -26), name="keel")
    m.cube(body, (-8.5, 16, -27), (8.5, 37, -6), name="torso")
    m.cube(body, (-6.5, 14, -26), (6.5, 17, -8), name="belly", mat="belly")
    m.cube(body, (-7.5, 21, -8), (7.5, 38, 10), name="hips")
    m.cube(body, (-4.5, 36, -30), (4.5, 39, -4), name="back")
    # the neck: short, thick and strong (it holds and shakes), carried low and nearly level
    n1 = m.bone("neck1", body, (0, 29, -34), (REST["neck1"], 0, 0))
    m.cube(n1, (-6.5, 20, -40), (6.5, 36, -31), name="shoulders")
    m.cube(n1, (-6, 22, -46), (6, 35, -38), name="neck1")
    n2 = m.bone("neck2", n1, (0, 29, -45), (REST["neck2"], 0, 0))
    m.cube(n2, (-5.5, 23, -52), (5.5, 34, -44), name="neck2")
    m.cube(n2, (-4, 20, -52), (4, 24, -45), name="throat")
    hd = m.bone("head", n2, (0, 28, -51))
    head(m, hd, 23, -51, rest=(REST["skull"], 0, 0))
    arms(m, body); legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the skin (skin2, the 1.10.1 standard)
TRUNK = {"chest", "keel", "torso", "hips", "back", "shoulders", "neck1", "neck2", "throat", "tail1", "tail2", "tail3",
         "tail4", "tail5", "tail_muscle"}
LEG = {"calf", "shin", "meta", "toe_mid", "toe_out", "toe_in", "hallux"}
LIMB = {"thigh", "thigh_low", "arm", "forearm"}
BODY_PARTS = TRUNK | LEG | LIMB | {"belly"}
HEAD = {"cranium", "occiput", "temporal", "maxilla", "snout", "premax", "jaw_back", "jaw_front"}

# THE MARKS (drawn, not drawn by lot):
# 1. BROAD ragged dark CROSSBANDS over the back from the shoulders, ringing the tail toward its tip (camouflage of a
#    low ambusher in dry grass): z centre, half width, how far down the flank (0 = belly, 1 = spine);
# 2. the dark horn of the dome and the nasal ridge (materials), and on the male the bare skin round the dome ochre;
# 3. a pale STRIPE from the corner of the mouth back down the side of the neck.
BANDS = [(-37, 1.8, 0.66), (-25, 2.6, 0.58), (-12, 2.8, 0.55), (1, 2.8, 0.55), (15, 2.6, 0.48), (28, 2.4, 0.38),
         (40, 2.0, 0.28), (51, 1.8, 0.16), (61, 1.4, 0.05)]


def body_tone(t, prof, sex):
    """the palette key of a body texel: the countershading by the silhouette, the bands, the neck stripe, blotches"""
    n = t.cube["name"]; f = t.face
    z, y = t.P[2], t.P[1]
    if f == "down" or n in ("belly", "keel", "tail_muscle"):
        h = 0.0 if f == "down" else min(0.17, prof.height(t))
    elif f == "up":             # the broad back: the spine dark, its shoulders a step lighter
        hw = max(1.0, (t.cube["to"][0] - t.cube["from"][0]) / 2.0)
        h = 1.0 - 0.3 * min(1.0, abs(t.P[0]) / hw)
    else:
        h = prof.height(t)
    b = skin2.bands(h, z, (0.22, 0.30, 0.52, 0.80), amp=0.04, seed=12)
    if b == 0:
        u, v = skin2.surface_uv(t)
        k = skin.scutes(u, v, row=3, width=5)
        return {"seam": "b0", "hi": "b2", "base": "b1"}[k]
    base = ["b1", "b0", "k4", "k3", "k2"][b]
    # the pale stripe down the side of the neck: from the jaw corner, slanting down toward the shoulder
    if n in ("neck1", "neck2", "shoulders", "throat") and f in ("east", "west"):
        yc = STRIPE[0] + (z - STRIPE[1]) * -0.3
        if abs(y - yc) < 0.9 + 0.4 * skin2.soft(z, 0, 3.0, seed=70) and z < STRIPE[1] + 16:
            return "st"
    # the broad ragged crossbands from the spine down to their own depth
    for k, (zc, half, low) in enumerate(BANDS):
        edge = half + 0.9 * (skin2.soft(*skin2.surface_uv(t), 2.2, seed=40 + k) - 0.5)
        if abs(z - zc) < edge and h > low:
            torn = h < low + 0.10 and skin2.soft(*skin2.surface_uv(t), 2.0, seed=50 + k) < 0.5
            if not torn:
                return "k1" if b >= 3 else "k2"
    if b >= 2:
        base = skin2.step(base, skin2.mottle(t, cell=9, strength=0.2, seed=13))
        # padrão v3: the body's own motif, PORES: the sculpted pits of the face carried onto the body, sparse and
        # one step deep, and now and then a low knob (never the face's density, never scales)
        base = skin2.step(base, max(-1, bone_pits(t, cell=BODY_PORE, seed=15, knobs=4)))
    return base


def limb_tone(t):
    """legs and arms: calm, lit on the front, a step darker behind and below; scutes across the front of the
    metatarsus and the toes"""
    n = t.cube["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    v = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    if n in ("thigh", "thigh_low"):
        base = "k3"
        if f in ("east", "west") and t.rel[2] > 0.55 and v < 0.45:
            base = "k2"
        if f in ("east", "west", "north") and t.rel[2] < 0.3 and 0.35 < v < 0.8:
            base = "k4"
        if f in ("east", "west") and v > 0.86:
            base = "k2"
        if f == "south" or f == "down":
            base = "k2"
        return skin2.step(base, skin2.mottle(t, cell=7, strength=0.22, seed=16))
    if n in ("arm", "forearm"):
        return "k4" if f in ("north", "up", "east", "west") and v > 0.3 else "k3"
    base = "k4" if f in ("north", "up") else "k3"
    if n in ("meta", "toe_mid", "toe_out", "toe_in") and f in ("north", "up", "east", "west"):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 2
        if k == 0 and (t.i % 3) != 1:
            return skin2.step(base, -1)
        return base
    if f == "south":
        return "k3"
    return skin2.step(base, skin2.mottle(t, cell=5, strength=0.25, seed=17))


# ------------------------------------------------------------------ padrão v3: the Majungasaurus' own head
# (docs/estudos/14, "Padrão v3": the engine only measures, every part below is drawn for this animal alone)
#
# THE MOTIF: the abelisaur's sculpted bone under thin skin, PITS (pores, the nerve and vessel foramina) and KNOBS
# (a lit top with its own shadow under it), on a jittered grid in body space; never scales. Dense and deep on the
# fused nasals, the dome and the brow, looser on the cheek, sparse pores on the body.
def bone_pits(t, cell=3.0, seed=0, knobs=3):
    """-2 a deep pore, -1 a knob's shadow, +1 a knob's lit top, 0 skin. One feature per jittered cell, so no two
    touch and the field does not repeat; the knob's shadow falls under it (body space: y down)"""
    u, v = skin2.surface_uv(t)
    iu, iv = math.floor(u), math.floor(v)
    for gx in (math.floor(u / cell), math.floor(u / cell) - 1):
        for gy in (math.floor(v / cell), math.floor(v / cell) + 1):
            fx = math.floor((gx + 0.2 + 0.6 * (h32(gx, gy, seed, 1) % 997) / 997.0) * cell)
            fy = math.floor((gy + 0.2 + 0.6 * (h32(gx, gy, seed, 2) % 997) / 997.0) * cell)
            kind = h32(gx, gy, seed, 3) % knobs
            if (iu, iv) == (fx, fy):
                return 1 if kind == 0 else -2
            if kind == 0 and (iu, iv) == (fx, fy - 1) and t.face not in ("up", "down"):
                return -1
    return 0


def _pit_step(base, k, floor="k0"):
    """the palette key for a pit field value: a pore two steps down (never under `floor`), a knob one up"""
    if k == -2:
        return skin2.step(base, -2) if base not in ("k1", "k0") else floor
    return skin2.step(base, k)


# padrão v3.1: the head's own value ladder, from the dark under the brow to the palest bone knob
HL = ["k0", "k1", "k2", "k3", "k4", "k5", "bn0", "bn1", "bn2"]


def hstep(key, d):
    return HL[max(0, min(len(HL) - 1, HL.index(key) + d))]


def _bone(base, k, knob=1, pore=-2):
    """rugose BONE seen from above: the knobs a step (or `knob` steps) paler, the pits `pore` steps darker, so the
    roof reads light with dark only in its pits"""
    return hstep(base, knob if k == 1 else (pore if k == -2 else k))


def _ochre(t, sex, rows=2):
    """the male's display skin, ONLY round the foot of the dome (study 13: a muted ochre-rust skin at its base): on
    the lowest rows of the dome's foot, broken into patches by a soft noise and its knobs, never a ring or a bar.
    The female has none"""
    if sex != "male" or t.face in ("up", "down") or t.j < t.h - rows:
        return None
    u, v = skin2.surface_uv(t)
    if skin2.soft(u, v, 1.3, seed=61) < 0.36:
        return None
    k = bone_pits(t, cell=2.2, seed=62, knobs=2)
    return "oc2" if k == 1 else ("oc0" if k == -2 or t.j == t.h - 1 else "oc1")


def head_tone(t, sex):
    """padrão v3.1: the VALUE structure of a heavy rugose head. The roof, the snout's top and everything facing up are
    pale rugose bone (bn0..bn2, pits dark), the face's sides a step under them (k4/k5, lighter toward the roof), the
    dark only in the pits, the mouth line and under the brow; a PALE lip line over the mouth and a pale lower jaw.
    The pale neck stripe starts at the jaw corner"""
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "b1"
    if n in ("jaw_back", "jaw_front"):
        if f == "up":
            return "k4"
        h = t.rel[1]
        if t.j == 0:
            return "b3"                       # the pale lower lip, the line the shut mouth reads by
        if n == "jaw_back" and f in ("east", "west") and 0.4 < h < 0.75 and t.rel[2] > 0.5:
            return "st"
        base = "b1" if h < 0.35 else "b2"
        return _pit_step(base, bone_pits(t, cell=2.4, seed=33, knobs=3), "k3")
    if f == "up":                             # the roof and the snout's top: pale bone, knobbed and pitted
        k = bone_pits(t, cell=2.1, seed=21 if n in ("snout", "premax", "maxilla") else 24, knobs=2)
        return _bone("bn0", k)
    if n in ("maxilla", "premax"):
        if t.j == t.h - 1:
            return "k1"                       # the mouth line, soft under the thick lip
        if t.j == t.h - 2:
            return "b2" if bone_pits(t, cell=2.0, seed=27, knobs=4) >= 0 else "lip"   # the pale upper lip, wrinkled
        if t.j == t.h - 3:
            return "k4"
    hv = (t.P[1] - HEAD_Y[0]) / max(1.0, HEAD_Y[1] - HEAD_Y[0])
    # the sides: slate low (on with the neck), a step lighter up the face, so the roof's bone stands over them
    base = ["k3", "k4", "k5"][skin2.bands(hv, t.P[2] * 2.0, (0.40, 0.76), amp=0.07, seed=31)]
    if n in ("cranium", "temporal") and f in ("east", "west"):
        # the bag of skin under the deep-set eye: a fold that catches the light, its crease under it
        dz = t.P[2] - EYE[0]; dy = t.P[1] - EYE[1]
        if -2.0 < dz < 2.5 and -3.6 < dy < -2.6:
            return "bn0"
        if -1.5 < dz < 3.0 and -4.6 < dy < -3.6:
            return "k3"
    if n in ("maxilla", "premax", "snout") and f in ("east", "west", "north"):
        k = bone_pits(t, cell=2.0, seed=9, knobs=2)
        return _bone(base, k, knob=2)         # the snout's knobs: big lumps, two steps up
    return _bone(base, bone_pits(t, cell=2.4, seed=32, knobs=2))


def teeth_up(t, p):
    """FEW short conical teeth on a short snout, but enough to read from the side (padrão v3.1: 9 px of row, five
    teeth), uneven: cones two texels wide at the root under the lip and one at the tip, single spikes, and the duller
    thin spike of a new tooth coming in (it replaced its teeth every two months, study 13), the gaps irregular.
    Columns from the FRONT"""
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2] - t.cube["from"][2])); row = t.j
    # (first column, root width, rows, tip column offset, tone) of each tooth
    for c0, wide, rows, tip, tone in ((0, 1, 2, 0, "tooth"), (2, 2, 2, 1, "tooth"), (5, 1, 2, 0, "tooth"),
                                      (6, 1, 1, 0, "tooth2"), (8, 1, 2, 0, "tooth")):
        if c0 <= col < c0 + wide and row < rows:
            if wide == 1:
                return p[tone]
            if row == 0:
                return p["tooth2"] if col == c0 + wide - 1 else p["tooth"]
            return p["tooth"] if col == c0 + tip else None
    return None


def teeth_lo(t, p):
    """the lower row inside the snout: blunt cones on every third column"""
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2] - t.cube["from"][2])); row = t.j
    if row == t.h - 1:
        return p["k1"]          # the jaw's inner lip: it shows at the front of the shut mouth, so skin, not gum
    if col % 3 == 1 and row >= 1:
        return p["tooth2"] if row == 1 else p["tooth"]
    return None


def mouth_interior(img, C, p):
    """the palate pale pink and ridged across (the short wide mouth), the floor of the jaw a broad tongue"""
    for name in ("maxilla", "premax", "cranium"):
        u, v, ww, hh = C[name]["uv"]["down"]
        for j in range(hh):
            for i in range(ww):
                ridge = j % 3 == 0 and 0 < i < ww - 1      # the rim stays dark: no red thread at the lip
                img[v + j, u + i] = (*(p["gum"] if ridge else p["mouth"]), 255)
    for name in ("jaw_front", "jaw_back"):
        u, v, ww, hh = C[name]["uv"]["up"]
        for j in range(hh):
            for i in range(ww):
                # the outer columns show in front of the narrower premaxilla: the lower lip's skin, not gum
                lip = i in (0, ww - 1) or (name == "jaw_front" and j >= hh - 2)   # (and its front rows)
                img[v + j, u + i] = (*(p["k2"] if lip else p["tongue"]), 255)


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]; f = t.face; n = t.cube["name"]
        if mat in ("hide", "fur", "strap", "iron", "bone", "rope"):
            return saddle_px(t)
        if mat == "claw":
            return p["ker0"] if f != "up" else p["ker1"]
        if mat == "dome":       # padrão v3.1: the knob is the skull's own rugose bone, paler layer by layer up
            k = ("dome_base", "dome", "dome_top", "dome_cap").index(n)     # to the crown (lit from above, round)
            pits = bone_pits(t, cell=2.0, seed=63 + k, knobs=2)
            if f == "up":
                return p[_bone(("bn0", "bn1", "bn1", "bn2")[k], pits, pore=-3 if k == 3 else -2)]
            if k == 0:
                oc = _ochre(t, sex)
                if oc:
                    return p[oc]
            side = ("k5", "bn0", "bn0", "bn1")[k]
            if t.j == 0 and k < 3:
                side = hstep(side, 1)                  # the rim turning into the layer above
            return p[_bone(side, pits)]
        if mat == "brow":       # the heavy rugose brow: pale knobbed bone on top, its underside the eye's shadow
            if f == "down":
                return p["k0"]
            if f in ("east", "west", "north") and t.j == t.h - 1:
                return p["k1"]
            if f in ("east", "west", "north") and t.j == 0:
                return p[_bone("bn1", bone_pits(t, cell=2.0, seed=66, knobs=2))]
            return p[_bone("bn1" if f == "up" else "bn0", bone_pits(t, cell=2.0, seed=65, knobs=2))]
        if mat == "plate":      # the thick fused nasals: a broad ridge of pale knobbed bone
            if f in ("up", "north"):
                return p[_bone("bn1", bone_pits(t, cell=1.9, seed=67, knobs=2), pore=-3)]
            if t.j == t.h - 1:
                return p["k3"]
            return p[_bone("bn0" if t.j == 0 else "k5", bone_pits(t, cell=2.0, seed=69, knobs=2))]
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
BODY_PORE = 6.5        # the body's pore cell in texels (body neighbours change 0.20-0.30)
HEAD_Y = [0.0, 1.0]       # the lowest and highest point of the face at rest (the head's countershading)
DOME = [0.0, 0.0]         # rest-pose z and foot height of the dome
EYE = [0.0, 0.0]          # rest-pose z and y of the eye's centre (the fold under it, the male's knobs behind it)
STRIPE = [0.0, 0.0]       # rest-pose y and z of the jaw corner (the neck stripe starts there)

# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP
# THE EYE: small and deep-set under the heavy brow (the brow's own shadow is its top lid, so no rim row on top);
# a round pupil low in a lichen-green iris, the glint at the FRONT top where the light comes in under the brow;
# below it the fold and crease of the eye bag are painted by head_tone
EYE_ART = [   # padrão v3.1: bigger (an iris of 3 x 2 and more), a low round pupil, an amber fleck, the socket under it
    "dgiiid",
    "diippd",
    "dIIaId",
    ".ssss.",
]
NOSTRIL = [      # a big round nostril high on the blunt snout, its rugose rim lit above and a pore behind it
    ".hh.",
    "hnnd",
    ".nn.",
]


def decals_for(sex):
    p = pal_for(sex)
    cm = {"d": p["k0"], "g": p["glint"], "i": p["iris"], "I": p["iris2"], "p": p["pupil"], "n": p["k0"],
          "h": p["bn0"], "a": p["iris3"], "s": p["k1"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", EYE_ART, cm, at=(0, 3))
        P.stamp(img, m, C["premax"], "east", NOSTRIL, cm, at=(0, 0))
        mouth_interior(img, C, p)
    return dec


def paint_sex(m, sex="male"):
    PROF[0] = skin2.Profile(m, TRUNK | {"belly"})
    import geo
    pts = {c["name"]: q for c, q in geo.cube_points(m.spec())}
    ys = [pts[n][:, 1] for n in ("cranium", "maxilla", "premax")]
    HEAD_Y[:] = [min(a.min() for a in ys), max(a.max() for a in ys)]
    DOME[:] = [float(pts["dome"][:, 2].mean()), float(pts["cranium"][:, 1].max())]
    br = pts["brow"]
    EYE[:] = [float(br[:, 2].mean()), float(br[:, 1].min()) - 2.0]
    jb = pts["jaw_back"]
    STRIPE[:] = [float(jb[:, 1].max()) + 3.0, float(jb[:, 2].max())]
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
