"""
Tyrannosaurus rex  (Late Cretaceous, North America)

Reference (Wikipedia, Sue / FMNH PR 2081 and later estimates):
  length 12.3-12.8 m, hip height 3.7-4.0 m, mass 5.4-8.8 t, skull up to 1.52 m,
  arms ~1 m with two fingers, body held horizontal with the tail as a
  counterweight, skull very wide at the back with a narrow snout (forward
  facing eyes), mostly scaly skin (scale impressions on neck, hip and tail).

In game: scale ~0.55 (1 m = ~8.8 px)  ->  ~6.6 blocks long, hips ~2.3 blocks.
"""
import math
from rig import Model, wave, sinx, siny, sinz, combo, track, keys

ID = "tyrannosaurus"


def build():
    m = Model(ID, render_scale=1.0)
    m.palette = {
        "dorsal": "#4b3f30", "flank": "#6f5b41", "belly": "#cdb994",
        "limb": "#514232", "limb_top": "#6a5640",
        "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a",
        "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#e2a93b", "pupil": "#17110c", "dark": "#2c241b",
    }

    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 31, 6))

    # ---------------------------------------------------------------- torso
    m.box("body", (-6, 23, -1), (6, 36, 13), name="hips")
    m.box("body", (-7, 17, -14), (7, 35, 0), name="belly")
    m.box("body", (-6, 17, -24), (6, 33, -13), name="chest")
    m.box("body", (-5, 27, -28), (5, 35, -22), name="shoulders")
    m.box("body", (-4, 35, -14), (4, 37, 10), name="back_ridge")
    m.box("body", (-5, 15, -19), (5, 17, -5), name="belly_low")

    # ---------------------------------------------------------------- neck & head
    neck = m.chain(["neck1", "neck2"], "body", 0, [(31, -23), (34, -28), (35.5, -32)], "-z",
                   [(9, 10), (8, 9)], overlap=(2.0, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))                       # look bone (GeckoLib turns it)
    m.bone("skull", "head", (0, ay, az), (-3 - neck["abs"], 0, 0))  # level, snout slightly down
    A = (0, ay, az)

    def rel(x0, y0, z0, x1, y1, z1):
        return (A[0] + x0, A[1] + y0, A[2] + z0), (A[0] + x1, A[1] + y1, A[2] + z1)

    m.box("skull", *rel(-4.5, -1, -8, 4.5, 6, 1), name="cranium",
          paint={"faces": {"down": "mouth"}})
    m.box("skull", *rel(-3, 0, -16, 3, 5, -8), name="snout",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}})
    m.box("skull", *rel(-2, 5, -14, 2, 6, -7), name="nasal_ridge")
    m.box("skull", *rel(2.5, 6, -8, 4.5, 7, -5), name="brow_l", tag="dorsal_dark")
    m.box("skull", *rel(-4.5, 6, -8, -2.5, 7, -5), name="brow_r", tag="dorsal_dark")
    m.bone("jaw", "skull", (0, ay + 0, az - 2))
    m.box("jaw", *rel(-4, -4, -9, 4, 0, -1), name="jaw_back", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *rel(-2.5, -3, -15, 2.5, 0, -9), name="jaw_front",
          paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}, inflate=0.0)

    eye_y, eye_z = ay + 3.5, az - 5.5
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4.5, eye_y, eye_z), "r": 1.5, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4.5, eye_y, eye_z), "r": 1.5, "side": -1},
        {"kind": "spot", "bones": ["skull"], "pos": (1.5, ay + 3.5, az - 16), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35},
        {"kind": "spot", "bones": ["skull"], "pos": (-1.5, ay + 3.5, az - 16), "r": 0.5, "rx": 0.5, "face": "north", "mul": 0.35},
    ]

    # ---------------------------------------------------------------- tiny arms
    def arm(side, sx):
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", 5.5 * sx, [(23, -20), (19.5, -21.5), (17.5, -24)], "-y",
                     [(2, 3), (2, 2)], tag="limb", overlap=(1.0, 0.5))
        ey, ez = ch["end"]
        m.box(f"forearm_{side}", (5.5 * sx - 1, ey - 2, ez - 1), (5.5 * sx, ey, ez), tag="claw", name="claw", paint={"axis": "-y"})
        m.box(f"forearm_{side}", (5.5 * sx, ey - 2, ez - 1), (5.5 * sx + 1, ey, ez), tag="claw", name="claw", paint={"axis": "-y"})
    m.sym(arm)

    # ---------------------------------------------------------------- legs
    def leg(side, sx):
        x = 6.5 * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x,
                     [(31, 6), (19, -1), (7, 8), (2, 4)], "-y",
                     [(6, 10, -0.5), (4, 6, 1.0, "limb"), (3, 4, 0.0, "limb")], overlap=(1.5, 1.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = lambda x0, y0, z0, x1, y1, z1: ((x + x0, by + y0, bz + z0), (x + x1, by + y1, bz + z1))
        m.box(f"toes_{side}", *T(-1, -2, -7, 1, 0, 1), tag="limb", name="toe_mid")
        m.box(f"toes_{side}", *T(1, -2, -5, 2, 0, 1), tag="limb", name="toe_out")
        m.box(f"toes_{side}", *T(-2, -2, -5, -1, 0, 1), tag="limb", name="toe_in")
        m.box(f"toes_{side}", *T(-1, -2, -8, 1, -1, -7), tag="claw", name="claw_mid")
        m.box(f"toes_{side}", *T(1, -2, -6, 2, -1, -5), tag="claw", name="claw_out")
        m.box(f"toes_{side}", *T(-2, -2, -6, -1, -1, -5), tag="claw", name="claw_in")
    m.sym(leg)

    # ---------------------------------------------------------------- tail
    m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0,
            [(31, 11), (30.5, 23), (30.5, 35), (31, 46), (31.5, 57)], "+z",
            [(10, 10), (8, 8), (6, 6), (4, 4)], overlap=(1.0, 1.0))

    # ---------------------------------------------------------------- pattern
    def pattern(model, tx, rgb, region):
        P = tx.P
        if tx.cube.tag == "dorsal_dark":
            return rgb
        if region in ("dorsal", "flank") and tx.cube.tag == "skin":
            band = math.sin(P[2] * 2 * math.pi / 8.5 + 0.6 * math.sin(P[0] * 0.5))
            k = 0.0
            if region == "dorsal":
                k = 0.22 if band > 0.35 else 0.0
            elif tx.cy > 0.5:
                k = 0.14 if band > 0.55 else 0.0
            rgb = rgb * (1 - k)
        return rgb
    m.pattern = pattern
    m.palette["dorsal_dark"] = "#3d3227"

    animations(m)
    return m


