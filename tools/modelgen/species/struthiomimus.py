"""
Struthiomimus altus  (Late Cretaceous, Campanian; Dinosaur Park and Horseshoe Canyon formations, Alberta)

Reference (Wikipedia; Osborn 1917; Nicholls & Russell 1985): the "ostrich mimic", 4.3 m and ~150 kg, known from a
nearly complete skeleton (AMNH 5339). Lighter than the Gallimimus: a small head with big eyes on a very long
neck, a slender toothless beak, long arms with three long fingers of equal length bearing straight claws (hooks for
pulling down branches), long legs and a stiff tail used as a balance pole; one of the fastest dinosaurs
(50-80 km/h). Relatives preserve wing-like arm feathers and a tail fan.

Small-theropod rig with its own proportions and plumage: the longer four-segment neck, the long hooked hands,
bigger wing and tail fans, a nape crest on the males. Modelled ~1x (~66 px long); SIZES scales it to 4.3 m.
Rufous above, cream below, faint bars on the flanks; black wing feathers with white bars and tips on the males,
dun with buff tips on the females.
"""
import math
from smalltheropod import build_small

ID = "struthiomimus"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "feather":
        # dark vanes with a pale bar across the middle and pale tips
        tip = (P[2] - tx.cube.frm[2]) / max(1.0, tx.cube.size[2])
        if tip > 0.78 or 0.38 < tip < 0.5:
            return tx.pal["feather_tip"].copy()
        return rgb
    if tag == "skin":
        if region == "flank" and math.sin(P[2] * 1.4 + P[1] * 0.3) > 0.72:
            rgb = rgb * 0.86                                   # faint vertical bars on the flanks
        if region == "dorsal" and math.sin(P[0] * 2.2) * math.sin(P[2] * 1.1) > 0.55:
            rgb = rgb * 0.9
        if tx.cube.bone == "skull" and P[1] > tx.cube.frm[1] + 1.5 and tx.cube.name == "cranium":
            rgb = tx.pal["cap"].copy()                         # dark cap over the eyes
    return rgb


def extra(m, neck, tail):
    # the hands: three long fingers of equal length with straight claws (the rig gives one claw; two more each side)
    ax = P["arm_x"]
    ey, ez = P["arm_pts"][-1]
    for side, sx in (("l", 1), ("r", -1)):
        x = ax * sx
        for dx in (-1.0, 1.0):
            m.box(f"forearm_{side}", (x + dx - 0.5, ey - 2.5, ez - 2.5), (x + dx + 0.5, ey - 0.5, ez - 1.5),
                  tag="claw", name="finger", paint={"axis": "-y"})
    # a soft ruff of plumage down the back of the neck
    for seg in neck["segments"][:2]:
        y0, z0 = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-1, y0 + 1.5, z0 - L), (1, y0 + 2.5, z0 + 1), tag="feather", name="ruff")


P = {
    "render_scale": 1.0,
    "palette": {
        "dorsal": "#8a5a3a", "flank": "#b8865a", "belly": "#f0e6d0", "cap": "#4a3020",
        "limb": "#a8805a", "limb_top": "#b8865a",
        "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#5d574c",
        "feather": "#2a2420", "feather_tip": "#f4f0e6", "beak": "#6a5a48",
        "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#d8a030", "pupil": "#120d08",
    },
    "sexes": {"male": {"feather": "#1e1a18", "feather_tip": "#fbf8f2", "dorsal": "#7a4a2e", "cap": "#36221a"},
              "female": {"feather": "#6a5848", "feather_tip": "#d8ccb4", "flank": "#b09070", "dorsal": "#8e6a4c", "cap": "#5a4030"}},
    # lighter than the Gallimimus: a shorter, shallower trunk, a longer neck, longer arms and shins
    "hip": (17, 4),
    "torso": [
        ((-3, 13, -1), (3, 19, 6), "hips"),
        ((-3, 12, -9), (3, 18, 0), "belly"),
        ((-2.5, 12, -13), (2.5, 17, -8), "chest"),
        ((-3.5, 19, -9), (3.5, 20, 5), "back", "feather"),
        ((-3, 17, -14), (3, 19, -9), "shoulders", "feather"),
    ],
    "neck_pts": [(16, -12), (21, -16), (26, -18), (30, -18), (33, -16.5)],
    "neck_secs": [(3, 4), (3, 3), (2, 3), (2, 2)],
    "head_pitch": 10,
    "head": {"cranium": (3, 3, 4), "snout": (2, 2, 7), "snout_y": 0, "jaw": (2, 1, 7),
             "eye": (0.5, -1.0), "eye_r": 1.4},
    "head_extra": [dict(box=(-1, 1.5, -2, 1, 3.5, 2), tag="feather", bone="male_display", name="crest")],
    "teeth": False,
    "beak": True,
    "arm_x": 3.0,
    "arm_pts": [(14, -10), (10.5, -9), (8, -12)],
    "arm_secs": [(1, 2), (1, 1)],
    "wing": (7, 3),
    "leg_x": 2.5,
    "leg_pts": [(17, 4), (11, 0), (4, 5), (1, 3)],
    "leg_secs": [(4, 5, -0.5), (2, 2, 0.5, "limb"), (1, 1, 0.0, "limb")],
    "toes": (3, 2),
    "sickle": False,
    "tail_pts": [(17, 6), (17.5, 14), (18, 22), (18, 30), (18, 37)],
    "tail_secs": [(4, 4), (3, 3), (2, 2), (2, 2)],
    "tail_fan": [(2, 5), (3, 9)],
    "saddle": (20, -6, 2, 6, 3.5, 4),
    "sit": {"drop": 9},
    "herbivore": True,
    "pattern": pattern,
    "extra": extra,
    "anim_speed": 1.3,
}


def build():
    return build_small(ID, P)
