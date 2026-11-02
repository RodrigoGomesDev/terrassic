"""Front-view 32x32 spawn-egg designs (v5 style), one function per species, drawn on eggfront.Egg."""
from eggfront import Egg, in_egg, N

K = "#16100c"
SHINE = "#fff8e8"
TOOTH = "#f4ecd6"
MOUTH = "#5a1414"


def eyes(e, y=14, x=10, **_):
    """Simple mirrored 2x2 dark eyes, like vanilla / Cobblemon eggs."""
    e.pal["K"] = "#2a1e18"
    e.px(e.mirror([(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]), "K")


def nostrils(e, y=21, x=13, ch="n"):
    e.px(e.mirror([(x, y)]), ch)


def fangs(e, y, xs):
    e.pal.setdefault("W", TOOTH)
    e.px(e.mirror([(x, y) for x in xs]), "W")


def cap(e, ch, top, body):
    """Two-tone head like the Gallimimus: a darker cap over the top, the body colour below."""
    e.ell(top, ch, clip=True)
    e.ell((top[0] + 1, top[1] + 7, top[2] - 1, top[3] + 16), "b", clip=True)


def tyrannosaurus():
    """T. rex v2 (29/10): the colours of the new model (dark green, rust bars, pale jaw), a long snout down the middle,
    the model's eyes (dark rim, amber with a pale top, round pupil towards the snout, glint, rust brow) and the upper
    teeth hanging over the closed jaws (no open red mouth)."""
    e = Egg("tyrannosaurus_front", {"b": "#465036", "d": "#2a3226", "l": "#5d6840", "c": "#cbb472", "r": "#8e4022",
                                     "n": "#1a1f18", "W": "#f1ebd4", "M": "#2a1012", "E": "#e8a92f", "e": "#b8741f",
                                     "Y": "#ffdf6e", "p": "#130d0c", "g": "#fff3c6", "D": "#141210", "h": "#5d6840"})
    e.ell((4, 1, 27, 19), "d", clip=True)
    e.ell((5, 8, 26, 30), "b", clip=True)
    # rust bars across the crown
    for (x0, y0, x1, y1) in ((12, 2, 14, 5), (17, 2, 19, 5), (8, 5, 10, 8), (21, 5, 23, 8)):
        e.line([(x0, y0), (x1, y1)] if x0 < 16 else [(x1, y0), (x0, y1)], "r", 2, clip=True)
    # long snout down the middle, a shade lighter
    e.poly([(11, 12), (20, 12), (21, 24), (10, 24)], "l", clip=True)
    e.px(e.mirror([(13, 19)]), "n")
    # the eyes, as on the model
    eye = ["rrrrrr..",
           ".DDDDDD.",
           ".DgYppD.",
           ".DYYppD.",
           ".DEEEeD.",
           "..DDDD..",
           "..hhh..."]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(3 + i, 10 + j)]) if in_egg(*q)], ch)
    # closed jaws: the lower jaw pale, upper teeth hanging over the lip line
    e.rect((5, 25, 26, 31), "c", clip=True)
    e.line([(5, 24), (26, 24)], "M", clip=True)
    for x in (7, 10, 13):
        e.px(e.mirror([(x, 25), (x, 26)]), "W")
    e.px(e.mirror([(x, 25) for x in (8, 11, 14)]), "W")
    return e


def spinosaurus():
    """Spinosaurus (02/11, the v3 model), front view like the T. rex egg: cool slate olive, the male's crimson sail
    rising behind the top of the egg with its dark spines and bone tips, the eyes set high (the model's: dark socket,
    gold with a pale top, the pupil toward the snout, a glint), the nostrils far back between them, the long narrow
    crocodile snout down the middle with the rosette of interlocking teeth at its tip, and the sand throat."""
    e = Egg("spinosaurus", {
        "b": "#4a5650", "d": "#35403d", "D": "#252c2c", "n": "#181c1c", "l": "#64715f", "L": "#838c72",
        "c": "#b7a982", "C": "#958866", "a": "#d6caa1",
        "r": "#9c3a28", "R": "#6e2420", "q": "#3e1716", "o": "#c86a3c", "t": "#e2c48c", "k": "#2a1c1a",
        "i": "#d9c24e", "I": "#9a7f26", "Y": "#f6e78a", "P": "#120d0c", "G": "#fff6cf", "S": "#121414",
        "W": "#efe8d0", "w": "#c4b892", "u": "#3a1618"})
    # the sail behind the top of the egg: crimson, darker at the base, the spines dark, the tips bone
    e.poly([(8, 9), (10, 3), (13, 0), (18, 0), (21, 3), (23, 9)], "r")
    e.poly([(9, 9), (22, 9), (21, 6), (10, 6)], "R")
    for x in (11, 14, 17, 20):
        e.line([(x, 1 if 13 <= x <= 18 else 3), (x, 8)], "k")
    e.px([(13, 0), (14, 0), (17, 0), (18, 0), (10, 3), (11, 2), (20, 2), (21, 3)], "t")
    e.px([(15, 2), (16, 2), (12, 4), (19, 4)], "o")
    # the head: slate olive, a darker crown, broken dark stripes back along the sides
    e.ell((3, 6, 28, 38), "b")
    for y in range(N):
        for x in range(N):
            if y > 10 and not in_egg(x, y):
                e.set(x, y, "_")
    e.ell((6, 6, 25, 16), "d", clip=True)
    for pts in ([(4, 16), (6, 19)], [(4, 21), (5, 24)]):
        e.line(pts, "D", clip=True); e.line([(N - 1 - x, y) for x, y in pts], "D", clip=True)
    # the eyes set high on the head, as on the model
    eye = [".SSSS..",
           "SYYGPS.",
           "SiiPPS.",
           ".SIISS.",
           "..SS..."]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(6 + i, 9 + j)]) if in_egg(*q)], ch)
    e.line([(6, 8), (11, 8)], "n", clip=True); e.line([(25, 8), (20, 8)], "n", clip=True)
    # the long narrow snout down the middle, a shade lighter, the nostrils far back by the eyes
    e.poly([(13, 10), (18, 10), (18, 24), (13, 24)], "l")
    e.line([(13, 11), (13, 23)], "d"); e.line([(18, 11), (18, 23)], "D")
    e.line([(15, 11), (15, 21)], "L")
    e.px([(14, 12), (17, 12)], "n")
    # the rosette at the tip: the snout widens, the long teeth interlock over the lip line
    e.poly([(11, 24), (20, 24), (20, 28), (11, 28)], "l")
    e.line([(11, 26), (20, 26)], "u")
    for x in (11, 13, 15, 17, 19):
        e.px([(x, 27), (x, 28)], "W")
    for x in (12, 14, 16, 18, 20):
        e.px([(x, 25), (x, 24)], "W")
    e.px([(12, 24), (16, 24), (20, 24)], "w")
    # the sand throat either side of the snout
    e.ell((5, 22, 11, 33), "c", clip=True); e.ell((20, 22, 26, 33), "c", clip=True)
    e.px([q for q in e.mirror([(7, 27), (8, 30)]) if in_egg(*q)], "C")
    e.line([(5, 23), (11, 25)], "u", clip=True); e.line([(26, 23), (20, 25)], "u", clip=True)
    return e


def dilophosaurus():
    e = Egg("dilophosaurus", {"b": "#76863c", "c": "#d6cc98", "d": "#3a4418", "n": "#363e1a",
                               "e": "#cc3424", "y": "#f4c838", "R": MOUTH})
    for side in (0, 1):
        pts = [(9, 8), (10, 2), (13, 0), (14, 5), (13, 8)]
        if side:
            pts = [(31 - x, y) for (x, y) in pts]
        e.poly(pts, "e")
        x = 11 if not side else 20
        e.line([(x, 2), (x, 7)], "y")
    cap(e, "d", (6, 4, 25, 18), (3, 10, 28, 36))
    e.rect((5, 17, 8, 18), "y", clip=True)
    e.rect((23, 17, 26, 18), "y", clip=True)
    e.px(e.mirror([(6, 21), (7, 21), (5, 23)]), "y")
    e.poly([(10, 19), (21, 19), (23, 31), (8, 31)], "c", clip=True)
    e.rect((8, 26, 23, 31), "E", clip=True)
    e.pal["E"] = "#b8483a"
    eyes(e, 14, 9, iris="#f0c030", brow="n", angry=True)
    nostrils(e, 21, 13)
    e.line([(9, 25), (22, 25)], "R")
    fangs(e, 26, [11, 14])
    return e


def velociraptor():
    e = Egg("velociraptor", {"b": "#7a6146", "l": "#574533", "d": "#3d3026", "D": "#2b221b", "k": "#1f1915",
                                 "K": "#0f0c0a", "r": "#436577", "R": "#2c4350", "E": "#f2b233", "e": "#b5761a",
                                 "p": "#0a0706", "w": "#efe8d2", "W": "#c9bd98", "s": "#4a4038", "c": "#bba783"})
    e.ell((2, 0, 29, 34), "D", clip=True)
    # the quill ridge: dark spikes with the steel-blue sheen, tallest in the middle
    for x, h in ((8, 2), (10, 3), (12, 4), (14, 4), (17, 4), (19, 4), (21, 3), (23, 2)):
        e.line([(x, 8), (x, 8 - h)], "K", 1, clip=True)
        e.px([q for q in [(x, 8 - h), (x, 9 - h)] if in_egg(*q)], "r")
    # the head: dark, a lighter cheek below the eyes, broken bars over the crown
    e.ell((4, 7, 27, 22), "d", clip=True)
    e.ell((5, 15, 26, 30), "b", clip=True)
    e.px(e.mirror([(6, 17), (7, 19), (6, 21), (8, 22)]), "l")
    e.px(e.mirror([(8, 7), (9, 8), (10, 8), (7, 10), (8, 11)]), "k")
    # sand throat and the dark lower jaw at the bottom
    e.ell((8, 25, 23, 38), "c", clip=True)
    e.rect((10, 27, 21, 29), "s", clip=True)
    # the long narrow snout down the middle, darker edges, the dark tip with the nostrils
    e.poly([(13, 11), (18, 11), (18, 27), (13, 27)], "d", clip=True)
    e.line([(13, 12), (13, 27)], "D"); e.line([(18, 12), (18, 27)], "D")
    e.line([(15, 12), (15, 24)], "l"); e.line([(16, 12), (16, 24)], "l")
    e.px([(14, 15), (17, 15), (14, 19), (17, 19)], "k")
    e.rect((13, 25, 18, 27), "K", clip=True)
    e.px([(14, 25), (17, 25)], "s")
    # the eyes: narrow slits under brows that slant down toward the snout (the angry V)
    band = ["KK......",
            "kKKK....",
            ".kkKKK..",
            ".kEpEe..",
            "..kkk..."]
    for j, row in enumerate(band):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(5 + i, 10 + j)]) if in_egg(*q)], ch)
    # the shut mouth: a dark line, the upper teeth hanging over it along both sides of the snout
    e.line([(8, 26), (23, 26)], "K", clip=True)
    e.px(e.mirror([(9, 27), (11, 27), (11, 28), (13, 27)]), "w"); e.px(e.mirror([(10, 27), (12, 27)]), "W")
    return e


