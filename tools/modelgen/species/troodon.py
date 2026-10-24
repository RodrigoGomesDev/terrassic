"""
Troodon formosus  (Late Cretaceous, Judith River / Two Medicine, Montana)

Reference (Wikipedia; Russell 1969; Varricchio 1997): length ~2.4 m, hip height ~0.9 m, mass ~50 kg. A gracile
troodontid: very long slender legs (a runner), a long narrow snout with many small serrated teeth, a large braincase
and the biggest eyes of any dinosaur for its size, set partly forward (binocular vision) - a crepuscular/nocturnal
hunter of small prey. A small sickle claw on the second toe, long arms with feathered wings, a long thin tail.

In game: 2.4 m (TAMANHOS.md) on the small theropod rig (scale from SIZES in gen_species.py). Not rideable: the
night guard. Owl-like mottled plumage: tawny grey with dark flecks, barred wings and tail fan, a pale facial disc
around big golden eyes; males with a rust crest and face, females grey.
"""
import math
from smalltheropod import build_small

ID = "troodon"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "feather":
        # fine bars across the wing and tail feathers
        bar = math.sin(P[2] * 2 * math.pi / 2.2)
        if bar > 0.5:
            return rgb * 0.45 + tx.pal["bar"] * 0.55
        return rgb
    if tag == "skin" and region in ("dorsal", "flank"):
        # owl mottling: dense dark flecks on the back, sparser on the flank
        fleck = math.sin(P[0] * 3.1 + P[2] * 2.3) * math.sin(P[1] * 2.7 + P[2] * 0.9)
        if region == "dorsal" and fleck > 0.3:
            rgb = rgb * 0.68
        elif region == "flank" and tx.cy > 0.45 and fleck > 0.55:
            rgb = rgb * 0.8
    return rgb


P = {
    "render_scale": 1.0,
    "palette": {
        "dorsal": "#5a4a38", "flank": "#8a7558", "belly": "#e2d8c0",
        "limb": "#6e5e48", "limb_top": "#8a7558",
        "claw": "#1f1b18", "claw_base": "#2a2420", "claw_tip": "#6b6158",
        "feather": "#4a3c2c", "bar": "#d8cfb8", "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#f0c850", "pupil": "#140f0a",
    },
    "hip": (20, 4),
    "torso": [
        ((-2.5, 15, -2), (2.5, 22, 7), "hips"),
        ((-3, 14, -11), (3, 22, -1), "belly"),
        ((-2.5, 14, -15), (2.5, 21, -10), "chest"),
        ((-1.5, 22, -12), (1.5, 23, 6), "back", "feather"),
    ],
    "neck_pts": [(20.5, -14), (24.5, -17), (28, -18.5)],
    "neck_secs": [(3, 4), (2, 3)],
    "head_pitch": 6,
    "head": {"cranium": (4, 4, 5), "snout": (2, 2, 7), "snout_y": -1, "jaw": (2, 1, 8),
             "eye": (1.2, -1.6), "eye_r": 1.5, "crest": (-1, 3, -2, 1, 4, 1)},
    "mask": True,
    "arm_x": 2.5,
    "arm_pts": [(18, -12), (14, -10), (13, -14)],
    "arm_secs": [(2, 2), (1, 2)],
    "wing": (6, 3),
    "extra": lambda m, neck, tail: m.box("body", (-2.5, 21, -16), (2.5, 24, -11), tag="feather", name="ruff"),
    "leg_x": 2.0,
    "leg_pts": [(20, 4), (12, -2), (4.5, 4.5), (1, 2.5)],
    "leg_secs": [(2, 5, -0.5), (2, 2, 0.5, "limb"), (1, 1, 0.0, "limb")],
    "toes": (3, 2),
    "sickle": True,
    "sickle_size": (1, 2),
    "tail_pts": [(20, 7), (20.5, 15), (21, 23), (21, 31), (21, 39)],
    "tail_secs": [(4, 4), (3, 3), (2, 2), (1, 1)],
    "tail_fan": [(2, 6), (2, 8)],
    "pattern": pattern,
    "sexes": {"male": {"feather": "#7a4a2c", "dorsal": "#5a4634", "bar": "#e4d8bc", "eye": "#f4cc48"},
              "female": {"feather": "#4e4640", "dorsal": "#565048", "flank": "#8a8068", "bar": "#d4cec0"}},
    "sit": {"drop": 7},
    "anim_speed": 1.3,
}


def build():
    return build_small(ID, P)
