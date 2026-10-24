"""
Archetype: large theropods (Tyrannosaurus, Spinosaurus and the other big two-legged predators). One rig and one
animation set (idle, walk, run, bite, roar, sit, knocked_out); a species gives a spec with its proportions, head,
claws, colours and pattern, plus optional hooks for special parts (Spinosaurus sail and tail fin). The in-game size
comes from the renderer scale (SIZES in tools/javagen/gen_species.py).

Spec keys (boxes are (x0, y0, z0, x1, y1, z1); head boxes are relative to the head anchor, -z = forward):
  palette, sexes, pattern   colours and the paint pattern function (see paint.py)
  body                      (y, z) of the body pivot
  torso                     [(name, box)] boxes of the body bone
  neck                      (points, sections) of the 2-bone neck chain; skull_tilt = extra skull pitch (deg)
  head                      [dict(bone="skull"|"jaw", box=..., name=..., tag=..., paint=..., inflate=...)]
  jaw_pivot                 (dy, dz) of the jaw hinge from the head anchor
  eyes                      (r, dy, dz, x) eye decals; extra_decals = more decals relative to the head anchor
  arm                       (x, points, sections, claws); claws = [(name, (dx0, dy0, dz0, dx1, dy1, dz1))] from the hand
  leg                       (x, points, sections, toes); toes = [(name, tag, box from the toes pivot)]
  tail                      (points, sections)
  saddle                    add_saddle(...) arguments after the bone, or None
  sit                       (drop, thigh, shin, foot, toes, {other joints}) resting pose
  after_torso(m), after_tail(m, tail)   hooks for special parts
  extra_anims(m)            hook for more animations (abelisaur charge)
"""
import math
from rig import Model, wave, sinx, track, keys, add_saddle, sit_tracks, add_knockout, ground_drop


def build(species_id, spec):
    m = Model(species_id, render_scale=1.0)
    m.palette = dict(spec["palette"])
    m.sexes = spec["sexes"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *spec["body"]))
    for name, (x0, y0, z0, x1, y1, z1) in spec["torso"]:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)
    if spec.get("after_torso"):
        spec["after_torso"](m)

    pts, secs = spec["neck"]
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(2.0, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))  # look bone (GeckoLib turns it)
    m.bone("skull", "head", (0, ay, az), (spec["skull_tilt"] - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)

    jaw_done = False
    for h in spec["head"]:
        if h["bone"] == "jaw" and not jaw_done:
            m.bone("jaw", "skull", (0, ay + spec["jaw_pivot"][0], az + spec["jaw_pivot"][1]))
            jaw_done = True
        kw = {k: h[k] for k in ("tag", "paint", "inflate") if k in h}
        m.box(h["bone"], *R(*h["box"]), name=h["name"], **kw)
    r, dy, dz, ex = spec["eyes"]
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (ex, ay + dy, az + dz), "r": r, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-ex, ay + dy, az + dz), "r": r, "side": -1},
    ]
    for d in spec.get("extra_decals", []):
        x, y, z = d["pos"]
        m.decals.append({**d, "pos": (x, ay + y, az + z)})

    ax, apts, asecs, claws = spec["arm"]

    def arm(side, sx):
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", ax * sx, apts, "-y", asecs, tag="limb", overlap=(1.0, 0.5))
        ey, ez = ch["end"]
        x = ax * sx
        for name, (x0, y0, z0, x1, y1, z1) in claws:
            m.box(f"forearm_{side}", (x + x0, ey + y0, ez + z0), (x + x1, ey + y1, ez + z1), tag="claw", name=name,
                  paint={"axis": "-y"})
    m.sym(arm)

    lx, lpts, lsecs, toes = spec["leg"]

    def leg(side, sx):
        x = lx * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(1.5, 1.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        for name, tag, (x0, y0, z0, x1, y1, z1) in toes:
            m.box(f"toes_{side}", (x + x0, by + y0, bz + z0), (x + x1, by + y1, bz + z1), tag=tag, name=name)
    m.sym(leg)

    tpts, tsecs = spec["tail"]
    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, tpts, "+z", tsecs, overlap=(1.0, 1.0))
    if spec.get("after_tail"):
        spec["after_tail"](m, tail)

    m.pattern = spec["pattern"]
    if spec.get("saddle"):
        add_saddle(m, "body", *spec["saddle"][0], **spec["saddle"][1])
    animations(m, spec["sit"])
    if spec.get("extra_anims"):
        spec["extra_anims"](m)
    return m


