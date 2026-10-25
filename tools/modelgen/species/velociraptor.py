"""
Velociraptor mongoliensis  (Campanian, Djadochta Formation, Mongolia; V. osmolskae from Inner Mongolia)

Reference:
  - Size (Norell & Makovicky 1999; Turner, Makovicky & Norell 2007): 1.5-2.07 m long, ~0.5 m at the hip,
    15-20 kg; the skull up to ~25 cm, long and low with a concave, slightly upturned snout, ~26-28 serrated
    teeth on each side of the upper jaw, the hind teeth larger and more curved.
  - Feathers (Turner et al. 2007): quill knobs on the ulna of IGM 100/981 = large pennaceous wing feathers like
    a bird's secondaries; the rest of the body covered by smaller feathers (dromaeosaurids such as Microraptor
    and Zhenyuanlong show a full coat, a tail fan and short feathered "trousers").
  - Hands: three long fingers with big curved claws, folded at the wrist like a bird's wing.
  - Feet: digit II carries the enlarged sickle claw (~6.5 cm on the bone, longer with the keratin) held off the
    ground; digits III and IV take the weight; a small first toe (hallux) behind.
  - Tail: long and stiff, wrapped in bony rods (elongated chevrons and zygapophyses) except at the base, held out
    straight as a balance; the "Fighting Dinosaurs" (Velociraptor locked with Protoceratops) show the sickle
    claw driven into the neck of the prey.

v2x (2026-10-24, remaster at the T. rex v3 level): its own model (no longer the shared small-biped rig), at the
same ~32 px = 1 m of the old model so its 2 m body keeps the detail (scale ~0.48 in SIZES). The head is ~1.3x
the real proportion. The animation set is the small-biped one (same pixel size, so no position scaling).
"""
import math
from rig import Model, lowest_point
import smalltheropod
from groundfit import fit_to_ground

ID = "velociraptor"


