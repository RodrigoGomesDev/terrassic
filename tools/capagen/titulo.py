"""
The TERRASSIC title: heavy serif letters like old adventure-film titles, built from Minecraft-style blocks.
Each letter cell is a little block textured at 5x5 texels; the word gets a chiselled bevel, a deep extrusion and a
dark outline. Three finishes: "pedra" (carved stone), "ambar" (amber) and "fossil" (bone).
"""
import numpy as np
from PIL import Image

from pixel import hexrgb, mix, noise2d

# 11 rows; stems 3 cells wide; wedge serifs
TITLE_GLYPHS = {
    "T": ["###########", "###########", "##..###..##", "....###....", "....###....", "....###....", "....###....",
          "....###....", "....###....", "...#####...", "...#####..."],
    "E": ["#########", "#########", ".###...##", ".###.....", ".######..", ".######..", ".###.....", ".###.....",
          ".###...##", "#########", "#########"],
    "R": ["########..", "#########.", ".###..###.", ".###...###", ".###..###.", ".#######..", ".######...",
          ".###.###..", ".###..###.", "####...###", "####...###"],
    "A": ["....###....", "....###....", "...#####...", "...##.##...", "..###.###..", "..##...##..", ".#########.",
          ".#########.", "###.....###", "###.....###", "###.....###"],
    "S": ["..#######", ".########", "###....##", "###......", ".#######.", "..#######", "......###", "......###",
          "##....###", "########.", "#######.."],
    "I": ["#####", "#####", ".###.", ".###.", ".###.", ".###.", ".###.", ".###.", ".###.", "#####", "#####"],
    "C": ["..#######", ".########", "###....##", "###......", "###......", "###......", "###......", "###......",
          "###....##", ".########", "..#######"],
}

FINISHES = {
    # face gradient top -> bottom, extrusion, outline, highlight
    "pedra": dict(face=[(0.0, "#f1e7cc"), (0.5, "#c4ad86"), (1.0, "#7a6046")], side=("#4a3628", "#24170f"),
                  outline="#100a08", grain=0.10),
    "ambar": dict(face=[(0.0, "#ffe9a3"), (0.45, "#f5ad3e"), (1.0, "#b4501b")], side=("#6b2a10", "#2c1006"),
                  outline="#140804", grain=0.05),
    "fossil": dict(face=[(0.0, "#f6efdc"), (0.6, "#ddd0b0"), (1.0, "#a99470")], side=("#5a4630", "#2a1e14"),
                   outline="#120c08", grain=0.07),
}


def _ramp(stops, t):
    pos = np.array([p for p, _ in stops])
    cols = np.array([hexrgb(c) for _, c in stops])
    return np.stack([np.interp(t, pos, cols[:, k]) for k in range(3)], -1)


def mask(text, gap=1):
    cols, x = [], 0
    rows = len(next(iter(TITLE_GLYPHS.values())))
    widths = [len(TITLE_GLYPHS[c][0]) for c in text]
    W = sum(widths) + gap * (len(text) - 1)
    m = np.zeros((rows, W), bool)
    for ch, w in zip(text, widths):
        for y, row in enumerate(TITLE_GLYPHS[ch]):
            for dx, c in enumerate(row):
                if c == "#":
                    m[y, x + dx] = True
        x += w + gap
    return m


