"""
Mesodma  (Late Cretaceous to Paleocene; Hell Creek and Lance, Montana, Wyoming, Dakotas)

Reference (Wikipedia; Clemens 1964; Wilson 2013; Weil & Krause 2008): a multituberculate, the rodents before the
rodents: a mouse-to-rat-sized mammal (M. thompsoni ~15 cm head and body plus a tail of nearly the same length,
20-40 g) with big gnawing incisors, a blade-like lower premolar and rows of cusped cheek teeth for seeds, nuts
and insects. The commonest mammal of the T. rex floodplain, in the leaf litter and the burrows under the roots;
some multituberculates climbed. Nocturnal, with big eyes.

Small mammal rig (Didelphodon) modelled large (render_scale 0.2): ~42 px nose to tail tip, SIZES scales it to
0.25 m. The "rabbit" of the Cretaceous: the smallest game, in the tall grass at dusk. Agouti grey-brown fur with
a darker spine, a cream belly and chin, a dark eye ring, a naked pink nose, pale paws and a scaly naked tail;
males a touch redder, females greyer.
"""
import math
from mammal import build_mammal
from rig import track, keys

ID = "mesodma"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag in ("skin", "limb", "fur"):
        # agouti fur: short streaks along the body, banded light and dark, darker along the spine
        grain = math.sin(P[2] * 4.1 + P[0] * 1.1) * math.sin(P[1] * 3.4 + P[2] * 0.5)
        if grain > 0.5:
            rgb = rgb * 0.84
        elif grain < -0.6:
            rgb = rgb * 1.08
        if tag == "skin" and region == "dorsal" and abs(P[0]) < 1.2 and tx.cube.bone == "body":
            rgb = rgb * 0.78
    return rgb


def nibble():
    """Sits up on its haunches, forepaws to the mouth, chewing a seed; ears flick."""
    return {"nibble": (2.4, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.4, -38, 0, 0), (2.0, -38, 0, 0), (2.4, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.4, 0, 5, -1), (2.0, 0, 5, -1), (2.4, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.4, 22, 0, 0), (2.0, 22, 0, 0), (2.4, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.4, 18, 0, 0), (0.8, 18, 6, 0), (1.2, 18, -6, 0), (1.6, 18, 6, 0), (2.0, 18, 0, 0), (2.4, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.5, -10, 0, 0), (0.7, 0, 0, 0), (0.9, -10, 0, 0), (1.1, 0, 0, 0), (1.3, -10, 0, 0), (1.5, 0, 0, 0), (1.7, -10, 0, 0), (1.9, 0, 0, 0), (2.4, 0, 0, 0)])),
        "upperarm_l": track(rot=keys([(0, 0, 0, 0), (0.4, -60, 0, 0), (2.0, -60, 0, 0), (2.4, 0, 0, 0)])),
        "upperarm_r": track(rot=keys([(0, 0, 0, 0), (0.4, -60, 0, 0), (2.0, -60, 0, 0), (2.4, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.4, 70, 0, 0), (2.0, 70, 0, 0), (2.4, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.4, 70, 0, 0), (2.0, 70, 0, 0), (2.4, 0, 0, 0)])),
        "thigh_l": track(rot=keys([(0, 0, 0, 0), (0.4, 20, 0, 0), (2.0, 20, 0, 0), (2.4, 0, 0, 0)])),
        "thigh_r": track(rot=keys([(0, 0, 0, 0), (0.4, 20, 0, 0), (2.0, 20, 0, 0), (2.4, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.4, 30, 0, 0), (2.0, 30, 0, 0), (2.4, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.4, 14, 0, 0), (2.0, 14, 0, 0), (2.4, 0, 0, 0)])),
    })}


S = {
    "render_scale": 0.2,
    "palette": {
        "dorsal": "#6a5a44", "flank": "#8c7a5c", "belly": "#e2d8c0",
        "limb": "#7a6a50", "limb_top": "#82705a",
        "claw": "#d8d0c0", "claw_base": "#d8d0c0", "claw_tip": "#f0ece4",
        "fur": "#7a6a50", "ear": "#5a4a3a", "nose": "#d08898",
        "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#1e1410", "pupil": "#060402",
    },
    "sexes": {"male": {"dorsal": "#6e5840", "flank": "#927a58"},
              "female": {"dorsal": "#665c4c", "flank": "#8a7e68", "belly": "#dcd4c0"}},
    "body": (6, 2),
    "torso": [
        ((-3, 3, -2), (3, 8, 5), "hips"),
        ((-3.5, 2, -9), (3.5, 8, -1), "belly"),
        ((-3, 3, -12), (3, 8, -8), "chest"),
    ],
    "neck": {"points": [(6.5, -11), (7, -13)], "sections": [(4, 4)], "tilt": 2},
    # a big head for the body (the rodent look): round cranium, short snout, small round ears, big nocturnal eyes
    "head": {"cranium": (5, 4, 4), "snout": (3, 2, 2), "snout_y": -1, "jaw": (3, 1, 3),
             "eye": (0.6, -2.0), "eye_r": 1.1, "ears": (2, 2, 1, 2.0, 1.0, -2)},
    "mask": False,
    "hind": {"x": 2.5, "pts": [(7, 2), (4.5, 0.5), (3, 2), (2, 2.5)], "secs": [(2, 2, -0.5), (1, 1, 0.0, "limb"), (1, 1, 0.0, "limb")], "pad": (2, 2, 1)},
    "front": {"x": 2.5, "pts": [(7, -10), (4, -10.5), (2, -10)], "secs": [(2, 2, 0.0), (1, 1, 0.0, "limb")], "pad": (2, 2, 1)},
    # the long naked tail, carried straight out behind
    "tail": {"points": [(7, 5), (7.5, 11), (8, 17), (8, 23)], "sections": [(2, 2), (1, 1), (1, 1)]},
    "gait": {"walk": (0.6, 30, 30, 0.4), "run": (0.3, 44, 44, 0.8)},
    "sit_drop": 2,
    "sit": {"hind": (50, -95, 45), "front": (-35, 95, -50), "tail": (4, 2), "neck": -4},
    "pattern": pattern,
    "extra_anims": nibble(),
    "knockout": {"lift": 0.5, "neck_down": -20},
}


def build():
    return build_mammal(ID, S)
