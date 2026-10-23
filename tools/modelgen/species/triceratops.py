"""
Triceratops horridus  (Late Cretaceous, North America)

Reference (Wikipedia): length 8-9 m, height ~3 m (Big John), mass 6-10 t,
skull up to 2.5 m (about a third of the body), brow horns ~1 m, a single nose
horn, a short solid frill edged with epoccipitals, a parrot-like beak,
rhino-like semi-erect forelimbs, hooved hands (3 weight bearing fingers) and
four-toed feet, large polygonal feature scales up to 10 cm.

In game: scale ~0.6 -> ~5.5 blocks long, ~2 blocks tall at the frill.
"""
import math
from rig import Model, wave, sinx, track, keys
from quadruped import hind_leg, front_leg, quad_gait, quad_sit
from rig import add_saddle
from paint import vnoise, hash3

ID = "triceratops"


def build():
    m = Model(ID, render_scale=1.0)
    m.palette = {
        "dorsal": "#5a5142", "flank": "#7b6e57", "belly": "#c3b490",
        "limb": "#655a48", "limb_top": "#766a55",
        "claw": "#38312a", "claw_base": "#38312a",
        "horn_base": "#6f5d42", "horn_tip": "#efe6ca",
        "beak": "#4a4038", "frill": "#9a4e2e", "frill_edge": "#eadcbc",
        "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
        "eye": "#b88a2e", "pupil": "#140f0a",
    }
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 24, 12))
    m.box("body", (-8, 13, 6), (8, 27, 20), name="hips")
    m.box("body", (-10, 9, -8), (10, 26, 8), name="belly")
    m.box("body", (-8, 9, -17), (8, 24, -7), name="chest")
    m.box("body", (-6, 24, -14), (6, 27, -2), name="hump")
    m.box("body", (-7, 26, -4), (7, 28, 16), name="back")

    neck = m.chain(["neck1", "neck2"], "body", 0, [(20, -15), (19.5, -19), (18.5, -22)], "-z",
                   [(12, 12), (10, 11)], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-16 - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)

    m.box("skull", *R(-5, -6, -9, 5, 4, 1), name="cranium")
    m.box("skull", *R(-4, -7, -15, 4, 1, -9), name="face")
    m.box("skull", *R(-3, -8, -20, 3, -1, -15), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, -9, -23, 2, -3, -20), name="beak", tag="beak")
    # nose horn
    m.box("skull", *R(-1, -1, -19, 1, 3, -17), name="nose_horn", tag="horn", rot=(-20, 0, 0),
          origin=(0, ay - 1, az - 18), paint={"axis": "+y"})
    # brow horns: modelled pointing forward (-z), raised and splayed
    for sx in (1, -1):
        x = 3 * sx
        o = (x, ay + 3.5, az - 6)
        m.box("skull", (x - 1, ay + 2.5, az - 18), (x + 1, ay + 4.5, az - 6), name="brow_horn", tag="horn",
              rot=(30, -10 * sx, 0), origin=o, paint={"axis": "-z"})
        m.box("skull", (x - 0.5, ay + 3, az - 22), (x + 0.5, ay + 4, az - 17), name="brow_horn_tip", tag="horn",
              rot=(30, -10 * sx, 0), origin=o, paint={"axis": "-z"}, inflate=0.0)
    # frill (tilted back over the neck)
    fo = (0, ay + 2, az + 1)
    m.box("skull", (-11, ay + 2, az), (11, ay + 16, az + 2), name="frill", tag="frill", rot=(34, 0, 0), origin=fo)
    m.box("skull", (-9, ay + 16, az), (9, ay + 18, az + 2), name="frill_top", tag="frill", rot=(34, 0, 0), origin=fo)
    m.bone("jaw", "skull", (0, ay - 6, az - 7))
    m.box("jaw", *R(-3.5, -10, -21, 3.5, -7, -9), name="jaw", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-2, -10, -23, 2, -8, -21), name="lower_beak", tag="beak")
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (5, ay + 1.0, az - 6.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-5, ay + 1.0, az - 6.0), "r": 1.0, "side": -1},
    ]

    m.sym(lambda s, sx: hind_leg(m, s, sx, 7, [(21, 13), (11, 11), (4, 13), (2, 12)],
                                 [(7, 10, 0.0), (5, 6, 0.5, "limb"), (5, 5, 0.0, "limb")], (6, 4, 2)))
    m.sym(lambda s, sx: front_leg(m, s, sx, 8, [(17, -11), (9, -9.5), (2, -11.5)],
                                  [(6, 7, 0.0), (5, 5, 0.0, "limb")], (6, 3, 2)))
    m.chain(["tail1", "tail2", "tail3"], "body", 0, [(22, 19), (20, 28), (17.5, 36), (15, 43)], "+z",
            [(10, 10), (7, 7), (4, 4)], overlap=(1.0, 1.0))

    def pattern(model, tx, rgb, region):
        P = tx.P
        tag = tx.cube.tag
        if tag == "frill":
            # display frill: cream epoccipital edge, rust field, dark centre band, eye spots
            c = tx.cube
            if c.name == "frill_top" or P[0] > c.to[0] - 1.01 or P[0] < c.frm[0] + 1.01:
                ok = (int(math.floor(P[0] + 0.5)) + int(math.floor(P[1]))) % 3 != 0
                return tx.pal["frill_edge"] * (1.0 if ok else 0.85)
            if abs(P[0]) < 1.5:
                return rgb * 0.7
            spot = ((abs(P[0]) - 6.5) ** 2 + (P[1] - (c.frm[1] + 8.5)) ** 2)
            if spot < 4.5:
                return tx.pal["frill_edge"] * 0.95 if spot > 1.5 else rgb * 0.55
            return rgb
        if tag == "skin":
            n = vnoise(P[0] / 3.0, P[1] / 3.0, P[2] / 3.0, 11)
            rgb = rgb * (0.86 + 0.22 * n)
            cell = hash3(math.floor(P[0] / 3), math.floor(P[1] / 3), math.floor(P[2] / 3), 5)
            if cell > 0.93 and region != "belly":
                rgb = rgb * 1.18
        return rgb

    m.pattern = pattern
    m.sexes = {"male": {"frill": "#a8482a", "frill_edge": "#f2e4c2", "horn_tip": "#f4ecd2"},
               "female": {"frill": "#7c6248", "frill_edge": "#cbbd9b", "dorsal": "#5e5545", "flank": "#7f725c"}}
    add_saddle(m, "body", 28, -3, 7, 10, 10, flap=7)
    animations(m)
    return m


