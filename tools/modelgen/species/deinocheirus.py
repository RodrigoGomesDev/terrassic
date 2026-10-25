"""
Deinocheirus mirificus  (Late Cretaceous, Maastrichtian; Nemegt Formation, Mongolia)

Reference:
  - Size (Osmólska & Roniewicz 1970; Lee et al. 2014; Wikipedia): the "terrible hand", known for 45 years only from
    a pair of 2.4 m arms; the 2014 skeletons showed the biggest ornithomimosaur, ~11 m and ~6.4 t.
  - Skull (Lee et al. 2014): ~1 m long, low and toothless, the bill long and broad, flaring into a spoon-like
    "duck bill" at the tip; a very deep lower jaw; small eyes set high; the nostrils high on the snout.
  - Back: very tall neural spines along the back and over the hips, rising toward the sacrum, made a hump or sail
    braced by ligaments.
  - Arms: huge, with three fingers of near equal length ending in blunt, gently curved claws (for digging and
    gathering plants, not killing); hind legs short and stout for its size, the foot with broad, blunt, hoof-like
    claws for soft river bottoms; the tail ending in fused vertebrae (a pygostyle) that probably held a fan of
    feathers.
  - Diet: over a thousand gastroliths and fish scales in its belly: an omnivore wading the river margins.
  - Colour unknown; kept from the old model: dusty grey-brown with a pale underside and darker mottling, a dark
    hump, a black-and-white tail fan; males with a taller, redder hump crest, females plainer.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared large-theropod rig), built
with the construction of the Therizinosaurus remaster at ~16 px = 1 m. The head is ~1.3x the real proportion. The
double-arm swipe, the "graze" and the "fish" scoop are kept.
"""
import math
from paint import vnoise
from rig import Model, track, keys, lowest_point, add_saddle
from groundfit import fit_to_ground
import large_theropod

ID = "deinocheirus"
K = 1.8  # position keys of the shared 1x set are scaled by this


