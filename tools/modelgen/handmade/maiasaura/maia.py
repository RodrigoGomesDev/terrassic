"""Maiasaura peeblesorum, made by hand from its own study (docs/estudos/15_HERBIVOROS_1_11.md, approved by Rodrigo on
10/11/2026). Real size 9 m (Wosik et al. 2020: up to ~9 m and ~4 t; Rodrigo's answer: as it is, the top).

The first herbivore of the 1.10 standard (docs/estudos/14_POR_QUE_PARECE_IA.md, "Padrão v3"), the way the four 1.10
predators set it:
- one texel = one Minecraft pixel: drawn at skin2.PX_PER_M (16.94 px per metre), shown at a model scale of ~1;
- the skin in BODY space (skin2): dark back, middle flank, pale belly as one shape, a calm base, marks DRAWN;
- the head drawn from its own anatomy (padrão v3): its own eye, beak edge, nostril, skin motif, accent and mouth;
- item 4 of study 14: the neck and the tail taper in overlapping pieces whose skin runs on, never equal boxes.

What makes it read as itself and NOT as the remade Edmontosaurus or Parasaurolophus (study 15):
1. the HEAD: SHORT, DEEP and broad for a hadrosaur, the bill broad and DROOPING at the tip (not the Edmontosaurus' long
   flat duck bill), and the mark of the genus, a SOLID low crest of bone (nasals and frontals) just in front of and
   over the eyes (Horner & Makela 1979) - a hump, not a tube (Parasaurolophus) nor a comb of flesh (Edmontosaurus);
   the hump is the signature, drawn ~25% bigger than the bone (study 14, C);
2. the body: a heavy quadruped when grown, 3 m shorter than the Edmontosaurus, the back without the Edmontosaurus'
   segmented frill, the neck short and thick, the tail deep and stiff with ossified tendons;
3. the young walk on TWO legs (Cubo et al. 2015): the calf has its own skin (paler, smooth), no hump (adult_bump), and
   a bigger head on a short snout (DinosaurEntity.babyHeadScale);
4. the colour "capim-seco": straw green of dry upland grass, the back a step darker with big loose VERTICAL blotches on
   the flanks (bush shadow), a cream belly, the head a little lighter than the neck; on the male the hump is
   ochre-rust with its worn crown paler; on the female the hump is the face's own colour.
"""
import math

import proto as P
import skin
import skin2
from proto import hx, h32

TEX_W = 256
PX_M = skin2.PX_PER_M
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# ------------------------------------------------------------------ palette ("capim-seco", study 15)
# k0..k5 the body ramp (dry upland grass, shadows to palha-sombra), b0..b3 the cream belly, sc the pale flat scales of
# the hump, oc the male's ochre-rust hump, bk the beak's keratin
SCHEME = {
    # (the painted skin measured 8.3 from the Edmontosaurus with the study's swatches, colourcheck --remade: the same
    # capim-seco a step greener, 12.9 from the nearest)
    "k0": "2a2919", "k1": "383c20", "k2": "5e6436", "k3": "868a4c", "k4": "9ca062", "k5": "b0b476",
    "b0": "bdb796", "b1": "ccc7aa", "b2": "e0dcc4", "b3": "ebe8d6",
    "sc0": "aba57a", "sc1": "c0bb92", "sc2": "d2cda8",
    "oc0": "7a4420", "oc1": "a0602c", "oc2": "c08048",
    "bk0": "26231a", "bk1": "3c372a", "bk2": "57503c", "lip": "77714e",
    "female": {"k2": "62663c", "k3": "8a8d54", "k4": "a0a36a", "k5": "b4b780",
               "oc0": "8c8656", "oc1": "a09a68", "oc2": "b3ad7e"},
}
PAL = {
    "iris": hx("a8702c"), "iris2": hx("7a4a1e"), "pupil": hx("100c08"), "glint": hx("f4ecd4"),
    "lid": hx("d8d2b2"), "lid2": hx("bfb894"),
    "mouth": hx("3a2420"), "tongue": hx("8a5048"), "gum": hx("6a3a34"),
    "tooth": hx("e8e2c6"), "tooth2": hx("bdb390"),
    "hoof0": hx("2c2820"), "hoof1": hx("4a4436"), "hoof2": hx("6c6450"),
}
# the calf: paler and smooth, straw (study 15: "o filhote é mais claro e liso, cor de palha")
CALF = {"k0": "4a4630", "k1": "6a6545", "k2": "8a855c", "k3": "a49e70", "k4": "b8b286", "k5": "c8c39a"}


