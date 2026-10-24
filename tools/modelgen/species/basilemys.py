"""
Basilemys  (Late Cretaceous, Campanian-Maastrichtian; Dinosaur Park, Judith River, Hell Creek)

Reference (Wikipedia; Hay 1902; Langston 1956; Brinkman 1998; Mallon & Brinkman 2011; Sullivan et al. 2013): a
nanhsiungchelyid, the biggest land turtle of the North American Cretaceous: a carapace of 1-1.3 m, high and
box-like, its whole surface sculptured with a fine pitted and grooved texture, a strong hooked beak with flaring
jaws, short thick limbs with big claws and a short tail. Everything about it says tortoise: it walked the
floodplains and ate plants, and the shell was the armour; it could not swim well.

Land-turtle rig (tortoise.py) modelled at 2x (render_scale 0.5): ~52 px nose to tail, SIZES scales it to 1.6 m.
In game: the slow herbivore of plains and deltas, meat and shell plates (scutes); hides in the shell when hurt.
Dark olive-brown sculptured shell with paler scute seams and a straw rim, grey-brown scaly skin, a yellowish
plastron; males with a darker shell and a redder throat, females browner.
"""
import math
from paint import vnoise
from rig import track, keys
from tortoise import build_tortoise

ID = "basilemys"


def shell(m):
    # a high box-like carapace: plastron, flaring rim, the sculptured dome in two steps and a low keel
    m.box("body", (-11, 3, -19), (11, 5, 19), name="plastron", tag="plastron")
    m.box("body", (-14, 5, -21), (14, 9, 21), name="rim", tag="shell")
    m.box("body", (-12, 9, -19), (12, 15, 19), name="carapace", tag="shell")
    m.box("body", (-9, 15, -16), (9, 19, 16), name="dome", tag="shell")
    m.box("body", (-3, 19, -14), (3, 21, 13), name="keel", tag="shell")


def head(m, R, ay, az):
    # a thick blunt head with a deep hooked beak and flaring jaws
    m.box("skull", *R(-4, -3, -8, 4, 3, 0), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -2, -12, 3, 2, -8), name="beak", tag="beak")
    m.box("skull", *R(-2, -3, -13, 2, 0, -12), name="beak_hook", tag="beak")
    m.bone("jaw", "skull", (0, ay - 3, az - 1))
    m.box("jaw", *R(-3.5, -5, -12, 3.5, -3, -1), name="jaw", tag="beak", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4, ay + 1, az - 5), "r": 1.1, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4, ay + 1, az - 5), "r": 1.1, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    name = tx.cube.name
    if tag == "shell":
        col = tx.pal["shell"].copy()
        n = vnoise(P[0] / 1.3, P[1] / 1.3, P[2] / 1.3, 83)
        if name == "rim":
            col = tx.pal["shell_rim"].copy()
        elif name == "keel":
            col = tx.pal["shell_ridge"].copy()
        if tx.face == "up" or name in ("carapace", "dome"):
            # the scutes: a grid of plates with pale seams, each plate pitted and grooved like the fossil
            u = P[0] if tx.face in ("up", "down", "north", "south") else P[2]
            v = P[2] if tx.face in ("up", "down") else P[1]
            cu, cv = u / 6.0 + 100, v / 7.0 + 100
            fu, fv = cu - math.floor(cu), cv - math.floor(cv)
            if min(fu, 1 - fu) < 0.09 or min(fv, 1 - fv) < 0.08:
                col = tx.pal["shell_seam"].copy()
            else:
                col = col * (0.84 + 0.3 * n)                       # the pitted sculpture
                if (int(math.floor(P[0] * 0.9)) + int(math.floor(P[2] * 0.7)) + int(math.floor(P[1] * 0.9))) % 5 == 0:
                    col = col * 0.82                               # the grooves
        elif tx.face == "down":
            col = tx.pal["plastron"].copy() * 0.9
        else:
            col = col * (0.9 + 0.2 * n)
        if tx.edge:
            col = col * 0.9
        return col
    if tag == "plastron":
        n = vnoise(P[0] / 2.0, P[1] / 2.0, P[2] / 2.0, 85)
        col = tx.pal["plastron"] * (0.92 + 0.16 * n)
        if abs(P[0]) < 0.6 or (int(math.floor(P[2] / 6.0 + 100))) % 1 == 0 and abs((P[2] / 6.0 + 100) % 1 - 0.5) > 0.45:
            col = col * 0.88                                       # the plastron seams
        return col
    if tag == "skin":
        n = vnoise(P[0] / 1.6, P[1] / 1.6, P[2] / 1.6, 87)
        rgb = rgb * (0.88 + 0.24 * n)
        if tx.cube.bone in ("neck1", "neck2") and region == "belly":
            rgb = tx.pal["throat"] * (0.92 + 0.16 * n)
        if (int(math.floor(P[0] * 1.1)) + int(math.floor(P[1] * 1.1)) + int(math.floor(P[2] * 1.1))) % 3 == 0:
            rgb = rgb * 0.9                                        # the big scales
    if tag == "limb":
        n = vnoise(P[0] / 1.4, P[1] / 1.4, P[2] / 1.4, 89)
        rgb = rgb * (0.86 + 0.28 * n)
    return rgb


S = {
    "render_scale": 0.5,
    "palette": {
        "dorsal": "#6e6a4e", "flank": "#7e7858", "belly": "#9a9470", "throat": "#b8a070",
        "limb": "#6a6648", "limb_top": "#74704e",
        "claw": "#d8d0b8", "claw_base": "#b8b098", "claw_tip": "#ece8dc",
        "shell": "#4e4a30", "shell_rim": "#9a8c58", "shell_ridge": "#3e3a24", "shell_seam": "#8c8458",
        "plastron": "#c8b878",
        "beak": "#5a5440", "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#3a2a14", "pupil": "#0a0604",
    },
    "sexes": {"male": {"shell": "#443e28", "throat": "#c07848", "shell_rim": "#8e7c4c"},
              "female": {"shell": "#5a5236", "shell_rim": "#a89a66", "flank": "#8a8262"}},
    "body": (12, 0),
    "shell": shell,
    "neck": {"points": [(10, -21), (10.5, -26), (10, -30)], "sections": [(6, 6), (5, 5)], "tilt": 4},
    "head": head,
    "pattern": pattern,
    # short thick legs, elephant-like, with big claws; the body stays low
    "hind": {"x": 10, "pts": [(9, 13), (5.5, 11.5), (3, 12.5), (2, 13)], "secs": [(5, 5, 0.0), (4, 4, 0.0, "limb"), (4, 4, 0.0, "limb")], "pad": (5, 3, 2)},
    "front": {"x": 10, "pts": [(9, -13), (5, -13.5), (2, -13)], "secs": [(5, 5, 0.0), (4, 4, 0.0, "limb")], "pad": (5, 3, 2)},
    "tail": {"points": [(9, 21), (8, 26), (7, 30)], "sections": [(4, 4), (2, 2)]},
    "gait": {"walk": (2.4, 14, 14, 0.2), "run": (1.5, 20, 20, 0.35)},
    "sit_drop": 2,
    "sit": {"hind": (40, -80, 40), "front": (-30, 80, -40), "tail": (2, 1), "neck": -2},
    "hide": {"neck": -22, "skull": 14, "back": 6, "drop": 1},
    "knockout": {"lift": 0.3, "neck_down": -16},
}


def build():
    return build_tortoise(ID, S)
