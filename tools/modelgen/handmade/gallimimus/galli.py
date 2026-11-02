"""Gallimimus bullatus, made by hand from its own study (page "Gallimimus: estudo e modelo", 02/11/2026, the second of
the six remakes of the 1.5 package). Real size 6 m, about 440 kg (Osmolska, Roniewicz & Barsbold 1972; Paul 2010).

Drawn at 32 px = 1 m (game scale 0.5), the Velociraptor's grain: the skull of a 6 m Gallimimus is only 0.33 m long
and at 24 px/m it would have 8 px for the beak, the big eye and the round braincase that gives the species its name
(bullatus: the bulb, the swollen capsule under the braincase).

What makes it itself (each point from the study, none taken from another species of the mod):
- the ostrich plan: a small round body slung between very long legs, a long thin neck held in an S, a long straight
  tail; the shin is longer than the thigh and the metatarsus is long and slender (a runner's leg);
- three toes and NO first toe (ornithomimids lost the hallux): the foot is a narrow tripod with blunt, hoof-like
  claws, not the hooked claws of a hunter;
- a toothless beak, long, low and a little spatulate at the tip; the lower jaw is shallow; a large eye high on the
  head, behind the snout, with a round pupil (a day-active plant eater, as in most birds);
- shaggy filament plumage on the body, the neck and the thigh, BARE scaly skin from the knee down (Ornithomimus,
  van der Reest et al. 2016), and a fan of longer feathers on the forearm of the adults (Zelenitsky et al. 2012):
  hidden on the young, who only had down;
- short arms for an ornithomimid, three fingers of near equal length, held folded like a bird's wing.

The colour ("grafite-azulado", its own in docs/CORES.md): blue-black above with the sheen of a black feather (the
melanosomes of Microraptor show an iridescent blue-black, Li et al. 2012: a hypothesis for this one, not a find),
slate on the flanks, chalk white under the neck and the body: the countershading of an animal of the open river
plains. The male's wing plumes black with white tips and his bare shins flushed rose (a display, as in a breeding
ostrich); the female drab cinnamon-brown, no sheen, her shins blue-grey (the ostrich's dull female sits the nest by
day, the black male by night).
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 32

# ------------------------------------------------------------------ palette (hue-shifted ramps: shadows lean violet,
# lights lean warm)
PAL_M = {
    "d0": "12141c", "d1": "1c2130", "d2": "283043", "d3": "384258", "d4": "4f5b70", "d5": "6b778a",
    "w0": "a6a39e", "w1": "c8c5bd", "w2": "dedbd2", "w3": "efede6",
    "s0": "583338", "s1": "744448", "s2": "8f5a5a", "s3": "a87270",          # bare shins: the male's rose flush
    "c0": "2c2a30", "c1": "45424a",                                         # claws (dark horn)
    "k0": "1c1a1e", "k1": "2e2b31", "k2": "57524f", "k3": "8a8177",         # beak keratin
    "wing0": "0e1018", "wing1": "1b2030", "wtip": "f1ede4", "wtip2": "cfcbc0",
}
PAL_F = dict(PAL_M)
PAL_F.update({     # the female: drab cinnamon-brown, no sheen, plain wing plumes, blue-grey shins. As on the ostrich,
    # where the dull female sits the nest by day and the black male by night (the study, "cor")
    "d0": "2a1a14", "d1": "3e2618", "d2": "563620", "d3": "6f4a2c", "d4": "8c623c", "d5": "a87c52",
    "s0": "3c3f48", "s1": "51555f", "s2": "686c76", "s3": "838790",
    "wing0": "3e2618", "wing1": "563620", "wtip": "d6c8ae", "wtip2": "b3a487",
})
EYE = {"lid": "141013", "ring": "b9b1a8", "iris": "8a4a1c", "iris2": "5e3012", "pupil": "0c0909", "glint": "f6efe0"}


def pal_for(sex):
    src = PAL_M if sex == "male" else PAL_F
    p = {k: hx(v) for k, v in src.items()}
    p.update({k: hx(v) for k, v in EYE.items()})
    return p


# ------------------------------------------------------------------ geometry
REST = {   # bone rest angles (x: positive = the far end up for the neck and the tail, knee forward for the thigh)
    "neck1": 58, "neck2": -14, "neck3": -30, "skull": -16,
    "thigh": 26, "shin": -58, "foot": 46, "toes": -14,
    "arm": 34, "forearm": -96, "hand": 38,
    "tail1": -7, "tail2": 3, "tail3": 2, "tail4": 1, "tail5": 0, "tail6": 0,
}


def _ground(m):
    import geo
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes}) if c["mat"] != "plume")
    m.shift(-lo)


def head(m, parent):
    """the skull: a round braincase (the bulla), the big eye on its front corner, a long low toothless beak with a
    slightly widened tip; the lower jaw is shallow and closes inside the upper beak's edge"""
    sk = m.bone("skull", parent, (0, 60.5, -71), (REST["skull"], 0, 0))
    m.cube(sk, (-2.5, 57, -77), (2.5, 63, -71), name="cranium")
    m.cube(sk, (-2, 58, -72), (2, 62, -70), name="occiput")
    m.cube(sk, (-1.5, 58, -82), (1.5, 61, -77), name="snout")
    m.cube(sk, (-1.5, 58, -85), (1.5, 60, -82), name="beak", mat="beak")        # the rhamphotheca, flat and wide
    m.cube(sk, (-1, 61, -80), (1, 62, -77), name="nasal")                        # the bridge, where the nostril sits
    jaw = m.bone("jaw", sk, (0, 58, -73))
    m.cube(jaw, (-1.5, 56, -77), (1.5, 58, -72), name="jaw_back")
    m.cube(jaw, (-1, 57, -84), (1, 58, -77), name="jaw_front", mat="beak")
    return sk


