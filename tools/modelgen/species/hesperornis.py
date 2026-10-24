"""
Hesperornis regalis  (Late Cretaceous, Campanian; Niobrara Chalk, Kansas; Marsh 1872)

Reference (Wikipedia; Marsh 1880; Bell & Chiappe 2015): a flightless diving bird up to 1.8 m long, built like a loon
or a grebe: a long neck, a long pointed beak with teeth in the lower jaw and the back of the upper one, wings reduced
to a stub, and powerful legs set so far back that it could barely shuffle on land; it swam with lobed feet, kicking
alternately, and hunted fish and squid under water. Dark above and pale below like a cormorant.

Built on the diver archetype, modelled at 2x (~70 px long); SIZES scales it to 1.8 m. Males black-backed with a
glossy blue sheen, females sooty brown.
"""
import math
from rig import track, keys
import diver

ID = "hesperornis"
BODY_Y = 11


def body_parts(m):
    # a loon's torpedo: deep chest, long flat back, pointed rump, a stub of a tail
    m.box("body", (-5, 7, -10), (5, 16, 12), name="torso")
    m.box("body", (-4, 8, -14), (4, 15, -10), name="breast")
    m.box("body", (-4, 8, 12), (4, 14, 17), name="rump")
    m.bone("tail1", "body", (0, 12, 17))
    m.box("tail1", (-3, 11, 17), (3, 13, 22), name="tail", tag="limb")


def head(m, ay, az, abs_pitch):
    m.bone("skull", "head", (0, ay, az), (-abs_pitch, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # small flat skull, a long spear of a beak: teeth only in the back of the upper jaw, all along the lower one
    m.box("skull", *R(-2.5, -2, -7, 2.5, 3, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1.5, -1, -13, 1.5, 1, -7), name="beak_rear", tag="beak",
          paint={"teeth": {"edge": "bottom", "rows": 1, "freq": 1.6}})
    m.box("skull", *R(-1, -1, -20, 1, 1, -13), name="beak", tag="beak")
    m.bone("jaw", "skull", (0, ay - 2, az - 6))
    m.box("jaw", *R(-1.5, -3, -13, 1.5, -1, -6), name="jaw_rear", tag="beak",
          paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1, "freq": 1.6}})
    m.box("jaw", *R(-1, -3, -20, 1, -1, -13), name="jaw", tag="beak", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (2.5, ay + 0.8, az - 4.5), "r": 0.9, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-2.5, ay + 0.8, az - 4.5), "r": 0.9, "side": -1},
    ]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    name = tx.cube.name
    if tag == "beak":
        col = tx.pal["beak"].copy()
        if tx.face == "up":
            col = col * 0.9
        return col
    if tag == "fin":
        col = tx.pal["fin"].copy()
        if int(math.floor(P[0] * 1.2 + 100)) % 2 == 0:
            col = col * 0.9                                   # the lobes of the toes
        return col
    if tag == "limb":
        if name == "wing":
            return tx.pal["dorsal"].copy() * (0.95 if tx.face != "up" else 1.05)
        if name == "tail":
            return tx.pal["dorsal"].copy() * (0.9 + 0.15 * (int(math.floor(P[2] * 1.5)) % 2))
        return rgb
    if tag == "skin":
        # feather rows on the back, a white throat patch and the pale flank line of a loon
        if region == "dorsal":
            if (int(math.floor(P[2] * 1.3)) + int(math.floor(P[0] * 1.3))) % 2 == 0:
                rgb = rgb * 1.07
            if tx.cube.bone.startswith("neck") and math.sin(P[1] * 2.2) > 0.6:
                rgb = tx.pal["sheen"].copy()                  # the glossy collar
        elif region == "flank" and tx.cube.bone == "body" and abs(P[1] - 9) < 0.9:
            rgb = rgb * 1.1
        elif region == "belly" and tx.cube.bone.startswith("neck"):
            rgb = tx.pal["throat"].copy()
    return rgb


def attack(m):
    # the loon's strike: the neck straightens and the beak stabs down, the jaw snapping on the fish
    m.anim("attack", 0.5, False, {
        "body": track(pos=keys([(0, 0, 0, 0), (0.12, 0, 0, 1), (0.25, 0, 0, -3), (0.5, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.12, 16, 0, 0), (0.25, -30, 0, 0), (0.5, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.12, -10, 0, 0), (0.25, 14, 0, 0), (0.5, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.12, 8, 0, 0), (0.25, -12, 0, 0), (0.5, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.12, -32, 0, 0), (0.22, -34, 0, 0), (0.27, 0, 0, 0), (0.5, 0, 0, 0)])),
        "shin_l": track(rot=keys([(0, 0, 0, 0), (0.12, -12, 0, 0), (0.25, 16, 0, 0), (0.5, 0, 0, 0)])),
        "shin_r": track(rot=keys([(0, 0, 0, 0), (0.12, -12, 0, 0), (0.25, 16, 0, 0), (0.5, 0, 0, 0)])),
    })


# knocked out on its side: neck laid out along the ground (pitch becomes a ground curve after the roll), legs trailing
LIMP = {"neck1": (-28, 0, 0), "neck2": (18, 0, 0), "skull": (6, 0, 0), "jaw": (-14, 0, 0), "tail1": (4, 0, 0),
        "thigh_l": (12, 0, 0), "thigh_r": (-10, 0, 0), "shin_l": (20, 0, 0), "shin_r": (10, 0, 0),
        "foot_l": (-30, 0, 0), "foot_r": (-20, 0, 0), "wing_l": (0, 0, 20), "wing_r": (0, 0, -20)}

SPEC = dict(
    render_scale=0.5,
    palette={"dorsal": "#262a30", "flank": "#5a5e62", "belly": "#e6e8e2", "throat": "#f0f2ec", "sheen": "#2c3e5a",
             "limb": "#3a3c3e", "limb_top": "#4a4c4e",
             "fin": "#5a5a52", "fin_edge": "#8a8a80",
             "beak": "#4a4038", "tooth": "#f0ece0", "mouth": "#8a4048", "gum": "#5a2a30",
             "eye": "#b03838", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#1c2028", "sheen": "#2e4a74", "flank": "#4e5258"},
           "female": {"dorsal": "#3e3630", "sheen": "#4a4038", "flank": "#6a6258", "belly": "#dcdad0"}},
    pattern=pattern, body=(BODY_Y, 0), body_parts=body_parts, head=head,
    neck=dict(points=[(14, -12), (20, -17), (22, -23)], sections=[(5, 5), (4, 4)]),
    wings=dict(pivot=(5, 13, -6), box=(5, 6, 12, 14, -7, 2)),
    legs=dict(pivot=(4.5, 9, 10), thigh=(3, 6, 5, 10, 9, 13),
              shin_pivot=(0, 6, 13), shin=(3.5, 5.5, 5, 7, 13, 23),
              foot_pivot=(0, 6, 23), foot=(2, 7, 5, 7, 23, 30), toes=(1, 8, 5, 6, 26, 31)),
    swim=dict(idle=(3.0, 8, 1.0), walk=(1.2, 24, 1.5), run=(0.7, 32, 2.0), sit=(4.0, 3, 0.6)),
    sit_pose=dict(neck1=-26, neck2=30, skull=8),
    attack=attack,
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-30),
)


def build():
    return diver.build(ID, SPEC)
