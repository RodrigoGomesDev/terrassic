"""
Citipati osmolskae  (Late Cretaceous, Djadochta Formation, Mongolia)

Reference (Wikipedia; Clark, Norell & Barsbold 2001; "Big Mama" IGM 100/979): length ~2.5-3 m, mass ~75-85 kg, one
of the largest oviraptorids. A tall cassowary-like casque on a short deep toothless skull, a long neck, long legs,
long arms with big wing feathers, a short tail with a fan. Several skeletons were found sitting on their nests with
the arms spread over the eggs: the brooding dinosaur.

In game: 3 m (TAMANHOS.md) on the oviraptorosaur rig. Savanna / badlands omnivore tamed with eggs and seeds; the
brooder: sitting by eggs it spreads its wings over them (brood animation) and they hatch much faster
(docs/NINHOS.md). Cassowary colours: slate-black plumage with white wing bars and a pale belly, an orange casque
over a blue face patch on the males, a dull brown casque on the females.
"""
import math
from oviraptorosaur import build_ovi

ID = "citipati"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "feather":
        # black vanes with two white bars and white tips
        tip = (P[2] - tx.cube.frm[2]) / max(1.0, tx.cube.size[2])
        if tip > 0.82 or 0.3 < tip < 0.4 or 0.56 < tip < 0.66:
            return tx.pal["bar"].copy()
        return rgb
    if tag == "skin" and region in ("dorsal", "flank"):
        # a fine scaly sheen on the dark plumage
        fleck = math.sin(P[0] * 2.9 + P[2] * 1.9) * math.sin(P[1] * 2.2 + P[2] * 0.6)
        if region == "dorsal" and fleck > 0.5:
            rgb = rgb * 0.78
        elif region == "flank" and tx.cy > 0.5 and fleck > 0.65:
            rgb = rgb * 0.88
    return rgb


def extra(m, neck, tail):
    ax = P["arm_x"]
    ey, ez = P["arm_pts"][-1]
    for side, sx in (("l", 1), ("r", -1)):
        x = ax * sx
        for dx in (-1.0, 1.0):
            m.box(f"forearm_{side}", (x + dx - 0.5, ey - 3, ez - 2.5), (x + dx + 0.5, ey - 1, ez - 1.5),
                  tag="claw", name="finger", paint={"axis": "-y"})
    # plume ruff down the whole neck
    for seg in neck["segments"]:
        y0, z0 = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-1, y0 + 2, z0 - L), (1, y0 + 3, z0 + 1), tag="feather", name="ruff")


P = {
    "render_scale": 1.0,
    "palette": {
        "dorsal": "#34343c", "flank": "#52525e", "belly": "#d6d0c2",
        "limb": "#4a4a54", "limb_top": "#52525e",
        "claw": "#1c1a18", "claw_base": "#1c1a18", "claw_tip": "#5a554c",
        "feather": "#1a1a20", "bar": "#f4f2ec", "beak": "#4a3a30", "casque": "#d88a2a", "face": "#3a6ab8",
        "tooth": "#efe7d2", "mouth": "#6a2a2a", "gum": "#4a1c1c",
        "eye": "#e8c040", "pupil": "#120d08",
    },
    "sexes": {"male": {"casque": "#e08a24", "face": "#3a6ab8", "feather": "#141418", "eye": "#f0c838"},
              "female": {"casque": "#8a6a48", "face": "#5a6a80", "feather": "#34302e", "bar": "#dcd8cc", "dorsal": "#4a4846", "flank": "#6a665e"}},
    "hip": (22, 4),
    "torso": [
        ((-3.5, 16, -2), (3.5, 25, 7), "hips"),
        ((-4, 15, -11), (4, 25, -1), "belly"),
        ((-3.5, 16, -16), (3.5, 24, -10), "chest"),
        ((-3.5, 25, -11), (3.5, 26, 6), "back", "feather"),
    ],
    "neck_pts": [(23, -15), (26.5, -19), (30, -22), (33, -23)],
    "neck_secs": [(3, 4), (3, 3), (2, 3)],
    "head_pitch": 22,
    "head": {"cranium": (4, 4, 4), "snout": (3, 3, 3), "snout_y": 0, "jaw": (3, 2, 3),
             "eye": (1.0, -1.0), "eye_r": 1.3},
    "casque": (-1, 3, -4, 1, 9, 1),
    "head_extra": [dict(box=(-2.5, 0, -4, 2.5, 3, -2), tag="face", name="face", inflate=0.1)],
    "arm_x": 3.5,
    "arm_pts": [(19, -13), (14, -11), (13, -16)],
    "arm_secs": [(2, 2), (1, 2)],
    "wing": (11, 6),
    "leg_x": 3.0,
    "leg_pts": [(22, 4), (13, -1), (5, 4.5), (1, 3)],
    "leg_secs": [(3, 6, -0.5), (2, 2, 0.5, "limb"), (2, 2, 0.0, "limb")],
    "toes": (4, 2),
    "tail_pts": [(22, 7), (22.5, 14), (23, 21), (23, 27)],
    "tail_secs": [(5, 5), (4, 4), (3, 3)],
    "tail_fan": [(1, 9), (2, 14)],
    "sit": {"drop": 10},
    "brood": {"drop": 11, "arms": (-10, 0, -80)},
    "pattern": pattern,
    "extra": extra,
    "anim_speed": 1.1,
}


def build():
    return build_ovi(ID, P)
