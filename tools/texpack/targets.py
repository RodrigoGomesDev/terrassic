"""Yardstick for the packs: per vanilla block, the luma mean, the p95-p5 luma contrast and the mean luma jump
between neighbouring pixels, measured on Rodrigo's Mac from the 1.20.1 client jar (only these numbers came over;
no vanilla pixel is in the project). Our drawings are original; the palette fitter aims each one at the numbers of
the vanilla block it replaces, so both live side by side in the same world."""
import colorsys

import numpy as np

# name: (luma mean, contrast p95-p5, neighbour jump, colours)
TARGETS = {
    "stone": (125.5, 39.0, 6.36, 4),
    "cobblestone": (127.4, 84.0, 27.41, 6),
    "mossy_cobblestone": (115.0, 77.9, 21.38, 11),
    "dirt": (102.3, 75.6, 24.72, 7),
    "coarse_dirt": (90.9, 91.9, 29.61, 77),
    "rooted_dirt": (110.2, 92.1, 29.27, 9),
    "grass_block_top": (147.4, 56.0, 20.67, 66),
    "grass_block_side": (108.3, 93.6, 25.93, 40),
    "grass_block_side_overlay": (154.5, 49.0, 14.1, 16),
    "grass_block_snow": (153.8, 189.5, 20.05, 17),
    "podzol_top": (66.5, 43.7, 12.0, 6),
    "podzol_side": (92.9, 85.7, 21.84, 58),
    "gravel": (128.3, 58.1, 17.61, 8),
    "sand": (206.6, 21.3, 11.48, 6),
    "sandstone": (202.6, 51.0, 14.02, 7),
    "sandstone_top": (213.1, 11.4, 5.71, 5),
    "sandstone_bottom": (201.5, 51.0, 16.21, 6),
    "cut_sandstone": (205.5, 51.0, 6.82, 7),
    "chiseled_sandstone": (202.4, 58.4, 9.25, 7),
    "clay": (166.2, 21.9, 6.52, 6),
    "mud": (58.3, 21.1, 5.81, 7),
}


def measure(img):
    """Same measures as TARGETS for one of our images (opaque pixels only)."""
    a = np.asarray(img.convert("RGBA"), float)
    op = a[..., 3] > 0
    lum = a[..., :3] @ np.array([0.299, 0.587, 0.114])
    lv = lum[op]
    dx = np.abs(lum - np.roll(lum, -1, 1))
    dy = np.abs(lum - np.roll(lum, -1, 0))
    sat = float(np.mean([colorsys.rgb_to_hsv(*(p / 255))[1] for p in a[op][:, :3]]))
    return {"lum": float(lv.mean()), "ctr": float(np.percentile(lv, 95) - np.percentile(lv, 5)),
            "nb": float((dx[op].mean() + dy[op].mean()) / 2), "colours": len({tuple(p) for p in a[op][:, :3].astype(int)}),
            "sat": sat}
