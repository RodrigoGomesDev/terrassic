"""
Corythosaurus casuarius  (Late Cretaceous, Campanian; Dinosaur Park Formation, Alberta)

Reference:
  - Size (Brown 1914; Evans et al. 2009; Wikipedia): ~9 m long, ~3-4 t; dozens of skulls of every age, many
    complete skeletons, several with skin (AMNH 5240, ROM 845).
  - Crest (Evans 2006; Weishampel 1981): a tall, thin, rounded "Corinthian helmet" made by the premaxillae and the
    nasals, rising from just behind the bill over the eyes and ending at the back of the skull; it is hollow, the
    nasal passages looping inside it into a resonating chamber for deep calls. It grows with age and is bigger in
    some adults (thought to be males), whose crest reaches higher and further back.
  - Head: short and deep for a hadrosaur, a narrower bill than the Edmontosaurus, the face below the crest short.
  - Body (lambeosaurines): tall neural spines over the back and hips make a high ridge; a deep body, light
    forelimbs with the fingers in a hoofed mitten, long hind legs with three hoofed toes, a tall flat-sided tail.
  - Skin (Bell 2014): small polygonal tubercles, rows of larger conical feature scales low on the flanks; a low
    row of knobs down the midline of the back.
  - Colour unknown; kept from the old model: olive green with sandy flanks and a dark back; the crest red with a
    pale rim on males, dull brown on females.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared hadrosaur rig), built with
the same hadrosaurid construction as the Maiasaura (9 m, 16 px = 1 m) with its own head and the high spine ridge.
The head is ~1.2x the real proportion. Males carry the taller helmet ("male_display").
"""
import math
from rig import Model, wave, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "corythosaurus"
K = 2.0                     # the archetype's moving poses were written for the ~1x hadrosaur rig
HEAD = 1.2


def _cell(P, size):
    a, b, c = P[0] / size, P[1] / size, P[2] / size
    row = math.floor(b)
    a += 0.5 * (row % 2)
    c += 0.5 * (row % 2)
    fa, fb, fc = a - math.floor(a), b - math.floor(b), c - math.floor(c)
    edge = min(fa, 1 - fa, fb, 1 - fb, fc, 1 - fc)
    h = (math.floor(a) * 73856093 ^ row * 19349663 ^ math.floor(c) * 83492791) & 1023
    return edge, h


