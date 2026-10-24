"""
Archetype: crocodylomorphs (Deinosuchus now, Baurusuchus with upright legs next, Sarcosuchus and the Triassic
sphenosuchians later). A long low body with rows of osteoderm scutes, a thick neck, a flat skull with long toothed
jaws, four limbs that sprawl out sideways (the "high walk" lifts the belly; the sprawl angle is a parameter, so an
upright runner like Baurusuchus uses the same rig), a long tail with a crest, and the animation set: idle, walk (high
walk), run (the gallop-like bound), sit (basking flat on the belly, legs splayed), attack (hook: the sideways head
sweep and jaw snap by default), knocked_out / wake / eat / beg / tame.

Spec keys:
  render_scale, palette, sexes, pattern   as in the other archetypes
  body                    (y, z) of the body pivot
  body_parts(m)           hook: torso, belly, scute rows
  neck                    dict(points=[(y, z), (y, z)], sections=[(w, h)])   one thick segment, "-z"
  head(m, ay, az, abs)    hook: skull / snout / jaw at the neck's end
  tail                    dict(points=[(y, z) ...], sections=[(w, h) ...], crest=[(segment_index, height) ...])
  legs                    dict(front=LEG, hind=LEG) with LEG = dict(pivot=(x, y, z), upper=(length, w, h),
                               sprawl=deg, lower=(length, w, d), foot=(w, length, thickness, forward))
                          the upper limb points +x from the pivot and is rolled down by `sprawl`; the lower limb
                          hangs vertical from its end; the foot is a flat box under it, `forward` px ahead
  gait                    dict(walk=(L, swing, bob, sway), run=(L, swing, bob, sway))
  sit                     dict(drop, upper, lower, neck, tail)     resting rotations (x) and the body drop
  attack(m)               optional hook; default = sideways sweep + snap
  ko                      dict(roll, lift, shift, joints, neck_down) for rig.add_knockout
"""
import math
from rig import Model, track, wave, keys, sit_tracks, ground_drop, add_knockout


def _leg(m, side, s, parent, prefix_upper, prefix_lower, leg):
    px, py, pz = leg["pivot"]
    ul, uw, uh = leg["upper"]
    ll, lw, ld = leg["lower"]
    fw, fl, ft, ff = leg["foot"]
    sprawl = leg["sprawl"]
    up = f"{prefix_upper}_{side}"
    lo = f"{prefix_lower}_{side}"
    # upper limb: a box pointing +x (outwards), rolled down around z by the sprawl angle
    m.bone(up, parent, (px * s, py, pz), (0, 0, -sprawl * s))
    x0, x1 = sorted((px * s, (px + ul) * s))
    m.box(up, (x0, py - uh / 2, pz - uw / 2), (x1, py + uh / 2, pz + uw / 2), tag="limb", name="upper")
    # lower limb: hangs from the upper limb's end; counter-rolled so it stands vertical in the rest pose
    ex, ey = px + ul * math.cos(math.radians(sprawl)), py - ul * math.sin(math.radians(sprawl))
    # the child pivot is given in the parent's (rolled) frame: the end of the upper box
    m.bone(lo, up, ((px + ul) * s, py, pz), (0, 0, sprawl * s))
    lx = (px + ul) * s
    m.box(lo, (min(lx - lw / 2 * s, lx + lw / 2 * s), py - ll, pz - ld / 2),
          (max(lx - lw / 2 * s, lx + lw / 2 * s), py, pz + ld / 2), tag="limb", name="lower")
    m.box(lo, (min(lx - fw / 2 * s, lx + fw / 2 * s), py - ll - ft, pz - fl + ff),
          (max(lx - fw / 2 * s, lx + fw / 2 * s), py - ll, pz + ff), tag="limb", name="foot")
    # three claws at the front of the foot
    for k in range(3):
        cx = lx - fw / 2 * s + (0.5 + k) * (fw / 3) * s
        m.box(lo, (min(cx - 0.5, cx + 0.5), py - ll - ft, pz - fl + ff - 2), (max(cx - 0.5, cx + 0.5), py - ll - ft + 1, pz - fl + ff),
              tag="claw", name="claw")
    return ey


def build(species_id, spec):
    m = Model(species_id, render_scale=spec.get("render_scale", 1.0))
    m.palette = dict(spec["palette"])
    m.sexes = spec["sexes"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *spec["body"]))
    spec["body_parts"](m)

    nk = spec["neck"]
    neck = m.chain(["neck1"], "body", 0, nk["points"], "-z", nk["sections"], overlap=(1.0, 0.0))
    ay, az = neck["end"]
    m.bone("head", "neck1", (0, ay, az))
    spec["head"](m, ay, az, neck["abs"])

    tl = spec["tail"]
    tails = [f"tail{i + 1}" for i in range(len(tl["points"]) - 1)]
    tail = m.chain(tails, "body", 0, tl["points"], "+z", tl["sections"], overlap=(1.0, 1.0))
    for k, extra in tl.get("crest", []):
        sg = tail["segments"][k - 1]
        y0, z0 = sg["unposed"]
        L = int(round(sg["len"]))
        h = tl["sections"][k - 1][1] / 2
        m.box(f"tail{k}", (-1, y0 + h - 1, z0), (1, y0 + h - 1 + extra, z0 + L), name="crest", tag="scute")

    lg = spec["legs"]

    def legs(side, s):
        _leg(m, side, s, "body", "upperarm", "forearm", lg["front"])
        _leg(m, side, s, "body", "thigh", "shin", lg["hind"])
    m.sym(legs)

    m.pattern = spec["pattern"]
    animations(m, spec, tails)
    return m


