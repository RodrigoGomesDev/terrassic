"""
Quetzalcoatlus northropi, made by hand from its own study (page "1.9: estudos do Quetzalcoatlus, do Edmontossauro e do
Dakotaraptor", approved by Rodrigo on 06/11/2026). 10 to 11 m of wingspan (Andres & Langston 2021), 200 to 250 kg,
the head as high as a giraffe's when it stands.

Drawn at 16 px = 1 m (game scale 1.0). Nothing of the Pteranodon but the plumbing of a pterosaur wing (bones, the
membrane cut in 1 px panels that fold with them): the azhdarchid is another animal and every proportion here is its own.

What makes it itself (each point from the study):
- the NECK: very long (about 3 m), tubular and stiff, carried high like a giraffe's; azhdarchid neck vertebrae barely
  bend, so the neck moves from its base and the head nods at the top;
- the HEAD: enormous, nearly as long as the neck, a straight toothless spear of a beak that is deep at the base and
  triangular in section, a low bony crest along the top (taller and coloured on the males), a small eye far back;
- a small body on LONG limbs: on the ground it walks upright on all fours, the wing finger folded back up along the
  arm, the long metacarpal standing like a stilt, the feet long and narrow (a stalker of open country, Witton &
  Naish 2008);
- the wings SHORT AND BROAD for its size (soaring over land, not the long narrow sea wings of the Pteranodon): a deep
  chord at the body running to the shin, a small propatagium in front of the arm;
- a coat of short grey pycnofibres; bare dark skin on the face round the eye and at the base of the beak.

The colour ("cinza-cegonha", docs/CORES.md): stork grey above, the throat and belly pale, the membrane slate with its
fibres marked and a dark trailing band, the beak pale grey horn with a dark tip; the male's crest and the base of his
beak a dull ochre-red, the female's crest low and grey.

Coordinates: px, x+ = left, z- = forward, y up; the rest pose stands on the feet with the wings open (the animations
fold them on the ground).
"""
import math
import zlib

import numpy as np

import proto as P
import geo
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 16

PAL_M = {
    # pycnofibres: stork grey above, lighter on the flanks, pale below
    "g0": "70726e", "g1": "8a8c88", "g2": "a4a6a2", "g3": "bebfba", "g4": "d2d2cc",
    "p0": "b4b2aa", "p1": "c8c6bd", "p2": "dbd8cf", "p3": "ebe8e0",
    # membrane, above and below
    "w0": "121519", "w1": "1c2026", "w2": "262b33", "w3": "343a43", "wv": "181c22", "we": "4c525a",
    "wu0": "585e62", "wu1": "6e7478", "wu2": "868b8e", "wuv": "60666a",
    # beak horn
    "k0": "6c6a62", "k1": "8e8c82", "k2": "aeab9f", "k3": "c8c5b8", "kt": "2a2826", "kd": "4a4640",
    # the male's crest and beak base: dull ochre-red
    "c0": "4a2418", "c1": "6e3622", "c2": "8e4a2c", "c3": "a8623a", "c4": "c08050",
    # bare face skin, legs, claws, eye
    "f0": "2a2624", "f1": "3c3634", "l0": "2e2e30", "l1": "424244", "l2": "58585a", "l3": "707070",
    "claw": "1c1a1a", "clawl": "5a5654",
    "eye": "120c0a", "ring": "b88a3a", "ring2": "7a5a26", "glint": "f2ead6",
}
PAL_F = dict(PAL_M)
PAL_F.update({   # the female: a warmer grey-brown above, the crest low and grey, no red at the beak
    "g0": "76706a", "g1": "908a82", "g2": "aaa49c", "g3": "c2bcb2", "g4": "d4cec4",
    "c0": "3e3a36", "c1": "56504a", "c2": "6e6860", "c3": "868078", "c4": "9e988e",
})


def pal_for(sex):
    return {k: hx(v) for k, v in (PAL_M if sex == "male" else PAL_F).items()}


# ------------------------------------------------------------------ wing outline (rest, left side)
WING_X0, WING_TIP = 6.0, 87.0


def lead_z(x):
    if 7.0 <= x <= 33.0:                                   # the small propatagium, shoulder to wrist
        return -8.0 - 3.0 * math.sin(math.pi * (x - 7.0) / 26.0) ** 0.8
    return -8.0 + 1.0 * max(0.0, (x - 60.0) / 27.0) ** 2


