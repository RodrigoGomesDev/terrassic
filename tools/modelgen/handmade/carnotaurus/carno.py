"""Carnotaurus sastrei, made by hand from its own study (page "Carnotaurus: estudo e modelo, passo a passo", study
approved by Rodrigo on 01/11/2026). Real size, 7.8 m.

Drawn at 24 px = 1 m (game scale 0.667), finer than the T. rex's 16 px/m, the way the Velociraptor is drawn finer:
the real Carnotaurus head is small (0.6 m skull), and at 16 px/m it only had 14 px to carry the horns, the forward eye,
the lips and the rugose skin (Rodrigo 01/11 13:59Z: "meio sem detalhes"). Inflating the head like the T. rex's would
lose the trait the study is about (a small head on a long-legged body), so the pixels get finer instead.

The head (each point from the study):
- short and deep: 21 px from the back of the skull to the blunt snout, 13 px tall over the mouth line;
- the lower jaw is long and shallow (3 px in front): quick, weak bites; a loose throat skin under it;
- two thick horns right over the eyes, pointing out and a little up, flat and worn on top, on a rugose base;
- the eyes face forward: each sits on the corner where the wide cranium meets the narrower snout, so it shows from
  the side AND from the front; the orbit is keyhole-shaped (a narrow slot under the eye);
- the big jaw muscle bulges behind the eye, under the horn;
- lips: the teeth stay hidden with the mouth shut; a row of small pits (nerve foramina) runs above the lips;
- no fossil skin of the head is known: rugose skin on the nasal ridge and the horn bases (as in cattle and rhinos),
  a few large feature scales on the cheek like the ones of the body, a dark face mask on males.

Every face of the head is drawn by hand below (FACE_ART), no noise: the shader only fills the hidden faces.
"""
import math

import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 24

# ------------------------------------------------------------------ palette
# The body ramp k0..k5 and the belly b0..b3 come from one of three schemes (Rodrigo picks; "ferrugem" is the
# proposal). Each ramp is hue-shifted: the shadows lean to red-violet, the lights to yellow.
SCHEMES = {
    "ferrugem": {   # rust red with dark saddles, cream belly: the dry coast of Patagonia, and no other dino has it
        "k0": "221414", "k1": "3a1e1a", "k2": "582b20", "k3": "7b3d26", "k4": "9e562e", "k5": "bd773f",
        "b0": "866849", "b1": "b0906a", "b2": "cfb68a", "b3": "e5d3aa", "m0": "2e1916", "m1": "45231c",
        "hr0": "4a1418", "hr1": "6e1f22", "hr2": "93302d", "lip": "c49f78",
        "female": {"k1": "43261f", "k2": "653727", "k3": "874c30", "k4": "a8683b", "k5": "c4874c"},
    },
    "ocre": {       # ochre with charcoal saddles
        "k0": "1e1a16", "k1": "322a21", "k2": "4d402d", "k3": "715e3c", "k4": "98814f", "k5": "baa266",
        "b0": "8c7a56", "b1": "b6a47a", "b2": "d4c59c", "b3": "e9deb8", "m0": "26201a", "m1": "382f24",
        "hr0": "6c2a1a", "hr1": "8f3c22", "hr2": "b2552f", "lip": "cbb48a",
        "female": {"k1": "3b3127", "k2": "574935", "k3": "7b6844", "k4": "a28b57", "k5": "c2aa6d"},
    },
    "cinza": {      # ash grey, dark face, red horn bases on the male
        "k0": "1a1a1c", "k1": "29282b", "k2": "3e3b3c", "k3": "57524e", "k4": "766d62", "k5": "958a7a",
        "b0": "7b725e", "b1": "a3997f", "b2": "c3b99f", "b3": "dbd2ba", "m0": "222124", "m1": "333134",
        "hr0": "5c1b1b", "hr1": "7f2b23", "hr2": "a33a2c", "lip": "b9ae95",
        "female": {"k1": "302e2e", "k2": "464240", "k3": "5f5953", "k4": "7d7467", "k5": "9b917f"},
    },
}
SCHEME = ["ferrugem"]

PAL = {
    "k0": hx("2c1e1c"), "k1": hx("45302a"), "k2": hx("5d432f"), "k3": hx("7c5c3a"), "k4": hx("9c7a47"),
    "k5": hx("b99b5c"), "b0": hx("a88f68"), "b1": hx("cdb88f"), "b2": hx("e0d0aa"), "b3": hx("ece0c0"),
    "m0": hx("2a201a"), "m1": hx("3d2e23"),
    "hr0": hx("6c2a1a"), "hr1": hx("8f3c22"), "hr2": hx("b2552f"),
    "hb0": hx("8a7556"), "hb1": hx("ab9672"), "hb2": hx("c9b791"),
    "ker0": hx("231a15"), "ker1": hx("3a2d24"), "ker2": hx("d2c3a2"), "ker3": hx("a8987a"),
    "n0": hx("6f5236"), "n1": hx("c2a676"),
    "iris": hx("e3a531"), "iris2": hx("ad6c1c"), "eye_hi": hx("f7d76c"), "pupil": hx("120d0a"), "lid": hx("1c1511"), "glint": hx("f4ecc4"),
    "gum": hx("7c3330"), "mouth": hx("3b1719"), "tongue": hx("a8524a"), "tooth": hx("ece3c9"), "tooth2": hx("c4b590"),
    "lip": hx("cbb48a"),
}


