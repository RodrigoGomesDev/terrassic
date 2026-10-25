"""
Edmontosaurus annectens  (Late Cretaceous, Maastrichtian; Hell Creek and Lance formations, western North America)

Reference:
  - Size (Campione & Evans 2011; Wosik et al. 2019): one of the largest hadrosaurids, adults ~12 m and ~5-6 t,
    some bigger individuals claimed. Lived in huge herds (bonebeds of thousands) and was the staple prey of the
    Tyrannosaurus (healed bite marks on a tail, Carpenter 1997).
  - Skull (Campione & Evans 2011; Xing et al. 2017): long, low and flat-topped, no bony crest; a long low snout
    with a big circumnarial depression around the nostril, a very broad, flat duck bill whose keratin sheath
    (LACM 23502) ran well past the bone and hung down at the edges; cheeks over dental batteries of hundreds of
    teeth; a big orbit high at the back of the head.
  - Soft tissue: E. regalis (Bell et al. 2013) shows a fleshy cockscomb on top of the head; the "Dakota" and the
    "Ed Mummies" (Sereno et al. 2025) preserve the skin: a fleshy crest along the neck and the back that turns
    into a single row of spikes over the tail, one spike over each vertebra; the hand with its fingers closed in a
    mitten ending in a crescent hoof; hoofed toes on the feet; tiny pebbly scales with patches of bigger ones.
  - Body (hadrosaurids): deep and long, highest over the hips; a long arched neck holding the head low (a grazer
    of the ground layer); slender forelimbs used for walking; long hind legs; a long deep tail stiffened by
    ossified tendons. Walked on four legs and ran on two.
  - Colour unknown; kept from the old model: dusty grey-brown, a pale belly, a dark stripe down the spine and soft
    saddle bands; males with the red comb and a darker back, females sandier.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared hadrosaur rig), built with
the same hadrosaurid construction rules as the Maiasaura and Parasaurolophus but longer and lower, with a longer
neck and tail; about 18 px = 1 m. The head is ~1.3x the real proportion. Males carry the fleshy comb
("male_display").
"""
import math
from rig import Model, wave, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "edmontosaurus"
K = 2.4                     # the archetype's moving poses were written for the ~1x hadrosaur rig
HEAD = 1.15


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
    """The mummy skin: tiny pebbly tubercles everywhere with patches of bigger feature scales on the flanks; a
    dark stripe down the spine, soft saddle bands over the back fading before the belly, a pale throat."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("claw", "eye", "mouth", "beak", "saddle"):
        return rgb
    if tag == "frill":
        col = pal["frill"].copy()
        if tx.face == "up":
            col = col * 1.15
        elif (tx.i + tx.j) % 3 == 0:
            col = col * 0.9
        return col
    if tag == "crest":
        return rgb * (1.12 if tx.face == "up" else (0.9 if (tx.i + tx.j) % 3 == 0 else 1.0))
    if tag in ("skin", "limb"):
        if tag == "limb" and cube.bone.startswith(("toes", "hand")) and tx.face != "down":
            return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)
        if region == "dorsal" and tx.face == "up" and abs(P[0]) < 2.0 and not cube.bone.startswith(("skull", "jaw")):
            return pal["spine"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)
        if region == "dorsal" and tag == "skin" and math.sin(P[2] * 0.33) > 0.72:
            rgb = rgb * 0.86                                                  # saddle bands
        big, hb = _cell(P, 3.0)
        if hb % 5 == 0 and region == "flank":
            return rgb * (0.88 if big < 0.12 else 1.08)                       # feature scales
        edge, _h = _cell(P, 1.5)
        if edge < 0.13:
            rgb = rgb * 0.93                                                  # pebbly tubercles
    return rgb


PALETTE = {"dorsal": "#6a6050", "flank": "#9a8c72", "belly": "#e2dac4", "spine": "#3e362c", "frill": "#4e4638",
           "limb": "#7a6e58", "limb_top": "#8a7e66",
           "claw": "#38312a", "claw_base": "#38312a", "beak": "#4a4238", "crest": "#b04838", "crest_band": "#b04838",
           "spot": "#3e3226", "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622", "eye": "#b8862c", "pupil": "#140f0a"}
SEXES = {"male": {"dorsal": "#5a5044", "flank": "#8c7e66", "crest": "#c04a38"},
         "female": {"dorsal": "#7a6e58", "flank": "#a89a7c", "belly": "#ece4ce", "crest": "#9a6a58"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (46, 14)                                      # hip joint
TORSO = [("hips", (-12.5, 30, -2, 12.5, 53, 28)), ("belly", (-15, 23, -31, 15, 49, 0)),
         ("chest", (-11, 24, -47, 11, 42, -29)), ("belly_low", (-11, 20, -38, 11, 23, -5)),
         ("back", (-8, 49, -29, 8, 53, -2)), ("sacrum", (-6.5, 53, -2, 6.5, 56, 25)),
         ("withers", (-7, 42, -45, 7, 46, -29)), ("shoulder", (-8, 46, -36, 8, 49, -26)),
         ("rump", (-9, 35, 28, 9, 52, 33))]
NECK = ([(37, -44), (46, -58), (51, -72)], [(12, 14), (10, 12)])
SKULL_PITCH = -16          # the long head held low, pointing forward and a little down from the arched neck
TAIL = ([(49, 31), (48, 46), (46, 61), (43, 76), (39, 91), (35, 105), (32, 118)],
        [(12, 20), (10, 16), (8, 12), (6, 9), (4, 6), (3, 4)])
LEG_X, LEG = 10, ([(46, 14), (25, 5), (9, 13), (2, 13)], [(12, 20, -1), (9, 12, 0, "limb"), (7, 8, 0, "limb")])
ARM_X, ARM = 9, ([(30, -39), (16, -37), (3, -39)], [(6, 8), (4, 5, 0, "limb")])
SADDLE = (53, -27, -5, 16, 15, 16)   # top_y, z0, z1, width, body half width, flap
GRAZE = (-62, -22, 40)      # neck1, neck2, skull: the bill reaches the ground, the head stays inclined
SIT_HIND = (50, -95, 45)
SIT_SPLAY = (14, -24)         # resting: thigh and shin roll out (deg)
RUN_LEAN = 9               # bipedal run: the chest rises off the forelimbs


def body_top(z0, z1):
    """Highest body-box top over the z span (every torso box crosses x = 0)."""
    return max(y1 for _n, (x0, y0, a, x1, y1, b) in TORSO if a < z1 and b > z0)


def frill(m, neck, tail):
    """The mummies' soft-tissue crest: a low fleshy crest of rounded lobes along the neck and the back, turning into
    a single row of spikes over the tail, one over each vertebra. Chain bones take the chain's unposed frame."""
    pts, secs = NECK
    for i, (seg, (w, h)) in enumerate(zip(neck["segments"], secs)):
        y = pts[0][0] + h / 2
        z0 = seg["unposed"][1]
        for k, z in enumerate(range(int(z0) - (4 if i == 0 else 1), int(z0 - seg["len"]) + 1, -3)):
            m.box(seg["bone"], (-1, y - 1, z - 3), (1, y + 1 + (k % 2), z), name="frill", tag="frill")
    for z in range(-45, 26, 3):
        top = body_top(z, z + 3)
        m.box("body", (-1, top - 1, z), (1, top + 1 + (z // 3) % 2, z + 3), name="frill", tag="frill")
    tp, ts = TAIL
    for i, (seg, (w, h)) in enumerate(zip(tail["segments"], ts)):
        y = tp[0][0] + h / 2
        z0 = seg["unposed"][1]
        ht = max(1, 4 - i)
        for z in range(int(z0) + 2, int(z0 + seg["len"]) - 1, 3):
            m.box(seg["bone"], (-0.5, y - 1, z), (0.5, y + ht, z + 2), name="spike", tag="frill")


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)

    # --- neck: long and arched, rising from the chest and bending the head down
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(3.0, 2.0))
    ay, az = neck["end"]
    h = lambda v: int(round(v * HEAD))
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (SKULL_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay + h(-3.5), az + h(-3)))

    def at(x, y, z):
        return (h(x), ay + h(y), az + h(z))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, at(x0, y0, z0), at(x1, y1, z1), tag=tag, name=name, **kw)

    def SM(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        B(bone, name + "_l", box, tag, **kw)
        B(bone, name + "_r", (-x1, y0, z0, -x0, y1, z1), tag, **kw)

    # --- head (head px, x HEAD): long, low and flat-topped; wide cheeks over the dental batteries; a long low snout
    # with the big nostril hollow; the very broad flat bill, its keratin edge hanging down in front
    B("skull", "braincase", (-3.5, -3.5, -5, 3.5, 4, 1), paint=MOUTH_DOWN)
    B("skull", "cheeks", (-4, -3.5, -10, 4, 2, -5), paint=MOUTH_DOWN)
    B("skull", "snout", (-3, -3.5, -17, 3, 2, -10), paint=MOUTH_DOWN)
    B("skull", "nasal", (-2, 2, -15, 2, 3, -5))
    B("skull", "bill_top", (-4, -1.5, -21, 4, 0, -17), tag="beak")
    B("skull", "bill", (-4.5, -3.5, -22, 4.5, -1.5, -17), tag="beak")
    B("skull", "bill_lip", (-4.5, -4.5, -22, 4.5, -3.5, -19), tag="beak")      # the drooping keratin rim
    SM("skull", "brow", (3, 3, -4, 4, 5, -1))
    m.bone("male_display", "skull", (0, ay, az))                                # the fleshy cockscomb
    B("male_display", "comb", (-1, 4, -7, 1, 6, 0), tag="crest")
    B("male_display", "comb_lobe", (-1, 6, -6, 1, 7, -4), tag="crest")
    B("male_display", "comb_lobe", (-1, 6, -3, 1, 7, -1), tag="crest")
    B("jaw", "jaw", (-3, -6, -17, 3, -3.5, -3), paint=MOUTH_UP)
    B("jaw", "jaw_angle", (-3.5, -6.5, -6, 3.5, -3.5, 0))
    B("jaw", "predentary", (-4, -6, -21, 4, -4.5, -17), tag="beak")
    m.decals += [{"kind": "spot", "bones": ["skull"], "pos": at(3, -0.5, -14), "r": 1.6, "rx": 2.6, "mul": 0.55, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-3, -0.5, -14), "r": 1.6, "rx": 2.6, "mul": 0.55, "side": -1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(3.5, 1.5, -3), "r": 1.0, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-3.5, 1.5, -3), "r": 1.0, "side": -1}]

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
    tail = m.chain([f"tail{i + 1}" for i in range(6)], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 1.0))
    ty, tz = tail["end"]
    m.box("tail6", (-1, ty - 1.5, tz), (1, ty + 1.5, tz + 3), name="tail_tip")
    frill(m, neck, tail)

    add_saddle(m, "body", *SADDLE)
    animations(m)
    return m


def siny_(a, ph=0.0):
    return lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0)


def animations(m):
    NT = 6
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
    Lc, bob = 1.6, 0.6 * K
    t = quad_gait(Lc, 20, 16)
    t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 1.5 * math.sin(2 * math.pi * p)), Lc),
                      pos=wave(8, lambda p: (0, bob * 0.5 * (1 + math.cos(4 * math.pi * p)), 0), Lc))
    t["neck1"] = track(rot=wave(8, lambda p: (-2 * 0.6 * math.cos(4 * math.pi * p), 0, 0), Lc))
    for i in range(NT):
        t[f"tail{i+1}"] = track(rot=wave(8, siny_(2.5 + 0.7 * i, 0.25 - 0.08 * i), Lc))
    m.anim("walk", Lc, True, t)
    # run on two legs: the chest rises, the forelimbs fold, the tail balances straight out
    Lc, bob = 0.85, 1.0 * K
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
    # attack (only when cornered): rear back, shove with the chest and swing the heavy tail
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
    m.anim("sit", 4.0, True, quad_sit(m, 20, hind=SIT_HIND, neck=10))
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
    # call: neck up, head raised, a low bellow through the inflated nostril sac
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
