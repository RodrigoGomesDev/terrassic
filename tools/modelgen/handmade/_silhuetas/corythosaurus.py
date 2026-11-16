"""Coritossauro, "o pavão da mata": três blocagens (9 m)."""
from sil import Sil

ID = "corythosaurus"
NAME = "Coritossauro"
THEME = "o pavão da mata"


def cory_head(s, parent, p, ang, helmet):
    """cabeça pequena e estreita, bico curto; o elmo (exagerado) é desenhado por `helmet(s, osso, p)`"""
    h = s.head("head", parent, p, ang, 0.75, 0.75, 0.6, bill=(0.45, 0.32, 0.5), low=0.0)
    helmet(s, h, p)
    return h


def plate(s, h, p):
    """elmo em prato vertical: disco alto e fino, maior que a cabeça inteira"""
    for along, up, hgt, lng in ((0.45, 0.95, 1.7, 0.9), (0.4, 0.9, 1.3, 1.35), (0.4, 0.75, 0.7, 1.65)):
        s.box(h, s.at(p, along, up), (0.25, hgt, lng))


def fan(s, h, p):
    """elmo em leque alto, varrido para trás como uma crista de cacatua"""
    s.box(h, s.at(p, 0.45, 0.6), (0.25, 0.6, 0.9))
    s.box(h, s.at(p, 0.25, 1.3), (0.22, 1.5, 0.7), rot=(-28, 0, 0))
    s.box(h, s.at(p, -0.05, 1.5), (0.2, 1.6, 0.55), rot=(-48, 0, 0))
    s.box(h, s.at(p, 0.55, 1.05), (0.22, 1.0, 0.5), rot=(-10, 0, 0))


def moon(s, h, p):
    """elmo em meia-lua grande, a frente subindo íngreme do focinho"""
    s.box(h, s.at(p, 0.55, 0.7), (0.26, 0.9, 1.1))
    s.box(h, s.at(p, 0.4, 1.15), (0.24, 0.6, 1.2))
    s.box(h, s.at(p, 0.3, 1.5), (0.22, 0.35, 0.8))
    s.box(h, s.at(p, 0.95, 0.6), (0.24, 0.7, 0.35), rot=(25, 0, 0))


def sail(s, bone, z0, z1, y, hgt, steps=5):
    """vela baixa dos espinhos neurais: degraus que sobem até o meio e descem"""
    n = steps; L = (z1 - z0) / n
    for i in range(n):
        k = 1 - abs((i + 0.5) / n - 0.5) * 1.2
        s.box(bone, (0, y + hgt * k / 2, z0 + L * (i + 0.5)), (0.3, hgt * k, L + 0.02))


def tall_plate():
    """A: elmo em prato vertical, pescoço em S, vela baixa"""
    s = Sil("cory_a")
    s.bone("body", "root", (0, 3.3, 0.8), (12, 0, 0))
    s.box("body", (0, 3.25, -0.6), (1.4, 1.5, 3.2))
    s.box("body", (0, 3.3, 0.8), (1.3, 1.5, 1.3))
    sail(s, "body", -1.9, 1.3, 3.95, 0.75)
    nb, npt = s.chain("neck", "body", (0, 3.55, -2.1), [(0.85, 0.75, 0.85, 50), (0.75, 0.65, 0.75, 15),
                                                         (0.55, 0.6, 0.65, -45)])
    cory_head(s, nb[-1], npt[-1], -30, plate)
    tb, tpt = s.chain("tail", "root", (0, 3.45, 1.4), [(1.3, 0.95, 1.05, 10), (1.2, 0.7, 0.75, 2), (1.1, 0.5, 0.5, 0),
                                                       (1.0, 0.32, 0.35, 2)], "back")
    sail(s, tb[0], 1.4, 2.6, 3.9, 0.5, 3)
    s.legs("hind", "root", (0, 3.15, 0.8), [(1.45, 0.65, 0.95, 12), (1.3, 0.42, 0.5, -28), (0.5, 0.4, 0.55, 16)], 0.55)
    s.legs("arm", "body", (0, 2.85, -1.9), [(1.45, 0.4, 0.45, -14), (1.68, 0.32, 0.36, 4), (0.3, 0.4, 0.45, 0)], 0.5)
    s.feet = ("hind", "arm")
    return s


