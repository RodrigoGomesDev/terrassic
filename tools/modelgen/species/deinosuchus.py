"""
Deinosuchus riograndensis  (Late Cretaceous, Campanian; both coasts of the Western Interior Seaway)

Reference:
  - Size (Schwimmer 2002; Cossette & Brochu 2020): an alligatoroid of ~10.6 m for the largest well-measured
    D. riograndensis (older estimates up to 12 m) and several tonnes. Bite marks on tyrannosaur and turtle bones.
  - Skull (Cossette & Brochu 2020): long (~1.5 m), broad and flat, with an enlarged, bulbous tip to the snout around a
    big nasal opening (unlike any living crocodilian), a narrowing just behind it, the eyes raised on bosses at the
    back of the skull table; the lower teeth close inside the upper row (alligator overbite), thick blunt teeth at
    the back for crushing turtles.
  - Body: a broad flat barrel armoured by heavy, pitted osteoderms in paired rows down the back (big, nearly
    round in this genus); sprawling limbs used in the "high walk"; a long deep tail with a double crest of scutes
    that merges into one towards the tip. An ambusher at the water's edge, like a living alligator.
  - Colour unknown; kept from the old model: dark olive-green with black cross bands over a buff belly; males
    darker and greener, females browner with a paler throat.

v2x (2026-10-25, remaster at the T. rex v3 level): modelled at ~16 px = 1 m, built on the crocodylomorph archetype
(species/croc.py) for the legs and the animation set; the archetype's position keys are scaled by K. Each
osteoderm is its own cube.
"""
import math
from rig import track, keys
from groundfit import fit_to_ground
import croc

ID = "deinosuchus"
K = 1.64                 # 16 px/m now / ~9.75 px/m of the old model
BODY_Y = 14
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
TORSO = [(-26, -14, 10.5, 8, 20), (-14, 16, 12, 7, 21), (16, 30, 10.5, 8, 20)]     # (z0, z1, half width, y0, y1)
TAIL = ([(14, 30), (14, 46), (13.5, 62), (12.5, 78), (11, 92), (9.5, 105), (8, 118)],
        [(18, 13), (14, 11), (11, 9), (8, 7), (6, 5), (4, 4)])
# osteoderm rows on the back of each torso section: (x centre, width, height); one cube every 4 px, 3 px long,
# set half a pixel into the skin
SCUTE_ROWS = [(2.5, 3, 2), (6.5, 3, 1), (10, 2, 1)]


def body_parts(m):
    for z0, z1, hw, y0, y1 in TORSO:
        m.box("body", (-hw, y0, z0), (hw, y1, z1), name="torso")
    m.box("body", (-10, 6, -22), (10, 7, 26), name="belly")
    for z0, z1, hw, y0, y1 in TORSO:
        for xc, w, h in SCUTE_ROWS:
            if xc + w / 2 > hw - 0.5:
                continue
            for s in (1, -1):
                for z in range(z0 + 1, z1 - 2, 4):
                    a, b = sorted((s * (xc - w / 2), s * (xc + w / 2)))
                    m.box("body", (a, y1 - 0.5, z), (b, y1 - 0.5 + h, z + 3), name="osteoderm", tag="scute")


