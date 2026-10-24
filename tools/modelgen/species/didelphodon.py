"""
Didelphodon vorax  (Late Cretaceous, Hell Creek / Lance, Montana and Wyoming)

Reference (Wikipedia; Wilson et al. 2016): skull ~12 cm, body ~1 m with the tail, mass ~5 kg: the largest
Mesozoic metatherian, badger-to-otter-like, with the strongest bite for its size of any known mammal (bone-crushing
premolars), an omnivore and egg eater living on the riverbanks beside the T. rex. Possibly semi-aquatic.

In game: 0.8 m body (TAMANHOS.md) on the new small mammal rig, modelled at 3x (render_scale 0.3). The egg thief:
wild ones break and eat dinosaur eggs they find; a tame one noses out lost eggs (docs/NINHOS.md). Otter-brown fur
with a pale throat and a dark mask, naked pink nose; males darker with a cream chest blaze, females lighter.
"""
import math
from mammal import build_mammal
from rig import track, keys

ID = "didelphodon"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag in ("skin", "limb", "fur"):
        # fur grain: fine streaks along the body, a shade darker along the spine
        grain = math.sin(P[2] * 3.2 + P[0] * 0.8) * math.sin(P[1] * 2.6)
        if grain > 0.55:
            rgb = rgb * 0.86
        if tag == "skin" and region == "dorsal" and math.sin(P[0] * 3.0 + P[2] * 1.3) > 0.6:
            rgb = rgb * 0.8
    return rgb


def sniff():
    """Nose to the ground, head swinging side to side (the egg hunt)."""
    return {"sniff": (2.0, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.4, -28, 0, 0), (1.6, -28, 0, 0), (2.0, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.4, -10, 0, 0), (0.7, -10, 18, 0), (1.0, -10, -18, 0), (1.3, -10, 18, 0), (1.6, -10, 0, 0), (2.0, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.5, 0, 10, 0), (0.9, 0, -10, 0), (1.3, 0, 10, 0), (1.7, 0, -10, 0), (2.0, 0, 0, 0)])),
    })}


S = {
    "render_scale": 0.3,
    "palette": {
        "dorsal": "#4e3a28", "flank": "#7a5c40", "belly": "#d8c8a8",
        "limb": "#5a4430", "limb_top": "#6a5038",
        "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#6d675c",
        "fur": "#5a4430", "ear": "#3a2a1e", "nose": "#c8788a",
        "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#2a1a10", "pupil": "#0a0604",
    },
    "sexes": {"male": {"dorsal": "#3e2c1c", "flank": "#6a4c32", "belly": "#e8dcc0"},
              "female": {"dorsal": "#5e4830", "flank": "#8a6c4c", "belly": "#d4c4a4"}},
    "body": (9, 3),
    "torso": [
        ((-4, 5, -3), (4, 12, 8), "hips"),
        ((-4.5, 4, -12), (4.5, 12, -2), "belly"),
        ((-4, 5, -17), (4, 12, -11), "chest"),
    ],
    "neck": {"points": [(9.5, -16), (10.5, -20)], "sections": [(5, 5)], "tilt": 4},
    "head": {"cranium": (6, 5, 5), "snout": (4, 3, 4), "snout_y": -2, "jaw": (4, 1, 5),
             "eye": (0.5, -3.0), "eye_r": 1.0, "ears": (2, 2, 1, 2.5, 1.5, -3)},
    "mask": True,
    "hind": {"x": 3.0, "pts": [(9, 4), (5.5, 1.5), (3, 3.5), (2, 4)], "secs": [(3, 3, -0.5), (2, 2, 0.0, "limb"), (2, 2, 0.0, "limb")], "pad": (3, 3, 1)},
    "front": {"x": 3.0, "pts": [(9, -13), (5, -13.5), (2, -13)], "secs": [(3, 3, 0.0), (2, 2, 0.0, "limb")], "pad": (3, 3, 1)},
    "tail": {"points": [(10, 8), (11, 16), (12, 24), (12.5, 31)], "sections": [(3, 3), (2, 2), (1, 1)], "fur": 2},
    "gait": {"walk": (1.0, 26, 26, 0.5), "run": (0.5, 40, 40, 0.9)},
    "sit_drop": 3,
    "sit": {"hind": (50, -95, 45), "front": (-35, 95, -50), "tail": (4, 2), "neck": -4},
    "pattern": pattern,
    "extra_anims": sniff(),
    "knockout": {"lift": 0.5, "neck_down": -20},
}


def build():
    return build_mammal(ID, S)
