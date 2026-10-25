"""
Hatzegopteryx thambema  (Maastrichtian, Densuș-Ciula Formation, Hațeg Island, Romania)

Reference:
  - Size (Buffetaut, Grigorescu & Csiki 2002; Naish & Witton 2017): wingspan ~10-12 m, one of the largest
    pterosaurs. Unlike the slender Quetzalcoatlus it was ROBUST: the skull very wide at the back (~50 cm across the
    jaw joints) with thick spongy bone walls, a massive beak, and a short (~1.5 m), extremely stout neck of thick
    vertebrae (Vremir et al. 2018) able to take the stress of big prey; heavy limb bones.
  - Ecology (Naish & Witton 2017): on its island there were no big theropods, so this azhdarchid was the apex
    predator, taking dwarf dinosaurs (Magyarosaurus, Zalmoxes) the size of a pony. A bruiser, not a stork.
  - Like other azhdarchids: walked on all fours on the three small fingers with the wing finger folded up, long
    narrow wings, plantigrade padded four-toed feet, a coat of short pycnofibres.

v2x (2026-10-24, remaster at the T. rex v3 level): modelled at twice the old resolution (~21 px = 1 m), with the
details above. Built on the pterosaur archetype (species/pterosaur.py): wing bones, folding and the animation
set; the archetype's position keys are scaled by K. Same class of giant as the Quetzalcoatlus, but a heavier
body, a short thick neck and a wide deep skull. Males darker with a dark red keel on the beak.
"""
import math
from groundfit import fit_to_ground
from rig import track, keys, add_saddle, lowest_point
import pterosaur

ID = "hatzegopteryx"
K = 2.0
SHOULDER = (10, 60, -8)
BODY_Y = 56
W1, W2, W3 = 30, 42, 44
CHORD = (20, 16, 12, 6)
TH = 2.5                         # half thickness of the arm and hand bones: heavy limb bones
# low keel ridge along the top of the beak as columns (z0, z1, top y) in head px; male columns +2
CREST = [(-30, -24, 8), (-24, -16, 10), (-16, -10, 10), (-10, -6, 9)]
MALE_CREST = {(-24, -16), (-16, -10)}
SIT_SPLAY = (30, -60)            # resting: thigh and shin roll out (deg)


