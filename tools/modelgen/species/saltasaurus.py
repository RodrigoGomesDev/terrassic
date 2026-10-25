"""
Saltasaurus loricatus  (Late Cretaceous, Campanian-Maastrichtian; Lecho Formation, Salta, Argentina)

Reference:
  - Wikipedia; Bonaparte & Powell 1980; Powell 1992; Paul 2010; Chiappe et al. 1998 (Auca Mahuevo): the "lizard from
    Salta, armoured", the first sauropod found with body armour: large oval osteoderms (10-12 cm) set in a skin paved
    with thousands of pea-sized ossicles. A small, stocky saltasaurid of ~12 m and ~7 t.
  - Build: a short neck, a deep and very wide barrel, short stout column legs set wide apart (wide gauge), the
    shoulders about level with the hips; the hand a horseshoe of metacarpals with no fingers or claws; a short
    padded hind foot with claws on the first toes; a medium tail, stiff at the base.
  - Skull (after its relatives Bonatitan and Rapetosaurus): small and blunt, the nostrils high and set back on an
    arched snout, a broad square muzzle with peg teeth at the front.
  - The Auca Mahuevo nesting grounds of Patagonia, thousands of eggs in floodplain mud, are usually credited to
    saltasaurids: a herd animal that came back to the same nesting beaches.
  - Colour unknown; kept from the old model: olive-grey with dark mottling, a cream belly, bone-pale scutes; males
    darker with keeled, rust-tipped scutes, females browner and paler.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared sauropod rig), built with the
construction of the Alamosaurus remaster at ~16 px = 1 m. The head is ~1.8x the real proportion. The armour is now
dense: rows of oval scutes down the back and the flanks, on the shoulders and the hips, along the neck and the tail.
Body bobs only rise, so the forefeet stay planted. The rearing stomp is kept.
"""
import math
from paint import vnoise, hash3
from rig import Model, wave, track, keys, add_knockout, add_saddle, lowest_point
from quadruped import quad_gait, quad_sit
from groundfit import fit_to_ground

ID = "saltasaurus"
K = 2.0          # 2x the old model: scales the position keys of the shared 1x animations


def pattern(model, tx, rgb, region):
    """The ossicle pavement (a pebble per pixel, some standing out pale), dark blotches over the back and the flanks,
    wrinkled column legs; the scutes bone-pale with darker rims, the males' keels rust."""
    P, pal = tx.P, tx.pal
    tag = tx.cube.tag
    if tag in ("claw", "eye", "mouth", "tooth_cube", "saddle"):
        return rgb
    if tag == "scute":
        col = pal["scute"] * (1.1 if tx.face in ("up", "east", "west") else 0.85)
        return col * 0.8 if tx.edge else col
    if tag == "keel":
        return pal["keel"] * (1.12 if tx.face == "up" else 0.95)
    if tag in ("skin", "limb"):
        c = hash3(math.floor(P[0]), math.floor(P[1]), math.floor(P[2]), 43)
        rgb = rgb * (0.88 + 0.22 * c)
        if tag == "skin" and c > 0.93 and region != "belly":
            rgb = rgb * 0.5 + pal["ossicle"] * 0.5                         # pale ossicles in the pavement
        n = vnoise(P[0] / 7.0, P[1] / 7.0, P[2] / 7.0, 47)
        if tag == "skin" and region in ("dorsal", "flank") and n > 0.62:
            rgb = pal["mottle"] * (0.9 + 0.2 * c)                            # dark blotches
        if tag == "limb" and tx.face in ("north", "south", "east", "west") and int(math.floor(P[1])) % 4 == 0:
            rgb = rgb * 0.9                                                  # wrinkles on the legs
    return rgb


PALETTE = {"dorsal": "#5e6450", "flank": "#7e8468", "belly": "#d4ccae", "mottle": "#3e4434",
           "scute": "#c8bc9c", "keel": "#9a5a3a", "ossicle": "#b8b49c",
           "limb": "#6a6e58", "limb_top": "#767a62", "claw": "#3a3630", "claw_base": "#3a3630",
           "tooth_cube_base": "#d6cfb6", "tooth_cube_tip": "#efe9d8", "tooth": "#d8d0b8", "mouth": "#6e3330",
           "gum": "#4e2622", "eye": "#b08a30", "pupil": "#140f0a", "saddle": "#7a4f2e"}
