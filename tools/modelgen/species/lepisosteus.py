"""
Lepisosteus  (Late Cretaceous to today; Hell Creek, Lance, Judith River rivers and deltas)

Reference (Wikipedia; Wiley 1976; Grande 2010; Brinkman et al. 2014): the gar, a living fossil already in the
Cretaceous rivers. A long cylindrical body armoured in hard rhombic ganoid scales in diagonal rows, each scale
with an enamel (ganoine) shine and joined to the next by a peg; the head covered in bony plates; a long narrow
snout, both jaws lined with needle teeth and a few bigger fangs, the nostrils at the very tip; the dorsal and anal
fins set far back, one over the other, near a rounded tail whose upper lobe still carries the scaled end of the
body axis (an abbreviated heterocercal tail); the leading edges of the fins armed with spiny fringing scales
(fulcra); small paired fins low on the body. A swim bladder that breathes air: it hangs still just under the
surface and strikes sideways. Hell Creek gars reached ~1-1.2 m. Olive above, bronze on the flanks, a cream belly,
round dark spots on the back, the flanks, the head and every fin.

Fish rig (fish.py) modelled large (render_scale 0.2): ~108 px snout to tail, SIZES scales it to 1.0 m. In game: the
river food fish of the Terrassic world, the salmon's seat; rivers, swamps and deltas, in little groups; snaps
sideways at small fish. Its hide is the ganoid armour. Males greener with more spots, females browner.
"""
import math
from paint import vnoise
from rig import track, keys
from fish import build_fish, paint_eye

ID = "lepisosteus"


def body(m):
    # the long cylindrical torso: a core with a narrower back and belly layer
    m.box("body", (-3.5, 6, -16), (3.5, 14, 10), name="torso")
    m.box("body", (-2.5, 14, -15), (2.5, 15, 9), name="back")
    m.box("body", (-2.5, 5, -15), (2.5, 6, 9), name="belly")


def neck(m):
    m.box("neck", (-3.5, 6, -22), (3.5, 14, -16), name="shoulder")
    m.box("neck", (-2.5, 14, -22), (2.5, 15, -16), name="shoulder_top")
    m.box("neck", (-2.5, 5, -22), (2.5, 6, -16), name="shoulder_low")


def head(m):
    # a flat bony head and the long narrow snout in three steps, ending in the fleshy knob with the nostrils
    m.box("skull", (-3, 7, -31), (3, 13, -22), tag="plate", name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", (-2, 13, -30), (2, 14, -22), tag="plate", name="cranium_top")
    m.box("skull", (-2, 9, -39), (2, 12, -31), tag="plate", name="snout",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1, "freq": 1.0}})
    m.box("skull", (-1.5, 9, -47), (1.5, 11, -39), tag="plate", name="snout_mid",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1, "freq": 1.0}})
    m.box("skull", (-1, 9, -54), (1, 11, -47), tag="plate", name="snout_tip",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1, "freq": 1.0}})
    m.box("skull", (-1.5, 9, -56), (1.5, 11, -54), name="snout_knob")
    # the lower jaw in the same three steps, the throat behind
    m.box("jaw", (-2.5, 6, -39), (2.5, 9, -23), tag="plate", name="jaw",
          paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1, "freq": 1.0}})
    m.box("jaw", (-1.5, 7, -47), (1.5, 9, -39), tag="plate", name="jaw_mid",
          paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1, "freq": 1.0}})
    m.box("jaw", (-1, 7, -53), (1, 9, -47), tag="plate", name="jaw_tip",
          paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1, "freq": 1.0}})
    m.box("jaw", (-2, 5, -31), (2, 6, -23), tag="throat", name="gular")

    def fangs(side, s):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        x0, x1 = X(0.5, 1.5)
        # the bigger fangs among the needle teeth, up and down the snout
        for z in (-45, -37):
            m.box("skull", (x0, 8, z), (x1, 9, z + 1), tag="tooth_cube", name="fang", paint={"axis": "-y"})
        for z in (-42, -34):
            m.box("jaw", (x0, 9, z), (x1, 10, z + 1), tag="tooth_cube", name="fang_low", paint={"axis": "+y"})
    m.sym(fangs)
    m.decals += [
        {"kind": "spot", "bones": ["skull"], "pos": (1.5, 10.5, -55), "r": 0.5, "color": "pupil", "side": 1},
        {"kind": "spot", "bones": ["skull"], "pos": (-1.5, 10.5, -55), "r": 0.5, "color": "pupil", "side": -1},
    ]


