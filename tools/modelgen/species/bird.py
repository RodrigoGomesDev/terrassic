"""
Shared rig for birds (Ichthyornis, Hesperornis-like divers later, shoulder birds): feathered wings in two bones
(arm with the secondaries, hand with the long primaries), a short tail fan, thin legs, a toothed or toothless beak.

Small birds are modelled at 4x and scaled down by the renderer so the feathers keep some texture detail.

spec keys:
  render_scale, palette, sexes, pattern
  body=(y, z)              body pivot
  shoulder=(x, y, z)       left shoulder pivot
  wing=(ARM, HAND)         bone lengths (px, spread pose along +X)
  vanes=(sec, prim, tip)   feather chord behind the arm, behind the hand, at the wing tip
  fold=(arm_rot, hand_rot) local rotations (x, y, z) that fold the left wing along the body
  body_parts(m), leg(m, side, s), after_wings(m)   species geometry hooks
  neck_rest=(n1, skull), neck_fly=(n1, skull)       neck pitch on the ground / in the air
  legs_fly=(thigh, shin[, foot])   legs tucked in flight
  flap=(length, amplitude) wing beat
  gait={"walk": (L, A), "run": (L, A)}
  sit=dict(drop, thigh, shin, neck, skull[, foot, toes])   toes counter-rotate so the web stays flat
  attack(m)                species attack animation
  ko=(roll, lift_frac, shift_frac), ko_joints={}
"""
import math
from rig import Model, track, keys, wave, sit_tracks, knockout_tracks, add_wake, add_actions, ground_drop, ground_lift


def build(species_id, spec):
    m = Model(species_id, render_scale=spec.get("render_scale", 1.0))
    m.palette = dict(spec["palette"])
    m.sexes = spec["sexes"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *spec["body"]))
    spec["body_parts"](m)

    sx0, sy, sz = spec["shoulder"]
    ARM, HAND = spec["wing"]
    SEC, PRIM, TIP = spec["vanes"]

    def wing(side, s):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        x1, x2, x3 = sx0, sx0 + ARM, sx0 + ARM + HAND
        m.bone(f"wing1_{side}", "body", (x1 * s, sy, sz))
        a, b = X(x1, x2)
        m.box(f"wing1_{side}", (a, sy - 1, sz - 1), (b, sy + 1, sz + 1), tag="limb", name="arm")
        # secondaries: a vane hanging behind the arm
        m.box(f"wing1_{side}", (a, sy - 0.5, sz + 1), (b, sy + 0.5, sz + 1 + SEC), tag="feather", name="secondaries")
        m.bone(f"wing2_{side}", f"wing1_{side}", (x2 * s, sy, sz))
        a, b = X(x2, x3)
        m.box(f"wing2_{side}", (a, sy - 0.5, sz - 0.5), (b, sy + 0.5, sz + 0.5), tag="limb", name="hand")
        half = HAND // 2
        a, b = X(x2, x2 + half)
        m.box(f"wing2_{side}", (a, sy - 0.5, sz + 0.5), (b, sy + 0.5, sz + 0.5 + PRIM), tag="feather", name="primaries")
        a, b = X(x2 + half, x3)
        m.box(f"wing2_{side}", (a, sy - 0.5, sz + 0.5), (b, sy + 0.5, sz + 0.5 + TIP), tag="feather", name="primaries_tip")
        spec["leg"](m, side, s)
    m.sym(wing)
    spec.get("after_wings", lambda m: None)(m)
    m.pattern = spec["pattern"]
    animations(m, spec)
    return m


def _fold(spec):
    a, h = spec["fold"]
    return {"wing1_l": a, "wing1_r": (a[0], -a[1], -a[2]), "wing2_l": h, "wing2_r": (h[0], -h[1], -h[2])}


