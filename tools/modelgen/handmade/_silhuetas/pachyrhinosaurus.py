"""Paquirrinossauro, "o aríete": três blocagens (8 m)."""
from sil import Sil

ID = "pachyrhinosaurus"
NAME = "Paquirrinossauro"
THEME = "o aríete"


def pachy_head(s, parent, p, ang, frill_tilt=55, frill=(2.4, 1.7), spikes=1.0, hook=(-20, -60, -50)):
    """cabeça enorme (~1/3 do bicho) num pescoço curto e estreito: crânio fundo, bossa nasal larga e chata que avança
    como a cabeça de um aríete, bico curto em gancho embaixo; gola curta e larga atrás (frill_tilt = graus deitada para
    trás a partir da vertical), com dois espinhos grossos que curvam para a frente"""
    nk = s.bone("neck", parent, p, (ang * 0.4, 0, 0))
    s.box(nk, s.at(p, 0.25, -0.1), (1.3, 1.2, 0.7))
    q = s.at(p, 0.5)
    h = s.head("head", nk, q, ang * 0.6, 1.6, 1.65, 1.45)
    s.box(h, s.at(q, 1.75, 0.35), (1.8, 1.0, 1.2))         # bossa nasal: larga, chata, a frente reta
    s.box(h, s.at(q, 2.0, -0.45), (0.7, 0.75, 0.6))        # bico em gancho embaixo da bossa
    s.box(h, s.at(q, 0.75, 0.95), (1.3, 0.3, 0.8))         # bossa da testa
    s.box(h, s.at(q, 0.75, -0.95), (1.1, 0.35, 1.1))       # mandíbula funda
    fw, fl = frill
    base = s.at(q, 0.1, 0.6)
    fb = s.bone("frill", h, base, (frill_tilt, 0, 0))
    s.box(fb, s.at(base, 0.0, fl / 2), (fw, fl, 0.5))
    s.box(fb, s.at(base, -0.1, fl * 0.3), (fw * 0.85, fl * 0.6, 0.6))
    for sx in (0.7, -0.7):
        top = (sx, base[1] + fl - 0.15, base[2])
        s.chain(f"spike{'l' if sx > 0 else 'r'}", fb, top, [(0.45 * spikes, 0.4, 0.4, hook[0]), (0.4 * spikes, 0.32, 0.32, hook[1]),
                                                            (0.3 * spikes, 0.22, 0.22, hook[2])], "fwd", x=sx)
    return h


def legs(s, hip_y, sh_y, hind=(0.8, 0.6, 0.25), arm=(0.75, 0.55, 0.25), hz=1.3, az=-0.9, hang=(6, -10, 4),
         aang=(-4, 6, 0)):
    s.legs("hind", "root", (0, hip_y, hz), [(hind[0], 0.8, 0.95, hang[0]), (hind[1], 0.62, 0.65, hang[1]),
                                            (hind[2], 0.8, 0.85, hang[2])], 0.8)
    s.legs("arm", "root", (0, sh_y, az), [(arm[0], 0.75, 0.8, aang[0]), (arm[1], 0.6, 0.65, aang[1]),
                                          (arm[2], 0.75, 0.8, aang[2])], 0.85)


def hump(s, bone, z, top, w=2.1):
    """corcova de bisão: frente íngreme, trás em rampa"""
    s.box(bone, (0, top - 0.7, z), (w, 1.4, 1.3))
    s.box(bone, (0, top - 1.0, z + 1.1), (w * 0.95, 1.4, 1.8), rot=(-20, 0, 0))


def mound(s, bone, profile, w=2.4, floor=1.6):
    """o lombo como uma fileira de fatias (z, topo): a corcova sai do perfil, sem caixa solta em cima"""
    for i, (z, top) in enumerate(profile):
        z1 = profile[i + 1][0] if i + 1 < len(profile) else z + 0.5
        L = z1 - z
        s.box(bone, (0, (top + floor) / 2, z + L / 2), (w, top - floor, L + 0.04))


