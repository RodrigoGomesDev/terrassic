"""Maiasaura peeblesorum v4, "a mãe empinada" (silhueta C da 1.11, escolhida pelo Rodrigo em 11/11/2026).

The v1 (10/11) was turned down: "os modelos tão muito padrão" - every duck-bill came out as the same horizontal body,
straight tail and thin legs, only the head changed. This one is built from the silhouette first
(tools/modelgen/handmade/_silhuetas/maiasaura.py, variant C), drawn at skin2.PX_PER_M (16.94 px per metre, one texel
= one Minecraft pixel at a model scale of ~1). Real size 9 m (Wosik et al. 2020).

THE SHAPE (what makes it read as itself before any colour):
- at rest it is HALF-REARED: the body tipped up 34 degrees on the hind legs, the deep tail running down to the ground
  behind (a tripod), the HUGE pale belly shown to the front, the thick arms hanging free in front of it and the short
  deep head held low on an S-neck, looking down at the nest; heavy, maternal, massive;
- when it walks it drops onto all four (maiaanims.posture): the body levels, the hands take the ground;
- the head: short and deep, the bill broad and DROOPING (wider than the face), its serrated rim, a solid HUMP of bone
  in front of the eyes (Horner & Makela 1979; drawn bigger than the bone), a THICK brow over the eye.

THE SKIN (drawn, not noise; study 15 colours "capim-seco"):
- a strong countershading laid on the unrolled body (cube space, so it follows the body when it rears or levels):
  a dark back, a straw flank, the enormous cream belly that the pose shows, ribbed with skin folds;
- a SADDLE OF CHEVRONS: dark V's pointing forward along the back from the shoulders to the middle of the tail, each with
  a pale trailing edge, running down the flanks as slanted bars (readable from far off);
- a dark facial MASK from the nostril through the eye to the back of the head, the lips and the throat pale;
- the male's hump ochre-rust with the worn crown pale; the female's the face's own colour; the calf paler and smooth,
  no hump, the chevrons only a shadow;
- under it all a discreet pebble scale one tone step deep.
"""
import math

import proto as P
import skin2
from proto import hx, h32

TEX_W = 256
PX_M = skin2.PX_PER_M
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# ------------------------------------------------------------------ palette ("capim-seco", study 15)
SCHEME = {
    "k0": "24231a", "k1": "34361f", "k2": "545a30", "k3": "7e8446", "k4": "9ca062", "k5": "b4b67c",
    "b0": "bfb894", "b1": "d0caa8", "b2": "e0dbc0", "b3": "ece8d4",
    "sc0": "aba57a", "sc1": "c0bb92", "sc2": "d2cda8",
    "oc0": "7a4420", "oc1": "a0602c", "oc2": "c08048",
    "bk0": "34302a", "bk1": "57513f", "bk2": "7a735a", "lip": "8a8460",
    "female": {"k2": "5a6038", "k3": "868a52", "k4": "a2a46c", "k5": "b8ba86",
               "oc0": "8c8656", "oc1": "a09a68", "oc2": "b3ad7e"},
}
PAL = {
    "iris": hx("b07a30"), "iris2": hx("7a4a1e"), "pupil": hx("100c08"), "glint": hx("f4ecd4"),
    "lid": hx("cfc8a4"), "lid2": hx("aaa27c"),
    "mouth": hx("3a2420"), "tongue": hx("8a5048"), "gum": hx("6a3a34"),
    "tooth": hx("e8e2c6"), "tooth2": hx("bdb390"),
    "hoof0": hx("2c2820"), "hoof1": hx("4a4436"), "hoof2": hx("6c6450"),
}
CALF = {"k0": "4c4832", "k1": "605c40", "k2": "8a855c", "k3": "a49e70", "k4": "b8b286", "k5": "c8c39a"}


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
# Model px at PX_M, the hip joint at z = 0. Every cube is laid out in its bone's UNROTATED frame: the body as if level
# (the bone itself carries the 34 degree rise), the neck, the legs and the tail straight from their joints. That frame
# is the "unrolled" animal the skin is drawn on.
# Signs (geo.rot_matrix): +x lifts what lies in front (-z) and lowers what lies behind (+z); a hanging limb with +x
# swings its far end forward.
RISE = 34.0
REST = {"body": RISE,
        "neck1": 8, "neck2": -40, "skull": -24,
        "thigh": -12, "shin": -42, "foot": 22, "toes": 12,
        "arm": -8, "forearm": 16, "hand": 18,
        "tail1": 6, "tail2": -28, "tail3": -10, "tail4": -4}
