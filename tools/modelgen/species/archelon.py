"""
Archelon ischyros  (Late Cretaceous, Campanian; Pierre Shale, South Dakota)

Reference:
  - Size (Wieland 1896, 1902; YPM 3000): the biggest turtle that ever lived, ~4.6 m long and ~4 m from flipper tip to
    flipper tip, over 2 t. A protostegid, related to (but not an ancestor of) the leatherback.
  - Shell: not a solid dome. The carapace was reduced to a frame of widened ribs with big gaps (fontanelles),
    covered in thick leathery skin like a leatherback's; a low teardrop in plan, widest at the shoulders and
    tapering to a point over the tail, with a ridge down the spine. The plastron was a reduced cross of bone.
  - Head: very large (~70-80 cm skull), with a long narrow snout ending in a strongly down-hooked beak, a crushing
    parrot-like bite for squid, ammonites and jellyfish; big eyes set high.
  - Limbs: enormous wing-like front flippers that "flew" under water, small hind flippers used as rudders; a tail
    longer than a modern sea turtle's. Came ashore to lay eggs.
  - Colour unknown; kept from the old model: olive-brown leathery carapace speckled pale (as in leatherbacks) over
    grey-green skin; males greener with a darker shell, females browner.

v2x (2026-10-25, remaster at the T. rex v3 level): modelled at ~16 px = 1 m, the head ~1.3x the real proportion.
Built on the turtle archetype (species/turtle.py) for the flipper stroke and the knockout; the archetype's position
keys are scaled by K.
"""
import math
from rig import track, keys
from groundfit import fit_to_ground
import turtle

ID = "archelon"
K = 1.18                     # 16 px/m now / ~13.6 px/m of the old model
BODY_Y = 8
MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
# the carapace in layers (x half width, y0, y1, z0, z1): a low teardrop dome, widest at the shoulders
SHELL = [(15, 3, 7, -14, -4), (16, 3, 7, -4, 6), (13, 3, 7, 6, 14), (8, 3, 6, 14, 20),
         (13, 7, 10, -15, -3), (14, 7, 10, -3, 7), (11, 7, 10, 7, 14), (6, 7, 9, 14, 19),
         (10, 10, 12, -13, 10), (6, 10, 11, 10, 15), (6, 12, 13, -11, 7)]
RIDGES = [(0.0, 13, 14, -11, 8), (7.5, 12, 13, -11, 6), (11.5, 10, 11, -11, 4)]   # (x centre, y0, y1, z0, z1)


def body_parts(m):
    m.box("body", (-10, 0, -14), (10, 3, 12), name="plastron", tag="plastron")
    for k, (hw, y0, y1, z0, z1) in enumerate(SHELL):
        m.box("body", (-hw, y0, z0), (hw, y1, z1), name="carapace", tag="shell")
    m.box("body", (-7, 9, -17), (7, 11, -15), name="nuchal", tag="shell")      # the front lip over the neck
    for xc, y0, y1, z0, z1 in RIDGES:
        for s in ((1,) if xc == 0 else (1, -1)):
            a = xc * s
            m.box("body", (a - 1 if xc == 0 else min(a - 0.5 * s, a + 0.5 * s), y0, z0),
                  (a + 1 if xc == 0 else max(a - 0.5 * s, a + 0.5 * s), y1, z1), name="ridge", tag="shell")


