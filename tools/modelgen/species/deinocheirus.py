"""
Deinocheirus mirificus  (Late Cretaceous, Maastrichtian; Nemegt Formation, Mongolia)

Reference (Wikipedia; Osmólska & Roniewicz 1970; Lee et al. 2014): the "terrible hand", known for 50 years only
from a pair of 2.4 m arms; the 2014 skeletons showed the biggest ornithomimosaur ever, 11 m and ~6.4 t: a
humped back of tall neural spines, a long duck-like toothless bill, a long neck, huge arms with three blunt
claws, short stout legs with broad hoof-like toes and a tail ending in a pygostyle (a feather fan). Fish scales
and gastroliths in its belly: an omnivore wading the river margins, scooping plants and fish.

Large-theropod rig with its own build: the hump, the bill, the long arms, the hoofed feet, the tail fan; a slow
double-arm swipe for an attack, a "graze" at the ground and a "fish" scoop at the water. Modelled ~96 px long;
SIZES scales it to 11 m. Dusty grey-brown with a pale underside, a dark hump and a black-and-white tail fan;
males with a taller, redder hump, females plainer.
"""
import math
from paint import vnoise
from rig import track, keys
import large_theropod

ID = "deinocheirus"
AX = 7.5
ARM_PTS = [(33, -24), (23, -25), (13, -27)]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "feather":
        frac = (P[2] - tx.cube.frm[2]) / max(1.0, tx.cube.size[2])
        if frac > 0.72 or 0.3 < frac < 0.42:
            return tx.pal["feather_tip"].copy()
        return rgb
    if tag == "hump":
        n = vnoise(P[0] / 2.0, P[1] / 2.0, P[2] / 2.0, 83)
        col = tx.pal["hump"] * (0.88 + 0.24 * n)
        if int(math.floor(P[2])) % 4 == 0:
            col = col * 0.86                                   # the spines under the skin
        return col
    if tag == "beak":
        if tx.face == "up" and tx.cube.name == "bill" and P[2] < tx.cube.frm[2] + 2.0:
            return tx.pal["beak_tip"].copy()                   # the pale nail at the tip of the bill
        return rgb
    if tag == "skin":
        n = vnoise(P[0] / 3.0, P[1] / 3.0, P[2] / 3.0, 89)
        rgb = rgb * (0.9 + 0.2 * n)
        if region == "dorsal" and math.sin(P[2] * 0.6) * math.sin(P[0] * 0.8 + P[1] * 0.2) > 0.5:
            rgb = tx.pal["mottle"].copy()
        if tx.cube.bone.startswith("neck") and region != "belly" and math.sin(P[1] * 1.1 + P[2] * 0.4) > 0.75:
            rgb = rgb * 0.86                                   # faint rings down the neck
    return rgb


def after_torso(m):
    # the hump: tall neural spines over the hips and back, under a thick ridge of skin
    m.box("body", (-4, 38, -12), (4, 43, 12), name="hump", tag="hump")
    m.box("body", (-3, 43, -8), (3, 47, 8), name="hump_top", tag="hump")
    m.bone("male_display", "body", (0, 40, 0))
    m.box("male_display", (-2, 47, -6), (2, 50, 6), name="hump_crest", tag="hump")


def after_tail(m, tail):
    # the arms: three long blunt claws per hand; the tail fan of feathers on the pygostyle
    ey, ez = ARM_PTS[-1]
    for side, sx in (("l", 1), ("r", -1)):
        x = AX * sx
        for dx in (-1.5, 0.0, 1.5):
            m.box(f"forearm_{side}", (x + dx - 0.5, ey - 5, ez - 1), (x + dx + 0.5, ey, ez), name="claw", tag="claw",
                  rot=(-8, 0, 0), origin=(x + dx, ey, ez - 0.5), paint={"axis": "-y"})
    sg = tail["segments"][3]
    y0, z0 = sg["unposed"]
    L = int(round(sg["len"]))
    m.box("tail4", (-4, y0 - 0.5, z0 + 1), (4, y0 + 0.5, z0 + L + 4), name="fan", tag="feather")
    m.box("tail4", (-6, y0 - 0.5, z0 + 3), (6, y0 + 0.5, z0 + L + 2), name="fan_wide", tag="feather")


