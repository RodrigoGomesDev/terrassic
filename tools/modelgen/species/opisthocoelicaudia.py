"""
Opisthocoelicaudia skarzynskii  (Late Cretaceous, Maastrichtian; Nemegt Formation, Mongolia)

Reference (Wikipedia; Borsuk-Bialynicka 1977; Currie et al. 2018): a small, stocky titanosaur of 11-12 m and ~8-9 t,
known from a nearly complete skeleton that lacked only the neck and head (both probably carried off by scavengers,
whose tooth marks are on the bones). Named for its tail vertebrae, convex behind ("opisthocoelous"), which lock the
tail into a stiff, strong rod: Borsuk-Bialynicka read it as a prop for rearing up on the hind legs, a tripod to
browse the high canopy. A short, wide, deep body on short legs; the neck was probably held low and forward.

Sauropod archetype with its own frame: the low, forward neck of three segments, a short deep barrel, short legs,
and the thick rod-stiff tail. Its "graze" is the tripod: it rears onto the tail and hind legs to pull leaves from the
canopy (the forage flag breaks the leaves). Attack: a hip-swing shove, the tail sweeping the other way, and a
forefoot slam. Modelled ~105 px long; SIZES scales it to 12 m. Sandy ochre of the Gobi with dark dorsal blotches
and tail rings; males darker with a dark neck stripe and a rust throat, females plain sand.
"""
import math
from paint import vnoise, hash3
from rig import track, keys
import sauropod

ID = "opisthocoelicaudia"


def body_parts(m):
    # short, deep and wide: the chest low, the hips massive and high, the back short
    m.box("body", (-9, 15, -20), (9, 33, -3), name="chest")
    m.box("body", (-11, 14, -5), (11, 33, 12), name="belly")
    m.box("body", (-10, 16, 10), (10, 35, 23), name="hips")
    m.box("body", (-6, 33, -17), (6, 35, 11), name="back")
    m.box("body", (-7, 12, -8), (7, 14, 8), name="belly_low")


def head(m, R, ay, az):
    # a short, boxy head carried low: broad muzzle, nostrils high, a deep lower jaw
    m.box("skull", *R(-3, -3, -4, 3, 3, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -3, -10, 3, 1, -4), name="muzzle", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, 1, -7, 2, 2, -4), name="nasal_bump")
    m.bone("jaw", "skull", (0, ay - 3, az - 1))
    m.box("jaw", *R(-2.5, -6, -10, 2.5, -3, -1), name="jaw", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3, ay + 0.5, az - 2.5), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 0.5, az - 2.5), "r": 1.0, "side": -1},
    ]


def armor(m, neck, tail):
    # no armour: the male's display is a crest of skin down the neck and a rust throat
    y0, z0 = SPEC["neck"]["points"][0]
    m.bone("male_display", "neck1", (0, y0, z0))
    m.box("male_display", (-1, y0 + 4, z0 - 16), (1, y0 + 5, z0 - 2), name="neck_crest", tag="crest")
    m.box("male_display", (-3, y0 - 7, z0 - 12), (3, y0 - 5, z0 - 2), name="throat", tag="throat")


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "crest":
        return tx.pal["crest"].copy()
    if tag == "throat":
        n = vnoise(P[0] / 2.0, P[1] / 2.0, P[2] / 2.0, 23)
        return tx.pal["throat"] * (0.9 + 0.2 * n)
    if tag == "skin":
        # fine, even scales; dark dorsal blotches; the tail ringed
        c = hash3(math.floor(P[0] / 1.5), math.floor(P[1] / 1.5), math.floor(P[2] / 1.5), 31)
        rgb = rgb * (0.93 + 0.14 * c)
        n = vnoise(P[0] / 4.5, P[1] / 4.5, P[2] / 4.5, 37)
        if region in ("dorsal", "flank") and n > 0.6:
            rgb = tx.pal["blotch"] * (0.9 + 0.2 * c)
        if tx.cube.bone.startswith("tail") and (math.floor(P[2] / 4) % 2 == 0):
            rgb = rgb * 0.8
        if tx.cube.bone.startswith("neck") and region == "dorsal" and abs(P[0]) < 1.5:
            rgb = tx.pal["stripe"].copy()
    return rgb


def shove(m, necks, tails):
    # the shove: the hips swing left with the shoulder, the tail sweeps right, then the right forefoot slams down
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.3, 2, 14, -4), (0.6, -2, -10, 3), (1.1, 0, 0, 0)]),
                       pos=keys([(0, 0, 0, 0), (0.3, 1.5, 0.5, 0), (0.6, -1, -0.5, -1), (1.1, 0, 0, 0)])),
         "neck1": track(rot=keys([(0, 0, 0, 0), (0.3, 0, -12, 0), (0.6, 4, 8, 0), (1.1, 0, 0, 0)])),
         "skull": track(rot=keys([(0, 0, 0, 0), (0.3, 0, -6, 0), (0.6, 6, 4, 0), (1.1, 0, 0, 0)])),
         "jaw": track(rot=keys([(0, 0, 0, 0), (0.3, -12, 0, 0), (0.7, 0, 0, 0), (1.1, 0, 0, 0)])),
         "upperarm_r": track(rot=keys([(0, 0, 0, 0), (0.3, -35, 0, 0), (0.55, 10, 0, 0), (1.1, 0, 0, 0)])),
         "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.3, 45, 0, 0), (0.55, 0, 0, 0), (1.1, 0, 0, 0)]))}
    for i, b in enumerate(tails):
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.3, 0, -14 - 5 * i, 0), (0.6, 0, 12 + 4 * i, 0), (1.1, 0, 0, 0)]))
    m.anim("attack", 1.1, False, t)


