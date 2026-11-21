"""Maiassauro, "a mãe pesada": três blocagens (9 m)."""
from sil import Sil

ID = "maiasaura"
NAME = "Maiassauro"
THEME = "a mãe pesada"


def maia_head(s, parent, p, ang):
    """cabeça curta e funda, bico largo caído, calombo sólido na frente dos olhos"""
    h = s.head("head", parent, p, ang, 0.95, 1.1, 1.0, bill=(0.8, 0.55, 1.3), low=0.1)
    s.box(h, s.at(p, 0.8, 0.62), (0.8, 0.5, 0.7))        # calombo sólido na frente dos olhos
    return h


def hippo():
    """A: quadrúpede-hipopótamo em rampa: anca alta, ombro baixo, barriga caída, cabeça no chão"""
    s = Sil("maia_a")
    s.box("root", (0, 2.0, -0.3), (2.3, 2.1, 3.6), rot=(-12, 0, 0))   # barril inclinado para a frente
    s.box("root", (0, 1.05, -0.4), (2.0, 0.6, 2.8))       # barriga caída, quase no chão
    s.box("root", (0, 2.75, 1.2), (2.0, 2.0, 1.8))        # anca alta
    s.box("root", (0, 3.85, 1.1), (1.4, 0.4, 1.4))        # topo da anca (o ponto mais alto)
    s.box("root", (0, 1.55, -2.1), (1.8, 1.5, 1.1))       # ombro baixo
    nb, npt = s.chain("neck", "root", (0, 1.75, -2.5), [(0.8, 1.35, 1.45, -34), (0.6, 1.2, 1.3, -8)])
    maia_head(s, nb[-1], npt[-1], 38)
    s.chain("tail", "root", (0, 3.1, 2.0), [(1.2, 1.6, 1.6, -26), (1.1, 1.2, 1.2, -6), (1.0, 0.9, 0.9, -2),
                                             (1.0, 0.6, 0.6, 4), (0.9, 0.38, 0.38, 6)], "back")
    s.legs("hind", "root", (0, 2.5, 1.2), [(1.3, 0.85, 1.1, 4), (0.85, 0.7, 0.75, -8), (0.35, 0.85, 0.95, 4)], 0.8)
    s.legs("arm", "root", (0, 1.3, -2.1), [(0.7, 0.75, 0.8, 0), (0.45, 0.7, 0.7, 0), (0.2, 0.8, 0.8, 0)], 0.75)
    return s


def arch():
    """B: costas em ponte, pastando"""
    s = Sil("maia_b")
    s.box("root", (0, 2.5, 0.0), (2.1, 2.0, 2.4))         # meio do arco
    s.box("root", (0, 3.55, 0.0), (1.5, 0.4, 1.5))        # pico das costas
    s.box("root", (0, 2.2, 1.4), (1.9, 1.8, 1.4), rot=(-30, 0, 0))   # anca descendo para trás
    s.box("root", (0, 2.05, -1.4), (1.9, 1.7, 1.4), rot=(30, 0, 0))  # ombro descendo para a frente
    s.box("root", (0, 1.35, 0.0), (1.9, 0.5, 2.0))        # barriga funda
    nb, npt = s.chain("neck", "root", (0, 2.0, -2.0), [(0.8, 1.35, 1.35, -38), (0.55, 1.2, 1.2, -10)])
    maia_head(s, nb[-1], npt[-1], 28)
    s.chain("tail", "root", (0, 2.3, 2.0), [(1.0, 1.5, 1.5, -35), (1.0, 1.1, 1.1, -15), (1.0, 0.75, 0.75, 10),
                                             (0.9, 0.45, 0.4, 25)], "back")
    s.legs("hind", "root", (0, 1.9, 1.3), [(1.0, 0.9, 1.1, -2), (0.7, 0.75, 0.8, 0), (0.3, 0.9, 0.95, 2)], 0.75)
    s.legs("arm", "root", (0, 1.7, -1.4), [(0.95, 0.8, 0.85, 2), (0.6, 0.7, 0.75, 0), (0.25, 0.8, 0.8, -2)], 0.75)
    return s


def rear():
    """C: mãe meio empinada, em tripé com a cauda, olhando para baixo (o ninho)"""
    s = Sil("maia_c")
    s.bone("body", "root", (0, 2.4, 0.9), (34, 0, 0))
    s.box("body", (0, 2.55, -0.4), (2.2, 2.0, 2.8))        # tronco
    s.box("body", (0, 1.25, -0.7), (2.1, 1.1, 2.3))        # barriga enorme, pendurada para a frente
    s.box("body", (0, 2.6, 0.9), (2.0, 1.9, 1.4))          # quadril
    s.box("body", (0, 2.45, -2.0), (1.8, 1.7, 0.8))        # peito
    nb, npt = s.chain("neck", "body", (0, 2.95, -2.2), [(0.8, 1.0, 1.1, 8), (0.7, 0.9, 1.0, -42)])
    maia_head(s, nb[-1], npt[-1], -22)
    # antebraços grossos pendurados na frente da barriga, mãos fora do chão
    s.legs("arm", "body", (0, 2.2, -2.3), [(1.0, 0.85, 0.9, -6), (0.85, 0.75, 0.8, 14), (0.3, 0.85, 0.85, 20)], 0.8)
    s.chain("tail", "root", (0, 2.1, 1.7), [(1.3, 1.6, 1.5, -36), (1.2, 1.15, 1.0, 26), (1.1, 0.8, 0.65, 10),
                                             (0.9, 0.5, 0.45, 4)], "back")
    s.legs("hind", "root", (0, 2.3, 0.9), [(1.2, 1.0, 1.3, 22), (1.0, 0.72, 0.72, -42), (0.35, 0.9, 1.15, 20)], 0.8)
    s.feet = ("hind",)
    return s


VARIANTS = [
    ("A", "hipopótamo em rampa", "anca alta como um morro e tudo descendo para a frente: barriga caída quase no chão, cabeça curta e funda pastando rente",
     hippo),
    ("B", "arco pastando", "costas em ponte: o pico no meio, a cabeça pastando e a cauda caindo até perto do chão",
     arch),
    ("C", "mãe empinada", "meio empinada sobre as patas e a cauda grossa em tripé, a barriga enorme à mostra, braços grossos pendurados e a cabeça baixa olhando o ninho",
     rear),
]
