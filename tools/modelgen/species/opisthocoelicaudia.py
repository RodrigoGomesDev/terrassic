"""
Opisthocoelicaudia skarzynskii  (Late Cretaceous, Maastrichtian; Nemegt Formation, Mongolia)

Reference:
  - Wikipedia; Borsuk-Bialynicka 1977; Currie et al. 2018: a small, stocky titanosaur of 11-12 m and ~8-9 t, known
    from a nearly complete skeleton that lacked only the neck and head (probably carried off by scavengers, whose
    tooth marks are on the bones).
  - Named for its tail vertebrae, convex behind ("opisthocoelous"), which lock the tail into a stiff, strong rod:
    Borsuk-Bialynicka read it as a prop for rearing up on the hind legs, a tripod to browse the high canopy.
  - Build: a short, wide, deep body, the hips massive and higher than the shoulders, short column legs set wide
    apart; the hand a horseshoe of metacarpals with no fingers or claws; the neck probably held low and forward.
  - Head unknown (after its relatives Nemegtosaurus and Quaesitosaurus, from the same rocks): short and boxy, a broad
    muzzle with peg teeth, the nostrils on a bump high on the snout, a deep lower jaw.
  - Colour unknown; kept from the old model: sandy ochre of the Gobi with dark dorsal blotches and tail rings; males
    darker with a dark neck stripe, a crest of skin down the neck and a rust throat, females plain sand.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared sauropod rig), built with the
construction of the Saltasaurus remaster at ~16 px = 1 m. The head is ~1.8x the real proportion. Body bobs only rise,
so the forefeet stay planted. Its "graze" is still the tripod (rears onto the tail to pull leaves from the canopy),
and the hip-swing shove is kept.
"""
import math
from paint import vnoise, hash3
from rig import Model, wave, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "opisthocoelicaudia"
K = 2.0          # 2x the old model: scales the position keys of the shared 1x animations


def pattern(model, tx, rgb, region):
    """Fine even scales, dark blotches over the back, the stiff tail ringed, a dark stripe down the neck; the males'
    crest dark and the throat rust."""
    P, pal = tx.P, tx.pal
    tag, bone = tx.cube.tag, tx.cube.bone
    if tag in ("claw", "eye", "mouth", "tooth_cube", "saddle"):
        return rgb
    if tag == "crest":
        return pal["crest"] * (1.08 if tx.face == "up" else 0.95)
    if tag == "throat":
        n = vnoise(P[0] / 3.0, P[1] / 3.0, P[2] / 3.0, 23)
        return pal["throat"] * (0.9 + 0.2 * n)
    if tag in ("skin", "limb"):
        c = hash3(math.floor(P[0] / 2.0), math.floor(P[1] / 2.0), math.floor(P[2] / 2.0), 31)
        rgb = rgb * (0.93 + 0.14 * c)
        n = vnoise(P[0] / 8.0, P[1] / 8.0, P[2] / 8.0, 37)
        if tag == "skin" and region in ("dorsal", "flank") and n > 0.6:
            rgb = pal["blotch"] * (0.9 + 0.2 * c)                            # dark dorsal blotches
        if bone.startswith("tail") and math.floor(P[2] / 6) % 2 == 0:
            rgb = rgb * 0.8                                                  # rings down the stiff tail
        if bone.startswith("neck") and region == "dorsal" and abs(P[0]) < 2.5:
            rgb = pal["stripe"] * (0.95 + 0.1 * c)                           # the neck stripe
        if tag == "limb" and tx.face in ("north", "south", "east", "west") and int(math.floor(P[1])) % 4 == 0:
            rgb = rgb * 0.9                                                  # wrinkles on the legs
    return rgb


PALETTE = {"dorsal": "#a88a5a", "flank": "#c4a876", "belly": "#e4d8b8", "blotch": "#6e5236", "stripe": "#4e3a28",
           "crest": "#5e4430", "throat": "#9a5c3c",
           "limb": "#b09868", "limb_top": "#baa274", "claw": "#3a3630", "claw_base": "#3a3630",
           "tooth_cube_base": "#d6cfb6", "tooth_cube_tip": "#efe9d8", "tooth": "#d8d0b8", "mouth": "#6e3330",
           "gum": "#4e2622", "eye": "#8a6a2c", "pupil": "#140f0a", "saddle": "#7a4f2e"}