def head(m, ay, az, abs_pitch):
    m.bone("skull", "head", (0, ay, az), (-abs_pitch, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # big head: a broad cranium with the eyes high, a long narrow snout, the strongly down-hooked beak
    m.box("skull", *R(-4.5, -3, -8, 4.5, 4, 0), name="cranium", paint=MOUTH_DOWN)
    m.box("skull", *R(-3.5, 4, -7, 3.5, 5, -1), name="crown")
    m.box("skull", *R(-3, -3, -13, 3, 3, -8), name="snout", paint=MOUTH_DOWN)
    m.box("skull", *R(-2, -3, -16, 2, 2, -13), name="beak", tag="beak", paint=MOUTH_DOWN)
    m.box("skull", *R(-1, -5, -17, 1, 1, -16), name="beak_hook", tag="beak_tip")
    m.bone("jaw", "skull", (0, ay - 3, az - 1))
    m.box("jaw", *R(-3.5, -5, -8, 3.5, -3, 0), name="jaw_back", paint=MOUTH_UP)
    m.box("jaw", *R(-2.5, -5, -13, 2.5, -3, -8), name="jaw", tag="beak", paint=MOUTH_UP)
    m.box("jaw", *R(-1.5, -5, -16, 1.5, -3, -13), name="jaw_tip", tag="beak", paint=MOUTH_UP)
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4.5, ay + 1.5, az - 5.5), "r": 1.2, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4.5, ay + 1.5, az - 5.5), "r": 1.2, "side": -1},
    ]
    for s in (1, -1):
        m.decals.append({"kind": "spot", "bones": ["skull"], "pos": (0.8 * s, ay + 2, az - 15), "r": 0.5,
                         "mul": 0.45, "face": "up"})                        # nostrils near the beak


