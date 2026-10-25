"""
Struthiomimus altus  (Late Cretaceous, Campanian; Dinosaur Park and Horseshoe Canyon formations, Alberta)

Reference:
  - Size (Osborn 1917; Nicholls & Russell 1985; Wikipedia): the "ostrich mimic", ~4.3 m and ~150 kg, known from a
    nearly complete skeleton (AMNH 5339); hips ~1.4 m high. Lighter than the Gallimimus.
  - Skull: small, with big eyes and a slender, straight, toothless beak (no widened tip).
  - Neck: very long and S-curved, longer than the back.
  - Arms (Nicholls & Russell 1985): long for an ornithomimid, the three fingers of almost equal length with long,
    nearly straight claws, used together as a hook to pull down branches.
  - Legs: built to run (50-80 km/h estimated), the shin and the arctometatarsal foot longer than the thigh, three
    toes; a stiff tail held out as a balance pole.
  - Feathers (Ornithomimus, Zelenitsky et al. 2012; van der Reest et al. 2016): a filament coat, long forearm
    feathers in adults (a "pennibrachium") and a fan of feathers on the tail; bare scaly shins and feet.
  - Colour unknown; kept from the old model: rufous above, cream below, faint bars on the flanks, a dark cap;
    black wing feathers with white bars and tips on the males, dun with buff tips on the females.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared small-biped rig), built
with the construction of the Gallimimus remaster at ~20 px = 1 m, lighter, with a four-segment neck, a smaller
head, longer arms with the three long hooked fingers and longer shins. The head is ~1.4x the real proportion.
Males carry a low comb of plumes on the crown ("male_display") and the black-and-white wings.
"""
import math
from rig import Model, add_saddle, lowest_point
import smalltheropod
from groundfit import fit_to_ground

ID = "struthiomimus"
K = 2.0          # ~20 px/m now / ~10 px/m of the shared small-biped animations: scales their position keys


def pattern(model, tx, rgb, region):
    """Plumage: a rufous coat with fine flecks and faint bars down the flanks, a dark cap over the eyes; the wing
    and tail feathers dark with a pale bar and pale tips; bare scaly shins and feet; the beak with a darker edge."""
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
            if u > 0.8 or 0.4 < u < 0.52:
                return pal["feather_tip"] * (0.94 if (tx.i + tx.j) % 2 else 1.0)
            return rgb
        if (tx.i * 7 + tx.j * 3) % 6 == 0:
            rgb = rgb * 0.86
        return rgb
    if tag == "limb" and cube.bone.startswith(("toes", "foot", "shin")) and tx.face != "down":
        return rgb * (0.86 if int(math.floor(P[1] + P[2] * 0.5)) % 2 == 0 else 1.0)   # scutes
    if tag == "skin":
        if cube.bone == "skull" and cube.name in ("cranium", "crown") and P[1] > model._cap_y:
            return pal["cap"] * (0.95 if (tx.i + tx.j) % 2 else 1.0)          # dark cap over the eyes
        if (tx.i * 7 + tx.j * 3) % 6 == 0:
            rgb = rgb * 0.86
        elif (tx.i * 5 + tx.j * 11) % 9 == 0:
            rgb = rgb * 1.08
        if region == "flank" and math.sin(P[2] * 0.9 + P[1] * 0.2) > 0.75:
            rgb = rgb * 0.86                                                  # faint bars down the flanks
    return rgb


PALETTE = {"dorsal": "#8a5a3a", "flank": "#b8865a", "belly": "#f0e6d0", "cap": "#4a3020",
           "limb": "#a8805a", "limb_top": "#b8865a", "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#5d574c",
           "feather": "#2a2420", "feather_tip": "#f4f0e6", "beak": "#6a5a48",
           "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421", "eye": "#d8a030", "pupil": "#120d08"}
