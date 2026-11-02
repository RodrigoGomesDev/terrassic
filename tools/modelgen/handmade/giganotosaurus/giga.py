"""Giganotosaurus carolinii, made by hand from its own study (page "Giganotosaurus: estudo antes de modelar", approved
by Rodrigo on 01/11/2026 18:31Z with the "tubarão" colours and 12.5 m).

Drawn at 24 px = 1 m (game scale 0.667), like the Carnotaurus: the real skull is 1.6 m, so at 16 px/m it would only
have 26 px to carry the rough snout, the hornlet, the eave over the eye, the chin and the blade teeth.

The head (each point from the study):
- a knife: long, low and NARROW, 38 px (1.6 m) from the snout tip to the back of the skull, 14 px tall at the back,
  8 px at the tip, 10 px wide at the back and 6 at the tip; the top line steps down to the snout;
- rough nasal bones: a low ridge down the middle of the snout, drawn with lumps (red-wine on the male);
- the lacrimal crest: a small hornlet in front of the eye that points up and back;
- the eye on the SIDE (not forward like the T. rex and the Carnotaurus), deep under a 1 px eave of bone (the
  supraorbital), with the keyhole notch under it (the postorbital process that reaches into the orbit);
- the jaw joint far behind, a long thin lower jaw and the "chin": the front of the jaw drops in a small step;
- blade teeth: flat, even and close, with a broad base and a tip bent back, hanging over the lower jaw;
- shark colours: slate on top down to the lip, a cream lower jaw and throat.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 24

SCHEMES = {
    "tubarao": {    # steel grey above, off-white below like a great white (lighter and bluer than the Spino's dark
                    # teal with a tan belly); shadows lean to blue-violet, lights to a warm grey
        "k0": "242a33", "k1": "343e49", "k2": "46525d", "k3": "5b6872", "k4": "74828a", "k5": "939f9f",
        "b0": "a6a495", "b1": "c3c0b0", "b2": "d9d6c8", "b3": "ece9de",
        "hr0": "3b2228", "hr1": "5a2c33", "hr2": "7a3a3d", "hr3": "96524b",
        "female": {"k1": "3c4650", "k2": "505c66", "k3": "66737b", "k4": "808d93", "k5": "a0aba9"},
    },
    "poeira": {
        "k0": "1d1916", "k1": "2c2620", "k2": "3d342b", "k3": "51463a", "k4": "6a5c4b", "k5": "86775f",
        "b0": "9c8f73", "b1": "b6a987", "b2": "cec19f", "b3": "e4d9bb",
        "hr0": "3e1a17", "hr1": "682a22", "hr2": "8f3f30", "hr3": "ad5a40",
        "female": {"k1": "322b24", "k2": "443a30", "k3": "594d40", "k4": "726452", "k5": "8e7f66"},
    },
}
SCHEME = ["tubarao"]

PAL = {
    "hb0": hx("6f6c60"), "hb1": hx("948f7d"), "hb2": hx("b6b19c"), "hb3": hx("cfcab4"),
    "claw": hx("2b2724"), "claw2": hx("4a433c"), "clawt": hx("b8b09a"),
    "iris": hx("c9b458"), "iris2": hx("8e7a32"), "pupil": hx("0f0d0c"), "glint": hx("f1ecc8"), "sock": hx("0f1216"),
    "gum": hx("6e2a2e"), "mouth": hx("33161a"), "tongue": hx("9c4a46"), "tooth": hx("f2eedd"), "tooth2": hx("c9c2a8"),
}


def pal_for(sex, scheme=None):
    sc = SCHEMES[scheme or SCHEME[0]]
    p = dict(PAL)
    for k, v in sc.items():
        if k != "female": p[k] = hx(v)
    if sex != "male":
        for k, v in sc["female"].items(): p[k] = hx(v)
    return p


def charmap(sex):
    male = sex == "male"
    p = pal_for(sex)
    c = {str(i): p[f"k{i}"] for i in range(6)}
    c.update({"a": p["b0"], "b": p["b1"], "c": p["b2"], "d": p["b3"], "L": p["k0"],
              "p": p["pupil"], "i": p["iris"], "I": p["iris2"], "g": p["glint"], "s": p["sock"]})
    # rough nasal lumps and the hornlet: wine red on the male, bone on the female
    for ch, a, b in (("q", "hr0", "hb0"), ("r", "hr1", "hb1"), ("R", "hr2", "hb2"), ("t", "hr3", "hb3")):
        c[ch] = p[a] if male else p[b]
    return c


def _ground(m):
    import geo
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes}))
    m.shift(-lo)


def head(m, parent, hy, hz, rest=(-4, 0, 0)):
    """the skull and the jaw. (hy, hz): the mouth line at the back of the skull; returns the skull bone"""
    def B(x0, y0, z0, x1, y1, z1):
        return (x0, hy + y0, hz + z0), (x1, hy + y1, hz + z1)
    sk = m.bone("skull", parent, (0, hy + 7, hz), rest)
    # the upper skull, stepping down from the back to the tip
    m.cube(sk, *B(-5, 0, -12, 5, 14, 0), name="cranium")
    m.cube(sk, *B(-4, 5, -1, 4, 13, 2), name="occiput")
    m.pair(sk, sk, *B(4, 2, -8, 7, 9, -2), name="temporal")            # the jaw muscle behind the eye
    m.pair(sk, sk, *B(4, 12, -11, 6, 13, -5), name="brow")             # the eave of bone over the eye
    m.cube(sk, *B(-4, 0, -20, 4, 12, -11), name="lacrimal")
    m.cube(sk, *B(-3.5, 0, -30, 3.5, 10, -19), name="snout")
    m.cube(sk, *B(-3, 0, -38, 3, 8, -29), name="tip")
    # the rough nasal ridge down the middle, in two steps; the hornlet of the lacrimal, leaning back
    # rough lumps, uneven in size and spacing, each 1 px proud of the bone
    m.cube(sk, *B(-1.5, 11, -19, 1.5, 13, -15), name="nasal_b")
    m.cube(sk, *B(-1, 9, -25, 1, 11, -20), name="nasal_m")
    m.cube(sk, *B(-1.5, 9, -29, 1.5, 11, -26), name="nasal_f")
    m.pair(sk, sk, *B(2, 11, -15, 3, 14, -13), name="hornlet", mat="hornlet", rot=(-28, 0, 0), origin=(2.5, hy + 12, hz - 14))
    # the jaw: hinged far back, long and thin, with the chin at the tip
    jaw = m.bone("jaw", sk, (0, hy + 1, hz - 1))
    m.cube(jaw, *B(-5, -6, -12, 5, 0, -1), name="jaw_back")
    m.cube(jaw, *B(-3.5, -5, -20, 3.5, 0, -11), name="jaw_mid")
    m.cube(jaw, *B(-2.5, -4, -37, 2.5, 0, -19), name="jaw_front")
    m.cube(jaw, *B(-2, -6, -37, 2, -3, -34), name="chin")
    m.cube(jaw, *B(-4, -7, -11, 4, -5, 0), name="gular", mat="gular")   # the throat skin
    m.cube(jaw, *B(-4, -1, -10, 4, 2, -2), name="cheek", mat="mouth")    # the mouth's inner wall (no slit half-open)
    m.cube(jaw, *B(-1.5, -2, -32, 1.5, 1, -6), name="tongue", mat="tongue")
    m.cube(sk, *B(-1, -1, -34, 1, 2, -14), name="palate", mat="mouth")
    # blade teeth: alpha planes between the lips and the lower jaw (upper row, shows with the mouth shut) and inside
    # the snout (lower row, shows only with the mouth open)
    m.pair(sk, sk, *B(3.75, -3, -20, 3.75, 1, -12), name="teeth_a", mat="teeth")
    m.pair(sk, sk, *B(3.0, -3, -30, 3.0, 1, -20), name="teeth_b", mat="teeth")
    m.pair(sk, sk, *B(2.75, -3, -37, 2.75, 1, -30), name="teeth_c", mat="teeth")
    m.pair(jaw, jaw, *B(3.0, -1, -20, 3.0, 2, -12), name="teeth_lo_a", mat="teeth_lo")
    m.pair(jaw, jaw, *B(2.0, -1, -36, 2.0, 2, -20), name="teeth_lo_b", mat="teeth_lo")
    return sk


def build_head_only():
    """step 1 of the model: the head on a stub of neck, for the close-up"""
    m = P.Model("giganotosaurus")
    root = m.bone("root", None, (0, 0, 0))
    n2 = m.bone("neck2", root, (0, 20, 6))
    m.cube(n2, (-6, 12, 1), (6, 26, 14), name="neck_stub")
    hd = m.bone("head", n2, (0, 20, 0))
    head(m, hd, 14, 0)
    _ground(m)
    return m


REST = {   # bone rest angles (x: positive = the far end up for necks/tail, knee forward for the thigh)
    "neck1": 10, "neck2": -6, "skull": -4, "thigh": 16, "shin": -42, "foot": 38, "toes": -12,
    "arm": 34, "forearm": -70, "tail1": -3, "tail2": 1, "tail3": 1, "tail4": 0, "tail5": 0,
}


def legs(m, body):
    """heavy legs for 7 t: a deep drumstick of a thigh set into the hip, a long femur (1.4 m) and a shorter shin
    (1.1 m): a walker, not a sprinter; a short stout metatarsus and broad toes. Knees out, feet in under the body"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (10 * sx, 76, 0), (REST["thigh"], 0, 5 * sx))
        sh = m.bone(f"shin_{side}", th, (12 * sx, 44, 0), (REST["shin"], 0, -9 * sx))
        ft = m.bone(f"foot_{side}", sh, (12 * sx, 17, 0), (REST["foot"], 0, 4 * sx))
        m.bone(f"toes_{side}", ft, (12 * sx, 1, 0), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (4, 46, -12), (16, 81, 10), name="thigh")          # the drumstick, into the hip
    m.pair("thigh_l", "thigh_r", (5, 38, -9), (16, 48, 5), name="knee")
    m.pair("shin_l", "shin_r", (6.5, 28, -8), (17.5, 45, 6), name="calf")
    m.pair("shin_l", "shin_r", (8, 15, -5), (16, 29, 3), name="shin")
    m.pair("foot_l", "foot_r", (8.5, -1, -4), (15.5, 18, 4), name="meta")
    m.pair("toes_l", "toes_r", (10, -3, -18), (14, 2, 0), name="toe_mid")
    m.pair("toes_l", "toes_r", (14, -3, -14), (18, 2, -1), name="toe_out")
    m.pair("toes_l", "toes_r", (6, -3, -14), (10, 2, -1), name="toe_in")
    m.pair("toes_l", "toes_r", (11.5, -3, -21), (12.5, 0, -17), name="claw_mid", mat="claw")
    m.pair("toes_l", "toes_r", (15.5, -3, -17), (16.5, 0, -13), name="claw_out", mat="claw")
    m.pair("toes_l", "toes_r", (7.5, -3, -17), (8.5, 0, -13), name="claw_in", mat="claw")
    m.pair("foot_l", "foot_r", (7, 2, 2), (9, 5, 6), name="hallux")


