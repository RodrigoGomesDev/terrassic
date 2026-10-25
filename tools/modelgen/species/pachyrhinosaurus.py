"""
Pachyrhinosaurus canadensis  (Late Cretaceous, Campanian-Maastrichtian; Alberta; P. perotorum in the Arctic of Alaska)

Reference:
  - Size (Sternberg 1950; Currie, Langston & Tanke 2008; Fiorillo & Tykoski 2012; Wikipedia): the "thick-nosed
    lizard", a big centrosaurine of 6-8 m and ~4 t, hips ~2.2 m high. Known from huge bonebeds (Pipestone Creek:
    herds of hundreds, every age) and from the polar Prince Creek Formation, where it lived through months of
    darkness: a hardy, cold-country animal.
  - Skull (Currie et al. 2008): no nose horn at all. A broad, flat, rugose bony BOSS covers the top of the snout,
    wider than the face, with a second pair of bosses over the eyes, set apart from it by a shallow groove; a deep
    face with a hooked rostral beak; big nostrils; small pointed epijugals.
  - Frill: short and broad with two big openings (skin-covered in life), small epoccipitals along the rim; from
    the top of the parietal a pair of horns (P3) curves up and forward, with small hooks beside them (P1-P2, P4-P5);
    P. lakustai adds a small spike in the middle (here on the males).
  - Body: the Styracosaurus/Centrosaurus build, larger: a short neck under the frill, a deep barrel trunk, a short
    tail; semi-erect forelimbs with three hoofed inner fingers; pillar hind legs with four short hoofed toes.
  - Skin (centrosaurine impressions): big polygonal scales with a low conical centre among small ones.
  - Colour unknown; kept from the old model: slate grey with darker mottling and a pale belly, a rust-brown boss,
    the frill dark with white spots and a pale rim; males darker with a bigger, redder boss, the middle spike and
    longer horn tips; females browner.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared ceratopsian rig), built
with the construction of the Styracosaurus remaster scaled 1.25x, at the 16 px = 1 m standard. The skull is
~1.3x the real proportion. The "scent" (musk) action is kept.
"""
import math
from paint import vnoise, hash3
from rig import Model, wave, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "pachyrhinosaurus"
K = 1.6  # position keys of the 1x animation set are scaled by this


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
    """Big polygonal scales with a pale conical centre among small ones, dark mottling over the back, a pale belly;
    the rugose boss; the frill dark with white spots, a median bar and a pale rim; keratin horns."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag, bone = cube.tag, cube.bone
    if tag == "boss":                                                        # rugose bone: pitted and knobbly
        n = vnoise(P[0] / 1.2, P[1] / 1.2, P[2] / 1.2, 53)
        return pal["boss"] * (0.8 + 0.4 * n) * (0.88 if tx.edge else 1.0)
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
            return rgb * 0.82                                                # median bar of the parietal
        if hash3(math.floor(P[0] / 2), math.floor(P[1] / 2), 0, 29) > 0.8:
            return pal["frill_spot"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)  # white spots over the dark frill
        ang = math.atan2(P[0], max(0.5, P[1] - fy))
        if int(math.floor(ang * 8.0)) % 2 == 0 and P[1] - fy > 2.5:
            rgb = rgb * 0.93                                                 # vessel grooves
        return rgb
    if tag in ("skin", "limb"):
        if tag == "limb" and bone.startswith(("toes", "hand")) and tx.face != "down":
            return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)  # scutes over the toes
        if tag == "skin" and region == "dorsal" and bone in ("body", "tail1", "neck1", "neck2"):
            if math.sin(P[2] * 0.45) * math.sin(P[0] * 0.5 + 0.8) > 0.42:
                rgb = pal["saddle_dark"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)   # dark mottling
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


PALETTE = {"dorsal": "#4a4e52", "flank": "#6e7276", "belly": "#c8c4b8", "saddle_dark": "#3a3e42",
           "limb": "#5a5e62", "limb_top": "#66686c", "claw": "#2e2c28", "claw_base": "#2e2c28",
           "horn_base": "#5a5048", "horn_tip": "#e8e0d0", "boss": "#8a5a3e", "beak": "#3e3a34",
           "frill": "#3c4044", "frill_edge": "#9a9690", "frill_spot": "#e8e4dc", "epoccipital": "#b8b2a6",
           "tooth": "#d8d0b8", "mouth": "#6e3330", "tongue": "#94504a", "eye": "#c0a040", "pupil": "#140f0a",
           "saddle": "#7a4f2e"}
SEXES = {"male": {"boss": "#a04a30", "dorsal": "#3e4246", "frill": "#2e3236", "frill_spot": "#f4f0e8"},
         "female": {"boss": "#8a6a50", "dorsal": "#5a5650", "flank": "#7e7a72", "frill": "#4e4a44",
                    "frill_spot": "#d4d0c4"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (36, 7.5)                                     # hip joint
TORSO = [("hips", (-12.0, 25.0, -5.0, 12.0, 45.0, 24.0)), ("sacrum", (-7.5, 45.0, 5.0, 7.5, 47.0, 20.0)),
         ("belly", (-15.0, 15.0, -24.0, 15.0, 41.0, -4.0)), ("chest", (-14.0, 15.0, -36.0, 14.0, 37.0, -20.0)),
         ("withers", (-10.0, 37.5, -34.0, 10.0, 39.5, -20.0)), ("back", (-10.5, 41.0, -21.0, 10.5, 43.0, -5.0)),
         ("belly_low", (-12.0, 14.0, -29.0, 12.0, 15.0, -8.0)),
         ("ribs_l", (15.0, 20.0, -21.0, 16.0, 38.0, -7.0)), ("ribs_r", (-16.0, 20.0, -21.0, -15.0, 38.0, -7.0)),
         ("ilium_l", (12.0, 32.5, 0.0, 13.0, 43.5, 18.0)), ("ilium_r", (-13.0, 32.5, 0.0, -12.0, 43.5, 18.0)),
         ("scapula_l", (14.0, 25.0, -34.0, 15.0, 36.0, -25.0)), ("scapula_r", (-15.0, 25.0, -34.0, -14.0, 36.0, -25.0))]
NECK = ([(32.5, -33.8), (32.5, -40.0), (31.2, -43.8)], [(20, 19), (19, 21)])
TAIL = ([(41.2, 21.2), (37.5, 33.8), (33.8, 45.0), (28.8, 55.0)], [(15, 15), (10, 10), (5, 5)])
LEG_X = 11.25
LEG = ([(36, 7.5), (20.0, -1.2), (10.0, 3.8), (4, 1.9)], [(12, 18, -1), (10, 11, 0, "limb"), (8, 8, 0, "limb")])
ARM_X = 13.75
ARM = ([(27.5, -27.5), (15.0, -23.8), (3.5, -26.9)], [(9, 11), (8, 8, 0, "limb")])
HEAD = 0.95                # head units of the Triceratops remaster -> px (the skull ~1.3x the real proportion)
SKULL_PITCH = -10          # face pitched down from the neck line
GRAZE = (-12, -8)          # neck, skull when grazing (the beak just reaches the ground)
FRILL_TILT = 46            # frill plate raised back from the skull roof
# frill rows in head units: (half width, y0, y1) from the base of the plate; broad, larger than the Styracosaurus'
FRILL = [(10, 0, 4), (14, 4, 9), (15, 9, 14), (13, 14, 16)]
# parietal horns in px from the frill centre: (x, row index for the base, length, fan angle, lean back, width); P3 the big
# pair curving up and forward, small hooks P1-P2 beside the midline and P4-P5 down the sides
SPIKES = [(2, 3, 3, -15, 20, 2), (6, 3, 10, 30, -36, 3), (10.5, 2, 4, 55, 15, 2), (13, 1, 3, 78, 10, 2)]


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
    m.box("neck1", (-8, y1 - 12.5, z1 - 6), (8, y1 - 8.5, z1 + 1), name="dewlap")
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

    # --- skull (head units, pitched down by the skull bone): braincase, deep face, hooked beak, no horns
    S("braincase", (-8, -6, -8, 8, 10, 3))
    S("orbits", (-9, -1, -12, 9, 9, -4), paint=MOUTH_DOWN)
    SM("jugal", (9, -8, -12, 11, 4, -3))
    SM("epijugal", (11, -10, -9, 13, -6, -5), tag="horn", paint={"axis": "-y"})
    S("face", (-7, -6, -17, 7, 8, -12), paint=MOUTH_DOWN)
    S("snout", (-5, -6, -22, 5, 7, -17), paint=MOUTH_DOWN)
    S("premaxilla", (-4, -8, -26, 4, 4, -22), paint=MOUTH_DOWN)
    S("rostral", (-2, -8, -28.5, 2, -1, -26), tag="beak")
    S("beak_hook", (-2, -11, -29.5, 2, -8, -27.5), tag="beak")
    # the bosses: a broad flat rugose pad over the whole top of the snout, wider than the face, and a pair over the
    # eyes, set apart by a shallow groove
    S("nasal_boss", (-6, 7, -25, 6, 12, -13), tag="boss")
    S("nasal_boss_top", (-5, 12, -24, 5, 14, -14), tag="boss")
    SM("supraorbital_boss", (3, 9, -12, 7, 12, -5), tag="boss")

    # --- frill: short and broad, rising back from the skull roof, a pale rim with small epoccipitals, the horns
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
    for x, row, L, fan, lean, w in SPIKES:
        y0 = fy + rows[row][2] - 1
        for sx in (1, -1):
            sp = dict(tag="horn", rot=(lean, 0, -fan * sx), origin=(x * sx, y0, fz + 1), paint={"axis": "+y"})
            m.box("frill", (x * sx - w / 2, y0, fz), (x * sx + w / 2, y0 + L - 2, fz + 2), name="spike", **sp)
            t = w - 1
            m.box("frill", (x * sx - t / 2, y0 + L - 2, fz + 0.5), (x * sx + t / 2, y0 + L, fz + 1.5), name="spike_tip", **sp)
            if L >= 9:                                                     # males: longer horn tips
                m.box("male_display", (x * sx - 0.5, y0 + L, fz + 0.5), (x * sx + 0.5, y0 + L + 2, fz + 1.5),
                      name="spike_end", **sp)
    y0 = fy + rows[3][2] - 1                                               # males: the small middle spike
    m.box("male_display", (-1, y0, fz), (1, y0 + 4, fz + 2), name="mid_spike", tag="horn", paint={"axis": "+y"})
    # males: a taller crown on the nasal boss (on the frill's display bone, turned back into the skull's frame)
    x0, y0_, z0 = at(-4, 14, -23)
    x1, y1_, z1 = at(4, 15, -15)
    m.box("male_display", (x0, y0_, z0), (x1, y1_, z1), name="boss_crown", tag="boss",
          rot=(-FRILL_TILT, 0, 0), origin=(0, fy, fz))

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
        m.box(f"shin_{side}", (x - 4.5, sy - 9, sz + 4), (x + 4.5, sy - 1, sz + 8), tag="limb", name="calf")
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 4, by - 4, bz - 1), (x + 4, by, bz + 5), tag="limb", name="heel_pad")
        for x0, x1, length in ((-4, -2, 4), (-2, 0, 5), (0, 2, 5), (2, 4, 3)):
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            m.box(T, (a, by - 4, bz - 1 - length), (b, by, bz - 1), tag="limb", name="toe")
            m.box(T, (a, by - 4, bz - 3 - length), (b, by - 1, bz - 1 - length), tag="claw", name="hoof")
    m.sym(leg)

    # --- forelimbs: semi-erect, elbow out, the hand turned so the three hoofed fingers point forward and out
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, overlap=(2.0, 1.0))
        uy, uz = ch["segments"][0]["unposed"]
        a = x + 4.5 * sx
        m.box(f"upperarm_{side}", (min(a, a + sx), uy - 10, uz - 2.5), (max(a, a + sx), uy - 2, uz + 3.5),
              name="elbow_flare")
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], -22 * sx, 0))
        H = f"hand_{side}"
        m.box(H, (x - 4, by - 3, bz - 2), (x + 4, by + 1, bz + 3), tag="limb", name="palm")
        for x0, x1, length in ((-4, -1, 4), (-1, 1, 4), (1, 4, 3)):          # digits I-III, hoofed
            a, b = sorted((x - x1 * sx, x - x0 * sx))
            m.box(H, (a, by - 3, bz - 2 - length), (b, by, bz - 2), tag="limb", name="finger")
            m.box(H, (a, by - 3, bz - 4 - length), (b, by - 1, bz - 2 - length), tag="claw", name="hoof")
        a = x + 4 * sx                                                     # digits IV-V: small, no hooves
        m.box(H, (min(a, a + sx), by - 3, bz - 3), (max(a, a + sx), by, bz - 1), tag="limb", name="finger_small")
    m.sym(arm)

    # --- tail: short, carried off the ground
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3"], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 1.0))
    ty, tz = tail["end"]
    m.box("tail3", (-2, ty - 2, tz), (2, ty + 2, tz + 3), name="tail_tip")
    t1y, t1z = tail["segments"][0]["unposed"]
    m.box("tail1", (-5, t1y - 11, t1z + 1), (5, t1y - 7, t1z + 10), name="chevrons")   # deep tail base

    add_saddle(m, "body", 45, -11, 4, 15, 15.5, flap=11)
    animations(m)
    scent(m)
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
    # attack: the charge; head low, then the boss rammed forward and up
    m.anim("attack", 0.9, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, -8, 0, 0), (0.5, 12, 0, 0), (0.9, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.3, -6, 0, 0), (0.5, 16, 0, 0), (0.9, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.3, -3, 0, 0), (0.5, 3, 0, 0), (0.9, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.3, 0, 1.4 * K, -1.5 * K), (0.5, 0, 0.6 * K, -3 * K), (0.9, 0, 0, 0)])),
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
    for bone, f in (("skull", 0.4), ("body", 0.12)):    # less head and body dip than the generic eat (forefeet planted)
        eat["bones"][bone]["rotation"] = [[k[0], k[1] * f, k[2], k[3]] for k in eat["bones"][bone]["rotation"]]
    for a in m.animations:      # eat / beg / tame come from the 1x set: scale their position keys
        if a["name"].split(".")[-1] in ("eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    for nm in ("graze", "eat", "attack"):      # the beak and the chewing jaw stay out of the ground
        fit_to_ground(m, nm, ("neck1", "neck2", "skull", "jaw"))
    tame = next(a for a in m.animations if a["name"].endswith(".tame"))      # a smaller sway of the wide body
    tame["bones"]["body"]["rotation"] = [[k[0], k[1], k[2], k[3] * 0.5] for k in tame["bones"]["body"]["rotation"]]


def scent(m):
    # the musk: head up, a long snort, a shiver down the body and a tail swish
    m.anim("scent", 1.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.4, 16, 0, 0), (1.3, 16, 0, 0), (1.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.4, 8, 0, 0), (0.7, 8, 0, 6), (1.0, 8, 0, -6), (1.3, 8, 0, 0), (1.8, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.4, -8, 0, 0), (0.5, -4, 0, 0), (0.6, -10, 0, 0), (0.7, -4, 0, 0), (0.8, -10, 0, 0), (1.3, 0, 0, 0), (1.8, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.6, 0, 0, 2), (0.8, 0, 0, -2), (1.0, 0, 0, 1.5), (1.2, 0, 0, 0), (1.8, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.5, 0, 18, 0), (0.9, 0, -18, 0), (1.3, 0, 12, 0), (1.8, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.6, 0, 24, 0), (1.0, 0, -24, 0), (1.4, 0, 14, 0), (1.8, 0, 0, 0)])),
    })
