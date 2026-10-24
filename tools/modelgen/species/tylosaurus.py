"""
Tylosaurus proriger  (Late Cretaceous, Santonian-Campanian; Western Interior Seaway, Kansas)

Reference (Wikipedia; Everhart 2005 "Oceans of Kansas"; Lindgren et al. 2014): a mosasaur of 12-13 m (the
"Bunker" specimen KUVP 5033 ~13 m), the top predator of the inland sea before the Mosasaurus: a slender, very long
body, a tail close to half the total length, SMALL flippers, and a long skull whose snout ends in a toothless,
reinforced rostrum used to ram prey (the "tylos" = knob). Fossil skin shows dark countershading. Stomach
contents: plesiosaurs, sharks, fish, birds and even a small mosasaur.

Modelled ~121 px long, sleeker than the Mosasaurus; SIZES scales it to 13 m. Slate-blue with pale flank bars;
males darker with sharper bars, females browner.
"""
import math
from rig import track, keys
import marine

ID = "tylosaurus"


def body_parts(m):
    # slimmer torso than the Mosasaurus, a long chest tapering to the neck
    m.box("body", (-5.5, 1.5, -10), (5.5, 14.5, 12), name="torso")
    m.box("body", (-5, 2.5, -20), (5, 13.5, -10), name="chest")

    neck = m.chain(["neck"], "body", 0, [(8.5, -19), (9, -26)], "-z", [(8, 8)], overlap=(1.0, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # long low skull; the toothed snout, then the toothless rostrum that sticks out past the teeth
    m.box("skull", *R(-4, -3, -8, 4, 3, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2.5, -3, -21, 2.5, 2, -8), name="snout",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}})
    m.box("skull", *R(-2, -2.5, -26, 2, 1.5, -21), name="rostrum", tag="rostrum")
    m.bone("jaw", "skull", (0, ay - 3, az - 3))
    m.box("jaw", *R(-2.5, -6, -21, 2.5, -3, -6), name="jaw", paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}})
    m.box("jaw", *R(-4, -6, -6, 4, -3, 0), name="jaw_back", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (4, ay + 1.0, az - 5.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-4, ay + 1.0, az - 5.0), "r": 1.0, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "fin":
        col = tx.pal["fin"].copy()
        if tx.edge:
            col = tx.pal["fin_edge"].copy()
        return col
    if tag == "rostrum":
        # scarred, pale knob of bone-backed skin
        col = tx.pal["rostrum"].copy()
        if math.sin(P[2] * 2.3 + P[1] * 1.1) > 0.6:
            col = col * 0.9
        return col
    if tag == "skin":
        if region == "flank" and math.sin(P[2] * 0.52 + 0.4 * math.sin(P[1] * 0.9)) > 0.55:
            rgb = tx.pal["bar"].copy()                      # pale vertical bars along the flanks
        elif region == "dorsal" and math.sin(P[2] * 1.1 + P[0] * 0.9) * math.sin(P[0] * 1.7) > 0.6:
            rgb = rgb * 0.86                                 # dark mottling on the back
    return rgb


def attack(m):
    # ram: the whole body lunges, the head drops so the rostrum leads, then a quick bite as it pulls back
    m.anim("attack", 0.8, False, {
        "body": track(pos=keys([(0, 0, 0, 0), (0.2, 0, 0, 3), (0.4, 0, 0, -6), (0.8, 0, 0, 0)]),
                      rot=keys([(0, 0, 0, 0), (0.2, -2, 0, 0), (0.4, 2, 0, 0), (0.8, 0, 0, 0)])),
        "neck": track(rot=keys([(0, 0, 0, 0), (0.2, -8, 0, 0), (0.4, 12, 0, 0), (0.6, -4, 0, 0), (0.8, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.4, 0, 0, 0), (0.55, -36, 0, 0), (0.65, -2, 0, 0), (0.8, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.2, 0, 14, 0), (0.4, 0, -12, 0), (0.8, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.25, 0, 18, 0), (0.45, 0, -16, 0), (0.8, 0, 0, 0)])),
    })


LIMP = {"neck": (3, -5, 0), "skull": (2, 0, 0), "jaw": (-14, 0, 0),
        "tail1": (-3, 0, 0), "tail2": (-4, 0, 0), "tail3": (-5, 0, 0), "tail4": (-6, 0, 0), "tail5": (-6, 0, 0), "tail6": (-5, 0, 0),
        "flipper_front_l": (0, -60, 20), "flipper_front_r": (0, 60, -20),
        "flipper_back_l": (0, -60, 20), "flipper_back_r": (0, 60, -20)}

SPEC = dict(
    palette={"dorsal": "#243038", "flank": "#4a5a62", "belly": "#cfd4cc", "bar": "#6e7e84",
             "limb": "#2c3840", "limb_top": "#36444c",
             "fin": "#1e2a30", "fin_edge": "#44545c",
             "rostrum": "#9aa09a",
             "tooth": "#efe9d6", "mouth": "#86363a", "gum": "#5a2426",
             "eye": "#d8b85a", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#1c262e", "bar": "#7a8c92"},
           "female": {"dorsal": "#34403e", "flank": "#5a6660", "bar": "#747e74", "belly": "#d6d6c8"}},
    pattern=pattern, body=(8, 0), body_parts=body_parts,
    # tail almost half the animal: six segments
    tail=dict(points=[(8, 11), (8, 24), (7.5, 36), (7, 47), (7, 56), (7, 63), (7.5, 69)],
              sections=[(10, 10), (8, 8), (6, 6), (5, 5), (4, 4), (3, 3)],
              fluke=dict(lower=(15, -40, 2.5), upper=(9, 36, 2)),
              keel=[(2, 2), (3, 2), (4, 1), (5, 1)]),
    # small paddles set low
    flippers=[dict(name="flipper_front", pivot=(4.5, 4, -15), rot=(0, -28, -18), span=(4.5, 13.5), y=(3.5, 4.5), z=(-18, -13)),
              dict(name="flipper_back", pivot=(4.5, 4, 8), rot=(0, -32, -18), span=(4.5, 10.5), y=(3.5, 4.5), z=(6, 10))],
    swim=dict(idle=(3.6, 6, 6, 2.0), walk=(1.8, 12, 10), run=(0.9, 18, 12, 4.0), sit=(4.0, 4, 4, 1.0)),
    attack=attack,
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-10),
)


def build():
    return marine.build(ID, SPEC)
