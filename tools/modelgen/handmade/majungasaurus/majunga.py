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
   tail (the first drawn mark), the dome and the nasal ridge dark horn and, on the male, the bare skin round the dome
   dull ochre-orange (the second), and a pale stripe from the corner of the mouth down the side of the neck (the
   third). The belly is a pale warm grey.
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
    "oc0": "8a5a30", "oc1": "a8723c", "st": "919aa1", "lip": "737d86",
    "female": {"k1": "163143", "k2": "254055", "k3": "365066", "k4": "486175", "k5": "5d7283",
               "b0": "757d84", "b1": "828a91", "b2": "8e979f", "oc0": "4a4440", "oc1": "5c5650"},
}
PAL = {
    "ker0": hx("1e1a18"), "ker1": hx("362e2a"), "ker2": hx("cfc4a8"), "ker3": hx("a09276"),
    "iris": hx("d0a43c"), "pupil": hx("0f0b0c"), "lid": hx("17111a"), "glint": hx("ece2c2"),
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


TOP_ROT = (-8, 0, 0)        # the top of the snout falls gently to the blunt tip (a short deep box, not a wedge)


def head(m, parent, hy, hz, rest=(-4, 0, 0)):
    """the short, deep, BROAD skull and the deep jaw. (hy, hz): the mouth line at the back of the skull; returns the
    skull. 16 px from the occiput to the blunt snout (0.95 m drawn against ~0.7 m: the head is the signature), 11 px
    wide at the cranium, the single DOME standing on the roof over the eyes, the thick rugose nasals in front of it"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    sk = m.bone("skull", parent, (0, hy + 5, hz), rest)
    so = (0, hy + 10, hz - 7)               # the top of the snout hinges at the front of the cranium
    m.cube(sk, *B(-5.5, 0, -7, 5.5, 10, 0), name="cranium")
    m.cube(sk, *B(-4.5, 3, 0, 4.5, 9, 2), name="occiput")
    m.pair(sk, sk, *B(5.5, 1, -3, 6.5, 6, 0), name="temporal")           # the jaw muscle bulging behind the eye
    # THE DOME: one rounded knob on the fused frontals, over and just behind the eyes (no brow horns); a broad base
    # and a smaller cap so it reads round from the side and from the front
    m.cube(sk, *B(-3.5, 10, -8, 3.5, 11, -1), name="dome_base", mat="dome")
    m.cube(sk, *B(-2.5, 11, -7, 2.5, 13, -2), name="dome", mat="horn")
    m.cube(sk, *B(-1.5, 13, -6, 1.5, 14, -3), name="dome_cap", mat="horn")
    m.cube(sk, *B(-4.5, 0, -14, 4.5, 7, -7), name="maxilla")              # the broad, blunt snout
    m.cube(sk, *B(-3.5, 5, -14, 3.5, 10, -7), name="snout", rot=TOP_ROT, origin=so)
    m.cube(sk, *B(-3.5, 0, -16, 3.5, 6, -14), name="premax")
    # the thick fused nasals, rugose and sculpted (keratin in life): a broad ridge along the top of the snout
    m.cube(sk, *B(-2, 10, -13, 2, 11, -7), name="nasal", mat="plate", rot=TOP_ROT, origin=so)
    jaw = m.bone("jaw", sk, (0, hy + 1, hz - 1))
    m.cube(jaw, *B(-5, -5, -7, 5, 0, 0), name="jaw_back")
    m.cube(jaw, *B(-4, -4, -16, 4, 0, -7), name="jaw_front", rot=(-2, 0, 0), origin=(0, hy, hz - 7))
    m.cube(jaw, *B(-3.5, -6, -9, 3.5, -4, -2), name="gular", mat="gular")
    m.cube(jaw, *B(-4.5, -1, -6, 4.5, 2, -1), name="cheek", mat="mouth")
    m.cube(jaw, *B(-2, -2, -14, 2, 1, -5), name="tongue", mat="tongue")
    m.cube(sk, *B(-1.5, -1, -15, 1.5, 2, -7), name="palate", mat="mouth")
    # the short, recurved teeth (the "crenatissimus": finely serrated) as alpha planes; with the mouth shut the lips
    # hide them (Cullen et al. 2023)
    m.pair(sk, sk, *B(3.5, -2, -15, 3.5, 1, -7), name="teeth_up", mat="teeth")
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
        if skin2.fleck(t, every=21, seed=14):
            base = skin2.step(base, -1)
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


def head_tone(t, sex):
    """the face: three tones by height (dark crown, middle cheek, light lips) as one shape over the whole head, the
    rugose sculpting of the deep snout (pits and ridges), the pale stripe starting at the jaw corner and, on the male,
    the ochre bare skin round the dome"""
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "b1"
    if n in ("jaw_back", "jaw_front"):
        h = t.rel[1] if f != "up" else 1.0
        if n == "jaw_back" and f in ("east", "west") and 0.45 < h < 0.8 and t.rel[2] > 0.5:
            return "st"
        return "b1" if h < 0.3 else ("lip" if h < 0.55 else "k4")
    if f == "up":
        if n == "cranium":       # the skin round the dome: ochre on the male, the female's a dull grey-brown
            dz = t.P[2] - DOME[0]; dx = t.P[0]
            if dx * dx / 16.0 + dz * dz / 16.0 < 1.0:
                return "oc1" if (t.i + t.j) % 3 else "oc0"
        if n in ("snout", "premax", "maxilla"):
            u, v = skin2.surface_uv(t)
            return "k1" if (math.floor(v) % 2 == 0 and math.floor(u) % 2 == 0) else "k2"
        return "k2" if skin2.mottle(t, cell=4, strength=0.3, seed=24) >= 0 else "k1"
    v = t.rel[1]
    if v < 0.12 and n in ("maxilla", "premax"):
        return "lip"
    hv = (t.P[1] - HEAD_Y[0]) / max(1.0, HEAD_Y[1] - HEAD_Y[0])
    base = ["k5", "k4", "k3"][skin2.bands(hv, t.P[2] * 2.0, (0.36, 0.70), amp=0.07, seed=31)]
    # the rugose snout: sculpted pits and short ridges all over the deep maxilla and the nasal sides
    if n in ("maxilla", "premax", "snout") and f in ("east", "west", "north") and 0.12 < v < 0.95:
        u, w = skin2.surface_uv(t)
        if h32(int(math.floor(u)), int(math.floor(w)), 9) % 6 == 0:
            return skin2.step(base, -1)
        return base
    return skin2.step(base, skin2.mottle(t, cell=5, strength=0.28, seed=32)) if base != "k5" else base


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]; f = t.face; n = t.cube["name"]
        if mat in ("hide", "fur", "strap", "iron", "bone", "rope"):
            return saddle_px(t)
        if mat == "claw":
            return p["ker0"] if f != "up" else p["ker1"]
        if mat == "horn":       # the dome's cap: rugose keratin, worn paler on top
            if f == "up":
                return p["ker3"] if h32(t.i, t.j, 5) % 3 else p["hn2"]
            return p["hn1"] if t.j >= t.h - 1 else (p["hn2"] if (t.i + t.j) % 3 else p["hn1"])
        if mat == "dome":       # the swelling the dome rises from: skin, the male's bare and ochre
            return p["oc1"] if f == "up" and (t.i + t.j) % 3 else p["oc0"]
        if mat == "plate":      # the thick rugose nasals: skin over sculpted bone, a ridge of knobs
            if f in ("up", "north"):
                return p["k1"] if math.floor(t.L[2]) % 2 == 0 else p["k3"]
            return p["k2"]
        if mat == "teeth":      # short recurved teeth, every second column
            if f not in ("east", "west"):
                return None
            col = int(math.floor(t.L[2])); row = t.j
            if row == 0:
                return p["gum"]
            if (col + 40) % 2:
                return None
            size = 2 if h32(col, 11) % 4 else 3
            return (p["tooth"] if row < size else p["tooth2"]) if row <= size else None
        if mat == "teeth_lo":
            if f not in ("east", "west"):
                return None
            col = int(math.floor(t.L[2])); row = t.j
            if row == t.h - 1:
                return p["gum"]
            if (col + 41) % 2 == 0 and row >= (0 if h32(col, 13) % 3 else 1):
                return p["tooth2"] if row == 0 else p["tooth"]
            return None
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
HEAD_Y = [0.0, 1.0]       # the lowest and highest point of the face at rest (the head's countershading)
DOME = [0.0]              # rest-pose z of the dome's centre (the ochre round it)
STRIPE = [0.0, 0.0]       # rest-pose y and z of the jaw corner (the neck stripe starts there)

# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP
EYE = [          # under the dome's foot: a heavy lid, an oval orbit, a gold point and a glint
    "lll",
    "lpi",
    "lpg",
]
NOSTRIL = ["n"]


def decals_for(sex):
    p = pal_for(sex)
    cm = {"l": p["k2"], "p": p["pupil"], "i": p["iris"], "g": p["glint"], "n": p["k1"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", EYE, cm, at=(1, 2))
        P.stamp(img, m, C["premax"], "east", NOSTRIL, cm, at=(0, 1))
        # the row of nerve foramina above the lip line
        u, v, w, h = C["maxilla"]["uv"]["east"]
        for k in range(1, w - 1, 2):
            img[v + h - 2, u + w - 1 - k] = (*p["k3"], 255)
        for name, f in (("maxilla", "down"), ("premax", "down"), ("cranium", "down"), ("jaw_front", "up"), ("jaw_back", "up")):
            c = C[name]; u, v, ww, hh = c["uv"][f]
            for j in range(hh):
                for i in range(ww):
                    rim = i in (0, ww - 1)
                    if name in ("maxilla", "premax"):
                        col = p["gum"] if rim or i in (1, ww - 2) else p["mouth"]
                    elif name == "cranium":
                        col = p["mouth"]
                    else:
                        col = p["gum"] if rim else p["tongue"]
                    img[v + j, u + i] = (*col, 255)
    return dec


def paint_sex(m, sex="male"):
    PROF[0] = skin2.Profile(m, TRUNK | {"belly"})
    import geo
    pts = {c["name"]: q for c, q in geo.cube_points(m.spec())}
    ys = [pts[n][:, 1] for n in ("cranium", "maxilla", "premax")]
    HEAD_Y[:] = [min(a.min() for a in ys), max(a.max() for a in ys)]
    DOME[0] = float(pts["dome"][:, 2].mean())
    jb = pts["jaw_back"]
    STRIPE[:] = [float(jb[:, 1].max()) + 3.0, float(jb[:, 2].max())]
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