def pal_for(sex, scheme=None):
    """the palette of one sex in the chosen scheme; the female is a tone lighter, without the mask"""
    sc = SCHEMES[scheme or SCHEME[0]]
    p = dict(PAL)
    for k, v in sc.items():
        if k != "female": p[k] = hx(v)
    p["n0"], p["n1"] = p["k3"], p["k5"]
    p["hb0"], p["hb1"], p["hb2"] = p["k3"], p["k4"], p["k5"]
    if sex != "male":
        for k, v in sc["female"].items(): p[k] = hx(v)
    return p


def charmap(sex):
    male = sex == "male"
    p = pal_for(sex)
    c = {"0": p["k0"], "1": p["k1"], "2": p["k2"], "3": p["k3"], "4": p["k4"], "5": p["k5"],
         "a": p["b0"], "b": p["b1"], "c": p["b2"], "L": p["lip"], "x": p["k4"], "f": p["k1"], "n": p["k0"],
         "p": p["pupil"], "i": p["iris"], "I": p["iris2"], "Y": p["eye_hi"], "g": p["glint"], "l": p["lid"],
         "h": p["ker0"], "H": p["ker1"], "w": p["ker2"], "W": p["ker3"], "N": p["n1"], "o": p["n0"],
         "q": p["hr0"] if male else p["hb0"], "r": p["hr1"] if male else p["hb1"], "R": p["hr2"] if male else p["hb2"]}
    # the male's face mask; on the female the same pixels take the plain head tones
    c["m"] = p["m0"] if male else p["k2"]
    c["M"] = p["m1"] if male else p["k3"]
    return c


# ------------------------------------------------------------------ geometry
def _ground(m):
    """shift the model so its lowest point at rest touches y = 0"""
    import geo
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes}))
    m.shift(-lo)