def ram():
    """A: aríete: cabeça baixa à frente na altura do peito, corcova nos ombros"""
    s = Sil("pachy_a")
    s.box("root", (0, 1.9, 0.5), (2.7, 1.9, 3.0))          # barril
    hump(s, "root", -0.2, 3.45, 2.2)
    s.box("root", (0, 2.05, -1.0), (2.3, 1.6, 0.9))        # peito
    s.box("root", (0, 1.1, 0.3), (2.4, 0.5, 2.4))          # barriga
    pachy_head(s, "root", (0, 1.55, -1.45), -6, frill_tilt=40, frill=(2.4, 1.3), spikes=1.7, hook=(10, -75, -70))
    s.chain("tail", "root", (0, 2.1, 2.0), [(0.8, 0.95, 0.95, -20), (0.6, 0.6, 0.6, -10), (0.45, 0.32, 0.32, -5)], "back")
    legs(s, 1.6, 1.55)
    return s


def bison():
    """B: bisão: corcova enorme, costas em rampa para trás, cabeça pendurada para baixo"""
    s = Sil("pachy_b")
    mound(s, "root", [(-1.55, 2.9), (-1.2, 3.55), (-0.85, 3.9), (-0.45, 3.85), (-0.05, 3.6), (0.35, 3.3), (0.75, 3.0),
                      (1.15, 2.7), (1.55, 2.45), (1.95, 2.25)], w=2.5, floor=1.1)
    s.box("root", (0, 1.15, 0.0), (2.3, 0.5, 2.4))         # barriga
    pachy_head(s, "root", (0, 2.2, -1.55), -32, frill_tilt=55, frill=(2.5, 1.5), spikes=1.5, hook=(-5, -70, -60))
    s.chain("tail", "root", (0, 1.9, 2.3), [(0.7, 0.85, 0.85, -30), (0.55, 0.55, 0.55, -10), (0.4, 0.3, 0.3, -5)], "back")
    legs(s, 1.45, 1.85, hind=(0.82, 0.5, 0.25), arm=(0.95, 0.7, 0.3), hz=1.4, az=-1.0)
    return s


def shield():
    """C: escudo: cabeça erguida, gola em pé como um escudo, espinhos sobre a bossa; traseiro agachado"""
    s = Sil("pachy_c")
    s.bone("body", "root", (0, 1.7, 1.3), (12, 0, 0))
    s.box("body", (0, 1.9, 0.4), (2.7, 1.9, 3.0))
    hump(s, "body", -0.6, 2.9)
    s.box("body", (0, 1.95, -1.15), (2.3, 1.9, 1.0))
    s.box("body", (0, 1.1, 0.2), (2.4, 0.5, 2.4))
    pachy_head(s, "body", (0, 2.2, -1.6), 30, frill_tilt=25, frill=(3.2, 2.4), spikes=1.4, hook=(10, -70, -60))
    s.chain("tail", "root", (0, 1.9, 1.8), [(0.8, 0.95, 0.95, -25), (0.6, 0.6, 0.6, 5), (0.45, 0.32, 0.32, 8)], "back")
    s.legs("hind", "root", (0, 1.6, 1.3), [(0.8, 0.8, 0.95, 40), (0.65, 0.62, 0.65, -60), (0.25, 0.8, 0.9, 20)], 0.8)
    s.legs("arm", "body", (0, 1.5, -0.9), [(0.85, 0.75, 0.8, 4), (0.75, 0.6, 0.65, -14), (0.3, 0.75, 0.8, 0)], 0.95)
    return s


VARIANTS = [
    ("A", "aríete", "cabeça enorme (um terço do bicho) levada baixa e reta como um aríete, bossa chata na frente; "
     "corcova de bisão sobre um barril de pernas curtas", ram),
    ("B", "bisão", "corcova enorme e costas descendo em rampa até a cauda curta; a cabeça pendura para baixo, "
     "bossa apontada para o chão", bison),
    ("C", "escudo", "cabeça erguida e gola em pé como um escudo, os dois espinhos curvando por cima da bossa; "
     "traseiro agachado", shield),
]
