"""Front-view 32x32 spawn-egg designs (v5), one function per species, drawn on eggfront.Egg."""
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


ORDER = ["tyrannosaurus", "spinosaurus", "dilophosaurus", "velociraptor", "compsognathus", "triceratops",
         "stegosaurus", "ankylosaurus", "brachiosaurus", "parasaurolophus", "pachycephalosaurus", "gallimimus",
         "maiasaura", "pteranodon", "mosasaurus"]


def render(name):
    return globals()[name]().render()
