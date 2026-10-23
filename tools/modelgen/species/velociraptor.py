"""
Velociraptor mongoliensis  (Late Cretaceous, Mongolia)

Reference (Wikipedia): length 1.5-2.07 m, hip height ~0.5 m, mass 14-20 kg,
skull up to 23 cm, long low upturned snout, three-fingered hands with curved
claws, retractable sickle claw on the 2nd toe held off the ground, long braced
tail, quill knobs on the ulna -> feathered (wing feathers on the forearm).

In game: real size. Modelled at 2x and rendered at 0.5 -> ~2 blocks long.
"""
import math
from smalltheropod import build_small

ID = "velociraptor"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "feather":
        # barred wing / tail feathers, darker tips
        bar = math.sin(P[2] * 2 * math.pi / 2.6)
        rgb = rgb * (0.78 if bar > 0.4 else 1.0)
        return rgb
    if tag == "skin" and region in ("dorsal", "flank"):
        bars = math.sin(P[2] * 2 * math.pi / 4.2 + 0.8 * math.sin(P[0]))
        if region == "dorsal" and bars > 0.2:
            rgb = rgb * 0.62
        elif region == "flank" and tx.cy > 0.55 and bars > 0.55:
            rgb = rgb * 0.75
    return rgb


P = {
    "render_scale": 0.5,
    "palette": {
        "dorsal": "#6a4a2e", "flank": "#9c7149", "belly": "#e7d7b5",
        "limb": "#857456", "limb_top": "#9c7149",
        "claw": "#1f1b18", "claw_base": "#2a2420", "claw_tip": "#6b6158",
        "feather": "#5b3e26", "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#e0b43c", "pupil": "#140f0a",
    },
    "hip": (16, 4),
    "torso": [
        ((-3, 12, -2), (3, 19, 7), "hips"),
        ((-3.5, 11, -11), (3.5, 19, -1), "belly"),
        ((-3, 11, -15), (3, 18, -10), "chest"),
        ((-2, 19, -12), (2, 20, 6), "back", "feather"),
    ],
    "neck_pts": [(16.5, -14), (19.5, -17), (22, -18.5)],
    "neck_secs": [(4, 5), (3, 4)],
    "head_pitch": 4,
    "head": {"cranium": (4, 4, 5), "snout": (3, 3, 7), "snout_y": -1, "jaw": (3, 1, 9),
             "eye": (1.0, -2.0), "eye_r": 1.0, "crest": (-1, 3, -2, 1, 4, 1)},
    "mask": True,
    "arm_x": 3.0,
    "arm_pts": [(14, -12), (10.5, -10), (9.5, -14)],
    "arm_secs": [(2, 2), (1, 2)],
    "wing": (6, 3),
    "leg_x": 2.5,
    "leg_pts": [(16, 4), (10.5, 0), (5, 4.5), (1, 2.5)],
    "leg_secs": [(3, 5, -0.5), (2, 3, 0.5, "limb"), (2, 2, 0.0, "limb")],
    "toes": (4, 2),
    "sickle": True,
    "tail_pts": [(16, 6), (16.5, 14), (17, 22), (17, 30), (17, 38)],
    "tail_secs": [(5, 5), (4, 4), (3, 3), (2, 2)],
    "tail_fan": [(2, 5), (3, 7)],
    "pattern": pattern,
    "sexes": {"male": {"feather": "#3f3024", "dorsal": "#5c3f28", "eye": "#e8c040"},
              "female": {"feather": "#6a4a30", "dorsal": "#7a5a3c", "flank": "#a88058"}},
    "sit": {"drop": 7},
    "anim_speed": 1.0,
}


def build():
    return build_small(ID, P)
