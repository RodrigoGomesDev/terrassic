"""
Archetype: abelisaurids (Carnotaurus, Majungasaurus). The large theropod rig (large_theropod.py) with what makes an
abelisaur an abelisaur: a short, deep, bull-like skull (horns or a dome from the species), stub arms with no real
forearm, long slender legs built for speed, a thick-based tail (the big caudofemoralis muscle), rows of osteoderm
scutes along the back and flanks, and a "charge" animation: the head-down sprint of the fastest big predators.

Spec: everything large_theropod takes, plus
  scutes      (x, y, z0, z1, step) rows of 1 px scutes on the body bone, mirrored, plus a dorsal row at y+2
  charge      (length, stride) of the charge cycle (default (0.6, 44))
"""
import math
import large_theropod
from rig import wave, sinx, track


def _scutes(spec):
    def hook(m):
        if spec.get("after_torso_species"):
            spec["after_torso_species"](m)
        x, y, z0, z1, step = spec["scutes"]
        for z in range(z0, z1, step):
            m.box("body", (x, y, z), (x + 1, y + 1, z + 1), name="scute", tag="scute")
            m.box("body", (-x - 1, y, z), (-x, y + 1, z + 1), name="scute", tag="scute")
            if (z - z0) // step % 2 == 0:
                m.box("body", (-0.5, y + 2, z + 1), (0.5, y + 3, z + 2), name="scute", tag="scute")
    return hook


def _charge(spec):
    length, stride = spec.get("charge", (0.6, 44))

    def hook(m):
        tracks = {}
        for side, ph in (("l", 0.0), ("r", 0.5)):
            tracks[f"thigh_{side}"] = track(rot=wave(8, lambda p, ph=ph: (stride * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
            tracks[f"shin_{side}"] = track(rot=wave(8, lambda p, ph=ph: (-46 * max(0.0, math.cos(2 * math.pi * (p + ph))) + 6, 0, 0), length))
            tracks[f"foot_{side}"] = track(rot=wave(8, lambda p, ph=ph: (30 * max(0.0, math.cos(2 * math.pi * (p + ph))) - 4 * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
            tracks[f"toes_{side}"] = track(rot=wave(8, lambda p, ph=ph: (10 * max(0.0, math.sin(2 * math.pi * (p + ph + 0.25))), 0, 0), length))
        # the body levels and leans in, the head drops behind the horns, the tail rises stiff as a rudder
        tracks["body"] = track(rot=wave(8, lambda p: (-9, 1.5 * math.sin(2 * math.pi * p), 2.5 * math.sin(2 * math.pi * p)), length),
                               pos=wave(8, lambda p: (0, 1.6 * math.cos(4 * math.pi * p) - 1.0, 0), length))
        tracks["neck1"] = track(rot=wave(8, lambda p: (14 - 2 * math.cos(4 * math.pi * p), 0, 0), length))
        tracks["neck2"] = track(rot=wave(8, lambda p: (8, 0, 0), length))
        tracks["skull"] = track(rot=wave(8, lambda p: (-6 + 2 * math.cos(4 * math.pi * p), 0, 0), length))
        tracks["jaw"] = track(rot=wave(8, lambda p: (-8 - 3 * math.cos(4 * math.pi * p), 0, 0), length))
        for i, a in enumerate((2, 3, 4, 5)):
            tracks[f"tail{i+1}"] = track(rot=wave(8, lambda p, a=a, i=i: (-3 + 1.5 * math.cos(4 * math.pi * p), -a * math.sin(2 * math.pi * (p - 0.12 * (i + 1))), 0), length))
        tracks["arm_l"] = track(rot=wave(4, sinx(5, 0.5, -10), length))
        tracks["arm_r"] = track(rot=wave(4, sinx(5, 0.0, -10), length))
        m.anim("charge", length, True, tracks)
    return hook


def build(species_id, spec):
    spec = dict(spec)
    if spec.get("after_torso"):
        spec["after_torso_species"] = spec["after_torso"]
    spec["after_torso"] = _scutes(spec)
    spec["extra_anims"] = _charge(spec)
    return large_theropod.build(species_id, spec)
