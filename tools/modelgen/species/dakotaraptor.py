"""
Dakotaraptor steini  (Late Cretaceous, Hell Creek, South Dakota)

Reference (Wikipedia, PBMNH.P.10.113.T, DePalma et al. 2015): length ~5.5 m, hip height ~1.5 m, mass
~220-350 kg: one of the largest dromaeosaurs, long-legged and built to run (slender leg bones), with quill
knobs on the ulna (big wing feathers on the arms), a 24 cm sickle claw, a long stiff tail with a feather fan.
Lived alongside the Tyrannosaurus in the Hell Creek floodplains.

In game: 5.5 m (TAMANHOS.md) on the small theropod rig at render scale 1 (the scale comes from SIZES in
gen_species.py), a raptor nearly three times the Velociraptor: long legs, broad wings, big sickle, a saddle
(the agile hunting mount that leaps). Hell Creek dark brown-black plumage with white wing bars and a pale
throat; males near-black with a blue sheen and bright wing bars, females brown.
"""
import math
from smalltheropod import build_small

ID = "dakotaraptor"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "feather":
        # white bars across the wing and tail feathers, dark tips
        bar = math.sin(P[2] * 2 * math.pi / 3.0)
        if bar > 0.55:
            return rgb * 0.35 + tx.pal["bar"] * 0.65
        return rgb
    if tag == "skin" and region in ("dorsal", "flank"):
        fleck = math.sin(P[0] * 2.3 + P[2] * 1.7) * math.sin(P[1] * 2.1)
        if region == "dorsal" and fleck > 0.45:
            rgb = rgb * 0.7
        elif region == "flank" and tx.cy > 0.5 and fleck > 0.65:
            rgb = rgb * 0.85
    return rgb


P = {
    "render_scale": 1.0,
    "palette": {
        "dorsal": "#3a3028", "flank": "#6a5440", "belly": "#d8cdb0",
        "limb": "#5c4e3c", "limb_top": "#6a5440",
        "claw": "#1f1b18", "claw_base": "#2a2420", "claw_tip": "#6b6158",
        "feather": "#2e2620", "bar": "#e8e2d2", "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#e0b43c", "pupil": "#140f0a",
    },
    "hip": (18, 4),
    "torso": [
        ((-3, 13, -2), (3, 21, 8), "hips"),
        ((-3.5, 12, -12), (3.5, 21, -1), "belly"),
        ((-3, 12, -17), (3, 20, -11), "chest"),
        ((-2, 21, -13), (2, 22, 7), "back", "feather"),
    ],
    "neck_pts": [(18.5, -16), (22, -19.5), (25, -21)],
    "neck_secs": [(4, 5), (3, 4)],
    "head_pitch": 4,
    "head": {"cranium": (4, 4, 5), "snout": (3, 3, 8), "snout_y": -1, "jaw": (3, 1, 10),
             "eye": (1.0, -2.0), "eye_r": 1.0, "crest": (-1, 3, -3, 1, 4, 1)},
    "mask": True,
    "arm_x": 3.0,
    "arm_pts": [(16, -13), (12, -11), (10.5, -16)],
    "arm_secs": [(2, 2), (1, 2)],
    "wing": (11, 5),
    "extra": lambda m, neck, tail: m.box("body", (-3, 20, -18), (3, 23, -12), tag="feather", name="ruff"),
    "leg_x": 2.5,
    "leg_pts": [(18, 4), (11, -1), (4.5, 4.5), (1, 2.5)],
    "leg_secs": [(3, 6, -0.5), (2, 3, 0.5, "limb"), (2, 2, 0.0, "limb")],
    "toes": (4, 2),
    "sickle": True,
    "sickle_size": (3, 4),
    "tail_pts": [(18, 7), (18.5, 16), (19, 25), (19, 34), (19, 43)],
    "tail_secs": [(5, 5), (4, 4), (3, 3), (2, 2)],
    "tail_fan": [(2, 7), (3, 11)],
    "saddle": (22, -8, 0, 6, 3.5, 3),
    "pattern": pattern,
    "sexes": {"male": {"feather": "#1e2028", "dorsal": "#2e2a30", "bar": "#f2eee4", "eye": "#e8c040"},
              "female": {"feather": "#4a3a2c", "dorsal": "#4e3f30", "flank": "#7a644c", "bar": "#d8d0bc"}},
    "sit": {"drop": 8},
    "anim_speed": 1.1,
}


def build():
    return build_small(ID, P)
