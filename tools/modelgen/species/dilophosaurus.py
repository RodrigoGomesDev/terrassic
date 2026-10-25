"""
Dilophosaurus wetherilli  (Sinemurian-Pliensbachian, Kayenta Formation, Arizona)

Reference:
  - Size (Welles 1984; Marsh & Rowe 2020 redescription): the largest known specimen ~7 m long, ~400 kg, about
    1.7 m at the hip; slender but strongly built, with long legs and a long tail.
  - Skull (~53 cm, Marsh & Rowe 2020): long and low; a deep notch between the premaxilla and the maxilla
    (the subnarial gap) with the premaxilla tip drooping below the rest of the upper jaw and an enlarged
    dentary tooth fitting up into the notch; the jaw strongly built (not the "weak jaw" of older ideas).
  - Crests: a pair of thin, semi-elliptical nasolacrimal crests running lengthwise from the nostril to above the
    eye, highest over the antorbital opening, pneumatic with grooves along their surface; probably a display
    structure, possibly larger in adults.
  - Neck long and S-curved; arms strong with four fingers (the fourth tiny) and large curved claws on I-III;
    three weight-bearing toes, a small hallux. Scaly: no frill and no venom spit (those are from the films).

v2x (2026-10-24, remaster at the T. rex v3 level): its own model (no longer the shared small-biped rig), modelled
at ~16 px = 1 m (one texture pixel = one vanilla pixel in game). The head is ~1.4x the real proportion. The
animation set is the small-biped one with its position keys scaled from the old ~10.5 px/m model; males carry
taller, brighter crests ("male_display" bone).
"""
import math
from rig import Model, lowest_point
import smalltheropod
from groundfit import fit_to_ground

ID = "dilophosaurus"
K = 1.55         # 16 px/m now / ~10.5 px/m of the old model: scales the shared animations' position keys


