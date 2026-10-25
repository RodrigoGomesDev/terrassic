"""
Euoplocephalus tutus  (Late Cretaceous, Campanian; Dinosaur Park Formation, Alberta)

Reference:
  - Size (Lambe 1902; Arbour & Currie 2013, "Euoplocephalus tutus and the diversity of ankylosaurid dinosaurs";
    Paul 2010): an ankylosaurid of ~5.5-6 m and ~2-2.5 t, one of the best known armoured dinosaurs (over 40
    specimens, many of them armour and skulls). Narrower and lighter than the Ankylosaurus.
  - Skull (Vickaryous & Russell 2003; Arbour & Currie 2013): broad and flat, roofed by small armour tiles; short
    pyramidal squamosal horns at the back corners and quadratojugal horns on the cheeks; a narrow horny beak;
    a bony eyelid (palpebral) over each eye that could shut like a shutter.
  - Armour: two cervical half-rings over the neck, each a collar of fused plates carrying tall keels; then
    transverse bands of keeled osteoderms across the back, the keels tall and pointed over the shoulders, small
    ossicles packed between the bands; short triangular plates along the edge of the flanks (no long spikes).
  - Tail: a muscular base with keeled side plates, then a stiff handle of interlocking vertebrae carrying a small
    rounded club of two big lateral osteoderms and a knob, smaller than the Ankylosaurus's.
  - Limbs: short and stout, the hind ones longer; three short hoofed toes, five short fingers.
  - Colour unknown; kept from the old model: olive and khaki with slate armour and rust keels on the plates;
    males darker with brick-red keels, females greyer with bone-coloured keels.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared ankylosaur rig), built
with the construction rules of the Ankylosaurus remaster at ~21 px = 1 m (so the keels, eyelids and fingers keep
their detail), narrower than the Ankylosaurus, with tall keels on every plate, the palpebral eyelids and the small
club. The head is ~1.25x the real proportion.
"""
import math
from rig import Model, wave, sinx, track, keys, add_knockout, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "euoplocephalus"
K = 2.0
HEAD = 1.25


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
    """Osteoderms: horn-covered bone with a pale keel and a dark rim; club: pitted bone; skin between the plates:
    a pebbly mosaic of tiny ossicles; head: armour tiles."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag == "keel":
        col = pal["scute"].copy()
        return col * (1.12 if tx.face == "up" else 0.9 if tx.face in ("north", "south") else 1.0)
    if tag in ("claw", "eye", "mouth", "beak", "horn"):
        if tag == "horn" and (tx.i + 2 * tx.j) % 5 == 0:
            return rgb * 0.93
        return rgb
    if tag == "armor":
        corner = tx.col in (0, tx.cols - 1) and tx.row in (0, tx.rows - 1)
        if corner and tx.cols > 2 and tx.rows > 2:
            return pal["dorsal"] * 0.9                                        # rounded corners: oval plates
        if tx.face == "up" and abs(P[0] - getattr(cube, "keel_x", 1e9)) < 0.6:
            return mix3(rgb, pal["scute"], 0.7)                               # pale worn keel
        if tx.edge:
            rgb = rgb * 0.9
        return rgb * (1.06 if (tx.i * 3 + tx.j) % 5 == 0 else 1.0)
    if tag == "club":
        edge, h = _cell(P, 1.6)
        if edge < 0.14:
            rgb = rgb * 0.84                                                  # pits and sutures
        if tx.face == "up" and h % 4 == 0:
            rgb = rgb * 1.1
        return rgb
    if tag == "ossicles":                                                 # small bony disks packed between the plates
        edge, h = _cell(P, 1.6)
        return pal["tile"] * (0.8 if edge < 0.15 else 1.08 if h % 5 == 0 else 0.95)
    if tag == "tile":
        return rgb * (0.82 if tx.edge else 1.04)
    if tag in ("skin", "limb"):
        if tag == "limb" and cube.bone.startswith(("toes", "hand")) and tx.face != "down":
            return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)
        if tag == "skin" and region == "flank" and math.sin(P[2] * 0.7 + P[1] * 0.4) * math.sin(P[1] * 0.9 - P[0] * 0.3) > 0.5:
            rgb = pal["blotch"] * 1.0                                         # dark blotches down the flanks
        edge, h = _cell(P, 1.5 if region != "belly" else 2.0)
        if edge < 0.14:
            rgb = rgb * 0.9                                                   # ossicle mosaic
        elif h % 7 == 0 and region != "belly":
            rgb = rgb * 1.1
    return rgb


def mix3(a, b, t):
    return a * (1 - t) + b * t


PALETTE = {"dorsal": "#5a6442", "flank": "#7c845a", "belly": "#cfc9a2", "blotch": "#3e4830",
           "limb": "#6a6e4e", "limb_top": "#767a58", "claw": "#3a362e", "claw_base": "#3a362e",
           "armor": "#4a4e3a", "scute": "#b06a3a", "spike_base": "#5a5a46", "spike_tip": "#e6dcc0",
           "horn_base": "#5a5a46", "horn_tip": "#e6dcc0", "club": "#6e6a58", "tile": "#555a44", "beak": "#3a3630",
           "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622", "eye": "#c09030", "pupil": "#140f0a"}
SEXES = {"male": {"scute": "#b85a30", "dorsal": "#505c3c", "blotch": "#34402a"},
         "female": {"scute": "#c4b48a", "flank": "#8a8c66", "armor": "#565848", "blotch": "#505a40"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (24, 10)                                      # hip joint
# (name, (x0, y0, z0, x1, y1, z1)): a wide low barrel, the back highest over the hips
TORSO = [("pelvis", (-12, 14, -2, 12, 30, 18)), ("barrel", (-14, 11, -22, 14, 29, 0)),
         ("chest", (-11.5, 12, -32, 11.5, 27, -20)), ("dome", (-10.5, 29, -20, 10.5, 31, 14)),
         ("shoulder_dome", (-9, 27, -30, 9, 29, -20)), ("belly", (-11.5, 9, -18, 11.5, 11, -2)),
         ("rump", (-9.5, 16, 18, 9.5, 28, 22))]
NECK = ([(21, -30), (20, -36), (19, -43)], [(14, 12), (12, 10)])
TAIL = ([(24, 20), (22, 32), (20, 43), (18, 53), (16, 67)], [(18, 14), (12, 10), (8, 6), (5, 4)])
LEG_X, LEG = 10, ([(24, 10), (13, 6), (5, 8), (2, 8)], [(11, 13, -1), (8, 8, 0, "limb"), (9, 6, 0, "limb")])
ARM_X, ARM = 10.5, ([(19, -24), (10, -22), (2.2, -24)], [(8, 9), (7, 7, 0, "limb")])
# osteoderm bands across the back: z of each band, and the plates' (x, half width) on the top
SIT_HIND = (20, -50, 30)
SIT_SPLAY = (14, -24)      # resting: thigh and shin roll out (deg)
BANDS = [-26, -19, -12, -5, 2, 9]
BAND_X = [(-8, 2), (-4, 2), (0, 2), (4, 2), (8, 2)]


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name, tag="ossicles" if "dome" in name else "skin")

    def plate(bone, frm, to, keel_x=None, **kw):
        c = m.box(bone, frm, to, tag="armor", name=kw.pop("name", "osteoderm"), **kw)
        c.keel_x = (frm[0] + to[0]) / 2 if keel_x is None else keel_x
        return c

    # --- armour bands: oval low-keeled plates over the top, bigger ones on the shoulders of the barrel,
    #     triangular keeled plates along the edge of the flanks
    for i, z in enumerate(BANDS):
        ytop = 29 if z < -20 else 31
        for x, hw in BAND_X:
            L = 5 if abs(x) < 6 else 6
            plate("body", (x - hw, ytop, z - L / 2), (x + hw, ytop + 1, z + L / 2))
            kh = 3 if (z < -20 and abs(x) == 8) else 2 if abs(x) == 8 or z < -20 else 1    # tall pointed keels
            m.box("body", (x - 0.5, ytop + 1, z - 1.5 + (kh > 1) * 0.5), (x + 0.5, ytop + 1 + kh, z + 1.5 - (kh > 1) * 0.5),
                  tag="keel", name="keel")
        for sx in (1, -1):
            xb = 11.5 if z < -20 else 14
            plate("body", (min(xb * sx, (xb + 2) * sx), 24, z - 2.5), (max(xb * sx, (xb + 2) * sx), 29, z + 2.5),
                  name="side_osteoderm")
            if z > 5:
                continue                                                      # the thigh moves here
            # flank edge: a keeled triangular plate pointing out and a little back
            xf = 11.5 if z < -20 else 14
            o = (xf * sx, 17, z)
            plate("body", (min(xf * sx, (xf + 3) * sx), 16, z - 2), (max(xf * sx, (xf + 3) * sx), 18, z + 2),
                  name="flank_osteoderm", rot=(0, 18 * sx, -12 * sx), origin=o)
            plate("body", (min((xf + 3) * sx, (xf + 5) * sx), 16.5, z - 1), (max((xf + 3) * sx, (xf + 5) * sx), 17.5, z + 1),
                  name="flank_tip", rot=(0, 18 * sx, -12 * sx), origin=o)
    for x in (-6, 0, 6):                                                    # small plates over the rump
        plate("body", (x - 1.5, 31, 13.5), (x + 1.5, 32, 16.5))

    # --- neck: short, two cervical half-rings of keeled plates
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(3.0, 2.0))
    for seg, (w, hh) in zip(neck["segments"], secs):
        sy, sz = seg["unposed"]
        zc = sz - seg["len"] / 2
        yt = sy + hh / 2
        for x0, x1, y0, y1 in ((-w / 2 - 1, -w / 2 + 3, yt - 4, yt + 1), (-w / 2 + 3, -1, yt, yt + 2),
                               (1, w / 2 - 3, yt, yt + 2), (w / 2 - 3, w / 2 + 1, yt - 4, yt + 1)):
            plate(seg["bone"], (x0, y0, zc - 2), (x1, y1, zc + 2), name="half_ring")
            xm = (x0 + x1) / 2
            m.box(seg["bone"], (xm - 0.5, y1, zc - 1), (xm + 0.5, y1 + 2, zc + 1), tag="keel", name="ring_keel")

    ay, az = neck["end"]
    h = lambda v: int(round(v * HEAD))
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-4 - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay + h(-3), az + h(-2)))

    def at(x, y, z):
        return (h(x), ay + h(y), az + h(z))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, at(x0, y0, z0), at(x1, y1, z1), tag=tag, name=name, **kw)

    def SM(name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        B("skull", name + "_l", box, tag, **kw)
        B("skull", name + "_r", (-x1, y0, z0, -x0, y1, z1), tag, **kw)

    # --- skull: wider than long, triangular from above, low; a blunt wide beak
    B("skull", "braincase", (-5.5, -3, -4, 5.5, 3, 2), paint=MOUTH_DOWN)
    B("skull", "cheeks", (-4.5, -4, -8, 4.5, 2, -4), paint=MOUTH_DOWN)
    B("skull", "snout", (-3.5, -3.5, -11, 3.5, 1.5, -8), paint=MOUTH_DOWN)
    B("skull", "beak", (-2, -4, -12, 2, -1, -11), tag="beak")
    B("skull", "rostrum", (-2, -1, -12, 2, 1, -11))
    SM("naris", (3, -2.5, -11, 4, 0.5, -8))                                # the nostril bulges, opening sideways
    SM("palpebral", (4.5, 0.8, -7.5, 6.2, 3, -3.5), tag="tile")            # the bony eyelid shutting over the eye
    for x, z in ((-3.5, -2), (0, -2), (3.5, -2), (-2, -5), (2, -5), (-1.5, -8), (1.5, -8), (0, -10)):   # caputegulae
        B("skull", "caputegula", (x - 1.5, 3 if z > -6 else 2 if z > -9 else 1.5, z - 1.5,
                                  x + 1.5, 4 if z > -6 else 3 if z > -9 else 2.5, z + 1.5), tag="tile")
    for sx in (1, -1):
        # squamosal horns: short pyramids at the rear corners, pointing back and out
        o = at(5.5 * sx, 1.5, 1)
        r = (8, 38 * sx, 0)
        B("skull", "squamosal_horn", (min(4.5 * sx, 6.5 * sx), 0, 0, max(4.5 * sx, 6.5 * sx), 2.5, 2.5), tag="horn",
          rot=r, origin=o, paint={"axis": "+z"})
        B("skull", "squamosal_tip", (min(5 * sx, 6 * sx), 0.8, 2.5, max(5 * sx, 6 * sx), 1.7, 4), tag="horn",
          rot=r, origin=o, paint={"axis": "+z"})
        # quadratojugal horns on the cheeks, pointing down and back
        o = at(4.5 * sx, -3, -4)
        r = (-30, 10 * sx, 0)
        B("skull", "qj_horn", (min(4 * sx, 5.5 * sx), -6, -5, max(4 * sx, 5.5 * sx), -3, -3), tag="horn",
          rot=r, origin=o, paint={"axis": "-y"})
    B("jaw", "jaw", (-3.5, -5.5, -11, 3.5, -3.5, -2), paint=MOUTH_UP)
    B("jaw", "predentary", (-2.5, -5.5, -12, 2.5, -3.5, -11), tag="beak")
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(4.5, 0.5, -5.5), "r": 1.0, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-4.5, 0.5, -5.5), "r": 1.0, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(4, -1, -9.5), "r": 1.0, "rx": 1.0, "mul": 0.55, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-4, -1, -9.5), "r": 1.0, "rx": 1.0, "mul": 0.55, "side": -1}]

    # --- hind legs: short thick pillars, three short hoofed toes
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(3.0, 2.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 4, by - 2, bz - 2), (x + 4, by, bz + 4), tag="limb", name="heel_pad")
        for dx, length in ((-4, 4), (-1, 5), (2, 4)):
            a, b = sorted((x + dx * sx, x + (dx + 2) * sx))
            m.box(T, (a, by - 2, bz - 2 - length), (b, by, bz - 2), tag="limb", name="toe")
            m.box(T, (a, by - 2, bz - 4 - length), (b, by - 1, bz - 2 - length), tag="claw", name="hoof")
    m.sym(leg)

    # --- forelimbs: short, elbows a little out, five short hoofed fingers
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, overlap=(2.0, 1.0))
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], -12 * sx, 0))
        H = f"hand_{side}"
        m.box(H, (x - 4, by - 2, bz - 2), (x + 4, by + 1, bz + 3), tag="limb", name="palm")
        for k, dx in enumerate((-4, -2, 0, 2)):
            a, b = sorted((x + dx * sx, x + (dx + 2) * sx))
            m.box(H, (a, by - 2, bz - 4 + (1 if k in (0, 3) else 0)), (b, by - 1, bz - 2), tag="claw", name="hoof")
        plate(f"upperarm_{side}", (min((x + 4 * sx), (x + 6 * sx)), 20, -26), (max(x + 4 * sx, x + 6 * sx), 25, -22),
              name="shoulder_osteoderm")
    m.sym(arm)

    # --- tail: a muscular base with side plates, then the stiff handle and the club
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 1.0))
    for seg, (w, hh) in list(zip(tail["segments"], tsecs))[:3]:
        sy, sz = seg["unposed"]
        n = 2 if seg["bone"] != "tail3" else 1
        for k in range(n):
            z = sz + (k + 0.5) * seg["len"] / n
            for sx in (1, -1):
                o = (w / 2 * sx, sy, z)
                plate(seg["bone"], (min(w / 2 * sx, (w / 2 + 3) * sx), sy - 1, z - 2), (max(w / 2 * sx, (w / 2 + 3) * sx), sy + 1, z + 2),
                      name="tail_osteoderm", rot=(0, 25 * sx, 0), origin=o)
            plate(seg["bone"], (-1.5, sy + hh / 2, z - 2), (1.5, sy + hh / 2 + 1, z + 2), name="tail_keel")
    ty, tz = tail["end"]
    # club: small and rounded, two big lateral osteoderms and a knob at the tip
    m.box("tail4", (-3.5, ty - 2.5, tz - 4), (3.5, ty + 2.5, tz + 2), tag="club", name="club_core")
    for sx in (1, -1):
        m.box("tail4", (min(3.5 * sx, 5.5 * sx), ty - 2, tz - 4), (max(3.5 * sx, 5.5 * sx), ty + 2, tz + 1), tag="club", name="club_lobe")
    m.box("tail4", (-2.5, ty - 1.5, tz + 2), (2.5, ty + 1.5, tz + 4), tag="club", name="club_tip")
    m.box("tail4", (-2, ty + 2.5, tz - 3), (2, ty + 3.5, tz + 1), tag="club", name="club_top")

    animations(m)
    return m


def siny_(a, ph=0.0):
    return lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0)


def animations(m):
    Li = 4.0
    m.anim("idle", Li, True, {
        "body": track(pos=wave(8, lambda p: (0, 0.075 * K * (1 + math.sin(2 * math.pi * p)), 0), Li)),   # breathing rises only: the forefeet stay planted
        "neck1": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * p), 3 * math.sin(2 * math.pi * (p + 0.2)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (1.5 * math.sin(2 * math.pi * (p + 0.25)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-4 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
        "tail1": track(rot=wave(8, siny_(3), Li)), "tail2": track(rot=wave(8, siny_(3, -0.1), Li)),
        "tail3": track(rot=wave(8, siny_(2, -0.2), Li)), "tail4": track(rot=wave(8, siny_(1, -0.3), Li)),
    })
    for name, Lc, Ah, Af, bob in (("walk", 2.0, 16, 16, 0.4 * K), ("run", 1.1, 24, 24, 0.8 * K)):
        t = quad_gait(Lc, Ah, Af)
        t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 2.2 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, b=bob: (0, b * 0.5 * (1 + math.cos(4 * math.pi * p)), 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, b=bob / K: (-2 * b * math.cos(4 * math.pi * p), 0, 0), Lc))
        for i, (a, ph) in enumerate(((4, 0.25), (4, 0.15), (3, 0.05), (1, 0.0))):
            t[f"tail{i+1}"] = track(rot=wave(8, siny_(a, ph), Lc))
        m.anim(name, Lc, True, t)
    # attack: the body pivots and the tail sweeps sideways; the stiff handle swings the club as one piece
    m.anim("attack", 1.1, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.35, 0, 12, 0), (0.6, 0, -14, 0), (1.1, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.35, 0, 14, 0), (0.6, 0, -20, 0), (1.1, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.35, 0, 14, 0), (0.6, 0, -24, 0), (1.1, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.35, 0, 10, 0), (0.6, 0, -24, 0), (1.1, 0, 0, 0)])),
        "tail4": track(rot=keys([(0, 0, 0, 0), (0.35, 0, 2, 0), (0.6, 0, -6, 0), (1.1, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.35, 0, -10, 0), (0.6, 0, 10, 0), (1.1, 0, 0, 0)])),
    })
    m.anim("sit", 4.0, True, quad_sit(m, 9, hind=SIT_HIND, front=(-25, 65, -40), neck=4))
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
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.6, -14, 0, 0), (2.3, -14, 0, 0), (2.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.6, -12, 0, 0), (2.3, -12, 0, 0), (2.8, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
    })
    add_knockout(m, lift=0.6, neck_down=-12)          # the wide armoured body rolls only part of the way
    for a in m.animations:      # eat / beg / tame come from the 1x set: scale their position keys
        if a["name"].split(".")[-1] in ("eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    fit_to_ground(m, "graze", ("neck1", "skull"))
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
