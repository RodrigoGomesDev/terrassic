"""Corythosaurus casuarius, made by hand from its own study (docs/estudos/15_HERBIVOROS_1_11.md, approved by Rodrigo on
10/11/2026). Real size 9 m (Benson et al. 2012: ~9 m on average; Rodrigo's answer: as it is, the top).

The second herbivore of the 1.10 standard (docs/estudos/14_POR_QUE_PARECE_IA.md, "Padrão v3"), after the Maiasaura:
- one texel = one Minecraft pixel: drawn at skin2.PX_PER_M (16.94 px per metre), shown at a model scale of ~1;
- the skin in BODY space (skin2): dark back, middle flank, pale belly as one shape, a calm base, marks DRAWN;
- the head drawn from its own anatomy (padrão v3): its own eye, beak edge, nostril, skin motif, accent and mouth;
- item 4 of study 14: the neck and the tail taper in overlapping pieces whose skin runs on, never equal boxes.

What makes it read as itself and NOT as the remade Parasaurolophus, Edmontosaurus or Maiasaura (study 15):
1. the HELMET: a tall crest flattened from the sides, a HALF-MOON standing UP over the head (the nasals, prefrontals and
   frontals, Brown 1914) - a plate standing on the head, not a tube running back (Parasaurolophus), a comb of flesh
   (Edmontosaurus) nor a low hump (Maiasaura); drawn ~25% bigger than the bone (study 14, C), and a little bigger in
   the male (Rodrigo's decision: male_display adds the upper rim);
2. the HEAD under it: a SHORT, NARROW snout with a shallow beak of straight smooth edge (a choosy browser, Benson et
   al. 2012), a BIG eye (an animal of the half-light, Schmitz & Motani 2011) set low under the back of the helmet;
3. the POSTURE: high at the withers (tall neural spines make a low ridge from the shoulders to the tail) and the neck
   carried UP, the helmet held high like a listening ear; the legs long, the lightest and fastest of the hadrosaurs;
4. the colour "azul-fumaça" (the cassowary of its name: a dark matte body and a coloured head): slate-blue, darker on
   the back and the spine ridge, thin pale VERTICAL stripes on the flanks and thighs (the bongo and the okapi of the
   forest), a pale grey belly; the male's helmet TERRACOTTA on its sides, the female's slate with thin pale bars;
5. the skin: big POLYGONAL tuberculate scales on the flanks and tail (Brown 1916), a mosaic on the helmet.
"""
import math

import proto as P
import skin2
from proto import hx, h32

TEX_W = 256
PX_M = skin2.PX_PER_M
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# ------------------------------------------------------------------ palette ("azul-fumaça", study 15)
# k0..k5 the body ramp (slate night to fumaça-clara), b0..b3 the misty grey belly and stripes, tc the male's
# terracotta helmet, sl the female's slate helmet, kl the helmet's keel, bk the beak
SCHEME = {
    "k0": "1f2836", "k1": "283446", "k2": "3e5068", "k3": "5a7290", "k4": "6e86a4", "k5": "8399b4",
    "b0": "a3abb7", "b1": "b6bcc6", "b2": "c8ccd4", "b3": "d8dbe0",
    "tc0": "7a3424", "tc1": "9c432e", "tc2": "b5543a", "tc3": "c8704f",
    "kl0": "1b1d22", "kl1": "33363c", "kl2": "5c5f63",
    "bk0": "22252b", "bk1": "3a3f48", "bk2": "565c66", "lip": "8b97a6",
    "female": {"tc0": "3e4b5e", "tc1": "52627a", "tc2": "687b94", "tc3": "a6b3c4"},
}
PAL = {
    "iris": hx("cdd2d6"), "iris2": hx("98a1aa"), "pupil": hx("0b0c0f"), "glint": hx("f6f8fa"),
    "ring": hx("8e9cae"), "ring2": hx("a7b2c0"),
    "mouth": hx("3a2428"), "tongue": hx("7e5058"), "gum": hx("5c3640"),
    "edge": hx("d6d2c4"), "edge2": hx("aaa596"),
    "hoof0": hx("1c1f24"), "hoof1": hx("34383f"), "hoof2": hx("51565e"),
}
# the calf: a paler smoke with the stripes bolder (the young hide in the undergrowth), no helmet colour
CALF = {"k0": "3c4654", "k1": "4c5868", "k2": "64748a", "k3": "7a8ba0", "k4": "8d9db0", "k5": "a0aec0"}


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
# Model px at PX_M, the hip joint at z = 0, the ground at y = 0 (after _ground), the beak toward -z.
# Signs (geo.rot_matrix): +x lifts what lies in front (-z) and lowers what lies behind (+z); a hanging limb with +x
# swings its far end forward.
REST = {"neck1": 68, "neck2": -22, "skull": -46,
        "thigh": 10, "shin": -24, "foot": 28, "toes": -14,
        "arm": -12, "forearm": 18, "hand": -6,
        "tail1": 3, "tail2": 1, "tail3": 0, "tail4": 0}
