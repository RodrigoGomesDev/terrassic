"""
Elasmosaurus platyurus  (Late Cretaceous, Campanian; Western Interior Seaway, Kansas)

Reference (Wikipedia; Sachs 2005; Cope 1868): a plesiosaur of ~10.3 m, of which the neck is about 7 m with 72
vertebrae (the longest neck of any animal, relative to the body); a small head with long interlocking needle
teeth for catching fish; a barrel body with a stiff trunk, four long paddle flippers of equal size that "flew"
under water, and a short tail. Gave birth to live young. Cope famously mounted the skull on the tail by mistake.

Modelled ~125 px long, the neck half of it (eight short segments so it sways and strikes); SIZES scales it to
10.3 m. Dark teal above, pale below, leopard-like spots on the back and neck; males darker with pale throat
bands, females browner.
"""
import math
from rig import track, keys
import plesiosaur

ID = "elasmosaurus"
BODY_Y = 8


def body_parts(m):
    # stiff barrel trunk, deep chest where the flippers attach, a flatter belly plate (the gastralia)
    m.box("body", (-7, 2, -11), (7, 15, 11), name="torso")
    m.box("body", (-6, 3, -14), (6, 14, -11), name="chest")
    m.box("body", (-5, 0, -9), (5, 2, 8), name="belly")


def head(m, ay, az, abs_pitch):
    m.bone("skull", "head", (0, ay, az), (-abs_pitch, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # tiny head on the end of the neck: rounded cranium, a slim snout bristling with needle teeth
    m.box("skull", *R(-2, -1.5, -4, 2, 2.5, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1.5, -1.5, -10, 1.5, 1.5, -4), name="snout",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1, "freq": 1.5}})
    m.bone("jaw", "skull", (0, ay - 1.5, az - 3))
    m.box("jaw", *R(-1.5, -3.5, -10, 1.5, -1.5, -3), name="jaw",
          paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1, "freq": 1.5}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (2, ay + 0.8, az - 2.0), "r": 0.9, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-2, ay + 0.8, az - 2.0), "r": 0.9, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "fin":
        col = tx.pal["fin"].copy()
        if tx.edge:
            col = tx.pal["fin_edge"].copy()
        # pale leading edge on the paddles
        if tx.face == "up" and tx.row == 0:
            col = tx.pal["fin_edge"].copy()
        return col
    if tag == "skin":
        if region in ("dorsal", "flank") and math.sin(P[0] * 1.4 + P[2] * 0.3) * math.sin(P[2] * 1.2 + P[1] * 0.7) > 0.62:
            return tx.pal["spot"].copy()                         # leopard spots over the back and neck
        if region == "belly" and tx.cube.bone.startswith("neck") and math.sin(P[2] * 1.6) > 0.7:
            return tx.pal["throat"].copy()                        # throat bands (strong on males)
    return rgb


def attack(m, necks):
    # the neck coils back, then whips forward and the jaws snap on the fish
    n = len(necks)
    t = {"body": track(pos=keys([(0, 0, 0, 0), (0.25, 0, 0, 2), (0.45, 0, 0, -3), (0.8, 0, 0, 0)]))}
    for i, b in enumerate(necks):
        # coil: base segments pitch up, outer ones down (an S); strike: the S straightens into a forward lunge
        coil = 8.0 if i < n // 2 else -10.0
        strike = -2.0 if i < n // 2 else 3.0
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.25, coil, 0, 0), (0.45, strike, 0, 0), (0.8, 0, 0, 0)]))
    t["skull"] = track(rot=keys([(0, 0, 0, 0), (0.25, 14, 0, 0), (0.45, -10, 0, 0), (0.8, 0, 0, 0)]))
    t["jaw"] = track(rot=keys([(0, 0, 0, 0), (0.25, -30, 0, 0), (0.42, -34, 0, 0), (0.5, 0, 0, 0), (0.8, 0, 0, 0)]))
    m.anim("attack", 0.8, False, t)


# knocked out: on its side, the long neck laid along the ground in a curve (pitch here becomes yaw after the roll),
# flippers swept back along the body (base yaw -20/-25 -> -80)
LIMP = {"skull": (4, 0, 0), "jaw": (-12, 0, 0), "tail1": (-4, 0, 0), "tail2": (-6, 0, 0),
        "flipper_front_l": (-70, -60, 14), "flipper_front_r": (0, 60, -14),
        "flipper_back_l": (-70, -55, 14), "flipper_back_r": (0, 55, -14)}
for _i in range(8):
    LIMP[f"neck{_i + 1}"] = (3.0 + 1.5 * _i, 0, 0)

SPEC = dict(
    palette={"dorsal": "#2a4a4a", "flank": "#5a7a76", "belly": "#dfe3d8", "spot": "#1c3232", "throat": "#eef0e4",
             "limb": "#2e4a48", "limb_top": "#3a5856",
             "fin": "#1e3a3a", "fin_edge": "#55746e",
             "tooth": "#f2eee0", "mouth": "#8a4048", "gum": "#5a2a30",
             "eye": "#d8c060", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#223e40", "spot": "#142626", "throat": "#f4f4ea"},
           "female": {"dorsal": "#3c4e44", "flank": "#6a7e6e", "spot": "#2a3a30", "throat": "#dfe3d8"}},
    pattern=pattern, body=(BODY_Y, 0), body_parts=body_parts, head=head,
    neck=dict(points=[(10, -13), (10.5, -20.5), (11, -28), (11.5, -35.5), (12, -43), (12.5, -50.5), (13, -58), (13.5, -65.5), (14, -73)],
              sections=[(6, 6), (6, 6), (5, 5), (5, 5), (4, 4), (4, 4), (3, 3), (3, 3)]),
    tail=dict(points=[(8, 11), (7, 20), (6.5, 28)], sections=[(7, 7), (4, 4)], tip=(1, 4, 5)),
    flippers=[dict(name="flipper_front", pivot=(6.5, 5, -6), rot=(0, -20, -15), span=(6.5, 22.5), y=(4.5, 5.5), z=(-9, -2)),
              dict(name="flipper_back", pivot=(6.5, 5, 6), rot=(0, -25, -15), span=(6.5, 21.5), y=(4.5, 5.5), z=(3, 9))],
    swim=dict(idle=(3.6, 10, 2.0), walk=(1.8, 22, 3.0), run=(1.0, 30, 4.0), sit=(4.0, 5, 1.5)),
    attack=attack,
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-12),
)


def build():
    return plesiosaur.build(ID, SPEC)
