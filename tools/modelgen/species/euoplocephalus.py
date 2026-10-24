"""
Euoplocephalus tutus  (Late Cretaceous, Campanian; Dinosaur Park and Horseshoe Canyon formations, Alberta)

Reference (Wikipedia; Lambe 1902; Arbour & Currie 2013; Paul 2010): an ankylosaurid of 5.5-6 m and ~2.5 t, one of
the best known armoured dinosaurs (over 40 specimens). A very wide, low body on short stout legs; a short neck
guarded by two bony half-rings of keeled plates (the cervical half-rings); the back covered in transverse bands of
small keeled osteoderms, with only short triangular plates along the flanks (no long spikes like the Ankylosaurus);
a broad flat skull with four short pyramidal horns at its back corners, a looping nasal passage, a horny beak and
BONY EYELIDS (palpebrals) that could shut over the eyes like shutters; a tail stiffened into a handle for a
knob-like club, smaller than the Ankylosaurus's.

Built on the ankylosaur archetype with its own body armour, skull and club. Modelled ~70 px long; SIZES scales it
to 6 m. Olive and khaki with slate armour bands and rust keels on the plates; males darker with brick-red keels,
females greyer with bone-coloured keels.
"""
import math
from paint import vnoise, hash3
from rig import track, keys
import ankylosaur

ID = "euoplocephalus"
BODY_Y = 12


def body_parts(m):
    # very wide, very low: the trunk is twice as wide as it is tall
    m.box("body", (-10, 5, -11), (10, 14, 11), name="trunk")
    m.box("body", (-8, 6, -14), (8, 13, -11), name="chest")
    m.box("body", (-8, 4, -8), (8, 5, 8), name="belly")
    m.box("body", (-9, 14, -10), (9, 16, 10), name="shield", tag="armor")


def armor(m, neck, tail):
    # transverse bands of armour across the back, each carrying a row of keeled plates (the middle pair taller)
    for z in (-8, -4, 0, 4, 8):
        m.box("body", (-9, 16, z - 1), (9, 17, z + 1), name="band", tag="armor")
        for x in (-6, -2, 2, 6):
            top = 19 if abs(x) == 2 else 18
            m.box("body", (x - 1, 17, z - 1), (x + 1, top, z + 1), name="keel", tag="scute")
    # short triangular plates along the flanks
    for z in (-7, -3, 1, 5, 9):
        for sx in (1, -1):
            x0 = 10 if sx > 0 else -11
            m.box("body", (x0, 11, z - 1), (x0 + 1, 13, z + 1), name="flank_plate", tag="spike",
                  paint={"axis": "+x" if sx > 0 else "-x"})
    # cervical half-rings: two collars of fused plates round the neck, each with three keels on top
    for i, seg in enumerate(neck["segments"]):
        y0, z0 = seg["unposed"]
        zc = z0 - seg["len"] / 2
        hw = 5.5 if i == 0 else 5
        m.box(seg["bone"], (-hw, y0 - 2.5, zc - 1.5), (hw, y0 + 4.5, zc + 1.5), name="half_ring", tag="armor")
        for x in (-3, 0, 3):
            m.box(seg["bone"], (x - 0.5, y0 + 4.5, zc - 1), (x + 0.5, y0 + 5.5, zc + 1), name="ring_keel", tag="scute")
    # the tail base: a pair of side plates and two keels on top
    seg = tail["segments"][0]
    ty, tz = seg["unposed"]
    for sx in (1, -1):
        x0 = 4 if sx > 0 else -5
        m.box("tail1", (x0, ty + 1, tz + 2), (x0 + 1, ty + 3, tz + 4), name="tail_plate", tag="spike",
              paint={"axis": "+x" if sx > 0 else "-x"})
    for z in (tz + 2, tz + 6):
        m.box("tail1", (-1, ty + 3.5, z - 1), (1, ty + 4.5, z + 1), name="tail_keel", tag="scute")


def head(m, R, ay, az):
    # broad, flat, armoured skull roof; a short snout ending in the horny beak
    m.box("skull", *R(-5.5, -3, -6, 5.5, 2, 1), name="cranium", tag="armor", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-4, -3, -10, 4, 1, -6), name="face", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(-3, -3, -12, 3, -1, -10), name="beak", tag="beak")
    for sx in (1, -1):
        x = 5.5 * sx
        # squamosal horns at the back corners, raked back; quadratojugal horns on the cheeks, pointing down
        m.box("skull", (x - 1, ay + 1, az - 1), (x + 1, ay + 3, az + 2), name="squamosal_horn", tag="horn",
              rot=(-35, 0, 0), origin=(x, ay + 1, az + 0.5), paint={"axis": "+z"})
        m.box("skull", (5 * sx - 0.5, ay - 5, az - 4), (5 * sx + 0.5, ay - 3, az - 2), name="cheek_horn", tag="horn",
              paint={"axis": "-y"})
        # the bony eyelid: a shutter of armour over each eye
        x0 = 5.5 if sx > 0 else -6.5
        m.box("skull", (x0, ay + 0.5, az - 5.5), (x0 + 1, ay + 1.5, az - 2.5), name="eyelid", tag="armor")
    m.bone("jaw", "skull", (0, ay - 3, az - 4))
    m.box("jaw", *R(-3.5, -5, -11, 3.5, -3, -3), name="jaw", paint={"faces": {"up": "mouth"}})
    m.box("jaw", *R(-2.5, -5, -12, 2.5, -3, -11), name="lower_beak", tag="beak")
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (5.5, ay + 0.2, az - 4.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-5.5, ay + 0.2, az - 4.0), "r": 1.0, "side": -1},
    ]