def animations(m, sit):
    def leg_cycle(length, A_th, A_sh, A_ft, n=8):
        tracks = {}
        for side, ph in (("l", 0.0), ("r", 0.5)):
            tracks[f"thigh_{side}"] = track(rot=wave(n, lambda p, ph=ph: (A_th * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
            tracks[f"shin_{side}"] = track(rot=wave(n, lambda p, ph=ph: (-A_sh * max(0.0, math.cos(2 * math.pi * (p + ph))) + 4, 0, 0), length))
            tracks[f"foot_{side}"] = track(rot=wave(n, lambda p, ph=ph: (A_ft * max(0.0, math.cos(2 * math.pi * (p + ph))) - 3 * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
            tracks[f"toes_{side}"] = track(rot=wave(n, lambda p, ph=ph: (12 * max(0.0, math.sin(2 * math.pi * (p + ph + 0.25))) * 0.6, 0, 0), length))
        return tracks

    # idle -------------------------------------------------------------
    Li = 4.0
    idle = {
        "body": track(rot=wave(8, sinx(0.7), Li), pos=wave(8, lambda p: (0, 0.3 * math.sin(2 * math.pi * p), 0), Li)),
        "neck1": track(rot=wave(8, sinx(1.6, 0.15), Li)),
        "skull": track(rot=wave(8, sinx(1.2, 0.3), Li)),
        "jaw": track(rot=wave(8, lambda p: (-3 * max(0.0, math.sin(2 * math.pi * p)), 0, 0), Li)),
        "arm_l": track(rot=wave(4, sinx(4, 0.1), Li)),
        "arm_r": track(rot=wave(4, sinx(4, 0.35), Li)),
    }
    for i, a in enumerate((2.5, 3.5, 4.5, 5.5)):
        idle[f"tail{i+1}"] = track(rot=wave(8, lambda p, a=a, i=i: (0.8 * math.sin(2 * math.pi * (p + 0.1 * i)), a * math.sin(2 * math.pi * (p - 0.08 * i)), 0), Li))
    m.anim("idle", Li, True, idle)

    # walk -------------------------------------------------------------
    Lw = 1.6
    walk = leg_cycle(Lw, 24, 26, 18)
    walk["body"] = track(rot=wave(8, lambda p: (0, 2.2 * math.sin(2 * math.pi * p), 1.6 * math.sin(2 * math.pi * p)), Lw),
                         pos=wave(8, lambda p: (0, 0.7 * math.cos(4 * math.pi * p) - 0.3, 0), Lw))
    walk["neck1"] = track(rot=wave(8, lambda p: (-2.0 * math.cos(4 * math.pi * p), -1.5 * math.sin(2 * math.pi * p), 0), Lw))
    walk["skull"] = track(rot=wave(8, lambda p: (1.5 * math.cos(4 * math.pi * p), 0, 0), Lw))
    for i, a in enumerate((3, 4, 5, 6)):
        walk[f"tail{i+1}"] = track(rot=wave(8, lambda p, a=a, i=i: (0.8 * math.cos(4 * math.pi * p), -a * math.sin(2 * math.pi * (p - 0.1 * (i + 1))), 0), Lw))
    walk["arm_l"] = track(rot=wave(4, sinx(6, 0.5), Lw))
    walk["arm_r"] = track(rot=wave(4, sinx(6, 0.0), Lw))
    m.anim("walk", Lw, True, walk)

    # run --------------------------------------------------------------
    Lr = 0.8
    run = leg_cycle(Lr, 36, 40, 26)
    run["body"] = track(rot=wave(8, lambda p: (-4, 2.5 * math.sin(2 * math.pi * p), 2.0 * math.sin(2 * math.pi * p)), Lr),
                        pos=wave(8, lambda p: (0, 1.3 * math.cos(4 * math.pi * p) - 0.8, 0), Lr))
    run["neck1"] = track(rot=wave(8, lambda p: (2 - 3 * math.cos(4 * math.pi * p), 0, 0), Lr))
    run["skull"] = track(rot=wave(8, lambda p: (2 + 2 * math.cos(4 * math.pi * p), 0, 0), Lr))
    run["jaw"] = track(rot=wave(8, lambda p: (-6 - 4 * math.cos(4 * math.pi * p), 0, 0), Lr))
    for i, a in enumerate((3, 4, 5, 6)):
        run[f"tail{i+1}"] = track(rot=wave(8, lambda p, a=a, i=i: (2 + 1.5 * math.cos(4 * math.pi * p), -a * math.sin(2 * math.pi * (p - 0.12 * (i + 1))), 0), Lr))
    m.anim("run", Lr, True, run)

    # attack (bite) ----------------------------------------------------
    La = 0.8
    attack = {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.2, 10, 0, 0), (0.38, -16, 0, 0), (0.55, -10, 0, 0), (0.8, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.2, 4, 0, 0), (0.38, -8, 0, 0), (0.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.2, 8, 0, 0), (0.38, -6, 0, 0), (0.8, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -32, 0, 0), (0.36, -36, 0, 0), (0.44, 0, 0, 0), (0.8, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.2, 2, 0, 0), (0.4, -4, 0, 0), (0.8, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.2, -2, 0, 0), (0.4, 4, 0, 0), (0.8, 0, 0, 0)])),
    }
    m.anim("attack", La, False, attack)

    # roar ---------------------------------------------------------------
    Lo = 2.4
    jaw_keys = [(0, 0, 0, 0), (0.35, -38, 0, 0)]
    t = 0.45
    while t < 1.75:
        jaw_keys.append((round(t, 2), -42 + (3 if int(t * 20) % 2 else -2), 0, 0))
        t += 0.15
    jaw_keys += [(1.95, -10, 0, 0), (2.4, 0, 0, 0)]
    roar = {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.4, 18, 0, 0), (1.0, 20, -4, 0), (1.6, 18, 4, 0), (2.0, 4, 0, 0), (2.4, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.4, 6, 0, 0), (1.6, 6, 0, 0), (2.4, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.4, 8, 0, 0), (1.0, 9, 0, 2), (1.6, 9, 0, -2), (2.4, 0, 0, 0)])),
        "jaw": track(rot=keys(jaw_keys)),
        "body": track(rot=keys([(0, 0, 0, 0), (0.4, 5, 0, 0), (1.6, 5, 0, 0), (2.4, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.4, 0, 0.6, 0), (1.6, 0, 0.6, 0), (2.4, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.4, -6, 0, 0), (1.6, -6, 0, 0), (2.4, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.4, -3, 4, 0), (1.0, -3, -4, 0), (1.6, -3, 4, 0), (2.4, 0, 0, 0)])),
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.4, -20, 0, -10), (1.6, -20, 0, -10), (2.4, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.4, -20, 0, 10), (1.6, -20, 0, 10), (2.4, 0, 0, 0)])),
    }
    m.anim("roar", Lo, False, roar)

    # resting: drops onto its belly with the legs folded
    drop, thigh, shin, foot, toes, other = sit
    joints = {}
    for side in ("l", "r"):
        joints["@thigh_" + side] = (thigh, 0, 0)
        joints["shin_" + side] = (shin, 0, 0)
        joints["foot_" + side] = (foot, 0, 0)
        joints["toes_" + side] = (toes, 0, 0)
    joints.update(other)
    drop = ground_drop(m, sit_tracks(4.0, drop, joints, breathe=0.4), drop)
    m.anim("sit", 4.0, True, sit_tracks(4.0, drop, joints, breathe=0.4))

    add_knockout(m, neck_down=-40)
