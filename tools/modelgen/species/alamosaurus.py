"""
Alamosaurus sanjuanensis  (Late Cretaceous, Maastrichtian; New Mexico, Texas, Utah)

Reference:
  - Size (Gilmore 1922; Fowler & Sullivan 2011; Tykoski & Fiorillo 2017; Wikipedia): the last and largest sauropod of
    North America, a titanosaur of 26-30 m and 30-80 t (the biggest bones, from Big Bend, rival the South American
    giants). It shared the land with Tyrannosaurus and Quetzalcoatlus.
  - Titanosaur plan: a wide-gauge stance (the feet set far apart), column legs, the shoulders about level with the
    hips; the hand a horseshoe of tall metacarpals with NO fingers or claws; the hind foot short and padded with
    claws on the first three toes; a long neck held forward and up; a long tapering tail.
  - Skull (after its relatives, Rapetosaurus, Tapuiasaurus): small, long and low, the nostrils pulled far back and up
    in front of the eyes, a square muzzle with thin pencil teeth at the front.
  - Skin: big rounded tubercles (titanosaur skin and embryos); at least one osteoderm is known, so a few scattered
    oval scutes along the back.
  - Colour unknown; kept from the old model: red-brown with big reticulated scales and faint bars down the flanks, a
    sandy belly; males darker with a dark dorsal stripe and a midline ridge, females paler.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared sauropod rig), built with the
construction of the Brachiosaurus remaster at 16 px = 1 m. The head is ~1.6x the real proportion (it is tiny next
to the body). Body bobs only rise, so the forefeet stay planted. The tail whip is kept.
"""
import math
from paint import vnoise, hash3
from rig import Model, wave, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "alamosaurus"
K = 3.2          # ~16 px/m now / ~5 px/m of the shared 1x animations: scales their position keys
HEAD = 1.2


