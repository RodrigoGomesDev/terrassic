"""
Enchodus  (Late Cretaceous to Eocene, worldwide; Niobrara, Pierre Shale, Hell Creek estuaries)

Reference (Wikipedia; Goody 1976; Everhart 2005; Cavin et al. 2012; Nelson, Fishes of the World): the
"sabre-toothed herring", an aulopiform (a cousin of the lizardfish, not a herring). A slender, slightly compressed
body, naked of scales except for rows of bony scutes (one along the back ahead of the dorsal fin, one along the
flank); a big head a quarter of the body with a huge orbit; enormous fangs, a pair on the palatines hanging from
the roof of the mouth and a pair at the tip of the lower jaw that stood up outside the upper lip when the mouth
closed; a tall dorsal fin a little ahead of mid-body, a small fleshy adipose fin behind it (the aulopiform mark),
abdominal pelvic fins, an anal fin set back and a deeply forked tail. Most species 0.5-1 m (E. petrosus 1.5 m);
the commonest fish of the Cretaceous seas, food for Xiphactinus, mosasaurs, Hesperornis and plesiosaurs, and a
bold little predator itself.

Fish rig (fish.py) modelled large (render_scale 0.2): ~96 px from the jaw tip to the fork, SIZES scales it to
0.8 m. In game: the sea food fish of the Terrassic world, the cod's seat; schools near the coast, snaps at squid and
small fish. Deep teal back with a dark reticulation, a thin gold line above mirror-silver naked flanks, the scute
row along the lateral line, a white belly, a silver gill cover with a dark spot, dusky-tipped grey-teal fins and a
gold eye; males a deeper teal with a dark eye stripe, females greener.
"""
import math
from paint import vnoise
from rig import track, keys
from fish import build_fish, paint_eye

ID = "enchodus"


def body(m):
    # a slender compressed torso, rounded by a narrower back and belly layer and a keel below
    m.box("body", (-4, 8, -14), (4, 20, 8), name="torso")
    m.box("body", (-3, 20, -13), (3, 22, 7), name="back")
    m.box("body", (-2, 22, -10), (2, 23, 4), name="ridge")
    m.box("body", (-3, 6, -13), (3, 8, 7), name="belly")
    m.box("body", (-2, 5, -10), (2, 6, 5), name="keel")
    # the dorsal scutes ahead of the fin
    for y, z in ((22, -13), (23, -10)):
        m.box("body", (-1, y, z), (1, y + 1, z + 2), tag="scute", name="scute")


def neck(m):
    # the shoulder girdle behind the gill covers
    m.box("neck", (-4, 8, -20), (4, 20, -14), name="shoulder")
    m.box("neck", (-3, 20, -20), (3, 21, -14), name="shoulder_top")
    m.box("neck", (-3, 7, -20), (3, 8, -14), name="shoulder_low")
    m.box("neck", (-1, 21, -18), (1, 22, -16), tag="scute", name="scute")


def head(m):
    # the big head: a tall cranium with the huge orbit, a pointed snout stepping down to the premaxilla
    m.box("skull", (-3.5, 9, -30), (3.5, 20, -20), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", (-2.5, 20, -29), (2.5, 21, -21), name="frontal")
    m.box("skull", (-2.5, 13, -38), (2.5, 18, -30), name="snout",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1, "freq": 0.9}})
    m.box("skull", (-1.5, 18, -36), (1.5, 19, -30), name="snout_top")
    m.box("skull", (-1.5, 13, -42), (1.5, 16, -38), name="premaxilla",
          paint={"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1, "freq": 1.0}})

    def sides(side, s):
        def X(a, b):
            return (min(a * s, b * s), max(a * s, b * s))
        x0, x1 = X(2.5, 3.5)
        # the maxilla: the long upper-lip bone along the side of the snout, toothed along its edge
        m.box("skull", (x0, 12, -37), (x1, 14, -25), tag="maxilla", name="maxilla",
              paint={"teeth": {"edge": "bottom", "rows": 1, "freq": 1.0, "faces": ("east", "west")}})
        # the sabre fangs of the palatine, hanging from the roof of the mouth, and a smaller pair behind
        x0, x1 = X(1, 2)
        m.box("skull", (x0, 9, -37), (x1, 13, -36), tag="tooth_cube", name="fang", paint={"axis": "-y"})
        m.box("skull", (x0, 11, -33), (x1, 13, -32), tag="tooth_cube", name="fang", paint={"axis": "-y"})
        # the dentary fangs at the jaw tip, standing up outside the upper lip
        x0, x1 = X(1.5, 2.5)
        m.box("jaw", (x0, 12, -42), (x1, 17, -41), tag="tooth_cube", name="fang_low", paint={"axis": "+y"})
    m.sym(sides)

    # the lower jaw: a deep dentary, a narrow chin and the throat (branchiostegals)
    m.box("jaw", (-3, 9, -38), (3, 12, -22), name="jaw", paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1, "freq": 0.9}})
    m.box("jaw", (-2, 9, -42), (2, 12, -38), name="dentary", paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1, "freq": 1.0}})
    m.box("jaw", (-2, 8, -38), (2, 9, -30), name="chin")
    m.box("jaw", (-2.5, 8, -30), (2.5, 9, -22), tag="throat", name="gular")
    m.decals += [
        {"kind": "spot", "bones": ["skull"], "pos": (2.5, 17, -36), "r": 0.5, "color": "pupil", "side": 1},
        {"kind": "spot", "bones": ["skull"], "pos": (-2.5, 17, -36), "r": 0.5, "color": "pupil", "side": -1},
    ]


