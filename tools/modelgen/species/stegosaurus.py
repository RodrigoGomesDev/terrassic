"""
Stegosaurus stenops  (Late Jurassic, North America / Portugal)

Reference (Wikipedia): S. stenops ~6.5 m (large individuals 7.5-9 m), mass
~3.5 t, 17-22 plates in two staggered (alternating) rows, the largest over the
hips (> 60 x 60 cm), four horizontal tail spikes 60-90 cm ("thagomizer"),
forelimbs much shorter than hind limbs, rounded back, tail held high, small
narrow head carried low (no higher than ~1 m).

In game: scale ~0.6 -> ~4.5 blocks long, ~2 blocks tall at the plates.
"""
import math
from rig import Model, wave, sinx, track, keys
from quadruped import hind_leg, front_leg, quad_gait, quad_sit
from paint import vnoise, hex2rgb, mix, smooth

ID = "stegosaurus"


def build():
    m = Model(ID, render_scale=1.0)
    m.palette = {
        "dorsal": "#4f5a35", "flank": "#727c49", "belly": "#c4c090",
        "limb": "#5b6140", "limb_top": "#6c7449",
        "claw": "#36352d", "claw_base": "#36352d",
        "spike_base": "#7d6c4f", "spike_tip": "#efe6cc",
        "plate": "#7a2e1f", "plate_edge": "#e09a44",
        "beak": "#4b453a", "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
        "eye": "#b5862c", "pupil": "#140f0a",
    }
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 22, 8))
    torso = [
        ((-7, 12, 0), (7, 26, 15), "hips"),
        ((-8, 10, -11), (8, 25, 2), "midbody"),
        ((-6, 8, -19), (6, 20, -9), "chest"),
        ((-5, 25, -6), (5, 28, 12), "arch"),
    ]
    for a, b, n in torso:
        m.box("body", a, b, name=n)

    neck = m.chain(["neck1", "neck2"], "body", 0, [(14, -18), (11.5, -23), (10, -27)], "-z",
                   [(7, 7), (6, 6)], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-8 - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    m.box("skull", *R(-3, -3, -5, 3, 2, 1), name="cranium")
    m.box("skull", *R(-2, -3, -10, 2, 1, -5), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1, -3, -12, 1, 0, -10), name="beak", tag="beak")
    m.bone("jaw", "skull", (0, ay - 3, az - 2))
    m.box("jaw", *R(-2, -4, -11, 2, -3, -2), name="jaw", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3, ay + 0.0, az - 3.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 0.0, az - 3.0), "r": 1.0, "side": -1},
    ]

    m.sym(lambda s, sx: hind_leg(m, s, sx, 6, [(19, 8), (10, 7), (3.5, 10), (2, 9)],
                                 [(6, 8, 0.0), (5, 5, 0.5, "limb"), (4, 4, 0.0, "limb")], (6, 4, 2)))
    m.sym(lambda s, sx: front_leg(m, s, sx, 6, [(13, -14), (6.5, -13), (2, -14.5)],
                                  [(5, 6, 0.0), (4, 4, 0.0, "limb")], (5, 3, 2)))
    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0,
                   [(24, 14), (23, 24), (20.5, 34), (18, 43), (16, 51)], "+z",
                   [(9, 9), (7, 7), (5, 5), (3, 3)], overlap=(1.0, 1.0))

    # ---------------------------------------------------------- plates
    k = [0]

    def plate(bone, y_top, z, s):
        x = 1.0 if k[0] % 2 == 0 else -1.0
        k[0] += 1
        cy = y_top + s * 0.45
        m.box(bone, (x - 0.5, cy - s / 2, z - s / 2), (x + 0.5, cy + s / 2, z + s / 2), tag="plate", name="plate",
              rot=(45, 0, -8 * x), origin=(x, cy, z))

    segs = {s["bone"]: s for s in neck["segments"] + tail["segments"]}

    def on_seg(bone, t, s, half_h):
        sg = segs[bone]
        y0, z0 = sg["unposed"]
        L = sg["len"]
        if bone.startswith("neck"):
            z = z0 - t * L
        else:
            z = z0 + t * L
        plate(bone, y0 + half_h, z, s)

    on_seg("neck2", 0.6, 3, 3)
    on_seg("neck1", 0.25, 3, 3.5)
    on_seg("neck1", 0.75, 4, 3.5)
    for z, s, top in ((-16, 4, 20), (-12, 5, 23), (-7.5, 6, 26), (-3, 7, 28), (1.5, 8, 28), (6, 8, 28), (10.5, 7, 27)):
        plate("body", top - 0.5, z, s)
    on_seg("tail1", 0.35, 7, 4.5)
    on_seg("tail1", 0.8, 6, 4.5)
    on_seg("tail2", 0.3, 5, 3.5)
    on_seg("tail2", 0.75, 4, 3.5)
    on_seg("tail3", 0.4, 3, 2.5)

    # ---------------------------------------------------------- thagomizer
    t4 = segs["tail4"]
    y0, z0 = t4["unposed"]
    for i, dz in enumerate((2.5, 6.0)):
        for sx in (1, -1):
            x = 1.0 * sx
            zb = z0 + dz
            m.box("tail4", (x - 0.5, y0 + 0.5, zb), (x + 0.5, y0 + 1.5, zb + 8), tag="spike", name="spike",
                  rot=(-22 - 6 * i, 52 * sx, 0), origin=(x, y0 + 1, zb), paint={"axis": "+z"})


    def pattern(model, tx, rgb, region):
        P = tx.P
        c = tx.cube
        if c.tag == "plate":
            cy_, cz_ = c.origin[1], c.origin[2]
            half = c.size[1] / 2
            e = max(abs(P[1] - cy_), abs(P[2] - cz_)) / max(half, 1e-6)
            col = mix(tx.pal["plate"], tx.pal["plate_edge"], smooth(0.25, 1.0, e))
            vein = math.sin((P[1] - cy_ + P[2] - cz_) * 2.2)
            if vein > 0.85 and e < 0.85:
                col = col * 0.8
            return col
        if c.tag == "skin":
            n = vnoise(P[0] / 2.5, P[1] / 2.5, P[2] / 2.5, 21)
            rgb = rgb * (0.88 + 0.2 * n)
            if region in ("dorsal", "flank") and tx.face in ("east", "west"):
                stripe = math.sin(P[2] * 2 * math.pi / 6.0)
                if stripe > 0.6 and tx.cy > 0.5:
                    rgb = rgb * 0.82
        return rgb
    m.pattern = pattern
    m.sexes = {"male": {"plate": "#8a2a1a", "plate_edge": "#f0a640"},
               "female": {"plate": "#5e4632", "plate_edge": "#b99c66", "dorsal": "#56603a"}}
    animations(m)
    return m


