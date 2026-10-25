"""
Stegosaurus stenops  (Kimmeridgian-Tithonian, Morrison Formation, North America; also Portugal)

Reference:
  - Size (Gilmore 1914; Maidment et al. 2015, "Sophie" NHMUK PV R36730; Galton 2010): "Sophie" 5.6 m (a young
    adult), the biggest individuals 7-9 m and ~5 t; hips ~2.5 m high, the head carried low (< 1 m).
  - Plates (Carpenter 1998; Main et al. 2005): 17-19 thin bony plates in two staggered rows from the neck to the
    tail, small on the neck, the tallest (60-90 cm) over the hips and the base of the tail, rounded-pentagonal with
    grooves left by blood vessels; probably display (keratin covered, colourful).
  - Tail (McWhinney et al. 2001): the "thagomizer", two pairs of bony spikes 60-90 cm long, pointing out, back and
    up; healed wounds on Allosaurus bones show it was a weapon.
  - Body: forelimbs about half the length of the hind limbs, so the back arches up to the hips and the tail is
    carried high; tiny, long, narrow skull with a horny beak; small bony disks (gular ossicles) under the throat.
  - Feet: five short hoofed toes on the hands, three on the feet.

v2x (2026-10-24, remaster at the T. rex v3 level): modelled at 16 px = 1 m (one texture pixel = one vanilla pixel
in game). The head is ~1.3x the real proportion. render_scale 0.5 = authoring scale; the in-game size comes from
SIZES in tools/javagen/gen_species.py (MODEL_SCALE ~0.9 for 9 m).
"""
import math
from rig import Model, wave, sinx, track, keys, add_knockout
from quadruped import quad_gait, quad_sit
from paint import mix, smooth
from groundfit import fit_to_ground

