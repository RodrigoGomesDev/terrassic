"""
Mosasaurus hoffmannii  (Maastrichtian; the seas of Europe and North America)

Reference:
  - Size (Grigoriev 2014; Street & Caldwell 2017): commonly 11-13 m, the largest jaws (~1.7 m) point to ~17 m.
    Not a dinosaur: a marine squamate, related to monitor lizards and snakes.
  - Skull (Lingham-Soliar 1995; Street & Caldwell 2017): massive, ~10% of the body length; a short blunt rostrum
    barely projecting in front of the teeth; the nostrils set far back on the snout; big orbits with sclerotic
    rings; large conical, slightly recurved teeth (~13-14 per side in the upper jaw), with a second set on the
    pterygoids in the roof of the mouth; an intramandibular joint and an expandable throat.
  - Body: deep barrel-shaped trunk, short neck; four paddles (the front pair bigger, many phalanges); the tail
    ~half the length ending in a crescent fluke whose lower lobe holds the bent-down vertebrae (hypocercal tail:
    Lindgren et al. 2013, Prognathodon). No dorsal frill or crest (an old error).
  - Skin (Lindgren et al. 2009, 2014): tiny keeled diamond scales; melanin points to a dark back and a pale belly
    (countershading).

v2x (2026-10-24, remaster at the T. rex v3 level): its own model (no longer the marine archetype geometry; only
its swimming wave and knockout), modelled at ~16 px = 1 m (one texture pixel = one vanilla pixel in game). The
head is ~1.1x the real proportion; lips cover the teeth (monitor lizard like) and the biggest crowns show their
tips. The animation position keys are scaled from the old ~7.2 px/m model.
"""
import math
from rig import Model, track, keys, add_knockout
import marine
from groundfit import fit_to_ground

ID = "mosasaurus"
K = 2.2          # 16 px/m now / ~7.2 px/m of the old model: scales the shared animations' position keys
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (16, 0)
# the trunk as a spindle of sections (z0, z1, half width, y0, y1), each with a narrower cap above and below
TORSO = [(-54, -42, 9, 6, 27), (-42, -28, 11, 4, 29), (-28, -12, 13, 2, 31), (-12, 4, 12, 2, 31),
         (4, 18, 11, 4, 29), (18, 30, 9, 6, 27)]
NECK = ([(17, -52), (17.5, -60), (18, -66)], [(18, 20), (16, 18)])
TAIL = ([(17, 28), (17.5, 50), (17.5, 72), (17.5, 92), (17.5, 110), (17, 126), (16, 140)],
        [(18, 22), (14, 20), (11, 17), (8, 15), (6, 12), (4, 10)])
FLUKE = {"lower": (30, 12, 30, 8, 12), "upper": (-36, 10, 22, 6, 10)}   # pitch, height, length, tip height, tip length
# flippers (left): pivot, rotation, then the parts (x0, x1, y0, y1, z0, z1): base, paddle, tip
FLIPPERS = [("flipper_front", (11, 9, -40), (0, -30, -20),
             [(10, 16, 7, 10, -44, -36), (16, 30, 7.5, 9.5, -45, -35), (30, 36, 7.5, 9.5, -43, -37)]),
            ("flipper_back", (9, 8, 18), (0, -35, -20),
             [(8, 13, 6.5, 8.5, 14, 21), (13, 23, 7, 9, 13, 21), (23, 27, 7, 9, 15, 20)])]


