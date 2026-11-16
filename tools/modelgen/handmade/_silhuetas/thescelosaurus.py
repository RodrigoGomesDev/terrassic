"""Tescelossauro, "o corredor": três blocagens (4 m)."""
from sil import Sil

ID = "thescelosaurus"
NAME = "Tescelossauro"
THEME = "o corredor"


def thes_head(s, parent, p, ang):
    """cabeça pequena e comprida, focinho estreito, as placas da bochecha saltando dos lados"""
    h = s.head("head", parent, p, ang, 0.32, 0.3, 0.26, bill=(0.22, 0.17, 0.18), low=0.0)
    s.box(h, s.at(p, 0.2, -0.04), (0.38, 0.14, 0.16))     # placas da bochecha (largas)
    s.box(h, s.at(p, 0.12, 0.16), (0.2, 0.06, 0.16))      # sobrancelha (palpebral)
    return h


def tail(s, parent, start, rise, n=5, L=0.62, w0=0.42, curl=0.0):
    """cauda muito longa e rígida (tendões ossificados): sobe `rise` graus na base e segue reta"""
    segs = []
    w = w0
    for i in range(n):
        segs.append((L, w, w * 1.1, rise if i == 0 else curl))
        w *= 0.72
    return s.chain("tail", parent, start, segs, "back")


def leg(s, side, hip, angs, x, thigh=(0.55, 0.42, 0.66)):
    """coxa grossa, canela longa e fina, metatarso longo, dedos"""
    a, b, c, d = angs
    return s.chain(f"hind_{side}", "root", hip, [(thigh[0], thigh[1], thigh[2], a), (0.66, 0.15, 0.2, b),
                                                  (0.42, 0.12, 0.14, c), (0.2, 0.16, 0.12, d)], "down", x=x)


def bird():
    """A: tipo ave: tronco curto empinado, pescoço em S, coxas grossas e canelas longas"""
    s = Sil("thes_a")
    s.bone("body", "root", (0, 1.25, 0.3), (22, 0, 0))
    s.box("body", (0, 1.25, -0.25), (0.62, 0.72, 1.2))
    s.box("body", (0, 1.3, 0.3), (0.58, 0.68, 0.5))
    nb, npt = s.chain("neck", "body", (0, 1.45, -0.8), [(0.32, 0.26, 0.3, 50), (0.28, 0.22, 0.25, 0),
                                                         (0.2, 0.2, 0.22, -60)])
    thes_head(s, nb[-1], npt[-1], -12)
    s.legs("arm", "body", (0, 1.1, -0.65), [(0.22, 0.1, 0.1, 30), (0.2, 0.08, 0.08, 50)], 0.3)
    tail(s, "root", (0, 1.4, 0.5), 14, n=5, L=0.62)
    leg(s, "l", (0, 1.2, 0.3), (32, -70, 52, 76), 0.3)
    leg(s, "r", (0, 1.2, 0.3), (10, -55, 58, 77), -0.3)
    s.feet = ("hind",)
    return s


def lizard():
    """B: lagarto corredor: baixo e horizontal, passada aberta, cauda reta erguida"""
    s = Sil("thes_b")
    s.box("root", (0, 0.95, -0.2), (0.6, 0.6, 1.4))
    s.box("root", (0, 1.0, 0.45), (0.56, 0.6, 0.5))
    nb, npt = s.chain("neck", "root", (0, 1.0, -0.9), [(0.35, 0.26, 0.3, 4), (0.3, 0.22, 0.25, -4)])
    thes_head(s, nb[-1], npt[-1], -6)
    s.legs("arm", "root", (0, 0.8, -0.7), [(0.22, 0.1, 0.1, -50), (0.2, 0.08, 0.08, 70)], 0.3)
    tail(s, "root", (0, 1.05, 0.65), 18, n=5, L=0.66)
    leg(s, "l", (0, 1.0, 0.35), (75, -60, 20, 70), 0.3, thigh=(0.55, 0.44, 0.68))
    leg(s, "r", (0, 1.0, 0.35), (-35, -10, 25, 60), -0.3, thigh=(0.55, 0.44, 0.68))
    s.feet = ("hind",)
    return s


def ambush():
    """C: de tocaia: agachado, barriga quase no chão, cabeça rente à frente, cauda erguida como uma vara"""
    s = Sil("thes_c")
    s.box("root", (0, 0.6, -0.2), (0.66, 0.55, 1.3))
    s.box("root", (0, 0.7, 0.45), (0.6, 0.6, 0.6))
    s.box("root", (0.0, 0.95, 0.35), (0.8, 0.55, 0.75))   # ancas para cima, as coxas dobradas dos lados
    nb, npt = s.chain("neck", "root", (0, 0.62, -0.85), [(0.3, 0.26, 0.3, -6), (0.28, 0.22, 0.25, 0)])
    thes_head(s, nb[-1], npt[-1], 0)
    s.legs("arm", "root", (0, 0.45, -0.7), [(0.2, 0.1, 0.1, 30), (0.2, 0.08, 0.08, -30)], 0.32)
    tail(s, "root", (0, 0.8, 0.7), 38, n=5, L=0.62)
    leg(s, "l", (0, 0.75, 0.35), (100, -160, 40, 90), 0.36, thigh=(0.55, 0.46, 0.7))
    leg(s, "r", (0, 0.75, 0.35), (95, -155, 40, 90), -0.36, thigh=(0.55, 0.46, 0.7))
    s.feet = ("hind",)
    return s


VARIANTS = [
    ("A", "tipo ave", "tronco curto e empinado como o de uma ave, pescoço em S; coxas grossas sobre canelas longas e "
     "uma cauda reta do comprimento do resto do bicho", bird),
    ("B", "lagarto corredor", "baixo e na horizontal, em passada aberta; a cauda rígida e muito longa sai para trás e "
     "para cima como uma vara", lizard),
    ("C", "de tocaia", "agachado com as coxas dobradas e a barriga quase no chão, cabeça rente à frente, a cauda "
     "erguida no alto como uma vara", ambush),
]
