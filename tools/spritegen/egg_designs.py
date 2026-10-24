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
    e = Egg("tyrannosaurus", {"b": "#7a5c3c", "c": "#d2bc90", "d": "#3a2818", "n": "#3a2a1a",
                               "R": MOUTH})
    cap(e, "d", (5, 2, 26, 18), (3, 9, 28, 36))
    for (x0, y0, x1, y1) in ((4, 15, 7, 12), (4, 19, 7, 16)):
        e.line([(x0, y0), (x1, y1)], "n", 2, clip=True)
        e.line([(31 - x0, y0), (31 - x1, y1)], "n", 2, clip=True)
    # big boxy jaw
    e.rect((6, 23, 25, 31), "c", clip=True)
    e.line([(8, 30), (23, 30)], "C", clip=True)
    e.pal["C"] = "#b8a074"
    e.line([(6, 22), (25, 22)], "R")
    e.px(e.mirror([(6, 21)]), "R")
    e.pal["W"] = TOOTH
    for x in (9, 13):
        e.px(e.mirror([(x, 23), (x, 24), (x + 1, 23)]), "W")
    eyes(e, 14, 9, iris="#f0b42a", brow="n", angry=True)
    e.px(e.mirror([(13, 19), (12, 19)]), "n")
    e.px(e.mirror([(10, 11), (11, 11), (12, 12)]), "n")
    return e


