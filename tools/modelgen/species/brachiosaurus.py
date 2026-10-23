"""
Brachiosaurus altithorax  (Late Jurassic, North America)

Reference (Wikipedia): length ~18-22 m, height ~9-13 m with the neck raised,
mass ~30-50 t. Front legs longer than the hind legs (sloping back, high
shoulders), very long neck held up, small head with an arched nasal crest,
relatively short tail.

In game: scale ~0.4 -> ~7 blocks long and ~5.3 blocks tall at the head - the
biggest animal in the mod. Males have a red nasal crest.
"""
import math
from rig import Model, track, keys, wave, add_saddle
from quadruped import hind_leg, front_leg, quad_anims

ID = "brachiosaurus"


def build():
    m = Model(ID, render_scale=1.0)
    m.palette = {
        "dorsal": "#5a6262", "flank": "#7f8984", "belly": "#c7c2a8",
        "limb": "#646c69", "limb_top": "#727c78",
        "claw": "#3a3630", "claw_base": "#3a3630",
        "crest": "#b0483a",
        "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
        "eye": "#a8822c", "pupil": "#140f0a",
    }
    m.sexes = {"male": {"crest": "#b8442f"},
               "female": {"crest": "#7c766a", "dorsal": "#62625a", "flank": "#868a80"}}
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 34, 10))
    m.box("body", (-10, 22, -22), (10, 44, -6), name="chest")
    m.box("body", (-11, 20, -8), (11, 40, 12), name="belly")
    m.box("body", (-9, 24, 10), (9, 36, 22), name="hips")
    m.box("body", (-8, 44, -20), (8, 46, -8), name="withers")

    neck = m.chain(["neck1", "neck2", "neck3", "neck4"], "body", 0,
                   [(40, -19), (50, -25), (60, -29), (69, -32), (77, -34)], "-z",
                   [(12, 12), (10, 10), (8, 8), (7, 7)], overlap=(2.0, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck4", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-15 - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    m.box("skull", *R(-3, -3, -5, 3, 3, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, 3, -6, 2, 6, -1), name="nasal_crest", tag="crest")
    m.box("skull", *R(-2.5, -3, -10, 2.5, 1, -5), name="snout", paint={"faces": {"down": "mouth"}})
    m.bone("jaw", "skull", (0, ay - 3, az - 2))
    m.box("jaw", *R(-2, -5, -10, 2, -3, -2), name="jaw", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3, ay + 1.0, az - 3.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 1.0, az - 3.0), "r": 1.0, "side": -1},
    ]

    m.sym(lambda s, sx: front_leg(m, s, sx, 8, [(27, -15), (14, -14), (2, -15)], [(8, 9, 0.0), (7, 7, 0.0, "limb")], (8, 3, 2)))
    m.sym(lambda s, sx: hind_leg(m, s, sx, 8, [(30, 16), (16, 18), (5, 17), (2, 17)],
                                 [(9, 11, 0.0), (7, 7, 0.5, "limb"), (6, 6, 0.0, "limb")], (8, 4, 2)))
    m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, [(32, 21), (30, 33), (27, 44), (24, 54), (22, 63)], "+z",
            [(12, 12), (9, 9), (6, 6), (3, 3)], overlap=(1.0, 1.0))
    add_saddle(m, "body", 46, -18, -8, 12, 10, flap=8)

    def pattern(model, tx, rgb, region):
        P = tx.P
        if tx.cube.tag == "skin" and region in ("dorsal", "flank"):
            n = math.sin(P[2] * 0.9 + P[1] * 0.35) * math.sin(P[0] * 1.3)
            if n > 0.6:
                rgb = rgb * 0.86
        return rgb
    m.pattern = pattern

    quad_anims(m, 4, nneck=4, walk=(2.4, 14, 14, 0.6), run=(1.4, 20, 20, 1.0), attack="stomp", sit_drop=14,
               graze_neck=-8, graze_skull=-14, sit_kw={"neck": -12})
    return m