def animations(m, spec):
    n1, sk = spec["neck_rest"]
    fn1, fsk = spec["neck_fly"]
    fold = _fold(spec)

    def const(pose, length):
        return {bone: track(rot=keys([(0, *rot), (length, *rot)])) for bone, rot in pose.items()}

    # idle: wings folded, quick head movements like a real bird
    Li = 2.4
    idle = const(fold, Li)
    idle["body"] = track(pos=wave(8, lambda p: (0, 0.15 * math.sin(2 * math.pi * p), 0), Li))
    idle["neck1"] = track(rot=keys([(0, n1, 0, 0), (0.6, n1, 0, 0), (0.7, n1, 0, 0), (0.75, n1 + 4, 25, 0), (1.5, n1 + 4, 25, 0),
                                   (1.6, n1, -20, 0), (2.1, n1, -20, 0), (2.4, n1, 0, 0)]))
    idle["skull"] = track(rot=keys([(0, sk, 0, 0), (0.75, sk + 6, 0, 12), (1.5, sk + 6, 0, 12), (1.6, sk - 2, 0, -8), (2.4, sk, 0, 0)]))
    idle["tail"] = track(rot=wave(8, lambda p: (3 * math.sin(2 * math.pi * p), 0, 0), Li))
    m.anim("idle", Li, True, idle)

    # walk / run: a bird's bobbing walk; the wings stay folded
    for name, (L, A) in spec["gait"].items():
        t = const(fold, L)
        for side, ph in (("l", 0.0), ("r", 0.5)):
            t[f"thigh_{side}"] = track(rot=wave(8, lambda p, ph=ph: (A * math.sin(2 * math.pi * (p + ph)), 0, 0), L))
            t[f"shin_{side}"] = track(rot=wave(8, lambda p, ph=ph: (-A * 0.9 * max(0.0, math.cos(2 * math.pi * (p + ph))), 0, 0), L))
            t[f"foot_{side}"] = track(rot=wave(8, lambda p, ph=ph: (A * 0.5 * max(0.0, -math.sin(2 * math.pi * (p + ph))), 0, 0), L))
        t["body"] = track(rot=wave(8, lambda p: (0, 4 * math.sin(2 * math.pi * p), 3 * math.sin(2 * math.pi * p)), L),
                          pos=wave(8, lambda p: (0, 0.4 * abs(math.sin(2 * math.pi * p)), 0), L))
        t["neck1"] = track(rot=wave(8, lambda p: (n1 + 8 * math.cos(4 * math.pi * p), 0, 0), L))   # head bob
        t["skull"] = track(rot=wave(8, lambda p: (sk - 6 * math.cos(4 * math.pi * p), 0, 0), L))
        m.anim(name, L, True, t)

    # flying: spread wings beating from the shoulder, hand following; legs tucked under the tail
    legs_fly = spec.get("legs_fly", (-70, 30))

    def air(L, flap, extra):
        t = {}
        for side in ("l", "r"):
            t[f"thigh_{side}"] = track(rot=keys([(0, legs_fly[0], 0, 0), (L, legs_fly[0], 0, 0)]))
            t[f"shin_{side}"] = track(rot=keys([(0, legs_fly[1], 0, 0), (L, legs_fly[1], 0, 0)]))
            if len(legs_fly) > 2:
                t[f"foot_{side}"] = track(rot=keys([(0, legs_fly[2], 0, 0), (L, legs_fly[2], 0, 0)]))
        for side, s in (("l", 1), ("r", -1)):
            t[f"wing1_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * flap * math.sin(2 * math.pi * p)), L))
            t[f"wing2_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * flap * 0.7 * math.sin(2 * math.pi * (p - 0.15))), L))
        t["body"] = track(rot=keys([(0, -6, 0, 0), (L, -6, 0, 0)]),
                          pos=wave(8, lambda p: (0, -0.6 * flap / 40 * math.sin(2 * math.pi * p), 0), L))
        t["neck1"] = track(rot=keys([(0, fn1, 0, 0), (L, fn1, 0, 0)]))
        t["skull"] = track(rot=keys([(0, fsk, 0, 0), (L, fsk, 0, 0)]))
        t["tail"] = track(rot=keys([(0, 8, 0, 0), (L, 8, 0, 0)]))
        t.update(extra)
        return t
    fl = spec.get("flap", (0.5, 40))
    m.anim("fly", fl[0], True, air(fl[0], fl[1], {}))
    m.anim("glide", 2.0, True, air(2.0, 3, {"body": track(rot=wave(8, lambda p: (-6, 0, 6 * math.sin(2 * math.pi * p)), 2.0))}))

    # resting / perched: legs folded, body down, wings folded
    st = spec["sit"]
    joints = dict(fold)
    for side in ("l", "r"):
        joints["@thigh_" + side] = (st["thigh"], 0, 0)
        joints["shin_" + side] = (st["shin"], 0, 0)
        if "foot" in st:
            joints["foot_" + side] = (st["foot"], 0, 0)
        if "toes" in st:
            joints["toes_" + side] = (st["toes"], 0, 0)
    joints["neck1"] = (st["neck"], 0, 0)
    joints["skull"] = (st["skull"], 0, 0)
    drop = ground_drop(m, sit_tracks(3.0, st["drop"], joints), st["drop"])
    m.anim("sit", 3.0, True, sit_tracks(3.0, drop, joints, breathe=0.15))

    spec["attack"](m)
    spec.get("extra_anims", lambda m: None)(m)

    # knocked out: on its side, wings folded, neck limp
    hip = spec["body"][0]
    limp = dict(fold)
    limp.update({"neck1": (-20, 0, 0), "skull": (10, 0, 0), "jaw": (-10, 0, 0)})
    for side in ("l", "r"):
        limp[f"thigh_{side}"] = (30, 0, 0)
        limp[f"shin_{side}"] = (-20, 0, 0)
    limp.update(spec.get("ko_joints", {}))
    ko = spec.get("ko", (85, 0.3, 0.5))
    lift_px = ground_lift(m, knockout_tracks(4.0, ko[0], -ko[1] * hip, ko[2] * hip, limp), ko[1] * hip)
    m.anim("knocked_out", 4.0, True, knockout_tracks(4.0, ko[0], -lift_px, ko[2] * hip, limp))
    add_wake(m, ko[0], lift_px, ko[2] * hip, limp)
    add_actions(m, neck_down=-40, chew=-10)
