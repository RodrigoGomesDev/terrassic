"""Blocagem de silhuetas (1.11, 11/11/2026): o passo "primeiro a silhueta, depois o modelo".

Monta o bicho só com cubos do motor (`_engine/proto.py`: Model/bone/cube) e desenha em PRETO chapado, sem pele, UV,
animação nem QA. Tudo é escrito em METROS e convertido para pixels do jogo (16 px = 1 bloco, 1 m = 1,059 bloco,
`METRE` de gen_species.py), então as blocagens saem no tamanho real que o jogo vai mostrar.

Peças:
- `Sil.box(bone, centro, tamanho, rot)`: um cubo (metros, espaço de repouso do modelo; o bicho olha para -Z).
- `Sil.chain(nome, pai, início, segmentos, dir)`: uma corrente de ossos (pescoço, cauda, perna). Cada segmento é
  (comprimento, largura, altura/espessura, ângulo); o ângulo é ACUMULADO pela hierarquia, como no jogo:
  dir "fwd" (pescoço, cabeça; para -Z): ângulo + levanta a ponta;
  dir "back" (cauda; para +Z): ângulo + levanta a ponta;
  dir "down" (perna; para -Y): ângulo + leva o pé para a FRENTE.
  Devolve os nomes dos ossos e os pontos de repouso (início de cada segmento e o fim).
- `Sil.legs(...)`: o par de pernas (esquerda e direita) com o mesmo desenho.
- `masks/render`: projeção ortográfica das faces (geo.faces) em polígonos, sem z-buffer (é silhueta).
- `load_game(sp)`: um geo.json do jogo, na escala em que o jogo o desenha (MODEL_SCALE x METRE).
- `similarity(a, b)`: semelhança de silhueta (0..1) por Dice das máscaras normalizadas (lado e 3/4), no melhor
  deslocamento pequeno; ver `simcheck.py`.
"""
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "_engine")
sys.path.insert(0, ENGINE)
import geo  # noqa: E402
from proto import Model  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
GEN_SPECIES = os.path.join(ROOT, "tools", "javagen", "gen_species.py")

HUMAN = 1.70
METRE = 1.8 / HUMAN          # blocos por metro (gen_species.METRE)
PX = 16.0 * METRE            # pixels do jogo por metro (16,94)


