"""
Elasmosaurus platyurus  (Late Cretaceous, Campanian; Western Interior Seaway, Kansas)

Reference:
  - Size (Cope 1868; Sachs 2005; Sachs, Kear & Everhart 2013, the redescription of the holotype): ~10.3 m, of
    which the neck is ~7 m with 72 vertebrae (the longest neck of any animal relative to the body). Cope famously
    mounted the skull on the tail by mistake.
  - Head small (~3-4% of the length): a flat triangular skull, big eyes looking up and forward, long slender
    interlocking fangs in front (fish trap), shorter teeth behind; nostrils set back near the eyes.
  - Body: a stiff, broad and flattened barrel braced by a plate of belly ribs (gastralia); four long, narrow,
    pointed hydrofoil paddles of nearly equal size that "flew" under water; a short tail, probably with a small
    vertical fin at the end (as in Seeleyosaurus). Gave birth to live young (Polycotylus, O'Keefe & Chiappe 2011).
  - Colour unknown; the model keeps the old scheme: dark teal above, pale below, leopard-like spots on the back
    and neck; males darker with pale throat bands, females browner.

v2x (2026-10-25, remaster at the T. rex v3 level): modelled at ~16 px = 1 m (one texture pixel = one vanilla pixel
in game), a neck of 14 short segments tapering from the shoulders to the head, the head ~1.4x the real
proportion. Built on the plesiosaur archetype (species/plesiosaur.py) for the neck chain, the swim and the
knockout; the paddles get a tapering hydrofoil and the body a real barrel. The archetype's position keys are
scaled by K, and the per-segment neck angles divided over the extra segments.
"""
import math
from rig import track, keys, add_knockout
from groundfit import fit_to_ground
import plesiosaur

ID = "elasmosaurus"
K = 1.42                     # 16 px/m now / ~11.3 px/m of the old model
NECK_N = 14
NK = 8.0 / NECK_N            # the old 8-segment neck angles, spread over 14 segments
BODY_Y = 12
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}


def _neck():
    pts, secs = [], []
    for i in range(NECK_N + 1):
        f = i / NECK_N
        pts.append((round(13 + 7 * f ** 1.4, 2), -22 - 9 * i))         # carried out level, rising gently
    for i in range(NECK_N):
        f = i / (NECK_N - 1)
        w = int(round(12 - 7 * f ** 0.8))
        secs.append((w, w))
    return pts, secs


def body_parts(m):
    # broad, flattened barrel trunk, a plate of belly ribs, the shoulder and hip girdles where the paddles attach
    m.box("body", (-11, 5, -18), (11, 19, 14), name="torso")
    m.box("body", (-9, 6, -24), (9, 18, -18), name="chest")
    m.box("body", (-8, 7, 14), (8, 17, 20), name="hips")
    m.box("body", (-8, 19, -16), (8, 20, 12), name="back")
    m.box("body", (-9, 4, -16), (9, 5, 12), name="gastralia")
    m.box("body", (-7, 6, -27), (7, 17, -24), name="neck_base")


