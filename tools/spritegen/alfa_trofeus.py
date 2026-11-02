"""
The alpha's spoils (docs/ALFAS.md "Recompensa"): the skull trophy and the hide rug of each T. rex alpha coat.

Study (02/11, see docs/ALFAS.md):
- The common trophy is a flat skull sprite on a plank plaque, the same for every species. The alpha's is a real
  3D skull in profile (tools/javagen/gen_blocks.py PROPS), mounted on its own hide stretched on a stick frame and
  laced to it, the way the mod's tanning frames are: the hide says which alpha it was (Marfim or Brasa).
- The skull follows a T. rex in side view: keyhole orbit with the rugose boss over it, the big antorbital opening,
  the narrow naris at the tip, the lateral temporal opening behind the eye, one row of teeth. An old ruler carries
  old wounds, like the Sue specimen (FMNH PR 2081): round healed pits in the lower jaw and a healed groove on the
  back of the skull, and one upper tooth broken off.
- The rugs are not the scale pattern every species rug shares: they are the alpha's back, cracked plates in the
  coat colour with the chevron marks of its back (rosy scars on Marfim, near-black bands on Brasa); laid side by
  side the chevrons line up into a band down the rug.

All textures are 16x16 and drawn here (no external art); light from the top-left like the vanilla blocks.
usage: python3 -B alfa_trofeus.py   -> writes into common/src/main/resources/assets/terrassic/textures/block
"""
import math
import os
import random

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEX = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "block")
N = 16