def tail_layers(m, segs):
    # the back and belly layers carried down the first two tail bones, and the adipose and anal fins
    for k, (top, bot) in ((1, (3, 3)), (2, (2, 2))):
        sg = segs[k - 1]
        y0, z0 = sg["unposed"]
        L = int(round(sg["len"]))
        w, h = (5, 4) if k == 1 else (3, 2)
        hh = {1: 5.5, 2: 4.0}[k]
        m.box(f"tail{k}", (-w / 2, y0 + hh, z0), (w / 2, y0 + hh + 1, z0 + L), name="tail_ridge")
        m.box(f"tail{k}", (-w / 2, y0 - hh - 1, z0), (w / 2, y0 - hh, z0 + L), name="tail_keel")
    y0, z0 = segs[0]["unposed"]
    m.box("tail1", (-0.5, y0 + 6.5, z0 + 3), (0.5, y0 + 8.5, z0 + 7), tag="fin", name="adipose")
    m.box("tail1", (-0.5, y0 - 9.5, z0 + 1), (0.5, y0 - 6.5, z0 + 8), tag="fin", name="anal")
    m.box("tail1", (-0.5, y0 - 11.5, z0 + 2), (0.5, y0 - 9.5, z0 + 6), tag="fin", name="anal")


def caudal(m, ey, ez):
    # deeply forked: the hypural plate, then each lobe a long outer blade, a shorter inner one and a thin tip
    m.box("caudal", (-0.5, ey - 3, ez - 2), (0.5, ey + 3, ez + 2), tag="fin", name="hypural")
    for s in (1, -1):
        y = ey + 1.5 * s
        m.box("caudal", (-0.5, y - 2.5, ez - 1), (0.5, y + 2.5, ez + 14), tag="fin", name="lobe",
              rot=(36 * s, 0, 0), origin=(0, y, ez))
        m.box("caudal", (-0.5, y - 2, ez - 1), (0.5, y + 2, ez + 9), tag="fin", name="lobe_inner",
              rot=(18 * s, 0, 0), origin=(0, y, ez))
        m.box("caudal", (-0.5, y + 0.5 * s - 1, ez + 13), (0.5, y + 0.5 * s + 1, ez + 18), tag="fin", name="lobe_tip",
              rot=(36 * s, 0, 0), origin=(0, y, ez))