def compsognathus():
    e = Egg("compsognathus", {"b": "#86903a", "c": "#ecdc96", "d": "#454a18", "n": "#3e4218",
                               "R": "#8a2a1e"})
    cap(e, "d", (9, 2, 22, 12), (4, 7, 27, 36))
    e.line([(15, 4), (15, 13)], "d", 2)
    e.ell((8, 19, 23, 34), "c", clip=True)
    e.px(e.mirror([(7, 19), (8, 20), (6, 22)]), "d")
    eyes(e, 14, 9)
    nostrils(e, 21, 14)
    e.line([(13, 24), (15, 25), (16, 25), (18, 24)], "R")
    return e


def triceratops():
    """Triceratops (02/11, the "ameixa" plum-grey of the new model), front view like the T. rex and Protoceratops
    eggs: the solid frill is the dome behind the egg, its pale rim with low flat bumps and, on the male, the
    terracotta band one scale in from the rim; the two long brow horns rise from over the eyes past the top of the
    frill (outside the egg's outline, the first thing you see in the hotbar); the short thick nose horn; the model's
    eyes (the house almond, rex-egg size: heavy brow, dark socket, pale top, dark honey iris, pupil toward the beak,
    glint, lower lid) deep under the horn roots; the cheeks flaring to their dark epijugal points and the dark parrot
    beak over the paler jaw."""
    e = Egg("triceratops", {
        "w": "#ddcfb6", "W": "#bfae96", "f": "#76697a", "F": "#8d7f8b", "v": "#574a5a", "x": "#a45c46", "X": "#86493c",
        "b": "#615665", "l": "#776b77", "d": "#4b4050", "s": "#2e2234", "c": "#b5a1a8", "C": "#a38f98",
        "i": "#e6dcc6", "I": "#cbbd9f", "j": "#a8997c", "o": "#6b5c4c", "O": "#4e4136",
        "k": "#3f3534", "K": "#262022", "B": "#574b48", "h": "#3d2d42", "n": "#1c1418",
        "D": "#1e1418", "Y": "#e8b860", "E": "#d09a42", "e": "#8a5a26", "P": "#140c0a", "G": "#fff4d6", "L": "#a38f98"})
    # the frill: a solid dome behind the egg, pale rim, low flat bumps, the male's terracotta band one scale in
    e.ell((0, 1, 31, 25), "w")
    e.ell((1, 2, 30, 24), "x")
    e.ell((3, 4, 28, 22), "f")
    e.px(e.mirror([(1, 9), (3, 4), (7, 2), (12, 1)]), "W")          # the low bumps of the rim, flat (not spikes)
    e.px(e.mirror([(2, 7), (5, 3), (10, 2)]), "X")                  # the band's darker scale edges
    for pts in ([(12, 7), (8, 4)], [(10, 10), (5, 8)], [(14, 6), (13, 3)]):   # vessel grooves out from the middle
        e.line(pts, "v"); e.line([(N - 1 - x, y) for x, y in pts], "v")
    e.px(e.mirror([(9, 6), (6, 11)]), "F")
    # the face: the egg under the frill, a dark edge against it, the crown a shade darker
    e.ell((5, 8, 26, 41), "s")
    e.ell((6, 9, 25, 41), "b")
    for y in range(N):
        for x in range(N):
            if y > 16 and not in_egg(x, y):
                e.set(x, y, "_")
    e.ell((8, 9, 23, 18), "d", clip=True)
    # drawn scales: plates lit on the upper side, rows on the crown and the cheeks
    for x, y in ((11, 10), (13, 12), (9, 22), (11, 24)):
        e.px(e.mirror([(x, y)]), "l")
        e.px(e.mirror([(x, y + 1)]), "h")
    # the brow horns: from the swollen brow over each eye, up and a little out, past the top of the frill; ivory
    # keratin, dark at the root, a lit edge on the outside and a groove up the root half
    for side in (0, 1):
        def mx(pts):
            return [(N - 1 - x, y) for x, y in pts] if side else pts
        e.poly(mx([(8, 14), (12, 14), (8, 2), (6, 0), (6, 3)]), "i")
        e.poly(mx([(8, 14), (12, 14), (11, 10), (8, 10)]), "o")
        e.line(mx([(7, 12), (6, 3)]), "I")
        e.line(mx([(11, 12), (9, 5)]), "j")
        e.px(mx([(9, 12), (10, 10)]), "O")
    # the eyes, as on the model, rex-egg size, deep under the horn roots
    eye = ["hhhhhhh.",
           ".DDDDDD.",
           "DYYYYGPD",
           "DEYYEPPD",
           "DeEEEEeD",
           ".DDDDDD.",
           "..LLL..."]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(4 + i, 14 + j)]) if 0 <= q[0] < N], ch)
    # the cheeks flaring out under the eyes to the dark epijugal points
    e.poly([(3, 21), (7, 21), (8, 25), (4, 24)], "d")
    e.px([(3, 21), (28, 21), (2, 22), (29, 22)], "o"); e.px([(1, 23), (30, 23), (2, 23), (29, 23)], "O")
    # the snout down the middle, lighter, with the short thick nose horn on it
    e.poly([(13, 13), (18, 13), (19, 24), (12, 24)], "l")
    e.poly([(14, 19), (17, 19), (16, 15), (15, 15)], "i")
    e.px([(14, 19), (17, 19)], "o"); e.px([(16, 18), (16, 17)], "j")
    e.px(e.mirror([(12, 21), (12, 22)]), "n")                         # the nostrils either side
    # the pale jaw at the bottom, the mouth line climbing to the cheek
    e.ell((9, 25, 22, 36), "c", clip=True)
    e.px(e.mirror([(11, 31), (12, 32)]), "C")
    e.line([(8, 25), (11, 27), (13, 27)], "s"); e.line([(23, 25), (20, 27), (18, 27)], "s")
    # the beak: the dark rostral narrowing down, a lit edge, the hooked tip over the predentary
    e.poly([(13, 23), (18, 23), (18, 26), (17, 29), (14, 29), (13, 26)], "k")
    e.line([(14, 23), (14, 27)], "B"); e.line([(18, 24), (18, 26)], "K")
    e.poly([(14, 28), (17, 28), (16, 30), (15, 30)], "K")
    e.px([(14, 31), (15, 31), (16, 31), (17, 31)], "h")
    return e


def stegosaurus():
    e = Egg("stegosaurus", {"b": "#6a8a42", "c": "#cbc48c", "d": "#36501e", "n": "#2e4418",
                             "e": "#e2922c", "D": "#8a2c18", "k": "#3a3428", "R": "#5a2a1a"})
    for (cx, cy, r) in ((15.5, 4, 4), (9, 7, 3), (22, 7, 3), (5, 12, 2), (26, 12, 2)):
        e.poly([(cx, cy - r - 2), (cx + r, cy + 1), (cx, cy + r + 1), (cx - r, cy + 1)], "D")
        e.poly([(cx, cy - r), (cx + r - 1, cy + 1), (cx, cy + r), (cx - r + 1, cy + 1)], "e")
        e.px([(round(cx), cy - r), (round(cx), cy - r + 1)], "f")
    e.pal["f"] = "#f8c858"
    for y in range(N):
        for x in range(N):
            if in_egg(x, y) and y > 9 and e.get(x, y) in ("e", "D"):
                e.set(x, y, "b")
    cap(e, "d", (5, 7, 26, 20), (3, 13, 28, 38))
    for p in ((6, 18), (8, 22), (5, 23)):
        e.px(e.mirror([p, (p[0] + 1, p[1])]), "d")
    e.ell((8, 19, 23, 34), "c", clip=True)
    eyes(e, 16, 10)
    nostrils(e, 22, 14)
    e.poly([(13, 26), (18, 26), (17, 28), (14, 28)], "k")
    return e


def ankylosaurus():
    e = Egg("ankylosaurus", {"b": "#6c5e44", "c": "#b8a780", "o": "#c8964a", "O": "#f2cc80",
                              "d": "#4a3e2c", "I": "#ece2c4", "k": "#3e342a", "n": "#3a3022"})
    e.ell((3, 2, 28, 26), "o", clip=True)
    for row, y in enumerate((7, 13)):
        start = 7 if row % 2 == 0 else 9
        for x in range(start, 24, 4):
            if in_egg(x, y) and in_egg(x + 1, y + 2):
                e.px([(x, y), (x + 1, y)], "O")
                e.px([(x, y + 2), (x + 1, y + 2)], "d")
    e.line([(4, 18), (27, 18)], "d")
    # horns at the corners and side spikes
    e.poly(e.mirror([(6, 6), (8, 8), (3, 4)])[:3], "I")
    e.poly([(25, 6), (23, 8), (28, 4)], "I")
    for y in (12, 16):
        e.poly([(4, y - 1), (4, y + 1), (1, y)], "I")
        e.poly([(27, y - 1), (27, y + 1), (30, y)], "I")
    e.ell((8, 21, 23, 34), "c", clip=True)
    e.poly([(5, 22), (5, 25), (2, 24)], "I")
    e.poly([(26, 22), (26, 25), (29, 24)], "I")
    eyes(e, 19, 9)
    nostrils(e, 24, 13)
    e.poly([(12, 27), (19, 27), (18, 29), (13, 29)], "k")
    return e


