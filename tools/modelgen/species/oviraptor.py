"""
Oviraptor philoceratops  (Late Cretaceous, Djadochta Formation, Mongolia)

Reference (Wikipedia, AMNH 6517, Osborn 1924): length ~1.6-2 m, mass ~33-40 kg. A toothless, short and very deep
parrot-like beak, a small crest on the skull (the tall casque belongs to Citipati), long arms with three clawed
fingers and big wing feathers (quill knobs in relatives), a long neck, long legs, a short tail with a pygostyle
-> a feather fan. The "egg thief" that turned out to be brooding its own nest.

In game: 2 m (TAMANHOS.md) on the oviraptorosaur rig. Desert and badlands omnivore, tamed with eggs and seeds;
skittish. A tame one makes the tame dinosaurs and chickens around it lay more often (docs/NINHOS.md).
Gobi dune plumage: ochre and rust with black wing feathers barred white, a cream belly, a red-and-blue crest on the
males, a dull brown one on the females.
"""
import math
from oviraptorosaur import build_ovi

ID = "oviraptor"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "feather":
        # black vanes with a white bar across the middle and white tips
        tip = (P[2] - tx.cube.frm[2]) / max(1.0, tx.cube.size[2])
        if tip > 0.8 or 0.42 < tip < 0.55:
            return tx.pal["bar"].copy()
        return rgb
    if tag == "skin" and region in ("dorsal", "flank"):
        # fine rust speckling over the ochre, denser on the back
        fleck = math.sin(P[0] * 2.7 + P[2] * 2.1) * math.sin(P[1] * 2.4 - P[2] * 0.7)
        if region == "dorsal" and fleck > 0.4:
            rgb = rgb * 0.75
        elif region == "flank" and tx.cy > 0.5 and fleck > 0.6:
            rgb = rgb * 0.85
    return rgb


def extra(m, neck, tail):
    # three long fingers with claws on each hand (the rig gives one claw; two more each side)
    ax = P["arm_x"]
    ey, ez = P["arm_pts"][-1]
    for side, sx in (("l", 1), ("r", -1)):
        x = ax * sx
        for dx in (-1.0, 1.0):
            m.box(f"forearm_{side}", (x + dx - 0.5, ey - 2.5, ez - 2.5), (x + dx + 0.5, ey - 0.5, ez - 1.5),
                  tag="claw", name="finger", paint={"axis": "-y"})
    # a plume ruff down the back of the neck
    for seg in neck["segments"][:2]:
        y0, z0 = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-1, y0 + 1.5, z0 - L), (1, y0 + 2.5, z0 + 1), tag="feather", name="ruff")


P = {
    "render_scale": 1.0,
    "palette": {
        "dorsal": "#9a6a3c", "flank": "#c09060", "belly": "#ecdfc4",
        "limb": "#a8865c", "limb_top": "#c09060",
        "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#5d574c",
        "feather": "#2a2420", "bar": "#f2ede2", "beak": "#5a4a3c", "casque": "#c84a3a",
        "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#e0b040", "pupil": "#120d08",
    },
    "sexes": {"male": {"casque": "#d8453a", "feather": "#1e1a18", "dorsal": "#8e5a30", "eye": "#e8b838"},
              "female": {"casque": "#8a6a4c", "feather": "#4a3c30", "bar": "#dcd2c0", "dorsal": "#7e6448", "flank": "#a88c68"}},
    "hip": (18, 4),
    "torso": [
        ((-3, 13, -2), (3, 21, 6), "hips"),
        ((-3.5, 12, -10), (3.5, 21, -1), "belly"),
        ((-3, 13, -14), (3, 20, -9), "chest"),
        ((-3, 21, -10), (3, 22, 5), "back", "feather"),
    ],
    "neck_pts": [(19, -13), (23, -16), (27, -17), (30, -16)],
    "neck_secs": [(3, 4), (3, 3), (2, 3)],
    "head_pitch": 12,
    "head": {"cranium": (4, 4, 4), "snout": (3, 3, 3), "snout_y": 0, "jaw": (3, 2, 3),
             "eye": (1.0, -1.0), "eye_r": 1.3},
    "casque": (-1, 3, -3, 1, 5, 1),
    "arm_x": 3.0,
    "arm_pts": [(16, -12), (12, -10), (11, -14)],
    "arm_secs": [(2, 2), (1, 2)],
    "wing": (9, 5),
    "leg_x": 2.5,
    "leg_pts": [(18, 4), (11, -1), (4.5, 4), (1, 2.5)],
    "leg_secs": [(3, 5, -0.5), (2, 2, 0.5, "limb"), (1, 1, 0.0, "limb")],
    "toes": (3, 2),
    "tail_pts": [(18, 6), (18.5, 13), (19, 20), (19, 26)],
    "tail_secs": [(4, 4), (3, 3), (2, 2)],
    "tail_fan": [(1, 8), (2, 12)],
    "sit": {"drop": 8},
    "brood": {"drop": 9, "arms": (-15, 0, -75)},
    "pattern": pattern,
    "extra": extra,
    "anim_speed": 1.25,
}


def build():
    return build_ovi(ID, P)
