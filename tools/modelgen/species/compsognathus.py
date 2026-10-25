"""
Compsognathus longipes  (Tithonian, Solnhofen limestone, Bavaria; the larger Canjuers specimen, France)

Reference:
  - Size (Ostrom 1978; Peyer 2006): the Munich specimen ~0.9 m long (a juvenile), the French one ~1.25 m;
    ~20-29 cm at the hip, up to ~3 kg. Light, very long-legged runner; the tail more than half the length.
  - Skull (~7.6 cm in the Munich specimen): long, low and narrow, a pointed snout, very large orbits; small
    sharp teeth, those of the premaxilla unserrated.
  - Arms short with three fingers (Gishlick & Gauthier 2007), digit I the stoutest with a big claw, digit III
    tiny. Legs: shin and metatarsus long, three weight-bearing toes and a small hallux.
  - Integument: none preserved over the body, but its close relative Sinosauropteryx (Smithwick et al. 2017)
    shows a coat of simple filaments, rufous above and pale below (countershading), a dark "bandit mask"
    through the eye and a tail ringed light and dark; this model follows that.

v2x (2026-10-24, remaster at the T. rex v3 level): its own model (no longer the shared small-biped rig), at the
same ~55 px = 1 m of the old model so its tiny body keeps the detail (scale ~0.3 in SIZES). The head is ~1.3x
the real proportion. The animation set is the small-biped one (same pixel size, so no position scaling).
"""
import math
from rig import Model, lowest_point
import smalltheropod
from groundfit import fit_to_ground

ID = "compsognathus"


