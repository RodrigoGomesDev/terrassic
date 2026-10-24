"""TX3d: the ground of the biomes, for the Late Cretaceous pack. Laterite sands and red sandstone with a sickle
claw carved in the chiseled block; badland terracotta as fired clay with faint strata, in earth pigments; adobe
mud bricks and packed mud bound with straw; mangrove roots; old, cracked lake ice, packed ice and deep blue ice;
powder snow; flowstone; a fungal mat for mycelium."""
import math

import numpy as np
from PIL import Image

import api
import cretaceo as C
import masonry as MS
import tex as T
from stamps import base, poisson, stamp
from tex import N

M = api.Material

# ---------------------------------------------------------------- laterite sand and red sandstone
RED = dict(hue=.05, sat=.62, hue_shift=.015, sat_shift=.05)


def red(ref, n=5, dl=-4):
    return M(ref, n=n, dl=dl, **RED)


def red_sand():
    return api.paint(C.sand_tones(11), red("red_sand"))


CLAW = [  # the killing claw of a dromaeosaur: a hook from the broad toe bone (right) to a sharp tip (left)
    "......###...",
    "....######..",
    "...###.####.",
    "..##....####",
    ".##.....####",
    ".#......####",
    "##.....#####",
    "#......#####",
    "#.....######",
    "......######",
]


def sickle_claw():
    return np.array([[c == "#" for c in r] for r in CLAW])


def chiseled_red_sandstone_tones():
    t = base(7, 2, 1, 3, .15, .15, layers=((8, 8, 1),))
    t[0, :] = 4; t[:, 0] = 4; t[N - 1, :] = 0; t[:, N - 1] = 0
    t[1, 1:N - 1] = 3; t[1:N - 1, 1] = 3; t[N - 2, 1:N - 1] = 1; t[1:N - 1, N - 2] = 1
    cut = np.zeros((N, N), bool)
    cut[3:13, 2:14] = sickle_claw()
    t = np.where(cut, 1, t)
    t = np.where(cut & ~T.roll(cut, -1, -1), 0, t)
    t = np.where(T.roll(cut, -1, -1) & ~cut, 4, t)
    return t


def red_sandstone_family():
    return {
        "red_sandstone": api.paint(C.sandstone_side_tones(7), red("red_sandstone")),
        "red_sandstone_top": api.paint(C.sandstone_top_tones(7), red("red_sandstone_top", n=4)),
        "red_sandstone_bottom": api.paint(C.sandstone_bottom_tones(8), red("red_sandstone_bottom")),
        "cut_red_sandstone": api.paint(C.cut_sandstone_tones(7), red("cut_red_sandstone")),
        "chiseled_red_sandstone": api.paint(chiseled_red_sandstone_tones(), red("chiseled_red_sandstone")),
    }


# ---------------------------------------------------------------- terracotta
# Earth and mineral pigments rather than dyes: hue of the middle tone; saturation comes from vanilla's numbers.
TERRACOTTA = {
    "terracotta": .045, "white_terracotta": .07, "orange_terracotta": .065, "magenta_terracotta": .9,
    "light_blue_terracotta": .56, "yellow_terracotta": .11, "lime_terracotta": .2, "pink_terracotta": .99,
    "gray_terracotta": .05, "light_gray_terracotta": .07, "cyan_terracotta": .5, "purple_terracotta": .82,
    "blue_terracotta": .66, "brown_terracotta": .06, "green_terracotta": .2, "red_terracotta": .015,
    "black_terracotta": .04,
}


def terracotta_tones(seed):
    """Fired clay: calm, with faint strata from the badland beds it was cut from and a few grit specks."""
    f = .7 * T.fbm(seed, [(2, 8, .6), (4, 16, .4)]) + .3 * T.fbm(seed + 1, [(8, 8, 1)])
    t = T.quantize(f, [.18, .64, .18]) + 1
    for (x, y) in poisson(seed + 2, 5, 4.0):
        stamp(t, x, y, ['D'], {'D': 0})
    for (x, y) in poisson(seed + 3, 3, 5.0):
        stamp(t, x, y, ['L'], {'L': 4})
    return T.cleanup(t, 1, keep=(t == 0) | (t == 4))


def terracotta():
    out = {}
    for i, (name, hue) in enumerate(TERRACOTTA.items()):
        sat = api.target(name)[5]
        mat = M(name, hue, sat * .9, hue_shift=.01, sat_shift=.03, dl=-3)
        for seed in range(300 + i, 400 + i, 20):          # a calm block must not show its edges
            img = api.paint(terracotta_tones(seed), mat)
            if T.seam_excess(img) <= 1.2:
                break
        out[name] = img
    return out


