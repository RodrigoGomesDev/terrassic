"""
Pteranodon longiceps  (Late Cretaceous, Western Interior Seaway, Kansas)

Reference (Wikipedia): wingspan 5.6-7.3 m in males, ~3.8 m in females; toothless beak; skull up to ~1.5 m
with a long backward crest (big in males, short and rounded in females); small body, tiny tail; walked on all
fours with the wings folded. Ate fish caught near the surface of the inland sea.

Modelled at 1 px = 1/16 block with the wings spread (the flying shape); the ground poses fold the wings so the
hands become front feet. Wingspan ~108 px -> ~6.75 blocks at scale 1. Not a dinosaur: a pterosaur.

Built on the pterosaur archetype (species/pterosaur.py) with exactly the v0.3 geometry; the archetype adds the
calibrated ground poses (the v0.3 fold pushed the hands below the ground) and knocked_out / wake / eat / beg / tame.
"""
import math
from rig import track, keys, add_saddle
import pterosaur

ID = "pteranodon"

SHOULDER = (4, 16, -4)       # x, y, z of the left shoulder
W1, W2, W3 = 12, 12, 26      # arm (humerus + forearm), metacarpal, wing finger (the longest bone)
CHORD = (12, 9, 6, 3)         # membrane depth behind the arm, hand and the two halves of the finger
HEAD = (15, -16)              # (y, z) where the head hangs off the neck


def body_parts(m):
    m.box("body", (-4, 10, -6), (4, 17, 8), name="torso")
    m.box("body", (-3, 9, -6), (3, 10, 3), name="keel")

    # neck: two short segments rising to the head
    m.bone("neck1", "body", (0, 15, -6), (25, 0, 0))
    m.box("neck1", (-1.5, 13.5, -12), (1.5, 16.5, -5), name="neck1")
    m.bone("neck2", "neck1", (0, 15, -11), (10, 0, 0))
    m.box("neck2", (-1.5, 13.5, -17), (1.5, 16.5, -10), name="neck2")
    ay, az = HEAD
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-35 - 8, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    m.box("skull", *R(-2, -1, -5, 2, 3, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1, -1, -11, 1, 1, -5), name="beak", tag="beak", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1, -1, -16, 1, 0, -11), name="beak_mid", tag="beak", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-0.5, -1, -20, 0.5, 0, -16), name="beak_tip", tag="beak")
    m.bone("jaw", "skull", (0, ay - 1, az - 3))
    m.box("jaw", *R(-1, -2, -15, 1, -1, -3), name="jaw", tag="beak", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-0.5, -2, -19, 0.5, -1, -15), name="jaw_tip", tag="beak")
    # crest: long blade backwards on males, a short rounded one on females
    co = (0, ay + 2, az + 1)
    m.bone("male_display", "skull", (0, ay, az))
    m.box("male_display", *R(-0.5, 2, 0, 0.5, 4, 13), name="crest", tag="crest", rot=(-14, 0, 0), origin=co,
          paint={"axis": "+z"})
    m.bone("female_display", "skull", (0, ay, az))
    m.box("female_display", *R(-0.5, 2, 0, 0.5, 4, 5), name="crest", tag="crest", rot=(-12, 0, 0), origin=co,
          paint={"axis": "+z"})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (2, ay + 1.0, az - 2.5), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-2, ay + 1.0, az - 2.5), "r": 1.0, "side": -1},
    ]


def leg(m, side, s):
    # hind leg: short, under the hips
    lx = 2.5 * s
    m.bone(f"thigh_{side}", "root", (lx, 11, 6))
    m.box(f"thigh_{side}", (lx - 1, 5, 5), (lx + 1, 11, 7), tag="limb", name="thigh")
    m.bone(f"shin_{side}", f"thigh_{side}", (lx, 5, 6))
    m.box(f"shin_{side}", (lx - 0.5, 1, 5.5), (lx + 0.5, 6, 6.5), tag="limb", name="shin")
    m.bone(f"foot_{side}", f"shin_{side}", (lx, 1, 6))
    m.box(f"foot_{side}", (lx - 1, 0, 3), (lx + 1, 1, 7), tag="limb", name="foot")
    m.box(f"foot_{side}", (lx - 1, 0, 2), (lx + 1, 1, 3), tag="claw", name="claws")


