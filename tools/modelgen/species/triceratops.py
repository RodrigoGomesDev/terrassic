"""
Triceratops horridus / T. prorsus  (Maastrichtian, western North America)

Reference:
  - Size (Wikipedia; Hatcher 1907; Scannella & Horner 2010): 8-9 m long, ~2.9-3 m at the hips, 6-12 t. Skulls up
    to ~2.5 m ("Big John" 2.62 m long and 2.0 m wide across the frill), about a third of the body.
  - Skull (Hatcher, Marsh & Lull 1907; Forster 1996; Horner & Goodwin 2006): an unpaired rostral bone makes the
    hooked upper beak and the predentary the lower one; a short thick nasal horn (longer and more upright in
    T. prorsus); two brow (postorbital) horns ~1 m long with the keratin sheath, rising forward and curving
    forward with age; a deep face with the large narial opening in front; jugals flaring out into a pointed
    epijugal "cheek horn" under each eye; a SOLID frill (no openings, unlike every other chasmosaurine), about as
    long as the face and wider than the body, with a low median ridge and grooves left by blood vessels; its edge
    carries triangular epoccipitals (~5 on each squamosal, ~7 along the parietal), flattened in old adults.
  - Body: short neck hidden under the frill; deep, barrel-shaped rib cage, the back rising from the shoulders to
    the long sacrum over the hips; short, deep tail held off the ground.
  - Limbs (Fujiwara 2009; Johnson & Ostrom 1995): forelimbs semi-erect with the elbows a little out, hands
    turned so the three hoofed inner fingers point forward and out (digits IV-V small, without hooves); pillar
    hind legs, femur longer than the tibia, four short hoofed toes and a fleshy heel pad.
  - Skin ("Lane", HMNS 2002.1): large polygonal scales up to ~10 cm, many with a low conical point in the centre,
    set among smaller ones; no quills.

v2x (2026-10-24, remaster after the T. rex v3, Rodrigo: "todos os dinos tem que ter essas proporções mais
detalhadas"): modelled at 16 px = 1 m like the T. rex v3, so one texture pixel is one vanilla pixel in game. The
skull is ~1.2x the real proportion. render_scale 0.5 = authoring scale; the in-game size comes from SIZES in
tools/javagen/gen_species.py (MODEL_SCALE ~0.95 for 9 m).
"""
import math
from rig import Model, wave, sinx, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "triceratops"
K = 2.0  # position keys of the 1x animation set are scaled by this


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
    """Lane-specimen scales (big polygons with a pale conical centre among small ones), a darker saddle band
    pattern on the back, pale belly, a display frill (rust field, dark radiating vessel grooves, a pale border and
    epoccipitals) and keratin horns."""
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
        # radiating vessel grooves from the base of the frill, a darker median band and two pale eye spots
        fy = model._frill_base
        ang = math.atan2(P[0], max(0.5, P[1] - fy))
        if abs(P[0]) < 1.6:
            return rgb * 0.78
        if int(math.floor(ang * 9.0)) % 2 == 0 and (tx.i + tx.j) % 2 == 0:
            rgb = rgb * 0.88
        if model._frill_spots:
            d = (abs(P[0]) - 8.0) ** 2 + (P[1] - fy - 13.0) ** 2
            if d < 10:
                return pal["frill_edge"] * 0.92 if d > 3.5 else rgb * 0.6
        return rgb
    if tag in ("skin", "limb"):
        if tag == "limb" and bone.startswith(("toes", "hand")) and tx.face != "down":
            return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)  # scutes over the toes
        if tag == "skin" and region in ("dorsal", "flank") and bone in ("body", "tail1", "tail2"):
            band = math.sin(P[2] * 2 * math.pi / 22 + 0.4 * math.sin(P[0] * 0.2))
            if band > 0.45 and (region == "dorsal" or tx.cy > 0.55):
                rgb = rgb * 0.84                                             # broad saddle bands
        big, hb = _cell(P, 4.0)
        if hb % 5 == 0 and region != "belly":
            # Lane feature scale: a dark rim and a pale conical centre
            if big < 0.12:
                return rgb * 0.86
            if big > 0.38:
                return rgb * 1.16
            return rgb * 1.05
        edge, _h = _cell(P, 2.0)
        if edge < 0.12:
            rgb = rgb * 0.94                                                 # small basement scales
    return rgb


PALETTE = {"dorsal": "#57503f", "flank": "#7a6d55", "belly": "#c8b994", "limb": "#5f5645", "limb_top": "#72674f",
           "claw": "#3a322a", "claw_base": "#3a322a", "horn_base": "#7a6748", "horn_tip": "#efe6cc",
           "beak": "#4d4238", "frill": "#9a4e2e", "frill_edge": "#e6d6b2", "epoccipital": "#d9c8a0",
           "tooth": "#d8d0b8", "mouth": "#6e3330", "tongue": "#94504a", "eye": "#b88a2e", "pupil": "#140f0a"}