def animations(m):
    Li = 4.0
    sy = lambda a, ph=0.0: (lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0))
    m.anim("idle", Li, True, {
        "body": track(rot=wave(8, sinx(0.5), Li), pos=wave(8, lambda p: (0, 0.2 * math.sin(2 * math.pi * p), 0), Li)),
        "neck1": track(rot=wave(8, lambda p: (2.5 * math.sin(2 * math.pi * p), 3 * math.sin(2 * math.pi * (p + 0.2)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * (p + 0.25)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-5 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
        "tail1": track(rot=wave(8, sy(3), Li)), "tail2": track(rot=wave(8, sy(4, -0.1), Li)),
        "tail3": track(rot=wave(8, sy(5, -0.2), Li)), "tail4": track(rot=wave(8, sy(6, -0.3), Li)),
    })
    for name, Lc, Ah, Af, bob in (("walk", 1.8, 18, 16, 0.5), ("run", 1.0, 26, 24, 1.0)):
        t = quad_gait(Lc, Ah, Af)
        t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 1.8 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, b=bob: (0, b * math.cos(4 * math.pi * p) - b * 0.5, 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, b=bob: (-2 * b * math.cos(4 * math.pi * p), 0, 0), Lc))
        for i in range(4):
            t[f"tail{i+1}"] = track(rot=wave(8, sy(3 + 1.5 * i, 0.25 - 0.08 * i), Lc))
        m.anim(name, Lc, True, t)
    # attack: big sideways tail swing with the thagomizer
    m.anim("attack", 1.0, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.3, 0, 10, 0), (0.55, 0, -14, 0), (1.0, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.3, -4, 14, 0), (0.55, -4, -22, 0), (1.0, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.3, 0, 14, 0), (0.55, 0, -24, 0), (1.0, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.3, 0, 12, 0), (0.55, 0, -24, 0), (1.0, 0, 0, 0)])),
        "tail4": track(rot=keys([(0, 0, 0, 0), (0.3, 0, 10, 0), (0.55, 0, -20, 0), (1.0, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, 0, -8, 0), (0.55, 0, 8, 0), (1.0, 0, 0, 0)])),
    })
    m.anim("sit", 4.0, True, quad_sit(m, 7))
    jk = [(0, 0, 0, 0), (0.6, 0, 0, 0)]
    for k in range(6):
        t0 = 0.75 + k * 0.3
        jk += [(t0, -12, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(2.8, 0, 0, 0)]
    m.anim("graze", 2.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.6, -14, 0, 0), (2.3, -14, 0, 0), (2.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.6, -14, 0, 0), (2.3, -14, 0, 0), (2.8, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
    })