def animations(m):
    L = ["thigh", "shin", "foot", "toes"]

    def leg_cycle(length, A_th, A_sh, A_ft, n=8):
        tracks = {}
        for side, ph in (("l", 0.0), ("r", 0.5)):
            tracks[f"thigh_{side}"] = track(rot=wave(n, lambda p, ph=ph: (A_th * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
            tracks[f"shin_{side}"] = track(rot=wave(n, lambda p, ph=ph: (-A_sh * max(0.0, math.cos(2 * math.pi * (p + ph))) + 4, 0, 0), length))
            tracks[f"foot_{side}"] = track(rot=wave(n, lambda p, ph=ph: (A_ft * max(0.0, math.cos(2 * math.pi * (p + ph))) - 3 * math.sin(2 * math.pi * (p + ph)), 0, 0), length))
            tracks[f"toes_{side}"] = track(rot=wave(n, lambda p, ph=ph: (12 * max(0.0, math.sin(2 * math.pi * (p + ph + 0.25))) * 0.6, 0, 0), length))
        return tracks

    # idle -------------------------------------------------------------
    Li = 4.0
    idle = {
        "body": track(rot=wave(8, sinx(0.7), Li), pos=wave(8, lambda p: (0, 0.3 * math.sin(2 * math.pi * p), 0), Li)),
        "neck1": track(rot=wave(8, sinx(1.6, 0.15), Li)),
        "skull": track(rot=wave(8, sinx(1.2, 0.3), Li)),
        "jaw": track(rot=wave(8, lambda p: (-3 * max(0.0, math.sin(2 * math.pi * p)), 0, 0), Li)),
        "arm_l": track(rot=wave(4, sinx(4, 0.1), Li)),
        "arm_r": track(rot=wave(4, sinx(4, 0.35), Li)),
    }
    for i, a in enumerate((2.5, 3.5, 4.5, 5.5)):
        idle[f"tail{i+1}"] = track(rot=wave(8, lambda p, a=a, i=i: (0.8 * math.sin(2 * math.pi * (p + 0.1 * i)), a * math.sin(2 * math.pi * (p - 0.08 * i)), 0), Li))
    m.anim("idle", Li, True, idle)

    # walk -------------------------------------------------------------
    Lw = 1.6
    walk = leg_cycle(Lw, 24, 26, 18)
    walk["body"] = track(rot=wave(8, lambda p: (0, 2.2 * math.sin(2 * math.pi * p), 1.6 * math.sin(2 * math.pi * p)), Lw),
                         pos=wave(8, lambda p: (0, 0.7 * math.cos(4 * math.pi * p) - 0.3, 0), Lw))
    walk["neck1"] = track(rot=wave(8, lambda p: (-2.0 * math.cos(4 * math.pi * p), -1.5 * math.sin(2 * math.pi * p), 0), Lw))
    walk["skull"] = track(rot=wave(8, lambda p: (1.5 * math.cos(4 * math.pi * p), 0, 0), Lw))
    for i, a in enumerate((3, 4, 5, 6)):
        walk[f"tail{i+1}"] = track(rot=wave(8, lambda p, a=a, i=i: (0.8 * math.cos(4 * math.pi * p), -a * math.sin(2 * math.pi * (p - 0.1 * (i + 1))), 0), Lw))
    walk["arm_l"] = track(rot=wave(4, sinx(6, 0.5), Lw))
    walk["arm_r"] = track(rot=wave(4, sinx(6, 0.0), Lw))
    m.anim("walk", Lw, True, walk)

    # run --------------------------------------------------------------
    Lr = 0.8
    run = leg_cycle(Lr, 36, 40, 26)
    run["body"] = track(rot=wave(8, lambda p: (-4, 2.5 * math.sin(2 * math.pi * p), 2.0 * math.sin(2 * math.pi * p)), Lr),
                        pos=wave(8, lambda p: (0, 1.3 * math.cos(4 * math.pi * p) - 0.8, 0), Lr))
    run["neck1"] = track(rot=wave(8, lambda p: (2 - 3 * math.cos(4 * math.pi * p), 0, 0), Lr))
    run["skull"] = track(rot=wave(8, lambda p: (2 + 2 * math.cos(4 * math.pi * p), 0, 0), Lr))
    run["jaw"] = track(rot=wave(8, lambda p: (-6 - 4 * math.cos(4 * math.pi * p), 0, 0), Lr))
    for i, a in enumerate((3, 4, 5, 6)):
        run[f"tail{i+1}"] = track(rot=wave(8, lambda p, a=a, i=i: (2 + 1.5 * math.cos(4 * math.pi * p), -a * math.sin(2 * math.pi * (p - 0.12 * (i + 1))), 0), Lr))
    m.anim("run", Lr, True, run)

    # attack (bite) ----------------------------------------------------
    La = 0.8
    attack = {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.2, 10, 0, 0), (0.38, -16, 0, 0), (0.55, -10, 0, 0), (0.8, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.2, 4, 0, 0), (0.38, -8, 0, 0), (0.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.2, 8, 0, 0), (0.38, -6, 0, 0), (0.8, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -32, 0, 0), (0.36, -36, 0, 0), (0.44, 0, 0, 0), (0.8, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.2, 2, 0, 0), (0.4, -4, 0, 0), (0.8, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.2, -2, 0, 0), (0.4, 4, 0, 0), (0.8, 0, 0, 0)])),
    }
    m.anim("attack", La, False, attack)

    # roar ---------------------------------------------------------------
    Lo = 2.4
    jaw_keys = [(0, 0, 0, 0), (0.35, -38, 0, 0)]
    t = 0.45
    while t < 1.75:
        jaw_keys.append((round(t, 2), -42 + (3 if int(t * 20) % 2 else -2), 0, 0))
        t += 0.15
    jaw_keys += [(1.95, -10, 0, 0), (2.4, 0, 0, 0)]
    roar = {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.4, 18, 0, 0), (1.0, 20, -4, 0), (1.6, 18, 4, 0), (2.0, 4, 0, 0), (2.4, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.4, 6, 0, 0), (1.6, 6, 0, 0), (2.4, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.4, 8, 0, 0), (1.0, 9, 0, 2), (1.6, 9, 0, -2), (2.4, 0, 0, 0)])),
        "jaw": track(rot=keys(jaw_keys)),
        "body": track(rot=keys([(0, 0, 0, 0), (0.4, 5, 0, 0), (1.6, 5, 0, 0), (2.4, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.4, 0, 0.6, 0), (1.6, 0, 0.6, 0), (2.4, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.4, -6, 0, 0), (1.6, -6, 0, 0), (2.4, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.4, -3, 4, 0), (1.0, -3, -4, 0), (1.6, -3, 4, 0), (2.4, 0, 0, 0)])),
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.4, -20, 0, -10), (1.6, -20, 0, -10), (2.4, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.4, -20, 0, 10), (1.6, -20, 0, 10), (2.4, 0, 0, 0)])),
    }
    m.anim("roar", Lo, False, roar)
