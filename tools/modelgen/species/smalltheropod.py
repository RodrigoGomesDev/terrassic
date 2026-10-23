"""
Shared rig for small, feathered theropods (Velociraptor, Compsognathus).

Both are modelled at a larger pixel size and scaled down by the renderer so
they keep enough texture detail (the raptor at 2x, the compy at 3x).
"""
import math
from rig import Model, wave, sinx, track, keys


def build_small(ident, P):
    m = Model(ident, render_scale=P["render_scale"])
    m.palette = dict(P["palette"])
    hy, hz = P["hip"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, hy, hz))
    for b in P["torso"]:
        m.box("body", b[0], b[1], name=b[2] if len(b) > 2 else "torso", tag=b[3] if len(b) > 3 else "skin")

    # neck + head --------------------------------------------------------
    neck = m.chain(["neck1", "neck2"], "body", 0, P["neck_pts"], "-z", P["neck_secs"], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (P.get("head_pitch", 0) - neck["abs"], 0, 0))
    A = (0, ay, az)

    def rel(x0, y0, z0, x1, y1, z1):
        return (x0, A[1] + y0, A[2] + z0), (x1, A[1] + y1, A[2] + z1)

    H = P["head"]
    cw, ch, cl = H["cranium"]          # width, height, length
    sw, sh, sl = H["snout"]
    m.box("skull", *rel(-cw / 2, -1, -cl + 1, cw / 2, ch - 1, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *rel(-sw / 2, H.get("snout_y", 0), -cl + 1 - sl, sw / 2, H.get("snout_y", 0) + sh, -cl + 1),
          name="snout", paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}})
    jw, jh, jl = H["jaw"]
    m.bone("jaw", "skull", (0, ay - 1, az - 1))
    m.box("jaw", *rel(-jw / 2, -1 - jh, -jl - 1, jw / 2, -1, -1), name="jaw",
          paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}})
    if H.get("crest"):
        cx0, cy0, cz0, cx1, cy1, cz1 = H["crest"]
        m.box("skull", *rel(cx0, cy0, cz0, cx1, cy1, cz1), name="crest", tag="feather")
    er = H.get("eye_r", 1.0)
    ey, ez = A[1] + H["eye"][0], A[2] + H["eye"][1]
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (cw / 2, ey, ez), "r": er, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-cw / 2, ey, ez), "r": er, "side": -1},
    ]
    if P.get("mask"):
        m.decals.append({"kind": "band_y", "bones": ["skull"], "pos": (0, ey + 0.0, 0), "r": 0.6, "mul": 0.55,
                         "zmin": A[2] - cl - sl + 2, "zmax": A[2] + 1})

    # arms ---------------------------------------------------------------
    ax = P["arm_x"]
    def arm(side, sx):
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", ax * sx, P["arm_pts"], "-y", P["arm_secs"],
                     tag="limb", overlap=(1.0, 0.5))
        ey_, ez_ = ch["end"]
        x = ax * sx
        m.box(f"forearm_{side}", (x - 0.5, ey_ - 1.5, ez_ - 1.5), (x + 0.5, ey_ + 0.5, ez_ - 0.5), tag="claw", name="claw",
              paint={"axis": "-y"})
        if P.get("wing"):
            wl, wh = P["wing"]
            # feather vane hanging behind the forearm (points back along +z in the unposed arm)
            top = ch["segments"][1]["unposed"][0]
            m.box(f"forearm_{side}", (x - 0.5 * sx - 0.5, ey_ - 1, ez_), (x - 0.5 * sx + 0.5, ey_ - 1 + wh, ez_ + wl),
                  tag="feather", name="wing")
    m.sym(arm)

    # legs ---------------------------------------------------------------
    lx = P["leg_x"]
    def leg(side, sx):
        x = lx * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, P["leg_pts"], "-y",
                     P["leg_secs"], overlap=(1.0, 0.8))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        tl, tw = P["toes"]
        m.box(f"toes_{side}", (x - tw / 2, by - 1, bz - tl), (x + tw / 2, by, bz + 1), tag="limb", name="toes")
        m.box(f"toes_{side}", (x - tw / 2, by - 1, bz - tl - 1), (x + tw / 2, by, bz - tl), tag="claw", name="claws")
        if P.get("sickle"):
            ix = x - sx * (tw / 2)  # inner edge
            m.box(f"toes_{side}", (min(ix, ix + sx), by, bz - 2), (max(ix, ix + sx), by + 2, bz - 1), tag="claw",
                  name="sickle", rot=(-25, 0, 0), origin=(ix, by, bz - 1), paint={"axis": "+y"})
    m.sym(leg)

    # tail ---------------------------------------------------------------
    names = [f"tail{i+1}" for i in range(len(P["tail_secs"]))]
    tail = m.chain(names, "body", 0, P["tail_pts"], "+z", P["tail_secs"], overlap=(1.0, 1.0))
    if P.get("tail_fan"):
        for k, (seg, wid) in enumerate(P["tail_fan"]):
            s = tail["segments"][seg]
            y0, z0 = s["unposed"]
            L = int(round(s["len"]))
            m.box(names[seg], (-wid / 2, y0 - 0.5, z0), (wid / 2, y0 + 0.5, z0 + L + 1), tag="feather", name="fan")

    m.pattern = P.get("pattern")
    animations(m, P)
    return m


