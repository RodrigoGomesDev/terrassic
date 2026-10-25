"""
Tylosaurus proriger  (Late Cretaceous, Santonian-Campanian; Western Interior Seaway, Kansas)

Reference:
  - Size (Everhart 2005 "Oceans of Kansas"; Stewart & Mallon 2018): 12-13 m (the "Bunker" specimen KUVP 5033
    ~13 m); the top predator of the inland sea before the Mosasaurus.
  - Skull (Russell 1967; Lindgren et al. 2011): long and low, ~13% of the body length; the premaxilla ends in a long
    TOOTHLESS conical rostrum that projects well past the first teeth ("tylos" = knob), probably for ramming prey;
    teeth conical and smooth, smaller than the Mosasaurus'; a row of pterygoid teeth in the roof of the mouth;
    nostrils set back on the snout.
  - Body (Lindgren et al. 2011, 2013): slender and very long, a short neck, SMALL paddles; the tail close to half
    the total length, ending in a crescent fluke whose lower lobe holds the bent-down vertebrae (hypocercal).
  - Skin (Lindgren et al. 2014): tiny keeled scales, dark back over a pale belly (countershading). Stomach
    contents: plesiosaurs, sharks, fish, seabirds and even a small mosasaur.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the marine archetype geometry; only
its swimming wave and knockout), at ~16 px = 1 m like the Mosasaurus remaster, but slimmer, a long low head with
the rostrum, smaller teeth and paddles. The swim wave's position keys are scaled from the old ~10 px/m model.
Slate-blue with pale flank bars; males darker with sharper bars, females browner.
"""
import math
from rig import Model, track, keys, add_knockout, lowest_point
import marine
from groundfit import fit_to_ground

ID = "tylosaurus"
K = 1.58         # 16 px/m now / ~10.1 px/m of the old model: scales the shared animations' position keys
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (13, 0)
# the trunk as a spindle of sections (z0, z1, half width, y0, y1), each with a narrower cap above and below
TORSO = [(-36, -26, 7, 6, 20), (-26, -12, 8.5, 4, 22), (-12, 4, 9, 3, 23), (4, 18, 8.5, 4, 22), (18, 34, 7, 6, 20)]
NECK = ([(13, -35), (13.5, -41), (14, -48)], [(12, 13), (11, 12)])
TAIL = ([(13, 30), (13.5, 48), (13.5, 64), (13.5, 78), (13.5, 90), (13, 100), (12.5, 108)],
        [(12, 16), (10, 14), (8, 12), (6, 11), (5, 9), (4, 7)])
FLUKE = {"lower": (30, 10, 24, 6, 9), "upper": (-36, 8, 16, 5, 7)}    # pitch, height, length, tip height, tip length
# small paddles (left): pivot, rotation, then the parts (x0, x1, y0, y1, z0, z1): base, paddle, tip
FLIPPERS = [("flipper_front", (7, 7, -28), (0, -28, -18),
             [(6, 10, 5, 8, -31, -25), (10, 19, 5.5, 7.5, -32, -25), (19, 23, 5.5, 7.5, -31, -26)]),
            ("flipper_back", (6, 7, 24), (0, -32, -18),
             [(5, 9, 5, 7, 21, 26), (9, 15, 5.5, 6.5, 20, 26), (15, 18, 5.5, 6.5, 21, 25)])]