# ---------------------------------------------------------------- mud family
def straw(t, seed, n, tone):
    """Short straws pressed into mud: two-pixel strokes in a few directions."""
    r = T.rng(seed)
    for (x, y) in poisson(seed + 1, n, 2.8):
        shape = [['LL'], ['L', 'L'], ['L.', '.L'], ['.L', 'L.']][int(r.integers(4))]
        stamp(t, x, y, shape, {'L': tone})
    return t


def mud_bricks():
    """Sun-dried adobe: big soft-edged bricks of mud and straw in dark joints, one course of headers."""
    t, gap, _ = MS.courses(121, heights=(4, 4, 4, 4), lengths=(7, 9), bodies=(2, 2, 3), gap_tone=0)
    straw(t, 122, 7, 4)
    t[gap] = 0
    return api.paint(t, M("mud_bricks", .075, .36, dl=-3, n=6))


def packed_mud():
    t = base(131, 2, 1, 3, .2, .2, layers=((4, 4, .5), (8, 8, .5)))
    straw(t, 132, 12, 4)
    for (x, y) in poisson(133, 4, 4.5):
        stamp(t, x, y, ['D'], {'D': 0})
    return api.paint(t, M("packed_mud", .07, .4, dl=-3, n=5))


def root_mask(seed, n_roots, top=False):
    """Roots wandering across the face (or seen end-on from the top), 1 to 2 px thick, wrapping at the edges."""
    r = T.rng(seed)
    m = np.zeros((N, N), bool)
    for k in range(n_roots):
        if top:
            x, y = r.uniform(0, N, 2)
            a = r.uniform(0, 2 * math.pi)
            steps = int(r.integers(10, 18))
        else:
            x, y = r.uniform(0, N), 0.0 if k % 2 == 0 else r.uniform(0, N)
            a = math.pi / 2 + r.uniform(-.7, .7)
            steps = int(r.integers(14, 22))
        for _ in range(steps):
            m[int(y) % N, int(x) % N] = True
            if k % 3 == 0:
                m[int(y) % N, int(x + 1) % N] = True
            a += r.uniform(-.45, .45)
            x += math.cos(a)
            y += math.sin(a)
    return m


def root_tones(m):
    """Body tone 2, the upper-left edge lit, the lower-right shaded."""
    t = np.where(m, 2, 0)
    lit = m & ~T.roll(m, 1, 0)
    shade = m & ~T.roll(m, -1, 0)
    t = np.where(lit, 3, np.where(shade, 1, t))
    return t


def mangrove_roots(top=False):
    m = root_mask(141 if not top else 151, 7 if not top else 9, top)
    ref = "mangrove_roots_top" if top else "mangrove_roots_side"
    return api.paint(root_tones(m), M(ref, .07, .32, dl=-2, n=4), alpha=m)


def muddy_mangrove_roots(top=False):
    ref = "muddy_mangrove_roots_top" if top else "muddy_mangrove_roots_side"
    mud = base(161 if not top else 171, 1, 0, 2, .2, .2, layers=((4, 4, .5), (8, 8, .5)))
    m = root_mask(141 if not top else 151, 7 if not top else 9, top)
    t = np.where(m, root_tones(m) + 2, mud)
    hollow = T.roll(m, -1, 0) & ~m                       # mud settles darker under each root
    t = np.where(hollow, 0, t)
    return api.paint(t, M(ref, .07, .3, dl=-2, n=6))


# ---------------------------------------------------------------- ice and snow
ICE_ALPHA = 172      # lake ice stays see-through (vanilla's ice is translucent too)


def ice_tones(seed, cells=3, cracks=True):
    """Plates of old ice: Voronoi plates, cracks between them, a few frozen bubbles, a lit diagonal sheen."""
    pts = T.jittered_points(seed, cells, cells, .9)
    idx, _, _ = T.voronoi(pts, warp=T.fbm(seed + 1, [(4, 4, 1)]), warp_amp=1.2)
    edges = T.cell_edges(idx)
    ys, xs = np.mgrid[0:N, 0:N]
    sheen = (((xs + ys) % 11) < 2) & (T.fbm(seed + 4, [(4, 4, 1)]) > .45)
    t = np.full((N, N), 2)
    t = np.where(T.fbm(seed + 2, [(4, 4, .6), (8, 8, .4)]) > .62, 3, t)
    t = np.where(sheen, 4, t)
    if cracks:
        t = np.where(edges, 1, t)
        t = np.where(T.roll(edges, -1, -1) & ~edges, np.minimum(t + 1, 4), t)
    for (x, y) in poisson(seed + 3, 4, 4.0):
        stamp(t, x, y, ['L', 'D'], {'L': 4, 'D': 1})
    return t


