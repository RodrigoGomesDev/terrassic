"""
Thescelosaurus neglectus  (Late Cretaceous, Maastrichtian; Hell Creek and Lance formations, North America)

Reference:
  - Size (Gilmore 1913, 1915; Boyd 2014; Wikipedia): a stout bipedal ornithopod of 3.5-4 m and ~250-300 kg, one of
    the last dinosaurs before the extinction. "Willo" (NCSM 15728) is the specimen with the supposed fossil heart.
  - Skull (Boyd 2014; Button & Zanno 2023): long and low for its body, a horny beak over a premaxilla that still
    carries small teeth, leaf-shaped cheek teeth set in from the side of the face (fleshy cheeks), a palpebral bone
    jutting over each eye, a flared jugal under the orbit. A huge olfactory bulb, poor eyesight and inner ears tuned
    to low sounds: a sniffing, digging animal of the undergrowth.
  - Body: a deep barrel trunk with thin intercostal plates along the ribs, a thick neck, strong arms with five
    fingers (three clawed, two short), robust hind legs with the thigh LONGER than the shin (a walker, not a
    sprinter), four toes, and a long tail stiffened by ossified tendons, held out straight.
  - Skin: small scales (relatives such as Kulindadromeus carried filaments; not shown here).
  - Colour unknown; kept from the old model: olive-brown with a pale stripe along the flank and freckles; males with
    dark cheek patches, a rust throat and a heavier brow, females plainer.

v2x (2026-10-25, remaster at the T. rex v3 level): its own model (no longer the shared small-biped rig), built
with the construction of the Struthiomimus remaster at ~20 px = 1 m: deep barrel body, thick two-segment neck,
long low head with beak, cheeks, palpebrals and jugal flare, five-fingered hands, robust four-toed legs and a
straight stiff tail. The head is ~1.3x the real proportion. The "dig" action is kept.
"""
import math
from rig import Model, track, keys, lowest_point
import smalltheropod
from groundfit import fit_to_ground

ID = "thescelosaurus"
K = 2.0          # ~20 px/m now / ~10 px/m of the shared small-biped animations: scales their position keys


