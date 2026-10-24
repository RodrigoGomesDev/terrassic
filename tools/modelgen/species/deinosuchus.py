"""
Deinosuchus riograndensis  (Late Cretaceous, Campanian; both coasts of the Western Interior Seaway)

Reference (Wikipedia; Schwimmer 2002; Cossette & Brochu 2020): an alligatoroid of 10.6 m (the largest well-measured
D. riograndensis; older estimates reach 12 m) and several tonnes, with a broad flat skull over 1.8 m long, a bulbous
snout tip, thick blunt teeth at the back for crushing turtles, rows of heavy osteoderms down the back and a strong
bite that marked tyrannosaur bones. It ambushed from the water like a living alligator.

Built on the crocodylomorph archetype. Modelled ~116 px long; SIZES scales it to 12 m. Dark olive-green with black
bands over a buff belly; males darker and greener, females browner with a paler throat.
"""
import math
from rig import track, keys
import croc

ID = "deinosuchus"
BODY_Y = 9


def body_parts(m):
    # a long, flat barrel; the belly plate; two inner and two outer rows of osteoderm scutes
    m.box("body", (-7, 4, -14), (7, 14, 16), name="torso")
    m.box("body", (-6, 3, -13), (6, 4, 15), name="belly")
    for x0 in (-4, 2):
        m.box("body", (x0, 14, -13), (x0 + 2, 16, 15), name="scute_in", tag="scute")
    for x0 in (-7, 5):
        m.box("body", (x0, 13, -11), (x0 + 2, 15, 13), name="scute_out", tag="scute")


def head(m, ay, az, abs_pitch):
    m.bone("skull", "head", (0, ay, az), (-abs_pitch, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # broad flat alligator skull: raised eye ridges, a long snout swelling at the tip (the bulla), teeth all along
    m.box("skull", *R(-5, -3, -10, 5, 3, 0), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-5, 3, -7, -3, 5, -3), name="brow_l", tag="scute")
    m.box("skull", *R(3, 3, -7, 5, 5, -3), name="brow_r", tag="scute")
    m.box("skull", *R(-4, -3, -22, 4, 2, -10), name="snout", paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1, "freq": 0.9}})
    m.box("skull", *R(-3, -3, -26, 3, 3, -22), name="snout_tip", paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1, "freq": 0.9}})
    m.bone("jaw", "skull", (0, ay - 3, az - 2))
    m.box("jaw", *R(-4, -6, -25, 4, -3, -2), name="jaw", paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1, "freq": 0.9}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4.0, ay + 3.6, az - 5.0), "r": 1.2, "side": 1, "up": True},
        {"kind": "eye", "bones": ["skull"], "pos": (-4.0, ay + 3.6, az - 5.0), "r": 1.2, "side": -1, "up": True},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "scute":
        col = tx.pal["scute"].copy()
        # each scute a raised keel: light at the top, dark seams every 3 px
        if tx.face == "up" and int(math.floor(P[2] + 100)) % 3 == 0:
            col = col * 0.72
        elif tx.face == "up":
            col = col * 1.12
        if tx.edge:
            col = col * 0.85
        return col
    if tag == "skin":
        # alligator banding: dark cross bands over the back and tail, fading on the flanks; yellow belly scales
        band = math.sin(P[2] * 0.55 + P[0] * 0.15)
        if region == "dorsal" and band > 0.45:
            rgb = tx.pal["band"].copy()
        elif region == "flank" and band > 0.75:
            rgb = rgb * 0.8
        elif region == "belly":
            if (int(math.floor(P[2] * 0.7)) + int(math.floor(P[0] * 0.7))) % 2 == 0:
                rgb = rgb * 0.93
            if tx.cube.bone.startswith("neck") or tx.cube.bone in ("skull", "jaw"):
                rgb = tx.pal["throat"].copy()
        if region in ("dorsal", "flank") and (int(math.floor(P[2] * 0.9)) + int(math.floor(P[1] * 0.9))) % 2 == 0:
            rgb = rgb * 0.95                                   # scale rows
    elif tag == "limb":
        if (int(math.floor(P[1] * 0.9)) + int(math.floor(P[0] * 0.9))) % 2 == 0:
            rgb = rgb * 0.94
    return rgb


# knocked out on its side: jaws slack, legs limp, the tail curving on the ground
# the body lies on its right side (-x down): both leg pairs fold to the belly side (roll around z), the lower limbs of
# the top legs dangle to the ground and those of the under legs continue the line of the upper limb
LIMP = {"neck1": (-6, 0, 0), "skull": (-2, 0, 0), "jaw": (-16, 0, 0),
        "tail1": (-4, 0, 0), "tail2": (-6, 0, 0), "tail3": (-6, 0, 0), "tail4": (-5, 0, 0),
        "upperarm_l": (10, 0, -60), "upperarm_r": (18, 0, 60), "forearm_l": (0, 0, -30), "forearm_r": (0, 0, -80),
        "thigh_l": (-8, 0, -60), "thigh_r": (-16, 0, 60), "shin_l": (0, 0, -30), "shin_r": (0, 0, -80)}

SPEC = dict(
    palette={"dorsal": "#3a4a2c", "flank": "#5c6a40", "belly": "#c8bc84", "band": "#1e2616", "throat": "#d8d0a0",
             "scute": "#2c3820",
             "limb": "#4a5636", "limb_top": "#5c6a40",
             "claw": "#3a3228", "claw_base": "#4a4234", "claw_tip": "#2a241c",
             "tooth": "#efe8d2", "mouth": "#8a3844", "gum": "#5e262e",
             "eye": "#c8a040", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#2e4026", "flank": "#4e5e38", "band": "#141c10", "scute": "#222e18"},
           "female": {"dorsal": "#4a4e30", "flank": "#6a6c46", "band": "#2a2a18", "throat": "#e4dcb0"}},
    pattern=pattern, body=(BODY_Y, 0), body_parts=body_parts, head=head,
    neck=dict(points=[(9, -14), (9, -20)], sections=[(11, 9)]),
    tail=dict(points=[(9, 16), (9, 30), (8, 44), (7, 57), (6, 70)],
              sections=[(11, 9), (8, 7), (5, 5), (3, 3)], crest=[(1, 3), (2, 3), (3, 2)]),
    legs=dict(front=dict(pivot=(7, 9, -9), upper=(8, 5, 5), sprawl=30, lower=(4, 4, 5), foot=(7, 6, 1, 2)),
              hind=dict(pivot=(7, 9, 10), upper=(8, 6, 6), sprawl=30, lower=(4, 4, 5), foot=(8, 6, 1, 2))),
    gait=dict(walk=(1.6, 18, 0.5, 4), run=(0.8, 26, 1.2, 6)),
    sit=dict(drop=5, upper=0, lower=0, lower_roll=-55, neck=-2, tail=-1),
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-6),
)


def build():
    return croc.build(ID, SPEC)
