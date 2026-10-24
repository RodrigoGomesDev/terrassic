"""
Pteranodon longiceps  (Late Cretaceous, Western Interior Seaway, Kansas)

Reference (Bennett 1992, 1994, 2001; Witton 2013; Wikipedia):
  - Wingspan 5.6-7.25 m in adult males, ~3.8 m in females; body ~2.6 m from beak to tail (USNM 50130); 20-50 kg.
  - Skull long and toothless: the upper beak is longer than the lower one, slender, slightly upturned and needle
    pointed; a long nasoantorbital opening in front of the eye; a pouched throat like a pelican's is likely.
  - Crest of the frontal bones: a long backswept blade in males of P. longiceps, small and rounded in females;
    some skulls show a low ridge running forward toward the beak.
  - Head, neck and shoulders heavily built like a diving bird's; notarium (fused front dorsals) over the shoulders,
    robust humerus with a big curved deltopectoral crest; metacarpal IV and the four-jointed wing finger make most of
    the span; three small clawed free fingers at the wrist; a pteroid bone holding the propatagium in front of the
    arm; wing membrane stiffened by actinofibrils; short hind legs with four clawed toes; tail tiny (~3.5% of span).
  - Body, neck and head covered in short pycnofibres (hair-like fuzz), not scales.
  - Quadrupedal on the ground (trackways), wings folded so the hands are front feet.

v3 (2026-10-24, "padrão T. rex" for every species): modelled at TWICE the old resolution (one texture pixel = one
vanilla pixel in game), with the details above. render_scale 0.5 = authoring scale; the in-game size comes from
SIZES in tools/javagen/gen_species.py (game exception: 1.5x the real span so a rider fits, docs/TAMANHOS.md).
Built on the pterosaur archetype (species/pterosaur.py): wing bones, folding and the animation set.
"""
import math
from rig import track, keys, add_saddle, lowest_point
import pterosaur

ID = "pteranodon"
K = 2.0                      # authoring resolution relative to the 1x archetype poses (position keys are scaled by it)

SHOULDER = (8, 32, -8)       # x, y, z of the left shoulder
W1, W2, W3 = 24, 24, 52      # arm (humerus + forearm), metacarpal IV, wing finger (the longest bone)
CHORD = (24, 18, 12, 6)      # membrane depth behind the arm, hand and the two halves of the finger
HEAD = (30, -32)             # (y, z) where the head hangs off the neck


