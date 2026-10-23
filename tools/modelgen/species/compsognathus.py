"""
Compsognathus longipes  (Late Jurassic, Germany / France)

Reference (Wikipedia): length 0.7-1.4 m, hip height 20-29 cm, mass 0.3-3.5 kg,
narrow long skull with large eyes, long slender legs, long balancing tail,
two large clawed fingers. No feathers preserved, but close relatives
(Sinosauropteryx) had simple filament "fuzz", so it is shown fuzzy.

In game: slightly enlarged for readability. Modelled at 3x, rendered at 0.3
-> ~1.2 blocks long, a chicken-sized skittish scavenger.
"""
import math
from smalltheropod import build_small

ID = "compsognathus"


def pattern(model, tx, rgb, region):
    P = tx.P
    if tx.cube.tag != "skin":
        return rgb
    # dark lateral stripe from the eye along the flank to the tail tip
    if tx.face in ("east", "west") and 0.45 < tx.cy < 0.72:
        rgb = rgb * 0.62
    if region == "dorsal":
        spot = math.sin(P[2] * 1.7) * math.sin(P[0] * 2.3 + P[2] * 0.4)
        if spot > 0.55:
            rgb = rgb * 0.72
    return rgb


P = {
    "render_scale": 0.3,
    "palette": {
        "dorsal": "#57562c", "flank": "#8c874a", "belly": "#e0d8a8",
        "limb": "#7a7447", "limb_top": "#8c874a",
        "claw": "#2a2620", "claw_base": "#2a2620", "claw_tip": "#5d574c",
        "feather": "#6b6330", "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#c9932a", "pupil": "#120d08",
    },
    "hip": (12, 4),
    "torso": [
        ((-2, 9, -1), (2, 14, 6), "hips"),
        ((-2.5, 8, -9), (2.5, 14, 0), "belly"),
        ((-2, 8, -13), (2, 13, -8), "chest"),
    ],
    "neck_pts": [(12, -12), (15.5, -15.5), (19, -17)],
    "neck_secs": [(3, 3), (3, 3)],
    "head_pitch": 6,
    "head": {"cranium": (4, 4, 4), "snout": (2, 2, 4), "snout_y": 0, "jaw": (2, 1, 5),
             "eye": (1.0, -1.0), "eye_r": 1.0},
    "mask": False,
    "arm_x": 2.0,
    "arm_pts": [(10, -10.5), (8, -10), (7, -12)],
    "arm_secs": [(1, 1), (1, 1)],
    "leg_x": 2.0,
    "leg_pts": [(12, 4), (7.5, 1), (3.5, 4), (1, 2.5)],
    "leg_secs": [(2, 4, -0.5), (2, 2, 0.0, "limb"), (1, 1, 0.0, "limb")],
    "toes": (3, 2),
    "sickle": False,
    "tail_pts": [(12, 5), (12.5, 12), (13, 19), (13, 26), (13, 33), (13.2, 40)],
    "tail_secs": [(4, 4), (3, 3), (2, 2), (2, 2), (1, 1)],
    "pattern": pattern,
    "anim_speed": 1.3,
}


def build():
    return build_small(ID, P)