def pal_for(sex):
    p = dict(PAL)
    for k, v in SCHEME.items():
        if k != "female":
            p[k] = hx(v)
    if sex == "female":
        for k, v in SCHEME["female"].items():
            p[k] = hx(v)
    if sex == "baby":
        for k, v in SCHEME["female"].items():
            p[k] = hx(v)
        for k, v in CALF.items():
            p[k] = hx(v)
    return p


# ------------------------------------------------------------------ geometry
# Model px at PX_M, the hip joint at z = 0, the ground at y = 0 (after _ground), the bill toward -z.
# Signs (geo.rot_matrix): +x lifts what lies in front (-z) and lowers what lies behind (+z); a hanging limb with +x
# swings its far end forward.
REST = {"neck1": 34, "neck2": -14, "skull": -26,
        "thigh": 10, "shin": -26, "foot": 30, "toes": -14,
        "arm": -14, "forearm": 20, "hand": -6,
        "tail1": 4, "tail2": 1, "tail3": 1, "tail4": 0}
HIP_Y = 36
SADDLE_MATS = ("hide", "leather", "weave", "bag", "cord", "wood")


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes})
             if c["mat"] not in SADDLE_MATS + ("teeth",))
    m.shift(-lo)


def head(m, parent, y, z):
    """the short, deep skull with the broad drooping bill, the jaw, the cheeks and the solid hump. (y, z): the
    occipital joint. 20 px from the occiput to the bill tip (1.2 m drawn against ~0.85 m: the head is the signature
    with the hump)"""
    sk = m.bone("skull", parent, (0, y, z), (REST["skull"], 0, 0))

    def B(x0, y0, z0, x1, y1, z1):
        return (x0, y + y0, z + z0), (x1, y + y1, z + z1)
    # a deep braincase with the eye at its front, a short deep face, the snout sloping to the broad bill
    m.cube(sk, *B(-4.5, -5, -7, 4.5, 5, 1), name="cranium")
    m.cube(sk, *B(-4, -5, -12, 4, 4, -6), name="face", faces=OUT("south"))
    m.cube(sk, *B(-3.5, -5, -15, 3.5, 1, -11), name="snout", faces=OUT("south"), rot=(-8, 0, 0), origin=(0, y + 1, z - 11))
    # the BROAD bill, wider than the snout, its tip DROOPING (study 15: "bico largo e caído na ponta")
    m.cube(sk, *B(-4.5, -5.5, -19, 4.5, -2.5, -14), name="bill", mat="beak", faces=OUT("south"))
    m.cube(sk, *B(-3.5, -6.5, -21, 3.5, -3.5, -18), name="bill_tip", mat="beak", faces=OUT("south"),
           rot=(10, 0, 0), origin=(0, y - 3.5, z - 18))
    # THE HUMP: the solid low crest of the nasals and frontals in front of and over the eyes, grown out of the roof
    # of the face in three layers, each starting inside the one under it (a rounded hump, not a stair); the grown
    # one's (adult_bump: the calf has a flat brow)
    ab = m.bone("adult_bump", sk, (0, y + 3, z - 6))
    for k, (w, y0, y1, z0, z1) in enumerate(((3.5, 3.0, 6.0, -13.0, -2.0), (3.0, 5.0, 8.0, -11.5, -3.5),
                                              (2.0, 7.0, 9.0, -10.0, -5.0))):
        m.cube(ab, *B(-w, y0, z0, w, y1, z1), name=("bump_base", "bump", "bump_top")[k], mat="bump",
               rot=(-9, 0, 0), origin=(0, y + 3, z - 6))
    # the cheeks over the dental batteries (they flex out as it chews)
    for side, sx in (("l", 1), ("r", -1)):
        m.bone(f"cheek_{side}", sk, (3.5 * sx, y - 1, z - 8))
    m.pair("cheek_l", "cheek_r", *B(4, -5, -12, 5, -2, -5), name="cheek", faces=OUT("west"))
    # the lower jaw: a deep dentary and the predentary under the bill
    jaw = m.bone("jaw", sk, (0, y - 4, z - 3))
    m.cube(jaw, *B(-3.5, -9, -13, 3.5, -5, -2), name="dentary")
    m.cube(jaw, *B(-4, -9, -19, 4, -6, -13), name="predentary", mat="beak", faces=OUT("south"))
    m.cube(jaw, *B(-3, -6.9, -18, 3, -5.9, -3), name="mouth", mat="mouth", faces=["up"])
    # the beak's EDGE: the keratin of the upper bill ran past the bone in a serrated rim (the Edmontosaurus mummies);
    # here a plane of pale denticles hung just outside the lower bill, so the rim shows with the bill shut
    m.pair(sk, sk, *B(4.75, -7.5, -21, 4.75, -5.5, -13), name="denticles", mat="teeth")
    return sk


