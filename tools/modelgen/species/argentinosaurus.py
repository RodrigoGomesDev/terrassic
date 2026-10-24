"""
Argentinosaurus huinculensis  (Late Cretaceous, Cenomanian; Huincul Formation, Neuquén, Argentina)

Reference (Wikipedia; Bonaparte & Coria 1993; Sellers et al. 2013; Paul 2019; Otero et al. 2020): known from a few
vertebrae, ribs and a femur, yet by every estimate among the largest land animals ever: 30-35 m and 65-75 t.
Reconstructed after its better-known cousins (Patagotitan, Futalognkosaurus): a colossal barrel on wide-set column
legs, hips higher and heavier than the shoulders, a long neck held well up, a tiny head, a long thick tail. The
Sellers model walked it at a stately 2 m/s. A heavy-sauropod skin of big rounded tubercles.

Sauropod archetype with its own frame: the deepest body in the mod, the raised hips, a six-segment neck and a
six-segment tail, a loose dewlap under the throat, rows of big tubercles along the flanks (no osteoderms are known).
Attack: a one-footed tread, the left forefoot raised and slammed. Modelled ~180 px long; SIZES scales it to 35 m.
Weathered grey-brown with a greenish cast, pale belly, horizontal wrinkles on neck and legs; males darker with a
near-black throat, females paler and warmer.
"""
import math
from paint import vnoise, hash3
from rig import track, keys
import sauropod

ID = "argentinosaurus"


def body_parts(m):
    # a colossal barrel: deep chest, wider belly, the hips taller and heavier than the shoulders
    m.box("body", (-12, 24, -27), (12, 46, -6), name="chest")
    m.box("body", (-14, 21, -8), (14, 45, 16), name="belly")
    m.box("body", (-13, 25, 14), (13, 48, 31), name="hips")
    m.box("body", (-8, 46, -23), (8, 48, 16), name="back")
    m.box("body", (-6, 48, 15), (6, 50, 29), name="hip_ridge")


def head(m, R, ay, az):
    # a tiny head for the frame: a rounded cranium, a broad short muzzle, nostrils far back
    m.box("skull", *R(-3, -3, -5, 3, 3, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -3, -11, 3, 0, -5), name="muzzle", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, 0, -7, 2, 2, -4), name="nasal_arch")
    m.bone("jaw", "skull", (0, ay - 3, az - 2))
    m.box("jaw", *R(-2.5, -5, -11, 2.5, -3, -2), name="jaw", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3, ay + 0.5, az - 3.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 0.5, az - 3.0), "r": 1.0, "side": -1},
    ]


def armor(m, neck, tail):
    # no osteoderms known: instead a dewlap under the throat and rows of big rounded tubercles along the flanks
    for seg, (w, h) in list(zip(neck["segments"], SPEC["neck"]["sections"]))[:3]:
        y0, zc = seg["unposed"]
        zm = zc - seg["len"] / 2.0
        m.box(seg["bone"], (-2, y0 - h / 2 - 2, zm - 3), (2, y0 - h / 2, zm + 3), name="dewlap", tag="dewlap")
    for z in (-20, -12, -4, 4, 12, 20, 27):
        for sx in (1, -1):
            hw = 14 if -8 <= z <= 16 else (13 if z > 16 else 12)
            x0 = hw if sx > 0 else -hw - 1
            m.box("body", (x0, 33 + (2 if z > 16 else 0), z - 1), (x0 + 1, 35 + (2 if z > 16 else 0), z + 1), name="tubercle", tag="tubercle",
                  paint={"axis": "+x" if sx > 0 else "-x"})
    # the males' throat: a bigger, darker pouch and a crest of tubercles down the neck
    m.bone("male_display", "neck1", (0, *SPEC["neck"]["points"][0]))
    y0, z0 = SPEC["neck"]["points"][0]
    m.box("male_display", (-3, y0 - 9, z0 - 10), (3, y0 - 6, z0 - 2), name="throat_pouch", tag="dewlap")
    m.box("male_display", (-1, y0 + 6, z0 - 10), (1, y0 + 7, z0 - 2), name="neck_crest", tag="tubercle")


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "tubercle":
        return tx.pal["tubercle"] * (1.1 if tx.face in ("up", "east", "west") else 0.85)
    if tag == "dewlap":
        n = vnoise(P[0] / 2.0, P[1] / 1.5, P[2] / 2.0, 83)
        return tx.pal["throat"] * (0.9 + 0.2 * n)
    if tag == "skin":
        # big rounded tubercles: a coarse cell grid of light centres and dark seams
        cx, cy, cz = math.floor(P[0] / 3.0), math.floor(P[1] / 3.0), math.floor(P[2] / 3.0)
        c = hash3(cx, cy, cz, 89)
        fx, fy, fz = P[0] / 3.0 - cx, P[1] / 3.0 - cy, P[2] / 3.0 - cz
        seam = min(fx, 1 - fx, fy, 1 - fy, fz, 1 - fz) < 0.2
        rgb = rgb * (0.9 + 0.2 * c) * (0.82 if seam else 1.0)
        # weathering: slow blotches of a greener cast over the back, and horizontal wrinkles on neck and limbs
        n = vnoise(P[0] / 7.0, P[1] / 7.0, P[2] / 7.0, 91)
        if region in ("dorsal", "flank"):
            rgb = rgb * (1 - 0.35 * n) + tx.pal["moss"] * (0.35 * n)
        if tx.cube.bone.startswith(("neck", "thigh", "shin", "upperarm", "forearm")) and (math.floor(P[1]) % 4 == 0):
            rgb = rgb * 0.86
    return rgb