def tail_layers(m, segs):
    # the dorsal and anal fins far back, one over the other, each with its fringe of spiny fulcra in front
    y0, z0 = segs[0]["unposed"]
    for s in (1, -1):
        base = y0 + 3.5 * s
        steps = [((z0 + 2, z0 + 9), 3), ((z0 + 3, z0 + 8), 2), ((z0 + 4, z0 + 7), 1)]
        y = base
        for (za, zb), h in steps:
            ya, yb = (y, y + h) if s > 0 else (y - h, y)
            m.box("tail1", (-0.5, ya, za), (0.5, yb, zb), tag="fin", name="dorsal" if s > 0 else "anal")
            y = yb if s > 0 else ya
        ya, yb = (base, base + 3) if s > 0 else (base - 3, base)
        m.box("tail1", (-0.5, ya, z0 + 1), (0.5, yb, z0 + 2), tag="fin", name="fulcra")


def caudal(m, ey, ez):
    # the rounded tail: the scaled end of the body axis turned up into the upper lobe, then the fan of rays
    m.box("caudal", (-1, ey - 0.5, ez - 1), (1, ey + 2.5, ez + 4), name="axis", rot=(12, 0, 0), origin=(0, ey, ez))
    m.box("caudal", (-0.5, ey - 6, ez - 1), (0.5, ey + 5, ez + 5), tag="fin", name="fan")
    m.box("caudal", (-0.5, ey - 5, ez + 5), (0.5, ey + 4, ez + 8), tag="fin", name="fan")
    m.box("caudal", (-0.5, ey - 4, ez + 8), (0.5, ey + 3, ez + 10), tag="fin", name="fan_edge")
    m.box("caudal", (-0.5, ey + 2.5, ez - 1), (0.5, ey + 4.5, ez + 1), tag="fin", name="fulcra")


FINS = [
    # small rounded paired fins low on the body
    dict(name="pectoral", parent="body", pivot=(3.5, 7, -15), rot=(0, 26, -20), sym=True, flap=("y", 14, 0.0),
         boxes=[((3.5, 4, -15), (4.5, 7, -9), "pectoral"), ((3.5, 4, -9), (4.5, 6, -6), "pectoral_tip")]),
    dict(name="pelvic", parent="body", pivot=(2.5, 6, 0), rot=(0, 14, -28), sym=True, flap=("z", 8, -0.3),
         boxes=[((2.5, 3, 0), (3.5, 6, 5), "pelvic"), ((2.5, 3, 5), (3.5, 5, 7), "pelvic_tip")]),
]


def ganoid(tx, rgb, size=2.2):
    """The rhombic ganoid scales in diagonal rows: a dark rim, the ganoine shine in the middle of each scale."""
    P = tx.P
    if tx.face in ("up", "down"):
        u, v = P[2], P[0]
    elif tx.face in ("north", "south"):
        u, v = P[0], P[1]
    else:
        u, v = P[2], P[1]
    a, b = (u + v) / size, (u - v) / size
    fa, fb = a - math.floor(a), b - math.floor(b)
    if min(fa, 1 - fa) < 0.13 or min(fb, 1 - fb) < 0.13:
        return rgb * 0.72
    if abs(fa - 0.5) < 0.22 and abs(fb - 0.5) < 0.22:
        return rgb * 1.12
    return rgb


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    name = tx.cube.name
    n = vnoise(P[0] / 1.5, P[1] / 1.5, P[2] / 1.5, 91)
    spot = vnoise(P[0] / 1.9, P[1] / 1.9, P[2] / 1.9, 113) > 0.69
    if tag == "fin":
        col = tx.pal["fin"].copy()
        if name == "fulcra":
            return tx.pal["fulcra"] * (0.9 + 0.2 * n)
        ray = P[2] if name not in ("pectoral", "pectoral_tip", "pelvic", "pelvic_tip") else P[1] + P[2] * 0.5
        col = col * (1.07 if int(math.floor(ray)) % 2 == 0 else 0.92)
        if name in ("fan", "fan_edge", "dorsal", "anal"):
            ray2 = P[1] if name.startswith("fan") else P[2]
            col = tx.pal["fin"] * (1.07 if int(math.floor(ray2)) % 2 == 0 else 0.92)
        if spot:
            col = tx.pal["spot"] * (0.9 + 0.2 * n)               # the round dark spots of the fins
        if tx.edge and name in ("fan_edge", "pectoral_tip", "pelvic_tip"):
            col = col * 0.8
        return col
    if tag == "gill_cover":
        col = tx.pal["gill"] * (0.92 + 0.16 * n)
        if (int(math.floor(P[1] * 0.8 + P[2] * 0.6))) % 3 == 0:
            col = col * 0.86                                     # the ridged bony plate
        if spot:
            col = tx.pal["spot"].copy()
        if tx.edge and P[2] > tx.cube.to[2] - 1:
            col = col * 0.7
        return col
    if tag == "throat":
        return tx.pal["belly"] * (0.92 + 0.08 * n)
    if tag in ("plate", "skin"):
        e = paint_eye(tx, rgb, (11.0, -27.0), 1.7, 0.9, 3.0)
        if e is not None:
            return e
    if tag == "plate":
        # the bony plates of the head: a network of sutures and the spots
        base, reg = rgb, region
        q = vnoise(P[0] / 2.4, P[1] / 2.4, P[2] / 2.4, 117)
        if abs(q - 0.5) < 0.035:
            return base * 0.68
        if spot and tx.face != "down":
            return tx.pal["spot"] * (0.9 + 0.2 * n)
        return base * (0.94 + 0.12 * n)
    if tag == "skin":
        if tx.cube.bone not in ("skull", "jaw"):
            rgb = ganoid(tx, rgb, 2.4 if region != "belly" else 2.0)
        if spot and region in ("dorsal", "flank"):
            rgb = tx.pal["spot"] * (0.9 + 0.2 * n)
        elif spot and region == "belly" and n > 0.6:
            rgb = rgb * 0.8
    return rgb


