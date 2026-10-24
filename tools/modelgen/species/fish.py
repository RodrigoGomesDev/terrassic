"""
Fish rig (Enchodus and Lepisosteus first; the Triassic and Jurassic fish later): a layered body on "body", a
shoulder segment on "neck", the head on "head"/"skull" with a hinged lower jaw ("jaw") and two gill covers that
open ("operculum_l"/"operculum_r"), a tail chain ending in the caudal fin ("caudal"), and any number of fins on
their own bones (paired pectorals and pelvics, single dorsal, anal, adipose...). The species module builds every
cube; the rig gives the bones, the swimming wave with fin sculling, gill breathing, knockout and the taming actions.

Spec keys:
  render_scale, palette, sexes, pattern
  body_pivot      (y, z) of the body bone
  body(m)         hook: the layered torso on "body"
  neck_pivot      (y, z) of the shoulder bone "neck"; neck(m) hook builds its cubes
  head_pivot      (y, z) of "head"/"skull"; jaw_pivot (y, z) of "jaw"
  head(m)         hook: cranium, snout, jaw, fangs, decals (skull and jaw bones already exist)
  operculum       dict(pivot=(x, y, z), boxes=[(frm, to), ...]) left side; mirrored to the right
  tail            dict(points=[(y, z) ...], sections=[(w, h) ...], layers=fn(m, segments) optional)
  caudal(m, y, z) hook: caudal fin cubes on "caudal" (pivot at the tail end)
  fins            [dict(name, parent, pivot, rot, boxes=[(frm, to, name)], sym, flap=(axis, amp, phase))]
                  left-side values for sym fins (x mirrored, y/z rotations flip sign)
  swim            dict(idle=(L, amp, head, fin), walk=..., run=..., sit=...)  fin = scale of the fin flaps
  breathe         (gill flare deg, jaw deg)
  attack(m)       hook adding the attack animation; extra_anims(m) optional
  ko              dict(roll, lift, shift, joints, neck_down)
"""
import math
from rig import Model, track, wave, add_knockout


def mirror_box(frm, to):
    return (-to[0], frm[1], frm[2]), (-frm[0], to[1], to[2])


def build_fish(ident, S):
    m = Model(ident, render_scale=S.get("render_scale", 1.0))
    m.palette = dict(S["palette"])
    m.sexes = S.get("sexes", {"male": {}, "female": {}})
    m.fins = []
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *S["body_pivot"]))
    S["body"](m)
    m.bone("neck", "body", (0, *S["neck_pivot"]))
    S["neck"](m)
    m.bone("head", "neck", (0, *S["head_pivot"]))
    m.bone("skull", "head", (0, *S["head_pivot"]))
    m.bone("jaw", "skull", (0, *S["jaw_pivot"]))
    S["head"](m)

    op = S["operculum"]
    for side, s in (("l", 1), ("r", -1)):
        px, py, pz = op["pivot"]
        m.bone(f"operculum_{side}", "skull", (px * s, py, pz))
        for frm, to, *rest in op["boxes"]:
            f, t = (frm, to) if s > 0 else mirror_box(frm, to)
            m.box(f"operculum_{side}", f, t, tag="gill_cover", name=rest[0] if rest else "operculum")

    tl = S["tail"]
    names = [f"tail{i + 1}" for i in range(len(tl["points"]) - 1)]
    tail = m.chain(names, "body", 0, tl["points"], "+z", tl["sections"], overlap=(1.0, 1.0))
    if tl.get("layers"):
        tl["layers"](m, tail["segments"])
    ey, ez = tail["end"]
    m.bone("caudal", names[-1], (0, ey, ez))
    S["caudal"](m, ey, ez)

    for f in S.get("fins", []):
        sides = (("l", 1), ("r", -1)) if f.get("sym") else (("", 1),)
        for side, s in sides:
            bname = f"{f['name']}_{side}" if side else f["name"]
            px, py, pz = f["pivot"]
            rx, ry, rz = f.get("rot", (0, 0, 0))
            m.bone(bname, f["parent"], (px * s, py, pz), (rx, ry * s, rz * s))
            for frm, to, cname in f["boxes"]:
                a, b = (frm, to) if s > 0 else mirror_box(frm, to)
                m.box(bname, a, b, tag="fin", name=cname)
            m.fins.append((bname, s, f.get("flap", ("z", 0, 0.0))))

    m.pattern = S.get("pattern")
    animations(m, S, names + ["caudal"])
    return m


