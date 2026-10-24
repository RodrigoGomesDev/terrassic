"""
Alamosaurus sanjuanensis  (Late Cretaceous, Maastrichtian; New Mexico, Texas, Utah)

Reference (Wikipedia; Gilmore 1922; Fowler & Sullivan 2011; Tykoski & Fiorillo 2017): the last and largest
sauropod of North America, a titanosaur of 26-30 m and 30-80 t (the biggest bones, from Big Bend, rival the
South American giants); a wide-gauge stance on column legs, the shoulders about level with the hips, a long
neck held forward and up, a small head and a long whip tail; a single osteoderm shows some body armour. It
shared the land with the Tyrannosaurus and Quetzalcoatlus.

Sauropod archetype with its own frame: the level back, the five-segment neck, the long whip tail (the attack),
a row of scattered osteoderms and a dark dorsal stripe on the males. Modelled ~150 px long; SIZES scales it to
30 m. Red-brown with big reticulated scales, a sandy belly; males darker with the stripe, females paler.
"""
import math
from paint import vnoise, hash3
from rig import track, keys
import sauropod

ID = "alamosaurus"


def body_parts(m):
    # a level back: deep chest, wide barrel belly, broad titanosaur hips
    m.box("body", (-11, 22, -24), (11, 42, -6), name="chest")
    m.box("body", (-12, 20, -8), (12, 41, 14), name="belly")
    m.box("body", (-11, 22, 12), (11, 40, 27), name="hips")
    m.box("body", (-7, 41, -20), (7, 43, 24), name="back")


def head(m, R, ay, az):
    # a small, low head with a blunt rounded snout and nostrils high up
    m.box("skull", *R(-3, -3, -5, 3, 2, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2.5, -3, -10, 2.5, 0, -5), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1.5, 0, -8, 1.5, 1, -5), name="nasal_bump")
    m.bone("jaw", "skull", (0, ay - 3, az - 2))
    m.box("jaw", *R(-2, -5, -10, 2, -3, -2), name="jaw", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3, ay + 0.5, az - 3.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 0.5, az - 3.0), "r": 1.0, "side": -1},
    ]


def armor(m, neck, tail):
    # scattered oval osteoderms along the back and the base of the tail
    for x, z in ((-4, -14), (4, -8), (-3, 0), (5, 6), (-5, 14), (3, 20)):
        m.box("body", (x - 1, 43, z - 1), (x + 1, 44, z + 1), name="osteoderm", tag="scute")
    seg = tail["segments"][0]
    ty, tz = seg["unposed"]
    for x, z in ((-3, tz + 3), (3, tz + 8)):
        m.box("tail1", (x - 1, ty + 6, z - 1), (x + 1, ty + 7, z + 1), name="osteoderm", tag="scute")
    # the males' dorsal stripe is painted (pattern), not boxed; a low ridge of skin marks the midline
    m.bone("male_display", "body", (0, 42, 0))
    m.box("male_display", (-1, 43, -18), (1, 44, 22), name="ridge", tag="crest")


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "scute":
        return tx.pal["scute"] * (1.1 if tx.face == "up" else 0.9)
    if tag == "crest":
        return tx.pal["stripe"].copy()
    if tag == "skin":
        # big reticulated scales: cells of slightly different shade with darker seams
        cell = hash3(math.floor(P[0] / 2.5), math.floor(P[1] / 2.5), math.floor(P[2] / 2.5), 97)
        rgb = rgb * (0.9 + 0.2 * cell)
        n = vnoise(P[0] / 4.0, P[1] / 4.0, P[2] / 4.0, 101)
        rgb = rgb * (0.92 + 0.16 * n)
        if region == "dorsal" and tx.cube.bone == "body" and abs(P[0]) < 2.0:
            rgb = tx.pal["stripe"].copy()                      # dorsal stripe (the females' is just a paler band)
        if region == "flank" and math.sin(P[2] * 0.35 + P[1] * 0.2) > 0.8:
            rgb = rgb * 0.9                                    # faint dark bars down the flanks
    return rgb


def whip(m, necks, tails):
    # the tail whip: the hips swing, the tail coils and cracks sideways, the wave running out to the tip
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.4, 0, 12, 0), (0.7, 0, -14, 0), (1.3, 0, 0, 0)])),
         "neck1": track(rot=keys([(0, 0, 0, 0), (0.4, 0, -8, 0), (0.7, 0, 8, 0), (1.3, 0, 0, 0)]))}
    for i, b in enumerate(tails):
        d = 0.06 * i
        amp = 16 + 9 * i
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.4 + d, -2, amp, 0), (0.7 + d, -2, -amp * 1.3, 0), (1.0 + d, 0, amp * 0.3, 0), (1.3, 0, 0, 0)]))
    m.anim("attack", 1.3, False, t)


SPEC = dict(
    palette={"dorsal": "#6e4e3a", "flank": "#9a7a5c", "belly": "#d8c8a8", "stripe": "#3e2c20", "scute": "#8a6a4c",
             "limb": "#7a5e48", "limb_top": "#8a6c52",
             "claw": "#3a3630", "claw_base": "#3a3630",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
             "eye": "#a8822c", "pupil": "#140f0a", "saddle": "#7a4f2e"},
    sexes={"male": {"dorsal": "#5e4030", "stripe": "#2e2018", "flank": "#8e6e50"},
           "female": {"dorsal": "#7a5c44", "stripe": "#9a7a5c", "flank": "#a68868", "scute": "#9a7e60"}},
    pattern=pattern, body=(36, 10), body_parts=body_parts, head=head, armor=armor,
    neck=dict(points=[(38, -22), (46, -31), (53, -39), (59, -47), (64, -55), (68, -62)],
              sections=[(11, 11), (9, 9), (8, 8), (7, 7), (6, 6)], tilt=14),
    front=dict(x=9, pts=[(27, -16), (14, -15), (2, -16)], secs=[(8, 9, 0.0), (7, 7, 0.0, "limb")], pad=(8, 3, 2)),
    hind=dict(x=10, pts=[(30, 19), (16, 20), (5, 19), (2, 19)], secs=[(10, 12, 0.0), (8, 8, 0.5, "limb"), (7, 7, 0.0, "limb")], pad=(9, 4, 2)),
    tail=dict(points=[(31, 26), (29, 40), (26, 53), (22, 65), (19, 76), (17, 86)],
              sections=[(12, 12), (9, 9), (6, 6), (4, 4), (2, 2)]),
    saddle=(43, -16, 0, 14, 12, 8),
    gait=dict(walk=(2.6, 13, 13, 0.6), run=(1.5, 19, 19, 1.0)),
    attack=whip,
    sit_drop=14, sit_kw={"neck": -10}, graze=(-10, -12),
    ko=dict(lift=0.3),
)


def build():
    return sauropod.build(ID, SPEC)