def neck(m, body):
    """short and thick, in two pieces that taper and overlap (the second starts 4 px inside the first), carried in a
    low S: up from the shoulders, the head held forward and down"""
    n1 = m.bone("neck1", body, (0, 30, -41), (REST["neck1"], 0, 0))
    m.cube(n1, (-6, 21, -53), (6, 35, -38), name="neck1")
    m.cube(n1, (-4.5, 19, -51), (4.5, 22, -40), name="throat", mat="belly", faces=OUT("up"))
    n2 = m.bone("neck2", n1, (0, 30, -50), (REST["neck2"], 0, 0))
    m.cube(n2, (-5, 24, -59.5), (5, 34, -47.5), name="neck2")
    hd = m.bone("head", n2, (0, 30, -59))
    head(m, hd, 30, -59)


def hind_legs(m, body):
    """the walker's leg of a big ornithopod: a long femur deep in the thigh, the knee a little bent, a short
    metatarsus and three broad toes with hoof-like nails; the foot wider than the shin"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (6 * sx, HIP_Y, 0), (REST["thigh"], 0, 2 * sx))
        sh = m.bone(f"shin_{side}", th, (6.5 * sx, 18, 0), (REST["shin"], 0, -2 * sx))
        ft = m.bone(f"foot_{side}", sh, (6.5 * sx, 4, 0), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (6.5 * sx, -2.5, -0.5), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (1.5, 18, -7), (10.5, 42, 7), name="thigh")
    m.pair("thigh_l", "thigh_r", (2, 13, -5), (10, 19, 4), name="knee")
    m.pair("shin_l", "shin_r", (3, 4, -3.5), (10, 17, 2.5), name="shin")
    m.pair("foot_l", "foot_r", (3.5, -3, -3), (9.5, 5, 2), name="meta")
    m.pair("toes_l", "toes_r", (3, -3.5, -6), (10, -1.5, -1), name="pes")
    m.pair("toes_l", "toes_r", (5.5, -4, -8), (7.5, -2, -6), name="nail_mid", mat="hoof", faces=OUT("south"))
    m.pair("toes_l", "toes_r", (7.5, -4, -7), (9.5, -2, -5), name="nail_out", mat="hoof", faces=OUT("south"),
           rot=(0, -12, 0), origin=(8.5, -3, -5.5))
    m.pair("toes_l", "toes_r", (3.5, -4, -7), (5.5, -2, -5), name="nail_in", mat="hoof", faces=OUT("south"),
           rot=(0, 12, 0), origin=(4.5, -3, -5.5))


def fore_legs(m, body):
    """half the hind leg, slender but carrying weight in the grown animal: the upper arm slanting back, the forearm
    forward, the bound metacarpals ending in a hoof-like mitten (the hadrosaur hand)"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (5.5 * sx, 26, -39), (REST["arm"], 0, 6 * sx))
        fa = m.bone(f"forearm_{side}", a, (5.5 * sx, 14, -39), (REST["forearm"], 0, -8 * sx))
        m.bone(f"hand_{side}", fa, (5.5 * sx, 4, -39), (REST["hand"], 0, 2 * sx))
    m.pair("arm_l", "arm_r", (2, 13, -43), (9, 29, -35), name="arm")
    m.pair("forearm_l", "forearm_r", (3, 3, -42), (8, 15, -36), name="forearm")
    m.pair("hand_l", "hand_r", (3.5, -1, -41), (7.5, 5, -37), name="hand")
    m.pair("hand_l", "hand_r", (3, -3, -42), (8, -1, -36), name="mitten")
    m.pair("hand_l", "hand_r", (3.5, -3.5, -43), (7.5, -1.5, -41), name="hand_nail", mat="hoof", faces=OUT("south"))