def trail_z(x):
    """a deep chord at the body (to the shin), short and broad, tapering to a blunt tip"""
    s = min(1.0, max(0.0, (x - WING_X0) / (WING_TIP - WING_X0)))
    chord = 30.0 * (1.0 - s ** 1.5) ** 0.9 + 2.0 * (1 - s)
    notch = 2.0 * math.exp(-((x - 12.0) / 5.0) ** 2)
    return -8.0 + chord - notch


PANELS = {"arm": [6, 11, 16], "forearm": [16, 21, 26, 31, 34], "hand": [34, 40, 46, 52, 54],
          "finger1": [54, 60, 66, 72, 75], "finger2": [75, 79, 83, 87]}
JOINT_X = {"arm": 6, "forearm": 16, "hand": 34, "finger1": 54, "finger2": 75}
WING_Y = 31


def build(saddle=True):
    m = P.Model("quetzalcoatlus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 30, 0))
    # a small, deep body: the keel of the flight muscles in front, narrow hips, a stub of a tail
    m.cube(body, (-5, 25, -9), (5, 33, 4), name="torso")
    m.cube(body, (-4, 22, -10), (4, 26, -2), name="keel", mat="belly", rot=(-10, 0, 0), origin=(0, 26, -2))
    m.pair(body, body, (4, 27, -10), (7, 33, -3), name="shoulder", rot=(0, 0, -8), origin=(5.5, 30, -6.5))
    m.cube(body, (-4, 24, 3), (4, 31, 9), name="hips")
    m.cube(body, (-1, 27, 8), (1, 29, 12), name="tail")
    # the neck: three long tubes, thickest at the shoulders; a short ridge of fibres on the nape
    n1 = m.bone("neck1", body, (0, 30, -9), (52, 0, 0))
    m.cube(n1, (-3, 27, -26), (3, 33, -8), name="neck1")
    m.cube(n1, (-2, 25, -24), (2, 27, -10), name="throat1", mat="belly")
    n2 = m.bone("neck2", n1, (0, 30, -25), (-4, 0, 0))
    m.cube(n2, (-2.5, 27.5, -42), (2.5, 32.5, -24), name="neck2")
    n3 = m.bone("neck3", n2, (0, 30, -41), (-4, 0, 0))
    m.cube(n3, (-2, 28, -54), (2, 32, -40), name="neck3")
    head = m.bone("head", n3, (0, 30, -53))
    skull = m.bone("skull", head, (0, 30, -53), (-38, 0, 0))
    # the skull: a tall narrow braincase far back, the beak a straight spear in three tapering parts
    m.cube(skull, (-3, 27, -62), (3, 34, -52), name="cranium")
    m.cube(skull, (-2, 28, -53), (2, 33, -50), name="occiput")
    m.cube(skull, (-2.5, 28, -84), (2.5, 33, -62), name="beak", mat="beak")
    m.cube(skull, (-1.5, 28, -98), (1.5, 32, -83), name="beak2", mat="beak")
    m.cube(skull, (-0.5, 28.1, -106), (0.5, 30.1, -97), name="beak3", mat="beak_tip")   # the tips meet with the bill shut
    jaw = m.bone("jaw", skull, (0, 28.5, -60))
    m.cube(jaw, (-2, 25, -84), (2, 28, -60), name="jaw", mat="beak")
    m.cube(jaw, (-1, 26, -98), (1, 28, -83), name="jaw2", mat="beak")
    m.cube(jaw, (-0.5, 25.9, -105), (0.5, 27.9, -97), name="jaw3", mat="beak_tip")
    m.cube(jaw, (-1.5, 24, -66), (1.5, 25, -58), name="gular", mat="belly")
    # the crest: a low bony ridge along the top of the beak and the skull; taller and coloured on the male
    cm = m.bone("male_display", skull, (0, 33, -60))
    m.cube(cm, (-0.45, 32.9, -78), (0.55, 34.9, -64), name="crest_m1", mat="crest")
    m.cube(cm, (-0.45, 33.9, -65), (0.55, 37.9, -54), name="crest_m2", mat="crest")
    cf = m.bone("female_display", skull, (0, 33, -60))
    m.cube(cf, (-0.55, 32.8, -74), (0.45, 33.8, -63), name="crest_f1", mat="crest")
    m.cube(cf, (-0.55, 33.8, -63), (0.45, 35.8, -55), name="crest_f2", mat="crest")
    # the wings
    for s, sx in (("l", 1), ("r", -1)):
        arm = m.bone(f"arm_{s}", body, (6 * sx, WING_Y, -6))
        fore = m.bone(f"forearm_{s}", arm, (16 * sx, WING_Y, -6))
        hand = m.bone(f"hand_{s}", fore, (34 * sx, WING_Y, -6))
        m.bone(f"fingers_{s}", hand, (52 * sx, WING_Y, -6))
        f1 = m.bone(f"finger1_{s}", hand, (54 * sx, WING_Y, -6))
        m.bone(f"finger2_{s}", f1, (75 * sx, WING_Y, -5.5))
        for b, piv in JOINT_X.items():
            m.bone(f"mem_{b}_{s}", f"{b}_{s}", (piv * sx, WING_Y, -6))
    m.pair("arm_l", "arm_r", (6, 28, -9), (16, 33, -3), name="humerus", mat="spar")
    m.pair("arm_l", "arm_r", (8, 26, -8.5), (13, 28, -4.5), name="crest_dp", mat="spar")
    m.pair("forearm_l", "forearm_r", (15.5, 29, -8), (32.5, 32, -4), name="forearm", mat="spar")
    m.pair("forearm_l", "forearm_r", (17, 30, -12), (19, 32, -8), name="pteroid", mat="spar", rot=(0, -20, 0), origin=(18, 31, -8))
    m.pair("hand_l", "hand_r", (32, 29, -8), (36, 33, -4), name="wrist", mat="spar")
    m.pair("hand_l", "hand_r", (35, 29, -8), (53, 32, -5), name="metacarpal", mat="spar")
    m.pair("fingers_l", "fingers_r", (50, 29, -12), (52, 31, -7), name="digit1", mat="claw", rot=(0, 18, 0), origin=(51, 30, -7))
    m.pair("fingers_l", "fingers_r", (52.2, 29, -12), (54.2, 31, -7), name="digit2", mat="claw", rot=(0, 6, 0), origin=(53, 30, -7))
    m.pair("fingers_l", "fingers_r", (54.4, 29, -11), (56.4, 31, -7), name="digit3", mat="claw", rot=(0, -8, 0), origin=(55, 30, -7))
    m.pair("finger1_l", "finger1_r", (52.5, 30, -8), (56.5, 33, -4), name="knuckle", mat="spar")
    m.pair("finger1_l", "finger1_r", (56, 30, -7), (75, 32, -5), name="phalanx1", mat="spar")
    m.pair("finger2_l", "finger2_r", (74.5, 30, -6.5), (86.5, 31, -5.5), name="phalanx2", mat="spar")
    for b, xs in PANELS.items():
        for k, (x0, x1) in enumerate(zip(xs, xs[1:])):
            zl = min(lead_z(x) for x in np.linspace(x0, x1, 12))
            tip = b == "finger2" and k == len(xs) - 2
            zt = trail_z(x0 + (x1 - x0) * (0.25 if tip else 0.5))
            z0 = math.floor(zl); z1 = max(z0 + 2, round(zt))
            m.pair(f"mem_{b}_l", f"mem_{b}_r", (x0, 30.5, z0), (x1, 31.5, z1), name=f"mem_{b}{k}", mat="mem", faces=["up", "down", "north", "south"])
    # the legs: long, a muscled thigh, a slender shin, a long narrow foot of four toes
    for s, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{s}", body, (4 * sx, 26, 6), (-10, 0, 0))
        sh = m.bone(f"shin_{s}", th, (4 * sx, 12, 6), (18, 0, 0))
        m.bone(f"foot_{s}", sh, (4 * sx, -6, 6), (-8, 0, 0))
    m.pair("thigh_l", "thigh_r", (2, 11, 3), (6, 28, 9), name="thigh")
    m.pair("shin_l", "shin_r", (2.5, -6, 4.5), (5.5, 13, 7.5), name="shin", mat="leg")
    m.pair("foot_l", "foot_r", (2, -8, 2), (6, -5, 8), name="foot", mat="leg")
    for k, x in enumerate((1.6, 2.8, 4.0, 5.2)):
        m.pair("foot_l", "foot_r", (x, -8, -1 + (k % 3 == 0) * 1.0), (x + 1, -6, 2), name=f"toe{k + 1}", mat="claw")
    if saddle:
        add_saddle(m, body)
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes}))
    m.shift(-lo)
    return m


