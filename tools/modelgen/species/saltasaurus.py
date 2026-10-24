"""
Saltasaurus loricatus  (Late Cretaceous, Campanian-Maastrichtian; Lecho Formation, Salta, Argentina)

Reference (Wikipedia; Bonaparte & Powell 1980; Paul 2010; Chiappe et al. 1998): the "lizard from Salta, armoured",
the first sauropod found with body armour: large oval osteoderms (10-12 cm) set in a skin paved with thousands of
pea-sized ossicles. A small, stocky titanosaur of ~12 m and ~7 t with a short neck, a deep wide belly, short stout
legs and a low stance. The Auca Mahuevo nesting grounds of Patagonia, thousands of eggs in the floodplain mud, are
usually credited to saltasaurids: a herd animal that came back to the same nesting beaches.

Sauropod archetype with its own frame: short neck (3 segments), a wide low barrel, short legs, a medium tail, and
the armour: oval scutes in rows along the back and the flanks, down the neck and onto the tail, over a skin of
painted ossicles. Attack: rears and stomps. Modelled ~100 px long; SIZES scales it to 12 m. Olive-grey, dark mottling,
cream belly, bone-pale scutes; males darker with keeled, rust-tipped scutes, females browner and paler.
"""
import math
from paint import vnoise, hash3
from rig import track, keys
import sauropod

ID = "saltasaurus"


def body_parts(m):
    # a low, wide barrel: the belly nearly drags, the hips are the widest point
    m.box("body", (-10, 16, -21), (10, 33, -4), name="chest")
    m.box("body", (-12, 13, -6), (12, 33, 12), name="belly")
    m.box("body", (-11, 15, 10), (11, 33, 23), name="hips")
    m.box("body", (-7, 33, -18), (7, 35, 21), name="back")


def head(m, R, ay, az):
    # a small blunt head, high nostrils, a square muzzle of peg teeth
    m.box("skull", *R(-3, -3, -4, 3, 2, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -3, -9, 3, 0, -4), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-2, 0, -8, 2, 1, -4), name="nasal_arch")
    m.bone("jaw", "skull", (0, ay - 3, az - 1))
    m.box("jaw", *R(-2.5, -5, -9, 2.5, -3, -1), name="jaw", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3, ay + 0.5, az - 2.5), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3, ay + 0.5, az - 2.5), "r": 1.0, "side": -1},
    ]


def armor(m, neck, tail):
    # the big oval osteoderms: two rows along the back, a row on each flank, and smaller ones down the neck and tail
    for i, z in enumerate(range(-17, 22, 5)):
        for sx in (1, -1):
            x = 4 * sx if i % 2 == 0 else 5 * sx
            m.box("body", (x - 1.5, 35, z - 1.5), (x + 1.5, 36, z + 1.5), name="scute", tag="scute")
    for z in (-15, -7, 1, 9, 17):
        for sx in (1, -1):
            x0 = 10 if sx > 0 else -11
            hw = 12 if abs(z) < 7 else 11
            x0 = hw if sx > 0 else -hw - 1
            m.box("body", (x0, 25, z - 1), (x0 + 1, 27, z + 1), name="flank_scute", tag="scute",
                  paint={"axis": "+x" if sx > 0 else "-x"})
    # (the chain boxes are axis-aligned in bone space, so a scute sits on the top face at the segment's middle)
    for seg, (w, h) in zip(neck["segments"], SPEC["neck"]["sections"]):
        y0, zc = seg["unposed"]
        zm = zc - seg["len"] / 2.0
        m.box(seg["bone"], (-1, y0 + h / 2, zm - 1), (1, y0 + h / 2 + 1, zm + 1), name="neck_scute", tag="scute")
    for seg, (w, h) in list(zip(tail["segments"], SPEC["tail"]["sections"]))[:3]:
        y0, zc = seg["unposed"]
        zm = zc + seg["len"] / 2.0
        m.box(seg["bone"], (-1, y0 + h / 2, zm - 1), (1, y0 + h / 2 + 1, zm + 1), name="tail_scute", tag="scute")
    # the males' scutes carry a keel: a taller ridge down the midline
    m.bone("male_display", "body", (0, 35, 0))
    for z in range(-14, 20, 5):
        m.box("male_display", (-1, 36, z - 1), (1, 37, z + 1), name="keel", tag="keel")


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "scute":
        col = tx.pal["scute"] * (1.1 if tx.face in ("up", "east", "west") else 0.85)
        if tx.edge:
            col = col * 0.8
        return col
    if tag == "keel":
        return tx.pal["keel"].copy()
    if tag == "skin":
        # the ossicle pavement: a pebble per pixel, each a little lighter or darker, some standing out pale
        c = hash3(math.floor(P[0]), math.floor(P[1]), math.floor(P[2]), 43)
        rgb = rgb * (0.88 + 0.22 * c)
        if c > 0.93 and region != "belly":
            rgb = rgb * 0.5 + tx.pal["ossicle"] * 0.5
        n = vnoise(P[0] / 5.0, P[1] / 5.0, P[2] / 5.0, 47)
        if region in ("dorsal", "flank") and n > 0.62:
            rgb = tx.pal["mottle"] * (0.9 + 0.2 * c)            # dark blotches over the back and flanks
    return rgb