def head(m, ay, az, abs_pitch):
    m.bone("skull", "head", (0, ay, az), (-abs_pitch, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)

    def RM(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        for s in (1, -1):
            a, b = sorted((x0 * s, x1 * s))
            m.box(bone, *R(a, y0, z0, b, y1, z1), name=name, tag=tag, **kw)
    # broad flat alligator skull: the skull table with raised eye bosses, a long snout that narrows, then the
    # bulbous tip around the big nasal opening
    m.box("skull", *R(-8, -3, -8, 8, 3, 0), name="cranium", paint=MOUTH_DOWN)
    m.box("skull", *R(-5, 3, -7, 5, 4, 0), name="skull_table")
    RM("skull", "eye_boss", (4, 3, -6, 7, 5, -2), tag="scute")
    m.box("skull", *R(-6, -3, -14, 6, 2, -8), name="snout_rear", paint=MOUTH_DOWN)
    m.box("skull", *R(-5, -3, -20, 5, 1, -14), name="snout", paint=MOUTH_DOWN)
    m.box("skull", *R(-4, -3, -23, 4, 1, -20), name="snout_neck", paint=MOUTH_DOWN)
    m.box("skull", *R(-5, -3, -27, 5, 2, -23), name="bulla", paint=MOUTH_DOWN)
    m.box("skull", *R(-1.5, 2, -26, 1.5, 3, -24), name="narial_boss")
    # lower jaw: narrower, closing inside the upper teeth
    m.bone("jaw", "skull", (0, ay - 3, az - 1))
    LT = dict(MOUTH_UP, teeth={"edge": "top", "rows": 1, "faces": ("east", "west"), "freq": 0.9})
    m.box("jaw", *R(-7, -6, -8, 7, -3, 1), name="jaw_back", paint=MOUTH_UP)
    m.box("jaw", *R(-5.5, -6, -14, 5.5, -3, -8), name="jaw_rear", paint=LT)
    m.box("jaw", *R(-4.5, -5, -20, 4.5, -3, -14), name="jaw", paint=LT)
    m.box("jaw", *R(-3.5, -5, -23, 3.5, -3, -20), name="jaw_front", paint=LT)
    m.box("jaw", *R(-4.5, -5, -27, 4.5, -3, -23), name="chin", paint=LT)
    # upper teeth overlapping the lower jaw: long fangs in the bulla, thick blunt crushers at the back
    for z, jh, L in ((-26, 4.5, 2), (-24, 4.5, 2), (-19, 4.5, 2), (-16, 4.5, 2), (-12, 5.5, 1), (-10, 5.5, 1)):
        for s in (1, -1):
            a, b = sorted((s * jh, s * (jh + 1)))
            m.box("skull", *R(a, -3 - L, z, b, -3, z + 1), name="fang", tag="tooth_cube", paint={"axis": "-y"})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (5.5, ay + 5, az - 4.0), "r": 1.3, "side": 1, "up": True},
        {"kind": "eye", "bones": ["skull"], "pos": (-5.5, ay + 5, az - 4.0), "r": 1.3, "side": -1, "up": True},
    ]
    for s in (1, -1):
        m.decals.append({"kind": "spot", "bones": ["skull"], "pos": (0.7 * s, ay + 3, az - 25), "r": 0.6,
                         "mul": 0.35, "face": "up"})                         # the nostrils on the bulla


def tail_crest(m):
    """Paired crest scutes on the first tail segments, merging into a single row towards the tip. Coordinates are the
    chain's unposed frame: the segments laid straight along +z from the first joint."""
    pts, secs = TAIL
    cz = pts[0][1]
    for k in range(len(secs)):
        (ya, za), (yb, zb) = pts[k], pts[k + 1]
        L = math.hypot(yb - ya, zb - za)
        y = pts[0][0] + secs[k][1] / 2 - (1 if k < 3 else 0.5)
        ht = 3 if k < 3 else 2
        for z in range(int(cz) + 1, int(cz + L) - 2, 4):
            for xc in ((2.5, -2.5) if k < 3 else (0.0,)):
                m.box(f"tail{k + 1}", (xc - 1, y, z), (xc + 1, y + ht, z + 3), name="crest", tag="scute")
        cz += L