def _fuzz(tx, rgb, k=0.12):
    """Pycnofibres: short streaks of lighter and darker hair-like fuzz."""
    h = (tx.i * 92821 + (tx.j // 2) * 68917 + tx.ci * 31) % 7
    return rgb * (1 - k if h == 0 else 1 + k * 0.7 if h == 3 else 1.0)


def body_parts(m):
    m.box("body", (-8, 20, -12), (8, 34, 16), name="torso")
    m.box("body", (-9, 22, -12), (9, 32, -2), name="pectorals")            # big flight muscles
    m.box("body", (-5, 18, -12), (5, 20, 4), name="sternum")
    m.box("body", (-4, 34, -12), (4, 35, -10), name="notarium")             # fused shoulder vertebrae
    m.box("body", (-6, 22, 16), (6, 31, 20), name="synsacrum")
    m.box("body", (-1, 34, 8), (1, 35, 14), tag="fuzz_dark", name="mane")    # fuzz along the spine behind the saddle

    # neck: two heavy segments rising to the head, with a fuzz mane
    m.bone("neck1", "body", (0, 30, -12), (25, 0, 0))
    m.box("neck1", (-3, 27, -24), (3, 33, -10), name="neck1")
    m.box("neck1", (-1, 33, -23), (1, 34, -11), tag="fuzz_dark", name="mane")
    m.bone("neck2", "neck1", (0, 30, -22), (10, 0, 0))
    m.box("neck2", (-3, 27, -34), (3, 33, -20), name="neck2")
    m.box("neck2", (-1, 33, -33), (1, 34, -21), tag="fuzz_dark", name="mane")
    ay, az = HEAD
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-35 - 8, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    MD = {"faces": {"down": "mouth"}}
    m.box("skull", *R(-4, -2, -10, 4, 6, 2), name="cranium", paint=MD)
    m.box("skull", *R(-3, 0, 2, 3, 5, 4), name="occiput")
    m.box("skull", *R(-3, -2, -22, 3, 4, -10), name="beak_base", tag="beak", paint=MD)
    m.box("skull", *R(-2, -2, -32, 2, 2, -22), name="beak_mid", tag="beak", paint=MD)
    m.box("skull", *R(-1.5, -2, -40, 1.5, 1, -32), name="beak_front", tag="beak", paint=MD)
    m.box("skull", *R(-1, -1, -46, 1, 1, -40), name="beak_tip", tag="beak")         # upturned, needle point
    m.box("skull", *R(-0.5, 0, -49, 0.5, 1, -46), name="beak_point", tag="beak_tip")
    m.box("skull", *R(-0.5, 4, -20, 0.5, 5, -10), name="ridge", tag="crest")         # low forward ridge
    m.bone("jaw", "skull", (0, ay - 2, az - 6))
    MU = {"faces": {"up": "mouth"}}
    m.box("jaw", *R(-3, -5, -24, 3, -2, -6), name="jaw", tag="beak", paint=MU)
    m.box("jaw", *R(-2, -4, -34, 2, -2, -24), name="jaw_mid", tag="beak", paint=MU)
    m.box("jaw", *R(-1, -4, -42, 1, -2, -34), name="jaw_front", tag="beak", paint=MU)
    m.box("jaw", *R(-0.5, -4, -45, 0.5, -3, -42), name="jaw_point", tag="beak_tip")
    m.box("jaw", *R(-2, -7, -22, 2, -5, -8), name="pouch", tag="pouch")                # throat pouch
    # crest: a long backswept blade on males, a small rounded one on females
    co = (0, ay + 4, az + 2)
    m.bone("male_display", "skull", (0, ay, az))
    for name, box in (("crest", (-1, 4, -2, 1, 10, 10)), ("crest_mid", (-1, 5, 10, 1, 10, 20)),
                      ("crest_tip", (-0.5, 6, 20, 0.5, 10, 28)), ("crest_point", (-0.5, 7, 28, 0.5, 9, 33))):
        m.box("male_display", *R(*box), name=name, tag="crest", rot=(-14, 0, 0), origin=co, paint={"axis": "+z"})
    m.bone("female_display", "skull", (0, ay, az))
    for name, box in (("crest", (-1, 4, -2, 1, 9, 6)), ("crest_tip", (-0.5, 5, 6, 0.5, 8, 11))):
        m.box("female_display", *R(*box), name=name, tag="crest", rot=(-12, 0, 0), origin=co, paint={"axis": "+z"})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4, ay + 2.5, az - 5), "r": 1.5, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4, ay + 2.5, az - 5), "r": 1.5, "side": -1},
        # nasoantorbital opening: a long dark slot in front of the eye
        {"kind": "spot", "bones": ["skull"], "pos": (3, ay + 1.5, az - 15), "r": 1.0, "rx": 1.2, "mul": 0.55, "side": 1},
        {"kind": "spot", "bones": ["skull"], "pos": (-3, ay + 1.5, az - 15), "r": 1.0, "rx": 1.2, "mul": 0.55, "side": -1},
    ]