SEXES = {"male": {"feather": "#1e1a18", "feather_tip": "#fbf8f2", "dorsal": "#7a4a2e", "cap": "#36221a"},
         "female": {"feather": "#6a5848", "feather_tip": "#d8ccb4", "flank": "#b09070", "dorsal": "#8e6a4c", "cap": "#5a4030"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

HIP = (28, 6)
TORSO = [("hips", (-4.5, 22, 0, 4.5, 33, 12), "skin"), ("belly", (-5, 20, -12, 5, 33, 2), "skin"),
         ("chest", (-4.5, 21, -17, 4.5, 32, -10), "skin"), ("back", (-4.5, 33, -14, 4.5, 35, 9), "feather"),
         ("shoulders", (-3.5, 31, -18, 3.5, 34, -13), "skin"), ("rump", (-3.5, 25, 12, 3.5, 32, 15), "skin")]
NECK = ([(30, -16), (37, -20), (44, -22), (50, -22), (55, -20)], [(5, 5), (4, 4), (3, 4), (3, 3)])
HEAD_PITCH = 4
ARM_X, ARM = 5, ([(29, -14), (23, -10), (18, -14)], [(2, 3), (2, 2)])
LEG_X, LEG = 3.5, ([(28, 6), (19, 2), (8, 6.5), (1, 6)], [(6, 9, -0.5), (4, 4, 0.5, "limb"), (2, 3, 0.0, "limb")])
TAIL = ([(30, 12), (30, 22), (30, 32), (29, 42), (28, 52)], [(6, 6), (5, 5), (4, 4), (3, 3)])
SADDLE = (35, -11, 2, 8, 5.5, 7)
GRAZE = {"body": -14, "neck1": -56, "neck2": -38, "neck3": -22, "neck4": -10, "skull": 26}
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

    # --- neck: very long and S-curved, a soft ruff of plumage down its back
    pts, secs = NECK
    names = [f"neck{i + 1}" for i in range(len(secs))]
    neck = m.chain(names, "body", 0, pts, "-z", secs, overlap=(1.5, 1.0))
    for seg, (w, hh) in list(zip(neck["segments"], secs))[:2]:
        top = pts[0][0] + hh / 2
        z0 = seg["unposed"][1]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-1, top - 1, z0 - L), (1, top + 1, z0), tag="feather", name="ruff")
    ay, az = neck["end"]
    m.bone("head", names[-1], (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (HEAD_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 1, az - 1))
    m._cap_y = ay + 1.0

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head: small, rounded braincase, big eyes, a slender straight toothless beak
    B("skull", "cranium", (-2, -2, -3, 2, 2, 1), paint=MOUTH_DOWN)
    B("skull", "crown", (-1.5, 2, -2.5, 1.5, 3, 0.5))
    B("skull", "face", (-1.5, -2, -5, 1.5, 1, -3), paint=MOUTH_DOWN)
    B("skull", "beak", (-1, -1.5, -8, 1, 0.5, -5), tag="beak", paint=MOUTH_DOWN)
    B("skull", "beak_tip", (-0.5, -1.5, -10.5, 0.5, -0.5, -7.5), tag="beak", paint=MOUTH_DOWN)   # tapers to a blunt point
    B("jaw", "lower_beak", (-1, -2.5, -8, 1, -1.5, -2), tag="beak", paint=MOUTH_UP)
    B("jaw", "lower_beak_tip", (-0.5, -2.5, -10, 0.5, -1.5, -8), tag="beak", paint=MOUTH_UP)
    m.bone("male_display", "skull", (0, ay, az))
    B("male_display", "crest", (-0.5, 2.5, -1, 0.5, 3.5, 2), tag="feather")      # a low comb of plumes on the crown
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (2, ay + 0.3, az - 1.5), "r": 1.2, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-2, ay + 0.3, az - 1.5), "r": 1.2, "side": -1}]

    # --- arms: long, three long fingers of equal length with nearly straight claws, the pennibrachium
    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", x, ARM[0], "-y", ARM[1], overlap=(1.0, 0.5))
        ey, ez = ch["end"]
        F = f"forearm_{side}"
        m.box(F, (x - 1, ey - 1, ez - 1), (x + 1, ey + 1, ez + 1), tag="limb", name="hand")
        # the three fingers hang on along the forearm's line (its frame is unposed: -y runs down the arm),
        # two side by side in front and the third just behind them
        for fx, fz in ((-1, -1), (0, -1), (-0.5, 0)):
            m.box(F, (x + fx, ey - 6, ez + fz), (x + fx + 1, ey - 1, ez + fz + 1), tag="limb", name="finger")
            m.box(F, (x + fx, ey - 8, ez + fz), (x + fx + 1, ey - 6, ez + fz + 1), tag="claw", name="finger_claw",
                  paint={"axis": "-y"})
        xo = x + 1 * sx                                                       # in the forearm's frame +y runs back
        m.box(F, (min(xo, xo + sx), ey - 1, ez - 0.5), (max(xo, xo + sx), ey + 9, ez + 2.5), tag="feather", name="wing")
    m.sym(arm)

    # --- legs: long runner's legs, the shin longer than the thigh, bare scaly shins and feet, three toes
    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, LEG[0], "-y", LEG[1], overlap=(1.5, 0.4))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 1.5, by - 1, bz - 1), (x + 1.5, by, bz + 1), tag="limb", name="toe_pad")
        for dx, L in ((-1.5, 3), (-0.5, 4), (0.5, 3)):
            a = x + dx * sx
            m.box(T, (min(a, a + sx), by - 1, bz - 1 - L), (max(a, a + sx), by, bz - 1), tag="limb", name="toe")
            m.box(T, (min(a, a + sx), by - 1, bz - 2 - L), (max(a, a + sx), by, bz - 1 - L), tag="claw", name="toe_claw")
    m.sym(leg)

    # --- tail: stiff balance pole, a fan of feathers along the rear half
    names = [f"tail{i+1}" for i in range(len(TAIL[1]))]
    tail = m.chain(names, "body", 0, TAIL[0], "+z", TAIL[1], overlap=(1.0, 1.0))
    for k, wid in ((2, 9), (3, 11)):
        s = tail["segments"][k]
        y0, z0 = s["unposed"]
        L = int(round(s["len"]))
        m.box(names[k], (-wid / 2, y0 - 0.5, z0), (wid / 2, y0 + 0.5, z0 + L + (3 if k == 3 else 1)), tag="feather",
              name="tail_fan")

    add_saddle(m, "body", *SADDLE)
    P = {"tail_secs": TAIL[1], "hip": HIP, "herbivore": True, "anim_speed": 1.3, "sit": {"drop": 14, "neck": 8}}
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
    att = next(a for a in m.animations if a["name"].endswith(".attack"))   # a peck and a rake of the hooked hands
    for side in ("l", "r"):
        tr = att["bones"][f"arm_{side}"]
        tr["rotation"] = [[k[0], k[1] * 0.6, k[2] * 0.6, k[3] * 0.6] for k in tr["rotation"]]
    gr = next(a for a in m.animations if a["name"].endswith(".graze"))   # the long neck reaches all the way down
    for bone, pitch in GRAZE.items():
        gr["bones"].setdefault(bone, {})["rotation"] = [[0, 0, 0, 0], [0.6, pitch, 0, 0], [2.1, pitch, 0, 0], [2.6, 0, 0, 0]]
    fit_to_ground(m, "graze", tuple(GRAZE))
    fit_to_ground(m, "eat", ("neck1", "neck2", "neck3", "skull", "body"))
    return m
