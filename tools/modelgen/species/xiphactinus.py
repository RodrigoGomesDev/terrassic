"""
Xiphactinus audax  (Late Cretaceous, Western Interior Seaway, Kansas)

Reference:
  - Size (Everhart 2005 "Oceans of Kansas"; Schwimmer et al. 1997): 4.5-6 m, the biggest ichthyodectiform fish.
    The famous "fish within a fish" (FHSM VP-333) holds a 1.8 m Gillicus swallowed whole.
  - Shape: a long, deep, laterally compressed tarpon-like body; a blunt deep head with a steep forehead and a big
    eye; a huge UPTURNED mouth, the lower jaw jutting up past the short upper jaw ("bulldog"), with long fangs at the
    front of both jaws and smaller teeth behind; a big bony gill cover.
  - Fins: long pointed pectorals low behind the head, small pelvics mid-belly, a dorsal and an anal fin set far
    back near the tail, and a tall, deeply forked tail with equal lobes on a narrow caudal peduncle.
  - Colour: blue-grey back over mirror-silver flanks (as in tarpons); males a deeper blue with a dark eye stripe,
    females greyer.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the marine archetype geometry; only
its swimming wave and knockout), at ~16 px = 1 m. The swim wave's position keys are scaled from the old model.
"""
import math
from rig import Model, track, keys, add_knockout, lowest_point
import marine
from groundfit import fit_to_ground

ID = "xiphactinus"
K = 1.16         # 16 px/m now / ~13.8 px/m of the old model
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (14, 0)
# compressed spindle (z0, z1, half width, y0, y1), each section with a narrower ridge above and keel below
TORSO = [(-20, -12, 3.5, 5, 23), (-12, 0, 4, 3, 25), (0, 12, 3.5, 4, 24), (12, 22, 3, 6, 21), (22, 30, 2.5, 8, 19)]
TAIL = ([(14, 28), (14, 36), (14, 43), (14, 49)], [(5, 10), (3, 8), (2, 5)])
FLUKE = {"lower": (36, 4, 14, 2, 4), "upper": (-36, 4, 14, 2, 4)}   # pitch, height, length, tip height, tip length
# fins (left): pivot, rotation, parts (x0, x1, y0, y1, z0, z1): long pointed pectorals, small pelvics
FLIPPERS = [("flipper_front", (3.5, 7, -16), (0, -35, -25),
             [(3, 6, 6, 9, -18, -14), (6, 14, 7, 8, -18, -13), (14, 19, 7, 8, -17, -14), (19, 22, 7, 8, -16, -15)]),
            ("flipper_back", (2.5, 5, 4), (0, -30, -30),
             [(2, 5, 4, 6, 2, 6), (5, 9, 4.5, 5.5, 2, 6), (9, 11, 4.5, 5.5, 3, 5)])]
DORSAL = [(-0.5, 24, 8, 0.5, 27, 18), (-0.5, 27, 10, 0.5, 30, 17), (-0.5, 30, 12, 0.5, 32, 16)]
ANAL = [(-0.5, 3, 13, 0.5, 6, 21), (-0.5, 1, 15, 0.5, 3, 21)]


def pattern(model, tx, rgb, region):
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("tooth_cube", "eye", "mouth"):
        return rgb
    if tag == "fin":
        col = pal["fin_edge"].copy() if tx.edge else pal["fin"].copy()
        ray = P[0] if cube.bone.startswith("flipper") else P[2] + P[1] * 0.5
        if int(math.floor(ray * 1.2)) % 2 == 0:
            col = col * 0.88                                               # fin rays
        return col
    if tag == "skin":
        if cube.bone == "skull":
            if cube.name in ("opercle", "opercle_low") and region != "dorsal":
                rgb = pal["gill"].copy()
                if P[2] > cube.to[2] - 1.01:
                    rgb = rgb * 0.8                                        # rim of the gill cover
            if abs(P[1] - model._eye_y) < 0.8 and tx.face in ("east", "west") and cube.name != "forehead":
                rgb = pal["stripe"].copy()                                 # stripe through the eye
            return rgb
        if region == "flank":
            # mirror-silver flanks, one row of big cycloid scales per two px, a lateral line
            sc = (int(math.floor(P[2] / 2.0)) + int(math.floor(P[1] / 2.0))) % 2
            rgb = rgb * (1.08 if sc == 0 else 0.95)
            if abs(P[1] - (BODY[0] + 1.5)) < 0.5:
                rgb = rgb * 0.82
        elif region == "dorsal" and math.sin(P[2] * 1.1) * math.sin(P[0] * 2.0) > 0.6:
            rgb = rgb * 0.88
    return rgb