def pattern(model, tx, rgb, region):
    """Dusty filament coat with darker mottling over the back and faint rings down the neck; the hump darker with the
    spines showing under the skin; the bill with a pale nail at the tip; feather fans with black and white bars."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("eye", "mouth", "saddle"):
        return rgb
    if tag == "claw":
        return rgb * (0.92 if (tx.i + 2 * tx.j) % 5 == 0 else 1.0)
    if tag == "beak":
        if tx.face == "up" and cube.name == "bill_tip" and P[2] < cube.frm[2] + 2.0:
            return pal["beak_tip"].copy()                                   # the pale nail at the tip of the bill
        return rgb * (0.82 if tx.face in ("east", "west") and tx.cy < 0.3 else 1.0)
    if tag == "hump":
        n = vnoise(P[0] / 2.0, P[1] / 2.0, P[2] / 2.0, 83)
        col = pal["hump"] * (0.88 + 0.24 * n)
        if int(math.floor(P[2])) % 4 == 0:
            col = col * 0.86                                                # the spines under the skin
        return col
    if tag == "feather":
        ax = 1 if cube.name.startswith("arm_fan") else 2
        u = (P[ax] - cube.frm[ax]) / max(1.0, cube.to[ax] - cube.frm[ax])
        if ax == 2 and (u > 0.72 or 0.3 < u < 0.42):
            return pal["feather_tip"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)
        if ax == 1 and (u < 0.2 or 0.55 < u < 0.67):
            return pal["feather_tip"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)
        return rgb
    if tag == "limb" and cube.bone.startswith("toes") and tx.face != "down":
        return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)
    if tag == "skin":
        n = vnoise(P[0] / 1.5, P[1] / 4.0, P[2] / 1.5, 89)                   # filament streaks
        rgb = rgb * (0.86 + 0.26 * n)
        if region == "dorsal" and math.sin(P[2] * 0.35) * math.sin(P[0] * 0.5 + P[1] * 0.12) > 0.5:
            rgb = pal["mottle"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)
        if cube.bone.startswith("neck") and region != "belly" and math.sin(P[1] * 0.7 + P[2] * 0.25) > 0.8:
            rgb = rgb * 0.86                                                # faint rings down the neck
    return rgb


PALETTE = {"dorsal": "#6a6256", "flank": "#938a78", "belly": "#e0d8c4", "mottle": "#4e4840", "hump": "#4a423a",
           "limb": "#746c5e", "limb_top": "#847c6c", "claw": "#3a3630", "claw_base": "#3a3630", "claw_tip": "#8a847a",
           "feather": "#2a2624", "feather_tip": "#ece8e0", "beak": "#50483e", "beak_tip": "#d8c8a0",
           "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421", "eye": "#c0a040", "pupil": "#17110c",
           "saddle": "#7a4f2e"}
SEXES = {"male": {"hump": "#6a3a2a", "dorsal": "#5e5648", "feather": "#1e1a18", "feather_tip": "#f4f0e8"},
         "female": {"hump": "#5a5048", "flank": "#9c9484", "feather": "#4a4440", "feather_tip": "#d0ccc0"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (46, 10)
# a deep barrel on wide hips, the chest the huge arms hang from
TORSO = [("hips", (-12, 36, -6, 12, 58, 20)), ("belly", (-14, 28, -30, 14, 58, -2)),
         ("belly_low", (-10, 25, -26, 10, 28, -6)), ("chest", (-12, 34, -46, 12, 60, -26)),
         ("shoulders", (-9, 52, -52, 9, 63, -42)), ("pubic_boot", (-3, 22, -2, 3, 28, 6)),
         ("pubis", (-2, 28, 0, 2, 36, 6))]
# the hump: tall neural spines under a thick ridge, rising to the sacrum: (z0, z1, height above y 57)
HUMP_BASE = 57
HUMP = [(-40, -32, 6), (-32, -24, 9), (-24, -16, 12), (-16, -8, 15), (-8, 0, 18), (0, 8, 19), (8, 14, 16), (14, 19, 10),
        (19, 23, 4)]
NECK = ([(60, -48), (68, -58), (74, -68), (78, -78)], [(13, 13), (11, 11), (9, 9)])
TAIL = ([(52, 20), (50, 36), (47, 50), (44, 62), (41, 72)], [(16, 16), (12, 12), (8, 8), (5, 5)])
ARM_X = 13
ARM = ([(56, -46), (40, -48), (28, -53)], [(6, 7), (5, 5)])
# blunt, gently curved claws of near equal length (x0, x1 across the hand, length)
CLAWS = [(-2.5, -0.5, 6), (-0.5, 1.5, 6), (1.5, 2.5, 5)]
LEG_X = 11
LEG = ([(46, 10), (28, 2), (12, 8), (3, 6)], [(12, 18, -1), (9, 10, 1, "limb"), (8, 7, 0, "limb")])
SIT = (26, 60, -115, 60, -6, {"tail1": (8, 0, 0), "tail2": (4, 0, 0), "neck1": (-8, 0, 0), "skull": (4, 0, 0),
                              "arm_l": (10, 0, 0), "arm_r": (10, 0, 0)})
SIT_SPLAY = (18, -34)
SKULL_TILT = -4


def extra_anims(m):
    # the attack: not a bite but a slow heavy swipe of both arms across the front
    m.animations = [a for a in m.animations if not a["name"].endswith(".attack")]
    m.anim("attack", 1.1, False, {
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.35, -80, 0, -40), (0.6, -40, 0, 30), (1.1, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.4, -80, 0, 40), (0.65, -40, 0, -30), (1.1, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.35, 30, 0, 0), (0.6, 0, 0, 0), (1.1, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.4, 30, 0, 0), (0.65, 0, 0, 0), (1.1, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.35, 5, 8, 0), (0.6, -4, -10, 0), (1.1, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.35, 10, 0, 0), (0.6, -6, 0, 0), (1.1, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.35, -16, 0, 0), (0.7, -16, 0, 0), (1.1, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.35, 0, -10, 0), (0.6, 0, 12, 0), (1.1, 0, 0, 0)])),
    })
    # grazing: the bill goes down to the ground and sweeps side to side
    jk = [(0, 0, 0, 0), (0.7, 0, 0, 0)]
    for k in range(5):
        t0 = 0.9 + k * 0.3
        jk += [(t0, -12, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(2.8, 0, 0, 0)]
    m.anim("graze", 2.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.7, -48, 0, 0), (2.3, -48, 0, 0), (2.8, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.7, -26, 0, 0), (2.3, -26, 0, 0), (2.8, 0, 0, 0)])),
        "neck3": track(rot=keys([(0, 0, 0, 0), (0.7, -16, 0, 0), (2.3, -16, 0, 0), (2.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.7, -12, 0, 0), (1.1, -12, 0, 10), (1.5, -12, 0, -10), (1.9, -12, 0, 8), (2.3, -12, 0, 0), (2.8, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
        "body": track(rot=keys([(0, 0, 0, 0), (0.7, -20, 0, 0), (2.3, -20, 0, 0), (2.8, 0, 0, 0)])),
    })
    # fishing: the body leans over the water, both arms scoop forward and down, then lift together to the bill
    m.anim("fish", 2.4, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.5, -8, 0, 0), (1.3, -8, 0, 0), (1.8, -2, 0, 0), (2.4, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, -20, 0, 0), (1.3, -20, 0, 0), (1.8, 6, 0, 0), (2.4, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.5, -6, 0, 0), (1.3, -6, 0, 0), (1.8, 8, 0, 0), (2.4, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (1.6, 0, 0, 0), (1.9, -18, 0, 0), (2.1, -4, 0, 0), (2.4, 0, 0, 0)])),
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.5, -60, 0, -10), (0.9, -30, 0, -20), (1.3, -60, 0, -10), (1.8, -100, 0, -5), (2.4, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.5, -60, 0, 10), (0.9, -30, 0, 20), (1.3, -60, 0, 10), (1.8, -100, 0, 5), (2.4, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.5, 20, 0, 0), (0.9, 40, 0, 0), (1.3, 20, 0, 0), (1.8, 60, 0, 0), (2.4, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.5, 20, 0, 0), (0.9, 40, 0, 0), (1.3, 20, 0, 0), (1.8, 60, 0, 0), (2.4, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.5, 8, 0, 0), (1.3, 8, 0, 0), (2.4, 0, 0, 0)])),
    })


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)
    for z0, z1, hh in HUMP:                                                # the hump over the back and hips
        m.box("body", (-3, HUMP_BASE, z0), (3, HUMP_BASE + hh, z1), tag="hump", name="hump")
    m.box("body", (-5, HUMP_BASE - 1, -34), (5, HUMP_BASE + 5, 20), tag="hump", name="hump_base")   # the thick ligament base
    m.bone("male_display", "body", (0, HUMP_BASE, 0))
    for z0, z1, hh in HUMP[1:-1]:
        m.box("male_display", (-2, HUMP_BASE + hh - 1, z0), (2, HUMP_BASE + hh + 3, z1), tag="hump", name="hump_crest")

    # --- neck: long, curving forward and up, a short mane of filaments down its back
    pts, secs = NECK
    names = ["neck1", "neck2", "neck3"]
    neck = m.chain(names, "body", 0, pts, "-z", secs, overlap=(3.0, 2.0))
    for seg, (w, hh) in zip(neck["segments"], secs):
        y0, z0 = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-1.5, y0 + hh / 2 - 1, z0 - L), (1.5, y0 + hh / 2 + 1, z0), tag="feather", name="neck_mane")
    ay, az = neck["end"]
    m.bone("head", "neck3", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (SKULL_TILT - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 2, az - 1))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head: long and low, the bill flaring into a spoon at the tip, a very deep lower jaw
    B("skull", "cranium", (-4, -2, -6, 4, 4, 1), paint=MOUTH_DOWN)
    B("skull", "face", (-3, -2, -12, 3, 3, -6), paint=MOUTH_DOWN)
    B("skull", "bill", (-3, -1.5, -18, 3, 1.5, -12), tag="beak", paint=MOUTH_DOWN)
    B("skull", "bill_tip", (-4, -1.5, -22, 4, 0.5, -18), tag="beak", paint=MOUTH_DOWN)
    B("jaw", "jaw_back", (-3.5, -6, -12, 3.5, -2, -1), paint=MOUTH_UP)
    B("jaw", "jaw_mid", (-3, -4.5, -18, 3, -1.5, -12), tag="beak", paint=MOUTH_UP)
    B("jaw", "jaw_tip", (-4, -3.5, -22, 4, -1.5, -18), tag="beak", paint=MOUTH_UP)
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (4, ay + 2, az - 3.5), "r": 1.0, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-4, ay + 2, az - 3.5), "r": 1.0, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": (2.5, ay + 2.5, az - 9), "r": 0.8, "rx": 1.0, "mul": 0.5, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": (-2.5, ay + 2.5, az - 9), "r": 0.8, "rx": 1.0, "mul": 0.5, "side": -1}]

    # --- arms: huge, a fan of feathers on the forearm, three fingers with blunt claws on a hand bone
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, overlap=(2.0, 1.0))
        fy, fz = ch["segments"][1]["unposed"]
        L = int(round(ch["segments"][1]["len"]))
        a = x + 2.5 * sx                                                   # in the forearm's frame -y runs down the arm
        m.box(f"forearm_{side}", (min(a, a + sx), fy - L, fz + 1), (max(a, a + sx), fy - 1, fz + 7), tag="feather",
              name="arm_fan")
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        H = f"hand_{side}"
        m.box(H, (x - 2.5, by - 3, bz - 1.5), (x + 2.5, by + 1, bz + 1.5), tag="limb", name="hand")
        # three long fingers of near equal length, each with a blunt claw curving back a little
        for x0, x1, Lc in CLAWS:
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            m.box(H, (a, by - 3 - Lc, bz - 1.5), (b, by - 3, bz + 0.5), tag="limb", name="finger")
            m.box(H, (a, by - 6 - Lc, bz - 1), (b, by - 3 - Lc, bz + 1), tag="claw", name="claw", paint={"axis": "-y"})
    m.sym(arm)

    # --- legs: short and stout for its size, three broad toes with blunt hoof-like claws
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(3.0, 1.0))
        ty, tz = ch["segments"][0]["unposed"]
        m.box(f"thigh_{side}", (x - 6.5, ty - 13, tz - 10), (x + 6.5, ty + 2, tz + 8), name="thigh_muscle")
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 5, by - 3, bz - 2), (x + 5, by, bz + 3), tag="limb", name="toe_pad")
        for name, (x0, x1), length in (("toe_ii", (-5, -2), 6), ("toe_iii", (-2, 2), 8), ("toe_iv", (2, 5), 6)):
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            m.box(T, (a, by - 3, bz - 2 - length), (b, by, bz - 2), tag="limb", name=name)
            m.box(T, (a, by - 3, bz - 4 - length), (b, by - 1, bz - 2 - length), tag="claw", name="hoof")
    m.sym(leg)

    # --- tail: ends in a pygostyle carrying a fan of feathers
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 2.0))
    t1y, t1z = tail["segments"][0]["unposed"]
    m.box("tail1", (-7, t1y - 12, t1z - 2), (7, t1y - 5, t1z + 10), name="caudofemoralis")
    sg = tail["segments"][3]
    y0, z0 = sg["unposed"]
    L = int(round(sg["len"]))
    m.box("tail4", (-5, y0, z0 + 1), (5, y0 + 1, z0 + L + 6), tag="feather", name="fan")
    m.box("tail4", (-8, y0 - 1, z0 + 3), (8, y0, z0 + L + 3), tag="feather", name="fan_wide")

    add_saddle(m, "body", 64, -52, -36, 14, 12.5, flap=10)
    large_theropod.animations(m, SIT)
    extra_anims(m)
    for a in m.animations:
        if a["name"].split(".")[-1] in ("idle", "walk", "run", "roar", "beg", "eat", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    sit = next(a for a in m.animations if a["name"].endswith(".sit"))
    for side, s in (("l", 1), ("r", -1)):
        for bone in ("thigh", "shin"):
            tr = sit["bones"][f"{bone}_{side}"]
            tr["rotation"] = [[k[0], k[1], k[2], k[3] + s * SIT_SPLAY[0 if bone == "thigh" else 1]] for k in tr["rotation"]]
    low = lowest_point(m, sit["bones"])
    for bone, tr in sit["bones"].items():
        if "position" in tr and (bone == "body" or bone.startswith("thigh")):
            tr["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in tr["position"]]
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    fit_to_ground(m, "graze", ("neck1", "neck2", "neck3", "skull", "body"))
    fit_to_ground(m, "fish", ("neck1", "skull", "body", "arm_l", "arm_r", "forearm_l", "forearm_r"))
    return m
