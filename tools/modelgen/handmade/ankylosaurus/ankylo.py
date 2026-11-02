"""Ankylosaurus magniventris, made by hand from its own study (page "Anquilossauro 1.5", 02/11/2026, the fifth of the
six remakes of the 1.5 package). Real size about 7 m and 5-8 t (Arbour & Mallon 2017, from the largest specimens,
AMNH 5214 and CMN 8880).

Drawn at 24 px = 1 m (game scale 0.667), like the Triceratops and the Parasaurolophus: the skull is 65 cm long and
75 cm wide (AMNH 5214), so it gets 16 x 18 px, room for the beak, the sideways nostril, the deep eye and the horns.

What makes it itself (each point from the study, none taken from another species of the mod):
- the plan of an ankylosaurid: the widest, lowest trunk in the mod (about 1.9 m across the hips for 1.7 m of height),
  the belly slung low between the legs (magniventris, "great belly": a big hind-gut fermenter), short legs set wide,
  the hips the highest point, the shoulders lower, the head carried low in front;
- the skull WIDER than long, triangular from above; a pyramidal horn at each upper rear corner (squamosal) pointing
  back and out, a second one under it at the cheek corner (quadratojugal) pointing down and back; the roof covered in
  small polygonal head plates (caputegulae); the eye small, deep under a brow boss; the NOSTRILS FACING SIDEWAYS, an
  open hole on each side of the snout (unique to Ankylosaurus among the ankylosaurids: Arbour & Mallon 2017); a narrow
  keratin beak;
- the neck short, armoured by two bony half-rings of fused keeled plates (cervical half-rings), one behind the skull,
  one at the base;
- the back armour in transverse bands of oval keeled osteoderms (the keel runs fore and aft), small round ossicles in
  the skin between the bands; along each flank edge a row of flat triangular plates pointing out and back (on the
  adult_l / adult_r bones: the young had them barely formed, so the renderer hides them on babies);
- the tail: a flexible base, then the "handle", the stiff end of the tail where the vertebrae interlock (they bend
  only at the root, Arbour 2009), ending in the CLUB: two big lateral osteoderms and small ones over the tip. Juvenile
  ankylosaurids had no club yet (Pinacosaurus, Currie et al. 2011): the club is its own bone (adult_club, hidden on
  babies) and the young's plain tail tip another (young_tail, shown only on them);
- short legs: five short hoofed fingers on the hand, three on the foot (ankylosaurid feet).

The colour ("líquen", its own in docs/CORES.md): the soft skin a dark slate grey-green, the armour plates a pale sage
horn colour with lighter keels, the belly a pale grey: a big slow animal that looks like a weathered boulder on the
forest floor. The male's flank plates and club carry a darker umber band at their base and pale tips; the female is
plainer, her armour more grey.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 24
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# ------------------------------------------------------------------ palette
# Tried and dropped (colourcheck.py vs the remade males and females, docs/CORES.md): "liquen" (slate grey-green under
# pale sage horn: 9.4 from the Spinosaurus female), "musgo_claro" (lichen yellow-green: 7.6 from the old
# Euoplocephalus), "jade" (the same teal skin under ivory horn: read as the old model's pale plates). Kept: teal-grey skin
# under DARK horn armour, countershaded like the nodosaur Borealopelta (Brown et al. 2017), pale keels, grey-green belly.
SCHEMES = {"jade_escuro": {
    # the skin: grey-teal, deepest in the folds
    "s0": "172121", "s1": "223030", "s2": "314342", "s3": "435957", "s4": "58716d", "s5": "708a84",
    # the armour: dark horn on top, the keels catching the light
    "a0": "221f1b", "a1": "35302a", "a2": "4b4439", "a3": "645b4b", "a4": "807561", "a5": "a3987f",
    # the belly: pale grey with a green cast
    "b0": "5d6a64", "b1": "75837c", "b2": "8f9c94", "b3": "aab6ad",
    # the female: the skin a touch greyer and lighter, the horn a touch warmer
    "female": {"s2": "354441", "s3": "485a56", "s4": "5e716c", "s5": "768a84",
               "a1": "38352f", "a2": "4f4a40", "a3": "686152", "a4": "837b69", "a5": "a29a86"}}}
SCHEME = ["jade_escuro"]
PAL = {
    "beak0": "1e1b17", "beak1": "322d26", "beak2": "4a443a", "beak3": "655d4f",
    "hoof0": "2a2620", "hoof1": "433d33", "hoof2": "5f5748",
    "horn0": "4a4434", "horn1": "6c6450", "horn2": "938a6e", "horn3": "bcb291",
    "mouth": "4a2a28",
}
EYE = {"eD": "100e0c", "eY": "a86d2c", "eE": "7a4a1c", "ee": "4a2c12", "pupil": "0a0807", "glint": "eae2c8",
       "lid": "6f7461", "nost": "100f0d", "nost2": "2a2a24"}


def pal_for(sex, scheme=None):
    sc = SCHEMES[scheme or SCHEME[0]]
    p = {k: hx(v) for k, v in PAL.items()}
    p.update({k: hx(v) for k, v in sc.items() if k != "female"})
    if sex != "male":
        p.update({k: hx(v) for k, v in sc["female"].items()})
    p.update({k: hx(v) for k, v in EYE.items()})
    p["male"] = sex == "male"
    return p


# ------------------------------------------------------------------ geometry
# Model px at 24 px/m, the hip joint at z = 0, the ground at y = 0 (after _ground), the beak toward -z.
# Signs (geo.rot_matrix): +x lifts what lies in front (-z) and lowers what lies behind (+z); a hanging limb with +x
# swings its far end forward; +y turns the front to the animal's left (+x).
REST = {"neck": -6, "skull": -10,
        "thigh": 8, "shin": -14, "foot": 8, "toes": -2,
        "arm": -6, "forearm": 12, "hand": -6,
        "tail1": 4, "tail2": 1, "tail3": -1, "tail4": -1, "tail5": 0}


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes}) if c["mat"] not in SADDLE_MATS)
    m.shift(-lo)


# the raised osteoderms of the back: transverse rows (z0 of the row, the part it lies on, and the plates of the left
# half as (x centre, width, length, height)); each plate is a keeled oval drawn on a low block, the rows not evenly
# spaced and the plates not in a grid (each row has its own count and offsets, as the ribs carry them)
ROWS = [
    (-58, "withers", [(3, 4, 5, 1), (9, 4, 5, 1)]),
    (-50, "withers", [(5, 4, 6, 2), (11, 4, 5, 1)]),
    (-40, "back_top", [(2.5, 4, 5, 1), (8.5, 4, 6, 2), (13, 3, 5, 1), (18, 3, 4, 1)]),
    (-31, "back_top", [(5, 4, 5, 1), (11, 4, 6, 1), (17.5, 3, 5, 1)]),
    (-22, "back_top", [(2.5, 4, 5, 1), (8.5, 4, 5, 2), (14, 3, 5, 1), (18.5, 3, 4, 1)]),
    (-13, "back_top", [(5.5, 4, 5, 1), (12, 3, 5, 1), (17.5, 3, 5, 1)]),
    (-4, "rump_top", [(3, 4, 5, 1), (9, 4, 5, 1), (16, 3, 4, 1)]),
    (5, "rump_top", [(6, 4, 4, 1), (12, 3, 4, 1)]),
]
LIE = {"withers": (36, (-7, 0, 0), (0, 24, -49), 11), "back_top": (39, (-3, 0, 0), (0, 26, -25), 14),
       "rump_top": (41, (0, 0, 0), (0, 0, 0), 13)}
LEDGE = {"withers": 33, "back_top": 36, "rump_top": 38}


def osteoderms(m, body):
    for k, (z0, on, plates) in enumerate(ROWS):
        top, rot, org, half = LIE[on]
        for q, (xc, wd, ln, ht) in enumerate(plates):
            y0 = top if xc < half else LEDGE[on]          # on the roof, or on the ledge of the barrel beside it
            x0 = xc - wd / 2
            zz = z0 + (q % 2) * 0.5 - (k % 3 == 1) * 0.5
            m.pair(body, body, (x0, y0, zz), (x0 + wd, y0 + ht, zz + ln), name=f"od{k}_{q}", mat="armor", part="od",
                   rot=rot, origin=org, faces=OUT("down"), od=(k, q))


def head(m, parent, y, z):
    """skull, horns, beak and jaw. (y, z): the occipital joint where the neck meets the skull"""
    sk = m.bone("skull", parent, (0, y, z), (REST["skull"], 0, 0))

    def B(x0, y0, z0, x1, y1, z1):
        return (x0, y + y0, z + z0), (x1, y + y1, z + z1)
    # the braincase and the cheeks: wider than the skull is long, low
    m.cube(sk, *B(-9, -7, -11, 9, 3, 1), name="cranium")
    # the snout narrowing to the beak (the sideways nostril on each side of it)
    m.cube(sk, *B(-7, -7, -16, 7, 1, -10), name="snout", faces=OUT("south"))
    m.cube(sk, *B(-4, -8, -18, 4, -3, -15), name="beak", mat="beak", faces=OUT("south"))
    # the roof of head plates (caputegulae), overhanging the sides a little: the brow boss over each eye
    m.cube(sk, *B(-10, 3, -12, 10, 5, 1), name="roof", mat="armor", part="roof", faces=OUT("down"))
    m.cube(sk, *B(-7, 1, -17, 7, 3, -11), name="nasal_roof", mat="armor", part="roof", faces=OUT("down"))
    # the horns: pyramids of bone sheathed in horn, two steps each (a broad base, a narrower tip)
    # squamosal: at the upper rear corner, pointing back and out past the roof
    m.pair(sk, sk, *B(8, 0, -3, 13, 5, 2), name="sq_horn", mat="horn", rot=(12, -40, 0), origin=(9, y + 2, z), hseg=0)
    m.pair(sk, sk, *B(11, 1, 1, 14, 4, 6), name="sq_tip", mat="horn", rot=(12, -40, 0), origin=(9, y + 2, z), hseg=1)
    # quadratojugal: at the cheek corner under the eye, pointing down and back
    m.pair(sk, sk, *B(8, -10, -6, 12, -5, -1), name="qj_horn", mat="horn", rot=(-34, -22, 0), origin=(9, y - 6, z - 3), hseg=0)
    m.pair(sk, sk, *B(8.5, -13, -4, 11.5, -9, -1), name="qj_tip", mat="horn", rot=(-34, -22, 0), origin=(9, y - 6, z - 3), hseg=1)
    # the lower jaw: short and deep, the predentary beak at its front
    jaw = m.bone("jaw", sk, (0, y - 6, z - 4))
    m.cube(jaw, *B(-7, -10, -15, 7, -6, -2), name="dentary")
    m.cube(jaw, *B(-3, -10, -17, 3, -8, -15), name="predentary", mat="beak", faces=OUT("south"))
    m.cube(jaw, *B(-5, -7, -14, 5, -6, -3), name="mouth", mat="mouth", faces=["up"])
    return sk


def neck(m, body):
    """short and thick, the two bony half-rings over it: one at the base, one behind the skull"""
    n = m.bone("neck", body, (0, 31, -56), (REST["neck"], 0, 0))
    m.cube(n, (-11, 17, -71), (11, 35, -54), name="neck")
    m.cube(n, (-8, 15, -69), (8, 18, -56), name="throat", mat="belly", faces=OUT("up"))
    for k, (z0, z1) in enumerate(((-70, -65), (-62, -56))):
        # the half-ring: a band of fused bone over the neck (the yoke) carrying big keeled plates, three over the top
        # and one low on each side
        m.cube(n, (-11.5, 35, z0), (11.5, 36, z1), name=f"ring{k}", mat="armor", part="ring", ring=k, faces=OUT("down"))
        m.pair(n, n, (11, 24, z0), (12, 35, z1), name=f"ring{k}_side", mat="armor", part="ring", ring=k, faces=OUT("west"))
        ln = z1 - z0
        m.cube(n, (-2.5, 36, z0), (2.5, 38, z1), name=f"ring{k}_od0", mat="armor", part="od", faces=OUT("down"))
        m.pair(n, n, (4, 36, z0 + 0.5), (9, 37 + k, z0 + 0.5 + ln - 1), name=f"ring{k}_od1", mat="armor", part="od", faces=OUT("down"),
               rot=(0, 0, -14), origin=(4, 36, z0))
        m.pair(n, n, (12, 26, z0 + 0.5), (14, 32, z0 + 0.5 + ln - 1), name=f"ring{k}_od2", mat="armor", part="odside", faces=OUT("west"))
    hd = m.bone("head", n, (0, 28, -70))
    head(m, hd, 28, -70)


def hind_legs(m, body):
    """short pillars set wide under the flaring hips: a thick thigh, a short shin, a short broad foot of three toes,
    each with a blunt hoof"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (15 * sx, 27, 0), (REST["thigh"], 0, 3 * sx))
        sh = m.bone(f"shin_{side}", th, (15.5 * sx, 14, 0), (REST["shin"], 0, -3 * sx))
        ft = m.bone(f"foot_{side}", sh, (15.5 * sx, 5, -1), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (15.5 * sx, 1, -4), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (10, 13, -8), (21, 33, 8), name="thigh")
    m.pair("shin_l", "shin_r", (11, 4, -5), (20, 15, 4), name="shin")
    m.pair("foot_l", "foot_r", (11.5, 0, -5), (19.5, 6, 2), name="meta")
    m.pair("toes_l", "toes_r", (11, 0, -9), (20, 2, -4), name="pes")
    for nm, x0, z0 in (("hoof_a", 11, -10), ("hoof_b", 14.5, -11), ("hoof_c", 18, -10)):
        m.pair("toes_l", "toes_r", (x0, -1, z0), (x0 + 2, 1, z0 + 3), name=nm, mat="hoof", faces=OUT("south"))