HIP_Y = 39
SADDLE_MATS = ("hide", "leather", "bark", "fringe", "cord", "bone")


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes})
             if c["mat"] not in SADDLE_MATS + ("teeth",))
    m.shift(-lo)


# the helmet in profile: a half-moon of layers, each starting inside the one under it, the plate thin from the sides.
# (half width, y0, y1, z0, z1) in skull space; the male's upper rim is its own bone (male_display)
# the front rises steep from the snout, the back curves down over the braincase (Brown 1914, AMNH 5240)
HELMET = ((1.5, -1.0, 3.0, -16.0, 1.0), (1.5, 3.0, 5.0, -16.0, 0.0), (1.5, 5.0, 7.0, -15.0, -1.0),
          (1.0, 7.0, 9.0, -14.0, -3.0), (1.0, 9.0, 10.0, -12.0, -5.0))
HELMET_MALE = ((1.0, 10.0, 12.0, -11.0, -6.0),)


def head(m, parent, y, z):
    """the short narrow skull under the tall half-moon helmet, the shallow beak, the cheeks and the jaw.
    (y, z): the occipital joint. 21 px from the occiput to the beak tip, the helmet 14 to 16 px over the roof"""
    sk = m.bone("skull", parent, (0, y, z), (REST["skull"], 0, 0))

    def B(x0, y0, z0, x1, y1, z1):
        return (x0, y + y0, z + z0), (x1, y + y1, z + z1)
    # a braincase low and narrow under the helmet with the big eye at its front, a short face, a NARROW shallow snout
    m.cube(sk, *B(-4, -6, -7, 4, 2, 1), name="cranium")
    m.cube(sk, *B(-3.5, -5, -12, 3.5, 1, -6), name="face", faces=OUT("south"))
    m.cube(sk, *B(-2.5, -5, -19, 2.5, -1, -12), name="snout", faces=OUT("south"))
    # the shallow beak, narrow, its edge straight and smooth (no denticles: a choosy browser)
    m.cube(sk, *B(-3, -5.5, -23, 3, -2.5, -18), name="beak", mat="beak", faces=OUT("south"))
    # THE HELMET (adult_crest: the calf has none, only a high brow, young_crest)
    hc = m.bone("adult_crest", sk, (0, y + 2, z - 7))
    for k, (w, y0, y1, z0, z1) in enumerate(HELMET):
        m.cube(hc, *B(-w, y0, z0, w, y1, z1), name=f"helmet{k}", mat="helmet", hk=k)
    md = m.bone("male_display", hc, (0, y + 10, z - 8))
    for k, (w, y0, y1, z0, z1) in enumerate(HELMET_MALE):
        m.cube(md, *B(-w, y0, z0, w, y1, z1), name="helmet_rim", mat="helmet", hk=4)
    yc = m.bone("young_crest", sk, (0, y + 2, z - 7))
    m.cube(yc, *B(-2.5, 1, -12, 2.5, 4, -2), name="young_brow", mat="helmet", hk=0)
    # the cheeks over the dental batteries (they flex out as it chews)
    for side, sx in (("l", 1), ("r", -1)):
        m.bone(f"cheek_{side}", sk, (3 * sx, y - 1, z - 8))
    m.pair("cheek_l", "cheek_r", *B(3.5, -5, -12, 4.5, -2, -5), name="cheek", faces=OUT("west"))
    # the lower jaw: a slim dentary and the predentary under the beak
    jaw = m.bone("jaw", sk, (0, y - 4, z - 3))
    m.cube(jaw, *B(-3, -8, -13, 3, -5, -2), name="dentary")
    m.cube(jaw, *B(-3, -8, -23, 3, -5, -13), name="predentary", mat="beak", faces=OUT("south"))
    m.cube(jaw, *B(-2.5, -5.9, -20, 2.5, -4.9, -3), name="mouth", mat="mouth", faces=["up"])
    # the beak's EDGE: straight and smooth, the pale cutting rim of the keratin, one even line along the lower beak
    m.pair(sk, sk, *B(3.25, -6.5, -23, 3.25, -5.5, -16), name="beak_edge", mat="teeth")
    return sk