def stomp(m, necks, tails):
    # rears onto the hind legs, the forefeet paw the air, then the whole weight comes down: the armoured tank's stomp
    t = {"body": track(rot=keys([(0, 0, 0, 0), (0.45, 18, 0, 0), (0.7, -3, 0, 0), (1.2, 0, 0, 0)]),
                       pos=keys([(0, 0, 0, 0), (0.45, 0, 3.5, 2), (0.7, 0, -1.5, -1), (1.2, 0, 0, 0)])),
         "neck1": track(rot=keys([(0, 0, 0, 0), (0.45, -12, 0, 0), (0.7, 6, 0, 0), (1.2, 0, 0, 0)])),
         "skull": track(rot=keys([(0, 0, 0, 0), (0.45, -6, 0, 0), (0.7, 6, 0, 0), (1.2, 0, 0, 0)])),
         "jaw": track(rot=keys([(0, 0, 0, 0), (0.4, -16, 0, 0), (0.75, -4, 0, 0), (1.2, 0, 0, 0)]))}
    for side in ("l", "r"):
        t[f"upperarm_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.45, -42, 0, 0), (0.7, 8, 0, 0), (1.2, 0, 0, 0)]))
        t[f"forearm_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.45, 48, 0, 0), (0.7, 0, 0, 0), (1.2, 0, 0, 0)]))
        t[f"thigh_{side}"] = track(rot=keys([(0, 0, 0, 0), (0.45, -14, 0, 0), (0.7, 2, 0, 0), (1.2, 0, 0, 0)]))
    for i, b in enumerate(tails):
        t[b] = track(rot=keys([(0, 0, 0, 0), (0.45, -9 - 2 * i, 0, 0), (0.7, 3, 0, 0), (1.2, 0, 0, 0)]))
    m.anim("attack", 1.2, False, t)


SPEC = dict(
    palette={"dorsal": "#5e6450", "flank": "#7e8468", "belly": "#d4ccae", "mottle": "#3e4434",
             "scute": "#c8bc9c", "keel": "#9a5a3a", "ossicle": "#b8b49c",
             "limb": "#6a6e58", "limb_top": "#767a62",
             "claw": "#3a3630", "claw_base": "#3a3630",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
             "eye": "#b08a30", "pupil": "#140f0a", "saddle": "#7a4f2e"},
    sexes={"male": {"dorsal": "#4e5442", "flank": "#6e745a", "mottle": "#2e3428", "scute": "#d0c4a4", "keel": "#a85a30"},
           "female": {"dorsal": "#6e6c54", "flank": "#8e8a6e", "mottle": "#4e4c3c", "scute": "#bcb094", "ossicle": "#c4c0a8"}},
    pattern=pattern, body=(28, 8), body_parts=body_parts, head=head, armor=armor,
    neck=dict(points=[(30, -19), (34, -27), (37, -34), (39, -40)], sections=[(9, 9), (7, 7), (6, 6)], tilt=10),
    front=dict(x=8, pts=[(22, -14), (12, -13), (2, -14)], secs=[(7, 8, 0.0), (6, 6, 0.0, "limb")], pad=(7, 3, 2)),
    hind=dict(x=9, pts=[(24, 16), (13, 17), (4, 16), (2, 16)], secs=[(9, 10, 0.0), (7, 7, 0.5, "limb"), (6, 6, 0.0, "limb")], pad=(8, 4, 2)),
    tail=dict(points=[(25, 22), (23, 32), (20, 41), (17, 49), (15, 56)], sections=[(10, 10), (7, 7), (5, 5), (3, 3)]),
    saddle=(35, -12, -2, 13, 12, 7),
    gait=dict(walk=(2.0, 15, 15, 0.5), run=(1.1, 22, 22, 0.9)),
    attack=stomp,
    sit_drop=10, sit_kw={"neck": -8}, graze=(-14, -12),
    ko=dict(lift=0.5),
)


def build():
    return sauropod.build(ID, SPEC)
