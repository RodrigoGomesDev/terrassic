"""
Archelon ischyros  (Late Cretaceous, Campanian; Pierre Shale, South Dakota)

Reference (Wikipedia; Wieland 1896, 1902; Yale Peabody YPM 3000): the biggest turtle that ever lived, 4.6 m long and
4 m from flipper tip to flipper tip, over 2 t. The shell was not a solid dome but a leathery carapace stretched over
a frame of widened ribs, with a knobbly ridge down the spine; the head ends in a strong hooked beak (a parrot-like
bite for squid and shellfish); the front flippers are enormous wings, the hind ones small rudders, and the tail is
longer than a sea turtle's. Came ashore to lay eggs.

Built on the turtle archetype. Modelled ~62 px long; SIZES scales it to 4.6 m. Olive-brown carapace over grey-green
skin; males greener with a darker shell, females browner.
"""
import math
from rig import track, keys
import turtle

ID = "archelon"
BODY_Y = 7


def body_parts(m):
    # carapace: a low stepped dome of leathery skin over the rib frame (a wide thin base where the widened ribs
    # end, the dome above it, a knobbly keel and two rib ridges down the back); flat plastron underneath
    m.box("body", (-9, 1, -10), (9, 3, 10), name="plastron", tag="plastron")
    m.box("body", (-13, 3, -11), (13, 7, 11), name="rim", tag="shell")
    m.box("body", (-11, 7, -12), (11, 10, 12), name="carapace", tag="shell")
    m.box("body", (-8, 10, -10), (8, 12, 10), name="dome", tag="shell")
    m.box("body", (-2, 12, -9), (2, 14, 8), name="keel", tag="shell")
    m.box("body", (-7, 12, -9), (-5, 13, 8), name="rib_l", tag="shell")
    m.box("body", (5, 12, -9), (7, 13, 8), name="rib_r", tag="shell")


def head(m, ay, az, abs_pitch):
    m.bone("skull", "head", (0, ay, az), (-abs_pitch, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # big blunt head, the upper beak narrowing to a down-turned hook
    m.box("skull", *R(-4, -3, -9, 4, 4, 0), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -2, -13, 3, 2, -9), name="beak", tag="beak")
    m.box("skull", *R(-2, -1, -15, 2, 1, -13), name="beak_tip", tag="beak")
    m.box("skull", *R(-1.5, -3, -15, 1.5, -1, -13), name="beak_hook", tag="beak")
    m.bone("jaw", "skull", (0, ay - 3, az - 1))
    m.box("jaw", *R(-3, -5, -13, 3, -3, -1), name="jaw", tag="beak", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4, ay + 1.5, az - 5.5), "r": 1.1, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4, ay + 1.5, az - 5.5), "r": 1.1, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    name = tx.cube.name
    if tag == "shell":
        col = tx.pal["shell"].copy()
        if name in ("keel", "rib_l", "rib_r"):
            col = tx.pal["shell_ridge"].copy()
            if tx.face == "up" and int(math.floor(P[2] * 0.5)) % 2 == 0:
                col = col * 1.12                                         # knobs along the ridges
        elif tx.face == "up":
            # leathery skin over the ribs: faint bands running across the back
            if int(math.floor(P[0] * 0.35 + 100)) % 2 == 0:
                col = col * 0.93
            if abs(P[2] - 0.5) < 0.6 and name == "carapace":
                col = col * 0.9
        elif tx.face == "down":
            col = tx.pal["plastron"].copy() * 0.9
        else:
            col = tx.pal["shell_side"].copy()
            if name == "rim" and tx.row == 0:
                col = col * 1.1
        if tx.edge:
            col = col * 0.88
        return col
    if tag == "fin":
        col = tx.pal["fin"].copy()
        # big scales on the paddles, a pale leading edge
        if (int(math.floor(P[0] * 0.6)) + int(math.floor(P[2] * 0.6))) % 2 == 0:
            col = col * 1.08
        if tx.face in ("up", "down") and tx.row == 0:
            col = tx.pal["fin_edge"].copy()
        if tx.edge:
            col = col * 0.9
        return col
    if tag == "skin":
        # wrinkled grey-green skin on the neck, tail and head
        if (int(math.floor(P[2] * 0.8)) + int(math.floor(P[1] * 0.8))) % 2 == 0:
            rgb = rgb * 0.94
    return rgb