def attack(m):
    # the sideways strike: it hangs still, then whips the head to the side and snaps the needle jaws shut
    m.anim("attack", 0.5, False, {
        "body": track(pos=keys([(0, 0, 0, 0), (0.12, 0, 0, 1), (0.25, 0, 0, -3), (0.5, 0, 0, 0)]),
                      rot=keys([(0, 0, 0, 0), (0.1, 0, 6, 0), (0.22, 0, -8, 0), (0.5, 0, 0, 0)])),
        "neck": track(rot=keys([(0, 0, 0, 0), (0.1, 0, -14, 0), (0.22, 0, 20, 0), (0.32, 0, 0, 0), (0.5, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.1, -16, 0, 0), (0.2, -18, 0, 0), (0.26, 0, 0, 0), (0.5, 0, 0, 0)])),
        "operculum_l": track(rot=keys([(0, 0, 0, 0), (0.12, 0, 18, 0), (0.3, 0, 0, 0), (0.5, 0, 0, 0)])),
        "operculum_r": track(rot=keys([(0, 0, 0, 0), (0.12, 0, -18, 0), (0.3, 0, 0, 0), (0.5, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.1, 0, 14, 0), (0.25, 0, -18, 0), (0.5, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.12, 0, 18, 0), (0.27, 0, -22, 0), (0.5, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.15, 0, 22, 0), (0.3, 0, -26, 0), (0.5, 0, 0, 0)])),
        "tail4": track(rot=keys([(0, 0, 0, 0), (0.17, 0, 24, 0), (0.32, 0, -26, 0), (0.5, 0, 0, 0)])),
    })


LIMP = {"neck": (2, 0, 0), "jaw": (-8, 0, 0), "operculum_l": (0, 10, 0), "operculum_r": (0, -10, 0),
        "tail1": (-2, 0, 0), "tail2": (-4, 0, 0), "tail3": (-5, 0, 0), "tail4": (-5, 0, 0),
        "pectoral_l": (0, -20, 10), "pectoral_r": (0, 20, -10), "pelvic_l": (0, -10, 20), "pelvic_r": (0, 10, -20)}

S = dict(
    render_scale=0.2,
    palette={"dorsal": "#4a5a30", "flank": "#8c8656", "belly": "#e2dab6", "gill": "#6a6a42", "spot": "#2a2c18",
             "fin": "#9a8a52", "fulcra": "#4a4428",
             "limb": "#4a5a30", "limb_top": "#5a6a3c", "claw": "#e2dab6",
             "tooth": "#f6f2e6", "mouth": "#8a3844", "gum": "#5e262e",
             "tooth_cube": "#f6f2e6", "tooth_cube_base": "#dad4c2", "tooth_cube_tip": "#fcfaf2",
             "eye": "#d0a840", "eye_shine": "#fff4d0", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#405a2a", "flank": "#84885a"},
           "female": {"dorsal": "#585a34", "flank": "#968a5c", "spot": "#3a3424"}},
    pattern=pattern,
    body_pivot=(10, 0), body=body,
    neck_pivot=(10, -16), neck=neck,
    head_pivot=(10, -22), jaw_pivot=(8, -23), head=head,
    operculum=dict(pivot=(3, 10, -25), boxes=[((3, 7, -25), (4, 13, -22), "operculum")]),
    tail=dict(points=[(10, 10), (10, 19), (10, 28), (10, 36), (10, 42)],
              sections=[(6, 7), (5, 6), (4, 5), (3, 4)], layers=tail_layers),
    caudal=caudal,
    fins=FINS,
    swim=dict(idle=(2.6, 5, 1.5, 0.7), walk=(1.3, 12, 2.0, 1.0), run=(0.55, 20, 2.5, 1.3), sit=(3.2, 3, 1.0, 0.4)),
    breathe=(8, 2),
    attack=attack,
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-6),
)


def build():
    return build_fish(ID, S)
