"""
Quetzalcoatlus northropi  (Late Cretaceous, Javelina Formation, Texas)

Reference (Wikipedia; Witton & Naish 2008; Andres & Langston 2021): wingspan 10-11 m, standing ~5 m tall (as tall
as a giraffe), ~200-250 kg. An azhdarchid: extremely long, stiff neck (~3 m) of elongated vertebrae, a huge head
(~2.5 m) with a long pointed toothless beak and a low bony crest, a small torso, very long legs and long
forelimbs with an unusually long metacarpal, so on the ground it stands tall on all fours and stalks small prey
like a giant stork. Wings long and narrow (high aspect ratio) for soaring.

Modelled at 1 px = 1/16 block in the flying shape, wingspan 120 px; SIZES scales it to 11 m. Males: taller crest
and a redder face; females: duller, shorter crest.
"""
import math
from rig import track, keys, add_saddle
import pterosaur

ID = "quetzalcoatlus"
SHOULDER = (4, 33, -3)
BODY_Y = 31


def body_parts(m):
    # small keeled torso, high on the stilt legs
    m.box("body", (-4, 27, -7), (4, 35, 7), name="torso")
    m.box("body", (-2.5, 25, -6), (2.5, 27, 3), name="keel")
    m.box("body", (-3, 34, -8), (3, 36, -4), name="shoulders")
    m.box("body", (-1, 30, 7), (1, 32, 10), name="tail", tag="limb")

    # giraffe neck: three stiff segments rising steeply from the chest (azhdarchid vertebrae are tubes)
    neck = m.chain(["neck1", "neck2", "neck3"], "body", 0, [(34, -7), (45, -11), (55, -14), (63, -16)], "-z",
                   [(4, 4), (3, 3), (3, 3)], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck3", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"] + 6, 0, 0))  # level, beak tipped slightly down

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # huge head: tall back of the skull around the eye, then a long tapering spear of a beak
    m.box("skull", *R(-2.5, -2, -6, 2.5, 3, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, -2, -14, 2, 2, -6), name="beak_base", tag="beak", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1.5, -2, -22, 1.5, 1, -14), name="beak_mid", tag="beak", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1, -2, -28, 1, 0, -22), name="beak_tip", tag="beak_tip")
    # low bony crest running from above the eyes down the beak; males carry a taller blade
    m.box("skull", *R(-0.5, 3, -12, 0.5, 5, -3), name="crest", tag="crest")
    m.bone("male_display", "skull", (0, ay, az))
    m.box("male_display", *R(-0.5, 5, -10, 0.5, 7, -4), name="crest_tall", tag="crest")
    m.bone("jaw", "skull", (0, ay - 2, az - 5))
    m.box("jaw", *R(-1.5, -4, -26, 1.5, -2, -5), name="jaw", tag="beak", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-1, -4, -28, 1, -3, -26), name="jaw_tip", tag="beak_tip")
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (2.5, ay + 0.5, az - 3.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-2.5, ay + 0.5, az - 3.0), "r": 1.0, "side": -1},
        # bare red skin around the eye, stork style
        {"kind": "spot", "bones": ["skull"], "pos": (2.5, ay + 0.5, az - 3.0), "r": 2.2, "rx": 0.6, "side": 1, "color": "face"},
        {"kind": "spot", "bones": ["skull"], "pos": (-2.5, ay + 0.5, az - 3.0), "r": 2.2, "rx": 0.6, "side": -1, "color": "face"},
    ]
    add_saddle(m, "body", 35, -3, 3, 6, 4, flap=4)


def leg(m, side, s):
    # stilt legs: long femur sloping forward, long shin back, long metatarsus; four slender toes
    x = 2.5 * s
    ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x,
                 [(28, 5), (17, 2), (6, 6), (1, 3)], "-y",
                 [(3, 3), (2, 2, 0.0, "limb"), (2, 2, 0.0, "limb")], overlap=(1.0, 0.5))
    by, bz = ch["end"]
    m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
    m.box(f"toes_{side}", (x - 1.5, by - 1, bz - 5), (x + 1.5, by, bz + 1), tag="limb", name="toes")
    m.box(f"toes_{side}", (x - 1.5, by - 1, bz - 6), (x + 1.5, by, bz - 5), tag="claw", name="claws")


