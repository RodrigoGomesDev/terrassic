"""
Pachycephalosaurus wyomingensis  (Maastrichtian, Hell Creek and Lance formations, western North America)

Reference:
  - Size (Gilmore 1931; Sullivan 2006; Wikipedia): ~4.5 m long, 370-450 kg; mostly known from skulls, the
    body restored from relatives (Stegoceras, Homalocephale, Prenocephale).
  - Skull (AMNH 1696, ~60 cm long): the roof thickened into a high rounded dome up to ~25 cm of bone; a rim of
    bony knobs around the back and sides of the dome (the squamosal shelf) with short blunt spikes at the rear
    corners; more small knobs on the snout; large eye sockets under a knobby brow; a small horny beak in front of
    small leaf-shaped teeth. Juvenile skulls ("Dracorex", "Stygimoloch") show the spikes shrinking as the dome
    grows (Horner & Goodwin 2009).
  - Body: bipedal with short arms and five small fingers; a very wide pelvis and gut extending back between the
    legs; long hind legs with three forward toes; a thick tail stiffened by a lattice of ossified tendons (the
    caudal "basket").
  - Domes: display, and probably butting contests: healed lesions on many domes (Peterson et al. 2013).

v2x (2026-10-24, remaster at the T. rex v3 level): its own model (no longer the shared small-biped rig), modelled
at 16 px = 1 m (one texture pixel = one vanilla pixel in game). The head is ~1.5x the real proportion (the dome is the species). The
animation set is the small-biped one (same 16 px/m as the old 1.5x model, so no position scaling).
"""
import math
from rig import Model, lowest_point
from groundfit import fit_to_ground
import smalltheropod
from paint import mix

ID = "pachycephalosaurus"
HEAD = 1.5          # the skull is drawn at 1.5x the real proportion (15 px for ~60 cm)


def _cell(P, size):
    a, b, c = P[0] / size, P[1] / size, P[2] / size
    row = math.floor(b)
    a += 0.5 * (row % 2)
    c += 0.5 * (row % 2)
    fa, fb, fc = a - math.floor(a), b - math.floor(b), c - math.floor(c)
    edge = min(fa, 1 - fa, fb, 1 - fb, fc, 1 - fc)
    h = (math.floor(a) * 73856093 ^ row * 19349663 ^ math.floor(c) * 83492791) & 1023
    return edge, h


