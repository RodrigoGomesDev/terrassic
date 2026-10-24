"""
Land-turtle rig (Basilemys first; the Triassic Proganochelys and the Jurassic land turtles later): a high shell
built by the species hook, a short neck with a beaked head, strong clawed legs from quadruped.py, a short tail
and the quadruped animation set plus "hide" (head and legs pulled in under the shell). Knocked out it lies on its
side with the legs limp.

Spec keys:
  render_scale, palette, sexes, pattern
  body            (y, z) of the body pivot
  shell(m)        hook: carapace, rim, plastron, keel (tags "shell" / "plastron")
  neck            dict(points=[(y, z) ...], sections=[(w, h) ...], tilt=deg)
  head(m, R, ay, az)   hook: skull, beak, jaw and eyes (R shifts a box to the neck's end)
  hind, front     dict(x, pts, secs, pad) for quadruped.hind_leg / front_leg
  tail            dict(points, sections)
  gait            dict(walk=(L, hind, front, bob), run=(L, hind, front, bob))
  sit_drop, sit   drop in px, quad_sit keyword overrides
  hide            dict(neck=deg, skull=deg, back=px, drop=px) for the "hide" action (legs use the sit fold)
  extra_anims     dict(name=(length, loop, tracks)) added on top
  knockout        dict(lift, neck_down)
"""
from rig import Model, track, keys
from quadruped import hind_leg, front_leg, quad_anims, quad_sit


def build_tortoise(ident, S):
    m = Model(ident, render_scale=S.get("render_scale", 1.0))
    m.palette = dict(S["palette"])
    m.sexes = S.get("sexes", {"male": {}, "female": {}})
    by, bz = S["body"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, by, bz))
    S["shell"](m)

    nk = S["neck"]
    names = [f"neck{i + 1}" for i in range(len(nk["points"]) - 1)]
    neck = m.chain(names, "body", 0, nk["points"], "-z", nk["sections"], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", names[-1], (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-nk.get("tilt", 6) - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    S["head"](m, R, ay, az)

    h, f = S["hind"], S["front"]
    m.sym(lambda s, sx: hind_leg(m, s, sx, h["x"], h["pts"], h["secs"], h["pad"]))
    m.sym(lambda s, sx: front_leg(m, s, sx, f["x"], f["pts"], f["secs"], f["pad"]))

    tl = S["tail"]
    tails = [f"tail{i + 1}" for i in range(len(tl["points"]) - 1)]
    m.chain(tails, "body", 0, tl["points"], "+z", tl["sections"], overlap=(1.0, 1.0))
    m.pattern = S.get("pattern")

    g = S.get("gait", {})
    extra = {**bite(), **hide(m, S), **S.get("extra_anims", {})}
    quad_anims(m, len(tails), nneck=len(names), walk=g.get("walk", (2.4, 14, 14, 0.2)), run=g.get("run", (1.4, 20, 20, 0.4)),
               attack=None, sit_drop=S.get("sit_drop", 2), graze_neck=-24, graze_skull=-18,
               sit_kw=S.get("sit"), extra=extra, knockout=S.get("knockout", {"lift": 0.3, "neck_down": -16}))
    return m


def bite():
    """The beak snap: the neck shoots out, the jaw opens wide and clamps."""
    return {"attack": (0.7, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.2, 12, 0, 0), (0.38, -16, 0, 0), (0.7, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.2, 8, 0, 0), (0.38, -8, 0, 0), (0.7, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -24, 0, 0), (0.36, -28, 0, 0), (0.42, 0, 0, 0), (0.7, 0, 0, 0)])),
        "body": track(pos=keys([(0, 0, 0, 0), (0.2, 0, 0, 1), (0.38, 0, 0, -2), (0.7, 0, 0, 0)])),
    })}


def hide(m, S):
    """Drops onto the plastron with the legs folded in under the rim (the sit fold, a little deeper) and pulls the
    head back and down against the shell; holds, then comes out again. Nanhsiungchelyids could not retract the
    head fully, so it stays out."""
    H = S.get("hide", {})
    n, sk, back = H.get("neck", -22), H.get("skull", 14), H.get("back", 6)
    L = 4.0
    t = quad_sit(m, S.get("sit_drop", 2) + H.get("drop", 1), length=L, **(S.get("sit") or {}))
    t["neck1"] = track(rot=keys([(0, 0, 0, 0), (0.5, n, 0, 0), (3.4, n, 0, 0), (L, 0, 0, 0)]),
                       pos=keys([(0, 0, 0, 0), (0.5, 0, 0, back), (3.4, 0, 0, back), (L, 0, 0, 0)]))
    t["skull"] = track(rot=keys([(0, 0, 0, 0), (0.5, sk, 0, 0), (3.4, sk, 0, 0), (L, 0, 0, 0)]))
    t["jaw"] = track(rot=keys([(0, 0, 0, 0), (L, 0, 0, 0)]))
    return {"hide": (L, False, t)}