def arms(m, body):
    """short arms (as on its relative Meraxes): an upper arm of 0.5 m, a forearm and a hand of three hooked fingers,
    folded against the chest"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (9 * sx, 60, -64), (REST["arm"], 0, 0))
        m.bone(f"forearm_{side}", a, (9.5 * sx, 48, -64), (REST["forearm"], 0, 0))
    m.pair("arm_l", "arm_r", (7, 47, -66), (11, 61, -62), name="arm")
    m.pair("forearm_l", "forearm_r", (7.5, 39, -66), (10.5, 49, -63), name="forearm")
    m.pair("forearm_l", "forearm_r", (7, 35, -67), (11, 40, -63), name="hand")
    m.pair("forearm_l", "forearm_r", (9.5, 32, -67), (10.5, 35, -65), name="claw_a", mat="claw")
    m.pair("forearm_l", "forearm_r", (7.5, 32, -67), (8.5, 35, -65), name="claw_b", mat="claw")


def tail(m, body):
    """long, TALL and NARROW: the tall spines on top and the blade-like chevrons under it make a deep blade, not the
    Carnotaurus' wide base; it tapers slowly to a thin tip"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 8, 42, 8, 60, 92), ("tail2", 40, 74, 6, 65, 88), ("tail3", 72, 104, 5, 69, 84),
        ("tail4", 102, 130, 3, 72, 81), ("tail5", 128, 154, 1.5, 74, 79)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    m.cube("tail1", (-2, 91, 10), (2, 94, 40), name="tail_ridge1", mat="ridge")     # the tall caudal spines
    m.cube("tail2", (-1.5, 87, 41), (1.5, 90, 70), name="tail_ridge2", mat="ridge")
    m.cube("tail1", (-5, 56, 4), (5, 62, 38), name="tail_keel")                  # the blade chevrons + the muscle


