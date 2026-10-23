"""
Pachycephalosaurus wyomingensis  (Late Cretaceous, North America)

Reference (Wikipedia): length ~4.5 m, mass ~370-450 kg, bipedal, skull roof
thickened into a dome up to 25 cm thick ringed by bony knobs and short spikes,
small beak, short arms, stiff tail. Domes probably used for display and/or
butting contests.

In game: scale ~0.6, modelled at 1.5x and rendered at 0.667 -> ~3 blocks long.
Males carry an extra crown of spikes ("male_display" bone) and a banded dome.
"""
import math
from smalltheropod import build_small

ID = "pachycephalosaurus"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "dome":
        band = math.sin(P[1] * 2.2)
        return tx.pal["dome"] * (1.0 if band > -0.2 else 0.82)
    if tag == "skin" and region in ("dorsal", "flank"):
        spot = math.sin(P[0] * 1.7) * math.sin(P[2] * 1.1 + P[1] * 0.5)
        if spot > 0.55:
            rgb = rgb * 0.8
    return rgb


P = {
    "render_scale": 0.667,
    "palette": {
        "dorsal": "#5e4e3e", "flank": "#8a7458", "belly": "#d6c6a4",
        "limb": "#6e5c46", "limb_top": "#8a7458",
        "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#5d574c",
        "dome": "#cdbb98", "knob": "#efe6cc",
        "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#c98a2a", "pupil": "#120d08",
    },
    "sexes": {"male": {"dome": "#d8b07a", "knob": "#f4ead0"},
              "female": {"dome": "#9a8a72", "knob": "#c8bca0", "dorsal": "#64553f"}},
    "hip": (20, 5),
    "torso": [
        ((-5, 15, 0), (5, 25, 10), "hips"),
        ((-5.5, 14, -11), (5.5, 25, 1), "belly"),
        ((-4.5, 15, -16), (4.5, 24, -10), "chest"),
    ],
    "neck_pts": [(21, -15), (24.5, -19), (27, -21)],
    "neck_secs": [(6, 6), (5, 6)],
    "head_pitch": -2,
    "head": {"cranium": (7, 6, 6), "snout": (4, 4, 5), "snout_y": -2, "jaw": (4, 1, 5),
             "eye": (2.0, -3.0), "eye_r": 1.0},
    "teeth": False,
    "head_extra": [
        (-3.5, 5, -5, 3.5, 7, 1, "dome", "skull"),
        (-2.5, 7, -4, 2.5, 9, 0, "dome", "skull"),
        (-4, 3, 1, -2, 5, 2, "knob", "skull"),
        (2, 3, 1, 4, 5, 2, "knob", "skull"),
        (-2, 2, -9, -1, 3, -8, "knob", "skull"),
        (1, 2, -9, 2, 3, -8, "knob", "skull"),
        (-5, 5, -2, -4, 7, 0, "knob", "male_display"),
        (4, 5, -2, 5, 7, 0, "knob", "male_display"),
        (-1, 6, 1, 1, 8, 2, "knob", "male_display"),
        (-5, 4, -5, -4, 5, -4, "knob", "male_display"),
        (4, 4, -5, 5, 5, -4, "knob", "male_display"),
    ],
    "arm_x": 4.5,
    "arm_pts": [(18, -12), (15, -11), (14, -13.5)],
    "arm_secs": [(2, 2), (2, 2)],
    "leg_x": 3.5,
    "leg_pts": [(20, 5), (12, 1), (5.5, 6), (1.5, 3.5)],
    "leg_secs": [(5, 7, -0.5), (4, 4, 0.5, "limb"), (3, 3, 0.0, "limb")],
    "toes": (5, 3),
    "sickle": False,
    "tail_pts": [(21, 9), (21, 19), (20.5, 28), (20, 36), (20, 43)],
    "tail_secs": [(8, 8), (6, 6), (4, 4), (3, 3)],
    "pachy": True,
    "herbivore": True,
    "sit": {"drop": 10},
    "pattern": pattern,
    "anim_speed": 1.0,
}


def build():
    return build_small(ID, P)