def _fuzz(tx, rgb, k=0.13):
    """Coarse pycnofibres: streaks of lighter and darker fuzz."""
    h = (tx.i * 92821 + (tx.j // 2) * 68917 + tx.ci * 31) % 7
    return rgb * (1 - k if h == 0 else 1 + k * 0.7 if h == 3 else 1.0)


def body_parts(m):
    # heavy barrel torso with a deep keel
    m.box("body", (-10, 46, -16), (10, 66, 16), name="torso")
    m.box("body", (-11, 48, -16), (11, 64, -4), name="pectorals")           # flight muscles
    m.box("body", (-7, 40, -14), (7, 46, 8), name="keel")
    m.box("body", (-8, 64, -20), (8, 68, -8), name="shoulders")
    m.box("body", (-5, 68, -18), (5, 69, -10), name="notarium")
    m.box("body", (-7, 50, 16), (7, 62, 20), name="synsacrum")
    m.box("body", (-1, 66, -2), (1, 67, 12), tag="fuzz_dark", name="mane")
    m.box("body", (-3, 54, 20), (3, 60, 28), tag="limb", name="tail")

    # short, very thick neck: two stout segments rising at ~55 degrees, a coarse mane
    secs = [(14, 14), (12, 12)]
    neck = m.chain(["neck1", "neck2"], "body", 0, [(62, -16), (76, -28), (88, -38)], "-z", secs, overlap=(4.0, 3.0))
    for seg, (w, hh) in zip(neck["segments"], secs):
        sy, sz = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-1.5, sy + hh / 2, sz - L + 1), (1.5, sy + hh / 2 + 1, sz), tag="fuzz_dark", name="mane")
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"] + 10, 0, 0))        # heavy head carried slightly down

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    MD, MU = {"faces": {"down": "mouth"}}, {"faces": {"up": "mouth"}}
    # wide deep skull: broad back of the head, then a massive beak that stays deep almost to the tip
    m.box("skull", *R(-9, -6, -14, 9, 8, 4), name="cranium", paint=MD)
    m.box("skull", *R(-7, -2, 4, 7, 6, 7), name="occiput")
    m.box("skull", *R(-6, -6, -30, 6, 6, -14), name="beak_base", tag="beak", paint=MD)
    m.box("skull", *R(-4.5, -6, -42, 4.5, 5, -30), name="beak_mid", tag="beak", paint=MD)
    m.box("skull", *R(-3, -5, -52, 3, 3, -42), name="beak_front", tag="beak", paint=MD)
    m.box("skull", *R(-1.5, -4, -58, 1.5, 1, -52), name="beak_tip", tag="beak_tip")
    for z0, z1, top in CREST:
        c = m.box("skull", *R(-1, 5, z0, 1, top, z1), name="crest", tag="crest")
        c.capped = (z0, z1) in MALE_CREST
    m.bone("male_display", "skull", (0, ay, az))
    for z0, z1, top in CREST:
        if (z0, z1) in MALE_CREST:
            m.box("male_display", *R(-1, top, z0, 1, top + 2, z1), name="crest_tall", tag="crest")
    m.bone("jaw", "skull", (0, ay - 6, az - 8))
    m.box("jaw", *R(-7, -11, -14, 7, -6, -2), name="jaw_back", paint=MU)    # the wide jaw joints
    m.box("jaw", *R(-5, -12, -30, 5, -6, -14), name="jaw", tag="beak", paint=MU)
    m.box("jaw", *R(-3.5, -11, -42, 3.5, -6, -30), name="jaw_mid", tag="beak", paint=MU)
    m.box("jaw", *R(-2.5, -9, -52, 2.5, -5, -42), name="jaw_front", tag="beak", paint=MU)
    m.box("jaw", *R(-1, -7, -57, 1, -4, -52), name="jaw_tip", tag="beak_tip")
    m.decals += [
        # pale bare face
        {"kind": "spot", "bones": ["skull"], "pos": (9, ay + 1, az - 7), "r": 3.5, "rx": 1.3, "side": 1, "color": "face"},
        {"kind": "spot", "bones": ["skull"], "pos": (-9, ay + 1, az - 7), "r": 3.5, "rx": 1.3, "side": -1, "color": "face"},
        {"kind": "eye", "bones": ["skull"], "pos": (9, ay + 2, az - 7), "r": 1.5, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-9, ay + 2, az - 7), "r": 1.5, "side": -1},
        # the nasoantorbital opening: a long dark slot on the beak base
        {"kind": "band_y", "bones": ["skull"], "pos": (0, ay + 1, 0), "r": 2.0, "mul": 0.66, "side": 1,
         "zmin": az - 28, "zmax": az - 16},
        {"kind": "band_y", "bones": ["skull"], "pos": (0, ay + 1, 0), "r": 2.0, "mul": 0.66, "side": -1,
         "zmin": az - 28, "zmax": az - 16},
    ]
    m._head_z = az
    add_saddle(m, "body", 66, -6, 8, 16, 11, flap=10)