def brachiosaurus():
    e = Egg("brachiosaurus", {"b": "#7892a0", "c": "#c4cabc", "d": "#3e5462", "n": "#38484f",
                               "e": "#c43c2a", "E": "#f07a4a", "R": "#4a2a2a"})
    e.ell((11, 0, 20, 9), "e")
    e.px([(13, 2), (14, 1)], "E")
    cap(e, "d", (6, 4, 25, 17), (3, 10, 28, 36))
    e.ell((8, 20, 23, 34), "c", clip=True)
    for p in ((6, 20), (7, 23)):
        e.px(e.mirror([p, (p[0], p[1] + 1)]), "d")
    eyes(e, 15, 8)
    nostrils(e, 11, 14, "d")
    e.line([(11, 26), (20, 26)], "R")
    return e


def parasaurolophus():
    """Parasaurolophus (02/11, the remade model, "ruivo de impala"), front view like the other remade eggs: the long
    tube of the crest leaves the top of the snout and sweeps up and back past the egg's outline to the right (the
    first thing seen in the hotbar), lit along its top, darkening to near black at the tip as on the male; the crown
    and the back of the head chestnut, the face rufous, the cheeks and the throat cream; the model's eyes (rex-egg
    size: dark socket, amber-brown iris, pupil toward the bill, glint) with the pale lower lid of a herd animal; the
    broad flat duck bill down the middle, dark keratin flaring at the bottom, its paler cutting edge, the slit
    nostrils high on its sides."""
    e = Egg("parasaurolophus", {
        "r": "#c06a2c", "R": "#a0521f", "q": "#733a1a", "Q": "#4c2516", "o": "#d8874a",
        "c": "#d3c4a4", "C": "#b6a284", "w": "#e9dfc6",
        "t": "#a0521f", "T": "#733a1a", "u": "#4e2d1f", "U": "#34221d", "v": "#1d1517", "h": "#d8874a",
        "D": "#120d0e", "Y": "#b07a3a", "E": "#7d4f24", "e": "#4d3018", "P": "#0c0a0a", "G": "#f0e6cc", "L": "#d9cdb0",
        "k": "#37302d", "K": "#221e1e", "B": "#524842", "A": "#75695e", "n": "#1a1314"})
    # the head: rufous, the crown chestnut, the cream coming up from the throat with a wandering edge
    e.ell((3, 3, 28, 36), "r", clip=True)
    e.ell((6, 3, 25, 14), "R", clip=True)
    e.ell((9, 3, 22, 9), "q", clip=True)
    e.poly([(3, 31), (4, 24), (7, 22), (9, 24), (10, 27), (21, 27), (22, 24), (24, 22), (27, 24), (28, 31)], "c", clip=True)
    e.px([(5, 23), (26, 23), (8, 26), (23, 26)], "C")
    e.px([(5, 28), (26, 29), (7, 30), (24, 30)], "w")
    # drawn scales: a few lit plates on the crown and the cheeks (the lit side up), never a row
    for x, y in ((11, 6), (8, 10), (12, 12), (6, 17)):
        e.px(e.mirror([(x, y)]), "o")
        e.px(e.mirror([(x + 1, y + 1)]), "q")
    # the crest: from the top of the snout up and back to the upper right, 3 px thick, lit on its upper edge, shaded
    # under, darkening toward the rounded tip (the male's); the suture a broken dark line along it
    e.line([(15, 11), (21, 5)], "t", 3)
    e.line([(21, 5), (25, 2)], "T", 3)
    e.line([(25, 2), (29, 0)], "u", 3)
    e.line([(14, 10), (20, 4)], "h"); e.line([(21, 3), (24, 1)], "t"); e.line([(25, 0), (27, 0)], "T")
    e.line([(17, 11), (22, 6)], "T"); e.line([(23, 5), (27, 2)], "U"); e.px([(29, 1), (29, 2), (28, 2)], "v")
    e.px([(18, 7), (22, 4), (26, 1)], "U")
    # the eyes, as on the model, rex-egg size, the pale lower lid
    eye = [".qqqq...",
           ".DDDDDD.",
           "DYYGYPD.",
           "DEYYEPPD",
           "DeEEEEeD",
           ".DDDDDD.",
           "..LLLL.."]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(3 + i, 12 + j)]) if in_egg(*q)], ch)
    # the duck bill: the snout narrows a little, then the keratin sheath flares broad and flat at the bottom, lit
    # down its middle, dark at the sides and under the rim
    e.poly([(13, 11), (18, 11), (19, 19), (12, 19)], "R")
    e.poly([(12, 20), (19, 20), (20, 25), (21, 28), (19, 30), (12, 30), (10, 28), (11, 25)], "B")
    e.line([(15, 21), (15, 28)], "A"); e.px([(16, 22), (16, 25)], "A")
    e.line([(12, 20), (11, 25)], "k"); e.line([(19, 20), (20, 25)], "k")
    e.line([(10, 28), (12, 30)], "k"); e.line([(21, 28), (19, 30)], "k")
    e.line([(13, 30), (18, 30)], "K"); e.px([(14, 31), (17, 31)], "K")
    e.px(e.mirror([(13, 21), (13, 22)]), "n")                            # the slit nostrils
    return e

def pachycephalosaurus():
    """Pachycephalosaurus (02/11, the remade model): the egg's top IS the dome, the way the animal's own head is mostly
    dome: honey at its base fading up to the male's bleached cream crown, with darker growth streaks fanning out from
    the top; a rim of blunt dark knobs of uneven size where the dome meets the face (never an even row: that reads as
    teeth); the heavy brow shelf over each eye and the model's eye under it (dark socket, olive-green iris, pupil
    toward the snout, glint); pale cheek spots; the short narrow snout down the middle with the low bosses on its
    bridge and the small horn-brown beak; the cream throat below."""
    e = Egg("pachycephalosaurus", {
        "b": "#a0661a", "B": "#bf8326", "d": "#7d4c14", "D": "#5a3510",
        "h": "#c4a36c", "H": "#d9c193", "j": "#ebdcb6", "s": "#a8814a",
        "n": "#3a2c22", "N": "#5a4636",
        "w": "#d8c9a3", "W": "#c2b08a",
        "S": "#2a1a14", "L": "#160e0c", "I": "#9aa466", "i": "#6b7646", "P": "#0d0b08", "G": "#f2ecd6",
        "k": "#5a4532", "K": "#3d2e22", "o": "#2a1a14"})
    # the dome: the top half of the egg, honey round its base rising to the bleached crown
    e.ell((3, 1, 28, 24), "B", clip=True)
    e.ell((6, 1, 25, 17), "s", clip=True)
    e.ell((8, 1, 23, 12), "h", clip=True)
    e.ell((10, 1, 21, 8), "H", clip=True)
    e.ell((13, 1, 18, 5), "j", clip=True)
    # growth streaks fanning out from the crown, uneven and broken
    for pts in (((14, 5), (12, 9), (11, 12)), ((17, 5), (19, 9)), ((15, 6), (15, 9)), ((12, 4), (9, 8)),
                ((19, 4), (22, 8), (23, 10))):
        e.line(list(pts), "s")
    # the knob rim where the dome meets the face: blunt bumps of different sizes, the biggest at the back corners
    for (x, y, sz) in ((3, 14, 2), (8, 15, 1), (12, 14, 2)):
        q = [(x + i, y + j) for i in range(sz) for j in range(sz)]
        e.px([p for p in e.mirror(q) if in_egg(*p)], "n")
        e.px([p for p in e.mirror([(x, y - 1)]) if in_egg(*p)], "N")
    # the face below the dome: honey, a darker band where the dome casts its shadow
    e.poly([(3, 17), (28, 17), (29, 31), (2, 31)], "b", clip=True)
    e.line([(4, 16), (27, 16)], "d", clip=True)
    # the heavy brow shelf over each eye, then the eye deep under it
    e.px(e.mirror([(x, 17) for x in range(4, 11)]), "D")
    eye = [".SSSSS.",
           "SLLLLLS",
           "SIiPGIS",
           "SiIPIiS",
           ".SSSSS."]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(4 + i, 18 + j)]) if in_egg(*q)], ch)
    # the pale cheek spots under the eyes (as on the model)
    e.px(e.mirror([(6, 24), (7, 24), (6, 25)]), "w")
    # the snout down the middle: narrow, the bosses on its bridge, the nostrils, the small beak at the bottom
    e.poly([(12, 17), (19, 17), (18, 27), (13, 27)], "d")
    e.line([(15, 18), (15, 25)], "b"); e.line([(16, 18), (16, 24)], "b")
    e.px([(14, 19), (17, 19)], "N")
    e.px([(13, 26), (18, 26)], "o")
    e.poly([(13, 27), (18, 27), (18, 30), (13, 30)], "k")
    e.line([(13, 30), (18, 30)], "K")
    # the cream throat on each side of the beak
    e.poly([(4, 27), (12, 27), (12, 33), (4, 33)], "w", clip=True)
    e.poly([(19, 27), (27, 27), (27, 33), (19, 33)], "w", clip=True)
    e.px(e.mirror([(5, 28), (8, 30)]), "W")
    return e


