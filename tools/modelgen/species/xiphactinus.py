"""
Xiphactinus audax  (Late Cretaceous, Western Interior Seaway, Kansas)

Reference (Wikipedia; Everhart 2005): a predatory bony fish of 4.5-6 m, the biggest of its family; a deep,
tarpon-like body, a huge upturned bulldog mouth with long fangs in the front of the jaws, a deeply forked tail,
long pointed pectoral fins, small pelvic fins and a dorsal and an anal fin set far back near the tail. The famous
"fish within a fish" fossil (FHSM VP-333) holds a 1.8 m Gillicus swallowed whole. Blue-grey above, silver below.

Built on the marine archetype (tail wave + paddles). Modelled ~96 px long; SIZES scales it to 6 m. Males a
deeper blue with a dark eye stripe, females greyer.
"""
import math
from rig import track, keys
import marine

ID = "xiphactinus"


def body_parts(m):
    # deep compressed body (narrow, tall), a heavy head that is a third of it
    m.box("body", (-4, 4, -8), (4, 20, 10), name="torso")
    m.box("body", (-3.5, 6, -16), (3.5, 19, -8), name="chest")
    # dorsal and anal fins set far back, like a tarpon's
    m.box("body", (-0.5, 20, 1), (0.5, 23, 9), name="dorsal_fin", tag="fin")
    m.box("body", (-0.5, 23, 5), (0.5, 26, 9), name="dorsal_fin_tip", tag="fin")
    m.box("body", (-0.5, 2, 2), (0.5, 4, 9), name="anal_fin", tag="fin")
    m.box("body", (-0.5, 1, 5), (0.5, 2, 9), name="anal_fin_tip", tag="fin")

    # the "neck" is just the back of the skull: the whole head tilts on it when the mouth opens
    neck = m.chain(["neck"], "body", 0, [(12, -15), (12, -18)], "-z", [(7, 13)], overlap=(1.0, 0.0))
    ay, az = neck["end"]
    m.bone("head", "neck", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # bulldog head: a tall skull, the upper jaw short and turned up, big fangs at the front
    m.box("skull", *R(-3.5, -4, -9, 3.5, 7, 0), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -3, -14, 3, 3, -9), name="snout", paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1, "freq": 0.7}})
    m.box("skull", *R(-2.5, -4, -15, 2.5, -2, -13), name="fangs_upper", tag="tooth_cube", paint={"axis": "-y"})
    m.bone("jaw", "skull", (0, ay - 4, az - 1))
    # the lower jaw juts out past the upper one
    m.box("jaw", *R(-3, -8, -16, 3, -4, -1), name="jaw", paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1, "freq": 0.7}})
    m.box("jaw", *R(-2.5, -6, -17, 2.5, -4, -15), name="fangs_lower", tag="tooth_cube", paint={"axis": "+y"})
    # gill cover
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3.5, ay + 2.5, az - 6.0), "r": 1.3, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3.5, ay + 2.5, az - 6.0), "r": 1.3, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "fin":
        col = tx.pal["fin"].copy()
        if tx.edge:
            col = tx.pal["fin_edge"].copy()
        # rays along the fins
        if int(math.floor((P[0] if tx.cube.name == "paddle" else P[2]) * 1.2)) % 2 == 0:
            col = col * 0.88
        return col
    if tag == "skin":
        # mirror-silver flanks with a row of big scales; the gill cover darker
        if region == "flank":
            if (int(math.floor(P[2] * 0.9)) + int(math.floor(P[1] * 0.9))) % 2 == 0:
                rgb = rgb * 1.08
            else:
                rgb = rgb * 0.94
            if tx.cube.bone == "skull" and P[2] > tx.cube.frm[2] + 6:
                rgb = tx.pal["gill"].copy()
        elif region == "dorsal" and math.sin(P[2] * 1.3) * math.sin(P[0] * 2.0) > 0.6:
            rgb = rgb * 0.88
        # dark stripe through the eye (males)
        if tx.cube.bone == "skull" and abs(P[1] - (tx.cube.frm[1] + 6.5)) < 0.8 and P[2] < tx.cube.frm[2] + 7:
            rgb = tx.pal["stripe"].copy()
    return rgb


def attack(m):
    # the lunge: a tail thrust shoots the body forward, the mouth gapes and the jaws clap shut on the prey
    m.anim("attack", 0.6, False, {
        "body": track(pos=keys([(0, 0, 0, 0), (0.15, 0, 0, 2), (0.3, 0, 0, -5), (0.6, 0, 0, 0)]),
                      rot=keys([(0, 0, 0, 0), (0.15, 5, 0, 0), (0.3, 1, 0, 0), (0.6, 0, 0, 0)])),
        "neck": track(rot=keys([(0, 0, 0, 0), (0.15, 24, 0, 0), (0.3, 0, 0, 0), (0.6, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.15, -30, 0, 0), (0.24, -32, 0, 0), (0.3, 0, 0, 0), (0.6, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.1, 0, 18, 0), (0.3, 0, -14, 0), (0.6, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.12, 0, 22, 0), (0.32, 0, -18, 0), (0.6, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.15, 0, 26, 0), (0.35, 0, -22, 0), (0.6, 0, 0, 0)])),
    })


# knocked out (stunned, floating on its side): fins folded, tail limp
LIMP = {"neck": (2, 0, 0), "jaw": (-10, 0, 0),
        "tail1": (-3, 0, 0), "tail2": (-5, 0, 0), "tail3": (-6, 0, 0),
        "flipper_front_l": (0, -50, 10), "flipper_front_r": (0, 50, -10),
        "flipper_back_l": (0, -40, 10), "flipper_back_r": (0, 40, -10)}

SPEC = dict(
    palette={"dorsal": "#3a5068", "flank": "#aab4b8", "belly": "#e8ece8", "gill": "#6e7a86", "stripe": "#1e2630",
             "limb": "#3a5068", "limb_top": "#4a6078",
             "fin": "#4a5a66", "fin_edge": "#8a98a0",
             "tooth": "#f4f0e4", "mouth": "#8a3844", "gum": "#5e262e",
             "tooth_cube": "#f4f0e4", "tooth_cube_base": "#d8d2c0", "tooth_cube_tip": "#fbf8f0",
             "eye": "#d8c060", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#2c4466", "stripe": "#141a22"},
           "female": {"dorsal": "#4a5a66", "flank": "#b4babc", "stripe": "#5a6470"}},
    pattern=pattern, body=(12, 0), body_parts=body_parts,
    tail=dict(points=[(12, 10), (12, 20), (12, 29), (12, 37)],
              sections=[(7, 14), (5, 10), (3, 6)],
              fluke=dict(lower=(14, -35, 2), upper=(14, 35, 2)),   # deeply forked, lobes alike
              keel=[]),
    # long pointed pectorals low on the chest, small pelvic fins
    flippers=[dict(name="flipper_front", pivot=(3.5, 8, -10), rot=(0, -35, -25), span=(3.5, 15.5), y=(7.5, 8.5), z=(-12, -8)),
              dict(name="flipper_back", pivot=(2.5, 5, 0), rot=(0, -30, -30), span=(2.5, 8.5), y=(4.5, 5.5), z=(-1, 2))],
    swim=dict(idle=(2.4, 8, 5, 2.0), walk=(1.2, 16, 8), run=(0.6, 22, 10, 3.0), sit=(3.0, 5, 4, 1.0)),
    attack=attack,
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-8),
)


def build():
    return marine.build(ID, SPEC)
