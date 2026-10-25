"""
Protoceratops andrewsi  (Late Cretaceous, Campanian; Djadokhta Formation, Mongolia - the Flaming Cliffs)

Reference:
  - Size (Granger & Gregory 1923; Brown & Schlaikjer 1940; Dodson 1976; Czepinski 2019): a sheep-sized
    protoceratopsid of ~1.8-2.5 m and 60-180 kg, known from dozens of skeletons of every age, nests and the
    "Fighting Dinosaurs" locked with a Velociraptor. Hips ~0.6 m high.
  - Skull (Brown & Schlaikjer 1940; Hone et al. 2014): huge for the body; no true horns, only a low bump over the
    nose (taller in males) and jugals flaring out into points under the eyes; a deep face, a parrot beak (rostral
    and predentary) with two small teeth in the premaxilla; very large orbits with big sclerotic rings (active at
    dusk and night, Schmitz & Motani 2011); a broad frill of parietal and squamosals with two big windows covered
    by skin, much bigger and more upright in adult males.
  - Body: chunky, the back highest over the hips; short forelimbs with five clawed fingers; longer hind legs with
    four toes ending in flattened claws (a digger: fossils in burrow-like poses, Fastovsky et al. 1997); a deep,
    flat-sided tail raised by tall neural spines, a low "sail" (Tereschenko 2008), likely a display.
  - Colour unknown; kept from the old model: sand and tan with a dark dorsal stripe and freckles; the frill tawny
    with dark windows and a pale rim, red-orange on males, dun on females.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared ceratopsian rig), built
with the construction rules of the Triceratops/Styracosaurus remasters at the old model's ~37 px = 1 m (a small
species keeps its density). The skull is ~1.2x the real proportion. Males carry the taller frill and nose bump
("male_display").
"""
import math
from rig import Model, wave, track, keys, add_knockout, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "protoceratops"
K = 2.0  # position keys of the 1x animation set are scaled by this


def _cell(P, size):
    """Staggered polygon scale cells of `size` px: (distance to the cell edge 0..0.5, cell hash)."""
    a, b, c = P[0] / size, P[1] / size, P[2] / size
    row = math.floor(b)
    a += 0.5 * (row % 2)
    c += 0.5 * (row % 2)
    fa, fb, fc = a - math.floor(a), b - math.floor(b), c - math.floor(c)
    edge = min(fa, 1 - fa, fb, 1 - fb, fc, 1 - fc)
    h = (math.floor(a) * 73856093 ^ row * 19349663 ^ math.floor(c) * 83492791) & 1023
    return edge, h


