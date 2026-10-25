"""
Parasaurolophus walkeri  (Campanian, Dinosaur Park Formation, Alberta; P. tubicen and P. cyrtocristatus from
New Mexico and Utah)

Reference:
  - Size (Parks 1922; Lull & Wright 1942; Wikipedia): ~9.5 m long, ~2.5-3.5 t; the holotype ROM 768 is a nearly
    complete skeleton with the skull.
  - Crest (Sullivan & Williamson 1999; Weishampel 1981): the premaxillae and nasals form a long hollow tube that
    rises from the snout over the eyes and sweeps back past the skull, ~1 m in P. walkeri; inside it the nasal
    passages loop forward and back, a resonating chamber for low calls (a "trombone"). It is straight and long in
    walkeri, short and curved in cyrtocristatus. Tall neural spines over the shoulders leave a notch where the
    crest lies against the neck.
  - Head: long and low with a wide, flat, toothless "duck bill" (keratin) in front of grinding dental batteries.
  - Body (hadrosaurids): a deep body, the back highest over the hips; forelimbs lighter and shorter, the three
    middle fingers bound in a fleshy hoofed "mitten", the fifth free; hind legs long with three broad hoofed toes;
    a tall, flat-sided tail stiffened by ossified tendons. Walked on four legs and ran on two.
  - Skin (hadrosaur mummies, e.g. "Dakota", Edmontosaurus): a mosaic of small pebbly tubercles with larger
    feature scales in patches; a fleshy midline crest of skin along the back is known in some hadrosaurs.

v2x (2026-10-24, remaster at the T. rex v3 level): its own model (no longer the shared hadrosaur rig), modelled
at 16 px = 1 m (one texture pixel = one vanilla pixel in game). The head is ~1.2x the real proportion.
render_scale 0.5 = authoring scale; the in-game size comes from SIZES in tools/javagen/gen_species.py
(MODEL_SCALE ~0.87 for 9.5 m). Runs on two legs.
"""
import math
from rig import Model, wave, sinx, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from paint import mix
from groundfit import fit_to_ground

