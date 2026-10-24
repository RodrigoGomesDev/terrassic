"""
Brachiosaurus altithorax  (Kimmeridgian-Tithonian, Morrison Formation, western North America)

Reference:
  - Size (Riggs 1903, FMNH P 25107; Taylor 2009; SV-POW 2014): ~20-22 m long, ~12-13 m tall with the neck raised,
    ~6 m at the shoulders, 30-50 t. The trunk is long (longer than in the African Giraffatitan) and the tail short
    for a sauropod (~6 m).
  - Posture: front legs longer than the hind legs (long metacarpals), so the back slopes down from high withers to
    the hips; the neck (~9 m, 13 vertebrae) rises steeply from the shoulders (Taylor, Wedel & Naish 2009).
  - Head (USNM 5730, D'Emic & Carrano 2020): small (~0.8 m), with a broad muzzle, spatulate (chisel) teeth at the
    front of the jaws, big nasal openings and an arched bony crest over them in front of the eyes.
  - Limbs: column legs; the hand is a tall U-shaped column of metacarpals with only a thumb claw; the hind foot is
    a wide padded foot with three claws on the inner toes.
  - Skin: none known for brachiosaurids; here polygonal tubercles like other sauropods (Diplodocus, titanosaur
    embryos), darker across the back, a pale throat.

v2x (2026-10-24, remaster at the T. rex v3 level): modelled at 16 px = 1 m (one texture pixel = one vanilla
pixel in game). The head is ~1.3x the real proportion (it is tiny next to the body). render_scale 0.5 =
authoring scale; the in-game size comes from SIZES in tools/javagen/gen_species.py (MODEL_SCALE ~1.0).
Males have a red nasal crest.
"""
import math
from rig import Model, track, keys, wave, add_saddle
from quadruped import quad_anims
from groundfit import fit_to_ground

ID = "brachiosaurus"
K = 2.0          # position keys of the 1x animation set are scaled by this
HEAD = 1.3


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
    """Polygonal tubercles (bigger on the back and flanks), faint giraffe-like patches over the back, vertical skin
    folds on the neck, wrinkled column legs."""
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag, bone = cube.tag, cube.bone
    if tag in ("claw", "eye", "mouth", "tooth_cube", "saddle"):
        return rgb
    if tag == "crest":
        return rgb * (0.88 if (tx.i + tx.j) % 4 == 0 else 1.0)
    if tag in ("skin", "limb"):
        if tag == "skin" and region in ("dorsal", "flank") and bone in ("body", "tail1", "neck1", "neck2"):
            edge, h = _cell(P, 9.0)
            if h % 3 == 0 and edge > 0.12:
                rgb = rgb * 0.88                                              # patches
        if bone.startswith("neck") and region != "dorsal" and int(math.floor(P[2] + P[1] * 0.6)) % 5 == 0:
            rgb = rgb * 0.92                                                  # neck folds
        if tag == "limb" and tx.face in ("north", "south", "east", "west") and int(math.floor(P[1])) % 4 == 0:
            rgb = rgb * 0.9                                                   # wrinkles on the legs
        size = 3.0 if region in ("dorsal", "flank") and bone == "body" else 2.0
        edge, h = _cell(P, size)
        if edge < 0.12:
            rgb = rgb * 0.94
        elif h % 13 == 0:
            rgb = rgb * 1.08
    return rgb


PALETTE = {"dorsal": "#585f5e", "flank": "#7c8580", "belly": "#c9c3a8", "limb": "#5f6764", "limb_top": "#6e7773",
           "claw": "#36322c", "claw_base": "#36322c", "crest": "#b0483a", "tooth_cube_base": "#d6cfb6",
           "tooth_cube_tip": "#efe9d8", "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
           "eye": "#a8822c", "pupil": "#140f0a"}
SEXES = {"male": {"crest": "#b8442f"},
         "female": {"crest": "#7c766a", "dorsal": "#5f5f57", "flank": "#82867c"}}
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}