def gallimimus():
    """Gallimimus (02/11, the remade model): the male's blue-black filament plumage over the crown and the neck
    (2-pixel locks, a few with pale tips, the borders wandering), the chalk throat and face below; the big eyes of a
    runner that watches far off, set out on the sides (the model's eye: dark lid, the pale ring of bare skin, chestnut
    iris, pupil toward the beak, glint); the small bare face in grey skin between them and the long flat beak down the
    middle, dark keratin, widening to the rounded spatulate tip at the bottom (it sifts and nips, no teeth)."""
    e = Egg("gallimimus", {
        "d": "#1c2130", "b": "#283043", "l": "#384258", "t": "#cfcbc0",
        "w": "#dedbd2", "W": "#c8c5bd", "q": "#a6a39e",
        "s": "#6b778a", "S": "#4f5b70",
        "D": "#141013", "R": "#b9b1a8", "I": "#8a4a1c", "i": "#5e3012", "P": "#0c0909", "G": "#f6efe0",
        "k": "#2e2b31", "K": "#1c1a1e", "B": "#57524f", "A": "#8a8177", "n": "#0c0909"})
    # the plumage: the whole egg blue-black, the chalk throat coming up from below with a wandering edge
    e.ell((3, 2, 28, 33), "b", clip=True)
    e.ell((5, 2, 26, 12), "d", clip=True)
    e.poly([(4, 31), (5, 22), (8, 20), (12, 22), (15, 21), (17, 22), (20, 20), (23, 21), (26, 23), (27, 31)], "w", clip=True)
    e.px([(7, 23), (24, 24), (10, 21), (21, 21)], "w")
    e.px([(8, 27), (23, 28), (6, 29), (25, 30), (12, 30), (19, 29)], "W")
    # filament locks: 2-pixel strokes down the crown and the cheeks, each its own length, some with a pale tip
    for (x, y, n, tip) in ((9, 3, 3, 0), (13, 2, 2, 0), (18, 3, 3, 0), (22, 4, 2, 0), (6, 8, 3, 1), (25, 9, 3, 0),
                           (11, 7, 2, 0), (20, 7, 2, 1), (4, 15, 3, 0), (27, 16, 3, 1), (5, 20, 2, 1), (26, 21, 2, 0)):
        e.px([(x, y + j) for j in range(n)], "l")
        e.px([(x + 1, y + j) for j in range(n - 1)], "l")
        if tip:
            e.px([(x, y + n)], "t")
    # the bare face between the eyes: grey skin, a shade lighter down the top of the beak's root
    e.poly([(12, 10), (19, 10), (20, 16), (11, 16)], "s")
    e.px([(12, 10), (19, 10), (11, 15), (20, 15)], "S")
    # the eyes: big, out on the sides, the pale ring of bare skin around them
    eye = [".RRRRR..",
           "RDDDDDR.",
           "RDIIGPDR",
           "RDIiPPDR",
           "RDiiiiDR",
           ".RDDDDR.",
           "..RRRR.."]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(3 + i, 11 + j)]) if in_egg(*q)], ch)
    # the long flat beak down the middle: narrow at the root, widening to the rounded tip, a lit ridge on top
    e.poly([(13, 15), (18, 15), (19, 23), (20, 27), (19, 30), (12, 30), (11, 27), (12, 23)], "k")
    e.line([(15, 16), (15, 28)], "B")
    e.px([(16, 17), (16, 21), (14, 26)], "A")
    e.line([(11, 27), (11, 29)], "K"); e.line([(20, 27), (20, 29)], "K")
    e.px([(12, 30), (19, 30), (13, 31), (18, 31)], "K")
    e.px([(14, 16), (17, 16)], "n")                                  # the nostrils high on the beak
    return e


def maiasaura():
    e = Egg("maiasaura", {"b": "#8e7c5a", "c": "#e0d4b0", "d": "#4e3e2a", "n": "#3a2c1e",
                          "e": "#c86a34", "f": "#e8a858", "m": "#b4946a", "M": "#4a3a2a"})
    cap(e, "d", (6, 4, 25, 17), (3, 10, 28, 36))
    # small orange crest knobs over the eyes
    e.poly([(13, 7), (15, 1), (16, 1), (18, 7)], "e")
    e.px([(15, 1), (16, 1)], "f")
    # dark blotches
    for (x, y) in ((5, 18), (7, 22), (5, 24)):
        e.px(e.mirror([(x, y), (x + 1, y), (x, y + 1)]), "n")
    eyes(e, 14, 9)
    # broad duck bill
    e.ell((8, 21, 23, 36), "c", clip=True)
    e.ell((8, 22, 23, 30), "m", clip=True)
    e.line([(10, 27), (21, 27)], "M")
    nostrils(e, 24, 12, "M")
    return e


def pteranodon():
    """Pteranodon v3 (30/10): front view like the T. rex egg, in the new model's colours (charcoal cap, pale face, dark
    wings folded at the sides), the model's eyes (amber ring in a patch of bare red skin), the horn beak with its dark
    tip down the middle and the male's banded crest blade rising over the top."""
    e = Egg("pteranodon_front", {"b": "#cfcbc1", "d": "#3e4449", "D": "#2d3236", "w": "#3e3532", "W": "#2b2626",
                              "k": "#bcab80", "K": "#8f7f5c", "t": "#2f2923", "c": "#a8381b", "C": "#2a1512", "y": "#e9ad4f",
                              "o": "#d2662a", "E": "#140d0a", "R": "#c8902c", "g": "#f3ecd2", "M": "#1f2326",
                              "s": "#5e1a16", "S": "#8e2a20", "f": "#7395a0"})
    # folded wings at the sides, stepping out of the egg
    for pts in ([(5, 13), (0, 18), (0, 23), (2, 25), (5, 22)],):
        e.poly(pts, "w"); e.poly([(31 - x, y) for x, y in pts], "w")
    e.line([(4, 14), (1, 19)], "W"); e.line([(27, 14), (30, 19)], "W")
    # slate cap over the top of the head and the neck
    e.ell((4, 2, 27, 19), "d", clip=True)
    e.ell((6, 9, 25, 34), "b", clip=True)
    # crest: a red blade rising from the crown, yellow at the tip
    e.poly([(14, 9), (17, 9), (17, 2), (16, 0), (15, 0), (14, 2)], "c")
    e.px([(14, 3), (15, 3), (16, 3), (17, 4), (14, 6), (15, 6), (16, 6), (17, 7)], "C")
    e.px([(15, 2), (16, 2), (15, 5), (16, 5)], "o")
    e.px([(15, 0), (16, 0), (15, 1), (16, 1)], "y")
    # the model's eyes, set wide on the sides
    eye = [".sSs..",
           "sMMMs.",
           "SRRRMs",
           "SREgRs",
           "SREER.",
           ".sRRs.",
           "..ss.."]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(5 + i, 10 + j)]) if in_egg(*q)], ch)
    # dark streak running back from each eye
    e.px(e.mirror([(5, 13), (4, 14)]), "M")
    # long toothless beak down the middle, horn with a dark tip
    e.poly([(13, 13), (18, 13), (17, 25), (16, 29), (15, 29), (14, 25)], "k")
    e.line([(15, 15), (15, 24)], "K")
    e.px([(15, 27), (16, 27), (15, 28), (16, 28), (15, 29), (16, 29)], "t")
    return e


def mosasaurus():
    e = Egg("mosasaurus", {"b": "#3e5260", "c": "#d6dad0", "d": "#26343e", "n": "#1a242c",
                           "f": "#2a3a46", "R": MOUTH, "s": "#6a8292"})
    # flippers
    for side in (0, 1):
        pts = [(4, 21), (0, 25), (1, 27), (5, 24)]
        if side:
            pts = [(31 - x, y) for (x, y) in pts]
        e.poly(pts, "f")
    cap(e, "d", (6, 3, 25, 17), (3, 9, 28, 36))
    for p in ((8, 7), (11, 5), (6, 11), (10, 9)):
        e.px(e.mirror([p]), "s")
    # long toothy jaw
    e.rect((7, 22, 24, 31), "c", clip=True)
    e.line([(7, 21), (24, 21)], "R")
    e.pal["W"] = TOOTH
    for x in (8, 11, 14):
        e.px(e.mirror([(x, 22), (x, 23)]), "W")
    eyes(e, 14, 9)
    nostrils(e, 18, 14)
    return e


# ------------------------------------------------------------------ shared templates (v0.4+ species)
def _side(e, pts, ch):
    """polygon on the left side plus its mirror on the right"""
    e.poly(pts, ch)
    e.poly([(31 - x, y) for (x, y) in pts], ch)


def _stripes(e, lines, ch="n"):
    for (x0, y0, x1, y1) in lines:
        e.line([(x0, y0), (x1, y1)], ch, 2, clip=True)
        e.line([(31 - x0, y0), (31 - x1, y1)], ch, 2, clip=True)


def theropod(name, pal, jaw="boxy", teeth=(9, 13), stripes=(), cap_top=(5, 2, 26, 18)):
    e = Egg(name, {"R": MOUTH, **pal})
    cap(e, "d", cap_top, None)
    _stripes(e, stripes)
    e.pal["W"] = TOOTH
    if jaw == "boxy":
        e.rect((6, 23, 25, 31), "c", clip=True)
        e.line([(6, 22), (25, 22)], "R")
        e.px(e.mirror([(6, 21)]), "R")
        for x in teeth:
            e.px(e.mirror([(x, 23), (x, 24), (x + 1, 23)]), "W")
        e.px(e.mirror([(13, 19), (12, 19)]), "n")
    else:
        e.poly([(11, 17), (20, 17), (22, 31), (9, 31)], "c", clip=True)
        e.line([(9, 25), (22, 25)], "R")
        for x in teeth:
            e.px(e.mirror([(x, 26)]), "W")
        nostrils(e, 20, 13)
    eyes(e, 14, 9)
    return e


def sauropod(name, pal, spots=()):
    e = Egg(name, {"R": "#4a2a2a", **pal})
    cap(e, "d", (6, 4, 25, 17), None)
    e.ell((8, 20, 23, 34), "c", clip=True)
    for p in spots:
        e.px(e.mirror([p, (p[0] + 1, p[1]), (p[0], p[1] + 1), (p[0] + 1, p[1] + 1)]), "s")
    eyes(e, 15, 8)
    nostrils(e, 11, 14, "n")
    e.line([(11, 26), (20, 26)], "R")
    return e


def hadrosaur(name, pal):
    e = Egg(name, {"m": "#c09a68", "M": "#4a3e30", **pal})
    cap(e, "d", (6, 5, 25, 17), None)
    eyes(e, 14, 9)
    e.ell((8, 21, 23, 36), "c", clip=True)
    e.ell((7, 23, 24, 30), "m", clip=True)
    e.line([(9, 27), (22, 27)], "M")
    nostrils(e, 25, 12, "M")
    return e


def ceratopsian(name, pal, frill=(1, 0, 30, 22), knobs=(), brow=True, nose="horn"):
    e = Egg(name, {"k": "#3e342a", **pal})
    e.ell(frill, "w")
    e.ell((frill[0] + 2, frill[1] + 2, frill[2] - 2, frill[3] - 2), "e")
    for (cx, cy) in knobs:
        e.px([(cx, cy - 1), (cx - 1, cy), (cx + 1, cy), (cx, cy + 1)], "w")
        e.px([(cx, cy)], "D")
    e.ell((6, 9, 25, 40), "b")
    for y in range(N):
        for x in range(N):
            if y > 18 and not in_egg(x, y):
                e.set(x, y, "_")
    e.ell((9, 9, 22, 20), "d", clip=True)
    e.ell((9, 21, 22, 33), "c", clip=True)
    if brow:
        _side(e, [(10, 13), (12, 12), (9, 6), (8, 7)], "i")
    eyes(e, 15, 9)
    if nose == "horn":
        e.poly([(14, 22), (17, 22), (16, 17), (15, 17)], "i")
    elif nose == "boss":
        e.ell((12, 17, 19, 22), "j")
    e.poly([(13, 26), (18, 26), (17, 30), (14, 30)], "k")
    nostrils(e, 24, 13)
    return e


