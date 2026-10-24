"""
Ankylosaurus magniventris  (Late Cretaceous, North America)

Reference (Wikipedia): length 6-8 m, mass 4.8-8 t, very wide low body covered
in bony plates (osteoderms) and knobs, a short wide triangular head with horns
at the back corners, short legs, and a tail ending in a heavy bony club.

In game: scale ~0.6 -> ~4.5 blocks long, ~1.2 blocks wide... in Minecraft
terms a walking tank. Males have ochre-tipped scutes, females grey ones.
"""
import math
from rig import Model, track, keys
from quadruped import hind_leg, front_leg, quad_anims

ID = "ankylosaurus"


def build():
    m = Model(ID, render_scale=1.0)
    m.palette = {
        "dorsal": "#57503e", "flank": "#7b7056", "belly": "#b5a988",
        "limb": "#615845", "limb_top": "#6e6450",
        "claw": "#38312a", "claw_base": "#38312a",
        "armor": "#6b5f48", "scute": "#c9a05a",
        "spike_base": "#7a6a50", "spike_tip": "#ece4c8",
        "horn_base": "#7a6a50", "horn_tip": "#ece4c8",
        "club": "#8b7d62", "beak": "#3e362e",
        "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
        "eye": "#b5862c", "pupil": "#140f0a",
    }
    m.sexes = {"male": {"scute": "#d2a456", "spike_tip": "#f4ead0"},
               "female": {"scute": "#a69d88", "spike_tip": "#c9c0a8", "armor": "#625846"}}
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 13, 6))
    m.box("body", (-9, 7, -12), (9, 17, 12), name="body")
    m.box("body", (-8, 17, -10), (8, 19, 10), name="shell", tag="armor")
    for z in (-8, -4, 0, 4, 8):
        for x in (-5, -1.5, 2, 5.5):
            m.box("body", (x - 1, 19, z - 1), (x + 1, 20, z + 1), name="scute", tag="scute")
    for z in (-6, -2, 2, 6, 10):
        for sx in (1, -1):
            x0 = 9 if sx > 0 else -11
            m.box("body", (x0, 12, z - 1), (x0 + 2, 13, z + 1), name="spike", tag="spike", paint={"axis": "+x" if sx > 0 else "-x"})
    for sx in (1, -1):
        x0 = 9 if sx > 0 else -12
        m.box("body", (x0, 13, -11), (x0 + 3, 15, -9), name="shoulder_spike", tag="spike", paint={"axis": "+x" if sx > 0 else "-x"})

    neck = m.chain(["neck1", "neck2"], "body", 0, [(12, -11), (12, -14.5), (11.5, -17)], "-z",
                   [(8, 7), (7, 6)], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-6 - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    m.box("skull", *R(-5, -4, -6, 5, 2, 1), name="cranium", tag="armor", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -4, -10, 3, 0, -6), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, -4, -11, 2, -1, -10), name="beak", tag="beak")
    for sx in (1, -1):
        x = 5 * sx
        m.box("skull", (x - 1, ay + 0, az - 1), (x + 1, ay + 2, az + 1), name="horn", tag="horn",
              rot=(0, 0, -25 * sx), origin=(x, ay + 1, az), paint={"axis": "+x" if sx > 0 else "-x"})
        m.box("skull", (x - 0.5, ay - 2, az - 5), (x + 0.5, ay, az - 3), name="cheek_horn", tag="horn",
              paint={"axis": "-y"})
    m.bone("jaw", "skull", (0, ay - 4, az - 4))
    m.box("jaw", *R(-3, -6, -10, 3, -4, -2), name="jaw", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (5, ay + 0.0, az - 4.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-5, ay + 0.0, az - 4.0), "r": 1.0, "side": -1},
    ]

    m.sym(lambda s, sx: front_leg(m, s, sx, 7, [(11, -8), (5.5, -7.5), (2, -8.5)], [(5, 6, 0.0), (4, 4, 0.0, "limb")], (5, 2, 2)))
    m.sym(lambda s, sx: hind_leg(m, s, sx, 7, [(11, 9), (6, 8), (3, 9.5), (2, 9)],
                                 [(6, 7, 0.0), (5, 5, 0.5, "limb"), (4, 3, 0.0, "limb")], (5, 3, 2)))
    tail = m.chain(["tail1", "tail2", "tail3"], "body", 0, [(12, 12), (12, 22), (11.5, 32), (11, 41)], "+z",
                   [(8, 7), (5, 5), (3, 3)], overlap=(1.0, 1.0))
    t3 = tail["segments"][2]
    y0, z0 = t3["unposed"]
    L = t3["len"]
    ze = z0 + L
    m.box("tail3", (-3.5, y0 - 2, ze - 4), (3.5, y0 + 2, ze + 1), name="club", tag="club")
    m.box("tail3", (-4.5, y0 - 1.5, ze - 3), (-3.5, y0 + 1.5, ze), name="club_lobe", tag="club")
    m.box("tail3", (3.5, y0 - 1.5, ze - 3), (4.5, y0 + 1.5, ze), name="club_lobe", tag="club")
    for sx in (1, -1):
        t1 = tail["segments"][0]
        ty, tz = t1["unposed"]
        x0 = 4 if sx > 0 else -6
        m.box("tail1", (x0, ty, tz + 3), (x0 + 2, ty + 1, tz + 5), name="spike", tag="spike", paint={"axis": "+x" if sx > 0 else "-x"})

    def pattern(model, tx, rgb, region):
        P = tx.P
        tag = tx.cube.tag
        if tag in ("armor", "club"):
            cell = (math.floor(P[0] / 2) + math.floor(P[2] / 2)) % 2
            rgb = rgb * (1.08 if cell else 0.92)
            if tx.edge:
                rgb = rgb * 0.85
        return rgb
    m.pattern = pattern
    quad_anims(m, 3, knockout={"lift": 0.8}, walk=(2.0, 14, 14, 0.4), run=(1.1, 22, 22, 0.8), attack="tail", sit_drop=5,
               graze_neck=-14, graze_skull=-12, sit_kw={"hind": (30, -60, 30), "front": (-25, 60, -35)})
    return m