FINS = [
    # long pointed pectorals low behind the gill cover
    # long pointed pectorals low behind the gill cover, swept back along the flank
    dict(name="pectoral", parent="body", pivot=(4, 10, -13), rot=(0, 24, -12), sym=True, flap=("y", 12, 0.0),
         boxes=[((4, 7, -13), (5, 11, -5), "pectoral"), ((4, 7, -5), (5, 9, -1), "pectoral_tip")]),
    # abdominal pelvic fins
    dict(name="pelvic", parent="body", pivot=(2.5, 6, -1), rot=(0, 14, -28), sym=True, flap=("z", 9, -0.3),
         boxes=[((2.5, 3, -1), (3.5, 6, 5), "pelvic"), ((2.5, 3, 5), (3.5, 5, 8), "pelvic_tip")]),
    # the tall dorsal fin, raked back, a little ahead of mid-body
    dict(name="dorsal", parent="body", pivot=(0, 23, -6), sym=False, flap=("z", 5, 0.2),
         boxes=[((-0.5, 23, -9), (0.5, 25, 1), "dorsal"), ((-0.5, 25, -7), (0.5, 27, -1), "dorsal"),
                ((-0.5, 27, -5), (0.5, 30, -2), "dorsal"), ((-0.5, 30, -4), (0.5, 32, -2), "dorsal"),
                ((-0.5, 32, -3), (0.5, 34, -2), "dorsal_tip")]),
]


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    name = tx.cube.name
    n = vnoise(P[0] / 1.4, P[1] / 1.4, P[2] / 1.4, 97)
    if tag == "fin":
        col = tx.pal["fin"].copy()
        # rays every other pixel along the fin, the membrane between them a shade darker
        ray = P[2] if name not in ("pectoral", "pectoral_tip", "pelvic", "pelvic_tip") else P[1] + P[2] * 0.5
        if int(math.floor(ray * 1.0)) % 2 == 0:
            col = col * 1.08
        else:
            col = col * 0.9
        # dusky distal margin
        if name in ("dorsal_tip", "lobe_tip", "pectoral_tip", "pelvic_tip") or (name == "dorsal" and tx.cy > 0.7) \
                or (name in ("lobe", "anal") and tx.edge):
            col = tx.pal["fin_dusk"] * (0.95 + 0.1 * n)
        if name == "adipose":
            col = tx.pal["dorsal"] * (0.9 + 0.2 * n)
        if name == "hypural":
            col = tx.pal["fin"] * 0.85
        return col
    if tag == "scute":
        col = tx.pal["scute"] * (0.9 + 0.2 * n)
        if tx.edge:
            col = col * 0.8
        return col
    if tag == "gill_cover":
        # silver gill cover with fine radial striae and the dark opercular spot at its upper rear corner
        col = tx.pal["flank"] * (1.05 + 0.08 * math.sin(P[1] * 2.2 + P[2] * 1.4))
        if tx.cy > 0.62 and P[2] > tx.cube.frm[2] + 2.0:
            col = tx.pal["gill"].copy()
        if tx.cy < 0.25:
            col = col * 0.92
        if tx.edge and P[2] > tx.cube.to[2] - 1:
            col = col * 0.7   # the gill slit behind it
        return col
    if tag == "maxilla":
        return tx.pal["maxilla"] * (0.92 + 0.16 * n)
    if tag == "throat":
        return tx.pal["belly"] * 0.94
    if tag == "skin":
        e = paint_eye(tx, rgb, (16.0, -27.0), 2.4, 1.3, 3.5)   # the huge orbit
        if e is not None:
            return e
        if region == "dorsal":
            # deep teal back with a fine dark reticulation
            if vnoise(P[0] / 0.9, P[1] / 0.9, P[2] / 0.9, 101) > 0.68:
                rgb = rgb * 0.78
            if tx.face != "up" and tx.cy < 0.7:
                rgb = tx.pal["gold"] * (0.95 + 0.1 * n)   # the thin gold line between back and flank
        elif region == "flank":
            # naked mirror-silver flank: vertical sheen bands, the lateral line and its scutes
            rgb = rgb * (0.96 + 0.08 * math.sin(P[2] * 0.9 + n * 2.0))
            on_body = tx.cube.bone in ("body", "neck", "tail1", "tail2", "tail3", "tail4")
            if on_body and abs(P[1] - 14.0) < 0.6:
                rgb = tx.pal["scute"].copy() if int(math.floor(P[2] / 2.0)) % 2 == 0 else rgb * 0.82
        elif region == "belly":
            rgb = rgb * (0.97 + 0.06 * n)
        if tx.cube.bone == "skull":
            if tx.face == "up" or tx.cube.name in ("frontal", "snout_top"):
                rgb = tx.pal["dorsal"] * (0.9 + 0.15 * n)
            # the eye stripe of the males (a darker band through the eye to the snout)
            if tx.face in ("east", "west") and abs(P[1] - 16.5) < 0.6 and P[2] < -22:
                rgb = tx.pal["stripe"].copy()
    return rgb


