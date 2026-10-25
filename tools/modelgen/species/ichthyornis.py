"""
Ichthyornis dispar  (Late Cretaceous, Niobrara Chalk, Kansas; Western Interior Seaway)

Reference (Marsh 1880; Clarke 2004; Field et al. 2018, the 3D skull):
  - A tern-sized seabird: ~60-66 cm wingspan, a body ~25 cm long, ~0.2-0.6 kg.
  - Skull (Field et al. 2018): proportionally large, with a big braincase and huge eyes like a modern bird, but
    long jaws that still carried small recurved TEETH along most of their length; only the tip of the snout was
    covered by a small hooked horny beak (the earliest known beak). Jaw muscles bulging at the back of the head.
  - Wings long and narrow with a deep keeled breastbone: a fast, strong flier over the sea. A short tail fan on a
    pygostyle (no tern streamers). Legs set back, three webbed front toes and a small hallux; it fished like a
    gull or tern.
  - Colours are unknown; the model keeps the tern-like scheme of the old one (white below, grey mantle, black
    cap and wingtips). Males with a cleaner black cap, females a browner mottled mantle.

v2x (2026-10-25, remaster at the T. rex v3 level): modelled at twice the old resolution (~128 px = 1 m, the
old one was ~64), so the toothed jaws, the coverts and each outer primary read. The head is ~1.4x the real
proportion (the old one was ~2.5x and as big as the body). Built on the bird archetype (species/bird.py): the
wing bones, folding and the animation set; the archetype's position keys are scaled by K.
"""
import math
from rig import track, keys, lowest_point
from groundfit import fit_to_ground
import bird

ID = "ichthyornis"
K = 2.0
BODY_Y = 21
DROP = 4                         # the body is authored 4 px higher, then lowered onto its short legs
SHOULDER = (6, 25 - DROP, -7)
ARM, HAND = 16, 20
SIT_SPLAY = (18, -30)            # resting: thigh and shin roll out (deg), feet beside the breast
TEETH = {"edge": "bottom", "rows": 1, "faces": ("east", "west"), "freq": 1.0}