def head(m, parent, hy, hz, rest=(-6, 0, 0)):
    """the skull, its horns and the jaw. (hy, hz): back of the skull at the mouth line; returns the skull bone"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    sk = m.bone("skull", parent, (0, hy + 5, hz), rest)
    m.cube(sk, *B(-5, 0, -9, 5, 13, 0), name="cranium")
    m.cube(sk, *B(-4, 3, 0, 4, 12, 2), name="occiput")
    m.pair(sk, sk, *B(4, 2, -6, 6, 8, -1), name="temporal")          # the jaw muscle behind the eye
    m.cube(sk, *B(-3.5, 0, -19, 3.5, 10, -9), name="snout")
    m.cube(sk, *B(-3, 0, -21, 3, 9, -19), name="premax")               # the blunt, rounded tip
    m.cube(sk, *B(-2, 10, -18, 2, 12, -9), name="nasal")               # rugose ridge down the snout
    m.pair(sk, sk, *B(4, 10, -11, 7, 13, -7), name="horn_base", mat="horn_base")
    rot, o = (0, 0, 22), (6.5, hy + 12.5, hz - 9)
    m.pair(sk, sk, *B(6, 11, -10.5, 10, 14, -7.5), name="horn", mat="horn", rot=rot, origin=o)
    m.pair(sk, sk, *B(10, 11.5, -10, 12, 13.5, -8), name="horn_tip", mat="horn", rot=rot, origin=o)
    jaw = m.bone("jaw", sk, (0, hy + 1, hz - 2))
    m.cube(jaw, *B(-4.5, -4, -7, 4.5, 0, 0), name="jaw_back")
    m.cube(jaw, *B(-2.5, -3, -20, 2.5, 0, -6), name="jaw_front")
    m.cube(jaw, *B(-3.5, -5, -11, 3.5, -3, -4), name="gular", mat="gular")   # loose throat skin
    m.cube(jaw, *B(-4, -1, -6, 4, 2, -1), name="cheek", mat="mouth")        # the mouth's inner wall: rides up into the
                                                                              # skull, so a half-open jaw shows no slit
    m.cube(jaw, *B(-1.5, -2, -17, 1.5, 1, -5), name="tongue", mat="tongue")  # in front the slit closes from both sides:
    m.cube(sk, *B(-1, -1, -18, 1, 2, -10), name="palate", mat="mouth")    # the tongue and the palate ridge, 1 px each
    # teeth, as on the other theropods of the mod: alpha planes just outside the jaw. The upper row hangs over the lower
    # jaw with the mouth shut (long, slender, slightly hooked, of uneven length); the lower row, smaller, stands inside
    # the snout and only shows with the mouth open
    m.pair(sk, sk, *B(3.25, -3, -19, 3.25, 1, -7), name="teeth_up", mat="teeth")
    m.pair(jaw, jaw, *B(2.25, -1, -19, 2.25, 2, -7), name="teeth_lo", mat="teeth_lo")
    return sk


REST = {   # bone rest angles (x: positive = the far end up for necks/tail, knee forward for the thigh)
    "neck1": 16, "neck2": 4, "skull": -18, "thigh": 22, "shin": -52, "foot": 44, "toes": -14,
    "arm": 30, "forearm": -60, "tail1": -4, "tail2": 2, "tail3": 1, "tail4": 0, "tail5": 0,
}


def legs(m, body):
    """long running legs drawn with weight (Rodrigo 01/11 15:53Z: the thin ones looked like stilts): a heavy thigh
    set into the hip (the tail muscle pulls the femur), a deep calf over the shin, a long metatarsus and a big foot
    of three toes plus the small first toe; a clear Z from the side, feet under the body seen from the front"""
    for side, sx in (("l", 1), ("r", -1)):
        # knees out, feet in under the body (seen from the front the thigh bulges past the flank, the shin comes back)
        th = m.bone(f"thigh_{side}", body, (9 * sx, 57, 0), (REST["thigh"], 0, 6 * sx))
        sh = m.bone(f"shin_{side}", th, (9 * sx, 32, 0), (REST["shin"], 0, -11 * sx))
        ft = m.bone(f"foot_{side}", sh, (9 * sx, 10, 0), (REST["foot"], 0, 5 * sx))
        m.bone(f"toes_{side}", ft, (9 * sx, 0, 0), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (4, 36, -10), (15, 66, 10), name="thigh")          # the drumstick, into the hip
    m.pair("thigh_l", "thigh_r", (5, 29, -7), (14, 38, 4), name="knee")             # and down to the knee
    m.pair("shin_l", "shin_r", (5, 20, -5.5), (13, 33, 4.5), name="calf")
    m.pair("shin_l", "shin_r", (6, 8, -3.5), (12, 21, 2.5), name="shin")
    m.pair("foot_l", "foot_r", (6, -1, -3), (12, 11, 3), name="meta")
    m.pair("toes_l", "toes_r", (7.5, -2, -13), (10.5, 1, 0), name="toe_mid")
    m.pair("toes_l", "toes_r", (10.5, -2, -10), (13.5, 1, -1), name="toe_out")
    m.pair("toes_l", "toes_r", (4.5, -2, -10), (7.5, 1, -1), name="toe_in")
    m.pair("toes_l", "toes_r", (8.5, -2, -15), (9.5, 0, -13), name="claw_mid", mat="claw")
    m.pair("toes_l", "toes_r", (11.5, -2, -12), (12.5, 0, -10), name="claw_out", mat="claw")
    m.pair("toes_l", "toes_r", (5.5, -2, -12), (6.5, 0, -10), name="claw_in", mat="claw")
    m.pair("foot_l", "foot_r", (5.5, 1, 1.5), (7.5, 3, 4.5), name="hallux")


def arms(m, body):
    """the arms: an upper arm of 7 px (0.3 m) and almost nothing below it, a forearm a quarter of that and a
    mitten of four stubby fingers; they hang close to the chest"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (7 * sx, 52, -44), (REST["arm"], 0, 0))
        m.bone(f"forearm_{side}", a, (7.5 * sx, 45, -44), (REST["forearm"], 0, 0))
    m.pair("arm_l", "arm_r", (6, 45, -45), (9, 53, -42), name="arm")
    m.pair("forearm_l", "forearm_r", (6.5, 42, -45), (8.5, 46, -43), name="forearm")
    m.pair("forearm_l", "forearm_r", (6, 40, -45.5), (9, 42, -42.5), name="hand")


