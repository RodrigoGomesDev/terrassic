"""Prévia do formato do continente Terrassic: porta em Python de ContinentDensity.shape() (mesma matemática).
A entrada "vanilla" (continentalidade do Minecraft) é imitada com fBm de ruído de valor na mesma escala.
Uso: python3 tools/worldgen/ilha_preview.py saida.png  (docs/MUNDO.md, seção 10)."""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

def value_noise(n, cells, rng):
    g = rng.uniform(-1, 1, (cells + 2, cells + 2))
    xs = np.linspace(0, cells, n, endpoint=False)
    i = xs.astype(int); f = xs - i; f = f * f * (3 - 2 * f)
    a = g[np.ix_(i, i)]; b = g[np.ix_(i + 1, i)]; c = g[np.ix_(i, i + 1)]; d = g[np.ix_(i + 1, i + 1)]
    fx = f[:, None]; fz = f[None, :]
    return lerp(lerp(a, b, fx), lerp(c, d, fx), fz)

def fake_vanilla(n, span, seed):
    rng = np.random.default_rng(seed)
    v = np.zeros((n, n)); amp = 0.55
    cells = max(2, int(span / 1600))
    for _ in range(5):
        v += amp * value_noise(n, cells, rng); amp *= 0.5; cells *= 2
    return v

def own_noise(X, Z, R, seed, wl):
    """fBm de ruído de valor próprio (no Java: hash da grade com o sal da semente)."""
    n = X.shape[0]
    span = X.max() - X.min()
    rng = np.random.default_rng(seed * 7919 + int(wl * 100))
    v = np.zeros_like(X); amp = 1.0; cells = max(2, int(span / (wl * R)))
    tot = 0
    for _ in range(3):
        v += amp * value_noise(n, cells, rng); tot += amp; amp *= 0.5; cells *= 2
    return v / tot

def shape(x, z, v, R, angle, n1, n2):
    # === igual a ContinentDensity.shape() ===
    ca, sa = math.cos(angle), math.sin(angle)
    u = (x * ca + z * sa) / R          # eixo do golfo (o mar entra por +u)
    w = (-x * sa + z * ca) / R         # eixo comprido do continente
    d = np.hypot(u, w / 1.35)
    e = d + 0.22 * n1 + 0.07 * n2 - 0.06 * v
    land = np.clip(lerp(0.60, -0.06, smooth(0.0, 0.85, e)) + 0.20 * v, -0.10, 1.0)
    ocean = lerp(-0.25, -0.95, smooth(0.95, 1.30, e))
    t = smooth(0.80, 0.97, e)
    c = lerp(land, ocean, t)
    # Mar Interior: golfo largo que entra pela costa até perto do centro (o "C" da Pangeia)
    along = np.clip((u - 0.30) / 1.0, 0.0, 1.0)
    halfw = 0.12 + 0.30 * along + 0.05 * n2
    off = w - 0.18 * np.sin(math.pi * along) * 1.0
    dl = np.where(u < 0.30, np.hypot(u - 0.30, w), np.abs(off))
    g = 1.0 - smooth(halfw * 0.6, halfw, dl)
    c = np.minimum(c, lerp(c, -0.38, g))
    # ilhotas num anel de mar raso em volta do continente
    ring = smooth(1.05, 1.18, e) * (1.0 - smooth(1.50, 1.70, e))
    islet = smooth(0.50, 0.64, n2) * ring
    c = lerp(c, np.maximum(c, -0.02), islet)
    return c

BANDS = [(-0.455, (18, 40, 84)), (-0.19, (34, 78, 140)), (-0.11, (222, 206, 150)),
         (0.03, (150, 176, 92)), (0.30, (96, 140, 64)), (9.0, (122, 104, 70))]

def color(c):
    out = np.zeros(c.shape + (3,), np.uint8)
    lo = -9
    for hi, col in BANDS:
        m = (c >= lo) & (c < hi); out[m] = col; lo = hi
    return out

def panel(R, seed, n=420, span_factor=2.2):
    span = R * span_factor
    xs = np.linspace(-span, span, n)
    X, Z = np.meshgrid(xs, xs, indexing="ij")
    v = fake_vanilla(n, 2 * span, seed)
    # direção do golfo: para onde o ruído é mais baixo num círculo de 0,6R (como no Java)
    ang = (seed * 2.399963) % (2 * math.pi)
    n1 = own_noise(X, Z, R, seed, 0.8)
    n2 = own_noise(X, Z, R, seed + 1, 0.22)
    c = shape(X, Z, v, R, ang, n1, n2)
    img = Image.fromarray(color(c).transpose(1, 0, 2))
    d = ImageDraw.Draw(img)
    s = (n - 1) / (2 * span)
    cx = cy = (n - 1) / 2
    b = 2 * R * s  # borda do mundo: quadrado de lado 4R
    d.rectangle([cx - b, cy - b, cx + b, cy + b], outline=(240, 90, 60), width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
    land = (c > -0.19).sum() * (2 * span / n) ** 2 / 1e6
    return img, land

def main(out):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 11)
    cols = [(800, 11), (1200, 11), (1200, 42), (2000, 7)]
    W = 420; pad = 10; top = 34; foot = 60
    sheet = Image.new("RGB", (len(cols) * (W + pad) + pad, top + W + foot), (24, 22, 20))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 8), "Terrassic: continente em C cercado de mar (prévia da função de densidade; laranja = borda do mundo)", fill=(240, 220, 180), font=font)
    for k, (R, seed) in enumerate(cols):
        img, land = panel(R, seed, W)
        x = pad + k * (W + pad)
        sheet.paste(img, (x, top))
        label = f"raio {R} blocos (semente {seed})  ~{land:.1f} km2 de terra"
        d.text((x, top + W + 6), label, fill=(230, 230, 230), font=font)
        d.text((x, top + W + 22), f"borda: {4*R} x {4*R} blocos", fill=(200, 160, 140), font=font)
    lx = pad
    for name, (hi, col) in zip(["oceano fundo", "mar", "costa", "terra baixa", "terra média", "interior alto"], BANDS):
        d.rectangle([lx, top + W + 40, lx + 12, top + W + 52], fill=col)
        d.text((lx + 16, top + W + 40), name, fill=(220, 220, 220), font=font); lx += 120
    sheet.save(out)

if __name__ == "__main__":
    main(sys.argv[1])
