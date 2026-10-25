"""
Gallimimus bullatus  (Maastrichtian, Nemegt Formation, Mongolia)

Reference:
  - Size (Osmólska, Roniewicz & Barsbold 1972; Wikipedia): the largest well-known ornithomimid, ~6 m long,
    ~1.9 m at the hip, ~440 kg.
  - Skull (~33 cm): small, long and low, a toothless horny beak that widens a little at the tip (a "shovel"),
    very large eyes set high, the braincase rounded.
  - Neck: long and S-curved, about as long as the back. Arms short for an ornithomimid, three fingers of similar
    length with gently curved claws, weak hands.
  - Legs: built to run, the shin longer than the thigh, the long metatarsus pinched in the middle
    (arctometatarsus), three toes, no hallux.
  - Feathers (Ornithomimus edmontonicus, Zelenitsky et al. 2012; van der Reest et al. 2016): a coat of
    filament-like feathers over the body and neck, adults with longer feathers along the forearm (a
    "pennibrachium", for display or brooding) and on the tail; the shins and feet bare and scaly.

v2x (2026-10-24, remaster at the T. rex v3 level): its own model (no longer the shared small-biped rig), modelled
at 16 px = 1 m (one texture pixel = one vanilla pixel in game). The head is ~1.4x the real proportion. The
animation set is the small-biped one with its position keys scaled from the old ~10 px/m model.
"""
import math
from rig import Model, add_saddle, lowest_point
import smalltheropod
from groundfit import fit_to_ground

ID = "gallimimus"
K = 1.6          # 16 px/m now / ~10 px/m of the old model: scales the shared animations' position keys


