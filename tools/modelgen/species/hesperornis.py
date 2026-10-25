"""
Hesperornis regalis  (Late Cretaceous, Campanian; Niobrara Chalk, Kansas; Marsh 1872)

Reference:
  - Size and build (Marsh 1880; Bell & Chiappe 2015): a flightless diving bird up to ~1.8 m long, built like a loon
    or a grebe: a long torpedo body, a long slender neck, a small flat skull with a long pointed beak.
  - Beak (Marsh 1880; Gingerich 1973): small sharp teeth set in a groove along the whole lower jaw and the back of
    the upper one (the maxilla); the tip of the upper jaw (premaxilla) toothless, covered in horn, slightly hooked.
  - Wings reduced to a tiny stub (only a slim humerus); powerful legs set far back, the knee inside the body
    outline; LOBED toes like a grebe's, the outer toe the longest (the feet probably turned edge-on on the
    recovery stroke). It could barely shuffle on land and hunted fish and squid under water.
  - Colour unknown: kept from the old model, dark above and pale below like a loon or cormorant, a glossy collar;
    males black-backed with a blue sheen, females sooty brown.

v2x (2026-10-25, remaster at the T. rex v3 level): its own geometry on the diver archetype (species/diver.py, its
swim and knockout), at the same ~41 px = 1 m as the old model (small species keep their density, like the
Compsognathus); the head ~1.3x the real proportion (the old one was ~2x). The foot is rebuilt as three lobed toes.
"""
import math
from rig import track, keys, add_knockout
import diver
from groundfit import fit_to_ground

ID = "hesperornis"
BODY_Y = 11


def body_parts(m):
    # a loon's torpedo: deep breast, long flat back, the rump tapering to a stub of a tail
    m.box("body", (-4, 8, -14), (4, 15, -10), name="breast")
    m.box("body", (-5, 7, -10), (5, 16, 0), name="chest")
    m.box("body", (-5.5, 7, 0), (5.5, 15, 10), name="torso")
    m.box("body", (-4, 8, 10), (4, 14, 16), name="rump")
    m.box("body", (-2.5, 9, 16), (2.5, 13, 19), name="rump_tip")
    m.box("body", (-3, 16, -9), (3, 17, 5), name="back")
    m.box("body", (-3, 6, -8), (3, 7, 8), name="belly")
    m.bone("tail1", "body", (0, 12, 18))
    m.box("tail1", (-2, 11, 18), (2, 12, 22), name="tail", tag="limb")


def head(m, ay, az, abs_pitch):
    m.bone("skull", "head", (0, ay, az), (-abs_pitch, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    TEETH = {"edge": "bottom", "rows": 1, "faces": ("east", "west"), "freq": 1.0}
    # small flat skull, a long spear of a beak: teeth in the back of the upper jaw, all along the lower one,
    # a toothless horny tip with a slight hook
    m.box("skull", *R(-2, -2, -4, 2, 2, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1.5, -2, -9, 1.5, 1, -4), name="beak_rear", tag="beak",
          paint={"faces": {"down": "mouth"}, "teeth": TEETH})
    m.box("skull", *R(-1, -2, -12, 1, 0, -9), name="beak", tag="beak", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-0.5, -3, -14, 0.5, 0, -12), name="beak_tip", tag="beak_tip")
    m.bone("jaw", "skull", (0, ay - 2, az - 3))
    m.box("jaw", *R(-1.5, -3, -9, 1.5, -2, -3), name="jaw_rear", tag="beak",
          paint={"faces": {"up": "mouth"}, "teeth": dict(TEETH, edge="top")})
    m.box("jaw", *R(-1, -3, -13, 1, -2, -9), name="jaw", tag="beak",
          paint={"faces": {"up": "mouth"}, "teeth": dict(TEETH, edge="top")})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (2, ay + 0.5, az - 2.0), "r": 0.9, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-2, ay + 0.5, az - 2.0), "r": 0.9, "side": -1},
    ]