PALETTE = {"dorsal": "#3a5068", "flank": "#aab4b8", "belly": "#e8ece8", "gill": "#7a8692", "stripe": "#1e2630",
           "limb": "#3a5068", "limb_top": "#4a6078", "fin": "#4a5a66", "fin_edge": "#8a98a0",
           "tooth": "#f4f0e4", "mouth": "#8a3844", "gum": "#5e262e",
           "tooth_cube_base": "#d8d2c0", "tooth_cube_tip": "#fbf8f0", "eye": "#d8c060", "pupil": "#0f0c0a"}
SEXES = {"male": {"dorsal": "#2c4466", "stripe": "#141a22"},
         "female": {"dorsal": "#4a5a66", "flank": "#b4babc", "stripe": "#5a6470"}}


def attack(m):
    # the lunge: a tail thrust shoots the body forward, the mouth gapes and the jaws clap shut on the prey
    m.anim("attack", 0.6, False, {
        "body": track(pos=keys([(0, 0, 0, 0), (0.15, 0, 0, 2 * K), (0.3, 0, 0, -5 * K), (0.6, 0, 0, 0)]),
                      rot=keys([(0, 0, 0, 0), (0.15, 5, 0, 0), (0.3, 1, 0, 0), (0.6, 0, 0, 0)])),
        "neck": track(rot=keys([(0, 0, 0, 0), (0.15, -14, 0, 0), (0.3, 0, 0, 0), (0.6, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.15, -34, 0, 0), (0.24, -36, 0, 0), (0.3, 0, 0, 0), (0.6, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.1, 0, 18, 0), (0.3, 0, -14, 0), (0.6, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.12, 0, 22, 0), (0.32, 0, -18, 0), (0.6, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.15, 0, 26, 0), (0.35, 0, -22, 0), (0.6, 0, 0, 0)])),
    })


# knocked out (stunned, on its side): fins folded, tail limp
LIMP = {"neck": (2, 0, 0), "jaw": (-10, 0, 0), "tail1": (-3, 0, 0), "tail2": (-5, 0, 0), "tail3": (-6, 0, 0),
        "flipper_front_l": (0, -50, 10), "flipper_front_r": (0, 50, -10),
        "flipper_back_l": (0, -40, 10), "flipper_back_r": (0, 40, -10)}
SWIM = dict(idle=(2.4, 8, 5, 2.0), walk=(1.2, 16, 8), run=(0.6, 22, 10, 3.0), sit=(3.0, 5, 4, 1.0))


