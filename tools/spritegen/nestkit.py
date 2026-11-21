"""Small helpers for the egg-and-nest block models of the 1.10 predators (dasple/alberto/carcharo/majunga_extras).

A nest model is a list of cuboid elements, as in the other *_extras.egg_model(): the ground textured by its block
coordinates (_faces, so a long slab reads as one surface), and the props (leaves, cones, sticks, a chick's snout)
cut from zones of a 16x16 prop sheet. Element rotation follows the vanilla rule: one axis, -45..45 in 22.5 steps.
No Pillow here: gen_resources imports the extras for egg_model() and must run without it.
"""
from rex_extras import _faces

SIDES = ("north", "south", "east", "west", "up")


def mapped(frm, to, tex="#nest", rot=None, bottom=False, top=True):
    """A cuboid textured by its coordinates (the ground, a mound, a bank)."""
    el = {"from": list(frm), "to": list(to),
          "faces": _faces(tex, frm[0], to[0], frm[2], to[2], frm[1], to[1], top=top, bottom=bottom)}
    if rot:
        el["rotation"] = rot
    return el


def zoned(frm, to, zone, tex="#prop", rot=None, faces=SIDES):
    """A cuboid whose faces all show one zone (u0, v0, u1, v1) of a prop sheet, cropped to the face's size so a
    thin face takes a thin strip instead of squeezing the whole zone."""
    u0, v0, u1, v1 = zone
    size = {"up": (to[0] - frm[0], to[2] - frm[2]), "down": (to[0] - frm[0], to[2] - frm[2]),
            "north": (to[0] - frm[0], to[1] - frm[1]), "south": (to[0] - frm[0], to[1] - frm[1]),
            "east": (to[2] - frm[2], to[1] - frm[1]), "west": (to[2] - frm[2], to[1] - frm[1])}
    f = {}
    for name in faces:
        w, h = size[name]
        f[name] = {"uv": [u0, v0, u0 + max(0.5, min(u1 - u0, w)), v0 + max(0.5, min(v1 - v0, h))], "texture": tex}
    el = {"from": list(frm), "to": list(to), "faces": f}
    if rot:
        el["rotation"] = rot
    return el


def yrot(cx, cy, cz, angle):
    return {"origin": [cx, cy, cz], "axis": "y", "angle": angle} if angle else None


def lying_egg(cx, cz, length, width, base, sink=0.0, angle=0.0, tex="#egg", height=None):
    """A long egg lying on its side along z, rounded by a long narrow core and a short full-width middle, sunk
    `sink` below `base` (the ground hides what is under it) and turned `angle` degrees about y."""
    height = height or width
    y0 = base - sink
    rot = yrot(cx, base, cz, angle)
    els = []
    for (l, w, ya, yb) in ((length * 0.62, width, 0.0, height),
                           (length, width * 0.68, height * 0.16, height * 0.84)):
        a, b = y0 + ya, y0 + yb
        if b <= base + 0.05:
            continue
        a = max(a, base)
        frm, to = [cx - w / 2, a, cz - l / 2], [cx + w / 2, b, cz + l / 2]
        el = {"from": frm, "to": to, "faces": _faces(tex, frm[0], to[0], frm[2], to[2], a, b, top=True)}
        if rot:
            el["rotation"] = rot
        els.append(el)
    return els


# a near-round egg in stacked rows: (y from, y to, half width) for a 4-unit egg, scaled by k
BALL = [(0.0, 0.8, 1.4), (0.8, 2.2, 2.05), (2.2, 3.4, 1.85), (3.4, 4.1, 1.1)]


def ball_egg(cx, cz, base, sink=0.0, k=1.0, tex="#egg"):
    els = []
    for y0, y1, hw in BALL:
        a, b = base + y0 * k - sink, base + y1 * k - sink
        if b <= base + 0.05:
            continue
        a = max(a, base)
        hw *= k
        frm, to = [cx - hw, a, cz - hw], [cx + hw, b, cz + hw]
        els.append({"from": frm, "to": to, "faces": _faces(tex, frm[0], to[0], frm[2], to[2], a, b, top=True)})
    return els


def model(textures, els, gui_y=2.0):
    """The block model with the display of the other nests (the item in hand and in the inventory)."""
    return {"parent": "block/block", "textures": dict(textures, particle=textures["nest"]), "elements": els,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, gui_y, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 3, 0], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"scale": [0.75, 0.75, 0.75]},
                        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0],
                                                  "scale": [0.45, 0.45, 0.45]},
                        "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.5, 0.5, 0.5]}}}


def paint(px, x, y, col):
    if 0 <= x < 16 and 0 <= y < 16:
        px[x, y] = tuple(col[:3]) + (255,)


def shade(col, k):
    return tuple(max(0, min(255, int(round(c * k)))) for c in col[:3])