def spinosaurus():
    e = Egg("spinosaurus", {"b": "#5e7a74", "c": "#a8b8a8", "d": "#2c403c", "n": "#2e403c",
                             "e": "#c4461e", "f": "#f0a03a", "R": MOUTH})
    e.poly([(9, 7), (11, 1), (14, 0), (17, 0), (20, 1), (22, 7)], "e")
    for x in (12, 15, 16, 19):
        e.line([(x, 2 if x in (12, 19) else 1), (x, 6)], "D")
    e.pal["D"] = "#8a2c16"
    e.line([(11, 1), (14, 0), (17, 0), (20, 1)], "f")
    cap(e, "d", (6, 5, 25, 18), (4, 11, 27, 36))
    e.rect((12, 15, 19, 31), "c", clip=True)
    e.ell((11, 26, 20, 33), "c", clip=True)
    e.rect((13, 15, 18, 16), "C")
    e.pal["C"] = "#7e928a"
    eyes(e, 13, 9, iris="#e8b232", brow="n", angry=True)
    nostrils(e, 18, 14)
    e.line([(12, 27), (19, 27)], "R")
    fangs(e, 28, [13])
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
    e = Egg("velociraptor", {"b": "#9a6a40", "c": "#e2cca2", "d": "#4a2c18", "n": "#2e2014",
                              "f": "#4a2e1a", "R": MOUTH})
    for (x, h) in ((11, 3), (13, 5), (15, 6), (17, 5), (19, 3)):
        e.line([(x, 5 - h + 1), (x + (1 if x < 15 else -1 if x > 16 else 0), 6)], "f", 2)
    cap(e, "d", (6, 4, 25, 17), (3, 9, 28, 36))
    for (x0, y0, x1, y1) in ((4, 18, 7, 15), (4, 23, 7, 20)):
        e.line([(x0, y0), (x1, y1)], "n", 2, clip=True)
        e.line([(31 - x0, y0), (31 - x1, y1)], "n", 2, clip=True)
    e.poly([(11, 17), (20, 17), (22, 31), (9, 31)], "c", clip=True)
    e.px([(15, 1), (16, 1), (13, 2), (18, 2)], "F")
    e.pal["F"] = "#b07a44"
    eyes(e, 14, 9, iris="#f4c22c", brow="n", angry=True)
    nostrils(e, 20, 13)
    e.line([(9, 25), (22, 25)], "R")
    for x in (11, 14):
        e.px(e.mirror([(x, 26)]), "W")
    e.pal["W"] = TOOTH
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
    e = Egg("triceratops", {"b": "#7b6c56", "c": "#b5a684", "e": "#bb4628", "w": "#ecdcb8",
                             "D": "#6e2414", "i": "#f2e8cc", "j": "#b8a87e", "k": "#3e342a", "n": "#4a3e30"})
    # frill peeking around the top of the egg
    e.ell((1, 0, 30, 22), "w")
    e.ell((3, 2, 28, 20), "e")
    for (cx, cy) in ((7, 9), (12, 5), (19, 5), (24, 9)):
        e.px([(cx, cy - 1), (cx - 1, cy), (cx + 1, cy), (cx, cy + 1)], "w")
        e.px([(cx, cy)], "D")
    for (x, y) in ((2, 8), (5, 3), (10, 0), (15, 0), (16, 0), (21, 0), (26, 3), (29, 8)):
        e.px([(x, y - 1)], "w")
    e.ell((6, 9, 25, 40), "b")
    e.ell((9, 9, 22, 20), "d", clip=True)
    e.pal["d"] = "#665844"
    for y in range(N):
        for x in range(N):
            if y > 18 and not in_egg(x, y):
                e.set(x, y, "_")
    e.ell((9, 21, 22, 33), "c", clip=True)
    e.poly([(5, 20), (5, 23), (3, 22)], "i")
    e.poly([(26, 20), (26, 23), (28, 22)], "i")
    # brow horns and nose horn
    for side in (0, 1):
        pts = [(10, 13), (12, 12), (9, 4), (8, 5)]
        if side:
            pts = [(31 - x, y) for (x, y) in pts]
        e.poly(pts, "i")
    e.line(e.mirror([(11, 12), (9, 6)])[:2], "j")
    e.line([(20, 12), (22, 6)], "j")
    eyes(e, 15, 9)
    e.poly([(14, 22), (17, 22), (16, 17), (15, 17)], "i")
    e.poly([(13, 26), (18, 26), (17, 30), (14, 30)], "k")
    nostrils(e, 24, 13)
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
    e = Egg("parasaurolophus", {"b": "#468070", "c": "#d8d2ac", "d": "#24443c", "n": "#1e3a34",
                                 "e": "#c43c28", "y": "#f2c866", "m": "#c09a68", "M": "#4a3e30"})
    e.line([(15, 8), (8, 0)], "e", 4)
    e.line([(13, 4), (11, 6)], "y")
    e.line([(10, 1), (8, 3)], "y")
    cap(e, "d", (6, 5, 25, 17), (3, 10, 28, 36))
    e.line([(15, 8), (8, 0)], "e", 4)
    e.line([(13, 4), (11, 6)], "y")
    e.line([(10, 1), (8, 3)], "y")
    for y in (18, 21):
        e.line([(4, y), (7, y)], "d", clip=True)
        e.line([(24, y), (27, y)], "d", clip=True)
    eyes(e, 14, 9, iris="#e0a832")
    # wide duck bill
    e.ell((8, 21, 23, 36), "c", clip=True)
    e.ell((7, 23, 24, 30), "m", clip=True)
    e.line([(9, 27), (22, 27)], "M")
    nostrils(e, 25, 12, "M")
    return e


def pachycephalosaurus():
    e = Egg("pachycephalosaurus", {"b": "#7c6448", "c": "#d6c4a0", "e": "#ddb878", "i": "#a8865a",
                                    "I": "#f2e6c8", "d": "#4e3c2a", "n": "#3a2c1e", "R": MOUTH})
    e.ell((4, 2, 27, 21), "e", clip=True)
    for y in range(13, 22):
        for x in range(N):
            if e.get(x, y) == "e" and y >= 13:
                e.set(x, y, "b")
    for x in range(5, 27, 3):
        e.px([(x, 12), (x + 1, 12)], "I")
        e.px([(x, 13)], "i")
    e.poly([(4, 12), (4, 14), (1, 12)], "I")
    e.poly([(27, 12), (27, 14), (30, 12)], "I")
    for p in ((10, 5), (14, 3), (19, 5), (12, 8), (17, 8), (21, 9), (8, 9)):
        e.px([p], "i")
    e.ell((8, 19, 23, 34), "c", clip=True)
    e.px(e.mirror([(9, 22), (8, 24), (10, 25)]), "I")
    eyes(e, 15, 9, iris="#e8a83a", brow="d")
    nostrils(e, 21, 13)
    e.line([(11, 26), (20, 26)], "R")
    return e


