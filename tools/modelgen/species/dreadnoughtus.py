"""
Dreadnoughtus schrani  (Late Cretaceous, Campanian-Maastrichtian; Cerro Fortaleza Formation, Santa Cruz, Argentina)

Reference:
  - Wikipedia; Lacovara et al. 2014; Bates et al. 2015; Ullmann & Lacovara 2016; Paul 2019: the most complete giant
    titanosaur known (~70 % of the skeleton), ~26 m long and 26-59 t by the estimates, still growing when it died.
    "Fears nothing".
  - Build: a neck of ~11 m, more than a third of the animal, carried high; a huge 1.7 m shoulder blade standing over
    a deep chest (a hump at the withers); a tail of ~9 m, shorter than the neck; the hips a little lower than the
    withers; column legs under a wide-gauge body; the hand a horseshoe of metacarpals with no fingers or claws.
  - Skull unknown (after its relatives Tapuiasaurus and Sarmientosaurus): small and long-snouted, the nostrils far
    back on an arch, pencil teeth at the front.
  - Colour unknown; kept from the old model: slate blue-grey with broken pale bars down the neck and the flanks and
    a cream belly; males darker with a white throat, females lighter and greyer.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared sauropod rig), built with the
construction of the Alamosaurus remaster at ~16 px = 1 m. The head is ~1.5x the real proportion. Body bobs only rise,
so the forefeet stay planted. The boom attack (the neck swung like a crane) and the "call" bellow are kept.
"""
import math
from paint import vnoise, hash3
from rig import Model, wave, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "dreadnoughtus"
K = 2.8          # ~2.8x the old model: scales the position keys of the shared 1x animations
HEAD = 1.1


def pattern(model, tx, rgb, region):
    """Fine scales, broken pale bars across the neck and down the flanks, a darker line along the spine; the males'
    throat white."""
    P, pal = tx.P, tx.pal
    tag, bone = tx.cube.tag, tx.cube.bone
    if tag in ("claw", "eye", "mouth", "tooth_cube", "saddle"):
        return rgb
    if tag == "throat":
        return pal["throat"] * (0.95 + 0.1 * vnoise(P[0] / 2.0, P[1] / 2.0, P[2] / 2.0, 11))
    if tag in ("skin", "limb"):
        c = hash3(math.floor(P[0] / 3), math.floor(P[1] / 3), math.floor(P[2] / 3), 57)
        rgb = rgb * (0.92 + 0.16 * c)
        if tag == "skin" and (region == "flank" or (region == "dorsal" and bone != "body")):
            bar = math.sin(P[2] * 0.33 + 0.6 * math.sin(P[1] * 0.25)) > 0.72
            broken = vnoise(P[0] / 8.0, P[1] / 8.0, P[2] / 8.0, 59) > 0.38
            if bar and broken:
                rgb = pal["bar"] * (0.95 + 0.1 * c)                         # broken pale bars
        if tag == "skin" and region == "dorsal" and bone == "body" and abs(P[0]) < 3.0:
            rgb = rgb * 0.8                                                  # the spine line
        if tag == "limb" and tx.face in ("north", "south", "east", "west") and int(math.floor(P[1])) % 5 == 0:
            rgb = rgb * 0.9                                                  # wrinkles on the legs
    return rgb


PALETTE = {"dorsal": "#4e5660", "flank": "#6e7884", "belly": "#d0d0c4", "bar": "#b8c0c4", "throat": "#eef0ea",
           "limb": "#5c646e", "limb_top": "#687078", "claw": "#2e2c2a", "claw_base": "#2e2c2a",
           "tooth_cube_base": "#d6cfb6", "tooth_cube_tip": "#efe9d8", "tooth": "#d8d0b8", "mouth": "#6e3330",
           "gum": "#4e2622", "eye": "#c0a050", "pupil": "#140f0a", "saddle": "#7a4f2e"}