def neck(m, body):
    """built straight along -z and bent into the S by the rest angles: up from the shoulders, forward under the head.
    Thick with feathers at the base, thin under the head"""
    n1 = m.bone("neck1", body, (0, 60, -38), (REST["neck1"], 0, 0))
    m.cube(n1, (-4.5, 55, -50), (4.5, 65, -35), name="neck1")
    n2 = m.bone("neck2", n1, (0, 60.5, -49), (REST["neck2"], 0, 0))
    m.cube(n2, (-3.5, 57, -62), (3.5, 64, -47), name="neck2")
    n3 = m.bone("neck3", n2, (0, 60.5, -61), (REST["neck3"], 0, 0))
    m.cube(n3, (-2, 58.5, -72), (2, 62.5, -60), name="neck3")
    hd = m.bone("head", n3, (0, 60.5, -71))
    head(m, hd)


def arms(m, body):
    """short for an ornithomimid: upper arm 9 px (0.28 m), forearm 8, a hand of three near-equal fingers with
    straight claws; folded at rest like a bird's wing. The fan of longer feathers on the forearm sits on its own bone
    (adult_l / adult_r) so the young can hide it: they only had down (Zelenitsky et al. 2012)"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (7 * sx, 57, -35), (REST["arm"], 0, 0))
        fa = m.bone(f"forearm_{side}", a, (7.5 * sx, 48.5, -35), (REST["forearm"], 0, 0))
        m.bone(f"hand_{side}", fa, (7.5 * sx, 41, -35), (REST["hand"], 0, 0))
        m.bone(f"adult_{side}", fa, (7.5 * sx, 48.5, -35))
    m.pair("arm_l", "arm_r", (6, 48, -36.5), (9, 58, -33.5), name="arm")
    m.pair("forearm_l", "forearm_r", (6.5, 40, -36), (8.5, 49, -34), name="forearm")
    # the hand: palms facing in (ornithomimid hands could not turn down), so from the side the three fingers show
    # one behind the other, each with its straight claw
    m.pair("hand_l", "hand_r", (6.5, 36, -36.5), (8.5, 41, -33.5), name="hand")
    m.pair("hand_l", "hand_r", (6.5, 34, -36.5), (8.5, 36, -33.5), name="claws", mat="claw")
    # the wing fan: a cut-out plane trailing behind the forearm (the male's plumes are longer: painted, not modelled)
    m.pair("adult_l", "adult_r", (7.5, 38, -34), (7.5, 49, -27), name="wing", mat="plume")


def legs(m, body):
    """the runner's leg: a short feathered drumstick, a long bare shin (longer than the thigh), a long slender
    metatarsus and three toes with blunt claws; no first toe"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (6 * sx, 58, 0), (REST["thigh"], 0, 3 * sx))
        sh = m.bone(f"shin_{side}", th, (6.5 * sx, 38, 0), (REST["shin"], 0, -5 * sx))
        ft = m.bone(f"foot_{side}", sh, (6.5 * sx, 12, -0.5), (REST["foot"], 0, 2 * sx))
        m.bone(f"toes_{side}", ft, (6.5 * sx, -6, -0.5), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (3, 46, -6), (10, 64, 6), name="thigh")           # the drumstick, into the hip
    m.pair("thigh_l", "thigh_r", (4, 36, -4), (9, 47, 3), name="knee")             # its feathers end over the knee
    m.pair("shin_l", "shin_r", (4, 24, -3.5), (9, 38, 2.5), name="calf")
    m.pair("shin_l", "shin_r", (4.5, 11, -2.5), (8.5, 25, 1.5), name="shin")
    m.pair("foot_l", "foot_r", (5, -7, -2), (8, 13, 1), name="meta")
    m.pair("toes_l", "toes_r", (5, -9, -9), (8, -7, 0), name="toe_mid")
    m.pair("toes_l", "toes_r", (7.5, -9, -6), (9.5, -7, 0), name="toe_out", rot=(0, -14, 0), origin=(7.5, -8, 0))
    m.pair("toes_l", "toes_r", (3.5, -9, -6), (5.5, -7, 0), name="toe_in", rot=(0, 14, 0), origin=(5.5, -8, 0))
    m.pair("toes_l", "toes_r", (6, -9, -11), (7, -8, -9), name="claw_mid", mat="claw")
    m.pair("toes_l", "toes_r", (8, -9, -8), (9, -8, -6), name="claw_out", mat="claw", rot=(0, -14, 0), origin=(7.5, -8, 0))
    m.pair("toes_l", "toes_r", (4, -9, -8), (5, -8, -6), name="claw_in", mat="claw", rot=(0, 14, 0), origin=(5.5, -8, 0))