def leg(m, side, s):
    # thick, fairly short legs; broad padded feet with four toes
    x = 6 * s
    ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x,
                 [(50, 12), (32, 6), (12, 12), (2, 8)], "-y",
                 [(8, 8), (6, 6, 0.0, "limb"), (5, 5, 0.0, "limb")], overlap=(2.0, 1.0))
    by, bz = ch["end"]
    T = f"toes_{side}"
    m.bone(T, f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
    m.box(T, (x - 4, by - 2, bz - 4), (x + 4, by, bz + 4), tag="limb", name="foot_pad")
    for k in range(4):
        a = x + (-4 + 2 * k) * s
        L = (6, 8, 8, 6)[k]
        a0, a1 = sorted((a, a + 2 * s))
        m.box(T, (a0, by - 2, bz - 4 - L), (a1, by, bz - 4), tag="limb", name="toe")
        m.box(T, (a0, by - 2, bz - 6 - L), (a1, by - 1, bz - 4 - L), tag="claw", name="claw")


def after_wings(m):
    sx0, sy, sz = SHOULDER
    for side, s in (("l", 1), ("r", -1)):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        a, b = X(sx0 + 5, sx0 + 13)
        m.box(f"wing1_{side}", (a, sy - 2, sz - 6), (b, sy + 1, sz - 2), tag="limb", name="deltopectoral")
        a, b = X(sx0 + 4, sx0 + W1 - 2)
        m.box(f"wing1_{side}", (a, sy, sz - 6.5), (b, sy + 1, sz - 2.5), tag="membrane", name="propatagium")
        wrist = sx0 + W1 + W2
        for k in range(3):                                   # three small clawed fingers: its feet on the ground
            a, b = X(wrist - 6 + 2 * k, wrist - 5 + 2 * k)
            m.box(f"wing2_{side}", (a, sy - 3, sz - 6.5), (b, sy - 1, sz - 2.5), tag="limb", name="finger")
            m.box(f"wing2_{side}", (a, sy - 4, sz - 8.5), (b, sy - 1, sz - 6.5), tag="claw", name="claw")
        # membrane taper: deeper next to the body (the brachiopatagium runs back to the leg)
        x1, x2, x3 = sx0, sx0 + W1, sx0 + W1 + W2
        z0 = sz + TH
        for bone, (xa, xb), c0, extra in (("mem1", (x1, x1 + 12), CHORD[0], 7), ("mem1", (x1 + 12, x2 - 4), CHORD[0], 3),
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
        rgb = rgb * (1.05 - 0.25 * max(0.0, min(1.0, chord)))
        if math.sin(abs(P[0]) * 0.275) > 0.45:
            rgb = rgb * 0.8                          # broad dark bars across the wing
        if abs(P[0]) > SHOULDER[0] + W1 + W2 + W3 / 2:
            rgb = pal["wingtip"].copy()
        if tx.face in ("up", "down") and tx.edge:
            rgb = pal["membrane_edge"].copy()
        if tx.face == "down":
            rgb = rgb * 1.08
    elif tag == "crest":
        top = tx.face == "up" or tx.cube.name == "crest_tall" or (P[1] > tx.cube.to[1] - 1.01 and not getattr(tx.cube, "capped", False))
        rgb = pal["crest_edge"].copy() if top else pal["crest"] * (0.85 + 0.15 * math.sin(P[2] * 0.45))
    elif tag in ("beak", "beak_tip"):
        g = max(0.0, min(1.0, (model._head_z - P[2]) / 58.0))
        rgb = rgb * (1.12 - 0.25 * g)                # dark beak, paler toward the base
        if tx.cube.bone == "jaw":
            rgb = rgb * 0.92
    elif tag in ("skin", "fuzz_dark"):
        if tx.cube.bone == "skull" and tx.face != "down" and P[1] > tx.cube.frm[1] + 6:
            rgb = pal["cap"].copy()
        elif tx.cube.bone.startswith("neck"):
            if region == "belly":
                rgb = pal["throat"].copy()               # pale throat
            elif math.sin(P[1] * 1.05 + P[0] * 0.65) * math.sin(P[2] * 0.85) > 0.55:
                rgb = rgb * 0.86                         # speckled sides
        elif region in ("dorsal", "flank") and math.sin(P[0] * 0.75) * math.sin(P[2] * 0.55 + P[1] * 0.5) > 0.6:
            rgb = rgb * 0.88
        rgb = _fuzz(tx, rgb)
    elif tag == "limb":
        rgb = _fuzz(tx, rgb, 0.08)
    return rgb


def attack(m):
    # slam: the whole body lunges and the heavy beak comes down like an axe, then shakes the prey
    m.anim("attack", 1.0, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.25, -6, 0, 0), (0.45, 10, 0, 0), (1.0, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.25, 0, 1, 1), (0.45, 0, -1.5, -3), (1.0, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.25, 22, 0, 0), (0.45, -30, 0, 0), (0.6, -28, 0, 6), (0.75, -28, 0, -6), (1.0, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.25, 8, 0, 0), (0.45, -14, 0, 0), (1.0, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.25, 10, 0, 0), (0.45, -16, 0, 0), (0.6, -14, 0, 8), (0.75, -14, 0, -8), (1.0, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.25, -30, 0, 0), (0.42, -34, 0, 0), (0.5, -4, 0, 0), (0.75, -4, 0, 0), (1.0, 0, 0, 0)])),
    })


