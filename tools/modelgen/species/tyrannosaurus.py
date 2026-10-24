"""
Tyrannosaurus rex  (Late Cretaceous, western North America)

Reference:
  - Size (Wikipedia; Persons et al. 2019): Sue FMNH PR 2081 12.3-12.8 m, Scotty RSM P2523.8 ~13 m; hips 3.7-4.0 m;
    5.4-9 t. Longest skull 1.37-1.52 m, widest 0.90 m (Sue): the back of the head is ~2/3 as wide as it is long.
  - Skull (Carr 2025, Osborn 1906, Brochu 2003): very wide temporal region and narrow snout, so the eyes face
    forward (binocular vision); U-shaped muzzle tip; tall triangular maxilla with a large antorbital fossa and
    maxillary fenestra; inflated, rugose lacrimal "horn" in front of and above the orbit; postorbital boss and
    a massive subocular process making the orbit tall and keyhole-like; deep jugal strut with a rough jugal boss
    under the eye; rugose nasals with a row of bumps; deep lower jaw with a convex bottom edge and a bulging
    surangular behind the tooth row.
  - Teeth: 4 D-shaped premaxillary incisors per side, ~12 maxillary "lethal bananas" (up to 30 cm with root),
    ~13 dentary teeth.
  - Lips (Cullen et al. 2023): extra-oral tissue covered the teeth like a monitor lizard's; here a scaly lip
    line with only the tips of the biggest fangs showing when the mouth is shut (full teeth when it opens).
  - Skin (Bell et al. 2017): small pebbly basement scales with scattered larger feature scales on the neck, hip
    and tail; no feathers on those areas.
  - Body: short, deep S neck; arms ~1 m with two clawed fingers and a splint of a third metacarpal; very long
    legs with an arctometatarsalian foot, three weight-bearing toes and a small raised hallux; heavy tail base
    (caudofemoralis) as the counterweight; a big pubic boot between the legs.

v3 (2026-10-24, Rodrigo: "mais detalhado, é um T. rex"): modelled at TWICE the resolution of the other large
theropods (16 px = 1 m, so one texture pixel is one vanilla pixel in game, like the Ravager or the Warden), with a
sculpted skull ~1.5x the real proportion, separate fangs and tongue inside the mouth, scale mosaic, rugose
bosses and scutes. render_scale 0.5 = authoring scale; the in-game size comes from SIZES in
tools/javagen/gen_species.py (MODEL_SCALE ~1.0). Animations are the large theropod set (large_theropod.py).
"""
import math
from rig import Model, add_saddle, lowest_point
import large_theropod

ID = "tyrannosaurus"
K = 2.0  # authoring resolution relative to the large theropod rig (position keys of the shared set are scaled by it)


# ---------------------------------------------------------------------------------------------------- paint
def _cell(P, size):
    """Pebbly scale mosaic: staggered cells of `size` px; returns (distance to the cell edge 0..0.5, cell hash)."""
    a, b, c = P[0] / size, P[1] / size, P[2] / size
    row = math.floor(b)
    a += 0.5 * (row % 2)
    c += 0.5 * (row % 2)
    fa, fb, fc = a - math.floor(a), b - math.floor(b), c - math.floor(c)
    edge = min(fa, 1 - fa, fb, 1 - fb, fc, 1 - fc)
    h = (math.floor(a) * 73856093 ^ row * 19349663 ^ math.floor(c) * 83492791) & 1023
    return edge, h