def head(m, ay, az, abs_pitch):
    m.bone("skull", "head", (0, ay, az), (-abs_pitch, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # small flat skull: a broad back with the eyes high, a slim snout, interlocking needle fangs
    m.box("skull", *R(-3, -2, -4, 3, 2, 1), name="cranium", paint=MOUTH_DOWN)
    m.box("skull", *R(-0.5, 2, -3, 0.5, 3, 1), name="parietal_crest")
    m.box("skull", *R(-2, -2, -9, 2, 1, -4), name="snout", paint=MOUTH_DOWN)
    m.box("skull", *R(-1.5, -2, -11, 1.5, 0, -9), name="snout_tip", paint=MOUTH_DOWN)
    # the lower jaw is narrower and fits inside the upper one; its teeth a painted row along the edge
    m.bone("jaw", "skull", (0, ay - 2, az - 2))
    m.box("jaw", *R(-2, -3, -4, 2, -2, 1), name="jaw_back", paint=MOUTH_UP)
    m.box("jaw", *R(-1, -3, -9, 1, -2, -4), name="jaw", paint=dict(MOUTH_UP, teeth={"edge": "top", "rows": 1, "faces": ("east", "west"), "freq": 1.0}))
    m.box("jaw", *R(-0.5, -3, -11, 0.5, -2, -9), name="jaw_tip", paint=dict(MOUTH_UP, teeth={"edge": "top", "rows": 1, "faces": ("east", "west"), "freq": 1.0}))
    for s in (1, -1):
        for z, half, L in ((-11, 1.5, 2), (-9, 2, 2), (-7, 2, 1)):             # upper fangs on the jaw margin
            a, b = sorted((s * half, s * (half - 1)))
            m.box("skull", *R(a, -2 - L, z, b, -2, z + 1), name="fang", tag="tooth_cube", paint={"axis": "-y"})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3, ay + 0.8, az - 2.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 0.8, az - 2.0), "r": 1.0, "side": -1},
    ]
    for s in (1, -1):                                                       # nostrils just ahead of the eyes
        m.decals.append({"kind": "spot", "bones": ["skull"], "pos": (0.8 * s, ay + 1, az - 5), "r": 0.6,
                         "mul": 0.45, "face": "up"})


# extra paddle parts (left side, model coordinates): the archetype makes the root box; these taper it into a
# long narrow pointed hydrofoil, thinner toward the tip, the trailing edge swept back
PADDLE = {"flipper_front": [(14, 28, 8.5, 10.5, -17, -7), (28, 36, 9, 10, -15, -8), (36, 41, 9, 10, -13, -9),
                            (41, 44, 9, 10, -12, -10)],
          "flipper_back": [(13, 25, 8.5, 10.5, 6, 15), (25, 32, 9, 10, 7, 14), (32, 36, 9, 10, 8, 13),
                           (36, 38, 9, 10, 9, 12)]}


def after(m):
    for name, parts in PADDLE.items():
        for side, s in (("l", 1), ("r", -1)):
            for x0, x1, y0, y1, z0, z1 in parts:
                a, b = sorted((x0 * s, x1 * s))
                m.box(f"{name}_{side}", (a, y0, z0), (b, y1, z1), tag="fin", name="paddle")


def pattern(model, tx, rgb, region):
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("tooth_cube", "eye", "mouth"):
        return rgb
    if tag == "fin":
        col = pal["fin_edge"].copy() if tx.edge else pal["fin"].copy()
        if tx.face == "up" and P[2] < cube.frm[2] + 1.01:
            col = pal["fin_edge"].copy()                                   # pale leading edge on the paddles
        return col * (0.94 if (tx.i + 2 * tx.j) % 3 == 0 else 1.0)
    if tag == "skin":
        if (tx.i + tx.j) % 2 == 0:
            rgb = rgb * 0.96                                               # fine scales
        if region in ("dorsal", "flank") and math.sin(P[0] * 0.9 + P[2] * 0.2) * math.sin(P[2] * 0.75 + P[1] * 0.45) > 0.62:
            return pal["spot"].copy()                                      # leopard spots over the back and neck
        if region == "belly" and cube.bone.startswith("neck") and math.sin(P[2] * 1.0) > 0.7:
            return pal["throat"].copy()                                    # throat bands (strong on males)
    return rgb


