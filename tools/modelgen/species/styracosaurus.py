"""
Styracosaurus albertensis  (Late Cretaceous, Campanian; Dinosaur Park Formation, Alberta)

Reference (Wikipedia; Lambe 1913; Ryan et al. 2007): a centrosaurine of 5-5.5 m and ~2.7 t with one long nose horn
(up to 57 cm), no real brow horns (just low bumps), and a frill crowned with four to six long spikes, the two
longest pointing back and out like the nose horn; a deep parrot beak, a lighter build than the Triceratops, in
bone beds that show it lived in herds.

Ceratopsian archetype with its own skull: the tall nose horn, the spiked frill (males with longer spikes) and the
small brow bumps. Modelled ~62 px long; SIZES scales it to 5.5 m. Sandy brown with a dark saddle, the frill rust
with cream spikes and a pair of eye spots on males, dull on females.
"""
import math
from paint import vnoise, hash3
import ceratopsian

ID = "styracosaurus"


def body_parts(m):
    # lighter than the Triceratops: a rounder barrel, a lower hump
    m.box("body", (-7, 13, 5), (7, 26, 17), name="hips")
    m.box("body", (-8, 10, -7), (8, 25, 7), name="belly")
    m.box("body", (-7, 10, -15), (7, 23, -6), name="chest")
    m.box("body", (-5, 23, -12), (5, 26, -2), name="hump")
    m.box("body", (-6, 25, -4), (6, 27, 14), name="back")


def head(m, R, ay, az):
    m.box("skull", *R(-4.5, -6, -8, 4.5, 3, 1), name="cranium")
    m.box("skull", *R(-3.5, -7, -14, 3.5, 1, -8), name="face")
    m.box("skull", *R(-2.5, -8, -18, 2.5, -1, -14), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, -9, -21, 2, -3, -18), name="beak", tag="beak")
    # the great nose horn: a thick base and a long tapering tip, raked forward
    m.box("skull", *R(-1.5, 0, -17, 1.5, 5, -14), name="nose_horn", tag="horn", rot=(-18, 0, 0),
          origin=(0, ay, az - 15.5), paint={"axis": "+y"})
    m.box("skull", *R(-1, 5, -16.5, 1, 12, -14.5), name="nose_horn_tip", tag="horn", rot=(-18, 0, 0),
          origin=(0, ay, az - 15.5), paint={"axis": "+y"})
    # brow bumps instead of horns
    for sx in (1, -1):
        m.box("skull", (3 * sx - 1, ay + 3, az - 7), (3 * sx + 1, ay + 4, az - 4), name="brow_bump", tag="horn", paint={"axis": "+y"})
    # frill tilted back over the neck, with the ring of spikes along its rim
    fo = (0, ay + 2, az + 1)
    m.box("skull", (-9, ay + 2, az), (9, ay + 13, az + 2), name="frill", tag="frill", rot=(36, 0, 0), origin=fo)
    m.box("skull", (-7, ay + 13, az), (7, ay + 15, az + 2), name="frill_top", tag="frill", rot=(36, 0, 0), origin=fo)
    spikes = [(-5, ay + 15, 8, 0, -20), (5, ay + 15, 8, 0, 20),       # the two big back spikes (x, y, length, rot_x, rot_z)
              (-8, ay + 11, 6, 0, -55), (8, ay + 11, 6, 0, 55),
              (-9, ay + 6, 4, 0, -85), (9, ay + 6, 4, 0, 85)]
    for k, (x, y, L, rx, rz) in enumerate(spikes):
        m.box("skull", (x - 1, y, az, x + 1, y + L, az + 2)[:3], (x + 1, y + L, az + 2), name="frill_spike", tag="horn",
              rot=(36, 0, rz), origin=(x, y, az + 1), paint={"axis": "+y"})
    m.bone("male_display", "skull", (0, ay, az))
    for x, y, L, rx, rz in spikes[:2]:
        m.box("male_display", (x - 0.5, y + L, az + 0.5), (x + 0.5, y + L + 3, az + 1.5), name="spike_tip", tag="horn",
              rot=(36, 0, rz), origin=(x, y, az + 1), paint={"axis": "+y"})
    m.bone("jaw", "skull", (0, ay - 6, az - 6))
    m.box("jaw", *R(-3, -10, -19, 3, -7, -8), name="jaw", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-2, -10, -21, 2, -8, -19), name="lower_beak", tag="beak")
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4.5, ay + 0.5, az - 5.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4.5, ay + 0.5, az - 5.0), "r": 1.0, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "frill":
        c = tx.cube
        if c.name == "frill_top" or P[0] > c.to[0] - 1.01 or P[0] < c.frm[0] + 1.01:
            return tx.pal["frill_edge"].copy()
        # rust field with a cream centre stripe and two eye spots (males)
        if abs(P[0]) < 1.2:
            return tx.pal["frill_edge"] * 0.9
        spot = ((abs(P[0]) - 5.0) ** 2 + (P[1] - (c.frm[1] + 7.0)) ** 2)
        if spot < 4.0:
            return tx.pal["frill_spot"].copy() if spot > 1.2 else rgb * 0.5
        return rgb
    if tag == "skin":
        n = vnoise(P[0] / 3.0, P[1] / 3.0, P[2] / 3.0, 17)
        rgb = rgb * (0.88 + 0.2 * n)
        if region == "dorsal" and math.sin(P[2] * 0.5) * math.sin(P[0] * 0.6) > 0.45:
            rgb = tx.pal["saddle_dark"].copy()                 # dark saddle blotches over the back
        cell = hash3(math.floor(P[0] / 3), math.floor(P[1] / 3), math.floor(P[2] / 3), 7)
        if cell > 0.92 and region != "belly":
            rgb = rgb * 1.16                                   # big feature scales
    return rgb