def fore_legs(m, body):
    """shorter than the hind legs: the upper arm leaves the shoulder a little out (the elbow beside the chest), the
    forearm comes back in, the short broad hand stands on five blunt hoofed fingers"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (13 * sx, 24, -50), (REST["arm"], 0, 8 * sx))
        fa = m.bone(f"forearm_{side}", a, (14 * sx, 12, -50), (REST["forearm"], 0, -10 * sx))
        m.bone(f"hand_{side}", fa, (14 * sx, 4, -50), (REST["hand"], 0, 2 * sx))
    m.pair("arm_l", "arm_r", (9, 11, -55), (19, 29, -45), name="arm")
    m.pair("forearm_l", "forearm_r", (10, 3, -54), (18, 13, -46), name="forearm")
    m.pair("hand_l", "hand_r", (9.5, 0, -55), (18.5, 5, -46), name="hand")
    for k, (nm, x0, z0) in enumerate((("nail_a", 9, -56), ("nail_b", 10.9, -57), ("nail_c", 12.8, -57.5), ("nail_d", 14.7, -57), ("nail_e", 16.6, -56))):
        y0 = -1 + 0.13 * k * (1 if k % 2 else -1)        # each its own plane (no two bottoms in one plane)
        m.pair("hand_l", "hand_r", (x0, y0, z0), (x0 + 2, y0 + 2, z0 + 2), name=nm, mat="hoof", faces=OUT("south"))


TAIL = [  # name, z0, z1, half width, y0, y1: the flexible base (tail1, tail2), then the stiff handle (tail3-5)
    ("tail1", 12, 28, 11, 21, 36), ("tail2", 26, 40, 8, 23, 34), ("tail3", 38, 52, 5, 25, 32),
    ("tail4", 50, 63, 4, 26, 31), ("tail5", 61, 72, 3, 26, 31)]


def tail(m, body):
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(TAIL):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    # the triangular plates along the sides of the flexible base, pointing out and back
    for k, (bone, z0, y0, size) in enumerate((("tail1", 15, 30, 6), ("tail1", 22, 30, 5), ("tail2", 29, 29, 5), ("tail2", 35, 28, 4))):
        hw = {"tail1": 11, "tail2": 8}[bone]
        m.pair(bone, bone, (hw - 1, y0, z0), (hw + 3, y0 + 2, z0 + size), name=f"tspike{k}", mat="armor", part="spike",
               rot=(0, -18, -8), origin=(hw, y0 + 1, z0 + size / 2), spike=k)
    # the club: two big osteoderms at the sides wrapping the end of the handle, small ones over the top and the tip
    # (AMNH 5214: about 57 cm across, 49 cm long, 30 cm deep: wider than deep, two rounded halves)
    cl = m.bone("adult_club", parent, (0, 28.5, 70))
    m.pair(cl, cl, (2, 24, 69), (8, 33, 82), name="club_side", mat="armor", part="club")
    m.pair(cl, cl, (7, 25, 71), (9, 32, 80), name="club_round", mat="armor", part="club", faces=OUT("west"))
    m.cube(cl, (-2, 31, 70), (2, 34, 80), name="club_top", mat="armor", part="club")
    m.cube(cl, (-2, 23, 71), (2, 26, 80), name="club_under", mat="armor", part="club")
    m.cube(cl, (-3, 26, 82), (3, 31, 85), name="club_tip", mat="armor", part="club")
    yt = m.bone("young_tail", parent, (0, 28.5, 70))
    m.cube(yt, (-2, 27, 72), (2, 30, 78), name="young_tip", part="young")


def flank_plates(m, body):
    """the flat triangular plates along each flank edge, pointing out and back (adult_l / adult_r: hidden on babies)"""
    for side, sx in (("l", 1), ("r", -1)):
        m.bone(f"adult_{side}", body, (21 * sx, 31, -25))
    for k, (z0, y0, out, ln, tilt) in enumerate(((-58, 29, 5, 6, -4), (-47, 31, 6, 7, -6), (-35, 32, 6, 8, -8),
                                                 (-22, 33, 6, 8, -8), (-9, 34, 5, 7, -6), (3, 34, 4, 6, -4))):
        x0 = 17 if z0 < -50 else 20
        m.pair("adult_l", "adult_r", (x0, y0, z0), (x0 + out, y0 + 2, z0 + ln), name=f"fplate{k}", mat="armor",
               part="spike", rot=(0, -20, tilt), origin=(x0, y0 + 1, z0 + ln / 2), spike=k)


def build(sex="male", saddle_on=True):
    m = P.Model("ankylosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 30, 0))
    # the trunk: a broad low barrel, the hips the widest and highest, the back sloping down to the shoulders, the
    # belly slung low between the legs
    m.cube(body, (-19, 14, -12), (19, 38, 14), name="hips")
    m.cube(body, (-21, 12, -40), (21, 36, -10), name="torso", rot=(-3, 0, 0), origin=(0, 26, -25))
    m.cube(body, (-17, 14, -60), (17, 33, -38), name="chest", rot=(-7, 0, 0), origin=(0, 24, -49))
    m.cube(body, (-19, 9, -44), (19, 13, -6), name="belly", mat="belly")
    # the top of the barrel: the roof the bands lie on
    m.cube(body, (-13, 38, -11), (13, 41, 13), name="rump_top")
    m.cube(body, (-14, 36, -39), (14, 39, -11), name="back_top", rot=(-3, 0, 0), origin=(0, 26, -25))
    m.cube(body, (-11, 33, -59), (11, 36, -39), name="withers", rot=(-7, 0, 0), origin=(0, 24, -49))
    osteoderms(m, body)
    neck(m, body)
    flank_plates(m, body)
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ the saddle: a pack deck on the armour
SADDLE_PAL = {   # its own: peeled pale poles, bark cloth (beaten inner bark, painted in dark bands), tanned hide and
                 # twisted cord. No A-frame and baskets (the Triceratops' cangalha), no felt (the Gallimimus), no rush (the
                 # Parasaurolophus), no metal
    "W0": hx("4f4636"), "W1": hx("6f644e"), "W2": hx("8e8266"), "W3": hx("aa9e80"),     # peeled poles and slats
    "T0": hx("6d5640"), "T1": hx("8f7656"), "T2": hx("ad936f"), "T3": hx("3f2c20"),     # bark cloth and its painted band
    "H0": hx("33281f"), "H1": hx("4d3d2e"), "H2": hx("66523d"), "H3": hx("7c6549"),     # smoked hide of the bales
    "C0": hx("4e4230"), "C1": hx("706146"),                                              # twisted cord
}
SADDLE_MATS = ("pole", "cloth", "bale", "cord")


def saddle(m, body):
    """A pack deck, the kind you can put on an animal whose back is a shield: two peeled poles laid fore and aft on the
    armour, slats lashed across them behind the seat (the deck the cargo rides on), a cushion of bark cloth stuffed
    with fern at the front over the shoulders (the rider sits low, where the back is lowest, and holds a cord tied to
    the first neck ring), two hide-wrapped bales lashed on the deck (its five rows of cargo). No girth: a strap under
    that belly would chafe, and the armour gives better hold, so the deck is tied down to the flank plates on each
    side, the plates acting as cleats."""
    sd = m.bone("saddle", body, (0, 41, -24), (-3, 0, 0))
    m.pair(sd, sd, (6, 42, -48), (8, 44, 0), name="pole", mat="pole")
    for k, z0 in enumerate((-30, -24.5, -19, -13.5, -8)):          # the slats, a hand's gap between them
        m.cube(sd, (-12, 44, z0), (12, 45, z0 + 3), name=f"slat{k}", mat="pole", faces=OUT("down"), slat=k)
    m.cube(sd, (-7, 44, -47), (7, 47, -35), name="cushion", mat="cloth")
    m.cube(sd, (-6, 47, -38), (6, 49, -35), name="cantle", mat="cloth", faces=OUT("down"))
    # the hand cord: from the cushion forward to the first neck ring
    m.pair(sd, sd, (3, 44, -56), (4, 45, -47), name="hand_cord", mat="cord", faces=OUT("west", "down"))
    # the bales on the deck, each tied with two turns of cord
    m.pair(sd, sd, (1, 45, -31), (10, 51, -12), name="bale", mat="bale")
    m.pair(sd, sd, (0.5, 50.5, -27), (10.5, 51.5, -25), name="bale_tie_f", mat="cord", faces=OUT("down"))
    m.pair(sd, sd, (0.5, 50.5, -18), (10.5, 51.5, -16), name="bale_tie_b", mat="cord", faces=OUT("down"))
    # tie-downs from the deck's corners to the flank plates
    for k, z0 in enumerate((-29, -10)):
        m.pair(sd, sd, (12, 36, z0), (13, 45, z0 + 1), name=f"tie{k}", mat="cord", faces=OUT("west"),
               rot=(0, 0, -16), origin=(12, 45, z0))


def saddle_px(t):
    """light from above, the bottom edge of each piece a step darker; the bark cloth beaten in fine lines with a
    painted dark band across the cushion; the hide of the bales with its seam and folds; the cord twisted"""
    c = t.cube; mat = c["mat"]; n = c["name"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "pole":
        if f == "up": return p["W3"] if (i + j * 3 + c.get("slat", 0)) % 9 else p["W2"]     # a knot now and then
        if f == "down": return p["W0"]
        return p["W1"] if j == h - 1 and h > 1 else p["W2"]
    if mat == "cloth":
        if f == "down": return p["T0"]
        z = t.L[2]
        band = -44 <= z < -42 or -40 <= z < -39                    # the painted bands, one wide, one thin
        if band: return p["T3"]
        if f == "up": return p["T2"] if (i % 3) else p["T1"]        # the beaten fibre lines
        return p["T0"] if j == h - 1 else p["T1"]
    if mat == "bale":
        if f == "up":
            if i == 0 or i == w - 1: return p["H1"]
            return p["H3"] if (j // 4) % 2 == 0 else p["H2"]         # the folds of the wrapping
        if f == "down": return p["H0"]
        if j == 0: return p["H2"]
        if j == h - 1: return p["H0"]
        if f in ("east", "west") and abs(t.L[2] - (c["from"][2] + c["to"][2]) / 2) < 0.5: return p["H1"]   # the seam
        return p["H2"]
    if mat == "cord":
        return p["C1"] if (i + j) % 3 else p["C0"]
    return p["W2"]


# ------------------------------------------------------------------ painting
TRUNK = {"hips", "torso", "chest", "rump_top", "back_top", "withers", "neck", "tail1", "tail2", "tail3", "tail4",
         "tail5", "thigh", "arm", "young_tip"}
UNDERSIDE = {"belly", "throat"}
LEG = {"shin", "meta", "pes", "forearm", "hand"}
HEADP = {"cranium", "snout", "dentary"}
UNDER = {"chest": 0.26, "torso": 0.22, "hips": 0.2, "neck": 0.3, "tail1": 0.3, "tail2": 0.32, "tail3": 0.36,
         "tail4": 0.4, "tail5": 0.42, "cranium": 0.25, "dentary": 1.0, "young_tip": 0.4}
DN = {"s5": "s4", "s4": "s3", "s3": "s2", "s2": "s1", "s1": "s0", "s0": "s0",
      "a5": "a4", "a4": "a3", "a3": "a2", "a2": "a1", "a1": "a0", "a0": "a0",
      "b3": "b2", "b2": "b1", "b1": "b0", "b0": "b0", "u2": "u1", "u1": "u0", "u0": "u0"}
UPS = {v: k for k, v in DN.items() if k != v}
CELL = 3.4


def _belly(p, u, w):
    sc = skin.scales(u, w, cell=3.0, seed=41)
    return p["b0"] if sc == "edge" else (p["b2"] if sc == "hi" else p["b1"])


def _ossicles(p, u, w, seed, base="s3"):
    """the skin between the plates: small round ossicles, a dark seam on the lower right of each (no highlights)"""
    d1, d2, c = skin.voronoi(math.floor(u) + 0.5, math.floor(w) + 0.5, 3.4, seed)
    if d2 - d1 < 0.9 and ((math.floor(u) + 0.5) - c[2] > -0.3 or (math.floor(w) + 0.5) - c[3] < 0.3):
        return p[DN[base]]
    return p[base]


def _plate(p, x, z, xc, zc, rx, rz, keel_lit="a5"):
    """one oval keeled osteoderm seen from above, or None outside it. The keel runs fore and aft: the side of it
    toward the animal's left (+x) takes the light, the other side a step darker, the rim on the shaded side darker"""
    d = ((x - xc) / rx) ** 2 + ((z - zc) / rz) ** 2
    if d > 1.0: return None
    if abs(x - xc) < 0.5: return p[keel_lit]
    lit = x > xc
    if d > 0.62 and not lit: return p["a1"]
    return p["a3"] if lit else p["a2"]