TAILS = ("tail1", "tail2", "tail3", "tail4")


def tail(m, body):
    """deep and flat-sided, stiff with ossified tendons, tapering in four overlapping pieces (each starts 4 px inside
    the one before; none repeats another's size)"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 9, 34, 7, 27, 44), ("tail2", 30, 53, 5.5, 30.5, 42.5), ("tail3", 49, 68, 4, 33, 40),
        ("tail4", 64, 82, 2.5, 34.5, 38.5)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-5, 24, 8), (5, 28, 23), name="tail_muscle", mat="belly")     # the deep chevrons under the root


def build(saddle_on=True):
    m = P.Model("maiasaura")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, HIP_Y, 0))
    # the trunk: heavy, the hips the highest point, the back sloping gently down to the shoulders, a deep barrel
    m.cube(body, (-7.5, 23, -10), (7.5, 44, 11), name="hips")
    m.cube(body, (-4.5, 43, -8), (4.5, 46, 9), name="sacrum")
    m.cube(body, (-8.5, 17, -30), (8.5, 41, -8), name="torso", rot=(-7, 0, 0), origin=(0, 31, -18))
    m.cube(body, (-7.5, 17, -46), (7.5, 37, -27), name="chest", rot=(-12, 0, 0), origin=(0, 27, -36))
    m.cube(body, (-6.5, 15, -33), (6.5, 18, -9), name="belly", mat="belly")
    neck(m, body)
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the saddle: the "Sela de Ninhal"
SADDLE_PAL = {   # its own: a broad woven reed mat, cured hide, two saddlebags of plaited bark fibre, a wooden frame
    "W0": hx("6a5a34"), "W1": hx("8a7848"), "W2": hx("a8945c"), "W3": hx("4c5a30"),      # reed weave, green weft
    "H0": hx("3a2a1e"), "H1": hx("5a4230"), "H2": hx("7a5a40"), "H3": hx("947252"),      # cured hide
    "L0": hx("2a1e16"), "L1": hx("44301f"),                                              # dark leather
    "G0": hx("5e4a30"), "G1": hx("7c6440"), "G2": hx("98804e"),                          # bark-fibre bags
    "C0": hx("6a5a3e"), "C1": hx("8c7a54"), "D0": hx("4a3826"), "D1": hx("6c5436"),       # cord, wood
}


def saddle(m, body):
    """The nesting-ground saddle (study 15: "uma Sela de Ninhal larga, com alforjes"): a broad mat of woven reeds
    over the back behind the shoulders, a low hide seat on a wooden frame, a pair of deep saddlebags of plaited bark
    fibre at the flanks (for leaves and eggs: its four rows of cargo), a cord girth. Faces lying on the body are
    left out (no back-face culling in GeckoLib)."""
    sd = m.bone("saddle", body, (0, 39, -18), (-6, 0, 0))
    m.cube(sd, (-9, 39, -29), (9, 40, -9), name="mat", mat="weave", faces=OUT("down"))
    m.pair(sd, sd, (9, 31, -28), (10, 39, -10), name="mat_side", mat="weave", faces=OUT("west"))
    m.cube(sd, (-5, 40, -25), (5, 41, -12), name="seat", mat="hide", faces=OUT("down"))
    m.cube(sd, (-4, 41, -14), (4, 44, -12), name="cantle", mat="wood")
    m.cube(sd, (-2, 41, -26), (2, 43, -24), name="pommel", mat="wood")
    m.pair(sd, sd, (10, 24, -25), (13, 33, -15), name="bag", mat="bag")
    m.pair(sd, sd, (10.5, 33, -23), (11.5, 39, -22), name="bag_cord", mat="cord", faces=OUT("west"))
    m.pair(sd, sd, (9.5, 17, -21), (10.5, 31, -18), name="girth_side", mat="cord", faces=OUT("west"))
    m.cube(sd, (-9.5, 16, -21), (9.5, 17, -18), name="girth_under", mat="cord", faces=OUT("up"))


def saddle_px(t):
    c = t.cube; mat = c["mat"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "weave":            # a twill of reeds, a green weft every fourth row
        if f == "up" and j % 4 == 2:
            return p["W3"]
        if j == h - 1 and f != "up":
            return p["W0"]
        return p["W2"] if (i + 2 * j) % 3 == 0 else p["W1"]
    if mat == "bag":              # plaited bark fibre, a darker rim and a flap
        if f in ("east", "west") and j <= 1:
            return p["G0"] if j == 1 else p["G2"]
        return p["G1"] if (i + j) % 2 else p["G2"] if f == "up" else p["G1"] if (i * 3 + j) % 5 else p["G0"]
    if mat == "cord":
        return p["C1"] if (i + j) % 3 else p["C0"]
    if mat == "wood":
        return p["D1"] if f == "up" or j == 0 else p["D0"]
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


# ------------------------------------------------------------------ the skin (skin2)
TRUNK = {"hips", "sacrum", "torso", "chest", "neck1", "neck2", "tail1", "tail2", "tail3", "tail4"}
UNDER = {"belly", "throat", "tail_muscle"}
LEG = {"shin", "meta", "pes", "forearm", "hand", "mitten"}
LIMB = {"thigh", "knee", "arm"}
HEAD = {"cranium", "face", "snout", "cheek", "dentary"}

# THE MARKS (drawn, not drawn by lot):
# 1. big loose VERTICAL blotches on the flanks, the shadow of a bush on dry grass: each a soft upright oval from the
#    back down to about the middle of the flank, spaced unevenly along the body (z centre, half width, how low);
# 2. the back a step darker than the flank (the countershading's top band);
# 3. on the male, the hump ochre-rust with its worn crown paler.
BLOTCH = [(-46, 2.6, 0.48), (-34, 3.2, 0.42), (-21, 3.6, 0.36), (-9, 3.4, 0.40), (4, 3.8, 0.34), (17, 3.2, 0.44),
          (31, 3.0, 0.40), (45, 2.6, 0.46), (59, 2.2, 0.52), (72, 1.8, 0.58)]


def body_tone(t, prof, calf=False):
    """the palette key of a body texel: the countershading by the silhouette, the vertical blotches, soft mottle and
    the small pebbly tubercles of hadrosaur skin a tone step deep"""
    n = t.cube["name"]; f = t.face
    z, y = t.P[2], t.P[1]
    if f == "down" or n in UNDER:
        h = 0.0 if f == "down" else min(0.18, prof.height(t))
    elif f == "up":
        hw = max(1.0, (t.cube["to"][0] - t.cube["from"][0]) / 2.0)
        h = 1.0 - 0.3 * min(1.0, abs(t.P[0]) / hw)
    else:
        h = prof.height(t)
    b = skin2.bands(h, z, (0.20, 0.28, 0.50, 0.80), amp=0.05, seed=21)
    if b == 0:
        u, v = skin2.surface_uv(t)
        k = skin2.scales(t, cell=3.0, seed=23)
        return "b1" if k == "base" else "b0"
    base = ["b1", "b0", "k4", "k3", "k2"][b]
    if calf:          # the calf: smooth, no blotches, only the countershading and a soft mottle
        return skin2.step(base, skin2.mottle(t, cell=10, strength=0.24, seed=27)) if b >= 2 else base
    if f in ("east", "west") and n in TRUNK:
        for k, (zc, half, low) in enumerate(BLOTCH):
            edge = half + 1.1 * (skin2.soft(*skin2.surface_uv(t), 2.6, seed=40 + k) - 0.5)
            top = 0.80 - 0.05 * math.sin(k * 1.7)
            if abs(z - zc) < edge and low < h < top and b < 4:
                torn = h < low + 0.08 and skin2.soft(*skin2.surface_uv(t), 1.8, seed=60 + k) < 0.45
                if not torn:
                    return skin2.step(base, -1)
    if b >= 2:
        base = skin2.step(base, skin2.mottle(t, cell=11, strength=0.24, seed=24))
        # the hadrosaur's small even tubercles (Parks 1922): a tone step on the shaded side of each, in body space
        if skin2.fleck(t, every=37, seed=25):
            base = skin2.step(base, -1)
    return base


def limb_tone(t):
    """legs: calm, lit on the front, a step darker behind and below; scutes across the front of the foot"""
    n = t.cube["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    v = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    if n in ("thigh", "knee", "arm"):
        base = "k3"
        if f in ("east", "west") and t.rel[2] > 0.55 and v < 0.45:
            base = "k2"
        if f in ("east", "west", "north") and t.rel[2] < 0.3 and 0.3 < v < 0.8:
            base = "k4"
        if f in ("south", "down"):
            base = "k2"
        return skin2.step(base, skin2.mottle(t, cell=7, strength=0.22, seed=16))
    base = "k3" if f in ("north", "up", "east", "west") else "k2"
    if n in ("meta", "pes", "mitten", "hand") and f in ("north", "up"):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 2
        if k == 0 and (t.i % 3) != 1:
            return skin2.step(base, -1)
    if skin2.scales(t, cell=3.4, seed=17, flat=0.5) == "edge":
        return skin2.step(base, -1)
    return base


# ------------------------------------------------------------------ padrão v3: the Maiasaura's own head
# (docs/estudos/14, "Padrão v3": the engine only measures, every part below is drawn for this animal alone)
#
# THE MOTIF: small PEBBLE scales on the face (round, a step darker on the seam), a band of slightly bigger ones on the
# muzzle, and on the hump big FLAT scales, paler (sc0..sc2), each a plate with a dark seam on its lower side. The face is
# a little lighter than the neck (study 15). The beak: dark olive keratin with a pale serrated rim (the denticles) and,
# behind it, the skin lip over the dental battery, pale with a dark mouth line under it.
HL = ["k1", "k2", "k3", "k4", "k5", "sc0", "sc1", "sc2"]


def hstep(key, d):
    return HL[max(0, min(len(HL) - 1, HL.index(key) + d))] if key in HL else skin2.step(key, d)


def pebble(t, cell=2.0, seed=0):
    """small round pebble scales of the face: 'edge' on the shaded seam, 'base' inside, 'hi' a lit centre now and
    then (one in three); body space, so they run on from cube to cube"""
    k = skin2.scales(t, cell=cell, seed=seed, flat=0.8)
    if k == "edge":
        return -1
    u, v = skin2.surface_uv(t)
    if h32(math.floor(u / cell), math.floor(v / cell), seed, 9) % 3 == 0 and (math.floor(u) + math.floor(v)) % 2:
        return 1
    return 0


def head_tone(t, sex):
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "b1"
    if n == "dentary":
        if f == "up":
            return "k3"
        if t.j == 0:
            return "lip"                       # the lower lip, the line the shut mouth reads by
        base = "b1" if t.rel[1] < 0.45 else "k4"
        return skin2.step(base, min(0, pebble(t, 1.8, 33)))
    if n == "cheek":
        if t.j == t.h - 1:
            return "k1"                         # the mouth line under the skin lip
        if t.j == t.h - 2:
            return "lip"                        # the skin lip over the dental battery
        return hstep("k4", pebble(t, 1.9, 34))
    if f == "up":                               # the roof: a step lighter, pebbles
        return hstep("k5", pebble(t, 2.2, 21))
    hv = (t.P[1] - HEAD_Y[0]) / max(1.0, HEAD_Y[1] - HEAD_Y[0])
    base = ["k3", "k4", "k5"][skin2.bands(hv, t.P[2] * 2.0, (0.30, 0.68), amp=0.06, seed=31)]
    if n in ("face", "snout") and f in ("east", "west", "north"):
        if t.j == t.h - 1:
            return "k1"                         # the mouth line along the face
        return hstep(base, pebble(t, 2.6, 9))   # the muzzle: bigger pebbles
    if n == "cranium" and f in ("east", "west"):
        # the eye's pale lower lid runs back into a soft fold under the eye
        dz = t.P[2] - EYE[0]; dy = t.P[1] - EYE[1]
        if -2.5 < dz < 2.5 and -3.6 < dy < -2.6:
            return "k5"
    return hstep(base, pebble(t, 2.0, 32))


def bump_px(t, p, sex):
    """the hump: big flat pale scales on the bone, a dark seam under each; the male's skin there ochre-rust with the
    worn crown paler; the female's the face's own pale"""
    n = t.cube["name"]; f = t.face
    k = ("bump_base", "bump", "bump_top").index(n)
    plate = skin2.scales(t, cell=3.4, seed=70 + k, flat=0.9)
    if k == 0:                                   # the foot of the hump: the face's own skin in flat scales
        key = "sc0" if f == "up" else "k5"
        if sex == "male" and f != "up" and t.j == 0 and skin2.soft(*skin2.surface_uv(t), 1.4, seed=77) > 0.45:
            key = "oc1"                          # the ochre creeping down onto its foot, in patches
        if plate == "edge":
            key = hstep(key, -2) if key != "oc1" else "oc0"
        return p[key]
    if sex == "male":
        ramp = ("oc0", "oc1", "oc2")
        if f == "up":
            # the crown worn pale (bone showing through the skin, study 15: "a ponta gasta mais clara"), the ochre on
            # the slopes round it: a hump of bone flushed with colour, not a cap (the Edmontosaurus' comb is a lid of red)
            key = ("sc2" if (t.i + 2 * t.j) % 4 else "sc1") if k == 2 else ramp[2] if (t.i + t.j) % 3 else "sc1"
        elif k == 2 and t.j == 0:
            key = "sc1"
        else:
            key = ramp[1] if k > 0 or t.j < t.h - 1 else ramp[0]
        if plate == "edge" and f != "up":
            key = {"oc2": "oc1", "oc1": "oc0", "oc0": "k2", "sc1": "oc2", "sc2": "sc1"}[key]
        return p[key]
    key = ("sc0", "sc1", "sc2")[k] if f == "up" else ("k5", "sc0", "sc1")[k]
    if plate == "edge":
        key = hstep(key, -2)
    return p[key]


def denticles(t, p):
    """the beak's serrated rim: pale keratin denticles of one texel, uneven in length and spacing (worn, a chip
    missing, a longer one), hanging from the bill's edge. Columns from the FRONT, row 0 at the TOP"""
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2] - t.cube["from"][2])); row = t.j
    # length (rows) of the denticle in each column from the front; 0 = a gap
    LEN = (1, 2, 0, 1, 1, 2, 0, 1)
    if col >= len(LEN) or row >= LEN[col]:
        return None
    return p["tooth2"] if row == 1 or col in (3, 9) else p["tooth"]


