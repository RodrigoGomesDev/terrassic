"""
Pixel-art kit for the 16x16 block textures (engine v2).

The vanilla textures look polished because they are drawn with a few deliberate tones, not with smooth gradients:
3 to 6 tones per material, pixels grouped in small clusters (dashes, flecks, lumps) instead of single-pixel
speckle, a one-pixel lit edge on top/left of every raised shape and a one-pixel shadow under/right of it, and the
darkest tone saved for joints and holes.  This kit works the same way: textures are painted as grids of TONE
INDICES (0 = darkest of the ramp) and turned into colours only at the end, so every texture keeps a short palette.

    g = clusters("seed", [0.1, 0.25, 0.4, 0.2, 0.05], periods=(4, 8), stretch=(0.5, 1.5))  # tone indices
    g = despeckle(g)                     # no lonely pixels
    relief(g, owner, joint=-1)           # bevel every region: lit top/left, shaded bottom/right, joints
    cv = colour(g, ramp_hex, extra={-1: "#2a241c"})

Everything wraps around (tileable on the 16x16 torus).
"""
import math
import random

from sprites import Canvas, hexc

N = 16
CLEAR = None  # transparent pixel in a tone grid


class Noise:
    """Tileable value noise on the 16x16 torus; stretch > 1 on an axis gives more cells along it."""

    def __init__(self, seed, periods=(2, 4, 8), weights=(0.5, 0.3, 0.2), stretch=(1.0, 1.0)):
        rnd = random.Random(seed)
        self.layers = []
        for p, w in zip(periods, weights):
            px = max(1, round(p * stretch[0]))
            py = max(1, round(p * stretch[1]))
            grid = [[rnd.random() for _ in range(px)] for _ in range(py)]
            self.layers.append((px, py, grid, w))

    def __call__(self, x, y):
        total = 0.0
        for px, py, grid, w in self.layers:
            fx, fy = x / N * px, y / N * py
            x0, y0 = int(math.floor(fx)), int(math.floor(fy))
            tx, ty = fx - x0, fy - y0
            tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
            a = grid[y0 % py][x0 % px]; b = grid[y0 % py][(x0 + 1) % px]
            c = grid[(y0 + 1) % py][x0 % px]; d = grid[(y0 + 1) % py][(x0 + 1) % px]
            total += w * ((a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty)
        return total


def grid(fill=0):
    return [[fill] * N for _ in range(N)]


def at(g, x, y):
    return g[y % N][x % N]


def put(g, x, y, v):
    g[y % N][x % N] = v


def field(fn):
    return [[fn(x, y) for x in range(N)] for y in range(N)]


def levels(f, shares, mask=None):
    """Quantise a float field into tone indices by RANK: shares[i] is the fraction of pixels that get tone i
    (dark -> light).  Ranking instead of fixed thresholds keeps the balance of tones the same for every seed."""
    cells = [(f[y][x], x, y) for y in range(N) for x in range(N) if mask is None or mask[y][x]]
    cells.sort()
    total = sum(shares)
    out = grid(CLEAR if mask is not None else 0)
    i, acc = 0, 0.0
    bounds = []
    for s in shares:
        acc += s / total
        bounds.append(acc)
    for k, (_, x, y) in enumerate(cells):
        while i < len(bounds) - 1 and (k + 0.5) / len(cells) > bounds[i]:
            i += 1
        out[y][x] = i
    return out


def clusters(seed, shares, periods=(4, 8, 16), weights=(0.45, 0.35, 0.2), stretch=(1.0, 1.0), mask=None):
    """Tone indices in small clusters: smooth noise ranked into len(shares) tones."""
    n = Noise(seed, periods, weights, stretch)
    return levels(field(n), shares, mask)


def despeckle(g, passes=1, protect=()):
    """Lonely pixels (no 4-neighbour of the same tone) take the most common tone around them, so the texture is
    made of clusters.  Tones in `protect` (sparkles, pores) are left alone."""
    for _ in range(passes):
        out = [row[:] for row in g]
        for y in range(N):
            for x in range(N):
                v = g[y][x]
                if v is CLEAR or v in protect:
                    continue
                nb = [at(g, x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                if v in nb:
                    continue
                nb = [c for c in nb if c is not CLEAR]
                if nb:
                    out[y][x] = max(set(nb), key=lambda c: (nb.count(c), -abs(c - v)))
        g = out
    return g


def shift(g, x, y, k, lo=0, hi=None):
    v = at(g, x, y)
    if v is CLEAR or v < 0:
        return
    v += k
    v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    put(g, x, y, v)


def relief(g, owner, hi, joint=None, light=1, dark=-1, left=True, right=True, corner=True):
    """Bevel every region of `owner` (region index per pixel, -1 = joint): the top row and left column of a
    region are lifted `light` tones, the bottom row and right column dropped `dark` tones (vanilla stone bricks,
    cobblestone).  Joint pixels get the `joint` tone when given."""
    out = [row[:] for row in g]
    for y in range(N):
        for x in range(N):
            o = at(owner, x, y)
            if o < 0:
                if joint is not None:
                    out[y][x] = joint
                continue
            up, lf = at(owner, x, y - 1) != o, at(owner, x - 1, y) != o
            dn, rt = at(owner, x, y + 1) != o, at(owner, x + 1, y) != o
            v = g[y][x]
            if v is CLEAR or v < 0:
                continue
            if dn or (right and rt):
                v += dark
            elif up or (left and lf):
                v += light
            out[y][x] = max(0, min(hi, v))
    if corner:  # the outer corners of each stone are rounded off into the joint
        for y in range(N):
            for x in range(N):
                o = at(owner, x, y)
                if o < 0:
                    continue
                if at(owner, x, y + 1) != o and at(owner, x + 1, y) != o and joint is not None:
                    out[y][x] = max(0, out[y][x] - 1)
    return out


def regions_from_cells(seed, count, gap=0.9, sx=1.0, sy=1.0):
    """Tileable Voronoi stones: owner[y][x] = stone index, -1 where the distance to the border is < gap."""
    rnd = random.Random(seed)
    spacing = 0.75 * N / math.sqrt(count)  # seeds kept apart, so no stone is a sliver
    seeds = []
    for _ in range(400):
        if len(seeds) == count:
            break
        p = (rnd.uniform(0, N), rnd.uniform(0, N))
        if all(math.hypot(min(abs(p[0] - q[0]), N - abs(p[0] - q[0])) * sx,
                          min(abs(p[1] - q[1]), N - abs(p[1] - q[1])) * sy) >= spacing for q in seeds):
            seeds.append(p)

    def dist(x, y, s):
        dx = abs(x - s[0]); dy = abs(y - s[1])
        return math.hypot(min(dx, N - dx) * sx, min(dy, N - dy) * sy)
    owner = grid(-1)
    for y in range(N):
        for x in range(N):
            ds = sorted((dist(x + 0.5, y + 0.5, s), i) for i, s in enumerate(seeds))
            owner[y][x] = ds[0][1] if ds[1][0] - ds[0][0] >= gap else -1
    return owner


def courses(seed, heights=None, lengths=(4, 9), round_corners=0.7, min_last=4):
    """Stones laid in horizontal courses with staggered joints; owner = stone index or -1 (joint)."""
    rnd = random.Random(seed)
    heights = heights or rnd.choice(([4, 3, 5, 4], [5, 3, 4, 4], [3, 4, 4, 5], [4, 4, 3, 5]))
    owner = grid(-1)
    stone, y0 = 0, 0
    for h in heights:
        x, total = rnd.randrange(N), 0
        while total < N:
            w = rnd.randint(*lengths)
            if N - total - w < min_last:
                w = N - total
            sx = x + total
            for yy in range(y0, y0 + h - 1):
                for xx in range(sx, sx + w - 1):
                    owner[yy % N][xx % N] = stone
            for (cx, cy) in ((sx, y0), (sx + w - 2, y0), (sx, y0 + h - 2), (sx + w - 2, y0 + h - 2)):
                if rnd.random() < round_corners:
                    owner[cy % N][cx % N] = -1
            stone += 1
            total += w
        y0 += h
    return owner, stone


def per_region(g, owner, count, seed, spread=(-1, 0, 0, 1), hi=None):
    """Each stone gets its own tone offset (some stones darker, some lighter)."""
    rnd = random.Random(seed)
    off = [rnd.choice(spread) for _ in range(count)]
    out = [row[:] for row in g]
    for y in range(N):
        for x in range(N):
            o = owner[y][x]
            if o >= 0 and out[y][x] is not CLEAR:
                v = out[y][x] + off[o]
                out[y][x] = max(0, v if hi is None else min(hi, v))
    return out


def colour(g, ramp, extra=None):
    """Tone grid -> Canvas.  Index i is ramp[i]; keys of `extra` (negative or any value) map to their own
    colours; CLEAR stays transparent."""
    cols = [hexc(c) if isinstance(c, str) else c for c in ramp]
    ext = {k: (hexc(v) if isinstance(v, str) else v) for k, v in (extra or {}).items()}
    cv = Canvas()
    for y in range(N):
        for x in range(N):
            v = g[y][x]
            if v is CLEAR:
                continue
            if v in ext:
                cv.set(x, y, ext[v])
            else:
                cv.set(x, y, cols[max(0, min(len(cols) - 1, v))])
    return cv


def to_grid(cv, ramp):
    """Canvas -> tone grid, each pixel snapped to the nearest ramp colour (used to retrofit old drawings)."""
    cols = [hexc(c) for c in ramp]
    g = grid(CLEAR)
    for y in range(N):
        for x in range(N):
            c = cv.get(x, y)
            if c is None or c[3] == 0:
                continue
            g[y][x] = min(range(len(cols)), key=lambda i: sum((c[k] - cols[i][k]) ** 2 for k in range(3)))
    return g


def snap(cv, ramp, keep_alpha=True):
    """Snap every opaque pixel of a canvas to the nearest colour of `ramp` (a list of hex colours)."""
    cols = [hexc(c) for c in ramp]
    out = Canvas()
    for y in range(N):
        for x in range(N):
            c = cv.get(x, y)
            if c is None or c[3] == 0:
                continue
            best = min(cols, key=lambda k: (0.3 * (c[0] - k[0]) ** 2 + 0.59 * (c[1] - k[1]) ** 2 +
                                            0.11 * (c[2] - k[2]) ** 2))
            out.set(x, y, (best[0], best[1], best[2], c[3] if keep_alpha else 255))
    return out


def dashes(g, seed, count, tone, length=(2, 4), horizontal=True, mask=None):
    """Short strokes of one tone (bedding lines, grain, fibres)."""
    rnd = random.Random(seed)
    for _ in range(count):
        x, y = rnd.randrange(N), rnd.randrange(N)
        for i in range(rnd.randint(*length)):
            px, py = (x + i, y) if horizontal else (x, y + i)
            if mask is None or at(mask, px, py):
                if at(g, px, py) is not CLEAR:
                    put(g, px, py, tone)
    return g


def fleck(g, x, y, shape, tone_map):
    """Stamp a small pattern: shape is a list of strings, each char a key of tone_map ('.' = untouched)."""
    for j, row in enumerate(shape):
        for i, ch in enumerate(row):
            if ch != "." and ch in tone_map:
                put(g, x + i, y + j, tone_map[ch])
    return g


def posterize(cv, k=5, protect_share=0.05, passes=1):
    """Turn a smoothly shaded drawing into k flat tones (k-means on its own colours), then clear out lonely
    pixels; tones used by fewer than protect_share of the pixels (embers, glints, pores) are kept as they are.
    Used for drawings whose shapes are right but whose gradients look blurry next to the vanilla blocks."""
    pts = [(x, y, cv.get(x, y)) for y in range(N) for x in range(N)
           if cv.get(x, y) is not None and cv.get(x, y)[3] > 0]
    if not pts:
        return cv
    lum = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]  # noqa: E731
    cols = sorted((p[2] for p in pts), key=lum)
    cent = [cols[int((i + 0.5) * len(cols) / k)][:3] for i in range(k)]
    for _ in range(8):
        groups = [[] for _ in cent]
        for _, _, c in pts:
            i = min(range(len(cent)), key=lambda j: sum((c[t] - cent[j][t]) ** 2 for t in range(3)))
            groups[i].append(c)
        cent = [tuple(sum(c[t] for c in gr) // len(gr) for t in range(3)) if gr else cent[i]
                for i, gr in enumerate(groups)]
    order = sorted(range(len(cent)), key=lambda i: lum(cent[i]))
    cent = [cent[i] for i in order]
    g = grid(CLEAR)
    alpha = {}
    for x, y, c in pts:
        g[y][x] = min(range(len(cent)), key=lambda j: sum((c[t] - cent[j][t]) ** 2 for t in range(3)))
        alpha[(x, y)] = c[3]
    counts = [sum(1 for row in g for v in row if v == i) for i in range(len(cent))]
    rare = tuple(i for i, n_ in enumerate(counts) if n_ < protect_share * len(pts))
    g = despeckle(g, passes=passes, protect=rare)
    out = Canvas()
    for y in range(N):
        for x in range(N):
            if g[y][x] is not CLEAR:
                c = cent[g[y][x]]
                out.set(x, y, (c[0], c[1], c[2], alpha[(x, y)]))
    return out


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def tame(cv, cap=68.0, max_transparent=0.4):
    """Pull a finished texture's tones towards its mean brightness until the spread between its darkest and
    lightest 5% (p95 - p5 of luminance) is at most `cap`.  Measured on the vanilla 1.20.1 blocks the median
    spread is 64 and few go past 85; ours ran at 110+, which is what made them look harsh and noisy next to
    vanilla.  Hue and the pattern are kept; sprites that are mostly transparent (torches, plants) are left alone."""
    pts = [cv.get(x, y) for y in range(N) for x in range(N)]
    op = [c for c in pts if c is not None and c[3] > 0]
    if not op or 1 - len(op) / (N * N) > max_transparent:
        return cv
    ls = sorted(lum(c) for c in op)
    spread = ls[min(len(ls) - 1, int(0.95 * len(ls)))] - ls[int(0.05 * len(ls))]
    if spread <= cap:
        return cv
    k = cap / spread
    mean = [sum(c[i] for c in op) / len(op) for i in range(3)]
    out = Canvas()
    for y in range(N):
        for x in range(N):
            c = cv.get(x, y)
            if c is None:
                continue
            out.set(x, y, tuple(int(round(mean[i] + (c[i] - mean[i]) * k)) for i in range(3)) + (c[3],))
    return out


def scatter(seed, count, min_dist=3.0, tries=600):
    """Blue-noise points on the 16x16 torus (Poisson disc): details spread evenly, never clumped or lined up."""
    rnd = random.Random(seed)
    pts = []
    for _ in range(tries):
        if len(pts) >= count:
            break
        p = (rnd.randrange(N), rnd.randrange(N))
        if all(math.hypot(min(abs(p[0] - q[0]), N - abs(p[0] - q[0])),
                          min(abs(p[1] - q[1]), N - abs(p[1] - q[1]))) >= min_dist for q in pts):
            pts.append(p)
    return pts


def calm(seed, base=2, spread=1, share=0.6, periods=(2, 4), weights=(0.6, 0.4), stretch=(1.0, 1.0), mask=None):
    """A calm face like the modern vanilla blocks: one dominant tone (share of the pixels) with a few big soft
    patches one tone lighter and darker, no pixel noise.  Details are added on top with stamps."""
    rest = (1 - share) / 2
    g = clusters(seed, [rest, share, rest], periods=periods, weights=weights, stretch=stretch, mask=mask)
    g = despeckle(despeckle(g))
    return [[CLEAR if v is CLEAR else base + (v - 1) * spread for v in row] for row in g]


def bevel(g, owner, hi, joint=None, light=1, dark=1, corner=True):
    """Two-level chamfer of every region (modern stone bricks): top row and left column lit, bottom row and right
    column shaded, the top-left corner pixel lit once more and the bottom-right one shaded once more."""
    out = [row[:] for row in g]
    for y in range(N):
        for x in range(N):
            o = at(owner, x, y)
            if o < 0:
                if joint is not None:
                    out[y][x] = joint
                continue
            v = g[y][x]
            if v is CLEAR:
                continue
            up, lf = at(owner, x, y - 1) != o, at(owner, x - 1, y) != o
            dn, rt = at(owner, x, y + 1) != o, at(owner, x + 1, y) != o
            if dn or rt:
                v -= dark + (1 if corner and dn and rt else 0)
            elif up or lf:
                v += light + (1 if corner and up and lf else 0)
            out[y][x] = max(0, min(hi, v))
    return out
