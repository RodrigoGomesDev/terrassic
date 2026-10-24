"""
Thescelosaurus neglectus  (Late Cretaceous, Maastrichtian; Hell Creek and Lance formations, North America)

Reference (Wikipedia; Gilmore 1913; Boyd 2014; Button & Zanno 2023): a stout bipedal ornithopod of 3.5-4 m and
~250-300 kg, one of the last dinosaurs before the extinction. A small head with a beak in front and leaf-shaped
cheek teeth behind, a thick neck, strong arms with five fingers, sturdy hind legs (no sprinter) and a long stiff
tail. "Willo" was the specimen with the supposed fossil heart. Its skull (Button & Zanno 2023) shows a huge
olfactory bulb, poor eyesight and inner ears tuned to low sounds: a sniffing, digging animal of the undergrowth.

Small-theropod rig with its own stout build and hands, no feathers, and a "dig" action added on top. Modelled
at 1.25x (render_scale 0.8, ~78 px long); SIZES scales it to 4 m. Olive-brown with a pale stripe along the flank
and freckles; males with dark cheek patches and a rust throat, females plainer.
"""
import math
from rig import track, keys
from smalltheropod import build_small

ID = "thescelosaurus"


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "skin":
        bone = tx.cube.bone
        if region == "flank" and bone.startswith(("neck", "tail")) is False and bone == "body":
            if abs(P[1] - 18.5) < 0.9:
                return tx.pal["stripe"].copy()                 # pale stripe along the flank
        if region == "flank" and bone.startswith("tail") and abs(P[1] - (tx.cube.frm[1] + tx.cube.size[1] * 0.55)) < 0.7:
            return tx.pal["stripe"].copy()
        if region in ("dorsal", "flank") and math.sin(P[0] * 2.3 + P[1]) * math.sin(P[2] * 1.7) > 0.62:
            rgb = rgb * 0.84                                   # freckles
        if bone == "skull" and tx.cube.name == "cheek":
            return tx.pal["cheek"].copy()
        if region == "belly" and bone.startswith("neck"):
            return tx.pal["throat"].copy()
    return rgb


def extra(m, neck, tail):
    # five-fingered hands: the rig's claw plus two stubby fingers each side
    ax = P["arm_x"]
    ey, ez = P["arm_pts"][-1]
    for side, sx in (("l", 1), ("r", -1)):
        x = ax * sx
        for dx in (-1.0, 1.0):
            m.box(f"forearm_{side}", (x + dx - 0.5, ey - 2, ez - 2), (x + dx + 0.5, ey, ez - 1),
                  tag="claw", name="finger", paint={"axis": "-y"})


def dig(m):
    # rooting: the body tips forward, the snout goes to the ground and the arms rake the soil in turns
    arm_l, arm_r, fore_l, fore_r = [], [], [], []
    for k in range(4):
        t0 = 0.5 + k * 0.4
        arm_l += [(t0, -45, 0, 0), (t0 + 0.2, 20, 0, 0)]
        arm_r += [(t0, 20, 0, 0), (t0 + 0.2, -45, 0, 0)]
        fore_l += [(t0, 25, 0, 0), (t0 + 0.2, 5, 0, 0)]
        fore_r += [(t0, 5, 0, 0), (t0 + 0.2, 25, 0, 0)]
    m.anim("dig", 2.6, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.5, -10, 0, 0), (2.1, -10, 0, 0), (2.6, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.5, 0, -1.0, 0), (2.1, 0, -1.0, 0), (2.6, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.5, -30, 0, 0), (2.1, -30, 0, 0), (2.6, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.5, -16, 0, 0), (2.1, -16, 0, 0), (2.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.5, -8, 0, 0), (0.9, -2, 0, 0), (1.3, -10, 0, 0), (1.7, -2, 0, 0), (2.1, -8, 0, 0), (2.6, 0, 0, 0)])),
        "arm_l": track(rot=keys([(0, 0, 0, 0)] + arm_l + [(2.6, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0)] + arm_r + [(2.6, 0, 0, 0)])),
        "forearm_l": track(rot=keys([(0, 0, 0, 0)] + fore_l + [(2.6, 0, 0, 0)])),
        "forearm_r": track(rot=keys([(0, 0, 0, 0)] + fore_r + [(2.6, 0, 0, 0)])),
        "thigh_l": track(rot=keys([(0, 0, 0, 0), (0.5, 8, 0, 0), (2.1, 8, 0, 0), (2.6, 0, 0, 0)])),
        "thigh_r": track(rot=keys([(0, 0, 0, 0), (0.5, 8, 0, 0), (2.1, 8, 0, 0), (2.6, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.5, 12, 0, 0), (2.1, 12, 0, 0), (2.6, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.7, 0, 10, 0), (1.1, 0, -10, 0), (1.5, 0, 10, 0), (1.9, 0, -10, 0), (2.6, 0, 0, 0)])),
    })