SEXES = {"male": {"dorsal": "#404852", "flank": "#5e6874", "bar": "#c8d0d4"},
         "female": {"dorsal": "#646c74", "flank": "#848c96", "bar": "#aab2b6", "throat": "#9aa2a8"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (68, 36)                     # hip joint, a little lower than the withers
# a deep chest under the great shoulder blades (the hump at the withers), a long belly, the hips lower
TORSO = [("chest", (-25, 40, -98, 25, 88, -54)), ("withers", (-16, 88, -94, 16, 92, -58)),
         ("scapular_hump", (-13, 92, -92, 13, 96, -68)),
         ("belly", (-28, 36, -58, 28, 86, 8)), ("back", (-17, 86, -56, 17, 89, 4)),
         ("hips", (-24, 44, 6, 24, 82, 54)), ("sacrum", (-15, 82, 4, 15, 85, 44)),
         ("belly_low", (-21, 33, -86, 21, 36, -6)),
         ("ribs_l", (28, 44, -50, 29, 78, 2)), ("ribs_r", (-29, 44, -50, -28, 78, 2)),
         ("scapula_l", (25, 56, -98, 26, 94, -72)), ("scapula_r", (-26, 56, -98, -25, 94, -72))]
NECK = ([(84, -92), (104, -109), (122, -127), (139, -146), (154, -165), (168, -186), (180, -207), (191, -228)],
        [(26, 28), (23, 25), (20, 21), (17, 18), (14, 15), (12, 13), (10, 11)])
TAIL = ([(78, 56), (74, 86), (68, 114), (60, 140), (52, 162), (45, 180)],
        [(28, 28), (21, 21), (15, 15), (10, 10), (6, 6)])
FRONT_X, FRONT = 21, ([(72, -78), (40, -74), (14, -77)], [(16, 18), (14, 14, 0, "limb")])
HIND_X, HIND = 20, ([(68, 36), (37, 32), (11, 38), (4, 36)], [(19, 25, -1), (16, 16, 0, "limb"), (14, 12, 0, "limb")])
SADDLE = (89, -56, -26, 28, 28, 22)
SKULL_PITCH = -16
GRAZE = (-34, -24, -18, -14, -10, -6, -4, -8)   # neck1..7 then the skull, when grazing
WALK, RUN = (2.6, 13, 13, 0.6 * K), (1.5, 19, 19, 1.0 * K)
SIT = dict(drop=36, neck=-6, tail=(3, -3))


def armor(m, neck, tail):
    # no armour known: the males' throat is a white dewlap down the base of the neck
    y1, z1 = neck["segments"][0]["unposed"]
    hh = NECK[1][0][1]
    L = int(round(neck["segments"][0]["len"]))
    m.bone("male_display", "neck1", (0, y1, z1))
    m.box("male_display", (-5, y1 - hh / 2 - 4, z1 - L + 2), (5, y1 - hh / 2 + 1, z1 - 3), name="throat", tag="throat")


def attack(m, necks, tails):
    # the boom: the neck swings far to the left, then whips right across the front, the head knocking at the end
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.4, 0, 8, 0), (0.8, 0, -10, 0), (1.4, 0, 0, 0)]))}
    for i, b in enumerate(necks):
        d = 0.04 * i
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.4 + d, 0, 12, 0), (0.8 + d, 0, -16, 0), (1.1 + d, 0, 3, 0), (1.4, 0, 0, 0)]))
    t["skull"] = track(rot=keys([(0, 0, 0, 0), (0.4, 0, 10, 0), (0.85, -8, -14, 0), (1.4, 0, 0, 0)]))
    t["jaw"] = track(rot=keys([(0, 0, 0, 0), (0.7, 0, 0, 0), (0.85, -16, 0, 0), (1.1, 0, 0, 0), (1.4, 0, 0, 0)]))
    for i, b in enumerate(tails):
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.4, 0, -6 - 2 * i, 0), (0.8, 0, 8 + 2 * i, 0), (1.4, 0, 0, 0)]))
    m.anim("attack", 1.4, False, t)