SEXES = {"male": {"frill": "#a8482a", "frill_edge": "#f0e2c0", "epoccipital": "#eadbb6", "horn_tip": "#f4ecd2"},
         "female": {"frill": "#7c6248", "frill_edge": "#cbbd9b", "epoccipital": "#c2b391",
                    "dorsal": "#5c5444", "flank": "#7e715b"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (40, 8)                                       # hip joint
TORSO = [("hips", (-13, 28, -6, 13, 50, 26)), ("sacrum", (-8, 50, 6, 8, 52, 22)),
         ("belly", (-17, 17, -26, 17, 46, -4)), ("chest", (-15, 16, -40, 15, 42, -22)),
         ("withers", (-11, 42, -38, 11, 45, -22)), ("back", (-12, 46, -24, 12, 49, -6)),
         ("belly_low", (-13, 15, -32, 13, 17, -8)),
         ("ribs_l", (17, 22, -24, 18, 42, -8)), ("ribs_r", (-18, 22, -24, -17, 42, -8)),
         ("ilium_l", (13, 36, 0, 14, 48, 20)), ("ilium_r", (-14, 36, 0, -13, 48, 20)),
         ("scapula_l", (15, 28, -38, 16, 40, -28)), ("scapula_r", (-16, 28, -38, -15, 40, -28))]
NECK = ([(36, -38), (36, -44), (35, -49)], [(20, 20), (18, 18)])
TAIL = ([(46, 24), (42, 38), (37, 50), (31, 62)], [(16, 16), (10, 11), (6, 6)])
LEG_X = 13
LEG = ([(40, 8), (22, -1), (8, 4), (3, 2)], [(14, 20, -1), (11, 12, 0, "limb"), (9, 8, 0, "limb")])
ARM_X = 15
ARM = ([(31, -31), (17, -26), (3.6, -30)], [(10, 12), (9, 9, 0, "limb")])
HEAD = 1.35                # skull size relative to the real proportion
SKULL_PITCH = -10          # face pitched down from the neck line
GRAZE = (-10, -6)          # neck, skull when grazing (the beak just reaches the ground)
EAT_NECK = 0               # eat (taming): the big head only dips a little to reach the food
FRILL_TILT = 40            # frill plate raised back from the skull roof
# frill rows: (half width, y0, y1) from the base of the plate
FRILL = [(10, 0, 3), (13, 3, 8), (15, 8, 13), (14, 13, 16), (12, 16, 18), (7, 18, 19)]


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m._frill_spots = False

    def mirror(bone, frm, to, **kw):
        name = kw.pop("name")
        m.box(bone, frm, to, name=name + "_l", **kw)
        m.box(bone, (-to[0], frm[1], frm[2]), (-frm[0], to[1], to[2]), name=name + "_r", **kw)

    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)

    # --- neck: short and thick, mostly under the frill
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(2.0, 0.5))
    y1, z1 = neck["segments"][0]["unposed"]
    m.box("neck1", (-8, y1 - 12, z1 - 7), (8, y1 - 9, z1 + 1), name="dewlap")
    ay, az = neck["end"]
    h = lambda v: int(round(v * HEAD))                          # skull drawn at HEAD x the real proportion
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

    # --- skull (authored level, pitched down by the skull bone): braincase, deep cheeks, face, beak
    S("braincase", (-8, -6, -8, 8, 10, 3))
    S("orbits", (-9, -1, -12, 9, 10, -4), paint=MOUTH_DOWN)
    S("horn_bases", (-7, 10, -10, 7, 12, -3))
    SM("jugal", (9, -8, -11, 11, 5, -2))                                  # flaring cheeks
    SM("epijugal", (11, -10, -8, 13, -6, -4), tag="horn", paint={"axis": "-y"})
    S("face", (-7, -6, -18, 7, 8, -12), paint=MOUTH_DOWN)                 # maxilla and nasals
    S("snout", (-5, -6, -23, 5, 6, -18), paint=MOUTH_DOWN)
    S("premaxilla", (-4, -8, -27, 4, 4, -23), paint=MOUTH_DOWN)
    S("rostral", (-2, -9, -30, 2, -1, -27), tag="beak")                    # unpaired rostral bone: upper beak
    S("beak_hook", (-2, -12, -31, 2, -9, -29), tag="beak")
    S("nasal_boss", (-2, 6, -21, 2, 9, -15))                              # base of the nose horn
    o = at(0, 9, -18.5)
    S("nasal_horn", (-1.5, 9, -20, 1.5, 13, -17), tag="horn", rot=(-12, 0, 0), origin=o, paint={"axis": "+y"})
    S("nasal_tip", (-1, 13, -20, 1, 15, -18), tag="horn", rot=(-12, 0, 0), origin=o, paint={"axis": "+y"})

    # --- brow horns: ~1 m, rising forward and out, the tip curving forward
    for side, sx in (("l", 1), ("r", -1)):
        H, T = f"brow_horn_{side}", f"brow_tip_{side}"
        m.bone(H, "skull", at(5 * sx, 11, -6), (52, -14 * sx, 0))
        B(H, "horn_base", (5 * sx - 2, 9, -14, 5 * sx + 2, 13, -4), tag="horn", paint={"axis": "-z"})
        m.bone(T, H, at(5 * sx, 11, -13), (-24, 0, 0))
        B(T, "horn_mid", (5 * sx - 1.5, 9.5, -21, 5 * sx + 1.5, 12.5, -12), tag="horn", paint={"axis": "-z"})
        x = h(5 * sx)
        m.box(T, (x - 0.5, ay + h(10.5), az + h(-25)), (x + 0.5, ay + h(10.5) + 1, az + h(-20)), tag="horn",
              name="horn_tip", paint={"axis": "-z"})

    # --- frill: a solid plate rising back from the skull roof, median ridge, thick rim, epoccipitals
    fy, fz = ay + h(8), az + h(-1)
    m._frill_base = fy
    m.bone("frill", "skull", (0, fy, fz), (FRILL_TILT, 0, 0))
    rows = [(h(hw), h(y0), h(y1)) for hw, y0, y1 in FRILL]
    for k, (hw, y0, y1) in enumerate(rows):
        m.box("frill", (-hw, fy + y0, fz), (hw, fy + y1, fz + 2), tag="frill", name=f"frill{k}")
        if k >= 1:
            for sx in (1, -1):                                             # squamosal rim, proud at the back
                a = sx * hw
                m.box("frill", (min(a, a - 2 * sx), fy + y0, fz), (max(a, a - 2 * sx), fy + y1, fz + 3),
                      tag="frill", name="frill_rim")
    hw, _y0, ytop = rows[-1]
    m.box("frill", (-hw, fy + ytop - 1, fz), (hw, fy + ytop, fz + 3), tag="frill", name="frill_rim_top")
    m.box("frill", (-1, fy + 1, fz - 1), (1, fy + ytop - 2, fz), tag="frill", name="frill_ridge")
    # epoccipitals: 5 along the parietal edge, 6 on each squamosal edge
    for x in (-6, -3, 0, 3, 6):
        m.box("frill", (x - 1, fy + ytop, fz), (x + 1, fy + ytop + 2, fz + 2), tag="epoccipital", name="epoccipital")
    for sx in (1, -1):
        for (hw, y0, y1) in rows[1:5]:
            for yy in (y0 + 1, (y0 + y1) // 2 + 1) if y1 - y0 > 5 else (y0 + 1,):
                a = sx * hw
                m.box("frill", (min(a, a + 2 * sx), fy + yy, fz), (max(a, a + 2 * sx), fy + yy + 2, fz + 2),
                      tag="epoccipital", name="epoccipital")
        a = sx * rows[4][0]
        m.box("frill", (min(a - 2 * sx, a), fy + rows[4][2], fz), (max(a - 2 * sx, a), fy + rows[4][2] + 2, fz + 2),
              tag="epoccipital", name="epoccipital")

    # --- lower jaw: coronoid, dentary, predentary beak, tongue
    J("jaw_back", (-8, -13, -10, 8, -6, 1), paint=MOUTH_UP)
    J("dentary", (-6, -12, -21, 6, -6, -10), paint=MOUTH_UP)
    J("jaw_front", (-4, -11, -27, 4, -7, -21), paint=MOUTH_UP)
    J("predentary", (-3, -12, -29, 3, -9, -27), tag="beak")
    J("tongue", (-3, -7, -22, 3, -6, -8), tag="tongue")
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(9, 5, -8), "r": 1.5, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-9, 5, -8), "r": 1.5, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(5, 1, -21), "r": 1.4, "rx": 1.3, "mul": 0.6, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-5, 1, -21), "r": 1.4, "rx": 1.3, "mul": 0.6, "side": -1}]

    # --- hind legs: pillar legs, four short hoofed toes, a heel pad
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(3.0, 2.0))
        sy, sz = ch["segments"][1]["unposed"]
        m.box(f"shin_{side}", (x - 5, sy - 10, sz + 4), (x + 5, sy - 2, sz + 9), tag="limb", name="calf")
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 4, by - 3, bz - 1), (x + 4, by, bz + 5), tag="limb", name="heel_pad")
        for k, (x0, x1, length) in enumerate(((-4, -2, 4), (-2, 0, 6), (0, 2, 6), (2, 4, 5))):
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            m.box(T, (a, by - 3, bz - length), (b, by, bz - 1), tag="limb", name="toe")
            m.box(T, (a, by - 3, bz - length - 2), (b, by - 1, bz - length), tag="claw", name="hoof")
    m.sym(leg)

    # --- forelimbs: semi-erect, elbow out, hand turned so the hoofed fingers point forward and out
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, overlap=(2.0, 1.0))
        uy, uz = ch["segments"][0]["unposed"]
        a = x + 5 * sx
        m.box(f"upperarm_{side}", (min(a, a + 2 * sx), uy - 12, uz - 3), (max(a, a + 2 * sx), uy - 3, uz + 4),
              name="elbow_flare")                                          # triceps / elbow out to the side
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], -22 * sx, 0))
        H = f"hand_{side}"
        m.box(H, (x - 4, by - 3, bz - 2), (x + 4, by + 1, bz + 3), tag="limb", name="palm")
        for k, (x0, x1, length) in enumerate(((-4, -2, 4), (-2, 0, 5), (0, 2, 5))):  # digits I-III, hoofed
            a, b = sorted((x - x1 * sx, x - x0 * sx))
            m.box(H, (a, by - 3, bz - 2 - length), (b, by, bz - 2), tag="limb", name="finger")
            m.box(H, (a, by - 3, bz - 4 - length), (b, by - 1, bz - 2 - length), tag="claw", name="hoof")
        a = x + 3 * sx                                                     # digits IV-V: small, no hooves
        m.box(H, (min(a, a + 2 * sx), by - 2, bz - 4), (max(a, a + 2 * sx), by, bz - 2), tag="limb", name="finger_small")
    m.sym(arm)

    # --- tail: deep, short, carried off the ground
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3"], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 1.0))
    ty, tz = tail["end"]
    m.box("tail3", (-2, ty - 2, tz), (2, ty + 2, tz + 3), name="tail_tip")
    t1y, t1z = tail["segments"][0]["unposed"]
    m.box("tail1", (-6, t1y - 12, t1z + 1), (6, t1y - 8, t1z + 12), name="chevrons")   # deep tail base

    add_saddle(m, "body", 50, -12, 4, 16, 17, flap=12)  # rider over the middle of the animal
    animations(m)
    return m


