"""The loud roar's burst in the air (particle terrassic:roar_wave, client/RoarWaveParticle): 8 frames of a hollow ring of
comic speed lines and little bolts racing outward and thinning out. 128 x 128 each, 1 texel = 1 Minecraft pixel, so
the burst is 8 blocks across."""
import math, random
from PIL import Image, ImageDraw

INK = (40, 38, 36, 230); LINE = (244, 240, 230, 220); BOLT = (40, 38, 36, 240)
N = 8; SZ = 128          # 1 texel = 1 Minecraft pixel: the burst is 8 blocks across

def bolt(d, x, y, ang, L):
    """small zigzag bolt pointing outward, 2 px wide, comic style"""
    ux, uy = math.cos(ang), math.sin(ang); px, py = -uy, ux
    pts = [(x, y), (x + ux * L * 0.45 + px * 2.5, y + uy * L * 0.45 + py * 2.5),
           (x + ux * L * 0.55 - px * 2.0, y + uy * L * 0.55 - py * 2.0), (x + ux * L, y + uy * L)]
    d.line([(round(a), round(b)) for a, b in pts], fill=BOLT, width=2)

def frame(k, seed=7):
    """frame k of N: a hollow ring of speed lines races outward and thins out"""
    rnd = random.Random(seed)
    img = Image.new('RGBA', (SZ, SZ), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    c = SZ / 2 - 0.5; u = k / (N - 1)
    r_in = 16 + 38 * u ** 0.75
    rays = 56
    for i in range(rays):
        a = 2 * math.pi * (i + rnd.random() * 0.7) / rays
        L = (6 + rnd.random() * 16) * (1 - 0.55 * u)
        r0 = r_in + rnd.random() * 6
        if rnd.random() < 0.15 + 0.55 * u: continue
        x0, y0 = c + math.cos(a) * r0, c + math.sin(a) * r0
        x1, y1 = c + math.cos(a) * min(r0 + L, SZ / 2 - 1), c + math.sin(a) * min(r0 + L, SZ / 2 - 1)
        col = LINE if i % 4 == 1 else INK
        d.line([(round(x0), round(y0)), (round(x1), round(y1))], fill=col, width=2 if (i % 5 == 0 and u < 0.5) else 1)
    if u < 0.6:
        for i in range(7):
            a = 2 * math.pi * (i + 0.3 + rnd.random() * 0.4) / 7
            r = r_in + 4 + rnd.random() * 6
            bolt(d, c + math.cos(a) * r, c + math.sin(a) * r, a, 9 * (1 - 0.5 * u))
    return img