HIP_Y = 40
SADDLE_MATS = ("hide", "leather", "weave", "bag", "cord", "wood")


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes})
             if c["mat"] not in SADDLE_MATS + ("teeth",))
    m.shift(-lo)


def head(m, parent, y, z):
    """the short deep skull with the broad drooping bill, the thick brow, the jaw, the cheeks and the hump.
    (y, z): the occipital joint; 30 px from the occiput to the bill tip"""
    sk = m.bone("skull", parent, (0, y, z), (REST["skull"], 0, 0))

    def B(x0, y0, z0, x1, y1, z1):
        return (x0, y + y0, z + z0), (x1, y + y1, z + z1)
    m.cube(sk, *B(-7, -7, -10, 7, 6, 1), name="cranium")
    m.cube(sk, *B(-5, 6, -9, 5, 8, 0), name="crown")
    m.cube(sk, *B(-6, -8, -18, 6, 4, -9), name="face", faces=OUT("south"))
    m.cube(sk, *B(-5, -8, -23, 5, 1, -17), name="snout", faces=OUT("south"), rot=(-8, 0, 0), origin=(0, y + 1, z - 17))
    # THE BILL: broad, wider than the face, its tip drooping
    m.cube(sk, *B(-8, -9, -28, 8, -4, -21), name="bill", mat="beak", faces=OUT("south"))
    m.cube(sk, *B(-7, -11, -31, 7, -6, -26), name="bill_tip", mat="beak", faces=OUT("south"),
           rot=(14, 0, 0), origin=(0, y - 6, z - 26))
    # the THICK BROW over the eye: a shelf of bone and skin jutting out of each side of the skull
    m.pair(sk, sk, *B(7, 1, -9, 9, 4, -2), name="brow", faces=OUT("west"))
    # THE HUMP: the solid crest of the nasals and frontals in front of and over the eyes, three layers each starting
    # inside the one under it (a rounded hump, not a stair); the grown one's (adult_bump: the calf has a flat brow)
    ab = m.bone("adult_bump", sk, (0, y + 4, z - 9))
    for k, (w, y0, y1, z0, z1) in enumerate(((5.0, 3.0, 8.0, -19.0, -5.0), (4.0, 7.0, 11.0, -17.0, -7.0),
                                              (3.0, 10.0, 13.0, -15.0, -9.0))):
        m.cube(ab, *B(-w, y0, z0, w, y1, z1), name=("bump_base", "bump", "bump_top")[k], mat="bump",
               rot=(-10, 0, 0), origin=(0, y + 4, z - 9))
    # the cheeks over the dental batteries (they flex out as it chews)
    for side, sx in (("l", 1), ("r", -1)):
        m.bone(f"cheek_{side}", sk, (6 * sx, y - 2, z - 12))
    m.pair("cheek_l", "cheek_r", *B(6, -8, -19, 8, -3, -8), name="cheek", faces=OUT("west"))
    # the lower jaw: a deep dentary and the predentary under the bill
    jaw = m.bone("jaw", sk, (0, y - 6, z - 4))
    m.cube(jaw, *B(-5, -13, -20, 5, -7, -3), name="dentary")
    m.cube(jaw, *B(-6, -13, -29, 6, -9, -19), name="predentary", mat="beak", faces=OUT("south"))
    m.cube(jaw, *B(-4, -8.9, -27, 4, -7.9, -4), name="mouth", mat="mouth", faces=["up"])
    m.cube(jaw, *B(-4, -15, -16, 4, -12, -5), name="throat_fold")
    # the beak's serrated EDGE: a plane of pale denticles hung just outside the lower bill
    m.pair(sk, sk, *B(7.25, -11, -28, 7.25, -9, -20), name="denticles", mat="teeth")
    return sk


