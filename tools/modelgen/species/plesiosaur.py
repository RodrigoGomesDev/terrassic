"""
Archetype: plesiosaurs (long-necked elasmosaurs now; the short-necked pliosaurs later with their own body/neck
hooks). Four long paddle flippers that "fly" under water (the tail is just a rudder), a neck chain of many short
segments so it can sway and strike, and the shared animation set: idle, walk, run, sit (resting afloat), attack
(the neck strikes), knocked_out / wake / eat / beg / tame.

Spec keys:
  render_scale            model pixel scale (in-game size comes from SIZES in tools/javagen/gen_species.py)
  palette, sexes, pattern colours and paint pattern (see paint.py)
  body                    (y, z) of the body pivot
  body_parts(m)           hook: torso boxes (and anything else on the body)
  neck                    dict(points=[(y, z) ...], sections=[(w, h) ...])   from the chest forward ("-z")
  head(m, ay, az, abs)    hook: builds head/skull/jaw at the neck's end (abs = neck's accumulated pitch)
  tail                    dict(points=[(y, z) ...], sections=[(w, h) ...], tip=(w, h, length))   short rudder
  flippers                [dict(name, pivot=(x, y, z), rot=(x, y, z), span=(x0, x1), y=(y0, y1), z=(z0, z1)) ...]
                          left-side values; the right side is mirrored (x and the y/z rotations flip sign)
  swim                    dict(idle=(L, flap, sway), walk=(L, flap, sway), run=(L, flap, sway), sit=(L, flap, sway))
  attack(m, necks)        hook that adds the attack animation (necks = the neck bone names, chest first)
  extra_anims(m)          optional hook for more animations
  ko                      dict(roll, lift, shift, joints, neck_down) for rig.add_knockout
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

    # neck: many short segments
    nk = spec["neck"]
    necks = [f"neck{i + 1}" for i in range(len(nk["points"]) - 1)]
    neck = m.chain(necks, "body", 0, nk["points"], "-z", nk["sections"], overlap=(1.0, 1.0))
    ay, az = neck["end"]
    m.bone("head", necks[-1], (0, ay, az))
    spec["head"](m, ay, az, neck["abs"])

    # tail: a short rudder
    tl = spec["tail"]
    tails = [f"tail{i + 1}" for i in range(len(tl["points"]) - 1)]
    tail = m.chain(tails, "body", 0, tl["points"], "+z", tl["sections"], overlap=(1.0, 1.0))
    ey, ez = tail["end"]
    if tl.get("tip"):
        w, h, L = tl["tip"]
        m.box(tails[-1], (-w / 2, ey - h / 2, ez), (w / 2, ey + h / 2, ez + L), name="tail_tip", tag="fin")

    # flippers: long flat paddles
    def flippers(side, s):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        for f in spec["flippers"]:
            px, py, pz = f["pivot"]
            rx, ry, rz = f["rot"]
            m.bone(f"{f['name']}_{side}", "body", (px * s, py, pz), (rx, ry * s, rz * s))
            a, b = X(*f["span"])
            m.box(f"{f['name']}_{side}", (a, f["y"][0], f["z"][0]), (b, f["y"][1], f["z"][1]), tag="fin", name="paddle")
    m.sym(flippers)

    m.pattern = spec["pattern"]
    animations(m, spec, necks, tails, [f["name"] for f in spec["flippers"]])
    return m


def swim(necks, tails, flipper_names, L, flap, sway):
    """Underwater flight: the front and hind pairs beat half a cycle apart, feathering as they go; the body rocks
    gently and the neck sways in a slow wave."""
    t = {}
    for k, name in enumerate(flipper_names):
        ph = 0.0 if k == 0 else 0.5
        for side, s in (("l", 1), ("r", -1)):
            t[f"{name}_{side}"] = track(rot=wave(8, lambda p, s=s, ph=ph: (
                flap * 0.35 * math.cos(2 * math.pi * (p + ph)), 0, s * flap * math.sin(2 * math.pi * (p + ph))), L))
    t["body"] = track(rot=wave(8, lambda p: (flap * 0.08 * math.sin(2 * math.pi * p), 0, 0), L),
                      pos=wave(8, lambda p: (0, 0.5 * math.sin(2 * math.pi * p), 0), L))
    n = len(necks)
    for i, b in enumerate(necks):
        t[b] = track(rot=wave(8, lambda p, i=i: (0.6 * sway * math.sin(2 * math.pi * (p * 0.5 + 0.08 * i)),
                                                  sway * math.sin(2 * math.pi * (p * 0.5 - 0.1 * i)), 0), L))
    for i, b in enumerate(tails):
        t[b] = track(rot=wave(8, lambda p, i=i: (0, 3.0 * (i + 1) * math.sin(2 * math.pi * (p - 0.15 * i)), 0), L))
    return t


def animations(m, spec, necks, tails, flipper_names):
    sw = spec["swim"]
    for name in ("idle", "walk", "run", "sit"):
        L, flap, sway = sw[name]
        m.anim(name, L, True, swim(necks, tails, flipper_names, L, flap, sway))
    spec["attack"](m, necks)
    spec.get("extra_anims", lambda m: None)(m)
    ko = spec["ko"]
    add_knockout(m, roll=ko["roll"], lift=ko["lift"], shift=ko["shift"], joints=ko["joints"], neck_down=ko["neck_down"])
