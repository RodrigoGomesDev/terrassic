"""
Carcharodontosaurus saharicus  (Late Cretaceous, North Africa)

Reference (Wikipedia, SGM-Din 1 skull and estimates): length 12-13.3 m, mass 6-15 t, skull ~1.6 m, deep and
boxy rather than long and low, with rugose bosses over the brow (lacrimal/postorbital) and a thickened nasal
ridge; blade teeth with serrations like a shark's ("shark-toothed lizard"); three-fingered arms; a long tail.
Hunted the river plains of the Sahara alongside the Spinosaurus.

In game: 12.5 m (TAMANHOS.md), a touch shorter than the Giganotosaurus but deeper-headed and with a dark
"mask" over the brow; Saharan red-brown with pale belly and dark vertical stripes down the flanks and tail.
Males wear a black mask and darker back; females a lighter mask and warmer flanks.
"""
import math
import large_theropod

ID = "carcharodontosaurus"


def pattern(model, tx, rgb, region):
    """Vertical dark stripes down the flanks, stronger on the back, continuing along the tail."""
    P = tx.P
    if tx.cube.tag != "skin":
        return rgb
    if region in ("dorsal", "flank"):
        band = math.sin(P[2] * 2 * math.pi / 6.0 + 0.3 * math.sin(P[1] * 0.9))
        if region == "dorsal" and band > 0.3:
            rgb = rgb * 0.78
        elif region == "flank" and tx.cy > 0.3 and band > 0.5:
            rgb = rgb * 0.84
    return rgb


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
SPEC = dict(
    palette={"dorsal": "#7a4a34", "flank": "#a9775a", "belly": "#e0d0b0", "limb": "#6e4434", "limb_top": "#8a5a44",
             "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a", "tooth": "#efe7d2", "mouth": "#7c3430",
             "gum": "#5b2421", "eye": "#c9a23c", "pupil": "#17110c", "dark": "#2c241b", "mask": "#4a2a22"},
    # males: black brow mask and darker back; females: lighter mask, warmer flanks
    sexes={"male": {"mask": "#2e1c18", "dorsal": "#6e4030"},
           "female": {"mask": "#7a5a48", "flank": "#b48868"}},
    pattern=pattern,
    body=(31, 6),
    torso=[("hips", (-5.5, 23, -1, 5.5, 36, 13)), ("belly", (-6.5, 18, -15, 6.5, 35, 0)),
           ("chest", (-5.5, 18, -25, 5.5, 33, -13)), ("shoulders", (-4.5, 27, -29, 4.5, 35, -23)),
           ("back_ridge", (-3, 35, -17, 3, 37, 11)), ("belly_low", (-4.5, 16, -20, 4.5, 18, -6))],
    neck=([(31, -24), (34.5, -29), (36, -33)], [(9, 10), (8, 9)]), skull_tilt=-3,
    head=[  # deep boxy skull, bosses over the brow, thick nasal ridge; shark teeth
        dict(bone="skull", box=(-4.5, -1, -8, 4.5, 6, 1), name="cranium", paint=MOUTH_DOWN),
        dict(bone="skull", box=(-3, 0, -18, 3, 5, -8), name="snout",
             paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}),
        dict(bone="skull", box=(-1.5, 5, -17, 1.5, 6, -9), name="nasal", tag="mask"),
        dict(bone="skull", box=(2.5, 6, -10, 3.5, 8, -7), name="boss_l", tag="mask"),        # lacrimal bosses
        dict(bone="skull", box=(-3.5, 6, -10, -2.5, 8, -7), name="boss_r", tag="mask"),
        dict(bone="skull", box=(3, 5, -8, 5, 7, -4), name="brow_l", tag="mask"),           # postorbital brow
        dict(bone="skull", box=(-5, 5, -8, -3, 7, -4), name="brow_r", tag="mask"),
        dict(bone="jaw", box=(-4, -5, -9, 4, 0, -1), name="jaw_back", paint=MOUTH_UP),
        dict(bone="jaw", box=(-2.5, -3, -17, 2.5, 0, -9), name="jaw_front",
             paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}, inflate=0.0),
    ],
    jaw_pivot=(0, -2), eyes=(1.4, 3.5, -5.5, 4.0),
    extra_decals=[{"kind": "spot", "bones": ["skull"], "pos": (1.3, 3.5, -18), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35},
                  {"kind": "spot", "bones": ["skull"], "pos": (-1.3, 3.5, -18), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35}],
    arm=(5.5, [(23, -21), (19, -22), (16, -25)], [(2, 3), (2, 2)],                 # three-fingered arms
         [("claw_in", (-1.5, -2, -1, -0.5, 0, 0)), ("claw_mid", (-0.5, -3, -2, 0.5, 0, -1)),
          ("claw_out", (0.5, -2, -1, 1.5, 0, 0))]),
    leg=(6.5, [(31, 6), (19, -1), (7, 8), (2, 4)], [(5, 10, -0.5), (4, 6, 1.0, "limb"), (3, 4, 0.0, "limb")],
         [("toe_mid", "limb", (-1, -2, -7, 1, 0, 1)), ("toe_out", "limb", (1, -2, -5, 2, 0, 1)),
          ("toe_in", "limb", (-2, -2, -5, -1, 0, 1)), ("claw_mid", "claw", (-1, -2, -8, 1, -1, -7)),
          ("claw_out", "claw", (1, -2, -6, 2, -1, -5)), ("claw_in", "claw", (-2, -2, -6, -1, -1, -5))]),
    tail=([(31, 11), (30, 23), (29.5, 35), (29.5, 47), (30, 59)], [(10, 11), (8, 8), (6, 6), (3, 3)]),
    saddle=((37, -6, 4, 8, 7), {"flap": 6}),
    sit=(13, 62, -118, 62, -6, {"tail1": (9, 0, 0), "tail2": (4, 0, 0), "tail3": (-2, 0, 0), "neck1": (-6, 0, 0), "skull": (4, 0, 0)}),
)


def build():
    return large_theropod.build(ID, SPEC)