def beak_px(t, p):
    n = t.cube["name"]; f = t.face
    if f == "up":
        return p["bk2"] if (t.i * 2 + t.j) % 5 else p["bk1"]
    if f == "down":
        return p["bk0"]
    if n in ("bill", "bill_tip") and t.j == t.h - 1:
        return p["tooth2"]                       # the paler cutting edge of the upper bill
    if n == "predentary" and t.j == 0:
        return p["bk2"]
    return p["bk1"] if t.j > 0 else p["bk2"]


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
        if mat == "bump":
            return bump_px(t, p, sex)
        if mat == "beak":
            return beak_px(t, p)
        if mat == "teeth":
            return denticles(t, p)
        if mat == "mouth":
            return p["tongue"] if (t.i + t.j) % 4 else p["gum"]
        if n in TRUNK or n in UNDER:
            return p[body_tone(t, PROF[0], calf)]
        if n in LEG or n in LIMB:
            return p[limb_tone(t)]
        if n in HEAD:
            return p[head_tone(t, sex)]
        return p["k3"]
    return sh


PROF = [None]
HEAD_Y = [0.0, 1.0]
EYE = [0.0, 0.0]

# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP
# THE EYE: medium, set BEHIND and BELOW the hump at the front of the braincase; a castanho-amber iris round a round
# pupil, the glint high at the back (the light from over the hump), the hump's shadow its upper lid and a THICK PALE
# lower lid of two rows, the lower one shorter
EYE_ART = [
    "kddd.",
    "diipg",
    "dIppi",
    ".iII.",
    ".LLLL",
    "..ll.",
]
NOSTRIL = [      # the nostril high at the back of the bill in its long shallow hollow
    "hhhh.",
    "nnnhh",
    ".nn..",
]


def decals_for(sex):
    p = pal_for(sex)
    cm = {"d": p["k1"], "k": p["k0"], "g": p["glint"], "i": p["iris"], "I": p["iris2"], "p": p["pupil"],
          "L": p["lid"], "l": p["lid2"], "n": p["k0"], "h": p["k2"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", EYE_ART, cm, at=(1, 2))
        P.stamp(img, m, C["snout"], "east", NOSTRIL, cm, at=(0, 1))
    return dec


def paint_sex(m, sex="male"):
    PROF[0] = skin2.Profile(m, TRUNK | UNDER)
    import geo
    pts = {c["name"]: q for c, q in geo.cube_points(m.spec())}
    ys = [pts[n][:, 1] for n in ("cranium", "face", "snout")]
    HEAD_Y[:] = [min(a.min() for a in ys), max(a.max() for a in ys)]
    cr = pts["cranium"]
    EYE[:] = [float(cr[:, 2].min()) + 3.0, float(cr[:, 1].max()) - 3.5]
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
