"""
Spinosaurus aegyptiacus  (Cenomanian, Kem Kem beds of Morocco and Bahariya of Egypt)

Reference:
  - Size (Ibrahim et al. 2014, 2020; Sereno et al. 2022): ~14 m long, ~7 t; one of the longest theropods.
  - Skull (dal Sasso et al. 2005, MSNM V4047; Ibrahim et al. 2014): long, low and narrow, crocodile-like; the tip of
    the snout widens into a "rosette" of big procumbent teeth, with a notch behind it where the lower rosette
    fits; the nostrils sit far back on the snout, close to the eyes; a small fluted crest on the nasals in front of
    the eyes; straight conical teeth without serrations, interlocking.
  - Sail: neural spines up to 1.65 m on the back, highest over the rear of the trunk, continuing lower over the
    hips onto the tail (Ibrahim et al. 2014; Sereno et al. 2022).
  - Tail (Ibrahim et al. 2020, FSAC-KK 11888): tall, flexible, paddle-like, with long neural spines above and long
    chevrons below forming a fin for swimming.
  - Limbs: long S-shaped neck; strong arms with a big hooked thumb claw; relatively short hind legs with dense
    bones, broad flat-bottomed claws and a hallux long enough to touch the ground (Ibrahim et al. 2014).
  - Skin: no impressions known; here fine scales, darker over the back, pale throat and belly, the sail as the
    display (males brighter).

v2x (2026-10-24, remaster at the T. rex v3 level): modelled at 16 px = 1 m (one texture pixel = one vanilla
pixel in game). The skull is ~1.2x the real proportion. render_scale 0.5 = authoring scale; the in-game size comes
from SIZES in tools/javagen/gen_species.py (MODEL_SCALE ~1.0). Animations are the large theropod set.
Males have a taller, red-orange sail top ("male_display" bone); females a duller one.
"""
import math
from groundfit import fit_to_ground
from rig import Model, lowest_point
import large_theropod

