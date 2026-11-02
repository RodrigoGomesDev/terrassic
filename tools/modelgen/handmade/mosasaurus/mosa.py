"""Mosasaurus hoffmannii, made by hand from its own study (page "Mosassauro 1.5", 02/11/2026, the sixth and last of the
remakes of the 1.5 package and the first animal of the sea to be remade). Shown at about 12 m: the old
17-17.6 m (Lingham-Soliar 1995, Grigoriev 2014 for the Penza jaw) rest on Russell's 1:10 jaw-to-body ratio, which was
never justified and is now taken as an overestimate (Cleary et al. 2018); the skull at about 1/7 of the body (Fanti et
al. 2014) gives the Penza animal 12 m (Gayford et al. 2024).

Drawn at 16 px per 17/12 m and shown at game scale 0.706: the skull is 31 px of the 262 px from snout to fluke (about
1/8.5, between Russell's 1/10 and the 1/7 taken from the short-bodied Prognathodon), room for the eye, the long nostril
slits, the two-part jaw and the conical teeth.

What makes it itself (each point from the study, none taken from another species of the mod or from the old model):
- a LIZARD of the sea, not a fish or a whale: a long barrel of a body on a short neck, four paddle flippers (the front
  pair bigger, swept back, the rear pair small), the trunk stiff and the work done by the tail;
- the TAIL FLUKE: the end of the spine bends DOWN into the lower lobe of a crescent fin and a soft upper lobe rises
  over it (hypocercal, like a shark turned the other way; Lindgren et al. 2013, the Prognathodon from Jordan with the
  outline of the fin preserved). The fluke is on its own bone ("fluke");
- the DOUBLE-HINGED JAW: each lower jaw bends half way along (the intramandibular joint of mosasaurs, Russell 1967), so
  the front of the jaw ("jaw_front") swings on the back half ("jaw"); with the rows of PTERYGOID TEETH in the roof of
  the mouth, the prey is walked down the throat in steps (the "ratchet"); the throat skin is its own bone ("throat");
- the head: long, deep at the back and narrowing to a short blunt rostrum in front of the first teeth (the Tylosaurus
  of the mod has the long bony ram, this one not); the eyes big and set high on the sides of the skull, under a brow;
  the NOSTRILS set far back on TOP of the snout as two long slits, so only the top of the head breaks the surface to
  breathe; big conical teeth with a ridge front and back, the upper row showing over the lower jaw;
- the skin: small keeled diamond scales, like a monitor's (the skin impressions of mosasaurs, Lindgren et al. 2010),
  never a voronoi of round scales like the dinosaurs.

The colour ("garrafa", its own in docs/CORES.md): dark pigment over the back (eumelanin found in the skin of a mosasaur,
Lindgren et al. 2014) and a pale belly, countershaded like a shark with a sharp, wavering line between the two, so from
below it vanishes against the bright surface and from above against the deep. The back is a deep bottle green: not the
blue of the old model (taken now by the Gallimimus) nor the teal-grey of the Ankylosaurus; an umber-black ("breu") was
tried first and dropped, it sat 3.4 from the Velociraptor. The male carries healed bite scars on the head (mosasaurs
fought with their jaws: Lindgren et al. 2007; Bastiaans et al. 2020), short level lines a shade lighter; the female is
plain and a touch greyer.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 16
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# ------------------------------------------------------------------ palette
SCHEMES = {"garrafa": {
    # the back: a deep bottle green, nearly black in the shadows, lightest where the light falls along the spine
    "d0": "0a1a10", "d1": "0c2816", "d2": "0e3a1f", "d3": "1a4f2f", "d4": "2f6744", "d5": "4a845d",
    # the belly: ivory, the shade a little grey
    "b0": "8c8375", "b1": "aaa08e", "b2": "c6bca6", "b3": "ddd4bf",
    # the female: the same green a touch greyer and lighter in the shadows
    "female": {"d0": "0b1a12", "d1": "0f2619", "d2": "133624", "d3": "1f4a32", "d4": "335f44", "d5": "4c7a5a"}}}
SCHEME = ["garrafa"]
PAL = {
    "tooth": "e6dcc3", "tooth2": "bdb197", "gum": "5d3a35", "mouth": "6e4440", "mouth2": "4f2e2b",
    "scar": "4f7a5e", "scar2": "35593f",
}
EYE = {"eD": "050c08", "eS": "07120b", "eY": "c49a3a", "eE": "8e6a24", "pupil": "050605", "glint": "f1ead6",
       "lid": "1f3a28", "nost": "050c08"}


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
# Model px at 16 px/m, the entity's centre at z = 0 (about the middle of the animal), the snout toward -z. The lowest
# point of the trunk sits at y = 2 (the flippers and the lower lobe of the fluke reach below it).
# Signs (geo.rot_matrix): +x lifts what lies in front (-z) and lowers what lies behind (+z); +y turns the front to the
# animal's left (+x) and the back end to its right.
REST = {"neck": 0, "skull": 0, "tail1": 0, "tail2": 1, "tail3": 1, "tail4": 2, "fluke": 14}


def head(m, parent):
    """skull, the two-part lower jaw, the teeth, the eyes' brows. The mouth line is at y = 14. The skull is big, about a
    seventh of the animal (Fanti et al. 2014, the ratio behind the 12 m): deep at the back where the jaw muscles sit,
    a tall conical snout, the lower jaw deep and straight"""
    sk = m.bone("skull", parent, (0, 17, -106), (REST["skull"], 0, 0))
    # the upper skull: deep and broad at the back (the jaw muscles), narrowing to the snout, a short blunt rostrum
    m.cube(sk, (-7, 14, -115), (7, 25, -104), name="cranium")
    m.pair(sk, sk, (7, 14, -108), (8, 20, -102), name="temporal")             # the jaw muscle bulge behind the eye
    m.pair(sk, sk, (6, 24, -119), (8, 25, -110), name="brow", faces=OUT("down"))   # the brow over the eye, 1 px proud
    m.cube(sk, (-6, 14, -124), (6, 23, -115), name="snout_back")
    m.cube(sk, (-5, 14, -131), (5, 21, -124), name="snout_mid", faces=OUT("south"))
    m.cube(sk, (-4, 14, -137), (4, 19, -131), name="snout_front", faces=OUT("south"))
    m.cube(sk, (-3, 14, -142), (3, 18, -137), name="rostrum", faces=OUT("south"))   # short: not the Tylosaurus' ram
    # the roof of the mouth with the pterygoid teeth (two short rows that show only with the jaws open)
    m.cube(sk, (-4, 13, -136), (4, 14, -108), name="palate", mat="mouth", faces=["down"])
    m.pair(sk, sk, (2, 11, -121), (2, 13, -110), name="ptery_teeth", mat="teeth")
    # the upper teeth: alpha planes hanging over the lower jaw with the mouth shut (the house style), big cones apart,
    # long enough to read from a boat (a Mosasaurus tooth crown is as long as a hand)
    m.pair(sk, sk, (4.5, 10, -141), (4.5, 14, -124), name="teeth_a", mat="teeth")
    m.pair(sk, sk, (6.25, 10, -124), (6.25, 14, -113), name="teeth_b", mat="teeth")
    # the lower jaw, back half: hinged at the quadrate behind the eye, deep (the jaw of a big Mosasaurus is a beam)
    jaw = m.bone("jaw", sk, (0, 14, -108))
    m.cube(jaw, (-6, 8, -124), (6, 14, -103), name="jaw_back")
    m.cube(jaw, (-5, 13, -123), (5, 14, -106), name="mouth_back", mat="mouth", faces=["up"])
    # the front half swings on the intramandibular joint (mosasaurs only): it can bow out and drop on its own
    jf = m.bone("jaw_front", jaw, (0, 11, -124))
    m.cube(jf, (-4, 9, -141), (4, 14, -124), name="jaw_front")
    m.cube(jf, (-3, 13, -140), (3, 14, -125), name="mouth_front", mat="mouth", faces=["up"])
    m.pair(jf, jf, (3, 14, -140), (3, 17, -126), name="teeth_lo", mat="teeth_lo")
    return sk


def neck(m, body):
    n = m.bone("neck", body, (0, 17, -88), (REST["neck"], 0, 0))
    m.cube(n, (-9, 6, -107), (9, 28, -87), name="neck")
    m.cube(n, (-7, 28, -105), (7, 29, -87), name="neck_top", faces=OUT("down"))
    # the throat skin under the jaws: its own bone, it swells when it swallows
    th = m.bone("throat", n, (0, 8, -102))
    m.cube(th, (-5, 5, -112), (5, 8, -96), name="throat", mat="belly")
    hd = m.bone("head", n, (0, 17, -106))
    head(m, hd)


def flippers(m, body):
    """four paddles, hydrofoils for steering: the front pair long and swept back, the rear pair small. Each a short
    thick root on the body and a flat blade (2 px, then 1 px at the tip), held a little below the horizontal"""
    for side, sx in (("l", 1), ("r", -1)):
        m.bone(f"flipper_f{side}", body, (11 * sx, 9, -80), (0, 0, 0))
        m.bone(f"flipper_h{side}", body, (9 * sx, 9, -24), (0, 0, 0))
    sweep_f, sweep_h = (0, -34, -10), (0, -40, -8)
    # the paddles are big: hyperphalangy (extra finger bones) made a long, broad hydrofoil of the hand
    m.pair("flipper_fl", "flipper_fr", (10, 6, -88), (16, 11, -73), name="fore_root", rot=sweep_f, origin=(11, 9, -80))
    m.pair("flipper_fl", "flipper_fr", (16, 7, -89), (30, 9, -72), name="fore_blade", mat="fin", rot=sweep_f, origin=(11, 9, -80))
    m.pair("flipper_fl", "flipper_fr", (30, 7.5, -88), (38, 8.5, -74), name="fore_mid", mat="fin", rot=sweep_f, origin=(11, 9, -80))
    m.pair("flipper_fl", "flipper_fr", (38, 7.5, -86), (43, 8.5, -77), name="fore_tip", mat="fin", rot=sweep_f, origin=(11, 9, -80))
    m.pair("flipper_hl", "flipper_hr", (8, 7, -30), (13, 10, -18), name="hind_root", rot=sweep_h, origin=(9, 9, -24))
    m.pair("flipper_hl", "flipper_hr", (13, 7.5, -30), (23, 9.5, -19), name="hind_blade", mat="fin", rot=sweep_h, origin=(9, 9, -24))
    m.pair("flipper_hl", "flipper_hr", (23, 8, -28), (28, 9, -21), name="hind_tip", mat="fin", rot=sweep_h, origin=(9, 9, -24))


TAIL = [  # name, z0, z1, half width, y0, y1 (behind the hips the tail flattens from side to side and stays deep: the
    #          tall haemal arches under it make a blade to scull with, deepest just before the bend into the fluke)
    ("tail1", 0, 30, 9, 5, 29), ("tail2", 28, 58, 6, 5, 28), ("tail3", 56, 86, 4, 5, 27), ("tail4", 84, 108, 3, 6, 25)]
KEEL = {"tail2": (2, 3), "tail3": (1.5, 2), "tail4": (1.5, 3)}   # the keel of the haemal arches under the tail: half width, y0


def tail(m, body):
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(TAIL):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + (2 if k else 0)), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        if n in KEEL:
            kw, ky = KEEL[n]
            m.cube(b, (-kw, ky, z0 + 2), (kw, y0, z1 - 1), name=n + "_keel", faces=OUT("up"))
        parent = b
    # the fluke: the spine bends down into the lower lobe (bone inside it), the soft upper lobe rises behind
    fl = m.bone("fluke", parent, (0, 16, 106), (REST["fluke"], 0, 0))
    m.cube(fl, (-2, 10, 104), (2, 21, 116), name="stock")
    # the crescent, each lobe a broad root and a narrower tip swept back: the lower (the spine runs down inside it)
    # angled down and back, the upper (soft, no bone) up and back
    lo, up = dict(rot=(-58, 0, 0), origin=(0, 12, 108)), dict(rot=(36, 0, 0), origin=(0, 20, 108))
    m.cube(fl, (-1, -10, 104), (1, 12, 117), name="lower_lobe", mat="fin", **lo)
    m.cube(fl, (-1, -18, 106), (1, -10, 114), name="lower_tip", mat="fin", **lo)
    m.cube(fl, (-1, 20, 104), (1, 37, 116), name="upper_lobe", mat="fin", **up)
    m.cube(fl, (-1, 37, 106), (1, 44, 113), name="upper_tip", mat="fin", **up)


def build(sex="male", saddle_on=True):
    m = P.Model("mosasaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 17, -40))
    # the trunk: a long barrel, deepest at the middle, the chest narrowing to the neck and the hips to the tail
    m.cube(body, (-13, 2, -64), (13, 32, -18), name="trunk")
    m.cube(body, (-14, 8, -58), (14, 27, -26), name="flank")          # the widest part, so the barrel reads round
    m.cube(body, (-11, 4, -88), (11, 30, -64), name="chest")
    m.cube(body, (-10, 5, -18), (10, 29, 2), name="hips")
    m.cube(body, (-10, 0, -60), (10, 2, -22), name="belly", mat="belly")
    m.cube(body, (-9, 32, -60), (9, 34, -24), name="back", faces=OUT("down"))
    m.cube(body, (-5, 34, -52), (5, 35, -32), name="hump", faces=OUT("down"))   # the high point of the back, over the ribs
    m.cube(body, (-8, 30, -86), (8, 31, -64), name="chest_top", faces=OUT("down"))
    m.cube(body, (-7, 29, -18), (7, 30, 0), name="hips_top", faces=OUT("down"))
    neck(m, body)
    flippers(m, body)
    tail(m, body)
    if saddle_on:
        saddle(m, body)
    return m


# ------------------------------------------------------------------ the saddle: a diving harness
SADDLE_PAL = {   # its own: dark oiled sea-hide, cord of twisted dried kelp, a float of sealed swim bladder. No wood, no
                 # basket (Triceratops), no felt (Gallimimus), no rush (Parasaurolophus), no poles and slats (Ankylosaurus)
    "H0": hx("2b2420"), "H1": hx("3d332c"), "H2": hx("52463b"), "H3": hx("67594b"),     # oiled hide pad
    "K0": hx("2e3320"), "K1": hx("454a2c"), "K2": hx("5d6039"),                         # dried-kelp cord
    "B0": hx("6e5a3a"), "B1": hx("8c7650"), "B2": hx("a69067"), "B3": hx("bfa97f"),     # the swim-bladder float
    "T0": hx("cbbf9f"),                                                                  # bone toggles
}
SADDLE_MATS = ("pad", "kelp", "float", "toggle")


def saddle(m, body):
    """A diving harness for an animal that goes under: no seat to fill with water, a pad of oiled hide moulded over the
    shoulders, a girth of twisted kelp cord round the chest behind the front flippers (the barrel holds it, nothing for
    it to slip on), a loop of cord in front of the pad to hold on to as it dives, and two floats of sealed swim bladder
    tied at the sides: the air the rider breathes when it goes under (why a rider does not drown on it)."""
    sd = m.bone("saddle", body, (0, 31, -74))
    m.cube(sd, (-9, 31, -82), (9, 33, -66), name="pad", mat="pad")
    m.cube(sd, (-6, 33, -80), (6, 34, -71), name="seat", mat="pad", faces=OUT("down"))
    m.cube(sd, (-5, 33, -71), (5, 36, -68), name="cantle", mat="pad", faces=OUT("down"))
    # the girth: round the chest, a turn of cord on each side and one under
    m.pair(sd, sd, (11, 5, -70), (12, 31, -68), name="girth", mat="kelp", faces=OUT("west"))
    m.cube(sd, (-11, 3, -70), (11, 4, -68), name="girth_under", mat="kelp", faces=OUT("up"))
    # the hand loop: two cords from the pad to a bone toggle ahead of it
    m.pair(sd, sd, (2, 33, -88), (3, 34, -82), name="hand_cord", mat="kelp", faces=OUT("west", "down"))
    m.cube(sd, (-3, 33, -90), (3, 35, -88), name="toggle", mat="toggle")
    # the floats: sealed bladders lashed on the flanks behind the pad, a cord round each
    m.pair(sd, sd, (12, 18, -80), (16, 26, -67), name="float", mat="float")
    m.pair(sd, sd, (11.5, 21, -75), (16.5, 22, -73), name="float_tie", mat="kelp", faces=OUT("down", "up"))


def saddle_px(t):
    c = t.cube; mat = c["mat"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "pad":
        if f == "down": return p["H0"]
        if f == "up":
            # the hide's grain and a stitched edge one texel in from the border
            if i == 1 or i == w - 2 or j == 1 or j == h - 2: return p["H1"] if (i + j) % 2 else p["H2"]
            return p["H3"] if (i * 7 + j * 3) % 11 == 0 else p["H2"]
        return p["H1"] if j == h - 1 else p["H2"]
    if mat == "kelp":
        return p["K2"] if (i + j) % 3 == 0 else (p["K1"] if (i + 2 * j) % 3 else p["K0"])
    if mat == "float":
        # a sealed bladder: lit on top, darker under, the creases of the dried membrane running along it
        if f == "up": return p["B3"] if i not in (0, w - 1) else p["B2"]
        if f == "down": return p["B0"]
        if j == 0: return p["B2"]
        if j >= h - 2: return p["B0"] if j == h - 1 else p["B1"]
        return p["B1"] if (t.L[2] * 2 + j) % 5 < 1 else p["B2"]
    if mat == "toggle":
        return p["T0"]
    return p["H2"]


# ------------------------------------------------------------------ painting
HEADP = {"cranium", "temporal", "brow", "snout_back", "snout_mid", "snout_front", "rostrum"}
JAW = {"jaw_back", "jaw_front"}
ROOTS = {"fore_root", "hind_root"}
DN = {"d5": "d4", "d4": "d3", "d3": "d2", "d2": "d1", "d1": "d0", "d0": "d0", "b3": "b2", "b2": "b1", "b1": "b0", "b0": "b0"}
CELL = 4.0


def line_y(z):
    """the countershading line in model px (rest pose), along the body: just under the middle of the flank, dipping
    behind the flippers and rising toward the tail, wandering slowly (never a straight band along a cube edge)"""
    base = 13.0 if z < 0 else 13.0 - 0.02 * z
    if z < -100: base = 14.5                                   # on the head: the line is the mouth
    return base + 1.7 * math.sin(z * 0.061 + 0.6) + 0.9 * math.sin(z * 0.17 + 1.3) + 0.5 * math.sin(z * 0.43 + 2.1)


def scales(u, v, cell=CELL, seed=0):
    """keeled diamond scales, overlapping backward like a monitor's: a lattice turned 45 degrees whose dark seam is
    drawn only on the rear-lower edge of each scale, in short dashes (never a full grid). Returns ('seam' | 'base',
    cell id); the tone is chosen per whole scale by the caller."""
    uc, vc = math.floor(u) + 0.5, math.floor(v) + 0.5
    a, b = (uc + vc) / cell, (uc - vc) / cell
    ia, ib = math.floor(a), math.floor(b)
    fa, fb = a - ia, b - ib
    if fa < 1.0 / cell and fb > 0.35:
        return "seam", (ia, ib)
    return "base", (ia, ib)


def _cell_centre(cid, cell):
    ia, ib = cid
    a, b = (ia + 0.5) * cell, (ib + 0.5) * cell
    return (a + b) / 2, (a - b) / 2


def dark_px(p, kind, cid, seed, tone):
    if h32(cid[0], cid[1], seed) % 11 == 0:
        tone = DN[tone]                 # the odd darker scale, never in a pattern, never a pale dot
    return p[DN[tone]] if kind == "seam" else p[tone]


def belly_px(p, u_, w_, seed):
    """the belly scales: the same overlap as the back but soft, the tone chosen per scale and the seam only one step
    darker than the scale it edges, missing on some (a pale belly shows its scales only in the light)"""
    kind, cid = scales(u_, w_, CELL + 1.0, seed + 5)
    h = h32(cid[0], cid[1], seed + 9)
    tone = "b3" if h % 5 == 0 else ("b1" if h % 13 == 0 else "b2")
    if kind == "seam" and (h >> 4) % 3:
        return p[{"b3": "b2", "b2": "b1", "b1": "b0"}[tone]]
    return p[tone]


# the male's healed bite scars: where a rival's jaws raked the head (mosasaurs fought with their jaws: Lindgren et al.
# 2007; Bastiaans et al. 2020). Three parallel gouges across the side of the snout and two along the lower jaw, each a
# short line slanting back and down (the tooth was dragged back), in fixed places
SCARS = {"snout_back": [(-121, 19), (-121, 17)], "jaw_back": [(-116, 12)]}


def scar_at(t, p):
    if not p["male"] or t.face not in ("east", "west"): return None
    z = math.floor(t.L[2]); y = math.floor(t.L[1])
    for z0, y0 in SCARS.get(t.cube["name"], ()):
        # a short line raked back: three texels level, the fourth a step down (where the tooth left the skin)
        if (z0 <= z <= z0 + 2 and y == y0) or (z == z0 + 3 and y == y0 - 1):
            return p["scar"] if z <= z0 + 2 else p["scar2"]
    return None


# the pattern (its own, a hypothesis like every colour of an extinct animal): broken dark bands across the back, made of
# whole scales, like the bands of a young monitor or a tiger shark's bars: they break the long outline seen from the
# side and from above, which is what countershading alone cannot do for an animal that hunts from below. On the male
# the bands run down to the countershading line; on the female they break into two rows of blotches. Behind the eye a
# dark stripe runs back over the jaw muscles to the neck with a pale line under it (the postocular stripe of the
# monitors, its nearest living kin).
def _bars():
    out, z, i = [], -98.0, 0
    while z < 100:
        w = 4 + h32(i, 61) % 3
        out.append((z, z + w, i))
        z += w + 9 + h32(i, 62) % 7; i += 1
    return out


BARS = _bars()


def bar_at(z, y, ly, cid, p):
    """'' outside a band, else 'bar' (the dark band) for this pixel; the edge is ragged by whole scales"""
    zz = z + (h32(cid[0], cid[1], 63) % 3 - 1)
    for z0, z1, i in BARS:
        if z0 <= zz < z1:
            # the tail end fades: the last bands stop higher up the flank
            fade = max(0.0, (z - 40) * 0.06)
            low = ly + 3 + fade + (h32(i, 64) % 3)
            if y < low: return ""
            if not p["male"]:
                # the female's band breaks into two blotches: a gap across the middle of the flank
                mid = (low + 30) / 2 + (h32(i, 65) % 3 - 1)
                if abs(y - mid) < 1.6: return ""
            return "bar"
    return ""


def stripe_at(n, f, z, y):
    """the postocular stripe: 'dark', 'pale' or ''"""
    if n not in ("cranium", "temporal", "neck") or f not in ("east", "west") or not (-109.5 < z < -93):
        return ""
    sy = 20.5 - 0.06 * (z + 109)
    if sy - 1 <= y < sy + 1: return "dark"
    if sy - 2 <= y < sy - 1: return "pale"
    return ""


def body_px(t, p):
    c = t.cube; n = c["name"]; f = t.face
    u_, w_ = skin.face_uv_coords(t)
    seed = zlib.crc32(n.encode()) % 97
    if c["mat"] == "belly" or n == "throat":
        if f == "up": return p["d1"]
        return belly_px(p, u_, w_, seed)
    sc = scar_at(t, p)
    if sc is not None: return sc
    if f == "down":
        return belly_px(p, t.L[0], t.L[2], seed)
    cell = 3.0 if (n in HEADP or n in JAW) else CELL
    kind, cid = scales(u_, w_, cell, seed)
    if f == "up":
        # the top: the spine's line a step lighter where the light falls, the rest dark
        if n not in HEADP and n not in JAW and bar_at(t.L[2], 99, 0, cid, p):
            return dark_px(p, kind, cid, seed, "d0" if p["male"] or abs(t.L[0]) > 2 else "d1")
        return dark_px(p, kind, cid, seed, "d2")
    y = t.L[1]; z = t.L[2] if f in ("east", "west") else (c["from"][2] if f == "north" else c["to"][2])
    if n in JAW:
        # the lower jaw: the scaly lip dark along the top (the upper teeth hang against it), pale below
        if y > 11: return p["d1"] if y > 13 else dark_px(p, kind, cid, seed, "d2")
        return belly_px(p, u_, w_, seed)
    ly = line_y(z)
    st = stripe_at(n, f, z, y)
    if st: return p["d0"] if st == "dark" else p["d4"]
    # the line is drawn per pixel, sharp like a shark's, and wanders slowly with the body (scales cross it)
    if y < ly:
        return belly_px(p, u_, w_, seed) if f in ("east", "west") else p["b1"]
    if y < ly + 1.0:
        return dark_px(p, kind, cid, seed, "d4")       # the edge row: a step lighter, the line soft but sharp
    if f in ("north", "south"):
        return dark_px(p, kind, cid, seed, "d1")
    if n not in HEADP and bar_at(z, y, ly, cid, p):
        return dark_px(p, kind, cid, seed, "d1")
    return dark_px(p, kind, cid, seed, "d3")


def fin_px(t, p):
    """the flippers and the fluke: dark on top, pale under (countershaded), the edge that leads a step darker, the
    trailing edge a step lighter; on the paddles one faint line where the long fingers lie under the skin"""
    c = t.cube; n = c["name"]; f = t.face
    if n in ("lower_lobe", "lower_tip", "upper_lobe", "upper_tip"):
        if f == "north": return p["d0"]
        if f == "south": return p["d2"]
        zr = t.rel[2]
        if zr > 0.75: return p["d4"]                         # the thin trailing edge, pale
        if n == "lower_lobe" and zr < 0.3: return p["d2"]    # the spine inside the lower lobe
        return p["d1"]
    if f == "down": return p["b1"] if t.rel[0] < 0.85 else p["b0"]
    if f == "up":
        zr = t.rel[2]
        if zr < 0.2: return p["d0"]                          # the leading edge
        if zr > 0.8: return p["d4"]                          # the trailing edge, pale (it shows the paddle's shape)
        if n in ("fore_blade", "fore_mid") and t.j in (t.h // 3, 2 * t.h // 3): return p["d1"]   # the long fingers
        return p["d2"]
    return p["d1"]


def teeth_px(t, p):
    """big cones apart, the house style (hanging over the lower jaw with the mouth shut): a dark lip edge on top, a
    broad base, a narrow point; the odd one shorter (a new tooth coming in), never in a pattern"""
    c = t.cube; f = t.face; mat = c["mat"]
    if f not in ("east", "west"): return None
    col = int(math.floor(t.L[2])); row = t.j
    if c["name"] == "ptery_teeth":
        k = (col + 400) % 3
        if row == 0: return p["mouth2"]
        return p["tooth2"] if (row == 1 and k) or k == 1 else None
    if mat == "teeth":
        k, short = _tooth_at(col, 31)
        if row == 0: return p["d0"]
        if row in (1, 2): return (p["tooth"] if k == 0 else p["tooth2"]) if k in (0, 1) and not (short and row == 2 and k == 1) else None
        if row == 3: return p["tooth"] if k == 0 and not short else None
        return None
    k, short = _tooth_at(col, 47)
    if row == t.h - 1: return p["gum"]
    if row == t.h - 2: return (p["tooth"] if k == 0 else p["tooth2"]) if k in (0, 1) else None
    if row == t.h - 3: return p["tooth"] if k == 0 and not short else None
    return None


def _tooth_at(col, seed):
    """where the teeth stand along a row: one every 3 to 5 texels, the gap chosen per tooth (teeth are shed and
    replaced one by one, so the row is never even); returns (texel inside the tooth or -1, whether it is a short new
    one)"""
    s, i = -140, 0
    while s <= col:
        if col - s < 2:
            return col - s, h32(i, seed + 1) % 5 == 0
        s += 3 + h32(i, seed) % 3; i += 1
    return -1, False


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]
        if mat in SADDLE_MATS: return saddle_px(t)
        if mat in ("teeth", "teeth_lo"): return teeth_px(t, p)
        if mat == "fin": return fin_px(t, p)
        if mat == "mouth": return p["mouth"] if t.face != "down" else p["mouth2"]
        if t.cube["name"] in ROOTS: return fin_px(t, p) if t.face in ("up", "down") else p["d1"]
        return body_px(t, p)
    return sh


def _col(u, w, i):
    return u + i if w > 0 else u - 1 - i


# the eye: big, high on the side of the skull, a dark socket round it, the gold iris, the pupil a round black (an
# animal of the dim water), the glint on top; the brow over it is its own cube. front = toward the snout
EYE_ART = [".SSSS.",
           "SYgYED",
           "SYppED",
           "SEppeD",
           ".LLLD."]


def decals_for(sex):
    p = pal_for(sex)
    cmap = {"D": p["eD"], "S": p["eS"], "Y": p["eY"], "E": p["eE"], "e": p["eE"], "p": p["pupil"], "g": p["glint"],
            "L": p["lid"], "n": p["nost"]}

    def put(img, cube, art, row0, col0):
        for f in ("east", "west"):
            u, v, w, h = cube["uv"][f]
            for j, row in enumerate(art):
                for k, ch in enumerate(row):
                    if ch == ".": continue
                    i = (abs(w) - 1 - col0 - k) if f == "east" else col0 + k
                    img[v + row0 + j, _col(u, w, i)] = (*cmap[ch], 255)

    def nostrils(img, cube):
        # two long slits on top of the snout, set far back (the nares of a mosasaur start over the 4th tooth)
        u, v, w, h = cube["uv"]["up"]
        for row in range(1, h - 1):
            for x in (w // 2 - 2, w // 2 + 1):
                img[v + row, u + x] = (*p["nost"], 255)

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        put(img, C["cranium"], EYE_ART, 2, 1)
        nostrils(img, C["snout_back"])
    return dec


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))


def preview_faces(m):
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m