def pattern(model, tx, rgb, region):
    """Dome: bare bone with growth bands and a darker rim; knobs: pale bone; skin: small tubercles, dark blotches
    over the back and a pale throat; banded tail."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("claw", "eye", "mouth", "beak"):
        return rgb
    if tag == "dome":
        top = model._dome_top
        g = max(0.0, min(1.0, (P[1] - model._dome_base) / max(1.0, top - model._dome_base)))
        col = mix(pal["dome_base"], pal["dome"], g)
        if math.sin(g * 9.0) > 0.7:
            col = col * 0.9                                                   # growth bands
        if (tx.i * 5 + tx.j * 3) % 11 == 0:
            col = col * 0.94                                                  # pitted bone
        return col
    if tag == "knob":
        return rgb * (1.08 if tx.face == "up" else 0.94)
    if tag in ("skin", "limb"):
        if tag == "limb" and cube.bone.startswith("toes") and tx.face != "down":
            return rgb * (0.86 if int(math.floor(P[2])) % 2 == 0 else 1.0)
        if tag == "skin" and region in ("dorsal", "flank") and not cube.bone.startswith(("skull", "jaw")):
            spot = math.sin(P[0] * 0.9 + P[2] * 0.55) * math.sin(P[2] * 0.7 + P[1] * 0.45)
            if spot > 0.5:
                rgb = rgb * 0.78                                              # blotches
            if cube.bone.startswith("tail") and math.sin(P[2] * 2 * math.pi / 6.0) > 0.6:
                rgb = rgb * 0.82                                              # tail bands
        edge, h = _cell(P, 1.2 if region != "belly" else 1.6)
        if edge < 0.14:
            rgb = rgb * 0.92                                                  # tubercles
        elif h % 9 == 0 and region == "flank":
            rgb = rgb * 1.1
    return rgb


PALETTE = {"dorsal": "#634632", "flank": "#94714f", "belly": "#e0cfa8", "limb": "#6a4d38", "limb_top": "#82624a",
           "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#5d574c",
           "dome": "#dccaa0", "dome_base": "#93603e", "knob": "#ece2c6", "beak": "#3e3530",
           "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421", "eye": "#c98a2a", "pupil": "#120d08"}
SEXES = {"male": {"dome": "#ecd29a", "dome_base": "#a8452c", "knob": "#f4ead0"},
         "female": {"dome": "#b3a488", "dome_base": "#7a6a56", "knob": "#cbbfa4", "dorsal": "#64553f"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

HIP = (21, 4)
TORSO = [("hips", (-6, 14, -2, 6, 26, 12)), ("belly", (-7, 13, -12, 7, 25, 3)),
         ("chest", (-5, 15, -18, 5, 24, -11)), ("back", (-4, 25, -14, 4, 27, 10)),
         ("withers", (-3.5, 24, -18, 3.5, 25, -14))]
NECK = ([(21, -16), (23, -20), (25, -26)], [(7, 8), (6, 7)])
HEAD_PITCH = -8
ARM_X, ARM = 4.5, ([(19, -14), (15, -12.5), (12, -14)], [(2, 3), (2, 2)])
LEG_X, LEG = 4.5, ([(21, 4), (12, 0), (5, 2), (1, 2)], [(6, 8, -0.5), (4, 5, 0.5, "limb"), (3, 3, 0.0, "limb")])
SIT_SPLAY = (10, -40)      # resting: thigh and shin roll out (deg)
TAIL = ([(23, 10), (22, 19), (21, 28), (20, 36), (19, 44)], [(10, 10), (7, 7), (5, 5), (3, 3)])


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *HIP))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)

    # --- neck: short, thick, held in a gentle S
    pts, secs = NECK
    neck = m.chain(["neck1", "neck2"], "body", 0, pts, "-z", secs, overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (HEAD_PITCH - neck["abs"], 0, 0))
    m.bone("male_display", "skull", (0, ay, az))
    m.bone("jaw", "skull", (0, ay - 5, az - 3))

    # head boxes are authored straight in px of the head (HEAD x the real skull), relative to the neck end
    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        if "origin" in kw:
            ox, oy, oz = kw["origin"]
            kw["origin"] = (ox, ay + oy, az + oz)
        return m.box(bone, (x0, ay + y0, az + z0), (x1, ay + y1, az + z1), tag=tag, name=name, **kw)

    # --- head: a short deep face, a small beak, big eyes under the front of the dome
    B("skull", "braincase", (-4, -3, -8, 4, 4, 2), paint=MOUTH_DOWN)
    B("skull", "cheeks", (-4, -5, -10, 4, 1, -4), paint=MOUTH_DOWN)
    B("skull", "muzzle", (-3, -5, -13, 3, 1, -10), paint=MOUTH_DOWN)
    B("skull", "snout_tip", (-2, -5, -15, 2, 0, -13), paint=MOUTH_DOWN)
    B("skull", "beak", (-1.5, -5, -16, 1.5, -2, -15), tag="beak")
    B("jaw", "jaw", (-3, -7, -14, 3, -5, -3), paint=MOUTH_UP)
    B("jaw", "predentary", (-1.5, -7, -16, 1.5, -5, -14), tag="beak")
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": (4, ay + 2, az - 6.5), "r": 1.2, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": (-4, ay + 2, az - 6.5), "r": 1.2, "side": -1}]

    # --- the dome: up to 25 cm of bone, a rounded cap from over the eyes back to the shelf
    DOME = [(4.5, 4, 5, -10, 3), (4.5, 5, 7, -10, 3), (4, 7, 8, -9, 2), (3.5, 8, 9, -8, 1), (3, 9, 10, -7, 0),
            (2, 10, 11, -5.5, -1.5)]
    m._dome_base, m._dome_top = ay + 4, ay + 11
    for i, (hw, y0, y1, z0, z1) in enumerate(DOME):
        B("skull", "dome" if i == 0 else f"dome_{i}", (-hw, y0, z0, hw, y1, z1), tag="dome")
    # squamosal shelf behind the dome, ringed by knobs; short blunt spikes at the rear corners
    B("skull", "squamosal_shelf", (-5, 2, 2, 5, 4, 5), tag="knob")
    for x in (-4, -2, 0, 2, 4):
        B("skull", "shelf_knob", (x - 0.5, 4, 3.5, x + 0.5, 5, 4.5), tag="knob")
    for sx in (1, -1):
        B("skull", "rear_spike", (min(4.5 * sx, 5.5 * sx), 2.5, 4, max(4.5 * sx, 5.5 * sx), 3.5, 7), tag="knob",
          rot=(15, 30 * sx, 0), origin=(5 * sx, 3, 4.5))
        for z in (-8, -5.5, -3, -0.5, 2):                                   # knobs along the base of the dome
            B("skull", "side_knob", (min(4.5 * sx, 5.5 * sx), 3.5, z - 0.5, max(4.5 * sx, 5.5 * sx), 4.5, z + 0.5), tag="knob")
        for x, z in ((4, -10.5), (2, -11)):                                  # knobby brow over the eyes
            B("skull", "brow_knob", (min((x - 0.5) * sx, (x + 0.5) * sx), 3.5, z - 0.5, max((x - 0.5) * sx, (x + 0.5) * sx), 4.5, z + 0.5),
              tag="knob")
        B("skull", "cheek_knob", (min(4 * sx, 5 * sx), -3.5, -7, max(4 * sx, 5 * sx), -2.5, -6), tag="knob")
        # males: a crown of longer spikes along the rear of the shelf
        B("male_display", "crown_spike", (min(2 * sx, 3 * sx), 3.5, 4, max(2 * sx, 3 * sx), 4.5, 8), tag="knob",
          rot=(25, 12 * sx, 0), origin=(2.5 * sx, 4, 4.5))
    for x, y, z in ((-1.5, 1, -11), (1.5, 1, -11), (0, 1, -12.5), (-1, 0, -14), (1, 0, -14)):   # nasal knobs
        B("skull", "nasal_knob", (x - 0.5, y, z - 0.5, x + 0.5, y + 1, z + 0.5), tag="knob")

    # --- arms: short, five small fingers
    def arm(side, sx):
        x = ARM_X * sx
        ch = m.chain([f"arm_{side}", f"forearm_{side}"], "body", x, ARM[0], "-y", ARM[1], tag="limb", overlap=(1.0, 0.5))
        ey, ez = ch["end"]
        F = f"forearm_{side}"
        m.box(F, (x - 1, ey - 1, ez - 1), (x + 1, ey + 1, ez + 1), tag="limb", name="hand")
        for k, dx in enumerate((-1, 0, 1)):
            m.box(F, (x + dx - 0.5, ey - 2, ez - 1), (x + dx + 0.5, ey - 1, ez), tag="claw", name="finger")
    m.sym(arm)

    # --- legs: long, three forward toes with blunt claws and a small dewclaw
    def leg(side, sx):
        x = LEG_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, LEG[0], "-y", LEG[1], overlap=(1.5, 1.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 1.5, by - 1, bz - 1), (x + 1.5, by, bz + 2), tag="limb", name="toe_pad")
        for dx, length in ((-2, 3), (-0.5, 4), (1, 3)):
            a, b = sorted((x + dx * sx, x + (dx + 1) * sx))
            m.box(T, (a, by - 1, bz - 1 - length), (b, by, bz - 1), tag="limb", name="toe")
            m.box(T, (a, by - 1, bz - 2 - length), (b, by, bz - 1 - length), tag="claw", name="claw")
        a = x - 1.5 * sx
        m.box(T, (min(a, a - sx), by, bz + 1), (max(a, a - sx), by + 1, bz + 2), tag="claw", name="dewclaw")
    m.sym(leg)

    # --- tail: thick at the base, stiffened by the tendon lattice
    names = [f"tail{i+1}" for i in range(len(TAIL[1]))]
    tail = m.chain(names, "body", 0, TAIL[0], "+z", TAIL[1], overlap=(1.0, 1.0))
    ty, tz = tail["end"]
    m.box(names[-1], (-1, ty - 1, tz), (1, ty + 1, tz + 2), name="tail_tip")

    P = {"tail_secs": TAIL[1], "hip": HIP, "herbivore": True, "pachy": True, "anim_speed": 0.9,
         "sit": {"drop": 11, "neck": -4}}
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
    fit_to_ground(m, "graze", ("neck1", "neck2", "skull", "body"))
    fit_to_ground(m, "attack", ("neck1", "skull", "body"))
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    return m