ID = "spinosaurus"
K = 2.0  # position keys of the shared 1x set are scaled by this


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
    """Sail: spines as dark ribs, colour fading up to a bright rim; tail fin likewise in the body colour; skin:
    dark blotched back, river-mud mottling on the flanks, pale throat, fine scales."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag, bone = cube.tag, cube.bone
    if tag in ("tooth_cube", "claw", "eye", "mouth", "tongue"):
        return rgb
    if tag == "sail":
        base, top = model._sail_base, cube.to[1]
        g = max(0.0, min(1.0, (P[1] - base) / max(1.0, model._sail_top - base)))
        col = pal["sail"] * (1 - 0.45 * g) + pal["sail_edge"] * 0.45 * g
        if int(math.floor(P[2])) % 4 == 0:
            col = col * 0.72                                                  # neural spines
        elif (tx.i * 5 + tx.j * 3) % 11 == 0:
            col = col * 0.9                                                   # vessels
        if P[1] > top - 1.01 and bone != "body" or (bone == "body" and P[1] > top - 1.01 and cube.name == "sail_rim"):
            col = pal["sail_edge"] * 1.05
        return col
    if tag == "fin":
        col = pal["fin"].copy()
        if int(math.floor(P[2])) % 4 == 0:
            col = col * 0.8
        if P[1] > cube.to[1] - 1.01 or P[1] < cube.frm[1] + 1.01:
            col = col * 0.7 + pal["sail"] * 0.3
        return col
    if tag == "crest":
        return rgb * (0.85 if int(math.floor(P[2])) % 2 == 0 else 1.0)       # fluted
    if tag in ("skin", "limb"):
        if bone in ("skull", "jaw") and region != "dorsal":
            rgb = rgb * 0.85 + pal["belly"] * 0.15
        elif region in ("dorsal", "flank"):
            edge, h = _cell(P, 5.0)
            if h % 4 == 0 and (region == "dorsal" or tx.cy > 0.5):
                rgb = rgb * 0.8                                               # blotches
        if tag == "limb" and bone.startswith("toes") and tx.face != "down":
            return rgb * (0.85 if int(math.floor(P[2])) % 3 == 0 else 1.0)
        edge, h = _cell(P, 2.0)
        if edge < 0.12:
            rgb = rgb * 0.95
        elif h % 29 == 0:
            rgb = rgb * 1.1
    return rgb


PALETTE = {"dorsal": "#3f443b", "flank": "#646957", "belly": "#d3caa8", "limb": "#4f5446", "limb_top": "#616656",
           "claw": "#2a2622", "claw_base": "#3a332d", "claw_tip": "#c2b69c", "sail": "#b8402a", "sail_edge": "#efa748",
           "fin": "#4f5446", "tooth": "#f0e9d5", "mouth": "#7c3430", "gum": "#5b2421", "tongue": "#9a4e46",
           "tooth_cube_base": "#d6ccb0", "tooth_cube_tip": "#f6f1e2", "eye": "#d8a838", "pupil": "#17110c",
           "crest": "#4a3a2e"}
SEXES = {"male": {"sail": "#bd3e26", "sail_edge": "#f2ac46", "crest": "#7a3224"},
         "female": {"sail": "#7a6a58", "sail_edge": "#ad9a72", "dorsal": "#47493f", "crest": "#4e4236"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (44, 10)
TORSO = [("hips", (-11, 34, 0, 11, 54, 24)), ("belly", (-12, 26, -24, 12, 52, 2)),
         ("chest", (-10, 26, -46, 10, 50, -22)), ("back_ridge", (-6, 52, -42, 6, 55, 22)),
         ("gastralia", (-8, 23, -40, 8, 26, -6)), ("pubic_boot", (-3, 18, -6, 3, 24, 2)), ("pubis", (-2, 24, -4, 2, 34, 2)),
         ("pectoral_l", (10, 30, -44, 11, 44, -30)), ("pectoral_r", (-11, 30, -44, -10, 44, -30))]
SAIL_BASE = 55
# sail vanes (z0, z1, height above the back): low at the shoulders, tallest over the rear of the trunk, down over
# the hips (1.65 m = 26 px at the top)
SAIL = [(-42, -36, 6), (-36, -30, 11), (-30, -24, 15), (-24, -18, 19), (-18, -12, 22), (-12, -6, 25), (-6, 0, 26),
        (0, 6, 26), (6, 12, 23), (12, 18, 17), (18, 22, 10)]
NECK = ([(46, -46), (54, -60), (60, -72)], [(16, 16), (14, 14)])
TAIL = ([(50, 24), (49, 48), (47, 70), (46, 90), (46, 108)], [(18, 18), (13, 14), (9, 10), (6, 7)])
ARM_X = 11
ARM = ([(38, -40), (29, -44), (21, -50)], [(6, 8), (5, 6)])
LEG_X = 12
LEG = ([(44, 10), (26, 2), (11, 10), (3, 6)], [(13, 20, -1), (9, 11, 1, "limb"), (7, 7, 0, "limb")])
SIT = (24, 62, -112, 58, -6, {"tail1": (7, 0, 0), "tail2": (3, 0, 0), "neck1": (-6, 0, 0), "skull": (4, 0, 0)})
SIT_SPLAY = (18, -34)
HEAD = 1.2


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern

    def mirror(bone, frm, to, **kw):
        name = kw.pop("name")
        m.box(bone, frm, to, name=name + "_l", **kw)
        m.box(bone, (-to[0], frm[1], frm[2]), (-frm[0], to[1], to[2]), name=name + "_r", **kw)

    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)

    # --- sail: thin vanes on the spine; the male's taller rim is its own bone (hidden on females)
    m._sail_base, m._sail_top = SAIL_BASE, SAIL_BASE + max(h for _a, _b, h in SAIL) + 3
    for z0, z1, h in SAIL:
        m.box("body", (-1, SAIL_BASE, z0), (1, SAIL_BASE + h, z1), tag="sail", name="sail")
    m.bone("male_display", "body", (0, SAIL_BASE, 0))
    for z0, z1, h in SAIL[1:-1]:
        m.box("male_display", (-1, SAIL_BASE + h, z0 + 1), (1, SAIL_BASE + h + 3, z1 - 1), tag="sail", name="sail_top")

    # --- neck: long and S-curved, a throat fold
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(3.0, 2.0))
    y1, z1 = neck["segments"][0]["unposed"]
    m.box("neck1", (-6, y1 - 10, z1 - 12), (6, y1 - 7, z1 + 1), name="throat")
    y2, z2 = neck["segments"][1]["unposed"]
    m.box("neck2", (-5, y2 - 9, z2 - 10), (5, y2 - 6, z2 + 1), name="throat2")

    ay, az = neck["end"]
    h = lambda v: int(round(v * HEAD))
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-6 - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay + h(-1), az + h(0)))

    def at(x, y, z):
        return (h(x), ay + h(y), az + h(z))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, at(x0, y0, z0), at(x1, y1, z1), tag=tag, name=name, **kw)

    def S(name, box, tag="skin", **kw):
        return B("skull", name, box, tag, **kw)

    def J(name, box, tag="skin", **kw):
        return B("jaw", name, box, tag, **kw)

    # --- skull: narrow braincase, eyes high, long crocodile snout, notch, rosette
    S("cranium", (-5, -1, -10, 5, 8, 2), paint=MOUTH_DOWN)
    S("occiput", (-4, 1, 2, 4, 7, 3))
    S("orbit", (-4, 0, -15, 4, 8, -10), paint=MOUTH_DOWN)
    S("brow", (-4, 8, -14, 4, 9, -9))
    S("crest", (-1, 7, -22, 1, 10, -13), tag="crest")                      # fluted nasal crest
    S("snout_back", (-3, -1, -24, 3, 7, -15), paint=MOUTH_DOWN)
    S("snout_mid", (-3, -1, -32, 3, 5, -24), paint=MOUTH_DOWN)
    S("snout_front", (-2, 0, -37, 2, 4, -32), paint=MOUTH_DOWN)            # raised margin: the notch
    S("rosette", (-3, -1, -42, 3, 4, -37), paint=MOUTH_DOWN)
    # upper teeth on the outer edge of each snout box: (z, length); the rosette ones are the biggest
    edges = [(-42, -37, 3, -1), (-37, -32, 2, 0), (-32, -24, 3, -1), (-24, -15, 3, -1)]   # (z0, z1, half width, bottom)
    for side in (1, -1):
        for z, L in ((-41, 3), (-39, 4), (-36, 2), (-34, 2), (-30, 2), (-27, 2), (-24, 2), (-21, 2), (-18, 2)):
            z0, z1, hw, bot = next(e for e in edges if e[0] <= z < e[1])
            x, top, zz = side * h(hw), ay + h(bot), az + h(z)
            m.box("skull", (min(x, x - side), top - L, zz), (max(x, x - side), top, zz + 1), tag="tooth_cube",
                  name="fang", paint={"axis": "-y"})

    J("jaw_back", (-4, -6, -14, 4, 0, 2), paint=MOUTH_UP)
    J("jaw_mid", (-2, -4, -30, 2, 0, -14), paint=MOUTH_UP)
    J("jaw_front", (-2, -3, -38, 2, 0, -30), paint=MOUTH_UP)
    J("jaw_rosette", (-3, -4, -42, 3, 0, -38), paint=MOUTH_UP)
    J("tongue", (-1, 0, -28, 1, 1, -8), tag="tongue")
    for side in (1, -1):
        for z, L in ((-41, 3), (-38, 3), (-33, 2), (-28, 2), (-23, 2), (-18, 2)):
            x = side * (h(3) if z < -37 else h(2))
            m.box("jaw", (min(x, x - side), ay + h(0), az + h(z)), (max(x, x - side), ay + h(0) + L, az + h(z) + 1),
                  tag="tooth_cube", name="fang_low", paint={"axis": "+y"})
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(4, 5, -12.5), "r": 1.3, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-4, 5, -12.5), "r": 1.3, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(3, 5, -21), "r": 1.0, "rx": 1.4, "mul": 0.4, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-3, 5, -21), "r": 1.0, "rx": 1.4, "mul": 0.4, "side": -1}]

    # --- arms: strong, three fingers, a big hooked thumb claw
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, tag="limb", overlap=(2.0, 1.0))
        ey, ez = ch["end"]
        F = f"forearm_{side}"
        a = x - 2 * sx                                                         # thumb on the inside
        m.box(F, (min(a, a - 2 * sx), ey - 4, ez - 3), (max(a, a - 2 * sx), ey + 1, ez), tag="limb", name="thumb")
        m.box(F, (min(a, a - 2 * sx), ey - 9, ez - 4), (max(a, a - 2 * sx), ey - 4, ez - 1), tag="claw",
              name="thumb_claw", paint={"axis": "-y"})
        for name, x0 in (("finger_mid", -1), ("finger_out", 1)):
            a, b = sorted((x + x0 * sx, x + (x0 + 2) * sx))
            m.box(F, (a, ey - 4, ez - 2), (b, ey, ez + 1), tag="limb", name=name)
            m.box(F, (a, ey - 6, ez - 2), (b, ey - 4, ez), tag="claw", name="claw", paint={"axis": "-y"})
    m.sym(arm)

    # --- legs: short and dense, broad flat claws, a long grounded hallux
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(3.0, 2.0))
        ty, tz = ch["segments"][0]["unposed"]
        m.box(f"thigh_{side}", (x - 7, ty - 12, tz - 11), (x + 7, ty + 2, tz + 9), name="thigh_muscle")
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        for name, (x0, x1), length in (("toe_mid", (-1, 2), 12), ("toe_out", (2, 5), 10), ("toe_in", (-4, -1), 10)):
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            m.box(T, (a, by - 3, bz - length + 2), (b, by, bz + 2), tag="limb", name=name)
            m.box(T, (a, by - 3, bz - length - 1), (b, by - 1, bz - length + 2), tag="claw", name="claw")
        a = x - 4 * sx
        m.box(T, (min(a, a - 2 * sx), by - 3, bz + 1), (max(a, a - 2 * sx), by - 1, bz + 7), tag="limb", name="hallux")
        m.box(T, (min(a, a - 2 * sx), by - 3, bz + 7), (max(a, a - 2 * sx), by - 2, bz + 9), tag="claw", name="hallux_claw")
    m.sym(leg)

    # --- tail: deep and flexible, a paddle fin of tall spines above and chevrons below
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 2.0))
    t1y, t1z = tail["segments"][0]["unposed"]
    m.box("tail1", (-10, t1y - 13, t1z - 2), (10, t1y - 5, t1z + 14), name="caudofemoralis")
    m.box("tail1", (-1, t1y + 9, t1z), (1, t1y + 15, t1z + 20), tag="sail", name="sail_tail")
    for k, (up, down) in ((1, (7, 5)), (2, (10, 7)), (3, (9, 6))):   # tallest mid-tail, like FSAC-KK 11888
        sg = tail["segments"][k]
        y0, z0 = sg["unposed"]
        L = int(round(sg["len"]))
        hh = tsecs[k][1] / 2
        m.box(f"tail{k+1}", (-1, y0 + hh, z0), (1, y0 + hh + up, z0 + L), name="fin", tag="fin")
        m.box(f"tail{k+1}", (-1, y0 - hh - down, z0 + 2), (1, y0 - hh, z0 + L), name="fin", tag="fin")
    ty, tz = tail["end"]
    m.box("tail4", (-2, ty - 2, tz), (2, ty + 2, tz + 6), name="tail_tip")

    large_theropod.animations(m, SIT)
    for a in m.animations:
        if a["name"].split(".")[-1] in ("idle", "walk", "run", "attack", "roar", "beg", "eat", "tame"):
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
    # keep the long snout out of the ground when it eats / strikes
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    return m
