"""
Giganotosaurus carolinii  (Late Cretaceous, Patagonia)

Reference (Wikipedia, MUCPv-Ch1 holotype and the larger MUCPv-95 dentary):
  length 12-13 m, hip height ~3.7 m, mass 6-8 t (some estimates higher), skull 1.6-1.8 m: long, low and
  narrow, with rugose lacrimal/postorbital ridges running along the top of the snout instead of the T. rex brow
  bosses; blade-like serrated teeth for slicing rather than crushing; three-fingered arms longer than a
  tyrannosaur's; a long, slender tail. Lived in dry plains and open woodland, likely in loose groups.

In game: 13 m (TAMANHOS.md), a little longer and lower than the T. rex, lean build; dry-country ochre with dark
mottling on the back and banded tail. Males carry a rust-red skull ridge, females a bone-brown one.
"""
import math
import large_theropod

ID = "giganotosaurus"


def pattern(model, tx, rgb, region):
    """Irregular dark mottling over the back, fading down the flanks; dark bands along the tail."""
    P = tx.P
    if tx.cube.tag == "ridge":
        return rgb
    if tx.cube.tag != "skin":
        return rgb
    if tx.cube.bone.startswith("tail"):
        band = math.sin(P[2] * 2 * math.pi / 7.0 + 0.4 * math.sin(P[1] * 0.7))
        if band > 0.45 and (region == "dorsal" or (region == "flank" and tx.cy > 0.35)):
            return rgb * 0.8
        return rgb
    if region in ("dorsal", "flank"):
        h = math.sin(P[0] * 1.7 + P[2] * 2.3) * math.cos(P[2] * 0.9 - P[1] * 0.6)
        if region == "dorsal" and h > 0.4:
            rgb = rgb * 0.76
        elif region == "flank" and tx.cy > 0.5 and h > 0.62:
            rgb = rgb * 0.86
    return rgb


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
SPEC = dict(
    palette={"dorsal": "#6b5a3a", "flank": "#8c7650", "belly": "#d6c6a2", "limb": "#5e4e36", "limb_top": "#7a6646",
             "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a", "tooth": "#efe7d2", "mouth": "#7c3430",
             "gum": "#5b2421", "eye": "#d9b04a", "pupil": "#17110c", "dark": "#2c241b", "ridge": "#5e4c38"},
    # males: rust-red skull ridges and a darker back; females: bone-brown ridges, paler flanks
    sexes={"male": {"ridge": "#8a3a28", "dorsal": "#5f4e32"},
           "female": {"ridge": "#5e4c38", "flank": "#968060"}},
    pattern=pattern,
    body=(33, 6),
    torso=[("hips", (-5.5, 24, -1, 5.5, 37, 13)), ("belly", (-6.5, 19, -15, 6.5, 36, 0)),
           ("chest", (-5.5, 19, -25, 5.5, 34, -13)), ("shoulders", (-4.5, 28, -29, 4.5, 36, -23)),
           ("back_ridge", (-3, 36, -16, 3, 38, 11)), ("belly_low", (-4.5, 17, -20, 4.5, 19, -6))],
    neck=([(32, -24), (35, -30), (36.5, -35)], [(9, 10), (8, 9)]), skull_tilt=-2,
    head=[  # long, low, narrow skull with ridges along the top; blade teeth
        dict(bone="skull", box=(-4.5, -1, -7, 4.5, 5, 1), name="cranium", paint=MOUTH_DOWN),
        dict(bone="skull", box=(-2.5, 0, -20, 2.5, 4, -7), name="snout",
             paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}),
        dict(bone="skull", box=(-1.5, 4, -19, 1.5, 5, -10), name="nasal"),
        dict(bone="skull", box=(2.0, 4, -17, 3.0, 6, -5), name="ridge_l", tag="ridge"),     # lacrimal/postorbital ridges
        dict(bone="skull", box=(-3.0, 4, -17, -2.0, 6, -5), name="ridge_r", tag="ridge"),
        dict(bone="skull", box=(-3.5, 5, -6, 3.5, 6, -1), name="crown", tag="ridge"),
        dict(bone="jaw", box=(-4, -5, -8, 4, 0, -1), name="jaw_back", paint=MOUTH_UP),
        dict(bone="jaw", box=(-2, -3, -19, 2, 0, -8), name="jaw_front",
             paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}, inflate=0.0),
    ],
    jaw_pivot=(0, -2), eyes=(1.3, 3.0, -5.0, 4.0),
    extra_decals=[{"kind": "spot", "bones": ["skull"], "pos": (1.2, 3.2, -20), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35},
                  {"kind": "spot", "bones": ["skull"], "pos": (-1.2, 3.2, -20), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35}],
    arm=(5.5, [(24, -21), (19.5, -22), (16, -25)], [(2, 3), (2, 2)],            # three-fingered arms, longer than a rex's
         [("claw_in", (-1.5, -2, -1, -0.5, 0, 0)), ("claw_mid", (-0.5, -3, -2, 0.5, 0, -1)),
          ("claw_out", (0.5, -2, -1, 1.5, 0, 0))]),
    leg=(6.5, [(33, 6), (20, -1), (7.5, 8), (2, 4)], [(5, 10, -0.5), (4, 6, 1.0, "limb"), (3, 4, 0.0, "limb")],
         [("toe_mid", "limb", (-1, -2, -7, 1, 0, 1)), ("toe_out", "limb", (1, -2, -5, 2, 0, 1)),
          ("toe_in", "limb", (-2, -2, -5, -1, 0, 1)), ("claw_mid", "claw", (-1, -2, -8, 1, -1, -7)),
          ("claw_out", "claw", (1, -2, -6, 2, -1, -5)), ("claw_in", "claw", (-2, -2, -6, -1, -1, -5))]),
    tail=([(33, 11), (32, 24), (31.5, 37), (31.5, 50), (32, 63)], [(10, 10), (7, 7), (5, 5), (3, 3)]),
    saddle=((39, -6, 4, 8, 7), {"flap": 6}),
    sit=(13, 62, -118, 62, -6, {"tail1": (9, 0, 0), "tail2": (4, 0, 0), "tail3": (-2, 0, 0), "neck1": (-6, 0, 0), "skull": (3, 0, 0)}),
)


def build():
    return large_theropod.build(ID, SPEC)
