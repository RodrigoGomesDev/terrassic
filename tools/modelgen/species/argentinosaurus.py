"""
Argentinosaurus huinculensis  (Late Cretaceous, Cenomanian; Huincul Formation, Neuquén, Argentina)

Reference:
  - Wikipedia; Bonaparte & Coria 1993; Sellers et al. 2013; Paul 2019; Otero et al. 2020: known from a few
    vertebrae, ribs and a femur, yet by every estimate among the largest land animals ever: 30-35 m and 65-75 t.
    The Sellers model walked it at a stately 2 m/s.
  - Reconstructed after its better-known cousins (Patagotitan, Futalognkosaurus): a colossal barrel on wide-set
    column legs, the hips higher and heavier than the shoulders, a long neck held well up, a tiny head, a long thick
    tail; the hand a horseshoe of metacarpals with no fingers or claws, the hind foot short and padded with claws on
    the first toes.
  - Skull (after Sarmientosaurus and Tapuiasaurus): small with a rounded dome, the nostrils far back on an arch,
    a short broad muzzle with pencil teeth.
  - A heavy-sauropod skin of big rounded tubercles; no osteoderms are known.
  - Colour unknown; kept from the old model: weathered grey-brown with a greenish cast, a pale belly, horizontal
    wrinkles on the neck and legs; males darker with a near-black throat pouch, females paler and warmer.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared sauropod rig), built with the
construction of the Alamosaurus remaster at ~16 px = 1 m, the biggest animal in the mod. The head is ~1.4x the real
proportion. Body bobs only rise, so the forefeet stay planted. The one-footed tread is kept.
"""
import math
from paint import vnoise, hash3
from rig import Model, wave, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "argentinosaurus"
K = 3.0          # 3x the old model: scales the position keys of the shared 1x animations
HEAD = 1.2


def pattern(model, tx, rgb, region):
    """Big rounded tubercles (a coarse cell grid of light centres and dark seams), slow greenish weathering over the
    back, horizontal wrinkles on the neck and the legs; the throat skin loose and darker."""
    P, pal = tx.P, tx.pal
    tag, bone = tx.cube.tag, tx.cube.bone
    if tag in ("claw", "eye", "mouth", "tooth_cube", "saddle"):
        return rgb
    if tag == "tubercle":
        return pal["tubercle"] * (1.1 if tx.face in ("up", "east", "west") else 0.85)
    if tag == "dewlap":
        n = vnoise(P[0] / 3.0, P[1] / 2.0, P[2] / 3.0, 83)
        rgb = pal["throat"] * (0.9 + 0.2 * n)
        return rgb * 0.9 if int(math.floor(P[2])) % 4 == 0 else rgb               # folds
    if tag in ("skin", "limb"):
        cx, cy, cz = math.floor(P[0] / 4.0), math.floor(P[1] / 4.0), math.floor(P[2] / 4.0)
        c = hash3(cx, cy, cz, 89)
        fx, fy, fz = P[0] / 4.0 - cx, P[1] / 4.0 - cy, P[2] / 4.0 - cz
        seam = min(fx, 1 - fx, fy, 1 - fy, fz, 1 - fz) < 0.15
        rgb = rgb * (0.9 + 0.2 * c) * (0.86 if seam else 1.0)
        n = vnoise(P[0] / 10.0, P[1] / 10.0, P[2] / 10.0, 91)
        if region in ("dorsal", "flank"):
            rgb = rgb * (1 - 0.35 * n) + pal["moss"] * (0.35 * n)           # greenish weathering
        if bone.startswith(("neck", "thigh", "shin", "upperarm", "forearm")) and math.floor(P[1]) % 5 == 0:
            rgb = rgb * 0.86                                                  # horizontal wrinkles
    return rgb


PALETTE = {"dorsal": "#5a5248", "flank": "#7e7260", "belly": "#c8bca4", "moss": "#5e6a48",
           "tubercle": "#9a8e78", "throat": "#6a5648",
           "limb": "#66604e", "limb_top": "#726a58", "claw": "#3a3630", "claw_base": "#3a3630",
           "tooth_cube_base": "#d6cfb6", "tooth_cube_tip": "#efe9d8", "tooth": "#d8d0b8", "mouth": "#6e3330",
           "gum": "#4e2622", "eye": "#a08a40", "pupil": "#140f0a", "saddle": "#7a4f2e"}