# ------------------------------------------------------------------ the saddle: a Patagonian recado
SADDLE_PAL = {   # its own: a gaucho recado from the same Patagonia as the animal, not the vanilla brown + iron
    "W0": hx("2e2420"), "W1": hx("6b2b28"), "W2": hx("a9946f"), "W3": hx("cdbd99"),   # wool: black-brown, wine, natural, light
    "L0": hx("2f1f16"), "L1": hx("4a3020"), "L2": hx("63412a"),                        # dark leather: carona and bastos
    "C0": hx("7a5636"), "C1": hx("9c7449"), "C2": hx("b48b5a"),                        # tan capybara hide on the seat
    "D0": hx("3e2a1b"), "D1": hx("5e4129"), "D2": hx("7f5a38"), "D3": hx("9b7246"),    # carved wood of the bell stirrups
    "G0": hx("4a3a2c"), "G1": hx("6f5a44"),                                            # the wide woven girth
    "I0": hx("4d4d4b"), "I1": hx("7d7d79"), "I2": hx("a9a9a2"),
}
SADDLE_MATS = ("wool", "carona", "basto", "seat", "girth", "wood", "iron")


def saddle(m, body):
    """A Patagonian recado, the gaucho's saddle from the land of the Giganotosaurus: built in layers, not on a tree.
    A woven wool blanket (jerga) over the back and down the flanks, with a stepped band; a dark leather carona on it;
    two leather rolls (bastos) lying either side of the keel, so the spine runs free in the channel between them; a
    tan capybara-hide cover as the seat; one wide woven girth with an iron ring; and carved wooden bell stirrups
    (estribos de campana) on long leathers. No bags, no studs. Faces lying on the body or on another layer are left
    out (GeckoLib draws without back-face culling; the model "east" face of a +x piece is the inner one in game)."""
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    sd = m.bone("saddle", body, (0, 88, -33))
    m.cube(sd, (-10, 88, -47), (10, 91, -19), name="jerga", mat="wool", faces=out("down"))
    m.pair(sd, sd, (10, 74, -47), (11, 91, -19), name="jerga_side", mat="wool", faces=out("east"))
    m.cube(sd, (-11, 91, -44), (11, 92, -22), name="carona", mat="carona", faces=out("down"))
    m.pair(sd, sd, (3, 92, -43), (7, 95, -23), name="basto", mat="basto", faces=out("down"))
    m.cube(sd, (-8, 95, -39), (8, 96, -27), name="cover", mat="seat", faces=out("down"))
    # the girth: over the blanket, in under the torso and the belly, across underneath
    m.pair(sd, sd, (11, 72, -35), (12, 91, -31), name="cinch", mat="girth", faces=out("east"))
    m.pair(sd, sd, (10, 55, -35), (11, 72, -31), name="cinch_low", mat="girth", faces=out("east", "down"))
    m.pair(sd, sd, (8, 54, -35), (11, 55, -31), name="cinch_step", mat="girth", faces=out("up"))
    m.pair(sd, sd, (8, 51, -35), (9, 54, -31), name="cinch_belly", mat="girth", faces=out("east", "up"))
    m.cube(sd, (-9, 50, -35), (9, 51, -31), name="cinch_under", mat="girth", faces=out("up"))
    m.pair(sd, sd, (12, 76, -36), (13, 79, -30), name="ring", mat="iron", faces=out("east"))
    # the stirrup leathers come out from under the bastos and run down the blanket; the bell hangs just below its
    # edge, about a rider's leg under the seat (lower and the boot would dangle)
    m.pair(sd, sd, (11, 75, -41), (12, 91, -39), name="leather", mat="basto", faces=out("east", "down"))
    m.pair(sd, sd, (11, 72, -42), (13, 75, -38), name="bell_top", mat="wood", faces=out("east"))
    m.pair(sd, sd, (10.5, 66, -43), (13.5, 72, -37), name="bell", mat="wood")


