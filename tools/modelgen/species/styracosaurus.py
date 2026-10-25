"""
Styracosaurus albertensis  (Late Cretaceous, Campanian; Dinosaur Park Formation, Alberta)

Reference:
  - Size (Lambe 1913; Ryan, Holmes & Russell 2007; Holmes & Ryan 2013): a centrosaurine of ~5-5.5 m and ~2.7 t,
    hips ~1.8 m high; bonebeds show it lived in herds. Lighter and shorter-faced than the Triceratops.
  - Skull (Ryan et al. 2007; Wikipedia): a deep face ending in a hooked rostral beak over the predentary; one long,
    straight, upright nasal horn (up to ~57 cm) over the big nostrils; no real brow horns, only low rounded bumps
    over the eyes; pointed epijugals on the cheeks.
  - Frill (Ryan et al. 2007): short and broad, made of the parietal (with two big openings, covered by skin in life)
    and the squamosals, edged with small epoccipitals; the parietal carries the famous spikes: small hooks near the
    midline (P1-P2) and, from P3 to P5, four to six long spikes up to ~55 cm that radiate back and out, the
    innermost pair the longest, varying from animal to animal.
  - Body: a short neck under the frill, a deep barrel-shaped trunk highest over the hips, a short tail; semi-erect
    forelimbs with three hoofed inner fingers; pillar hind legs with four short hoofed toes and a heel pad.
  - Skin (centrosaurine skin impressions): big polygonal scales with a low conical centre among small ones.
  - Colour unknown; kept from the old model: sandy brown with a dark saddle, the frill rust with cream spikes and a
    pair of eye spots on males, dull on females.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared ceratopsian rig), built
with the construction rules of the Triceratops remaster at ~20 px = 1 m (denser than the 16 px standard so the
spikes and the hoofed fingers keep their detail). The skull is ~1.35x the real proportion. Males carry longer
spike tips ("male_display").
"""
import math
from rig import Model, wave, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "styracosaurus"
K = 1.5  # position keys of the 1x animation set are scaled by this