SPEC = dict(
    palette={"dorsal": "#6e5a3c", "flank": "#a08660", "belly": "#d8c8a0", "saddle_dark": "#4a3c28",
             "limb": "#7a6446", "limb_top": "#8a7454",
             "claw": "#38312a", "claw_base": "#38312a",
             "horn_base": "#6a5838", "horn_tip": "#efe6ca",
             "beak": "#4a4038", "frill": "#9a4e2e", "frill_edge": "#eadcbc", "frill_spot": "#e0b060",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
             "eye": "#b88a2e", "pupil": "#140f0a", "saddle": "#7a4f2e"},
    sexes={"male": {"frill": "#b04a26", "frill_edge": "#f4e6c4", "frill_spot": "#f0c060", "dorsal": "#5e4c32"},
           "female": {"frill": "#7c5a40", "frill_edge": "#cbbd9b", "frill_spot": "#b89a68", "flank": "#a89470"}},
    pattern=pattern, body=(23, 10), body_parts=body_parts, head=head,
    neck=dict(points=[(19, -13), (18.5, -17), (17.5, -20)], sections=[(10, 10), (9, 9)], tilt=16),
    hind=dict(x=6, pts=[(20, 11), (11, 9), (4, 11), (2, 10)], secs=[(6, 9, 0.0), (5, 5, 0.5, "limb"), (4, 4, 0.0, "limb")], pad=(5, 4, 2)),
    front=dict(x=7, pts=[(16, -10), (9, -8.5), (2, -10.5)], secs=[(5, 6, 0.0), (4, 4, 0.0, "limb")], pad=(5, 3, 2)),
    tail=dict(points=[(21, 16), (19, 24), (16.5, 31), (14, 37)], sections=[(9, 9), (6, 6), (3, 3)]),
    saddle=(27, -3, 6, 9, 8, 6),
    gait=dict(walk=(1.6, 20, 20, 0.6), run=(0.8, 32, 32, 1.2)),
    sit_drop=8, graze=(-22, -16), ko_lift=0.4,
)


def build():
    return ceratopsian.build(ID, SPEC)
