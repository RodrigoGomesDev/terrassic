"""
Terrassic 16x16 pixel-art generator: spawn eggs (one unique sprite per species), dinosaur egg block textures
(3 hatch stages) and archaic weapons / materials.  Everything is drawn with code (no external art).

usage: python3 sprites.py   -> writes into common/src/main/resources/assets/terrassic/textures/{item,block}
"""
import math
import os
import random
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEX = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures")


def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def shade(c, k):
    return (max(0, min(255, int(c[0] * k))), max(0, min(255, int(c[1] * k))), max(0, min(255, int(c[2] * k))), c[3])


def mixc(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(4))


class Canvas:
    def __init__(self, n=16):
        self.n = n
        self.p = [[None] * n for _ in range(n)]

    def set(self, x, y, c):
        if 0 <= x < self.n and 0 <= y < self.n and c is not None:
            self.p[y][x] = c

    def get(self, x, y):
        if 0 <= x < self.n and 0 <= y < self.n:
            return self.p[y][x]
        return None

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def diag(self, x0, y0, length, c, light=None, dark=None, width=2):
        """Diagonal bar going up-right from (x0,y0): pixels (x0+i, y0-i). width 2 adds the pixel to the right
        (lighter top edge / darker bottom edge for a rounded look)."""
        for i in range(length):
            x, y = x0 + i, y0 - i
            self.set(x, y, light or c)
            if width >= 2:
                self.set(x + 1, y, c)
            if width >= 3:
                self.set(x + 1, y + 1, dark or shade(c, 0.8))

    def outline(self, k=0.42, darken_outer=None):
        """Vanilla-style outline: transparent pixels touching the sprite get a dark version of the neighbour."""
        add = []
        for y in range(self.n):
            for x in range(self.n):
                if self.p[y][x] is not None:
                    continue
                nb = [self.get(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                nb = [c for c in nb if c is not None]
                if nb:
                    c = nb[0]
                    add.append((x, y, shade(c, k)))
        for x, y, c in add:
            self.p[y][x] = c

    def save(self, path, scale=1):
        img = Image.new("RGBA", (self.n, self.n), (0, 0, 0, 0))
        for y in range(self.n):
            for x in range(self.n):
                if self.p[y][x] is not None:
                    img.putpixel((x, y), self.p[y][x])
        save_png(img, path)
        return img


def save_png(img, path):
    """Writes the PNG only when its pixels changed, so re-running the generators leaves untouched files
    byte-identical (git then sees no change)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        try:
            with Image.open(path) as old:
                if old.size == img.size and old.convert("RGBA").tobytes() == img.convert("RGBA").tobytes():
                    return
        except OSError:
            pass
    img.save(path)


# ------------------------------------------------------------------ spawn eggs
# egg silhouette: (row, x_from, x_to) inclusive, 16x16, vanilla-like proportions
EGG_ROWS = {2: (6, 9), 3: (5, 10), 4: (4, 11), 5: (4, 11), 6: (3, 12), 7: (3, 12), 8: (3, 12), 9: (3, 12),
            10: (3, 12), 11: (3, 12), 12: (4, 11), 13: (5, 10), 14: (6, 9)}


def egg_mask(x, y):
    r = EGG_ROWS.get(y)
    return r is not None and r[0] <= x <= r[1]


def base_egg(c, top, bottom, light=1.22):
    """Egg body: vertical gradient top->bottom, highlight top-left, shading bottom-right."""
    cv = Canvas()
    for y, (a, b) in EGG_ROWS.items():
        for x in range(a, b + 1):
            t = (y - 2) / 12.0
            col = mixc(hexc(top), hexc(bottom), t)
            # roundness
            cx = (a + b) / 2
            edge = abs(x - cx) / max(1, (b - a) / 2)
            if x > cx and y > 6:
                col = shade(col, 1.0 - 0.18 * edge)
            if x < cx and y < 9:
                col = shade(col, 1.0 + 0.08 * (1 - edge))
            cv.set(x, y, col)
    # specular highlight
    cv.set(5, 5, shade(hexc(top), light + 0.1)); cv.set(5, 6, shade(hexc(top), light)); cv.set(6, 4, shade(hexc(top), light))
    return cv


def inside(cv, x, y):
    return egg_mask(x, y)


def eye(cv, x, y, iris="#e2a93b"):
    cv.set(x, y, hexc("#17110c")); cv.set(x - 1, y, hexc(iris))


def spawn_eggs():
    eggs = {}

    # Tyrannosaurus: brown, toothy grin, amber eye, dark back stripes
    cv = base_egg(None, "#6f5b41", "#cdb994") if False else base_egg(None, "#5e4c37", "#cdb994")
    for x in range(3, 13):
        if inside(cv, x, 9):
            cv.set(x, 9, hexc("#3a1f1c"))
        if inside(cv, x, 10) and x % 2 == 0:
            cv.set(x, 10, hexc("#efe7d2"))
        if inside(cv, x, 8) and x % 2 == 1 and x > 4:
            cv.set(x, 8, hexc("#efe7d2"))
    for (x, y) in ((7, 3), (8, 3), (6, 5), (9, 5)):
        cv.set(x, y, hexc("#3d3227"))
    eye(cv, 10, 6)
    eggs["tyrannosaurus"] = cv

    # Spinosaurus: grey-green egg with a red sail rising from the top, long jaw line
    cv = base_egg(None, "#4e5248", "#c8c0a0")
    for x, h in ((5, 1), (6, 2), (7, 3), (8, 3), (9, 2), (10, 1)):
        for k in range(h):
            cv.set(x, 2 - k, hexc("#bd3e26") if k < h - 1 else hexc("#f2ac46"))
    for x in range(5, 11):
        cv.set(x, 3, hexc("#bd3e26") if x not in (5, 10) else cv.get(x, 3))
    for x in range(3, 13):
        if inside(cv, x, 10):
            cv.set(x, 10, hexc("#2f2a22") if x > 3 else cv.get(x, 10))
    eye(cv, 9, 7, "#d8a838")
    eggs["spinosaurus"] = cv

    # Dilophosaurus: olive egg, twin red crests on top, yellow stripes
    cv = base_egg(None, "#5a5a3a", "#d9d0a8")
    for x in (6, 9):
        for y in (0, 1, 2):
            cv.set(x, y, hexc("#cc3a22") if y > 0 else hexc("#f6cc48"))
        cv.set(x + (1 if x == 6 else -1), 1, hexc("#cc3a22"))
    for y in (6, 9, 12):
        for x in range(3, 13):
            if inside(cv, x, y) and (x + y) % 3 != 0:
                cv.set(x, y, shade(cv.get(x, y), 0.75))
    eye(cv, 10, 5)
    eggs["dilophosaurus"] = cv

    # Velociraptor: tan egg with dark bars, feather tuft, sickle claw mark
    cv = base_egg(None, "#7a5a3c", "#e7d7b5")
    for y in (4, 7, 10):
        for x in range(3, 13):
            if inside(cv, x, y) and x < 11:
                cv.set(x, y, hexc("#3e2c1d"))
    cv.set(7, 1, hexc("#5b3e26")); cv.set(8, 1, hexc("#5b3e26")); cv.set(8, 0, hexc("#3e2c1d"))
    for (x, y) in ((9, 12), (10, 11), (10, 12)):
        cv.set(x, y, hexc("#1f1b18"))
    eye(cv, 10, 5, "#e0b43c")
    eggs["velociraptor"] = cv

    # Compsognathus: small green egg with a dark lateral stripe and big eye
    cv = base_egg(None, "#6e6c36", "#e0d8a8")
    for x in range(3, 13):
        if inside(cv, x, 8):
            cv.set(x, 8, hexc("#3e3e1e"))
        if inside(cv, x, 7) and x > 8:
            cv.set(x, 7, hexc("#3e3e1e"))
    for (x, y) in ((5, 4), (8, 5), (6, 11), (9, 12), (11, 10)):
        cv.set(x, y, shade(hexc("#6e6c36"), 0.7))
    cv.set(10, 5, hexc("#120d08")); cv.set(9, 5, hexc("#c9932a")); cv.set(10, 4, hexc("#c9932a"))
    eggs["compsognathus"] = cv

    # Triceratops: grey-brown egg, rust frill band with cream edge on top, three ivory horns
    cv = base_egg(None, "#7b6e57", "#c3b490")
    for x in range(4, 12):
        if inside(cv, x, 4):
            cv.set(x, 4, hexc("#a8482a"))
        if inside(cv, x, 3):
            cv.set(x, 3, hexc("#f2e4c2"))
    for x in (5, 8, 11):
        cv.set(x, 2, hexc("#f2e4c2")) if inside(cv, x, 2) else None
    cv.set(4, 6, hexc("#efe6ca")); cv.set(3, 5, hexc("#efe6ca")); cv.set(2, 4, hexc("#ffffff"))
    cv.set(11, 6, hexc("#efe6ca")); cv.set(12, 5, hexc("#efe6ca")); cv.set(13, 4, hexc("#ffffff"))
    cv.set(7, 10, hexc("#efe6ca")); cv.set(8, 10, hexc("#efe6ca")); cv.set(8, 9, hexc("#ffffff"))
    cv.set(5, 8, hexc("#17110c")); cv.set(10, 8, hexc("#17110c"))
    eggs["triceratops"] = cv

    # Stegosaurus: green egg with orange diamond plates along the top edge
    cv = base_egg(None, "#5f6b3c", "#c4c090")
    for (x, y) in ((4, 3), (6, 1), (6, 2), (8, 0), (8, 1), (8, 2), (10, 1), (10, 2), (12, 3), (5, 2), (7, 1), (9, 1), (11, 2)):
        cv.set(x, y, hexc("#e09a44") if y < 2 else hexc("#8a2a1a"))
    for y in range(5, 13):
        for x in range(3, 13):
            if inside(cv, x, y) and (x * 2 + y) % 7 == 0:
                cv.set(x, y, shade(cv.get(x, y), 0.8))
    eye(cv, 10, 8, "#b5862c")
    eggs["stegosaurus"] = cv

    # Ankylosaurus: brown egg covered in ochre scute dots, side spikes
    cv = base_egg(None, "#6b5f48", "#b5a988")
    for y in range(3, 14):
        for x in range(3, 13):
            if inside(cv, x, y) and x % 2 == 0 and y % 2 == 1:
                cv.set(x, y, hexc("#d2a456"))
    for y in (7, 10):
        cv.set(2, y, hexc("#ece4c8")); cv.set(13, y, hexc("#ece4c8"))
    eggs["ankylosaurus"] = cv

    # Brachiosaurus: tall grey egg with a long neck silhouette and red nasal crest
    cv = base_egg(None, "#7f8984", "#c7c2a8")
    for i in range(7):
        cv.set(9 - i // 3, 12 - i, shade(hexc("#5a6262"), 0.85))
        cv.set(10 - i // 3, 12 - i, hexc("#5a6262"))
    cv.set(7, 5, hexc("#5a6262")); cv.set(6, 5, hexc("#5a6262")); cv.set(6, 4, hexc("#5a6262"))
    cv.set(7, 4, hexc("#b8442f")); cv.set(7, 3, hexc("#b8442f"))
    cv.set(6, 5, hexc("#17110c"))
    eggs["brachiosaurus"] = cv

    # Parasaurolophus: teal egg with the long red crest sweeping back from the top
    cv = base_egg(None, "#46584c", "#d8d4b0")
    for i, (x, y) in enumerate(((7, 4), (6, 3), (5, 2), (4, 1), (3, 0))):
        cv.set(x, y, hexc("#c0402c") if i % 2 == 0 else hexc("#f0cc7c"))
        cv.set(x + 1, y, hexc("#8a2a1e"))
    for y in (7, 10):
        for x in range(3, 13):
            if inside(cv, x, y) and x > 4:
                cv.set(x, y, shade(cv.get(x, y), 0.78))
    eye(cv, 10, 6, "#b8862c")
    eggs["parasaurolophus"] = cv

    # Pachycephalosaurus: brown egg with a cream dome cap and knobs
    cv = base_egg(None, "#8a7458", "#d6c6a4")
    for y in range(2, 6):
        a, b = EGG_ROWS[y]
        for x in range(a, b + 1):
            cv.set(x, y, hexc("#d8b07a") if (y != 5) else hexc("#a8865a"))
    for x in (4, 6, 9, 11):
        cv.set(x, 6, hexc("#f4ead0"))
    cv.set(6, 3, hexc("#f2e2c0"))
    eye(cv, 10, 8, "#c98a2a")
    eggs["pachycephalosaurus"] = cv

    # Gallimimus: pale grey egg with a black wing band and white tips, little beak
    cv = base_egg(None, "#8f8678", "#ebe4d0")
    for x in range(3, 13):
        if inside(cv, x, 9):
            cv.set(x, 9, hexc("#3a3632"))
        if inside(cv, x, 10) and x % 2 == 0:
            cv.set(x, 10, hexc("#f2efe6"))
    cv.set(12, 5, hexc("#5a4e40")); cv.set(13, 5, hexc("#5a4e40")); cv.set(13, 6, hexc("#3a3028"))
    eye(cv, 10, 4, "#d89a2a")
    eggs["gallimimus"] = cv

    # Maiasaura: brown egg with dark blotches and a little orange crest
    cv = base_egg(None, "#5a4a36", "#e0d6b6")
    for (x, y) in ((4, 8), (5, 8), (9, 9), (10, 9), (6, 11), (11, 11), (7, 7)):
        if inside(cv, x, y):
            cv.set(x, y, hexc("#3e3226"))
    cv.set(8, 2, hexc("#c06a36")); cv.set(9, 2, hexc("#d8a860"))
    cv.set(12, 6, hexc("#3e362e")); cv.set(13, 6, hexc("#3e362e")); cv.set(13, 7, hexc("#2a241e"))
    eye(cv, 10, 5, "#b8862c")
    eggs["maiasaura"] = cv

    # Pteranodon: grey-white egg with a slate wing band and a red crest sweeping back
    cv = base_egg(None, "#77736a", "#ece6d8")
    for x in range(3, 13):
        if inside(cv, x, 10):
            cv.set(x, 10, hexc("#6a5244"))
    cv.set(4, 3, hexc("#c0482a")); cv.set(5, 3, hexc("#c0482a")); cv.set(3, 2, hexc("#e8a040")); cv.set(6, 4, hexc("#c0482a"))
    cv.set(11, 6, hexc("#d8c08a")); cv.set(12, 6, hexc("#d8c08a")); cv.set(13, 7, hexc("#b8a070"))
    eye(cv, 9, 5, "#d8a838")
    eggs["pteranodon"] = cv

    # Quetzalcoatlus: sandy cream egg with a long grey beak line running diagonally and the red face patch
    cv = base_egg(None, "#9a9284", "#efe9dc")
    for k, (x, y) in enumerate(((4, 11), (5, 10), (6, 10), (7, 9), (8, 9), (9, 8), (10, 8), (11, 7))):
        if inside(cv, x, y):
            cv.set(x, y, hexc("#d8c89a" if k < 6 else "#2a2522"))
    for (x, y) in ((4, 4), (5, 4), (6, 3)):
        cv.set(x, y, hexc("#9a3a2a"))
    cv.set(7, 6, hexc("#c8472e")); cv.set(8, 6, hexc("#c8472e")); cv.set(7, 7, hexc("#c8472e"))
    cv.set(10, 12, hexc("#5b5550")); cv.set(11, 12, hexc("#5b5550"))
    eye(cv, 9, 6, "#e6c24a")
    eggs["quetzalcoatlus"] = cv

    # Hatzegopteryx: dark slate egg with a broad black band, pale face patch and the dark red keel
    cv = base_egg(None, "#4e4a48", "#9c948c")
    for x in range(3, 13):
        if inside(cv, x, 8):
            cv.set(x, 8, hexc("#1f1a19"))
        if inside(cv, x, 9) and x % 2 == 0:
            cv.set(x, 9, hexc("#1f1a19"))
    for (x, y) in ((5, 5), (6, 5), (5, 6), (6, 6)):
        cv.set(x, y, hexc("#d8c6a8"))
    for (x, y) in ((8, 3), (9, 3), (10, 4)):
        cv.set(x, y, hexc("#7a2a22"))
    cv.set(10, 11, hexc("#5a4a3e")); cv.set(11, 11, hexc("#5a4a3e")); cv.set(12, 10, hexc("#1e1917"))
    eye(cv, 7, 5, "#d9b14a")
    eggs["hatzegopteryx"] = cv

    # Ichthyornis: small pale blue-grey egg speckled dark like a tern's, a tiny toothed beak line
    cv = base_egg(None, "#9fb0b4", "#e4ebe8")
    rnd = random.Random("ichthyornis")
    for _ in range(14):
        x, y = rnd.randrange(3, 13), rnd.randrange(3, 14)
        if inside(cv, x, y):
            cv.set(x, y, hexc("#4a4a4c" if rnd.random() < 0.6 else "#6e6560"))
    cv.set(10, 6, hexc("#2a2b2e")); cv.set(11, 6, hexc("#2a2b2e")); cv.set(12, 7, hexc("#2a2b2e"))
    cv.set(11, 7, hexc("#f4f0e4"))
    eye(cv, 9, 5, "#2b2420")
    eggs["ichthyornis"] = cv

    # Mosasaurus: dark sea-blue egg with a pale belly, a row of teeth and a tail fluke
    cv = base_egg(None, "#2e3a44", "#d8dbd0")
    for x in range(3, 13):
        if inside(cv, x, 9):
            cv.set(x, 9, hexc("#8a3a36"))
        if inside(cv, x, 8) and x % 2 == 1:
            cv.set(x, 8, hexc("#efe9d6"))
        if inside(cv, x, 10) and x % 2 == 0:
            cv.set(x, 10, hexc("#efe9d6"))
    cv.set(2, 3, hexc("#26323a")); cv.set(3, 4, hexc("#26323a")); cv.set(2, 5, hexc("#26323a"))
    eye(cv, 10, 5, "#c8b04a")
    eggs["mosasaurus"] = cv

    # Tylosaurus: slate egg with pale vertical bars and the pale rostrum knob at the front (live-bearer: spawn egg only)
    cv = base_egg(None, "#243038", "#6e7e84")
    for x in range(3, 13, 3):
        for y in range(4, 13):
            if inside(cv, x, y) and (y + x) % 2 == 0:
                cv.set(x, y, hexc("#8a9a9e"))
    cv.set(11, 7, hexc("#9aa09a")); cv.set(12, 7, hexc("#9aa09a")); cv.set(12, 8, hexc("#9aa09a"))
    for x in range(6, 11):
        cv.set(x, 9, hexc("#efe9d6" if x % 2 == 0 else "#86363a"))
    eye(cv, 9, 6, "#d8b85a")
    eggs["tylosaurus"] = cv

    # Elasmosaurus: dark teal egg with leopard spots and a long pale neck line curling over the top (live-bearer: spawn egg only)
    cv = base_egg(None, "#2a4a4a", "#9ab4ae")
    rnd = random.Random("elasmosaurus")
    for _ in range(10):
        x, y = rnd.randrange(3, 13), rnd.randrange(5, 14)
        if inside(cv, x, y):
            cv.set(x, y, hexc("#1c3232"))
    for x, y in ((5, 9), (5, 8), (5, 7), (6, 6), (7, 5), (8, 4), (9, 4), (10, 4)):
        if inside(cv, x, y):
            cv.set(x, y, hexc("#dfe3d8"))
    cv.set(11, 4, hexc("#2a4a4a")); cv.set(11, 5, hexc("#2a4a4a"))
    eye(cv, 10, 5, "#d8c060")
    eggs["elasmosaurus"] = cv

    # species with a front-view 32x32 design (egg_designs.py) use it; the rest keep the 16x16 sketch above
    import egg_designs
    for name, cv in eggs.items():
        path = os.path.join(TEX, "item", f"{name}_spawn_egg.png")
        if name in egg_designs.ORDER:
            save_png(egg_designs.render(name), path)   # no-op when the pixels did not change
            continue
        cv.outline(0.45)
        cv.save(path)
    return eggs


# ------------------------------------------------------------------ dinosaur egg blocks
EGG_BLOCK = {
    # species: (shell, spots)
    "tyrannosaurus": ("#e4d6b8", "#8a6a4a"), "spinosaurus": ("#d8d2bc", "#6b6f60"),
    "dilophosaurus": ("#e2dcbc", "#8a8455"), "velociraptor": ("#ece2cc", "#7a5a3c"),
    "compsognathus": ("#eae6c8", "#8c874a"), "triceratops": ("#e6dcc4", "#a8482a"),
    "stegosaurus": ("#dfe0c4", "#5f6b3c"), "ankylosaurus": ("#d8ccb0", "#6b5f48"),
    "brachiosaurus": ("#e2e2d6", "#7f8984"), "parasaurolophus": ("#dfe6d8", "#46584c"),
    "pachycephalosaurus": ("#e8dcc4", "#8a7458"), "gallimimus": ("#f0ece0", "#9c917c"),
    "maiasaura": ("#e4dac0", "#7a6244"),
    "pteranodon": ("#e6e2d4", "#5c6870"),
    "quetzalcoatlus": ("#efe9dc", "#8c8378"), "hatzegopteryx": ("#9c948c", "#2a2626"),
    "ichthyornis": ("#e4ebe8", "#4a4a4c"),
}


def egg_blocks():
    import random
    for name, (shell, spot) in EGG_BLOCK.items():
        rnd = random.Random(name)
        base = Canvas()
        for y in range(16):
            for x in range(16):
                col = hexc(shell)
                col = shade(col, 0.94 + 0.08 * rnd.random())
                if y < 5:
                    col = shade(col, 1.04)
                if y > 12:
                    col = shade(col, 0.9)
                base.set(x, y, col)
        for _ in range(16):
            x, y = rnd.randrange(16), rnd.randrange(16)
            base.set(x, y, hexc(spot))
            if rnd.random() < 0.5:
                base.set(x + 1, y, shade(hexc(spot), 1.1))
        for stage in range(3):
            cv = Canvas()
            cv.p = [row[:] for row in base.p]
            dark = shade(hexc(shell), 0.35)
            if stage >= 1:
                cv.line(3, 6, 6, 8, dark); cv.line(6, 8, 8, 6, dark); cv.line(8, 6, 11, 8, dark)
            if stage >= 2:
                cv.line(11, 8, 13, 6, dark); cv.line(5, 10, 8, 12, dark); cv.line(8, 12, 10, 10, dark)
                cv.set(7, 7, shade(hexc(shell), 0.2)); cv.set(9, 7, shade(hexc(shell), 0.2))
            cv.save(os.path.join(TEX, "block", f"{name}_egg_{stage}.png"))


# ------------------------------------------------------------------ weapons and materials
WOOD = hexc("#8a6034"); WOOD_L = hexc("#b0824c"); WOOD_D = hexc("#5e3e1e")
LEATHER = hexc("#6e4426"); LEATHER_D = hexc("#4a2c18")
STRING = hexc("#d8d0b8")
FLINT = hexc("#4a4a4e"); FLINT_L = hexc("#7a7a80"); FLINT_D = hexc("#2c2c30")
BONE = hexc("#e8e0c8"); BONE_D = hexc("#b8ad90"); BONE_L = hexc("#fbf6e8")
IVORY = hexc("#efe6ca"); IVORY_D = hexc("#c9bc96")
HORN_B = hexc("#7a6748")
CLUB = hexc("#8b7d62"); CLUB_L = hexc("#b4a482"); CLUB_D = hexc("#5e5440"); SCUTE = hexc("#c9a05a")


def handle(cv, x0, y0, length, wrap_from=None, wrap_len=0):
    for i in range(length):
        x, y = x0 + i, y0 - i
        cv.set(x, y, WOOD_L)
        cv.set(x + 1, y, WOOD)
    if wrap_from is not None:
        for i in range(wrap_from, wrap_from + wrap_len):
            x, y = x0 + i, y0 - i
            cv.set(x, y, LEATHER if i % 2 == 0 else LEATHER_D)
            cv.set(x + 1, y, LEATHER_D)


def weapons():
    out = {}
    # flint knife
    cv = Canvas()
    handle(cv, 2, 13, 4, 0, 3)
    cv.set(5, 9, BONE); cv.set(6, 10, BONE); cv.set(6, 9, BONE_D)
    for i in range(7):
        x, y = 6 + i, 8 - i
        cv.set(x, y, FLINT_L); cv.set(x + 1, y, FLINT)
        if i < 5:
            cv.set(x + 1, y + 1, FLINT_D)
    cv.set(13, 1, FLINT_L)
    out["flint_knife"] = cv

    # flint hatchet (hand axe on a short haft)
    cv = Canvas()
    handle(cv, 2, 14, 10, 0, 2)
    head = [(9, 2), (10, 2), (8, 3), (9, 3), (10, 3), (11, 3), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4), (12, 4),
            (7, 5), (8, 5), (9, 5), (11, 5), (12, 5), (13, 5), (8, 6), (12, 6), (13, 6), (13, 7)]
    for (x, y) in head:
        cv.set(x - 1, y, FLINT if (x + y) % 3 else FLINT_L)
    for (x, y) in ((6, 4), (7, 3), (8, 2)):
        cv.set(x, y, FLINT_L)
    cv.set(10, 5, STRING); cv.set(11, 6, STRING); cv.set(9, 6, STRING)
    out["flint_hatchet"] = cv

    # bone club
    cv = Canvas()
    for i in range(8):
        x, y = 3 + i, 12 - i
        cv.set(x, y, BONE_L); cv.set(x + 1, y, BONE); cv.set(x + 1, y + 1, BONE_D)
    for (x, y) in ((10, 2), (11, 2), (12, 2), (9, 3), (10, 3), (11, 3), (12, 3), (13, 3), (9, 4), (10, 4), (11, 4),
                   (12, 4), (13, 4), (10, 5), (11, 5), (12, 5), (13, 5), (12, 6)):
        cv.set(x, y, BONE if (x + y) % 4 else BONE_L)
    for (x, y) in ((13, 2), (14, 4), (9, 2), (11, 6)):
        cv.set(x, y, BONE_D)
    for (x, y) in ((2, 13), (3, 14), (2, 14), (1, 13)):
        cv.set(x, y, BONE)
    cv.set(3, 12, LEATHER); cv.set(4, 11, LEATHER_D); cv.set(4, 12, LEATHER_D)
    out["bone_club"] = cv

    # flint spear
    cv = Canvas()
    for i in range(11):
        x, y = 1 + i, 14 - i
        cv.set(x, y, WOOD_L if i % 3 else WOOD)
        cv.set(x + 1, y + 1, WOOD_D) if i % 4 == 0 else None
    cv.set(10, 5, STRING); cv.set(11, 4, STRING); cv.set(11, 5, STRING)
    for (x, y, c) in ((12, 3, FLINT), (13, 3, FLINT), (12, 2, FLINT_L), (13, 2, FLINT), (14, 2, FLINT_D),
                      (13, 1, FLINT_L), (14, 1, FLINT), (15, 0, FLINT_L), (12, 4, FLINT_D), (11, 3, FLINT_L)):
        cv.set(x, y, c)
    out["flint_spear"] = cv

    # horn spear (triceratops horn tip)
    cv = Canvas()
    for i in range(10):
        x, y = 1 + i, 14 - i
        cv.set(x, y, WOOD_L if i % 3 else WOOD)
    cv.set(9, 6, LEATHER); cv.set(10, 5, LEATHER_D); cv.set(10, 6, LEATHER)
    for (x, y, c) in ((11, 4, HORN_B), (10, 4, HORN_B), (11, 5, HORN_B), (12, 3, IVORY_D), (11, 3, IVORY), (12, 4, IVORY_D),
                      (13, 2, IVORY), (12, 2, IVORY), (13, 3, IVORY_D), (14, 1, IVORY), (13, 1, hexc("#fbf6e8")), (15, 0, hexc("#ffffff"))):
        cv.set(x, y, c)
    out["horn_spear"] = cv

    # T. rex tooth dagger
    cv = Canvas()
    handle(cv, 2, 13, 4, 0, 4)
    cv.set(5, 10, BONE_D); cv.set(6, 10, BONE); cv.set(5, 9, BONE)
    tooth = [(6, 8, 3), (7, 7, 3), (8, 6, 3), (9, 5, 2), (10, 4, 2), (11, 3, 2), (12, 2, 1), (13, 1, 1)]
    for (x, y, w) in tooth:
        for k in range(w):
            c = IVORY if k == 0 else (IVORY_D if k == w - 1 else BONE_L)
            cv.set(x + k, y + (1 if k == 2 else 0), c)
    for (x, y) in ((8, 8), (10, 6), (12, 4)):
        cv.set(x, y, IVORY_D)
    out["rex_tooth_dagger"] = cv

    # ankylosaurus tail club (weapon)
    cv = Canvas()
    handle(cv, 1, 14, 7, 0, 3)
    blob = [(8, 2), (9, 2), (10, 2), (11, 2), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3), (12, 3), (7, 4), (8, 4), (9, 4),
            (10, 4), (11, 4), (12, 4), (13, 4), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5), (13, 5), (8, 6), (9, 6),
            (10, 6), (11, 6), (12, 6), (9, 7), (10, 7), (11, 7)]
    for (x, y) in blob:
        cv.set(x, y, CLUB_L if (y < 4 or x < 9) else (CLUB_D if (x > 11 and y > 5) else CLUB))
    for (x, y) in ((9, 3), (11, 4), (9, 5), (11, 6), (12, 4)):
        cv.set(x, y, SCUTE)
    out["tail_club"] = cv

    # materials ----------------------------------------------------------
    cv = Canvas()  # rex tooth
    for (y, a, b) in ((2, 9, 9), (3, 8, 9), (4, 8, 9), (5, 7, 9), (6, 7, 10), (7, 6, 10), (8, 6, 10), (9, 6, 10),
                      (10, 5, 10), (11, 5, 10), (12, 5, 10), (13, 6, 9)):
        for x in range(a, b + 1):
            cv.set(x, y, IVORY if x < b else IVORY_D)
        cv.set(a, y, hexc("#fbf6e8"))
    for x in range(6, 10):
        cv.set(x, 13, hexc("#a08a64"))
    cv.set(8, 6, IVORY_D); cv.set(8, 9, IVORY_D)
    out["rex_tooth"] = cv

    cv = Canvas()  # mosasaurus tooth: stout cone curving back, with a brown root
    for (y, a, b) in ((2, 10, 10), (3, 9, 10), (4, 9, 11), (5, 8, 11), (6, 8, 11), (7, 7, 11), (8, 7, 11),
                      (9, 6, 11), (10, 6, 11)):
        for x in range(a, b + 1):
            cv.set(x, y, IVORY if x < b else IVORY_D)
        cv.set(a, y, hexc("#fbf6e8"))
    for (y, a, b) in ((11, 5, 11), (12, 5, 11), (13, 6, 10)):
        for x in range(a, b + 1):
            cv.set(x, y, hexc("#8a6a48") if x < b else hexc("#64482e"))
    cv.set(9, 6, IVORY_D); cv.set(8, 9, IVORY_D)
    out["mosasaurus_tooth"] = cv

    cv = Canvas()  # triceratops horn (curved)
    pts = [(3, 13, 4), (4, 12, 4), (5, 11, 4), (6, 10, 4), (7, 9, 3), (8, 8, 3), (9, 7, 3), (10, 6, 2), (10, 5, 2), (11, 4, 2), (11, 3, 1), (12, 2, 1), (12, 1, 1)]
    for i, (x, y, w) in enumerate(pts):
        t = i / (len(pts) - 1)
        c = mixc(HORN_B, IVORY, min(1.0, t * 1.3))
        for k in range(w):
            cv.set(x + k, y, c if k else shade(c, 1.12))
    out["triceratops_horn"] = cv

    cv = Canvas()  # ankylosaurus club (material)
    for (y, a, b) in ((4, 6, 9), (5, 4, 11), (6, 3, 12), (7, 3, 12), (8, 3, 12), (9, 3, 12), (10, 4, 11), (11, 6, 9)):
        for x in range(a, b + 1):
            cv.set(x, y, CLUB_L if y < 7 else (CLUB_D if y > 9 else CLUB))
    for (x, y) in ((5, 6), (8, 5), (10, 7), (6, 9), (9, 9)):
        cv.set(x, y, SCUTE)
    for y in (12, 13, 14):
        cv.set(7, y, BONE_D); cv.set(8, y, BONE)
    out["ankylosaurus_club"] = cv

    for sid, cv in hide_sprites().items():
        out[f"{sid}_hide"] = cv

    for name, cv in out.items():
        cv.outline(0.42)
        cv.save(os.path.join(TEX, "item", f"{name}.png"))
    return out


# ------------------------------------------------------------------ hides
FUZZY = {"velociraptor", "gallimimus", "compsognathus", "pteranodon", "quetzalcoatlus", "hatzegopteryx", "ichthyornis"}  # feathers / pycnofibres
HIDE_ROWS = {2: ((4, 5), (10, 11)), 3: ((3, 12),), 4: ((2, 13),), 5: ((2, 13),), 6: ((2, 13),), 7: ((2, 13),),
             8: ((2, 13),), 9: ((2, 13),), 10: ((2, 13),), 11: ((3, 12),), 12: ((4, 5), (10, 11))}


def species_palettes():
    """{species: palette} read from the modelgen species files (the same colours as the entity texture)."""
    import importlib
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(here, "..", "modelgen"), os.path.join(here, "..", "modelgen", "species")):
        if p not in sys.path:
            sys.path.insert(0, p)
    from build_all import ALL
    return {sid: importlib.import_module(sid).build().palette for sid in ALL}


def hide_sprite(sid, pal):
    """A stretched pelt with four leg flaps: dorsal colour down the middle, flank at the sides, belly along the
    bottom edge; scaly species get a checker of darker scales, fuzzy ones get speckles."""
    dorsal, flank = hexc(pal["dorsal"]), hexc(pal["flank"])
    belly = hexc(pal.get("belly", pal["flank"]))
    dark = shade(dorsal, 0.72)
    cv = Canvas()
    for y, spans in HIDE_ROWS.items():
        for a, b in spans:
            for x in range(a, b + 1):
                c = flank
                if 5 <= x <= 10 and 3 <= y <= 11:
                    c = dorsal
                if y >= 10 and (x < 5 or x > 10):
                    c = belly
                if sid in FUZZY:
                    if (x * 7 + y * 3) % 5 == 0:
                        c = dark
                elif (x + y) % 2 == 0 and 3 <= y <= 11:
                    c = shade(c, 0.9)
                if x == a or x == b or y in (2, 12):
                    c = shade(c, 0.78)          # rolled edge
                if x == a + 1 and y in range(4, 9):
                    c = shade(c, 1.15)          # highlight
                cv.set(x, y, c)
    cv.set(7, 6, shade(dorsal, 1.1)); cv.set(8, 7, shade(dorsal, 1.1))
    return cv


def hide_sprites():
    return {sid: hide_sprite(sid, pal) for sid, pal in species_palettes().items()}


def preview(path):
    """Contact sheet of every generated item sprite, upscaled 8x."""
    names = sorted(f for f in os.listdir(os.path.join(TEX, "item")) if f.endswith(".png"))
    blocks = sorted(f for f in os.listdir(os.path.join(TEX, "block")) if f.endswith(".png"))
    cell = 16 * 6 + 8
    cols = 8
    allf = [("item", n) for n in names] + [("block", n) for n in blocks if n.endswith("_0.png") or n.startswith("tyrannosaurus")]
    rows = (len(allf) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (70, 70, 80, 255))
    for i, (d, n) in enumerate(allf):
        im = Image.open(os.path.join(TEX, d, n)).resize((96, 96), Image.NEAREST)
        sheet.alpha_composite(im, ((i % cols) * cell + 4, (i // cols) * cell + 4))
    sheet.save(path)


if __name__ == "__main__":
    import sys
    spawn_eggs()
    egg_blocks()
    weapons()
    if len(sys.argv) > 1:
        preview(sys.argv[1])
    print("sprites written to", TEX)