def beaked(name, pal, beak=(13, 15, 18, 29)):
    """ornithomimid / bird face: cap, pale throat, long beak down the middle (like the Gallimimus)."""
    e = Egg(name, {"m": "#4e4844", "M": "#7a7268", **pal})
    cap(e, "d", (6, 2, 25, 18), None)
    e.ell((9, 18, 22, 34), "c", clip=True)
    eyes(e, 13, 8)
    x0, y0, x1, y1 = beak
    e.poly([(x0, y0), (x1, y0), (x1 - 1, y1 - 2), (x1 - 2, y1), (x0 + 2, y1), (x0 + 1, y1 - 2)], "m")
    e.line([(15, y0 + 2), (15, y1 - 3)], "M")
    return e


def pterosaur(name, pal, crest=((17, 8), (6, 0)), beak=(13, 15, 18, 30)):
    e = Egg(name, {"w": "#5a4a3e", "m": "#d8bc84", "M": "#a88c5a", **pal})
    _side(e, [(4, 15), (0, 19), (1, 22), (4, 21)], "w")
    cap(e, "d", (6, 3, 25, 17), None)
    if crest:
        e.line(list(crest), "e", 3)
    e.ell((9, 18, 22, 34), "c", clip=True)
    eyes(e, 13, 9)
    x0, y0, x1, y1 = beak
    e.poly([(x0, y0), (x1, y0), (x1 - 1, y1 - 2), (x1 - 2, y1), (x0 + 2, y1), (x0 + 1, y1 - 2)], "m")
    e.line([(15, y0 + 3), (15, y1 - 3)], "M")
    return e


def marine(name, pal, teeth=(8, 11, 14), fins=True):
    e = Egg(name, {"R": MOUTH, **pal})
    if fins:
        _side(e, [(4, 21), (0, 25), (1, 27), (5, 24)], "f")
    cap(e, "d", (6, 3, 25, 17), None)
    e.rect((7, 22, 24, 31), "c", clip=True)
    e.line([(7, 21), (24, 21)], "R")
    e.pal["W"] = TOOTH
    for x in teeth:
        e.px(e.mirror([(x, 22), (x, 23)]), "W")
    eyes(e, 14, 9)
    nostrils(e, 18, 14)
    return e


def croc(name, pal, tall=False):
    e = Egg(name, {"R": MOUTH, **pal})
    cap(e, "d", (5, 3, 26, 18), None)
    for p in ((10, 6), (14, 5), (8, 9), (12, 9)):
        e.px(e.mirror([p, (p[0] + 1, p[1])]), "s")
    top = 18 if tall else 20
    e.rect((5, top, 26, 31), "c", clip=True)
    e.line([(5, 24), (26, 24)], "R")
    e.pal["W"] = TOOTH
    for x in (6, 9, 12, 14):
        e.px(e.mirror([(x, 25)]), "W")
    for x in (7, 10, 13):
        e.px(e.mirror([(x, 23)]), "W")
    if tall:
        e.px(e.mirror([(8, 25), (8, 26)]), "W")
    e.px(e.mirror([(13, top + 1)]), "n")
    eyes(e, 12, 9)
    e.px(e.mirror([(8, 11), (9, 11), (10, 11), (11, 11)]), "d")
    return e


# ------------------------------------------------------------------ tyrannosaurs and other big theropods
def tarbosaurus():
    return theropod("tarbosaurus", {"b": "#8a7458", "c": "#d6c4a0", "d": "#4a3a2a", "n": "#33281c"},
                    stripes=((4, 16, 7, 13),))


def daspletosaurus():
    e = theropod("daspletosaurus", {"b": "#6e7448", "c": "#d2c89c", "d": "#3e4428", "n": "#2c301a",
                                    "e": "#b8402a"}, teeth=(8, 11, 14))
    _side(e, [(8, 11), (11, 11), (10, 8)], "e")
    return e


def albertosaurus():
    e = theropod("albertosaurus", {"b": "#8a8a78", "c": "#dcd8c4", "d": "#3a4458", "n": "#2a3242"},
                 jaw="narrow", teeth=(10, 13), stripes=((4, 18, 7, 15),))
    e.px(e.mirror([(9, 10), (10, 10)]), "n")
    return e


def giganotosaurus():
    """Giganotosaurus (02/11, skin 'tubarao'), front view like the T. rex egg: steel grey above and off-white below
    like a great white, the darker stripes over the crown, the long low knife snout down the middle with the two rows
    of rough wine-red lumps along its top, the model's eyes (dark socket, the pale gold iris, the pupil toward the
    snout, a glint) under a heavy brow, and the closed jaws with the blade teeth over the pale lip."""
    e = Egg("giganotosaurus", {
        "b": "#5b6872", "d": "#46525d", "D": "#343e49", "n": "#242a33", "l": "#74828a", "L": "#939f9f",
        "c": "#d9d6c8", "C": "#c3c0b0", "a": "#a6a495",
        "q": "#3b2228", "r": "#5a2c33", "R": "#7a3a3d", "t": "#96524b",
        "i": "#c9b458", "I": "#8e7a32", "P": "#0f0d0c", "G": "#f1ecc8", "S": "#0f1216", "Y": "#e2d07a",
        "W": "#f2eedd", "w": "#c9c2a8", "u": "#33161a"})
    # the head: steel grey, a darker cap, broken dark stripes over the crown, lighter cheeks
    e.ell((3, 1, 28, 34), "b", clip=True)
    e.ell((5, 1, 26, 14), "d", clip=True)
    for pts in ([(7, 4), (9, 8)], [(10, 2), (11, 5)], [(5, 9), (6, 11)]):
        e.line(pts, "D", clip=True); e.line([(N - 1 - x, y) for x, y in pts], "D", clip=True)
    e.px(e.mirror([(5, 19), (6, 21), (4, 22), (7, 24)]), "l")
    # the heavy brow ridges over the eyes
    e.line([(4, 11), (11, 10)], "n", clip=True); e.line([(27, 11), (20, 10)], "n", clip=True)
    e.line([(5, 10), (10, 9)], "L", clip=True); e.line([(26, 10), (21, 9)], "L", clip=True)
    # the eyes, as on the model: dark socket, pale gold iris, the pupil toward the snout, a glint over it
    eye = [".SSSSS..",
           "SYYiGPS.",
           "SiiIPPS.",
           ".SIIISS.",
           "..SSS..."]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(4 + i, 12 + j)]) if in_egg(*q)], ch)
    # the long low knife snout down the middle, a shade lighter, with its two rows of rough wine-red lumps
    e.poly([(12, 9), (19, 9), (20, 25), (11, 25)], "l", clip=True)
    e.line([(12, 10), (11, 24)], "d"); e.line([(19, 10), (20, 24)], "d")
    for x, y in ((14, 10), (13, 14), (14, 18)):
        e.px(e.mirror([(x, y), (x + 1, y)]), "R"); e.px(e.mirror([(x, y + 1), (x + 1, y + 1)]), "r")
        e.px(e.mirror([(x, y + 2)]), "q")
    e.px(e.mirror([(14, 9)]), "t")
    e.px(e.mirror([(13, 22)]), "n")    # the nostrils
    # closed jaws: the pale lip, the blade teeth hanging over the dark lip line, the off-white throat
    e.ell((6, 25, 25, 38), "c", clip=True)
    e.line([(4, 24), (27, 24)], "u", clip=True)
    for x in (6, 8, 10, 12, 14):
        e.px(e.mirror([(x, 25), (x, 26)]), "W")
        e.px(e.mirror([(x + 1, 25)]), "w")
    e.px([q for q in e.mirror([(9, 29), (12, 30)]) if in_egg(*q)], "C")
    return e


def carcharodontosaurus():
    e = theropod("carcharodontosaurus", {"b": "#8e5a42", "c": "#dcc2a0", "d": "#5a3424", "n": "#3e2418"},
                 teeth=(8, 10, 12, 14))
    e.px(e.mirror([(9, 10), (10, 10), (11, 11)]), "n")
    return e


