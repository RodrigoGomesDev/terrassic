"""
Therizinosaurus cheloniformis  (Late Cretaceous, Maastrichtian; Nemegt Formation, Mongolia)

Reference:
  - Size (Maleev 1954; Barsbold 1976; Zanno 2010; Paul 2010; Wikipedia): a giant herbivorous theropod of 9-10 m and
    ~3-5 t, known from arms, claws and hind-limb parts; the rest follows its relatives (Nothronychus, Segnosaurus,
    Erlikosaurus). First taken for a giant turtle ("cheloniformis") from its claws.
  - Claws: the longest of any animal, up to 52 cm of bone on digit I (close to 1 m with the horny sheath), straight-
    ish, flattened from side to side and only gently curved, three per hand, I longest, III shortest; long, strong
    arms (humerus ~0.76 m).
  - Body (therizinosaurid plan): a small head with a toothless beak in front and small leaf-shaped cheek teeth
    behind; a long neck; the trunk carried steeply tilted up toward the shoulders; a broad pelvis with the pubis
    swept back under a deep pot belly; short stout hind legs on a short broad foot with FOUR weight-bearing toes and
    short claws; a short tail.
  - Integument (Beipiaosaurus, Jianchangosaurus): a shaggy coat of long filaments, longer quills on the back and
    neck, a fan of feathers on the arm.
  - A high browser that pulled branches down with its claws; the claws were for reach and defence.
  - Colour unknown; kept from the old model: dark shaggy brown with a pale belly and cream claws; males darker with a
    rusty neck ruff, females dun.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared large-theropod rig), built
with the construction of the Spinosaurus remaster at ~15 px = 1 m. The head is ~1.4x the real proportion. The
claw slash and the high browse ("graze") are kept.
"""
import math
from paint import vnoise
from rig import Model, track, keys, lowest_point, add_saddle
from groundfit import fit_to_ground
import large_theropod

ID = "therizinosaurus"
K = 1.8  # position keys of the shared 1x set are scaled by this