def neck(m, body):
    """longer and slimmer than the Maiasaura's, carried UP: two pieces that taper and overlap (the second starts 4 px
    inside the first), the head high with the helmet over the herd"""
    n1 = m.bone("neck1", body, (0, 36, -43), (REST["neck1"], 0, 0))
    m.cube(n1, (-5, 28, -61), (5, 40, -40), name="neck1")
    m.cube(n1, (-3.5, 26, -59), (3.5, 29, -42), name="throat", mat="belly", faces=OUT("up"))
    n2 = m.bone("neck2", n1, (0, 35, -58), (REST["neck2"], 0, 0))
    m.cube(n2, (-4, 30, -70), (4, 37, -57), name="neck2")
    m.cube(n2, (-3, 28, -70), (3, 31, -58), name="throat2", mat="belly", faces=OUT("up"))
    hd = m.bone("head", n2, (0, 35, -70))
    head(m, hd, 35, -70)


def hind_legs(m, body):
    """long legs for a hadrosaur (the fastest of the three): the femur deep in the thigh, a long shin and metatarsus,
    three toes with hoof-like nails"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (6 * sx, HIP_Y, 0), (REST["thigh"], 0, 2 * sx))
        sh = m.bone(f"shin_{side}", th, (6.5 * sx, 20, 0), (REST["shin"], 0, -2 * sx))
        ft = m.bone(f"foot_{side}", sh, (6.5 * sx, 5, 0), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (6.5 * sx, -2.5, -0.5), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (2, 20, -6.5), (9, 45, 6.5), name="thigh")
    m.pair("thigh_l", "thigh_r", (2.5, 15, -4.5), (9.5, 21, 3.5), name="knee")
    m.pair("shin_l", "shin_r", (3.5, 5, -3), (9.5, 19, 2), name="shin")
    m.pair("foot_l", "foot_r", (4, -3, -2.5), (9, 6, 1.5), name="meta")
    m.pair("toes_l", "toes_r", (3.5, -3.5, -6), (9.5, -1.5, -1), name="pes")
    m.pair("toes_l", "toes_r", (5.5, -4, -8), (7.5, -2, -6), name="nail_mid", mat="hoof", faces=OUT("south"))
    m.pair("toes_l", "toes_r", (7.5, -4, -7), (9.5, -2, -5), name="nail_out", mat="hoof", faces=OUT("south"),
           rot=(0, -12, 0), origin=(8.5, -3, -5.5))
    m.pair("toes_l", "toes_r", (3.5, -4, -7), (5.5, -2, -5), name="nail_in", mat="hoof", faces=OUT("south"),
           rot=(0, 12, 0), origin=(4.5, -3, -5.5))


def fore_legs(m, body):
    """longer than the Maiasaura's (the high withers): the upper arm slanting back, the forearm forward, the bound
    metacarpals ending in a hoof-like mitten"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (5 * sx, 30, -40), (REST["arm"], 0, 5 * sx))
        fa = m.bone(f"forearm_{side}", a, (5 * sx, 16, -40), (REST["forearm"], 0, -7 * sx))
        m.bone(f"hand_{side}", fa, (5 * sx, 4, -40), (REST["hand"], 0, 2 * sx))
    m.pair("arm_l", "arm_r", (2, 15, -43), (8, 33, -37), name="arm")
    m.pair("forearm_l", "forearm_r", (2.5, 3, -42.5), (7.5, 17, -37.5), name="forearm")
    m.pair("hand_l", "hand_r", (3, -1, -42), (7, 5, -38), name="hand")
    m.pair("hand_l", "hand_r", (2.5, -3, -43), (7.5, -1, -37), name="mitten")
    m.pair("hand_l", "hand_r", (3, -3.5, -44), (7, -1.5, -42), name="hand_nail", mat="hoof", faces=OUT("south"))