SPEC = dict(
    render_scale=0.5,
    palette={"dorsal": "#4e4a48", "flank": "#78706a", "belly": "#b9ada0", "throat": "#cfc4b4", "cap": "#2a2626",
             "limb": "#3f3a38", "limb_top": "#524c49", "fuzz_dark": "#3e3a38",
             "membrane": "#4a3f3b", "membrane_edge": "#2b2422", "wingtip": "#1f1a19",
             "beak": "#5a4a3e", "beak_tip": "#1e1917", "crest": "#7a2a22", "crest_edge": "#a84030", "face": "#d8c6a8",
             "claw": "#1e1917", "claw_base": "#2c2522", "mouth": "#7a4038", "eye": "#d9b14a", "pupil": "#0f0b09"},
    sexes={"male": {"crest": "#8a2820", "crest_edge": "#b83a2a", "dorsal": "#44403e", "cap": "#1e1b1b"},
           "female": {"crest": "#5e4a42", "crest_edge": "#7a6458", "dorsal": "#5a5452", "face": "#c9b9a0",
                      "flank": "#827a74"}},
    pattern=pattern, body=(BODY_Y, 0), shoulder=SHOULDER,
    wing=(W1, W2, W3), chord=CHORD, wing_thick=TH,
    # on the ground: a stockier stance than the Quetzalcoatlus, humerus more vertical
    fold_dirs={"wing1": (0.3, -0.6, -0.62), "wing2": (0.05, -0.95, 0.25), "wing3": (-0.1, 0.75, 0.65)},
    body_tilt=10, neck_rest=(-2, 0), neck_fly=(-50, 42),
    legs_fly=(-78, 22, -16), flap=(1.6, 24),             # slow, powerful beats
    body_parts=body_parts, leg=leg, after_wings=after_wings, attack=attack,
    gait={"walk": (1.9, 14), "run": (1.1, 24)},
    sit=dict(drop=44, thigh=50, shin=-120, foot=70, neck=-18, skull=12, body=(4, 0.6)),
    sit_wings={"wing1": (0.1, -0.5, 0.86), "wing2": (0.0, -0.06, -1.0), "wing3": (0.0, 0.6, 0.8)},
    ko=(80, 0.2, 0.7),
    ko_joints={"neck1": (-48, 10, 0), "neck2": (-10, 3, 0), "skull": (42, 0, 0), "jaw": (-16, 0, 0)},
)


def build():
    m = pterosaur.build(ID, SPEC)
    m.cubes = [c for c in m.cubes if c.name != "fingers"]   # the archetype's claw strip: replaced by three fingers
    for a in m.animations:      # the archetype's moving poses are authored at 1x: scale their position keys
        if a["name"].split(".")[-1] in ("idle", "walk", "run", "fly", "glide", "attack", "eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    idle = next(a for a in m.animations if a["name"].endswith(".idle"))  # breathing lifts the heavy body, never sinks it
    idle["bones"]["body"]["position"] = [[k[0], k[1], round((k[2] + 0.4) / 2, 3), k[3]] for k in idle["bones"]["body"]["position"]]
    sit = next(a for a in m.animations if a["name"].endswith(".sit"))   # folded legs beside the belly, not inside it
    for side, sg in (("l", 1), ("r", -1)):
        for bone, roll in (("thigh", SIT_SPLAY[0]), ("shin", SIT_SPLAY[1])):
            tr = sit["bones"][f"{bone}_{side}"]
            tr["rotation"] = [[k[0], k[1], k[2], k[3] + sg * roll] for k in tr["rotation"]]
    low = lowest_point(m, sit["bones"])
    for bone, tr in sit["bones"].items():
        if "position" in tr and (bone == "body" or bone.startswith("thigh")):
            tr["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in tr["position"]]
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    fit_to_ground(m, "attack", ("neck1", "neck2", "skull", "body"))
    return m
