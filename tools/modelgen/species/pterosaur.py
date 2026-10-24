"""
Archetype: pterosaurs. Shared wing construction (three bones per side with their own membrane bones so the ground
poses can fold them), the fold/fly/glide machinery and the animation set (idle, walk, run, fly, glide, sit,
attack, knocked_out). Everything that makes a species look like itself (body, neck, head, crest, legs, tail,
colours and pattern) is built by the species module through hooks, so an azhdarchid with a giraffe neck and stilt
legs shares no geometry with the Pteranodon beyond the wing bones.

Spec keys:
  render_scale            model pixel scale (in-game size comes from SIZES in tools/javagen/gen_species.py)
  palette, sexes, pattern colours and paint pattern (see paint.py)
  body                    (y, z) of the body pivot
  shoulder                (x, y, z) of the left shoulder
  wing                    (W1, W2, W3) lengths of arm, metacarpal and wing finger, in px
  chord                   (c1, c2, c3, c4) membrane depth behind arm, hand and the two halves of the finger
  wing_thick              half thickness of the arm/hand bones (0.5 for slender wings, 1 for the Pteranodon)
  fold_dirs               world directions of the folded wing bones (left side); see pteranodon.py
  body_tilt               ground pose body pitch (deg); 0 for animals that stand level
  neck_rest               (neck1, skull) pitch on the ground; neck_fly (neck1, skull) pitch in flight
  leg(m, side, s)         hook: builds thigh_/shin_/foot_<side> (thigh parented to root)
  body_parts(m)           hook: torso, neck, head, crest, tail, saddle, decals. Returns nothing.
  gait                    dict(walk=(length, amplitude), run=(length, amplitude)); legs swing by amplitude
  sit                     dict(drop=, thigh=, shin=, foot=, neck=, skull=, body=(pitch, dy))
  attack(m)               hook that adds the attack animation
  extra_anims(m)          optional hook for more animations
"""
import math
from rig import add_wake, add_actions, ground_drop, ground_lift, Model, track, keys, wave, sit_tracks, knockout_tracks


def build(species_id, spec):
    m = Model(species_id, render_scale=spec.get("render_scale", 1.0))
    m.palette = dict(spec["palette"])
    m.sexes = spec["sexes"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *spec["body"]))
    spec["body_parts"](m)

    sx0, sy, sz = spec["shoulder"]
    W1, W2, W3 = spec["wing"]
    CH = spec["chord"]
    th = spec.get("wing_thick", 1.0)

    def wing(side, s):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        x1, x2, x3, x4 = sx0, sx0 + W1, sx0 + W1 + W2, sx0 + W1 + W2 + W3
        m.bone(f"wing1_{side}", "body", (x1 * s, sy, sz))
        a, b = X(x1, x2)
        m.box(f"wing1_{side}", (a, sy - th, sz - th), (b, sy + th, sz + th), tag="limb", name="arm")
        m.bone(f"mem1_{side}", f"wing1_{side}", (x1 * s, sy, sz + th))
        m.box(f"mem1_{side}", (a, sy - 0.5, sz + th), (b, sy + 0.5, sz + th + CH[0]), tag="membrane", name="membrane1")
        m.bone(f"wing2_{side}", f"wing1_{side}", (x2 * s, sy, sz))
        a, b = X(x2, x3)
        m.box(f"wing2_{side}", (a, sy - th, sz - th), (b, sy + th, sz + th), tag="limb", name="hand")
        m.bone(f"mem2_{side}", f"wing2_{side}", (x2 * s, sy, sz + th))
        m.box(f"mem2_{side}", (a, sy - 0.5, sz + th), (b, sy + 0.5, sz + th + CH[1]), tag="membrane", name="membrane2")
        c0, c1 = X(x3 - 1, x3)
        m.box(f"wing2_{side}", (c0, sy - 2, sz - 2), (c1, sy, sz - 1), tag="claw", name="fingers", paint={"axis": "-y"})
        m.bone(f"wing3_{side}", f"wing2_{side}", (x3 * s, sy, sz))
        a, b = X(x3, x4)
        m.box(f"wing3_{side}", (a, sy - 0.5, sz - 0.5), (b, sy + 0.5, sz + 0.5), tag="limb", name="finger")
        m.bone(f"mem3_{side}", f"wing3_{side}", (x3 * s, sy, sz + 0.5))
        half = W3 // 2
        a, b = X(x3, x3 + half)
        m.box(f"mem3_{side}", (a, sy - 0.5, sz + 0.5), (b, sy + 0.5, sz + 0.5 + CH[2]), tag="membrane", name="membrane3")
        a, b = X(x3 + half, x4)
        m.box(f"mem3_{side}", (a, sy - 0.5, sz + 0.5), (b, sy + 0.5, sz + 0.5 + CH[3]), tag="membrane", name="membrane4")
        spec["leg"](m, side, s)
    m.sym(wing)
    spec.get("after_wings", lambda m: None)(m)
    m.pattern = spec["pattern"]
    animations(m, spec)
    return m