TAILS = ("tail1", "tail2", "tail3", "tail4")


def tail(m, body):
    """deep and flat-sided (the tall spines over it and long chevrons under it), stiff with ossified tendons, tapering
    in four overlapping pieces (each starts 4 px inside the one before; none repeats another's size); the spine ridge
    runs on along the top of the first two"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 9, 35, 6.5, 29, 48), ("tail2", 31, 56, 5, 32, 46), ("tail3", 52, 72, 3.5, 34, 42),
        ("tail4", 68, 84, 2, 36, 40)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-2.5, 47, 9), (2.5, 51, 31), name="ridge_tail")
    m.cube("tail2", (-2, 45, 31), (2, 48, 48), name="ridge_tail2")
    m.cube("tail1", (-4.5, 25, 8), (4.5, 30, 24), name="tail_muscle", mat="belly")     # the long chevrons under it


def build(saddle_on=True):
    m = P.Model("corythosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, HIP_Y, 0))
    # the trunk: slimmer than the Maiasaura's, the back nearly level from the hips to the HIGH withers
    m.cube(body, (-7, 26, -10), (7, 46, 11), name="hips")
    m.cube(body, (-7.5, 21, -30), (7.5, 44, -8), name="torso", rot=(-3, 0, 0), origin=(0, 33, -18))
    m.cube(body, (-6.5, 21, -47), (6.5, 42, -27), name="chest", rot=(-5, 0, 0), origin=(0, 31, -36))
    m.cube(body, (-5.5, 19, -34), (5.5, 22, -9), name="belly", mat="belly")
    # THE SPINE RIDGE: the tall neural spines make a low ridge from the withers over the hips to the tail
    m.cube(body, (-2.5, 41, -44), (2.5, 46, -27), name="ridge_withers", rot=(-5, 0, 0), origin=(0, 31, -36))
    m.cube(body, (-3, 43, -29), (3, 49, -8), name="ridge_back", rot=(-3, 0, 0), origin=(0, 33, -18))
    m.cube(body, (-3, 45, -10), (3, 51, 11), name="ridge_hips")
    neck(m, body)
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the saddle: the forest saddle ("sela de mata")
SADDLE_PAL = {   # its own: low and narrow for riding under branches; a pad of beaten bark cloth, dark hide, a bone grip
    "K0": hx("3a3424"), "K1": hx("54492e"), "K2": hx("6e6038"), "K3": hx("4a5434"),      # bark cloth, a moss-green seam
    "H0": hx("2a2420"), "H1": hx("443830"), "H2": hx("5e4c40"), "H3": hx("766252"),      # dark hide
    "L0": hx("221a16"), "L1": hx("3a2c22"),                                              # leather
    "F0": hx("4c5a3a"), "F1": hx("66744c"),                                              # fringe of dyed strips
    "C0": hx("5e5440"), "C1": hx("7c7056"), "B0": hx("bcb49c"), "B1": hx("dcd6c2"),      # cord, bone
}


def saddle(m, body):
    """The forest saddle (study 15: "sela de mata, baixa e estreita"): a NARROW pad of beaten bark cloth over the
    spine ridge behind the withers, a low hide seat with no high cantle (nothing to catch on a branch), a bone grip
    to duck behind, a fringe of dyed strips along the pad, a cord girth. Faces lying on the body are left out."""
    sd = m.bone("saddle", body, (0, 47, -20), (-4, 0, 0))
    m.cube(sd, (-6, 47, -31), (6, 48, -9), name="pad", mat="bark", faces=OUT("down"))
    m.pair(sd, sd, (6, 41, -30), (7, 47, -10), name="pad_side", mat="bark", faces=OUT("west"))
    m.pair(sd, sd, (6.5, 39, -29), (7.5, 41, -11), name="fringe", mat="fringe", faces=OUT("west"))
    m.cube(sd, (-4, 48, -27), (4, 49, -13), name="seat", mat="hide", faces=OUT("down"))
    m.cube(sd, (-3, 49, -15), (3, 50, -13), name="cantle", mat="leather")
    m.cube(sd, (-1, 49, -29), (1, 53, -27), name="grip", mat="bone")
    m.cube(sd, (-2, 52, -29.5), (2, 53, -26.5), name="grip_top", mat="bone")
    m.pair(sd, sd, (7, 21, -23), (8, 41, -20), name="girth_side", mat="cord", faces=OUT("west"))
    m.cube(sd, (-7.5, 20, -23), (7.5, 21, -20), name="girth_under", mat="cord", faces=OUT("up"))


def saddle_px(t):
    c = t.cube; mat = c["mat"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "bark":             # beaten bark cloth: long fibres along the body, a moss-green seam near the edge
        if f == "up" and (i == 1 or i == w - 2):
            return p["K3"]
        if j == h - 1 and f != "up":
            return p["K0"]
        return p["K2"] if h32(i // 3, j, 5) % 4 == 0 else p["K1"]
    if mat == "fringe":           # strips of dyed hide hanging from the pad
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


# ------------------------------------------------------------------ the skin (skin2)
TRUNK = {"hips", "torso", "chest", "neck1", "neck2", "tail1", "tail2", "tail3", "tail4",
         "ridge_withers", "ridge_back", "ridge_hips", "ridge_tail", "ridge_tail2"}
RIDGE = {"ridge_withers", "ridge_back", "ridge_hips", "ridge_tail", "ridge_tail2"}
UNDER = {"belly", "throat", "throat2", "tail_muscle"}
NECK = {"neck1", "neck2"}
LEG = {"shin", "meta", "pes", "forearm", "hand", "mitten"}
LIMB = {"thigh", "knee", "arm"}
HEAD = {"cranium", "face", "snout", "cheek", "dentary"}

# THE MARKS (drawn, not drawn by lot):
# 1. thin pale VERTICAL stripes on the flanks and the thighs (the bongo's and the okapi's: a forest animal broken up
#    in the light through the trees), 1 to 2 texels wide, from just under the ridge down into the flank, uneven in
#    spacing, the ones on the rump and the thigh longer; none on the neck or the tail tip;
# 2. the back and the spine ridge a step darker (ardósia-breu), the legs darker;
# 3. big POLYGONAL scales in a mosaic on the flanks and the tail (Brown 1916), their seams a step deep.
STRIPES = [(-41, 0.9, 0.52), (-33, 0.7, 0.46), (-26, 1.0, 0.40), (-17, 0.8, 0.44), (-9, 1.0, 0.36), (-1, 0.9, 0.34),
           (6, 1.0, 0.30), (13, 0.8, 0.36), (21, 0.9, 0.42), (30, 0.7, 0.50), (38, 0.6, 0.58)]
THIGH_STRIPES = [(-4.5, 0.6), (-1.0, 0.7), (2.5, 0.6)]


def body_tone(t, prof, calf=False):
    """the palette key of a body texel: the countershading by the silhouette, the dark ridge, the thin pale stripes,
    and the polygonal scale mosaic a tone step deep at the seams"""
    n = t.cube["name"]; f = t.face
    z, y = t.P[2], t.P[1]
    if n in RIDGE:
        return "k1" if f == "up" or t.j < 2 else "k2"
    if n in NECK and f in ("down", "north", "south"):
        # the front of the raised neck: a grey throat stripe, darker than the belly, softly mottled
        return skin2.step("b0", min(0, skin2.mottle(t, cell=6, strength=0.2, seed=38)))
    if n in ("throat", "throat2"):
        return "b1" if f != "down" else "b0"
    if f == "down" or n in UNDER:
        h = 0.0 if f == "down" else min(0.18, prof.height(t))
    elif f == "up":
        hw = max(1.0, (t.cube["to"][0] - t.cube["from"][0]) / 2.0)
        h = 1.0 - 0.3 * min(1.0, abs(t.P[0]) / hw)
    elif n in NECK:
        h = 0.20 + 0.72 * float(t.rel[1])      # the neck stands up: its own height, not the body's profile
    else:
        h = prof.height(t)
    b = skin2.bands(h, z, (0.18, 0.26, 0.52, 0.80), amp=0.05, seed=31)
    if b == 0:
        return "b2" if skin2.scales(t, cell=3.6, seed=33, flat=0.5) == "base" else "b1"
    base = ["b1", "b0", "k4", "k3", "k2"][b]
    if f in ("east", "west") and n in TRUNK and b >= 2:
        for k, (zc, half, low) in enumerate(STRIPES):
            wob = 0.5 * math.sin(y * 0.55 + k * 1.3)
            if abs(z - zc - wob) < half and low < h < 0.86:
                torn = skin2.soft(*skin2.surface_uv(t), 2.2, seed=90 + k) < (0.32 if not calf else 0.2)
                if not torn:
                    return "b0" if b == 2 else "k5"
    if calf:
        return skin2.step(base, skin2.mottle(t, cell=10, strength=0.26, seed=37)) if b >= 2 else base
    if b >= 2:
        base = skin2.step(base, skin2.mottle(t, cell=15, strength=0.34, seed=34))
        # the polygonal tuberculate scales (Brown 1916) on the lower flank and the tail: whole seams a tone step deep
        # round cells of ~4.5 px, in body space (no loose specks)
        if (h < 0.5 or z > 20) and skin2.scales(t, cell=4.6, seed=35, flat=0.35) == "edge":
            base = skin2.step(base, -1)
    return base


def limb_tone(t):
    """legs: darker than the body (the study: "as patas são mais escuras"), thin pale stripes across the back of the
    thigh, scutes over the front of the foot"""
    n = t.cube["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    v = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    if n in ("thigh", "knee", "arm"):
        base = "k3"
        if f in ("east", "west") and t.rel[2] > 0.55 and v < 0.45:
            base = "k2"
        if f in ("south", "down"):
            base = "k2"
        if n == "thigh" and f in ("east", "west") and v > 0.25:
            zr = t.P[2]
            for zc, half in THIGH_STRIPES:
                if abs(zr - zc - 0.5 * math.sin(t.P[1] * 0.6)) < half:
                    return "b0"
        return skin2.step(base, skin2.mottle(t, cell=7, strength=0.24, seed=16))
    base = "k2" if f in ("north", "up", "east", "west") else "k1"
    if n in ("meta", "pes", "mitten", "hand") and f in ("north", "up"):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 2
        if k == 0 and (t.i % 3) != 1:
            return skin2.step(base, -1)
    return skin2.step(base, skin2.mottle(t, cell=6, strength=0.3, seed=18))


# ------------------------------------------------------------------ padrão v3: the Corythosaurus' own head
# (docs/estudos/14, "Padrão v3": the engine only measures, every part below is drawn for this animal alone)
#
# THE MOTIF: the helmet IS the head. Its sides carry BIG POLYGONAL scales in a mosaic, 2 to 3 texels, the seams a tone
# below, getting smaller toward the rim; the top edge is a smooth KEEL of dark keratin, worn paler at the front. The
# face below is small irregular scales, the throat pale and smooth. The beak: dark slate keratin with a straight
# smooth pale cutting edge (no denticles) and the lip running up in a line to under the helmet.
HL = ["k1", "k2", "k3", "k4", "k5"]


def hstep(key, d):
    return HL[max(0, min(len(HL) - 1, HL.index(key) + d))] if key in HL else skin2.step(key, d)


def poly(t, cell, seed):
    """a polygon mosaic in body space: -1 on the seams (both sides of the joint, so the cells read as plates), 0 inside,
    +1 a lit plate now and then"""
    k = skin2.scales(t, cell=cell, seed=seed, flat=1.0)
    if k == "edge":
        return -1
    u, v = skin2.surface_uv(t)
    if h32(math.floor(u / cell), math.floor(v / cell), seed, 3) % 4 == 0:
        return 1
    return 0


def head_tone(t, sex):
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "b2"
    if n == "dentary":
        if f == "up":
            return "k3"
        if t.j == 0:
            return "lip"                       # the lower lip, the line the shut mouth reads by
        base = "b2" if t.rel[1] < 0.5 else "b1"   # the throat pale and smooth
        return base
    if n == "cheek":
        if t.j == t.h - 1:
            return "k0"                         # the mouth line under the skin lip
        if t.j == t.h - 2:
            return "lip"                        # the lip, rising in a line to under the helmet
        return hstep("k3", -1 if skin2.scales(t, cell=1.8, seed=44, flat=0.7) == "edge" else 0)
    if f == "up":
        return hstep("k3", -1 if skin2.scales(t, cell=2.0, seed=41, flat=0.7) == "edge" else 0)
    hv = (t.P[1] - HEAD_Y[0]) / max(1.0, HEAD_Y[1] - HEAD_Y[0])
    base = ["k2", "k3", "k4"][skin2.bands(hv, t.P[2] * 2.0, (0.30, 0.70), amp=0.06, seed=42)]
    if n in ("face", "snout", "cranium") and f in ("east", "west", "north") and t.j == t.h - 1 and n != "cranium":
        return "k0"                             # the mouth line along the face
    if n == "cranium" and f in ("east", "west"):
        # the pale ring of bare skin round the big eye, wider under it
        dz = t.P[2] - EYE[0]; dy = t.P[1] - EYE[1]
        if dz * dz / 9.0 + dy * dy / 7.0 < 1.0 and not (abs(dz) < 2.0 and abs(dy) < 1.6):
            return "ring2" if dy < -1.0 else "ring"
    # small irregular face scales, an uneven tone between them (not the Maiasaura's pebbles: angular, smaller)
    k = skin2.scales(t, cell=1.7, seed=43, flat=0.55)
    return hstep(base, -1 if k == "edge" else 0)


def helmet_px(t, p, sex):
    """the helmet: polygonal plates in a mosaic, shrinking toward the rim, the seams a tone below; the smooth dark keel
    along the top edge, worn paler at the front. The male's sides TERRACOTTA running down from the keel and fading
    before the eye; the female's slate with thin pale bars; the calf's brow the face's own"""
    n = t.cube["name"]; f = t.face; k = t.cube.get("hk", 0)
    u, v = skin2.surface_uv(t)
    if sex == "baby" or n == "young_brow":
        return p[hstep("k4", -1 if skin2.scales(t, cell=2.0, seed=46, flat=0.7) == "edge" else 0)]
    top = HELMET_TOP[0]
    up = (t.P[1] - top[0]) / max(1.0, top[1] - top[0])       # 0 at the helmet's foot, 1 at the keel
    if f == "up" or (f in ("north", "south") and up > 0.85):
        # the keel: smooth dark keratin, worn paler toward the front
        worn = (t.P[2] - HELMET_Z[0]) / max(1.0, HELMET_Z[1] - HELMET_Z[0]) < 0.35
        return p["kl2"] if worn and (t.i + t.j) % 3 else p["kl1"] if not worn or (t.i + t.j) % 3 == 0 else p["kl2"]
    cell = 2.9 - 1.1 * up                                    # big plates at the foot, smaller to the rim
    d = poly(t, cell, 50 + k)
    if f in ("north", "south"):
        d = min(d, 0)
    if sex == "male":
        # the terracotta field: from the keel down, its lower edge wandering, gone before the eye
        edge = 0.42 + 0.08 * math.sin(t.P[2] * 0.7) + 0.06 * (skin2.soft(u, v, 2.5, seed=52) - 0.5)
        if up > edge:
            return p[("tc1", "tc2", "tc3")[1 + d]]
        if up > edge - 0.12 and (t.i + t.j) % 2:
            return p["tc1"]                                   # the field breaks up into the slate in dots
        return p[hstep("k3", d)]
    # the female: slate with thin pale bars across the plate
    if up > 0.25 and (math.floor(t.P[2] * 0.9 + 0.4 * t.P[1]) % 4 == 0):
        return p["tc3"] if d >= 0 else p["tc2"]
    return p[["tc0", "tc1", "tc2"][max(0, min(2, 1 + d))]]


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
    """the straight smooth cutting edge: one even pale line, a shade darker at the back where it meets the lip"""
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
HELMET_TOP = [(0.0, 1.0)]
HELMET_Z = [0.0, 1.0]
EYE = [0.0, 0.0]

# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP
# THE EYE: BIG (an animal of the half-light), set low under the back of the helmet, no brow; a pale silver-grey iris
# round a WIDE round pupil, the glint high, a dark socket rim all round, inside the ring of pale bare skin
EYE_ART = [
    ".kkkk.",
    "kiiigk",
    "kippik",
    "kIppIk",
    ".kIIk.",
]
NOSTRIL = [      # the nostril: a slit high at the back of the narrow beak, its rim darker (the S-bent canal starts here)
    "hhh..",
    "nnnh.",
]


def decals_for(sex):
    p = pal_for(sex)
    cm = {"k": p["k0"], "g": p["glint"], "i": p["iris"], "I": p["iris2"], "p": p["pupil"], "n": p["k0"], "h": p["k1"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", EYE_ART, cm, at=(0, 1))
        P.stamp(img, m, C["snout"], "east", NOSTRIL, cm, at=(1, 1))
    return dec


def paint_sex(m, sex="male"):
    PROF[0] = skin2.Profile(m, (TRUNK | UNDER) - NECK - {"throat", "throat2"})
    import geo
    pts = {c["name"]: q for c, q in geo.cube_points(m.spec())}
    ys = [pts[n][:, 1] for n in ("cranium", "face", "snout")]
    HEAD_Y[:] = [min(a.min() for a in ys), max(a.max() for a in ys)]
    hs = [pts[f"helmet{k}"] for k in range(len(HELMET))] + [pts["helmet_rim"]]
    HELMET_TOP[0] = (min(q[:, 1].min() for q in hs), max(q[:, 1].max() for q in hs))
    HELMET_Z[:] = [min(q[:, 2].min() for q in hs), max(q[:, 2].max() for q in hs)]
    cr = pts["cranium"]
    EYE[:] = [float(cr[:, 2].min()) + 3.0, float(cr[:, 1].max()) - 3.0]
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
