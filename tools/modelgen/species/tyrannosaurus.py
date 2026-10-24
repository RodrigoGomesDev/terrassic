"""
Tyrannosaurus rex  (Late Cretaceous, North America)

Reference (Wikipedia, Sue / FMNH PR 2081 and later estimates):
  length 12.3-12.8 m, hip height 3.7-4.0 m, mass 5.4-8.8 t, skull up to 1.52 m,
  arms ~1 m with two fingers, body held horizontal with the tail as a
  counterweight, skull very wide at the back with a narrow snout (forward
  facing eyes), mostly scaly skin (scale impressions on neck, hip and tail).

In game: scale ~0.55 (1 m = ~8.8 px)  ->  ~6.6 blocks long, hips ~2.3 blocks.
"""
import math
import large_theropod

ID = "tyrannosaurus"


def pattern(model, tx, rgb, region):
    """Dark bands across the back, fading down the flanks."""
    P = tx.P
    if tx.cube.tag == "dorsal_dark":
        return rgb
    if region in ("dorsal", "flank") and tx.cube.tag == "skin":
        band = math.sin(P[2] * 2 * math.pi / 8.5 + 0.6 * math.sin(P[0] * 0.5))
        k = 0.0
        if region == "dorsal":
            k = 0.22 if band > 0.35 else 0.0
        elif tx.cy > 0.5:
            k = 0.14 if band > 0.55 else 0.0
        rgb = rgb * (1 - k)
    return rgb


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
SPEC = dict(
    palette={"dorsal": "#4b3f30", "flank": "#6f5b41", "belly": "#cdb994", "limb": "#514232", "limb_top": "#6a5640",
             "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a", "tooth": "#efe7d2", "mouth": "#7c3430",
             "gum": "#5b2421", "eye": "#e2a93b", "pupil": "#17110c", "dark": "#2c241b", "dorsal_dark": "#3d3227"},
    # males: rusty-red brow horns and darker back; females: plain
    sexes={"male": {"dorsal_dark": "#7a3424", "dorsal": "#45392b"},
           "female": {"dorsal_dark": "#4b3f30", "flank": "#7a6548"}},
    pattern=pattern,
    body=(31, 6),
    torso=[("hips", (-6, 23, -1, 6, 36, 13)), ("belly", (-7, 17, -14, 7, 35, 0)), ("chest", (-6, 17, -24, 6, 33, -13)),
           ("shoulders", (-5, 27, -28, 5, 35, -22)), ("back_ridge", (-4, 35, -14, 4, 37, 10)),
           ("belly_low", (-5, 15, -19, 5, 17, -5))],
    neck=([(31, -23), (34, -28), (35.5, -32)], [(10, 11), (9, 10)]), skull_tilt=-3,
    head=[  # deep skull, wide at the back, narrow snout; brow horns
        dict(bone="skull", box=(-5, -1, -8, 5, 6, 1), name="cranium", paint=MOUTH_DOWN),
        dict(bone="skull", box=(-3, 0, -16, 3, 5, -8), name="snout",
             paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}),
        dict(bone="skull", box=(-2, 5, -14, 2, 6, -7), name="nasal_ridge"),
        dict(bone="skull", box=(3, 6, -7, 5, 7, -4), name="brow_l", tag="dorsal_dark"),       # postorbital bosses
        dict(bone="skull", box=(-5, 6, -7, -3, 7, -4), name="brow_r", tag="dorsal_dark"),
        dict(bone="skull", box=(2.5, 6, -10, 3.5, 8, -8), name="horn_l", tag="dorsal_dark"),  # lacrimal horns
        dict(bone="skull", box=(-3.5, 6, -10, -2.5, 8, -8), name="horn_r", tag="dorsal_dark"),
        dict(bone="jaw", box=(-4.5, -5, -9, 4.5, 0, -1), name="jaw_back", paint=MOUTH_UP),
        dict(bone="jaw", box=(-2.5, -3, -15, 2.5, 0, -9), name="jaw_front",
             paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}, inflate=0.0),
    ],
    jaw_pivot=(0, -2), eyes=(1.5, 3.5, -5.5, 4.5),
    extra_decals=[{"kind": "spot", "bones": ["skull"], "pos": (1.5, 3.5, -16), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35},
                  {"kind": "spot", "bones": ["skull"], "pos": (-1.5, 3.5, -16), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35}],
    arm=(5.5, [(23, -20), (19.5, -21.5), (17.5, -24)], [(2, 3), (2, 2)],          # tiny two-fingered arms
         [("claw", (-1, -2, -1, 0, 0, 0)), ("claw", (0, -2, -1, 1, 0, 0))]),
    leg=(6.5, [(31, 6), (19, -1), (7, 8), (2, 4)], [(6, 10, -0.5), (4, 6, 1.0, "limb"), (3, 4, 0.0, "limb")],
         [("toe_mid", "limb", (-1, -2, -7, 1, 0, 1)), ("toe_out", "limb", (1, -2, -5, 2, 0, 1)),
          ("toe_in", "limb", (-2, -2, -5, -1, 0, 1)), ("claw_mid", "claw", (-1, -2, -8, 1, -1, -7)),
          ("claw_out", "claw", (1, -2, -6, 2, -1, -5)), ("claw_in", "claw", (-2, -2, -6, -1, -1, -5))]),
    tail=([(31, 11), (30.5, 23), (30.5, 35), (31, 46), (31.5, 57)], [(11, 11), (8, 8), (6, 6), (4, 4)]),
    saddle=((37, -6, 4, 8, 7), {"flap": 6}),
    sit=(13, 62, -118, 62, -6, {"tail1": (9, 0, 0), "tail2": (4, 0, 0), "tail3": (-2, 0, 0), "neck1": (-6, 0, 0), "skull": (4, 0, 0)}),
)


def build():
    return large_theropod.build(ID, SPEC)