def pattern(model, tx, rgb, region):
    """Feathers: a dark-barred brown coat, the barring wider on the back, pale-tipped wing and tail feathers;
    a dark mask through the eye; scaly feet."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("claw", "eye", "mouth", "tooth"):
        return rgb
    if tag == "feather":
        name = cube.name
        if name.startswith(("primaries", "tail_fan")):
            # long feathers: dark bars across the vane and pale tips at the free end
            ax = 1 if name.startswith("primaries") else 2
            u = (P[ax] - cube.frm[ax]) / max(1.0, cube.to[ax] - cube.frm[ax])
            if u > 0.82:
                return pal["feather_tip"] * (0.92 if (tx.i + tx.j) % 2 else 1.0)
            if math.sin(P[ax] * 2 * math.pi / 2.5) > 0.4:
                return rgb * 0.7
            return rgb
        bar = math.sin(P[2] * 2 * math.pi / 4.4 + 0.7 * math.sin(P[0] * 0.8))
        if region == "dorsal" and bar > 0.15:
            rgb = rgb * 0.62
        elif bar > 0.55:
            rgb = rgb * 0.8
        if (tx.i * 3 + tx.j * 7) % 5 == 0:
            rgb = rgb * 1.08                                                  # loose feather texture
        return rgb
    if tag == "limb" and cube.bone.startswith(("toes", "foot")) and tx.face != "down":
        return rgb * (0.85 if int(math.floor(P[2] + P[1])) % 2 == 0 else 1.0)  # scutes
    if tag == "skin" and region in ("dorsal", "flank"):
        bar = math.sin(P[2] * 2 * math.pi / 4.4)
        if bar > 0.4:
            rgb = rgb * 0.8
    return rgb


PALETTE = {"dorsal": "#5f4229", "flank": "#9a7048", "belly": "#e7d7b5", "limb": "#7f6c50", "limb_top": "#8e6a46",
           "claw": "#1f1b18", "claw_base": "#2a2420", "claw_tip": "#6b6158",
           "feather": "#5b3e26", "feather_tip": "#e9dcc0", "tooth": "#efe7d2", "mouth": "#6a2e2a", "gum": "#3a2a20",
           "eye": "#e0b43c", "pupil": "#140f0a"}
SEXES = {"male": {"feather": "#3c2c20", "dorsal": "#553923", "feather_tip": "#f2e6c8", "eye": "#e8c040"},
         "female": {"feather": "#6a4a30", "dorsal": "#715237", "flank": "#a88058", "feather_tip": "#d7c6a2"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

HIP = (16, 4)
TORSO = [("hips", (-3, 12, -2, 3, 19, 7), "skin"), ("belly", (-3.5, 11, -11, 3.5, 19, -1), "feather"),
         ("chest", (-3, 11.5, -15, 3, 18.5, -10), "feather"), ("back", (-2.5, 19, -13, 2.5, 20, 6), "feather"),
         ("ruff", (-3.5, 16, -17, 3.5, 20, -12), "feather"), ("rump", (-2.5, 13, 6, 2.5, 18, 9), "feather")]
NECK = ([(17, -15), (20, -17), (23, -20)], [(4, 5), (3, 4)])
HEAD_PITCH = 2
ARM_X, ARM = 3.5, ([(14, -12), (11, -8.5), (11.5, -13)], [(2, 2), (2, 2)])
LEG_X, LEG = 2.5, ([(16, 4), (10.5, 0), (5, 4.5), (1, 2.5)], [(3, 5, -0.5), (2, 3, 0.5, "limb"), (2, 2, 0.0, "limb")])
TAIL = ([(16, 7), (16.5, 15), (17, 23), (17, 31), (17, 39)], [(5, 5), (4, 4), (3, 3), (2, 2)])
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

    # --- neck: S-curved, feathered
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(1.5, 1.0), tag="feather")
    for seg, (w, hh) in zip(neck["segments"], secs):                        # a mane of longer neck feathers
        sy, sz = seg["unposed"]
        L = int(round(seg["len"]))
        m.box(seg["bone"], (-1, sy + hh / 2, sz - L), (1, sy + hh / 2 + 1, sz + 1), tag="feather", name="mane")
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (HEAD_PITCH - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay - 2, az - 1))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        if "origin" in kw:
            ox, oy, oz = kw["origin"]
            kw["origin"] = (ox, ay + oy, az + oz)
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head (px of the head, HEAD ~1.3x): long and low, a concave upturned snout, serrated teeth
    teeth_up = {"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}
    teeth_dn = {"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}
    B("skull", "cranium", (-2, -2, -4, 2, 2, 1), paint=MOUTH_DOWN)
    B("skull", "face", (-1.5, -2, -7, 1.5, 1, -4), paint=teeth_up)
    B("skull", "snout", (-1, -2, -10, 1, 0, -7), paint=teeth_up)
    B("skull", "snout_tip", (-1, -2, -11, 1, 1, -10), paint=teeth_up)        # the upturned tip
    B("skull", "brow", (-2, 2, -4, 2, 3, -1), tag="feather")
    B("skull", "head_crest", (-1, 2, -1, 1, 4, 2), tag="feather")             # a small tuft of head feathers
    B("jaw", "jaw", (-1.5, -4, -10, 1.5, -2, -1), paint=teeth_dn)
    for sx in (1, -1):                                                        # the big hind teeth show
        B("skull", "fang", (min(0.5 * sx, 1.5 * sx), -3, -6, max(0.5 * sx, 1.5 * sx), -2, -5), tag="tooth")
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (2, ay + 0.5, az - 2.5), "r": 0.9, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-2, ay + 0.5, az - 2.5), "r": 0.9, "side": -1},
                 {"kind": "band_y", "bones": ["skull"], "pos": (0, ay + 0.5, 0), "r": 0.6, "mul": 0.55,
                  "zmin": az - 8, "zmax": az + 1}]

    # --- arms: folded like wings, three long clawed fingers, pennaceous feathers on the forearm and hand
    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", x, ARM[0], "-y", ARM[1], tag="feather", overlap=(1.0, 0.5))
        ey, ez = ch["end"]
        F = f"forearm_{side}"
        m.box(F, (x - 0.5, ey - 1, ez - 1), (x + 0.5, ey + 1, ez + 1), tag="limb", name="hand")
        # digits I-III and their claws carry on along the forearm's line (its frame is unposed: -y runs down the arm)
        for k, (dz, L) in enumerate(((-1, 2), (0, 3), (1, 2))):
            m.box(F, (x - 0.5, ey - 1 - L, ez + dz - 0.5), (x + 0.5, ey - 1, ez + dz + 0.5), tag="limb", name="finger")
            m.box(F, (x - 0.5, ey - 2 - L, ez + dz - 0.5), (x + 0.5, ey - 1 - L, ez + dz + 0.5), tag="claw", name="hand_claw",
                  paint={"axis": "-y"})
        # the folded wing: in the forearm's frame +y runs back along the arm and +z hangs below it
        xo = x + 0.5 * sx
        m.box(F, (min(xo, xo + sx), ey - 1, ez - 0.5), (max(xo, xo + sx), ey + 8, ez + 1.5), tag="feather", name="primaries")
        m.box(F, (min(xo, xo + sx), ey + 2, ez + 1.5), (max(xo, xo + sx), ey + 7, ez + 2.5), tag="feather", name="primaries_tip")
    m.sym(arm)

    # --- legs: feathered thighs, the sickle claw raised on digit II, a small hallux
    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, LEG[0], "-y", LEG[1], overlap=(1.0, 0.8))
        ty_, tz_ = ch["segments"][0]["unposed"]
        m.box(f"thigh_{side}", (x - 2, ty_ - 4, tz_ - 2.5), (x + 2, ty_ + 1, tz_ + 2.5), tag="feather", name="trousers")
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        for dx, L in ((-0.5, 4), (0.5, 3)):                                   # digits III and IV
            a = x + dx * sx
            m.box(T, (min(a, a + sx), by - 1, bz - L), (max(a, a + sx), by, bz + 1), tag="limb", name="toe")
            m.box(T, (min(a, a + sx), by - 1, bz - L - 1), (max(a, a + sx), by, bz - L), tag="claw", name="toe_claw")
        ix = x - 1.5 * sx                                                     # digit II, raised, the sickle claw
        m.box(T, (min(ix, ix + sx), by, bz - 2), (max(ix, ix + sx), by + 1, bz + 1), tag="limb", name="toe_ii")
        m.box(T, (min(ix, ix + sx), by, bz - 4), (max(ix, ix + sx), by + 3, bz - 2), tag="claw", name="sickle",
              rot=(-30, 0, 0), origin=(ix, by + 0.5, bz - 2), paint={"axis": "+y"})
        hx = x - 1 * sx
        m.box(T, (min(hx, hx + sx), by, bz + 1), (max(hx, hx + sx), by + 1, bz + 2), tag="claw", name="hallux")
    m.sym(leg)

    # --- tail: long and stiff, a feather fan along the rear half
    names = [f"tail{i+1}" for i in range(len(TAIL[1]))]
    tail = m.chain(names, "body", 0, TAIL[0], "+z", TAIL[1], overlap=(1.0, 1.0), tag="feather")
    for k, wid in ((1, 7), (2, 9), (3, 9)):
        s = tail["segments"][k]
        y0, z0 = s["unposed"]
        L = int(round(s["len"]))
        m.box(names[k], (-wid / 2, y0 - 0.5, z0), (wid / 2, y0 + 0.5, z0 + L + (2 if k == 3 else 1)), tag="feather",
              name="tail_fan")

    P = {"tail_secs": TAIL[1], "hip": HIP, "anim_speed": 1.0, "sit": {"drop": 7}}
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
    att = next(a for a in m.animations if a["name"].endswith(".attack"))   # the grab: arms forward, not into the chest
    for side in ("l", "r"):
        tr = att["bones"][f"arm_{side}"]
        tr["rotation"] = [[k[0], k[1] * 0.6 if k[1] < 0 else k[1], k[2], k[3]] for k in tr["rotation"]]
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    return m
