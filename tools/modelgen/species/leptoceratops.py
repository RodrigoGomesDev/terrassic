"""
Leptoceratops gracilis  (Late Cretaceous, Maastrichtian; Scollard, Hell Creek and Lance formations, western North America)

Reference (Wikipedia; Brown 1914; Sternberg 1951; Ott 2007; Longrich 2010): a primitive, hornless ceratopsian that
lived alongside Triceratops and T. rex, about 2 m long and 70-200 kg. No horns at all, a short solid frill without
windows, a deep short skull with a big parrot beak and self-sharpening leaf teeth; large eyes. Long hind legs and
short arms with grasping hands: it probably ran on two legs when hurried and walked on four. A long deep tail.
Known from several skeletons found together: small herds in forest and floodplain, the "pigs" of the Hell Creek
undergrowth.

Ceratopsian archetype with its own skull, frill and tail, and a "rear" action (rising on the hind legs to look
over the ferns). Modelled at 2x (~80 px long, render_scale 0.5 for the Blockbench file); SIZES scales it to 2 m.
Forest camouflage: olive dorsal, tan flanks dappled with dark blotches, cream belly; the frill russet with a dark
central patch and a pale rim, brighter on males; females duller with a greyer flank.
"""
import math
from paint import vnoise, hash3
from rig import track, keys
import ceratopsian

ID = "leptoceratops"


def body_parts(m):
    # a slim body for a ceratopsian: deep hips over the long hind legs, a shallow chest between the short arms
    m.box("body", (-5, 12, 3), (5, 23, 13), name="hips")
    m.box("body", (-6, 11, -6), (6, 22, 5), name="belly")
    m.box("body", (-5, 12, -12), (5, 21, -5), name="chest")
    m.box("body", (-4, 22, -4), (4, 24, 11), name="back")


def head(m, R, ay, az):
    # a deep short skull: tall cranium, big orbits, a short face ending in a tall parrot beak
    m.box("skull", *R(-4, -4, -7, 4, 3, 1), name="cranium")
    m.box("skull", *R(-3, -5, -12, 3, 1, -7), name="face")
    m.box("skull", *R(-2, -6, -15, 2, -1, -12), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1, -7, -17, 1, -2, -15), name="beak", tag="beak")
    # the jugals flare a little under the eyes (no horns, no nasal bump)
    for sx in (1, -1):
        x0 = 4 if sx > 0 else -5
        m.box("skull", (x0, ay - 3, az - 8), (x0 + 1, ay - 1, az - 5), name="jugal")
    # the short solid frill: one fan tilted back, a thick pale rim, no windows
    fo = (0, ay + 1, az + 1)
    m.box("skull", (-5, ay + 1, az), (5, ay + 6, az + 2), name="frill", tag="frill", rot=(38, 0, 0), origin=fo)
    m.bone("male_display", "skull", (0, ay, az))
    m.box("male_display", (-3, ay + 6, az), (3, ay + 8, az + 2), name="frill_top", tag="frill", rot=(38, 0, 0), origin=fo)
    m.bone("jaw", "skull", (0, ay - 5, az - 6))
    m.box("jaw", *R(-2.5, -8, -16, 2.5, -5, -7), name="jaw", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-1, -8, -17, 1, -6, -16), name="lower_beak", tag="beak")
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4, ay - 0.5, az - 5.5), "r": 1.3, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4, ay - 0.5, az - 5.5), "r": 1.3, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "frill":
        c = tx.cube
        if P[0] > c.to[0] - 1.01 or P[0] < c.frm[0] + 1.01 or P[1] > c.to[1] - 1.01:
            return tx.pal["frill_edge"].copy()                 # the pale rim
        # one dark patch in the middle of the frill, speckled
        d = ((P[0] / 2.4) ** 2 + ((P[1] - (c.frm[1] + 2.5)) / 1.8) ** 2)
        if d < 1.0:
            n = vnoise(P[0] / 1.5, P[1] / 1.5, 0.0, 77)
            return tx.pal["frill_spot"] * (0.9 + 0.2 * n)
        return rgb
    if tag == "skin":
        n = vnoise(P[0] / 2.5, P[1] / 2.5, P[2] / 2.5, 53)
        rgb = rgb * (0.9 + 0.18 * n)
        if region != "belly" and tx.cube.bone not in ("skull", "jaw"):
            # forest dapples: round dark blotches two to three pixels wide, denser on the back
            cell = (math.floor(P[0] / 3.0), math.floor(P[1] / 3.0), math.floor(P[2] / 3.0))
            h = hash3(*cell, 29)
            thresh = 0.62 if region == "dorsal" else 0.74
            if h > thresh:
                cx = (cell[0] + 0.5) * 3.0 + (hash3(*cell, 31) - 0.5)
                cy = (cell[1] + 0.5) * 3.0 + (hash3(*cell, 37) - 0.5)
                cz = (cell[2] + 0.5) * 3.0 + (hash3(*cell, 41) - 0.5)
                if (P[0] - cx) ** 2 + (P[1] - cy) ** 2 + (P[2] - cz) ** 2 < 1.6:
                    rgb = tx.pal["blotch"] * (0.9 + 0.15 * n)
        if region == "dorsal" and abs(P[0]) < 0.8 and tx.cube.bone not in ("skull", "jaw"):
            rgb = tx.pal["stripe"].copy()                      # a thin dark line down the spine
    return rgb