def lift(m, dy):
    for b in m.bones[1:]:
        b.pivot[1] += dy
    for c in m.cubes:
        c.frm[1] += dy
        c.to[1] += dy
        c.origin[1] += dy
    m.decals = [dict(d, pos=(d["pos"][0], d["pos"][1] + dy, d["pos"][2])) for d in m.decals]
    m._eye_y += dy


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for z0, z1, hw, y0, y1 in TORSO:
        m.box("body", (-hw, y0, z0), (hw, y1, z1), name="torso")
        m.box("body", (-(hw - 1), y1, z0 + 1), (hw - 1, y1 + 1, z1 - 1), name="back")
        m.box("body", (-(hw - 1), y0 - 1, z0 + 1), (hw - 1, y0, z1 - 1), name="belly")
    for k, box in enumerate(DORSAL):
        m.box("body", box[:3], box[3:], tag="fin", name="dorsal_fin")
    for box in ANAL:
        m.box("body", box[:3], box[3:], tag="fin", name="anal_fin")

    # the "neck" is the back of the skull: the whole head tilts on it when the mouth opens
    neck = m.chain(["neck"], "body", 0, [(14, -19), (14, -22)], "-z", [(6, 16)], overlap=(1.0, 0.0))
    ay, az = neck["end"]
    m.bone("head", "neck", (0, ay, az))
    m.bone("skull", "head", (0, ay, az))
    m.bone("jaw", "skull", (0, ay - 4, az - 5))
    m._eye_y = ay + 3

    def S(name, box, tag="skin", bone="skull", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head (head px): steep forehead, big eye, the bony gill cover, a short upper jaw
    S("cranium", (-4, -4, -8, 4, 9, 0), paint=MOUTH_DOWN)
    S("opercle", (-4.5, -4, -4, 4.5, 6, 1))                                 # the gill cover, standing proud
    S("opercle_low", (-4, -9, -6, 4, -4, 1))
    S("forehead", (-3, 3, -12, 3, 8, -8))
    S("snout", (-3, -3, -13, 3, 3, -8), paint=MOUTH_DOWN)
    S("premaxilla", (-2.5, -3, -15, 2.5, 1, -13), paint=MOUTH_DOWN)
    # --- the big upturned lower jaw: deep, and jutting up in front of the upper one
    S("jaw", (-3.5, -9, -13, 3.5, -3, -6), bone="jaw", paint=MOUTH_UP)
    S("jaw_front", (-3, -8, -16, 3, -3, -13), bone="jaw", paint=MOUTH_UP)
    S("chin", (-2, -6, -17, 2, -1, -16), bone="jaw", paint=MOUTH_UP)
    for s in (1, -1):
        for z, half, L in ((-15, 2.5, 3), (-13, 3, 2), (-11, 3, 1)):          # upper fangs, the front ones long
            a, b = sorted((s * half, s * (half - 1)))
            S("fang", (a, -3 - L, z, b, -3, z + 1), tag="tooth_cube", paint={"axis": "-y"})
        a, b = sorted((s * 2, s * 1))                                         # lower fangs on the rising chin
        S("fang_low", (a, -1, -17, b, 2, -16), tag="tooth_cube", bone="jaw", paint={"axis": "+y"})
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (4, ay + 3, az - 6), "r": 1.3, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-4, ay + 3, az - 6), "r": 1.3, "side": -1}]

    # --- tail: narrow peduncle, the tall forked caudal fin
    names = [f"tail{i + 1}" for i in range(len(TAIL[1]))]
    tail = m.chain(names, "body", 0, TAIL[0], "+z", TAIL[1], overlap=(1.0, 1.0))
    ey, ez = tail["end"]
    m.bone("fluke", names[-1], (0, ey, ez))
    for lobe, (pitch, h, L, th, tl) in FLUKE.items():
        org = (0, ey, ez - 2)
        m.box("fluke", (-0.5, ey - h / 2, ez - 2), (0.5, ey + h / 2, ez - 2 + L), name=f"fluke_{lobe}", tag="fin",
              rot=(pitch, 0, 0), origin=org)
        m.box("fluke", (-0.5, ey - th / 2, ez - 2 + L), (0.5, ey + th / 2, ez - 2 + L + tl), name=f"fluke_{lobe}_tip",
              tag="fin", rot=(pitch, 0, 0), origin=org)

    for name, (px, py, pz), (rx, ry, rz), parts in FLIPPERS:
        for side, s in (("l", 1), ("r", -1)):
            b = f"{name}_{side}"
            m.bone(b, "body", (px * s, py, pz), (rx, ry * s, rz * s))
            for k, (x0, x1, y0, y1, z0, z1) in enumerate(parts):
                a, c = sorted((x0 * s, x1 * s))
                m.box(b, (a, y0, z0), (c, y1, z1), tag="fin", name="fin_base" if k == 0 else "paddle")

    flipper_names = [f[0] for f in FLIPPERS]
    for nm in ("idle", "walk", "run", "sit"):
        m.anim(nm, SWIM[nm][0], True, marine.swim(names + ["fluke"], flipper_names, *SWIM[nm]))
    for a in m.animations:
        for tr in a["bones"].values():
            if "position" in tr:
                tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    idle = next(a for a in m.animations if a["name"].endswith(".idle"))
    low = min(lowest_point(m, idle["bones"], idle["length"] * f / 8) for f in range(9))
    lift(m, round(-low, 2))      # resting on the ground (beached / stranded): the lowest fin tip just touches it
    attack(m)
    add_knockout(m, roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-8)
    for nm in ("attack", "eat", "beg", "tame"):
        fit_to_ground(m, nm, ("neck",))
    return m
