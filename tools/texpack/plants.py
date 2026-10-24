"""TX2 (scratch): ground plants for the Late Cretaceous pack, drawn by hand as pixel grids (plantart.py) and
coloured by the palette fitter. Grass as we know it was rare in the Cretaceous, so the grass textures become
what covered the ground then: horsetails with whorls and spore cones beside low ferns; the large fern is a young
tree fern; the vine is a climbing fern. Tinted plants are grey (the biome colours them)."""
import sys

import numpy as np
from PIL import Image

import tex as T  # noqa: E402
from fit import fit  # noqa: E402

import plantart as A  # noqa: E402
from vanilla import VANILLA as TX2  # noqa: E402


def grid(rows):
    t = np.array([[0 if c == '.' else int(c) - 1 for c in r] for r in rows])
    op = np.array([[c != '.' for c in r] for r in rows])
    return t, op


def sprite(rows, name, hue=0.0, sat=0.0, dl=-2, n=4):
    t, op = grid(rows)
    m, c = TX2[name][0] + dl, TX2[name][1]
    pal = fit(t[op], n, m, c, hue, sat, hue_shift=.03 if sat else 0, sat_shift=.06 if sat else 0)
    img = np.asarray(T.colorize(t, pal)).copy()
    img[..., 3] = np.where(op, 255, 0)
    img[~op, :3] = 0
    return Image.fromarray(img, "RGBA")


ALL = {
    "grass": sprite(A.GRASS, "grass"),
    "fern": sprite(A.FERN, "fern"),
    "tall_grass_top": sprite(A.TALL_TOP, "tall_grass_top"),
    "tall_grass_bottom": sprite(A.TALL_BOTTOM, "tall_grass_bottom"),
    "large_fern_top": sprite(A.LARGE_FERN_TOP, "large_fern_top"),
    "large_fern_bottom": sprite(A.LARGE_FERN_BOTTOM, "large_fern_bottom"),
    "vine": sprite(A.VINE, "vine"),
    "dead_bush": sprite(A.DEAD_BUSH, "dead_bush", .08, .55, dl=0),
}