def pattern(model, tx, rgb, region):
    """Countershaded: slate back, grey flanks with faint mottling, pale belly; tiny keeled scales; dark paddles with
    a paler trailing edge; a few old pale scars on the flanks."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("tooth_cube", "eye", "mouth", "tongue"):
        return rgb
    if tag == "fin":
        col = pal["fin"].copy()
        if tx.edge:
            col = pal["fin_edge"].copy()
        return col * (0.94 if (tx.i + 2 * tx.j) % 3 == 0 else 1.0)
    if tag == "skin":
        if (tx.i + tx.j) % 2 == 0:
            rgb = rgb * 0.95                                                  # keeled scales
        if region == "dorsal" and math.sin(P[2] * 0.45 + 1.7 * math.sin(P[0] * 0.4)) > 0.7:
            rgb = rgb * 0.86                                                  # mottling
        if region == "flank" and abs(math.sin(P[2] * 0.19 + P[1] * 0.1)) > 0.992:
            rgb = pal["scar"].copy()                                          # old scars from fights
    return rgb


PALETTE = {"dorsal": "#2e3a44", "flank": "#566670", "belly": "#d8dbd0", "limb": "#34424c", "limb_top": "#3e4c56",
           "fin": "#26323a", "fin_edge": "#56666e", "tooth": "#efe9d6", "mouth": "#8a3a36", "gum": "#5e2623",
           "tongue": "#9a4a48", "tooth_cube_base": "#cfc6aa", "tooth_cube_tip": "#f3eddd",
           "eye": "#c8b04a", "pupil": "#0f0c0a", "scar": "#7c8a90"}
SEXES = {"male": {}, "female": {"dorsal": "#36424a", "flank": "#5e6c72"}}


def attack(m):
    # bite: head pulls back, jaw opens wide, snaps shut
    m.anim("attack", 0.7, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.2, -10, 0, 0), (0.38, 8, 0, 0), (0.7, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -36, 0, 0), (0.34, -38, 0, 0), (0.4, 0, 0, 0), (0.7, 0, 0, 0)])),
        "body": track(pos=keys([(0, 0, 0, 0), (0.2, 0, 0, 2 * K), (0.38, 0, 0, -3 * K), (0.7, 0, 0, 0)])),
    })


# knocked out: rolled onto its side, flippers swept back along the flanks, the tail in a lazy curve on the ground
LIMP = {"neck1": (3, -4, 0), "skull": (2, 0, 0), "jaw": (-14, 0, 0),
        "tail1": (-3, 0, 0), "tail2": (-4, 0, 0), "tail3": (-5, 0, 0), "tail4": (-5, 0, 0), "tail5": (-4, 0, 0),
        "tail6": (-4, 0, 0),
        "flipper_front_l": (0, -60, 20), "flipper_front_r": (0, 60, -20),
        "flipper_back_l": (0, -60, 20), "flipper_back_r": (0, 60, -20)}
LIFT = 11        # px: the hypocercal fluke reaches below the belly, so the whole model rides this much higher


def lift(m, dy):
    for b in m.bones[1:]:
        b.pivot[1] += dy
    for c in m.cubes:
        c.frm[1] += dy
        c.to[1] += dy
        c.origin[1] += dy
    m.decals = [dict(d, pos=(d["pos"][0], d["pos"][1] + dy, d["pos"][2])) for d in m.decals]


SWIM = dict(idle=(4.0, 5, 6, 2.0), walk=(2.0, 10, 10), run=(1.0, 13, 12, 4.0), sit=(4.0, 3, 4, 1.0))


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for k, (z0, z1, hw, y0, y1) in enumerate(TORSO):
        name = ("chest", "chest", "torso", "torso", "abdomen", "abdomen")[k]
        m.box("body", (-hw, y0, z0), (hw, y1, z1), name=name)
        m.box("body", (-(hw - 3), y1, z0 + 1), (hw - 3, y1 + 1, z1 - 1), name="back")
        m.box("body", (-(hw - 3), y0 - 1, z0 + 1), (hw - 3, y0, z1 - 1), name="belly")

    # --- neck: short and thick
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 4, az + 1))

    def S(name, box, tag="skin", bone="skull", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    def SM(name, box, tag="skin", bone="skull", **kw):
        x0, y0, z0, x1, y1, z1 = box
        for s in (1, -1):
            a, b = sorted((x0 * s, x1 * s))
            m.box(bone, (a, ay + y0, az + z0), (b, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- skull (head px): temporal block, big orbits, a long tapering snout, the short blunt rostrum
    S("temporal", (-9, -4, -10, 9, 7, 2), paint=MOUTH_DOWN)
    S("parietal", (-4, 7, -8, 4, 8, 1))
    S("orbit", (-8, -4, -16, 8, 6, -10), paint=MOUTH_DOWN)
    SM("brow", (5, 6, -16, 8, 7, -10))                                    # prefrontal / postorbital rim
    S("snout_mid", (-6.5, -4, -22, 6.5, 4, -16), paint=MOUTH_DOWN)
    S("snout", (-5, -4, -27, 5, 3, -22), paint=MOUTH_DOWN)
    S("premaxilla", (-3.5, -4, -30, 3.5, 2, -27), paint=MOUTH_DOWN)
    S("rostrum", (-2.5, -3, -31, 2.5, 1, -30))                            # barely projecting
    S("nasal_ridge", (-1.5, 4, -22, 1.5, 5, -12))
    # upper teeth on the outer edge of the upper jaw, the lower jaw fits inside; the lips leave the tips showing
    for s in (1, -1):
        for k, z in enumerate((-29, -26, -23, -20, -17, -14, -11)):
            half = 3.5 if z < -27 else 5 if z < -22 else 6.5 if z < -16 else 8
            L = 2 if k in (0, 6) else 3
            a, b = sorted((s * half, s * (half - 1)))
            S("fang", (a, -4 - L, z, b, -4, z + 1), tag="tooth_cube", paint={"axis": "-y"})
        for z in (-14, -11, -8):                                          # pterygoid teeth in the roof of the mouth
            a, b = sorted((s * 1.5, s * 2.5))
            S("fang", (a, -5, z, b, -4, z + 1), tag="tooth_cube", paint={"axis": "-y"})

    # --- lower jaw: slender in front, deep at the back, an expandable throat
    S("chin", (-2.5, -8, -30, 2.5, -4, -26), bone="jaw", paint=MOUTH_UP)
    S("jaw_front", (-4, -9, -26, 4, -4, -19), bone="jaw", paint=MOUTH_UP)
    S("jaw_mid", (-5.5, -10, -19, 5.5, -4, -11), bone="jaw", paint=MOUTH_UP)
    S("jaw_back", (-8, -11, -11, 8, -4, 2), bone="jaw", paint=MOUTH_UP)
    S("throat", (-6, -12, -14, 6, -11, 0), bone="jaw")
    S("tongue", (-2, -4, -24, 2, -3, -8), tag="tongue", bone="jaw")
    for s in (1, -1):
        for z in (-28, -24, -20, -16, -12):
            half = 2.5 if z < -26 else 4 if z < -19 else 5.5
            a, b = sorted((s * half, s * (half - 1)))
            S("fang_low", (a, -4, z, b, -2, z + 1), tag="tooth_cube", bone="jaw", paint={"axis": "+y"})

    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (8, ay + 2.5, az - 13), "r": 1.5, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-8, ay + 2.5, az - 13), "r": 1.5, "side": -1}]
    for s in (1, -1):                                                         # nostrils far back on the snout
        m.decals.append({"kind": "spot", "bones": ["skull"], "pos": (2.5 * s, ay + 4, az - 19), "r": 1.5, "rx": 0.6,
                         "mul": 0.4, "face": "up"})

    # --- tail: long, deepening sideways toward the end, the hypocercal fluke
    names = [f"tail{i + 1}" for i in range(len(TAIL[1]))]
    tail = m.chain(names, "body", 0, TAIL[0], "+z", TAIL[1], overlap=(1.0, 1.0))
    ey, ez = tail["end"]
    m.bone("fluke", names[-1], (0, ey, ez))
    for lobe, (pitch, h, L, th, tl) in FLUKE.items():
        org = (0, ey, ez - 2)
        m.box("fluke", (-1, ey - h / 2, ez - 2), (1, ey + h / 2, ez - 2 + L), name=f"fluke_{lobe}", tag="fin",
              rot=(pitch, 0, 0), origin=org)
        m.box("fluke", (-0.5, ey - th / 2, ez - 2 + L), (0.5, ey + th / 2, ez - 2 + L + tl), name=f"fluke_{lobe}_tip",
              tag="fin", rot=(pitch, 0, 0), origin=org)

    # --- paddles: a thick base, the broad paddle, a narrower tip
    for name, (px, py, pz), (rx, ry, rz), parts in FLIPPERS:
        for side, s in (("l", 1), ("r", -1)):
            b = f"{name}_{side}"
            m.bone(b, "body", (px * s, py, pz), (rx, ry * s, rz * s))
            for k, (x0, x1, y0, y1, z0, z1) in enumerate(parts):
                a, c = sorted((x0 * s, x1 * s))
                m.box(b, (a, y0, z0), (c, y1, z1), tag="fin" if k else "skin", name=("flipper_base", "paddle", "paddle_tip")[k])

    lift(m, LIFT)
    flipper_names = [f[0] for f in FLIPPERS]
    for nm in ("idle", "walk", "run", "sit"):
        m.anim(nm, SWIM[nm][0], True, marine.swim(names + ["fluke"], flipper_names, *SWIM[nm]))
    for a in m.animations:      # the swim wave's position keys were written for the old ~7.2 px/m model
        for bone, tr in a["bones"].items():
            if bone == "neck":
                a["bones"]["neck1"] = a["bones"].pop("neck")
                break
        for tr in a["bones"].values():
            if "position" in tr:
                tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    attack(m)
    add_knockout(m, roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-10)
    for nm in ("attack", "eat", "beg", "tame"):
        fit_to_ground(m, nm, ("neck1", "neck2", "skull"))
    return m