def pattern(model, tx, rgb, region):
    """Small polygonal tubercles with rows of bigger conical scales low on the flanks (AMNH 5240), faint dark bars
    over the back, a dark midline; the helmet with a pale rim along its front and top and darker growth lines."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("claw", "eye", "mouth", "beak", "saddle"):
        return rgb
    if tag == "frill":
        return pal["frill"] * (1.1 if tx.face == "up" else 1.0)
    if tag == "crest":
        if tx.face == "north" or (tx.face == "up" and cube.name in ("crest_top", "crest_tip")):
            return pal["crest_band"].copy()                                   # the pale rim
        if math.sin(P[1] * 1.8 + P[2] * 0.4) > 0.75:
            return rgb * 0.82
        return rgb
    if tag in ("skin", "limb"):
        if tag == "limb" and cube.bone.startswith(("toes", "hand")) and tx.face != "down":
            return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)
        if region == "dorsal" and tx.face == "up" and abs(P[0]) < 1.5 and not cube.bone.startswith(("skull", "jaw")):
            return pal["spine"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)
        if region in ("dorsal", "flank") and tag == "skin" and math.sin(P[2] * 0.75 + 0.6 * math.sin(P[1] * 0.5)) > 0.8:
            rgb = rgb * 0.84                                                  # faint dark bars
        if region == "flank" and tx.cy < 0.45 and int(math.floor(P[2] / 2.5)) % 2 == 0 \
                and int(math.floor(P[1] / 2.5)) % 2 == 0:
            return pal["flank_knob"] * (0.92 if (tx.i + tx.j) % 2 else 1.0)  # rows of conical feature scales
        edge, _h = _cell(P, 1.5)
        if edge < 0.13:
            rgb = rgb * 0.93                                                  # polygonal tubercles
    return rgb


PALETTE = {"dorsal": "#3c5038", "flank": "#8c9a60", "belly": "#e2dcb8", "spine": "#2e3e2a", "frill": "#2e3e2a",
           "flank_knob": "#a4b070", "limb": "#5a6a48", "limb_top": "#6c7e56",
           "claw": "#38312a", "claw_base": "#38312a", "beak": "#463c32", "crest": "#b8402f", "crest_band": "#e8c27a",
           "spot": "#2e3e2a", "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622", "eye": "#b8862c", "pupil": "#140f0a"}
SEXES = {"male": {"dorsal": "#304430", "crest": "#c4402a", "crest_band": "#f0d080"},
         "female": {"dorsal": "#4e5a3c", "flank": "#9aa270", "crest": "#7a6248", "crest_band": "#b8a888"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (40, 12)                                      # hip joint
TORSO = [("hips", (-11, 26, -2, 11, 46, 24)), ("belly", (-13.5, 20, -26, 13.5, 43, 0)),
         ("chest", (-10, 21, -40, 10, 37, -24)), ("belly_low", (-10, 17, -32, 10, 20, -4)),
         ("back", (-7, 43, -24, 7, 46, -2)), ("sacrum", (-6, 46, -2, 6, 49, 22)),
         ("withers", (-6, 36, -38, 6, 40, -24)), ("shoulder", (-7, 40, -30, 7, 43, -22)),
         ("rump", (-8, 30, 22, 8, 45, 28)),
         ("spine_ridge", (-3.5, 46, -20, 3.5, 49, -2)), ("hip_ridge", (-3, 49, -2, 3, 51, 20))]   # the tall spines
NECK = ([(33, -38), (43, -48), (50, -56)], [(11, 13), (9, 11)])
SKULL_PITCH = -18          # head pointing forward and a little down from the rising neck
TAIL = ([(43, 26), (42, 40), (40, 54), (37, 68), (33, 82), (30, 96)], [(11, 18), (9, 15), (7, 11), (5, 8), (3, 5)])
LEG_X, LEG = 9, ([(40, 12), (22, 4), (8, 11), (2, 11)], [(11, 18, -1), (8, 11, 0, "limb"), (7, 7, 0, "limb")])
ARM_X, ARM = 8, ([(27, -33), (15, -31), (3, -33)], [(5, 7), (4, 5, 0, "limb")])
SADDLE = (46, -22, -4, 15, 14, 14)   # top_y, z0, z1, width, body half width, flap
GRAZE = (-66, -24, 46)      # neck1, neck2, skull: the bill reaches the ground, the head stays inclined
SIT_HIND = (50, -95, 45)
SIT_SPLAY = (14, -24)         # resting: thigh and shin roll out (deg)
RUN_LEAN = 9               # bipedal run: the chest rises off the forelimbs


def body_top(z0, z1):
    """Highest body-box top over the z span (every torso box crosses x = 0)."""
    return max(y1 for _n, (x0, y0, a, x1, y1, b) in TORSO if a < z1 and b > z0)


def frill(m, neck, tail):
    """The low row of knobs down the midline of the back (AMNH 5240), over the ridge of tall spines and the first
    tail segments, shrinking towards the tip. Chain bones take the chain's unposed frame."""
    for z in range(-36, 22, 3):
        top = body_top(z, z + 2)
        m.box("body", (-0.5, top - 1, z), (0.5, top + 1, z + 2), name="knob", tag="frill")
    tp, ts = TAIL
    for i, (seg, (w, h)) in enumerate(zip(tail["segments"][:3], ts)):
        y = tp[0][0] + h / 2
        z0 = seg["unposed"][1]
        for z in range(int(z0) + 2, int(z0 + seg["len"]) - 1, 3):
            m.box(seg["bone"], (-0.5, y - 1, z), (0.5, y + (2 if i < 2 else 1), z + 2), name="knob", tag="frill")


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)

    # --- neck: arched, rising from the chest
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(3.0, 2.0))
    ay, az = neck["end"]
    h = lambda v: int(round(v * HEAD))
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (SKULL_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay + h(-3), az + h(-3)))

    def at(x, y, z):
        return (h(x), ay + h(y), az + h(z))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, at(x0, y0, z0), at(x1, y1, z1), tag=tag, name=name, **kw)

    def SM(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        B(bone, name + "_l", box, tag, **kw)
        B(bone, name + "_r", (-x1, y0, z0, -x0, y1, z1), tag, **kw)

    # --- head (head px, x HEAD): short and deep, a narrow bill; the tall thin helmet crest rising from behind the bill
    # over the eyes to the back of the skull, built up in rounded tiers
    B("skull", "braincase", (-3, -3, -5, 3, 3, 1), paint=MOUTH_DOWN)
    B("skull", "cheeks", (-3.5, -3, -9, 3.5, 1.5, -5), paint=MOUTH_DOWN)
    B("skull", "snout", (-2.5, -3, -13, 2.5, 1, -9), paint=MOUTH_DOWN)
    B("skull", "bill_top", (-2.5, -1.5, -15.5, 2.5, 0, -13), tag="beak")
    B("skull", "bill", (-3, -3.5, -16, 3, -1.5, -13), tag="beak")
    B("skull", "crest_nasal", (-1.5, 1, -12, 1.5, 3, -5), tag="crest")          # rising from the snout
    B("skull", "crest", (-1.5, 3, -11, 1.5, 6, 1), tag="crest")
    B("skull", "crest_mid", (-1, 6, -10, 1, 8, 0.5), tag="crest")
    B("skull", "crest_top", (-1, 8, -8.5, 1, 9.5, -1), tag="crest")
    m.bone("male_display", "skull", (0, ay, az))                                # males: the taller, longer helmet
    B("male_display", "crest_tip", (-1, 9.5, -7, 1, 10.5, -2.5), tag="crest")
    B("male_display", "crest_back", (-1, 5, 0.5, 1, 7.5, 2.5), tag="crest")
    B("jaw", "jaw", (-2.5, -6, -13, 2.5, -3, -3), paint=MOUTH_UP)
    B("jaw", "jaw_angle", (-3, -6, -6, 3, -3, 0))
    B("jaw", "predentary", (-3, -6, -16, 3, -4.5, -13), tag="beak")
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(3, 0.5, -3), "r": 1.0, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-3, 0.5, -3), "r": 1.0, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(2.5, -0.5, -12), "r": 0.9, "rx": 1.2, "mul": 0.5, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-2.5, -0.5, -12), "r": 0.9, "rx": 1.2, "mul": 0.5, "side": -1}]

    # --- hind legs: long, knee forward, three broad hoofed toes
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(3.0, 2.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 4.5, by - 2, bz - 2), (x + 4.5, by, bz + 4), tag="limb", name="heel_pad")
        for dx, length in ((-4.5, 4), (-1, 7), (2.5, 4)):
            a, b = sorted((x + dx * sx, x + (dx + 2) * sx))
            m.box(T, (a, by - 2, bz - 2 - length), (b, by, bz - 2), tag="limb", name="toe")
            m.box(T, (a, by - 2, bz - 4 - length), (b, by - 1, bz - 2 - length), tag="claw", name="hoof")
    m.sym(leg)

    # --- forelimbs: slender walking arms, the middle fingers closed in a mitten ending in a crescent hoof
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, overlap=(2.0, 1.0))
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], -8 * sx, 0))
        H = f"hand_{side}"
        m.box(H, (x - 3, by - 3, bz - 4), (x + 3, by + 1, bz + 2), tag="limb", name="mitten")
        m.box(H, (x - 3, by - 3, bz - 6), (x + 3, by - 1, bz - 4), tag="claw", name="hoof")
        a = x + 3 * sx
        m.box(H, (min(a, a + sx), by - 2, bz - 2), (max(a, a + sx), by + 1, bz + 1), tag="limb", name="finger5")
    m.sym(arm)

    # --- tail: long, tall and flat-sided, held straight out by the ossified tendons
    tpts, tsecs = TAIL
    tail = m.chain([f"tail{i + 1}" for i in range(5)], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 1.0))
    ty, tz = tail["end"]
    m.box("tail5", (-1, ty - 1.5, tz), (1, ty + 1.5, tz + 3), name="tail_tip")
    frill(m, neck, tail)

    add_saddle(m, "body", *SADDLE)
    animations(m)
    return m


