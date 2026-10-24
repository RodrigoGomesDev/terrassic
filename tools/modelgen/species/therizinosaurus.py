"""
Therizinosaurus cheloniformis  (Late Cretaceous, Maastrichtian; Nemegt Formation, Mongolia)

Reference (Wikipedia; Maleev 1954; Barsbold 1976; Zanno 2010; Paul 2010): a giant herbivorous theropod of 9-10 m
and ~5 t, first known only from its claws, which were taken for a turtle's ribs ("cheloniformis"). The longest
claws of any animal, up to 52 cm of bone (close to 1 m with the horny sheath), three per hand on long arms;
a pot belly over wide hips, a long neck with a small beaked head, short stout legs on four weight-bearing toes and
a short tail. Relatives (Beipiaosaurus) show a shaggy coat of feathers. A high browser that pulled branches
down with its claws, and a fearsome fighter when pushed.

Large-theropod rig with its own build (the pot belly, the long arms, the four-toed feet, the short tail), the
huge curved claws, shaggy plumage, a claw-slash attack and a high-browsing "graze" (branches down to the beak).
Modelled ~84 px long and ~55 px tall; SIZES scales it to 10 m. Dark shaggy brown with a pale belly, cream claws;
males darker with a rusty neck ruff, females dun.
"""
import math
from paint import vnoise
from rig import track, keys
import large_theropod

ID = "therizinosaurus"
AX = 7.0
ARM_PTS = [(31, -20), (23, -21), (16, -22)]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "feather":
        frac = (P[2] - tx.cube.frm[2]) / max(1.0, tx.cube.size[2])
        if frac > 0.8:
            return tx.pal["feather_tip"].copy()
        n = vnoise(P[0] / 1.2, P[1] / 1.2, P[2] / 4.0, 61)
        return rgb * (0.85 + 0.3 * n)
    if tag == "ruff":
        n = vnoise(P[0] / 1.5, P[1] / 1.5, P[2] / 1.5, 67)
        return tx.pal["ruff"] * (0.85 + 0.3 * n)
    if tag == "skin":
        # shaggy: vertical streaks of light and dark, like hanging feathers
        n = vnoise(P[0] / 1.3, P[1] / 5.0, P[2] / 1.3, 71)
        rgb = rgb * (0.84 + 0.32 * n)
        if region == "belly":
            rgb = rgb * 1.04
    return rgb


def after_torso(m):
    # the shaggy back: a feather mantle over the shoulders and hips
    m.box("body", (-6, 38, -18), (6, 40, 10), name="mantle", tag="feather")
    m.box("body", (-7, 35, -26), (7, 38, -16), name="shoulder_coat", tag="feather")


def after_tail(m, tail):
    # the giant claws: three per hand, curving down and in, each of a base and a hooked tip; and the arm feathers
    ey, ez = ARM_PTS[-1]
    for side, sx in (("l", 1), ("r", -1)):
        x = AX * sx
        for dx in (-1.5, 0.0, 1.5):
            org = (x + dx, ey, ez - 0.5)
            m.box(f"forearm_{side}", (x + dx - 0.5, ey - 5, ez - 1), (x + dx + 0.5, ey, ez), name="claw", tag="claw",
                  rot=(-12, 0, 0), origin=org, paint={"axis": "-y"})
            m.box(f"forearm_{side}", (x + dx - 0.5, ey - 9, ez - 2), (x + dx + 0.5, ey - 5, ez - 1), name="claw_tip", tag="claw",
                  rot=(-30, 0, 0), origin=org, paint={"axis": "-y"})
        # a vane of long feathers hanging from the forearm's trailing edge
        m.box(f"forearm_{side}", (x - 0.5, ey, ez), (x + 0.5, ey + 7, ez + 5), name="arm_feathers", tag="feather")
    # the male neck ruff
    m.bone("male_display", "neck1", (0, 36, -24))
    m.box("male_display", (-4, 32, -29), (4, 40, -24), name="ruff", tag="ruff")