def body_parts(m):
    # streamlined torso: deep keeled breast in front, tapering to the rump; a smooth feathered spindle
    m.box("body", (-5, 16, -14), (5, 26, -6), name="chest")
    m.box("body", (-6, 15, -6), (6, 27, 6), name="torso")
    m.box("body", (-4, 12, -13), (4, 16, 1), name="breast")             # the keel and flight muscles
    m.box("body", (-5, 17, 6), (5, 26, 11), name="flanks")
    m.box("body", (-3, 18, 11), (3, 24, 16), name="rump")
    m.box("body", (-4, 27, -10), (4, 28, 9), tag="feather", name="mantle")
    m.bone("tail", "body", (0, 22, 15))
    # short rounded tail fan on the pygostyle, the central feathers a little longer
    m.box("tail", (-5, 21, 15), (5, 22, 25), name="tail_fan", tag="feather")
    m.box("tail", (-3, 21, 25), (3, 22, 27), name="tail_mid", tag="feather")
    m.box("tail", (-2, 22, 15), (2, 23, 19), name="uppertail", tag="feather")

    # short S-neck carried forward, head held above the shoulders
    secs = [(5, 5), (4, 4)]
    neck = m.chain(["neck1", "neck2"], "body", 0, [(23, -11), (30, -16), (36, -19)], "-z", secs, overlap=(2.0, 1.5))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"] + 4, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    m._eye_y = ay + 1
    MD, MU = {"faces": {"down": "mouth"}}, {"faces": {"up": "mouth"}}
    # big rounded braincase, jaw muscles bulging behind the eye, long toothed jaws, a small hooked beak at the tip
    m.box("skull", *R(-3, -2, -5, 3, 3, 1), name="cranium", paint=MD)
    m.box("skull", *R(-2, 3, -4, 2, 4, 0), name="crown")
    m.box("skull", *R(-3.5, -2, -1, 3.5, 1, 1), name="jaw_muscle")
    m.box("skull", *R(-2, -2, -7, 2, 2, -5), name="lores", paint=MD)
    m.box("skull", *R(-1.5, -2, -12, 1.5, 1, -7), name="upper_jaw", tag="beak", paint=dict(MD, teeth=TEETH))
    m.box("skull", *R(-1, -2, -15, 1, 0, -12), name="upper_jaw_front", tag="beak", paint=dict(MD, teeth=TEETH))
    m.box("skull", *R(-1, -2, -17, 1, 0, -15), name="beak", tag="beak_tip", paint=MD)
    m.box("skull", *R(-0.5, -3, -18, 0.5, -1, -17), name="beak_hook", tag="beak_tip")
    m.bone("jaw", "skull", (0, ay - 2, az - 3))
    m.box("jaw", *R(-2, -4, -5, 2, -2, 0), name="jaw_back", paint=MU)
    m.box("jaw", *R(-1.5, -4, -12, 1.5, -2, -5), name="jaw", tag="beak", paint=dict(MU, teeth=dict(TEETH, edge="top")))
    m.box("jaw", *R(-1, -3, -16, 1, -2, -12), name="jaw_front", tag="beak", paint=dict(MU, teeth=dict(TEETH, edge="top")))
    m.box("jaw", *R(-0.5, -3, -17, 0.5, -2, -16), name="jaw_tip", tag="beak_tip")
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3, ay + 1, az - 2.5), "r": 1.4, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 1, az - 2.5), "r": 1.4, "side": -1},
        {"kind": "spot", "bones": ["skull"], "pos": (0, ay + 0.5, az - 13.5), "r": 0.5, "mul": 0.45, "side": 1},
        {"kind": "spot", "bones": ["skull"], "pos": (0, ay + 0.5, az - 13.5), "r": 0.5, "mul": 0.45, "side": -1},
    ]
    for b in m.bones[1:]:
        b.pivot[1] -= DROP
    for c in m.cubes:
        c.frm[1] -= DROP
        c.to[1] -= DROP
        c.origin[1] -= DROP
    m.decals = [dict(d, pos=(d["pos"][0], d["pos"][1] - DROP, d["pos"][2])) for d in m.decals]
    m._eye_y -= DROP


def leg(m, side, s):
    # short legs set well back, thin scaly shanks, three webbed front toes and a small hallux
    x = 4.0 * s
    ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x,
                 [(14, 6), (9, 4), (5, 7), (2, 5)], "-y",
                 [(4, 4), (2, 2, 0.0, "limb"), (2, 2, 0.0, "limb")], overlap=(1.5, 1.0))
    by, bz = ch["end"]
    T = f"toes_{side}"
    m.bone(T, f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))

    def X(a, b):
        return (min(x + a * s, x + b * s), max(x + a * s, x + b * s))
    for (a, b), L in (((-3.5, -2.5), 6), ((-0.5, 0.5), 8), ((2.5, 3.5), 7)):    # digits II, III, IV
        x0, x1 = X(a, b)
        m.box(T, (x0, by - 2, bz - L), (x1, by - 1, bz + 1), tag="limb", name="toe")
        m.box(T, (x0, by - 2, bz - L - 1), (x1, by - 1, bz - L), tag="claw", name="toe_claw")
    for (a, b), L in (((-2.5, -0.5), 5), ((0.5, 2.5), 6)):                      # the webs between them
        x0, x1 = X(a, b)
        m.box(T, (x0, by - 2, bz - L), (x1, by - 1, bz), tag="web", name="web")
    m.box(T, (x - 0.5, by - 2, bz + 1), (x + 0.5, by - 1, bz + 3), tag="claw", name="hallux")