def after_wings(m):
    m.bone("tail1", "body", (0, 14, 8))
    m.box("tail1", (-1, 13, 8), (1, 15, 12), name="tail")
    add_saddle(m, "body", 17, -5, 3, 6, 4, flap=4)


def pattern(model, tx, rgb, region):
    tag = tx.cube.tag
    P = tx.P
    sz = SHOULDER[2]
    az = HEAD[1]
    if tag == "membrane":
        # darker towards the trailing edge, thin stiffening fibres running along the wing
        chord = (P[2] - (sz + 1)) / float(CHORD[0])
        rgb = rgb * (1.05 - 0.25 * max(0.0, min(1.0, chord)))
        if int(math.floor(abs(P[0]) / 3.0 + P[2] / 4.0)) % 3 == 0:
            rgb = rgb * 0.9
        if tx.face in ("up", "down") and tx.edge:
            rgb = tx.pal["membrane_edge"].copy()
        if tx.face == "down":
            rgb = rgb * 1.12
    elif tag == "crest":
        g = max(0.0, min(1.0, (P[2] - az) / 12.0))
        rgb = tx.pal["crest"] * (1 - g) + tx.pal["crest_tip"] * g
    elif tag == "skin" and region == "dorsal":
        if math.sin(P[2] * 1.3 + P[0] * 0.7) > 0.7:
            rgb = rgb * 0.9
    return rgb


def attack(m):
    # quick beak jab
    m.anim("attack", 0.6, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.15, 20, 0, 0), (0.3, -25, 0, 0), (0.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.15, 10, 0, 0), (0.3, -10, 0, 0), (0.6, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.15, -25, 0, 0), (0.28, -30, 0, 0), (0.34, 0, 0, 0), (0.6, 0, 0, 0)])),
    })


SPEC = dict(
    palette={"dorsal": "#6f6a62", "flank": "#b9b2a4", "belly": "#ece6d8",
             "limb": "#7a6e60", "limb_top": "#8c8070",
             "membrane": "#7a5e4a", "membrane_edge": "#4e3a2e",
             "beak": "#d8c08a", "crest": "#c0482a", "crest_tip": "#e8a040",
             "claw": "#2c2420", "claw_base": "#3a302a",
             "mouth": "#8a5040", "eye": "#d8a838", "pupil": "#120d0a"},
    sexes={"male": {"crest": "#c0482a", "crest_tip": "#f0a838"},
           "female": {"crest": "#8a7a62", "crest_tip": "#b0a080", "membrane": "#806a58", "dorsal": "#77736a"}},
    pattern=pattern, body=(14, 0), shoulder=SHOULDER,
    wing=(W1, W2, W3), chord=CHORD, wing_thick=1.0,
    # folded (left side, body tilted): the arm goes out, down and forward, the hand down to the ground, the long
    # finger back up along the body. Shallower than v0.3 so the hands rest ON the ground instead of through it.
    fold_dirs={"wing1": (0.35, -0.5, -0.65), "wing2": (0.1, -0.72, 0.6), "wing3": (-0.25, 0.5, 0.83)},
    body_tilt=18, neck_rest=(-10, -4), neck_fly=(-20, 12),
    legs_fly=(-75, 10, -10), flap=(0.8, 32),
    body_parts=body_parts, leg=leg, after_wings=after_wings, attack=attack,
    gait={"walk": (1.0, 18), "run": (0.6, 28)},
    sit=dict(drop=5, thigh=60, shin=-100, foot=40, neck=-30, skull=10, body=(10, 0.2)),
    ko=(80, 0.3, 0.6),
    ko_joints={"neck1": (-34, 10, 0), "neck2": (-8, 2, 0), "skull": (26, 0, 0), "jaw": (-12, 0, 0)},
)


def build():
    return pterosaur.build(ID, SPEC)