def _row(p, x, z, z0, z1, cell, k, pad=0.45):
    """a transverse row of oval plates between z0 and z1, across x, not evenly spaced (jitter per plate)"""
    off = (h32(k, 7) % 7) / 7.0 * cell
    xi = math.floor((x + off) / cell)
    best = None
    for q in (xi - 1, xi, xi + 1):
        jx = ((h32(q, k, 1) % 100) / 100.0 - 0.5) * cell * 0.25
        xc = (q + 0.5) * cell - off + jx
        rx = cell * (0.40 + 0.08 * ((h32(q, k, 2) % 100) / 100.0))
        rz = (z1 - z0) / 2 - pad - 0.4 * ((h32(q, k, 3) % 100) / 100.0)
        col = _plate(p, x, z, xc, (z0 + z1) / 2, rx, max(1.0, rz))
        if col is not None: best = col
    return best


def body_px(t, p):
    c = t.cube; n = c["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    u_, w_ = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    if c["mat"] == "hoof":
        if f == "up": return p["hoof2"]
        return p["hoof1"] if t.j < t.h - 1 else p["hoof0"]
    if (f == "down" and n not in LEG and n not in ("thigh", "arm")) or n in UNDERSIDE:
        if f == "up": return p["s3"]
        if f == "down": return _belly(p, t.L[0], t.L[2])
        return _belly(p, u_, w_)
    if n in LEG:
        # the lower legs: thick skin of small round scales, darker toward the hoofs
        low = n in ("meta", "pes", "hand")
        base = ("s2" if low else "s3") if f in ("east", "west", "north", "up") else ("s1" if low else "s2")
        sc = skin.scales(u_, w_, cell=3.0, seed=seed)
        return p[DN[base]] if sc == "edge" else p[base]
    if f == "up":
        if n.startswith("tail") or n == "young_tip":
            # the top of the tail: oval plates scattered over it (one per cell, not in rows), the skin between
            x, z = math.floor(t.L[0]) + 0.5, math.floor(t.L[2]) + 0.5
            d1, d2, cc = skin.voronoi(x, z, 4.8, seed + 3)
            if d1 < 1.9:
                if abs(x - cc[2]) < 0.5: return p["a5"]
                return p["a3"] if x > cc[2] else p["a2"]
            return _ossicles(p, u_, w_, seed, "s2")
        return _ossicles(p, u_, w_, seed, "a1" if n in ("rump_top", "back_top", "withers") else "s2")
    vc = t.rel[1]
    if side and n in UNDER and f != "south":
        zc = t.L[2] if f in ("east", "west") else t.L[0]
        line = UNDER[n] + 0.05 * math.sin(zc * 0.21 + 0.4) + 0.035 * math.sin(zc * 0.47 + 1.9)
        if vc < line:
            return _belly(p, u_, w_)
    if n in ("rump_top", "back_top", "withers"):
        return _ossicles(p, u_, w_, seed, "a1")
    if n in HEADP:
        base = "s4" if vc > 0.55 else "s3"
        sc = skin.scales(u_, w_, cell=3.0, seed=seed)
        return p[DN[base]] if sc == "edge" else p[base]
    # flanks, neck, tail, thigh, arm: slate skin, darker low, lighter toward the armour, tone per whole scale
    d1, d2, cc = skin.voronoi(math.floor(u_) + 0.5, math.floor(w_) + 0.5, CELL, seed)
    vcc = (cc[3] - c["from"][1]) / max(1, c["to"][1] - c["from"][1]) if f in ("east", "west") else vc
    wob = 0.05 * math.sin(cc[2] * 0.17 + seed) + 0.04 * math.sin(cc[2] * 0.43)
    if n in ("thigh", "arm"):
        base = "s3" if vcc > 0.45 else "s2"
    else:
        base = "s2" if vcc < 0.48 + wob else ("s3" if vcc < 0.8 + wob else "s4")
    sc = skin.scales(u_, w_, cell=CELL, seed=seed)
    return p[DN[base]] if sc == "edge" else p[base]


def armor_px(t, p):
    """the keratin-sheathed plates. Bands and rings: a row of oval keeled osteoderms with the skin between them; the
    flank and tail plates one keeled plate each; the club a pair of big rough plates; the head roof small polygons"""
    c = t.cube; f = t.face; part = c.get("part"); n = c["name"]
    i, j, w, h = t.i, t.j, t.w, t.h
    if f == "down": return p["a0"]
    if part == "roof":
        # caputegulae: polygons, a dark seam on the lower right, a pale corner on the upper left of the bigger ones
        u_, w_ = skin.face_uv_coords(t)
        if f in ("east", "west", "north", "south"):
            return p["a1"] if t.j == t.h - 1 else p["a2"]
        d1, d2, cc = skin.voronoi(math.floor(u_) + 0.5, math.floor(w_) + 0.5, 4.6, 17 if n == "roof" else 23)
        if d2 - d1 < 0.8 and ((math.floor(u_) + 0.5) - cc[2] > 0.0 or (math.floor(w_) + 0.5) - cc[3] < 0.0): return p["a1"]
        if (math.floor(u_) + 0.5 - cc[2]) < -0.8 and (math.floor(w_) + 0.5 - cc[3]) > 0.8 and d1 < 1.6: return p["a4"]
        return p["a3"] if h32(cc[0], cc[1], 4) % 3 else p["a2"]
    if part == "odside":
        if f in ("north", "south", "up"): return p["a2"] if f != "up" else p["a3"]
        zc = (c["from"][2] + c["to"][2]) / 2; yc = (c["from"][1] + c["to"][1]) / 2
        col = _plate(p, -t.L[1] + 2 * yc, t.L[2], yc, zc, (c["to"][1] - c["from"][1]) / 2 + 0.3, (c["to"][2] - c["from"][2]) / 2 + 0.3)
        return col if col is not None else p["a1"]
    if part == "od":
        if f in ("north", "south", "east", "west"):
            return p["a2"] if j < h - 1 or h == 1 else p["a1"]
        xc = (c["from"][0] + c["to"][0]) / 2; zc = (c["from"][2] + c["to"][2]) / 2
        rx = (c["to"][0] - c["from"][0]) / 2 + 0.25; rz = (c["to"][2] - c["from"][2]) / 2 + 0.25
        x = t.L[0]
        col = _plate(p, x, t.L[2], xc, zc, rx, rz)
        return col if col is not None else p["a1"]
    if part in ("mid", "side", "ring"):
        if f in ("north", "south", "east", "west"):
            if j == 0: return p["a3"]
            if j == h - 1: return p["a1"]
            return p["a2"]
        k = c.get("band", 10 + c.get("ring", 0))
        x = t.L[0] if part != "side" else abs(t.L[0])
        cell = {"ring": 6.5}.get(part, 5.6 if k < 2 else (5.0 if k < 5 else 4.4))
        col = _row(p, x if part != "side" else x * 1.1, t.L[2], c["from"][2], c["to"][2], cell, k)
        if col is not None: return col
        return _ossicles(p, t.L[0], t.L[2], 5 + k, "s2")
    if part == "spike":
        # a flat triangular plate pointing out and back: its keel a pale line along it, the base darker
        if f in ("north", "south", "east", "west"):
            return p["a1"] if j == h - 1 else p["a2"]
        x = abs(t.L[0]); x0 = min(abs(c["from"][0]), abs(c["to"][0])); x1 = max(abs(c["from"][0]), abs(c["to"][0]))
        r = (x - x0) / max(1e-6, x1 - x0)
        zr = (t.L[2] - c["from"][2]) / max(1, c["to"][2] - c["from"][2])
        if r < 0.22: return p["a1"]
        if abs(zr - 0.5) < 0.17: return p["a5"] if r > 0.55 else p["a4"]
        return p["a3"] if zr < 0.5 else p["a2"]
    if part == "club":
        # two big rough plates: one small pit per cell (not noise), lit on top, darker low on the sides
        u_, w_ = skin.face_uv_coords(t)
        base = "a3" if f == "up" else ("a2" if t.rel[1] > 0.4 else "a1")
        if f in ("east", "west", "south", "north") and t.j == t.h - 1: return p[DN[base]]
        d1, d2, cc = skin.voronoi(math.floor(u_) + 0.5, math.floor(w_) + 0.5, 3.2, 61)
        if d2 - d1 < 0.8 and ((math.floor(u_) + 0.5) - cc[2] > -0.3): return p[DN[base]]
        if f == "up" and (math.floor(w_) + 0.5 - cc[3]) > 0.8 and d1 < 1.3: return p["a4"]
        return p[base]
    return p["a2"]


def horn_px(t, p):
    """the skull horns: horn over bone, lit on the upper face, darker toward the base, paler at the tip"""
    f = t.face; k = t.cube.get("hseg", 0)
    if f == "up": return p["horn3"] if k else p["horn2"]
    if f == "down": return p["horn0"]
    return p["horn2"] if k else (p["horn1"] if t.j < t.h - 1 else p["horn0"])


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]
        if mat in SADDLE_MATS: return saddle_px(t)
        if mat == "armor": return armor_px(t, p)
        if mat == "horn": return horn_px(t, p)
        if mat == "beak":
            if t.face == "up": return p["beak2"] if t.i % 3 else p["beak3"]
            if t.face == "down": return p["beak0"]
            if t.cube["name"] == "beak" and t.j == t.h - 1: return p["beak3"]
            return p["beak1"] if t.j > 0 else p["beak2"]
        if mat == "mouth": return p["mouth"]
        return body_px(t, p)
    return sh