def neck(m, body):
    """short and very thick, in two pieces carried in an S: up off the chest, then bent down so the head hangs low over
    the nest; the dewlap of the throat pale under it"""
    n1 = m.bone("neck1", body, (0, 50, -52), (REST["neck1"], 0, 0))
    m.cube(n1, (-8, 40, -67), (8, 60, -48), name="neck1")
    m.cube(n1, (-6, 37, -64), (6, 41, -50), name="throat", mat="belly", faces=OUT("up"))
    n2 = m.bone("neck2", n1, (0, 50, -64), (REST["neck2"], 0, 0))
    m.cube(n2, (-7, 42, -77), (7, 59, -61), name="neck2")
    m.cube(n2, (-5, 39, -75), (5, 43, -63), name="throat2", mat="belly", faces=OUT("up"))
    hd = m.bone("head", n2, (0, 50, -76))
    head(m, hd, 51, -76)


def hind_legs(m, body):
    """the pillars of the tripod: a huge drumstick of a thigh, the knee forward, a short thick shin, a heavy
    metatarsus and three broad hoofed toes"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (13 * sx, HIP_Y, 0), (REST["thigh"], 0, 2 * sx))
        sh = m.bone(f"shin_{side}", th, (13 * sx, 21, 0), (REST["shin"], 0, -2 * sx))
        ft = m.bone(f"foot_{side}", sh, (13 * sx, 5, 0), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (13 * sx, -2, -1), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (5, 18, -10), (21, 46, 11), name="thigh")
    m.pair("thigh_l", "thigh_r", (7, 15, -8), (19, 19, 7), name="knee")
    m.pair("shin_l", "shin_r", (8, 3, -5), (18, 19, 5), name="shin")
    m.pair("foot_l", "foot_r", (8.5, -3, -4), (17.5, 6, 4), name="meta")
    m.pair("toes_l", "toes_r", (7.5, -4, -8), (18.5, -1, 1), name="pes")
    m.pair("toes_l", "toes_r", (11.5, -4.5, -11), (14.5, -1.5, -8), name="nail_mid", mat="hoof", faces=OUT("south"))
    m.pair("toes_l", "toes_r", (15, -4.5, -10), (18, -1.5, -7), name="nail_out", mat="hoof", faces=OUT("south"),
           rot=(0, -14, 0), origin=(16.5, -3, -7.5))
    m.pair("toes_l", "toes_r", (8, -4.5, -10), (11, -1.5, -7), name="nail_in", mat="hoof", faces=OUT("south"),
           rot=(0, 14, 0), origin=(9.5, -3, -7.5))


def fore_legs(m, body):
    """thick arms hanging free in front of the belly at rest, the weight-bearers when it drops onto all four: the upper
    arm, a deep forearm and the hoof-like mitten of the bound fingers"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (13 * sx, 37, -53), (REST["arm"], 0, 5 * sx))
        fa = m.bone(f"forearm_{side}", a, (13 * sx, 20, -53), (REST["forearm"], 0, -6 * sx))
        m.bone(f"hand_{side}", fa, (13 * sx, 5, -53), (REST["hand"], 0, 2 * sx))
    m.pair("arm_l", "arm_r", (8, 18, -59), (19, 41, -46), name="arm")
    m.pair("forearm_l", "forearm_r", (8.5, 4, -58), (17.5, 21, -48), name="forearm")
    m.pair("hand_l", "hand_r", (9, -1, -57.5), (17, 6, -48.5), name="hand")
    m.pair("hand_l", "hand_r", (8.5, -3, -58), (17.5, -1, -48), name="mitten")
    m.pair("hand_l", "hand_r", (9.5, -3.5, -60), (16.5, -1.5, -57), name="hand_nail", mat="hoof", faces=OUT("south"))


TAILS = ("tail1", "tail2", "tail3", "tail4")