def pattern(model, tx, rgb, region):
    """Shaggy plumage: vertical streaks of light and dark like hanging filaments, quills with pale tips, a rusty
    ruff; the beak dark; cream keratin claws with a darker base; scutes on the toes."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("eye", "mouth", "saddle"):
        return rgb
    if tag == "claw":
        return rgb * (0.92 if (tx.i + 2 * tx.j) % 5 == 0 else 1.0)            # keratin grain
    if tag == "beak":
        return rgb * (0.82 if tx.face in ("east", "west") and tx.cy < 0.3 else 1.0)
    if tag == "feather":
        ax = 1 if cube.name.startswith(("arm_fan", "quill")) else 2
        u = (P[ax] - cube.frm[ax]) / max(1.0, cube.to[ax] - cube.frm[ax])
        if (ax == 1 and u < 0.2) or (ax == 2 and u > 0.8):
            return pal["feather_tip"] * (0.94 if (tx.i + tx.j) % 2 else 1.0)
        n = vnoise(P[0] / 1.2, P[1] / 4.0, P[2] / 1.2, 61)
        return rgb * (0.82 + 0.34 * n)
    if tag == "ruff":
        n = vnoise(P[0] / 1.5, P[1] / 3.0, P[2] / 1.5, 67)
        return pal["ruff"] * (0.85 + 0.3 * n)
    if tag == "limb" and cube.bone.startswith("toes") and tx.face != "down":
        return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)
    if tag == "skin":
        n = vnoise(P[0] / 1.3, P[1] / 5.0, P[2] / 1.3, 71)                    # shaggy streaks
        rgb = rgb * (0.82 + 0.34 * n)
        if region == "belly":
            rgb = rgb * 1.04
    return rgb


PALETTE = {"dorsal": "#4e4034", "flank": "#7a6448", "belly": "#d4c4a4", "limb": "#5e4e40", "limb_top": "#6e5c48",
           "claw": "#d8ccb0", "claw_base": "#8a7a60", "claw_tip": "#f0e8d8",
           "feather": "#3a3028", "feather_tip": "#c8b890", "ruff": "#a04a28",
           "beak": "#4a4036", "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
           "eye": "#c89a30", "pupil": "#17110c", "saddle": "#7a4f2e"}
SEXES = {"male": {"dorsal": "#423428", "feather": "#2a2220", "feather_tip": "#e8d8a8", "ruff": "#b04a24"},
         "female": {"dorsal": "#5e4e40", "flank": "#8a7458", "feather": "#5a4a3c", "feather_tip": "#b8a888",
                    "ruff": "#8a6a4c"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (46, 8)
# the trunk rises steeply to the shoulders; a deep pot belly hangs between the broad hips
TORSO = [("hips", (-13, 36, -6, 13, 58, 18)), ("belly", (-15, 26, -26, 15, 58, -2)),
         ("belly_low", (-11, 23, -22, 11, 26, -6)), ("chest", (-12, 40, -40, 12, 66, -22)),
         ("shoulders", (-9, 58, -46, 9, 72, -34)), ("pubic_boot", (-3, 20, -2, 3, 26, 6)),
         ("pubis", (-2, 26, 0, 2, 36, 6))]
# shaggy coat of quills: (z0, z1, y base, height) along the back
MANE = [(-44, -36, 72, 4), (-36, -28, 67, 5), (-28, -20, 64, 5), (-20, -10, 59, 5), (-10, 2, 58, 4), (2, 14, 58, 3)]
NECK = ([(66, -44), (74, -51), (81, -57), (86, -64)], [(13, 13), (11, 11), (9, 9)])
TAIL = ([(52, 18), (50, 33), (47, 46), (44, 58), (41, 70)], [(16, 16), (12, 12), (8, 8), (5, 5)])
ARM_X = 12
ARM = ([(60, -42), (44, -45), (30, -50)], [(6, 7), (5, 5)])
# claws (x0, x1 across the hand, length): digit I the longest, on the inside
CLAWS = [(-2.5, -0.5, 16), (-0.5, 1.5, 13), (1.5, 2.5, 10)]
LEG_X = 11
LEG = ([(46, 8), (28, 0), (12, 6), (3, 4)], [(12, 18, -1), (9, 10, 1, "limb"), (8, 7, 0, "limb")])
SIT = (26, 60, -115, 60, -6, {"tail1": (8, 0, 0), "tail2": (4, 0, 0), "neck1": (-8, 0, 0), "skull": (4, 0, 0),
                              "arm_l": (10, 0, 0), "arm_r": (10, 0, 0)})
SIT_SPLAY = (18, -34)
SKULL_TILT = -8


def extra_anims(m):
    # replace the rig's bite with a claw slash: both arms rise, then rake down and across
    m.animations = [a for a in m.animations if not a["name"].endswith(".attack")]
    m.anim("attack", 0.9, False, {
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.25, -110, 0, -25), (0.45, 30, 0, 10), (0.9, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.3, -110, 0, 25), (0.5, 30, 0, -10), (0.9, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.25, 40, 0, 0), (0.45, -10, 0, 0), (0.9, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.3, 40, 0, 0), (0.5, -10, 0, 0), (0.9, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.25, 6, 0, 0), (0.45, -5, 0, 0), (0.9, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.25, 0, 0.5 * K, 1 * K), (0.45, 0, -0.5 * K, -2 * K), (0.9, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.25, 10, 0, 0), (0.45, -8, 0, 0), (0.9, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.25, -20, 0, 0), (0.5, -24, 0, 0), (0.7, 0, 0, 0), (0.9, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.25, -4, 0, 0), (0.45, 5, 0, 0), (0.9, 0, 0, 0)])),
    })
    # browsing: the neck reaches up, the claws hook a branch down to the beak, and it chews
    jk = [(0, 0, 0, 0), (0.9, 0, 0, 0)]
    for k in range(5):
        t0 = 1.1 + k * 0.3
        jk += [(t0, -14, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(3.0, 0, 0, 0)]
    m.anim("graze", 3.0, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, 16, 0, 0), (0.9, 8, 0, 0), (2.6, 8, 0, 0), (3.0, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.5, 8, 0, 0), (2.6, 4, 0, 0), (3.0, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.5, 10, 0, 0), (0.9, -6, 0, 0), (2.6, -6, 0, 0), (3.0, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.5, -120, 0, -15), (0.9, -60, 0, -10), (2.6, -60, 0, -10), (3.0, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.5, -120, 0, 15), (0.9, -60, 0, 10), (2.6, -60, 0, 10), (3.0, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.5, 20, 0, 0), (0.9, 50, 0, 0), (2.6, 50, 0, 0), (3.0, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.5, 20, 0, 0), (0.9, 50, 0, 0), (2.6, 50, 0, 0), (3.0, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.5, 4, 0, 0), (2.6, 3, 0, 0), (3.0, 0, 0, 0)])),
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
    for z0, z1, yb, hh in MANE:                                            # the shaggy mantle down the back
        m.box("body", (-7, yb - 1, z0), (7, yb + hh, z1), tag="feather", name="mantle")

    # --- neck: long, rising, a coat of long filaments down its back
    pts, secs = NECK
    names = ["neck1", "neck2", "neck3"]
    neck = m.chain(names, "body", 0, pts, "-z", secs, overlap=(3.0, 2.0))
    for seg, (w, hh) in zip(neck["segments"], secs):
        y0, z0 = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-2, y0 + hh / 2 - 1, z0 - L), (2, y0 + hh / 2 + 2, z0), tag="feather", name="neck_quills")
    y1, z1 = neck["segments"][0]["unposed"]
    m.bone("male_display", "neck1", (0, y1, z1))
    m.box("male_display", (-7.5, y1 - 7, z1 - 9), (7.5, y1 + 7, z1 - 2), tag="ruff", name="ruff")
    ay, az = neck["end"]
    m.bone("head", "neck3", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (SKULL_TILT - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 1.5, az - 1))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head: small and long, a rounded braincase, a narrow toothless beak turned down at the tip
    B("skull", "cranium", (-3.5, -1.5, -5, 3.5, 4.5, 1), paint=MOUTH_DOWN)
    B("skull", "brow", (-3, 4.5, -5, 3, 5.5, 0))
    B("skull", "face", (-2.5, -1.5, -10, 2.5, 3.5, -5), paint=MOUTH_DOWN)
    B("skull", "beak", (-1.5, -1.5, -14, 1.5, 2.5, -10), tag="beak", paint=MOUTH_DOWN)
    B("skull", "beak_hook", (-1, -2.5, -15, 1, 1.5, -14), tag="beak")
    B("jaw", "lower_jaw", (-2.5, -3.5, -10, 2.5, -1.5, -1), paint=MOUTH_UP)
    B("jaw", "lower_beak", (-1.5, -3.5, -14, 1.5, -1.5, -10), tag="beak", paint=MOUTH_UP)
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (3.5, ay + 2.5, az - 3), "r": 1.1, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-3.5, ay + 2.5, az - 3), "r": 1.1, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": (2.5, ay + 2, az - 9), "r": 0.8, "rx": 1.0, "mul": 0.5, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": (-2.5, ay + 2, az - 9), "r": 0.8, "rx": 1.0, "mul": 0.5, "side": -1}]

    # --- arms: long and strong, a fan of feathers on the forearm, the three giant claws on a hand bone
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
        m.box(H, (x - 2.5, by - 5, bz - 1.5), (x + 2.5, by + 1, bz + 1.5), tag="limb", name="hand")
        # each claw hangs from the hand and curves back gently: three stacked pieces stepping back, then the tip
        for x0, x1, Lc in CLAWS:
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            y = by - 5
            steps = (round(Lc * 0.4), round(Lc * 0.35), Lc - round(Lc * 0.4) - round(Lc * 0.35))
            for k, ln in enumerate(steps):
                m.box(H, (a, y - ln, bz - 1.5 + k), (b, y, bz + 0.5 + k), tag="claw", name="claw", paint={"axis": "-y"})
                y -= ln
    m.sym(arm)

    # --- legs: short and stout, a short broad foot on four weight-bearing toes with short claws
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(3.0, 1.0))
        ty, tz = ch["segments"][0]["unposed"]
        m.box(f"thigh_{side}", (x - 6.5, ty - 13, tz - 10), (x + 6.5, ty + 2, tz + 8), name="thigh_coat")
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 5, by - 3, bz - 2), (x + 5, by, bz + 3), tag="limb", name="toe_pad")
        for name, (x0, x1), length in (("toe_i", (-5, -3), 4), ("toe_ii", (-3, 0), 7), ("toe_iii", (0, 3), 7),
                                       ("toe_iv", (3, 5), 6)):
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            m.box(T, (a, by - 3, bz - 2 - length), (b, by, bz - 2), tag="limb", name=name)
            m.box(T, (a, by - 3, bz - 4 - length), (b, by - 1, bz - 2 - length), tag="claw", name="toe_claw")
    m.sym(leg)

    # --- tail: short, with a tuft of long feathers at the end
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 2.0))
    t1y, t1z = tail["segments"][0]["unposed"]
    m.box("tail1", (-7, t1y - 12, t1z - 2), (7, t1y - 5, t1z + 10), name="caudofemoralis")
    for k in (1, 2, 3):
        sg = tail["segments"][k]
        y0, z0 = sg["unposed"]
        L = int(round(sg["len"]))
        hh = tsecs[k][1] / 2
        m.box(f"tail{k+1}", (-2, y0 + hh - 1, z0), (2, y0 + hh + 2, z0 + L), tag="feather", name="tail_quills")
    ty, tz = tail["end"]
    m.box("tail4", (-3, ty - 3, tz - 1), (3, ty + 3, tz + 6), tag="feather", name="tail_tuft")

    add_saddle(m, "body", 63, -14, 2, 16, 15, flap=10)
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
    return m
