"""The Terrassic title face ("Degraus"): stepped capitals of worn stone, in four finishes.

Each letter gets its own height and sits on its own step, like stones stacked unevenly; the stems stretch and the
bars and serifs keep their size. The stone is worn: corners broken off, bites out of the edges, hairline cracks and
pits. Four finishes, from the mod's palette: basalto (dark, amber top edge), ambar, osso and pedra.
Glyphs in tools/fontgen/degraus.py. The same drawing as the Terrassic site (scripts/letreiro.py there).

usage:  python3 -B letreiro.py   -> art/identidade/marca/letreiro/ (TERRASSIC in the four finishes, 1x and 2x,
                                    alphabet and sample words of each)
in code: letreiro.image("TERRASSIC", "pedra", s=10) -> PIL RGBA image
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'fontgen'))
from degraus import CEDILLA, COMPOSED, GLYPHS, MARKS, SPACE  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/identidade/marca/letreiro'
P = dict(B950=(14, 11, 14), B800=(28, 24, 30), B700=(42, 35, 41), B600=(58, 48, 54), B500=(82, 69, 80), S400=(138, 124, 106),
         S300=(179, 164, 140), S200=(216, 204, 178), BONE=(239, 230, 210), A700=(185, 119, 28), A600=(217, 149, 44),
         A500=(242, 181, 68), A300=(255, 210, 122))
FILLS = {  # tones top to bottom of each letter, share of sub-pixels that take the next tone, colour of the lit top edge
    'basalto': ([P['B500'], P['B600'], P['B700'], P['B800']], .12, P['A500']),
    'ambar': ([P['A300'], P['A500'], P['A600'], P['A700']], 0, None),
    'osso': ([P['BONE'], P['BONE'], P['S200'], P['S300']], 0, None),
    'pedra': ([P['BONE'], P['S200'], P['S300'], P['S400']], .22, None),
}
# The approved TERRASSIC: heights (rows) and steps (rows lifted off the baseline) per letter.
TERRASSIC = dict(heights=[14, 11, 12, 11, 13, 11, 12, 14, 11], lifts=[1, 0, 2, 1, 0, 2, 0, 1, 3])


def stretch(rows, extra):
    """Taller letter: repeat rows that only carry stems (no wide bar), low in the letter, so bars and serifs keep their size."""
    rows = list(rows)
    w = len(rows[0])
    for _ in range(extra):
        n = len(rows)
        thin = [i for i in range(2, n - 2) if rows[i].count('#') <= w * .62 and (rows[i] == rows[i - 1] or rows[i] == rows[i + 1])]
        cands = thin or [i for i in range(2, n - 2) if rows[i].count('#') <= w * .62] or [n // 2]
        i = min(cands, key=lambda k: abs(k - n * .62))
        rows.insert(i, rows[i])
    return rows


def glyph(ch, extra):
    """Rows of one character, the index of its baseline row, and its width."""
    base, mark = COMPOSED.get(ch, (ch, None))
    rows = GLYPHS[base]
    body, tail = rows[:11], rows[11:]
    body = stretch(body, extra)
    w = len(body[0])
    rows = body + tail
    baseline = len(body) - 1
    if mark == 'cedilla':
        rows = rows + [r.center(w, '.')[:w] for r in CEDILLA]
    elif mark:
        m = [r.center(w, '.')[:w] for r in MARKS[mark]]
        rows = m + ['.' * w] + rows
        baseline += len(m) + 1
    return rows, baseline, w


def steps(text, seed):
    """Heights and steps for any text; TERRASSIC keeps the approved ones."""
    if text == 'TERRASSIC':
        return TERRASSIC['heights'], TERRASSIC['lifts']
    rnd = random.Random(seed + sum(map(ord, text)))
    return [11 + rnd.choice((0, 1, 1, 2, 3)) for _ in text], [rnd.choice((0, 0, 1, 2, 3)) for _ in text]


def layout(text, seed=1, gap=1):
    heights, lifts = steps(text, seed)
    parts, x = [], 0
    for ch, hgt, lift in zip(text, heights, lifts):
        if ch == ' ':
            x += SPACE
            continue
        rows, baseline, w = glyph(ch, hgt - 11 if ch.isalpha() else 0)
        parts.append((x, rows, baseline, lift if ch.isalpha() else 0))
        x += w + gap
    W = x - gap
    above = max(b + l for _, _, b, l in parts) + 1
    below = max(len(r) - 1 - b for _, r, b, _ in parts)
    H = above + below
    mask = [[0] * W for _ in range(H)]
    owner = [[-1] * W for _ in range(H)]
    for i, (x0, rows, baseline, lift) in enumerate(parts):
        y0 = above - 1 - lift - baseline
        for gy, row in enumerate(rows):
            for gx, c in enumerate(row):
                if c == '#':
                    mask[y0 + gy][x0 + gx] = 1
                    owner[y0 + gy][x0 + gx] = i
    return mask, owner, W, H


def render(text, fill, s=6, age=1.0, seed=11, pad=3):
    rnd = random.Random(seed)
    mask, owner, w, h = layout(text, seed)
    span = {}
    for y in range(h):
        for x in range(w):
            o = owner[y][x]
            if o >= 0:
                a, b = span.get(o, (y, y))
                span[o] = (min(a, y), max(b, y))
    # Worn stone, block level: outer corners break off, a few edge blocks are missing.
    if age:
        for y in range(h):
            for x in range(w):
                if mask[y][x]:
                    open_sides = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if not (0 <= x + dx < w and 0 <= y + dy < h and mask[y + dy][x + dx]))
                    if open_sides >= 2 and rnd.random() < age * .3 or open_sides == 1 and rnd.random() < age * .035:
                        mask[y][x] = 0
    m = lambda x, y: 0 <= x < w and 0 <= y < h and mask[y][x]
    W, H = (w + pad * 2) * s, (h + pad * 2) * s
    img = [[(0, 0, 0, 0)] * W for _ in range(H)]
    ramp, noise, rim = FILLS[fill]
    for y in range(h):
        for x in range(w):
            if not m(x, y):
                continue
            a, b = span.get(owner[y][x], (0, h - 1))
            for sy in range(s):
                for sx in range(s):
                    lt = min(.999, max(0.0, (y + sy / s - a) / max(1, b - a + 1)))
                    c = ramp[min(len(ramp) - 1, int(lt * len(ramp) + (1 if rnd.random() < noise else 0)))]
                    if sy == 0 and not m(x, y - 1):
                        c = rim or tuple(min(255, v + 26) for v in ramp[0])
                    elif sx == 0 and not m(x - 1, y):
                        c = tuple(min(255, v + 14) for v in c)
                    if sy == s - 1 and not m(x, y + 1) or sx == s - 1 and not m(x + 1, y):
                        c = tuple(max(0, v - 34) for v in c)
                    img[(y + pad) * s + sy][(x + pad) * s + sx] = c + (255,)
    if age:
        ink = lambda X, Y: 0 <= X < W and 0 <= Y < H and img[Y][X][3] > 0
        edge = [(X, Y) for Y in range(H) for X in range(W) if ink(X, Y) and not all(ink(X + dx, Y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        k = s / 6
        # Bites out of the edges, at sub-pixel scale.
        for (X, Y) in rnd.sample(edge, int(len(edge) * age * .09)):
            for dy in range(max(1, round(rnd.choice((1, 2)) * k))):
                for dx in range(max(1, round(rnd.choice((1, 2, 2)) * k))):
                    if 0 <= X + dx < W and 0 <= Y + dy < H:
                        img[Y + dy][X + dx] = (0, 0, 0, 0)
        # Hairline cracks running in from the edges: a dark line with a lit lip above it.
        for (X, Y) in rnd.sample(edge, max(1, int(age * 22 * w / 90))):
            dx, dy = rnd.choice(((1, 1), (1, 0), (0, 1), (-1, 1), (1, -1)))
            for _ in range(rnd.randrange(4, int((6 + age * 10) * k) + 5)):
                if not ink(X, Y):
                    break
                img[Y][X] = tuple(max(0, v - 70) for v in img[Y][X][:3]) + (255,)
                if ink(X, Y - 1):
                    img[Y - 1][X] = tuple(min(255, v + 18) for v in img[Y - 1][X][:3]) + (255,)
                X += dx if rnd.random() < .8 else 0
                Y += dy if rnd.random() < .8 else rnd.choice((-1, 1))
        inside = [(X, Y) for Y in range(H) for X in range(W) if ink(X, Y)]
        for (X, Y) in rnd.sample(inside, int(len(inside) * age * .012)):
            img[Y][X] = tuple(max(0, v - 55) for v in img[Y][X][:3]) + (255,)
    # Outline and a deep extrusion down and to the right, in basalt.
    filled = [[img[y][x][3] > 0 for x in range(W)] for y in range(H)]
    out = [[(0, 0, 0, 0)] * W for _ in range(H)]
    depth = s // 2 + 2
    for y in range(H):
        for x in range(W):
            if filled[y][x]:
                for d in range(1, depth + 1):
                    yy, xx = y + d, x + d // 2
                    if yy < H and xx < W and not filled[yy][xx]:
                        out[yy][xx] = (P['B700'] if d < depth else P['B950']) + (255,)
    for y in range(H):
        for x in range(W):
            if filled[y][x]:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < H and 0 <= xx < W and not filled[yy][xx] and out[yy][xx][3] == 0:
                            out[yy][xx] = P['B950'] + (255,)
                out[y][x] = img[y][x]
    return out, W, H


def stack(lines, gap=0):
    W = max(w for _, w, _ in lines)
    rows = []
    for img, w, h in lines:
        rows += [r + [(0, 0, 0, 0)] * (W - w) for r in img] + [[(0, 0, 0, 0)] * W for _ in range(gap)]
    return rows, W, len(rows)


SPECIMEN = ['ABCDEFGHIJKLM', 'NOPQRSTUVWXYZ', '0123456789', "ÁÂÃÉÊÍÓÕÚÇÑ .,:!?-'"]
WORDS = ['ECOS DO FIM', 'O SALTO', 'CRETÁCEO SUPERIOR']


def to_image(rows, W, H):
    img = Image.new('RGBA', (W, H))
    img.putdata([c for r in rows for c in r])
    return img


def image(text, fill='pedra', s=6, age=1.0, seed=11, pad=3):
    """The text in Degraus as a PIL RGBA image (transparent background)."""
    return to_image(*render(text, fill, s, age, seed, pad))


def main():
    ART.mkdir(parents=True, exist_ok=True)
    for fill in FILLS:
        for s, suffix in ((6, ''), (12, '_2x')):
            image('TERRASSIC', fill, s=s).save(ART / f'terrassic_{fill}{suffix}.png')
        to_image(*stack([render(line, fill, s=4) for line in SPECIMEN], gap=6)).save(ART / f'alfabeto_{fill}.png')
        to_image(*stack([render(word, fill, s=4) for word in WORDS], gap=6)).save(ART / f'palavras_{fill}.png')
        print(fill)


if __name__ == '__main__':
    main()