class Sil:
    def __init__(self, ident):
        self.m = Model(ident)
        self.m.bone("root", None, (0, 0, 0))

    # ------------------------------------------------------------ peças
    def bone(self, name, parent, pivot, rot=(0, 0, 0)):
        self.m.bone(name, parent, [v * PX for v in pivot], rot)
        return name

    def box(self, bone, c, size, rot=(0, 0, 0)):
        """cubo de centro c e tamanho size (metros), girado sobre o próprio centro"""
        lo = [(c[i] - size[i] / 2) * PX for i in range(3)]
        hi = [(c[i] + size[i] / 2) * PX for i in range(3)]
        self.m.cube(bone, lo, hi, rot=list(rot), origin=[v * PX for v in c])

    def chain(self, name, parent, start, segs, dir="fwd", x=0.0):
        """segs: [(comprimento, largura, altura, ângulo)]; devolve (ossos, pontos)"""
        d = {"fwd": (0, 0, -1), "back": (0, 0, 1), "down": (0, -1, 0)}[dir]
        p = [x, start[1], start[2]]
        bones, pts = [], [tuple(p)]
        par = parent
        for i, (L, w, h, ang) in enumerate(segs):
            rot = {"fwd": (ang, 0, 0), "back": (-ang, 0, 0), "down": (ang, 0, 0)}[dir]
            b = self.bone(f"{name}{i}", par, p, rot)
            q = [p[k] + d[k] * L for k in range(3)]
            mid = [(p[k] + q[k]) / 2 for k in range(3)]
            if dir == "down":
                self.box(b, mid, (w, L, h))
            else:
                self.box(b, mid, (w, h, L))
            bones.append(b); par = b; p = q; pts.append(tuple(p))
        return bones, pts

    def head(self, name, parent, p, ang, L, H, W, bill=None, low=0.0):
        """crânio (caixa L x H x W a partir de p, para a frente) e um bico/focinho opcional (Lb, Hb, Wb) na frente,
        apoiado embaixo (low = quanto o bico desce além do crânio); devolve o osso"""
        b = self.bone(name, parent, p, (ang, 0, 0))
        self.box(b, self.at(p, L / 2), (W, H, L))
        if bill:
            Lb, Hb, Wb = bill
            self.box(b, self.at(p, L + Lb / 2 - 0.05, -H / 2 + Hb / 2 - low), (Wb, Hb, Lb))
        return b

    def legs(self, name, parent, hip, segs, spread):
        """par de pernas a +-spread do meio; devolve os ossos (esq, dir) e os pontos da esquerda"""
        bl, pl = self.chain(name + "_l", parent, hip, segs, "down", x=spread)
        br, _ = self.chain(name + "_r", parent, hip, segs, "down", x=-spread)
        return bl, br, pl

    def spec(self):
        m = self.m
        for c in m.cubes:
            c["uv"] = {f: (0, 0, 1, 1) for f in geo.FACES}
        m.tw = m.th = 1
        sp = m.spec()
        if getattr(self, "grounded", True) and m.cubes:
            feet = getattr(self, "feet", ("hind", "arm", "leg"))
            pts = geo.cube_points(sp)
            ys = [p[1] for c, q in pts for p in q if c["bone"].startswith(feet)] or [p[1] for _c, q in pts for p in q]
            dy = -min(ys)
            low = min(p[1] for _c, q in pts for p in q) + dy
            if low < -0.05 * PX:
                print(f"  aviso {m.id}: algo entra {-low / PX:.2f} m no chão")
            grp = {}
            for c, q in pts:
                if c["bone"].startswith(feet):
                    k = c["bone"].rstrip("0123456789")
                    grp[k] = min(grp.get(k, 1e9), min(p[1] for p in q) + dy)
            for k, v in sorted(grp.items()):
                if v > 0.08 * PX and getattr(self, "report_feet", True):
                    print(f"  pé {m.id}/{k}: {v / PX:+.2f} m")
            for b in m.bones:
                b["origin"][1] += dy
            for c in m.cubes:
                c["from"][1] += dy; c["to"][1] += dy; c["origin"][1] += dy
            self.grounded = False
        return sp

    def at(self, p, along=0.0, up=0.0, side=0.0, dir="fwd"):
        """um ponto a `along` metros de p no sentido da corrente (fwd = -z, back = +z, down = -y)"""
        if dir == "down":
            return (p[0] + side, p[1] - along, p[2] - up)    # em perna, 'up' = para a frente
        s = -1 if dir == "fwd" else 1
        return (p[0] + side, p[1] + up, p[2] + s * along)


def human():
    """pessoa de 1,70 m em proporção do Steve (pernas, tronco, cabeça 3:3:2)"""
    s = Sil("human")
    u = HUMAN / 8.0
    s.box("root", (u * 0.5, u * 1.5, 0), (u, u * 3, u))
    s.box("root", (-u * 0.5, u * 1.5, 0), (u, u * 3, u))
    s.box("root", (0, u * 4.5, 0), (u * 2, u * 3, u))
    s.box("root", (u * 1.5, u * 4.5, 0), (u, u * 3, u))
    s.box("root", (-u * 1.5, u * 4.5, 0), (u, u * 3, u))
    s.box("root", (0, u * 7, 0), (u * 2, u * 2, u * 2))
    return s.spec()


# ------------------------------------------------------------ os modelos do jogo
def game_scale(sp):
    """MODEL_SCALE do jogo (tabela SIZES de gen_species.py, vezes METRE)"""
    src = open(GEN_SPECIES).read()
    m = re.search(r'"%s":\s+dict\(real=[^)]*?scale=([0-9.]+)' % sp, src)
    return float(m.group(1)) * METRE


HIDE = ("saddle", "female_display", "young_crest", "young_horns", "young_frill", "young_horn_l", "young_horn_r")