SADDLE_MATS = ("pad", "leather", "wood", "strap")


def add_saddle(m, body):
    """Its own saddle (the study): the seat sits between the shoulders, where the flight muscles carry the weight, on a
    padded felt; a grab bar rises in front of it and two straps go round the base of the neck instead of round the
    wing roots, so the wings stay free"""
    sd = m.bone("saddle", body, (0, 33, -4))
    m.cube(sd, (-5, 32.5, -9), (5, 34.5, 2), name="pad", mat="pad")
    m.cube(sd, (-3.5, 34.5, -6), (3.5, 35.5, 1), name="seat", mat="leather")
    m.cube(sd, (-3, 35.5, 0), (3, 37.5, 2), name="cantle", mat="leather")
    m.cube(sd, (-0.5, 34.5, -9), (0.5, 40.5, -8), name="grab", mat="wood")
    m.cube(sd, (-2.5, 39.5, -9), (2.5, 40.5, -8), name="grab_bar", mat="wood")
    m.pair(sd, sd, (3.5, 26, -11), (4.5, 33, -10), name="neck_strap", mat="strap")
    m.cube(sd, (-3.5, 25, -11), (3.5, 26, -10), name="neck_strap_under", mat="strap")


# ---------------------------------------------------------------- skin
def strokes(t, dark, base, light, seed=0, dense=5):
    """short pycnofibres lying back along the body, in three tones: a stroke every few texels, offset row by row"""
    u, v = skin.face_uv_coords(t)
    i, j = math.floor(u), math.floor(v)
    if t.face in ("up", "down"):
        i, j = math.floor(t.L[0]), math.floor(t.L[2])
    stroke = math.floor((j + 2 * (i % 2)) / 2)
    if (i * 7 + stroke * 3) % dense == 0:
        return dark if h32(i, stroke, seed) % 3 else light
    return base