def pattern(model, tx, rgb, region):
    P, cube, pal = tx.P, tx.cube, tx.pal
    tag = cube.tag
    if tag in ("eye", "mouth"):
        return rgb
    if tag == "shell":
        if cube.name == "ridge":
            col = pal["shell_ridge"].copy()
            if int(math.floor(P[2] * 0.5)) % 2 == 0:
                col = col * 1.14                                         # knobs along the ridges
            return col
        if tx.face == "down":
            return pal["plastron"] * 0.9
        col = pal["shell"].copy() if tx.face == "up" else pal["shell_side"].copy()
        if tx.face == "up" and int(math.floor(abs(P[0]) * 0.33)) % 2 == 0:
            col = col * 0.94                                             # the rib frame under the skin
        h = (int(math.floor(P[0])) * 73 + int(math.floor(P[2])) * 37 + int(math.floor(P[1])) * 11) % 17
        if h == 0:
            col = pal["speckle"].copy()                                  # pale leatherback speckles
        elif h in (5, 11):
            col = col * 0.9
        if tx.edge:
            col = col * 0.88
        return col
    if tag == "plastron":
        return pal["plastron"] * (0.94 if (int(P[0]) // 3 + int(P[2]) // 3) % 2 else 1.0)
    if tag == "fin":
        col = pal["fin"].copy()
        if (int(math.floor(P[0] * 0.6)) + int(math.floor(P[2] * 0.6))) % 2 == 0:
            col = col * 1.08                                             # big scales on the paddles
        if tx.face in ("up", "down") and P[2] < cube.frm[2] + 1.01:
            col = pal["fin_edge"].copy()                                 # pale leading edge
        if (int(P[0]) * 31 + int(P[2]) * 17) % 13 == 0:
            col = pal["speckle"] * 0.95
        if tx.edge:
            col = col * 0.9
        return col
    if tag in ("beak", "beak_tip"):
        return rgb * (0.92 if int(math.floor(P[2])) % 2 == 0 and tx.face not in ("up", "down") else 1.0)
    if tag == "skin":
        if (int(math.floor(P[2] * 0.8)) + int(math.floor(P[1] * 0.8))) % 2 == 0:
            rgb = rgb * 0.94                                             # wrinkled skin
        if cube.bone == "skull" and (int(P[0]) * 29 + int(P[2]) * 13 + int(P[1]) * 7) % 19 == 0:
            rgb = pal["speckle"] * 0.95                                  # pale spots on the head
    return rgb


def attack(m, necks):
    # the neck shoots out of the shell and the hooked beak clamps shut
    m.anim("attack", 0.7, False, {
        "body": track(pos=keys([(0, 0, 0, 0), (0.2, 0, 0, 2 * K), (0.35, 0, 0, -4 * K), (0.7, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.2, 8, 0, 0), (0.35, -6, 0, 0), (0.7, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.2, 4, 0, 0), (0.35, -3, 0, 0), (0.7, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.2, 6, 0, 0), (0.35, -4, 0, 0), (0.7, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.2, -34, 0, 0), (0.3, -36, 0, 0), (0.36, 0, 0, 0), (0.7, 0, 0, 0)])),
        "flipper_front_l": track(rot=keys([(0, 0, 0, 0), (0.2, 0, 0, 12), (0.35, 0, 0, -10), (0.7, 0, 0, 0)])),
        "flipper_front_r": track(rot=keys([(0, 0, 0, 0), (0.2, 0, 0, -12), (0.35, 0, 0, 10), (0.7, 0, 0, 0)])),
    })


# knocked out: flipped onto its back (root roll ~172), so "up" in the body frame points at the ground: the flippers
# and the head sag towards +y, the jaw hangs open
LIMP = {"neck1": (10, 0, 0), "neck2": (6, 0, 0), "skull": (6, 0, 0), "jaw": (-14, 0, 0), "tail1": (8, 0, 0),
        "tail2": (10, 0, 0),
        "flipper_front_l": (0, -10, 45), "flipper_front_r": (0, 10, -45),
        "flipper_back_l": (0, -10, 40), "flipper_back_r": (0, 10, -40)}

SPEC = dict(
    render_scale=0.5,
    palette={"dorsal": "#66684e", "flank": "#8c8a6a", "belly": "#cfcaa6",
             "shell": "#5e4e36", "shell_ridge": "#3e3224", "shell_side": "#6e5c42", "plastron": "#d8ccaa",
             "speckle": "#b8ae8c", "limb": "#5c5a44", "limb_top": "#6e6c52",
             "fin": "#5e5c46", "fin_edge": "#9a9676",
             "beak": "#c4b088", "beak_tip": "#8a7a5c", "mouth": "#8a4048", "gum": "#5a2a30", "tooth": "#c4b088",
             "eye": "#a08040", "pupil": "#0f0c0a"},
    sexes={"male": {"shell": "#4e4e34", "shell_side": "#5e5e40", "flank": "#7c8a6a", "dorsal": "#566450"},
           "female": {"shell": "#6a5234", "shell_side": "#7a6244", "flank": "#948a6a"}},
    pattern=pattern, body=(BODY_Y, 0), body_parts=body_parts, head=head,
    neck=dict(points=[(8, -15), (8.5, -21), (9, -26)], sections=[(9, 8), (8, 7)]),
    tail=dict(points=[(6, 16), (5, 23), (4, 29)], sections=[(5, 4), (3, 3)]),
    # huge wing-like front flippers tapering to a point, small hind rudders
    flippers=[dict(name="flipper_front", pivot=(13, 6, -9), rot=(0, -20, -3),
                   boxes=[(13, 22, 5, 7, -13, -4), (22, 32, 5.5, 6.5, -12, -5), (32, 38, 5.5, 6.5, -11, -6),
                          (38, 42, 5.5, 6.5, -10, -7)]),
              dict(name="flipper_back", pivot=(11, 4, 10), rot=(0, -40, -3),
                   boxes=[(11, 18, 3, 5, 8, 14), (18, 23, 3.5, 4.5, 9, 14), (23, 26, 3.5, 4.5, 10, 13)])],
    swim=dict(idle=(4.0, 8, 3), walk=(2.0, 26, 4), run=(1.2, 34, 5), sit=(5.0, 3, 1, 35)),
    attack=attack,
    ko=dict(roll=172, lift=0.3, shift=0.0, joints=LIMP, neck_down=-10),
)


def build():
    m = turtle.build(ID, SPEC)
    for a in m.animations:      # the archetype's swim was written for the old ~13.6 px/m model
        if a["name"].split(".")[-1] in ("idle", "walk", "run", "sit", "eat", "beg", "tame"):
            for tr in a["bones"].values():
                if "position" in tr:
                    tr["position"] = [[k[0]] + [round(v * K, 3) for v in k[1:]] for k in tr["position"]]
    for nm in ("attack", "eat"):
        fit_to_ground(m, nm, ("neck1", "neck2", "skull"))
    return m