def gait(L, swing, bob, sway, tails):
    """High walk: diagonal pairs, the upper limb swinging fore and aft, the lower limb lifting on the recovery; the
    spine bends side to side with the steps and the tail swings against it."""
    t = {}
    for side, s, ph in (("l", 1, 0.0), ("r", -1, 0.5)):
        for up, lo, p0 in (("upperarm", "forearm", ph + 0.25), ("thigh", "shin", ph)):
            t[f"{up}_{side}"] = track(rot=wave(8, lambda p, p0=p0, s=s: (
                swing * math.sin(2 * math.pi * (p + p0)), 0, 0), L))
            t[f"{lo}_{side}"] = track(rot=wave(8, lambda p, p0=p0: (
                -swing * 0.8 * max(0.0, math.cos(2 * math.pi * (p + p0))), 0, 0), L))
    t["body"] = track(rot=wave(8, lambda p: (0, sway * math.sin(2 * math.pi * p), 0), L),
                      pos=wave(8, lambda p: (0, bob * math.cos(4 * math.pi * p) - bob * 0.5, 0), L))
    t["neck1"] = track(rot=wave(8, lambda p: (0, -sway * 1.5 * math.sin(2 * math.pi * p), 0), L))
    for i, b in enumerate(tails):
        t[b] = track(rot=wave(8, lambda p, i=i: (0, -(sway * 1.2 + 2.5 * i) * math.sin(2 * math.pi * (p - 0.12 * i)), 0), L))
    return t


def default_attack(m, tails):
    # the sideways sweep: head swings out, jaws gape, then snaps back across with the bite
    a = {
        "body": track(rot=keys([(0, 0, 0, 0), (0.25, 0, 10, 0), (0.45, 0, -8, 0), (0.8, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.25, 0, 0, 1), (0.45, 0, 0, -3), (0.8, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.25, 10, 22, 0), (0.45, -2, -16, 0), (0.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.25, 22, 0, 0), (0.44, 16, 0, 0), (0.55, -2, 0, 0), (0.8, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -28, 0, 0), (0.38, -32, 0, 0), (0.44, 0, 0, 0), (0.8, 0, 0, 0)])),
    }
    for i, b in enumerate(tails):
        a[b] = track(rot=keys([(0, 0, 0, 0), (0.25, 0, -12 - 4 * i, 0), (0.45, 0, 10 + 3 * i, 0), (0.8, 0, 0, 0)]))
    m.anim("attack", 0.8, False, a)


def animations(m, spec, tails):
    Li = 4.0
    idle = {
        "body": track(pos=wave(8, lambda p: (0, 0.3 * math.sin(2 * math.pi * p), 0), Li)),
        "neck1": track(rot=wave(8, lambda p: (1.5 * math.sin(2 * math.pi * p), 3 * math.sin(2 * math.pi * (p + 0.3)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (1.0 * math.sin(2 * math.pi * (p + 0.2)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-5 * max(0.0, math.sin(2 * math.pi * p)), 0, 0), Li)),   # mouth gaping to cool
    }
    for i, b in enumerate(tails):
        idle[b] = track(rot=wave(8, lambda p, i=i: (0, (2 + 1.5 * i) * math.sin(2 * math.pi * (p - 0.1 * i)), 0), Li))
    m.anim("idle", Li, True, idle)
    g = spec["gait"]
    for name in ("walk", "run"):
        L, swing, bob, sway = g[name]
        m.anim(name, L, True, gait(L, swing, bob, sway, tails))

    st = spec["sit"]
    joints = {}
    for side, s in (("l", 1), ("r", -1)):
        joints[f"upperarm_{side}"] = (st["upper"], 0, 0)
        joints[f"forearm_{side}"] = (st["lower"], 0, st.get("lower_roll", 0) * s)
        joints[f"thigh_{side}"] = (st["upper"], 0, 0)
        joints[f"shin_{side}"] = (st["lower"], 0, st.get("lower_roll", 0) * s)
    joints["neck1"] = (st["neck"], 0, 0)
    for i, b in enumerate(tails):
        joints[b] = (st["tail"], 2 * (i + 1), 0)
    drop = ground_drop(m, sit_tracks(4.0, st["drop"], joints), st["drop"])
    m.anim("sit", 4.0, True, sit_tracks(4.0, drop, joints))

    if spec.get("attack"):
        spec["attack"](m, tails)
    else:
        default_attack(m, tails)
    spec.get("extra_anims", lambda m: None)(m)
    ko = spec["ko"]
    add_knockout(m, roll=ko["roll"], lift=ko["lift"], shift=ko["shift"], joints=ko["joints"], neck_down=ko["neck_down"])
