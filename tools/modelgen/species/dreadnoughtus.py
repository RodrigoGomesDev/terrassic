"""
Dreadnoughtus schrani  (Late Cretaceous, Campanian-Maastrichtian; Cerro Fortaleza Formation, Santa Cruz, Argentina)

Reference (Wikipedia; Lacovara et al. 2014; Bates et al. 2015; Paul 2019): the most complete giant titanosaur known
(~70 % of the skeleton), 26 m long and 26-59 t by the estimates, still growing when it died. "Fears nothing":
a neck of 11 m, more than a third of the animal, carried high; a huge 1.7 m shoulder blade over a deep chest; a
tail of ~9 m, shorter than the neck; column legs under a wide-gauge body. Skin unknown.

Sauropod archetype with its own frame: the very long neck (seven segments, rising steeply), the shoulder hump of
the great scapula, the shortish five-segment tail. Attack: the boom, the whole neck swinging sideways like a crane
and the head knocking. Extra "call": the neck rises straight up and it bellows (call flag: the bellow answers
being hurt). Modelled ~150 px long; SIZES scales it to 26 m. Slate blue-grey with broken pale bars down the
neck and flanks and a cream belly; males darker with a white throat, females lighter and greyer.
"""
import math
from paint import vnoise, hash3
from rig import track, keys
import sauropod

ID = "dreadnoughtus"


def body_parts(m):
    # a deep chest under the great shoulder blades, a long belly, hips a little lower than the withers
    m.box("body", (-11, 24, -26), (11, 46, -8), name="chest")
    m.box("body", (-12, 22, -10), (12, 44, 14), name="belly")
    m.box("body", (-11, 24, 12), (11, 43, 26), name="hips")
    m.box("body", (-7, 44, -22), (7, 46, 14), name="back")
    m.box("body", (-8, 46, -27), (8, 49, -12), name="withers")       # the scapular hump


def head(m, R, ay, az):
    # a small, long-snouted head on the end of the boom
    m.box("skull", *R(-3, -3, -5, 3, 2, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, -3, -11, 2, 0, -5), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1, 0, -7, 1, 1, -4), name="nasal_arch")
    m.bone("jaw", "skull", (0, ay - 3, az - 2))
    m.box("jaw", *R(-2, -5, -11, 2, -3, -2), name="jaw", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3, ay + 0.5, az - 3.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 0.5, az - 3.0), "r": 1.0, "side": -1},
    ]


def armor(m, neck, tail):
    # no armour known: the male's throat is a white dewlap along the first two neck segments
    for seg, (w, h) in list(zip(neck["segments"], SPEC["neck"]["sections"]))[:2]:
        y0, zc = seg["unposed"]
        zm = zc - seg["len"] / 2.0
        m.bone("male_display" if seg["bone"] == "neck1" else "male_display2", seg["bone"], (0, y0, zc))
        m.box("male_display" if seg["bone"] == "neck1" else "male_display2",
              (-2, y0 - h / 2 - 2, zm - 3), (2, y0 - h / 2, zm + 3), name="throat", tag="throat")


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "throat":
        return tx.pal["throat"] * (0.95 + 0.1 * vnoise(P[0], P[1], P[2], 11))
    if tag == "skin":
        c = hash3(math.floor(P[0] / 2), math.floor(P[1] / 2), math.floor(P[2] / 2), 57)
        rgb = rgb * (0.92 + 0.16 * c)
        # broken pale bars: along the neck they run across (by z), on the body down the flanks (by z too)
        bone = tx.cube.bone
        if region in ("dorsal", "flank") and bone != "body" or region == "flank":
            bar = math.sin(P[2] * 0.9 + 0.6 * math.sin(P[1] * 0.7)) > 0.72
            broken = vnoise(P[0] / 3.0, P[1] / 3.0, P[2] / 3.0, 59) > 0.38
            if bar and broken:
                rgb = tx.pal["bar"] * (0.95 + 0.1 * c)
        if region == "dorsal" and bone == "body" and abs(P[0]) < 1.5:
            rgb = rgb * 0.8
    return rgb