def pattern(model, tx, rgb, region):
    """Olive-brown scales with dark saddle bars across the back, a pale belly, a dark stripe through the eye;
    the crests banded with the grooves of their pneumatic surface and a bright rim."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("claw", "eye", "mouth", "tooth"):
        return rgb
    if tag == "crest":
        if tx.face == "up" or cube.name == "crest_display" or (P[1] > cube.to[1] - 1.01 and not getattr(cube, "capped", False)):
            return pal["crest_edge"].copy()
        groove = math.sin(P[2] * 2 * math.pi / 2.5 + P[1] * 0.9)
        return pal["crest"] * (0.72 if groove > 0.45 else 1.0)
    if tag == "limb" and cube.bone.startswith(("toes", "foot")) and tx.face != "down":
        return rgb * (0.86 if int(math.floor(P[1] + P[2] * 0.5)) % 2 == 0 else 1.0)   # scutes
    if tag in ("skin", "limb"):
        if (tx.i * 7 + tx.j * 3) % 7 == 0:
            rgb = rgb * 0.9                                                   # scales
        elif (tx.i * 5 + tx.j * 11) % 11 == 0:
            rgb = rgb * 1.07
        if region in ("dorsal", "flank") and cube.bone.startswith(("body", "tail", "neck")):
            bars = math.sin(P[2] * 2 * math.pi / 7.0 + 0.5 * math.sin(P[0] * 0.8))
            if region == "dorsal" and bars > 0.35:
                rgb = rgb * 0.66
            elif tx.cy > 0.45 and bars > 0.72:
                rgb = rgb * 0.8
    return rgb


PALETTE = {"dorsal": "#55573a", "flank": "#8a8555", "belly": "#ddd3ab", "limb": "#6f6c48", "limb_top": "#878452",
           "claw": "#24201b", "claw_base": "#2c2620", "claw_tip": "#6b6158",
           "crest": "#c8402a", "crest_edge": "#f2c44a",
           "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421", "eye": "#e0b43c", "pupil": "#140f0a"}
SEXES = {"male": {"crest": "#cc3a22", "crest_edge": "#f6cc48"},
         "female": {"crest": "#77704e", "crest_edge": "#a89c70", "dorsal": "#5e5a40"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
TEETH_UP = {"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}
TEETH_DN = {"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}

HIP = (28, 4)
TORSO = [("hips", (-5, 22, -2, 5, 34, 10), "skin"), ("belly", (-6, 20, -15, 6, 34, 0), "skin"),
         ("chest", (-5, 21, -21, 5, 33, -13), "skin"), ("shoulders", (-4, 31, -23, 4, 35, -15), "skin"),
         ("back", (-4, 34, -15, 4, 36, 8), "skin"), ("rump", (-4, 25, 10, 4, 33, 14), "skin")]
NECK = ([(31, -20), (36, -26), (41, -30), (45, -33)], [(7, 8), (6, 7), (5, 6)])
HEAD_PITCH = 4
# the crests as columns along the snout (z0, z1, top y in head px), a long low semi-ellipse peaking over the
# antorbital opening; the male's columns stand one px taller (male_display)
CREST = [(-13, -11, 2), (-11, -9, 4), (-9, -7, 5), (-7, -5, 6), (-5, -3, 6), (-3, -1, 5), (-1, 1, 4)]
MALE_CREST = {(-9, -7), (-7, -5), (-5, -3), (-3, -1)}
ARM_X, ARM = 6, ([(29, -18), (25, -15), (22, -20)], [(3, 3), (2, 3)])
LEG_X, LEG = 4, ([(28, 4), (18, -1), (8.5, 4), (1, 4)], [(7, 10, -0.5), (4, 5, 0.5, "limb"), (3, 3, 0.0, "limb")])
TAIL = ([(31, 12), (31.5, 24), (31, 36), (30, 48), (29, 60)], [(8, 8), (6, 6), (4, 5), (3, 3)])
DISPLAY_ARM = (0.5, -1.5)   # scale of the shared display arm pitch / roll
SIT_SPLAY = (10, -30)      # resting: thigh and shin roll out (deg)


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *HIP))
    for name, (x0, y0, z0, x1, y1, z1), tag in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name, tag=tag)

    # --- neck: long, S-curved
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2", "neck3"], "body", 0, pts, "-z", secs, overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck3", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (HEAD_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 2.5, az - 1))
    m.bone("male_display", "skull", (0, ay, az))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head (px of the head, ~1.4x): long and low, the subnarial notch with the drooping premaxilla
    B("skull", "cranium", (-3, -2.5, -4, 3, 2.5, 1), paint=MOUTH_DOWN)
    B("skull", "face", (-2.5, -2, -8, 2.5, 2, -4), paint=TEETH_UP)
    B("skull", "snout", (-2, -1, -11, 2, 1, -8), paint=TEETH_UP)           # the notch: the jaw edge rises
    B("skull", "premaxilla", (-1.5, -3, -14, 1.5, 0, -11), paint=TEETH_UP)  # the drooping tip
    B("jaw", "jaw", (-2, -4.5, -13, 2, -2.5, -1), paint=TEETH_DN)
    for sx in (1, -1):
        B("jaw", "notch_tooth", (min(0.5 * sx, 1.5 * sx), -2.5, -11, max(0.5 * sx, 1.5 * sx), -1.5, -10), tag="tooth")
    for z0, z1, top in CREST:                                                 # the paired thin crests
        for sx in (1, -1):
            xs = (min(0.5 * sx, 1.5 * sx), max(0.5 * sx, 1.5 * sx))
            c = B("skull", "crest", (xs[0], 0, z0, xs[1], top, z1), tag="crest")
            c.capped = (z0, z1) in MALE_CREST                                 # the male's cap carries the rim
            if c.capped:
                B("male_display", "crest_display", (xs[0], top, z0, xs[1], top + 1, z1), tag="crest")
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (3, ay + 0.8, az - 2.5), "r": 1.1, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 0.8, az - 2.5), "r": 1.1, "side": -1},
                 {"kind": "band_y", "bones": ["skull"], "pos": (0, ay + 0.8, 0), "r": 0.7, "mul": 0.6,
                  "zmin": az - 7, "zmax": az + 1}]

    # --- arms: strong, three big curved claws and a tiny fourth finger
    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", x, ARM[0], "-y", ARM[1], overlap=(1.0, 0.5))
        ey, ez = ch["end"]
        F = f"forearm_{side}"
        m.box(F, (x - 1, ey - 1.5, ez - 1), (x + 1, ey + 1.5, ez + 1), tag="limb", name="hand")
        for dy, L in ((1, 3), (0, 4), (-1, 3)):                                # digits I-III and their claws
            m.box(F, (x - 0.5, ey + dy - 0.5, ez - 1 - L), (x + 0.5, ey + dy + 0.5, ez - 1), tag="limb", name="finger")
            m.box(F, (x - 0.5, ey + dy - 0.5, ez - 3 - L), (x + 0.5, ey + dy + 0.5, ez - 1 - L), tag="claw",
                  name="hand_claw", paint={"axis": "-z"})
        m.box(F, (x - 0.5, ey - 2.5, ez - 2), (x + 0.5, ey - 1.5, ez - 1), tag="limb", name="finger_iv")
    m.sym(arm)

    # --- legs: long, three toes with claws, a small hallux behind
    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, LEG[0], "-y", LEG[1], overlap=(1.5, 1.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 2, by - 1, bz - 1.5), (x + 2, by, bz + 1.5), tag="limb", name="toe_pad")
        for dx, L in ((-2, 4), (-0.5, 6), (1, 5)):                            # digits II, III, IV
            a = x + dx * sx
            m.box(T, (min(a, a + sx), by - 1, bz - 1.5 - L), (max(a, a + sx), by, bz - 1.5), tag="limb", name="toe")
            m.box(T, (min(a, a + sx), by - 1, bz - 2.5 - L), (max(a, a + sx), by, bz - 1.5 - L), tag="claw",
                  name="toe_claw")
        hx = x - 1 * sx
        m.box(T, (min(hx, hx + sx), by, bz + 1.5), (max(hx, hx + sx), by + 1, bz + 2.5), tag="claw", name="hallux")
    m.sym(leg)

    # --- tail: long, tapering
    names = [f"tail{i+1}" for i in range(len(TAIL[1]))]
    m.chain(names, "body", 0, TAIL[0], "+z", TAIL[1], overlap=(1.0, 1.0))

    P = {"tail_secs": TAIL[1], "hip": HIP, "anim_speed": 0.9, "display": True, "sit": {"drop": 15, "neck": 8}}
    smalltheropod.animations(m, P)
    for a in m.animations:      # position keys of the shared set were written for the old ~10.5 px/m model
        if a["name"].split(".")[-1] not in ("sit", "knocked_out", "wake"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    sit = next(a for a in m.animations if a["name"].endswith(".sit"))   # folded legs beside the belly
    for side, sg in (("l", 1), ("r", -1)):
        for bone, roll in (("thigh", SIT_SPLAY[0]), ("shin", SIT_SPLAY[1])):
            tr = sit["bones"][f"{bone}_{side}"]
            tr["rotation"] = [[k[0], k[1], k[2], k[3] + sg * roll] for k in tr["rotation"]]
    low = lowest_point(m, sit["bones"])
    for bone, tr in sit["bones"].items():
        if "position" in tr and (bone == "body" or bone.startswith("thigh")):
            tr["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in tr["position"]]
    disp = next(a for a in m.animations if a["name"].endswith(".display"))   # arms held out from the chest
    for side, sg in (("l", 1), ("r", -1)):
        disp["bones"][f"arm_{side}"]["rotation"] = [[k[0], k[1] * DISPLAY_ARM[0], k[2], k[3] * DISPLAY_ARM[1]]
                                                    for k in disp["bones"][f"arm_{side}"]["rotation"]]
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    return m