def pattern(model, tx, rgb, region):
    """A rufous filament coat with fine flecks, the tail ringed dark and light, a pale belly; scaly feet."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("claw", "eye", "mouth", "tooth"):
        return rgb
    if tag == "limb" and cube.bone.startswith(("toes", "foot")) and tx.face != "down":
        return rgb * (0.85 if int(math.floor(P[2] + P[1])) % 2 == 0 else 1.0)  # scutes
    if tag == "skin" and cube.bone == "jaw" and tx.face != "up":
        return pal["belly"] * 0.94                                            # pale throat (countershading)
    if tag in ("skin", "feather"):
        if cube.bone.startswith("tail") and region != "belly" and int(math.floor((P[2] - 8) / 3.0)) % 2 == 1:
            rgb = pal["ring"] * (0.94 if (tx.i + tx.j) % 2 else 1.0)          # the ringed tail
        if (tx.i * 7 + tx.j * 3) % 6 == 0:
            rgb = rgb * 0.86                                                  # filament flecks
        elif (tx.i * 5 + tx.j * 11) % 9 == 0:
            rgb = rgb * 1.08
    return rgb


PALETTE = {"dorsal": "#8a5530", "flank": "#b27a48", "belly": "#eddcbc", "limb": "#8a6a48", "limb_top": "#a8744a",
           "claw": "#2a2620", "claw_base": "#2a2620", "claw_tip": "#5d574c",
           "feather": "#7a4a2a", "ring": "#e6d4b2", "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
           "eye": "#c9932a", "pupil": "#120d08"}
SEXES = {"male": {"dorsal": "#80492a", "flank": "#b8783e", "feather": "#6e3e22"},
         "female": {"dorsal": "#8c6040", "flank": "#ae8458", "feather": "#7c5434", "ring": "#ddd0b4"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

HIP = (12, 4)
TORSO = [("hips", (-2, 9, -1, 2, 14, 6), "skin"), ("belly", (-2.5, 8, -9, 2.5, 14, 0), "skin"),
         ("chest", (-2, 8.5, -12, 2, 13.5, -8), "skin"), ("back", (-1.5, 14, -10, 1.5, 15, 5), "feather")]
NECK = ([(12, -11), (14.5, -14), (17, -16.5), (19.5, -18)], [(3, 3), (2, 3), (2, 2)])
HEAD_PITCH = 4
ARM_X, ARM = 2.5, ([(10, -10), (8, -9), (7, -11)], [(1, 2), (1, 1)])
LEG_X, LEG = 2, ([(12, 4), (8, 0.5), (3.5, 4), (1, 4)], [(2, 3, -0.5), (1, 2, 0.5, "limb"), (1, 1, 0.0, "limb")])
TAIL = ([(12, 6), (12.5, 13), (13, 20), (13, 27), (13, 34), (13.2, 43)], [(4, 4), (3, 3), (2, 2), (2, 2), (1, 1)])
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

    # --- neck: long and thin, S-curved, a fuzzy mane
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2", "neck3"], "body", 0, pts, "-z", secs, overlap=(1.0, 0.5))
    for seg, (w, hh) in zip(neck["segments"], secs):
        sy, sz = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-0.5, sy + hh / 2, sz - L), (0.5, sy + hh / 2 + 1, sz + 1), tag="feather", name="mane")
    ay, az = neck["end"]
    m.bone("head", "neck3", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (HEAD_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 1.5, az - 1))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head (px of the head, ~1.3x): long, low and narrow, a pointed snout and a big eye; the teeth (~2 mm) are
    # far below one pixel, so none are painted
    B("skull", "cranium", (-1.5, -1.5, -3, 1.5, 1.5, 1), paint=MOUTH_DOWN)
    B("skull", "face", (-1, -1.5, -6, 1, 0.5, -3), paint=MOUTH_DOWN)
    B("skull", "snout", (-1, -1.5, -8, 1, -0.5, -6), paint=MOUTH_DOWN)
    B("skull", "snout_tip", (-0.5, -1.5, -9, 0.5, -0.5, -8), paint=MOUTH_DOWN)  # the pointed premaxilla
    B("jaw", "jaw", (-1, -2.5, -8, 1, -1.5, -1), paint=MOUTH_UP)
    B("jaw", "jaw_tip", (-0.5, -2.5, -9, 0.5, -1.5, -8), paint=MOUTH_UP)
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (1.5, ay + 0.3, az - 1.5), "r": 1.0, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-1.5, ay + 0.3, az - 1.5), "r": 1.0, "side": -1},
                 {"kind": "band_y", "bones": ["skull"], "pos": (0, ay + 0.3, 0), "r": 0.6, "mul": 0.45,
                  "zmin": az - 5, "zmax": az + 1}]                            # the bandit mask

    # --- arms: short, digit I stout with a big claw, digit II long, digit III tiny
    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", x, ARM[0], "-y", ARM[1], overlap=(1.0, 0.5))
        ey, ez = ch["end"]
        F = f"forearm_{side}"
        m.box(F, (x - 0.5, ey - 0.5, ez - 2), (x + 0.5, ey + 0.5, ez), tag="limb", name="finger")       # digit II
        m.box(F, (x - 0.5, ey - 0.5, ez - 3), (x + 0.5, ey + 0.5, ez - 2), tag="claw", name="hand_claw",
              paint={"axis": "-z"})
        ix = x + 0.5 * sx                                                     # digit I, beside it
        m.box(F, (min(ix, ix + sx), ey - 0.5, ez - 1), (max(ix, ix + sx), ey + 0.5, ez), tag="limb", name="thumb")
        m.box(F, (min(ix, ix + sx), ey - 0.5, ez - 3), (max(ix, ix + sx), ey + 0.5, ez - 1), tag="claw",
              name="thumb_claw", paint={"axis": "-z"})
    m.sym(arm)

    # --- legs: long and slender, fuzzy thighs, three toes and a small hallux
    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, LEG[0], "-y", LEG[1], overlap=(1.0, 0.5))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        for dx, L in ((-1, 2), (0, 3), (1, 2)):                               # digits II, III, IV
            a = x - 0.5 + dx * sx
            m.box(T, (a, by - 1, bz - L), (a + 1, by, bz + 1), tag="limb", name="toe")
            m.box(T, (a, by - 1, bz - L - 1), (a + 1, by, bz - L), tag="claw", name="toe_claw")
        m.box(T, (x - 0.5, by, bz + 1), (x + 0.5, by + 1, bz + 2), tag="claw", name="hallux")
    m.sym(leg)

    # --- tail: very long and thin, the rings painted
    names = [f"tail{i+1}" for i in range(len(TAIL[1]))]
    m.chain(names, "body", 0, TAIL[0], "+z", TAIL[1], overlap=(1.0, 1.0))

    P = {"tail_secs": TAIL[1], "hip": HIP, "anim_speed": 1.3, "sit": {"drop": 5}}
    smalltheropod.animations(m, P)
    sit = next(a for a in m.animations if a["name"].endswith(".sit"))   # folded legs beside the belly
    for side, sg in (("l", 1), ("r", -1)):
        for bone, roll in (("thigh", SIT_SPLAY[0]), ("shin", SIT_SPLAY[1])):
            tr = sit["bones"][f"{bone}_{side}"]
            tr["rotation"] = [[k[0], k[1], k[2], k[3] + sg * roll] for k in tr["rotation"]]
    low = lowest_point(m, sit["bones"])
    for bone, tr in sit["bones"].items():
        if "position" in tr and (bone == "body" or bone.startswith("thigh")):
            tr["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in tr["position"]]
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    return m