def after_wings(m):
    sx0, sy, sz = SHOULDER
    x2, x3 = sx0 + ARM, sx0 + ARM + HAND
    for side, s in (("l", 1), ("r", -1)):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        # coverts: a second, shorter feather layer over the arm and the base of the hand
        a, b = X(sx0 + 1, x2)
        m.box(f"wing1_{side}", (a, sy + 0.5, sz), (b, sy + 1.5, sz + 6), tag="feather", name="coverts")
        a, b = X(x2, x2 + 8)
        m.box(f"wing2_{side}", (a, sy + 0.5, sz - 0.5), (b, sy + 1.5, sz + 5.5), tag="feather", name="coverts")
        a, b = X(x2 - 1, x2 + 2)
        m.box(f"wing2_{side}", (a, sy, sz - 1.5), (b, sy + 1, sz - 0.5), tag="feather", name="alula")
        # the pointed tip: the outer primaries step out past the hand, longest at the front edge
        for k, (dx, chord) in enumerate(((4, 3), (3, 3), (2, 3))):
            a, b = X(x3 + (0 if k == 0 else 0), x3 + dx)
            z0 = sz - 0.5 + 3 * k
            m.box(f"wing2_{side}", (a, sy - 0.5, z0), (b, sy + 0.5, z0 + chord), tag="feather", name="primaries_tip")


def pattern(model, tx, rgb, region):
    P = tx.P
    cube = tx.cube
    tag = cube.tag
    pal = tx.pal
    if tag == "feather":
        if cube.name == "primaries_tip" or (cube.name == "primaries" and abs(P[0]) > SHOULDER[0] + ARM + HAND * 0.7):
            return pal["wingtip"].copy()
        if cube.name == "primaries":
            k = (abs(P[0]) - abs(cube.frm[0])) / max(1.0, cube.size[0])
            rgb = rgb * (1.0 - 0.3 * max(0.0, min(1.0, k)))     # darkening toward the hand tip
            if int(abs(P[0])) % 3 == 0:
                rgb = rgb * 0.88                               # each primary shaft
            return rgb
        if cube.name == "secondaries":
            if tx.face in ("up", "down") and P[2] > cube.to[2] - 1.01:
                return pal["feather_edge"].copy()              # white trailing edge
            return rgb * (0.9 if int(abs(P[0])) % 2 == 0 else 1.0)
        if cube.name == "coverts":
            return pal["dorsal"] * (1.08 if int(math.floor(P[2] - cube.frm[2])) % 3 == 2 else 1.0)
        if cube.name in ("tail_fan", "tail_mid", "uppertail"):
            if tx.face in ("up", "down") and tx.edge:
                return pal["feather_edge"].copy()
            return pal["dorsal"] * (0.94 if int(abs(P[0])) % 2 else 1.0)
        if cube.name == "mantle":
            return pal["dorsal"] * (0.93 if (int(P[2]) + int(abs(P[0]))) % 3 == 0 else 1.0)
        return rgb
    if tag == "skin":
        if cube.bone == "skull":
            # black cap down through the eye, white throat and cheeks
            if tx.face != "down" and P[1] > model._eye_y - 0.6:
                return pal["cap"].copy()
            return pal["belly"].copy()
        if cube.bone.startswith("neck"):
            return pal["dorsal"].copy() if region == "dorsal" else pal["belly"].copy()
        if region == "dorsal":
            rgb = pal["dorsal"] * (0.92 if math.sin(P[0] * 1.4) * math.sin(P[2] * 0.9 + P[0]) > 0.7 else 1.0)
        elif region == "flank":
            rgb = pal["flank"].copy()
        if (tx.i * 7 + tx.j * 5) % 11 == 0:
            rgb = rgb * 0.95                                   # feather texture
        return rgb
    if tag == "beak" and tx.face not in ("down", "up"):
        return rgb * (0.9 if int(math.floor(P[2])) % 2 == 0 else 1.0)
    if tag == "limb" and cube.bone.startswith(("foot", "toes")) and tx.face != "down":
        return rgb * (0.85 if int(math.floor(P[2] + P[1])) % 2 == 0 else 1.0)   # scutes
    return rgb


