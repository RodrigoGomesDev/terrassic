"""
Tarbosaurus bataar  (Late Cretaceous, Mongolia and China)

Reference (Wikipedia, PIN 551-1 and the Nemegt material): length 10-12 m, hip height ~3 m, mass 4-5 t, skull
up to 1.35 m: longer, lower and narrower than the T. rex's, with a locking joint in the lower jaw, the back of the
skull narrow (eyes less forward-facing), small lacrimal bumps, and the smallest arms of any tyrannosaurid
relative to size (two fingers). The top predator of the Nemegt river plains and the Gobi, with a heavier
build than the Albertosaurus: the sturdy Asian cousin.

In game: 12 m (TAMANHOS.md) on the large theropod rig; sandy grey-brown of the Gobi with a continuous dark
stripe down the spine and faint oblique flank bars, pale belly. Males wear a dark cap over the skull, females a
lighter one and warmer flanks.
"""
import math
import large_theropod

ID = "tarbosaurus"


def pattern(model, tx, rgb, region):
    """A dark spine stripe the whole length of the animal, with faint oblique bars down the flanks."""
    P = tx.P
    if tx.cube.tag != "skin":
        return rgb
    if region == "dorsal" and abs(P[0]) < 1.6:
        return rgb * 0.7
    if region in ("dorsal", "flank"):
        bar = math.sin(P[2] * 2 * math.pi / 7.5 + P[1] * 0.35)
        if region == "dorsal" and bar > 0.55:
            rgb = rgb * 0.84
        elif region == "flank" and tx.cy > 0.45 and bar > 0.7:
            rgb = rgb * 0.9
    return rgb


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
SPEC = dict(
    palette={"dorsal": "#5f5648", "flank": "#8a7c62", "belly": "#d4c7a6", "limb": "#5a5042", "limb_top": "#75694f",
             "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a", "tooth": "#efe7d2", "mouth": "#7c3430",
             "gum": "#5b2421", "eye": "#d2a63a", "pupil": "#17110c", "dark": "#2c241b", "cap": "#4a3f33"},
    # males: dark cap over the skull and a darker back; females: lighter cap, warmer flanks
    sexes={"male": {"cap": "#352822", "dorsal": "#554c3f"},
           "female": {"cap": "#6b5a46", "flank": "#968566"}},
    pattern=pattern,
    body=(30, 6),
    torso=[("hips", (-6, 22, -1, 6, 35, 13)), ("belly", (-7, 17, -14, 7, 34, 0)), ("chest", (-6, 17, -24, 6, 32, -13)),
           ("shoulders", (-5, 26, -28, 5, 34, -22)), ("back_ridge", (-3, 34, -14, 3, 36, 10)),
           ("belly_low", (-5, 15, -19, 5, 17, -5))],
    neck=([(30, -23), (33, -28), (34.5, -32)], [(9, 10), (8, 9)]), skull_tilt=-3,
    head=[  # longer, lower, narrower skull than the rex; narrow at the back; small lacrimal bumps; deep jaw
        dict(bone="skull", box=(-4, -1, -8, 4, 5, 1), name="cranium", paint=MOUTH_DOWN),
        dict(bone="skull", box=(-2.5, 0, -18, 2.5, 4, -8), name="snout",
             paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}),
        dict(bone="skull", box=(-1.5, 4, -16, 1.5, 5, -7), name="nasal_ridge", tag="cap"),
        dict(bone="skull", box=(-4, 5, -7, 4, 6, -1), name="cap", tag="cap"),
        dict(bone="skull", box=(2, 4, -11, 3, 6, -9), name="lacrimal_l", tag="cap"),
        dict(bone="skull", box=(-3, 4, -11, -2, 6, -9), name="lacrimal_r", tag="cap"),
        dict(bone="jaw", box=(-3.5, -6, -9, 3.5, 0, -1), name="jaw_back", paint=MOUTH_UP),
        dict(bone="jaw", box=(-2, -3, -17, 2, 0, -9), name="jaw_front",
             paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}, inflate=0.0),
    ],
    jaw_pivot=(0, -2), eyes=(1.4, 3.0, -6.0, 4.0),
    extra_decals=[{"kind": "spot", "bones": ["skull"], "pos": (1.3, 3.2, -18), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35},
                  {"kind": "spot", "bones": ["skull"], "pos": (-1.3, 3.2, -18), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35}],
    arm=(5.5, [(22, -20), (19.5, -21), (18, -23)], [(2, 2), (1, 2)],                 # the smallest tyrannosaur arms
         [("claw", (-1, -2, -1, 0, 0, 0)), ("claw", (0, -2, -1, 1, 0, 0))]),
    leg=(6.5, [(30, 6), (18, -1), (7, 8), (2, 4)], [(6, 10, -0.5), (4, 6, 1.0, "limb"), (3, 4, 0.0, "limb")],
         [("toe_mid", "limb", (-1, -2, -7, 1, 0, 1)), ("toe_out", "limb", (1, -2, -5, 2, 0, 1)),
          ("toe_in", "limb", (-2, -2, -5, -1, 0, 1)), ("claw_mid", "claw", (-1, -2, -8, 1, -1, -7)),
          ("claw_out", "claw", (1, -2, -6, 2, -1, -5)), ("claw_in", "claw", (-2, -2, -6, -1, -1, -5))]),
    tail=([(30, 11), (29.5, 23), (29.5, 35), (30, 46), (30.5, 56)], [(11, 11), (8, 8), (6, 6), (4, 4)]),
    saddle=((36, -6, 4, 8, 7), {"flap": 6}),
    sit=(13, 62, -118, 62, -6, {"tail1": (9, 0, 0), "tail2": (4, 0, 0), "tail3": (-2, 0, 0), "neck1": (-6, 0, 0), "skull": (4, 0, 0)}),
)


def build():
    return large_theropod.build(ID, SPEC)
