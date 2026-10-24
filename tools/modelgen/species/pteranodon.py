"""
Pteranodon longiceps  (Late Cretaceous, Western Interior Seaway, Kansas)

Reference (Wikipedia): wingspan 5.6-7.3 m in males, ~3.8 m in females; toothless beak; skull up to ~1.5 m
with a long backward crest (big in males, short and rounded in females); small body, tiny tail; walked on all
fours with the wings folded. Ate fish caught near the surface of the inland sea.

Modelled at 1 px = 1/16 block with the wings spread (the flying shape); the ground poses fold the wings so the
hands become front feet. Wingspan ~108 px -> ~6.75 blocks at scale 1. Not a dinosaur: a pterosaur.
"""
import math
from rig import Model, track, keys, wave, add_saddle, sit_tracks

ID = "pteranodon"

SHOULDER = (4, 16, -4)       # x, y, z of the left shoulder
W1, W2, W3 = 12, 12, 26      # arm (humerus + forearm), metacarpal, wing finger (the longest bone)
CHORD = (12, 9, 6, 3)         # membrane depth behind the arm, hand and the two halves of the finger


def build():
    m = Model(ID, render_scale=1.0)
    m.palette = {
        "dorsal": "#6f6a62", "flank": "#b9b2a4", "belly": "#ece6d8",
        "limb": "#7a6e60", "limb_top": "#8c8070",
        "membrane": "#7a5e4a", "membrane_edge": "#4e3a2e",
        "beak": "#d8c08a", "crest": "#c0482a", "crest_tip": "#e8a040",
        "claw": "#2c2420", "claw_base": "#3a302a",
        "mouth": "#8a5040", "eye": "#d8a838", "pupil": "#120d0a",
    }
    m.sexes = {"male": {"crest": "#c0482a", "crest_tip": "#f0a838"},
               "female": {"crest": "#8a7a62", "crest_tip": "#b0a080", "membrane": "#806a58", "dorsal": "#77736a"}}

    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 14, 0))
    m.box("body", (-4, 10, -6), (4, 17, 8), name="torso")
    m.box("body", (-3, 9, -6), (3, 10, 3), name="keel")

    # neck: two short segments rising to the head
    m.bone("neck1", "body", (0, 15, -6), (25, 0, 0))
    m.box("neck1", (-1.5, 13.5, -12), (1.5, 16.5, -5), name="neck1")
    m.bone("neck2", "neck1", (0, 15, -11), (10, 0, 0))
    m.box("neck2", (-1.5, 13.5, -17), (1.5, 16.5, -10), name="neck2")
    ay, az = 15, -16
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

    # wings: three bones per side, a thin leading edge with the membrane behind it (+Z)
    sx0, sy, sz = SHOULDER

    def wing(side, s):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        x1, x2, x3, x4 = sx0, sx0 + W1, sx0 + W1 + W2, sx0 + W1 + W2 + W3
        # each membrane has its own bone (pivot on the leading edge) so the ground poses can fold it away
        m.bone(f"wing1_{side}", "body", (x1 * s, sy, sz))
        a, b = X(x1, x2)
        m.box(f"wing1_{side}", (a, sy - 1, sz - 1), (b, sy + 1, sz + 1), tag="limb", name="arm")
        m.bone(f"mem1_{side}", f"wing1_{side}", (x1 * s, sy, sz + 1))
        m.box(f"mem1_{side}", (a, sy - 0.5, sz + 1), (b, sy + 0.5, sz + 1 + CHORD[0]), tag="membrane", name="membrane1")
        m.bone(f"wing2_{side}", f"wing1_{side}", (x2 * s, sy, sz))
        a, b = X(x2, x3)
        m.box(f"wing2_{side}", (a, sy - 1, sz - 1), (b, sy + 1, sz + 1), tag="limb", name="hand")
        m.bone(f"mem2_{side}", f"wing2_{side}", (x2 * s, sy, sz + 1))
        m.box(f"mem2_{side}", (a, sy - 0.5, sz + 1), (b, sy + 0.5, sz + 1 + CHORD[1]), tag="membrane", name="membrane2")
        c0, c1 = X(x3 - 1, x3)
        m.box(f"wing2_{side}", (c0, sy - 2, sz - 2), (c1, sy, sz - 1), tag="claw", name="fingers", paint={"axis": "-y"})
        m.bone(f"wing3_{side}", f"wing2_{side}", (x3 * s, sy, sz))
        a, b = X(x3, x4)
        m.box(f"wing3_{side}", (a, sy - 0.5, sz - 0.5), (b, sy + 0.5, sz + 0.5), tag="limb", name="finger")
        m.bone(f"mem3_{side}", f"wing3_{side}", (x3 * s, sy, sz + 0.5))
        half = W3 // 2
        a, b = X(x3, x3 + half)
        m.box(f"mem3_{side}", (a, sy - 0.5, sz + 0.5), (b, sy + 0.5, sz + 0.5 + CHORD[2]), tag="membrane", name="membrane3")
        a, b = X(x3 + half, x4)
        m.box(f"mem3_{side}", (a, sy - 0.5, sz + 0.5), (b, sy + 0.5, sz + 0.5 + CHORD[3]), tag="membrane", name="membrane4")

        # hind leg: short, under the hips
        lx = 2.5 * s
        m.bone(f"thigh_{side}", "root", (lx, 11, 6))
        m.box(f"thigh_{side}", (lx - 1, 5, 5), (lx + 1, 11, 7), tag="limb", name="thigh")
        m.bone(f"shin_{side}", f"thigh_{side}", (lx, 5, 6))
        m.box(f"shin_{side}", (lx - 0.5, 1, 5.5), (lx + 0.5, 6, 6.5), tag="limb", name="shin")
        m.bone(f"foot_{side}", f"shin_{side}", (lx, 1, 6))
        m.box(f"foot_{side}", (lx - 1, 0, 3), (lx + 1, 1, 7), tag="limb", name="foot")
        m.box(f"foot_{side}", (lx - 1, 0, 2), (lx + 1, 1, 3), tag="claw", name="claws")
    m.sym(wing)

    m.bone("tail1", "body", (0, 14, 8))
    m.box("tail1", (-1, 13, 8), (1, 15, 12), name="tail")
    add_saddle(m, "body", 17, -5, 3, 6, 4, flap=4)

    def pattern(model, tx, rgb, region):
        tag = tx.cube.tag
        P = tx.P
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
    m.pattern = pattern

    animations(m)
    return m