# The jerga's flank, woven by hand: column 0 at the FRONT, row 0 at the top. 0 black-brown, 1 wine, 2 natural, 3 light.
# A plain natural field, wine stripes, and a stepped line over wine (a range of hills, the "Degraus" of the logo):
# rings or diamonds with a hole read as eyes on a flank, so none.
JERGA_SIDE = [
    "2222222222222222222222222222",
    "2222222222222222222222222222",
    "2222222222222222222222222222",
    "1111111111111111111111111111",
    "3333333333333333333333333333",
    "0000000000000000000000000000",
    "3300000000000003330000000000",
    "1333000000000333133300000000",
    "1113330000033311111333000003",
    "1111133303331111111113330333",
    "1111111333111111111111133311",
    "0000000000000000000000000000",
    "3333333333333333333333333333",
    "1111111111111111111111111111",
    "2222222222222222222222222222",
    "2222222222222222222222222222",
    "1111111111111111111111111111",
]
WOOL = {"0": "W0", "1": "W1", "2": "W2", "3": "W3"}


def saddle_px(t):
    """the recado, painted by layer; light from above, the bottom edge of each layer one step darker"""
    c = t.cube; mat = c["mat"]; n = c["name"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "wool":
        if n == "jerga_side" and f in ("east", "west"):
            fc = (w - 1 - i) if f == "east" else i
            return p[WOOL[JERGA_SIDE[min(j, len(JERGA_SIDE) - 1)][min(fc, len(JERGA_SIDE[0]) - 1)]]]
        if n == "jerga_side" and f == "down": return p["W1"]                 # the wine fringe seen from below
        if f in ("north", "south"): return p["W1"] if n == "jerga" else p[WOOL[JERGA_SIDE[min(j, 16)][0]]]
        return p["W2"]
    if mat == "carona":
        if f == "up": return p["L1"]
        return p["L0"]
    if mat == "basto":      # rolled leather: lit on top, a dark seam along the bottom
        if f == "up": return p["L2"]
        if f == "down": return p["L0"]
        return p["L0"] if (j == h - 1 and h > 1) else p["L1"]
    if mat == "seat":       # capybara hide: plain tan, a darker stitched border (no pores: dots read as noise)
        if f == "up":
            edge = i == 0 or j == 0 or i == w - 1 or j == h - 1
            return p["C1"] if edge else p["C2"]
        return p["C0"]
    if mat == "girth":      # woven: one lighter thread down the middle, never a checker
        if f in ("east", "west", "north", "south", "down", "up") and w >= 3 and (i == w // 2): return p["G1"]
        return p["G0"]
    if mat == "wood":       # carved bell: a raised band round the crown, darker at the open mouth below
        if f == "up": return p["D3"]
        if f == "down": return p["D0"]
        if n == "bell_top": return p["D2"] if j == 0 else p["D1"]
        return p["D1"] if j == h - 1 else (p["D3"] if j == 1 else p["D2"])
    # iron
    if f == "up": return p["I2"]
    return p["I0"] if (j == h - 1 and h > 1) else p["I1"]


def preview_faces(m):
    """previews only, called BEFORE packing: geo.load_geo puts a dropped model "east" face on the outer (+x) side, but
    GeckoLib mirrors x once more and in game it is the INNER face that goes (tested on the T. rex saddle). Swap
    east/west on the cubes that drop one, so the preview shows what the game shows. Never export this for the game."""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m


def build(saddle_on=False, head_only=False):
    m = P.Model("giganotosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 76, 0))
    # the trunk: a deep, NARROW chest, the belly rising to the hips, and the keel of the high neural arches on top
    m.cube(body, (-9, 50, -76), (9, 85, -50), name="chest")
    m.cube(body, (-6, 45, -72), (6, 51, -54), name="keel_low")            # the narrow bottom of the chest
    m.cube(body, (-10, 55, -52), (10, 88, -14), name="torso")
    m.cube(body, (-8, 51, -50), (8, 56, -18), name="belly", mat="belly")
    m.cube(body, (-9, 61, -16), (9, 90, 12), name="hips")
    m.cube(body, (-2, 84, -74), (2, 87, -51), name="ridge1", mat="ridge")
    m.cube(body, (-2, 87, -53), (2, 90, -15), name="ridge2", mat="ridge")
    m.cube(body, (-2, 89, -17), (2, 92, 11), name="ridge3", mat="ridge")
    # the neck: strong and fairly long, lower than the T. rex's; each segment starts inside the one behind it
    n1 = m.bone("neck1", body, (0, 70, -74), (REST["neck1"], 0, 0))
    m.cube(n1, (-8, 52, -86), (8, 84, -68), name="shoulders")
    m.cube(n1, (-7, 58, -98), (7, 82, -84), name="neck1")
    n2 = m.bone("neck2", n1, (0, 72, -96), (REST["neck2"], 0, 0))
    m.cube(n2, (-6, 64, -112), (6, 87, -90), name="neck2")      # reaches back into neck1: no slit when it bends
    m.cube(n2, (-4, 60, -114), (4, 65, -92), name="throat")
    hd = m.bone("head", n2, (0, 79, -110))
    head(m, hd, 76, -110, rest=(REST["skull"], 0, 0))
    arms(m, body); legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the head, drawn face by face
# east = the animal's left side (mirrored onto the right); column 0 is the FRONT, row 0 the TOP.
# north = the front (column 0 on the animal's left); up = the top (row 0 at the back).
# 0..5 = the slate ramp (dark to light), a..d = the cream underside, L = the lip line, s = the eye socket,
# i/I/p/g = iris, its shade, pupil, glint; q r R t = the male's red-wine lumps (bone on the female)
FACE_ART = {
    ('cranium', 'east'): ['211122212112', '1ssssss22222', '1sigiIs22222', '1sipIIs22322', '21ssss122222', '222122222222', '232223222222', '332333222222', '333333222222', '343333222222', '333433222223', '443344222334', '554555445555', 'LLLLLLLLLLLL'],
    ('cranium', 'up'): ['1112112111', '1222112221', '2222112222', '2222112222', '2232112322', '2222112222', '2222112222', '2322112232', '2222112222', '2222112222', '2222222222', '2222222222'],
    ('temporal', 'east'): ['433343', '333333', '333233', '332333', '333333', '343333', '444444'],
    ('brow', 'east'): ['122221'],
    ('brow', 'up'): ['34', '33', '33', '33', '34', '33'],
    ('lacrimal', 'east'): ['212211222', '222222222', '222222222', '222322222', '222222222', '322222322', '333223333', '333333333', '343334333', '443444444', '554555455', 'LLLLLLLLL'],
    ('snout', 'east'): ['21222122222', '2s222222222', '2ss22222222', '22222232222', '32222222222', '33322333222', '33333333333', '43343334333', '54555455544', 'LLLLLLLLLLL'],
    ('tip', 'east'): ['212222222', '222222222', '322222222', '332232222', '333333333', '433343333', '554554555', 'LLLLLLLLL'],
    ('tip', 'north'): ['121121', '222222', '232232', '333333', '333333', '433334', '545545', 'LLLLLL'],
    ('tip', 'up'): ['222222', '212212', '222222', '221222', '222122', '222222', '212222', '222222', '222212'],
    ('snout', 'up'): ['2222222', '2222222', '2122222', '2222212', '2222222', '2212222', '2222222', '2222122', '2122222', '2222222', '2222212'],
    ('lacrimal', 'up'): ['22222222', '22222222', '21222212', '22222222', '22222222', '22122222', '22222212', '22222222', '22222222'],
    ('jaw_front', 'east'): ['222222222222222222', '333333343333333333', '343333333334333333', 'bbcbbbbbcbbbbbcbbb'],
    ('jaw_front', 'north'): ['22222', '33333', '33333', 'bbcbb'],
    ('jaw_mid', 'east'): ['222222222', '333343333', '333333343', '4bcbbbbcb', 'bbbabbbbb'],
    ('jaw_back', 'east'): ['22222222222', '33334333333', '33333333433', '44bbcbbbbbb', 'cbcccbccbcc', 'bbbbbabbbbb'],
    ('chin', 'east'): ['bcb', 'bbb', 'abb'],
    ('chin', 'north'): ['bbbb', 'bcbb', 'abba'],
    ('gular', 'east'): ['dcdcdcdcdcd', 'cbcbbcbcbcb'],
    ('gular', 'north'): ['dcdcdcdc', 'cbcbcbcb'],
    ('occiput', 'east'): ['111', '122', '222', '222', '222', '233', '333', '333'],
    ('neck_stub', 'east'): ['1121111211211', '2222222222222', '2222232222222', '2222222222222', '3223222232222', '3333333333333', '3333333333333', '3343333433333', '4444444444444', 'bbbcbbbbbbbbc', 'ccccccccccccc', 'ccbccccccbccc', 'ccccccccccccc', 'bbbbbbbbbbbbb'],
    ('nasal_f', 'up'): ['rRr', 'qrR', 'rqr'],
    ('nasal_f', 'east'): ['rRq', '222'],
    ('nasal_f', 'north'): ['r2r', '222'],
    ('nasal_f', 'south'): ['qrq', '222'],
    ('nasal_m', 'up'): ['qr', 'rR', 'Rr', 'rq', 'qR'],
    ('nasal_m', 'east'): ['rqrRr', '22222'],
    ('nasal_m', 'north'): ['22', '22'],
    ('nasal_m', 'south'): ['qq', '22'],
    ('nasal_b', 'up'): ['qrq', 'rRr', 'Rrq', 'qrR'],
    ('nasal_b', 'east'): ['rRqr', '2222'],
    ('nasal_b', 'north'): ['222', '222'],
    ('nasal_b', 'south'): ['qqq', 'qqq'],
    ('hornlet', 'east'): ['tR', '32', '22'],
    ('hornlet', 'west'): ['Rt', '23', '22'],
    ('hornlet', 'north'): ['2', '2', '2'],
    ('hornlet', 'south'): ['2', '2', '1'],
    ('hornlet', 'up'): ['2', '3'],
}


FIT_WARN = []


def fill_face(img, cube, face, rows, cmap):
    u, v, w, h = cube["uv"][face]
    if (len(rows), len(rows[0])) != (h, w):      # fit while drawing; the build reports it so the art gets fixed
        FIT_WARN.append((cube["name"], face, (w, h), (len(rows[0]), len(rows))))
        rows = [(r + r[-1] * w)[:w] for r in (rows + [rows[-1]] * h)[:h]]
    # the plain slate tones get the same small scales as the body: a seam on the shaded side, no lone lit texel
    seed = zlib.crc32((cube["name"] + face).encode()) % 97
    out = []
    for j, row in enumerate(rows):
        r = []
        for i, ch in enumerate(row):
            if ch in "23" and face in ("east", "west", "up"):
                if skin.scales(i, h - 1 - j, cell=4.2, seed=seed) == "edge": ch = str(int(ch) - 1)
            r.append(ch)
        out.append("".join(r))
    P.stamp(img, None, cube, face, out, cmap, at=(0, 0))


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        c = t.cube; f = t.face; mat = c["mat"]
        if mat == "claw":       # keratin: dark at the base, pale toward the tip, lit on top
            if f in ("east", "west"):
                tip = t.rel[2] < 0.34
                return p["clawt"] if tip else (p["claw2"] if t.rel[1] > 0.5 else p["claw"])
            if f == "north": return p["clawt"]
            return p["claw2"] if f == "up" else p["claw"]
        if mat in SADDLE_MATS: return saddle_px(t)
        if c["name"] in BODY_PARTS or mat == "ridge": return body_px(t, sex)
        if mat == "teeth":      # rows from the top: gum, then blades 4 px apart: a broad base, the tip set back
            if f not in ("east", "west"): return None
            col = int(math.floor(t.L[2])); row = t.j
            if row == 0: return p["gum"]
            k = (col + 300) % 4
            short = h32(col // 4, 21) % 4 == 0        # now and then a shorter (new) blade, never in a pattern
            lost = h32(col // 4, 22) % 13 == 0        # and a gap where one was lost
            if lost: return None
            if row in (1, 2): return (p["tooth"] if row == 1 or k == 2 else p["tooth2"]) if k in (1, 2) else None
            if row == 3: return p["tooth2"] if (k == 2 and not short) else None
            return None
        if mat == "teeth_lo":
            if f not in ("east", "west"): return None
            col = int(math.floor(t.L[2])); row = t.j
            if row == t.h - 1: return p["gum"]
            k = (col + 301) % 3
            if row == t.h - 2: return p["tooth"] if k in (1, 2) else None
            if row == t.h - 3: return p["tooth2"] if k == 1 else None
            return None
        if mat == "mouth": return p["gum"] if f in ("up", "down") else p["mouth"]
        if mat == "tongue": return p["tongue"] if f == "up" else p["mouth"]
        if mat == "hornlet": return p["hr1"] if sex == "male" else p["hb1"]
        if mat == "gular" or f == "down": return p["b1"]
        if f in ("up", "south"): return p["k2"]
        return p["k3"]
    return sh



# ------------------------------------------------------------------ the body skin
# The house skin (drawn scales with a seam on the shaded side, belly scutes; no lone lit texel) with the
# Giganotosaurus marks: shark countershading whose border runs between whole scales and wanders slowly along the
# body; a few pale Komodo scales on the flank (whole scales, never dots); the keel of the neural arches in the dark
# top tone, cut into segments; wide rectangular scales under the tail (Concavenator) and bird scutes on the feet.
TRUNK = {"chest", "torso", "hips", "shoulders", "neck1", "neck2", "tail1", "tail2", "tail3", "tail4", "tail5",
         "thigh", "knee", "arm", "forearm", "hand", "neck_stub"}
UNDERSIDE = {"belly", "keel_low", "throat", "tail_keel"}
LEG = {"calf", "shin", "meta", "toe_mid", "toe_out", "toe_in", "hallux"}
BODY_PARTS = TRUNK | UNDERSIDE | LEG
STEP_DN = {"k5": "k4", "k4": "k3", "k3": "k2", "k2": "k1", "k1": "k0", "k0": "k0", "b2": "b1", "b1": "b0", "b0": "b0"}
# where the pale underside ends on the side of each part (fraction of its height)
UNDER = {"chest": 0.30, "torso": 0.24, "hips": 0.16, "shoulders": 0.34, "neck1": 0.36, "neck2": 0.30,
         "tail1": 0.22, "tail2": 0.26, "tail3": 0.30, "tail4": 0.34, "tail5": 0.4, "neck_stub": 0.3}
CELL = 5.0


def _line(n, z):
    """the countershade border on part n at length z: wanders slowly, a little higher over the shoulders"""
    return UNDER.get(n, 0.3) + 0.06 * math.sin(z * 0.11 + 0.7) + 0.04 * math.sin(z * 0.29 + 2.1)


def body_px(t, sex):
    p = pal_for(sex)
    c = t.cube; n = c["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    u_, w_ = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    belly = lambda uu, ww, width=6: p[{"seam": "b0", "hi": "b2", "base": "b1"}[skin.scutes(uu, ww, row=3, width=width)]]
    tailish = n.startswith("tail")
    # ---- the underside: wide scutes, wider still under the tail
    if (f == "down" and n not in LEG and n not in ("thigh", "knee", "arm", "forearm", "hand")) or n in UNDERSIDE:
        if f == "up": return p["k3"]
        if f == "down": return belly(t.L[0], t.L[2], 9 if tailish else 6)
        return belly(u_, w_, 9 if tailish else 6)
    # ---- legs: bird-like scutes across the front of the shin, the foot and the toes; small scales elsewhere
    if n in LEG:
        base = "k3" if f in ("north", "up") else "k2"
        if n in ("meta", "toe_mid", "toe_out", "toe_in", "shin") and f in ("north", "up", "east", "west"):
            k = math.floor(t.L[1] if f != "up" else t.L[2]) % 3
            if k == 0 and (t.i % 4) != 1: return p[STEP_DN[base]]
            return p[base]
        return p[STEP_DN[base]] if skin.scales(u_, w_, cell=4.0, seed=seed) == "edge" else p[base]
    if n in ("arm", "forearm", "hand"):
        base = "k3" if f != "down" else "k2"
        return p[STEP_DN[base]] if skin.scales(u_, w_, cell=3.0, seed=seed) == "edge" else p[base]
    if c["mat"] == "ridge":   # the keel: the darkest top tone, plain (a row of notches read as teeth on the Carno)
        sc = skin.scales(u_, w_, cell=CELL, seed=seed)
        base = "k2" if f == "up" else "k1"
        return p[STEP_DN[base]] if sc == "edge" else p[base]
    # ---- trunk, neck, tail, thigh: tone per whole scale, by the height of its centre
    d1, d2, cc = skin.voronoi(math.floor(u_) + 0.5, math.floor(w_) + 0.5, CELL, seed)
    if side and n in UNDER:
        vc = (cc[3] - c["from"][1]) / max(1, t.h) if f in ("east", "west") else t.rel[1]
        if vc < _line(n, cc[2] if f in ("east", "west") else t.L[2]):
            return belly(u_, w_)
    elif side:
        vc = t.rel[1]
    else:
        vc = 1.0
    if n in ("thigh", "knee"):
        base = "k3"                     # the same tone as the flank beside it: no "trousers"
        if f in ("east", "west") and t.rel[1] < 0.4 and t.rel[2] > 0.45: base = "k2"   # shade behind, low
    elif f == "up":
        base = "k2"
    else:
        base = "k4" if vc < 0.48 else ("k3" if vc < 0.78 else "k2")
        # a few pale scales on the flank, like a Komodo dragon's: whole scales, mid flank only
        if f in ("east", "west") and 0.4 < vc < 0.72 and h32(cc[0], cc[1], seed, 5) % 13 == 0 and n not in ("neck1", "neck2", "shoulders"):
            base = "k5"
    sc = skin.scales(u_, w_, cell=CELL, seed=seed)
    return p[STEP_DN[base]] if sc == "edge" else p[base]


def decals_for(sex):
    cmap = charmap(sex)
    p = pal_for(sex)

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        for (name, face), rows in FACE_ART.items():
            if name in C and face in C[name]["uv"] and C[name]["uv"][face][2] > 0:
                fill_face(img, C[name], face, rows, cmap)
        # inside the mouth: the gum rim and the dark roof, the tongue on the jaw floor
        for name, f in (("snout", "down"), ("tip", "down"), ("lacrimal", "down"), ("cranium", "down"),
                        ("jaw_front", "up"), ("jaw_mid", "up"), ("jaw_back", "up")):
            c = C[name]; u, v, ww, hh = c["uv"][f]
            for j in range(hh):
                for i in range(ww):
                    rim = i in (0, ww - 1)
                    if name.startswith("jaw"):
                        col = p["gum"] if rim else p["tongue"]
                    else:
                        col = p["gum"] if rim else p["mouth"]
                    img[v + j, u + i] = (*col, 255)
    return dec


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
