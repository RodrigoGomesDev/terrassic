"""
Daspletosaurus torosus  (Late Cretaceous, Alberta and Montana)

Reference (Wikipedia, CMN 8506 and the Dinosaur Park material): length 8.5-9 m, hip height ~2.5 m, mass
2.5-3.8 t, skull ~1 m: massive and deep for its size, with rugose bosses behind the eyes (postorbital) that in
life carried horn-like scales, a thickened rugose nasal ridge, proportionally the largest teeth of any
tyrannosaurid, and arms a little longer than its cousins'. "Frightful lizard". Bonebeds suggest it moved and
hunted in small groups: in Terrassic, pairs.

In game: 9 m (TAMANHOS.md) on the large theropod rig, stockier than the Albertosaurus; forest green-brown with
big dark saddle blotches over the back and a cream belly. Males carry red-orange postorbital hornlets and a
darker back, females dull bosses and a warmer flank.
"""
import math
import large_theropod

ID = "daspletosaurus"


def pattern(model, tx, rgb, region):
    """Large dark saddle blotches over the back, fading down the flanks."""
    P = tx.P
    if tx.cube.tag != "skin":
        return rgb
    if region in ("dorsal", "flank"):
        blot = math.sin(P[2] * 2 * math.pi / 11.0 + 0.8 * math.sin(P[0] * 0.6)) * math.cos(P[1] * 0.35 + P[2] * 0.2)
        if region == "dorsal" and blot > 0.2:
            rgb = rgb * 0.74
        elif region == "flank" and tx.cy > 0.4 and blot > 0.5:
            rgb = rgb * 0.84
    return rgb


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
SPEC = dict(
    palette={"dorsal": "#4a5038", "flank": "#6f7352", "belly": "#d6ccaa", "limb": "#4e5240", "limb_top": "#5f6448",
             "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a", "tooth": "#efe7d2", "mouth": "#7c3430",
             "gum": "#5b2421", "eye": "#d8aa3a", "pupil": "#17110c", "dark": "#2c241b", "boss": "#6b4a3a"},
    # males: red-orange postorbital hornlets and darker back; females: dull bosses, warmer flanks
    sexes={"male": {"boss": "#a84a2a", "dorsal": "#414632"},
           "female": {"boss": "#6b5646", "flank": "#7c7a58"}},
    pattern=pattern,
    body=(29, 6),
    torso=[("hips", (-6, 21, -1, 6, 34, 12)), ("belly", (-7, 16, -13, 7, 33, 0)), ("chest", (-6, 16, -22, 6, 31, -12)),
           ("shoulders", (-5, 25, -26, 5, 33, -20)), ("back_ridge", (-3, 33, -13, 3, 35, 9)),
           ("belly_low", (-5, 14, -17, 5, 16, -5))],
    neck=([(29, -21), (32, -26), (33.5, -29)], [(9, 10), (8, 9)]), skull_tilt=-3,
    head=[  # massive deep skull for its size; postorbital bosses with hornlets; thick rugose nasal; big teeth
        dict(bone="skull", box=(-4.5, -1, -7, 4.5, 6, 1), name="cranium", paint=MOUTH_DOWN),
        dict(bone="skull", box=(-3, 0, -15, 3, 5, -7), name="snout",
             paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}),
        dict(bone="skull", box=(-2, 5, -14, 2, 6, -6), name="nasal_rugose", tag="boss"),
        dict(bone="skull", box=(3, 5, -6, 5, 7, -3), name="boss_l", tag="boss"),            # postorbital bosses
        dict(bone="skull", box=(-5, 5, -6, -3, 7, -3), name="boss_r", tag="boss"),
        dict(bone="skull", box=(3.5, 7, -5, 4.5, 8, -4), name="hornlet_l", tag="boss"),
        dict(bone="skull", box=(-4.5, 7, -5, -3.5, 8, -4), name="hornlet_r", tag="boss"),
        dict(bone="jaw", box=(-4, -5, -8, 4, 0, -1), name="jaw_back", paint=MOUTH_UP),
        dict(bone="jaw", box=(-2.5, -3, -14, 2.5, 0, -8), name="jaw_front",
             paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}, inflate=0.0),
    ],
    jaw_pivot=(0, -2), eyes=(1.5, 3.5, -5.0, 4.5),
    extra_decals=[{"kind": "spot", "bones": ["skull"], "pos": (1.4, 3.5, -15), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35},
                  {"kind": "spot", "bones": ["skull"], "pos": (-1.4, 3.5, -15), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35}],
    arm=(5.5, [(21, -18), (17.5, -19.5), (15.5, -22)], [(2, 3), (2, 2)],           # a little longer than its cousins'
         [("claw", (-1, -2, -1, 0, 0, 0)), ("claw", (0, -2, -1, 1, 0, 0))]),
    leg=(6.5, [(29, 6), (17.5, -1), (7, 7), (2, 4)], [(6, 10, -0.5), (4, 6, 1.0, "limb"), (3, 4, 0.0, "limb")],
         [("toe_mid", "limb", (-1, -2, -7, 1, 0, 1)), ("toe_out", "limb", (1, -2, -5, 2, 0, 1)),
          ("toe_in", "limb", (-2, -2, -5, -1, 0, 1)), ("claw_mid", "claw", (-1, -2, -8, 1, -1, -7)),
          ("claw_out", "claw", (1, -2, -6, 2, -1, -5)), ("claw_in", "claw", (-2, -2, -6, -1, -1, -5))]),
    tail=([(29, 10), (28.5, 21), (28.5, 32), (29, 42), (29.5, 51)], [(11, 11), (8, 8), (6, 6), (4, 4)]),
    saddle=((35, -5, 4, 8, 7), {"flap": 6}),
    sit=(12, 62, -118, 62, -6, {"tail1": (9, 0, 0), "tail2": (4, 0, 0), "tail3": (-2, 0, 0), "neck1": (-6, 0, 0), "skull": (4, 0, 0)}),
)


def build():
    return large_theropod.build(ID, SPEC)
