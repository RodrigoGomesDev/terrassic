"""
Carnotaurus sastrei  (Late Cretaceous, Patagonia)

Reference (Wikipedia, MACN-CH 894, the only specimen, with skin impressions): length 7.5-8 m, hip height ~2.5 m,
mass 1.3-2.1 t. A short, deep, bull-like skull with two thick horns over the small eyes, projecting sideways and
up; the shortest arms of any large theropod (four stub fingers, no forearm to speak of); very long slender legs
and a huge tail-base muscle: the fastest of the big predators (sprint estimates 48-56 km/h). Skin of small
scales with rows of large conical scutes along the back and flanks (no feathers).

In game: 8 m (TAMANHOS.md) on the abelisaur rig (abelisaur.py): horns, stub arms, scute rows, charge animation.
Dark slate-olive with a cream belly; males carry rust-red horns and a flushed face, females bone-brown horns.
"""
import math
import abelisaur

ID = "carnotaurus"


def pattern(model, tx, rgb, region):
    """Fine dark speckle over back and flanks (small scales), nothing on the belly."""
    P = tx.P
    if tx.cube.tag != "skin":
        return rgb
    if region in ("dorsal", "flank"):
        h = math.sin(P[0] * 3.1 + P[2] * 1.9) * math.sin(P[1] * 2.3 + P[2] * 0.4)
        if h > 0.55:
            rgb = rgb * (0.82 if region == "dorsal" else 0.88)
    return rgb


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
SPEC = dict(
    palette={"dorsal": "#55503f", "flank": "#7d745a", "belly": "#d8cfae", "limb": "#5a5444", "limb_top": "#6e6650",
             "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a", "tooth": "#efe7d2", "mouth": "#7c3430",
             "gum": "#5b2421", "eye": "#c8a040", "pupil": "#17110c", "dark": "#2c241b", "horn_base": "#5a3a2c", "horn_tip": "#3a2a22",
             "scute": "#3c3a30", "face": "#6a4a3a"},
    # males: rust-red horns and a flushed face, darker back; females: bone-brown horns, lighter flanks
    sexes={"male": {"horn_base": "#8a3626", "horn_tip": "#5a2418", "face": "#7e4030", "dorsal": "#4b4738"},
           "female": {"horn_base": "#6a5040", "horn_tip": "#4a3a30", "face": "#7a6a52", "flank": "#8a8164"}},
    pattern=pattern,
    body=(30, 6),
    torso=[("hips", (-5, 22, -2, 5, 35, 12)), ("belly", (-5.5, 18, -14, 5.5, 34, 0)),
           ("chest", (-5, 19, -23, 5, 33, -12)), ("shoulders", (-4, 27, -26, 4, 34, -21)),
           ("back_ridge", (-2, 34, -14, 2, 36, 10)), ("belly_low", (-4, 16, -18, 4, 18, -6))],
    scutes=(4, 31, -12, 11, 3),
    neck=([(31, -22), (34, -26), (35, -29)], [(8, 9), (7, 8)]), skull_tilt=-4,
    head=[  # short deep bull skull, small eyes, two thick horns projecting sideways and up
        dict(bone="skull", box=(-4, -2, -6, 4, 5, 1), name="cranium", paint=MOUTH_DOWN),
        dict(bone="skull", box=(-3, -1, -12, 3, 4, -6), name="snout",
             paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}),
        dict(bone="skull", box=(-2, 4, -11, 2, 6, -4), name="face", tag="face"),
        dict(bone="skull", box=(3, 5, -5, 6, 7, -3), name="horn_l", tag="horn", paint={"axis": "+x"}),
        dict(bone="skull", box=(-6, 5, -5, -3, 7, -3), name="horn_r", tag="horn", paint={"axis": "-x"}),
        dict(bone="skull", box=(5, 7, -5, 7, 9, -4), name="horn_tip_l", tag="horn", paint={"axis": "+y"}),
        dict(bone="skull", box=(-7, 7, -5, -5, 9, -4), name="horn_tip_r", tag="horn", paint={"axis": "+y"}),
        dict(bone="jaw", box=(-3.5, -5, -7, 3.5, 0, -1), name="jaw_back", paint=MOUTH_UP),
        dict(bone="jaw", box=(-2.5, -3, -11, 2.5, 0, -7), name="jaw_front",
             paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}, inflate=0.0),
    ],
    jaw_pivot=(0, -2), eyes=(1.0, 2.5, -4.0, 4.0),
    extra_decals=[{"kind": "spot", "bones": ["skull"], "pos": (1.2, 2.5, -12), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35},
                  {"kind": "spot", "bones": ["skull"], "pos": (-1.2, 2.5, -12), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35}],
    arm=(4.5, [(27, -19), (24.5, -19.5), (23, -21)], [(2, 2), (1, 2)],                 # stub arms, four tiny fingers
         [("finger_a", (-1, -1, -1, 0, 0, 0)), ("finger_b", (0, -1, -1, 1, 0, 0))]),
    leg=(5.5, [(30, 6), (17, -2), (6, 8), (2, 4)], [(5, 9, -0.5), (3, 5, 1.0, "limb"), (3, 3, 0.0, "limb")],  # long slim legs
         [("toe_mid", "limb", (-1, -2, -6, 1, 0, 1)), ("toe_out", "limb", (1, -2, -4, 2, 0, 1)),
          ("toe_in", "limb", (-2, -2, -4, -1, 0, 1)), ("claw_mid", "claw", (-1, -2, -7, 1, -1, -6)),
          ("claw_out", "claw", (1, -2, -5, 2, -1, -4)), ("claw_in", "claw", (-2, -2, -5, -1, -1, -4))]),
    tail=([(30, 10), (29, 22), (28.5, 34), (28.5, 46), (29, 56)], [(10, 12), (7, 8), (5, 5), (3, 3)]),  # thick base
    saddle=((36, -4, 4, 7, 6), {"flap": 5}),
    sit=(12, 62, -118, 62, -6, {"tail1": (8, 0, 0), "tail2": (4, 0, 0), "tail3": (-2, 0, 0), "neck1": (-5, 0, 0), "skull": (4, 0, 0)}),
    charge=(0.6, 44),
)


def build():
    return abelisaur.build(ID, SPEC)
