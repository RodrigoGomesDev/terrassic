"""
Archetype: ceratopsians (Styracosaurus now; Pachyrhinosaurus, Protoceratops and the rest of the horned family
later; the Triceratops keeps its own bespoke file). A barrel body on rhino-like legs, a short heavy neck, a skull
hook that builds the beak, horns and frill of the species, a short tail, the saddle, and the family's animation set:
idle, walk, run, attack (lower the head and gore upwards), sit, graze, knocked_out / wake / eat / beg / tame.

Spec keys:
  render_scale, palette, sexes, pattern   as in the other archetypes (pattern may use tags "horn", "frill", "beak")
  body                    (y, z) of the body pivot
  body_parts(m)           hook: hips / belly / chest / back boxes
  neck                    dict(points=[(y, z) x3], sections=[(w, h), (w, h)], tilt=deg)   skull pitch = -tilt
  head(m, R, ay, az)      hook: skull boxes, horns, frill, jaw bone + boxes, eyes (R(x0,y0,z0,x1,y1,z1) head-relative)
  hind, front             dict(x, pts, secs, pad) for quadruped.hind_leg / front_leg
  tail                    dict(points, sections)
  saddle                  (top_y, z0, z1, width, body_half_width, flap) for rig.add_saddle
  gait                    dict(walk=(L, hind, front, bob), run=(L, hind, front, bob))
  sit_drop                px the body drops when resting
  graze                   (neck, skull) pitches while grazing
  ko_lift                 add_knockout lift (fraction of the hip height)
"""
import math
from rig import Model, wave, sinx, track, keys, add_knockout, add_saddle
from quadruped import hind_leg, front_leg, quad_gait, quad_sit


def build(species_id, spec):
    m = Model(species_id, render_scale=spec.get("render_scale", 1.0))
    m.palette = dict(spec["palette"])
    m.sexes = spec["sexes"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *spec["body"]))
    spec["body_parts"](m)

    nk = spec["neck"]
    neck = m.chain(["neck1", "neck2"], "body", 0, nk["points"], "-z", nk["sections"], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-nk.get("tilt", 16) - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    spec["head"](m, R, ay, az)

    h, f = spec["hind"], spec["front"]
    m.sym(lambda s, sx: hind_leg(m, s, sx, h["x"], h["pts"], h["secs"], h["pad"]))
    m.sym(lambda s, sx: front_leg(m, s, sx, f["x"], f["pts"], f["secs"], f["pad"]))
    tl = spec["tail"]
    tails = [f"tail{i + 1}" for i in range(len(tl["points"]) - 1)]
    m.chain(tails, "body", 0, tl["points"], "+z", tl["sections"], overlap=(1.0, 1.0))
    m.pattern = spec["pattern"]
    add_saddle(m, "body", *spec["saddle"][:5], flap=spec["saddle"][5])
    animations(m, spec, tails)
    add_knockout(m, lift=spec.get("ko_lift", 0.4))
    return m


def _siny(a, ph=0.0):
    return lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0)


def animations(m, spec, tails):
    Li = 4.0
    idle = {
        "body": track(rot=wave(8, sinx(0.5), Li), pos=wave(8, lambda p: (0, 0.25 * math.sin(2 * math.pi * p), 0), Li)),
        "neck1": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * p), 2 * math.sin(2 * math.pi * (p + 0.3)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (1.5 * math.sin(2 * math.pi * (p + 0.2)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-4 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
    }
    for i, b in enumerate(tails):
        idle[b] = track(rot=wave(8, _siny(3 + 1.5 * i, -0.1 * i), Li))
    m.anim("idle", Li, True, idle)
    g = spec["gait"]
    for name in ("walk", "run"):
        Lc, Ah, Af, bob = g[name]
        t = quad_gait(Lc, Ah, Af)
        t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 1.5 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, b=bob: (0, b * math.cos(4 * math.pi * p) - b * 0.5, 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, b=bob: (-2 * b * math.cos(4 * math.pi * p), 0, 0), Lc))
        for i, b in enumerate(tails):
            t[b] = track(rot=wave(8, _siny(4 + 1.5 * i, 0.25 - 0.1 * i), Lc))
        m.anim(name, Lc, True, t)
    # attack: lower the head and thrust the horns upward
    m.anim("attack", 0.9, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, -14, 0, 0), (0.5, 12, 0, 0), (0.9, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.3, -12, 0, 0), (0.5, 14, 0, 0), (0.9, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.3, -3, 0, 0), (0.5, 3, 0, 0), (0.9, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.3, 0, -0.6, -1.5), (0.5, 0, 0.2, -3), (0.9, 0, 0, 0)])),
    })
    m.anim("sit", 4.0, True, quad_sit(m, spec.get("sit_drop", 8)))
    gn, gs = spec.get("graze", (-22, -16))
    jk = [(0, 0, 0, 0), (0.6, 0, 0, 0)]
    for k in range(6):
        t0 = 0.75 + k * 0.3
        jk += [(t0, -10, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(2.8, 0, 0, 0)]
    m.anim("graze", 2.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.6, gn, 0, 0), (2.3, gn, 0, 0), (2.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.6, gs, 0, 0), (2.3, gs, 0, 0), (2.8, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
    })
    spec.get("extra_anims", lambda m: None)(m)