def extra_anims(m):
    # the attack: not a bite but a slow heavy swipe of both arms across the front
    m.animations = [a for a in m.animations if not a["name"].endswith(".attack")]
    m.anim("attack", 1.1, False, {
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.35, -80, 0, -40), (0.6, -40, 0, 30), (1.1, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.4, -80, 0, 40), (0.65, -40, 0, -30), (1.1, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.35, 30, 0, 0), (0.6, 0, 0, 0), (1.1, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.4, 30, 0, 0), (0.65, 0, 0, 0), (1.1, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.35, 5, 8, 0), (0.6, -4, -10, 0), (1.1, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.35, 10, 0, 0), (0.6, -6, 0, 0), (1.1, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.35, -16, 0, 0), (0.7, -16, 0, 0), (1.1, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.35, 0, -10, 0), (0.6, 0, 12, 0), (1.1, 0, 0, 0)])),
    })
    # grazing: the bill goes down to the ground and sweeps side to side
    jk = [(0, 0, 0, 0), (0.7, 0, 0, 0)]
    for k in range(5):
        t0 = 0.9 + k * 0.3
        jk += [(t0, -12, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(2.8, 0, 0, 0)]
    m.anim("graze", 2.8, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.7, -36, 0, 0), (2.3, -36, 0, 0), (2.8, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.7, -24, 0, 0), (2.3, -24, 0, 0), (2.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.7, -12, 0, 0), (1.1, -12, 0, 10), (1.5, -12, 0, -10), (1.9, -12, 0, 8), (2.3, -12, 0, 0), (2.8, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
        "body": track(rot=keys([(0, 0, 0, 0), (0.7, -6, 0, 0), (2.3, -6, 0, 0), (2.8, 0, 0, 0)])),
    })
    # fishing: the body leans over the water, both arms scoop forward and down, then lift together to the bill
    m.anim("fish", 2.4, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.5, -8, 0, 0), (1.3, -8, 0, 0), (1.8, -2, 0, 0), (2.4, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, -20, 0, 0), (1.3, -20, 0, 0), (1.8, 6, 0, 0), (2.4, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.5, -6, 0, 0), (1.3, -6, 0, 0), (1.8, 8, 0, 0), (2.4, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (1.6, 0, 0, 0), (1.9, -18, 0, 0), (2.1, -4, 0, 0), (2.4, 0, 0, 0)])),
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.5, -60, 0, -10), (0.9, -30, 0, -20), (1.3, -60, 0, -10), (1.8, -100, 0, -5), (2.4, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.5, -60, 0, 10), (0.9, -30, 0, 20), (1.3, -60, 0, 10), (1.8, -100, 0, 5), (2.4, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.5, 20, 0, 0), (0.9, 40, 0, 0), (1.3, 20, 0, 0), (1.8, 60, 0, 0), (2.4, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.5, 20, 0, 0), (0.9, 40, 0, 0), (1.3, 20, 0, 0), (1.8, 60, 0, 0), (2.4, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.5, 8, 0, 0), (1.3, 8, 0, 0), (2.4, 0, 0, 0)])),
    })


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
SPEC = dict(
    palette={"dorsal": "#6a6256", "flank": "#938a78", "belly": "#e0d8c4", "mottle": "#4e4840", "hump": "#4a423a",
             "limb": "#746c5e", "limb_top": "#847c6c",
             "claw": "#3a3630", "claw_base": "#3a3630", "claw_tip": "#8a847a",
             "feather": "#2a2624", "feather_tip": "#ece8e0", "beak": "#50483e", "beak_tip": "#d8c8a0",
             "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
             "eye": "#c0a040", "pupil": "#17110c", "saddle": "#7a4f2e"},
    sexes={"male": {"hump": "#6a3a2a", "dorsal": "#5e5648", "feather": "#1e1a18", "feather_tip": "#f4f0e8"},
           "female": {"hump": "#5a5048", "flank": "#9c9484", "feather": "#4a4440", "feather_tip": "#d0ccc0"}},
    pattern=pattern, after_torso=after_torso, after_tail=after_tail, extra_anims=extra_anims,
    body=(35, 8),
    # a deep barrel on wide hips, the chest the huge arms hang from, a tall humped back
    torso=[("hips", (-7, 25, -2, 7, 39, 13)), ("belly", (-8, 19, -16, 8, 38, 0)), ("chest", (-7, 21, -27, 7, 37, -15)),
           ("shoulders", (-6, 30, -30, 6, 38, -24)), ("belly_low", (-5, 16, -14, 5, 19, -3))],
    neck=([(37, -28), (45, -34), (52, -37)], [(7, 8), (6, 6)]), skull_tilt=14,
    head=[  # a long flat duck bill on a low skull
        dict(bone="skull", box=(-3, -1, -5, 3, 3, 1), name="cranium", paint=MOUTH_DOWN),
        dict(bone="skull", box=(-3, -0.5, -14, 3, 1.5, -5), name="bill", tag="beak", paint=MOUTH_DOWN),
        dict(bone="jaw", box=(-3, -2.5, -13, 3, -0.5, -1), name="jaw", tag="beak", paint=MOUTH_UP),
    ],
    jaw_pivot=(-1, -1), eyes=(1.1, 1.5, -3.0, 3.0),
    arm=(AX, ARM_PTS, [(4, 5), (3, 4)], []),             # the claws come from after_tail
    leg=(7.0, [(35, 8), (22, 3), (10, 10), (2, 6)], [(8, 11, -0.5), (6, 7, 1.0, "limb"), (5, 6, 0.0, "limb")],
         [("toe_mid", "limb", (-2, -2, -7, 2, 0, 1)), ("toe_out", "limb", (2, -2, -5, 4, 0, 1)),
          ("toe_in", "limb", (-4, -2, -5, -2, 0, 1)), ("hoof_mid", "claw", (-2, -2, -8, 2, -1, -7)),
          ("hoof_out", "claw", (2, -2, -6, 4, -1, -5)), ("hoof_in", "claw", (-4, -2, -6, -2, -1, -5))]),
    tail=([(35, 13), (34, 24), (33, 34), (32, 42), (31, 48)], [(10, 10), (7, 7), (5, 5), (3, 3)]),
    saddle=((44, -8, 4, 9, 7), {"flap": 6}),
    sit=(14, 60, -115, 60, -6, {"tail1": (8, 0, 0), "tail2": (4, 0, 0), "neck1": (-8, 0, 0), "skull": (4, 0, 0),
                                "arm_l": (10, 0, 0), "arm_r": (10, 0, 0)}),
)


def build():
    m = large_theropod.build(ID, SPEC)
    SPEC["extra_anims"](m)
    return m
