"""
Hatzegopteryx thambema  (Late Cretaceous, Hațeg Island, Romania)

Reference (Wikipedia; Buffetaut et al. 2002; Naish & Witton 2017): wingspan 10-12 m, one of the largest pterosaurs.
Unlike the slender Quetzalcoatlus it was ROBUST: a very wide skull (~50 cm across the back, ~3 m long) with thick
bone walls, a short, extremely stout neck built of massive vertebrae, heavy limb bones. On its island, with no big
theropods around, it was the top predator, taking dwarf dinosaurs the size of a horse. A bruiser, not a stork.

Modelled at the same wingspan as the Quetzalcoatlus (120 px) so the two read as the same class of giant, but with a
heavier body, a short thick neck and a wide deep skull. Males darker with a dark red keel on the beak.
"""
import math
from rig import track, keys, add_saddle
import pterosaur

ID = "hatzegopteryx"
SHOULDER = (5, 30, -4)
BODY_Y = 28


def body_parts(m):
    # heavy barrel torso with a deep keel
    m.box("body", (-5, 23, -8), (5, 33, 8), name="torso")
    m.box("body", (-3.5, 20, -7), (3.5, 23, 4), name="keel")
    m.box("body", (-4, 32, -10), (4, 34, -4), name="shoulders")
    m.box("body", (-1.5, 27, 8), (1.5, 30, 12), name="tail", tag="limb")

    # short, very thick neck: two stout segments rising at ~55 degrees
    neck = m.chain(["neck1", "neck2"], "body", 0, [(31, -8), (38, -14), (44, -19)], "-z",
                   [(7, 7), (6, 6)], overlap=(2.0, 1.5))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"] + 10, 0, 0))   # heavy head carried slightly down

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # wide deep skull: broad back of the head, then a massive beak that stays deep almost to the tip
    m.box("skull", *R(-4, -3, -7, 4, 4, 2), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -3, -16, 3, 3, -7), name="beak_base", tag="beak", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, -3, -24, 2, 2, -16), name="beak_mid", tag="beak", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1, -2, -29, 1, 1, -24), name="beak_tip", tag="beak_tip")
    # low keel ridge along the top of the beak (bony crest), taller in males
    m.box("skull", *R(-1, 3, -15, 1, 5, -4), name="crest", tag="crest")
    m.bone("male_display", "skull", (0, ay, az))
    m.box("male_display", *R(-0.5, 5, -13, 0.5, 6, -6), name="crest_tall", tag="crest")
    m.bone("jaw", "skull", (0, ay - 3, az - 6))
    m.box("jaw", *R(-2.5, -6, -27, 2.5, -3, -6), name="jaw", tag="beak", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-1, -5, -29, 1, -3, -27), name="jaw_tip", tag="beak_tip")
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4, ay + 1.0, az - 3.5), "r": 1.2, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4, ay + 1.0, az - 3.5), "r": 1.2, "side": -1},
        # pale bare face
        {"kind": "spot", "bones": ["skull"], "pos": (4, ay + 0.5, az - 3.5), "r": 3.0, "rx": 0.7, "side": 1, "color": "face"},
        {"kind": "spot", "bones": ["skull"], "pos": (-4, ay + 0.5, az - 3.5), "r": 3.0, "rx": 0.7, "side": -1, "color": "face"},
    ]
    add_saddle(m, "body", 33, -3, 4, 8, 5, flap=5)


def leg(m, side, s):
    # thick, fairly short legs; broad feet
    x = 3.0 * s
    ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x,
                 [(25, 6), (16, 3), (6, 6), (1, 4)], "-y",
                 [(4, 4), (3, 3, 0.0, "limb"), (3, 3, 0.0, "limb")], overlap=(1.0, 0.5))
    by, bz = ch["end"]
    m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
    m.box(f"toes_{side}", (x - 2, by - 1, bz - 5), (x + 2, by, bz + 2), tag="limb", name="toes")
    m.box(f"toes_{side}", (x - 2, by - 1, bz - 6), (x + 2, by, bz - 5), tag="claw", name="claws")


