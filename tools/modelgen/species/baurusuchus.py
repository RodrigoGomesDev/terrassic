"""
Baurusuchus salgadoensis  (Late Cretaceous, Turonian-Santonian; Adamantina Formation, Bauru Group, Brazil)

Reference (Wikipedia; Carvalho, Campos & Nobre 2005; Riff & Kellner 2011): a land-living crocodylomorph of ~3.5 m
with upright legs under the body and a deep, narrow, dog-like skull: big serrated blade teeth, two of them
hypertrophied canines, nostrils opening to the sides, a short tail, rows of small osteoderms. A running predator of
the hot Bauru plains, not a swimmer.

Built on the crocodylomorph archetype with the sprawl set to 70 degrees (legs nearly under the body). Modelled
~70 px long; SIZES scales it to 3.5 m. Sandy ochre with dark bands across the back; males redder with black bands,
females paler.
"""
import math
from rig import track, keys
import croc

ID = "baurusuchus"
BODY_Y = 14


def body_parts(m):
    # a deep, narrow body held high on the legs; a pale belly plate; two rows of small scutes
    m.box("body", (-5, 10, -10), (5, 18, 12), name="torso")
    m.box("body", (-4, 9, -9), (4, 10, 11), name="belly")
    for x0 in (-3, 1):
        m.box("body", (x0, 18, -9), (x0 + 2, 19, 11), name="scute_in", tag="scute")


def head(m, ay, az, abs_pitch):
    m.bone("skull", "head", (0, ay, az), (-abs_pitch, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # tall narrow skull: deep snout, brow ridges, blade teeth and two big canines at the front
    m.box("skull", *R(-3.5, -3, -8, 3.5, 4, 0), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3.5, 4, -6, -1.5, 5, -3), name="brow_l", tag="scute")
    m.box("skull", *R(1.5, 4, -6, 3.5, 5, -3), name="brow_r", tag="scute")
    m.box("skull", *R(-2.5, -3, -16, 2.5, 3, -8), name="snout", paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1, "freq": 0.8}})
    m.box("skull", *R(-2, -5, -14, -1, -3, -13), name="canine_l", tag="tooth_cube", paint={"axis": "-y"})
    m.box("skull", *R(1, -5, -14, 2, -3, -13), name="canine_r", tag="tooth_cube", paint={"axis": "-y"})
    m.bone("jaw", "skull", (0, ay - 3, az - 1))
    m.box("jaw", *R(-2.5, -6, -15, 2.5, -3, -1), name="jaw", paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1, "freq": 0.8}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3.5, ay + 2.2, az - 4.5), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3.5, ay + 2.2, az - 4.5), "r": 1.0, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "scute":
        col = tx.pal["scute"].copy()
        if tx.face == "up" and int(math.floor(P[2] + 100)) % 2 == 0:
            col = col * 0.8
        return col
    if tag == "skin":
        # narrow dark bands across the back that break into blotches on the flanks; a pale throat
        band = math.sin(P[2] * 0.8 + 0.3 * math.sin(P[0]))
        if region == "dorsal" and band > 0.55:
            rgb = tx.pal["band"].copy()
        elif region == "flank" and band > 0.8 and math.sin(P[1] * 1.7) > 0:
            rgb = tx.pal["band"].copy() * 1.2
        elif region == "belly" and (tx.cube.bone.startswith("neck") or tx.cube.bone in ("skull", "jaw")):
            rgb = tx.pal["throat"].copy()
        if (int(math.floor(P[2] * 1.1)) + int(math.floor(P[1] * 1.1))) % 2 == 0:
            rgb = rgb * 0.95
    elif tag == "limb":
        if region != "limb" or True:
            if math.sin(P[1] * 1.4) > 0.6:
                rgb = rgb * 0.85                                 # rings on the legs
    return rgb


# knocked out on its side: the top legs stretched out in front of the belly, the under legs folded forward
LIMP = {"neck1": (-6, 0, 0), "skull": (-2, 0, 0), "jaw": (-16, 0, 0),
        "tail1": (-4, 0, 0), "tail2": (-6, 0, 0), "tail3": (-6, 0, 0),
        "upperarm_l": (15, 0, -30), "upperarm_r": (25, 0, 30), "forearm_l": (0, 0, -40), "forearm_r": (0, 0, -30),
        "thigh_l": (-10, 0, -30), "thigh_r": (-20, 0, 30), "shin_l": (0, 0, -40), "shin_r": (0, 0, -30)}

SPEC = dict(
    palette={"dorsal": "#8a6a3c", "flank": "#b08c58", "belly": "#e2d2a8", "band": "#3e2a18", "throat": "#ecdfbe",
             "scute": "#5a4028",
             "limb": "#9a7a4a", "limb_top": "#a8885a",
             "claw": "#3a3228", "claw_base": "#4a4234", "claw_tip": "#2a241c",
             "tooth": "#efe8d2", "mouth": "#8a3844", "gum": "#5e262e",
             "tooth_cube": "#efe8d2", "tooth_cube_base": "#d8d0b8", "tooth_cube_tip": "#fbf8ee",
             "eye": "#c89a30", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#8a5a30", "flank": "#b4824a", "band": "#1e1410", "scute": "#4a3020"},
           "female": {"dorsal": "#9a8050", "flank": "#bca070", "band": "#5a4028", "throat": "#f0e6cc"}},
    pattern=pattern, body=(BODY_Y, 0), body_parts=body_parts, head=head,
    neck=dict(points=[(14, -10), (15, -16)], sections=[(8, 7)]),
    tail=dict(points=[(13, 12), (12, 22), (10, 31), (8, 39)], sections=[(8, 6), (5, 4), (3, 2)], crest=[(1, 2)]),
    legs=dict(front=dict(pivot=(5, 13, -6), upper=(6, 4, 4), sprawl=70, lower=(6, 3, 4), foot=(4, 5, 1, 1)),
              hind=dict(pivot=(5, 14, 8), upper=(7, 5, 5), sprawl=70, lower=(6, 4, 4), foot=(5, 6, 1, 1))),
    gait=dict(walk=(1.2, 26, 0.6, 3), run=(0.6, 38, 1.4, 4)),
    sit=dict(drop=8, upper=-75, lower=150, lower_roll=0, neck=-4, tail=-2),
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-20),
)


def build():
    return croc.build(ID, SPEC)