SEXES = {"male": {"dorsal": "#987a4c", "blotch": "#5e4228", "stripe": "#3e2c1c", "throat": "#a4583a"},
         "female": {"dorsal": "#b89a6a", "flank": "#d0b484", "blotch": "#8a6e4c", "stripe": "#a88a5a", "throat": "#c4a876"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (42, 16)                     # hip joint, higher than the shoulders
# short, deep and wide: the chest low, the hips massive and high, the back short
TORSO = [("chest", (-15, 20, -44, 15, 42, -22)), ("withers", (-9, 42, -42, 9, 44, -26)),
         ("belly", (-19, 16, -26, 19, 44, 6)), ("back", (-11, 44, -24, 11, 47, 4)),
         ("hips", (-19, 22, 4, 19, 48, 26)), ("sacrum", (-12, 48, 4, 12, 51, 22)),
         ("belly_low", (-14, 14, -36, 14, 16, -2)),
         ("scapula_l", (15, 28, -42, 16, 40, -30)), ("scapula_r", (-16, 28, -42, -15, 40, -30))]
NECK = ([(36, -40), (39, -54), (41, -68), (43, -81), (44, -93)],
        [(17, 17), (15, 15), (12, 13), (9, 9)])
TAIL = ([(42, 22), (39, 40), (35, 57), (30, 72), (24, 86), (18, 98)],
        [(22, 22), (17, 17), (13, 13), (9, 9), (6, 6)])
FRONT_X, FRONT = 14, ([(36, -36), (19, -34), (6, -35)], [(9, 10), (8, 8, 0, "limb")])
HIND_X, HIND = 15, ([(42, 16), (23, 14), (7, 18), (3, 17)], [(12, 15, -1), (9, 9, 0, "limb"), (8, 7, 0, "limb")])
SADDLE = (44, -38, -24, 18, 15, 12)
SKULL_PITCH = -6
WALK, RUN = (1.9, 16, 16, 0.5 * K), (1.0, 24, 24, 0.9 * K)
SIT = dict(drop=20, neck=-6, tail=(-21, -2, 0, 0, 0))


def armor(m, neck, tail):
    # no armour: the males' display is a crest of skin down the neck and a rust throat
    y1, z1 = neck["segments"][0]["unposed"]
    hh = NECK[1][0][1]
    m.bone("male_display", "neck1", (0, y1, z1))
    m.box("male_display", (-1, y1 + hh / 2 - 0.5, z1 - 16), (1, y1 + hh / 2 + 1.5, z1 + 1), name="neck_crest", tag="crest")
    m.box("male_display", (-5, y1 - hh / 2 - 2.5, z1 - 13), (5, y1 - hh / 2 + 0.5, z1 - 1), name="throat", tag="throat")


def attack(m, necks, tails):
    # the shove: the hips swing with the shoulder, the stiff tail sweeps the other way, then the right forefoot stamps
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.3, 2, 14, 0), (0.6, 0, -10, 0), (1.1, 0, 0, 0)]),
                       pos=keys([(0, 0, 0, 0), (0.3, 1.5 * K, 0.5 * K, 0), (0.6, -K, 0, -K), (1.1, 0, 0, 0)])),
         "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, 0, -12, 0), (0.6, 4, 8, 0), (1.1, 0, 0, 0)])),
         "skull": track(rot=keys([(0, 0, 0, 0), (0.3, 0, -6, 0), (0.6, 6, 4, 0), (1.1, 0, 0, 0)])),
         "jaw": track(rot=keys([(0, 0, 0, 0), (0.3, -12, 0, 0), (0.7, 0, 0, 0), (1.1, 0, 0, 0)])),
         "upperarm_r": track(rot=keys([(0, 0, 0, 0), (0.3, -35, 0, 0), (0.55, 0, 0, 0), (0.8, 0, 0, 0), (1.1, 0, 0, 0)])),
         "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.3, 45, 0, 0), (0.55, 0, 0, 0), (0.8, 0, 0, 0), (1.1, 0, 0, 0)]))}
    for i, b in enumerate(tails):
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.3, 0, -10 - 2 * i, 0), (0.6, 0, 8 + 2 * i, 0), (1.1, 0, 0, 0)]))
    m.anim("attack", 1.1, False, t)


def tripod(m, necks, tails):
    # the tripod browse: the stiff tail plants on the ground, the body rears on the hips, the forefeet hang, the neck
    # reaches up into the canopy and the jaw strips leaves
    L = 3.6
    jk = [(0, 0, 0, 0), (1.0, 0, 0, 0)]
    for k in range(5):
        t0 = 1.2 + k * 0.3
        jk += [(t0, -12, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(3.0, 0, 0, 0), (L, 0, 0, 0)]
    hold = lambda a: track(rot=keys([(0, 0, 0, 0), (0.9, a, 0, 0), (2.9, a, 0, 0), (L, 0, 0, 0)]))
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.9, TRI["body"], 0, 0), (2.9, TRI["body"], 0, 0), (L, 0, 0, 0)]),
                       pos=keys([(0, 0, 0, 0), (0.9, 0, TRI["lift"], TRI["back"]), (2.9, 0, TRI["lift"], TRI["back"]), (L, 0, 0, 0)])),
         "skull": hold(TRI["skull"]), "jaw": track(rot=keys(jk))}
    for b, a in zip(necks, TRI["neck"]):
        t[b] = hold(a)
    for b, a in zip(tails, TRI["tail"]):
        t[b] = hold(a)
    for side in ("l", "r"):
        t[f"upperarm_{side}"] = hold(TRI["arm"][0])
        t[f"forearm_{side}"] = hold(TRI["arm"][1])
        t[f"thigh_{side}"] = hold(TRI["leg"][0])
        t[f"shin_{side}"] = hold(TRI["leg"][1])
        t[f"foot_{side}"] = hold(TRI["leg"][2])
    m.anim("graze", L, False, t)


