"""
Ichthyornis dispar  (Late Cretaceous, Niobrara Chalk, Kansas; Western Interior Seaway)

Reference (Wikipedia; Marsh 1880; Clarke 2004; Field et al. 2018): a tern-sized seabird (~60 cm wingspan,
~25 cm body) that still carried TEETH on the back half of its jaws, behind a small horny beak at the tip; long,
narrow, strongly keeled wings built for fast flight over the sea; a short tail fan on a pygostyle; legs set far
back with webbed feet, fishing by plunge-diving. Behaviourally the mod treats it like a gull that follows the
player: it lands on the shoulder and brings fish.

Modelled at 4x (render_scale 0.25) so the feathers and teeth keep some texture: wingspan 42 px -> 0.66 m in the
world. Colours: white below, grey mantle, black cap and wingtips (tern style); males carry a cleaner black cap,
females a browner, mottled mantle.
"""
import math
from rig import track, keys
import bird

ID = "ichthyornis"
BODY_Y = 10.5
SHOULDER = (3.5, 12.5, -3)


def body_parts(m):
    # streamlined torso with a deep breast keel, rump narrowing to the tail; carried low on short legs
    m.box("body", (-3, 7.5, -6), (3, 13.5, 6), name="torso")
    m.box("body", (-2, 5.5, -6), (2, 7.5, 1), name="breast")
    m.box("body", (-2, 8.5, 6), (2, 11.5, 9), name="rump")
    m.bone("tail", "body", (0, 10.5, 8))
    m.box("tail", (-3, 9.5, 8), (3, 10.5, 14), name="tail_fan", tag="feather")
    m.box("tail", (-1, 10, 14), (1, 11, 16), name="tail_streamers", tag="feather")

    # short S-neck carried forward, head a little above the back
    neck = m.chain(["neck1"], "body", 0, [(11.5, -5), (16.5, -9)], "-z", [(3, 3)], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck1", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-neck["abs"] + 4, 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)
    teeth = {"edge": "bottom", "rows": 1, "faces": ("east", "west"), "freq": 1.0}
    # rounded cranium; the rear half of the jaws carries small teeth, the front half is a slim horny beak with a hook
    m.box("skull", *R(-2, -1.5, -5, 2, 2.5, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-1, -1.5, -8, 1, 1.5, -5), name="beak_rear", tag="beak", paint={"faces": {"down": "mouth"}, "teeth": teeth})
    m.box("skull", *R(-1, -1.5, -11, 1, 0.5, -8), name="beak", tag="beak", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-0.5, -1.5, -13, 0.5, 0.5, -11), name="beak_tip", tag="beak_tip")
    m.bone("jaw", "skull", (0, ay - 1.5, az - 4))
    m.box("jaw", *R(-1, -2.5, -8, 1, -1.5, -4), name="jaw_rear", tag="beak",
          paint={"faces": {"up": "mouth"}, "teeth": dict(teeth, edge="top")})
    m.box("jaw", *R(-1, -2.5, -12, 1, -1.5, -8), name="jaw", tag="beak", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-0.5, -2.5, -13, 0.5, -1.5, -12), name="jaw_tip", tag="beak_tip")
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (2, ay + 0.8, az - 2.8), "r": 0.9, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-2, ay + 0.8, az - 2.8), "r": 0.9, "side": -1},
    ]


def leg(m, side, s):
    # short legs set far back (a foot-propelled swimmer), thin shanks, broad webbed feet
    x = 2.0 * s
    ch = m.chain([f"thigh_{side}", f"shin_{side}", f"foot_{side}"], "root", x,
                 [(8.5, 3), (5.5, 1.5), (2.5, 4), (1, 2.5)], "-y",
                 [(2, 2), (1, 1, 0.0, "limb"), (1, 1, 0.0, "limb")], overlap=(1.0, 0.5))
    by, bz = ch["end"]
    m.bone(f"toes_{side}", f"foot_{side}", (x, by, bz), (-ch["abs"], 0, 0))
    m.box(f"toes_{side}", (x - 2, by - 1, bz - 4), (x + 2, by, bz + 1), tag="web", name="web")