def swim(m, S, tail_bones, L, amp, head, fin):
    """Side to side wave down the tail (yaw), the body following a little, fins sculling, gills breathing once a cycle."""
    t = {}
    for i, b in enumerate(tail_bones):
        a = amp * (0.3 + 0.22 * i)
        t[b] = track(rot=wave(8, lambda p, i=i, a=a: (0, a * math.sin(2 * math.pi * (p - 0.12 * i)), 0), L))
    t["body"] = track(rot=wave(8, lambda p: (0, -amp * 0.22 * math.sin(2 * math.pi * (p + 0.1)), 0), L),
                      pos=wave(8, lambda p: (0, 0.3 * math.sin(4 * math.pi * p), 0), L))
    t["neck"] = track(rot=wave(8, lambda p: (0, head * math.sin(2 * math.pi * (p + 0.25)), 0), L))
    for bname, s, (axis, a0, ph) in m.fins:
        a = a0 * fin
        if axis == "z":
            fn = lambda p, s=s, a=a, ph=ph: (0, 0, s * a * math.sin(2 * math.pi * (p + ph)))
        elif axis == "y":
            fn = lambda p, s=s, a=a, ph=ph: (0, s * a * math.sin(2 * math.pi * (p + ph)), 0)
        else:
            fn = lambda p, a=a, ph=ph: (a * math.sin(2 * math.pi * (p + ph)), 0, 0)
        t[bname] = track(rot=wave(8, fn, L))
    g, j = S.get("breathe", (10, 4))
    t["operculum_l"] = track(rot=wave(8, lambda p: (0, g * (0.5 - 0.5 * math.cos(2 * math.pi * (p - 0.15))), 0), L))
    t["operculum_r"] = track(rot=wave(8, lambda p: (0, -g * (0.5 - 0.5 * math.cos(2 * math.pi * (p - 0.15))), 0), L))
    t["jaw"] = track(rot=wave(8, lambda p: (-j * (0.5 - 0.5 * math.cos(2 * math.pi * p)), 0, 0), L))
    return t


def animations(m, S, tail_bones):
    sw = S["swim"]
    for name in ("idle", "walk", "run", "sit"):
        m.anim(name, sw[name][0], True, swim(m, S, tail_bones, *sw[name]))
    S["attack"](m)
    S.get("extra_anims", lambda m: None)(m)
    ko = S["ko"]
    add_knockout(m, roll=ko["roll"], lift=ko["lift"], shift=ko["shift"], joints=ko["joints"], neck_down=ko["neck_down"])


def paint_eye(tx, rgb, centre, r_eye, r_pupil, face_x):
    """A round fish eye painted on the side of the skull: a dark rim, the iris, a round pupil and a highlight.
    Returns the colour, or None when the pixel is outside the eye."""
    if tx.cube.bone != "skull" or tx.face not in ("east", "west") or abs(abs(tx.P[0]) - face_x) > 0.6:
        return None
    cy, cz = centre
    dy, dz = tx.P[1] - cy, tx.P[2] - cz
    d = math.hypot(dy, dz)
    if d > r_eye + 0.75:
        return None
    if d > r_eye:
        return rgb * 0.55                                           # the orbit rim
    if d <= r_pupil:
        if dy > r_pupil * 0.2 and dz < -r_pupil * 0.2:
            return tx.pal["eye_shine"].copy()                       # the highlight
        return tx.pal["pupil"].copy()
    return tx.pal["eye"] * (0.85 + 0.25 * (dy / max(r_eye, 1e-6) + 1) / 2)
