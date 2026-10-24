"""
Archetype: marine reptiles that swim with the tail (mosasaurs; later the same hooks serve big fish). Shared tail
chain with a crescent fluke and a dorsal keel, four paddle flippers, the swimming wave (idle, walk, run, sit),
knocked_out / wake / eat / beg / tame. Body, neck, head, jaw, colours and pattern come from the species module,
so a Tylosaurus with its ramming rostrum shares no geometry with the Mosasaurus beyond the construction rules.

Spec keys:
  render_scale            model pixel scale (in-game size comes from SIZES in tools/javagen/gen_species.py)
  palette, sexes, pattern colours and paint pattern (see paint.py)
  body                    (y, z) of the body pivot
  body_parts(m)           hook: torso, chest, neck (bone "neck"), head ("skull", "jaw"), decals
  tail                    dict(points=[(y, z) ...], sections=[(w, h) ...],
                               fluke=dict(lower=(length, pitch, half_height), upper=(length, pitch, half_height)),
                               keel=[(segment_index, height) ...])   low fin along the top of those tail segments
  flippers                [dict(name, pivot=(x, y, z), rot=(x, y, z), span=(x0, x1), y=(y0, y1), z=(z0, z1)) ...]
                          left-side values; the right side is mirrored (x and the y/z rotations flip sign)
  swim                    dict(idle=(L, amp, flip, head), walk=(L, amp, flip), run=(L, amp, flip, head), sit=(...))
  attack(m)               hook that adds the attack animation
  extra_anims(m)          optional hook for more animations
  ko                      dict(roll, lift, shift, joints, neck_down) for rig.add_knockout; joints are the limp pose
                          (the body rolls ~90 degrees, so a pitch on the tail curves it along the ground)
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

    # tail: long, tapering, ending in a crescent fluke (lower lobe bigger)
    tl = spec["tail"]
    names = [f"tail{i + 1}" for i in range(len(tl["points"]) - 1)]
    tail = m.chain(names, "body", 0, tl["points"], "+z", tl["sections"], overlap=(1.0, 1.0))
    ey, ez = tail["end"]
    m.bone("fluke", names[-1], (0, ey, ez))
    lo_len, lo_rot, lo_h = tl["fluke"]["lower"]
    up_len, up_rot, up_h = tl["fluke"]["upper"]
    m.box("fluke", (-0.5, ey - lo_h, ez - 2), (0.5, ey + lo_h, ez - 2 + lo_len), name="fluke_lower", tag="fin",
          rot=(lo_rot, 0, 0), origin=(0, ey, ez - 2))
    m.box("fluke", (-0.5, ey - up_h, ez - 2), (0.5, ey + up_h, ez - 2 + up_len), name="fluke_upper", tag="fin",
          rot=(up_rot, 0, 0), origin=(0, ey, ez - 2))
    # low keel along the top of the tail
    for k, extra in tl.get("keel", []):
        sg = tail["segments"][k - 1]
        y0, z0 = sg["unposed"]
        L = int(round(sg["len"]))
        h = tl["sections"][k - 1][1] / 2
        m.box(f"tail{k}", (-0.5, y0 + h, z0), (0.5, y0 + h + extra, z0 + L), name="keel", tag="fin")

    # flippers: flat paddles
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
    animations(m, spec, names + ["fluke"], [f["name"] for f in spec["flippers"]])
    return m


def swim(tail_bones, flipper_names, L, amp, flip, head=3.0):
    """Side to side wave running down the tail (yaw), the body following a little, flippers sculling."""
    t = {}
    for i, b in enumerate(tail_bones):
        a = amp * (0.35 + 0.22 * i)
        t[b] = track(rot=wave(8, lambda p, i=i, a=a: (0, a * math.sin(2 * math.pi * (p - 0.12 * i)), 0), L))
    t["body"] = track(rot=wave(8, lambda p: (0, -amp * 0.25 * math.sin(2 * math.pi * (p + 0.1)), 0), L),
                      pos=wave(8, lambda p: (0, 0.3 * math.sin(4 * math.pi * p), 0), L))
    t["neck"] = track(rot=wave(8, lambda p: (0, head * math.sin(2 * math.pi * (p + 0.25)), 0), L))
    for k, name in enumerate(flipper_names):
        f = flip * (1.0 if k == 0 else 0.7)
        ph = 0.0 if k == 0 else -0.3
        for side, s in (("l", 1), ("r", -1)):
            t[f"{name}_{side}"] = track(rot=wave(8, lambda p, s=s, f=f, ph=ph: (0, 0, s * f * math.sin(2 * math.pi * (p + ph))), L))
    return t


def animations(m, spec, tail_bones, flipper_names):
    sw = spec["swim"]
    m.anim("idle", sw["idle"][0], True, swim(tail_bones, flipper_names, *sw["idle"]))
    m.anim("walk", sw["walk"][0], True, swim(tail_bones, flipper_names, *sw["walk"]))
    m.anim("run", sw["run"][0], True, swim(tail_bones, flipper_names, *sw["run"]))
    # resting in the water: a slow idle (the base class expects a sit pose)
    m.anim("sit", sw["sit"][0], True, swim(tail_bones, flipper_names, *sw["sit"]))
    spec["attack"](m)
    spec.get("extra_anims", lambda m: None)(m)
    ko = spec["ko"]
    add_knockout(m, roll=ko["roll"], lift=ko["lift"], shift=ko["shift"], joints=ko["joints"], neck_down=ko["neck_down"])
