"""
Quetzalcoatlus northropi  (Maastrichtian, Javelina Formation, Texas)

Reference:
  - Size (Lawson 1975; Witton & Naish 2008; Andres & Langston 2021): wingspan 10-11 m, standing ~5 m tall (as tall
    as a giraffe), ~200-250 kg. Known from a huge wing; the skull and neck come from the smaller Q. lawsoni
    (~4.5 m span) found nearby, scaled up.
  - Skull (Andres & Langston 2021, Q. lawsoni): very long (~2.5 m scaled to northropi), toothless, the upper beak
    a long tapering spear with a huge nasoantorbital opening and a low rounded crest over it; the eye small and set
    far back.
  - Neck (~3 m): few, extremely elongate tube-like cervicals, stiff and held up; a small torso with a notarium;
    long forelimbs with an unusually long metacarpal, so on the ground it stood tall on all fours, walking on the
    three small fingers with the wing finger folded up (Haenamichnus trackways), and stalked small prey like a giant
    stork ("terrestrial stalker", Witton & Naish 2008). Long narrow soaring wings.
  - Body and neck covered in short pycnofibres (hair-like fuzz); legs long with plantigrade, padded four-toed feet.

v2x (2026-10-24, remaster at the T. rex v3 level): modelled at twice the old resolution (~22 px = 1 m), with the
details above. Built on the pterosaur archetype (species/pterosaur.py): wing bones, folding and the animation
set; the archetype's position keys are scaled by K. Males: taller crest and a redder face.
"""
import math
from groundfit import fit_to_ground
from rig import track, keys, add_saddle, lowest_point
import pterosaur

ID = "quetzalcoatlus"
K = 2.0
SHOULDER = (8, 66, -6)
BODY_Y = 62
W1, W2, W3 = 28, 40, 44          # arm, metacarpal IV (the long "front leg" on the ground), wing finger
CHORD = (18, 14, 10, 4)
TH = 1.5                         # half thickness of the arm and hand bones: slender azhdarchid wings
# low rounded crest over the nasoantorbital opening as columns (z0, z1, top y) in head px; male columns +2
CREST = [(-30, -26, 6), (-26, -22, 7), (-22, -16, 8), (-16, -10, 8), (-10, -6, 7)]
MALE_CREST = {(-26, -22), (-22, -16), (-16, -10)}
SIT_SPLAY = (30, -60)      # resting: thigh and shin roll out (deg)