def pattern(model, tx, rgb, region):
    """Olive-brown scaly hide with fine scale flecks and freckles, a pale stripe along each flank and the tail,
    dark cheeks, a rust throat; the beak with a darker cutting edge; scutes on the shins and feet."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("claw", "eye", "mouth"):
        return rgb
    if tag == "beak":
        return rgb * (0.8 if tx.face in ("east", "west") and tx.cy < 0.3 else 1.0)
    if tag == "limb" and cube.bone.startswith(("toes", "foot", "shin")) and tx.face != "down":
        return rgb * (0.86 if int(math.floor(P[1] + P[2] * 0.5)) % 2 == 0 else 1.0)   # scutes
    if tag == "skin":
        bone = cube.bone
        if cube.name == "cheek":
            return pal["cheek"] * (0.94 if (tx.i + tx.j) % 2 else 1.0)
        if region == "belly" and bone.startswith("neck"):
            return pal["throat"] * (0.95 if (tx.i * 3 + tx.j) % 4 == 0 else 1.0)
        if region == "flank" and bone == "body" and abs(P[1] - model._stripe_y) < 0.9:
            return pal["stripe"].copy()                                         # pale stripe along the flank
        if region == "flank" and bone.startswith("tail") and abs(P[1] - (cube.frm[1] + cube.size[1] * 0.55)) < 0.7:
            return pal["stripe"].copy()
        if (tx.i * 7 + tx.j * 3) % 6 == 0:
            rgb = rgb * 0.88                                                    # scale flecks
        elif (tx.i * 5 + tx.j * 11) % 9 == 0:
            rgb = rgb * 1.07
        if region in ("dorsal", "flank") and math.sin(P[0] * 2.3 + P[1]) * math.sin(P[2] * 1.7) > 0.62:
            rgb = rgb * 0.82                                                    # freckles
    return rgb


PALETTE = {"dorsal": "#5c5a3a", "flank": "#8c8458", "belly": "#d8d0a8", "stripe": "#d4cc9c", "cheek": "#545034",
           "throat": "#b86a3a", "limb": "#7a7250", "limb_top": "#8c8458",
           "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#5d574c", "beak": "#4e4638",
           "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421", "eye": "#8a6a2a", "pupil": "#120d08"}
SEXES = {"male": {"cheek": "#423e28", "throat": "#c05a2a", "dorsal": "#52502e"},
         "female": {"cheek": "#6a6448", "throat": "#c8b088", "flank": "#948c64"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

HIP = (20, 5)
TORSO = [("hips", (-5.5, 15, -1, 5.5, 26, 10)), ("belly", (-6.5, 12, -13, 6.5, 25, 1)),
         ("chest", (-5.5, 13.5, -19, 5.5, 23.5, -12)), ("back", (-4.5, 25, -15, 4.5, 27, 8)),
         ("rump", (-4.5, 17, 10, 4.5, 25, 13))]
NECK = ([(22, -18), (25, -23), (27, -27)], [(8, 7), (7, 6)])
HEAD_PITCH = -6
ARM_X, ARM = 5.5, ([(20.5, -16), (15.5, -14.5), (11.5, -17)], [(3, 3), (2, 3)])
LEG_X, LEG = 4.0, ([(20, 5), (11.5, 0.5), (4.5, 3.5), (1, 3)], [(6, 9, -0.5), (4, 5, 0.5, "limb"), (3, 3, 0.0, "limb")])
TAIL = ([(22, 12), (22, 20), (21.5, 28), (21, 36), (20.5, 44)], [(7, 8), (5, 6), (4, 4), (3, 3)])
SIT_SPLAY = (10, -28)      # resting: thigh and shin roll out (deg)


def dig(m):
    # rooting: the body tips forward, the snout goes to the ground and the arms rake the soil in turns
    arm_l, arm_r, fore_l, fore_r = [], [], [], []
    for k in range(4):
        t0 = 0.5 + k * 0.4
        arm_l += [(t0, -45, 0, 0), (t0 + 0.2, 20, 0, 0)]
        arm_r += [(t0, 20, 0, 0), (t0 + 0.2, -45, 0, 0)]
        fore_l += [(t0, 25, 0, 0), (t0 + 0.2, 5, 0, 0)]
        fore_r += [(t0, 5, 0, 0), (t0 + 0.2, 25, 0, 0)]
    m.anim("dig", 2.6, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.5, -10, 0, 0), (2.1, -10, 0, 0), (2.6, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.5, 0, -1.0 * K, 0), (2.1, 0, -1.0 * K, 0), (2.6, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, -30, 0, 0), (2.1, -30, 0, 0), (2.6, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.5, -16, 0, 0), (2.1, -16, 0, 0), (2.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.5, -8, 0, 0), (0.9, -2, 0, 0), (1.3, -10, 0, 0), (1.7, -2, 0, 0), (2.1, -8, 0, 0), (2.6, 0, 0, 0)])),
        "arm_l": track(rot=keys([(0, 0, 0, 0)] + arm_l + [(2.6, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0)] + arm_r + [(2.6, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0)] + fore_l + [(2.6, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0)] + fore_r + [(2.6, 0, 0, 0)])),
        "thigh_l": track(rot=keys([(0, 0, 0, 0), (0.5, 8, 0, 0), (2.1, 8, 0, 0), (2.6, 0, 0, 0)])),
        "thigh_r": track(rot=keys([(0, 0, 0, 0), (0.5, 8, 0, 0), (2.1, 8, 0, 0), (2.6, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.5, 12, 0, 0), (2.1, 12, 0, 0), (2.6, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.7, 0, 10, 0), (1.1, 0, -10, 0), (1.5, 0, 10, 0), (1.9, 0, -10, 0), (2.6, 0, 0, 0)])),
    })


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m._stripe_y = 18.5
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *HIP))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)

    # --- neck: short, thick, rising forward
    pts, secs = NECK
    names = [f"neck{i + 1}" for i in range(len(secs))]
    neck = m.chain(names, "body", 0, pts, "-z", secs, overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", names[-1], (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (HEAD_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 2.5, az - 1))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head: long and low, a deep cheek region, the beak, palpebrals over small eyes
    B("skull", "cranium", (-3, -2.5, -4, 3, 2.5, 1), paint=MOUTH_DOWN)
    B("skull", "face", (-2.5, -2.5, -7.5, 2.5, 1.5, -3.5), paint=MOUTH_DOWN)
    B("skull", "snout", (-2, -2.5, -10.5, 2, 0.5, -7.5), paint=MOUTH_DOWN)
    B("skull", "beak", (-1.5, -2.5, -12, 1.5, -0.5, -10), tag="beak", paint=MOUTH_DOWN)
    for sx in (1, -1):
        x0 = 2.5 if sx > 0 else -3.5
        B("skull", "palpebral", (x0, 1.2, -5.5, x0 + 1, 2.2, -1.5))                    # bony bar over the eye
        x0 = 2.6 if sx > 0 else -3.6
        B("skull", "jugal", (x0, -2.2, -4, x0 + 1, -0.2, -1))                         # flare under the orbit
        x0 = 2.1 if sx > 0 else -3.1
        B("skull", "cheek", (x0, -2.2, -7, x0 + 1, -0.2, -4))                       # fleshy cheek over the inset teeth
    B("jaw", "lower_jaw", (-2, -4.5, -10.5, 2, -2.5, -1.5), paint=MOUTH_UP)
    B("jaw", "predentary", (-1, -4.5, -11.5, 1, -2.5, -10.5), tag="beak", paint=MOUTH_UP)
    m.bone("male_display", "skull", (0, ay, az))
    B("male_display", "brow", (-2.5, 2.5, -4, 2.5, 3.5, 0))
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (3, ay + 0.5, az - 2.5), "r": 1.0, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 0.5, az - 2.5), "r": 1.0, "side": -1}]

    # --- arms: strong, five fingers: three with blunt claws, two short ones on the outside
    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", x, ARM[0], "-y", ARM[1], overlap=(1.0, 0.5))
        ey, ez = ch["end"]
        F = f"forearm_{side}"
        m.box(F, (x - 1.5, ey - 1, ez - 1.5), (x + 1.5, ey + 1, ez + 1.5), tag="limb", name="hand")
        # the fingers carry on along the forearm's line (its frame is unposed: -y runs down the arm): three clawed
        # ones in front, the short clawless IV and V behind them on the outer side
        for fx in (-1.5, -0.5, 0.5):
            a = x + fx * sx
            m.box(F, (min(a, a + sx), ey - 3, ez - 1.5), (max(a, a + sx), ey - 1, ez - 0.5), tag="limb", name="finger")
            m.box(F, (min(a, a + sx), ey - 4, ez - 1.5), (max(a, a + sx), ey - 3, ez - 0.5), tag="claw", name="finger_claw",
                  paint={"axis": "-y"})
        for fx in (-0.5, 0.5):
            a = x + fx * sx
            m.box(F, (min(a, a + sx), ey - 2, ez - 0.5), (max(a, a + sx), ey - 1, ez + 0.5), tag="limb", name="finger_short")
    m.sym(arm)

    # --- legs: robust, the thigh longer than the shin, four toes (the first a short dewclaw)
    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, LEG[0], "-y", LEG[1], overlap=(1.5, 0.4))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 2, by - 1, bz - 1.5), (x + 2, by, bz + 1.5), tag="limb", name="toe_pad")
        for dx, L in ((-1.5, 3), (-0.5, 4), (0.5, 3)):
            a = x + dx * sx
            m.box(T, (min(a, a + sx), by - 1, bz - 1.5 - L), (max(a, a + sx), by, bz - 1.5), tag="limb", name="toe")
            m.box(T, (min(a, a + sx), by - 1, bz - 2.5 - L), (max(a, a + sx), by, bz - 1.5 - L), tag="claw", name="toe_claw")
        a = x - 2 * sx                                                         # the inner dewclaw, off the ground
        m.box(T, (min(a, a - sx), by + 1, bz - 1), (max(a, a - sx), by + 2, bz + 1), tag="claw", name="dewclaw")
    m.sym(leg)

    # --- tail: long, straight and stiff (ossified tendons)
    names = [f"tail{i+1}" for i in range(len(TAIL[1]))]
    m.chain(names, "body", 0, TAIL[0], "+z", TAIL[1], overlap=(1.0, 1.0))

    P = {"tail_secs": TAIL[1], "hip": HIP, "herbivore": True, "anim_speed": 0.9, "sit": {"drop": 10, "neck": 6}}
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
    dig(m)
    fit_to_ground(m, "graze", ("neck1", "neck2", "skull", "body"))
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    fit_to_ground(m, "dig", ("neck1", "neck2", "skull", "body"))
    return m