def boom(m, necks, tails):
    # the boom: the neck swings far to the left, then whips right across the front, the head knocking at the end
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.4, 0, 8, 0), (0.8, 0, -10, 0), (1.4, 0, 0, 0)]))}
    for i, b in enumerate(necks):
        d = 0.04 * i
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.4 + d, 0, 12, 0), (0.8 + d, 0, -16, 0), (1.1 + d, 0, 3, 0), (1.4, 0, 0, 0)]))
    t["skull"] = track(rot=keys([(0, 0, 0, 0), (0.4, 0, 10, 0), (0.85, -8, -14, 0), (1.4, 0, 0, 0)]))
    t["jaw"] = track(rot=keys([(0, 0, 0, 0), (0.7, 0, 0, 0), (0.85, -16, 0, 0), (1.1, 0, 0, 0), (1.4, 0, 0, 0)]))
    for i, b in enumerate(tails):
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.4, 0, -6 - 2 * i, 0), (0.8, 0, 8 + 2 * i, 0), (1.4, 0, 0, 0)]))
    m.anim("attack", 1.4, False, t)


def call(m):
    # the bellow: the neck rises straight up, the throat swells, the jaw drops and the sound rolls out
    L = 2.6
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.6, -2, 0, 0), (2.0, -2, 0, 0), (L, 0, 0, 0)]))}
    for i in range(1, 8):
        t[f"neck{i}"] = track(rot=keys([(0, 0, 0, 0), (0.6, 7, 0, 0), (2.0, 7, 0, 0), (L, 0, 0, 0)]))
    t["skull"] = track(rot=keys([(0, 0, 0, 0), (0.6, 10, 0, 0), (2.0, 10, 0, 0), (L, 0, 0, 0)]))
    t["jaw"] = track(rot=keys([(0, 0, 0, 0), (0.6, -4, 0, 0), (0.8, -26, 0, 0), (1.8, -22, 0, 0), (2.1, 0, 0, 0), (L, 0, 0, 0)]))
    t["male_display"] = track(pos=keys([(0, 0, 0, 0), (0.8, 0, -1.5, 0), (1.8, 0, -1.5, 0), (2.1, 0, 0, 0), (L, 0, 0, 0)]))
    t["tail1"] = track(rot=keys([(0, 0, 0, 0), (0.8, 4, 0, 0), (2.0, 4, 0, 0), (L, 0, 0, 0)]))
    m.anim("call", L, False, t)


SPEC = dict(
    palette={"dorsal": "#4e5660", "flank": "#6e7884", "belly": "#d0d0c4", "bar": "#b8c0c4", "throat": "#eef0ea",
             "limb": "#5c646e", "limb_top": "#687078",
             "claw": "#2e2c2a", "claw_base": "#2e2c2a",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
             "eye": "#c0a050", "pupil": "#140f0a", "saddle": "#7a4f2e"},
    sexes={"male": {"dorsal": "#404852", "flank": "#5e6874", "bar": "#c8d0d4"},
           "female": {"dorsal": "#646c74", "flank": "#848c96", "bar": "#aab2b6", "throat": "#9aa2a8"}},
    pattern=pattern, body=(38, 10), body_parts=body_parts, head=head, armor=armor,
    neck=dict(points=[(42, -24), (49, -33), (56, -41), (63, -48), (70, -54), (76, -59), (82, -63), (87, -66)],
              sections=[(11, 11), (10, 10), (9, 9), (8, 8), (7, 7), (6, 6), (5, 5)], tilt=30),
    front=dict(x=9, pts=[(29, -18), (15, -17), (2, -18)], secs=[(8, 9, 0.0), (7, 7, 0.0, "limb")], pad=(8, 3, 2)),
    hind=dict(x=10, pts=[(30, 19), (16, 20), (5, 19), (2, 19)], secs=[(10, 12, 0.0), (8, 8, 0.5, "limb"), (7, 7, 0.0, "limb")], pad=(9, 4, 2)),
    tail=dict(points=[(33, 26), (31, 39), (28, 51), (24, 62), (21, 71), (19, 78)], sections=[(12, 12), (9, 9), (7, 7), (5, 5), (3, 3)]),
    saddle=(46, -14, 2, 14, 12, 8),
    gait=dict(walk=(2.6, 13, 13, 0.6), run=(1.5, 19, 19, 1.0)),
    attack=boom,
    sit_drop=14, sit_kw={"neck": -6}, graze=(-16, -14),
    ko=dict(lift=0.3),
    extra_anims=call,
)


def build():
    return sauropod.build(ID, SPEC)