def high_fan():
    """B: elmo em leque alto, pescoço de girafa"""
    s = Sil("cory_b")
    s.bone("body", "root", (0, 3.3, 0.8), (18, 0, 0))
    s.box("body", (0, 3.25, -0.6), (1.4, 1.5, 3.1))
    s.box("body", (0, 3.3, 0.8), (1.3, 1.5, 1.3))
    sail(s, "body", -1.9, 1.3, 3.95, 1.1, 6)
    nb, npt = s.chain("neck", "body", (0, 3.6, -2.1), [(0.9, 0.75, 0.85, 62), (0.85, 0.65, 0.75, 8),
                                                        (0.5, 0.6, 0.65, -20)])
    cory_head(s, nb[-1], npt[-1], -55, fan)
    tb, tpt = s.chain("tail", "root", (0, 3.45, 1.4), [(1.3, 0.95, 1.05, 14), (1.2, 0.7, 0.75, 4), (1.1, 0.5, 0.5, 0),
                                                       (1.0, 0.32, 0.35, -4)], "back")
    sail(s, tb[0], 1.4, 2.6, 3.9, 0.8, 3)
    s.legs("hind", "root", (0, 3.15, 0.8), [(1.45, 0.65, 0.95, 12), (1.3, 0.42, 0.5, -28), (0.5, 0.4, 0.55, 16)], 0.55)
    s.legs("arm", "body", (0, 2.85, -1.9), [(1.6, 0.4, 0.45, -20), (1.83, 0.32, 0.36, 4), (0.3, 0.4, 0.45, 0)], 0.5)
    s.feet = ("hind", "arm")
    return s


def biped():
    """C: corredor em duas patas, cauda alta, elmo em meia-lua"""
    s = Sil("cory_c")
    s.bone("body", "root", (0, 3.4, 0.8), (26, 0, 0))
    s.box("body", (0, 3.35, -0.5), (1.35, 1.45, 2.8))
    s.box("body", (0, 3.4, 0.8), (1.3, 1.5, 1.3))
    sail(s, "body", -1.6, 1.3, 4.05, 0.7)
    nb, npt = s.chain("neck", "body", (0, 3.65, -1.8), [(0.85, 0.75, 0.85, 30), (0.75, 0.65, 0.75, 10),
                                                         (0.55, 0.6, 0.65, -40)])
    cory_head(s, nb[-1], npt[-1], -40, moon)
    tb, tpt = s.chain("tail", "root", (0, 3.55, 1.4), [(1.3, 0.95, 1.05, 18), (1.2, 0.7, 0.75, 6), (1.1, 0.5, 0.5, 4),
                                                       (1.1, 0.32, 0.35, 4)], "back")
    sail(s, tb[0], 1.4, 2.6, 4.0, 0.45, 3)
    # passada: a esquerda à frente, a direita atrás
    s.chain("hind_l", "root", (0, 3.25, 0.8), [(1.5, 0.65, 0.95, 38), (1.35, 0.42, 0.5, -45), (0.55, 0.4, 0.55, 10)],
            "down", x=0.55)
    s.chain("hind_r", "root", (0, 3.25, 0.8), [(1.5, 0.65, 0.95, -18), (1.35, 0.42, 0.5, -30), (0.72, 0.4, 0.55, 60)],
            "down", x=-0.55)
    s.legs("arm", "body", (0, 2.85, -1.6), [(0.8, 0.3, 0.36, 10), (0.7, 0.26, 0.28, 60), (0.2, 0.32, 0.36, 10)], 0.5)
    s.feet = ("hind",)
    return s


VARIANTS = [
    ("A", "prato vertical", "elmo em disco alto e fino, mais alto que a cabeça inteira, no alto de um pescoço em S; "
     "vela baixa de espinhos nas costas", tall_plate),
    ("B", "leque alto", "elmo em leque varrido para trás como crista de cacatua, pescoço quase vertical e vela alta",
     high_fan),
    ("C", "corredor bípede", "em duas patas a passos longos, tronco inclinado e cauda alta; elmo em meia-lua grande",
     biped),
]
