"""
Maiasaura peeblesorum  (Late Cretaceous, Two Medicine Formation, Montana)

Reference (Wikipedia): length ~9 m, mass ~3 t; a flat-headed hadrosaur (no hollow crest) with a small solid
spiky crest in front of the eyes, a broad duck-like beak, heavy body; walked on four legs and could run on two.
Known from big nesting colonies ("Egg Mountain") with eggs, hatchlings and juveniles: the young stayed in the
nest and were fed by the adults, hence the name "good mother lizard".

Same build as the Parasaurolophus (both hadrosaurs) but heavier, with a short deep snout and the little crest.
Males have a taller crest ("male_display").
"""
import math
from rig import Model, track, keys, add_saddle
from quadruped import hind_leg, front_leg, quad_anims

ID = "maiasaura"


def build():
    m = Model(ID, render_scale=1.0)
    m.palette = {
        "dorsal": "#5a4a36", "flank": "#8c7a58", "belly": "#e0d6b6",
        "limb": "#6a5a42", "limb_top": "#7c6a4e",
        "claw": "#38312a", "claw_base": "#38312a",
        "beak": "#3e362e", "crest": "#9a5a32", "crest_band": "#d8a860", "spot": "#3e3226",
        "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
        "eye": "#b8862c", "pupil": "#140f0a",
    }
    m.sexes = {"male": {"crest": "#a8502a", "crest_band": "#e8b060"},
               "female": {"dorsal": "#62553e", "flank": "#968660", "crest": "#7c6648", "crest_band": "#b8a078"}}
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 23, 8))
    m.box("body", (-6, 15, 2), (6, 28, 16), name="hips")
    m.box("body", (-7.5, 11, -12), (7.5, 27, 4), name="belly")
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
    m.box("skull", *R(-3, -3, -12, 3, 3, -6), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3.5, -3, -14, 3.5, 0, -12), name="bill", tag="beak")
    # small solid crest just in front of the eyes
    m.box("skull", *R(-1, 3, -6, 1, 5, -2), name="crest", tag="crest")
    m.bone("male_display", "skull", (0, ay, az))
    m.box("male_display", *R(-1, 5, -5, 1, 6, -3), name="crest_tip", tag="crest")
    m.bone("jaw", "skull", (0, ay - 3, az - 3))
    m.box("jaw", *R(-3, -5, -13, 3, -3, -3), name="jaw", paint={"faces": {"up": "mouth"}})
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
            # irregular dark blotches, like a ground-nesting bird
            n = math.sin(P[2] * 0.9 + 2.0 * math.sin(P[1] * 0.7)) + math.sin(P[0] * 1.3 + P[2] * 0.4)
            if n > 1.3:
                rgb = tx.pal["spot"].copy()
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