def extra_anims(m):
    # replace the rig's bite with a claw slash: both arms rise, then rake down and across
    m.animations = [a for a in m.animations if not a["name"].endswith(".attack")]
    m.anim("attack", 0.9, False, {
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.25, -110, 0, -25), (0.45, 30, 0, 10), (0.9, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.3, -110, 0, 25), (0.5, 30, 0, -10), (0.9, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.25, 40, 0, 0), (0.45, -10, 0, 0), (0.9, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.3, 40, 0, 0), (0.5, -10, 0, 0), (0.9, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.25, 6, 0, 0), (0.45, -5, 0, 0), (0.9, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.25, 0, 0.5, 1), (0.45, 0, -0.5, -2), (0.9, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.25, 10, 0, 0), (0.45, -8, 0, 0), (0.9, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.25, -20, 0, 0), (0.5, -24, 0, 0), (0.7, 0, 0, 0), (0.9, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.25, -4, 0, 0), (0.45, 5, 0, 0), (0.9, 0, 0, 0)])),
    })
    # browsing: the neck reaches up, the claws hook a branch down to the beak, and it chews
    jk = [(0, 0, 0, 0), (0.9, 0, 0, 0)]
    for k in range(5):
        t0 = 1.1 + k * 0.3
        jk += [(t0, -14, 0, 0), (t0 + 0.15, -2, 0, 0)]
    jk += [(3.0, 0, 0, 0)]
    m.anim("graze", 3.0, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, 16, 0, 0), (0.9, 8, 0, 0), (2.6, 8, 0, 0), (3.0, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.5, 8, 0, 0), (2.6, 4, 0, 0), (3.0, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.5, 10, 0, 0), (0.9, -6, 0, 0), (2.6, -6, 0, 0), (3.0, 0, 0, 0)])),
        "jaw": track(rot=keys(jk)),
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.5, -120, 0, -15), (0.9, -60, 0, -10), (2.6, -60, 0, -10), (3.0, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.5, -120, 0, 15), (0.9, -60, 0, 10), (2.6, -60, 0, 10), (3.0, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0), (0.5, 20, 0, 0), (0.9, 50, 0, 0), (2.6, 50, 0, 0), (3.0, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0), (0.5, 20, 0, 0), (0.9, 50, 0, 0), (2.6, 50, 0, 0), (3.0, 0, 0, 0)])),
        "body": track(rot=keys([(0, 0, 0, 0), (0.5, 4, 0, 0), (2.6, 3, 0, 0), (3.0, 0, 0, 0)])),
    })


MOUTH_UP, MOUTH_DOWN = {"faces": {"up": "mouth"}}, {"faces": {"down": "mouth"}}
SPEC = dict(
    palette={"dorsal": "#4e4034", "flank": "#7a6448", "belly": "#d4c4a4", "limb": "#5e4e40", "limb_top": "#6e5c48",
             "claw": "#d8ccb0", "claw_base": "#8a7a60", "claw_tip": "#f0e8d8",
             "feather": "#3a3028", "feather_tip": "#c8b890", "ruff": "#a04a28",
             "beak": "#4a4036", "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
             "eye": "#c89a30", "pupil": "#17110c", "saddle": "#7a4f2e"},
    sexes={"male": {"dorsal": "#423428", "feather": "#2a2220", "feather_tip": "#e8d8a8", "ruff": "#b04a24"},
           "female": {"dorsal": "#5e4e40", "flank": "#8a7458", "feather": "#5a4a3c", "feather_tip": "#b8a888", "ruff": "#8a6a4c"}},
    pattern=pattern, after_torso=after_torso, after_tail=after_tail, extra_anims=extra_anims,
    body=(34, 8),
    # the pot belly between wide hips; a deep chest the long arms hang from
    torso=[("hips", (-8, 24, -2, 8, 38, 12)), ("belly", (-9, 19, -16, 9, 37, 0)), ("chest", (-7, 22, -24, 7, 36, -15)),
           ("shoulders", (-5, 30, -27, 5, 37, -22)), ("belly_low", (-6, 16, -13, 6, 19, -2))],
    neck=([(36, -24), (43, -30), (49, -34)], [(7, 7), (5, 5)]), skull_tilt=10,
    head=[  # a small head: rounded cranium, a short beak, a slim lower jaw
        dict(bone="skull", box=(-2.5, -1, -5, 2.5, 3, 1), name="cranium", paint=MOUTH_DOWN),
        dict(bone="skull", box=(-2, 0, -9, 2, 2, -5), name="beak", tag="beak", paint=MOUTH_DOWN),
        dict(bone="jaw", box=(-2, -2, -9, 2, 0, -1), name="jaw", tag="beak", paint=MOUTH_UP),
    ],
    jaw_pivot=(-1, -1), eyes=(1.0, 1.5, -3.0, 2.5),
    arm=(AX, ARM_PTS, [(3, 4), (3, 3)], []),             # the claws come from after_tail (they need rotation)
    leg=(6.5, [(34, 8), (21, 2), (9, 9), (2, 5)], [(7, 10, -0.5), (5, 6, 1.0, "limb"), (4, 5, 0.0, "limb")],
         [("toe_a", "limb", (-4, -2, -5, -2, 0, 1)), ("toe_b", "limb", (-2, -2, -6, 0, 0, 1)),
          ("toe_c", "limb", (0, -2, -6, 2, 0, 1)), ("toe_d", "limb", (2, -2, -5, 4, 0, 1)),
          ("claw_a", "claw", (-4, -2, -6, -2, -1, -5)), ("claw_b", "claw", (-2, -2, -7, 0, -1, -6)),
          ("claw_c", "claw", (0, -2, -7, 2, -1, -6)), ("claw_d", "claw", (2, -2, -6, 4, -1, -5))]),
    tail=([(34, 12), (33, 20), (31.5, 27), (30, 33), (28, 38)], [(9, 9), (7, 7), (5, 5), (3, 3)]),
    saddle=((40, -8, 4, 9, 8), {"flap": 6}),
    sit=(14, 60, -115, 60, -6, {"tail1": (8, 0, 0), "tail2": (4, 0, 0), "neck1": (-8, 0, 0), "skull": (4, 0, 0),
                                "arm_l": (10, 0, 0), "arm_r": (10, 0, 0)}),
)


def build():
    m = large_theropod.build(ID, SPEC)
    SPEC["extra_anims"](m)
    return m