# ------------------------------------------------------------------ poses
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


def folded(spec):
    from pybench import rot_matrix
    tilt = spec["body_tilt"]
    n1, sk = spec["neck_rest"]
    p = {"body": (tilt, 0, 0), "neck1": (n1, 0, 0), "skull": (sk, 0, 0)}
    R = rot_matrix((tilt, 0, 0))
    for bone in ("wing1", "wing2", "wing3"):
        rot, R = _aim(R, spec["fold_dirs"][bone])
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


def animations(m, spec):
    tilt = spec["body_tilt"]
    n1, sk = spec["neck_rest"]
    fn1, fsk = spec["neck_fly"]
    fold = folded(spec)

    def const(pose, length, moving=None):
        t = membranes_folded(length)
        for bone, rot in pose.items():
            t[bone] = track(rot=keys([(0, *rot), (length, *rot)]))
        if moving:
            t.update(moving)
        return t

    # idle on the ground: folded wings, breathing, head looking around
    Li = 3.0
    idle = const(fold, Li)
    idle["body"] = track(rot=wave(8, lambda p: (tilt + 1.0 * math.sin(2 * math.pi * p), 0, 0), Li),
                         pos=wave(8, lambda p: (0, 0.2 * math.sin(2 * math.pi * p), 0), Li))
    idle["neck1"] = track(rot=wave(8, lambda p: (n1 + 3 * math.sin(2 * math.pi * (p + 0.1)), 6 * math.sin(2 * math.pi * p), 0), Li))
    idle["skull"] = track(rot=wave(8, lambda p: (sk + 2 * math.sin(2 * math.pi * (p + 0.3)), 0, 4 * math.sin(2 * math.pi * p)), Li))
    m.anim("idle", Li, True, idle)

    # walk / run on all fours: folded arms swing like front legs, opposite to the hind legs
    for name, (L, A) in spec["gait"].items():
        t = const(fold, L)
        for side, ph, s in (("l", 0.0, 1), ("r", 0.5, -1)):
            base1 = fold[f"wing1_{side}"]
            t[f"wing1_{side}"] = track(rot=wave(8, lambda p, ph=ph, b=base1: (b[0] + A * math.sin(2 * math.pi * (p + ph + 0.5)), b[1], b[2]), L))
            t[f"thigh_{side}"] = track(rot=wave(8, lambda p, ph=ph: (A * math.sin(2 * math.pi * (p + ph)), 0, 0), L))
            t[f"shin_{side}"] = track(rot=wave(8, lambda p, ph=ph: (-A * 0.8 * max(0.0, math.cos(2 * math.pi * (p + ph))), 0, 0), L))
            # toes lift as the leg trails behind, so they never dig into the ground
            t[f"foot_{side}"] = track(rot=wave(8, lambda p, ph=ph: (A * 0.6 * max(0.0, -math.sin(2 * math.pi * (p + ph))), 0, 0), L))
        t["body"] = track(rot=wave(8, lambda p: (tilt, 3 * math.sin(2 * math.pi * p), 2 * math.sin(2 * math.pi * p)), L),
                          pos=wave(8, lambda p: (0, 0.4 * math.cos(4 * math.pi * p), 0), L))
        m.anim(name, L, True, t)

    # flying: the rest pose is the spread wing; the legs trail behind
    legs_fly = spec.get("legs_fly", (-75, 10, -10))

    def air(L, flap, extra):
        t = {}
        for side in ("l", "r"):
            t[f"thigh_{side}"] = track(rot=keys([(0, legs_fly[0], 0, 0), (L, legs_fly[0], 0, 0)]))
            t[f"shin_{side}"] = track(rot=keys([(0, legs_fly[1], 0, 0), (L, legs_fly[1], 0, 0)]))
            t[f"foot_{side}"] = track(rot=keys([(0, legs_fly[2], 0, 0), (L, legs_fly[2], 0, 0)]))
        for side, s in (("l", 1), ("r", -1)):
            t[f"wing1_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * flap * math.sin(2 * math.pi * p)), L))
            t[f"wing2_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * flap * 0.6 * math.sin(2 * math.pi * (p - 0.12))), L))
            t[f"wing3_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * flap * 0.4 * math.sin(2 * math.pi * (p - 0.22))), L))
        t["body"] = track(rot=keys([(0, -4, 0, 0), (L, -4, 0, 0)]),
                          pos=wave(8, lambda p: (0, -0.8 * flap / 30 * math.sin(2 * math.pi * p), 0), L))
        t["neck1"] = track(rot=keys([(0, fn1, 0, 0), (L, fn1, 0, 0)]))
        t["skull"] = track(rot=keys([(0, fsk, 0, 0), (L, fsk, 0, 0)]))
        t.update(extra)
        return t
    fl = spec.get("flap", (0.8, 32))
    m.anim("fly", fl[0], True, air(fl[0], fl[1], {}))
    m.anim("glide", 3.0, True, air(3.0, 4, {
        "body": track(rot=wave(8, lambda p: (-4, 0, 5 * math.sin(2 * math.pi * p)), 3.0))}))

    # resting: folded, body down
    st = spec["sit"]
    joints = {k: v for k, v in fold.items() if k != "body" and not k.startswith("wing")}
    joints.update(tucked(spec.get("sit_wings", SIT_TUCK)))   # forelimbs folded along the body, hands on the ground
    for side in ("l", "r"):
        joints["@thigh_" + side] = (st["thigh"], 0, 0)
        joints["shin_" + side] = (st["shin"], 0, 0)
        joints["foot_" + side] = (st["foot"], 0, 0)
    joints["neck1"] = (st["neck"], 0, 0)
    joints["skull"] = (st["skull"], 0, 0)
    drop = ground_drop(m, sit_tracks(3.0, st["drop"], joints, extra=membranes_folded(3.0)), st["drop"])
    sit = sit_tracks(3.0, drop, joints, extra=membranes_folded(3.0))
    bp, bdy = st["body"]
    sit["body"] = track(pos=keys([(0, 0, -drop, 0), (1.5, 0, -drop + bdy, 0), (3.0, 0, -drop, 0)]),
                        rot=keys([(0, bp, 0, 0), (1.5, bp + 0.6, 0, 0), (3.0, bp, 0, 0)]))
    m.anim("sit", 3.0, True, sit)

    spec["attack"](m)
    spec.get("extra_anims", lambda m: None)(m)
    if spec.get("knockout", True):
        add_knockout_pterosaur(m, spec, fold)


SIT_TUCK = {"wing1": (0.1, -0.75, 0.65), "wing2": (0.0, -0.08, -1.0), "wing3": (0.0, 0.6, 0.8)}  # resting
KO_TUCK = {"wing1": (0.05, -0.45, 0.9), "wing2": (0.0, -0.05, -1.0), "wing3": (0.0, 0.25, 0.97)}  # wings tucked along the body


def tucked(dirs):
    """Wing rotations (body frame, no tilt) that lay the three wing bones along the given world directions."""
    import numpy as np
    R = np.eye(3)
    p = {}
    for bone in ("wing1", "wing2", "wing3"):
        rot, R = _aim(R, dirs[bone])
        p[bone + "_l"] = rot
        p[bone + "_r"] = (rot[0], -rot[1], -rot[2])
    return p


def add_knockout_pterosaur(m, spec, fold):
    """Knocked out: wings tucked along the body, lying on its side, neck down (docs/DOMESTICACAO.md).
    spec["ko"] = (roll, lift_frac, shift_frac); spec["ko_wings"] = tucked wing directions; spec["ko_joints"] = extra
    or overriding limp rotations (neck, skull, legs...)."""
    hip = spec["body"][0]
    limp = tucked(spec.get("ko_wings", KO_TUCK))
    limp.update({"neck1": (-6, 0, 0), "skull": (4, 0, 0), "jaw": (-8, 0, 0)})
    for side in ("l", "r"):
        limp[f"thigh_{side}"] = (40, 0, 0)
        limp[f"shin_{side}"] = (-30, 0, 0)
    limp.update(spec.get("ko_joints", {}))
    ko = spec.get("ko", (80, 0.3, 0.6))
    probe = knockout_tracks(4.0, ko[0], -ko[1] * hip, ko[2] * hip, limp)
    probe.update(membranes_folded(4.0))
    lift_px = ground_lift(m, probe, ko[1] * hip)        # lowest cube (beak, wing...) exactly on the ground
    t = knockout_tracks(4.0, ko[0], -lift_px, ko[2] * hip, limp)
    t.update(membranes_folded(4.0))
    m.anim("knocked_out", 4.0, True, t)
    add_wake(m, ko[0], lift_px, ko[2] * hip, limp)
    add_actions(m, neck_down=-45)
