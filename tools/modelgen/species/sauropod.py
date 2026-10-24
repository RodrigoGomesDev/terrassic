"""
Archetype: sauropods (the titanosaurs of v0.6 now: Alamosaurus, Saltasaurus, Argentinosaurus, Opisthocoelicaudia,
Dreadnoughtus; the Brachiosaurus keeps its own bespoke file). A huge barrel body on four column legs, a many-segment
neck ("-z") ending in a small head, a long tapering tail ("+z"), a saddle, and the family's animation set through
quadruped.quad_anims: idle, walk, run, attack (a rearing stomp, or a tail whip, or a hook), sit, graze,
knocked_out / wake / eat / beg / tame.

Spec keys:
  render_scale, palette, sexes, pattern   as in the other archetypes (pattern may use tags "scute", "crest")
  body                    (y, z) of the body pivot
  body_parts(m)           hook: chest / belly / hips boxes (and anything else on the body)
  neck                    dict(points=[(y, z) ...], sections=[(w, h) ...], tilt=deg)   skull pitch = -tilt
  head(m, R, ay, az)      hook: skull boxes, jaw bone + boxes, eyes (R(x0,y0,z0,x1,y1,z1) head-relative)
  front, hind             dict(x, pts, secs, pad) for quadruped.front_leg / hind_leg
  tail                    dict(points, sections)
  armor(m, neck, tail)    optional hook: osteoderms on body / neck / tail (chain results passed)
  saddle                  (top_y, z0, z1, width, body_half_width, flap) for rig.add_saddle
  gait                    dict(walk=(L, hind, front, bob), run=(L, hind, front, bob))
  attack                  "stomp" | "tail" | "headbutt", or a hook attack(m, necks, tails)
  sit_drop, sit_kw        px the body drops when resting, quad_sit keyword overrides
  graze                   (neck, skull) pitches while grazing
  ko                      dict(lift[, roll, shift, joints, neck_down]) for rig.add_knockout
  extra_anims(m)          optional hook for more animations
"""
from rig import Model, add_saddle
from quadruped import hind_leg, front_leg, quad_anims


def build(species_id, spec):
    m = Model(species_id, render_scale=spec.get("render_scale", 1.0))
    m.palette = dict(spec["palette"])
    m.sexes = spec["sexes"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *spec["body"]))
    spec["body_parts"](m)

    nk = spec["neck"]
    necks = [f"neck{i + 1}" for i in range(len(nk["points"]) - 1)]
    neck = m.chain(necks, "body", 0, nk["points"], "-z", nk["sections"], overlap=(2.0, 1.0))
    ay, az = neck["end"]
    m.bone("head", necks[-1], (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-nk.get("tilt", 12) - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    spec["head"](m, R, ay, az)

    f, h = spec["front"], spec["hind"]
    m.sym(lambda s, sx: front_leg(m, s, sx, f["x"], f["pts"], f["secs"], f["pad"]))
    m.sym(lambda s, sx: hind_leg(m, s, sx, h["x"], h["pts"], h["secs"], h["pad"]))

    tl = spec["tail"]
    tails = [f"tail{i + 1}" for i in range(len(tl["points"]) - 1)]
    tail = m.chain(tails, "body", 0, tl["points"], "+z", tl["sections"], overlap=(1.0, 1.0))
    if spec.get("armor"):
        spec["armor"](m, neck, tail)
    if spec.get("saddle"):
        add_saddle(m, "body", *spec["saddle"][:5], flap=spec["saddle"][5])

    m.pattern = spec["pattern"]
    g = spec["gait"]
    attack = spec.get("attack", "stomp")
    quad_anims(m, len(tails), nneck=len(necks), walk=g["walk"], run=g["run"],
               attack=attack if isinstance(attack, str) else "none",
               sit_drop=spec.get("sit_drop", 14), graze_neck=spec["graze"][0], graze_skull=spec["graze"][1],
               sit_kw=spec.get("sit_kw"), knockout=spec.get("ko"))
    if callable(attack):
        attack(m, necks, tails)
    spec.get("extra_anims", lambda m: None)(m)
    return m