def _grow(m, r=1):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def title(text="TERRASSIC", finish="pedra", texel=2, sub=5, depth=6, seed=4):
    """RGBA title. texel = screen px per texel; sub = texels per letter cell; depth = extrusion in texels."""
    f = FINISHES[finish]
    rng = np.random.default_rng(seed)
    cm = mask(text)
    pad = depth + 4
    face = np.kron(cm, np.ones((sub, sub), bool))
    face = np.pad(face, pad)
    H, W = face.shape
    img = np.zeros((H, W, 3))
    alpha = np.zeros((H, W), bool)

    # extrusion straight down, darkening with depth
    s0, s1 = hexrgb(f["side"][0]), hexrgb(f["side"][1])
    for d in range(depth, 0, -1):
        sh = np.zeros_like(face)
        sh[d:] = face[:-d]
        new = sh & ~alpha
        img[new] = mix(s0, s1, d / depth)
        alpha |= sh
    # little block seams on the extrusion, one per letter cell column
    yy, xx = np.mgrid[0:H, 0:W]
    seam = alpha & ~face & (((xx - pad) % sub) == 0)
    img[seam] *= 0.8

    # face: vertical gradient over the letter height + grain + per-cell block tone
    t = np.clip((yy - pad) / (cm.shape[0] * sub), 0, 1)
    base = _ramp(f["face"], t)
    grain = noise2d(H, W, 1.2, rng, 2)
    cell_tone = rng.uniform(-1, 1, (H // sub + 2, W // sub + 2))[(yy - pad) // sub, (xx - pad) // sub]
    base *= (1 + grain[..., None] * f["grain"] + cell_tone[..., None] * 0.035)
    # chiselled bevel on the letter outline: lit top-left, shaded bottom-right
    up = face & ~np.roll(face, 1, 0)
    left = face & ~np.roll(face, 1, 1)
    down = face & ~np.roll(face, -1, 0)
    right = face & ~np.roll(face, -1, 1)
    base[up | left] = base[up | left] * 1.18 + 12
    base[down | right] = base[down | right] * 0.72
    # faint block seams inside the face (Minecraft blocks), lighter than the bevel
    inner = face & (((xx - pad) % sub == 0) | ((yy - pad) % sub == 0)) & ~(up | left)
    base[inner] *= 0.93

    if finish == "ambar":
        # bubbles and a few dark inclusions trapped in the amber
        bub = (rng.random((H, W)) > 0.985) & face & ~(up | left | down | right)
        base[bub] = mix(base[bub], hexrgb("#fff6d8"), 0.7)
        inc = (rng.random((H, W)) > 0.996) & face
        base[inc] = mix(base[inc], hexrgb("#5a2a0c"), 0.6)
    if finish == "fossil":
        # hairline cracks and pores in old bone
        for _ in range(int(W / 14)):
            x, y = rng.uniform(pad, W - pad), rng.uniform(pad, H - pad)
            for _k in range(int(rng.integers(4, 10))):
                ix, iy = int(x), int(y)
                if face[iy, ix]:
                    base[iy, ix] *= 0.62
                x += rng.choice([-1, 0, 1])
                y += 1
        pore = (rng.random((H, W)) > 0.975) & face
        base[pore] *= 0.8
    if finish == "pedra":
        moss = face & (noise2d(H, W, 6, rng, 2) > 0.45) & (t > 0.55)
        base[moss] = mix(base[moss], hexrgb("#7d8a4a"), 0.35)

    img[face] = base[face]
    alpha |= face
    ring = _grow(alpha) & ~alpha
    img[ring] = hexrgb(f["outline"])
    alpha |= ring
    out = Image.fromarray(np.dstack([np.clip(img, 0, 255), alpha * 255.0]).astype(np.uint8), "RGBA")
    return out.resize((W * texel, H * texel), Image.NEAREST)


SLOGANS = {
    "pt_br": "O PASSADO ACORDOU.",
    "en_us": "THE PAST HAS AWOKEN.",
    "es_es": "EL PASADO DESPERTÓ.",
}


def slogan(text, cell=4, color="#d8ccb2", shadow=(10, 8, 6, 200), spacing=2):
    """Slogan in the 5x7 block font (with accents), widely spaced, with a soft shadow."""
    from font import layout_text
    cells, (cw, ch) = layout_text(text, spacing)
    sh = max(1, cell // 2)
    px = np.zeros((ch * cell + sh, cw * cell + sh, 4), np.uint8)
    fc = tuple(int(v) for v in hexrgb(color)) + (255,)
    for (x, y) in cells:
        px[y * cell + sh:(y + 1) * cell + sh, x * cell + sh:(x + 1) * cell + sh] = shadow
    for (x, y) in cells:
        px[y * cell:(y + 1) * cell, x * cell:(x + 1) * cell] = fc
    return Image.fromarray(px, "RGBA")
