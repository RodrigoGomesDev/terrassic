"""Shared limb helpers + gait for big quadrupeds (Triceratops, Stegosaurus)."""
import math
from rig import wave, track


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