def animations(m, P):
    sp = P.get("anim_speed", 1.0)

    def legs(length, A_th, A_sh, A_ft, n=8):
        t = {}
        for side, ph in (("l", 0.0), ("r", 0.5)):
            t[f"thigh_{side}"] = track(rot=wave(n, lambda p, ph=ph: (A_th * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
            t[f"shin_{side}"] = track(rot=wave(n, lambda p, ph=ph: (-A_sh * max(0.0, math.cos(2 * math.pi * (p + ph))) + 3, 0, 0), length))
            t[f"foot_{side}"] = track(rot=wave(n, lambda p, ph=ph: (A_ft * max(0.0, math.cos(2 * math.pi * (p + ph))) - 4 * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
            t[f"toes_{side}"] = track(rot=wave(n, lambda p, ph=ph: (10 * max(0.0, math.sin(2 * math.pi * (p + ph + 0.25))), 0, 0), length))
        return t

    ntail = len(P["tail_secs"])
    Li = 3.0
    idle = {
        "body": track(rot=wave(8, sinx(1.0), Li), pos=wave(8, lambda p: (0, 0.25 * math.sin(2 * math.pi * p), 0), Li)),
        "neck1": track(rot=wave(8, lambda p: (3 * math.sin(2 * math.pi * (p + 0.1)), 4 * math.sin(2 * math.pi * p * 2) * 0.5, 0), Li)),
        "neck2": track(rot=wave(8, lambda p: (-2 * math.sin(2 * math.pi * (p + 0.25)), 0, 0), Li)),
        "skull": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * (p + 0.3)), 0, 3 * math.sin(2 * math.pi * p)), Li)),
        "arm_l": track(rot=wave(4, sinx(4, 0.2), Li)),
        "arm_r": track(rot=wave(4, sinx(4, 0.45), Li)),
    }
    for i in range(ntail):
        a = 3 + 1.5 * i
        idle[f"tail{i+1}"] = track(rot=wave(8, lambda p, a=a, i=i: (1.0 * math.sin(2 * math.pi * (p + 0.1 * i)), a * math.sin(2 * math.pi * (p - 0.1 * i)), 0), Li))
    m.anim("idle", Li, True, idle)

    for name, Lc, A in (("walk", 0.9 / sp, (26, 30, 20)), ("run", 0.5 / sp, (40, 46, 30))):
        t = legs(Lc, *A)
        run = name == "run"
        t["body"] = track(rot=wave(8, lambda p, run=run: (-5 if run else 0, 2.5 * math.sin(2 * math.pi * p), 2 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, run=run: (0, (0.9 if run else 0.5) * math.cos(4 * math.pi * p) - (0.6 if run else 0.2), 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, run=run: ((-6 if run else 0) - 3 * math.cos(4 * math.pi * p), 0, 0), Lc))
        t["skull"] = track(rot=wave(8, lambda p, run=run: ((5 if run else 0) + 2.5 * math.cos(4 * math.pi * p), 0, 0), Lc))
        t["arm_l"] = track(rot=wave(4, lambda p: (-8 + 5 * math.sin(2 * math.pi * (p + 0.5)), 0, 0), Lc))
        t["arm_r"] = track(rot=wave(4, lambda p: (-8 + 5 * math.sin(2 * math.pi * p), 0, 0), Lc))
        for i in range(ntail):
            a = (3 if run else 4) + i
            t[f"tail{i+1}"] = track(rot=wave(8, lambda p, a=a, i=i, run=run: ((3 if run else 0) + 1.2 * math.cos(4 * math.pi * p), -a * math.sin(2 * math.pi * (p - 0.1 * (i + 1))), 0), Lc))
        m.anim(name, Lc, True, t)

    La = 0.6
    m.anim("attack", La, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.15, 14, 0, 0), (0.3, -18, 0, 0), (0.45, -8, 0, 0), (0.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.15, 10, 0, 0), (0.3, -8, 0, 0), (0.6, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.15, -35, 0, 0), (0.28, -40, 0, 0), (0.34, 0, 0, 0), (0.6, 0, 0, 0)])),
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.15, -40, 0, -10), (0.3, 20, 0, 0), (0.6, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.15, -40, 0, 10), (0.3, 20, 0, 0), (0.6, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.15, 4, 0, 0), (0.3, -6, 0, 0), (0.6, 0, 0, 0)])),
    })