def _fuzz(tx, rgb, k=0.12):
    """Pycnofibres: short streaks of lighter and darker hair-like fuzz."""
    h = (tx.i * 92821 + (tx.j // 2) * 68917 + tx.ci * 31) % 7
    return rgb * (1 - k if h == 0 else 1 + k * 0.7 if h == 3 else 1.0)


def body_parts(m):
    # small keeled torso, high on the stilt legs
    m.box("body", (-8, 54, -14), (8, 70, 14), name="torso")
    m.box("body", (-9, 56, -14), (9, 68, -4), name="pectorals")             # flight muscles
    m.box("body", (-5, 50, -12), (5, 54, 6), name="keel")
    m.box("body", (-6, 68, -16), (6, 72, -8), name="shoulders")
    m.box("body", (-4, 72, -14), (4, 73, -10), name="notarium")             # fused shoulder vertebrae
    m.box("body", (-6, 56, 14), (6, 66, 18), name="synsacrum")
    m.box("body", (-1, 70, 0), (1, 71, 12), tag="fuzz_dark", name="mane")
    m.box("body", (-1, 60, 18), (1, 63, 24), tag="limb", name="tail")

    # giraffe neck: three stiff tube-like segments rising steeply from the chest, a fuzz mane along the top
    secs = [(8, 8), (6, 7), (5, 6)]
    neck = m.chain(["neck1", "neck2", "neck3"], "body", 0, [(68, -14), (90, -22), (110, -28), (126, -32)], "-z",
                   secs, overlap=(1.5, 1.0))
    for seg, (w, hh) in zip(neck["segments"], secs):
        sy, sz = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-1, sy + hh / 2, sz - L + 1), (1, sy + hh / 2 + 1, sz), tag="fuzz_dark", name="mane")
    ay, az = neck["end"]
    m.bone("head", "neck3", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"] + 6, 0, 0))          # level, beak tipped slightly down

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    MD, MU = {"faces": {"down": "mouth"}}, {"faces": {"up": "mouth"}}
    # huge head: the braincase around the small eye, then a long tapering spear of a beak
    m.box("skull", *R(-5, -4, -12, 5, 6, 2), name="cranium", paint=MD)
    m.box("skull", *R(-4, -1, 2, 4, 5, 5), name="occiput")
    m.box("skull", *R(-4, -4, -28, 4, 4, -12), name="beak_base", tag="beak", paint=MD)
    m.box("skull", *R(-3, -4, -42, 3, 2, -28), name="beak_mid", tag="beak", paint=MD)
    m.box("skull", *R(-2, -4, -52, 2, 0, -42), name="beak_front", tag="beak", paint=MD)
    m.box("skull", *R(-1, -4, -58, 1, -1, -52), name="beak_tip", tag="beak_tip")
    for z0, z1, top in CREST:
        c = m.box("skull", *R(-0.5, 3, z0, 0.5, top, z1), name="crest", tag="crest")
        c.capped = (z0, z1) in MALE_CREST
    m.bone("male_display", "skull", (0, ay, az))
    for z0, z1, top in CREST:
        if (z0, z1) in MALE_CREST:
            m.box("male_display", *R(-0.5, top, z0, 0.5, top + 2, z1), name="crest_tall", tag="crest")
    m.bone("jaw", "skull", (0, ay - 4, az - 10))
    m.box("jaw", *R(-3.5, -8, -26, 3.5, -4, -8), name="jaw", tag="beak", paint=MU)
    m.box("jaw", *R(-2.5, -7, -42, 2.5, -4, -26), name="jaw_mid", tag="beak", paint=MU)
    m.box("jaw", *R(-1.5, -6, -52, 1.5, -4, -42), name="jaw_front", tag="beak", paint=MU)
    m.box("jaw", *R(-1, -6, -57, 1, -4, -52), name="jaw_tip", tag="beak_tip")
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (5, ay + 2, az - 6), "r": 1.5, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-5, ay + 2, az - 6), "r": 1.5, "side": -1},
        # bare red skin around the eye, stork style
        {"kind": "spot", "bones": ["skull"], "pos": (5, ay + 2, az - 6), "r": 3.6, "rx": 1.2, "side": 1, "color": "face"},
        {"kind": "spot", "bones": ["skull"], "pos": (-5, ay + 2, az - 6), "r": 3.6, "rx": 1.2, "side": -1, "color": "face"},
        # the huge nasoantorbital opening: a long dark slot on the beak base
        {"kind": "band_y", "bones": ["skull"], "pos": (0, ay + 0.5, 0), "r": 1.6, "mul": 0.66, "side": 1,
         "zmin": az - 25, "zmax": az - 14},
        {"kind": "band_y", "bones": ["skull"], "pos": (0, ay + 0.5, 0), "r": 1.6, "mul": 0.66, "side": -1,
         "zmin": az - 25, "zmax": az - 14},
    ]
    m._head_z = az
    add_saddle(m, "body", 70, -6, 6, 12, 9, flap=8)