ID = "stegosaurus"
K = 2.0
HEAD = 1.3


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
    """Plates: dark base fading to a bright rim, branching vessel grooves; spikes: keratin; skin: tubercle mosaic,
    faint vertical stripes on the flanks, pale throat with gular ossicles."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("claw", "eye", "mouth", "beak", "saddle"):
        return rgb
    if tag == "plate":
        base, top, rows = cube.plate_base, cube.plate_top, cube.plate_rows
        g = max(0.0, min(1.0, (P[1] - base) / max(1.0, top - base)))
        # distance to the plate's outline (0 centre .. 1 rim), from the stacked rows' half-lengths
        half = next((L / 2 for y0, y1, L in rows if y0 <= P[1] < y1), rows[-1][2] / 2)
        d = max(abs(P[2] - cube.plate_z) / max(0.5, half), g)
        col = mix(pal["plate"], pal["plate_dark"], smooth(0.0, 0.55, 1 - d) * (0.25 if cube.plate_row > 0 else 0.75))
        col = mix(col, pal["plate_edge"], smooth(0.62, 0.78, d))               # crisp keratin rim: each plate
        if tx.face in ("up", "north", "south"):                                # reads against the one behind
            col = mix(col, pal["plate_edge"], 0.7)
        vein = math.sin(P[2] * 1.3 + (P[1] - base) * 0.7) * math.sin((P[1] - base) * 0.5)
        if vein > 0.6 and d < 0.7:
            col = col * 0.84                                                  # vessel grooves
        if (tx.i + tx.j * 2) % 7 == 0:
            col = col * 0.94
        return col
    if tag == "ossicle":
        return rgb * (1.1 if tx.face == "down" else 0.95)
    if tag in ("skin", "limb"):
        if tag == "skin" and region == "flank" and tx.face in ("east", "west") and cube.bone == "body":
            if math.sin(P[2] * 2 * math.pi / 11.0) > 0.6 and tx.cy > 0.45:
                rgb = rgb * 0.84                                              # stripes
        if tag == "limb" and cube.bone.startswith(("toes", "hand")) and tx.face != "down":
            return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)
        edge, h = _cell(P, 2.5 if region != "belly" else 2.0)
        if edge < 0.12:
            rgb = rgb * 0.93
        elif h % 11 == 0 and region != "belly":
            rgb = rgb * 1.12                                                  # bigger tubercles
    return rgb


PALETTE = {"dorsal": "#4c5734", "flank": "#6f7a48", "belly": "#c6c193", "limb": "#57603e", "limb_top": "#687347",
           "claw": "#34332b", "claw_base": "#34332b", "spike_base": "#7a684b", "spike_tip": "#f0e7cd",
           "plate": "#8c3420", "plate_dark": "#5a1c14", "plate_edge": "#e3a046", "ossicle": "#a8a47a",
           "beak": "#47423a", "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
           "eye": "#b5862c", "pupil": "#140f0a"}
SEXES = {"male": {"plate": "#9a2e1c", "plate_edge": "#f0a640"},
         "female": {"plate": "#6a4c34", "plate_dark": "#44301f", "plate_edge": "#c4a46a", "dorsal": "#535d38"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (38, 14)
TORSO = [("hips", (-14, 26, 4, 14, 48, 32)), ("midbody", (-16, 17, -18, 16, 46, 6)),
         ("chest", (-13, 15, -38, 13, 38, -16)), ("arch", (-10, 48, -4, 10, 51, 26)),
         ("back", (-11, 46, -16, 11, 48, 4)), ("withers", (-10, 38, -34, 10, 41, -16)),
         ("shoulder_slope", (-10, 41, -24, 10, 44, -14)),
         ("belly_low", (-12, 15, -28, 12, 17, 2)),
         ("ribs_l", (16, 22, -16, 17, 40, 4)), ("ribs_r", (-17, 22, -16, -16, 40, 4))]
NECK = ([(30, -38), (27, -46), (23, -54)], [(12, 13), (10, 11)])
TAIL = ([(46, 30), (46, 48), (42, 64), (37, 78), (33, 92)], [(18, 18), (13, 13), (9, 9), (5, 6)])
LEG_X, LEG = 10, ([(38, 14), (22, 10), (8, 14), (3, 12)], [(12, 16, -1), (9, 10, 0, "limb"), (8, 7, 0, "limb")])
ARM_X, ARM = 11, ([(24, -34), (13, -31), (4, -33)], [(9, 10), (8, 8, 0, "limb")])
# plates: (bone, where, height); "where" is z on the body, or the fraction along a neck/tail segment
PLATES = [("neck2", 0.55, 5), ("neck1", 0.2, 6), ("neck1", 0.7, 8),
          ("body", -32, 10), ("body", -25, 12), ("body", -18, 14), ("body", -11, 16), ("body", -4, 18),
          ("body", 3, 20), ("body", 10, 21), ("body", 17, 21), ("body", 24, 20),
          ("tail1", 0.3, 18), ("tail1", 0.75, 15), ("tail2", 0.3, 12), ("tail2", 0.72, 9), ("tail3", 0.45, 6)]


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)

    # --- neck: short, low, gular ossicles under the throat
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(3.0, 2.0))
    for seg, (w, hh) in zip(neck["segments"], secs):
        sy, sz = seg["unposed"]
        for k in range(int(seg["len"] // 3)):
            if seg["bone"] == "neck1" and k < 2:
                continue                                                      # this end sits inside the chest
            for x in (-3, 1):
                m.box(seg["bone"], (x, sy - hh / 2 - 1, sz - 2 - 3 * k), (x + 2, sy - hh / 2, sz - 3 * k),
                      tag="ossicle", name="ossicle")
    ay, az = neck["end"]
    h = lambda v: int(round(v * HEAD))
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-10 - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay + h(-3), az + h(-2)))

    def at(x, y, z):
        return (h(x), ay + h(y), az + h(z))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, at(x0, y0, z0), at(x1, y1, z1), tag=tag, name=name, **kw)

    # --- head: tiny, long and narrow, a horny beak
    B("skull", "cranium", (-3, -2, -5, 3, 3, 1), paint=MOUTH_DOWN)
    B("skull", "brow", (-3, 3, -5, 3, 4, -2))
    B("skull", "cheeks", (-4, -3, -6, 4, 1, -2), paint=MOUTH_DOWN)
    B("skull", "snout", (-2, -3, -11, 2, 2, -6), paint=MOUTH_DOWN)
    B("skull", "beak", (-1.5, -3, -13, 1.5, 1, -11), tag="beak")
    B("jaw", "jaw", (-2, -5, -12, 2, -3, -2), paint=MOUTH_UP)
    B("jaw", "predentary", (-1.5, -5, -13, 1.5, -3, -12), tag="beak")
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(4, 0, -4), "r": 1.0, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-4, 0, -4), "r": 1.0, "side": -1}]

    # --- hind legs: long pillars, three hoofed toes
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(3.0, 2.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 5, by - 3, bz - 4), (x + 5, by, bz + 5), tag="limb", name="foot_pad")
        for dx in (-5, -1, 3):
            a = x + dx * sx
            m.box(T, (min(a, a + 2 * sx), by - 3, bz - 7), (max(a, a + 2 * sx), by, bz - 4), tag="limb", name="toe")
            m.box(T, (min(a, a + 2 * sx), by - 3, bz - 9), (max(a, a + 2 * sx), by - 1, bz - 7), tag="claw", name="hoof")
    m.sym(leg)

    # --- forelimbs: short and straight, five short hoofed toes
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, overlap=(2.0, 1.0))
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], -14 * sx, 0))
        H = f"hand_{side}"
        m.box(H, (x - 5, by - 3, bz - 3), (x + 5, by + 1, bz + 4), tag="limb", name="palm")
        for k, dx in enumerate((-5, -3, -1, 1, 3)):
            a = x + dx * sx
            m.box(H, (min(a, a + 2 * sx), by - 3, bz - 5 + (1 if k == 4 else 0)), (max(a, a + 2 * sx), by - 1, bz - 3),
                  tag="claw", name="hoof")
    m.sym(arm)

    # --- tail: carried high, tapering
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 1.0))
    ty, tz = tail["end"]
    m.box("tail4", (-2, ty - 2, tz), (2, ty + 2, tz + 4), name="tail_tip")

    # --- plates: two staggered rows, rounded-pentagonal (three stacked thin boxes), tilted a little outward
    segs = {s["bone"]: s for s in neck["segments"] + tail["segments"]}
    body_top = [(z0, z1, y1) for _n, (x0, y0, z0, x1, y1, z1) in TORSO if abs(x0) <= 12]

    def top_at(z):
        return max(y1 for z0, z1, y1 in body_top if z0 <= z < z1)

    for k, (bone, where, s) in enumerate(PLATES):
        sx = 1 if k % 2 == 0 else -1
        if bone == "body":
            z, y = where, top_at(where) - 1
        else:
            sg = segs[bone]
            y0, z0 = sg["unposed"]
            z = z0 - where * sg["len"] if bone.startswith("neck") else z0 + where * sg["len"]
            z = round(z)
            y = y0 + secs[0][1] / 2 - 1 if bone.startswith("neck") else y0 + tsecs[int(bone[-1]) - 1][1] / 2 - 1
        x = 2 * sx
        tall = round(s * 1.4)                                             # plate height; s is its base length
        # rounded pentagon: narrow root, widest at ~40%, tapering to a blunt point (four stacked thin boxes)
        prof = [(0.00, 0.2, 0.5), (0.2, 0.5, 0.78), (0.5, 0.76, 0.56), (0.76, 1.00, 0.24)]
        rows, yb = [], y
        for i, (f0, f1, fl) in enumerate(prof):
            yt = y + (tall if i == len(prof) - 1 else max(yb - y + 1, round(tall * f1)))
            L = max(1, round(s * fl))
            rows.append((yb, yt, L))
            yb = yt
        o = (x, y, z)
        rot = (0, 0, -11 * sx)
        for name, (y_0, y_1, L) in zip(("plate", "plate_mid", "plate_upper", "plate_tip"), rows):
            c = m.box(bone, (x - 1, y_0, z - L / 2), (x + 1, y_1, z + L / 2), tag="plate", name=name, rot=rot, origin=o)
            c.plate_base, c.plate_top, c.plate_z, c.plate_rows, c.plate_row = y, y + tall, z, rows, sx
    # --- thagomizer: two pairs of spikes pointing out, back and up
    t4 = segs["tail4"]
    y0, z0 = t4["unposed"]
    for i, dz in enumerate((2, 7)):
        for sx in (1, -1):
            x, zb = 2 * sx, z0 + dz
            o = (x, y0 + 1, zb)
            rot = (-24 - 8 * i, 55 * sx, 0)
            m.box("tail4", (x - 1.5, y0 - 0.5, zb), (x + 1.5, y0 + 2.5, zb + 8), tag="spike", name="spike", rot=rot, origin=o,
                  paint={"axis": "+z"})
            m.box("tail4", (x - 1, y0, zb + 8), (x + 1, y0 + 2, zb + 13), tag="spike", name="spike_mid",
                  rot=rot, origin=o, paint={"axis": "+z"})
            m.box("tail4", (x - 0.5, y0 + 0.5, zb + 13), (x + 0.5, y0 + 1.5, zb + 17), tag="spike", name="spike_tip",
                  rot=rot, origin=o, paint={"axis": "+z"})

    animations(m)
    return m


def animations(m):
    Li = 4.0
    sy = lambda a, ph=0.0: (lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0))
    m.anim("idle", Li, True, {
        "body": track(rot=wave(8, sinx(0.5), Li), pos=wave(8, lambda p: (0, 0.2 * K * math.sin(2 * math.pi * p), 0), Li)),
        "neck1": track(rot=wave(8, lambda p: (2.5 * math.sin(2 * math.pi * p), 3 * math.sin(2 * math.pi * (p + 0.2)), 0), Li)),
        "skull": track(rot=wave(8, lambda p: (2 * math.sin(2 * math.pi * (p + 0.25)), 0, 0), Li)),
        "jaw": track(rot=wave(8, lambda p: (-5 * max(0.0, math.sin(4 * math.pi * p)), 0, 0), Li)),
        "tail1": track(rot=wave(8, sy(3), Li)), "tail2": track(rot=wave(8, sy(4, -0.1), Li)),
        "tail3": track(rot=wave(8, sy(5, -0.2), Li)), "tail4": track(rot=wave(8, sy(6, -0.3), Li)),
    })
    for name, Lc, Ah, Af, bob in (("walk", 1.8, 18, 16, 0.5 * K), ("run", 1.0, 26, 24, 1.0 * K)):
        t = quad_gait(Lc, Ah, Af)
        t["body"] = track(rot=wave(8, lambda p: (0, 1.5 * math.sin(2 * math.pi * p), 1.8 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, b=bob: (0, b * math.cos(4 * math.pi * p) - b * 0.5, 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, b=bob / K: (-2 * b * math.cos(4 * math.pi * p), 0, 0), Lc))
        for i in range(4):
            t[f"tail{i+1}"] = track(rot=wave(8, sy(3 + 1.5 * i, 0.25 - 0.08 * i), Lc))
        m.anim(name, Lc, True, t)
    # attack: big sideways tail swing with the thagomizer
    m.anim("attack", 1.0, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.3, 0, 10, 0), (0.55, 0, -14, 0), (1.0, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.3, -4, 14, 0), (0.55, -4, -22, 0), (1.0, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.3, 0, 14, 0), (0.55, 0, -24, 0), (1.0, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.3, 0, 12, 0), (0.55, 0, -24, 0), (1.0, 0, 0, 0)])),
        "tail4": track(rot=keys([(0, 0, 0, 0), (0.3, 0, 10, 0), (0.55, 0, -20, 0), (1.0, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, 0, -8, 0), (0.55, 0, 8, 0), (1.0, 0, 0, 0)])),
    })
    m.anim("sit", 4.0, True, quad_sit(m, 14, neck=6))
    jk = [(0, 0, 0, 0), (0.6, 0, 0, 0)]
    for k in range(6):
        t0 = 0.75 + k * 0.3
        jk += [(t0, -12, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(2.8, 0, 0, 0)]
    m.anim("graze", 2.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.6, -14, 0, 0), (2.3, -14, 0, 0), (2.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.6, -14, 0, 0), (2.3, -14, 0, 0), (2.8, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
    })
    add_knockout(m)
    for a in m.animations:      # eat / beg / tame come from the 1x set: scale their position keys
        if a["name"].split(".")[-1] in ("eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    fit_to_ground(m, "graze", ("neck1", "skull"))
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