def siny_(a, ph=0.0):
    return lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0)


def animations(m):
    Li = 4.0
    idle = {
        "body": track(pos=wave(8, lambda p: (0, 0.125 * K * (1 + math.sin(2 * math.pi * p)), 0), Li)),   # breathing rises only: the forefeet stay planted
        "neck1": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * p), 2 * math.sin(2 * math.pi * (p + 0.3)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (1.5 * math.sin(2 * math.pi * (p + 0.2)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-4 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
        "tail1": track(rot=wave(8, siny_(3), Li)),
        "tail2": track(rot=wave(8, siny_(4, -0.1), Li)),
        "tail3": track(rot=wave(8, siny_(6, -0.2), Li)),
    }
    m.anim("idle", Li, True, idle)
    for name, Lc, Ah, Af, bob in (("walk", 1.8, 18, 18, 0.6 * K), ("run", 0.9, 28, 28, 1.1 * K)):
        t = quad_gait(Lc, Ah, Af)
        t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 1.5 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, b=bob: (0, b * 0.5 * (1 + math.cos(4 * math.pi * p)), 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, b=bob / K: (-2 * b * math.cos(4 * math.pi * p), 0, 0), Lc))
        t["tail1"] = track(rot=wave(8, siny_(4, 0.25), Lc))
        t["tail2"] = track(rot=wave(8, siny_(5, 0.15), Lc))
        t["tail3"] = track(rot=wave(8, siny_(7, 0.05), Lc))
        m.anim(name, Lc, True, t)
    # attack: lower the head and thrust the horns forward and up
    m.anim("attack", 0.9, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, -8, 0, 0), (0.5, 12, 0, 0), (0.9, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.3, -5, 0, 0), (0.5, 14, 0, 0), (0.9, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.3, -3, 0, 0), (0.5, 3, 0, 0), (0.9, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.3, 0, 0, -1.5 * K), (0.5, 0, 0.2 * K, -3 * K), (0.9, 0, 0, 0)])),
    })
    m.anim("sit", 4.0, True, quad_sit(m, 16, neck=12))  # head up so the belly, not the beak, rests on the ground
    # graze: dip the head to the ground and chew
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
    add_knockout(m, lift=0.42, neck_down=EAT_NECK)  # the wide body and frill rest higher on the ground
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