def leg(m, side, s):
    # stilt legs: long femur sloping forward, long shin back, long metatarsus; a padded foot with four slender toes
    x = 5 * s
    ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x,
                 [(56, 10), (34, 4), (12, 12), (2, 6)], "-y",
                 [(6, 6), (4, 4, 0.0, "limb"), (3, 3, 0.0, "limb")], overlap=(2.0, 1.0))
    by, bz = ch["end"]
    T = f"toes_{side}"
    m.bone(T, f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
    m.box(T, (x - 3, by - 2, bz - 4), (x + 3, by, bz + 3), tag="limb", name="foot_pad")
    for k in range(4):
        a = x + (-3 + 1.5 * k) * s
        L = (6, 8, 8, 6)[k]
        a0, a1 = sorted((a, a + s))
        m.box(T, (a0, by - 1, bz - 4 - L), (a1, by, bz - 4), tag="limb", name="toe")
        m.box(T, (a0, by - 1, bz - 6 - L), (a1, by, bz - 4 - L), tag="claw", name="claw")


def after_wings(m):
    sx0, sy, sz = SHOULDER
    for side, s in (("l", 1), ("r", -1)):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        a, b = X(sx0 + 5, sx0 + 12)
        m.box(f"wing1_{side}", (a, sy - 3, sz - 3), (b, sy + 1, sz - 1), tag="limb", name="deltopectoral")
        a, b = X(sx0 + 3, sx0 + W1 - 2)
        m.box(f"wing1_{side}", (a, sy, sz - 5.5), (b, sy + 1, sz - 1.5), tag="membrane", name="propatagium")
        wrist = sx0 + W1 + W2
        for k in range(3):                                   # three small clawed fingers: its feet on the ground
            a, b = X(wrist - 5 + 1.5 * k, wrist - 4 + 1.5 * k)
            m.box(f"wing2_{side}", (a, sy - 2, sz - 5.5), (b, sy - 1, sz - 1.5), tag="limb", name="finger")
            m.box(f"wing2_{side}", (a, sy - 3, sz - 6.5), (b, sy - 1, sz - 5.5), tag="claw", name="claw")
        # membrane taper: deeper next to the body (the brachiopatagium runs back to the leg)
        x1, x2, x3 = sx0, sx0 + W1, sx0 + W1 + W2
        z0 = sz + TH
        for bone, (xa, xb), c0, extra in (("mem1", (x1, x1 + 12), CHORD[0], 6), ("mem1", (x1 + 12, x2 - 4), CHORD[0], 3),
                                          ("mem2", (x2, x2 + 14), CHORD[1], 3), ("mem3", (x3, x3 + 12), CHORD[2], 2)):
            a, b = X(xa, xb)
            m.box(f"{bone}_{side}", (a, sy - 0.5, z0 + c0), (b, sy + 0.5, z0 + c0 + extra), tag="membrane",
                  name="membrane_taper")


def pattern(model, tx, rgb, region):
    tag = tx.cube.tag
    P = tx.P
    pal = tx.pal
    if tag == "membrane":
        chord = (P[2] - (SHOULDER[2] + TH)) / float(CHORD[0])
        rgb = rgb * (1.05 - 0.3 * max(0.0, min(1.0, chord)))
        if int(math.floor(abs(P[0]) / 5.0 + P[2] / 10.0)) % 4 == 0:
            rgb = rgb * 0.88                         # stiffening fibres (actinofibrils)
        if abs(P[0]) > SHOULDER[0] + W1 + W2 + W3 / 2:
            rgb = pal["wingtip"].copy()              # dark outer wing
        if tx.face in ("up", "down") and tx.edge:
            rgb = pal["membrane_edge"].copy()
        if tx.cube.name == "propatagium":
            rgb = rgb * 1.08
        if tx.face == "down":
            rgb = rgb * 1.1
    elif tag == "crest":
        top = tx.face == "up" or tx.cube.name == "crest_tall" or (P[1] > tx.cube.to[1] - 1.01 and not getattr(tx.cube, "capped", False))
        rgb = pal["crest_edge"].copy() if top else pal["crest"] * (0.85 + 0.15 * math.sin(P[2] * 0.6))
    elif tag in ("beak", "beak_tip"):
        g = max(0.0, min(1.0, (model._head_z - P[2]) / 58.0))
        rgb = rgb * (1.06 - 0.22 * g)                # darker toward the tip
        if tx.face in ("east", "west") and tx.edge and tx.cube.bone == "skull" and P[1] < model._jaw_y + 1:
            rgb = rgb * 0.82                         # cutting edge
    elif tag in ("skin", "fuzz_dark"):
        if tx.cube.bone == "skull" and tx.face != "down":
            rgb = pal["cap"].copy() if P[1] > tx.cube.frm[1] + 5 else rgb      # dark cap over the skull
        elif tx.cube.bone.startswith("neck"):
            if region == "belly":
                rgb = pal["throat"].copy()                                     # pale throat
            elif math.sin(P[1] * 0.55) > 0.6:
                rgb = rgb * 0.92                                               # faint rings down the neck
        elif region == "dorsal" and math.sin(P[2] * 0.45 + P[0] * 0.3) > 0.75:
            rgb = rgb * 0.9
        rgb = _fuzz(tx, rgb)
    elif tag == "limb":
        rgb = _fuzz(tx, rgb, 0.08)
    return rgb


def attack(m):
    # spear-fishing jab: the whole neck whips down and forward, then snaps back
    m.anim("attack", 0.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.2, 15, 0, 0), (0.42, -40, 0, 0), (0.6, -30, 0, 0), (0.8, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.2, 6, 0, 0), (0.42, -18, 0, 0), (0.8, 0, 0, 0)])),
        "neck3": track(rot=keys([(0, 0, 0, 0), (0.2, 4, 0, 0), (0.42, -10, 0, 0), (0.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.2, 8, 0, 0), (0.42, -12, 0, 0), (0.8, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -22, 0, 0), (0.4, -26, 0, 0), (0.48, 0, 0, 0), (0.8, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.42, -5, 0, 0), (0.8, 0, 0, 0)])),
    })


