"""
Baurusuchus salgadoensis  (Late Cretaceous, Turonian-Santonian; Adamantina Formation, Bauru Group, Brazil)

Reference:
  - Size and build (Carvalho, Campos & Nobre 2005; Riff & Kellner 2011; Godoy et al. 2016): a land-living
    baurusuchid crocodylomorph of ~3.5 m with long upright legs held under the body (a fast walker and runner of
    the hot, dry Bauru plains, not a swimmer), a deep narrow trunk, a short tail.
  - Skull: tall, narrow and short-snouted, almost dog-like, with ziphodont (flattened, serrated, blade-like) teeth
    in a reduced count; an enlarged "canine" in the upper jaw and a bigger one at the front of the lower jaw that
    fits outside the upper jaw in a notch; nostrils opening forward and to the sides at the snout tip; heavy
    brows over the eyes. Teeth marks suggest it subdued prey by bite and shake.
  - Armour: two paired rows of small osteoderms down the back.
  - Colour unknown; kept from the old model: sandy ochre with dark bands across the back; males redder with black
    bands, females paler.

v2x (2026-10-25, remaster at the T. rex v3 level): its own geometry on the crocodylomorph archetype (species/
croc.py, legs at a 70 degree sprawl, the animation set), at the same ~20 px = 1 m as the old model (no position
scaling); the head ~1.4x the real proportion. Each osteoderm is its own cube.
"""
import math
from rig import track, keys
from groundfit import fit_to_ground
import croc

ID = "baurusuchus"
BODY_Y = 14


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
TORSO = [(-10, -4, 4.5, 10.5, 17.5), (-4, 8, 5, 10, 18), (8, 13, 4.5, 10.5, 17.5)]   # (z0, z1, half w, y0, y1)
SCUTE_ROWS = [(1.5, 2, 1), (3.5, 1, 1)]           # (x centre, width, height): one cube every 3 px, 2 px long


def body_parts(m):
    # a deep, narrow body held high on the legs; a pale belly plate; two paired rows of small scutes
    for z0, z1, hw, y0, y1 in TORSO:
        m.box("body", (-hw, y0, z0), (hw, y1, z1), name="torso")
        for xc, w, h in SCUTE_ROWS:
            for s in (1, -1):
                for z in range(z0 + 1, z1 - 1, 3):
                    a, b = sorted((s * (xc - w / 2), s * (xc + w / 2)))
                    m.box("body", (a, y1 - 0.5, z), (b, y1 - 0.5 + h, z + 2), name="osteoderm", tag="scute")
    m.box("body", (-4, 9, -8), (4, 10, 11), name="belly")


