"""
Protoceratops andrewsi  (Late Cretaceous, Campanian; Djadokhta Formation, Mongolia - the Flaming Cliffs)

Reference (Wikipedia; Granger & Gregory 1923; Dodson 1976; Fastovsky et al. 2011): a sheep-sized ceratopsian of
1.8-2.5 m and 60-180 kg, known from dozens of skeletons of every age, nests and the "Fighting Dinosaurs" locked
with a Velociraptor. No true horns, only a bump on the nose and flaring cheek bones; a parrot beak; a broad
frill with two big windows, bigger in the males; very large eye sockets with big sclerotic rings (it may have
been active at dusk and night); a deep tail with tall spines; short front legs. Lived in herds on the dunes and
probably dug, as a fossil in a burrow-like pose suggests. The likely origin of the griffin legend.

Ceratopsian archetype with its own skull and a "dig" action. Modelled at 2x (~78 px long, render_scale 0.5 for
the Blockbench file); SIZES scales it to 2 m. Sand and tan with a dark dorsal stripe and freckles; the frill tawny
with dark windows and a pale rim, red-orange on males, dun on females.
"""
import math
from paint import vnoise, hash3
from rig import track, keys
import ceratopsian

ID = "protoceratops"


def body_parts(m):
    # a chunky little body: deep hips, a round belly, a narrow chest between the short front legs
    m.box("body", (-6, 12, 4), (6, 24, 14), name="hips")
    m.box("body", (-7, 10, -6), (7, 23, 6), name="belly")
    m.box("body", (-6, 10, -13), (6, 21, -5), name="chest")
    m.box("body", (-5, 23, -4), (5, 25, 12), name="back")


def head(m, R, ay, az):
    # a big head for the body: broad cranium, a short deep face, the parrot beak
    m.box("skull", *R(-4.5, -5, -8, 4.5, 3, 1), name="cranium")
    m.box("skull", *R(-3.5, -6, -13, 3.5, 1, -8), name="face")
    m.box("skull", *R(-2.5, -7, -16, 2.5, -1, -13), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, -8, -18, 2, -3, -16), name="beak", tag="beak")
    # the nasal bump (no real horn) and the flaring cheek bones
    m.box("skull", *R(-1, 1, -14, 1, 3, -12), name="nasal_bump", tag="horn", paint={"axis": "+y"})
    for sx in (1, -1):
        x0 = 4.5 if sx > 0 else -5.5
        m.box("skull", (x0, ay - 3, az - 7), (x0 + 1, ay - 1, az - 4), name="cheek_bone", tag="horn",
              paint={"axis": "+x" if sx > 0 else "-x"})
    # the frill: a broad fan tilted back, with a scalloped top; males grow it taller
    fo = (0, ay + 1, az + 1)
    m.box("skull", (-7, ay + 1, az), (7, ay + 9, az + 2), name="frill", tag="frill", rot=(40, 0, 0), origin=fo)
    m.box("skull", (-5, ay + 9, az), (5, ay + 11, az + 2), name="frill_top", tag="frill", rot=(40, 0, 0), origin=fo)
    m.bone("male_display", "skull", (0, ay, az))
    m.box("male_display", (-3, ay + 11, az), (3, ay + 13, az + 2), name="frill_crest", tag="frill", rot=(40, 0, 0), origin=fo)
    m.box("male_display", (-1, ay + 3, az - 14), (1, ay + 4, az - 12), name="nasal_bump_tip", tag="horn", paint={"axis": "+y"})
    m.bone("jaw", "skull", (0, ay - 6, az - 6))
    m.box("jaw", *R(-3, -9, -17, 3, -6, -7), name="jaw", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-1.5, -9, -18, 1.5, -7, -17), name="lower_beak", tag="beak")
    # big night eyes
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4.5, ay - 0.5, az - 5.5), "r": 1.5, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4.5, ay - 0.5, az - 5.5), "r": 1.5, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "frill":
        c = tx.cube
        if c.name != "frill" or P[0] > c.to[0] - 1.01 or P[0] < c.frm[0] + 1.01 or P[1] > c.to[1] - 1.01:
            return tx.pal["frill_edge"].copy()                 # pale rim and scalloped top
        # the two frill windows show as dark ovals under the skin
        win = ((abs(P[0]) - 3.6) / 2.2) ** 2 + ((P[1] - (c.frm[1] + 4.5)) / 2.6) ** 2
        if win < 1.0:
            return tx.pal["frill_window"].copy() if win > 0.45 else tx.pal["frill_window"] * 0.85
        if abs(P[0]) < 0.9:
            return tx.pal["frill_edge"] * 0.92                 # the midline bar between the windows
        return rgb
    if tag == "skin":
        n = vnoise(P[0] / 2.5, P[1] / 2.5, P[2] / 2.5, 41)
        rgb = rgb * (0.9 + 0.18 * n)
        if region == "dorsal" and abs(P[0]) < 1.1 and tx.cube.bone not in ("skull", "jaw"):
            rgb = tx.pal["stripe"].copy()                      # dark stripe down the spine and tail
        if region != "belly" and hash3(math.floor(P[0] / 1.5), math.floor(P[1] / 1.5), math.floor(P[2] / 1.5), 13) > 0.9:
            rgb = tx.pal["stripe"] * 1.3                       # freckles
    return rgb