def attack(m, necks):
    # the neck coils back, then whips forward and the jaws snap on the fish
    n = len(necks)
    t = {"body": track(pos=keys([(0, 0, 0, 0), (0.25, 0, 0, 2 * K), (0.45, 0, 0, -3 * K), (0.8, 0, 0, 0)]))}
    for i, b in enumerate(necks):
        coil = (8.0 if i < n // 2 else -10.0) * NK
        strike = (-2.0 if i < n // 2 else 3.0) * NK
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.25, coil, 0, 0), (0.45, strike, 0, 0), (0.8, 0, 0, 0)]))
    t["skull"] = track(rot=keys([(0, 0, 0, 0), (0.25, 14, 0, 0), (0.45, -10, 0, 0), (0.8, 0, 0, 0)]))
    t["jaw"] = track(rot=keys([(0, 0, 0, 0), (0.25, -30, 0, 0), (0.42, -34, 0, 0), (0.5, 0, 0, 0), (0.8, 0, 0, 0)]))
    m.anim("attack", 0.8, False, t)


# knocked out: on its side, the long neck laid along the ground in a curve, paddles swept back along the body
LIMP = {"skull": (4, 0, 0), "jaw": (-12, 0, 0), "tail1": (-4, 0, 0), "tail2": (-6, 0, 0), "tail3": (-6, 0, 0),
        "flipper_front_l": (-70, -60, 14), "flipper_front_r": (0, 60, -14),
        "flipper_back_l": (-70, -55, 14), "flipper_back_r": (0, 55, -14)}
for _i in range(NECK_N):
    LIMP[f"neck{_i + 1}"] = ((3.0 + 1.5 * _i * NK) * NK, 0, 0)

_pts, _secs = _neck()
SPEC = dict(
    render_scale=0.5,
    palette={"dorsal": "#2a4a4a", "flank": "#5a7a76", "belly": "#dfe3d8", "spot": "#1c3232", "throat": "#eef0e4",
             "limb": "#2e4a48", "limb_top": "#3a5856", "fin": "#1e3a3a", "fin_edge": "#55746e",
             "tooth": "#f2eee0", "mouth": "#8a4048", "gum": "#5a2a30",
             "tooth_cube_base": "#d6cfb8", "tooth_cube_tip": "#f6f2e6", "eye": "#d8c060", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#223e40", "spot": "#142626", "throat": "#f4f4ea"},
           "female": {"dorsal": "#3c4e44", "flank": "#6a7e6e", "spot": "#2a3a30", "throat": "#dfe3d8"}},
    pattern=pattern, body=(BODY_Y, 0), body_parts=body_parts, head=head,
    neck=dict(points=_pts, sections=_secs),
    tail=dict(points=[(12, 18), (11.5, 24), (11, 30), (10.5, 35)], sections=[(9, 8), (6, 6), (4, 4)], tip=(1, 6, 5)),
    flippers=[dict(name="flipper_front", pivot=(10, 9, -12), rot=(0, -20, -15), span=(9, 14), y=(8, 11), z=(-16, -7)),
              dict(name="flipper_back", pivot=(9, 9, 10), rot=(0, -25, -15), span=(8, 13), y=(8, 11), z=(6, 15))],
    swim=dict(idle=(3.6, 10, 2.0 * NK), walk=(1.8, 22, 3.0 * NK), run=(1.0, 30, 4.0 * NK), sit=(4.0, 5, 1.5 * NK)),
    attack=attack,
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-12),
)


def build():
    m = plesiosaur.build(ID, SPEC)
    after(m)
    # redo the knockout set now that the paddles are full length (the archetype grounded the short root boxes)
    m.animations = [a for a in m.animations
                    if a["name"].split(".")[-1] not in ("knocked_out", "wake", "eat", "beg", "tame")]
    ko = SPEC["ko"]
    add_knockout(m, roll=ko["roll"], lift=ko["lift"], shift=ko["shift"], joints=ko["joints"], neck_down=ko["neck_down"])
    for a in m.animations:      # the archetype's swim was written for the old ~11 px/m model
        if a["name"].split(".")[-1] in ("idle", "walk", "run", "sit", "eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    for nm in ("attack", "eat", "beg", "tame"):
        fit_to_ground(m, nm, tuple(f"neck{i + 1}" for i in range(NECK_N)) + ("skull",))
    return m
