"""
"Caderno": Dr. Katarina Usha's handwriting, for her notebook pages and field notes (8 px cell, like "Sedimento").

Built from "Sedimento" so both read as one family, then made to look written by hand: every square corner is
rounded (a pen does not cut corners like a chisel), the top half leans one pixel to the right (a fast, slanted hand),
and the letters a pen changes most have their own shapes (single-storey a and g, looped e, long-tailed f, open k...).
"""
import sedimento as S

OVERRIDES = {
    "a": ["....", "....", ".###", "#..#", "#..#", "#.##", ".#.#", "...."],
    "e": ["....", "....", ".##.", "#..#", "###.", "#...", ".###", "...."],
    "f": ["..##", ".#..", "###.", ".#..", ".#..", ".#..", ".#..", "#..."],
    "g": ["....", "....", ".###", "#..#", "#..#", ".###", "...#", ".##."],
    "k": ["#...", "#...", "#..#", "#.#.", "###.", "#..#", "#..#", "...."],
    "r": ["....", "....", "#.#.", "##.#", "#...", "#...", "#...", "...."],
    "s": ["....", "....", ".###", "#...", ".##.", "...#", "###.", "...."],
    "t": [".#..", ".#..", "####", ".#..", ".#..", ".#..", "..##", "...."],
    "y": ["....", "....", "#..#", "#..#", "#..#", ".###", "...#", ".##."],
    "d": ["...#", "...#", ".###", "#..#", "#..#", "#..#", ".#.#", "...."],
    "u": ["....", "....", "#..#", "#..#", "#..#", "#..#", ".#.#", "...."],
    "l": ["#.", "#.", "#.", "#.", "#.", "#.", ".#", ".."],
    "i": ["#.", "..", "#.", "#.", "#.", "#.", ".#", ".."],
    "ı": ["..", "..", "#.", "#.", "#.", "#.", ".#", ".."],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
}

SLANT_ROWS = 4   # rows 0..3 lean one pixel to the right


def _round(rows):
    """Cuts every convex square corner of the strokes (keeps 1-pixel stems and dots)."""
    h = len(rows)
    w = max(len(r) for r in rows)
    g = [list(r.ljust(w, ".")) for r in rows]

    def ink(x, y):
        return 0 <= y < h and 0 <= x < w and g[y][x] == "#"
    out = [row[:] for row in g]
    for y in range(h):
        for x in range(w):
            if not ink(x, y):
                continue
            n = ink(x, y - 1); s_ = ink(x, y + 1); e = ink(x + 1, y); wv = ink(x - 1, y)
            # a corner pixel: exactly one horizontal and one vertical neighbour, nothing on the other two sides,
            # and the inner diagonal empty (so it is the corner of a frame, not part of a thick block)
            for (hx, vy) in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                has_h = ink(x + hx, y)
                has_v = ink(x, y + vy)
                other_h = ink(x - hx, y)
                other_v = ink(x, y - vy)
                if has_h and has_v and not other_h and not other_v and not ink(x + hx, y + vy):
                    out[y][x] = "."
    return ["".join(r) for r in out]


def _slant(rows):
    w = max(len(r) for r in rows) + 1
    out = []
    for y, r in enumerate(rows):
        r = r.ljust(w - 1, ".")
        out.append(("." + r) if y < SLANT_ROWS else (r + "."))
    # drop empty columns on the left (keeps glyphs flush left like the rest of the family)
    while all(row[0] == "." for row in out) and len(out[0]) > 1:
        out = [row[1:] for row in out]
    return out


def glyphs():
    base = {}
    base.update(S.UPPER)
    base.update(S.LOWER)
    base.update(S.DIGITS)
    out = {}
    for ch, rows in base.items():
        rows = list(OVERRIDES.get(ch, rows))
        while len(rows) < 8:
            rows.append("." * len(rows[0]))
        # the pen rounds the bowls; letters built on a straight stem (B, D, E, P, R...) keep their corners
        if ch not in OVERRIDES and (ch.islower() or ch.isdigit() or ch in "CGOQSJU"):
            rows = _round(rows)
        out[ch] = _slant(rows)
    for ch, rows in S.PUNCT.items():
        rows = list(rows)
        while len(rows) < 8:
            rows.append("." * len(rows[0]))
        out[ch] = _slant(rows) if ch.isalnum() or ch in "!?&@$%" else rows
    return out


ACCENTS = {k: ["." + r if i == 0 else r + "." for i, r in enumerate(v)] for k, v in S.ACCENTS.items()}
CEDILLA = S.CEDILLA
COMPOSED = S.COMPOSED
SPACE = 3
