"""
Vegavis iaai  (Late Cretaceous, Maastrichtian ~68-66 Ma; Vega Island, Antarctic Peninsula)

Reference (Wikipedia; Clarke et al. 2005, 2016; Acosta Hospitaleche & Worthy 2021): one of the few modern-type birds
known from the age of the dinosaurs, a close relative of ducks and geese (Anseriformes), about the size of a small
duck or a teal. The 2016 skeleton preserved a SYRINX, the oldest voice box of any bird: it honked like a goose.
Thick-walled leg bones and a strong, far-set hindlimb mark a foot-propelled swimmer and diver like a loon or a
diving duck; it also flew. A toothless, duck-like bill.

Bird archetype (the Ichthyornis rig) modelled at 4x (render_scale 0.25): ~38 px nose to tail and a 64 px wingspan
-> 0.6 m body, 1.0 m wingspan in the world. The "duck" of the Cretaceous: flocks on rivers, deltas and beaches.
Colours: dark olive-brown back, buff speckled flanks, cream belly, a chestnut head with a pale cheek stripe and a
dark cap on the male (the female is drab, mottled brown all over), a slate bill with a pale nail, orange-grey webbed
feet, a white bar on the secondaries.
"""
import math
from paint import vnoise, hash3
from rig import track, keys
import bird

ID = "vegavis"
BODY_Y = 10.5
SHOULDER = (3.5, 13, -2)


def body_parts(m):
    # a plump duck body: deep rounded breast, broad back, rump rising to a short upturned tail
    m.box("body", (-4, 7, -6), (4, 14, 6), name="torso")
    m.box("body", (-3, 5, -6), (3, 7, 2), name="breast")
    m.box("body", (-3, 8, 6), (3, 13, 9), name="rump")
    m.bone("tail", "body", (0, 11, 9))
    m.box("tail", (-3, 10.5, 9), (3, 11.5, 14), name="tail_fan", tag="feather", rot=(-12, 0, 0), origin=(0, 11, 9))

    # the duck neck: thick, carried in a gentle S, the head level with the back
    neck = m.chain(["neck1"], "body", 0, [(12.5, -5), (17, -8.5)], "-z", [(3, 3)], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck1", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"] + 6, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    # rounded cranium with a slight forehead, then the flat broad bill ending in a nail
    m.box("skull", *R(-2.5, -2, -5, 2.5, 2, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, -1.5, -9, 2, 0.5, -5), name="bill", tag="beak", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1.5, -1.5, -11, 1.5, 0.5, -9), name="bill_tip", tag="beak", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-0.5, -1, -12, 0.5, 0, -11), name="nail", tag="beak_tip")
    m.bone("jaw", "skull", (0, ay - 1.5, az - 5))
    m.box("jaw", *R(-2, -2.5, -9, 2, -1.5, -5), name="jaw", tag="beak", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-1.5, -2.5, -11, 1.5, -1.5, -9), name="jaw_tip", tag="beak", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (2.5, ay + 0.9, az - 2.6), "r": 0.9, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-2.5, ay + 0.9, az - 2.6), "r": 0.9, "side": -1},
    ]


def leg(m, side, s):
    # strong legs set far back (the foot-propelled diver), short shanks, big webbed feet
    x = 2.5 * s
    ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x,
                 [(8, 3.5), (5, 2.5), (2.5, 4.5), (1, 3)], "-y",
                 [(3, 3), (2, 2, 0.0, "limb"), (1, 1, 0.0, "limb")], overlap=(1.0, 0.5))
    by, bz = ch["end"]
    m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
    m.box(f"toes_{side}", (x - 2.5, by - 1, bz - 5), (x + 2.5, by, bz + 1), tag="web", name="web")


def pattern(model, tx, rgb, region):
    P = tx.P
    cube = tx.cube
    tag = cube.tag
    if tag == "feather":
        if cube.name == "primaries_tip":
            return tx.pal["wingtip"].copy()
        if cube.name == "primaries":
            k = (abs(P[0]) - abs(cube.frm[0])) / max(1.0, cube.size[0])
            return rgb * (1.0 - 0.3 * max(0.0, min(1.0, k)))
        if cube.name == "secondaries":
            # the speculum: a white bar along the trailing edge of the secondaries
            if P[2] > cube.to[2] - 1.6:
                return tx.pal["speculum"].copy()
            return tx.pal["feather"] * 0.92
        if cube.name == "tail_fan" and tx.face in ("up", "down") and tx.edge:
            return tx.pal["feather_edge"].copy()
        return rgb
    if tag == "skin":
        n = vnoise(P[0] / 1.5, P[1] / 1.5, P[2] / 1.5, 61)
        if cube.bone == "skull":
            # chestnut head with a dark cap from the forehead over the nape, and a pale stripe under the eye
            if tx.face != "down" and P[1] > cube.frm[1] + 3.2:
                return tx.pal["cap"].copy()
            if abs(P[1] - (cube.frm[1] + 1.6)) < 0.55 and P[2] < cube.to[2] - 0.5:
                return tx.pal["cheek"].copy()
            return tx.pal["head"] * (0.92 + 0.16 * n)
        if cube.bone == "neck1":
            if region == "dorsal":
                return tx.pal["dorsal"] * (0.92 + 0.16 * n)
            # a thin pale collar at the base of the neck
            if P[2] > cube.to[2] - 1.2:
                return tx.pal["collar"].copy()
            return tx.pal["head"] * (0.92 + 0.16 * n)
        if cube.bone == "body":
            if region == "belly":
                return tx.pal["belly"] * (0.95 + 0.1 * n)
            # flanks: buff with fine dark speckles (the scalloped feather edges of a duck)
            cell = (math.floor(P[0] / 1.5), math.floor(P[1] / 1.5), math.floor(P[2] / 1.5))
            h = hash3(*cell, 19)
            rgb = rgb * (0.9 + 0.2 * n)
            if region != "dorsal" and h > 0.78:
                rgb = tx.pal["speckle"] * (0.9 + 0.15 * n)
            elif region == "dorsal" and h > 0.7:
                rgb = tx.pal["mantle_edge"].copy()          # pale feather edges on the dark back
            return rgb
        if cube.bone == "tail":
            return rgb
    return rgb