def attack(m, necks):
    # the neck shoots out of the shell and the beak clamps shut
    m.anim("attack", 0.7, False, {
        "body": track(pos=keys([(0, 0, 0, 0), (0.2, 0, 0, 2), (0.35, 0, 0, -4), (0.7, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.2, 10, 0, 0), (0.35, -8, 0, 0), (0.7, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.2, 6, 0, 0), (0.35, -4, 0, 0), (0.7, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -34, 0, 0), (0.3, -36, 0, 0), (0.36, 0, 0, 0), (0.7, 0, 0, 0)])),
        "flipper_front_l": track(rot=keys([(0, 0, 0, 0), (0.2, 0, 0, 12), (0.35, 0, 0, -10), (0.7, 0, 0, 0)])),
        "flipper_front_r": track(rot=keys([(0, 0, 0, 0), (0.2, 0, 0, -12), (0.35, 0, 0, 10), (0.7, 0, 0, 0)])),
    })


# knocked out: flipped onto its back (root roll ~172), so "up" in the body frame points at the ground: the flippers
# and the head sag towards +y, the jaw hangs open
LIMP = {"neck1": (14, 0, 0), "skull": (6, 0, 0), "jaw": (-14, 0, 0), "tail1": (8, 0, 0), "tail2": (10, 0, 0),
        "flipper_front_l": (0, -10, 45), "flipper_front_r": (0, 10, -45),
        "flipper_back_l": (0, -10, 40), "flipper_back_r": (0, 10, -40)}

SPEC = dict(
    palette={"dorsal": "#66684e", "flank": "#8c8a6a", "belly": "#cfcaa6",
             "shell": "#5e4e36", "shell_ridge": "#3e3224", "shell_side": "#6e5c42", "plastron": "#d8ccaa",
             "limb": "#5c5a44", "limb_top": "#6e6c52",
             "fin": "#5e5c46", "fin_edge": "#9a9676",
             "beak": "#c4b088", "mouth": "#8a4048", "gum": "#5a2a30", "tooth": "#c4b088",
             "eye": "#a08040", "pupil": "#0f0c0a"},
    sexes={"male": {"shell": "#4e4e34", "shell_side": "#5e5e40", "flank": "#7c8a6a", "dorsal": "#566450"},
           "female": {"shell": "#6a5234", "shell_side": "#7a6244", "flank": "#948a6a"}},
    pattern=pattern, body=(BODY_Y, 0), body_parts=body_parts, head=head,
    neck=dict(points=[(7, -12), (7, -19)], sections=[(7, 6)]),
    tail=dict(points=[(5, 12), (4, 20), (3, 27)], sections=[(4, 3), (2, 2)]),
    flippers=[dict(name="flipper_front", pivot=(11, 6, -6), rot=(0, -20, -3),
                   boxes=[(11, 27, 5, 7, -9, -3), (27, 35, 5, 7, -8, -5)]),
              dict(name="flipper_back", pivot=(10, 4, 8), rot=(0, -40, -3),
                   boxes=[(10, 20, 3, 5, 6, 11), (20, 25, 3, 5, 7, 10)])],
    swim=dict(idle=(4.0, 8, 3), walk=(2.0, 26, 4), run=(1.2, 34, 5), sit=(5.0, 3, 1, 35)),
    attack=attack,
    ko=dict(roll=172, lift=0.3, shift=0.0, joints=LIMP, neck_down=-10),
)


def build():
    return turtle.build(ID, SPEC)
