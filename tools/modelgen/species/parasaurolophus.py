"""
Parasaurolophus walkeri  (Late Cretaceous, North America)

Reference (Wikipedia): length ~9.5 m, mass ~2.5 t, a long hollow crest
(over 1 m) curving back from the top of the skull, with internal tubes that
worked as a resonating chamber (calls); duck-like beak; walked on four legs
and could run on two; long hind legs, lighter forelimbs.

In game: scale ~0.6 -> ~6 blocks long. Males have the full-length crest
("male_display" bone adds the tip), females a shorter one.
"""
import math
from rig import Model, track, keys, add_saddle
from quadruped import hind_leg, front_leg, quad_anims

ID = "parasaurolophus"


def build():
    m = Model(ID, render_scale=1.0)
    m.palette = {
        "dorsal": "#46584c", "flank": "#748c76", "belly": "#d8d4b0",
        "limb": "#5d6c5a", "limb_top": "#6f8670",
        "claw": "#38312a", "claw_base": "#38312a",
        "beak": "#4a4038", "crest": "#b8402f", "crest_band": "#e8c27a",
        "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
        "eye": "#b8862c", "pupil": "#140f0a",
    }
    m.sexes = {"male": {"dorsal": "#3c5248", "crest": "#c0402c", "crest_band": "#f0cc7c"},
               "female": {"dorsal": "#5c5848", "flank": "#8c866a", "crest": "#7a6e5a", "crest_band": "#b9ad8e"}}
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 23, 8))
    m.box("body", (-6, 15, 2), (6, 28, 16), name="hips")
    m.box("body", (-7, 12, -12), (7, 27, 4), name="belly")
    m.box("body", (-5.5, 12, -20), (5.5, 24, -11), name="chest")
    m.box("body", (-4, 27, -10), (4, 29, 12), name="back")

    neck = m.chain(["neck1", "neck2"], "body", 0, [(21, -19), (24, -25), (25.5, -29)], "-z",
                   [(8, 8), (7, 7)], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-12 - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    m.box("skull", *R(-3.5, -3, -6, 3.5, 4, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2.5, -3, -14, 2.5, 2, -6), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -3, -16, 3, 0, -14), name="bill", tag="beak")
    co = (0, ay + 4, az - 2)
    m.box("skull", *R(-1, 3, -2, 1, 5, 8), name="crest", tag="crest", rot=(-30, 0, 0), origin=co)
    m.bone("male_display", "skull", (0, ay, az))
    m.box("male_display", *R(-1, 3, 8, 1, 5, 13), name="crest_tip", tag="crest", rot=(-30, 0, 0), origin=co)
    m.bone("jaw", "skull", (0, ay - 3, az - 3))
    m.box("jaw", *R(-2.5, -5, -15, 2.5, -3, -3), name="jaw", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3.5, ay + 1.0, az - 3.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3.5, ay + 1.0, az - 3.0), "r": 1.0, "side": -1},
    ]

    m.sym(lambda s, sx: front_leg(m, s, sx, 5, [(15, -15), (8, -14), (2, -15.5)], [(4, 5, 0.0), (3, 3, 0.0, "limb")], (4, 2, 1)))
    m.sym(lambda s, sx: hind_leg(m, s, sx, 6, [(23, 9), (13, 6), (5, 11), (2, 9)],
                                 [(7, 10, 0.0), (5, 6, 0.5, "limb"), (4, 4, 0.0, "limb")], (6, 4, 2)))
    m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, [(24, 15), (23, 26), (21.5, 37), (20, 47), (19, 55)], "+z",
            [(10, 10), (8, 8), (6, 6), (3, 3)], overlap=(1.0, 1.0))
    add_saddle(m, "body", 29, -6, 4, 8, 7, flap=6)

    def pattern(model, tx, rgb, region):
        P = tx.P
        if tx.cube.tag == "crest":
            band = math.sin((P[1] + P[2]) * 1.4)
            return tx.pal["crest_band"].copy() if band > 0.75 else rgb
        if tx.cube.tag == "skin" and region in ("dorsal", "flank"):
            st = math.sin(P[2] * 2 * math.pi / 7.0)
            if st > 0.55 and (region == "dorsal" or tx.cy > 0.55):
                rgb = rgb * 0.78
        return rgb
    m.pattern = pattern

    call = {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.35, 16, 0, 0), (1.3, 16, 0, 0), (1.6, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.35, 8, 0, 0), (1.3, 8, 0, 0), (1.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.35, 14, 0, 0), (1.3, 14, 0, 0), (1.6, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.35, -16, 0, 0), (1.25, -16, 0, 0), (1.5, 0, 0, 0)])),
    }
    quad_anims(m, 4, walk=(1.5, 20, 16, 0.6), run=(0.75, 32, 22, 1.2), attack="headbutt", sit_drop=9,
               graze_neck=-26, graze_skull=-10, extra={"call": (1.6, False, call)})
    return m