def carnotaurus():
    """Carnotaurus (02/11, skin 'ferrugem'), front view like the T. rex egg: rust red with the darker saddle over
    the crown, the two bull horns standing out sideways from over the eyes (dark keratin, pale tips) with the crimson
    skin at their bases, the dark mask across the eyes, the model's eyes (almond, the slot pupil toward the snout,
    a glint, the gold top), rows of round bumps over the crown, the short deep snout and the closed jaws with the
    upper teeth over the cream lip."""
    e = Egg("carnotaurus", {
        "b": "#7b3d26", "d": "#582b20", "D": "#3a1e1a", "l": "#9e562e", "L": "#bd773f",
        "m": "#2e1916", "M": "#45231c", "c": "#cfb68a", "C": "#b0906a", "q": "#c49f78",
        "h": "#3a2d24", "H": "#231a15", "t": "#d2c3a2", "T": "#a8987a", "r": "#93302d", "R": "#6e1f22",
        "i": "#e3a531", "I": "#ad6c1c", "Y": "#f7d76c", "P": "#120d0a", "G": "#f4ecc4", "K": "#1c1511",
        "W": "#ece3c9", "w": "#c4b590", "u": "#3b1719", "n": "#2c1e1c"})
    # the head: rust, the dark saddle over the crown, lighter cheeks
    e.ell((3, 1, 28, 34), "b", clip=True)
    e.ell((6, 1, 25, 13), "d", clip=True)
    e.px(e.mirror([(5, 18), (6, 20), (5, 22), (7, 23)]), "l")
    # rows of round bumps over the crown, lit on top
    for x, y in ((9, 5), (12, 4), (8, 8), (11, 7), (14, 6)):
        e.px(e.mirror([(x, y)]), "l"); e.px(e.mirror([(x, y + 1)]), "D")
    # the horns: thick at the crimson base over each eye, standing out sideways and up, pale at the tip
    e.poly([(9, 9), (5, 8), (1, 4), (0, 5), (3, 9), (8, 12)], "h")
    e.poly([(22, 9), (26, 8), (30, 4), (31, 5), (28, 9), (23, 12)], "h")
    e.line([(2, 5), (6, 8)], "T"); e.line([(29, 5), (25, 8)], "T")
    e.px([(0, 4), (1, 4), (0, 5), (31, 4), (30, 4), (31, 5)], "t")
    e.px([(1, 3), (30, 3)], "t")
    e.ell((7, 8, 11, 12), "r"); e.ell((20, 8, 24, 12), "r")
    e.px([(8, 9), (21, 9)], "R"); e.px([(9, 11), (22, 11)], "R")
    # the dark mask across the eyes
    e.poly([(3, 13), (13, 12), (13, 18), (4, 19)], "m", clip=True)
    e.poly([(28, 13), (18, 12), (18, 18), (27, 19)], "m", clip=True)
    # the eyes, as on the model: almond, gold top, the slot pupil toward the snout, a glint over it
    eye = [".KKKKK..",
           "KYYYGiK.",
           "KiiiPIK.",
           "KIiiPIK.",
           ".KKKKK..",
           "..MMM..."]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(5 + i, 13 + j)]) if in_egg(*q)], ch)
    # the short deep snout down the middle, a shade lighter, wrinkled, the nostrils near the top
    e.poly([(12, 13), (19, 13), (20, 25), (11, 25)], "l", clip=True)
    for y in (15, 18, 21):
        e.line([(13, y), (18, y)], "b")
    e.px([(14, 16), (17, 19), (13, 22), (16, 22)], "L")
    e.px(e.mirror([(13, 14)]), "n")
    # closed jaws: cream lip, the upper teeth hanging over the dark lip line, the pale throat under it
    e.ell((6, 25, 25, 38), "c", clip=True)
    e.line([(5, 24), (26, 24)], "u", clip=True)
    e.line([(5, 23), (26, 23)], "q", clip=True)
    for x in (7, 10, 13):
        e.px(e.mirror([(x, 25), (x, 26)]), "W")
    e.px(e.mirror([(8, 25), (11, 25), (14, 25)]), "w")
    e.px(e.mirror([(10, 29), (12, 30)]), "C")
    return e


def majungasaurus():
    e = theropod("majungasaurus", {"b": "#9a5236", "c": "#e0c4a0", "d": "#5e2c1c", "n": "#3e1c12",
                                   "f": "#e8a04a"}, jaw="narrow", teeth=(10, 13),
                 stripes=((4, 17, 7, 14), (4, 22, 7, 19)))
    e.poly([(14, 5), (15, 2), (16, 2), (17, 5)], "f")
    return e


def dakotaraptor():
    e = theropod("dakotaraptor", {"b": "#6a5444", "c": "#e2d4bc", "d": "#2a2420", "n": "#1a1614",
                                  "f": "#1e1a18", "F": "#f0ece2"}, jaw="narrow", teeth=(11, 14))
    for (x, h) in ((11, 3), (13, 5), (15, 6), (17, 5), (19, 3)):
        e.line([(x, 5 - h + 1), (x + (1 if x < 15 else -1 if x > 16 else 0), 6)], "f", 2)
    for y in (17, 20, 23):
        e.line([(4, y), (6, y)], "F", clip=True)
        e.line([(25, y), (27, y)], "F", clip=True)
    return e


def troodon():
    e = theropod("troodon", {"b": "#8a6a48", "c": "#e2d0aa", "d": "#4a3624", "n": "#2e2216",
                             "f": "#5a4030"}, jaw="narrow", teeth=(12,), stripes=((4, 19, 7, 16),))
    for (x, h) in ((13, 3), (15, 4), (17, 3)):
        e.line([(x, 5 - h + 1), (x, 6)], "f", 2)
    # big night eyes
    e.pal["K"] = "#2a1e18"
    e.rect((8, 13, 10, 15), "K")
    e.rect((21, 13, 23, 15), "K")
    return e


# ------------------------------------------------------------------ feathered / beaked theropods
def struthiomimus():
    e = beaked("struthiomimus", {"b": "#a8825a", "c": "#efe4cc", "d": "#2e2620", "n": "#2e2620",
                                 "m": "#3e3630"})
    e.line([(15, 1), (14, 4)], "d", 2)
    return e


def oviraptor():
    e = beaked("oviraptor", {"b": "#b07c4a", "c": "#ecdcbc", "d": "#3a2a1e", "n": "#2a1e14",
                             "m": "#5a4a3c", "e": "#d2582a"}, beak=(12, 16, 19, 25))
    e.ell((11, 0, 20, 9), "e")
    e.px([(13, 2), (14, 1)], "f")
    e.pal["f"] = "#f0a04a"
    return e


def citipati():
    e = beaked("citipati", {"b": "#4a4a56", "c": "#d6d0c2", "d": "#2a2a32", "n": "#1a1a20",
                            "m": "#4a3a30", "e": "#e08a24", "F": "#3a6ab8", "W": "#f4f2ec"}, beak=(12, 17, 19, 26))
    # the tall cassowary casque
    e.poly([(12, 9), (19, 9), (18, 0), (13, 0)], "e")
    e.line([(14, 1), (14, 8)], "f")
    e.pal["f"] = "#f0b060"
    # blue face band under it, white wing bars at the sides
    e.rect((10, 10, 21, 11), "F", clip=True)
    for y in (20, 24):
        e.line([(3, y), (6, y)], "W", clip=True)
        e.line([(25, y), (28, y)], "W", clip=True)
    return e


def mononykus():
    e = theropod("mononykus", {"b": "#b08c5c", "c": "#ecdfc0", "d": "#7a5c3a", "n": "#3a2c20",
                               "f": "#8a4a28"}, jaw="narrow", teeth=(), stripes=((3, 20, 5, 16),))
    # rust cap plumes and the two big thumb claws held in front
    for (x, h) in ((14, 3), (16, 4)):
        e.line([(x, 5 - h + 1), (x, 6)], "f", 2)
    e.pal["I"] = "#2a2520"
    _side(e, [(6, 24), (5, 28), (7, 30), (8, 27)], "I")
    return e


def didelphodon():
    """The mammal: a furry face, round ears, a dark bandit mask and a pink nose over a strong jaw."""
    e = Egg("didelphodon", {"b": "#7a5c40", "c": "#d8c8a8", "d": "#4e3a28", "n": "#c8788a", "k": "#2a1e14", "R": MOUTH})
    cap(e, "d", (5, 3, 26, 19), None)
    for x0 in (6, 20):
        e.ell((x0, 0, x0 + 5, 6), "d")
        e.ell((x0 + 1, 1, x0 + 4, 5), "n")
    e.rect((5, 12, 26, 16), "k", clip=True)
    e.ell((9, 19, 22, 33), "c", clip=True)
    e.rect((14, 20, 17, 22), "n")
    e.line([(11, 27), (20, 27)], "R")
    fangs(e, 28, (12, 19))
    e.pal["K"] = "#f0e0c0"
    e.px(e.mirror([(10, 13), (11, 13), (10, 14), (11, 14)]), "K")
    e.pal["P"] = "#0a0604"
    e.px(e.mirror([(11, 14)]), "P")
    return e


def mesodma():
    """The little multituberculate: a round grey-brown furry face, big dark eyes, round ears, a pink nose, long whiskers."""
    e = Egg("mesodma", {"b": "#8c7a5c", "c": "#e2d8c0", "d": "#6a5a44", "n": "#d08898", "k": "#1e1410", "W": "#f0ece4", "R": MOUTH})
    cap(e, "d", (5, 3, 26, 19), None)
    for x0 in (7, 20):
        e.ell((x0, 1, x0 + 4, 5), "d")
        e.ell((x0 + 1, 2, x0 + 3, 4), "n")
    e.ell((9, 19, 22, 33), "c", clip=True)
    for cx in (11, 20):
        e.ell((cx - 2, 11, cx + 2, 15), "k")
        e.px([(cx + 1, 12)], "W")
    e.rect((14, 20, 17, 22), "n")
    e.line([(13, 25), (18, 25)], "R")
    e.px([(14, 26), (15, 26), (16, 26), (17, 26)], "W")      # the gnawing incisors
    for y in (22, 24):
        e.line([(4, y), (11, y + 1)], "W", clip=True)
        e.line([(20, y + 1), (27, y)], "W", clip=True)
    return e


def basilemys():
    """The land turtle: a high dark sculptured carapace with the scute grid and a straw rim, the hooked beak below."""
    e = Egg("basilemys", {"b": "#4e4a30", "c": "#c8b878", "d": "#3e3a24", "n": "#262014",
                          "o": "#9a8c58", "O": "#8c8458", "k": "#5a5440", "s": "#7e7858", "S": "#9a9470"})
    # the box-like carapace over the top, with the seams of the scutes and the pale rim
    e.ell((2, 0, 29, 19), "b", clip=True)
    for y in (5, 11):
        e.line([(3, y), (28, y)], "O", clip=True)
    for x in (9, 15, 21):
        e.line([(x, 1), (x, 16)], "O", clip=True)
    e.line([(3, 16), (28, 16)], "d", clip=True)
    e.line([(2, 17), (29, 17)], "o", clip=True)
    e.line([(2, 18), (29, 18)], "o", clip=True)
    # the head below the rim: grey-brown skin, the beak hooked down, the plastron patch at the bottom
    e.ell((9, 19, 22, 31), "s", clip=True)
    e.ell((11, 20, 20, 25), "S", clip=True)
    eyes(e, 23, 13)
    e.poly([(12, 27), (19, 27), (18, 31), (16, 33), (14, 31)], "k")
    e.line([(13, 29), (18, 29)], "n")
    e.ell((10, 33, 21, 40), "c", clip=True)
    return e


def enchodus():
    """The sabre-toothed herring: a silver egg with a blue-green cap, big gold eyes and the fangs over the lip."""
    e = Egg("enchodus", {"b": "#b8c4c0", "c": "#eef0ea", "d": "#3c6a6e", "n": "#243236",
                         "f": "#5a7a7c", "g": "#e0c060", "R": MOUTH})
    e.poly([(13, 6), (15, 1), (18, 1), (18, 6)], "f")
    _side(e, [(4, 20), (0, 23), (1, 25), (5, 23)], "f")
    cap(e, "d", (5, 3, 26, 17), None)
    e.ell((8, 19, 23, 36), "c", clip=True)
    for cx in (11, 20):
        e.ell((cx - 2, 12, cx + 2, 16), "g")
        e.px([(cx, 14)], "n")
    e.poly([(9, 23), (22, 23), (20, 27), (11, 27)], "R")
    e.pal["W"] = TOOTH
    e.px(e.mirror([(11, 21), (11, 22), (11, 23)]), "W")               # the palatine fangs
    e.px(e.mirror([(13, 27), (13, 28), (13, 29)]), "W")               # the lower fangs outside the lip
    return e


