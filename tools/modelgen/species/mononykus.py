"""
Mononykus olecranus  (Late Cretaceous, Nemegt Formation, Mongolia)

Reference (Wikipedia; Perle et al. 1993): length ~1-1.2 m, mass ~3.5 kg. An alvarezsaurid: very long slender legs
(a sprinter), a long thin tail, a small narrow head with tiny teeth and big eyes, a long neck, and the oddest arms
of any dinosaur: short, massively built, with a single huge thumb claw - a digging tool for termite mounds and
rotten logs, like an anteater. Feathered (Shuvuuia preserves them).

In game: 1 m (TAMANHOS.md) on the small theropod rig modelled at 3x like the Compsognathus (the scale comes from
SIZES in gen_species.py); no wing feathers, stub arms with one big claw each, a sand-and-dust plumage: tawny with a
darker back, a pale throat and belly, a dark eye stripe; males with a rust cap and tail tip, females plain.
Rides on the shoulder when tamed; digs for insects.
"""
import math
from smalltheropod import build_small
from rig import track, keys

ID = "mononykus"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "feather":
        return rgb
    if tag == "skin" and region in ("dorsal", "flank"):
        # fine dust speckling, a touch darker along the spine
        fleck = math.sin(P[0] * 3.3 + P[2] * 2.4) * math.sin(P[1] * 2.9 - P[2] * 0.8)
        if region == "dorsal" and fleck > 0.45:
            rgb = rgb * 0.8
        elif region == "flank" and tx.cy > 0.55 and fleck > 0.7:
            rgb = rgb * 0.88
    return rgb


def extra(m, neck, tail):
    # the single huge thumb claw on each stub arm, curved down and in
    ax = P["arm_x"]
    ey, ez = P["arm_pts"][-1]
    for side, sx in (("l", 1), ("r", -1)):
        x = ax * sx
        m.box(f"forearm_{side}", (x - 0.5, ey - 4, ez - 1.5), (x + 0.5, ey - 1, ez - 0.5), tag="claw", name="thumb_claw",
              rot=(20, 0, -15 * sx), origin=(x, ey - 1, ez - 1), paint={"axis": "-y"})
    # a soft crest of plumes on the back of the head and down the neck
    for seg in neck["segments"][1:]:
        y0, z0 = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-1, y0 + 1, z0 - L), (1, y0 + 2, z0 + 1), tag="feather", name="ruff")


P = {
    "render_scale": 0.3,
    "palette": {
        "dorsal": "#7a5c3a", "flank": "#b08c5c", "belly": "#ecdfc0",
        "limb": "#9c7c52", "limb_top": "#b08c5c",
        "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#6d675c",
        "feather": "#5a4028", "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#d8a030", "pupil": "#120d08",
    },
    "hip": (16, 4),
    "torso": [
        ((-2, 13, -1), (2, 18, 6), "hips"),
        ((-2.5, 12, -8), (2.5, 18, 0), "belly"),
        ((-2, 12, -12), (2, 17, -7), "chest"),
        ((-1.5, 18, -8), (1.5, 19, 5), "back", "feather"),
    ],
    "neck_pts": [(16, -11), (19.5, -14), (23, -16), (26, -17)],
    "neck_secs": [(3, 3), (2, 2), (2, 2)],
    "head_pitch": 8,
    "head": {"cranium": (3, 3, 4), "snout": (2, 2, 5), "snout_y": 0, "jaw": (2, 1, 5),
             "eye": (0.5, -1.0), "eye_r": 1.3, "crest": (-1, 2, -2, 1, 3, 1)},
    "mask": True,
    "arm_x": 2.0,
    "arm_pts": [(14, -10), (12.5, -9.5), (12, -11)],
    "arm_secs": [(2, 2), (2, 2)],
    "leg_x": 2.0,
    "leg_pts": [(16, 4), (9.5, -1), (3, 4.5), (1, 2.5)],
    "leg_secs": [(2, 5, -0.5), (1, 1, 0.0, "limb"), (1, 1, 0.0, "limb")],
    "toes": (3, 2),
    "sickle": False,
    "tail_pts": [(16, 5), (16.5, 12), (17, 19), (17, 26), (17, 33), (17.2, 40)],
    "tail_secs": [(3, 3), (2, 2), (2, 2), (1, 1), (1, 1)],
    "pattern": pattern,
    "extra": extra,
    "sexes": {"male": {"feather": "#8a4a28", "dorsal": "#6e4e30"},
              "female": {"feather": "#6a5a44", "dorsal": "#7e6448", "flank": "#a89068"}},
    "sit": {"drop": 7},
    "anim_speed": 1.4,
}


def dig(m):
    """Termite digging: head down, body low, the stub arms hammer alternately with the thumb claw."""
    arm_l, arm_r = [], []
    for k in range(5):
        t0 = 0.5 + k * 0.3
        arm_l += [(t0, -70, 0, 0), (t0 + 0.15, -10, 0, 0)]
        arm_r += [(t0, -10, 0, 0), (t0 + 0.15, -70, 0, 0)]
    m.anim("dig", 2.4, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.5, 14, 0, 0), (2.0, 14, 0, 0), (2.4, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.5, 0, -1.5, 0), (2.0, 0, -1.5, 0), (2.4, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, -30, 0, 0), (2.0, -30, 0, 0), (2.4, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.5, -20, 0, 0), (2.0, -20, 0, 0), (2.4, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.5, -10, 0, 0), (0.9, -4, 0, 6), (1.3, -10, 0, -6), (1.7, -4, 0, 6), (2.0, -10, 0, 0), (2.4, 0, 0, 0)])),
        "arm_l": track(rot=keys([(0, 0, 0, 0)] + arm_l + [(2.4, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0)] + arm_r + [(2.4, 0, 0, 0)])),
        "thigh_l": track(rot=keys([(0, 0, 0, 0), (0.5, -14, 0, 0), (2.0, -14, 0, 0), (2.4, 0, 0, 0)])),
        "thigh_r": track(rot=keys([(0, 0, 0, 0), (0.5, -14, 0, 0), (2.0, -14, 0, 0), (2.4, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.5, -10, 0, 0), (2.0, -10, 0, 0), (2.4, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.7, 0, 12, 0), (1.1, 0, -12, 0), (1.5, 0, 12, 0), (1.9, 0, -12, 0), (2.4, 0, 0, 0)])),
    })


def build():
    m = build_small(ID, P)
    dig(m)
    return m
