"""
Small mammal rig (Didelphodon first; the Ice Age epilogue and the Mesozoic mammals later): a low, long-bodied
quadruped on short legs with five-toed paws, a broad head with a strong jaw, round ears, a long tail. Modelled
large and rendered small (render_scale) like the Compsognathus so the fur keeps its texture detail.

Spec keys:
  render_scale, palette, sexes, pattern
  body            (y, z) of the body pivot (hip height, hip z)
  torso           [((x0,y0,z0),(x1,y1,z1), name[, tag]), ...]
  neck            dict(points=[(y,z),(y,z)], sections=[(w,h)], tilt=deg)
  head            dict(cranium=(w,h,l), snout=(w,h,l), snout_y=, jaw=(w,h,l), eye=(y,z), eye_r=, ears=(w,h,l, x, y, z))
  hind, front     dict(x, pts, secs, pad) for quadruped.hind_leg / front_leg (pad = (w, l0, l1))
  tail            dict(points, sections, fur=True for a bushy tag "fur" sleeve on the first segments)
  gait            dict(walk=(L, hind, front, bob), run=(L, hind, front, bob))
  sit_drop, sit   drop in px, quad_sit keyword overrides
  extra(m)        hook for species-only geometry
  extra_anims     dict(name=(length, loop, tracks)) added on top (e.g. "dig", "sniff")
"""
from rig import Model, track, keys
from quadruped import hind_leg, front_leg, quad_anims


def build_mammal(ident, S):
    m = Model(ident, render_scale=S.get("render_scale", 1.0))
    m.palette = dict(S["palette"])
    m.sexes = S.get("sexes", {"male": {}, "female": {}})
    by, bz = S["body"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, by, bz))
    for b in S["torso"]:
        m.box("body", b[0], b[1], name=b[2], tag=b[3] if len(b) > 3 else "skin")

    nk = S["neck"]
    names = [f"neck{i + 1}" for i in range(len(nk["points"]) - 1)]
    neck = m.chain(names, "body", 0, nk["points"], "-z", nk["sections"], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", names[-1], (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-nk.get("tilt", 10) - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    H = S["head"]
    cw, ch, cl = H["cranium"]
    sw, sh, sl = H["snout"]
    sy = H.get("snout_y", -1)
    m.box("skull", *R(-cw / 2, -ch / 2, -cl + 1, cw / 2, ch / 2, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-sw / 2, sy, -cl + 1 - sl, sw / 2, sy + sh, -cl + 1), name="snout",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}})
    m.box("skull", *R(-1, sy + sh - 1, -cl - sl, 1, sy + sh, -cl + 1 - sl), name="nose", tag="nose")
    jw, jh, jl = H["jaw"]
    m.bone("jaw", "skull", (0, ay + sy, az - cl + 2))
    m.box("jaw", *R(-jw / 2, sy - jh, -cl + 1 - jl, jw / 2, sy, -cl + 2), name="jaw",
          paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}})
    if H.get("ears"):
        ew, eh, el, ex, ey, ez = H["ears"]
        for sx in (1, -1):
            m.box("skull", *R(sx * ex - ew / 2, ey, ez, sx * ex + ew / 2, ey + eh, ez + el), name="ear", tag="ear")
    er = H.get("eye_r", 1.0)
    eyy, eyz = ay + H["eye"][0], az + H["eye"][1]
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (cw / 2, eyy, eyz), "r": er, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-cw / 2, eyy, eyz), "r": er, "side": -1},
    ]
    if S.get("mask"):
        m.decals.append({"kind": "band_y", "bones": ["skull"], "pos": (0, eyy, 0), "r": 0.8, "mul": 0.5,
                         "zmin": az - cl - sl + 1, "zmax": az + 1})

    h, f = S["hind"], S["front"]
    m.sym(lambda s, sx: hind_leg(m, s, sx, h["x"], h["pts"], h["secs"], h["pad"]))
    m.sym(lambda s, sx: front_leg(m, s, sx, f["x"], f["pts"], f["secs"], f["pad"]))

    tl = S["tail"]
    tails = [f"tail{i + 1}" for i in range(len(tl["points"]) - 1)]
    tail = m.chain(tails, "body", 0, tl["points"], "+z", tl["sections"], overlap=(1.0, 1.0))
    if tl.get("fur"):
        for seg, name, (w, hgt) in zip(tail["segments"][:tl["fur"]], tails, tl["sections"]):
            y0, z0 = seg["unposed"]
            L = int(round(seg["len"]))
            m.box(name, (-w / 2 - 1, y0 - hgt / 2 - 1, z0), (w / 2 + 1, y0 + hgt / 2 + 1, z0 + L), tag="fur", name="brush")
    if S.get("extra"):
        S["extra"](m)
    m.pattern = S.get("pattern")

    g = S.get("gait", {})
    quad_anims(m, len(tails), nneck=len(names), walk=g.get("walk", (1.0, 24, 24, 0.5)), run=g.get("run", (0.5, 36, 36, 0.9)),
               attack=None, sit_drop=S.get("sit_drop", by * 0.4), graze_neck=-18, graze_skull=-20,
               sit_kw=S.get("sit"), extra={**bite(), **S.get("extra_anims", {})}, knockout=S.get("knockout", {"lift": 0.5, "neck_down": -20}))
    return m


def bite():
    """A lunge and snap: the head darts forward, jaw wide, then clamps."""
    return {"attack": (0.6, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.15, 10, 0, 0), (0.3, -14, 0, 0), (0.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.15, 8, 0, 0), (0.3, -6, 0, 0), (0.6, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.15, -40, 0, 0), (0.28, -45, 0, 0), (0.34, 0, 0, 0), (0.6, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.15, 3, 0, 0), (0.3, -4, 0, 0), (0.6, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.15, 0, 0, 1), (0.3, 0, 0, -2), (0.6, 0, 0, 0)])),
    })}