def pattern(model, tx, rgb, region):
    tag = tx.cube.tag
    P = tx.P
    if tag == "membrane":
        chord = (P[2] - (SHOULDER[2] + 1)) / 9.0
        rgb = rgb * (1.05 - 0.3 * max(0.0, min(1.0, chord)))
        if int(math.floor(abs(P[0]) / 2.5 + P[2] / 5.0)) % 4 == 0:
            rgb = rgb * 0.88                         # stiffening fibres
        if abs(P[0]) > SHOULDER[0] + 14 + 20 + 11:
            rgb = tx.pal["wingtip"].copy()          # dark outer wing
        if tx.face in ("up", "down") and tx.edge:
            rgb = tx.pal["membrane_edge"].copy()
        if tx.face == "down":
            rgb = rgb * 1.1
    elif tag == "crest":
        rgb = tx.pal["crest"] * (0.8 + 0.2 * math.sin(P[2] * 1.2))
    elif tag == "skin":
        if tx.cube.bone == "skull" and tx.face != "down":
            rgb = tx.pal["cap"].copy() if P[1] > tx.cube.frm[1] + 2.5 else rgb   # dark cap over the skull
        elif tx.cube.bone.startswith("neck"):
            # fine pycnofibre fuzz: lighter throat, faint rings down the neck
            if region == "belly":
                rgb = tx.pal["throat"].copy()
            elif math.sin(P[1] * 1.1) > 0.6:
                rgb = rgb * 0.92
        elif region == "dorsal" and math.sin(P[2] * 0.9 + P[0] * 0.6) > 0.75:
            rgb = rgb * 0.9
    return rgb


def attack(m):
    # spear-fishing jab: the whole neck whips down and forward, then snaps back
    m.anim("attack", 0.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.2, 15, 0, 0), (0.42, -40, 0, 0), (0.6, -30, 0, 0), (0.8, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.2, 6, 0, 0), (0.42, -18, 0, 0), (0.8, 0, 0, 0)])),
        "neck3": track(rot=keys([(0, 0, 0, 0), (0.2, 4, 0, 0), (0.42, -10, 0, 0), (0.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.2, 8, 0, 0), (0.42, -12, 0, 0), (0.8, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -22, 0, 0), (0.4, -26, 0, 0), (0.48, 0, 0, 0), (0.8, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.42, -5, 0, 0), (0.8, 0, 0, 0)])),
    })


SPEC = dict(
    palette={"dorsal": "#8c8378", "flank": "#c9c1b2", "belly": "#efe9dc", "throat": "#f3eee2", "cap": "#3c3a3a",
             "limb": "#5b5550", "limb_top": "#6e6760",
             "membrane": "#5d4a3f", "membrane_edge": "#3a2c25", "wingtip": "#2e2420",
             "beak": "#e0cfa0", "beak_tip": "#2a2522", "crest": "#9a3a2a", "face": "#c8472e",
             "claw": "#2c2420", "claw_base": "#3a302a", "mouth": "#8a5040", "eye": "#e6c24a", "pupil": "#120d0a"},
    sexes={"male": {"face": "#d84a2c", "crest": "#a83828"},
           "female": {"face": "#9a6a5a", "crest": "#7a5a4a", "cap": "#55504c", "dorsal": "#948b80"}},
    pattern=pattern, body=(BODY_Y, 0), shoulder=SHOULDER,
    wing=(14, 20, 22), chord=(9, 7, 5, 2), wing_thick=1.0,
    # on the ground the long metacarpal is the front leg: humerus down and forward, hand straight down,
    # the wing finger folded back up along the body
    fold_dirs={"wing1": (0.3, -0.7, -0.6), "wing2": (0.05, -0.95, 0.3), "wing3": (-0.1, 0.8, 0.6)},
    body_tilt=8, neck_rest=(-4, 0), neck_fly=(-62, 52),
    legs_fly=(-80, 25, -20), flap=(1.4, 26),             # slow, deep beats of a soaring giant
    body_parts=body_parts, leg=leg, attack=attack,
    gait={"walk": (1.6, 16), "run": (0.9, 26)},
    sit=dict(drop=24, thigh=80, shin=-155, foot=95, neck=-25, skull=14, body=(4, 0.3)),
    sit_wings={"wing1": (0.1, -0.46, 0.88), "wing2": (0.0, -0.06, -1.0), "wing3": (0.0, 0.6, 0.8)},
    ko=(80, 0.2, 0.7),
    # unconscious: the long neck falls forward and down to the ground, beak flat, jaw slack
    ko_joints={"neck1": (-62, 8, 0), "neck2": (-8, 2, 0), "neck3": (-4, 0, 0), "skull": (58, 0, 0), "jaw": (-14, 0, 0)},
)


def build():
    return pterosaur.build(ID, SPEC)