def lepisosteus():
    """The gar: an olive egg with the diamond ganoid scales, dark spots and the long needle snout drawn down the front."""
    e = Egg("lepisosteus", {"b": "#8c9460", "c": "#d8d4b0", "d": "#4e5e34", "n": "#2e3620",
                            "f": "#6e7848", "g": "#c8b050", "R": MOUTH})
    e.poly([(17, 7), (19, 2), (22, 2), (22, 7)], "f")
    _side(e, [(4, 20), (0, 23), (1, 25), (5, 23)], "f")
    cap(e, "d", (5, 3, 26, 17), None)
    e.ell((8, 19, 23, 36), "c", clip=True)
    for (x, y) in ((8, 8), (13, 5), (18, 9), (23, 6), (11, 13), (20, 14)):
        e.px([(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)], "n")      # the dark spots
    for cx in (11, 20):
        e.ell((cx - 1, 13, cx + 1, 15), "g")
        e.px([(cx, 14)], "n")
    e.poly([(13, 18), (18, 18), (17, 33), (14, 33)], "d")                  # the long snout
    e.line([(14, 20), (14, 32)], "R")
    e.pal["W"] = TOOTH
    e.px([(15, 21), (15, 23), (15, 25), (15, 27), (15, 29), (15, 31)], "W")  # the needle teeth
    return e


def therizinosaurus():
    e = beaked("therizinosaurus", {"b": "#5e4634", "c": "#d8c4a4", "d": "#2e2218", "n": "#2e2218",
                                   "m": "#c8a878", "M": "#8a6e48", "e": "#c0502a"}, beak=(13, 18, 18, 26))
    e.ell((9, 21, 22, 34), "e", clip=True)
    e.ell((11, 24, 20, 35), "c", clip=True)
    e.poly([(13, 18), (18, 18), (17, 24), (16, 26), (15, 26), (14, 24)], "m")
    # the long scythe claws at the sides
    for side in (0, 1):
        pts = [(3, 22), (1, 26), (2, 29), (3, 27), (4, 24)]
        if side:
            pts = [(31 - x, y) for (x, y) in pts]
        e.poly(pts, "I")
    e.pal["I"] = "#ece2c4"
    return e


def deinocheirus():
    e = beaked("deinocheirus", {"b": "#9a948a", "c": "#e4e0d6", "d": "#5a5650", "n": "#3e3a36",
                                "m": "#6a5e50", "e": "#a8442c"}, beak=(11, 17, 20, 30))
    e.poly([(10, 6), (12, 1), (19, 1), (21, 6)], "e")
    e.line([(13, 2), (18, 2)], "E")
    e.pal["E"] = "#d06a40"
    return e


def thescelosaurus():
    e = beaked("thescelosaurus", {"b": "#6e7444", "c": "#dcd4a8", "d": "#3e4424", "n": "#2c301a",
                                  "m": "#5a4a32", "e": "#c8642c"}, beak=(13, 22, 18, 28))
    _side(e, [(5, 17), (8, 17), (8, 20), (5, 20)], "e")
    return e


# ------------------------------------------------------------------ hadrosaurs, ceratopsians, armour
def edmontosaurus():
    e = hadrosaur("edmontosaurus", {"b": "#7e7462", "c": "#d8d0b8", "d": "#4a4232", "n": "#2e2a20",
                                    "e": "#b8442c"})
    e.poly([(13, 7), (15, 3), (17, 3), (19, 7)], "e")
    return e


def corythosaurus():
    e = hadrosaur("corythosaurus", {"b": "#5e7a4c", "c": "#d8d4ac", "d": "#344a2a", "n": "#22321a",
                                    "e": "#c03c28", "y": "#f0b450"})
    e.ell((9, 0, 22, 12), "e")
    e.line([(10, 5), (21, 5)], "y")
    for y in range(7, 13):
        for x in range(N):
            if e.get(x, y) in ("e", "y"):
                e.set(x, y, "d" if in_egg(x, y) else "_")
    return e


def styracosaurus():
    e = ceratopsian("styracosaurus", {"b": "#8a7a5e", "c": "#c4b48e", "e": "#b84a2c", "w": "#ece0c0",
                                      "D": "#6e2414", "i": "#f2e8cc", "j": "#b8a87e", "d": "#6a5c44",
                                      "n": "#4a3e30"}, frill=(3, 4, 28, 22), knobs=((8, 11), (23, 11)),
                    brow=False)
    # the long frill spikes
    for (x0, y0, x1, y1) in ((7, 6, 4, 0), (10, 4, 9, -1), (13, 4, 13, -1)):
        e.line([(x0, y0), (x1, y1)], "i", 2)
        e.line([(31 - x0, y0), (31 - x1, y1)], "i", 2)
    e.poly([(14, 22), (17, 22), (16, 14), (15, 14)], "i")
    return e


def pachyrhinosaurus():
    e = ceratopsian("pachyrhinosaurus", {"b": "#5e646a", "c": "#b8bcb8", "e": "#a8462c", "w": "#e8e4d8",
                                         "D": "#2e3236", "i": "#efe6cc", "j": "#c8c0a4", "d": "#44484e",
                                         "n": "#2e3236"}, knobs=((7, 9), (24, 9)), brow=False, nose="boss")
    e.line([(12, 4), (11, 0)], "i", 2)
    e.line([(19, 4), (20, 0)], "i", 2)
    return e


def protoceratops():
    """Protoceratops (02/11, skin B 'penhasco'), front view like the T. rex egg: the frill is the silhouette, a fan
    behind the egg with the pale rim and its bumps, the male's rust flush at the corners and the grooves of the blood
    vessels running out from the middle. Under it the deep short face with drawn scales, the rust nasal bump, the
    model's eyes (the house almond: dark socket, pale top, amber, pupil toward the beak, glint, a small brow), the
    cheeks flaring out to their dark keratin points and the grey hooked beak over the pale jaw."""
    e = Egg("protoceratops", {
        "f": "#7a5a3f", "F": "#8d6a4b", "v": "#5e4330", "w": "#e2cfa6", "W": "#c9b088", "x": "#b2553a", "X": "#8e3e2a",
        "b": "#b08e64", "l": "#c6a676", "d": "#977552", "o": "#7d5f42", "s": "#4e2f22", "c": "#ead9b0", "C": "#d6c09a",
        "r": "#74432c", "R": "#8a5233", "h": "#5a4332", "k": "#3a2a20",
        "B": "#3e372f", "m": "#665d52", "M": "#867c6e", "j": "#b2a892",
        "D": "#1e1712", "Y": "#f6d27a", "E": "#e0a33a", "e": "#a8681c", "P": "#120c09", "G": "#fff4d6", "L": "#d9c39b"})
    # the frill: a fan behind the top of the egg, pale rim with bumps, rust flush at the corners
    e.ell((0, 0, 31, 23), "w")
    e.ell((2, 2, 29, 21), "f")
    e.px(e.mirror([(3, 4), (1, 8), (0, 12), (7, 1), (12, 1)]), "W")          # the bumps along the rim
    e.px(e.mirror([(2, 6), (2, 7), (3, 5), (3, 6), (4, 4), (5, 3), (1, 9), (2, 8), (1, 10), (6, 3)]), "x")
    e.px(e.mirror([(4, 5), (3, 7), (2, 9)]), "X")
    # the grooves of the blood vessels running out from the middle, branching
    for pts in ([(11, 6), (9, 2)], [(9, 8), (5, 5)]):
        e.line(pts, "v"); e.line([(N - 1 - x, y) for x, y in pts], "v")
    e.line([(15, 1), (15, 8)], "F"); e.line([(16, 1), (16, 8)], "F")    # the midline ridge
    # the face: the egg under the frill, dark edge against it, a shade darker cap
    e.ell((5, 6, 26, 40), "s")
    e.ell((6, 7, 25, 40), "b")
    for y in range(N):
        for x in range(N):
            if y > 14 and not in_egg(x, y):
                e.set(x, y, "_")
    e.ell((8, 7, 23, 17), "d", clip=True)
    # drawn scales: small plates lit on their upper side, in rows on the cap and the cheeks
    for x, y in ((10, 8), (12, 10)):
        e.px(e.mirror([(x, y)]), "b")
        e.px(e.mirror([(x, y + 1)]), "o")
    for x, y in ((8, 20), (10, 22), (8, 23)):
        e.px(e.mirror([(x, y)]), "l")
        e.px(e.mirror([(x, y + 1)]), "d")
    # the cheeks flaring out under the eyes with their dark keratin point (the epijugal)
    e.poly([(4, 18), (8, 18), (8, 22), (4, 21)], "o")
    e.px([(4, 18), (27, 18)], "d")
    e.px([(3, 20), (28, 20), (3, 19), (28, 19)], "h"); e.px([(2, 20), (29, 20), (2, 21), (29, 21)], "k")
    # the rust nasal bump down the middle, lit along its left side
    e.poly([(14, 8), (17, 8), (18, 18), (13, 18)], "r")
    e.line([(14, 9), (14, 16)], "R"); e.line([(15, 8), (15, 12)], "R")
    e.line([(17, 10), (17, 17)], "s")
    # the eyes, as on the model, big like the T. rex egg's
    eye = ["..kkkk..",
           ".DDDDDD.",
           "DYYYYGPD",
           "DEYYEPPD",
           "DeEEEEeD",
           ".DDDDDD.",
           "..LLL..."]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch != ".":
                e.px([q for q in e.mirror([(5 + i, 11 + j)]) if 0 <= q[0] < N], ch)
    # the pale jaw at the bottom, the mouth line climbing to the cheek
    e.ell((9, 23, 22, 35), "c", clip=True)
    e.px(e.mirror([(11, 30), (12, 31), (10, 29)]), "C")
    e.line([(8, 24), (11, 26), (13, 26)], "s"); e.line([(23, 24), (20, 26), (18, 26)], "s")
    # the beak: grey horn narrowing down from the nostrils, a pale edge, the dark hooked tip over the small lower
    # beak, the nostrils either side of the bump
    e.poly([(13, 18), (18, 18), (18, 23), (17, 27), (14, 27), (13, 23)], "m")
    e.line([(14, 18), (14, 23)], "j"); e.line([(13, 19), (13, 22)], "M")
    e.line([(18, 19), (18, 23)], "B")
    e.poly([(14, 26), (17, 26), (16, 29), (15, 29)], "B")
    e.px([(15, 30), (16, 30), (14, 30), (17, 30)], "h")
    e.px(e.mirror([(12, 18), (12, 19)]), "k")
    return e


