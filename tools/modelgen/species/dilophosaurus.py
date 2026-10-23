"""
Dilophosaurus wetherilli  (Early Jurassic, Arizona)

Reference (Wikipedia): length ~7 m, mass ~400 kg, slender build, a pair of thin
semicircular crests running lengthwise on top of the skull, a notch (kink) in the
upper jaw, long neck and tail. (No neck frill and no venom spit - those come
from the movies.)

In game: scale ~0.6, modelled at 1x -> ~4.5 blocks long.
Males show taller, brighter crests ("male_display" bone).
"""
import math
from smalltheropod import build_small

ID = "dilophosaurus"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "crest":
        band = math.sin(P[2] * 2 * math.pi / 3.0)
        return tx.pal["crest"] * (1.0 if band > -0.3 else 0.55) if P[1] < tx.cube.to[1] - 0.6 else tx.pal["crest_edge"].copy()
    if tag == "skin" and region in ("dorsal", "flank"):
        bars = math.sin(P[2] * 2 * math.pi / 6.0 + 0.6 * math.sin(P[0]))
        if region == "dorsal" and bars > 0.3:
            rgb = rgb * 0.7
        elif tx.cy > 0.5 and bars > 0.7:
            rgb = rgb * 0.82
    return rgb


P = {
    "render_scale": 1.0,
    "palette": {
        "dorsal": "#55573a", "flank": "#878452", "belly": "#d9d0a8",
        "limb": "#6f6c48", "limb_top": "#878452",
        "claw": "#24201b", "claw_base": "#2c2620", "claw_tip": "#6b6158",
        "crest": "#c8402a", "crest_edge": "#f2c44a",
        "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#e0b43c", "pupil": "#140f0a",
    },
    "sexes": {"male": {"crest": "#cc3a22", "crest_edge": "#f6cc48"},
              "female": {"crest": "#77704e", "crest_edge": "#a89c70", "dorsal": "#5e5a40"}},
    "hip": (17, 4),
    "torso": [
        ((-3.5, 13, -1), (3.5, 20, 8), "hips"),
        ((-4, 12, -11), (4, 20, 0), "belly"),
        ((-3, 12, -16), (3, 19, -10), "chest"),
    ],
    "neck_pts": [(17, -15), (20.5, -19), (23, -21)],
    "neck_secs": [(5, 5), (4, 5)],
    "head_pitch": 2,
    "head": {"cranium": (5, 5, 5), "snout": (3, 4, 7), "snout_y": -1, "jaw": (3, 1, 10),
             "eye": (2.0, -2.0), "eye_r": 1.0},
    "head_extra": [
        (0.5, 3, -10, 1.5, 5, -2, "crest", "skull"),
        (-1.5, 3, -10, -0.5, 5, -2, "crest", "skull"),
        (0.5, 5, -8, 1.5, 6, -3, "crest", "skull"),
        (-1.5, 5, -8, -0.5, 6, -3, "crest", "skull"),
        (0.5, 6, -7, 1.5, 8, -4, "crest", "male_display"),
        (-1.5, 6, -7, -0.5, 8, -4, "crest", "male_display"),
    ],
    "mask": False,
    "arm_x": 3.5,
    "arm_pts": [(15, -13), (11.5, -12), (10, -15)],
    "arm_secs": [(2, 2), (1, 2)],
    "leg_x": 3.0,
    "leg_pts": [(17, 4), (10.5, 0), (4.5, 5), (1, 2.5)],
    "leg_secs": [(4, 6, -0.5), (3, 3, 0.5, "limb"), (2, 2, 0.0, "limb")],
    "toes": (5, 3),
    "sickle": False,
    "tail_pts": [(17, 7), (17.5, 16), (18, 25), (18, 33), (18, 40)],
    "tail_secs": [(6, 6), (4, 4), (3, 3), (2, 2)],
    "display": True,
    "sit": {"drop": 8},
    "pattern": pattern,
    "anim_speed": 0.9,
}


def build():
    return build_small(ID, P)