def attack(m):
    # stab: a quick lunge of the head and a snap of the toothed jaws
    m.anim("attack", 0.5, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.15, -8, 0, 0), (0.3, 4, 0, 0), (0.5, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.12, 14, 0, 0), (0.25, -20, 0, 0), (0.5, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.12, 8, 0, 0), (0.25, -10, 0, 0), (0.5, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.12, 6, 0, 0), (0.25, -12, 0, 0), (0.5, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.12, -32, 0, 0), (0.25, -36, 0, 0), (0.3, -2, 0, 0), (0.5, 0, 0, 0)])),
    })


SPEC = dict(
    render_scale=0.125,
    palette={"dorsal": "#9aa1a6", "flank": "#c9cdcf", "belly": "#f1f0ea", "cap": "#1c1c1e",
             "limb": "#3a3236", "limb_top": "#4a4044", "web": "#4d3a3c",
             "feather": "#8e959a", "feather_edge": "#f1f0ea", "wingtip": "#22232a",
             "beak": "#55585c", "beak_tip": "#2a2b2e", "tooth": "#f4f0e4", "gum": "#4c4f54", "mouth": "#8a3f4a",
             "eye": "#2b2420", "pupil": "#0a0808", "claw": "#2a2b2e", "claw_base": "#2a2b2e", "claw_tip": "#4a4b4e"},
    sexes={"male": {"cap": "#101012", "dorsal": "#8f979d", "wingtip": "#15161a"},
           "female": {"cap": "#3a3430", "dorsal": "#a39e94", "feather": "#9a948a", "flank": "#cdc8be"}},
    pattern=pattern, body=(BODY_Y, 0), shoulder=SHOULDER,
    wing=(ARM, HAND), vanes=(10, 12, 7),
    # folded: humerus+forearm back along the flank, vane hanging down over the side, primaries crossing over the tail
    fold=((78, -82, -12), (-80, -6, 0)),
    body_parts=body_parts, leg=leg, after_wings=after_wings, attack=attack,
    neck_rest=(-6, 2), neck_fly=(-28, 20),
    legs_fly=(-80, 21, -60),                               # legs trailing under the tail
    flap=(0.45, 42),                                       # quick tern beats
    gait={"walk": (0.6, 24), "run": (0.4, 34)},
    sit=dict(drop=12, thigh=50, shin=-110, foot=80, toes=-45, neck=-14, skull=10),   # on its breast, feet tucked
    ko=(85, 0.3, 0.5),
    ko_joints={"neck1": (-30, 14, 0), "neck2": (-10, 0, 0), "skull": (30, 0, 0), "jaw": (-14, 0, 0)},
)


def build():
    m = bird.build(ID, SPEC)
    for a in m.animations:      # the archetype's moving poses are authored at 1x: scale their position keys
        if a["name"].split(".")[-1] in ("idle", "walk", "run", "fly", "glide", "attack", "eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    idle = next(a for a in m.animations if a["name"].endswith(".idle"))  # breathing lifts the body, never sinks it
    idle["bones"]["body"]["position"] = [[k[0], k[1], round(k[2] + 0.3, 3), k[3]] for k in idle["bones"]["body"]["position"]]
    sit = next(a for a in m.animations if a["name"].endswith(".sit"))   # feet beside the breast, not inside it
    for side, sg in (("l", 1), ("r", -1)):
        for bone, roll in (("thigh", SIT_SPLAY[0]), ("shin", SIT_SPLAY[1])):
            tr = sit["bones"][f"{bone}_{side}"]
            tr["rotation"] = [[k[0], k[1], k[2], k[3] + sg * roll] for k in tr["rotation"]]
    low = lowest_point(m, sit["bones"])
    for bone, tr in sit["bones"].items():
        if "position" in tr and (bone == "body" or bone.startswith("thigh")):
            tr["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in tr["position"]]
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    return m