def dig(m):
    # digging: the head goes down between the forefeet and they scrape the sand back in turns, the tail wagging
    arm_l, arm_r, fore_l, fore_r = [], [], [], []
    for k in range(4):
        t0 = 0.5 + k * 0.4
        arm_l += [(t0, -38, 0, 0), (t0 + 0.2, 22, 0, 0)]
        arm_r += [(t0, 22, 0, 0), (t0 + 0.2, -38, 0, 0)]
        fore_l += [(t0, 30, 0, 0), (t0 + 0.2, 10, 0, 0)]
        fore_r += [(t0, 10, 0, 0), (t0 + 0.2, 30, 0, 0)]
    m.anim("dig", 2.6, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.5, -4, 0, 0), (2.1, -4, 0, 0), (2.6, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.5, 0, -0.5, 0), (2.1, 0, -0.5, 0), (2.6, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, -7, 0, 0), (2.1, -7, 0, 0), (2.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.5, -2, 0, 0), (0.9, 1, 0, 0), (1.3, -3, 0, 0), (1.7, 1, 0, 0), (2.1, -2, 0, 0), (2.6, 0, 0, 0)])),
        "upperarm_l": track(rot=keys([(0, 0, 0, 0)] + arm_l + [(2.6, 0, 0, 0)])),
        "upperarm_r": track(rot=keys([(0, 0, 0, 0)] + arm_r + [(2.6, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0)] + fore_l + [(2.6, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0)] + fore_r + [(2.6, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.7, 2, 14, 0), (1.1, 2, -14, 0), (1.5, 2, 14, 0), (1.9, 2, -14, 0), (2.6, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.8, 0, 18, 0), (1.2, 0, -18, 0), (1.6, 0, 18, 0), (2.0, 0, -18, 0), (2.6, 0, 0, 0)])),
    })


SPEC = dict(
    render_scale=0.5,
    palette={"dorsal": "#8a6a42", "flank": "#b89a68", "belly": "#e4d8b4", "stripe": "#5a4428",
             "limb": "#9a7e52", "limb_top": "#a68a5c",
             "claw": "#3a3028", "claw_base": "#3a3028",
             "horn_base": "#7a6848", "horn_tip": "#e8dcc0",
             "beak": "#4a4036", "frill": "#a06a3c", "frill_edge": "#e6d4a8", "frill_window": "#6a4a30",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
             "eye": "#c89a40", "pupil": "#140f0a", "saddle": "#7a4f2e"},
    sexes={"male": {"frill": "#b85a30", "frill_window": "#5a3424", "dorsal": "#7a5c38", "frill_edge": "#f0dcb0"},
           "female": {"frill": "#8a6a48", "frill_edge": "#d4c4a0", "flank": "#b8a478", "frill_window": "#6e5a40"}},
    pattern=pattern, body=(22, 8), body_parts=body_parts, head=head,
    neck=dict(points=[(18, -12), (18, -15), (17.5, -18)], sections=[(8, 8), (7, 7)], tilt=12),
    hind=dict(x=5, pts=[(19, 9), (10, 7), (4, 9), (2, 8)], secs=[(5, 8, 0.0), (4, 4, 0.5, "limb"), (3, 3, 0.0, "limb")], pad=(4, 3, 2)),
    front=dict(x=6, pts=[(15, -9), (8, -8), (2, -9.5)], secs=[(4, 5, 0.0), (3, 3, 0.0, "limb")], pad=(4, 2, 2)),
    # a deep tail with tall spines, narrowing to a point
    tail=dict(points=[(19, 14), (18, 22), (16, 30), (13, 38)], sections=[(7, 11), (5, 8), (3, 4)]),
    saddle=(25, -3, 5, 7, 7, 5),
    gait=dict(walk=(1.0, 26, 26, 0.5), run=(0.5, 38, 38, 1.0)),
    sit_drop=8, graze=(-10, -5), ko_lift=0.4,
    extra_anims=dig,
)


def build():
    return ceratopsian.build(ID, SPEC)
