"""
Mosasaurus hoffmannii  (Late Cretaceous, Maastrichtian; seas of Europe and North America)

Reference (Wikipedia): up to ~12-17 m long, one of the largest marine reptiles; a big skull (~1.5 m) with
conical teeth and extra teeth on the palate; long streamlined body, four paddle-shaped flippers (the front pair
bigger), and a long tail ending in a crescent fluke whose lower lobe holds the bent-down vertebrae (hypocercal
tail, known from Prognathodon and Platecarpus fossils). Countershaded: dark back, pale belly. Gave birth to live
young in the water. Not a dinosaur: a marine lizard related to monitor lizards and snakes.

Modelled ~100 px long; SIZES scales it to 17 m. Built on the marine reptile archetype (species/marine.py) with
exactly the v0.3 geometry.
"""
import math
from rig import track, keys
import marine

ID = "mosasaurus"


def body_parts(m):
    m.box("body", (-6.5, 1, -12), (6.5, 15, 10), name="torso")
    m.box("body", (-6, 2, -22), (6, 14, -12), name="chest")

    neck = m.chain(["neck"], "body", 0, [(8.5, -21), (9, -27)], "-z", [(10, 10)], overlap=(1.0, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    m.box("skull", *R(-4.5, -3, -8, 4.5, 4, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -3, -21, 3, 2, -8), name="snout",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}})
    m.box("skull", *R(-2, -3, -23, 2, 1, -21), name="snout_tip", paint={"faces": {"down": "mouth"}})
    m.bone("jaw", "skull", (0, ay - 3, az - 3))
    m.box("jaw", *R(-3, -6, -21, 3, -3, -6), name="jaw", paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}})
    m.box("jaw", *R(-4.5, -6, -6, 4.5, -3, 0), name="jaw_back", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4.5, ay + 1.5, az - 5.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4.5, ay + 1.5, az - 5.0), "r": 1.0, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    if tx.cube.tag == "fin":
        col = tx.pal["fin"].copy()
        if tx.edge:
            col = tx.pal["fin_edge"].copy()
        return col
    if tx.cube.tag == "skin" and region == "dorsal":
        # faint mottling on the back
        if math.sin(P[2] * 0.9 + 1.7 * math.sin(P[0] * 0.8)) > 0.75:
            rgb = rgb * 0.88
    if tx.cube.tag == "skin" and region == "flank" and abs(math.sin(P[2] * 0.37 + P[1] * 0.2)) > 0.985:
        rgb = tx.pal["scar"].copy()  # old scars from fights
    return rgb


def attack(m):
    # bite: head pulls back, jaw opens wide, snaps shut
    m.anim("attack", 0.7, False, {
        "neck": track(rot=keys([(0, 0, 0, 0), (0.2, -12, 0, 0), (0.38, 10, 0, 0), (0.7, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -38, 0, 0), (0.34, -40, 0, 0), (0.4, 0, 0, 0), (0.7, 0, 0, 0)])),
        "body": track(pos=keys([(0, 0, 0, 0), (0.2, 0, 0, 2), (0.38, 0, 0, -3), (0.7, 0, 0, 0)])),
    })


# knocked out: rolled onto its side, flippers swept back along the flanks, the tail in a lazy curve on the ground
# (in the water it floats like this). Base flipper yaw is -30/+30, so -60/+60 lays the paddles along the body.
LIMP = {"neck": (3, -4, 0), "skull": (2, 0, 0), "jaw": (-14, 0, 0),
        "tail1": (-3, 0, 0), "tail2": (-5, 0, 0), "tail3": (-6, 0, 0), "tail4": (-6, 0, 0), "tail5": (-5, 0, 0),
        "flipper_front_l": (0, -60, 20), "flipper_front_r": (0, 60, -20),
        "flipper_back_l": (0, -60, 20), "flipper_back_r": (0, 60, -20)}

SPEC = dict(
    palette={"dorsal": "#2e3a44", "flank": "#566670", "belly": "#d8dbd0",
             "limb": "#34424c", "limb_top": "#3e4c56",
             "fin": "#26323a", "fin_edge": "#4a5a64",
             "tooth": "#efe9d6", "mouth": "#8a3a36", "gum": "#5e2623",
             "eye": "#c8b04a", "pupil": "#0f0c0a", "scar": "#7c8a90"},
    sexes={"male": {}, "female": {"dorsal": "#36424a", "flank": "#5e6c72"}},
    pattern=pattern, body=(8, 0), body_parts=body_parts,
    tail=dict(points=[(8, 9), (8, 21), (7.5, 32), (7, 42), (6.5, 51), (6, 59)],
              sections=[(11, 11), (9, 9), (7, 7), (5, 5), (3, 3)],
              fluke=dict(lower=(18, -40, 2.5), upper=(13, 35, 2)),
              keel=[(2, 2), (3, 2), (4, 1)]),
    flippers=[dict(name="flipper_front", pivot=(5.5, 4, -17), rot=(0, -30, -20), span=(5.5, 17.5), y=(3.5, 4.5), z=(-20, -14)),
              dict(name="flipper_back", pivot=(5.5, 4, 6), rot=(0, -35, -20), span=(5.5, 13.5), y=(3.5, 4.5), z=(4, 9))],
    swim=dict(idle=(4.0, 6, 6, 2.0), walk=(2.0, 12, 10), run=(1.0, 16, 12, 4.0), sit=(4.0, 4, 4, 1.0)),
    attack=attack,
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-10),
)


def build():
    return marine.build(ID, SPEC)