def tail(m, body):
    """the tail: very deep and WIDE at the base (the caudal ribs stick out sideways like wings and carry the big
    running muscle), the back half slim and stiff"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 8, 30, 8, 49, 71), ("tail2", 28, 50, 7, 52, 68), ("tail3", 48, 68, 5, 54, 65),
        ("tail4", 66, 84, 3, 56, 62), ("tail5", 82, 98, 1.5, 57, 61)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-6, 44, 6), (6, 49, 26), name="tail_muscle")            # the caudofemoralis under the base
    m.pair("tail1", "tail1", (8, 58, 10), (10, 61, 30), name="rib1")          # caudal ribs: the 'wings'
    m.pair("tail2", "tail2", (7, 59, 30), (9, 61, 48), name="rib2")


SADDLE_PAL = {   # brown leather and grey iron like the vanilla saddle item (Carnotaurus takes the plain saddle)
    "L0": hx("3b2414"), "L1": hx("5a3720"), "L2": hx("7a4b2a"), "L3": hx("9a6236"), "L4": hx("b57d48"),
    "st": hx("c79e66"), "F0": hx("9a8259"), "F1": hx("c2a97f"), "F2": hx("ddc9a0"),
    "I0": hx("4d4d4b"), "I1": hx("7d7d79"), "I2": hx("a9a9a2"),
}


def saddle(m, body):
    """A light racing saddle, its own and not the T. rex one: the Carnotaurus is the sprinter mount. A low seat with
    a pommel to hold and a cantle behind, on a sheepskin that shows round the edges, short leather flaps (longer in
    front, where the rider's calf lies), jockey-short stirrups and one girth that follows the belly down. No breast
    collar, no bags, no studs: nothing that does not hold the rider on. Faces that lie on the body are left out
    (GeckoLib draws without back-face culling; the model "east" face of a +x cube is the inner one in game)."""
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    sd = m.bone("saddle", body, (0, 76, -15))
    m.cube(sd, (-9.5, 70, -26), (9.5, 72, -4), name="pad", mat="fur", faces=out("down"))
    m.pair(sd, sd, (8, 62, -24), (9, 70, -15), name="flap_f", mat="hide", faces=out("east", "up"))
    m.pair(sd, sd, (8, 65, -15), (9, 70, -6), name="flap_b", mat="hide", faces=out("east", "up", "north"))
    m.cube(sd, (-5.5, 72, -21), (5.5, 74, -8), name="seat", mat="hide", faces=out("down"))
    m.cube(sd, (-3.5, 74, -21), (3.5, 76, -18), name="pommel", mat="hide")
    m.cube(sd, (-5, 74, -10), (5, 76, -7), name="cantle", mat="hide")
    m.cube(sd, (-4, 76, -9), (4, 77, -7), name="cantle_lip", mat="hide")
    # jockey-short stirrups: the leather runs over the flap from under the sheepskin, the iron hangs just below it
    m.pair(sd, sd, (9, 58, -20), (10, 70, -19), name="leather", mat="strap", faces=out("east", "up"))
    m.pair(sd, sd, (9, 55, -21), (12, 58, -20), name="iron_f", mat="iron")
    m.pair(sd, sd, (9, 55, -19), (12, 58, -18), name="iron_b", mat="iron")
    m.pair(sd, sd, (9, 54, -21), (12, 55, -18), name="iron_t", mat="iron")
    # the girth: down the flank under the flap, in onto the belly and across under it
    m.pair(sd, sd, (8, 46, -16), (9, 62, -14), name="girth", mat="strap", faces=out("east", "up"))
    m.pair(sd, sd, (6, 45, -16), (9, 46, -14), name="girth_step", mat="strap", faces=out("up"))
    m.pair(sd, sd, (6, 41, -16), (7, 45, -14), name="girth_low", mat="strap", faces=out("east"))
    m.cube(sd, (-6, 41, -16), (6, 42, -14), name="girth_under", mat="strap", faces=out("up"))


# The flaps, drawn by hand, column 0 at the FRONT, row 0 at the top. a = L1, b = L2, c = L3 (rubbed by the calf),
# d = L0. Dark top row: the shadow of the sheepskin. The wear sits where the rider's leg presses, not in the middle.
SADDLE_ART = {
    "flap_f": [
        "aaaaaaaaa",
        "bbbbbbbbb",
        "bbbbbbbbb",
        "bbbbbbbbb",
        "bbbbbbbbb",
        "bbbbbbbab",
        "bbbbbbbbb",
        "abbbbbbbb",
        "aadaaaaaa",
    ],
    "flap_b": [
        "aaaaaaaaa",
        "bbbbbbbbb",
        "bbbbbbbbb",
        "bbbbbbbbb",
        "abbbbbbbb",
        "aaaaaaada",
    ],
}
SEAT_TOP = [        # 11 x 13, row 0 at the back (under the cantle). Plain: any wear mark here read as a face
    "aaaaaaaaaaa",
    "bbbbbbbbbbb",
    "bbbbbbbbbbb",
    "bbbbbbbbbbb",
    "bbbbbbbbbbb",
    "bbbbbbbbbbb",
    "bbbbbbbbbbb",
    "bbbbbbbbbbb",
    "bbbbbbbbbbb",
    "bbbbbbbbbbb",
    "bbbbbbbbbbb",
    "bbbbbbbbbbb",
    "aaaaaaaaaaa",
]


def saddle_px(t):
    """the racing saddle, painted by part; light from above (bright top, dark bottom edge, no rim all round)"""
    mat = t.cube["mat"]; n = t.cube["name"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    key = {"a": "L1", "b": "L2", "c": "L3", "d": "L0"}
    if mat == "fur":        # sheepskin: soft uneven tufts, no grid
        if f == "up":       # a few lit tips of wool, no grid
            return p["F2"] if h32(i, j, 33) % 100 < 11 else p["F1"]
        if j == h - 1: return p["F1"] if h32(i, 37) % 100 < 30 else p["F0"]
        return p["F2"] if h32(i, 39) % 100 < 25 else p["F1"]
    if mat == "iron":
        if f == "up": return p["I2"]
        return p["I0"] if j == h - 1 and h > 1 else p["I1"]
    if mat == "strap":
        if n == "girth" and f in ("east", "west", "north", "south") and 1 <= j <= 2:
            return p["I2"] if j == 1 else p["I1"]                 # the buckle just under the flap
        if f in ("up", "down"): return p["L1"] if f == "down" else p["L2"]
        return p["L1"] if (n == "leather" and j == h - 1) else p["L2"]
    # hide
    if n in SADDLE_ART and f in ("east", "west"):
        fc = (w - 1 - i) if f == "east" else i
        return p[key[SADDLE_ART[n][j][fc]]]
    if n == "seat" and f == "up":
        return p[key[SEAT_TOP[j][i]]]
    if f == "up": return p["L4"] if n in ("pommel", "cantle_lip") else p["L3"]
    if f == "down": return p["L0"]
    return p["L3"] if j == 0 else (p["L1"] if j == h - 1 else p["L2"])


def preview_faces(m):
    """For previews only: geo.load_geo puts a dropped model "east" face on the outer (+x) side, but GeckoLib mirrors x
    once more and in game it is the INNER face that goes (tested on the T. rex saddle). Swap east/west on the cubes
    that drop one of them, so the preview shows what the game shows. Never call this before exporting for the game."""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m


def build(saddle_on=True, neck_stub=False):
    m = P.Model("carnotaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 57, 0))
    # the trunk: narrow, deep chest, the belly rising to the hips, a low ridge of back muscle
    m.cube(body, (-7, 47, -52), (7, 68, -34), name="chest")
    m.cube(body, (-5, 41, -50), (5, 48, -36), name="keel")                 # the narrow bottom of the chest
    m.cube(body, (-8, 46, -36), (8, 70, -6), name="torso")
    m.cube(body, (-6, 42, -37), (6, 47, -12), name="belly", mat="belly")
    m.cube(body, (-7, 50, -8), (7, 72, 12), name="hips")
    m.cube(body, (-5, 68, -42), (5, 71, -6), name="back")
    # the neck: thick and muscular, straight here and bent up into an S by the rest angles
    # each segment starts well inside the one behind it, its top on the same line and its bottom on the throat line,
    # so the joints never show a step (Rodrigo 01/11 16:29Z: the neck did not fit); it narrows from the shoulders
    # to the head and goes in under the back of the skull
    n1 = m.bone("neck1", body, (0, 57, -52), (REST["neck1"], 0, 0))
    m.cube(n1, (-5.5, 47, -58), (5.5, 67, -40), name="shoulders")      # the base, nearly as deep as the chest
    m.cube(n1, (-4.5, 50, -67), (4.5, 66, -56), name="neck1")
    n2 = m.bone("neck2", n1, (0, 58.5, -64), (REST["neck2"], 0, 0))
    m.cube(n2, (-4, 53, -79), (4, 65, -61), name="neck2")
    m.cube(n2, (-3, 50, -79), (3, 54, -69), name="throat")          # the throat skin from the jaw down to the neck
    hd = m.bone("head", n2, (0, 59, -77))
    head(m, hd, 53, -77, rest=(REST["skull"], 0, 0))
    arms(m, body); legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the head, drawn face by face
# east = the animal's left side (mirrored onto the right); column 0 is the FRONT, row 0 the TOP.
# north = the front (column 0 on the animal's left); up = the top (row 0 at the back).
FACE_ART = {
    ("cranium", "east"): [      # 9 x 13: the forward eye on the front corner (amber, a slit pupil, a glint over
        "221222122",            # it, the mask's shadow as a brow), the mask behind it, the keyhole slot as one
        "m1mm22222",            # dark notch under its front, crease, cheek, lips
        "mmmmmm222",
        "YgpifM212",
        "iIpIfM222",
        "ffffmm222",
        "1fmM12222",
        "MM1M13333",
        "M44433333",
        "333334333",
        "433333333",
        "343334343",
        "111111111"],      # the lip line over the teeth
    ("cranium", "north"): [     # 10 x 13: only the outer columns and the top show (the snout is in front)
        "2221221222",
        "2222222222",
        "m22222222m",
        "Y22222222Y",
        "i22222222i",
        "f22222222f",
        "f33333333f",
        "M33333333M",
        "3333333333",
        "4333333334",
        "3333333333",
        "4333333334",
        "4444444444"],
    ("cranium", "up"): [        # 10 x 9: midline groove, rugose toward the horns
        "2222112222",
        "2o221122o2",
        "oNo2112oNo",
        "2o221122o2",
        "2222112222",
        "2222112222",
        "2o22112222",
        "2222112o22",
        "2222112222"],
    ("temporal", "east"): [     # 5 x 6: the muscle, two feature scales with their shadow
        "23332",
        "33x33",
        "33133",
        "34333",
        "333x3",
        "44414"],
    ("snout", "east"): [        # 10 x 10: nostril, mask from the eye forward, foramina, lips
        "2222222222",
        "2222222mmm",
        "2nn222mmmm",
        "23333Mmmm1",
        "33333MMmm1",
        "333333333M",
        "3333333333",
        "3233323332",
        "3333333333",
        "1111111111"],
    ("snout", "up"): [          # 7 x 10 (the nasal ridge covers the middle)
        "2122212",
        "2222222",
        "1222221",
        "2222222",
        "2122212",
        "2222222",
        "2222221",
        "1222222",
        "2222222",
        "2122212"],
    ("snout", "north"): ["2222222", "2222222", "3333333", "3333333", "3333333", "3333333", "3333333", "3333333",
                         "4333334", "4444444"],
    ("premax", "east"): ["22", "22", "23", "33", "33", "33", "34", "44", "11"],
    ("premax", "north"): [
        "222222",
        "222222",
        "323323",
        "333333",
        "333333",
        "333333",
        "344443",
        "444444",
        "444444"],
    ("premax", "up"): ["222222", "212212"],
    ("nasal", "up"): ["2222", "2NN2", "2oo2", "2222", "22N2", "2No2", "2222", "2NN2", "2oo2"],
    ("nasal", "east"): ["232332323", "222222222"],
    ("nasal", "north"): ["2332", "2222"],
    ("horn_base", "east"): ["RRrR", "rrqr", "rqrr"],
    ("horn_base", "up"): ["RrR", "rrR", "Rrr", "rRr"],
    ("horn_base", "north"): ["RRr", "rqr", "rrq"],
    ("horn_base", "south"): ["rRr", "rrq", "qrr"],
    ("horn", "east"): ["HHH", "hhH", "hhh"],
    ("horn", "west"): ["HHH", "hhh", "hhh"],
    ("horn", "up"): ["HWWW", "HWwW", "HWWW"],
    ("horn", "north"): ["HHHH", "hhhH", "hhhh"],
    ("horn", "south"): ["HHHH", "hhhh", "hhhh"],
    ("horn_tip", "east"): ["WH", "HH"],
    ("horn_tip", "west"): ["WH", "HH"],
    ("horn_tip", "up"): ["wW", "Ww"],
    ("horn_tip", "north"): ["WW", "HH"],
    ("horn_tip", "south"): ["WH", "HH"],
    ("jaw_front", "east"): [    # 14 x 3
        "22222222222222",
        "44444444444444",
        "bbbbabbbbbbabb"],
    ("jaw_front", "north"): ["22222", "44444", "bbbbb"],
    ("jaw_back", "east"): ["2222222", "4444444", "4444b44", "bbbbabb"],
    ("gular", "east"): ["bcbbcbb", "ababaab"],
    ("gular", "north"): ["bbbbbbb", "abababa"],
    ("occiput", "east"): ["22", "22", "23", "33", "33", "33", "33", "34", "44"],
}


def fill_face(img, cube, face, rows, cmap):
    u, v, w, h = cube["uv"][face]
    assert (len(rows), len(rows[0])) == (h, w), (cube["name"], face, (w, h), (len(rows[0]), len(rows)))
    # the plain skin tones get the same small scales as the body (a seam on the shaded side, a lit corner);
    # the drawn marks (eye, mask, lips, horns, rugosity) stay as drawn
    seed = zlib.crc32((cube["name"] + face).encode()) % 97
    out = []
    for j, row in enumerate(rows):
        r = []
        for i, ch in enumerate(row):
            if ch in KNOB.get("head_scales", "23"):
                sc = skin.scales(i, h - 1 - j, cell=4.2, seed=seed)
                ch = str(int(ch) - 1) if sc == "edge" else (str(int(ch) + 1) if sc == "hi" and KNOB["head_hi"] else ch)
            r.append(ch)
        out.append("".join(r))
    rows = out
    P.stamp(img, None, cube, face, rows, cmap, at=(0, 0))


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        if t.cube["mat"] in ("hide", "fur", "strap", "iron"): return saddle_px(t)
        c = t.cube; f = t.face; mat = c["mat"]
        if mat == "claw": return p["ker0"]
        if c["name"] in BODY_PARTS: return body_px(t, sex)
        if mat == "horn": return p["ker0"]
        if mat == "horn_base": return p["hr0"] if sex == "male" else p["hb0"]
        if mat == "teeth":      # rows from the top: gum (inside the snout), then 1-3 px of tooth below the lip
            if f not in ("east", "west"): return None
            col = int(math.floor(t.L[2])); row = t.j
            if row == 0: return p["gum"]
            if (col + 40) % 2: return None                                        # slender teeth, close together
            r = h32(col, 11) % 6
            if r == 5 and h32(col, 14) % 2: return None                            # a lost tooth: an uneven row
            size = 3 if r < 2 else (1 if r == 5 else 2)                        # long ones, and now and then a new one
            return (p["tooth"] if row < size else p["tooth2"]) if row <= size else None
            return None
        if mat == "teeth_lo":   # rows from the top: 2 px of tooth, then the gum inside the jaw
            if f not in ("east", "west"): return None
            col = int(math.floor(t.L[2])); row = t.j
            if row == t.h - 1: return p["gum"]
            if (col + 41) % 3 == 0 and row >= (0 if h32(col, 13) % 3 else 1): return p["tooth2"] if row == 0 else p["tooth"]
            return None
        if mat == "mouth": return p["gum"] if f in ("up", "down") else p["mouth"]
        if mat == "tongue": return p["tongue"] if f == "up" else p["mouth"]
        if mat == "gular" or f == "down": return p["b1"]
        if f == "up": return p["k2"]
        return p["k3"]
    return sh


# ------------------------------------------------------------------ the body skin
# The rules against the "AI look" (study of 01/11, on the page): every mark has a cause in the animal (no noise);
# a small palette with hue-shifted ramps; tone borders follow the body and wander slowly (no bands parallel to the
# cube edges); one light from above (highlight on top, shadow below, never a dark rim all round = pillow shading);
# detail where the eye goes (head, shoulders, tail base), calm big areas; spacing irregular but never random dots.
TRUNK = {"chest", "keel", "torso", "hips", "back", "shoulders", "neck1", "neck2", "throat", "tail1", "tail2", "tail3", "tail4",
         "tail5", "tail_muscle", "rib1", "rib2", "thigh", "knee", "arm", "forearm", "hand"}
LEG = {"calf", "shin", "meta", "toe_mid", "toe_out", "toe_in", "hallux"}
BODY_PARTS = TRUNK | LEG | {"belly"}
STEP_DN = {"k5": "k4", "k4": "k3", "k3": "k2", "k2": "k1", "k1": "k0", "k0": "k0", "b1": "b0", "b0": "k4", "b2": "b1"}
STEP_UP = {"k0": "k1", "k1": "k2", "k2": "k3", "k3": "k4", "k4": "k5", "k5": "k5", "b0": "b1", "b1": "b2", "b2": "b2"}

# the saddles across the back: (z centre, half length at the spine), from the neck to the tail tip; the last ones
# close into rings on the thin tail
SADDLES = [(-66, 4), (-43, 6), (-19, 6), (6, 6), (31, 5), (53, 4), (72, 3), (88, 2.5)]


def _wave(z):
    return 0.05 * math.sin(z * 0.17) + 0.035 * math.sin(z * 0.41 + 1.3)


def _feature_scales():
    """centres of the big scattered scales on one side, in (z, y) of the rest pose: never in rows, denser on the
    shoulders, the chest and the tail base (Hendrickx & Bell 2021), sparse elsewhere"""
    pts = []
    for z in range(-90, 100):
        for y in range(0, 82):
            k = h32(z, y, 77) % 1000
            dense = (-62 <= z <= -30) or (6 <= z <= 42)
            if k < (26 if dense else 8):
                if all((z - a) ** 2 + ((y - b) * 1.3) ** 2 > 40 for a, b in pts[-80:]):
                    pts.append((z, y))
    return set(pts)


FEATURE = _feature_scales()
BELLY_ROWS = set()
_z = -52
while _z < 14:
    BELLY_ROWS.add(_z); _z += 3 + h32(_z, 3) % 2
WRINKLES = {}
_z = 9
while _z < 32:        # vertical wrinkles on the front of the tail: uneven spacing and length, short creases
    WRINKLES[_z] = 0.30 + (h32(_z, 5) % 4) * 0.07
    _z += 5 + h32(_z, 9) % 4


# where the pale underside ends on each part (fraction of the part's height), and the size of the body scales
UNDER = {"chest": 0.24, "torso": 0.2, "shoulders": 0.24, "neck1": 0.22, "neck2": 0.24, "hips": 0.12, "tail1": 0.14,
         "tail2": 0.2, "tail3": 0.22, "tail4": 0.25, "tail5": 0.3}
CELL = {"k4": 5.0, "k3": 5.6, "k2": 6.2}
KNOB = {"feature": False, "hi": False, "head_hi": False, "cellband": True, "head_scales": "3"}   # 17:2xZ: calmer skin, one tone per scale


def _in_saddle(z, y, v, up):
    """is a scale centred at (z, y) inside one of the dark saddles? returns (zc, depth into it 0..1) or None"""
    for zc, hl in SADDLES:
        if not up and v < 0.58 + 0.08 * math.sin(z * 0.8 + zc):
            continue
        reach = hl * (0.4 + 0.6 * (v if not up else 1.0)) + 0.8 * math.sin(y * 0.7 + zc)
        if abs(z - zc) < reach:
            return zc, 1 - abs(z - zc) / max(reach, 0.1)
    return None


def body_px(t, sex):
    """the house skin (scales with a seam on the shaded side and a lit corner, belly scutes, muscle contour) with the
    Carnotaurus marks: dark saddles whose edges follow whole scales, and big feature scales scattered on the flanks
    (Hendrickx & Bell 2021), more of them on the shoulders and the tail base"""
    male = sex == "male"; p = pal_for(sex)
    c = t.cube; n = c["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    u_, w_ = skin.face_uv_coords(t)
    z, y = t.L[2], t.L[1]
    zi, yi = int(math.floor(z)), int(math.floor(y))
    v = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    seed = zlib.crc32(n.encode()) % 97
    belly = lambda uu, ww: p[{"seam": "b0", "hi": "b2", "base": "b1"}[skin.scutes(uu, ww, row=3, width=6)]]
    # ---- the underside: rows of wide scutes
    if (f == "down" and n not in LEG and n not in ("thigh", "knee")) or n in ("belly", "keel", "tail_muscle", "throat"):
        if f == "down": return belly(t.L[0], t.L[2])
        if f == "up": return p["k3"]
        return belly(u_, w_)
    # ---- legs: bird-like scutes across the front of the shin, the foot and the toes, small scales on the sides
    if n in LEG:
        base = "k3" if f in ("north", "up") else "k2"
        if n in ("meta", "toe_mid", "toe_out", "toe_in", "shin") and f in ("north", "up", "east", "west"):
            k = math.floor(t.L[1] if f != "up" else t.L[2]) % 3
            if k == 0 and (t.i % 4) != 1: return p[STEP_DN[base]]
            return p[base]
        sc = skin.scales(u_, w_, cell=4.0, seed=seed)
        if sc == "edge": return p[STEP_DN[base]]
        if sc == "hi" and KNOB["hi"]: return p[STEP_UP[base]]
        return p[base]
    if n in ("arm", "forearm", "hand"):
        base = "k3" if f != "down" else "k2"
        return p[STEP_DN[base]] if skin.scales(u_, w_, cell=2.6, seed=seed) == "edge" else p[base]
    # ---- trunk, neck, tail, thigh
    if side and n in UNDER:
        jag = (0, 0, 1, 1, 1, 0)[int(z // 3) % 6] / max(1, t.h)
        line = UNDER[n] + jag
        if v < line: return belly(u_, w_)
        if v < line + 1.2 / max(1, t.h): return p["b0"]
    if n in ("thigh", "knee"):
        base = "k3" if v > 0.3 else "k4"
    elif n in ("back", "rib1", "rib2") or f == "up":
        base = "k2"
    else:
        base = "k4" if v < 0.5 else ("k3" if v < 0.78 else "k2")
    cell = CELL[base]
    if KNOB.get("cellband") and side and n not in ("thigh", "knee", "back", "rib1", "rib2"):
        # the flank tone is picked per whole scale (by the height of its centre), so a band border runs between
        # scales instead of cutting through them: no half-scales of two tones
        cell = 5.6
        d1, d2, cc = skin.voronoi(math.floor(u_) + 0.5, math.floor(w_) + 0.5, cell, seed)
        vc = (cc[3] - c["from"][1]) / max(1, t.h)
        base = "k4" if vc < 0.5 else ("k3" if vc < 0.78 else "k2")
    d1, d2, cc = skin.voronoi(math.floor(u_) + 0.5, math.floor(w_) + 0.5, cell, seed)
    # the saddles, scale by scale: a scale is dark when its centre falls inside the saddle
    if n not in ("thigh", "knee"):
        cz, cy = (cc[2], cc[3]) if side else (cc[3], y)
        if f in ("east", "west"):
            sad = _in_saddle(cz, cy, max(0.0, min(1.0, (cy - c["from"][1]) / max(1, t.h))), False)
        elif f == "up":
            sad = _in_saddle(cz, cy, 1.0, True)
        else:
            sad = None
        if sad:
            zc, deep = sad
            base = "k1" if (male or (zc // 7) % 2 == 0) else "k2"
            if male and deep > 0.55 and (f == "up" or v > 0.82): base = "k0"
    # the big feature scales: a raised 2x2 scale, lit on top, its shadow under it
    if KNOB["feature"] and f in ("east", "west") and v > 0.2 and n not in ("knee",):
        for (fz, fy) in ((zi, yi), (zi - 1, yi), (zi, yi + 1), (zi - 1, yi + 1), (zi, yi - 1), (zi - 1, yi - 1)):
            if (fz, fy) in FEATURE:
                dy = yi - fy
                if dy == 0: return p[STEP_UP[STEP_UP[base]]] if base in ("k0", "k1", "k2") else p[STEP_UP[base]]
                if dy == -1: return p[STEP_UP[base]]
                if dy == 1: return p[STEP_DN[base]]
    # the thigh: lit on its upper front, in shade low behind where it meets the tail muscle (no drawn ring: on this
    # thigh it read as a badge)
    if n == "thigh" and f in ("east", "west") and t.rel[1] < 0.35 and t.rel[2] > 0.5:
        base = STEP_DN[base]
    sc = skin.scales(u_, w_, cell=cell, seed=seed)
    if sc == "edge": return p[STEP_DN[base]]
    if sc == "hi" and KNOB["hi"]: return p[STEP_UP[base]]
    return p[base]


def decals_for(sex):
    cmap = charmap(sex)
    p = pal_for(sex)

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        for (name, face), rows in FACE_ART.items():
            if name in C and face in C[name]["uv"] and C[name]["uv"][face][2] > 0:
                fill_face(img, C[name], face, rows, cmap)
        # mouth interior: palate rim with the teeth (hidden by the lips when shut), tongue on the jaw floor
        for name, f in (("snout", "down"), ("premax", "down"), ("cranium", "down"), ("jaw_front", "up"), ("jaw_back", "up")):
            c = C[name]; u, v, ww, hh = c["uv"][f]
            for j in range(hh):
                for i in range(ww):
                    rim = i in (0, ww - 1)
                    if name in ("snout", "premax"):
                        k = h32(j, name, 29) % 4      # teeth of uneven size: a long one, a worn one, a gap
                        tooth = p["tooth"] if k < 2 else (p["tooth2"] if k == 2 else p["gum"])
                        col = (tooth if j % 2 == 0 else p["gum"]) if rim else p["gum"] if i in (1, ww - 2) else p["mouth"]
                    elif name == "cranium":
                        col = p["mouth"]
                    elif name == "jaw_front":
                        k = h32(j, 23) % 5
                        tooth = p["tooth"] if k < 2 else (p["tooth2"] if k < 4 else p["gum"])
                        col = (tooth if j % 2 == 0 else p["gum"]) if rim else (p["tongue"] if 1 <= i < ww - 1 else p["gum"])
                    else:
                        col = p["gum"] if rim else p["tongue"]
                    img[v + j, u + i] = (*col, 255)
    return dec


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