SEXES = {"male": {"dorsal": "#4a4238", "flank": "#6e6250", "throat": "#2e2420", "moss": "#4e5a3c", "tubercle": "#8a7e68"},
         "female": {"dorsal": "#7a6e5c", "flank": "#968872", "belly": "#d8ccb4", "throat": "#8a7060", "moss": "#7a8260"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (99, 47)                     # hip joint, higher than the shoulders
# the deepest body in the mod: a colossal barrel, the hips taller and heavier than the shoulders
TORSO = [("chest", (-33, 54, -129, 33, 110, -70)), ("withers", (-21, 110, -122, 21, 113, -77)),
         ("belly", (-38, 47, -75, 38, 114, 12)), ("back", (-22, 114, -73, 22, 117, 5)),
         ("hips", (-32, 63, 7, 32, 118, 73)), ("hip_ridge", (-20, 118, 5, 20, 123, 58)),
         ("belly_low", (-28, 43, -112, 28, 47, -7)),
         ("ribs_l", (38, 58, -66, 40, 106, 2)), ("ribs_r", (-40, 58, -66, -38, 106, 2)),
         ("scapula_l", (33, 70, -126, 34, 106, -98)), ("scapula_r", (-34, 70, -126, -33, 106, -98))]
NECK = ([(108, -117), (128, -143), (146, -167), (163, -192), (177, -216), (187, -241), (194, -264)],
        [(33, 35), (28, 30), (23, 26), (19, 21), (15, 17), (11, 12)])
TAIL = ([(104, 70), (99, 108), (91, 143), (80, 176), (70, 206), (60, 232), (51, 253)],
        [(38, 38), (30, 30), (23, 23), (17, 17), (12, 12), (7, 7)])
FRONT_X, FRONT = 28, ([(94, -101), (51, -96), (18, -99)], [(21, 23), (19, 19, 0, "limb")])
HIND_X, HIND = 27, ([(99, 47), (53, 42), (14, 49), (5, 47)], [(26, 33, -1), (21, 21, 0, "limb"), (19, 16, 0, "limb")])
SADDLE = (113, -112, -80, 35, 33, 26)
SKULL_PITCH = -14
GRAZE = (-28, -19, -14, -10, -6, -4, -8)   # neck1..6 then the skull, when grazing
WALK, RUN = (3.0, 12, 12, 0.6 * K), (1.8, 17, 17, 0.9 * K)
SIT = dict(drop=46, neck=-10, tail=(3, -3))


def armor(m, neck, tail):
    # no osteoderms known: a loose dewlap under the throat and rows of big rounded tubercles along the flanks
    for seg, (w, hh) in list(zip(neck["segments"], NECK[1]))[:3]:
        sy, sz = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-w // 4, sy - hh / 2 - 4, sz - L + 4), (w // 4, sy - hh / 2 + 1, sz - 2), name="dewlap", tag="dewlap")
    for z, hw, y in ((-122, 33, 84), (-80, 33, 84), (-60, 38, 84), (-40, 38, 86), (-20, 38, 86), (0, 38, 86),
                     (20, 32, 94), (70, 32, 96)):
        for sx in (1, -1):
            x0 = hw if sx > 0 else -hw - 2
            m.box("body", (x0, y, z - 2), (x0 + 2, y + 4, z + 2), name="tubercle", tag="tubercle",
                  paint={"axis": "+x" if sx > 0 else "-x"})
    # the males' throat: a bigger, darker pouch and a crest of tubercles along the top of the neck base
    y1, z1 = neck["segments"][0]["unposed"]
    m.bone("male_display", "neck1", (0, y1, z1))
    m.box("male_display", (-8, y1 - 27, z1 - 22), (8, y1 - 20, z1 - 6), name="throat_pouch", tag="dewlap")
    m.box("male_display", (-1.5, y1 + 17, z1 - 28), (1.5, y1 + 19, z1 + 2), name="neck_crest", tag="tubercle")


def attack(m, necks, tails):
    # the tread: the weight shifts right, the left forefoot rises high, hangs, and slams down; the neck recoils
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.5, 3, 0, -4), (0.8, 3, 0, -4), (1.0, 0, 0, 0), (1.2, 0, 0, 0), (1.6, 0, 0, 0)]),
                       pos=keys([(0, 0, 0, 0), (0.5, K, 1.5 * K, 0), (0.8, K, 1.5 * K, 0), (1.0, 0, 0, 0), (1.08, 0, 0.5 * K, 0), (1.2, 0, 0, 0), (1.6, 0, 0, 0)])),
         "upperarm_l": track(rot=keys([(0, 0, 0, 0), (0.5, -55, 0, -10), (0.8, -60, 0, -10), (1.0, 0, 0, 0), (1.2, 0, 0, 0), (1.6, 0, 0, 0)])),
         "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.5, 70, 0, 0), (0.8, 75, 0, 0), (1.0, 0, 0, 0), (1.2, 0, 0, 0), (1.6, 0, 0, 0)])),
         "upperarm_r": track(rot=keys([(0, 0, 0, 0), (0.5, 4, 0, 6), (0.8, 4, 0, 6), (1.0, 0, 0, 0), (1.6, 0, 0, 0)])),
         "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, -8, 0, 4), (0.8, -8, 0, 4), (1.0, 10, 0, 0), (1.6, 0, 0, 0)])),
         "neck2": track(rot=keys([(0, 0, 0, 0), (0.5, -4, 0, 0), (1.0, 6, 0, 0), (1.6, 0, 0, 0)])),
         "skull": track(rot=keys([(0, 0, 0, 0), (0.5, -6, 0, 0), (1.0, 8, 0, 0), (1.6, 0, 0, 0)])),
         "jaw": track(rot=keys([(0, 0, 0, 0), (0.9, 0, 0, 0), (1.0, -14, 0, 0), (1.3, 0, 0, 0), (1.6, 0, 0, 0)]))}
    for i, b in enumerate(tails):
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.5, -2, 4 + i, 0), (1.0, 3, -3 - i, 0), (1.6, 0, 0, 0)]))
    m.anim("attack", 1.6, False, t)


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

    # --- neck: long and thick, held well up
    pts, secs = NECK
    necks = [f"neck{i + 1}" for i in range(len(secs))]
    neck = m.chain(necks, "body", 0, pts, "-z", secs, overlap=(4.0, 2.0))
    y1, z1 = neck["segments"][0]["unposed"]

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

    # --- head: small with a rounded dome, the nostrils far back on an arch, a short broad muzzle with pencil teeth
    B("skull", "cranium", (-5, -4, -7, 5, 6, 2), paint=MOUTH_DOWN)
    B("skull", "dome", (-4, 6, -6, 4, 7, 1))
    B("skull", "orbits", (-6, -1, -9, 6, 4, -4))
    B("skull", "nasal_arch", (-3, 4, -12, 3, 7, -6))
    B("skull", "snout", (-5, -4, -17, 5, 3, -7), paint=MOUTH_DOWN)
    B("skull", "muzzle", (-4, -4, -19, 4, 2, -17), paint=MOUTH_DOWN)
    for x in (-3, -1, 1, 3):                                                # thin pencil teeth across the muzzle
        a = h(x) - 0.5
        m.box("skull", (a, ay + h(-4) - 2, az + h(-19) + 0.5), (a + 1, ay + h(-4), az + h(-19) + 1.5),
              tag="tooth_cube", name="tooth", paint={"axis": "-y"})
    B("jaw", "jaw", (-4, -7, -18, 4, -4, -4), paint=MOUTH_UP)
    B("jaw", "jaw_back", (-5, -7, -4, 5, -4, 2), paint=MOUTH_UP)
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(6, 2, -7), "r": 1.2, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-6, 2, -7), "r": 1.2, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(2, 7, -10), "r": 1.2, "rx": 1.5, "mul": 0.45, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-2, 7, -10), "r": 1.2, "rx": 1.5, "mul": 0.45, "side": -1}]

    # --- front legs: wide-set columns; the hand a horseshoe of metacarpals with no fingers or claws
    fpts, fsecs = FRONT

    def front(side, sx):
        x = FRONT_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, fpts, "-y", fsecs, overlap=(3.0, 2.0))
        uy, uz = ch["segments"][0]["unposed"]
        a = x + 11 * sx
        m.box(f"upperarm_{side}", (min(a, a + 2 * sx), uy - 28, uz - 6), (max(a, a + 2 * sx), uy - 5, uz + 6),
              name="triceps")
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        H = f"hand_{side}"
        m.box(H, (x - 8, by - 16, bz - 8), (x + 8, by + 1, bz + 7), tag="limb", name="metacarpus")
        m.box(H, (x - 9, by - 18, bz - 9), (x + 9, by - 16, bz + 8), tag="limb", name="hand_pad")
    m.sym(front)

    # --- hind legs: wide-set pillars, a short padded foot with claws on the first three toes
    hpts, hsecs = HIND

    def hind(side, sx):
        x = HIND_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, hpts, "-y", hsecs, overlap=(3.0, 2.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 12, by - 5, bz - 11), (x + 12, by, bz + 11), tag="limb", name="foot_pad")
        for dx in (-10, -6, -2):                                             # claws on digits I-III (inner side)
            a = x + dx * sx
            m.box(T, (min(a, a + 3 * sx), by - 5, bz - 14), (max(a, a + 3 * sx), by - 1, bz - 10), tag="claw",
                  name="claw", paint={"axis": "-z"})
    m.sym(hind)

    # --- tail: long and thick, tapering, held clear of the ground
    tpts, tsecs = TAIL
    tails = [f"tail{i + 1}" for i in range(len(tsecs))]
    tail = m.chain(tails, "body", 0, tpts, "+z", tsecs, overlap=(3.0, 2.0))
    ty, tz = tail["end"]
    m.box(tails[-1], (-2, ty - 2, tz), (2, ty + 2, tz + 7), name="tail_tip")

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