# ------------------------------------------------------------------ poses
BODY_TILT = 18  # ground poses lift the front of the body

# where each wing bone points when folded (left side, world directions with the body tilted): the arm goes out,
# down and forward, the hand straight down to the ground, the long finger back up along the body.
FOLD_DIRS = {"wing1": (0.35, -0.6, -0.7), "wing2": (0.1, -0.85, 0.5), "wing3": (-0.25, 0.5, 0.83)}


def _aim(parent_rot, direction):
    """Local (x=0, y, z) Euler angles that turn the bone's +X into the world direction, given the parent's world
    rotation matrix."""
    import numpy as np
    from pybench import rot_matrix
    d = np.array(direction, dtype=float)
    d /= np.linalg.norm(d)
    v = parent_rot.T @ d
    y = math.degrees(math.asin(max(-1.0, min(1.0, -v[2]))))
    z = math.degrees(math.atan2(v[1], v[0]))
    return (0.0, round(y, 2), round(z, 2)), parent_rot @ rot_matrix((0.0, y, z))


def folded():
    from pybench import rot_matrix
    p = {"body": (BODY_TILT, 0, 0), "neck1": (-10, 0, 0), "skull": (-4, 0, 0)}
    R = rot_matrix((BODY_TILT, 0, 0))
    for bone in ("wing1", "wing2", "wing3"):
        rot, R = _aim(R, FOLD_DIRS[bone])
        p[bone + "_l"] = rot
        p[bone + "_r"] = (rot[0], -rot[1], -rot[2])
    return p


FOLD_SCALE = (1.0, 1.0, 0.12)  # membranes squashed against the bones when folded


def membranes_folded(length):
    t = {}
    for side in ("l", "r"):
        for k in (1, 2, 3):
            t[f"mem{k}_{side}"] = {"scale": keys([(0, *FOLD_SCALE), (length, *FOLD_SCALE)])}
    return t