def extra(m):
    # the bellow: the neck rises straight up, the throat swells, the jaw drops and the sound rolls out
    L = 2.6
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.6, 0, 0, 0), (2.0, 0, 0, 0), (L, 0, 0, 0)]))}
    for i in range(1, len(NECK[1]) + 1):
        t[f"neck{i}"] = track(rot=keys([(0, 0, 0, 0), (0.6, 6, 0, 0), (2.0, 6, 0, 0), (L, 0, 0, 0)]))
    t["skull"] = track(rot=keys([(0, 0, 0, 0), (0.6, 10, 0, 0), (2.0, 10, 0, 0), (L, 0, 0, 0)]))
    t["jaw"] = track(rot=keys([(0, 0, 0, 0), (0.6, -4, 0, 0), (0.8, -26, 0, 0), (1.8, -22, 0, 0), (2.1, 0, 0, 0), (L, 0, 0, 0)]))
    t["male_display"] = track(pos=keys([(0, 0, 0, 0), (0.8, 0, -1.5 * K, 0), (1.8, 0, -1.5 * K, 0), (2.1, 0, 0, 0), (L, 0, 0, 0)]))
    t["tail1"] = track(rot=keys([(0, 0, 0, 0), (0.8, 4, 0, 0), (2.0, 4, 0, 0), (L, 0, 0, 0)]))
    m.anim("call", L, False, t)


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

    # --- neck: very long (over a third of the animal), rising steeply, a low ridge along the top
    pts, secs = NECK
    necks = [f"neck{i + 1}" for i in range(len(secs))]
    neck = m.chain(necks, "body", 0, pts, "-z", secs, overlap=(4.0, 2.0))
    y1, z1 = neck["segments"][0]["unposed"]
    for seg, (w, hh) in zip(neck["segments"][:5], secs[:5]):
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

    # --- head: small and long-snouted, the nostrils far back on an arch, pencil teeth at the front
    B("skull", "cranium", (-5, -4, -7, 5, 5, 2), paint=MOUTH_DOWN)
    B("skull", "orbits", (-6, -2, -10, 6, 4, -4))
    B("skull", "nasal_arch", (-2, 3, -12, 2, 6, -4))
    B("skull", "snout", (-3, -4, -17, 3, 2, -6), paint=MOUTH_DOWN)
    B("skull", "muzzle", (-3, -4, -21, 3, 1, -17), paint=MOUTH_DOWN)
    for x in (-2, 0, 2):                                                    # thin pencil teeth across the muzzle
        a = h(x) - 0.5
        m.box("skull", (a, ay + h(-4) - 2, az + h(-21) + 0.5), (a + 1, ay + h(-4), az + h(-21) + 1.5),
              tag="tooth_cube", name="tooth", paint={"axis": "-y"})
    B("jaw", "jaw", (-3, -7, -20, 3, -4, -4), paint=MOUTH_UP)
    B("jaw", "jaw_back", (-5, -7, -4, 5, -4, 2), paint=MOUTH_UP)
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(6, 2, -7), "r": 1.2, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-6, 2, -7), "r": 1.2, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(1, 6, -9), "r": 1.0, "rx": 1.4, "mul": 0.45, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-1, 6, -9), "r": 1.0, "rx": 1.4, "mul": 0.45, "side": -1}]

    # --- front legs: wide-set columns; the hand a horseshoe of metacarpals with no fingers or claws
    fpts, fsecs = FRONT

    def front(side, sx):
        x = FRONT_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, fpts, "-y", fsecs, overlap=(3.0, 2.0))
        uy, uz = ch["segments"][0]["unposed"]
        a = x + 8 * sx
        m.box(f"upperarm_{side}", (min(a, a + 2 * sx), uy - 22, uz - 5), (max(a, a + 2 * sx), uy - 4, uz + 5),
              name="triceps")
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        H = f"hand_{side}"
        m.box(H, (x - 6, by - 12, bz - 6), (x + 6, by + 1, bz + 5), tag="limb", name="metacarpus")
        m.box(H, (x - 7, by - 14, bz - 7), (x + 7, by - 12, bz + 6), tag="limb", name="hand_pad")
    m.sym(front)

    # --- hind legs: wide-set pillars, a short padded foot with claws on the first three toes
    hpts, hsecs = HIND

    def hind(side, sx):
        x = HIND_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, hpts, "-y", hsecs, overlap=(3.0, 2.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 9, by - 4, bz - 8), (x + 9, by, bz + 8), tag="limb", name="foot_pad")
        for dx in (-7, -4, -1):                                             # claws on digits I-III (inner side)
            a = x + dx * sx
            m.box(T, (min(a, a + 2 * sx), by - 4, bz - 10), (max(a, a + 2 * sx), by - 1, bz - 7), tag="claw",
                  name="claw", paint={"axis": "-z"})
    m.sym(hind)

    # --- tail: shorter than the neck, tapering, held clear of the ground
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