def ice():
    img = np.asarray(api.paint(ice_tones(181), M("ice", .56, .42, hue_shift=-.01, sat_shift=.06, dl=0, n=5))).copy()
    img[..., 3] = ICE_ALPHA
    return Image.fromarray(img, "RGBA")


def packed_ice():
    t = ice_tones(191, cells=4)
    return api.paint(t, M("packed_ice", .57, .3, hue_shift=-.01, sat_shift=.06, dl=-2, n=5))


def blue_ice():
    """Glacier ice pressed for ages: deep blue, almost no cracks, long bubble trails."""
    t = ice_tones(201, cells=2, cracks=False)
    r = T.rng(202)
    for (x, y) in poisson(203, 3, 5.0):
        for k in range(int(r.integers(3, 6))):
            t[(y + k) % N, x] = 4 if k % 2 == 0 else t[(y + k) % N, x]
    return api.paint(t, M("blue_ice", .58, .52, hue_shift=-.01, sat_shift=.06, dl=-2, n=5))


def powder_snow():
    """Loose, deep snow: fine grain everywhere, little pits where flakes settle."""
    t = T.quantize(T.fbm(211, [(8, 8, .4), (16, 16, .6)]), [.2, .5, .3]) + 1
    for (x, y) in poisson(212, 12, 2.8):
        stamp(t, x, y, ['D', 'L'], {'D': 0, 'L': 3})
    return api.paint(t, M("powder_snow", .55, .04, dl=-1, n=4))


# ---------------------------------------------------------------- caves and fungi ground
def dripstone_block():
    """Flowstone: thin calcite layers laid down by seeping water, wavy and bulging, with drip pits."""
    ys, xs = np.mgrid[0:N, 0:N]
    wob = 1.5 * (T.fbm(221, [(2, 1, .5), (4, 2, .5)]) - .5) * 2
    band = ((ys + wob) / (N / 3)) % 1.0                 # three layers per block, so it tiles
    t = np.where(band < .16, 0, np.where(band < .3, 1, np.where(band < .62, 2, np.where(band < .86, 3, 4))))
    t = np.where((t == 2) & (T.fbm(222, [(8, 8, 1)]) > .7), 3, t)
    for (x, y) in poisson(223, 3, 5.0):
        stamp(t, x, y, ['D', 'L'], {'D': 0, 'L': 4})
    return api.paint(T.cleanup(t, 1, keep=(t == 0)), M("dripstone_block", .08, .2, dl=-3, n=5))


def mycelium_tones(seed):
    """A fungal mat over the earth: pale threads in tangles, tiny dark fruiting dots."""
    t = base(seed, 2, 1, 3, .22, .22, layers=((4, 4, .5), (8, 8, .5)))
    r = T.rng(seed + 1)
    for (x, y) in poisson(seed + 2, 10, 3.0):
        shape = [['L.L', '.L.'], ['.L', 'LL'], ['LL.', '..L']][int(r.integers(3))]
        stamp(t, x, y, shape, {'L': 4})
    for (x, y) in poisson(seed + 3, 6, 3.6):
        stamp(t, x, y, ['D'], {'D': 0})
    return t


MYCELIUM = dict(hue=.82, sat=.09, hue_shift=-.03, sat_shift=.03)


def mycelium_top():
    return api.paint(mycelium_tones(231), M("mycelium_top", dl=-2, n=5, **MYCELIUM))


def mycelium_side():
    mask, depth = C.fringe(233)
    top = np.asarray(mycelium_top()).copy()
    t = C.dirt_tones(1)
    pal = C.dirt_palette(t)
    t = C.add_pebbles(t, 10, 2, 5)
    for x in range(N):
        if depth[x] < N:
            t[depth[x], x] = 0
    img = np.asarray(C.paint(t, pal + C.PEBBLE)).copy()
    img[mask] = top[mask]
    return Image.fromarray(img, "RGBA")


def textures():
    out = {"red_sand": red_sand()}
    out.update(red_sandstone_family())
    out.update(terracotta())
    out.update({
        "mud_bricks": mud_bricks(), "packed_mud": packed_mud(),
        "mangrove_roots_side": mangrove_roots(), "mangrove_roots_top": mangrove_roots(True),
        "muddy_mangrove_roots_side": muddy_mangrove_roots(), "muddy_mangrove_roots_top": muddy_mangrove_roots(True),
        "ice": ice(), "packed_ice": packed_ice(), "blue_ice": blue_ice(), "powder_snow": powder_snow(),
        "dripstone_block": dripstone_block(), "mycelium_top": mycelium_top(), "mycelium_side": mycelium_side(),
    })
    return out


ALL = textures()
