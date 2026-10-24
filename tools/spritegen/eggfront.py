"""
Terrassic spawn eggs v3: 32x32, front view, always egg-shaped (Cobblemon / vanilla-egg style).
Each species paints letters on an egg canvas with shape commands; render() adds soft lighting,
a light texture and a dark outline taken from the neighbouring colour.
"""
import colorsys
import math
import random
from PIL import Image, ImageDraw

N = 32
CX, CY, RX, RY = 15.5, 17.0, 12.0, 13.6


def in_egg(x, y):
    t = (y - CY) / RY
    return abs(t) < 1 and abs(x - CX) <= RX * math.sqrt(1 - t * t) * (1 + 0.10 * t)


def rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def mix(a, b, t):
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


def mul(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)


def saturate(c, k):
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
    r, g, b = colorsys.hls_to_rgb(h, l, min(1.0, s * k))
    return (int(r * 255), int(g * 255), int(b * 255))


WARM, COOL, INK = rgb("#fff1c8"), rgb("#241c44"), rgb("#16111c")


def ramp(c):
    c = saturate(c, 1.2)
    return [mix(mul(c, 0.70), COOL, 0.18), c, mix(mul(c, 1.12), WARM, 0.10), mix(mul(c, 1.28), WARM, 0.28)]


LIGHT = (-0.45, -0.60, 0.66)
_l = math.sqrt(sum(v * v for v in LIGHT))
LIGHT = tuple(v / _l for v in LIGHT)


class Egg:
    def __init__(self, name, pal):
        self.name = name
        self.pal = dict(pal)
        self.codes = {"_": 0}
        self.idx = Image.new("L", (N, N), 0)
        self.d = ImageDraw.Draw(self.idx)
        for y in range(N):
            for x in range(N):
                if in_egg(x, y):
                    self.idx.putpixel((x, y), self.code("b"))

    def code(self, ch):
        if ch not in self.codes:
            self.codes[ch] = len(self.codes)
        return self.codes[ch]

    def get(self, x, y):
        if 0 <= x < N and 0 <= y < N:
            v = self.idx.getpixel((x, y))
            for k, c in self.codes.items():
                if c == v:
                    return None if k == "_" else k
        return None

    def set(self, x, y, ch):
        if 0 <= x < N and 0 <= y < N:
            self.idx.putpixel((x, y), self.code(ch))

    # shape commands; clip=True keeps the shape inside the egg
    def _shape(self, draw, ch, clip):
        tmp = Image.new("L", (N, N), 0)
        draw(ImageDraw.Draw(tmp))
        for y in range(N):
            for x in range(N):
                if tmp.getpixel((x, y)) and (not clip or in_egg(x, y)):
                    self.set(x, y, ch)

    def poly(self, pts, ch, clip=False):
        self._shape(lambda d: d.polygon(pts, fill=1), ch, clip)

    def ell(self, box, ch, clip=False):
        self._shape(lambda d: d.ellipse(box, fill=1), ch, clip)

    def rect(self, box, ch, clip=False):
        self._shape(lambda d: d.rectangle(box, fill=1), ch, clip)

    def line(self, pts, ch, w=1, clip=False):
        self._shape(lambda d: d.line(pts, fill=1, width=w), ch, clip)

    def px(self, pts, ch):
        for (x, y) in pts:
            self.set(x, y, ch)

    def mirror(self, pts):
        """points plus their mirror image around the egg's vertical axis"""
        return list(pts) + [(N - 1 - x, y) for (x, y) in pts]

    def render(self):
        rnd = random.Random(self.name)
        cells = [[self.get(x, y) for x in range(N)] for y in range(N)]
        occ = lambda x, y: 0 <= x < N and 0 <= y < N and cells[y][x] is not None
        px = [[None] * N for _ in range(N)]
        for y in range(N):
            for x in range(N):
                ch = cells[y][x]
                if ch is None:
                    continue
                base = rgb(self.pal[ch])
                if ch.isupper():
                    px[y][x] = base
                    continue
                r = ramp(base)
                if in_egg(x, y):
                    nx, ny = (x - CX) / (RX + 0.6), (y - CY) / (RY + 0.6)
                    nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
                    i = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
                    tone = 0 if i < 0.18 else (1 if i < 0.72 else 2)
                    if math.hypot(x - (CX - RX * 0.42), y - (CY - RY * 0.55)) < 1.5:
                        tone = 3
                else:
                    tone = 0 if not occ(x, y + 1) else (2 if not occ(x, y - 1) else 1)
                c = r[tone]
                c = mul(c, 1.0 + (rnd.random() - 0.5) * 0.04)
                px[y][x] = c
        out = [row[:] for row in px]
        for y in range(N):
            for x in range(N):
                if px[y][x] is not None:
                    continue
                nb = [px[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                      if 0 <= x + dx < N and 0 <= y + dy < N and px[y + dy][x + dx] is not None]
                if nb:
                    avg = tuple(sum(c[i] for c in nb) // len(nb) for i in range(3))
                    out[y][x] = mix(mul(avg, 0.40), INK, 0.35)
        img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
        for y in range(N):
            for x in range(N):
                if out[y][x] is not None:
                    img.putpixel((x, y), out[y][x] + (255,))
        return img