SPEC = dict(
    render_scale=0.5,
    palette={"dorsal": "#8c8378", "flank": "#c9c1b2", "belly": "#efe9dc", "throat": "#f3eee2", "cap": "#3c3a3a",
             "limb": "#5b5550", "limb_top": "#6e6760", "fuzz_dark": "#6a635a",
             "membrane": "#5d4a3f", "membrane_edge": "#3a2c25", "wingtip": "#2e2420",
             "beak": "#e0cfa0", "beak_tip": "#2a2522", "crest": "#9a3a2a", "crest_edge": "#d87048", "face": "#c8472e",
             "claw": "#2c2420", "claw_base": "#3a302a", "mouth": "#8a5040", "eye": "#e6c24a", "pupil": "#120d0a"},
    sexes={"male": {"face": "#d84a2c", "crest": "#a83828", "crest_edge": "#e88050"},
           "female": {"face": "#9a6a5a", "crest": "#7a5a4a", "crest_edge": "#a88068", "cap": "#55504c",
                      "dorsal": "#948b80"}},
    pattern=pattern, body=(BODY_Y, 0), shoulder=SHOULDER,
    wing=(W1, W2, W3), chord=CHORD, wing_thick=TH,
    # on the ground the long metacarpal is the front leg: humerus down and forward, hand straight down,
    # the wing finger folded back up along the body
    fold_dirs={"wing1": (0.3, -0.7, -0.6), "wing2": (0.05, -0.95, 0.3), "wing3": (-0.1, 0.8, 0.6)},
    body_tilt=8, neck_rest=(-4, 0), neck_fly=(-62, 52),
    legs_fly=(-80, 25, -20), flap=(1.4, 26),             # slow, deep beats of a soaring giant
    body_parts=body_parts, leg=leg, after_wings=after_wings, attack=attack,
    gait={"walk": (1.6, 16), "run": (0.9, 26)},
    sit=dict(drop=48, thigh=50, shin=-120, foot=70, neck=-25, skull=14, body=(4, 0.6)),
    sit_wings={"wing1": (0.1, -0.46, 0.88), "wing2": (0.0, -0.06, -1.0), "wing3": (0.0, 0.6, 0.8)},
    ko=(80, 0.2, 0.7),
    # unconscious: the long neck falls forward and down to the ground, beak flat, jaw slack
    ko_joints={"neck1": (-62, 8, 0), "neck2": (-8, 2, 0), "neck3": (-4, 0, 0), "skull": (58, 0, 0), "jaw": (-14, 0, 0)},
)


def build():
    m = pterosaur.build(ID, SPEC)
    for a in m.animations:      # the archetype's moving poses are authored at 1x: scale their position keys
        if a["name"].split(".")[-1] in ("idle", "walk", "run", "fly", "glide", "attack", "eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    sit = next(a for a in m.animations if a["name"].endswith(".sit"))   # folded legs beside the belly, not inside it
    for side, sg in (("l", 1), ("r", -1)):
        for bone, roll in (("thigh", SIT_SPLAY[0]), ("shin", SIT_SPLAY[1])):
            tr = sit["bones"][f"{bone}_{side}"]
            tr["rotation"] = [[k[0], k[1], k[2], k[3] + sg * roll] for k in tr["rotation"]]
    low = lowest_point(m, sit["bones"])
    for bone, tr in sit["bones"].items():
        if "position" in tr and (bone == "body" or bone.startswith("thigh")):
            tr["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in tr["position"]]
    m._jaw_y = 0
    for b in m.bones:
        if b.name == "jaw":
            m._jaw_y = b.pivot[1]
    fit_to_ground(m, "eat", ("neck1", "neck2", "neck3", "skull", "body"))
    fit_to_ground(m, "attack", ("neck1", "neck2", "neck3", "skull", "body"))
    return m