def rear(m):
    # rising on the hind legs to look over the ferns: the body pitches up, the arms tuck in, the tail props
    m.anim("rear", 2.2, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.4, -34, 0, 0), (1.7, -34, 0, 0), (2.2, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.4, 0, 7, -2), (1.7, 0, 7, -2), (2.2, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.4, 18, 0, 0), (0.9, 18, 20, 0), (1.3, 18, -20, 0), (1.7, 18, 0, 0), (2.2, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.4, 10, 0, 0), (1.7, 10, 0, 0), (2.2, 0, 0, 0)])),
        "upperarm_l": track(rot=keys([(0, 0, 0, 0), (0.4, -30, 0, 0), (1.7, -30, 0, 0), (2.2, 0, 0, 0)])),
        "upperarm_r": track(rot=keys([(0, 0, 0, 0), (0.4, -30, 0, 0), (1.7, -30, 0, 0), (2.2, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.4, 55, 0, 0), (1.7, 55, 0, 0), (2.2, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.4, 55, 0, 0), (1.7, 55, 0, 0), (2.2, 0, 0, 0)])),
        "thigh_l": track(rot=keys([(0, 0, 0, 0), (0.4, 30, 0, 0), (1.7, 30, 0, 0), (2.2, 0, 0, 0)])),
        "thigh_r": track(rot=keys([(0, 0, 0, 0), (0.4, 30, 0, 0), (1.7, 30, 0, 0), (2.2, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.4, 24, 0, 0), (1.7, 24, 0, 0), (2.2, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.4, 10, 0, 0), (1.7, 10, 0, 0), (2.2, 0, 0, 0)])),
    })


SPEC = dict(
    render_scale=0.5,
    palette={"dorsal": "#6e6838", "flank": "#a8945c", "belly": "#e0d6ac", "stripe": "#46421f", "blotch": "#403c1c",
             "limb": "#8c7e4c", "limb_top": "#988a56",
             "claw": "#3a3028", "claw_base": "#3a3028",
             "horn_base": "#7a6848", "horn_tip": "#e8dcc0",
             "beak": "#4e4438", "frill": "#a4683a", "frill_edge": "#e4d4a6", "frill_spot": "#623420",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
             "eye": "#c8a846", "pupil": "#140f0a", "saddle": "#7a4f2e"},
    sexes={"male": {"frill": "#c26a30", "frill_spot": "#52281a", "frill_edge": "#f0dcac", "dorsal": "#62602e"},
           "female": {"frill": "#8e6c4a", "frill_edge": "#d2c49e", "flank": "#a89c74", "frill_spot": "#6a4a34"}},
    pattern=pattern, body=(23, 7), body_parts=body_parts, head=head,
    neck=dict(points=[(19, -11), (19.5, -14), (19, -17)], sections=[(7, 7), (6, 6)], tilt=14),
    # long hind legs for a ceratopsian (it could run on two), short slim arms
    hind=dict(x=4, pts=[(20, 8), (11, 6), (4, 8), (2, 7)], secs=[(4, 8, 0.0), (3, 4, 0.5, "limb"), (3, 3, 0.0, "limb")], pad=(4, 3, 2)),
    front=dict(x=5, pts=[(16, -9), (9, -8), (2, -9.5)], secs=[(3, 5, 0.0), (3, 3, 0.0, "limb")], pad=(3, 2, 2)),
    # a long deep tail, four segments, tapering to a whip
    tail=dict(points=[(20, 13), (19, 22), (17, 31), (14, 40), (11, 47)], sections=[(6, 10), (5, 8), (4, 5), (2, 3)]),
    saddle=(24, -3, 4, 6, 6, 4),
    gait=dict(walk=(1.0, 28, 24, 0.5), run=(0.45, 42, 36, 1.2)),
    sit_drop=8, graze=(-12, -6), ko_lift=0.4,
    extra_anims=rear,
)


def build():
    return ceratopsian.build(ID, SPEC)