def _col(u, w, i):
    """texture column of face-local column i (a face packed as a mirror of its twin runs backwards)"""
    return u + i if w > 0 else u - 1 - i


# the eye: small and deep, under the brow boss (the roof overhang is right above it); front = toward the beak
EYE_ART = ["DDDD.",
           "DYgED",
           "DEpeD",
           ".LLL."]
# the nostril: an open hole facing sideways on the snout, a plate arching over it
NOSE_ART = [".aaa.",
            "anNnA",
            ".nnn."]


def decals_for(sex):
    p = pal_for(sex)
    cmap = {"D": p["eD"], "Y": p["eY"], "E": p["eE"], "e": p["ee"], "p": p["pupil"], "g": p["glint"], "L": p["lid"],
            "n": p["nost"], "N": p["nost2"], "a": p["s5"], "A": p["s4"]}

    def put(img, cube, art, row0, col0):
        for f in ("east", "west"):
            u, v, w, h = cube["uv"][f]
            for j, row in enumerate(art):
                for k, ch in enumerate(row):
                    if ch == ".": continue
                    i = (abs(w) - 1 - col0 - k) if f == "east" else col0 + k     # counted from the front corner
                    img[v + row0 + j, _col(u, w, i)] = (*cmap[ch], 255)

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        put(img, C["cranium"], EYE_ART, 1, 2)
        put(img, C["snout"], NOSE_ART, 1, 1)
    return dec


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))


def preview_faces(m):
    """previews only, BEFORE packing: swap east/west on cubes that drop one, so the preview shows what the game shows"""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m
