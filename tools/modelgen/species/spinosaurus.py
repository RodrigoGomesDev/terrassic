"""
Spinosaurus aegyptiacus  (Cretaceous, North Africa)

Reference (Wikipedia): length ~14 m (one of the longest theropods), a sail on
the back up to ~1.65 m tall made of elongated neural spines, a long narrow
crocodile-like snout with conical teeth and a rosette at the tip, relatively
short hind legs, strong arms with big thumb claws, and a deep paddle-like tail
(2020 finding) for swimming. A semi-aquatic fish eater.

In game: scale ~0.5 -> ~7.5 blocks long, sail top ~2.9 blocks.
Males have a taller, red-orange sail ("male_display" bone); females a duller one.
"""
import math
from rig import Model, track, keys, sit_tracks
import tyrannosaurus as trex

ID = "spinosaurus"


def build():
    m = Model(ID, render_scale=1.0)
    m.palette = {
        "dorsal": "#464a42", "flank": "#6b6f60", "belly": "#d0c8a8",
        "limb": "#55584c", "limb_top": "#66695a",
        "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a",
        "sail": "#b8402a", "sail_edge": "#eea444", "fin": "#575a4c",
        "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#d8a838", "pupil": "#17110c", "dorsal_dark": "#3d3227",
    }
    m.sexes = {"male": {"sail": "#bd3e26", "sail_edge": "#f2ac46"},
               "female": {"sail": "#7a6a58", "sail_edge": "#ad9a72", "dorsal": "#4e4e44"}}
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 26, 8))
    m.box("body", (-5.5, 19, 1), (5.5, 30, 14), name="hips")
    m.box("body", (-6.5, 16, -14), (6.5, 30, 2), name="belly")
    m.box("body", (-5.5, 16, -24), (5.5, 28, -13), name="chest")
    m.box("body", (-4.5, 24, -28), (4.5, 30, -22), name="shoulders")
    # sail: thin vertical vanes along the spine, tallest over the middle of the back
    sail = [(-22, 6, 5), (-16, 6, 10), (-10, 6, 14), (-4, 6, 16), (2, 6, 14), (8, 6, 9), (14, 4, 4)]
    for z0, ln, h in sail:
        m.box("body", (-0.5, 30, z0), (0.5, 30 + h, z0 + ln), name="sail", tag="sail")
    m.bone("male_display", "body", (0, 30, 0))
    for z0, ln, h in sail[1:-1]:
        m.box("male_display", (-0.5, 30 + h, z0 + 1), (0.5, 30 + h + 3, z0 + ln - 1), name="sail_top", tag="sail")

    neck = m.chain(["neck1", "neck2"], "body", 0, [(27, -26), (31, -31), (33.5, -35)], "-z",
                   [(8, 8), (7, 7)], overlap=(2.0, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-4 - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    m.box("skull", *R(-3.5, -2, -7, 3.5, 4, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, -2, -21, 2, 2, -7), name="snout",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}})
    m.box("skull", *R(-2.5, -2, -24, 2.5, 2, -21), name="rosette",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}})
    m.box("skull", *R(-1, 4, -8, 1, 5, -3), name="crest", tag="dorsal_dark")
    m.bone("jaw", "skull", (0, ay - 2, az - 2))
    m.box("jaw", *R(-2, -4, -23, 2, -2, -6), name="jaw", paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}})
    m.box("jaw", *R(-3, -5, -7, 3, -2, -1), name="jaw_back", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3.5, ay + 2.0, az - 4.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3.5, ay + 2.0, az - 4.0), "r": 1.0, "side": -1},
    ]

    def arm(side, sx):
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", 5.5 * sx, [(21, -20), (16, -21), (12.5, -24)], "-y",
                     [(3, 3), (2, 3)], tag="limb", overlap=(1.0, 0.5))
        ey, ez = ch["end"]
        x = 5.5 * sx
        m.box(f"forearm_{side}", (x - 1, ey - 3, ez - 1.5), (x, ey, ez - 0.5), tag="claw", name="thumb_claw", paint={"axis": "-y"})
        m.box(f"forearm_{side}", (x, ey - 2, ez - 1.5), (x + 1, ey, ez - 0.5), tag="claw", name="claw", paint={"axis": "-y"})
    m.sym(arm)

    def leg(side, sx):
        x = 6 * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x,
                     [(26, 7), (16, 2), (7, 8), (2, 5.5)], "-y",
                     [(6, 8, -0.5), (4, 5, 0.5, "limb"), (3, 3, 0.0, "limb")], overlap=(1.5, 1.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = lambda x0, y0, z0, x1, y1, z1: ((x + x0, by + y0, bz + z0), (x + x1, by + y1, bz + z1))
        m.box(f"toes_{side}", *T(-2.5, -2, -6, 2.5, 0, 1), tag="limb", name="toes")
        m.box(f"toes_{side}", *T(-2.5, -2, -7, 2.5, -1, -6), tag="claw", name="claws")
    m.sym(leg)

    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0,
                   [(26, 13), (25.5, 25), (25, 37), (25, 49), (25, 61)], "+z",
                   [(9, 9), (7, 7), (5, 5), (3, 3)], overlap=(1.0, 1.0))
    # paddle tail: tall thin fin above and below the last segments
    for k, (up, down) in ((1, (3, 2)), (2, (5, 4)), (3, (6, 5))):
        sg = tail["segments"][k]
        y0, z0 = sg["unposed"]
        L = int(round(sg["len"]))
        hh = (7, 5, 3)[k - 1] / 2
        m.box(f"tail{k+1}", (-0.5, y0 + hh, z0), (0.5, y0 + hh + up, z0 + L), name="fin", tag="fin")
        m.box(f"tail{k+1}", (-0.5, y0 - hh - down, z0 + 1), (0.5, y0 - hh, z0 + L), name="fin", tag="fin")

    def pattern(model, tx, rgb, region):
        P = tx.P
        if tx.cube.tag == "sail":
            top = tx.cube.to[1]
            base = 30.0
            g = (P[1] - base) / max(1.0, top - base) if tx.cube.bone in ("body", "male_display") else 0.5
            col = tx.pal["sail"] * (1 - 0.35 * max(0.0, min(1.0, g))) + tx.pal["sail_edge"] * 0.35 * max(0.0, min(1.0, g))
            if int(math.floor(P[2])) % 3 == 0:
                col = col * 0.78   # neural spines
            if P[1] > top - 1.0:
                col = tx.pal["sail_edge"].copy()
            return col
        if tx.cube.tag == "fin":
            col = tx.pal["fin"].copy()
            if int(math.floor(P[2])) % 3 == 0:
                col = col * 0.82
            if P[1] > tx.cube.to[1] - 1.0 or P[1] < tx.cube.frm[1] + 1.0:
                col = col * 0.7 + tx.pal["sail"] * 0.3
            return col
        if tx.cube.tag == "skin" and region in ("dorsal", "flank"):
            band = math.sin(P[2] * 2 * math.pi / 9.0 + 0.5 * math.sin(P[0]))
            if region == "dorsal" and band > 0.4:
                rgb = rgb * 0.8
        return rgb
    m.pattern = pattern

    trex.animations(m)
    # lower hips than the T. rex: re-make the resting pose
    m.animations = [a for a in m.animations if not a["name"].endswith(".sit")]
    joints = {}
    for side in ("l", "r"):
        joints["@thigh_" + side] = (60, 0, 0)
        joints["shin_" + side] = (-112, 0, 0)
        joints["foot_" + side] = (58, 0, 0)
        joints["toes_" + side] = (-6, 0, 0)
    joints.update({"tail1": (7, 0, 0), "tail2": (3, 0, 0), "neck1": (-6, 0, 0), "skull": (4, 0, 0)})
    m.anim("sit", 4.0, True, sit_tracks(4.0, 11, joints, breathe=0.4))
    return m
