"""
Archetype: sea turtles (Archelon now; Protostega and the Triassic Odontochelys later with their own shell hooks).
A shell body built by the species hook, a short neck with a beaked head, a short tail, two big front flippers that
"fly" under water and two small hind flippers used as rudders, and the shared animation set: idle, walk, run, sit
(resting afloat with the flippers tucked), attack (the neck shoots out and the beak snaps), knocked_out / wake /
eat / beg / tame. Knocked out it lies on its back.

Spec keys:
  render_scale            model pixel scale (in-game size comes from SIZES in tools/javagen/gen_species.py)
  palette, sexes, pattern colours and paint pattern (see paint.py)
  body                    (y, z) of the body pivot
  body_parts(m)           hook: the shell (carapace, rim, keel, plastron) and anything else on the body
  neck                    dict(points=[(y, z) ...], sections=[(w, h) ...])   from the shell forward ("-z")
  head(m, ay, az, abs)    hook: builds skull/beak/jaw at the neck's end (abs = neck's accumulated pitch)
  tail                    dict(points=[(y, z) ...], sections=[(w, h) ...])
  flippers                [dict(name, pivot=(x, y, z), rot=(x, y, z), boxes=[(x0, x1, y0, y1, z0, z1) ...]) ...]
                          left-side values; the right side is mirrored (x and the y/z rotations flip sign).
                          The first entry is the front pair (the power stroke), the rest steer.
  swim                    dict(idle=(L, stroke, sway), walk=..., run=..., sit=(L, stroke, sway, tuck))
  attack(m, necks)        hook that adds the attack animation
  extra_anims(m)          optional hook for more animations
  ko                      dict(roll, lift, shift, joints, neck_down) for rig.add_knockout (roll ~172 = on its back)
"""
import math
from rig import Model, track, wave, add_knockout


def build(species_id, spec):
    m = Model(species_id, render_scale=spec.get("render_scale", 1.0))
    m.palette = dict(spec["palette"])
    m.sexes = spec["sexes"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *spec["body"]))
    spec["body_parts"](m)

    nk = spec["neck"]
    necks = [f"neck{i + 1}" for i in range(len(nk["points"]) - 1)]
    neck = m.chain(necks, "body", 0, nk["points"], "-z", nk["sections"], overlap=(1.0, 0.0))
    ay, az = neck["end"]
    m.bone("head", necks[-1], (0, ay, az))
    spec["head"](m, ay, az, neck["abs"])

    tl = spec["tail"]
    tails = [f"tail{i + 1}" for i in range(len(tl["points"]) - 1)]
    m.chain(tails, "body", 0, tl["points"], "+z", tl["sections"], overlap=(1.0, 1.0))

    def flippers(side, s):
        for f in spec["flippers"]:
            px, py, pz = f["pivot"]
            rx, ry, rz = f["rot"]
            name = f"{f['name']}_{side}"
            m.bone(name, "body", (px * s, py, pz), (rx, ry * s, rz * s))
            for k, (x0, x1, y0, y1, z0, z1) in enumerate(f["boxes"]):
                a, b = min(x0 * s, x1 * s), max(x0 * s, x1 * s)
                m.box(name, (a, y0, z0), (b, y1, z1), tag="fin", name="paddle" if k == 0 else f"paddle{k + 1}")
    m.sym(flippers)

    m.pattern = spec["pattern"]
    animations(m, spec, necks, tails, [f["name"] for f in spec["flippers"]])
    return m


def swim(necks, tails, flipper_names, L, stroke, sway, tuck=0.0):
    """Underwater flight: the front flippers beat down and back, feathering on the way up; the hind pair just steers.
    The body rocks a little, the neck sways and the tail trails."""
    t = {}
    for k, name in enumerate(flipper_names):
        front = k == 0
        amp = stroke if front else stroke * 0.3
        ph = 0.0 if front else 0.35
        for side, s in (("l", 1), ("r", -1)):
            t[f"{name}_{side}"] = track(rot=wave(8, lambda p, s=s, amp=amp, ph=ph, front=front: (
                amp * 0.4 * math.cos(2 * math.pi * (p + ph)) * (1 if front else 0.5),
                s * tuck * (-1 if front else -0.6),
                s * amp * math.sin(2 * math.pi * (p + ph))), L))
    t["body"] = track(rot=wave(8, lambda p: (1.5 * math.sin(2 * math.pi * p), 0, 0), L),
                      pos=wave(8, lambda p: (0, 0.4 * math.sin(2 * math.pi * p), 0), L))
    for i, b in enumerate(necks):
        t[b] = track(rot=wave(8, lambda p, i=i: (0.5 * sway * math.sin(2 * math.pi * p),
                                                  sway * math.sin(2 * math.pi * (p * 0.5 - 0.1 * i)), 0), L))
    for i, b in enumerate(tails):
        t[b] = track(rot=wave(8, lambda p, i=i: (0, 4.0 * (i + 1) * math.sin(2 * math.pi * (p - 0.15 * i)), 0), L))
    return t


def animations(m, spec, necks, tails, flipper_names):
    sw = spec["swim"]
    for name in ("idle", "walk", "run", "sit"):
        m.anim(name, sw[name][0], True, swim(necks, tails, flipper_names, *sw[name]))
    spec["attack"](m, necks)
    spec.get("extra_anims", lambda m: None)(m)
    ko = spec["ko"]
    add_knockout(m, roll=ko["roll"], lift=ko["lift"], shift=ko["shift"], joints=ko["joints"], neck_down=ko["neck_down"])