P = {
    "render_scale": 0.8,
    "palette": {
        "dorsal": "#5c5a3a", "flank": "#8c8458", "belly": "#d8d0a8", "stripe": "#d4cc9c", "cheek": "#3e3424",
        "throat": "#b86a3a",
        "limb": "#7a7250", "limb_top": "#8c8458",
        "claw": "#2a2520", "claw_base": "#2a2520", "claw_tip": "#5d574c",
        "beak": "#4e4638",
        "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421",
        "eye": "#8a6a2a", "pupil": "#120d08",
    },
    "sexes": {"male": {"cheek": "#2a2016", "throat": "#c05a2a", "dorsal": "#52502e"},
              "female": {"cheek": "#6a5e44", "throat": "#c8b088", "flank": "#948c64"}},
    # a stout, deep-bodied biped: barrel belly, thick neck, strong arms, sturdy legs, a long stiff tail
    "hip": (19, 5),
    "torso": [
        ((-5, 14, 0), (5, 24, 9), "hips"),
        ((-5.5, 13, -10), (5.5, 23, 1), "belly"),
        ((-4.5, 14, -15), (4.5, 22, -9), "chest"),
    ],
    "neck_pts": [(21, -14), (24, -18), (26, -21)],
    "neck_secs": [(5, 5), (4, 4)],
    "head_pitch": -4,
    "head": {"cranium": (5, 4, 5), "snout": (3, 3, 5), "snout_y": -1, "jaw": (3, 1, 5),
             "eye": (1.0, -2.0), "eye_r": 1.0},
    "head_extra": [
        dict(box=(-3.5, -2, -5, -2.5, 0, -1), tag="skin", bone="skull", name="cheek"),
        dict(box=(2.5, -2, -5, 3.5, 0, -1), tag="skin", bone="skull", name="cheek"),
        dict(box=(-3, 2.5, -4, 3, 3.5, 0), tag="skin", bone="male_display", name="brow"),
    ],
    "teeth": False,
    "beak": True,
    "arm_x": 4.0,
    "arm_pts": [(17, -11), (13, -10), (10, -12.5)],
    "arm_secs": [(2, 3), (2, 2)],
    "leg_x": 3.5,
    "leg_pts": [(19, 5), (11, 1), (5, 6), (1.5, 4)],
    "leg_secs": [(5, 7, -0.5), (3, 3, 0.5, "limb"), (2, 2, 0.0, "limb")],
    "toes": (4, 3),
    "sickle": False,
    "tail_pts": [(20, 8), (20, 17), (19.5, 26), (19, 34), (18.5, 41)],
    "tail_secs": [(6, 7), (5, 5), (3, 3), (2, 2)],
    "sit": {"drop": 10},
    "herbivore": True,
    "pattern": pattern,
    "extra": extra,
    "anim_speed": 0.9,
}


def build():
    m = build_small(ID, P)
    dig(m)
    return m