def tail(m, body):
    """the third leg of the tripod: very deep and broad at the root, running down behind to the ground and then out
    level, stiff with ossified tendons, in four overlapping pieces"""
    segs = [  # name, pivot z, z0, z1, half width, y0, y1
        ("tail1", 12, 8, 38, 12, 31, 55), ("tail2", 36, 33, 57, 9, 35, 51), ("tail3", 56, 53, 75, 6.5, 38, 48),
        ("tail4", 74, 71, 90, 4, 40, 46)]
    parent = body
    for n, pz, z0, z1, hw, y0, y1 in segs:
        b = m.bone(n, parent, (0, 43, pz), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-9, 28, 10), (9, 32, 30), name="tail_muscle", mat="belly", faces=OUT("up"))
    m.cube("tail1", (-8, 54, 6), (8, 57, 32), name="tail_ridge", faces=OUT("down"))


def build(saddle_on=True):
    m = P.Model("maiasaura")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, HIP_Y, 0), (REST["body"], 0, 0))
    # the trunk (laid out level; the bone rears it): a deep barrel, the hips over the legs, the chest in front, a
    # rounded back, and the ENORMOUS belly hanging under all of it, its lowest fold narrower (the barrel rounds off)
    m.cube(body, (-18, 27, -46), (18, 60, 2), name="trunk")
    m.cube(body, (-14, 59, -42), (14, 63, 4), name="back")
    m.cube(body, (-17, 29, -10), (17, 61, 15), name="hips")
    m.cube(body, (-13, 60, -6), (13, 64, 13), name="sacrum")
    m.cube(body, (-15, 28, -58), (15, 55, -44), name="chest")
    m.cube(body, (-17, 14, -46), (17, 30, -8), name="belly", mat="belly", faces=OUT("up"))
    m.cube(body, (-13, 10, -42), (13, 15, -13), name="belly_low", mat="belly", faces=OUT("up"))
    neck(m, body)
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the saddle: the "Sela de Ninhal"
SADDLE_PAL = {   # its own: a broad woven reed mat, cured hide, two saddlebags of plaited bark fibre, a wooden frame
    "W0": hx("6a5a34"), "W1": hx("8a7848"), "W2": hx("a8945c"), "W3": hx("4c5a30"),
    "H0": hx("3a2a1e"), "H1": hx("5a4230"), "H2": hx("7a5a40"), "H3": hx("947252"),
    "L0": hx("2a1e16"), "L1": hx("44301f"),
    "G0": hx("5e4a30"), "G1": hx("7c6440"), "G2": hx("98804e"),
    "C0": hx("6a5a3e"), "C1": hx("8c7a54"), "D0": hx("4a3826"), "D1": hx("6c5436"),
}


def saddle(m, body):
    """The nesting-ground saddle: a broad mat of woven reeds over the back behind the shoulders, a low hide seat on a
    wooden frame, a pair of deep saddlebags of plaited bark fibre at the flanks, a cord girth round the belly."""
    sd = m.bone("saddle", body, (0, 63, -22))
    m.cube(sd, (-15, 63, -38), (15, 64, -12), name="mat", mat="weave", faces=OUT("down"))
    m.pair(sd, sd, (15, 48, -37), (16, 63, -13), name="mat_side", mat="weave", faces=OUT("west"))
    m.cube(sd, (-7, 64, -33), (7, 65, -16), name="seat", mat="hide", faces=OUT("down"))
    m.cube(sd, (-6, 65, -18), (6, 68, -16), name="cantle", mat="wood")
    m.cube(sd, (-2, 65, -33), (2, 67, -31), name="pommel", mat="wood")
    m.pair(sd, sd, (16, 38, -32), (20, 49, -19), name="bag", mat="bag")
    m.pair(sd, sd, (16.5, 49, -29), (17.5, 56, -28), name="bag_cord", mat="cord", faces=OUT("west"))
    m.pair(sd, sd, (18.5, 9, -27), (19.5, 48, -24), name="girth_side", mat="cord", faces=OUT("west"))
    m.cube(sd, (-19.5, 8, -27), (19.5, 9, -24), name="girth_under", mat="cord", faces=OUT("up"))