def membrane(t, p):
    """the wing: fibres sloping to the tip, a few soft mottles, a dark trailing band; countershaded below"""
    x = abs(t.L[0]); z = t.L[2]; f = t.face
    if f not in ("up", "down"):
        return p["w0"] if f != "north" else p["w2"]
    under = f == "down"
    c = t.cube; z1 = c["to"][2]
    d_te = z1 - z; d_le = z - c["from"][2]
    if d_te < 1.0:
        return p["wu0"] if under else (p["we"] if math.floor(x) % 6 == 3 else p["w0"])
    if d_le < 1.0: return p["wu2"] if under else p["w3"]
    fib = x * 0.5 + z * 0.9
    if math.floor(fib / 3.0) % 3 == 0 and fib % 3.0 < 1.0:
        return p["wuv"] if under else p["wv"]
    if under: return p["wu1"] if x > 30 else p["wu2"]
    if d_te < 3.0: return p["w1"]
    d1, d2, cell = skin.voronoi(math.floor(x) + 0.5, math.floor(z) + 0.5, 7.0, 41)
    if d2 - d1 < 0.7: return p["w1"]
    return p["w3"] if h32(cell[0], cell[1], 6) % 100 < 30 - 25 * min(1.0, x / 70.0) else p["w2"]


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        c = t.cube; n = c["name"]; f = t.face; v = t.rel[1]; mat = c["mat"]
        if mat == "mem": return membrane(t, p)
        if mat == "claw": return p["clawl"] if (f in ("north", "up") and t.j == 0) else p["claw"]
        if mat in SADDLE_MATS: return saddle_px(t)
        if mat in ("beak", "beak_tip"):
            along = (-t.L[2] - 62.0) / 44.0          # 0 at the base of the beak, 1 at the tip (rest coordinates)
            if mat == "beak_tip": return p["k0"] if f != "up" else p["k1"]
            if f == "down": return p["k1"]
            if along < 0.07 and sex == "male" and n in ("beak", "jaw"): return p["c2"] if f != "up" else p["c3"]
            if along < 0.06: return p["kd"]
            if f == "up": return p["k3"] if t.i == t.w // 2 else (p["k1"] if math.floor(abs(t.L[2])) % 9 == 0 else p["k2"])
            edge = (n.startswith("jaw") and t.j == 0) or (n.startswith("beak") and t.j == t.h - 1)
            if edge: return p["k0"]
            if along > 0.75: return p["k0"] if t.j == 0 else p["k1"]
            return p["k1"] if (t.j * 5 + math.floor(abs(t.L[2])) // 6) % 7 == 0 else p["k2"]
        if mat == "crest":
            if f == "up" or (f in ("east", "west") and t.j == 0): return p["c4"]
            if f == "down": return p["c0"]
            return p["c2"] if (math.floor(abs(t.L[2])) + t.j) % 4 else p["c1"]
        if mat == "spar":
            if f == "down": return p["p0"]
            if n in ("knuckle", "wrist") and f == "up": return p["g3"]
            if f == "up": return p["g2"] if (t.i // 3) % 4 else p["g3"]
            if f == "north": return p["g2"]
            return p["g1"] if t.j < t.h / 2 else p["g0"]
        if mat == "leg":
            k = math.floor(t.L[1] if f != "up" else t.L[2]) % 3
            if f in ("east", "west", "north", "south") and k == 0 and t.i % 4 != 2: return p["l1"] if t.i % 2 else p["l0"]
            if f == "up": return p["l3"] if k == 1 else p["l2"]
            return p["l1"] if k != 1 else p["l2"]
        if mat == "belly" or f == "down":
            return strokes(t, p["p0"], p["p2"], p["p3"], seed=3, dense=4)
        seed = zlib.crc32(n.encode()) % 97
        if n in ("cranium", "occiput"):
            if f in ("east", "west") and 0.25 < v < 0.75: return p["f1"] if (t.i + t.j) % 4 else p["f0"]   # bare dark face
            return strokes(t, p["g1"], p["g2"], p["g3"], seed)
        if f == "up": return strokes(t, p["g0"], p["g1"], p["g2"], seed)
        if f in ("east", "west", "north", "south"):
            line = {"torso": 0.35, "hips": 0.4, "neck1": 0.35, "neck2": 0.35, "neck3": 0.35, "thigh": 0.25,
                    "shoulder": 0.3, "tail": 0.4}.get(n, 0.5)
            if f == "north" and n.startswith("neck"): line = 1.0           # the front of the neck pale all the way
            jag = (0, 1, 1, 0, -1, -1)[math.floor(abs(t.P[2]) / 2) % 6] / max(1, t.h)
            if v + jag < line - 0.06: return strokes(t, p["p0"], p["p1"], p["p2"], seed, 4)
            if v + jag < line + 0.02: return p["g4"] if t.i % 2 else p["p0"]
            return strokes(t, p["g1"], p["g2"], p["g3"], seed) if v < 0.75 else strokes(t, p["g0"], p["g1"], p["g2"], seed)
        return p["p2"]
    return sh


def saddle_px(t):
    mat = t.cube["mat"]; f = t.face
    if mat == "leather":
        edge = t.i in (0, t.w - 1) or t.j in (0, t.h - 1)
        return hx("2e1d14") if edge else (hx("b89b6a") if (t.i + t.j) % 4 == 0 and f == "up" else hx("4a2f1f"))
    if mat == "pad":         # felt in faded madder red with an ochre rim
        if t.j in (0, t.h - 1) or t.i in (0, t.w - 1): return hx("b08a4a")
        return hx("7a3a2a") if (t.i + 2 * t.j) % 5 else hx("5e2c20")
    if mat == "wood": return hx("a4824f") if (f == "up" or t.j == 0) else hx("7a5e3e")
    return hx("2e1d14") if t.i in (0, t.w - 1) else hx("4a2f1f")


def decals_for(sex):
    p = pal_for(sex)
    pal = {"E": p["eye"], "R": p["ring"], "r": p["ring2"], "g": p["glint"], "f": p["f0"], "F": p["f1"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        # the small eye high and far back on the skull, a dark bare patch round it
        P.stamp(img, m, C["cranium"], "east", ["..ffff....",
                                               ".fFRRFf...",
                                               ".fREgRf...",
                                               ".fRErRf...",
                                               "..ffff...."], pal, at=(3, 1))
    return dec


def paint_sex(m, sex):
    return P.paint(m, shader_for(sex), [decals_for(sex)])