def leg(m, side, s):
    # hind leg: short, under the hips; four clawed toes
    lx = 5 * s
    m.bone(f"thigh_{side}", "root", (lx, 22, 12))
    m.box(f"thigh_{side}", (lx - 2, 10, 10), (lx + 2, 22, 14), tag="limb", name="thigh")
    m.bone(f"shin_{side}", f"thigh_{side}", (lx, 10, 12))
    m.box(f"shin_{side}", (lx - 1, 2, 11), (lx + 1, 11, 13), tag="limb", name="shin")
    m.bone(f"foot_{side}", f"shin_{side}", (lx, 2, 12))
    m.box(f"foot_{side}", (lx - 2, 0, 6), (lx + 2, 2, 14), tag="limb", name="foot")
    for k in range(4):
        x = lx - 2 + k
        m.box(f"foot_{side}", (x, 0, 3), (x + 1, 1, 6), tag="claw", name="claw")


def after_wings(m):
    sx0, sy, sz = SHOULDER
    for side, s in (("l", 1), ("r", -1)):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        a, b = X(sx0 + 2, sx0 + 8)
        m.box(f"wing1_{side}", (a, sy - 2, sz - 4), (b, sy + 1, sz - 2), tag="limb", name="deltopectoral")
        a, b = X(sx0 + 3, sx0 + W1 - 2)
        m.box(f"wing1_{side}", (a, sy, sz - 5), (b, sy + 1, sz - 2), tag="membrane", name="propatagium")
        wrist = sx0 + W1 + W2
        for k in range(3):                                   # three small clawed free fingers
            a, b = X(wrist - 4 + k, wrist - 3 + k)
            m.box(f"wing2_{side}", (a, sy - 1, sz - 5), (b, sy, sz - 2), tag="limb", name="finger")
            m.box(f"wing2_{side}", (a, sy - 2, sz - 6), (b, sy, sz - 5), tag="claw", name="claw")
        # membrane taper: deeper next to the body (the brachiopatagium runs back to the leg), narrowing to the tip
        th = 2.0
        x1, x2, x3, x4 = sx0, sx0 + W1, sx0 + W1 + W2, sx0 + W1 + W2 + W3
        z0 = sz + th
        for bone, (xa, xb), c0, extra in (("mem1", (x1, x1 + 10), CHORD[0], 6), ("mem1", (x1 + 10, x2 - 4), CHORD[0], 3),
                                          ("mem2", (x2, x2 + 12), CHORD[1], 3), ("mem3", (x3, x3 + 13), CHORD[2], 3),
                                          ("mem3", (x3 + 26 + 13, x4), CHORD[3], -3)):
            a, b = X(xa, xb)
            if extra > 0:
                m.box(f"{bone}_{side}", (a, sy - 0.5, z0 + c0), (b, sy + 0.5, z0 + c0 + extra), tag="membrane", name="membrane_taper")
        # the outermost quarter of the finger membrane is cut back to a point
    m.bone("tail1", "body", (0, 28, 16))
    m.box("tail1", (-1, 27, 16), (1, 29, 26), name="tail")
    add_saddle(m, "body", 34, -10, 6, 12, 8, flap=8)


def pattern(model, tx, rgb, region):
    tag = tx.cube.tag
    P = tx.P
    sz = SHOULDER[2]
    az = HEAD[1]
    pal = tx.pal
    if tag == "membrane":
        # darker towards the trailing edge, actinofibrils running along the wing, a pale leading edge
        chord = (P[2] - (sz + 2)) / float(CHORD[0])
        rgb = rgb * (1.06 - 0.3 * max(0.0, min(1.0, chord)))
        if int(math.floor(abs(P[0]) / 2.0 + P[2] / 3.0)) % 4 == 0:
            rgb = rgb * 0.88
        if tx.face in ("up", "down") and tx.edge:
            rgb = pal["membrane_edge"].copy()
        if tx.cube.name == "propatagium":
            rgb = rgb * 1.08
        if tx.face == "down":
            rgb = rgb * 1.14
    elif tag == "crest":
        g = max(0.0, min(1.0, (P[2] - az) / 24.0))
        rgb = pal["crest"] * (1 - g) + pal["crest_tip"] * g
        if int(math.floor(P[2] / 3.0 + P[1] / 2.0)) % 3 == 0:       # display bars
            rgb = rgb * 0.82
    elif tag in ("beak", "beak_tip"):
        g = max(0.0, min(1.0, (az - P[2]) / 46.0))
        rgb = rgb * (1.05 - 0.25 * g)
        if tx.face in ("east", "west") and tx.edge and P[1] < model._jaw_y:
            rgb = rgb * 0.8                                          # cutting edge
    elif tag == "pouch":
        rgb = rgb * (0.95 if (tx.i + tx.j) % 3 else 0.88)
    elif tag in ("skin", "fuzz_dark"):
        if region == "dorsal" and math.sin(P[2] * 0.7 + P[0] * 0.35) > 0.65:
            rgb = rgb * 0.9
        rgb = _fuzz(tx, rgb)
    elif tag == "limb":
        rgb = _fuzz(tx, rgb, 0.08)
    return rgb