def animations(m):
    Li = 4.0
    idle = {
        "body": track(rot=wave(8, sinx(0.5), Li), pos=wave(8, lambda p: (0, 0.25 * math.sin(2 * math.pi * p), 0), Li)),
        "neck1": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * p), 2 * math.sin(2 * math.pi * (p + 0.3)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (1.5 * math.sin(2 * math.pi * (p + 0.2)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-4 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
        "tail1": track(rot=wave(8, siny_(3), Li)),
        "tail2": track(rot=wave(8, siny_(4, -0.1), Li)),
        "tail3": track(rot=wave(8, siny_(6, -0.2), Li)),
    }
    m.anim("idle", Li, True, idle)
    for name, Lc, Ah, Af, bob in (("walk", 1.8, 18, 18, 0.6), ("run", 0.9, 30, 30, 1.2)):
        t = quad_gait(Lc, Ah, Af)
        t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 1.5 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, b=bob: (0, b * math.cos(4 * math.pi * p) - b * 0.5, 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, b=bob: (-2 * b * math.cos(4 * math.pi * p), 0, 0), Lc))
        t["tail1"] = track(rot=wave(8, siny_(4, 0.25), Lc))
        t["tail2"] = track(rot=wave(8, siny_(5, 0.15), Lc))
        t["tail3"] = track(rot=wave(8, siny_(7, 0.05), Lc))
        m.anim(name, Lc, True, t)
    # attack: lower the head and thrust the horns upward
    m.anim("attack", 0.9, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, -14, 0, 0), (0.5, 12, 0, 0), (0.9, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.3, -12, 0, 0), (0.5, 14, 0, 0), (0.9, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.3, -3, 0, 0), (0.5, 3, 0, 0), (0.9, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.3, 0, -0.6, -1.5), (0.5, 0, 0.2, -3), (0.9, 0, 0, 0)])),
    })
    m.anim("sit", 4.0, True, quad_sit(m, 8))
    # graze: dip the head to the ground and chew
    jk = [(0, 0, 0, 0), (0.6, 0, 0, 0)]
    for k in range(6):
        t0 = 0.75 + k * 0.3
        jk += [(t0, -10, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(2.8, 0, 0, 0)]
    m.anim("graze", 2.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.6, -22, 0, 0), (2.3, -22, 0, 0), (2.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.6, -16, 0, 0), (2.3, -16, 0, 0), (2.8, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
    })


def siny_(a, ph=0.0):
    return lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0)