SEXES = {"male": {"dorsal": "#4e5442", "flank": "#6e745a", "mottle": "#2e3428", "scute": "#d0c4a4", "keel": "#a85a30"},
         "female": {"dorsal": "#6e6c54", "flank": "#8e8a6e", "mottle": "#4e4c3c", "scute": "#bcb094", "ossicle": "#c4c0a8"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (40, 16)                     # hip joint
# a low, very wide barrel: the belly hangs low between the legs, the hips the widest point
TORSO = [("chest", (-16, 22, -48, 16, 46, -24)), ("withers", (-10, 46, -46, 10, 48, -28)),
         ("belly", (-20, 18, -28, 20, 46, 6)), ("back", (-12, 46, -26, 12, 48, 4)),
         ("hips", (-19, 24, 4, 19, 46, 26)), ("sacrum", (-12, 46, 4, 12, 48, 22)),
         ("belly_low", (-16, 16, -40, 16, 18, -2)),
         ("scapula_l", (16, 30, -46, 17, 44, -34)), ("scapula_r", (-17, 30, -46, -16, 44, -34))]
NECK = ([(40, -44), (47, -56), (53, -67), (57, -78), (60, -89)],
        [(17, 17), (15, 15), (12, 13), (9, 9)])
TAIL = ([(40, 22), (38, 38), (35, 53), (31, 67), (27, 80), (23, 92)],
        [(16, 16), (12, 12), (9, 9), (6, 6), (4, 4)])
FRONT_X, FRONT = 14, ([(38, -38), (20, -36), (6, -37)], [(9, 10), (8, 8, 0, "limb")])
HIND_X, HIND = 15, ([(40, 16), (22, 14), (7, 18), (3, 17)], [(11, 14, -1), (9, 9, 0, "limb"), (8, 7, 0, "limb")])
SADDLE = (48, -42, -26, 20, 16, 12)
SKULL_PITCH = -10
GRAZE = (-24, -22, -16, -10, -10)   # neck1..4 then the skull, when grazing
WALK, RUN = (2.0, 15, 15, 0.5 * K), (1.1, 22, 22, 0.9 * K)
SIT = dict(drop=20, neck=-8, tail=(3, -3))


def armor(m, neck, tail):
    # two staggered rows of big oval scutes down the back, a row on each flank, scutes over shoulders and hips
    for i, z in enumerate(range(-22, 24, 6)):
        for sx in (1, -1):
            x = (5 if i % 2 == 0 else 8) * sx
            m.box("body", (x - 2, 48, z - 2), (x + 2, 49, z + 2), name="scute", tag="scute")
    for z, hw, y in ((-40, 17, 41), (-18, 20, 34), (-8, 20, 34), (2, 20, 34), (14, 19, 42), (22, 19, 42)):
        for sx in (1, -1):
            x0 = hw if sx > 0 else -hw - 1
            m.box("body", (x0, y, z - 2), (x0 + 1, y + 3, z + 2), name="flank_scute", tag="scute",
                  paint={"axis": "+x" if sx > 0 else "-x"})
    for sx in (1, -1):                                                       # a lower row along the barrel
        for z in (-12, 0):
            x0 = 20 if sx > 0 else -21
            m.box("body", (x0, 26, z - 2), (x0 + 1, 29, z + 2), name="flank_scute_low", tag="scute",
                  paint={"axis": "+x" if sx > 0 else "-x"})
    for seg, (w, hh) in zip(neck["segments"], NECK[1]):                  # one scute on top of each neck segment
        sy, sz = seg["unposed"]
        zm = sz - seg["len"] / 2.0
        m.box(seg["bone"], (-1.5, sy + hh / 2, zm - 1.5), (1.5, sy + hh / 2 + 1, zm + 1.5), name="neck_scute", tag="scute")
    for seg, (w, hh) in list(zip(tail["segments"], TAIL[1]))[:4]:          # a pair down the tail
        sy, sz = seg["unposed"]
        zm = sz + seg["len"] / 2.0
        for sx in (1, -1):
            x = max(1, w // 4) * sx
            m.box(seg["bone"], (x - 1, sy + hh / 2, zm - 1.5), (x + 1, sy + hh / 2 + 1, zm + 1.5),
                  name="tail_scute", tag="scute")
    # the males' scutes carry a keel: a taller rust ridge down the midline
    m.bone("male_display", "body", (0, 48, 0))
    for z in range(-22, 24, 6):
        m.box("male_display", (-1, 48, z - 1.5), (1, 50, z + 1.5), name="keel", tag="keel")


def attack(m, necks, tails):
    # rears onto the hind legs, the forefeet paw the air, then the whole weight comes down: the armoured tank's stomp
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.45, 18, 0, 0), (0.62, 4, 0, 0), (0.7, 0, 0, 0), (0.9, 0, 0, 0), (1.2, 0, 0, 0)]),
                       pos=keys([(0, 0, 0, 0), (0.45, 0, 3.5 * K, 2 * K), (0.62, 0, 0.6 * K, 0), (0.7, 0, 0, -K), (0.9, 0, 0, -K), (1.2, 0, 0, 0)])),
         "neck1": track(rot=keys([(0, 0, 0, 0), (0.45, -12, 0, 0), (0.7, 6, 0, 0), (1.2, 0, 0, 0)])),
         "skull": track(rot=keys([(0, 0, 0, 0), (0.45, -6, 0, 0), (0.7, 6, 0, 0), (1.2, 0, 0, 0)])),
         "jaw": track(rot=keys([(0, 0, 0, 0), (0.4, -16, 0, 0), (0.75, -4, 0, 0), (1.2, 0, 0, 0)]))}
    for side in ("l", "r"):
        t[f"upperarm_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.45, -42, 0, 0), (0.7, 0, 0, 0), (0.9, 0, 0, 0), (1.2, 0, 0, 0)]))
        t[f"forearm_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.45, 48, 0, 0), (0.7, 0, 0, 0), (0.9, 0, 0, 0), (1.2, 0, 0, 0)]))
        t[f"thigh_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.45, -14, 0, 0), (0.7, 0, 0, 0), (1.2, 0, 0, 0)]))
    for i, b in enumerate(tails):
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.45, -9 - 2 * i, 0, 0), (0.7, 3, 0, 0), (1.2, 0, 0, 0)]))
    m.anim("attack", 1.2, False, t)


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

    # --- neck: short and thick, held forward and up, a dewlap fold under the base
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

    # --- head: small and blunt, the brows bulging, the nostrils high on an arched snout, a broad square muzzle
    B("skull", "cranium", (-4, -3, -5, 4, 4, 2), paint=MOUTH_DOWN)
    B("skull", "orbits", (-5, -1, -7, 5, 3, -3))
    B("skull", "nasal_arch", (-2, 3, -10, 2, 6, -3))
    B("skull", "snout", (-4, -3, -11, 4, 3, -5), paint=MOUTH_DOWN)
    B("skull", "muzzle", (-4, -3, -14, 4, 2, -11), paint=MOUTH_DOWN)
    for x in (-3, -1, 1):                                                  # peg teeth across the front of the muzzle
        m.box("skull", (x + 0.5, ay - 5, az - 13.5), (x + 1.5, ay - 3, az - 12.5),
              tag="tooth_cube", name="tooth", paint={"axis": "-y"})
    B("jaw", "jaw", (-3, -5, -12, 3, -3, -1), paint=MOUTH_UP)
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (5, ay + 1, az - 5), "r": 1.1, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-5, ay + 1, az - 5), "r": 1.1, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": (1, ay + 6, az - 7), "r": 0.9, "rx": 1.3, "mul": 0.45, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": (-1, ay + 6, az - 7), "r": 0.9, "rx": 1.3, "mul": 0.45, "side": -1}]

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

    # --- hind legs: stout pillars, a short padded foot with claws on the first three toes
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

    # --- tail: medium, stiff and thick at the base, tapering
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