# lobed toes on the foot (left side): (x0, x1, z1) of each toe from the foot's end at z 28, the outer toe longest;
# then the lobes (x0, x1, z0, z1)
TOES = [(1, 2, 33), (4, 5, 35), (7, 8, 36)]
LOBES = [(0, 1, 29, 32), (3, 4, 29, 34), (8, 9, 29, 35)]


def lobed_feet(m):
    m.cubes = [c for c in m.cubes if c.name != "toes"]
    for side, s in (("l", 1), ("r", -1)):
        def X(a, b):
            return min(a * s, b * s), max(a * s, b * s)
        for x0, x1, z1 in TOES:
            a, b = X(x0, x1)
            m.box(f"foot_{side}", (a, 5, 27), (b, 6, z1), name="toe", tag="limb")
        for x0, x1, z0, z1 in LOBES:
            a, b = X(x0, x1)
            m.box(f"foot_{side}", (a, 5, z0), (b, 6, z1), name="lobe", tag="fin")


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    name = tx.cube.name
    if tag in ("beak", "beak_tip"):
        col = tx.pal[tag].copy()
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
        if name == "toe":
            return rgb * (0.85 if int(math.floor(P[2])) % 2 == 0 else 1.0)   # scutes
        if name == "tail":
            return tx.pal["dorsal"].copy() * (0.9 + 0.15 * (int(math.floor(P[2] * 1.5)) % 2))
        return rgb
    if tag == "skin":
        # feather rows on the back, a white throat patch and the pale flank line of a loon
        if region == "dorsal":
            if (int(math.floor(P[2] * 1.3)) + int(math.floor(P[0] * 1.3))) % 2 == 0:
                rgb = rgb * 1.07
            if tx.cube.bone == "body" and (int(P[0]) * 7 + int(P[2]) * 5) % 9 == 0 and int(P[2]) % 2 == 0:
                rgb = tx.pal["fleck"].copy()                  # fine pale flecks on the back, as in loons
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
             "beak": "#4a4038", "beak_tip": "#2e2822", "fleck": "#8a8e92", "tooth": "#f0ece0", "mouth": "#8a4048", "gum": "#3a332c",
             "eye": "#b03838", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#1c2028", "sheen": "#2e4a74", "flank": "#4e5258"},
           "female": {"dorsal": "#3e3630", "sheen": "#4a4038", "flank": "#6a6258", "belly": "#dcdad0"}},
    pattern=pattern, body=(BODY_Y, 0), body_parts=body_parts, head=head,
    neck=dict(points=[(14, -12), (19, -17), (22, -24)], sections=[(5, 5), (4, 4)]),
    wings=dict(pivot=(5, 13, -5), box=(5, 6, 12, 13, -6, 0)),            # a tiny stub: only a slim humerus
    legs=dict(pivot=(4.5, 9, 10), thigh=(3, 6, 5, 10, 9, 13),
              shin_pivot=(0, 6, 13), shin=(3.5, 5.5, 5, 7, 13, 23),
              foot_pivot=(0, 6, 23), foot=(3.5, 5.5, 5, 7, 23, 28), toes=(4, 5, 5, 6, 27, 28)),
    swim=dict(idle=(3.0, 8, 1.0), walk=(1.2, 24, 1.5), run=(0.7, 32, 2.0), sit=(4.0, 3, 0.6)),
    sit_pose=dict(neck1=-26, neck2=30, skull=8),
    attack=attack,
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-30),
)


def build():
    m = diver.build(ID, SPEC)
    lobed_feet(m)
    # redo the knockout set with the full feet (the archetype grounded the old single toe box)
    m.animations = [a for a in m.animations
                    if a["name"].split(".")[-1] not in ("knocked_out", "wake", "eat", "beg", "tame")]
    ko = SPEC["ko"]
    add_knockout(m, roll=ko["roll"], lift=ko["lift"], shift=ko["shift"], joints=ko["joints"], neck_down=ko["neck_down"])
    for nm in ("attack", "eat"):
        fit_to_ground(m, nm, ("neck1", "neck2", "skull"))
    return m