def pattern(model, tx, rgb, region):
    tag = tx.cube.tag
    P = tx.P
    if tag == "membrane":
        chord = (P[2] - (SHOULDER[2] + 1)) / 10.0
        rgb = rgb * (1.05 - 0.25 * max(0.0, min(1.0, chord)))
        # broad dark bars across the wing
        if math.sin(abs(P[0]) * 0.55) > 0.45:
            rgb = rgb * 0.8
        if abs(P[0]) > SHOULDER[0] + 15 + 21 + 12:
            rgb = tx.pal["wingtip"].copy()
        if tx.face in ("up", "down") and tx.edge:
            rgb = tx.pal["membrane_edge"].copy()
        if tx.face == "down":
            rgb = rgb * 1.08
    elif tag == "crest":
        rgb = tx.pal["crest"] * (0.85 + 0.15 * math.sin(P[2] * 0.9))
    elif tag == "beak":
        # dark beak, paler toward the base and along the cutting edges
        if tx.cube.bone == "jaw":
            rgb = rgb * 0.9
        if P[2] > tx.cube.frm[2] + 0.6 * tx.cube.size[2]:
            rgb = rgb * 1.12
    elif tag == "skin":
        if tx.cube.bone == "skull" and tx.face != "down" and P[1] > tx.cube.frm[1] + 3:
            rgb = tx.pal["cap"].copy()
        elif tx.cube.bone.startswith("neck"):
            # coarse pycnofibre coat: dark top, pale throat, speckled sides
            if region == "belly":
                rgb = tx.pal["throat"].copy()
            elif math.sin(P[1] * 2.1 + P[0] * 1.3) * math.sin(P[2] * 1.7) > 0.55:
                rgb = rgb * 0.86
        elif region in ("dorsal", "flank") and math.sin(P[0] * 1.5) * math.sin(P[2] * 1.1 + P[1]) > 0.6:
            rgb = rgb * 0.88
    return rgb


def attack(m):
    # slam: the whole body lunges and the heavy beak comes down like an axe, then shakes the prey
    m.anim("attack", 1.0, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.25, -6, 0, 0), (0.45, 10, 0, 0), (1.0, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.25, 0, 1, 1), (0.45, 0, -1.5, -3), (1.0, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.25, 22, 0, 0), (0.45, -30, 0, 0), (0.6, -28, 0, 6), (0.75, -28, 0, -6), (1.0, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.25, 8, 0, 0), (0.45, -14, 0, 0), (1.0, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.25, 10, 0, 0), (0.45, -16, 0, 0), (0.6, -14, 0, 8), (0.75, -14, 0, -8), (1.0, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.25, -30, 0, 0), (0.42, -34, 0, 0), (0.5, -4, 0, 0), (0.75, -4, 0, 0), (1.0, 0, 0, 0)])),
    })


SPEC = dict(
    palette={"dorsal": "#4e4a48", "flank": "#78706a", "belly": "#b9ada0", "throat": "#cfc4b4", "cap": "#2a2626",
             "limb": "#3f3a38", "limb_top": "#524c49",
             "membrane": "#4a3f3b", "membrane_edge": "#2b2422", "wingtip": "#1f1a19",
             "beak": "#5a4a3e", "beak_tip": "#1e1917", "crest": "#7a2a22", "face": "#d8c6a8",
             "claw": "#1e1917", "claw_base": "#2c2522", "mouth": "#7a4038", "eye": "#d9b14a", "pupil": "#0f0b09"},
    sexes={"male": {"crest": "#8a2820", "dorsal": "#44403e", "cap": "#1e1b1b"},
           "female": {"crest": "#5e4a42", "dorsal": "#5a5452", "face": "#c9b9a0", "flank": "#827a74"}},
    pattern=pattern, body=(BODY_Y, 0), shoulder=SHOULDER,
    wing=(15, 21, 22), chord=(10, 8, 6, 3), wing_thick=1.5,
    # on the ground: a stockier stance than the Quetzalcoatlus, humerus more vertical
    fold_dirs={"wing1": (0.3, -0.6, -0.62), "wing2": (0.05, -0.95, 0.25), "wing3": (-0.1, 0.75, 0.65)},
    body_tilt=10, neck_rest=(-2, 0), neck_fly=(-50, 42),
    legs_fly=(-78, 22, -16), flap=(1.6, 24),             # slow, powerful beats
    body_parts=body_parts, leg=leg, attack=attack,
    gait={"walk": (1.9, 14), "run": (1.1, 24)},
    sit=dict(drop=22, thigh=78, shin=-150, foot=90, neck=-18, skull=12, body=(4, 0.3)),
    sit_wings={"wing1": (0.1, -0.5, 0.86), "wing2": (0.0, -0.06, -1.0), "wing3": (0.0, 0.6, 0.8)},
    ko=(80, 0.2, 0.7),
    ko_joints={"neck1": (-48, 10, 0), "neck2": (-10, 3, 0), "skull": (42, 0, 0), "jaw": (-16, 0, 0)},
)


def build():
    return pterosaur.build(ID, SPEC)
