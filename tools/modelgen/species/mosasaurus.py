"""
Mosasaurus hoffmannii  (Late Cretaceous, Maastrichtian; seas of Europe and North America)

Reference (Wikipedia): up to ~12-17 m long, one of the largest marine reptiles; a big skull (~1.5 m) with
conical teeth and extra teeth on the palate; long streamlined body, four paddle-shaped flippers (the front pair
bigger), and a long tail ending in a crescent fluke whose lower lobe holds the bent-down vertebrae (hypocercal
tail, known from Prognathodon and Platecarpus fossils). Countershaded: dark back, pale belly. Gave birth to live
young in the water. Not a dinosaur: a marine lizard related to monitor lizards and snakes.

Modelled ~100 px long; scale 2.4 in game -> ~15 blocks.
"""
import math
from rig import Model, track, keys, wave, add_knockout

ID = "mosasaurus"


def build():
    m = Model(ID, render_scale=1.0)
    m.palette = {
        "dorsal": "#2e3a44", "flank": "#566670", "belly": "#d8dbd0",
        "limb": "#34424c", "limb_top": "#3e4c56",
        "fin": "#26323a", "fin_edge": "#4a5a64",
        "tooth": "#efe9d6", "mouth": "#8a3a36", "gum": "#5e2623",
        "eye": "#c8b04a", "pupil": "#0f0c0a", "scar": "#7c8a90",
    }
    m.sexes = {"male": {}, "female": {"dorsal": "#36424a", "flank": "#5e6c72"}}

    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 8, 0))
    m.box("body", (-6.5, 1, -12), (6.5, 15, 10), name="torso")
    m.box("body", (-6, 2, -22), (6, 14, -12), name="chest")

    neck = m.chain(["neck"], "body", 0, [(8.5, -21), (9, -27)], "-z", [(10, 10)], overlap=(1.0, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    m.box("skull", *R(-4.5, -3, -8, 4.5, 4, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -3, -21, 3, 2, -8), name="snout",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}})
    m.box("skull", *R(-2, -3, -23, 2, 1, -21), name="snout_tip", paint={"faces": {"down": "mouth"}})
    m.bone("jaw", "skull", (0, ay - 3, az - 3))
    m.box("jaw", *R(-3, -6, -21, 3, -3, -6), name="jaw", paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}})
    m.box("jaw", *R(-4.5, -6, -6, 4.5, -3, 0), name="jaw_back", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4.5, ay + 1.5, az - 5.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4.5, ay + 1.5, az - 5.0), "r": 1.0, "side": -1},
    ]

    # tail: long, tapering, ending in a crescent fluke (lower lobe bigger)
    tail = m.chain(["tail1", "tail2", "tail3", "tail4", "tail5"], "body", 0,
                   [(8, 9), (8, 21), (7.5, 32), (7, 42), (6.5, 51), (6, 59)], "+z",
                   [(11, 11), (9, 9), (7, 7), (5, 5), (3, 3)], overlap=(1.0, 1.0))
    ey, ez = tail["end"]
    m.bone("fluke", "tail5", (0, ey, ez))
    m.box("fluke", (-0.5, ey - 2.5, ez - 2), (0.5, ey + 2.5, ez + 16), name="fluke_lower", tag="fin",
          rot=(-40, 0, 0), origin=(0, ey, ez - 2))
    m.box("fluke", (-0.5, ey - 2, ez - 2), (0.5, ey + 2, ez + 11), name="fluke_upper", tag="fin",
          rot=(35, 0, 0), origin=(0, ey, ez - 2))
    # low keel along the top of the tail
    for k in (2, 3, 4):
        sg = tail["segments"][k - 1]
        y0, z0 = sg["unposed"]
        L = int(round(sg["len"]))
        h = (9, 7, 5)[k - 2] / 2
        m.box(f"tail{k}", (-0.5, y0 + h, z0), (0.5, y0 + h + (2, 2, 1)[k - 2], z0 + L), name="keel", tag="fin")

    # flippers: flat paddles, the front pair bigger
    def flippers(side, s):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        m.bone(f"flipper_front_{side}", "body", (5.5 * s, 4, -17), (0, -30 * s, -20 * s))
        a, b = X(5.5, 17.5)
        m.box(f"flipper_front_{side}", (a, 3.5, -20), (b, 4.5, -14), tag="fin", name="paddle")
        m.bone(f"flipper_back_{side}", "body", (5.5 * s, 4, 6), (0, -35 * s, -20 * s))
        a, b = X(5.5, 13.5)
        m.box(f"flipper_back_{side}", (a, 3.5, 4), (b, 4.5, 9), tag="fin", name="paddle")
    m.sym(flippers)

    def pattern(model, tx, rgb, region):
        P = tx.P
        if tx.cube.tag == "fin":
            col = tx.pal["fin"].copy()
            if tx.edge:
                col = tx.pal["fin_edge"].copy()
            return col
        if tx.cube.tag == "skin" and region == "dorsal":
            # faint mottling on the back
            if math.sin(P[2] * 0.9 + 1.7 * math.sin(P[0] * 0.8)) > 0.75:
                rgb = rgb * 0.88
        if tx.cube.tag == "skin" and region == "flank" and abs(math.sin(P[2] * 0.37 + P[1] * 0.2)) > 0.985:
            rgb = tx.pal["scar"].copy()  # old scars from fights
        return rgb
    m.pattern = pattern

    animations(m)
    return m


