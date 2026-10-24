"""
Archetype: foot-propelled diving birds (Hesperornis now; Baptornis and the other hesperornithines later). A loon-
like body lying flat on the water, a long neck in two segments, a toothed beak, vestigial wings, and legs set far
back that kick alternately like a grebe's (thigh / shin / lobed foot). Animation set: idle (floating, slow paddling),
walk (steady kicks), run (fast kicks, neck stretched, wings out), sit (resting afloat, head tucked back), attack
(neck strike, jaw snap), knocked_out / wake / eat / beg / tame.

Spec keys:
  render_scale, palette, sexes, pattern   as in the other archetypes
  body                    (y, z) of the body pivot
  body_parts(m)           hook: torso boxes, tail, anything on the body
  neck                    dict(points=[(y, z) ...3 points], sections=[(w, h), (w, h)])
  head(m, ay, az, abs)    hook: skull / beak / jaw at the neck's end
  wings                   dict(pivot=(x, y, z), box=(x0, x1, y0, y1, z0, z1))     left side, mirrored
  legs                    dict(pivot=(x, y, z), thigh=(x0, x1, y0, y1, z0, z1), shin_pivot=(x, y, z),
                               shin=(...), foot_pivot=(x, y, z), foot=(...), toes=(...))   left side, mirrored
  swim                    dict(idle=(L, kick, bob), walk=(L, kick, bob), run=(L, kick, bob), sit=(L, kick, bob))
  sit_pose                dict(neck1, neck2, skull) rotations (x) added while resting
  attack(m)               hook that adds the attack animation
  ko                      dict(roll, lift, shift, joints, neck_down) for rig.add_knockout
"""
import math
from rig import Model, track, wave, keys, add_knockout


def build(species_id, spec):
    m = Model(species_id, render_scale=spec.get("render_scale", 1.0))
    m.palette = dict(spec["palette"])
    m.sexes = spec["sexes"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *spec["body"]))
    spec["body_parts"](m)

    nk = spec["neck"]
    neck = m.chain(["neck1", "neck2"], "body", 0, nk["points"], "-z", nk["sections"], overlap=(1.0, 0.5))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    spec["head"](m, ay, az, neck["abs"])

    w = spec["wings"]
    lg = spec["legs"]

    def sides(side, s):
        def B(b):
            x0, x1, y0, y1, z0, z1 = b
            return (min(x0 * s, x1 * s), y0, z0), (max(x0 * s, x1 * s), y1, z1)
        px, py, pz = w["pivot"]
        m.bone(f"wing_{side}", "body", (px * s, py, pz))
        m.box(f"wing_{side}", *B(w["box"]), name="wing", tag="limb")
        px, py, pz = lg["pivot"]
        m.bone(f"thigh_{side}", "body", (px * s, py, pz))
        m.box(f"thigh_{side}", *B(lg["thigh"]), name="thigh", tag="limb")
        px, py, pz = lg["shin_pivot"]
        m.bone(f"shin_{side}", f"thigh_{side}", (px * s, py, pz))
        m.box(f"shin_{side}", *B(lg["shin"]), name="shin", tag="limb")
        px, py, pz = lg["foot_pivot"]
        m.bone(f"foot_{side}", f"shin_{side}", (px * s, py, pz))
        m.box(f"foot_{side}", *B(lg["foot"]), name="foot", tag="limb")
        m.box(f"foot_{side}", *B(lg["toes"]), name="toes", tag="fin")
    m.sym(sides)

    m.pattern = spec["pattern"]
    animations(m, spec)
    return m


def swim(L, kick, bob, stretch=0.0, wings=0.0, rest=None):
    """Alternate foot strokes: the shin swings back (power) and forward (recovery, foot folded), the lobed foot
    opens on the power stroke; the body bobs and yaws a little with each kick; the neck sways."""
    t = {}
    rest = rest or {}
    for side, s, ph in (("l", 1, 0.0), ("r", -1, 0.5)):
        t[f"thigh_{side}"] = track(rot=wave(8, lambda p, ph=ph: (kick * 0.3 * math.sin(2 * math.pi * (p + ph)), 0, 0), L))
        t[f"shin_{side}"] = track(rot=wave(8, lambda p, ph=ph: (kick * math.sin(2 * math.pi * (p + ph)), 0, 0), L))
        # the foot spreads flat on the power stroke and folds on the way forward
        t[f"foot_{side}"] = track(rot=wave(8, lambda p, ph=ph: (
            -kick * 0.6 * math.sin(2 * math.pi * (p + ph)) - kick * 0.25, 0, 0), L))
        t[f"wing_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * (wings + 3 * math.sin(4 * math.pi * p))), L))
    t["body"] = track(rot=wave(8, lambda p: (bob * 0.6 * math.sin(4 * math.pi * p), bob * 1.5 * math.sin(2 * math.pi * p), 0), L),
                      pos=wave(8, lambda p: (0, bob * 0.3 * math.sin(4 * math.pi * p), 0), L))
    t["neck1"] = track(rot=wave(8, lambda p: (rest.get("neck1", 0) - stretch + 2 * math.sin(4 * math.pi * p), 3 * math.sin(2 * math.pi * p), 0), L))
    t["neck2"] = track(rot=wave(8, lambda p: (rest.get("neck2", 0) + stretch * 0.6 + 1.5 * math.sin(4 * math.pi * (p + 0.1)), 0, 0), L))
    t["skull"] = track(rot=wave(8, lambda p: (rest.get("skull", 0) + stretch * 0.4, 4 * math.sin(2 * math.pi * (p + 0.2)), 0), L))
    t["tail1"] = track(rot=wave(8, lambda p: (3 * math.sin(4 * math.pi * p), 6 * math.sin(2 * math.pi * p), 0), L))
    return t


def animations(m, spec):
    sw = spec["swim"]
    m.anim("idle", sw["idle"][0], True, swim(*sw["idle"]))
    m.anim("walk", sw["walk"][0], True, swim(*sw["walk"]))
    m.anim("run", sw["run"][0], True, swim(*sw["run"], stretch=8, wings=25))
    m.anim("sit", sw["sit"][0], True, swim(*sw["sit"], rest=spec.get("sit_pose")))
    spec["attack"](m)
    spec.get("extra_anims", lambda m: None)(m)
    ko = spec["ko"]
    add_knockout(m, roll=ko["roll"], lift=ko["lift"], shift=ko["shift"], joints=ko["joints"], neck_down=ko["neck_down"])