def pattern(model, tx, rgb, region):
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("tooth_cube", "eye", "mouth", "claw"):
        return rgb
    if tag == "scute":
        col = pal["scute"].copy()
        if tx.face == "up":
            col = col * (1.12 if (int(P[0] * 2) + int(P[2] * 2)) % 3 else 0.9)   # pitted, keeled osteoderms
        if tx.edge:
            col = col * 0.82
        return col
    if tag == "skin":
        band = math.sin(P[2] * 0.36 + P[0] * 0.1)
        if region == "dorsal" and band > 0.45:
            rgb = pal["band"].copy()                       # alligator cross bands over the back and tail
        elif region == "flank" and band > 0.75:
            rgb = rgb * 0.8
        elif region == "belly":
            if (int(math.floor(P[2] * 0.5)) + int(math.floor(P[0] * 0.5))) % 2 == 0:
                rgb = rgb * 0.93                           # square belly scales
            if cube.bone.startswith("neck") or cube.bone in ("skull", "jaw"):
                rgb = pal["throat"].copy()
        if region in ("dorsal", "flank") and (int(math.floor(P[2] * 0.6)) + int(math.floor(P[1] * 0.6))) % 2 == 0:
            rgb = rgb * 0.95                               # scale rows
        if cube.bone == "skull" and tx.face == "up" and (int(P[0]) * 7 + int(P[2]) * 3) % 5 == 0:
            rgb = rgb * 0.88                               # rough, pitted skull roof
    elif tag == "limb":
        if (int(math.floor(P[1] * 0.7)) + int(math.floor(P[0] * 0.7))) % 2 == 0:
            rgb = rgb * 0.94
    return rgb


# knocked out on its side: jaws slack, legs limp, the tail curving on the ground
LIMP = {"neck1": (-6, 0, 0), "skull": (-2, 0, 0), "jaw": (-16, 0, 0),
        "tail1": (-4, 0, 0), "tail2": (-5, 0, 0), "tail3": (-5, 0, 0), "tail4": (-5, 0, 0), "tail5": (-4, 0, 0),
        "tail6": (-4, 0, 0),
        "upperarm_l": (10, 0, -60), "upperarm_r": (18, 0, 60), "forearm_l": (0, 0, -30), "forearm_r": (0, 0, -80),
        "thigh_l": (-8, 0, -60), "thigh_r": (-16, 0, 60), "shin_l": (0, 0, -30), "shin_r": (0, 0, -80)}

SPEC = dict(
    render_scale=0.5,
    palette={"dorsal": "#3a4a2c", "flank": "#5c6a40", "belly": "#c8bc84", "band": "#1e2616", "throat": "#d8d0a0",
             "scute": "#2c3820", "limb": "#4a5636", "limb_top": "#5c6a40",
             "claw": "#3a3228", "claw_base": "#4a4234", "claw_tip": "#2a241c",
             "tooth": "#efe8d2", "mouth": "#8a3844", "gum": "#4a3a2c",
             "tooth_cube_base": "#d8ceb0", "tooth_cube_tip": "#f2ecd8", "eye": "#c8a040", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#2e4026", "flank": "#4e5e38", "band": "#141c10", "scute": "#222e18"},
           "female": {"dorsal": "#4a4e30", "flank": "#6a6c46", "band": "#2a2a18", "throat": "#e4dcb0"}},
    pattern=pattern, body=(BODY_Y, 0), body_parts=body_parts, head=head,
    neck=dict(points=[(14, -25), (14, -36)], sections=[(16, 12)]),
    tail=dict(points=TAIL[0], sections=TAIL[1], crest=[]),
    legs=dict(front=dict(pivot=(11, 11, -18), upper=(10, 7, 7), sprawl=30, lower=(4, 6, 6), foot=(11, 9, 2, 3)),
              hind=dict(pivot=(11, 11, 20), upper=(10, 9, 9), sprawl=30, lower=(4, 7, 7), foot=(12, 11, 2, 3))),
    gait=dict(walk=(1.6, 18, 0.5, 4), run=(0.8, 26, 1.2, 6)),
    sit=dict(drop=7, upper=0, lower=0, lower_roll=-55, neck=-2, tail=-1),
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-6),
)


def build():
    m = croc.build(ID, SPEC)
    tail_crest(m)
    for a in m.animations:      # the archetype's moving poses were written for the old ~9.75 px/m model
        if a["name"].split(".")[-1] in ("idle", "walk", "run", "attack", "eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    for nm in ("attack", "eat"):
        fit_to_ground(m, nm, ("neck1", "skull"))
    return m