BODY = (58, 26)                     # hip joint
TORSO = [("chest", (-22, 52, -72, 22, 100, -30)), ("withers", (-16, 100, -68, 16, 104, -36)),
         ("belly", (-24, 48, -32, 24, 92, 4)), ("back", (-14, 92, -34, 14, 96, -6)),
         ("hips", (-20, 50, -2, 20, 78, 48)), ("sacrum", (-12, 78, -4, 12, 82, 26)),
         ("belly_low", (-18, 45, -50, 18, 48, -2)),
         ("ribs_l", (24, 56, -28, 25, 86, 0)), ("ribs_r", (-25, 56, -28, -24, 86, 0)),
         ("scapula_l", (22, 66, -70, 23, 96, -50)), ("scapula_r", (-23, 66, -70, -22, 96, -50))]
NECK = ([(92, -64), (112, -86), (134, -104), (156, -118), (176, -130), (192, -140), (204, -148)],
        [(26, 28), (22, 24), (18, 20), (15, 16), (13, 13), (11, 11)])
TAIL = ([(70, 48), (64, 78), (56, 106), (48, 132), (42, 156)], [(24, 24), (17, 18), (11, 12), (6, 7)])
FRONT_X, FRONT = 16, ([(72, -52), (40, -47), (15, -50)], [(16, 18), (14, 15, 0, "limb")])
HIND_X, HIND = 16, ([(58, 26), (28, 22), (9, 28), (4, 26)], [(20, 26, -1), (16, 17, 0, "limb"), (14, 12, 0, "limb")])
SADDLE = (104, -62, -40, 24, 24, 16)


