"""Shared limb helpers + gait for big quadrupeds (Triceratops, Stegosaurus)."""
import math
from rig import wave, track, keys, sit_tracks


def hind_leg(m, side, sx, x, pts, secs, pad):
    ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x * sx, pts, "-y", secs, overlap=(1.5, 1.0))
    by, bz = ch["end"]
    xx = x * sx
    m.bone(f"toes_{side}", f"foot_{side}", (xx, by, bz), (-ch["abs"], 0, 0))
    w, l0, l1 = pad
    m.box(f"toes_{side}", (xx - w / 2, by - 2, bz - l0), (xx + w / 2, by, bz + l1), tag="limb", name="pad")
    # three hoof-like claws
    for k, dx in enumerate((-w / 2 + 0.0, -0.5, w / 2 - 1.0)):
        x0 = xx + dx if k != 1 else xx - 0.5
        m.box(f"toes_{side}", (x0, by - 2, bz - l0 - 1), (x0 + 1, by - 1, bz - l0), tag="claw", name="hoof")


def front_leg(m, side, sx, x, pts, secs, pad):
    ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x * sx, pts, "-y", secs, overlap=(1.5, 1.0))
    by, bz = ch["end"]
    xx = x * sx
    m.bone(f"hand_{side}", f"forearm_{side}", (xx, by, bz), (-ch["abs"], 0, 0))
    w, l0, l1 = pad
    m.box(f"hand_{side}", (xx - w / 2, by - 2, bz - l0), (xx + w / 2, by, bz + l1), tag="limb", name="hand")
    for dx in (-w / 2, -0.5, w / 2 - 1):
        m.box(f"hand_{side}", (xx + dx, by - 2, bz - l0 - 1), (xx + dx + 1, by - 1, bz - l0), tag="claw", name="hoof")


