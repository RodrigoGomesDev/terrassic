"""
Majungasaurus crenatissimus  (Late Cretaceous, Madagascar)

Reference (Wikipedia, FMNH PR 2100 and the Maevarano material): length 6-7 m (up to 8 m), hip height ~2 m,
mass ~1.1 t. An abelisaurid with a very short, deep, broad snout, thick rugose skull bones, a single blunt dome
horn on the skull roof (the fused frontals), tiny eyes, the stub arms of the family, short strong legs and a
long tail: not a long-distance runner but a burst ambusher. Tooth marks on its own bones make it the one
dinosaur with firm evidence of cannibalism.

In game: 7.5 m (TAMANHOS.md) on the abelisaur rig (abelisaur.py): dome horn, stub arms, scute rows, the charge.
Madagascar rust-red with charcoal bands over back and tail and a cream belly. Males carry an orange dome and
blacker bands, females a brown dome and softer bands.
"""
import math
import abelisaur

ID = "majungasaurus"


def pattern(model, tx, rgb, region):
    """Charcoal bands across the back and down the tail, fading on the flanks."""
    P = tx.P
    if tx.cube.tag != "skin":
        return rgb
    if region in ("dorsal", "flank"):
        band = math.sin(P[2] * 2 * math.pi / 6.5 + 0.5 * math.sin(P[0] * 0.7))
        if region == "dorsal" and band > 0.25:
            rgb = rgb * 0.6 + tx.pal["band"] * 0.4
        elif region == "flank" and tx.cy > 0.4 and band > 0.55:
            rgb = rgb * 0.8 + tx.pal["band"] * 0.2
    return rgb


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
SPEC = dict(
    palette={"dorsal": "#7a3f2c", "flank": "#a8694a", "belly": "#dccba8", "limb": "#6e3e30", "limb_top": "#8a5440",
             "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a", "tooth": "#efe7d2", "mouth": "#7c3430",
             "gum": "#5b2421", "eye": "#d6a83c", "pupil": "#17110c", "dark": "#2c241b", "horn_base": "#8a5a2c", "horn_tip": "#6a4a24",
             "scute": "#4a2c22", "face": "#8a4a36", "band": "#2e2420"},
    # males: orange dome and blacker bands; females: brown dome, softer bands and lighter flanks
    sexes={"male": {"horn_base": "#c8782a", "horn_tip": "#a85a1c", "band": "#231c18", "dorsal": "#703a28"},
           "female": {"horn_base": "#7a5a3c", "horn_tip": "#5a4030", "band": "#4a3a30", "flank": "#b07a5a"}},
    pattern=pattern,
    body=(27, 6),
    torso=[("hips", (-5, 20, -2, 5, 32, 11)), ("belly", (-5.5, 16, -13, 5.5, 31, 0)),
           ("chest", (-5, 17, -21, 5, 30, -11)), ("shoulders", (-4, 25, -24, 4, 31, -19)),
           ("back_ridge", (-2, 31, -13, 2, 33, 9)), ("belly_low", (-4, 14, -16, 4, 16, -6))],
    scutes=(4, 28, -11, 10, 3),
    neck=([(28, -20), (31, -24), (32, -27)], [(8, 9), (7, 8)]), skull_tilt=-4,
    head=[  # very short, deep, broad snout; single dome horn on the skull roof; tiny eyes
        dict(bone="skull", box=(-4, -2, -6, 4, 5, 1), name="cranium", paint=MOUTH_DOWN),
        dict(bone="skull", box=(-3.5, -1, -11, 3.5, 4, -6), name="snout",
             paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}),
        dict(bone="skull", box=(-2.5, 4, -10, 2.5, 6, -4), name="face", tag="face"),
        dict(bone="skull", box=(-2, 5, -5, 2, 8, -2), name="dome", tag="horn", paint={"axis": "+y"}),
        dict(bone="skull", box=(-1, 8, -5, 1, 9, -3), name="dome_tip", tag="horn", paint={"axis": "+y"}),
        dict(bone="jaw", box=(-3.5, -5, -7, 3.5, 0, -1), name="jaw_back", paint=MOUTH_UP),
        dict(bone="jaw", box=(-3, -3, -10, 3, 0, -7), name="jaw_front",
             paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}, inflate=0.0),
    ],
    jaw_pivot=(0, -2), eyes=(1.0, 2.5, -4.0, 4.0),
    extra_decals=[{"kind": "spot", "bones": ["skull"], "pos": (1.4, 2.5, -11), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35},
                  {"kind": "spot", "bones": ["skull"], "pos": (-1.4, 2.5, -11), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35}],
    arm=(4.5, [(24, -17), (21.5, -17.5), (20, -19)], [(2, 2), (1, 2)],
         [("finger_a", (-1, -1, -1, 0, 0, 0)), ("finger_b", (0, -1, -1, 1, 0, 0))]),
    leg=(5.5, [(27, 6), (16, -1), (6, 7), (2, 4)], [(5, 9, -0.5), (4, 5, 1.0, "limb"), (3, 3, 0.0, "limb")],  # shorter, stronger legs
         [("toe_mid", "limb", (-1, -2, -6, 1, 0, 1)), ("toe_out", "limb", (1, -2, -4, 2, 0, 1)),
          ("toe_in", "limb", (-2, -2, -4, -1, 0, 1)), ("claw_mid", "claw", (-1, -2, -7, 1, -1, -6)),
          ("claw_out", "claw", (1, -2, -5, 2, -1, -4)), ("claw_in", "claw", (-2, -2, -5, -1, -1, -4))]),
    tail=([(27, 9), (26.5, 21), (26, 33), (26, 45), (26.5, 56)], [(10, 11), (7, 8), (5, 5), (3, 3)]),  # long tail
    saddle=((33, -4, 4, 7, 6), {"flap": 5}),
    sit=(11, 62, -118, 62, -6, {"tail1": (8, 0, 0), "tail2": (4, 0, 0), "tail3": (-2, 0, 0), "neck1": (-5, 0, 0), "skull": (4, 0, 0)}),
    charge=(0.55, 46),
)


def build():
    return abelisaur.build(ID, SPEC)