def pattern(model, tx, rgb, region):
    """Dark bands across the back that break into blotches down the flanks, a dark mask through the eye, pale
    lips and throat, and a pebbly scale mosaic with scattered bigger feature scales (Bell et al. 2017)."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag, bone = cube.tag, cube.bone
    if tag in ("tooth_cube", "claw", "saddle", "eye", "mouth", "tongue"):
        return rgb
    if tag in ("rugose", "boss"):
        # keratin-covered rough bone: bumpy light and dark specks
        n = (tx.i * 7 + tx.j * 13 + tx.ci * 3) % 5
        return rgb * (0.86 if n == 0 else 1.08 if n == 3 else 1.0)
    if tag == "scute":
        return rgb * (1.1 if tx.face == "up" else 0.95)
    if tag == "skin":
        hy = model._head_y
        if bone in ("skull", "jaw"):
            if bone == "skull" and cube.name in ("orbit", "temporal", "jugal_l", "jugal_r") and abs(P[1] - (hy + 9)) < 3.5:
                rgb = rgb * 0.8                                              # eye mask
            if cube.name.startswith("antorbital") and tx.face in ("east", "west"):
                rgb = rgb * 0.88                                             # antorbital fossa shadow
            if bone == "jaw" and region != "dorsal":
                rgb = rgb * 0.82 + pal["belly"] * 0.18                       # pale lower jaw
        elif region in ("dorsal", "flank"):
            band = math.sin(P[2] * 2 * math.pi / 17 + 0.5 * math.sin(P[0] * 0.25))
            if region == "dorsal" and band > 0.3:
                rgb = rgb * 0.78
            elif region == "flank" and tx.cy > 0.45 and band > 0.55:
                edge, h = _cell(P, 3.0)
                if h % 3 != 0:                                               # bands break into blotches
                    rgb = rgb * 0.86
        if bone in ("neck1", "neck2") and region == "belly":
            rgb = rgb * 0.92 + pal["belly"] * 0.08
    if tag in ("skin", "limb"):
        if tag == "limb" and cube.bone.startswith(("toes", "foot")) and tx.face != "down":
            return rgb * (0.84 if int(math.floor(P[2] if cube.bone.startswith("toes") else P[1])) % 3 == 0 else 1.0)  # scutate scales
        edge, h = _cell(P, 3.0)
        if edge < 0.1:
            rgb = rgb * 0.95                                                 # scale outlines
        elif h % 23 == 0:
            rgb = rgb * 1.12                                                 # feature scale
    return rgb


# ---------------------------------------------------------------------------------------------------- palette
PALETTE = {"dorsal": "#43372a", "flank": "#6b563c", "belly": "#cfbb95", "limb": "#4b3d2d", "limb_top": "#665139",
           "claw": "#2b2723", "claw_base": "#3d3530", "claw_tip": "#c4b89f", "tooth": "#ece3cb", "mouth": "#7a3330",
           "gum": "#4a3a2c",  # lip line between the fang tips
           "tongue": "#9a4a44", "tooth_cube_base": "#cbbd9c", "tooth_cube_tip": "#f3eddd",
           "eye": "#e0a536", "pupil": "#140e09", "dark": "#2c241b", "scute": "#3a2f24",
           "rugose": "#5b4a37", "boss": "#3c3127"}
SEXES = {"male": {"boss": "#7b3524", "rugose": "#86452c", "dorsal": "#3f3328"},       # rusty display bosses
         "female": {"boss": "#4a3d2f", "rugose": "#665340", "flank": "#78624a"}}

MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
LIP_UP, LIP_LOW = MOUTH_DOWN, MOUTH_UP  # lips cover the teeth; the fang cubes show their tips (Cullen et al. 2023)

BODY = (62, 12)
TORSO = [("hips", (-13, 46, -2, 13, 72, 26)), ("belly", (-14, 34, -28, 14, 70, 0)),
         ("chest", (-12, 32, -48, 12, 66, -26)),
         ("withers", (-9, 66, -46, 9, 70, -28)), ("back_ridge", (-9, 70, -30, 9, 74, 22)),
         ("gastralia", (-10, 30, -42, 10, 34, -8)),
         ("pubic_boot", (-4, 24, -10, 4, 30, 4)), ("pubis", (-3, 30, -6, 3, 46, 2)),
         ("flank_l", (14, 40, -24, 15, 64, -2)), ("flank_r", (-15, 40, -24, -14, 64, -2)),
         ("pectoral_l", (12, 36, -46, 13, 58, -28)), ("pectoral_r", (-13, 36, -46, -12, 58, -28))]
NECK = ([(62, -46), (68, -56), (72, -64)], [(22, 22), (20, 20)])
TAIL = ([(62, 22), (61, 44), (61, 64), (62, 84), (63, 102)], [(24, 24), (17, 17), (11, 11), (6, 6)])
ARM_X = 14  # out on the side of the chest (at 11 the arms sank into it)
ARM = ([(46, -40), (40, -43), (36, -48)], [(4, 6), (3, 4)])
LEG_X = 14
LEG = ([(62, 12), (38, -2), (14, 16), (4, 8)], [(14, 22, -1), (10, 12, 2, "limb"), (6, 8, 0, "limb")])
SIT_SPLAY = (18, -34)  # resting: thigh and shin roll out (deg) so the folded legs lie beside the belly
SIT = (26, 62, -118, 62, -6, {"tail1": (9, 0, 0), "tail2": (4, 0, 0), "tail3": (-2, 0, 0), "neck1": (-6, 0, 0), "skull": (4, 0, 0)})


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern

    def mirror(bone, frm, to, **kw):
        """Left box as given (+X) and its mirror image on the right."""
        name = kw.pop("name")
        m.box(bone, frm, to, name=name + "_l", **kw)
        m.box(bone, (-to[0], frm[1], frm[2]), (-frm[0], to[1], to[2]), name=name + "_r", **kw)

    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)
    for z in (-36, -22, -16, 12, 18):                         # dorsal scutes (the saddle sits on -12..8)
        top = 70 if z < -30 else 74                                 # on the withers / on the back ridge
        m.box("body", (-1, top, z), (1, top + 1, z + 3), tag="scute", name="scute")

    # --- neck: short, deep S, a throat fold under it
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(3.0, 2.0))
    n1, n2 = neck["segments"]
    y1, z1 = n1["unposed"]
    m.box("neck1", (-8, y1 - 14, z1 - 10), (8, y1 - 11, z1 + 1), name="throat")
    for o in (3, 8):
        m.box("neck1", (-1, y1 + 11, z1 - o - 1), (1, y1 + 12, z1 - o + 2), tag="scute", name="scute")
    y2, z2 = n2["unposed"]
    m.box("neck2", (-7, y2 - 13, z2 - 9), (7, y2 - 10, z2 + 1), name="throat2")
    m.box("neck2", (-1, y2 + 10, z2 - 5), (1, y2 + 11, z2 - 2), tag="scute", name="scute")

    ay, az = neck["end"]
    m._head_y = ay
    m.bone("head", "neck2", (0, ay, az))                         # look bone (GeckoLib turns it)
    m.bone("skull", "head", (0, ay, az), (-2 - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay, az + 2))

    def S(name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box("skull", (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    def SM(name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        mirror("skull", (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    def J(name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box("jaw", (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    def JM(name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        mirror("jaw", (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- skull: wide temporal box, tall forward-facing orbits, two-step snout to a U-shaped muzzle
    S("temporal", (-10, 0, -8, 10, 13, 4), paint=MOUTH_DOWN)             # squamosal / quadratojugal block
    S("parietal", (-5, 13, -6, 5, 14, 4))                                # sagittal crest
    S("occiput", (-7, 3, 4, 7, 12, 6))                                   # back of the head, over the neck
    S("orbit", (-9, 1, -14, 9, 13, -8), paint=MOUTH_DOWN)                # orbit region (a bit narrower)
    SM("postorbital", (5, 13, -12, 10, 15, -7), tag="boss")              # postorbital bosses over the eyes
    SM("subocular", (9, 3, -12, 10, 7, -8), tag="boss")                  # subocular bar: the keyhole orbit
    SM("jugal", (10, -1, -14, 11, 6, -2))                                # deep jugal strut, flaring
    SM("jugal_boss", (11, 1, -7, 12, 3, -4), tag="rugose")              # rough jugal boss under the eye
    SM("lacrimal", (4, 12, -17, 8, 16, -13), tag="boss")                 # inflated lacrimal horn
    SM("lacrimal_tip", (5, 16, -16, 7, 17, -14), tag="rugose")
    S("antorbital", (-8, 0, -20, 8, 12, -14), paint=LIP_UP)               # maxilla, antorbital fossa
    S("antorbital_mid", (-7, 0, -26, 7, 10, -20), paint=LIP_UP)
    S("premaxilla", (-6, 0, -31, 6, 8, -26), paint=LIP_UP)               # U-shaped muzzle
    S("muzzle_tip", (-5, 1, -32, 5, 7, -31), paint=LIP_UP)
    S("nasal", (-2, 12, -20, 2, 13, -12), tag="rugose")                  # rugose nasals
    S("nasal_mid", (-2, 10, -26, 2, 11, -20), tag="rugose")
    for z, y in ((-25, 11), (-22, 11), (-18, 13), (-15, 13)):            # nasal bumps
        S("nasal_bump", (-1, y, z, 1, y + 1, z + 2), tag="rugose")
    # upper fangs along the outer edge of the upper jaw: the lower jaw fits inside it, so their tips hang over the
    # lower lip when the mouth is shut and the whole row shows when it opens
    for side in (1, -1):
        for k, z in enumerate((-31, -28, -25, -22, -19, -16)):
            half = 5 if z < -30 else 6 if z < -25 else 7 if z < -19 else 8
            L = 2 if k == 0 else 4 if 2 <= k <= 3 else 3
            x = side * half
            S("fang", (min(x, x - side), -L, z, max(x, x - side), 0, z + 1), tag="tooth_cube", paint={"axis": "-y"})

    # --- lower jaw: deep, convex bottom, surangular bulge, a tongue
    J("jaw_back", (-9, -11, -12, 9, 0, 2), paint=MOUTH_UP)
    JM("surangular", (9, -9, -10, 10, -3, 0))
    J("jaw_mid", (-6, -9, -20, 6, 0, -12), paint=LIP_LOW)
    J("jaw_front", (-5, -7, -27, 5, 0, -20), paint=LIP_LOW)
    J("chin", (-4, -6, -31, 4, 0, -27), paint=LIP_LOW)
    J("tongue", (-3, 0, -24, 3, 1, -6), tag="tongue")
    for side in (1, -1):
        for z in (-29, -25, -21, -17, -13):
            half = 4 if z < -27 else 5 if z < -20 else 6     # on the outer edge of the lower jaw, inside the upper one
            x = side * half
            J("fang_low", (min(x, x - side), 0, z, max(x, x - side), 3, z + 1), tag="tooth_cube", paint={"axis": "+y"})

    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (9, ay + 9, az - 11), "r": 1.5, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-9, ay + 9, az - 11), "r": 1.5, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": (5, ay + 6, az - 29.5), "r": 1.0, "rx": 1.2, "mul": 0.35, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": (-5, ay + 6, az - 29.5), "r": 1.0, "rx": 1.2, "mul": 0.35, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": (8, ay + 6, az - 17), "r": 1.5, "rx": 1.2, "mul": 0.7, "side": 1},     # maxillary fenestra
                 {"kind": "spot", "bones": ["skull"], "pos": (-8, ay + 6, az - 17), "r": 1.5, "rx": 1.2, "mul": 0.7, "side": -1}]

    # --- arms: short, robust, two clawed fingers and a splint
    apts, asecs = ARM

    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", x, apts, "-y", asecs, tag="limb", overlap=(2.0, 1.0))
        ey, ez = ch["end"]
        for name, (x0, x1) in (("finger_in", (-2, -1)), ("finger_out", (0, 1))):
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            m.box(f"forearm_{side}", (a, ey - 3, ez - 1), (b, ey, ez + 1), tag="limb", name=name)
            m.box(f"forearm_{side}", (a, ey - 5, ez - 1), (b, ey - 3, ez), tag="claw", name="claw", paint={"axis": "-y"})
        a = x + 1 * sx
        m.box(f"forearm_{side}", (min(a, a + sx), ey - 1, ez), (max(a, a + sx), ey, ez + 1), tag="limb", name="splint")
    m.sym(arm)

    # --- legs: drumstick thighs, long shins, arctometatarsalian feet, three toes and a hallux
    lpts, lsecs = LEG

    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, lpts, "-y", lsecs, overlap=(3.0, 2.0))
        ty, tz = ch["segments"][0]["unposed"]
        m.box(f"thigh_{side}", (x - 8, ty - 12, tz - 13), (x + 8, ty + 3, tz + 11), name="thigh_muscle")
        sy, sz = ch["segments"][1]["unposed"]
        m.box(f"shin_{side}", (x - 6, sy - 13, sz - 3), (x + 6, sy - 3, sz + 8), tag="limb", name="calf")
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        for name, (x0, x1), length in (("toe_mid", (-2, 2), 13), ("toe_out", (2, 4), 10), ("toe_in", (-4, -2), 10)):
            a, b = sorted((x + x0 * sx, x + x1 * sx))
            m.box(T, (a, by - 4, bz - length + 2), (b, by, bz + 2), tag="limb", name=name)
            m.box(T, (a, by - 4, bz - length - 1), (b, by - 1, bz - length + 2), tag="claw", name="claw")
        a = x - 3 * sx
        m.box(T, (min(a, a - 2 * sx), by - 1, bz + 2), (max(a, a - 2 * sx), by + 2, bz + 5), tag="claw", name="hallux")
    m.sym(leg)

    # --- tail: heavy base (caudofemoralis), tapering, scutes along the top
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, tpts, "+z", tsecs, overlap=(2.0, 2.0))
    t1y, t1z = tail["segments"][0]["unposed"]
    m.box("tail1", (-13, t1y - 14, t1z - 2), (13, t1y - 4, t1z + 14), name="caudofemoralis")
    ty, tz = tail["end"]
    m.box("tail4", (-2, ty - 2, tz), (2, ty + 2, tz + 6), name="tail_tip")
    for seg, (w, _h) in zip(tail["segments"][:3], tsecs[:3]):
        sy, sz = seg["unposed"]
        for o in (4, 10, 16):
            if o + 2 < seg["len"]:
                m.box(seg["bone"], (-1, sy + w / 2, sz + o), (1, sy + w / 2 + 1, sz + o + 3), tag="scute", name="scute")

    add_saddle(m, "body", 74, -12, 8, 16, 14, flap=12)
    large_theropod.animations(m, SIT)
    # the shared set is authored at the 1x rig: scale its position keys (body bob, roar lift) to this resolution
    for a in m.animations:
        if a["name"].split(".")[-1] in ("idle", "walk", "run", "attack", "roar", "beg", "eat", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    # resting: the legs fold out to the sides of the belly (not into it), then the body goes back onto the ground
    sit = next(a for a in m.animations if a["name"].endswith(".sit"))
    for side, s in (("l", 1), ("r", -1)):
        for bone in ("thigh", "shin"):
            tr = sit["bones"][f"{bone}_{side}"]
            tr["rotation"] = [[k[0], k[1], k[2], k[3] + s * SIT_SPLAY[0 if bone == "thigh" else 1]] for k in tr["rotation"]]
    low = lowest_point(m, sit["bones"])
    for bone, tr in sit["bones"].items():
        if "position" in tr and (bone == "body" or bone.startswith("thigh")):
            tr["position"] = [[k[0], k[1], round(k[2] - low, 3), k[3]] for k in tr["position"]]
    return m