def attack(m):
    # the nip: a lunge of the neck and a snap of the bill, with a wing slap
    m.anim("attack", 0.5, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.15, -6, 0, 0), (0.3, 4, 0, 0), (0.5, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.12, 16, 0, 0), (0.25, -26, 0, 0), (0.5, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.12, 6, 0, 0), (0.25, -10, 0, 0), (0.5, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.12, -28, 0, 0), (0.25, -32, 0, 0), (0.3, -2, 0, 0), (0.5, 0, 0, 0)])),
        "wing1_l": track(rot=keys([(0, 78, -82, -12), (0.15, 20, -30, -40), (0.35, 20, -30, -40), (0.5, 78, -82, -12)])),
        "wing1_r": track(rot=keys([(0, 78, 82, 12), (0.15, 20, 30, 40), (0.35, 20, 30, 40), (0.5, 78, 82, 12)])),
    })


def extra(m):
    # the honk (the oldest syrinx known): neck stretched up and forward, bill open, tail flicking
    m.anim("call", 1.2, False, {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.25, -32, 0, 0), (0.8, -36, 0, 0), (1.2, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.25, -14, 0, 0), (0.8, -10, 0, 0), (1.2, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.25, -26, 0, 0), (0.45, -10, 0, 0), (0.6, -26, 0, 0), (0.8, -8, 0, 0), (1.2, 0, 0, 0)])),
        "tail": track(rot=keys([(0, 0, 0, 0), (0.3, 14, 0, 0), (0.6, -6, 0, 0), (0.9, 12, 0, 0), (1.2, 0, 0, 0)])),
        "body": track(pos=keys([(0, 0, 0, 0), (0.25, 0, 0.6, 0), (0.8, 0, 0.6, 0), (1.2, 0, 0, 0)])),
    })


SPEC = dict(
    render_scale=0.25,
    palette={"dorsal": "#4e4630", "flank": "#b8a070", "belly": "#e8e0c8", "head": "#7a4a2e", "cap": "#2a2420",
             "cheek": "#e6d8b8", "collar": "#e6d8b8", "speckle": "#5a4a30", "mantle_edge": "#8a7a52",
             "limb": "#6a5a44", "limb_top": "#746448", "web": "#b87a48",
             "feather": "#5a5038", "feather_edge": "#b8a878", "wingtip": "#2c2820", "speculum": "#eee8dc",
             "beak": "#4a5058", "beak_tip": "#d8d0b8", "tooth": "#f4f0e4", "gum": "#3e3034", "mouth": "#8a4a4a",
             "eye": "#2b2420", "pupil": "#0a0808", "claw": "#3a3028"},
    sexes={"male": {"head": "#8a4a2a", "cap": "#1e1c1a", "dorsal": "#46402a", "speculum": "#f4f0e4"},
           "female": {"head": "#7a6648", "cap": "#5a4a34", "cheek": "#d8c8a4", "collar": "#c8b890",
                      "dorsal": "#5e5438", "flank": "#aa9870", "speckle": "#4e4230"}},
    pattern=pattern, body=(BODY_Y, 0), shoulder=SHOULDER,
    wing=(9, 11), vanes=(5, 6, 3),
    fold=((78, -82, -12), (-80, -6, 0)),
    body_parts=body_parts, leg=leg, attack=attack, extra_anims=extra,
    neck_rest=(-4, 0), neck_fly=(-24, 16),
    legs_fly=(-78, 24, -60),
    flap=(0.4, 44),                                        # fast duck beats
    gait={"walk": (0.7, 22), "run": (0.45, 30)},           # the waddle
    sit=dict(drop=5, thigh=60, shin=-110, foot=95, toes=-45, neck=-10, skull=8),
    ko=(85, 0.3, 0.5),
    ko_joints={"neck1": (-36, 12, 0), "skull": (26, 0, 0), "jaw": (-12, 0, 0)},
)


def build():
    return bird.build(ID, SPEC)