def gallimimus():
    e = Egg("gallimimus", {"b": "#aaa498", "c": "#f0ece2", "d": "#4a4642", "n": "#3a3632",
                            "m": "#4e4844", "M": "#7a7268"})
    e.line([(15, 1), (14, 4)], "d", 2)
    e.px([(17, 2), (16, 3)], "d")
    e.ell((6, 2, 25, 18), "d", clip=True)
    e.ell((7, 9, 24, 34), "b", clip=True)
    e.ell((9, 18, 22, 34), "c", clip=True)
    eyes(e, 13, 8, iris="#ee9a2a")
    # long beak pointing down the middle
    e.poly([(13, 15), (18, 15), (17, 27), (16, 29), (15, 29), (14, 27)], "m")
    e.line([(15, 17), (15, 26)], "M")
    nostrils(e, 17, 14, "n")
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
    e = Egg("pteranodon", {"b": "#b8b2a6", "c": "#eeeae0", "d": "#55504a", "n": "#3a3632",
                           "e": "#d0582c", "f": "#f0a04a", "w": "#6a5444", "m": "#d8bc84", "M": "#a88c5a"})
    # folded wings at the sides
    for side in (0, 1):
        pts = [(4, 15), (0, 19), (1, 22), (4, 21)]
        if side:
            pts = [(31 - x, y) for (x, y) in pts]
        e.poly(pts, "w")
    cap(e, "d", (6, 3, 25, 17), (3, 9, 28, 36))
    # long crest sweeping back over the head
    e.line([(17, 8), (6, 0)], "e", 3)
    e.line([(8, 1), (6, 0)], "f", 2)
    e.ell((9, 18, 22, 34), "c", clip=True)
    eyes(e, 13, 9)
    # long toothless beak down the middle
    e.poly([(13, 15), (18, 15), (17, 28), (16, 30), (15, 30), (14, 28)], "m")
    e.line([(15, 18), (15, 27)], "M")
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
    e = theropod("giganotosaurus", {"b": "#8e7e56", "c": "#dccc9c", "d": "#5a4c30", "n": "#3e3420",
                                    "e": "#b84a2a"}, stripes=((4, 16, 7, 13), (4, 20, 7, 17)))
    e.line([(11, 9), (20, 9)], "e", 2)
    return e


def carcharodontosaurus():
    e = theropod("carcharodontosaurus", {"b": "#8e5a42", "c": "#dcc2a0", "d": "#5a3424", "n": "#3e2418"},
                 teeth=(8, 10, 12, 14))
    e.px(e.mirror([(9, 10), (10, 10), (11, 11)]), "n")
    return e


def carnotaurus():
    e = theropod("carnotaurus", {"b": "#7a786a", "c": "#d0ccb8", "d": "#4a4a40", "n": "#30302a",
                                 "e": "#8a2e22", "i": "#e8dcc0"}, jaw="narrow", teeth=(10, 13),
                 cap_top=(5, 4, 26, 18))
    # the two bull horns
    _side(e, [(8, 9), (11, 9), (7, 3), (6, 4)], "i")
    for p in ((7, 18), (6, 21), (8, 23)):
        e.px(e.mirror([p]), "n")
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
    e = ceratopsian("protoceratops", {"b": "#9a8460", "c": "#dccaa0", "e": "#a8483a", "w": "#e8d8b4",
                                      "D": "#6e2a20", "i": "#f2e8cc", "j": "#c8b48c", "d": "#7a6648",
                                      "n": "#4e3e2a"}, frill=(4, 2, 27, 20), knobs=((10, 7), (21, 7)),
                    brow=False, nose=None)
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
               "archelon", "deinosuchus", "baurusuchus", "citipati", "mononykus", "didelphodon", "leptoceratops", "vegavis", "mesodma", "basilemys"]


ORDER = ["tyrannosaurus", "spinosaurus", "dilophosaurus", "velociraptor", "compsognathus", "triceratops",
         "stegosaurus", "ankylosaurus", "brachiosaurus", "parasaurolophus", "pachycephalosaurus", "gallimimus",
         "maiasaura", "pteranodon", "mosasaurus"] + NEW_SPECIES


def render(name):
    return globals()[name]().render()