def quad_gait(length, A_hind, A_front, n=8):
    """Lateral-sequence walk: LH, LF, RH, RF each a quarter cycle apart."""
    t = {}
    phases = {"l": 0.0, "r": 0.5}
    for side, ph in phases.items():
        fph = ph + 0.25
        t[f"thigh_{side}"] = track(rot=wave(n, lambda p, ph=ph: (A_hind * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
        t[f"shin_{side}"] = track(rot=wave(n, lambda p, ph=ph: (-A_hind * 0.9 * max(0.0, math.cos(2 * math.pi * (p + ph))), 0, 0), length))
        t[f"foot_{side}"] = track(rot=wave(n, lambda p, ph=ph: (A_hind * 0.6 * max(0.0, math.cos(2 * math.pi * (p + ph))) - 0.25 * A_hind * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
        t[f"upperarm_{side}"] = track(rot=wave(n, lambda p, ph=fph: (A_front * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
        t[f"forearm_{side}"] = track(rot=wave(n, lambda p, ph=fph: (A_front * 1.1 * max(0.0, math.cos(2 * math.pi * (p + ph))), 0, 0), length))
        t[f"hand_{side}"] = track(rot=wave(n, lambda p, ph=fph: (-A_front * 0.8 * max(0.0, math.cos(2 * math.pi * (p + ph))) - 0.3 * A_front * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
    return t


def quad_sit(m, drop, hind=(50, -95, 45), front=(-35, 95, -50), tail=(6, 3), neck=-8, length=4.0):
    """Resting pose: belly on the ground, legs folded under the body."""
    joints = {}
    for side in ("l", "r"):
        joints["@thigh_" + side] = (hind[0], 0, 0)
        joints["shin_" + side] = (hind[1], 0, 0)
        joints["foot_" + side] = (hind[2], 0, 0)
        joints["upperarm_" + side] = (front[0], 0, 0)
        joints["forearm_" + side] = (front[1], 0, 0)
        joints["hand_" + side] = (front[2], 0, 0)
    joints["tail1"] = (tail[0], 0, 0)
    joints["tail2"] = (tail[1], 0, 0)
    joints["neck1"] = (neck, 0, 0)
    tr = sit_tracks(length, drop, joints)
    # front legs hang from the body, so they go down with it automatically
    return tr


def quad_anims(m, ntail, nneck=2, walk=(1.8, 18, 18, 0.6), run=(0.9, 28, 28, 1.1), attack="headbutt",
               sit_drop=8, graze_neck=-22, graze_skull=-16, sit_kw=None, extra=None):
    """Standard animation set for quadrupeds: idle, walk, run, sit, graze and an attack style:
    'headbutt' (lower the head and thrust up), 'tail' (big sideways tail swing), 'stomp' (rear up)."""
    from rig import sinx
    Li = 4.0
    sy = lambda a, ph=0.0: (lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0))
    idle = {
        "body": track(rot=wave(8, sinx(0.5), Li), pos=wave(8, lambda p: (0, 0.25 * math.sin(2 * math.pi * p), 0), Li)),
        "neck1": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * p), 2.5 * math.sin(2 * math.pi * (p + 0.3)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (1.5 * math.sin(2 * math.pi * (p + 0.2)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-4 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
    }
    for i in range(2, nneck + 1):
        idle[f"neck{i}"] = track(rot=wave(8, lambda p, i=i: (1.2 * math.sin(2 * math.pi * (p + 0.1 * i)), 1.5 * math.sin(2 * math.pi * (p + 0.3 + 0.1 * i)), 0), Li))
    for i in range(ntail):
        idle[f"tail{i+1}"] = track(rot=wave(8, sy(3 + 1.2 * i, -0.08 * i), Li))
    m.anim("idle", Li, True, idle)
    for name, (Lc, Ah, Af, bob) in (("walk", walk), ("run", run)):
        t = quad_gait(Lc, Ah, Af)
        t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 1.5 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, b=bob: (0, b * math.cos(4 * math.pi * p) - b * 0.5, 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, b=bob: (-2 * b * math.cos(4 * math.pi * p), 0, 0), Lc))
        for i in range(ntail):
            t[f"tail{i+1}"] = track(rot=wave(8, sy(3 + 1.2 * i, 0.25 - 0.08 * i), Lc))
        m.anim(name, Lc, True, t)
    if attack == "headbutt":
        m.anim("attack", 0.9, False, {
            "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, -14, 0, 0), (0.5, 12, 0, 0), (0.9, 0, 0, 0)])),
            "skull": track(rot=keys([(0, 0, 0, 0), (0.3, -12, 0, 0), (0.5, 14, 0, 0), (0.9, 0, 0, 0)])),
            "body": track(rot=keys([(0, 0, 0, 0), (0.3, -3, 0, 0), (0.5, 3, 0, 0), (0.9, 0, 0, 0)]),
                          pos=keys([(0, 0, 0, 0), (0.3, 0, -0.6, -1.5), (0.5, 0, 0.2, -3), (0.9, 0, 0, 0)])),
        })
    elif attack == "tail":
        a = {"body": track(rot=keys([(0, 0, 0, 0), (0.3, 0, 10, 0), (0.55, 0, -14, 0), (1.0, 0, 0, 0)])),
             "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, 0, -8, 0), (0.55, 0, 8, 0), (1.0, 0, 0, 0)]))}
        for i in range(ntail):
            a[f"tail{i+1}"] = track(rot=keys([(0, 0, 0, 0), (0.3, -3, 14, 0), (0.55, -3, -24, 0), (1.0, 0, 0, 0)]))
        m.anim("attack", 1.0, False, a)
    elif attack == "stomp":
        a = {"body": track(rot=keys([(0, 0, 0, 0), (0.45, 16, 0, 0), (0.7, -2, 0, 0), (1.2, 0, 0, 0)]),
                           pos=keys([(0, 0, 0, 0), (0.45, 0, 2, 2), (0.7, 0, -1, -1), (1.2, 0, 0, 0)])),
             "neck1": track(rot=keys([(0, 0, 0, 0), (0.45, -10, 0, 0), (0.7, 4, 0, 0), (1.2, 0, 0, 0)]))}
        for side in ("l", "r"):
            a[f"upperarm_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.45, -30, 0, 0), (0.7, 6, 0, 0), (1.2, 0, 0, 0)]))
            a[f"forearm_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.45, 40, 0, 0), (0.7, 0, 0, 0), (1.2, 0, 0, 0)]))
        for i in range(ntail):
            a[f"tail{i+1}"] = track(rot=keys([(0, 0, 0, 0), (0.45, 8, 0, 0), (1.2, 0, 0, 0)]))
        m.anim("attack", 1.2, False, a)
    m.anim("sit", 4.0, True, quad_sit(m, sit_drop, **(sit_kw or {})))
    jk = [(0, 0, 0, 0), (0.6, 0, 0, 0)]
    for k in range(6):
        t0 = 0.75 + k * 0.3
        jk += [(t0, -10, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(2.8, 0, 0, 0)]
    g = {"neck1": track(rot=keys([(0, 0, 0, 0), (0.6, graze_neck, 0, 0), (2.3, graze_neck, 0, 0), (2.8, 0, 0, 0)])),
         "skull": track(rot=keys([(0, 0, 0, 0), (0.6, graze_skull, 0, 0), (2.3, graze_skull, 0, 0), (2.8, 0, 0, 0)])),
         "jaw": track(rot=keys(jk))}
    m.anim("graze", 2.8, False, g)
    for name, (length, loop, tracks) in (extra or {}).items():
        m.anim(name, length, loop, tracks)