ID = "parasaurolophus"
K = 2.0
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
    """Pebbly tubercle mosaic with patches of feature scales, dark bands across the back fading on the flanks,
    a pale throat and belly; the crest is a display: a dark tube with pale bands that follow its curve."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("claw", "eye", "mouth", "beak", "saddle"):
        return rgb
    if tag == "crest":
        u = getattr(cube, "crest_u", 0.0) + (P[2] - cube.frm[2]) / 16.0
        band = math.sin(u * 2 * math.pi * 2.2)
        if band > 0.62:
            return pal["crest_band"] * (0.95 if (tx.i + tx.j) % 3 == 0 else 1.0)
        return rgb * (0.9 if tx.face == "down" else 1.0)
    if tag == "frill":                                                    # fleshy midline crest along the back
        return mix(rgb, pal["crest"], 0.35) * (0.9 if tx.edge else 1.0)
    if tag in ("skin", "limb"):
        if tag == "limb" and cube.bone.startswith(("toes", "hand")) and tx.face != "down":
            return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)
        if tag == "skin" and region in ("dorsal", "flank") and not cube.bone.startswith(("skull", "jaw")):
            st = math.sin(P[2] * 2 * math.pi / 13.0 + 0.5 * math.sin(P[1] * 0.25))
            if st > 0.5 and (region == "dorsal" or tx.cy > 0.5):
                rgb = rgb * 0.8                                               # bands across the back
        big, hb = _cell(P, 3.0)
        if hb % 6 == 0 and region == "flank":
            return rgb * (0.88 if big < 0.12 else 1.1)                       # feature scales
        edge, _h = _cell(P, 1.5)
        if edge < 0.13:
            rgb = rgb * 0.92                                                  # pebbly tubercles
    return rgb


PALETTE = {"dorsal": "#46584c", "flank": "#748c76", "belly": "#d8d4b0", "limb": "#5a6a57", "limb_top": "#6c8370",
           "claw": "#38312a", "claw_base": "#38312a", "beak": "#5a4e40", "crest": "#a63a2b", "crest_band": "#ecc77e",
           "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622", "eye": "#b8862c", "pupil": "#140f0a"}
SEXES = {"male": {"dorsal": "#3c5248", "crest": "#b63a28", "crest_band": "#f2cf80"},
         "female": {"dorsal": "#5c5848", "flank": "#8c866a", "crest": "#6e6352", "crest_band": "#bdb190"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (40, 12)                                      # hip joint
TORSO = [("hips", (-10, 26, -2, 10, 46, 24)), ("belly", (-12, 21, -26, 12, 43, 0)),
         ("chest", (-9, 21, -40, 9, 36, -24)), ("belly_low", (-9, 18, -32, 9, 21, -4)),
         ("back", (-7, 43, -24, 7, 46, -2)), ("sacrum", (-6, 46, -2, 6, 49, 22)),
         ("withers", (-6, 36, -38, 6, 40, -24)), ("shoulder", (-7, 40, -30, 7, 43, -22)),
         ("rump", (-8, 30, 22, 8, 45, 28))]
NECK = ([(33, -38), (43, -48), (50, -56)], [(11, 13), (9, 11)])
SKULL_PITCH = -22          # head pointing forward and a little down from the rising neck
TAIL = ([(43, 26), (42, 40), (40, 54), (37, 68), (33, 82), (30, 96)], [(11, 18), (9, 15), (7, 11), (5, 8), (3, 5)])
LEG_X, LEG = 9, ([(40, 12), (22, 4), (8, 11), (2, 11)], [(11, 18, -1), (8, 11, 0, "limb"), (7, 7, 0, "limb")])
ARM_X, ARM = 8, ([(27, -33), (15, -31), (2, -33)], [(5, 7), (4, 5, 0, "limb")])
# crest: (y, z) joints of the tube in the head's frame (real px, x HEAD), -z = forward
CREST = [(1, -10), (4.5, -5), (5.5, 3), (6, 11)]
MALE_CREST = [(6, 11), (6.2, 18)]
SADDLE = (46, -22, -4, 15, 13, 14)   # top_y, z0, z1, width, body half width, flap
GRAZE = (-66, -24, 46)      # neck1, neck2, skull: the bill reaches the ground, the head stays inclined
SIT_HIND = (50, -95, 45)
SIT_SPLAY = (14, -24)         # resting: thigh and shin roll out (deg)
RUN_LEAN = 9               # bipedal run: the chest rises off the forelimbs


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)
    for z0, z1, y in ((-36, -30, 40), (-30, -24, 43), (-24, -2, 46), (-2, 22, 49)):        # fleshy midline crest of skin
        m.box("body", (-1, y, z0), (1, y + 2, z1), tag="frill", name="dorsal_frill")

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

    def SM(name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        B("skull", name + "_l", box, tag, **kw)
        B("skull", name + "_r", (-x1, y0, z0, -x0, y1, z1), tag, **kw)

    # --- head: long and low, a wide flat duck bill
    B("skull", "braincase", (-3, -2, -5, 3, 4, 1), paint=MOUTH_DOWN)
    B("skull", "cheeks", (-3.5, -4, -9, 3.5, 2, -4), paint=MOUTH_DOWN)
    B("skull", "snout", (-2.5, -3.5, -13, 2.5, 1, -9), paint=MOUTH_DOWN)
    B("skull", "bill", (-3.5, -3.5, -16, 3.5, -1, -13), tag="beak")
    B("skull", "bill_top", (-2.5, -1, -15, 2.5, 0, -13), tag="beak")
    SM("brow", (2.5, 3, -7, 3.5, 4, -3))
    B("jaw", "jaw", (-2.5, -5.5, -13, 2.5, -3.5, -3), paint=MOUTH_UP)
    B("jaw", "predentary", (-3, -5.5, -16, 3, -3.5, -13), tag="beak")
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(3.5, 1, -5.5), "r": 1.0, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-3.5, 1, -5.5), "r": 1.0, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(2.5, -1, -11.5), "r": 1.0, "rx": 1.4, "mul": 0.55, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-2.5, -1, -11.5), "r": 1.0, "rx": 1.4, "mul": 0.55, "side": -1}]

    # --- crest: a hollow tube from the snout over the eyes and back past the skull (tilted boxes)
    def tube(bone, joints, name, u0=0.0):
        u = u0
        for (y0, z0), (y1, z1) in zip(joints, joints[1:]):
            L = math.hypot(y1 - y0, z1 - z0)
            ang = -math.degrees(math.atan2(y1 - y0, z1 - z0))
            o = at(0, y0, z0)
            th = 4 if name == "crest" else 3
            c = m.box(bone, (-1.5, o[1] - 1.5, o[2] - 1), (1.5, o[1] - 1.5 + th, o[2] + h(L) + 1), tag="crest", name=name,
                      rot=(ang, 0, 0), origin=o)
            c.crest_u = u
            u += L / 16.0
        return u
    u = tube("skull", CREST, "crest")
    m.bone("male_display", "skull", (0, ay, az))
    tube("male_display", MALE_CREST, "crest_tip", u)

    # --- hind legs: long, knee forward, three broad hoofed toes
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(3.0, 2.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 4, by - 2, bz - 2), (x + 4, by, bz + 3), tag="limb", name="heel_pad")
        for dx, length in ((-4, 4), (-1, 6), (2, 4)):
            a, b = sorted((x + dx * sx, x + (dx + 2) * sx))
            m.box(T, (a, by - 2, bz - 2 - length), (b, by, bz - 2), tag="limb", name="toe")
            m.box(T, (a, by - 2, bz - 4 - length), (b, by - 1, bz - 2 - length), tag="claw", name="hoof")
    m.sym(leg)

    # --- forelimbs: light, the three middle fingers in a hoofed mitten, the fifth free
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, overlap=(2.0, 1.0))
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], -8 * sx, 0))
        H = f"hand_{side}"
        m.box(H, (x - 3, by - 2, bz - 4), (x + 3, by + 1, bz + 2), tag="limb", name="mitten")
        m.box(H, (x - 3, by - 2, bz - 5), (x + 3, by - 1, bz - 4), tag="claw", name="hoof")
        a = x + 3 * sx
        m.box(H, (min(a, a + sx), by - 1, bz - 3), (max(a, a + sx), by + 1, bz), tag="limb", name="finger5")
    m.sym(arm)

    # --- tail: tall and flat-sided, held straight out by the ossified tendons
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3", "tail4", "tail5"], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 1.0))
    ty, tz = tail["end"]
    m.box("tail5", (-1, ty - 2, tz), (1, ty + 2, tz + 3), name="tail_tip")
    for seg, (w, hh) in list(zip(tail["segments"], tsecs))[:3]:
        sy, sz = seg["unposed"]
        m.box(seg["bone"], (-1, sy + hh / 2, sz), (1, sy + hh / 2 + 2, sz + int(round(seg["len"]))), tag="frill", name="tail_frill")

    add_saddle(m, "body", *SADDLE)
    animations(m)
    return m


def siny_(a, ph=0.0):
    return lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0)


def animations(m):
    Li = 4.0
    idle = {
        "body": track(pos=wave(8, lambda p: (0, 0.125 * K * (1 + math.sin(2 * math.pi * p)), 0), Li)),   # breathing rises only: the forefeet stay planted
        "neck1": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * p), 3 * math.sin(2 * math.pi * (p + 0.3)), 0), Li)),
        "neck2": track(rot=wave(8, lambda p: (1.2 * math.sin(2 * math.pi * (p + 0.1)), 1.5 * math.sin(2 * math.pi * (p + 0.4)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * (p + 0.2)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-4 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
    }
    for i in range(5):
        idle[f"tail{i+1}"] = track(rot=wave(8, siny_(2 + 0.8 * i, -0.08 * i), Li))
    m.anim("idle", Li, True, idle)
    # walk on four legs
    Lc, bob = 1.5, 0.6 * K
    t = quad_gait(Lc, 20, 16)
    t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 1.5 * math.sin(2 * math.pi * p)), Lc),
                      pos=wave(8, lambda p: (0, bob * 0.5 * (1 + math.cos(4 * math.pi * p)), 0), Lc))
    t["neck1"] = track(rot=wave(8, lambda p: (-2 * 0.6 * math.cos(4 * math.pi * p), 0, 0), Lc))
    for i in range(5):
        t[f"tail{i+1}"] = track(rot=wave(8, siny_(2.5 + 0.8 * i, 0.25 - 0.08 * i), Lc))
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
    for i in range(1, 5):
        t[f"tail{i+1}"] = track(rot=wave(8, siny_(2 + 0.6 * i, 0.2 - 0.06 * i), Lc))
    m.anim("run", Lc, True, t)
    # attack (only when cornered): rear back and shove with the chest and the head
    m.anim("attack", 0.9, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, 10, 0, 0), (0.5, -14, 0, 0), (0.9, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.3, 8, 0, 0), (0.5, -12, 0, 0), (0.9, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.3, 6, 0, 0), (0.5, -2, 0, 0), (0.9, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.3, 0, 0.5 * K, 1.0 * K), (0.5, 0, 0.9 * K, -2.5 * K), (0.9, 0, 0, 0)])),
        "upperarm_l": track(rot=keys([(0, 0, 0, 0), (0.3, -20, 0, 0), (0.5, 4, 0, 0), (0.9, 0, 0, 0)])),
        "upperarm_r": track(rot=keys([(0, 0, 0, 0), (0.3, -20, 0, 0), (0.5, 4, 0, 0), (0.9, 0, 0, 0)])),
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
    # call: neck up, head raised, the crest tube sounding
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