def attack(m):
    # the strike: a tail flick shoots it forward, the jaws gape wide on the fangs, the gill covers flare
    m.anim("attack", 0.5, False, {
        "body": track(pos=keys([(0, 0, 0, 0), (0.12, 0, 0, 2), (0.25, 0, 0, -5), (0.5, 0, 0, 0)]),
                      rot=keys([(0, 0, 0, 0), (0.12, 4, 0, 0), (0.25, 1, 0, 0), (0.5, 0, 0, 0)])),
        "neck": track(rot=keys([(0, 0, 0, 0), (0.12, 14, 0, 0), (0.25, -2, 0, 0), (0.5, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.12, 8, 0, 0), (0.25, 0, 0, 0), (0.5, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.12, -38, 0, 0), (0.2, -40, 0, 0), (0.26, 0, 0, 0), (0.5, 0, 0, 0)])),
        "operculum_l": track(rot=keys([(0, 0, 0, 0), (0.12, 0, 24, 0), (0.3, 0, 0, 0), (0.5, 0, 0, 0)])),
        "operculum_r": track(rot=keys([(0, 0, 0, 0), (0.12, 0, -24, 0), (0.3, 0, 0, 0), (0.5, 0, 0, 0)])),
        "pectoral_l": track(rot=keys([(0, 0, 0, 0), (0.1, 0, 30, 0), (0.3, 0, 0, 0), (0.5, 0, 0, 0)])),
        "pectoral_r": track(rot=keys([(0, 0, 0, 0), (0.1, 0, -30, 0), (0.3, 0, 0, 0), (0.5, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.08, 0, 18, 0), (0.25, 0, -14, 0), (0.5, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.1, 0, 22, 0), (0.27, 0, -18, 0), (0.5, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.12, 0, 26, 0), (0.3, 0, -22, 0), (0.5, 0, 0, 0)])),
        "tail4": track(rot=keys([(0, 0, 0, 0), (0.14, 0, 28, 0), (0.32, 0, -24, 0), (0.5, 0, 0, 0)])),
    })


LIMP = {"neck": (2, 0, 0), "jaw": (-14, 0, 0), "operculum_l": (0, 14, 0), "operculum_r": (0, -14, 0),
        "tail1": (-3, 0, 0), "tail2": (-5, 0, 0), "tail3": (-6, 0, 0), "tail4": (-6, 0, 0),
        "pectoral_l": (0, -20, 10), "pectoral_r": (0, 20, -10), "pelvic_l": (0, -10, 20), "pelvic_r": (0, 10, -20),
        "dorsal": (0, 0, 25)}

S = dict(
    render_scale=0.2,
    palette={"dorsal": "#2f5e66", "flank": "#c4cec8", "belly": "#f0f2ec", "gill": "#3a4e56", "stripe": "#1c2a30",
             "gold": "#c8a850", "scute": "#dfe6de", "maxilla": "#9c9078",
             "limb": "#2f5e66", "limb_top": "#3c6e76", "claw": "#dfe6de",
             "fin": "#6e8a88", "fin_dusk": "#36484c",
             "tooth": "#f6f2e6", "mouth": "#8a3844", "gum": "#5e262e",
             "tooth_cube": "#f6f2e6", "tooth_cube_base": "#dad4c2", "tooth_cube_tip": "#fcfaf2",
             "eye": "#e0b848", "eye_shine": "#fff6d8", "pupil": "#0f0c0a"},
    sexes={"male": {"dorsal": "#24525e", "stripe": "#121c20"},
           "female": {"dorsal": "#3e6a5c", "flank": "#c8d0c4", "stripe": "#4c6064"}},
    pattern=pattern,
    body_pivot=(14, 0), body=body,
    neck_pivot=(14, -14), neck=neck,
    head_pivot=(14, -20), jaw_pivot=(12, -22), head=head,
    operculum=dict(pivot=(3.5, 14, -24), boxes=[((3.5, 9, -24), (4.5, 19, -20), "operculum"),
                                                 ((3.5, 8, -23), (4.5, 9, -20), "subopercle")]),
    tail=dict(points=[(14, 8), (14, 16), (14, 24), (14, 31), (14, 36)],
              sections=[(7, 11), (5, 8), (4, 5), (3, 3)], layers=tail_layers),
    caudal=caudal,
    fins=FINS,
    swim=dict(idle=(2.0, 8, 2.0, 0.7), walk=(1.0, 16, 2.5, 1.0), run=(0.5, 24, 3.0, 1.4), sit=(3.0, 5, 1.0, 0.4)),
    breathe=(12, 4),
    attack=attack,
    ko=dict(roll=85, lift=0.3, shift=0.5, joints=LIMP, neck_down=-8),
)


def build():
    return build_fish(ID, S)