def saddle_px(t):
    c = t.cube; mat = c["mat"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "weave":
        if f == "up" and j % 4 == 2:
            return p["W3"]
        if j == h - 1 and f != "up":
            return p["W0"]
        return p["W2"] if (i + 2 * j) % 3 == 0 else p["W1"]
    if mat == "bag":
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


# ------------------------------------------------------------------ the skin, drawn on the unrolled body
TRUNK = {"trunk", "back", "hips", "sacrum", "chest", "neck1", "neck2", "tail1", "tail2", "tail3", "tail4", "tail_ridge"}
UNDER = {"belly", "belly_low", "throat", "throat2", "tail_muscle"}
LEG = {"shin", "meta", "pes", "forearm", "hand", "mitten"}
LIMB = {"thigh", "knee", "arm"}
HEAD = {"cranium", "crown", "face", "snout", "cheek", "dentary", "brow", "throat_fold"}


class Unrolled:
    """top and bottom of the unrolled body (cube space, the bones' rotations left out) along its length: the spine
    line and the belly line the countershading and the chevrons are drawn from"""

    def __init__(self, m):
        tops, bots, half = {}, {}, {}
        for c in m.cubes:
            if c["name"] not in TRUNK | UNDER:
                continue
            z0, z1 = int(math.floor(c["from"][2])), int(math.ceil(c["to"][2]))
            for z in range(z0, z1 + 1):
                tops[z] = max(tops.get(z, -1e9), c["to"][1])
                bots[z] = min(bots.get(z, 1e9), c["from"][1])
                half[z] = max(half.get(z, 0), c["to"][0])
        self.z0 = min(tops)
        n = max(tops) - self.z0 + 1
        import numpy as np
        k = np.ones(5) / 5
        def run(d, dflt):
            a = np.array([d.get(self.z0 + i, dflt) for i in range(n)], float)
            return np.convolve(np.pad(a, 2, mode="edge"), k, "valid")
        self.top, self.bot, self.half = run(tops, 50), run(bots, 30), run(half, 8)

    def at(self, z):
        i = int(min(max(round(z) - self.z0, 0), len(self.top) - 1))
        return self.bot[i], self.top[i], self.half[i]


def around(t, U):
    """(h, a): h = 0 on the belly line .. 1 on the spine; a = how far round from the spine, in px over the skin (the
    top face across, then down the side)"""
    z, y, x = t.L[2], t.L[1], t.L[0]
    bot, top, half = U.at(z)
    h = min(1.0, max(0.0, (y - bot) / max(1.0, top - bot)))
    if t.face == "up":
        return h, abs(x)
    if t.face == "down":
        return 0.0, half + (top - bot)
    if t.face in ("north", "south"):
        return h, abs(x) if y > top - 3 else half + (top - y)
    return h, half * 0.8 + (top - y)


# THE CHEVRONS: their positions along the unrolled body (z of the point of each V on the spine), from the shoulders
# to the middle of the tail, closer together on the tail; each V's arms sweep back 0.55 px per px round the body
CHEVRONS = (-56, -42, -28, -14, 0, 14, 28, 41, 53, 64)
SWEEP = 0.9


def chevron(t, U, calf=False):
    """'dark' inside a chevron, 'edge' on its pale trailing edge, None outside"""
    z = t.L[2]
    h, a = around(t, U)
    bot, top, half = U.at(z)
    reach = half * 0.8 + 0.42 * (top - bot)          # the arms end about the middle of the flank
    if a > reach:
        return None
    w = 3.6 if z < 36 else 2.6
    for k, zc in enumerate(CHEVRONS):
        d = z - (zc + SWEEP * a)
        # the tips of the arms thin out: drawn, not cut
        ww = w * (1.0 - 0.5 * max(0.0, (a - 0.6 * reach) / (0.4 * reach)))
        if 0 <= d < ww:
            return "dark"
        if ww <= d < ww + 1.5 and not calf:
            return "edge"
    return None


def body_tone(t, U, calf=False):
    """the palette key of a body texel: the countershading, the chevron saddle, the belly folds, the pebble scale"""
    n = t.cube["name"]; f = t.face
    h, a = around(t, U)
    if f == "down" or n in UNDER:
        # the belly: cream, ribbed with skin folds across it every 4 px, a darker fold at its edge
        if f == "down" or (f in ("east", "west") and t.rel[1] < 0.8) or f in ("north", "south"):
            k = int(math.floor(t.L[2])) % 4
            return "b0" if k == 0 else "b2" if k == 2 else "b1"
        return "b0"
    # the countershading: the border between flank and belly is a scalloped line, drawn (one bulge per 9 px)
    sc = 0.04 * math.cos(2 * math.pi * t.L[2] / 9.0)
    if h < 0.22 + sc:
        base = "b1"
    elif h < 0.30 + sc:
        base = "k4"
    elif h < 0.58:
        base = "k3"
    elif h < 0.86:
        base = "k2"
    else:
        base = "k1"
    ch = chevron(t, U, calf)
    if calf:
        if ch == "dark":
            return skin2.step(base, -1) if base not in ("b1",) else base
        return base
    if ch == "dark":
        return "k0" if base in ("k1", "k2") else skin2.step(base, -2)
    if ch == "edge":
        return {"k1": "k3", "k2": "k4", "k3": "k4", "k4": "k5"}.get(base, base)
    # the discreet pebble scale under the pattern (one tone step on the shaded seam)
    if base != "b1" and skin2.scales(t, cell=4.0, seed=23, flat=0.45) == "edge":
        return skin2.step(base, -1)
    return base


def limb_tone(t, calf=False):
    """legs: the outer thigh and upper arm carry the flank's colour with a dark bar (the chevron's echo) across the
    thigh; shins and forearms a step darker, scutes across the front of the feet"""
    n = t.cube["name"]; f = t.face
    if n in ("thigh", "knee", "arm"):
        base = "k3"
        if f in ("south", "down"):
            base = "k2"
        elif f == "up":
            base = "k2"
        if n == "thigh" and f in ("east", "west") and not calf:
            # two dark bars down the outer thigh, slanting forward like the chevrons on the hips
            v = t.rel[1]
            zz = t.rel[2] * 21 - v * 6
            if 4 <= zz < 6.5 or 11 <= zz < 13.5:
                return "k1"
        return base
    base = "k2" if f in ("south", "down", "west") else "k3"
    if n in ("meta", "pes", "mitten", "hand") and f in ("north", "up"):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 2
        if k == 0 and (t.i % 3) != 1:
            return skin2.step(base, -1)
    if n in ("meta", "pes", "hand", "mitten") and skin2.scales(t, cell=3.0, seed=17, flat=0.5) == "edge":
        return skin2.step(base, -1)
    if n in ("shin", "forearm") and f in ("east", "west") and t.rel[2] > 0.7:
        return skin2.step(base, -1)              # the back of the shin and the forearm a step darker
    return base


# ------------------------------------------------------------------ the head
# THE MOTIF: a dark MASK from the nostril back through the eye to the end of the skull (k1, its lower edge a crisp
# line), the roof and the hump above it lighter, the lips, the cheeks' lower half and the throat pale; small pebble
# scales on the face, big flat plates on the hump.
HL = ["k0", "k1", "k2", "k3", "k4", "k5", "sc0", "sc1", "sc2"]


def hstep(key, d):
    return HL[max(0, min(len(HL) - 1, HL.index(key) + d))] if key in HL else skin2.step(key, d)


def pebble(t, cell=2.0, seed=0):
    k = skin2.scales(t, cell=cell, seed=seed, flat=0.8)
    if k == "edge":
        return -1
    u, v = skin2.surface_uv(t)
    if h32(math.floor(u / cell), math.floor(v / cell), seed, 9) % 3 == 0 and (math.floor(u) + math.floor(v)) % 2:
        return 1
    return 0


def mask_band(t):
    """the mask, in skull space: a band about 5 px deep through the eye, rising a little toward the nostril"""
    z = t.L[2] - HEAD_O[1]; y = t.L[1] - HEAD_O[0]       # z from the occiput (negative forward), y from the joint
    centre = -1.0 + 0.12 * (-z)                          # rises toward the snout
    if z < -24:
        return 0
    if abs(y - centre) <= 2.5:
        return 2
    if abs(y - centre) <= 3.5:
        return 1
    return 0


def head_tone(t, sex):
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "b1"
    if n == "throat_fold":
        return "b1" if (t.i + t.j) % 5 else "b0"
    if n == "dentary":
        if f == "up":
            return "k3"
        if t.j == 0:
            return "lip"
        base = "b1" if t.rel[1] < 0.5 else "b0"
        return skin2.step(base, min(0, pebble(t, 1.8, 33)))
    if n == "cheek":
        if t.j == t.h - 1:
            return "k1"
        if t.j == t.h - 2:
            return "lip"
        base = "k3" if mask_band(t) else "k5"
        return hstep(base, pebble(t, 1.9, 34))
    if n == "brow":
        if f == "down":
            return "k0"
        return hstep("k2" if f in ("east", "west") else "k4", pebble(t, 1.6, 36))
    if f == "up":
        return hstep("k5", pebble(t, 2.2, 21))
    if f in ("east", "west", "north"):
        mb = mask_band(t)
        if n in ("face", "snout") and t.j == t.h - 1:
            return "k0"                                   # the mouth line along the face
        if mb == 2:
            return hstep("k1", pebble(t, 2.0, 9))
        if mb == 1:
            return "k2"
        if t.L[1] - HEAD_O[0] < -1.0 + 0.12 * -(t.L[2] - HEAD_O[1]) - 3:
            return hstep("k5", pebble(t, 2.2, 32))         # below the mask: pale
        return hstep("k4", pebble(t, 2.0, 31))             # above: the light roof colour
    return hstep("k4", pebble(t, 2.0, 32))


def bump_px(t, p, sex):
    n = t.cube["name"]; f = t.face
    k = ("bump_base", "bump", "bump_top").index(n)
    plate = skin2.scales(t, cell=3.4, seed=70 + k, flat=0.9)
    if k == 0:
        key = "sc0" if f == "up" else "k5"
        if sex == "male" and f != "up" and t.j <= 1:
            key = "oc1"
        if plate == "edge":
            key = hstep(key, -2) if key != "oc1" else "oc0"
        return p[key]
    if sex == "male":
        ramp = ("oc0", "oc1", "oc2")
        if f == "up":
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
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2] - t.cube["from"][2])); row = t.j
    LEN = (1, 2, 0, 1, 2, 1, 0, 2)
    if col >= len(LEN) or row >= LEN[col]:
        return None
    return p["tooth2"] if row == 1 else p["tooth"]