def club(m, tails, tail):
    t3 = tail["segments"][2]
    y0, z0 = t3["unposed"]
    ze = z0 + t3["len"]
    # a rounded knob, smaller than the Ankylosaurus's, with a small lobe each side
    m.box("tail3", (-2.5, y0 - 2, ze - 3), (2.5, y0 + 2, ze + 1), name="club", tag="club")
    m.box("tail3", (-3.5, y0 - 1.5, ze - 2), (-2.5, y0 + 1.5, ze), name="club_lobe", tag="club")
    m.box("tail3", (2.5, y0 - 1.5, ze - 2), (3.5, y0 + 1.5, ze), name="club_lobe", tag="club")


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag in ("armor", "club"):
        # a mosaic of small polygonal ossicles between the big plates
        n = vnoise(P[0] / 1.5, P[1] / 1.5, P[2] / 1.5, 23)
        rgb = rgb * (0.86 + 0.28 * n)
        if tx.edge:
            rgb = rgb * 0.82
        return rgb
    if tag == "scute":
        col = tx.pal["scute"].copy()
        if tx.face == "up":
            col = col * 1.12                                   # the keel catches the light
        elif tx.face in ("north", "south"):
            col = col * 0.9
        return col
    if tag == "skin":
        n = vnoise(P[0] / 3.0, P[1] / 3.0, P[2] / 3.0, 31)
        rgb = rgb * (0.9 + 0.18 * n)
        if region == "flank" and math.sin(P[2] * 0.7 + P[1] * 0.4) * math.sin(P[1] * 0.9 - P[0] * 0.3) > 0.5:
            rgb = tx.pal["blotch"].copy()                      # dark blotches down the flanks
        if hash3(math.floor(P[0] / 2), math.floor(P[1] / 2), math.floor(P[2] / 2), 11) > 0.93 and region != "belly":
            rgb = rgb * 1.14                                   # scattered pebble scales
    return rgb


def attack(m, tails):
    # the club: the hips swing round, the tail coils to one side and whips through, then holds a beat on the far side
    m.anim("attack", 1.1, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.35, 0, 14, 0), (0.55, 0, -20, 0), (0.7, 0, -18, 0), (1.1, 0, 0, 0)]),
                      pos=keys([(0, 0, 0, 0), (0.35, 0, 0.5, 0), (0.55, 0, -0.5, 0), (1.1, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.35, 0, -10, 0), (0.55, 0, 12, 0), (0.7, 0, 10, 0), (1.1, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.35, -3, 18, 0), (0.55, -3, -30, 0), (0.7, -2, -28, 0), (1.1, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.38, -3, 22, 0), (0.56, -3, -40, 0), (0.7, -2, -36, 0), (1.1, 0, 0, 0)])),
        "tail3": track(rot=keys([(0, 0, 0, 0), (0.4, -2, 24, 0), (0.58, -2, -48, 0), (0.7, -2, -42, 0), (1.1, 0, 0, 0)])),
        "thigh_l": track(rot=keys([(0, 0, 0, 0), (0.35, -8, 0, 0), (0.55, 10, 0, 0), (1.1, 0, 0, 0)])),
        "thigh_r": track(rot=keys([(0, 0, 0, 0), (0.35, 10, 0, 0), (0.55, -8, 0, 0), (1.1, 0, 0, 0)])),
    })


SPEC = dict(
    palette={"dorsal": "#5a6442", "flank": "#7c845a", "belly": "#cfc9a2", "blotch": "#3e4830",
             "limb": "#6a6e4e", "limb_top": "#767a58",
             "claw": "#3a362e", "claw_base": "#3a362e",
             "armor": "#4a4e3a", "scute": "#b06a3a",
             "spike_base": "#5a5a46", "spike_tip": "#e6dcc0",
             "horn_base": "#5a5a46", "horn_tip": "#e6dcc0",
             "club": "#6e6a58", "beak": "#3a3630",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622",
             "eye": "#c09030", "pupil": "#140f0a"},
    sexes={"male": {"scute": "#b85a30", "dorsal": "#505c3c", "blotch": "#34402a"},
           "female": {"scute": "#c4b48a", "flank": "#8a8c66", "armor": "#565848", "blotch": "#505a40"}},
    pattern=pattern, body=(BODY_Y, 6), body_parts=body_parts, armor=armor, head=head, club=club,
    neck=dict(points=[(11, -11), (11, -14.5), (10.5, -17)], sections=[(9, 7), (8, 6)], tilt=6),
    hind=dict(x=7, pts=[(10, 9), (5.5, 8.5), (3, 9.5), (2, 9)],
              secs=[(6, 7, 0.0), (5, 5, 0.5, "limb"), (4, 3, 0.0, "limb")], pad=(6, 3, 2)),
    front=dict(x=8, pts=[(10, -8), (5, -7.5), (2, -8.5)], secs=[(5, 6, 0.0), (4, 4, 0.0, "limb")], pad=(5, 2, 2)),
    tail=dict(points=[(11, 11), (11, 20), (10.5, 29), (10, 37)], sections=[(8, 7), (5, 5), (3, 3)]),
    gait=dict(walk=(2.0, 14, 14, 0.4), run=(1.2, 20, 20, 0.7)),
    attack=attack,
    sit_drop=4, sit_kw={"hind": (30, -60, 30), "front": (-25, 60, -35)}, graze=(-12, -5),
    ko=dict(lift=0.8),
)


def build():
    return ankylosaur.build(ID, SPEC)