def tail(m, body):
    """long and straight, held level as a counterweight; round and feathered, thinning to a point"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 8, 28, 5, 53, 67), ("tail2", 26, 46, 4, 55, 65), ("tail3", 44, 64, 3, 56.5, 63.5),
        ("tail4", 62, 82, 2, 57.5, 62.5), ("tail5", 80, 98, 1.5, 58, 62), ("tail6", 96, 114, 1, 59, 61)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b


SADDLE_MATS = ("felt", "hide", "strap", "bone")


def saddle(m, body):
    """Its own riding pad (the study, "sela"): the rider sits over the HIPS, where the weight of a biped on long
    legs is carried (ostrich jockeys sit there too), not behind the shoulders as on the T. rex. A thin felted pad of
    hide on a wool blanket, two knee rolls, a bone grab handle in front (no stirrups: the knees grip the rolls), and a
    breast strap across the chest that keeps the pad from sliding back when it sprints. Faces lying on the body are
    left out (GeckoLib draws without back-face culling)."""
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    sd = m.bone("saddle", body, (0, 68, 0))
    m.cube(sd, (-7, 66.8, -11), (7, 67.8, 9), name="blanket", mat="felt", faces=out("down"))
    m.cube(sd, (-5, 67.8, -9), (5, 68.8, 7), name="pad", mat="hide", faces=out("down"))
    m.pair(sd, sd, (4, 68.8, -9), (6, 70.8, -5), name="knee_roll", mat="hide")
    m.cube(sd, (-4, 68.8, 4), (4, 69.8, 7), name="cantle", mat="hide")
    m.pair(sd, sd, (2, 68.8, -10), (3, 71.8, -9), name="grip_post", mat="bone")
    m.cube(sd, (-3, 71.8, -10), (3, 72.8, -9), name="grip_bar", mat="bone")
    # the girth: down each flank in front of the thighs and under the belly
    m.pair(sd, sd, (7.25, 43, -14), (8.25, 67, -12), name="girth", mat="strap", faces=out("east", "up"))
    m.cube(sd, (-6.5, 42.9, -14), (6.5, 43.9, -12), name="girth_under", mat="strap", faces=out("up"))
    # the breast strap: forward along the flank to the chest and across in front of it
    m.pair(sd, sd, (7, 58, -34), (8, 60, -14), name="breast_side", mat="strap", faces=out("east"))
    m.cube(sd, (-7, 56, -42), (7, 58, -41), name="breast", mat="strap", faces=out("south"))


def build(saddle_on=True):
    m = P.Model("gallimimus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 58, 0))
    # the trunk: short and round (a bird's), the chest the deepest part, the hips narrow and high
    m.cube(body, (-6, 46, -41), (6, 64, -29), name="chest")
    m.cube(body, (-7, 47, -30), (7, 67, -6), name="torso")
    m.cube(body, (-5, 44, -36), (5, 47, -12), name="belly", mat="belly")
    m.cube(body, (-6, 50, -7), (6, 68, 10), name="hips")
    # the shaggy fringe of the body plumage hanging over the flank's lower edge (cut-out planes)
    m.pair(body, body, (7, 42, -30), (7, 48, -6), name="fringe", mat="plume")
    neck(m, body)
    arms(m, body); legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ painting
# The rules against the "AI look" (Carnotaurus page): every mark has a cause in the animal, a short palette with
# hue-shifted ramps, borders that follow the body, one light from above, detail where the eye goes.
#
# The plumage is its own: hair-like filaments (Ornithomimus), drawn as LOCKS hanging down: 2 px wide, 4 px long,
# staggered row under row; each lock is lit at its root on the leading column and its tip falls into the shadow of
# the row below. The Velociraptor's contour feathers are short and wide (3 x 2): the two read apart.
DN = {"d5": "d4", "d4": "d3", "d3": "d2", "d2": "d1", "d1": "d0", "d0": "d0",
      "w3": "w2", "w2": "w1", "w1": "w0", "w0": "d4"}
UP = {"d0": "d1", "d1": "d2", "d2": "d3", "d3": "d4", "d4": "d5", "d5": "d5",
      "w0": "w1", "w1": "w2", "w2": "w3", "w3": "w3"}
FEATHERED = {"chest", "torso", "hips", "neck1", "neck2", "neck3", "tail1", "tail2", "tail3", "tail4", "tail5", "tail6",
             "thigh", "knee", "arm", "forearm", "cranium", "occiput"}
BARE = {"calf", "shin", "meta", "toe_mid", "toe_out", "toe_in"}
# where the chalk underside ends on each part (fraction of the face's height from the bottom); the neck is pale on its
# whole front (the throat), a ragged border
UNDER = {"chest": 0.42, "torso": 0.26, "hips": 0.14, "neck1": 0.42, "neck2": 0.5, "neck3": 0.5, "tail1": 0.18,
         "tail2": 0.22, "tail3": 0.26, "tail4": 0.3, "tail5": 0.34, "tail6": 0.4}


def lock(u, v, base, p, seed=0, length=5):
    """one texel of the hanging filament locks. u runs along the body, v up. Locks are 2 px wide and `length` long;
    each lock column has its own phase, so the tips never line up into rows (a grid of dashes read as AI). The tip of
    every other lock is a 2 px dash in the shadow of the lock below it; now and then the root catches the light"""
    c = math.floor(u / 2)
    ph = h32(c, seed, 3) % length
    k = math.floor((v + ph) / length); j = (v + ph) - k * length          # j = 0 at the lock's tip (bottom)
    hsh = h32(c, k, seed)
    if j < 1 and hsh % 2 == 0:
        return p[DN[base]]
    if j >= length - 1 and hsh % 5 == 0:
        return p[UP[base]]
    return p[base]


def _uv(t):
    if t.face in ("up", "down"): return t.L[2], t.L[0]
    return skin.face_uv_coords(t)


def body_px(t, p, sex):
    c = t.cube; n = c["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    u, v = _uv(t)
    seed = zlib.crc32(n.encode()) % 7
    rel = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    if f == "down" and n not in ("thigh", "knee", "arm", "forearm"):
        return lock(t.L[2], t.L[0], "w1", p, seed)
    if n == "belly":
        return lock(u, v, "w1", p, seed) if f != "up" else p["w1"]
    if side and n in UNDER and f in ("east", "west", "north"):
        # the dark locks hang over the chalk, each 2 px lock its own length (0 to 2 px, now and then 4), and the line
        # itself drifts slowly along the body: feathers overlap downward, so the border is ragged from above, never a comb
        col = math.floor((t.L[2] if f != "north" else t.L[0] + 8) / 2)
        drop = h32(col, seed, 9) % 3 + (2 if h32(col, seed, 11) % 6 == 0 else 0)
        line = UNDER[n] + 0.06 * math.sin(col * 0.7 + seed) + (2.5 - drop) / max(1, t.h)
        if f == "north" and n.startswith("neck"): line = 1.0          # the throat is chalk all the way up
        if rel < line:
            return lock(u, v, "w2" if rel > line * 0.45 else "w1", p, seed)
    if n in ("thigh", "knee"):
        base = "d3" if rel > 0.45 else "d4"
        if f == "north": base = "d4"
    elif n in ("arm", "forearm"):
        base = "d2" if f != "north" else "d3"
    elif f == "up":
        base = "d1" if n in ("torso", "hips", "chest", "tail1", "tail2", "neck1") else "d2"
    else:
        # the bands follow the body and wander (never a border parallel to the cube's edge), picked per lock
        zz = math.floor(t.L[2] / 2) * 2 if f in ("east", "west") else math.floor(t.L[0] / 2) * 2
        wob = 0.07 * math.sin(zz * 0.23 + seed) + 0.05 * math.sin(zz * 0.61)
        base = "d4" if rel < 0.5 + wob else ("d3" if rel < 0.8 + wob else "d2")
        if n in ("cranium", "occiput"): base = "d3"
    return lock(u, v, base, p, seed, length=3 if n in ("neck2", "neck3", "cranium", "occiput", "arm", "forearm") else 5)


def bare_px(t, p, sex):
    """the bare legs: bird scutes across the front of the shin, the metatarsus and the toes (a dark seam every 3 px),
    small round scales on the sides; light from above"""
    n = t.cube["name"]; f = t.face
    base = "s2" if f in ("north", "up") else "s1"
    if f == "down": return p["s0"]
    if f in ("north", "up") or (n in ("meta", "toe_mid", "toe_out", "toe_in") and f in ("east", "west")):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 3
        if k == 0: return p[{"s2": "s1", "s1": "s0"}[base]]
        if k == 2 and f == "north" and t.i == 0: return p["s3"]
        return p[base]
    sc = skin.scales(*skin.face_uv_coords(t), cell=2.6, seed=zlib.crc32(n.encode()) % 97)
    return p[{"s2": "s1", "s1": "s0"}[base]] if sc == "edge" else p[base]


def plume_px(t, p, sex):
    """cut-out feather planes: the wing fan (black plumes with white tips on the male, shorter brown ones on the
    female) and the shaggy fringe of the body plumage"""
    n = t.cube["name"]
    if n == "wing":
        # the fan in the forearm's frame: z runs back from the bone, y down along it. Each plume is 1 px wide and
        # lies back, the longest in the middle of the forearm
        z = t.L[2] - t.cube["from"][2]; y = t.L[1] - t.cube["from"][1]
        H = t.cube["to"][1] - t.cube["from"][1]
        s = y / H                                       # 0 at the wrist, 1 at the elbow
        reach = (5.5 + 1.5 * math.sin(math.pi * min(1, s * 1.2))) if sex == "male" else (3.5 + 1.0 * math.sin(math.pi * s))
        reach -= (0, 0.6, 0.2, 1.0, 0.4)[int(math.floor(y)) % 5]
        if z > reach: return None
        tipz = reach - z
        if tipz < 1.0: return p["wtip"] if int(math.floor(y)) % 2 == 0 else p["wtip2"]
        if tipz < 2.0 and sex == "male": return p["wing1"]
        return p["wing0"] if int(math.floor(y)) % 2 == 0 else p["wing1"]
    if n == "fringe":
        z = t.L[2]; y = t.L[1] - t.cube["from"][1]
        i = int(math.floor(z))
        top = t.cube["to"][1] - t.cube["from"][1]
        drop = (2.0, 3.4, 4.6, 3.0, 5.2, 4.0, 2.6, 4.4, 3.6)[(i + h32(i // 3, 5) % 4) % 9]
        if y < top - drop - 0.01: return None
        if y < top - drop + 1: return p["w0"]                     # the tips, in shade
        return p["w1"] if (i + h32(i, 6) % 2) % 3 else p["w2"]
    return None


def saddle_px(t, p):
    mat = t.cube["mat"]; n = t.cube["name"]; f = t.face; i, j, w, h = t.i, t.j, t.w, t.h
    S = SADDLE_PAL
    if mat == "felt":        # the wool blanket: a woven edge, a stripe near the rim
        if f == "up":
            edge = i in (0, w - 1) or j in (0, h - 1)
            return S["f2"] if edge else (S["f1"] if (i + 2 * j) % 5 else S["f0"])
        return S["f0"] if j == h - 1 else S["f3"]
    if mat == "bone":
        return S["b1"] if f == "up" else (S["b0"] if j == h - 1 and h > 1 else S["b2"])
    if mat == "strap":
        if n == "girth" and f in ("east", "west") and 2 <= j <= 3: return S["b1"] if j == 2 else S["b0"]   # bone buckle
        return S["l1"] if f in ("down",) else S["l2"]
    # hide: the pad and the rolls, lit on top, a stitched rim
    if f == "up":
        if n == "pad" and (i in (0, w - 1) or j in (0, h - 1)): return S["l1"]
        if n == "pad" and (i in (1, w - 2)) and j % 2 == 0: return S["st"]
        return S["l3"]
    if f == "down": return S["l0"]
    return S["l2"] if j < h - 1 else S["l1"]


SADDLE_PAL = {
    "l0": hx("3a2416"), "l1": hx("573722"), "l2": hx("74492b"), "l3": hx("8f5e38"), "st": hx("c9a774"),
    "f0": hx("5e3a2a"), "f1": hx("8a5236"), "f2": hx("c79a5a"), "f3": hx("70432e"),        # madder-red wool, ochre rim
    "b0": hx("a8997a"), "b1": hx("e2d8bd"), "b2": hx("c6b998"),                             # bone
}


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]
        if mat in SADDLE_MATS: return saddle_px(t, p)
        if mat == "plume": return plume_px(t, p, sex)
        if mat == "claw": return p["c0"] if t.face != "up" else p["c1"]
        if mat == "beak":
            if t.face == "up": return p["k1"]
            if t.face == "down": return p["k0"]
            return p["k2"] if t.j == t.h - 1 else p["k1"]       # the paler cutting edge along the bottom
        if mat == "mouth": return hx("6a3a3a") if t.face == "up" else hx("3c2224")
        n = t.cube["name"]
        if n in BARE: return bare_px(t, p, sex)
        if n in ("hand",): return p["s1"] if t.face != "up" else p["s2"]
        if n in ("snout", "nasal", "jaw_back"):
            # the face in front of the eye: short dense feathers going to bare skin at the beak
            if t.face == "down": return p["w1"]
            if t.face in ("east", "west") and t.rel[1] < 0.4: return p["w1"]
            return p["d3"] if t.face != "up" else p["d2"]
        return body_px(t, p, sex)
    return sh


# the head, drawn face by face: east = the animal's left (mirrored to the right), column 0 the FRONT, row 0 the TOP
FACE_ART = {
    ("cranium", "east"): [      # 6 wide x 6 tall: the big eye on the front corner (3 x 2), a round pupil with its
        "333333",               # glint, a dark lid line over it, the pale bare ring under it (as on an ostrich), the
        "2lll33",               # ear opening a dark notch behind
        "rgpi33",
        "rIiI2n",
        "3rrr33",
        "wwww33"],
    ("snout", "east"): [        # 5 x 3: the nostril high and back on the bridge; the beak's edge starts here
        "33n33",
        "33333",
        "kkkkw"],
    ("cranium", "north"): ["32223", "rr2rr", "l222l", "l222l", "w222w", "wwwww"],
}


def decals_for(sex):
    p = pal_for(sex)
    cmap = {"2": p["d2"], "3": p["d3"], "4": p["d4"], "w": p["w1"], "r": p["ring"], "l": p["lid"], "i": p["iris"],
            "I": p["iris2"], "p": p["pupil"], "g": p["glint"], "n": p["d0"], "k": p["k2"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        for (name, face), rows in FACE_ART.items():
            c = C.get(name)
            if not c or face not in c["uv"]: continue
            u, v, w, h = c["uv"][face]
            if w <= 0: continue
            assert (len(rows), len(rows[0])) == (h, w), (name, face, (w, h), (len(rows[0]), len(rows)))
            P.stamp(img, m, c, face, rows, cmap, at=(0, 0))
    return dec


def _clean(img, m):
    import qa
    qa.clean_orphans(img, m, cutout=("plume",), keep=())


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex), _clean))


def preview_faces(m):
    """for previews only: swap east/west on the cubes that drop one of them (see carno.preview_faces)"""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m