def hx(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


# coats: the alpha skins' own colours (tools/modelgen/handmade/tyrannosaurus/rex2.py ALPHA_MALE / ALPHA_FEMALE)
COATS = {
    "ivory": {  # Marfim (male): cold white, rosy scar marks
        "skin": [hx("85817a"), hx("b3afa7"), hx("c6c3bb"), hx("d7d4cd"), hx("e6e3dd")],
        "crack": hx("6f6b65"),
        "mark": [hx("9e8c87"), hx("b8a5a0"), hx("cfb3ab")],
    },
    "ember": {  # Brasa (female): blood red, near-black bands
        "skin": [hx("34120e"), hx("561812"), hx("732116"), hx("8f2c1c"), hx("ad4128")],
        "crack": hx("240c09"),
        "mark": [hx("170c0b"), hx("241210"), hx("3e1913")],
    },
}
# old bone, years in the sun: tan, not chalk white (it has to stand off the white Marfim hide behind it)
BONE = [hx("5e4c36"), hx("86704f"), hx("a68e6a"), hx("bfa883"), hx("d6c39d")]
HOLE, HOLE_RIM = hx("2a241c"), hx("4a4032")
TOOTH, TOOTH_ROOT = hx("e9dcb4"), hx("a88f5c")
STICK = [hx("3a2814"), hx("54391d"), hx("6e4d2a"), hx("87623a")]
LACE, LACE_D = hx("d8c9a4"), hx("a8946c")


def img():
    return Image.new("RGBA", (N, N), (0, 0, 0, 0))


def noise(seed):
    rnd = random.Random(seed)
    return [[rnd.random() for _ in range(N)] for _ in range(N)]


def cells(seed, count):
    """Tileable Voronoi on the 16x16 torus: owner of each pixel and whether it lies on a crack between plates."""
    rnd = random.Random(seed)
    pts = [(rnd.uniform(0, N), rnd.uniform(0, N)) for _ in range(count)]
    owner, edge = [[0] * N for _ in range(N)], [[False] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            ds = sorted((min(abs(x + 0.5 - px), N - abs(x + 0.5 - px)) ** 2 + min(abs(y + 0.5 - py), N - abs(y + 0.5 - py)) ** 2, i)
                        for i, (px, py) in enumerate(pts))
            owner[y][x] = ds[0][1]
            edge[y][x] = math.sqrt(ds[1][0]) - math.sqrt(ds[0][0]) < 0.9
    return owner, edge


# ------------------------------------------------------------------ the skull (viewer space: u right, v down)
# The alpha T. rex skull in profile, snout to the left, one character per pixel; gen_blocks.py builds the 3D model
# from it (each run of a row is a box; the openings are real holes, the stretched hide shows through them).
#   b bone  r rugose boss over the eye  g healed groove  T upper tooth  t lower tooth  j jaw  p healed pit
#   . nothing (the orbit, the antorbital and temporal openings, the naris and the open mouth are holes)
SKULL_U, SKULL_V = 1, 2          # where the mask's first column / row sits in the texture (viewer space)
SKULL_SCALE = 0.75               # the skull is set at 3/4: at full size it covered the hide and the two coats looked alike
SKULL = [
    "........r.r..",
    ".....bbbbbbbb",
    "..bbbbbbb.bbg",
    ".bbbb..bb..bg",
    "b.bb...bbbb.b",
    "bbbbbbbbbbb.b",
    "bbbbbbbbbbbbb",
    "T.T.T...T.T.b",
    ".mmmmmmmmmmbb",
    "..t.t.t.t.jjj",
    ".jjjjjjjjpjpj",
    "..jjjjjjjjjj.",
]
# m: the inside of the open mouth (dark, no bone); every hole closed in on both sides along its row is dark inside
# too, so the openings read as openings and not as the hide behind


def skull_depth(ch, c):
    """(z0, z1) of a pixel of the mask: the back of the skull is wide (the jaw muscles), the snout narrow, the
    teeth inside the jaw line, the boss over the eye stands out at the side."""
    if ch == "r":
        return 9.5, 12.0
    if ch in "Tt":
        return 11.0, 13.0
    if ch in "jp":
        return (10.0, 14.0) if c >= 9 else (10.5, 13.5)
    return (9.0, 15.0) if c >= 7 else (10.5, 13.5)


def inside(r, c):
    """Whether this pixel of the mask is the dark inside of the skull (the open mouth, or a hole between bones)."""
    row = SKULL[r]
    if row[c] == "m":
        return True
    return row[c] == "." and any(ch not in ".m" for ch in row[:c]) and any(ch not in ".m" for ch in row[c + 1:])


def skull_runs():
    """[(u0, u1, v0, v1, z0, z1, kind)] in block pixels; kind "bone", "teeth" or "inside" (the dark back wall of
    the openings and of the mouth, just in front of the hide)."""
    out = []
    for r, row in enumerate(SKULL):
        c = 0
        while c < len(row):
            if inside(r, c):
                e = c + 1
                while e < len(row) and inside(r, e) and (e >= 7) == (c >= 7):
                    e += 1
                z = (13.5, 14.5) if c >= 7 else (12.5, 13.5)
                out.append((SKULL_U + c, SKULL_U + e, SKULL_V + r, SKULL_V + r + 1, z[0], z[1], "inside"))
                c = e
                continue
            ch = row[c]
            if ch in ".m":
                c += 1
                continue
            d = skull_depth(ch, c)
            kind = "teeth" if ch in "Tt" else "bone"
            e = c + 1
            while e < len(row) and row[e] not in ".m" and skull_depth(row[e], e) == d and (row[e] in "Tt") == (kind == "teeth"):
                e += 1
            out.append((SKULL_U + c, SKULL_U + e, SKULL_V + r, SKULL_V + r + 1, d[0], d[1], kind))
            c = e
    return out


def skull_boxes():
    """skull_runs() in the block: [(u0, u1, v0, v1, z0, z1, kind, uv)], the skull at SKULL_SCALE in the middle of the
    frame with its back on the hide (z = 15), so a ring of the hide shows around it; uv keeps the mask's pixels."""
    def bu(x):
        return 8 + (x - (SKULL_U + len(SKULL[0]) / 2)) * SKULL_SCALE

    def bv(y):
        return 8 + (y - (SKULL_V + len(SKULL) / 2)) * SKULL_SCALE

    def bz(z):
        return 15 - (15 - z) * SKULL_SCALE
    return [(bu(u0), bu(u1), bv(v0), bv(v1), bz(z0), bz(z1), kind, [u0, v0, u1, v1])
            for u0, u1, v0, v1, z0, z1, kind in skull_runs()]


def mask_at(u, v):
    c, r = u - SKULL_U, v - SKULL_V
    if 0 <= r < len(SKULL) and 0 <= c < len(SKULL[r]):
        return SKULL[r][c]
    return "."


def bone_base(seed, rugose=False):
    im, n = img(), noise(seed)
    for y in range(N):
        for x in range(N):
            t = 2 + (1 if n[y][x] > 0.72 else 0) - (1 if n[y][x] < 0.22 else 0)
            if rugose and (x + 2 * y) % 5 == 0:
                t = max(0, t - 1)
            im.putpixel((x, y), BONE[t])
    return im


def skull_side():
    """The faces turned to the room, pixel for pixel over the mask: lit where nothing is above, shaded where
    nothing is below, the rim of each opening lit on its lower edge and shaded under its upper edge."""
    im, n = img(), noise("alpha_skull")
    for v in range(N):
        for u in range(N):
            ch = mask_at(u, v)
            if ch in ".m":
                im.putpixel((u, v), BONE[2])
                continue
            if ch in "Tt":
                im.putpixel((u, v), TOOTH)
                continue
            t = 3 if n[v][u] > 0.8 else 2
            if mask_at(u, v - 1) in ".m" or mask_at(u - 1, v) in ".m":
                t = 4                                   # edges facing the light (top, left)
            if mask_at(u, v + 1) in ".m" or mask_at(u + 1, v) in ".m":
                t = 0 if mask_at(u, v + 1) in ".m" else 1   # edges in shade (bottom darkest, right)
            if ch == "r":
                t = 4 if (u + v) % 2 else 3
            elif ch == "g":
                t = 0
            elif ch == "p":
                im.putpixel((u, v), HOLE_RIM)
                continue
            elif ch == "j" and mask_at(u, v + 1) == ".":
                t = 0
            im.putpixel((u, v), BONE[max(0, min(4, t))])
    return im


def skull_top():
    """Tops, bottoms, ends and the walls of the openings: plain rough bone."""
    return bone_base("alpha_skull_top", rugose=True)


def skull_inside():
    """The dark inside of the skull seen through its openings: the far wall of bone in shadow."""
    im, n = img(), noise("alpha_skull_inside")
    for y in range(N):
        for x in range(N):
            im.putpixel((x, y), (40, 31, 22, 255) if n[y][x] > 0.6 else (28, 22, 16, 255))
    return im


# ------------------------------------------------------------------ the alpha's hide
def back_hide(coat, seed, tanned=0.18):
    """Cracked plates of the alpha's back in its coat colours, with one chevron mark (rows 4-11) that lines up
    with the next tile."""
    c = COATS[coat]
    owner, edge = cells(seed, 11)
    n = noise(seed + "n")
    tone = {o: random.Random(f"{seed}{o}").choice((1, 2, 2, 3)) for o in range(11)}
    im = img()
    for y in range(N):
        for x in range(N):
            o = owner[y][x]
            if edge[y][x]:
                col = c["crack"]
            else:
                t = tone[o] + (1 if n[y][x] > 0.8 else 0)
                below = owner[(y + 1) % N][x] != o
                above = owner[(y - 1) % N][x] != o
                t = t - 1 if below else t + 1 if above else t
                col = c["skin"][max(0, min(4, t))]
            im.putpixel((x, y), col)
    # the chevron: a V two pixels thick, point down at the middle, ends at the edges so tiles join
    for x in range(N):
        d = abs(x - 7.5)
        y = round(11 - d * 0.9)
        for k, col in ((0, c["mark"][1]), (1, c["mark"][0])):
            im.putpixel((x, (y + k) % N), col)
        im.putpixel((x, (y - 1) % N), c["mark"][2])  # soft edge above the mark
    if tanned:
        px = im.load()
        for y in range(N):
            for x in range(N):
                r, g, b, a = px[x, y]
                l = 0.3 * r + 0.59 * g + 0.11 * b
                px[x, y] = (int(r + (l - r) * tanned), int(g + (l - g) * tanned), int(b + (l - b) * tanned), a)
    return im


def trophy_hide(coat):
    """The hide stretched on its stick frame: the same back skin, darker at the edges where it is pulled over the
    sticks, with sinew lacing it to them every few pixels (the sticks are their own boxes; this is u1-15 v1-15)."""
    im = back_hide(coat, f"trophy_{coat}", tanned=0.1)
    sinew = (74, 58, 40, 255)
    for i in range(N):
        for j in (1, 14):
            for x, y in ((i, j), (j, i)):
                r, g, b, a = im.getpixel((x, y))
                im.putpixel((x, y), (int(r * 0.72), int(g * 0.72), int(b * 0.72), a))
    for i in range(2, 14, 3):
        for x, y in ((i, 1), (i, 14), (1, i), (14, i)):
            im.putpixel((x, y), sinew)
    return im


def stick():
    """Round stick of the frame: lit, mid, mid, shaded across, a knot here and there."""
    im = img()
    for y in range(N):
        for x in range(N):
            im.putpixel((x, y), STICK[(3, 2, 1, 0)[x % 4]])
    for y in (3, 11):
        im.putpixel((1, y), STICK[0]); im.putpixel((2, y), STICK[1])
    return im


def textures():
    out = {"tyrannosaurus_alpha_skull": skull_side(), "tyrannosaurus_alpha_skull_top": skull_top(),
           "tyrannosaurus_alpha_skull_inside": skull_inside(), "alpha_trophy_stick": stick()}
    for coat in COATS:
        out[f"tyrannosaurus_{coat}_hide_rug"] = back_hide(coat, f"rug_{coat}")
        out[f"tyrannosaurus_{coat}_trophy_hide"] = trophy_hide(coat)
    return out


def main():
    out = textures()
    for name, im in out.items():
        im.save(os.path.join(TEX, f"{name}.png"))
    return out


if __name__ == "__main__":
    print(len(main()), "alpha trophy/rug textures written to", TEX)
