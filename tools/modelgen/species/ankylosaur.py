"""
Archetype: ankylosaurs (Euoplocephalus now; Talarurus, Saichania and the rest of the club-tailed family later; the
Ankylosaurus keeps its own bespoke file). A wide low body on short stout legs, a short neck, a skull hook that builds
the beak, horns, eyelids and armour of the species, a body-armour hook (every species arranges its own osteoderms),
a three-segment tail with a club hook at the tip, and the family's animation set: idle, walk, run, attack (the tail
club swings), sit, graze, knocked_out / wake / eat / beg / tame.

Spec keys:
  render_scale, palette, sexes, pattern   as in the other archetypes (pattern may use tags "armor", "scute", "spike",
                                          "horn", "club", "beak")
  body                    (y, z) of the body pivot
  body_parts(m)           hook: trunk boxes
  armor(m, neck, tail)    hook: osteoderms, bands, spikes on body / neck / tail (neck and tail = chain results)
  neck                    dict(points=[(y, z) x3], sections=[(w, h), (w, h)], tilt=deg)   skull pitch = -tilt
  head(m, R, ay, az)      hook: skull boxes, horns, jaw bone + boxes, eyes (R(x0,y0,z0,x1,y1,z1) head-relative)
  hind, front             dict(x, pts, secs, pad) for quadruped.hind_leg / front_leg
  tail                    dict(points, sections)
  club(m, tails, tail)    hook: the club boxes on the last tail bone (tail = chain result)
  gait                    dict(walk=(L, hind, front, bob), run=(L, hind, front, bob))
  attack                  "tail" for the standard sideways swing, or a hook attack(m, tails)
  sit_drop, sit_kw        px the body drops when resting, quad_sit keyword overrides
  graze                   (neck, skull) pitches while grazing
  ko                      dict(lift[, roll, shift, joints, neck_down]) for rig.add_knockout
"""
from rig import Model
from quadruped import hind_leg, front_leg, quad_anims


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
    m.bone("skull", "head", (0, ay, az), (-nk.get("tilt", 6) - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    spec["head"](m, R, ay, az)

    h, f = spec["hind"], spec["front"]
    m.sym(lambda s, sx: front_leg(m, s, sx, f["x"], f["pts"], f["secs"], f["pad"]))
    m.sym(lambda s, sx: hind_leg(m, s, sx, h["x"], h["pts"], h["secs"], h["pad"]))

    tl = spec["tail"]
    tails = [f"tail{i + 1}" for i in range(len(tl["points"]) - 1)]
    tail = m.chain(tails, "body", 0, tl["points"], "+z", tl["sections"], overlap=(1.0, 1.0))
    spec["club"](m, tails, tail)
    spec["armor"](m, neck, tail)

    m.pattern = spec["pattern"]
    g = spec["gait"]
    attack = spec.get("attack", "tail")
    quad_anims(m, len(tails), knockout=spec["ko"], walk=g["walk"], run=g["run"],
               attack=attack if isinstance(attack, str) else "none",
               sit_drop=spec.get("sit_drop", 5), graze_neck=spec["graze"][0], graze_skull=spec["graze"][1],
               sit_kw=spec.get("sit_kw"))
    if callable(attack):
        attack(m, tails)
    return m