def head(m, ay, az, abs_pitch):
    m.bone("skull", "head", (0, ay, az), (-abs_pitch, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    UT = dict(MOUTH_DOWN, teeth={"edge": "bottom", "rows": 1, "faces": ("east", "west"), "freq": 0.8})
    LT = dict(MOUTH_UP, teeth={"edge": "top", "rows": 1, "faces": ("east", "west"), "freq": 0.8})
    # tall narrow skull, short deep snout, heavy brows, the nostrils at the tip
    m.box("skull", *R(-3.5, -3, -6, 3.5, 4, 0), name="cranium", paint=MOUTH_DOWN)
    m.box("skull", *R(-1.5, 4, -5, 1.5, 5, 0), name="skull_table")
    for s in (1, -1):
        a, b = sorted((s * 1.5, s * 3.5))
        m.box("skull", *R(a, 4, -6, b, 6, -2), name="brow", tag="scute")
    m.box("skull", *R(-2.5, -3, -11, 2.5, 3, -6), name="snout_rear", paint=UT)
    m.box("skull", *R(-2, -3, -15, 2, 2, -11), name="snout", paint=UT)
    m.box("skull", *R(-1.5, -3, -16, 1.5, 1, -15), name="snout_tip", paint=MOUTH_DOWN)
    m.bone("jaw", "skull", (0, ay - 3, az - 1))
    m.box("jaw", *R(-3, -6, -6, 3, -3, 1), name="jaw_back", paint=MOUTH_UP)
    m.box("jaw", *R(-2, -6, -11, 2, -3, -6), name="jaw", paint=LT)
    m.box("jaw", *R(-1.5, -5, -16, 1.5, -3, -11), name="jaw_front", paint=LT)
    for s in (1, -1):
        a, b = sorted((s * 1.5, s * 2.5))
        m.box("skull", *R(a, -5, -14, b, -3, -13), name="fang", tag="tooth_cube", paint={"axis": "-y"})   # upper canine
        a, b = sorted((s * 2, s * 3))
        m.box("jaw", *R(a, -3, -12, b, 0, -11), name="fang", tag="tooth_cube", paint={"axis": "+y"})    # lower canine
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3.5, ay + 2.2, az - 4.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3.5, ay + 2.2, az - 4.0), "r": 1.0, "side": -1},
    ]
    for s in (1, -1):
        m.decals.append({"kind": "spot", "bones": ["skull"], "pos": (1.5 * s, ay - 0.5, az - 15.5), "r": 0.6,
                         "mul": 0.4, "side": s})                            # nostrils opening to the sides


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag in ("tooth_cube", "eye", "mouth", "claw"):
        return rgb
    if tag == "scute":
        col = tx.pal["scute"].copy()
        if tx.face == "up":
            col = col * 1.1
        if tx.edge:
            col = col * 0.82
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
        "tail1": (-4, 0, 0), "tail2": (-6, 0, 0), "tail3": (-6, 0, 0), "tail4": (-5, 0, 0),
        "upperarm_l": (15, 0, -30), "upperarm_r": (25, 0, 30), "forearm_l": (0, 0, -40), "forearm_r": (0, 0, -30),
        "thigh_l": (-10, 0, -30), "thigh_r": (-20, 0, 30), "shin_l": (0, 0, -40), "shin_r": (0, 0, -30)}

SPEC = dict(
    render_scale=0.5,
    palette={"dorsal": "#8a6a3c", "flank": "#b08c58", "belly": "#e2d2a8", "band": "#3e2a18", "throat": "#ecdfbe",
             "scute": "#5a4028",
             "limb": "#9a7a4a", "limb_top": "#a8885a",
             "claw": "#3a3228", "claw_base": "#4a4234", "claw_tip": "#2a241c",
             "tooth": "#efe8d2", "mouth": "#8a3844", "gum": "#5a4030",
             "tooth_cube": "#efe8d2", "tooth_cube_base": "#d8d0b8", "tooth_cube_tip": "#fbf8ee",
             "eye": "#c89a30", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#8a5a30", "flank": "#b4824a", "band": "#1e1410", "scute": "#4a3020"},
           "female": {"dorsal": "#9a8050", "flank": "#bca070", "band": "#5a4028", "throat": "#f0e6cc"}},
    pattern=pattern, body=(BODY_Y, 0), body_parts=body_parts, head=head,
    neck=dict(points=[(14, -10), (15, -16)], sections=[(8, 6)]),
    tail=dict(points=[(13, 12), (12, 21), (10.5, 30), (9, 38), (8, 44)], sections=[(8, 6), (6, 5), (4, 3), (2, 2)],
              crest=[(1, 2)]),
    # long upright legs nearly under the body, the hind ones longer and heavier
    legs=dict(front=dict(pivot=(4.5, 12.6, -6), upper=(6, 4, 4), sprawl=70, lower=(6, 3, 4), foot=(4, 5, 1, 1)),
              hind=dict(pivot=(4.5, 13.6, 8), upper=(7, 5, 5), sprawl=70, lower=(6, 4, 4), foot=(5, 6, 1, 1))),
    gait=dict(walk=(1.2, 26, 0.6, 3), run=(0.6, 38, 1.4, 4)),
    sit=dict(drop=8, upper=-75, lower=150, lower_roll=0, neck=-4, tail=-2),
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-20),
)


def build():
    m = croc.build(ID, SPEC)
    for nm in ("attack", "eat"):
        fit_to_ground(m, nm, ("neck1", "skull"))
    return m