def pattern(model, tx, rgb, region):
    P = tx.P
    cube = tx.cube
    tag = cube.tag
    if tag == "feather":
        if cube.name in ("primaries_tip",):
            return tx.pal["wingtip"].copy()
        if cube.name == "primaries":
            # outer primaries darken toward the tip of the hand
            k = (abs(P[0]) - abs(cube.frm[0])) / max(1.0, cube.size[0])
            return rgb * (1.0 - 0.35 * max(0.0, min(1.0, k)))
        if cube.name == "tail_streamers":
            return tx.pal["wingtip"].copy()
        if cube.name == "tail_fan" and tx.face in ("up", "down") and tx.edge:
            return tx.pal["feather_edge"].copy()
        return rgb
    if tag == "skin":
        if cube.bone == "skull":
            # black cap down to the eye line, white throat and cheeks
            if tx.face != "down" and P[1] > cube.frm[1] + 2.0:
                return tx.pal["cap"].copy()
            return tx.pal["belly"].copy()
        if cube.bone == "neck1":
            return tx.pal["belly"].copy() if region != "dorsal" else tx.pal["dorsal"].copy()
        if region == "dorsal" and math.sin(P[0] * 2.3) * math.sin(P[2] * 1.7 + P[0]) > 0.7:
            rgb = rgb * 0.9                                    # faint mantle mottling
    return rgb


def attack(m):
    # stab: a quick lunge of the head and a snap of the toothed jaws
    m.anim("attack", 0.5, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.15, -8, 0, 0), (0.3, 4, 0, 0), (0.5, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.12, 18, 0, 0), (0.25, -28, 0, 0), (0.5, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.12, 6, 0, 0), (0.25, -12, 0, 0), (0.5, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.12, -32, 0, 0), (0.25, -36, 0, 0), (0.3, -2, 0, 0), (0.5, 0, 0, 0)])),
    })


SPEC = dict(
    render_scale=0.25,
    palette={"dorsal": "#9aa1a6", "flank": "#c9cdcf", "belly": "#f1f0ea", "cap": "#1c1c1e",
             "limb": "#3a3236", "limb_top": "#4a4044", "web": "#4d3a3c",
             "feather": "#8e959a", "feather_edge": "#f1f0ea", "wingtip": "#22232a",
             "beak": "#55585c", "beak_tip": "#2a2b2e", "tooth": "#f4f0e4", "gum": "#3e3034", "mouth": "#8a3f4a",
             "eye": "#2b2420", "pupil": "#0a0808", "claw": "#2a2b2e"},
    sexes={"male": {"cap": "#101012", "dorsal": "#8f979d", "wingtip": "#15161a"},
           "female": {"cap": "#3a3430", "dorsal": "#a39e94", "feather": "#9a948a", "flank": "#cdc8be"}},
    pattern=pattern, body=(BODY_Y, 0), shoulder=SHOULDER,
    wing=(8, 10), vanes=(5, 6, 3),
    # folded: humerus+forearm back along the flank, vane hanging down over the side, primaries crossing over the tail
    fold=((78, -82, -12), (-80, -6, 0)),
    body_parts=body_parts, leg=leg, attack=attack,
    neck_rest=(-6, 2), neck_fly=(-28, 20),
    legs_fly=(-80, 21, -60),                               # legs trailing under the tail
    flap=(0.45, 42),                                       # quick tern beats
    gait={"walk": (0.6, 24), "run": (0.4, 34)},
    sit=dict(drop=6, thigh=63, shin=-113, foot=95, toes=-45, neck=-14, skull=10),   # on its breast, feet tucked
    ko=(85, 0.3, 0.5),
    ko_joints={"neck1": (-40, 14, 0), "skull": (30, 0, 0), "jaw": (-14, 0, 0)},
)


def build():
    return bird.build(ID, SPEC)
