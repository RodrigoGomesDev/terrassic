"""
Gallimimus bullatus  (Late Cretaceous, Mongolia)

Reference (Wikipedia): length ~6 m, hip height ~1.9 m, mass ~440 kg; the largest
ornithomimid. Small head with a long toothless beak, large eyes, long neck,
short arms with three fingers, very long legs (fast runner) and a long tail.
Close relatives (Ornithomimus) preserve feathers and wing-like arm feathers.

In game: scale ~0.6, modelled at 1x -> ~3.8 blocks long, head ~1.8 blocks high.
"""
import math
from smalltheropod import build_small

ID = "gallimimus"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "feather":
        # dark wing/tail feathers with pale tips
        tip = (P[2] - tx.cube.frm[2]) / max(1.0, tx.cube.size[2])
        if tip > 0.75:
            return tx.pal["feather_tip"].copy()
        return rgb
    if tag == "skin" and region in ("dorsal", "flank"):
        n = math.sin(P[0] * 1.9 + P[2] * 0.7) * math.sin(P[1] * 1.3 - P[2] * 0.9)
        if n > 0.6:
            rgb = rgb * 0.85
    return rgb


P = {
    "render_scale": 1.0,
    "palette": {
        "dorsal": "#6e665a", "flank": "#9c917c", "belly": "#ebe4d0",
        "limb": "#8f8467", "limb_top": "#9c917c",
        "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#5d574c",
        "feather": "#4a4036", "feather_tip": "#e8e0cc", "beak": "#5a4e40",
        "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#d89a2a", "pupil": "#120d08",
    },
    "sexes": {"male": {"feather": "#3a3632", "feather_tip": "#f2efe6", "dorsal": "#5e5a52"},
              "female": {"feather": "#6a5a46", "feather_tip": "#cfc3a8", "dorsal": "#756a58"}},
    # ostrich build: short deep torso under a thick plumage, long S-curved neck, tiny head with big eyes and a long
    # beak, very long shins and metatarsals; arm and tail feathers (Ornithomimus)
    "hip": (18, 4),
    "torso": [
        ((-3, 14, -1), (3, 20, 7), "hips"),
        ((-3.5, 13, -9), (3.5, 20, 0), "belly"),
        ((-3, 13, -13), (3, 19, -8), "chest"),
        ((-3.5, 20, -9), (3.5, 21, 6), "back", "feather"),
        ((-2.5, 19, -13), (2.5, 20, -8), "shoulders", "feather"),
    ],
    "neck_pts": [(17, -12), (22, -15), (27, -15.5), (31, -14.5)],
    "neck_secs": [(3, 4), (3, 3), (2, 3)],
    "head_pitch": 8,
    "head": {"cranium": (3, 3, 4), "snout": (2, 2, 6), "snout_y": 0, "jaw": (2, 1, 6),
             "eye": (0.5, -1.0), "eye_r": 1.3},
    "teeth": False,
    "beak": True,
    "arm_x": 3.0,
    "arm_pts": [(15, -10), (12.5, -9), (11, -11.5)],
    "arm_secs": [(1, 2), (1, 1)],
    "wing": (6, 3),
    "leg_x": 2.5,
    "leg_pts": [(18, 4), (12, 0), (5, 5), (1, 3)],
    "leg_secs": [(4, 5, -0.5), (2, 2, 0.5, "limb"), (1, 1, 0.0, "limb")],
    "toes": (3, 2),
    "sickle": False,
    "tail_pts": [(18, 6), (18.5, 14), (19, 22), (19, 30), (19, 38)],
    "tail_secs": [(4, 4), (3, 3), (2, 2), (2, 2)],
    "tail_fan": [(2, 6), (3, 8)],
    "saddle": (21, -6, 2, 6, 3.5, 4),
    "sit": {"drop": 9},
    "herbivore": True,
    "pattern": pattern,
    "anim_speed": 1.2,
}


def build():
    return build_small(ID, P)