def load_game(sp):
    spec = geo.load_geo(os.path.join(ASSETS, "geo", "entity", f"{sp}.geo.json"))
    k = game_scale(sp) / PX * 16.0      # px do modelo -> px do jogo, depois metros = /PX
    hid = set(n for n in HIDE)
    for b in spec["bones"]:
        if b["parent"] in hid:
            hid.add(b["name"])
    for b in spec["bones"]:
        b["origin"] = [v * k for v in b["origin"]]
    for c in spec["cubes"]:
        c["from"] = [v * k for v in c["from"]]
        c["to"] = [v * k for v in c["to"]]
        c["origin"] = [v * k for v in c["origin"]]
        c["inflate"] = (c.get("inflate") or 0) * k
    spec["cubes"] = [c for c in spec["cubes"] if c["bone"] not in hid]
    # chão: o pé mais baixo em y=0
    ys = [p[1] for _c, q in geo.cube_points(spec) for p in q]
    dy = -min(ys)
    for b in spec["bones"]:
        b["origin"][1] += dy
    for c in spec["cubes"]:
        c["from"][1] += dy; c["to"][1] += dy; c["origin"][1] += dy
    return spec


# ------------------------------------------------------------ desenho
SIDE = (90, 0)        # de lado, cabeça à esquerda
TQ = (50, 14)         # 3/4 de frente, cabeça à esquerda


def cam(yaw, pitch):
    yr, pr = math.radians(yaw), math.radians(pitch)
    fwd = -np.array([-math.sin(yr) * math.cos(pr), math.sin(pr), -math.cos(yr) * math.cos(pr)])
    right = np.cross(fwd, [0, 1.0, 0]); right /= np.linalg.norm(right); up = np.cross(right, fwd)
    return right, up


def polys(spec, view):
    right, up = cam(*view)
    out = []
    for _c, _f, cs, _uv in geo.faces(spec):
        q = [cs[k] for k in ((0, 0), (1, 0), (1, 1), (0, 1))]
        out.append([(float(p @ right) / PX, float(-(p @ up)) / PX) for p in q])   # metros na tela, y para baixo
    return out


def extent(spec, view):
    P = np.array([pt for pl in polys(spec, view) for pt in pl])
    return P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max()


def draw(img, spec, view, ppm, at, colour=(0, 0, 0)):
    """desenha a silhueta com o ponto (min x, max y = o chão) do bicho em `at` (px da imagem)"""
    x0, x1, y0, y1 = extent(spec, view)
    d = ImageDraw.Draw(img)
    for pl in polys(spec, view):
        d.polygon([(at[0] + (x - x0) * ppm, at[1] - (y1 - y) * ppm) for x, y in pl], fill=colour)
    return (x1 - x0) * ppm, (y1 - y0) * ppm


def mask(spec, view, ppm=40):
    x0, x1, y0, y1 = extent(spec, view)
    W, H = int((x1 - x0) * ppm) + 4, int((y1 - y0) * ppm) + 4
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    for pl in polys(spec, view):
        d.polygon([(2 + (x - x0) * ppm, 2 + (y - y0) * ppm) for x, y in pl], fill=255)
    return np.asarray(im) > 0


# ------------------------------------------------------------ semelhança
N = 160


def norm(mk):
    """recorta, encaixa num quadro N x N mantendo a proporção, apoiado no chão e centrado"""
    ys, xs = np.nonzero(mk)
    mk = mk[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = mk.shape
    k = (N - 8) / max(h, w)
    im = Image.fromarray(mk.astype(np.uint8) * 255).resize((max(1, round(w * k)), max(1, round(h * k))), Image.BILINEAR)
    a = np.asarray(im) > 127
    out = np.zeros((N, N), bool)
    oy = N - 4 - a.shape[0]; ox = (N - a.shape[1]) // 2
    out[oy:oy + a.shape[0], ox:ox + a.shape[1]] = a
    return out


def dice(a, b, shift=8):
    best = 0.0
    for dy in range(-shift, shift + 1, 2):
        for dx in range(-shift, shift + 1, 2):
            bb = np.roll(np.roll(b, dy, 0), dx, 1)
            best = max(best, 2.0 * (a & bb).sum() / max(1, a.sum() + bb.sum()))
    return best


def signature(spec):
    return {v: norm(mask(spec, view)) for v, view in (("side", SIDE), ("tq", TQ))}


def similarity(sa, sb):
    """média do Dice de lado e de 3/4 (1 = a mesma silhueta)"""
    return 0.5 * (dice(sa["side"], sb["side"]) + dice(sa["tq"], sb["tq"]))


# ------------------------------------------------------------ texto
def font(size, bold=False):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()
