"""
A pixel font built from glyph grids ('#' = ink): composes accented letters, lays out text like Minecraft's bitmap
fonts (advance = glyph width + 1 + extra spacing) and renders specimens.

Coordinates: a glyph is a list of rows, top first. `above` = rows above the baseline (the font's ascent for that sheet).
"""
from PIL import Image


class Glyph:
    def __init__(self, rows, above):
        width = max((len(r) for r in rows), default=0)
        self.rows = [r.ljust(width, ".") for r in rows]
        self.above = above            # rows of this glyph that sit above the baseline
        self.width = width

    @property
    def height(self):
        return len(self.rows)

    def ink_width(self):
        w = 0
        for r in self.rows:
            for i, ch in enumerate(r):
                if ch == "#":
                    w = max(w, i + 1)
        return w


def overlay(base, mark, dx, dy):
    """Rows of `mark` stamped onto `base` at (dx, dy); grows base downwards/rightwards if needed."""
    rows = [list(r) for r in base]
    for y, r in enumerate(mark):
        yy = y + dy
        while yy >= len(rows):
            rows.append(["."] * len(rows[0]))
        for x, ch in enumerate(r):
            if ch != "#":
                continue
            xx = x + dx
            if xx >= len(rows[yy]):
                for row in rows:
                    row.extend(["."] * (xx + 1 - len(row)))
            rows[yy][xx] = "#"
    return ["".join(r) for r in rows]


class PixelFont:
    """glyphs: char -> rows (base cell of `cell_h` rows, `ascent` above the baseline)."""

    def __init__(self, name, glyphs, cell_h, ascent, space, accents=None, composed=None, cedilla=None,
                 accent_gap=0, spacing=0, upper_caps_accent_rows=2):
        self.name = name
        self.cell_h = cell_h
        self.ascent = ascent
        self.space = space
        self.spacing = spacing
        self.base = {}
        for ch, rows in glyphs.items():
            rows = list(rows)
            while len(rows) < cell_h:
                rows.append("." * len(rows[0]))
            self.base[ch] = Glyph(rows, ascent)
        # accented glyphs live on a taller sheet: `extra` rows on top for the mark
        self.extra = len(next(iter(accents.values()))) + accent_gap if accents else 0
        self.accented = {}
        if composed:
            for ch, (b, mark) in composed.items():
                if b not in self.base:
                    continue
                g = self.base[b]
                rows = ["." * g.width] * self.extra + g.rows
                if mark == "cedilla":
                    m = cedilla
                    dy = self.extra + ascent          # the first row under the baseline
                else:
                    m = accents[mark]
                    if b.isupper():
                        dy = 0
                    else:
                        # lowercase: the mark sits just above the x-height (top of the first inked row)
                        top = next(i for i, r in enumerate(g.rows) if "#" in r)
                        dy = max(0, self.extra + top - len(m) - 1)
                mw = max(len(r) for r in m)
                ink = [i for r in g.rows for i, c in enumerate(r) if c == "#"]
                centre = (min(ink) + max(ink) + 1) / 2.0
                dx = max(0, int(round(centre - mw / 2.0)))
                self.accented[ch] = Glyph(overlay(rows, m, dx, dy), ascent + self.extra)

    def glyph(self, ch):
        return self.base.get(ch) or self.accented.get(ch)

    def chars(self):
        return list(self.base) + list(self.accented)

    def advance(self, ch):
        if ch == " ":
            return self.space
        g = self.glyph(ch)
        if g is None:
            return self.space + 1
        return g.ink_width() + 1 + self.spacing

    def text_width(self, s):
        return sum(self.advance(c) for c in s)

    def draw(self, img, s, x, y, colour, scale=1, shadow=None):
        """Draws `s` with its baseline at y + ascent * scale (y = top of the line)."""
        px = img.load()
        for pass_, col in ((1, shadow), (0, colour)) if shadow else ((0, colour),):
            cx = x
            for ch in s:
                g = self.glyph(ch)
                if g is not None:
                    top = y + (self.ascent - g.above) * scale + pass_ * scale
                    for gy, row in enumerate(g.rows):
                        for gx, c in enumerate(row):
                            if c != "#":
                                continue
                            for sy in range(scale):
                                for sx in range(scale):
                                    X = cx + (gx + pass_) * scale + sx
                                    Y = top + gy * scale + sy
                                    if 0 <= X < img.width and 0 <= Y < img.height:
                                        px[X, Y] = col
                cx += self.advance(ch) * scale
        return cx

    def sheet(self, glyphs, cell_w, cell_h, per_row=16, spacer_alpha=False):
        """A Minecraft bitmap sheet: glyphs left-aligned in equal cells. Returns (image, rows of chars).
        spacer_alpha: adds an almost invisible pixel after each glyph so Minecraft counts `spacing` extra columns."""
        items = list(glyphs)
        nrows = (len(items) + per_row - 1) // per_row
        img = Image.new("RGBA", (cell_w * per_row, cell_h * nrows), (0, 0, 0, 0))
        px = img.load()
        lines = []
        for r in range(nrows):
            line = ""
            for c in range(per_row):
                i = r * per_row + c
                if i >= len(items):
                    line += "\u0000"
                    continue
                ch, g = items[i]
                line += ch
                if g.width > cell_w or g.height > cell_h:
                    raise SystemExit(f"{self.name}: glyph {ch!r} {g.width}x{g.height} does not fit {cell_w}x{cell_h}")
                for gy, row in enumerate(g.rows):
                    for gx, cc in enumerate(row):
                        if cc == "#":
                            px[c * cell_w + gx, r * cell_h + gy] = (255, 255, 255, 255)
                if spacer_alpha and self.spacing:
                    sx = g.ink_width() + self.spacing - 1
                    if sx < cell_w:
                        px[c * cell_w + sx, r * cell_h + cell_h - 1] = (255, 255, 255, 1)
            lines.append(line)
        return img, lines