def pattern(model, tx, rgb, region):
    """Plumage: a soft grey-brown coat with fine darker flecks, the wing and tail feathers dark with pale
    tips; bare scaly shins and feet; the beak with a darker cutting edge."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("claw", "eye", "mouth", "saddle"):
        return rgb
    if tag == "beak":
        return rgb * (0.82 if tx.face in ("east", "west") and tx.cy < 0.3 else 1.0)
    if tag == "feather":
        if cube.name.startswith(("wing", "tail_fan")):
            ax = 1 if cube.name.startswith("wing") else 2
            u = (P[ax] - cube.frm[ax]) / max(1.0, cube.to[ax] - cube.frm[ax])
            if u > 0.78:
                return pal["feather_tip"] * (0.94 if (tx.i + tx.j) % 2 else 1.0)
            return rgb * (0.85 if math.sin(P[ax] * 2 * math.pi / 2.0) > 0.5 else 1.0)
        if (tx.i * 7 + tx.j * 3) % 6 == 0:
            rgb = rgb * 0.86                                                  # flecks
        if region == "belly":
            return rgb * 1.05
        return rgb
    if tag == "limb" and cube.bone.startswith(("toes", "foot", "shin")) and tx.face != "down":
        return rgb * (0.86 if int(math.floor(P[1] + P[2] * 0.5)) % 2 == 0 else 1.0)   # scutes
    if tag == "skin":                                                         # the filament coat
        if (tx.i * 7 + tx.j * 3) % 6 == 0:
            rgb = rgb * 0.86
        elif (tx.i * 5 + tx.j * 11) % 9 == 0:
            rgb = rgb * 1.08
        if region == "dorsal" and math.sin(P[2] * 0.5 + P[0]) > 0.7:
            rgb = rgb * 0.9
    return rgb


PALETTE = {"dorsal": "#6e665a", "flank": "#9c917c", "belly": "#ebe4d0", "limb": "#8f8467", "limb_top": "#9c917c",
           "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#5d574c",
           "feather": "#4a4036", "feather_tip": "#e8e0cc", "beak": "#5a4e40",
           "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421", "eye": "#d89a2a", "pupil": "#120d08"}
SEXES = {"male": {"feather": "#3a3632", "feather_tip": "#f2efe6", "dorsal": "#5e5a52"},
         "female": {"feather": "#6a5a46", "feather_tip": "#cfc3a8", "dorsal": "#756a58"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

HIP = (30, 6)
TORSO = [("hips", (-5, 24, 0, 5, 36, 13), "skin"), ("belly", (-6, 22, -14, 6, 36, 2), "skin"),
         ("chest", (-5, 23, -20, 5, 35, -12), "skin"), ("back", (-5, 36, -16, 5, 38, 10), "feather"),
         ("shoulders", (-4, 34, -21, 4, 37, -15), "skin"), ("rump", (-4, 27, 13, 4, 35, 16), "skin")]
NECK = ([(33, -19), (40, -23), (47, -25), (53, -25)], [(5, 6), (4, 5), (4, 4)])
HEAD_PITCH = 6
ARM_X, ARM = 5.5, ([(31, -16), (26, -13), (24, -18)], [(2, 3), (2, 2)])
LEG_X, LEG = 4, ([(30, 6), (19, 1), (8.5, 6), (1, 6)], [(7, 10, -0.5), (4, 5, 0.5, "limb"), (2, 3, 0.0, "limb")])
TAIL = ([(32, 12), (32, 23), (32, 34), (31, 45), (30, 56)], [(7, 7), (5, 5), (4, 4), (3, 3)])
SADDLE = (38, -12, 2, 8, 6, 8)
GRAZE = {"body": -25, "neck1": -45, "neck2": -30, "neck3": -15, "skull": 15}
SIT_SPLAY = (10, -30)      # resting: thigh and shin roll out (deg)


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *HIP))
    for name, (x0, y0, z0, x1, y1, z1), tag in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name, tag=tag)

    # --- neck: long, S-curved, feathered
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2", "neck3"], "body", 0, pts, "-z", secs, overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck3", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (HEAD_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 1, az - 1))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head (px of the head, ~1.4x): rounded braincase, huge eyes, a long flat toothless beak
    B("skull", "cranium", (-2.5, -2, -3, 2.5, 2, 1), paint=MOUTH_DOWN)
    B("skull", "crown", (-2, 2, -3, 2, 3, 0))
    B("skull", "face", (-2, -2, -5, 2, 1, -3), paint=MOUTH_DOWN)
    B("skull", "beak", (-1.5, -1.5, -9, 1.5, 0.5, -5), tag="beak", paint=MOUTH_DOWN)
    B("skull", "beak_tip", (-2, -1.5, -10, 2, 0.5, -9), tag="beak", paint=MOUTH_DOWN)
    B("jaw", "lower_beak", (-1.5, -2.5, -10, 1.5, -1.5, -2), tag="beak", paint=MOUTH_UP)
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (2.5, ay + 0.5, az - 1.5), "r": 1.2, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-2.5, ay + 0.5, az - 1.5), "r": 1.2, "side": -1}]

    # --- arms: short, three clawed fingers, a fan of long forearm feathers (pennibrachium)
    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", x, ARM[0], "-y", ARM[1], overlap=(1.0, 0.5))
        ey, ez = ch["end"]
        F = f"forearm_{side}"
        m.box(F, (x - 1, ey - 1, ez - 1), (x + 1, ey + 1, ez + 1), tag="limb", name="hand")
        # the fingers hang on along the forearm's line (its frame is unposed: -y runs down the arm)
        for dz in (-1, 0):
            m.box(F, (x - 1, ey - 4, ez + dz), (x, ey - 1, ez + dz + 1), tag="limb", name="finger")
        m.box(F, (x, ey - 4, ez - 0.5), (x + 1, ey - 1, ez + 0.5), tag="limb", name="finger")
        m.box(F, (x - 1, ey - 5, ez - 1), (x + 1, ey - 4, ez + 1), tag="claw", name="hand_claws", paint={"axis": "-y"})
        xo = x + 1 * sx                                                       # in the forearm's frame +y runs back
        m.box(F, (min(xo, xo + sx), ey - 1, ez - 0.5), (max(xo, xo + sx), ey + 8, ez + 2.5), tag="feather", name="wing")
    m.sym(arm)

    # --- legs: long runner's legs, bare scaly shins and feet, three toes
    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, LEG[0], "-y", LEG[1], overlap=(1.5, 1.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 1.5, by - 1, bz - 1), (x + 1.5, by, bz + 1), tag="limb", name="toe_pad")
        for dx, L in ((-1.5, 4), (-0.5, 5), (0.5, 4)):
            a = x + dx * sx
            m.box(T, (min(a, a + sx), by - 1, bz - 1 - L), (max(a, a + sx), by, bz - 1), tag="limb", name="toe")
            m.box(T, (min(a, a + sx), by - 1, bz - 2 - L), (max(a, a + sx), by, bz - 1 - L), tag="claw", name="toe_claw")
    m.sym(leg)

    # --- tail: long, a fan of feathers along the rear half
    names = [f"tail{i+1}" for i in range(len(TAIL[1]))]
    tail = m.chain(names, "body", 0, TAIL[0], "+z", TAIL[1], overlap=(1.0, 1.0))
    for k, wid in ((2, 9), (3, 11)):
        s = tail["segments"][k]
        y0, z0 = s["unposed"]
        L = int(round(s["len"]))
        m.box(names[k], (-wid / 2, y0 - 0.5, z0), (wid / 2, y0 + 0.5, z0 + L + (3 if k == 3 else 1)), tag="feather",
              name="tail_fan")

    add_saddle(m, "body", *SADDLE)
    P = {"tail_secs": TAIL[1], "hip": HIP, "herbivore": True, "anim_speed": 1.2, "sit": {"drop": 16, "neck": 8}}
    smalltheropod.animations(m, P)
    for a in m.animations:      # position keys of the shared set were written for the old ~10 px/m model
        if a["name"].split(".")[-1] not in ("sit", "knocked_out", "wake"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    sit = next(a for a in m.animations if a["name"].endswith(".sit"))   # folded legs beside the belly
    for side, sg in (("l", 1), ("r", -1)):
        for bone, roll in (("thigh", SIT_SPLAY[0]), ("shin", SIT_SPLAY[1])):
            tr = sit["bones"][f"{bone}_{side}"]
            tr["rotation"] = [[k[0], k[1], k[2], k[3] + sg * roll] for k in tr["rotation"]]
    low = lowest_point(m, sit["bones"])
    for bone, tr in sit["bones"].items():
        if "position" in tr and (bone == "body" or bone.startswith("thigh")):
            tr["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in tr["position"]]
    att = next(a for a in m.animations if a["name"].endswith(".attack"))   # a peck and a shove, the weak arms stay out
    for side in ("l", "r"):
        tr = att["bones"][f"arm_{side}"]
        tr["rotation"] = [[k[0], k[1] * 0.3, k[2] * 0.3, k[3] * 0.3] for k in tr["rotation"]]
    gr = next(a for a in m.animations if a["name"].endswith(".graze"))   # the long neck reaches all the way down
    for bone, pitch in GRAZE.items():
        gr["bones"].setdefault(bone, {})["rotation"] = [[0, 0, 0, 0], [0.6, pitch, 0, 0], [2.1, pitch, 0, 0], [2.6, 0, 0, 0]]
    fit_to_ground(m, "graze", tuple(GRAZE))
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    return m