def leptoceratops():
    """Hornless: a short russet frill with a pale rim, olive back, cream belly and the forest dapples."""
    e = ceratopsian("leptoceratops", {"b": "#a8945c", "c": "#e0d6ac", "e": "#a4683a", "w": "#e4d4a6",
                                      "D": "#623420", "i": "#f0e8cc", "j": "#c8b48c", "d": "#6e6838",
                                      "n": "#46421f"}, frill=(5, 3, 26, 17), knobs=(), brow=False, nose=None)
    e.pal["s"] = "#524c2a"
    e.px([(9, 16), (10, 16), (9, 17), (21, 17), (22, 17), (22, 18), (12, 22), (13, 22), (19, 23), (18, 23),
          (10, 20), (21, 21)], "s")
    return e


def euoplocephalus():
    e = ankylosaurus()
    e.name = "euoplocephalus"
    e.pal.update({"b": "#5e6c44", "c": "#c4c294", "o": "#6e8048", "O": "#b8483a", "d": "#3a4428",
                  "I": "#d86a3a", "k": "#3a3428"})
    return e


# ------------------------------------------------------------------ titanosaurs
def alamosaurus():
    return sauropod("alamosaurus", {"b": "#8a6a4e", "c": "#dccaa8", "d": "#5a4230", "n": "#3a2a1e",
                                    "s": "#4a3424"}, spots=((5, 19), (7, 23), (10, 7)))


def saltasaurus():
    return sauropod("saltasaurus", {"b": "#6a7a5e", "c": "#d0d0b4", "d": "#3e4a36", "n": "#2a3424",
                                    "s": "#c8743a"}, spots=((6, 19), (8, 21), (6, 23), (10, 6), (13, 4)))


def argentinosaurus():
    return sauropod("argentinosaurus", {"b": "#6e6a60", "c": "#c8c4b4", "d": "#3e3a34", "n": "#2a2824",
                                        "s": "#34302a"}, spots=((5, 18), (7, 22), (11, 6), (8, 9)))


def opisthocoelicaudia():
    return sauropod("opisthocoelicaudia", {"b": "#b49c72", "c": "#e6dcc0", "d": "#7a6244", "n": "#4e3e2a",
                                           "s": "#6a4e34"}, spots=((6, 19), (8, 22), (5, 24), (11, 7)))


def dreadnoughtus():
    return sauropod("dreadnoughtus", {"b": "#5a6470", "c": "#c8ccd0", "d": "#2e343c", "n": "#1e2228",
                                      "s": "#d8dce0"}, spots=((6, 18), (6, 21), (6, 24)))


# ------------------------------------------------------------------ flyers and birds
def quetzalcoatlus():
    return pterosaur("quetzalcoatlus", {"b": "#d8d0bc", "c": "#f0ece2", "d": "#8a8270", "n": "#5a5446",
                                        "e": "#c4402a", "m": "#d8c08a", "M": "#a88c5a"},
                     crest=((15, 7), (12, 1)), beak=(13, 15, 18, 31))


def hatzegopteryx():
    return pterosaur("hatzegopteryx", {"b": "#7a5e4a", "c": "#d8c8b0", "d": "#3e2e24", "n": "#2a1e16",
                                       "e": "#a8302a", "w": "#3e322a", "m": "#c8a87a", "M": "#7a6248"},
                     crest=((16, 7), (10, 1)), beak=(11, 15, 20, 29))


def vegavis():
    """The duck: chestnut head with a dark cap and a pale cheek stripe, a slate bill with a pale nail, buff speckled body."""
    e = beaked("vegavis", {"b": "#b8a070", "c": "#e8e0c8", "d": "#7a4a2e", "n": "#2a2420",
                           "m": "#4a5058", "M": "#6a7078"}, beak=(12, 16, 19, 27))
    e.pal["k"] = "#2a2420"
    e.rect((7, 2, 24, 7), "k", clip=True)                 # the dark cap
    e.pal["w"] = "#e6d8b8"
    e.line([(8, 11), (23, 11)], "w")                      # the pale cheek stripe
    e.pal["s"] = "#5a4a30"
    e.px([(9, 21), (12, 24), (20, 22), (18, 26), (11, 28), (21, 29), (15, 31)], "s")
    e.pal["N"] = "#d8d0b8"
    e.px([(15, 26), (16, 26)], "N")                        # the nail at the tip of the bill
    return e


def hesperornis():
    e = beaked("hesperornis", {"b": "#4e5864", "c": "#e8ecee", "d": "#1e2630", "n": "#1e2630",
                               "m": "#3a3632", "f": "#2a3440"}, beak=(13, 15, 18, 30))
    e.line([(8, 17), (8, 22)], "f")
    e.line([(23, 17), (23, 22)], "f")
    return e


def ichthyornis():
    e = beaked("ichthyornis", {"b": "#c8ccd0", "c": "#f4f4f2", "d": "#1e1e22", "n": "#1e1e22",
                               "m": "#5a5a5e"}, beak=(13, 16, 18, 27))
    e.pal["W"] = TOOTH
    e.px([(13, 20), (13, 23), (18, 21), (18, 24)], "W")
    return e


# ------------------------------------------------------------------ sea and swamp
def tylosaurus():
    e = marine("tylosaurus", {"b": "#344a5a", "c": "#d2d8d4", "d": "#1e2c36", "n": "#141e26",
                              "f": "#22323e", "s": "#5e7686"}, teeth=(9, 12))
    e.ell((13, 26, 18, 32), "d", clip=True)
    for p in ((8, 7), (11, 5)):
        e.px(e.mirror([p]), "s")
    return e


def elasmosaurus():
    e = marine("elasmosaurus", {"b": "#4a7a7e", "c": "#d6e0d8", "d": "#24484c", "n": "#183236",
                                "f": "#2e5a5e"}, teeth=(9, 11, 13, 15))
    for p in ((8, 8), (12, 6), (6, 12)):
        e.px(e.mirror([p, (p[0] + 1, p[1])]), "c")
    return e


def xiphactinus():
    e = Egg("xiphactinus", {"b": "#9aa6b0", "c": "#e8ecee", "d": "#2e4a6a", "n": "#1e3048",
                            "f": "#5e7286", "R": MOUTH})
    # fins: dorsal on top, pectorals at the sides
    e.poly([(14, 5), (16, 0), (18, 0), (18, 5)], "f")
    _side(e, [(4, 20), (0, 23), (1, 25), (5, 23)], "f")
    cap(e, "d", (5, 3, 26, 17), None)
    e.ell((8, 19, 23, 36), "c", clip=True)
    # big upturned bulldog mouth
    e.poly([(8, 21), (23, 21), (21, 26), (10, 26)], "R")
    e.pal["W"] = TOOTH
    e.px(e.mirror([(10, 21), (10, 22), (13, 21), (13, 22)]), "W")
    e.px(e.mirror([(12, 25)]), "W")
    eyes(e, 14, 8)
    return e


def archelon():
    e = Egg("archelon", {"b": "#5e7a5a", "c": "#d6d2a8", "d": "#3a3424", "n": "#262014",
                         "o": "#4e4a30", "O": "#6e6a46", "k": "#3a3428"})
    # shell over the top, head below
    e.ell((2, 0, 29, 18), "o", clip=True)
    for (x, y) in ((10, 6), (15, 4), (20, 6), (12, 11), (18, 11)):
        e.ell((x - 2, y - 2, x + 2, y + 2), "O", clip=True)
    e.line([(4, 15), (27, 15)], "d")
    _side(e, [(4, 20), (0, 24), (1, 26), (5, 23)], "o")
    e.ell((8, 22, 23, 36), "c", clip=True)
    eyes(e, 18, 9)
    # hooked beak
    e.poly([(12, 24), (19, 24), (17, 29), (16, 30), (15, 30), (14, 29)], "k")
    e.line([(13, 26), (18, 26)], "n")
    return e


def deinosuchus():
    return croc("deinosuchus", {"b": "#4e5e3e", "c": "#c8c49a", "d": "#2a3420", "n": "#1a2014",
                                "s": "#6e7e52"})


def baurusuchus():
    return croc("baurusuchus", {"b": "#9a6e44", "c": "#e0cca4", "d": "#4e3420", "n": "#2e1e12",
                                "s": "#b88a58"}, tall=True)


NEW_SPECIES = ["tarbosaurus", "daspletosaurus", "albertosaurus", "giganotosaurus", "carcharodontosaurus",
               "carnotaurus", "majungasaurus", "dakotaraptor", "troodon", "struthiomimus", "oviraptor",
               "therizinosaurus", "deinocheirus", "thescelosaurus", "edmontosaurus", "corythosaurus",
               "styracosaurus", "pachyrhinosaurus", "protoceratops", "euoplocephalus", "alamosaurus",
               "saltasaurus", "argentinosaurus", "opisthocoelicaudia", "dreadnoughtus", "quetzalcoatlus",
               "hatzegopteryx", "hesperornis", "ichthyornis", "tylosaurus", "elasmosaurus", "xiphactinus",
               "archelon", "deinosuchus", "baurusuchus", "citipati", "mononykus", "didelphodon", "leptoceratops", "vegavis", "mesodma", "basilemys", "enchodus", "lepisosteus"]


ORDER = ["tyrannosaurus", "spinosaurus", "dilophosaurus", "velociraptor", "compsognathus", "triceratops",
         "stegosaurus", "ankylosaurus", "brachiosaurus", "parasaurolophus", "pachycephalosaurus", "gallimimus",
         "maiasaura", "pteranodon", "mosasaurus"] + NEW_SPECIES


def render(name):
    return globals()[name]().render()