def animations(m):
    def const(pose, length, moving=None):
        t = membranes_folded(length)
        for bone, rot in pose.items():
            t[bone] = track(rot=keys([(0, *rot), (length, *rot)]))
        if moving:
            t.update(moving)
        return t

    # idle on the ground: folded wings, breathing, head looking around
    Li = 3.0
    idle = const(folded(), Li)
    idle["body"] = track(rot=wave(8, lambda p: (18 + 1.0 * math.sin(2 * math.pi * p), 0, 0), Li),
                         pos=wave(8, lambda p: (0, 0.2 * math.sin(2 * math.pi * p), 0), Li))
    idle["neck1"] = track(rot=wave(8, lambda p: (-10 + 3 * math.sin(2 * math.pi * (p + 0.1)), 6 * math.sin(2 * math.pi * p), 0), Li))
    idle["skull"] = track(rot=wave(8, lambda p: (-4 + 2 * math.sin(2 * math.pi * (p + 0.3)), 0, 4 * math.sin(2 * math.pi * p)), Li))
    m.anim("idle", Li, True, idle)

    # walk / run on all fours: folded arms swing like front legs, opposite to the hind legs
    for name, L, A in (("walk", 1.0, 18), ("run", 0.6, 28)):
        t = const(folded(), L)
        for side, ph, s in (("l", 0.0, 1), ("r", 0.5, -1)):
            base1 = folded()[f"wing1_{side}"]
            t[f"wing1_{side}"] = track(rot=wave(8, lambda p, ph=ph, b=base1: (b[0] + A * math.sin(2 * math.pi * (p + ph + 0.5)), b[1], b[2]), L))
            t[f"thigh_{side}"] = track(rot=wave(8, lambda p, ph=ph: (A * math.sin(2 * math.pi * (p + ph)), 0, 0), L))
            t[f"shin_{side}"] = track(rot=wave(8, lambda p, ph=ph: (-A * 0.8 * max(0.0, math.cos(2 * math.pi * (p + ph))), 0, 0), L))
        t["body"] = track(rot=wave(8, lambda p: (18, 3 * math.sin(2 * math.pi * p), 2 * math.sin(2 * math.pi * p)), L),
                          pos=wave(8, lambda p: (0, 0.4 * math.cos(4 * math.pi * p), 0), L))
        m.anim(name, L, True, t)

    # flying: the rest pose is the spread wing; the legs trail behind
    def air(L, flap, extra):
        t = {}
        for side in ("l", "r"):
            t[f"thigh_{side}"] = track(rot=keys([(0, -75, 0, 0), (L, -75, 0, 0)]))
            t[f"shin_{side}"] = track(rot=keys([(0, 10, 0, 0), (L, 10, 0, 0)]))
            t[f"foot_{side}"] = track(rot=keys([(0, -10, 0, 0), (L, -10, 0, 0)]))
        for side, s in (("l", 1), ("r", -1)):
            t[f"wing1_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * flap * math.sin(2 * math.pi * p)), L))
            t[f"wing2_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * flap * 0.6 * math.sin(2 * math.pi * (p - 0.12))), L))
            t[f"wing3_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * flap * 0.4 * math.sin(2 * math.pi * (p - 0.22))), L))
        t["body"] = track(rot=keys([(0, -4, 0, 0), (L, -4, 0, 0)]),
                          pos=wave(8, lambda p: (0, -0.8 * flap / 30 * math.sin(2 * math.pi * p), 0), L))
        t["neck1"] = track(rot=keys([(0, -20, 0, 0), (L, -20, 0, 0)]))
        t["skull"] = track(rot=keys([(0, 12, 0, 0), (L, 12, 0, 0)]))
        t.update(extra)
        return t
    m.anim("fly", 0.8, True, air(0.8, 32, {}))
    m.anim("glide", 3.0, True, air(3.0, 4, {
        "body": track(rot=wave(8, lambda p: (-4, 0, 5 * math.sin(2 * math.pi * p)), 3.0))}))

    # resting: folded, body down
    joints = {k: v for k, v in folded().items() if k != "body"}
    for side in ("l", "r"):
        joints["@thigh_" + side] = (60, 0, 0)
        joints["shin_" + side] = (-100, 0, 0)
        joints["foot_" + side] = (40, 0, 0)
    joints["neck1"] = (-30, 0, 0)
    joints["skull"] = (10, 0, 0)
    sit = sit_tracks(3.0, 5, joints, extra=membranes_folded(3.0))
    sit["body"] = track(pos=keys([(0, 0, -5, 0), (1.5, 0, -4.8, 0), (3.0, 0, -5, 0)]),
                        rot=keys([(0, 10, 0, 0), (1.5, 10.6, 0, 0), (3.0, 10, 0, 0)]))
    m.anim("sit", 3.0, True, sit)

    # attack: quick beak jab
    m.anim("attack", 0.6, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.15, 20, 0, 0), (0.3, -25, 0, 0), (0.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.15, 10, 0, 0), (0.3, -10, 0, 0), (0.6, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.15, -25, 0, 0), (0.28, -30, 0, 0), (0.34, 0, 0, 0), (0.6, 0, 0, 0)])),
    })
