"""
Albertosaurus sarcophagus  (Late Cretaceous, Alberta)

Reference (Wikipedia, CMN 5600 and the Dry Island bonebed): length 8-10 m, hip height ~3 m, mass 1.7-2.5 t,
skull ~1 m: a lighter, longer-legged tyrannosaurid than the Daspletosaurus, with a longer, lower snout, a short
blunt horn (lacrimal crest) above each eye, and long shins and feet: the fast one. The Dry Island bonebed
(more than twenty animals of all ages together) is the best evidence of pack life in any tyrannosaur.

In game: 9.5 m (TAMANHOS.md) on the large theropod rig, lean and long-legged; slate blue-grey over the back,
tan flanks with a pale horizontal stripe from the shoulder to the hip, cream belly. Males carry ochre lacrimal
horns and a darker back; females brown horns and a lighter flank.
"""
import math
import large_theropod

ID = "albertosaurus"


def pattern(model, tx, rgb, region):
    """A pale lateral stripe along the flank at mid height, finer dark speckle over the back."""
    P = tx.P
    if tx.cube.tag != "skin":
        return rgb
    if region == "flank" and 0.42 < tx.cy < 0.58 and tx.cube.bone in ("body", "neck1", "neck2", "tail1", "tail2"):
        return rgb * 0.55 + tx.pal["belly"] * 0.45
    if region == "dorsal":
        h = math.sin(P[0] * 2.7 + P[2] * 2.1) * math.sin(P[1] * 1.9 - P[2] * 0.5)
        if h > 0.5:
            rgb = rgb * 0.82
    return rgb


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
SPEC = dict(
    palette={"dorsal": "#4e5560", "flank": "#8c7f66", "belly": "#dcd2b4", "limb": "#5a5a58", "limb_top": "#6e6c62",
             "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a", "tooth": "#efe7d2", "mouth": "#7c3430",
             "gum": "#5b2421", "eye": "#d6b040", "pupil": "#17110c", "dark": "#2c241b", "horn": "#7a6a46"},
    # males: ochre lacrimal horns and a darker back; females: brown horns, lighter flanks
    sexes={"male": {"horn": "#b48a3a", "dorsal": "#444b56"},
           "female": {"horn": "#6e5a44", "flank": "#998b70"}},
    pattern=pattern,
    body=(31, 6),
    torso=[("hips", (-5, 24, -1, 5, 36, 12)), ("belly", (-5.5, 19, -14, 5.5, 35, 0)), ("chest", (-5, 19, -23, 5, 33, -13)),
           ("shoulders", (-4, 27, -27, 4, 35, -21)), ("back_ridge", (-2, 35, -14, 2, 37, 10)),
           ("belly_low", (-4, 17, -18, 4, 19, -6))],
    neck=([(31, -22), (34.5, -27), (36, -31)], [(8, 9), (7, 8)]), skull_tilt=-3,
    head=[  # longer lower snout than the Daspletosaurus; short blunt horn over each eye
        dict(bone="skull", box=(-4, -1, -7, 4, 5, 1), name="cranium", paint=MOUTH_DOWN),
        dict(bone="skull", box=(-2.5, 0, -17, 2.5, 4, -7), name="snout",
             paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}),
        dict(bone="skull", box=(-1.5, 4, -15, 1.5, 5, -7), name="nasal_ridge"),
        dict(bone="skull", box=(2.5, 5, -8, 3.5, 7, -6), name="horn_l", tag="horn"),         # lacrimal horns
        dict(bone="skull", box=(-3.5, 5, -8, -2.5, 7, -6), name="horn_r", tag="horn"),
        dict(bone="jaw", box=(-3.5, -4, -8, 3.5, 0, -1), name="jaw_back", paint=MOUTH_UP),
        dict(bone="jaw", box=(-2, -3, -16, 2, 0, -8), name="jaw_front",
             paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}, inflate=0.0),
    ],
    jaw_pivot=(0, -2), eyes=(1.3, 3.0, -5.5, 4.0),
    extra_decals=[{"kind": "spot", "bones": ["skull"], "pos": (1.2, 3.0, -17), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35},
                  {"kind": "spot", "bones": ["skull"], "pos": (-1.2, 3.0, -17), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35}],
    arm=(5, [(23, -19), (19.5, -20.5), (17.5, -23)], [(2, 2), (1, 2)],
         [("claw", (-1, -2, -1, 0, 0, 0)), ("claw", (0, -2, -1, 1, 0, 0))]),
    leg=(6, [(31, 6), (18, -2), (6, 8), (2, 4)], [(5, 10, -0.5), (3, 6, 1.0, "limb"), (3, 4, 0.0, "limb")],  # long shins and feet
         [("toe_mid", "limb", (-1, -2, -7, 1, 0, 1)), ("toe_out", "limb", (1, -2, -5, 2, 0, 1)),
          ("toe_in", "limb", (-2, -2, -5, -1, 0, 1)), ("claw_mid", "claw", (-1, -2, -8, 1, -1, -7)),
          ("claw_out", "claw", (1, -2, -6, 2, -1, -5)), ("claw_in", "claw", (-2, -2, -6, -1, -1, -5))]),
    tail=([(31, 10), (30.5, 22), (30, 34), (30, 46), (30.5, 57)], [(9, 10), (7, 7), (5, 5), (3, 3)]),
    saddle=((37, -5, 4, 7, 6), {"flap": 5}),
    sit=(13, 62, -118, 62, -6, {"tail1": (9, 0, 0), "tail2": (4, 0, 0), "tail3": (-2, 0, 0), "neck1": (-6, 0, 0), "skull": (4, 0, 0)}),
)


def build():
    return large_theropod.build(ID, SPEC)