def tripod(m):
    # the tripod browse: the tail plants on the ground, the body rears, the forefeet hang, the neck reaches the canopy
    m.animations = [a for a in m.animations if not a["name"].endswith(".graze")]
    L = 3.6
    jk = [(0, 0, 0, 0), (1.0, 0, 0, 0)]
    for k in range(5):
        t0 = 1.2 + k * 0.3
        jk += [(t0, -12, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(3.0, 0, 0, 0), (L, 0, 0, 0)]
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.9, 34, 0, 0), (2.9, 34, 0, 0), (L, 0, 0, 0)]),
                       pos=keys([(0, 0, 0, 0), (0.9, 0, 4, 2), (2.9, 0, 4, 2), (L, 0, 0, 0)])),
         "neck1": track(rot=keys([(0, 0, 0, 0), (0.9, 14, 0, 0), (2.9, 14, 0, 0), (L, 0, 0, 0)])),
         "neck2": track(rot=keys([(0, 0, 0, 0), (0.9, 10, 0, 0), (2.9, 10, 0, 0), (L, 0, 0, 0)])),
         "neck3": track(rot=keys([(0, 0, 0, 0), (0.9, 8, 0, 0), (2.9, 8, 0, 0), (L, 0, 0, 0)])),
         "skull": track(rot=keys([(0, 0, 0, 0), (0.9, -10, 0, 0), (2.9, -10, 0, 0), (L, 0, 0, 0)])),
         "jaw": track(rot=keys(jk)),
         "tail1": track(rot=keys([(0, 0, 0, 0), (0.9, -34, 0, 0), (2.9, -34, 0, 0), (L, 0, 0, 0)])),
         "tail2": track(rot=keys([(0, 0, 0, 0), (0.9, -22, 0, 0), (2.9, -22, 0, 0), (L, 0, 0, 0)])),
         "tail3": track(rot=keys([(0, 0, 0, 0), (0.9, -8, 0, 0), (2.9, -8, 0, 0), (L, 0, 0, 0)])),
         "tail4": track(rot=keys([(0, 0, 0, 0), (0.9, 6, 0, 0), (2.9, 6, 0, 0), (L, 0, 0, 0)])),
         "tail5": track(rot=keys([(0, 0, 0, 0), (0.9, 10, 0, 0), (2.9, 10, 0, 0), (L, 0, 0, 0)]))}
    for side in ("l", "r"):
        t[f"upperarm_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.9, -50, 0, 0), (2.9, -50, 0, 0), (L, 0, 0, 0)]))
        t[f"forearm_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.9, 55, 0, 0), (2.9, 55, 0, 0), (L, 0, 0, 0)]))
        t[f"thigh_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.9, -20, 0, 0), (2.9, -20, 0, 0), (L, 0, 0, 0)]))
        t[f"shin_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.9, 12, 0, 0), (2.9, 12, 0, 0), (L, 0, 0, 0)]))
    m.anim("graze", L, False, t)


SPEC = dict(
    palette={"dorsal": "#a88a5a", "flank": "#c4a876", "belly": "#e4d8b8", "blotch": "#6e5236", "stripe": "#4e3a28",
             "crest": "#5e4430", "throat": "#9a5c3c",
             "limb": "#b09868", "limb_top": "#baa274",
             "claw": "#3a3630", "claw_base": "#3a3630",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
             "eye": "#8a6a2c", "pupil": "#140f0a", "saddle": "#7a4f2e"},
    sexes={"male": {"dorsal": "#987a4c", "blotch": "#5e4228", "stripe": "#3e2c1c", "throat": "#a4583a"},
           "female": {"dorsal": "#b89a6a", "flank": "#d0b484", "blotch": "#8a6e4c", "stripe": "#a88a5a", "throat": "#c4a876"}},
    pattern=pattern, body=(28, 8), body_parts=body_parts, head=head, armor=armor,
    neck=dict(points=[(29, -19), (31, -28), (33, -37), (34, -45)], sections=[(9, 9), (7, 7), (6, 6)], tilt=4),
    front=dict(x=8, pts=[(21, -14), (12, -13), (2, -14)], secs=[(7, 8, 0.0), (6, 6, 0.0, "limb")], pad=(7, 3, 2)),
    hind=dict(x=9, pts=[(24, 16), (13, 17), (4, 16), (2, 16)], secs=[(9, 10, 0.0), (7, 7, 0.5, "limb"), (6, 6, 0.0, "limb")], pad=(8, 4, 2)),
    tail=dict(points=[(27, 22), (24, 33), (20, 43), (16, 52), (12, 60), (9, 66)], sections=[(10, 10), (8, 8), (6, 6), (4, 4), (3, 3)]),
    saddle=(35, -12, -1, 12, 11, 7),
    gait=dict(walk=(1.9, 16, 16, 0.5), run=(1.0, 24, 24, 0.9)),
    attack=shove,
    sit_drop=10, sit_kw={"neck": -6}, graze=(-14, -10),
    ko=dict(lift=0.5),
    extra_anims=tripod,
)


def build():
    return sauropod.build(ID, SPEC)