def build():
    m = Model(ID, render_scale=0.5)
    m.palette = dict(PALETTE)
    m.sexes = SEXES
    m.pattern = pattern
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, *BODY))
    for name, (x0, y0, z0, x1, y1, z1) in TORSO:
        m.box("body", (x0, y0, z0), (x1, y1, z1), name=name)

    # --- neck: six segments rising steeply from the withers, a dewlap fold under the base
    pts, secs = NECK
    names = [f"neck{i + 1}" for i in range(len(secs))]
    neck = m.chain(names, "body", 0, pts, "-z", secs, overlap=(4.0, 2.0))
    y1, z1 = neck["segments"][0]["unposed"]
    m.box("neck1", (-9, y1 - 18, z1 - 20), (9, y1 - 13, z1 + 2), name="dewlap")
    for seg, (w, hh) in zip(neck["segments"][:4], secs[:4]):
        sy, sz = seg["unposed"]
        m.box(seg["bone"], (-2, sy + hh / 2, sz - int(round(seg["len"])) + 4), (2, sy + hh / 2 + 1, sz + 2), name="neck_ridge")

    ay, az = neck["end"]
    h = lambda v: int(round(v * HEAD))
    m.bone("head", names[-1], (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-16 - neck["abs"], 0, 0))
    m.bone("jaw", "skull", (0, ay + h(-4), az + h(0)))

    def at(x, y, z):
        return (h(x), ay + h(y), az + h(z))

    def B(bone, name, box, tag="skin", **kw):
        x0, y0, z0, x1, y1, z1 = box
        return m.box(bone, at(x0, y0, z0), at(x1, y1, z1), tag=tag, name=name, **kw)

    # --- head: braincase, the arched nasal crest over the nostrils, a broad muzzle with chisel teeth
    B("skull", "cranium", (-5, -4, -7, 5, 5, 2), paint=MOUTH_DOWN)
    B("skull", "orbits", (-6, -2, -9, 6, 5, -4))
    B("skull", "nasal_arch", (-3, 5, -11, 3, 8, -4))
    B("skull", "arch_top", (-2, 8, -10, 2, 10, -5), tag="crest")
    B("skull", "snout", (-5, -4, -16, 5, 4, -9), paint=MOUTH_DOWN)
    B("skull", "muzzle", (-5, -4, -20, 5, 2, -16), paint=MOUTH_DOWN)
    for k, x in enumerate((-4, -2, 0, 2)):                                  # spatulate teeth across the muzzle
        a = h(x)
        m.box("skull", (a, ay + h(-4) - 2, az + h(-20)), (a + 2, ay + h(-4), az + h(-20) + 1), tag="tooth_cube",
              name="tooth", paint={"axis": "-y"})
    B("jaw", "jaw", (-4, -7, -19, 4, -4, -4), paint=MOUTH_UP)
    B("jaw", "jaw_back", (-5, -7, -4, 5, -4, 2), paint=MOUTH_UP)
    m.decals += [{"kind": "eye", "bones": ["skull"], "pos": at(6, 2, -6), "r": 1.3, "side": 1},
                 {"kind": "eye", "bones": ["skull"], "pos": at(-6, 2, -6), "r": 1.3, "side": -1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(3, 7, -8), "r": 1.2, "rx": 1.5, "mul": 0.45, "side": 1},
                 {"kind": "spot", "bones": ["skull"], "pos": at(-3, 7, -8), "r": 1.2, "rx": 1.5, "mul": 0.45, "side": -1}]

    # --- front legs: long, the hand a tall column of metacarpals with one thumb claw
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
        m.box(H, (x - 7, by - 13, bz - 7), (x + 7, by + 1, bz + 6), tag="limb", name="metacarpus")
        m.box(H, (x - 8, by - 15, bz - 8), (x + 8, by - 13, bz + 7), tag="limb", name="hand_pad")
        a = x - 6 * sx                                                        # thumb claw on the inner side
        m.box(H, (min(a, a - 2 * sx), by - 14, bz - 10), (max(a, a - 2 * sx), by - 11, bz - 6), tag="claw",
              name="thumb_claw", paint={"axis": "-z"})
    m.sym(front)

    # --- hind legs: pillars, a wide padded foot with three claws
    hpts, hsecs = HIND

    def hind(side, sx):
        x = HIND_X * sx
        ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x, hpts, "-y", hsecs, overlap=(3.0, 2.0))
        by, bz = ch["end"]
        m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
        T = f"toes_{side}"
        m.box(T, (x - 9, by - 4, bz - 9), (x + 9, by, bz + 8), tag="limb", name="foot_pad")
        for k, dx in enumerate((-7, -4, -1)):                                   # claws on digits I-III (inner side)
            a = x + dx * sx
            m.box(T, (min(a, a + 2 * sx), by - 4, bz - 11), (max(a, a + 2 * sx), by - 1, bz - 8), tag="claw",
                  name="claw", paint={"axis": "-z"})
    m.sym(hind)

    # --- tail: short for a sauropod, held off the ground, tapering
    tpts, tsecs = TAIL
    tail = m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, tpts, "+z", tsecs, overlap=(3.0, 2.0))
    ty, tz = tail["end"]
    m.box("tail4", (-2, ty - 2, tz), (2, ty + 2, tz + 6), name="tail_tip")

    add_saddle(m, "body", *SADDLE[:5], flap=SADDLE[5])
    quad_anims(m, 4, nneck=len(secs), walk=(2.4, 14, 14, 0.6 * K), run=(1.4, 20, 20, 1.0 * K), attack="stomp",
               sit_drop=28, graze_neck=-8, graze_skull=-14, sit_kw={"neck": -6})
    for a in m.animations:     # attack / eat / beg / tame come from the 1x set: scale their position keys
        if a["name"].split(".")[-1] in ("attack", "eat", "beg", "tame", "idle"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    fit_to_ground(m, "eat", ("neck1", "neck2", "skull", "body"))
    # rearing stomp: the long tail swings up against the body so it does not dig into the ground
    atk = next(a for a in m.animations if a["name"].endswith(".attack"))
    atk["bones"]["tail1"] = track(rot=keys([(0, 0, 0, 0), (0.45, -18, 0, 0), (0.7, 2, 0, 0), (1.2, 0, 0, 0)]))
    atk["bones"]["body"] = track(rot=keys([(0, 0, 0, 0), (0.45, 16, 0, 0), (0.7, 0, 0, 0), (1.2, 0, 0, 0)]),
                                 pos=keys([(0, 0, 0, 0), (0.45, 0, 2 * K, 2 * K), (0.7, 0, 0, 0), (1.2, 0, 0, 0)]))
    return m