def siny_(a, ph=0.0):
    return lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0)


def animations(m):
    NT = 5
    Li = 4.0
    idle = {
        "body": track(pos=wave(8, lambda p: (0, 0.125 * K * (1 + math.sin(2 * math.pi * p)), 0), Li)),   # breathing rises only: the hands stay on the ground
        "neck1": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * p), 3 * math.sin(2 * math.pi * (p + 0.3)), 0), Li)),
        "neck2": track(rot=wave(8, lambda p: (1.2 * math.sin(2 * math.pi * (p + 0.1)), 1.5 * math.sin(2 * math.pi * (p + 0.4)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * (p + 0.2)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-4 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
    }
    for i in range(NT):
        idle[f"tail{i+1}"] = track(rot=wave(8, siny_(2 + 0.7 * i, -0.08 * i), Li))
    m.anim("idle", Li, True, idle)
    # walk on four legs
    Lc, bob = 1.5, 0.6 * K
    t = quad_gait(Lc, 20, 16)
    t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 1.5 * math.sin(2 * math.pi * p)), Lc),
                      pos=wave(8, lambda p: (0, bob * 0.5 * (1 + math.cos(4 * math.pi * p)), 0), Lc))
    t["neck1"] = track(rot=wave(8, lambda p: (-2 * 0.6 * math.cos(4 * math.pi * p), 0, 0), Lc))
    for i in range(NT):
        t[f"tail{i+1}"] = track(rot=wave(8, siny_(2.5 + 0.7 * i, 0.25 - 0.08 * i), Lc))
    m.anim("walk", Lc, True, t)
    # run on two legs: the chest rises, the forelimbs fold, the tail balances straight out
    Lc, bob = 0.8, 1.0 * K
    t = {k: v for k, v in quad_gait(Lc, 34, 0).items() if not k.startswith(("upperarm", "forearm", "hand"))}
    t["body"] = track(rot=wave(8, lambda p: (RUN_LEAN, 1.5 * math.sin(2 * math.pi * p), 1.2 * math.sin(2 * math.pi * p)), Lc),
                      pos=wave(8, lambda p: (0, bob * math.cos(4 * math.pi * p), 0), Lc))
    for side in ("l", "r"):
        t[f"upperarm_{side}"] = track(rot=keys([(0, -20, 0, 0), (Lc, -20, 0, 0)]))
        t[f"forearm_{side}"] = track(rot=keys([(0, 45, 0, 0), (Lc, 45, 0, 0)]))
    t["neck1"] = track(rot=wave(8, lambda p: (-RUN_LEAN * 0.8 - 2 * math.cos(4 * math.pi * p), 0, 0), Lc))
    t["tail1"] = track(rot=wave(8, lambda p: (-RUN_LEAN * 0.7, 2 * math.sin(2 * math.pi * (p + 0.25)), 0), Lc))
    for i in range(1, NT):
        t[f"tail{i+1}"] = track(rot=wave(8, siny_(2 + 0.5 * i, 0.2 - 0.06 * i), Lc))
    m.anim("run", Lc, True, t)
    # attack (only when cornered): rear back, shove with the chest and swing the tail
    m.anim("attack", 0.9, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, 10, 0, 0), (0.5, -14, 0, 0), (0.9, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.3, 8, 0, 0), (0.5, -12, 0, 0), (0.9, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.3, 6, 0, 0), (0.5, -2, 0, 0), (0.9, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.3, 0, 0.5 * K, 1.0 * K), (0.5, 0, 0.9 * K, -2.5 * K), (0.9, 0, 0, 0)])),
        "upperarm_l": track(rot=keys([(0, 0, 0, 0), (0.3, -20, 0, 0), (0.5, 4, 0, 0), (0.9, 0, 0, 0)])),
        "upperarm_r": track(rot=keys([(0, 0, 0, 0), (0.3, -20, 0, 0), (0.5, 4, 0, 0), (0.9, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.35, 0, -8, 0), (0.6, 0, 10, 0), (0.9, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.35, 0, -8, 0), (0.6, 0, 12, 0), (0.9, 0, 0, 0)])),
    })
    m.anim("sit", 4.0, True, quad_sit(m, 17, hind=SIT_HIND, neck=10))
    sit = m.animations[-1]                       # the folded hind legs lie beside the belly, not inside it
    for side, sg in (("l", 1), ("r", -1)):
        for bone, roll in (("thigh", SIT_SPLAY[0]), ("shin", SIT_SPLAY[1])):
            tr = sit["bones"][f"{bone}_{side}"]
            tr["rotation"] = [[k[0], k[1], k[2], k[3] + sg * roll] for k in tr["rotation"]]
    low = lowest_point(m, sit["bones"])
    for bone, tr in sit["bones"].items():
        if "position" in tr and (bone == "body" or bone.startswith("thigh")):
            tr["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in tr["position"]]
    jk = [(0, 0, 0, 0), (0.6, 0, 0, 0)]
    for k in range(6):
        t0 = 0.75 + k * 0.3
        jk += [(t0, -10, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(2.8, 0, 0, 0)]
    m.anim("graze", 2.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.6, GRAZE[0], 0, 0), (2.3, GRAZE[0], 0, 0), (2.8, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.6, GRAZE[1], 0, 0), (2.3, GRAZE[1], 0, 0), (2.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.6, GRAZE[2], 0, 0), (2.3, GRAZE[2], 0, 0), (2.8, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
    })
    # call: neck up, head raised, the deep resonating call through the looping passages of the crest
    m.anim("call", 1.6, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.35, 16, 0, 0), (1.3, 16, 0, 0), (1.6, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.35, 8, 0, 0), (1.3, 8, 0, 0), (1.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.35, 14, 0, 0), (1.3, 14, 0, 0), (1.6, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.35, -16, 0, 0), (1.25, -16, 0, 0), (1.5, 0, 0, 0)])),
    })
    add_knockout(m)
    for a in m.animations:      # eat / beg / tame come from the 1x set: scale their position keys
        if a["name"].split(".")[-1] in ("eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    fit_to_ground(m, "graze", ("neck1", "neck2", "skull"))
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