TAIL = ["tail1", "tail2", "tail3", "tail4", "tail5", "fluke"]


def swim(L, amp, flip, head=3.0):
    """Side to side wave running down the tail (yaw), the body following a little."""
    t = {}
    for i, b in enumerate(TAIL):
        a = amp * (0.35 + 0.22 * i)
        t[b] = track(rot=wave(8, lambda p, i=i, a=a: (0, a * math.sin(2 * math.pi * (p - 0.12 * i)), 0), L))
    t["body"] = track(rot=wave(8, lambda p: (0, -amp * 0.25 * math.sin(2 * math.pi * (p + 0.1)), 0), L),
                      pos=wave(8, lambda p: (0, 0.3 * math.sin(4 * math.pi * p), 0), L))
    t["neck"] = track(rot=wave(8, lambda p: (0, head * math.sin(2 * math.pi * (p + 0.25)), 0), L))
    for side, s in (("l", 1), ("r", -1)):
        t[f"flipper_front_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * flip * math.sin(2 * math.pi * p)), L))
        t[f"flipper_back_{side}"] = track(rot=wave(8, lambda p, s=s: (0, 0, s * flip * 0.7 * math.sin(2 * math.pi * (p - 0.3))), L))
    return t


def animations(m):
    m.anim("idle", 4.0, True, swim(4.0, 6, 6, 2.0))
    m.anim("walk", 2.0, True, swim(2.0, 12, 10))
    m.anim("run", 1.0, True, swim(1.0, 16, 12, 4.0))
    # never tamed in this version, but the base class expects a resting pose
    m.anim("sit", 4.0, True, swim(4.0, 4, 4, 1.0))
    # bite: head pulls back, jaw opens wide, snaps shut
    m.anim("attack", 0.7, False, {
        "neck": track(rot=keys([(0, 0, 0, 0), (0.2, -12, 0, 0), (0.38, 10, 0, 0), (0.7, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -38, 0, 0), (0.34, -40, 0, 0), (0.4, 0, 0, 0), (0.7, 0, 0, 0)])),
        "body": track(pos=keys([(0, 0, 0, 0), (0.2, 0, 0, 2), (0.38, 0, 0, -3), (0.7, 0, 0, 0)])),
    })
    # knocked out (docs/DOMESTICACAO.md): rolled onto its side, flippers hanging, the tail trailing in a lazy curve;
    # in the water it floats like this, beached it lies on the sand. Also brings wake / eat / beg / tame.
    # (the body rolls ~90 degrees, so a pitch here curves the tail along the ground and a yaw would lift it)
    limp = {"neck": (3, -4, 0), "skull": (2, 0, 0), "jaw": (-14, 0, 0),
            "tail1": (-3, 0, 0), "tail2": (-5, 0, 0), "tail3": (-6, 0, 0), "tail4": (-6, 0, 0), "tail5": (-5, 0, 0),
            # paddles swept back along the flanks (base yaw is -30/+30, so -60/+60 lays them along the body)
            "flipper_front_l": (0, -60, 20), "flipper_front_r": (0, 60, -20),
            "flipper_back_l": (0, -60, 20), "flipper_back_r": (0, 60, -20)}
    add_knockout(m, roll=85, lift=0.3, shift=0.5, joints=limp, neck_down=-10)