def tread(m, necks, tails):
    # the tread: the weight shifts right, the left forefoot rises high, hangs, and slams down; the neck recoils
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.5, 3, 0, -5), (0.8, 3, 0, -5), (1.0, -2, 0, 2), (1.6, 0, 0, 0)]),
                       pos=keys([(0, 0, 0, 0), (0.5, 1, 1.5, 0), (0.8, 1, 1.5, 0), (1.0, 0, -1.5, 0), (1.6, 0, 0, 0)])),
         "upperarm_l": track(rot=keys([(0, 0, 0, 0), (0.5, -55, 0, -10), (0.8, -60, 0, -10), (1.0, 8, 0, 0), (1.6, 0, 0, 0)])),
         "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.5, 70, 0, 0), (0.8, 75, 0, 0), (1.0, 0, 0, 0), (1.6, 0, 0, 0)])),
         "upperarm_r": track(rot=keys([(0, 0, 0, 0), (0.5, 4, 0, 6), (0.8, 4, 0, 6), (1.0, 0, 0, 0), (1.6, 0, 0, 0)])),
         "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, -8, 0, 4), (0.8, -8, 0, 4), (1.0, 10, 0, 0), (1.6, 0, 0, 0)])),
         "neck2": track(rot=keys([(0, 0, 0, 0), (0.5, -4, 0, 0), (1.0, 6, 0, 0), (1.6, 0, 0, 0)])),
         "skull": track(rot=keys([(0, 0, 0, 0), (0.5, -6, 0, 0), (1.0, 8, 0, 0), (1.6, 0, 0, 0)])),
         "jaw": track(rot=keys([(0, 0, 0, 0), (0.9, 0, 0, 0), (1.0, -14, 0, 0), (1.3, 0, 0, 0), (1.6, 0, 0, 0)]))}
    for i, b in enumerate(tails):
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.5, -2, 4 + i, 0), (1.0, 3, -3 - i, 0), (1.6, 0, 0, 0)]))
    m.anim("attack", 1.6, False, t)


SPEC = dict(
    palette={"dorsal": "#5a5248", "flank": "#7e7260", "belly": "#c8bca4", "moss": "#5e6a48",
             "tubercle": "#9a8e78", "throat": "#6a5648",
             "limb": "#66604e", "limb_top": "#726a58",
             "claw": "#3a3630", "claw_base": "#3a3630",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
             "eye": "#a08a40", "pupil": "#140f0a", "saddle": "#7a4f2e"},
    sexes={"male": {"dorsal": "#4a4238", "flank": "#6e6250", "throat": "#2e2420", "moss": "#4e5a3c", "tubercle": "#8a7e68"},
           "female": {"dorsal": "#7a6e5c", "flank": "#968872", "belly": "#d8ccb4", "throat": "#8a7060", "moss": "#7a8260"}},
    pattern=pattern, body=(40, 10), body_parts=body_parts, head=head, armor=armor,
    neck=dict(points=[(42, -25), (50, -34), (57, -42), (63, -50), (68, -58), (72, -65), (75, -72)],
              sections=[(12, 12), (10, 10), (9, 9), (8, 8), (7, 7), (6, 6)], tilt=16),
    front=dict(x=10, pts=[(30, -19), (16, -18), (2, -19)], secs=[(9, 10, 0.0), (8, 8, 0.0, "limb")], pad=(9, 3, 2)),
    hind=dict(x=12, pts=[(34, 23), (18, 24), (5, 23), (2, 23)], secs=[(11, 13, 0.0), (9, 9, 0.5, "limb"), (8, 8, 0.0, "limb")], pad=(10, 4, 2)),
    tail=dict(points=[(34, 30), (32, 44), (29, 57), (25, 69), (22, 80), (19, 90), (17, 98)],
              sections=[(13, 13), (10, 10), (8, 8), (6, 6), (4, 4), (2, 2)]),
    saddle=(48, -18, 0, 15, 13, 9),
    gait=dict(walk=(3.0, 12, 12, 0.6), run=(1.8, 17, 17, 0.9)),
    attack=tread,
    sit_drop=16, sit_kw={"neck": -10}, graze=(-12, -12),
    ko=dict(lift=0.3),
)


def build():
    return sauropod.build(ID, SPEC)