def pattern(model, tx, rgb, region):
    """Small pebbly scales with scattered bigger ones and freckles, a dark stripe down the spine and the tail sail;
    the frill tawny with a pale rim, a pale midline bar and the two windows showing dark under the skin."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag, bone = cube.tag, cube.bone
    if tag in ("claw", "eye", "mouth", "tongue", "horn", "beak", "tooth_cube"):
        if tag == "horn" and (tx.i + 2 * tx.j) % 5 == 0:
            return rgb * 0.93
        return rgb
    if tag == "frill":
        if cube.name.startswith("frill_rim"):
            return pal["frill_edge"] * (0.92 if (tx.i + tx.j) % 3 == 0 else 1.0)
        fy = model._frill_base
        if abs(P[0]) < 1.0:
            return pal["frill_edge"] * 0.9                                   # midline bar between the windows
        wx, wy, rx, ry = model._frill_window
        win = ((abs(P[0]) - wx) / rx) ** 2 + ((P[1] - fy - wy) / ry) ** 2
        if win < 1.0:
            return pal["frill_window"] * (1.0 if win > 0.45 else 0.85)       # the windows under the skin
        return rgb
    if tag in ("skin", "limb"):
        if tag == "limb" and bone.startswith(("toes", "hand")) and tx.face != "down":
            return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)
        if region == "dorsal" and abs(P[0]) < 1.2 and bone not in ("skull", "jaw"):
            return pal["stripe"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)    # dark stripe down the spine and tail
        if region != "belly":
            big, hb = _cell(P, 2.5)
            if hb % 9 == 0:
                return pal["stripe"] * 1.3                                   # freckles
            if hb % 5 == 0:
                return rgb * (0.88 if big < 0.12 else 1.08)                  # bigger scales
        edge, _h = _cell(P, 1.2)
        if edge < 0.12:
            rgb = rgb * 0.94
    return rgb


PALETTE = {"dorsal": "#8a6a42", "flank": "#b89a68", "belly": "#e4d8b4", "stripe": "#5a4428",
           "limb": "#9a7e52", "limb_top": "#a68a5c", "claw": "#3a3028", "claw_base": "#3a3028",
           "horn_base": "#7a6848", "horn_tip": "#e8dcc0", "beak": "#4a4036",
           "frill": "#a06a3c", "frill_edge": "#e6d4a8", "frill_window": "#6a4a30",
           "tooth": "#d8d0b8", "tooth_cube": "#e8e0c8", "tooth_cube_base": "#d0c8b0", "tooth_cube_tip": "#f4f0e0",
           "mouth": "#6e3330", "tongue": "#94504a", "gum": "#4e2622", "eye": "#c89a40", "pupil": "#140f0a"}
SEXES = {"male": {"frill": "#b85a30", "frill_window": "#5a3424", "dorsal": "#7a5c38", "frill_edge": "#f0dcb0"},
         "female": {"frill": "#8a6a48", "frill_edge": "#d4c4a0", "flank": "#b8a478", "frill_window": "#6e5a40"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (21, 8)                                       # hip joint
TORSO = [("hips", (-6, 12, 3, 6, 24, 14)), ("sacrum", (-4, 24, 4, 4, 26, 13)),
         ("belly", (-7, 10, -6, 7, 23, 3)), ("chest", (-6, 10, -14, 6, 21, -6)),
         ("back", (-5, 23, -5, 5, 25, 4)), ("withers", (-4.5, 21, -13, 4.5, 23, -6)),
         ("belly_low", (-5, 9, -11, 5, 10, 1)), ("rump", (-4.5, 14, 14, 4.5, 23, 17))]
NECK = ([(18, -12), (18, -15), (17.5, -18)], [(10, 11), (9, 9)])
TAIL = ([(20, 16), (19, 24), (17, 32), (14, 40), (11, 46)], [(7, 11), (6, 9), (4, 6), (2, 3)])
SAIL = [(4, 3), (3, 3), (2, 2)]                       # tall neural spines over the tail: (height px, spacing)
LEG_X = 5
LEG = ([(21, 8), (11, 6), (5.5, 9.5), (2, 7.5)], [(6, 9, -0.5), (4, 5, 0.5, "limb"), (3, 3, 0, "limb")])
ARM_X = 6
ARM = ([(15, -10), (8, -8.5), (2, -10)], [(4, 5), (3, 3, 0, "limb")])
SKULL_PITCH = -8
GRAZE = (-12, -8)
FRILL_TILT = 38
# frill rows in px: (half width, y0, y1) from the base of the plate
FRILL = [(6, 0, 3), (7, 3, 6), (7.5, 6, 9), (6.5, 9, 11)]


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern

    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)
    for sx in (1, -1):                                                     # shoulder blades
        a = 6 * sx
        m.box("body", (min(a, a + sx), 14, -13), (max(a, a + sx), 20, -8), name="scapula")

    # --- neck: short, under the frill
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(2.0, 1.5))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (SKULL_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 5, az - 6))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    def S(name, box, tag="skin", **kw):
        return B("skull", name, box, tag, **kw)

    def SM(name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        B("skull", name + "_l", box, tag, **kw)
        B("skull", name + "_r", (-x1, y0, z0, -x0, y1, z1), tag, **kw)

    # --- skull (px): a big head for the body; broad cranium with the huge orbits, a short deep face, the beak
    S("braincase", (-4, -5, -7, 4, 3, 1))
    S("orbits", (-5, -2, -8, 5, 3, -4), paint=MOUTH_DOWN)
    SM("jugal", (4, -6, -9, 6, -1, -4))
    SM("jugal_horn", (6, -6, -7, 7, -4, -5), tag="horn", paint={"axis": "+x"})   # the flaring cheek points
    S("face", (-3.5, -5, -13, 3.5, 2, -7), paint=MOUTH_DOWN)
    S("snout", (-2.5, -5, -16, 2.5, 1, -13), paint=MOUTH_DOWN)
    S("nasal_bump", (-1, 1, -14, 1, 3, -11), tag="horn", paint={"axis": "+y"})
    S("rostral", (-1.5, -6, -18, 1.5, 0, -16), tag="beak")
    S("beak_hook", (-1.5, -8, -18.5, 1.5, -6, -16.5), tag="beak")
    for sx in (1, -1):                                                     # the two premaxillary teeth
        a = 1.5 * sx
        m.box("skull", (min(a, a - sx), ay - 6, az - 15.5), (max(a, a - sx), ay - 5, az - 14.5), name="fang",
              tag="tooth_cube", paint={"axis": "-y"})
    m.bone("male_display", "skull", (0, ay, az))
    B("male_display", "nasal_bump_tip", (-0.5, 3, -13.5, 0.5, 4, -11.5), tag="horn", paint={"axis": "+y"})

    # --- frill: a broad fan rising back from the skull roof, pale rim, the windows painted under the skin
    fy, fz = ay + 2, az
    m._frill_base = fy
    m._frill_window = (3.6, 5.5, 2.2, 2.6)
    m.bone("frill", "skull", (0, fy, fz), (FRILL_TILT, 0, 0))
    for k, (hw, y0, y1) in enumerate(FRILL):
        if k >= 1:                                                         # the base row sits inside the neck
            m.box("frill", (-hw, fy + y0, fz), (hw, fy + y1, fz + 2), tag="frill", name=f"frill{k}")
            for sx in (1, -1):
                a = sx * hw
                m.box("frill", (min(a, a - sx), fy + y0, fz - 0.5), (max(a, a - sx), fy + y1, fz + 2.5),
                      tag="frill", name="frill_rim")
    hw, _y0, ytop = FRILL[-1]
    m.box("frill", (-hw, fy + ytop - 1, fz - 0.5), (hw, fy + ytop, fz + 2.5), tag="frill", name="frill_rim_top")
    m.bone("frill_male", "frill", (0, fy, fz))
    m.box("frill_male", (-4.5, fy + ytop, fz), (4.5, fy + ytop + 2, fz + 2), tag="frill", name="frill_crest")
    m.box("frill_male", (-4.5, fy + ytop + 2, fz - 0.5), (4.5, fy + ytop + 3, fz + 2.5), tag="frill", name="frill_rim_crest")

    # --- lower jaw
    B("jaw", "jaw_back", (-4, -8, -9, 4, -5, 0), paint=MOUTH_UP)
    B("jaw", "dentary", (-3, -8, -15, 3, -5, -9), paint=MOUTH_UP)
    B("jaw", "predentary", (-1.5, -8, -18, 1.5, -6, -15), tag="beak")
    B("jaw", "tongue", (-2, -6, -14, 2, -5, -6), tag="tongue")
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (5, ay + 0.5, az - 6.5), "r": 1.8, "side": 1},     # big night eyes
                 {"kind": "eye", "bones": ["skull"], "pos": (-5, ay + 0.5, az - 6.5), "r": 1.8, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": (2.5, ay - 1.5, az - 14.5), "r": 0.8, "rx": 1.0, "mul": 0.55, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": (-2.5, ay - 1.5, az - 14.5), "r": 0.8, "rx": 1.0, "mul": 0.55, "side": -1}]

    # --- hind legs: four toes with flattened digging claws, a heel pad
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(2.0, 1.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 2, by - 2, bz - 1), (x + 2, by, bz + 2), tag="limb", name="heel_pad")
        for x0, x1, length in ((-2, -1, 2), (-1, 0, 3), (0, 1, 3), (1, 2, 2)):
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            m.box(T, (a, by - 2, bz - 1 - length), (b, by, bz - 1), tag="limb", name="toe")
            m.box(T, (a, by - 2, bz - 2 - length), (b, by - 1, bz - 1 - length), tag="claw", name="claw")
    m.sym(leg)

    # --- forelimbs: short, five clawed fingers
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, overlap=(1.5, 1.0))
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], -15 * sx, 0))
        H = f"hand_{side}"
        m.box(H, (x - 2, by - 2, bz - 1), (x + 2, by, bz + 2), tag="limb", name="palm")
        for x0, x1, length in ((-2, -1, 1), (-1, 0, 2), (0, 1, 2), (1, 2, 1)):
            a, b = sorted((x - x1 * sx, x - x0 * sx))
            m.box(H, (a, by - 2, bz - 1 - length), (b, by, bz - 1), tag="limb", name="finger")
            m.box(H, (a, by - 1.5, bz - 2 - length), (b, by - 0.5, bz - 1 - length), tag="claw", name="claw")
    m.sym(arm)

    # --- tail: deep and flat-sided, raised by the tall spines into a low sail
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, tpts, "+z", tsecs, overlap=(1.5, 1.0))
    ty, tz = tail["end"]
    m.box("tail4", (-0.5, ty - 1, tz), (0.5, ty + 1, tz + 2), name="tail_tip")
    for (seg, (w, hh)), (ht, step) in zip(zip(tail["segments"], tsecs), SAIL):
        y = tpts[0][0] + hh / 2
        z0 = seg["unposed"][1]
        for z in range(int(z0) + 1, int(z0 + seg["len"]) - 1, step):
            m.box(seg["bone"], (-0.5, y - 1, z), (0.5, y + ht, z + 2), name="sail_spine")

    animations(m)
    return m


def siny_(a, ph=0.0):
    return lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0)


def animations(m):
    NT = 4
    Li = 4.0
    idle = {
        "body": track(pos=wave(8, lambda p: (0, 0.1 * K * (1 + math.sin(2 * math.pi * p)), 0), Li)),   # breathing rises only
        "neck1": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * p), 3 * math.sin(2 * math.pi * (p + 0.3)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * (p + 0.2)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-4 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
    }
    for i in range(NT):
        idle[f"tail{i+1}"] = track(rot=wave(8, siny_(3 + i, -0.1 * i), Li))
    m.anim("idle", Li, True, idle)
    for name, Lc, Ah, Af, bob in (("walk", 1.0, 26, 26, 0.5 * K), ("run", 0.5, 38, 38, 1.0 * K)):
        t = quad_gait(Lc, Ah, Af)
        t["body"] = track(rot=wave(8, lambda p: (0, 2 * math.sin(2 * math.pi * p), 2 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, b=bob: (0, b * 0.5 * (1 + math.cos(4 * math.pi * p)), 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, b=bob / K: (-2 * b * math.cos(4 * math.pi * p), 0, 0), Lc))
        for i in range(NT):
            t[f"tail{i+1}"] = track(rot=wave(8, siny_(4 + i, 0.25 - 0.08 * i), Lc))
        m.anim(name, Lc, True, t)
    # attack: a head-down shove and a bite with the beak
    m.anim("attack", 0.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.25, -8, 0, 0), (0.45, 10, 0, 0), (0.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.25, -6, 0, 0), (0.45, 12, 0, 0), (0.8, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.3, 22, 0, 0), (0.45, 0, 0, 0), (0.8, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.25, -3, 0, 0), (0.45, 3, 0, 0), (0.8, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.25, 0, 0.3 * K, -1 * K), (0.45, 0, 0.5 * K, -2 * K), (0.8, 0, 0, 0)])),
    })
    m.anim("sit", 4.0, True, quad_sit(m, 8, neck=10))
    sit = m.animations[-1]
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
        "skull": track(rot=keys([(0, 0, 0, 0), (0.6, GRAZE[1], 0, 0), (2.3, GRAZE[1], 0, 0), (2.8, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
    })
    dig(m)
    add_knockout(m, lift=0.4, neck_down=-6)
    for a in m.animations:      # eat / beg / tame come from the 1x set: scale their position keys
        if a["name"].split(".")[-1] in ("eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    for nm in ("graze", "attack", "dig"):      # the beak and the chewing jaw stay out of the ground
        fit_to_ground(m, nm, ("neck1", "neck2", "skull", "jaw"))
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "jaw", "body"))


def dig(m):
    # digging: the head goes down between the forefeet and they scrape the sand back in turns, the tail wagging
    arm_l, arm_r, fore_l, fore_r = [], [], [], []
    for k in range(4):
        t0 = 0.5 + k * 0.4
        arm_l += [(t0, -38, 0, 0), (t0 + 0.2, 22, 0, 0)]
        arm_r += [(t0, 22, 0, 0), (t0 + 0.2, -38, 0, 0)]
        fore_l += [(t0, 30, 0, 0), (t0 + 0.2, 10, 0, 0)]
        fore_r += [(t0, 10, 0, 0), (t0 + 0.2, 30, 0, 0)]
    m.anim("dig", 2.6, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.5, -4, 0, 0), (2.1, -4, 0, 0), (2.6, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.5, 0, 0.6, 0), (2.1, 0, 0.6, 0), (2.6, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, -7, 0, 0), (2.1, -7, 0, 0), (2.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.5, -2, 0, 0), (0.9, 1, 0, 0), (1.3, -3, 0, 0), (1.7, 1, 0, 0), (2.1, -2, 0, 0), (2.6, 0, 0, 0)])),
        "upperarm_l": track(rot=keys([(0, 0, 0, 0)] + arm_l + [(2.6, 0, 0, 0)])),
        "upperarm_r": track(rot=keys([(0, 0, 0, 0)] + arm_r + [(2.6, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0)] + fore_l + [(2.6, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0)] + fore_r + [(2.6, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.7, 2, 14, 0), (1.1, 2, -14, 0), (1.5, 2, 14, 0), (1.9, 2, -14, 0), (2.6, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.8, 0, 18, 0), (1.2, 0, -18, 0), (1.6, 0, 18, 0), (2.0, 0, -18, 0), (2.6, 0, 0, 0)])),
    })
