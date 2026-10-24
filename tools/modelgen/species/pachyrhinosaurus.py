"""
Pachyrhinosaurus canadensis  (Late Cretaceous, Campanian-Maastrichtian; Alberta; P. perotorum in the Arctic of Alaska)

Reference (Wikipedia; Sternberg 1950; Currie et al. 2008; Fiorillo & Tykoski 2012): the "thick-nosed lizard", a big
centrosaurine of 6-8 m and ~4 t. No nose horn at all: a flat, rough bony BOSS covers the snout, with a second boss
over the eyes; the frill carries a pair of horns curving up and forward from its top and small hooks along the rim
(P. lakustai adds a spike in the middle). Known from huge bone beds (herds of hundreds) and from the polar Prince
Creek Formation, where it lived through months of darkness: a hardy, cold-country animal.

Ceratopsian archetype with its own heavy skull (bosses instead of horns), bigger frame and a "scent" action.
Modelled ~84 px long; SIZES scales it to 8 m. Slate grey with a rust-brown nasal boss, a pale belly and white
spots on the frill; males darker with a bigger, redder boss and an extra crest on the frill, females browner.
"""
import math
from paint import vnoise, hash3
from rig import track, keys
import ceratopsian

ID = "pachyrhinosaurus"


def body_parts(m):
    # the heaviest frame of the family after the Triceratops: a deep barrel, a thick hump over the shoulders
    m.box("body", (-8, 13, 5), (8, 28, 18), name="hips")
    m.box("body", (-9, 10, -8), (9, 27, 8), name="belly")
    m.box("body", (-8, 10, -16), (8, 25, -7), name="chest")
    m.box("body", (-6, 25, -13), (6, 29, -2), name="hump")
    m.box("body", (-7, 27, -4), (7, 29, 15), name="back")


def head(m, R, ay, az):
    m.box("skull", *R(-5, -6, -8, 5, 4, 1), name="cranium")
    m.box("skull", *R(-4, -7, -15, 4, 2, -8), name="face")
    m.box("skull", *R(-3, -7, -19, 3, 0, -15), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, -8, -22, 2, -2, -19), name="beak", tag="beak")
    # the nasal boss: a flat rugose pad over the whole snout, and the brow boss over the eyes
    m.box("skull", *R(-3, 2, -17, 3, 5, -10), name="nasal_boss", tag="boss")
    m.box("skull", *R(-2, 5, -16, 2, 6, -11), name="nasal_boss_top", tag="boss")
    m.box("skull", *R(-4, 4, -9, 4, 6, -4), name="brow_boss", tag="boss")
    m.bone("male_display", "skull", (0, ay, az))
    m.box("male_display", *R(-2, 6, -15, 2, 7, -12), name="boss_crown", tag="boss")
    # the frill, tilted back, with the pair of forward-curving horns at the top and small hooks along the rim
    fo = (0, ay + 2, az + 1)
    m.box("skull", (-10, ay + 2, az), (10, ay + 14, az + 2), name="frill", tag="frill", rot=(34, 0, 0), origin=fo)
    m.box("skull", (-8, ay + 14, az), (8, ay + 16, az + 2), name="frill_top", tag="frill", rot=(34, 0, 0), origin=fo)
    # everything on the frill turns about the same pivot (fo), so it stays glued to the plate
    for sx in (1, -1):
        x = 4 * sx
        m.box("skull", (x - 1, ay + 16, az), (x + 1, ay + 21, az + 2), name="frill_horn", tag="horn",
              rot=(34, 0, 0), origin=fo, paint={"axis": "+y"})
        m.box("skull", (x - 1, ay + 21, az - 2), (x + 1, ay + 23, az + 1), name="frill_horn_tip", tag="horn",
              rot=(34, 0, 0), origin=fo, paint={"axis": "+y"})
        for hy in (ay + 11, ay + 7, ay + 3):
            x0 = 10 if sx > 0 else -12
            m.box("skull", (x0, hy, az), (x0 + 2, hy + 2, az + 2), name="frill_hook", tag="horn",
                  rot=(34, 0, 0), origin=fo, paint={"axis": "+x" if sx > 0 else "-x"})
    # P. lakustai-style middle spike only on the males
    m.box("male_display", (-1, ay + 16, az), (1, ay + 20, az + 2), name="frill_spike", tag="horn",
          rot=(34, 0, 0), origin=fo, paint={"axis": "+y"})
    m.bone("jaw", "skull", (0, ay - 5, az - 7))
    m.box("jaw", *R(-3.5, -9, -20, 3.5, -6, -8), name="jaw", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-2, -9, -22, 2, -7, -20), name="lower_beak", tag="beak")
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (5, ay + 1.0, az - 5.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-5, ay + 1.0, az - 5.0), "r": 1.0, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "boss":
        # rugose bone: a pitted, knobbly surface
        n = vnoise(P[0] / 1.2, P[1] / 1.2, P[2] / 1.2, 53)
        col = tx.pal["boss"] * (0.8 + 0.4 * n)
        if tx.edge:
            col = col * 0.85
        return col
    if tag == "frill":
        c = tx.cube
        if c.name == "frill_top" or P[0] > c.to[0] - 1.01 or P[0] < c.frm[0] + 1.01:
            return tx.pal["frill_edge"].copy()
        # white spots scattered over a dark frill
        if hash3(math.floor(P[0] / 2), math.floor(P[1] / 2), 0, 29) > 0.8:
            return tx.pal["frill_spot"].copy()
        return rgb
    if tag == "skin":
        n = vnoise(P[0] / 3.0, P[1] / 3.0, P[2] / 3.0, 19)
        rgb = rgb * (0.88 + 0.22 * n)
        if region in ("dorsal", "flank") and math.sin(P[2] * 0.45 + P[0] * 0.3) * math.sin(P[1] * 0.5) > 0.5:
            rgb = tx.pal["mottle"].copy()                      # darker mottling
        if hash3(math.floor(P[0] / 3), math.floor(P[1] / 3), math.floor(P[2] / 3), 5) > 0.93 and region != "belly":
            rgb = rgb * 1.15
    return rgb