def attack(m):
    # quick beak jab
    m.anim("attack", 0.6, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.15, 20, 0, 0), (0.3, -25, 0, 0), (0.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.15, 10, 0, 0), (0.3, -10, 0, 0), (0.6, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.15, -25, 0, 0), (0.28, -30, 0, 0), (0.34, 0, 0, 0), (0.6, 0, 0, 0)])),
    })


SPEC = dict(
    render_scale=0.5,
    palette={"dorsal": "#6a655d", "flank": "#b6ae9f", "belly": "#ebe5d6",
             "limb": "#776b5d", "limb_top": "#8a7e6e", "fuzz_dark": "#5a544c",
             "membrane": "#7a5e4a", "membrane_edge": "#4a372b",
             "beak": "#dcc48e", "beak_tip": "#8c7650", "crest": "#c0482a", "crest_tip": "#e8a040",
             "pouch": "#c99a7a", "claw": "#2c2420", "claw_base": "#3a302a",
             "mouth": "#8a5040", "eye": "#d8a838", "pupil": "#120d0a"},
    sexes={"male": {"crest": "#b8402a", "crest_tip": "#f0a838"},
           "female": {"crest": "#8a7a62", "crest_tip": "#b0a080", "membrane": "#806a58", "dorsal": "#726d64"}},
    pattern=pattern, body=(28, 0), shoulder=SHOULDER,
    wing=(W1, W2, W3), chord=CHORD, wing_thick=2.0,
    fold_dirs={"wing1": (0.35, -0.5, -0.65), "wing2": (0.1, -0.72, 0.6), "wing3": (-0.25, 0.5, 0.83)},
    body_tilt=18, neck_rest=(-10, -4), neck_fly=(-20, 12),
    legs_fly=(-75, 10, -10), flap=(0.8, 32),
    body_parts=body_parts, leg=leg, after_wings=after_wings, attack=attack,
    gait={"walk": (1.0, 18), "run": (0.6, 28)},
    sit=dict(drop=10, thigh=60, shin=-100, foot=40, neck=-30, skull=10, body=(10, 0.4)),
    ko=(80, 0.3, 0.6),
    ko_joints={"neck1": (-34, 10, 0), "neck2": (-8, 2, 0), "skull": (26, 0, 0), "jaw": (-12, 0, 0)},
)


def build():
    m = pterosaur.build(ID, SPEC)
    # the archetype's moving poses are authored at 1x: scale their position keys (bob, flap lift) to this resolution
    for a in m.animations:
        if a["name"].split(".")[-1] in ("idle", "walk", "run", "fly", "glide", "attack", "eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    # the sit pose's body pitch is set after the archetype's ground_drop: put its lowest cube back on the ground
    sit = next(a for a in m.animations if a["name"].endswith(".sit"))
    low = lowest_point(m, sit["bones"])
    sit["bones"]["body"]["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in sit["bones"]["body"]["position"]]
    m._jaw_y = HEAD[0] - 2   # jaw line height, for the beak's cutting edge in pattern()
    return m