# ---------------------------------------------------------------------------------------------------- paint
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
    """Big polygonal scales with a pale conical centre among small ones, dark saddle blotches over the back, a pale
    belly; the frill a rust display field with a dark median band, a pale rim and two eye spots; keratin horns."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag, bone = cube.tag, cube.bone
    if tag in ("claw", "saddle", "eye", "mouth", "tongue", "horn", "beak"):
        if tag == "horn" and (tx.i + 2 * tx.j) % 5 == 0:
            return rgb * 0.93                                                # keratin grain
        return rgb
    if tag == "epoccipital":
        return rgb * (1.08 if tx.face == "up" else 0.96)
    if tag == "frill":
        if cube.name.startswith("frill_rim"):
            return pal["frill_edge"] * (0.92 if (tx.i + tx.j) % 3 == 0 else 1.0)
        fy = model._frill_base
        if abs(P[0]) < 1.2:
            return rgb * 0.78                                                # median bar of the parietal
        sx, sy, r2 = model._frill_spot
        d = (abs(P[0]) - sx) ** 2 + (P[1] - fy - sy) ** 2
        if d < r2:
            return pal["frill_spot"] * 0.95 if d > r2 * 0.35 else rgb * 0.55   # eye spots over the openings
        ang = math.atan2(P[0], max(0.5, P[1] - fy))
        if int(math.floor(ang * 8.0)) % 2 == 0 and P[1] - fy > 2.5:
            rgb = rgb * 0.92                                                 # vessel grooves
        return rgb
    if tag in ("skin", "limb"):
        if tag == "limb" and bone.startswith(("toes", "hand")) and tx.face != "down":
            return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)  # scutes over the toes
        if tag == "skin" and region == "dorsal" and bone in ("body", "tail1", "neck1", "neck2"):
            if math.sin(P[2] * 0.45) * math.sin(P[0] * 0.5 + 0.8) > 0.42:
                rgb = pal["saddle_dark"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)   # dark saddle blotches
        big, hb = _cell(P, 3.0)
        if hb % 5 == 0 and region != "belly":
            if big < 0.12:
                return rgb * 0.86
            if big > 0.38:
                return rgb * 1.16
            return rgb * 1.05
        edge, _h = _cell(P, 1.5)
        if edge < 0.12:
            rgb = rgb * 0.94                                                 # small basement scales
    return rgb


PALETTE = {"dorsal": "#6e5a3c", "flank": "#a08660", "belly": "#d8c8a0", "saddle_dark": "#4a3c28",
           "limb": "#7a6446", "limb_top": "#8a7454", "claw": "#38312a", "claw_base": "#38312a",
           "horn_base": "#6a5838", "horn_tip": "#efe6ca", "beak": "#4a4038",
           "frill": "#9a4e2e", "frill_edge": "#eadcbc", "frill_spot": "#e0b060", "epoccipital": "#dccca4",
           "tooth": "#d8d0b8", "mouth": "#6e3330", "tongue": "#94504a", "eye": "#b88a2e", "pupil": "#140f0a",
           "saddle": "#7a4f2e"}
SEXES = {"male": {"frill": "#b04a26", "frill_edge": "#f4e6c4", "frill_spot": "#f0c060", "dorsal": "#5e4c32"},
         "female": {"frill": "#7c5a40", "frill_edge": "#cbbd9b", "frill_spot": "#b89a68", "flank": "#a89470"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (29, 6)                                       # hip joint
TORSO = [("hips", (-9.5, 20, -4, 9.5, 36, 19)), ("sacrum", (-6, 36, 4, 6, 38, 16)),
         ("belly", (-12, 12, -19, 12, 33, -3)), ("chest", (-11, 12, -29, 11, 30, -16)),
         ("withers", (-8, 30, -27, 8, 32, -16)), ("back", (-8.5, 33, -17, 8.5, 35, -4)),
         ("belly_low", (-9.5, 11, -23, 9.5, 12, -6)),
         ("ribs_l", (12, 16, -17, 13, 30, -6)), ("ribs_r", (-13, 16, -17, -12, 30, -6)),
         ("ilium_l", (9.5, 26, 0, 10.5, 35, 14)), ("ilium_r", (-10.5, 26, 0, -9.5, 35, 14)),
         ("scapula_l", (11, 20, -27, 12, 29, -20)), ("scapula_r", (-12, 20, -27, -11, 29, -20))]
NECK = ([(26, -27), (26, -32), (25, -35)], [(16, 15), (15, 16)])
TAIL = ([(33, 17), (30, 27), (27, 36), (23, 44)], [(12, 12), (8, 8), (4, 4)])
LEG_X = 9
LEG = ([(29, 6), (16, -1), (8, 3), (3, 1.5)], [(10, 14, -1), (8, 9, 0, "limb"), (6, 6, 0, "limb")])
ARM_X = 11
ARM = ([(22, -22), (12, -19), (2.5, -21.5)], [(7, 9), (6, 6, 0, "limb")])
HEAD = 0.75                # head units of the Triceratops remaster -> px (the skull ~1.35x the real proportion)
SKULL_PITCH = -10          # face pitched down from the neck line
GRAZE = (-12, -8)          # neck, skull when grazing (the beak just reaches the ground)
FRILL_TILT = 46            # frill plate raised back from the skull roof
# frill rows in head units: (half width, y0, y1) from the base of the plate; short and broad
FRILL = [(9, 0, 3), (12, 3, 7), (13, 7, 11), (11, 11, 13)]
# parietal spikes in px from the frill centre: (x, row index for the base, length, fan angle); P1-P2 hooks, P3-P5
SPIKES = [(1.5, 3, 3, -25), (4.5, 3, 14, 10), (7.5, 3, 12, 32), (9.5, 2, 9, 58)]


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern

    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)

    # --- neck: short and thick, mostly under the frill
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(3.0, 2.0))
    y1, z1 = neck["segments"][0]["unposed"]
    m.box("neck1", (-6.5, y1 - 10, z1 - 5), (6.5, y1 - 7, z1 + 1), name="dewlap")
    ay, az = neck["end"]
    h = lambda v: int(round(v * HEAD))
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (SKULL_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay + h(-6), az + h(1)))

    def at(x, y, z):
        return (h(x), ay + h(y), az + h(z))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, at(x0, y0, z0), at(x1, y1, z1), tag=tag, name=name, **kw)

    def S(name, box, tag="skin", **kw):
        return B("skull", name, box, tag, **kw)

    def SM(name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        B("skull", name + "_l", box, tag, **kw)
        B("skull", name + "_r", (-x1, y0, z0, -x0, y1, z1), tag, **kw)

    def J(name, box, tag="skin", **kw):
        return B("jaw", name, box, tag, **kw)

    # --- skull (head units, pitched down by the skull bone): braincase, deep face, hooked beak, the tall nose horn
    S("braincase", (-8, -6, -8, 8, 10, 3))
    S("orbits", (-9, -1, -12, 9, 9, -4), paint=MOUTH_DOWN)
    SM("brow_bump", (4, 9, -11, 7, 12, -6), tag="horn", paint={"axis": "+y"})   # low bumps, no brow horns
    SM("jugal", (9, -8, -12, 11, 4, -3))
    SM("epijugal", (11, -10, -9, 13, -6, -5), tag="horn", paint={"axis": "-y"})
    S("face", (-7, -6, -17, 7, 8, -12), paint=MOUTH_DOWN)
    S("snout", (-5, -6, -22, 5, 7, -17), paint=MOUTH_DOWN)
    S("premaxilla", (-4, -8, -26, 4, 4, -22), paint=MOUTH_DOWN)
    S("rostral", (-2, -8, -28.5, 2, -1, -26), tag="beak")
    S("beak_hook", (-2, -11, -29.5, 2, -8, -27.5), tag="beak")
    S("nasal_boss", (-3, 7, -22, 3, 10, -15))
    o = at(0, 10, -18.5)                                   # the long straight nose horn, a little raked forward
    S("nasal_horn", (-2.5, 10, -21, 2.5, 16, -16), tag="horn", rot=(-8, 0, 0), origin=o, paint={"axis": "+y"})
    S("nasal_mid", (-1.5, 16, -20, 1.5, 22, -17), tag="horn", rot=(-8, 0, 0), origin=o, paint={"axis": "+y"})
    S("nasal_tip", (-1, 22, -19.5, 1, 26, -17.5), tag="horn", rot=(-8, 0, 0), origin=o, paint={"axis": "+y"})

    # --- frill: short and broad, rising back from the skull roof, a pale rim with small epoccipitals, the spikes
    fy, fz = ay + h(8), az + h(-1)
    m._frill_base = fy
    m.bone("frill", "skull", (0, fy, fz), (FRILL_TILT, 0, 0))
    rows = [(h(hw), h(y0), h(y1)) for hw, y0, y1 in FRILL]
    m._frill_spot = (rows[2][0] * 0.5, (rows[1][2] + rows[2][2]) * 0.5, 4.5)
    for k, (hw, y0, y1) in enumerate(rows):
        if k >= 1:                                                         # the base row sits inside the neck
            m.box("frill", (-hw, fy + y0, fz), (hw, fy + y1, fz + 2), tag="frill", name=f"frill{k}")
        if k >= 1:
            for sx in (1, -1):                                             # squamosal rim
                a = sx * hw
                m.box("frill", (min(a, a - 1 * sx), fy + y0, fz - 0.5), (max(a, a - 1 * sx), fy + y1, fz + 2.5),
                      tag="frill", name="frill_rim")
    hw, _y0, ytop = rows[-1]
    m.box("frill", (-hw, fy + ytop - 1, fz - 0.5), (hw, fy + ytop, fz + 2.5), tag="frill", name="frill_rim_top")
    for sx in (1, -1):                                                     # small epoccipitals on the squamosals
        for (hw, y0, y1) in rows[1:3]:
            a = sx * hw
            m.box("frill", (min(a, a + sx), fy + y0 + 1, fz), (max(a, a + sx), fy + y0 + 3, fz + 2),
                  tag="epoccipital", name="epoccipital")
    m.bone("male_display", "frill", (0, fy, fz))
    for x, row, L, fan in SPIKES:
        y0 = fy + rows[row][2] - 1
        for sx in (1, -1):
            sp = dict(tag="horn", rot=(18, 0, -fan * sx), origin=(x * sx, y0, fz + 1), paint={"axis": "+y"})
            m.box("frill", (x * sx - 1, y0, fz), (x * sx + 1, y0 + L - 2, fz + 2), name="spike", **sp)
            m.box("frill", (x * sx - 0.5, y0 + L - 2, fz + 0.5), (x * sx + 0.5, y0 + L, fz + 1.5), name="spike_tip", **sp)
            if L >= 9:                                                     # males: longer spike tips
                m.box("male_display", (x * sx - 0.5, y0 + L, fz + 0.5), (x * sx + 0.5, y0 + L + 2, fz + 1.5),
                      name="spike_end", **sp)

    # --- lower jaw: coronoid, dentary, predentary beak, tongue
    J("jaw_back", (-8, -13, -10, 8, -6, 1), paint=MOUTH_UP)
    J("dentary", (-6, -12, -21, 6, -6, -10), paint=MOUTH_UP)
    J("jaw_front", (-3, -11, -26, 3, -7, -21), paint=MOUTH_UP)
    J("predentary", (-3, -12, -28, 3, -9, -26), tag="beak")
    J("tongue", (-3, -7, -21, 3, -6, -8), tag="tongue")
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(9, 5, -8), "r": 1.1, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-9, 5, -8), "r": 1.1, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(5, 1, -20), "r": 1.1, "rx": 1.3, "mul": 0.6, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-5, 1, -20), "r": 1.1, "rx": 1.3, "mul": 0.6, "side": -1}]

    # --- hind legs: pillar legs, four short hoofed toes (the fourth small), a heel pad
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(3.0, 2.0))
        sy, sz = ch["segments"][1]["unposed"]
        m.box(f"shin_{side}", (x - 3.5, sy - 7, sz + 3), (x + 3.5, sy - 1, sz + 6), tag="limb", name="calf")
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 3, by - 3, bz - 1), (x + 3, by, bz + 4), tag="limb", name="heel_pad")
        for x0, x1, length in ((-3, -1, 3), (-1, 1, 4), (1, 3, 4), (3, 4, 2)):
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            m.box(T, (a, by - 3, bz - 1 - length), (b, by, bz - 1), tag="limb", name="toe")
            m.box(T, (a, by - 3, bz - 2 - length), (b, by - 1, bz - 1 - length), tag="claw", name="hoof")
    m.sym(leg)

    # --- forelimbs: semi-erect, elbow out, the hand turned so the three hoofed fingers point forward and out
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, overlap=(2.0, 1.0))
        uy, uz = ch["segments"][0]["unposed"]
        a = x + 3.5 * sx
        m.box(f"upperarm_{side}", (min(a, a + sx), uy - 8, uz - 2), (max(a, a + sx), uy - 2, uz + 3),
              name="elbow_flare")
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], -22 * sx, 0))
        H = f"hand_{side}"
        m.box(H, (x - 3, by - 2, bz - 1.5), (x + 3, by + 1, bz + 2.5), tag="limb", name="palm")
        for x0, x1, length in ((-3, -1, 3), (-1, 1, 3), (1, 3, 2)):          # digits I-III, hoofed
            a, b = sorted((x - x1 * sx, x - x0 * sx))
            m.box(H, (a, by - 2, bz - 1.5 - length), (b, by, bz - 1.5), tag="limb", name="finger")
            m.box(H, (a, by - 2, bz - 2.5 - length), (b, by - 1, bz - 1.5 - length), tag="claw", name="hoof")
        a = x + 3 * sx                                                     # digits IV-V: small, no hooves
        m.box(H, (min(a, a + sx), by - 2, bz - 2.5), (max(a, a + sx), by, bz - 0.5), tag="limb", name="finger_small")
    m.sym(arm)

    # --- tail: short, carried off the ground
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3"], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 1.0))
    ty, tz = tail["end"]
    m.box("tail3", (-1.5, ty - 1.5, tz), (1.5, ty + 1.5, tz + 2), name="tail_tip")
    t1y, t1z = tail["segments"][0]["unposed"]
    m.box("tail1", (-4, t1y - 9, t1z + 1), (4, t1y - 6, t1z + 8), name="chevrons")   # deep tail base

    add_saddle(m, "body", 36, -9, 3, 12, 12.5, flap=9)
    animations(m)
    return m


def siny_(a, ph=0.0):
    return lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0)


def animations(m):
    Li = 4.0
    idle = {
        "body": track(pos=wave(8, lambda p: (0, 0.125 * K * (1 + math.sin(2 * math.pi * p)), 0), Li)),   # breathing rises only
        "neck1": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * p), 2.5 * math.sin(2 * math.pi * (p + 0.3)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (1.5 * math.sin(2 * math.pi * (p + 0.2)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-4 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
        "tail1": track(rot=wave(8, siny_(3), Li)),
        "tail2": track(rot=wave(8, siny_(4, -0.1), Li)),
        "tail3": track(rot=wave(8, siny_(6, -0.2), Li)),
    }
    m.anim("idle", Li, True, idle)
    for name, Lc, Ah, Af, bob in (("walk", 1.6, 20, 20, 0.6 * K), ("run", 0.8, 30, 30, 1.2 * K)):
        t = quad_gait(Lc, Ah, Af)
        t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 1.5 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, b=bob: (0, b * 0.5 * (1 + math.cos(4 * math.pi * p)), 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, b=bob / K: (-2 * b * math.cos(4 * math.pi * p), 0, 0), Lc))
        t["tail1"] = track(rot=wave(8, siny_(4, 0.25), Lc))
        t["tail2"] = track(rot=wave(8, siny_(5, 0.15), Lc))
        t["tail3"] = track(rot=wave(8, siny_(7, 0.05), Lc))
        m.anim(name, Lc, True, t)
    # attack: the charge; head low, then the nose horn thrust forward and up
    m.anim("attack", 0.9, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, -8, 0, 0), (0.5, 12, 0, 0), (0.9, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.3, -6, 0, 0), (0.5, 16, 0, 0), (0.9, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.3, -3, 0, 0), (0.5, 3, 0, 0), (0.9, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.3, 0, 0.3 * K, -1.5 * K), (0.5, 0, 0.6 * K, -3 * K), (0.9, 0, 0, 0)])),
    })
    m.anim("sit", 4.0, True, quad_sit(m, 12, neck=12))
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
    add_knockout(m, lift=0.42, neck_down=0)       # the wide body and frill rest higher on the ground
    eat = next(a for a in m.animations if a["name"].endswith(".eat"))
    for bone in ("skull", "body"):                      # less head and body dip than the generic eat
        eat["bones"][bone]["rotation"] = [[k[0], k[1] * 0.4, k[2], k[3]] for k in eat["bones"][bone]["rotation"]]
    for a in m.animations:      # eat / beg / tame come from the 1x set: scale their position keys
        if a["name"].split(".")[-1] in ("eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    for nm in ("graze", "eat", "attack"):      # the beak and the chewing jaw stay out of the ground
        fit_to_ground(m, nm, ("neck1", "neck2", "skull", "jaw"))