def scent(m):
    # the musk: head up, a long snort, a shiver down the body and a tail swish
    m.anim("scent", 1.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.4, 16, 0, 0), (1.3, 16, 0, 0), (1.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.4, 8, 0, 0), (0.7, 8, 0, 6), (1.0, 8, 0, -6), (1.3, 8, 0, 0), (1.8, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.4, -8, 0, 0), (0.5, -4, 0, 0), (0.6, -10, 0, 0), (0.7, -4, 0, 0), (0.8, -10, 0, 0), (1.3, 0, 0, 0), (1.8, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.6, 0, 0, 3), (0.8, 0, 0, -3), (1.0, 0, 0, 2), (1.2, 0, 0, 0), (1.8, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.5, 0, 18, 0), (0.9, 0, -18, 0), (1.3, 0, 12, 0), (1.8, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.6, 0, 24, 0), (1.0, 0, -24, 0), (1.4, 0, 14, 0), (1.8, 0, 0, 0)])),
    })


SPEC = dict(
    palette={"dorsal": "#4a4e52", "flank": "#6e7276", "belly": "#c8c4b8", "mottle": "#3a3e42",
             "limb": "#5a5e62", "limb_top": "#66686c",
             "claw": "#2e2c28", "claw_base": "#2e2c28",
             "horn_base": "#5a5048", "horn_tip": "#e8e0d0", "boss": "#8a5a3e",
             "beak": "#3e3a34", "frill": "#3c4044", "frill_edge": "#9a9690", "frill_spot": "#e8e4dc",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
             "eye": "#c0a040", "pupil": "#140f0a", "saddle": "#7a4f2e"},
    sexes={"male": {"boss": "#a04a30", "dorsal": "#3e4246", "frill": "#2e3236", "frill_spot": "#f4f0e8"},
           "female": {"boss": "#8a6a50", "dorsal": "#5a5650", "flank": "#7e7a72", "frill": "#4e4a44", "frill_spot": "#d4d0c4"}},
    pattern=pattern, body=(25, 11), body_parts=body_parts, head=head,
    neck=dict(points=[(22, -14), (22, -18), (21.5, -22)], sections=[(11, 11), (10, 10)], tilt=8),
    hind=dict(x=7, pts=[(22, 12), (12, 10), (4, 12), (2, 11)], secs=[(7, 10, 0.0), (6, 6, 0.5, "limb"), (5, 5, 0.0, "limb")], pad=(6, 4, 2)),
    front=dict(x=8, pts=[(17, -11), (9.5, -9.5), (2, -11.5)], secs=[(6, 7, 0.0), (5, 5, 0.0, "limb")], pad=(6, 3, 2)),
    tail=dict(points=[(23, 17), (21, 26), (18, 33), (15, 40)], sections=[(10, 10), (7, 7), (4, 4)]),
    saddle=(29, -3, 7, 10, 9, 6),
    gait=dict(walk=(1.8, 18, 18, 0.6), run=(0.9, 30, 30, 1.2)),
    sit_drop=9, graze=(-14, -8), ko_lift=0.4,
    extra_anims=scent,
)


def build():
    return ceratopsian.build(ID, SPEC)