TRI = dict(body=30, lift=0, back=0, neck=(10, 8, 6, 4), skull=-10, tail=(-21, -2, 0, 0, 0),
           arm=(-45, 55), leg=(0, 0, 0))


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

    # --- neck: short and thick, held low and forward, a dewlap fold under the base
    pts, secs = NECK
    necks = [f"neck{i + 1}" for i in range(len(secs))]
    neck = m.chain(necks, "body", 0, pts, "-z", secs, overlap=(3.0, 1.5))
    y1, z1 = neck["segments"][0]["unposed"]
    m.box("neck1", (-6, y1 - 11, z1 - 11), (6, y1 - 8, z1 + 1), name="dewlap")

    ay, az = neck["end"]
    m.bone("head", necks[-1], (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (SKULL_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 3, az))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head: short and boxy, carried low, a broad muzzle with the nostrils on a bump, a deep lower jaw
    B("skull", "cranium", (-4, -3, -5, 4, 4, 2), paint=MOUTH_DOWN)
    B("skull", "orbits", (-5, -1, -7, 5, 3, -3))
    B("skull", "nasal_bump", (-2, 3, -9, 2, 5, -4))
    B("skull", "muzzle", (-4.5, -3, -12, 4.5, 1, -5), paint=MOUTH_DOWN)
    for x in (-3, -1, 1):                                                  # peg teeth across the front of the muzzle
        m.box("skull", (x + 0.5, ay - 5, az - 11.5), (x + 1.5, ay - 3, az - 10.5),
              tag="tooth_cube", name="tooth", paint={"axis": "-y"})
    B("jaw", "jaw", (-3.5, -7, -10, 3.5, -3, -1), paint=MOUTH_UP)
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (5, ay + 1, az - 5), "r": 1.1, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-5, ay + 1, az - 5), "r": 1.1, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": (1, ay + 5, az - 6.5), "r": 0.9, "rx": 1.3, "mul": 0.45, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": (-1, ay + 5, az - 6.5), "r": 0.9, "rx": 1.3, "mul": 0.45, "side": -1}]

    # --- front legs: short wide-set columns; the hand a horseshoe of metacarpals with no fingers or claws
    fpts, fsecs = FRONT

    def front(side, sx):
        x = FRONT_X * sx
        ch = m.chain([f"upperarm_{side}", f"forearm_{side}"], "body", x, fpts, "-y", fsecs, overlap=(2.0, 1.5))
        uy, uz = ch["segments"][0]["unposed"]
        a = x + 4 * sx
        m.box(f"upperarm_{side}", (min(a, a + 1 * sx), uy - 12, uz - 3), (max(a, a + 1 * sx), uy - 2, uz + 3),
              name="triceps")
        by, bz = ch["end"]
        m.bone(f"hand_{side}", f"forearm_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        H = f"hand_{side}"
        m.box(H, (x - 4, by - 5, bz - 4), (x + 4, by + 1, bz + 3), tag="limb", name="metacarpus")
        m.box(H, (x - 5, by - 6, bz - 5), (x + 5, by - 5, bz + 4), tag="limb", name="hand_pad")
    m.sym(front)

    # --- hind legs: stout pillars under the high hips, a short padded foot with claws on the first three toes
    hpts, hsecs = HIND

    def hind(side, sx):
        x = HIND_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, hpts, "-y", hsecs, overlap=(2.0, 1.5))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 5, by - 3, bz - 5), (x + 5, by, bz + 5), tag="limb", name="foot_pad")
        for dx in (-4, -2, 0):                                              # claws on digits I-III (inner side)
            a = x + dx * sx
            m.box(T, (min(a, a + 1 * sx), by - 3, bz - 7), (max(a, a + 1 * sx), by - 1, bz - 5), tag="claw",
                  name="claw", paint={"axis": "-z"})
    m.sym(hind)

    # --- tail: the stiff rod of locked vertebrae, thick and ringed
    tpts, tsecs = TAIL
    tails = [f"tail{i + 1}" for i in range(len(tsecs))]
    tail = m.chain(tails, "body", 0, tpts, "+z", tsecs, overlap=(2.0, 1.5))
    ty, tz = tail["end"]
    m.box(tails[-1], (-1, ty - 1, tz), (1, ty + 1, tz + 4), name="tail_tip")

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
    tripod(m, necks, tails)
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
    fit_to_ground(m, "eat", tuple(necks[:2] + ["skull"]))