def pattern(model, tx, rgb, region):
    """Big reticulated tubercles with darker seams, faint dark bars down the flanks, a dark dorsal stripe (the females'
    only a paler band), wrinkled column legs; scutes bone-pale."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag, bone = cube.tag, cube.bone
    if tag in ("claw", "eye", "mouth", "tooth_cube", "saddle"):
        return rgb
    if tag == "scute":
        return pal["scute"] * (1.1 if tx.face == "up" else 0.9)
    if tag == "crest":
        return pal["stripe"] * (0.94 if (tx.i + tx.j) % 3 == 0 else 1.0)
    if tag in ("skin", "limb"):
        cell = hash3(math.floor(P[0] / 4.0), math.floor(P[1] / 4.0), math.floor(P[2] / 4.0), 97)
        rgb = rgb * (0.92 + 0.16 * cell)
        n = vnoise(P[0] / 8.0, P[1] / 8.0, P[2] / 8.0, 101)
        rgb = rgb * (0.93 + 0.14 * n)
        if tag == "skin" and region == "dorsal" and bone == "body" and abs(P[0]) < 3.0:
            rgb = pal["stripe"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)          # dorsal stripe
        if tag == "skin" and region == "flank" and math.sin(P[2] * 0.18 + P[1] * 0.1) > 0.82:
            rgb = rgb * 0.9                                                  # faint dark bars down the flanks
        if bone.startswith("neck") and region != "dorsal" and int(math.floor(P[2] + P[1] * 0.6)) % 6 == 0:
            rgb = rgb * 0.92                                                 # neck folds
        if tag == "limb" and tx.face in ("north", "south", "east", "west") and int(math.floor(P[1])) % 5 == 0:
            rgb = rgb * 0.9                                                  # wrinkles on the legs
        edge = min((P[0] / 3.0) % 1, (P[1] / 3.0) % 1, (P[2] / 3.0) % 1)
        if edge < 0.12:
            rgb = rgb * 0.95                                                 # tubercle seams
    return rgb


PALETTE = {"dorsal": "#6e4e3a", "flank": "#9a7a5c", "belly": "#d8c8a8", "stripe": "#3e2c20", "scute": "#8a6a4c",
           "limb": "#7a5e48", "limb_top": "#8a6c52", "claw": "#3a3630", "claw_base": "#3a3630",
           "tooth_cube_base": "#d6cfb6", "tooth_cube_tip": "#efe9d8", "tooth": "#d8d0b8", "mouth": "#6e3330",
           "gum": "#4e2622", "eye": "#a8822c", "pupil": "#140f0a", "saddle": "#7a4f2e"}
SEXES = {"male": {"dorsal": "#5e4030", "stripe": "#2e2018", "flank": "#8e6e50"},
         "female": {"dorsal": "#7a5c44", "stripe": "#9a7a5c", "flank": "#a68868", "scute": "#9a7e60"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (78, 40)                     # hip joint
# a level back: deep chest, a wide barrel, broad titanosaur hips
TORSO = [("chest", (-28, 46, -110, 28, 98, -60)), ("withers", (-18, 98, -104, 18, 102, -66)),
         ("belly", (-32, 40, -64, 32, 96, 10)), ("back", (-19, 96, -62, 19, 100, 4)),
         ("hips", (-27, 52, 6, 27, 94, 62)), ("sacrum", (-17, 94, 4, 17, 98, 50)),
         ("belly_low", (-24, 37, -96, 24, 40, -6)),
         ("ribs_l", (32, 50, -56, 33, 88, 2)), ("ribs_r", (-33, 50, -56, -32, 88, 2)),
         ("scapula_l", (28, 62, -108, 29, 94, -84)), ("scapula_r", (-29, 62, -108, -28, 94, -84))]
NECK = ([(92, -100), (109, -122), (125, -143), (139, -164), (151, -185), (160, -206), (166, -226)],
        [(28, 30), (24, 26), (20, 22), (17, 18), (14, 15), (11, 12)])
TAIL = ([(84, 60), (80, 92), (74, 122), (66, 150), (58, 176), (50, 198), (43, 216)],
        [(32, 32), (25, 25), (19, 19), (14, 14), (10, 10), (6, 6)])
FRONT_X, FRONT = 24, ([(80, -86), (44, -82), (15, -85)], [(18, 20), (16, 16, 0, "limb")])
HIND_X, HIND = 23, ([(78, 40), (42, 36), (12, 42), (4, 40)], [(22, 28, -1), (18, 18, 0, "limb"), (16, 14, 0, "limb")])
SADDLE = (101, -84, -54, 30, 32, 22)
SKULL_PITCH = -14
GRAZE = (-26, -18, -13, -9, -6, -4, -8)   # neck1..6 then the skull, when grazing
WALK, RUN = (2.6, 13, 13, 0.6 * K), (1.5, 19, 19, 1.0 * K)
SIT = dict(drop=40, neck=-10, tail=(3, -3))


def armor(m, neck, tail):
    # scattered oval osteoderms along the back and the base of the tail; the males' midline ridge
    for x, z in ((-9, -50), (10, -34), (-7, -16), (12, -2), (-12, 16), (8, 32)):
        top = 100 if z < 4 else 98
        m.box("body", (x - 2, top - 1, z - 3), (x + 2, top + 1, z + 3), name="osteoderm", tag="scute")
    y0, z0 = tail["segments"][0]["unposed"]
    for x, dz in ((-6, 6), (7, 16)):
        m.box("tail1", (x - 2, y0 + 15, z0 + dz - 3), (x + 2, y0 + 17, z0 + dz + 3), name="osteoderm", tag="scute")
    m.bone("male_display", "body", (0, 100, 0))
    m.box("male_display", (-1.5, 100, -60), (1.5, 102, 50), name="ridge", tag="crest")


def attack(m, necks, tails):
    # the tail whip: the hips swing, the tail coils and cracks sideways, the wave running out to the tip
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.4, 0, 12, 0), (0.7, 0, -14, 0), (1.3, 0, 0, 0)])),
         "neck1": track(rot=keys([(0, 0, 0, 0), (0.4, 0, -8, 0), (0.7, 0, 8, 0), (1.3, 0, 0, 0)]))}
    for i, b in enumerate(tails):
        d = 0.06 * i
        amp = 12 + 6 * i
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.4 + d, -2, amp, 0), (0.7 + d, -2, -amp * 1.3, 0), (1.0 + d, 0, amp * 0.3, 0), (1.3, 0, 0, 0)]))
    m.anim("attack", 1.3, False, t)


def extra(m):
    pass


def ground_anim(m, name, n=18, passes=3):
    """Re-keys the root of a one-shot animation densely and lifts it wherever the feet would pass through the ground
    (the generic wake rolls a long-legged giant up through the ground)."""
    a = next(x for x in m.animations if x["name"].endswith("." + name))
    L = a["length"]
    root = a["bones"].setdefault("root", {})
    old = root.get("position", [[0, 0, 0, 0]])

    def interp(t):
        if t <= old[0][0]:
            return list(old[0][1:])
        for k0, k1 in zip(old, old[1:]):
            if k0[0] <= t <= k1[0]:
                f = (t - k0[0]) / max(1e-9, k1[0] - k0[0])
                return [float(k0[j]) + (float(k1[j]) - float(k0[j])) * f for j in (1, 2, 3)]
        return list(old[-1][1:])
    keys_ = [[round(L * k / n, 4)] + interp(L * k / n) for k in range(n + 1)]
    root["position"] = keys_
    for _ in range(passes):
        for key in keys_:
            low = lowest_point(m, a["bones"], key[0])
            if low < 0:
                key[2] = round(key[2] - low, 3)


def siny_(a, ph=0.0):
    return lambda p: (0, a * math.sin(2 * math.pi * (p + ph)), 0)


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)

    # --- neck: long, held forward and up, a dewlap fold under the base and a low ridge along the top
    pts, secs = NECK
    necks = [f"neck{i + 1}" for i in range(len(secs))]
    neck = m.chain(necks, "body", 0, pts, "-z", secs, overlap=(4.0, 2.0))
    y1, z1 = neck["segments"][0]["unposed"]
    m.box("neck1", (-10, y1 - 19, z1 - 22), (10, y1 - 14, z1 + 2), name="dewlap")
    for seg, (w, hh) in zip(neck["segments"][:4], secs[:4]):
        sy, sz = seg["unposed"]
        m.box(seg["bone"], (-2, sy + hh / 2, sz - int(round(seg["len"])) + 4), (2, sy + hh / 2 + 1, sz + 2), name="neck_ridge")

    ay, az = neck["end"]
    h = lambda v: int(round(v * HEAD))
    m.bone("head", necks[-1], (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (SKULL_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay + h(-4), az + h(0)))

    def at(x, y, z):
        return (h(x), ay + h(y), az + h(z))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, at(x0, y0, z0), at(x1, y1, z1), tag=tag, name=name, **kw)

    # --- head: long and low, the nostrils retracted up in front of the eyes, a square muzzle with pencil teeth
    B("skull", "cranium", (-5, -4, -7, 5, 5, 2), paint=MOUTH_DOWN)
    B("skull", "orbits", (-6, -2, -10, 6, 4, -4))
    B("skull", "nares", (-3, 3, -11, 3, 7, -4))
    B("skull", "snout", (-4, -4, -17, 4, 3, -6), paint=MOUTH_DOWN)
    B("skull", "muzzle", (-4, -4, -22, 4, 2, -17), paint=MOUTH_DOWN)
    for x in (-3, -1, 1, 3):                                                # thin pencil teeth across the muzzle
        a = h(x) - 0.5
        m.box("skull", (a, ay + h(-4) - 2, az + h(-22) + 0.5), (a + 1, ay + h(-4), az + h(-22) + 1.5),
              tag="tooth_cube", name="tooth", paint={"axis": "-y"})
    B("jaw", "jaw", (-4, -7, -21, 4, -4, -4), paint=MOUTH_UP)
    B("jaw", "jaw_back", (-5, -7, -4, 5, -4, 2), paint=MOUTH_UP)
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(6, 2, -7), "r": 1.3, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-6, 2, -7), "r": 1.3, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(2, 7, -8), "r": 1.2, "rx": 1.5, "mul": 0.45, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-2, 7, -8), "r": 1.2, "rx": 1.5, "mul": 0.45, "side": -1}]

    # --- front legs: wide-set columns; the hand a horseshoe of metacarpals with no fingers or claws
    fpts, fsecs = FRONT

    def front(side, sx):
        x = FRONT_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, fpts, "-y", fsecs, overlap=(3.0, 2.0))
        uy, uz = ch["segments"][0]["unposed"]
        a = x + 9 * sx
        m.box(f"upperarm_{side}", (min(a, a + 2 * sx), uy - 24, uz - 5), (max(a, a + 2 * sx), uy - 4, uz + 5),
              name="triceps")
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        H = f"hand_{side}"
        m.box(H, (x - 7, by - 13, bz - 7), (x + 7, by + 1, bz + 6), tag="limb", name="metacarpus")
        m.box(H, (x - 8, by - 15, bz - 8), (x + 8, by - 13, bz + 7), tag="limb", name="hand_pad")
    m.sym(front)

    # --- hind legs: wide-set pillars, a short padded foot with claws on the first three toes
    hpts, hsecs = HIND

    def hind(side, sx):
        x = HIND_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, hpts, "-y", hsecs, overlap=(3.0, 2.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 10, by - 4, bz - 9), (x + 10, by, bz + 9), tag="limb", name="foot_pad")
        for dx in (-8, -5, -2):                                             # claws on digits I-III (inner side)
            a = x + dx * sx
            m.box(T, (min(a, a + 2 * sx), by - 4, bz - 11), (max(a, a + 2 * sx), by - 1, bz - 8), tag="claw",
                  name="claw", paint={"axis": "-z"})
    m.sym(hind)

    # --- tail: long, tapering to a thin end, held clear of the ground
    tpts, tsecs = TAIL
    tails = [f"tail{i + 1}" for i in range(len(tsecs))]
    tail = m.chain(tails, "body", 0, tpts, "+z", tsecs, overlap=(3.0, 2.0))
    ty, tz = tail["end"]
    m.box(tails[-1], (-2, ty - 2, tz), (2, ty + 2, tz + 6), name="tail_tip")

    armor(m, neck, tail)
    add_saddle(m, "body", *SADDLE[:5], flap=SADDLE[5])
    animations(m, necks, tails)
    extra(m)
    return m


def animations(m, necks, tails):
    Li = 5.0
    idle = {"body": track(pos=wave(8, lambda p: (0, 0.125 * K * (1 + math.sin(2 * math.pi * p)), 0), Li))}   # rises only
    for i, b in enumerate(necks):
        idle[b] = track(rot=wave(8, lambda p, i=i: (0.8 * math.sin(2 * math.pi * (p - 0.06 * i)),
                                                    1.2 * math.sin(2 * math.pi * (p + 0.3 - 0.06 * i)), 0), Li))
    for i, b in enumerate(tails):
        idle[b] = track(rot=wave(8, siny_(2 + i, -0.08 * i), Li))
    m.anim("idle", Li, True, idle)
    for name, (Lc, Ah, Af, bob) in (("walk", WALK), ("run", RUN)):
        t = quad_gait(Lc, Ah, Af)
        t["body"] = track(rot=wave(8, lambda p: (0, 1.2 * math.sin(2 * math.pi * p), 1.0 * math.sin(2 * math.pi * p)), Lc),
                          pos=wave(8, lambda p, b=bob: (0, b * 0.5 * (1 + math.cos(4 * math.pi * p)), 0), Lc))
        t["neck1"] = track(rot=wave(8, lambda p, b=bob / K: (-1.5 * b * math.cos(4 * math.pi * p), 0, 0), Lc))
        for i, b in enumerate(tails):
            t[b] = track(rot=wave(8, siny_(2.5 + i, 0.25 - 0.08 * i), Lc))
        m.anim(name, Lc, True, t)
    attack(m, necks, tails)
    m.anim("sit", 4.0, True, quad_sit(m, SIT["drop"], neck=SIT["neck"], tail=SIT["tail"]))
    sit = m.animations[-1]
    low = min(lowest_point(m, sit["bones"], 4.0 * k / 8) for k in range(9))
    for bone, tr in sit["bones"].items():
        if "position" in tr and (bone == "body" or bone.startswith("thigh")):
            tr["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in tr["position"]]
    jk = [(0, 0, 0, 0), (0.6, 0, 0, 0)]
    for k in range(6):
        t0 = 0.75 + k * 0.3
        jk += [(t0, -10, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(2.8, 0, 0, 0)]
    g = {"jaw": track(rot=keys(jk))}
    for b, ang in zip(necks + ["skull"], GRAZE[:len(necks)] + GRAZE[-1:]):
        g[b] = track(rot=keys([(0, 0, 0, 0), (0.6, ang, 0, 0), (2.3, ang, 0, 0), (2.8, 0, 0, 0)]))
    m.anim("graze", 2.8, False, g)
    add_knockout(m, lift=0.3, neck_down=0)
    eat = next(a for a in m.animations if a["name"].endswith(".eat"))
    for bone in ("skull", "body"):                      # less head and body dip than the generic eat
        if bone in eat["bones"]:
            eat["bones"][bone]["rotation"] = [[k[0], k[1] * (0.4 if bone == "skull" else 0.0), k[2], k[3]]
                                              for k in eat["bones"][bone]["rotation"]]
    for a in m.animations:      # eat / beg / tame come from the 1x set: scale their position keys
        if a["name"].split(".")[-1] in ("eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    tame = next(a for a in m.animations if a["name"].endswith(".tame"))      # a smaller sway of the huge body
    if "body" in tame["bones"]:
        tame["bones"]["body"]["rotation"] = [[k[0], k[1], k[2], k[3] * 0.35] for k in tame["bones"]["body"]["rotation"]]
    ground_anim(m, "wake")
    fit_to_ground(m, "graze", tuple(necks + ["skull"]))
    fit_to_ground(m, "eat", tuple(necks[:2] + ["skull"]))