def pattern(model, tx, rgb, region):
    """Countershaded: slate back with dark mottling, pale vertical bars along the flanks, pale belly; tiny keeled
    scales; a scarred pale rostrum; dark paddles with a paler trailing edge."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("tooth_cube", "eye", "mouth", "tongue"):
        return rgb
    if tag == "fin":
        col = pal["fin_edge"].copy() if tx.edge else pal["fin"].copy()
        return col * (0.94 if (tx.i + 2 * tx.j) % 3 == 0 else 1.0)
    if tag == "rostrum":
        col = pal["rostrum"].copy()
        if math.sin(P[2] * 2.3 + P[1] * 1.1) > 0.6:
            col = col * 0.9                                                   # old scars from ramming
        return col
    if tag == "skin":
        if (tx.i + tx.j) % 2 == 0:
            rgb = rgb * 0.95                                                  # keeled scales
        if region == "flank" and cube.bone.startswith(("body", "tail")) \
                and math.sin(P[2] * 0.33 + 0.4 * math.sin(P[1] * 0.6)) > 0.6:
            rgb = pal["bar"].copy() * (0.96 if (tx.i + tx.j) % 2 else 1.0)    # pale vertical bars
        elif region == "dorsal" and math.sin(P[2] * 0.7 + P[0] * 0.6) * math.sin(P[0] * 1.1) > 0.6:
            rgb = rgb * 0.86                                                  # dark mottling on the back
    return rgb


PALETTE = {"dorsal": "#243038", "flank": "#4a5a62", "belly": "#cfd4cc", "bar": "#6e7e84",
           "limb": "#2c3840", "limb_top": "#36444c", "fin": "#1e2a30", "fin_edge": "#44545c", "rostrum": "#9aa09a",
           "tooth": "#efe9d6", "mouth": "#86363a", "gum": "#5a2426", "tongue": "#9a4a48",
           "tooth_cube_base": "#cfc6aa", "tooth_cube_tip": "#f3eddd", "eye": "#d8b85a", "pupil": "#0f0c0a"}
SEXES = {"male": {"dorsal": "#1c262e", "bar": "#7a8c92"},
         "female": {"dorsal": "#34403e", "flank": "#5a6660", "bar": "#747e74", "belly": "#d6d6c8"}}


def attack(m):
    # ram: the whole body lunges, the head drops so the rostrum leads, then a quick bite as it pulls back
    m.anim("attack", 0.8, False, {
        "body": track(pos=keys([(0, 0, 0, 0), (0.2, 0, 0, 3 * K), (0.4, 0, 0, -6 * K), (0.8, 0, 0, 0)]),
                      rot=keys([(0, 0, 0, 0), (0.2, -2, 0, 0), (0.4, 2, 0, 0), (0.8, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.2, -8, 0, 0), (0.4, 12, 0, 0), (0.6, -4, 0, 0), (0.8, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.4, 0, 0, 0), (0.55, -36, 0, 0), (0.65, -2, 0, 0), (0.8, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.2, 0, 14, 0), (0.4, 0, -12, 0), (0.8, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.25, 0, 18, 0), (0.45, 0, -16, 0), (0.8, 0, 0, 0)])),
    })


# knocked out: rolled onto its side, paddles swept back along the flanks, the tail in a lazy curve on the ground
LIMP = {"neck1": (3, -5, 0), "skull": (2, 0, 0), "jaw": (-14, 0, 0),
        "tail1": (-3, 0, 0), "tail2": (-4, 0, 0), "tail3": (-5, 0, 0), "tail4": (-6, 0, 0), "tail5": (-6, 0, 0),
        "tail6": (-5, 0, 0),
        "flipper_front_l": (0, -60, 20), "flipper_front_r": (0, 60, -20),
        "flipper_back_l": (0, -60, 20), "flipper_back_r": (0, 60, -20)}
SWIM = dict(idle=(3.6, 6, 6, 2.0), walk=(1.8, 12, 10), run=(0.9, 18, 12, 4.0), sit=(4.0, 4, 4, 1.0))


def lift(m, dy):
    for b in m.bones[1:]:
        b.pivot[1] += dy
    for c in m.cubes:
        c.frm[1] += dy
        c.to[1] += dy
        c.origin[1] += dy
    m.decals = [dict(d, pos=(d["pos"][0], d["pos"][1] + dy, d["pos"][2])) for d in m.decals]


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for k, (z0, z1, hw, y0, y1) in enumerate(TORSO):
        name = ("chest", "torso", "torso", "abdomen", "abdomen")[k]
        m.box("body", (-hw, y0, z0), (hw, y1, z1), name=name)
        m.box("body", (-(hw - 3), y1, z0 + 1), (hw - 3, y1 + 1, z1 - 1), name="back")
        m.box("body", (-(hw - 3), y0 - 1, z0 + 1), (hw - 3, y0, z1 - 1), name="belly")

    # --- neck: short
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 3, az + 1))

    def S(name, box, tag="skin", bone="skull", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    def SM(name, box, tag="skin", bone="skull", **kw):
        x0, y0, z0, x1, y1, z1 = box
        for s in (1, -1):
            a, b = sorted((x0 * s, x1 * s))
            m.box(bone, (a, ay + y0, az + z0), (b, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- skull (head px): long and low, the toothed snout, then the toothless rostrum well past the first teeth
    S("temporal", (-6, -3, -8, 6, 5, 2), paint=MOUTH_DOWN)
    S("parietal", (-3, 5, -6, 3, 6, 1))
    S("orbit", (-5.5, -3, -13, 5.5, 4, -8), paint=MOUTH_DOWN)
    SM("brow", (3.5, 4, -13, 5.5, 5, -8))                                   # prefrontal / postorbital rim
    S("snout_mid", (-4.5, -3, -20, 4.5, 3, -13), paint=MOUTH_DOWN)
    S("snout", (-3.5, -3, -26, 3.5, 2, -20), paint=MOUTH_DOWN)
    S("premaxilla", (-2.5, -3, -29, 2.5, 2, -26), paint=MOUTH_DOWN)
    S("rostrum", (-2, -2.5, -33, 2, 1.5, -29), tag="rostrum")
    S("rostrum_tip", (-1, -1.5, -35, 1, 0.5, -33), tag="rostrum")
    S("nasal_ridge", (-1, 3, -20, 1, 4, -10))
    # upper teeth on the outer edge of the upper jaw, the lower jaw fits inside; the lips leave the tips showing
    for s in (1, -1):
        for k, z in enumerate((-28, -25, -22, -19, -16, -13)):
            half = 2.5 if z < -26 else 3.5 if z < -20 else 4.5
            L = 2 if k in (0, 5) else 3
            a, b = sorted((s * half, s * (half - 1)))
            S("fang", (a, -3 - L, z, b, -3, z + 1), tag="tooth_cube", paint={"axis": "-y"})
        for z in (-12, -9, -6):                                           # pterygoid teeth in the roof of the mouth
            a, b = sorted((s * 1.5, s * 2.5))
            S("fang", (a, -4, z, b, -3, z + 1), tag="tooth_cube", paint={"axis": "-y"})

    # --- lower jaw: slender, deeper at the back, an expandable throat
    S("chin", (-2, -6, -30, 2, -3, -25), bone="jaw", paint=MOUTH_UP)
    S("jaw_front", (-3, -7, -25, 3, -3, -18), bone="jaw", paint=MOUTH_UP)
    S("jaw_mid", (-4, -7, -18, 4, -3, -10), bone="jaw", paint=MOUTH_UP)
    S("jaw_back", (-5, -8, -10, 5, -3, 2), bone="jaw", paint=MOUTH_UP)
    S("throat", (-4, -9, -13, 4, -8, 0), bone="jaw")
    S("tongue", (-1.5, -3, -23, 1.5, -2, -8), tag="tongue", bone="jaw")
    for s in (1, -1):
        for z in (-27, -23, -19, -15, -11):
            half = 2 if z < -25 else 3 if z < -17 else 4
            a, b = sorted((s * half, s * (half - 1)))
            S("fang_low", (a, -3, z, b, -1, z + 1), tag="tooth_cube", bone="jaw", paint={"axis": "+y"})

    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (5.5, ay + 1.5, az - 10.5), "r": 1.3, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-5.5, ay + 1.5, az - 10.5), "r": 1.3, "side": -1}]
    for s in (1, -1):                                                         # nostrils set back on the snout
        m.decals.append({"kind": "spot", "bones": ["skull"], "pos": (2 * s, ay + 3, az - 18), "r": 1.3, "rx": 0.6,
                         "mul": 0.4, "face": "up"})

    # --- tail: about half the animal, the hypocercal fluke
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

    # --- small paddles: a thick base, the paddle, a narrower tip
    for name, (px, py, pz), (rx, ry, rz), parts in FLIPPERS:
        for side, s in (("l", 1), ("r", -1)):
            b = f"{name}_{side}"
            m.bone(b, "body", (px * s, py, pz), (rx, ry * s, rz * s))
            for k, (x0, x1, y0, y1, z0, z1) in enumerate(parts):
                a, c = sorted((x0 * s, x1 * s))
                m.box(b, (a, y0, z0), (c, y1, z1), tag="fin" if k else "skin", name=("flipper_base", "paddle", "paddle_tip")[k])

    flipper_names = [f[0] for f in FLIPPERS]
    for nm in ("idle", "walk", "run", "sit"):
        m.anim(nm, SWIM[nm][0], True, marine.swim(names + ["fluke"], flipper_names, *SWIM[nm]))
    for a in m.animations:      # the swim wave's position keys were written for the old ~10 px/m model
        if "neck" in a["bones"]:
            a["bones"]["neck1"] = a["bones"].pop("neck")
        for tr in a["bones"].values():
            if "position" in tr:
                tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    low = min(lowest_point(m, a["bones"], a.get("length", 1) * f / 8) for a in m.animations for f in range(9))
    lift(m, math.ceil(-low) if low < 0 else 0)   # the lower fluke lobe reaches below the belly: ride higher
    attack(m)
    add_knockout(m, roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-10)
    for nm in ("attack", "eat", "beg", "tame"):
        fit_to_ground(m, nm, ("neck1", "neck2", "skull"))
    return m