def beak_px(t, p):
    n = t.cube["name"]; f = t.face
    if f == "up":
        return p["bk2"] if (t.i * 2 + t.j) % 5 else p["bk1"]
    if f == "down":
        return p["bk0"]
    if n in ("bill", "bill_tip") and t.j == t.h - 1:
        return p["tooth2"]
    if n == "predentary" and t.j == 0:
        return p["bk2"]
    return p["bk1"] if t.j > 0 else p["bk2"]


def shader_for(sex, U):
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
            return p[body_tone(t, U, calf)]
        if n in LEG or n in LIMB:
            return p[limb_tone(t, calf)]
        if n in HEAD:
            return p[head_tone(t, sex)]
        return p["k3"]
    return sh


HEAD_O = [0.0, 0.0]      # the skull joint (y, z) in cube space

# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP
# THE EYE: under the thick brow (the brow's shadow is its upper lid), sunk in the mask; a warm amber iris round a round
# pupil, the glint high at the back, a thick pale lower lid of two rows
EYE_ART = [
    "kkkkk.",
    "kiipgk",
    "kIppik",
    ".kIIk.",
    ".LLLL.",
    "..ll..",
]
NOSTRIL = [
    "hhhhh.",
    "nnnnhh",
    ".nnn..",
]


def decals_for(sex):
    p = pal_for(sex)
    cm = {"d": p["k1"], "k": p["k0"], "g": p["glint"], "i": p["iris"], "I": p["iris2"], "p": p["pupil"],
          "L": p["lid"], "l": p["lid2"], "n": p["k0"], "h": p["k1"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", EYE_ART, cm, at=(1, 6))
        P.stamp(img, m, C["snout"], "east", NOSTRIL, cm, at=(0, 2))
    return dec


def paint_sex(m, sex="male"):
    U = Unrolled(m)
    sk = next(b for b in m.bones if b["name"] == "skull")
    HEAD_O[:] = [sk["origin"][1], sk["origin"][2]]
    return P.paint(m, shader_for(sex, U), decals=(decals_for(sex),))
